# Practice Questions — Data Governance, Security, Privacy and Compliance

> **Stage:** 2D — Data Architecture  
> **Module:** 10 — Data Governance, Security, Privacy and Compliance  
> **Scope:** Topics 01–09  
> **Target:** `10-Data-Governance-Security-Privacy-and-Compliance/practice-questions.md`

## Source alignment and scope

This assessment is based primarily on `roadmap-Data-Governance-Security-Privacy-and-Compliance.md`, with the overall curriculum dependencies and target folder/file names grounded in `Roadmap_ptree.md`. The module roadmap identifies `practice-questions.md` as empty and proposes a study method, readiness threshold, classification-to-control exercise, supplementary control-validation exercises, and a sensitive-data governance/access-design capstone shape. This document creates a new assessment consistent with that scope; it does not claim these questions previously existed.

The nine lesson documents were available for inspection. The project file `Projects/10-sensitive-data-governance-and-access-design.md` is named in the tree, but its contents were not available for inspection. Section F therefore follows the **integration goal described by the module roadmap**, not any uninspected project-specific instructions.

**Legal and compliance boundary:** Northbridge Bank scenarios and data are fictional and synthetic. Requirements and numeric values are illustrative unless explicitly described as a general engineering concept. This assessment is not legal advice and does not establish that a design satisfies a particular law, regulation, contract, or standard. Qualified specialists must interpret real obligations.

## How to use this assessment

1. Answer the topic-aligned questions closed-book after each lesson.
2. After Topics 01–03, review governance, classification and access together; after Topics 04–07, review protection, privacy and lifecycle; after Topics 08–09, review evidence and enforcement.
3. Complete the practical exercises using synthetic data, then attempt the integrated assessment before the capstone.
4. Mark responses **Correct**, **Partly correct**, or **Incorrect**, with a one-sentence reason. For design questions, score reasoning, assumptions, accountable roles, failure handling and testable evidence—not agreement with a single vendor choice.

---

## Requirements traceability — module learning outcomes

The module roadmap documents ten module-level learning outcomes. The matrix below maps each outcome to the assessment items and the evidence that demonstrates mastery. IDs refer to the question/exercise identifiers in this file. Coverage is assessed from the actual question wording and rubric, not merely from a topic label.

| Roadmap outcome ID | Documented learning outcome (faithfully summarised) | Assessment IDs | Expected evidence of mastery | Coverage |
|---|---|---|---|---|
| MLO-01 | Explain a data governance operating model and accountability structure. | A01, A11, B01, C01, D01, D04, E01, F1/F2 | Responsibility matrix, decision rights, escalation, metrics and role separation. | Covered; re-audited |
| MLO-02 | Classify data by sensitivity, criticality and protection requirements. | A02, A12, B02, C02, D01, E02, F1 | Field/asset register, separate sensitivity and criticality, handling map and propagation rationale. | Covered; re-audited |
| MLO-03 | Design identity and access controls using least-privilege principles. | A03, A13, B03–B04, C03–C04, D01, D03–D04, E03, F1/F2 | Role/access matrix, identity lifecycle, revocation, denied-access tests and bypass analysis. | Covered; re-audited |
| MLO-04 | Explain encryption, key-management and secrets-management responsibilities. | A04, A14, B05, C04, D03, E03, F1 | Encryption map, key/secret lifecycle, separation of duties, recovery and audit evidence. | Covered; re-audited |
| MLO-05 | Distinguish masking, tokenization, pseudonymisation and anonymisation; select techniques with stated limits. | A05, A14, B06, C05, D01–D03, E02, E04, F1 | Field-level protection matrix, mapping-vault boundaries, utility and re-identification risk. | Covered; re-audited |
| MLO-06 | Translate consent, purpose-limitation and residency constraints into architecture. | A06, A15, B07–B08, C03, C05–C06, D01–D02, E04–E05, F1 | Purpose/consent register, residency map, propagation/reconciliation workflow and specialist list. | Covered; re-audited |
| MLO-07 | Design retention, deletion, legal-hold and auditability controls. | A07, A15, B09, C06, D01–D02, E04, F1 | Retention/deletion matrix, hold-aware workflow, restore/replay handling and reconciliation evidence. | Covered; re-audited |
| MLO-08 | Map applicable requirements to technical controls and auditable evidence. | A08, B10, C07, D04, E01, E05, F1 | Requirement-to-control-to-test-to-evidence mapping, test results, gaps and remediation. | Covered; re-audited |
| MLO-09 | Integrate governance policies into architecture and delivery workflows. | A09–A10, B11–B12, C08–C09, D01–D04, E05, F1/F2 | CI/CD and runtime enforcement workflow, negative/bypass tests, exception/failure modes and drift metrics. | Covered; re-audited |
| MLO-10 | Produce and defend a sensitive-data governance and access design. | D01–D04, E01–E05, F1–F2, H3–H5 | Consistent capstone artifacts, traceable decisions, reviewer defence, limitations and readiness declaration. | Covered; re-audited |

## Requirements traceability — topic learning objectives

These rows follow the learning objectives listed in Sections 5.1–5.9 of `roadmap-Data-Governance-Security-Privacy-and-Compliance.md`. Wording is condensed for readability without adding new mandatory outcomes. Exercise/capstone IDs are supplemental evidence; a response must satisfy the relevant rubric to count as demonstrated mastery.

| Topic | Roadmap objective ID | Documented objective (condensed) | Assessment IDs | Expected mastery evidence | Status |
|---|---|---|---|---|---|
| 01 | T01-1 | Define owner, steward, operator/custodian and policy-owner roles. | A11, B01, C01, E01, F1 | Roles and boundaries distinguished in responsibility matrix. | Covered; re-audited |
| 01 | T01-2 | Build a responsibility matrix for governance decisions. | B01, C01, E01, F1 | RACI/equivalent with accountable role per decision. | Covered; re-audited |
| 01 | T01-3 | Define decision rights, escalation paths and governance forums. | B01, C01, D01, E01, F1/F2 | Decision-rights and escalation table with triggers. | Covered; re-audited |
| 01 | T01-4 | Distinguish asset ownership, platform operation, access approval and independent testing. | A01, A11, B01, C01, D04, E01, F1 | No silent conflation of approval, implementation and testing. | Covered; re-audited |
| 01 | T01-5 | Identify accountability gaps and conflicts. | A11, B01, C01, D04, E01, F1 | Conflict and escalation path with named owner. | Covered; re-audited |
| 01 | T01-6 | Define governance-effectiveness measures. | C01, E01, F1 | Metric definition, source, owner, cadence and action threshold. | Covered; re-audited |
| 02 | T02-1 | Build/apply a classification scheme with defined levels. | A02, A12, B02, C02, E02, F1 | Classification scheme and field register with rationale. | Covered; re-audited |
| 02 | T02-2 | Distinguish sensitivity from criticality. | A02, A12, B02, E02, F1 | Two separately reasoned dimensions. | Covered; re-audited |
| 02 | T02-3 | Inventory data and classify assets at field level where needed. | A12, B02, D01, E02, F1 | Complete synthetic field/asset inventory; unknowns explicitly blocked or reviewed. | Covered; re-audited |
| 02 | T02-4 | Link classification to handling requirements. | A12, B02, C02, E02, E05, F1 | Labels mapped to access/protection/lifecycle controls. | Covered; re-audited |
| 02 | T02-5 | Describe classification propagation through pipelines and derived data. | B02, C02, C05, D02, E02, E04, F1 | Lineage and propagation rules for joins, features and model datasets. | Covered; re-audited |
| 02 | T02-6 | Design classification review and recertification. | C02, E02, F1 | Review date, trigger, owner and approved downgrade/recertification evidence. | Covered; re-audited |
| 03 | T03-1 | Distinguish authentication from authorisation. | A03, B03, C03, E03 | Identity proof and permission decision explained separately. | Covered; re-audited |
| 03 | T03-2 | Distinguish user, group, role, service and workload identities. | B04, C04, D03, E03, F1 | Identity types and lifecycle in access design. | Covered; re-audited |
| 03 | T03-3 | Compare RBAC, ABAC and combined models. | B03, C03, E03, F1 | Role baseline plus trusted attributes and failure behavior. | Covered; re-audited |
| 03 | T03-4 | Apply least privilege and separation of duties. | A13, B01, C03–C04, D03, E03, F1 | Justified grants and separated approval, operation and test roles. | Covered; re-audited |
| 03 | T03-5 | Design privileged access, reviews and revocation. | A13, B04, C04, D03–D04, E03, F1 | Review/revocation workflow including sessions, tokens and effective-state checks. | Covered; re-audited |
| 03 | T03-6 | Design service-to-service access and fine-grained restrictions. | B03–B04, C03, C08, D03, E03, F1 | Scoped workload identities and resource/action-level policy. | Covered; re-audited |
| 03 | T03-7 | Produce a realistic role and access matrix. | C03, D01, E03, F1 | Role/asset/action/justification/approver/review matrix. | Covered; re-audited |
| 04 | T04-1 | Explain encryption at rest/in transit and where each applies. | A14, B05, C04, D03, E03, F1 | Data-flow map with protection boundaries and limits. | Covered; re-audited |
| 04 | T04-2 | Distinguish keys, application secrets, credentials and access tokens. | A04, A14, B05, D03, E03 | Terminology and lifecycle responsibilities separated. | Covered; re-audited |
| 04 | T04-3 | Explain key ownership, hierarchy and key-management services. | B05, C04, E03, F1 | DEK/KEK or equivalent hierarchy and ownership boundaries. | Covered; re-audited |
| 04 | T04-4 | Design rotation, revocation, recovery and key access policies. | B05, C04, D03, E03, F1 | Lifecycle procedure, recovery validation and revocation tests. | Covered; re-audited |
| 04 | T04-5 | Design secrets handling for pipelines and applications. | B04–B05, D03, E03 | Approved secret retrieval, scoped identity and exposure response. | Covered; re-audited |
| 04 | T04-6 | Define monitoring and auditing of key/secret use. | C04, D03, E03, E05, F1 | Identity/action/time/outcome evidence without secret values. | Covered; re-audited |
| 04 | T04-7 | State what encryption does not protect against. | A14, B05, C04, D03, F1 | Authorized plaintext exposure, compromised identity and key-access limits explained. | Covered; re-audited |
| 05 | T05-1 | Identify PII and quasi-identifiers. | A05, B06, C05, E02, E04, F1 | Identifier/quasi-identifier and combination risk assessment. | Covered; re-audited |
| 05 | T05-2 | Distinguish static and dynamic masking. | A14, B06, E02, E04 | Technique choice and scope/bypass limitations. | Covered; re-audited |
| 05 | T05-3 | Explain tokenization and protect its mapping. | A05, B06, C05, E02, E04 | Mapping vault/control boundary and linkability limitations. | Covered; re-audited |
| 05 | T05-4 | Distinguish pseudonymisation from anonymisation. | A05, B06, C05, E02, E04 | No guarantee claim; residual re-identification risk described. | Covered; re-audited |
| 05 | T05-5 | Assess re-identification risk and utility trade-offs. | B02, B06, C05, E02, E04, F1 | Rare-pattern, auxiliary-data and utility assessment. | Covered; re-audited |
| 05 | T05-6 | Design protection for production, analytics and test use. | A14, B06, C05, D01, E02, E04, F1 | Field-level technique, access, test-data and residual-risk decisions. | Covered; re-audited |
| 06 | T06-1 | Explain purpose limitation and data minimisation. | A06, A15, B07, C03, D01, E04, F1 | Purpose-specific use and minimisation rationale. | Covered; re-audited |
| 06 | T06-2 | Model consent lifecycle: given, scope, change and withdrawal. | B07, D02, E04, F1 | Versioned state/event flow, idempotency and reconciliation. | Covered; re-audited |
| 06 | T06-3 | Translate purposes/consent into data attributes and access conditions. | A06, B07, C03, E04–E05, F1 | Trusted policy attributes and explicit decisions. | Covered; re-audited |
| 06 | T06-4 | Translate residency into storage, processing and movement rules. | B08, D01, E04, F1 | Layered residency map and remediation/unknown list. | Covered; re-audited |
| 06 | T06-5 | Trace restrictions into downstream datasets, sharing and AI. | B07, C05, D02, E04, F1 | Lineage/copy inventory and downstream handling. | Covered; re-audited |
| 06 | T06-6 | Define evidence demonstrating permitted use. | B07, C03, D02, E04–E05, F1 | Purpose decision, identity, resource, time, outcome and traceable evidence. | Covered; re-audited |
| 06 | T06-7 | Identify requirements needing legal-specialist confirmation. | A06, C06, D01–D02, E04, F1/F2 | Explicit specialist-confirmation list; no invented legal rule. | Covered; re-audited |
| 07 | T07-1 | Define retention schedules with drivers, owners and dispositions. | A07, A15, B09, C06, E04, F1 | Source/driver, owner, trigger, disposition and review fields. | Covered; re-audited |
| 07 | T07-2 | Design deletion reaching replicas, derived datasets, logs and backups. | B09, C06, D02, E04, F1 | System-by-system copy/derivative inventory and outcome reconciliation. | Covered; re-audited |
| 07 | T07-3 | Design hold scope/release and interaction with automated deletion. | A07, B09, C06, E04, F1 | Authoritative hold state, scope, release authority and conflict handling. | Covered; re-audited |
| 07 | T07-4 | Design audit trails and deletion evidence. | B09, C06, D02, E04–E05, F1 | Evidence with per-system status, timestamps, identifiers and limitations. | Covered; re-audited |
| 07 | T07-5 | Handle exceptions and conflicting requirements. | C06, D01–D02, E04, F1 | Explicit pause/escalation, owner, exception and specialist questions. | Covered; re-audited |
| 07 | T07-6 | Verify deletion through reconciliation. | B09, C06, D02, E04, F1 | Expected-versus-confirmed counts/statuses, retries and unresolved outcomes. | Covered; re-audited |
| 08 | T08-1 | Identify and record obligations from a requirements source. | B10, C07, D04, E05, F1 | Source-labelled requirement register with interpretation status and owner. | Covered; re-audited |
| 08 | T08-2 | Define control objectives and choose preventive/detective/corrective controls. | B10, C07, D04, E05, F1 | Testable objective and control mix with risk rationale. | Covered; re-audited |
| 08 | T08-3 | Distinguish technical/procedural controls and assign owners. | B01, B10, C07, D04, E01, E05, F1 | Owner/operator/reviewer/tester roles and implementation details. | Covered; re-audited |
| 08 | T08-4 | Map requirements to controls, systems and evidence. | A08, B10, C07, D04, E05, F1 | Traceable requirement→objective→control→system→test→evidence chain. | Covered; re-audited |
| 08 | T08-5 | Design control testing, evidence collection and exception handling. | B10, C07, D04, E05, F1 | Population, sampling, evidence source, exception and reviewer procedure. | Covered; re-audited |
| 08 | T08-6 | Plan gap remediation. | C07, D04, E05, F1 | Finding owner/date, remediation, retest and caveated closure. | Covered; re-audited |
| 08 | T08-7 | Distinguish policy, implementation, operation and evidence. | A08, A09, B10, C07, D04, E05, F1 | Accurate assurance conclusion based on operating evidence. | Covered; re-audited |
| 09 | T09-1 | Distinguish documenting a policy from enforcing it. | A09, B11, C08–C09, D04, E05, F1 | Decision and enforcement-point behavior tested separately. | Covered; re-audited |
| 09 | T09-2 | Design classification-driven protection and enforcement points. | A09, B11, C08, D01, E02, E05, F1 | Actual data boundary and negative/bypass tests. | Covered; re-audited |
| 09 | T09-3 | Design governance checkpoints in pipelines and CI/CD. | B11, C09, D01, E05, F1 | Build-time and runtime controls, gates and release tests. | Covered; re-audited |
| 09 | T09-4 | Integrate metadata and lineage with enforcement. | B02, B07, B11, C05, C08, D02, E02, E04–E05, F1 | Trusted attributes, lineage propagation and missing-edge handling. | Covered; re-audited |
| 09 | T09-5 | Design approval and exception workflows. | B01, C01, C09, D01, E01, E05, F1 | Authority, justification, expiry, revocation and post-review. | Covered; re-audited |
| 09 | T09-6 | Define continuous validation and governance metrics. | C01, C09, D04, E05, F1 | Drift/bypass/decision metrics, owner, cadence and response. | Covered; re-audited |
| 09 | T09-7 | Decide what can be automated and what needs human judgment. | A10, B12, C03, C09, D01–D04, E05, F1/F2 | Deterministic checks separated from legal/business/risk decisions. | Covered; re-audited |

**Traceability interpretation:** “Covered” means an item or rubric directly assesses the objective at an appropriate level; it does not mean a learner has passed. A question label alone is not evidence of mastery. For each objective, review the referenced answer/rubric and the learner’s work product. The capstone project file named in the project tree was not available for content inspection, so the integrated assessment is aligned to the documented module-roadmap project objectives and deliverables rather than uninspected project-specific instructions.

---

# Section A — Beginner-Level Questions

**Suggested weighting: 30 points.** A01–A10 are 2 points each; A11–A15 are 2 points each.

## A1. Multiple-choice questions

### A01 — Governance accountability (Topic 01; Beginner; 2 points)
**Objective:** distinguish accountability from implementation. Who should normally be accountable for approving the intended business use and access requirements of a governed data asset?

A. Any engineer who can change the pipeline  
B. The designated data owner or authorized business decision owner  
C. The person who happens to run the query  
D. The audit-log storage administrator

*Choose one best answer.*

### A02 — Sensitivity versus criticality (Topic 02; Beginner; 2 points)
**Objective:** distinguish confidentiality impact from business/operational criticality. Which statement is most accurate?

A. High criticality always means the data are highly sensitive.  
B. Sensitivity and criticality are separate dimensions and should be assessed separately.  
C. If a dataset is Public, its criticality must be Low.  
D. Criticality replaces the need for classification.

### A03 — Authentication versus authorization (Topic 03; Beginner; 2 points)
**Objective:** distinguish identity verification from permission evaluation. A service verifies that a caller is `risk-batch-job`, then checks whether that service may read `dp.customer_risk_features`. The first operation is primarily:

A. Authorization  
B. Authentication  
C. Data masking  
D. Retention enforcement

### A04 — Key management (Topic 04; Beginner; 2 points)
**Objective:** distinguish encryption from key custody. Why should an encryption key not simply be stored beside encrypted data with identical access permissions?

A. Encryption only works if the key is stored in a different cloud.  
B. Anyone who can obtain both may defeat the protection; separate access boundaries reduce that risk.  
C. Encryption keys are public metadata.  
D. The data become impossible to back up if the key is separate.

### A05 — De-identification terminology (Topic 05; Beginner; 2 points)
**Objective:** distinguish tokenization/pseudonymisation from anonymisation. Which statement is safest?

A. Replacing a customer ID with a token guarantees anonymity.  
B. Hashing a phone number always prevents re-identification.  
C. Tokenization and pseudonymisation can reduce exposure but may preserve linkability or re-identification risk.  
D. Masking a display field means raw data cannot be accessed elsewhere.

### A06 — Purpose limitation (Topic 06; Beginner; 2 points)
**Objective:** understand that technical access does not itself establish an approved purpose. A user has permission to read a dataset for fraud detection and now wants to use it for a new marketing campaign. What is the best first response?

A. Permit it because the user already has read access.  
B. Check the approved purpose and applicable consent/other requirements with authorized owners and specialists.  
C. Copy the data into a new table to create a new purpose.  
D. Remove the dataset's classification label.

### A07 — Legal hold (Topic 07; Beginner; 2 points)
**Objective:** understand the interaction between retention expiry and a hold. A record reaches its configured retention date, but the authoritative hold registry says the record is under an active hold. The workflow should:

A. Delete it because the retention date always wins.  
B. Ignore the hold registry if data are in a backup.  
C. Prevent deletion of the held scope and record the outcome for authorized review.  
D. Remove audit logs before deleting it.

### A08 — Evidence chain (Topic 08; Beginner; 2 points)
**Objective:** distinguish policy from implemented and operating control. Which sequence best represents a control assurance chain?

A. Policy documented → control implemented → control operates → evidence produced  
B. Policy documented → declare compliance → stop testing  
C. Screenshot captured → no need to identify a control owner  
D. Audit request → create a policy after the fact

### A09 — Policy enforcement (Topic 09; Beginner; 2 points)
**Objective:** distinguish a policy decision from actual enforcement. A policy decision point returns `DENY`, but the application ignores it and returns the data. What failed?

A. The policy has become a data contract.  
B. Enforcement failed; the decision alone did not protect the resource.  
C. Classification is no longer needed.  
D. The audit record automatically blocks access.

### A10 — Human judgment (Topics 01, 06, 09; Beginner; 2 points)
**Objective:** distinguish deterministic checks from decisions needing accountable judgment. Which decision is most likely to require authorized human judgment rather than a simple deterministic rule alone?

A. Whether a required `classification` field is missing  
B. Whether an infrastructure plan enables a prohibited public endpoint  
C. Whether a novel proposed use is compatible with an approved purpose and relevant obligations  
D. Whether a policy JSON file parses

## A2. Short-answer questions

### A11 — Roles and separation (Topic 01; Beginner; 2 points)
In 3–5 sentences, distinguish the responsibilities of a data owner, data steward, platform engineer, and control tester. Explain one risk of having the same person implement and independently attest to a high-impact control.

### A12 — Classification metadata (Topic 02; Beginner; 2 points)
A table contains a synthetic customer reference, public product code, transaction amount, and operational processing timestamp. Why might a single table-level label be insufficient? Name at least three metadata fields, other than data values, that help govern the asset.

### A13 — Least privilege (Topic 03; Beginner; 2 points)
A marketing analyst needs aggregated segment counts but not raw customer identifiers. State two design choices that reduce unnecessary access and one control needed when the analyst changes teams.

### A14 — Encryption versus masking (Topics 04–05; Beginner; 2 points)
Explain why encryption at rest does not replace masking in an analytics view, and why masking does not replace encryption.

### A15 — Purpose, residency, retention (Topics 06–07; Beginner; 2 points)
Name three places or processes other than the primary database table where data-location or retention rules may still matter. Give one example of how a restriction can be lost downstream.

---

# Section B — Intermediate-Level Questions

**Suggested weighting: 36 points.** B01–B12 are 3 points each.

### B01 — RACI and decision rights (Topic 01; Intermediate; 3 points)
Northbridge's data science team requests raw access to a Restricted customer field. The platform team can technically grant it, but the data owner is responsible for approved business use and Security sets the technical access baseline. Assign roles for: (1) justify use, (2) approve access, (3) implement grant, (4) independently test grant, and (5) resolve a policy conflict. State which roles must not be assumed interchangeable.

### B02 — Classification propagation (Topic 02; Intermediate; 3 points)
A derived feature table joins a Restricted customer identifier with Internal transaction aggregates. The team argues that the output is Internal because the direct identifier column was dropped. Explain why that conclusion cannot be made from column removal alone. Give four checks or metadata elements needed before approving a lower handling category.

### B03 — RBAC and ABAC (Topic 03; Intermediate; 3 points)
A platform serves several teams, purposes, data classes, and regions. Explain when RBAC is useful, when ABAC adds value, and how the two can be combined. Give one example of an attribute that should come from a trusted source rather than the requester.

### B04 — Service identities and revocation (Topic 03; Intermediate; 3 points)
A scheduled pipeline uses a shared human credential embedded in a configuration file. Identify three risks and propose a safer replacement, including rotation or revocation.

### B05 — Envelope encryption and secrets (Topic 04; Intermediate; 3 points)
Describe envelope encryption. Identify the roles of the data encryption key (DEK) and key-encryption key (KEK), two operational controls for the KEK, and why a database password should be handled as a secret rather than stored in source code.

### B06 — Selecting a PII protection technique (Topic 05; Intermediate; 3 points)
Northbridge wants to (a) show only the last few characters of a customer identifier in a support UI, (b) join research records across datasets without routinely revealing identity, and (c) publish an aggregate report. Recommend a candidate technique for each, state one limitation each, and identify one condition that requires specialist review before claiming anonymisation.

### B07 — Consent/purpose propagation (Topic 06; Intermediate; 3 points)
A synthetic consent withdrawal arrives after a customer contributed to a lake table, feature store, cache, and training dataset. Propose a propagation and reconciliation workflow. Identify two questions for authorized privacy/legal or business decision-makers.

### B08 — Residency map (Topic 06; Intermediate; 3 points)
The main dataset is in `region-a`; backups are in `region-b`, support logs go to a SaaS service, and an operator in `region-c` can access the environment. The approved synthetic residency policy permits storage and processing only in `region-a`. List location dimensions to investigate, identify at least three possible conflicts, and propose a remediation or confirmation path for each. Do not assume a region label resolves every legal question.

### B09 — Retention and deletion matrix (Topic 07; Intermediate; 3 points)
A synthetic deletion request affects a primary database, CDC log, bronze lake, warehouse table, feature store, cache, backup, and partner extract. Design the minimum columns of a lifecycle control matrix and describe how the workflow handles a legal hold, backup expiry, and a partner that has not confirmed deletion.

### B10 — Evidence quality (Topic 08; Intermediate; 3 points)
A control owner provides one screenshot of an access-review dashboard. The auditor asks whether the control operated throughout the last six months. Explain why the screenshot is insufficient by itself and list at least five evidence properties or artefacts that strengthen the conclusion.

### B11 — CI/CD governance gate (Topic 09; Intermediate; 3 points)
A pull request adds a new table but omits owner, classification, retention-policy reference, and purpose metadata. Specify checks before merge, expected outcome, and at least two checks that must still operate after deployment.

### B12 — Policy-engine outage (Topics 03, 08–09; Intermediate; 3 points)
The central policy decision service becomes unavailable. Ordinary users are reading Restricted fields, a pipeline attempts cross-region export, and a scheduled job wants to delete data whose hold status cannot be retrieved. Recommend immediate handling for each and explain the availability/security trade-off.

---

# Section C — Advanced-Level Questions

**Suggested weighting: 36 points.** C01–C09 are 4 points each. Alternative designs are acceptable when assumptions, trade-offs, owners, tests, and residual risks are explicit.

### C01 — Governance operating model at scale (Topics 01, 08–09; Advanced; 4 points)
Northbridge has Risk, Marketing, Finance, Data Science, Platform Engineering, Security, and Privacy teams. Product teams complain every access decision reaches the governance council; the council says teams bypass it. Design decision rights for routine low-risk access, elevated access to Restricted fields, new purposes, classification disputes, and emergency access. Include escalation triggers, review cadence, evidence, and a metric that reveals poor process design.

### C02 — Classification conflict and propagation (Topics 02, 05–06, 09; Advanced; 4 points)
A source contract labels a customer attribute `Restricted`; a downstream team manually labels the derived table `Internal`. Lineage shows a join with merchant location and transaction timing. What should happen before publication? Explain how to avoid both automatic over-classification forever and unsafe automatic declassification.

### C03 — Access model with purpose and context (Topics 03, 06; Advanced; 4 points)
Design an authorization decision for a synthetic request to read a Restricted field. Identify subject, resource, action, declared purpose, classification, residency context, and relevant consent/purpose state. Specify handling of missing/stale attributes and explain why a valid role alone is insufficient.

### C04 — Key lifecycle and separation of duties (Topics 03–04, 07–08; Advanced; 4 points)
A production analytics service uses envelope encryption. One platform administrator can administer storage, read application secrets, and approve key-policy changes. Identify the separation-of-duties problem. Propose a key/secret lifecycle covering creation, access, rotation, recovery, revocation, audit, and retirement; name evidence that demonstrates operation rather than design alone.

### C05 — Re-identification and derived AI assets (Topics 02, 05–06, 09; Advanced; 4 points)
A research dataset removes names and direct customer IDs but retains exact timestamps, merchant locations, and rare transaction patterns. It is tokenized so rows can be linked across tables. Explain at least four residual risks, recommend a safer release design, and state what metadata/lineage should travel with downstream features or model datasets.

### C06 — Conflicting lifecycle requirements (Topics 04, 06–08; Advanced; 4 points)
A synthetic record reaches its configured retention limit, an erasure request is pending, and one subset is under an active hold. Backups expire later; audit evidence includes an event reference to the record. Propose a decision process separating known technical state from interpretations requiring specialist confirmation. Include restore/replay protection and evidence minimisation.

### C07 — Control operating effectiveness (Topic 08; Advanced; 4 points)
A team has an approved access-review policy and quarterly calendar. Three reviews occurred, but the grant inventory was incomplete and evidence is missing for one month. Can the control be concluded effective for the full period? Define a test approach and explain how to record the gap without making an unsupported compliance claim.

### C08 — Enforcement coverage and bypass (Topic 09, connected to Topics 02–08; Advanced; 4 points)
A query gateway enforces masking, but analysts also have direct object-storage access; notebooks can export files; training pipelines read feature tables; backups can be restored into a separate environment. Build a coverage strategy with at least five paths, PEP/control, negative test, evidence, and owner. Identify a safe short-term containment action.

### C09 — Policy release regression (Topics 08–09; Advanced; 4 points)
A new policy version lowers allowed Restricted-data requests by 60%. Some denials are correct; others appear to block legitimate Risk workflows. Describe investigation and release decisions using unit/negative tests, sample-log simulation, canary deployment, runtime metrics, human review, and rollback criteria. Explain why simply reverting may create risk.

---

# Section D — Scenario-Based Questions

**Suggested weighting: 32 points, 8 points each.** Use fictional Northbridge Bank scenarios and synthetic data only.

## D01 — Customer analytics launch (Topics 01–09; Advanced; 8 points)
Northbridge plans `customer_analytics`, combining customer profiles, account summaries, and transaction summaries. Consumers include Risk, Marketing, Finance, Customer Service, Data Science, platform operators, and auditors. **Illustrative assumptions for this exercise:** Restricted identifiers are not needed for most analytics consumers; Marketing use depends on an approved purpose/consent decision; a synthetic residency policy permits storage/processing only in `region-a`; a transaction-retention rule exists but its real source and period require specialist confirmation; copies may exist in source systems, streams, lake/warehouse, feature store, cache, backup, and partner extract; access and lifecycle controls must emit evidence.

**Tasks:** (1) state the problem and assumptions needing confirmation; (2) identify accountable roles/escalation; (3) propose classification and protection for field groups; (4) design access rules and masked/aggregated paths; (5) map purpose, residency, retention, hold and deletion constraints across copies; (6) map at least five requirements to controls/evidence; (7) draw a governance-by-design workflow with preventive and detective checkpoints; (8) identify three residual risks and how to validate the design.

## D02 — Consent change fails to propagate (Topics 05–09; Advanced; 8 points)
A synthetic withdrawal event was processed by the consent service, but a feature store and existing training dataset still contain records whose use may be affected. The lineage catalogue is missing one transformation edge, and the nightly pipeline reports success.

**Tasks:** (1) explain why pipeline success is insufficient; (2) propose immediate containment and scope discovery; (3) list systems/derived assets to reconcile; (4) separate automatable actions from decisions needing authorized privacy/legal or business judgment; (5) define closure evidence and tests; (6) recommend one architectural change and one monitoring metric.

## D03 — Key exposure and uncertain access (Topics 01, 03–04, 08–09; Advanced; 8 points)
A developer accidentally commits a synthetic-but-realistic database credential to a shared repository. The credential may have been copied to a build log. The same service identity accesses both Restricted analytics and a lower-sensitivity reference dataset.

**Tasks:** (1) state immediate containment actions in priority order; (2) describe revocation/replacement without assuming deleting the Git commit is enough; (3) determine scope of access/exposure; (4) recommend identity, secret-retrieval and separation-of-duties changes; (5) specify evidence, tests and closure criteria; (6) explain what to preserve for investigation and what secret material not to copy into evidence.

## D04 — Audit finding: policy exists, control is uncertain (Topics 01–03, 08–09; Advanced; 8 points)
An internal review finds an approved policy requiring quarterly access reviews of Restricted data. The catalogue has incomplete classification tags, one platform's direct-access path bypasses the query gateway, and evidence is missing for one review period. The team says it is compliant because the policy is approved.

**Tasks:** (1) explain assurance gaps; (2) build requirement → objective → control → implementation → test → evidence; (3) identify risk-based containment; (4) design evidence-completeness and direct-access tests; (5) propose remediation with owners/dates; (6) state how conclusions should be worded until resolved.

---

# Section E — Practical Design Exercises

Use synthetic data only. Each exercise is scored out of 20 points. Produce reviewable artifacts, not only prose.

## E01 — Governance responsibility matrix (Topics 01, 08; Intermediate; 20 points)
**Inputs:** Data Owner, Data Steward, Platform Engineering, Security, Privacy/Legal Specialist, Risk Authority, Control Tester; decisions include classification approval, access approval, implementation, exception approval, emergency access, control testing, risk acceptance, remediation closure.

**Tasks:** build a RACI or equivalent; assign accountability; define escalation for purpose dispute, high-risk access, and urgent incident; identify conflicts of interest; define two governance metrics.

**Deliverables:** responsibility matrix; decision-rights/escalation table; review cadence and metric definitions.

**Objective validation criteria:** every decision has one accountable role or explicitly documented joint authority; approval/implementation/testing are distinguished; high-risk exceptions have delegated authority and expiry; metrics have definition, source, owner, cadence and threshold action; unresolved legal/policy interpretations go to specialists.

## E02 — Classification-to-control register (Topics 02–05, 09; Intermediate–Advanced; 20 points)
**Synthetic schema:** `customer_profile.customer_ref` (stable synthetic reference), `customer_profile.contact_email`, `customer_profile.segment`, `transaction_summary.amount_band`, `transaction_summary.merchant_area`, `transaction_summary.event_time`, `risk_features.behaviour_score`, `consent_preference.marketing_status`.

**Tasks:** classify each field using a labelled organisational scheme; assess criticality separately; record owner/steward, permitted purposes, access roles, encryption, masking/tokenization, retention/residency references, lineage, review date, review triggers and recertification owner; define propagation through joins, aggregates, features and model datasets; identify decisions requiring human review and the evidence needed to justify any downgrade.

**Deliverables:** classification register; classification-to-control mapping; propagation rules and unresolved-decision list.

**Objective validation criteria:** all eight fields have a classification or `Unknown—publication blocked`; sensitivity and criticality are separate; labels map to handling requirements and owner; derived features retain applicable restrictions unless documented assessment supports a change; review trigger/cadence and recertification owner are explicit; no technique is claimed to guarantee anonymity.

## E03 — Access, key, and secret lifecycle (Topics 03–04; Advanced; 20 points)
**Inputs:** personas Risk Analyst, Marketing Analyst, Data Scientist, Pipeline Service, Platform Administrator, Auditor; assets raw customer table, masked view, Restricted feature store, encryption keys, database credentials, evidence repository.

**Tasks:** produce role/access matrix for read/write/export/administer/decrypt/audit; define authentication, authorization, service identity and revocation; describe envelope encryption and separation of key duties; define secret creation/storage/retrieval/rotation/revocation/recovery/retirement; define evidence and independent tests.

**Deliverables:** access matrix and rationale; key/secret lifecycle procedure; separation-of-duties map; denied-access, revocation and exposure test cases.

**Objective validation criteria:** no unjustified wildcard grants; workload identities replace shared human credentials; raw-data/key boundaries are explicit; revocation propagation and caches/sessions are addressed; evidence includes identity, action, resource, time and result without recording secret material.

## E04 — Privacy, residency, retention, deletion (Topics 05–07; Advanced; 20 points)
**Synthetic system inventory:** source database, CDC stream, raw lake, curated warehouse, feature store, cache, backup, support logs, partner extract, model training dataset.

**Tasks:** map storage/processing/movement/access/metadata/key locations; define purpose and consent attributes; select techniques for identifiers/quasi-identifiers and state residual risk; create retention/deletion matrix for each system; define hold, backup expiry, restore/replay suppression, partner confirmation and reconciliation; define evidence and specialist-confirmation items.

**Deliverables:** purpose/consent register; residency map/remediation list; retention/deletion matrix and hold-aware workflow; protection matrix/residual-risk note; deletion evidence template and specialist list.

**Objective validation criteria:** all ten systems addressed or explicitly out of scope with owner/rationale; all location dimensions considered; withdrawal/deletion reaches all identified copies/derivatives; unknown hold state does not mean “no hold”; backups, logs, caches, partners and models addressed; technical actions separated from legal interpretation.

## E05 — Requirement-to-control-to-evidence and enforcement workflow (Topics 08–09, integrating 01–07; Advanced; 20 points)
**Illustrative synthetic requirements:** R-01 Restricted raw fields only for approved identities/purposes; R-02 new assets require owner/classification/retention reference before publication; R-03 storage/processing follow approved synthetic residency policy; R-04 deletion respects authoritative hold state and reconciles known copies; R-05 each control decision emits minimised, traceable evidence. These are exercise assumptions, not statements of law.

**Tasks:** map each requirement to objective, preventive/detective/corrective controls, owner, location, test, evidence and remediation; draw workflow from code review through monitoring; define policy-as-code checks and at least eight negative/boundary tests; select fail modes for Restricted reads, exports, provisioning and deletion with unknown hold state; design exception approval, compensating controls, expiry, revocation verification and review; define five metrics and an ADR.

**Deliverables:** requirement/control/evidence map; governance-by-design workflow; policy examples and test matrix; exception/fail-mode decisions; coverage/bypass analysis, metrics catalogue and ADR.

**Objective validation criteria:** every requirement maps to control or explicit gap; every control has owner, implementation point, test and evidence; tests exercise actual PEP enforcement; bypass paths are tested/mitigated or accepted by authorized authority; exceptions expire; human decisions/specialist confirmations are explicit; no compliance guarantee is inferred from a design/test pass.

---

# Section F — Integrated Assessment

## F1. Cumulative case: Sensitive data governance and access design (Topics 01–09)
**Difficulty:** Capstone readiness. **Suggested score:** 50 points. **Objective:** integrate all nine topic deliverables into one coherent architecture.

### Scenario
Northbridge Bank (fictional) is launching a shared customer analytics data product combining customer profiles, account summaries, transaction summaries, consent preferences, and derived risk features. Consumers include Risk, Marketing, Finance, Customer Service, Data Science, platform operators, and auditors. Use synthetic data only.

**Illustrative assumptions to validate rather than treat as facts:** Risk proposes fraud-detection use for selected Restricted fields; Marketing use depends on an approved purpose/consent decision; a synthetic residency policy permits storage/processing in `region-a`; retention periods and legal holds require an authoritative register, with no universal period assumed; copies may exist in source systems, streams, lake/warehouse layers, caches, feature stores, backups, logs, partner extracts and model-training datasets; access, change, exception, deletion and control-test evidence is required.

### Required work products
1. **Governance operating model:** owners, stewards, policy owners, approvers, operators, testers, escalation, RACI and review cadence.
2. **Data inventory/classification:** asset/field register, separate sensitivity and criticality axes, propagation and review rules.
3. **Access design:** role/attribute matrix, service identities, least privilege, review, revocation, and raw/masked/aggregated paths.
4. **Encryption/secrets:** data-flow encryption map, envelope-encryption pattern, key/secret owners, rotation, recovery, revocation and separation of duties.
5. **PII protection:** field-level technique selection, test-data policy, token mapping controls, re-identification risk and limits.
6. **Purpose/consent/residency:** purpose register, consent state/events, withdrawal propagation, residency across storage/processing/movement/access/metadata/keys, and specialist-confirmation list.
7. **Lifecycle:** retention register, copies/derivatives inventory, hold-aware deletion, backup/restore handling, partner confirmation, reconciliation and evidence.
8. **Controls/evidence:** source-labelled requirement register, many-to-many control mapping, evidence plan, control tests, gap/remediation register and ADR.
9. **Governance by design:** policy lifecycle, policy examples, CI/CD and runtime checkpoints, fail modes, exceptions, tests, drift monitoring, bypass analysis, metrics and human/automation boundary.
10. **Defence:** explain at least five architecture decisions and respond to reviewer challenges.

### Scoring rubric (50 points)

| Dimension | Points | Full-credit evidence |
|---|---:|---|
| Accountability and decision rights | 5 | Clear owners, approvers, operators, testers, escalation and separation |
| Classification and propagation | 5 | Every field handled; sensitivity/criticality separated; derived-data logic stated |
| Access, keys and secrets | 6 | Least privilege, identity separation, lifecycle, revocation, key boundaries |
| Privacy and protection | 6 | Purpose, consent, residency, masking/tokenization, residual risk, specialist questions |
| Retention and deletion | 6 | Copies/derivatives, backups, hold-aware logic, reconciliation and evidence |
| Control/evidence mapping | 6 | Requirement → objective → control → owner → test → evidence |
| Enforcement and tests | 8 | CI/CD/runtime PEPs, negative/bypass tests, expiry, drift monitoring |
| Assumptions and residual risk | 4 | Explicit assumptions, alternatives, failure behavior, no unsupported legal conclusions |
| Defence and completeness | 4 | Consistent identifiers and traceable decisions |

**Recommended capstone readiness:** **43/50 (86%)**, no zero in any dimension, all nine topic gates completed, and no unresolved high-risk issue without an owner and disposition. This aligns the capstone threshold with the module’s recommended 85% readiness target. This is a learning recommendation, not external certification.

## F2. Reviewer challenge prompts
Answer each in 2–4 minutes and cite the artifact supporting your answer.

1. Who can approve raw Restricted access, and who implements it?
2. What prevents a developer relabelling a Restricted field as Internal?
3. How is a revoked identity prevented from continuing through cached sessions or credentials?
4. What happens if the policy engine or authoritative metadata source is unavailable?
5. How do you know deletion reached backups, caches, features and partner copies?
6. What evidence demonstrates operating effectiveness across a review period?
7. Which decisions are automated, which are human, and why?
8. What happens when policies conflict or metadata are ambiguous?
9. How do you detect direct access that bypasses the query gateway?
10. Which conclusions require privacy/legal or other specialist confirmation?

---

# Section G — Answer Key and Explanations

Attempt the questions before reading this section. These are model answers, not the only defensible architecture. Credit equivalent designs that state assumptions, cover the risk, name decision owners and define validation.

## G1. Section A answers

| ID | Answer / expected points | Explanation and common error |
|---|---|---|
| A01 | **B.** The designated data owner or authorized business decision owner. | Technical capability does not confer business decision rights. A confuses implementation with accountability. |
| A02 | **B.** Sensitivity and criticality are separate dimensions. | Confidentiality impact and operational/business impact can differ. A/C infer one axis from the other. |
| A03 | **B. Authentication.** | Authentication verifies identity; authorization evaluates permission. A reverses the concepts. |
| A04 | **B.** Separate key boundaries reduce the chance one compromise exposes ciphertext and key. | Key custody is part of protection. There is no universal requirement to use a different cloud. |
| A05 | **C.** Tokens and pseudonyms can remain linkable/re-identifiable. | A/B/D overstate technique guarantees and ignore bypass paths. |
| A06 | **B.** Check approved purpose and applicable requirements with authorized owners/specialists. | Technical access does not establish permitted use. Copying or relabelling data is not a valid bypass. |
| A07 | **C.** Prevent deletion of held scope and record the result. | The explicit active hold must be respected in the scenario. |
| A08 | **A.** Policy → implemented control → operation → evidence. | A policy or screenshot alone cannot establish operating effectiveness. |
| A09 | **B.** Enforcement failed. | A PDP decision does not protect data unless the PEP actually applies it. |
| A10 | **C.** Novel purpose compatibility may require accountable human judgment. | Missing fields, public endpoint configuration and JSON parsing are deterministic checks when rules are clear. |

**A11 model answer (2 points):** The data owner is accountable for intended use and business access decisions; the steward maintains definitions and metadata quality; the platform engineer implements/operates technical controls; the control tester independently assesses design and operation. If the implementer independently attests to a high-impact control without compensating review, errors or conflicts of interest may go undetected. Full credit: all roles plus a specific risk.

**A12 model answer (2 points):** A table-level label can over-protect some fields while under-describing others. Useful metadata include field/asset owner, classification, criticality, permitted purposes, retention-policy reference, residency-policy reference, lineage and review date. Full credit: mixed-field rationale and three metadata fields.

**A13 model answer (2 points):** Provide aggregated/masked views and deny direct raw identifier access; scope actions and columns to need. On team change, trigger entitlement review and timely revocation of roles, sessions, tokens and grants as applicable. Full credit: two least-privilege choices and one revocation control.

**A14 model answer (2 points):** Encryption at rest protects stored ciphertext under its key/access assumptions, but an authorized query may decrypt values. Masking limits what the view reveals. Masking does not protect underlying files/backups if unauthorized identities can read them directly, so encryption and access controls still matter. Full credit: complementary threat models.

**A15 model answer (2 points):** Backups, CDC/event logs, support logs, replicas, caches, feature stores, partner extracts, notebooks, model datasets, catalogues and DR environments are examples. A derived feature can lose purpose/residency tags if lineage propagation is not enforced. Full credit: three locations and one propagation failure.

## G2. Section B model answers and rubrics

### B01 — RACI (3 points)
A defensible assignment: requester/business owner justifies need and purpose; data owner or delegated approver approves access; platform/IAM operator implements the approved grant; control tester/independent reviewer tests it; policy owner/governance escalation forum resolves conflicts, with qualified specialists interpreting legal/privacy issues. Do not conflate approver, implementer and independent tester without documenting compensating controls. **Scoring:** role assignment (1), separation (1), escalation/independence (1).

### B02 — Classification propagation (3 points)
Dropping a direct identifier does not prove lower sensitivity: quasi-identifiers, joins, timing, uniqueness or inference may retain/increase risk. Assess combinations and re-identification risk; inspect lineage and transformations; confirm audience/purpose; document residual risk and authorized classification decision; update metadata and controls. **Scoring:** residual risk (1), lineage/combination analysis (1), documented review (1).

### B03 — RBAC/ABAC (3 points)
RBAC is useful for stable job functions and understandable baseline grants. ABAC adds context such as classification, purpose, region, resource, action or time. A hybrid uses roles for baseline eligibility and attributes for contextual restrictions. Trusted attributes include catalogue classification, authenticated entitlements, approved purpose registry and trusted resource region—not an unverified requester field. **Scoring:** RBAC (1), ABAC/hybrid (1), trusted attribute (1).

### B04 — Service identity (3 points)
Risks include source-control/log disclosure, poor attribution, broad shared permissions, hard rotation and persistence after staff changes. Use a dedicated least-privilege workload identity with short-lived credentials or approved secret retrieval. Revoke/rotate exposed credentials, invalidate sessions/tokens as needed, audit use and test effective revocation. **Scoring:** three risks (1), replacement (1), revocation verification (1).

### B05 — Envelope encryption (3 points)
A DEK encrypts data; a KEK wraps/protects the DEK. The wrapped DEK may be stored with ciphertext, while authorized services use the KEK under controlled permissions. KEK controls include restrictive policy, separated administrative roles, rotation, monitoring, recovery testing and audited access. Source-code passwords leak through clones, logs or history; retrieve through approved secret management and rotate exposed values. **Scoring:** DEK/KEK (1), two key controls (1), secret rationale (1).

### B06 — PII protection (3 points)
(a) Partial masking in support UI plus restriction of underlying raw access; limitation: other paths may expose raw data or partial values may identify someone. (b) Tokenization/pseudonymisation with mapping vault separately controlled; limitation: linkability/re-identification remain possible. (c) Aggregate/coarsen/suppress data; limitation: small groups, rare combinations or auxiliary data can permit inference. Assess realistic re-identification risks and obtain specialist confirmation before claiming anonymisation. **Scoring:** one point per use with a limitation.

### B07 — Consent/purpose propagation (3 points)
Record withdrawal with stable event ID/version; identify copies through lineage/inventory; propagate idempotently; apply approved handling; reconcile expected vs confirmed outcomes; retry failures and alert on unresolved copies; preserve evidence. Specialist questions include affected purposes, treatment of already-trained models, timing, and retained evidence duties. **Scoring:** propagation (1), reconciliation/evidence (1), specialist questions (1).

### B08 — Residency (3 points)
Investigate storage (primary/backup/replicas), processing, movement, access/support, logs, metadata/catalogue, keys, SaaS and DR. Conflicts may include backup in `region-b`, logs leaving the region, operator access from `region-c`, and key/metadata replication. Remediate by moving/disabling backup, regionalising logs, restricting/approving support access, or routing ambiguity to specialists. **Scoring:** dimensions (1), conflicts (1), remediation/confirmation (1).

### B09 — Retention/deletion (3 points)
Matrix columns can include asset/copy, owner, classification, source/driver, policy/version, trigger, system/location, method, hold source/state, backup/restore behavior, downstream/partner action, retry state, evidence ID, outcome/time and exception owner. Check authoritative hold state before destructive disposition; document backup expiry/restore filtering; track partner notification and confirmation, escalating missing confirmation instead of claiming completion. **Scoring:** matrix (1), holds/backups (1), partner/reconciliation (1).

### B10 — Evidence quality (3 points)
A screenshot is point-in-time and may omit complete population, history, approvals, failed reviews, changes and integrity. Stronger evidence includes complete grant population, dated review records, approver identity, review outcomes, remediation tickets, source extracts, protected logs, retention controls, test procedure and independent sampling/reconciliation. **Scoring:** insufficiency (1), five artefacts/properties (1), period coverage/independence (1).

### B11 — CI/CD (3 points)
Validate contract/schema, owner, approved classification, retention reference, purpose metadata, policy IDs, IaC encryption/residency/access settings and policy tests. Block merge/release with actionable diagnostics; route ambiguity to an owner instead of permissive defaults. After deployment, runtime access/export PEPs and drift/freshness scans must still operate. **Scoring:** checks (1), fail behavior (1), runtime controls (1).

### B12 — Policy outage (3 points)
Restricted reads: deny/pause unless a specifically approved, tested bounded fallback is safe. Cross-region export: block transfer. Deletion with unknown hold state: pause affected destructive action until authoritative state is resolved. These choices reduce disclosure/irreversible-deletion risk but reduce availability; alert, retry safely and monitor control-plane health. **Scoring:** one point per operation with reasoning.

## G3. Section C evaluation rubrics

Each C question is worth 4 points. Award one point for each listed element; equivalent defensible designs earn credit.

- **C01:** risk-tiered decision rights; named approvers/operators/testers; escalation/emergency paths; meaningful metric such as approval lead time, repeat exception rate or bypass rate.
- **C02:** block/hold publication pending review; use trusted metadata and lineage; assess quasi-identifiers/inference; document human-approved downgrade criteria and tests instead of unsafe auto-downgrade or perpetual unreviewed over-classification.
- **C03:** define subject/resource/action/purpose/classification/context; use trusted attribute sources; specify missing/stale/conflicting behavior; enforce at real data boundary and test/evidence it.
- **C04:** identify incompatible admin powers; separate data/storage, key and secret duties where practical; cover create/access/rotate/recover/revoke/retire; provide operational evidence and independent tests.
- **C05:** identify linkability and rare-pattern risk; quasi-identifiers/auxiliary-data/inference; recommend minimisation/coarsening/suppression or controlled access; propagate classification, purpose, lineage, transformation and residual-risk metadata to features/models.
- **C06:** preserve held scope and avoid unsupported deletion claims; route interpretation to specialists; address backups, restore filtering/replay, derivatives and evidence minimisation; provide per-system reconciliation and exceptions.
- **C07:** full-period effectiveness is not demonstrated with incomplete population/missing evidence; test population completeness and period coverage; independently sample/reconcile outcomes; log gap, owner, risk, remediation and caveated conclusion.
- **C08:** include at least five paths; assign control/PEP, owner and negative test; contain direct access with restrictive underlying permissions while testing alternatives; define evidence and residual-risk handling.
- **C09:** compare allowed/denied cases and simulate historical requests; canary and review segmented metrics with domain owners; define rollback/hold criteria and evidence; explain rollback can restore prohibited access and may need targeted correction instead.

## G4. Section D model approach

### D01 — Northbridge launch (8 points)
Award one point for each: separate facts from assumptions/specialist questions; assign roles/escalation; classify field groups and separate sensitivity/criticality; design least-privilege raw/masked/aggregated paths; map purpose/consent and residency across jobs/exports/access/metadata/keys/backups; map lifecycle to copies/derivatives; provide five traceable requirement-control-evidence rows; identify residual risks and validation including negative/bypass tests. Deduct for treating illustrative residency/retention statements as universal legal rules.

### D02 — Withdrawal failure (8 points)
A strong response explains that job success may only mean the job completed, not every copy was updated. Contain affected use if appropriate; establish event ID and scope; use lineage plus inventory to reconcile source/lake/warehouse/cache/feature/training datasets/models/partners; preserve minimised evidence; refer trained-model and legal/contractual interpretation to specialists; repair missing lineage and add retry/reconciliation plus stale-copy alerts. Closure needs per-system outcomes and regression tests.

### D03 — Credential exposure (8 points)
Revoke/rotate promptly and restrict access if safe; invalidate sessions/tokens; recognize repository history/logs may persist; inspect clones, CI logs, secret scans, identity logs and accessed resources; replace shared identity with scoped workload identity/secret retrieval; separate permissions; preserve event IDs/timestamps/principal/resource references without copying secret value; run negative/revocation tests; record owner, remediation, reviewer and closure evidence.

### D04 — Policy exists, control uncertain (8 points)
Identify incomplete classification, direct-access bypass, missing period evidence, and the invalid inference that policy approval proves operation. Trace source-labelled requirement → objective → control → implementation → test → evidence. Contain direct access by restricting underlying permissions while assessing impact; block/quarantine unclassified assets where appropriate; reconstruct missing evidence only from trustworthy sources and label gaps honestly. Assign owners/dates, test full grant population and alternate paths, and state that full-period effectiveness is **not demonstrated** until evidence supports it.

## G5. Practical exercise scoring rubrics

Each E exercise is worth 20 points. Award 4 points for each dimension; a technically sound alternative earns credit if its assumptions and validation are explicit.

- **E01 — Governance responsibility matrix:** (1) role clarity: owner/steward/operator/approver/tester/specialist/risk authority distinguished; (2) decision rights and escalation; (3) conflicts and independent testing; (4) review cadence and exception expiry; (5) measurable metrics with source, owner, cadence and action. Each dimension is scored 0–4.
- **E02 — Classification-to-control register:** (1) coverage of all eight fields; (2) separate sensitivity/criticality axes; (3) handling controls linked to metadata; (4) lineage/propagation through joins, features and models; (5) residual risk, owner and human review path.
- **E03 — Access, key and secret lifecycle:** (1) justified least privilege; (2) identity lifecycle and effective revocation; (3) DEK/KEK architecture and key boundaries; (4) secret lifecycle and separation of duties; (5) negative tests and evidence that avoids logging secret material.
- **E04 — Privacy/residency/lifecycle:** (1) purpose/protection and residual risk; (2) residency coverage across storage, processing, movement, access, metadata and keys; (3) copies/derivatives across all ten systems; (4) holds, backup/restore, partner handling; (5) reconciliation evidence and specialist questions.
- **E05 — Control/evidence/enforcement:** (1) requirement-to-control traceability; (2) lifecycle enforcement checkpoints; (3) negative, boundary, integration, bypass and resilience tests; (4) exception/fail-mode design; (5) metrics and ADR trade-offs.

## G6. Section F scoring guidance

Use the 50-point rubric in Section F1. Apply the following deductions where appropriate; do not double-penalize the same defect. Record each deduction and rationale.

- **−1 to −4:** an illustrative assumption is treated as an established legal fact.
- **−1 to −4:** policy approval is presented as proof of implementation or operating effectiveness.
- **−1 to −4:** a protection technique is claimed to guarantee anonymity without assessment.
- **−1 to −4:** deletion covers only the primary table while known copies are ignored.
- **−1 to −4:** fail-open behavior is implicit for a high-risk operation.
- **−1 to −4:** a claimed control has no owner, test or evidence source.

---

# Section H — Self-Assessment and Completion Gate

## H1. Recommended scoring model

| Section | Maximum |
|---|---:|
| A — Beginner | 30 |
| B — Intermediate | 36 |
| C — Advanced | 36 |
| D — Scenarios | 32 |
| E — Practical exercises | 100 |
| F — Integrated assessment | 50 |
| **Total** | **284** |

Section F is a separate cumulative assessment. For a shorter written-only score, report A–D out of 134 and practical/capstone results separately; do not silently change the denominator. Record the denominator used for every topic score. For the 70% topic floor, use the primary topic-specific question IDs in H2 and the associated rubric points; do not count a cross-topic item more than once in the overall total. Where an item tests multiple topics, use the mapped rubric dimensions to assign topic-level evidence rather than duplicating its points.

### Suggested interpretation

- **85% or above overall:** at least **242/284 points** on the full weighted assessment, plus every topic at least 70% and no critical safety gap. This is a recommended learning threshold, not external certification.
- **70–84%:** partial readiness; remediate weak topics and reattempt missed questions.
- **Below 70%:** revisit foundations and complete topic exercises before attempting the capstone.
- **Any critical gap:** do not mark the module Completed solely because the numeric threshold is met. Examples include allowing unknown Restricted access by default, ignoring legal holds, claiming tokenization guarantees anonymity, or claiming compliance without evidence.

These are recommended learning thresholds consistent with the roadmap's suggested 85% average and 70% per-topic floor; they are not external certification criteria.

## H2. Topic-by-topic score and gap log

| Topic | Primary question IDs | Evidence artifact to review | Score / status |
|---|---|---|---|
| 01 — Governance and accountability | A01, A11, B01, C01, E01 | Responsibility matrix, decision rights, escalation, governance metrics | |
| 02 — Classification and criticality | A02, A12, B02, C02, E02 | Classification register, propagation rules | |
| 03 — Identity/access/least privilege | A03, A13, B03–B04, C03, E03 | Role/access matrix, revocation and review procedure | |
| 04 — Encryption/keys/secrets | A04, A14, B05, C04, E03 | Encryption map, key design, secrets lifecycle | |
| 05 — PII protection | A05, A14, B06, C05, E02, E04 | Protection matrix, re-identification risk note | |
| 06 — Purpose/consent/residency | A06, A15, B07–B08, C03, E04 | Purpose/consent register, propagation design, residency map | |
| 07 — Retention/deletion/holds | A07, A15, B09, C06, E04 | Lifecycle matrix, hold-aware deletion procedure, evidence template | |
| 08 — Controls/evidence | A08, B10, C07, D04, E05 | Requirement/control map, evidence plan, test procedure, remediation register | |
| 09 — Governance by design | A09–A10, B11–B12, C08–C09, D01–D04, E05 | Workflow, policy examples, coverage analysis, exception/fail-mode decisions, metrics, ADR | |

### Gap-log template

| Date | Question/exercise ID | Topic | Result | Specific misconception or defect | Remedial action | Owner | Reattempt date | Reattempt result |
|---|---|---|---|---|---|---|---|---|
| | | | Correct / Partial / Incorrect | | | Learner / Reviewer | | |

**Remediation method**
1. Write the exact misconception in one sentence.
2. Revisit the matching topic and its completion gate.
3. Redo the related artifact or scenario without copying the answer key.
4. Ask a reviewer to check against objective criteria.
5. Reattempt the missed question after several days.
6. If the same topic fails twice, redo the topic exercise instead of memorising the answer.

## H3. Topic mastery checklist

Mark **Completed** only when the topic gate and deliverable have been reviewed, practice questions answered, and gaps closed.

- [ ] **Topic 01 — Governance:** explain roles, accountability, decision rights and escalation; responsibility matrix reviewed.
- [ ] **Topic 02 — Classification:** classify and justify fields, separate sensitivity/criticality, define propagation; register reviewed.
- [ ] **Topic 03 — Access:** design least privilege, review, service identity and revocation; access matrix/ADR reviewed.
- [ ] **Topic 04 — Encryption:** explain encryption, key management and secrets; encryption/key design and secrets plan reviewed.
- [ ] **Topic 05 — PII protection:** select/evaluate masking, tokenization, pseudonymisation or de-identification; protection matrix and residual-risk note reviewed.
- [ ] **Topic 06 — Consent/purpose/residency:** translate restrictions into architecture and propagation; purpose register, residency map and specialist-confirmation list reviewed.
- [ ] **Topic 07 — Lifecycle:** design retention, deletion, legal-hold and audit controls; lifecycle matrix, deletion/hold procedure and evidence template reviewed.
- [ ] **Topic 08 — Controls/evidence:** map requirements to controls/evidence and assess operating effectiveness; mapping, evidence plan and test procedures reviewed.
- [ ] **Topic 09 — Governance by design:** integrate governance into workflows and justify automation boundary; workflow, policy examples and coverage analysis reviewed.

## H4. Module completion checklist

- [ ] All nine topic gates are **Completed**.
- [ ] Practice score meets the recommended threshold (85%), with no topic below 70%.
- [ ] Classification-to-control exercise is complete and reviewed.
- [ ] Governance responsibility matrix and escalation paths are explicit.
- [ ] Access, encryption/key, and sensitive-field protection artifacts are consistent.
- [ ] Purpose/consent, residency, retention, deletion and legal-hold flows address copies and derived assets.
- [ ] Each important requirement maps to a control, owner, test and evidence source—or a documented gap.
- [ ] Governance-by-design workflow includes CI/CD and runtime checkpoints.
- [ ] Negative tests demonstrate enforcement at the actual PEP and test known bypass paths.
- [ ] Fail behavior and exception expiry are defined.
- [ ] Evidence and remediation procedures are documented.
- [ ] At least five ADRs have been written across the module, consistent with the roadmap's module-level checklist.
- [ ] Integrated assessment is at or above the recommended threshold and has been defended.
- [ ] A reviewer has examined deliverables; unresolved weaknesses are marked **Needs revision**.
- [ ] Specialist-confirmation items are explicit; no unsupported legal/compliance conclusion is claimed.
- [ ] Only synthetic data are used.

## H5. Final readiness declaration

Complete this statement in your own words:

> I can trace a governance requirement from its source and accountable owner through policy, classification/metadata, implementation, enforcement point, test, evidence, monitoring and remediation. I can identify what must be automated, what requires human authority, what remains uncertain, and how the system behaves when policy information or enforcement dependencies fail.

If you cannot support each clause with a specific artifact or test, record the gap and remediate it before starting or defending the integrated project.
