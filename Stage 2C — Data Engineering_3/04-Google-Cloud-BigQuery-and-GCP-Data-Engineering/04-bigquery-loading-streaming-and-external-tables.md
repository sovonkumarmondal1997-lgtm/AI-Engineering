# Topic 04 — BigQuery Loading, Streaming, and External Tables

> **Roadmap location:** `Stage 2C — Data Engineering_3/04-Google-Cloud-BigQuery-and-GCP-Data-Engineering/04-bigquery-loading-streaming-and-external-tables.md`  
> **Prerequisites:** Topic 02 — BigQuery architecture, slots, and storage; Topic 03 — partitioning, clustering, and query cost control  
> **Downstream connection:** Topic 06 — Pub/Sub and Dataflow (Apache Beam)  
> **Lab root:** `experiments/04_loading/`

## 1. Learning objectives and prerequisites

By completing this lesson, you will be able to:

- Choose a reliable ingestion pattern for batch files, low-latency events, external data, and change data capture (CDC).
- Load CSV, newline-delimited JSON, Avro, Parquet, and ORC from Cloud Storage with explicit schemas, safe write dispositions, and retry-aware job identifiers.
- Use the Python BigQuery client methods `load_table_from_uri`, `load_table_from_dataframe`, and `load_table_from_file`.
- Compare external tables and BigLake with native BigQuery tables, including Hive-style partitioning and metadata caching.
- Explain the Storage Write API's default stream and committed-stream semantics, and where legacy `insertAll` fits.
- Evolve schemas safely, validate contracts, and avoid incompatible type changes.
- Apply CDC inserts, updates, and deletes without creating duplicate current-state rows.
- Build quarantine, replay, reconciliation, and data-quality controls.
- Monitor ingestion through job metadata, load-job metadata, row counts, and source-to-target reconciliation.
- Design landing, raw, and curated layers with clear ownership and recovery boundaries.

### Prerequisites

You should be comfortable with:

- GoogleSQL, DDL/DML, `MERGE`, window functions, and `QUALIFY`.
- BigQuery datasets, table schemas, query jobs, partition filters, and cost controls.
- Cloud Storage URIs, IAM, service accounts, Application Default Credentials (ADC), and the `gcloud`/`bq` CLIs.
- Basic event identity, retries, offsets/cursors, late arrivals, and duplicate handling.

### Source roadmap alignment

Topic 04 is the practical ingestion module after Topic 02 explains BigQuery storage/execution and Topic 03 teaches cost guardrails. Topic 06 extends the streaming path into Pub/Sub and Dataflow. The source roadmap specifically expects a 50 GB daily file-drop decision, a 5,000-events/second stream decision, a PostgreSQL CDC design, and explicit idempotency reasoning. The exercises here default to small datasets and require a deliberate scale-up decision before production-sized tests.

---

## 2. Ingestion architecture and design principles

### 2.1 Choose by freshness, volume, source semantics, and recovery needs

| Requirement | Starting pattern | Why / caveat |
|---|---|---|
| Daily/hourly files, minutes-to-hours latency acceptable | Cloud Storage + BigQuery load job | Efficient for batch; load jobs are atomic. Under on-demand pricing, batch load jobs generally have no separate BigQuery ingestion charge; if load jobs are assigned to a capacity reservation, they can consume the applicable reservation capacity. Cloud Storage storage and network costs can still apply. |
| Files must be queried before copying or are large/open-format lake data | External table; BigLake where access governance or metadata caching is needed | Avoids immediate copy, but query latency, source-file layout, object listing, and external-storage charges matter. |
| Low-latency event stream | Storage Write API or Pub/Sub BigQuery subscription | Choose API control vs managed direct subscription; define duplicate, schema, dead-letter, and replay strategy. |
| Transform, enrich, window, route, or validate a stream | Pub/Sub + Dataflow (Topic 06) + Storage Write API or another supported sink | More operational components, but supports streaming transformations and error routing. |
| Replicate operational database inserts/updates/deletes | Datastream CDC into BigQuery, or a designed log-based CDC pipeline | Preserves change semantics better than repeatedly exporting full tables; source engine/version and primary-key requirements must be verified. |
| Occasional live lookup against an operational database | Federated query / external dataset where supported | Useful for small or fresh lookups; repeated analytical workloads may be slow, increase source load, and couple analytics availability to the source. |
| Supported SaaS/cross-cloud source on a schedule | BigQuery Data Transfer Service connector | Managed scheduling/backfill for supported connectors; source coverage, region, credentials, and incremental semantics vary by connector. |

### 2.2 A practical landing → raw → curated design

```text
Source systems
  ├─ Cloud Storage batch files ───────────┐
  ├─ Pub/Sub / application events ────────┤
  ├─ Datastream CDC ──────────────────────┤
  └─ SaaS / cross-cloud transfer ─────────┘
                                           ↓
Landing: immutable source files, event envelope, source offsets,
         ingestion timestamp, batch ID, schema/version metadata
                                           ↓
Raw: append-oriented BigQuery tables, source-shaped columns,
     source event identity, operation type, source commit/cursor
                                           ↓
Validation / quarantine / deduplication / replay
                                           ↓
Curated: typed, deduplicated, business-keyed tables; CDC current state;
         partitioned and clustered to match downstream queries
```

**Landing** preserves replayable source artifacts and source identity. **Raw** records what arrived, including invalid or late data when policy permits. **Curated** contains trusted, typed, reconciled business data. Do not discard the raw event before the curated write and quality checks are durable.

The terms “landing”, “raw”, and “curated” describe logical responsibilities. They can be separate datasets/projects/buckets or controlled schemas in one project. Separate access boundaries, retention, encryption, and billing labels where the risk profile requires it.

### 2.3 The core correctness properties

Define these before writing an ingestion pipeline:

1. **Identity:** what uniquely identifies a file/batch, event, database row, or CDC change?
2. **Ordering:** is order relevant? If yes, which sequence number, source offset, log position, or version defines it?
3. **Delivery:** at-most-once, at-least-once, or a specific exactly-once capability?
4. **Atomicity:** what is committed together, and what can be partially visible?
5. **Idempotency:** what happens if the same work is retried after an unknown network outcome?
6. **Schema contract:** which fields/types are required, optional, additive, or breaking?
7. **Reconciliation:** how are source and target counts, keys, offsets, and aggregates compared?
8. **Recovery:** how are failed work items quarantined, replayed, or backfilled without duplication?
9. **Cost/freshness:** what ingestion latency and cost are acceptable for this workload?

### 2.4 Delivery guarantees: be precise

- **At-most-once:** work is not retried after uncertainty, so duplicates are avoided at the risk of data loss.
- **At-least-once:** work is retried until acknowledged, so duplicates are possible and must be handled.
- **Exactly-once within a defined boundary:** the service uses a stable identity/offset/transaction to prevent duplicate acceptance within that boundary. It does not automatically guarantee exactly-once business effects across the source, transport, BigQuery, and downstream consumers.

Examples:

- A BigQuery load job with a known job ID is retry-safe for submitting/polling that *same job*. It does not prevent a pipeline from creating a new job ID and loading the same file again.
- Storage Write API committed streams with record offsets can provide exactly-once writes **within that stream**. The application must persist and advance offsets correctly.
- Pub/Sub redelivery and a dead-letter topic do not automatically deduplicate business events in a destination table.
- A CDC pipeline needs source transaction/sequence metadata and key semantics; a timestamp alone may not provide deterministic ordering.

### 2.5 A safe retry state machine

```text
DISCOVERED
   ↓ compute immutable batch identity (source URI + object generation/checksum + config version)
SUBMITTED with deterministic job ID
   ├─ network timeout / unknown response → GET existing job by same ID
   ├─ DONE + no fatal error             → verify output and mark committed
   ├─ RUNNING                           → poll existing job; do not resubmit under a new ID
   └─ terminal failure                  → classify failure, fix/reconcile, then create an explicit retry attempt
```

Persist the batch identity, source object generation/checksum, destination, write disposition, schema/config version, job ID, status, row counts, and retry attempt. A deterministic ID alone is not enough: the source must be immutable or versioned, and the target write semantics must be correct.

---

## 3. Batch ingestion from Cloud Storage

### 3.1 Supported file formats and selection

| Format | BigQuery load format | Advantages | Risks / considerations |
|---|---|---|---|
| CSV | `CSV` | Portable, easy to inspect, compact for simple records | Weak type/schema metadata; delimiters, quoting, headers, nulls, encoding, and malformed rows require explicit handling |
| Newline-delimited JSON | `NEWLINE_DELIMITED_JSON` | Flexible nested records; one JSON object per line | Larger text payloads; schema drift and malformed JSON need handling; not the same as one arbitrary multi-line JSON document |
| Avro | `AVRO` | Self-describing schema; good record-oriented interoperability | Logical type mapping and schema evolution must be understood |
| Parquet | `PARQUET` | Columnar, compressed, typed; often suitable for analytics/lake data | Field names/types and nested structure must align; many tiny files harm external scans |
| ORC | `ORC` | Columnar format with type metadata | Validate supported logical types and upstream writer compatibility |

For recurring production loads, prefer a stable, versioned schema and columnar format such as Parquet or Avro when the upstream ecosystem supports it. CSV/JSON can be reasonable for interchange and small feeds, but they require stronger validation.

### 3.2 Batch load jobs: core properties

A load job reads one or more Cloud Storage objects and writes rows to a BigQuery table. BigQuery load jobs are atomic: a failed load does not expose a partial successful result as a completed load. This does **not** mean every row is necessarily valid when the job succeeds: if a permissive bad-record setting is used, some invalid rows can be skipped. Verify `output_rows`, `badRecords`, job errors, and source counts.

Key configuration choices:

- `source_format`
- `schema` or `autodetect`
- `write_disposition`
- `create_disposition`
- `schema_update_options`
- `max_bad_records`
- `ignore_unknown_values`
- `skip_leading_rows` / CSV parsing options
- destination dataset location
- source URI pattern and immutable object version
- destination partitioning/clustering and labels where applicable

### 3.3 Explicit schema vs autodetection

**Explicit schema** is preferred for stable production contracts. It makes type expectations reviewable, avoids sample-dependent inference, and gives controlled handling of nullable/required fields.

**Autodetection** is useful for exploration, onboarding an unknown feed, or prototyping. It infers from source data and can be brittle when files are small, inconsistent, or change over time. Do not let a production contract silently change because a new file happens to contain a different value.

Example schema for event records:

```python
from google.cloud import bigquery

EVENT_SCHEMA = [
    bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("event_ts", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("tenant_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("event_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("user_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("amount", "NUMERIC", mode="NULLABLE"),
    bigquery.SchemaField("source_batch_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="REQUIRED"),
]
```

`REQUIRED` fields must be populated by every source row. If source feeds legitimately omit a field, make it `NULLABLE` and enforce the business requirement in a quality check instead.

### 3.4 Write dispositions

| Disposition | Behavior | Safe use |
|---|---|---|
| `WRITE_APPEND` | Add loaded rows to existing table | New immutable batch with an audit key and deduplication/reconciliation strategy |
| `WRITE_TRUNCATE` | Replace existing table data (and can affect schema/policies depending on operation/configuration) | Deliberate full refresh of a controlled target, with recovery and downstream coordination |
| `WRITE_EMPTY` | Write only if the destination is empty | Initial create or guarded one-time load where non-empty destination should fail |

Do not use `WRITE_TRUNCATE` as a casual retry fix. A retried full refresh may be valid if the source snapshot is stable and the replacement is intentional, but it can erase intervening data or alter metadata/policies. Review the current client/API behavior before using truncation on partitioned tables or tables with governance settings.

### 3.5 Idempotent load jobs with deterministic job IDs

Derive the logical batch ID from immutable source identity and the load contract. Example components:

- object URI and Cloud Storage generation or checksum
- destination table
- write disposition
- schema/configuration version
- pipeline version if it changes the meaning of the load

Then derive a valid deterministic BigQuery job ID from a sanitized prefix and a hash. On retry after a timeout, retrieve the job by the same ID and inspect its state; do not blindly create a new job.

```python
import hashlib
import re
from google.api_core.exceptions import (
    Conflict,
    DeadlineExceeded,
    NotFound,
    ServiceUnavailable,
)
from google.cloud import bigquery

def stable_job_id(batch_identity: str) -> str:
    digest = hashlib.sha256(batch_identity.encode("utf-8")).hexdigest()[:32]
    return f"load_{digest}"

def submit_or_reuse_load(
    client: bigquery.Client,
    source_uri: str,
    destination: str,
    batch_identity: str,
    location: str = "US",
) -> bigquery.job.LoadJob:
    job_id = stable_job_id(batch_identity)
    config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        schema=EVENT_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
        max_bad_records=0,
    )
    try:
        job = client.load_table_from_uri(
            source_uri,
            destination,
            job_id=job_id,
            location=location,
            job_config=config,
        )
    except Conflict:
        # The deterministic job ID already exists; inspect that job.
        job = client.get_job(job_id, location=location)
    except (DeadlineExceeded, ServiceUnavailable):
        # The submit outcome is unknown. First look for the same job ID.
        try:
            job = client.get_job(job_id, location=location)
        except NotFound:
            # Re-submit only with the SAME job ID and identical configuration.
            # A race may still produce Conflict, in which case fetch that job.
            try:
                job = client.load_table_from_uri(
                    source_uri,
                    destination,
                    job_id=job_id,
                    location=location,
                    job_config=config,
                )
            except Conflict:
                job = client.get_job(job_id, location=location)
    try:
        job.result()  # Wait for the job and surface terminal job failures.
    except Exception as exc:
        job.reload()
        if job.error_result:
            raise RuntimeError(f"Load failed: {job.error_result}") from exc
        raise
    if job.error_result:
        raise RuntimeError(f"Load failed: {job.error_result}")
    return job
```

This pattern assumes the logical batch identity is unique for one immutable batch and that configuration is identical on retries. The BigQuery API does not permit reusing a job ID for a different job definition. If the prior job is terminally failed, do not silently change its configuration under the same ID; record the failure and use an explicit attempt ID after correcting the cause. If a successful `WRITE_APPEND` job is retried under a *different* ID, the same rows can be appended twice. Reconcile target rows before starting a new logical attempt.

### 3.6 Cloud Storage layout, object identity, and file sizing

Prefer immutable, uniquely named batch objects and a manifest with:

- source system and batch ID
- URI and object generation/checksum
- schema version
- expected row count / byte count where available
- source extraction time and watermark
- expected destination and load mode

Avoid overwriting a source object after submission. A URI alone may point to different content at a later time. Use object generation/versioning or a content checksum when building the batch identity, but note that a normal `gs://bucket/object` load URI does not pin BigQuery to a particular Cloud Storage generation. Enforce immutability for the object's lifetime or copy the intended generation to a unique immutable path before submitting the load. A generation value in the ledger is an audit signal, not by itself a guarantee that the load read that exact generation.

Avoid enormous numbers of tiny files. Many tiny files increase listing/scheduling overhead, particularly for external tables. For batch loads, group files into a sensible number and size for the service limits and latency requirement; consult current load-job quotas rather than hard-coding a universal ideal size. For partitioned data, use predictable directory and file naming conventions.

### 3.7 Load errors and `max_bad_records`

`max_bad_records` controls how many bad records a load job can tolerate for supported formats; it is **not** a durable rejected-row table. BigQuery load jobs do not automatically materialize every rejected input row into a user-queryable error table. Job errors often contain only a limited set of diagnostic messages and may not contain the full rejected payload. If rejected rows must be retained for audit or replay, design a quarantine path before loading. For supported CSV/JSON sources, a tolerant load can help identify that bad records occurred, but preserving the exact invalid payload generally requires retaining the source and parsing/validating it separately.

For strict loads, use `max_bad_records=0` and fail the batch on invalid data. For tolerant loads, specify the tolerance deliberately and reconcile source count = accepted + rejected. A successful job with skipped bad records is not automatically a data-quality success.

---

## 4. Python client and CLI workflows

### 4.1 Setup, APIs, and IAM

Example setup:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install "google-cloud-bigquery" "google-cloud-bigquery-storage" "google-cloud-storage" "pyarrow" "pandas" "db-dtypes"
gcloud auth application-default login
gcloud config set project YOUR_PROJECT
gcloud services enable bigquery.googleapis.com storage.googleapis.com bigquerystorage.googleapis.com
```

Use a service account in production rather than a developer's personal ADC. Grant least privilege at the narrowest scope. Depending on the workflow, the principal commonly needs:

- BigQuery job creation permission (`bigquery.jobs.create`) in the job project.
- Dataset/table permissions to create or write the destination, and read metadata for verification.
- Cloud Storage object read permissions on the source bucket (for example, a role granting `storage.objects.get` and `storage.objects.list` where needed).
- Storage Write API permissions to write the destination and create streams for committed-stream workflows.
- `bigquery.connections.use` / connection-user access plus source-specific IAM when using federation.
- Pub/Sub subscription service-agent/table write permissions for direct BigQuery subscriptions.
- Datastream source access, replication privileges, destination write permissions, and service networking requirements when applicable.

Exact roles depend on whether the job creates tables, reads source objects, changes schemas, creates connections, or manages services. Do not grant project Owner or Editor merely to make a lab work. Check the current product-specific IAM documentation and audit logs.

### 4.2 `load_table_from_uri` — Parquet from GCS

```python
from google.cloud import bigquery

client = bigquery.Client(project="YOUR_PROJECT")
destination = "YOUR_PROJECT.ingest_lab.events_raw"
uri = "gs://YOUR_BUCKET/events/batch_id=2026-10-19/part-000.parquet"

config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.PARQUET,
    schema=EVENT_SCHEMA,
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    max_bad_records=0,
)
job = client.load_table_from_uri(
    uri,
    destination,
    job_config=config,
    location="US",
)
job.result()
print({
    "job_id": job.job_id,
    "output_rows": job.output_rows,
    "input_files": job.input_files,
    "input_bytes": job.input_file_bytes,
    "errors": job.errors,
})
```

Use the deterministic job ID pattern from Section 3.5 in production. This shorter example demonstrates the API signature; it is not a complete retry controller.

### 4.3 `load_table_from_file` — local file or stream

```python
from pathlib import Path
from google.cloud import bigquery

client = bigquery.Client(project="YOUR_PROJECT")
destination = "YOUR_PROJECT.ingest_lab.events_csv"
config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    schema=[
        bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("event_ts", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("tenant_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("event_name", "STRING", mode="REQUIRED"),
    ],
    skip_leading_rows=1,
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    max_bad_records=0,
)
with Path("events.csv").open("rb") as source_file:
    job = client.load_table_from_file(
        source_file,
        destination,
        job_config=config,
        rewind=True,
        location="US",
    )
job.result()
print(f"Rows loaded: {job.output_rows}")
```

Use binary mode. If retrying from a file-like object, ensure it is rewound or reopened. Avoid accidentally loading a partial stream after a previous read.

### 4.4 `load_table_from_dataframe` — pandas

```python
import pandas as pd
from google.cloud import bigquery

client = bigquery.Client(project="YOUR_PROJECT")
df = pd.DataFrame([
    {
        "event_id": "evt-001",
        "event_ts": pd.Timestamp("2026-10-19T09:00:00Z"),
        "tenant_id": "tenant-01",
        "event_name": "page_view",
        "user_id": "user-01",
        "amount": 0,
        "source_batch_id": "batch-001",
        "ingested_at": pd.Timestamp.now(tz="UTC"),
    }
])
config = bigquery.LoadJobConfig(
    schema=EVENT_SCHEMA,
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
)
job = client.load_table_from_dataframe(
    df,
    "YOUR_PROJECT.ingest_lab.events_raw",
    job_config=config,
    location="US",
)
job.result()
```

`load_table_from_dataframe` uses the BigQuery client and commonly relies on `pyarrow` for serialization. Confirm pandas dtypes map to the intended BigQuery types; nullable integer, timestamp timezone, decimal, and nested fields deserve explicit tests. For repeatable batch loads, persist the batch ID and avoid re-appending the same DataFrame after an ambiguous failure.

### 4.5 `bq load` CLI examples

Parquet:

```bash
bq --location=US load \
  --source_format=PARQUET \
  --replace=false \
  YOUR_PROJECT:ingest_lab.events_raw \
  'gs://YOUR_BUCKET/events/batch_id=2026-10-19/*.parquet'
```

CSV with explicit schema:

```bash
bq --location=US load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  --schema=event_id:STRING,event_ts:TIMESTAMP,tenant_id:STRING,event_name:STRING \
  --replace=false \
  YOUR_PROJECT:ingest_lab.events_csv \
  gs://YOUR_BUCKET/events.csv
```

`--replace=false` is an append behavior. The CLI's job ID behavior should be made explicit for automated retries by using a script/API workflow that stores and reuses a deterministic job ID. For production pipelines, prefer a controlled orchestration layer with persisted state over a bare shell command.

---

## 5. External tables and BigLake

### 5.1 External table versus native table

| Dimension | External table | Native BigQuery table |
|---|---|---|
| Data location | Files remain in Cloud Storage or another supported external source | Data is stored in BigQuery-managed storage |
| Ingestion delay | No copy required; data can be queried after external metadata/data is available | Requires a load/stream/transfer step |
| Performance | Depends on file format, file count, source access, metadata listing, pruning, and caching | Usually more predictable for repeated analytical workloads; benefits from native storage organization |
| Cost | Query charges can apply; external storage/network costs also apply; no native table storage for source files | Storage charges plus query/compute charges; ingestion path may have separate charges |
| Governance | Access to source objects, connection permissions, and BigQuery metadata all matter | BigQuery IAM, policy controls, and native table governance apply |
| Data freshness | Reflects external source contents subject to metadata/cache behavior | Reflects successful writes/loads into the table |
| Best fit | Exploration, lake data, infrequently queried data, open-format access, avoiding copy | Frequent analytics, stable SLAs, predictable performance, transformations, high reuse |

External does not mean free. Querying can incur BigQuery analysis charges, and reading/listing external objects can have latency and storage/network implications. BigLake adds connection-based access delegation and, for supported sources/tables, metadata caching; it does not magically turn all external queries into native-table performance.

### 5.2 Create an external table over Parquet

```sql
CREATE OR REPLACE EXTERNAL TABLE `YOUR_PROJECT.ingest_lab.events_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://YOUR_BUCKET/events/*.parquet']
);
```

For production, prefer a narrow URI prefix and a predictable file layout. The external table schema can be inferred from self-describing formats such as Parquet, but validate types and field compatibility across every file in the URI set.

### 5.3 Hive-style partitioning

A path such as:

```text
gs://YOUR_BUCKET/events/event_date=2026-10-18/tenant=tenant-01/part-000.parquet
gs://YOUR_BUCKET/events/event_date=2026-10-19/tenant=tenant-02/part-000.parquet
```

encodes partition values in the object path. Create an external table with Hive partition columns:

```sql
CREATE OR REPLACE EXTERNAL TABLE `YOUR_PROJECT.ingest_lab.events_hive_external`
WITH PARTITION COLUMNS (
  event_date DATE,
  tenant STRING
)
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://YOUR_BUCKET/events/*'],
  hive_partition_uri_prefix = 'gs://YOUR_BUCKET/events',
  require_hive_partition_filter = TRUE
);
```

The URI prefix must end before the first partition key in the path; partition key order and types must match the directory layout. Validate exact prefix semantics and supported path patterns against the current documentation before deployment. If partition keys change, recreate the external table.

Query with filters that use the partition columns:

```sql
SELECT event_name, COUNT(*) AS event_count
FROM `YOUR_PROJECT.ingest_lab.events_hive_external`
WHERE event_date >= DATE '2026-10-01'
  AND event_date < DATE '2026-11-01'
  AND tenant = 'tenant-01'
GROUP BY event_name;
```

### 5.4 Metadata caching

Metadata caching can improve query startup and pruning for supported BigLake/external table types, especially when there are many files and Hive partition filters. It trades freshness against latency: a configured maximum staleness allows queries to use cached metadata within that interval. Confirm supported source type and table kind; ordinary external tables do not all support the same caching features.

Example for a supported BigLake table, where the exact connection/location must be configured for your project:

```sql
-- Illustrative DDL: verify the connection and options for your table type.
CREATE OR REPLACE EXTERNAL TABLE `YOUR_PROJECT.ingest_lab.events_biglake`
WITH PARTITION COLUMNS (event_date DATE, tenant STRING)
WITH CONNECTION `YOUR_PROJECT.US.REGION_CONNECTION`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://YOUR_BUCKET/events/*'],
  hive_partition_uri_prefix = 'gs://YOUR_BUCKET/events',
  require_hive_partition_filter = TRUE,
  metadata_cache_mode = 'AUTOMATIC',
  max_staleness = INTERVAL 1 HOUR
);
```

Treat this as a template: replace `YOUR_PROJECT.US.REGION_CONNECTION` with the actual `PROJECT_ID.LOCATION.CONNECTION_ID` resource name; the connection location must be compatible with the dataset/table location. Metadata caching options vary by supported BigLake source/table type. Check the current DDL documentation before running. A one-hour staleness example is not appropriate if the application requires immediate discovery of newly arrived files.

### 5.5 Compare external and native tables fairly

1. Use the same logical dataset and equivalent schema.
2. Load/copy external data into a native table once.
3. Use equivalent queries and selected columns.
4. Control result caching and run multiple trials.
5. Record bytes processed/billed, elapsed time, query plan, and source file count/size.
6. Include the native table's storage and load/refresh cost, not just query latency.
7. Test the actual workload: metadata listing and file layout can dominate external-table performance.

### 5.6 Federated queries and external datasets: Cloud SQL, Spanner, and Bigtable

Federation lets BigQuery query supported operational data without first copying it into a native BigQuery table, but the source system remains part of the query's latency, availability, authorization, and capacity path. The supported interface differs by source; do not assume a single `EXTERNAL_QUERY` syntax works for every source.

| Source | BigQuery integration | Good fit | Key limitations to verify |
|---|---|---|---|
| Cloud SQL (supported MySQL/PostgreSQL configurations) | `EXTERNAL_QUERY` through a BigQuery connection | Selective lookup or modest source-side query whose result is useful for analysis | Connection region, database permissions, supported engine/version, SQL dialect conversion, source load, and network/connection constraints |
| Spanner | `EXTERNAL_QUERY` through a BigQuery connection | Selective reads from operational Spanner data or cross-system analysis | Connection setup, supported types/functions, source query cost/latency, and region compatibility |
| Bigtable | Bigtable external table / supported connection configuration | Analytical reads over selected Bigtable data where external-table semantics fit | Schema mapping, row-key/range design, source read load, supported options, and external-table performance; it is not the same integration path as Cloud SQL/Spanner `EXTERNAL_QUERY` |

For recurring warehouse analytics, high scan volume, strict performance SLAs, or heavy joins, replicate/ingest the required data into BigQuery rather than repeatedly pushing analytical scans to an operational database. Use least-privilege connection access and test a small selective query before production use. See the official Cloud SQL, Spanner, and Bigtable integration references in Section 16.

### 5.7 Data Transfer Service for SaaS and cross-cloud sources

BigQuery Data Transfer Service (DTS) is a managed scheduled-transfer mechanism, not a universal connector to every SaaS product or cloud storage system. Examples in the current connector catalog include Google marketing/analytics products, Salesforce, ServiceNow, selected payment/marketing SaaS connectors, Cloud Storage, Amazon S3, Azure Blob Storage, and supported database/warehouse sources such as Redshift, Snowflake, MySQL, PostgreSQL, and Oracle. Availability and preview status can change; confirm the current source catalog, region support, credentials, backfill behavior, and incremental key semantics for the chosen connector. A successful transfer run still needs row-count/watermark reconciliation.

---

## 6. Streaming ingestion and delivery guarantees

### 6.1 Choose the streaming interface

| Interface | Semantics / use | Key cautions |
|---|---|---|
| Storage Write API default stream | Managed stream with immediate query availability after acknowledgement; at-least-once behavior | Retries can duplicate records; use stable event IDs and downstream dedupe if duplicates are unacceptable |
| Storage Write API application-created committed stream with offsets | Exactly-once write semantics within a stream when offsets are correctly supplied and persisted | Offset management and stream lifecycle become application responsibilities |
| Legacy `tabledata.insertAll` (`insertAll`) | Older streaming inserts with row-level insert IDs and best-effort deduplication | Insert IDs are not a strict exactly-once guarantee; legacy behavior and pricing should be checked against current documentation |
| Pub/Sub BigQuery subscription | Managed direct write from Pub/Sub to a BigQuery table using Storage Write API | Less transformation flexibility; schema compatibility and dead-letter handling are essential |
| Pub/Sub + Dataflow | Stream transformations, event-time/windowing, routing, validation, enrichment | More components to operate; checkpointing and sink semantics still matter |

### 6.2 Storage Write API stream types

- **Default stream:** append-only and available for immediate querying after acknowledgement, but delivery is at-least-once. It is convenient for simple event producers.
- **Committed stream:** application-created; acknowledged rows become queryable, and offsets allow exactly-once writes within the stream. Persist offset state and retry the same offset after an ambiguous result.
- **Pending stream:** rows remain buffered until the stream is finalized and committed; useful for batch-like atomic publication.
- **Buffered stream:** intermediate mode with different visibility/flush behavior; use only when the specific latency/commit semantics match the workload.

Do not describe “exactly once” without naming the scope. Stream-level exactly-once does not make a downstream `MERGE`, external side effect, or second destination exactly-once automatically.

### 6.3 Small Python Storage Write API example (default stream)

The Storage Write API's gRPC Python client uses serialized protobuf rows or Arrow record batches. This example uses a small generated protobuf schema so the wire representation is explicit. It writes to the default stream, so it is **at-least-once**; it is a demonstration of the API path, not a production exactly-once producer.

Install dependencies:

```bash
pip install "google-cloud-bigquery" "google-cloud-bigquery-storage" "protobuf"
```

Create `event.proto`:

```protobuf
syntax = "proto2";
package ingest_lab;

message EventRow {
  required string event_id = 1;
  required string event_ts = 2;
  required string tenant_id = 3;
  required string event_name = 4;
  optional string source_batch_id = 5;
}
```

Compile it with Protocol Buffers compiler installed:

```bash
protoc --python_out=. event.proto
```

Create the destination table first:

```sql
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.ingest_lab.events_streamed` (
  event_id STRING NOT NULL,
  event_ts STRING NOT NULL,
  tenant_id STRING NOT NULL,
  event_name STRING NOT NULL,
  source_batch_id STRING
);
```

Python `write_default_stream.py`:

```python
from google.cloud import bigquery_storage_v1
from google.cloud.bigquery_storage_v1 import types
from google.cloud.bigquery_storage_v1 import writer
from google.protobuf import descriptor_pb2
from event_pb2 import EventRow

PROJECT = "YOUR_PROJECT"
DATASET = "ingest_lab"
TABLE = "events_streamed"

def main():
    client = bigquery_storage_v1.BigQueryWriteClient()
    table_path = client.table_path(PROJECT, DATASET, TABLE)
    stream_name = f"{table_path}/_default"

    request_template = types.AppendRowsRequest()
    request_template.write_stream = stream_name

    proto_schema = types.ProtoSchema()
    proto_descriptor = descriptor_pb2.DescriptorProto()
    EventRow.DESCRIPTOR.CopyToProto(proto_descriptor)
    proto_schema.proto_descriptor = proto_descriptor

    proto_data = types.AppendRowsRequest.ProtoData()
    proto_data.writer_schema = proto_schema
    request_template.proto_rows = proto_data

    stream = writer.AppendRowsStream(client, request_template)
    try:
        rows = [
            EventRow(
                event_id="evt-001",
                event_ts="2026-10-19T09:00:00Z",
                tenant_id="tenant-01",
                event_name="page_view",
                source_batch_id="demo-batch-001",
            ),
            EventRow(
                event_id="evt-002",
                event_ts="2026-10-19T09:00:01Z",
                tenant_id="tenant-01",
                event_name="purchase",
                source_batch_id="demo-batch-001",
            ),
        ]
        proto_rows = types.ProtoRows()
        for row in rows:
            proto_rows.serialized_rows.append(row.SerializeToString())

        request = types.AppendRowsRequest()
        proto_data = types.AppendRowsRequest.ProtoData()
        proto_data.rows = proto_rows
        request.proto_rows = proto_data

        # The returned future must be awaited. A successful acknowledgement
        # means this append was accepted, not that downstream business work ran.
        stream.send(request).result()
        print(f"Appended {len(rows)} rows to {stream_name}")
    finally:
        stream.close()
        client.close()

if __name__ == "__main__":
    main()
```

**Schema mapping note:** the BigQuery destination schema intentionally stores `event_ts` as `STRING`, matching the protobuf field and preserving the raw timestamp representation. In the curated layer, use `SAFE_CAST(event_ts AS TIMESTAMP)` (or a stricter parse/validation expression) and quarantine values that fail. This avoids assuming an ISO timestamp string is automatically mapped to a BigQuery `TIMESTAMP` by the protobuf wire format. For a production typed stream, use the documented timestamp logical representation and verify it against the installed client/API version.

### 6.4 Exactly-once with committed stream offsets

For strict stream-level deduplication, create a `COMMITTED` stream, assign every record/batch a stable sequence, and append with an offset equal to the next expected row offset. Persist the next offset only after the append is acknowledged.

```python
# Pseudocode: exact client call shapes depend on the Storage Write API
# client version and the selected serialized row format.
#
# 1. create WriteStream(type=COMMITTED)
# 2. persist stream_name and next_offset in durable state
# 3. AppendRowsRequest(write_stream=stream_name, offset=next_offset, rows=batch)
# 4. on success: persist next_offset += number_of_rows
# 5. on timeout/unknown outcome: retry same batch at same offset
# 6. if offset already exists: verify the previous append was accepted
# 7. never allocate a new offset merely because the client timed out
```

Offsets are scoped to a stream. If an application restarts and creates a new stream, the old stream's offset does not deduplicate records in the new stream. Keep a durable mapping between source offsets/event IDs and stream offsets; design replay across stream recreation explicitly.

### 6.5 Legacy `insertAll`, streaming buffers, and DML

`tabledata.insertAll` is the legacy streaming-insert API. Its `insertId` mechanism can provide best-effort duplicate suppression, but it is not a strict exactly-once contract. If using it, treat source event IDs and downstream deduplication as the correctness layer.

Recently streamed rows can reside in a streaming buffer. Some operations/metadata may not reflect those rows immediately, and recently streamed data can have limitations for operations such as copy/export or certain DML patterns depending on ingestion path and current product behavior. Do not assume a just-streamed row can immediately be updated/deleted by a `MERGE`; verify the current streaming/DML documentation and design a staging/curation delay if needed.

Streaming costs vary by API and current pricing. Batch load jobs from Cloud Storage are often the cheaper default when minutes/hours of latency are acceptable. Compare current Storage Write API pricing, legacy streaming pricing, Pub/Sub subscription pricing, Dataflow costs, and the cost of operating the pipeline. Do not hard-code a price from an old tutorial.

### 6.6 Pub/Sub BigQuery subscriptions and Topic 06

Use a Pub/Sub BigQuery subscription when messages can be written directly to a compatible BigQuery table without per-message transformations. Configure the destination table, schema mode (topic schema, table schema, or raw `data` column), optional message metadata, unknown-field behavior, and a dead-letter topic.

Constraints to design for:

- The destination table and schema must exist and be compatible.
- A malformed/incompatible message may fail to write and remain unacknowledged.
- A dead-letter topic is strongly recommended for undeliverable messages; monitor it and replay after fixing the schema/data.
- Throughput and Storage Write API quotas apply.
- Direct subscriptions are not a substitute for Dataflow when you need windowing, enrichment, routing, complex validation, or multiple sinks.
- Message redelivery means downstream business idempotency still needs a plan.

Topic 06 extends this by using Pub/Sub + Dataflow to transform, validate, enrich, and route events before BigQuery writes.

---

## 7. Schema evolution and data contracts

### 7.1 Prefer additive, backward-compatible changes

A data contract should specify field names, types, nullability, meaning, units, timestamp timezone, event identity, and schema version.

Generally safer changes include:

- Adding a nullable field.
- Relaxing a required field to nullable when downstream consumers support nulls.
- Adding a field to a supported append/load workflow with an explicit schema-update option.

Potentially breaking changes include:

- Renaming/removing a field.
- Changing a type incompatibly (for example, `STRING` to `INT64` without a migration).
- Making a nullable field required without backfilling/validating existing rows.
- Reusing a field name for a different business meaning.
- Changing timestamp timezone conventions or numeric units.

### 7.2 `ALLOW_FIELD_ADDITION` and `ALLOW_FIELD_RELAXATION`

For supported load/query append jobs:

```python
config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    schema_update_options=[
        bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
        bigquery.SchemaUpdateOption.ALLOW_FIELD_RELAXATION,
    ],
)
```

These options do not make arbitrary schema changes safe. Adding a new field to an existing table generally requires the new field to be `NULLABLE` or `REPEATED`; a new required field cannot be populated for existing rows by a schema-only change. Relaxation changes a `REQUIRED` field to `NULLABLE`; it does not convert an incompatible data type.

Schema-update options are supported only for particular job types/write dispositions. Confirm current restrictions before relying on them for a specific load/query path. For breaking changes, create a new versioned table or migrate via a controlled backfill and compatibility view.

### 7.3 Contract rollout procedure

1. Publish the new schema version and compatibility rules.
2. Add nullable field(s) to the destination schema or use a supported additive update.
3. Deploy producers that populate the new field while retaining old fields during the migration window.
4. Validate row counts, null rates, type parse failures, and semantic constraints.
5. Update downstream consumers.
6. Only later deprecate old fields after consumer inventory and sign-off.
7. Record schema version with each file/batch/event where possible.

### 7.4 Raw-first typing

For feeds with uncertain quality, land source values as raw strings/JSON or preserve the original source object, then cast in a curated transformation. This avoids losing the original payload when a type conversion fails. Use explicit typed tables for trusted downstream analytics, but retain the raw evidence needed for replay and investigation.

---

## 8. CDC, upserts, deletes, and deduplication

### 8.1 CDC event contract

A CDC record should preserve at least:

- primary/business key
- operation (`INSERT`, `UPDATE`, `DELETE`, or source-specific equivalent)
- source commit timestamp and/or log sequence/offset
- source transaction identifier if available
- payload after change (and before image when needed)
- source table/database identity
- ingestion timestamp
- source batch/stream identity

A timestamp alone may not order changes deterministically. Prefer a source log position/LSN/SCN/binlog coordinate or version when the connector provides one.

### 8.2 Deduplicate a staging batch

Assume a CDC staging table has `customer_id`, `source_sequence`, `source_commit_ts`, `operation`, `name`, `status`, and `ingested_at`. Keep the latest deterministic change per key before applying it:

```sql
CREATE OR REPLACE TABLE `YOUR_PROJECT.ingest_lab.cdc_latest` AS
SELECT * EXCEPT(row_num)
FROM (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY customer_id
      ORDER BY source_sequence DESC, source_commit_ts DESC, ingested_at DESC
    ) AS row_num
  FROM `YOUR_PROJECT.ingest_lab.cdc_stage`
)
WHERE row_num = 1;
```

The order must be deterministic. If `source_sequence` is not comparable across source partitions/tables, include the source identity or use the connector's ordering guarantees. Add a stable source event/transaction identifier as a final tie-breaker when the source can emit equal sequence/timestamp values; if no valid deterministic order can be established, quarantine the conflicting key rather than choosing an arbitrary row. Do not use `ingested_at` as the only ordering field if events can arrive out of order.

### 8.3 Apply inserts/updates/deletes with `MERGE`

For a current-state table keyed by `customer_id`:

```sql
MERGE `YOUR_PROJECT.ingest_lab.customer_current` AS T
USING `YOUR_PROJECT.ingest_lab.cdc_latest` AS S
ON T.customer_id = S.customer_id
WHEN MATCHED
  AND S.operation = 'DELETE'
  AND S.source_sequence > COALESCE(T.source_sequence, -1)
THEN DELETE
WHEN MATCHED AND S.operation IN ('INSERT', 'UPDATE')
  AND (
    T.source_sequence IS NULL
    OR S.source_sequence > T.source_sequence
  )
THEN UPDATE SET
  name = S.name,
  status = S.status,
  source_sequence = S.source_sequence,
  source_commit_ts = S.source_commit_ts
WHEN NOT MATCHED AND S.operation IN ('INSERT', 'UPDATE')
THEN INSERT (
  customer_id, name, status, source_sequence, source_commit_ts
) VALUES (
  S.customer_id, S.name, S.status, S.source_sequence, S.source_commit_ts
);
```

This example assumes `source_sequence` is a non-negative, comparable, monotonically increasing value per key. If the source provides a composite ordering key, use that. A delete for a key absent from the target is intentionally a no-op. If the pipeline can replay older events after a delete, a physically deleted row loses its last sequence number; use a tombstone/current-state version table or a durable processed-offset ledger so stale replays cannot resurrect deleted data.

### 8.4 Transaction boundaries and exactly-once business state

`MERGE` is a BigQuery DML operation with atomic statement behavior, but the entire ingestion pipeline is not automatically one distributed transaction. Loading CDC to staging, updating the target, and marking source offsets processed are separate steps unless coordinated by a supported transaction/orchestration design.

Safer pattern:

1. Persist source batch/offset and load into a staging table idempotently.
2. Deduplicate staging by primary key and source order.
3. Apply one deterministic `MERGE` to current state.
4. Record reconciliation and committed watermark in durable pipeline state only after the target operation succeeds.
5. Re-running the same staging batch should leave the current state unchanged.
6. Keep delete tombstones or a processed-offset ledger when replay could otherwise resurrect stale rows.

### 8.5 Datastream

Datastream is a serverless change data capture and replication service with supported sources that include MySQL, PostgreSQL, and Oracle, subject to source engine/version and configuration requirements. Current support also includes other sources in some product configurations; verify the source-specific matrix rather than treating the list as fixed.

For BigQuery destinations, understand:

- Initial backfill versus ongoing changes.
- Primary-key discovery/requirements and how keys map to destination tables.
- Destination write mode and CDC merge behavior.
- `max_staleness` / freshness-versus-cost behavior where applicable.
- Source log retention, network connectivity, permissions, and replication lag.
- Schema evolution and unsupported source types/DDL.
- How to reconcile source counts and recover after a gap.

Do not run a second independent `MERGE` against a Datastream-managed destination without understanding the connector's own change application semantics.

### 8.6 BigQuery native CDC ingestion versus a custom `MERGE`

BigQuery also supports native CDC ingestion through the Storage Write API. In that model, stream protobuf rows to a destination table with a declared primary key (`PRIMARY KEY (...) NOT ENFORCED`) and use the `_CHANGE_TYPE` pseudocolumn with `UPSERT` or `DELETE`; `_CHANGE_SEQUENCE_NUMBER` can provide a source-defined ordering value where required. This is a different path from loading ordinary event rows into a staging table and running your own SQL `MERGE`.

Important boundaries for native CDC:

- It uses the Storage Write API gRPC default stream and protobuf format for CDC row mutations; it is not the same as the committed-stream-offset pattern described in Section 6.4.
- BigQuery does not enforce declared primary-key uniqueness. The producer/CDC source must preserve key correctness.
- Tables with active native CDC do not support mutating SQL DML such as `UPDATE`, `DELETE`, or `MERGE`; do not apply the custom `MERGE` pattern from Section 8.3 to the same active-CDC destination.
- `max_staleness` controls freshness versus query latency/cost. Pending row modifications may be applied in background jobs or at query time; resource availability, reservation assignment, and current CDC pricing matter.
- Validate source ordering, delete handling, table schema, and connector behavior against the current CDC documentation before rollout.

Choose native CDC when the supported Storage Write API mutation contract fits the source and operational requirements. Choose a staging-table plus `MERGE` design when you need to own validation, transformation, deduplication, and application semantics in SQL. Do not combine the two patterns on the same target without a documented design.

---

## 9. Failure handling, quarantine, replay, and reconciliation

### 9.1 Why `max_bad_records` is not a quarantine table

A load job's bad-record tolerance can allow some rows to be skipped, but it does not provide a complete durable table of every rejected payload. Job error details are diagnostic and may be limited. If row-level quarantine is a requirement, explicitly capture raw rows before typed ingestion.

### 9.2 Robust quarantine patterns

**Pattern A — Immutable source file + strict typed load**

- Preserve the source object in a landing bucket with object generation/checksum.
- Load with `max_bad_records=0`.
- On failure, keep the object and job metadata; parse/validate it into accepted and rejected outputs with a separate validation step.
- Replay only after correcting the cause, using a new attempt record and reconciliation.

**Pattern B — Raw text/JSON staging + typed transform**

- Load each line into a raw table with batch ID, source URI, line/event ID, payload, and ingestion timestamp.
- Use `SAFE_CAST`/JSON parsing in a query to create accepted rows.
- Route invalid rows to a quarantine table with failure reason and original payload.
- Reconcile accepted + rejected = source records, accounting explicitly for headers/blank lines and duplicate policy.

### 9.3 Quarantine example using raw JSON strings

Raw table:

```sql
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.ingest_lab.raw_lines` (
  batch_id STRING,
  source_uri STRING,
  line_number INT64,
  raw_payload STRING,
  ingested_at TIMESTAMP
);
```

Validation into accepted records:

```sql
CREATE OR REPLACE TABLE `YOUR_PROJECT.ingest_lab.events_validated` AS
WITH parsed AS (
  SELECT
    batch_id,
    source_uri,
    line_number,
    raw_payload,
    JSON_VALUE(raw_payload, '$.event_id') AS event_id,
    SAFE_CAST(JSON_VALUE(raw_payload, '$.event_ts') AS TIMESTAMP) AS event_ts,
    JSON_VALUE(raw_payload, '$.tenant_id') AS tenant_id,
    JSON_VALUE(raw_payload, '$.event_name') AS event_name,
    ingested_at
  FROM `YOUR_PROJECT.ingest_lab.raw_lines`
)
SELECT *
FROM parsed
WHERE event_id IS NOT NULL
  AND event_ts IS NOT NULL
  AND tenant_id IS NOT NULL
  AND event_name IS NOT NULL;
```

Quarantine invalid rows:

```sql
CREATE OR REPLACE TABLE `YOUR_PROJECT.ingest_lab.events_quarantine` AS
WITH parsed AS (
  SELECT
    *,
    JSON_VALUE(raw_payload, '$.event_id') AS event_id,
    SAFE_CAST(JSON_VALUE(raw_payload, '$.event_ts') AS TIMESTAMP) AS event_ts,
    JSON_VALUE(raw_payload, '$.tenant_id') AS tenant_id,
    JSON_VALUE(raw_payload, '$.event_name') AS event_name
  FROM `YOUR_PROJECT.ingest_lab.raw_lines`
)
SELECT
  *,
  CASE
    WHEN event_id IS NULL THEN 'missing_event_id'
    WHEN event_ts IS NULL THEN 'invalid_or_missing_event_ts'
    WHEN tenant_id IS NULL THEN 'missing_tenant_id'
    WHEN event_name IS NULL THEN 'missing_event_name'
    ELSE 'unknown_validation_failure'
  END AS quarantine_reason
FROM parsed
WHERE event_id IS NULL
   OR event_ts IS NULL
   OR tenant_id IS NULL
   OR event_name IS NULL;
```

The two statements repeat parsing; for production, materialize a parsed staging table or use a view so the validation logic has one maintained definition. The example is illustrative and treats each raw payload as a JSON object per row. For CSV, parse using a CSV-aware ingestion/validation tool rather than splitting on commas (quoted delimiters make naive splitting unsafe).

### 9.4 Replay without duplication

Replay is safe only if the destination write is idempotent for the same logical batch/event. Options include:

- Retry a known load job by the same job ID and inspect its state.
- Load each immutable batch into a batch-specific staging table, then `MERGE` by stable event ID.
- Deduplicate events with `QUALIFY ROW_NUMBER()` and a deterministic ordering rule.
- Track source offsets/watermarks and commit them only after target success.
- For Storage Write API committed streams, retry the same offset after an unknown outcome.
- Keep source files/events until reconciliation succeeds and retention policy permits deletion.

Never replay a failed or ambiguous append into a shared target under a new job ID without checking whether the original job succeeded.

### 9.5 Reconciliation checks

Examples of operational checks:

```sql
-- Raw count by batch.
SELECT batch_id, COUNT(*) AS raw_rows
FROM `YOUR_PROJECT.ingest_lab.raw_lines`
GROUP BY batch_id;

-- Accepted and quarantined rows by batch.
SELECT batch_id, 'accepted' AS disposition, COUNT(*) AS row_count
FROM `YOUR_PROJECT.ingest_lab.events_validated`
GROUP BY batch_id
UNION ALL
SELECT batch_id, 'quarantined' AS disposition, COUNT(*) AS row_count
FROM `YOUR_PROJECT.ingest_lab.events_quarantine`
GROUP BY batch_id;

-- Duplicate business event IDs in curated data.
SELECT event_id, COUNT(*) AS copies
FROM `YOUR_PROJECT.ingest_lab.events_validated`
GROUP BY event_id
HAVING COUNT(*) > 1;
```

Define the counting unit: source lines, valid records, unique events, or current-state entities. The expected equation may be `source records = accepted + rejected`, while unique curated event count is smaller because duplicates are intentionally removed. Document that distinction.

---

## 10. Ingestion-method comparison matrix

| Method | Freshness | Typical fit | Duplicate/retry design | Main costs/risks |
|---|---|---|---|---|
| Cloud Storage load job | Batch | Large files and scheduled drops | Stable batch identity + deterministic job ID + immutable source + disposition/reconciliation | Load quotas, source storage/network, bad-record handling |
| Local/DataFrame load job | Batch | Small controlled files or Python-produced frames | Persist batch ID; avoid resubmitting same content as a new append | Client memory/serialization; DataFrame type mapping |
| External table | On-demand | Lake exploration, open formats, avoiding copy | Source object naming/versioning and file lifecycle | Query latency, file listing, source access, query and storage/network costs |
| BigLake | On-demand | Governed external access and supported metadata caching | Same external-source controls plus connection/IAM | Connection/IAM complexity, metadata staleness, supported-source limitations |
| Storage Write API default stream | Low latency | Event ingestion where duplicates can be handled downstream | Stable event IDs + dedupe/reconciliation | Streaming charges/quotas, schema drift, duplicate delivery |
| Storage Write API committed stream | Low latency | Stream-level exactly-once requirements | Durable stream identity and offsets; retry same offset | Offset state, stream lifecycle, application complexity |
| Legacy `insertAll` | Low latency | Existing systems requiring compatibility | Do not rely solely on insert IDs; dedupe in raw/curated layer | Legacy semantics, best-effort dedupe, current pricing/features |
| Pub/Sub BigQuery subscription | Low latency managed direct write | Events with table-compatible schema and little transformation | Message/event ID, schema compatibility, dead-letter/replay | Pub/Sub pricing, write quotas, schema failure/backlog |
| Pub/Sub + Dataflow | Low latency transformed stream | Enrichment, windows, validation, multiple routes | Dataflow state/checkpoints + stable event key + sink strategy | Pipeline operations, worker cost, backpressure, replay semantics |
| Datastream CDC | Continuous replication | Supported operational DB CDC | Source log position/PK semantics + destination reconciliation | Source compatibility, log retention, networking, lag, CDC merge cost |
| Federated query | On-demand live read | Small/current lookups against supported Cloud SQL/Spanner | Source-side transaction semantics; not a copy pipeline | Source load, network/region charges, latency, availability coupling |
| BigQuery Data Transfer Service | Scheduled managed transfer | Supported SaaS/cross-cloud connectors | Connector-specific incremental keys/backfill/retry semantics | Connector coverage, credentials, source/API quotas, transfer charges |

---

## 11. Hands-on experiments

### 11.1 Lab folder layout

```text
experiments/04_loading/
├── README.md
├── requirements.txt
├── 01_load_parquet_idempotently.py
├── 02_create_hive_external.sql
├── 03_storage_write_api/
│   ├── event.proto
│   ├── write_default_stream.py
│   └── README.md
├── 04_apply_cdc.sql
├── 05_quarantine_invalid_rows.sql
├── 06_load_job_audit.sql
└── results-template.csv
```

Use a dedicated project/dataset and a Cloud Storage bucket in a compatible location. Set a budget alert before running any scale-up. These exercises default to small samples; they do not create a million events automatically. Before using external tables, verify that the source object layout and Hive partition types match the DDL. Before using the Storage Write API, verify the installed client version and generated protobuf module against the official sample.

### 11.2 Requirements and service setup

`requirements.txt`:

```text
google-cloud-bigquery
google-cloud-bigquery-storage
google-cloud-storage
pandas
pyarrow
db-dtypes
```

Enable the APIs used by the labs:

```bash
gcloud services enable \
  bigquery.googleapis.com \
  bigquerystorage.googleapis.com \
  storage.googleapis.com
```

Additional exercises may require:

- Pub/Sub API and a Pub/Sub service agent with write access to the destination table for direct subscriptions.
- Datastream API, source DB access, destination permissions, and network connectivity for CDC.
- BigQuery Connection API and source-specific permissions for federated queries.
- BigQuery Data Transfer Service API and connector-specific source credentials for managed transfers.

The person running `bq`/Python needs permission to create jobs, read source objects, create/write destination tables, and inspect job metadata. Use least privilege and a dedicated lab dataset.

### 11.3 Create the lab dataset and schema

Choose a location (example `US`) and keep the dataset, bucket, external source, and jobs in compatible locations:

```bash
bq --location=US mk --dataset YOUR_PROJECT:ingest_lab
```

Create a native raw table:

```sql
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.ingest_lab.events_raw` (
  event_id STRING NOT NULL,
  event_ts TIMESTAMP NOT NULL,
  tenant_id STRING NOT NULL,
  event_name STRING NOT NULL,
  user_id STRING,
  amount NUMERIC,
  source_batch_id STRING NOT NULL,
  ingested_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(event_ts)
CLUSTER BY tenant_id, event_name;
```

Before inserting data, confirm that the schema, partition key, and clustering columns match Topic 03's query patterns. Do not create clustering/partitioning by habit if the sample is tiny; the DDL is for learning the physical design.

### 11.4 Exercise 1 — Load Parquet with deterministic job ID and safe retry

Create a small Parquet file from Python using pandas/pyarrow, or use a compatible Parquet file in your own GCS bucket. Do not rely on a mutable URI for a production retry.

`01_load_parquet_idempotently.py` should:

1. Read an immutable source URI and capture object generation/checksum from Cloud Storage metadata.
2. Build a batch identity including URI, generation/checksum, destination, write disposition, and schema version.
3. Generate the deterministic job ID from the identity.
4. Submit the load with `load_table_from_uri`.
5. On conflict/timeout, fetch the same job ID and poll it; do not create a new append job blindly.
6. Check `job.error_result`, `job.errors`, `job.output_rows`, and `job.input_files`.
7. Record the batch ID and committed status in an ingestion ledger.
8. Verify destination row counts and event IDs.

Example retry skeleton:

```python
import hashlib
from google.api_core.exceptions import Conflict, DeadlineExceeded, NotFound, ServiceUnavailable
from google.cloud import bigquery, storage

PROJECT = "YOUR_PROJECT"
BUCKET = "YOUR_BUCKET"
OBJECT = "events/batch_id=batch-001/part-000.parquet"
DESTINATION = f"{PROJECT}.ingest_lab.events_raw"
LOCATION = "US"

# Match this explicit schema to the Parquet file's physical/logical schema.
EVENT_SCHEMA = [
    bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("event_ts", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("tenant_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("event_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("user_id", "STRING"),
    bigquery.SchemaField("amount", "NUMERIC"),
    bigquery.SchemaField("source_batch_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="REQUIRED"),
]

storage_client = storage.Client(project=PROJECT)
blob = storage_client.bucket(BUCKET).blob(OBJECT)
blob.reload()  # Requires permission to read object metadata.
if blob.generation is None:
    raise RuntimeError("Could not determine source object generation")
uri = f"gs://{BUCKET}/{OBJECT}"
batch_identity = (
    f"uri={uri};generation={blob.generation};destination={DESTINATION};"
    "disposition=WRITE_APPEND;schema=v1"
)
job_id = "load_" + hashlib.sha256(batch_identity.encode()).hexdigest()[:32]
client = bigquery.Client(project=PROJECT)
config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.PARQUET,
    schema=EVENT_SCHEMA,
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    max_bad_records=0,
)
try:
    job = client.load_table_from_uri(
        uri, DESTINATION, job_id=job_id, job_config=config, location=LOCATION
    )
except Conflict:
    job = client.get_job(job_id, location=LOCATION)
except (DeadlineExceeded, ServiceUnavailable):
    # Unknown submit outcome: inspect/re-submit only under the SAME job ID.
    try:
        job = client.get_job(job_id, location=LOCATION)
    except NotFound:
        try:
            job = client.load_table_from_uri(
                uri, DESTINATION, job_id=job_id,
                job_config=config, location=LOCATION
            )
        except Conflict:
            job = client.get_job(job_id, location=LOCATION)

try:
    job.result()
except Exception as exc:
    job.reload()
    if job.error_result:
        raise RuntimeError(f"Load failed: {job.error_result}") from exc
    raise
print("job_id", job.job_id, "rows", job.output_rows, "errors", job.errors)
# A generation in the identity does NOT pin the gs:// URI to that generation.
# Ensure this object path is immutable, or copy the chosen generation to a unique path.
```

This is a skeleton: replace the generation placeholder with a real object generation obtained from Cloud Storage metadata, use an explicit schema in production, and handle terminal failed jobs with a recorded retry-attempt policy. The deterministic job ID protects a retry of the same job submission; it does not deduplicate a new job that loads the same source again. A normal Cloud Storage URI reads the live object path rather than pinning a recorded object generation, so enforce immutability or copy the selected object generation to a unique immutable path before loading.

**Expected validation:** the same logical batch and same job ID should resolve to one BigQuery job; verify that the ledger records the job's final state and output row count. Re-running with a different ID is a new append and can duplicate rows. Verify that the pipeline prevents that second case. The code sample is a retry skeleton, not a complete ledger implementation; implement and test the ledger transaction around job submission before treating it as production-ready.

### 11.5 Exercise 2 — Hive-partitioned Parquet external vs native

Organize files as:

```text
gs://YOUR_BUCKET/events/
  event_date=2026-10-18/tenant=tenant-01/part-000.parquet
  event_date=2026-10-19/tenant=tenant-01/part-000.parquet
```

`02_create_hive_external.sql`:

```sql
CREATE OR REPLACE EXTERNAL TABLE `YOUR_PROJECT.ingest_lab.events_external`
WITH PARTITION COLUMNS (
  event_date DATE,
  tenant STRING
)
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://YOUR_BUCKET/events/*'],
  hive_partition_uri_prefix = 'gs://YOUR_BUCKET/events',
  require_hive_partition_filter = TRUE
);
```

Create a native comparison table from the external data:

```sql
CREATE OR REPLACE TABLE `YOUR_PROJECT.ingest_lab.events_native_copy`
PARTITION BY event_date
CLUSTER BY tenant, event_name
AS
SELECT
  event_id,
  event_ts,
  event_date,
  tenant,
  event_name,
  user_id,
  amount
FROM `YOUR_PROJECT.ingest_lab.events_external`
WHERE event_date >= DATE '2026-10-01'
  AND event_date < DATE '2026-11-01';
```

Adjust the projected columns to match the real Parquet schema. Run equivalent queries on external and native tables with result caching controlled, and record bytes processed/billed, elapsed time, source file count/size, and row counts. Expected observations: results and row counts should agree; the native copy adds load and storage costs, while external-query latency may be more sensitive to object count and metadata listing. Neither option is guaranteed to win without measurement. The external table's schema must include the data fields plus the Hive partition columns. Do not assume an external table is faster or cheaper merely because it avoids loading.

### 11.6 Exercise 3 — Storage Write API streaming (small scale)

Use the schema and Python example in Section 6.3. Start with **2–100 rows**. Validate:

```sql
SELECT
  COUNT(*) AS row_count,
  COUNT(DISTINCT event_id) AS unique_events,
  COUNTIF(event_ts IS NULL OR SAFE_CAST(event_ts AS TIMESTAMP) IS NULL) AS invalid_timestamps
FROM `YOUR_PROJECT.ingest_lab.events_streamed`;
```

Record acknowledgement latency, errors, row count, duplicate count, and whether the destination schema matches. Expected result: the first run should append the two sample rows when the request succeeds; the default stream is at-least-once, so rerunning can append duplicates (though duplicate appearance is not guaranteed on every run). Verify event IDs and timestamps, and deduplicate in the curated layer if this behavior is unacceptable. Do not treat a small two-row sample as a throughput benchmark.

**Scale-up procedure:** do not start with one million events. First validate 100 rows, then 1,000, then 10,000 while measuring payload size, throughput, error rate, latency, quota headroom, and cost. Increase batch size/concurrency only after observing the results. The roadmap's one-million-event run is an advanced scale test: perform it only after the small tests pass, with a documented budget, quota review, cleanup plan, event identity/deduplication strategy, and an agreed test window. Record real measurements; never copy invented throughput or latency values into the results template.

### 11.7 Exercise 4 — CDC `MERGE` with updates and deletes

Create staging and target tables:

```sql
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.ingest_lab.customer_current` (
  customer_id STRING NOT NULL,
  name STRING,
  status STRING,
  source_sequence INT64,
  source_commit_ts TIMESTAMP,
  is_deleted BOOL
);

CREATE OR REPLACE TABLE `YOUR_PROJECT.ingest_lab.cdc_stage` AS
SELECT * FROM UNNEST([
  STRUCT('c1' AS customer_id, 1 AS source_sequence,
         TIMESTAMP '2026-10-19 08:00:00+00' AS source_commit_ts,
         'INSERT' AS operation, 'Asha' AS name, 'active' AS status),
  STRUCT('c2', 1, TIMESTAMP '2026-10-19 08:00:01+00',
         'INSERT', 'Ravi', 'active'),
  STRUCT('c1', 2, TIMESTAMP '2026-10-19 08:05:00+00',
         'UPDATE', 'Asha', 'premium'),
  STRUCT('c2', 2, TIMESTAMP '2026-10-19 08:06:00+00',
         'DELETE', CAST(NULL AS STRING), CAST(NULL AS STRING))
]);
```

Deduplicate and apply the latest change. This exercise uses `is_deleted` as a tombstone to prevent stale replay from resurrecting a deleted key:

```sql
CREATE OR REPLACE TABLE `YOUR_PROJECT.ingest_lab.cdc_latest` AS
SELECT * EXCEPT(rn)
FROM (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY customer_id
      ORDER BY source_sequence DESC, source_commit_ts DESC
    ) AS rn
  FROM `YOUR_PROJECT.ingest_lab.cdc_stage`
)
WHERE rn = 1;

MERGE `YOUR_PROJECT.ingest_lab.customer_current` T
USING `YOUR_PROJECT.ingest_lab.cdc_latest` S
ON T.customer_id = S.customer_id
WHEN MATCHED AND S.source_sequence > COALESCE(T.source_sequence, -1)
THEN UPDATE SET
  name = IF(S.operation = 'DELETE', T.name, S.name),
  status = IF(S.operation = 'DELETE', T.status, S.status),
  source_sequence = S.source_sequence,
  source_commit_ts = S.source_commit_ts,
  is_deleted = (S.operation = 'DELETE')
WHEN NOT MATCHED AND S.operation IN ('INSERT', 'UPDATE', 'DELETE') THEN
  INSERT (customer_id, name, status, source_sequence, source_commit_ts, is_deleted)
  VALUES (
    S.customer_id, S.name, S.status, S.source_sequence,
    S.source_commit_ts, S.operation = 'DELETE'
  );
```

The target stores tombstones rather than physically removing rows. Curated consumers filter `WHERE NOT is_deleted`. For production, ensure sequence ordering is valid per key and add a deterministic tie-breaker if source sequence can tie. Verify that replaying the same staging rows leaves the target unchanged and that a later valid sequence can update a tombstone.

Validation:

```sql
SELECT customer_id, name, status, source_sequence, is_deleted
FROM `YOUR_PROJECT.ingest_lab.customer_current`
ORDER BY customer_id;
```

Expected state: `c1` is `premium` and not deleted; `c2` has `is_deleted = TRUE`. The exact row count should be two tombstoned/current-state keys.

### 11.8 Exercise 5 — Invalid rows and quarantine

Create `raw_lines` and load newline-delimited JSON strings with a strict raw schema. Include valid and invalid records, for example:

```json
{"event_id":"evt-1","event_ts":"2026-10-19T09:00:00Z","tenant_id":"t1","event_name":"page_view"}
{"event_id":"evt-2","event_ts":"not-a-timestamp","tenant_id":"t1","event_name":"purchase"}
{"event_ts":"2026-10-19T09:02:00Z","tenant_id":"t2","event_name":"search"}
```

Load into a raw table with columns `batch_id STRING`, `source_uri STRING`, `line_number INT64`, `raw_payload STRING`, `ingested_at TIMESTAMP`. Run the accepted/quarantine SQL in Section 9.3. Validate that the valid event is accepted and the malformed timestamp/missing ID rows are quarantined with reasons.

Do not rely on `max_bad_records` to produce a rejected-row table. For a true CSV feed, use a CSV-aware parser or Dataflow pipeline to preserve original row content and line numbers; do not split CSV lines naïvely on commas.

### 11.9 Exercise 6 — Load-job metadata and data quality

Query recent load jobs in the correct BigQuery region:

```sql
SELECT
  creation_time,
  job_id,
  user_email,
  destination_table.project_id AS destination_project,
  destination_table.dataset_id AS destination_dataset,
  destination_table.table_id AS destination_table,
  source_uris,
  source_format,
  write_disposition,
  state,
  error_result.reason AS error_reason,
  error_result.message AS error_message,
  input_files,
  input_file_bytes,
  output_rows,
  bad_records
FROM `YOUR_PROJECT.region-us.INFORMATION_SCHEMA.LOAD_JOBS_BY_PROJECT`
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY creation_time DESC
LIMIT 100;
```

Use the region qualifier matching the job location (for example `region-us`); `INFORMATION_SCHEMA` region must match the data/job location. Metadata columns can vary by view/version; confirm the current `LOAD_JOBS` schema if a field is unavailable.

Expected observations: only load jobs visible to the selected project/region and within the seven-day creation-time window appear; a successful job should have a final state and output count consistent with the source manifest, unless an explicitly tolerated bad-record policy applies. Compare `output_rows` with the expected batch row count and the source manifest. For the lab, also query the destination:

```sql
SELECT
  source_batch_id,
  COUNT(*) AS rows_loaded,
  COUNT(DISTINCT event_id) AS unique_event_ids,
  COUNTIF(event_id IS NULL) AS null_event_ids,
  COUNTIF(event_ts IS NULL) AS null_event_timestamps
FROM `YOUR_PROJECT.ingest_lab.events_raw`
GROUP BY source_batch_id;
```

A job being `DONE` is not enough. Check whether it succeeded, whether bad records were skipped, whether row counts reconcile, and whether the destination contains duplicate business keys.

### 11.10 Results template

Record real measurements only:

| Field | What to record |
|---|---|
| `run_id` | Unique measurement ID |
| `method` | load job / external / Storage Write API / CDC / transfer |
| `source_identity` | URI + generation/checksum, event range, or source offset |
| `destination` | Project/dataset/table |
| `schema_version` | Contract version |
| `location` | Region/multi-region |
| `input_files` / `input_bytes` | Job/source metadata |
| `expected_rows` | Manifest or producer count |
| `output_rows` | Job output count |
| `bad_records` | Job metadata if available |
| `accepted_rows` / `quarantined_rows` | From quality queries |
| `duplicate_keys` | Count from dedupe checks |
| `elapsed_ms` | Job/producer elapsed time |
| `stream_ack_latency_ms` | For streaming tests |
| `retry_count` | Retries by attempt |
| `estimated_cost` | If calculated with documented assumptions |
| `actual_cost_source` | Billing export/SKU/period or not reconciled |
| `notes` | Error, cache, data layout, replay outcome |

### 11.11 Cleanup

First verify you are in the dedicated lab dataset and have exported any results you need. Then remove lab tables:

```sql
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.events_external`;
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.events_hive_external`;
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.events_biglake`;
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.events_native_copy`;
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.events_raw`;
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.events_csv`;
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.events_streamed`;
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.cdc_stage`;
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.cdc_latest`;
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.customer_current`;
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.raw_lines`;
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.events_validated`;
DROP TABLE IF EXISTS `YOUR_PROJECT.ingest_lab.events_quarantine`;
```

Remove the lab bucket objects only if you created them for this exercise and verified their paths. Stop/delete Pub/Sub subscriptions, topics, Dataflow jobs, Datastream streams, and BigQuery connections only if they were created for this lab. Do not delete shared production resources.

---

## 12. Operational troubleshooting and common mistakes

| Symptom | Likely cause | Action |
|---|---|---|
| Load job succeeds but row count is lower than source | `max_bad_records`, source filtering, header handling, or malformed records | Inspect `bad_records`, job errors, manifest counts, and quarantine path |
| Same file appears twice | Retry created a new job ID or a batch was submitted twice | Persist immutable batch identity and job ID; reconcile destination keys |
| Job ID conflict | Job already exists for that ID | Fetch job by ID and inspect state/result; never change job config under the same ID |
| `WRITE_EMPTY` fails | Destination is not empty | Decide whether the batch should be appended or the target reset intentionally |
| `WRITE_TRUNCATE` removed data unexpectedly | Disposition used on shared target or wrong batch | Restrict permissions, use staging, review write mode, and implement rollback/recovery |
| Autodetected schema changed unexpectedly | Source files vary or sample data was misleading | Pin explicit schema; version and validate contract |
| Added column rejected | Required field added to existing table or schema update option unsupported for the job type | Add nullable/repeated field with supported option, then backfill if needed |
| Type change fails | BigQuery cannot safely coerce existing schema/data | Create versioned table and controlled migration; preserve raw source |
| External query slow | Too many tiny files, expensive object listing, poor format, no metadata cache where supported | Compact files, use Hive filters, evaluate BigLake cache or native table |
| External table misses new files temporarily | Metadata/cache staleness or source path pattern | Check URI pattern, cache refresh/staleness, object permissions, and source location |
| Storage Write API duplicates rows | Default stream is at-least-once or retries occurred without offsets | Use stable event IDs and dedupe; committed stream offsets for stream-level exactly-once |
| Committed stream offset error | Wrong offset or uncertain prior append | Retry from durable last confirmed offset; handle already-exists/out-of-range semantics |
| Pub/Sub backlog grows | Schema mismatch, permission error, quota/throughput, destination unavailable | Inspect subscription state, service-agent IAM, dead-letter topic, and throughput quotas |
| CDC resurrects deleted row | Delete physically removed target key and stale event replayed | Retain tombstone/sequence ledger and reject stale source versions |
| `MERGE` produces multiple-match error | Staging has multiple source rows per key | Deduplicate with `QUALIFY ROW_NUMBER()` using deterministic source ordering |
| Federated query overloads source DB | BigQuery repeatedly queries operational source | Materialize/replicate via Datastream or scheduled loads for analytical workloads |
| Streaming data unavailable for DML/copy | Streaming buffer behavior or path-specific restrictions | Check current streaming-buffer documentation; stage/delay curation where needed |
| Quarantine is empty despite skipped rows | `max_bad_records` does not persist complete rejected rows | Preserve raw source and validate into accepted/quarantine tables |
| Ingestion cost unexpectedly high | Streaming path used when batch suffices, external scan, cross-region transfer, or repeated backfills | Review current SKU pricing, batch windows, source/target locations, and transfer logs |

---

## 13. Knowledge-check questions with detailed answers

### Q1. Why is a deterministic job ID useful, and why is it not enough for pipeline idempotency?

**Answer:** Reusing the same job ID allows a retry to discover/poll the original job after a timeout rather than submit another append. But a pipeline can still duplicate data by using a new job ID for the same file, changing the source object behind a URI, or retrying downstream transformations. Idempotency also requires immutable source identity, correct write disposition, persisted batch state, stable event keys, and reconciliation.

### Q2. Which format would you choose for a 50 GB daily file drop?

**Answer:** If the source can produce it reliably, a typed columnar format such as Parquet or Avro is a reasonable starting point. Use a Cloud Storage load job, explicit schema/contract, immutable batch path, deterministic job ID, manifest row counts, and a reconciliation step. Choose format based on upstream support, nested data, interoperability, compression, and schema evolution—not only file extension.

### Q3. How would you handle 5,000 events/second?

**Answer:** Do not decide from event rate alone. Measure payload size, burstiness, freshness SLO, transformation needs, regional quotas, and budget. Use Storage Write API or Pub/Sub with a BigQuery subscription for direct compatible writes; use Pub/Sub + Dataflow when validation/enrichment/windowing/routing is needed. Test a scaled-down workload, use stable event IDs, monitor backlog/errors/latency, and review quotas before ramping.

### Q4. What does exactly-once mean for the Storage Write API?

**Answer:** For application-created committed streams, supplying offsets allows BigQuery to accept records exactly once within that stream. The producer must durably manage offsets and retry the same offset after an unknown outcome. It does not guarantee exactly-once effects across stream recreation, Pub/Sub, transformations, or downstream business operations.

### Q5. Should you use schema autodetection in production?

**Answer:** Only when the source contract is inherently variable and the pipeline explicitly validates and versions inferred schema. For stable production feeds, an explicit schema is more predictable. Autodetection is convenient for exploration but can change types/fields based on sampled data.

### Q6. What is the difference between an external table and BigLake?

**Answer:** Both can expose external data without immediately copying it into native BigQuery storage. BigLake adds connection-based access delegation and supports metadata caching for certain external sources/table types. The actual feature set depends on source and table type. Neither guarantees native-table performance, and external data access/query charges still need consideration.

### Q7. How should invalid rows be quarantined?

**Answer:** Preserve the immutable source or raw payload, then validate rows into accepted and rejected outputs with a reason code, source identity, batch ID, and ingestion timestamp. `max_bad_records` is a tolerance setting, not a durable rejected-row store. Reconcile accepted and rejected counts against the defined source-record counting unit.

### Q8. How do you apply CDC deletes safely?

**Answer:** Carry the operation type and a source ordering/version value. Deduplicate each key to the latest change, apply a deterministic `MERGE`, and retain tombstones or a durable sequence ledger if old changes can replay. A physical delete without a tombstone can allow a stale replay to reinsert the row.

### Q9. When is federation a trap?

**Answer:** When recurring analytics repeatedly scans operational databases, causes source load, has poor latency, crosses regions, or requires stable warehouse performance. Federation is useful for selective live lookups; replicate or transfer data for sustained analytical workloads.

### Q10. What should be checked after a load job reports `DONE`?

**Answer:** Check fatal `error_result`, nonfatal errors, bad-record count, input files/bytes, output rows, destination schema, source-to-target counts, duplicate business keys, and downstream quality checks. `DONE` is a job state, not proof of business correctness.

### Q11. Which source is appropriate for MySQL/PostgreSQL/Oracle CDC?

**Answer:** Datastream is a common managed CDC choice for supported source versions/configurations. Validate the exact source matrix, network setup, source log permissions/retention, primary-key behavior, initial backfill, schema changes, destination semantics, and lag. Do not treat a connector name as a guarantee of support for every engine version.

### Q12. What is the relationship between Topic 04 and Topic 06?

**Answer:** Topic 04 teaches destination write patterns and ingestion guarantees. Topic 06 teaches Pub/Sub and Dataflow as upstream streaming/processing components. A direct Pub/Sub BigQuery subscription is suitable when message schema maps to the table; Dataflow is appropriate when events need transformation, event-time processing, enrichment, validation, or multiple output paths.

---

## 14. Syllabus checkpoint

- [ ] Choose a batch load, external/BigLake, Storage Write API, Pub/Sub subscription, Datastream, federation, or Data Transfer Service pattern for a stated workload.
- [ ] Explain CSV, newline-delimited JSON, Avro, Parquet, and ORC trade-offs.
- [ ] Use explicit schema and explain when autodetection is appropriate.
- [ ] Explain `WRITE_APPEND`, `WRITE_TRUNCATE`, and `WRITE_EMPTY`.
- [ ] Demonstrate deterministic job IDs and explain source immutability, job-state inspection, and new-attempt policy.
- [ ] Use `load_table_from_uri`, `load_table_from_file`, and `load_table_from_dataframe`.
- [ ] Create a Hive-partitioned external table and compare it with a native table.
- [ ] Explain BigLake metadata caching and freshness trade-offs.
- [ ] Explain default stream at-least-once semantics and committed-stream offsets.
- [ ] Explain legacy `insertAll`, streaming buffers, DML caveats, and ingestion costs.
- [ ] Apply additive schema evolution and explain incompatible type changes.
- [ ] Deduplicate CDC with `QUALIFY ROW_NUMBER()` and apply updates/deletes with `MERGE`.
- [ ] Explain Datastream, Pub/Sub BigQuery subscriptions, federation, and Data Transfer Service.
- [ ] Quarantine invalid rows and reconcile source/accepted/rejected counts.
- [ ] Query `INFORMATION_SCHEMA.LOAD_JOBS` metadata and validate row counts.
- [ ] Explain why a Cloud Storage generation in a ledger does not pin a `gs://` load URI, and enforce immutable source paths.
- [ ] Explain the difference between BigQuery native CDC ingestion via `_CHANGE_TYPE` and a custom staging-table `MERGE` pipeline.
- [ ] Describe landing/raw/curated layers and replay safety.

### Checkpoint standard

Move to Topic 05 when you can implement and explain a retry-safe batch load, demonstrate a small streaming write, create an external table, apply CDC including deletes, and reconcile a batch. You should be able to say exactly which guarantee is provided by each service and what remains the pipeline's responsibility.

---

## 15. Summary and transition to Topic 05

Choose ingestion from the freshness requirement, data volume, source semantics, transformation needs, and recovery contract.

- **Batch files:** immutable source object, explicit schema, load job, stable job ID, correct write disposition, reconciliation.
- **External data:** Hive partitioning and file layout matter; evaluate metadata caching and compare native-table performance with total cost.
- **Streaming:** the Storage Write API is the recommended modern path for many workloads; default stream is at-least-once, while committed streams with offsets provide stream-level exactly-once semantics.
- **Schema evolution:** prefer additive nullable fields and explicit contracts; use versioned migrations for breaking changes.
- **CDC:** preserve key, operation, and source ordering metadata; dedupe before `MERGE`; keep tombstones/offset ledgers where replay can resurrect stale rows.
- **Failures:** raw source retention, quarantine, retry state, and reconciliation are core correctness mechanisms, not optional monitoring.
- **Governance:** use least privilege, source/destination location compatibility, budgets, quotas, and workload-specific cost checks.

**Transition to Topic 05 — BigQuery ML and Scheduled Queries:** once data arrives reliably, build transformations, scheduled jobs, routines, and models on top of curated tables. Carry forward the schema contracts, raw/curated boundaries, source watermarks, freshness SLAs, and quality checks you established here.

---

## 16. Official documentation references

Consult the current official documentation before production rollout; API signatures, supported sources, pricing, quotas, and schema rules can change.

1. [Load data from Cloud Storage](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage)
2. [Load Parquet data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-parquet)
3. [Load Avro data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-avro)
4. [Load ORC data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-orc)
5. [Load CSV data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-csv)
6. [Load newline-delimited JSON data](https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-json)
7. [BigQuery Python client reference](https://cloud.google.com/python/docs/reference/bigquery/latest)
8. [Manage table schemas and schema update options](https://cloud.google.com/bigquery/docs/managing-table-schemas)
9. [Create Cloud Storage external tables](https://cloud.google.com/bigquery/docs/external-data-cloud-storage)
10. [Hive-partitioned external tables](https://cloud.google.com/bigquery/docs/hive-partitioned-queries-gcs)
11. [Metadata caching for external data sources](https://cloud.google.com/bigquery/docs/metadata-caching-external-tables)
12. [BigLake overview](https://cloud.google.com/bigquery/docs/biglake-intro)
13. [Storage Write API introduction](https://cloud.google.com/bigquery/docs/write-api-intro)
14. [Stream data using the Storage Write API](https://cloud.google.com/bigquery/docs/write-api-streaming)
15. [Storage Write API best practices and offsets](https://cloud.google.com/bigquery/docs/write-api-best-practices)
16. [Legacy streaming inserts](https://cloud.google.com/bigquery/docs/streaming-data-into-bigquery)
17. [BigQuery pricing](https://cloud.google.com/bigquery/pricing)
18. [Datastream BigQuery destination](https://cloud.google.com/datastream/docs/destination-bigquery)
19. [Datastream FAQ and supported sources](https://cloud.google.com/datastream/docs/faq)
20. [BigQuery CDC with SQL](https://cloud.google.com/bigquery/docs/change-data-capture)
21. [Pub/Sub BigQuery subscriptions](https://cloud.google.com/pubsub/docs/bigquery)
22. [Troubleshoot Pub/Sub BigQuery subscriptions](https://cloud.google.com/pubsub/docs/bigquery-troubleshooting)
23. [Federated queries introduction](https://cloud.google.com/bigquery/docs/federated-queries-intro)
24. [Cloud SQL federated queries](https://cloud.google.com/bigquery/docs/cloud-sql-federated-queries)
25. [Spanner federated queries](https://cloud.google.com/bigquery/docs/spanner-federated-queries)
26. [Bigtable external tables](https://cloud.google.com/bigquery/docs/bigtable-external-data)
27. [BigQuery Data Transfer Service introduction](https://cloud.google.com/bigquery/docs/dts-introduction)
28. [Amazon S3 transfers to BigQuery](https://cloud.google.com/bigquery/docs/s3-transfer)
29. [Azure Blob Storage transfers to BigQuery](https://cloud.google.com/bigquery/docs/azure-blob-storage-transfer)
30. [Current BigQuery Data Transfer Service source catalog](https://cloud.google.com/bigquery/docs/dts-data-sources-intro)
31. [`LOAD_JOBS` information schema](https://cloud.google.com/bigquery/docs/information-schema-load-jobs)
32. [BigQuery IAM roles and permissions](https://cloud.google.com/bigquery/docs/access-control)
33. [Cloud Storage IAM](https://cloud.google.com/storage/docs/access-control/iam-roles)

---

## Validation note

This artifact was statically reviewed for the requested 16-section structure, roadmap coverage, delivery-guarantee distinctions, code-block balance, retry/idempotency caveats, and absence of fabricated benchmark results. The SQL/Python/API examples have **not** been executed against a live Google Cloud project. Before production use, verify current client versions, Storage Write API schema mapping, source engine support, dataset/bucket locations, IAM permissions, quotas, and pricing. In particular, treat the streaming sample as a teaching template until tested in a disposable project; use the official Storage Write API example matching the installed client version.
