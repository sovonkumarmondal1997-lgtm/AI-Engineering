# Roadmap — Module 2C.5: Azure Data Engineering and Microsoft Fabric

This is the learning roadmap for the fifth module of Stage 2C, **Data
Engineering_3**. It tells you **what** to learn about data engineering on
Microsoft Azure and Microsoft Fabric, **in what order**, **how** to learn
each topic, and **how to prove to yourself** that you have learned it
before you move on.

Azure is the dominant cloud in many large enterprises, especially those
already using Microsoft 365, Active Directory, and SQL Server. Azure data
engineering jobs are common, and the platform has changed fast: Azure
Synapse Analytics is being succeeded by **Microsoft Fabric**, a unified
SaaS platform built on **OneLake** and Delta tables. A data engineer today
must understand both the classic services (ADLS Gen2, Data Factory,
Synapse, Event Hubs) and Fabric.

Most of the concepts are ones you already know from AWS, GCP, and
Databricks (Stage 2B and Modules 2C.3–2C.4). This module teaches where
Azure **names**, **packages**, and **bills** them differently.

---

## 1. Module outcome

By the end of this module you will be able to:

- Map Azure data services to their AWS/GCP equivalents and choose among
  them.
- Design storage on **ADLS Gen2** (hierarchical namespace, ACLs, tiers) and
  Blob Storage.
- Build pipelines with **Azure Data Factory**: linked services, datasets,
  activities, triggers, and **mapping data flows**.
- Explain Synapse **dedicated** and **serverless** SQL pools and when each
  fits.
- Build streaming ingestion with **Event Hubs** and **Stream Analytics**.
- Build a lakehouse in **Microsoft Fabric**: OneLake, lakehouses,
  warehouses, notebooks, pipelines, and Direct Lake.
- Integrate **Azure Databricks** with ADLS, Unity Catalog, and ADF.
- Secure the platform with **Microsoft Entra ID**, RBAC, managed
  identities, and **Key Vault**.
- Govern data with **Microsoft Purview**: catalog, classification, and
  lineage.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| SQL, T-SQL familiarity helps | Stage 2 — Module 2.6 | Synapse and Fabric warehouses use T-SQL |
| ETL/ELT, orchestration, triggers | Stage 2 — Modules 2.1, 2.13 | Data Factory concepts |
| Parquet, Delta, medallion | Stage 2 — Modules 2.5, 2.15 | OneLake stores Delta |
| Spark | Stage 2 — Module 2.14 | Fabric notebooks, Synapse Spark, Databricks |
| Kafka and streaming concepts | Stage 2 — Module 2.16 | Event Hubs has a Kafka endpoint |
| Cloud IAM and storage | Stage 2 — Module 2.17; Stage 2B — 2B.3 | The Azure equivalents |
| Databricks and Unity Catalog | Stage 2B — Module 2B.4 | Azure Databricks integration |
| Secrets and CI/CD | Stage 2 — Module 2.18 | Key Vault, deployment |
| Governance and lineage | Stage 2 — Module 2.20 | Purview |

**Tools needed:**

- An **Azure free account** or Visual Studio subscription; a **Microsoft
  Fabric trial capacity** (check availability in your region). Set a
  **budget alert** and a spending limit first.
- Azure CLI (`az`), Bicep or Terraform, and Python 3.12+ in a `uv`
  project: `uv add azure-identity azure-storage-file-datalake
  azure-eventhub azure-keyvault-secrets pyspark pytest`.
- Azure Storage Explorer, VS Code with Azure extensions.

**A note on versions:** Azure product names and features change often
(Synapse → Fabric, Azure AD → Entra ID, Data Factory in Fabric). Treat
tutorials older than a year with caution and check the official docs.

---

## 3. How the module is organised

The nine topics are grouped into five phases. Work through them **in order**.

```text
Phase A — The Platform                               (Basics)
  01 Azure data services landscape

Phase B — Storage and Integration                    (Intermediate)
  02 ADLS Gen2 and Blob Storage
  03 Azure Data Factory: pipelines and mapping data flows

Phase C — Analytics and Streaming                    (Intermediate → Advanced)
  04 Synapse Analytics: dedicated and serverless pools
  05 Event Hubs and Stream Analytics

Phase D — The Unified Platform                       (Advanced)
  06 Microsoft Fabric: lakehouse and OneLake
  07 Azure Databricks integration

Phase E — Security and Governance                    (Advanced)
  08 Entra ID, RBAC, and Key Vault
  09 Purview: governance and lineage

Consolidate
  Module mini-project: an Azure medallion platform
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09
map  store move  query stream unify  Spark secure govern
                 SQL            (Fabric)
```

Why this order:

- Storage (02) comes before everything that reads or writes it.
- Data Factory (03) moves data into storage; Synapse (04) and Event Hubs
  (05) query and stream it.
- Fabric (06) unifies those services; Databricks (07) is the main
  alternative engine.
- Identity and secrets (08) apply to all; Purview (09) governs the whole.

---

## 4. Suggested schedule

About **5 weeks at 8 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — landscape · Topic 02 — ADLS Gen2 |
| 2 | Topic 03 — Data Factory |
| 3 | Topic 04 — Synapse · Topic 05 — Event Hubs and Stream Analytics |
| 4 | Topic 06 — Fabric · Topic 07 — Azure Databricks |
| 5 | Topic 08 — Entra ID and Key Vault · Topic 09 — Purview · mini-project |

---

## 5. How to study every topic (the Azure loop)

```text
Read → Map to AWS/GCP → Build with code (Bicep/Terraform/CLI) → Run it
→ Check identity and network → Break a permission → Inspect cost
→ Clean up → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Map** each service to a twin you already know.
3. **Build** with Bicep/Terraform or `az` scripts, not only the portal.
4. **Run it** with small data.
5. **Check identity**: which principal accessed what, and via which role.
6. **Break a permission** and read the error.
7. **Inspect cost** in Cost Management.
8. **Clean up** the resource group.
9. **Write it down** in `module-2c5-notes.md`.
10. **Explain aloud** the data flow and who is allowed to do what.

Keep one `azure_lab/` project:

```text
azure_lab/
├── infra/               # Bicep or Terraform: storage, ADF, Event Hubs, Key Vault, Fabric items
├── adf/                 # pipeline, dataset, and data flow JSON (Git-integrated)
├── notebooks/           # Fabric / Databricks / Synapse notebooks
├── sql/                 # T-SQL for Synapse and Fabric warehouses
├── streaming/           # Event Hubs producers and Stream Analytics queries
├── governance/          # RBAC assignments, Purview scans
└── tests/
```

---

## 6. Phase A — The Platform (Basics)

### Topic 01 — [Azure data services landscape](01-azure-data-services-landscape.md)

**Why it comes first:** Azure has many overlapping and renamed services. A
map prevents confusion and expensive mistakes.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Tenants, management groups, subscriptions, resource groups, regions; the portal, `az` CLI, Bicep/ARM, and Terraform |
| Basics | Core data services: **ADLS Gen2**, **Data Factory**, **Synapse Analytics**, **Event Hubs**, **Stream Analytics**, **Azure Databricks**, **Azure SQL / SQL MI / Cosmos DB**, **Microsoft Fabric**, **Purview**, **Power BI** |
| Basics | Mapping: S3↔ADLS, Glue/ADF↔Data Factory, Redshift/BigQuery↔Synapse/Fabric Warehouse, Kinesis↔Event Hubs, EMR↔HDInsight/Databricks/Fabric Spark, Lake Formation↔Purview + RBAC |
| Intermediate | The **Fabric era**: how Fabric replaces and absorbs Synapse, ADF (as Fabric Data Factory), Power BI, and Event Streams; what stays separate |
| Intermediate | Reference architectures: classic modern data warehouse, Databricks lakehouse on ADLS, and Fabric end-to-end |
| Intermediate | Networking basics: VNets, private endpoints, service endpoints, and firewalls on storage |
| Advanced | Landing zones, naming/tagging standards, and cost management (budgets, tags, reservations) |
| Advanced | Region and capacity planning, SKUs/tiers, and licensing models (Fabric capacities F SKUs, pay-as-you-go vs reserved) |
| Advanced | Choosing Fabric vs Databricks vs Synapse for a new project and for a migration |

**How to learn it**

1. Read the topic file.
2. Fill a mapping table AWS/GCP → Azure for ten services.
3. Draw the classic architecture and the Fabric architecture side by side.

**Hands-on exercise — `experiments/01_landscape/`**

1. Create a resource group, budget alert, and tags with Bicep/Terraform.
2. Deploy a storage account and a Key Vault; view them in Cost Management.
3. Write a one-page "which service for which job" guide.

**Checkpoint:**

- [ ] Map Azure services to AWS/GCP twins.
- [ ] Explain how Fabric relates to Synapse and Power BI.
- [ ] Choose among Fabric, Databricks, and Synapse.

**Common mistakes:** following Synapse-only tutorials for a Fabric
decision; no tags or budgets; public network access left open.

---

## 7. Phase B — Storage and Integration (Intermediate)

### Topic 02 — [ADLS Gen2 and Blob Storage](02-adls-gen2-and-blob-storage.md)

**Why here:** every Azure data platform sits on ADLS Gen2. Its
hierarchical namespace and ACL model differ from S3 in ways that matter for
performance and security.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Storage accounts, containers, blobs; **hierarchical namespace (HNS)** turns Blob into ADLS Gen2 with real directories |
| Basics | Redundancy options: LRS, ZRS, GRS, GZRS; performance tiers (Standard vs Premium) |
| Basics | Access tiers: hot, cool, cold, archive; lifecycle management policies |
| Basics | Access via `abfss://` URIs, Storage Explorer, `azcopy`, and the Python SDK |
| Intermediate | Why HNS matters: atomic directory renames, faster listings, and POSIX-style **ACLs** |
| Intermediate | Authorisation layers: Azure RBAC (data roles like Storage Blob Data Contributor), ACLs, shared access signatures (SAS), and account keys — and the order of evaluation |
| Intermediate | Lake layout for medallion: containers/folders per zone, partitioning by date, naming conventions (links to Module 2.5) |
| Intermediate | Python: `azure-storage-file-datalake`, `adlfs`/`fsspec`, and Spark/Pandas access (Module 2.17) |
| Advanced | Security: private endpoints, firewalls, managed identities, encryption with customer-managed keys, immutability (WORM) policies |
| Advanced | Performance and limits: request rates, parallel `azcopy`, small-file overhead, and throughput scaling |
| Advanced | Soft delete, versioning, change feed, and point-in-time restore for recovery |
| Advanced | Cost levers: tiering, lifecycle rules, transaction costs, and egress |

**How to learn it**

1. Read the topic file.
2. Design a container and folder layout for bronze/silver/gold for three
   source systems.
3. Write the RBAC + ACL grants needed for a pipeline identity and an
   analyst group.

**Hands-on exercise — `experiments/02_adls/`**

1. Create an HNS-enabled account with Bicep; upload a dataset with `azcopy`.
2. Rename a large directory in ADLS and in plain Blob storage (no HNS);
   compare the time.
3. Set ACLs on a folder and verify access for two identities.
4. Add a lifecycle policy that moves old data to cool and deletes it later.
5. Read Parquet from ADLS in Python and Spark using a managed identity or
   service principal.

**Checkpoint:**

- [ ] Explain ADLS Gen2 vs Blob and why HNS matters.
- [ ] Combine RBAC and ACLs correctly.
- [ ] Design a medallion layout.
- [ ] Apply lifecycle and tiering.

**Common mistakes:** account keys in code; forgetting that ACLs need
execute permission on parent folders; using SAS tokens as the main
security model; ignoring transaction costs.

---

### Topic 03 — [Azure Data Factory: pipelines and mapping data flows](03-azure-data-factory-pipelines-and-mapping-data-flows.md)

**Why here:** Data Factory (ADF) is Azure's main data-movement and
orchestration service, and the model carries into Fabric Data Factory.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The building blocks: **linked services**, **datasets**, **activities**, **pipelines**, **triggers**, **integration runtimes** (Azure, self-hosted, Azure-SSIS) |
| Basics | The **Copy activity**: sources, sinks, parallelism, and data integration units (DIUs); the connector catalogue |
| Basics | Triggers: schedule, tumbling window, storage event, and custom event |
| Intermediate | Control flow: `ForEach`, `If`, `Switch`, `Until`, `Execute Pipeline`, `Lookup`, `Get Metadata`, `Web`; parameters, variables, and dynamic content expressions |
| Intermediate | **Metadata-driven pipelines**: one parameterised pipeline driven by a control table (links to Module 2.12) |
| Intermediate | **Incremental loads**: watermark columns, change tracking, CDC resources, and tumbling-window triggers with `windowStart`/`windowEnd` |
| Intermediate | **Mapping data flows**: visual Spark-based transformations (source, join, aggregate, derived column, window, sink); debug clusters; schema drift handling |
| Intermediate | Error handling: retries, timeouts, failure paths, and logging to a table |
| Advanced | Git integration, environments, CI/CD with ARM/Bicep publishing, and global parameters |
| Advanced | Self-hosted integration runtime for on-prem sources; networking and managed virtual networks |
| Advanced | Cost and performance: DIU tuning, data flow cluster TTL, and avoiding per-activity overhead for tiny loads |
| Advanced | When ADF is the wrong tool: heavy transformations (use Spark/dbt), complex dependencies (Airflow) — and ADF triggering Databricks/dbt |

**How to learn it**

1. Read the topic file.
2. Design a metadata-driven pipeline for 20 source tables with a control
   table.
3. Plan an incremental load with a tumbling window trigger.

**Hands-on exercise — `experiments/03_adf/`**

1. Create a Copy pipeline from Azure SQL (or a public API) to ADLS Parquet.
2. Make it metadata-driven with `Lookup` + `ForEach` over a control table.
3. Add a watermark-based incremental load with a stored procedure to
   update the watermark.
4. Build a mapping data flow that deduplicates and aggregates.
5. Put the factory in Git and deploy to a second environment with
   parameters.
6. Add failure alerting.

**Checkpoint:**

- [ ] Build parameterised, metadata-driven pipelines.
- [ ] Implement incremental loads.
- [ ] Use data flows and know their cost.
- [ ] Promote ADF between environments.

**Common mistakes:** one pipeline per table; hard-coded connection
strings; leaving data flow debug clusters running; using ADF for complex
transformation logic.

---

## 8. Phase C — Analytics and Streaming (Intermediate → Advanced)

### Topic 04 — [Synapse Analytics: dedicated and serverless pools](04-synapse-analytics-dedicated-and-serverless-pools.md)

**Why here:** Synapse is the incumbent Azure analytics service in many
companies. You will maintain or migrate it even as Fabric grows.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The Synapse workspace: dedicated SQL pools, serverless SQL pool, Spark pools, pipelines, and Synapse Studio |
| Basics | **Serverless SQL pool**: query files in ADLS with T-SQL (`OPENROWSET`, external tables), pay per TB processed |
| Basics | **Dedicated SQL pool** (formerly SQL DW): MPP architecture, DWUs, pause/resume |
| Intermediate | Dedicated pool design: **distribution** (hash, round-robin, replicated), partitioning, **clustered columnstore** indexes |
| Intermediate | Loading with `COPY INTO` and PolyBase; CTAS patterns; avoiding data movement (`ShuffleMove`) |
| Intermediate | Statistics, workload management (workload groups, classifiers), and result-set caching |
| Intermediate | Synapse Spark pools and notebooks; linked services and pipelines |
| Advanced | Serverless patterns: logical data warehouse over a lake, views with security, partition elimination with `filepath()` |
| Advanced | Performance tuning with DMVs, query plans, and skew analysis |
| Advanced | Cost control: pause dedicated pools, serverless cost limits, and tier decisions |
| Advanced | **Migration to Fabric**: what Fabric Warehouse/Lakehouse replaces and the migration paths (and Synapse's lifecycle status — check current guidance) |

**How to learn it**

1. Read the topic file.
2. Choose distribution keys for a fact and three dimensions.
3. Decide serverless vs dedicated for five workloads.

**Hands-on exercise — `experiments/04_synapse/`**

1. Query Parquet in ADLS with the serverless pool; compare cost for
   `SELECT *` vs selected columns and with partition elimination.
2. Create a dedicated pool; load a fact table with `COPY INTO` using hash
   vs round-robin distribution; compare join speed.
3. Inspect data movement in the execution plan.
4. Create a workload group and classifier.
5. Pause the pool and document the cost impact.

**Checkpoint:**

- [ ] Choose serverless vs dedicated.
- [ ] Choose distributions and columnstore appropriately.
- [ ] Load efficiently with `COPY INTO`.
- [ ] Explain the path from Synapse to Fabric.

**Common mistakes:** round-robin everything; leaving dedicated pools
running; skewed hash keys; building new systems on Synapse without
checking its roadmap.

---

### Topic 05 — [Event Hubs and Stream Analytics](05-event-hubs-and-stream-analytics.md)

**Why here:** Azure's streaming ingestion and simple stream processing
(concepts from Module 2.16 in Azure form).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Event Hubs**: namespaces, event hubs, partitions, throughput/processing units, retention, and consumer groups |
| Basics | The Kafka-compatible endpoint: using Kafka clients against Event Hubs |
| Basics | Sending and receiving with the Python SDK (`azure-eventhub`); checkpointing in Blob storage |
| Intermediate | Event Hubs **Capture**: automatic archival to ADLS as Avro/Parquet |
| Intermediate | Schema Registry for Event Hubs; partition keys and ordering |
| Intermediate | **Azure Stream Analytics**: jobs, inputs, outputs, the SQL-like query language, windowing (tumbling, hopping, sliding, session), temporal joins, reference data |
| Intermediate | Streaming units, late arrival and out-of-order policies, and watermarks |
| Advanced | Outputs: ADLS, Synapse, Cosmos DB, Power BI, Event Hubs; exactly-once and idempotency considerations |
| Advanced | Alternatives for heavier processing: Spark Structured Streaming on Databricks/Fabric, Flink on Azure, Fabric Real-Time Intelligence (Eventstream, Eventhouse/KQL) |
| Advanced | Monitoring: lag, throttling, backlogged events, and alerting; scaling throughput units |
| Advanced | IoT Hub vs Event Hubs; geo-disaster recovery |
| Advanced | Choosing Event Hubs/Stream Analytics vs Kafka vs Pub/Sub vs Kinesis |

**How to learn it**

1. Read the topic file.
2. Map Event Hubs concepts to Kafka's (partitions, consumer groups,
   offsets).
3. Write a windowed aggregation in Stream Analytics SQL.

**Hands-on exercise — `experiments/05_eventhubs_asa/`**

1. Deploy an Event Hub with Capture to ADLS; send 100k events from Python
   and confirm archived files.
2. Consume with checkpointing; kill and restart the consumer.
3. Build a Stream Analytics job: 1-minute tumbling window per device,
   output to ADLS and Power BI (or Synapse).
4. Send late events and tune the late-arrival policy.
5. Use a Kafka client against the Event Hubs endpoint.

**Checkpoint:**

- [ ] Explain partitions, consumer groups, and Capture.
- [ ] Write Stream Analytics window queries.
- [ ] Handle late data.
- [ ] Choose a stream processing engine for a workload.

**Common mistakes:** too few partitions; no checkpointing; Stream
Analytics for complex stateful logic; ignoring throughput limits.

---

## 9. Phase D — The Unified Platform (Advanced)

### Topic 06 — [Microsoft Fabric: lakehouse and OneLake](06-microsoft-fabric-lakehouse-and-onelake.md)

**Why here:** Fabric is Microsoft's strategic analytics platform. It
combines storage, engines, pipelines, real-time analytics, and BI behind
one capacity and one lake.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Fabric as SaaS: tenant, **capacities** (F SKUs), **workspaces**, and the experiences (Data Engineering, Data Factory, Data Warehouse, Real-Time Intelligence, Data Science, Power BI) |
| Basics | **OneLake**: one logical lake per tenant, Delta/Parquet as the storage format, shortcuts, and the `abfss://` OneLake endpoint |
| Basics | **Lakehouse** items: Files vs Tables, the SQL analytics endpoint, and notebooks |
| Intermediate | **Shortcuts** to ADLS, S3, GCS, and other lakehouses: virtual access without copying |
| Intermediate | Spark in Fabric: notebooks, Spark job definitions, environments, V-Order optimisation, and Delta maintenance (OPTIMIZE, VACUUM) |
| Intermediate | **Fabric Data Warehouse** (T-SQL over Delta), cross-database queries, and when to choose lakehouse vs warehouse |
| Intermediate | **Data pipelines** and Dataflows Gen2; mirroring (replicating Azure SQL, Snowflake, Cosmos DB into OneLake) |
| Intermediate | **Direct Lake** mode: Power BI reading Delta files directly; semantic models |
| Advanced | Medallion architecture in Fabric: workspaces per layer, deployment pipelines, Git integration, and CI/CD |
| Advanced | Capacity management: Capacity Metrics app, smoothing and throttling, workload isolation, and cost control |
| Advanced | Security: workspace roles, item permissions, OneLake data access roles, row- and column-level security, sensitivity labels |
| Advanced | Real-Time Intelligence: Eventstream, Eventhouse (KQL) — awareness; Fabric Data Science and Copilot — awareness |
| Advanced | Fabric vs Databricks vs Snowflake: strengths, lock-in, and interoperability via Delta/Iceberg |

**How to learn it**

1. Read the topic file.
2. Draw a medallion design with workspaces, lakehouses, a warehouse, and a
   semantic model.
3. Decide for five datasets: lakehouse table, warehouse table, or
   shortcut.

**Hands-on exercise — `experiments/06_fabric/`**

1. Create a workspace and lakehouse; ingest CSV into Files and convert to
   Delta tables with a notebook.
2. Add a shortcut to an ADLS folder and query it without copying.
3. Query the lakehouse through the SQL analytics endpoint; build a
   warehouse gold layer with T-SQL.
4. Orchestrate the flow with a data pipeline; schedule it.
5. Build a Power BI semantic model in Direct Lake mode.
6. Review the Capacity Metrics app after your load.

**Checkpoint:**

- [ ] Explain OneLake, shortcuts, and capacities.
- [ ] Build a bronze→silver→gold flow in Fabric.
- [ ] Choose lakehouse vs warehouse.
- [ ] Explain Direct Lake and capacity throttling.

**Common mistakes:** one giant workspace; ignoring capacity limits;
copying data that a shortcut could reach; applying security only at the
Power BI layer.

---

### Topic 07 — [Azure Databricks integration](07-azure-databricks-integration.md)

**Why here:** Azure Databricks is first-party and extremely common.
Module 2B.4 covered the platform; this topic covers the **Azure-specific
integration**.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Azure Databricks workspace deployment: control plane vs compute plane in your subscription; managed resource group |
| Basics | Accessing ADLS: **Unity Catalog** external locations and storage credentials backed by **managed identities** (replacing mounts and account keys) |
| Basics | Entra ID SSO and SCIM provisioning; workspace and account groups |
| Intermediate | VNet injection, secure cluster connectivity (no public IP), private endpoints |
| Intermediate | Secrets: Key Vault–backed secret scopes |
| Intermediate | Orchestration: ADF activities for notebooks/jobs, or Databricks Workflows called from ADF; Azure DevOps / GitHub Actions deployment (Databricks Asset Bundles) |
| Intermediate | Data movement patterns: ADF/Event Hubs → ADLS → Auto Loader → Delta (links to Module 2B.4) |
| Advanced | Integration with Fabric/OneLake and Power BI: reading Delta from OneLake, publishing to Power BI from Unity Catalog |
| Advanced | Cost: DBUs plus Azure VM cost, reservations, Spot VMs, cluster policies, and tagging for chargeback |
| Advanced | Monitoring with Azure Monitor and Log Analytics; system tables |
| Advanced | Databricks vs Fabric vs Synapse Spark decision framework |
| Advanced | Landing-zone and hub-and-spoke network patterns for regulated industries |

**How to learn it**

1. Read the topic file.
2. Compare how an S3-based Databricks workspace and an ADLS-based one
   authenticate to storage.
3. List the Azure services touching one Databricks pipeline.

**Hands-on exercise — `experiments/07_azure_databricks/`**

1. Deploy a workspace with Bicep/Terraform (Unity Catalog enabled).
2. Create a storage credential from a managed identity and an external
   location on ADLS.
3. Read bronze Parquet, write silver Delta, and register tables.
4. Trigger a Databricks job from an ADF pipeline with parameters.
5. Add a Key Vault–backed secret scope and use it in a notebook.
6. Estimate monthly cost for a given workload (DBUs + VMs).

**Checkpoint:**

- [ ] Connect Databricks to ADLS securely with managed identity.
- [ ] Trigger and schedule Databricks from ADF.
- [ ] Use Key Vault–backed secrets.
- [ ] Choose Databricks vs Fabric for a workload.

**Common mistakes:** account keys or mounts instead of Unity Catalog; one
workspace for dev/test/prod; ignoring VM costs outside DBUs.

---

## 10. Phase E — Security and Governance (Advanced)

### Topic 08 — [Entra ID, RBAC, and Key Vault](08-entra-id-rbac-and-key-vault.md)

**Why here:** identity is the Azure security perimeter. Most real-world
failures here are permission mistakes, not technology failures.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Microsoft Entra ID** (formerly Azure AD): users, groups, service principals, app registrations, managed identities |
| Basics | **Azure RBAC**: roles, scopes (management group → subscription → resource group → resource), role assignments, built-in vs custom roles |
| Basics | Control-plane vs data-plane roles (Contributor vs Storage Blob Data Contributor) |
| Intermediate | **Managed identities** (system- and user-assigned) for ADF, Databricks, Functions, and Synapse; eliminating passwords and keys |
| Intermediate | **Azure Key Vault**: secrets, keys, certificates; access policies vs RBAC; soft delete and purge protection |
| Intermediate | Reading Key Vault from Python (`azure-identity` + `azure-keyvault-secrets`) with `DefaultAzureCredential` |
| Intermediate | Conditional access and MFA for humans; groups for access, not individuals |
| Advanced | Least-privilege design for data teams; Privileged Identity Management (PIM) for just-in-time elevation |
| Advanced | Network security: private endpoints, firewalls, NSGs, service endpoints, and Private DNS zones |
| Advanced | Encryption: Microsoft-managed vs customer-managed keys, double encryption |
| Advanced | Azure Policy and Defender for Cloud: guardrails and posture management; infrastructure-as-code review |
| Advanced | Auditing: Activity Log, diagnostic settings to Log Analytics, and sign-in logs |

**How to learn it**

1. Read the topic file.
2. For an ADF pipeline reading ADLS and writing Synapse, list every
   identity and exactly which role/scope it needs.
3. Replace each secret with a managed identity where possible.

**Hands-on exercise — `experiments/08_identity_keyvault/`**

1. Create a user-assigned managed identity; grant data roles on ADLS only.
2. Store a database password in Key Vault; read it from Python using
   `DefaultAzureCredential` locally and in a deployed job.
3. Remove a role and read the exact error; fix it.
4. Create a private endpoint for storage and show public access blocked.
5. Write an Azure Policy that denies storage accounts with public network
   access.

**Checkpoint:**

- [ ] Explain control-plane vs data-plane permissions.
- [ ] Use managed identities and Key Vault correctly.
- [ ] Design least-privilege role assignments.
- [ ] Apply guardrails with Azure Policy.

**Common mistakes:** Owner/Contributor everywhere; assigning roles to
users instead of groups; secrets in pipeline JSON; forgetting Private DNS
for private endpoints.

---

### Topic 09 — [Purview: governance and lineage](09-purview-governance-and-lineage.md)

**Why it comes last:** governance is the final layer over everything built
above, extending Module 2.20 to the Azure ecosystem.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Microsoft Purview**: the Unified Catalog / Data Map, data estate scanning, and business glossary |
| Basics | Registering sources (ADLS, Azure SQL, Synapse, Fabric, Power BI, Databricks) and running scans |
| Basics | Automatic classification of sensitive data (built-in and custom classifiers) |
| Intermediate | Collections, roles (data curator, reader, source admin), and domains |
| Intermediate | **Lineage** from ADF, Synapse, Fabric, Databricks (Unity Catalog), and Power BI; OpenLineage integration |
| Intermediate | **Sensitivity labels** and information protection across Microsoft 365 and data stores |
| Intermediate | Business glossary, data products, and ownership (links to Module 2C.8) |
| Advanced | Data quality and data health in Purview; policies for access (self-service access requests) |
| Advanced | Compliance features: data lifecycle and retention, DSPM/insider-risk integrations — awareness |
| Advanced | Automating Purview via REST API / Atlas APIs and Terraform; custom lineage ingestion |
| Advanced | Comparing Purview with Unity Catalog, Dataplex, and Glue/Lake Formation; multi-cloud scanning |
| Advanced | Operating a catalogue: stewardship processes, coverage metrics, and keeping metadata fresh |

**How to learn it**

1. Read the topic file.
2. Draw lineage for your mini-project from source to Power BI report.
3. List which classifications your data would trigger and what policy
   follows.

**Hands-on exercise — `experiments/09_purview/`**

1. Register ADLS and Azure SQL; run scans; review classifications.
2. Add glossary terms and attach them to assets.
3. Run an ADF pipeline and verify lineage appears; add a gap and note what
   lineage misses.
4. Apply sensitivity labels to a Power BI dataset.
5. Export catalogue coverage statistics via API.

**Checkpoint:**

- [ ] Scan and classify data sources.
- [ ] Explain and use lineage across ADF, Databricks, and Power BI.
- [ ] Use a glossary and ownership model.
- [ ] Compare Purview to other catalogues.

**Common mistakes:** scanning once and never again; no owners for
assets; trusting automatic classification without review; ignoring
lineage gaps.

---

## 11. Module mini-project — an Azure medallion platform

**Goal:** build a secure, governed medallion platform on Azure using the
unified Fabric path and the classic Databricks path.

**Requirements**

1. **Ingest:** Data Factory copies from a SQL source and a REST API into
   ADLS bronze (metadata-driven, incremental). Event Hubs with Capture
   handles a streaming source.
2. **Transform:** Databricks (or Fabric notebooks) builds silver and gold
   Delta tables; one mapping data flow shows the visual alternative.
3. **Serve:** a Fabric lakehouse or warehouse with a Direct Lake semantic
   model and a Power BI report.
4. **Security:** all access through managed identities and Key Vault; no
   account keys; private endpoints for storage.
5. **Governance:** Purview scans, classifications, glossary, and lineage.
6. **Cost:** budgets, tags, auto-pause, and a cost review.
7. All infrastructure in Bicep/Terraform; CI/CD deploying to dev and test;
   README with an architecture diagram and identity map.

**Done when** the platform deploys from scratch, no secret appears in
code, lineage shows source to report, and a teammate can explain who can
access what and why.

---

## 12. Module self-assessment — exit criteria

You have completed this module when you can do all of the following
**without notes**:

- [ ] Map Azure data services and explain Fabric's relationship to the
      older ones.
- [ ] Design ADLS Gen2 storage with RBAC and ACLs.
- [ ] Build parameterised, incremental Data Factory pipelines.
- [ ] Choose and tune Synapse serverless vs dedicated pools.
- [ ] Ingest and process streams with Event Hubs and Stream Analytics.
- [ ] Build a medallion lakehouse in Fabric with Direct Lake.
- [ ] Integrate Azure Databricks securely with ADLS and ADF.
- [ ] Use Entra ID, managed identities, RBAC, and Key Vault correctly.
- [ ] Govern data with Purview.

---

## 13. Recommended reading and references

- Microsoft Learn: Azure Data Engineer (DP-203 retired — use current
  learning paths), Fabric Analytics Engineer (DP-600), Fabric Data
  Engineer (DP-700).
- Azure Architecture Center: modern data warehouse and lakehouse
  reference architectures.
- Official docs: ADLS Gen2, Data Factory, Synapse, Event Hubs, Fabric,
  Purview, Key Vault, Entra ID.
- Azure Databricks documentation and best practices.

---

## 14. Where this module leads

- **Module 2C.6** (dbt) runs on Fabric, Synapse, Databricks, Snowflake, and
  BigQuery.
- **Module 2C.8** covers platform architecture, build vs buy, and vendor
  selection across clouds.
- **Module 2C.10** continues into ML handoff (Fabric Data Science, Azure
  ML, MLflow).
