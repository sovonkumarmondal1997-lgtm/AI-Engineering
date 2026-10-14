# Roadmap — Module 2C.2: Hadoop Ecosystem and Legacy Big Data

This is the learning roadmap for the second module of Stage 2C, **Data
Engineering_3**. It tells you **what** to learn about the Hadoop ecosystem,
**in what order**, **how** to learn each topic, and **how to prove to
yourself** that you have learned it before you move on.

Almost every modern tool you learned in Stage 2 — Spark, Hive-style
metastores, Parquet and ORC, partitioned directory layouts, data lakes —
descends from Hadoop. Many large companies (banks, telecoms, retailers)
still run Hadoop clusters, and a data engineer will be asked to read,
maintain, or **migrate** them. You do not need to *build* new Hadoop
clusters in 2026, but you do need to read the architecture, understand why
it was designed that way, and know how to move its workloads to the cloud
lakehouse.

This module is deliberately about **understanding and migrating**, not
about adopting Hadoop for new projects.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain HDFS: NameNode, DataNodes, blocks, replication, rack awareness,
  and high availability — and read an `fsck` report.
- Explain YARN: ResourceManager, NodeManagers, containers, schedulers, and
  queues; and run Spark on YARN.
- Explain the MapReduce model (map, shuffle, reduce) and why Spark replaced
  it for most workloads.
- Use Hive: the metastore, HiveQL, partitioned and bucketed tables, ORC,
  and execution engines (Tez, Spark).
- Explain HBase's data model and when it fits.
- Recognise legacy tooling: Sqoop, Flume, Oozie, and their modern
  replacements.
- Plan and execute a **Hadoop-to-cloud-lakehouse migration** with
  validation and cutover.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Linux shell, permissions, processes | Stage 0; Stage 2B — Module 2B.2 | Operating cluster nodes and reading logs |
| Distributed computing, Spark, shuffle, partitioning | Stage 2 — Module 2.14 | MapReduce and YARN are the ancestors of these ideas |
| Parquet/ORC, partitioning, small-files problem | Stage 2 — Module 2.5 | HDFS block size and file layout |
| SQL, window functions, EXPLAIN | Stage 2 — Module 2.6 | HiveQL builds on it |
| Lakehouse table formats, catalogs | Stage 2 — Module 2.15 | The migration target |
| Object storage and cloud platforms | Stage 2 — Module 2.17; Stage 2B — Modules 2B.3–2B.4 | S3/ADLS/GCS replace HDFS |
| Docker Compose | Stage 2B — Module 2B.1 | Running a small cluster locally |
| Data reconciliation | Stage 2 — Module 2.11 | Validating a migration |

**Tools needed:**

- Docker Compose with a small Hadoop stack (HDFS NameNode + 2–3 DataNodes,
  YARN, Hive Metastore + HiveServer2, optionally HBase). A prebuilt
  community compose project is fine.
- Python 3.12+ in a `uv` project: `uv add pyspark pyhive hdfs pyarrow
  pytest`.
- MinIO (from earlier modules) as the migration target.

**A note on versions:** Hadoop 3.x is the line in use; most distributions
(Cloudera, older HDP/CDH) are legacy or end-of-life. Many tutorials show
Hadoop 2. Check the version before you trust a diagram.

---

## 3. How the module is organised

The seven topics are grouped into four phases. Work through them **in
order**.

```text
Phase A — Storage and Resource Management           (Basics → Intermediate)
  01 HDFS architecture: NameNode, DataNodes, and replication
  02 YARN resource management

Phase B — Processing                                (Intermediate)
  03 MapReduce and why Spark replaced it
  04 Hive: metastore and HiveQL

Phase C — Wide-Column and Legacy Tooling            (Intermediate)
  05 HBase and wide-column on HDFS
  06 Sqoop, Flume, and Oozie: legacy tooling

Phase D — Moving Forward                            (Advanced)
  07 Migrating Hadoop workloads to a cloud lakehouse

Consolidate
  Module mini-project: plan and rehearse a Hadoop migration
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07
store  share  old   SQL on  random legacy  move
data   the    way   Hadoop  access glue    off it
       cluster
```

Why this order:

- HDFS (01) and YARN (02) are the base layers everything runs on.
- MapReduce (03) is the original compute model; Hive (04) put SQL on top.
- HBase (05) and the legacy tools (06) complete the picture of a typical
  cluster.
- Migration (07) only makes sense once you know every component you are
  moving.

---

## 4. Suggested schedule

About **4 weeks at 6–8 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — HDFS · Topic 02 — YARN |
| 2 | Topic 03 — MapReduce · Topic 04 — Hive |
| 3 | Topic 05 — HBase · Topic 06 — Sqoop/Flume/Oozie |
| 4 | Topic 07 — migration · mini-project |

---

## 5. How to study every topic (the legacy-system loop)

```text
Read → Draw the architecture → Predict failures → Run it → Inspect it
→ Break a node → Compare with the cloud equivalent → Write it down
→ Explain aloud
```

1. **Read** the topic file once, fully.
2. **Draw** the components and the data/control flow.
3. **Predict** what happens when a node, a disk, or the master fails.
4. **Run it** in the Docker cluster; use the web UIs (NameNode 9870,
   ResourceManager 8088).
5. **Inspect** with `hdfs dfs`, `hdfs fsck`, `yarn application`, `beeline`.
6. **Break a node** and watch recovery.
7. **Compare** with the modern equivalent (object storage, Kubernetes,
   Iceberg, Airflow).
8. **Write it down** in `module-2c2-notes.md`.
9. **Explain aloud** why the design made sense in 2010 and what replaced it.

Keep one `hadoop_lab/` project:

```text
hadoop_lab/
├── docker-compose.yml   # HDFS, YARN, Hive Metastore + HiveServer2, optional HBase, MinIO
├── data/                # sample datasets (logs, orders)
├── hive/                # HiveQL scripts
├── jobs/                # MapReduce (streaming) and Spark jobs
├── migration/           # inventory, copy, validation scripts
└── tests/
```

---

## 6. Phase A — Storage and Resource Management (Basics → Intermediate)

### Topic 01 — [HDFS architecture: NameNode, DataNodes, and replication](01-hdfs-architecture-namenode-datanodes-and-replication.md)

**Why it comes first:** HDFS is the storage layer of every Hadoop
workload. Its design — large blocks, replication, a central namespace —
explains the small-files problem, partitioned layouts, and why object
storage later became attractive.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why HDFS exists: very large files, commodity hardware, sequential reads, "move compute to data" |
| Basics | **Blocks** (128 MB default), **NameNode** (metadata) and **DataNodes** (blocks); the read and write path |
| Basics | The `hdfs dfs` command line: `ls`, `put`, `get`, `cat`, `du`, `rm`, `chmod` |
| Intermediate | **Replication** (default 3), rack awareness, and re-replication after a failure |
| Intermediate | The NameNode in memory: fsimage, edit log, checkpointing; why millions of small files hurt |
| Intermediate | Permissions, ACLs, quotas, and trash; snapshots |
| Intermediate | Reading `hdfs fsck`, `dfsadmin -report`, and the NameNode UI |
| Intermediate | Python access: WebHDFS, `hdfs`/`pyarrow.fs.HadoopFileSystem`, Spark |
| Advanced | **High availability**: active/standby NameNodes, JournalNodes, ZooKeeper failover; federation |
| Advanced | **Erasure coding** (Hadoop 3) vs replication: storage vs reconstruction cost |
| Advanced | Balancer, disk balancer, decommissioning nodes, and safe mode |
| Advanced | Security: Kerberos, delegation tokens, encryption zones — awareness |
| Advanced | HDFS vs object storage: consistency, rename semantics, cost, and why the industry moved |

**How to learn it**

1. Read the topic file.
2. Draw the write path of a 300 MB file with replication 3 across racks.
3. Compute NameNode memory for 100 million small files vs 1 million large
   files (rule of thumb ~150 bytes per object).

**Hands-on exercise — `experiments/01_hdfs/`**

1. Upload a large file; use `fsck -files -blocks -locations` to see where
   blocks live.
2. Stop a DataNode and watch under-replicated blocks recover.
3. Create 50,000 tiny files and observe the cost; compact them into a
   few large files.
4. Set a quota and trigger a quota error.
5. Compare reading the same Parquet from HDFS and MinIO with Spark.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain blocks, NameNode, and DataNodes.
- [ ] Trace a read and a write.
- [ ] Explain replication, rack awareness, and recovery.
- [ ] Explain why small files hurt HDFS.
- [ ] Explain HA and erasure coding at a high level.

**Common mistakes:** thinking HDFS suits many small files; ignoring the
NameNode as a single point of memory; forgetting that `hdfs dfs -rm`
moves to trash first.

---

### Topic 02 — [YARN resource management](02-yarn-resource-management.md)

**Why here:** YARN decides who gets CPU and memory in a Hadoop cluster.
Most "my job is stuck" problems on legacy clusters are YARN problems.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The problem YARN solves: sharing one cluster between many jobs and frameworks |
| Basics | **ResourceManager**, **NodeManagers**, **ApplicationMaster**, and **containers** (vcores + memory) |
| Basics | Submitting and monitoring: `yarn application -list/-status/-kill`, the ResourceManager UI, logs |
| Intermediate | **Schedulers**: FIFO, **Capacity** and **Fair**; queues, capacities, and preemption |
| Intermediate | Running **Spark on YARN**: client vs cluster mode, executor sizing, dynamic allocation (links to Module 2.14) |
| Intermediate | Container memory limits and the common "container killed by YARN for exceeding memory limits" failure |
| Intermediate | Log aggregation and debugging failed applications |
| Advanced | Resource tuning: min/max allocation, vcore ratios, overhead memory, queue design for teams and SLAs |
| Advanced | Multi-tenancy, queue ACLs, user limits, and noisy-neighbour control |
| Advanced | Node labels, GPU scheduling — awareness |
| Advanced | YARN vs Kubernetes as the data-workload scheduler; why many teams moved (Stage 2 Module 2.18) |

**How to learn it**

1. Read the topic file.
2. Draw the lifecycle of a Spark-on-YARN application from submit to
   completion.
3. For a 10-node cluster, design two queues (ETL guaranteed 60%, ad hoc
   40%) with the Capacity scheduler.

**Hands-on exercise — `experiments/02_yarn/`**

1. Submit a Spark job to YARN in client and cluster modes; compare logs.
2. Set executor memory too low on purpose and read the YARN kill message;
   fix it with overhead settings.
3. Configure two queues; run jobs in both and observe sharing and
   preemption.
4. Write a short runbook: "my application is stuck in ACCEPTED".

**Checkpoint:**

- [ ] Name the YARN components and their jobs.
- [ ] Choose Capacity vs Fair scheduling.
- [ ] Size executors for YARN.
- [ ] Debug a failed or pending application.

**Common mistakes:** giving Spark more memory than a container can hold;
ignoring memory overhead; one giant queue for all teams; reading only the
client log, not the aggregated container logs.

---

## 7. Phase B — Processing (Intermediate)

### Topic 03 — [MapReduce and why Spark replaced it](03-mapreduce-model-and-why-spark-replaced-it.md)

**Why here:** MapReduce is the idea behind "shuffle", "partition", and
"combiner" in every later engine. Existing jobs also still run in
production and need to be understood before they are rewritten.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The model: **map** → shuffle/sort → **reduce**; key-value pairs; word count |
| Basics | Input splits, mappers, reducers, and output files (`part-r-00000`) |
| Basics | Running a job: Hadoop Streaming with Python (`mapper.py`, `reducer.py`) |
| Intermediate | **Combiners**, partitioners, and custom sort/grouping; why the shuffle dominates cost |
| Intermediate | Joins in MapReduce: map-side (broadcast) vs reduce-side joins; secondary sort |
| Intermediate | Fault tolerance: task retries, speculative execution, and the on-disk shuffle |
| Intermediate | Python libraries (`mrjob`) and their limits |
| Advanced | Why Spark replaced it: in-memory pipelines, DAG scheduling, lazy evaluation, richer APIs, no disk write between every stage |
| Advanced | Mapping MapReduce concepts to Spark: `reduceByKey`, `groupByKey`, narrow vs wide dependencies |
| Advanced | Reading legacy MapReduce code (Java) well enough to port its logic |
| Advanced | Where MapReduce-like batch processing still wins: very large, simple, I/O-bound jobs — awareness |

**How to learn it**

1. Read the topic file.
2. By hand, run word count on three small text lines: map output, sort,
   reduce.
3. Compare a MapReduce word count and a PySpark word count line by line.

**Hands-on exercise — `experiments/03_mapreduce/`**

1. Write word count with Hadoop Streaming in Python; run it on HDFS.
2. Add a combiner and compare shuffle bytes.
3. Implement a reduce-side join of orders and customers.
4. Port the same logic to PySpark DataFrames; compare runtime, code size,
   and number of stages.

**Checkpoint:**

- [ ] Explain map, shuffle, and reduce with an example.
- [ ] Explain combiners and joins in MapReduce.
- [ ] Explain exactly why Spark is usually faster.
- [ ] Port a simple MapReduce job to Spark.

**Common mistakes:** thinking MapReduce is "wrong" rather than superseded;
forgetting the shuffle cost; writing reducers that need all values in
memory.

---

### Topic 04 — [Hive: metastore and HiveQL](04-hive-metastore-and-hiveql.md)

**Why here:** Hive brought SQL to Hadoop, and its **metastore** survives
everywhere — Spark, Trino, Athena, Glue, and Unity Catalog all speak its
language. Hive-style partitioned tables are the layout you will find in
most legacy lakes.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What Hive is: SQL-on-Hadoop translating queries into jobs; schema-on-read |
| Basics | **Databases, tables, and the metastore**: metadata separate from data; the relational backing database |
| Basics | **Managed vs external tables**; `CREATE EXTERNAL TABLE`, `LOCATION`; `LOAD DATA` and `INSERT` |
| Basics | Connecting: `beeline`, HiveServer2, JDBC, and Python (`pyhive`) |
| Intermediate | HiveQL: joins, aggregations, windowing, lateral view/explode, complex types (array, map, struct) |
| Intermediate | **Partitioning** (static and dynamic) and **bucketing**; partition pruning |
| Intermediate | **File formats**: text, SequenceFile, Avro, **ORC**, Parquet; SerDes |
| Intermediate | Execution engines: MapReduce → **Tez** → Spark; reading `EXPLAIN` |
| Intermediate | Statistics (`ANALYZE TABLE`) and the cost-based optimizer; `MSCK REPAIR TABLE` |
| Advanced | **ACID tables** in Hive (transactional ORC), compaction, and the pain of small deltas |
| Advanced | Performance: vectorisation, map joins, skew handling, partition design mistakes |
| Advanced | **Hive metastore as the shared catalog** for Spark, Trino, Presto, and cloud services (Glue as a managed equivalent, Module 2.15) |
| Advanced | Hive vs modern table formats (Iceberg, Delta): what Hive tables lack |
| Advanced | Security: Ranger, authorisation models — awareness |

**How to learn it**

1. Read the topic file.
2. Create an external table over existing Parquet files and query it.
3. Compare a partitioned and unpartitioned version of the same table with
   `EXPLAIN`.

**Hands-on exercise — `experiments/04_hive/`**

1. Create an external ORC table with dynamic partitions by date; load a
   month of data.
2. Run a query with and without partition pruning; compare scanned data.
3. Add new partition directories manually and fix visibility with
   `MSCK REPAIR TABLE`.
4. Point Spark and Trino at the same metastore and query the same table.
5. Convert the table to Iceberg and list what improves.

**Checkpoint:**

- [ ] Explain the metastore and why it outlives Hive.
- [ ] Create managed and external partitioned tables.
- [ ] Choose a file format and partition scheme.
- [ ] Read an `EXPLAIN` plan.
- [ ] Explain Hive ACID's limits vs Delta/Iceberg.

**Common mistakes:** too many partitions; forgetting to repair/refresh
partitions; dropping a managed table and deleting data; using text files
for large tables.

---

## 8. Phase C — Wide-Column and Legacy Tooling (Intermediate)

### Topic 05 — [HBase and wide-column on HDFS](05-hbase-and-wide-column-on-hdfs.md)

**Why here:** HBase gave Hadoop random, low-latency reads and writes
(Module 2C.1 covered the same family via Cassandra). It still sits under
many legacy systems.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The HBase data model: tables, **row keys**, column families, qualifiers, versioned cells |
| Basics | Architecture: HMaster, RegionServers, regions, ZooKeeper, HDFS as storage |
| Basics | The shell: `create`, `put`, `get`, `scan`, `delete` |
| Intermediate | **Row key design**: sortedness, avoiding hotspots (salting, hashing, reversing), composite keys |
| Intermediate | The write path (WAL, MemStore, HFile) and read path (BlockCache, Bloom filters); compactions and splits |
| Intermediate | Python access via Thrift/`happybase` |
| Advanced | Region balancing, hot regions, and tuning; coprocessors and filters |
| Advanced | Phoenix (SQL on HBase) — awareness; Spark-HBase connectors |
| Advanced | HBase vs Cassandra vs DynamoDB: consistency model, operations, cost |
| Advanced | Migrating HBase data: snapshots, `ExportSnapshot`, and bulk loads into Bigtable, Cassandra, DynamoDB, or the lakehouse |

**How to learn it**

1. Read the topic file.
2. Design a row key for "events by user, newest first" and test for
   hotspots.
3. Map HBase concepts to Cassandra and DynamoDB (Module 2C.1).

**Hands-on exercise — `experiments/05_hbase/`**

1. Create a table with two column families; insert and scan data.
2. Load sequential row keys and observe a hot region; fix with salting.
3. Export a snapshot and read it from Spark.
4. Write a one-page migration note for moving the table to another store.

**Checkpoint:**

- [ ] Explain the HBase data model and architecture.
- [ ] Design a row key that avoids hotspots.
- [ ] Compare HBase with Cassandra and DynamoDB.
- [ ] Outline how to migrate HBase data.

**Common mistakes:** monotonically increasing row keys; too many column
families; treating HBase as a general SQL store.

---

### Topic 06 — [Sqoop, Flume, and Oozie: legacy tooling](06-sqoop-flume-and-oozie-legacy-tooling.md)

**Why here:** these tools carried ingestion and scheduling in the Hadoop
era. You will meet them in old jobs; the skill is recognising what each did
and replacing it cleanly.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Sqoop**: bulk transfer between relational databases and HDFS/Hive; import/export, `--split-by`, incremental modes |
| Basics | **Flume**: sources, channels, sinks for streaming logs into HDFS |
| Basics | **Oozie**: XML workflows, coordinators (time/data triggers), and bundles |
| Intermediate | Reading and documenting an existing Sqoop command, Flume config, and Oozie workflow |
| Intermediate | What each replaced and its weaknesses: parallelism skew, no schema evolution, fragile XML, weak retries |
| Intermediate | Modern replacements: Spark JDBC, dlt/Airbyte/managed connectors (Module 2.9); Kafka and Kafka Connect/Fluent Bit (Module 2.16); Airflow/Dagster (Module 2.13) |
| Advanced | Building an **inventory** of legacy jobs: sources, targets, schedules, owners, and SLAs |
| Advanced | Translating an Oozie workflow into an Airflow DAG without changing behaviour |
| Advanced | Translating Sqoop incremental imports into watermark-based extraction with idempotent loads |
| Advanced | Knowing when not to rewrite: wrap, freeze, or retire |

**How to learn it**

1. Read the topic file.
2. Read three sample legacy configs and write a plain-English description
   of each.
3. For each, name today's replacement and the risk of the swap.

**Hands-on exercise — `experiments/06_legacy_tooling/`**

1. Run a Sqoop-style import in a lab (or emulate with Spark JDBC) with
   parallel splits.
2. Translate a sample Oozie workflow with a coordinator into an Airflow
   DAG.
3. Replace a Flume log pipeline with a small Kafka-based pipeline.
4. Produce a legacy job inventory spreadsheet for a pretend cluster.

**Checkpoint:**

- [ ] Describe what Sqoop, Flume, and Oozie each did.
- [ ] Name a modern replacement for each.
- [ ] Translate a simple Oozie workflow into a DAG.
- [ ] Build a job inventory.

**Common mistakes:** rewriting without documenting current behaviour;
losing incremental state during the swap; ignoring implicit dependencies
between jobs.

---

## 9. Phase D — Moving Forward (Advanced)

### Topic 07 — [Migrating Hadoop workloads to a cloud lakehouse](07-migrating-hadoop-workloads-to-cloud-lakehouse.md)

**Why it comes last:** this is the most valuable skill in the module.
Migrations are common, risky, and expensive — and they use everything
above.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why migrate: cost, scarce skills, end-of-life distributions, elasticity, separation of storage and compute |
| Basics | Target architectures: object storage + Spark/Databricks/EMR + Iceberg/Delta + a catalog |
| Basics | The component map: HDFS → S3/ADLS/GCS; YARN → Kubernetes/serverless; Hive → Iceberg/Delta + Glue/Unity; Oozie → Airflow; HBase → Bigtable/DynamoDB/Cassandra |
| Intermediate | **Discovery and inventory**: datasets, sizes, access patterns, jobs, dependencies, users, and SLAs |
| Intermediate | **Data movement**: `DistCp`, network transfer, Snowball/Data Box-style appliances, and incremental syncs; throughput planning |
| Intermediate | **Code migration**: HiveQL to Spark SQL/dbt, MapReduce to Spark, UDF rewrites, and dependency changes |
| Intermediate | Strategies: lift-and-shift, replatform, refactor; wave-based vs big-bang; strangler pattern |
| Intermediate | Table conversion: Hive tables → Iceberg/Delta (in place vs rewrite), partition redesign |
| Advanced | **Validation**: row counts, checksums, column statistics, and query-result diffing between old and new; running in parallel |
| Advanced | **Cutover**: freeze windows, dual-run, rollback plans, and decommissioning criteria |
| Advanced | Security and governance migration: Ranger → IAM/Lake Formation/Unity Catalog; Kerberos → cloud identity |
| Advanced | Cost modelling: TCO of on-prem vs cloud, egress, storage tiers, and avoiding cost surprises (Stage 2 Module 2.21) |
| Advanced | Organisational side: training, ownership, communication, and defining "done" |

**How to learn it**

1. Read the topic file.
2. Build a component-mapping table for a pretend cluster of 500 TB, 300
   Hive tables, 120 Oozie workflows, and 2 HBase tables.
3. Sketch a four-wave migration plan with risks and validation per wave.

**Hands-on exercise — `experiments/07_migration/`**

1. Inventory the lab cluster's Hive tables with a script (name, size,
   partitions, format, last access).
2. Copy one table from HDFS to MinIO with `DistCp` or Spark; convert it to
   Iceberg.
3. Write a validation script that compares counts, checksums of key
   columns, and a set of business queries between old and new.
4. Translate three HiveQL queries to Spark SQL and compare results.
5. Run old and new in parallel for a week of simulated data and produce a
   cutover report.

**Checkpoint:**

- [ ] Map each Hadoop component to its modern equivalent.
- [ ] Plan discovery, movement, code migration, validation, and cutover.
- [ ] Validate a migrated table rigorously.
- [ ] Explain rollback and decommissioning criteria.
- [ ] Estimate the cost of the target platform.

**Common mistakes:** migrating data before inventorying jobs; no parallel
run; forgetting permissions and governance; underestimating egress and
small-file overhead; treating migration as purely a copy job.

---

## 10. Module mini-project — plan and rehearse a Hadoop migration

**Goal:** migrate a small but realistic Hadoop lab to the lakehouse.

**Requirements**

1. A source lab: HDFS with partitioned ORC tables behind a Hive metastore,
   a MapReduce (Streaming) job, a Sqoop-style import, and an Oozie-style
   daily workflow.
2. A written **inventory** and **component-mapping** document.
3. A migration of at least three tables to MinIO as Iceberg/Delta with
   partitions redesigned where needed.
4. The MapReduce job ported to Spark; the workflow rebuilt as an Airflow
   DAG.
5. An automated **validation suite** comparing source and target, and a
   parallel-run report.
6. A cutover plan with rollback and decommissioning criteria.

**Done when** every migrated table passes validation, the DAG reproduces
the old workflow's outputs, and your plan could be handed to a team that
has never seen the source cluster.

---

## 11. Module self-assessment — exit criteria

You have completed this module when you can do all of the following
**without notes**:

- [ ] Explain HDFS and YARN architecture and failure handling.
- [ ] Explain MapReduce and why Spark superseded it.
- [ ] Create and tune partitioned Hive tables and explain the metastore's
      continuing role.
- [ ] Explain HBase and design a row key.
- [ ] Recognise and replace Sqoop, Flume, and Oozie.
- [ ] Plan, execute, and validate a Hadoop-to-lakehouse migration.

---

## 12. Recommended reading and references

- *Hadoop: The Definitive Guide* — Tom White.
- Apache Hadoop, Hive, and HBase official documentation.
- Cloud migration guides: AWS EMR/Hadoop migration, Azure HDInsight
  migration, Google Dataproc migration, Databricks Hadoop migration.
- The original GFS and MapReduce papers (for the "why").

---

## 13. Where this module leads

- **Modules 2C.3–2C.5** show the cloud warehouses and platforms that
  replaced most Hadoop clusters.
- **Module 2C.7** covers modern query engines (Trino) that still use the
  Hive metastore.
- **Module 2C.8** places migrations inside wider platform strategy
  (build vs buy, vendor selection).
