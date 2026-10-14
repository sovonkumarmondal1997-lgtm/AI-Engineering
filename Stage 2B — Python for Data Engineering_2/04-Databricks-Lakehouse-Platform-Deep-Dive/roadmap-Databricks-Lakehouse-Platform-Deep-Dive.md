# Roadmap — Gap Module G4: Databricks Lakehouse Platform Deep Dive

This is the learning roadmap for the fourth gap module, **Databricks
Lakehouse Platform Deep Dive**. It tells you **what** to learn about
building and operating data platforms on Databricks, **in what order**,
**how** to learn each topic, and **how to prove to yourself** that you have
learned it before you move on.

**When to take it:** after Stage 2 **Module 2.17**, ideally after Modules
2.18 and 2.20 as well. It is one of two **alternative depth tracks** —
choose this module **or** Gap Module G3 (AWS), depending on the roles you
target. Databricks runs on AWS, Azure, and Google Cloud, so this track is
also useful for teams that are multi-cloud.

**What this module is not:** it does **not** re-teach Spark (Module 2.14),
Delta Lake internals, time travel, `MERGE`, compaction, liquid clustering
concepts, or catalog fundamentals (Module 2.15), Structured Streaming and
Kafka (Module 2.16), dbt (Module 2.12), Airflow (Module 2.13), or cloud
storage and IAM basics (Module 2.17). It goes deep into **Databricks
platform features** — how Databricks packages, manages, governs, automates,
and bills those capabilities.

> **Change warning:** Databricks renames and evolves products quickly. For
> example, Delta Live Tables became **Lakeflow Declarative Pipelines**,
> Workflows became **Lakeflow Jobs**, Repos became **Git folders**, and
> compute access modes were renamed. Exam guides are updated to match.
> Always confirm names, APIs, and availability in the current Databricks
> documentation for your cloud and region.

> **Cost warning:** classic compute runs virtual machines in your cloud
> account plus Databricks charges (DBUs). Use auto-termination, compute
> policies, and budgets; prefer serverless or a free learning edition where
> possible; and delete lab workspaces or resources you do not need.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain Databricks' architecture — account, workspaces, control plane,
  classic and serverless compute planes — and set up a workspace sensibly.
- Choose and configure compute: all-purpose vs jobs compute, serverless,
  SQL warehouses, access modes, policies, and pools.
- Organise code professionally with Git folders, Python packages, and local
  development against remote compute.
- Govern everything with **Unity Catalog**: catalogs, schemas, managed and
  external tables, **volumes**, storage credentials, external locations,
  permissions, row filters, column masks, lineage, and audit.
- Ingest files incrementally with **Auto Loader** and sources with
  **Lakeflow Connect**.
- Build medallion pipelines with **Lakeflow Declarative Pipelines**,
  expectations, and automatic CDC and SCD handling.
- Orchestrate with **Lakeflow Jobs**: task types, triggers, parameters,
  retries, and repair.
- Tune performance with **Photon**, liquid clustering, and **predictive
  optimization**.
- Serve analytics with **Databricks SQL**, AI/BI dashboards, and **Genie**.
- Share data with **Delta Sharing** and the **Marketplace**.
- Deploy everything as code with **Databricks Asset Bundles** and CI/CD.
- Control and attribute cost with **system tables**, tags, and policies.
- Hand data over to ML with **MLflow** and **feature engineering in Unity
  Catalog**.
- Prepare for the **Databricks Certified Data Engineer** certifications.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Command line, SSH, data CLI tools | Gap Module G2 | Databricks CLI and troubleshooting |
| SQL, window functions, `MERGE` | Module 2.6 | Databricks SQL and pipelines |
| Data modelling, SCD types | Module 2.8 | Declarative pipelines' SCD handling |
| Ingestion patterns, CDC, file drops | Module 2.9 | Auto Loader and Lakeflow Connect |
| Data quality, contracts, WAP | Module 2.11 | Expectations and quality gates |
| Pipeline design, dbt | Module 2.12 | Declarative pipelines, dbt tasks |
| Orchestration concepts | Module 2.13 | Lakeflow Jobs vs Airflow |
| **PySpark and tuning** | Module 2.14 | All processing; **not** re-taught |
| **Delta Lake, catalogs, maintenance** | Module 2.15 | Delta and Unity Catalog foundations; **not** re-taught |
| **Structured Streaming** | Module 2.16 | Streaming tables and Auto Loader |
| **Cloud storage, IAM, managed Spark comparison** | Module 2.17 | Storage credentials and cloud set-up |
| **CI/CD, Terraform, secrets** | Module 2.18 | Asset Bundles and workspace infrastructure |
| Testing | Module 2.19 | Testing notebooks-free, package-based code |
| Governance, lineage, PII | Module 2.20 | Unity Catalog governance |
| Performance and cost | Module 2.21 | Photon, clustering, cost attribution |
| Semantic layers, feature stores | Module 2.22 | Metric definitions, Genie, feature engineering |

**Environment options:**

- **Databricks Free Edition** (serverless-only, with usage limits) for most
  topics — check its current capabilities.
- A **cloud trial or company sandbox workspace** for account-level topics
  (Unity Catalog set-up, classic compute, storage credentials, system
  tables, Delta Sharing), with budgets and policies.
- Local tools: Python 3.12+ with `uv`, the **Databricks CLI**, **Databricks
  Connect**, the VS Code (or other IDE) extension, pytest, and Git.

---

## 3. How the module is organised

The fourteen topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — Platform Foundations                        (Basics)
  01 Databricks architecture, workspaces, and planes
  02 Compute: clusters, serverless, and SQL warehouses
  03 Notebooks, Git folders, and project structure

Phase B — Governance                                  (Intermediate)
  04 Unity Catalog deep dive: volumes, locations, and permissions

Phase C — Ingestion and Pipelines                     (Intermediate → Advanced)
  05 Auto Loader and incremental file ingestion
  06 Lakeflow Connect managed ingestion
  07 Lakeflow Declarative Pipelines and expectations
  08 Lakeflow Jobs orchestration

Phase D — Performance, Analytics, and Sharing         (Advanced)
  09 Photon, performance, and predictive optimization
  10 Databricks SQL, AI/BI dashboards, and Genie
  11 Delta Sharing and Marketplace

Phase E — Delivery, Cost, and ML Handoff              (Advanced)
  12 Databricks Asset Bundles and CI/CD
  13 Cost management and system tables
  14 MLflow and feature engineering handoff

Consolidate
  practice-questions.md
  interview-practice.md
  certification-prep-databricks-data-engineer.md
  Module mini-project: a Databricks lakehouse platform (→ Projects/04-databricks-lakehouse-platform.md)
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09 ► 10 ► 11 ► 12 ► 13 ► 14
where compute code govern files sources pipelines jobs speed serve share deploy pay handoff
```

Why this order:

- Architecture (01), compute (02), and code organisation (03) come before
  anything else because every later feature runs on them.
- Unity Catalog (04) comes before ingestion because every table, volume,
  and pipeline is created inside it.
- Ingestion (05–06) feeds declarative pipelines (07), which jobs (08)
  orchestrate.
- Performance (09), SQL analytics (10), and sharing (11) operate on the
  tables built in Phase C.
- Asset Bundles (12), cost (13), and the ML handoff (14) cover delivering,
  paying for, and extending the whole platform.

---

## 4. Suggested schedule

About **5 weeks at 8–10 hours per week**, plus 1–2 weeks of certification
preparation if you choose to certify.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — architecture · Topic 02 — compute · Topic 03 — code organisation |
| 2 | Topic 04 — Unity Catalog deep dive · Topic 05 — Auto Loader |
| 3 | Topic 06 — Lakeflow Connect · Topic 07 — declarative pipelines |
| 4 | Topic 08 — Lakeflow Jobs · Topic 09 — performance · Topic 10 — Databricks SQL and Genie |
| 5 | Topic 11 — Delta Sharing · Topic 12 — Asset Bundles · Topic 13 — cost · Topic 14 — ML handoff · mini-project |
| 6–7 (optional) | Interview practice · certification preparation |

---

## 5. How to study every topic (the Databricks build loop)

```text
Read → Map it to the open-source concept → Build it in a dev target
→ Govern it in Unity Catalog → Run it on the cheapest adequate compute
→ Break it → Observe (UI, event logs, system tables) → Put it in a bundle
→ Measure cost → Write it down → Explain aloud
```

1. **Read** the topic file and the current Databricks documentation page
   for the feature.
2. **Map it** to what you already know from Stage 2 (e.g. Auto Loader ↔
   incremental file discovery, declarative pipelines ↔ medallion jobs with
   quality gates, Lakeflow Jobs ↔ Airflow DAGs).
3. **Build it** in a personal development target or schema.
4. **Govern it**: every object in Unity Catalog with owners and grants.
5. **Run it on the cheapest adequate compute** (serverless or a small jobs
   cluster with auto-termination).
6. **Break it**: bad data, schema change, missing permission, failed task.
7. **Observe** with the UI, pipeline event logs, query profiles, and system
   tables.
8. **Put it in a bundle** (from Topic 12 onwards, retrofit earlier topics).
9. **Measure cost** with system tables and tags.
10. **Write down** lessons, costs, and exam-relevant facts in
    `module-g4-notes.md`.
11. **Explain aloud** what Databricks did for you that you built by hand in
    Stage 2 — and what it did not.

Keep one `databricks_lab/` repository:

```text
databricks_lab/
├── databricks.yml             # Asset Bundle (from Topic 12)
├── resources/                 # job and pipeline definitions
├── src/lab/                   # Python package: transformations, utilities
├── pipelines/                 # declarative pipeline source files
├── sql/                       # Databricks SQL queries, metric definitions
├── notebooks/                 # exploration only (not production logic)
├── tests/                     # pytest (local and Databricks Connect)
└── docs/                      # notes, cost log, diagrams, exam notes
```

---

## 6. Phase A — Platform Foundations (Basics)

### Topic 01 — [Databricks architecture, workspaces, and planes](01-databricks-architecture-workspaces-and-planes.md)

**Why it comes first:** Security, networking, cost, and governance
decisions all depend on where Databricks runs what — and which parts live
in your cloud account versus Databricks'.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The **account** (account console) and **workspaces**; regions and clouds |
| Basics | **Control plane** (managed by Databricks: web app, job scheduler, notebooks metadata) vs **compute plane** — **classic** (VMs in your cloud account) and **serverless** (compute managed by Databricks) |
| Basics | Where data lives: your cloud object storage, governed by Unity Catalog (Topic 04); why legacy workspace-level storage patterns are discouraged for new work |
| Intermediate | **Identity**: account-level users, groups, and **service principals**; syncing identities from an identity provider; assigning identities to workspaces |
| Intermediate | Workspace objects: folders, notebooks, files, queries, dashboards, jobs, pipelines, and their permissions |
| Intermediate | Networking and security options — private connectivity, customer-managed network, IP access lists, customer-managed keys — awareness and when they matter |
| Advanced | Workspace strategy: separate workspaces per environment or business unit vs shared workspaces with catalog isolation |
| Advanced | Workspace infrastructure as code with the Databricks Terraform provider (Module 2.18) |
| Advanced | Where Databricks fits relative to AWS/Azure/GCP-native services and open-source equivalents |

**How to learn it**

1. Read the topic file.
2. Draw the architecture: control plane, classic and serverless compute
   planes, your storage, and identity flows.
3. Explore the account console (if available) and one workspace; list what
   is configured at account level vs workspace level.

**Hands-on exercise — `docs/architecture.md`**

1. Draw and explain your lab's architecture, including where each kind of
   compute runs and where data is stored.
2. Create groups (`data-engineers`, `analysts`, `ml-engineers`) and a
   service principal `ci-deployer`; assign them to your workspace.
3. Write a one-page workspace strategy for a company with dev, staging, and
   prod environments.
4. Record which settings you would manage with Terraform.

**Checkpoint — you are ready to move on when you can:**

- [ ] Explain control plane vs classic and serverless compute planes.
- [ ] Explain account vs workspace responsibilities.
- [ ] Use groups and service principals instead of individual users.
- [ ] Propose a workspace strategy.

**Common mistakes:** granting permissions to individual users; mixing
production and experimentation in one workspace without catalog isolation;
storing data in legacy workspace storage.

---

### Topic 02 — [Compute: clusters, serverless, and SQL warehouses](02-compute-clusters-serverless-and-sql-warehouses.md)

**Why here:** Compute is where most Databricks money is spent and where
most permission surprises come from (access modes). Choosing the right
compute for each workload is a core Databricks skill.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **All-purpose compute** (interactive) vs **jobs compute** (created per job run) — and why production runs on jobs compute or serverless |
| Basics | **Databricks Runtime** versions, long-term-support versions, and ML runtimes |
| Basics | Autoscaling, **auto-termination**, worker and driver sizes |
| Basics | **SQL warehouses** for SQL and BI workloads: serverless vs classic/pro types, sizes, scaling, and auto-stop |
| Intermediate | **Serverless compute** for notebooks, jobs, and pipelines: fast start, no infrastructure, and its limitations |
| Intermediate | **Access modes** (standard/shared vs dedicated/single-user): what each supports with Unity Catalog, and why they matter for security |
| Intermediate | **Compute policies** to limit instance types, sizes, auto-termination, and tags — enforcing cost and security rules |
| Intermediate | Libraries: installing Python wheels and packages on compute, environment specifications for serverless |
| Advanced | **Instance pools** to reduce start-up time, **spot instances** for workers, and init scripts (use sparingly) |
| Advanced | Choosing compute per workload: exploration, scheduled ETL, streaming, SQL dashboards, ML — with cost reasoning |
| Advanced | The Spark UI, driver logs, and metrics for Databricks compute (Module 2.14 debugging on Databricks) |

**How to learn it**

1. Read the topic file.
2. Run the same Spark job on all-purpose compute, jobs compute, and
   serverless; record start-up time, run time, and cost.
3. Try an operation that is blocked in one access mode and allowed in
   another; explain why.

**Hands-on exercise — `docs/compute.md`**

1. Create a compute policy that enforces auto-termination, maximum size,
   and cost tags; create a cluster only through it.
2. Create a small serverless SQL warehouse with auto-stop.
3. Benchmark the Module 2.14 silver job on three compute types and build a
   cost/time table.
4. Install your lab Python package as a library on compute and on a
   serverless environment.
5. Write a compute decision guide for your team.

**Checkpoint:**

- [ ] Choose between all-purpose, jobs, serverless, and SQL warehouses.
- [ ] Explain access modes and their Unity Catalog implications.
- [ ] Enforce cost and security rules with compute policies.
- [ ] Diagnose jobs with the Spark UI and logs on Databricks.

**Common mistakes:** production jobs on all-purpose clusters; no
auto-termination; oversized warehouses running idle; ignoring access mode
limitations until a job fails in production.

---

### Topic 03 — [Notebooks, Git folders, and project structure](03-notebooks-git-folders-and-project-structure.md)

**Why here:** Notebooks are great for exploration and terrible as the only
home of production logic. Professional Databricks projects are Python
packages in Git, tested locally and deployed as code.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Notebooks: languages, magic commands, widgets, and visualisations — for exploration |
| Basics | **Git folders**: cloning repositories into the workspace, branches, commits, pulls, and pull requests |
| Basics | **Workspace files** and importing Python modules from files (instead of `%run` chains) |
| Intermediate | **Project structure**: a Python package (`src/`), notebooks as thin entry points (or none at all), tests, and configuration — applying Stage 1 and Module 2.12 structure |
| Intermediate | `dbutils` utilities (widgets, secrets, file system) and replacing them with parameters and Unity Catalog volumes in production code |
| Intermediate | **Secrets**: secret scopes and reading secrets in code without printing them (Module 2.18) |
| Intermediate | **Local development**: the IDE extension and **Databricks Connect** to run Spark code from your laptop against remote compute; pytest with local Spark vs remote compute (Module 2.19) |
| Advanced | Job parameters and notebook widgets vs Python entry-point arguments |
| Advanced | Code review, linting, and formatting in a Databricks project (Module 2.18) |
| Advanced | Anti-patterns: logic spread across many notebooks, `%run` chains, hard-coded paths and catalogs, secrets in notebooks |

**How to learn it**

1. Read the topic file.
2. Take one exploratory notebook and refactor its logic into a tested
   package function called by a thin entry point.
3. Run the same function from your IDE via Databricks Connect.

**Hands-on exercise — `databricks_lab/`**

1. Create the `databricks_lab` repository, clone it into a Git folder, and
   work on a feature branch.
2. Write `src/lab/transforms.py` with pure DataFrame functions and pytest
   tests that run locally.
3. Run the same tests (or an integration test) against remote compute with
   Databricks Connect.
4. Store a credential in a secret scope and read it in code; verify it is
   redacted in outputs.
5. Write a project README explaining structure and development workflow.

**Checkpoint:**

- [ ] Use Git folders and branches for all code.
- [ ] Structure projects as tested Python packages.
- [ ] Develop locally with Databricks Connect.
- [ ] Handle secrets correctly.

**Common mistakes:** production logic only in notebooks; copying code
between notebooks; editing directly in the main branch in the workspace;
secrets pasted into notebooks.

---

## 7. Phase B — Governance (Intermediate)

### Topic 04 — [Unity Catalog deep dive: volumes, locations, and permissions](04-unity-catalog-deep-dive-volumes-locations-and-permissions.md)

**Why here:** On Databricks, **everything** — tables, views, files,
functions, models — lives in Unity Catalog. Module 2.15 introduced catalogs
in general; this topic makes you able to design and operate Unity Catalog
for a real platform.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The **metastore** and the three-level namespace: **catalog → schema → object** (tables, views, volumes, functions, models) |
| Basics | **Managed tables** (storage managed by Unity Catalog) vs **external tables** (your storage paths) — and why managed tables are the default recommendation |
| Basics | **Volumes** (managed and external) for non-tabular files: landing files, images, documents, model artefacts |
| Intermediate | **Storage credentials** and **external locations**: how Unity Catalog accesses cloud storage securely (Module 2.17 IAM on Databricks) |
| Intermediate | **Privileges**: `USE CATALOG`, `USE SCHEMA`, `SELECT`, `MODIFY`, `CREATE TABLE`, `READ VOLUME`, `WRITE VOLUME`, and more; inheritance down the hierarchy; ownership; granting to groups |
| Intermediate | Catalog design: per environment (`dev`, `staging`, `prod`) and per domain; schemas per layer (bronze, silver, gold); binding catalogs to specific workspaces |
| Intermediate | **Row filters** and **column masks** (SQL functions applied per table) for fine-grained access; dynamic views as an alternative (Module 2.20) |
| Intermediate | Tags on catalogs, schemas, tables, and columns (e.g. PII classification) and newer attribute/tag-based policy capabilities — check current availability |
| Intermediate | Automatic **lineage** (table- and column-level) across notebooks, jobs, pipelines, and dashboards |
| Advanced | **Audit logs** and access history via system tables (Topic 13) |
| Advanced | **Lakehouse Federation**: querying external databases and catalogs through Unity Catalog without copying data |
| Advanced | Interoperability: Iceberg and Delta clients reading Unity Catalog tables (e.g. via open REST catalog interfaces and UniForm — Module 2.15) |
| Advanced | Migrating legacy Hive metastore tables to Unity Catalog — awareness |

**How to learn it**

1. Read the topic file.
2. Design catalogs, schemas, volumes, and grants for three environments and
   four personas before creating anything.
3. Test every grant by acting as each persona (or a service principal).

**Hands-on exercise — `sql/governance/`**

1. Create an external location and storage credential for your landing
   storage (if your environment allows), a landing **volume**, and catalogs
   `dev_lab` and `prod_lab` with schemas `bronze`, `silver`, `gold`.
2. Grant access to groups: engineers write bronze/silver, analysts read
   gold, marketing sees gold without PII.
3. Apply a **row filter** (analysts see only their region) and a **column
   mask** (emails masked except for a privacy group) on `gold.customers`.
4. Tag PII columns; query tags through the information schema.
5. Run a notebook and a job that read and write tables, then inspect the
   lineage graph for a gold column.
6. Query a PostgreSQL database through Lakehouse Federation (if available)
   and document when you would copy data instead.

**Checkpoint:**

- [ ] Design catalogs, schemas, and volumes for environments and layers.
- [ ] Configure storage credentials and external locations.
- [ ] Grant privileges to groups with inheritance in mind.
- [ ] Apply row filters, column masks, and tags.
- [ ] Use lineage and explain audit options.

**Common mistakes:** grants to individuals; external tables everywhere
without a reason; one catalog for all environments; PII protected by
convention instead of masks and filters.

---

## 8. Phase C — Ingestion and Pipelines (Intermediate → Advanced)

### Topic 05 — [Auto Loader and incremental file ingestion](05-auto-loader-and-incremental-file-ingestion.md)

**Why here:** Most lakehouses start with files landing in cloud storage.
Auto Loader discovers and ingests new files incrementally and exactly once
— the managed version of the file registries you built in Modules 2.9 and
Project 04.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Auto Loader as a Structured Streaming source (`cloudFiles`) for JSON, CSV, Parquet, Avro, text, and binary files |
| Basics | Checkpoints and exactly-once file processing; running as a scheduled batch with `availableNow` or continuously (Module 2.16) |
| Basics | Loading from Unity Catalog **volumes** or external locations |
| Intermediate | **File discovery modes**: directory listing vs file notification/file events — scalability and cost |
| Intermediate | **Schema inference and evolution**: schema location, evolution modes (e.g. add new columns, rescue, fail), and the **rescued data column** for unexpected fields |
| Intermediate | Schema hints and explicit schemas for contracted sources (Module 2.11) |
| Intermediate | Handling corrupt files and records, and adding file metadata (source path, modification time) for provenance |
| Advanced | Rate limiting (maximum files or bytes per trigger), backfills of historical files, and periodic listing to catch missed events |
| Advanced | **`COPY INTO`** as a SQL-based, idempotent alternative for simpler or batch-only ingestion — when to choose it |
| Advanced | Auto Loader inside declarative pipelines (Topic 07) |
| Advanced | Cost and performance for millions of files |

**How to learn it**

1. Read the topic file.
2. Land files in a volume over several "days" with a new column appearing
   and a few corrupt files; ingest them with Auto Loader.
3. Compare Auto Loader with `COPY INTO` and with your Project 04 bronze
   ingestion.

**Hands-on exercise — `src/lab/ingest/`**

1. Ingest clickstream JSON files from a landing volume into
   `bronze.events` with Auto Loader (`availableNow`), a schema location,
   file metadata columns, and a rescued-data column.
2. Add files with a new field and observe schema evolution; add a corrupt
   file and show it is captured, not lost.
3. Run the ingestion twice and confirm no duplicates.
4. Ingest partner CSV files with `COPY INTO` and compare behaviour.
5. Backfill a year of historical files with rate limits and measure time and
   cost.

**Checkpoint:**

- [ ] Ingest files incrementally and exactly once with Auto Loader.
- [ ] Configure schema inference, evolution, and rescued data.
- [ ] Choose between directory listing and file notification modes.
- [ ] Choose between Auto Loader and `COPY INTO`.

**Common mistakes:** sharing or deleting checkpoints; inferring schemas for
contracted sources; ignoring the rescued data column; directory listing on
huge buckets without considering cost.

---

### Topic 06 — [Lakeflow Connect managed ingestion](06-lakeflow-connect-managed-ingestion.md)

**Why here:** Not every source is files. Lakeflow Connect provides managed
connectors for SaaS applications and databases — the "buy" option from
Module 2.9's build-vs-buy decision, inside Databricks.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What Lakeflow Connect provides: managed, incremental ingestion from supported SaaS applications and databases into Unity Catalog tables |
| Basics | Connections (credentials stored in Unity Catalog), ingestion pipelines, and destination catalogs and schemas |
| Intermediate | **Database connectors** with change data capture: ingestion gateways, snapshots, incremental changes, and source prerequisites (Module 2.9 CDC concepts) |
| Intermediate | **SaaS connectors**: incremental cursors, deletes, and API limits handled for you |
| Intermediate | Scheduling and monitoring ingestion pipelines; schema changes in sources |
| Intermediate | Other ingestion options on Databricks: Auto Loader (Topic 05), Structured Streaming from Kafka (Module 2.16), partner tools (e.g. Fivetran, dlt — Module 2.9), and custom Python data sources (Module 2.14) |
| Advanced | **Evaluating** a managed connector: supported objects, delete handling, history mode (SCD Type 2), latency, cost, and limits — and verifying completeness with reconciliation (Module 2.11) |
| Advanced | Governance of ingested data: classification and masking on arrival (Topic 04) |

**How to learn it**

1. Read the topic file.
2. List every source in your Stage 2 platform and decide: Auto Loader,
   Lakeflow Connect, Kafka streaming, partner tool, or custom code.
3. Set up one available connector (a database or SaaS source available in
   your environment) and inspect what it creates.

**Hands-on exercise — `docs/ingestion_decisions.md`**

1. Configure a Lakeflow Connect ingestion from a supported source in your
   environment (for example a database with CDC), landing into `bronze`.
2. Make inserts, updates, and deletes in the source and verify how they
   appear; test a schema change.
3. Reconcile row counts and keys between source and destination.
4. Write a build-vs-buy decision record for five sources (Module 2.9
   criteria), including cost.

**Checkpoint:**

- [ ] Explain Lakeflow Connect's components and connector types.
- [ ] Configure and monitor a managed ingestion pipeline.
- [ ] Evaluate connectors for deletes, history, latency, and cost.
- [ ] Choose among Databricks ingestion options.

**Common mistakes:** assuming connectors capture deletes and history the
way you need without testing; skipping reconciliation; credentials outside
Unity Catalog connections.

---

### Topic 07 — [Lakeflow Declarative Pipelines and expectations](07-lakeflow-declarative-pipelines-and-expectations.md)

**Why here:** Declarative pipelines let you describe **what** tables should
contain; Databricks manages dependencies, incremental processing,
retries, data-quality expectations, CDC, and infrastructure. They are
central to modern Databricks data engineering — and to the certification.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The declarative model: define datasets in SQL or Python; the platform infers the dependency graph and runs it |
| Basics | Dataset types: **streaming tables** (incremental, append-oriented sources) and **materialized views** (results kept up to date incrementally where possible); temporary views |
| Basics | Pipeline settings: target catalog and schema, compute (serverless or classic), triggered vs continuous mode, development vs production mode |
| Intermediate | **Expectations**: constraints with actions — keep and record (warn), **drop** invalid rows, or **fail** the update — and data-quality metrics in the event log (Module 2.11) |
| Intermediate | **Change data capture in pipelines**: the automatic CDC/"apply changes" API to build **SCD Type 1 and Type 2** tables from change feeds, with sequencing columns and delete handling (Modules 2.6, 2.8, 2.12) |
| Intermediate | Using Auto Loader (Topic 05) and Kafka sources inside pipelines |
| Intermediate | The **event log**: querying pipeline progress, lineage, and expectation results |
| Intermediate | **Full refresh** vs incremental updates; selective refresh of tables |
| Advanced | Flows (multiple sources writing into one table), backfills, and handling late data |
| Advanced | Parameterising pipelines per environment; organising source files as modules |
| Advanced | Declarative pipelines vs hand-written Structured Streaming + `MERGE` jobs (Project 04) vs dbt (Module 2.12): control, transparency, cost, and portability — including the open-source declarative pipelines effort in Apache Spark (awareness) |
| Advanced | Serverless pipeline performance and cost settings |

**How to learn it**

1. Read the topic file.
2. Rebuild the Project 04 medallion (or a subset) as a declarative pipeline.
3. Compare lines of code, operational effort, and behaviour on bad data with
   your hand-built version.

**Hands-on exercise — `pipelines/orders_medallion/`**

1. Build a pipeline: Auto Loader bronze streaming tables for orders and
   customers → silver streaming tables with expectations (drop invalid rows,
   warn on suspicious values, fail on contract violations) → gold
   materialized views for daily revenue and customer lifetime value.
2. Build `silver.dim_customer` as **SCD Type 2** from a customer change feed
   using the automatic CDC API, including deletes and out-of-order changes.
3. Inject bad data and show each expectation action; query the event log
   for quality metrics.
4. Run in development mode, then production mode; perform a full refresh of
   one table only.
5. Parameterise the target catalog per environment.

**Checkpoint:**

- [ ] Explain streaming tables vs materialized views.
- [ ] Use expectations with the right actions.
- [ ] Build SCD Type 1 and 2 tables with the automatic CDC API.
- [ ] Monitor pipelines through the event log.
- [ ] Choose between declarative pipelines, custom jobs, and dbt.

**Common mistakes:** materialized views for append-only high-volume data
(or streaming tables for aggregations that need recomputation); `fail`
expectations on non-critical rules; ignoring expectation metrics; frequent
full refreshes of large tables.

---

### Topic 08 — [Lakeflow Jobs orchestration](08-lakeflow-jobs-orchestration.md)

**Why here:** Lakeflow Jobs is Databricks' built-in orchestrator. It runs
notebooks, Python packages, SQL, declarative pipelines, and dbt projects
with dependencies, triggers, retries, and monitoring — often replacing an
external orchestrator for Databricks-only platforms.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Jobs, **tasks**, and dependencies; task types: notebook, Python script or wheel, SQL, **pipeline**, **dbt**, run another job |
| Basics | Compute per task: jobs compute, shared job clusters, or serverless |
| Basics | Schedules, retries, timeouts, and notifications |
| Intermediate | **Triggers**: scheduled, **file arrival**, **table update**, and continuous |
| Intermediate | **Parameters**: job parameters, task parameters, dynamic value references (e.g. run date), and passing **task values** between tasks |
| Intermediate | Control flow: **if/else** conditions, **for-each** tasks for fan-out (e.g. per source table), and run-if dependencies |
| Intermediate | **Repair runs**: re-running only failed tasks and their dependents |
| Intermediate | Monitoring: run history, task logs, and alerting on failures and duration |
| Advanced | Backfills and reruns for past data intervals (Module 2.12) with job parameters |
| Advanced | Concurrency limits and queueing; avoiding overlapping runs |
| Advanced | **Lakeflow Jobs vs Airflow** (Module 2.13): when a Databricks-native orchestrator is enough and when a platform-wide orchestrator is needed; triggering Databricks from Airflow with its provider |
| Advanced | Running jobs as **service principals** in production |

**How to learn it**

1. Read the topic file.
2. Orchestrate the Topic 05–07 work as a multi-task job with a file-arrival
   trigger.
3. Fail one task on purpose and repair the run.

**Hands-on exercise — `resources/jobs/`**

1. Create a job: ingestion (Auto Loader) → declarative pipeline update →
   SQL quality check → `if/else` → publish (or alert).
2. Add a **for-each** task that ingests several partner sources with the
   same code and different parameters.
3. Trigger it on file arrival in the landing volume and on a daily schedule
   with a run-date parameter.
4. Fail a task, **repair** the run, and confirm only the failed path reruns.
5. Run the job as a service principal with minimal Unity Catalog grants.
6. Write a decision note: Lakeflow Jobs or Airflow for your platform.

**Checkpoint:**

- [ ] Build multi-task jobs with different task types and compute.
- [ ] Use triggers, parameters, task values, and control flow.
- [ ] Repair runs and backfill intervals.
- [ ] Choose between Lakeflow Jobs and an external orchestrator.

**Common mistakes:** jobs owned by and running as individual users; one
monolithic notebook task; all-purpose clusters for jobs; no alerts on
failures or long durations.

---

## 9. Phase D — Performance, Analytics, and Sharing (Advanced)

### Topic 09 — [Photon, performance, and predictive optimization](09-photon-performance-and-predictive-optimization.md)

**Why here:** Databricks adds its own performance features on top of Spark
and Delta. Knowing what they do — and what they cannot fix — lets you
deliver fast queries at a sensible cost.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Photon**: Databricks' vectorised query engine — which workloads benefit (SQL, joins, aggregations, Delta writes) and its cost implications |
| Basics | The **query profile** in Databricks SQL and the Spark UI for jobs |
| Intermediate | **Liquid clustering** on Databricks (Module 2.15 concept): choosing clustering keys, automatic clustering-key selection where available, and clustering incrementally |
| Intermediate | **Predictive optimization**: automatic `OPTIMIZE`, `VACUUM`, and statistics collection for Unity Catalog managed tables — enabling it and checking what it did |
| Intermediate | Data skipping with file statistics; the disk cache |
| Intermediate | Applying Module 2.14 tuning on Databricks: adaptive query execution, skew, broadcast joins, shuffle partitions |
| Advanced | Serverless performance settings and their cost trade-offs |
| Advanced | Deletion vectors and row-level operations performance |
| Advanced | Benchmarking fairly on Databricks (Module 2.21): warm vs cold, cache effects, and cost per query |
| Advanced | What performance features cannot fix: poor data models, huge scans without filters, Python UDF-heavy logic |

**How to learn it**

1. Read the topic file.
2. Run five typical gold queries with and without Photon, before and after
   liquid clustering; compare time and cost.
3. Enable predictive optimization and later inspect the operations it
   performed.

**Hands-on exercise — `docs/performance.md`**

1. Build a benchmark of five queries on a large table; record times, bytes
   read, and cost.
2. Apply liquid clustering on common filter columns; rerun the benchmark.
3. Compare Photon and non-Photon compute for a transformation job and a SQL
   query.
4. Enable predictive optimization on the lab catalog; after some days of
   writes, query what maintenance ran (system tables).
5. Read one query profile and explain its most expensive operator.

**Checkpoint:**

- [ ] Explain when Photon helps and what it costs.
- [ ] Apply liquid clustering on Databricks.
- [ ] Use predictive optimization and verify its effects.
- [ ] Read query profiles and apply Spark tuning on Databricks.

**Common mistakes:** expecting Photon to fix bad data models; clustering on
rarely filtered columns; running manual maintenance on top of predictive
optimization without coordination.

---

### Topic 10 — [Databricks SQL, AI/BI dashboards, and Genie](10-databricks-sql-ai-bi-dashboards-and-genie.md)

**Why here:** Gold tables are only useful when people can query and see
them. Databricks SQL, AI/BI dashboards, and Genie serve analysts and
business users directly from the lakehouse.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The **SQL editor**, query history, saved queries, and query parameters |
| Basics | **AI/BI dashboards**: datasets, visualisations, filters, scheduling, and sharing with permissions |
| Basics | **SQL alerts** on query results (e.g. freshness or threshold breaches) |
| Intermediate | Serving from **SQL warehouses** (Topic 02): sizing, scaling for concurrency, and auto-stop |
| Intermediate | Databricks SQL features for pipelines: materialized views and streaming tables created from SQL |
| Intermediate | **Genie** spaces: natural-language questions over curated tables, with instructions, example queries, and trusted assets |
| Intermediate | **Metric definitions** in Unity Catalog (e.g. metric views) as a semantic layer — check current availability (Module 2.22) |
| Advanced | Governing AI-assisted analytics: curating tables, certified metrics, row/column security, and reviewing generated SQL — never letting a model guess over raw tables (Module 2.22) |
| Advanced | Connecting external BI tools to SQL warehouses; query federation and caching |
| Advanced | Dashboard performance: pre-aggregated gold tables, clustering, and result caching |

**How to learn it**

1. Read the topic file.
2. Build a finance dashboard on your gold tables with filters and a
   schedule.
3. Create a Genie space over the same tables and test 20 real business
   questions; improve its instructions until answers are reliable.

**Hands-on exercise — `sql/analytics/`**

1. Write parameterised queries for daily revenue, top products, and
   conversion; build an AI/BI dashboard and share it with the analyst
   group.
2. Create an alert that fires when `gold.daily_revenue` is stale or drops
   more than 30% day over day.
3. Define certified metrics (e.g. net revenue, AOV) in the semantic layer
   feature available to you, and use them in the dashboard.
4. Create a Genie space with instructions, example SQL, and trusted assets;
   evaluate accuracy on your 20 questions and record failures.
5. Confirm that row filters and column masks apply in dashboards and Genie.

**Checkpoint:**

- [ ] Build parameterised queries, dashboards, and alerts.
- [ ] Size SQL warehouses for BI workloads.
- [ ] Curate and evaluate a Genie space responsibly.
- [ ] Keep metrics consistent and access-controlled in every interface.

**Common mistakes:** dashboards on silver or bronze tables; oversized
always-on warehouses; Genie spaces over raw tables without instructions or
evaluation; metrics defined differently in each dashboard.

---

### Topic 11 — [Delta Sharing and Marketplace](11-delta-sharing-and-marketplace.md)

**Why here:** Data often needs to reach partners, other business units, or
other platforms. Delta Sharing shares live data without copying or
building extracts.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Delta Sharing**: an open protocol for sharing data; **providers**, **shares**, and **recipients** |
| Basics | **Databricks-to-Databricks** sharing vs **open sharing** to recipients on other platforms (e.g. pandas, Spark, BI tools) |
| Intermediate | What can be shared: tables (with history and change data feed), views, volumes, and other assets depending on sharing type |
| Intermediate | Sharing subsets safely: partitions, views, and filters instead of whole tables; never exposing PII unintentionally |
| Intermediate | Recipient authentication and access revocation; auditing share access (system tables) |
| Intermediate | Consuming a share from Python with the open-source Delta Sharing client |
| Advanced | **Databricks Marketplace**: publishing and consuming data products and listings |
| Advanced | **Clean rooms** for privacy-safe collaboration on joint data — awareness |
| Advanced | Delta Sharing vs file exports vs APIs (Module 2.22) vs warehouse data sharing (Gap Module G3) |

**How to learn it**

1. Read the topic file.
2. Share a gold view with a recipient and read it from Python outside
   Databricks with the open-source client.
3. Revoke access and confirm the recipient loses it.

**Hands-on exercise — `sql/sharing/`**

1. Create a share with a partner-specific view of `gold.orders` (filtered to
   the partner, PII removed).
2. Create an open-sharing recipient; read the share with the Python client
   into pandas.
3. Share with change data feed and read incremental changes as a recipient.
4. Audit who accessed the share and when.
5. Revoke the recipient and verify.
6. Write a decision table: Delta Sharing vs API vs file export for three
   partner scenarios.

**Checkpoint:**

- [ ] Create shares and recipients for Databricks and non-Databricks
      consumers.
- [ ] Share safe subsets and audit access.
- [ ] Explain Marketplace and clean rooms at a high level.

**Common mistakes:** sharing whole tables with PII; never revoking old
recipients; copying data to partners when a live share would do.

---

## 10. Phase E — Delivery, Cost, and ML Handoff (Advanced)

### Topic 12 — [Databricks Asset Bundles and CI/CD](12-databricks-asset-bundles-and-ci-cd.md)

**Why here:** Everything you built by clicking must become code, reviewed
in pull requests and deployed identically to dev, staging, and production.
Asset Bundles are Databricks' way to do this (Module 2.18 applied to
Databricks).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What a **bundle** is: project files plus resource definitions (jobs, pipelines, and other resources) in YAML, deployed together |
| Basics | `databricks.yml`: bundle name, **targets** (dev, staging, prod), workspace settings, variables |
| Basics | The CLI workflow: `bundle validate`, `bundle deploy`, `bundle run`, `bundle destroy` |
| Intermediate | **Development mode** (per-user prefixes, paused schedules) vs **production mode** (run as a service principal, guarded settings) |
| Intermediate | Building and deploying Python wheels with the bundle; referencing them from jobs and pipelines |
| Intermediate | Per-target overrides: catalogs, compute sizes, schedules, and permissions |
| Intermediate | **CI/CD** with GitHub Actions (or similar): lint and unit tests → validate → deploy to dev and run integration tests → deploy to staging → approval → deploy to prod |
| Intermediate | **Authentication for CI**: service principals and workload identity federation (OIDC) instead of personal tokens (Modules 2.17–2.18) |
| Advanced | Bundles vs the Terraform provider: bundles for jobs and pipelines, Terraform for workspaces, Unity Catalog objects, and cloud infrastructure |
| Advanced | Integration tests against a dev target with small data; data diffs before promotion (Module 2.19) |
| Advanced | Rollback: redeploying a previous bundle version and restoring tables with time travel (Module 2.15) |

**How to learn it**

1. Read the topic file.
2. Convert your lab jobs and pipelines into a bundle with dev and prod
   targets.
3. Build a CI/CD workflow that deploys through environments with a service
   principal.

**Hands-on exercise — `databricks.yml` and `.github/workflows/`**

1. Define the ingestion job, declarative pipeline, and quality job as bundle
   resources with variables for catalog, schedule, and compute.
2. Deploy to `dev` in development mode and confirm resource name prefixes
   and paused schedules.
3. Build a CI workflow: unit tests → `bundle validate` → deploy to dev →
   run an integration job → deploy to prod after approval, authenticating
   with a service principal via OIDC.
4. Deliberately break a resource definition and see CI fail at validation.
5. Roll back production to the previous version.

**Checkpoint:**

- [ ] Define jobs and pipelines as bundle resources with targets.
- [ ] Deploy through environments from CI with service principals.
- [ ] Choose between bundles and Terraform for different resources.

**Common mistakes:** production resources created by hand; personal access
tokens in CI; the same catalog used for dev and prod; skipping validation
and integration runs.

---

### Topic 13 — [Cost management and system tables](13-cost-management-and-system-tables.md)

**Why here:** Databricks bills by usage units (DBUs) on top of cloud
infrastructure (for classic compute). Without attribution and controls,
costs grow quietly; with system tables, you can see exactly who spends what.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Billing basics: **DBUs**, product SKUs (jobs, all-purpose, SQL, serverless, pipelines), and cloud infrastructure costs for classic compute |
| Basics | **System tables**: billing usage and list prices, compute, jobs and pipeline runs, query history, and audit logs — queried with SQL |
| Intermediate | **Cost attribution**: custom tags on compute, jobs, and warehouses; serverless budget policies; mapping spend to teams, pipelines, and data products (Module 2.21) |
| Intermediate | Controls: compute policies, auto-termination and auto-stop, warehouse sizing, and job compute instead of all-purpose |
| Intermediate | Dashboards and alerts on spend trends and anomalies |
| Intermediate | **Audit** with system tables: who accessed which tables, and who changed permissions (Module 2.20) |
| Advanced | Comparing serverless vs classic cost for your workloads with real data |
| Advanced | Unit costs: cost per pipeline run, per dashboard, per TB processed |
| Advanced | Budgets and account-level cost reporting — awareness of what your account tier exposes |

**How to learn it**

1. Read the topic file.
2. Tag every compute resource, job, and warehouse in your lab.
3. Write SQL over system tables to answer: "what did each pipeline cost last
   week, and what drove it?"

**Hands-on exercise — `sql/cost/`**

1. Write queries over billing system tables joined with list prices to
   compute cost per tag (pipeline, team, environment) per day.
2. Build a cost dashboard with an alert on day-over-day spikes.
3. Find the most expensive jobs and queries, and the idle warehouse time.
4. Implement at least two optimisations (e.g. switch a job to serverless or
   smaller compute, add auto-stop, cluster a table) and measure savings.
5. Query audit system tables to list who accessed gold PII tables.

**Checkpoint:**

- [ ] Explain DBUs and cost components.
- [ ] Attribute cost with tags and system tables.
- [ ] Control spend with policies and settings.
- [ ] Audit access with system tables.

**Common mistakes:** untagged compute; interactive clusters doing
production work; warehouses that never stop; looking at total monthly spend
only after the bill arrives.

---

### Topic 14 — [MLflow and feature engineering handoff](14-mlflow-and-feature-engineering-handoff.md)

**Why last:** On Databricks, data engineering and ML share one platform.
The data engineer's job is to hand ML teams governed, reproducible,
point-in-time-correct data — and to understand the tools they use.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **MLflow** essentials for data engineers: experiments, runs, parameters, metrics, artefacts, and models |
| Basics | **Models in Unity Catalog**: registering models with versions and aliases, governed like tables |
| Intermediate | **Feature engineering in Unity Catalog**: feature tables as Delta tables with primary keys (and timestamp keys), owned and governed in Unity Catalog |
| Intermediate | **Point-in-time lookups** for training sets (Module 2.22): creating training datasets that use only feature values known at each label's time |
| Intermediate | Reproducible training data: logging dataset versions (Delta table versions) and lineage from tables to models |
| Intermediate | Batch inference pipelines writing predictions to gold tables as jobs (Topic 08) |
| Advanced | **Online serving of features** and models (online feature stores and model serving) — awareness of current offerings |
| Advanced | **Vector search** for retrieval pipelines (Module 2.22) — awareness |
| Advanced | Monitoring data and prediction drift with lakehouse monitoring tools — awareness |
| Advanced | The handoff contract with ML teams: schemas, freshness, point-in-time rules, and ownership (Module 2.22) |

**How to learn it**

1. Read the topic file.
2. Create customer features from your gold tables as a feature table and
   build a point-in-time-correct training set.
3. Train a tiny model (or use a baseline) with MLflow and register it in
   Unity Catalog; check lineage from tables to the model.

**Hands-on exercise — `src/lab/features/`**

1. Create `features.customer_daily` (primary key `customer_id`, timestamp
   key `as_of_date`) with churn-relevant features, built by a scheduled job.
2. Create a training set with point-in-time lookups against churn labels;
   prove no leakage by recomputing a sample by hand.
3. Log a simple model with MLflow, including the training table's Delta
   version, and register it in Unity Catalog.
4. Run a batch-inference job writing predictions to `gold.churn_scores`.
5. Write a handoff document for the ML team (Module 2.22 template).

**Checkpoint:**

- [ ] Explain MLflow runs, models, and Unity Catalog model governance.
- [ ] Build feature tables and point-in-time-correct training sets.
- [ ] Make training data reproducible and traceable.
- [ ] Hand off data to ML teams with a clear contract.

**Common mistakes:** feature logic duplicated in training and serving;
training sets joined with current feature values (leakage); models trained
on unversioned data.

---

## 11. Consolidate — practice, interviews, and certification

### [`practice-questions.md`](practice-questions.md)

For every question:

1. Identify the workload and its requirements (latency, volume, governance,
   cost).
2. Choose Databricks features and justify them against alternatives
   (including non-Databricks options from Stage 2).
3. Define Unity Catalog objects, grants, and compute.
4. Implement it in your lab as bundle resources where possible.
5. Measure behaviour and cost with system tables.

### [`interview-practice.md`](interview-practice.md)

Databricks interviews mix platform features, Spark and Delta depth, and
design. Practise out loud with a **30-minute timer**:

- design a medallion lakehouse on Databricks with Unity Catalog governance;
- ingest SaaS, database, and file sources — which ingestion option for
  each?;
- declarative pipelines vs hand-written Structured Streaming jobs vs dbt;
- implement SCD Type 2 from a CDC feed;
- a job's cost doubled — how do you find out why?;
- set up dev/staging/prod with bundles and CI/CD;
- share curated data with an external partner securely;
- hand features to an ML team without leakage.

### [`certification-prep-databricks-data-engineer.md`](certification-prep-databricks-data-engineer.md)

Databricks offers **Data Engineer Associate** and **Data Engineer
Professional** certifications. Preparation plan:

1. Download the **current exam guides** (they are updated as products are
   renamed) and map every objective to a topic here and to Stage 2 modules.
2. Use the official Databricks Academy learning paths and documentation.
3. Practise hands-on for every objective you have not used in a real
   exercise — especially Unity Catalog permissions, declarative pipelines,
   Auto Loader, jobs, and Delta operations.
4. Take practice exams; for every wrong answer, record why the correct
   answer is right and why each distractor is wrong.
5. Take the Associate first; attempt the Professional after the mini-project
   and real-world practice.

---

## 12. Module mini-project — a Databricks lakehouse platform

This mini-project is expanded in
[`../00-Gap-Modules-Overview/Projects/04-databricks-lakehouse-platform.md`](../00-Gap-Modules-Overview/Projects/04-databricks-lakehouse-platform.md).
The short version:

**Goal:** Rebuild the core of your Stage 2 orders platform on Databricks —
governed by Unity Catalog, built with declarative pipelines, orchestrated by
Lakeflow Jobs, deployed with Asset Bundles, and cost-attributed.

1. **Governance:** dev and prod catalogs; bronze/silver/gold schemas;
   landing volumes; group-based grants; row filters and column masks on PII;
   tags; lineage.
2. **Ingestion:** Auto Loader for clickstream and partner files; Lakeflow
   Connect (or Kafka streaming) for orders and customers.
3. **Pipelines:** a declarative pipeline with expectations (warn, drop,
   fail), SCD Type 2 customers from CDC, and gold materialized views.
4. **Orchestration:** a Lakeflow Job with file-arrival and schedule
   triggers, for-each ingestion, quality checks with `if/else`, repair runs,
   and alerts — running as a service principal.
5. **Analytics:** AI/BI finance dashboard, SQL alerts on freshness,
   certified metrics, and an evaluated Genie space.
6. **Sharing and ML:** a partner Delta Share without PII; a customer feature
   table with a point-in-time training set and a registered model.
7. **Delivery:** everything in an Asset Bundle with dev and prod targets,
   deployed by CI/CD with OIDC and tests.
8. **Cost and performance:** tags everywhere, system-table cost dashboard,
   predictive optimization, liquid clustering, and a before/after
   performance and cost report.

**Grading yourself:** the whole platform deploys to a fresh target from the
bundle; each persona sees only permitted rows and columns in every
interface; bad data is handled according to expectations; every pipeline's
cost is visible per day; and a new engineer can run the project from the
README.

---

## 13. Module self-assessment — exit criteria

Tick every box without looking at your notes:

- [ ] I can explain Databricks' architecture and set up identities and
      workspaces sensibly.
- [ ] I can choose and control compute for every workload type.
- [ ] I can structure Databricks projects as tested packages in Git.
- [ ] I can design and operate Unity Catalog governance, including volumes,
      external locations, filters, masks, lineage, and audit.
- [ ] I can ingest files with Auto Loader and sources with Lakeflow Connect.
- [ ] I can build declarative pipelines with expectations and SCD handling.
- [ ] I can orchestrate with Lakeflow Jobs, including triggers and repair.
- [ ] I can tune performance with Photon, clustering, and predictive
      optimization.
- [ ] I can serve analytics with Databricks SQL, dashboards, and a curated
      Genie space.
- [ ] I can share data with Delta Sharing securely.
- [ ] I can deploy with Asset Bundles through CI/CD.
- [ ] I can attribute and control cost with system tables.
- [ ] I can hand off governed, point-in-time-correct data to ML.
- [ ] I have finished the practice questions, interview practice, and the
      mini-project (and, optionally, a certification).

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| Databricks documentation (for your cloud): architecture, compute, Unity Catalog, Auto Loader, Lakeflow Connect, Lakeflow Declarative Pipelines, Lakeflow Jobs, Databricks SQL, AI/BI and Genie, Delta Sharing, Asset Bundles, system tables, MLflow and feature engineering | All topics |
| Databricks Academy learning paths for data engineering | All topics, certification |
| Current Databricks Certified Data Engineer Associate and Professional exam guides | Certification prep |
| *Delta Lake: The Definitive Guide* (O'Reilly) — for the Delta foundations behind the platform | 07, 09, 11 |
| Databricks Terraform provider and Databricks CLI documentation | 01, 12 |
| Open-source Delta Sharing and Unity Catalog project documentation | 04, 11 |
| Databricks engineering blog — product announcements and best practices (watch for renames) | All topics |

---

## 15. Where this module leads

| This module's skill | Where you use it next |
| --- | --- |
| A complete Databricks lakehouse | Stage 2 **Capstone** (Project 07) — Option B on Databricks |
| Platform trade-offs and reference designs | Gap Module G5 — Data Engineering System Design Interviews |
| Unity Catalog governance and Delta Sharing | Governance evidence for the capstone and any Databricks role |
| Feature engineering, MLflow, vector search | Applied AI and Agentic AI stages built on Databricks |

A managed platform does much of the heavy lifting you learned to do by hand
in Stage 2 — and that is exactly why the Stage 2 foundations matter: you can
now judge what the platform does for you, what it hides, and when to step
outside it. The habits you build here — govern everything in Unity Catalog,
develop as code and deploy with bundles, run production as service
principals on the cheapest adequate compute, enforce expectations, and
track cost in system tables — are what Databricks data engineering roles
expect.
