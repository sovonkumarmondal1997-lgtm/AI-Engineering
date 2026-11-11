# Azure Databricks Integration: Identity, Networking, Orchestration, and Operations

> **Scope:** Azure-specific integration and production operations. Databricks/Spark/Delta fundamentals are covered in Stage 2B, Module 2B.4; this lesson focuses on connecting those foundations to Azure services securely and operating them reliably.

## 1. Purpose, prerequisites, and outcomes

Azure Databricks is a managed analytics platform integrated with Azure identity, networking, storage, orchestration, governance, and monitoring. A production deployment is more than a workspace and notebook: it needs an identity model, controlled data paths, network routes, repeatable releases, observability, and a cost model that includes both Databricks usage and Azure infrastructure.

### Prerequisites

- Python, SQL, Spark DataFrames, Parquet, Delta Lake, and medallion architecture.
- Azure tenants, subscriptions, resource groups, Microsoft Entra ID, Azure RBAC, managed identities, VNets, private endpoints, and ADLS Gen2.
- Azure Data Factory (ADF) pipelines, activities, linked services, and parameters.
- Git, CI/CD, secret handling, and cloud cost management.

### Learning outcomes

You will be able to explain the control and compute planes; deploy a workspace with Unity Catalog; configure ADLS access through an Access Connector managed identity, storage credential, and external location; reason about Entra SSO/SCIM/groups and private networking; use Key Vault-backed scopes safely; transform bronze Parquet into silver Delta; orchestrate jobs from ADF; deploy with Databricks Asset Bundles; integrate with Fabric/Power BI; estimate full costs; and troubleshoot operational failures.

## 2. Architecture and workspace deployment

### Control plane vs compute plane

- **Control plane:** Azure Databricks-managed services for workspace UI/API, job orchestration, metadata/control operations, and other platform functions.
- **Compute plane:** resources that execute workloads. Classic compute runs in the customer subscription and commonly in a Databricks-managed resource group; with VNet injection, classic compute uses customer-provided subnets. Serverless compute is provisioned and operated by Databricks in a serverless compute plane and has different networking and security configuration.
- **Managed resource group:** Databricks creates and manages supporting resources for classic workspaces. Do not edit, delete, or repurpose these resources manually; use supported workspace lifecycle operations.
- **Workspace:** collaboration and execution boundary, but not automatically a complete data-security boundary. Unity Catalog privileges, workspace bindings, Azure Storage authorization, network rules, and account identity still matter.

```text
Microsoft Entra ID / SCIM groups
              |
              v
Azure Databricks account ---- Unity Catalog metastore
              |                     |
       dev / test / prod             +-- storage credential (managed identity)
       workspaces                    +-- external location (ADLS path)
              |                                  |
       Jobs / notebooks -------------------------+--> ADLS Gen2
              |
        ADF / Workflows / CI-CD / Azure Monitor
```

This is a logical diagram. Not every feature uses the same identity or network path.

### Deployment decisions

Before deploying, record the region, workspace plan, Unity Catalog metastore, classic vs serverless compute, network topology, outbound requirements, diagnostics, naming, tags, and budget. Co-locate the workspace, metastore, Access Connector, and storage region where practical. Account-level metastore setup may require a Databricks account admin.

Illustrative CLI shape for a basic workspace only (not a production network deployment):

```bash
az group create --name rg-dbx-dev --location eastus
az databricks workspace create \
  --resource-group rg-dbx-dev \
  --name adb-example-dev \
  --location eastus \
  --sku premium \
  --managed-resource-group rg-dbx-dev-managed
```

The managed resource group is a Databricks-managed lifecycle boundary; do not place unrelated resources in it or edit its resources manually. This command does **not** configure VNet injection, private endpoints, diagnostics, outbound connectivity, Unity Catalog metastore attachment, or ADLS authorization. The companion lab now includes a small Bicep starter for the workspace and Access Connector, but intentionally leaves feature-specific networking to an approved landing-zone module.

## 3. Unity Catalog access to ADLS with managed identity

### Identity chain

Use Unity Catalog (UC) external locations rather than embedding storage keys or defaulting to legacy DBFS mounts:

1. Create an **Azure Databricks Access Connector** with a system-assigned or user-assigned managed identity.
2. Grant that identity the minimum Azure Storage data-plane role at the narrowest practical scope. `Storage Blob Data Contributor` is common for a read/write lab; use narrower read-only access for read-only paths where possible.
3. In UC, create a **storage credential** referencing the Access Connector resource ID.
4. Create an **external location** binding an `abfss://` path to that credential.
5. Grant UC privileges (`READ FILES`, `WRITE FILES`, `CREATE EXTERNAL TABLE`, etc.) only as needed.
6. Register external tables or access governed files under approved paths.

Azure RBAC and UC are separate authorization layers. The managed identity must be allowed to access the storage account; the human or workload principal must also have UC privileges. A grant in only one layer is insufficient. Storage firewall and DNS/routing must permit the request as well.

### SQL setup examples

Run in a UC-enabled workspace as a principal with the required metastore privileges. Replace placeholders; do not paste credentials.

```sql
CREATE STORAGE CREDENTIAL IF NOT EXISTS adls_bronze_credential
WITH AZURE_MANAGED_IDENTITY (
  ACCESS_CONNECTOR_ID = '/subscriptions/<subscription-id>/resourceGroups/<rg>/providers/Microsoft.Databricks/accessConnectors/<connector-name>'
)
COMMENT 'Managed identity for governed ADLS access';
```

```sql
CREATE EXTERNAL LOCATION IF NOT EXISTS bronze_landing
URL 'abfss://bronze@<storage-account>.dfs.core.windows.net/'
WITH (STORAGE CREDENTIAL adls_bronze_credential)
COMMENT 'Approved bronze landing area';

CREATE EXTERNAL LOCATION IF NOT EXISTS silver_landing
URL 'abfss://silver@<storage-account>.dfs.core.windows.net/'
WITH (STORAGE CREDENTIAL adls_bronze_credential)
COMMENT 'Approved silver Delta output area';
```

These show the object relationship; verify syntax against the current SQL reference and your runtime before production use. Create separate, appropriately scoped locations for bronze and silver. Grant `READ FILES` on bronze and `WRITE FILES` on silver only to the required workload principal/group; grant `CREATE EXTERNAL TABLE` only to the principal that registers the table. Do not grant routine engineers broad metastore administration privileges.

Example grants, to be adapted to your role model:

```sql
GRANT READ FILES ON EXTERNAL LOCATION bronze_landing TO `data_engineers`;
GRANT WRITE FILES ON EXTERNAL LOCATION silver_landing TO `databricks_job_runners`;
GRANT CREATE EXTERNAL TABLE ON EXTERNAL LOCATION silver_landing TO `table_publishers`;
-- Use account-level groups that exist in your metastore; scope grants narrowly.
```

### Bronze Parquet to silver Delta

This is a Databricks notebook example, not a standalone Python script. Assume the bronze and silver external locations already exist and the job principal has the required privileges. The example uses `run_date` as an ISO date parameter and processes events whose `event_ts` falls on that date. Adapt the source contract if files are already date-partitioned or `run_date` means ingestion date instead.

```python
from pyspark.sql import functions as F
from delta.tables import DeltaTable
from datetime import date

bronze_path = "abfss://bronze@<storage-account>.dfs.core.windows.net/events/"
silver_path = "abfss://silver@<storage-account>.dfs.core.windows.net/events/"
run_date = "2026-01-31"  # In the job, receive this from a validated parameter/widget.
# Validate calendar date, not just a non-empty string.
if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", run_date):
    raise ValueError("run_date must use YYYY-MM-DD format")
try:
    date.fromisoformat(run_date)
except ValueError as exc:
    raise ValueError("run_date must be a real calendar date") from exc

raw = spark.read.parquet(bronze_path)
required = {"event_id", "device_id", "event_ts", "reading"}
missing = required - set(raw.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

silver = (raw
    .withColumn("event_ts", F.to_timestamp("event_ts"))
    .withColumn("reading", F.col("reading").cast("double"))
    .withColumn("event_date", F.to_date("event_ts"))
    .filter(F.col("event_id").isNotNull() & F.col("device_id").isNotNull())
    .filter(F.col("event_ts").isNotNull() & F.col("reading").isNotNull())
    .filter(F.col("event_date") == F.lit(run_date).cast("date"))
    .withColumn("ingested_at", F.current_timestamp()))

# Reject duplicate business keys in the incoming batch rather than selecting
# an arbitrary record. Define a deterministic conflict policy upstream if needed.
if silver.groupBy("event_id").count().filter(F.col("count") > 1).limit(1).count():
    raise ValueError("Source batch contains duplicate event_id values; resolve upstream")

if DeltaTable.isDeltaTable(spark, silver_path):
    (DeltaTable.forPath(spark, silver_path).alias("t")
        .merge(silver.alias("s"), "t.event_id = s.event_id")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute())
else:
    # errorifexists avoids silently overwriting a non-Delta or unexpected path.
    silver.write.format("delta").mode("errorifexists").save(silver_path)
```

**Idempotency contract:** this example filters to `run_date`, rejects duplicate `event_id` values within a batch, and uses Delta `MERGE` keyed by `event_id` for cross-run reprocessing. The source owner must define whether a matching key represents an update or an immutable event; concurrent writers to the same target must be controlled. An empty batch should be handled as an explicit business case, not silently reported as a successful load.

Register the Delta directory after the first successful write and after the path is covered by `silver_landing`. Before relying on `CREATE TABLE IF NOT EXISTS`, inspect any existing table's location and schema; the clause does not repair a table already registered to the wrong path:

```sql
CREATE SCHEMA IF NOT EXISTS main.silver;
CREATE TABLE IF NOT EXISTS main.silver.device_events
USING DELTA
LOCATION 'abfss://silver@<storage-account>.dfs.core.windows.net/events/';
```

The registering principal needs the applicable catalog/schema privileges and `CREATE EXTERNAL TABLE` on the external location. The job writer needs `WRITE FILES` on the silver external location. For a managed table, omit `LOCATION` and use a configured Unity Catalog managed storage location.

### Auto Loader: files, not a direct Event Hubs consumer

```text
ADF / Event Hubs / producers -> ADLS bronze files
                                    |
                                    v
                           Auto Loader (cloudFiles)
                                    |
                                    v
                              Delta silver
```

Auto Loader incrementally discovers cloud files. For direct Event Hubs ingestion, use a supported Event Hubs/Kafka connector and design offset/checkpoint semantics explicitly; do not assume Auto Loader consumes Event Hubs directly.

Illustrative streaming notebook for JSON files:

```python
source = "abfss://bronze@<storage-account>.dfs.core.windows.net/iot-json/"
schema_path = "abfss://checkpoints@<storage-account>.dfs.core.windows.net/autoloader/schema/device_events/"
checkpoint_path = "abfss://checkpoints@<storage-account>.dfs.core.windows.net/autoloader/checkpoints/device_events/"

stream = (spark.readStream.format("cloudFiles")
          .option("cloudFiles.format", "json")
          .option("cloudFiles.schemaLocation", schema_path)
          .load(source))

(stream.writeStream.format("delta")
 .option("checkpointLocation", checkpoint_path)
 .outputMode("append")
 .toTable("main.silver.device_events_stream"))
```

Keep schema and checkpoint locations durable and access-controlled. Give each independent query its own checkpoint. Configure file events and permissions according to the chosen Auto Loader mode and current recommendations.

## 4. Entra ID SSO, SCIM, groups, and isolation

- **SSO** delegates interactive authentication to Microsoft Entra ID. Authentication is not authorization.
- **SCIM provisioning** synchronizes users and groups from the identity provider. Prefer account-level groups and identity federation where supported, rather than manually maintaining user/group copies in every workspace.
- **Account groups** are centrally managed and assigned to workspaces. Follow current account/workspace identity-federation guidance; workspace-local groups may not behave like centrally provisioned groups in every configuration.
- **Workload identities** (service principals or supported managed/federated identities) are for automation. Avoid using a human user's personal access token as a long-lived production credential.
- **Separate dev/test/prod workspaces** when blast radius, compliance, network boundary, release controls, or data sensitivity justify it. Use separate catalogs/schemas, storage paths, identities, and deployment targets. Workspace separation alone does not enforce data access.
- Apply least privilege across Azure RBAC, UC, workspace entitlements, job permissions, secret-scope ACLs, and Power BI permissions.

## 5. Networking: VNet injection, SCC, Private Link, hub-and-spoke

Answer these before deployment:

1. Is the workspace using classic compute or serverless? Controls differ.
2. Do users need private access to the workspace UI/API?
3. Does compute need private access to ADLS, Key Vault, Event Hubs, SQL, or on-premises systems?
4. How does compute reach the Databricks control plane?
5. What outbound access is required for package repositories, identity, monitoring, and other dependencies?
6. Which DNS zones, routes, NSGs, and private endpoint approvals are required?
7. How is egress inspected and logged?

- **VNet injection** places classic compute in customer-provided subnets and supports custom routes, NSGs, and private connectivity.
- **Secure Cluster Connectivity (SCC)** removes the need for inbound ports to cluster nodes. It does not by itself make every service private or eliminate outbound network requirements.
- **Private Link** has distinct front-end (user/API) and back-end (compute-to-control-plane) patterns. Serverless data access can require separate network connectivity configuration. “Private Link enabled” is not a complete network design.
- **No public IP on cluster nodes** does not mean no public egress. Explicitly design outbound connectivity.
- **Hub-and-spoke:** shared firewall, DNS, VPN/ExpressRoute, egress controls, and approved endpoints can live in the hub; workload VNets live in spokes. Validate routes, latency, DNS, throughput, and supported services before forcing all traffic through a hub.
- IAM success does not prove network access. Diagnose DNS, route tables, NSGs, firewall logs, endpoint approval, and service-specific network access together. For storage protected by network rules, follow the current Azure Databricks trusted-access guidance for managed identities and the chosen VNet-injected/serverless compute mode; a managed identity alone does not bypass storage firewall rules.

> **Current-deployment caution:** Networking defaults and Databricks requirements evolve. Verify current outbound-connectivity requirements (including NAT/firewall design for new VNet-injected workspaces), subnet sizing, NSG rules, private endpoint types, and regional feature availability in official docs. This lesson intentionally avoids a universal NSG rule list because requirements depend on feature set and architecture.

## 6. Key Vault-backed secret scopes

A Key Vault-backed secret scope exposes secrets from Azure Key Vault through Databricks. It is a secret-retrieval mechanism, not a replacement for Azure RBAC or UC authorization.

- The documented Azure Databricks Key Vault-backed scope integration requires the **Key Vault access-policy permission model**; the Azure RBAC permission model is not supported by this particular integration. Confirm current docs before choosing the vault design.
- Scope access is broad: users who can read secrets through a Key Vault-backed scope may be able to access secrets in that vault. Use separate vaults for distinct trust domains where necessary.
- Key Vault firewall/network rules must permit the documented integration. Do not weaken a production vault's network controls merely to complete a lab.
- Redaction of secret values in notebook output is best-effort, not a security boundary. Never print secrets, interpolate them into SQL/log messages, or include them in exception text.
- Prefer managed identity or workload identity when the target service supports it; use secrets only when required.

```python
# The scope and key must already exist. Never print/log the returned value.
api_token = dbutils.secrets.get(scope="kv-app-scope", key="vendor-api-token")
# Use api_token only in the client configuration that needs it.
```

Create the scope through the supported UI/CLI/API, grant minimum scope permissions, and manage the secret value in Key Vault rather than notebooks or Git.

## 7. Orchestration: ADF vs Databricks Workflows

Use **ADF** when the workflow spans Azure services: copy data, wait for dependencies, invoke a Databricks job, and route success/failure notifications. Use **Databricks Workflows/Jobs** for Databricks-native task dependencies, notebooks, Python wheel tasks, job compute, retries, task values, and Databricks-native scheduling. A common pattern is ADF as the outer orchestrator and a Databricks Job as the internal multi-task graph. Avoid two schedulers owning the same dependency graph.

### Parameterized job contract

ADF can execute a notebook through its native Azure Databricks Notebook activity, or invoke an existing multi-task Databricks Job using a supported authenticated REST/Web activity and the Jobs `run-now` API. These are different execution patterns. For a job invocation, use `experiments/07_azure_databricks/adf/run-now-payload.json` as an illustrative request body. Configure an authentication method supported by the selected ADF activity and Databricks workspace (for example, a governed Databricks service principal/OAuth flow where supported). Do not assume an ADF managed identity is automatically accepted by every Databricks endpoint. Connector and authentication support is version-sensitive; verify current ADF and Databricks documentation.

Illustrative parameter contract (not a complete ADF pipeline or Jobs API request):

```json
{
  "source_path": "abfss://bronze@<storage-account>.dfs.core.windows.net/events/",
  "target_path": "abfss://silver@<storage-account>.dfs.core.windows.net/events/",
  "target_table": "main.silver.device_events",
  "run_date": "2026-01-31"
}
```

Notebook widget validation:

```python
import re
from datetime import date

dbutils.widgets.text("source_path", "")
dbutils.widgets.text("target_path", "")
dbutils.widgets.text("target_table", "main.silver.device_events")
dbutils.widgets.text("run_date", "")

source_path = dbutils.widgets.get("source_path")
target_path = dbutils.widgets.get("target_path")
target_table = dbutils.widgets.get("target_table")
run_date = dbutils.widgets.get("run_date")

allowed_storage_account = "<replace-with-lab-storage-account>"
source_pattern = rf"^abfss://bronze@{re.escape(allowed_storage_account)}\.dfs\.core\.windows\.net/[A-Za-z0-9_./=-]*$"
target_pattern = rf"^abfss://silver@{re.escape(allowed_storage_account)}\.dfs\.core\.windows\.net/[A-Za-z0-9_./=-]*$"
if not re.fullmatch(source_pattern, source_path) or ".." in source_path.split("/"):
    raise ValueError("Source path is not within the approved ADLS bronze prefix")
if not re.fullmatch(target_pattern, target_path) or ".." in target_path.split("/"):
    raise ValueError("Target path is not within the approved ADLS silver prefix")
if not re.fullmatch(r"main\.silver\.[A-Za-z_][A-Za-z0-9_]*", target_table):
    raise ValueError("target_table must be an allow-listed identifier in main.silver")
if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", run_date):
    raise ValueError("run_date must use YYYY-MM-DD format")
try:
    date.fromisoformat(run_date)
except ValueError as exc:
    raise ValueError("run_date must be a real calendar date") from exc
```

Treat parameters as untrusted input. Allow-list paths and identifiers; validate `run_date` as a real ISO date; never concatenate arbitrary input into SQL. Use parameter binding where supported. Record job run IDs and audit counts. If ADF times out after a Delta commit, inspect the job and target state before retrying; retries do not provide exactly-once behavior by themselves.

## 8. CI/CD with Databricks Asset Bundles

Databricks Asset Bundles (also called Declarative Automation Bundles in current docs) define jobs and related resources as code. Keep environment-specific values in target configuration and secrets in a secret manager.

Minimal illustrative `databricks.yml`:

```yaml
bundle:
  name: azure-medallion-pipeline

variables:
  catalog:
    description: Unity Catalog target catalog

targets:
  dev:
    default: true
    mode: development
    workspace:
      host: https://<dev-workspace-url>
    variables:
      catalog: dev_catalog
  prod:
    mode: production
    workspace:
      host: https://<prod-workspace-url>
    variables:
      catalog: prod_catalog
```

Validate the bundle schema against the installed CLI and official resource reference before deployment. Common commands:

```bash
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run -t dev <resource-key>
```

Production release sequence:

1. Run formatting, unit tests, data-contract tests, and security checks.
2. Validate and deploy to an isolated dev workspace.
3. Run smoke tests on non-production data.
4. Require approval before production deployment.
5. Deploy versioned code; record the Git commit SHA with job runs.
6. Use separate service identities, catalogs, storage paths, and secrets by environment.
7. Prefer federated workload identity/OIDC for CI/CD where supported; do not share a developer's personal token.

## 9. Fabric/OneLake and Power BI integration

Databricks and Fabric do not become a single security or compute plane just because they can access related data. Choose the data-access direction, governance owner, and semantic-model owner explicitly.

- **Read OneLake from Databricks:** use a currently supported OneLake/ADLS-compatible endpoint and Entra ID authentication for the selected workload, with appropriate Fabric/OneLake permissions. Do not assume every `abfss://` URI or identity mode works in every compute configuration.
- **Expose curated data to Power BI:** use a supported Databricks SQL/Power BI connector and authentication mode, or publish data to a Fabric item using a supported integration. Confirm whether the target design is Import, DirectQuery, or Direct Lake; they are not interchangeable.
- **Power BI with Unity Catalog:** grant the required UC permissions and separately design Power BI semantic-model/workspace permissions. UC grants do not automatically transfer to Fabric or Power BI.
- **Copy vs shared access:** copying gives an independent snapshot but adds storage and refresh work; shared access avoids some copies but couples permissions, schema evolution, availability, and workload performance.
- Verify current product support, tenant settings, licensing, private networking, and identity propagation before choosing a cross-platform pattern.

## 10. Cost: DBUs plus Azure VM charges

Databricks usage charges and Azure infrastructure charges are distinct. A useful estimate is:

\[
\text{Monthly cost} \approx (\text{DBU rate} \times \text{DBU-hours}) + \text{VM-hours} + \text{storage} + \text{network/egress} + \text{supporting Azure services}
\]

This is a model, not a quote. Use current regional prices, your contract, and the selected compute type. Azure's Databricks pricing pages/calculators may show DBU-only rates or combined totals for particular SKUs; identify which pricing basis you are using and **never add VM cost twice** when the displayed total already includes it. Validate discounts, reservations/savings plans, Spot eligibility, and VM/DBU billing treatment against the current offer and contract.

For each job/cluster, record runs/month, average runtime, driver/worker count and VM types, DBU consumption rate, VM hourly prices, storage, ADLS transactions, egress, NAT/firewall, private endpoints, Log Analytics ingestion, and retry overhead.

| Input | Illustrative assumption | Calculation |
|---|---:|---|
| Runs/month | 120 | Workload requirement |
| Average runtime | 0.5 hours | Measured/estimated |
| Runtime hours | 60 | 120 × 0.5 |
| DBUs/hour | 8 | Selected compute usage rate; replace |
| DBU-hours | 480 | 60 × 8 |
| DBU price per DBU | `$R_d` | Current contract/region price per DBU |
| DBU cost | `480 × $R_d` | DBU-hours × price per DBU |
| VM cost | `60 × (driver VM rate + worker count × worker VM rate)` | Actual VM types and counts |
| Other costs | separately estimated | Storage, egress, monitoring, endpoints, etc. |

Do not assume DBUs include Azure VM charges. Spot VMs can reduce costs but can be evicted; use only where retries/checkpoints and SLOs tolerate interruption. Reservations/savings plans depend on eligibility and terms. Cluster policies should limit node types, autoscaling, idle time, tags, and risky configurations.

Use consistent tags such as `env`, `cost_center`, `owner`, `application`, `data_product`, and `managed_by`. Verify which tags flow to each billing source. Reconcile Azure Cost Management, Databricks usage/system tables, and billing exports rather than assuming one report includes all charges.

## 11. Monitoring and troubleshooting

Monitor job/task duration, retries, failures, queue/start time, autoscaling, input/output counts, duplicate rate, null rate, schema drift, freshness, Spark stage/task skew, shuffle spill, executor failures, storage throttling, and network denials.

Use Azure Activity Log, configured Azure Monitor/Log Analytics diagnostic settings, Spark UI, job run history, and Databricks system tables where available. System-table availability and columns vary by account/region/release and permissions; they may not be automatically enabled.

Example query shape, if the billing usage system table is enabled and accessible:

```sql
SELECT *
FROM system.billing.usage
WHERE usage_date >= current_date() - INTERVAL 7 DAYS
LIMIT 100;
```

Do not treat this as a complete financial report. Join usage to the correct price data and account/workspace metadata before calculating costs.

| Symptom | First checks |
|---|---|
| `403` on ADLS | Access Connector identity, Azure RBAC scope, UC grants, ACLs, external location, firewall/network |
| External location creation fails | Metastore privilege, credential resource ID, ADLS path, workspace binding, firewall |
| Dev works, prod fails | Different identity, catalog grants, secret scope, DNS, endpoint approval, linked service |
| Duplicate rows after retry | Non-idempotent append, partial commit, unstable business key, incorrect checkpoint use |
| Slow Spark job | Skew, small files, shuffle, partitions, inefficient joins, cold start, storage throttling |
| Cluster cannot start/connect | Quotas, subnet IPs, NSGs, DNS, routes, outbound/NAT/firewall, Private Link configuration |
| ADF timeout after write | Check Databricks run ID and audit/commit state before retrying |
| Cost overrun | VM cost omitted, idle clusters, excess DBUs, retries, egress/NAT, log ingestion |

## 12. Landing zones and regulated environments

A robust landing zone defines subscriptions/resource groups, hub-and-spoke networking, private DNS, firewall/egress controls, private endpoints, VPN/ExpressRoute, Entra groups, privileged identity management, workload identities, UC ownership and external-location boundaries, secret access, diagnostic settings, retention, budgets, tags, data residency, encryption/key ownership, and incident-response evidence.

Separate dev/test/prod workspaces and data paths when needed for compliance, blast-radius control, or release management. Network isolation increases cost and operational complexity. Test control-plane, compute-plane, storage, package, monitoring, and identity paths before enabling deny-by-default egress.

## 13. Databricks vs Fabric vs Synapse Spark

| Factor | Azure Databricks | Microsoft Fabric | Synapse Spark |
|---|---|---|---|
| Strong fit | Lakehouse engineering, advanced Spark/Delta, ML/AI and engineering workflows | Integrated SaaS analytics across OneLake, pipelines, Warehouse, real-time, and Power BI | Existing Synapse estates or dependencies that justify Synapse integration |
| Governance | Unity Catalog and account/workspace controls | Fabric workspace/item/OneLake/semantic-model controls | Synapse workspace and Azure data/security controls |
| Storage | Commonly ADLS Gen2 with governed external locations | OneLake and Fabric-managed items; supported shortcuts/connectors | Commonly ADLS Gen2 |
| Orchestration | Databricks Workflows; external orchestrators such as ADF | Fabric Data Factory pipelines | Synapse pipelines and notebooks |
| Cost lens | DBUs + Azure VM + storage/network/supporting services | Capacity/F SKU consumption plus related storage/network/service costs | Check current Spark pool and Azure resource pricing |
| Portability | Spark/Delta portable in part; UC, jobs and platform features are specific | Delta/Parquet can interoperate; Fabric items, semantic models, shortcuts and capacity integration create coupling | Spark/Delta concepts portable; Synapse-specific integration is not |

Decide using workload performance, skills, governance, connectivity, migration effort, pricing, operational maturity, and exit strategy—not product positioning alone. The roadmap requires learning Databricks even when Fabric is a strategic alternative.

## 14. Hands-on lab — `experiments/07_azure_databricks/`

The companion folder contains a deployment checklist, notebook starter, Unity Catalog SQL, ADF parameter contract, and cost worksheet.

### Prerequisites and permissions

- Azure subscription and permissions to create resources; Contributor/Owner on the chosen resource group as required.
- Owner or User Access Administrator on the storage scope to create role assignments.
- Unity Catalog-enabled workspace attached to a metastore; privileges to create storage credentials/external locations and schemas/tables.
- ADLS Gen2 account with HNS and bronze/silver/checkpoint paths.
- ADF instance and workload identity/service principal authorized to invoke the intended Databricks job.
- Key Vault configured with a permission model supported by Key Vault-backed scopes, plus required networking/access policy.
- For private networking: approved VNet/subnets, DNS, routes/NSGs/firewall, private endpoints as applicable, and explicit outbound connectivity.
- Current Azure CLI/Bicep or Terraform, Databricks CLI, Git, and Python. Availability and cost vary by region, plan, and tenant.

### Procedure

1. Review `experiments/07_azure_databricks/infra/deployment-checklist.md`; deploy only after reviewing network egress, private connectivity, and cost.
2. Create ADLS bronze/silver/checkpoint paths and upload sample `events` Parquet with columns `event_id`, `device_id`, `event_ts`, and `reading`.
3. Create an Access Connector; assign least-privilege data access to its managed identity.
4. Adapt and run `sql/unity_catalog_setup.sql` in the UC-enabled workspace.
5. Run `notebooks/bronze_to_silver.py` as a Databricks notebook after configuring widgets and catalog/path names.
6. Validate row counts, null constraints, duplicate keys, and the Delta transaction log. Make reruns idempotent before production use.
7. Create a parameterized Databricks Job and call it from ADF using `adf/job-parameters.json` as the parameter contract and `adf/run-now-payload.json` as an illustrative Jobs API body. Configure the actual supported activity and authentication in the ADF UI or Git mode.
8. Create a Key Vault-backed scope using current official UI/CLI guidance; restrict scope permissions and test with a non-production secret. Never print the secret.
9. Complete `cost/monthly-cost-estimate.csv` with current regional DBU and VM prices.
10. Inspect job history, Spark UI, Activity Log/diagnostics, and available system tables. Test an unauthorized path and a controlled failure/retry.
11. Clean up workspace and lab resources through supported Azure resource operations; remove role assignments and test secrets as appropriate. Confirm no billable compute remains running.

### Validation criteria

- The storage identity can access only intended paths; an unauthorized path fails.
- Reruns do not duplicate records for the same stable key.
- ADF passes parameters without embedding credentials.
- Job failure/retry is observable and committed data is reconciled before replay.
- Secrets do not appear in logs, notebook output, or source control.
- Cost estimate includes DBUs and Azure VM charges and documents excluded costs.

**Not claimed:** No workspace, Access Connector, UC object, ADF pipeline, Key Vault scope, or production network has been deployed from this lesson. The SQL, notebook, CLI, and YAML examples are educational templates that must be checked against the chosen runtime, CLI version, plan, and tenant. No live execution or benchmark is claimed.

## 15. Practice exercises and answer key

### Exercises

1. A notebook reads ADLS in dev but gets `403` in prod. List checks in order.
2. Why does Azure RBAC alone not grant a Databricks user access through Unity Catalog?
3. ADF times out after a Databricks job commits Delta output. How do you recover?
4. Security requires private connectivity and no public cluster IPs. What must be decided beyond SCC?
5. A nightly job runs for 20 minutes but an interactive cluster idles for two hours. Which controls help?
6. Compare an account key, service-principal secret, and Access Connector managed identity.
7. Choose ADF or Databricks Workflows for a workflow containing ADF Copy, a multi-task Databricks job, and notification.

### Suggested answers

1. Compare prod Access Connector/identity, Azure RBAC scope, external location URL/credential, UC grants, storage ACLs, workspace binding, firewall/private endpoint, DNS and routes.
2. Azure RBAC authorizes the managed identity against Azure Storage; UC separately authorizes the user/group against the credential, external location, catalog/schema/table, or file privileges.
3. Inspect Databricks run ID and durable audit/commit record. Check if the batch committed, then rerun with idempotent `MERGE` or deterministic partition replacement; do not blindly append.
4. Decide front-end/back-end Private Link, VNet injection for classic compute, SCC, private endpoints for dependencies, DNS, NSGs/routes/firewall, outbound/NAT, serverless network connectivity if used, and user access path.
5. Use job compute or appropriate serverless job compute, auto-termination, cluster policies, right-sized nodes, autoscaling, avoid idle interactive clusters, tag workloads, and include VM plus DBU costs.
6. Account keys are broad shared credentials; service principals require secret/certificate lifecycle; managed identity avoids secret rotation and supports Azure-native authorization. UC grants still apply.
7. Let ADF own cross-service dependencies and call a Databricks Job for the internal task graph, or let Workflows own an all-Databricks graph. Avoid competing schedulers.

## 16. Common mistakes to avoid

- Using account keys or broad service-principal secrets when an Access Connector managed identity and Unity Catalog can govern ADLS access.
- Treating Azure RBAC as a substitute for Unity Catalog grants, or vice versa.
- Assuming a private endpoint or SCC alone creates a fully private deployment; missing DNS, outbound routes, firewall rules, or serverless network configuration can still break connectivity.
- Sharing one workspace, catalog, storage path, and credential across dev/test/prod without a deliberate isolation model.
- Treating Key Vault-backed scopes as a replacement for authorization, overlooking the scope's broad access implications, or printing a secret while debugging.
- Calling ADF activity retries “exactly once”; a timed-out caller may not know whether the job committed output.
- Using `append` plus `dropDuplicates` as cross-run deduplication, or sharing a streaming checkpoint across independent queries.
- Assuming Auto Loader directly consumes Event Hubs rather than discovering files in cloud storage.
- Underestimating cost by counting DBUs but omitting Azure VM, storage, network egress, NAT/firewall, and log-ingestion charges.
- Using a personal token for long-lived production automation, or putting secrets and environment-specific identifiers in Git.

### S3-based vs ADLS-based workspace authentication

The conceptual problem is the same—grant a platform-managed identity controlled access to cloud storage—but the identity and policy mechanisms are cloud-specific. On Azure, an Access Connector's managed identity can be referenced by a Unity Catalog storage credential and authorized with Azure RBAC/ADLS ACLs. On AWS, Unity Catalog commonly uses an AWS IAM role and the appropriate trust relationship/policies for S3. Do not copy an IAM role, trust policy, or S3 URI into Azure configuration; translate the identity chain and storage policy to Azure-native primitives.

## 17. Checkpoint

- [ ] Explain control plane, compute plane, and managed resource group.
- [ ] Configure a managed-identity-backed UC storage credential and ADLS external location.
- [ ] Explain Entra SSO, SCIM, account groups, and workspace isolation.
- [ ] Describe VNet injection, SCC, Private Link, DNS, and outbound requirements.
- [ ] Use Key Vault-backed secret scopes without treating them as authorization.
- [ ] Trigger and schedule Databricks from ADF with validated parameters.
- [ ] Explain Asset Bundles CI/CD and environment-specific deployment.
- [ ] Estimate DBUs and VM charges separately and inspect usage.
- [ ] Choose Databricks, Fabric, or Synapse Spark for a concrete workload.

## 18. Official references

Check current documentation before deploying; product names, feature availability, and network defaults evolve.

- [Azure Databricks documentation](https://learn.microsoft.com/azure/databricks/)
- [ADLS Gen2 external locations](https://learn.microsoft.com/azure/databricks/connect/unity-catalog/external-locations)
- [Azure managed identities in Unity Catalog](https://learn.microsoft.com/azure/databricks/connect/unity-catalog/cloud-storage/azure-managed-identities)
- [Unity Catalog storage credentials](https://learn.microsoft.com/azure/databricks/connect/unity-catalog/cloud-storage/storage-credentials)
- [VNet injection](https://learn.microsoft.com/azure/databricks/security/network/classic/vnet-inject)
- [Secure Cluster Connectivity](https://learn.microsoft.com/azure/databricks/security/network/classic/secure-cluster-connectivity)
- [Private Link concepts](https://learn.microsoft.com/azure/databricks/security/network/concepts/private-link)
- [Secret management and Key Vault-backed scopes](https://learn.microsoft.com/azure/databricks/security/secrets/)
- [Databricks Asset Bundles](https://learn.microsoft.com/azure/databricks/dev-tools/bundles/)
- [ADF Databricks notebook activity](https://learn.microsoft.com/azure/data-factory/transform-data-databricks-notebook)
- [Databricks Jobs API parameterization](https://learn.microsoft.com/azure/databricks/jobs/parameters)
- [ADLS Gen2 external locations — prerequisites and SQL](https://learn.microsoft.com/azure/databricks/connect/unity-catalog/cloud-storage/storage-credentials)
- [Azure Databricks system tables](https://learn.microsoft.com/azure/databricks/admin/system-tables/)
- [Azure pricing calculator](https://azure.microsoft.com/pricing/calculator/)
- [Azure Databricks pricing](https://azure.microsoft.com/pricing/details/databricks/)
- [Monitor costs using Databricks system tables](https://learn.microsoft.com/azure/databricks/admin/usage/system-tables)
- [Deploy a workspace with the Azure CLI](https://learn.microsoft.com/azure/databricks/admin/workspace/azure-cli)
- [Azure Databricks workspace ARM/Bicep reference](https://learn.microsoft.com/azure/templates/microsoft.databricks/workspaces)
- [Azure Databricks Access Connector ARM/Bicep reference](https://learn.microsoft.com/azure/templates/microsoft.databricks/accessconnectors)
- [Configure identity federation and account-level identity](https://learn.microsoft.com/azure/databricks/admin/account-settings-e2/identity-federation)
- [Provision users and groups with SCIM](https://learn.microsoft.com/azure/databricks/admin/users-groups/scim/)
- [Azure Databricks networking overview](https://learn.microsoft.com/azure/databricks/security/network/)
- [Azure managed identity trusted access for storage](https://learn.microsoft.com/azure/databricks/connect/unity-catalog/cloud-storage/azure-managed-identities)
- [Databricks Jobs API — run now](https://learn.microsoft.com/azure/databricks/dev-tools/api/latest/jobs)
