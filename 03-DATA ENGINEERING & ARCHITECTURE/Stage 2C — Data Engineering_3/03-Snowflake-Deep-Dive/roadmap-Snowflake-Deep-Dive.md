# Roadmap — Module 2C.3: Snowflake Deep Dive

This is the learning roadmap for the third module of Stage 2C, **Data
Engineering_3**. It tells you **what** to learn about Snowflake, **in what
order**, **how** to learn each topic, and **how to prove to yourself** that
you have learned it before you move on.

Snowflake is one of the most widely used cloud data platforms. Stage 2
introduced cloud warehouses at overview level (Module 2.17). This module
goes deep: how Snowflake separates storage, compute, and services; how it
loads, transforms, secures, shares, and bills; and how to run it
efficiently.

Snowflake rewards engineers who understand **what it does under the
hood** — micro-partitions, warehouse sizing, caching, and credits — because
the same SQL can cost ten times more or less depending on those choices.
You will write mostly SQL, with Python through **Snowpark** and the
connector.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain Snowflake's three-layer architecture and how it differs from
  Redshift/BigQuery/Spark.
- Size, configure, and govern **virtual warehouses** (including
  multi-cluster and auto-suspend).
- Explain **micro-partitions**, clustering, and pruning, and tune a large
  table.
- Load data with **stages**, `COPY INTO`, and **Snowpipe**, and handle load
  errors and idempotency.
- Build incremental pipelines with **streams, tasks, and dynamic tables**.
- Write **Snowpark Python** code and UDFs/UDTFs/stored procedures.
- Use **Time Travel, Fail-safe, and zero-copy cloning** for recovery and
  testing.
- Secure data with **RBAC**, masking policies, row access policies, and
  tags.
- Share data with **secure sharing** and the Marketplace.
- Monitor and control cost with resource monitors, account usage views, and
  query profiling.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| SQL, CTEs, window functions, MERGE | Stage 2 — Module 2.6 | Snowflake is SQL-first |
| Columnar formats, partitioning, pruning | Stage 2 — Module 2.5 | Micro-partitions are the same ideas, automated |
| Dimensional modelling, SCDs | Stage 2 — Module 2.8 | What you build in Snowflake |
| Incremental loads, CDC, MERGE patterns | Stage 2 — Modules 2.9, 2.12 | Streams and tasks implement them |
| Orchestration | Stage 2 — Module 2.13 | Tasks vs external orchestrators |
| Cloud object storage, IAM | Stage 2 — Module 2.17; Stage 2B — 2B.3 | Stages, storage integrations |
| Access control, PII masking | Stage 2 — Module 2.20 | Policies and governance |
| Cost thinking | Stage 2 — Module 2.21 | Credits and resource monitors |
| Python DB connectivity | Stage 2 — Module 2.7 | The Snowflake connector |

**Tools needed:**

- A **Snowflake trial or free account** (no local install exists). Create
  a dedicated database and a small warehouse; set a **resource monitor**
  on day one.
- Python 3.12+ in a `uv` project: `uv add snowflake-connector-python
  snowflake-snowpark-python pandas pytest`.
- An object-storage bucket (S3/GCS/Azure) or the internal stages for
  loading practice.
- SnowSQL or the Snowflake CLI, and Snowsight (the web UI).

**A note on cost:** Snowflake bills by the second for running warehouses.
Always set `AUTO_SUSPEND`, use `X-SMALL`, and drop what you create.

---

## 3. How the module is organised

The ten topics are grouped into five phases. Work through them **in order**.

```text
Phase A — Architecture and Compute                  (Basics → Intermediate)
  01 Architecture: storage, compute, and services
  02 Virtual warehouses: sizing and scaling

Phase B — Storage Internals and Loading             (Intermediate)
  03 Micro-partitions, clustering, and pruning
  04 Stages, COPY INTO, and Snowpipe

Phase C — Transformation and Programmability        (Intermediate → Advanced)
  05 Streams, tasks, and dynamic tables
  06 Snowpark Python and UDFs

Phase D — Data Protection and Governance            (Intermediate → Advanced)
  07 Time Travel, cloning, and zero-copy
  08 RBAC, masking policies, and row access

Phase E — Sharing and Cost                          (Advanced)
  09 Data sharing and the Marketplace
  10 Cost monitoring and resource monitors

Consolidate
  Module mini-project: an incremental ELT platform on Snowflake
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09 ► 10
shape  size  how   get   keep  code  safety secure share  pay
of it  it    data  data  it    in    nets   it     it     less
             is    in    fresh Python
             stored
```

Why this order:

- Architecture (01) and warehouses (02) explain compute and cost.
- Micro-partitions (03) explain performance; loading (04) fills the tables.
- Streams/tasks (05) and Snowpark (06) transform it.
- Time Travel (07) and RBAC (08) protect it; sharing (09) distributes it.
- Cost (10) ties everything together with measurement.

---

## 4. Suggested schedule

About **5 weeks at 8 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — architecture · Topic 02 — warehouses |
| 2 | Topic 03 — micro-partitions · Topic 04 — loading |
| 3 | Topic 05 — streams, tasks, dynamic tables · Topic 06 — Snowpark |
| 4 | Topic 07 — Time Travel/cloning · Topic 08 — RBAC and policies |
| 5 | Topic 09 — sharing · Topic 10 — cost · mini-project |

---

## 5. How to study every topic (the warehouse loop)

```text
Read → Predict cost and performance → Run it → Open the Query Profile
→ Change one thing → Re-run → Compare credits and time → Write it down
→ Explain aloud
```

1. **Read** the topic file once, fully.
2. **Predict** how many micro-partitions will be scanned, how long the
   query will take, and its credit cost.
3. **Run it** on a small warehouse.
4. Open the **Query Profile**; note scanned partitions, spilling, and
   bytes scanned.
5. **Change one variable** (warehouse size, clustering key, query shape).
6. **Compare** using `QUERY_HISTORY` and `WAREHOUSE_METERING_HISTORY`.
7. **Write it down** in `module-2c3-notes.md`.
8. **Explain aloud** why it behaved that way.

Keep one `snowflake_lab/` project:

```text
snowflake_lab/
├── sql/                  # numbered, idempotent scripts (databases, roles, tables, tasks)
├── python/               # Snowpark and connector code
├── data/                 # sample files (CSV, JSON, Parquet) for loading
├── governance/           # roles, policies, tags
├── cost/                 # usage and monitoring queries
└── tests/
```

---

## 6. Phase A — Architecture and Compute (Basics → Intermediate)

### Topic 01 — [Snowflake architecture: storage, compute, and services](01-snowflake-architecture-storage-compute-and-services.md)

**Why it comes first:** every Snowflake feature and cost follows from the
separation of storage, compute, and cloud services.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The three layers: **database storage**, **virtual warehouses (compute)**, **cloud services** (metadata, optimiser, security, transactions) |
| Basics | Accounts, regions, clouds, editions; organisations and multiple accounts |
| Basics | The object hierarchy: account → database → schema → table/view/stage/etc. |
| Basics | Using Snowsight, SnowSQL, the Snowflake CLI, and a Python connector session |
| Intermediate | Table types: permanent, temporary, transient, external, Iceberg; views, secure views, materialised views |
| Intermediate | Data types including `VARIANT`, `OBJECT`, `ARRAY` for semi-structured data; the `FLATTEN` function |
| Intermediate | The three **caches**: result cache, local disk cache (warehouse), and metadata cache |
| Intermediate | Comparison with Redshift, BigQuery, Databricks SQL, and Spark: shared-nothing vs decoupled storage and compute |
| Advanced | Query lifecycle: parse → compile → optimise → execute; where cloud services credits come from |
| Advanced | Account-level structure for dev/test/prod: databases per environment vs accounts per environment |
| Advanced | Snowflake on Iceberg and open table formats; Polaris/Open Catalog — awareness |
| Advanced | Snowflake features beyond the warehouse: Cortex AI, Streamlit, native apps — awareness |

**How to learn it**

1. Read the topic file.
2. Draw the three layers and mark what each charges for.
3. Run a query twice and prove the result cache served the second run.

**Hands-on exercise — `experiments/01_architecture/`**

1. Create a database, schemas, transient and permanent tables; compare
   their storage behaviour.
2. Load JSON into a `VARIANT` column and query nested fields with `:` and
   `FLATTEN`.
3. Prove each cache by running a query, resuming a suspended warehouse, and
   re-running.
4. Write a one-page comparison of Snowflake and one other platform you
   know.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain the three layers and what each costs.
- [ ] Choose a table type.
- [ ] Query semi-structured data.
- [ ] Explain the three caches.

**Common mistakes:** treating Snowflake like a traditional database with
indexes; ignoring the result cache when benchmarking; mixing environments
in one schema.

---

### Topic 02 — [Virtual warehouses: sizing and scaling](02-virtual-warehouses-sizing-and-scaling.md)

**Why here:** the warehouse is where credits are spent. Right-sizing and
isolating workloads is the biggest cost and performance lever.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What a virtual warehouse is; T-shirt sizes (XS → 6XL) and the credit-per-hour doubling rule |
| Basics | `CREATE WAREHOUSE`, `AUTO_SUSPEND`, `AUTO_RESUME`, `INITIALLY_SUSPENDED`; billing per second with a 60-second minimum |
| Basics | Scaling **up** (larger size for complex queries) vs scaling **out** (more clusters for concurrency) |
| Intermediate | **Multi-cluster warehouses**: min/max clusters, standard vs economy scaling policy, queueing |
| Intermediate | Workload isolation: separate warehouses for ETL, BI, data science, and ad hoc |
| Intermediate | Reading the Query Profile: spilling to local/remote storage, queued time, and when a bigger warehouse helps |
| Intermediate | Timeouts, statement limits, and query tags for attribution |
| Advanced | Warehouse sizing methodology: test the same workload at several sizes and compare cost per query, not time alone |
| Advanced | **Query Acceleration Service**, **Search Optimization Service**, and when each pays off |
| Advanced | Gen2 and other warehouse types, Snowpark-optimised warehouses (large memory), and serverless compute for tasks — awareness |
| Advanced | Concurrency design for BI: caching, result reuse, and per-team warehouses with budgets |

**How to learn it**

1. Read the topic file.
2. Compute the credit cost of the same job on XS, S, M, L assuming runtime
   halves each step — then find where it does not.
3. Design a warehouse layout for a team of ETL, BI, and ML users.

**Hands-on exercise — `experiments/02_warehouses/`**

1. Run one heavy query on XS through L; record time, spilling, and credits.
2. Run 30 concurrent small queries and compare a single cluster with a
   multi-cluster warehouse.
3. Set auto-suspend to 60 seconds and measure the saving over a day of
   bursty use.
4. Produce a warehouse design document with names, sizes, and policies.

**Checkpoint:**

- [ ] Explain credits and the doubling rule.
- [ ] Choose scale-up vs scale-out.
- [ ] Read spilling in the Query Profile.
- [ ] Design isolated warehouses for workloads.

**Common mistakes:** one big warehouse for everyone; no auto-suspend;
scaling up when the query is badly written; judging size by runtime only.

---

## 7. Phase B — Storage Internals and Loading (Intermediate)

### Topic 03 — [Micro-partitions, clustering, and pruning](03-micro-partitions-clustering-and-pruning.md)

**Why here:** Snowflake has no indexes you manage. Performance on large
tables is decided by how data is laid out in micro-partitions and how well
queries prune them.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Micro-partitions**: immutable, compressed, columnar units of ~50–500 MB uncompressed, created automatically |
| Basics | Metadata per partition (min/max, counts) and **pruning** with `WHERE` filters |
| Basics | Natural ordering by load order and why date-ordered loads prune well |
| Intermediate | Clustering **depth** and **overlap**; `SYSTEM$CLUSTERING_INFORMATION` |
| Intermediate | **Clustering keys**: choosing columns (low-to-medium cardinality, frequently filtered), expressions, and ordering |
| Intermediate | **Automatic clustering**: background reclustering, its credit cost, and when it is worth it |
| Intermediate | Reading "partitions scanned / total" in the Query Profile |
| Advanced | When to cluster: tables > ~1 TB with selective filters; when to re-sort on load instead |
| Advanced | Interaction with `MERGE`/`UPDATE` (rewriting partitions) and DML cost |
| Advanced | Search Optimization Service for point lookups and selective semi-structured queries |
| Advanced | Materialised views and their maintenance cost; comparison with dynamic tables |
| Advanced | Iceberg tables and external tables: pruning limits compared with native tables |

**How to learn it**

1. Read the topic file.
2. Predict the partitions scanned for three filter shapes on a date-ordered
   table.
3. Draw overlapping vs well-clustered partitions for a key.

**Hands-on exercise — `experiments/03_micro_partitions/`**

1. Load 100 million rows (generated) ordered by date; run date-range
   queries and note pruning.
2. Randomise the load order; show pruning collapse.
3. Add a clustering key; read `SYSTEM$CLUSTERING_INFORMATION` before and
   after; track reclustering credits.
4. Compare pruning on a filter by a non-clustered column.
5. Decide whether the key was worth its credits.

**Checkpoint:**

- [ ] Explain micro-partitions and pruning.
- [ ] Read clustering information.
- [ ] Choose clustering keys and justify the cost.
- [ ] Explain why DML can disturb clustering.

**Common mistakes:** clustering small tables; clustering on very
high-cardinality columns; ignoring reclustering credits; expecting indexes.

---

### Topic 04 — [Stages, COPY INTO, and Snowpipe](04-stages-copy-into-and-snowpipe.md)

**Why here:** getting data in correctly, repeatably, and cheaply is the core
ingestion skill for Snowflake.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Stages**: user, table, named internal, and **external** (S3/GCS/Azure); `PUT`, `LIST`, `REMOVE` |
| Basics | **File formats** for CSV, JSON, Parquet, Avro, ORC; `CREATE FILE FORMAT` |
| Basics | `COPY INTO <table>` from a stage; `COPY INTO <location>` for unloading |
| Intermediate | **Storage integrations** and IAM roles instead of keys (from Module 2.17) |
| Intermediate | Load metadata: 64-day load history and idempotent re-runs; `FORCE`; `ON_ERROR`, `VALIDATION_MODE`, `PURGE` |
| Intermediate | Loading semi-structured data and transforming during load (`SELECT` in `COPY`); `MATCH_BY_COLUMN_NAME` |
| Intermediate | **Schema detection and evolution**: `INFER_SCHEMA`, `ENABLE_SCHEMA_EVOLUTION` |
| Intermediate | Python connector bulk loads: `write_pandas`, `PUT` + `COPY` vs row inserts |
| Advanced | **Snowpipe**: auto-ingest from cloud event notifications, serverless billing, latency, and per-file overhead |
| Advanced | **Snowpipe Streaming** and the Kafka connector for low-latency ingestion |
| Advanced | File sizing guidance (~100–250 MB compressed) and avoiding too-many-small-files costs |
| Advanced | Error handling: `COPY_HISTORY`, `PIPE_STATUS`, dead-letter patterns, and reprocessing |
| Advanced | External tables and querying data in place — trade-offs vs loading |

**How to learn it**

1. Read the topic file.
2. Plan the load of one S3 prefix: format, stage, error handling, and
   idempotency.
3. Decide between batch `COPY` and Snowpipe for three scenarios.

**Hands-on exercise — `experiments/04_loading/`**

1. Create an external stage with a storage integration; load CSV, JSON, and
   Parquet with proper file formats.
2. Load a file with bad rows under different `ON_ERROR` settings; inspect
   with `VALIDATE`.
3. Re-run a load and prove idempotency from load history.
4. Set up Snowpipe auto-ingest; drop files in the bucket and measure
   latency and cost.
5. Compare loading 10,000 tiny files vs 100 larger files.

**Checkpoint:**

- [ ] Create stages, file formats, and storage integrations.
- [ ] Load idempotently and handle bad records.
- [ ] Choose between `COPY` and Snowpipe.
- [ ] Explain file-size guidance and its cost impact.

**Common mistakes:** embedding cloud keys in stages; tiny files with
Snowpipe; ignoring `COPY_HISTORY` errors; assuming `FORCE` is harmless.

---

## 8. Phase C — Transformation and Programmability (Intermediate → Advanced)

### Topic 05 — [Streams, tasks, and dynamic tables](05-streams-tasks-and-dynamic-tables.md)

**Why here:** these three features let you build incremental pipelines
entirely inside Snowflake — change capture, scheduling, and declarative
refresh.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Streams**: change tracking on a table; standard vs append-only; the `METADATA$ACTION`, `METADATA$ISUPDATE`, `METADATA$ROW_ID` columns |
| Basics | **Tasks**: scheduled SQL or Snowpark procedures; cron and interval schedules; serverless vs warehouse tasks |
| Basics | Consuming a stream in a `MERGE` advances its offset only when the transaction commits |
| Intermediate | **Task graphs (DAGs)**: root tasks, `AFTER` dependencies, finalizer tasks, retries, and `SYSTEM$STREAM_HAS_DATA` conditions |
| Intermediate | CDC patterns: stream + task `MERGE` into silver/gold; handling deletes and updates |
| Intermediate | **Dynamic tables**: declarative `SELECT` with `TARGET_LAG`; refresh modes (incremental vs full); dependencies between dynamic tables |
| Intermediate | Streams/tasks vs dynamic tables vs materialised views vs dbt: choosing the right tool |
| Advanced | Stream staleness and the data retention interaction; recovering a stale stream |
| Advanced | Monitoring: `TASK_HISTORY`, `DYNAMIC_TABLE_REFRESH_HISTORY`, alerts, and notification integrations |
| Advanced | Cost control for continuous pipelines: lag settings, warehouse choice, and avoiding full refreshes |
| Advanced | Orchestrating beyond tasks: Airflow/Dagster/dbt calling Snowflake (Module 2.13) |
| Advanced | Event tables, alerts, and observability — awareness |

**How to learn it**

1. Read the topic file.
2. Draw the flow: raw table → stream → task → merge → silver → dynamic
   table → gold.
3. List the failure modes for each arrow.

**Hands-on exercise — `experiments/05_streams_tasks/`**

1. Create a raw table, a stream, and a task that merges changes into a
   silver table every minute.
2. Insert, update, and delete rows in raw; verify silver and the stream's
   metadata.
3. Build a gold layer as a dynamic table with a 5-minute lag; compare with
   a task-based version.
4. Suspend the task until the stream goes stale, then recover.
5. Add monitoring queries and an alert for failed tasks.

**Checkpoint:**

- [ ] Explain how streams track changes and when offsets advance.
- [ ] Build a task graph with dependencies.
- [ ] Choose between tasks, dynamic tables, and dbt.
- [ ] Recover a stale stream.

**Common mistakes:** consuming a stream outside a transaction; frequent
tasks on large warehouses burning credits; full refresh dynamic tables by
accident; no monitoring of failed tasks.

---

### Topic 06 — [Snowpark Python and UDFs](06-snowpark-python-and-udfs.md)

**Why here:** Snowpark lets you write DataFrame code in Python that runs
inside Snowflake, next to the data. It replaces moving data out to pandas.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The Snowpark **Session**; DataFrame API (`select`, `filter`, `join`, `group_by`, `with_column`); lazy evaluation compiled to SQL |
| Basics | Reading and writing tables; `to_pandas()` and its cost; `collect()` vs `show()` |
| Basics | Differences from pandas/PySpark; function library (`snowflake.snowpark.functions`) |
| Intermediate | **UDFs** (scalar), **UDTFs** (table functions), **UDAFs**, and vectorised (batch) UDFs; registering and packaging dependencies (Anaconda channel, stage imports) |
| Intermediate | **Stored procedures** in Python for orchestration and multi-step logic; owner's vs caller's rights |
| Intermediate | Pandas on Snowflake — awareness; writing tests for Snowpark code locally (local testing framework) |
| Intermediate | Using Snowpark inside tasks and dbt Python models (Module 2.12) |
| Advanced | Performance: push down to SQL, avoid row-by-row UDFs, vectorised UDFs, and memory-optimised warehouses |
| Advanced | Machine learning in Snowflake: Snowpark ML, model registry, feature store — awareness (links to Module 2C.10) |
| Advanced | Container services (Snowpark Container Services) — awareness |
| Advanced | Security: external access integrations, secrets, and network rules for UDFs calling APIs |
| Advanced | When Snowpark vs SQL vs external Spark is the right choice |

**How to learn it**

1. Read the topic file.
2. Rewrite one SQL transformation as a Snowpark DataFrame and compare the
   generated SQL (`df.queries`).
3. List which steps in your pipeline should stay SQL.

**Hands-on exercise — `experiments/06_snowpark/`**

1. Build a Snowpark pipeline that cleans and aggregates an events table
   and writes a gold table.
2. Write a scalar UDF, then a vectorised UDF; benchmark both on 10 million
   rows.
3. Write a Python UDTF that parses a messy string column into rows.
4. Wrap the pipeline in a stored procedure and schedule it with a task.
5. Add unit tests using the local testing framework.

**Checkpoint:**

- [ ] Explain how Snowpark executes (lazy, pushed down).
- [ ] Write UDFs, UDTFs, and procedures.
- [ ] Choose vectorised over scalar UDFs.
- [ ] Test Snowpark code.

**Common mistakes:** calling `to_pandas()` on huge data; row-by-row UDFs;
undeclared package dependencies; putting secrets in code.

---

## 9. Phase D — Data Protection and Governance (Intermediate → Advanced)

### Topic 07 — [Time Travel, cloning, and zero-copy](07-time-travel-cloning-and-zero-copy.md)

**Why here:** these features give recovery and cheap test environments that
other warehouses make hard. They change how you handle mistakes and
deployments.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Time Travel**: `AT`/`BEFORE` with timestamp, offset, or statement id; retention periods (1 day standard, up to 90 on higher editions) |
| Basics | `UNDROP` for tables, schemas, and databases |
| Basics | **Zero-copy cloning**: `CREATE ... CLONE` of tables, schemas, and databases; storage shared until data changes |
| Intermediate | **Fail-safe**: 7 days of Snowflake-managed recovery, not user accessible; storage cost implications |
| Intermediate | Cloning for dev/test: clone prod schema, mask data, run CI; combining clones with Time Travel |
| Intermediate | Recovering from a bad `UPDATE`/`DELETE`/`DROP`; restore patterns (`CREATE ... CLONE ... AT`) |
| Intermediate | Storage costs: Time Travel + Fail-safe bytes in `TABLE_STORAGE_METRICS`; transient tables to avoid them |
| Advanced | Clone limits and gotchas: privileges not cloned for some objects, external tables, streams and tasks behaviour |
| Advanced | Database replication, failover groups, and cross-region disaster recovery — awareness |
| Advanced | Blue/green deployments with clones and `SWAP WITH` |
| Advanced | Data retention policy design per layer (raw vs gold) and compliance interactions (right to be forgotten vs retention) |

**How to learn it**

1. Read the topic file.
2. For four disasters (dropped table, bad update, wrong deploy, corrupt
   load), state the recovery tool and its time limit.
3. Draw how clones share micro-partitions and diverge.

**Hands-on exercise — `experiments/07_time_travel/`**

1. Update a table wrongly; recover with `AT (STATEMENT => ...)`.
2. Drop and `UNDROP` a table; try after the retention window and note the
   outcome (on a transient table).
3. Clone a 100 GB schema; compare storage before and after changing 1%
   of rows.
4. Build a CI-style job: clone prod → run a migration → run tests → drop.
5. Measure the storage cost of 30 days of daily full reloads.

**Checkpoint:**

- [ ] Query and restore data with Time Travel.
- [ ] Explain Fail-safe vs Time Travel.
- [ ] Use cloning for dev/test safely.
- [ ] Explain the storage cost of retention.

**Common mistakes:** assuming Time Travel is a backup strategy for all
eternity; long retention on churny staging tables; forgetting that clones
inherit data you may need to mask.

---

### Topic 08 — [RBAC, masking policies, and row access](08-rbac-masking-policies-and-row-access.md)

**Why here:** Snowflake concentrates sensitive data. Role-based access and
policy-based protection are mandatory skills (building on Module 2.20).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Securable objects, **roles**, **privileges**, **grants**, and role hierarchy; system roles (ACCOUNTADMIN, SECURITYADMIN, SYSADMIN, USERADMIN, PUBLIC) |
| Basics | Least privilege; never working as ACCOUNTADMIN; `USE ROLE`; default roles |
| Basics | Users, authentication methods: passwords, MFA, key pair, SSO (SAML/OAuth); service users |
| Intermediate | Role design: functional roles, access roles per schema, and **database roles**; future grants and managed access schemas |
| Intermediate | **Dynamic data masking** policies on columns; conditional masking by role/attribute |
| Intermediate | **Row access policies** with mapping tables |
| Intermediate | **Tags** and tag-based masking; classification of sensitive data |
| Advanced | Secure views and secure UDFs; protecting definitions and preventing information leaks |
| Advanced | Network policies, private connectivity, and encryption (managed keys, Tri-Secret Secure) — awareness |
| Advanced | Auditing: `ACCESS_HISTORY`, `LOGIN_HISTORY`, `QUERY_HISTORY`; detecting over-privileged roles |
| Advanced | Access governance at scale: infrastructure as code (Terraform provider, schemachange), review workflows |
| Advanced | Data classification, GDPR and retention interplay with Time Travel |

**How to learn it**

1. Read the topic file.
2. Design roles for analysts, engineers, and a finance team with PII.
3. Write which policies apply to which columns and rows.

**Hands-on exercise — `experiments/08_rbac/`**

1. Build a role hierarchy with access roles and functional roles using
   scripted grants and future grants.
2. Apply a masking policy to email and SSN with different results per role.
3. Add a row access policy by region and test with two roles.
4. Tag columns as PII and attach a tag-based masking policy.
5. Use `ACCESS_HISTORY` to find who read a sensitive column.

**Checkpoint:**

- [ ] Design least-privilege role hierarchies.
- [ ] Apply masking and row access policies.
- [ ] Use tags for scalable governance.
- [ ] Audit access.

**Common mistakes:** granting to users instead of roles; over-using
ACCOUNTADMIN; forgetting future grants; masking in the application layer
only.

---

## 10. Phase E — Sharing and Cost (Advanced)

### Topic 09 — [Data sharing and the Marketplace](09-data-sharing-and-marketplace.md)

**Why here:** secure sharing is one of Snowflake's distinctive features:
no copies, no ETL, live access.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Secure Data Sharing**: providers, consumers, shares; no data copy, read-only access |
| Basics | Creating a share, granting objects, and adding consumer accounts; reader accounts for non-Snowflake customers |
| Basics | The **Snowflake Marketplace**: consuming third-party datasets |
| Intermediate | Sharing secure views to expose subsets; row- and column-level protection |
| Intermediate | **Listings** and data products; cross-region and cross-cloud sharing via replication and auto-fulfilment |
| Intermediate | Consumer experience: creating a database from a share; cost paid by the consumer's compute |
| Advanced | **Data clean rooms** — awareness; Native Apps for distributing logic with data |
| Advanced | Governance of outbound sharing: approvals, auditing, and revocation |
| Advanced | Alternatives and comparisons: Delta Sharing, BigQuery Analytics Hub, S3 exports (links to Module 2B.4 Topic 11) |
| Advanced | Commercial and operational models: monetising data, SLAs, versioning of shared schemas (links to Module 2C.8) |

**How to learn it**

1. Read the topic file.
2. Sketch sharing an orders dataset with a partner so they see only their
   own rows.
3. List the failure modes (schema change, revoked access, region mismatch).

**Hands-on exercise — `experiments/09_sharing/`**

1. Create a secure view with a row filter and share it with a second
   (trial) account.
2. Create a database from the share on the consumer side and query it.
3. Revoke an object and verify the consumer's behaviour.
4. Subscribe to a free Marketplace dataset and join it with your data.

**Checkpoint:**

- [ ] Explain why sharing involves no copy.
- [ ] Share safely using secure views.
- [ ] Explain consumer vs provider cost.
- [ ] Compare Snowflake sharing with Delta Sharing.

**Common mistakes:** sharing base tables with sensitive columns; breaking
consumers with schema changes; forgetting cross-region replication costs.

---

### Topic 10 — [Cost monitoring and resource monitors](10-cost-monitoring-and-resource-monitors.md)

**Why it comes last:** cost control uses everything above and is a
visible, valued skill.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The cost model: compute credits, storage, data transfer, cloud services, serverless features |
| Basics | **Resource monitors**: credit quotas, notification and suspend thresholds |
| Basics | Finding the top spenders in Snowsight's cost management views |
| Intermediate | `ACCOUNT_USAGE` views: `WAREHOUSE_METERING_HISTORY`, `QUERY_HISTORY`, `STORAGE_USAGE`, `METERING_DAILY_HISTORY`, `SERVERLESS_TASK_HISTORY` |
| Intermediate | Attribution: query tags, warehouse-per-team, and `QUERY_ATTRIBUTION_HISTORY` |
| Intermediate | Typical savings: auto-suspend, right-sizing, result cache, pruning, avoiding `SELECT *`, and deleting unused tables |
| Intermediate | **Budgets** and alerts |
| Advanced | Finding expensive queries and fixing them (spilling, exploding joins, no pruning, repeated full scans) |
| Advanced | Serverless costs: Snowpipe, auto-clustering, search optimisation, dynamic tables, tasks — and monitoring them |
| Advanced | Storage optimisation: transient tables, retention tuning, and cleaning stage files |
| Advanced | Capacity contracts vs on-demand; chargeback/showback; FinOps for data (Module 2.21) |
| Advanced | Building a cost dashboard and weekly review routine |

**How to learn it**

1. Read the topic file.
2. Write the SQL for "top 20 queries by credits this week".
3. List ten optimisations in order of expected savings.

**Hands-on exercise — `experiments/10_cost/`**

1. Create resource monitors on every warehouse with notify and suspend
   thresholds.
2. Build views over `ACCOUNT_USAGE` for daily credits by warehouse, role,
   and query tag.
3. Find the three most expensive queries in your lab and fix them;
   measure the savings.
4. Review serverless feature spend and decide which to keep.
5. Produce a one-page FinOps report.

**Checkpoint:**

- [ ] Explain every component of the bill.
- [ ] Set resource monitors and budgets.
- [ ] Attribute cost to teams and workloads.
- [ ] Find and fix an expensive query.

**Common mistakes:** monitoring only compute; no tagging; ignoring
serverless features; setting suspend thresholds that break critical jobs
without a plan.

---

## 11. Module mini-project — an incremental ELT platform on Snowflake

**Goal:** build a governed, cost-aware pipeline from files to a shared gold
layer.

**Requirements**

1. Land JSON/CSV/Parquet files from object storage using stages, a
   storage integration, and Snowpipe or scheduled `COPY`.
2. Raw → silver with streams and tasks (idempotent `MERGE`, deletes
   handled); silver → gold with dynamic tables.
3. A Snowpark Python step with a vectorised UDF.
4. Roles, masking, and row access policies, all defined in scripts.
5. A dev environment created by cloning prod; a test run in CI.
6. A secure view shared with a second account.
7. Resource monitors, query tags, and a cost dashboard; a before/after
   optimisation report.

**Done when** the pipeline runs unattended, a bad update can be reverted,
PII is masked for analysts, and your cost report explains every credit.

---

## 12. Module self-assessment — exit criteria

You have completed this module when you can do all of the following
**without notes**:

- [ ] Explain Snowflake's architecture and caches.
- [ ] Size and isolate warehouses and justify the cost.
- [ ] Explain micro-partitions, pruning, and when to cluster.
- [ ] Load data idempotently with `COPY` and Snowpipe.
- [ ] Build incremental pipelines with streams, tasks, and dynamic tables.
- [ ] Write Snowpark code and UDFs.
- [ ] Recover data with Time Travel and use clones safely.
- [ ] Design RBAC and apply masking and row access policies.
- [ ] Share data securely.
- [ ] Monitor and reduce spend.

---

## 13. Recommended reading and references

- Snowflake documentation (architecture, loading, streams and tasks,
  dynamic tables, Snowpark, access control, cost management).
- *Snowflake Cookbook* and the Snowflake Quickstarts library.
- Snowflake's engineering blog and the "Snowflake: A Cloud-Native Data
  Warehouse" paper.
- SnowPro Core / Advanced Data Engineer certification guides (as study
  outlines).

---

## 14. Where this module leads

- **Module 2C.4** compares BigQuery's slot-based model with Snowflake's
  warehouses.
- **Module 2C.6** (dbt) is the most common way teams build models on
  Snowflake.
- **Module 2C.7** covers engines that compete with warehouses for
  low-latency analytics.
- **Module 2C.8** covers platform decisions such as warehouse vs lakehouse
  and vendor selection.
