# Trino and Presto: Federated Queries

> **Module:** Stage 2C — Data Engineering_3 / 07-Real-Time-OLAP-and-Query-Engines  
> **Lesson:** `03-trino-and-presto-federated-queries.md`  
> **Level:** Beginner → Advanced  
> **Primary implementation target:** Trino. PrestoDB and Amazon Athena are distinguished where behavior or terminology differs.

## How to use this lesson

Read Sections 1–9 in order, then complete the lab in Section 11. Use the checkpoints to test understanding rather than memorizing definitions. SQL and configuration examples are version-sensitive: pin a Trino release and match connector properties to that release before using them in a shared environment. Text labelled **illustrative** describes a possible plan or outcome, not a measured result.

## 1. Learning objectives and prerequisites

By the end, you should be able to:

- Explain what Trino and PrestoDB do, how they are related, and how they differ from a database or warehouse.
- Trace a query through a coordinator, workers, stages, tasks, splits, exchanges, and connectors.
- Configure catalogs and explain the catalog → schema → table namespace.
- Query Parquet/ORC lake data and relational sources through separate connectors, including cross-catalog joins.
- Read `EXPLAIN` and `EXPLAIN ANALYZE`, recognize pushdown, partition pruning, dynamic filtering, and join distribution, and explain what evidence supports each claim.
- Use statistics and `ANALYZE` to help the cost-based optimizer make better choices.
- Understand connector-dependent CTAS, `INSERT`, Iceberg `MERGE`, and maintenance operations.
- Recognize production risks involving memory, spilling, resource groups, fault-tolerant execution, worker scaling, authentication, authorization, caching, and small files.
- Run the `experiments/03_trino/` lab and compare Trino with DuckDB without fabricating performance results.

### Prerequisites

You should know basic SQL (`SELECT`, `WHERE`, `JOIN`, `GROUP BY`), relational tables, object storage, Parquet at a conceptual level, and basic shell/Docker use. Familiarity with PostgreSQL and Python is helpful. If these are new, focus first on the guided SQL and treat the advanced operations as a reference.

## 2. Trino and Presto fundamentals

### 2.1 What are they?

**Definition.** Trino is a distributed SQL query engine for interactive analytics and batch processing across data sources. PrestoDB is a separate open-source project that continues the original Presto codebase. Both use SQL to query external systems through connectors.

**Origin and fork.** Presto originated at Facebook to query data across large-scale data stores. Around 2019–2020, the community and governance split resulted in two projects: the Presto project (often called PrestoDB) and the Trino project, which was originally named PrestoSQL before being renamed Trino. They share ancestry and concepts but have diverged in releases, APIs, connectors, configuration, and capabilities. Do not assume a Trino configuration property or SQL feature works in PrestoDB, or vice versa.

**Purpose.** A conventional database typically owns and manages its primary storage format. Trino generally does not own a central analytical copy of the datasets it queries. It coordinates distributed execution while connectors read or write data in systems such as Iceberg tables on object storage, PostgreSQL, MySQL, Kafka, or a cloud warehouse.

**Internal behavior.** The coordinator parses SQL, analyzes names and types, plans work, schedules tasks, and tracks execution. Workers execute plan fragments and interact with connectors. Data may be read remotely, processed on workers, exchanged across the cluster, and returned to the client.

**When to use it.** Use Trino when analysts or jobs need SQL over data already distributed across a lakehouse, databases, and supported external systems; when data virtualization avoids unnecessary copies; or when one query must combine multiple systems.

**When not to use it.** Trino is not a universal replacement for a transactional database, a durable serving store, a streaming processor, or a warehouse with tightly integrated storage and workload management. Avoid unbounded cross-source joins when one source can filter or aggregate the data more efficiently. For a strict sub-10-ms user-facing lookup or a high-QPS serving workload, a purpose-built serving system is usually a better fit.

**Trade-offs.** Federation reduces data duplication and can simplify access, but latency, availability, permissions, and performance depend on every participating source and network path. Queries may consume source-system capacity even when the SQL runs through Trino.

### 2.2 Keep the names distinct

| Name | What it means | Practical caution |
| --- | --- | --- |
| **Trino** | Independent distributed SQL engine descended from PrestoSQL | Use Trino docs and connector compatibility for Trino releases. |
| **PrestoDB** | Separate project continuing the original Presto project | Validate syntax and properties against PrestoDB documentation for the deployed release. |
| **Amazon Athena** | AWS-managed query service with Presto/Trino lineage and service-specific behavior | Athena is not simply a self-managed Trino cluster. Engine versions, SQL, connectors, permissions, and operational controls differ. |
| **Starburst** | Commercial distribution and services built around Trino | Some capabilities and integrations are distribution-specific. |

### 2.3 Federated SQL: query data where it lives

**Definition.** A federated query reads from more than one catalog/source in a single SQL statement. For example, a fact table in Iceberg can be joined to a customer dimension in PostgreSQL.

**Why.** It can avoid building a duplicate integration table for every analytical question and gives a common SQL layer over heterogeneous data.

**How.** Trino resolves each table through its catalog and connector. A connector can translate supported filters, projections, aggregations, or joins to the source. If work cannot be pushed down, Trino reads rows into its own execution pipeline and processes them on workers.

**Limitations.** A single SQL statement does not make multiple systems one transaction. Cross-source consistency, type mappings, pushdown, writes, and fault tolerance vary. A slow or unavailable source can bottleneck the whole query.

**Engineering rule.** Before joining two large systems, estimate rows and bytes read from each source, apply selective filters as early as semantics allow, and confirm the plan and runtime metrics.

## 3. Distributed execution architecture

### 3.1 Coordinator and workers

**Coordinator** responsibilities include accepting client requests, parsing and analyzing SQL, resolving catalogs/schemas/tables, optimizing the logical plan, splitting work into distributed stages, scheduling tasks, tracking failures and statistics, and returning results. It is a control-plane bottleneck if overloaded, but most scan and operator data processing happens on workers.

**Workers** execute tasks. They read splits through connectors, run operators such as filters, projections, aggregations and joins, and exchange intermediate data with other tasks. Workers need network access and credentials/configuration to reach their data sources.

```text
Client (CLI / JDBC / Python)
          |
          v
    Coordinator
  parse → analyze → optimize → schedule
          |
      stage graph
       /       \
      v         v
 Worker A     Worker B       ... more workers
 split reads  split reads
 filters      projections
       \       /
        exchange (shuffle / broadcast)
                |
          join / aggregate
                |
         result to client
```

This is a conceptual diagram. A real query can have several stages, pipelines, and exchange boundaries; exact shape depends on SQL, connector capabilities, statistics, and session/system settings.

### 3.2 Stages, tasks, splits, and exchanges

- **Stage:** a fragment of a distributed plan separated from other fragments by an exchange boundary or another scheduling boundary.
- **Task:** a scheduled unit of a stage running on a worker. A stage normally has multiple tasks.
- **Split:** a unit of source work assigned to a task, such as a file range, a file, or a connector-specific chunk of source data. Split granularity is connector-specific.
- **Exchange:** transfer of intermediate pages between tasks/stages. A repartition exchange redistributes rows by a key (often for joins or aggregations); a gather exchange brings rows to fewer tasks; a broadcast exchange replicates a smaller build side to many tasks.
- **Pipeline:** a chain of operators that can process data incrementally rather than materializing the entire result between every operator.

**MPP and pipelining.** Massively parallel processing (MPP) divides work across worker tasks. Pipelining lets filters and projections process rows as they arrive. But not every operation is fully streaming: hash joins build hash tables, sorts need ordering state, and repartition exchanges move data over the network.

**Why network transfer matters.** A join can be CPU-light but network-heavy if a large relation must be shuffled. Broadcast can avoid shuffling the probe side but replicates the build side to workers and increases memory pressure. Remote source reads, inter-worker exchange, object-store bandwidth, and client result transfer are separate costs.

### 3.3 From SQL to distributed work

For a query such as:

```sql
SELECT c.region, sum(e.amount) AS revenue
FROM lake.analytics.events e
JOIN postgres.crm.customers c ON e.customer_id = c.customer_id
WHERE e.event_date >= DATE '2026-10-01'
  AND e.event_date <  DATE '2026-11-01'
GROUP BY c.region;
```

The coordinator resolves both table names and types, builds a logical plan, applies valid rewrites, chooses join order/distribution using available statistics, and creates distributed stages. Workers read selected Iceberg files and PostgreSQL rows via connectors, filter/project where possible, exchange rows for the join/aggregation if needed, and send result pages back. This is the conceptual flow; a specific plan may differ and must be inspected.

### 3.4 Connect from clients

**Trino CLI.** Use a CLI JAR/version compatible with the cluster. A typical local connection is:

```bash
trino --server http://localhost:8080 --user analyst --catalog iceberg --schema analytics
```

The CLI artifact/version and authentication options should match the server's release and security setup. Do not use an unauthenticated HTTP example for a production cluster.

**JDBC.** Download the official Trino JDBC driver matching your client requirements. A typical URL shape is:

```text
jdbc:trino://trino.example.com:8443/iceberg/analytics?SSL=true
```

The exact TLS and authentication properties depend on the driver/server configuration. Keep credentials in a secret manager or client configuration, not in source code. For a Trino 484 lab, use the matching versioned documentation; the examples below pin `trinodb/trino:484` and are not guaranteed to be drop-in compatible with later releases.

**Python DBAPI.** Install the official client with `python -m pip install trino` and use:

```python
import os
from trino.dbapi import connect
from trino.auth import BasicAuthentication

conn = connect(
    host=os.environ["TRINO_HOST"],
    port=int(os.getenv("TRINO_PORT", "8443")),
    user=os.environ["TRINO_USER"],
    catalog="iceberg",
    schema="analytics",
    http_scheme="https",
    auth=BasicAuthentication(
        os.environ["TRINO_USER"], os.environ["TRINO_PASSWORD"]
    ),
)
try:
    cur = conn.cursor()
    cur.execute("SELECT current_catalog, current_schema, current_timestamp")
    print(cur.fetchall())
finally:
    conn.close()
```

This example expects HTTPS and a server configured for compatible basic/password authentication. For local development without authentication, omit `auth` and use the server's actual HTTP settings; never disable TLS verification as a production workaround. OAuth2 and Kerberos/GSSAPI are also available through client authentication classes when the server is configured for them.

## 4. Catalogs, schemas, tables, and connectors

### 4.1 The namespace model

- **Catalog:** configured access to a source, including the connector and its properties. A catalog is usually created by a properties file such as `etc/catalog/iceberg.properties`.
- **Connector:** the adapter that implements Trino's connector interface for a data source or table format.
- **Schema:** namespace within a catalog.
- **Table:** relation exposed by the connector. It may be a physical table, a lakehouse table, a view, or a connector-specific representation.

The usual fully qualified name is `catalog.schema.table`, for example `iceberg.analytics.events` or `postgres.crm.customers`. Catalog names are the configured catalog filenames without `.properties`.

### 4.2 Connector map and qualifications

| Connector | Common use | Important qualification |
| --- | --- | --- |
| **Hive** | Hive-metastore tables over files such as Parquet/ORC on HDFS or object storage | Requires compatible metastore/storage configuration. File listing and partition metadata can dominate scans. Hive tables are not the same thing as Iceberg tables. |
| **Iceberg** | Lakehouse tables with snapshots, manifests, schema/partition evolution and table-level metadata | Needs a supported Iceberg catalog/metastore and storage access. Writes, `MERGE`, maintenance, and catalog capabilities depend on Trino version and catalog type. |
| **Delta Lake** | Delta tables | Delta protocol features and write operations are version- and connector-dependent. Do not assume full parity with Spark. |
| **PostgreSQL / MySQL** | Federated relational tables | Pushdown and type mapping depend on connector, source version, query semantics and configuration. Source load and network round trips matter. |
| **Kafka** | Query records in Kafka topics using configured schemas | It is not a general-purpose replacement for a durable analytical table; schema/format mapping and time-window scan behavior require care. |
| **MongoDB** | Query supported MongoDB collections | Type mapping, filter/aggregation pushdown and write support differ from relational connectors. |
| **Elasticsearch** | Search/document data via SQL-like access | Pushdown depends on expression support and mappings; nested fields and aggregations may have limitations. |
| **BigQuery** | Federate with Google BigQuery datasets | Network, billing, auth, source SQL semantics and pushdown affect cost; this is a remote service connector. |
| **Snowflake** | Federate with Snowflake objects | Connector capabilities, auth, source execution and costs depend on release and service configuration. |

A connector is not a promise that every SQL operation is supported. Check the documentation for the exact Trino version and connector before designing writes, predicate pushdown, aggregation pushdown, transactions, or maintenance.

### 4.3 Example catalog properties

These are **illustrative configuration fragments**, not a complete production deployment. Put each file in `etc/catalog/` on every coordinator/worker according to deployment practice, and protect credentials. Names and properties must be checked against the selected release.

**PostgreSQL** (`etc/catalog/postgres.properties`):

```properties
connector.name=postgresql
connection-url=jdbc:postgresql://postgres:5432/crm
connection-user=${ENV:PG_USER}
connection-password=${ENV:PG_PASSWORD}
```

Environment-variable substitution depends on the server's configuration support and deployment method; confirm it for the pinned release. If unsupported in your packaging, inject secrets using the deployment's supported secret mechanism rather than literal passwords.

**Iceberg using a REST catalog** (`etc/catalog/iceberg.properties`):

```properties
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=http://iceberg-rest:8181
# Add REST-catalog authentication properties if the service requires them.
# Configure object-storage access using the properties supported by your
# chosen Trino version and S3-compatible storage implementation.
```

This fragment deliberately does not pretend that every REST catalog configures S3 credentials the same way. The REST catalog service must be configured to use the same warehouse and MinIO endpoint that Trino can access. Verify the current Trino Iceberg REST-catalog and S3 filesystem properties for the exact release. A Hive catalog is an alternative when you have a compatible Hive Metastore service.

**Hive over S3-compatible object storage:** the Hive catalog typically needs `connector.name=hive`, a metastore URI, and version-appropriate S3 filesystem/endpoint/credentials settings. Do not mix Iceberg catalog properties into the Hive connector configuration.

### 4.4 Parquet/ORC, metastore, and partition pruning

With the Hive connector, the metastore describes schemas, partitions, and file locations; workers read Parquet/ORC files from storage. The Hive connector often needs to enumerate files under selected partitions. With Iceberg, table metadata/manifests identify the data files, so the engine can avoid broad object-store listings and can use Iceberg metadata to prune files.

**Partition pruning** means using partition metadata and filter predicates to skip irrelevant partitions/files before scanning their rows. Write sargable predicates on partition columns when possible. For example, a date range on a `DATE` partition column is generally easier to prune than wrapping the column in a function that the connector cannot translate.

```sql
SELECT count(*)
FROM iceberg.analytics.events
WHERE event_date >= DATE '2026-10-01'
  AND event_date <  DATE '2026-11-01';
```

Do not assume a partition filter actually pruned files: confirm with plan details and runtime input metrics. Partitioning helps only when partition values align with real query filters; very high-cardinality partitioning can create excessive small files and metadata overhead.

### 4.5 Cross-catalog SQL

Once catalogs are configured and permissions allow it, one query can reference both:

```sql
SELECT c.region, count(*) AS event_count
FROM iceberg.analytics.events e
JOIN postgres.crm.customers c
  ON e.customer_id = c.customer_id
WHERE e.event_date >= DATE '2026-10-01'
  AND e.event_date <  DATE '2026-11-01'
  AND c.is_active = true
GROUP BY c.region;
```

This is syntactically a single query, not necessarily a single-source execution. If PostgreSQL can push `is_active = true` down, fewer customer rows may reach Trino. The Iceberg scan may prune date partitions. The join itself is commonly executed in Trino unless a connector/source can support the complete operation in a pushdown-compatible way. Prove the actual behavior in the plan.

## 5. Guided lakehouse query

### 5.1 Create a small Iceberg table

Assume `iceberg` is a configured Iceberg catalog backed by MinIO and a supported REST or Hive catalog. Create a schema if supported by that catalog:

```sql
CREATE SCHEMA IF NOT EXISTS iceberg.analytics;

CREATE TABLE iceberg.analytics.events (
    event_id BIGINT,
    customer_id BIGINT,
    event_date DATE,
    event_type VARCHAR,
    amount DECIMAL(12, 2)
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['month(event_date)']
);
```

Iceberg table properties and partition transforms vary by connector release. If the deployed version rejects a property, consult that version's Iceberg connector documentation rather than guessing a different spelling. `month(event_date)` is a logical partition transform; Iceberg manages the physical partition metadata.

Insert safe synthetic development rows:

```sql
INSERT INTO iceberg.analytics.events VALUES
    (1, 101, DATE '2026-10-02', 'purchase', 19.99),
    (2, 102, DATE '2026-10-08', 'view',      0.00),
    (3, 101, DATE '2026-11-03', 'purchase', 49.50);

SELECT event_date, event_type, amount
FROM iceberg.analytics.events
WHERE event_date >= DATE '2026-10-01'
  AND event_date <  DATE '2026-11-01'
ORDER BY event_date;
```

**Why this matters.** The SQL is familiar, but the table's data files live in object storage. Iceberg metadata records snapshots, manifests, schemas and partition information. Trino reads metadata and selected files through its connector.

**Limitations.** Creating a schema or table may fail if the REST/Hive catalog, storage permissions, bucket/warehouse, or connector properties are incomplete. `INSERT` support and transaction behavior depend on the connector and catalog.

## 6. Guided federated join

### 6.1 Prepare the relational side

In the PostgreSQL database configured by the `postgres` catalog, create a small development table using a PostgreSQL client:

```sql
CREATE SCHEMA IF NOT EXISTS crm;

CREATE TABLE IF NOT EXISTS crm.customers (
    customer_id BIGINT PRIMARY KEY,
    region TEXT NOT NULL,
    is_active BOOLEAN NOT NULL
);

INSERT INTO crm.customers (customer_id, region, is_active) VALUES
    (101, 'south', true),
    (102, 'west',  true),
    (103, 'north', false)
ON CONFLICT (customer_id) DO UPDATE
SET region = EXCLUDED.region,
    is_active = EXCLUDED.is_active;
```

Then run through Trino:

```sql
SELECT c.region,
       count(*) AS event_count,
       sum(e.amount) AS revenue
FROM iceberg.analytics.events e
JOIN postgres.crm.customers c
  ON e.customer_id = c.customer_id
WHERE e.event_date >= DATE '2026-10-01'
  AND e.event_date <  DATE '2026-11-01'
  AND c.is_active = true
GROUP BY c.region
ORDER BY revenue DESC;
```

The PostgreSQL DDL is executed against PostgreSQL, not necessarily through Trino. The cross-catalog `SELECT` is executed through Trino. Keep source DDL separate from Trino SQL when connector write support is unknown.

### 6.2 Where does the data move?

1. Trino asks the Iceberg connector for the relevant table metadata and files.
2. Trino asks the PostgreSQL connector for table metadata and, depending on pushdown, filtered/projected rows.
3. Workers scan the Iceberg files and receive relational rows. If the source can evaluate the filter, fewer rows cross the network.
4. Trino joins the inputs. A partitioned join typically repartitions both sides by join key; a broadcast join sends the build side to multiple tasks.
5. The final aggregate/order is performed in distributed stages as needed and results are returned to the client.

**Trade-off.** The fastest design is often the one that reduces rows and bytes before crossing the source boundary. If the PostgreSQL side is large, a selective predicate or a precomputed extract may be necessary. If the data is queried repeatedly, a governed replicated lakehouse dimension may outperform repeated federation, at the cost of freshness management and storage duplication.

## 7. Query plans, pushdown, statistics, and optimization

### 7.1 `EXPLAIN` versus `EXPLAIN ANALYZE`

- **`EXPLAIN`** shows the planned execution strategy. It is useful for identifying scans, filters, exchanges, joins, estimated rows/costs, and visible connector pushdown.
- **`EXPLAIN ANALYZE`** executes the query and reports observed runtime statistics such as input/output rows, CPU, wall time, and operator/stage details depending on the version and output format. It can be expensive and should be used thoughtfully on production-sized data.

```sql
EXPLAIN
SELECT count(*)
FROM iceberg.analytics.events
WHERE event_date >= DATE '2026-10-01'
  AND event_date <  DATE '2026-11-01';

EXPLAIN ANALYZE
SELECT count(*)
FROM iceberg.analytics.events
WHERE event_date >= DATE '2026-10-01'
  AND event_date <  DATE '2026-11-01';
```

A logical plan describes intended relational operations; a physical/distributed plan describes chosen operators and exchanges; runtime analysis reports what actually happened in that execution. A plan alone is not proof of real runtime performance.

### 7.2 Pushdown types

| Type | Meaning | Evidence to look for | Caveat |
| --- | --- | --- | --- |
| Predicate/filter pushdown | Source applies a supported filter before returning rows | Connector plan details show pushed constraints; runtime input rows/bytes fall | Complex expressions, casts, null semantics, collation and type mappings may prevent it. |
| Projection pushdown | Source returns only required columns | Scan lists fewer columns; source query/metrics show a narrower projection | Some formats or connector paths may still read row groups/column chunks beyond apparent columns. |
| Aggregation pushdown | Source computes a compatible aggregate | Plan shows aggregation handled by connector/source, with reduced rows sent to Trino | Not all aggregates/grouping semantics are supported; approximate, distinct, or complex expressions often have restrictions. |
| Join pushdown | A connector executes a join at source | Connector-specific plan explicitly shows the pushed join | Usually only possible within one source/connector under specific conditions; do not assume a cross-catalog join is pushed to PostgreSQL. |

**How to improve a query.** Select only required columns, add selective filters, avoid unnecessary casts/functions on filtered columns, use compatible join key types, and aggregate before a cross-source boundary only when semantics allow it. Then rerun `EXPLAIN` and `EXPLAIN ANALYZE`. Never claim pushdown just because a query is faster once; caching, data distribution and warm-up may explain the difference.

### 7.3 Broadcast versus partitioned joins

**Broadcast join:** copy the build-side relation to each participating task/worker. Best when the build side is genuinely small and fits in memory on every relevant worker. Risk: replication multiplies memory and network use; a table believed to be small may grow unexpectedly.

**Partitioned join:** repartition both sides by join key so matching keys meet on the same tasks. Better for larger relations when cluster resources can handle the shuffle. Risk: network shuffle, skewed keys, spill and longer stage barriers.

Trino's cost-based optimizer chooses join order and distribution using statistics and cost estimates, subject to configuration and connector capabilities. A session can often be used to experiment with join distribution, but exact property names and allowed values should be checked for the deployed release. Do not hard-code broadcast as a universal fix.

### 7.4 Statistics and `ANALYZE`

The cost-based optimizer benefits from row counts, data size, null fractions and distinct-value information when available. Connector support and statistic quality differ. Missing or stale statistics can lead to a poor join order or distribution.

```sql
ANALYZE iceberg.analytics.events;
```

Run only if the selected connector supports `ANALYZE` and statistics collection for that table. For relational sources, statistics may be maintained in the source or exposed through connector metadata rather than collected by Trino in the same way. Check connector docs for supported columns and behavior.

To test whether statistics changed a plan:

1. Capture `EXPLAIN` for the same query before `ANALYZE`.
2. Record estimated rows/costs and join distribution.
3. Run `ANALYZE` where supported; verify it completed and populated usable statistics.
4. Capture `EXPLAIN` again with the same SQL/session settings.
5. Compare estimated cardinalities, join order and exchanges. If nothing changes, report that; the table may be too small, stats may already be present, or the optimizer may still prefer the same plan.

### 7.5 Dynamic filtering

Dynamic filtering uses values observed from a join's build side to reduce work on the probe side at runtime. For example, if only a small set of customer IDs qualifies, Trino may use those values to avoid reading unrelated data on the fact side. Connectors differ in how much they can apply the filter to partition/file selection or push it into the source.

Look for dynamic-filter-related plan annotations and runtime statistics supported by the version. It may not help if the build side is large, filter values arrive late, the source cannot consume the filter, or the join semantics prevent the optimization. Dynamic filtering complements, but does not replace, good table statistics and selective predicates.

### 7.6 File sizes, small files, and caching

**Small-file problem.** Thousands of tiny files increase listing/metadata work, split scheduling, object-store requests and per-file overhead. Large files are not automatically optimal either: parallelism, partition size, compression, row-group size and query selectivity matter. Use representative benchmarks and connector-specific maintenance/compaction tools to find a reasonable size range rather than treating one size as universal.

**Caching.** A filesystem cache can retain remote file blocks on local worker disks; an external cache such as Alluxio can provide a shared caching layer for supported storage paths. Cache effectiveness depends on locality, eviction, capacity, file immutability, access patterns and whether the connector actually uses that layer. Measure cold and warm behavior separately and never assume a cache is active merely because it is installed.

### 7.7 Query diagnosis workflow

1. Start with `EXPLAIN` to understand scan columns, predicates, join order, exchanges and estimates.
2. Run `EXPLAIN ANALYZE` on a safe representative workload.
3. Compare scan input rows/bytes to expected filtered volume.
4. Inspect source-system query/metrics when evaluating pushdown.
5. Check statistics, file counts/sizes, partition layout and data skew.
6. Change one factor at a time and keep the SQL, data, cluster, concurrency and cache state consistent.
7. Save the plan and measurements; don't report a causal performance improvement from a single noisy run.

## 8. Write operations and Iceberg maintenance

### 8.1 CTAS and `INSERT`

`CREATE TABLE AS SELECT` (CTAS) creates a table from a query result. Whether a connector supports CTAS, table properties, format choices and writes depends on that connector and catalog.

```sql
CREATE TABLE iceberg.analytics.daily_revenue
WITH (format = 'PARQUET') AS
SELECT event_date,
       customer_id,
       sum(amount) AS revenue
FROM iceberg.analytics.events
GROUP BY event_date, customer_id;
```

This example writes a derived table into the Iceberg catalog; verify the table properties and partitioning supported by the selected release. It is not intended to overwrite a production table.

`INSERT INTO` appends rows where supported:

```sql
INSERT INTO iceberg.analytics.events
SELECT event_id, customer_id, event_date, event_type, amount
FROM iceberg.analytics.events_staging
WHERE event_date >= DATE '2026-10-01';
```

This can duplicate data if rerun. Design idempotency explicitly using a staging strategy, deterministic replacement/merge, or a source-controlled load key. Do not assume append is idempotent.

### 8.2 Iceberg `MERGE`

Use `MERGE` only when the chosen Trino version, Iceberg connector, catalog and table support it. Validate semantics and limitations for the release.

```sql
MERGE INTO iceberg.analytics.customer_status AS target
USING iceberg.analytics.customer_status_updates AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN UPDATE SET
    status = source.status,
    updated_at = source.updated_at
WHEN NOT MATCHED THEN INSERT (customer_id, status, updated_at)
VALUES (source.customer_id, source.status, source.updated_at);
```

This is an illustrative Iceberg merge pattern, not a promise that every connector supports it. Make the source unique on the merge key; multiple source matches can cause errors or ambiguous outcomes. Validate concurrency, snapshot isolation, and retry behavior before production use.

### 8.3 Maintenance: optimize and expire snapshots

Iceberg maintenance operations are connector-specific `ALTER TABLE ... EXECUTE` procedures and differ by release. Common Trino Iceberg versions expose operations such as `optimize` to rewrite small data files and `expire_snapshots` to remove expired snapshots and eligible orphaned metadata/data files. Verify exact syntax and retention properties against the deployed connector docs before running.

Illustrative forms (verify supported parameters in your release):

```sql
ALTER TABLE iceberg.analytics.events
EXECUTE optimize;

-- Example only: retention must comply with your safety policy and
-- the connector's minimum retention constraints.
ALTER TABLE iceberg.analytics.events
EXECUTE expire_snapshots(retention_threshold => '7d');
```

Do not run snapshot expiration as a casual cleanup command. It can remove time-travel/recovery history and may make files eligible for deletion. Confirm retention requirements, backups, concurrent writers, and recovery policies first. `optimize` may rewrite many files, use significant resources, and change data layout; schedule it appropriately.

### 8.4 Safe development-data practices

- Use a dedicated bucket/warehouse prefix and development catalog/schema.
- Use synthetic data and non-production credentials.
- Inspect `SHOW TABLES`, `SHOW CREATE TABLE`, and the target path before writes.
- Prefer append-only lab tables; avoid destructive `DROP`, overwrite, `MERGE`, or snapshot-expiration tests on shared data.
- Capture a before-state and know how to recreate the lab. Do not confuse dropping catalog metadata with deleting every underlying object-store file.

## 9. Resource management, security, and advanced operations

### 9.1 Memory, spilling, limits

Hash joins, aggregations, sorts and exchanges consume memory. A query can fail with a memory-limit error even if the source scan is fast. Spilling can move supported intermediate state to disk and reduce peak memory pressure, but adds I/O and does not guarantee that every operator or query can spill. Configuration names and supported operators depend on release; spilling and fault-tolerant execution are not interchangeable features.

Use query/session limits and cluster-wide limits to prevent a single query from consuming all resources. Set limits based on worker count, memory, concurrency, and workload class; a copied value from another cluster is not a sizing methodology. Diagnose memory failures using query/stage statistics and worker logs, then reduce input cardinality, project fewer columns, avoid skew, tune join distribution, or adjust resources based on evidence.

### 9.2 Resource groups and multi-tenancy

Resource groups route and constrain workloads by user, source, query type or other configured selectors. A common design separates short dashboard queries from long ETL queries so ETL does not consume all concurrency slots or queue capacity. The exact JSON/configuration schema and selectors vary by release and deployment; use the matching Trino resource-group documentation.

A resource group is not proven effective just because its config loads. Run concurrent representative queries as separate dashboard and ETL users, record queue time, running-query counts, failures and latency, and verify each query's assigned group through supported system tables/UI/logging. Keep dashboard service levels and ETL throughput measurable.

### 9.3 Fault-tolerant execution (FTE)

FTE allows supported query work to be retried after failures, depending on retry policy, exchange manager, connector support and query type. It can improve reliability for long ETL scans, but adds coordination, exchange storage/network traffic and operational complexity. Write support is not universal; enabling retries can make writes fail for connectors that do not support the configured retry policy.

Before using FTE, verify: release-specific configuration; an appropriate exchange manager where required; storage capacity and security; connector read/write support; retry policy; and behavior for non-idempotent side effects. Test failure recovery in a controlled environment, not by killing production workers.

### 9.4 Kubernetes worker autoscaling

Worker autoscaling can add or remove capacity based on queue depth, CPU, memory, or custom signals, but scaling is not instantaneous and may be limited by source throughput, object-store bandwidth, scheduler overhead, or query-stage topology. New workers must receive matching configuration, connector plugins, credentials, network access and resource limits. Scale-in must respect graceful shutdown and running work. Avoid treating pod count as a direct proxy for throughput.

### 9.5 Authentication and authorization

Authentication establishes who the caller is; authorization determines what that identity can do.

- **LDAP/password authentication:** common enterprise option when configured with TLS and appropriate identity controls.
- **OAuth2:** token-based authentication flows supported by the server/client configuration.
- **Kerberos:** common in Hadoop/Hive environments; requires correct principals, keytabs, clock synchronization and service configuration.
- **File-based access control:** simple rules managed with configuration files; useful for smaller deployments but requires disciplined rollout/review.
- **Apache Ranger / OPA:** external policy integrations may be available through Trino distributions/plugins and version-specific integrations. Verify compatibility and deployment requirements; they are not automatically present in every Trino installation.

Row filters and column masks can restrict which rows or values an identity sees, where the selected access-control system supports those features. Test least-privilege access with both allowed and denied queries. Also secure the source systems: Trino access controls do not necessarily replace native database permissions, object-store IAM, or warehouse policies.

### 9.6 Operational monitoring

Track query latency/queue time, failed queries, worker CPU and memory, spill, blocked time, exchange bytes, split counts, source errors, object-store throttling, and resource-group saturation. Correlate Trino query IDs with source-system logs. Use controlled query IDs/tags for experiments. Avoid exposing sensitive SQL literals or credentials in logs and dashboards.

### 9.7 Choosing between Trino, Spark SQL, Athena, and warehouses

| Workload | Often a strong candidate | Why / caution |
| --- | --- | --- |
| Interactive SQL across multiple existing systems | Trino | Federation and interactive distributed SQL; source latency and connector capabilities dominate some queries. |
| Large, stateful transformation pipeline with complex iterative processing | Spark SQL | Broad batch/data-processing ecosystem and transformation capabilities; startup and cluster overhead may be less suitable for quick ad hoc queries. |
| Managed ad hoc SQL over AWS data in supported services | Athena | Managed operations and AWS integration; service-specific engine version, pricing, limits and SQL behavior apply. |
| Repeated BI/warehouse workloads with managed storage, governance and workload controls | Cloud data warehouse | Integrated storage/compute and workload features; data may need to be loaded or exposed through supported federation features. |
| Small-to-medium local analytical exploration | DuckDB | Simple embedded engine with low setup overhead; single-node limits differ from distributed execution. |

This is a workload decision, not a ranking. Benchmark representative queries, concurrency, freshness, reliability, security, total cost and operating effort. Trino is useful as a data-virtualization layer in a data mesh when domains expose governed data products through consistent catalogs and access policies. It does not by itself create domain ownership, semantic contracts, quality guarantees, or product SLAs.

## 10. Troubleshooting and common mistakes

| Symptom | Likely cause | Investigation and correction |
| --- | --- | --- |
| `Catalog ... does not exist` | Missing/misnamed catalog properties or config not loaded | Check catalog filename, `connector.name`, deployment rollout and coordinator logs. |
| Table/schema not found | Wrong catalog namespace, metadata not registered, wrong case/mapping | Run `SHOW CATALOGS`, `SHOW SCHEMAS FROM catalog`, and `SHOW TABLES FROM catalog.schema`. |
| Object storage access denied | Credentials, endpoint, TLS, bucket policy, path-style or region mismatch | Test connectivity from coordinator and workers; align MinIO/S3 settings and least-privilege policies. |
| Query reads far more rows than expected | Predicate not pushed, missing partition filter, poor layout, type cast, stats/connector limitation | Inspect scan constraints and runtime input; simplify predicates and verify source metrics. |
| Join is unexpectedly slow | Large shuffle, broadcast build side too large, skew, poor join order, missing stats | Compare estimated and actual rows; run `ANALYZE` where supported; test distribution safely. |
| Query runs out of memory | Large hash table, aggregation state, sort, skew, too much concurrency | Reduce rows/columns, inspect distribution/skew, configure appropriate limits/spilling/resources. |
| Many tiny files | Frequent small writes or poor partitioning | Batch writes and use supported Iceberg/Hive maintenance after measuring impact. |
| `ANALYZE` fails or does nothing | Connector does not support it, stats already adequate, table too small, unsupported columns | Check connector documentation and compare plans before/after rather than assuming a change. |
| `MERGE` or maintenance SQL rejected | Unsupported connector/version/catalog or unsupported operation parameters | Check exact version docs; use only supported write/maintenance patterns. |
| FTE query fails after enabling retries | Connector write/retry incompatibility or exchange manager/configuration issue | Review retry policy, connector support, exchange configuration and query type. |
| Query works in DuckDB but not Trino (or vice versa) | SQL dialect/type/extension differences, catalog permissions or connector limitations | Reduce to a minimal query and compare supported syntax and data types. |

**Common mistakes from the roadmap:**

1. **No table statistics.** The optimizer may choose a poor join order or distribution. Check stats support and collect them where useful.
2. **Huge cross-database joins without filter pushdown.** Reduce rows before they cross the network; confirm with plans and source metrics.
3. **Treating Trino as a low-latency serving layer.** It is a distributed query engine, not a guaranteed sub-millisecond lookup store. Use workload-specific service-level evidence.
4. **Ignoring small files.** File enumeration and split scheduling can dominate otherwise simple lake scans.

## 11. Hands-on experiments — `experiments/03_trino/`

### 11.1 Lab goals and layout

Create a reproducible experiment directory in the project repository:

```text
experiments/03_trino/
├── README.md
├── compose.yaml
├── trino/
│   ├── config.properties
│   ├── node.properties
│   ├── jvm.config
│   └── catalog/
│       ├── iceberg.properties
│       └── postgres.properties
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_partition_pruning.sql
│   ├── 03_federated_join.sql
│   ├── 04_statistics.sql
│   └── 05_maintenance.sql
├── python/
│   └── compare_trino_duckdb.py
└── results/
    ├── README.md
    ├── plans/
    └── measurements.csv
```

The roadmap requires Trino with Iceberg on MinIO, a REST or Hive catalog, and PostgreSQL. The following is a **single-node local lab template** (not a production topology). It uses the published `apache/iceberg-rest-fixture:1.10.1` image as an example of a versioned fixture tag; confirm REST API compatibility with your pinned Trino release before starting. The fixture is a development/test catalog, not a production catalog service. Pin all images (preferably by digest for strict repeatability) in your own `.env` file. The local credentials below are placeholders for an isolated development environment only.

Create `.env` in `experiments/03_trino/` (do not commit it):

```dotenv
TRINO_IMAGE=trinodb/trino:484
# Versioned Apache Iceberg REST test fixture; verify protocol compatibility.
ICEBERG_REST_IMAGE=apache/iceberg-rest-fixture:1.10.1
MINIO_IMAGE=minio/minio:RELEASE.2024-05-10T01-41-38Z
POSTGRES_IMAGE=postgres:16.4
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=local-only-change-me
PG_USER=trino
PG_PASSWORD=local-only-change-me-too
```

The image tag is pinned in this example; verify compatibility before use and prefer an image digest for strict reproducibility. Do not use these credentials beyond a disposable local lab.

`compose.yaml`:

```yaml
services:
  minio:
    image: ${MINIO_IMAGE}
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    ports:
      - "127.0.0.1:9000:9000"
      - "127.0.0.1:9001:9001"
    volumes:
      - minio-data:/data
    networks: [lab]

  create-warehouse:
    image: minio/mc:RELEASE.2024-05-09T17-04-24Z
    depends_on: [minio]
    entrypoint: ["/bin/sh", "-ec"]
    command: >-
      until mc alias set local http://minio:9000 "$${MINIO_ROOT_USER}"
      "$${MINIO_ROOT_PASSWORD}"; do sleep 2; done;
      mc mb --ignore-existing local/warehouse
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    networks: [lab]

  iceberg-rest:
    image: ${ICEBERG_REST_IMAGE}
    depends_on:
      create-warehouse:
        condition: service_completed_successfully
    environment:
      AWS_ACCESS_KEY_ID: ${MINIO_ROOT_USER}
      AWS_SECRET_ACCESS_KEY: ${MINIO_ROOT_PASSWORD}
      AWS_REGION: us-east-1
      CATALOG_WAREHOUSE: s3://warehouse/
      CATALOG_IO__IMPL: org.apache.iceberg.aws.s3.S3FileIO
      CATALOG_S3_ENDPOINT: http://minio:9000
      CATALOG_S3_PATH__STYLE__ACCESS: "true"
    ports:
      - "127.0.0.1:8181:8181"
    networks: [lab]

  postgres:
    image: ${POSTGRES_IMAGE}
    environment:
      POSTGRES_DB: crm
      POSTGRES_USER: ${PG_USER}
      POSTGRES_PASSWORD: ${PG_PASSWORD}
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro
      - postgres-data:/var/lib/postgresql/data
    networks: [lab]

  trino:
    image: ${TRINO_IMAGE}
    depends_on: [iceberg-rest, postgres]
    environment:
      MINIO_ACCESS_KEY: ${MINIO_ROOT_USER}
      MINIO_SECRET_KEY: ${MINIO_ROOT_PASSWORD}
      PG_USER: ${PG_USER}
      PG_PASSWORD: ${PG_PASSWORD}
    ports:
      - "127.0.0.1:8080:8080"
    volumes:
      - ./trino:/etc/trino:ro
    networks: [lab]

networks:
  lab:

volumes:
  minio-data:
  postgres-data:
```

Create `trino/node.properties`:

```properties
node.environment=development
node.id=trino-lab
node.data-dir=/data/trino
```

Create `trino/config.properties` for the single-node lab:

```properties
coordinator=true
node-scheduler.include-coordinator=true
http-server.http.port=8080
discovery-server.enabled=true
discovery.uri=http://trino:8080
```

Create `trino/jvm.config` with a heap appropriate for your machine, for example:

```text
-server
-Xmx2G
-XX:+UseG1GC
-XX:G1HeapRegionSize=32M
-XX:+ExplicitGCInvokesConcurrent
-XX:+ExitOnOutOfMemoryError
```

Create `trino/catalog/iceberg.properties`:

```properties
connector.name=iceberg
iceberg.catalog.type=rest
iceberg.rest-catalog.uri=http://iceberg-rest:8181
iceberg.rest-catalog.warehouse=s3://warehouse/
fs.s3.enabled=true
s3.region=us-east-1
s3.endpoint=http://minio:9000
s3.path-style-access=true
s3.aws-access-key=${ENV:MINIO_ACCESS_KEY}
s3.aws-secret-key=${ENV:MINIO_SECRET_KEY}
```

Create `trino/catalog/postgres.properties`:

```properties
connector.name=postgresql
connection-url=jdbc:postgresql://postgres:5432/crm
connection-user=${ENV:PG_USER}
connection-password=${ENV:PG_PASSWORD}
```

Create `postgres/init.sql`:

```sql
CREATE SCHEMA IF NOT EXISTS crm;
CREATE TABLE IF NOT EXISTS crm.customers (
    customer_id BIGINT PRIMARY KEY,
    region TEXT NOT NULL,
    is_active BOOLEAN NOT NULL
);
INSERT INTO crm.customers (customer_id, region, is_active) VALUES
    (101, 'south', true),
    (102, 'west', true),
    (103, 'north', false)
ON CONFLICT (customer_id) DO UPDATE
SET region = EXCLUDED.region, is_active = EXCLUDED.is_active;
```

Start and verify the services:

```bash
docker compose config
docker compose up -d
# Wait for the REST catalog and Trino to become ready; then:
docker compose logs --tail=100 trino iceberg-rest postgres
```

Connect with a Trino CLI compatible with the image, or run the CLI inside the Trino container if that image/release includes it:

```bash
trino --server http://localhost:8080 --user lab --catalog iceberg
```

The Iceberg REST fixture and object-storage properties are version-sensitive. This catalog uses Trino 484 native S3 settings (`fs.s3.enabled`, `s3.endpoint`, `s3.path-style-access`, and `s3.aws-*`); do not substitute legacy `hive.s3.*` settings. If you change the Trino release or REST implementation, validate the exact properties and protocol compatibility against the matching official docs before running. Do not silently switch to public bucket access as a fix. The MinIO and PostgreSQL ports are bound to localhost only; keep the lab isolated.

**Minimum setup checklist**

1. Create `experiments/03_trino/` using the directory layout above. Save the PostgreSQL initialization SQL as `postgres/init.sql`, and place Trino files under `trino/` exactly as shown.
2. Start MinIO with a dedicated development bucket/warehouse and safe local-only credentials; do not expose its console publicly.
3. Start a compatible Iceberg REST catalog service (or Hive Metastore) configured for that warehouse. For REST, configure the service's S3 FileIO/endpoint/credentials as its implementation requires.
4. Start PostgreSQL with a development database and user. Create the `crm.customers` table from Section 6.1.
5. Start a pinned Trino release with `iceberg` and `postgres` catalogs configured. Ensure the coordinator and workers share compatible catalog configs and have network access.
6. Verify `SELECT version()`, `SHOW CATALOGS`, `SHOW SCHEMAS FROM iceberg`, and `SHOW SCHEMAS FROM postgres`.
7. If any component fails, resolve service readiness, DNS, credentials, bucket/warehouse paths, connector properties and version compatibility before proceeding.

This lab intentionally separates Trino configuration from catalog-service-specific bootstrap variables. The Apache Iceberg REST fixture uses a lightweight JDBC/SQLite catalog backend by default and is intended for development/testing; its metadata persistence and operational characteristics are not a production catalog design. A single universal Compose file cannot safely claim compatibility across arbitrary Trino, REST catalog, storage and metastore versions.

### 11.2 Experiment A — create Iceberg data and prove partition pruning

**Objective:** Compare a scan without a selective partition predicate to a scan with one.

1. Create `iceberg.analytics.events` as shown in Section 5.1. For a reproducible starter dataset, run the following Trino insert once in the disposable lab (100,000 rows across September–November 2026). Scale only after confirming storage and runtime headroom; do not rerun without first recreating/truncating the lab table because event IDs are deterministic.

```sql
INSERT INTO iceberg.analytics.events
SELECT
    n AS event_id,
    100 + mod(n, 1000) AS customer_id,
    date_add('day', mod(n, 90), DATE '2026-09-01') AS event_date,
    CASE WHEN mod(n, 10) = 0 THEN 'purchase'
         WHEN mod(n, 3) = 0 THEN 'signup'
         ELSE 'view' END AS event_type,
    CAST(mod(n, 50000) AS DECIMAL(12, 2)) / 100 AS amount
FROM UNNEST(sequence(1, 100000)) AS t(n);
```

   The generated customer IDs range from 100 through 1099; only IDs present in `crm.customers` will match the tiny example dimension. Increase that dimension or use a controlled join-key subset if you need a higher match rate. Keep the row count, generator expression and query mix identical across repeated runs.
2. Run and save plans/results for a query without a date filter:

```sql
EXPLAIN ANALYZE
SELECT event_type, count(*)
FROM iceberg.analytics.events
GROUP BY event_type;
```

3. Run and save the filtered version:

```sql
EXPLAIN ANALYZE
SELECT event_type, count(*)
FROM iceberg.analytics.events
WHERE event_date >= DATE '2026-10-01'
  AND event_date <  DATE '2026-11-01'
GROUP BY event_type;
```

4. Compare scanned/input rows, physical input bytes, split/file counts if reported, CPU and wall time. Repeat runs with recorded warm/cold cache conditions.

**Expected observation, not a guaranteed result:** If the table contains multiple months and the partition transform is applied as expected, the filtered query should be eligible to skip data outside October. Confirm from the scan constraints and runtime input metrics. A small dataset, cached files, or version-specific plan formatting may make latency differences noisy or invisible.

**Failure diagnostics:** Check table properties and Iceberg metadata, ensure the dates really span multiple partitions, confirm the predicate type matches the column, and verify the connector supports the partition transform. A faster run alone does not prove pruning.

### 11.3 Experiment B — federated join and pushdown evidence

**Objective:** Join Iceberg events with PostgreSQL customers and identify which work executes at the source.

1. Populate both tables with repeatable synthetic data and record row counts.
2. Run the Section 6.1 query with `EXPLAIN` and `EXPLAIN ANALYZE`.
3. Save the plan under `results/plans/` and record scan input rows/bytes, exchange volume, CPU, wall time, and source query metrics where available.
4. Modify one factor at a time:
   - remove unused columns from `SELECT`;
   - add a selective date range on the Iceberg partition column;
   - keep `c.is_active = true` on the PostgreSQL relation;
   - ensure join keys have compatible types;
   - test a pre-filtered PostgreSQL subquery if it remains semantically equivalent.
5. Compare plans and source-side metrics.

**Evidence of pushdown:** the plan/connector details explicitly show a pushed predicate/projection/aggregation, or source-system logs/metrics show a reduced remote query/result. Lower runtime alone is insufficient. If the plan still shows a filter in Trino, rows read from PostgreSQL do not decline, or the connector does not expose pushdown, report it as not demonstrated rather than claiming success.

### 11.4 Experiment C — `ANALYZE` and optimizer decisions

**Objective:** Test whether usable statistics change cardinality estimates or join distribution.

1. Create two tables with noticeably different sizes and a join key; record row counts and data distribution.
2. Capture `EXPLAIN` for the federated query before collecting stats.
3. Run `ANALYZE` only on tables/connectors that support it. Confirm the command succeeded and inspect the available statistics interface.
4. Capture `EXPLAIN` again with identical SQL, session properties and data.
5. Compare estimates, join order, broadcast/partitioned distribution and exchange nodes.

**Expected observation:** the optimizer may choose a different plan if statistics meaningfully change estimated cardinalities and costs. No change is a valid result. If the connector does not support `ANALYZE`, document the limitation and use source-maintained statistics or a different supported table for this experiment; do not invent an optimizer change.

### 11.5 Experiment D — resource-group isolation

**Objective:** Prove dashboard and ETL workloads do not compete without controls in the same way they do with controls.

1. Configure the file-based resource-group manager using the official resource-group manager for the pinned Trino release. Add `etc/resource-groups.properties` with `resource-groups.configuration-manager=file` and `resource-groups.config-file=/etc/trino/resource-groups.json` (the JSON file is read on the coordinator).
2. Use this **illustrative minimal policy** as a starting point; validate the exact schema and selectors against the pinned release before enabling it:

```json
{
  "rootGroups": [
    {
      "name": "global",
      "softMemoryLimit": "100%",
      "hardConcurrencyLimit": 8,
      "maxQueued": 50,
      "subGroups": [
        {
          "name": "dashboard",
          "softMemoryLimit": "40%",
          "hardConcurrencyLimit": 5,
          "maxQueued": 20
        },
        {
          "name": "etl",
          "softMemoryLimit": "60%",
          "hardConcurrencyLimit": 2,
          "maxQueued": 10
        }
      ]
    }
  ],
  "selectors": [
    {"user": "dashboard", "group": "global.dashboard"},
    {"user": "etl", "group": "global.etl"}
  ]
}
```

Create distinct `dashboard` and `etl` users only in a lab identity setup that supports those identities, or adapt selectors to client tags/sources that the server actually receives. Mount the resource-group files into the Trino configuration and restart/reload as required. This policy is a demonstration, not a capacity recommendation.
3. Validate config parsing and reload/restart requirements before load testing.
3. Prepare one short dashboard-style query and one larger scan/aggregation ETL query.
4. Run both concurrently with separate identities/tags. Record queue time, execution time, concurrency, failures and group assignment.
5. Repeat after changing only the resource-group policy.

**Evidence:** query assignment to the expected groups plus repeatable differences in queuing/concurrency or isolation behavior. The experiment is complete only if group assignment and behavior are observed, not just if the config file exists. If the local version/environment cannot support resource groups, document the blocker and mark this sub-experiment unexecuted.

### 11.6 Experiment E — Trino versus DuckDB

**Objective:** Compare a representative query on a local analytical engine and a distributed federated engine for small and larger data.

Use the same generated Parquet dataset, SQL semantics, data types and query result checks. DuckDB can query Parquet locally; Trino should query the same logical data through the configured Iceberg/Hive catalog. Compare a small dataset and a larger one (for example, start at 100k rows and scale to 10M+ only if resources permit). Do not compare different data, different filters, or one cold run against one warm run.

A minimal DuckDB baseline can be:

```python
import duckdb

con = duckdb.connect("experiments/03_trino/results/duckdb_lab.duckdb")
result = con.execute("""
    SELECT event_type, count(*) AS n, sum(amount) AS total_amount
    FROM read_parquet('data/events/*.parquet')
    WHERE event_date >= DATE '2026-10-01'
      AND event_date <  DATE '2026-11-01'
    GROUP BY event_type
    ORDER BY event_type
""").fetchall()
print(result)
```

Adjust the file path and DuckDB version to your local environment. The equivalent Trino query must read the same records and apply equivalent semantics. Validate result equality before comparing speed.

**Measurement protocol:** run at least several repetitions; report median and range (or p50/p95 where enough samples exist), data size, row count, hardware, versions, concurrency, cache state, and whether startup/setup time is included. Measure Trino query execution separately from client/network startup when possible. Expect DuckDB often to have lower overhead on small local data; Trino may scale across workers and sources, but is not guaranteed to be faster on a single-node dataset. The result is workload- and hardware-dependent.

### 11.7 Results template

Fill in measured values only after running the experiments. Leave cells blank or mark `not run` until evidence exists.

| Run ID | Engine/version | Dataset rows/bytes | Query | Cache state | Concurrency | p50 ms | p95 ms | Input rows/bytes | Exchange bytes | Notes |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `run-001` | `not run` | `not run` | date-filter scan | `not run` | 1 | `not run` | `not run` | `not run` | `not run` | Do not fill from expectations. |

### 11.8 Cleanup

1. Stop the local Compose services after confirming no needed data/results remain.
2. Keep plans and measurements under `results/` if they are useful for the learning record.
3. Delete only the dedicated development bucket/prefix and lab database objects. Double-check the endpoint and bucket name before deletion.
4. Avoid running snapshot expiration or broad object-store deletion against shared environments.
5. Remove secrets from shell history/logs and rotate any credentials that were accidentally exposed.

## 12. Checkpoints, common-mistake review, and references

### 12.1 Knowledge checkpoints

Answer without looking back, then verify your reasoning.

1. What is the difference between Trino, PrestoDB and Athena?
2. Why is Trino a query engine rather than the storage system of record for an Iceberg table?
3. Describe the coordinator, worker, stage, task, split and exchange using one query.
4. What is the difference between a catalog, connector, schema and table?
5. How does a federated join move data, and why can the network dominate cost?
6. What evidence distinguishes a pushed predicate from a filter executed in Trino?
7. When is a broadcast join appropriate, and what memory risk does it create?
8. What does `ANALYZE` do, and why might it not change a plan?
9. How do partition pruning and dynamic filtering differ?
10. Why is `EXPLAIN` not a substitute for `EXPLAIN ANALYZE`?
11. Why must Iceberg `MERGE`, `optimize`, and `expire_snapshots` be checked against the connector version?
12. How would you prove resource-group isolation instead of merely proving the config loaded?
13. When might DuckDB be the better tool, and when might Trino be the better tool?
14. List two conditions under which federation is a poor design choice.

### 12.2 Practical checkpoint

- [ ] Explain coordinator, workers, connectors and catalogs.
- [ ] Query an Iceberg table with a correct partition filter.
- [ ] Write and tune a federated query across Iceberg and PostgreSQL.
- [ ] Read `EXPLAIN` and `EXPLAIN ANALYZE`; identify exchanges and evidence for pushdown.
- [ ] Explain how statistics affect the cost-based optimizer and document whether `ANALYZE` changed the plan.
- [ ] Explain when Trino is not the right tool.
- [ ] Keep measured observations separate from expected behavior and assumptions.

### 12.3 Final revision checklist

Before considering this lesson complete, confirm that you can explain the query's source reads, rows/bytes crossing the network, join distribution, and failure modes. Keep experiment files version-controlled, remove secrets, and record exact engine/connector versions with every result.

### 12.4 References

Use documentation for the **same release** as the cluster. This lab pins Trino 484; the linked 484 docs are used for version-sensitive settings. The `current` docs are useful for discovery but may describe features newer than a deployed version.

- [Trino documentation](https://trino.io/docs/current/)
- [Trino concepts: data sources, connectors, catalogs, schemas and tables](https://trino.io/docs/current/overview/concepts.html)
- [Trino clients](https://trino.io/docs/current/client.html)
- [Trino Iceberg connector](https://trino.io/docs/484/connector/iceberg.html)
- [Trino 484 S3 filesystem support](https://trino.io/docs/484/object-storage/file-system-s3.html)
- [Apache Iceberg REST fixture configuration](https://apache.googlesource.com/iceberg/+/refs/heads/main/docker/iceberg-rest-fixture/README.md)
- [Trino Hive connector](https://trino.io/docs/current/connector/hive.html)
- [Trino PostgreSQL connector](https://trino.io/docs/current/connector/postgresql.html)
- [Trino query optimizer](https://trino.io/docs/current/optimizer.html)
- [Trino dynamic filtering](https://trino.io/docs/current/admin/dynamic-filtering.html)
- [Trino resource groups](https://trino.io/docs/current/admin/resource-groups.html)
- [Trino fault-tolerant execution](https://trino.io/docs/current/admin/fault-tolerant-execution.html)
- [Trino access control](https://trino.io/docs/current/security/built-in-system-access-control.html) and the version-specific external access-control integration docs
- [Trino Python client](https://github.com/trinodb/trino-python-client)
- [PrestoDB project](https://prestodb.io/) and [PrestoDB repository/wiki](https://github.com/prestodb/presto/wiki)
- [Amazon Athena documentation](https://docs.aws.amazon.com/athena/)
- *Trino: The Definitive Guide*, Matt Fuller, Manfred Moser and Martin Traverso, for deeper system concepts; verify details against current docs.

---

**Verification note:** This lesson was checked against the provided project tree and Topic 03 roadmap and reviewed for internal consistency. Runtime smoke tests and benchmark experiments were not executed in this environment; all performance outcomes in the lab are framed as hypotheses to test, not reported results. Version-sensitive configuration and connector operations must be confirmed against the exact deployment release before use.
