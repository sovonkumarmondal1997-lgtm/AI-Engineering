# Practice Questions — Cloud, Hybrid and Multi-Cloud Data Architecture

**Module:** Stage 2D — Data Architecture  
**Folder:** `08-Cloud-Hybrid-and-Multi-Cloud-Data-Architecture/`  
**Assessment scope:** Topics 01–08 and the integrated cloud-platform architecture comparison exercise  
**Status:** Newly designed assessment resource based on `roadmap-Cloud-Hybrid-and-Multi-Cloud-Data-Architecture.md`. The roadmap identifies the prior `practice-questions.md` as empty; this file does not claim to preserve a previous question bank.

> **How to use this file.** Attempt the questions before reading the answer key. Questions marked *illustrative* use fictional systems and assumed values. Provider service names and features can change: use the topic lessons and current official provider documentation to verify implementation-specific claims. Where a question asks for an architecture, the answer key gives one defensible answer, not the only acceptable design. No question requires a paid cloud deployment.

## Contents

- [Assessment method and scoring](#assessment-method-and-scoring)
- [Section A — Cloud architecture principles](#section-a--cloud-architecture-principles)
- [Section B — AWS data architecture](#section-b--aws-data-architecture)
- [Section C — Azure data architecture](#section-c--azure-data-architecture)
- [Section D — GCP data architecture](#section-d--gcp-data-architecture)
- [Section E — Three-provider comparison](#section-e--three-provider-comparison)
- [Section F — Networking, identity, and private connectivity](#section-f--networking-identity-and-private-connectivity)
- [Section G — Hybrid connectivity and on-premises integration](#section-g--hybrid-connectivity-and-on-premises-integration)
- [Section H — Portability, vendor lock-in, and multi-cloud](#section-h--portability-vendor-lock-in-and-multi-cloud)
- [Section I — Infrastructure as code and environments](#section-i--infrastructure-as-code-and-environments)
- [Section J — Integrated architecture scenarios](#section-j--integrated-architecture-scenarios)
- [Answer key and evaluation rubrics](#answer-key-and-evaluation-rubrics)
- [Study, remediation, and reassessment](#study-remediation-and-reassessment)
- [Final project readiness checklist](#final-project-readiness-checklist)

---

## Assessment method and scoring

### Difficulty levels

- **Beginner:** terminology, foundational concepts, and direct interpretation.
- **Intermediate:** apply concepts to a concrete architecture or diagnose a bounded failure.
- **Advanced:** evaluate competing designs, calculate consequences, expose assumptions, and justify decisions under constraints.

### Question types

The bank mixes multiple choice (MCQ), true/false with justification (T/F), short answer (SA), calculation (CALC), diagram/design (DESIGN), troubleshooting (TROUBLESHOOT), code/configuration review (CODE), and architecture decision record (ADR) tasks.

### Suggested scoring

Unless a question gives a specific score, use **4 points** per question:

- **4 — Complete:** correct conclusion, relevant reasoning, explicit assumptions/constraints, and key risks or limitations.
- **3 — Sound:** substantially correct, with one material omission.
- **2 — Partial:** some correct concepts but incomplete reasoning or a significant missing control.
- **1 — Weak:** largely descriptive, unsupported, or misses the core issue.
- **0 — Incorrect / not attempted:** materially wrong or no answer.

For MCQs, award 4 for the correct option and 0 otherwise, then explain why. For calculations, use the answer key's stated assumptions and accept equivalent rounding when units and method are correct. For design questions, apply the rubric in the answer key; do not require the exact reference design.


### Point totals and topic-level readiness scoring

The scoring is a **recommended learning aid**, not an external certification standard. The default maximum is 4 points per question, except `J1-Q01` (20 points) and `J1-Q04` (12 points), as stated in their rubrics. Across this 40-question bank, the maximum is **184 points**. Calculate the overall percentage as `points earned ÷ 184 × 100`; an 85% threshold therefore requires at least **157/184 points** when using whole-number scores.

For the separate **70% minimum per topic**, use the dedicated topic sections below; do not treat the mixed-provider comparison in Section E or the integrated scenario in Section J as if they were a single topic. Section E and J still count toward the overall score.

| Topic gate | Dedicated section | Maximum points | Minimum points for at least 70% |
|---|---:|---:|---:|
| Topic 01 — Cloud architecture principles | A | 20 | 14 |
| Topic 02 — AWS data architecture | B | 16 | 12 |
| Topic 03 — Azure data architecture | C | 12 | 9 |
| Topic 04 — GCP data architecture | D | 12 | 9 |
| Topic 05 — Networking, identity, private connectivity | F | 16 | 12 |
| Topic 06 — Hybrid connectivity and on-premises integration | G | 16 | 12 |
| Topic 07 — Portability, lock-in and multi-cloud | H | 16 | 12 |
| Topic 08 — Infrastructure as code and environments | I | 20 | 14 |

Section E has 16 points and Section J has 40 points. Those 56 points contribute to the overall assessment, while the eight dedicated section scores provide the per-topic threshold check. Passing the numerical thresholds does not replace completion of all eight roadmap topic gates or the reviewed integrated exercise.

### Source alignment

The roadmap is the controlling source for learning order, intended deliverables, and gates. Topic files provide detailed implementation material. Provider examples in this assessment are learning prompts, not a substitute for verifying current service semantics, quotas, regional availability, or pricing. If a provider-specific fact cannot be established from the lesson or official documentation, record it as a **research item**, not a guess.

---

# Section A — Cloud architecture principles

## A1-Q01 — Shared responsibility [Beginner | MCQ | Topic 01]

A team uses a managed cloud analytics service. Which statement best describes the shared-responsibility model?

A. The cloud provider is responsible for every security control because the service is managed.  
B. The customer is responsible for physical data-centre security and all underlying hardware.  
C. Responsibilities are divided; the provider operates parts of the service, while the customer still configures identities, data access, classification, and workload use appropriately.  
D. Shared responsibility means the customer and provider must both administer every control.

## A1-Q02 — Deployment models [Beginner | T/F with justification | Topic 01]

True or false: **Hybrid cloud and multi-cloud are always more resilient than a single-cloud architecture.** Justify your answer with at least two operational considerations.

## A1-Q03 — Residency and failure domains [Intermediate | SA | Topic 01]

A regulator requires personal data to remain in-country. Name at least **five** architecture items to verify before approving a cloud design. Explain why choosing an in-country primary region alone may not be sufficient.

## A1-Q04 — Cost drivers [Intermediate | SA | Topic 01]

A data platform's monthly bill rises even though stored data volume is nearly unchanged. List six plausible cost drivers or changes to investigate. For each, name one piece of evidence you would collect before recommending a fix.

## A1-Q05 — Availability zones and recovery [Advanced | DESIGN | Topic 01]

A reporting service has a 99.5% monthly availability objective. Explain how you would translate this into architecture and operational questions. Distinguish availability, durability, resilience, RTO, and RPO. Do not assume that a service's advertised SLA proves the whole platform meets the objective.

---

# Section B — AWS data architecture

## B1-Q01 — Capability-first mapping [Beginner | MCQ | Topic 02]

A team needs durable object storage for a data lake, a managed SQL query capability over stored data, and a central permissions/governance model. Which approach is best?

A. Pick three familiar AWS service names first and then rewrite the requirements to fit them.  
B. Define the logical capabilities and requirements, map candidate AWS services to them, then verify their semantics, boundaries, security, and costs.  
C. Use one service for every capability because fewer service names always mean lower cost.  
D. Select the architecture based only on the number of services in the diagram.

## B1-Q02 — Trace an AWS flow [Intermediate | SA | Topic 02]

**Illustrative design prompt.** A bank lands daily files from an on-premises source, transforms them, stores curated datasets, and allows analysts to query them. Sketch a provider-specific flow using plausible AWS capability candidates. Identify the purpose of each component and at least four failure/security checks. Mark service-specific details that require current verification.

## B1-Q03 — Processing and governance trade-off [Advanced | ADR | Topic 02]

The platform team is deciding between a managed/serverless analytics path and a cluster-based processing path for a workload with irregular demand and a few predictable heavy jobs. Write a short ADR outline covering requirements, options, decision criteria, costs, operational burden, governance, risks, and what evidence could change the decision. You do not need to name one universally best AWS service.

## B1-Q04 — AWS reliability and cost diagnosis [Intermediate | TROUBLESHOOT | Topic 02]

A daily pipeline sometimes completes late. The team proposes doubling compute size immediately. List an ordered diagnostic sequence that checks orchestration, source arrival, throttling/quotas, data skew, retries, network access, and cost signals before selecting a remedy.

---

# Section C — Azure data architecture

## C1-Q01 — Identity and storage [Beginner | MCQ | Topic 03]

An Azure-hosted pipeline must access storage through an approved private network path without embedding long-lived access keys in source code. Which design principle is best?

A. Put the storage key in a repository secret and give every pipeline the same key.  
B. Use a suitable workload identity/managed identity with narrowly scoped permissions, and verify network reachability and storage authorization separately.  
C. Make storage public but use an obscure URL.  
D. Give the pipeline subscription-wide administrator rights to avoid permission errors.

## C1-Q02 — Azure capability map [Intermediate | SA | Topic 03]

Map these logical capabilities to plausible Azure service families: object storage, managed orchestration/ingestion, Spark-based processing, analytical serving, identity, and governance/catalogue. For each mapping, state one semantic or operational difference that must be verified rather than assuming equivalence with AWS or GCP.

## C1-Q03 — Integrated platform trade-off [Advanced | DESIGN | Topic 03]

An organization already uses Microsoft identity and has a small data-platform team. Compare an integrated analytics-platform approach with a composed design using separately managed storage, orchestration, processing, and query services. Discuss time to value, skills, governance, portability, operational responsibility, cost visibility, and vendor dependence. State which facts you would verify before deciding.

---

# Section D — GCP data architecture

## D1-Q01 — GCP data flow [Beginner | MCQ | Topic 04]

Which statement is the strongest architecture practice when mapping a logical data platform to GCP?

A. Treat similarly named services on different clouds as behaviorally identical.  
B. Map logical capabilities first, then verify service semantics, location behavior, security, cost model, and provider-specific dependencies.  
C. Assume serverless means no partitioning, governance, quota, or cost design is needed.  
D. Choose the service with the largest feature list regardless of workload.

## D1-Q02 — Location and cost [Intermediate | SA | Topic 04]

A workload uses object storage, stream/batch processing, and a serverless analytical warehouse. Identify five location, governance, performance, or cost questions to resolve before production. Include at least one question about data movement and one about query/processing billing.

## D1-Q03 — Provider-specific warehouse dependency [Advanced | ADR | Topic 04]

The analytics team wants to use a proprietary warehouse SQL feature that speeds up delivery but may increase exit cost. Write a decision outline that weighs the feature's business value against portability, open data formats, query rewrite, staff skills, security/governance, and the cost of keeping a migration path available.

---

# Section E — Three-provider comparison

## E1-Q01 — Fair comparison [Beginner | T/F with justification | Topics 02–04, 07]

True or false: **If AWS, Azure, and GCP each offer a service in a category called “object storage,” the three implementations are equivalent for architecture comparison.** Explain what evidence is needed.

## E1-Q02 — Comparison matrix [Intermediate | DESIGN | Topics 01–07]

Create a comparison table for AWS, Azure, and GCP for these logical capabilities: ingestion/CDC, object storage, transformation, orchestration, catalogue/governance, private access, and analytical serving. Include columns for candidate service, key behavior to verify, security boundary, pricing unit, portability concern, and evidence/source date. If you cannot establish a fact, mark it “research item.”

## E1-Q03 — Equivalence claim review [Advanced | TROUBLESHOOT | Topics 02–04, 07]

A draft architecture review says: “Service X is the AWS equivalent of Service Y on Azure, so we can switch without code changes.” List at least eight dimensions to investigate before accepting the claim. Explain why service-category similarity does not prove migration equivalence.

## E1-Q04 — No clear winner [Intermediate | SA | Topics 02–04, 07]

Under what conditions is “no provider is clearly best” a sound comparison outcome? Give a defensible method for identifying unresolved research items without disguising them as scores.

---

# Section F — Networking, identity, and private connectivity

## F1-Q01 — Network reachability versus permission [Beginner | MCQ | Topic 05]

A pipeline's TCP connection to a private storage endpoint succeeds, but a read request returns an authorization error. Which statement is best?

A. Network reachability proves the identity has permission.  
B. The issue is necessarily DNS.  
C. The network path may be working; check authentication, authorization scope, and service-side policy independently.  
D. The fix is to grant organization-wide administrator rights.

## F1-Q02 — CIDR arithmetic [Intermediate | CALC | Topic 05]

An IPv4 subnet is `10.20.4.0/24`. How many total IPv4 addresses are in the CIDR block? Show the calculation. Explain why the number of usable addresses in a particular cloud subnet may be smaller.

## F1-Q03 — Diagnose private access [Intermediate | TROUBLESHOOT | Topic 05]

A pipeline suddenly times out when reading a managed data service that it accessed yesterday. Build a diagnostic sequence using the roadmap's five-layer model: name resolution, network path, authentication, authorization, and service-side network rules. For each layer, name a check and a likely symptom.

## F1-Q04 — Least-privilege role design [Advanced | DESIGN | Topic 05]

A transformation job reads a raw-data prefix and writes a curated-data prefix. Propose a least-privilege identity and permission design. Include environment separation, encryption/key permissions where relevant, audit logging, private network path, and how to avoid long-lived credentials. State which permissions should not be granted by default.

---

# Section G — Hybrid connectivity and on-premises integration

## G1-Q01 — VPN versus dedicated connectivity [Beginner | SA | Topic 06]

Compare site-to-site VPN and dedicated private connectivity for an on-premises bank connecting to cloud data services. Discuss setup, path characteristics, resilience, routing, encryption responsibilities, cost, and why neither choice removes the need for identity authorization.

## G1-Q02 — Transfer-time calculation [Intermediate | CALC | Topic 06]

**Illustrative assumptions:** transfer `20 TB` of decimal data (`20 × 10^12` bytes) over a `1 Gbit/s` link. Average effective utilization is `70%`; ignore protocol overhead beyond that utilization assumption. Estimate transfer time in seconds, hours, and days. Show units and state at least two real-world limitations.

## G1-Q03 — Hybrid failure matrix [Intermediate | TROUBLESHOOT | Topic 06]

The on-premises ledger sends CDC changes to cloud storage. A link outage lasts 45 minutes, DNS resolution fails for the private service name after failover, and the CDC consumer has a growing backlog. Identify the immediate risks, recovery order, reconciliation checks, and operational owners. Explain why blindly replaying all records may be unsafe.

## G1-Q04 — Connectivity decision [Advanced | ADR | Topic 06]

Choose between VPN, dedicated connectivity, or a staged combination for a workload that initially transfers 20 TB once, then sends 2 TB/day, has a near-real-time target, and must survive one link failure. State assumptions, calculate the initial transfer time for a 1 Gbit/s link at 70% efficiency, compare alternatives, and identify what measurements would trigger a design change.

---

# Section H — Portability, vendor lock-in, and multi-cloud

## H1-Q01 — Portability layers [Beginner | SA | Topic 07]

Name at least six distinct layers at which a data platform can be more or less portable. Give one example of a dependency or migration concern at each layer.

## H1-Q02 — Egress estimate [Intermediate | CALC | Topic 07]

**Illustrative assumptions only, not provider pricing:** an exit plan must transfer `50 TB` of decimal data (`50,000 GB`) out of a cloud. Assume a hypothetical egress price of `$0.09/GB`, excluding taxes, discounts, inter-region fees, requests, and transfer tooling. Calculate the illustrative egress charge. Then explain why this is not a provider quote or a complete exit-cost estimate.

## H1-Q03 — Single, hybrid, or multi-cloud [Advanced | ADR | Topics 06–07]

Use the following **illustrative** scenario: a regulator requires an exit plan, the core ledger must remain on premises for three years, no rule mandates active-active multi-cloud, the platform team has deep expertise in one cloud, and data egress is expensive. Compare (a) single cloud with open data formats and a tested exit plan, (b) hybrid during the three-year transition, and (c) distributed multi-cloud. Recommend a strategy under explicit assumptions and name conditions that would change the recommendation.

## H1-Q04 — Data gravity and exit planning [Intermediate | SA | Topic 07]

Outline an exit plan for a cloud data platform. Include dependency inventory, data export, schemas/metadata, identity, networking, pipelines, validation/reconciliation, cutover, rollback/contingency, cost/time ranges, owners, and a test cadence. Explain why “we store Parquet” is not a complete portability strategy.

---

# Section I — Infrastructure as code and environments

## I1-Q01 — Declarative and imperative IaC [Beginner | MCQ | Topic 08]

Which statement best distinguishes declarative from imperative infrastructure automation?

A. Declarative code describes the desired end state; imperative automation emphasizes steps to execute. Both can have failure modes and operational constraints.  
B. Declarative code cannot create resources.  
C. Imperative automation is always unsafe and should never be used.  
D. Declarative code guarantees zero drift and zero outages.

## I1-Q02 — State, drift, and concurrency [Intermediate | SA | Topic 08]

Define desired state, actual state, state file/state backend, drift, reconciliation, idempotency, and state locking. Explain what can go wrong if two engineers apply changes concurrently against the same state without reliable locking or coordination.

## I1-Q03 — Code review [Intermediate | CODE | Topic 08]

Review this **intentionally unsafe pseudocode**, not valid provider-specific IaC:

```text
create storage bucket
public_access = true
encryption = false
admin_role = "*"
secret = "prod-access-key-value"
environment = "all"
```

Identify at least five defects and propose safe design principles. Do not rewrite it into a deployable cloud configuration; instead specify controls the module should enforce.

## I1-Q04 — Promotion and recovery [Advanced | DESIGN | Topic 08]

Design a development → test → staging → production promotion workflow. Cover source control, pull request review, static/policy checks, plan/preview, approval, immutable module/artifact versioning, environment-specific configuration, deployment identity, post-apply verification, rollback/recovery, emergency break-glass, and drift detection. Explicitly distinguish rollback of infrastructure from rollback of data.

## I1-Q05 — State-security scenario [Advanced | TROUBLESHOOT | Topic 08]

A remote state backend contains sensitive values. Two pipeline runs overlap; one holds a lock and fails. A teammate proposes deleting the state file and rerunning apply. Explain why that is unsafe, what to inspect first, and a safe recovery sequence. Include backups, lock ownership, state integrity, access control, and audit evidence.

---

# Section J — Integrated architecture scenarios

## J1-Q01 — Northbridge Bank integrated exercise [Advanced | DESIGN | Topics 01–08]

**Illustrative scenario based on the roadmap.** Northbridge Bank is a fictional mid-sized bank. It plans to host an analytics and ML platform in public cloud, while its core ledger remains on premises for three years. The board requires an exit plan. A regulator expects private access to customer data and in-country residency. Assume approximately `250 TB` in the total source estate today, with net estate growth of `30% per year` compounded annually. The `2 TB/day` figure is CDC/change-data volume (which can include updates and deletes), not net growth. The initial `20 TB` historical load is the first migration wave, not the whole estate; the exit/migration plan must account for the remaining data. Use a near-real-time fraud-feature target of `≤60 seconds p95`. No paid deployment is required.

Produce:
1. measurable requirements, assumptions, and decision criteria;
2. a logical capability diagram with no provider names;
3. a mapping to any two providers, marking unverified claims;
4. a network/identity boundary diagram and five-layer access-path table;
5. hybrid connectivity options and initial transfer-time arithmetic;
6. per-layer portability assessment and exit-plan outline;
7. environment/IaC promotion workflow and drift policy;
8. one ADR for single cloud versus multi-cloud;
9. risk register with owner, mitigation, and residual risk.

## J1-Q02 — Transfer arithmetic and throughput [Intermediate | CALC | Topics 06–07]

Use the same illustrative transfer assumptions as G1-Q02: `20 × 10^12` bytes, `1 × 10^9` bits/s link rate, and `0.70` effective utilization. Calculate seconds, hours, and days. Then estimate the theoretical daily transfer capacity in decimal TB at the same effective throughput. Explain why the theoretical daily capacity does not guarantee the near-real-time fraud target.

## J1-Q03 — Architecture review panel [Advanced | SA | Topics 01–08]

A reviewer challenges the design with these claims:
- “The provider is managed, so our team no longer owns security.”
- “The private endpoint means the pipeline is authorized.”
- “Open file formats make the platform fully portable.”
- “Using two clouds automatically reduces risk.”
- “IaC makes production changes safe without human review.”
For each claim, explain what is wrong, give a corrected statement, and identify one piece of evidence or control the architecture should include.

## J1-Q04 — Final recommendation defense [Advanced | ADR | Topics 01–08]

Write a concise recommendation for Northbridge that is defensible even if there is no universal provider winner. Compare three provider realizations using identical criteria; state the strongest evidence, unknowns, major provider-specific dependencies, security/connectivity controls, operating model, cost drivers, exit path, IaC strategy, and what would change your recommendation. Distinguish facts, assumptions, and research items.

---

# Answer key and evaluation rubrics

> **Stop here until you have attempted the questions.** The solutions below are reference answers. Provider services and capabilities should be verified against the relevant topic lesson and current official documentation before implementation.

## Section A — Answer key

### A1-Q01 — Shared responsibility

**Expected answer: C.** Managed services reduce the customer's responsibility for underlying infrastructure, but do not remove customer responsibility for identity configuration, data classification, permissions, retention, workload settings, and correct use. The exact split varies by service and service model.

- **Why other options fail:** A overstates provider responsibility; B assigns physical data-centre duties incorrectly; D wrongly implies every control is jointly administered.
- **Scoring:** 4 for C; 0 otherwise.

### A1-Q02 — Deployment models

**Expected answer: False.** Hybrid and multi-cloud can reduce a specific concentration risk only if the architecture, failover, data synchronization, and operations actually support it. They also add failure modes: interconnect outages, duplicated identity/governance, inconsistent policy, cross-cloud latency/egress, and unfamiliar recovery procedures. A single-cloud design with multi-zone resilience and a tested exit plan may be more reliable for a given team.

- **Common misconception:** counting providers instead of analyzing failure domains and tested recovery.
- **Scoring:** 2 points for false; 1 for two valid operational considerations; 1 for explaining that resilience depends on design and testing.

### A1-Q03 — Residency and failure domains

**Expected answer — at least five of:**
1. primary service region and actual regional availability;
2. backup, replica, snapshot, log, and disaster-recovery locations;
3. replication defaults and cross-region copies;
4. data-processing location and temporary/staging storage;
5. metadata/catalogue location where it can contain sensitive values;
6. support access, administrative access, and contractual/legal scope;
7. encryption and key custody/location;
8. network paths, exports, and downstream consumers;
9. service-specific residency terms and applicable regulation;
10. audit evidence showing actual configuration.

A primary region alone is insufficient because replicas, backups, processing, or exports may leave the jurisdiction. Residency requirements should be translated into service-specific controls and verified evidence.

- **Rubric (4):** 1 point for at least five relevant checks; 1 for replicas/backups; 1 for processing/exports; 1 for verification/evidence and no unsupported guarantee.

### A1-Q04 — Cost drivers

**Expected examples and evidence:**

| Possible driver | Evidence to collect |
|---|---|
| More queries or larger scans | Query logs, bytes scanned, workload counts |
| Compute scaling or longer runtime | Job duration, utilization, scaling history |
| Retries or failed jobs | Orchestration logs, retry counts, failure rate |
| Cross-region or cross-cloud transfer | Network/egress billing records and flow volumes |
| More requests/list operations | Storage request metrics and application logs |
| New replicas, backups, or retention | Storage inventory, lifecycle and replication settings |
| Idle clusters or always-on capacity | Utilization and uptime reports |
| Private endpoints, NAT, gateways, or dedicated links | Network resource inventory and billing dimensions |
| Premium support or license/commitment changes | Invoice line items and contract changes |
| Data growth hidden by compression or tier shifts | Metered bytes by storage class and lifecycle |

The answer should not recommend deleting data or disabling resilience controls solely because a bill rose. First attribute the change to a measured driver and check workload/business impact.

- **Rubric (4):** 3 points for six plausible driver/evidence pairs; 1 for a safe evidence-led recommendation.

### A1-Q05 — Availability and recovery

**Expected answer:** Convert 99.5% into a measurable service objective and clarify measurement window, exclusions, business hours, dependencies, and user-visible success. For a 30-day month, 0.5% of 30 days is `0.005 × 30 × 24 = 3.6 hours` of unavailability in that month if measured continuously; if the objective is only during defined business hours, calculate against those hours instead.

- **Availability:** proportion of time the service meets the defined availability criterion.
- **Durability:** probability that stored data is not lost/corrupted over a stated period; distinct from access availability.
- **Resilience:** ability to withstand or recover from failures.
- **RTO:** target maximum time to restore service after disruption.
- **RPO:** target maximum acceptable data-loss window measured in time.

Architecture questions include zone failure, dependencies, data replication, restore paths, monitoring, alerting, and tested recovery. A component SLA does not prove end-to-end platform availability because integrations and customer configuration can fail.

- **Rubric (4):** 1 point for the 3.6-hour continuous-month calculation and caveat; 2 for correct definitions; 1 for end-to-end evidence/testing.

## Section B — Answer key

### B1-Q01 — Capability-first mapping

**Expected answer: B.** Requirements and logical capabilities should precede product selection. Then verify feature semantics, operational responsibilities, permissions, integration, cost, limits, and portability. A service count is not an architecture quality metric.

### B1-Q02 — Trace an AWS flow

**One defensible illustrative flow:** on-premises source → controlled batch transfer or ingestion mechanism → Amazon S3 landing zone → transformation with an appropriate managed or cluster-based compute service (for example AWS Glue or Amazon EMR, depending on workload) → curated S3 datasets and/or an analytical serving system such as Amazon Redshift → SQL query path such as Amazon Athena where suitable → catalog/governance and IAM policies → audit and monitoring. Orchestration may use AWS Step Functions or Amazon MWAA depending on workflow requirements. This is a candidate pattern, not a claim that all listed services are necessary.

**Checks (at least four):**
- encryption and key permissions;
- workload IAM scoped to required resources/actions;
- private path and DNS/network policy where required;
- schema/data-quality validation and idempotent retries;
- source-arrival monitoring and late-file handling;
- catalogue permissions and direct-storage access controls;
- query/compute/egress cost telemetry;
- recovery and retention policies.

**Rubric (4):** 1 for a coherent end-to-end flow; 1 for explaining capability responsibilities; 1 for four valid checks; 1 for explicitly verifying provider-specific details and avoiding a service-list-only answer.

### B1-Q03 — Processing and governance trade-off

**Expected answer:** The ADR should first describe workload shape, latency/freshness, language/runtime, data volume, security, team skill, and budget. A managed/serverless path can reduce cluster operations and fit bursty demand but may have service-specific limits, billing behavior, and lock-in. A cluster-based path may suit custom dependencies, sustained jobs, or framework control but adds sizing, patching, capacity, and idle-cost concerns. Compare the same representative workload and include governance, private access, observability, retry semantics, and failure recovery. Choose based on measured requirements, not a universal rule.

**Rubric (4):** 1 for context/requirements; 1 for balanced options; 1 for security/operations/cost; 1 for a revisit trigger or evidence that could change the decision.

### B1-Q04 — AWS reliability and cost diagnosis

**Expected ordered sequence:**
1. Confirm the freshness SLO and exact late interval; check orchestration state and dependencies.
2. Check source arrival and completeness before compute starts.
3. Inspect job logs, retry patterns, throttling, quotas, and service health.
4. Compare input size and partition distribution; investigate skew and small-file overhead.
5. Check network/DNS/permissions for intermittent access.
6. Inspect runtime, utilization, queueing, and bottlenecks before resizing.
7. Attribute cost to runtime, retries, scans, data movement, and idle resources.
8. Apply the smallest evidence-supported change in a non-production environment; verify success and regressions.

Doubling compute can increase cost without fixing late source files, throttling, skew, or dependency failure.

- **Rubric (4):** 1 for checking upstream/orchestration; 1 for quotas/retries/data shape; 1 for network/security and cost evidence; 1 for controlled change and verification.

## Section C — Answer key

### C1-Q01 — Identity and storage

**Expected answer: B.** Prefer an appropriate managed/workload identity and narrowly scoped role. Network reachability, authentication, authorization, and service-side network rules are separate checks. Do not embed long-lived keys, make the storage public, or grant broad administrator rights to bypass diagnosis.

### C1-Q02 — Azure capability map

**Plausible mappings to verify:** Azure Data Lake Storage Gen2 for object/data-lake storage; Azure Data Factory for orchestration and ingestion; Azure Databricks or an appropriate Azure analytics/Spark capability for Spark processing; Azure Synapse Analytics or Microsoft Fabric analytical capabilities depending on requirements; Microsoft Entra ID and managed identities for identity; Microsoft Purview and/or current catalogue/governance capabilities for governance. These are candidate families, not automatic equivalents.

**Differences to investigate:** account/subscription/resource-group scope; hierarchical namespace and access-control behavior; managed identity support and scope; private endpoint and DNS behavior; orchestration connectors and retry semantics; catalogue/lineage coverage; query pricing and workload isolation; regional availability; service lifecycle/renaming; direct data-plane access paths.

**Rubric (4):** 2 for plausible capability mappings; 1 for meaningful differences; 1 for labeling verification needs rather than claiming equivalence.

### C1-Q03 — Integrated platform trade-off

**Expected answer:** An integrated platform can shorten initial delivery, simplify user experience, and align with existing identity/skills, but can couple data, governance, processing, and serving to a vendor-specific control plane and commercial model. A composed design can offer component choice and clearer boundaries but requires more integration, observability, access-policy consistency, and operational ownership. Compare total cost (including staff and network), required workloads, data location, private connectivity, governance, failure domains, exit needs, and team capacity. Verify current feature boundaries, licensing/pricing, regional support, identity flows, and export interfaces before deciding.

**Rubric (4):** 1 for balanced options; 1 for identity/governance/operations; 1 for portability/cost; 1 for explicit verification and conditions that would change the recommendation.

## Section D — Answer key

### D1-Q01 — GCP data flow

**Expected answer: B.** Serverless does not eliminate design for data location, partitioning, access control, quota, cost, recovery, or portability. Map the logical capability first and verify the actual service behavior.

### D1-Q02 — Location and cost

**Expected questions include:**
- Which region or multi-region location is supported for each resource?
- Do datasets, backups, processing outputs, logs, and exports meet residency requirements?
- What identity and service-account permissions allow each stage?
- Is private access configured and does DNS resolve to the intended address?
- Is warehouse pricing based on scanned data, capacity, or another model, and what controls limit spend?
- What processing and streaming units are billed?
- What data moves between regions/services/providers and what are the costs/latency?
- Are quotas, retries, partitioning, clustering, and retention configured for the workload?
- What is the recovery path and what are the RTO/RPO?

**Rubric (4):** 2 for five relevant questions; 1 for cost and movement; 1 for residency/security/reliability coverage.

### D1-Q03 — Provider-specific warehouse dependency

**Expected answer:** Quantify the feature's delivery/performance/business value and its usage scope. Compare with a portable SQL/data-processing alternative, keep raw/curated data in suitable open formats where practical, document SQL extensions and transformation dependencies, estimate rewrite and validation effort, and decide whether the feature's benefit justifies the residual exit cost. Record security, governance, staff skill, and operational implications. “Open format” mitigates some data-layer lock-in but does not automatically port SQL semantics, IAM, orchestration, catalogue, or monitoring.

**Rubric (4):** 1 for explicit value; 1 for exit/dependency analysis; 1 for mitigations with residual limitations; 1 for ADR alternatives and revisit triggers.

## Section E — Answer key

### E1-Q01 — Fair comparison

**Expected answer: False.** The category label does not prove identical consistency, lifecycle/tiering, request behavior, IAM semantics, encryption/key integration, region model, endpoint/DNS behavior, limits, pricing, or replication. Use the same workload and requirements for all providers, consult current official documentation, record source date, and label unknowns as research items.

### E1-Q02 — Comparison matrix

**Expected answer:** A complete matrix uses identical logical rows for all providers and records evidence or research items. A good row does not merely list product names; it includes:
- capability and workload requirement;
- candidate service and why it fits;
- behavior/limits to verify;
- network and identity boundary;
- pricing unit and cost drivers;
- provider-specific dependencies/exit impact;
- evidence source and date;
- unresolved research item and owner.

**Rubric (4):** 1 for consistent capability-first rows; 1 for network/identity and behavior; 1 for cost/portability; 1 for evidence/date and explicit unknowns. Do not award full credit for a product-name-only table.

### E1-Q03 — Equivalence claim review

**Expected dimensions include:** APIs/SDKs; data format and metadata; consistency and transaction semantics; batch/CDC/stream delivery guarantees; SQL dialect and query behavior; identity and permission model; private networking/DNS; regional and residency behavior; quota/throughput limits; scaling model; failure/retry semantics; observability/audit; cost unit and egress; backup/restore and DR; governance/catalogue/lineage; operational skills and service lifecycle.

Service-category similarity establishes only a broad capability overlap. Migration can still require data conversion, code changes, policy redesign, network changes, validation, and a different operating model.

- **Rubric (4):** 2 for eight or more dimensions; 1 for explaining semantic differences; 1 for an evidence-based migration test plan.

### E1-Q04 — No clear winner

**Expected answer:** This is sound when providers meet must-have requirements but evidence, workload-specific performance, total cost, skills, or risk scores differ only within uncertainty—or when each has material trade-offs. Fix criteria before scoring; use the same workload and assumptions; keep a research log with question, impact, owner, source needed, and decision deadline. Do not assign arbitrary scores to unknowns or conceal a tie with false precision.

**Rubric (4):** 1 for conditions; 1 for consistent comparison; 1 for transparent uncertainty; 1 for research ownership and decision impact.

## Section F — Answer key

### F1-Q01 — Reachability versus permission

**Expected answer: C.** A successful TCP connection is evidence for part of the network path, not proof of identity authorization. Inspect caller identity/token, requested action, resource scope, policy conditions, and service-side access policy. Do not widen access to administrator scope as a first fix.

### F1-Q02 — CIDR arithmetic

A `/24` leaves `32 − 24 = 8` host bits. Total addresses are `2^8 = 256`. Some cloud providers reserve addresses for network/service purposes, so usable addresses can be fewer; the exact reservation behavior is provider- and subnet-specific and should be checked in current documentation.

- **Scoring:** 2 for correct exponent/total; 1 for units/context; 1 for cloud reservation caveat.

### F1-Q03 — Diagnose private access

**Expected sequence:**

| Layer | First checks | Typical symptom |
|---|---|---|
| Name resolution | Resolve the service FQDN from the workload environment; inspect private DNS zone/link/forwarding | Wrong/public IP, NXDOMAIN |
| Network path | Routes, firewall/security rules, endpoint/subnet, peering, return route | Timeout or unreachable |
| Authentication | Token acquisition, identity, expiry, audience/issuer | 401 or credential/token error |
| Authorization | Role/policy scope, action, resource, conditions, deny rules | 403/access denied |
| Service-side network rules | Storage/service firewall, approved network/source, perimeter policy | Service rejects source despite a route |

Start with low-cost, non-invasive checks; compare a known-good path; change one control at a time and record evidence. A timeout is not automatically a permission issue, and a 403 is not automatically a routing issue.

### F1-Q04 — Least-privilege role design

**Expected answer:** Use a dedicated workload identity per application/environment. Grant read/list only on the required raw prefix or dataset and write permissions only to the curated destination. Separate key-management rights from data permissions; grant decrypt/encrypt rights only if the workflow requires them. Use private access where required, DNS and route controls, service-side restrictions, audit logs, and short-lived/federated credentials. Separate development and production identities and data. Do not grant account/subscription/organization admin, broad wildcard resource access, public access, or key-administration permissions by default.

**Rubric (4):** 1 for identity/environment separation; 1 for scoped read/write actions; 1 for network/encryption/audit controls; 1 for explicit denied-by-default privileges and credential handling.

## Section G — Answer key

### G1-Q01 — VPN versus dedicated connectivity

**Expected answer:** A site-to-site VPN typically uses encrypted tunnels over an existing network/internet path and can be quicker or lower initial cost, but performance can vary and throughput depends on tunnel/device/service limits. Dedicated private connectivity uses a provider/partner circuit and may offer more predictable path characteristics but often has longer lead time, recurring cost, and still needs resilient design. Both require routing, CIDR planning, DNS, monitoring, and failover testing. Do not assume the dedicated path is automatically encrypted end-to-end; define encryption based on threat model and service requirements. Neither path grants data access: IAM and service authorization remain separate.

### G1-Q02 — Transfer-time calculation

Given:
- Data = `20 × 10^12 bytes`
- Bits = `20 × 10^12 bytes × 8 bits/byte = 160 × 10^12 bits`
- Effective throughput = `1 × 10^9 bits/s × 0.70 = 0.70 × 10^9 bits/s`

Time:

`160 × 10^12 bits ÷ (0.70 × 10^9 bits/s) = 228,571.43 s`

`228,571.43 s ÷ 3,600 s/hour = 63.49 hours`

`63.49 hours ÷ 24 hours/day = 2.645 days`, approximately **2.65 days**.

Real-world limitations include retransmissions and protocol overhead, competing traffic, source/target throughput limits, file count and request latency, encryption/compression CPU, link outages, and throttling. The 70% assumption is an average utilization assumption, not a guarantee.

### G1-Q03 — Hybrid failure matrix

**Expected response:**
1. Declare/triage the link outage; preserve CDC offsets/checkpoints and monitor source retention capacity.
2. Verify alternate path and routing state; do not change multiple routing variables without evidence.
3. Diagnose private DNS after failover: resolver path, private-zone links/forwarding, record target, TTL/caches.
4. Restore a valid route and private name resolution; verify authentication and authorization separately.
5. Resume CDC from a known checkpoint using the connector's documented semantics.
6. Reconcile source change positions/counts against destination checkpoints; detect duplicates, gaps, and out-of-order events.
7. Confirm idempotent sink behavior and downstream freshness before closing the incident.
8. Assign network/DNS ownership, source database/CDC ownership, cloud platform ownership, and data product owner for reconciliation/business validation.

Blind replay can create duplicates, overwrite newer state, violate ordering, or replay changes outside retention/checkpoint guarantees. Recovery must follow the actual CDC connector and sink semantics.

**Rubric (4):** 1 for safe triage and DNS/network recovery; 1 for checkpoint/replay safety; 1 for reconciliation; 1 for named operational owners and closure evidence.

### G1-Q04 — Connectivity decision

**Initial transfer calculation:** same as G1-Q02: about `228,571 s = 63.49 h = 2.65 days` at 1 Gbit/s and 70% utilization.

**Defensible answer:** A staged approach may use a tested VPN for early development/initial transfer if its measured throughput and security meet requirements, while planning dedicated connectivity if daily change volume, stable latency, or availability needs justify it. Alternatively, dedicated connectivity may be appropriate from the outset if the near-real-time target and link-failure requirement are strict and budget/lead time allow. Either design needs redundant paths, route failover, DNS validation, CDC buffering, monitoring, and recovery tests. The stated transfer calculation concerns the bulk historical load, not the p95 freshness of each fraud feature.

**Revisit triggers:** measured utilization/latency, backlog growth, repeated outages, missed freshness SLOs, source retention constraints, transfer-cost break-even, or compliance requirements.

**Rubric (4):** 1 for correct calculation; 1 for trade-off comparison; 1 for redundancy/failure handling; 1 for explicit measurements and conditions that change the design.

## Section H — Answer key

### H1-Q01 — Portability layers

**Examples (any six):**
- Data files: proprietary serialization or inaccessible exports.
- Table/transaction metadata: catalog formats, snapshots, transaction semantics.
- Schema: incompatible type/constraint behavior.
- Processing code: proprietary APIs or runtime extensions.
- SQL/warehouse: dialect, functions, stored procedures.
- Orchestration: provider-specific workflow definitions/connectors.
- Streaming: broker APIs, ordering/delivery guarantees, schema registry.
- Identity/governance: roles, policy tags, lineage and audit semantics.
- Networking: private endpoints, DNS, routing, firewall models.
- Observability/operations: provider-specific metrics, logs, alerts.
- Infrastructure automation: provider-specific resource definitions.
- AI/ML: proprietary feature, model, or serving APIs.
- Commercial/legal: export terms, support, region constraints.

Portability is per layer, not a binary property.

### H1-Q02 — Egress estimate

`50 TB` decimal = `50,000 GB` under the stated assumption.

`50,000 GB × $0.09/GB = $4,500`.

This is only an illustrative arithmetic exercise. It is not a provider quote: actual pricing can depend on destination, route, region, volume tiers, contract, free allowances, and time. It omits engineering, temporary duplicate storage, compute, validation, downtime, network circuits, licenses, support, staff, and application rewrite. Confirm whether the pricing unit is decimal GB and whether the assumed rate applies before using it in a decision.

### H1-Q03 — Single, hybrid, or multi-cloud

**One defensible recommendation:** use one primary public cloud for the analytics platform, maintain the ledger on premises during the stated three-year transition, and reduce avoidable exit friction through open data formats, documented provider-specific dependencies, exportable metadata where feasible, least-privilege identity design, infrastructure definitions, and a tested exit plan. This is not “single cloud only” in the sense of moving the ledger immediately; the scenario already imposes a hybrid period. Distributed multi-cloud is not justified without a requirement for active multi-provider operation because it adds duplicated governance, skills, data movement, failure handling, and cost.

**Would change if:** a regulator mandates active dual-cloud operation, a business continuity requirement cannot be met within one provider, a specific workload has a proven provider requirement, acquisition constraints force separate platforms, or measured concentration risk outweighs operating complexity.

**Rubric (4):** 1 for explicit assumptions; 1 for comparison of all three options; 1 for cost/skills/data movement; 1 for a clear recommendation and revisit triggers. Other recommendations can score fully if evidence-backed.

### H1-Q04 — Data gravity and exit planning

**Expected steps:** inventory resources and service-specific dependencies; export raw/curated data and verify checksums/counts; export schemas and metadata/catalogue/lineage where possible; recreate identity and least-privilege roles; establish network/DNS/private access; port processing and orchestration; validate query semantics and data quality; run parallel reconciliation; plan cutover and rollback; document RTO/RPO, owners, costs and time ranges; test at a defined cadence.

Parquet is a file format, not a complete platform contract. It does not automatically port SQL, table transactions, catalogue metadata, access policy, orchestration, streaming semantics, audit, monitoring, networking, or operational skills.

**Rubric (4):** 2 for a coherent sequence across data/code/metadata/identity/network; 1 for reconciliation/cutover/rollback; 1 for owners, cost/time ranges and test cadence.

## Section I — Answer key

### I1-Q01 — Declarative and imperative IaC

**Expected answer: A.** Declarative definitions state desired properties; imperative automation specifies actions/steps. Both need review, access controls, error handling, state/observability appropriate to the tool, and recovery planning. Neither style automatically prevents drift or outages.

### I1-Q02 — State, drift, and concurrency

- **Desired state:** what the code/configuration says should exist.
- **Actual state:** what exists in the provider at the moment.
- **State file/backend:** the IaC tool's record of managed objects and their relationship to configuration; it may contain sensitive data.
- **Drift:** actual configuration differs from declared/recorded state due to manual changes, external automation, or changed defaults.
- **Reconciliation:** inspect differences and intentionally bring code or infrastructure into a consistent state.
- **Idempotency:** repeated execution with the same inputs converges on the same intended outcome rather than producing duplicate side effects.
- **State locking:** coordination that prevents conflicting operations against the same state when supported by the backend/tool.

Concurrent uncoordinated applies can race, overwrite state updates, create duplicate or conflicting resources, produce misleading plans, and make recovery harder. Use supported locking, pipeline concurrency controls, reviewable plans, backups, and scoped state.

### I1-Q03 — Code review

**Defects:**
1. Public access is enabled without a requirement.
2. Encryption is disabled.
3. Wildcard/admin privileges violate least privilege.
4. A real-looking secret is hardcoded and may be exposed in source history/logs.
5. One environment setting (`all`) risks accidental cross-environment changes.
6. No resource naming, region, retention, logging, ownership tags, or policy controls.
7. No state, review, plan, or deployment workflow.
8. No network/private-access or data-residency requirements.
9. No lifecycle/backup/recovery plan.
10. No validation or post-deployment verification.

**Safe principles:** default deny/public access disabled; provider-managed encryption or approved key configuration; dedicated environment-specific workload identity with scoped actions/resources; secrets manager or federated short-lived credentials; typed and validated environment variables; required tags; policy-as-code checks; protected state; reviewed plan; approvals for production; and recovery controls.

### I1-Q04 — Promotion and recovery

**One defensible workflow:**
1. Change code on a branch; open a pull request with linked requirement/issue and risk classification.
2. Run formatting, syntax/validation, security and policy checks, module-interface tests, and static analysis.
3. Peer review the diff and generated plan/preview; inspect replacement/deletion actions and cost/security changes.
4. Merge a reviewed commit; pin tool/provider/module versions and promote the same versioned code artifact.
5. Apply first in development, then test and staging using separate environment identities/configuration and non-production data.
6. Run smoke tests, security checks, data-flow tests, and evidence capture.
7. Production apply requires the correct approver, restricted apply identity, recorded plan/context, and change window as appropriate.
8. Verify actual resources, access paths, monitoring, cost tags, and workload health.
9. Detect drift continuously or on a scheduled basis; alert and reconcile through a reviewed change.
10. For emergencies, use audited break-glass with a named approver, limited duration, incident record, and mandatory code reconciliation afterward.

**Rollback caution:** reverting infrastructure code may not undo schema migrations, data deletion, messages already emitted, or changed data. Use backups, compatible migrations, data reconciliation, and a tested recovery plan. Prefer forward fixes where reversal is unsafe.

**Rubric (4):** 1 for review/validation/plan; 1 for isolated environments and promotion; 1 for least privilege/audit/drift; 1 for data-aware rollback and emergency reconciliation.

### I1-Q05 — State-security scenario

**Expected answer:** Do not delete the state file as a first response. It may be the only reliable mapping between managed resources and the tool; deleting it can cause resource recreation, orphaning, or destructive plans. First stop overlapping runs, inspect backend lock owner/lease and logs, confirm whether the original process is still active, inspect backend versioning/backups, and verify the state is readable and consistent. Follow the tool/backend's documented lock-recovery process only after establishing the lock is stale. Restore from a known-good backup only after assessing changes since that backup. Re-run a plan/refresh/validation and carefully reconcile real resources; do not blindly apply a plan with replacements/deletions. Preserve audit evidence and rotate credentials if state exposure is suspected.

State controls should include encryption, strict backend access, versioning/backups, audit logging, minimal read access, no public exposure, and concurrency controls. State can contain sensitive attributes even if the source code contains no secrets.

- **Rubric (4):** 1 for avoiding deletion; 1 for lock/owner/run investigation; 1 for backup and careful reconciliation; 1 for security/audit safeguards.

## Section J — Answer key

### J1-Q01 — Northbridge Bank integrated exercise

**A strong answer should include the following, while accepting defensible alternatives:**

1. **Requirements and assumptions:** in-country location for regulated data, private access, no long-lived keys, ledger remains on premises for three years, the first-wave 20 TB historical load, 2 TB/day CDC/change volume, 30% annual compounded net estate growth, fraud-feature p95 ≤60 seconds, stated availability/recovery needs, team skills, and cost/exit constraints. Calculate the three-year planning volume as `250 TB × 1.3³ ≈ 549.25 TB` before any separately modelled retention, compression, deduplication, or other assumptions. Do not treat the 2 TB/day CDC volume as net growth. Separate facts from assumptions and open research items.
2. **Logical architecture:** source ledger → batch historical load and CDC/stream path → landing/raw storage → validation/transformation → curated data products/analytical serving → BI/ML/fraud consumer; include catalogue/governance, identity, monitoring, and control-plane responsibilities.
3. **Two provider maps:** use the same logical capabilities and workload requirements for both providers. Mark unverified regional/service behaviors and pricing as research items.
4. **Access path:** document name resolution, network route/rules, authentication, authorization, and service-side network controls for each sensitive path.
5. **Transfer:** the first-wave 20 TB over 1 Gbit/s at 70% efficiency is about 228,571 seconds, 63.49 hours, or 2.65 days, before real-world overhead. This does not estimate the transfer time for the full 250 TB estate or its remaining 230 TB; estimate those separately for the migration plan.
6. **Portability:** assess data format, table metadata, SQL/processing, orchestration, identity/governance, networking, observability, and infrastructure definitions separately. State residual limitations.
7. **IaC:** separate dev/test/staging/prod boundaries; reviewed plan; controlled apply identity; production approval; drift alert/reconciliation; protected state; emergency path and code follow-up.
8. **ADR:** compare single primary cloud with a tested exit plan against multi-cloud; state criteria and conditions that would change the decision.
9. **Risk register:** include owner, likelihood/impact, mitigation, residual risk, evidence, and review date.

**Rubric (20 points recommended):** 2 requirements/assumptions; 2 logical diagram and traced flow; 3 provider mapping/evidence; 3 network/identity five-layer path; 2 correct transfer arithmetic; 2 per-layer portability/exit; 2 IaC promotion/drift; 2 ADR and risk ownership. Full credit requires a coherent trace from ledger record to a consumer, not just a list of services. No live deployment is required.

### J1-Q02 — Transfer arithmetic and throughput

Transfer time from G1-Q02 is:

- Bits: `20 × 10^12 bytes × 8 = 160 × 10^12 bits`.
- Effective throughput: `1 × 10^9 bit/s × 0.70 = 0.70 × 10^9 bit/s`.
- Time: `160 × 10^12 ÷ (0.70 × 10^9) = 228,571.43 s`.
- Hours: `228,571.43 ÷ 3,600 = 63.49 h`.
- Days: `63.49 ÷ 24 = 2.645 days`, approximately **2.65 days**.

Theoretical daily capacity at the same effective throughput:

`0.70 × 10^9 bit/s × 86,400 s/day ÷ 8 bit/byte = 7.56 × 10^12 bytes/day = 7.56 TB/day` (decimal).

This is a sustained average transfer estimate, not a latency guarantee. A ≤60-second p95 fraud-feature objective depends on event capture, delivery, processing, queueing, stateful computation, sink latency, and end-to-end monitoring. Bulk-transfer capacity cannot prove event-level freshness.

### J1-Q03 — Architecture review panel

| Claim | Corrected statement | Evidence/control |
|---|---|---|
| Managed provider means customer no longer owns security | Provider/customer responsibilities vary by service; customer still configures identity, data access, settings, and workload behavior | Responsibility matrix, access review, audit evidence |
| Private endpoint means pipeline is authorized | Endpoint helps define network path; identity and resource permissions remain separate | Five-layer access-path table and denied/allowed tests |
| Open formats make platform fully portable | Open formats help data-layer portability; SQL, metadata, identity, orchestration, network, governance, and operations can remain coupled | Dependency inventory and exit rehearsal |
| Two clouds automatically reduce risk | Additional clouds can reduce a specific concentration risk only if failover and operating model are real; they add synchronization and governance risks | Risk model, recovery test, cross-cloud cost/latency model |
| IaC makes changes safe without review | IaC improves repeatability and traceability but can consistently deploy unsafe changes | PR review, policy checks, plan review, approvals, post-apply verification |

**Rubric (4):** 1 for correctly challenging all five claims; 1 for corrected statements; 1 for evidence/control; 1 for recognizing residual risk rather than claiming guarantees.

### J1-Q04 — Final recommendation defense

**Expected structure, not a single prescribed provider winner:**
- State the decision and the requirements it satisfies.
- Compare AWS, Azure, and GCP using the same capability rows, workload assumptions, security requirements, cost dimensions, and evidence standard.
- Separate verified facts, assumptions, and research items.
- Explain identity and private access using the five-layer model.
- Describe hybrid ingestion and CDC recovery, including link failure and reconciliation.
- Inventory provider-specific dependencies by layer and estimate exit time/cost as ranges with stated assumptions.
- Define environment isolation, versioned IaC modules, state protection, production approvals, drift policy, and break-glass reconciliation.
- List residual risks and owners.
- State what would change the recommendation, including the legitimate possibility that no provider is clearly best yet.

**Rubric (12 points recommended):** 2 for requirement traceability; 2 for fair three-provider comparison; 2 for security/connectivity; 2 for portability/exit and cost; 2 for IaC/operations; 2 for assumptions, evidence, risks, and revisit triggers. Award full marks to any defensible recommendation that applies consistent criteria and makes uncertainty explicit.

---

## Study, remediation, and reassessment

### Recommended study sequence

Follow the roadmap's ordering and topic gates:

1. After **Topic 01**, attempt Section A closed-book.
2. After **Topic 02**, attempt Section B.
3. After **Topic 03**, attempt Section C.
4. After **Topic 04**, attempt Section D.
5. After Topics **02–04**, complete Section E as a mixed-provider comparison.
6. After **Topic 05**, attempt Section F.
7. After **Topic 06**, complete Section G, including transfer calculations and failure handling.
8. After Topics **07–08**, attempt Sections H and I.
9. Complete Section J as the integrated exercise connecting principles, provider mappings, networking, hybrid connectivity, portability, and IaC.
10. Attempt the full assessment before starting `Projects/08-cloud-platform-architecture-comparison.md`. Reattempt missed questions after reviewing the matching lesson.

### Marking and reassessment method

For every question, mark **Correct / Partly correct / Wrong** and write a one-sentence reason. For an incorrect answer:
1. identify the specific misconception;
2. revisit the relevant lesson and roadmap completion gate;
3. redo the related exercise or diagram without copying the answer key;
4. reattempt after several days;
5. record evidence that the gap is closed.

Two consecutive failures on the same concept indicate that the learner should redo the relevant topic exercise, not simply memorize the answer.

### Gap-log template

| Question ID | Topic | Result (C/P/W) | Misconception or missing evidence | Remediation task | Reassessment date | Status / evidence |
|---|---|---|---|---|---|---|
| A1-Q03 | 01 Principles |  |  | Revisit residency and failure-domain checklist; update evidence list |  |  |
| F1-Q03 | 05 Networking |  |  | Complete five-layer troubleshooting matrix for a second scenario |  |  |
| G1-Q02 | 06 Hybrid |  |  | Recalculate with units and independently check conversions |  |  |
| I1-Q05 | 08 IaC |  |  | Write a state recovery runbook with backup and lock checks |  |  |

**Recommended project-readiness thresholds — learning guidance, not an external certification or industry standard:**
- At least **85% overall** on the full assessment.
- No topic below **70%**.
- All **eight topic gates** completed.
- The integrated architecture exercise in Section 7.4 of the roadmap completed.
- No unresolved gap-log item older than **one week**.

These thresholds supplement, rather than replace, reviewed deliverables and the roadmap's module completion criteria.

---

## Final project readiness checklist

Before beginning `Projects/08-cloud-platform-architecture-comparison.md`, confirm:

- [ ] All eight topic gates are signed off with evidence; reading alone is not mastery.
- [ ] I can explain cloud shared responsibility, failure domains, residency, resilience, and cost drivers.
- [ ] I can map logical data-platform capabilities to AWS, Azure, and GCP without assuming service equivalence.
- [ ] My comparison criteria are fixed before scoring; unknowns are research items with owners and source dates.
- [ ] I have a logical, provider-neutral architecture and at least two provider-specific mappings.
- [ ] I can describe each access path using name resolution, network route, authentication, authorization, and service-side network rules.
- [ ] I can design hybrid connectivity at concept level, calculate transfer time with units, and explain link/DNS/CDC recovery.
- [ ] I have a per-layer portability/dependency inventory, an exit-plan outline, and egress/exit-cost ranges with assumptions.
- [ ] I can explain IaC, state, locking, drift, secrets, environment separation, review/approval, promotion, and data-aware rollback.
- [ ] My design distinguishes architecture documentation, IaC definitions, and actual deployment/operation.
- [ ] I have a decision record with alternatives, rationale, trade-offs, residual risks, and revisit triggers.
- [ ] The integrated exercise is complete and the evidence traces a record from on-premises source to a consumer.
- [ ] The assessment reaches the recommended thresholds and the gap log has no unresolved item older than one week.
- [ ] I can defend the recommendation to a security reviewer and a finance reviewer, including what could change the decision.
- [ ] No paid cloud deployment is required to satisfy this assessment.

**Completion standard:** A defensible assessment answer links requirements to design, explains why alternatives were accepted or rejected, states assumptions, identifies evidence and residual risk, and does not claim that a design has been deployed or tested unless it has.


## Official documentation references for fact-sensitive checks

These primary-source references support examples and troubleshooting concepts in this assessment. They do not establish that a specific architecture is deployed, that a particular SKU/region supports a feature, or that a price applies to a learner's account. Recheck the current documentation and exact configuration before implementation. Reviewed on **2026-10-20**.

- AWS, [Amazon S3 security best practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html) — block public access, least privilege, and application roles/temporary credentials.
- AWS, [Amazon S3 access control](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-management.html) — identity- and resource-based authorization and object access.
- Microsoft Learn, [Authorize requests to Azure Storage](https://learn.microsoft.com/en-us/rest/api/storageservices/authorize-requests-to-azure-storage) — Microsoft Entra ID/managed identity authorization guidance.
- Microsoft Learn, [About active-active VPN gateways](https://learn.microsoft.com/en-us/azure/vpn-gateway/about-active-active-gateways) — Azure VPN topology requirements and failover behavior.
- Google Cloud, [Cloud VPN overview](https://docs.cloud.google.com/network-connectivity/docs/vpn/concepts/overview) and [HA VPN topologies](https://docs.cloud.google.com/network-connectivity/docs/vpn/concepts/topologies) — topology-dependent routing and availability characteristics.
- HashiCorp, [Terraform state locking](https://developer.hashicorp.com/terraform/language/state/locking) and [managing sensitive data](https://developer.hashicorp.com/terraform/language/manage-sensitive-data) — state-locking caveats and sensitivity of state/plan files.

Provider features, service names, prices, regional support, quotas, and SKUs can change. The assessment intentionally treats unresolved provider-specific facts as research items rather than asserting equivalence.
