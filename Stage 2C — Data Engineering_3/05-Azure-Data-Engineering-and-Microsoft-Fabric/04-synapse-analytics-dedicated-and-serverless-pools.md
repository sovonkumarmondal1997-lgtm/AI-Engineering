# Synapse Analytics: Dedicated and Serverless SQL Pools

> **Roadmap position:** Stage 2C — Data Engineering_3 → `05-Azure-Data-Engineering-and-Microsoft-Fabric/04-synapse-analytics-dedicated-and-serverless-pools.md`  
> **Level:** Beginner → advanced  
> **Primary focus:** Querying lake data with serverless SQL, modeling and loading a dedicated MPP warehouse, operational performance, cost control, and informed migration decisions to Microsoft Fabric.

## 1. Purpose, prerequisites, and learning objectives

Azure Synapse Analytics remains relevant because many enterprises operate existing Synapse workspaces, dedicated SQL pools, serverless SQL endpoints, Spark jobs, and Synapse pipelines. Microsoft Fabric is a strategic unified analytics platform, but that does not make every Synapse workload an automatic or immediate migration. Engineers need to maintain existing systems, measure their behavior, and make migration decisions from evidence.

This lesson follows Topic 04 of `roadmap-Azure-Data-Engineering-and-Microsoft-Fabric.md`. It does not attempt to teach every Synapse feature or replace the dedicated Fabric lesson later in the roadmap.

### Prerequisites

You should be comfortable with:

- SQL and basic T-SQL (`SELECT`, joins, aggregates, DDL, and permissions).
- ETL/ELT concepts and orchestration from the Azure Data Factory lesson.
- ADLS Gen2 paths, Parquet, partitions, and medallion-style storage.
- Basic Spark concepts and cloud identity/networking.
- The distinction between storage, compute, and orchestration.

### Learning objectives

By the end, you should be able to:

1. Explain the Synapse workspace and its SQL, Spark, and pipeline components.
2. Choose serverless or dedicated SQL for a workload and explain the billing model.
3. Query Parquet in ADLS with `OPENROWSET`, external data sources, views, and `filepath()`.
4. Design dedicated tables using hash, round-robin, and replicated distributions, partitions, and clustered columnstore indexes.
5. Load data with `COPY INTO`, understand PolyBase and CTAS, and diagnose data movement.
6. Inspect DMVs, skew, statistics, workload management, and result-set caching.
7. Integrate Spark and pipelines without confusing orchestration with execution.
8. Compare Synapse with Fabric and build a migration decision based on workload fit, feature gaps, risk, and current Microsoft guidance.

## 2. The workspace mental model

A Synapse workspace is a management and development boundary, not one single compute engine. Synapse Studio is the browser-based authoring and monitoring experience. The workload you submit determines which compute system executes it.

```text
                         Synapse workspace
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
  Serverless SQL             Dedicated SQL              Apache Spark
  query lake files           MPP warehouse              notebooks/jobs
        |                         |                         |
        +-------------------------+-------------------------+
                                  |
                     ADLS Gen2 / external systems
                                  |
                    Synapse pipelines orchestrate work
```

The diagram is conceptual. Workspace capabilities, networking, identities, and linked-service configuration determine which resources can reach which data.

### Major components

- **Serverless SQL pool:** a logical SQL endpoint for querying supported files in a lake without provisioning a dedicated warehouse. Compute is managed by the service; users pay based on data processed under the applicable pricing model.
- **Dedicated SQL pool:** a provisioned MPP data warehouse with a selected DWU service level. Data is distributed across 60 distributions. Compute can be scaled and paused; stored data remains and storage charges continue while paused.
- **Apache Spark pools:** managed Spark compute for notebooks and Spark jobs. Useful for distributed engineering, complex transformations, and workloads not naturally expressed as SQL.
- **Synapse pipelines:** orchestration for activities such as copy, notebook execution, stored procedures, and control flow. Pipelines coordinate engines; they are not themselves a query engine.
- **Synapse Studio:** workspace interface for developing SQL scripts/notebooks/pipelines, browsing data, and monitoring runs.
- **Linked services:** connection definitions to storage, databases, and compute endpoints. They may use managed identity, service principals, or other supported authentication methods; avoid embedded secrets.
- **Lake storage:** ADLS often remains the source of truth for raw and curated files. Serverless SQL can expose a logical relational layer over those files; dedicated SQL physically loads data into warehouse tables.

## 3. Serverless vs dedicated SQL pool

| Dimension | Serverless SQL pool | Dedicated SQL pool |
|---|---|---|
| Main purpose | Ad hoc SQL over lake files, exploration, virtual/logical warehouse views | Predictable, repeatable warehouse workloads and curated relational serving |
| Provisioned compute | No dedicated warehouse capacity to manage | Choose a DWU service level; scale up/down and pause/resume |
| Typical billing driver | Amount of data processed by queries, subject to current pricing and configuration | Compute while running plus storage and other applicable charges |
| Data location | Reads external files in the lake | Stores loaded data in distributed warehouse tables; can also read external data for supported patterns |
| Table distribution | Not applicable to lake files as dedicated SQL distribution | Hash, round-robin, or replicated |
| Best fit | Infrequent queries, discovery, lake views, lightweight serving | Frequent scans/joins/aggregations, concurrency needs, predictable latency, curated dimensional models |
| Main tuning levers | Parquet, projected columns, file layout, partition elimination, filters, path design | Distribution, columnstore, partitions, statistics, DWUs, workload management, data movement |
| Cost risk | Repeated wide scans, poor file layout, unexpected query volume | Leaving compute running, overprovisioning, inefficient data movement, excess concurrency |

**Decision rule:** if data already sits in a well-organized lake and queries are intermittent, start by evaluating serverless SQL. If the same large analytical queries run repeatedly under concurrency or predictable service expectations, benchmark a dedicated pool. Neither choice is automatically cheaper; query frequency, data scanned, data layout, concurrency, and operational requirements decide.

Serverless SQL is not “free SQL,” and dedicated SQL is not billed only for query execution. Check the current regional pricing page before estimating spend. Storage and networking charges can be separate from compute charges.

## 4. Serverless SQL over ADLS

### 4.1 Prerequisites and permissions

You need a Synapse workspace with the serverless SQL endpoint, an ADLS Gen2 account containing readable Parquet files, and network access between the workspace and storage. For private storage, configure the required managed virtual network/private endpoints and DNS/network rules as applicable.

A common managed-identity pattern is:

1. Grant the workspace managed identity an appropriate storage data role, commonly **Storage Blob Data Reader** for read-only access, scoped as narrowly as possible.
2. In the serverless SQL database, create a database-scoped credential for the workspace identity.
3. Create an external data source pointing at the storage account/container.
4. Grant SQL callers the SQL-layer permissions required for the selected access pattern. For `OPENROWSET` with a credential-backed data source, this includes `REFERENCES` on the database-scoped credential and `ADMINISTER DATABASE BULK OPERATIONS` (or an equivalent supported permission). For an external table, callers need `SELECT` on the table and `REFERENCES` on the credential used by its data source.

Example grants (run as an administrator in the serverless user database; replace the principal and grant only to the intended lab reader):

```sql
GRANT REFERENCES ON DATABASE SCOPED CREDENTIAL::WorkspaceIdentity TO [<sql-user>];
GRANT ADMINISTER DATABASE BULK OPERATIONS TO [<sql-user>];
```

These SQL permissions do not grant storage permissions by themselves. Conversely, storage RBAC/ACLs do not grant SQL database permissions. Because the shared workspace identity can read the files permitted to it, limit its storage scope and do not expose the credential-backed data source to untrusted SQL users. Exact identity setup varies with workspace, storage firewall, and private endpoint design. The examples are templates, not a full infrastructure deployment.

```sql
-- Run in the serverless SQL database with sufficient permissions.
-- The workspace managed identity must already have storage data access.
CREATE DATABASE SCOPED CREDENTIAL WorkspaceIdentity
WITH IDENTITY = 'Managed Identity';
GO

CREATE EXTERNAL DATA SOURCE LakeData
WITH (
    LOCATION = 'https://<storage-account>.dfs.core.windows.net/<container>',
    CREDENTIAL = WorkspaceIdentity
);
GO
```

Replace placeholders. Do not paste account keys or long-lived secrets into notebooks or SQL scripts. For a public or differently authenticated source, the configuration may differ; prefer managed identity for Azure-to-Azure access when supported.

### 4.2 Query Parquet with `OPENROWSET`

`OPENROWSET` lets serverless SQL infer or use the schema for a supported file format. Use a path relative to the external data source when `DATA_SOURCE` is specified.

```sql
SELECT TOP (100)
    SalesId,
    CustomerKey,
    OrderDate,
    SalesAmount
FROM OPENROWSET(
    BULK 'curated/sales/year=*/month=*/*.parquet',
    DATA_SOURCE = 'LakeData',
    FORMAT = 'PARQUET'
) AS sales;
```

This assumes the Parquet files have compatible column names/types. If schema inference is ambiguous or columns need explicit types, use a `WITH (...)` schema clause supported by the selected format and current endpoint syntax. `TOP` is not a promise that the engine reads only a small fraction of the underlying files; design paths and predicates to reduce scanning.

### 4.3 Projection pushdown and scan reduction

Compare these queries on the same data and record bytes processed in Synapse monitoring. Do not assume a fixed percentage improvement.

```sql
-- Wide scan: reads all columns needed to materialize every column.
SELECT *
FROM OPENROWSET(
    BULK 'curated/sales/year=*/month=*/*.parquet',
    DATA_SOURCE = 'LakeData', FORMAT = 'PARQUET'
) AS s;

-- Narrow scan: request only columns used by the report.
SELECT CustomerKey, SUM(SalesAmount) AS Revenue
FROM OPENROWSET(
    BULK 'curated/sales/year=*/month=*/*.parquet',
    DATA_SOURCE = 'LakeData', FORMAT = 'PARQUET'
) AS s
GROUP BY CustomerKey;
```

Parquet is columnar, so the engine can often skip unused columns. Actual bytes processed depend on the schema, file metadata, compression, filters, and query plan. Avoid `SELECT *` in stable production views unless all columns are deliberately part of the contract.

### 4.4 Partition elimination with `filepath()`

A lake may store files like:

```text
curated/sales/year=2025/month=01/part-000.parquet
curated/sales/year=2025/month=02/part-000.parquet
curated/sales/year=2026/month=01/part-000.parquet
```

Use wildcard paths and `filepath()` to expose path segments. The ordinal depends on the wildcard structure; verify the returned values before relying on them.

```sql
SELECT
    filepath(1) AS year_folder,
    filepath(2) AS month_folder,
    SUM(SalesAmount) AS Revenue
FROM OPENROWSET(
    BULK 'curated/sales/year=*/month=*/*.parquet',
    DATA_SOURCE = 'LakeData', FORMAT = 'PARQUET'
) AS s
WHERE filepath(1) = '2025'
  AND filepath(2) = '02'
GROUP BY filepath(1), filepath(2);
```

A path predicate can restrict which folders/files are considered. Test the exact wildcard layout and `filepath()` indexing against your data; do not copy ordinal assumptions across different path patterns. If possible, keep partition columns represented consistently in file paths and data schema.

### 4.5 External tables and secure views

External tables give a lake path a relational object name. They are useful for stable interfaces, but schema and path behavior still depend on the external files. A common pattern uses an external data source, a file format, and an external table.

```sql
CREATE EXTERNAL FILE FORMAT ParquetFormat
WITH (FORMAT_TYPE = PARQUET);
GO

CREATE EXTERNAL TABLE dbo.SalesLake
(
    SalesId       BIGINT,
    CustomerKey   INT,
    OrderDate     DATE,
    SalesAmount   DECIMAL(12,2)
)
WITH
(
    LOCATION = 'curated/sales/**',
    DATA_SOURCE = LakeData,
    FILE_FORMAT = ParquetFormat
);
GO
```

For serverless SQL, the `/**` suffix makes the external table scan nested folders. A manually created external table over partitioned folders does **not** automatically expose folder names as partition columns or guarantee folder partition elimination; use `OPENROWSET` with `filepath()` or a supported partitioned-view/Spark-synchronized-table pattern when path-based pruning is required. The example uses a simple recursive scan, not a partition-aware external-table design.

External-table syntax and supported options vary by SQL endpoint and feature; validate the statement in the target serverless database before standardizing it. Do not create an external table until the file schema and location are understood.

A view can expose a curated projection and apply filters. If the `reporting` schema does not already exist, create it first (do not rerun this statement if the schema already exists):

```sql
CREATE SCHEMA reporting;
GO
```

Then create the view:

```sql
CREATE VIEW reporting.vw_SalesSummary
AS
SELECT CustomerKey, OrderDate, SUM(SalesAmount) AS Revenue
FROM dbo.SalesLake
GROUP BY CustomerKey, OrderDate;
GO
```

After `dbo.SalesLake` exists, grant the intended readers access to it, for example `GRANT SELECT ON OBJECT::dbo.SalesLake TO [<sql-user>];`. A view is not automatically a security boundary. Grant only intended permissions, review ownership chaining and underlying object access behavior, and test access using a least-privileged identity. If different consumers must see different rows/columns, implement and test an explicit security design rather than relying on a view name alone.

### 4.6 Serverless cost and limits

- Reduce bytes scanned by using Parquet, selected columns, explicit predicates, and useful folder partitioning.
- Avoid repeated full scans when a curated result or dedicated warehouse would serve the same data more efficiently.
- Configure the serverless SQL pool's **data-processed cost control** in Synapse Studio or with the supported stored procedure. For example, the following illustrative budgets are measured in TB of data processed; choose values appropriate to your own workload and budget:

```sql
EXEC sp_set_data_processed_limit @type = N'daily',   @limit_tb = 1;
EXEC sp_set_data_processed_limit @type = N'weekly',  @limit_tb = 2;
EXEC sp_set_data_processed_limit @type = N'monthly', @limit_tb = 5;

SELECT * FROM sys.configurations WHERE name LIKE 'Data processed %';
SELECT * FROM sys.dm_external_data_processed;
```

The values above are examples, not recommendations or measured usage. If a query crosses a configured limit while it is running, the in-flight query is **not** terminated; subsequent queries can be rejected after the limit is exceeded. This is a service cost-control mechanism, not a per-query cancellation guarantee or a complete Azure subscription budget.
- Large numbers of tiny files, skewed file sizes, storage throttling, and poorly partitioned paths can increase latency.
- Data processed includes more than compressed source bytes in some cases (for example, metadata and intermediate results), and each query has a minimum/rounding rule. Use service monitoring and current pricing rules rather than equating billable data with compressed file size.

## 5. Dedicated SQL pool architecture and design

### 5.1 MPP, DWUs, and pause/resume

Dedicated SQL pool is a massively parallel processing warehouse. A control node parses and coordinates requests, while compute nodes process work over 60 distributions. Data movement services redistribute or broadcast rows when operators need rows co-located for joins or aggregations.

DWUs represent a service-level capacity choice, not a direct promise of a specific query duration. More DWUs may improve parallelism, memory, or concurrency, but cannot compensate for every poor distribution or query design. Benchmark representative workloads at controlled service levels.

Pause stops dedicated compute billing while leaving warehouse data persisted; storage charges continue, and resume takes time. Pausing is useful for dev/test or scheduled workloads with predictable idle windows. It is not suitable when the service must respond continuously with low startup latency. Automate pause/resume only with clear ownership, dependency handling, and failure alerts.

### 5.2 Distribution strategies

A dedicated pool uses 60 distributions. Choose a distribution for the workload, not as a universal default.

| Strategy | How rows are placed | Appropriate use | Main trade-off |
|---|---|---|---|
| `HASH(column)` | Rows with the same hash key land in the same distribution | Large fact tables frequently joined or aggregated on a suitable key | Low-cardinality or uneven keys create skew; a wrong key causes movement |
| `ROUND_ROBIN` | Rows are spread without key-based placement | Staging, quick loads, or tables without a strong access pattern | Joins commonly require redistribution; often a poor final design for large facts |
| `REPLICATE` | A full copy is available on each compute node | Small dimensions/lookups used in joins | Replication storage/maintenance cost; avoid for large or frequently changed tables |

A good hash key has high cardinality, reasonably even frequency, and is used in joins/aggregations. The most common business identifier is not necessarily the best key. Validate row counts by distribution and test joins under realistic data. Skew means some distributions hold or process far more data than others, limiting parallel performance.

```sql
CREATE TABLE dbo.FactSales_Hash
(
    SalesId       BIGINT NOT NULL,
    CustomerKey   INT NOT NULL,
    ProductKey    INT NOT NULL,
    OrderDate     DATE NOT NULL,
    SalesAmount   DECIMAL(12,2) NOT NULL
)
WITH
(
    DISTRIBUTION = HASH(CustomerKey),
    CLUSTERED COLUMNSTORE INDEX
);

CREATE TABLE dbo.FactSales_RoundRobin
(
    SalesId       BIGINT NOT NULL,
    CustomerKey   INT NOT NULL,
    ProductKey    INT NOT NULL,
    OrderDate     DATE NOT NULL,
    SalesAmount   DECIMAL(12,2) NOT NULL
)
WITH
(
    DISTRIBUTION = ROUND_ROBIN,
    HEAP
);
```

These are alternative lab tables. A heap is shown for a load/staging comparison; for an analytical fact table, clustered columnstore is commonly a strong starting point, but confirm row count and workload suitability.

### 5.3 Partitioning and clustered columnstore

Partitioning divides a table into logical ranges, often by date. It can help manage retention and enable partition elimination when queries filter on the partition column. It does not automatically make a query faster: too many tiny partitions or partitioning on an infrequently filtered column can hurt manageability and performance.

Clustered columnstore indexes compress columnar data and support large analytical scans and aggregations. They are usually appropriate for sizable fact tables. Small tables, narrow lookup patterns, and tiny batches may need different indexing. Small rowgroups reduce compression and scan efficiency; load design and batch sizes matter.

Design sequence:

1. Understand the queries and joins.
2. Select a distribution key based on cardinality, skew, and join patterns.
3. Select a partition key only when pruning/maintenance needs justify it.
4. Choose columnstore or another index/heap based on table size and access pattern.
5. Load representative data, inspect movement/skew, and measure again.

## 6. Loading with COPY INTO, PolyBase, and CTAS

### 6.1 `COPY INTO`

`COPY INTO` is a preferred high-throughput ingestion option for many dedicated SQL pool workloads. Prepare appropriately sized files and ensure storage is reachable and authorized. The example assumes a CSV directory whose columns match the target table order.

```sql
COPY INTO dbo.FactSales_Hash
FROM 'https://<storage-account>.dfs.core.windows.net/<container>/sales-csv/'
WITH
(
    FILE_TYPE = 'CSV',
    CREDENTIAL = (IDENTITY = 'Managed Identity'),
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0A',
    FIRSTROW = 2,
    ENCODING = 'UTF8'
);
```

Before running it, configure the workspace identity and storage authorization according to the target configuration. Replace placeholders. CSV quoting, line endings, column mapping, and data types must match the actual files. This is a focused example, not a complete production loader with rejection handling, deduplication, audit logging, or transactional orchestration.

For a hash-vs-round-robin comparison, load the same input into separate empty tables, validate row counts and totals, then run the same join/aggregation against both. Repeat enough times to reduce one-off noise; do not fabricate or generalize benchmark results from a tiny sample.

### 6.2 PolyBase

PolyBase is an external-data loading/query mechanism historically used for high-throughput loading from supported external sources. It relies on external objects and appropriate credentials/file formats. Choose it when the existing architecture or specific source pattern benefits from it, but evaluate `COPY INTO` first for a straightforward new load. Availability and behavior depend on file type, source, endpoint, and configuration; check current Synapse documentation for the exact scenario.

### 6.3 CTAS

`CREATE TABLE AS SELECT` (CTAS) creates a new table from a query result. It is useful for transforming, filtering, or redistributing data in parallel, including staging-to-final patterns.

```sql
CREATE TABLE dbo.FactSales_Curated
WITH
(
    DISTRIBUTION = HASH(CustomerKey),
    CLUSTERED COLUMNSTORE INDEX
)
AS
SELECT
    SalesId,
    CustomerKey,
    ProductKey,
    OrderDate,
    SalesAmount
FROM dbo.FactSales_Hash
WHERE SalesAmount >= 0;
```

The source table and columns must exist, and the query must be valid for dedicated SQL pool. CTAS is a table creation operation, not an automatic upsert. Plan table swaps/renames and cleanup explicitly, and validate constraints, permissions, statistics, and downstream dependencies after materialization.

## 7. Data movement, statistics, workload management, and caching

### 7.1 Understand data movement

The engine may move rows so each distribution can perform a join or aggregation. Common movement concepts include:

- **ShuffleMove:** rows are redistributed across distributions, commonly for a join/aggregate that requires another distribution key.
- **BroadcastMove:** a smaller input is copied to distributions to join locally with another input.
- **Partition movement:** rows are moved as part of an operation involving partitions or data placement.

Data movement is not always a defect; it is a cost the optimizer judged necessary. The goal is to avoid excessive or repeated movement where a compatible distribution can make the operation local.

Use the graphical execution plan in supported clients and dedicated-pool DMVs. For example:

```sql
-- Recent requests (run in the dedicated SQL pool).
SELECT TOP (50)
    request_id,
    status,
    submit_time,
    start_time,
    end_time,
    total_elapsed_time,
    command
FROM sys.dm_pdw_exec_requests
ORDER BY submit_time DESC;

-- After identifying a request_id, inspect its steps.
SELECT
    request_id,
    step_index,
    operation_type,
    distribution_type,
    status,
    row_count,
    command
FROM sys.dm_pdw_request_steps
WHERE request_id = '<request-id>'
ORDER BY step_index;
```

Use the actual request ID from the previous query. DMV visibility depends on permissions and request retention. Look for large movement steps, row counts, long-running steps, and repeated redistribution. Correlate with table distribution and query shape rather than blindly changing the distribution key.

### 7.2 Skew analysis

For a quick table-space view, run the supported dedicated-pool command:

```sql
DBCC PDW_SHOWSPACEUSED ('dbo.FactSales_Hash');
```

Review per-distribution row counts and space. For deeper analysis, use supported system views/DMVs for the target Synapse version and permissions. Investigate keys with low cardinality, highly uneven values, null/default concentration, and join keys that differ between tables.

### 7.3 Statistics

Statistics help the optimizer estimate cardinality and choose join/order strategies. Stale or missing statistics can lead to poor plans, unexpected movement, and bad resource choices. Maintain statistics after substantial loads or distribution changes using supported `UPDATE STATISTICS`/automatic statistics behavior for the target dedicated pool. Validate whether automatic statistics is enabled and use current product guidance for large tables; avoid assuming every statistics operation is cheap or required after every small insert.

### 7.4 Workload groups and classifiers

Workload management isolates resources and classifies requests. A workload group defines resource allocation; a classifier routes matching requests into a group and can assign importance. Configuration requires the dedicated pool to be online and suitable database permissions. Test syntax and allowed values in the chosen pool configuration.

Illustrative pattern (resource percentages must fit the pool's configuration and other groups):

```sql
CREATE WORKLOAD GROUP DataLoads
WITH
(
    MIN_PERCENTAGE_RESOURCE = 10,
    CAP_PERCENTAGE_RESOURCE = 40,
    REQUEST_MIN_RESOURCE_GRANT_PERCENT = 5
);
GO

-- The database principal must exist; replace etl_user with a real user.
CREATE WORKLOAD CLASSIFIER DataLoadsClassifier
WITH
(
    WORKLOAD_GROUP = 'DataLoads',
    MEMBERNAME = 'etl_user',
    IMPORTANCE = NORMAL
);
GO
```

Treat this as an example to adapt, not a drop-in production configuration. Resource percentages interact with the workload-management configuration, and a resource reservation can reduce capacity available to other groups. Create a dedicated SQL user/group for the intended workload; avoid classifying every query through an overly broad identity.

### 7.5 Result-set caching

Dedicated SQL pool can cache results for eligible repeated queries. It may reduce repeated compute work, but it is not a universal accelerator: exact-query and data/schema validity rules apply, nondeterministic queries and certain security patterns may not be cached, and large result sets can create control-node pressure. It is disabled by default at database/session levels in documented configurations; verify current behavior and configuration before depending on it.

Use `sys.dm_pdw_exec_requests` and its result-cache indicators where supported to investigate hits/misses. Do not enable caching without considering freshness requirements, security, and query result size. Pausing a pool does not itself empty the result-set cache.

## 8. Spark, notebooks, linked services, and pipelines

Synapse Spark is appropriate when transformations need distributed Python/Scala/Spark SQL, complex semi-structured processing, custom libraries, or engineering patterns that are awkward in SQL. Notebooks and Spark job definitions run on Spark pools; pipelines orchestrate notebook/job execution and dependencies.

A typical flow is:

1. Ingest source data into ADLS with a pipeline or another ingestion service.
2. Run a Spark notebook for parsing, complex enrichment, or large-scale transformations.
3. Write curated Parquet/Delta data to the lake.
4. Query curated files using serverless SQL for exploration, or load selected data into dedicated SQL for repeated warehouse serving.
5. Monitor each pipeline activity and engine independently.

Linked services define connections and authentication. Use managed identity where possible, scope storage/database roles narrowly, and ensure network access. A pipeline success status only says its activity completed according to the activity contract; it does not prove data quality or business correctness. Add row-count, schema, freshness, and reconciliation checks.

## 9. Five workload scenarios: serverless or dedicated?

| Scenario | Initial choice | Why | What would change the decision? |
|---|---|---|---|
| 1. Analyst explores a new month of Parquet data a few times per week | Serverless | No need to load a warehouse first; pay according to query processing | Queries become frequent and repetitive, or data layout causes excessive scans |
| 2. Executive dashboard joins large facts/dimensions every few minutes with concurrency expectations | Evaluate dedicated | Curated distribution/indexing and controlled capacity may provide more predictable repeated serving | Fabric Warehouse or another managed serving layer meets needs better; benchmark with real concurrency |
| 3. One-time audit across historical lake partitions | Serverless, if the scan is acceptable | Direct lake access avoids a separate load step | Repeated audits scan the same data so often that materialization is cheaper/faster |
| 4. Nightly ELT builds curated facts and dimensions for recurring BI | Dedicated is a strong candidate; compare Fabric Warehouse | Repeatable warehouse modeling, joins, distribution, and scheduled compute can fit | Small workload or Fabric-first strategic direction makes another serving engine more suitable |
| 5. Raw JSON parsing, complex ML feature engineering, or large graph-like transformations | Spark first, then serverless/dedicated for SQL serving | Spark is better suited to distributed data engineering beyond relational SQL | Simple transforms over structured data may be cheaper/easier in SQL |

For every scenario, state workload frequency, scanned bytes, concurrency, freshness, latency, data layout, security, and operational constraints before making a cost claim.

## 10. Synapse and Microsoft Fabric: compare capabilities, not names

Fabric is a SaaS analytics platform built around OneLake and integrated experiences for data engineering, warehouse, real-time analytics, data science, and Power BI. Synapse is an Azure analytics service with separately configured workspace resources and compute engines. Some concepts map closely; they are not all one-to-one replacements.

| Synapse capability | Potential Fabric destination | Migration caution |
|---|---|---|
| Dedicated SQL pool warehouse | Fabric Warehouse, or a Lakehouse plus SQL endpoint depending on serving needs | T-SQL coverage, workload behavior, distribution/index assumptions, security, stored procedures, and performance require assessment |
| Serverless SQL over ADLS | Lakehouse SQL analytics endpoint, Fabric Warehouse, or continued access to ADLS via supported shortcuts/patterns | Query semantics, external data access, permissions, billing, and file layout differ |
| Synapse Spark notebooks/jobs | Fabric notebooks, Spark job definitions, Lakehouse | Runtime, libraries, identity, environment, storage paths, and orchestration may require refactoring |
| Synapse pipelines | Fabric Data Factory pipelines where supported | Activities, linked services/connections, triggers, global parameters, and integration patterns may not all upgrade unchanged |
| ADLS data | OneLake, or OneLake shortcuts to ADLS where appropriate | Decide between in-place access and data migration; consider governance, latency, network, and data ownership |

### Migration path

1. **Inventory:** list SQL objects, external data sources, pipelines, notebooks, schedules, permissions, network dependencies, downstream consumers, and operational SLAs.
2. **Assess:** use the current Microsoft migration assessment/assistant relevant to the workload. Treat “ready” as a starting point, not proof of semantic/performance equivalence.
3. **Choose destination per workload:** Fabric Warehouse, Lakehouse, continued Synapse operation, or another engine. Avoid a single-platform mandate when workloads differ.
4. **Map and refactor:** resolve unsupported T-SQL, stored procedures, data movement assumptions, security models, notebook dependencies, pipeline activities, and connection definitions.
5. **Validate:** compare row counts, aggregates, nulls, duplicates, freshness, access control, query results, concurrency, cost, and recovery behavior.
6. **Cut over safely:** run parallel/reconciliation windows, document rollback, freeze schema changes as needed, and retain old assets until acceptance criteria pass.
7. **Decommission:** remove resources only after consumer sign-off, retention/legal checks, lineage review, and verified rollback expiry.

### Lifecycle guidance

The roadmap notes Synapse is being succeeded strategically by Fabric. That is not the same as a blanket statement that every Synapse component is retired or has a single retirement date. Lifecycle status varies by component and changes over time. As checked on **19 October 2026**, the [Microsoft Lifecycle entry for Azure Synapse Analytics](https://learn.microsoft.com/en-us/lifecycle/products/azure-synapse-analytics) lists the service under the Modern Lifecycle Policy as **In Support** with no retirement date shown on that entry. This service-level listing does not replace component-specific checks: Spark runtime versions, individual preview features, integrations, and networking/security mechanisms can have separate support or retirement notices. Before creating a new long-lived platform or planning a migration, verify the current official lifecycle/retirement notices and migration guidance for the exact capability: dedicated SQL pool, serverless SQL, Spark runtime, pipelines, or other workspace features. Record the date checked and the applicable notice in the architecture decision record. Do not infer product retirement from marketing positioning alone.

## 11. Hands-on lab

The lab is in `experiments/04_synapse/`. It uses a small sales dataset so you can validate correctness without inventing performance results. The expected outcome is evidence you collect from your own Azure environment—not a prewritten benchmark number.

### Lab prerequisites and guardrails

- Azure subscription with permission to create/use a Synapse workspace and storage resources, or access to an existing training workspace.
- ADLS Gen2 with a container/folder for sample files; workspace managed identity with appropriate read/write roles.
- Serverless SQL endpoint for the lake query portion.
- A dedicated SQL pool for the distribution/load/workload-management/pause portions. This is a billable resource; set a budget alert first and use the smallest appropriate lab capacity.
- Synapse Studio or a SQL client that can connect to each endpoint.
- Lab files: `experiments/04_synapse/data/sales.csv`, `make_parquet.py`, and SQL scripts in `experiments/04_synapse/sql/`.

**Cost warning:** dedicated pools incur compute charges while running. Pause the pool immediately after the dedicated-pool exercises, and delete lab resources only after confirming no other workload depends on them. Serverless queries can also incur charges based on data processed.

### Part A — Prepare lake files and query with serverless SQL

1. Upload `data/sales.csv` to a local environment and run `python make_parquet.py` after installing `pandas` and `pyarrow`, or create equivalent Parquet files using your normal data pipeline.
2. Upload the generated Parquet files to a path such as `curated/sales/year=2025/month=01/` and `curated/sales/year=2025/month=02/` in ADLS. Ensure the folder structure matches the SQL path examples.
3. Configure the workspace identity, storage RBAC/networking, credential, and external data source as in Section 4.
4. Run `sql/01_serverless_queries.sql` after replacing the storage/database placeholders.
5. Compare the `SELECT *`, projected-column aggregate, and `filepath()`-filtered queries. Capture the query's reported data processed, duration, and path/partition behavior in your notes. Run each more than once if comparing repeated execution, and avoid concurrent workloads during the comparison.

**Expected observations:** selected columns on Parquet often reduce data read; a restrictive path predicate can reduce the files considered; actual bytes, duration, and cost vary by file layout, region, service configuration, and current pricing. The lab does not provide fabricated performance figures.

### Part B — Load and compare hash vs round-robin

1. Create a dedicated SQL pool and wait until it is online.
2. Upload the CSV file to a storage path accessible to the workspace managed identity.
3. In the dedicated SQL database, run `sql/02_dedicated_tables.sql` to create hash and round-robin tables.
4. Run the `COPY INTO` statements in `sql/03_copy_and_ctas.sql` against the same input files. For a fair comparison, load into empty tables and validate counts/totals before timing queries.
5. Execute equivalent join/aggregation queries against each table. Capture elapsed time, request steps, movement operations, and distribution-space observations. Small datasets may not demonstrate a meaningful difference; do not infer production behavior from this dataset.

### Part C — Inspect movement and statistics

1. Run the request DMV queries in `sql/04_diagnostics_workload.sql`.
2. Identify the request ID for your join/aggregate and inspect `sys.dm_pdw_request_steps`.
3. Review the graphical plan in your SQL client if available. Look for `ShuffleMove`/`BroadcastMove`, estimate/actual row mismatches where available, and expensive scans or joins.
4. Compare table distribution and row counts. Consider whether a hash key is suitable; do not change the design until you can state the workload hypothesis.

### Part D — Workload management and pause

1. Ensure the dedicated pool is online, your account has the required database permissions, and `etl_user` exists before running the optional workload group/classifier statements. Tune resource percentages for your configuration; the example is not a universal production setting.
2. Verify the classifier/group in the supported workload-management views or Synapse Studio.
3. Pause the dedicated SQL pool in Synapse Studio/Azure portal or with the supported management command for your environment. Confirm the state is paused. Record the running-compute billing implication and the fact that storage charges continue. Resume only if further testing is required.
4. Delete the dedicated pool and temporary resources if they were created solely for this lab and are no longer needed.

### Validation checklist

- [ ] Serverless SQL can read the uploaded Parquet files using managed identity.
- [ ] `SELECT *` and selected-column query both return logically consistent results.
- [ ] The `filepath()` predicate selects the intended partition folders.
- [ ] Hash and round-robin tables have matching row counts and business totals.
- [ ] You inspected request steps/plan and documented any movement operation observed—or explicitly recorded that the tiny workload did not reveal a meaningful difference.
- [ ] Workload group/classifier was created and validated, or the configuration limitation was documented.
- [ ] Dedicated pool was paused and cleanup was completed.

## 12. Practice questions and answer key

### Questions

1. A team queries 10 TB of Parquet once per month. What should it evaluate first, and what can make serverless unexpectedly expensive?
2. Why is `ROUND_ROBIN` often reasonable for staging but not automatically ideal for a large final fact table?
3. A large join has a `ShuffleMove`. Is that necessarily a bug? What should you inspect?
4. When can partitioning improve a dedicated table, and when can it hurt?
5. What does pausing a dedicated SQL pool stop billing for, and what does it not stop?
6. A Synapse pipeline is marked ready by a Fabric migration assessment. What checks are still required?
7. A serverless view exposes a table to a reporting user. Why is that not enough to assume the underlying data is secure?
8. How would you compare hash and round-robin layouts without misleading yourself with noisy results?

### Answer key

1. Start by evaluating serverless over the lake, using Parquet, projection, predicates, and partitions. Repeated broad scans, high query frequency, poor file layout, and storage throttling can increase cost or latency. Compare against materialization/dedicated or Fabric for repeated workloads.
2. Round-robin spreads rows without a key and can load quickly, but joins may redistribute data. A hash key can co-locate rows for recurring joins/aggregations when the key has good cardinality and low skew.
3. No. It indicates redistribution was needed for the plan. Inspect row counts, join keys, table distributions, skew, and whether a compatible design or replicated small dimension could reduce movement.
4. Partitioning helps when queries filter on the partition key or retention/maintenance is range-based. Excessive small partitions, poor filter alignment, or tiny data volumes can add overhead.
5. It stops dedicated compute billing while paused. Stored data remains, storage charges continue, and resume time/availability still matter.
6. Validate activity support, linked-service/connection mapping, global parameters, identity, network, T-SQL semantics, data correctness, security, performance, alerting, rollback, and cost in the target Fabric capacity.
7. View permissions/ownership chaining and underlying access behavior must be tested. Use least privilege and explicit row/column security where needed.
8. Use identical data, empty target tables, the same query shape, controlled concurrency, repeated runs, and row-count/aggregate reconciliation. Record the service level, file layout, request steps, and variability; do not claim a result from one small run.

## 13. Checkpoint

Before moving to Topic 05, verify that you can:

- [ ] Choose serverless vs dedicated SQL for a workload and explain billing behavior.
- [ ] Query Parquet in ADLS with `OPENROWSET` and explain the role of external data sources/credentials.
- [ ] Use `filepath()` and describe why partition elimination matters.
- [ ] Choose hash, round-robin, or replicated distribution for a fact/dimension/staging table.
- [ ] Explain partitioning and clustered columnstore trade-offs.
- [ ] Load data with `COPY INTO`, describe PolyBase and CTAS, and validate the load.
- [ ] Diagnose data movement, skew, and statistics using plans and DMVs.
- [ ] Explain workload groups/classifiers and the limits of result-set caching.
- [ ] Explain how Synapse SQL, Spark, and pipelines work together.
- [ ] Describe a safe, evidence-based Synapse-to-Fabric migration path.

## 14. Troubleshooting

| Symptom | Likely causes | Checks |
|---|---|---|
| Serverless SQL cannot read files | Incorrect path, missing storage role, expired/wrong credential, firewall/private endpoint/DNS issue | Validate URL/container, managed identity role scope, storage network rules, credential, and workspace network route |
| `OPENROWSET` returns schema/type errors | Inconsistent Parquet schemas, inferred types differ, invalid wildcard/path | Inspect sample file schema; use explicit schema where supported; test a single known file before wildcarding |
| Query scans more data than expected | `SELECT *`, missing filters, poor folder partitioning, path wildcard too broad | Project columns, add predicates, verify `filepath()` ordinals and actual folder layout, review monitoring |
| Dedicated join is slow | Skew, incompatible distribution, large data movement, stale statistics, insufficient resources | Inspect request steps/plan, row counts by distribution, join keys, stats freshness, and representative workload profile |
| `COPY INTO` fails | Storage identity lacks data access, network blocked, bad CSV format, schema mismatch | Validate identity/RBAC/network, file delimiters/quotes/line endings, column order/types, and exact error details |
| Workload group/classifier creation fails | Pool offline, missing permissions, existing conflicting object, unsupported syntax/configuration | Confirm dedicated pool is online, inspect permissions/object names, verify syntax against current docs |
| Fabric migration changes results or performance | T-SQL gaps, different storage/access/security, activity incompatibility, runtime differences | Run side-by-side reconciliation and representative load tests; check official migration assessment and feature matrix |
| Cost exceeds expectations | Dedicated pool left running, broad/repeated serverless scans, high concurrency, unnecessary duplicate data | Inspect usage and billing, pause unused compute, optimize file scans, and revisit architecture with measured workload data |

## 15. Official references

Use current Microsoft documentation because service syntax, supported features, pricing, and migration tools change. These links are reference starting points; confirm the exact endpoint and region before applying commands.

- [Microsoft Lifecycle: Azure Synapse Analytics](https://learn.microsoft.com/en-us/lifecycle/products/azure-synapse-analytics)  
- [Synapse Spark runtime lifecycle and supportability](https://learn.microsoft.com/en-us/azure/synapse-analytics/spark/runtime-for-apache-spark-lifecycle-and-supportability)  
- [Azure Synapse Analytics pricing](https://azure.microsoft.com/en-us/pricing/details/synapse-analytics/)  
- [Synapse SQL architecture](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/overview-architecture)
- [Dedicated SQL pool MPP architecture](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/massively-parallel-processing-mpp-architecture)
- [Dedicated SQL pool table distribution guidance](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/sql-data-warehouse-tables-distribute)
- [Dedicated SQL pool table design](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/sql-data-warehouse-tables-overview)
- [Best practices for serverless SQL pool](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/best-practices-serverless-sql-pool)
- [Serverless SQL storage access and permissions](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/develop-storage-files-storage-access-control)
- [Serverless SQL cost management and data-processed limits](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/data-processed)
- [External tables, recursive paths, and partition elimination](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/develop-tables-external-tables)
- [Use `OPENROWSET` with serverless SQL](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/develop-openrowset)
- [Use `filepath()` and `filename()`](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/query-specific-files)
- [Dedicated SQL pool result-set caching](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/performance-tuning-result-set-caching)
- [Workload classification for dedicated SQL pool](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/sql-data-warehouse-workload-classification)
- [Fabric migration planning for Synapse dedicated SQL pools](https://learn.microsoft.com/en-us/fabric/data-warehouse/migration-synapse-dedicated-sql-pool-planning)
- [Overview of migrating Synapse Spark to Fabric](https://learn.microsoft.com/en-us/fabric/data-engineering/migrate-synapse-overview)
- [Migrate Synapse data and pipelines to Fabric](https://learn.microsoft.com/en-us/fabric/data-engineering/migrate-synapse-data-pipelines)
- [Upgrade Synapse pipelines to Fabric Data Factory](https://learn.microsoft.com/en-us/fabric/data-factory/how-to-upgrade-your-azure-synapse-analytics-pipelines-to-fabric-data-factory)

---

**Verification note:** The lesson was aligned against the Topic 04 syllabus and its stated lab/checkpoint/common-mistake list. SQL and configuration fragments are illustrative and were reviewed for internal consistency, but they were not executed against a live Synapse workspace. The Python conversion script passed syntax parsing; its Parquet generation could not be run in this environment because `pyarrow` is not installed. No benchmark values or deployment outcomes are claimed. Verify current syntax, endpoint support, permissions, prices, and lifecycle notices before production use.
