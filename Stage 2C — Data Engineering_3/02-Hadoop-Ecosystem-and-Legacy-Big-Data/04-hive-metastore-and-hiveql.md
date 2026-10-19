# Hive Metastore and HiveQL

> **Roadmap location:** `Stage 2C — Data Engineering_3/02-Hadoop-Ecosystem-and-Legacy-Big-Data/04-hive-metastore-and-hiveql.md`  
> **Purpose:** Learn to understand, query, maintain, and migrate Hive-based data lakes. This is a legacy-platform and interoperability lesson, not a recommendation to build every new analytical platform on Hive.

## 1. Learning objectives

After completing this lesson, you should be able to:

- Explain Hive, HiveQL, schema-on-read, HiveServer2, and the Hive Metastore.
- Distinguish table metadata from the underlying data files and understand the metastore's relational backing database.
- Create and safely manage managed and external tables.
- Query relational and complex data with joins, aggregations, windows, `LATERAL VIEW`, and `EXPLODE`.
- Design static/dynamic partitions and bucketing; understand partition pruning.
- Select among text, SequenceFile, Avro, ORC, and Parquet and explain SerDes.
- Connect through Beeline, JDBC, and Python (`PyHive`).
- Read `EXPLAIN` plans, collect statistics, and repair missing partition metadata.
- Explain Hive execution engines, ACID/ORC, compaction, vectorization, map joins, skew, and security controls.
- Compare a Hive-style table with Iceberg and Delta Lake, and plan a controlled migration.

## 2. Prerequisites and roadmap placement

Expected prior knowledge:

- Linux shell, file permissions, and reading application logs.
- HDFS: NameNode/DataNodes, blocks, paths, replication, and `hdfs dfs` commands.
- YARN: ResourceManager, NodeManagers, containers, and resource allocation.
- MapReduce and Spark: jobs/stages, shuffle, partitions, and execution plans.
- SQL joins, aggregations, window functions, and `EXPLAIN`.
- Parquet/ORC, object storage, lakehouse table formats, and data reconciliation.

### How the lesson fits Stage 2C

| Module lesson | Dependency or connection |
|---|---|
| `01-hdfs-architecture-namenode-datanodes-and-replication.md` | Legacy Hive tables commonly reference data in HDFS. Metadata is not the same as the data files. |
| `02-yarn-resource-management.md` | YARN may allocate resources for Hive execution engines in Hadoop deployments, depending on the distribution and engine. |
| `03-mapreduce-model-and-why-spark-replaced-it.md` | Hive queries may execute with MapReduce, Tez, or Spark depending on platform support and configuration. |
| This lesson | Teaches HiveQL, the metastore, partitioned data layouts, and legacy catalog behavior. |
| `05-hbase-and-wide-column-on-hdfs.md` | Contrasts analytical Hive tables with HBase's low-latency key/row access model. |
| `06-sqoop-flume-and-oozie-legacy-tooling.md` | Hive tables often sit downstream of legacy ingestion and orchestration pipelines. |
| `07-migrating-hadoop-workloads-to-cloud-lakehouse.md` | Hive metadata and file layouts must be inventoried, validated, and mapped to the destination catalog/table format. |

The module roadmap frames this as understanding and migration. Modern engines can use Hive-compatible metadata, but compatibility is not universal: verify exact engine versions, catalog configuration, file format, and table features before sharing a table.

## 3. What Hive is

Apache Hive is a data warehouse system that provides SQL-like querying (HiveQL) over data stored in distributed storage such as HDFS and, in supported deployments, object storage. Historically it translated SQL into distributed jobs; current deployments may use Tez or other supported execution engines. Hive is useful for batch analytics, ETL, and querying data files using a defined schema.

### 3.1 Schema-on-read

With **schema-on-read**, the table definition tells the query engine how to interpret files when they are read. A directory of ORC files can contain values without the files themselves being a fully managed relational database table. The metastore stores metadata such as column names/types, storage format, SerDe, location, and partition definitions.

Schema-on-read does not mean “no schema.” A table schema still governs interpretation. If the physical file layout or field order/types do not match the table definition, queries can return incorrect values or fail.

### 3.2 Hive is not the storage engine

Keep these roles separate:

- **HiveQL:** SQL-like language for declaring tables and querying data.
- **HiveServer2 (HS2):** accepts client sessions and SQL statements over interfaces such as JDBC/ODBC.
- **Driver/compiler/optimizer:** parses SQL, resolves metadata, builds and optimizes a plan.
- **Hive Metastore (HMS):** stores table, column, partition, storage, and related metadata.
- **Metastore backing database:** relational database used by HMS to persist metadata.
- **Execution engine:** runs the plan using a supported engine, such as Tez, MapReduce, or Spark in compatible distributions.
- **Storage:** HDFS or another supported filesystem/object store holding data files.
- **SerDe and file format:** determine how records are deserialized/serialized and how bytes are physically represented.

HiveServer2 and the Metastore are separate services in common production deployments, though a development environment may package them together.

## 4. Architecture and query lifecycle

```text
Analyst / Application
  |  Beeline, JDBC/ODBC, Python client
  v
HiveServer2
  |
  v
Driver -> Parser / Semantic Analysis
  |              |
  |              v
  |        Hive Metastore <----> Relational backing DB
  |              |
  v              v
Optimizer / Physical Plan (metadata, schema, partitions, stats)
  |
  v
Execution Engine (MapReduce / Tez / supported Spark integration)
  |
  +------> YARN/resource manager where applicable
  |
  v
Storage readers/writers <----> HDFS / supported object storage
  |
  v
ORC / Parquet / Avro / Text / SequenceFile data
  |
  v
Results returned through HiveServer2 to the client
```

Conceptual lifecycle:

1. The client connects to HiveServer2 and submits HiveQL.
2. The parser validates syntax; semantic analysis resolves table/column names and types.
3. Hive obtains metadata from the Metastore, including partitions and storage definitions.
4. The optimizer uses available metadata/statistics to produce a plan.
5. The execution engine schedules tasks and reads the relevant data files.
6. Results are returned to the client, or a write statement commits output using the relevant table/storage semantics.

Exact architecture and engine options depend on the distribution and version. “Hive supports Spark” does not mean every current Hive release includes the same Spark integration; Spark can also use the Hive Metastore as a catalog without running queries through Hive's own execution engine.

## 5. The Hive Metastore and its relational backing database

The Metastore stores **descriptions of data**, not the bulk contents of every ORC or Parquet file. It commonly records:

- Databases and table names.
- Columns, types, comments, and partition keys.
- Table type (managed/external), storage location, input/output formats, and SerDe properties.
- Partition values and locations.
- Table/partition parameters, statistics, and other metadata.
- Metadata used by compatible clients to discover and interpret data.

The Hive Metastore service persists its catalog in a relational database, for example a supported MySQL or PostgreSQL deployment. A Derby database may be used for local development, but an embedded/dev setup is not an appropriate multi-user production architecture. The exact database options depend on the Hive distribution and supported versions.

### 5.1 Why persistence and availability matter

If the Metastore database or service is unavailable, table files may still exist, but clients may be unable to resolve table names or partition metadata. If someone deletes a table's metadata, the data files may remain (especially for external tables), but the table can disappear from SQL discovery. Conversely, manually creating files in a partition directory does not necessarily register that partition in the catalog.

Production concerns include backing-database backups, access control, schema upgrades, service availability, metadata migration, and compatibility testing for clients.

### 5.2 Catalog is not the same as table format

A catalog tells an engine where a table is and how to resolve it. A table format such as Iceberg or Delta adds a protocol and metadata model for tracking snapshots, files, schema evolution, and transactional changes. A Hive Metastore entry pointing at Parquet files is not automatically an Iceberg or Delta table.

## 6. Databases, tables, managed tables, and external tables

### 6.1 Create a database

```sql
CREATE DATABASE IF NOT EXISTS analytics;
USE analytics;

SHOW DATABASES;
SHOW TABLES;
DESCRIBE FORMATTED some_table;
```

`DESCRIBE FORMATTED` is Hive-specific/implementation-specific rather than portable standard SQL. It is useful for inspecting location, table type, SerDe, and storage settings.

### 6.2 Managed tables

A managed table's lifecycle is managed by Hive. In common Hive deployments, dropping a managed table removes the metadata and may delete the table's underlying data location. Exact behavior depends on Hive version, table properties, storage, and configuration; transactional tables can have additional rules.

```sql
CREATE TABLE analytics.events_managed (
    event_id BIGINT,
    event_type STRING,
    event_ts TIMESTAMP
)
STORED AS ORC;
```

Do not run `DROP TABLE` against production data until you have confirmed table type, location, retention policies, backups, and the deployed version's deletion behavior.

### 6.3 External tables

An external table describes data stored at a location whose lifecycle is generally managed outside Hive. Dropping the external table usually removes catalog metadata but preserves the data files, though `external.table.purge` and distribution-specific properties can alter behavior.

```sql
CREATE EXTERNAL TABLE analytics.events_external (
    event_id BIGINT,
    event_type STRING,
    event_ts TIMESTAMP
)
STORED AS PARQUET
LOCATION 'hdfs:///data/analytics/events';
```

This example assumes compatible Parquet files already exist at that path and that the Hive service identity can read them. On object storage, use the URI and credentials/configuration appropriate to that platform.

Inspect the actual table before dropping it:

```sql
DESCRIBE FORMATTED analytics.events_external;
```

| Concern | Managed table | External table |
|---|---|---|
| Metadata | Stored in Metastore | Stored in Metastore |
| Data files | Commonly managed as part of table lifecycle | Commonly managed externally |
| Drop behavior | May delete data as well as metadata | Usually drops metadata only, subject to properties/configuration |
| Typical use | Hive-controlled warehouse datasets | Shared/existing files, externally managed data lake paths |
| Main risk | Accidental data deletion | Multiple writers/readers changing files outside the table contract |

### 6.4 `LOCATION`, `LOAD DATA`, and `INSERT`

- `LOCATION` declares where a table or partition's data lives.
- `LOAD DATA` loads or moves/copies files into a table/partition according to Hive version and table type; it is not a universal row-by-row ingestion API. Its exact behavior has changed across Hive versions and storage configurations.
- `INSERT INTO` appends rows.
- `INSERT OVERWRITE` replaces the data for the target table/partition scope and is potentially destructive.

Example for an external table over pre-existing text files:

```sql
CREATE EXTERNAL TABLE analytics.raw_events (
    event_id BIGINT,
    event_type STRING,
    event_date STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION 'hdfs:///data/landing/events';
```

This table expects tab-separated text files with fields in the declared order. It does not create those files.

For a controlled load, create a disposable target and test with a small input first:

```sql
CREATE TABLE analytics.events_orc (
    event_id BIGINT,
    event_type STRING,
    event_date DATE
)
STORED AS ORC;

INSERT INTO TABLE analytics.events_orc
SELECT
    event_id,
    event_type,
    CAST(event_date AS DATE)
FROM analytics.raw_events
WHERE event_id IS NOT NULL;
```

This example assumes source values are castable to dates. Validate malformed values and null policy before production use. For large data, use an explicit partition design and an appropriate load/insert workflow rather than repeatedly rewriting an unpartitioned table.

## 7. HiveQL examples

The examples use a consistent conceptual schema:

- `analytics.customers(customer_id BIGINT, customer_name STRING, region STRING)`
- `analytics.orders(order_id BIGINT, customer_id BIGINT, order_ts TIMESTAMP, amount DECIMAL(12,2))`
- `analytics.events(event_id BIGINT, event_ts TIMESTAMP, event_date DATE, attributes MAP<STRING,STRING>, tags ARRAY<STRING>)`

Create tables with compatible definitions and load representative data before running these queries. HiveQL syntax and supported functions vary by version/distribution; verify against the deployed Hive release.

### 7.1 Join and aggregation

```sql
SELECT
    c.region,
    COUNT(*) AS order_count,
    SUM(o.amount) AS gross_amount
FROM analytics.orders o
JOIN analytics.customers c
  ON o.customer_id = c.customer_id
WHERE o.order_ts >= TIMESTAMP '2026-01-01 00:00:00'
GROUP BY c.region
ORDER BY gross_amount DESC;
```

The join type matters. `INNER JOIN` excludes orders with no matching customer. A `LEFT JOIN` retains every order and returns null customer columns for unmatched rows. Use `COUNT(o.order_id)` rather than `COUNT(*)` when the count should exclude null-extended rows after an outer join.

### 7.2 Window functions

```sql
SELECT
    customer_id,
    order_id,
    order_ts,
    amount,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id
        ORDER BY order_ts DESC, order_id DESC
    ) AS rn,
    SUM(amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_ts
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_spend
FROM analytics.orders;
```

A stable tie-breaker (`order_id`) makes row-number ordering deterministic when timestamps tie. Window functions may require repartitioning and sorting, which can be expensive for large partitions.

### 7.3 Complex types: arrays, maps, and structs

Hive supports complex types such as:

- `ARRAY<STRING>`: ordered collection of values.
- `MAP<STRING,STRING>`: key/value map.
- `STRUCT<city:STRING,postal_code:STRING>`: named fields grouped into one value.

Example table:

```sql
CREATE TABLE analytics.customer_profiles (
    customer_id BIGINT,
    tags ARRAY<STRING>,
    attributes MAP<STRING, STRING>,
    address STRUCT<city:STRING, postal_code:STRING>
)
STORED AS ORC;
```

Access elements with expressions such as `tags[0]`, `attributes['source']`, and `address.city`. Array indexing conventions and null behavior should be tested for the deployed Hive version; do not assume every SQL engine uses the same indexing convention.

### 7.4 `LATERAL VIEW` and `EXPLODE`

`EXPLODE` turns array elements into rows; `LATERAL VIEW` applies the table-generating function to each input row and makes the generated columns available to the query.

```sql
SELECT
    p.customer_id,
    tag
FROM analytics.customer_profiles p
LATERAL VIEW EXPLODE(p.tags) exploded_tags AS tag;
```

For a map:

```sql
SELECT
    p.customer_id,
    attribute_key,
    attribute_value
FROM analytics.customer_profiles p
LATERAL VIEW EXPLODE(p.attributes) exploded_attributes
    AS attribute_key, attribute_value;
```

Each array element or map entry can produce a separate row, increasing row count substantially. Empty/null collections may produce no rows with ordinary `LATERAL VIEW`; where supported, `LATERAL VIEW OUTER` preserves the input row with null generated values. Confirm behavior in the target release.

## 8. Partitioning and partition pruning

Partitioning stores table data under directory-like paths keyed by partition columns, with the values recorded in the Metastore. It can reduce the amount of data scanned when a query filters on partition columns.

Example layout:

```text
hdfs:///warehouse/analytics/events_partitioned/
  event_date=2026-01-01/
    part-00000.orc
  event_date=2026-01-02/
    part-00000.orc
```

A partitioned table might be declared as:

```sql
CREATE EXTERNAL TABLE analytics.events_partitioned (
    event_id BIGINT,
    event_type STRING,
    amount DECIMAL(12,2)
)
PARTITIONED BY (event_date DATE)
STORED AS ORC
LOCATION 'hdfs:///warehouse/analytics/events_partitioned';
```

The partition column is declared separately from the ordinary data columns. In a traditional Hive-style partition layout, its value is represented by the partition directory and metadata rather than repeated as a normal field in each file. When loading, do not include `event_date` in the non-partition column list unless your input/table design explicitly requires it.

### 8.1 Static partition insert

```sql
INSERT OVERWRITE TABLE analytics.events_partitioned
PARTITION (event_date = '2026-01-01')
SELECT event_id, event_type, amount
FROM analytics.events_staging
WHERE event_date = DATE '2026-01-01';
```

Static partition values are specified explicitly. The selected columns must match the non-partition columns in the target table in the expected order. The partition value is shown as a string literal because Hive partition specifications commonly use string values that the metastore/type-checking layer converts to the declared partition type; verify behavior for the installed Hive release.

### 8.2 Dynamic partition insert

Dynamic partitions derive partition values from the query result. In classic Hive deployments, dynamic partitioning settings may need to be enabled:

```sql
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;
```

Then:

```sql
INSERT OVERWRITE TABLE analytics.events_partitioned
PARTITION (event_date)
SELECT
    event_id,
    event_type,
    amount,
    event_date
FROM analytics.events_staging
WHERE event_date >= DATE '2026-01-01'
  AND event_date <  DATE '2026-02-01';
```

For dynamic partitioning, partition columns are supplied at the end of the `SELECT` list in the order declared in the `PARTITION` clause. This example assumes `events_staging` has `event_date` and all values are valid. Test the exact type and date-literal syntax supported by your Hive version.

### 8.3 Partition-pruning logic

A filter such as:

```sql
SELECT COUNT(*)
FROM analytics.events_partitioned
WHERE event_date >= DATE '2026-01-01'
  AND event_date < DATE '2026-02-01';
```

can allow Hive to select only partitions in the date range, rather than scanning every partition. Confirm pruning in `EXPLAIN` and execution metrics; do not claim a specific speedup without measurements.

Good partition keys are commonly used in filters and have a manageable number of distinct values. Over-partitioning (for example, one partition per unique event ID) can create many tiny directories/files and excessive metadata. Under-partitioning can force scans of much more data than necessary.

## 9. Bucketing

Bucketing distributes rows into a fixed number of files/buckets based on a hash of one or more columns. It differs from partitioning:

- Partitioning creates logical groups, often visible as directory paths and used for partition pruning.
- Bucketing distributes rows within the table according to a bucket hash and count.
- Bucketing is not a substitute for partition pruning and does not automatically guarantee that every engine will exploit the layout.

Example:

```sql
CREATE TABLE analytics.orders_bucketed (
    order_id BIGINT,
    customer_id BIGINT,
    order_ts TIMESTAMP,
    amount DECIMAL(12,2)
)
CLUSTERED BY (customer_id) INTO 32 BUCKETS
STORED AS ORC;
```

The number of buckets and the hash/layout must be respected when writing data. In many modern engines, enforcement and optimization behavior differs; do not assume a Spark or Trino writer will create Hive-compatible buckets unless explicitly configured and supported.

## 10. File formats and SerDes

A table's file format describes how data is physically stored; a SerDe (serializer/deserializer) describes how Hive maps between file bytes/records and table columns. Some formats have a format-specific SerDe and input/output formats; do not mix arbitrary SerDe settings with an incompatible storage format.

| Format | Type | Strengths | Trade-offs / common use |
|---|---|---|---|
| TextFile | Row-oriented text | Human-readable, simple ingestion/debugging | Larger storage, parsing CPU, weak type encoding; delimiter/escaping must be correct |
| SequenceFile | Hadoop binary key/value container | Legacy Hadoop ecosystem support; splittable variants and compression support | Primarily a legacy/intermediate format; less convenient for modern cross-engine analytics |
| Avro | Row-oriented, schema-aware serialization | Schema evolution and record-oriented interchange | Often suitable for ingestion/exchange; analytics may benefit from columnar formats |
| ORC | Columnar | Hive-oriented optimizations, compression, stripes, indexes/statistics, predicate pushdown/vectorized reads where supported | Best support depends on engine/version; not every ORC feature is used by every engine |
| Parquet | Columnar | Broad cross-engine ecosystem, column pruning and predicate pushdown | Performance depends on schema, row groups, compression, file sizes, and engine support |

### 10.1 ORC table example

```sql
CREATE EXTERNAL TABLE analytics.events_orc (
    event_id BIGINT,
    event_type STRING,
    amount DECIMAL(12,2)
)
STORED AS ORC
LOCATION 'hdfs:///data/analytics/events_orc';
```

The directory must contain valid ORC files matching the expected schema. `CREATE EXTERNAL TABLE` does not convert text or Parquet bytes into ORC. To convert, read the source table and write into a new ORC table/location using `INSERT` or an appropriate ETL process, then validate the output.

### 10.2 Parquet and Avro examples

```sql
CREATE EXTERNAL TABLE analytics.events_parquet (
    event_id BIGINT,
    event_type STRING,
    amount DECIMAL(12,2)
)
STORED AS PARQUET
LOCATION 'hdfs:///data/analytics/events_parquet';
```

The location must already contain Parquet files with a compatible schema. Query a small sample to validate the schema and physical files:

```sql
SELECT event_id, event_type, amount
FROM analytics.events_parquet
LIMIT 10;
```

A successful `CREATE EXTERNAL TABLE` only registers metadata; it does not convert existing files. For Avro, SerDe configuration is version/distribution-sensitive. A common Hive pattern uses the Avro SerDe and schema URL or schema literal properties, for example:

```sql
CREATE EXTERNAL TABLE analytics.events_avro
STORED AS AVRO
LOCATION 'hdfs:///data/analytics/events_avro';
```

The abbreviated Avro definition is valid only where the installed Hive distribution supplies the relevant Avro support and can infer/resolve the schema from the files or configured properties. For a production table, specify the schema configuration required by that release and verify it with a small representative file.

### 10.3 SerDe and schema mismatch

A SerDe mismatch can cause parse errors, nulls, shifted columns, or incorrect values. Check:

- Delimiter, quote, escape, and null representations for text.
- Physical file format and schema for ORC/Parquet/Avro.
- Column ordering and type compatibility.
- Compression codec support.
- Whether all writers used compatible schema evolution rules.
- Whether a shared engine supports the format and SerDe in use.

## 11. Execution engines: MapReduce, Tez, and Spark

HiveQL is a query language; the execution engine runs the physical plan.

- **MapReduce:** classic Hadoop batch engine, robust but often expensive for multi-stage pipelines because job boundaries and materialization can add overhead.
- **Tez:** DAG-based execution engine designed to execute connected processing stages with less overhead than a chain of separate MapReduce jobs.
- **Spark:** a separate distributed processing engine with DAG scheduling and RDD/DataFrame/SQL APIs. Some deployments integrate Spark with Hive metadata; not all Hive releases provide Spark as a directly selectable Hive execution engine.

The roadmap's progression `MapReduce → Tez → Spark` describes a historical and conceptual evolution, not a universal guaranteed runtime ordering. Actual availability and performance depend on the distribution, Hive version, workload, file layout, statistics, cluster resources, and configuration.

Do not assume that changing `hive.execution.engine` to `spark` works in every Hive distribution. Check the installed engine options and vendor support. Spark reading a Hive Metastore catalog is not the same as HiveServer2 executing a query through Spark.

## 12. Beeline, HiveServer2, JDBC, and Python

### 12.1 Beeline

Beeline is a command-line JDBC client for HiveServer2. You need a running HiveServer2 endpoint, compatible client libraries, network access, and appropriate authentication.

```bash
beeline -u 'jdbc:hive2://hive-server.example.com:10000/default' \
  -n analyst
```

This is a template. Replace the host/database and supply authentication/TLS options required by your environment. Avoid putting passwords directly into shell history. Kerberos deployments often use a principal and service discovery settings; use the cluster's documented connection string.

After connecting:

```sql
SHOW DATABASES;
USE analytics;
SHOW TABLES;
DESCRIBE FORMATTED events_partitioned;
```

### 12.2 JDBC

Applications can connect to HiveServer2 using the Hive JDBC driver. JDBC is the protocol/client layer; it does not mean the application connects directly to the Metastore's backing database. Directly querying or modifying Metastore database tables is not a supported substitute for the Hive APIs.

### 12.3 Python with PyHive

Install a version compatible with your Python and HiveServer2 setup:

```bash
python -m pip install PyHive thrift thrift-sasl
```

Authentication dependencies vary by mechanism and operating system. Some environments require SASL/GSSAPI packages or vendor-provided client libraries. Test connectivity with the cluster administrator's supported configuration.

Example for an environment where username/password authentication is enabled:

```python
from pyhive import hive

connection = hive.Connection(
    host="hive-server.example.com",
    port=10000,
    username="analyst",
    database="analytics",
    auth="NONE",  # Example only; use the actual configured auth mechanism.
)

cursor = connection.cursor()
cursor.execute("""
    SELECT event_type, COUNT(*) AS n
    FROM events_orc
    GROUP BY event_type
    ORDER BY n DESC
""")

for row in cursor.fetchall():
    print(row)

cursor.close()
connection.close()
```

`auth="NONE"` is appropriate only for an environment configured to allow that authentication mode. Do not use it as a production security recommendation. Kerberos or LDAP/password modes require different connection parameters and dependencies. Use TLS and secret management where required.

## 13. EXPLAIN and query-plan reading

`EXPLAIN` shows the planned operations; exact output depends on Hive version and execution engine.

```sql
EXPLAIN
SELECT event_type, COUNT(*)
FROM analytics.events_partitioned
WHERE event_date >= DATE '2026-01-01'
  AND event_date < DATE '2026-02-01'
GROUP BY event_type;
```

Where supported, extended or cost-based explain modes can show additional information:

```sql
EXPLAIN EXTENDED
SELECT event_type, COUNT(*)
FROM analytics.events_partitioned
WHERE event_date = DATE '2026-01-01'
GROUP BY event_type;
```

Do not assume every Hive release supports every `EXPLAIN` option identically. Read the plan produced by the actual deployment.

Look for:

- **Table/partition scan:** is the intended table being read?
- **Partition pruning:** are only relevant partition values selected?
- **Predicate pushdown:** can filters be pushed to the storage reader?
- **Projection/column pruning:** are only required columns read?
- **Join strategy:** shuffle/reduce-side join versus map/broadcast join, where shown.
- **Aggregation and sort:** where data is grouped, sorted, or redistributed.
- **Estimated rows/bytes and statistics:** are estimates present and plausible?
- **Execution stages/operators:** do the stages match the expected query shape?

A plan shows intended execution, not measured elapsed time. Confirm actual scan bytes, input records, task durations, and spill/shuffle metrics in the relevant engine UI/logs when available.

## 14. Statistics, cost-based optimization, and metadata repair

### 14.1 Statistics

The optimizer may use table/column statistics to estimate row counts and choose join order or join strategy. Stale/missing statistics can lead to poor plans. Collect statistics after major loads when supported and appropriate:

```sql
ANALYZE TABLE analytics.events_partitioned COMPUTE STATISTICS;
```

Column statistics syntax and supported types vary by Hive release. A common form is:

```sql
ANALYZE TABLE analytics.events_partitioned
COMPUTE STATISTICS FOR COLUMNS event_id, event_type, amount;
```

Check the exact syntax in your Hive version. Statistics collection is itself a job and can be expensive on very large datasets; schedule it as part of ingestion/maintenance rather than running it blindly after every tiny write.

### 14.2 `MSCK REPAIR TABLE`

In classic Hive-style external partitioned tables, manually creating a directory such as `event_date=2026-01-15/` does not necessarily register it in the Metastore. The metadata repair operation can discover compatible partition directories:

```sql
MSCK REPAIR TABLE analytics.events_partitioned;
```

In supported Hive versions, repair may support synchronization modes such as `ADD`, `DROP`, or `SYNC`; availability and behavior vary by release/distribution. Use the plain command only after confirming the target's behavior.

**Important:** `MSCK REPAIR TABLE` repairs partition metadata; it does not create data files, validate their contents, convert formats, or repair malformed data. If a directory contains no files, the partition may still be registered but have no useful rows. Verify that directory names match the partition schema and expected encoding.

If the metastore already has partitions but external files were moved or deleted, a repair command may not be the right fix. Inspect table/partition locations and data files first.

## 15. Hive ACID tables and compaction

Hive ACID provides transactional behavior for supported managed tables and configurations, historically using ORC and a Hive transaction manager. ACID is not automatically enabled by creating any ORC table; it requires compatible Hive versions, table properties, transaction settings, and supported write paths.

A simplified transactional-table example for compatible Hive deployments:

```sql
CREATE TABLE analytics.customer_status_acid (
    customer_id BIGINT,
    status STRING,
    updated_at TIMESTAMP
)
CLUSTERED BY (customer_id) INTO 8 BUCKETS
STORED AS ORC
TBLPROPERTIES (
    'transactional'='true'
);
```

This is a conceptual DDL pattern. Exact ACID requirements—including bucketing rules, transactional properties, managed-table requirements, table properties, and supported insert/update/delete operations—differ across Hive versions and vendors. Verify prerequisites before using it; do not copy it into production without checking the release-specific ACID documentation.

### 15.1 Why compaction exists

Transactional writes can create delta files that represent inserts, updates, and deletes. Repeated small writes can create many delta directories/files, increasing file-open overhead and read/merge work. Compaction combines delta files and/or base data into a more efficient layout:

- **Minor compaction:** merges delta files.
- **Major compaction:** merges base and delta files into a newer base representation.

The compactor and cleaner are background services in supported Hive ACID deployments. Compaction may consume substantial I/O and compute. Monitor queue depth, failures, delta counts, write rates, and cleanup rather than triggering compaction without a plan.

## 16. Performance tuning

### 16.1 Vectorization

Vectorized execution processes batches of column values rather than interpreting every row independently, reducing per-row overhead for supported operators and formats. It depends on engine/version, data types, query operators, and configuration. Confirm whether vectorization is enabled and actually used; do not assume every query is vectorized.

### 16.2 Map joins / broadcast joins

A map join can load a sufficiently small table into mapper-side memory so the large table does not need a full join-key shuffle. It can be highly effective for a small dimension table and large fact table, but risks memory pressure if the “small” side is larger than estimated or duplicated in each task. Confirm the physical plan and relevant configuration/hints for the installed version.

### 16.3 Skew handling

A skewed key can send a disproportionate amount of data to one reducer or task. Symptoms include a few very long-running tasks while most finish quickly. Check key distributions, per-task input sizes, and plan metrics. Possible mitigations include filtering, salting keys for appropriate aggregations, skew-aware join strategies, or using engine-specific skew handling. Salting is not a generic fix for every join and must preserve semantics.

### 16.4 Partition and file design

- Partition on frequently filtered, moderate-cardinality columns, often dates.
- Avoid one partition per high-cardinality entity.
- Avoid creating thousands of tiny files per partition.
- Prefer columnar formats for analytical scans where compatible.
- Filter early and project only needed columns.
- Use statistics to help join/aggregation planning.
- Inspect whether partition pruning and predicate pushdown occur.
- Tune parallelism and file sizes based on measured workload and cluster limits.

### 16.5 Troubleshooting table

| Symptom | Possible causes | First investigation |
|---|---|---|
| Table not found | Wrong database, missing metastore entry, wrong catalog | `USE`, `SHOW TABLES`, `DESCRIBE`, connection target |
| Table exists but returns no rows | Wrong location, empty files, wrong SerDe/schema, partition not registered | `DESCRIBE FORMATTED`, filesystem listing, sample file inspection |
| New partition directory is invisible | Directory not registered in Metastore | Verify path/partition naming, then appropriate `MSCK REPAIR TABLE` workflow |
| Query scans too much data | Missing partition filter, wrong partition metadata, no pruning | `EXPLAIN`, actual scan metrics, table/partition metadata |
| Join unexpectedly slow | Missing/stale stats, large shuffle, skew, wrong join strategy | Explain plan, statistics, task skew, shuffle/spill metrics |
| Many small files | Excessive tiny writes or partitions | File count/size distribution; plan controlled compaction/rewrite |
| ACID reads degrade | Many deltas or compaction backlog | Transaction/compaction logs, delta count, compactor health |
| Wrong column values | SerDe mismatch, schema evolution, column-order issue | Compare table schema to actual files and writer schema |

## 17. Shared catalogs: Hive Metastore, Glue, and Unity Catalog

### 17.1 Hive Metastore as a shared catalog

Spark, Trino, Presto, and other systems can be configured to use a Hive Metastore-compatible catalog in supported versions. That can allow multiple engines to resolve database/table metadata and access the same files.

Compatibility must be tested. Different engines may vary in:

- Supported SerDes and storage formats.
- Hive table properties and partition discovery.
- Bucket semantics.
- Transactional Hive ACID support.
- SQL syntax and function behavior.
- Write/commit protocols, schema evolution, and concurrent writes.
- Authorization and identity propagation.

A table being visible in two engines does not prove that both engines safely support concurrent writes or every table feature.

### 17.2 AWS Glue Data Catalog

AWS Glue Data Catalog is a managed metadata catalog that can serve as a Hive Metastore-compatible catalog for supported integrations. It is not simply a managed relational database endpoint that you operate like a self-hosted HMS database. Check the service-specific integration, permissions, and feature compatibility for each engine.

### 17.3 Unity Catalog

Unity Catalog is a broader governance and catalog layer in the Databricks lakehouse ecosystem, with access control, discovery, lineage/governance capabilities, and support for supported table/storage patterns. It is not merely another name for the Hive Metastore, and not every Hive table or external catalog feature maps one-to-one into Unity Catalog. Migration requires assessing table format, external locations, permissions, ownership, lineage, and engine-specific capabilities.

## 18. Hive tables versus Iceberg and Delta Lake

A traditional Hive external table commonly points to files at a location and uses Metastore metadata to describe columns, partitions, and storage. That can work well for append-oriented data lakes, but the table abstraction alone does not necessarily provide snapshot isolation, atomic multi-file commits, or robust concurrent update semantics.

Iceberg and Delta Lake are table formats with transaction/log/metadata protocols designed to manage sets of data files and table changes. They are not merely alternative file extensions.

| Capability | Traditional Hive-style table | Apache Iceberg | Delta Lake |
|---|---|---|---|
| Data files | Commonly text, ORC, Parquet, Avro, etc. | Often Parquet, with format metadata/snapshots | Commonly Parquet, with transaction log |
| Catalog | Hive Metastore or compatible catalog | Catalog plus Iceberg metadata/snapshots | Catalog plus Delta transaction log |
| Snapshot/history model | Not inherently provided by a basic external table | Snapshot-based table metadata | Transaction log and supported history features |
| Schema/partition evolution | Depends on Hive table metadata and engine support | Table-format-managed evolution features | Table-format-managed evolution features |
| Concurrent writes/transactions | Depends on table type/engine; basic external table is limited | Depends on catalog/engine support and isolation model | Depends on engine/runtime and protocol features |
| Cross-engine access | Broad for basic Hive tables, but SerDe/features vary | Depends on engine/catalog support for Iceberg version/features | Depends on engine/runtime support for Delta protocol features |

### 18.1 Migration principles

- Do not assume an existing Hive directory can be declared Iceberg/Delta by changing the file format property.
- Choose a supported writer and catalog integration for the target table format.
- A safer general migration pattern is to create a new Iceberg/Delta table, write/copy the validated data, compare row counts and business aggregates, validate nulls/duplicates and partition coverage, then cut consumers over.
- Some platforms provide specific in-place migration procedures for eligible tables. Use those only when the source layout and versions meet the documented requirements.
- Plan rollback, permissions, downstream dependencies, schema evolution, retention, compaction/maintenance, and concurrent-writer behavior.

### 18.2 Creating an Iceberg target through Spark (illustrative)

This is a template for an environment where Spark is configured with a compatible Iceberg runtime and catalog. Catalog configuration is deployment-specific and must be set before submission.

```sql
-- Run through Spark SQL only when the catalog and Iceberg runtime are configured.
CREATE TABLE lakehouse.analytics_events
USING iceberg
AS
SELECT event_id, event_type, event_date
FROM hive_metastore.analytics.events_source;
```

This is a **copy/CTAS migration**, not an in-place conversion of the original Hive table. Verify that the source catalog name is correct for the Spark deployment and that the Iceberg catalog is configured. A Delta target uses its own supported provider/runtime syntax; do not assume Iceberg SQL syntax is interchangeable with Delta.

## 19. Security and authorization awareness

Hive security is a layered concern:

- **Authentication:** identifies the client/service (for example Kerberos or supported enterprise identity).
- **Authorization:** decides which identities may access databases, tables, columns, or operations.
- **Transport security:** TLS protects network connections where configured.
- **Storage permissions:** HDFS/object-store ACLs and service identities control file access.
- **Audit/governance:** logs and policies support investigation and compliance.

Apache Ranger is commonly used in Hadoop ecosystems for centralized authorization policies and auditing across supported services. Its exact integration and enforcement points depend on the distribution. Do not assume a SQL grant automatically restricts direct access to underlying files; data lake security must account for both engine/catalog access and storage-level permissions.

## 20. Hands-on exercises — `experiments/04_hive/`

These exercises are designed to be reproducible, but require a compatible Hive environment and, for some labs, compatible Spark/Trino/Iceberg integrations. Record the versions and configuration before beginning. Do not treat example commands as proof of successful execution.

### Exercise 1 — External ORC table with dynamic partitions for one month

**Goal:** Load a month of sample events into an external ORC table partitioned by date.

1. Create a staging table containing `event_id`, `event_type`, `amount`, and `event_date`.
2. Prepare sample data covering a full month, for example January 2026, with valid date values.
3. Create an external partitioned ORC table at a new, dedicated location:

```sql
CREATE EXTERNAL TABLE analytics.lab_events_by_date (
    event_id BIGINT,
    event_type STRING,
    amount DECIMAL(12,2)
)
PARTITIONED BY (event_date DATE)
STORED AS ORC
LOCATION 'hdfs:///labs/04_hive/events_by_date';
```

4. Enable dynamic partitioning if required by the installed Hive version:

```sql
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;
```

5. Insert the month of data:

```sql
INSERT OVERWRITE TABLE analytics.lab_events_by_date
PARTITION (event_date)
SELECT event_id, event_type, amount, event_date
FROM analytics.lab_events_staging
WHERE event_date >= DATE '2026-01-01'
  AND event_date < DATE '2026-02-01';
```

6. Verify the result:

```sql
SHOW PARTITIONS analytics.lab_events_by_date;
SELECT event_date, COUNT(*) AS rows_per_day, SUM(amount) AS total_amount
FROM analytics.lab_events_by_date
GROUP BY event_date
ORDER BY event_date;
```

**Validation:** compare source and target row counts, date coverage, daily counts, sums, nulls, and duplicate IDs. Because this is an external table, understand the configured location and the deployed version's `INSERT OVERWRITE` behavior before rerunning. Use a disposable lab path.

### Exercise 2 — Partitioned versus unpartitioned query

1. Create an unpartitioned ORC table with the same rows and a partitioned table containing the same logical data.
2. Run the same date-range query against each.
3. Capture `EXPLAIN` output.
4. Capture available execution metrics: input bytes, rows read, task count, elapsed time, and relevant engine counters.
5. Explain whether partition pruning appears in the plan and whether measured scans differ.

Keep input data, file format, compression, cluster resources, query semantics, and cache conditions comparable. Do not claim a speedup unless measured. `EXPLAIN` alone is evidence of the planned scan, not proof of elapsed-time improvement.

### Exercise 3 — Manually add partition directories and repair metadata

1. Identify the external table's exact location and partition column type.
2. In the disposable lab location, create a correctly named directory such as `event_date=2026-01-15/`.
3. Place valid ORC files matching the table schema in that directory. Creating a directory alone does not create valid rows.
4. Check whether the partition is registered:

```sql
SHOW PARTITIONS analytics.lab_events_by_date;
```

5. Use the repair operation supported by your Hive version:

```sql
MSCK REPAIR TABLE analytics.lab_events_by_date;
```

6. Verify the partition appears and query the rows.

**Validation:** confirm both metadata and actual files. If the directory is empty or contains incompatible bytes, repair may register the partition but will not manufacture or correct the data. Some versions support repair modes; use only syntax documented for your release.

### Exercise 4 — Share the Metastore with Spark and Trino

1. Record Hive, Spark, Trino/Presto, and Metastore versions.
2. Configure Spark to use the intended Hive-compatible catalog and required Hive client jars/configuration.
3. Configure Trino's Hive connector to use the same compatible Metastore and appropriate filesystem credentials.
4. Query the same external Parquet table from Hive, Spark, and Trino.
5. Compare schemas, row counts, null handling, partition visibility, and representative results.
6. Do not test concurrent writes until each engine's write and commit behavior is explicitly supported.

**Validation:** successful table discovery alone is insufficient. Verify that each engine reads the intended files and interprets types/partitions consistently. ACID, bucketed, custom-SerDe, and modern table-format support may differ.

### Exercise 5 — Migrate a suitable Hive table to Iceberg

1. Select a non-transactional external Hive table with a known schema and stable source snapshot.
2. Record source location, partitioning, row count, nulls, duplicate keys, and key aggregates.
3. Configure a supported Spark/Iceberg runtime and catalog.
4. Create a new Iceberg table using a documented CTAS/copy process (see Section 18.2), rather than changing the source table's format property.
5. Validate the target using counts, aggregates, partition/date coverage, and representative rows.
6. Test schema evolution and snapshot/time-travel behavior supported by your installed Iceberg version.
7. Document catalog configuration, access control, storage permissions, downstream dependencies, rollback path, and cutover criteria.

**Validation:** write down what the new table format provides in the selected platform, what it does not provide automatically, and which clients can read/write the table. Do not drop or repoint the source table until reconciliation and rollback are approved.

## 21. Production use cases

- **Batch warehouse ETL:** aggregate transactions and publish daily/monthly reporting tables.
- **Data lake query layer:** define schemas over Parquet/ORC files without loading them into a traditional row-store database.
- **Legacy Hadoop analytics:** maintain existing HiveQL workloads and understand their execution plans.
- **Shared metadata:** expose compatible Hive table definitions to Spark/Trino and other supported engines.
- **Migration staging:** inventory Hive schemas/locations, validate converted files and query semantics, then migrate eligible datasets to Iceberg/Delta or a managed analytics service.

## 22. Common mistakes

- Confusing Metastore metadata with the underlying data files.
- Assuming `CREATE EXTERNAL TABLE` creates or converts the data files.
- Dropping a managed table without checking whether its data will be deleted.
- Assuming an external table is safe from every destructive operation; `INSERT OVERWRITE`, filesystem deletion, and external purge settings can still destroy data.
- Treating HiveQL as identical to standard SQL or assuming syntax works in Spark/Trino.
- Forgetting partition columns are declared separately from ordinary columns in Hive-style partitioned tables.
- Assuming `MSCK REPAIR TABLE` creates files or repairs malformed data.
- Assuming a directory named `event_date=...` is sufficient if it has no valid data or the wrong schema.
- Using high-cardinality partition keys and producing excessive small files.
- Assuming bucketing is automatically respected by every writer and query engine.
- Treating ORC/Parquet as interchangeable with text or assuming a SerDe can decode arbitrary bytes.
- Assuming every Hive release supports Tez, Spark integration, ACID, or every `EXPLAIN` mode.
- Collecting statistics but never checking whether they are current or used by the optimizer.
- Claiming partition pruning improved runtime without inspecting the plan and metrics.
- Assuming a shared Metastore guarantees safe cross-engine writes.
- Assuming Unity Catalog is simply a Hive Metastore replacement with identical semantics.
- Changing a Hive table's format property and assuming the data became Iceberg or Delta.

## 23. Interview questions and answers

**1. What does the Hive Metastore store?**  
Catalog metadata such as database/table definitions, columns, partition values/locations, storage properties, and statistics. The bulk data remains in files in HDFS or another storage system.

**2. Why does the Metastore use a relational database?**  
To persist catalog metadata in a durable, queryable backend. Production deployments typically use a supported external relational database rather than an embedded development database.

**3. What is schema-on-read?**  
The table definition is applied when data files are read, rather than requiring all data to be loaded into a traditional relational table first.

**4. What is the difference between managed and external tables?**  
A managed table's lifecycle is more directly controlled by Hive and dropping it may remove data. An external table generally leaves underlying files under external lifecycle control, but properties and version-specific behavior must be checked.

**5. What does `LOCATION` do?**  
It associates a table or partition with a filesystem/object-store path; it does not convert or create data files.

**6. What is partition pruning?**  
The engine excludes irrelevant partitions based on partition-column predicates, potentially reducing data scanned.

**7. What does `MSCK REPAIR TABLE` do?**  
In supported Hive deployments, it discovers compatible partition directories and synchronizes partition metadata according to the command/version. It does not create or repair data files.

**8. How do partitioning and bucketing differ?**  
Partitioning divides a table by column values, often into directories. Bucketing hashes rows into a fixed number of buckets within a table or partition.

**9. Why collect statistics?**  
Statistics help the optimizer estimate data size/cardinality and choose plans, including join strategies. Stale or missing statistics can lead to poor plans.

**10. What is the role of a SerDe?**  
It defines how Hive translates between stored representation and table rows/columns. It must match the file format and schema.

**11. Why does Hive ACID need compaction?**  
Transactional writes can accumulate delta files. Compaction merges these into more efficient layouts and helps control read and file-management overhead.

**12. Is Hive Metastore the same as Iceberg or Delta Lake?**  
No. The Metastore is a catalog service/metadata store; Iceberg and Delta are table formats with transaction and table-metadata protocols. A catalog can help locate a table format but does not make a plain Hive table transactional.

**13. Can Spark, Trino, and Hive always query and write the same table safely?**  
No. Catalog visibility, read support, file formats, ACID behavior, schema evolution, and concurrent-write semantics vary by engine/version and configuration.

**14. What should you inspect when a partitioned query scans too much data?**  
The `EXPLAIN` plan, partition metadata, partition predicates, actual scan metrics, and statistics. Check whether the filter uses the partition column in a form the optimizer can prune.

## 24. Final self-assessment checklist

Mark an item only when you can explain it or demonstrate it on a compatible lab environment.

- [ ] I can diagram the HiveQL-to-result lifecycle and explain HiveServer2, Metastore, backing database, execution engine, and storage roles.
- [ ] I can explain schema-on-read and distinguish catalog metadata from physical data files.
- [ ] I can create and inspect managed/external tables and explain destructive-operation risks.
- [ ] I can use `LOAD DATA`, `INSERT INTO`, and `INSERT OVERWRITE` with a clear understanding of the target path and data effect.
- [ ] I can query joins, aggregations, window functions, arrays, maps, structs, `LATERAL VIEW`, and `EXPLODE`.
- [ ] I can create static and dynamic partitions and explain partition pruning.
- [ ] I can explain bucketing and its engine compatibility constraints.
- [ ] I can compare TextFile, SequenceFile, Avro, ORC, and Parquet, including SerDe/schema requirements.
- [ ] I can connect using Beeline and understand how JDBC/PyHive authenticate to HiveServer2.
- [ ] I can read `EXPLAIN`, collect statistics, and check whether partition pruning is used.
- [ ] I understand `MSCK REPAIR TABLE` repairs metadata rather than creating or fixing data files.
- [ ] I can explain Hive ACID prerequisites, transactional ORC, delta files, and compaction.
- [ ] I can identify likely causes of skew, excessive small files, missing statistics, and poor join plans.
- [ ] I understand the limitations of shared Hive Metastore catalogs across Spark, Trino/Presto, Glue, and Unity Catalog.
- [ ] I can describe a safe Hive-to-Iceberg/Delta migration and validate the target before cutover.
- [ ] I can explain the role of authentication, authorization, storage permissions, and Ranger.

## 25. Further reading

Version-match documentation to the Hive/Spark/Trino distribution actually deployed. Some links point to rolling documentation and may describe features unavailable in older clusters.

- Apache Hive documentation: https://hive.apache.org/
- Apache Hive Language Manual: https://cwiki.apache.org/confluence/display/Hive/LanguageManual
- Apache Hive Configuration: https://cwiki.apache.org/confluence/display/Hive/Configuration+Properties
- Apache Iceberg documentation: https://iceberg.apache.org/docs/latest/
- Delta Lake documentation: https://docs.delta.io/
- Trino Hive connector: https://trino.io/docs/current/connector/hive.html
- AWS Glue Data Catalog documentation: https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html
- Databricks Unity Catalog documentation: https://docs.databricks.com/en/data-governance/unity-catalog/index.html

---

**Completion criterion:** You can create and query a Hive table over existing files, explain how metadata is stored, demonstrate partition pruning and metadata repair, and plan a validated migration to a modern table format without confusing catalog metadata with data files.
