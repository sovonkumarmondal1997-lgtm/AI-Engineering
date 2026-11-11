# Roadmap — Module 2D.8: Cloud, Hybrid and Multi-Cloud Data Architecture

This is the learning roadmap for the eighth module of Stage 2D, **Data
Architecture**. It tells you **what** to learn, **in what order**, **how** to
learn each topic from beginner to advanced level, **how to prove** you have
learned it, and **how to complete** the module's final cloud platform
architecture comparison project.

Module 2D.7 designed a **logical** enterprise data platform. This module asks how
that platform is realised on real cloud and hybrid environments: which provider
services supply which capabilities, how networks and identities connect them,
how far the design can be moved between providers, and how environments are
built and changed repeatably.

> **Repository note (source-of-truth limits).** The eight topic files,
> `practice-questions.md`, `README.md`, `Projects/README.md` and
> `Projects/08-cloud-platform-architecture-comparison.md` currently exist but are
> **empty**, as are the Stage 2D overview files. This roadmap therefore cannot be
> grounded in their contents. It is the first written statement of the module's
> scope, derived from the file names, the Stage 2D structure and the earlier
> module roadmaps. It does **not** claim that any topic file already contains the
> material below. Every exercise, template, scenario and target in it is a
> **recommendation**, not a documented requirement. When the topic files and the
> project file are written, their scope governs and this roadmap should be
> updated to match.
>
> **Provider service names.** Because the AWS, Azure and GCP topic files are
> empty, the provider services named in this roadmap come from **general
> architectural knowledge**, not from the repository. They are given as
> **starting points for investigation**, not as established equivalences, and
> they can change. Verify every service, capability and limit against current
> provider documentation and the topic files once written. Where the roadmap says
> "investigate", that is an instruction to research, not a claim.
>
> **Directory name.** The prompt that requested this roadmap referred to
> `STAGE 2D - DATA ARCHITECURE/`. The actual directory is
> `Stage 2D — Data Architecture/`, and the actual name is preserved.
>
> **Illustrative content.** Every number, price, system and organisation here is
> an **illustrative assumption** used to teach a method. None is a real price,
> quota, benchmark or recommended target.

---

## 1. Module overview

### 1.1 What cloud data architecture means

**Cloud data architecture** is the design of how data are acquired, stored,
processed, governed, secured and served using public-cloud infrastructure and
services, within the business, regulatory and operational constraints of an
organisation. It is about the **platform as a whole**, not about individual
products.

### 1.2 Why enterprises use public cloud for data workloads

| Driver | What it means for data |
| --- | --- |
| Elasticity | Compute scales up for peaks (month-end) and down afterwards |
| Separation of storage and compute | Cheap durable storage; pay for compute when used (see 2D.7 Topic 4) |
| Managed services | Provider operates infrastructure for databases, streaming, catalogues |
| Speed | New capability in days, not procurement cycles |
| Reach | Regions close to users; built-in redundancy options |
| Ecosystem | Analytics, ML and AI services adjacent to the data |

The costs are real too: ongoing spend, shared-responsibility security duties,
provider dependence and skills demand.

### 1.3 Cloud-native, hybrid and multi-cloud

| Term | Plain meaning | Typical reason | Main cost |
| --- | --- | --- | --- |
| **Cloud-native** (single cloud) | Designed around one provider's managed services and elasticity | Speed, simplicity, depth of integration | Provider dependence |
| **Hybrid cloud** | Some systems stay on premises (or in a private data centre) and connect to cloud | Legacy systems, latency, regulation, sunk cost | Connectivity, two operating models |
| **Multi-cloud** | Using more than one public cloud | Distinct workloads, acquisitions, resilience policy, negotiating position | Operational complexity, skills, data movement cost |

Hybrid and multi-cloud are **not** goals in themselves. They are consequences of
requirements and constraints, and each adds complexity that must be justified.

### 1.4 Business and technical drivers

Business: time to market, cost model change (capital to operating expense),
regulatory requirements, merger and acquisition integration, risk reduction.
Technical: scalability, resilience, managed operations, access to analytics and
ML capabilities, geographic distribution.

### 1.5 How cloud architecture affects each part of the data platform

| Platform area | Cloud effect |
| --- | --- |
| Ingestion | Managed ingestion and streaming services; network paths from sources matter |
| Storage | Object storage as the foundation; tiers and regions; egress costs |
| Processing | Elastic compute; serverless vs cluster; per-use billing |
| Governance | Provider IAM, policy, encryption and audit services; shared-responsibility split |
| Security | Identity-centred model plus network controls; key management |
| Availability | Zones and regions; provider-managed redundancy and its limits |
| Consumption | Managed query and serving services; private access for consumers |

### 1.6 Architecture is not a list of services

Choosing a service answers "what product?" Architecture answers "which
capabilities, with which boundaries, under which constraints, and why this
combination?". Two platforms built from the same services can have very
different security, cost and resilience depending on networking, identity,
data layout and operating model.

### 1.7 Why networking, identity, connectivity, portability and automation are architectural concerns

- **Networking and connectivity** decide who and what can reach data, how
  on-premises systems connect, and what traffic costs.
- **Identity** decides who may do what; in the cloud it is the primary control
  plane for access.
- **Portability** decides how expensive it is to change direction later.
- **Automation (infrastructure as code)** decides whether environments are
  repeatable, reviewable and recoverable.

Left to individual teams, each becomes inconsistent and risky.

### 1.8 How the module builds on earlier ones

| Earlier module | Provides |
| --- | --- |
| `../01-Data-Architecture-Foundations-and-Principles/` | Principles, quality attributes, governance, ownership |
| `../02-Requirements-Constraints-and-Architecture-Decisions/` | Measurable requirements, constraints, trade-off method, ADRs |
| `../03-Data-Architecture-Patterns-and-Reference-Architectures/` | Pattern and reference-architecture vocabulary |
| `../04-Conceptual-Logical-and-Physical-Data-Modeling/` | Models and schema evolution |
| `../05-Database-and-Storage-Architecture/` | Stores, formats, replication, lifecycle |
| `../06-Data-Integration-and-Interoperability/` | Ingestion, contracts, failure handling |
| `../07-Enterprise-Data-Platform-and-Lakehouse-Architecture/` | The logical platform that this module maps to providers |

### 1.9 How cloud architecture supports analytics, ML and AI

Cloud platforms colocate scalable storage, elastic compute, managed ML services
and model-serving options. For ML and AI, the architectural issues are: where
training data live, how they are secured and kept in region, how features and
retrieval indexes are refreshed, and how private network paths keep sensitive
data off the public internet. These depend on the networking, identity and
portability decisions in this module (serving detail follows in
`../14-Data-Access-Serving-Semantic-and-AI-Data-Architecture/`).

### 1.10 Terminology in plain language

| Term | Plain meaning |
| --- | --- |
| IaaS / PaaS / SaaS | Rent infrastructure / rent a platform to build on / rent finished software |
| Region / availability zone | A geographic area / an isolated location within it |
| Shared responsibility | Provider secures the cloud; you secure what you put in it |
| VPC/VNet | A private virtual network you control inside a provider |
| Private endpoint | A private address in your network for reaching a provider service |
| IAM | Identity and access management: who may do what to which resource |
| Egress | Data leaving a provider's network (usually charged) |
| IaC | Infrastructure described in code and applied repeatably |
| Lock-in | Cost and difficulty of leaving a provider or service |

---

## 2. Learning outcomes

After completing the module you will be able to:

1. **Explain** fundamental cloud data architecture principles, including
   shared responsibility, elasticity, resilience and cost.
2. **Describe and evaluate** AWS data architecture reference patterns.
3. **Describe and evaluate** Azure data architecture reference patterns.
4. **Describe and evaluate** GCP data architecture reference patterns.
5. **Compare** cloud services by architectural capability rather than product
   name alone, and **document** where they differ.
6. **Explain** cloud networking, identity and private connectivity, and
   distinguish reachability from permission.
7. **Design** high-level hybrid connectivity and on-premises integration
   approaches.
8. **Evaluate** portability, vendor lock-in and multi-cloud trade-offs, and
   **justify** single-cloud, hybrid or multi-cloud choices.
9. **Explain** infrastructure as code and environment promotion strategies.
10. **Produce** a documented comparison of cloud platform architecture options.
11. **Justify** architectural decisions against business, security,
    operational and financial constraints.

Each outcome is demonstrated through exercises, deliverables and the gates in
Sections 5, 9 and 10.

---

## 3. Prerequisites and knowledge dependencies

### 3.1 Prerequisite table

| # | Knowledge required | Why it matters for cloud architecture | Provided by | Review if weak |
| --- | --- | --- | --- | --- |
| P1 | Principles, quality attributes, governance, ownership | Cloud decisions are judged against these | `../01-Data-Architecture-Foundations-and-Principles/04-architecture-principles-and-quality-attributes.md`, `05-data-architecture-lifecycle-and-governance.md` | Write five principles with rationale |
| P2 | Measurable requirements and targets (freshness, availability, throughput) | Provider comparison needs numbers | `../02-Requirements-Constraints-and-Architecture-Decisions/04-latency-throughput-freshness-and-availability-targets.md` | Convert three vague statements into SLOs |
| P3 | Constraints, assumptions, dependencies, risks | Residency, vendor and skills limits eliminate options | `../02-Requirements-Constraints-and-Architecture-Decisions/05-constraints-assumptions-dependencies-and-risks.md` | Classify 15 statements |
| P4 | Trade-offs and ADRs | Provider choice is a recorded decision | `../02-Requirements-Constraints-and-Architecture-Decisions/06-architecture-trade-offs-and-decision-criteria.md`, `07-architecture-decision-records-adrs.md` | Write one ADR with three options |
| P5 | Reference architectures and pattern selection | Providers publish reference patterns that you must evaluate, not copy | `../03-Data-Architecture-Patterns-and-Reference-Architectures/07-selecting-and-combining-architecture-patterns.md` | Compare three patterns in a table |
| P6 | Logical, physical models; schema evolution | Portability of schemas and formats | `../04-Conceptual-Logical-and-Physical-Data-Modeling/01-conceptual-logical-and-physical-models.md`, `07-schema-evolution-and-backward-compatibility.md` | Explain logical vs physical |
| P7 | Object storage, formats, table formats, replication, lifecycle | Foundation of every provider's data lake | `../05-Database-and-Storage-Architecture/03-object-storage-and-file-format-selection.md`, `04-warehouse-lakehouse-and-table-format-design.md`, `06-replication-consistency-and-transaction-boundaries.md`, `07-retention-archival-and-data-lifecycle-storage-tiers.md` | Explain storage system vs table format vs platform |
| P8 | Ingestion mechanisms, CDC, contracts, failure handling | Provider ingestion services implement these mechanisms | `../06-Data-Integration-and-Interoperability/02-change-data-capture-and-database-replication.md`, `05-data-contracts-schema-registry-and-compatibility.md`, `08-integration-pattern-selection-and-failure-handling.md` | Draw failure behaviour for one flow |
| P9 | The logical platform: capabilities, zones, planes, metadata, tenancy, service levels | This module maps that platform to providers | `../07-Enterprise-Data-Platform-and-Lakehouse-Architecture/01-platform-capabilities-and-logical-reference-architecture.md`, `04-compute-storage-and-control-plane-separation.md`, `07-multi-team-isolation-and-tenant-boundaries.md` | Redraw a logical platform diagram without tool names |

### 3.2 Essential vs concurrent

| Essential before starting | Can be learned during this module |
| --- | --- |
| P1, P2, P4, P7, P9 | Basic IP addressing and DNS (taught in Topic 5) |
| P3, P5, P6, P8 (at least their gates) | Provider console familiarity (free tiers optional) |
| | Governance depth (`../10-Data-Governance-Security-Privacy-and-Compliance/`) |
| | Streaming depth (`../09-Streaming-and-Real-Time-Data-Architecture/`) |

Do the review exercise for any weak prerequisite before Topic 1. Do not begin the
project until P1–P9 are solid.

---

## 4. Recommended learning sequence

All effort estimates are **recommendations** (about 6–8 hours per week assumed),
not repository requirements.

| Seq | Source file | Topic | Why at this point | Prerequisites | Concepts first | Output before progressing | Effort (rec.) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `01-cloud-data-architecture-principles.md` | Cloud principles | Establishes vocabulary and decision criteria that make provider topics comparable | P1–P4, P9 | Shared responsibility, regions/zones, elasticity | Principles and criteria sheet | 6–8 h |
| 2 | `05-networking-identity-and-private-connectivity.md` *(Beginner level only)* | Networking and identity preview | Provider topics refer to networks and identity constantly; learn the vocabulary first | Seq 1 | VPC/VNet, subnet, IAM, endpoint | One-page glossary and diagram | 2–3 h |
| 3 | `02-aws-data-architecture-reference-patterns.md` | AWS patterns | First provider; build the capability-to-service mapping habit | Seq 1–2, P7–P9 | Capability families | AWS capability map and one traced flow | 6–8 h |
| 4 | `03-azure-data-architecture-reference-patterns.md` | Azure patterns | Same logical capabilities mapped to a second provider; start comparing | Seq 3 | Same capability families | Azure map; AWS/Azure difference notes | 6–8 h |
| 5 | `04-gcp-data-architecture-reference-patterns.md` | GCP patterns | Third provider completes the comparison set | Seq 3–4 | Same capability families | GCP map; three-way comparison draft | 6–8 h |
| 6 | `05-networking-identity-and-private-connectivity.md` *(full)* | Networking, identity, private connectivity | Now apply networking and identity concepts across the three providers | Seq 1–5 | Reachability vs permission | Network and identity boundary diagrams | 7–9 h |
| 7 | `06-hybrid-connectivity-and-on-premises-integration.md` | Hybrid connectivity | Extends private connectivity to on-premises systems | Seq 6, P8 | Latency, bandwidth, routing, DNS | Hybrid connectivity design | 6–8 h |
| 8 | `07-portability-lock-in-and-multi-cloud-trade-offs.md` | Portability, lock-in, multi-cloud | Needs the three provider views and connectivity costs | Seq 3–7 | Layers of portability, egress | Portability assessment and decision framework | 6–8 h |
| 9 | `08-infrastructure-as-code-and-environment-strategy.md` | IaC and environments | Codifies the architecture so it is repeatable; needs the decisions made earlier | Seq 1–8 | Declarative, state, promotion | IaC plan and promotion workflow | 6–8 h |
| — | `practice-questions.md` | Validation | After each topic, and fully before the project | Seq 1–9 | — | Gap log | 3–4 h |
| — | `Projects/08-cloud-platform-architecture-comparison.md` | Final project | Integrates all eight | All | — | Comparison package | 14–18 h |

**Ordering decisions.**

- The sequence follows the numeric file order, with one deliberate exception: the
  **Beginner level of Topic 5** (VPC/VNet, subnets, IAM, private endpoints) is
  studied before the provider topics, because AWS, Azure and GCP patterns are
  hard to follow without that vocabulary. The full Topic 5 follows the three
  provider topics so you can compare how each provider implements networking and
  identity.
- The three provider topics are studied **back to back, with the same capability
  framework**, so that you build a comparison and not three unrelated product
  catalogues. Keep one running comparison table (Section 7.1).
- Topic 8 (IaC) comes last because it automates decisions made in all the others.

---

## 5. Detailed beginner-to-advanced roadmap for every topic

Each topic uses the same twelve parts. Levels are cumulative. Examples use the
**illustrative** scenario of *Northbridge Bank* (Section 10.2), a fictional
mid-sized bank. Because the source topic files are empty, any specific subtopic
named below is a **recommended** learning focus.

---

### 5.1 Topic 01 — Cloud data architecture principles

Source: [`01-cloud-data-architecture-principles.md`](01-cloud-data-architecture-principles.md)

#### 5.1.1 Topic overview

This topic gives you the shared vocabulary and decision criteria for any cloud
data architecture: service and deployment models, shared responsibility,
elasticity and resilience, regions and zones, cost model, governance and
security. It also separates a **cloud service's capabilities** from the
**architecture of the platform** built from several services.

#### 5.1.2 Learning objectives

1. Define IaaS, PaaS, SaaS and the public, private, hybrid and multi-cloud
   deployment models.
2. Explain shared responsibility for a managed data service.
3. Explain elasticity, scalability, availability and resilience across zones and
   regions.
4. Explain how data residency and regulation constrain regional design.
5. Explain the cloud cost model and its main drivers.
6. State principles and decision criteria for a cloud data platform.

#### 5.1.3 Prerequisites

P1–P4, P9 (Section 3). Terms from `../07-Enterprise-Data-Platform-and-Lakehouse-Architecture/01-platform-capabilities-and-logical-reference-architecture.md`.

#### 5.1.4 Beginner level — build the foundations

- **Terms:** service model, deployment model, region, availability zone,
  shared responsibility, elasticity, managed service, pay-as-you-go.
- **Analogy:** renting a car (IaaS: you maintain it), taking a taxi (PaaS/SaaS:
  you only choose the destination), and buying one (on premises).
- **Study:** the shared-responsibility idea — for a managed database the provider
  secures hardware and the service; you secure identities, data, configuration,
  network exposure and key usage.
- **Create:** a one-page table of IaaS/PaaS/SaaS with who is responsible for
  what, and a region/zone diagram (a region with three zones).
- **Questions to answer:** What does "managed" take off your plate and what
  stays with you? Why would you put replicas in different zones?
- **Small exercise (no cloud account):** classify twelve services-in-the-abstract
  (virtual machine, managed database, object store, SaaS CRM…) by service model
  and list what you still own.

#### 5.1.5 Intermediate level — understand the architecture

- **Cloud-native data architecture:** object storage as foundation; elastic,
  separated compute; managed ingestion and catalogue; identity-centred security
  (links to 2D.7).
- **Resilience building blocks:** zone redundancy within a region; cross-region
  replication for disaster recovery; what is provider-managed vs your
  responsibility.
- **Regions and residency:** choosing regions by latency, regulation, cost and
  service availability; data that must not leave a jurisdiction; replication
  that may cross it unintentionally.
- **Cost model:** compute-time, storage volume and tier, requests, data transfer
  (especially egress), managed-service premiums, support; cost visibility via
  tagging.
- **Operational model:** who runs what; monitoring and incident handling
  responsibilities.
- **Failure scenarios:** zone outage, region outage, service-level incident at the
  provider, mis-scoped permission, runaway cost.
- **Design exercise:** draw a single-region, three-zone data platform and mark what
  survives a zone failure and what does not.
- **Trade-offs:** managed convenience vs control; elasticity vs predictability.

#### 5.1.6 Advanced level — make architecture decisions

- **Scalability and performance:** limits and quotas as design inputs (investigate
  per provider); scaling behaviour of serverless vs cluster services.
- **Reliability and disaster recovery:** zone vs region failure domains; recovery
  point and time objectives (`../12-Reliability-Resilience-and-Disaster-Recovery/`);
  idealised redundancy arithmetic:

  ```text
  parallel redundancy (independent failures): A = 1 − (1 − A1) × (1 − A2)
  e.g. two zones each 99.9%: A = 1 − 0.001 × 0.001 = 99.9999%
  ```

  This assumes independent failure; shared dependencies (a regional control
  plane, a shared service) break the assumption. State it.
- **Security and compliance:** shared-responsibility mapping to specific controls;
  residency; key management; audit.
- **Operational complexity and skills:** the cost of knowing the platform.
- **Cost optimisation:** committed-use or reserved capacity vs on-demand,
  storage tiering, right-sizing, egress avoidance; FinOps (see
  `../13-Performance-Scalability-and-Cost-Architecture/`). Prices are
  assumptions.
- **Portability and maintainability:** where provider-specific features are
  accepted (later formalised in Topic 7).
- **Decision criteria:** write a short weighted criteria set (fit, security,
  resilience, cost, skills, lock-in, time to value), fixed before comparing
  providers (2D.2 Topic 6).
- **Document** the principles and criteria in an ADR.

#### 5.1.7 Industry application and hands-on exercises

| | Exercise A — Responsibility and residency model | Exercise B — Principles and criteria |
| --- | --- | --- |
| Scenario | Northbridge plans to move analytics data to a managed cloud service | The board wants cloud principles before any vendor talks |
| Problem | Clarify what the bank still owns and where data may live | Define criteria for comparing providers |
| Inputs | Data classification, regulation assumptions | Requirements register |
| Tasks | Build a shared-responsibility table for storage, compute, identity, network, keys; define allowed regions and replication rules | Write 6–8 principles with rationale; define weighted criteria with the basis for weights |
| Deliverables | Responsibility and residency table | Principles and criteria sheet; ADR |
| Validation | Every responsibility has an owner; residency rule covers replicas and backups | Criteria fixed before scoring; each principle decides between options |
| Demonstrates | You can apply shared responsibility | You can set decision criteria |

#### 5.1.8 Real-world scenarios and architecture trade-offs

| Scenario | Business context | Constraints | Options | Pros / cons | Risks | Recommended (assumptions) | Would change if |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Single region vs cross-region DR | Regulatory reporting must survive a regional outage | Residency requires same country | (a) Single region, multi-zone; (b) second region in country; (c) second region abroad | (a) cheap, regional risk; (b) resilient, cost; (c) violates residency | Replication lag; cost doubling | (b) if a second in-country region exists and the recovery objective needs it | RTO relaxed enough for backups only |
| Managed vs self-managed | Small platform team | Skills limited | (a) Managed services; (b) self-run open-source on VMs | (a) low ops, dependence; (b) control, heavy ops | Staff turnover | (a) | Strict portability or cost control needs |

#### 5.1.9 Expected deliverables

- Shared-responsibility table.
- Region and residency rules.
- Principles and decision criteria sheet.
- Cost-driver list with assumptions.
- ADR on principles and criteria.

#### 5.1.10 Common mistakes and misconceptions

| Mistake | Why problematic | How to avoid |
| --- | --- | --- |
| "Managed means the provider handles security" | Misconfiguration and identity remain yours | Build a responsibility table |
| Assuming multi-zone equals disaster recovery | A region-level event defeats it | State failure domains explicitly |
| Ignoring egress and request costs | Surprise bills | List all cost drivers |
| Treating services as architecture | No boundaries or flows | Draw capability-level diagrams first |
| Assuming redundancy failures are independent | Shared control planes fail together | State dependencies |

#### 5.1.11 Mastery criteria

- Explain shared responsibility for a managed service with specifics.
- Distinguish zone from region failure and say which designs survive which.
- List the cost drivers of a data platform and the levers on each.

#### 5.1.12 Completion gate

- [ ] Responsibility table, residency rules and criteria sheet reviewed by one
      other person.
- [ ] You can explain the difference between a cloud service and a cloud
      architecture.
- [ ] Weaknesses (for example conflating zones and regions) addressed by redrawing
      the failure-domain diagram.

---

### 5.2 Topic 02 — AWS data architecture reference patterns

Source: [`02-aws-data-architecture-reference-patterns.md`](02-aws-data-architecture-reference-patterns.md)

> **Source status.** The topic file is empty. The services named below are
> general-knowledge **starting points for investigation**; confirm each against
> current AWS documentation and the topic file once written. Do not memorise
> service names; learn the **capability** each provides.

#### 5.2.1 Topic overview

AWS publishes reference patterns for data lakes, warehouses, streaming and
governance. This topic teaches you to read such a pattern as a set of
**capabilities** (ingest, store, process, catalogue, govern, orchestrate, serve)
and to see which services supply them, how they connect, and what constraints the
pattern introduces.

#### 5.2.2 Learning objectives

1. Map the logical capabilities of the 2D.7 platform to AWS services.
2. Trace data through a reference pattern from source to consumer.
3. Explain component responsibilities and integration points.
4. Evaluate security, reliability, scalability and cost for a pattern.
5. Compare alternative AWS designs and say when each fits.

#### 5.2.3 Prerequisites

Seq 1–2; P7–P9; the Topic 5 Beginner level.

#### 5.2.4 Beginner level — build the foundations

- **Study the capability families first** (the same list you will reuse for Azure
  and GCP): ingestion and integration, storage, processing and transformation,
  orchestration, catalogue and metadata, governance and access control,
  querying and serving, networking and identity, monitoring.
- **Starting points to investigate for each family (AWS, general knowledge):**

  | Capability family | Examples to investigate |
  | --- | --- |
  | Object storage (lake foundation) | Amazon S3 |
  | Batch/ETL and catalogue | AWS Glue (jobs and Data Catalog) |
  | Query over lake data | Amazon Athena |
  | Warehouse | Amazon Redshift |
  | Big-data processing | Amazon EMR |
  | Streaming ingestion | Amazon Kinesis; Amazon MSK (managed Kafka) |
  | Database migration / CDC | AWS Database Migration Service |
  | Orchestration | AWS Step Functions; Amazon MWAA (managed Airflow) |
  | Governance and lake permissions | AWS Lake Formation |
  | Identity and keys | AWS IAM; AWS KMS |

  Treat the list as prompts to research, **not** as a complete or authoritative
  catalogue.
- **Create:** an AWS capability map: logical capability → candidate service →
  one-sentence responsibility → "what I still need to verify".
- **Questions to answer:** Which service holds the data? Which runs the
  transformation? Which holds table definitions? Which decides who may read?
- **Small exercise (no account):** read a published AWS data lake reference
  diagram, if available, and relabel every box with its logical capability.

#### 5.2.5 Intermediate level — understand the architecture

- **Trace a flow.** Example (conceptual): source database → CDC service → raw
  object storage → ETL job → curated storage → catalogue registration → query
  service → BI. For each hop name the responsibility, the identity used, the
  network path and where failure is detected.
- **Responsibilities and boundaries:** storage vs compute vs control services;
  which services are regional; which are account-level constructs; how multi-
  account organisation separates workloads (investigate "account structure" as a
  tenancy mechanism, tying to 2D.7 Topic 7).
- **Common reference patterns:** lake-centric with serverless query; warehouse-
  centric; lakehouse with an open table format; streaming-first (investigate which
  table formats the services support).
- **Operational and security considerations:** encryption defaults, key policies,
  logging, private access to storage and analytics services, resource policies vs
  identity policies.
- **Failure scenarios:** throttling in a managed service; a failed ETL job;
  permission denied on cross-account access; zone vs region events.
- **Design exercise:** draw the AWS realisation of the 2D.7 logical architecture
  for one domain, with accounts, storage locations, catalogue and access path.
- **Trade-offs:** serverless query (low ops, per-query cost, concurrency/limit
  behaviour to investigate) vs provisioned warehouse (predictable, capacity
  management).

#### 5.2.6 Advanced level — make architecture decisions

- **Scalability and performance:** service quotas and scaling behaviour
  (investigate); partitioning and file layout effect on query cost
  (`../05-Database-and-Storage-Architecture/05-partitioning-indexing-clustering-and-data-layout.md`).
- **Reliability and disaster recovery:** zone-redundant services vs services needing
  your configuration; cross-region replication of storage and catalogue; what must
  be recreated after a region loss.
- **Security and access control:** least-privilege roles, separation of accounts,
  data-lake permission models vs raw storage permissions (investigate how
  fine-grained controls interact with direct storage access), encryption keys per
  domain, audit logging.
- **Data residency and compliance:** region choice, replication settings,
  service availability by region.
- **Cost:** storage class, request, query-scan and data-transfer charges; compute
  billing model; commitment options. Estimate with ranges and label prices as
  assumptions.
- **Operational complexity:** number of services to operate; managed vs self-run
  streaming; upgrade responsibility.
- **Portability:** open formats and table formats on object storage reduce
  coupling; proprietary catalogue and permission models increase it (Topic 7).
- **Vendor-specific capabilities and constraints:** record any capability you rely
  on that has no direct equivalent elsewhere, and any limit that shapes design.
- **Long-term evolution:** how new services attach without redesign.
- **Document** the AWS option in an ADR with alternatives and revisit triggers.
- **No universal claims:** AWS is not superior or inferior in general; fit depends
  on requirements.

#### 5.2.7 Industry application and hands-on exercises

| | Exercise A — Capability-to-service mapping | Exercise B — Pattern evaluation |
| --- | --- | --- |
| Scenario | Northbridge logical platform needs an AWS option | Two AWS patterns: serverless lake query vs provisioned warehouse |
| Problem | Map every logical capability to a candidate service with reasons | Choose between them for a BI and ML workload mix |
| Inputs | 2D.7 capability inventory | Workload profiles, cost assumptions, requirements |
| Tasks | Table of capability, candidate, rationale, assumption, verification item | Compare on cost, performance, concurrency, governance, operations; run a cost sketch |
| Deliverables | AWS capability map; traced flow diagram | Pattern comparison and ADR |
| Validation | Each capability mapped or "gap"; no unsupported equivalence claims | Criteria fixed first; sensitivity on query volume |
| Demonstrates | You think capability-first | You can evaluate patterns |

#### 5.2.8 Real-world scenarios and architecture trade-offs

| Scenario | Business context | Constraints | Options | Pros / cons | Risks | Recommended (assumptions) | Would change if |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ad hoc analytics on a large lake | Many analysts, spiky usage | Cost-sensitive | (a) Serverless query; (b) always-on warehouse | (a) pay per use, scan-cost risk; (b) predictable, idle cost | Unbounded scan costs | (a) with partitioned, columnar data and cost guardrails | Concurrency or latency needs exceed serverless behaviour |
| Cross-account data sharing | Risk consumes Retail data | Governance required | (a) Copy; (b) governed cross-account sharing | (a) simple, duplicate; (b) no copy, config complexity | Permission misconfiguration | (b) via data product interface | Consumer cannot use shared access |

#### 5.2.9 Expected deliverables

- AWS capability map with verification items.
- Traced flow diagram with identities and network paths.
- Pattern comparison and ADR.
- Dependency inventory of AWS-specific features relied upon.

#### 5.2.10 Common mistakes and misconceptions

| Mistake | Why problematic | How to avoid |
| --- | --- | --- |
| Memorising service names | Knowledge expires; no reasoning | Map capabilities |
| Assuming a service does everything its name implies | Hidden limits | Verify in docs |
| Ignoring account and permission structure | Tenancy and security gaps | Design account/identity boundaries |
| Choosing serverless without cost guardrails | Scan-driven cost surprises | Model cost ranges |
| Treating the reference pattern as a mandate | Overfit | State deviations |

#### 5.2.11 Mastery criteria

- Map each logical capability to a service and justify it.
- Trace a flow and name the identity and network path at each hop.
- Compare two patterns with numbers and constraints.

#### 5.2.12 Completion gate

- [ ] Capability map, traced flow and pattern ADR reviewed.
- [ ] No "equivalent to X" claims without a verification note.
- [ ] You can state two AWS-specific dependencies in your design.
- [ ] Weaknesses (service-name recall without reasoning) addressed by redoing the
      mapping from the logical platform.

---

### 5.3 Topic 03 — Azure data architecture reference patterns

Source: [`03-azure-data-architecture-reference-patterns.md`](03-azure-data-architecture-reference-patterns.md)

> **Source status.** The topic file is empty. Services below are general-knowledge
> **starting points for investigation**; confirm against current Azure
> documentation and the topic file once written.

#### 5.3.1 Topic overview

Azure publishes reference architectures for data lakes, warehouses, analytics
platforms and governance. This topic teaches you to read them by capability and
to compare them with the AWS mapping you already built, noting both similarities
and meaningful differences.

#### 5.3.2 Learning objectives

1. Map the logical platform capabilities to Azure services.
2. Explain how the services interact and where boundaries lie.
3. Trace data and identity through an Azure reference pattern.
4. Evaluate security, identity, networking, reliability and cost.
5. Compare viable Azure alternatives and compare them with AWS **without
   assuming identical behaviour**.

#### 5.3.3 Prerequisites

Seq 3; Topic 5 Beginner level.

#### 5.3.4 Beginner level — build the foundations

- **Reuse the capability families** from Topic 2. Fill an Azure column.
- **Starting points to investigate (general knowledge):**

  | Capability family | Examples to investigate |
  | --- | --- |
  | Object / lake storage | Azure Data Lake Storage Gen2 (on Blob Storage) |
  | Orchestration and integration | Azure Data Factory |
  | Analytics / warehouse | Azure Synapse Analytics; Microsoft Fabric |
  | Big-data / lakehouse processing | Azure Databricks (a partner-provided service on Azure) |
  | Streaming ingestion | Azure Event Hubs |
  | Governance and catalogue | Microsoft Purview |
  | Identity | Microsoft Entra ID (formerly Azure AD); managed identities |
  | Keys and secrets | Azure Key Vault |
  | Policy and organisation | Azure Policy; management groups and subscriptions |

  Names and product boundaries (for example how Fabric relates to Synapse) change;
  **verify the current state** before relying on any statement.
- **Create:** an Azure capability map beside your AWS one.
- **Questions:** Which Azure construct plays the role of an AWS account (a
  subscription? investigate), and is it equivalent?
- **Small exercise (no account):** relabel a published Azure analytics reference
  diagram with logical capabilities.

#### 5.3.5 Intermediate level — understand the architecture

- **Trace a flow:** source → integration service → lake storage (landing) →
  processing → curated storage → catalogue → warehouse/lakehouse query → BI, with
  identity (managed identities, service principals) at each hop.
- **Responsibilities and boundaries:** tenant, management group, subscription,
  resource group hierarchy as governance and billing scopes (investigate).
- **Patterns:** lake-and-warehouse; lakehouse; unified analytics SaaS-style
  platform; streaming with a lake sink.
- **Identity-centred access:** role-based access control scoped to resources;
  managed identities for service-to-service; how network rules and identity
  rules combine for storage access.
- **Operational and security considerations:** private endpoints for storage and
  analytics; encryption; monitoring; policy enforcement.
- **Failure scenarios:** a pipeline identity loses permission; a private endpoint
  DNS misconfiguration; capacity limits in a shared analytics service.
- **Design exercise:** draw the Azure realisation of the same logical domain
  platform as in Topic 2.
- **Trade-offs:** integrated platform (simpler, bundled) vs composing separate
  services (flexible, more integration).
- **Compare with AWS:** build a "similar responsibility, different behaviour"
  list; for each pair record at least one difference to investigate.

#### 5.3.6 Advanced level — make architecture decisions

- **Scalability and performance:** capacity models and limits per service
  (investigate); lake layout effects.
- **Reliability and DR:** redundancy options for storage; paired or alternate
  region approach (investigate); what must be rebuilt after region loss.
- **Security, identity and networking:** least-privilege RBAC, conditional access,
  private connectivity, firewall rules, key custody.
- **Residency and compliance:** region and sovereignty options; policy as a
  guardrail.
- **Cost:** licensing and capacity models differ from per-query models;
  reservations; storage tiers; data transfer. Prices are assumptions.
- **Operational complexity:** number of services; platform bundles reduce
  integration work and increase product coupling.
- **Portability:** open formats on the lake vs reliance on a bundled platform;
  consequences for exit.
- **Vendor-specific capabilities and constraints:** record those you depend on.
- **Existing estate:** organisations with a Microsoft identity and productivity
  estate may gain integration advantages; treat that as a requirement-specific
  factor, not a general superiority claim.
- **Document** the Azure option in an ADR.

#### 5.3.7 Industry application and hands-on exercises

| | Exercise A — Azure mapping and difference notes | Exercise B — Identity and network path |
| --- | --- | --- |
| Scenario | Northbridge already uses a Microsoft identity platform | Pipelines must read private storage without keys in code |
| Problem | Map the same logical platform to Azure and note differences from AWS | Design the identity and network path for a pipeline to storage |
| Inputs | Logical platform; AWS map | Network boundary assumptions |
| Tasks | Table: capability, Azure candidate, difference vs AWS to investigate, verification item | Specify identity type, role scope, network rule, DNS, auditing; diagram |
| Deliverables | Azure capability map; difference notes | Identity and network path diagram |
| Validation | No claim of equivalence without evidence; each difference is a research item | Reachability and permission are separately stated |
| Demonstrates | Comparative thinking | Combined identity/network reasoning |

#### 5.3.8 Real-world scenarios and architecture trade-offs

| Scenario | Business context | Constraints | Options | Pros / cons | Risks | Recommended (assumptions) | Would change if |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Unified platform vs composed services | Small team, fast delivery | Limited platform skills | (a) Integrated analytics platform; (b) compose lake, orchestration, engine | (a) fast, coupled; (b) flexible, effort | Product-roadmap dependence | (a) for the pilot, with open formats for exit | Strict portability mandate |
| Existing identity estate | Staff already in a Microsoft identity system | Single sign-on required | (a) Use existing identity for data access; (b) separate identities | (a) consistent, central; (b) isolation, duplication | Over-broad groups | (a) with scoped roles | Segregation rules forbid shared identity |

#### 5.3.9 Expected deliverables

- Azure capability map and difference notes vs AWS.
- Traced flow and identity/network path diagram.
- Azure pattern ADR.
- Dependency inventory of Azure-specific features.

#### 5.3.10 Common mistakes and misconceptions

| Mistake | Why problematic | How to avoid |
| --- | --- | --- |
| Assuming a subscription equals an AWS account | Different scoping, billing and policy behaviour | Research and record differences |
| Treating the bundled platform as portable | Coupling grows | Keep data in open formats |
| Confusing network rules with permissions | Access fails or over-grants | Separate reachability from permission |
| Relying on product names without checking current status | Products are renamed and merged | Verify documentation dates |

#### 5.3.11 Mastery criteria

- Map the logical platform to Azure and explain differences from AWS as research
  items.
- Explain a pipeline's identity and network path.
- Weigh integrated vs composed designs with stated criteria.

#### 5.3.12 Completion gate

- [ ] Azure map, difference notes and ADR reviewed.
- [ ] Every "similar to" statement carries a verification note.
- [ ] You can describe a managed-identity access path without stored keys.
- [ ] Weaknesses (equating products) addressed by listing three behavioural
      differences to research.

---

### 5.4 Topic 04 — GCP data architecture reference patterns

Source: [`04-gcp-data-architecture-reference-patterns.md`](04-gcp-data-architecture-reference-patterns.md)

> **Source status.** The topic file is empty. Services below are general-knowledge
> **starting points for investigation**; confirm against current Google Cloud
> documentation and the topic file once written.

#### 5.4.1 Topic overview

Google Cloud's data patterns centre on object storage, a serverless analytical
warehouse, managed streaming and batch processing, and governance tooling. This
topic completes your three-provider comparison and highlights how provider-
specific design choices affect portability.

#### 5.4.2 Learning objectives

1. Map the logical platform capabilities to GCP services.
2. Explain component interactions and data flows.
3. Evaluate storage, processing, governance, security, scalability and cost.
4. Compare GCP patterns with AWS and Azure **without assuming identical
   semantics**.
5. Explain how provider-specific choices affect portability.

#### 5.4.3 Prerequisites

Seq 3–4; Topic 5 Beginner level.

#### 5.4.4 Beginner level — build the foundations

- **Reuse the capability families.** Fill a GCP column.
- **Starting points to investigate (general knowledge):**

  | Capability family | Examples to investigate |
  | --- | --- |
  | Object storage | Cloud Storage |
  | Analytical warehouse | BigQuery |
  | Batch and stream processing | Dataflow (Apache Beam based); Dataproc (managed Spark/Hadoop) |
  | Messaging / streaming ingestion | Pub/Sub |
  | CDC / replication | Datastream |
  | Orchestration | Cloud Composer (managed Airflow) |
  | Governance and metadata | Dataplex (and its catalogue capabilities) |
  | Lakehouse-style access over open formats | BigLake (investigate) |
  | Identity and keys | Cloud IAM; Cloud KMS |

  Verify current names and scope.
- **Create:** a GCP capability map beside the AWS and Azure columns.
- **Questions:** How is the organisation hierarchy (organisation, folders,
  projects) used for governance and billing (investigate), and how does it
  differ from the other providers?
- **Small exercise (no account):** relabel a published GCP data reference diagram
  with logical capabilities.

#### 5.4.5 Intermediate level — understand the architecture

- **Trace a flow:** source → messaging/CDC → landing storage → processing →
  warehouse/curated tables → governance → BI/ML.
- **Responsibilities and boundaries:** projects as isolation and billing units;
  service accounts as workload identities; shared networking constructs
  (investigate whether networks are global or regional objects and what that
  means for design).
- **Patterns:** warehouse-centric with a serverless engine; lake plus warehouse;
  streaming into the warehouse; open-format lake accessed by multiple engines.
- **Operational and security considerations:** private access to Google services,
  organisation policies, encryption keys, audit logs.
- **Failure scenarios:** quota exhaustion; a streaming pipeline backlog; a service
  account with excessive roles; cross-region data location mistakes.
- **Design exercise:** draw the GCP realisation of the same logical domain
  platform.
- **Trade-offs:** a tightly integrated serverless warehouse (low operations,
  provider-specific SQL and billing model) vs open-format lake with external
  engines (flexible, more to run).
- **Compare:** extend the "similar responsibility, different behaviour" list.

#### 5.4.6 Advanced level — make architecture decisions

- **Scalability and performance:** how the serverless engine allocates and bills
  resources; slot or capacity models (investigate); partitioning and clustering
  effects on scan cost.
- **Reliability and DR:** location choices (region, multi-region) and what each
  means for durability and residency; cross-region replication (investigate).
- **Security and governance:** least-privilege roles, column/row-level controls
  where available, policy tags, VPC service perimeters (investigate), key
  management.
- **Residency:** dataset location is a fixed design decision in some services
  (investigate); verify before committing.
- **Cost:** on-demand per-byte-scanned vs capacity pricing; storage tiers; egress;
  streaming charges. Prices are assumptions.
- **Operational complexity:** fewer infrastructure components to run in the
  serverless model; deeper dependence on provider-specific behaviour.
- **Portability and lock-in:** the warehouse's SQL dialect, extensions and
  storage format; use of open table formats and external access to reduce
  coupling; cost of exit.
- **Vendor-specific capabilities:** record the capabilities you adopt because they
  have no equivalent, and the exit cost they imply.
- **Document** the GCP option in an ADR.
- **No universal claims:** the serverless model is a strength for some
  workloads and a constraint for others.

#### 5.4.7 Industry application and hands-on exercises

| | Exercise A — GCP mapping and three-way table | Exercise B — Portability impact of a provider-specific choice |
| --- | --- | --- |
| Scenario | Northbridge compares all three providers | The team likes a provider-specific warehouse feature |
| Problem | Complete the capability mapping for GCP and compare with AWS/Azure | Decide whether to adopt it and record the lock-in consequence |
| Inputs | AWS and Azure maps | Feature description, exit scenario |
| Tasks | Three-column table with differences to research and verification items | Assess dependency, exit effort (qualitative and ranges), mitigation (open formats, abstraction at a layer) |
| Deliverables | Three-way capability table; GCP ADR | Portability assessment row set |
| Validation | No equivalence claim without a verification note | Exit effort stated with assumptions; mitigation has a cost |
| Demonstrates | Fair comparison | Portability reasoning |

#### 5.4.8 Real-world scenarios and architecture trade-offs

| Scenario | Business context | Constraints | Options | Pros / cons | Risks | Recommended (assumptions) | Would change if |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Unpredictable analyst demand | Highly variable query load | Small ops team | (a) Serverless per-scan billing; (b) capacity reservation | (a) elastic, cost spikes; (b) predictable, idle waste | Budget overruns | (a) with quotas and cost alerts, move heavy users to (b) | Spend exceeds capacity pricing break-even |
| ML and analytics on the same data | Data science needs raw and curated | Governance required | (a) Warehouse-only; (b) lake plus warehouse | (a) simple; (b) flexible for ML | Duplicated governance | (b) with unified metadata | Warehouse supports the ML tooling needed |

#### 5.4.9 Expected deliverables

- GCP capability map.
- Three-way comparison table with research and verification items.
- Portability assessment for provider-specific choices.
- GCP ADR.

#### 5.4.10 Common mistakes and misconceptions

| Mistake | Why problematic | How to avoid |
| --- | --- | --- |
| "Serverless = no design needed" | Layout and cost behaviour still matter | Design partitioning and guardrails |
| Treating similar names as identical features | Wrong comparisons | Verify behaviour, record differences |
| Ignoring location constraints | Residency breaches | Check fixed-location settings early |
| Adopting provider-specific features without exit estimate | Hidden lock-in | Record dependency and exit cost |

#### 5.4.11 Mastery criteria

- Map the logical platform to GCP and place it in the three-way table.
- Explain a provider-specific choice's effect on portability.
- Compare per-use and capacity pricing models with numbers.

#### 5.4.12 Completion gate

- [ ] GCP map, three-way table and portability notes reviewed.
- [ ] Differences are phrased as research items, not conclusions.
- [ ] Break-even arithmetic for one pricing choice completed (assumed prices).
- [ ] Weaknesses (name-based equivalence) addressed by listing differences for
      three paired services.

---

### 5.5 Topic 05 — Networking, identity and private connectivity

Source: [`05-networking-identity-and-private-connectivity.md`](05-networking-identity-and-private-connectivity.md)

#### 5.5.1 Topic overview

In the cloud the question "can this component read that data?" has two
independent halves: **can it reach it** (network) and **is it allowed to** (identity
and permission). This topic teaches both, how they complement each other, and
how private connectivity keeps data off the public internet.

#### 5.5.2 Learning objectives

1. Explain virtual networks, subnets, routing and name resolution.
2. Explain security rules, segmentation and trust boundaries.
3. Explain private endpoints or equivalent private service access.
4. Distinguish authentication from authorisation; explain workload identity and
   least privilege.
5. Distinguish network reachability from permission, and show how they combine.

#### 5.5.3 Prerequisites

Seq 1; basics of IP addressing (learned here); P9 (tenant boundaries:
`../07-Enterprise-Data-Platform-and-Lakehouse-Architecture/07-multi-team-isolation-and-tenant-boundaries.md`).

#### 5.5.4 Beginner level — build the foundations

- **Terms:** IP address, CIDR block, subnet, route, gateway, firewall/security
  group, DNS, public vs private address, endpoint, identity, role, policy.
- **Analogy:** a building: corridors and doors (network) and key cards with
  access rights (identity). Having a corridor to a room does not mean your card
  opens it.
- **Basic arithmetic:** a /24 block has 2^(32−24) = 256 addresses; a /16 has
  65,536. (Providers reserve some addresses in each subnet; investigate.)
- **Create:** a diagram of one virtual network with a public and a private
  subnet, and a data service reached from the private subnet.
- **Questions to answer:** What does a route table decide? What does a security
  rule decide? What does an identity policy decide?
- **Small exercise (no account):** for ten access attempts (an analyst's laptop to
  storage, a pipeline to a database, a partner to an API…) state whether the
  failure would be a network, DNS or permission issue.

#### 5.5.5 Intermediate level — understand the architecture

- **Network design:** address planning without overlaps (especially with on-
  premises ranges); subnets per tier; separate subnets or networks per
  environment and sensitivity.
- **Controls:** security groups/NSGs/firewall rules (stateful vs stateless is a
  concept to investigate), routing, network ACLs.
- **Private access to managed services:** private endpoints or equivalent so that
  traffic to a storage or analytics service stays on the provider's private
  network; the DNS consequence: names must resolve to private addresses inside
  your network (a frequent failure cause).
- **Identity:** users, groups, roles, service identities; short-lived credentials
  vs long-lived keys; federation with a corporate identity provider; separation
  of administrative and data access.
- **Authentication vs authorisation:** who are you vs what may you do.
- **Encryption in transit:** TLS everywhere; certificates; what private
  connectivity does and does not encrypt.
- **Combined model.** An access succeeds only if **all** hold:

  | Layer | Question | Typical failure |
  | --- | --- | --- |
  | Name resolution | Does the name resolve to the intended (private) address? | Resolves to public address |
  | Network path | Is there a route and is it allowed by rules? | Timeout |
  | Authentication | Is the caller who it claims to be? | 401 / token errors |
  | Authorisation | Is the identity permitted this action on this resource? | 403 / access denied |
  | Service-side network rules | Does the service accept traffic from this source? | Blocked by service firewall |

- **Failure scenarios:** DNS not forwarded for private names; overlapping
  address ranges; role too broad; secret in code.
- **Design exercise:** diagram users, applications, data services and an on-
  premises system with trust boundaries and the five layers above.
- **Trade-offs:** strict segmentation (safer, more to manage) vs flat network
  (simple, larger blast radius).

#### 5.5.6 Advanced level — make architecture decisions

- **Scalability and performance:** address space exhaustion; throughput limits of
  gateways and endpoints (investigate); cross-zone/region traffic cost and
  latency.
- **Reliability:** redundant paths; DNS as a dependency; regional failure of
  shared network services.
- **Security:** zero-trust thinking (verify identity per request, not by network
  location); data-exfiltration controls (service perimeters or policies that stop
  data leaving to unapproved destinations — investigate per provider);
  workload identity federation to avoid stored keys; just-in-time elevated
  access; auditing and alerting.
- **Compliance:** logging retention, key custody, separation of duties.
- **Operational complexity:** central network team vs delegated; landing zones;
  guardrails as policy; troubleshooting responsibilities.
- **Cost:** private endpoints, gateways, inter-zone/region transfer and NAT
  charges (investigate each; prices are assumptions).
- **Provider differences:** how each provider models networks, identity scopes and
  private service access (collect in the three-way table; do not assume the
  same semantics).
- **Decision criteria and ADR:** public endpoint with strong identity vs private
  endpoint; flat vs segmented; per-domain networks vs shared network.
- **Network controls and identity controls complement each other; neither
  replaces the other.** A private network does not authorise a caller; a valid
  identity does not make an exposed endpoint safe.

#### 5.5.7 Industry application and hands-on exercises

| | Exercise A — Boundary and identity diagram | Exercise B — Troubleshooting matrix |
| --- | --- | --- |
| Scenario | Northbridge analytics must read customer data privately | A pipeline suddenly cannot read storage |
| Problem | Design network and identity boundaries for users, pipelines, services and on-premises systems | Decide the diagnostic order |
| Inputs | Logical platform; classification; on-premises ranges (assumed) | Five-layer model |
| Tasks | Draw boundaries; choose private access; define workload identities, roles, secrets approach; plan address ranges without overlap | For 8 symptoms give likely layer, first check, fix owner |
| Deliverables | Network and identity boundary diagram; address plan | Troubleshooting matrix |
| Validation | Each access path lists name, route, authn, authz, service rule; no long-lived keys in design | Each symptom maps to one layer; checks ordered cheapest first |
| Demonstrates | You can design secure connectivity | You can reason about failures |

#### 5.5.8 Real-world scenarios and architecture trade-offs

| Scenario | Business context | Constraints | Options | Pros / cons | Risks | Recommended (assumptions) | Would change if |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Public vs private storage access | Regulated data | Auditor requires no public exposure | (a) Public endpoint with strict identity; (b) private endpoints | (a) simple, internet-exposed; (b) private, DNS/endpoint management | DNS misconfiguration | (b) for regulated data | Cost or complexity unjustifiable for low-risk data |
| Pipeline credentials | Pipelines run in several accounts | No stored secrets allowed | (a) Long-lived keys; (b) workload identity with short-lived tokens | (a) simple, leak risk; (b) safer, setup effort | Over-broad roles | (b) | Legacy tools cannot use workload identity |

#### 5.5.9 Expected deliverables

- Network and identity boundary diagram with trust boundaries.
- Address plan.
- Access-path table (name, route, authn, authz, service rule).
- Troubleshooting matrix.
- ADR on private vs public access.

#### 5.5.10 Common mistakes and misconceptions

| Mistake | Why problematic | How to avoid |
| --- | --- | --- |
| "Private network = authorised" | Any workload in it may read | Apply least-privilege identity too |
| "Strong identity = safe public endpoint" | Exposure and denial-of-service risk | Combine layers |
| Overlapping address ranges | Cannot connect on-premises or peer networks | Plan ranges up front |
| Forgetting DNS | Private endpoints unusable | Include name resolution in every design |
| Long-lived access keys | Leak risk | Workload identity |

#### 5.5.11 Mastery criteria

- Explain the five-layer access model with an example failure at each layer.
- Design an address plan with no overlaps.
- Explain how network and identity controls complement each other.

#### 5.5.12 Completion gate

- [ ] Boundary diagram, address plan and troubleshooting matrix reviewed.
- [ ] Reachability and permission are separately stated for every path.
- [ ] You can describe how a provider-specific private-access mechanism differs
      (as a research item) across the three providers.
- [ ] Weaknesses (DNS blindness, key reliance) addressed by redoing one path.

---

### 5.6 Topic 06 — Hybrid connectivity and on-premises integration

Source: [`06-hybrid-connectivity-and-on-premises-integration.md`](06-hybrid-connectivity-and-on-premises-integration.md)

#### 5.6.1 Topic overview

Most enterprises cannot move everything to the cloud at once. Hybrid
architecture connects on-premises systems to cloud data platforms with
acceptable security, latency, bandwidth and reliability. This topic teaches you
to choose a connectivity pattern from requirements and to design the
integration at a conceptual level, not to configure devices.

#### 5.6.2 Learning objectives

1. Identify hybrid requirements and constraints.
2. Compare VPN and dedicated private connectivity.
3. Explain routing and DNS dependencies in a hybrid design.
4. Design on-premises source integration with data movement estimates.
5. Define security boundaries, failure handling, ownership and troubleshooting.

#### 5.6.3 Prerequisites

Seq 6; P8 (CDC, batch, failure handling); Topic 5.

#### 5.6.4 Beginner level — build the foundations

- **Terms:** hybrid, site-to-site VPN, dedicated private connection (a physical
  circuit from a data centre to the provider), bandwidth, latency, throughput,
  routing (static/dynamic), on-premises, data gateway/agent.
- **Analogy:** a private road between your factory and the provider's depot
  versus a public road with an armoured van (VPN over the internet).
- **Study:** why hybrid exists — legacy systems, regulation, latency to
  factory/branch systems, sunk cost, phased migration.
- **Create:** a simple diagram: on-premises sources → connection → cloud
  landing storage.
- **Questions to answer:** What can a VPN over the internet not promise? Why is
  an encrypted tunnel not the same as a dedicated circuit?
- **Small exercise:** list six on-premises systems and, for each, whether it
  could connect over VPN, a dedicated link, or neither.

#### 5.6.5 Intermediate level — understand the architecture

- **Connectivity options (conceptual comparison):**

  | Aspect | Site-to-site VPN over internet | Dedicated private connection |
  | --- | --- | --- |
  | Path | Public internet, encrypted tunnel | Private circuit via a connectivity provider |
  | Setup time | Short | Long (provisioning) |
  | Bandwidth | Limited by tunnel and internet path | Higher, committed options |
  | Latency/jitter | Variable | More predictable |
  | Cost | Lower | Higher (port and circuit) |
  | Typical use | Start, backup, low volume | Large, steady or latency-sensitive flows |

  Combining them (dedicated primary, VPN backup) is a common pattern to
  investigate. Specific product names per provider are research items.
- **Routing and DNS:** exchanging routes between sites and cloud (static vs
  dynamic routing — investigate); address overlap; DNS forwarding so
  on-premises systems resolve private cloud names and cloud workloads resolve
  on-premises names.
- **On-premises integration patterns:** extraction agents, CDC from on-premises
  databases (2D.6 Topic 2), file transfer, API gateways, message bridging, data
  gateways.
- **Data movement arithmetic.** *Illustrative:* moving 50 TB over a 1 Gbps
  link:

  ```text
  bits = 50 × 10^12 B × 8 = 4 × 10^14 bits
  time at 100% utilisation = 4 × 10^14 / 10^9 = 400,000 s ≈ 4.6 days
  time at 70% effective throughput = 400,000 / 0.7 ≈ 571,429 s ≈ 6.6 days
  ```

  State the assumed efficiency and whether the link is shared.
- **Security boundaries:** what on-premises systems may reach, what the cloud may
  reach back, inspection points, segmentation, credentials for agents.
- **Failure scenarios:** link failure; route flapping; DNS forwarder failure;
  on-premises maintenance window; agent crash.
- **Design exercise:** produce a conceptual hybrid design for three on-premises
  sources.
- **Trade-offs:** cost vs reliability vs setup time.

#### 5.6.6 Advanced level — make architecture decisions

- **Selecting the pattern from requirements:** volume and growth, freshness
  (`../02-Requirements-Constraints-and-Architecture-Decisions/04-latency-throughput-freshness-and-availability-targets.md`), availability, security, timeline, budget.
- **Reliability and recovery:** redundant links across different physical paths and
  locations; failover behaviour and its time; what happens to in-flight data
  movements; idempotent resumable transfers (2D.6 Topics 7–8).
- **Latency and chattiness:** application protocols that make many small round
  trips perform badly over distance; batch rather than chat.
- **Bandwidth planning:** peak vs sustained; backlog catch-up
  (`catch_up_time = backlog / (capacity − arrival)`); reserving headroom for
  recovery.
- **Security and compliance:** encryption in transit across the link; key
  custody; residency; logging at the boundary; third-party connectivity provider
  risk.
- **Operational ownership:** who owns the on-premises side, the circuit, the cloud
  side, the DNS; joint troubleshooting runbooks; change coordination.
- **Cost:** circuit, port, transfer charges (direction-dependent; investigate),
  duplicated operations. Prices are assumptions.
- **Migration strategy:** phased; coexistence; when to retire on-premises
  systems; dependency order.
- **Conceptual vs implemented design:** the output of this topic is an
  architecture and a validation plan, not router configurations.
- **Document** the connectivity choice in an ADR with alternatives and revisit
  triggers (for example data volume doubling).
- **When hybrid is preferable to moving everything:** latency-bound local
  systems, regulation, expensive-to-migrate platforms, long-lived depreciation.

#### 5.6.7 Industry application and hands-on exercises

| | Exercise A — Connectivity pattern selection | Exercise B — Hybrid integration design |
| --- | --- | --- |
| Scenario | Northbridge's core ledger remains on premises for three years | 2 TB/day of ledger changes and files must reach the cloud lake |
| Problem | Choose a connectivity pattern | Design source integration, security, failure handling |
| Inputs | Volumes, freshness, availability target, timeline, budget (assumed) | Pattern chosen; CDC and batch concepts |
| Tasks | Compare options on the criteria; compute transfer time and headroom; recommend and record ADR | Draw the design; define agents, routes, DNS, identity, retry/resume, monitoring, ownership |
| Deliverables | Option comparison and ADR | Conceptual hybrid design and failure matrix |
| Validation | Arithmetic with units and assumptions; criteria fixed first | Every failure has detection and recovery; DNS and routing dependencies stated |
| Demonstrates | You can select a pattern | You can design hybrid integration |

#### 5.6.8 Real-world scenarios and architecture trade-offs

| Scenario | Business context | Constraints | Options | Pros / cons | Risks | Recommended (assumptions) | Would change if |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Quick start vs long-term link | Pilot must start next month | Dedicated link takes months | (a) VPN now; (b) wait for dedicated link; (c) VPN now, dedicated later | (a) fast, limited; (b) delay; (c) staged | Pilot saturates VPN | (c) | Pilot volume exceeds VPN capacity |
| Latency-sensitive branch systems | Branch applications need low latency to a database | Cloud region far from branches | (a) Move database; (b) keep on premises and replicate | (a) simpler estate, latency risk; (b) low latency, replication | Replication lag | (b) | A closer region is available |

#### 5.6.9 Expected deliverables

- Connectivity option comparison with transfer-time arithmetic.
- Conceptual hybrid architecture diagram.
- Routing and DNS dependency list.
- Failure and recovery matrix.
- Connectivity ADR.

#### 5.6.10 Common mistakes and misconceptions

| Mistake | Why problematic | How to avoid |
| --- | --- | --- |
| Assuming advertised bandwidth is usable throughput | Overheads and sharing | Use an efficiency factor |
| Forgetting DNS and routing | Connectivity "works" but names do not resolve | List dependencies |
| Single link without a failure plan | Outage halts ingestion | Design redundancy and resumable transfers |
| Treating conceptual design as configuration | False confidence | State it is conceptual |
| Ignoring ownership | Nobody owns cross-boundary incidents | Assign joint owners |

#### 5.6.11 Mastery criteria

- Compare VPN and dedicated connectivity on specific criteria.
- Compute transfer times with assumptions and plan for backlog recovery.
- Design failure handling for link, DNS and agent failures.

#### 5.6.12 Completion gate

- [ ] Option comparison, arithmetic, design diagram and failure matrix reviewed.
- [ ] Routing, DNS and ownership documented.
- [ ] You can explain why you did or did not choose a dedicated link.
- [ ] Weaknesses (bandwidth optimism) addressed by recomputing with a lower
      efficiency factor.

---

### 5.7 Topic 07 — Portability, lock-in and multi-cloud trade-offs

Source: [`07-portability-lock-in-and-multi-cloud-trade-offs.md`](07-portability-lock-in-and-multi-cloud-trade-offs.md)

#### 5.7.1 Topic overview

**Lock-in** is the cost and difficulty of changing provider or service.
**Portability** is how much of your data, code, metadata and operational
procedures can move. Portability is **not binary**: an architecture can be
highly portable at one layer and tightly coupled at another. **Multi-cloud**
means using more than one provider; it is justified only by explicit
requirements, because it multiplies complexity.

#### 5.7.2 Learning objectives

1. Identify the layers at which lock-in occurs.
2. Distinguish genuine portability requirements from unnecessary abstraction.
3. Quantify egress, transfer and exit costs.
4. Evaluate multi-cloud operational complexity and skills.
5. Decide between single-cloud, hybrid, multi-cloud-by-workload and
   distributed multi-cloud.

#### 5.7.3 Prerequisites

Seq 3–7; P4 (trade-offs); `../05-Database-and-Storage-Architecture/03-object-storage-and-file-format-selection.md`.

#### 5.7.4 Beginner level — build the foundations

- **Terms:** lock-in, portability, abstraction layer, managed-service dependency,
  open standard, egress, exit cost, multi-cloud, active-active, disaster recovery
  (DR).
- **Layers of portability to study:**

  | Layer | Examples | Typical portability |
  | --- | --- | --- |
  | Data | Files in open formats | High |
  | Table/metadata | Open table formats and their catalogues | Medium |
  | Code | SQL dialects, Spark/Beam code, UDFs | Medium–low |
  | Services | Managed streaming, warehouse features | Low |
  | Identity and policy | IAM models | Low |
  | Operations | Runbooks, monitoring, IaC | Medium–low |

- **Analogy:** moving house: boxes of books (data) move easily; built-in
  cabinets (managed services) do not.
- **Questions to answer:** Which layers matter for your organisation? What would
  leaving cost?
- **Small exercise:** place twenty platform components into the layer table with a
  portability rating.

#### 5.7.5 Intermediate level — understand the architecture

- **Why organisations choose multi-cloud:** regulatory (concentration risk or
  data location), acquisitions, best-of-breed service for a specific workload,
  customer requirements, negotiating position. Each should be evidenced.
- **Why many do not benefit:** duplicated skills, lowest-common-denominator
  design, egress costs, security-model differences, more tooling.
- **Data movement costs.** *Illustrative:* transferring 50 TB out at an assumed
  $0.09 per GB:

  ```text
  50 TB = 50,000 GB;  cost = 50,000 × 0.09 = $4,500  (assumed price, one-off)
  recurring: 5 TB/month × 12 × $0.09 × 1,000 GB/TB = $5,400 per year
  ```

  Add transfer time (Topic 6 arithmetic) and the cost of running both sides.
- **Abstraction layers:** open-source engines, portable orchestration, container
  platforms, formats. Benefits (reduced coupling) and costs (lowest common
  denominator, extra ownership, leaky abstractions).
- **DR vs active multi-cloud:** a second provider for DR (cold/warm standby) is
  much simpler than running active workloads on two providers.
- **Failure scenarios:** a cross-cloud link fails; identity differs between
  clouds; a portability layer lags behind provider features.
- **Design exercise:** classify each layer of a Northbridge design as portable,
  partly portable or provider-specific.
- **Trade-offs:** speed and depth (provider-specific features) vs flexibility
  (portable stack).

#### 5.7.6 Advanced level — make architecture decisions

- **Portability by layer is a decision per layer.** Decide where you accept
  coupling (the warehouse engine?), where you insist on openness (data formats,
  table format, schemas) and where you add thin abstraction (orchestration
  definitions, IaC modules).
- **Exit cost estimation.** Components: data transfer, re-implementation of code,
  re-creation of policies and identity, retraining, parallel running, risk of
  errors. Express as ranges with assumptions; compare with the cost of
  maintaining portability.

  ```text
  expected_value_of_portability ≈ P(exit needed) × avoided_exit_cost − cost_of_maintaining_portability
  ```

  Inputs are uncertain; present low/expected/high, and show the sensitivity to
  P(exit needed).
- **Concentration risk and regulators:** when regulators expect an exit plan or
  concentration management (investigate applicable rules for your sector); an
  exit plan can be a documented, tested procedure rather than live multi-cloud.
- **Operational complexity and skills:** two sets of tooling, security models,
  billing, support contracts; incident handling across providers.
- **Security consistency:** policy parity across providers; identity federation.
- **Data gravity:** data and compute attract each other; splitting them across
  clouds causes continuous transfer cost and latency.
- **Decision framework:** single cloud with open data layer and an exit plan;
  hybrid for on-premises constraints; multi-cloud by workload where there is an
  evidenced reason; distributed multi-cloud only with a strong requirement
  (Section 7.3).
- **Document** the portability stance per layer in an ADR with revisit triggers.
- **Avoid:** "multi-cloud for resilience" without recovery objectives and tested
  failover; abstractions that remove the benefits that justified the cloud.

#### 5.7.7 Industry application and hands-on exercises

| | Exercise A — Portability and lock-in assessment | Exercise B — Multi-cloud justification |
| --- | --- | --- |
| Scenario | Northbridge's board asks "can we leave in two years?" | A business unit wants a second cloud for ML |
| Problem | Assess portability per layer and estimate exit cost | Decide whether multi-cloud is justified |
| Inputs | Provider mappings, data volumes, code inventory | Requirements, costs, skills |
| Tasks | Fill the portability table; estimate exit cost ranges; propose mitigations (open formats, exit plan) | Compare single cloud, workload-split and distributed options; compute egress and operating cost; recommend |
| Deliverables | Portability assessment and exit-plan outline | Multi-cloud decision record |
| Validation | Each dependency has mitigation and residual limitation; ranges with assumptions | Requirement-evidence for each driver; costs include both sides |
| Demonstrates | Layered portability reasoning | Justified multi-cloud decision |

#### 5.7.8 Real-world scenarios and architecture trade-offs

| Scenario | Business context | Constraints | Options | Pros / cons | Risks | Recommended (assumptions) | Would change if |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Regulator expects an exit plan | Critical workloads in one provider | No live multi-cloud mandated | (a) Live multi-cloud; (b) single cloud, open data layer, tested exit plan | (a) strongest, costly; (b) cheaper, exit takes time | Untested plan | (b), test annually | Regulator requires active dual running |
| Best-of-breed ML service | One provider offers a service needed | Data in another provider | (a) Move data; (b) use cross-cloud access; (c) copy a subset | (a) one cloud; (b) latency/egress; (c) duplicate | Continuous egress | (c) for a bounded subset if volume small | Subset grows beyond break-even |

#### 5.7.9 Expected deliverables

- Portability layer assessment.
- Exit-cost range estimate and exit-plan outline.
- Multi-cloud decision record.
- Dependency inventory (provider-specific features and mitigations).

#### 5.7.10 Common mistakes and misconceptions

| Mistake | Why problematic | How to avoid |
| --- | --- | --- |
| Treating portability as all or nothing | Wrong decisions | Decide per layer |
| Multi-cloud "for resilience" without tests | Complexity without benefit | Define recovery objectives and drill |
| Heavy abstraction to avoid lock-in | Lose provider strengths; new lock-in to the abstraction | Abstract where it pays |
| Ignoring egress and data gravity | Runaway cost | Quantify transfers |
| Believing lock-in is always bad | Depth often brings value | Compare cost of coupling with benefit |

#### 5.7.11 Mastery criteria

- Classify a design by portability layer and justify each choice.
- Estimate exit and egress costs with ranges.
- Decide among deployment strategies with explicit requirement evidence.

#### 5.7.12 Completion gate

- [ ] Assessment, exit-cost ranges and decision record reviewed.
- [ ] A case where single cloud is recommended is written and defended.
- [ ] Egress arithmetic has units and assumed prices.
- [ ] Weaknesses (binary thinking) addressed by redoing the assessment per layer.

---

### 5.8 Topic 08 — Infrastructure as code and environment strategy

Source: [`08-infrastructure-as-code-and-environment-strategy.md`](08-infrastructure-as-code-and-environment-strategy.md)

#### 5.8.1 Topic overview

**Infrastructure as code (IaC)** describes infrastructure in version-controlled
files that are reviewed, tested and applied automatically, so environments are
repeatable and changes are traceable. **Environment strategy** defines how
development, test, staging and production are separated and how changes are
promoted between them.

#### 5.8.2 Learning objectives

1. Explain IaC and the declarative vs imperative styles.
2. Design environment separation and a promotion workflow.
3. Explain state management, drift detection and policy enforcement.
4. Manage configuration and secrets safely.
5. Plan rollback and recovery.
6. Distinguish documenting a design, writing IaC and deploying/operating.

#### 5.8.3 Prerequisites

Seq 1–8; version-control basics (Stage 0, `../../Stage 0 — Computer & Digital Foundation/04-Developer-Environment/10-git-github-and-ssh-basics.md`); P9.

#### 5.8.4 Beginner level — build the foundations

- **Terms:** IaC, declarative (describe the desired end state), imperative
  (describe the steps), state, drift, module, environment, promotion, pipeline,
  policy as code, secret.
- **Analogy:** a recipe and a kitchen: IaC is the recipe; running it produces the
  same dish each time; drift is someone changing the kitchen by hand.
- **Study:** why click-built infrastructure fails: undocumented, unrepeatable,
  unreviewable.
- **Create:** a one-page table of declarative vs imperative with pros and cons.
- **Questions to answer:** What is the state, and why does it matter? What can
  go wrong when two people change infrastructure by hand?
- **Small exercise (local, free):** write pseudocode IaC for "a storage location
  with encryption on and a read role"; no provider account needed.
  Illustrative pseudocode:

  ```text
  resource storage_location "raw":
      region     = var.region
      encryption = true
      versioning = true
  resource role_binding "pipeline_reads_raw":
      principal  = identity.pipeline
      permission = "read"
      scope      = storage_location.raw
  ```

#### 5.8.5 Intermediate level — understand the architecture

- **Environments:** development, test, staging, production; isolation (separate
  accounts/subscriptions/projects, 2D.7 Topic 7); data in non-production
  (synthetic or masked); parity vs cost.
- **Reusable modules:** versioned building blocks (a "data product storage"
  module with encryption, tagging, access baked in); parameterised per
  environment.
- **Version control and review:** changes by pull request, peer review, automated
  checks.
- **Promotion workflow:** same code, different variables; plan → review → apply
  per environment; approvals for production; artefact versioning.
- **State management:** where state is stored, locking against concurrent
  changes, protecting state (it may contain sensitive values), splitting state
  to limit blast radius.
- **Configuration and secrets:** configuration in variables; secrets in a
  secrets manager, never in code; rotation.
- **Drift detection:** compare actual with declared; alert; reconcile by
  re-applying or by updating the code deliberately.
- **Policy enforcement:** policy as code (for example "no public storage", "tags
  required") checked before apply and continuously.
- **Failure scenarios:** a failed apply leaves partial infrastructure; state
  lock stuck; a manual fix causes drift; a module change breaks many stacks.
- **Design exercise:** draw the promotion workflow from commit to production with
  checks.
- **Trade-offs:** strictness of review vs speed; many small stacks vs few large.

#### 5.8.6 Advanced level — make architecture decisions

- **Scalability:** organise code and state by domain, environment and lifecycle;
  avoid a single giant state.
- **Reliability and recovery:** rollback is usually "apply the previous version"
  and may not undo data-affecting changes; destructive changes need protection
  (prevent-destroy, backups, approvals); rebuilding an environment from code as a
  DR technique (links to `../12-Reliability-Resilience-and-Disaster-Recovery/`).
- **Security and least privilege:** the pipeline identity is powerful; scope it
  per environment; separate plan and apply identities; approval gates; audit.
- **Governance and compliance:** evidence that production changed only via
  reviewed pipelines; policy exceptions with expiry.
- **Multi-provider IaC:** a provider-neutral tool can drive several providers,
  but the resources are still provider-specific; you reuse the workflow, not the
  definitions (links to Topic 7).
- **Cost:** tagging and budgets in code; ephemeral environments; cleanup.
- **Operational complexity:** module versioning, upgrade of tooling, state
  hygiene, team ownership.
- **Testing:** static checks, policy tests, plan reviews, test deployments in a
  sandbox; contract tests for module interfaces.
- **Distinguish three activities:** (1) *documenting an infrastructure design*
  (diagrams and ADRs, this module's main output), (2) *writing IaC definitions*
  (code that could create it), (3) *deploying and operating* (running pipelines,
  handling incidents, paying bills). Each has different skills, risks and
  evidence. This module requires (1), uses small examples of (2) and does not
  require (3).
- **Document** the environment and promotion strategy in an ADR.

#### 5.8.7 Industry application and hands-on exercises

| | Exercise A — Environment and promotion design | Exercise B — IaC plan and drift policy |
| --- | --- | --- |
| Scenario | Northbridge platform team supports 25 teams | Production incidents trace to manual changes |
| Problem | Define environments and how changes reach production | Define what is code, how drift is detected and handled |
| Inputs | Tenant model (2D.7), compliance needs | Component inventory |
| Tasks | Define environments, isolation, data policy, promotion gates, approvals, rollback | List resources to be code; module boundaries; state layout; secrets; policy checks; drift detection and response; write short pseudocode for one module |
| Deliverables | Environment and promotion workflow diagram | IaC plan with module/state layout and policy list |
| Validation | Every production change has a review and an audit trail; non-production data policy defined | Every resource category has a owner; drift response defined; no secrets in code |
| Demonstrates | You can design change control | You can plan IaC |

#### 5.8.8 Real-world scenarios and architecture trade-offs

| Scenario | Business context | Constraints | Options | Pros / cons | Risks | Recommended (assumptions) | Would change if |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Emergency manual fix | Outage at night | Manual console fix possible | (a) Allow and reconcile later; (b) forbid; (c) break-glass with mandatory code follow-up | (a) fast, drift; (b) slow; (c) controlled | Never reconciled | (c) with tracked follow-up | Regulation forbids manual access |
| One state vs many | 25 teams | Parallel work | (a) Single state; (b) per-domain states | (a) simple, contention and blast radius; (b) isolated, more coordination | Cross-state dependencies | (b) | Very small team |

#### 5.8.9 Expected deliverables

- Environment strategy and promotion workflow diagram.
- IaC plan (scope, modules, state layout, secrets, policy, drift).
- Short pseudocode example for one module.
- Rollback and recovery notes.
- ADR on environment strategy.

#### 5.8.10 Common mistakes and misconceptions

| Mistake | Why problematic | How to avoid |
| --- | --- | --- |
| Secrets in code or state | Leakage | Secrets manager; protect state |
| One giant state | Large blast radius, lock contention | Split by domain and lifecycle |
| Treating IaC as documentation only | Drifts from reality | Apply through pipelines |
| Assuming rollback undoes data changes | Data loss | Plan data-aware rollback |
| Equating a diagram with deployed infrastructure | False confidence | Distinguish design, code and operation |

#### 5.8.11 Mastery criteria

- Explain declarative vs imperative and state/drift.
- Design a promotion workflow with gates, secrets and rollback.
- State what is evidence of design, of code, and of deployment.

#### 5.8.12 Completion gate

- [ ] Workflow, IaC plan and pseudocode reviewed.
- [ ] Break-glass and drift handling documented.
- [ ] You can explain why this module does not require deployment.
- [ ] Weaknesses (secrets handling, state design) addressed by redoing that part.

---

## 6. Topic-specific learning requirements

These distinctive questions supplement Section 5.

| Topic | Distinctive learning question | How to check |
| --- | --- | --- |
| 01 Principles | What does the cloud change about responsibility, resilience and cost, and what remains my architecture? | Responsibility table plus failure-domain diagram |
| 02 AWS | Which service supplies each logical capability, and what constraints does the pattern create? | Capability map with verification items; traced flow |
| 03 Azure | How does the same logical platform look on Azure, and where do semantics genuinely differ? | Map plus differences-to-research list |
| 04 GCP | What does the serverless, location-centred model change, and what does it mean for portability? | Map plus portability assessment |
| 05 Networking and identity | Can it reach it, and may it? | Five-layer access-path table for each flow |
| 06 Hybrid | Which connectivity pattern fits these volumes, latencies and risks, and what fails? | Option comparison with arithmetic; failure matrix |
| 07 Portability | At which layers do I accept coupling, and what would leaving cost? | Per-layer assessment with exit-cost ranges |
| 08 IaC | How do changes reach production repeatably, reviewably and recoverably? | Promotion workflow and drift policy |

---

## 7. Cross-cloud comparison and architectural integration

### 7.1 AWS, Azure and GCP comparison framework

The comparison is **capability-first**. Service names fill cells; they never
define rows. Service entries must come from the topic files (once written) or be
marked as a research item. **Do not claim equivalence.**

| Dimension | Logical capability being compared | How to identify provider services | Differences to investigate | Requirements that influence the decision | How to document fairly |
| --- | --- | --- | --- | --- | --- |
| Ingestion and integration | Batch, CDC and streaming ingestion | Topic 2–4 capability maps | Supported sources, CDC fidelity, ordering and delivery guarantees, throughput limits | Freshness, source types, volume | Same source scenarios for all three; note unsupported cases |
| Storage | Durable object store and tiers | Capability maps | Consistency behaviour, tiering, minimum durations, request limits | Retention, residency, cost | Same data profile; same retention |
| Processing and transformation | Batch/stream compute; SQL engines | Capability maps | Execution model, scaling, language support, billing unit | Workload mix, skills | Same workloads; ranges for cost |
| Orchestration | Scheduling and dependencies | Capability maps | Managed vs bundled, integrations, SLAs | Complexity, team skills | Same pipeline example |
| Cataloguing and metadata | Catalogue/metastore, lineage | Capability maps | Open interfaces, lineage coverage, tag/classification model | Governance, interoperability | Same metadata requirements (2D.7 Topic 5) |
| Governance and access control | Policies, fine-grained access, audit | Capability maps | Column/row controls, policy propagation, direct-storage bypass | Regulatory needs | Same access scenarios |
| Networking and private connectivity | Private access to services | Topic 5 | Private access mechanism, DNS behaviour, network object scope | Privacy, residency | Same flows traced |
| Hybrid integration | Connectivity to on-premises | Topic 6 | Connection options, routing features, resilience options | Volume, latency, availability | Same link requirements |
| Infrastructure automation | IaC and policy tooling | Topic 8 | Native tooling vs neutral tooling, policy features | Governance, skills | Same environment strategy |
| Reliability and DR | Redundancy, cross-region options | Topic 1 + provider topics | Failure domains, replication options, recovery behaviours | RTO/RPO | Same recovery objectives |
| Cost and operational complexity | Total cost and effort | All | Pricing units, free tiers, commitments, support | Budget, skills | Same workload profile, ranges, assumed prices labelled |
| Portability and dependencies | Exit cost, openness | Topic 7 | Open formats, proprietary features | Exit and concentration requirements | Dependency inventory per provider |

**Fair comparison rules.** (1) Fix requirements and criteria **before** looking
at providers. (2) Apply the same workload scenarios to each. (3) Record
unknowns as "research item", not as guesses. (4) Date every claim and cite the
documentation consulted. (5) Include a "no provider is clearly best" outcome as
legitimate.

### 7.2 Logical capabilities versus provider implementations

Produce four artefacts, in order:

1. **Logical architecture** — capabilities, responsibilities, interfaces, flows,
   no vendor names (builds on 2D.7).
2. **Provider mapping** — one column per provider: service chosen for each
   capability, with verification items.
3. **Decision record** — why those services were chosen (criteria, alternatives,
   trade-offs; ADR form from 2D.2 Topic 7).
4. **Dependency inventory** — provider-specific features relied on, the lock-in
   each creates, mitigation and residual limitation.

If the logical architecture needs a change after mapping, change the logical
diagram first, then re-map. Never let a provider's service catalogue redefine the
requirement.

### 7.3 Hybrid and multi-cloud decision framework

| Option | Choose when… | Costs and risks | Evidence you need |
| --- | --- | --- | --- |
| **Single cloud** | Requirements are met by one provider; skills are concentrated; speed matters | Provider dependence; concentration risk | Fit to requirements; documented exit plan |
| **Hybrid** | Systems cannot move yet (latency, regulation, cost, risk) | Connectivity and two operating models | Requirement for on-premises; volumes; migration plan |
| **Multiple clouds for distinct workloads** | A specific workload needs a service or location another provider offers; or acquisitions | Data movement, duplicated skills and governance | Workload-specific justification; boundary of data movement |
| **Distributed multi-cloud** (the same workload spans clouds) | Regulation or business continuity requires it and cannot be met otherwise | Highest complexity and cost | Mandate, tested failover, cost model |

Decision questions: What requirement forces more than one environment? Can an
open data layer plus exit plan meet the concern? Who will operate it, and with
what skills? What does inter-cloud transfer cost and add in latency? Hybrid and
multi-cloud introduce additional complexity and must be justified by explicit
requirements.

### 7.4 Integrated architecture exercise (connects Topics 1, 2–4, 5, 6, 7 and 8)

**Scenario (illustrative).** Northbridge Bank will place its analytics platform
in one public cloud, keeping the core ledger on premises for three years. The
board wants an exit plan, and a regulator expects private access to customer
data.

**Tasks.**

1. Using Topic 1 principles, state the criteria and residency rules.
2. Draw the logical architecture and map it to **two** providers (choose any
   two of AWS, Azure, GCP) using the capability-first framework (Topics 2–4).
3. Define the network and identity boundaries and the private access path to
   the lake (Topic 5).
4. Design the connectivity from the on-premises ledger and compute the transfer
   time for an initial 20 TB load over an assumed 1 Gbps link at 70% efficiency
   (Topic 6): `20×10¹²×8 / (10⁹×0.7) ≈ 228,571 s ≈ 2.6 days`.
5. Produce a per-layer portability assessment and an exit-plan outline
   (Topic 7).
6. Define environments, promotion and drift handling (Topic 8).

**Deliverables.** A 3–4 page design note with the four artefacts of Section 7.2
(for two providers), the connectivity design, and one ADR on single cloud vs
multi-cloud.

**Completion criteria.** Mappings carry verification items; reachability and
permission are separate; transfer arithmetic has units and assumptions; the
exit plan has steps and an owner; a reviewer can follow one record from the
on-premises ledger to a dashboard.

### 7.5 Architecture decision questions

These are original supplementary questions, **not** questions from
`practice-questions.md`.

1. Which requirements justify using a provider-specific managed service rather
   than an open-source alternative, and what is the exit cost you accept?
2. Which capabilities must remain portable (data? table format? orchestration?),
   and which may be coupled?
3. How should on-premises systems connect securely to the platform, and what
   happens during a link failure?
4. Which responsibilities belong to network controls and which to identity
   controls? Give a case where each alone is insufficient.
5. When is hybrid connectivity preferable to moving every workload to the cloud?
6. What additional costs and operational risks arise from multi-cloud, and how
   would you quantify them?
7. How should infrastructure changes be reviewed and promoted between
   environments, and who may bypass the process in an emergency?
8. Your regulator requires data to stay in-country. Which provider capabilities
   (regions, replication settings, support access) must you verify?
9. Which comparison dimensions are you unable to complete from the topic files
   alone, and what research will you do?

---

## 8. Practice questions and knowledge validation

### 8.1 Source status

[`practice-questions.md`](practice-questions.md) is currently **empty**. This
roadmap does not assume any question numbers, sections or categories exist and
does not modify the file. The method below is a **proposed study method** for use
once the file is populated.

### 8.2 When to attempt the questions

| When | What | Purpose |
| --- | --- | --- |
| After each topic | Questions relating to that topic, closed-book | Check against the topic gate |
| After Topics 2–4 | Mixed provider-comparison questions | Test capability-first thinking |
| After Topics 5–6 | Networking, identity and hybrid questions | Test layered access reasoning |
| After Topics 7–8 | Portability and IaC questions | Test decision reasoning |
| Before the project | The full set | Readiness check |
| After the project | Re-attempt missed questions | Close gaps |

### 8.3 Using incorrect answers

1. Mark each answer correct / partly correct / wrong with a one-sentence reason.
2. Map each wrong answer to its topic and revisit the corresponding source file
   and roadmap section (Section 6 table).
3. Keep a **gap log**: question, topic, misconception, remedial exercise,
   re-attempt date.
4. Re-attempt after several days; two consecutive failures mean redoing the topic
   exercise.

### 8.4 Expected reinforcement map (recommended)

| Question area | Revisit |
| --- | --- |
| Principles, responsibility, regions | `01-cloud-data-architecture-principles.md` |
| AWS patterns | `02-aws-data-architecture-reference-patterns.md` |
| Azure patterns | `03-azure-data-architecture-reference-patterns.md` |
| GCP patterns | `04-gcp-data-architecture-reference-patterns.md` |
| Network, DNS, identity, private access | `05-networking-identity-and-private-connectivity.md` |
| VPN, dedicated links, on-premises | `06-hybrid-connectivity-and-on-premises-integration.md` |
| Lock-in, portability, egress, multi-cloud | `07-portability-lock-in-and-multi-cloud-trade-offs.md` |
| IaC, environments, drift | `08-infrastructure-as-code-and-environment-strategy.md` |
| Integrated cases | Section 7 and the project |

### 8.5 Readiness for the project

- [ ] All eight topic gates signed off.
- [ ] Average at least 85% correct on the full set (*recommended threshold*),
      with no topic below 70%.
- [ ] Integrated exercise (Section 7.4) completed.
- [ ] Gap log has no unresolved items older than one week.

### 8.6 Gaps in testing practical cloud decisions and supplementary exercises

Recall questions rarely test architecture decisions. Add these **supplementary
exercises** (recommendations):

1. Map a given logical architecture to a provider in 45 minutes, marking every
   unverified claim.
2. Given an access failure, name the layer (name, route, authn, authz, service
   rule) and the first check.
3. Compute transfer time and egress cost for a given migration and defend the
   chosen link.
4. Write an ADR choosing single cloud versus multi-cloud for a described bank.
5. Review a flawed IaC plan for secrets in code, giant state and missing drift
   handling.
6. Defend your design to a sceptical security lead and a sceptical finance lead.

---

## 9. Module completion assessment

### 9.1 Status definitions

| Status | Meaning |
| --- | --- |
| **Not started** | No work done on the item |
| **In progress** | Topic read and exercises started; gate not yet met |
| **Completed** | Gate met, deliverables reviewed by another person, practice questions answered with gaps closed |
| **Needs revision** | Gate attempted but a reviewer found a weakness, or later work exposed a contradiction; redo the specific exercise |

Reading a topic file alone is **not** evidence of mastery.

### 9.2 Per-topic checklist

| Topic | Status | Capability you can demonstrate | Evidence required |
| --- | --- | --- | --- |
| 01 Principles | ☐ | Explain shared responsibility, failure domains, cost drivers | Responsibility table, residency rules, criteria sheet, ADR |
| 02 AWS | ☐ | Map logical capabilities to AWS and evaluate a pattern | Capability map with verification items, traced flow, pattern ADR |
| 03 Azure | ☐ | Map to Azure and compare with AWS without assuming equivalence | Azure map, difference notes, identity/network path |
| 04 GCP | ☐ | Map to GCP; reason about provider-specific portability effects | GCP map, three-way table, portability notes |
| 05 Networking and identity | ☐ | Explain network, DNS, identity, private connectivity; separate reachability and permission | Boundary diagram, address plan, access-path table, troubleshooting matrix |
| 06 Hybrid | ☐ | Design hybrid connectivity at concept level | Option comparison with arithmetic, design diagram, failure matrix |
| 07 Portability | ☐ | Evaluate lock-in and justify single/hybrid/multi-cloud | Per-layer assessment, exit-cost ranges, decision record |
| 08 IaC | ☐ | Explain IaC and promotion; separate design, code and operation | Workflow diagram, IaC plan, pseudocode, ADR |

### 9.3 Module-level checklist

- [ ] All eight topics **Completed**.
- [ ] Can map logical platform capabilities to services on at least two
      providers, with verification items.
- [ ] Can compare AWS, Azure and GCP reference patterns with consistent criteria.
- [ ] Can explain networking, identity and private connectivity with the five-
      layer model.
- [ ] Can design hybrid connectivity at concept level with arithmetic.
- [ ] Can evaluate portability and justify single-cloud, hybrid or multi-cloud.
- [ ] Can explain IaC and environment promotion.
- [ ] Has produced architecture documentation and at least five ADRs.
- [ ] Final project **Completed** and defended (Section 10.8).
- [ ] No topic in **Needs revision**.

---

## 10. Final project — Cloud platform architecture comparison

Project file:
[`Projects/08-cloud-platform-architecture-comparison.md`](Projects/08-cloud-platform-architecture-comparison.md)
and its index [`Projects/README.md`](Projects/README.md).

> **Source status.** Both project files are currently **empty**. There is no
> existing specification to preserve. This section therefore proposes a project
> shape consistent with the file name. Everything in it (scenario, steps,
> deliverables, templates) is a **recommendation**. If the project file is later
> written with different requirements, **its content governs** and this guide
> should be adjusted to it. This section does not replace the project's real
> instructions and does not make the proposed deliverables mandatory.

### 10.1 Project overview

- **Objective (proposed):** compare AWS, Azure and GCP realisations of one
  logical enterprise data platform, and produce a defensible, documented
  recommendation including networking, identity, hybrid connectivity,
  portability and infrastructure strategy.
- **Problem addressed:** an organisation must choose where and how to host its
  data platform without being led by familiarity, marketing or service names.
- **Skills validated:** capability-first mapping, consistent comparison, secure
  connectivity design, hybrid reasoning, portability and cost reasoning, decision
  documentation.
- **Use of the eight topics:** 1 → criteria; 2–4 → provider mappings; 5 →
  network and identity; 6 → hybrid; 7 → portability and multi-cloud; 8 →
  infrastructure and environments.
- **Expected final deliverables:** to be taken from the project file when
  populated; a recommended set is in 10.5.

### 10.2 Project scenario and requirements

**Scenario (proposed assumption; not from the project file).** *Northbridge
Bank* is a fictional mid-sized bank. It will host a new enterprise analytics
and ML data platform in public cloud. The core ledger and cards platform remain
on premises for at least three years. Personal data must stay in a stated
jurisdiction. The board requests a documented exit plan.

| Assumption (all illustrative) | Value |
| --- | --- |
| Data volume today / growth | ~250 TB / +30% per year |
| Daily on-premises change volume to cloud | ~2 TB/day |
| Initial historical load | ~20 TB |
| Workloads | BI/regulatory reporting, ML training, near-real-time fraud features (≤ 60 s p95) |
| Availability target (curated tables, business hours) | 99.5% monthly |
| Regulated data share | ~30% by volume |
| Teams | ~25 across 6 domains |
| Constraints | In-country data; no stored long-lived keys; private access to regulated data; existing corporate identity provider; no mandatory paid cloud deployment for this exercise |

If you use your own scenario, label observed facts versus assumptions.

### 10.3 Prerequisites

- [ ] All eight topic gates signed off.
- [ ] Integrated exercise (Section 7.4) completed.
- [ ] Practice-question readiness met (Section 8.5).
- [ ] Prerequisites P1–P9 solid (Section 3).
- [ ] The three provider topics reviewed for the comparison framework.

### 10.4 Step-by-step project execution

A proposed workflow; adapt to the real project file when populated. For each
step: **purpose, tasks, output, check**.

| Step | Purpose | Tasks | Output | Check |
| --- | --- | --- | --- | --- |
| 1 — Understand the problem and requirements | Know what must be satisfied | Business goals, workloads, functional and non-functional requirements, constraints, assumptions, dependencies, risks; **fix comparison criteria and weights now** | Requirements and constraints register; criteria sheet | Requirements measurable; criteria dated before provider work |
| 2 — Identify logical capabilities | Vendor-neutral scope | Ingestion, storage, processing, governance, metadata, consumption; required vs optional | Capability inventory | Two-way trace to requirements |
| 3 — Baseline logical architecture | Provider-independent design | Components, responsibilities, interfaces, flows, trust boundaries, operational responsibilities | Logical architecture diagram | No vendor names |
| 4 — Map to AWS | First realisation | Topic 2 patterns; capability → service; reasoning; assumptions and limits; verification items | AWS mapping and diagram | Every capability mapped or "gap"; claims verified or flagged |
| 5 — Map to Azure | Second realisation | Topic 3 patterns; same capabilities; differences | Azure mapping and diagram | Same capability list as AWS |
| 6 — Map to GCP | Third realisation | Topic 4 patterns; same capabilities; differences | GCP mapping and diagram | Same capability list |
| 7 — Compare consistently | Fair evaluation | Apply identical requirements and criteria; functional fit, operations, security, reliability, scalability, cost ranges; dependencies | Cross-cloud comparison matrix | Evidence per cell; unknowns are research items; no assumed equivalence |
| 8 — Networking and identity boundaries | Secure connectivity | Users, applications, services, external systems; network boundaries; identity types; least privilege; private access | Network and identity diagram; access-path table | Reachability and permission separate; no long-lived keys |
| 9 — Hybrid and on-premises integration | Connect the ledger | Systems remaining on premises; data movement; latency, bandwidth; reliability; compare options; transfer-time arithmetic | Hybrid integration design and comparison | Arithmetic with units and assumptions; failure handling |
| 10 — Portability and multi-cloud | Judge coupling | Data/code/metadata/operations portability; dependency inventory; egress and complexity; decide on multi-cloud | Portability and lock-in assessment; multi-cloud decision | Per-layer; exit cost as ranges; justified by requirements |
| 11 — Infrastructure and environment strategy | Repeatable change | Environments; what is code; review, promotion, configuration, drift; no deployment assumed | Infrastructure and environment strategy | Design/code/operation distinguished |
| 12 — Document decisions and trade-offs | Defensibility | Major choices linked to requirements; alternatives and rejections; assumptions, risks, limits | ADRs and risk register | Rejected alternatives have specific reasons |
| 13 — Consolidate the comparison | Package | Assemble mappings, diagrams, matrix, connectivity, portability, ADRs; consistency check; preferred option **only if the evidence supports it** | Comparison package; recommendation (or "no clear winner" with conditions) | Same criteria and requirements applied to all three |
| 14 — Validate and review | Verify and learn | Requirement coverage; security and connectivity assumptions; portability claims; cost and operations assumptions; unresolved questions | Validation report; review notes | Gaps logged; reviewer objections answered |

### 10.5 Project deliverables

Required deliverables are those in the project file once it is populated.
The following are **recommended**; keep them proportionate and avoid
duplication.

| # | Deliverable | Contents | Why needed | Supporting topics | How to validate |
| --- | --- | --- | --- | --- | --- |
| D1 | Requirements, constraints and assumptions register | IDs, measures, sources, confidence | Traceability | 1 | Measurable, sourced |
| D2 | Logical capability map and logical architecture | Capabilities, flows, boundaries | Provider-neutral baseline | 1, (2D.7) | No vendor names |
| D3 | Three provider-specific architecture diagrams | One per provider | Concrete realisations | 2, 3, 4 | Same capabilities mapped; verification items |
| D4 | Cross-cloud comparison matrix | Criteria, evidence, ratings, research items | Fair comparison | 1–4 | Criteria fixed first; no unsupported equivalence |
| D5 | Network and identity diagram with access-path table | Boundaries, identities, private access | Security | 5 | Five-layer check per path |
| D6 | Hybrid integration design | Connectivity options, chosen pattern, routing/DNS, failure matrix | On-premises integration | 6 | Arithmetic and failures covered |
| D7 | Portability and lock-in assessment | Per-layer dependencies, mitigations, exit-cost ranges | Exit and concentration risk | 7 | Residual limitations stated |
| D8 | Infrastructure and environment strategy | Environments, IaC plan, promotion, drift | Repeatability | 8 | Design/code/operation distinguished |
| D9 | Architecture decision records | ADRs for major choices | Defensibility | All | Alternatives and revisit triggers |
| D10 | Risk register | Risks, mitigations, owners | Honesty | All | Linked to findings |
| D11 | Final recommendation and limitations | One to two pages | Decision readout | All | Non-specialist can follow in ten minutes |

### 10.6 Suggested templates

**Requirements and constraints**

| ID | Requirement | Priority | Constraint or assumption | Validation method |
|---|---|---|---|---|
| R-01 | Regulated data remain in the stated jurisdiction, including replicas and backups | Must | Assumes in-country regions exist at each provider (verify) | Region and replication inspection per provider |

**Cloud capability mapping**

| Logical capability | AWS implementation | Azure implementation | GCP implementation | Key differences |
|---|---|---|---|---|
| Durable object storage | (from Topic 2; verify) | (from Topic 3; verify) | (from Topic 4; verify) | Research items: consistency, tiers, limits |

**Architecture decision record**

| Field | Description |
|---|---|
| Decision | The architectural choice |
| Context | The requirement or problem |
| Alternatives | Options considered |
| Rationale | Why the chosen option fits |
| Trade-offs | Benefits and limitations |
| Risks | Known risks and mitigations |

**Portability assessment**

| Component or capability | Provider dependency | Portability concern | Mitigation | Residual limitation |
|---|---|---|---|---|
| Analytical warehouse SQL | Provider-specific SQL extensions | Rewrite cost at exit | Keep curated data in open table format; limit use of extensions | Query rewrite still needed |

**Access-path table (recommended addition)**

| Path | Name resolution | Network route | Authentication | Authorisation | Service-side network rule | Evidence |
|---|---|---|---|---|---|---|

**Comparison scoring (if used)**

| Criterion | Weight (basis) | AWS | Azure | GCP | Evidence / research item |
|---|---|---|---|---|---|

Scores are decision support, not objective truth; document sensitivity and ties.

These are suggested templates, not replacements for templates explicitly
required by the project file.

### 10.7 Project validation checklist

Apply the items that match the (eventual) real project requirements.

- [ ] **Requirements traceability:** every decision traces to requirements and
      vice versa.
- [ ] **Logical architecture completeness:** all capability families present,
      vendor-neutral.
- [ ] **AWS mapping accuracy:** every service claim verified against current
      documentation or marked as a research item.
- [ ] **Azure mapping accuracy:** same.
- [ ] **GCP mapping accuracy:** same.
- [ ] **Fairness and consistency of the comparison:** same requirements,
      scenarios, criteria and evidence standard for all three; criteria fixed
      before scoring.
- [ ] **Networking and identity boundaries:** every path has name, route, authn,
      authz and service rule; reachability and permission separated.
- [ ] **Hybrid assumptions:** bandwidth, latency, efficiency and ownership
      stated; arithmetic reproducible.
- [ ] **Portability and lock-in:** per-layer; exit costs as ranges; mitigations
      with residual limits.
- [ ] **Infrastructure and environment strategy:** design vs code vs operation
      distinguished; secrets and drift addressed.
- [ ] **Cost and operational trade-offs:** assumed prices labelled; people
      included.
- [ ] **Documentation consistency:** names, IDs and numbers agree across
      artefacts.
- [ ] **Decision rationale:** rejected alternatives with specific reasons.
- [ ] **Known limitations and unresolved risks:** listed with owners.

### 10.8 Project completion gate

The project is complete only when **all** hold:

- [ ] Deliverables required by the project file (or D1–D11 if none are specified)
      exist, are version-dated and use consistent identifiers.
- [ ] You can explain the purpose and structure of each proposed architecture.
- [ ] Three major decisions trace to requirements and ADRs with rejected
      alternatives; three requirements trace forward to decisions.
- [ ] The comparison applies identical criteria to all three providers and marks
      unknowns as research items.
- [ ] Security and connectivity boundaries are explained with the five-layer
      model; no path relies on network location alone.
- [ ] Portability and multi-cloud decisions are justified by requirement
      evidence and cost ranges.
- [ ] Limitations and risks are listed; the recommendation states what would
      change it (including "no clear winner" if that is the honest outcome).
- [ ] You have defended the recommendation against at least five reviewer
      questions (for example from Section 7.5) using recorded evidence.
- [ ] A reviewer who did not do the work agrees the evidence supports the
      conclusions.
- [ ] No step requires paid cloud deployment.

Producing diagrams and documents alone is **not** sufficient.

### 10.9 Connection to later modules

| Later module (actual directory) | How the project prepares you | What belongs to that module |
| --- | --- | --- |
| `../09-Streaming-and-Real-Time-Data-Architecture/` | Provider streaming mappings, networking for streams, fraud freshness requirement | Stream-processing design, state, delivery semantics, serving stores |
| `../10-Data-Governance-Security-Privacy-and-Compliance/` | Identity, private access, residency rules, key custody, policy-as-code | Governance operating model, controls, evidence design |
| `../11-Metadata-Lineage-Quality-and-Master-Data/` | Provider catalogue/metadata mappings, classification | Lineage tooling, quality services, master data |
| `../12-Reliability-Resilience-and-Disaster-Recovery/` | Failure domains, cross-region choices, rebuild-from-code | DR strategies, drills, backup and restore validation |
| `../13-Performance-Scalability-and-Cost-Architecture/` | Cost ranges, pricing models, egress arithmetic | Capacity validation, FinOps, performance engineering |
| `../14-Data-Access-Serving-Semantic-and-AI-Data-Architecture/` | Provider analytics and ML services, private access to data for AI | Serving architectures, semantic layers, feature and retrieval design |

Do not add requirements to those modules beyond what their own files specify.

---

## 11. Where this module leads

Module 2D.9, **Streaming and Real-Time Data Architecture**, takes the platform,
connectivity and provider mappings produced here and designs real-time data
paths in depth: latency budgets, event brokers and partitions, event-time
processing and watermarks, stream state and delivery semantics, CDC backbones,
real-time serving stores and failure modes.
