# Querying Files and Object Storage with DuckDB

> **Stage 2 · Module 2.4 · Topic 06**
>
> Complete learning chapter: direct analytical file querying, multi-file lake datasets, Hive partitions, Parquet pruning, object storage, MinIO, secure credentials, remote-read mechanics, and production file-layout design.

## Central mental model

```text
Local:
Parquet / CSV / JSON
        ↓
      DuckDB
        ↓
       SQL
        ↓
      result

Remote:
S3 / MinIO / S3-compatible endpoint
        ↓
      DuckDB + httpfs
        ↓
       SQL
        ↓
      result
```

The important engineering question is not only **"Can DuckDB query the file?"** but:

> **How much physical data must DuckDB actually touch to answer the query?**

That amount depends on file format, partitions, file count, selected columns, predicates, Parquet row-group statistics, compression, cache state, network latency, and object-store request behavior.

---

# 1. Learning Objectives

After this chapter, you should be able to:

- query Parquet, CSV, and JSON directly;
- use `read_parquet`, `read_csv`, and `read_json`;
- read globs and explicit file lists;
- use `filename` for traceability;
- handle compatible schema drift with `union_by_name`;
- understand Hive partitioning and partition pruning;
- distinguish partition pruning, file selection, column pruning, and row-group skipping;
- inspect Parquet schema and metadata;
- write Parquet with `COPY`, compression, and `PARTITION_BY`;
- reason about the small-files problem;
- explain buckets, objects, keys, prefixes, endpoints, and credentials;
- use DuckDB `httpfs` for remote access;
- configure S3-compatible access safely;
- use MinIO for local remote-storage experiments;
- explain HTTP range requests and remote Parquet metadata/column-range reads;
- measure local versus remote query behavior fairly;
- understand Delta/Iceberg extension awareness;
- design production file layouts;
- diagnose slow remote queries and schema drift.

---

# 2. Prerequisites

You should already have basic knowledge of:

- Python;
- SQL;
- DuckDB fundamentals;
- Arrow;
- Parquet;
- Polars;
- Data Lakes/Lakehouses.

This chapter does not reteach those modules. It connects them.

---

# 3. Why Query Files Directly?

A common traditional workflow is:

```text
raw file
   ↓
load into database table
   ↓
query table
```

DuckDB also supports:

```text
raw analytical file
   ↓
query directly
```

This is valuable for:

- exploration;
- local ETL;
- CI data validation;
- development;
- ad-hoc investigation;
- single-node transformations;
- serverless/batch workloads.

The trade-off is that the **file becomes part of the physical design**. Repeatedly querying poorly organized raw files can be inefficient even when DuckDB is fast.

---

# 4. What Does "Query a File Directly" Mean?

```sql
SELECT *
FROM 'data/orders.parquet';
```

Equivalent reader-function form:

```sql
SELECT *
FROM read_parquet('data/orders.parquet');
```

Conceptually:

```text
SQL
 ↓
file reference
 ↓
file scanner
 ↓
query operators
 ↓
result
```

No persistent DuckDB table is required first.

Current DuckDB supports filename-based Parquet querying and `read_parquet()`; `read_parquet` is the form to use when you need scan options. [Official docs: current Parquet querying and file loading.]

---

# 5. Parquet as the Primary Analytical File

Parquet is well suited to analytical reads because it is:

- columnar;
- typed;
- compressed;
- organized into row groups;
- accompanied by metadata/statistics.

That allows a query engine to reason about physical reads rather than treating the file as an opaque text stream.

```text
Parquet
= on-disk analytical representation

DuckDB
= analytical query engine
```

---

# 6. Direct Parquet Queries

Start wide:

```sql
SELECT *
FROM 'orders.parquet';
```

Then select only required columns:

```sql
SELECT customer_id, amount
FROM 'orders.parquet';
```

Then aggregate:

```sql
SELECT customer_id, SUM(amount) AS revenue
FROM 'orders.parquet'
GROUP BY customer_id;
```

Then filter:

```sql
SELECT customer_id, SUM(amount) AS revenue
FROM 'orders.parquet'
WHERE order_date >= DATE '2026-01-01'
GROUP BY customer_id;
```

The later queries can perform less physical work because they request less data.

DuckDB documents automatic Parquet filter pushdown and reading only relevant columns when possible.

---

# 7. `read_parquet()`

```sql
SELECT *
FROM read_parquet('data/orders.parquet');
```

Multiple files:

```sql
SELECT *
FROM read_parquet('data/*.parquet');
```

Explicit list:

```sql
SELECT *
FROM read_parquet([
    'data/january.parquet',
    'data/february.parquet',
    'data/march.parquet'
]);
```

Use `read_parquet` when you need options such as:

```text
union_by_name
filename
hive_partitioning
```

---

# 8. CSV Reading

```sql
SELECT *
FROM read_csv('orders.csv');
```

CSV is weaker than Parquet as an analytical interchange format because it does not intrinsically carry the same structured schema and columnar metadata.

CSV concerns include:

- delimiter;
- quoting;
- escaping;
- header;
- null representation;
- type inference;
- date interpretation;
- malformed rows.

---

# 9. CSV Auto-Detection / Sniffer

DuckDB's CSV reader can infer:

```text
delimiter
quoting
escape
header
column types
date/timestamp characteristics
```

The inference is useful for exploration, but production pipelines should make important assumptions explicit.

You can inspect detection separately:

```sql
FROM sniff_csv('orders.csv');
```

The current sniffer is sampling-based; the sample size can be adjusted. Ambiguous dates are an especially important reason not to blindly trust inference.

Example ambiguity:

```text
01-02-2026
```

Could mean different dates depending on the producer's convention.

---

# 10. Explicit CSV Options

Required production controls include:

```text
columns=
types=
dateformat=
```

Schema example:

```sql
SELECT *
FROM read_csv(
    'orders.csv',
    columns = {
        'order_id': 'BIGINT',
        'customer_id': 'BIGINT',
        'amount': 'DECIMAL(18,2)',
        'order_date': 'DATE'
    }
);
```

Type override:

```sql
SELECT *
FROM read_csv(
    'orders.csv',
    types = {
        'order_id': 'BIGINT',
        'amount': 'DECIMAL(18,2)'
    }
);
```

Date format:

```sql
SELECT *
FROM read_csv(
    'orders.csv',
    dateformat = '%d-%m-%Y'
);
```

### Production lesson

Automatic inference is convenient. A schema contract is more reliable.

---

# 11. JSON Reading

```sql
SELECT *
FROM read_json('orders.json');
```

JSON is useful for semi-structured sources but introduces concerns around:

- nested objects;
- lists;
- missing keys;
- optional fields;
- inconsistent types.

Keep this chapter focused on file-level querying; deeper JSON data modeling belongs elsewhere.

---

# 12. Multi-File Reads

Data lakes commonly have:

```text
data/
├── 2026-01.parquet
├── 2026-02.parquet
└── 2026-03.parquet
```

Query:

```sql
SELECT *
FROM read_parquet('data/*.parquet');
```

Or:

```sql
SELECT *
FROM read_parquet([
    'data/a.parquet',
    'data/b.parquet'
]);
```

A multi-file scan should always be treated as an input contract:

```text
Which files are included?
Which schemas are expected?
Could old/temporary files match?
```

---

# 13. Globs

Examples:

```text
*.parquet
2026/*.parquet
2026/01/*.parquet
2026/**/*.parquet
```

A glob defines candidate paths.

It is **not** the same concept as pruning.

```text
glob
 ↓
candidate files

partition predicate
 ↓
files/partitions that may be necessary
```

An overly broad glob can include:

- archived data;
- temporary files;
- test outputs;
- incompatible schemas.

---

# 14. `filename=true`

For multi-file investigations:

```sql
SELECT *
FROM read_parquet(
    'data/*.parquet',
    filename = true
);
```

Use file provenance for:

- lineage;
- reconciliation;
- bad-file identification;
- schema-drift analysis;
- debugging.

Example:

```sql
SELECT
    filename,
    COUNT(*) AS row_count
FROM read_parquet(
    'data/*.parquet',
    filename = true
)
GROUP BY filename
ORDER BY filename;
```

Version note: current DuckDB releases also expose filename behavior through virtual-column machinery in newer file readers. Verify the installed version's exact behavior.

---

# 15. Schema Drift Across Files

Example:

```text
file1:
id
name
amount

file2:
id
name
amount
currency
```

Use name-based union when the differences are compatible:

```sql
SELECT *
FROM read_parquet(
    'data/*.parquet',
    union_by_name = true
);
```

Current DuckDB documentation states that `union_by_name` aligns columns by name and fills absent fields with `NULL`.

But this does not make incompatible types safe.

Example:

```text
file1.amount = INTEGER
file2.amount = VARCHAR
```

That is a type-contract problem.

---

# 16. Schema Drift vs Schema Evolution

### Schema drift

Unexpected change:

```text
producer changes shape without contract update
```

### Schema evolution

Managed change:

```text
version 1
id, amount

version 2
id, amount, currency
```

The technical scanner may be able to read both, but the operational treatment should differ.

---

# 17. Hive-Style Partitioning

Example:

```text
lake/
├── year=2025/
│   ├── month=01/
│   └── month=02/
└── year=2026/
    ├── month=01/
    └── month=02/
```

The directory/key structure encodes partition values.

```text
year=2026
month=02
```

This is Hive-style partitioning.

It is useful because query predicates can sometimes eliminate entire directories/prefixes before opening the actual Parquet data.

---

# 18. `hive_partitioning=true`

Current DuckDB syntax:

```sql
SELECT *
FROM read_parquet(
    'lake/**/*.parquet',
    hive_partitioning = true
);
```

The engine can interpret:

```text
year=2026
month=3
```

as partition columns.

DuckDB also documents automatic detection for common Hive layouts; explicit configuration remains useful when you want an intentional, visible setting.

---

# 19. Partition Pruning

Query:

```sql
SELECT SUM(revenue)
FROM read_parquet(
    'lake/**/*.parquet',
    hive_partitioning = true
)
WHERE year = 2026
  AND month = 3;
```

Conceptual execution:

```text
query predicate
      ↓
partition values
      ↓
skip irrelevant partitions
      ↓
read remaining files
```

Without effective pruning:

```text
many partitions
 ↓
many candidate files
```

With effective pruning:

```text
matching partitions
 ↓
smaller candidate set
```

DuckDB's current Hive-partition documentation describes partition filters being pushed into scans to skip unnecessary files.

Do not assume every predicate automatically prunes.

---

# 20. Partition Pruning vs File Filtering vs Row-Group Skipping

| Technique | Where it operates | Main information |
|---|---|---|
| Partition pruning | directory/key level | partition values |
| File selection | file level | paths/file metadata |
| Row-group skipping | within Parquet | statistics/metadata |
| Column pruning | column level | query projection |

These can stack:

```text
query
 ↓
partition pruning
 ↓
file selection
 ↓
row-group skipping
 ↓
column pruning
 ↓
physical reads
```

---

# 21. Parquet Projection Pushdown

Compare:

```sql
SELECT *
FROM 'orders.parquet';
```

with:

```sql
SELECT customer_id, amount
FROM 'orders.parquet';
```

Column pruning matters because Parquet stores columns separately enough for the engine to avoid unnecessary physical reads when the query does not need them.

Current DuckDB documentation explicitly notes automatic reading of relevant columns.

Remote benefit:

```text
fewer columns
 ↓
potentially fewer byte ranges
 ↓
less transfer
```

Do not infer exact byte counts without measurement.

---

# 22. Parquet Filter Pushdown

Example:

```sql
SELECT customer_id, amount
FROM 'orders.parquet'
WHERE amount > 1000;
```

The filter can be pushed into the Parquet scan.

Conceptually:

```text
SQL filter
 ↓
scan-level filtering
 ↓
less downstream work
```

The effectiveness depends on predicate form and file metadata.

---

# 23. Row-Group Statistics

A row group may have statistics such as:

```text
min
max
null count
```

Example:

```text
Row Group 1: amount 10..100
Row Group 2: amount 1000..5000
```

Query:

```sql
WHERE amount > 900
```

Row Group 1 can be excluded safely because:

```text
max(amount) = 100
```

No row there can satisfy the predicate.

The important word is **safely**.

If statistics are absent, broad, or not useful for the predicate, the engine may need to read the group.

---

# 24. `parquet_metadata()`

```sql
SELECT *
FROM parquet_metadata('orders.parquet');
```

Current DuckDB documentation exposes fields including:

```text
file_name
row_group_id
row_group_num_rows
row_group_bytes
path_in_schema
stats_min
stats_max
stats_null_count
compression
total_compressed_size
total_uncompressed_size
```

It also supports glob patterns.

Use it to investigate:

- row-group structure;
- compression;
- statistics;
- data sizes;
- file-level physical organization.

---

# 25. `parquet_schema()`

```sql
SELECT *
FROM parquet_schema('orders.parquet');
```

It exposes metadata describing the Parquet schema.

Use it to investigate:

- column names;
- physical types;
- logical types;
- nested fields;
- schema mismatches.

For a quick query-level view:

```sql
DESCRIBE
SELECT *
FROM 'orders.parquet';
```

---

# 26. Metadata Investigation Lab

1. Select a Parquet file.
2. Run `parquet_schema()`.
3. Run `parquet_metadata()`.
4. Identify row groups.
5. Inspect min/max information.
6. Select one highly selective query.
7. Explain what metadata could allow skipping.
8. Measure actual query behavior where practical.

Write:

```text
query
 ↓
metadata
 ↓
possible pruning
 ↓
physical reads
```

Then explain why pruning is not guaranteed.

---

# 27. Writing Files with `COPY`

```sql
COPY (
    SELECT customer_id, SUM(amount) AS revenue
    FROM orders
    GROUP BY customer_id
)
TO 'gold/customer_revenue.parquet'
(
    FORMAT parquet
);
```

DuckDB supports writing Parquet through `COPY`, including query results and tables.

This is useful for:

```text
raw/bronze
   ↓
DuckDB SQL
   ↓
silver/gold Parquet
```

---

# 28. Parquet Compression

Compression affects:

- storage;
- read I/O;
- network transfer;
- CPU cost.

Current DuckDB Parquet output supports multiple codecs, including:

```text
uncompressed
snappy
gzip
zstd
brotli
lz4/lz4_raw
```

Example:

```sql
COPY orders
TO 'orders-zstd.parquet'
(
    FORMAT parquet,
    COMPRESSION zstd
);
```

There is no universal best codec.

---

# 29. `PARTITION_BY`

Current DuckDB supports Hive-partitioned output:

```sql
COPY orders
TO 'gold/orders'
(
    FORMAT parquet,
    PARTITION_BY (year, month)
);
```

Conceptual result:

```text
gold/orders/
├── year=2026/
│   ├── month=01/
│   ├── month=02/
│   └── month=03/
└── year=2027/
```

`PARTITION_BY` accepts columns; if you need expressions, derive the columns in the `SELECT` feeding `COPY`.

---

# 30. Small-Files Problem

Compare:

```text
10,000 × 5 MB
```

with:

```text
100 × 500 MB
```

Similar total volume does not mean similar query behavior.

Tiny files can increase:

- object requests;
- metadata operations;
- planning overhead;
- network latency;
- operational complexity.

Remote object storage makes the penalty especially visible.

Never memorize a universal file size.

---

# 31. File Sizing Strategy

Ask:

- How many files does a typical query touch?
- How many queries run concurrently?
- What is the compression ratio?
- How selective are predicates?
- How many partitions exist?
- How frequently are files produced?
- How much parallelism is useful?

A good target balances:

```text
scan efficiency
+
parallelism
+
pruning
+
manageable object count
```

---

# 32. Object Storage Fundamentals

Core concepts:

- **bucket** — storage namespace;
- **object** — stored item;
- **key** — object identifier;
- **prefix** — common key prefix;
- **endpoint** — API service address;
- **credentials** — access identity/configuration.

Example:

```text
s3://lake/trips/year=2026/month=03/file.parquet
```

Think:

```text
s3://
 ↓
service protocol

lake
 ↓
bucket

trips/year=2026/month=03/file.parquet
 ↓
object key/prefix
```

Object storage is not literally a POSIX filesystem.

---

# 33. Local Filesystem vs Object Storage

| Concern | Local filesystem | Object storage |
|---|---|---|
| Path | filesystem path | object URI/key |
| Access | local OS/filesystem | API/network |
| Typical latency | local | network-dependent |
| Security | local permissions | credentials/IAM |
| Directory semantics | real filesystem hierarchy | key-prefix convention |
| Failure modes | disk/process/OS | network/service/auth/storage |

The remote model changes how file layout should be designed.

---

# 34. DuckDB `httpfs`

`httpfs` provides HTTP and S3 API filesystem support.

Manual installation/loading:

```sql
INSTALL httpfs;
LOAD httpfs;
```

The extension is autoloadable for supported functionality in current DuckDB installations.

Current documentation describes support for:

- HTTP(S) reads;
- S3 reads;
- S3 writes;
- S3 globbing;
- HTTP Range requests.

---

# 35. Querying S3-Compatible Storage

Conceptual example:

```sql
SELECT *
FROM 's3://lake/trips/year=2026/month=03/*.parquet';
```

Hive-aware:

```sql
SELECT COUNT(*)
FROM read_parquet(
    's3://lake/trips/**/*.parquet',
    hive_partitioning = true
)
WHERE year = 2026
  AND month = 3;
```

A valid remote query requires:

```text
correct endpoint
+
correct credentials
+
correct bucket/key
+
network access
```

---

# 36. MinIO as a Local S3-Compatible Environment

Architecture:

```text
Docker
  ↓
MinIO
  ↓
S3-compatible API
  ↓
DuckDB + httpfs
```

MinIO is useful for learning:

- object keys;
- buckets;
- S3 requests;
- remote query behavior;
- credentials;
- small-file effects.

This chapter does not create the Docker Compose file in the repository. Copy the file below into your own lab directory as `docker-compose.yml`. Set the lab-only credentials in your shell first (fake values, never real keys):

```bash
export MINIO_ACCESS_KEY=labuser
export MINIO_SECRET_KEY=labpassword123
export MINIO_ENDPOINT=localhost:9000
```

```yaml
services:
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY:?set MINIO_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY:?set MINIO_SECRET_KEY}
    ports:
      - "9000:9000"   # S3 API  -> MINIO_ENDPOINT=localhost:9000
      - "9001:9001"   # web console
    volumes:
      - minio-data:/data

  minio-init:
    image: minio/mc
    depends_on:
      - minio
    environment:
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY:?set MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY:?set MINIO_SECRET_KEY}
    volumes:
      - ./data/trips:/seed/trips:ro   # your local Hive-layout Parquet files
    entrypoint: >
      /bin/sh -c "
      until mc alias set lab http://minio:9000 $$MINIO_ACCESS_KEY $$MINIO_SECRET_KEY; do sleep 1; done &&
      mc mb --ignore-existing lab/lake &&
      mc mirror --overwrite /seed/trips lab/lake/trips &&
      mc ls --recursive lab/lake/trips
      "
    restart: "no"

volumes:
  minio-data:
```

Start it with `docker compose up`; the `minio-init` service waits for MinIO, creates the `lake` bucket, uploads your local files, lists what it uploaded, and exits. Pin the MinIO and `mc` image tags you validate in your own lab, and check the current MinIO documentation for image and command changes. This Compose file was checked for YAML syntax only; it was not run against Docker in the environment used to write this chapter.

Where the files come from: Compose cannot create Parquet data. The local source is `./data/trips/`, which you create yourself (for example with the fixture writer in the `lake_queries.py` reference implementation, or by copying NYC Taxi Parquet files into the layout below):

```text
data/trips/
├── year=2025/
│   ├── month=01/
│   │   └── part-001.parquet
│   └── month=02/
│       └── part-001.parquet
└── year=2026/
    ├── month=01/
    │   └── part-001.parquet
    └── month=02/
        └── part-001.parquet
```

Where they go: the init service mirrors `./data/trips/` to `s3://lake/trips/`, so the objects appear as `lake/trips/year=YYYY/month=MM/part-001.parquet`. The bucket is called `lake` because it stands in for a data lake bucket, and the layout is Hive-style (`key=value` directories) so DuckDB can read the partition values from the path and prune whole partitions.

---

# 37. MinIO Bucket/Layout Example

Use:

```text
s3://lake/trips/year=YYYY/month=MM/
```

Example:

```text
lake/
└── trips/
    ├── year=2025/
    │   ├── month=01/
    │   └── month=02/
    └── year=2026/
        ├── month=01/
        └── month=02/
```

This gives:

```text
S3 object storage
+
Hive partitioning
+
Parquet
```

---

# 38. DuckDB `CREATE SECRET`

Current DuckDB documentation recommends Secrets Manager-based authentication for S3 access.

Generic configuration-provider example:

```sql
CREATE OR REPLACE SECRET my_s3 (
    TYPE s3,
    PROVIDER config,
    KEY_ID '<ACCESS_KEY>',
    SECRET '<SECRET_KEY>',
    REGION '<REGION>'
);
```

For a custom S3-compatible service such as MinIO, a version-sensitive pattern is:

```sql
CREATE OR REPLACE SECRET minio_secret (
    TYPE s3,
    PROVIDER config,
    KEY_ID '<MINIO_ACCESS_KEY>',
    SECRET '<MINIO_SECRET_KEY>',
    ENDPOINT '<MINIO_ENDPOINT>',
    URL_STYLE 'path',
    USE_SSL false
);
```

Verify exact endpoint, SSL, and URL-style settings for the installed version and deployment.

The placeholders above show the shape only. In a real script, read the values from environment variables and pass them as parameters, so credentials never appear in SQL text. Verified on DuckDB 1.5.6, `CREATE SECRET` accepts positional `?` parameters:

```python
import os

import duckdb

minio_access_key = os.environ["MINIO_ACCESS_KEY"]
minio_secret_key = os.environ["MINIO_SECRET_KEY"]
minio_endpoint = os.environ.get("MINIO_ENDPOINT", "localhost:9000")

con = duckdb.connect()
try:
    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")
    con.execute(
        """
        CREATE OR REPLACE SECRET minio_secret (
            TYPE s3,
            PROVIDER config,
            KEY_ID ?,
            SECRET ?,
            ENDPOINT ?,
            URL_STYLE 'path',
            USE_SSL false
        )
        """,
        [minio_access_key, minio_secret_key, minio_endpoint],
    )
    print(con.execute(
        """
        SELECT COUNT(*) AS trips
        FROM read_parquet('s3://lake/trips/**/*.parquet', hive_partitioning = true)
        """
    ).fetchone())
finally:
    con.close()
```

```text
environment variables
        ↓
Python os.environ
        ↓
parameterized CREATE SECRET
        ↓
DuckDB
```

Do not build the statement with an f-string or string concatenation. `INSTALL httpfs` needs network access the first time; the query needs MinIO running with data uploaded (this block was not run against a live MinIO in the environment used to write this chapter; the parameterized `CREATE SECRET` itself was run).

---

# 39. Credential Sources

Possible approaches include:

- environment variables;
- local profiles;
- cloud credential chains;
- workload/instance identity;
- temporary session credentials;
- DuckDB secrets.

Current DuckDB documentation describes an S3 `credential_chain` provider for discovering credentials through AWS SDK mechanisms.

Production preference:

```text
managed identity / credential chain
        ↓
temporary authorization
        ↓
DuckDB
```

rather than permanent plaintext keys.

---

# 40. Secrets Hygiene

Never do this:

```python
access_key = "REAL_SECRET"
secret_key = "REAL_SECRET"
```

Never commit real secrets to SQL:

```sql
CREATE SECRET ...
```

with production keys.

Safer:

```text
credential source
 ↓
environment / identity / secret manager
 ↓
DuckDB
```

Secrets can leak through:

- Git history;
- logs;
- notebooks;
- screenshots;
- shell history;
- error reports.

Use placeholders in educational examples.

---

# 41. Remote Read Mechanics

Conceptual model:

```text
SQL
 ↓
candidate files/partitions
 ↓
metadata discovery
 ↓
selected columns / ranges
 ↓
HTTP Range requests
 ↓
decode
 ↓
query operators
```

Remote analytics therefore does not inherently mean:

```text
download everything
 ↓
save locally
 ↓
query
```

An analytical engine can often issue targeted requests.

The exact request pattern depends on implementation, format, cache state, and remote service.

---

# 42. Reading File Footers Remotely

Parquet places important metadata near the end of a file.

Conceptually:

```text
┌─────────────────────────────┐
│ column data                 │
│ row groups                  │
│ column chunks               │
│ ...                         │
│ Parquet metadata/footer     │
└─────────────────────────────┘
```

Remote clients can use byte-range reads to retrieve metadata without downloading the complete data payload.

Do not memorize an exact one-request rule. Actual requests vary.

---

# 43. Reading Required Column Chunks

Suppose:

```text
id | name | amount | address | notes
```

and:

```sql
SELECT id, amount
FROM 'orders.parquet';
```

The engine can often avoid reading unrelated columns.

Conceptually:

```text
Need:
id
amount

Potentially avoid:
name
address
notes
```

That becomes particularly important over object storage because bytes not transferred are often more valuable than bytes transferred quickly.

---

# 44. Remote Query Cost Model

Use this engineering model:

```text
remote query cost
≈
metadata requests
+
bytes transferred
+
network latency
+
decompression CPU
+
query CPU
+
temporary storage
```

It is not a literal DuckDB formula.

It is a checklist for reasoning.

---

# 45. Local vs MinIO Benchmark

Run the same query against:

```text
local Parquet
```

and:

```text
MinIO Parquet
```

Keep the following identical:

- logical data;
- layout;
- SQL;
- DuckDB version;
- machine;
- configuration.

Measure:

```text
runtime
files touched
partitions
bytes/request data where measurable
correctness
```

Never fabricate a result.

---

# 46. Bytes Actually Read vs Total File Size

Important:

```text
total lake size
≠
bytes transferred by every query
```

A selective query can read much less physical data than the logical dataset because of:

- partition pruning;
- projection;
- filter pushdown;
- row-group skipping;
- caching.

Conversely, a broad query can approach a full scan.

## Comparing File Size With Measured I/O

Keep these separate:

```text
file size
    ≠
bytes physically read by every query
    ≠
bytes transferred over the network
```

Start with the local size of the dataset:

```python
from pathlib import Path

total_bytes = sum(
    p.stat().st_size
    for p in Path("data/trips").rglob("*.parquet")
)

print(f"Total Parquet file bytes: {total_bytes:,}")
```

Then run the query under `EXPLAIN ANALYZE`:

```sql
EXPLAIN ANALYZE
SELECT
    COUNT(*) AS trips,
    SUM(fare_amount) AS revenue
FROM read_parquet(
    's3://lake/trips/**/*.parquet',
    hive_partitioning = true
)
WHERE year = 2026
  AND month = 2;
```

The layout in this chapter has months 01 and 02, so `month = 2` selects a partition that exists. `EXPLAIN ANALYZE` is the query and operator evidence: inspect the table scan node (which columns it projects, the file filters, and how many files it scanned out of the total), the row counts at each operator, and the per-operator and total time. It does not, by itself, report exact network bytes. On the local fixture the scan node reported `Scanning Files: 1/4` for this kind of query; check what yours reports.

For physical I/O, pair it with a separate source: MinIO request logs or metrics, network or object-store telemetry, local file statistics, or another I/O metric your DuckDB version exposes. Record which one you used.

Exercise:

1. Measure total Parquet bytes (above).
2. Run `EXPLAIN ANALYZE` on the broad query (no partition predicate).
3. Apply the selective partition predicate (`year = 2026 AND month = 2`).
4. Compare the broad query with the selective query: files scanned, rows at the scan, runtime.
5. Inspect MinIO request and byte telemetry where available.
6. Record runtime and confirm both queries are correct (row counts, sums).
7. Explain why the selective query should touch less data, and where your measurements agree or disagree.

Do not copy numbers from anywhere else; the values depend on your data, cache state and setup.

---

# 47. MinIO Request Logs / Metrics

The diagnostic question is:

> How many requests did the query create?

Use the current MinIO logging/metrics mechanism available in your environment.

Correlate:

```text
SQL
 ↓
files
 ↓
requests
 ↓
bytes
 ↓
runtime
```

This turns a vague "remote is slow" problem into a measurable engineering problem.

---

# 48. Remote Small-Files Problem

Example:

```text
50,000 tiny objects
```

Potential consequences:

```text
object count
 ↓
request count
 ↓
latency
 ↓
startup/planning overhead
 ↓
slow query
```

Even when total bytes are small, request overhead can dominate.

---

# 49. Caching

Benchmarking needs to distinguish:

```text
cold
```

and:

```text
warm
```

Cold may involve more physical reads.

Warm may reuse cached data/metadata.

Possible cache layers include:

- operating-system cache;
- local filesystem cache;
- remote service/cache layers;
- repeated-access effects.

Do not assume every layer behaves the same.

---

# 50. Remote Performance Tuning Framework

1. Reduce files touched.
2. Reduce columns read.
3. Reduce row groups read.
4. Reduce bytes transferred.
5. Avoid tiny files.
6. Align partitions with real query predicates.
7. Choose compression deliberately.
8. Avoid repeated remote scans.
9. Measure cold and warm cases.
10. Verify endpoint and credentials.

The guiding principle is:

> **Reduce physical remote work before optimizing the remaining computation.**

---

# 51. Debugging Remote Queries

## Symptom 1 — Too much data downloaded

Investigate:

- `SELECT *`;
- weak predicates;
- poor partition layout;
- unhelpful row-group statistics.

## Symptom 2 — Too many requests

Investigate:

- tiny files;
- excessive partitions;
- broad glob patterns.

## Symptom 3 — Authentication failure

Investigate:

- credentials;
- endpoint;
- scope;
- region;
- temporary credential expiration.

## Symptom 4 — Local fast, MinIO slow

Investigate:

- latency;
- request count;
- bytes transferred;
- cache state;
- MinIO resources.

## Symptom 5 — Schema mismatch

Investigate:

- `union_by_name`;
- file schemas;
- filename provenance;
- producer changes.

For every incident, write:

```text
symptom
→ root cause
→ evidence
→ correction
→ production lesson
```

---

# 52. Delta and Iceberg Extensions — Awareness Level

At awareness level:

```text
DuckDB
 ↓
extension
 ↓
Delta / Iceberg table metadata
 ↓
data files
```

The important architectural point is that an open table format adds managed metadata/table semantics around data files.

Do not turn this section into a deep Delta/Iceberg implementation course.

---

# 53. `delta` Extension

Conceptually:

```text
DuckDB
 ↓
delta extension
 ↓
Delta Lake table
```

Use it to understand interoperability.

Verify current installation/loading/query syntax against the installed DuckDB version.

---

# 54. `iceberg` Extension

Conceptually:

```text
DuckDB
 ↓
iceberg extension
 ↓
Iceberg table
```

The same rule applies: awareness here; deep table-format architecture later.

---

# 55. Folder of Parquet vs Lakehouse Table

### Plain Parquet dataset

```text
orders/
├── a.parquet
├── b.parquet
└── c.parquet
```

### Table format

```text
orders/
├── table metadata
├── manifests/log structures
└── data files
```

A folder is primarily a set of files plus naming/layout conventions.

A table format can add:

- snapshots;
- table metadata;
- schema-management semantics;
- table-level visibility/maintenance.

---

# 56. Production File Layout Design

Evaluate:

- common predicates;
- partition cardinality;
- file size;
- row-group structure;
- compression;
- schema consistency;
- update frequency;
- object-store request overhead.

Potentially dangerous:

```text
year/month/day/customer_id
```

when `customer_id` has extremely high cardinality.

The correct design is workload-dependent.

---

# 57. Partition-Key Design Trade-offs

### Too coarse

```text
year=2026
```

A month query can still scan a lot of data.

### Too fine

```text
year/month/day/customer_id
```

Can create enormous numbers of objects.

Therefore:

```text
query pattern
+
data volume
+
cardinality
+
write pattern
+
operational constraints
```

should drive partition selection.

---

# 58. Schema Management

Production rules:

- define explicit schemas where possible;
- validate incoming schema;
- track changes;
- use controlled evolution;
- maintain type compatibility.

For multi-file scans:

```text
schema drift
+
remote access
=
reliability + performance risk
```

---

# 59. Data Quality + File-Level Traceability

Use filename provenance to support:

- lineage;
- reconciliation;
- quarantine;
- producer accountability;
- malformed-file debugging.

Example:

```sql
SELECT
    filename,
    COUNT(*) AS rows
FROM read_parquet(
    'raw/*.parquet',
    filename = true
)
GROUP BY filename;
```

---

# 60. Required Hands-On Project — `lake_queries.py`

> **Do not create the actual script in this chapter.** This section specifies the exercise only. A complete reference implementation follows Step 13; write your own version first.

Goal:

```text
bronze Parquet
 ↓
Hive-partitioned dataset
 ↓
MinIO
 ↓
DuckDB + httpfs
 ↓
selective remote SQL
 ↓
gold Parquet
```

### Step 1 — Create MinIO environment

Use the Docker Compose file in "MinIO as a Local S3-Compatible Environment".

Record:

- endpoint;
- bucket;
- MinIO version;
- lab-only credentials.

### Step 2 — Create Hive layout

```text
s3://lake/trips/year=YYYY/month=MM/
```

### Step 3 — Upload Parquet

Use the roadmap's NYC Taxi dataset or an equivalent generated dataset.

### Step 4 — Configure DuckDB

Use current `httpfs` functionality.

### Step 5 — Configure credentials

Use:

- environment variables;
- managed credential chain;
- or appropriate secret configuration.

Never hard-code credentials.

### Step 6 — Query one month

```sql
SELECT
    COUNT(*) AS trips,
    SUM(fare_amount) AS revenue
FROM read_parquet(
    's3://lake/trips/**/*.parquet',
    hive_partitioning = true
)
WHERE year = 2026
  AND month = 3;
```

### Step 7 — Projection experiment

Compare:

```sql
SELECT *
FROM read_parquet('s3://lake/trips/**/*.parquet');
```

with:

```sql
SELECT pickup_zone, fare_amount
FROM read_parquet('s3://lake/trips/**/*.parquet');
```

### Step 8 — Partition pruning experiment

Compare:

```text
broad scan
```

with:

```text
year=2026 AND month=3
```

### Step 9 — Schema drift experiment

Read compatible files using:

```text
union_by_name=true
filename=true
```

### Step 10 — Gold output

```sql
COPY (
    SELECT *
    FROM read_parquet(
        's3://lake/trips/**/*.parquet',
        hive_partitioning = true
    )
)
TO 'gold/trips'
(
    FORMAT parquet,
    PARTITION_BY (year, month)
);
```

Verify current syntax before execution.

### Step 11 — Local vs MinIO benchmark

Measure:

```text
environment
files
partitions
bytes/requests
runtime
correctness
```

### Step 12 — Investigate requests

Use MinIO logs/metrics or another valid telemetry method.

### Step 13 — Document findings

```text
| Environment | Files | Partitions | Bytes/Requests | Runtime | Correct? |
|-------------|-------|------------|----------------|---------|----------|
| Local       |       |            |                |         |          |
| MinIO       |       |            |                |         |          |
```

### Reference implementation — `lake_queries.py`

```text
functional validation dataset   → the 400-row fixture below: proves the SQL and workflow
performance benchmark dataset   → large realistic data (for example NYC Taxi): the only basis for performance conclusions
```

The script reads MinIO credentials from environment variables and creates the secret with a parameterized call. Without those variables it runs the same queries against the local `data/trips` directory, so you can validate the logic before starting MinIO. Only remote mode exercises `httpfs` and S3 access, and remote mode was not run in the environment used to write this chapter; local mode was run on DuckDB 1.5.6. The gold output goes to `s3://lake/gold/trips_by_zone` in remote mode and to `gold/trips` locally.

```python
"""Reference implementation for the Topic 06 project.

Functional validation dataset: 4 small partitions (400 rows), so it runs in seconds.
It proves the SQL and the workflow, NOT performance. Use a large realistic dataset
(for example NYC Taxi) for any performance conclusion.

Remote mode: MINIO_ACCESS_KEY and MINIO_SECRET_KEY are set, MinIO is running via the
Compose file, and data/trips has been uploaded to s3://lake/trips/.
Local mode (otherwise): the same queries run against ./data/trips.
"""

import os
from pathlib import Path

import duckdb

LOCAL_TRIPS = Path("data/trips")
CSV_DIR = Path("data/csv_drift")


def write_fixture_trips() -> None:
    """Deterministic Hive-layout Parquet: data/trips/year=YYYY/month=MM/part-001.parquet."""
    if list(LOCAL_TRIPS.rglob("*.parquet")):
        return
    con = duckdb.connect()
    try:
        for year in (2025, 2026):
            for month in (1, 2):
                part = LOCAL_TRIPS / f"year={year}" / f"month={month:02d}"
                part.mkdir(parents=True, exist_ok=True)
                con.execute(f"""
                    COPY (
                        SELECT
                            i AS trip_id,
                            'zone-' || (i % 5) AS pickup_zone,
                            CAST(10 + (i % 20) AS DECIMAL(10, 2)) AS fare_amount
                        FROM range(100) AS t(i)
                    ) TO '{part / "part-001.parquet"}' (FORMAT parquet)
                """)  # paths are generated here, not user input
    finally:
        con.close()


def connect() -> tuple[duckdb.DuckDBPyConnection, str, str]:
    """Returns (connection, trips_base_url, gold_base_url)."""
    con = duckdb.connect()
    if "MINIO_ACCESS_KEY" not in os.environ:
        print("mode: LOCAL (MINIO_ACCESS_KEY is not set)")
        Path("gold").mkdir(exist_ok=True)
        return con, str(LOCAL_TRIPS), "gold/trips"

    print("mode: REMOTE (MinIO)")
    access_key = os.environ["MINIO_ACCESS_KEY"]
    secret_key = os.environ["MINIO_SECRET_KEY"]
    endpoint = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")
    con.execute(
        """
        CREATE OR REPLACE SECRET minio_secret (
            TYPE s3,
            PROVIDER config,
            KEY_ID ?,
            SECRET ?,
            ENDPOINT ?,
            URL_STYLE 'path',
            USE_SSL false
        )
        """,
        [access_key, secret_key, endpoint],
    )
    return con, "s3://lake/trips", "s3://lake/gold/trips_by_zone"


def csv_drift_lab(con: duckdb.DuckDBPyConnection) -> None:
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    (CSV_DIR / "2026-01.csv").write_text("id,name,amount\n1,alice,10.5\n2,bob,20.0\n")
    (CSV_DIR / "2026-02.csv").write_text("id,name,amount,currency\n3,cara,30.0,EUR\n")
    pattern = str(CSV_DIR / "*.csv")

    unsafe = con.execute("SELECT * FROM read_csv(?)", [pattern])
    unsafe_columns = [c[0] for c in unsafe.description]
    print("default read columns:", unsafe_columns)  # is 'currency' missing?

    safe = con.execute(
        "SELECT * FROM read_csv(?, union_by_name = true, filename = true) ORDER BY id",
        [pattern],
    )
    safe_columns = [c[0] for c in safe.description]
    rows = safe.fetchall()
    print("union_by_name columns:", safe_columns)
    assert "currency" in safe_columns and "filename" in safe_columns
    assert len(rows) == 3
    currency = safe_columns.index("currency")
    assert [r[currency] for r in rows] == [None, None, "EUR"]  # earlier file -> NULL


def main() -> None:
    write_fixture_trips()
    con, trips, gold = connect()
    try:
        glob = f"{trips}/**/*.parquet"
        # Zero-padded directories such as month=02 are read as VARCHAR by default,
        # so pin the partition column types explicitly.
        hive = "hive_partitioning = true, hive_types = {'year': 'INTEGER', 'month': 'INTEGER'}"
        source = f"read_parquet('{glob}', {hive})"

        # Hive partition filtering + projection (only the needed columns)
        selective = f"""
            SELECT COUNT(*) AS trips, SUM(fare_amount) AS revenue
            FROM {source}
            WHERE year = 2026 AND month = 2
        """
        trips_count, revenue = con.execute(selective).fetchone()
        assert trips_count == 100
        total = con.execute(f"SELECT COUNT(*) FROM {source}").fetchone()[0]
        assert total == 400 and trips_count < total
        print("month 2026-02:", trips_count, "trips; all partitions:", total)

        # filename=true: which file produced which rows
        by_file = con.execute(
            f"SELECT filename, COUNT(*) FROM read_parquet('{glob}', {hive}, filename = true) GROUP BY filename ORDER BY filename"
        ).fetchall()
        assert len(by_file) == 4
        print("files read:", len(by_file))

        # EXPLAIN ANALYZE: operator evidence for the selective query
        plan = con.execute("EXPLAIN ANALYZE " + selective).fetchall()[0][1]
        print(plan)

        # CSV schema drift, unsafe vs intentional
        csv_drift_lab(con)

        # Gold: write a partitioned aggregate, then read it back and reconcile
        con.execute(
            f"""
            COPY (
                SELECT year, month, pickup_zone, COUNT(*) AS trips, SUM(fare_amount) AS revenue
                FROM {source}
                GROUP BY ALL
            ) TO '{gold}' (FORMAT parquet, PARTITION_BY (year, month), OVERWRITE_OR_IGNORE)
            """
        )
        gold_trips = con.execute(
            f"SELECT SUM(trips) FROM read_parquet('{gold}/**/*.parquet', hive_partitioning = true)"
        ).fetchone()[0]
        assert gold_trips == total
        print("gold reconciles:", gold_trips, "trips")
    finally:
        con.close()
    print("all checks passed")


if __name__ == "__main__":
    main()
```

---

# 61. Required Parquet Metadata Lab

Required work:

1. inspect `parquet_schema()`;
2. inspect `parquet_metadata()`;
3. identify row groups;
4. inspect statistics;
5. run selective filters;
6. compare physical behavior where measurable;
7. document when pruning did and did not help.

---

# 62. Required Schema-Drift Lab

**Warning:** in the verified environment used for this chapter (DuckDB 1.5.6), the default multi-file CSV read did not fail when the later file contained an additional column, and the extra column was not preserved in the resulting relation. That is not a guarantee about every DuckDB version, reader option or CSV configuration. Never interpret "the query succeeded" as "the schema was preserved."

Create logically equivalent files:

```text
2026-01.csv
id,name,amount

2026-02.csv
id,name,amount,currency
```

First, the risky read, without `union_by_name`:

```sql
SELECT *
FROM read_csv('data/csv_drift/*.csv');
```

Then the intentional read:

```sql
SELECT *
FROM read_csv(
    'data/csv_drift/*.csv',
    union_by_name = true,
    filename = true
);
```

The intentional read should return these columns, with `NULL` in `currency` for rows from the earlier file (when the schemas are compatible):

```text
id
name
amount
currency
filename
```

A runnable version that writes the two files and runs both reads:

```python
from pathlib import Path

import duckdb

csv_dir = Path("data/csv_drift")
csv_dir.mkdir(parents=True, exist_ok=True)
(csv_dir / "2026-01.csv").write_text("id,name,amount\n1,alice,10.5\n2,bob,20.0\n")
(csv_dir / "2026-02.csv").write_text("id,name,amount,currency\n3,cara,30.0,EUR\n")
pattern = str(csv_dir / "*.csv")

con = duckdb.connect()
try:
    unsafe = con.execute("SELECT * FROM read_csv(?)", [pattern])
    print("default columns:      ", [c[0] for c in unsafe.description])

    safe = con.execute(
        "SELECT * FROM read_csv(?, union_by_name = true, filename = true) ORDER BY id",
        [pattern],
    )
    print("union_by_name columns:", [c[0] for c in safe.description])
    for row in safe.fetchall():
        print(row)
finally:
    con.close()
```

Inspect the row count, the column names, the `currency` nulls and the `filename` values. Then answer:

- What changed between the two files?
- What was silently lost without `union_by_name`?
- Which rows receive `NULL` for the new field?
- Which file produced each row?
- Which fields are new?
- Are the resulting types correct?
- Is the change expected?

---

# 63. Required Partition-Pruning Lab

Dataset:

```text
year=2025/month=01
year=2025/month=02
year=2026/month=01
year=2026/month=02
```

Queries:

```text
A: all years
B: year=2026
C: year=2026 AND month=02
```

For each record:

```text
files
partitions
bytes
runtime
correctness
```

---

# 64. Required Remote-Cost Lab

Build two layouts containing the same logical data:

### A — Many small files

### B — Fewer larger files

Run identical queries.

Measure:

```text
request count
bytes transferred
runtime
correctness
```

Explain why physical layout changed cost.

---

# 65. Required Security Lab

Start with:

```python
access_key = "REAL_SECRET"
```

Redesign it into:

```text
environment / credential chain / managed identity
+
secret configuration
+
least privilege
```

No real secret should appear in the chapter or repository.

---

# 66. Required File-to-Object-Storage Architecture

```text
Source
 ↓
Raw files
 ↓
Parquet conversion
 ↓
Object storage
 ↓
Hive partitions
 ↓
DuckDB
 ↓
partition pruning
+ projection pushdown
+ predicate pushdown
 ↓
analytics
 ↓
gold Parquet
```

Identify for each stage:

```text
data size
schema
security
I/O
failure modes
observability
```

---

# 67. Production Object-Storage Architecture

```text
Applications / pipelines
          ↓
      object store
          ↓
   partitioned Parquet
          ↓
     query engines
          ↓
      downstream
```

Production concerns:

- layout;
- schema;
- identity;
- object count;
- request rate;
- monitoring;
- correctness;
- recovery.

---

# 68. Senior Data Engineer Performance Questions

Ask before running a remote query:

- How many files?
- How many partitions?
- Which columns?
- How selective is the predicate?
- Can row groups be skipped?
- How many bytes?
- How many object requests?
- Are files too small?
- Is cache cold?
- Does the query repeatedly rescan the same remote data?

---

# 69. Important Principle — `SELECT *`

`SELECT *` is reasonable when you genuinely need all columns.

It is often unnecessary for a wide remote dataset.

Prefer:

```sql
SELECT customer_id, amount
FROM 's3://lake/orders/*.parquet';
```

when that is the actual data requirement.

---

# 70. Important Principle — Remote Data Changes the Cost Model

Local:

```text
CPU + RAM + disk
```

Remote:

```text
CPU
+
RAM
+
network
+
request latency
+
object-store behavior
+
credentials
```

A query can be cheap locally and expensive remotely without the SQL being wrong.

---

# 71. Important Principle — Security Is Part of Pipeline Design

A production remote query needs:

```text
data access
+
identity
+
least privilege
+
credential lifecycle
+
auditability
```

Authentication is part of architecture.

---

# 72. Debugging Checklist

When a file query is unexpectedly slow:

```text
1. How many files?
2. How many partitions?
3. Is the partition filter present?
4. Is SELECT * used?
5. Is the file format Parquet?
6. What statistics exist?
7. Are row groups selective?
8. Are files tiny?
9. Local or remote?
10. How many requests?
11. How many bytes?
12. Is cache cold?
13. Did schema drift occur?
14. Is the endpoint/credential configuration correct?
```

---

# 73. Benchmarking Methodology

A fair benchmark requires:

```text
same dataset
+
same query
+
same file layout
+
same hardware
+
same DuckDB version
+
same configuration
```

Remote tests should also document:

```text
endpoint
network conditions
cache state
object count
partition count
```

Measure:

- runtime;
- bytes;
- files;
- requests;
- correctness.

Never fabricate values.

---

# 74. Cold vs Warm Runs

### Cold

Caches are not already populated to the same degree.

### Warm

Repeated reads may benefit from caching.

Both are valid benchmark conditions.

The mistake is comparing them without documenting the difference.

---

# 75. Correctness Before Optimization

Every experiment must validate:

- row count;
- schema;
- aggregate results;
- selected values;
- output equivalence.

Remember:

```text
faster
≠
correct
```

---

# 76. Production Failure Scenarios

1. `SELECT *` over huge remote files  
   **Fix:** reduce projection and measure bytes.

2. Partition filter omitted  
   **Fix:** align query predicates with the partition design.

3. Tiny-file explosion  
   **Fix:** compact and revisit partition cardinality.

4. Monthly schema drift  
   **Fix:** detect, classify, validate, and manage evolution.

5. Credential expiry  
   **Fix:** use supported credential refresh/chain mechanisms.

6. Wrong S3 endpoint  
   **Fix:** validate endpoint and URL-style configuration.

7. MinIO differs from production cloud  
   **Fix:** treat MinIO as a local compatibility environment, not an exact production simulation.

8. Row-group pruning weak  
   **Fix:** inspect metadata and data clustering.

9. Warm cache hides cost  
   **Fix:** benchmark cold/warm separately.

10. Gold output creates too many objects  
    **Fix:** revisit partition keys and file sizing.

---

# 77. Common Mistakes

- trusting CSV auto-detection in production;
- creating thousands of tiny files;
- hard-coding secrets;
- scanning a whole remote dataset when the query could be selective;
- unnecessary `SELECT *`;
- over-partitioning;
- under-partitioning;
- confusing partitions and row groups;
- assuming remote query means full download;
- assuming remote query never downloads unnecessary data;
- ignoring schema drift;
- ignoring request count;
- comparing cold and warm benchmarks as if identical.

---

# 78. Production Engineering Patterns

## Pattern A — CSV → Parquet

```text
CSV
 ↓
schema validation
 ↓
DuckDB
 ↓
Parquet
```

## Pattern B — Lake analytics

```text
S3/MinIO
 ↓
Hive-partitioned Parquet
 ↓
DuckDB
 ↓
SQL
```

## Pattern C — Gold build

```text
raw object storage
 ↓
DuckDB
 ↓
partitioned Parquet
 ↓
gold
```

## Pattern D — Drift-aware ingestion

```text
multi-file scan
 ↓
union_by_name
 ↓
filename
 ↓
schema validation
```

---

# 79. DuckDB + Object Storage vs Loading Everything Locally

### Full download first

Potential downsides:

- local storage;
- duplicated bytes;
- unnecessary transfer;
- startup delay.

### Direct remote query

Potential benefits:

- selective reads;
- no full local copy;
- lake-native access.

Potential downsides:

- network dependency;
- credentials;
- request latency;
- remote-service failures.

The correct design depends on workload.

---

# 80. Security and Operations in Production

Consider:

- credential rotation;
- temporary credentials;
- IAM/role-based access;
- endpoint configuration;
- audit logging;
- network controls;
- least privilege.

Deep cloud IAM belongs in later modules.

---

# 81. Interview Preparation

## Beginner

### What is direct file querying?

Treating the supported file as a relation during query execution without first creating a persistent database table.

### What is `read_parquet()`?

DuckDB's Parquet reader/table function for scanning one or more Parquet files.

### What is a glob?

A path pattern identifying candidate files.

### What is object storage?

API-based storage of objects in buckets using object keys.

### What is Hive partitioning?

A layout that encodes partition values in path components such as `year=2026/month=03`.

## Intermediate

### What is `union_by_name`?

A multi-file read option that aligns columns by name and can fill missing fields with `NULL`.

### Why `filename=true`?

For lineage, reconciliation, debugging, and schema-drift tracing.

### What is partition pruning?

Avoiding partitions that cannot satisfy the query predicate.

### What is projection pushdown?

Reading only columns required by the query.

### What is filter pushdown?

Pushing a predicate toward the scan to reduce downstream work and potentially physical reads.

### What are row-group statistics?

Parquet metadata that can support safe exclusion of row groups.

### What are `parquet_metadata()` and `parquet_schema()`?

Queryable functions exposing Parquet metadata and embedded schema.

### Why do tiny files hurt?

They increase file/object count, metadata operations, and often request latency.

### What is `httpfs`?

DuckDB's HTTP/S3 filesystem extension for remote analytical file access.

## Advanced

### How does DuckDB reduce remote I/O?

By combining query projections/predicates with partition and Parquet metadata where possible.

### What is an HTTP range request?

A request for a selected byte range of a remote object.

### Why does the footer matter?

It provides Parquet metadata needed to understand file structure.

### How can only required columns be read?

The engine uses the query projection plus Parquet physical layout/metadata to select relevant column ranges.

### How do you design partitions?

Start with common filters, constrain cardinality, maintain usable files, and validate real queries.

### How do you diagnose high remote transfer?

Measure files, partitions, projection, predicate, metadata, request count, bytes, cache state, and layout.

### Why might row-group pruning fail?

Statistics may not be selective or the predicate may not permit safe elimination.

### How do you design object-storage credentials?

Prefer managed/temporary identity mechanisms, scope access, and keep long-lived keys out of source control.

### How do you compare local and MinIO?

Same data, query, layout, version, machine, configuration, documented cache state, and correctness checks.

### How do you redesign 100,000 tiny files?

Measure first, compact, reconsider partition cardinality, and validate query performance after redesign.

### Folder of Parquet vs Delta/Iceberg?

The table format adds managed metadata and table semantics around the data files.

---

# 82. Architecture Scenarios

1. **5 TB lake partitioned only by year:** evaluate common query filters and consider whether another low/moderate-cardinality partition improves pruning.
2. **500 GB with millions of tiny files:** measure request overhead and compact/repartition.
3. **Two columns needed but `SELECT *`:** narrow the projection.
4. **MinIO is much slower than local:** measure latency, requests, bytes, cache, and resource limits.
5. **Schema changes every month:** establish an evolution contract and validation gate.
6. **Month predicate still scans everything:** verify Hive detection, path pattern, and actual partition columns.
7. **Credentials in SQL files:** rotate/remove them and move to safe credential sources.
8. **Gold data has excessive partition cardinality:** redesign partitions based on query patterns.
9. **First query slow, second fast:** identify cache effects.
10. **Team wants lakehouse table format:** evaluate snapshots, metadata, schema evolution, governance, and update semantics.

---

# 83. Explain-Aloud Exercises

Explain without reading:

1. direct file querying;
2. why Parquet fits DuckDB;
3. schema drift;
4. `union_by_name`;
5. `filename`;
6. Hive partitioning;
7. partition pruning;
8. row-group skipping;
9. projection pushdown;
10. filter pushdown;
11. small-files problem;
12. object storage;
13. `httpfs`;
14. HTTP range request;
15. Parquet footer;
16. credential architecture;
17. local versus remote performance.

---

# 84. Practice Problems

## Basic — 10

1. Query a single Parquet file.
2. Query two Parquet files.
3. Read a CSV file.
4. Read a JSON file.
5. Use a Parquet glob.
6. Use a list of Parquet files.
7. Aggregate by `customer_id`.
8. Filter before an aggregation.
9. Inspect `parquet_schema()`.
10. Inspect `parquet_metadata()`.

### Answer key

```sql
SELECT * FROM 'orders.parquet';

SELECT * FROM read_parquet(['a.parquet','b.parquet']);

SELECT * FROM read_csv('orders.csv');

SELECT * FROM read_json('orders.json');

SELECT * FROM read_parquet('data/*.parquet');

SELECT customer_id, SUM(amount)
FROM 'orders.parquet'
GROUP BY customer_id;

SELECT customer_id, SUM(amount)
FROM 'orders.parquet'
WHERE order_date >= DATE '2026-01-01'
GROUP BY customer_id;

SELECT * FROM parquet_schema('orders.parquet');

SELECT * FROM parquet_metadata('orders.parquet');
```

## Moderate — 10

1. Add `filename`.
2. Use `union_by_name`.
3. Enable Hive partitioning.
4. Filter one partition.
5. Write Parquet.
6. Write partitioned Parquet.
7. Override CSV types.
8. Set CSV date format.
9. Explain `SELECT *` remote cost.
10. Explain partition vs row group.

### Answer key

1. `read_parquet(..., filename=true)`.
2. `read_parquet(..., union_by_name=true)`.
3. `read_parquet(..., hive_partitioning=true)`.
4. Add the partition predicate in `WHERE`.
5. Use `COPY (...) TO 'out.parquet' (FORMAT parquet)`.
6. Use `PARTITION_BY (...)`.
7. Use `types={...}`.
8. Use `dateformat='...'`.
9. It requests every projected column.
10. Partition is a layout boundary; row group is a physical unit inside a file.

## Hard — 10

1. Explain row-group skipping.
2. Explain why pruning can fail.
3. Diagnose a slow remote query.
4. Explain the small-files problem.
5. Explain `httpfs`.
6. Explain secure credential management.
7. Explain `union_by_name`.
8. Diagnose a high-cardinality partition design.
9. Explain cold vs warm benchmarking.
10. Explain remote bytes versus total dataset size.

### Answer key

Use evidence from layout, metadata, query projection/predicate, request telemetry, and runtime measurement. Do not infer physical behavior from SQL text alone.

## Advanced — 10

1. Design partitions for a 5 TB event lake.
2. Diagnose 100,000 remote objects.
3. Design secure S3 access.
4. Design schema-drift handling.
5. Explain remote Parquet range reads.
6. Explain why file layout is part of query performance.
7. Design a compaction approach.
8. Diagnose failed pruning.
9. Design local-to-production validation.
10. Decide when plain Parquet versus a managed table format is appropriate.

### Answer key

The solution must be workload-driven and evidence-based: query patterns, cardinality, file size, request count, bytes, metadata, identity, correctness, and operational requirements.

---

# 85. Final Practical Capstone

> **Build and analyze a small object-storage analytical lake queried directly by DuckDB.**

Required:

1. generate/obtain sample data;
2. convert to Parquet;
3. create Hive partitions;
4. put the data in MinIO;
5. configure DuckDB securely;
6. query without copying the full dataset locally;
7. demonstrate partition pruning;
8. demonstrate projection reduction;
9. inspect metadata;
10. demonstrate schema drift handling;
11. write gold partitioned Parquet;
12. benchmark local vs MinIO;
13. inspect request behavior;
14. compare small-file vs larger-file layout;
15. document security practices;
16. write a production recommendation.

All measurements must come from execution.

---

# 86. Mastery Checklist

- [ ] I understand direct file querying.
- [ ] I can query Parquet directly.
- [ ] I can use `read_parquet()`.
- [ ] I can query CSV directly.
- [ ] I understand CSV sniffing.
- [ ] I know when to override CSV detection.
- [ ] I understand `columns=`.
- [ ] I understand `types=`.
- [ ] I understand `dateformat=`.
- [ ] I can query JSON.
- [ ] I understand multi-file reads.
- [ ] I understand globs.
- [ ] I can use file lists.
- [ ] I understand `filename=true`.
- [ ] I understand schema drift.
- [ ] I understand `union_by_name=true`.
- [ ] I understand schema drift vs evolution.
- [ ] I understand Hive partitions.
- [ ] I can use `hive_partitioning=true`.
- [ ] I understand partition pruning.
- [ ] I understand projection pushdown.
- [ ] I understand filter pushdown.
- [ ] I understand row-group statistics.
- [ ] I can inspect `parquet_metadata()`.
- [ ] I can inspect `parquet_schema()`.
- [ ] I can write Parquet with `COPY`.
- [ ] I understand compression.
- [ ] I understand `PARTITION_BY`.
- [ ] I understand small files.
- [ ] I understand file-sizing trade-offs.
- [ ] I understand object storage.
- [ ] I understand local vs object storage.
- [ ] I understand `httpfs`.
- [ ] I can query S3-compatible storage.
- [ ] I understand MinIO.
- [ ] I understand `CREATE SECRET`.
- [ ] I understand credential chains.
- [ ] I understand secrets hygiene.
- [ ] I understand HTTP range requests.
- [ ] I understand remote metadata reads.
- [ ] I understand selective column-range reads.
- [ ] I understand remote query cost.
- [ ] I can reason about caching.
- [ ] I can benchmark local vs MinIO fairly.
- [ ] I understand Delta/Iceberg awareness.
- [ ] I completed the labs.
- [ ] I completed `lake_queries.py`.
- [ ] I completed the capstone.
- [ ] I can explain the topic aloud.

---

# 87. Final Mastery Assessment

## Part A — Fundamentals (15)

1. Define direct file querying.
2. Explain how a file acts as a relation.
3. Distinguish file and table.
4. Define glob.
5. Explain multi-file scanning.
6. Define schema drift.
7. Explain `union_by_name`.
8. Explain filename provenance.
9. Define Hive partitioning.
10. Define partition pruning.
11. Define projection pushdown.
12. Define filter pushdown.
13. Define row group.
14. Define row-group statistics.
15. Explain why object storage changes query cost.

## Part B — File Querying and Schema (15)

1. Query one Parquet file.
2. Query many Parquet files.
3. Use a glob.
4. Use a path list.
5. Read CSV.
6. Override types.
7. Set a date format.
8. Read JSON.
9. Enable Hive partitioning.
10. Add filename lineage.
11. Handle compatible schema differences.
12. Inspect Parquet schema.
13. Inspect Parquet metadata.
14. Write Parquet.
15. Write partitioned Parquet.

## Part C — Partitioning and Pushdown (15)

1. Explain partition pruning.
2. Distinguish glob expansion from pruning.
3. Explain projection pushdown.
4. Explain filter pushdown.
5. Explain row-group skipping.
6. Give two reasons pruning can be ineffective.
7. Explain partition cardinality.
8. Explain why `SELECT *` can be costly.
9. Explain file size versus partition count.
10. Explain why Parquet statistics matter.
11. Explain logical dataset size versus physical transfer.
12. Design a layout from common filters.
13. Explain under-partitioning.
14. Explain over-partitioning.
15. Distinguish partition and row group.

## Part D — Object Storage and MinIO (15)

1. Define bucket.
2. Define object key.
3. Define prefix.
4. Explain why object storage is not POSIX.
5. Explain `httpfs`.
6. Explain an S3 URI.
7. Explain endpoint.
8. Explain a secret.
9. Explain credential chain.
10. Explain temporary credentials.
11. Explain MinIO.
12. Explain path-style access.
13. Explain credential leakage.
14. Design a safe MinIO credential pattern.
15. Explain why MinIO is a local simulation, not a full cloud replica.

## Part E — Remote Performance (10)

1. Why can `SELECT *` be expensive?
2. Why can tiny objects be expensive?
3. Why does the Parquet footer matter?
4. What is a range request?
5. How can projection reduce network traffic?
6. How can partition pruning reduce network traffic?
7. How can row-group statistics reduce reads?
8. Why do cold/warm runs differ?
9. How do you measure object requests?
10. How do you separate I/O from CPU bottlenecks?

## Part F — Debugging (10)

1. Month filter touches all years.
2. Remote query transfers every column.
3. New column breaks a scan.
4. Glob includes test files.
5. Credentials expire.
6. Remote is much slower than local.
7. Row-group pruning is weak.
8. Second run is much faster.
9. Output creates millions of files.
10. Team proposes a managed table format.

## Part G — Production Architecture (10)

1. Design a 5 TB lake layout.
2. Design monthly schema evolution.
3. Design secure remote access.
4. Design request/byte monitoring.
5. Design compaction.
6. Design a local/MinIO benchmark.
7. Design a gold Parquet dataset.
8. Decide when plain Parquet is enough.
9. Identify signals for adopting a table format.
10. Create an operational checklist.

### Complete Assessment Answer Key

The correct answer to every advanced assessment item should explicitly reason about:

```text
data layout
+
file format
+
partitioning
+
metadata
+
bytes read
+
requests
+
network
+
cache
+
schema
+
credentials
+
correctness
+
operational trade-offs
```

A good answer is not a memorized syntax fragment. It explains the physical consequences of the decision.

---

# 88. Final "Teach It Back" Exercise

Without notes, explain:

1. how DuckDB queries local Parquet;
2. how it reads multiple files;
3. how schema drift is handled;
4. why filename provenance matters;
5. how Hive partitioning works;
6. how partition pruning works;
7. how projection pushdown works;
8. how filter pushdown works;
9. how row-group skipping works;
10. why small files hurt;
11. what object storage is;
12. what `httpfs` does;
13. what an HTTP range request is;
14. why the Parquet footer matters;
15. how selected column ranges can reduce transfer;
16. why network cost matters;
17. how credentials fit into architecture;
18. how to benchmark remote access;
19. how to detect poor file layout;
20. when a table format may be justified.

---

# 89. Version Awareness

DuckDB evolves quickly.

For version-sensitive functionality:

1. check `duckdb.__version__`;
2. use current stable documentation;
3. verify examples with a small test query;
4. identify changed syntax;
5. avoid deprecated APIs;
6. never invent parameters.

Pay special attention to:

- `read_parquet`;
- `read_csv`;
- `read_json`;
- `union_by_name`;
- `filename`;
- `hive_partitioning`;
- `COPY`;
- `PARTITION_BY`;
- `CREATE SECRET`;
- S3 secret providers;
- `httpfs`;
- MinIO endpoint settings;
- Delta/Iceberg extensions.

---

# 90. Technical Accuracy Requirements

Be precise about:

- file versus table;
- filesystem versus object storage;
- partition versus file;
- file versus row group;
- row group versus byte range;
- logical data size versus physical transfer;
- metadata versus data;
- schema drift versus schema evolution;
- pruning versus guaranteed elimination;
- cache state;
- credentials;
- network latency.

Avoid:

> "Remote query always downloads only required bytes."

Prefer:

> DuckDB can use Parquet layout, metadata, projection, filters, and partition information to reduce physical reads, but the amount of data transferred depends on the query and file layout.

---

# 91. Important Distinction — Partition vs Row Group

```text
Hive partition
 = directory/object-key boundary

Parquet row group
 = physical group of rows inside a file
```

Example:

```text
year=2026/month=03/
    file-a.parquet
        ├── row group 1
        └── row group 2
    file-b.parquet
        ├── row group 1
        └── row group 2
```

Partition pruning and row-group skipping are separate mechanisms.

---

# 92. Important Distinction — File Size vs Bytes Read

```text
file size
≠
bytes read by every query
```

A selective Parquet query may read only the columns, partitions, and row groups needed.

The only reliable way to claim a specific reduction is to measure it.

---

# 93. Important Distinction — Remote Query vs Full Download

Remote query:

```text
query
 ↓
metadata
 ↓
selected requests/ranges
 ↓
execution
```

Full download:

```text
download object
 ↓
store locally
 ↓
query
```

They are different architectural patterns.

---

# 94. Important Distinction — Files vs Table Formats

```text
Parquet folder
= collection of data files + layout conventions

Delta/Iceberg
= data files + managed table metadata/semantics
```

Do not use the terms interchangeably.

---

# 95. Production Decision Framework

Before adopting or changing a file layout, ask:

```text
1. What queries are common?
2. What are the dominant filters?
3. How many files exist?
4. How large are files?
5. What is partition cardinality?
6. What columns are usually needed?
7. How selective are predicates?
8. Can row groups be skipped?
9. What is the expected remote request count?
10. What bytes move?
11. Is the cache cold or warm?
12. How will schemas evolve?
13. How are credentials obtained?
14. What is the operational SLA?
15. Are plain Parquet semantics still sufficient?
```

The architecture decision must come from workload characteristics, not from a simplistic "tool X is better" rule.

---

# 96. Style Requirements

Use:

- simple language first;
- progressive complexity;
- diagrams;
- comparison tables;
- executable SQL;
- executable Python;
- realistic data-engineering examples;
- measurement methodology;
- debugging;
- production architecture;
- interview preparation.

Repeated learning loop:

```text
Concept
 ↓
example
 ↓
physical layout
 ↓
execution
 ↓
performance
 ↓
failure
 ↓
measurement
 ↓
redesign
 ↓
production lesson
```

Avoid:

- marketing language;
- fake performance values;
- unexplained jargon;
- giant code dumps;
- absolute pruning claims;
- deep cloud IAM;
- deep Delta/Iceberg internals;
- deep distributed systems.

---

# 97. Code Quality Requirements

Every example should:

- be runnable where applicable;
- include imports/setup;
- use current DuckDB APIs;
- clearly identify version-sensitive syntax;
- avoid deprecated forms;
- use placeholders for credentials;
- explain important lines;
- separate pseudocode from executable code.

Object-storage examples must never contain real credentials.

---

# 98. Benchmarking Requirements

For every benchmark:

```text
same data
+
same query
+
same layout
+
same hardware
+
same DuckDB version
+
same configuration
```

Record:

- row count;
- data size;
- object count;
- partition count;
- cache state;
- runtime;
- bytes transferred where measurable;
- request count where measurable;
- correctness.

> **Never fabricate benchmark numbers.**

---

# 99. Final Quality Control

Before considering the chapter complete, verify:

1. direct file querying is explained;
2. Parquet is covered;
3. `read_parquet` is covered;
4. CSV is covered;
5. CSV sniffing is covered;
6. `columns=` is covered;
7. `types=` is covered;
8. `dateformat=` is covered;
9. JSON is covered;
10. multi-file reads are covered;
11. globs are covered;
12. file lists are covered;
13. `filename=true` is covered;
14. schema drift is covered;
15. `union_by_name=true` is covered;
16. schema evolution distinction is covered;
17. Hive partitions are covered;
18. `hive_partitioning=true` is covered;
19. partition pruning is covered;
20. file filtering is distinguished from partition pruning;
21. projection pushdown is covered;
22. filter pushdown is covered;
23. row-group statistics are covered;
24. `parquet_metadata()` is covered;
25. `parquet_schema()` is covered;
26. `COPY` is covered;
27. compression is covered;
28. `PARTITION_BY` is covered;
29. small files are covered deeply;
30. file sizing is covered;
31. object storage is explained;
32. filesystem vs object storage is explained;
33. `httpfs` is covered;
34. S3-compatible querying is covered;
35. MinIO is covered;
36. `CREATE SECRET` is covered;
37. credential chains are covered;
38. secrets hygiene is covered;
39. HTTP range requests are covered;
40. remote footer reads are covered;
41. selective column-range reads are covered;
42. remote query cost is covered;
43. bytes-read versus total file size is covered;
44. local vs MinIO benchmark is included;
45. request investigation is included;
46. caching is covered;
47. remote small-files problem is covered;
48. Delta awareness is covered;
49. Iceberg awareness is covered;
50. plain Parquet vs table formats is covered;
51. production file layout is covered;
52. partition-key trade-offs are covered;
53. schema management is covered;
54. filename traceability is covered;
55. `lake_queries.py` is fully specified;
56. metadata lab exists;
57. schema-drift lab exists;
58. partition-pruning lab exists;
59. remote-cost lab exists;
60. security lab exists;
61. debugging scenarios exist;
62. common mistakes exist;
63. production patterns exist;
64. interview questions and answer guidance exist;
65. architecture scenarios exist;
66. explain-aloud exercises exist;
67. practice problems and answer keys exist;
68. capstone exists;
69. mastery checklist exists;
70. final assessment exists;
71. teach-back exists;
72. no benchmark numbers are fabricated;
73. version-sensitive APIs are treated carefully;
74. no credentials are exposed;
75. correctness validation is mandatory;
76. partition/file/row-group/range boundaries are explicitly distinguished;
77. no unrelated files are changed by this task.

---

## Official documentation anchors used for version-sensitive examples

Use the current DuckDB documentation for final execution verification, especially:

- Parquet querying and writing;
- Parquet metadata and schema;
- CSV auto-detection and options;
- Hive partitioning;
- `httpfs` and S3 API support;
- Secrets Manager and credential chains.

This chapter is educational material, not a guarantee that every API signature will remain unchanged across future DuckDB versions.
