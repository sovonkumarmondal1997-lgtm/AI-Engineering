# Migrating Hadoop Workloads to a Cloud Lakehouse

> **Stage 2C — Data Engineering_3 · Module 2C.2 · Topic 07 · Advanced**  
> **Purpose:** Plan, execute, validate, cut over, and safely complete a Hadoop-to-cloud-lakehouse migration.  
> **Position in the roadmap:** The capstone lesson after HDFS, YARN, MapReduce, Hive, HBase, and Sqoop/Flume/Oozie.

## 1. Learning outcomes

By completing this lesson, you should be able to:

- Explain the business and technical reasons for modernizing a legacy Hadoop platform without assuming cloud is automatically cheaper or faster.
- Distinguish storage migration, compute migration, table-format/catalog migration, orchestration migration, and full platform modernization.
- Build a source-to-target component map for HDFS, YARN, MapReduce, Hive, HBase, Sqoop, Flume, and Oozie.
- Inventory datasets, tables, jobs, dependencies, owners, SLAs, security controls, and operating costs before choosing a target.
- Choose between lift-and-shift, replatforming, refactoring, wave-based migration, and the strangler pattern.
- Estimate bulk-transfer time, plan incremental synchronization, and validate transferred data.
- Convert or rewrite Hive tables deliberately, including partition redesign and metadata ownership.
- Migrate HiveQL, MapReduce, UDFs, Oozie workflows, ingestion, and HBase workloads based on workload semantics.
- Design reconciliation that detects missing, duplicated, changed, and semantically inconsistent records.
- Run old and new paths in parallel, establish objective cutover gates, and execute rollback safely.
- Move identity, authorization, governance, lineage, observability, and support ownership—not only data files.
- Build a four-wave migration plan for a representative 500 TB platform with 300 Hive tables, 120 Oozie workflows, and two HBase tables.

## 2. Prerequisites and roadmap dependencies

This lesson assumes that you have completed the six preceding lessons in this module. The table below describes how each prior lesson is used during migration planning.

| Preceding lesson | Knowledge reused in this lesson | Migration implication |
|---|---|---|
| 01 — HDFS architecture, NameNode, DataNodes, replication | Namespace, blocks, replication, rack awareness, snapshots, small-file effects, file permissions | Inventory paths and file counts; distinguish logical data volume from replicated physical storage; plan source consistency and transfer load. |
| 02 — YARN resource management | ResourceManager, NodeManagers, containers, queues, application scheduling | Measure contention and job resource profiles; map queue/SLA needs to target compute limits, concurrency, and isolation. |
| 03 — MapReduce and why Spark replaced it | Map/shuffle/reduce, partitioning, sort, combiners, retry behavior | Identify algorithmic behavior and shuffle cost; rewrite jobs only after proving output equivalence. |
| 04 — Hive Metastore and HiveQL | Managed/external tables, SerDes, partitions, file formats, metastore metadata, SQL semantics | Inventory table metadata and ownership; separate catalog migration from physical data conversion; test SQL semantics. |
| 05 — HBase and wide-column storage | Row keys, column families, regions, read/write paths, consistency and access patterns | Treat HBase as an online serving workload, not just a folder of HFiles; select targets from latency and access requirements. |
| 06 — Sqoop, Flume, and Oozie | Batch imports/exports, event ingestion, workflow dependencies, watermarks, retries | Preserve ingestion checkpoints and delivery semantics; migrate orchestration as dependency graphs, not as a one-to-one syntax translation. |

**Authoritative scope:** `roadmap-Hadoop-Ecosystem-and-Legacy-Big-Data.md`, Topic 07, specifies this lesson's concepts, the illustrative 500 TB / 300 Hive table / 120 Oozie workflow / two HBase table scale, the five hands-on exercises, and the checkpoint. `Roadmap_ptree.md` places this file at `Stage 2C — Data Engineering_3/02-Hadoop-Ecosystem-and-Legacy-Big-Data/07-migrating-hadoop-workloads-to-cloud-lakehouse.md`.

**Tooling assumption for the lab:** The roadmap describes a small Docker-based Hadoop environment, Python 3.12+ in a `uv` project, and MinIO as a local S3-compatible target. The exact Docker image versions and connector combinations are environment-specific and must be pinned and verified before execution.

## 3. Migration fundamentals

### 3.1 Why organizations migrate

Common drivers include:

- **Support and lifecycle risk:** the distribution or component may be out of support, difficult to patch, or dependent on scarce operational expertise.
- **Elasticity:** on-premises clusters are sized for peaks and may sit underused; cloud compute can be provisioned and stopped, but only if workload schedules and operational controls support it.
- **Storage/compute separation:** durable object storage can be shared by independent compute engines. This changes scaling and lifecycle choices; it does not eliminate storage request costs, small-file overhead, or catalog requirements.
- **Operating-model change:** managed services may reduce undifferentiated cluster operations but introduce service limits, platform-specific controls, vendor dependencies, and new skills requirements.
- **Reliability and recovery:** modern storage, managed control planes, multi-zone designs, and better deployment practices may improve recovery objectives when explicitly engineered.
- **Analytics and AI enablement:** a governed lakehouse may make historical data easier to share with SQL, Spark, BI, and ML workloads.
- **Security and governance:** the target may provide stronger identity integration, centralized policy, audit, and lineage—but only after controls are designed and validated.

Migration is not inherently a cost-saving or performance-improving operation. Poorly sized always-on compute, repeated object listing, cross-region reads, egress, high request rates, inefficient SQL, and duplicated data can make the new platform more expensive.

### 3.2 Five distinct migration dimensions

| Dimension | What changes | What may stay the same | Main risks |
|---|---|---|---|
| **Storage migration** | HDFS files move to object storage such as S3, ADLS Gen2, or GCS | File format, schema, and jobs may initially remain unchanged | Incomplete copies, path/permission assumptions, small files, transfer window overruns |
| **Compute migration** | YARN-managed execution moves to managed Spark, serverless processing, Kubernetes, or another engine | Data and SQL may initially remain the same | Different Spark/Hadoop versions, resource behavior, shuffle/network differences, unsupported libraries |
| **Table-format/catalog migration** | Hive-style table metadata becomes Iceberg or Delta metadata with an appropriate catalog | Data files may sometimes be reused | Incompatible schema/partition assumptions, shared-file lifecycle hazards, unsupported feature combinations |
| **Orchestration/ingestion migration** | Oozie, Sqoop, and Flume functions move to Airflow/Dagster/managed workflows and modern ingestion services | Business transformations may initially stay the same | Lost dependency ordering, watermark gaps, duplicate delivery, retries that are not idempotent |
| **Full platform modernization** | Storage, compute, table format, governance, pipelines, and operating model are redesigned together | Business contracts and outcomes should remain stable | Broad scope, organizational complexity, long parallel run, hard-to-isolate regressions |

A project may combine these dimensions, but its plan should track them separately. “The files copied” is not proof that a workload has migrated.

### 3.3 Define objectives and constraints before selecting technology

Document measurable objectives such as:

- Required cutover date and end-of-support deadline.
- Data freshness, batch completion time, interactive query latency, and availability SLOs.
- Recovery time objective (RTO), recovery point objective (RPO), and permitted downtime.
- Data retention, deletion, residency, encryption, and audit obligations.
- Maximum migration-period and steady-state budget.
- Required query engines, BI clients, ML consumers, and external data sharing.
- Operational constraints: region, network connectivity, procurement, platform standards, skills, and vendor agreements.
- Source freeze options, write ownership, and ability to replay or reconstruct data.

**Success criteria must be testable.** Example: “All tier-1 tables reconcile at the approved business grain; all tier-1 pipelines meet their agreed freshness SLO for seven consecutive simulated or observed days; all access-control tests pass; rollback is rehearsed; and the accountable data owner signs off.” Avoid vague acceptance criteria such as “data looks right.”

### 3.4 Migration invariants

Treat these as non-negotiable unless the business owner explicitly approves a changed contract:

1. **Meaning:** business definitions, time zones, null semantics, deduplication rules, and late-arrival handling remain equivalent.
2. **Completeness:** every in-scope source record is accounted for, including deletes and corrections where applicable.
3. **Uniqueness:** keys and duplicate-handling behavior remain correct.
4. **Security:** no user gains broader access during migration; restricted data stays restricted.
5. **Recoverability:** source data, checkpoints, and rollback procedures remain available until exit gates pass.
6. **Ownership:** every target dataset, job, alert, and policy has a named accountable owner.
7. **Evidence:** validation results, exceptions, approvals, and cutover events are retained for audit.

## 4. Source-to-target component mapping

No component maps perfectly to one product. Select a target from requirements, not from name similarity alone.

| Hadoop source | Common target choices | Selection questions and migration notes |
|---|---|---|
| **HDFS** | Amazon S3; Azure Data Lake Storage Gen2; Google Cloud Storage; local S3-compatible object store for labs | Compare throughput, request cost, object count, lifecycle, consistency semantics, access control, region, network, and client compatibility. Object stores are not POSIX filesystems; rename/list semantics differ. |
| **YARN** | Managed Spark/Hadoop services (for example, EMR or Dataproc); serverless Spark; Kubernetes-based Spark; other managed processing services | Match executor sizing, autoscaling, queue isolation, scheduling, libraries, network and shuffle needs. Kubernetes is an execution platform, not an automatic equivalent for every YARN queue or scheduler policy. |
| **MapReduce** | Spark (batch/distributed transformations); Beam/Dataflow or another engine for appropriate stream/batch patterns; SQL engine where work is relational | Reconstruct algorithm, ordering, side effects, partitioner, retry behavior, counters, and output contract. Do not translate code mechanically. |
| **Hive tables + Hive Metastore** | Iceberg or Delta Lake tables plus a compatible catalog; cloud catalog or Unity Catalog depending on platform | Separate physical file movement, table metadata registration, table-format conversion, and catalog migration. Check readers/writers and catalog compatibility. |
| **HiveQL** | Spark SQL; dbt models on a compatible SQL engine; managed warehouse SQL where appropriate | Validate dialect differences, UDFs, timestamps, decimal precision, null handling, implicit casts, ordering, and window functions. dbt is a transformation/development framework, not a distributed execution engine by itself. |
| **HBase** | Google Cloud Bigtable; Amazon DynamoDB; Cassandra; another wide-column/key-value serving database; sometimes a relational or search store | Compare row-key access patterns, p99 latency, throughput, conditional mutations, scan patterns, TTL, cell versions, consistency, secondary indexes, and cost. There is no universal HBase replacement. |
| **Oozie** | Apache Airflow; Dagster; managed workflow/orchestration services; cloud-native state machines for suitable patterns | Rebuild dependency graph, scheduling/time zone, retries, sensors, parameters, failure paths, SLA alerts, and backfill behavior. A syntax conversion is insufficient. |
| **Sqoop** | Managed database connectors; Spark JDBC; CDC tools; managed replication/ingestion services | Preserve snapshot boundaries, watermarks, deletes, transaction isolation, schema evolution, retry safety, and source database load. |
| **Flume** | Kafka/Kafka Connect; managed streaming ingestion; Fluent Bit/Vector or application-native telemetry pipelines, depending on event type | Match buffering, delivery guarantees, backpressure, ordering, replay, schema registry, and dead-letter behavior. A log shipper is not automatically a durable event bus. |
| **Ranger policies** | Cloud IAM plus service-specific authorization; AWS Lake Formation; Unity Catalog; equivalent governance control plane | Recreate table/column/row policies, tag-based access, admin boundaries, audit and break-glass workflows. Cloud IAM alone may not implement table-level semantics. |
| **Kerberos** | Cloud workload identity, managed identities, IAM roles/service accounts, federated identity, short-lived credentials | Replace principals, service-to-service authentication, delegation, keytabs, and trust boundaries. Never replace Kerberos with long-lived static access keys as a default. |
| **Hadoop logs/metrics/lineage** | Cloud monitoring/logging, OpenTelemetry where supported, lineage/catalog tooling, SIEM integration | Preserve alert coverage, correlation IDs, retention, incident runbooks, lineage continuity, and access to audit history. |

### 4.1 Choose an architecture, not a list of products

A common target pattern is:

```text
Source databases / event producers / retained HDFS
                │
       bulk copy + CDC/incremental ingestion
                │
                ▼
   Cloud object storage: raw / landing zone
                │
      validation + schema enforcement
                │
                ▼
    Lakehouse tables: Iceberg or Delta
                │
    catalog + governance + lineage
                │
       ┌────────┼───────────┐
       ▼        ▼           ▼
    Spark     SQL/BI       ML/AI
       │        │           │
       └──── observability ─┘
                │
   orchestration, CI/CD, IAM, audit, cost controls
```

This diagram is conceptual, not a claim that every platform supports every engine or catalog combination. Validate interoperability, catalog semantics, and supported write paths for the exact versions and managed-service configuration.

### 4.2 Storage and compute separation

Object storage typically provides durable, independently scalable storage; compute clusters or serverless jobs read and write objects. This enables independent scaling and transient compute, but brings different performance characteristics from HDFS:

- Rename may be implemented as copy/delete rather than an atomic metadata operation.
- Directory listing is often a paginated object-list operation and can be expensive for millions of small objects.
- There is no HDFS block placement or data locality in the same sense; performance depends on object layout, request patterns, network, and engine behavior.
- Many small files can increase listing, planning, scheduling, and request overhead. Compaction and target file sizing should be planned.
- Access permissions and encryption are enforced through cloud identities, bucket/container policies, catalog policies, and service controls rather than inherited POSIX assumptions alone.
- Cross-region reads, cross-account access, and internet egress may introduce cost or compliance constraints.

## 5. Discovery and inventory

**Inventory before copy.** Moving data first and discovering job dependencies later often creates duplicated effort, missed tables, incorrect cutover order, and unexpected consumers.

### 5.1 Dataset and table inventory schema

Maintain a versioned CSV, database table, or inventory service with at least these fields:

| Field | Meaning |
|---|---|
| `dataset_id`, `database`, `table_name` | Stable identity; do not rely on display name alone |
| `source_location`, `storage_owner` | HDFS path, HBase namespace/table, or upstream system; accountable owner |
| `logical_size_bytes`, `physical_size_bytes`, `file_count` | Distinguish table data size from HDFS replication overhead and filesystem metadata |
| `file_format`, `compression`, `schema_fingerprint` | Parquet/ORC/Avro/text, codec, and versioned schema representation |
| `partition_columns`, `partition_count`, `bucket_columns` | Physical layout and pruning/scan behavior |
| `row_count`, `null_profile`, `key_profile` | Measured data-quality profile, with measurement timestamp and method |
| `last_access_at`, `last_modified_at` | Populate only if a reliable source exists; otherwise mark unavailable rather than infer |
| `readers`, `writers`, `downstream_consumers` | Jobs, BI, users, exports, APIs, ML pipelines |
| `access_pattern`, `freshness_slo`, `availability_slo` | Full scan, point lookup, incremental, interactive, batch, etc. |
| `retention`, `deletion_policy`, `sensitivity`, `residency` | Legal and governance constraints |
| `owner`, `steward`, `criticality`, `migration_wave` | Decision ownership and planned sequencing |
| `migration_strategy`, `validation_plan`, `exception_status` | In-place metadata, rewrite, retain, retire, or special handling |
| `evidence_uri`, `measured_at`, `confidence` | Auditability of collected facts |

**Metadata discipline:** “Not available” is not the same as “zero.” The Hive Metastore may not record last query time. HDFS file modification time is not last access. Query logs, audit events, scheduler history, or table-format metrics may provide evidence, but their coverage and retention must be checked. Mark each value as `collected`, `derived`, `estimated`, or `unavailable`.

### 5.2 Job and workflow inventory schema

Track one record per job/action and one record per dependency edge.

| Field | Example or purpose |
|---|---|
| `job_id`, `workflow_id`, `job_type`, `entrypoint` | Oozie workflow/action, HiveQL, MapReduce JAR, Spark application, Sqoop import, Flume agent |
| `schedule`, `timezone`, `trigger`, `backfill_policy` | Preserve calendar semantics and historical reruns |
| `upstream_dependencies`, `downstream_dependencies` | Explicit DAG edges, not only a free-text description |
| `source_datasets`, `target_datasets`, `write_mode` | Inputs/outputs and append/overwrite/merge behavior |
| `runtime_p50`, `runtime_p95`, `runtime_max`, `resource_profile` | CPU, memory, shuffle, I/O, concurrency, peak behavior |
| `owner`, `support_team`, `pager`, `business_contact` | Operational accountability |
| `SLA`, `freshness`, `RTO`, `RPO`, `criticality` | Service contract |
| `failure_modes`, `retry_policy`, `idempotency_key`, `checkpoint` | Failure and recovery behavior |
| `code_location`, `libraries`, `JDK/Python/Spark/Hadoop versions` | Dependency and compatibility risk |
| `identity`, `secrets`, `permissions`, `network_dependencies` | Runtime access and security boundary |
| `business_rule_tests`, `source_of_truth`, `cutover_method` | Acceptance and ownership |

For Oozie, inventory workflow, coordinator, bundle, actions, parameters, time zone, frequency, dependency conditions, kill/error transitions, retries, and external sensors. For Sqoop, capture source database, isolation/snapshot behavior, split column, import mode, watermark storage, deletes, and target write semantics. For Flume, capture sources, channels, sinks, capacity, backpressure, and delivery/replay behavior. For HBase, capture row-key design, families, TTL, versions, expected read/write QPS, p95/p99 latency, scan patterns, and consistency requirements.

### 5.3 Dependency graph and critical path

Represent the platform as a directed graph:

- **Nodes:** datasets, jobs, workflows, services, users/consumers, security policies.
- **Edges:** reads, writes, triggers, publishes, authorizes, and serves.
- **Edge attributes:** schedule, expected freshness, data volume, owner, failure impact.

A cycle may indicate a real iterative process or a poorly documented dependency. Resolve it before migration. Calculate the critical path for each business deliverable using observed runtimes and wait times, not only nominal job durations. Prioritize by combined business criticality, dependency fan-out, technical risk, and migration effort—not table size alone.

### 5.4 Worked fictional discovery example

The following is an **illustrative inventory**, not measured production evidence.

| Asset | Measured/known facts in the scenario | Unknowns to resolve | Initial decision |
|---|---|---|---|
| `sales.orders_daily` | 18 TB, Parquet, partitioned by `order_date`, batch append with corrections for prior 3 days, BI + finance consumers | Whether all writers honor the late-correction window; actual last query time not yet verified | Pilot candidate after write-path and correction-window tests |
| `clickstream.events` | 140 TB, ORC, date/hour partitions, very high file count, several Spark and Hive readers | Exact active-reader list; late event distribution; cost of object listing | Repartition/compact during rewrite; do not copy blindly as-is |
| `risk.customer_features` | 2 TB, daily batch, sensitive fields, used by ML scoring and regulated reporting | Policy equivalence, training-serving freshness, historical lineage | High governance priority; migration only after policy and consumer contract approval |
| `hbase.customer_profile` | Online point lookups by customer ID; low-latency serving dependency | QPS, p99, mutation conditions, TTL, secondary lookup requirements | Separate serving-database workstream; not a file-copy task |
| `workflow.finance_close` | Oozie coordinator with upstream data checks and downstream reconciliation; hard monthly deadline | Time-zone edge cases, rerun and partial-failure behavior | Critical-path workflow; migrate after dependency and backfill tests |

Before assigning waves, replace all scenario assumptions with collected evidence and obtain owner sign-off. The initial inventory is a hypothesis to validate, not an approved migration plan.

## 6. Target architecture and migration strategy

### 6.1 Select compute based on workload behavior

| Option | Strong fit | Trade-offs to evaluate |
|---|---|---|
| Managed Spark/Hadoop service | Existing Hadoop/Spark code with limited first-stage changes; control over runtime and configuration | Cluster lifecycle, version upgrades, idle cost, operational responsibilities, service-specific constraints |
| Serverless Spark or managed batch | Intermittent jobs, reduced cluster operations, elastic batch workloads | Startup latency, quotas, supported dependencies, networking, runtime customization, per-job cost model |
| Kubernetes-based Spark | Organization already operates Kubernetes well; needs custom scheduling or workload portability | Requires cluster/network/storage expertise; scheduler and autoscaling behavior differ from YARN; avoid treating Kubernetes as “no operations” |
| SQL warehouse/query engine | Relational transformations and interactive analytics fit the engine's semantics and cost model | SQL dialect differences, concurrency/slot/warehouse limits, data movement, UDF support, vendor lock-in |
| Stream/batch processing service | Event-time windows, streaming ingestion, replay, or Beam-style pipelines | Delivery guarantees, state compatibility, watermark semantics, operational model, sink support |

Benchmark representative workloads in the target environment. Do not extrapolate from a tiny development sample to 500 TB without accounting for file counts, skew, concurrency, network, catalog calls, and cold-start behavior.

### 6.2 Choose Iceberg or Delta Lake deliberately

Both are table formats that add transactional metadata and table-level behavior over data files. They are not simply file codecs and are not interchangeable in every deployment.

Evaluate:

- Supported Spark/engine versions and runtime distribution.
- Catalog implementation, locking/commit behavior, permissions, and cross-engine access.
- Required features: schema evolution, partition evolution, deletes/updates/merges, time travel, streaming writes, compaction, and snapshot retention.
- Writer concurrency and supported write modes.
- Governance and lineage integration.
- Operational capabilities for metadata cleanup, orphan-file handling, compaction, and recovery.
- Interoperability requirements and whether the selected catalog supports all intended engines.

**Compatibility gate:** record exact versions of Hadoop, Spark, Scala binary version, JDK, Iceberg or Delta, catalog client, cloud storage connector, Hive integration, and any runtime-specific extensions. Consult the compatibility matrix and release documentation for the selected versions. A package that compiles is not proof that every reader/writer and catalog operation is supported.

### 6.3 Lift-and-shift, replatform, refactor, retire

| Strategy | Description | When useful | Main limitation |
|---|---|---|---|
| **Lift-and-shift** | Move a workload with minimal code and behavior changes, often onto a managed cluster | Deadline-driven exit from hardware or unsupported infrastructure | Preserves technical debt and may preserve poor performance/cost |
| **Replatform** | Keep the workload's core logic but change runtime, storage, orchestration, or catalog | Good first step when existing Spark/Hive logic is mostly portable | Still requires connector, security, SQL and operational adaptation |
| **Refactor** | Redesign data layout, SQL, pipelines, serving model, or architecture | High-value workloads where legacy design is a bottleneck or cannot meet target needs | Higher effort and more semantic regression risk |
| **Retain/retire** | Keep a justified system temporarily, archive it read-only, or eliminate unused assets | Unmigratable dependency, legal retention, or no active consumer | Must have explicit owner, exit date, risk acceptance, and evidence |

“Lift-and-shift first, optimize later” is a strategy, not a universal rule. It is unsafe when the legacy runtime cannot run securely or reliably in the target, or when the new platform cannot preserve required semantics.

### 6.4 Wave-based migration versus big bang

**Wave-based migration** limits the blast radius, learns from pilots, and allows rollback by workload group. It requires temporary dual operations, careful dependency boundaries, and a clear source-of-truth rule.

**Big-bang migration** can shorten the period of dual running but concentrates risk, requires a coordinated freeze, and makes root-cause isolation harder. Use it only when dependencies are tightly coupled, a short downtime is acceptable, the cutover is rehearsed, and rollback is feasible.

For the representative platform in this lesson, use four waves. Each wave must have its own inventory baseline, validation evidence, security sign-off, cost review, runbook, and rollback decision.

### 6.5 Strangler pattern

The strangler pattern moves a bounded capability at a time while the legacy system continues to serve remaining capabilities. A routing or ownership layer decides which platform is authoritative for each table/API/job.

Rules for safe use:

1. Define the source of truth for each dataset and each time interval.
2. Do not allow uncontrolled dual writes to two independent table-format/catalog systems.
3. Use CDC, an append-only log, or controlled change capture when both systems must stay current.
4. Route consumers explicitly; do not silently point a query engine at a partially migrated path.
5. Keep rollback at the routing/ownership boundary, not by manually copying a possibly divergent target back over the source.
6. Retire each legacy capability only after all consumers and audit requirements are resolved.

## 7. Data movement and transfer planning

### 7.1 Choose a transfer method

| Method | Appropriate use | Checks and limitations |
|---|---|---|
| **DistCp** | Large HDFS-to-HDFS or HDFS-to-compatible-filesystem copy when the deployed Hadoop distribution and filesystem connector support it | Validate exact `hadoop distcp` version, filesystem connector, auth, endpoint settings, path mapping, retries, and object-store update semantics. `-update` may compare size and modification time rather than a cross-store content checksum. |
| **Spark read/write** | Copy while transforming, repartitioning, validating, or writing to a target format | Requires correct source reader, target connector, catalog, resource profile, and safe write strategy; do not use an unbounded `collect()` for large data. |
| **Network-based transfer service** | Cloud provider's managed online transfer path | Check supported source/target, agent requirements, bandwidth, throttling, encryption, and per-request or egress costs. |
| **Offline transfer appliance** | Large initial bulk load where WAN bandwidth/window is insufficient or network transfer is impractical | Consider procurement/shipping, device capacity, encryption/key handling, import throughput, staging, chain of custody, and incremental changes during transit. Examples include provider-specific Snowball/Data Box/Transfer Appliance offerings; availability and specifications vary over time. |
| **CDC / incremental replication** | Keep the target current while the source remains writable | Requires reliable log position/watermark, delete handling, schema evolution, replay, idempotency, and lag monitoring. |

Use DistCp for file transfer, not as a substitute for table-format conversion or semantic validation. A successful copy job only confirms the tool completed its defined operation.

### 7.2 Initial bulk copy and incremental synchronization

A common safe sequence is:

1. Freeze the inventory and record source table/file baselines.
2. Identify active writers and define a consistent source snapshot or a documented point-in-time boundary.
3. Copy the bulk historical dataset into a staging prefix/location.
4. Validate file inventory, byte counts, schema and sampled/full data-level checks as appropriate.
5. Start incremental capture from a known offset/watermark after the bulk snapshot boundary.
6. Reconcile changes, deletes, updates, and late-arriving records.
7. Repeat until lag is within the cutover threshold.
8. During the approved freeze window, stop or fence source writes, capture a final high-water mark, drain in-flight writes, apply final changes, validate, and switch the authoritative writer/reader.
9. Keep source data read-only until the rollback period ends.

The bulk snapshot and incremental stream must have a precisely defined boundary. If bulk copy includes data through time `T` and CDC starts after `T`, no changes may be lost between the two. If both include the same records, the target must deduplicate by stable key/version or use an idempotent merge.

**Deletes matter.** File copy and append-only watermark jobs do not automatically propagate source deletes. Use tombstones/CDC or a full reconciliation policy when the source supports updates/deletes. Late-arriving events may change earlier partitions; include a correction horizon or replay policy.

### 7.3 Transfer throughput calculations

For a first-order estimate:

\[
\text{required line rate (bits/s)} = \frac{\text{bytes to transfer} \times 8}{\text{available seconds} \times \text{effective utilization}}
\]

This assumes the stated utilization captures protocol overhead and sustained usable throughput. Real transfer time may be longer because of small files, source read limits, throttling, encryption/compression CPU, retries, checksum passes, target write limits, or concurrent production load.

**Worked calculation — illustrative assumptions:** transfer 500 TB decimal (`500 × 10^12` bytes) within 30 days (`30 × 24 × 3600 = 2,592,000` seconds), assuming 70% effective utilization.

- Data volume in bits: `500 × 10^12 × 8 = 4 × 10^15 bits`.
- Ideal sustained throughput at 100%: `4 × 10^15 / 2,592,000 ≈ 1.543 × 10^9 bits/s = 1.54 Gbit/s`.
- Required line rate at 70% utilization: `1.543 / 0.70 ≈ 2.20 Gbit/s`.
- At a nominal 1 Gbit/s line rate and 70% utilization, throughput is `87.5 MB/s` decimal. Approximate transfer time is `500,000,000 MB / 87.5 MB/s ≈ 5,714,286 s ≈ 66.1 days`.
- At 10 Gbit/s and 70% utilization, idealized transfer time is approximately `6.6 days`.

These estimates exclude verification, incremental changes, throttling, retries, and any reformatting. They are planning arithmetic, not a benchmark or a cloud-provider guarantee. Confirm whether “500 TB” means decimal TB or binary TiB and whether it represents logical bytes or replicated physical capacity. Do not multiply logical dataset size by HDFS replication factor unless the transfer plan is actually copying all replicas (normally it is not).

### 7.4 DistCp usage and caveats

A representative HDFS-to-object-store command may look like this **only if the Hadoop distribution, S3A connector, authentication, and target endpoint have been configured and tested**:

```bash
# Example shape only; replace URIs and verify your Hadoop/S3A distribution.
hadoop distcp \
  -m 32 \
  hdfs:///warehouse/sales/orders \
  s3a://migration-bucket/staging/sales/orders
```

The `-m` value is a starting point for a controlled pilot, not a universal tuning recommendation. Tune map count and concurrency from observed source throughput, file sizes, network capacity, and target request limits.

A second pass might use `-update` where supported and appropriate:

```bash
hadoop distcp -update \
  hdfs:///warehouse/sales/orders \
  s3a://migration-bucket/staging/sales/orders
```

Do not assume that `-update` detects every content change across filesystems. In particular, object-store checksum algorithms and timestamp behavior may differ. Confirm the exact deployed DistCp semantics, and use a manifest/checksum/data-level validation when the integrity requirement demands it. Do not use an object-store `-atomic` assumption as a universal guarantee: directory rename/atomicity semantics vary by filesystem and connector.

For MinIO, a compatible S3A connector may work, but version and endpoint configuration are environment-specific. If DistCp support is not available or reliable in the local stack, use the Spark workflow below. Never place credentials directly in shell history or source control.

### 7.5 Spark copy and Iceberg conversion lab pattern

First prove the Spark runtime can read the source Hive table and write to the configured Iceberg catalog. The following is a **configuration-dependent example**, not a complete drop-in `spark-submit` command; catalog, warehouse, Hadoop/S3A, Iceberg runtime, and MinIO endpoint settings must match the selected versions.

```python
# migration/copy_table_to_iceberg.py
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("orders-hive-to-iceberg").enableHiveSupport().getOrCreate()

source_table = "hive_src.orders"
target_table = "lakehouse.orders_migration"

source = spark.table(source_table)
# Prefer explicit column selection and type/schema assertions in a real migration.
(source.writeTo(target_table)
       .using("iceberg")
       .create())

# Verify the registered target and basic row count before continuing.
source_count = spark.table(source_table).count()
target_count = spark.table(target_table).count()
if source_count != target_count:
    raise RuntimeError(f"Count mismatch: source={source_count}, target={target_count}")

print({"source": source_table, "target": target_table,
       "source_rows": source_count, "target_rows": target_count})
spark.stop()
```

Important limitations:

- This example performs a **rewrite into a new table**. It is not an in-place metadata conversion.
- It assumes the target catalog is already configured to create Iceberg tables and that source/target identifiers resolve correctly.
- For a production migration, write to a staging table/location, validate schema and data, apply partitioning intentionally, and publish only after acceptance.
- For a very large table, estimate the rewrite's compute, shuffle, target file count, temporary storage, and read/write amplification before running.

## 8. Hive table conversion and partition redesign

### 8.1 Metadata conversion versus data rewrite

These are different operations.

- **Metadata/in-place conversion:** create new table-format metadata over existing compatible data files, without rewriting every row. This may reduce elapsed time and temporary storage, but the source and target may share physical files. Source cleanup, overwrite, compaction, or retention operations can break the new table if file ownership is misunderstood.
- **Rewrite/full data migration:** read source rows and write new data files in the target table format, often with new partitioning or file sizes. This uses more compute and temporary storage but creates stronger physical isolation and provides an opportunity to normalize schemas and compact small files.
- **Snapshot-style migration:** create a read/test table that references existing files for controlled comparison. A snapshot that shares files is not a durable independent copy; destructive source operations can invalidate it.

Do not equate “registered as Iceberg/Delta” with “all data rewritten” or “the old Hive table is now safely removable.”

### 8.2 Conversion approach

For each table, select one of these paths:

1. **Compatible format + low change risk + supported conversion procedure:** consider metadata conversion after validating file ownership, partition metadata, catalog support, and rollback strategy.
2. **Need a new partition layout, compaction, schema cleanup, or strong isolation:** rewrite to a new table.
3. **Unsupported format/SerDe or unclear semantics:** read through a compatible source reader and rewrite; test nulls, timestamps, decimals, complex types, and custom SerDes.
4. **Low-value or unused table:** archive, retain temporarily, or retire with owner and legal approval rather than automatically migrating it.

Apache Iceberg provides migration procedures such as snapshotting or migrating supported Hive/Spark tables in supported Spark/catalog configurations. Delta Lake has conversion mechanisms for supported Parquet tables and other supported cases. These features have version and format constraints; consult the official documentation for the deployed release and do not assume every Hive table can be converted in place.

### 8.3 Partition redesign

Legacy Hive tables often partition by multiple high-cardinality fields or create one directory per tiny batch. Object storage and modern table formats change the trade-offs, but do not remove the need for thoughtful layout.

Use observed query predicates, data volume, update patterns, and retention rules. Evaluate:

- Partition columns and granularity: date/hour, tenant, region, or other predicates.
- Cardinality and partition explosion.
- Target file size and number of files per partition.
- Pruning effectiveness versus planning/listing overhead.
- Skewed partitions and uneven data distribution.
- Late updates, partition evolution, and merge behavior.
- Whether partitioning should be managed by the table format rather than manually maintained directories.

Do not carry over partition columns just because they exist in the old directory tree. Do not partition on a high-cardinality key such as `customer_id` without strong evidence and a design review. Test representative query plans and runtime distributions before publishing a redesigned table.

## 9. Code and workflow migration

### 9.1 HiveQL to Spark SQL or dbt

Migrate query behavior, not just syntax. Review:

- `LATERAL VIEW` / `EXPLODE`, complex types, UDFs and UDAFs.
- `INSERT OVERWRITE`, dynamic partitions, table ownership, and write modes.
- Timestamp parsing, session time zone, daylight-saving transitions, and date truncation.
- Decimal precision/scale, integer overflow, implicit casts, collation and string comparison.
- Null-safe equality, `COUNT(DISTINCT ...)`, approximate aggregates, window frames, and tie-breaking.
- Sort order: a query's result order is not guaranteed without explicit `ORDER BY`.
- Nondeterministic functions and functions whose output depends on current time or locale.
- Hive SerDes, custom input formats, storage handlers, and UDF JARs.

**Example 1 — partitioned aggregation**

HiveQL:

```sql
SELECT order_date, COUNT(*) AS order_count, SUM(net_amount) AS net_sales
FROM sales.orders
WHERE order_date >= '2026-01-01'
GROUP BY order_date;
```

Spark SQL (assuming `order_date` is a `DATE` and `net_amount` has compatible decimal semantics):

```sql
SELECT order_date, COUNT(*) AS order_count, SUM(net_amount) AS net_sales
FROM lakehouse.orders
WHERE order_date >= DATE '2026-01-01'
GROUP BY order_date;
```

Compare one row per date after canonical sorting, with a defined numeric tolerance only if the business contract allows it. Decimal totals should normally match exactly when precision and rounding are equivalent.

**Example 2 — latest record per entity**

HiveQL:

```sql
SELECT customer_id, status, updated_at
FROM (
  SELECT customer_id, status, updated_at,
         ROW_NUMBER() OVER (
           PARTITION BY customer_id
           ORDER BY updated_at DESC, source_sequence DESC
         ) AS rn
  FROM customer_status
) ranked
WHERE rn = 1;
```

Spark SQL:

```sql
SELECT customer_id, status, updated_at
FROM (
  SELECT customer_id, status, updated_at,
         ROW_NUMBER() OVER (
           PARTITION BY customer_id
           ORDER BY updated_at DESC, source_sequence DESC
         ) AS rn
  FROM lakehouse.customer_status
) ranked
WHERE rn = 1;
```

The tie-breaker `source_sequence` must be stable and available. If it is absent, records with equal `updated_at` can produce nondeterministic winners in either engine.

**Example 3 — exploding an array**

HiveQL:

```sql
SELECT e.event_id, item
FROM events e
LATERAL VIEW EXPLODE(e.items) exploded AS item;
```

Spark SQL:

```sql
SELECT e.event_id, item
FROM lakehouse.events e
LATERAL VIEW EXPLODE(e.items) exploded AS item;
```

This is syntactically similar, but test empty arrays, null arrays, null elements, and row-multiplication behavior. If the desired semantics include rows for null/empty arrays, evaluate `OUTER` explode semantics explicitly.

**dbt's role:** use dbt when SQL transformations benefit from version control, modular models, tests, documentation, lineage, and controlled deployment on a compatible execution engine. It does not remove the need to validate engine-specific SQL semantics or configure distributed execution.

### 9.2 MapReduce to Spark

For each MapReduce job, document:

- InputFormat, key/value types, mapper logic, partitioner, sort/group comparator, reducer logic, combiner assumptions, counters, and output format.
- Whether output depends on key ordering, number of reducers, task side effects, or retry timing.
- Whether the job is map-only, reduce-heavy, iterative, stateful, or relational.
- Data skew, shuffle volume, compression, spill, and temporary output behavior.

A safe conversion workflow is:

1. Freeze a representative input snapshot and retain the original output.
2. Write Spark transformations with explicit schemas and stable keys.
3. Preserve custom partitioning/sorting only when required by the contract.
4. Remove non-idempotent external side effects from retryable tasks or protect them with idempotency keys/transactional sinks.
5. Compare row-level results, counters translated to equivalent metrics, business aggregates, and performance under representative scale.
6. Load-test concurrency and failure recovery; task retries and speculative execution can expose unsafe side effects.

A combiner is valid only when its algebraic behavior is compatible with the reducer. A Spark aggregation rewrite must preserve the same mathematical result, not just the same broad operation name.

### 9.3 UDFs and dependency changes

Inventory JARs, Python packages, native libraries, custom SerDes, timezone databases, JDBC drivers, compression codecs, and environment variables. Pin dependency versions and test on the target runtime. Prefer built-in SQL/Spark functions when they preserve semantics and perform better, but validate behavior before replacing a UDF.

Package and runtime controls:

- Pin JDK, Python, Spark, Scala, Hadoop connector, and table-format versions.
- Build immutable job artifacts and use CI tests against the intended runtime image.
- Store secrets in a managed secret service or workload identity, not in job arguments or source code.
- Make the input snapshot, code version, config version, and output partition identifiable for every run.

### 9.4 Oozie to Airflow or another orchestrator

Do not translate XML action-for-action without reconstructing semantics. Inventory:

- Workflow action dependencies and fork/join behavior.
- Coordinator frequency, time zone, input availability conditions, and dataset dependencies.
- Bundle-level grouping and deployment lifecycle.
- Retries, error/kill transitions, alerts, timeouts, concurrency, and backfills.
- Parameters, credentials, proxy users, and environment setup.

A representative Airflow DAG fragment:

```python
from datetime import timedelta
import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="sales_daily_migration_example",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule="0 3 * * *",
    catchup=False,  # Explicitly chosen; enable backfills only with a reviewed policy.
    max_active_runs=1,
    default_args={
        "owner": "data-platform",
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
        "execution_timeout": timedelta(hours=2),
    },
    tags=["migration", "sales"],
) as dag:
    wait_for_inputs = BashOperator(
        task_id="wait_for_inputs",
        bash_command="python /opt/pipelines/check_inputs.py",
    )
    transform = BashOperator(
        task_id="transform",
        bash_command="spark-submit /opt/jobs/sales_daily.py",
    )
    validate = BashOperator(
        task_id="validate",
        bash_command="python /opt/pipelines/validate_sales_daily.py",
    )
    wait_for_inputs >> transform >> validate
```

This is a template, not a tested drop-in conversion. Production DAGs should use provider-specific operators, explicit data intervals, sensors/deferrable waits where appropriate, secret integration, callbacks/alerts, and deployment-specific executor settings. The example uses UTC and `catchup=False` intentionally; preserve the old coordinator's local-time behavior and backfill contract rather than copying those settings blindly. Ensure every task can be retried safely.

### 9.5 Replace Sqoop ingestion

Options include managed database connectors, Spark JDBC, CDC products, or custom ingestion where justified. Decide based on source database load, transaction isolation, update/delete behavior, freshness, schema evolution, and operational ownership.

For Spark JDBC, partitioned reads can improve parallelism but can also overload the source database. The `lowerBound` and `upperBound` options determine partition stride; they do not necessarily filter rows to that range. Add the intended SQL predicate separately when filtering is required, and ensure partition predicates do not omit or duplicate records.

For incremental ingestion, maintain a durable state record such as:

```text
pipeline_id | source_id | last_committed_offset | target_commit_id | status | updated_at
```

Commit the new checkpoint only after the target write and validation succeed. A retry should re-read the same source interval and produce the same logical target state. Prefer a transactionally safe merge keyed by stable business key and source version/sequence. Timestamp-only watermarks can miss updates when clocks are skewed, precision is low, or late changes arrive; use database log sequence numbers/CDC offsets where available or a carefully designed overlap window plus deduplication.

### 9.6 Replace Flume ingestion

Choose based on whether the workload is log shipping, event streaming, telemetry, or application event collection. Verify buffering and replay, at-least-once/at-most-once behavior, ordering scope, event timestamps, schema evolution, backpressure, dead-letter routing, and retention.

If the new pipeline is at-least-once, downstream writes must deduplicate or be idempotent. Do not claim end-to-end exactly-once semantics simply because a broker or sink supports transactions; the full source-to-sink path and failure boundaries determine the guarantee.

### 9.7 Migrate HBase deliberately

HBase is an online key-value/wide-column serving database backed by HDFS, not a collection of analytical files. Choose a target only after capturing:

- Row-key and key-range distribution; hotspotting risk.
- Point reads/writes, scans, batch operations, write amplification, and p95/p99 latency.
- Column families/qualifiers, cell versions, TTL, tombstones/deletes, atomic row mutations, and consistency requirements.
- Secondary lookup requirements, index patterns, and query shape.
- Data volume, growth, retention, backup/restore, replication, and regional availability.

Target examples are conditional: Bigtable is a wide-column serving option; DynamoDB is a managed key-value/document database with its own key and access-pattern model; Cassandra is a distributed wide-column database with different operational and consistency trade-offs. Data modeling often must be redesigned. Exporting HBase records into Parquet or Iceberg is useful for analytics/archival, but does not replace a low-latency serving API.

A safe HBase migration usually includes a snapshot/export or controlled replication, incremental mutation capture, dual-read/shadow-read comparison, application cutover, and a rollback window. Dual writes require ordering, idempotency, and reconciliation; if those cannot be guaranteed, use a single writer plus change-log replication.

## 10. Validation and reconciliation

Validation is an evidence system. Each check must specify the source boundary, target boundary, comparison grain, tolerance, result, owner, and disposition of exceptions.

### 10.1 Validation layers

| Layer | Checks | What it catches |
|---|---|---|
| File/transfer | File count, byte count, expected paths, failed copy records, manifests | Missing or unexpected files; incomplete transfer |
| Schema | Column names/order where relevant, types, nullability, decimal precision, timestamp semantics, nested fields | Schema drift and silent type coercion |
| Basic profile | Row count, null counts, min/max, distinct counts, approximate statistics where explicitly acceptable | Broad omissions, null changes, out-of-range values |
| Key integrity | Duplicate primary/business keys, key coverage, orphan foreign keys | Missing, duplicated, orphaned entities |
| Content | Canonical row hashes, key-based full outer join, selected-column checksums | Changed rows and key-level discrepancies |
| Business semantics | Revenue totals, counts by status/date/region, latest-state selection, balances, SLA-specific aggregates | Wrong filters, joins, deduplication, time boundaries, or calculations |
| Query behavior | Compare representative query outputs and query plans/performance | SQL semantic differences and regression |
| Operational | Runtime, retries, freshness, lag, failure recovery, alert delivery | Workload or service-level regression |
| Security/governance | Positive and negative access tests, lineage, audit events, retention/deletion | Overexposure, broken policy, missing traceability |

A row count is necessary for many tables but never sufficient by itself. Counts can match while records are duplicated and others are missing, or while values are changed.

### 10.2 Define a canonical comparison contract

Before comparing, define:

- The source snapshot/version and exact time boundary.
- The stable business key (or a multiset-based strategy if no unique key exists).
- Included columns and canonical type normalization.
- Timestamp timezone and precision, decimal rounding, string normalization, and null representation.
- Expected late-arrival/update/delete handling.
- Whether results require exact equality or a business-approved tolerance.
- How nondeterministic outputs (for example, tied window ordering) are made deterministic.

Avoid comparing raw serialized rows when source and target serialize equivalent values differently. Canonicalization must preserve business meaning and must not silently normalize away a real data defect.

### 10.3 PySpark validation script for keyed tables

The following script compares two Spark tables that are accessible through the configured Spark session. It assumes the selected key columns uniquely identify a row in each snapshot. It reports schema differences, counts, null counts, duplicate keys, and mismatching keyed rows. It is a lab template: set table names and column lists to the actual environment, pin the runtime, and validate timestamp/decimal canonicalization before production use.

```python
# migration/validate_tables.py
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence
from pyspark.sql import DataFrame, SparkSession, functions as F

SOURCE_TABLE = "hive_src.orders"
TARGET_TABLE = "lakehouse.orders_migration"
KEY_COLUMNS = ["order_id"]
COMPARE_COLUMNS = ["customer_id", "order_date", "status", "net_amount"]
REPORT_PATH = Path("experiments/07_migration/validation/table_validation_report.json")
RUN_ID = os.environ.get("MIGRATION_RUN_ID", "UNSET")
SOURCE_BOUNDARY = os.environ.get("SOURCE_SNAPSHOT_OR_OFFSET", "UNSET")
TARGET_BOUNDARY = os.environ.get("TARGET_SNAPSHOT_OR_COMMIT", "UNSET")
CODE_VERSION = os.environ.get("MIGRATION_CODE_VERSION", "UNSET")


def schema_signature(df: DataFrame, columns: Sequence[str]) -> list[tuple[str, str]]:
    fields = {field.name: field.dataType.simpleString() for field in df.schema.fields}
    missing = [name for name in columns if name not in fields]
    if missing:
        raise ValueError(f"Required columns missing: {missing}")
    return [(name, fields[name]) for name in columns]


def duplicate_key_count(df: DataFrame, keys: Sequence[str]) -> int:
    return (df.groupBy(*keys).count().where(F.col("count") > 1).count())


def null_counts(df: DataFrame, columns: Sequence[str]) -> dict[str, int]:
    expressions = [
        F.sum(F.when(F.col(name).isNull(), F.lit(1)).otherwise(F.lit(0))).alias(name)
        for name in columns
    ]
    row = df.agg(*expressions).first()
    return {name: int(row[name] or 0) for name in columns}


def canonical_digest(df: DataFrame, columns: Sequence[str]) -> DataFrame:
    # The struct column order is explicit. For timestamps/decimals, apply the
    # agreed business canonicalization before calling this function.
    payload = F.to_json(F.struct(*[F.col(name).alias(name) for name in columns]))
    return df.withColumn("__row_sha256", F.sha2(payload, 256))


def main() -> None:
    spark = (SparkSession.builder
             .appName("hadoop-migration-table-validation")
             .enableHiveSupport()
             .getOrCreate())
    try:
        src = spark.table(SOURCE_TABLE).select(*(KEY_COLUMNS + COMPARE_COLUMNS))
        tgt = spark.table(TARGET_TABLE).select(*(KEY_COLUMNS + COMPARE_COLUMNS))

        src_schema = schema_signature(src, KEY_COLUMNS + COMPARE_COLUMNS)
        tgt_schema = schema_signature(tgt, KEY_COLUMNS + COMPARE_COLUMNS)
        src_count, tgt_count = src.count(), tgt.count()
        src_dupes = duplicate_key_count(src, KEY_COLUMNS)
        tgt_dupes = duplicate_key_count(tgt, KEY_COLUMNS)
        src_nulls, tgt_nulls = null_counts(src, COMPARE_COLUMNS), null_counts(tgt, COMPARE_COLUMNS)

        report = {
            "run_id": RUN_ID,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "code_version": CODE_VERSION,
            "source_snapshot_or_offset": SOURCE_BOUNDARY,
            "target_snapshot_or_commit": TARGET_BOUNDARY,
            "source_table": SOURCE_TABLE,
            "target_table": TARGET_TABLE,
            "source_rows": src_count,
            "target_rows": tgt_count,
            "row_count_equal": src_count == tgt_count,
            "source_schema": src_schema,
            "target_schema": tgt_schema,
            "schema_equal": src_schema == tgt_schema,
            "source_duplicate_key_groups": src_dupes,
            "target_duplicate_key_groups": tgt_dupes,
            "source_null_counts": src_nulls,
            "target_null_counts": tgt_nulls,
        }

        if src_dupes or tgt_dupes:
            report["keyed_row_comparison"] = "NOT_RUN: key columns are not unique"
            report["mismatching_keys"] = None
        else:
            s = canonical_digest(src, KEY_COLUMNS + COMPARE_COLUMNS).select(
                *KEY_COLUMNS, F.col("__row_sha256").alias("src_hash")
            )
            t = canonical_digest(tgt, KEY_COLUMNS + COMPARE_COLUMNS).select(
                *KEY_COLUMNS, F.col("__row_sha256").alias("tgt_hash")
            )
            join_condition = [s[k] == t[k] for k in KEY_COLUMNS]
            joined = s.join(t, on=join_condition, how="full_outer")
            mismatch = joined.where(
                F.col("src_hash").isNull()
                | F.col("tgt_hash").isNull()
                | (F.col("src_hash") != F.col("tgt_hash"))
            )
            report["mismatching_keys"] = mismatch.count()
            report["keyed_row_comparison"] = "COMPLETED"

        failed_checks = []
        if RUN_ID == "UNSET" or SOURCE_BOUNDARY == "UNSET" or TARGET_BOUNDARY == "UNSET" or CODE_VERSION == "UNSET":
            failed_checks.append("required_evidence_metadata_unset")
        if src_count != tgt_count:
            failed_checks.append("row_count_mismatch")
        if src_schema != tgt_schema:
            failed_checks.append("schema_mismatch")
        if src_dupes or tgt_dupes:
            failed_checks.append("duplicate_keys_prevent_keyed_comparison")
        elif report["mismatching_keys"]:
            failed_checks.append("keyed_row_mismatches")
        report["failed_checks"] = failed_checks
        report["passed"] = not failed_checks
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        print(json.dumps(report, indent=2, default=str))
    finally:
        spark.stop()
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

**Interpretation and limitations:**

- A duplicate-key group count is the number of key groups with duplicates, not the number of duplicate rows.
- If keys are duplicated, do not run the keyed join and assume correctness. Either resolve the key contract or compare row-hash multiplicities as a multiset.
- `sha2` hashes the canonical JSON representation; this is a practical comparison mechanism, not a mathematical proof against all collisions. For high-assurance use, retain key-level mismatches and use stronger reconciliation appropriate to the domain.
- Schema signature compares Spark's `simpleString()` types; extend it to compare nullability, nested schemas, decimal precision, and metadata if those are part of the contract.
- The script uses Spark actions (`count`, groupBy, join) that may scan the full dataset. Use partition-aware validation, cached snapshots, or staged aggregate checks where appropriate, but do not silently substitute samples for full validation.
- If the source and target are not on the same Spark session/catalog, run the same deterministic manifest process on each side and compare the exported evidence securely.

### 10.4 Multiset comparison when no unique key exists

If no stable key exists, compute a canonical digest per row and compare the **count of each digest** between source and target. This detects both missing/changed records and duplicate multiplicity, subject to canonicalization and hash-collision assumptions. For very large tables, aggregate by deterministic partitions/buckets and compare manifests rather than collecting all rows to the driver.

Example pattern:

```python
from pyspark.sql import functions as F

cols = ["event_time", "event_type", "payload"]

def digest_multiset(df):
    canonical = F.to_json(F.struct(*[F.col(c).alias(c) for c in cols]))
    return (df.withColumn("digest", F.sha2(canonical, 256))
              .groupBy("digest").count())

source_multiset = digest_multiset(source_df).withColumnRenamed("count", "source_count")
target_multiset = digest_multiset(target_df).withColumnRenamed("count", "target_count")
comparison = (source_multiset.join(target_multiset, "digest", "full_outer")
              .fillna(0, subset=["source_count", "target_count"])
              .where(F.col("source_count") != F.col("target_count")))
```

This snippet assumes `source_df` and `target_df` already exist and that columns have been normalized to a canonical representation. Do not call `.collect()` on the raw source or target rows. Persist comparison counts and mismatching digests as evidence.

### 10.5 Business-query result comparison

For each critical query, store:

- Query ID and versioned SQL.
- Input snapshot IDs/high-water marks.
- Execution time and engine/runtime version.
- Result schema, row count, and deterministic ordering key.
- Canonical row hashes or business aggregates.
- Approved tolerance and explanation for any non-exact comparison.

Example aggregate comparison:

```sql
SELECT order_date,
       COUNT(*) AS orders,
       COUNT(DISTINCT order_id) AS distinct_orders,
       SUM(net_amount) AS net_sales,
       SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled_orders
FROM lakehouse.orders
WHERE order_date >= DATE '2026-01-01'
GROUP BY order_date;
```

Run the equivalent query against the source snapshot. Compare per-day/per-region aggregates rather than only one grand total; offsetting errors can otherwise cancel each other out. Distinct counts and sums are complementary, not substitutes for row-level checks.

### 10.6 Parallel runs and reconciliation tolerances

During parallel runs, the old and new pipelines must process the same logical input boundary. Record each run's source offsets, code/config versions, completion time, output snapshot, and validation report. Avoid comparing two outputs that naturally represent different event-time windows.

A tolerance is allowed only when the business contract defines it. Examples include a known approximation error for an approximate distinct count or a floating-point aggregation tolerance. Exact financial amounts, identifiers, and regulated facts normally require exact or explicitly governed rounding semantics. Every tolerated discrepancy needs a reason, bound, owner, and expiration or remediation date.

## 11. Cutover, rollback, and decommissioning

### 11.1 Cutover readiness gate

Do not approve cutover until every applicable gate is green or has a documented, explicitly accepted exception:

- Inventory is complete; owners and consumers have signed off.
- All critical datasets and workflows have passed agreed validation on defined source boundaries.
- Incremental lag is below the agreed threshold; deletes and late updates are reconciled.
- Parallel-run evidence covers the required cycle (the roadmap exercise uses one simulated week; production may require month-end, quarter-end, or seasonal cycles).
- Security, row/column access, secrets, encryption, network, audit, and governance tests pass.
- SLA, freshness, recovery, alerting, dashboards, and on-call runbooks are tested.
- Performance and cost are within approved limits under representative load.
- Rollback has been rehearsed, including routing/writer ownership and the last safe source checkpoint.
- Stakeholder communications and change approvals are complete.

### 11.2 Freeze window and final synchronization

A controlled cutover sequence:

1. Announce the window, owners, stop conditions, and decision authority.
2. Stop new source scheduling or fence source writes using the agreed mechanism; do not assume a scheduler pause stops all external writers.
3. Wait for or explicitly terminate in-flight jobs; record incomplete outputs and checkpoints.
4. Capture a final source high-water mark (transaction log position, CDC offset, batch ID, or source snapshot ID).
5. Apply final incremental changes, including deletes and late-arriving corrections.
6. Run final row/key/content/business reconciliation and security smoke tests.
7. Switch writer ownership and consumer routing in a controlled, logged operation.
8. Run a small set of production smoke queries and end-to-end pipeline checks.
9. Monitor latency, error rates, freshness, cost, and reconciliation for the agreed observation period.
10. Keep the legacy source read-only and intact until rollback criteria and retention rules permit retirement.

### 11.3 Rollback design

Define rollback before cutover. It must specify:

- **Trigger:** which validation failure, data-lag breach, security issue, SLA regression, or operational outage forces rollback.
- **Decision owner:** one accountable incident/change authority, not a committee assembled during an outage.
- **Writer fencing:** how the system guarantees that only one platform is authoritative.
- **Data reconciliation:** how target-only writes are replayed or reconciled if the target accepted production writes after cutover.
- **Routing reversal:** exact config/alias/connection change and its expected propagation time.
- **Checkpoint:** last known-good source/target offsets and table snapshots.
- **Verification:** queries and checks that prove legacy service is restored and data is consistent.
- **Communication:** status page/channel, stakeholder notification, incident record, and follow-up.

A rollback is straightforward only while the old platform remains current or target writes can be replayed safely. If users write to the new platform after cutover, simply pointing readers back to the old platform may lose those writes. Choose one of these designs explicitly: a short read-only target observation period; reverse CDC/change capture; dual writes with proven consistency; or forward-fix recovery when rollback is unsafe. Do not promise a rollback path that cannot preserve writes.

### 11.4 Decommissioning criteria

Decommission only when all criteria are satisfied and approved:

- No active consumer, job, service account, or external integration uses the cluster or old paths.
- Data owners approve archival, deletion, or retention; legal holds and compliance retention are resolved.
- Required lineage, audit logs, run histories, schemas, code, configuration, and evidence are retained in an accessible location.
- Source-to-target reconciliation and cutover approvals are complete.
- Recovery/rollback window has expired and the decision is recorded.
- Backups and disaster recovery procedures for the new platform have been tested.
- Security team confirms credentials, keytabs, certificates, network routes, and unused access are revoked safely.
- Costs, licenses, hardware contracts, and vendor support are closed out.
- A final change record identifies the decommission date, approvers, archived artifacts, and residual risks.

Do not delete HDFS data merely because the target has matching row counts. Ensure retention policy, audit evidence, table-format ownership, and rollback period are complete.

## 12. Security, governance, lineage, and organizational readiness

### 12.1 Identity and access migration

Map both **human access** and **workload identity**. For each old Kerberos principal/service account, identify the new workload identity, allowed services, data scope, token lifetime, and secret rotation owner.

| Legacy control | Target design | Validation required |
|---|---|---|
| Kerberos user/service principals and keytabs | Federated identity, cloud IAM roles/service accounts, managed identities, or short-lived workload credentials | Positive/negative authentication tests, rotation, impersonation/delegation behavior, least privilege |
| HDFS POSIX owner/group/mode | Object/container IAM plus catalog/table authorization and service-level policies | Test list/read/write/delete separately; confirm object permissions do not bypass catalog governance |
| Ranger resource/column/row/tag policies | IAM and service-specific authorization, Lake Formation, Unity Catalog, or platform-equivalent controls | Recreate policy semantics, tag inheritance, masking, row filters, admin and break-glass access |
| Hadoop audit logs | Cloud audit logs, query/job logs, SIEM export | Verify event coverage, actor identity, retention, alerting, tamper resistance, and time synchronization |
| HDFS encryption zones / KMS | Cloud encryption at rest, customer-managed keys where required, key policies and rotation | Verify encryption scope, key ownership, restore access, cross-account/region behavior |
| Network segmentation and private endpoints | VPC/VNet, private endpoints, firewall/security groups, service perimeters | Test data-plane and control-plane connectivity, DNS, egress restrictions, and approved routes |
| Secret files and command-line passwords | Managed secret store or workload identity | Confirm secrets do not appear in logs, shell history, images, or CI artifacts |

IAM is not automatically equivalent to Ranger. A successful object-store read test by a service principal does not prove that end users are still subject to row/column policies. Test effective access through the actual query engine and catalog.

### 12.2 Governance and lineage continuity

For each table and pipeline, migrate or recreate:

- Business definition, owner, steward, classification, retention, and data quality contract.
- Source-to-target lineage and transformation version.
- Schema change history and compatibility policy.
- Access policy, masking/filter rules, and approved consumer list.
- Audit evidence, deletion workflows, legal hold, and subject/data-subject requests where applicable.
- Operational metadata: last successful run, freshness, failures, exceptions, and support contact.

Lineage should bridge old and new systems. Mark the migration boundary so consumers can distinguish source-era lineage from target-era lineage. Preserve historical audit records even after the source scheduler or catalog is retired.

### 12.3 Organizational readiness

Assign named accountable owners for platform, data domains, pipelines, security, governance, finance, and application consumers. Plan role-specific training for Spark/runtime operations, table-format maintenance, catalog policies, cost observability, and incident response. Publish migration wave calendars, freeze windows, known changes, support contacts, and a rollback status channel.

Acceptance should be signed by both a technical owner and a business/data owner. The platform team can attest to technical checks; only the data owner can approve changed business semantics or an explicit exception to data quality requirements.

## 13. Cost model and total cost of ownership

### 13.1 Cost categories

Compare on-premises and target costs across the same period and workload envelope.

**On-premises TCO** may include hardware depreciation/refresh, storage, network, power/cooling, data-center costs, software/support, backup/DR, security, platform engineering, operations/on-call, and opportunity cost of scarce skills.

**Cloud TCO** may include object storage, requests/listing, storage tiers and retrieval, managed compute/serverless execution, cluster idle time, shuffle disks, catalog/metadata operations, network transfer/egress, cross-region/cross-account traffic, logging/monitoring, backups/replication, security services, support plans, licensing, and platform engineering.

Use the same assumptions for retention, concurrency, recovery, data growth, and service levels. A cloud bill without staffing and operational costs is not a complete TCO comparison; neither is an on-premises hardware invoice without data-center and support costs.

### 13.2 A parameterized cost model

Use variables instead of inventing provider prices:

```text
C_cloud_month =
    C_object_storage
  + C_storage_requests
  + C_compute
  + C_catalog_and_governance
  + C_network_and_egress
  + C_transfer_appliance_and_ingest
  + C_observability_and_security
  + C_backup_and_DR
  + C_support_and_licenses
  + C_platform_engineering
```

For each category, document quantity, unit price source, billing unit, region, discount/commitment assumptions, expected utilization, and owner. Prices vary by provider, region, service, date, and contract; retrieve current prices for the selected design before approving the budget.

### 13.3 Sensitivity analysis

At minimum, calculate base, low, and high scenarios for:

- Average and peak compute hours; utilization and idle time.
- Data growth and retention duration.
- Object count and request/listing volume.
- Cross-region reads, data egress, and repeat transfers.
- Compression ratio and target file size.
- Parallel-run duration and duplicate platform costs.
- Recovery/DR copies and replication frequency.
- Number of queries, scanned bytes, and concurrency.

A useful sensitivity question is: “What happens if the migration takes 12 weeks longer, the dual-run lasts 2 extra months, and the data grows 30% faster than forecast?” State that these are scenario assumptions, not forecasts. If cost reduction is an objective, define a comparable workload unit (for example, cost per successful daily batch or cost per TB scanned) and monitor it after cutover.

### 13.4 Common cloud cost surprises

- Keeping clusters running while waiting for schedules or approvals.
- Over-parallelizing Spark and overwhelming source databases or object-store request limits.
- Excessive small-file listing and planning overhead.
- Rewriting all data when metadata conversion would have been safe—or choosing in-place conversion when physical isolation is required.
- Duplicating storage during parallel runs and retaining orphan files indefinitely.
- Cross-region/cross-account data access and egress.
- Unbounded logs, audit retention, query history, or debug output.
- Repeated full scans for validation instead of planned partitioned reconciliation.
- Repeated retries that reprocess the full dataset.

## 14. Worked enterprise migration scenario

All details in this section are **illustrative planning assumptions**. They are not measured results, benchmark outcomes, cloud quotes, or evidence that a migration has run successfully.

### 14.1 Starting environment and assumptions

| Attribute | Illustrative value | Required discovery action |
|---|---:|---|
| HDFS logical data volume | 500 TB decimal | Measure source logical bytes, physical bytes, file count, replication factor, and growth |
| Hive tables | 300 | Inventory format, partitioning, schema, readers/writers, owners, sensitivity, and freshness |
| Oozie workflows | 120 | Export workflow/coordinator/bundle graph, schedule, retries, parameters, dependencies, and SLAs |
| HBase tables | 2 | Measure QPS, p95/p99 latency, row-key distribution, mutations, TTL, versions, scans, and recovery needs |
| Source compute | YARN-managed MapReduce and Spark | Collect job runtimes, resource usage, shuffle, failures, and queue contention |
| Target | Cloud object storage + Spark + Iceberg or Delta + compatible catalog | Choose provider and exact runtime after requirements and compatibility review |
| Data sync | Initial bulk + incremental changes | Identify CDC/log support, update/delete behavior, late arrivals, and final high-water mark |
| Migration strategy | Four waves with a strangler boundary | Assign workload owners and source-of-truth rules per wave |
| Parallel-run exercise | One simulated week | Label generated/simulated evidence; production acceptance may require longer business cycles |

### 14.2 First-pass component map

| Source | Proposed target pattern | Decision gate |
|---|---|---|
| HDFS raw/history | Cloud object storage raw/landing prefixes | Validate transfer window, security, lifecycle, path mapping, and object count |
| Hive external/managed tables | Iceberg or Delta tables and compatible catalog | Classify each table as metadata conversion, rewrite, archive, or retire |
| HiveQL/Spark jobs | Spark SQL/dbt or managed SQL where appropriate | Query-level reconciliation and runtime compatibility |
| MapReduce jobs | Spark or another fit-for-purpose engine | Algorithm/output equivalence, failure behavior, resource profile |
| YARN queues | Managed compute/serverless/Kubernetes execution pools | Match isolation, quotas, concurrency, SLA, and operational support |
| Oozie | Airflow/managed orchestrator | Schedule/time-zone/backfill equivalence and idempotent retries |
| Sqoop jobs | CDC/managed connector/Spark JDBC | Snapshot consistency, watermark correctness, deletes, and source load |
| Flume agents | Kafka/managed event ingestion/log pipeline | Buffering, replay, event ordering, schema and delivery behavior |
| HBase tables | Workload-selected serving database plus analytics export where needed | Latency/QPS and application API acceptance; not merely data count |
| Ranger/Kerberos | IAM + catalog governance + workload identity | Effective permission tests and audit continuity |

### 14.3 Four-wave plan

The counts below partition the 300 Hive tables and 120 Oozie workflows for planning purposes. Actual counts should change after inventory and dependency analysis. Both HBase tables are assigned to Wave 4 as a separate, high-risk serving migration; they must not be treated as low-risk table copies.

| Wave | Scope | Dependencies | Main risks | Validation | Acceptance criteria | Rollback | Exit conditions |
|---|---|---|---|---|---|---|---|
| **Wave 1 — pilot and low-risk batch** | 30 low-risk Hive tables; 10 low-complexity workflows; a small representative sample of file formats and query patterns | Target landing zone, identity, network, catalog, monitoring, version matrix, source snapshot, inventory | Pilot is unrepresentative; source paths or metadata are misunderstood; hidden consumer discovered | File manifest, schema, row counts, key hashes, business aggregates, query result comparison, negative access tests, rerun test | All pilot owners sign off; no unexplained critical mismatch; retry is idempotent; measured transfer/compute behavior supports revised plan | Route reads/writes to source; retain target staging data for investigation; replay from source snapshot | Runbook proven; reusable CI validation and observability in place; revised throughput/cost estimates approved |
| **Wave 2 — core batch domains** | 90 Hive tables; 35 workflows; ingestion replacements for selected Sqoop jobs | Wave 1 exit; dependency graph; CDC/checkpoint design; target capacity and cost controls | Watermark gaps, schema drift, source database overload, late corrections | Daily and partition-level reconciliation; CDC lag; delete/update checks; parallel run over representative business cycles | All tier-1 tables in scope pass contracts; workflow SLA met; no missing/duplicate changes; security and owner approvals complete | Freeze target writer, resume source schedule, replay from committed source offset, revert routing | No unresolved critical defects; operations and finance accept cost/performance; next wave capacity proven |
| **Wave 3 — high-volume and complex analytics** | 120 Hive tables; 50 workflows; high-volume ORC/Parquet, small-file and skew-heavy jobs; selected MapReduce-to-Spark rewrites | Wave 2 operational maturity; representative load testing; partition/compaction design; UDF dependency build | Rewrites alter SQL semantics; shuffle/skew regression; conversion shares source files unsafely; cost overrun | Full table profiles, key/multiset hashes, business query diff, query plan/runtime comparison, failure injection, retention/compaction tests | Business outputs equivalent or formally approved; SLA and cost limits met; metadata/file ownership documented; rollback rehearsal passes | Keep old jobs/source data intact; stop target scheduling; route consumers to old output; replay target-only changes if writes occurred | All critical analytics consumers migrated; no unexplained data-quality delta; catalog/lineage and runbooks accepted |
| **Wave 4 — serving, final cutover, and retirement** | Remaining 60 Hive tables; 25 workflows; both HBase tables; final consumer routing; source decommission preparation | Prior waves accepted; HBase access-pattern study; dual-read/replication design; final freeze approval; compliance sign-off | Online latency/consistency regression; write divergence; hidden legacy consumer; rollback cannot preserve target writes | HBase shadow reads and mutation reconciliation; p95/p99/QPS tests; full final synchronization; access-control tests; one-week parallel-run report plus business-cycle-specific checks | Serving API owners sign off; RTO/RPO and SLA tests pass; final counts/hashes/business rules reconcile; rollback/forward-recovery decision approved | Keep source available/read-only or use rehearsed reverse replication; fence one writer; restore old routing and reconcile target-only writes | No legacy dependency; evidence archived; keys/credentials safely retired; retention and legal hold approved; formal decommission sign-off |

**Wave count note:** 30 + 90 + 120 + 60 = 300 Hive tables; 10 + 35 + 50 + 25 = 120 workflows. These are illustrative allocations, not a claim that all assets are equally difficult. Move assets between waves based on dependency and risk.

### 14.4 Decision log template

For every material decision, record:

```text
Decision ID:
Date / owner / approvers:
Asset(s) affected:
Decision: convert in place | rewrite | replatform | refactor | retain | retire
Options considered:
Evidence collected:
Assumptions and unknowns:
Compatibility/version evidence:
Security/governance impact:
Cost and operational impact:
Validation plan and acceptance threshold:
Rollback/recovery plan:
Risks accepted and expiry/review date:
```

## 15. Hands-on exercises: `experiments/07_migration/`

### Exercise 1 — inventory the lab Hive tables

**Goal:** Produce a machine-readable table inventory and clearly distinguish measured metadata from unavailable or inferred information.

**Suggested outputs:**

```text
experiments/07_migration/
├── inventory/
│   ├── hive_tables.csv
│   ├── inventory_run.json
│   └── inventory_notes.md
├── copy/
├── validation/
├── sql_rewrite/
└── cutover/
```

Required columns: database, table, location, provider/format, partition columns, partition count, file count, logical size bytes, schema fingerprint, owner, sensitivity, last-access timestamp, last-modified timestamp, source/method, confidence, collected-at timestamp.

**Procedure:**

1. Connect to Hive Metastore/HiveServer2 with a read-only lab identity.
2. Enumerate databases and tables.
3. For each table, collect `DESCRIBE FORMATTED`/catalog metadata where available: location, input format, output format, SerDe, partition keys, table type, and properties.
4. Measure file count and bytes from the underlying filesystem using an API or controlled filesystem listing; record the measurement timestamp and method. Do not assume metastore table size is always current.
5. Capture partition count from metastore/catalog metadata or a documented partition listing. Avoid expensive `MSCK REPAIR` or full scans merely for inventory.
6. Look for last-access data in query/audit logs or scheduler history. If not reliably available, set `last_access_at=unavailable`; do not substitute file modification time.
7. Add data owner/sensitivity from a governed source or mark it `unverified`; do not infer sensitivity from a table name alone.
8. Review the output with a data owner and identify unknowns that block migration.

Example `inventory_notes.md` entry:

```text
Table: sales.orders
Size: 1,240,000,000,000 bytes
Method: recursive filesystem metadata listing at 2026-10-19T00:00:00Z
Status: collected (metadata-based, not a full data scan)
Last access: unavailable — Hive Metastore has no verified query timestamp in this lab
Owner: unverified — awaiting domain owner confirmation
```

The values above are examples of how to label evidence, not measurements from your environment.

**Starter inventory script (Spark catalog / lab scale):** save as `experiments/07_migration/inventory/inventory_hive.py`. It enumerates catalog tables, reads available `DESCRIBE EXTENDED` metadata, fingerprints the Spark schema, measures accessible data-file bytes and latest visible data-file modification time through Hadoop's filesystem API, and explicitly leaves last access unavailable. Owner metadata is only a hint; sensitivity must come from a governed source. The script is intended for a small lab; do not run a full file listing or `SHOW PARTITIONS` over an enormous production catalog without assessing metastore and object-store load.

```python
# experiments/07_migration/inventory/inventory_hive.py
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from pyspark.sql import SparkSession

OUTPUT = Path("experiments/07_migration/inventory/hive_tables.csv")
MANIFEST = Path("experiments/07_migration/inventory/inventory_run.json")


def quote_identifier(value: str) -> str:
    return "`" + value.replace("`", "``") + "`"


def describe_properties(spark: SparkSession, db: str, table: str) -> dict[str, str]:
    ident = f"{quote_identifier(db)}.{quote_identifier(table)}"
    props: dict[str, str] = {}
    for row in spark.sql(f"DESCRIBE EXTENDED {ident}").collect():
        key = str(row[0]).strip() if row[0] is not None else ""
        value = str(row[1]).strip() if row[1] is not None else ""
        if key and key not in {"# col_name", "# Detailed Table Information", "# Partition Information"}:
            props[key.rstrip(":")] = value
    return props


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    spark = SparkSession.builder.appName("hive-metadata-inventory").enableHiveSupport().getOrCreate()
    rows: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    try:
        for db in sorted(d.name for d in spark.catalog.listDatabases()):
            for table in sorted(spark.catalog.listTables(dbName=db), key=lambda t: t.name):
                if table.tableType.upper() == "VIEW":
                    continue
                try:
                    ident = f"{quote_identifier(db)}.{quote_identifier(table.name)}"
                    props = describe_properties(spark, db, table.name)
                    columns = spark.catalog.listColumns(table.name, dbName=db)
                    partition_cols = [c.name for c in columns if getattr(c, "isPartition", False)]
                    location = props.get("Location", "")
                    provider = props.get("Provider", props.get("InputFormat", "unknown"))
                    df = spark.table(ident)
                    schema_json = df.schema.json()
                    schema_fingerprint = hashlib.sha256(schema_json.encode("utf-8")).hexdigest()
                    files = df.inputFiles()
                    conf = spark.sparkContext._jsc.hadoopConfiguration()
                    total_bytes = 0
                    accessible_files = 0
                    max_mtime_ms: int | None = None
                    for uri in files:
                        path = spark.sparkContext._jvm.org.apache.hadoop.fs.Path(uri)
                        fs = path.getFileSystem(conf)
                        status = fs.getFileStatus(path)
                        if status.isFile():
                            total_bytes += int(status.getLen())
                            accessible_files += 1
                            mtime_ms = int(status.getModificationTime())
                            max_mtime_ms = mtime_ms if max_mtime_ms is None else max(max_mtime_ms, mtime_ms)
                    last_modified_at = (
                        datetime.fromtimestamp(max_mtime_ms / 1000, tz=timezone.utc).isoformat()
                        if max_mtime_ms is not None else "unavailable_no_visible_data_files"
                    )
                    partition_count: object = "not_partitioned"
                    if partition_cols:
                        # Appropriate for the small lab only; can be expensive at production scale.
                        partition_count = spark.sql(f"SHOW PARTITIONS {ident}").count()
                    rows.append({
                        "database": db, "table": table.name, "table_type": table.tableType,
                        "location": location, "provider_or_input_format": provider,
                        "partition_columns": ",".join(partition_cols),
                        "partition_count": partition_count, "file_count": accessible_files,
                        "logical_file_bytes_observed": total_bytes,
                        "schema_fingerprint_sha256": schema_fingerprint,
                        "owner_from_metadata": props.get("Owner", "unavailable"),
                        "sensitivity": "unverified_governance_source_required",
                        "last_access_at": "unavailable_without_query_or_audit_evidence",
                        "last_modified_at_max_visible_data_file_utc": last_modified_at,
                        "measurement_method": "Spark inputFiles + Hadoop FileStatus; visible data-file metadata, not row scan",
                        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
                        "confidence": "file metrics cover accessible Spark-visible files only; owner/sensitivity and last access require independent verification",
                    })
                except Exception as exc:  # preserve inventory progress; investigate every failed table
                    errors.append({"database": db, "table": table.name, "error": repr(exc)})
        fieldnames = list(rows[0].keys()) if rows else [
            "database", "table", "table_type", "location", "provider_or_input_format",
            "partition_columns", "partition_count", "file_count", "logical_file_bytes_observed",
            "schema_fingerprint_sha256", "owner_from_metadata", "sensitivity", "last_access_at",
            "last_modified_at_max_visible_data_file_utc", "measurement_method", "collected_at_utc", "confidence",
        ]
        with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        MANIFEST.write_text(json.dumps({
            "started_at_utc": started,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "tables_written": len(rows),
            "table_errors": errors,
            "note": "Last access is not inferred from file modification time. Review table errors and metadata coverage.",
        }, indent=2), encoding="utf-8")
        if errors:
            raise RuntimeError(f"Inventory completed with {len(errors)} table errors; inspect {MANIFEST}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
```

**Interpretation caveats:** `inputFiles()` and filesystem status results reflect the files visible to that Spark reader and filesystem connector, not necessarily every hidden/orphan file under the table path. The reported byte total is the sum of accessible data files, not HDFS replicated physical capacity. The schema fingerprint is a hash of Spark's schema JSON, not a data-content checksum. `last_modified_at_max_visible_data_file_utc` is the latest modification time among visible data files, not a reliable table-level last-modified or last-access time. The script intentionally does not claim a last-access time and does not infer it from modification time. Review catalog-specific behavior, permissions, views, transactional table metadata, and partition-listing cost before adapting it to production.

**Deliverable:** `hive_tables.csv`, an inventory run manifest, and a short gap report listing unknowns and their resolution owners.

### Exercise 2 — copy one table from HDFS to MinIO and convert to Iceberg

**Goal:** Exercise a controlled copy/conversion on a small, non-sensitive table.

**Prerequisites:** Local Hadoop/Hive lab, MinIO, credentials provided securely, compatible S3A connector if using DistCp, Spark runtime, Iceberg runtime JARs/catalog configured for the selected Spark version, and a table with stable schema and a known row count.

**Procedure:**

1. Choose a table small enough for a local lab and record source path, schema, partition columns, row count, key profile, file count, and bytes.
2. Confirm the table is not actively being overwritten; take a snapshot or stop its writer for the copy boundary.
3. Choose one transfer path and document it. **DistCp path:** run the configured `hadoop distcp` command from Section 7.4 into a unique staging prefix, only after validating the installed S3A connector and MinIO endpoint. **Spark path:** use the configured Spark session to read the source table and write to a unique staging prefix using an explicitly selected, compatible file format. Do not assume a generic Spark installation can access MinIO without S3A/catalog configuration.
4. Copy into a unique staging prefix. Do not overwrite a production-looking prefix during the experiment.
5. Verify transfer status and compare the expected source/target file manifest. Do not treat successful command exit as complete data validation.
6. Read the copied staging files with an explicit schema and matching reader/SerDe assumptions (for example, ORC only when the source files are actually ORC), verify schema and record semantics, and create a new Iceberg table using the configured catalog. Alternatively, use the Section 7.5 direct Hive-to-Iceberg rewrite and label it as a direct rewrite rather than a separate raw-file copy. For this exercise, a rewrite into a new table is preferred if it makes the data ownership boundary clearer.
7. Run row-count, key-duplicate, null-profile, row-hash, and business-query comparisons.
8. Record runtime, bytes read/written, file count, output file sizes, and any retries as **observed lab measurements**. Do not extrapolate them directly to 500 TB.
9. Retain the source until all checks pass; then clean up staging artifacts only after recording the evidence and confirming no table metadata references them.

**Deliverable:** transfer log, source/target manifest, Iceberg table identifier, validation report, and a short explanation of why this was a rewrite or metadata conversion.

### Exercise 3 — write a validation script

**Goal:** Compare row counts, key-based hashes, and selected business queries.

1. Use `migration/validate_tables.py` from Section 10.3 as a starting point. Set `MIGRATION_RUN_ID`, `SOURCE_SNAPSHOT_OR_OFFSET`, `TARGET_SNAPSHOT_OR_COMMIT`, and `MIGRATION_CODE_VERSION` in the environment before running. It writes `experiments/07_migration/validation/table_validation_report.json` and exits with status 1 when row counts or schemas differ, duplicate keys prevent keyed comparison, or keyed rows mismatch. A successful process exit is necessary but not sufficient; review the report and ensure none of the evidence metadata remains `UNSET`.
2. Replace placeholder table names and key/compare columns.
3. Confirm the key is unique; if not, design a multiset comparison or correct the business key.
4. Add schema/nullability/decimal/timestamp checks required by the table contract.
5. Implement at least two business queries—for example, daily order count/net sales and latest customer status—and compare source/target outputs by deterministic keys.
6. Test the script against deliberately introduced defects: remove a row, duplicate a key, change a status, change a decimal, and shift a timestamp. Verify that the expected checks fail.
7. Save the report with run ID, snapshot boundary, code version, timestamp, and pass/fail outcome.

**Deliverable:** script, automated test cases, JSON/CSV result, and defect-detection notes.

### Exercise 4 — translate three HiveQL queries to Spark SQL

Use the three examples in Section 9.1 or select three queries from the lab that represent different patterns: aggregate, window function, and complex type/array expansion.

For each query:

- Save original HiveQL and translated Spark SQL under version control.
- Record required UDFs and type assumptions.
- Run both against the same immutable input boundary.
- Compare schema, row count, key coverage, and business aggregates; compare sorted row-level output when practical.
- Include edge cases: nulls, empty arrays, duplicate keys, timestamp boundaries, decimal rounding, ties in window ordering, and late corrections as relevant.
- Record query plans and runtime separately from correctness. A faster but incorrect query is a failed migration.

**Deliverable:** three query pairs, a comparison report, and a list of semantic changes or unresolved differences.

### Exercise 5 — parallel run for a simulated week and cutover report

**Goal:** Run old and new pipelines in parallel over seven simulated daily input intervals and produce an evidence-based cutover recommendation.

If no real historical dataset is available, generate deterministic synthetic data with a fixed seed and label every result `SIMULATED`. Do not present simulated values as observed production metrics.

For each of seven days, create an immutable day-specific input interval (for example, `event_date=2026-10-01` through `event_date=2026-10-07` in a lab fixture) and invoke the actual old and new pipeline entrypoints against the same interval. Record the exact commands/configuration, input manifest, output table/path, and run IDs; do not substitute a mock comparison for execution of the two pipeline paths. If the old Hadoop stack is unavailable, label the old side as a deterministic reference implementation rather than claiming that a legacy job ran. Use a fixed random seed for any generated fixture and store the generator version and seed in the report.

For each of seven days, record:

```text
run_date, source_snapshot_or_offset, source_job_version, target_job_version,
source_rows, target_rows, missing_keys, extra_keys, changed_rows,
business_metric_diffs, late_events, duplicate_events, source_runtime_seconds,
target_runtime_seconds, retries, target_lag_seconds, estimated_cost_basis,
security_checks, status, evidence_uri, reviewer
```

Inject at least these scenarios: late-arriving event, duplicate delivery, source correction to an earlier date, one failed target run followed by retry, and a schema-compatible new nullable column. Verify that the reconciliation logic identifies the intended behavior and that retries do not duplicate output.

**Cutover report sections:**

1. Scope and whether evidence is observed or simulated.
2. Source/target versions and exact input boundaries.
3. Seven-day result summary and daily exceptions.
4. Data-quality and business-query comparison.
5. Freshness/SLA and recovery behavior.
6. Security/governance test status.
7. Performance/cost observations and limitations.
8. Unresolved risks, owners, and due dates.
9. Recommendation: cut over, extend parallel run, remediate, or rollback.
10. Sign-off from technical and business owners.

A report with no discrepancies is not automatically a pass if the tests failed to cover deletes, late data, or semantic edge cases.

## 16. Common failure modes and controls

| Failure mode | Why it happens | Control |
|---|---|---|
| Copy starts before inventory | Data movement is mistaken for migration | Freeze inventory baseline and map every dataset to owner, consumers, and validation plan first |
| “All files copied” treated as success | File-level completion does not prove table semantics | Compare manifests, counts, keys, hashes, business queries, and metadata |
| Last-access timestamp invented from modification time | Different concepts are conflated | Label unavailable; use query/audit evidence with coverage limits |
| Bulk copy and CDC have a gap or overlap | Snapshot boundary is undefined | Define source snapshot/high-water mark and deduplicate/reconcile overlap |
| Deletes are missed | Append-only incremental process cannot express delete semantics | Use CDC/tombstones or full reconciliation policy |
| Retry duplicates output | Job side effects are not idempotent | Stable idempotency keys, deterministic partition overwrite, transactional merge, checkpoint commit after success |
| `-update` assumed to checksum all object contents | Cross-filesystem checksums and timestamps differ | Verify deployed semantics and perform independent data validation |
| Hive table “converted” but old writer continues | Metadata/file ownership and writer ownership are ambiguous | Fence old writer, document shared-file ownership, and validate catalog/write behavior |
| Partition scheme copied without review | Legacy layout optimized for different storage/engine | Base layout on query predicates, cardinality, file count, and update patterns |
| SQL results differ at time boundaries | Time zone, precision, casts, or window ties changed | Define canonical time/decimal semantics and add deterministic tie-breakers |
| HBase is treated as a file copy | Online point lookup and mutation contracts ignored | Load test target access patterns and preserve API/consistency requirements |
| IAM is assumed to replace Ranger directly | Resource, column, row, and tag policy semantics differ | Map effective policy and run positive/negative access tests through actual query paths |
| Target cost exceeds forecast | Idle compute, request costs, egress, logging, and duplicate runs omitted | Model full TCO and monitor cost per successful workload unit |
| Rollback loses new writes | Target accepted writes after source became stale | Fence writers, retain reverse CDC or reconcile target-only changes, rehearse routing reversal |
| Old cluster retired too early | Hidden consumer or audit requirement remains | Dependency scan, owner attestations, evidence retention, and formal decommission approval |

## 17. Operational checklists and checkpoints

### 17.1 Before migration

- [ ] Inventory data, jobs, dependencies, users, owners, SLAs, and access patterns.
- [ ] Mark every inventory field as collected, derived, estimated, or unavailable.
- [ ] Freeze the scope and source snapshot strategy.
- [ ] Select target storage, compute, table format, catalog, orchestration, and serving database from workload requirements.
- [ ] Verify version compatibility for Hadoop, Spark, JDK, connectors, Iceberg/Delta, catalog, and UDF dependencies.
- [ ] Define validation contracts and acceptable tolerances.
- [ ] Model transfer window, incremental changes, cost, and rollback.
- [ ] Approve identity, network, encryption, governance, lineage, and audit design.

### 17.2 Before cutover

- [ ] Bulk copy and incremental sync are reconciled to a documented source boundary.
- [ ] Critical tables and queries pass validation; exceptions are approved and time-bounded.
- [ ] Parallel run covers required operational/business cycles.
- [ ] Freshness, SLA, alerting, on-call, recovery, and cost dashboards are tested.
- [ ] Writer fencing and consumer routing are rehearsed.
- [ ] Rollback or forward-recovery path preserves target-only writes.
- [ ] Security and data owners have signed off.
- [ ] Change window, communications, and decision authority are confirmed.

### 17.3 Before decommission

- [ ] No active consumers or hidden integrations remain.
- [ ] Required records, logs, lineage, schemas, code, and evidence are archived.
- [ ] Retention, legal hold, deletion, and data-owner approval are complete.
- [ ] Rollback period has ended and recovery on target is proven.
- [ ] Credentials, keytabs, network routes, and unused privileges are retired safely.
- [ ] Hardware/support/license obligations are closed.
- [ ] Formal decommission record and residual-risk approval are stored.

### 17.4 Roadmap checkpoint

You are ready to move on when you can:

- [ ] Map every Hadoop component to a justified modern equivalent and explain why the mapping is not one-to-one.
- [ ] Produce an inventory and dependency graph for a real or lab environment.
- [ ] Plan data movement with a correct throughput estimate and a defined snapshot/CDC boundary.
- [ ] Distinguish metadata conversion from full rewrite and explain shared-file risks.
- [ ] Translate HiveQL and MapReduce workloads while preserving semantics and retry safety.
- [ ] Validate a migrated table using counts, keys/hashes, schema, nulls, and business queries.
- [ ] Explain freeze windows, dual-run evidence, rollback triggers, write fencing, and decommission gates.
- [ ] Estimate cloud TCO with explicit assumptions and sensitivity analysis.
- [ ] Produce a four-wave migration plan with dependencies, risks, validation, acceptance, rollback, and exit conditions.

## 18. Interview and design-review questions

1. Why is a 500 TB HDFS copy not the same as a 500 TB lakehouse migration?
2. When would you choose metadata conversion over a full rewrite of a Hive table? What are the shared-file risks?
3. How do you estimate a transfer window and account for utilization, file count, and incremental changes?
4. Why can DistCp `-update` miss or unnecessarily copy files across some filesystem combinations?
5. How would you prove that a target table has no missing or duplicated rows when there is no unique key?
6. How do you reconcile late-arriving events and source deletes during a bulk-copy-plus-CDC migration?
7. Which MapReduce semantics commonly break during a Spark rewrite?
8. What Oozie coordinator behaviors must be preserved when migrating to Airflow?
9. Why is HBase migration a serving-workload redesign rather than just an HDFS transfer?
10. Why is cloud IAM not automatically equivalent to Ranger policy behavior?
11. What makes rollback unsafe after target writes begin?
12. Which costs are often omitted from a cloud migration business case?
13. What evidence is required before decommissioning the old cluster?
14. How would you choose between a wave-based migration and a big-bang cutover?
15. Which facts in a migration report must be labeled as measured, inferred, estimated, or simulated?

## 19. Reference documentation and source traceability

### Roadmap sources

- `Roadmap_ptree.md` — authoritative project-tree path and lesson order.
- `roadmap-Hadoop-Ecosystem-and-Legacy-Big-Data.md` — authoritative Topic 07 syllabus, scale assumptions, five hands-on exercises, checkpoint, and common mistakes.
- Preceding lessons in this module: HDFS; YARN; MapReduce; Hive Metastore/HiveQL; HBase; Sqoop/Flume/Oozie. They provide the component knowledge reused throughout this lesson.

### Technical references to consult for the exact deployed versions

- Apache Hadoop DistCp Guide: <https://hadoop.apache.org/docs/current/hadoop-distcp/DistCp>
- Apache Iceberg — Hive table migration: <https://iceberg.apache.org/docs/nightly/hive-migration/>
- Apache Iceberg — table migration approaches: <https://github.com/apache/iceberg/blob/main/docs/docs/table-migration.md>
- Apache Iceberg — Spark procedures: <https://github.com/apache/iceberg/blob/main/docs/docs/spark-procedures.md>
- Delta Lake — migration/porting guide: <https://docs.delta.io/porting/>
- Delta Lake — table utility commands and conversion constraints: <https://docs.delta.io/delta-utility/>
- AWS Snowball Edge Developer Guide: <https://docs.aws.amazon.com/snowball/latest/developer-guide/>
- AWS large data migration planning: <https://docs.aws.amazon.com/snowball/latest/developer-guide/LargeDataMigration.html>
- Apache Spark SQL data sources and JDBC options: <https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html>
- Apache Airflow scheduling/timetable concepts: <https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/timetable.html>

These links are technical starting points, not a substitute for checking the release-specific documentation and support matrix for the exact platform, distribution, connector, catalog, and region being deployed. “Latest” or “nightly” documentation can describe features unavailable in a production release; pin and review the documentation for your actual versions.

---

**Final principle:** a Hadoop-to-cloud-lakehouse migration is complete only when the data, computation, table semantics, orchestration, security, governance, operating model, and business outcomes have been validated—and when rollback and decommissioning decisions are supported by evidence rather than assumptions.
