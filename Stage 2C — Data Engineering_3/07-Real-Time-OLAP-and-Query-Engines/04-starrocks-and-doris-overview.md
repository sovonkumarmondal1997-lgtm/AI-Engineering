# StarRocks and Apache Doris: MPP OLAP, Real-Time Upserts, and Lakehouse Analytics

> **Module:** Stage 2C — Data Engineering_3  
> **Folder:** `07-Real-Time-OLAP-and-Query-Engines/`  
> **Lesson:** `04-starrocks-and-doris-overview.md`  
> **Level:** Beginner → advanced engineering  
> **Primary lab:** `experiments/04_starrocks_doris/`

---

## How to use this lesson

This lesson follows Topic 04 of `roadmap-Real-Time-OLAP-and-Query-Engines.md`. The roadmap emphasizes join-heavy analytical workloads, high concurrency, MySQL-protocol compatibility, FE/BE architecture, StarRocks CN nodes in shared-data mode, table models, partitioning and buckets, ingestion, materialized views, lakehouse catalogs, optimization, ecosystem risk, and the `experiments/04_starrocks_doris/` lab.

Product features and syntax change across releases. Examples below are either labelled **common SQL pattern**, **StarRocks-specific**, or **Doris-specific**. Before using them in a production environment, match the syntax and feature support to the exact engine release you deploy. Commands that depend on an external Kafka cluster, ClickHouse instance, object store, or catalog are intentionally separated from the small local smoke test.

## Learning objectives

After completing this module, you should be able to:

1. Explain where StarRocks and Apache Doris fit in the OLAP landscape and why they are often effective for join-heavy, interactive analytics.
2. Describe each engine's FE/BE execution model and StarRocks shared-data FE/CN model.
3. Choose Duplicate, Aggregate, or Primary/Unique Key models based on the required row semantics.
4. Design sort keys, partitions, hash buckets, and indexes around measured access patterns.
5. Select an ingestion method: INSERT, Stream Load, Routine Load, Broker/Spark/Flink integration, or CDC.
6. Explain upsert visibility and ordering risks rather than assuming all ingestion paths behave identically.
7. Create a materialized view, distinguish synchronous maintenance from asynchronous refresh, and prove whether the optimizer rewrites a query.
8. Query external Hive/Iceberg/Delta/Hudi data where the selected release supports the needed catalog and format.
9. Read plans and benchmark fairly against ClickHouse or Trino without fabricating performance claims.
10. Make an architecture decision that includes operational maturity, support, costs, and exit risks.

## Prerequisites

- Basic SQL: `SELECT`, `JOIN`, `GROUP BY`, `INSERT`, primary keys, and aggregation.
- Familiarity with a fact table and dimension tables.
- Basic command-line and environment-variable usage.
- For the full lab: Docker, a MySQL-compatible CLI such as `mysql`, and enough RAM/CPU to run one analytical engine. Kafka, ClickHouse, and an Iceberg catalog are optional extensions, not prerequisites for the first smoke test.

---

# 1. The OLAP use case and engine positioning

## 1.1 What are StarRocks and Apache Doris?

**Definition.** StarRocks and Apache Doris are distributed, column-oriented MPP (massively parallel processing) analytical database engines. They store and/or query data across multiple nodes, plan SQL centrally, and execute scans, joins, aggregations, and exchanges in parallel.

**Why they exist.** Many analytical workloads combine large fact tables with dimensions, filter across several attributes, group by multiple dimensions, and serve many concurrent dashboard or application queries. These patterns need efficient joins, a cost-based optimizer, parallel execution, and predictable resource management.

**Internal behavior.** A Frontend (FE) parses and plans SQL, tracks metadata and coordinates execution. Backend (BE) nodes store data and execute query operators in the traditional shared-nothing deployment. StarRocks also offers a shared-data architecture where compute nodes (CNs) query data in object storage/HDFS and cache hot data locally. Apache Doris has its own FE/BE architecture and Multi-Catalog features for external sources; do not assume its architecture is identical to StarRocks shared-data mode.

**When to use them.**
- Interactive BI and dashboards with multi-table joins.
- Product analytics, reporting marts, and operational analytics.
- Real-time analytical tables fed by Kafka or CDC.
- Workloads where update/upsert semantics are important.
- Some lakehouse queries, if the selected catalog, file format, and table features are supported.

**When another tool may fit better.**
- Use Trino when federation across many existing systems is the primary goal and you do not want to make StarRocks/Doris the main serving store.
- Use Spark when large-scale transformation, arbitrary distributed ETL, or a broad compute API is more important than interactive SQL serving.
- Use ClickHouse when its scan-oriented analytics, storage model, operational profile, and workload fit are better; test complex joins and updates with representative queries.
- Use Druid/Pinot for workloads whose ingestion, indexing, and serving pattern is specifically aligned to those engines.
- Use a cloud warehouse when managed governance, ecosystem integration, and elastic SQL capacity outweigh cost, control, or latency requirements.

**Trade-off.** These engines are not automatically faster or cheaper. Results depend on data model, table size, join keys, skew, concurrency, storage tier, cache state, ingestion freshness, query mix, and operational expertise.

## 1.2 MySQL protocol compatibility

Both engines expose a MySQL-compatible wire protocol for SQL clients. A client can connect to the FE/query endpoint using a MySQL driver; this does **not** mean either engine is MySQL, implements every MySQL feature, or has the same transaction/storage semantics.

Common ports in typical deployments:
- MySQL protocol: often `9030` for FE/query access.
- HTTP load/management endpoints: often `8030` for FE and `8040` for BE in conventional layouts.

Ports are configurable and may differ in containers or managed services. Use the endpoint and port exposed by your deployment.

```bash
# Use environment variables instead of embedding credentials in scripts.
export OLAP_HOST=127.0.0.1
export OLAP_PORT=9030
export OLAP_USER=lab_user
read -s -p "OLAP password: " OLAP_PASSWORD; export OLAP_PASSWORD; echo

mysql --protocol=TCP \
  -h "$OLAP_HOST" -P "$OLAP_PORT" \
  -u "$OLAP_USER" -p"$OLAP_PASSWORD"
```

`-p"$OLAP_PASSWORD"` can briefly expose a secret in local process arguments on some systems. For shared or production environments, prefer a protected option file, credential manager, or approved secret injection mechanism. For an interactive lab, omit the password from the command and allow the client to prompt.

## 1.3 Core terms

| Term | Meaning | Engineering implication |
|---|---|---|
| FE (Frontend) | Metadata, SQL parsing/planning, catalog and cluster coordination | FE availability and metadata replication matter to query admission and DDL |
| BE (Backend) | Stores local data and executes operators in shared-nothing deployments | Data placement, replica health, disk and CPU affect query behavior |
| CN (Compute Node) | StarRocks shared-data compute node; executes work and caches remote data | Scale compute without rebalancing the full dataset, but cache misses incur remote I/O |
| Tablet / bucket | Physical data distribution unit (terminology and mechanics vary by engine/version) | Too many tiny units add scheduling and metadata overhead; too few limit parallelism |
| Partition | Coarse logical/physical grouping, often time-based | Helps pruning and lifecycle operations; excessive partition counts are harmful |
| Sort key | Orders rows within storage units and helps prefix/range pruning | Choose from common predicates and access patterns, not habit |
| Runtime filter | A filter derived from one side of a join and applied to reduce work on the other | Helps when selective join keys can be propagated in time |
| Materialized view (MV) | Persisted result of a query, maintained synchronously or refreshed asynchronously | Saves query work but costs storage, write/refresh compute, and freshness |

---

# 2. StarRocks architecture

## 2.1 FE, BE, and CN

**Definition.** StarRocks has FE nodes and two possible backend roles: BE for local-storage/shared-nothing deployments, and CN for shared-data deployments.

**Purpose.** FE separates query planning and metadata coordination from parallel data execution. BEs or CNs execute scans, filters, joins, aggregations, and data exchange.

**Internal behavior.**
1. A client submits SQL to an FE over the MySQL protocol.
2. FE parses SQL, resolves metadata, optimizes a logical plan, and creates a distributed physical plan.
3. Execution fragments run on BE/CN nodes. Operators scan tablets or external data, filter and project columns, and exchange intermediate rows as required.
4. Join and aggregate stages may repartition data over the network. A poor distribution or skewed key can make one node the bottleneck.
5. Results are returned to the client; the engine may also write intermediate or final results to storage for CTAS/load operations.

```text
MySQL-compatible client
          |
          v
   FE cluster (metadata, SQL, optimizer, scheduling)
          |
      distributed plan
          |
    +-----+------------------+
    |                        |
    v                        v
BE node / tablet         BE node / tablet
(local storage +         (local storage +
 execution)              execution)
    \                        /
     \---- network exchange-/
             |
         query result
```

**When to use.** Shared-nothing StarRocks is attractive when predictable local-storage performance and high query throughput are priorities.

**Limitations and trade-offs.**
- Shared-nothing data is placed on BEs; changing capacity can require data movement/rebalancing.
- FE quorum/availability and metadata replication must be designed correctly.
- Network exchanges for joins can dominate query time even when scans are fast.
- Node counts, replica counts, partitions, and buckets should be chosen based on workload and release-specific guidance.

## 2.2 Shared-nothing versus shared-data StarRocks

### Shared-nothing

Each BE stores a portion of the table's data on local storage and executes queries against it. Replication provides redundancy and may provide additional read capacity.

**Benefits:** local reads, mature distributed OLAP model, low latency when data is local and cache is not involved.

**Costs:** capacity management includes both compute and storage; scaling out may involve tablet redistribution or rebalancing; local disks are part of the operational design.

### Shared-data

StarRocks shared-data separates persistent data from compute. Data lives on object storage or HDFS; CNs execute queries and may cache hot data locally. FE still manages metadata and planning.

```text
Client -> FE -> CN 1 ----\
                 CN 2 -----+--> Object storage / HDFS
                 CN 3 ----/     (durable table data)
                   |
              local cache
```

**Benefits:** add/remove compute more elastically, reduce data rebalancing during compute scaling, and independently scale durable storage and compute.

**Costs:** remote I/O and cache misses can affect latency; object-store request rates, throughput, consistency assumptions, and network costs matter. A cache hit can make performance strong, but it should be measured rather than assumed. Confirm which table models and features the deployed StarRocks release supports in shared-data mode.

**Important distinction:** CN is a StarRocks architecture role. Do not describe Doris as having StarRocks-style CNs by default. Doris has FE/BE nodes; its own cloud/disaggregated-storage capabilities and terminology are release-specific and must be evaluated from Doris documentation for the exact version.

## 2.3 A basic StarRocks connection and database

```sql
CREATE DATABASE IF NOT EXISTS olap_lab;
USE olap_lab;
SELECT VERSION();
SHOW FRONTENDS;
SHOW BACKENDS;
```

The availability and exact output of cluster-inspection statements depend on permissions and release. Run them as a lab administrator. In a managed service, use the provider's supported endpoint and administrative console.

---

# 3. Apache Doris architecture

## 3.1 FE and BE roles

**Definition.** Apache Doris uses FE nodes for metadata, SQL parsing and optimization, scheduling/coordination, and BE nodes for storage and distributed execution.

**Purpose.** A SQL query is planned once and distributed across the relevant BEs. The execution layer uses columnar storage and vectorized operators for analytical throughput.

**Internal behavior.**
1. The client connects to an FE endpoint.
2. FE resolves tables, partitions, statistics, privileges, and query semantics.
3. The optimizer chooses scans, join order/distribution, runtime filters, and aggregation placement where applicable.
4. BEs scan tablet data and execute operators; data is exchanged between nodes when a join or aggregation requires redistribution.
5. FE coordinates query status and returns the result.

```text
MySQL-compatible client
          |
          v
   FE cluster (metadata, planner, optimizer)
          |
    distributed fragments
       /          \
      v            v
    BE 1          BE 2
  tablets +      tablets +
  execution      execution
       \          /
        network exchange
```

**When to use.** Doris is a candidate for interactive analytics, join-heavy SQL, high-concurrency serving, and real-time tables loaded from Kafka or CDC.

**Limitations and trade-offs.**
- FE/BE sizing and high availability are separate operational responsibilities.
- Distributed joins remain sensitive to skew, network bandwidth, partitioning, and statistics.
- Feature availability may differ across Doris versions, particularly for optimizer features, async materialized views, lakehouse formats, and refresh strategies.
- Use the matching version's documentation rather than copying SQL from the `dev` documentation into an older cluster without verification.

## 3.2 StarRocks and Doris: architecture comparison

| Concern | StarRocks | Apache Doris |
|---|---|---|
| Query frontend | FE nodes | FE nodes |
| Traditional local-storage execution | BE stores data and computes | BE stores data and computes |
| Shared-data / compute separation | Shared-data architecture uses FE + CN with object storage/HDFS | Doris has its own evolving cloud/disaggregated-storage capabilities; do not equate them directly with StarRocks CN |
| MySQL protocol | Yes | Yes |
| Native table models | Duplicate, Aggregate, Primary Key | Duplicate Key, Aggregate Key, Unique Key |
| External lake access | External catalogs including Hive, Iceberg, Hudi, Delta Lake, subject to version/config | Multi-Catalog for formats/sources including Hive, Iceberg, Hudi, Delta Lake, subject to version/config |
| MV families | Synchronous rollup-style MVs and asynchronous MVs with broader query rewrite | Synchronous MVs and asynchronous MVs; exact rewrite and refresh capabilities are version-sensitive |

---

# 4. Table models, keys, and data distribution

The model is not just a storage detail. It defines what happens when the same business key arrives again.

## 4.1 Duplicate-key tables: preserve events

**Definition.** A Duplicate Key table retains repeated rows. Its key/order definition primarily helps sorting and query pruning; it does not promise uniqueness.

**Purpose.** Preserve raw events, logs, clicks, measurements, and append-oriented facts.

**Common StarRocks pattern:**

```sql
CREATE TABLE events (
    event_date DATE NOT NULL,
    tenant_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    event_type VARCHAR(64),
    amount DECIMAL(12,2)
)
ENGINE=OLAP
DUPLICATE KEY(event_date, tenant_id, event_id)
PARTITION BY date_trunc('day', event_date)
DISTRIBUTED BY HASH(tenant_id) BUCKETS 8
PROPERTIES ("replication_num" = "1");
```

**Version note:** Partition expressions and bucketing syntax have changed across releases; this is a teaching pattern, not a universal cross-version migration script. Use the matching product's table-creation guide. A one-replica table is acceptable only for a disposable local lab; use a supported replica count for production.

**Interpretation.** If the same `event_id` is inserted twice, both records can remain. If your application requires “latest row per ID,” a Duplicate Key table is the wrong model unless you explicitly implement deduplication downstream.

## 4.2 Aggregate-key tables: combine values by key

**Definition.** Aggregate tables group rows by key columns and apply aggregate functions to value columns during load/compaction/query processing according to engine semantics.

**Purpose.** Pre-aggregate facts such as counts or revenue by a stable dimension grain.

**Trade-off.** Detail may be lost. If the table stores `SUM(amount)` by day and product, it cannot answer arbitrary event-level questions. Late corrections and deletes need a carefully designed model and supported correction strategy.

**Illustrative StarRocks pattern:**

```sql
CREATE TABLE daily_sales (
    sale_date DATE NOT NULL,
    product_id BIGINT NOT NULL,
    order_count BIGINT SUM,
    revenue DECIMAL(18,2) SUM
)
ENGINE=OLAP
AGGREGATE KEY(sale_date, product_id)
DISTRIBUTED BY HASH(product_id) BUCKETS 8
PROPERTIES ("replication_num" = "1");
```

Check supported aggregate-key data types and DDL for the release in use. Do not assume that an aggregate table behaves like a general-purpose SQL `GROUP BY` view for every update pattern.

**Apache Doris equivalent model (Doris-specific DDL):**

```sql
CREATE TABLE daily_sales_doris (
    sale_date DATE NOT NULL,
    product_id BIGINT NOT NULL,
    order_count BIGINT SUM,
    revenue DECIMAL(18,2) SUM
)
AGGREGATE KEY(sale_date, product_id)
DISTRIBUTED BY HASH(product_id) BUCKETS 8
PROPERTIES ("replication_num" = "1");
```

In both engines, key columns define the aggregation grain and value-column aggregation operators define how incoming values combine. Verify NULL handling, supported aggregate types, compaction behavior, and corrections/deletes in the exact release before using this model for financial data.

## 4.3 Primary Key / Unique Key tables: maintain current state

### StarRocks Primary Key

**Definition.** StarRocks Primary Key tables maintain one current row for each primary key and support upsert semantics through supported load paths and DML. The key must satisfy the engine's nullability/uniqueness rules. The physical sort key can be decoupled from the primary key in newer releases; verify release support.

**Use cases:** customer profile current state, inventory balances, order status, CDC replicas, latest device state.

**Important loading distinction.** Current StarRocks documentation says Primary Key table changes can be applied through Stream Load, Broker Load, or Routine Load; it also notes restrictions for some load methods such as Spark Load or `INSERT` depending on the exact release and feature path. Do not infer that every method supports every update/delete operation. Verify the chosen method and version before adopting a write path.

### Apache Doris Unique Key

**Definition.** Doris Unique Key tables keep the latest row per declared key. In modern Doris releases, Merge-on-Write (MoW) is the default for Unique Key tables; writes mark prior row versions as deleted and append new row data so reads do not have to merge all versions in the older Merge-on-Read style.

**Use cases:** CDC and frequent updates, dimensions, profiles, current status, deduplicated entities.

**Important differences.** StarRocks calls the model `PRIMARY KEY`; Doris calls it `UNIQUE KEY`. Their write-path capabilities, partial updates, sequence-column behavior, and release defaults are not identical. Never copy the DDL from one engine into the other and assume equivalent semantics.

### StarRocks Primary Key example

```sql
CREATE TABLE user_profile (
    user_id BIGINT NOT NULL,
    user_name VARCHAR(100),
    city VARCHAR(80),
    source_version BIGINT
)
ENGINE=OLAP
PRIMARY KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 8
PROPERTIES ("replication_num" = "1");
```

### Doris Unique Key example

```sql
CREATE TABLE user_profile (
    user_id BIGINT NOT NULL,
    user_name VARCHAR(100),
    city VARCHAR(80),
    source_version BIGINT
)
UNIQUE KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 8
PROPERTIES ("replication_num" = "1");
```

The syntax above illustrates the table model; property names, bucket syntax, and distribution defaults are release-specific. If you use a sequence column to protect against out-of-order CDC events, configure it using the product's documented syntax and test equal-version ties. Without ordering protection, an older arriving event may overwrite a newer business state.

**Concrete Doris sequence-column example:** because `source_version` is part of the table schema above, a Doris deployment that supports visible sequence-column mapping can configure the table property as follows at creation time:

```sql
-- Doris only; create a new table with this property (do not assume it can
-- be retrofitted to an existing table without a supported ALTER procedure).
CREATE TABLE user_profile_ordered (
    user_id BIGINT NOT NULL,
    user_name VARCHAR(100),
    city VARCHAR(80),
    source_version BIGINT NOT NULL
)
UNIQUE KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 4
PROPERTIES (
    "replication_num" = "1",
    "function_column.sequence_col" = "source_version"
);
```

This makes the configured sequence value participate in conflict resolution for competing writes to the same key. Confirm that the target Doris release supports the property and sequence-column type; test lower, higher, and tied sequence values. StarRocks Primary Key ordering/version features have their own supported configuration and restrictions: do not copy the Doris property into StarRocks. If you cannot establish supported sequence semantics for the selected StarRocks release, enforce ordering upstream and document that guarantee.

## 4.4 Sorting keys and prefix indexes

**Definition.** Rows are stored in a sort order within storage units. A prefix index or related index structure helps the engine locate relevant key ranges without scanning all rows.

**Why it matters.** A query that filters by the leading sort columns can skip more data. A query that filters only on a non-leading column may get less benefit from the sort key and need another index or more scanning.

Example access patterns:
- `WHERE tenant_id = ? AND event_date >= ?` suggests considering tenant/date ordering.
- A global date dashboard may prefer date-first ordering.
- A query dominated by product joins may need a different layout than a tenant-scoped event feed.

Do not choose a key solely because a column is frequently selected. Choose it from filter selectivity, sort/group requirements, data distribution, and query patterns.

## 4.5 Partitions and buckets

- **Partitions** group data by a coarse dimension, often date, and support pruning and lifecycle management.
- **Buckets** hash or distribute rows across physical units/nodes to enable parallel work and balance data.
- Too many tiny partitions/buckets increase metadata and scheduling overhead.
- Too few buckets reduce parallelism or create oversized units.
- Skewed hash keys can make one bucket much larger than others.

Partitioning is not a universal speed button. A partition key should align with common filters and retention policies; avoid high-cardinality partitioning unless the engine and workload justify it.

## 4.6 Colocation joins

**Definition.** Tables are colocated when matching join-key values are placed on compatible nodes/buckets so a join can be executed locally or with less data shuffling.

**Purpose.** Reduce network transfer for repeated joins between large tables.

**Requirements and limitations.** Colocation requires compatible distribution definitions and engine-specific group/property configuration. If one side has different buckets, incompatible hash keys, or a skewed key, the optimizer may still need to redistribute data. Check the actual physical plan; never assume colocation merely because two tables contain the same column.

## 4.7 Bitmap and Bloom-filter indexes

- **Bitmap indexes** are useful for selected low-/medium-cardinality filtering patterns where the engine supports the target type and query shape.
- **Bloom filters** can help rule out data units that definitely do not contain a value; a positive result can be a false positive, so the filter does not prove a row exists.
- Indexes add build, storage, and maintenance costs. They do not replace good sorting, partitioning, statistics, or selective predicates.

Create an index only after identifying a repeated bottleneck and measuring plan/rows-read changes on representative data.

### Engine-specific index examples

Run these examples only after creating the `events_dup` table in Section 10.3. **StarRocks — bitmap index and Bloom-filter index** (confirm column-type support and index-build state for your release):

```sql
-- Bitmap index: useful for supported, repeated filter predicates.
CREATE INDEX idx_events_product ON events_dup (product_id) USING BITMAP;
-- Check index state using the release-supported SHOW/ALTER commands.

-- Bloom filters are configured as a table property, not with CREATE INDEX.
-- Include this property in CREATE TABLE, or alter the table as documented:
ALTER TABLE events_dup SET ("bloom_filter_columns" = "user_id");
```

**Apache Doris — bitmap index and BloomFilter index** (the syntax is not identical to StarRocks):

```sql
CREATE INDEX idx_events_product ON events_dup (product_id)
USING BITMAP COMMENT 'filter product id';

ALTER TABLE events_dup SET ("bloom_filter_columns" = "user_id");
```

These are examples, not a recommendation to index every column. Bitmap index eligibility depends on table model, column type, and engine version. Bloom filters primarily help supported equality/`IN` predicates on selective higher-cardinality columns; they can produce false positives and do not return rows themselves. Index creation/alteration can be asynchronous; wait for completion and inspect the plan/profile before measuring.

### Engine-specific colocation example

StarRocks uses the `colocate_with` table property and requires compatible bucket key types/order, bucket count, replica count, and placement within a colocation group. Example (use only when both tables have compatible distribution):

```sql
-- StarRocks only; apply the same group and compatible distribution to both tables.
CREATE TABLE customer_dim (
    customer_id BIGINT NOT NULL,
    region_id BIGINT
)
DUPLICATE KEY(customer_id)
DISTRIBUTED BY HASH(customer_id) BUCKETS 8
PROPERTIES ("replication_num" = "1", "colocate_with" = "customer_join_group");
```

Doris also supports colocate groups in supported releases, but verify its deployment/version-specific requirements independently. In either engine, a matching `colocate_with` property alone is not evidence that a query used a colocated join: inspect `EXPLAIN`/profile and confirm compatible distribution and group stability.

---

# 5. Ingestion and upsert workflows

## 5.1 Choose the load path deliberately

| Method | Best fit | Main operational consideration |
|---|---|---|
| `INSERT` | Small controlled writes, SQL transformations, demos | Not equivalent to a high-throughput bulk-ingestion path; support differs by model/version |
| Stream Load | HTTP-based bulk file/data ingestion | Requires FE/BE HTTP endpoint, authentication, correct format and load labels/options |
| Routine Load | Continuous Kafka ingestion | Requires Kafka connectivity, topic/partition setup, job monitoring, and schema mapping |
| Broker Load / broker integrations | Batch files in object storage/HDFS | Depends on external storage access and version-specific support |
| Spark/Flink connectors | Pipeline-native loading and transformation | Connector versions, checkpoints, retries, and delivery semantics need alignment |
| CDC pipeline | Propagate inserts, updates, deletes from an OLTP source | Must handle ordering, duplicate delivery, deletes, schema evolution, and replay |

Do not describe the ingestion methods as interchangeable. The correct method depends on source format, throughput, latency, update semantics, and the product version.

## 5.2 Stream Load

**Definition.** Stream Load accepts data through an HTTP request and loads it into a target table.

**Why use it.** It is convenient for bounded files or micro-batches from an application or pipeline.

**Operational checklist.**
1. Ensure the target table model is correct.
2. Use an authorized account with load privileges.
3. Confirm endpoint and authentication.
4. Choose the correct file format and delimiter.
5. Use a unique load label where supported to make retries safer.
6. Inspect the returned status and row counts; then query the target table.
7. Monitor rejected rows and load error logs.

A typical pattern is:

```bash
# Example only: endpoint and authentication depend on the deployment.
# Prefer a credential helper or protected netrc/secret injection.
curl --fail-with-body -u "$OLAP_USER:$OLAP_PASSWORD" \
  -H "label: events_smoke_$(date +%s)" \
  -H "format: csv" \
  -H "column_separator:," \
  -T events.csv \
  "http://${OLAP_HOST}:8030/api/olap_lab/events/_stream_load"
```

**Do not run this blindly.** Stream Load URL paths, authentication, redirects, database/table names, and accepted headers can vary by product and deployment. StarRocks and Doris both provide Stream Load, but use their own official syntax and endpoint guidance. For a secure production client, handle FE redirects and TLS certificates according to the official load API.

## 5.3 Routine Load from Kafka

**Definition.** Routine Load creates a long-running job that continuously consumes a Kafka topic and writes records to a table.

**Purpose.** Keep an analytical table fresh without a separate polling application.

**Internal behavior.** The engine schedules consumption tasks over Kafka partitions, parses messages, loads batches, and records progress. StarRocks and Doris both document exactly-once loading guarantees for their supported Routine Load transaction/job semantics. Treat those as engine-and-job scoped guarantees, not proof of end-to-end exactly-once behavior across arbitrary producers, transformations, external side effects, or downstream consumers; verify the exact release and replay/recovery behavior.

**Prerequisites.**
- Kafka brokers reachable from the engine's execution nodes.
- Topic created with enough partitions for the intended concurrency.
- Message schema agreed with table columns.
- Network/TLS/SASL settings configured if required.
- A table model that matches the desired duplicate/upsert behavior.
- Monitoring for job state, lag, rejected rows, and restarts.

### Target table for the Kafka upsert exercise

Create the matching table before creating a Routine Load job. The `source_version` column is included so the lab can compare arrival-order behavior with sequence-aware behavior; it does not by itself enforce ordering.

**StarRocks:**

```sql
CREATE TABLE user_profile_kafka_sr (
    user_id BIGINT NOT NULL,
    user_name VARCHAR(100),
    city VARCHAR(80),
    source_version BIGINT
)
PRIMARY KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");
```

**Doris:** use the `user_profile_ordered` table from the Doris sequence-column example in Section 4.3, or create a normal `UNIQUE KEY(user_id)` table if explicitly testing arrival-order last-write-wins without sequence protection. For the four-column Kafka message sequence below, create the sequence-enabled table in `olap_lab` before creating the job.

### Doris Routine Load: illustrative SQL shape

```sql
CREATE ROUTINE LOAD olap_lab.user_profile_kafka
ON user_profile_ordered
COLUMNS(user_id, user_name, city, source_version)
PROPERTIES
(
  "desired_concurrent_number" = "1",
  "max_batch_interval" = "10",
  "max_batch_rows" = "200000"
)
FROM KAFKA
(
  "kafka_broker_list" = "kafka:9092",
  "kafka_topic" = "user_profile",
  "property.group.id" = "doris_user_profile_lab",
  "property.kafka_default_offsets" = "OFFSET_BEGINNING"
);
```

This is an **illustrative Doris configuration**, not a portable cross-version recipe. Verify the current Doris Routine Load syntax and job options before running. If messages are JSON, configure the appropriate JSON format and column mapping rather than using this CSV-style mapping. For StarRocks, use its `CREATE ROUTINE LOAD` documentation and property names; do not assume the Doris statement is interchangeable.

**StarRocks Routine Load — CSV-shaped example:**

```sql
-- StarRocks only. Broker address must be reachable from the cluster.
CREATE ROUTINE LOAD olap_lab.user_profile_kafka_sr ON user_profile_kafka_sr
COLUMNS (user_id, user_name, city, source_version)
PROPERTIES (
    "desired_concurrent_number" = "1",
    "max_batch_interval" = "10"
)
FROM KAFKA (
    "kafka_broker_list" = "kafka:9092",
    "kafka_topic" = "user_profile",
    "property.kafka_default_offsets" = "OFFSET_BEGINNING"
);

SHOW ROUTINE LOAD FOR user_profile_kafka_sr;
```

For JSON payloads, add the release-supported JSON format and mapping options rather than retaining CSV-style `COLUMNS` assumptions. Do not run both engine-specific job definitions against one cluster. Stop/cancel test jobs and delete the lab topic when the experiment is complete.

**Ordering limitation:** the StarRocks table above demonstrates primary-key upsert semantics, not source-version conflict resolution. StarRocks and Doris do not share one universal sequence-column configuration. If the deployed StarRocks release or CDC connector does not provide a documented ordering mechanism for this path, preserve source order upstream (for example, partition CDC events by primary key) and test replay behavior. The Doris `function_column.sequence_col` example is Doris-specific.

### Testing an upsert

1. Publish a row with key `101`, city `Pune`, version `1`.
2. Wait until the load job reports progress and the row is visible.
3. Publish the same key with city `Bengaluru`, version `2`.
4. Query the target table repeatedly while observing job status; the current-state table should expose one row for key `101` after the write becomes visible.
5. Then publish the old version-1 message again. In a table without sequence protection, this late write may replace the newer state because arrival order is not source-version order.
6. Repeat against a table configured with the engine's supported sequence/version mechanism. Confirm that version `2` remains current, including behavior for tied sequence values.

A duplicate-key table is expected to preserve both messages. A primary/unique-key table is intended to maintain current state, but the key model alone does not guarantee source-order conflict resolution. Do not claim sequence protection unless the relevant table property/feature is configured and the late-event test passes.

## 5.4 CDC design rules

- Preserve a stable source primary key.
- Carry a source commit sequence/version/timestamp when available.
- Define delete representation explicitly.
- Decide whether partial updates are allowed and how missing fields are interpreted.
- Handle duplicate delivery and replay.
- Treat schema evolution as a contract change.
- Monitor source lag and target freshness separately.
- Reconcile counts and sampled keys against the source.
- Test an update, delete, duplicate, late event, and full replay before production rollout.

---

# 6. Materialized views and query rewrite

## 6.1 What is a materialized view?

A regular SQL view stores query logic; a materialized view stores precomputed data derived from a query. It can reduce repeated scans, joins, or aggregations.

**Why use it.** If many dashboards repeatedly calculate revenue by day/product, a suitable materialized view may shift work from query time to write or refresh time.

**Trade-offs.**
- More storage.
- More work during ingestion or refresh.
- Potentially stale results for asynchronous refresh.
- Query rewrite is conditional, not guaranteed.
- Updates, deletes, late events, and changed business logic require validation and possibly rebuild/backfill.

## 6.2 StarRocks: synchronous and asynchronous MVs

StarRocks distinguishes synchronous rollup-style materialized views from asynchronous materialized views.

- **Synchronous MV:** maintained with base-table loading and commonly used for supported single-table rollup/prefilter patterns. Data freshness is tied closely to base writes, but supported definitions and aggregate functions are constrained.
- **Asynchronous MV:** a persisted object refreshed asynchronously or manually according to its definition and refresh policy. It supports broader patterns, including some joins and query rewrite, subject to release-specific rules.

A StarRocks synchronous rollup-style MV is tied to a supported base-table definition and maintained with base-table data changes; it is not scheduled with `REFRESH ASYNC`. Its supported definition and creation syntax are version-sensitive. Use the version-matched synchronous MV/rollup documentation and test load-time cost separately from async refresh cost. Do not treat the async DDL below as a synchronous MV.

A simple aggregate query for the lab:

```sql
SELECT event_date, product_id, SUM(amount) AS revenue
FROM events_dup
GROUP BY event_date, product_id;
```

**StarRocks-specific asynchronous MV example** (supported syntax and refresh options vary by release):

```sql
CREATE MATERIALIZED VIEW daily_revenue_mv
REFRESH ASYNC EVERY (INTERVAL 1 HOUR)
AS
SELECT event_date, product_id, SUM(amount) AS revenue
FROM events_dup
GROUP BY event_date, product_id;

-- If the scheduled refresh has not completed or a manual refresh is needed:
REFRESH MATERIALIZED VIEW daily_revenue_mv;
SHOW MATERIALIZED VIEWS;
```

The scheduled interval is an example, not a freshness guarantee. Confirm the actual refresh state, last refresh time, and base-table change behavior using the deployed version's supported metadata commands. StarRocks synchronous rollup MVs have a different creation/maintenance model and narrower supported query definitions; do not call the asynchronous definition above a synchronous MV.

### Proving a StarRocks rewrite

1. Create and fully build the MV.
2. Run the original query without explicitly referencing the MV.
3. Inspect the plan with `EXPLAIN` (and the release's supported verbose/trace mechanisms).
4. Confirm the physical plan scans the MV or includes an explicit rewrite indicator.
5. Compare the result against a direct query over the base table.
6. Compare latency under both cold and warm cache conditions and record refresh lag.

A faster runtime alone is not proof of rewrite: cache warming, different concurrency, or noise can explain a timing difference.

## 6.3 Doris: synchronous and asynchronous MVs

- **Synchronous MV:** commonly used for supported single-table rollup/precomputation patterns and maintained as base data changes. It has narrower definition support than async MVs.
- **Asynchronous MV:** a stored result with a refresh policy, supporting broader query patterns including multi-table joins and transparent rewrite when the optimizer determines the MV is valid and useful.

In Doris, the synchronous form is commonly described as a rollup materialized view/index and has narrower single-table capabilities; it is not the same object or refresh model as the asynchronous MV DDL below. Confirm supported aggregate expressions and maintenance behavior for the deployed release.

The exact syntax and supported refresh methods vary by Doris release. Recent Doris documentation describes `BUILD`, `REFRESH`, and scheduled/manual refresh settings; newer releases also document more incremental refresh options. Do not copy an example using `dev` documentation into an older cluster without checking version compatibility.

### Doris asynchronous MV: illustrative shape

```sql
-- Verify syntax against the exact Doris release first.
CREATE MATERIALIZED VIEW daily_revenue_mv_doris
BUILD IMMEDIATE
REFRESH AUTO ON SCHEDULE EVERY 1 HOUR
DISTRIBUTED BY RANDOM BUCKETS 4
PROPERTIES ("replication_num" = "1")
AS
SELECT event_date, product_id, SUM(amount) AS revenue
FROM events_dup
GROUP BY event_date, product_id;
```

If the selected release does not support this exact refresh syntax, use the version-matched DDL documented by Apache Doris. Ensure the MV has completed its build and refresh before testing rewrite.

### Proving a Doris rewrite

```sql
EXPLAIN
SELECT event_date, product_id, SUM(amount) AS revenue
FROM events_dup
GROUP BY event_date, product_id;
```

Inspect the plan for MV rewrite information and the selected scan. Recent Doris versions provide rewrite-status details in EXPLAIN output; exact fields vary. Also inspect MV build/refresh state. If no rewrite occurs, check:
- MV is built and usable.
- The optimizer is enabled/configured as required by that version.
- Query shape, predicates, group-by dimensions, join types, and aggregate functions are compatible.
- The MV has not become stale or invalid.
- Cost-based optimization chooses the MV rather than another plan.

## 6.4 Materialized view decision checklist

Before adding an MV, answer:

1. Which real query is slow and how often does it run?
2. What scan, join, or aggregation work can be precomputed?
3. Which dimensions must remain available for filtering and grouping?
4. What is the required freshness SLA?
5. How are late records, updates, deletes, and backfills represented?
6. How much extra storage and refresh/write compute will it require?
7. How will you prove rewrite and reconcile results to the base data?

Do not create MVs speculatively or use high-cardinality dimensions without estimating result size.

---

# 7. Lakehouse integration and query optimization

## 7.1 External catalogs

An external catalog lets the engine query data managed by another system without first copying all of it into native tables. Supported integrations depend on engine version, catalog type, metadata service, storage credentials, and file format.

Common roadmap formats:
- Hive tables and Hive Metastore.
- Apache Iceberg.
- Delta Lake.
- Apache Hudi.

StarRocks documents external catalogs for Hive, Iceberg, Hudi, and Delta Lake. Apache Doris documents Multi-Catalog support for Hive, Iceberg, Hudi, Delta Lake, and other systems. This does not mean all table operations, snapshots, writes, deletes, or schema evolution features work identically for every format.

**Required components may include:**
- Metadata service such as Hive Metastore, a REST catalog, or a cloud catalog.
- Object storage/HDFS credentials and network access.
- Supported Parquet/ORC reader path.
- Compatible table-format version and metadata features.
- Appropriate catalog configuration and privileges.

### Example: catalog-first query shape

Exact catalog creation properties depend on the chosen metastore, object store, and engine release. Use the official product catalog guide to create a catalog named `iceberg_lake`. Once configured, a query may resemble:

```sql
-- Illustrative only: catalog/database/table names must exist.
SELECT event_date, COUNT(*) AS event_count
FROM iceberg_lake.analytics.events
WHERE event_date >= DATE '2026-01-01'
GROUP BY event_date
ORDER BY event_date;
```

Do not paste credentials into SQL history or a shared notebook. Prefer IAM/workload identity or a secret store when supported; otherwise use restricted configuration files and least-privilege credentials.

## 7.2 Local caching for lakehouse queries

Remote object storage is durable and elastic, but repeated reads can incur request, network, and file-open overhead. Local caching can keep frequently accessed data closer to compute.

**Benefits:** repeated queries over hot data can avoid repeated remote reads.

**Limitations:** cache capacity is finite; cache invalidation, data freshness, cold-start performance, and workload locality matter. Cache behavior may differ across StarRocks shared-data CNs, Doris deployments, and managed services. Do not assume a particular cache is enabled or that an external-catalog query will be cached.

## 7.3 Cost-based optimization and statistics

A cost-based optimizer (CBO) estimates alternatives using row counts, data sizes, distinct values, selectivity, and available statistics. It may choose join order, join distribution, scan predicates, aggregation placement, and other physical plan details.

**Common failure mode:** stale/missing statistics lead to a poor join order or a large table being chosen as a broadcast side.

Actions:
1. Gather statistics using the supported mechanism for the engine/version.
2. Inspect the plan before and after.
3. Validate cardinality estimates against actual row counts.
4. Measure the effect under representative data and concurrency.

Statistics are inputs to decisions, not guarantees of a better plan.

## 7.4 Runtime filters

A runtime filter can be built from the join-key values produced by one side of a join and applied to reduce the rows scanned by the other side. This is especially useful when one side is selective.

It may not help when:
- The build side is large or not selective.
- Filter arrival is too late to avoid much scan work.
- The storage format/scan path cannot apply it efficiently.
- Join keys are skewed or estimates are wrong.

Inspect the actual plan and runtime profile for filter creation and application. A SQL-level `WHERE` clause is not the same thing as a runtime filter.

## 7.5 Vectorized execution and join performance

Vectorized execution processes batches of values rather than invoking a scalar operation for every row. It can improve CPU efficiency, cache locality, and operator throughput.

Join performance depends on:
- Join algorithm and distribution.
- Join key types and compatible encodings.
- Build-side size and memory.
- Network exchanges and skew.
- Statistics and filter selectivity.
- Sorting, partitioning, and data locality.
- Concurrency and resource limits.

A four-table star join is a useful evaluation workload, but it is not a universal benchmark. Use representative table sizes and realistic dimension cardinalities.

---

# 8. Advanced operations and architectural trade-offs

## 8.1 Memory and workload isolation

Hash joins, hash aggregations, sorts, and exchanges consume memory. When memory is insufficient, queries can slow down, spill where supported/configured, fail, or be rejected by resource limits.

Production controls include:
- Query and session limits.
- Workload groups/resource groups where supported by the release.
- Separate capacity or admission policies for dashboards and ETL.
- Monitoring queue time, peak memory, spill bytes, CPU, disk, and network.
- Avoiding uncontrolled fan-out and oversized concurrency.

Use workload isolation to protect interactive latency from long ETL. Isolation is not merely two usernames: prove it through configured resource policies and concurrent load tests.

## 8.2 High availability and operations

- Deploy the supported number of FE nodes and verify quorum/metadata replication behavior for the selected product.
- Monitor BE/CN health, disk space, compaction/maintenance pressure, query failures, and ingestion lag.
- Plan rolling upgrades against the supported compatibility matrix.
- Test backup/restore and disaster recovery rather than assuming replicas replace backups.
- Track schema changes, MV refresh state, and external catalog availability.
- For shared-data deployments, monitor object storage and cache hit/miss metrics in addition to CPU/memory.

## 8.3 Security

- Use least-privilege accounts for load jobs, analysts, and administration.
- Avoid shared admin credentials in application services.
- Protect MySQL and HTTP endpoints with TLS where supported.
- Restrict object-storage and catalog credentials to the required prefixes/catalogs.
- Apply row/column restrictions using supported authorization features or a governed serving layer.
- Audit access to sensitive dimensions and CDC data.
- Rotate secrets and test credential failure/revocation.

Exact authorization capabilities and policy integrations vary by engine edition, release, and deployment. Verify the supported mechanisms rather than assuming compatibility with another engine's plugin.

## 8.4 Managed services and ecosystem

- **CelerData** is associated with commercial StarRocks offerings and managed deployment options.
- **VeloDB** is associated with commercial/managed Apache Doris offerings and ecosystem services.
- Managed offerings may reduce operational burden, but compare service boundaries, region availability, data residency, support SLAs, upgrade control, pricing, network/egress costs, and export/exit paths.
- Evaluate the project's release cadence, issue response, documentation quality, connector compatibility, hiring availability, and support model—not only benchmark claims.

---

# 9. Comparative decision table

| Engine | Strong fit | Storage ownership / data access | Join and update considerations | Main trade-offs |
|---|---|---|---|---|
| **StarRocks** | Interactive analytics, multi-table joins, high concurrency, real-time current-state tables | Native tables; shared-nothing BEs or shared-data CNs on object storage/HDFS; external catalogs | Strong SQL join focus; Primary Key model for upserts; MVs can accelerate compatible queries | Requires table-model and distribution design; cache/object-store behavior matters in shared-data mode |
| **Apache Doris** | BI/reporting, join-heavy SQL, real-time analytics and CDC-fed tables | Native FE/BE storage plus Multi-Catalog external data access; cloud/disaggregated options depend on release | Unique Key model for upserts; synchronous and asynchronous MVs with version-dependent rewrite/refresh | Version-specific features and deployment complexity; test refresh and query rewrite behavior |
| **ClickHouse** | Fast analytical scans, event/log analytics, aggregation-heavy workloads | Primarily its own columnar storage; external access options vary | Joins are supported, but table layout and join strategy matter; update/delete semantics differ from primary-key OLTP tables | MergeTree design, parts/merges, mutation costs, and workload-specific join performance |
| **Trino** | Federated SQL across lakes, databases, and warehouses | Primarily queries data in place through connectors; not a native serving database for all data | Cross-source joins are possible; performance depends on pushdown, source limits, and data movement | Federation can be expensive; no native serving storage model like StarRocks/Doris for every workload |
| **Druid** | Time-oriented event analytics, ingestion-time rollups, selective dashboards | Segmented analytics storage and ingestion pipeline | Excellent fit for supported time/filter/aggregation patterns; general join semantics differ by workload | Data modeling and ingestion choices strongly shape query capability |
| **Pinot** | Low-latency, high-QPS user-facing analytics over streaming/batch data | Segment-based serving architecture | Index-driven filters and aggregations; query semantics and update patterns differ from StarRocks/Doris | Indexing and ingestion complexity; verify join and upsert fit for workload |
| **Cloud warehouse** | Managed BI, broad SQL, ELT and governed enterprise analytics | Managed storage and compute | Broad SQL ecosystem; concurrency/latency/cost depend on service and sizing | Pricing, platform coupling, and operational controls vary by provider |

**Decision rule:** benchmark the query mix you actually operate. A fair comparison uses the same logical data, equivalent result semantics, documented hardware/resources, controlled warm/cold cache conditions, representative concurrency, and measured cost/freshness.

---

# 10. Hands-on lab: `experiments/04_starrocks_doris/`

## 10.1 Lab objective and stages

Create a reproducible experiment directory:

```text
experiments/04_starrocks_doris/
├── README.md
├── data/
│   ├── sales.csv
│   ├── customers.csv
│   ├── products.csv
│   └── regions.csv
├── sql/
│   ├── 01_schema.sql
│   ├── 02_load_smoke.sql
│   ├── 03_star_join.sql
│   └── 04_materialized_view.sql
├── scripts/
│   ├── generate_data.py
│   └── benchmark.py
└── results/
    └── README.md
```

**Required sequence:**
1. Start one engine locally.
2. Create Duplicate Key and Primary/Unique Key tables.
3. Load a tiny dataset and verify semantics.
4. If Kafka is available, configure Routine Load and test an upsert.
5. Run a four-table star-schema join and record measurements.
6. Create an async MV and prove or disprove rewrite using the plan.
7. If an Iceberg catalog is available, query a table and compare the workflow with Trino.
8. Compare ClickHouse only when it is available and use identical logical results.

Do not record invented timings. Save actual command output, version, dataset scale, hardware, cache state, and settings under `results/`.

## 10.2 Start an engine locally

Use the official installation/quick-start documentation for the selected version rather than an unpinned community image. The project documentation and Docker packaging evolve, and a copied Compose file may become invalid.

- StarRocks: <https://docs.starrocks.io/docs/quick_start/>
- Apache Doris: <https://doris.apache.org/docs/get-starting/quick-start/>

Record:
```sql
SELECT VERSION();
SHOW FRONTENDS;
SHOW BACKENDS;
```

For StarRocks shared-data, verify the deployment uses CN nodes and object storage/HDFS. For the initial table-model lab, shared-nothing is simpler because the table DDL and local data placement are easier to reason about.

Set the actual FE host and port from the deployment:

```bash
export OLAP_HOST=127.0.0.1
export OLAP_PORT=9030
export OLAP_USER=lab_user
# Let mysql prompt for password:
mysql --protocol=TCP -h "$OLAP_HOST" -P "$OLAP_PORT" -u "$OLAP_USER" -p
```

Do not assume a default password. Create a dedicated lab user with only the permissions required for the exercise.

## 10.3 Smoke dataset and table models

Create a database:

```sql
CREATE DATABASE IF NOT EXISTS olap_lab;
USE olap_lab;
```

Create a raw event table and a current-state table. Choose the engine-specific DDL below.

### StarRocks schema

```sql
CREATE TABLE IF NOT EXISTS events_dup (
    event_date DATE NOT NULL,
    event_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    amount DECIMAL(12,2) NOT NULL
)
ENGINE=OLAP
DUPLICATE KEY(event_date, event_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS user_state (
    user_id BIGINT NOT NULL,
    city VARCHAR(80),
    source_version BIGINT
)
ENGINE=OLAP
PRIMARY KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");
```

### Apache Doris schema

```sql
CREATE TABLE IF NOT EXISTS events_dup (
    event_date DATE NOT NULL,
    event_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    amount DECIMAL(12,2) NOT NULL
)
DUPLICATE KEY(event_date, event_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS user_state (
    user_id BIGINT NOT NULL,
    city VARCHAR(80),
    source_version BIGINT
)
UNIQUE KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");
```

**Version and cluster notes:** Some releases infer or manage bucket counts differently; replication settings may be invalid on a single-BE deployment unless set to one for a disposable lab. A production cluster should use supported replica placement. The table model and DDL need to be verified against the selected version before using as a template.

Insert a smoke dataset:

```sql
INSERT INTO events_dup VALUES
('2026-01-01', 1, 101, 10, 12.50),
('2026-01-01', 2, 101, 11,  7.50),
('2026-01-01', 3, 102, 10, 20.00),
('2026-01-02', 4, 103, 12,  5.00);

INSERT INTO user_state VALUES
(101, 'Pune', 1),
(102, 'Delhi', 1);
```

Verify:
```sql
SELECT COUNT(*) AS rows_loaded, SUM(amount) AS total_amount
FROM events_dup;

SELECT * FROM user_state ORDER BY user_id;
```

Now write the same key again:

```sql
INSERT INTO user_state VALUES (101, 'Bengaluru', 2);
SELECT * FROM user_state WHERE user_id = 101;
```

**Expected semantic observation:** the current-state table should expose the newer row for key `101` after the write becomes visible. If not, inspect load success, table model, transaction completion, and the selected engine/version. Do not expect the Duplicate Key table to collapse repeated events.

## 10.4 Four-table star-schema join

Create three small dimensions and a fact table (the event table serves as a small fact table in the smoke test):

```sql
CREATE TABLE IF NOT EXISTS customers (
    user_id BIGINT NOT NULL,
    customer_name VARCHAR(100),
    region_id BIGINT
)
ENGINE=OLAP
DUPLICATE KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS products (
    product_id BIGINT NOT NULL,
    product_name VARCHAR(100),
    category VARCHAR(60)
)
ENGINE=OLAP
DUPLICATE KEY(product_id)
DISTRIBUTED BY HASH(product_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");

CREATE TABLE IF NOT EXISTS regions (
    region_id BIGINT NOT NULL,
    region_name VARCHAR(80)
)
ENGINE=OLAP
DUPLICATE KEY(region_id)
DISTRIBUTED BY HASH(region_id) BUCKETS 4
PROPERTIES ("replication_num" = "1");
```

For Doris, use the same column definitions and distribution, but omit `ENGINE=OLAP` and use Doris's supported table DDL. Then load rows:

```sql
INSERT INTO customers VALUES
(101, 'Asha', 1), (102, 'Ravi', 2), (103, 'Meera', 1);

INSERT INTO products VALUES
(10, 'Keyboard', 'Accessories'),
(11, 'Mouse', 'Accessories'),
(12, 'Monitor', 'Displays');

INSERT INTO regions VALUES (1, 'West'), (2, 'North');
```

Join:

```sql
SELECT
    r.region_name,
    p.category,
    COUNT(*) AS event_count,
    SUM(f.amount) AS revenue
FROM events_dup f
JOIN customers c ON f.user_id = c.user_id
JOIN products p ON f.product_id = p.product_id
JOIN regions r ON c.region_id = r.region_id
GROUP BY r.region_name, p.category
ORDER BY revenue DESC;
```

Check correctness by manually calculating the four input rows. Save `EXPLAIN` output. The optimizer may choose a join order different from the written order; SQL text order is not proof of physical execution order.

## 10.5 Generate a larger dataset safely

Start with 10,000 rows, then 100,000, then a size that fits the available memory and storage. Only increase scale after the smoke test is correct.

Suggested generator contract:
- Deterministic random seed.
- `event_id` unique in the generated fact data.
- Skewed and uniform variants for `user_id` and `product_id`.
- Repeatable customer/product/region dimensions.
- Configurable output rows and output directory.
- CSV schema exactly matches the target table.

Example command:
```bash
python scripts/generate_data.py --rows 100000 --seed 42 --out data/
```

Minimal deterministic generator implementation (writes only local CSV files; it does not connect to a database):

```python
#!/usr/bin/env python3
"""Generate deterministic StarRocks/Doris lab data."""
import argparse
import csv
import random
from pathlib import Path
from datetime import date, timedelta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path("data"))
    args = parser.parse_args()
    if args.rows < 1:
        parser.error("--rows must be >= 1")
    rng = random.Random(args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    start = date(2026, 1, 1)
    with (args.out / "events.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for event_id in range(1, args.rows + 1):
            event_date = start + timedelta(days=(event_id - 1) % 90)
            user_id = 1 + (rng.randrange(100) if event_id % 10 else rng.randrange(10_000))
            product_id = 1 + rng.randrange(100)
            amount_cents = rng.randrange(100, 100_000)
            writer.writerow([event_date.isoformat(), event_id, user_id, product_id,
                             f"{amount_cents / 100:.2f}"])
    with (args.out / "customers.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for user_id in range(1, 10_001):
            writer.writerow([user_id, f"customer_{user_id}", 1 + (user_id % 5)])
    with (args.out / "products.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for product_id in range(1, 101):
            writer.writerow([product_id, f"product_{product_id}", f"category_{1 + product_id % 8}"])
    with (args.out / "regions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for region_id in range(1, 6):
            writer.writerow([region_id, f"region_{region_id}"])


if __name__ == "__main__":
    main()
```

This emits `events.csv` columns in the order `event_date,event_id,user_id,product_id,amount`; `customers.csv` columns `user_id,customer_name,region_id`; `products.csv` columns `product_id,product_name,category`; and `regions.csv` columns `region_id,region_name`. The event generator intentionally creates a mix of hot and less-common users. Record the generator version and command. Do not benchmark a tiny smoke dataset and extrapolate it to billions of rows.

## 10.6 Stream Load

For a CSV file, use the engine-specific Stream Load API. The common workflow is:

1. Verify the target table and column order.
2. Generate a unique load label.
3. Send the CSV to the target database/table endpoint with the documented format headers.
4. Inspect HTTP status and JSON response for load state, loaded rows, filtered rows, and error details.
5. Query the table and reconcile row counts.

StarRocks loading guide: <https://docs.starrocks.io/docs/loading/Stream_Load/>  
Doris loading guide: <https://doris.apache.org/docs/data-operate/import/import-way/stream-load-manual/>

Avoid placing a real password in a committed script or shell history. Use the official endpoint behavior for FE redirects, TLS, and authentication. For repeatable retries, use the product's documented label/idempotency semantics.

## 10.7 Routine Load from Kafka and test an upsert

This extension requires a running Kafka broker reachable from the engine. Use the product-specific official guide:
- StarRocks Routine Load: <https://docs.starrocks.io/docs/integrations/streaming/kafka/RoutineLoad/>
- Doris Routine Load: <https://doris.apache.org/docs/data-operate/import/import-way/routine-load-manual/>

Suggested message sequence (JSON or CSV according to the job configuration):
```text
101,Asha,Pune,1
101,Asha,Bengaluru,2
101,Asha,Pune,1
```

Use the engine-specific Kafka target table from Section 5.3. Publish the messages, monitor job state/lag, and query the target table. The third record deliberately tests out-of-order delivery. For Doris, use `user_profile_ordered` to validate the configured sequence column. For StarRocks, test the CDC connector's documented ordering behavior or enforce upstream per-key ordering; do not assume a `source_version` column alone controls conflict resolution.

Record:
- Kafka topic and partition count.
- Job configuration with secrets removed.
- Job status and consumed offsets before/after.
- Time from publish to query visibility.
- Target rows and reconciliation result.
- Behavior after replay or a broker/job restart, if safe to test.

Do not claim exactly-once behavior from the end result alone. Review the engine's documented delivery guarantees, job status, offsets, and replay behavior for the selected version.

## 10.8 Create and verify an asynchronous materialized view

Create the same aggregate query as a materialized view using the exact syntax supported by your selected engine/version. For StarRocks, follow the asynchronous MV documentation: <https://docs.starrocks.io/docs/sql-reference/sql-statements/materialized_view/CREATE_MATERIALIZED_VIEW/>. For Doris, follow: <https://doris.apache.org/docs/query-acceleration/materialized-view/async-materialized-view/functions-and-demands/>.

Target query:
```sql
SELECT
    event_date,
    product_id,
    SUM(amount) AS revenue
FROM events_dup
GROUP BY event_date, product_id;
```

After MV creation:
1. Wait for the build/refresh to finish.
2. Run the target query without naming the MV.
3. Run `EXPLAIN` and save the plan.
4. Confirm a scan of the MV or an explicit rewrite-hit indicator.
5. Compare exact results with the same aggregate over the base table.
6. Insert another row and observe the refresh/visibility behavior.
7. Measure query time only after recording cache state, repetitions, and concurrent load.

**Expected observation:** if the MV definition, data freshness, query shape, and optimizer conditions match, the plan may use the MV. If it does not, record “rewrite not observed” and investigate; do not change the results section to claim success. For async MVs, freshness depends on refresh completion/policy.

## 10.9 Query Iceberg through an external catalog

This extension requires a functioning Iceberg table, metadata catalog, and storage credentials reachable from the engine. Use the official catalog guide for the exact release:
- StarRocks external catalogs: <https://docs.starrocks.io/docs/data_source/catalog/>
- Doris Multi-Catalog: <https://doris.apache.org/docs/key-features/multi-catalog/>

Workflow:
1. Create an Iceberg table using the lab's selected catalog (Hive Metastore, REST, or supported cloud catalog).
2. Configure the StarRocks external catalog or Doris catalog with least-privilege credentials.
3. Confirm the database and table are visible.
4. Query a selective partition/date filter.
5. Run `EXPLAIN`; inspect scan predicates, partitions/files, and remote I/O indicators available in the version.
6. Compare with Trino using the same logical SQL and Iceberg snapshot.
7. Record setup complexity, query latency, data freshness, supported features, and cost. Do not compare results from different snapshots or cache states without stating the difference.

**StarRocks — Iceberg through a Hive Metastore (template):**

```sql
CREATE EXTERNAL CATALOG iceberg_lake
PROPERTIES (
    "type" = "iceberg",
    "iceberg.catalog.type" = "hive",
    "iceberg.catalog.hive.metastore.uris" = "thrift://hive-metastore.example:9083"
);
SHOW DATABASES FROM iceberg_lake;
-- After confirming the real names:
SELECT COUNT(*) FROM iceberg_lake.analytics.events;
```

**Apache Doris — Iceberg through a Hive-compatible metastore (template):**

```sql
CREATE CATALOG iceberg_lake_doris PROPERTIES (
    "type" = "iceberg",
    "iceberg.catalog.type" = "hms",
    "hive.metastore.uris" = "thrift://hive-metastore.example:9083"
);
SHOW DATABASES FROM iceberg_lake_doris;
SELECT COUNT(*) FROM iceberg_lake_doris.analytics.events;
```

These templates intentionally omit object-store authentication because it depends on S3-compatible, cloud, or HDFS storage and catalog type. Configure storage credentials/roles, endpoint, region, TLS, and any required Hadoop settings using the exact product release's documentation; do not place secrets in source control. The catalog name is not proof of compatibility: validate the actual Iceberg table version, metadata format, catalog API, storage access from all relevant nodes, and supported operations. StarRocks has separate Hive, Iceberg, Hudi, Delta Lake, and unified catalog paths; Doris uses Multi-Catalog connectors. Neither engine's support for one format/catalog implies identical support for all table features, write operations, caching, or MV rewrite.

Example query shape:
```sql
SELECT event_date, COUNT(*) AS n
FROM iceberg_lake.analytics.events
WHERE event_date >= DATE '2026-01-01'
GROUP BY event_date;
```

The identifier `iceberg_lake.analytics.events` is illustrative. Replace it with the actual catalog/database/table names. Some external catalog operations are read-only or have restrictions; verify before attempting writes.

## 10.10 Compare against ClickHouse

Only run this step if ClickHouse is available and the same logical dataset can be loaded into it.

Fair comparison procedure:
1. Use identical logical rows, types, filters, and result semantics.
2. Run correctness checks first.
3. Benchmark the same four-table join and aggregate.
4. Warm up the engines separately; record cold-cache and warm-cache runs independently.
5. Run at least 5–10 repetitions for each condition and report median plus p95 if sample size supports it.
6. Record concurrency (for example 1 and 10 clients), CPU/RAM/disk, storage mode, replica count, data size, engine versions, and query settings.
7. Avoid simultaneous uncontrolled background ingestion during latency measurements.
8. Report load time and storage size alongside query latency.
9. Do not compare one engine's warm cache to another engine's cold cache.

Results template:

| Engine/version | Rows | Query | Cache state | Concurrency | p50 ms | p95 ms | Correct result? | Notes |
|---|---:|---|---|---:|---:|---:|---|---|
| StarRocks or Doris | | 4-table join | | 1 | | | | |
| ClickHouse | | 4-table join | | 1 | | | | |

Leave cells blank until measurements are actually collected.

## 10.11 What counts as evidence?

| Claim | Evidence required |
|---|---|
| An upsert worked | Query result shows one current row per key and the intended version/value |
| Kafka ingestion is healthy | Job state, offsets/lag, accepted/rejected rows, target reconciliation |
| MV was used | `EXPLAIN`/profile shows MV scan or supported rewrite indicator |
| Runtime filter helped | Plan/profile indicates filter creation/application and measurable reduced input work |
| Colocation reduced shuffling | Physical plan confirms colocated/local join behavior and measurements support improvement |
| Query became faster | Repeated, controlled measurements with hardware, data size, and cache state recorded |
| Lakehouse table is queried in place | External catalog/table reference and plan show external scan; no native-copy step in the experiment |

## 10.12 Troubleshooting

| Symptom | Likely causes | Checks and remedies |
|---|---|---|
| Client cannot connect | Wrong FE endpoint/port, container port not published, service not healthy | Verify service logs, endpoint, protocol, port, and network path |
| `CREATE TABLE` fails | Syntax/version mismatch, invalid partition expression, replication count too high | Check engine version and table-model guide; use valid replica count |
| Load rejected | Wrong delimiter/schema, invalid types, missing privilege, bad label or endpoint | Inspect HTTP response/job details and rejected-row messages |
| Upsert appears not to work | Duplicate Key model, key mismatch, load still running, wrong column mapping | Inspect DDL, target key, job status, and loaded rows |
| Older CDC event overwrites newer state | No sequence/order rule, tied versions, unordered source delivery | Configure supported sequence semantics and test out-of-order replay |
| Routine Load paused | Kafka unreachable, offsets out of range, auth/TLS error, malformed records | Inspect job state, Kafka logs, topic offsets, network and credentials |
| MV not selected | Build incomplete, stale/invalid MV, incompatible query shape, optimizer config, cost model | Check MV state, EXPLAIN rewrite details, definition, freshness and stats |
| Join unexpectedly slow | Bad estimates, skew, large build side, data exchange, missing filters | Inspect plan/profile, cardinality, join distribution, runtime filters, and skew |
| External Iceberg table unavailable | Catalog URI/metadata service, storage credentials, format/version incompatibility | Validate metadata access and credentials from engine nodes; consult format-specific guide |
| Benchmark results fluctuate | Cache state, concurrent load, thermal/resource variation, too few repetitions | Separate cold/warm tests, repeat, capture resource telemetry, and report variance |

---

# 11. Checkpoints and common mistakes

## Checkpoint A — explain the architecture

Without notes, explain:
- FE versus BE responsibilities.
- Why StarRocks CN exists in shared-data architecture.
- What moves across the network during a distributed join.
- Why storage-compute separation can improve elasticity but may add remote-read cost.

## Checkpoint B — choose the table model

For each scenario, choose a model and justify it:
1. Immutable clickstream events where duplicates are meaningful.
2. Daily revenue totals by date and product.
3. Customer profile CDC with repeated updates to the same ID.
4. A table that must preserve full event history and support later deduplication.

## Checkpoint C — prove query optimization

- Can you show the selected join order and distribution in `EXPLAIN`?
- Can you show whether a runtime filter is actually applied?
- Can you show that an MV is used rather than merely created?
- Can you distinguish lower latency due to rewrite from cache warming?

## Checkpoint D — evaluate a production design

Document:
- Target latency and concurrency.
- Data volume, ingestion rate, and freshness SLA.
- Update/delete semantics.
- Storage mode and availability design.
- Required catalog formats and query shapes.
- Operational skills and support expectations.
- Expected costs and migration/exit plan.

## Common mistakes

1. **Choosing based on a benchmark headline.** Benchmarks must match the production query mix and resource configuration.
2. **Using Duplicate Key for current-state data.** It preserves repeated rows; it does not provide uniqueness.
3. **Using Primary/Unique Key when history is required.** Upserts collapse current state; preserve a separate event/history table if needed.
4. **Ignoring out-of-order CDC.** Arrival order may not equal source commit order.
5. **Assuming identical SQL behavior across StarRocks and Doris.** Syntax, defaults, table-model details, MV refresh, and connector support differ.
6. **Assuming MV creation implies rewrite.** Build state, query shape, freshness, and cost-based choices all matter.
7. **Over-partitioning or over-bucketing.** Excess metadata and tiny data units can hurt performance.
8. **Ignoring skew.** A single hot key can dominate a distributed join or aggregation.
9. **Treating cache as a guarantee.** Cold cache, node churn, and remote storage can change latency materially.
10. **Ignoring operational maturity.** Documentation, release cadence, incident response, upgrades, hiring, and managed-service support affect TCO.

---

# 12. Final revision checklist

- [ ] I can explain StarRocks and Doris architecture separately.
- [ ] I can distinguish StarRocks BE and CN roles.
- [ ] I can choose Duplicate, Aggregate, and Primary/Unique Key models from semantics.
- [ ] I can explain sort keys, prefix indexes, partitions, buckets, and colocation.
- [ ] I can load a smoke dataset and verify row counts and aggregates.
- [ ] I can test a repeated key and an out-of-order CDC update.
- [ ] I can explain Stream Load versus Routine Load and CDC pipeline responsibilities.
- [ ] I can create an MV, check freshness, and prove or disprove query rewrite.
- [ ] I can query a lakehouse table through a supported external catalog.
- [ ] I can inspect join plans, statistics, and runtime-filter evidence.
- [ ] I can benchmark fairly without inventing results.
- [ ] I can justify the selected engine against ClickHouse, Trino, Druid, and Pinot.

---

# References

The official documentation is the authority for version-specific syntax. Use the documentation version that matches your deployed release.

## Project syllabus
- `Roadmap_ptree.md` — target path and neighboring modules.
- `roadmap-Real-Time-OLAP-and-Query-Engines.md` — Topic 04 concepts, lab, checkpoint, and common mistakes.

## StarRocks
- [Architecture](https://docs.starrocks.io/docs/introduction/Architecture/)
- [Duplicate Key tables](https://docs.starrocks.io/docs/table_design/table_types/duplicate_key_table/)
- [Primary Key tables](https://docs.starrocks.io/docs/table_design/table_types/primary_key_table/)
- [Change data through loading](https://docs.starrocks.io/docs/loading/Load_to_Primary_Key_tables/)
- [Stream Load](https://docs.starrocks.io/docs/loading/Stream_Load/)
- [Routine Load](https://docs.starrocks.io/docs/integrations/streaming/kafka/RoutineLoad/)
- [External catalogs](https://docs.starrocks.io/docs/data_source/catalog/)
- [Create materialized view](https://docs.starrocks.io/docs/sql-reference/sql-statements/materialized_view/CREATE_MATERIALIZED_VIEW/)
- [Bloom-filter indexes](https://docs.starrocks.io/docs/table_design/indexes/Bloomfilter_index/)
- [Colocate joins](https://docs.starrocks.io/docs/using_starrocks/Colocate_join)
- [Iceberg catalog](https://docs.starrocks.io/docs/data_source/catalog/iceberg/)
- [Asynchronous MV query rewrite](https://docs.starrocks.io/docs/using_starrocks/async_mv/use_cases/query_rewrite_with_materialized_views/)

## Apache Doris
- [Getting started / quick start](https://doris.apache.org/docs/get-starting/quick-start/)
- [Data model overview](https://doris.apache.org/docs/dev/key-features/data-model/)
- [Unique Key model](https://doris.apache.org/docs/dev/key-features/unique-key/)
- [Routine Load](https://doris.apache.org/docs/dev/data-operate/import/import-way/routine-load-manual/)
- [Stream Load](https://doris.apache.org/docs/data-operate/import/import-way/stream-load-manual/)
- [Multi-Catalog](https://doris.apache.org/docs/dev/key-features/multi-catalog/)
- [Iceberg catalog](https://doris.apache.org/docs/4.x/lakehouse/catalogs/iceberg-catalog/)
- [Bitmap index](https://doris.apache.org/docs/dev/table-design/index/bitmap-index)
- [BloomFilter index](https://doris.apache.org/docs/dev/table-design/index/bloomfilter/)
- [Async materialized views](https://doris.apache.org/docs/dev/query-acceleration/materialized-view/async-materialized-view/functions-and-demands/)
- [Async MV overview and refresh](https://doris.apache.org/docs/dev/query-acceleration/materialized-view/async-materialized-view/overview/)

## Comparative reading
- [Trino documentation](https://trino.io/docs/current/)
- [ClickHouse documentation](https://clickhouse.com/docs)
- [Apache Druid documentation](https://druid.apache.org/docs/latest/)
- [Apache Pinot documentation](https://docs.pinot.apache.org/)

---

## Verification note

This lesson has been reviewed for syllabus coverage, internal consistency, and obvious SQL/configuration hazards. No live StarRocks, Doris, Kafka, Iceberg, Trino, or ClickHouse runtime was available for this authoring pass; therefore no commands, query rewrites, ingestion guarantees, or benchmark results are claimed as executed. Validate all version-sensitive examples against the exact product release and run the smoke test before using any pattern in production.
