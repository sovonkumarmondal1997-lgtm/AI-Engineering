# Databricks Architecture, Workspaces and Planes

> **Topic 01 — Phase A: Platform Foundations**

## 1. What You Will Learn

This Topic 01 establishes the architectural foundation for the Databricks Lakehouse Platform Deep Dive. You will learn the Databricks account and workspace model; AWS/Azure/GCP cloud context; control plane, classic compute plane, and serverless compute plane; cloud object storage; Unity Catalog's governance relationship; users, groups, service principals; workspace objects and permissions; networking and security boundaries; development/staging/production separation; single versus multiple workspace strategies; Terraform and infrastructure as code; Databricks versus cloud-provider responsibilities; Databricks versus open-source technologies; production troubleshooting; architecture trade-offs; and senior-level reasoning.

By the end, you should be able to explain: what Databricks is, where it runs, what an account is, what a workspace is, where computation happens, where persistent data lives, how identities and permissions work, how networking affects workloads, how enterprises structure workspaces, and which responsibilities belong to Databricks versus the underlying cloud.

## 2. Why This Topic Matters

A Data Engineer who only knows notebooks and Spark is not yet proficient in the Databricks platform. Production engineering also requires security, governance, cost control, networking, reliability, environment separation, CI/CD, Unity Catalog, jobs, pipelines, and enterprise architecture.

The central principle is:

> Databricks proficiency is broader than Spark proficiency.

Architecture decisions determine blast radius, access control, deployment safety, cost, network reachability, and operational ownership.

## 3. Databricks Mental Model

```text
Databricks Account
        |
        +----------------------+
        |                      |
   Workspaces              Identity
        |                 Users / Groups
        |              Service Principals
        |
   Workspace Objects
        |
  Notebooks / Jobs / SQL /
  Pipelines / Git folders
        |
      Compute
        |
  Classic / Serverless
        |
       Data
        |
  Cloud Object Storage
        |
  S3 / ADLS / GCS
        |
    Governance
        |
   Unity Catalog
```

**Account** is the organization/platform boundary. **Workspace** is a working environment. **Identity** determines who or what is acting. **Workspace objects** are development and operational assets. **Compute** executes workloads. **Cloud storage** commonly holds persistent data. **Unity Catalog** provides the governance/data-access layer.

Do not treat the diagram as saying every internal Databricks service is physically implemented in exactly these boxes; it is a durable architectural mental model.

## 4. What Is Databricks?

Databricks is a managed cloud data, analytics, and AI platform. A useful model is:

```text
Open-source technologies
        +
Cloud infrastructure
        +
Databricks managed platform
        =
Databricks Lakehouse Platform
```

Databricks integrates with technologies such as Apache Spark, Delta Lake, Iceberg, and MLflow while adding managed compute, SQL, workflows, governance, platform operations, and development interfaces.

> Databricks is not simply “Spark in the cloud.”

Spark is a distributed processing engine. Databricks is the broader managed platform around data and AI workloads. This module intentionally does not reteach Spark or Delta internals covered elsewhere in the roadmap.

## 5. Cloud Context

Databricks operates within AWS, Microsoft Azure, or Google Cloud. Keep cloud-neutral concepts separate from cloud-specific implementation details.

```text
Cloud Provider
    |
    +-- Networking
    +-- Object Storage
    +-- Compute Infrastructure
    +-- Identity/Security Integration
    |
Databricks
    |
    +-- Data Engineering Platform
    +-- Analytics
    +-- Governance
    +-- Compute Management
    +-- Workflows
```

**AWS:** S3, VPC, IAM, cloud compute infrastructure.  
**Azure:** ADLS, VNet, Microsoft Entra ID, Azure infrastructure.  
**GCP:** GCS, VPC, Google Cloud IAM, GCP infrastructure.

Do not assume every capability is identical across clouds. Verify cloud-specific behavior against current Databricks and cloud-provider documentation.

## 6. Databricks Account

Think of the account as the top-level Databricks organization/platform boundary. It provides an administrative level above individual workspaces and is associated with account-level identity, governance, and platform concepts.

| Concept | Meaning | Scope |
|---|---|---|
| Account | Top-level Databricks organization boundary | Account |
| Workspace | Environment where users work | Workspace |
| Catalog | Governance/data namespace | Unity Catalog |
| Schema | Logical namespace | Catalog |
| Object | Table/view/volume/etc. | Schema |

Confusing account and workspace leads either to unnecessary duplication or to underestimating workspace isolation and blast radius.

## 7. Databricks Workspaces

A workspace is a working environment where users interact with Databricks and manage or use assets such as notebooks, Git folders, jobs, pipelines, SQL assets, dashboards, files, compute, settings, and permissions.

A workspace is **not the data lake**.

```text
Workspace
    |
    +-- Development environment
    +-- Notebooks
    +-- Jobs
    +-- SQL assets
    +-- Compute configuration
    +-- User collaboration

Cloud Storage
    |
    +-- S3 / ADLS / GCS
    +-- Bronze / Silver / Gold data
    +-- Tables and files
```

When a user runs a notebook, authentication and permissions are evaluated, the notebook object is resolved, compute executes the workload, governed data access is evaluated, and the compute reads/writes the configured data systems. Exact execution paths vary by cloud, compute model, access mode, and platform capability.

## 8. Workspace Architecture

A useful conceptual architecture is:

```text
User
 |
 v
Workspace
 |
 +--> Notebook
 +--> Job
 +--> SQL Warehouse
 +--> Compute
 +--> Unity Catalog
 +--> Cloud Storage
```

The important relationship is that the workspace organizes users and platform assets while compute performs execution and cloud storage commonly persists data. Governance connects identities and workloads to governed data.

Keep code/assets separate conceptually from persistent data. Production architecture should identify the identity, compute, governance path, storage system, and network path for every important workload.

## 9. Control Plane

The control plane is the management and coordination side of the platform. At a conceptual level it participates in platform management, workspace management, configuration, orchestration, metadata/platform state, APIs, identity-related operations, and job configuration.

Analogy: an airport's control function manages schedules and coordination while aircraft perform the actual flight.

```text
CONTROL PLANE
    |
    +-- Manage
    +-- Configure
    +-- Authenticate / authorize
    +-- Coordinate
    +-- Provide platform services

COMPUTE PLANE
    |
    +-- Execute workloads
    +-- Run processing
    +-- Execute SQL
    +-- Process data
```

Do not claim that all customer data is stored or processed in the control plane. Exact implementation varies and can evolve.

## 10. Classic Compute Plane

Classic compute is a compute architecture in which workload execution has an important relationship to customer/cloud infrastructure and network configuration.

```text
Databricks
   |
   v
Classic Compute
   |
   v
Cloud Network
   |
   v
Cloud Storage / Databases / APIs
```

For a Data Engineer, the architectural concerns are network placement, subnets, routes, firewall/security-group rules, private connectivity, storage access, database reachability, and cloud identity. Detailed cluster configuration belongs to Topic 02.

## 11. Serverless Compute Plane

Serverless means Databricks manages more of the compute infrastructure lifecycle and abstracts more infrastructure operations from the user.

```text
Classic
Customer/cloud infrastructure
        |
        v
Databricks workload

Serverless
Databricks-managed compute model
        |
        v
Databricks workload
```

Serverless does **not** mean no servers, free compute, no networking, or no security. Workloads still have connectivity, identity, governance, capability, and cost considerations. Classic and serverless can differ in supported capabilities and networking behavior, so verify current documentation for the target workload.

## 12. Control Plane vs Compute Plane

| Dimension | Control Plane | Compute Plane |
|---|---|---|
| Primary purpose | Management | Workload execution |
| Configuration | Platform/workspace configuration | Runtime configuration |
| Job definitions | Managed/configured | Executed |
| Notebook metadata | Platform/workspace side | Notebook code executes here |
| Spark processing | Not the workload execution layer | Yes |
| Data processing | Not the workload execution layer | Yes |
| Networking relevance | Platform connectivity matters | Very high for workload dependencies |
| Scaling | Platform management | Workload/compute scaling |

Mental model: **control plane coordinates and manages; compute plane executes.** Exact implementation differs between classic and serverless architectures.

## 13. Where Data Lives

Databricks is not simply “where the data lives.” Persistent lakehouse data commonly resides in cloud object storage such as S3, ADLS, or GCS.

```text
Compute
   |
   v
Unity Catalog / Governance
   |
   v
Cloud Object Storage
   +-- S3
   +-- ADLS
   +-- GCS
```

Databricks can work with managed tables, external tables, volumes, and files depending on the platform configuration. Unity Catalog governs supported data and AI assets; detailed catalog, schema, storage credential, external location, and authorization mechanics belong to Topic 04.

Compute/storage separation allows compute to change without requiring the persistent data to move.

## 14. Identity Architecture

The core identity model is:

| Identity | Typical Use |
|---|---|
| User | Human interaction |
| Group | Access-management unit |
| Service Principal | Automation/workloads |

```text
Human
  -> User
  -> Group
  -> Permissions

Automation
  -> Service Principal
  -> Job / CI/CD
  -> Permissions
```

Use groups for scalable human access management. Use service principals for production jobs, CI/CD, and automation rather than personal credentials. Production identity design should apply least privilege, separation of duties, auditable ownership, and an explicit credential lifecycle.

## 15. Workspace Objects

Workspace objects conceptually include:

- notebooks,
- Git folders,
- workspace files,
- jobs,
- pipelines,
- SQL queries,
- dashboards,
- alerts.

Consider object ownership carefully: critical production automation should not depend permanently on one employee's personal identity.

Keep **code/assets** separate from **data**:

```text
Code / workspace assets
  -> notebook, Git folder, job definition, pipeline definition

Data
  -> tables, files, volumes, object-storage data
```

They interact but are not the same asset.

## 16. Workspace Permissions

Workspace permissions concern access to the workspace and its assets. They are not identical to data permissions or cloud infrastructure permissions.

```text
Layer 1 — Databricks Workspace Access
Layer 2 — Unity Catalog / Data Access
Layer 3 — Cloud Infrastructure Access
```

A user may enter a workspace but lack table access. A service principal may have Databricks permissions but fail to reach a private cloud resource. Cloud authorization may be correct while the workspace object is inaccessible.

> “Access denied” is a symptom, not a diagnosis.

## 17. Security Boundaries

Production security is layered across:

1. account boundary,
2. workspace boundary,
3. identity boundary,
4. compute boundary,
5. network boundary,
6. data-governance boundary,
7. cloud account/subscription/project boundary.

Do not attempt to solve every security problem with table permissions. Security requires defense in depth across identity, workspace, compute, data governance, networking, cloud infrastructure, secrets, and auditability.

## 18. Networking Awareness

This is not a networking course. Learn enough to reason about production workloads:

- VPC/VNet,
- subnets,
- routes,
- DNS,
- security groups/firewalls,
- private/public connectivity,
- object-storage access,
- database access,
- control-plane connectivity awareness,
- classic compute networking,
- serverless networking awareness.

A correct notebook can still fail:

```text
Notebook works
   |
Code is correct
   |
Database connection fails
   |
Possibly networking
```

Investigate compute network, DNS, route, firewall/security-group rules, private endpoint/connectivity, target port, and only then credentials where appropriate. A timeout is not automatically an authentication failure.

## 19. Workspace Strategy

There is no universal correct workspace count. Evaluate isolation, security, cost, governance, collaboration, networking, administration, blast radius, CI/CD, user experience, and operational complexity.

### One workspace

Simple and collaborative, but has a larger blast radius and requires disciplined permissions.

### Multiple workspaces

```text
Organization
   |
   +-- Development
   +-- Staging
   +-- Production
```

Provides stronger environment isolation but increases administration and deployment complexity.

### Domain-oriented topology

```text
Organization
   |
   +-- Finance
   |     +-- Dev
   |     +-- Prod
   |
   +-- Customer
         +-- Dev
         +-- Prod
```

Use domain separation when security, ownership, network, compliance, or operational requirements justify it. Do not create one workspace per domain automatically.

## 20. Development / Staging / Production

A common controlled promotion model is:

```text
DEV
 |
 | CI/CD
 v
STAGING
 |
 | validation / approval
 v
PRODUCTION
```

Production should not simply be the same environment where developers experiment. Consider separate identities, service principals, catalog/data strategy, compute policies, secrets, network access, deployment, audit, and blast radius.

Topic 12 covers Asset Bundles and CI/CD in depth. Here the architectural principle is controlled promotion rather than manual production editing.

## 21. Workspace Strategy Decision Matrix

| Strategy | Appropriate when | Advantages | Disadvantages | Security/Governance | Operational Cost |
|---|---|---|---|---|---|
| Single workspace | Small team, low isolation needs | Simple, collaborative | Larger blast radius | Strong permission discipline required | Low |
| Dev + Prod | Small/medium production | Clear production boundary | Less staging isolation | Better environment separation | Medium |
| Dev + Staging + Prod | Mature engineering | Strong promotion path | More administration | Stronger environment controls | Medium-high |
| Domain-based | Domains need isolation | Clear ownership | Fragmentation risk | Strong domain boundaries | High |
| Regulated isolated | High-risk/compliance | Strong isolation | Highest complexity | Strongest boundaries | High |
| Hybrid | Mixed requirements | Flexible | Harder to govern | Tailored | Variable |

Decision rule: use multiple workspaces when the benefit of isolation is greater than the operational complexity introduced.

## 22. Databricks vs Cloud Provider

| Capability | Databricks | Cloud Provider |
|---|---|---|
| Spark platform | Managed platform capability | Underlying infrastructure |
| Object storage | Integrates with storage | S3 / ADLS / GCS |
| Networking | Platform integration/configuration | VPC/VNet/network infrastructure |
| IAM integration | Uses/integrates with identity | Cloud IAM/identity |
| Data governance | Unity Catalog and platform controls | Cloud-native controls also exist |
| Compute | Managed compute abstraction | Physical/cloud infrastructure |
| Billing | Databricks usage/SKUs | Cloud infrastructure cost |

Do not ask “does Databricks handle security?” Ask which control belongs to Databricks, which belongs to the cloud provider, and which must be implemented at both layers.

## 23. Databricks vs Open Source

```text
Open Source / Ecosystem
    |
    +-- Apache Spark
    +-- Delta Lake
    +-- Iceberg
    +-- MLflow

Databricks Platform
    |
    +-- Managed compute
    +-- Unity Catalog
    +-- Workflows
    +-- Lakeflow
    +-- SQL
    +-- Serverless
    +-- Governance
    +-- Platform operations
```

Spark is a distributed processing engine. Delta Lake and Iceberg are table-format technologies. MLflow is an open-source ML lifecycle project. Databricks is a broader managed platform around data and AI workloads.

Key interview statement: **Databricks provides a managed platform and operating model around data and AI workloads; open-source projects provide individual technologies that can also exist outside Databricks.**

## 24. Terraform and Infrastructure as Code

Infrastructure as Code describes desired platform/infrastructure state in version-controlled code.

```text
Version Control
      |
      v
Desired State
      |
      v
Terraform
      |
      v
Databricks / Cloud Resources
```

IaC improves reproducibility, review, environment consistency, promotion, auditability, and drift detection.

Good candidates include groups, service principals, permissions, workspace configuration, jobs, compute policies/configuration where supported, and critical cloud infrastructure.

Illustrative example:

```hcl
# Illustrative only. Verify current provider resources/arguments.
resource "databricks_group" "data_engineers" {
  display_name = "data-engineers"
}

resource "databricks_service_principal" "production_jobs" {
  display_name = "production-jobs"
}
```

Provider resources, arguments, authentication, and capabilities are version-sensitive. Verify against current Databricks Terraform provider documentation before execution.

## 25. Hands-On Labs

## Lab 1 — Draw the Databricks Architecture

Draw:

```text
Account -> Workspace -> Identity -> Workspace Objects -> Compute
        -> Unity Catalog -> Cloud Storage
```

Explain every arrow. Identify which pieces belong to Databricks and which belong to the cloud.

## Lab 2 — Architecture Decision

Scenario: 50 Data Engineers, three environments, PII, multiple domains, CI/CD, centralized governance.

Design workspace topology, identity, service principals, catalog strategy, environment isolation, networking, and security boundaries.

**Model direction:** begin with explicit dev/staging/prod boundaries; use groups for humans, service principals for automation, Unity Catalog for centralized governance, and private networking where required. Add domain-specific workspace isolation only where requirements justify it.

## Lab 3 — Identity Design

Design access for a Data Engineer, Data Analyst, Platform Engineer, CI/CD pipeline, and production job.

**Model:** users for humans, groups for role-based access, service principals for automation, and least privilege for every identity.

## Lab 4 — Classic vs Serverless

Choose between classic and serverless for:
- a private-network-dependent workload needing specific infrastructure controls;
- an intermittent analytics workload where managed scaling is valuable.

Evaluate networking, security, operational overhead, workload characteristics, supported capabilities, and cost. Do not assume serverless is universally superior.

## Lab 5 — Terraform Architecture

Classify groups, service principals, permissions, production jobs, workspace configuration, exploratory notebooks, and cloud networking as appropriate or inappropriate IaC candidates. Explain why durable production state is a stronger IaC candidate than temporary experimentation.

## 26. Troubleshooting and Break/Fix

Use this loop:

```text
Symptom
↓
Evidence
↓
Hypotheses
↓
Commands/UI checks
↓
Root cause
↓
Fix
↓
Verification
↓
Prevention
```

### Incident 1 — Workspace access but table access denied

Check workspace access, exact catalog/schema/table, Unity Catalog permissions, execution identity, cloud authorization where relevant, and environment mismatch.

### Incident 2 — Notebook works in development but fails in production

Compare workspace, identity, service principal, catalog, storage, network, secrets, compute model, and environment-specific configuration.

### Incident 3 — Job works manually but fails in production

Compare developer-user execution with scheduled service-principal execution. Check permissions, data access, secrets, cloud access, network access, and configuration.

### Incident 4 — Classic compute cannot access a private database

Check DNS, subnet, route, firewall/security-group rules, private connectivity, target port/listener, then credentials.

### Incident 5 — Serverless behaves differently from classic

Investigate networking, access mode, supported capabilities, permissions, secrets, and environment configuration.

### Incident 6 — Two teams affect each other's production workloads

Diagnose insufficient workspace/permission/deployment isolation. Consider stronger workspace, identity, data, and deployment boundaries while avoiding unnecessary workspace proliferation.

## 27. Common Architecture Mistakes

1. Treating the workspace as the data lake.
2. Giving every user individual permissions.
3. Running production automation with personal credentials.
4. Mixing production and experimentation.
5. Having no workspace isolation strategy.
6. Ignoring service principals.
7. Ignoring cloud networking.
8. Assuming serverless means no security concerns.
9. Assuming Databricks replaces cloud infrastructure.
10. Assuming Databricks is only Spark.
11. Hardcoding environment-specific paths.
12. Creating production resources manually.
13. Ignoring cost boundaries.
14. Using one workspace without considering blast radius.
15. Creating too many workspaces without governance.
16. Confusing workspace permissions with data permissions.

Each mistake can increase security risk, blast radius, operational fragility, cost, or governance complexity.

## 28. Production Reference Architectures

### Architecture A — Small Team

```text
Databricks Account
   |
Shared Workspace
   |
Users/Groups -> Jobs/Compute -> Unity Catalog -> Cloud Storage
```

Use this when requirements are simple and blast radius is acceptable. Keep production automation under service principals.

### Architecture B — Enterprise Data Platform

```text
Databricks Account
   |
   +-- Dev Workspace(s)
   +-- Staging Workspace(s)
   +-- Production Workspace(s)
            |
            +-- Service principals
            +-- Governed compute
            +-- Unity Catalog
            |
            +------> Cloud Storage
```

Centralize governance while giving domains controlled ownership.

### Architecture C — Regulated Enterprise

```text
Cloud Organization
   |
Restricted Network
   |
Private Connectivity
   |
Restricted Production Workspace
   |
Restricted Groups / Service Principals
   |
Controlled Compute
   |
Unity Catalog
   |
PII / Financial Data in Cloud Storage
```

Use stronger isolation, least privilege, private networking, auditability, and controlled automation where requirements justify them.

For each architecture, explicitly document components, data flow, identity flow, security boundaries, operational model, advantages, and disadvantages.

## 29. Architecture Decision Records

### ADR-001 — Single Workspace vs Multiple Workspaces

**Context:** balance collaboration with environment/security isolation.  
**Options:** single, dev/prod, dev/staging/prod, domain-based, hybrid.  
**Decision:** use the smallest topology that satisfies security, compliance, operational, and blast-radius requirements.  
**Trade-off:** more workspaces increase isolation but also administration and deployment complexity.  
**Consequence:** every workspace needs a documented purpose, owner, environment, network model, identity model, governance model, and deployment process.

### ADR-002 — Classic vs Serverless

**Context:** workloads have different network and operational requirements.  
**Decision:** select compute per workload, not by universal rule.  
**Trade-off:** serverless can reduce infrastructure operations; classic may better fit particular network/control requirements.  
**Consequence:** validate networking, security, supported features, cost, and operations.

### ADR-003 — User Credentials vs Service Principals

**Context:** production automation must survive employee changes and remain auditable.  
**Decision:** use service principals for production automation.  
**Reasons:** ownership independence, least privilege, auditability, controlled lifecycle.  
**Consequence:** define ownership, permissions, credential lifecycle, and emergency access.

### ADR-004 — Manual Configuration vs Terraform

**Context:** multiple environments must remain consistent.  
**Decision:** use IaC for durable platform and infrastructure configuration.  
**Reasons:** reproducibility, review, version control, promotion, auditability.  
**Consequence:** manage state, provider versions, authentication, review, deployment, and drift.

## 30. Command-Line / API / Configuration Examples

Databricks CLI, REST APIs, Python automation, and cloud CLIs are useful for platform operations, but exact interfaces are version-sensitive.

Use this ownership model:

```text
Databricks CLI -> Databricks platform
AWS CLI        -> AWS resources
Azure CLI      -> Azure resources
gcloud         -> GCP resources
```

Before executing any command, verify the installed CLI/API/provider version and current official documentation. Do not fabricate endpoints or teach obsolete commands as current.

For API automation, identify:
- authentication mechanism,
- target workspace/account,
- resource ownership,
- required permissions,
- idempotency,
- error handling,
- auditability.

## 31. Architecture Diagrams

### Account and workspace

```text
Databricks Account
   |
   +-- Workspace A
   |      +-- Dev
   |      +-- Jobs
   |      +-- Compute
   |
   +-- Workspace B
          +-- Production
          +-- Jobs
          +-- Compute
```

### Control/compute relationship

```text
CONTROL / MANAGEMENT
   |
   +-- configuration
   +-- APIs
   +-- job definitions
   +-- coordination
          |
          v
COMPUTE / EXECUTION
   |
   +-- classic compute
   +-- serverless compute
   +-- Spark / SQL execution
          |
          v
Cloud data systems
```

### Identity flow

```text
Human -> User -> Group -> Permissions
Automation -> Service Principal -> Job/CI/CD -> Permissions
```

### Data flow

```text
User / Job
   |
Workspace
   |
Compute
   |
Governance / Authorization
   |
Cloud Object Storage
```

Every diagram is a conceptual architecture aid; verify exact cloud/product implementation before production deployment.

## 32. Interview Preparation

### Q1. What is a Databricks workspace?
**Strong answer:** A working environment where users interact with Databricks and manage assets such as notebooks, Git folders, jobs, SQL assets, compute, and related resources. It is not the data lake.

### Q2. Account vs workspace?
**Strong answer:** The account is the higher-level organizational/platform boundary; a workspace is an environment where users and workloads operate.

### Q3. What is the control plane?
**Strong answer:** The management and coordination side of the platform, including platform/workspace configuration, APIs, orchestration, and identity-related operations at a conceptual level.

### Q4. What is the compute plane?
**Strong answer:** The execution side where Spark/SQL and other workloads actually run.

### Q5. Classic vs serverless?
**Strong answer:** Classic exposes more relationship to customer/cloud infrastructure; serverless abstracts more infrastructure management. Choose based on workload, networking, security, capabilities, operations, and cost.

### Q6. Where does customer data live?
**Strong answer:** Persistent data commonly resides in cloud object storage such as S3, ADLS, or GCS, with Databricks providing compute, governance, and platform interfaces.

### Q7. Why service principals?
**Strong answer:** They provide machine identities for automation, avoiding dependency on personal credentials and supporting least privilege and auditability.

### Q8. How would you design dev/staging/prod?
**Strong answer:** Establish explicit environment boundaries, use groups for humans, service principals for automation, governed data access, environment-specific configuration, and controlled CI/CD promotion.

### Q9. When use multiple workspaces?
**Strong answer:** When security, compliance, network, ownership, environment, or blast-radius requirements justify isolation.

### Q10. How does networking affect Databricks?
**Strong answer:** It determines whether compute can reach databases, storage, APIs, and other dependencies. DNS, routing, firewall rules, private connectivity, and network access modes can all matter.

### Q11. Databricks vs Spark?
**Strong answer:** Spark is a processing engine; Databricks is a broader managed platform around data and AI workloads.

### Q12. Databricks vs cloud provider?
**Strong answer:** Databricks provides the managed platform while the cloud provider supplies foundational infrastructure and services; production architecture must account for both.

### Q13. How secure a production workspace?
**Strong answer:** Strong identity, groups, service principals, least privilege, governed data access, network controls, environment isolation, auditable deployment, secrets management, and restricted production access.

### Q14. Why Terraform?
**Strong answer:** It makes important platform/infrastructure state reproducible, reviewable, version-controlled, promotable, and less prone to drift.

**Follow-up discipline:** For every answer, be prepared to explain a trade-off, a failure mode, and a production example.

## 33. Practice Questions

## Basic — 10

1. What is a Databricks workspace, and what is it not?
2. Which is higher level: account or workspace?
3. Which plane executes Spark processing?
4. Where does persistent data commonly live? Name S3, ADLS, and GCS.
5. Which identity should normally run production automation?
6. Why use groups instead of individual grants?
7. Does serverless mean no servers?
8. Name three workspace objects.
9. Name two cloud networking concepts relevant to Databricks.
10. Give three Databricks capabilities beyond Spark.

## Moderate — 10

11. Explain workspace, data, and cloud access as three layers.
12. A user can enter a workspace but cannot query a table. What do you check?
13. Why can a notebook work in development but fail in production?
14. Compare single workspace and dev/prod workspace strategies.
15. Why are service principals preferable for CI/CD?
16. Why is compute-storage separation useful?
17. What problems does Terraform reduce?
18. Is a database timeout automatically an authentication problem?
19. Why might a regulated workload need stronger workspace isolation?
20. Explain Databricks vs cloud provider using an S3 example.

## Hard — 5

21. Design a workspace topology for 50 Data Engineers, three environments, and PII.
22. A production job succeeds manually but fails on schedule. Design the investigation.
23. Two domains repeatedly interfere with each other in a shared workspace. What changes would you consider?
24. A company wants everything on serverless. What must be evaluated first?
25. Design an enterprise identity model including users, groups, service principals, workspace permissions, data permissions, and cloud permissions.

## 34. Knowledge Checkpoints

### Foundations
- [ ] Explain Databricks.
- [ ] Explain lakehouse compute/storage separation.
- [ ] Explain Databricks vs Spark.
- [ ] Explain Databricks vs cloud provider.

### Account and Workspace
- [ ] Explain account vs workspace.
- [ ] Explain workspace vs data lake.
- [ ] Explain workspace objects.
- [ ] Explain workspace permissions.

### Planes
- [ ] Explain control plane.
- [ ] Explain compute plane.
- [ ] Explain classic compute.
- [ ] Explain serverless.
- [ ] Explain why exact implementation can vary.

### Identity
- [ ] Explain users.
- [ ] Explain groups.
- [ ] Explain service principals.
- [ ] Explain least privilege.

### Security and Networking
- [ ] Distinguish workspace/data/cloud access.
- [ ] Explain VPC/VNet, subnet, route, DNS, firewall.
- [ ] Diagnose connectivity versus authentication.

### Workspace Strategy
- [ ] Evaluate single vs multiple workspaces.
- [ ] Design dev/staging/prod.
- [ ] Explain blast radius.
- [ ] Justify domain or regulated isolation.

### Automation
- [ ] Explain IaC.
- [ ] Explain desired state.
- [ ] Explain drift.
- [ ] Explain why Terraform matters.

## 35. Production Mental Models

```text
ACCOUNT
= Organization / platform boundary

WORKSPACE
= Working environment

CONTROL PLANE
= Management and coordination

COMPUTE PLANE
= Workload execution

STORAGE
= Where persistent data lives

UNITY CATALOG
= Governance and data-access layer

USER
= Human identity

GROUP
= Access-management unit

SERVICE PRINCIPAL
= Machine identity

NETWORK
= Connectivity boundary

TERRAFORM
= Reproducible platform configuration
```

Use these as anchors rather than memorizing isolated product terminology.

## 36. Final Capstone Exercise

### Scenario

A multinational company has:
- AWS as primary cloud,
- 100 Data Engineers,
- Data Analysts,
- ML Engineers,
- Finance data,
- customer PII,
- multiple business domains,
- dev/staging/prod,
- CI/CD,
- automated production jobs,
- private databases,
- centralized governance,
- cost controls.

### Design

Decide:
1. account strategy,
2. workspace strategy,
3. environment strategy,
4. identity strategy,
5. service-principal strategy,
6. control/compute plane understanding,
7. classic/serverless usage,
8. networking model,
9. Unity Catalog relationship,
10. cloud storage relationship,
11. Terraform strategy,
12. security boundaries,
13. production deployment model,
14. blast-radius strategy.

### Model solution

```text
AWS Organization
    |
    +-- Network / Private Connectivity
    +-- S3 / Lake
    |
Databricks Account
    |
    +-- DEV
    +-- STAGING
    +-- PROD
          |
          +-- Restricted Groups
          +-- Production Service Principals
          +-- Controlled Compute
          |
          +-- Unity Catalog
                 |
                 +-- Finance
                 +-- Customer PII
                 +-- Domain Data
                 |
                 +-- Cloud Storage
```

Use environment separation, groups for humans, service principals for automation, centralized governance, private networking where required, and IaC for durable platform state. Add domain-specific workspace isolation only where security, compliance, network, ownership, or blast-radius requirements justify it.

This is a starting architecture, not a universal template. Validate current Databricks capabilities, cloud-specific behavior, region availability, cost, networking, and regulatory requirements.

## 37. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Evidence |
|---|---|---|
| Account architecture | Yes | Account mental model and scope table |
| Workspaces | Yes | Workspace definition and architecture |
| AWS/Azure/GCP | Yes | Cloud context |
| Control plane | Yes | Dedicated section and diagram |
| Classic compute plane | Yes | Dedicated section |
| Serverless compute plane | Yes | Dedicated section and misconceptions |
| Cloud object storage | Yes | Data location |
| Unity Catalog relationship | Yes | Mental model and data access |
| Users | Yes | Identity architecture |
| Groups | Yes | Identity architecture |
| Service principals | Yes | Identity and production automation |
| Workspace objects | Yes | Object section |
| Workspace permissions | Yes | Three-layer model |
| Workspace security | Yes | Security boundaries |
| Networking | Yes | Networking awareness |
| Workspace strategy | Yes | Topology and decision matrix |
| Dev/staging/prod | Yes | Environment section |
| Multiple workspaces | Yes | Strategy |
| Domain-oriented strategy | Yes | Domain topology |
| Terraform | Yes | IaC section and example |
| Databricks vs cloud | Yes | Responsibility matrix |
| Databricks vs open source | Yes | Comparison |
| Common mistakes | Yes | 16 mistakes |
| Hands-on labs | Yes | 5 labs |
| Troubleshooting | Yes | 6 incidents |
| Production architecture | Yes | 3 reference architectures |
| ADRs | Yes | 4 ADRs |
| Architecture diagrams | Yes | Multiple diagrams |
| Interview preparation | Yes | 14 questions |
| Practice questions | Yes | 25 questions |
| Knowledge checkpoints | Yes | 7 groups |
| Final capstone | Yes | Enterprise architecture challenge |

**Audit conclusion:** Topic 01 requirements are covered with meaningful instructional treatment rather than keyword-only mentions.

## 38. Completion Checklist

### Architecture
- [ ] I can explain Databricks at a high level.
- [ ] I can explain account vs workspace.
- [ ] I can explain control plane vs compute plane.
- [ ] I can explain classic vs serverless.
- [ ] I understand where customer data lives.
- [ ] I understand Databricks/cloud responsibility boundaries.

### Identity
- [ ] I understand users.
- [ ] I understand groups.
- [ ] I understand service principals.
- [ ] I understand workspace permissions.
- [ ] I understand least privilege.

### Networking
- [ ] I understand basic VPC/VNet concepts.
- [ ] I understand private connectivity.
- [ ] I can reason about network failures.
- [ ] I can distinguish connectivity from authentication failures.

### Workspace Strategy
- [ ] I can design dev/staging/prod.
- [ ] I can evaluate single vs multiple workspaces.
- [ ] I understand blast radius.
- [ ] I can design an enterprise workspace topology.

### Automation
- [ ] I understand why Terraform matters.
- [ ] I understand infrastructure as code.
- [ ] I understand reproducible platform configuration.
- [ ] I understand configuration drift.

### Production
- [ ] I can troubleshoot workspace access issues.
- [ ] I can troubleshoot compute/network issues.
- [ ] I can reason about identity failures.
- [ ] I can design secure production architecture.
- [ ] I can explain the architecture in an interview.

## 39. Final Operating Standard

You are ready to move to Topic 02 when you can, without notes:

1. Draw the account → workspace → identity → objects → compute → governance → storage relationship.
2. Explain control plane vs compute plane in plain language.
3. Explain classic vs serverless without saying “serverless means no servers.”
4. Explain why workspace access, data access, and cloud access are different.
5. Design a reasonable dev/staging/prod topology.
6. Explain when multiple workspaces are justified.
7. Explain why production automation uses service principals.
8. Diagnose a private-database connectivity failure.
9. Explain Databricks vs Spark.
10. Explain Databricks vs the underlying cloud.
11. Explain why Terraform matters.
12. Defend architecture trade-offs using security, cost, governance, networking, reliability, and blast radius.

Use this senior-level reasoning loop:

```text
Requirement
    ↓
Security boundary
    ↓
Identity model
    ↓
Workspace topology
    ↓
Compute model
    ↓
Network path
    ↓
Governance model
    ↓
Cloud resources
    ↓
IaC / deployment model
    ↓
Operational blast radius
    ↓
Cost and reliability
```

### Current-documentation safety

Databricks product names, capabilities, CLI interfaces, Terraform resources, networking patterns, and cloud integrations evolve. Separate:
1. stable architectural concepts,
2. current Databricks terminology,
3. version-sensitive implementation details.

Verify current official Databricks and cloud-provider documentation immediately before production implementation. Do not invent APIs, CLI syntax, Terraform resource names, cloud-specific behavior, pricing, or service limits.
