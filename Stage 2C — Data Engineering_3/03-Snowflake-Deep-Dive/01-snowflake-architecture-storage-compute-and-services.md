# Snowflake Architecture: Storage, Compute, and Cloud Services

**Curriculum location:** Stage 2C — Data Engineering_3 / `03-Snowflake-Deep-Dive/`  
**Lesson file:** `01-snowflake-architecture-storage-compute-and-services.md`  
**Level:** Beginner → Intermediate → Advanced  
**Scope:** Topic 01 of `roadmap-Snowflake-Deep-Dive.md`; this lesson establishes the architecture vocabulary needed by the later warehouse, micro-partition, loading, and cost lessons. It does not replace those lessons.

## 1. Prerequisites and learning objectives

### Prerequisites

You should be comfortable with basic SQL (`SELECT`, `WHERE`, `GROUP BY`), relational tables, schemas, cloud object storage at a conceptual level, and Python environments. You do not need to administer Snowflake before beginning. A Snowflake trial/free account is optional for the reading sections and required only for the hands-on lab. Account entitlements and trial availability vary by region and date.

Before running the lab, choose a small warehouse, set a short auto-suspend interval, use non-sensitive sample data, and understand that even a short-lived warehouse can consume credits. Do not put passwords, private keys, or account identifiers in source control.

### Learning objectives

By the end, you should be able to:

1. Explain Snowflake's database-storage, virtual-warehouse-compute, and cloud-services layers and their interactions.
2. Distinguish an organisation, account, cloud provider, region, and edition, and choose a sensible dev/test/prod boundary.
3. Navigate the account → database → schema → object hierarchy and identify common client interfaces.
4. Choose between permanent, temporary, transient, external, and Iceberg tables, and between standard, secure, and materialized views.
5. Query nested JSON using `VARIANT`, `OBJECT`, `ARRAY`, path notation (`:`), and `FLATTEN`.
6. Explain result, warehouse-local-disk, and metadata caching without claiming that one cache proves another.
7. Describe query parsing, compilation/optimization, and execution, and explain the broad billing model for warehouse compute, storage, and cloud services.
8. Compare Snowflake's architecture with Redshift, BigQuery, Databricks SQL, and Apache Spark at the architectural—not marketing—level.

## 2. Beginner lesson: what Snowflake is

### 2.1 Definition and purpose

Snowflake is a managed cloud data platform used for analytical data storage, SQL querying, data engineering, data sharing, and related workloads. It runs on supported public-cloud infrastructure (AWS, Microsoft Azure, or Google Cloud, depending on region and offering); it is not software you install as a self-managed local database or deploy on arbitrary private infrastructure.

A data engineering team uses Snowflake to ingest data, transform it with SQL/Python tooling, expose governed tables and views, and serve BI or analytical consumers. Snowflake manages much of the underlying storage layout, infrastructure maintenance, and query execution infrastructure. That reduces operational work, but does not remove the need to design data models, access policies, query patterns, or cost controls.

**Problem it solves:** in a tightly coupled database, adding query capacity can require changing the same cluster that stores data, and competing workloads can interfere. Snowflake separates persistent storage from independently managed virtual warehouses, so different workloads can query shared governed data using separate compute resources.

**Trade-off:** managed infrastructure is convenient, but compute, storage, data transfer, and certain services have different usage and billing rules. Separation does not mean unlimited performance or free compute.

### 2.2 The three architectural layers

```text
                Users / applications / BI / Python
                              |
                    SQL or connector request
                              v
+----------------------------------------------------------------+
| CLOUD SERVICES                                                 |
| Authentication, access control, metadata, transaction control, |
| query parsing/optimization/coordination, infrastructure services|
+-------------------------------+--------------------------------+
                                | plan + metadata + coordination
                                v
+----------------------------------------------------------------+
| COMPUTE: VIRTUAL WAREHOUSES                                    |
| Independent MPP compute clusters; scan, filter, join, aggregate|
| Warehouse-local cache may help repeated scans                  |
+-------------------------------+--------------------------------+
                                | read/write optimized table data
                                v
+----------------------------------------------------------------+
| DATABASE STORAGE                                               |
| Managed cloud storage; compressed, columnar data and metadata  |
| for native Snowflake tables, plus supported external formats   |
+----------------------------------------------------------------+
```

The diagram is conceptual. Real execution involves interactions among the layers, and not every statement uses every layer in the same way.

| Layer | Responsibility | Production significance | Cost lens |
|---|---|---|---|
| Database storage | Persisted table data and related storage structures/metadata; native tables are reorganized into Snowflake-managed compressed columnar storage | Durable shared data can be queried by multiple warehouses; storage design and retention affect storage volume | Storage is billed separately from a running warehouse; retained historical data and clones can affect storage usage |
| Compute (virtual warehouses) | Executes scans, joins, aggregations, sorts, and other query work using parallel compute | Separate warehouses can isolate ELT, BI, and ad hoc workloads; sizing and suspension affect latency and cost | Warehouse credits accrue while a warehouse runs, subject to product-specific billing rules and minimums |
| Cloud services | Coordinates authentication, authorization, metadata, transaction management, query compilation/optimization, and other platform control-plane work | Enables managed governance and query planning; high metadata/query activity can create cloud-services usage | Cloud-services usage is measured separately; billing adjustments apply under Snowflake's documented rules, including the daily 10% adjustment framework for eligible usage |

**Important:** “cloud services” does not mean all cloud infrastructure costs on your own cloud bill. Snowflake consumption is generally metered through Snowflake credits and storage charges according to the commercial agreement. The underlying cloud provider is part of Snowflake's managed service architecture.

### 2.3 How the layers interact: one query

Imagine a sales table with millions of rows and a request to total sales for one month.

1. A client submits SQL and authenticates to an account.
2. Cloud services check the active role and privileges, resolve object names, inspect metadata, and build/optimize a plan.
3. If the result cache can satisfy the request, Snowflake may return a previously computed result without executing the full data scan.
4. Otherwise, the selected virtual warehouse runs the plan. It reads the required table data from managed storage, possibly benefiting from warehouse-local cache, and performs parallel operations.
5. Snowflake returns result rows to the client. Query history/profile provide evidence about the run, subject to visibility and retention limits.

This is a simplified mental model, not a promise that every query follows a single rigid sequence or uses the same cache.

### 2.4 Accounts, regions, clouds, editions, and organisations

- **Cloud provider:** the underlying cloud platform on which a Snowflake deployment is hosted: AWS, Azure, or Google Cloud, subject to available regions and product support.
- **Region:** a geographic cloud region where the Snowflake account is hosted. Region choice affects data residency, latency to source systems and users, disaster-recovery design, and cross-region transfer/replication considerations.
- **Account:** the primary administrative and security boundary for a Snowflake deployment. It has users, roles, databases, warehouses, policies, usage, and account-level configuration. An account is associated with a cloud/region and an edition/service configuration.
- **Organisation:** a grouping that can manage multiple Snowflake accounts, support organisation-level visibility and governance capabilities, and simplify account administration. Exact features depend on account configuration and Snowflake's current organisation capabilities.
- **Edition:** a service tier that determines availability of some features and protections, such as certain governance, recovery, and security capabilities. Do not assume a feature exists in every edition; verify the current feature matrix and contract.
- **Multiple accounts:** commonly used to isolate production from non-production, separate business units, or meet regional/compliance needs. They add stronger isolation but require deliberate identity, deployment, sharing, and monitoring design.

A region is not a schema, and an edition is not a compute size. A warehouse size is a compute configuration, not an account edition.

### 2.5 Object hierarchy

```text
Organisation (may contain multiple accounts)
└── Account
    ├── Users, roles, warehouses, integrations, policies
    └── Database
        └── Schema
            ├── Tables (permanent / temporary / transient / external / Iceberg)
            ├── Views (standard / secure / materialized)
            ├── Stages and file formats
            ├── Sequences, functions, procedures, and other objects
            └── Other supported schema-level objects
```

A common fully qualified object name is `DATABASE_NAME.SCHEMA_NAME.TABLE_NAME`. The account and organisation are not normally written as leading parts of that three-part SQL identifier. Access depends on active role and granted privileges; knowing an object's name does not imply permission to read it.

### 2.6 Interfaces: Snowsight, SnowSQL, Snowflake CLI, and Python connector

| Interface | Best fit | Trade-offs / cautions |
|---|---|---|
| **Snowsight** | Browser UI for worksheets, query history/profile, object exploration, administration, and supported monitoring features | Easy for exploration; manual clicks are less reproducible than version-controlled SQL and deployment automation |
| **SnowSQL** | Legacy/established command-line SQL client, scripting, and interactive SQL workflows where supported | Check current support and lifecycle guidance; do not automatically choose it for a new CLI workflow without checking Snowflake's current recommendation |
| **Snowflake CLI** | Current command-line tooling for Snowflake development/deployment and related workflows | CLI commands and configuration can evolve; pin and document versions in team workflows |
| **Python Connector** | Python applications, data jobs, tests, and scripts that submit SQL and fetch results | Credentials, network policy, retries, result size, and connection lifecycle must be handled deliberately |

Example SQL session in Snowsight or a SQL CLI:

```sql
SELECT CURRENT_ACCOUNT(), CURRENT_REGION(), CURRENT_ROLE(), CURRENT_WAREHOUSE();
```

The returned values depend on the authenticated account and active session. This is a diagnostic query; it does not create or change resources.

Example Python connector session (install first with `python -m pip install snowflake-connector-python`; use your approved secret manager/environment variables):

```python
import os
import snowflake.connector

conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],  # Prefer SSO/key-pair/OAuth where appropriate.
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    database=os.environ["SNOWFLAKE_DATABASE"],
    schema=os.environ["SNOWFLAKE_SCHEMA"],
    role=os.environ.get("SNOWFLAKE_ROLE"),
)
try:
    with conn.cursor() as cur:
        cur.execute("SELECT CURRENT_ACCOUNT(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
        print(cur.fetchone())
finally:
    conn.close()
```

Prerequisites: a valid account identifier and user authentication method, a role with the required privileges, and a warehouse if the query needs one. Environment variable names are examples, not automatically configured values. Do not commit a `.env` file containing credentials. For production, prefer key-pair, OAuth, or SSO/service authentication appropriate to the workload and organisation's policy.

## 3. Intermediate lesson: tables, views, and semi-structured data

### 3.1 Table types and when to use them

| Type | Where data lives / behavior | Recovery and retention considerations | Use when / avoid when |
|---|---|---|---|
| **Permanent** (default) | Native Snowflake-managed table; persists until dropped | Supports configured Time Travel retention; permanent tables have a 7-day Fail-safe period under documented rules. Actual Time Travel retention depends on edition/configuration and object settings | Use for durable business data and curated production datasets. Avoid using it automatically for every disposable scratch result |
| **Temporary** | Session-scoped; visible only in the creating session and purged when that session ends | No Fail-safe; Time Travel retention can be 0 or 1 day while the table exists, but session termination purges the data and it is not recoverable after the session ends | Use for session-specific scratch data. Avoid for shared intermediate data or workflows that must survive session termination |
| **Transient** | Persists until dropped and can be shared by permitted users; data is still stored and charged | No Fail-safe; Time Travel retention is limited (commonly 0 or 1 day, depending on configuration) | Use for reproducible staging/intermediate data that can be rebuilt. Do not use as the only copy of irreplaceable data |
| **External table** | Metadata in Snowflake references files in an external stage; the files remain in external cloud storage; typically read-only through the external table | Recovery and lifecycle depend substantially on the external files and cloud-storage controls, not native-table Time Travel semantics | Use to query supported external data in place when appropriate. Consider load latency, query performance, metadata refresh, and governance trade-offs |
| **Apache Iceberg table** | Uses the Iceberg open table format and metadata/files in configured storage; Snowflake can query/manage supported Iceberg configurations depending on table type/catalog setup | Behavior depends on catalog, ownership mode, storage integration, and supported operations; do not assume every native-table feature or recovery behavior applies | Use when open-format interoperability and lakehouse access matter. Validate catalog ownership, write support, feature limitations, and operational responsibilities before choosing |

Do not treat external tables and Iceberg tables as synonyms. An external table is a Snowflake object that exposes data files through metadata; Iceberg is an open table format with snapshots and metadata semantics, and Snowflake supports specific Iceberg integration modes.

Example:

```sql
CREATE TABLE IF NOT EXISTS orders_permanent (
  order_id NUMBER,
  amount NUMBER(12,2)
);

CREATE TRANSIENT TABLE IF NOT EXISTS orders_stage (
  order_id NUMBER,
  amount NUMBER(12,2)
);

CREATE TEMPORARY TABLE orders_session_scratch (
  order_id NUMBER,
  amount NUMBER(12,2)
);
```

`IF NOT EXISTS` prevents an error if the named object already exists, but does not reconcile an existing table's schema with the definition shown. Temporary tables can shadow same-named permanent/transient objects within the session; avoid reusing production names for scratch tables.

### 3.2 Views, secure views, and materialized views

- **Standard view:** stores a query definition, not a separately maintained full copy of its result. On query, Snowflake evaluates the view definition as part of the query. It is useful for reusable logic and abstraction, but a view alone is not a guarantee of faster queries.
- **Secure view:** a view designed to protect the underlying view definition and support controlled data exposure, including sharing scenarios. Secure does not mean that a poorly designed access policy becomes safe; test privileges and information leakage risks.
- **Materialized view:** stores maintained results for supported query patterns so eligible queries can reuse precomputed data. It can improve latency, but maintenance and storage have costs and restrictions. Use only after measuring benefit against maintenance overhead.

Use a standard view for semantic reuse, a secure view where definition protection/controlled exposure is needed, and a materialized view only when supported query patterns and measured workload justify its maintenance cost. View features and restrictions can change; consult current documentation before designing around them.

### 3.3 Semi-structured types: VARIANT, OBJECT, ARRAY

- **`VARIANT`** can hold a value of different supported types, including JSON-like objects and arrays. It is the usual landing type for flexible semi-structured payloads.
- **`OBJECT`** represents key-value pairs (an object/map-like structure).
- **`ARRAY`** represents an ordered collection of values.

Snowflake's colon path syntax accesses nested fields from a semi-structured value. The result is generally a semi-structured value; use casts such as `::STRING` or `::NUMBER` when a typed scalar is required. JSON keys are case-sensitive in path expressions unless quoted/handled according to identifier/path rules. Missing keys and type mismatches can yield `NULL` or conversion errors depending on the operation.

Example data:

```sql
CREATE OR REPLACE TABLE events_json (
  event_id NUMBER,
  payload VARIANT
);

INSERT INTO events_json (event_id, payload)
SELECT 1, PARSE_JSON('{"user":{"id":42,"country":"IN"},"items":[{"sku":"A1","qty":2},{"sku":"B2","qty":1}]}');
```

Query nested fields:

```sql
SELECT
  event_id,
  payload:user.id::NUMBER AS user_id,
  payload:user.country::STRING AS country
FROM events_json;
```

Expand array elements with `FLATTEN`:

```sql
SELECT
  e.event_id,
  f.index AS item_index,
  f.value:sku::STRING AS sku,
  f.value:qty::NUMBER AS quantity
FROM events_json AS e,
LATERAL FLATTEN(INPUT => e.payload:items) AS f;
```

`FLATTEN` is a table function that turns array/object elements into rows. `LATERAL` allows the function to reference the current row's payload. If the array is missing or empty, default flatten behavior may produce no row for that parent; `OUTER => TRUE` can preserve a parent row with null expansion fields when that is the desired semantics. Check row counts after flattening: arrays multiply parent rows and can accidentally inflate aggregates.

### 3.4 Three different caches

Caching is a major source of misleading benchmark results. These mechanisms are distinct and have different evidence. The roadmap uses “metadata cache” as a learning category; unlike persisted result reuse and warehouse-local data caching, metadata-driven planning/pruning is not a general user-toggleable cache with a single definitive cache-hit flag.

| Cache | What it reuses | Scope and typical behavior | Evidence / limitation |
|---|---|---|---|
| **Persisted query result cache** | Results of an eligible prior query | Persisted results normally expire after 24 hours; reuse can reset the expiry, up to a documented maximum of 31 days from the original execution. Eligible results can be reused across sessions and warehouses. Reuse depends on query identity and eligibility/invalidation rules | In Query Profile, the **Query Result Reuse** operator is direct evidence for that query. Account Usage `BYTES_READ_FROM_RESULT` can corroborate after its latency window. Query text, data changes, privileges, and configuration affect eligibility. A fast query alone does not prove result-cache use |
| **Warehouse local disk cache** | Data already fetched from remote storage that remains in the running warehouse's local cache | Tied to the warehouse's lifecycle and available cache capacity; a suspended warehouse loses its local cache. A running warehouse can reuse cached data for eligible scans | Compare Query Profile and scan metrics across controlled runs. Runtime alone is weak evidence; the same result can be fast due to result cache, metadata pruning, or other effects |
| **Metadata cache / metadata-based optimization** | Metadata/statistics used to resolve objects, prune data, and plan/answer some operations without scanning all table data | Metadata is managed by Snowflake services; it is not the same as a warehouse-local copy of table data. Certain metadata-only queries can avoid scanning data | Query Profile, bytes scanned, partitions scanned, and query type provide clues. There is no universal user command that proves every metadata lookup was served from a particular cache |

**Key lab distinction:** repeating the identical query may test the result cache. To investigate local disk cache, use a query that actually scans data, disable/avoid result-cache reuse for the experiment, and compare a warm run with a run after warehouse suspension/resumption. A resumed warehouse is cold with respect to its prior local cache, but query timing still has noise. Metadata behavior is often inferred from profile/scan evidence rather than directly toggled or conclusively proven by a single experiment.

To avoid accidentally reusing a persisted result while testing execution, a session can use:

```sql
ALTER SESSION SET USE_CACHED_RESULT = FALSE;
```

This disables reuse of persisted query results for that session; it does **not** disable warehouse-local disk caching or metadata-based optimization. Restore the default after the experiment if needed:

```sql
ALTER SESSION UNSET USE_CACHED_RESULT;
```

## 4. Advanced lesson: query lifecycle, billing, and environment boundaries

### 4.1 Query lifecycle

```text
Client submits SQL
       |
       v
1. Parse and validate syntax
       |
       v
2. Resolve names, types, roles, privileges, and metadata
       |
       v
3. Compile / optimize logical operations into an execution plan
       |       (cloud-services work; exact internal stages are managed)
       v
4. Check eligible result reuse and prepare execution
       |
       v
5. Warehouse executes parallel scans / joins / aggregates
       |       (compute; may use local cache and read storage)
       v
6. Produce and return rows; record history/profile evidence
```

This is a teaching model, not a promise that Snowflake exposes each internal stage as a separate event. Optimization can rewrite query plans, and result-cache checks can affect whether execution proceeds through the full warehouse path.

- **Parsing:** validates SQL grammar and creates a representation of the statement.
- **Compilation/name resolution:** resolves identifiers and types and checks applicable privileges.
- **Optimization:** uses metadata and cost/heuristic decisions to choose an efficient plan, including join order and pruning opportunities.
- **Execution:** a warehouse performs the data-processing operators in parallel, reads required data, and returns results.

If a query is slow, do not immediately increase warehouse size. First determine whether time is spent queued, compiling, scanning too much data, spilling, joining poorly, or returning too many rows. The later warehouse and micro-partition lessons cover these topics in depth.

### 4.2 Billing implications of the layers

1. **Storage:** native table data consumes storage. Retention, historical data, clones that diverge, and other stored objects can affect usage. External files are billed by the external cloud provider; Snowflake may charge for related Snowflake services or query activity according to the feature.
2. **Warehouse compute:** virtual warehouses consume credits while running. Auto-suspend, right-sizing, workload isolation, and avoiding idle time are core cost controls. A result-cache hit can avoid much of the compute that a full execution would require, but never assume it without evidence.
3. **Cloud services:** cloud services consume resources for operations such as authentication, metadata, optimization, and transaction coordination. Snowflake calculates the cloud-services adjustment daily in UTC: eligible cloud-services usage is billed only to the extent it exceeds 10% of that day's eligible virtual-warehouse usage. Serverless compute does not count toward the warehouse-usage denominator for this adjustment. The adjustment never exceeds actual cloud-services usage, and the exact calculation/exclusions are product-documented. This is not a promise that cloud-services usage is always free or capped at 10% of total cost.
4. **Other services:** serverless features, data transfer, replication, marketplace products, and other capabilities may have separate usage/billing models. They are outside this lesson's detailed scope.

Use current account usage views and commercial documentation for reconciliation. Account Usage views can have latency (for example, documented metering views may lag by hours), so they are not necessarily real-time billing dashboards.

### 4.3 Dev/test/prod: databases or separate accounts?

| Pattern | Advantages | Risks / costs | Good fit |
|---|---|---|---|
| Separate schemas in one database | Minimal setup; convenient for a single learner or tightly controlled prototype | Weak separation; easy to mix environments; privileges and naming mistakes can cross boundaries | Personal lab only, or very small low-risk use |
| Separate databases in one account | Clearer object separation and grants; easy to share account services and administration | Accounts still share a major security/admin boundary; users may have cross-environment privileges; quotas, policies, and some configuration remain account-wide | Small teams with mature role design and low regulatory isolation requirements |
| Separate accounts for dev/test/prod | Stronger administrative/security boundary, distinct policies/configuration and usage visibility; production blast radius is reduced | More setup and governance; deployment promotion, identity, replication/sharing, and cross-account operations need design | Production systems, regulated workloads, multiple teams, or where independent access and policy boundaries matter |

**Recommendation:** choose boundaries from threat model, compliance, blast radius, operational ownership, and cost attribution—not convenience alone. Even with separate accounts, automate repeatable deployments and prevent production data from being copied into lower environments without appropriate masking and approval. Never treat a separate schema as equivalent to a separate account security boundary.

### 4.4 Iceberg and open table formats (awareness)

Apache Iceberg is an open table format that defines table metadata, snapshots, and data-file organization for analytic tables. Snowflake supports Iceberg table configurations that integrate Snowflake query/compute capabilities with Iceberg data and metadata, but details differ by catalog and ownership mode. Native Snowflake tables and Iceberg tables are not identical in storage ownership, write behavior, metadata lifecycle, or feature availability.

**Why it matters:** open formats can support interoperability across engines and reduce dependence on one table format. **Trade-offs:** catalog coordination, permissions, compaction/maintenance ownership, feature compatibility, and write concurrency become architectural concerns. Before adopting it, validate current support for the chosen catalog, cloud, region, and operation set.

**Polaris / Open Catalog awareness:** Polaris Catalog was announced as an open catalog implementation for Apache Iceberg and became part of the Snowflake Open Catalog story. Current Snowflake documentation also directs new customers toward Snowflake Horizon Catalog for Iceberg interoperability, while existing Open Catalog customers may continue using that service. Treat Polaris/Open Catalog as an evolving product lineage rather than assuming historical names, signup paths, or feature availability are unchanged. Check the current official catalog documentation before selecting a catalog. This lesson requires awareness, not catalog deployment.

### 4.5 Cortex AI, Streamlit, and Native Apps (awareness only)

- **Cortex AI:** Snowflake capabilities for building AI/LLM-powered workflows close to governed enterprise data. Availability, model choices, regional support, and consumption models are product- and region-dependent.
- **Streamlit in Snowflake:** supports data applications and interactive interfaces that can run in Snowflake's ecosystem. It is an application layer, not a replacement for warehouse architecture.
- **Native Apps:** packaging and distributing application logic within Snowflake's ecosystem, with controlled access to data and platform capabilities. This is broader than a SQL view and has its own security and distribution model.

These are extensions around the core platform. The objective here is to know they exist and where they fit, not to learn their APIs or build an application.

## 5. Platform comparison: architecture and trade-offs

Products change, and each platform has multiple deployment modes. The following is a conceptual comparison; verify current product-specific behavior before selecting a platform.

| Platform | Main architectural model | Compute/storage relationship | Strengths | Trade-offs / operational considerations |
|---|---|---|---|---|
| **Snowflake** | Managed analytical data platform with storage, virtual warehouses, and cloud services separated | Persistent data is shared across independently managed warehouses; warehouse-local caching is separate from persistent storage | Workload isolation, low infrastructure administration, SQL-first analytics, managed optimization | Credit-based compute and separate storage/services billing; proprietary platform behavior; feature/edition/region differences |
| **Amazon Redshift** | Managed MPP warehouse; provisioned clusters and Serverless are different operating modes | In provisioned clusters, compute nodes store/process data; RA3 and managed storage separate some storage capacity from compute, while Serverless abstracts capacity | Tight AWS integration, mature SQL analytics, multiple provisioning options | Architecture and scaling depend on chosen mode; cluster/node design and workload management remain important in provisioned setups |
| **Google BigQuery** | Serverless-oriented analytical warehouse with separated storage and query capacity/slots | Storage and compute capacity are decoupled; query execution uses managed distributed infrastructure | Low infrastructure administration, strong GCP integration, on-demand or capacity-based pricing models | Query cost/performance depends on bytes scanned, slots/capacity, partitioning, reservations, and workload configuration |
| **Databricks SQL** | SQL analytics over a lakehouse, commonly using Delta Lake and cloud object storage with managed compute | Compute warehouses access data in lake storage; caching and compute modes depend on configuration | Lakehouse integration, Spark ecosystem, open data formats, unified engineering/analytics workflows | More architecture choices across catalog, file/table layout, compute policy, and governance; performance depends on data layout and runtime configuration |
| **Apache Spark** | Distributed processing engine, usually deployed on a cluster or managed service | Compute processes data from object storage, distributed filesystems, or other sources; persistent storage is not inherently a single warehouse | General distributed batch/stream processing, flexible APIs, large ecosystem, open-source engine | Not a complete managed warehouse by itself; deployment, scheduling, catalog, security, file layout, and cluster sizing depend on the surrounding platform |

**Shared-nothing vs decoupled storage/compute:** shared-nothing describes distributed compute nodes that own/handle partitions of data and work. Decoupled storage/compute means persistent data can be separated from independently provisioned processing capacity. These are not mutually exclusive labels: Snowflake uses parallel compute clusters while sharing a central persistent data layer, which combines ideas from shared-disk and shared-nothing designs. Redshift provisioned clusters historically couple node storage and compute more closely, while RA3/managed storage and Serverless change the trade-offs. Spark is an execution engine, not a direct one-to-one equivalent to a fully managed warehouse product.

### Choosing between them

- Choose based on workload shape, team skills, governance, latency, concurrency, ecosystem, portability requirements, and measured total cost—not on one feature table.
- Benchmark representative queries with realistic data and concurrency. Include data ingestion, storage, compute, egress, operations, and governance in total cost.
- For a team already standardized on one cloud, cloud-native integration may be a major factor, but it should not substitute for workload testing.

## 6. Practical lab: `experiments/01_architecture/`

### 6.1 Lab safety and setup

**Goal:** create minimal objects, inspect table lifecycles, query JSON, investigate caches, and compare architectures. This is a teaching experiment, not a production benchmark.

1. Use a trial/free account or an approved sandbox. Use a role with permission to create the lab database and warehouse (typically a controlled administrative role or explicitly granted creation privileges), plus ownership/creation privileges for the lab schemas and tables.
2. Choose names unique to this run (for example, append a short personal suffix to `ARCH_LAB_DB` and `ARCH_LAB_WH`). If a name already exists, change the name before running setup. The setup intentionally fails on collisions rather than silently reusing resources that cleanup could delete.
3. Use an `X-SMALL` warehouse if available. Set `AUTO_SUSPEND` and `AUTO_RESUME`; suspend or drop the warehouse after the lab.
3. If your account has resource monitors available, configure one according to your organisation's permissions and policy. Resource monitors do not necessarily control every serverless feature, so do not rely on one as the only safety measure.
4. Use synthetic data only. Do not load personal or confidential JSON.
5. Run statements in order and record actual observations from Snowsight Query History/Profile. No outputs are promised here because the SQL has not been executed in your account.

### 6.2 Create database, schemas, warehouse, and tables

Run with a role permitted to create these objects. Adapt names if they already exist; `CREATE OR REPLACE` can drop/recreate an object and is not harmless in a shared account.

```sql
-- Use unique, lab-owned names. If either name already exists, choose a new suffix.
CREATE DATABASE ARCH_LAB_DB;
CREATE SCHEMA ARCH_LAB_DB.PERMANENT_SCHEMA;
CREATE SCHEMA ARCH_LAB_DB.TRANSIENT_SCHEMA;

CREATE WAREHOUSE ARCH_LAB_WH
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

USE WAREHOUSE ARCH_LAB_WH;
USE DATABASE ARCH_LAB_DB;
USE SCHEMA PERMANENT_SCHEMA;

CREATE TABLE TABLE_LIFECYCLE_PERMANENT (
  id NUMBER,
  note STRING
);

CREATE TRANSIENT TABLE ARCH_LAB_DB.TRANSIENT_SCHEMA.TABLE_LIFECYCLE_TRANSIENT (
  id NUMBER,
  note STRING
);

CREATE TEMPORARY TABLE TABLE_LIFECYCLE_TEMPORARY (
  id NUMBER,
  note STRING
);

INSERT INTO TABLE_LIFECYCLE_PERMANENT VALUES (1, 'permanent sample');
INSERT INTO ARCH_LAB_DB.TRANSIENT_SCHEMA.TABLE_LIFECYCLE_TRANSIENT VALUES (1, 'transient sample');
INSERT INTO TABLE_LIFECYCLE_TEMPORARY VALUES (1, 'session sample');

SHOW TABLES IN SCHEMA ARCH_LAB_DB.PERMANENT_SCHEMA;
SHOW TABLES IN SCHEMA ARCH_LAB_DB.TRANSIENT_SCHEMA;
```

**Observe and record:** object type, row visibility from the same session, and what happens after the Snowflake session actually ends for the temporary table. Closing a browser tab or client connection is not always the same as immediately terminating the server-side session. Temporary-table data is purged when its session ends and is not recoverable after that. Do not attempt to prove Fail-safe behavior by inducing a system failure; that is not a safe or reproducible lab. Table type determines lifecycle/recovery guarantees, but storage cost is not necessarily zero for transient data. All retained table data can incur storage charges.

To inspect table definitions, run `DESCRIBE TABLE ...`. To inspect storage and retention properties, use Snowsight object details or the appropriate supported metadata/account-usage views available to your role. Account Usage views may lag, and tiny sample tables may be too small to produce meaningful storage measurements.

### 6.3 Load JSON into VARIANT and flatten an array

```sql
CREATE TABLE ARCH_LAB_DB.PERMANENT_SCHEMA.EVENTS_JSON (
  event_id NUMBER,
  payload VARIANT
);

INSERT INTO ARCH_LAB_DB.PERMANENT_SCHEMA.EVENTS_JSON (event_id, payload)
SELECT 1001, PARSE_JSON(
  '{"user":{"id":42,"country":"IN"},"items":[{"sku":"A1","qty":2},{"sku":"B2","qty":1}]}'
);

SELECT
  event_id,
  payload:user.id::NUMBER AS user_id,
  payload:user.country::STRING AS country
FROM ARCH_LAB_DB.PERMANENT_SCHEMA.EVENTS_JSON;

SELECT
  e.event_id,
  f.index AS item_index,
  f.value:sku::STRING AS sku,
  f.value:qty::NUMBER AS qty
FROM ARCH_LAB_DB.PERMANENT_SCHEMA.EVENTS_JSON AS e,
LATERAL FLATTEN(INPUT => e.payload:items) AS f
ORDER BY item_index;
```

**Expected observations, not fabricated outputs:** the first query projects the nested user id and country as typed scalar columns. The second produces one row per array element, with the SKU and quantity extracted from each object. If the results differ, verify the JSON string, path spelling/case, active database/schema, and whether the insert ran successfully.

### 6.4 Investigate result-cache behavior

First create a modest synthetic table to make the query do actual work rather than relying on a metadata-only `COUNT(*)` result. This creates 100,000 rows; it is deliberately small enough for a lab, not a benchmark:

```sql
CREATE TABLE ARCH_LAB_DB.PERMANENT_SCHEMA.CACHE_TEST AS
WITH generated AS (
  SELECT SEQ4() AS id
  FROM TABLE(GENERATOR(ROWCOUNT => 100000))
)
SELECT id, RPAD(TO_VARCHAR(id), 100, 'x') AS payload
FROM generated;
```

Run this deterministic aggregate and note its query ID, duration, and Query Profile:

```sql
SELECT
  SUM(id) AS id_sum,
  COUNT(*) AS row_count,
  SUM(LENGTH(payload)) AS payload_chars
FROM ARCH_LAB_DB.PERMANENT_SCHEMA.CACHE_TEST;
```

Repeat the **exact same SQL text** without changing data, role, or relevant configuration. In Query Profile, look for the **Query Result Reuse** operator on the second query; it is direct evidence that persisted results were reused. The Information Schema `QUERY_HISTORY` table function can help identify the query IDs and compare execution/scan metrics shortly after the test (adjust the database qualifier if needed):

```sql
SELECT
  query_id,
  start_time,
  query_text,
  execution_time,
  total_elapsed_time,
  bytes_scanned
FROM TABLE(ARCH_LAB_DB.INFORMATION_SCHEMA.QUERY_HISTORY(
  END_TIME_RANGE_START => DATEADD('minute', -30, CURRENT_TIMESTAMP()),
  RESULT_LIMIT => 1000
))
WHERE query_text ILIKE '%CACHE_TEST%'
  AND query_text ILIKE '%SUM(ID)%'
  AND query_text NOT ILIKE '%INFORMATION_SCHEMA.QUERY_HISTORY%'
ORDER BY start_time DESC;
```

The recent-query table function is useful for identifying the two test query IDs and comparing elapsed/execution time and scan bytes, but it does not expose every Account Usage column. For a delayed corroborating check, query the Account Usage view after its latency window:

```sql
SELECT
  query_id,
  start_time,
  query_text,
  execution_time,
  bytes_scanned,
  bytes_read_from_result,
  partitions_scanned,
  partitions_total
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD('hour', -2, CURRENT_TIMESTAMP())
  AND query_text ILIKE '%CACHE_TEST%'
  AND query_text ILIKE '%SUM(ID)%'
  AND query_text NOT ILIKE '%ACCOUNT_USAGE.QUERY_HISTORY%'
ORDER BY start_time DESC;
```

The Account Usage view can lag by up to about 45 minutes, so it might not show the just-run queries immediately. Use the Snowsight Query History/Profile result-reuse indicator as the primary immediate evidence; the view's result-read and scan metrics are corroborating evidence. Do not infer a cache hit from elapsed time alone. Exact eligibility rules are Snowflake-managed and can change.

For a controlled execution comparison, disable persisted result reuse for the session:

```sql
ALTER SESSION SET USE_CACHED_RESULT = FALSE;
SELECT
  SUM(id) AS id_sum,
  COUNT(*) AS row_count,
  SUM(LENGTH(payload)) AS payload_chars
FROM ARCH_LAB_DB.PERMANENT_SCHEMA.CACHE_TEST;
```

This prevents the persisted result cache from masking execution. The 100,000-row table is intentionally modest; execution can still be fast, and result-cache reuse is never guaranteed. Re-enable the default after testing:

```sql
ALTER SESSION UNSET USE_CACHED_RESULT;
```

### 6.5 Investigate warehouse-local disk cache

Use the `CACHE_TEST` table for the initial local-disk-cache experiment. Its 100,000 rows are intentionally modest, so a measurable difference is not guaranteed. Do not create a huge synthetic dataset just to see a timing difference; if the experiment is inconclusive, record that result or request approval to use a larger non-sensitive test dataset.

Use the same deterministic scan/aggregation query for each run:

```sql
SELECT
  MOD(id, 1000) AS bucket,
  COUNT(*) AS row_count,
  SUM(LENGTH(payload)) AS payload_chars
FROM ARCH_LAB_DB.PERMANENT_SCHEMA.CACHE_TEST
GROUP BY 1
ORDER BY 1;
```

1. Set `USE_CACHED_RESULT = FALSE` for the session so a persisted result does not short-circuit execution.
2. Run a representative scan/aggregation against an existing test table. Capture query ID, bytes scanned, partitions scanned, execution time, and Query Profile details.
3. Repeat the same query while the warehouse remains running. Compare profile evidence and timing; the second run may benefit from local cache, but caching is not guaranteed and timings are noisy.
4. Suspend the warehouse (`ALTER WAREHOUSE ARCH_LAB_WH SUSPEND`) and resume it (`ALTER WAREHOUSE ARCH_LAB_WH RESUME`). Re-run the query. Suspension discards warehouse-local cache, so the resumed warehouse starts without that prior local cache.
5. Compare scan and timing evidence across runs. Record alternative explanations such as cloud variance, compilation overhead, result size, pruning, and concurrent activity.
6. Restore default session behavior with `ALTER SESSION UNSET USE_CACHED_RESULT`.

**Do not claim local cache was proven from runtime alone.** Stronger evidence is a consistent profile difference across controlled repeats, with persisted result reuse disabled and comparable data/warehouse conditions. The platform does not provide a universal switch that directly exposes every cache hit as a simple truth value.

### 6.6 Investigate metadata caching/metadata-based optimization

Metadata can help Snowflake resolve objects, prune micro-partitions, and answer some metadata-oriented queries without reading all table data. The details are managed by the service, and there is no general “turn metadata cache off” lab switch.

Use Query Profile to record bytes scanned and partitions scanned for a query that filters a table by a selective predicate. Compare that evidence with a query that returns metadata or uses a supported metadata-only path, if appropriate. Keep result-cache reuse disabled when comparing actual execution. Treat low/zero bytes scanned as evidence consistent with pruning or metadata-based execution—not proof that a specific internal metadata cache served every operation. Unlike result-cache reuse, this mechanism cannot be cleanly toggled off by a general session parameter; the lab's result is an evidence-based explanation, not a definitive internal cache-hit proof.

Avoid drawing conclusions from a tiny table: it may fit in a few micro-partitions and may not reveal meaningful pruning behavior. Large-scale partitioning and pruning are covered in the dedicated micro-partitions lesson.

### 6.7 Compare Snowflake with another platform

Write a one-page comparison with **one** platform you know. Include:

- What is managed vs user-managed?
- How are persistent storage and compute capacity related?
- How does compute scale, and how is it billed?
- What are the operational responsibilities for data layout, catalog, permissions, and performance?
- Which workloads and existing ecosystem make each option attractive?
- What would you measure in a fair benchmark?

Example starting point: compare Snowflake with BigQuery's serverless-oriented model, or with provisioned Redshift clusters. Use current official documentation and distinguish provisioned vs serverless modes where applicable. Do not write “Snowflake is always faster/cheaper” without representative measurements.

### 6.8 Troubleshooting

| Symptom | Likely causes | What to check |
|---|---|---|
| `CREATE` fails with privilege error | Active role lacks database/schema/warehouse creation privilege | `SELECT CURRENT_ROLE()`; request least-privilege grants or use an approved sandbox role |
| Query says warehouse is not selected | No active warehouse in session | `USE WAREHOUSE ARCH_LAB_WH;` and verify it exists/you can use it |
| Nested path returns NULL | Wrong key case/path, malformed JSON, absent key, or type mismatch | Inspect `payload`, verify `PARSE_JSON`, and test each path segment |
| `FLATTEN` returns no rows | Array missing/empty, wrong path, or parent row absent | Query `payload:items` directly; check row count and path; consider `OUTER => TRUE` only if semantics require retaining empty parents |
| Cache experiment shows no difference | Table too small, query not scan-heavy, cache not populated, noise, or plan differences | Use controlled repeats, inspect query IDs/profiles, disable result-cache reuse, and avoid claiming more than evidence supports |
| Re-run doesn't show expected table | Temporary table ended with session, wrong database/schema, or same-name temporary table shadowing another table | Fully qualify names and inspect `SHOW TABLES` / session context |
| Unexpected cost | Warehouse remained running, repeated queries, retained data, or service usage | Suspend/drop resources, inspect usage history after its latency window, and check account billing controls |

### 6.9 Cleanup

Run cleanup only after saving your observations. Execute each `DROP` only if this run created that uniquely named resource. If setup failed partway through, inspect what was created and drop only the objects you can confirm belong to this run. Never substitute an existing shared or production name.

```sql
DROP DATABASE IF EXISTS ARCH_LAB_DB;
DROP WAREHOUSE IF EXISTS ARCH_LAB_WH;
```

Dropping the database removes its contained lab objects, including the transient/permanent tables. Temporary objects disappear when their session ends. If you reused an existing database or warehouse rather than creating dedicated lab resources, do **not** drop it; remove only objects you created and are authorized to delete.

### 6.10 Lab acceptance criteria

- [ ] Created a database, at least two schemas, and permanent, transient, and temporary tables.
- [ ] Explained the table lifecycle and recovery trade-offs without treating transient storage as free.
- [ ] Inserted JSON into `VARIANT`, extracted nested fields with `:`, and expanded an array with `LATERAL FLATTEN`.
- [ ] Created the modest `CACHE_TEST` table, repeated an identical deterministic aggregate, and captured actual Query Profile evidence for result-cache behavior (or recorded why the run was inconclusive).
- [ ] Investigated local disk cache with result-cache reuse disabled and warehouse suspend/resume; recorded limitations and alternative explanations.
- [ ] Investigated metadata/pruning evidence without claiming a cache hit that cannot be directly observed.
- [ ] Wrote a one-page architecture comparison with one other platform.
- [ ] Suspended or dropped lab compute and cleaned up only lab-owned objects.

## 7. Production engineering practices

1. **Treat object names and grants as architecture.** Use fully qualified names in automation when context could be ambiguous. Prefer role-based least privilege and avoid broad administrative roles for daily engineering.
2. **Separate workloads.** Dedicated warehouses for ELT, BI, and ad hoc work can reduce interference and make attribution clearer. Right-sizing and multi-cluster decisions belong to the next lesson.
3. **Control idle compute.** Configure auto-suspend/resume intentionally and verify that scheduled jobs do not keep a warehouse alive unexpectedly.
4. **Benchmark honestly.** Record query IDs, warehouse size, cache settings, data volume, concurrency, bytes scanned, partitions scanned, spill, queue time, and credits where available. Run multiple comparable trials.
5. **Choose table lifecycle deliberately.** Use permanent tables for durable business data; temporary/transient only when lifecycle and recovery trade-offs are understood. External/Iceberg data needs ownership/catalog clarity.
6. **Make environment promotion repeatable.** Keep DDL and SQL in version control; avoid manual-only production changes; ensure test data is masked or synthetic.
7. **Design for observability.** Use Query History/Profile and appropriate account-usage views. Account Usage data may be delayed, and visibility depends on role/edition/configuration.
8. **Review data locality and residency.** Select account regions with source systems, users, legal requirements, and cross-region transfer implications in mind.
9. **Avoid premature materialization.** Views provide logical reuse; materialized views introduce maintenance/storage cost. Measure the workload first.
10. **Verify feature support before design commitment.** Editions, regions, cloud providers, catalog integrations, and new AI/application features can have different availability and behavior.

## 8. Common mistakes and misconceptions

- **“Snowflake has no indexes, so it has no physical organization.”** Snowflake manages columnar storage and micro-partitions and uses metadata/pruning; you generally do not create traditional indexes. Micro-partition design is covered later.
- **“Storage and compute are separated, so queries cannot interfere.”** Warehouses can be isolated, but shared services, data layout, concurrency, and account-level limits still matter.
- **“Every query costs warehouse credits.”** Eligible result-cache reuse can avoid a full warehouse execution; other services and billing rules still need to be considered.
- **“A fast second query proves local disk caching.”** It may be the persisted result cache or other effects. Disable result-cache reuse and inspect profile evidence before making claims.
- **“Metadata cache is the same as result cache.”** Result cache reuses a query result; metadata supports planning/pruning and some metadata-oriented operations; local disk cache holds data in a running warehouse.
- **“Transient tables are free.”** They still use storage and can incur compute costs; they simply have different recovery protections, including no Fail-safe.
- **“External table and Iceberg are the same.”** External tables expose external files; Iceberg is an open table format with its own metadata/snapshot model and Snowflake integration modes.
- **“Secure view automatically solves all security.”** Grants, row/column policy, data exposure, and consumer behavior still require testing.
- **“A database per environment is always equivalent to separate accounts.”** Separate accounts provide a stronger administrative/security boundary.
- **“Cloud services are always free because of the 10% rule.”** The rule is a daily adjustment framework, with eligibility/exclusions and account-specific usage; verify the current billing documentation.
- **“Spark is just another cloud warehouse.”** Spark is a distributed processing engine; its deployment, storage, catalog, governance, and orchestration are supplied by the surrounding platform.
- **“CREATE IF NOT EXISTS updates the object.”** It does not reconcile an existing definition. Inspect or migrate schema changes deliberately.

## 9. Practice questions with answers

### Q1. What are Snowflake's three main architectural layers?
**Answer:** Database storage, virtual-warehouse compute, and cloud services. Storage persists data, warehouses execute data-processing work, and cloud services handle coordination, metadata, security, transaction-related work, and query planning. They interact, and their consumption/billing models differ.

### Q2. Why can two warehouses query the same native table?
**Answer:** Persistent data is managed in a shared storage layer accessible to independently managed warehouses. This allows workload isolation and independent compute sizing without creating a separate full data copy for every warehouse.

### Q3. When would you use a transient table instead of a permanent table?
**Answer:** For intermediate data that must persist beyond one session but can be rebuilt and does not require permanent-table Fail-safe protection. Transient data still consumes storage and is not appropriate as the only copy of irreplaceable data.

### Q4. How do a view and a materialized view differ?
**Answer:** A standard view primarily stores a query definition and evaluates it when queried; a materialized view stores maintained results for supported query patterns, trading maintenance/storage cost for potential query savings.

### Q5. What is the role of `VARIANT` and `FLATTEN`?
**Answer:** `VARIANT` stores semi-structured values such as JSON. Path notation accesses nested values; `FLATTEN` converts array/object elements into rows, which can multiply parent rows and affect aggregates.

### Q6. You repeat a query and it runs much faster. What can you conclude?
**Answer:** Only that the observed run was faster. Check Query History/Profile and cache eligibility. It could be persisted result reuse, local data cache, pruning, compilation effects, or noise. Runtime alone does not prove a particular cache was used.

### Q7. How would you investigate warehouse-local cache?
**Answer:** Use a scan-heavy query, disable persisted result reuse for the session, run controlled repeats on a running warehouse, then suspend/resume and repeat. Compare profile/scan evidence and timing, while documenting noise and limitations.

### Q8. Does Snowflake's cloud-services 10% adjustment mean cloud services are always free?
**Answer:** No. It is a documented daily billing adjustment framework for eligible cloud-services usage relative to eligible warehouse compute, with exclusions and calculation details. Check current billing docs and account usage.

### Q9. When are separate accounts preferable to separate databases for dev/test/prod?
**Answer:** When stronger security/administrative isolation, regulatory boundaries, separate policies, or blast-radius reduction are important enough to justify deployment and governance overhead.

### Q10. Is Apache Spark a direct architectural equivalent to Snowflake?
**Answer:** No. Spark is a distributed processing engine. A Spark-based platform still needs storage, catalog, security, orchestration, and capacity management; Databricks SQL is a closer SQL analytics comparison but also has a different lakehouse model.

### Q11. What is the architectural motivation for Iceberg?
**Answer:** It provides an open table format and snapshot/metadata model that can support interoperability across engines. Trade-offs include catalog and metadata coordination, feature compatibility, and explicit operational ownership.

### Q12. Name three facts you should capture for a credible performance comparison.
**Answer:** At least the query/profile ID and plan evidence, data size/shape and cache settings, and warehouse/compute configuration. For cost comparisons also record credits/bytes scanned and include ingestion/storage/transfer costs where relevant.

## 10. Final checkpoint mapped to the roadmap

Use this checklist from Topic 01 in `roadmap-Snowflake-Deep-Dive.md` as the completion gate.

| Roadmap checkpoint | Evidence that you have learned it | Status |
|---|---|---|
| Explain the three layers and what each costs | Explain storage vs warehouse compute vs cloud services; distinguish warehouse credits, storage, and cloud-services billing adjustment | [ ] |
| Choose a table type | Given session scratch data, rebuildable staging data, durable business data, external files, and open-format interoperability, justify the table type and recovery trade-off | [ ] |
| Query semi-structured data | Run `VARIANT` path extraction and `LATERAL FLATTEN` and explain row multiplication/casting | [ ] |
| Explain the three caches | Define result cache, warehouse local disk cache, and metadata cache; describe valid evidence and what cannot be conclusively proven from timing alone | [ ] |

**Ready to continue to Topic 02 (Virtual warehouses: sizing and scaling) when:** you can explain the architecture without notes, complete the lab safely, and defend cache observations using Query History/Profile rather than assumptions.

## 11. References and version-sensitive documentation

Use official documentation as the source of truth for current syntax, edition/region availability, product naming, and billing rules. Documentation is updated frequently; check the page at the time you implement a design.

1. Snowflake, **Key concepts and architecture**: https://docs.snowflake.com/en/user-guide/intro-key-concepts
2. Snowflake, **Databases, tables, and views overview**: https://docs.snowflake.com/en/guides-overview-db
3. Snowflake, **Temporary and transient tables**: https://docs.snowflake.com/en/user-guide/tables-temp-transient
4. Snowflake, **CREATE TABLE reference**: https://docs.snowflake.com/en/sql-reference/sql/create-table
5. Snowflake, **Semi-structured data concepts**: https://docs.snowflake.com/en/user-guide/semistructured-concepts
6. Snowflake, **FLATTEN table function**: https://docs.snowflake.com/en/sql-reference/functions/flatten
7. Snowflake, **Persisted query results**: https://docs.snowflake.com/en/user-guide/querying-persisted-results
8. Snowflake, **Optimizing the warehouse cache**: https://docs.snowflake.com/en/user-guide/performance-query-warehouse-cache
9. Snowflake, **Understanding compute cost**: https://docs.snowflake.com/en/user-guide/cost-understanding-compute
10. Snowflake, **Exploring compute cost**: https://docs.snowflake.com/en/user-guide/cost-exploring-compute
11. Snowflake, **Metering daily history view**: https://docs.snowflake.com/en/sql-reference/account-usage/metering_daily_history
12. Snowflake, **Iceberg tables overview**: https://docs.snowflake.com/en/user-guide/tables-iceberg
13. Snowflake, **Open Catalog / Iceberg integration notes**: https://docs.snowflake.com/en/user-guide/tables-iceberg-open-catalog
14. Snowflake, **Horizon Catalog overview**: https://docs.snowflake.com/en/user-guide/snowflake-horizon
15. Snowflake, **Snowflake CLI documentation**: https://docs.snowflake.com/en/developer-guide/snowflake-cli/index
16. Snowflake, **Python Connector documentation**: https://docs.snowflake.com/en/developer-guide/python-connector/python-connector
17. Snowflake, **Streamlit in Snowflake**: https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit
18. Snowflake, **Cortex AI functions**: https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions
19. Snowflake, **Native Apps overview**: https://docs.snowflake.com/en/developer-guide/native-apps/native-apps-about
20. AWS, **Amazon Redshift data warehouse system architecture**: https://docs.aws.amazon.com/redshift/latest/dg/c_high_level_system_architecture.html
21. Google Cloud, **BigQuery architecture introduction**: https://cloud.google.com/bigquery/docs/introduction
22. Databricks, **Lakehouse architecture**: https://docs.databricks.com/en/lakehouse/index.html
23. Apache Spark, **Cluster mode overview**: https://spark.apache.org/docs/latest/cluster-overview.html
24. Apache Iceberg, **Documentation**: https://iceberg.apache.org/docs/latest/
25. Snowflake, **QUERY_HISTORY table function**: https://docs.snowflake.com/en/sql-reference/functions/query_history
26. Snowflake, **QUERY_HISTORY Account Usage view**: https://docs.snowflake.com/en/sql-reference/account-usage/query_history

---

**Lesson boundary:** warehouses and sizing, micro-partitions/clustering, ingestion/stages, streams/tasks, Snowpark programming, recovery, detailed governance, sharing, and full cost monitoring are separate lessons in this module. This file introduces only the concepts necessary to understand the architecture and complete Topic 01's checkpoint.
