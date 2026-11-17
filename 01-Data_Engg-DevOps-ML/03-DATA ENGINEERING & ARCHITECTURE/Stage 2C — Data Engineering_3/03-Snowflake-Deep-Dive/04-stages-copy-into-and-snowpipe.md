# Stages, `COPY INTO`, and Snowpipe

**Roadmap location:** `Stage 2C — Data Engineering_3/03-Snowflake-Deep-Dive/04-stages-copy-into-and-snowpipe.md`  
**Lab location:** `Stage 2C — Data Engineering_3/03-Snowflake-Deep-Dive/experiments/04_loading/`

This lesson follows Topics 01–03: Snowflake architecture and compute, warehouse sizing, and micro-partitions/clustering/pruning. The objective is to ingest data reliably, securely, repeatably, and at a cost appropriate to the required latency.

> **Execution note:** SQL and Python below are worked examples, not claims that a Snowflake account, cloud bucket, IAM role, or benchmark was executed. Replace placeholders, validate privileges and region support, and run experiments in a non-production environment. Run object-creation examples in a fresh, dedicated schema. Examples use fail-fast `CREATE` statements rather than silently replacing same-named objects; if a name already exists, stop and choose a new lab namespace or inspect the object before any deliberate replacement. Never run these examples in a shared or production schema without adapting names and reviewing every destructive operation.

## Learning objectives

By the end, you should be able to:

- Distinguish user, table, named internal, and external stages, and know where `PUT`, `LIST`, `GET`, and `REMOVE` work.
- Create file formats for CSV, JSON, Parquet, Avro, and ORC.
- Load files using `COPY INTO <table>`, validate failures, inspect load history, and unload data using `COPY INTO <location>`.
- Configure cloud access through a storage integration and least-privilege IAM rather than embedding long-lived keys.
- Explain the 64-day load-metadata behavior and why file-level idempotency is not business-level deduplication.
- Use `ON_ERROR`, `VALIDATION_MODE`, `VALIDATE`, `FORCE`, `PURGE`, `MATCH_BY_COLUMN_NAME`, `INFER_SCHEMA`, and schema evolution safely.
- Choose among batch `COPY`, file-based Snowpipe, Snowpipe Streaming, and external tables.
- Monitor ingestion, recover from bad files, and make cost/latency trade-offs using measurements rather than assumptions.

## Prerequisites

You should understand databases, schemas, tables, SQL `SELECT`/`WHERE`, basic cloud object storage, roles and grants, Snowflake stages and warehouses at a high level, and micro-partitions. Review Topics 01–03 first if these are unfamiliar.

---

# 1. The ingestion mental model

A stage is a **location reference**, not the target table. A file format describes how to parse bytes into records and values. `COPY INTO <table>` reads staged files and loads rows into an existing target table. Snowpipe automates file loading; it does not remove the need to design schemas, access controls, error handling, or deduplication.

## 1.1 File-to-table lifecycle

```text
Producer / export job
        |
        v
CSV / JSON / Parquet / Avro / ORC files
        |
        v
Stage location (@~ / @%table / @named_stage / cloud object storage)
        |
        +---- file format + path/pattern + access permissions
        |
        v
COPY INTO <table>  OR  Snowpipe pipe (contains a COPY statement)
        |
        +---- parse / map / optional supported transformation
        +---- file load metadata and error reporting
        |
        v
Native Snowflake table -> query / transform / downstream pipeline
```

**Why it matters:** most production ingestion failures occur at boundaries: wrong prefix, inaccessible object, mismatched file format, schema drift, malformed rows, duplicate business events, or an unmonitored backlog. Validate each boundary independently.

## 1.2 Batch, event-driven, and row streaming are different patterns

```text
BATCH COPY
Files land in storage -> scheduled/orchestrated COPY -> table
              (minutes/hours cadence; you control when COPY runs)

SNOWPIPE AUTO-INGEST
Files land in cloud storage -> cloud event notification -> queue/integration
       -> Snowpipe serverless file loading -> table
              (continuous; latency is not guaranteed)

SNOWPIPE STREAMING
Application / Kafka connector -> Snowpipe Streaming client/connector
       -> streaming ingest endpoint and channels -> table
              (rows/events, without first creating a batch of staged files)
```

| Pattern | Input unit | Trigger / execution | Best fit | Main trade-off |
|---|---|---|---|---|
| Scheduled `COPY INTO` | Files | Scheduler or orchestrator runs SQL | Periodic bulk loads, controlled backfills | Data waits for the next run; warehouse/compute and orchestration must be managed |
| Snowpipe auto-ingest | Files | Cloud event notifications identify new objects | Continuous file drops with modest operational overhead | Per-file/event overhead; serverless ingestion charge; cloud notification setup; no strict latency guarantee |
| Snowpipe REST API | Files | Application submits file paths to a pipe | Programmatic file ingestion where event auto-ingest is unsuitable | Caller must handle authentication, retries, and file notifications |
| Snowpipe Streaming | Rows/events | SDK or supported connector sends records | Low-latency event ingestion without file staging | Different client/offset/error model; requires stream-aware operations and checkpointing |
| External table | Files remain in object storage | Queries scan registered external data | Exploration, infrequent access, or avoiding a copy into native storage | Queries can be slower; metadata refresh and source-file governance matter |

Do not choose by product name alone. State the latency objective, volume, file count, retry model, schema evolution plan, and acceptable cost first.

---

# 2. Beginner — stages and file formats

## 2.1 Stage types

A stage identifies where Snowflake should find or place files. Internal stages store files in Snowflake-managed staging storage; external stages point to object storage such as S3, Google Cloud Storage, or Azure storage.

| Stage type | Reference | Typical use | Notes |
|---|---|---|---|
| User stage | `@~` | Personal scratch upload/download | Exists for each user; useful for interactive work, not ideal as a shared production contract |
| Table stage | `@%MY_TABLE` | Files associated with a specific table | Exists with the table; useful for quick loading, but tied to the table object and its lifecycle |
| Named internal stage | `@DB.SCHEMA.MY_STAGE` | Shared internal landing area | Explicit permissions and reusable file format settings; files are stored in Snowflake-managed staging |
| Named external stage | `@DB.SCHEMA.S3_STAGE` | Files in S3/GCS/Azure | Uses a URL and typically a storage integration; object storage and its lifecycle remain external |

### `PUT`, `LIST`, `GET`, and `REMOVE`

- `PUT` uploads local files to an **internal** stage. It is a client-side staging command supported by Snowflake clients/connectors; it is not a way to upload local files directly to an external stage. Use the cloud provider's tools to upload to S3/GCS/Azure.
- `LIST @stage` lists staged files. Support and syntax depend on the stage and client context; `LIST` can be used with named external stages as well as internal stages.
- `GET` downloads files from an internal stage to a local client machine. It is not the general-purpose way to download from an external stage.
- `REMOVE @stage/path` removes staged files where supported and authorized. On external stages, removal deletes cloud objects and requires cloud delete permissions. Never use it as casual cleanup in a shared landing zone.

Example, using a local SnowSQL / compatible client context:

```sql
CREATE STAGE ingest_internal;

-- Run from a client that supports PUT and can access this local file.
PUT file:///absolute/path/orders.csv @ingest_internal AUTO_COMPRESS = TRUE;

LIST @ingest_internal;
-- After confirming the file is no longer needed (destructive):
-- REMOVE @ingest_internal/orders.csv.gz;
```

`PUT` paths must be accessible to the client executing the command. A web worksheet generally does not have access to a path on your laptop; use the supported UI upload flow or a client/connector for local files. Do not assume every command works in every interface.

## 2.2 File formats

A file format defines how the source bytes are interpreted. Create reusable named formats to keep loading behavior consistent and reviewable.

```sql
CREATE FILE FORMAT ingest_csv_ff
  TYPE = CSV
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  NULL_IF = ('', 'NULL', 'null')
  EMPTY_FIELD_AS_NULL = TRUE
  TRIM_SPACE = TRUE;

CREATE FILE FORMAT ingest_json_ff
  TYPE = JSON
  STRIP_OUTER_ARRAY = FALSE;

CREATE FILE FORMAT ingest_parquet_ff
  TYPE = PARQUET
  USE_LOGICAL_TYPE = TRUE;

CREATE FILE FORMAT ingest_avro_ff
  TYPE = AVRO;

CREATE FILE FORMAT ingest_orc_ff
  TYPE = ORC;
```

| Format | Typical structure | Key concerns |
|---|---|---|
| CSV | Delimited records and fields | Header rows, quoting, delimiters, embedded newlines, null tokens, encoding, column order and count |
| JSON | Semi-structured objects/arrays | One-record-per-line vs outer arrays, nested keys, type coercion, null/missing fields |
| Parquet | Columnar binary format with schema and row groups | Logical types, column-name mapping, schema compatibility, row-group/file sizing |
| Avro | Row-oriented binary format with schema | Schema compatibility and mapping to target columns |
| ORC | Columnar binary format with schema/stripes | Schema compatibility, logical types and column mapping |

Snowflake supports loading these formats, but a file format does not magically repair schema mismatches. Inspect representative files, test type conversions, and keep source schema versions visible.

## 2.3 Create a target table and load CSV

Assume a file `orders.csv` has header `ORDER_ID,ORDER_TS,AMOUNT` and data rows in that order.

```sql
CREATE TABLE orders_csv (
  order_id NUMBER,
  order_ts TIMESTAMP_NTZ,
  amount NUMBER(12,2)
);

-- Stage file first using PUT into @ingest_internal.
COPY INTO orders_csv
  FROM @ingest_internal
  FILE_FORMAT = (FORMAT_NAME = ingest_csv_ff)
  PATTERN = '.*orders[.]csv([.]gz)?'
  ON_ERROR = ABORT_STATEMENT;
```

**Important:** `SKIP_HEADER = 1` tells the parser to skip a header line for this CSV format. The example assumes the staged object is named `orders.csv` or auto-compressed as `orders.csv.gz`. `PATTERN` is a regular expression against staged file paths; make it as narrow as possible so unrelated files are not loaded.

## 2.4 Load JSON into a `VARIANT` column

For JSON where schema may evolve, a common landing design preserves each parsed JSON record in a `VARIANT` column before typed transformation.

```sql
CREATE TABLE raw_events (payload VARIANT);

COPY INTO raw_events
  FROM @ingest_internal/events/
  FILE_FORMAT = (FORMAT_NAME = ingest_json_ff)
  ON_ERROR = ABORT_STATEMENT;

SELECT
  payload:event_id::STRING AS event_id,
  payload:event_type::STRING AS event_type,
  TRY_TO_TIMESTAMP_NTZ(payload:event_ts::STRING) AS event_ts
FROM raw_events;
```

The path `@ingest_internal/events/` is an example prefix. The JSON file must be staged there. If the JSON structure contains an outer array, decide whether to set `STRIP_OUTER_ARRAY = TRUE` or preserve the array as a record; test with a small file first.

## 2.5 Load Parquet into typed columns

When file fields map to target columns by name, use `MATCH_BY_COLUMN_NAME` rather than relying on physical field order.

```sql
CREATE TABLE orders_parquet (
  order_id NUMBER,
  order_ts TIMESTAMP_NTZ,
  amount NUMBER(12,2)
);

COPY INTO orders_parquet
  FROM @ingest_internal/parquet/
  FILE_FORMAT = (FORMAT_NAME = ingest_parquet_ff)
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
  ON_ERROR = ABORT_STATEMENT;
```

The staged Parquet schema must be compatible with the destination. `MATCH_BY_COLUMN_NAME` supports matching names, not arbitrary transformations. It cannot be combined with a `SELECT` transformation in the same `COPY INTO` statement. Validate type conversions and nullability separately.

## 2.6 Validate before production loading

For a file that has not yet been loaded, use validation mode to ask Snowflake to parse and report errors without loading rows:

```sql
COPY INTO orders_csv
  FROM @ingest_internal
  FILE_FORMAT = (FORMAT_NAME = ingest_csv_ff)
  PATTERN = '.*orders[.]csv([.]gz)?'
  VALIDATION_MODE = RETURN_ERRORS;
```

Supported values include `RETURN_n_ROWS`, `RETURN_ERRORS`, and `RETURN_ALL_ERRORS`. Validation mode has limitations: it is not supported for a `COPY` that transforms data using a `SELECT`, and it is not supported for Iceberg tables. For errors from a completed earlier load, use the `VALIDATE` table function when supported by that load pattern.

```sql
-- After a failed or partially loaded standard COPY, use its query ID.
SELECT *
FROM TABLE(VALIDATE(orders_csv, JOB_ID => '<copy_query_id>'));
```

Replace `<copy_query_id>` with the actual query ID from query history. `VALIDATE` does not support transformed `COPY` loads. Do not confuse validation with business-quality checks: a syntactically valid row may still violate business rules.

---

# 3. Intermediate — secure cloud access and reliable bulk loading

## 3.1 Storage integrations: use IAM, not embedded keys

A storage integration is a Snowflake object that establishes a controlled trust relationship with a cloud identity. For S3, Snowflake exposes an IAM identity and external ID; an AWS administrator configures a role trust policy and grants that role only the required bucket/prefix permissions. Similar integration concepts apply to supported GCS and Azure configurations, but provider-specific setup differs.

**Security goals:**

1. Limit access to a dedicated bucket and prefix, not `*` unless there is a documented need.
2. Prefer a storage integration over embedding long-lived cloud access keys in stage definitions or scripts.
3. Separate read-only ingestion access from write/delete permissions needed for unloading or purge.
4. Restrict Snowflake roles: only the roles that need to create/use stages, file formats, pipes, and target tables should receive those privileges.
5. Rotate and review cloud IAM policies, monitor object access, and avoid sensitive information in object names or comments.

### S3 setup pattern (requires cloud administrator work)

The following is a template; placeholders must be replaced with real values. This SQL does **not** create the AWS role or its policies for you.

```sql
-- Usually requires ACCOUNTADMIN or a role with CREATE INTEGRATION.
CREATE STORAGE INTEGRATION s3_ingest_int
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::<aws_account_id>:role/<snowflake_ingest_role>'
  STORAGE_ALLOWED_LOCATIONS = ('s3://<bucket>/<approved-prefix>/');

DESC INTEGRATION s3_ingest_int;
-- Use STORAGE_AWS_IAM_USER_ARN and STORAGE_AWS_EXTERNAL_ID from the result
-- to configure the AWS role trust relationship as directed by Snowflake docs.

CREATE STAGE s3_orders_stage
  URL = 's3://<bucket>/<approved-prefix>/'
  STORAGE_INTEGRATION = s3_ingest_int
  FILE_FORMAT = (FORMAT_NAME = ingest_csv_ff);
```

Typical requirements include `CREATE INTEGRATION` (or an administrator role) to create the integration, `CREATE STAGE` on the target schema and `USAGE` on the integration to create a stage, plus `USAGE` on the stage and required database/schema/table privileges to load. Cloud-side IAM permissions must also allow the required object operations. For an S3 read-only load, permissions typically include listing the bucket and reading objects; unloading or deleting/purging requires additional write/delete permissions. Confirm exact permissions for the chosen provider and operations.

Test the configuration with the provider-specific Snowflake validation procedure/function documented for that integration, then run `LIST @s3_orders_stage` and a small `COPY` before production.

## 3.2 Load-history metadata and the 64-day concept

Snowflake records file-level load metadata so that a normal `COPY INTO <table>` can skip files that have already been loaded and have not changed. The roadmap calls out **64 days** because the load metadata and the staged file's `LAST_MODIFIED` timestamp interact with that retention window.

Do **not** interpret this as “Snowflake guarantees duplicate prevention forever.” When the staged file's last-modified timestamp is older than 64 days and the relevant load-history evidence is also older than 64 days, Snowflake may no longer be able to definitively determine whether that file was loaded. To avoid accidental reloading, normal `COPY` behavior skips the file in this ambiguous situation; design explicit recovery procedures for old files.

### File-level idempotency is not business-level deduplication

- **File-level load metadata:** protects against repeatedly loading the same unchanged staged file into the same target through normal `COPY` behavior while metadata is available.
- **Business-level deduplication:** protects against the same business event arriving in a different file, under a different filename, or through another ingestion path. This requires a stable business key, event ID, source sequence, or deterministic merge strategy.

For reliable pipelines, retain immutable source files with manifests/checksums and load timestamps; capture source file name and row identifiers where useful; and apply business deduplication in a staging/curated layer. Never use `FORCE = TRUE` as a generic retry setting.

## 3.3 `FORCE`, `ON_ERROR`, and `PURGE`

```sql
-- Default behavior: abort if a load error is encountered.
COPY INTO orders_csv
  FROM @s3_orders_stage
  FILE_FORMAT = (FORMAT_NAME = ingest_csv_ff)
  ON_ERROR = ABORT_STATEMENT;

-- Continue through row errors; inspect error counts and validate afterward.
COPY INTO orders_csv
  FROM @s3_orders_stage
  FILE_FORMAT = (FORMAT_NAME = ingest_csv_ff)
  ON_ERROR = CONTINUE;

-- Only when intentionally reloading already-loaded files after review:
-- COPY INTO orders_csv FROM @s3_orders_stage
--   FILE_FORMAT = (FORMAT_NAME = ingest_csv_ff)
--   FORCE = TRUE;

-- Destructive: removes successfully loaded source files from the stage.
-- COPY INTO orders_csv FROM @s3_orders_stage
--   FILE_FORMAT = (FORMAT_NAME = ingest_csv_ff)
--   PURGE = TRUE;
```

| Option | Behavior | Appropriate use | Risk / operational note |
|---|---|---|---|
| `ON_ERROR = ABORT_STATEMENT` | Stops the statement on an error (default behavior) | Strict ingestion contracts | One malformed row/file can block the batch; investigate and reprocess after correction |
| `ON_ERROR = CONTINUE` | Loads what it can and records row/file errors | Quarantine workflows where partial acceptance is allowed | A file may be partially loaded; do not blindly rerun the whole file or assume atomicity |
| `ON_ERROR = SKIP_FILE` | Skips a file that encounters errors | File-level rejection is acceptable | Valid rows in a bad file are not loaded; keep the file and route it to remediation |
| `VALIDATION_MODE` | Tests parsing without loading | Preflight checks | Has restrictions, including transformed `COPY` statements and Iceberg tables |
| `FORCE = TRUE` | Reloads files regardless of prior load status | Controlled replay into a deliberately reset or isolated target | Can duplicate rows; file history is not a business-key guarantee |
| `PURGE = TRUE` | Deletes successfully loaded files from the stage | Only where post-load deletion is explicitly required | Destructive; requires delete permissions and may violate retention/replay/audit requirements |

Other `ON_ERROR` variants such as `SKIP_FILE_n` and `SKIP_FILE_X%` can be useful but should be chosen only after reviewing the current command reference and the intended acceptance policy. Some load configurations and transformations have special error-handling limitations. Do not assume a single option behaves identically for every file format or target type.

**Recommended production pattern:** immutable landing prefix → validate/parse → `COPY` into a raw/staging table → record file-level status and errors → apply business checks and deduplication → promote accepted rows → retain or archive source files according to a documented retention policy.

## 3.4 Load transformations and semi-structured data

`COPY INTO <table>` can use a supported `SELECT` transformation over staged file columns, for example to select fields, cast values, or attach file metadata. The syntax uses staged file column references such as `$1`, `$2`, and `METADATA$FILENAME` where supported.

```sql
CREATE TABLE orders_landing (
  order_id NUMBER,
  amount NUMBER(12,2),
  source_file STRING
);

COPY INTO orders_landing (order_id, amount, source_file)
FROM (
  SELECT
    TRY_TO_NUMBER($1),
    TRY_TO_DECIMAL($2, 12, 2),
    METADATA$FILENAME
  FROM @ingest_internal/transformed/
)
FILE_FORMAT = (FORMAT_NAME = ingest_csv_ff)
ON_ERROR = ABORT_STATEMENT;
```

This is an illustrative CSV transform and assumes that the staged file has the expected field positions and that the header handling in the named file format matches the file. `TRY_` casts can convert invalid values to `NULL` instead of throwing; that may be useful for landing but must be paired with a reject-quality check so bad data is not silently accepted.

**Important incompatibility:** do not combine `MATCH_BY_COLUMN_NAME` with a `SELECT` transformation in the same `COPY INTO` statement. Use one method or the other. Also, `VALIDATION_MODE` and `VALIDATE` have limitations for transformed loads. Test the exact load shape against the current Snowflake SQL reference.

## 3.5 `MATCH_BY_COLUMN_NAME`

For supported structured and semi-structured file formats, `MATCH_BY_COLUMN_NAME = CASE_SENSITIVE | CASE_INSENSITIVE | NONE` maps source fields to target columns by name. This is useful when field order changes or producers add optional fields, but it does not make incompatible types compatible automatically.

```sql
COPY INTO orders_parquet
  FROM @s3_orders_stage/parquet/
  FILE_FORMAT = (TYPE = PARQUET USE_LOGICAL_TYPE = TRUE)
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
  ON_ERROR = ABORT_STATEMENT;
```

Use explicit target schemas and schema contracts for important pipelines. A permissive mapping setting can hide unexpected upstream changes if nobody monitors newly populated or missing columns.

## 3.6 `INFER_SCHEMA` and schema evolution

`INFER_SCHEMA` inspects supported staged files (CSV, JSON, Parquet, Avro, ORC) and returns column definitions. It is useful for initial discovery and scaffolding, not as a substitute for a reviewed data contract.

```sql
-- Example for Parquet; assumes @s3_orders_stage/parquet/ exists and the
-- named file format is appropriate for those files.
SELECT *
FROM TABLE(
  INFER_SCHEMA(
    LOCATION => '@s3_orders_stage/parquet/',
    FILE_FORMAT => 'INGEST_PARQUET_FF'
  )
);
```

A common way to create a table from inferred definitions is `CREATE TABLE ... USING TEMPLATE (...)`. This example intentionally fails if `INFERRED_ORDERS` already exists; review inferred names, types, nullability, and case before using it in a production deployment. Do not change it to `CREATE OR REPLACE` unless replacing the existing table is explicitly intended and its data/dependencies are protected.

```sql
CREATE TABLE inferred_orders
USING TEMPLATE (
  SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
  FROM TABLE(
    INFER_SCHEMA(
      LOCATION => '@s3_orders_stage/parquet/',
      FILE_FORMAT => 'INGEST_PARQUET_FF'
    )
  )
);
```

For large inferred schemas, selecting only required columns from `INFER_SCHEMA` may be safer than aggregating every output field into one object; Snowflake documents size limitations for large `ARRAY_AGG(OBJECT_CONSTRUCT(*))` results.

### Automatic schema evolution

```sql
ALTER TABLE orders_parquet SET ENABLE_SCHEMA_EVOLUTION = TRUE;
```

Schema evolution is not automatic for every load by default. Common prerequisites include:

- `ENABLE_SCHEMA_EVOLUTION = TRUE` on the target table.
- `COPY INTO <table>` or Snowpipe file loading with `MATCH_BY_COLUMN_NAME`.
- The loading role has `EVOLVE SCHEMA` or `OWNERSHIP` on the table.
- For CSV evolution using `MATCH_BY_COLUMN_NAME` and `PARSE_HEADER`, `ERROR_ON_COLUMN_COUNT_MISMATCH` must be `FALSE`.

Supported formats include Avro, Parquet, CSV, JSON, and ORC. The feature can add columns and drop `NOT NULL` constraints from columns absent in new files; it is not a general-purpose schema migration engine. The documented default limit is 100 added columns per load operation unless Snowflake Support approves a higher limit. Establish alerts and review changes so an upstream typo does not become a permanent new column.

## 3.7 Python connector: bulk loading versus row-by-row inserts

For bulk ingestion, prefer files plus `COPY INTO` or `write_pandas` over issuing one `INSERT` per row. `write_pandas` serializes a pandas DataFrame to Parquet, uploads files to a temporary stage, then uses `COPY INTO` to load them.

```python
import os
import snowflake.connector
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas

# Configure credentials through environment variables or a supported
# secret/workload identity mechanism; do not hard-code secrets in source.
conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],  # use a stronger supported auth method in production
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    database=os.environ["SNOWFLAKE_DATABASE"],
    schema=os.environ["SNOWFLAKE_SCHEMA"],
    role=os.environ.get("SNOWFLAKE_ROLE"),
)

try:
    df = pd.DataFrame({
        "ORDER_ID": [101, 102],
        "AMOUNT": [19.95, 42.00],
    })
    success, nchunks, nrows, output = write_pandas(
        conn,
        df,
        table_name="ORDERS_PANDAS",
        auto_create_table=False,
        overwrite=False,
        quote_identifiers=False,
    )
    if not success or nrows != len(df):
        raise RuntimeError(f"Bulk load did not meet expectations: {output}")
finally:
    conn.close()
```

Create `ORDERS_PANDAS` with compatible columns before running this example. `quote_identifiers=False` is suitable only when you intentionally use ordinary unquoted identifiers; quoted/mixed-case identifiers need different handling. Production authentication should use a supported key-pair, OAuth, workload identity, or secret-management pattern appropriate to the environment. Install compatible Snowflake Connector, pandas, and PyArrow dependencies as required by the connector version.

| Method | Best fit | Trade-off |
|---|---|---|
| Individual `INSERT` statements | Tiny transactional changes, small reference updates | High per-statement overhead for bulk data; poor fit for millions of rows |
| Connector `executemany` | Batching many parameterized rows when row semantics are required | Still not the preferred default for large file-oriented analytics loads; test batch size and transaction behavior |
| `PUT` + `COPY INTO` | General file-based bulk ingestion | Requires file lifecycle, stage access, format and load-history management |
| `write_pandas` | DataFrame already exists in Python | Convenient bulk path; creates staged Parquet and invokes copy loading; not a streaming ingestion interface |

---

# 4. Advanced — Snowpipe, Snowpipe Streaming, and file sizing

## 4.1 Snowpipe architecture

Snowpipe is continuous **file-based** loading. A pipe contains a `COPY INTO` statement. In auto-ingest mode, a cloud storage notification reports new file paths; Snowpipe reads the files from the stage and loads them using Snowflake-managed serverless compute.

```text
S3 / GCS / Azure object created
          |
          v
Cloud notification service / queue
          |
          v
Snowflake notification integration + PIPE
          |
          v
Snowpipe serverless file ingestion (COPY logic)
          |
          v
Target table + load history
```

A notification contains object/event information, not the file's data. Snowpipe then accesses the file through the stage's configured permissions. In auto-ingest mode, a newly created pipe processes new arrivals after notification setup; it does not automatically backfill all older files. Load historical or missed files using the documented backfill procedure or a controlled `COPY` process.

Example pipe (the stage, target table, and cloud notification setup must already be configured). The required pipe parameter depends on the cloud provider; these are **alternative templates**, not one statement to combine:

```sql
-- AWS S3 when using an SNS topic:
CREATE PIPE orders_pipe
  AUTO_INGEST = TRUE
  AWS_SNS_TOPIC = 'arn:aws:sns:<region>:<account-id>:<topic-name>'
  AS
  COPY INTO orders_csv
    FROM @s3_orders_stage/orders/
    FILE_FORMAT = (FORMAT_NAME = ingest_csv_ff);

SHOW PIPES LIKE 'ORDERS_PIPE';
SELECT SYSTEM$PIPE_STATUS('MYDB.MYSCHEMA.ORDERS_PIPE');
```

For Google Cloud Storage and Azure, use the provider-specific notification integration and `INTEGRATION = '<notification_integration_name>'`; for S3 multi-queue notification integrations, follow the current Snowflake syntax rather than using `AWS_SNS_TOPIC`. The exact notification integration and cloud configuration differ by provider. `AUTO_INGEST = TRUE` alone is not sufficient: the cloud event notification must be configured to deliver events to the notification channel expected by Snowflake. Validate the actual pipe status and load history after dropping a test file. Snowpipe does not support every `COPY INTO <table>` option; in particular, do not put `ON_ERROR = ABORT_STATEMENT`, `FORCE`, `PURGE`, `FILES`, or `SIZE_LIMIT` into the pipe's copy statement. Review the current `CREATE PIPE` reference before moving a bulk `COPY` statement into a pipe.

## 4.2 Latency and billing

Snowpipe runs on serverless compute and is currently billed using a fixed credit amount per GB loaded (with text-file billed size based on uncompressed bytes and binary-file billed size based on observed size). There is no standalone per-file charge under the current model, although file count and staging frequency still affect latency, throughput, and queue-management efficiency. Cloud notification services may also have charges. Review the current Snowflake service-consumption table and your cloud provider's pricing before estimating costs. Do not assume the same cost model as a user-managed warehouse running scheduled `COPY`.

Snowpipe can make new data queryable quickly, often within minutes and sometimes around a minute for typical workloads, but **latency is not guaranteed**. Queue depth, event delivery, file sizes, file counts, schema parsing, and service conditions all matter. Monitor actual end-to-end latency against an SLO.

## 4.3 Snowpipe Streaming and Kafka connector

Snowpipe Streaming is a separate ingestion path for applications that send rows/events through supported client APIs rather than landing each event as a file first. It can reduce latency for event-oriented sources, but requires an application or connector to manage ordering, channel/offset progress, retries, and source checkpoints correctly.

The Snowflake Connector for Kafka v4 uses Snowpipe Streaming's high-performance architecture. Do not assume older v3 connector behavior, configuration, or operational guidance applies unchanged; review the current migration and compatibility documentation when upgrading. The high-performance architecture has specific SDK, channel, pipe, networking, and table constraints.

| Need | Choose | Do not choose it when… |
|---|---|---|
| Load a large batch once or on a schedule | `COPY INTO` | Data must appear continuously between scheduled runs |
| Automatically ingest files arriving in cloud storage | Snowpipe auto-ingest | Source sends individual events and file creation is not a natural boundary |
| Low-latency row/event ingestion | Snowpipe Streaming or an appropriate supported connector | You only need periodic bulk loads and do not need streaming semantics |
| Query data in place without copying it into a native table | External table | Frequent, latency-sensitive queries require the performance and management model of native storage |

## 4.4 File sizing: 100–250 MB compressed is a starting heuristic

The roadmap uses approximately **100–250 MB compressed** as practical guidance for staged-file ingestion. Treat this as a starting point, not a strict Snowflake limit or a universal optimum. The right size depends on format, compression ratio, record size, available parallelism, ingestion mode, and how quickly the producer can close files.

- **Too many tiny files:** more listing, event, queue, scheduling, and per-file processing work, which can hurt latency and throughput. Under Snowpipe's current credit-per-GB billing model there is no standalone per-file fee, but file count can still affect operational efficiency and the relationship between billed bytes and useful work.
- **Too few very large files:** fewer independent units of work, less parallelism, slower retry granularity, and longer waits if a file is only finalized after a large accumulation window.
- **Columnar files such as Parquet:** row groups and format characteristics affect scan parallelism; tune with representative data rather than copying a CSV rule blindly.
- **Snowpipe:** file arrivals are the trigger, so extremely small files can create disproportionate event/processing overhead. Consider batching upstream if the latency objective permits.

The roadmap's exercise compares 10,000 tiny files with 100 larger files. This is a measurement exercise, not a claim that the second design always wins by a fixed percentage.

---

# 5. Unloading: `COPY INTO <location>`

`COPY INTO <location>` exports rows from a table or query to one or more files in an internal or external stage/location. It is the inverse direction of `COPY INTO <table>` but has different options and failure modes.

```sql
-- Unload to an external stage as Parquet files.
COPY INTO @s3_orders_stage/exports/orders_
  FROM (SELECT order_id, order_ts, amount FROM orders_csv)
  FILE_FORMAT = (TYPE = PARQUET COMPRESSION = SNAPPY)
  INCLUDE_QUERY_ID = TRUE;

-- For an internal stage, use GET from a compatible client to download.
-- For an external stage, use the cloud provider's tools to retrieve objects.
```

`INCLUDE_QUERY_ID = TRUE` helps make output filenames unique and protects against duplicate output from internal retries in supported patterns. `OVERWRITE = TRUE` is not a universal deduplication strategy: parallel unloads can generate different filenames, and stale files not matching the new output names remain. Use a unique output prefix per run, a controlled cleanup policy, and manifests for downstream consumers.

---

# 6. Monitoring, history, and recovery

## 6.1 `COPY_HISTORY`

The Information Schema table function returns recent load activity for bulk `COPY` and Snowpipe. The table function's documented window is the last 14 days; use the Account Usage `COPY_HISTORY` view for longer-term operational reporting, respecting its documented latency and retention behavior.

```sql
SELECT
  FILE_NAME,
  LAST_LOAD_TIME,
  ROW_COUNT,
  ROW_PARSED,
  ERROR_COUNT,
  STATUS,
  FIRST_ERROR_MESSAGE,
  PIPE_NAME
FROM TABLE(
  MYDB.INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'ORDERS_CSV',
    START_TIME => DATEADD('hour', -24, CURRENT_TIMESTAMP())
  )
)
ORDER BY LAST_LOAD_TIME DESC;
```

Use the database's `INFORMATION_SCHEMA` for the target table's database; fully qualify it as appropriate. The `COPY_HISTORY` function has privilege requirements: for bulk loads, roles need the documented monitoring or database/schema/table visibility; Snowpipe results may require visibility on the pipe as well. Confirm the current reference for your role design.

## 6.2 Pipe status

```sql
SELECT SYSTEM$PIPE_STATUS('MYDB.MYSCHEMA.ORDERS_PIPE');
```

The result is JSON with state and queue/error fields where applicable. Typical checks include `executionState`, `pendingFileCount`, oldest pending file time, most recent error/fault, and last ingested file/time. Access is restricted to the pipe owner or a role with the relevant monitoring privilege. A status of `RUNNING` does not prove that the expected file arrived or loaded; correlate status with source object inventory and `COPY_HISTORY`.

## 6.3 Dead-letter and reprocessing pattern

```text
Source landing prefix (immutable)
          |
          v
Validation / COPY
   | success                | row/file errors
   v                        v
Raw landing table       Reject manifest + original file
   |                        |
   v                        v
Business validation     Investigate / repair / approve replay
   |                        |
   v                        v
Curated table <------ controlled reprocess to isolated target/prefix
```

A reject record should capture at least source object path, load/query ID, timestamp, error message, schema/version, and remediation status. Retain the original bytes until the replay has been verified. When reprocessing, decide explicitly whether to reload into a clean isolated table, truncate/replace a partition, or merge by business key. `FORCE = TRUE` merely changes file-load suppression; it does not make replay safe.

### Useful recovery checks

1. Does the object exist at the exact stage prefix? `LIST @stage/path` or the cloud provider's object listing.
2. Can the Snowflake role access the stage? Check `USAGE` grants, storage integration configuration, allowed locations, cloud IAM, and network/private-connectivity settings.
3. Does the file match the `PATTERN`? Test the regex against the full staged path.
4. Does the parser agree with the file? Check headers, delimiters, quotes, compression, JSON record boundaries, encoding, Parquet logical types, and column names.
5. Did the file already load? Inspect `COPY_HISTORY`, query history, and load metadata before retrying.
6. Was it partially loaded under `ON_ERROR = CONTINUE`? Run `VALIDATE` where supported, review error counts, and design the retry to avoid duplicate accepted rows.
7. Is Snowpipe waiting on notifications? Check cloud notification wiring, pipe status, queue/backlog, event prefixes, and whether the object arrived after pipe setup.
8. Has the pipe been paused or stale for too long? Review notification retention and Snowflake's documented recovery/backfill process.

---

# 7. External tables versus loading into native tables

An external table lets Snowflake query data that remains in cloud object storage. It is read-only and stores file-level metadata; it does not copy the data into native Snowflake table storage. External table queries may be slower than queries over native tables, and results can be stale if metadata refresh is misconfigured. Querying Parquet files may be a good use case for an external table or Iceberg design, depending on the data architecture and query requirements.

| Decision factor | External table | Load into native Snowflake table |
|---|---|---|
| Data duplication | Avoids a native copy of the source data | Stores a native copy; storage and ingestion costs apply |
| Freshness | Depends on file arrival and metadata refresh/registration | Depends on `COPY`, Snowpipe, or streaming ingestion completion |
| Query performance | Can be slower; source-file format/layout and metadata pruning matter | Usually a better fit for frequent analytics and Snowflake-managed storage optimization |
| DML / transformations | External table is read-only; use downstream tables/views for transformation | Supports normal table DML and richer downstream processing |
| Governance | Cloud object permissions and Snowflake external-table privileges both matter | Snowflake table access controls govern the native copy, while source files still need their own retention/security policy |
| Operational burden | Manage external files, refresh, schemas, and file layout | Manage loading, deduplication, retention, storage, and load failures |
| Best fit | Infrequent reads, exploration, shared data lake, or avoiding copies | Frequently queried, production analytics data with predictable performance needs |

External tables can use partitioning and metadata to prune some files/regions, but they do not behave identically to native tables. Plan file paths and partition metadata deliberately, and monitor refresh history. A materialized view over an external table can improve repeated query performance but adds maintenance/storage cost and edition prerequisites; evaluate current product documentation before choosing it.

---

# 8. Hands-on lab — `experiments/04_loading/`

## 8.1 Lab goals

By the end, you will have tested CSV, JSON, and Parquet loads; observed error handling; inspected load history; assessed a safe rerun; and made a reasoned decision between scheduled `COPY`, Snowpipe, and external tables.

### Prerequisites and safety

- A non-production Snowflake database/schema and a warehouse with permission to run the lab.
- Privileges to create tables, file formats, and stages in the lab schema; `USAGE` on the warehouse; and `USAGE`/write permissions appropriate to the chosen stage.
- For an external S3 stage: an AWS bucket/prefix, an administrator who can configure IAM role trust/policy and cloud notifications, and a Snowflake role allowed to create/use a storage integration and stage. GCS/Azure use different provider-specific setup.
- A supported client or Snowflake UI workflow for local file staging. `PUT` requires a local file accessible to the client and an internal stage.
- Budget approval for warehouse compute, storage, event notifications, and Snowpipe ingestion. **Do not begin with 10,000 files or large volumes in production.**

Keep secrets out of SQL files, notebooks, logs, and Git. Use a dedicated lab prefix such as `s3://<bucket>/snowflake-lab/04-loading/` and restrict the integration's allowed locations to that prefix. Before running the setup, confirm that `INGEST_LAB` and `LOADING` do not already exist; otherwise choose a new database/schema name and update every later reference consistently. The setup intentionally fails if the database or schema already exists, rather than reusing unknown objects.

## 8.2 Lab directory layout

```text
experiments/04_loading/
├── README.md                    # setup, prerequisites, cleanup checklist
├── sample-data/
│   ├── orders.csv
│   ├── events.json
│   ├── orders.parquet           # generated locally with a compatible tool
│   └── orders_bad.csv           # intentionally malformed fixture
├── 01_objects_and_file_formats.sql
├── 02_load_and_validate.sql
├── 03_history_and_idempotency.sql
├── 04_snowpipe_auto_ingest.sql   # optional: requires cloud event setup
├── 05_file_count_comparison.md
└── results.csv                  # observed metrics, never prefilled with fabricated values
```

This is the requested lab structure to create in your repository; the lesson does not claim these files were generated or run.

## 8.3 Step 1 — Create lab objects

```sql
CREATE DATABASE INGEST_LAB;
CREATE SCHEMA INGEST_LAB.LOADING;
USE DATABASE INGEST_LAB;
USE SCHEMA LOADING;

CREATE FILE FORMAT LAB_CSV_FF
  TYPE = CSV SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  EMPTY_FIELD_AS_NULL = TRUE
  TRIM_SPACE = TRUE;

CREATE FILE FORMAT LAB_JSON_FF
  TYPE = JSON STRIP_OUTER_ARRAY = FALSE;

CREATE FILE FORMAT LAB_PARQUET_FF
  TYPE = PARQUET USE_LOGICAL_TYPE = TRUE;

CREATE TABLE ORDERS_CSV (
  ORDER_ID NUMBER,
  ORDER_TS TIMESTAMP_NTZ,
  AMOUNT NUMBER(12,2)
);

CREATE TABLE RAW_EVENTS (PAYLOAD VARIANT);

CREATE TABLE ORDERS_PARQUET (
  ORDER_ID NUMBER,
  ORDER_TS TIMESTAMP_NTZ,
  AMOUNT NUMBER(12,2)
);
```

Use a small internal stage for the no-cloud version:

```sql
CREATE STAGE LAB_INTERNAL;
LIST @LAB_INTERNAL;
```

Stage local files into `@LAB_INTERNAL` with a supported client. Alternatively, use the external stage configured through the storage-integration setup earlier.

## 8.4 Step 2 — Load three formats

For CSV:

```sql
COPY INTO ORDERS_CSV
  FROM @LAB_INTERNAL
  FILE_FORMAT = (FORMAT_NAME = LAB_CSV_FF)
  PATTERN = '.*orders[.]csv([.]gz)?'
  ON_ERROR = ABORT_STATEMENT;
```

For JSON:

```sql
COPY INTO RAW_EVENTS
  FROM @LAB_INTERNAL
  FILE_FORMAT = (FORMAT_NAME = LAB_JSON_FF)
  PATTERN = '.*events[.]json([.]gz)?'
  ON_ERROR = ABORT_STATEMENT;
```

For Parquet:

```sql
COPY INTO ORDERS_PARQUET
  FROM @LAB_INTERNAL
  FILE_FORMAT = (FORMAT_NAME = LAB_PARQUET_FF)
  PATTERN = '.*orders[.]parquet'
  MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
  ON_ERROR = ABORT_STATEMENT;
```

**Expected observation (not a benchmark claim):** successful loads report file and row counts; the JSON table contains a `VARIANT` payload per parsed record; Parquet mapping uses source column names. If no files match, check `LIST`, prefix, case, and `PATTERN` before changing the target schema.

## 8.5 Step 3 — Introduce malformed rows and compare `ON_ERROR`

Use `orders_bad.csv` with a valid header, a valid row, and a row with an invalid numeric/timestamp value. Validate first:

```sql
COPY INTO ORDERS_CSV
  FROM @LAB_INTERNAL
  FILE_FORMAT = (FORMAT_NAME = LAB_CSV_FF)
  PATTERN = '.*orders_bad[.]csv([.]gz)?'
  VALIDATION_MODE = RETURN_ERRORS;
```

Then test in a **separate empty table** for each behavior so previous rows do not contaminate the comparison:

```sql
CREATE TABLE ORDERS_ABORT LIKE ORDERS_CSV;
CREATE TABLE ORDERS_CONTINUE LIKE ORDERS_CSV;
CREATE TABLE ORDERS_SKIP_FILE LIKE ORDERS_CSV;

COPY INTO ORDERS_ABORT FROM @LAB_INTERNAL
  FILE_FORMAT = (FORMAT_NAME = LAB_CSV_FF)
  PATTERN = '.*orders_bad[.]csv([.]gz)?'
  ON_ERROR = ABORT_STATEMENT;

COPY INTO ORDERS_CONTINUE FROM @LAB_INTERNAL
  FILE_FORMAT = (FORMAT_NAME = LAB_CSV_FF)
  PATTERN = '.*orders_bad[.]csv([.]gz)?'
  ON_ERROR = CONTINUE;

COPY INTO ORDERS_SKIP_FILE FROM @LAB_INTERNAL
  FILE_FORMAT = (FORMAT_NAME = LAB_CSV_FF)
  PATTERN = '.*orders_bad[.]csv([.]gz)?'
  ON_ERROR = SKIP_FILE;
```

`ABORT_STATEMENT` is expected to fail the statement on a load error; `CONTINUE` can partially load valid rows and report errors; `SKIP_FILE` skips a file that encounters errors. Exact row/file outcomes depend on the malformed data and parser behavior. Capture actual query IDs and row/error counts. For transformed loads, validation support differs; this lab uses standard loads.

## 8.6 Step 4 — Inspect errors and history

```sql
SELECT *
FROM TABLE(INGEST_LAB.INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'ORDERS_CONTINUE',
  START_TIME => DATEADD('hour', -2, CURRENT_TIMESTAMP())
))
ORDER BY LAST_LOAD_TIME DESC;
```

Use the actual table and database names. For a failed/partial load, run `VALIDATE` using its query ID where supported:

```sql
SELECT *
FROM TABLE(VALIDATE(ORDERS_CONTINUE, JOB_ID => '<actual_copy_query_id>'));
```

Record `FILE_NAME`, `STATUS`, `ROW_COUNT`, `ROW_PARSED`, `ERROR_COUNT`, and the first error. The Information Schema function covers only the last 14 days. If it returns no rows, verify the target table name, time window, query completion, and privileges.

## 8.7 Step 5 — Test idempotency without duplicating the table

First run the same `COPY` a second time with default `FORCE = FALSE` and unchanged staged files. Compare output and `COPY_HISTORY` to the first run. Then test `FORCE = TRUE` only against an isolated disposable table.

```sql
-- Normal repeat: unchanged files already loaded should ordinarily be skipped
-- while load metadata can determine their status.
COPY INTO ORDERS_CSV
  FROM @LAB_INTERNAL
  FILE_FORMAT = (FORMAT_NAME = LAB_CSV_FF)
  PATTERN = '.*orders[.]csv([.]gz)?';

-- Demonstration only, isolated target: forced reload can duplicate rows.
CREATE TABLE ORDERS_FORCE_TEST LIKE ORDERS_CSV;
COPY INTO ORDERS_FORCE_TEST
  FROM @LAB_INTERNAL
  FILE_FORMAT = (FORMAT_NAME = LAB_CSV_FF)
  PATTERN = '.*orders[.]csv([.]gz)?';
COPY INTO ORDERS_FORCE_TEST
  FROM @LAB_INTERNAL
  FILE_FORMAT = (FORMAT_NAME = LAB_CSV_FF)
  PATTERN = '.*orders[.]csv([.]gz)?'
  FORCE = TRUE;

SELECT COUNT(*) FROM ORDERS_FORCE_TEST;
```

The second forced copy can reload file rows and therefore duplicate them. Record the actual counts. Then explain why two files containing the same `ORDER_ID` can both load even if each file has valid file-level load history. Add a business-key deduplication strategy in a separate transformation step; do not claim the load-history feature solves it.

## 8.8 Step 6 — Optional Snowpipe auto-ingest

Only do this step if you have cloud storage access, notification infrastructure, integration privileges, and an approved budget. Follow the current Snowflake provider-specific setup for S3/SQS, GCS/Pub/Sub, or Azure Event Grid/queue; do not copy a generic event policy across providers.

1. Create the storage integration and external stage restricted to the lab prefix.
2. Configure the cloud notification service and the Snowflake notification integration according to the current provider-specific guide.
3. Create the target table and pipe containing the intended `COPY` statement.
4. Configure cloud notifications for the exact prefix the stage/pipe watches.
5. Drop a uniquely named test file **after** notification setup is complete.
6. Poll `SYSTEM$PIPE_STATUS`, inspect `COPY_HISTORY`, and record object arrival time, first successful query visibility time, row count, and any errors.
7. Repeat with a small controlled number of files and compare latency/overhead. Do not assume latency is guaranteed or that historical files are automatically backfilled.

```sql
CREATE PIPE LAB_ORDERS_PIPE
  AUTO_INGEST = TRUE
  AWS_SNS_TOPIC = 'arn:aws:sns:<region>:<account-id>:<topic-name>'
  AS
  COPY INTO ORDERS_CSV
    FROM @S3_ORDERS_STAGE/orders/
    FILE_FORMAT = (FORMAT_NAME = LAB_CSV_FF);

SELECT SYSTEM$PIPE_STATUS('INGEST_LAB.LOADING.LAB_ORDERS_PIPE');
```

This lab SQL is the AWS S3 + SNS variant; replace the placeholder ARN and stage with your approved values. For GCS/Azure, replace `AWS_SNS_TOPIC` with `INTEGRATION = '<notification_integration_name>'` and follow that provider's setup guide. A pipe can be created without `AUTO_INGEST = TRUE` for the Snowpipe REST API pattern, but that is not the same as cloud-event auto-ingest.

### Lower-cost alternative if event infrastructure is unavailable

Skip cloud notifications and Snowpipe creation. Use the internal stage, load the same files through scheduled/manual `COPY`, and measure the effect of file count on elapsed time and warehouse usage. Write a design note specifying the additional event-infrastructure steps required for Snowpipe. This still teaches batch loading, idempotency, file sizing, and error handling without cloud event costs.

## 8.9 Step 7 — Compare many tiny files with fewer larger files

The roadmap proposes 10,000 tiny files versus 100 larger files. That is a potentially expensive test: each object can create listing, notification, scheduling, parsing, and history work. Current Snowpipe billing is credit-per-GB rather than a separate fee per file, but file count still affects operational efficiency. Do not begin at full scale. Start with a small representative comparison (for example, 20–100 files versus 1–5 files with similar total bytes), then scale only if budget and account limits permit.

Keep total uncompressed records/bytes as comparable as possible. Use separate target tables or clean targets, identical warehouse size for `COPY`, the same file format and data distribution, and no concurrent workload. For Snowpipe, use separate isolated prefixes/pipes or a carefully designed repeated trial; cloud notification charges and serverless ingestion charges may apply.

Record **observed** values:

| Trial | Files | Total compressed bytes | Rows | Elapsed seconds | Warehouse credits (COPY only) | Snowpipe bytes/credits where exposed | Error count |
|---|---:|---:|---:|---:|---:|---:|---:|
| A: many small | Fill from measurements | Fill | Fill | Fill | Fill | Fill | Fill |
| B: fewer larger | Fill from measurements | Fill | Fill | Fill | Fill | Fill | Fill |

**Measurement limitations:** caching, warehouse warm-up, network variability, file compression, and different parallelism can affect timing. Repeat trials and report ranges/medians rather than one lucky run. Do not compare Snowpipe credits directly with warehouse credits without checking current billing units and the cloud provider charges. A small lab result does not guarantee production behavior at 10,000 files.

## 8.10 Step 8 — Decide whether to use external tables

Use the same data files to sketch or create an external table only if your stage and privileges allow it. Compare:

- Time to query representative filters and aggregations.
- Metadata refresh behavior after adding a file.
- Operational steps needed to ensure fresh results.
- Cost and complexity of ingestion versus querying in place.

The correct conclusion may be different for occasional exploration and a heavily queried dashboard. Document the workload assumptions instead of declaring one option universally better.

## 8.11 Lab cleanup

After retaining your measurement notes, remove only resources you own and are authorized to delete. Run the cleanup block only after confirming that each listed object was successfully created by this lab run; if setup stopped on a name collision, do not run blanket cleanup against that name. For a Snowpipe test, pause/drop the pipe according to the approved cleanup plan before deleting notification resources. Delete test tables and file formats as appropriate. Do **not** delete source cloud objects or use `PURGE = TRUE` unless the files are disposable and retention requirements are satisfied.

```sql
-- Example cleanup for disposable lab objects only; adapt the object names.
DROP PIPE IF EXISTS LAB_ORDERS_PIPE;
DROP TABLE IF EXISTS ORDERS_ABORT;
DROP TABLE IF EXISTS ORDERS_CONTINUE;
DROP TABLE IF EXISTS ORDERS_SKIP_FILE;
DROP TABLE IF EXISTS ORDERS_FORCE_TEST;
DROP TABLE IF EXISTS ORDERS_CSV;
DROP TABLE IF EXISTS ORDERS_PARQUET;
DROP TABLE IF EXISTS RAW_EVENTS;
DROP STAGE IF EXISTS LAB_INTERNAL;
DROP FILE FORMAT IF EXISTS LAB_CSV_FF;
DROP FILE FORMAT IF EXISTS LAB_JSON_FF;
DROP FILE FORMAT IF EXISTS LAB_PARQUET_FF;
```

Do not drop a shared storage integration or bucket. Remove cloud IAM and notification resources only through the owning team's change process after verifying nothing else uses them.

---

# 9. Cost, security, and production design checklist

## 9.1 Cost controls

- Choose scheduled `COPY` for bulk loads when the latency objective allows batching.
- Avoid excessive tiny files; batch upstream when this does not violate freshness requirements.
- Monitor file bytes, number of files, row counts, error rates, elapsed time, warehouse credits for batch `COPY`, and Snowpipe billed bytes/credits where available.
- Estimate cloud event, storage, request, and egress charges in addition to Snowflake charges.
- Keep auto-suspend and warehouse sizing appropriate for scheduled `COPY` workloads; avoid leaving a warehouse running for a small periodic load.
- Use representative benchmarks, with equal data volume and repeatable conditions. Compare cost per successful row/GB and end-to-end latency, not elapsed time alone.
- Keep retention and replay requirements in the design before using `PURGE` or deleting external files.

## 9.2 Security checklist

- [ ] Storage integration allowed locations are narrowed to approved buckets/prefixes.
- [ ] Cloud role has only required list/read permissions for ingestion; write/delete is granted only when required.
- [ ] No long-lived access keys are embedded in SQL, source code, notebooks, or CI logs.
- [ ] Stage, pipe, database, schema, table, warehouse, and integration privileges follow least privilege.
- [ ] Data classification, encryption, private connectivity, audit logging, and retention are reviewed for the actual account/cloud setup.
- [ ] Error logs and dead-letter manifests do not expose sensitive payloads unnecessarily.
- [ ] `PURGE`, `REMOVE`, `FORCE`, `OVERWRITE`, and destructive DDL require explicit review.

## 9.3 Production readiness checklist

- [ ] File contract specifies encoding, compression, schema version, nulls, quoting, naming, and maximum expected size.
- [ ] File producer writes atomically or publishes a manifest only after a file is complete.
- [ ] Each file has a stable identity and the pipeline records path, size, modified time/checksum where available, arrival time, load/query ID, and status.
- [ ] Load history is monitored and retained long enough for incident investigation.
- [ ] Business deduplication uses stable business keys/event IDs, not only Snowflake file load history.
- [ ] Error policy is explicit: abort, continue, or reject files; partial loads have a documented replay path.
- [ ] Schema evolution is permission-controlled and monitored.
- [ ] Snowpipe notification health, pending files, last successful ingest, and latency are monitored where used.
- [ ] Reprocessing is tested on duplicate, malformed, delayed, and old files.
- [ ] Ownership, alert routing, retention, backfill, and cleanup responsibilities are assigned.

---

# 10. Common mistakes and troubleshooting

| Mistake / symptom | Why it happens | Corrective action |
|---|---|---|
| Long-lived cloud keys in stage SQL | Credential shortcut creates rotation and leakage risk | Use a storage integration and least-privilege cloud role; rotate/remove exposed credentials |
| `PUT` to an external stage | `PUT` uploads local files to internal stages | Upload with the cloud provider's tools, then use the external stage |
| `COPY` reports no files loaded | Wrong path/prefix, regex, file already loaded, or inaccessible object | `LIST` the exact prefix, check pattern, inspect load history and integration permissions |
| Header becomes a data row | CSV format does not skip/parse the header as intended | Configure `SKIP_HEADER` or header parsing appropriately and test the exact file |
| Many rows become NULL | `TRY_` conversions or source values don't match target types | Capture reject reasons, validate source types and business rules, avoid silent null conversion |
| Rerun duplicates rows | `FORCE = TRUE`, changed file name, expired/ambiguous load metadata, or duplicate business events | Inspect load history; use isolated replay and business-key deduplication |
| `VALIDATION_MODE` errors on transformed `COPY` | Validation mode does not support `SELECT` transformations in `COPY` | Validate the source with a supported standard `COPY` shape, then test transformations separately |
| `MATCH_BY_COLUMN_NAME` compilation error with transform | The two options cannot be combined | Use name mapping or a `SELECT` transform, then transform in a later step if both are needed |
| Snowpipe pipe is `RUNNING` but file is absent | File may be outside monitored prefix, notification misconfigured, or load failed | Check cloud events, stage prefix, pipe status JSON, `COPY_HISTORY`, and source object listing |
| Old staged file is skipped | Load metadata cannot definitively establish old file status | Follow documented older-file behavior; replay into an isolated target or use a controlled recovery plan |
| Tiny-file workload is unexpectedly expensive | Per-file overhead and event/processing overhead dominate | Batch files where latency permits; measure bytes and count together |
| `PURGE` removes data needed for replay | Source file deletion was treated as routine cleanup | Disable purge, restore from retained source if possible, and formalize archive/retention policies |
| External-table query is stale | Metadata refresh not configured or not completed | Check external-table refresh and event notifications; manually refresh if appropriate and authorized |

---

# 11. Practice questions with answers

### 1. What is the difference between a stage and a file format?

**Answer:** A stage identifies a file location and access method; a file format describes how to parse the files. They solve different problems and are often referenced together in `COPY INTO`.

### 2. Can `PUT` upload a local file to S3 through an external stage?

**Answer:** No. `PUT` uploads local files to an internal stage. Upload to external object storage using cloud tools, then reference it through the external stage.

### 3. Why prefer a storage integration over embedded cloud credentials?

**Answer:** It delegates authentication through a managed trust relationship, avoids distributing long-lived keys, and lets administrators constrain allowed locations and permissions.

### 4. Does the 64-day load-history behavior guarantee deduplication forever?

**Answer:** No. File load metadata has retention and old-file ambiguity behavior. Business-level deduplication needs stable business keys/event IDs and explicit transformation logic.

### 5. What is the difference between `ON_ERROR = CONTINUE` and `SKIP_FILE`?

**Answer:** `CONTINUE` may load valid rows from a file while recording bad rows; `SKIP_FILE` rejects a file that encounters errors. Exact outcomes should be verified with the actual file and format.

### 6. Why can `FORCE = TRUE` be dangerous?

**Answer:** It reloads files that normal load-history checks would skip, potentially duplicating rows. Use only in a controlled replay plan.

### 7. Can `MATCH_BY_COLUMN_NAME` be combined with a `SELECT` transformation in `COPY`?

**Answer:** No. Choose column-name mapping or a transformation in that `COPY`; if needed, transform in a later SQL step.

### 8. What does `INFER_SCHEMA` do, and what does it not do?

**Answer:** It derives candidate column definitions from supported staged files. It does not replace schema review, business validation, or a controlled schema migration process.

### 9. How is Snowpipe different from Snowpipe Streaming?

**Answer:** Snowpipe loads files based on event notifications or submitted file paths using a pipe with `COPY` logic. Snowpipe Streaming sends row/event data through streaming APIs/connectors without the same staged-file workflow.

### 10. Why are 10,000 tiny files not automatically better than 100 larger files?

**Answer:** Tiny files can create disproportionate listing, notification, scheduling, parsing, and per-file overhead. Larger files reduce file count but may affect latency and parallelism; measure both under representative conditions.

### 11. What is `COPY_HISTORY` useful for?

**Answer:** It exposes file-level load activity, status, row counts, error information, and pipe details where visible. The Information Schema function has a 14-day window; use Account Usage for longer-term analysis.

### 12. When might an external table be preferable to native ingestion?

**Answer:** When data is queried infrequently, must remain in the data lake, or avoiding a native copy is valuable. For frequent performance-sensitive analytics, native tables are often a better fit, but workload and cost must decide.

---

# 12. Roadmap checkpoint

Use this checklist to decide whether you have mastered Topic 04.

- [ ] Create and distinguish user, table, named internal, and external stages.
- [ ] Explain where `PUT`, `LIST`, `GET`, and `REMOVE` are supported and their destructive/access implications.
- [ ] Create file formats for CSV, JSON, Parquet, Avro, and ORC.
- [ ] Load data with `COPY INTO <table>` and unload with `COPY INTO <location>`.
- [ ] Configure a storage integration with least-privilege cloud IAM and no embedded long-lived keys.
- [ ] Explain the 64-day load-metadata behavior and distinguish file-level idempotency from business deduplication.
- [ ] Use and explain `FORCE`, `ON_ERROR`, `VALIDATION_MODE`, `VALIDATE`, and `PURGE` safely.
- [ ] Explain semi-structured loading, supported `COPY` transformations, and `MATCH_BY_COLUMN_NAME` incompatibility with transformation queries.
- [ ] Use `INFER_SCHEMA` for discovery and explain schema-evolution prerequisites and limitations.
- [ ] Explain how `write_pandas` uses Parquet staging and `COPY` compared with row-by-row inserts.
- [ ] Distinguish scheduled `COPY`, Snowpipe file auto-ingest, Snowpipe REST API, and Snowpipe Streaming.
- [ ] Explain why file size and count affect throughput, latency, and cost; support recommendations with observations.
- [ ] Inspect `COPY_HISTORY` and `SYSTEM$PIPE_STATUS`, investigate errors, and describe a dead-letter/reprocessing workflow.
- [ ] Decide when an external table is preferable to loading data into a native table.

**Roadmap exercise to submit:** plan one S3 prefix with a storage integration, file format, target schema, error policy, file-level idempotency strategy, business deduplication strategy, monitoring queries, retention policy, and a decision between scheduled `COPY` and Snowpipe. Include a brief cost/latency comparison based on stated assumptions.

---

# 13. Official documentation references

Use the current documentation for syntax, provider-specific prerequisites, limits, and pricing; cloud integrations and streaming architecture evolve over time.

1. [Stages overview and data loading](https://docs.snowflake.com/en/user-guide/data-load-overview)
2. [`CREATE STAGE`](https://docs.snowflake.com/en/sql-reference/sql/create-stage)
3. [`PUT`](https://docs.snowflake.com/en/sql-reference/sql/put)
4. [`CREATE FILE FORMAT`](https://docs.snowflake.com/en/sql-reference/sql/create-file-format)
5. [`COPY INTO <table>`](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table)
6. [`COPY INTO <location>`](https://docs.snowflake.com/en/sql-reference/sql/copy-into-location)
7. [Loading data and 64-day load metadata](https://docs.snowflake.com/en/user-guide/data-load-considerations-load)
8. [Configure an S3 storage integration](https://docs.snowflake.com/en/user-guide/data-load-s3-config-storage-integration)
9. [`CREATE PIPE` and provider-specific auto-ingest parameters](https://docs.snowflake.com/en/sql-reference/sql/create-pipe)
10. [Snowpipe costs and current credit-per-GB billing](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-billing)
11. [`INFER_SCHEMA`](https://docs.snowflake.com/en/sql-reference/functions/infer_schema)
12. [Automatic table schema evolution](https://docs.snowflake.com/en/user-guide/data-load-schema-evolution)
13. [Snowpipe overview](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro)
14. [Snowpipe auto-ingest with cloud notifications](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-auto)
15. [`SYSTEM$PIPE_STATUS`](https://docs.snowflake.com/en/sql-reference/functions/system_pipe_status)
16. [`COPY_HISTORY`](https://docs.snowflake.com/en/sql-reference/functions/copy_history)
17. [Python Connector example](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-example)
18. [Python Connector API and `write_pandas`](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-api)
19. [Snowpipe Streaming high-performance architecture limitations and considerations](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-limitations)
20. [External tables overview](https://docs.snowflake.com/en/user-guide/tables-external-intro)
21. [Snowpipe Streaming Kafka connector architecture transition](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-classic-deprecation)

**Scope reminder:** this lesson covers the Stage 2C Snowflake Deep Dive Topic 04 syllabus and its required `experiments/04_loading/` exercise. It is a learning artifact, not evidence that cloud infrastructure, Snowpipe, or performance benchmarks were executed.
