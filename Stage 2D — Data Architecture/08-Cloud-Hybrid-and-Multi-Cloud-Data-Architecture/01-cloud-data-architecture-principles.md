# Cloud Data Architecture Principles

> **Stage:** 2D — Data Architecture  
> **Module:** 08 — Cloud, Hybrid and Multi-Cloud Data Architecture  
> **Lesson:** 01 — Cloud Data Architecture Principles  
> **Level:** Beginner → Intermediate → Advanced  
> **Estimated effort:** 6–8 hours (recommended, not a repository requirement)  
> **Primary scenario:** Northbridge Bank, a fictional mid-sized bank  
> **Source of scope:** `roadmap-Cloud-Hybrid-and-Multi-Cloud-Data-Architecture.md`, Topic 5.1  
> **Status note:** The roadmap describes recommended learning scope; the source lesson file was a planned file, not an existing body of content. This lesson implements the roadmap's recommendations and does not claim they were previously documented requirements.

---

## 1. Purpose and learning outcomes

Cloud data architecture is the design of how an organisation acquires, stores, transforms, governs, secures, and serves data using cloud services and infrastructure, while meeting business, regulatory, security, reliability, cost, and operational constraints.

A cloud provider offers individual services. **Architecture is the reasoned design of the whole system**: the capabilities required, how components connect, which identities can access them, where data may reside, what happens during failure, how the system is operated, and why the chosen trade-offs are acceptable.

By the end of this lesson, you should be able to:

1. Define IaaS, PaaS, SaaS and public, private, hybrid, and multi-cloud deployment models.
2. Explain shared responsibility for infrastructure, configuration, identity, data, networks, and encryption keys.
3. Distinguish scalability, elasticity, availability, resilience, and disaster recovery.
4. Explain regions, availability zones, failure domains, data residency, and replication implications.
5. Map cloud capabilities to a data platform without confusing a service catalogue with an architecture.
6. Identify cost drivers and propose cost-control measures without inventing prices.
7. Assign operational ownership for monitoring, incident response, recovery, and managed-service configuration.
8. Evaluate security, reliability, cost, skills, maintainability, and portability trade-offs.
9. Create principles, weighted decision criteria, and an Architecture Decision Record (ADR).

### Prerequisite check

This lesson assumes you have a basic understanding of data-platform capabilities, data classification, measurable quality attributes, storage, ingestion, and architecture trade-offs. These ideas are covered earlier in Stage 2D, especially the enterprise data-platform and lakehouse module.

If the following are unclear, pause and review them before proceeding:

- Logical architecture versus physical implementation.
- Data classification and data ownership.
- Availability, freshness, latency, and recovery objectives.
- Object storage, database/warehouse, and processing responsibilities.
- Constraints, assumptions, dependencies, risks, and ADRs.

The module roadmap names P1–P4 and P9 as direct prerequisites for this topic. Use these Stage 2D lessons for remediation when needed:

- [Architecture principles and quality attributes](../01-Data-Architecture-Foundations-and-Principles/04-architecture-principles-and-quality-attributes.md) and [data architecture lifecycle and governance](../01-Data-Architecture-Foundations-and-Principles/05-data-architecture-lifecycle-and-governance.md) — P1.
- [Latency, throughput, freshness and availability targets](../02-Requirements-Constraints-and-Architecture-Decisions/04-latency-throughput-freshness-and-availability-targets.md) — P2.
- [Constraints, assumptions, dependencies and risks](../02-Requirements-Constraints-and-Architecture-Decisions/05-constraints-assumptions-dependencies-and-risks.md) — P3.
- [Architecture trade-offs and decision criteria](../02-Requirements-Constraints-and-Architecture-Decisions/06-architecture-trade-offs-and-decision-criteria.md) and [architecture decision records](../02-Requirements-Constraints-and-Architecture-Decisions/07-architecture-decision-records-adrs.md) — P4.
- [Platform capabilities and logical reference architecture](../07-Enterprise-Data-Platform-and-Lakehouse-Architecture/01-platform-capabilities-and-logical-reference-architecture.md), [compute, storage and control-plane separation](../07-Enterprise-Data-Platform-and-Lakehouse-Architecture/04-compute-storage-and-control-plane-separation.md), and [multi-team isolation and tenant boundaries](../07-Enterprise-Data-Platform-and-Lakehouse-Architecture/07-multi-team-isolation-and-tenant-boundaries.md) — P9.
- The roadmap also marks P7 (object storage, formats, replication and lifecycle) as essential to beginning the module; review [object storage and file-format selection](../05-Database-and-Storage-Architecture/03-object-storage-and-file-format-selection.md) if those concepts are weak.

---

## 2. Beginner level — establish the vocabulary

### 2.1 Service model versus deployment model

A **service model** describes how much of the technology stack the provider operates. A **deployment model** describes where and across how many environments the workload runs. They answer different questions and can be combined.

| Model | Meaning | Customer typically manages | Typical fit | Main trade-off |
|---|---|---|---|---|
| **IaaS** — Infrastructure as a Service | Provider offers virtual compute, storage, and networking primitives | OS, patching inside guest OS, runtime, applications, data, identity and network configuration | Custom software, migration of legacy workloads, special OS/runtime needs | High control, high operational burden |
| **PaaS** — Platform as a Service | Provider operates more of the runtime/platform; customer deploys code or data workloads | Data, access, configuration, code, workload logic, service-specific controls | Managed databases, managed processing, application platforms | Less infrastructure work, more service-specific dependence |
| **SaaS** — Software as a Service | Finished application delivered to users | Users, access, configuration, data governance, retention and use of the application | Business applications such as CRM or collaboration tools | Lowest infrastructure burden, least control over implementation |

These categories are useful mental models, not perfect labels for every product. A cloud service may combine characteristics, and responsibility varies by the specific service and configuration.

**Analogy:** IaaS is like renting a mostly empty workshop: you manage more of the equipment and maintenance. PaaS is like using a managed workshop where core equipment is maintained for you. SaaS is like using a finished service. The analogy is only a memory aid; always verify the actual responsibility matrix.

| Deployment model | Meaning | Why choose it? | Cost or risk to consider |
|---|---|---|---|
| **Public cloud** | Services run on a provider-operated cloud platform and are consumed by customers over provider-supported access paths | Elastic capacity, managed capabilities, broad ecosystem | Provider dependence, configuration risk, consumption-based spend |
| **Private cloud** | Cloud-like infrastructure dedicated to one organisation, operated by that organisation or a service provider | Specific control, isolation, or organisational requirements | Capital/operational cost and responsibility remain substantial |
| **Hybrid cloud** | Workloads or data span cloud and on-premises/private environments | Legacy dependencies, latency, migration sequencing, constraints | Network dependency, duplicated operations, integration complexity |
| **Multi-cloud** | Workloads use two or more public cloud providers | Acquisitions, distinct workload fit, explicit resilience or negotiation requirements | Skills, governance, observability, identity, and data-movement complexity |

**Important:** hybrid and multi-cloud are not automatically more resilient. They increase the number of components and failure modes. Adopt them when a concrete requirement outweighs the extra complexity.

#### Beginner practice — classify twelve abstract services

Classify each example as **primarily IaaS, PaaS, SaaS, or a deployment model/context**. Some offerings combine models, so explain your reasoning and list one customer responsibility that remains. The goal is to reason about the operating boundary, not memorise labels.

| Example | Suggested classification | What the customer still owns |
|---|---|---|
| 1. A virtual machine where your team installs and patches Linux | IaaS | Guest OS, patching, runtime, application, data, access |
| 2. A managed relational database service | PaaS-like managed data service | Schema, data, access policies, configuration, workload recovery requirements |
| 3. A hosted CRM application | SaaS | Users, access, data governance, retention and configuration |
| 4. An object storage service | Infrastructure/storage capability; exact classification varies by provider taxonomy | Data classification, access, retention, key choices and replication configuration |
| 5. A managed function runtime triggered by events | PaaS/FaaS-like | Function code, permissions, data handling, observability and failure behaviour |
| 6. A company-operated private cloud | Private-cloud deployment model | Depending on the operating contract, substantial platform, security and workload responsibilities |
| 7. A workload split between an on-premises data centre and a public cloud | Hybrid-cloud deployment model | Cross-boundary identity, network, data movement and operational coordination |
| 8. An analytics workload using two public cloud providers | Multi-cloud deployment model | Cross-cloud governance, identity, monitoring, skills, data movement and recovery |
| 9. A managed data warehouse with SQL access | PaaS-like managed analytics service | Data access, query/workload design, cost controls, governance and recovery requirements |
| 10. A self-managed Kafka cluster running on virtual machines | IaaS used to host self-managed software | OS, cluster upgrades, brokers, capacity, security, monitoring and recovery |
| 11. A hosted email and collaboration suite | SaaS | Identity, user lifecycle, sharing controls, retention and appropriate use |
| 12. A cloud provider's managed ETL/orchestration service | PaaS-like managed platform capability | Pipeline logic, secrets/identity, retries, data quality, alerting and business recovery objectives |

**Check your reasoning:** classifications describe the operating model, not the complete architecture. Object storage, for example, can be described as a storage infrastructure capability, while the provider may expose it as a fully managed service. Use the provider's service-specific responsibility documentation for implementation decisions.

### 2.2 Cloud service versus architecture

A service provides a capability; an architecture composes capabilities into a working system.

For example, object storage alone does not define:

- How data arrives and whether ingestion can be replayed.
- Which transformations validate and curate records.
- Where schemas and ownership metadata are recorded.
- Which identities may read raw versus curated data.
- How data quality failures are quarantined.
- Whether data are replicated and to which locations.
- How query workloads are isolated from ingestion.
- How spend, freshness, failures, and access are monitored.
- How the platform recovers after a regional outage.

Two teams can select the same products and still build systems with very different security, reliability, and costs.

### 2.3 Core terminology

| Term | Definition | Architectural question |
|---|---|---|
| **Region** | A geographic area containing a provider's cloud infrastructure | Does this location meet latency, service availability, legal, and recovery needs? |
| **Availability zone (AZ)** | An isolated location within a region; provider-specific implementation and terminology vary | Can the workload continue if one zone is impaired? |
| **Failure domain** | A set of components that may fail together due to a shared cause | What can a single event disable at once? |
| **Scalability** | Ability to handle increased load by adding or using more resources | Can the design meet forecast demand? |
| **Elasticity** | Ability to adjust resources to demand, including scaling down | Can capacity follow a burst without paying for it indefinitely? |
| **Availability** | Fraction of time a system provides its intended service | Does the service meet its availability objective? |
| **Resilience** | Ability to withstand, adapt to, and recover from disruption | How does the system behave during and after failure? |
| **Replication** | Maintaining copies of data or state in more than one location/system | What is copied, how quickly, and with what consistency? |
| **RTO** | Recovery Time Objective: target time to restore a service after disruption | How long can the business tolerate an outage? |
| **RPO** | Recovery Point Objective: maximum targeted data-loss window measured in time | How much recent data can the business tolerate losing? |
| **Egress** | Data transferred out of a provider or relevant network boundary | What is the cost of exporting, replicating, or serving data externally? |
| **Pay-as-you-go** | A consumption-based billing approach in which charges depend on measured usage under the service's pricing rules | Which usage dimensions are metered, and which fixed, minimum, tiered, or committed charges also apply? |
| **Managed service** | Service where the provider operates some underlying components | Which operational responsibilities remain with the customer? |

Do not use “high availability,” “resilient,” or “disaster recovery” as interchangeable terms. A system may be highly available during a zone failure but still have no tested recovery plan for losing its region.

---

## 3. Shared responsibility: managed does not mean responsibility-free

Cloud security and operations are shared. Providers generally protect the underlying cloud infrastructure; customers remain responsible for their data, identities, access policies, configuration, and use of the service. The exact division depends on the service model and product.

### 3.1 Responsibility matrix

This matrix is a starting point, not a contractual control assessment. Assign a named owner and verify the chosen service's documentation.

| Area | Provider responsibility commonly includes | Customer responsibility commonly includes |
|---|---|---|
| Physical facilities and hardware | Physical access, facility operations, underlying hardware | Understand provider assurance and service scope |
| Managed service software/platform | Operating the provider-managed platform components | Select/configure features; review service-specific controls |
| Guest OS and installed software on IaaS VMs | Physical host and virtualization layer | OS hardening, patching, runtime, application updates |
| Data | Durable service infrastructure and documented service controls | Classification, lawful use, retention, access, quality, backup requirements |
| Identity and access | Identity control mechanisms the service provides | User lifecycle, role design, least privilege, MFA, workload identities, access review |
| Network | Underlying provider network | Network boundaries, routing, exposure, private connectivity, firewall rules where configurable |
| Encryption and keys | Service encryption features and managed key infrastructure as documented | Choose appropriate key model, policies, permissions, rotation requirements, and audit |
| Monitoring and incidents | Provider service-health information and incident communications | Workload-level telemetry, alerting, runbooks, escalation, customer communications |
| Recovery | Service-level durability/availability features as documented | Define RTO/RPO, configure replication/backups, test restoration, validate application recovery |

**Security principle:** reachability is not permission, and permission is not proof of appropriate use. A network path may exist while IAM denies access; a valid identity may still be able to access data it should not see if policies are too broad.

### 3.2 A practical ownership method

For each critical control, document:

1. **Control objective:** e.g., only the fraud analytics role may read curated fraud data.
2. **Implementation:** identity policy, resource policy, network boundary, key policy, or application control.
3. **Owner:** named team or role accountable for configuration.
4. **Evidence:** policy review, audit log, test result, configuration export, or monitoring signal.
5. **Failure response:** who is paged, what is disabled, and how access is restored safely.

Avoid vague owners such as “cloud team.” Name the team that can make the change and the team that verifies it.

### 3.3 Identity, data, and encryption keys

Identity and access management (IAM) decides **who or what can perform which action on which resource**. Use separate human and workload identities, least privilege, time-bounded elevation where appropriate, and regular access reviews.

Encryption at rest and in transit are important controls, but encryption does not compensate for excessive access. If an identity is authorised to decrypt and read data, encryption may not prevent that identity from misusing it.

Customer-managed keys can provide additional control over key policy and lifecycle, but also introduce operational obligations: key availability, permissions, rotation policy, recovery, and the consequences of disabling or deleting a key. Do not select a key model solely because it sounds more secure; map it to a threat model and recovery plan.

---

## 4. Regions, zones, resilience, and residency

### 4.1 How to reason about locations

A region is not simply a billing choice. It can affect latency, service availability, data location, legal constraints, operational support, replication options, and disaster recovery.

A zone is intended to provide isolation within a region, but it is not a guarantee that every dependency is zone-independent. The precise topology and available resilience options vary by provider and service. Confirm current documentation for each service rather than assuming a generic cloud property applies universally.

```text
                 One cloud region
  +---------------------------------------------------+
  |                                                   |
  |  Zone A              Zone B             Zone C    |
  | +----------+       +----------+       +----------+|
  | | Compute  |       | Compute  |       | Compute  ||
  | | Storage* |       | Storage* |       | Storage* ||
  | +----------+       +----------+       +----------+|
  |       \                 |                 /       |
  |        +------ regional services --------+        |
  |                  may be shared                    |
  +---------------------------------------------------+

  *Only if the selected service and configuration support it.
  A multi-zone diagram does not prove every component is redundant.
```

A **regional failure** may affect all zones and shared regional services. Cross-region recovery is a separate design that may require replication, access policies, metadata, keys, network paths, orchestration, and tested failover procedures.

### 4.2 Availability arithmetic: useful but idealised

For two redundant components that are both capable of serving the request, with independent unavailability and correct failover, the idealised availability is:

\[
A_{\text{combined}} = 1 - (1-A_1)(1-A_2)
\]

If each component has availability \(A_1=A_2=0.999\) (99.9%):

\[
A_{\text{combined}} = 1 - (0.001)(0.001)
= 0.999999 = 99.9999\%
\]

This arithmetic assumes that either component can serve the workload, failures are independent, failover works, and no shared dependency is a single point of failure. It is **not** a prediction that a real cloud platform will achieve 99.9999% availability.

Examples of dependencies that break the simple independence assumption:

- Both zones rely on a shared regional control plane or configuration.
- Both paths use the same identity provider, DNS dependency, or network route.
- Replication is delayed or the secondary copy is unusable.
- Failover is manual, untested, or blocked by permissions.
- A common software defect or bad deployment affects both copies.
- Both replicas depend on the same key or metadata service.

For a production design, use the service's documented SLA/SLO terms and the architecture's actual dependency graph. Do not multiply advertised service SLAs as if they were independent probabilities unless the assumptions are justified.

### 4.3 Availability is not the same as recovery

| Mechanism | Helps with | Does not automatically solve |
|---|---|---|
| Multi-zone deployment | Some zone-level failures | Region loss, logical deletion, compromised credentials, bad deployments |
| Backup | Recovery from deletion/corruption when backups are isolated and restorable | Fast failover unless restore time meets RTO |
| Cross-region replication | Regional recovery and regional read access, depending on service | Accidental deletion or corruption if changes replicate; residency constraints |
| Point-in-time recovery | Some logical errors and data corruption within retained window | All region-wide incidents or indefinite history |
| Tested runbook and failover | Human and operational execution | Missing replicas, incorrect assumptions, untested dependencies |

Define recovery objectives before selecting mechanisms:

- **RTO:** maximum acceptable time to restore the service.
- **RPO:** maximum acceptable age of recovered data, expressed as a time window.

**Illustrative example:** If Northbridge requires an RPO of 15 minutes for curated analytics, a daily backup alone does not meet the objective. The team must evaluate a replication or recovery mechanism capable of meeting the target under realistic load and failure conditions, then test it.

### 4.4 Data residency and regional selection

**Data residency** concerns where data is stored or processed under applicable rules, contracts, and organisational policy. It is not the same as a general claim that a provider is “compliant.” Legal obligations depend on the data, organisation, jurisdiction, processing activity, contracts, and applicable law. Architecture teams should work with legal, privacy, compliance, and security owners rather than interpreting regulation alone.

Create a **data-location inventory** for each data class:

| Data asset | Classification | Permitted storage/processing locations | Replicas and backups | Access/support considerations | Owner |
|---|---|---|---|---|---|
| Customer identifiers | Sensitive personal data (illustrative) | Approved in-country regions only (assumption) | Must remain within approved boundary | Review admin access and audit | Data owner + compliance |
| Aggregated operational metrics | Internal (illustrative) | Approved regions; verify whether cross-border transfer is allowed | May be broader only after review | Prevent re-identification | Platform owner |
| Public reference data | Public | Broadly permitted, subject to licence | Broadly permitted | Licence and integrity | Data product owner |

Check more than the primary data store. Consider replicas, backups, logs, query results, temporary files, disaster-recovery copies, metadata, support access, and data exports. A region label alone is not evidence that every processing or access path meets the requirement.

### 4.5 Region-selection decision order

1. **Eliminate invalid options:** legal, residency, contractual, security, or service-availability constraints.
2. **Check resilience:** is there a viable second location if the RTO/RPO requires it?
3. **Evaluate latency and data gravity:** where are producers, consumers, and dependent systems?
4. **Estimate total cost:** compute, storage, requests, replication, egress, support, and operations.
5. **Evaluate skills and operations:** can the team monitor, recover, and secure the design?
6. **Document uncertainty:** list every capability or legal interpretation requiring confirmation.

Do not select a region only because it is geographically close or currently cheaper.

---

## 5. Cloud data-platform architecture: capabilities first

A data platform usually includes ingestion, storage, processing, governance, query/serving, and consumption capabilities. The cloud provider's services are implementation choices for those capabilities.

```text
Operational databases / files / applications / events
                         |
                         v
                [Ingestion & CDC]
                         |
                         v
              [Landing / raw storage]
                         |
                         v
            [Validation & processing]
                         |
                         v
              [Curated / trusted data]
                  |              |
                  v              v
          [Warehouse/query]  [Feature / AI data]
                  |              |
                  v              v
             BI / reports   ML / retrieval / apps

Cross-cutting capabilities:
identity & access | catalog & lineage | quality | encryption
network boundaries | monitoring | audit | cost allocation
backup/recovery | orchestration | data contracts
```

This is a **logical** diagram, not a deployable architecture. Each box needs a defined responsibility, interface, owner, failure behaviour, and service-level objective. The diagram also omits detailed networking, hybrid connectivity, provider-specific mapping, and infrastructure-as-code implementation; those are taught in the later files in this module.

### 5.1 Design questions by capability

| Capability | Key design questions |
|---|---|
| Ingestion | Batch or streaming? Can the source be replayed? How are duplicates and partial failures handled? |
| Storage | Which data format, lifecycle, retention, encryption, and replication policy applies? |
| Processing | Is compute ephemeral or persistent? How does it scale? What happens on retry? |
| Governance | Where are schemas, ownership, classification, lineage, and quality results recorded? |
| Querying/serving | What are latency, concurrency, isolation, and access requirements? |
| Consumption | Which people, applications, reports, models, or agents consume the data? |
| Security | Which identity accesses which data through which route, under what policy? |
| Operations | How are freshness, failure, spend, drift, and suspicious access detected? |
| Recovery | What is recoverable, from where, by whom, and within which RTO/RPO? |

### 5.2 Separate data plane, control plane, and management responsibilities

A useful architectural distinction is:

- **Data plane:** the paths and operations that move, transform, store, or query business data.
- **Control plane:** the APIs and systems used to configure, manage, or orchestrate resources.
- **Management/observability plane:** inventory, logs, metrics, policy, cost, and incident workflows.

These are conceptual distinctions; provider terminology varies. A workload can have a healthy data path while a management dependency is impaired, or management access can work while the data path is blocked. Design and test these cases explicitly. The management/observability grouping is not universally a separate plane; in some architectures, its functions are part of the control plane or implemented by shared operational services.

### 5.3 Common cloud-native data-platform patterns

These are design patterns to evaluate, not requirements that every platform must adopt. Validate each pattern against workload needs, provider semantics, and operational constraints.

- **Decouple storage and compute where useful.** Durable object storage can hold data independently of short-lived processing or query compute. This can let teams scale or schedule compute separately from retained data, but does not make compute free, eliminate storage/request charges, or guarantee that every service is independent of the same storage or metadata dependencies.
- **Use elastic or ephemeral compute when the workload shape supports it.** Batch jobs may scale for a processing window and then stop; steady, latency-sensitive workloads may need provisioned capacity. Test startup time, concurrency, quotas, retries, and peak cost.
- **Treat ingestion and cataloguing as platform capabilities.** Managed ingestion, CDC, orchestration, catalog, lineage, and quality services can reduce custom operations, but the team still owns contracts, permissions, retry/replay behaviour, data quality rules, and incident response.
- **Apply identity-centred controls across the data flow.** Authorisation should be enforced at relevant layers—identity, resource policy, service configuration, and application/data controls—not inferred from private network placement alone.
- **Design for observable data products.** Track freshness, completeness/quality, pipeline success, access events, latency, and cost. Define an owner and a response path for each critical signal.

A useful review question is: *Which capability is this pattern improving, what new dependency does it introduce, and what evidence would show that the trade-off is acceptable?*

---

## 6. Cost architecture and FinOps fundamentals

Cloud cost is not just compute plus storage. A data platform's bill can include:

- Compute time, node/cluster capacity, or per-query processing.
- Stored data volume, storage class/tier, and retention duration.
- API/request counts, reads, writes, listing operations, and transactions.
- Data transfer between zones, regions, networks, or providers.
- Egress to users, on-premises systems, or another cloud.
- Replication, backup, snapshots, and disaster-recovery capacity.
- Managed-service premiums, licences, support plans, and observability.
- Idle resources, overprovisioned capacity, failed jobs, and repeated scans.

Exact charging rules vary by provider, service, region, agreement, and date. Use the current provider pricing pages and calculators for estimates; do not copy a price from an old tutorial and treat it as a quote.

### 6.1 Worked cost-driver calculation (illustrative, not a price quote)

Assume a platform stores **50 TB** of data, scans **12 TB per day** for analytics, and transfers **2 TB per month** to an external destination. Assume decimal units for this exercise:

- Stored data: \(50 \text{ TB} = 50{,}000 \text{ GB}\)
- Monthly scanned volume for a 30-day month: \(12 \times 30 = 360 \text{ TB}\)
- Monthly outbound transfer: \(2 \text{ TB} = 2{,}000 \text{ GB}\)

This gives **quantities**, not cost. To estimate cost, obtain the applicable unit rates and billing rules for the actual region/service and calculate:

\[
\text{Estimated monthly cost} =
\text{storage quantity}\times\text{storage rate}
+\text{scan quantity}\times\text{scan rate}
+\text{egress quantity}\times\text{egress rate}
+\text{other applicable charges}
\]

The formula is a simplified model. Real bills may have tiered pricing, minimums, free allowances, compression, caching, request charges, cross-zone transfer, committed capacity, taxes, and different billing units. Record these assumptions in the estimate.

**Architectural implication:** reducing bytes scanned can be more valuable than changing compute products. Partitioning, clustering, columnar formats, compaction, incremental processing, caching, lifecycle policies, and reducing unnecessary cross-boundary movement may lower spend—but must be tested against query performance, freshness, retention, and operational complexity.

### 6.2 Cost controls

| Control | What it does | Guardrail |
|---|---|---|
| Resource tags/labels | Attribute spend to team, domain, environment, and owner | Enforce required tags and handle shared costs |
| Budgets and alerts | Surface spend above a threshold | Alerts do not always stop consumption |
| Right-sizing | Match resources to measured workload | Avoid sizing solely from average load |
| Autoscaling/elastic compute | Match capacity to demand | Set limits; rapid scale-out can amplify cost |
| Lifecycle and retention | Move/delete eligible data according to policy | Confirm legal holds, recovery, and analytical needs |
| Query optimisation | Reduce scanned data and repeated work | Validate correctness and freshness |
| Egress reduction | Keep data movement purposeful and reduce duplicate transfers | Do not compromise required resilience or portability |
| Scheduling and shutdown | Stop non-production resources when unused | Protect shared dependencies and required test windows |
| Cost review | Review trends, anomalies, and unit economics | Include business volume so cost per outcome is visible |

A useful metric is not only “monthly spend” but also a unit measure such as cost per successful pipeline run, per terabyte curated, or per report served. A lower bill is not an improvement if freshness, reliability, or security deteriorates below agreed targets.

---

## 7. Managed versus self-managed services and operational ownership

Managed services reduce the amount of infrastructure the customer operates, but do not remove responsibility for architecture or workload outcomes.

| Dimension | Managed service | Self-managed service |
|---|---|---|
| Infrastructure patching | Provider handles documented underlying components | Team schedules and validates more patching |
| Scaling | May be built in or configurable | Team designs and operates scaling |
| Control | May expose fewer low-level choices | More control over runtime and configuration |
| Time to value | Often faster | Usually more engineering and operational setup |
| Portability | May depend on provider APIs and semantics | Open-source components can improve portability, but do not guarantee it |
| Failure handling | Provider operates service infrastructure; customer still handles workload recovery | Team owns more layers of diagnosis and recovery |
| Cost profile | Service premiums or consumption-based charges | Infrastructure plus engineering/on-call cost |
| Skills | Service-specific expertise still required | Deeper infrastructure and component expertise required |

Choose based on total cost of ownership (TCO), required control, skills, operational maturity, portability, and business risk—not on a simplistic assumption that managed is always cheaper or self-managed is always more portable.

### 7.1 Minimum operational model

For every production capability, specify:

- Service owner and escalation path.
- SLI/SLO or operational target (for example freshness, availability, processing completion).
- Metrics, logs, traces where applicable, and audit events.
- Alert thresholds, severity, and runbooks.
- Dependency map and expected behaviour when a dependency fails.
- Backup/restore and disaster-recovery procedure.
- Change management and rollback plan.
- Capacity, quota, and spend monitoring.
- Access review and incident evidence retention.

**Failure scenario — runaway query cost:** A dashboard change causes repeated full-table scans. Without query metrics, budgets, and an owner, the cost increase may remain unnoticed until the bill arrives. Prevention includes query-cost visibility, workload limits where available, review of data layout, and alerts. The exact controls depend on the service.

**Failure scenario — over-broad access:** A developer role is granted read access to all raw customer data to troubleshoot one pipeline. The network is private, but access is still excessive. Use a scoped role, time-bounded elevation, audited access, and a curated test dataset where possible.

**Failure scenario — zone outage:** A processing worker disappears. If the workload can restart elsewhere but its checkpoint, metadata, or output path is tied to the failed zone, the pipeline may still fail. Test the entire workflow, not just compute redundancy.

---

## 8. Architectural principles and decision criteria

Principles are durable statements that guide multiple decisions. They should be specific enough to influence design, with rationale and implications.

### 8.1 Example principles for Northbridge Bank

The following are **illustrative principles**, not legal advice or universal rules. The bank must confirm its own constraints with appropriate stakeholders.

1. **Classify before placement.** Data must have an owner and classification before production ingestion.  
   *Rationale:* region, access, retention, and encryption decisions depend on data sensitivity.
2. **Minimise access.** Human and workload identities receive only the permissions required for their duties.  
   *Rationale:* reduces the impact of compromised credentials and mistakes.
3. **Design to explicit recovery objectives.** Every critical data product defines RTO and RPO and has evidence from recovery tests.  
   *Rationale:* “high availability” is not a measurable recovery plan.
4. **Prefer capability-first designs.** Document logical responsibilities before selecting provider products.  
   *Rationale:* supports review, provider comparison, and future change.
5. **Make data movement intentional.** Every replica, export, and cross-boundary transfer has a purpose, owner, and approved destination.  
   *Rationale:* controls residency risk, egress cost, and uncontrolled copies.
6. **Instrument the platform.** Critical pipelines expose freshness, success/failure, quality, access, and cost signals.  
   *Rationale:* failures that cannot be detected cannot be managed reliably.
7. **Automate repeatable changes.** Infrastructure and policy changes should be reviewed, versioned, and reproducible.  
   *Rationale:* reduces configuration drift and improves recovery.
8. **Accept provider coupling deliberately.** Use provider-specific capabilities when their value exceeds their migration and skills costs; record the exit implications.  
   *Rationale:* abstracting everything can increase complexity without creating useful portability.

A good principle changes decisions. “The platform should be secure and scalable” is too vague unless it leads to controls and acceptance criteria.

### 8.2 Weighted decision criteria

Set the criteria and weights **before** scoring providers or architectures to reduce confirmation bias. Weights should reflect stakeholder priorities; scores should be supported by evidence and uncertainty notes.

Example only:

| Criterion | Weight | What evidence could support a score? |
|---|---:|---|
| Requirements and workload fit | 25% | Required capabilities, service availability, tested workload fit |
| Security and residency | 20% | Control mapping, approved locations, identity and key options |
| Reliability and recovery | 15% | Failure-domain design, documented features, tested RTO/RPO |
| Total cost of ownership | 15% | Transparent estimate including egress, operations, and support |
| Skills and operability | 10% | Team experience, support model, on-call readiness |
| Maintainability and time to value | 10% | Complexity, automation, monitoring, delivery timeline |
| Portability/exit cost | 5% | Data formats, dependencies, export and migration plan |
| **Total** | **100%** | |

A simple weighted score can be calculated as:

\[
\text{Weighted score}=\sum_i w_i s_i
\]

where \(w_i\) is a weight expressed as a fraction (all weights sum to 1) and \(s_i\) is a score on a consistent scale, such as 1–5. The score helps structure discussion; it does not make uncertain evidence objective. A hard legal or security constraint should eliminate an option rather than be “offset” by a high cost or feature score.

### 8.3 Architecture Decision Record (ADR)

An ADR records one important architectural decision and why it was made.

Recommended structure:

```markdown
# ADR-001: Cloud data-platform principles and location strategy

- Status: Proposed | Accepted | Superseded
- Date:
- Decision owner:
- Reviewers:

## Context
Business outcomes, requirements, constraints, assumptions, and risks.

## Decision drivers
Ranked criteria and any hard constraints.

## Options considered
A. ...
B. ...
C. ...

## Decision
The selected approach and its boundaries.

## Rationale
Evidence and trade-offs behind the decision.

## Consequences
Benefits, costs, risks, operational obligations, and exit implications.

## Validation plan
Tests, proof points, owners, and review date.
```

An ADR is not merely a description of the chosen product. It records the rejected options and the reasoning so future teams can revisit the decision when assumptions change.

---

## 9. Intermediate level — Northbridge Bank design exercise

### 9.1 Scenario and explicit assumptions

**Northbridge Bank is fictional.** For this exercise, assume:

- The bank plans to move analytics workloads to one public cloud.
- The core ledger remains on premises for three years.
- Customer-level analytics data are treated as sensitive.
- The bank's policy requires sensitive customer data and its backups to remain in approved in-country locations. This is a **scenario assumption**, not a statement of any real law.
- Regulatory reporting must survive a regional outage; the exact RTO/RPO must be agreed with business and risk owners.
- The team is small and prefers managed services where they meet the requirements.
- Current prices, provider availability, service limits, and legal interpretations have not been supplied and must be verified before implementation.

### 9.2 First-pass architecture

```text
On-premises core ledger
        |
        | approved, monitored connection
        v
Ingestion / CDC boundary
        |
        v
Raw landing zone  ---> quarantine / failed-record handling
        |
        v
Validation + transformation
        |
        v
Curated data products
        |                    \
        v                     v
Regulatory reporting       Analytics / ML datasets
        |
        v
Authorised consumers

Cross-cutting: IAM, key policies, catalog/lineage, audit,
quality checks, monitoring, cost allocation, backup/DR.
```

This diagram intentionally remains provider-neutral. It defines capabilities and trust boundaries before the AWS, Azure, and GCP lessons map those capabilities to concrete services.

### 9.3 Questions to resolve before product selection

1. Which data classes can be ingested, stored, processed, and backed up in each proposed location?
2. Does the chosen service support the required private access and identity model?
3. Which records must be masked or tokenised before broader analytics use?
4. What are the reporting freshness target, availability objective, RTO, and RPO?
5. Which failures should be automatic, and which require operator approval?
6. What is the expected daily data volume and growth rate?
7. What are the main query patterns and concurrency needs?
8. Which data movement is required for backup, DR, analytics consumers, and exit?
9. Who owns each service, alert, permission policy, and recovery runbook?
10. What evidence is required before production approval?

---

## 10. Advanced level — trade-offs, risk, and failure-domain reasoning

### 10.1 Single region, multi-zone, or cross-region recovery

| Option | Benefits | Limitations and risks | Suitable when |
|---|---|---|---|
| Single zone | Simple and potentially lower complexity | Zone failure may make the workload unavailable | Non-critical or explicitly accepted risk |
| Multi-zone within one region | Can withstand some zone failures if every dependency and data path is designed accordingly | Does not by itself address region-wide failures or logical corruption | Zone-level availability target matters; regional recovery is separately addressed |
| Cross-region recovery | Can reduce exposure to some regional failures | Replication lag, extra cost, more operations, residency restrictions, and failover complexity | RTO/RPO and risk analysis justify it and locations are permitted |
| Backup and restore | Can recover from deletion/corruption and may be cheaper than hot standby | Restore may take longer; backups must be isolated and tested | Business recovery objectives allow the tested restore time |

The choice depends on workload criticality, recovery objectives, cost, and legal boundaries. There is no universal “best” pattern.

### 10.2 Managed versus self-managed

A managed database can reduce patching and infrastructure work, but the customer still designs access, schema, retention, data quality, backups where configurable, monitoring, query patterns, and recovery. A self-managed database may allow more control, but the team must be prepared to operate the complete stack, including upgrades and incident response.

Ask: **What exact responsibility are we buying the provider to operate, and what will we still need to build and run?**

### 10.3 Elasticity versus predictability

Elasticity is useful for irregular or bursty workloads, such as month-end reporting. It can also create surprising spend if concurrency, retry behaviour, or query scans are unbounded. Provisioned capacity may provide more predictable throughput and cost at stable utilisation, but may be wasteful during idle periods.

Measure workload shape before deciding:

- Average and peak load.
- Duration and frequency of peaks.
- Startup/cold-start and scale-out time.
- Quotas and concurrency limits.
- Cost at typical and peak load.
- Behaviour when capacity cannot scale quickly enough.

Do not assume “serverless” means unlimited, instant, or always cheaper.

### 10.4 Portability and maintainability

Portability is layered. A data file may be portable while orchestration, identity policies, catalog semantics, SQL behaviour, encryption configuration, monitoring, and operational processes are not.

This lesson introduces the trade-off only; detailed provider comparison and exit planning belong in `07-portability-lock-in-and-multi-cloud-trade-offs.md`.

A sensible principle is **selective portability**: keep important data and interfaces portable where it has a clear business value, while accepting managed/provider-specific features where they materially improve delivery or operations. Record the coupling and exit cost explicitly.

### 10.5 Common failure scenarios and the design response

| Scenario | Likely impact | Preventive/detective controls | Recovery question |
|---|---|---|---|
| Zone failure | Some compute or zonal resources unavailable | Multi-zone design, health checks, workload-level monitoring | Can the full data flow continue? |
| Region failure | Regional services and workloads may be unavailable | Cross-region recovery design, backups, documented dependencies | Is the secondary environment complete and usable? |
| Mis-scoped permission | Unauthorised data exposure or destructive action | Least privilege, policy review, audit, access tests | How is access revoked and impact assessed? |
| Key disabled or unavailable | Encrypted data may become inaccessible | Key ownership, change controls, monitoring, recovery procedures | Can authorised operators restore key access safely? |
| Replication lag | Secondary copy is stale | Lag metrics and alert thresholds | Does actual recovery point meet RPO? |
| Corrupt data replicated | Secondary copy may also be corrupted | Validation, versioning/retention, independent backups | Can a known-good point be restored? |
| Runaway query/compute spend | Budget overrun or resource contention | Usage metrics, budgets, limits, query optimisation | Who can contain spend without causing a wider outage? |
| On-premises link failure | Ingestion delays or backlog | Queue/buffer where appropriate, retry, replay, link monitoring | Can ingestion catch up without duplicates or loss? |

---

## 11. Hands-on exercises

### Exercise A — Shared responsibility and residency model

**Scenario:** Northbridge plans to move analytics data to a managed cloud service.

**Tasks**

1. Create a responsibility table for storage, compute, identity, network, keys, data classification, audit, backup, and recovery.
2. Assign one accountable owner to each responsibility.
3. Define permitted locations for each data class.
4. Include replicas, backups, logs, exports, and support-access considerations.
5. Write at least three validation tests that could reveal a configuration error.

**Deliverable:** `northbridge-responsibility-and-residency.md`

**Validation criteria**

- No row is left with an ambiguous owner.
- Provider-managed controls are distinguished from customer configuration.
- Residency rules include secondary copies and operational data, not only the primary store.
- Each critical rule has evidence or a test method.

### Exercise B — Principles and weighted criteria

**Scenario:** The board asks for architecture principles before provider demonstrations.

**Tasks**

1. Write 6–8 principles, each with a rationale and a concrete implication.
2. Define weighted decision criteria before scoring providers.
3. Identify hard constraints that eliminate an option.
4. List assumptions and evidence still needed.
5. Write an ADR comparing at least three options, such as single-region, multi-zone with backup, and cross-region recovery.

**Deliverables:** principles sheet, criteria matrix, and ADR.

**Validation criteria**

- Criteria weights total 100%.
- Hard constraints are not treated as ordinary weighted preferences.
- Each principle changes a decision or control.
- Trade-offs and rejected options are explicit.

### Exercise C — Failure-domain diagram

Draw a single-region architecture with three zones. Label every component as one of:

- Zonal.
- Multi-zone or zone-redundant (only where verified).
- Regional/shared dependency.
- External dependency.
- Unknown; requires verification.

Then annotate what is expected to survive (a) one zone failure and (b) a regional failure. Do not assume that a component is redundant just because it is managed.

### Exercise D — Cost-driver worksheet

Using the illustrative quantities in Section 6.1:

1. Keep storage, scanned data, and outbound transfer as separate line items.
2. Find the current official rates for the specific provider/service/region you choose.
3. Record retrieval/request/replication charges and applicable free tiers or commitments.
4. Calculate a low, expected, and high estimate where usage is uncertain.
5. State what workload change would most reduce spend and what quality or reliability trade-off it introduces.

Do not publish an estimate without a date, region, units, and assumptions.

---

## 12. Review questions with answer guidance

Try to answer without looking at the guidance first.

1. **What is the difference between a cloud service and a cloud architecture?**  
   *Answer guidance:* a service provides a capability; architecture defines how capabilities, boundaries, identities, data flows, operations, and failure behaviour work together to meet requirements.

2. **Why is managed service not the same as fully managed responsibility?**  
   *Answer guidance:* provider operation reduces infrastructure work, but customers retain responsibility for data, access, configuration, workload logic, monitoring, and recovery requirements according to the service.

3. **How do scalability and elasticity differ?**  
   *Answer guidance:* scalability concerns handling increased load; elasticity adjusts capacity with demand, including scaling down.

4. **Why does multi-zone deployment not guarantee regional disaster recovery?**  
   *Answer guidance:* zones share a region and may share dependencies; a regional event can affect all of them. Regional recovery needs a separate, tested design.

5. **What assumptions are required for the idealised redundant-availability formula?**  
   *Answer guidance:* either component can serve, failures are independent, failover works, and there are no shared single points of failure or correlated defects.

6. **Name five cost drivers beyond stored data volume.**  
   *Answer guidance:* compute, requests, scans, egress, replication, backup, support, licence, idle capacity, observability, cross-zone/region transfer.

7. **Why must residency analysis include backups and logs?**  
   *Answer guidance:* secondary copies and operational artefacts may contain sensitive data and may cross the intended boundary.

8. **Why should criteria and weights be set before provider scoring?**  
   *Answer guidance:* to reduce confirmation bias and prevent changing criteria to justify a preferred product.

9. **When might a self-managed service be justified?**  
   *Answer guidance:* when required control, compatibility, or portability value exceeds the additional operational burden and the team can operate it safely.

10. **What belongs in an ADR?**  
    *Answer guidance:* context, constraints, decision drivers, options, decision, rationale, consequences, risks, and validation/review plan.

11. **Give an example where network controls alone are insufficient.**  
    *Answer guidance:* a workload on a private network still has excessive IAM permissions; the network restricts reachability but does not limit authorised actions enough.

12. **What would make a cloud cost estimate untrustworthy?**  
    *Answer guidance:* missing region/date/units, outdated prices, omitted egress or requests, unrealistic usage assumptions, unaccounted discounts/tiers, and no uncertainty range.

13. **What evidence is needed to claim that a recovery design meets RPO?**  
    *Answer guidance:* defined target, measured replication/backup behaviour under representative conditions, and a successful recovery test demonstrating the age of recovered data.

14. **Why is a provider comparison not a product-name matching exercise?**  
    *Answer guidance:* products can have different semantics, limits, security models, and operating responsibilities despite occupying a similar capability category.

---

## 13. Expected deliverables and mastery gate

Complete and review these artefacts before moving to the provider-specific lessons:

- [ ] Shared-responsibility table with named owners and evidence.
- [ ] Region and residency rules covering replicas, backups, logs, and exports.
- [ ] Capability-level data-platform diagram.
- [ ] Cost-driver list with quantities, rate sources, dates, and assumptions.
- [ ] Six to eight architecture principles with rationale.
- [ ] Weighted decision criteria sheet with weights totalling 100%.
- [ ] ADR recording options, rationale, trade-offs, and validation plan.
- [ ] Failure-domain diagram showing zone and region boundaries.
- [ ] Exercise gap log and corrected answers.

### Mastery criteria

You are ready to progress when you can, without relying on product names:

1. Explain the difference between a cloud service and the architecture built around it.
2. Explain shared responsibility for one managed data service and identify what the customer still owns.
3. Distinguish zone failure from region failure and describe which components would survive.
4. Explain why availability arithmetic can overstate real reliability.
5. List major cloud data-platform cost drivers and identify a plausible optimisation for each.
6. Define residency constraints that cover primary data, replicas, backups, and operational artefacts.
7. Defend architecture principles and weighted criteria with evidence and explicit assumptions.
8. Produce an ADR that another engineer can review and challenge.

**Completion gate:** Ask another person to review the responsibility table, residency rules, criteria sheet, and ADR. If you cannot explain a failure-domain diagram or have left any critical responsibility owner blank, revise the artefact before proceeding.

---

## 14. Quick completion checklist

- [ ] I can explain IaaS, PaaS, SaaS and deployment models in my own words.
- [ ] I know what a managed service does and does not take off my plate.
- [ ] I can distinguish scalability, elasticity, availability, resilience, RTO, and RPO.
- [ ] I have not assumed that zone redundancy equals disaster recovery.
- [ ] I can explain the assumptions and limitations of the availability formula.
- [ ] I have documented region and data-residency constraints.
- [ ] I can draw the platform as capabilities and data flows before naming products.
- [ ] I have included egress, requests, replication, and operations in cost reasoning.
- [ ] I have assigned owners for monitoring, incident handling, and recovery.
- [ ] I have written principles, weighted criteria, and an ADR.
- [ ] I have recorded unverified service, legal, quota, and pricing details for follow-up.

---

## 15. Authoritative references and verification notes

The following sources were consulted for core cloud concepts. Provider-specific capabilities, regional availability, pricing, quotas, and contractual terms must still be checked for the exact service and deployment at implementation time.

1. [AWS — Shared Responsibility Model](https://aws.amazon.com/compliance/shared-responsibility-model/) — explains security responsibilities of the cloud provider and customer.
2. [AWS — Regions and Availability Zones](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions-availability-zones.html) — describes regions and AZs and notes that some resources are not automatically replicated across regions.
3. [Microsoft Learn — Shared responsibility in the cloud](https://learn.microsoft.com/en-us/azure/security/fundamentals/shared-responsibility/) — outlines how responsibilities vary across IaaS, PaaS, and SaaS.
4. [Microsoft Azure — Bandwidth pricing](https://azure.microsoft.com/en-in/pricing/details/bandwidth/) — illustrates that data-transfer charges and categories are service- and location-dependent; prices and terms can change.
5. [Google Cloud Architecture Center — Shared responsibilities and shared fate](https://docs.cloud.google.com/architecture/framework/security/shared-responsibility-shared-fate) — explains workload-dependent customer and provider security responsibilities.
6. [Google Cloud — Regions and zones](https://cloud.google.com/compute/docs/regions-zones) — describes the scope of regions and zones; service-specific resilience and replication behaviour still needs separate verification.
7. [Microsoft Learn — Availability Zones](https://learn.microsoft.com/en-us/azure/reliability/availability-zones-overview) — describes Azure availability zones and the need to check service-specific availability-zone support.

**Verification discipline**

- No cloud prices, quotas, performance benchmarks, or compliance guarantees are asserted as universal facts in this lesson.
- Numeric quantities in the cost exercise and the Northbridge Bank scenario are illustrative assumptions.
- The availability formula is mathematical under stated assumptions, not a cloud-provider SLA.
- Before implementing an architecture, verify current provider documentation, regional service availability, pricing, service limits, security configuration, contractual terms, and applicable legal requirements.
- Provider-specific service mapping belongs in `02-aws-data-architecture-reference-patterns.md`, `03-azure-data-architecture-reference-patterns.md`, and `04-gcp-data-architecture-reference-patterns.md`. Detailed networking, hybrid connectivity, portability, and infrastructure-as-code belong in Topics 5–8 of this module.
