# Sqoop, Flume, and Oozie: Legacy Hadoop Tooling

> **Roadmap path:** `Stage 2C — Data Engineering_3/02-Hadoop-Ecosystem-and-Legacy-Big-Data/06-sqoop-flume-and-oozie-legacy-tooling.md`  
> **Position:** Topic 06, Phase C — Wide-Column and Legacy Tooling  
> **Purpose:** Understand, maintain, document, and migrate existing workloads. These are historical Hadoop-era tools, not default choices for new platforms.

## 1. Learning objectives

By the end, you should be able to:

- Explain the separate roles of Sqoop (bulk relational transfer), Flume (event/log collection), and Oozie (workflow orchestration).
- Read legacy commands, XML workflows, and property-style configurations without assuming every distribution behaves identically.
- Explain Sqoop imports/exports, `--split-by`, parallelism, and incremental modes.
- Trace Flume events through source, channel, and sink, including delivery and recovery implications.
- Explain Oozie actions, workflow control flow, coordinators, and bundles.
- Inventory production jobs with owners, dependencies, schedules, SLAs, security, and recovery behavior.
- Design a safer watermark-based extraction with idempotent loads.
- Translate an Oozie workflow to Airflow while preserving dependency, schedule, failure, and output semantics.
- Replace a Flume-style log pipeline with Kafka-based ingestion.
- Decide whether to rewrite, wrap, freeze, or retire a legacy job.

## 2. Prerequisites and roadmap fit

| Prerequisite | How it applies |
|---|---|
| Linux shell, permissions, processes, logs | Inspect service processes, configs, logs, and scheduler handoffs. |
| HDFS and YARN | Sqoop and Oozie actions often execute Hadoop jobs; Flume commonly writes to HDFS. |
| MapReduce/Spark | Understand the compute jobs launched by ingestion and orchestration tools. |
| Hive and HBase | Identify targets and downstream consumers; Sqoop often loaded HDFS/Hive tables, while other workflows may write HBase. |
| SQL and JDBC | Understand relational extraction, split columns, incremental predicates, and schema drift. |
| Kafka and Airflow basics | Useful for evaluating modern replacements. |
| Data reconciliation | Validate source/target counts, watermarks, duplicates, and business outputs. |

**Roadmap sequence:** HDFS → YARN → MapReduce → Hive → HBase → this legacy-tooling lesson → Hadoop-to-cloud-lakehouse migration. HDFS supplies storage, YARN schedules resources, MapReduce/Spark perform processing, Hive provides SQL/catalog conventions, and HBase serves random access. Sqoop/Flume/Oozie complete the legacy-cluster picture: transfer, event ingestion, and orchestration. The next lesson inventories and migrates the whole platform.

The roadmap recommends a Docker Compose Hadoop lab, Python 3.12+ in a `uv` project, and MinIO as an earlier-module migration target. Community images and old Hadoop distributions vary: pin versions, use isolated test data, and do not infer production support from a container starting successfully.

## 3. Historical context: three different responsibilities

Sqoop, Flume, and Oozie often appeared together, but they are not interchangeable.

```text
Relational DB ---- Sqoop / JDBC batch extraction ----> HDFS / Hive
Application logs ---- Flume source -> channel -> sink ----> HDFS
                                                        |
                                                        v
Oozie coordinator --> workflow actions --> Sqoop / Hive / MapReduce / scripts
                                                        |
                                                        v
                                           downstream datasets / reports
```

- **Sqoop** moved structured data between relational databases and Hadoop storage/processing systems in bulk. It generated parallel map tasks and was useful for initial loads and incremental imports.
- **Flume** collected and transported event streams, especially logs, through pluggable sources, channels, and sinks.
- **Oozie** defined and scheduled workflows made of actions and control-flow transitions. It coordinated jobs; it was not itself the database importer or event transport.
- **Modern alternatives are not drop-in replacements.** Spark JDBC, Airbyte, Kafka, Airflow, and Dagster have different runtime, retry, state, security, and operational semantics.

### 3.1 Why engineers still need to know them

Legacy estates may have years of implicit behavior encoded in XML, shell scripts, service configs, database grants, and schedules. A safe migration starts by discovering that behavior—not by replacing a tool based on its name. The goal is to reproduce required outputs and operational guarantees, then improve them deliberately.

## 4. Sqoop: bulk transfer between relational systems and Hadoop

### 4.1 Core concepts

Apache Sqoop was designed to move structured data between relational databases and Hadoop ecosystems such as HDFS and Hive. Common operations included:

- **Import:** relational table/query → HDFS or Hive.
- **Export:** HDFS data → relational table.
- **Parallel import:** multiple mapper tasks extract disjoint ranges of rows.
- **`--split-by`:** selects a column used to divide an import into ranges when Sqoop cannot use a suitable primary-key split automatically or when a specific split column is required.
- **Incremental import:** imports rows based on a `check-column` and a `last-value` boundary or imports new rows by key using an append mode.
- **Schema mapping:** maps relational column types to Hadoop representations; type and nullability behavior must be checked for the actual driver and Sqoop version.

Sqoop is a historical/deprecated ecosystem component in many environments. Some vendor distributions retain it, while newer database drivers, JDKs, Hadoop APIs, and security requirements may make old commands difficult to run. Treat examples below as representative legacy syntax; validate them against the installed Sqoop release and JDBC driver.

### 4.2 Representative legacy import

Historical command pattern:

```bash
sqoop import \
  --connect 'jdbc:mysql://db.example.internal:3306/sales' \
  --username "$DB_USER" \
  --password-file 'hdfs:///user/sqoop/secrets/db.password' \
  --table orders \
  --target-dir '/data/landing/orders/run_date=2026-10-19' \
  --as-parquetfile \
  --num-mappers 4 \
  --split-by order_id
```

**Prerequisites and caveats**

- A compatible Sqoop installation, Hadoop configuration, JDBC driver, database network route, and least-privilege database account.
- The password-file mechanism and filesystem URI must be supported by the installed distribution and readable only by the intended principal. Do not put passwords directly in shell history.
- `--as-parquetfile` is not supported uniformly by every historical Sqoop build; some distributions need a compatible connector or a different output format. Confirm the actual release before using this exact flag.
- `--target-dir` should be a new, run-specific path unless overwrite/append behavior is intentionally designed.
- The `orders` table and `order_id` column are illustrative. The split column should be stable and reasonably distributed.

### 4.3 `--split-by` and parallelism

Parallel mappers improve throughput when each mapper extracts a disjoint subset. Sqoop commonly determines split boundaries using min/max values of the split column and generates range predicates. The split column should generally be numeric/date-like and indexed where practical.

Risks include:

- **Skew:** one range contains far more rows than another, so one mapper runs much longer.
- **Bad split column:** a low-cardinality or uneven column creates poor parallelism.
- **Database overload:** more mappers increase concurrent queries and can harm the source OLTP system.
- **Nulls and gaps:** split logic and null handling depend on version/connector; test actual behavior.
- **Non-repeatable extraction:** rows can change while parallel queries run unless transaction/isolation and source mutation behavior are understood.

Do not maximize mapper count blindly. Select it based on database capacity, connection limits, query plans, network throughput, and observed skew. In production, coordinate with the database owner and establish a source-load ceiling.

### 4.4 Import modes: full, append, lastmodified

A full import extracts the selected table/query. It is simple to reason about but can be expensive for large sources.

Sqoop's historical incremental options included:

- `--incremental append`: import rows whose incrementing key is greater than `--last-value`; typically appropriate for insert-only data with a monotonic key.
- `--incremental lastmodified`: import rows whose check-column timestamp is newer than the saved boundary; commonly used for rows that can be updated.
- `--check-column`: column used to determine whether rows are new/changed.
- `--last-value`: starting boundary supplied to the import. The next successful boundary must be recorded by the orchestration/state mechanism.

Example pattern:

```bash
sqoop import \
  --connect 'jdbc:postgresql://db.example.internal:5432/commerce' \
  --username "$DB_USER" \
  --password-file 'hdfs:///user/sqoop/secrets/commerce.password' \
  --table orders \
  --target-dir '/data/landing/orders/incremental/run_id=20261019T090000Z' \
  --incremental lastmodified \
  --check-column updated_at \
  --last-value '2026-10-18 00:00:00' \
  --num-mappers 1
```

This command is illustrative, not a complete stateful production pipeline. The `last-value` shown must come from durable orchestration state, and timestamp literal parsing varies by database/driver. A single mapper avoids parallel split complexity in this example; if parallelism is needed, design and test it separately.

### 4.5 Incremental import failure modes

- `append` can miss updates to existing rows because an update does not necessarily increase the key.
- `lastmodified` can miss rows if timestamps are not updated reliably, if the boundary is advanced too early, or if late transactions commit with old timestamps.
- A strict `>` boundary can miss equal-timestamp records if multiple rows share the boundary and a checkpoint is advanced incorrectly.
- Re-running a window can produce duplicates unless the target has a deterministic deduplication/upsert strategy.
- Updating the watermark before target commit can create data loss after a crash.
- Advancing the watermark only after target commit can cause replays; that is safe only if loading is idempotent.

**Safer principle:** use a durable high-water mark, extract an overlapping/replayable window when feasible, deduplicate by business key plus source version/change timestamp, commit target data before advancing state, and make retries safe. For sources with deletes, a simple updated-at query may not capture deleted rows; use CDC, soft-delete records, tombstones, or periodic reconciliation.

### 4.6 Exporting to a relational database

Representative historical command pattern:

```bash
sqoop export \
  --connect 'jdbc:postgresql://db.example.internal:5432/commerce' \
  --username "$DB_USER" \
  --password-file 'hdfs:///user/sqoop/secrets/commerce.password' \
  --table daily_order_totals \
  --export-dir '/warehouse/exports/daily_order_totals/run_date=2026-10-19' \
  --input-fields-terminated-by '\001' \
  --num-mappers 4
```

Export expects a compatible row format and column mapping. The target table/schema must exist unless a specific supported workflow creates it. Delimiters, null encodings, quoting, escaping, and column order matter. Export may issue parallel inserts; duplicate keys, partial task failure, and retry behavior must be evaluated against target constraints and transaction semantics.

**Production rule:** use staging tables or deterministic keys and explicit merge/upsert logic when the target must not receive duplicate or partially applied rows. Verify how the exact Sqoop version commits batches and handles task retries.

## 5. Flume: collecting and transporting log events

### 5.1 Source, channel, sink

Apache Flume is a distributed service for collecting, aggregating, and moving event data, especially logs.

- **Source:** receives events from a source system, such as a file tailing source, syslog source, or network source.
- **Channel:** buffers events between source and sink. Common historical channels include memory and file channels.
- **Sink:** delivers events to a destination, such as HDFS, HBase, or another Flume agent.
- **Agent:** a running Flume process with named sources, channels, and sinks connected by configuration.

```text
Application log / syslog
          |
          v
       Source
          |
    transaction boundary
          v
       Channel  <---- durable file channel can survive some process failures
          |
          v
         Sink
          |
          +----> HDFS files / downstream processing
```

The source and sink often transact with the channel so an event is removed only after sink delivery is acknowledged according to the configured component semantics. This is not a universal end-to-end exactly-once guarantee: retries, sink behavior, partial failures, and downstream processing can still create duplicates or loss if configured incorrectly.

### 5.2 Representative historical configuration

The following is a teaching example of classic Flume agent configuration. Component class names and options depend on the Flume release and distribution; validate them against the deployed documentation before using them.

```properties
# Agent name: a1
a1.sources = r1
a1.channels = c1
a1.sinks = k1

# Source: tail a local application log
a1.sources.r1.type = exec
a1.sources.r1.command = tail -F /var/log/myapp/events.log
a1.sources.r1.channels = c1

# Channel: disk-backed buffering
a1.channels.c1.type = file
a1.channels.c1.checkpointDir = /var/lib/flume/checkpoint
a1.channels.c1.dataDirs = /var/lib/flume/data

# Sink: HDFS
a1.sinks.k1.type = hdfs
a1.sinks.k1.hdfs.path = hdfs://nameservice1/logs/myapp/%Y/%m/%d/%H
a1.sinks.k1.hdfs.filePrefix = events
a1.sinks.k1.hdfs.fileType = DataStream
a1.sinks.k1.hdfs.rollInterval = 300
a1.sinks.k1.channel = c1
```

**Important limitations**

- `exec` with `tail -F` is convenient for a lab but is not a robust production source in every scenario. It can lose data across process restarts, rotation behavior, or command failure depending on the setup. Prefer a source with a well-understood checkpoint/acknowledgement model when available.
- The file channel requires persistent storage, correct permissions, capacity planning, and recovery testing. A disk-full channel can block or reject events.
- HDFS sink properties and defaults vary by Flume version. Confirm path templating, file rolling, compression, HDFS HA URI, Kerberos, and small-file behavior.
- File sinks must roll files to avoid a single open file growing indefinitely; overly frequent rolling creates too many small files.

### 5.3 Delivery semantics and operational concerns

Ask these questions of every existing pipeline:

1. When does the source consider an event accepted?
2. Is the channel in-memory or disk-backed? What survives process/node failure?
3. Does the sink acknowledge only after the destination has persisted data?
4. Can retries replay an event? What is the deduplication key?
5. What happens when the sink is unavailable or the channel fills?
6. Are events ordered, and at what scope?
7. How are source offsets/file positions/checkpoints preserved across restart?
8. How are schema changes and malformed records handled?
9. What are the channel capacity, queue depth, back-pressure, and alert thresholds?

Do not call a pipeline “exactly once” solely because it uses a file channel. End-to-end delivery guarantees depend on every stage and on the destination's idempotency/deduplication behavior.

### 5.4 Flume-to-Kafka architecture

```text
Applications / agents
       |
       v
Fluent Bit or another supported log shipper
       |
       v
Kafka topic (partitioned, replicated)
       |
       +----> Kafka Connect sink / stream processor ----> object storage / lakehouse
       |
       +----> consumer group ---------------------------> alerting / search
```

Kafka is a durable event log with partition ordering, retention, replication, and consumer offsets. Kafka Connect manages connector-based movement into/out of Kafka. Fluent Bit is a lightweight log processor/forwarder; it is not a direct semantic clone of every Flume source or channel.

Migration must map event identity, partition key, ordering requirements, buffering, retries, retention, back-pressure, dead-letter behavior, security, and downstream file layout. A Kafka topic does not automatically reproduce Flume's HDFS file naming/rolling conventions or its failure semantics.

## 6. Oozie: XML workflow orchestration

### 6.1 Main concepts

Apache Oozie historically orchestrated Hadoop jobs through XML definitions.

- **Workflow:** a directed control-flow graph of actions and transitions.
- **Action:** a unit of work, such as a MapReduce, Hive, Pig, Sqoop, Java, Shell, or supported Spark action; availability depends on the distribution and Oozie extensions.
- **`ok` / `error` transitions:** route control flow after an action succeeds or fails.
- **Kill node:** ends a failed/aborted workflow.
- **Coordinator:** schedules workflow executions based on time intervals and/or data availability/dependencies.
- **Bundle:** groups related coordinators for management and lifecycle operations.
- **Workflow parameters:** values supplied at submission/runtime, often including input/output paths and dates.

Oozie schedules and coordinates jobs; YARN still allocates resources to underlying Hadoop jobs. An Oozie workflow is not simply a list of commands: dependency transitions, retry policies, timeouts, coordinator missed/late-data behavior, and output paths are part of its behavior.

### 6.2 Workflow architecture

```text
Coordinator (time/data trigger)
          |
          v
      Workflow
          |
          v
   Sqoop import
          |
          | ok
          v
    Hive transform
          |
          | ok
          v
   Publish / validate
          |
          +-- error --> alert / controlled failure
```

### 6.3 Representative workflow XML

This is a compact historical example, not a complete production workflow. Oozie XML namespaces and action support must match the installed Oozie release and Hadoop distribution.

```xml
<workflow-app name="daily-orders" xmlns="uri:oozie:workflow:0.5">
  <start to="import-orders"/>

  <action name="import-orders">
    <sqoop xmlns="uri:oozie:sqoop-action:1.0">
      <resource-manager>${resourceManager}</resource-manager>
      <name-node>${nameNode}</name-node>
      <arg>import</arg>
      <arg>--connect</arg>
      <arg>${jdbcUrl}</arg>
      <arg>--username</arg>
      <arg>${dbUser}</arg>
      <arg>--password-file</arg>
      <arg>${passwordFile}</arg>
      <arg>--table</arg>
      <arg>orders</arg>
      <arg>--target-dir</arg>
      <arg>${landingPath}</arg>
      <arg>--num-mappers</arg>
      <arg>1</arg>
    </sqoop>
    <ok to="transform-orders"/>
    <error to="fail"/>
  </action>

  <action name="transform-orders">
    <hive xmlns="uri:oozie:hive-action:0.5">
      <job-tracker>${jobTracker}</job-tracker>
      <name-node>${nameNode}</name-node>
      <script>sql/transform_orders.hql</script>
      <param>input_path=${landingPath}</param>
      <param>run_date=${runDate}</param>
    </hive>
    <ok to="end"/>
    <error to="fail"/>
  </action>

  <kill name="fail">
    <message>daily-orders failed</message>
  </kill>
  <end name="end"/>
</workflow-app>
```

This illustrates action ordering and error transitions. The Sqoop action uses the documented `uri:oozie:sqoop-action:1.0` namespace and individual `<arg>` elements so each command-line argument remains distinct; a single `<command>` string is split on spaces and is fragile when an argument itself contains spaces. The workflow namespace and Hive action namespace must also match the deployed Oozie release. Validate the complete workflow against that release's XSD and sample workflows before deployment. Do not paste this into production without adapting it to the installed version.

### 6.4 Coordinators and bundles

A coordinator can trigger workflow instances by time and/or data availability. In data-driven workflows, a nominal schedule is not equivalent to “all upstream data is ready.” The coordinator's input dataset frequency, timezone, start/end time, availability check, and late-data policy determine actual runs.

A bundle groups coordinators so operators can manage a suite of related schedules together. During migration, inventory bundle membership and shared parameters; converting each workflow independently may lose orchestration-level controls.

For every coordinator, capture:

- start/end time, frequency, timezone, and schedule alignment;
- input/output dataset definitions and readiness conditions;
- behavior when data arrives late or never arrives;
- catch-up/missed-run behavior and concurrency;
- run-specific parameter expressions;
- notifications, retries, timeouts, and kill behavior.

A minimal **time-based coordinator** illustrates how the workflow is scheduled and how its nominal date is passed to the workflow. This is a versioned XML template: replace the application path and parameters, then validate it against the coordinator XSD installed with the cluster.

```xml
<coordinator-app name="daily-orders-coord"
                 frequency="${coord:days(1)}"
                 start="${startTime}"
                 end="${endTime}"
                 timezone="UTC"
                 xmlns="uri:oozie:coordinator:0.4">
  <action>
    <workflow>
      <app-path>${nameNode}/user/${user}/apps/daily-orders</app-path>
      <configuration>
        <property>
          <name>runDate</name>
          <value>${coord:formatTime(coord:nominalTime(), 'yyyy-MM-dd')}</value>
        </property>
      </configuration>
    </workflow>
  </action>
</coordinator-app>
```

For a **data-triggered coordinator**, define an input dataset with a frequency, URI template, and readiness marker (often `_SUCCESS` for a completed HDFS output), then reference it from an `<input-events><data-in>…</data-in></input-events>` section. The exact dataset URI template and done-flag must match the upstream producer's contract; a file existing is not proof that its contents are complete. A bundle groups coordinator applications for lifecycle management; it does not by itself create dependencies between those coordinators. These XML namespaces and dataset conventions are release-specific and must be schema-validated before use.

### 6.5 Failure handling and retries

Oozie action failure transitions are explicit in XML. The action's own retry behavior may also be configured by action type/distribution. A workflow can route to an error handler, terminate, or perform compensating steps.

Before migration, distinguish:
- **Task retry:** rerun a failed action attempt.
- **Workflow rerun:** rerun a failed workflow instance, potentially reusing or replacing outputs.
- **Coordinator catch-up:** create or run instances for missed schedule intervals.
- **Data replay:** deliberately process a prior business date/input range.
- **Idempotency:** ensure repeated work does not create duplicate or conflicting output.

Airflow retries and catchup are not automatically equivalent to Oozie semantics. Preserve old behavior intentionally, then improve it in a separately reviewed change.

## 7. Modern alternatives: choose by responsibility and required semantics

| Legacy responsibility | Candidate replacement | Suitable when | Migration caveats |
|---|---|---|---|
| Sqoop bulk import/export | Spark JDBC | Transformations, distributed extraction, or custom reconciliation are required | JDBC reads can overload the source; partitioning, isolation, and retries need explicit design. Spark JDBC is not automatically a CDC system. |
| Sqoop connector-driven ingestion | Airbyte, dlt, or a managed connector | The source/destination is supported and connector behavior matches the required load mode | Verify incremental cursor, deletes, schema drift, rate limits, state persistence, destination merge, and licensing/hosting. Feature support varies by connector. |
| Flume log/event transport | Kafka + Kafka Connect | Durable replayable event streams and multiple independent consumers are useful | Requires broker operations or a managed service, topic/partition design, retention, consumer lag monitoring, and schema strategy. |
| Flume log forwarding | Fluent Bit or another maintained agent | Host/container logs need filtering, enrichment, and forwarding | Does not recreate every Flume channel/source/sink behavior; test buffering, disk limits, back-pressure, and delivery guarantees. |
| Oozie workflows/coordinators | Airflow | Python-defined DAGs, broad integrations, observability, and operator tooling fit | Oozie coordinator data availability and catch-up semantics need explicit recreation; retries and task state are not identical. |
| Oozie workflows | Dagster | Asset/data-product orchestration and data-aware lineage are a strong fit | Requires translating job-centric workflows to asset/job concepts and validating scheduling semantics. |

Modern tools are options, not mandatory destinations. A managed connector may be operationally simpler than custom Spark code, while Spark JDBC may be more suitable when extraction is tightly coupled to transformation and data validation. Kafka is a platform, not merely a replacement executable for Flume. Airflow and Dagster orchestrate work; they do not themselves replace data movement engines.

## 8. A safe incremental ingestion design with watermarks

The goal is not to recreate Sqoop flags one for one. It is to preserve the required source-to-target contract under retries, late updates, and partial failures.

### 8.1 State machine

```text
Read durable watermark W
        |
        v
Choose extraction window [W - overlap, upper_bound U)
        |
        v
Extract rows to run-specific staging area
        |
        v
Validate schema, row counts, bounds, and malformed records
        |
        v
Deduplicate by primary key + source version/change timestamp
        |
        v
Idempotent merge/upsert into target (or atomic partition replace)
        |
        v
Commit target successfully, then persist new watermark U
```

**Important ordering:** persist the new watermark only after the target commit succeeds. If a crash occurs after target commit but before watermark commit, the next run may replay data; the target must therefore be idempotent. If the watermark advances first and the target write then fails, rows can be skipped permanently.

### 8.2 Watermark strategy

- Prefer a reliable source `updated_at` or change sequence maintained by the source transaction, not an application timestamp that may be stale.
- Use a bounded upper limit `U` captured at the start of the run where the source supports a stable snapshot/consistent read. This prevents the extraction window from drifting while it runs.
- Use an overlap window to accommodate late commits and timestamp precision issues, then deduplicate deterministically. The overlap is a mitigation, not a substitute for CDC or source guarantees.
- If multiple records can share a timestamp, use a composite cursor such as `(updated_at, primary_key)` or a source change sequence. Store both values and define lexicographic boundary semantics.
- For hard deletes, use CDC/delete events, soft-delete flags, or reconciliation. A simple `WHERE updated_at > watermark` query cannot discover a physically deleted row.
- Treat schema changes as an explicit compatibility event. Fail closed or route unknown columns/types to a reviewed path rather than silently corrupting the target.

### 8.3 Spark JDBC emulation lab code

This example illustrates a **batch JDBC extraction** in Spark, not a complete production connector. It assumes the source has a numeric primary key `order_id` and a reliable `updated_at` column. Configure the JDBC driver, Spark/JDBC versions, credentials, database access, and target table for your environment.

```python
import os
from pyspark.sql import SparkSession, functions as F, Window

spark = SparkSession.builder.appName("orders-incremental-lab").getOrCreate()

jdbc_url = os.environ["ORDERS_JDBC_URL"]
user = os.environ["DB_USER"]
password = os.environ["DB_PASSWORD"]

# These values are supplied by the orchestrator from durable control state.
# overlap_start is computed from the previous committed watermark minus overlap;
# upper_bound is captured at the beginning of this run.
overlap_start = os.environ["ORDERS_OVERLAP_START"]
upper_bound = os.environ["ORDERS_UPPER_BOUND"]

# Use a trusted, deployment-controlled identifier; do not accept arbitrary user input here.
# Adjust the schema/table name for the source database and validate it during deployment.
source_table = "public.orders"
query = f"""(
  SELECT order_id, customer_id, status, updated_at
  FROM {source_table}
  WHERE updated_at >= TIMESTAMP '{overlap_start}'
    AND updated_at <  TIMESTAMP '{upper_bound}'
) AS incremental_source"""

source = (spark.read.format("jdbc")
    .option("url", jdbc_url)
    .option("dbtable", query)
    .option("partitionColumn", "order_id")
    .option("lowerBound", os.environ["ORDERS_ID_LOWER_BOUND"])
    .option("upperBound", os.environ["ORDERS_ID_UPPER_BOUND"])
    .option("numPartitions", "4")
    .option("user", user)
    .option("password", password)
    .option("driver", "org.postgresql.Driver")
    .option("fetchsize", "1000")
    .load())

# Keep the latest source version for each business key in this extraction.
window = Window.partitionBy("order_id").orderBy(F.col("updated_at").desc())
deduplicated = (source.withColumn("rn", F.row_number().over(window))
                      .filter(F.col("rn") == 1)
                      .drop("rn"))

# Write to a run-specific staging target. A separate, database-specific MERGE/upsert
# or atomic partition replacement is required before advancing durable watermark state.
(deduplicated.write.format("parquet")
    .mode("overwrite")
    .save("s3a://training-lake/landing/orders/run_id=20261019T090000Z"))

spark.stop()
```

**Code notes:** this is illustrative and intentionally writes to a run-specific staging path. The JDBC URL, credentials, extraction bounds, and overlap start come from environment/secret-backed orchestration configuration. Do not build SQL predicates from untrusted user input; the source table name is trusted configuration here. Spark JDBC `lowerBound` and `upperBound` determine partition stride; they do **not** filter the result set, so the explicit `updated_at` predicate defines the extraction window. The ID bounds should reflect the key range and the source should be checked for skew. The code does not perform the target merge or update the watermark: those are separate transactional steps and must be implemented for the actual destination. `updated_at` alone may not totally order rows with identical timestamps; add a stable tie-breaker/version column when needed.

### 8.4 Idempotency patterns

- **Warehouse/lakehouse:** write to a run-specific staging table/path, validate, then `MERGE` on stable keys or atomically replace a deterministic partition. Confirm that the table format/catalog supports the chosen operation.
- **Relational target:** load a staging table and use a transaction with `INSERT ... ON CONFLICT`/`MERGE` semantics supported by that database.
- **File output:** publish immutable run paths and atomically update a manifest/pointer after validation. Avoid append-only retries to the same output directory without deduplication.
- **Watermark state:** store the old and new cursor, run ID, upper bound, target commit status, row counts, and validation outcome in a durable control table.
- **Failure recovery:** if a run fails before target commit, discard or reuse staging safely; if it fails after target commit, rerun idempotently and only then reconcile/advance the watermark.

## 9. Legacy-job inventory and discovery

Do not begin a migration until the team can answer what each job reads, writes, schedules, owns, and promises. Config files alone are not a complete inventory: inspect scheduler history, logs, HDFS paths, database grants, downstream queries, alerts, and operator knowledge.

### 9.1 Inventory schema

Use one row per job/action or one normalized job record plus dependency records. The following fields are a practical minimum.

| Field | Meaning / example |
|---|---|
| `job_id`, `job_name`, `tool` | Stable ID; e.g. `sqoop_orders_daily`; Sqoop/Flume/Oozie/script. |
| `business_purpose`, `criticality` | Why it exists; business impact if late or missing. |
| `source_system`, `source_object` | DB/schema/table, log path, topic, API, or upstream dataset. |
| `target_system`, `target_object` | HDFS path, Hive table, HBase table, database table, or downstream topic. |
| `load_mode`, `key_columns`, `watermark` | Full/incremental/CDC; merge keys; checkpoint state and owner. |
| `schedule`, `timezone`, `trigger_type` | Cron/coordinator interval, timezone, time vs data availability. |
| `dependencies_upstream`, `dependencies_downstream` | Required jobs, datasets, files, or control conditions. |
| `owner_team`, `technical_owner`, `on_call` | Accountable team and incident escalation. |
| `SLA`, `freshness_target`, `RPO`, `RTO` | Delivery deadline, tolerated data loss, recovery expectations. |
| `runtime_p50_p95`, `last_success`, `failure_rate` | Measured history, clearly labelled by time window and source. |
| `volume_rows_bytes`, `peak_rate` | Source/target volume and observed peak throughput. |
| `retry_policy`, `timeout`, `backfill_policy` | Retry count/delay, kill timeout, historical replay behavior. |
| `idempotency_strategy`, `dedupe_key` | What makes retries safe and how duplicates are removed. |
| `schema_contract`, `change_policy` | Column/type evolution, malformed data, compatibility expectations. |
| `security_identity`, `secrets_location`, `network_path` | Service principal, secret reference (never secret value), access path. |
| `data_classification`, `retention`, `lineage` | PII/sensitivity, retention/deletion rules, producers/consumers. |
| `monitoring`, `alerts`, `runbook` | Logs/metrics, alert destination, incident steps. |
| `migration_candidate`, `target_option`, `risk`, `decision` | Rewrite/wrap/freeze/retire and rationale. |
| `validation_plan`, `rollback_plan`, `cutover_owner` | Evidence of parity, rollback trigger, accountable approver. |

Do not invent runtime/volume values. Use observed history or mark them `unknown` with a discovery task and owner.

### 9.2 Discovery workflow

1. Search repository/configuration management for Sqoop commands, Flume properties, Oozie XML, shell scripts, cron entries, and environment-specific properties.
2. Export scheduler/job history for at least one representative business cycle, including failed, rerun, and late runs.
3. Trace every input/output to its actual HDFS path, Hive table, HBase table, relational object, or log source.
4. Inspect downstream consumers and implicit file-based dependencies. A job may depend on a directory being present, a `_SUCCESS` marker, a file naming convention, or a partition being complete.
5. Interview the operational owner about manual reruns, late data, known incidents, and exceptions that are not encoded in the config.
6. Capture service identities, credentials references, network routes, ACLs, encryption, retention, and audit obligations.
7. Build a dependency graph, mark cycles and hidden edges, and validate it against run history.
8. Assign confidence to each inventory fact and create remediation tasks for unknowns.

## 10. Oozie-to-Airflow migration: preserve behavior first

### 10.1 Mapping concepts carefully

| Oozie concept | Airflow concept | Required verification |
|---|---|---|
| Workflow action | Task/operator | Does the task invoke the same code, parameters, environment, and output paths? |
| `ok` transition | Downstream dependency | Ensure downstream runs only after the required upstream success. |
| `error` transition / kill node | Task failure, callbacks, failure task, DAG-run status | Preserve alerting, cleanup, and failure visibility. A failure callback alone is not a dependency branch. |
| Coordinator time schedule | DAG schedule/timetable | Match timezone, start/end, data interval, and schedule boundaries. |
| Coordinator data availability | Dataset/sensor/deferrable wait or explicit readiness check | Match what “data ready” means, timeout, late arrivals, and no-data behavior. |
| Coordinator catch-up | `catchup`, start date, data intervals, max active runs | Test missed intervals and backfills; do not assume defaults match Oozie. |
| Bundle | DAG grouping, deployment/configuration grouping, or orchestration-level controls | Bundles group coordinators but do not inherently impose dependencies between them. Preserve that distinction. |
| Oozie parameters | DAG/task params, Variables, Connections, templating | Keep secrets in a secret backend; define parameter scope and default behavior. |
| Action retries | Task `retries`, `retry_delay`, retry callbacks | Match attempts, delays, retryable exceptions, and idempotency. |

### 10.2 Example Airflow DAG

The following is an Airflow 2.x-style example using the `DAG` and `PythonOperator` APIs. The `schedule` argument and import paths should be checked against the installed Airflow minor version. It is a template, not a tested drop-in conversion. Replace the callables with environment-specific jobs, configure the executor/connections/secrets, and validate the installed Airflow version. A production implementation should normally invoke a real Sqoop-compatible legacy command or a modern extraction job through an appropriate operator/container, rather than embedding heavy extraction in the scheduler process.

```python
from datetime import timedelta
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator


def import_orders(**context):
    # Invoke a versioned extraction job/container or a well-tested command wrapper.
    # Use the logical data interval/run date, not datetime.now(), for reproducibility.
    run_date = context["ds"]
    run_id = context["run_id"]
    print(f"Run orders import for data date={run_date}, run_id={run_id}")
    # TODO: submit job, wait for completion, validate its exit status and output manifest.


def transform_orders(**context):
    # Submit Hive/Spark SQL using explicit run-date and input-path parameters.
    # Ensure the output is deterministic or atomically published for this data interval.
    print(f"Transform orders for data date={context['ds']}")
    # TODO: submit transformation and validate expected output.


def publish_and_validate(**context):
    # Compare counts/schema/business checks; publish only after validation passes.
    print(f"Validate and publish output for data date={context['ds']}")
    # TODO: fail the task if reconciliation does not meet documented tolerances.


def notify_failure(context):
    # Replace with the organization's alerting integration; do not swallow the failure.
    print(f"Pipeline failed: {context['dag'].dag_id} / {context['run_id']}")


default_args = {
    "owner": "data-platform",
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
    "depends_on_past": False,
}

with DAG(
    dag_id="daily_orders_legacy_migration_template",
    description="Template for preserving an Oozie import -> transform -> publish workflow",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule="0 2 * * *",  # Example only; replace UTC with the source coordinator's timezone.
    catchup=False,          # Deliberate choice; set only after matching coordinator semantics.
    max_active_runs=1,
    default_args=default_args,
    on_failure_callback=notify_failure,
    tags=["migration", "legacy-hadoop"],
) as dag:
    extract = PythonOperator(task_id="import_orders", python_callable=import_orders)
    transform = PythonOperator(task_id="transform_orders", python_callable=transform_orders)
    validate_publish = PythonOperator(task_id="publish_and_validate", python_callable=publish_and_validate)
    extract >> transform >> validate_publish
```

**What this preserves in the example:** import must succeed before transformation; transformation must succeed before publication; a task failure marks the DAG run failed and invokes the callback; retries are bounded; one active DAG run prevents overlapping runs. The code intentionally uses placeholders rather than pretending to submit real jobs.

**What it does not automatically preserve:** Oozie coordinator data availability, timezone, missed/late-run behavior, bundle controls, action-specific retry behavior, output cleanup, and exact alert/kill semantics. `catchup=False` is a sample policy, not a universal migration default. Set it only after reviewing how the old coordinator handled missed intervals. For data-driven schedules, use an explicit readiness sensor or dataset/event mechanism with timeout and late-data policy. If the original workflow ran every scheduled interval, test a backfill of representative intervals before cutover.

### 10.3 Migration parity test

For at least one normal run, one late-data run, one failure/retry, one manual rerun, and one backfill, compare:

- logical data interval and parameters;
- input set and readiness condition;
- action order and parallel branches;
- retry count, delays, timeout, and terminal status;
- output path/table/partition and marker-file behavior;
- notification recipients and failure visibility;
- source/target counts and deterministic business checks;
- concurrency and overlapping-run behavior;
- recovery after worker/scheduler restart.

Do not call the migration complete because the DAG parses. It is complete when behavior is demonstrated against a documented acceptance suite.

## 11. Flume-to-Kafka migration example

### 11.1 Design the replacement contract

Before choosing components, specify:

- event schema and schema-version policy;
- stable event ID or deduplication key;
- Kafka topic, partition key, partition count, replication factor, retention, and ACLs;
- source buffering and behavior when Kafka is unavailable;
- consumer offset/commit policy and replay strategy;
- dead-letter topic or quarantine path for malformed events;
- consumer lag, broker disk, producer errors, and end-to-end freshness alerts;
- downstream file/table layout and file rolling/compaction policy.

### 11.2 Example producer (modern implementation, not a Flume config)

This example uses Python's `kafka-python` package version that supports the `enable_idempotence` producer option (use a current compatible release and verify it against the installed Kafka broker). It assumes a reachable Kafka cluster, a topic named `app-events`, and appropriate authentication configuration if required. It is a learning snippet; production security, batching, retry policy, schema registry, metrics, and shutdown handling must be added for the deployment. Producer idempotence covers producer retry behavior within the broker protocol; it does not provide end-to-end exactly-once processing across consumers and external sinks.

```python
import json
import os
import time
import uuid
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=os.environ["KAFKA_BOOTSTRAP_SERVERS"].split(","),
    key_serializer=lambda value: value.encode("utf-8"),
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    acks="all",
    enable_idempotence=True,
)

try:
    event = {
        "event_id": str(uuid.uuid4()),
        "event_time_ms": int(time.time() * 1000),
        "service": "orders-api",
        "level": "INFO",
        "message": "order accepted",
        "schema_version": 1,
    }
    future = producer.send("app-events", key=event["service"], value=event)
    metadata = future.get(timeout=30)
    print(f"acknowledged topic={metadata.topic} partition={metadata.partition} offset={metadata.offset}")
finally:
    producer.flush(timeout=30)
    producer.close(timeout=30)
```

A producer acknowledgement confirms the broker accepted the record according to the configured acknowledgement semantics; it does not prove that every downstream consumer processed it or that the event is exactly-once end to end. A service key preserves partition order for that key but may hotspot if one key dominates. Choose the key according to ordering and distribution requirements.

### 11.3 Migration sequence

1. Document the Flume source, channel, sink, buffering, event headers, and destination layout.
2. Deploy Kafka topics, ACLs, retention, monitoring, and a test producer/consumer.
3. Forward a sample stream in parallel where possible; assign event IDs and compare counts, lateness, ordering, and duplicates.
4. Build Kafka Connect or a consumer to land events in the target. Test sink retries and offset commits against partial failures.
5. Validate malformed-record handling, schema evolution, replay, and back-pressure.
6. Switch consumers or producers using a controlled cutover; retain rollback until parity and freshness SLOs pass.
7. Remove Flume only after no downstream dependencies or rollback needs remain.

Kafka Connect is a connector runtime, not a guarantee that a suitable connector exists or supports all source/destination semantics. Fluent Bit can be a log forwarder, but it is not a universal replacement for a Flume agent topology.

## 12. Rewrite, wrap, freeze, or retire

| Decision | Choose when | Guardrails |
|---|---|---|
| **Rewrite** | Business value remains, requirements are changing, and a modern target clearly improves maintainability or reliability | Capture behavior first; write parity tests; use staged rollout and rollback. |
| **Wrap** | The job works and replacement risk is high, but it needs standardized scheduling, monitoring, or interfaces | Keep the wrapper thin; define exit codes, timeouts, idempotent reruns, secrets, and ownership. |
| **Freeze** | The workload is stable, changes are rare, and a near-term rewrite has poor risk-adjusted value | Pin dependencies, restrict access, monitor it, document recovery, and set an end-of-life review date. |
| **Retire** | No consumers/business owner remain, output is unused, or functionality is superseded | Prove no downstream reads; preserve required retention/audit data; obtain owner approval; retain rollback evidence. |

Use impact, change frequency, failure rate, supportability, security exposure, data criticality, dependency complexity, and cost to make the decision. “Old” alone is not a sufficient reason to rewrite; “it still runs” is not a sufficient reason to keep it forever.

## 13. Production migration risks and controls

- **Hidden file dependencies:** downstream jobs may watch a path or `_SUCCESS` marker instead of using an explicit scheduler dependency. Inventory and test those contracts.
- **Schedule drift:** cron timezone, DST, Oozie coordinator frequency, and Airflow data intervals may differ. Compare actual run timestamps and logical dates.
- **Incremental-state loss:** capture the last successful watermark, source timezone, precision, and update semantics before changing extraction code.
- **Duplicates on retry:** use idempotent merges, deterministic run paths, event IDs, and reconciliation.
- **Late updates/deletes:** overlap windows help with late commits but cannot guarantee capture of physical deletes; CDC or reconciliation may be needed.
- **Source overload:** parallel JDBC tasks can overwhelm the OLTP database. Bound concurrency and monitor query plans/locks.
- **Schema drift:** define type mapping, nullable fields, added/removed columns, malformed data handling, and target evolution.
- **Delivery semantics:** do not equate Flume file channels, Kafka producer idempotence, and consumer exactly-once processing. Document the guarantee end to end.
- **Security drift:** migrate service identities, least-privilege grants, secret rotation, network policies, encryption, and audit logs.
- **Small-file explosion:** preserve appropriate rolling/compaction behavior when changing Flume/HDFS sinks to object storage/lakehouse targets.
- **Unowned pipelines:** assign a business owner, technical owner, on-call path, SLA, and rollback approver before cutover.
- **Unproven success:** do not claim parity based only on successful task status. Compare data and business outputs.

## 14. Hands-on exercises

Use a disposable lab, synthetic data, and non-production credentials. Record the commands, versions, assumptions, and evidence. Do not report benchmark results unless you measured them.

### Lab 1 — Sqoop-style import with parallel splits

**Option A: legacy Sqoop, only if a compatible lab exists**

1. Create a small relational `orders` table with a numeric key and representative skew.
2. Run a full import into a new HDFS run directory with `--num-mappers 2` or `4` and `--split-by order_id`.
3. Inspect mapper logs, generated predicates, row counts, and source load.
4. Repeat with a skewed split column; compare task completion times and explain the cause without claiming general performance conclusions.
5. Run an incremental `append` or `lastmodified` import with an explicit saved watermark; test a retry and an update to an existing row.

**Option B: emulate with Spark JDBC**

1. Use Spark JDBC's `partitionColumn`, `lowerBound`, `upperBound`, and `numPartitions` options only with a suitable numeric/date partition column and valid bounds.
2. Compare with a single JDBC read and inspect the source database query load.
3. Remember that Spark JDBC bounds define partition stride, not necessarily a filtering clause that limits all returned rows; add an explicit SQL predicate for the intended extraction window.
4. Write to a run-specific staging path, reconcile counts, deduplicate, and design the idempotent target merge and watermark commit.

**Deliverable:** command/config, version information, split-column rationale, row-count reconciliation, retry test, and a short note on source-load risk.

### Lab 2 — Translate Oozie workflow and coordinator to Airflow

1. Start from a sample workflow with import → transform → publish and explicit success/error transitions.
2. Capture coordinator frequency, timezone, start/end, input availability, late-data behavior, and catch-up policy.
3. Implement an Airflow DAG with the same dependency order, run-date parameters, bounded retries, failure notification, and explicit output paths.
4. Test normal execution, upstream failure, retry, late input, manual rerun, and backfill behavior. If no real cluster is available, use stub tasks and label the test as a control-flow simulation.
5. Compare outputs and logical data intervals. Do not assume Airflow `catchup` defaults reproduce Oozie coordinator behavior.

**Deliverable:** old-to-new mapping table, DAG source, parity checklist, unresolved behavior gaps, and rollback plan.

### Lab 3 — Replace Flume-style log pipeline with Kafka

1. Document the source, channel type/capacity, sink, rolling settings, event headers, and failure behavior of a sample Flume config.
2. Create a Kafka topic in a local or managed training environment and publish synthetic structured log events.
3. Choose a partition key and explain ordering versus distribution trade-offs.
4. Consume events into a file or test destination; test consumer restart, replay, duplicate event IDs, malformed JSON, and Kafka unavailability where safe.
5. Compare the new pipeline's behavior to the Flume contract, including buffering, retention, alerting, and downstream layout.

**Deliverable:** config/code, event schema, delivery guarantee statement, monitoring checklist, and migration risks. Do not claim exactly-once unless the end-to-end design and tests establish it.

### Lab 4 — Legacy job inventory

Build an inventory for a representative cluster with at least:

- one Sqoop import/export;
- one Flume agent flow;
- one Oozie workflow and its coordinator/bundle context;
- downstream Hive/HDFS/HBase or database consumers.

Populate the schema in Section 9. Use observed values where available; mark unknowns explicitly and assign a discovery owner. Add a dependency graph and select rewrite/wrap/freeze/retire for each job with a rationale. Identify at least three high-risk unknowns and propose validation tasks.

**Deliverable:** inventory CSV or spreadsheet, dependency diagram, modernization mapping, and prioritized migration wave proposal.

## 15. Common mistakes

- Treating Sqoop, Flume, and Oozie as interchangeable tools.
- Assuming Sqoop incremental mode handles deletes or every update correctly.
- Advancing a watermark before target data is committed.
- Assuming `--split-by` guarantees even work distribution or no source impact.
- Running too many JDBC mappers against an OLTP database.
- Treating `exec` + `tail -F` as a reliable, lossless production log source.
- Assuming a Flume file channel guarantees end-to-end exactly-once delivery.
- Assuming Kafka Connect or Fluent Bit reproduces every Flume feature without redesign.
- Translating Oozie XML to Airflow task order while ignoring coordinator data availability, catch-up, timezone, bundle controls, and rerun semantics.
- Treating a task success status as proof that output is correct.
- Leaving passwords in commands, configs, notebooks, or Git.
- Rewriting before inventorying file markers, hidden dependencies, and manual operator steps.
- Inventing runtime/volume numbers rather than marking them unknown.

## 16. Interview questions with model answers

### Q1. What is the difference between Sqoop, Flume, and Oozie?

Sqoop bulk-transfers structured data between relational systems and Hadoop; Flume collects and transports event/log streams through sources, channels, and sinks; Oozie orchestrates actions and schedules workflows. Their responsibilities are distinct.

### Q2. What does `--split-by` do in Sqoop?

It selects a column used to divide a parallel import into ranges. A good column has suitable type, stable values, useful indexing, and a reasonably balanced distribution. It does not guarantee balanced mapper work or protect the source database from excessive concurrency.

### Q3. When is Sqoop `append` appropriate?

For insert-only data with a reliable monotonically increasing key. It does not detect updates to existing rows unless those updates create new records in the selected model. Deletes require another mechanism.

### Q4. Why is `lastmodified` not automatically safe for incremental loads?

The watermark can be advanced too early, timestamps may be unreliable or tied, late transactions may commit with old timestamps, retries can duplicate rows, and physical deletes are not returned by an updated-at predicate. Durable state, overlap/replay, deduplication, idempotent target writes, and reconciliation are required.

### Q5. What do Flume sources, channels, and sinks do?

Sources accept events, channels buffer them, and sinks deliver them to destinations. Reliability depends on each component's acknowledgement, transaction, buffering, retry, and failure semantics.

### Q6. Does a Flume file channel guarantee exactly-once delivery?

No. A file channel can persist buffered events across some failures, but end-to-end exactly-once behavior depends on source acknowledgement, sink semantics, retries, and destination idempotency/deduplication.

### Q7. What is the difference between Oozie workflow, coordinator, and bundle?

A workflow defines action/control flow; a coordinator schedules workflow instances based on time and/or data availability; a bundle groups coordinators for operational management. A bundle does not inherently define dependencies between its coordinators.

### Q8. Why can an Airflow DAG that has the same task order still behave differently from Oozie?

Schedule intervals, timezone, data availability, late-data behavior, catch-up, concurrency, retries, kill/alert behavior, parameter expressions, and output cleanup may differ. Each must be mapped and tested explicitly.

### Q9. What makes a retry safe?

Deterministic input windows, idempotent writes/upserts or atomic replacement, stable deduplication keys, run-specific staging, and watermark advancement only after successful target commit. External side effects must also be idempotent or explicitly compensated.

### Q10. When should a legacy job be wrapped rather than rewritten?

When it still meets requirements and rewrite risk/cost outweighs near-term benefit, but operations need standard scheduling, observability, or interfaces. The wrapper must define timeouts, exit codes, secrets, rerun safety, and ownership; it should not hide failures.

### Q11. What should be validated before retiring Flume?

No remaining consumers, equivalent event identity/order/retention and malformed-event handling, source buffering and back-pressure, monitoring, access control, downstream output layout, replay behavior, and a tested rollback/cutover plan.

### Q12. What is the first deliverable in a Hadoop migration?

A credible inventory and dependency map including data assets, jobs, schedules, owners, SLAs, security, outputs, hidden file contracts, and validation/rollback requirements. Without this, a rewrite can silently change behavior.

## 17. Final self-assessment checklist

### Concepts and legacy analysis
- [ ] Explain why Sqoop, Flume, and Oozie existed and why their roles differ.
- [ ] Read a Sqoop command and explain connection, table/query, output, mapper, split, and credential settings.
- [ ] Explain append vs lastmodified, watermark boundaries, deletes, duplicates, and retry safety.
- [ ] Read a Flume config and trace source → channel → sink, including buffering and failure semantics.
- [ ] Read Oozie workflow XML and identify actions, success/error transitions, kill behavior, coordinator schedule/data dependencies, and bundle membership.

### Modernization
- [ ] Choose between Spark JDBC, dlt/Airbyte/managed connectors based on required semantics.
- [ ] Explain Kafka topic/partition/retention/consumer offsets and how they differ from Flume channels.
- [ ] Translate Oozie dependencies and schedules into Airflow or Dagster without assuming semantic equivalence.
- [ ] Build a job inventory with owner, SLA, source/target, dependencies, state, security, monitoring, and rollback.
- [ ] Decide rewrite/wrap/freeze/retire with evidence and explicit risk.

### Migration proof
- [ ] Reconcile counts, keys, schema, checksums, and business outputs.
- [ ] Test failure, retry, replay, late data, and duplicate behavior.
- [ ] Validate timezone, catch-up, concurrency, and data-ready conditions.
- [ ] Document service identity, secrets, network path, retention, and audit requirements.
- [ ] Produce a cutover plan with acceptance criteria, rollback triggers, owner, and decommissioning criteria.

## 18. References and version discipline

Prefer the documentation matching the exact installed version/distribution. Legacy Hadoop stacks may combine old Oozie schemas, Sqoop builds, JDBC drivers, Java versions, and vendor patches; do not assume a current example works unchanged on an older cluster.

- Apache Sqoop user guide: https://sqoop.apache.org/docs/1.4.7/SqoopUserGuide.html
- Apache Sqoop import command reference: https://sqoop.apache.org/docs/1.4.7/SqoopUserGuide.html#_purpose
- Apache Flume User Guide: https://flume.apache.org/FlumeUserGuide
- Apache Oozie documentation: https://oozie.apache.org/docs/5.2.0/
- Apache Oozie Bundle specification: https://oozie.apache.org/docs/5.2.0/BundleFunctionalSpec.html
- Apache Airflow documentation: https://airflow.apache.org/docs/
- Apache Kafka documentation: https://kafka.apache.org/documentation/
- Fluent Bit documentation: https://docs.fluentbit.io/
- Spark JDBC data source: https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html

**Version and evidence note:** Sqoop, Flume, and Oozie examples in this lesson are historical patterns with stated caveats, not assertions that a particular cluster was tested. Connector availability, supported JDKs, action XML schemas, and configuration properties must be verified against the actual distribution. No benchmarks or successful lab executions are claimed.
