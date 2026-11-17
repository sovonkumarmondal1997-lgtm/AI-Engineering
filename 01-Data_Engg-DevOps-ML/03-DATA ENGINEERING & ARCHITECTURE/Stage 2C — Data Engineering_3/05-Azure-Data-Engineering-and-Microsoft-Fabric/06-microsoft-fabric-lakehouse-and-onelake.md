# Microsoft Fabric: Lakehouse and OneLake

> **Module:** Stage 2C — Data Engineering_3 / `05-Azure-Data-Engineering-and-Microsoft-Fabric/`  
> **Topic:** 06 — Microsoft Fabric: lakehouse and OneLake  
> **Level:** Beginner → Intermediate → Advanced  
> **Purpose:** Learn the Fabric storage-and-compute model, implement a small medallion pipeline, and make evidence-based choices about lakehouse, warehouse, shortcuts, security, capacity, and deployment.

## 1. Purpose, prerequisites, and learning outcomes

Microsoft Fabric is a software-as-a-service analytics platform that brings data engineering, data integration, data warehousing, real-time analytics, data science, and Power BI into a common tenant and capacity model. OneLake provides a common logical data lake. The important engineering skill is not memorizing every Fabric screen: it is understanding **which item owns the data, which engine processes it, which permission boundary applies, and which capacity pays for the work**.

This lesson follows Topic 06 in `roadmap-Azure-Data-Engineering-and-Microsoft-Fabric.md`. It covers the assigned Fabric concepts and the lab in `experiments/06_fabric/`; it is not a full Power BI, Databricks, or general Spark course.

### Prerequisites

You should be comfortable with:

- SQL and basic T-SQL, including joins, grouping, and table creation.
- ETL/ELT pipelines and orchestration concepts.
- CSV, Parquet, Delta Lake, and bronze/silver/gold medallion architecture.
- Basic PySpark DataFrame operations and reading/writing files.
- Cloud identity, role-based access control, managed identities, and secrets.
- Git branches, commits, pull requests, and environment-specific configuration.

The earlier roadmap modules introduce SQL, Spark, Parquet/Delta, medallion architecture, cloud IAM, secrets, CI/CD, Databricks, and governance. Revisit those modules if these prerequisites are unfamiliar.

### Learning outcomes

By the end, you should be able to:

1. Explain Fabric tenants, F SKU capacities, workspaces, items, and experiences.
2. Explain OneLake, Delta/Parquet storage, OneLake paths, and shortcuts.
3. Distinguish lakehouse Files, lakehouse Tables, the SQL analytics endpoint, and Fabric Warehouse.
4. Build and validate a bronze → silver → gold data flow with Spark and T-SQL.
5. Decide when to copy data, use a shortcut, use a lakehouse, or use a warehouse.
6. Explain Data Factory pipelines, Dataflows Gen2, mirroring, and Direct Lake at the right level.
7. Distinguish workspace, item, OneLake, SQL, and semantic-model security.
8. Read capacity metrics and reason about smoothing, throttling, and cost.
9. Promote artifacts through Git/deployment pipelines without accidentally retaining development bindings.
10. Compare Fabric, Azure Databricks, and Snowflake based on workload, skills, governance, and portability.

## 2. Fabric architecture and major experiences

### 2.1 The basic hierarchy

A useful mental model is:

```text
Microsoft Entra tenant
└── Microsoft Fabric tenant (OneLake logical namespace and tenant settings)
    ├── Capacity A (F SKU; shared compute budget)
    │   ├── Development workspace
    │   │   ├── Lakehouse (Files + Delta Tables + SQL analytics endpoint)
    │   │   ├── Notebook / Spark job definition
    │   │   ├── Data pipeline / Dataflow Gen2
    │   │   ├── Warehouse
    │   │   └── Power BI semantic model / report
    │   └── Test workspace
    └── Capacity B (separate compute allocation / cost boundary)
        └── Production workspace
```

The diagram is conceptual, not a deployment specification. A tenant may have one or multiple capacities, and a workspace is assigned to a capacity or an available shared/trial capacity. A workspace contains items; it is not itself a storage engine. Items use different compute experiences, but their workloads may draw from the capacity assigned to the workspace.

**Do not confuse shared storage with shared compute.** OneLake provides a logical storage foundation, but Spark, Warehouse, the SQL analytics endpoint, pipelines, Power BI, and Real-Time Intelligence do not become one interchangeable engine. They have distinct execution models, capabilities, configuration, and limits.

### 2.2 Major experiences and their jobs

| Experience / item | Primary job | Typical output or interaction | Important boundary |
|---|---|---|---|
| **Data Engineering** | Spark notebooks, Spark job definitions, lakehouse engineering | Delta tables and files in OneLake | Spark runtime, libraries, session sizing, and supported APIs matter |
| **Data Factory** | Copy/ingestion, pipeline orchestration, Dataflows Gen2 | Data movement and transformation workflows | Connector and item deployment support varies; verify before standardizing |
| **Data Warehouse** | Relational analytics and governed SQL transformations | Warehouse tables, views, procedures, and SQL queries | T-SQL surface is substantial but not identical to SQL Server in every feature |
| **Real-Time Intelligence** | Event ingestion, streaming, KQL-based analytics | Eventstreams, Eventhouse/KQL databases, dashboards | Not a replacement for batch Spark or every warehouse workload |
| **Data Science** | Experiments, models, ML workflows | Models and scored/analytical datasets | ML lifecycle details are outside this lesson |
| **Power BI** | Semantic modeling, measures, reporting, consumption | Semantic models and reports | Report access and semantic-model security must be designed, not assumed from lake permissions |
| **Mirroring** | Keep supported source data synchronized into Fabric | Mirrored database/data in OneLake | Source support, region, networking, licensing, and feature state vary |

### 2.3 Tenant, capacity, and workspace

- **Tenant:** The organization's Fabric boundary, controlled by tenant settings and identity policies.
- **Capacity:** Compute resources measured in Capacity Units (CUs). F SKUs are provisioned capacity options; the exact size should be chosen from measured workload and concurrency, not guesswork.
- **Workspace:** Collaboration, permission, lifecycle, and capacity-assignment boundary for items.
- **Item:** A lakehouse, warehouse, notebook, pipeline, semantic model, report, eventhouse, or another supported Fabric object.

A workspace-per-environment model (Dev/Test/Prod) is common. A workspace-per-medallion-layer model can create useful ownership/security boundaries, but it also introduces cross-workspace deployment and permission complexity. Use separate workspaces when they represent a real access, lifecycle, ownership, or capacity boundary—not just because a diagram has three medallion boxes.

A Fabric trial may not be available in every tenant or for every user. Tenant administrators can disable trials, and trial capabilities/limits differ from paid capacity. Before starting the lab, verify that you can create items and run Spark on an eligible capacity. Do not assume a trial is enabled or free for your account.

## 3. OneLake fundamentals

### 3.1 What OneLake is—and is not

OneLake is the unified logical data lake automatically associated with a Fabric tenant. It is built on Azure Data Lake Storage concepts and provides a common namespace for analytics data. Fabric lakehouse tables commonly use **Delta Lake transaction metadata over Parquet data files**. OneLake also has growing support for open table formats such as Iceberg, but support differs by item and engine; do not assume every Fabric experience can read/write every table format in the same way.

OneLake's value is that several Fabric experiences can work against shared data without every workload maintaining another copy. It does not mean that all workloads share one catalog, one query engine, one security policy, or one performance profile.

### 3.2 Files versus Tables in a lakehouse

- **Files** is for files and folder structures: raw CSV/JSON, source extracts, documents, images, intermediate outputs, and other non-table assets.
- **Tables** exposes registered/recognized tabular data, commonly Delta tables, for Spark and the lakehouse SQL analytics endpoint.
- A Delta table is not just a directory of Parquet files. The `_delta_log` records table versions and transactions; do not manipulate or delete its internals as if it were a plain CSV folder.
- A CSV stored under `Files/` does not automatically become a table. Read it and write a Delta table or use a supported ingestion experience.
- The SQL analytics endpoint reads supported Delta tables. It is not the general-purpose SQL editor for arbitrary CSV files in `Files/`.

### 3.3 OneLake paths and ABFS access

A common OneLake ABFS URI shape is:

```text
abfss://<workspace-name>@onelake.dfs.fabric.microsoft.com/<lakehouse-name>.Lakehouse/Files/<path>
abfss://<workspace-name>@onelake.dfs.fabric.microsoft.com/<lakehouse-name>.Lakehouse/Tables/<table-path>
```

Names and path forms must match the actual workspace/item. For production automation, use the supported item IDs and APIs where appropriate instead of relying on display names that can be renamed. Access requires an authenticated identity and the necessary permissions; a correct path alone does not grant access.

In a Fabric notebook attached to a lakehouse, the default lakehouse is commonly available under `/lakehouse/default/`. For example:

```python
input_path = "/lakehouse/default/Files/landing/sales.csv"
```

The notebook must actually have the intended lakehouse attached and the file must exist at that path. Notebook path availability differs from a local Python process.

### 3.4 Shortcuts: virtual access instead of copying

A shortcut is a OneLake reference to data stored elsewhere. It can expose supported data in Azure storage, Amazon S3, another lakehouse, and other supported sources, depending on current connector availability. The shortcut typically avoids creating an independent data copy in the target lakehouse. It does **not** eliminate source-side storage, source API/network charges, or compute needed to read and transform the data.

A shortcut is useful when the source remains authoritative and users need governed analytical access. A physical copy may be preferable when you need an immutable landing snapshot, a transformed/curated version, predictable local performance, independent retention, or a source that cannot meet query/runtime requirements.

**Source-specific caveats:** ADLS Gen2, S3, GCS, and OneLake shortcuts do not have identical authentication or feature support. S3 and GCS shortcuts are read-only; do not design a write-back pipeline through them. ADLS shortcut authentication differs for same-tenant versus cross-tenant storage, and some private-network configurations are not supported by shortcuts. For OneLake-to-OneLake shortcuts, users may need authorization on both the shortcut path and the target path. Check the current source-specific documentation before relying on a particular identity, network, or nested-shortcut pattern.

| Decision | Shortcut is a good fit when… | Copy/ingest is a good fit when… |
|---|---|---|
| Freshness | Source data should remain current and the connector supports the required semantics | You need scheduled snapshots, replay, or an auditable ingestion boundary |
| Data movement | Avoiding duplicate storage and transfer is valuable | Data must be standardized, filtered, encrypted, partitioned, or compacted |
| Availability | Source availability and access are acceptable dependencies | You need an independent copy for resilience or source isolation |
| Security | The shortcut's connection/identity and downstream permissions are designed correctly | A separate curated security boundary is required |
| Performance | Remote read behavior meets the workload SLA | Repeated scans or source latency make a local optimized copy more appropriate |

**Shortcut security matters.** Confirm the identity/connection used to reach the target, who can manage the shortcut, who can read data through each Fabric engine, and whether source-side policies remain effective. Shortcut creation does not mean every downstream user automatically has access to the source, nor should it be treated as a way to bypass source authorization. Supported authentication and source limitations can differ between ADLS, S3, GCS, and OneLake.

### 3.5 Choosing five example datasets

| Dataset | Recommended starting choice | Reasoning |
|---|---|---|
| Daily raw point-of-sale CSV exports | **Files → bronze Delta table** | Preserve raw files, then parse/validate into a table |
| Frequently updated ADLS customer reference data owned by another team | **Shortcut**, if permissions and freshness are appropriate | Avoid duplicating an externally governed source; materialize only if repeated reads or isolation justify it |
| Multi-terabyte clickstream with nested payloads | **Lakehouse** | Spark/Delta is suitable for schema evolution and large-scale transformations |
| Curated sales facts/dimensions with governed T-SQL transformations and BI reporting | **Warehouse** (or a lakehouse gold table if Spark/open files dominate) | Relational modeling and SQL-first business transformations |
| Small static mapping file used by many pipelines | **Files or a shortcut** | Keep it simple; choose copy if the mapping needs controlled versioning or snapshot semantics |

These are starting decisions, not universal rules. Volume, latency, governance, concurrency, team skills, and cost can change the choice.

## 4. Lakehouse SQL analytics endpoint versus Warehouse

### 4.1 Lakehouse SQL analytics endpoint

The SQL analytics endpoint automatically exposes supported lakehouse Delta tables for T-SQL querying. It is primarily **read-only with respect to table data**: you can query tables and create supported SQL objects such as views, but use Spark or another supported write path to change the underlying lakehouse data. Do not expect to `INSERT`, `UPDATE`, or `DELETE` lakehouse table rows through this endpoint as if it were a Warehouse.

Example query:

```sql
SELECT
    product_category,
    COUNT_BIG(*) AS line_count,
    SUM(CAST(net_amount AS decimal(18, 2))) AS net_sales
FROM dbo.silver_sales
GROUP BY product_category
ORDER BY net_sales DESC;
```

This assumes a `silver_sales` Delta table is registered/exposed in the SQL analytics endpoint, and its column names/types match the query. Use the endpoint's own database/item context when selecting the object.

The SQL analytics endpoint is useful for SQL-first exploration, views, BI connections, and cross-item queries over supported Fabric data. It is not a replacement for a transactional OLTP database or a full writable Warehouse.

### 4.2 Fabric Data Warehouse

Fabric Warehouse is a relational analytical warehouse on a data-lake foundation. It is SQL-first and supports a substantial T-SQL surface, including curated tables and multi-table transactions, but it is not identical to SQL Server in every feature. Warehouse data is stored in Delta/Parquet-based OneLake storage, with Fabric managing much of the storage/compute implementation.

A Warehouse is often a good fit for curated star schemas, corporate data marts, SQL-oriented ELT, and governed BI datasets. A Lakehouse is often a better starting point for heterogeneous raw data, Spark-first engineering, semi-structured processing, and open file-oriented workflows. They can coexist.

Example cross-item query from a Warehouse or supported SQL endpoint context:

```sql
-- Replace the item and object names with real objects visible to the SQL endpoint.
SELECT
    s.product_category,
    SUM(CAST(s.net_amount AS decimal(18, 2))) AS net_sales
FROM [SilverLakehouse].dbo.silver_sales AS s
GROUP BY s.product_category;
```

Cross-database naming, permissions, and supported query behavior depend on the SQL endpoint and item types involved. Test cross-item references in the actual target workspace; do not assume all SQL objects are queryable from all Fabric items.

### 4.3 Quick comparison

| Capability | Lakehouse Files | Lakehouse Tables + SQL endpoint | Fabric Warehouse | Shortcut |
|---|---|---|---|---|
| Primary use | Files and landing zones | Spark/Delta engineering and SQL reads | SQL-first curated analytical models | Access data at another supported location |
| Data ownership | File/folder assets in OneLake | Delta tables in OneLake | Managed warehouse item with data in OneLake | Source owns the referenced data |
| Write path | File APIs/notebooks/pipelines | Usually Spark/ingestion writes; SQL endpoint is read-only for table data | T-SQL and supported load paths | Writes generally happen at source, not by editing the shortcut target as a local copy |
| Best skill fit | File/data engineering | Spark + Delta + SQL | T-SQL, dimensional modeling, BI | Data federation/access without an edge copy |
| Main caveat | Files are not automatically queryable tables | SQL endpoint does not provide general table DML | Not every SQL Server feature is available | Source permissions/availability and remote-read behavior matter |

## 5. Bronze → silver → gold implementation

### 5.1 Data model for the lab

The lab uses a small sales CSV with columns:

- `sale_id`: unique sale line identifier.
- `sale_timestamp`: timestamp string in ISO-8601 format.
- `device_id`: store terminal/device identifier.
- `product_category`: category label.
- `quantity`: integer quantity.
- `unit_price`: decimal price per unit.
- `region`: sales region.

The provided CSV is synthetic learning data. It contains no credentials or real customer information. The intended flow is:

```text
CSV in lakehouse Files/landing/
        │
        ▼
Bronze Delta table (raw typed-as-string/ingestion columns)
        │ validate, parse timestamps/numbers, remove invalid rows
        ▼
Silver Delta table (typed, deduplicated, quality-checked)
        │ aggregate business measures
        ▼
Gold table in Fabric Warehouse (business-ready aggregate)
        │
        ▼
Power BI semantic model (Direct Lake where supported)
```

Bronze should preserve enough source information to replay and investigate ingestion issues. Silver should enforce types, quality checks, and deduplication rules. Gold should express business meaning, not merely repeat silver data under a different name.

### 5.2 Spark notebook: ingest and validate

The accompanying script `experiments/06_fabric/notebooks/bronze_silver_gold.py` is a **Fabric notebook code companion**, not a standalone local script. Attach the target lakehouse as the notebook's default lakehouse, upload `sample_sales.csv` to `Files/landing/`, and run the cells in order. If you use a different workspace/item name, change the relevant path and table names.

Core pattern:

```python
from pyspark.sql import functions as F
from pyspark.sql import types as T

source_path = "/lakehouse/default/Files/landing/sample_sales.csv"
raw = (spark.read
       .option("header", True)
       .option("mode", "PERMISSIVE")
       .csv(source_path))

# Preserve raw source values in bronze; add an ingestion timestamp.
bronze = raw.withColumn("_ingested_at_utc", F.current_timestamp())
bronze.write.format("delta").mode("overwrite").saveAsTable("bronze_sales")

silver = (bronze
    .withColumn("sale_id", F.trim(F.col("sale_id")))
    .withColumn("sale_timestamp", F.to_timestamp(F.col("sale_timestamp"), "yyyy-MM-dd'T'HH:mm:ssX"))
    .withColumn("quantity", F.col("quantity").cast("int"))
    .withColumn("unit_price", F.col("unit_price").cast(T.DecimalType(12, 2)))
    .withColumn("net_amount", (F.col("quantity") * F.col("unit_price")).cast(T.DecimalType(18, 2)))
    .withColumn("region", F.upper(F.trim(F.col("region"))))
    .withColumn("product_category", F.trim(F.col("product_category")))
    .filter(F.col("sale_id").isNotNull() & (F.col("sale_id") != ""))
    .filter(F.col("sale_timestamp").isNotNull())
    .filter(F.col("quantity").isNotNull() & (F.col("quantity") > 0))
    .filter(F.col("unit_price").isNotNull() & (F.col("unit_price") >= 0))
    .dropDuplicates(["sale_id"]))

silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("silver_sales")

# Validation: these are queries to run, not claimed results.
print("bronze rows:", spark.table("bronze_sales").count())
print("silver rows:", spark.table("silver_sales").count())
spark.table("silver_sales").groupBy("region").count().orderBy("region").show()
```

**Engineering notes:**

- `mode("overwrite")` makes this simple lab repeatable, but it is not a safe default for production incremental pipelines. Production ingestion usually uses deterministic batch IDs, idempotent merge/upsert logic, or append-plus-deduplication according to the source contract.
- `dropDuplicates(["sale_id"])` chooses a row for duplicate keys without defining a business ordering. If duplicates can contain conflicting updates, use a deterministic rule (for example, latest source version/timestamp) with a window function before writing.
- Timestamp parsing depends on source format and Spark session time zone. Standardize event timestamps and define whether they represent UTC or local time.
- Invalid rows are filtered here to keep the lesson short. Production pipelines should write rejected rows and reason codes to a quarantine table/path, then alert on threshold breaches.
- Re-running the notebook overwrites the lab tables. Do not reuse this overwrite pattern against production tables without explicit approval and a recovery plan.

### 5.3 Gold aggregation in Fabric Warehouse

Create a Fabric Warehouse in the workspace and ensure the SQL execution context can read the silver table through a supported cross-item query. The SQL below is a **teaching pattern**: replace `[SilverLakehouse]` with the actual lakehouse item name and verify that the silver table is visible from the Warehouse query context.

```sql
-- Run in Fabric Warehouse, not the lakehouse SQL analytics endpoint.
DROP TABLE IF EXISTS dbo.GoldDailySales;

CREATE TABLE dbo.GoldDailySales
AS
SELECT
    CAST(s.sale_timestamp AS date) AS sale_date,
    s.region,
    s.product_category,
    SUM(CAST(s.quantity AS bigint)) AS units_sold,
    SUM(CAST(s.net_amount AS decimal(18, 2))) AS net_sales,
    COUNT_BIG(*) AS sale_lines
FROM [SilverLakehouse].dbo.silver_sales AS s
GROUP BY
    CAST(s.sale_timestamp AS date),
    s.region,
    s.product_category;
```

If CTAS is unavailable in the selected query context or the cross-item reference is not permitted, create `dbo.GoldDailySales` with an explicit schema and load it through a supported `INSERT ... SELECT`, pipeline, or Spark write path. Check current Fabric Warehouse T-SQL support before using advanced SQL Server syntax. The script intentionally drops and rebuilds a small lab table; production loads should be incremental or use a controlled replacement strategy.

Validate the gold output:

```sql
SELECT TOP (20) *
FROM dbo.GoldDailySales
ORDER BY sale_date DESC, net_sales DESC;

SELECT SUM(net_sales) AS gold_total_sales
FROM dbo.GoldDailySales;
```

Compare totals with the silver source using equivalent filters and numeric precision. A mismatch can be caused by rejected rows, duplicate removal, timestamp/time-zone boundaries, decimal casting, or an incomplete source load—not necessarily by the Warehouse engine.

## 6. Spark notebooks, job definitions, environments, and Delta maintenance

### 6.1 Notebooks and Spark job definitions

A **notebook** is interactive code organized into cells; it is ideal for exploration, engineering, validation, and parameterized workflows. A **Spark job definition** runs a packaged/scripted Spark workload as a job, which can be easier to automate when an interactive notebook is unnecessary. Both run on Fabric-managed Spark infrastructure; runtime versions, libraries, compute startup, concurrency, and session configuration still matter.

A Fabric **environment** can define Spark runtime settings and libraries for reproducibility. Avoid relying on a library installed manually in one interactive session. Record runtime/library versions, use a controlled environment, and validate the same artifact in test before production.

### 6.2 Small files, compaction, V-Order, and OPTIMIZE

Many tiny Parquet files can increase listing, planning, and scan overhead. Compact only after measuring file sizes and downstream query patterns; compaction consumes compute and rewrites files.

- **V-Order** is a write-time Parquet layout optimization intended to improve downstream reads, especially for cross-engine consumers such as Power BI Direct Lake. Current defaults and settings can vary by workspace, runtime, and session; do not assume it is enabled. Measure both write overhead and downstream query behavior before enabling it broadly.
- **OPTIMIZE** compacts/optimizes supported Delta tables in the Fabric Spark context. The Lakehouse table-maintenance UI and supported pipeline maintenance activity are alternatives; exact options depend on the runtime and current feature state. Run maintenance in the Spark/lakehouse-maintenance context, not the SQL analytics endpoint or Warehouse SQL editor.
- **VACUUM** removes unreferenced data files older than a retention threshold. The documented default threshold is seven days, and supported maintenance requests reject shorter retention by default. It can permanently remove files needed for historical reads/time travel. Do not shorten retention or disable safety checks just to reclaim storage; account for concurrent readers, recovery requirements, and retention policy.

Example patterns to test in the target Fabric Spark runtime:

```sql
-- Run in a Fabric Spark notebook against a table you own.
OPTIMIZE silver_sales;

-- Review the table's retention/time-travel requirements before cleanup.
-- Use the platform-supported VACUUM syntax and safe retention threshold.
VACUUM silver_sales RETAIN 168 HOURS;
```

The `VACUUM` statement above illustrates the documented seven-day retention form; confirm the runtime's supported syntax and safety checks before running it. Do not run it against shared or production tables during this lab. The UI's Lakehouse table-maintenance experience can be preferable when you want supported compaction, V-Order, and cleanup options without managing every command yourself. The sample dataset is too small to justify optimization; these commands are included for operational literacy, not as a performance exercise.

### 6.3 Performance troubleshooting sequence

1. Confirm whether the slow step is source read, Spark transformation, Delta write, SQL query, semantic-model query, or pipeline orchestration.
2. Inspect input size, number of files, file-size distribution, partition cardinality, and skew.
3. Avoid high-cardinality partitioning that creates many tiny files. Partition only when the filtering pattern and data size justify it.
4. Filter and project columns early; avoid `collect()` on large datasets; use built-in Spark functions before Python UDFs when possible.
5. Check shuffle stages and skewed keys before increasing compute. More capacity may hide inefficient logic without fixing it.
6. Compare cold-start versus warm-session behavior. Notebook startup and orchestration overhead can dominate tiny datasets.
7. Measure end-to-end pipeline duration and CU consumption, not only notebook execution time.

## 7. Data Factory pipelines, Dataflows Gen2, mirroring, and Direct Lake

### 7.1 Data pipelines

Use Fabric Data Factory pipelines to orchestrate dependencies, parameters, retries, schedules, and calls to notebooks, copy operations, SQL scripts, and other supported activities. A pipeline should express the workflow, not duplicate all transformation logic inside orchestration expressions.

A typical lab pipeline sequence is:

1. Copy/upload the CSV to `Files/landing/` (manual upload is acceptable for the first run).
2. Run the bronze/silver notebook.
3. Run the Warehouse SQL script that rebuilds the gold table.
4. Run validation queries or a validation notebook.
5. Notify/record success or failure using the connectors and alert mechanism available in the workspace.

For production, parameterize workspace-specific item references, storage paths, and destinations. Use supported pipeline parameters/variables and managed connections rather than embedding credentials. Validate activity retry behavior against idempotency: retrying a destructive overwrite is not automatically safe.

### 7.2 Dataflows Gen2

Dataflows Gen2 provides a Power Query-based data preparation experience, with Fabric destinations and orchestration integration depending on supported connectors/features. It can be appropriate for connector-driven shaping and teams comfortable with Power Query. Spark is usually more flexible for complex large-scale transformations, custom libraries, and advanced Delta engineering. Do not choose a tool only because it exists in the product; consider transformation complexity, source connector support, skill ownership, observability, and cost.

### 7.3 Mirroring

Mirroring can continuously replicate supported source data into Fabric/OneLake so that downstream analytics can query it without building a traditional batch copy pipeline for every table. The supported source list and feature status change over time and can vary by region and source configuration. Azure SQL, Cosmos DB, Snowflake, and other sources have had mirroring support, but **check the current mirroring documentation for the exact source, region, limitations, and feature status before making a design commitment**.

Mirroring is not identical to a full database migration: verify supported data types, schema changes, delete/update handling, latency expectations, network access, source workload impact, and security. It also does not remove the need to design curated bronze/silver/gold products where the business needs transformations or quality rules.

### 7.4 Direct Lake and semantic models

Direct Lake is a Power BI semantic-model storage mode designed to read supported Delta data in OneLake without importing a full separate data copy into the semantic model. It can reduce refresh and duplication costs, but it still depends on table layout, model design, capacity, data size, and security configuration.

Important nuance:

- Direct Lake behavior depends on the semantic model's source path and Direct Lake implementation/settings. Some Direct Lake paths can fall back to DirectQuery under conditions such as SQL endpoint security features or unsupported model/data conditions; fallback can affect performance.
- Direct Lake on OneLake is designed for DirectLakeOnly behavior and does not support DirectQuery fallback. Confirm that your chosen item/model creation path is actually Direct Lake on OneLake and test the model's behavior.
- Direct Lake is not the same as Import or DirectQuery. Test freshness, model compatibility, relationships, measures, row-level security, and expected concurrency.
- Data access to the underlying table and permission to consume a semantic model/report are separate questions. A report user should not gain broader access to data merely because the report was shared.

The lab's Direct Lake step is conditional on workspace/capacity availability and the semantic-model path supported by the tenant. If the option is not available, record the reason and query the SQL analytics endpoint as the alternate learning step; do not claim Direct Lake was configured. When creating the model, explicitly record whether it is **Direct Lake on OneLake** or **Direct Lake on a SQL analytics endpoint**: the security and fallback behaviors differ. Direct Lake on OneLake does not fall back to DirectQuery; unsupported conditions can fail the query instead. Direct Lake on SQL analytics endpoints can fall back to DirectQuery under documented conditions, including SQL endpoint RLS or views, which can change performance and security evaluation.

## 8. Security boundaries: workspace, item, data, SQL, and semantic model

Fabric security is layered. A secure design must account for every path a user can use to read the data.

| Layer | What it controls | Common mistake |
|---|---|---|
| Tenant settings | Which Fabric features and integrations are allowed at organization level | Assuming every user can create trials, use Git, or enable mirroring |
| Workspace role | Broad ability to collaborate and manage workspace items | Giving Contributor/Member when read-only access is sufficient |
| Item permissions | Access to a particular lakehouse, warehouse, notebook, pipeline, report, or model | Assuming sharing one item automatically grants only the intended table-level access |
| OneLake data access roles / folder-level access | Supported granular access to OneLake data in the supported security model; availability may be preview/limited by feature | Assuming all Fabric engines and access paths enforce every granular rule identically |
| SQL endpoint permissions and RLS/column controls | SQL access to exposed tables/objects and supported row/column filtering | Securing only the report while users can query the source endpoint directly |
| Semantic model permissions and RLS | Who can build/consume a model and what rows they see through supported model queries | Assuming report sharing alone enforces all data policy requirements |
| Source connection / shortcut identity | Whether Fabric can access the external source | Treating a shortcut as an authorization bypass or sharing a credential broadly |
| Sensitivity labels and protection policies | Classification/protection of supported items and export/sharing workflows | Ignoring labels in deployment, Git, and export paths |

**Practical principles:**

- Use least privilege and security groups; review Admin/Member/Contributor assignments regularly.
- Use managed identities/service principals and approved connections where supported. Do not store passwords, account keys, tokens, or client secrets in notebooks, pipeline JSON, Git, or CSV files.
- Separate development/test/production access and use non-production data when possible.
- Apply row-level security in the layer that matches the intended access path; test it through SQL, semantic models, and any other allowed interface.
- OneLake data access roles can scope access to selected tables/folders and, where supported, apply row-level security (RLS) and column-level security (CLS) for read roles. They complement rather than erase workspace/item permissions. Check the supported item types, role precedence, shortcut behavior, and engine enforcement in the current OneLake security model; do not assume every external client or engine enforces every rule identically.
- RLS/CLS at the OneLake layer, SQL analytics endpoint, and semantic-model layer are distinct mechanisms. Avoid accidental gaps or conflicting policies; test using a least-privileged test identity through each permitted access path.
- Sensitivity labels require the relevant tenant configuration, user permissions, and licensing. A label is a classification/protection control, not a substitute for authorization. Validate how labels propagate to supported downstream items and what export/sharing controls apply in your tenant.
- Audit shortcuts and connections: the identity used to create a connection may not be the same as the downstream user's identity.

## 9. Capacity management, throttling, and cost control

### 9.1 What is billed and shared

Fabric workloads assigned to a capacity consume that capacity's CUs according to the operation and service behavior. Spark, pipelines, Warehouse, semantic models, and other workloads can compete for the same capacity resources when assigned to the same capacity. OneLake storage and external-source charges may be separate from compute charges. Exact billing depends on SKU, region, capacity state, licensing, storage, data movement, and service-specific rules.

Avoid pricing estimates based on a generic sample query. Use current Microsoft pricing pages and your own measured workload. Trial availability and quotas are tenant-specific. A paused capacity may stop compute billing for that capacity while storage and some related charges may continue; verify the current SKU and billing terms before relying on pause/resume as a cost control.

### 9.2 Smoothing and throttling

Fabric may burst above the nominal capacity for short periods and smooth CU consumption over time. **Smoothing spreads accounting; it does not make a workload free and does not necessarily slow down the operation itself.** Sustained overload can trigger throttling, delayed interactive requests, or rejected operations. Policies and thresholds can change; do not hard-code them into an SLA.

A large notebook, Warehouse query, semantic-model refresh, and pipeline can all contribute to capacity pressure. More than one workload can be responsible for a spike. Do not diagnose from one item's wall-clock duration alone.

### 9.3 Capacity Metrics app workflow

After the lab workload:

1. Open the Microsoft Fabric Capacity Metrics app with the required capacity/admin permissions.
2. Select the capacity and a time window that includes the lab run.
3. Inspect CU consumption by item type and operation, background versus interactive workload where shown, and any overload/throttling indicators.
4. Compare notebook/pipeline/warehouse activity to the timeline.
5. Record the workload, duration, item, capacity SKU, and whether the run overlapped other users' work.
6. Optimize first: reduce duplicate scans, compact pathological small files, filter/project early, avoid unnecessary refreshes, and schedule expensive jobs sensibly.
7. Right-size only after the workload is measured. Increasing capacity may be appropriate, but it is not the first response to inefficient work.

The app may not show useful history for a very short lab run or if the user lacks permissions. A lack of visible throttling is not proof that the workload has no cost or cannot overload a shared capacity.

### 9.4 Workload isolation

Separate capacities can provide stronger compute/cost isolation for production workloads, but increase cost and administration. Separate workspaces on the same capacity are not full compute isolation. Choose the boundary based on criticality, concurrency, chargeback, data sensitivity, and recovery requirements.

## 10. Git, deployment pipelines, and CI/CD

### 10.1 Development workflow

A typical lifecycle is:

```text
Feature branch → review / validation → development workspace
       ↓ merge
Main/release branch → test workspace → validation / approvals
       ↓ promote
Production workspace → smoke tests / monitoring
```

Fabric supports Git integration and deployment pipelines for supported item types, but support is not universal. Item definitions, data, connections, credentials, environment-specific bindings, schedules, and permissions do not all behave the same way during deployment.

### 10.2 Recommended practices

- Connect a development workspace to an approved Azure DevOps or GitHub repository where supported.
- Keep notebook source, SQL scripts, configuration templates, and documentation under version control.
- Do not commit credentials or exported tokens. Use approved connection management, Key Vault/secret stores where appropriate, and service identities supported by the deployment path.
- Use parameters/configuration for environment-specific lakehouse, warehouse, storage path, connection, and workspace identifiers.
- Promote through test before production. Validate item bindings after deployment, especially Direct Lake semantic models, shortcuts, pipelines, and connections.
- Use deployment rules or the supported item/API mechanism for environment-specific configuration. Some Data Factory features and Dataflows Gen2 have limitations in deployment pipelines; check the current supported-item matrix.
- Include post-deployment smoke tests: source reachability, table existence, row-count/totals, permissions, pipeline execution, semantic-model binding, and capacity monitoring.
- Keep a rollback strategy. Reverting code does not necessarily revert data or undo destructive table operations.

### 10.3 What is and is not automated

Git integration is source control, not a guarantee that all runtime resources are reproducibly provisioned. Deployment pipelines are a promotion mechanism, not a universal infrastructure-as-code engine. A production CI/CD process often combines Git, supported Fabric APIs/automation, deployment pipelines, environment configuration, and explicit post-deployment validation. Record any manual steps and reduce them over time.

## 11. Awareness: Real-Time Intelligence, Data Science, and Copilot

- **Eventstream** routes and transforms streaming events within supported Fabric real-time workflows.
- **Eventhouse/KQL database** is designed for event/telemetry analytics with KQL query semantics and time-oriented patterns.
- **Fabric Data Science** provides Fabric-integrated data science workflows; it complements rather than replaces a complete model-governance and ML engineering lifecycle.
- **Copilot** capabilities depend on tenant settings, eligible capacity/licensing, region, and current feature availability. Treat generated code and summaries as drafts requiring review, tests, security checks, and data validation.

These are awareness-level topics in this roadmap lesson. Do not expand this into a full KQL, Power BI, or ML course.

## 12. Fabric vs Azure Databricks vs Snowflake

| Dimension | Microsoft Fabric | Azure Databricks | Snowflake |
|---|---|---|---|
| Primary strength | Integrated SaaS analytics across data engineering, BI, warehouse, and real-time workloads | Flexible Spark/lakehouse engineering, advanced data processing, ML/AI and open ecosystem | Managed cloud data platform with strong SQL analytics, data sharing, and warehouse-centric workloads |
| Storage/interoperability | OneLake, Delta/Parquet; Iceberg support is evolving and experience-specific | Cloud object storage, Delta Lake and broader open-data ecosystem through supported connectors/catalogs | Managed storage abstractions; external/open table interoperability depends on supported features and configuration |
| Compute model | Fabric capacities and item-specific engines | DBUs plus underlying cloud infrastructure and configuration choices | Virtual warehouses and service-specific compute models |
| Best fit | Microsoft-centric organizations wanting integrated analytics and Power BI | Teams needing flexible Spark workloads, advanced engineering, ML, and granular compute/runtime choices | SQL-first analytics, data sharing, and mature Snowflake-centric data platforms |
| Operational trade-off | Strong integration, but capacity sharing and product-specific behavior must be understood | More engineering control and ecosystem flexibility, with more platform/compute choices to operate | Managed SQL experience, with platform-specific design and cost/governance considerations |
| Portability risk | Fabric item definitions, orchestration, semantic models, and capacity model can create platform coupling | Delta and open tooling can improve portability, but Unity Catalog/runtime features still create dependencies | SQL dialect, managed services, and proprietary features can create dependencies |

**Do not claim that Delta or Iceberg makes every workload portable.** Open file/table formats help, but portability also depends on catalogs, transaction semantics, security, table features, SQL dialect, orchestration, streaming behavior, metadata, and vendor-specific APIs. Test read/write interoperability with the exact versions and features used.

### Decision guide

Choose Fabric when integrated Microsoft analytics, OneLake, Power BI, and SaaS operations are strong priorities. Choose Databricks when advanced Spark/lakehouse/ML engineering flexibility and runtime control are central. Choose Snowflake when its managed SQL analytics, data-sharing, and existing organizational platform are the best fit. Hybrid architectures can be rational, but each cross-platform boundary adds governance, networking, lineage, data duplication, and operational cost.

## 13. Hands-on lab: `experiments/06_fabric/`

The lab is designed to use a small synthetic sales dataset. It contains scripts and checklists, not a deployed Fabric environment. The exact portal workflow and available options can change by tenant, region, capacity, and current product release.

### 13.1 Prerequisites and cost guardrails

- An organization-approved Fabric tenant and an eligible capacity/trial that permits creating a workspace, lakehouse, notebook, Warehouse, and pipeline.
- Workspace permissions sufficient to create items; capacity/tenant administrators may need to enable features, assign capacity, allow Git, or grant access.
- Power BI/Fabric permissions to create a semantic model and access the Capacity Metrics app if you will do those optional steps.
- An ADLS Gen2 account/container and approved connection/identity if you will create the external shortcut.
- A Git repository and workspace Git integration enabled by the tenant admin if you will practice source control.
- A region/source combination where the desired shortcut and Direct Lake capabilities are supported.

Start with the smallest eligible lab capacity and a small dataset. Do not run large Spark jobs or repeated optimization commands just to produce a capacity spike. Check the current Fabric pricing and licensing pages before provisioning paid resources. Clean up items and stop/resize capacity according to your organization's policies when finished.

### 13.2 Lab sequence

1. Create a workspace on eligible capacity and create a lakehouse named, for example, `SalesLakehouse`.
2. Upload `data/sample_sales.csv` to the lakehouse at `Files/landing/sample_sales.csv`.
3. Attach the lakehouse to a Spark notebook and run the notebook script in `notebooks/bronze_silver_gold.py` cell-by-cell.
4. Verify `bronze_sales` and `silver_sales` table counts, schema, null checks, duplicate key behavior, and sales totals.
5. Create an ADLS Gen2 shortcut under the lakehouse `Files` area to a test directory at least one level below the container (for example, `Files/shortcuts/adls_sales`). Configure a supported connection and least-privilege source access. For a Parquet folder, query the shortcut without copying it by running `spark.read.format("parquet").load("/lakehouse/default/Files/shortcuts/adls_sales")` in the attached notebook. This path assumes the shortcut is created at that exact lakehouse-relative location and the target contains Parquet files. If the target is a Delta table, use the documented Delta-compatible access pattern for that source and verify it in the current Fabric runtime. If no eligible ADLS account is available, document that the external shortcut step was not executed; do not substitute a fake shortcut.
6. Open the lakehouse SQL analytics endpoint and query `dbo.silver_sales`. Verify that the endpoint is read-only for table data.
7. Create a Fabric Warehouse, adapt and run `sql/gold-layer.sql` using the actual item name and supported query context, and compare totals.
8. Create a data pipeline with the order in `pipeline/pipeline-design.md`; schedule it only after a successful manual run. Confirm the retry/re-run strategy is safe for the overwrite-based lab.
9. If supported, create a Power BI semantic model in Direct Lake mode and validate model binding, relationships, measures, row-level security, and report access. If the mode is unavailable, record the tenant/capacity limitation and use the SQL analytics endpoint for the query portion.
10. After running the workflow, inspect the Capacity Metrics app and record observations without inventing values.
11. If the workspace is connected to Git, commit the notebook/SQL/configuration where supported, deploy to a test workspace, and verify item bindings and connections. This step is conditional on tenant settings and supported item types.

### 13.3 Expected observations (not claimed results)

- Bronze should preserve the raw source values plus ingestion timestamp.
- The provided CSV has 13 data rows. Given its two invalid records (blank `sale_id` and negative `quantity`) and one repeated `S1003` key, this example is expected to yield 13 bronze rows and 10 silver rows. Treat these as dataset-derived expectations to verify in the tenant, not as observed execution results.
- Silver should have typed timestamp/numeric fields and no null/empty sale IDs among accepted records; invalid values are filtered by the example code.
- The gold aggregate should contain one row per date/region/product-category combination represented by silver data.
- A shortcut should reference external data without intentionally creating a separate edge copy; actual access still depends on source connection, permissions, and source availability.
- The lakehouse SQL analytics endpoint should allow T-SQL reads of exposed Delta tables but not table-data DML.
- Capacity metrics may show a small/brief workload with little visible detail; a trial/limited capacity may not expose every feature.

These are expected behaviors to validate, not results observed in this environment. No Fabric tenant was provisioned or tested as part of writing this lesson.

### 13.4 Validation checklist

- [ ] Workspace and lakehouse exist on eligible capacity.
- [ ] CSV is present at the documented Files path.
- [ ] Bronze and silver Delta tables exist with expected schema.
- [ ] Invalid rows and duplicate keys are handled according to the stated lab rule.
- [ ] Silver totals reconcile to the accepted bronze rows.
- [ ] ADLS shortcut can be queried by an authorized identity, or the missing prerequisite is documented.
- [ ] SQL analytics endpoint query succeeds and table-data write behavior is understood.
- [ ] Warehouse gold aggregation succeeds and reconciles with silver.
- [ ] Pipeline activities execute in dependency order; rerun behavior is understood.
- [ ] Direct Lake model was tested or the limitation was recorded.
- [ ] Capacity Metrics app was reviewed if permissions/data are available.
- [ ] No secrets were committed to Git or placed in notebook source.

### 13.5 Cleanup

1. Stop running notebooks and pipelines.
2. Delete the lab-created Warehouse, lakehouse, notebook, pipeline, semantic model, and shortcut if they are no longer needed and your organization's retention policy allows it. Deleting a shortcut should not delete the external source data, but verify the UI's deletion confirmation.
3. Remove only the lab-specific ADLS test files/container if you created them and have approval; do not delete a shared source folder.
4. Disconnect the lab workspace from Git only if it is no longer needed and your team permits it. Do not delete a shared repository.
5. If you created a paid capacity solely for the lab, pause/delete it only under the account's billing and governance process. Confirm the actual billing effect in current terms; storage and other resources may incur charges separately.
6. Remove temporary access grants and credentials/connections that are no longer required.

## 14. Practice exercises and answer key

### Exercise 1 — Architecture
A team stores raw JSON, cleans it with Spark, publishes a sales data mart, and serves Power BI dashboards. Propose the Fabric items and explain which components share storage and which have distinct compute behavior.

### Exercise 2 — Shortcut or copy?
An ADLS folder owned by another team is updated every five minutes. Your analysts need read access, but a month-end audit also requires an immutable snapshot. Propose a design.

### Exercise 3 — Lakehouse or Warehouse?
A workload is 90% T-SQL transformations over well-defined fact and dimension tables, with a small amount of raw JSON ingestion. Choose the starting architecture and explain the trade-off.

### Exercise 4 — Direct Lake and security
A semantic model user can view a report but must not query the full lakehouse table directly. What permissions and validation are needed?

### Exercise 5 — Capacity
A notebook and semantic-model refresh run at the same time, and interactive users see delays. What do you inspect before purchasing a larger capacity?

### Exercise 6 — Deployment
A Direct Lake semantic model is deployed from Dev to Test but remains bound to the Dev lakehouse. What likely happened and how do you fix it?

### Suggested answers

1. Store raw JSON in Files or a bronze landing area; transform with a notebook/Spark into bronze and silver Delta tables; build a Warehouse or gold Delta table based on SQL/BI needs; create a semantic model/report. OneLake is the shared logical lake, but Spark, Warehouse, SQL endpoint, pipelines, and Power BI remain distinct experiences with their own execution and permission behavior.
2. Use a shortcut for current governed access if the connection and permissions meet the requirement. Separately create a dated/immutable snapshot for month-end audit, with retention controls and reconciliation metadata. A shortcut alone does not provide an immutable snapshot.
3. A Warehouse is a strong candidate for the SQL-first curated mart; keep raw JSON ingestion in a lakehouse/Files/Spark or pipeline. Avoid forcing all raw processing into Warehouse, but don't create a lakehouse merely to follow a pattern if a simpler design meets the workload.
4. Share the report/model with least privilege, apply appropriate semantic-model RLS, restrict direct lakehouse/SQL endpoint access, test OneLake/SQL permissions and any Direct Lake fallback behavior, and verify with the actual user's identity. Report access is not a substitute for data-layer security.
5. Inspect Capacity Metrics by item and time window; identify overlapping CU consumers, Spark shuffles, repeated scans, file sizes, semantic model query/refresh patterns, pipeline schedules, and throttling signals. Optimize the workload and scheduling first; right-size based on measured peak/concurrency and SLA.
6. Cross-stage deployment does not always rebind Direct Lake models to paired target items automatically. Use the supported deployment datasource rules/binding mechanism, then verify the model points to the target lakehouse and rerun smoke tests.

## 15. Checkpoint

You are ready to move on when you can explain and demonstrate all of the following:

- [ ] Explain OneLake, shortcuts, and capacities.
- [ ] Build a bronze → silver → gold flow in Fabric.
- [ ] Choose lakehouse vs Warehouse for a stated workload.
- [ ] Explain Direct Lake and capacity throttling.
- [ ] Distinguish Files, Delta Tables, SQL analytics endpoint, and Warehouse.
- [ ] Explain the security boundaries between workspace, item, OneLake, SQL, and semantic model.
- [ ] Inspect Capacity Metrics and identify a measured optimization or capacity decision.
- [ ] Explain why a shortcut is not the same as an immutable copy.
- [ ] Explain how Git and deployment pipelines fit into environment promotion and what still needs post-deployment validation.

## 16. Troubleshooting

| Symptom | Likely cause | What to check |
|---|---|---|
| Notebook cannot find CSV | File was uploaded to a different folder or wrong default lakehouse is attached | Confirm `Files/landing/sample_sales.csv`, attached lakehouse, and path spelling |
| `saveAsTable` fails | Missing write permissions, table name conflict, invalid schema, or session/namespace issue | Check workspace role, attached lakehouse, table state, and full error |
| SQL endpoint cannot see a Spark table | Table is not a supported Delta table, metadata discovery has not completed, or query uses wrong item/context | Confirm Delta format/table registration and correct SQL endpoint; refresh/retry metadata as documented |
| `INSERT`/`UPDATE` fails in SQL analytics endpoint | Endpoint is read-only for table data | Use Spark or a supported write path; use Warehouse for writable SQL analytical tables |
| Cross-item query fails | Wrong item name, unsupported object/context, or missing permissions | Verify exact three-part name, SQL endpoint context, and permissions |
| Shortcut is visible but reads fail | Source credential/connection, source ACL, network, or connector limitation | Test source identity and current shortcut prerequisites; do not weaken security blindly |
| Direct Lake option missing or falls back | Capacity/item/semantic-model constraints, model features, or source mode | Confirm current Direct Lake support and source path; inspect model behavior and security configuration |
| Pipeline deployment works but references Dev | Cross-stage binding/connection not remapped | Apply supported deployment rules/rebinding and test target workspace |
| CU spikes or throttling | Concurrent workloads, inefficient scans/shuffles, repeated refreshes, or undersized capacity | Use Capacity Metrics app, optimize code/layout, coordinate schedules, then evaluate SKU |
| VACUUM removes history needed for recovery | Retention was too short or historical readers were not considered | Stop cleanup, review Delta retention/time-travel policy and recovery options; never lower retention casually |

## 17. Official references

Product features and limitations evolve. Check these Microsoft Learn pages before production implementation, especially for shortcuts, mirroring sources, Direct Lake, Git/deployment support, capacity behavior, and Delta maintenance.

1. [What is Microsoft OneLake?](https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview)
2. [OneLake shortcuts](https://learn.microsoft.com/en-us/fabric/onelake/onelake-shortcuts)
3. [What is a lakehouse SQL analytics endpoint?](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-sql-analytics-endpoint)
4. [What is Fabric Data Warehouse?](https://learn.microsoft.com/en-us/fabric/data-warehouse/data-warehousing)
5. [How Direct Lake works](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-how-it-works)
6. [Optimize Delta Lake tables with V-Order](https://learn.microsoft.com/en-us/fabric/data-engineering/delta-optimization-and-v-order)
7. [VACUUM Delta tables](https://learn.microsoft.com/en-us/fabric/data-engineering/delta-lake-vacuum)
8. [Delta table maintenance in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-table-maintenance)
9. [Mirroring overview](https://learn.microsoft.com/en-us/fabric/mirroring/overview)
10. [Fabric Capacity Metrics app](https://learn.microsoft.com/en-us/fabric/enterprise/metrics-app)
11. [Understand capacity throttling and smoothing](https://learn.microsoft.com/en-us/fabric/enterprise/throttling)
12. [Git integration process](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-integration-process)
13. [CI/CD workflow options in Fabric](https://learn.microsoft.com/en-us/fabric/cicd/manage-deployment)
14. [Assign a workspace to a deployment pipeline](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/assign-pipeline)
15. [Lakehouse sharing and permission management](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-sharing)
16. [Workspace roles in a lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/workspace-roles-lakehouse)

---

**Verification note:** This lesson was aligned to the Topic 06 syllabus and lab requirements in the supplied roadmap, and examples were reviewed for internal consistency. The lesson and companion lab files are instructional artifacts; no Fabric workspace, capacity, shortcut, Warehouse, pipeline, semantic model, or live workload was deployed or executed while authoring. Product support and portal labels should be verified against the linked official documentation and the learner's tenant before a production deployment.
