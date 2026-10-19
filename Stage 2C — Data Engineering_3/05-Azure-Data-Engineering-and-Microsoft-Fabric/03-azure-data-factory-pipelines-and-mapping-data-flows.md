# Azure Data Factory Pipelines and Mapping Data Flows

> **Stage:** 2C — Data Engineering_3  
> **Module:** 05 — Azure Data Engineering and Microsoft Fabric  
> **Level:** Beginner → Advanced  
> **Primary purpose:** Build maintainable, parameterised ingestion and orchestration pipelines in Azure Data Factory (ADF), understand when to use Mapping Data Flows, and operate the result safely in production.

## 1. Purpose, prerequisites, and learning outcomes

Azure Data Factory is a managed data-integration and orchestration service. It coordinates movement of data between systems, executes transformations, and manages dependencies, retries, schedules, and monitoring. It is not a universal replacement for SQL engines, Spark, dbt, or workflow orchestrators.

This lesson follows Topic 03 of `roadmap-Azure-Data-Engineering-and-Microsoft-Fabric.md`. It focuses on ADF pipelines and Mapping Data Flows; it does not attempt to teach every Azure data service.

### Prerequisites

You should be comfortable with:

- SQL `SELECT`, filtering, joins, aggregation, stored procedures, and basic transaction concepts.
- ETL/ELT, orchestration, batch processing, and retries.
- ADLS Gen2 containers and folders, Parquet, and bronze/silver/gold data zones (Topic 02).
- Cloud identity, managed identities, secrets, and least-privilege access.
- Basic Git and environment configuration.

### Learning outcomes

After completing the lesson and lab, you should be able to:

1. Explain linked services, datasets, activities, pipelines, triggers, and integration runtimes and how they relate.
2. Build Copy activity pipelines and reason about connector support, parallelism, DIUs, and bottlenecks.
3. Choose between schedule, tumbling-window, storage-event, and custom-event triggers.
4. Use control-flow activities, parameters, variables, and dynamic content safely.
5. Design one metadata-driven pipeline to ingest many source tables without creating one pipeline per table.
6. Implement watermark-based incremental ingestion with safe watermark advancement and recovery.
7. Build a Mapping Data Flow that deduplicates and aggregates data, including handling schema drift deliberately.
8. Monitor, alert, version, test, and promote a factory between environments.
9. Explain when ADF should orchestrate another compute engine rather than perform complex transformations itself.

## 2. Mental model: what happens during a pipeline run?

Think of ADF as a **control plane plus managed execution bridges**. A pipeline defines the workflow; activities perform work; linked services describe connections; datasets describe the data location/shape; integration runtimes provide connectivity and/or dispatch execution; triggers create pipeline runs.

```text
Trigger or manual/API invocation
              |
              v
        Pipeline run
              |
     +--------+---------+
     |        |         |
   Lookup   Copy      Data Flow
     |        |         |
  control   source ->  Spark-based
  metadata   ADLS      transformation
     |                  |
  ForEach / If / Execute Pipeline
              |
       logging + alerting
```

Typical lifecycle:

1. **Author** linked services, datasets, pipeline activities, data flows, triggers, and parameters in the ADF Studio authoring experience.
2. **Validate and publish** the factory artifacts. In Git mode, publishing generates deployment artifacts for the factory.
3. **Trigger** a pipeline manually, on a schedule, from an event, or through an API/another pipeline.
4. **Resolve configuration**: pipeline parameters, activity expressions, dataset parameters, linked-service settings, and trigger metadata are evaluated.
5. **Execute**: activities run in dependency order; independent activities may run in parallel. The appropriate Integration Runtime provides connectivity and/or dispatches the work to the target service.
6. **Observe**: activity output, duration, rows read/written where available, errors, and run status appear in monitoring. Diagnostics can also be sent to Azure Monitor/Log Analytics.
7. **Recover**: fix the underlying issue, then rerun the failed work with an explicit plan for duplicates, partial output, and checkpoint state.

A pipeline run is an execution instance, not the pipeline definition. Pipeline parameters are inputs to a run and are read-only during that run; variables are mutable pipeline-local state. A successful activity does not automatically mean the entire business load is correct: validate row counts, keys, freshness, and downstream invariants too.

## 3. Core ADF objects and relationships

### 3.1 Linked services

A linked service describes connection information for a data store or compute service. Examples include Azure SQL Database, ADLS Gen2, REST, Key Vault, Azure Databricks, and an Azure-SSIS IR configuration.

- Prefer **managed identity** where supported; grant the identity only the required data-plane permissions.
- Use Key Vault-backed secrets when a connector requires a secret. Do not put passwords, account keys, tokens, or connection secrets in pipeline expressions or source control.
- A linked service can be parameterised in supported scenarios, which helps reuse a connection definition across environments or endpoints. Validate connector-specific parameter support before designing around it.

### 3.2 Datasets

A dataset identifies the data to read or write: a table, file, folder, or other connector-specific object. It commonly references a linked service and defines format or location details. Dataset parameters allow reusable paths, table names, and file names.

Example: an ADLS Parquet dataset may parameterise `container`, `folderPath`, and `fileName`; a SQL dataset may parameterise a table name. Parameterising a dataset does not make arbitrary SQL identifiers safe—validate table identifiers against a controlled allow-list.

### 3.3 Activities

Activities are the steps in a pipeline. Common categories:

- **Data movement:** Copy activity.
- **Transformation:** Mapping Data Flow and activities that dispatch work to another service.
- **Control:** Lookup, Get Metadata, ForEach, If Condition, Switch, Until, Execute Pipeline, Web, Wait, Set Variable, and related activities.
- **Database operations:** Stored Procedure or Script activity where supported by the connector.

Activity dependencies specify whether the next activity runs after **Succeeded**, **Failed**, **Skipped**, or **Completed**. Use these paths deliberately; a failure branch should not accidentally cause a pipeline to report success when a required load failed.

### 3.4 Pipelines, parameters, and variables

A pipeline is a logical workflow. Keep it reusable and composable: a parent pipeline can read metadata and call a child ingestion pipeline once per table. Parameters configure a run; variables hold temporary state. Avoid relying on a variable as a shared accumulator inside a parallel `ForEach`: parallel iterations can race. If state must be accumulated, use a serial loop or, preferably, write per-item results to a durable logging table.

### 3.5 Triggers

Triggers create pipeline runs. They are not the same thing as activities and should be versioned and deployed as part of the release process where applicable. Stop or disable triggers during risky deployment operations if the release procedure requires it; restart them only after successful deployment and validation.

### 3.6 Integration Runtime (IR)

An IR provides the connectivity and execution bridge for supported activities. It is not a universal compute cluster used by every activity.

| IR type | Typical use | Operational notes |
|---|---|---|
| **Azure IR** | Cloud-to-cloud movement and dispatch to supported managed services | Managed by Azure; region, network path, connector support, and data residency still matter. |
| **Self-hosted IR (SHIR)** | Private/on-premises data sources, network-isolated servers, or connectors requiring a machine inside that network | Install on managed Windows hosts; patch, monitor, secure, and scale the nodes. Provide outbound connectivity to required Azure endpoints. Avoid single-node critical-path designs. |
| **Azure-SSIS IR** | Lift-and-shift or execute existing SQL Server Integration Services (SSIS) packages | A managed cluster for SSIS package execution; it is not the same as a SHIR and may incur compute cost while running. Validate package compatibility and runtime sizing. |

The selected IR depends on the activity and connector. Do not assume every source/sink combination supports every IR or network mode; consult the connector's current support matrix.

## 4. Trigger types and execution-window semantics

| Trigger | Use when | Semantics and cautions |
|---|---|---|
| **Schedule** | Run daily, hourly, or at a defined calendar cadence | Starts runs at configured times. It does not inherently guarantee exactly-once processing or represent a durable business window. Make the pipeline idempotent. |
| **Tumbling window** | Process discrete, contiguous time windows such as each 15-minute interval | Has a defined window start/end and supports dependencies, retries, and backfill patterns. Design the pipeline to process the specific window, not “whatever is newest.” Overlapping windows and concurrency need explicit planning. |
| **Storage event** | React to supported storage events, commonly new or deleted blobs | Event-driven ingestion reduces polling. Account for event delivery behavior, duplicate notifications, file-completion conventions, and whether a blob represents a complete logical batch. |
| **Custom event** | Start from supported Event Grid custom events | Useful when an upstream system emits a business event. Define an event schema and idempotency key; the trigger is a signal, not a transaction with the source system. |

### Tumbling-window boundaries

A tumbling-window run exposes window metadata such as `windowStartTime` and `windowEndTime` in trigger context; the roadmap shorthand refers to `windowStart`/`windowEnd`. In ADF expressions, the exact property names and activity context must match the trigger configuration and current product documentation. A typical expression pattern is:

```text
@trigger().outputs.windowStartTime
@trigger().outputs.windowEndTime
```

Use the values as **half-open intervals**: `event_time >= window_start AND event_time < window_end`. Half-open windows avoid double-counting the boundary record in adjacent windows. Confirm the exact trigger output shape in your factory's trigger run output before using it in production.

For late-arriving data, choose a policy: allow a lookback period, rerun affected windows, consume source change tracking/CDC, or reconcile periodically. A time trigger alone does not solve late updates.

## 5. Copy activity: configuration and performance

Copy activity is usually the first choice for moving data between supported connectors with little transformation.

### 5.1 Configure source and sink

For each Copy activity, specify:

1. **Source linked service and dataset**: endpoint, authentication, table/query/path, and source options.
2. **Source extraction**: full table, query, partitioned read where supported, watermark predicate, or source-native incremental capability.
3. **Sink linked service and dataset**: target storage/table, output format (for this lab, Parquet), path and write behavior.
4. **Mapping and type conversion**: explicit column mappings for stable contracts; validate decimal precision, timestamps/time zones, nullability, and source-specific types.
5. **Fault tolerance**: decide whether bad rows should fail the activity or be logged/skipped. Silent row skipping is inappropriate for strict financial or regulatory loads.
6. **Integration Runtime**: select the compatible IR and network route.

For Parquet in ADLS, define a predictable partition/path convention, for example `bronze/<source>/<table>/load_date=YYYY-MM-DD/`. Avoid one tiny file per row or per very small batch. File count affects downstream listing, planning, and query performance.

### 5.2 Parallelism and DIUs

**Data Integration Units (DIUs)** are a Copy activity performance concept for applicable Azure IR scenarios; they are not a general compute unit for every IR or every connector. Auto or a manual DIU setting may be available depending on connector and copy pattern. SHIR throughput is more directly constrained by its node CPU, memory, network, disk, and source/sink capacity.

Copy performance is bounded by the slowest component:

- Source query and source connection limits.
- Network bandwidth/latency and IR region/path.
- Copy parallelism, partitioning, and connector implementation.
- Sink write throughput, transaction limits, and file layout.
- Serialization/type conversion and compression.

Tune in this order:

1. Establish a baseline using representative data and record bytes, rows, duration, source/sink metrics, and cost.
2. Check whether source or sink is the bottleneck before increasing parallelism.
3. Use source partitioning only when the source can sustain concurrent queries and the partition key distributes work evenly.
4. Increase concurrency gradually; excessive parallelism can throttle databases, create too many files, or increase transaction costs.
5. Re-measure end-to-end latency and cost. Faster is not automatically cheaper or safer.

A pipeline with dozens of activities may spend more on orchestration and setup than on moving a tiny amount of data. Batch small entities into a metadata-driven loop or consolidate work when it is operationally safe.

## 6. Control flow, parameters, variables, and expressions

ADF expressions are not ordinary SQL, Python, or shell expressions. Use the expression builder and validate against the current ADF expression language.

### 6.1 Frequently used activities

- **Lookup:** Read a small control/result set. Configure first-row-only when you expect one row; otherwise consume the `value` array. Respect the activity's result-size limits; it is not a bulk extraction mechanism. Explicitly handle zero rows: an empty array makes `ForEach` execute zero iterations, which can look like success even when the configuration table unexpectedly returned nothing. Log an intentional no-op when empty is valid, or fail the pipeline when at least one enabled row is required.
- **Get Metadata:** Inspect supported properties such as child items or last modified information. It does not recursively enumerate arbitrary data lakes unless you build that logic.
- **ForEach:** Iterate over an array such as `@activity('LookupEnabledTables').output.value`. Set batch count/concurrency conservatively and make each item independent.
- **If Condition:** Branch on a boolean expression, such as whether a watermark query returned a usable range.
- **Switch:** Route based on a finite, controlled value, such as `source_type` (`azure_sql`, `rest`). Do not use it as a substitute for validating metadata.
- **Until:** Repeat until a condition becomes true. Always define timeout and a terminating condition; a faulty loop can burn time and cost.
- **Execute Pipeline:** Invoke a reusable child pipeline and pass parameters explicitly. Use wait-on-completion when the parent depends on the child result.
- **Web:** Call an HTTP endpoint for supported APIs, with authentication and response handling configured. Never put bearer tokens in literal expressions or logs.

### 6.2 Parameters vs variables

Example child pipeline parameters:

```text
p_source_schema   String
p_source_table    String
p_watermark_col   String
p_target_folder   String
p_low_watermark   String
p_high_watermark  String
p_load_id         String
```

Expressions commonly used in pipelines include:

```text
@pipeline().parameters.p_source_table
@pipeline().parameters.p_target_folder
@activity('LookupEnabledTables').output.value
@item().source_table
@pipeline().RunId
@utcNow()
@concat('bronze/', item().source_schema, '/', item().source_table, '/')
```

Expressions above are illustrative. Check activity output paths in the actual run output; Lookup output differs for first-row-only versus array mode. `@item()` is valid in the scope of a ForEach iteration.

### 6.3 Safe dynamic content

Dynamic content should parameterise values and approved identifiers, not allow arbitrary caller input to become executable SQL. Prefer source query parameters or stored procedures when supported. If an identifier such as schema/table/column cannot be bound as a SQL value parameter, validate it against an allow-list maintained by an administrator and quote it using the database's identifier rules. Do not concatenate user-controlled predicates or table names into SQL.

For REST endpoints, allow-list hostnames and path patterns; do not let metadata supply arbitrary URLs. This prevents accidental data exfiltration and server-side request abuse.

### 6.4 Example parent pipeline

Conceptual activity graph:

```text
LookupEnabledTables (firstRowOnly = false)
  --Succeeded--> ForEachTable (items = @activity('LookupEnabledTables').output.value)
                    --each item--> Execute Pipeline: PL_LoadOneTable
```

The parent passes `source_schema`, `source_table`, `watermark_column`, `target_folder`, and the metadata row's key to the child. Keep per-table details in the control table; keep shared orchestration logic in the child pipeline. Avoid one separately maintained pipeline for every table.

## 7. Metadata-driven ingestion for 20 tables

A metadata-driven design stores the configuration that differs by source table in a control table, then runs a shared pipeline over the enabled rows.

### 7.1 Example control table

The following SQL Server/Azure SQL schema is illustrative. Adapt types and naming conventions to your database and permissions model.

```sql
CREATE TABLE etl.TableConfig (
    table_config_id       int IDENTITY(1,1) PRIMARY KEY,
    source_schema         sysname       NOT NULL,
    source_table          sysname       NOT NULL,
    watermark_column      sysname       NULL,
    initial_watermark     datetime2(7)  NULL,
    target_container      varchar(63)   NOT NULL,
    target_folder          varchar(512)  NOT NULL,
    load_strategy          varchar(20)   NOT NULL, -- FULL or WATERMARK
    source_type            varchar(20)   NOT NULL, -- e.g. AZURE_SQL
    is_enabled             bit           NOT NULL DEFAULT 1,
    max_parallel_runs      int           NOT NULL DEFAULT 1,
    last_success_watermark datetime2(7)  NULL,
    last_run_id            varchar(64)   NULL,
    last_status            varchar(20)   NULL,
    updated_at_utc         datetime2(7)  NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_TableConfig UNIQUE (source_schema, source_table),
    CONSTRAINT CK_TableConfig_LoadStrategy CHECK (load_strategy IN ('FULL','WATERMARK')),
    CONSTRAINT CK_TableConfig_SourceType CHECK (source_type IN ('AZURE_SQL')),
    CONSTRAINT CK_TableConfig_Parallel CHECK (max_parallel_runs BETWEEN 1 AND 20)
);

CREATE TABLE etl.TableWatermark (
    table_config_id int PRIMARY KEY
        REFERENCES etl.TableConfig(table_config_id),
    watermark_value datetime2(7) NOT NULL,
    updated_at_utc datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE etl.PipelineRunLog (
    log_id           bigint IDENTITY(1,1) PRIMARY KEY,
    pipeline_run_id  varchar(64) NOT NULL,
    table_config_id  int NULL,
    source_schema    sysname NULL,
    source_table     sysname NULL,
    low_watermark    datetime2(7) NULL,
    high_watermark   datetime2(7) NULL,
    status           varchar(20) NOT NULL,
    rows_copied      bigint NULL,
    started_at_utc   datetime2(7) NOT NULL DEFAULT SYSUTCDATETIME(),
    finished_at_utc  datetime2(7) NULL,
    error_code       varchar(100) NULL,
    error_message    nvarchar(2000) NULL
);
```

Use separate permissions for configuration and runtime state. Pipeline identities should generally read enabled configuration and execute approved procedures, not have unrestricted DDL or broad update rights. `max_parallel_runs` is descriptive metadata in this starter schema; ADF does not automatically enforce that per-table value. If you use it, implement explicit validation/scheduling plus a per-table lease or lock, and reject overlapping runs. The schema is a teaching baseline, not a complete operational control plane; add locking/lease fields and audit columns if concurrent runs are allowed.

### 7.2 Parent pipeline design

1. Lookup enabled rows from `etl.TableConfig`, ordered by `table_config_id`. Check the returned `count` before looping: distinguish an expected empty/no-op run from a missing or misconfigured control table, and log or fail accordingly.
2. ForEach the returned array. Start with sequential execution or a small batch count, then increase only after validating source/sink capacity.
3. Execute `PL_LoadOneTable`, passing the current row's configuration values.
4. In the child, validate that the configuration exists, is enabled, and uses an approved `source_type` and `load_strategy`.
5. Read the current low watermark from durable state; capture a bounded high watermark from the source; copy the half-open interval; validate/write output; then advance the watermark only after successful completion.
6. Log both success and failure. A failed child must remain a failed child; the parent should make failed table IDs visible and should not claim overall success if any required table failed.

### 7.3 Illustrative ADF expression fragments

Lookup (multiple rows):

```text
Items for ForEach:
@activity('LookupEnabledTables').output.value
```

Inside `ForEach`:

```text
@item().table_config_id
@item().source_schema
@item().source_table
@item().watermark_column
@item().target_folder
```

Pass to Execute Pipeline parameters using the activity's parameter mapping UI. Do not paste the child parameter name where the parent expression belongs; these are separate namespaces.

### 7.4 Concurrency policy

- Start with `ForEach` sequential (`isSequential = true`) while proving correctness.
- `max_parallel_runs` in the example control table does not configure ADF concurrency by itself. If you implement parallel processing, explicitly enforce that metadata policy, set a modest `batchCount`, cap overlapping trigger runs, and enforce per-table mutual exclusion or leases if the same table can be processed by concurrent runs.
- Never share a mutable pipeline variable across concurrent iterations as a run log or counter.
- A concurrency limit is not a substitute for idempotent writes or database locking.

## 8. Watermark-based incremental loading

A watermark is a durable boundary used to identify data to process. Common choices include a `LastModifiedUtc` timestamp or monotonically increasing key. The watermark must reflect **all changes the extraction strategy promises to capture**, not just new inserts.

### 8.1 The safe pattern

For each table/run:

1. Acquire a per-table lease or ensure only one active run can process that table.
2. Read the committed low watermark `L`.
3. Capture a stable high watermark `H` from the source (for example, `MAX(LastModifiedUtc)` at the start of the load). For stronger consistency, use a source snapshot or CDC/change tracking position supported by the source.
4. Extract rows where `watermark_column > L AND watermark_column <= H` (or consistently use `>= L AND < H`; choose one convention and avoid mixing them). The roadmap's tutorial pattern commonly uses a low-exclusive/high-inclusive interval.
5. Write to a run-specific staging path, such as `bronze/<table>/load_id=<pipelineRunId>/`, or write into a sink with an idempotent merge/upsert key.
6. Validate row counts, schema, required fields, and any source-specific reconciliation checks.
7. Publish the staged output atomically where the sink supports it, or write a completion manifest/commit marker only after all files are complete.
8. Advance the durable watermark to `H` **only after** output is committed and validation passes.
9. Mark the run successful and release the lease.

If the process fails before step 8, rerunning the same interval may copy rows again. That is acceptable only if the sink strategy is idempotent: overwrite the run-specific staging output, deduplicate/merge by stable keys, or publish a single committed manifest. If the watermark advances before the output is safely committed, a failure can cause permanent data loss.

### 8.2 Stored procedure for compare-and-set watermark advancement

A simple unconditional `UPDATE` can be unsafe when two runs overlap. The following is a teaching example that requires the expected old value and refuses to advance if another run changed it. Add lease acquisition and transaction coordination for production.

```sql
CREATE OR ALTER PROCEDURE etl.usp_AdvanceWatermark
    @TableConfigId int,
    @ExpectedLow    datetime2(7),
    @NewHigh        datetime2(7),
    @PipelineRunId  varchar(64)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @NewHigh < @ExpectedLow
        THROW 50001, 'New watermark is earlier than the expected low watermark.', 1;

    BEGIN TRANSACTION;

    UPDATE etl.TableWatermark WITH (UPDLOCK, HOLDLOCK)
       SET watermark_value = @NewHigh,
           updated_at_utc = SYSUTCDATETIME()
     WHERE table_config_id = @TableConfigId
       AND watermark_value = @ExpectedLow;

    IF @@ROWCOUNT <> 1
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 50002, 'Watermark changed concurrently; do not commit this run.', 1;
    END;

    UPDATE etl.TableConfig
       SET last_success_watermark = @NewHigh,
           last_run_id = @PipelineRunId,
           last_status = 'SUCCEEDED',
           updated_at_utc = SYSUTCDATETIME()
     WHERE table_config_id = @TableConfigId;

    COMMIT TRANSACTION;
END;
```

This procedure updates metadata state, not the data sink itself. Call it only after the output is validated and committed. It assumes `etl.TableWatermark` has been seeded for the config row. It does not alone provide exactly-once delivery or solve a crash between output commit and watermark commit; the run-specific output/manifest or idempotent merge strategy is still required.

### 8.3 Late updates and deletes

A timestamp watermark can miss changes if source timestamps are not reliably maintained, if timestamps arrive late behind the committed boundary, or if rows are hard-deleted without a tombstone. Options include:

- A bounded lookback window and sink-side deduplication/upsert.
- SQL Server Change Tracking or CDC, with the correct source-specific retention and checkpoint semantics.
- Source-native change feeds or transaction logs.
- Periodic full reconciliation for high-value entities.

Change Tracking generally identifies changed keys and requires querying current rows; CDC can expose change records and operation metadata. They are different mechanisms and must be designed around the source's version/retention guarantees. Do not treat a generic watermark timestamp as equivalent to CDC.

### 8.4 Tumbling-window and watermark relationship

A tumbling-window trigger determines the **time interval being orchestrated**. A data watermark determines the **source changes already committed**. They can be used together but are not interchangeable. If event-time windows are used, extract with `event_time >= windowStart AND event_time < windowEnd`; track late arrivals and replay/backfill windows as needed. If using a change timestamp, maintain a separate source watermark/checkpoint and do not advance it merely because a trigger window completed.

## 9. Mapping Data Flows

Mapping Data Flows are visual, Spark-based transformations executed on managed compute. They can be useful when teams want visual transformation graphs and managed scale without authoring Spark code. They also incur cluster startup/compute costs, so they are not automatically the best choice for tiny loads or complex engineering logic.

### 9.1 Main transformations

- **Source:** Reads a dataset or inline source; projection and schema options determine available columns.
- **Derived Column:** Creates or modifies columns with expressions, e.g. normalized names or derived business flags.
- **Filter:** Retains rows matching a condition.
- **Select:** Renames, drops, or reorders columns.
- **Join:** Combines streams using join keys and join type. Check null behavior and key cardinality.
- **Aggregate:** Groups by key(s) and calculates counts, sums, minimums, maximums, or other supported aggregates.
- **Window:** Computes values over a partition/order, such as ranking records by update time.
- **Sink:** Writes to a target dataset, with settings for mapping, output behavior, and error handling.

Example design for a customer feed:

```text
Source customer_delta
   -> Derived Column (normalized_email, ingest_ts)
   -> Window (partition by customer_id; order by modified_utc desc, source_sequence desc)
   -> Filter (row_number == 1)
   -> Aggregate (group by region; count distinct customer_id, sum approved measures)
   -> Sink silver/customer_current and/or gold/customer_region_summary
```

For a production current-state table, ensure the deduplication ordering is deterministic. A timestamp alone may tie; use a source sequence/version or stable tie-breaker. The exact function names and expression syntax must be selected from the Mapping Data Flow expression builder; do not assume SQL window syntax can be pasted unchanged.

### 9.2 Schema drift

Schema drift means source fields can be added, removed, or typed differently over time. Mapping Data Flows can allow drifted columns, but accepting drift is not the same as governing it.

- Enable drift only where the source contract is intentionally flexible.
- Use rule-based mapping or column patterns only when the downstream contract can tolerate changing columns.
- Explicitly cast important business fields and validate required columns.
- Monitor unexpected additions, removals, and type changes; route invalid records or fail the run according to data criticality.
- For curated silver/gold outputs, prefer an explicit schema contract. Do not let a new upstream field silently change a published table.

### 9.3 Debug clusters and TTL

Data Flow debug enables interactive authoring and uses compute that can remain available for a configured TTL. Stop debug sessions when finished and configure the shortest practical TTL for the learning environment. Debug sessions and production execution have different lifecycle/cost behavior; inspect current pricing and activity details for your region. For production, tune compute size and partitioning using representative data rather than assuming the default is optimal.

## 10. Error handling, logging, monitoring, and alerting

### 10.1 Retry and timeout policy

Retries are appropriate for transient failures (brief network faults, throttling, temporary service unavailability). They are not a fix for invalid credentials, malformed schema, rejected business rules, or an incorrect query.

- Configure retry count and retry interval based on source behavior and service throttling guidance.
- Set realistic activity timeouts. A too-short timeout causes needless retries; a too-long timeout delays incident detection.
- Ensure repeated execution is safe. Copying into append-only paths with random names can create duplicates on retry.
- Separate transient technical failures from data-quality failures. Route data-quality failures to a quarantine or failed-batch process where appropriate.

### 10.2 Success and failure paths

Use explicit dependency conditions. A typical child pipeline should:

1. Write a `STARTED` record with run ID and table ID.
2. Capture watermarks and start Copy.
3. Validate output and record counts.
4. Commit/publish output, then advance the watermark.
5. Write `SUCCEEDED` and completion timestamp.
6. On failure, write `FAILED`, store a sanitised error code/message, and rethrow/fail the pipeline so monitoring can alert.

Failure logging itself can fail if the database is unavailable. Consider a secondary diagnostic channel such as ADF diagnostics to Log Analytics. Never log secrets, full connection strings, or unredacted sensitive payloads.

### 10.3 What to monitor

Track at minimum:

- Pipeline and activity success/failure, duration, retry count, and run ID.
- Rows/bytes read and written where exposed, plus source/sink throughput.
- Watermark before/after, source high watermark, and last successful completion time.
- Freshness SLA, missing expected files, zero-row anomalies, duplicate-key rate, schema changes, and reconciliation deltas.
- Per-table failures, overlapping runs, and growing backlog.

Use ADF Monitor for interactive triage. Configure diagnostic settings to send relevant pipeline/activity logs and metrics to Log Analytics/Azure Monitor when durable central monitoring is required. Create Azure Monitor alert rules/action groups or a supported webhook/Logic App route for failures. Validate alert routing with a controlled failure in a non-production environment.

## 11. Git, environment promotion, CI/CD, and global parameters

### 11.1 Development workflow

1. Connect the development factory to the supported Git repository/provider.
2. Use feature branches and pull requests; review pipeline JSON and linked-service changes.
3. Validate and publish from the designated collaboration branch according to the team's workflow.
4. Generate the supported ARM deployment artifacts for ADF; deploy to test/staging/prod using a controlled pipeline.
5. Override environment-specific values through deployment parameters/global parameters, managed identity, and Key Vault references.
6. Run post-deployment smoke tests and data-quality checks before enabling production triggers.

The generated `adf_publish` branch and ARM artifacts are a common ADF deployment workflow. Bicep can provision the surrounding Azure infrastructure—factory, managed identity, networking, diagnostic settings, Key Vault, storage, and permissions—but do not assume hand-writing Bicep replaces the factory's supported publishing process for all ADF pipeline artifacts. Choose a documented deployment pattern and test it end to end.

### 11.2 Environment separation

Keep dev/test/prod endpoints and identities separate. Promote the same logical pipeline definition while parameterising environment-specific values such as storage account, SQL server/database, Key Vault, and monitoring workspace. Never promote development secrets. Use least-privilege deployment identities and runtime identities; these are different responsibilities.

Global parameters are referenced in expressions using a pattern such as:

```text
@pipeline().globalParameters.environmentName
```

Use clear names and include global parameters in the chosen deployment process. Verify the generated ARM parameter files and current Microsoft guidance; global-parameter deployment mechanics have changed over time.

### 11.3 Release safeguards

- Keep source-controlled artifacts free of credentials.
- Avoid destructive deployment modes unless the release explicitly intends to remove resources.
- Stop triggers if required by the chosen deployment process, deploy, validate, then restart them.
- Test linked-service connectivity, permissions, Key Vault references, and IR availability in the target environment.
- Confirm no debug cluster, test trigger, or test destination remains enabled in production.
- Keep deployment logs and a rollback/recovery procedure.

## 12. Security, networking, cost, and operational trade-offs

### Identity and secrets

Use a factory's managed identity for Azure services that support it, and grant the minimum required data-plane roles/ACLs. Use Key Vault for secrets where unavoidable. Restrict who can author and publish pipelines: an author who can modify a pipeline may be able to redirect data or invoke privileged services. Treat pipeline authoring permissions as a production security boundary.

### Network paths

- **Azure IR:** managed cloud connectivity; private endpoints and managed virtual network features depend on service, connector, and configuration.
- **Managed virtual network:** can isolate supported Azure IR activities and use managed private endpoints for supported targets. Approve private endpoint connections where required and verify DNS, firewall, and region constraints.
- **Self-hosted IR:** provides a route into private/on-premises networks. Secure the host, restrict outbound access, patch it, and monitor availability. Avoid exposing source systems broadly just to make ADF connectivity work.
- **REST:** restrict allowed endpoints, configure authentication securely, and consider API rate limits and pagination.

### Cost levers

- Copy: bytes transferred, DIU/IR use where applicable, source/sink charges, transactions, and network/egress costs.
- Mapping Data Flow: Spark compute and startup overhead; debug cluster time/TTL.
- Orchestration: activity/run volume and many tiny activity executions.
- SHIR/Azure-SSIS IR: host or managed integration runtime capacity and uptime.
- Storage: file count, format/compression, retention, and downstream read amplification.

Cost optimisation is a measurement exercise. Record a baseline, tune one variable at a time, and compare cost per GB/table/run as well as duration and reliability. Do not reduce retries or validation merely to make a dashboard cheaper.

## 13. Choosing ADF, Spark, dbt, or Airflow

| Tool | Best fit | Less suitable when |
|---|---|---|
| **ADF** | Managed ingestion, connector-based movement, schedules/events, dependencies, parameters, monitoring, and dispatching work to Azure services | The core workload is highly algorithmic transformation code, complex software-style testing, or fine-grained orchestration requiring extensive custom logic. |
| **Mapping Data Flows** | Visual, managed Spark transformations; teams benefit from a visual graph and can accept managed Spark startup/cost characteristics | Tiny frequent transformations, complex custom libraries, advanced Spark tuning, or transformations best expressed and tested as code. |
| **Azure Databricks / Spark** | Large-scale distributed transformation, complex data engineering, ML feature preparation, reusable code, Delta Lake operations | Simple connector-to-connector copy where ADF Copy is sufficient and cheaper to operate. |
| **dbt** | SQL-centric transformations, model dependencies, tests, documentation, and analytics engineering in a supported warehouse/Spark platform | Moving raw data across many connectors or handling all infrastructure/orchestration needs by itself. ADF can invoke dbt jobs where integration is supported. |
| **Airflow** | Code-defined DAGs, rich dependency logic, broad integrations, and workflows across multiple platforms | A team wants minimal orchestration infrastructure and ADF already meets the requirements. Airflow requires operational ownership or a managed service. |

A common production architecture is **ADF for ingestion and orchestration → Databricks/Spark or a SQL warehouse for heavy transformation → dbt for warehouse models/tests where appropriate**. ADF can dispatch to supported services and wait for completion. Keep business transformation logic in the engine that best supports testing, versioning, observability, and performance. Avoid duplicating the same transformation in both ADF Mapping Data Flow and Spark/dbt without a clear ownership boundary.

## 14. Hands-on lab — `experiments/03_adf/`

The lab is designed around the roadmap's six tasks. The companion files in this folder contain an example SQL control-plane schema, a run checklist, and deployment notes. This lesson provides the design; Azure resources must be created and configured in your own subscription.

### Lab prerequisites and safety

- Azure subscription with budget alert; do not use production credentials or data.
- ADF instance, ADLS Gen2 storage account, and either Azure SQL Database or an accessible test REST API.
- Permissions to create pipeline artifacts and configure identity/network access.
- Azure SQL source table containing a stable key and a reliable `LastModifiedUtc` (or use an API with a documented cursor/change token).
- A non-production second factory or environment for deployment practice.

### Task 1 — Copy SQL/API data to ADLS as Parquet

In ADF Studio, create linked services for the source and ADLS Gen2. Prefer managed identity where supported. Grant the factory identity the minimum source read permission and destination write permission. Create a source dataset for the SQL table or REST endpoint and a Parquet sink dataset for a path such as `bronze/sales/orders/`.

Create `PL_LoadOneTable` with a Copy activity. Start with a full load for a small test table. Set explicit mappings for critical fields, select Parquet as sink format, and run a test. Validate row counts and inspect the output files in Storage Explorer or a notebook. If using REST, configure pagination and rate limits according to the API contract; a single GET is not a general extraction strategy.

### Task 2 — Use Lookup + ForEach over the control table

Create and seed `etl.TableConfig` and `etl.TableWatermark` using `experiments/03_adf/sql/control_tables.sql`. Create a Lookup activity that selects enabled rows, with first-row-only disabled. Add a ForEach whose items expression is:

```text
@activity('LookupEnabledTables').output.value
```

Inside the loop, execute `PL_LoadOneTable` and map parameters from `@item()`. Start sequentially. Validate that each enabled table is processed exactly once per parent run and that disabled tables are skipped. Add a third or fourth table before scaling the pattern toward the roadmap's 20-table design.

### Task 3 — Watermark incremental load

Add a source watermark column or equivalent change token. Implement the low/high watermark query and the stored procedure pattern in `sql/watermark_procedures.sql`. The child pipeline should:

1. Read low watermark from `etl.TableWatermark`.
2. Capture high watermark from the source before extracting the range.
3. Copy the range to a run-specific staging path.
4. Validate output and publish/merge it using an idempotent strategy.
5. Call the watermark advancement procedure only after output commit.
6. Log success; on failure, retain the previous committed watermark and mark the run failed.

Test failure injection by forcing a validation failure before watermark advancement. Confirm the low watermark does not move. Rerun the interval and verify the sink has no duplicate logical records. Then test an update to an existing source row and confirm your selected watermark/CDC strategy captures it.

**Important:** writing Parquet files and updating a SQL watermark are not one distributed transaction. Use run-specific staging and a commit/manifest convention, or load into a transactional target with idempotent merge semantics. Document the recovery procedure for a crash between output commit and watermark update.

### Task 4 — Mapping Data Flow deduplication and aggregation

Create a Mapping Data Flow with a source pointing to the staged Parquet files. Add a Derived Column for normalisation, a Window transformation partitioned by the business key and ordered by modification time plus a deterministic tie-breaker, a Filter retaining the latest row, then an Aggregate grouped by the chosen dimension. Write the result to a silver or gold target.

Use debug mode on a small sample. Check null keys, timestamp ties, data types, and aggregate totals. If enabling schema drift, demonstrate an added optional column and verify the sink mapping behavior. Stop the debug session when finished and set a suitable TTL.

### Task 5 — Git and second-environment deployment

Connect the development factory to the supported Git provider from ADF Studio. Create a feature branch, commit the pipeline/data flow, open a pull request, and publish according to your collaboration-branch workflow. Deploy the generated factory ARM artifacts to a second test factory using environment-specific parameter values. Use a different identity or permissions boundary where possible. Verify linked services, Key Vault references, IR connectivity, global parameters, and output paths before enabling triggers.

Do not treat an ARM/Bicep snippet as a substitute for validating the actual generated ADF deployment artifacts. Use the current official CI/CD instructions for your repository and deployment service.

### Task 6 — Failure alerting

Configure ADF diagnostic settings to send supported pipeline/activity logs and metrics to Log Analytics or Azure Monitor. Create an alert/action group for pipeline failures, or use a supported webhook/Logic App notification route. Trigger a deliberate failure in a test pipeline, confirm the alert arrives, and check that logs contain the pipeline run ID and activity context without secrets.

### Expected evidence (not pre-claimed results)

Your evidence should include screenshots or exported JSON of the pipeline graph, control table rows, one successful full load, one incremental load, one intentionally failed run with an unchanged watermark, Mapping Data Flow design, Git commit/PR, deployment to the second environment, and a received alert. Record actual durations and costs from your environment. This lesson does not claim any Azure deployment or runtime test has already occurred.

## 15. Practice exercises

1. A source table has no reliable modification timestamp but supports SQL Server Change Tracking. Explain why a simple `MAX(id)` watermark is insufficient and sketch a safe checkpoint strategy.
2. A ForEach loop processes 20 tables. Two tables fail but the parent pipeline is marked successful. What dependency/error-handling design would you change?
3. A Copy activity is slow. List at least five measurements or checks you would perform before increasing DIUs or parallelism.
4. A new source column appears unexpectedly. When would schema drift be acceptable, and when should the pipeline fail?
5. A pipeline writes Parquet successfully but crashes before updating its watermark. Describe a safe retry and publication strategy.
6. A transformation uses a join, ranking, and multiple custom functions over several terabytes. Decide between Mapping Data Flow, Databricks/Spark, and dbt, explaining the boundary of responsibility.

## 16. Answer key (summary)

1. `MAX(id)` only captures inserts with monotonically increasing IDs; it usually misses updates and deletes. Use a supported change token/CT version, persist the last committed version, query changes within the valid retention window, and checkpoint only after the sink is committed. Detect expired retention and trigger a reinitialisation/reconciliation path.
2. Make each child failure visible and propagate required failures to the parent. Use failure dependencies for logging/notification, then ensure the pipeline's final outcome is failed if any required table failed. Do not swallow the exception or report success after logging.
3. Check source query plan/locks and throttling, bytes and rows, source/sink throughput, IR region/network, partition distribution, DIU applicability, parallel-copy settings, sink transaction/file counts, type conversion, and competing workloads. Benchmark one change at a time.
4. Drift can be accepted in exploratory/raw ingestion when fields are intentionally flexible and monitored. Curated contracts should validate required columns/types and alert or fail on unexpected changes that could break consumers.
5. Write to a run-specific staging path, validate, publish through an idempotent merge or commit marker, and then advance the watermark. A rerun must overwrite/reconcile the same logical interval rather than append duplicate rows blindly.
6. Mapping Data Flow is suitable for managed visual transformations when its expressiveness and cost profile fit. Databricks/Spark is often preferable for large/custom code-heavy transformations and deeper Spark control. dbt is suited to SQL-model layers and tests in a supported engine. ADF orchestrates and monitors the chosen engine.

## 17. Checkpoint

Before moving to Topic 04, verify that you can:

- [ ] Build parameterised, metadata-driven pipelines using Lookup and ForEach.
- [ ] Explain linked services, datasets, activities, pipelines, triggers, and all three IR types.
- [ ] Select an appropriate trigger and explain its execution-window semantics.
- [ ] Implement an incremental load with safe watermark advancement and recovery.
- [ ] Build a Mapping Data Flow that deduplicates and aggregates, and explain schema drift and debug-cluster cost.
- [ ] Configure retries, timeouts, failure paths, durable logging, and failure alerting.
- [ ] Promote the factory between environments through Git and a repeatable deployment process.
- [ ] Explain when to orchestrate Spark/dbt/Airflow instead of implementing transformations in ADF.

### Common mistakes to avoid

- Creating one independent pipeline per source table instead of a controlled metadata-driven pattern.
- Hard-coding connection strings, credentials, environment names, or endpoints in expressions.
- Building SQL or REST URLs from unvalidated metadata.
- Advancing a watermark before the sink is committed and validated.
- Assuming retries imply exactly-once execution or that Copy is automatically idempotent.
- Ignoring late updates, hard deletes, duplicate event notifications, and overlapping runs.
- Leaving Mapping Data Flow debug compute running.
- Increasing DIUs or parallelism without measuring source/sink bottlenecks.
- Swallowing failures in a logging branch and allowing the parent pipeline to appear successful.
- Using Mapping Data Flow for complex transformation logic that belongs in tested Spark/dbt code.
- Assuming a successful deployment proves runtime permissions, network connectivity, or data correctness.

## 18. Official references

Use these official Microsoft Learn pages as the source of truth for current connector support, expressions, feature availability, and deployment steps:

1. [Introduction to Azure Data Factory](https://learn.microsoft.com/en-us/azure/data-factory/introduction) — core objects, pipelines, data flows, and IR.
2. [Pipelines and activities](https://learn.microsoft.com/en-us/azure/data-factory/concepts-pipelines-activities) — control flow and activity behavior.
3. [Linked services and datasets](https://learn.microsoft.com/en-us/azure/data-factory/concepts-datasets-linked-services) — connection and data-reference model.
4. [Copy activity performance and scalability](https://learn.microsoft.com/en-us/azure/data-factory/copy-activity-performance) — tuning and throughput guidance.
5. [Incrementally copy a table](https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-portal) — watermark-based copy pattern.
6. [Incrementally copy multiple tables](https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-multiple-tables-portal) — metadata-driven multi-table example.
7. [Mapping Data Flow schema drift](https://learn.microsoft.com/en-us/azure/data-factory/concepts-data-flow-schema-drift) — drifted columns and mappings.
8. [Global parameters](https://learn.microsoft.com/en-us/azure/data-factory/author-global-parameters) — environment configuration.
9. [Automate continuous integration and delivery](https://learn.microsoft.com/en-us/azure/data-factory/continuous-integration-delivery-automate-azure-pipelines) — deployment workflow.
10. [Linked ARM templates](https://learn.microsoft.com/en-us/azure/data-factory/continuous-integration-delivery-linked-templates) — large-factory deployment artifacts.
11. [Create a tumbling-window trigger](https://learn.microsoft.com/en-us/azure/data-factory/how-to-create-tumbling-window-trigger) — window boundaries, dependencies, backfill, and concurrency.
12. [Lookup activity](https://learn.microsoft.com/en-us/azure/data-factory/control-flow-lookup-activity) — first-row-only behavior and array output.
13. [ForEach activity](https://learn.microsoft.com/en-us/azure/data-factory/control-flow-for-each-activity) — iteration expressions, concurrency, and limits.
14. [System variables](https://learn.microsoft.com/en-us/azure/data-factory/control-flow-system-variables) — trigger metadata and context-specific system variables.
15. [Choose the right Integration Runtime configuration](https://learn.microsoft.com/en-us/azure/data-factory/choose-the-right-integration-runtime-configuration) — IR capability and connectivity decisions.
16. [Integration Runtime performance](https://learn.microsoft.com/en-us/azure/data-factory/concepts-integration-runtime-performance) — Mapping Data Flow cluster sizing and TTL.
17. [Copy activity overview](https://learn.microsoft.com/en-us/azure/data-factory/copy-activity-overview) — connector behavior, DIUs, parallel copies, and supported scenarios.

**Verification limitation:** This is a source-aligned learning lesson with illustrative SQL and expression fragments. Azure connector behavior, exact trigger output shapes, supported dynamic parameterization, networking options, pricing, and deployment artifacts can vary by connector, region, and product updates. Validate these in the target factory and current official documentation. No Azure resources were created and no pipeline, Mapping Data Flow, stored procedure, CI/CD deployment, or alert was executed as part of authoring this file.
