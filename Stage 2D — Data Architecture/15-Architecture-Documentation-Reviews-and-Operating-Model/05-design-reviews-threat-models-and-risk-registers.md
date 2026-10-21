# Design Reviews, Threat Models and Risk Registers

**Module:** Stage 2D — Data Architecture / Architecture Documentation, Reviews and Operating Model  
**Topic:** 05  
**Learning progression:** Beginner → Intermediate → Advanced  
**Estimated effort:** 7–9 hours (roadmap recommendation)  
**Example status:** All Northbridge Bank names, events, IDs, ratings, dates, architecture details, and evidence in this lesson are synthetic and illustrative. They are not claims about a real bank, a real incident, an actual production environment, or a verified vulnerability.

> **Purpose:** Learn to evaluate an architecture against explicit criteria, analyse plausible threats against data flows and trust boundaries, turn evidence into owned findings and risks, and verify treatment without creating false confidence. This lesson teaches review methods; it does not certify a design as secure or compliant. Qualified specialists and the organisation's formal processes make those determinations.

## Table of contents

1. [Learning objectives](#1-learning-objectives)
2. [Prerequisites and connection to earlier topics](#2-prerequisites-and-connection-to-earlier-topics)
3. [Beginner: core concepts](#3-beginner-core-concepts)
4. [Plan and conduct a design review](#4-plan-and-conduct-a-design-review)
5. [Build review criteria from requirements and quality attributes](#5-build-review-criteria-from-requirements-and-quality-attributes)
6. [Separate findings, threats, risks, issues, assumptions, and questions](#6-separate-findings-threats-risks-issues-assumptions-and-questions)
7. [Threat modelling for data architecture](#7-threat-modelling-for-data-architecture)
8. [Risk assessment and treatment](#8-risk-assessment-and-treatment)
9. [Intermediate worked review: Northbridge Bank ingestion path](#9-intermediate-worked-review-northbridge-bank-ingestion-path)
10. [Risk register and follow-up governance](#10-risk-register-and-follow-up-governance)
11. [Advanced review practices](#11-advanced-review-practices)
12. [Reusable templates and checklists](#12-reusable-templates-and-checklists)
13. [Practical exercises with model answers](#13-practical-exercises-with-model-answers)
14. [Common mistakes and corrections](#14-common-mistakes-and-corrections)
15. [Deliverables, mastery criteria, and completion gate](#15-deliverables-mastery-criteria-and-completion-gate)
16. [Readiness for Topic 06](#16-readiness-for-topic-06)
17. [Practice questions and answer key](#17-practice-questions-and-answer-key)

---

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Plan and run a proportionate architecture review with a defined scope, participants, criteria, evidence package, and outputs.
2. Derive review criteria from stakeholder concerns, requirements, constraints, quality attributes, security and privacy needs, reliability, performance, cost, and operability.
3. Write findings that distinguish observed evidence from assumptions, inferences, and recommendations.
4. Explain the difference between a finding, a threat, a risk, an issue, an assumption, and an unresolved question.
5. Use architecture diagrams and data-flow diagrams (DFDs) to identify assets, actors, entry points, trust boundaries, and plausible threat scenarios.
6. Use a threat-modelling method as a structured prompt without treating it as proof of completeness.
7. Assess likelihood and impact transparently, prioritise risks without false precision, and identify treatment options.
8. Maintain a risk register with sources, owners, treatment actions, due dates, status, residual risk, acceptance authority, and review triggers.
9. Link findings and risks to the relevant DFD flows, architecture views, ADRs, requirements, controls, and migration work.
10. Verify mitigation through appropriate evidence and define objective closure criteria.
11. Escalate material uncertainty, overdue treatment, disputed findings, and residual risk through explicit governance.
12. Prepare a review package that supports the next topic: evaluating reference architectures, standards, and reusable patterns with judgement.

The expected outcome is a review package that another reviewer can understand, challenge, and continue without relying on undocumented verbal context.

## 2. Prerequisites and connection to earlier topics

### 2.1 Roadmap prerequisites

The module roadmap identifies **Topic 02**, **Topic 04**, **P6**, and **P9** as prerequisites or dependencies for Topic 05.

- **Topic 02 — Data-flow and trust-boundary diagrams:** be able to read a DFD, identify external entities, processes, stores, labelled flows, and trust-boundary crossings. Know that a diagram is a model to validate, not automatic proof of implementation.
- **Topic 04 — Architecture decision records and decision log:** be able to find the context, alternatives, rationale, consequences, status, and revisit triggers behind important choices. Review findings may challenge a decision or trigger a new ADR; do not silently rewrite the historical rationale.
- **P6 — Security basics:** identity, access control and least privilege, encryption, key management and secrets, network boundaries, privacy, and evidence design. The roadmap points to the security/privacy module's identity/access, encryption/secrets, and regulatory-controls/evidence topics.
- **P9 — Failure domains and resilience:** understand blast radius, runbooks, failure modes, and resilience testing. The roadmap points to failure-domain and business-continuity/resilience-testing material.

If a prerequisite is unfamiliar, review it before relying on this lesson's examples. This lesson does not replace specialist security, privacy, legal, regulatory, resilience, or penetration-testing expertise.

### 2.2 How the earlier artefacts fit together

| Artefact | Question it answers | How Topic 05 uses it |
|---|---|---|
| Context/container/component/deployment views (Topic 01) | What are the system boundaries, major parts, responsibilities, and deployment locations? | Identify components, dependencies, deployment boundaries, and missing architecture elements. |
| DFD and trust-boundary view (Topic 02) | Which actors, processes, stores, and flows move data across which boundaries? | Anchor threat scenarios to a specific element or flow; identify crossings needing review. |
| Architecture description and viewpoint mapping (Topic 03) | Which stakeholder concerns are represented by which views and evidence? | Derive review criteria and identify uncovered concerns. |
| ADRs and decision log (Topic 04) | Why was a significant choice made, what alternatives were considered, and what consequences were accepted? | Test whether the decision's assumptions remain valid; record new decisions or reconsideration triggers. |
| Requirements, constraints, operational evidence | What must be true, what is prohibited, and what has been demonstrated? | Judge the design against explicit criteria rather than personal preference. |
| Risk register and review findings (this topic) | What needs correction, treatment, acceptance, or further evidence? | Track accountability and close the loop back into architecture artefacts. |

**Traceability principle:** a finding should identify where the concern appears, what evidence supports it, why it matters, and what action or decision is needed. A risk should point back to the threat, finding, assumption, requirement, or dependency that makes it relevant. A mitigation should point forward to the evidence that would demonstrate its effectiveness.

### 2.3 Scope and method caveat

The roadmap names STRIDE as an **illustrative** threat-thinking mnemonic. It does not establish that the repository has formally adopted STRIDE, a risk scoring scheme, a security framework, a compliance standard, or a particular review board. The templates and scoring examples below are learning methods, not organisational policy. Adapt them to approved local processes where those exist.

---

## 3. Beginner: core concepts

### 3.1 What is an architecture design review?

A **design review** is a structured examination of an architecture or proposed change against stated criteria, requirements, constraints, and risks. It asks whether the design is sufficiently understood and whether its important claims are supported by appropriate evidence.

A review is not merely a diagram presentation, a vote on the architect's preferred technology, a compliance certification, or a guarantee that no defect exists. It is a disciplined way to surface gaps early, make disagreements explicit, and assign follow-up work.

**Why it matters:** architecture mistakes can become expensive once interfaces, data contracts, access policies, operational dependencies, and migration plans are implemented. A review gives stakeholders an opportunity to identify avoidable risks before they become harder to change.

**When to use:** use a review for meaningful architecture changes, new trust boundaries, new sensitive-data processing, new external integrations, major platform dependencies, material changes in availability or recovery assumptions, or decisions with significant long-term cost or lock-in. Use a lighter review for low-impact, reversible changes when the review policy permits it.

**Trade-off:** a review consumes time and can slow delivery. An unstructured or excessively broad review consumes even more time while producing weak outcomes. Proportional scope and clear acceptance criteria help balance assurance with delivery speed.

### 3.2 Threat, vulnerability, risk, control, and finding

These terms are related but not interchangeable.

- **Asset:** something of value that requires protection or dependable operation, such as customer records, credentials, data integrity, a critical pipeline, or service availability.
- **Threat actor or source:** an entity or circumstance that could contribute to harm. Examples include an external attacker, malicious insider, compromised partner, careless operator, or accidental system failure. Do not assume every threat requires a malicious human.
- **Threat scenario:** a plausible sequence of events that could cause harm to an asset.
- **Vulnerability or weakness:** a condition that may make a threat scenario possible or more damaging. A diagram's missing annotation alone is not proof of a runtime vulnerability; it may indicate that evidence is missing.
- **Control:** a preventive, detective, or corrective measure intended to reduce likelihood, impact, or both.
- **Risk:** the uncertain possibility of a harmful outcome, considered with its likelihood and impact in a defined context.
- **Finding:** a documented review observation against a criterion, supported by evidence or explicitly labelled as an evidence gap, with significance and follow-up.
- **Issue:** a condition that is already occurring or confirmed, rather than merely possible. Use the term consistently in the local register.
- **Assumption:** something temporarily treated as true but not yet established by sufficient evidence.
- **Unresolved question:** a material question for which an answer is still needed; it should have an owner and target date if it affects a decision or risk.

A threat can exist even when a particular design has strong controls. A finding can concern missing evidence rather than a proven weakness. A risk can arise from uncertainty or dependency, not only from a security threat. A confirmed issue may create further risks.

### 3.3 Evidence, assumption, inference, and recommendation

Use explicit labels so readers can distinguish what is known from what is proposed.

| Type | Meaning | Example in the fictional scenario | How to write it |
|---|---|---|---|
| Evidence / observation | A source was inspected or a test result was observed | “The supplied DFD shows a partner file crossing the external-to-ingestion boundary.” | Cite artefact ID, version, section, flow ID, test, log, or configuration extract. |
| Reported statement | A person or team asserts something | “The platform owner reports that service authentication is enabled.” | Identify speaker/role and date; do not silently upgrade to verified fact. |
| Assumption | Temporarily accepted but unverified | “Assume the partner channel supports authenticated transfer.” | Label it; assign validation owner/date if material. |
| Inference | A reasoned conclusion from evidence | “The DFD does not show how the transfer identity is authorised.” | Explain the reasoning and what evidence could confirm or refute it. |
| Recommendation | A proposed action | “Document the authentication mechanism and verify it against the deployed configuration.” | State owner, expected evidence, and closure criteria. |

**Important:** “Not shown in the diagram” supports a finding that the diagram or evidence package is incomplete. It does **not**, by itself, prove that a control is absent in the deployed system. Phrase the conclusion accordingly.

### 3.4 Review finding versus threat versus risk

| Item | Core question | Example | Typical output |
|---|---|---|---|
| Finding | What did the review observe against a criterion? | “The DFD does not identify the authentication method for flow F-03.” | Finding ID, evidence, severity, owner, action, due date. |
| Threat | What plausible harmful scenario could occur? | “An unauthorised sender could submit a forged partner file if sender identity and integrity are not adequately verified.” | Threat scenario linked to asset, flow, existing controls, gaps. |
| Risk | What uncertain harm may result, and how should it be prioritised? | “A forged file could corrupt downstream customer analytics or trigger incorrect operational action.” | Likelihood, impact, treatment, owner, residual risk. |
| Issue | What confirmed condition already exists? | “A test upload was accepted without the expected validation rule.” This is only an example if the test was actually run. | Incident/defect record, containment, remediation, verification. |
| Assumption | What are we temporarily treating as true? | “Partner files are digitally signed.” | Validation task, owner, due date. |

Do not create duplicate records without links. One finding may contribute to several threat scenarios; one risk may be supported by several findings. Keep IDs stable and use explicit relationships.

### 3.5 Severity and priority

**Severity** describes the significance of a finding under the agreed review rubric. **Priority** describes how urgently the team should act, considering impact, exposure, dependencies, and timing. A high-severity finding may have a lower immediate priority if it is not applicable to the current release and exposure is contained; a moderate finding can be urgent if it blocks a near-term critical milestone. Define local meanings before scoring.

The roadmap suggests a simple finding scale: **blocker, major, minor, advisory**. A useful illustrative interpretation is:

| Level | Meaning | Typical response |
|---|---|---|
| Blocker | A critical requirement or safety condition is unmet, or a material unresolved risk makes proceeding unjustified under the agreed gate. | Do not proceed through the affected gate until corrected or handled through authorised governance. |
| Major | Material weakness, missing evidence, or unresolved decision likely to affect security, privacy, reliability, data integrity, or delivery. | Named owner and near-term corrective plan; escalation if gate-critical. |
| Minor | Limited impact or bounded gap that should be corrected but does not independently invalidate the design. | Planned correction with due date. |
| Advisory | Improvement or question with no current material blocker established. | Consider, document rationale if declined, and avoid presenting it as a confirmed defect. |

These labels are illustrative. The review charter must define how severity affects release gates, escalation, and risk acceptance. Do not let a label replace the explanation of impact.

---

## 4. Plan and conduct a design review

### 4.1 Review workflow

Use this sequence as a repeatable baseline. Tailor it to change size and risk.

```text
Trigger and scope
      ↓
Identify stakeholders, criteria, and decision rights
      ↓
Collect versioned architecture artefacts and evidence
      ↓
Check completeness and traceability before the meeting
      ↓
Walk the design against criteria and trust boundaries
      ↓
Record findings, threats, risks, disagreements, and gaps
      ↓
Agree actions, owners, due dates, and closure evidence
      ↓
Publish the report and update linked artefacts
      ↓
Verify treatment, residual risk, and gate outcome
      ↓
Feed recurring lessons into patterns and standards
```

### 4.2 Scope and review charter

Before the review, record:

- **Purpose:** the decision or change being reviewed and the decision the review should enable.
- **Scope:** systems, data classes, flows, environments, interfaces, migration phase, and exclusions.
- **Review type:** architecture quality, security/threat review, operational readiness, change review, or a combined review.
- **Criteria:** explicit checks tied to requirements, constraints, quality attributes, and agreed policies.
- **Inputs:** current diagrams, DFD, architecture description, ADRs, requirement list, risk register, ownership map, deployment/configuration evidence, test results, runbooks, and open questions as relevant.
- **Participants:** author/architect, lead reviewer, domain/data owner, security/privacy specialist, platform/operations representative, delivery owner, and scribe as needed.
- **Decision rights:** who can approve the design, accept a residual risk, defer the decision, or escalate. A reviewer is not automatically the risk-acceptance authority.
- **Outputs:** review report, findings, threat table, risk register updates, actions, decisions, and affected artefacts.
- **Gate and timing:** what must be true before proceeding and when follow-up will occur.

**Why this matters:** without a scope and criteria, the review can become a debate about personal preferences or drift into topics outside the decision being made. Scope exclusions should be explicit, justified, and visible as residual uncertainty—not hidden.

### 4.3 Participants and responsibilities

| Role | Primary responsibility | Must not be assumed to do |
|---|---|---|
| Architecture owner / author | Explain intended design, context, decisions, assumptions, and evidence; respond to findings. | Self-certify every control or close findings without evidence. |
| Lead reviewer | Keep review criteria, scope, and discussion disciplined; distinguish facts from opinions. | Substitute personal preference for agreed criteria. |
| Security reviewer | Analyse threats, identity, access, boundary crossings, controls, and evidence within their remit. | Guarantee that all attacks are impossible. |
| Data/privacy owner | Explain data sensitivity, permitted uses, retention, minimisation, and relevant handling constraints. | Make unsupported legal or regulatory conclusions. |
| Platform/operations owner | Evaluate failure domains, observability, recovery, support access, runbooks, and operational burden. | Treat an undocumented operational process as proven. |
| Risk owner | Account for treatment, residual risk, escalation, and review dates. | Delegate accountability entirely to the person implementing the fix. |
| Scribe / coordinator | Maintain findings, IDs, decisions, action owners, and links. | Resolve technical disagreements by rewriting them as consensus. |
| Risk-acceptance authority | Accept residual risk within delegated authority, if applicable. | Accept risks outside their authority or without understanding duration and impact. |

One person may fill more than one role in a small team, but separate the responsibilities conceptually. Where independence matters, avoid having the design author be the sole reviewer of a high-impact control.

### 4.4 Preparation checklist

Before the meeting, confirm:

- [ ] Scope, review trigger, decision to be supported, and exclusions are stated.
- [ ] Current diagrams have IDs/versions and match the intended design baseline.
- [ ] Every relevant DFD flow is labelled; trust-boundary crossings are visible.
- [ ] Stakeholder concerns and requirements have traceable identifiers.
- [ ] ADRs identify the decisions and assumptions behind important design choices.
- [ ] Data classification, ownership, retention, and permitted use are available where relevant.
- [ ] Security, identity, network, encryption, and secret-management evidence is supplied or explicitly marked unavailable.
- [ ] Reliability objectives, failure domains, recovery expectations, and runbooks are supplied where relevant.
- [ ] Performance/capacity and cost assumptions are stated rather than implied.
- [ ] Open questions, prior findings, exceptions, and accepted risks are visible.
- [ ] Reviewers know which criteria and severity definitions will be used.

A missing artefact may itself be a review finding, but do not infer a missing deployed control solely from missing documentation.

### 4.5 During and after the review

**During:** walk through the design from actor to data store and from deployment boundary to operational dependency. Ask which requirement supports each significant element, what evidence supports each important claim, and what happens when a dependency fails or trust changes. Record dissent and uncertainty without forcing artificial consensus.

**After:** publish findings with evidence locations; create or update risk entries; assign one accountable owner per action; set due dates and escalation paths; link to affected ADRs and diagrams; and define closure evidence. Verify the result by re-review, test, configuration inspection, or another suitable method. “Developer says fixed” is a status update, not necessarily closure evidence.

---

## 5. Build review criteria from requirements and quality attributes

### 5.1 What makes a good criterion?

A review criterion is a testable question or condition derived from a requirement, constraint, agreed principle, stakeholder concern, or necessary quality attribute. A criterion should be specific enough that reviewers can state what evidence would satisfy it.

Weak criterion: “Security must be good.”  
Stronger criterion: “For every flow carrying restricted customer data across a trust boundary, the design identifies the sender/receiver identities, authorisation decision, transport protection, data validation, logging expectations, and evidence needed to verify the deployed configuration.”

The stronger statement is still a proposed review criterion, not a claim that the system meets it. Local security requirements and specialists determine the actual required controls.

### 5.2 Criteria catalogue

Use only the categories relevant to the change; document exclusions.

| Area | Review questions | Example evidence | Common gap |
|---|---|---|---|
| Requirements and scope | Are in-scope stakeholder concerns represented? Are acceptance conditions testable? | Requirement IDs, concern-to-view matrix, acceptance tests | Requirement says “near real time” without a measurable freshness target. |
| Data flow and trust | Are actors, processes, stores, flows, classifications, and boundary crossings represented? | Versioned DFD, flow inventory, integration contract | Flow exists in configuration but not in the diagram. |
| Identity and access | Are workload and human identities identified? Are permissions scoped to required actions and data? | IAM policy/configuration, identity flow, access tests | Diagram labels “secure API” without identifying caller identity or authorisation. |
| Confidentiality and privacy | Is sensitive data minimised, protected, retained appropriately, and accessible only for justified purposes? | Classification, retention policy, masking design, access evidence | Logs or debug exports may copy sensitive fields without a stated need. |
| Integrity and quality | Are schema, provenance, validation, deduplication, and replay semantics clear? | Contract tests, validation rules, lineage, reconciliation results | Invalid or replayed files can enter curated datasets without an identified control. |
| Reliability and recovery | Are failure domains, retries, idempotency, RPO/RTO where applicable, backup, restore, and runbooks addressed? | Failure analysis, restore test, runbook, resilience test | Retry behaviour can duplicate records or hide persistent failure. |
| Performance and scale | Are volume, throughput, concurrency, latency/freshness, and growth assumptions explicit? | Load test, benchmark, capacity model, queueing assumptions | Capacity claim is based only on average volume. |
| Cost and sustainability | Are storage, compute, egress, retention, support, and dual-running costs understood? | Cost estimate, usage assumptions, scenario comparison | Migration plan ignores parallel-running costs. |
| Operability | Are ownership, alerting, dashboards, support access, incident handling, and runbooks defined? | Ownership map, telemetry design, runbook, alert test | No team owns failed-file triage. |
| Dependencies and change | Are external dependencies, contracts, versioning, rollback, and migration steps clear? | Dependency inventory, ADR, migration plan, rollback test | Partner contract changes without compatibility handling. |
| Governance and evidence | Are important claims traceable, uncertainties visible, and decisions/risks assigned? | ADRs, evidence register, risk register, exception records | “Approved” appears without approver, scope, date, or conditions. |

### 5.3 Criterion-to-evidence matrix

A criterion is not passed merely because an artefact exists. Evidence must be relevant, current, and strong enough for the claim.

| Criterion ID | Criterion | Evidence required | Evidence state | Reviewer conclusion | Follow-up |
|---|---|---|---|---|---|
| C-01 | Every sensitive boundary-crossing flow is identified | DFD + flow inventory | Available / partial / missing | Met / not met / uncertain | Owner + date |
| C-02 | Workload identity and permission scope are clear | Identity design + policy/config evidence | Available / partial / missing | Met / not met / uncertain | Owner + date |
| C-03 | Recovery claims have supporting evidence | Recovery objective + restore/resilience test | Available / partial / missing | Met / not met / uncertain | Owner + date |

Use “uncertain” when evidence is insufficient. Do not force a binary pass/fail if the review package cannot support it.

---

## 6. Separate findings, threats, risks, issues, assumptions, and questions

### 6.1 A finding's minimum structure

A useful finding contains:

1. **ID and title:** stable, concise, and unique.
2. **Criterion:** the requirement or review condition being assessed.
3. **Evidence and location:** artefact ID/version, diagram flow, configuration, test, log, interview, or missing evidence explicitly noted.
4. **Observation:** what is actually shown, measured, or reported.
5. **Interpretation:** why the observation does or may not satisfy the criterion.
6. **Impact:** the plausible architectural or business consequence.
7. **Severity and priority:** using the agreed rubric, with rationale.
8. **Recommendation or required outcome:** what must change or be demonstrated; avoid over-prescribing a technology without reason.
9. **Owner and due date:** one accountable person/role and a target date.
10. **Closure criteria and evidence:** what observable result will permit closure.
11. **Links:** relevant threat, risk, ADR, requirement, DFD flow, and action record.

### 6.2 Evidence-based finding example

**F-01 — Authentication mechanism is not represented for partner ingestion flow F-03**

- **Criterion:** C-02, the caller identity and authorisation path for the partner transfer must be understandable and verifiable.
- **Evidence:** In illustrative artefact `DFD-NB-02 v0.4`, flow `F-03` is labelled “Partner file upload” and crosses the external-partner to ingestion boundary. The supplied diagram does not name the authentication mechanism or identify where sender authorisation is enforced.
- **Observation:** The current diagram omits these details.
- **Interpretation:** The review cannot determine from the provided artefact how sender identity is established or how unauthorised uploads are prevented.
- **Limit:** This is a documentation/evidence gap. It does not prove the deployed system lacks authentication.
- **Potential impact:** If effective sender authentication and authorisation are absent or misconfigured, an unauthorised file could enter downstream processing.
- **Severity:** Major, illustrative, because the flow is in scope and handles synthetic customer data. Final severity depends on the review's agreed rubric and additional evidence.
- **Recommendation:** Document the intended identity and authorisation path, then inspect the relevant configuration or test evidence.
- **Owner:** Ingestion service owner (role, not a named real person).
- **Due:** Before the architecture gate for the proposed release (the actual date must be assigned by the project).
- **Closure criteria:** Versioned DFD/description names the identity and enforcement point; a reviewer inspects relevant configuration or a suitable test result; linked risk is reassessed.
- **Links:** `F-03`, `C-02`, `T-01`, `R-01`, and the relevant ADR if the mechanism is an architecture decision.

This is stronger than “authentication missing,” because it distinguishes the evidence gap from a confirmed control failure.

### 6.3 Finding severity and risk priority are different

A finding severity helps the review team classify the observation. Risk priority helps decide what to treat first. Do not automatically copy the finding's severity into every linked risk: a finding can be minor while revealing a severe risk, or major because evidence is absent while the actual risk remains uncertain.

### 6.4 Disagreement and uncertainty

When reviewers disagree:

- capture the claim each person is making;
- identify the evidence each claim depends on;
- record missing evidence or different assumptions;
- identify who can resolve the disagreement and by when;
- escalate if the disagreement affects a gate or risk acceptance.

Do not mark a finding “closed” just because the team agrees to disagree. Record the unresolved issue, decision authority, and any residual risk.

---

## 7. Threat modelling for data architecture

### 7.1 What threat modelling does

**Threat modelling** is a structured way to reason about how a system or data flow could be misused, attacked, or fail in ways that harm assets. It starts with a scoped model of the system, identifies valuable assets and trust boundaries, develops plausible scenarios, considers existing controls, and decides what needs treatment or further evidence.

Threat modelling is useful early in design and again when architecture changes: a new external integration, identity provider, data class, deployment environment, administrative interface, replay path, or AI retrieval component can change the threat surface.

It is not a penetration test, a proof that all threats have been found, or a substitute for implementation verification. Its quality depends on the model's completeness, the reviewers' knowledge, the assumptions disclosed, and the follow-up performed.

### 7.2 Threat-modelling workflow

1. **Scope:** name the system, data classes, environments, actors, and change under review.
2. **Model the system:** use the Topic 01 views and Topic 02 DFD. Mark processes, stores, flows, external entities, deployment locations, and trust boundaries.
3. **Identify assets:** confidentiality, integrity, availability, provenance, privacy, credentials, auditability, and business decisions that depend on the data.
4. **Identify entry points and privileges:** file transfer endpoints, APIs, schedulers, service identities, admin consoles, notebooks, logs, backup/restore, support paths, and CI/CD/control-plane paths where relevant.
5. **Enumerate plausible scenarios:** describe the actor or cause, preconditions, action, affected asset, and harmful outcome. Avoid vague entries such as “hacking.”
6. **Record existing controls and evidence:** distinguish a designed control, a reported control, and a control whose implementation/effectiveness has been verified.
7. **Assess risk:** estimate likelihood and impact with stated assumptions and a defined scale.
8. **Choose treatment:** avoid, mitigate, transfer/share where meaningful, or accept within authorised governance.
9. **Record residual risk and evidence needs:** treatment reduces risk; it does not necessarily eliminate it.
10. **Validate and revisit:** test assumptions, review after material changes, and update linked DFDs, ADRs, and risk entries.

### 7.3 Threat-model scope for data platforms

Data architecture reviews should look beyond the obvious ingestion-to-storage path. Consider where relevant:

- partner files, APIs, event streams, batch transfers, and schema/contract changes;
- identity and permissions for humans, workloads, services, and administrators;
- data stores, staging areas, raw/curated zones, replicas, caches, exports, and temporary files;
- logs, metrics, traces, dead-letter queues, debugging dumps, notebooks, and support workflows;
- backups, restore paths, replication, replay, reprocessing, and disaster-recovery environments;
- data classification propagation, masking, tokenisation, aggregation, and re-identification possibilities;
- control-plane access such as identity configuration, catalogues, orchestration, CI/CD, secrets, and policy administration;
- multi-tenant or cross-domain access boundaries;
- ML/AI pipelines where relevant, including training data provenance, feature access, embedding stores, retrieval permissions, prompt injection, and data poisoning;
- failure and misuse scenarios: duplicate processing, stale data, incorrect joins, loss of provenance, denial of service, or unauthorised changes.

Not every topic applies to every architecture. State scope decisions and exclusions rather than filling the threat table with generic threats unrelated to the system.

### 7.4 Trust boundaries and data-flow analysis

A trust boundary is a change in control, identity, ownership, or assumptions about who can access or influence a component. Examples include internet-to-ingestion, partner-to-enterprise, one cloud account/project to another, production-to-nonproduction, human-to-service, application-to-database, and tenant-to-tenant boundaries.

For every important crossing, ask:

- Who initiates the flow and how is identity established?
- What authorisation decision is made, where, and against which resource/action?
- What is the data classification and minimum necessary payload?
- How are integrity, schema, size, replay, duplicate, and malformed-input concerns handled?
- What transport protection and key/secret management are intended, and what evidence verifies them?
- What is logged, who can read those logs, and could logs expose sensitive data?
- What rate/volume limits, failure handling, retries, and alerting exist?
- Which team owns the flow and responds when it fails?
- What happens during replay, backup restore, emergency support, or migration?

The answers should link to actual architecture flows and evidence. A boundary crossing is not automatically a vulnerability; it is a place where assumptions and controls need explicit analysis.

### 7.5 STRIDE as an illustrative prompt

The roadmap mentions **STRIDE** as a simple illustrative mnemonic. It expands to:

- **Spoofing:** pretending to be another identity or component.
- **Tampering:** unauthorised modification of data, configuration, or messages.
- **Repudiation:** inability to establish what action occurred or who performed it when reliable evidence is required.
- **Information disclosure:** exposing data to an unauthorised party.
- **Denial of service:** preventing or degrading intended service.
- **Elevation of privilege:** obtaining capabilities beyond the intended permissions.

Use these categories to generate questions about a specific flow or component. They are not an adopted repository standard and do not guarantee completeness. Supplement them with data-specific concerns such as provenance loss, incorrect transformation, privacy leakage, replay errors, excessive retention, and operational failure where relevant.

### 7.6 Threat analysis table: reusable form

| ID | Element / flow | Asset and classification | Threat category (illustrative) | Threat scenario | Existing control and evidence state | Gap / uncertainty | Likelihood + rationale | Impact + rationale | Exposure score / basis | Priority / linked risk | Treatment / mitigation | Owner | Verification evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-xx | Flow or component ID | Asset; class if known | STRIDE prompt or data-specific category; do not imply formal adoption | Actor/cause → action → harm | Implemented / reported / designed / unknown; cite evidence | What remains unproven | Scale + rationale, or unknown | Scale + rationale, or unknown | L × I only if a defined scale is used; otherwise unknown | Priority rationale and R-xx link | Specific action or investigate | Role/name | Test/config/review evidence |

Do not list a control as effective solely because it appears in a design diagram. A design annotation describes intent; configuration inspection, tests, operational evidence, or specialist assessment may be needed to establish implementation and effectiveness.

---

## 8. Risk assessment and treatment

### 8.1 What is a risk assessment?

Risk assessment estimates the possibility and significance of a harmful outcome in a defined context. It supports prioritisation; it does not remove uncertainty. A useful risk statement has a causal shape:

> Because **[condition or uncertainty]**, **[event or scenario]** may occur, causing **[impact to asset, service, data, or objective]**.

Example: “Because the ingestion flow's sender-authorisation mechanism has not yet been evidenced, an unauthorised sender may be able to submit a file, potentially corrupting downstream customer analytics and consuming incident-response capacity.” This is a scenario, not a claim that unauthorised upload has occurred.

### 8.2 Qualitative versus quantitative assessment

**Qualitative assessment** uses defined categories such as low/medium/high or ordinal scales. It is relatively fast and useful when reliable numeric data is unavailable. Its limitations include subjective ratings, inconsistent interpretation, and loss of detail within each category.

**Quantitative assessment** estimates numeric quantities such as expected loss, frequency, duration, or financial impact when credible data and a suitable model exist. It can support comparisons but depends on data quality, model assumptions, uncertainty ranges, and scope. A numeric estimate is not automatically more accurate than a well-explained qualitative judgement.

The roadmap gives an illustrative ordinal scoring example: likelihood and impact each on a 1–5 scale, with exposure calculated as likelihood × impact (range 1–25). This lesson uses that only as a **ranking aid**. It is not a probability, monetary loss estimate, or universal risk formula.

### 8.3 Illustrative likelihood and impact scales

Define scale meanings before scoring. The following is a training example, not an organisation-wide policy.

| Score | Likelihood (illustrative) | Impact (illustrative) |
|---:|---|---|
| 1 | Unlikely under stated assumptions; no known direct path in current scope | Negligible and readily recoverable effect |
| 2 | Possible but would require uncommon conditions | Limited local disruption or contained data-quality effect |
| 3 | Plausible under realistic conditions; important evidence uncertain | Material operational disruption or meaningful data integrity/confidentiality impact |
| 4 | Likely in the scenario or supported by relevant evidence | Major service/data impact, broad remediation, or substantial business consequences |
| 5 | Expected or repeatedly observed in a comparable context | Severe, widespread, prolonged, or difficult-to-reverse harm |

A team must adapt these definitions to its context and avoid assigning a numeric score when evidence is insufficient. Use “unknown” or a range where appropriate and make the uncertainty itself visible.

### 8.4 Example scoring, with limitations

Assume, solely for training, a reviewer rates a threat scenario likelihood **3** and impact **5**. The simple exposure score is 3 × 5 = **15/25**. This suggests high review attention under the example's ranking scheme. It does **not** mean a 60% probability, a 15% chance of loss, or a quantified monetary expectation.

Scores should be accompanied by rationale, evidence quality, uncertainty, and treatment urgency. Multiplying ordinal values does not guarantee meaningful mathematical distance between scores. Avoid comparing scores from teams using different scale definitions. Do not sum scores across risks and call the result enterprise risk without a valid aggregation method.

### 8.5 Risk priority and treatment choices

Prioritisation should consider more than a score:

- severity of potential harm and sensitivity/criticality of the asset;
- exposure and plausibility of the scenario;
- quality of evidence and uncertainty;
- existing controls and their demonstrated effectiveness;
- duration of exposure and ease of exploitation or accidental occurrence;
- dependency on other fixes and the timing of a release or migration;
- reversibility and available containment;
- the authority required to accept residual risk.

Common treatment choices are:

| Treatment | Meaning | Example | Limitation |
|---|---|---|---|
| Avoid | Change scope or design so the risky activity does not occur | Do not permit a sensitive dataset to be exported to an unmanaged destination | May reduce capability or require a different design. |
| Mitigate | Reduce likelihood and/or impact through controls or design changes | Enforce sender identity, validate the file, constrain permissions, and test the path | Controls need evidence and ongoing operation; residual risk remains. |
| Transfer/share | Allocate part of the financial or operational consequence through a contract, insurance, or service arrangement where meaningful | Contractual service commitment for a third-party dependency | Does not remove accountability for data, customers, or all consequences; contract is not a technical control. |
| Accept | Authorised decision to tolerate residual risk within defined boundaries | Accept a bounded low residual risk for a limited period with compensating controls and a review date | Requires an authorised owner, rationale, duration, monitoring, and revisit trigger. |

“Transfer” is not a synonym for making risk disappear. Outsourcing a service does not outsource all accountability. “Mitigate” is not complete until the action and evidence are defined.

### 8.6 Inherent and residual risk

**Inherent risk** is assessed before considering the relevant controls (or under a clearly defined baseline). **Residual risk** is what remains after the proposed or implemented treatment is considered. Teams sometimes use “current risk” to mean risk under controls already implemented and “target residual risk” for the expected result after planned treatment. Define these labels consistently.

Do not lower a risk score merely because a mitigation is planned. Until implemented and appropriately verified, the control may not reduce current risk. It is reasonable to record an expected target residual assessment, but label it as a forecast and state its assumptions.

### 8.7 Risk acceptance governance

An acceptance record should state:

- exact risk ID and scenario being accepted;
- current and residual assessment, with uncertainty;
- business rationale and alternatives considered;
- existing compensating controls and monitoring;
- acceptance authority and evidence of approval;
- scope, environment, data class, and duration covered;
- expiry or review date and explicit revisit triggers;
- conditions that invalidate acceptance, such as a new integration, increased data sensitivity, control failure, or material change in exposure.

A project deadline is not, by itself, sufficient justification for accepting a risk. If no authorised acceptance process is known, record that governance gap and escalate; do not invent authority or imply approval.

---

## 9. Intermediate worked review: Northbridge Bank ingestion path

### 9.1 Scenario and assumptions

Northbridge Bank is fictional. The scenario is a synthetic partner-file ingestion service that receives daily files containing customer/account data, validates them, stores raw copies, and produces curated datasets for internal analytics.

For the worked review, assume the following **review inputs**, not verified production evidence:

- `ARCH-NB-01 v0.6`: context/container/deployment views identify a partner transfer service, ingestion service, raw data store, validation process, curated store, and analyst access path.
- `DFD-NB-02 v0.4`: the DFD shows flow `F-03` from the external partner to ingestion, `F-04` from ingestion to raw storage, `F-05` through validation, and `F-06` from validation to curated storage. It marks the external-to-ingestion and production-to-analytics trust boundaries.
- `ADR-NB-01`: an illustrative accepted decision chooses a managed ingestion service to reduce operational burden; its record says the team will validate identity, failure handling, and cost assumptions before production approval.
- `EVID-NB-01`: a synthetic package index says configuration evidence for sender authentication and restore-test evidence have not yet been supplied.
- No test, exploit, incident, or production configuration has been inspected for this exercise.

These assumptions intentionally create **evidence gaps**. They do not establish that authentication, restore capability, or any other control is absent.

### 9.2 Sample review criteria

| ID | Criterion | Evidence expected | Initial status from synthetic package |
|---|---|---|---|
| C-01 | Sensitive flows and trust-boundary crossings are represented consistently | DFD + flow inventory + architecture views | Partially represented; classification and identity details need clarification |
| C-02 | Sender identity and upload authorisation are defined and verifiable | Identity design + configuration/test evidence | Evidence not supplied; outcome uncertain |
| C-03 | File integrity and schema validation are defined before downstream use | Validation design + contract/test evidence | Design mentions validation; effectiveness not demonstrated in supplied package |
| C-04 | Retry/replay and duplicate handling preserve data integrity | Processing semantics + tests | Open question in the synthetic package |
| C-05 | Backup/restore and recovery assumptions are supported | Recovery objectives + restore test/runbook | Restore-test evidence not supplied |
| C-06 | Operational ownership and failed-file response are clear | Ownership map + runbook + alerting design | Ownership role identified; runbook evidence incomplete |
| C-07 | Data is not exposed through logs or unmanaged exports beyond intended access | Logging/export design + access evidence | Open question; no evidence of an actual leak |

### 9.3 Sample findings

| Finding | Evidence / observation | Interpretation and possible impact | Severity (illustrative) | Action and closure criteria |
|---|---|---|---|---|
| F-01: Sender identity not evidenced | `DFD-NB-02 v0.4`, `F-03` says “Partner file upload”; `EVID-NB-01` lists no authentication configuration/test evidence | Review cannot verify sender identity or authorisation; if the control is ineffective, forged or unauthorised files may enter processing | Major pending evidence | Ingestion owner documents identity/enforcement path; reviewer inspects suitable configuration or test evidence; update DFD and link risk. |
| F-02: File validation effectiveness unproven | `ARCH-NB-01 v0.6` shows a validation process; no contract-test output supplied | A box in a diagram does not demonstrate validation rules, failure handling, or enforcement; malformed data could propagate if validation is inadequate | Major or minor depending on data impact and gate | Data pipeline owner supplies rules and test evidence for invalid schema, malformed fields, and rejected-file handling; define expected outcomes. |
| F-03: Replay and duplicate semantics unclear | DFD shows a batch path but does not describe retry/idempotency behaviour | Retries or replays could duplicate records or produce inconsistent aggregates if semantics are not designed correctly | Major if downstream decisions depend on correctness; otherwise severity to be agreed | Pipeline owner documents idempotency/deduplication and replay policy; demonstrate with a repeat/replay test and reconciliation evidence. |
| F-04: Recovery claim lacks test evidence | `EVID-NB-01` says no restore-test evidence supplied | Recovery capability cannot be confirmed from the package; outage duration or data loss may exceed expectations if recovery is ineffective | Major pending recovery objectives | Platform/operations owner supplies recovery objectives, runbook, and a dated restore/resilience-test result; record limitations and residual risk. |
| F-05: Logging data handling unspecified | Package does not identify which file fields appear in logs or who can access logs | Sensitive fields may be copied into operational telemetry; this is a plausible scenario, not a confirmed exposure | Minor/major depending on classification and evidence | Data/security owner documents log fields, access, retention, masking, and tests or inspection evidence. |

Severity is deliberately provisional where impact or evidence remains unknown. The review lead must apply the agreed rubric and record the rationale rather than treating the table as a universal scorecard.

### 9.4 Threat analysis for selected flows

| Threat ID | Flow / asset | Threat category (illustrative) | Scenario | Existing control / evidence state | Assessment | Treatment | Linked records |
|---|---|---|---|---|---|---|---|
| T-01 | `F-03`; incoming customer data | Spoofing / unauthorised submission | An unauthorised sender submits a forged file if sender identity/authorisation is ineffective | Mechanism and test evidence not supplied; control status unknown | Likelihood unknown pending evidence; impact potentially high due to downstream data integrity and incident response | Verify identity and authorisation path; test rejected unauthorised upload; document logging and alerting | F-01, R-01, ADR-NB-01 |
| T-02 | `F-04`/`F-05`; raw and curated records | Tampering / data-integrity failure | Malformed or tampered file passes validation or replay handling and alters downstream results | Validation process shown; rules and test evidence incomplete | Plausible; impact depends on downstream decisions and reconciliation controls | Define schema/integrity checks, quarantine/reject behaviour, idempotency and reconciliation; test representative failure cases | F-02, F-03, R-02 |
| T-03 | Logs/support path; customer data | Information disclosure | Sensitive fields are emitted to logs or exported during troubleshooting and become accessible to a broader audience | Logging and support-path evidence not supplied | Exposure unknown; validate actual logged fields, access, retention, and support procedures | Minimise logged data, restrict access, set retention, and test redaction/permissions where required | F-05, R-03 |
| T-04 | Recovery path; raw/curated data | Availability / recovery-integrity failure | Restore or replay fails to recover consistent data within the agreed objective | Restore test not supplied | Capability unverified; impact depends on recovery needs and source replayability | Run a controlled restore/reconciliation test; document recovery limits and dependencies | F-04, R-04 |

No row states that an attack or failure has occurred. These are plausible scenarios derived from the synthetic architecture and evidence gaps.

### 9.5 Illustrative risk register entries

For this training example, use 1–5 ordinal scales and multiply likelihood × impact only as a ranking aid. Where likelihood is unknown, do not manufacture a number. A provisional score may be used only if the review explicitly records the assumption and uncertainty.

| Risk ID | Risk statement | Source | Current assessment | Exposure / priority | Treatment | Owner | Due / trigger | Status and closure evidence | Residual risk |
|---|---|---|---|---|---|---|---|---|---|
| R-01 | Because sender identity/authorisation evidence is unavailable, an unauthorised upload may be accepted if the effective control is absent or misconfigured, corrupting downstream data | F-01, T-01, `F-03` | Likelihood unknown; impact potentially high | Not scored while likelihood is unknown; collect evidence before gate | Verify mechanism, inspect config, test rejected unauthorised sender, document alerting | Ingestion service owner | Before architecture gate; revisit if partner/auth method changes | Open until evidence reviewed; closure requires configuration/test evidence and updated DFD | To be reassessed after verification; not assumed low merely because action is planned |
| R-02 | Because validation and replay semantics are not demonstrated, malformed or duplicate data may affect curated outputs | F-02, F-03, T-02 | Likelihood/impact require data-owner input; integrity consequence may be material | Not scored until assumptions and scale are agreed; integrity concern requires review | Specify schema checks, quarantine, idempotency and reconciliation; test invalid/replayed files | Data pipeline owner | Before production readiness; revisit on schema/processing change | Open; close after tests show expected reject/deduplicate/reconcile behaviour | Depends on test scope and operational monitoring |
| R-03 | Because logging/support data handling is unspecified, sensitive data may be copied to logs or support exports accessible beyond the intended audience | F-05, T-03 | Likelihood unknown; impact depends on classification, field content, and log access | Not scored while classification/log evidence is missing | Inspect log fields and permissions; minimise/mask sensitive fields; define retention and support process | Data/security owner | Before release gate; revisit on logging or support-path change | Open; close when log inspection and access/retention evidence meet criterion | Residual exposure may remain through privileged support paths; document it |
| R-04 | Because restore capability has not been evidenced, recovery may exceed expected objectives or produce inconsistent datasets | F-04, T-04 | Impact depends on recovery objectives; current capability unverified | Not scored until recovery objectives and test evidence are available | Define objectives, run restore/reconciliation test, update runbook | Platform/operations owner | Before operational readiness; revisit after platform/storage change | Open until test result and runbook reviewed | Record actual test limits and any accepted recovery gap |

**Owner distinction:** the risk owner is accountable for ensuring the risk is assessed and treated or escalated. The person implementing a control may be a different action owner. Name both when necessary; do not leave accountability ambiguous.

### 9.6 Review report summary and gate recommendation

**Summary:** The synthetic package provides a useful starting architecture model, but several material control and operability claims are not yet supported by evidence. The review has identified four principal risk themes: sender identity, validation/replay integrity, sensitive logging, and recovery. These are evidence gaps and plausible risk scenarios—not verified vulnerabilities or incidents.

**Illustrative recommendation:** do not claim the design is fully reviewed or ready for a gate until the gate owner has considered the unresolved evidence and risks. Require the assigned owners to supply evidence and update the linked records. The authorised gate/acceptance authority determines whether the design may proceed under the organisation's actual process.

### 9.7 Cross-artefact consistency check

| Claim / element | Architecture view | DFD / flow | ADR | Finding / risk | Consistency test |
|---|---|---|---|---|---|
| Partner upload crosses an external trust boundary | `ARCH-NB-01 v0.6` shows partner and ingestion service | `DFD-NB-02 v0.4`, `F-03` | `ADR-NB-01` mentions managed ingestion | F-01 / R-01 | Names and boundaries match; identity details remain an explicit gap. |
| Validation precedes curated storage | Architecture view shows validation component | `F-05`/`F-06` | ADR does not replace validation specification | F-02 / R-02 | Ensure flow ordering is consistent and test evidence exists. |
| Recovery can meet stated needs | Deployment/recovery view should show relevant stores and dependencies | Restore/replay flows may need explicit representation | ADR assumptions about operations may be affected | F-04 / R-04 | No conclusion until recovery objectives and test evidence are reviewed. |
| Logs/support paths may carry sensitive data | Operational view may not yet include these paths | Add flow if data movement is confirmed; mark as unverified if not | New decision may be needed if logging design changes | F-05 / R-03 | Do not draw a confirmed data flow without evidence; record the discovery task. |

A consistency check looks for contradictory names, missing elements, mismatched boundaries, and claims that appear in one artefact but are unsupported elsewhere. The goal is not to force every detail into every diagram; each artefact should provide the level of detail appropriate to its purpose and link to the others.

---

## 10. Risk register and follow-up governance

### 10.1 Risk-register fields

A risk register is a living record, not a one-time spreadsheet. Minimum useful fields include:

| Field | Purpose |
|---|---|
| Risk ID and title | Stable reference used by findings, ADRs, and action trackers. |
| Risk statement | Condition/uncertainty → possible event → impact. |
| Source links | Finding, threat, requirement, assumption, dependency, ADR, flow, or incident record. |
| Asset / scope | What system, data, environment, or objective is affected. |
| Inherent/current assessment | Likelihood, impact, rationale, uncertainty, and evidence basis. |
| Existing controls | Controls already implemented and their evidence state. |
| Treatment decision | Avoid, mitigate, transfer/share, or accept; include rationale. |
| Actions | Specific tasks, each with an accountable owner, due date, and dependency. |
| Risk owner | Person/role accountable for treatment and escalation. |
| Status | Open, in treatment, awaiting evidence, accepted until date, monitoring, closed, or other locally defined values. |
| Residual risk | Assessment after verified controls; separate current from forecast target residual risk. |
| Acceptance record | Authority, rationale, scope, date, expiry/review date, compensating controls, and triggers if accepted. |
| Closure criteria/evidence | Observable conditions and evidence needed to close or downgrade. |
| Review trigger/date | Periodic review date and events that force reassessment. |

### 10.2 Reusable risk-register template

Copy and adapt this table to the chosen register tool. Use stable IDs and link to a full record if a table cell becomes too large.

| Risk ID | Risk statement | Source links | Likelihood + rationale | Impact + rationale | Exposure score / basis | Priority / uncertainty | Treatment | Risk owner | Action owner(s) | Due date | Status | Residual risk | Acceptance / review date | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R-XX | Because …, … may occur, causing … | F-XX, T-XX, ADR-XX, flow ID | Score/category and basis, or unknown | Score/category and basis, or unknown | L × I only if the adopted scale supports the ranking; otherwise unknown | Rank plus evidence confidence | Avoid / mitigate / transfer-share / accept | Role/person | Role/person | YYYY-MM-DD | Open / treating / awaiting evidence / accepted / monitoring / closed | Current vs forecast target clearly labelled | Authority and approval evidence; expiry/review date or N/A with rationale | Specific test/config/review evidence |

### 10.3 Ownership and escalation

A risk without an owner is a statement, not a managed risk. An owner should have the authority or escalation path to secure resources and decisions. For every material item:

- name a **risk owner** accountable for the risk's disposition;
- name an **action owner** for each concrete task;
- set a due date and identify dependencies;
- define the evidence expected at closure;
- define escalation for overdue or blocked actions;
- state who may accept residual risk and under what limits;
- record who reviewed and changed the status.

Do not invent an approval board or risk authority. If the organisation's delegated authority is unknown, make it an explicit governance question and escalate to the appropriate accountable sponsor.

### 10.4 Closure and re-opening

A finding may be closed when the agreed closure criteria are met and the evidence is reviewed. Examples include a configuration inspection, a negative/positive security test, a schema contract test, a restore/reconciliation result, a runbook exercise, or an updated diagram validated against actual implementation. The evidence must be appropriate to the claim.

A risk may be closed only when the risk has been eliminated or reduced to a state the local process permits to close, and any residual risk has been handled according to policy. Some organisations keep low residual risks open in monitoring rather than close them; use the local lifecycle.

Reopen or reassess when:

- the architecture or data classification changes;
- a new flow, trust boundary, identity, or external dependency appears;
- a control fails, a test contradicts the design, or an incident occurs;
- an accepted-risk expiry or review date arrives;
- the underlying assumption is disproven;
- exposure, impact, business use, or regulatory context changes;
- a migration phase changes the failure domain or rollback path.

### 10.5 Risk acceptance example

**Illustrative record AR-01 for R-03:** a hypothetical authorised risk owner accepts a bounded residual logging risk for a non-production diagnostic dataset for 30 days while a masking change is implemented. The record would need to identify the actual fields, environment, access restrictions, compensating monitoring, approval evidence, expiry date, and triggers that invalidate acceptance. It would not apply automatically to production or to a more sensitive data class.

This example demonstrates the structure only. No real acceptance is being asserted. If the authority, scope, compensating controls, or expiry are missing, the acceptance record is incomplete.

---

## 11. Advanced review practices

### 11.1 Proportionality and review triggers

Review depth should match impact, uncertainty, novelty, and reversibility. Lightweight review may be appropriate for a low-impact, reversible internal change. A more rigorous review is appropriate for new sensitive data processing, a new trust boundary, broad access changes, new external dependencies, changes to recovery assumptions, or high-consequence data products.

Use explicit triggers rather than relying only on project size. A small configuration change can materially change exposure; a large but well-understood change may have a standard review path. Define the trigger and review depth in the actual governance process.

### 11.2 Beyond the happy path

Advanced reviewers deliberately inspect hidden and secondary flows:

- logs, metrics, traces, dead-letter queues, and debug artefacts;
- backup, restore, replication, and disaster-recovery copies;
- support access, emergency access, and privileged administrative paths;
- notebooks, local downloads, exports, and test/non-production datasets;
- replay, backfill, reprocessing, and schema migration paths;
- CI/CD, orchestration, secrets, identity configuration, and other control-plane operations;
- tenant and domain boundaries, shared service identities, and inherited permissions;
- data provenance, quality, poisoning/tampering, stale records, and unintended joins;
- AI/ML flows where relevant: training data lineage, feature access, embedding stores, retrieval-time permissions, prompt injection, and model/service credentials.

These are candidate areas for inquiry, not an assertion that every system contains each path. Use network/configuration inventories, lineage, IAM inventories, logs, interviews, runbooks, and tests to confirm what exists. Record unverified paths as questions or evidence gaps until established.

### 11.3 Control effectiveness and evidence strength

A useful evidence ladder is:

1. **Assertion:** someone says a control exists.
2. **Design evidence:** an architecture description or specification defines the intended control.
3. **Implementation evidence:** relevant configuration, code, policy, or deployment artefact shows implementation.
4. **Test evidence:** a repeatable test exercises expected and failure behaviour.
5. **Operational evidence:** monitoring, access reviews, restore exercises, or other operational records show the control functioning in context.
6. **Independent/specialist assessment:** appropriate review by a qualified party where required by the risk or governance process.

This is a practical reasoning aid, not a universal formal hierarchy. Different claims require different evidence. A load test may support a throughput claim but not an access-control claim. A configuration extract may show a setting but not prove the whole path is secure. Record evidence scope, date, environment, and limitations.

### 11.4 Quantification and uncertainty

Use numeric loss models only when the organisation has credible data and a defensible method. If using scenarios, estimate ranges, show assumptions, identify uncertainty, and avoid implying that a single number predicts the future. Ordinal scales are useful for prioritisation but are not mathematically precise measures of risk. Correlated risks, common-cause failures, and dependency chains make naive score aggregation misleading.

Where likelihood cannot be estimated responsibly, state “unknown” and prioritise evidence collection based on potential impact and decision timing. Unknown is not the same as low.

### 11.5 Review quality and feedback loops

Track whether the review process produces useful outcomes, not simply the number of findings. Potential measures include:

- percentage of material findings with evidence, owners, dates, and closure criteria;
- time from finding creation to triage and verified closure;
- overdue material actions and accepted-risk expiries;
- recurring finding categories across designs;
- proportion of findings reopened because closure evidence was inadequate;
- material issues discovered late that earlier reviews could reasonably have identified;
- reviewer coverage of relevant stakeholder concerns and trust boundaries.

Metrics can be gamed. A falling finding count may indicate improved designs—or weaker reviews. Interpret trends alongside independent sampling, reviewer feedback, scope, and changes in architecture complexity.

### 11.6 Feeding results back into architecture

A review is incomplete if its findings remain isolated in a meeting note. Update linked artefacts when justified:

- **DFD/architecture views:** add a missing confirmed flow, boundary, control, or component; preserve uncertainty where still unverified.
- **ADR:** record a significant new choice, reconsidered alternative, or accepted trade-off. Link the triggering finding/risk and preserve the historical record.
- **Requirements/criteria:** clarify ambiguous or untestable requirements and identify who can approve the change.
- **Risk register:** add or update the scenario, treatment, owner, residual assessment, and review trigger.
- **Migration plan:** schedule changes, dependencies, verification steps, rollback, and gates.
- **Reference pattern/standard:** consider a reusable improvement if the same finding recurs. Topic 06 covers reuse with judgement.

### 11.7 Governance and decision integrity

Good governance means the right people make the right decision with enough evidence and explicit accountability. It does not mean every review needs a large committee. Record who made a decision, their authority, the scope, conditions, dissent, and date when those details matter.

Never use a review result as an unsupported statement such as “secure,” “compliant,” or “risk-free.” A more accurate outcome might be: “The review found no unresolved blocker against the stated criteria in the supplied artefacts; the following evidence gaps and residual risks remain.” The scope, evidence baseline, and limitations must accompany the conclusion.

---

## 12. Reusable templates and checklists

### 12.1 Review plan template

```markdown
# Architecture Review Plan
- Review ID:
- System / change:
- Review owner / lead:
- Date and version baseline:
- Purpose and decision to support:
- Scope (systems, data, flows, environments, migration phase):
- Explicit exclusions and why:
- Stakeholders / participants and roles:
- Decision rights and risk-acceptance authority (or open question):
- Criteria IDs and sources:
- Input artefacts and versions:
- Evidence requested but unavailable:
- Review method and schedule:
- Severity / priority rubric:
- Required outputs:
- Gate conditions:
- Follow-up date:
```

### 12.2 Finding template

```markdown
## F-XX — [Short finding title]
- Status:
- Criterion ID / source requirement:
- Affected component, flow, environment, and data class:
- Evidence reference and version:
- Observation (what the evidence actually shows):
- Evidence limitation / missing evidence:
- Interpretation and reasoning:
- Potential impact:
- Severity and rationale:
- Priority and rationale:
- Recommendation / required outcome:
- Accountable owner:
- Action owner:
- Due date:
- Closure criteria:
- Closure evidence expected:
- Related threat IDs:
- Related risk IDs:
- Related ADR / requirement / DFD flow:
- Reopen triggers:
```

### 12.3 Threat scenario template

```markdown
## T-XX — [Scenario title]
- Scope and element / flow ID:
- Asset and data classification:
- Threat source / actor / cause:
- Preconditions and entry point:
- Scenario (actor/cause → action → consequence):
- Trust boundary crossed:
- Existing controls and evidence state:
- Weakness or uncertainty:
- Likelihood assessment and basis:
- Impact assessment and basis:
- Related finding(s):
- Related risk(s):
- Treatment / mitigation options:
- Chosen treatment and rationale:
- Owner and due date:
- Verification evidence:
- Residual risk and revisit triggers:
```

### 12.4 Review report template

```markdown
# Architecture Review Report
1. Executive summary and review outcome (scope-qualified)
2. System/change, artefact versions, and review scope
3. Participants, roles, criteria, and method
4. Evidence reviewed and evidence unavailable
5. Architecture and data-flow summary
6. Findings by severity, with evidence and owners
7. Threat scenarios and controls/evidence state
8. Risk assessment, treatment, and residual risk
9. Decision requests, dissent, and unresolved questions
10. Gate recommendation and conditions (decision authority named)
11. Follow-up actions, due dates, and escalation
12. Artefacts requiring updates (DFDs, ADRs, requirements, migration plan)
13. Limitations and exclusions
14. Next review date and change triggers
```

### 12.5 Reviewer checklist

**Scope and evidence**
- [ ] Review purpose, change boundary, and exclusions are clear.
- [ ] Criteria are explicit and linked to requirements/concerns.
- [ ] Artefact versions are recorded and cross-view consistency is checked.
- [ ] Observed facts, reported claims, assumptions, inferences, and recommendations are distinguished.

**Architecture and data flow**
- [ ] Relevant actors, components, stores, dependencies, and deployment boundaries are represented.
- [ ] Important flows and trust-boundary crossings are labelled.
- [ ] Data classification, ownership, retention, and permitted use are considered.
- [ ] Logs, support, backup, replay, exports, and control-plane paths are considered where relevant.

**Threat and risk**
- [ ] Threat scenarios name the affected asset and plausible harmful outcome.
- [ ] Existing controls and evidence state are explicit.
- [ ] Likelihood and impact have rationale; unknowns are not scored as low by default.
- [ ] Treatment, owner, due date, residual risk, and acceptance authority are recorded.
- [ ] Risk acceptance is bounded, time-limited or periodically reviewed, and authorised.

**Follow-up**
- [ ] Findings have IDs, evidence, severity/priority rationale, owner, due date, and closure criteria.
- [ ] Actions have verification evidence, not just verbal completion claims.
- [ ] Relevant DFDs, ADRs, requirements, risk register, and migration plan are updated.
- [ ] Escalation and revisit triggers are clear.
- [ ] Review limitations and the scope of the conclusion are stated.

### 12.6 Cross-artefact traceability matrix

| Finding / risk | Requirement or criterion | Architecture view / DFD flow | ADR | Threat | Action / migration step | Closure evidence |
|---|---|---|---|---|---|---|
| F-XX / R-XX | REQ/C-XX | `DFD-ID`, flow `F-XX` | `ADR-XX` or N/A with rationale | `T-XX` | Action ID / phase | Test/config/review reference |

Use `N/A` only with a reason. If a material risk has no owner or no evidence path, the traceability chain is incomplete.

---

## 13. Practical exercises with model answers

All exercises use fictional Northbridge Bank and synthetic information. Treat each stated artefact or evidence item as part of the exercise only; do not infer anything about a real system.

### Exercise 1 — Beginner: identify criteria and potential findings

**Scenario:** A proposed analytics ingestion service receives partner files, stores raw copies, validates them, and publishes curated tables. The only supplied diagram is a high-level DFD. It shows the partner upload flow and validation process but does not label the data classification, identify sender identity, or describe duplicate/replay handling. A stakeholder says, “We already secure the upload.” No configuration or test evidence is supplied.

**Tasks:**
1. List at least six review criteria.
2. Write three potential findings without claiming an unverified vulnerability.
3. Classify each statement as evidence, reported claim, inference, assumption, or recommendation.
4. Assign provisional severity and explain what additional information could change it.

**Model answer:**

Possible criteria include: flow and boundary completeness; data classification; sender identity and authorisation; transport protection evidence; schema validation; duplicate/replay semantics; raw-data retention/access; operational ownership and failed-file handling; logging data handling; recovery/replay capability.

| Finding | Evidence/observation | Interpretation | Provisional severity | Action |
|---|---|---|---|---|
| F-B1: Data classification not shown | Supplied DFD lacks classification labels | Reviewers cannot confirm handling requirements from the diagram; this does not prove the data is mishandled | Minor or major depending on sensitivity and gate | Data owner supplies classification and updates flow inventory/DFD; review resulting controls. |
| F-B2: Sender identity not evidenced | DFD names partner upload; stakeholder says upload is secure; no config/test supplied | The statement is reported, not verified; the review cannot determine identity and authorisation behaviour | Major pending evidence if sensitive data and external boundary are in scope | Document mechanism; inspect configuration/test evidence. |
| F-B3: Replay/duplicate behaviour unspecified | No replay semantics in the supplied package | Duplicate processing may affect data integrity if retries or replay occur; actual risk depends on implementation and use | Major/minor based on downstream consequence | Define idempotency/reconciliation; test repeated file handling. |

Classification: “DFD lacks labels” is an observation; “we already secure the upload” is a reported claim; “review cannot determine mechanism” is an inference; “assume sender auth is effective” is an assumption; “inspect configuration and test” is a recommendation.

**Validation criteria:** at least six specific criteria; three evidence-grounded findings; no statement that authentication is absent unless evidence establishes it; each finding has a corrective next step.

### Exercise 2 — Intermediate: review a trust-boundary crossing

**Scenario:** `DFD-NB-INT v1.1` shows `F-10` from a third-party partner to a managed ingestion endpoint, `F-11` from ingestion to a raw store, and `F-12` from validation to curated storage. The external-to-enterprise boundary is marked. A synthetic evidence pack contains: (a) a design document saying “mutual authentication planned”; (b) no deployed configuration extract; (c) a schema test that rejects a missing required field; (d) no test for duplicate replay; (e) a runbook assigning failed-file triage to the Data Operations team; (f) no log-field review.

**Tasks:**
1. Separate design evidence from implementation/test evidence.
2. Review at least three selected flows and their trust-boundary crossings.
3. Produce at least **ten findings**, a threat table for at least **three flows**, and a risk register containing at least **eight risks** (as required by the module roadmap).
4. For every finding, provide evidence or explicitly identify missing evidence, severity rationale, owner, due date, and closure criteria.
5. Specify treatment and objective verification evidence for every material risk; distinguish current from forecast residual risk.
6. Identify what must be checked or updated in the DFD, architecture description, and ADRs.

**Model answer:**

Evidence state: mutual authentication is planned in design, not verified as deployed; required-field validation has one test for one failure case, not proof of complete validation; duplicate replay is untested; failed-file ownership is documented in the supplied runbook; log fields remain unknown.

The following compact model output demonstrates the minimum breadth. In a real exercise submission, expand each row into the full finding template from Section 12.2.

| Finding | Evidence/observation | Provisional severity | Owner / closure evidence |
|---|---|---|---|
| F-I1: Sender identity not evidenced | Design says mutual authentication planned; no deployed config evidence | Major pending evidence | Ingestion owner; config inspection + negative test |
| F-I2: Authorisation point unclear | DFD does not locate enforcement | Major pending evidence | Security/ingestion owner; updated view + policy evidence |
| F-I3: Data classification absent from flow | `F-10` has no class label | Minor/major based on classification | Data owner; approved classification linked to flow |
| F-I4: Transport protection not evidenced | Design intent only; no deployed evidence | Major if sensitive data crosses boundary | Platform owner; configuration/test evidence |
| F-I5: Validation coverage incomplete | One required-field test only | Major/minor by impact | Pipeline owner; schema/negative-case tests |
| F-I6: Duplicate replay untested | No replay test or documented semantics | Major if downstream outputs require uniqueness | Pipeline owner; replay test + reconciliation |
| F-I7: Quarantine/rejection path unclear | DFD does not show failed-file disposition | Minor/major by operational impact | Pipeline owner; updated DFD/runbook + test |
| F-I8: Logging data exposure unknown | No log-field/access review | Minor/major by sensitivity | Data/security owner; representative log and permission review |
| F-I9: Failed-file alerting not evidenced | Runbook assigns triage but no alert test supplied | Minor/major by service objective | Data Operations owner; alert test and runbook exercise |
| F-I10: Recovery/restore evidence missing | No restore test in evidence pack | Major pending recovery objectives | Operations owner; restore/reconciliation test and runbook |

**Threat table for the three named flows:** the category labels below are analytical prompts, not a claim that STRIDE is formally adopted. A separate logging/support threat is included only as a candidate path; confirm that the path exists before adding it to the authoritative DFD.

| Threat ID | Flow / element | Threat category (illustrative) | Scenario | Linked risk(s) |
|---|---|---|---|---|
| T-I1 | `F-10` partner → managed ingestion endpoint | Spoofing / unauthorised submission | An unauthorised sender may submit a forged file if identity or authorisation is ineffective | R-I1, R-I2 |
| T-I2 | `F-11` ingestion → raw store | Tampering / excessive access | A workload or operator with broader-than-needed write access may alter or replace a raw file, weakening provenance and downstream integrity | R-I2, if evidence confirms the relevant access-scope risk; otherwise record this as a threat hypothesis and establish a separately justified risk link |
| T-I3 | `F-12` validation → curated store | Data integrity / validation failure and replay | Invalid or duplicated records may reach curated outputs if validation or idempotency is inadequate | R-I5, R-I6 |
| T-I4 (candidate) | Logging/support path, if confirmed by inventory or evidence | Information disclosure | Sensitive fields may be copied to logs or support exports with broader access than intended | R-I7 |

**Eight-risk register (compact model):** dates and numeric ratings are not supplied by the scenario, so the model records unknowns and event-based due triggers rather than inventing values. The risk owner is accountable for disposition; action owners perform the named work.

| Risk ID | Causal risk statement | Likelihood / impact / exposure | Treatment | Risk owner / action owner | Due date or trigger | Status | Current / target residual risk | Closure evidence / review trigger |
|---|---|---|---|---|---|---|---|---|
| R-I1 | Sender identity is not evidenced → unauthorised upload may corrupt downstream data | Unknown / potentially major / not scored pending evidence | Verify identity and authorisation; do not assume a control is absent | Ingestion service owner / ingestion engineer | Before architecture gate; calendar date to be assigned | Open — evidence pending | Current: unknown; target: reassess after verification; no reduction assumed | Configuration inspection + suitable negative test; revisit if endpoint or identity model changes |
| R-I2 | Authorisation boundary is unclear → sender or workload permissions may be broader than intended | Unknown / potentially major / not scored pending evidence | Document enforcement and scope; test least-privilege denial | Security/risk owner / ingestion engineer | Before architecture gate; calendar date to be assigned | Open — evidence pending | Current: unknown; target: reassess after policy/access tests | Policy/config evidence + access test; revisit if roles, scopes, or tenancy change |
| R-I3 | Data classification is unknown → handling controls may not match sensitivity | Unknown / impact depends on classification / not scored | Determine and approve classification; link it to flows and stores | Data owner / data steward | Before control selection and architecture gate | Open — classification pending | Current: unknown; target: assess after classification | Approved classification and updated flow inventory; revisit on data-use/classification change |
| R-I4 | Transport protection is unverified → data may be exposed in transit if protection is ineffective | Unknown / potentially major / not scored pending evidence | Verify required transport protection and relevant configuration | Platform owner / platform engineer | Before architecture gate; calendar date to be assigned | Open — evidence pending | Current: unknown; target: reassess after configuration/test evidence | Configuration and appropriate test evidence; revisit on endpoint/protocol change |
| R-I5 | Validation coverage is incomplete → malformed data may propagate | Unknown / impact depends on downstream use / not scored | Define validation outcomes and add contract/negative-case tests | Data pipeline owner / pipeline engineer | Before production-readiness gate | Open — test coverage incomplete | Current: partial evidence only; target: reassess after full test suite | Positive/negative schema tests and rejection-path evidence; revisit on schema/contract change |
| R-I6 | Replay semantics are unknown → duplicate or inconsistent aggregates may occur | Unknown / impact depends on consumer semantics / not scored | Define idempotency, replay and reconciliation behaviour | Data pipeline owner / pipeline engineer | Before replay/backfill approval or production gate | Open — semantics unconfirmed | Current: unknown; target: reassess after replay/reconciliation test | Repeat/replay test plus reconciliation result; revisit on retry or processing-model change |
| R-I7 | Logging has not been reviewed → sensitive fields may be disclosed through telemetry | Unknown / depends on data class and access / not scored | Inspect fields, minimise or mask where needed, restrict access, review retention | Data/security owner / observability owner | Before operational readiness; calendar date to be assigned | Open — evidence pending | Current: unknown; target: reassess after log/access review | Representative log sample, permissions and retention review; revisit on telemetry or data-class change |
| R-I8 | Recovery is untested → restore may miss objectives or yield inconsistent data | Unknown / depends on recovery objectives / not scored | Define objectives and run restore/reconciliation exercise | Service/operations owner / operations engineer | Before operational-readiness gate | Open — restore evidence pending | Current: unknown; target: reassess after dated test; no reduction assumed | Restore result, reconciliation evidence, runbook and limitations; revisit on architecture/recovery change |

The roadmap's illustrative likelihood × impact scale may be used only after the scenario supplies enough evidence and the reviewer defines the scale. Do not invent scores to fill a table. Event-based due triggers are provisional exercise placeholders; a real action tracker needs an agreed calendar date and escalation path.

DFD checks: `F-10` boundary and identity/authorisation; `F-11` raw-store access and integrity; `F-12` validation and publication sequence; add the logging/support path only if confirmed. ADR checks: whether managed ingestion was selected, which identity/failure assumptions were recorded, and whether new evidence invalidates a decision assumption. Do not alter an accepted ADR silently; record reconsideration if a significant choice changes.

**Validation criteria:** ten findings and eight risks are present; evidence states are correctly separated; threats are tied to flows/assets; risks have causal statements; each material mitigation has testable closure evidence; unknown flows are not drawn as confirmed.

### Exercise 3 — Advanced: create a structured review package

**Scenario:** Review the synthetic Northbridge package in Section 9 and extend it to an illustrative AI retrieval platform with three trust boundaries: (1) enterprise document source to ingestion/indexing; (2) indexing pipeline to embedding/vector store; (3) retrieval service to model API and user-facing application. The architecture and all evidence remain hypothetical.

Your deliverable must include:

- a review report with scope, participants/roles, criteria, evidence limitations, summary, and gate recommendation;
- at least **15 findings** spanning architecture consistency, identity/access, data handling, operations, resilience, and evidence gaps;
- a threat model covering all **three trust boundaries** and linking threats to flows/assets;
- a prioritised risk register with current assessment, treatment, owner, due date, residual-risk plan, and revisit triggers;
- an accepted-risk record with authority, bounded scope, compensating controls, expiry/review date, and triggers;
- updates proposed for at least one DFD, one ADR, and one migration/follow-up plan;
- a consistency matrix and a list of unresolved questions/evidence requests.

**Model answer outline:** The Northbridge ingestion findings in Section 9 are a starting pattern, not a complete AI-platform answer. For the AI extension, inspect document ingestion permissions, source ACL propagation, embedding-store access, retrieval-time authorisation, model API identity, prompt injection and untrusted document content, logging/telemetry, retention/deletion, data poisoning/tampering, index rebuild/replay, backup/restore, and operational ownership. For each finding, state whether the evidence is observed, reported, missing, or hypothetical. The gate recommendation should be scope-qualified and must not conclude “secure,” “compliant,” or “vulnerable” without appropriate evidence.

**Example unresolved questions:**

1. Which identity establishes the partner sender, and where is authorisation enforced?
2. What are the file schema, integrity, size, and validation rules?
3. Are processing and replay idempotent? How are duplicates reconciled?
4. Which sensitive fields, if any, are emitted to logs, and who can access them?
5. What recovery objectives apply, and when was restore/reconciliation last tested?
6. Who accepts residual risk, and what are their delegated limits?
7. Which migration gate depends on each outstanding action?

**Validation criteria:** every finding has evidence or explicitly names missing evidence; every risk has an owner, treatment, due date, and review trigger; scores have rationale; residual risk is not assumed reduced before verification; the gate conclusion is scoped to the supplied evidence; the ADR is linked where a significant choice or assumption is affected.

**Advanced model-answer checklist — 15 finding themes:** these are candidate findings for the synthetic AI retrieval extension, not assertions that the controls are absent. The learner must anchor each to the relevant supplied artefact or explicitly mark it as a question/evidence gap.

| Finding ID | Review observation or evidence gap | Likely concern | Required next step / closure evidence |
|---|---|---|---|
| F-AI01 | Source document ACL propagation is not described | Unauthorised source content may enter a shared index | Document ACL mapping and test access inheritance/denial |
| F-AI02 | Ingestion workload identity is unspecified | Unclear source access scope | Identify workload identity and inspect least-privilege policy |
| F-AI03 | Document classification propagation is unclear | Restricted content may receive incorrect handling | Link classification metadata through ingestion/indexing and test representative cases |
| F-AI04 | Parser treatment of hostile/malformed files is undocumented | Parser abuse or content tampering | Define file allowlist/validation and inspect suitable negative tests |
| F-AI05 | Embedding creation and model endpoint identity are not evidenced | Unclear access to content/model services | Document identities, secrets handling, and configuration evidence |
| F-AI06 | Vector-store tenant/domain isolation is unclear | Cross-tenant retrieval exposure | Document isolation model and test cross-scope denial |
| F-AI07 | Retrieval-time authorisation is not demonstrated | Previously permitted content may be retrieved after access changes | Define authoritative permission check and test revocation/denial |
| F-AI08 | Prompt-injection handling is not addressed in the threat model | Untrusted content may influence model instructions or outputs | Threat-model the scenario and test applicable mitigations; do not promise elimination |
| F-AI09 | Retrieval results and source citations are not reconciled to source IDs | Incorrect or untraceable content may be presented | Test source mapping, provenance, and deletion/update propagation |
| F-AI10 | Embedding/index deletion semantics are unclear | Deleted or reclassified documents may remain retrievable | Define deletion/rebuild workflow and verify index state after removal |
| F-AI11 | Logs may include prompts, snippets, or retrieved content | Sensitive data may enter telemetry | Inspect log samples, access, retention, and masking controls |
| F-AI12 | Model API quotas/timeouts/failure handling are unspecified | Denial of service or cascading failures | Define timeout/retry/rate-limit behaviour and test failure cases |
| F-AI13 | Index rebuild/replay consistency is unproven | Duplicate, stale, or inconsistent embeddings may persist | Document idempotency/versioning and run rebuild/reconciliation test |
| F-AI14 | Backup/restore and recovery dependencies are not evidenced | Recovery may not restore a consistent index and metadata | Run restore/rebuild test and document limitations |
| F-AI15 | Ownership for source ACL drift, deletion requests, and incident response is unclear | Operational gaps may leave stale access or unresolved incidents | Assign accountable owners and exercise the runbook/escalation path |

**Illustrative prioritised risk register for the advanced exercise:** prioritisation depends on actual classification, evidence, exposure, and business context; the ranking below is a training hypothesis only.

| Risk | Scenario | Illustrative priority | Treatment / owner | Revisit trigger |
|---|---|---|---|---|
| R-AI01 | Source permissions fail to propagate, allowing retrieval of content outside the user's source permissions | High pending evidence | Mitigate: document and test ACL propagation/retrieval denial; data-platform/security owner | Permission model, source system, or index tenancy changes |
| R-AI02 | Sensitive document content or prompts enter broadly accessible logs | High/medium depending on classification | Mitigate: minimise/mask logs, restrict access, verify retention; operations/security owner | Logging, observability vendor, or data class changes |
| R-AI03 | Prompt injection in untrusted retrieved content influences downstream model behaviour | Requires scenario-specific assessment; not a claim of exploitability | Mitigate layered input/output controls, instruction/data separation, constrained tools, and tests; AI service owner | Model, prompt, retrieval policy, or tool capability changes |
| R-AI04 | Deletion or permission revocation does not propagate to the index | High if sensitive data remains retrievable | Mitigate and test deletion/reindex workflow; data owner | Retention policy, source ACL, or indexing pipeline changes |
| R-AI05 | Index rebuild or restore produces stale/inconsistent content | Medium/high based on use | Mitigate: versioned rebuild, reconciliation, restore tests; platform owner | Index schema, embedding model, or recovery process changes |

**Accepted-risk example:** `AR-AI01` may hypothetically record a limited non-production diagnostic logging exposure for a named dataset until a masking change is deployed. The record is incomplete unless it identifies the exact data/scope, approver with actual authority, compensating controls, monitoring, expiry/review date, and invalidating triggers. It must not be used as blanket acceptance for production or all document classes. This example is a template, not an actual approval.

**Required artefact updates:** (1) update the DFD to represent confirmed source-ACL, indexing, retrieval, and model-API flows, marking any unverified path as open; (2) create or revisit an ADR if retrieval-time authorisation or index isolation requires a significant architectural choice; (3) add migration tasks for ACL propagation, deletion/reindex validation, and recovery testing, with owners and gate dependencies. Preserve historical ADR status and link the review finding that triggered reconsideration.

### Exercise 4 — Review a weak finding

**Weak entry:** “F-9: The pipeline is insecure. Severity: critical. Fix security. Owner: Engineering. Due: ASAP. Close when fixed.”

**Tasks:** Identify at least seven defects and rewrite the entry.

**Model answer:** Defects include no criterion, no evidence, no affected flow/component, no specific threat or impact, unsupported “insecure” claim, unexplained severity, vague recommendation, no accountable owner, no date, no closure criteria, no linked risk/ADR, and no distinction between evidence gap and confirmed weakness.

**Rewritten illustrative entry:**

> **F-09 — Authorisation path for cross-boundary flow F-10 is not evidenced.** Criterion C-02 requires the caller identity and authorisation point to be documented and verifiable. In `DFD-NB-INT v1.1`, `F-10` crosses the partner-to-enterprise boundary, but the supplied package does not identify the enforcement point or include implementation/test evidence. This is an evidence gap; it does not prove the deployed endpoint lacks authorisation. If effective authorisation is absent or misconfigured, an unauthorised sender may submit data for downstream processing. Provisional severity: major, subject to the agreed rubric and data classification. Action: ingestion owner documents the identity/authorisation path and supplies configuration plus a suitable negative test. Due: before the defined architecture gate. Close after the reviewer confirms the evidence meets C-02 and updates the linked risk R-09.

**Validation criteria:** the rewritten finding is traceable, proportionate, owned, and verifiable; no unsupported claim remains.

### Exercise 5 — Treatment and residual risk

**Scenario:** A synthetic risk assessment finds that a managed data service's recovery behaviour has not been demonstrated. The team proposes a restore test, runbook update, and reconciliation test. Before those tests run, a manager says the risk score should be reduced because the work is planned.

**Question:** What should the reviewer do?

**Model answer:** Keep the current assessment based on current controls and evidence. Record the planned treatment, action owners, due dates, and expected target residual assessment separately. Do not lower current risk until evidence supports the change. After the tests, assess their scope, results, limitations, and any residual gap; then update the risk register. If the release cannot wait, use the actual authorised risk-acceptance process with bounded scope, compensating controls, expiry/review date, and named authority. A schedule commitment is not evidence of control effectiveness.

**Validation criteria:** current and target residual risk are separated; treatment is not counted as implemented; closure depends on test evidence; acceptance authority is not invented.

### Exercise 6 — Owner, due date, and closure design

For each case, propose an owner role, due-date trigger, closure evidence, and escalation path:

1. Missing data classification in the DFD.
2. No duplicate/replay test.
3. Restore-test evidence missing.
4. A material residual risk needs acceptance but the delegated authority is unknown.

**Model answer:**

| Case | Owner | Due-date trigger | Closure evidence | Escalation |
|---|---|---|---|---|
| Classification | Data owner/steward | Before flow-control review or architecture gate | Approved classification record linked to flow inventory/DFD | Data governance owner if classification cannot be agreed |
| Replay test | Pipeline owner | Before production readiness or release gate | Repeat/replay test output plus reconciliation result | Engineering lead / gate owner if blocked |
| Restore evidence | Platform/operations owner | Before operational readiness gate | Dated restore test, result, runbook, and limitations | Service owner / resilience authority if objectives cannot be met |
| Unknown acceptance authority | Architecture/risk coordinator to identify authority | Before any acceptance is relied upon | Documented delegated authority and approval record | Accountable sponsor / governance function; do not assume approval |

**Validation criteria:** owners are roles with relevant responsibility; due dates are event-based if calendar dates are not known; closure is objective; escalation resolves authority or delivery blockers.

---

## 14. Common mistakes and corrections

| Mistake | Why it fails | Correction |
|---|---|---|
| Reviewing without agreed criteria | Turns the meeting into opinion or technology preference | Derive criteria from requirements, concerns, constraints, and quality attributes before the review. |
| Treating a missing diagram label as proof a control is absent | Confuses documentation gaps with implementation facts | State what is not shown and request suitable implementation evidence. |
| Calling a design “secure” after a checklist | Implies a guarantee the review cannot provide | State the scope, evidence baseline, remaining gaps, and limitations. |
| Threat table contains generic “hacking” entries | Does not identify asset, entry point, action, or consequence | Write a concrete scenario linked to a component or flow. |
| STRIDE is treated as exhaustive or mandatory | A mnemonic cannot guarantee complete analysis; roadmap only presents it as illustrative | Use it as a prompt and add context-specific data/operational threats. |
| Risk score is presented as a precise probability | Ordinal scales do not have calibrated mathematical meaning | Define scales, record rationale, and use scores for ranking only. |
| Unknown likelihood is scored low | Hides uncertainty and can under-prioritise evidence gathering | Mark unknown, assess impact, and prioritise evidence collection. |
| Planned mitigation lowers current risk immediately | Treats intention as implemented control | Separate current assessment from forecast target residual risk. |
| Finding says “fix security” | Action is unbounded and cannot be verified | Specify the required outcome, owner, due date, and closure evidence. |
| Risk register has no owner or expiry | No one is accountable; acceptance can become permanent by default | Assign risk/action owners and review dates; bound accepted risk. |
| “Risk transferred to vendor” means no residual responsibility | Contracts do not remove all technical or business consequences | Document retained obligations, dependencies, and residual risk. |
| Review closes when meeting ends | Actions remain unresolved and no evidence is checked | Track actions to evidence-based closure and update linked artefacts. |
| Every concern becomes a blocker | Destroys prioritisation and review credibility | Apply a consistent severity rubric and explain impact. |
| Reviewers force consensus | Hides dissent and unresolved assumptions | Record disagreement, evidence needed, decision authority, and deadline. |
| Risk aggregation adds ordinal scores | Creates a misleading enterprise number | Analyse dependencies and common causes; aggregate only with a defensible method. |
| Only the happy-path flow is reviewed | Misses logs, replay, backups, support, admin, and failure paths | Inspect secondary flows and control-plane paths where relevant. |
| No link back to ADR or diagram | Findings become detached from the architecture they evaluate | Use stable IDs and maintain cross-artefact traceability. |

---

## 15. Deliverables, mastery criteria, and completion gate

### 15.1 Expected deliverables

The Topic 05 roadmap expects:

1. **Review plan and criteria** defining scope, participants, inputs, decision rights, and review method.
2. **Findings report** with evidence, severity, owners, due dates, and closure criteria.
3. **Threat-model artefacts** with scenarios tied to the DFD and relevant assets/boundaries.
4. **Risk register** with assessment, treatment, owners, due dates, status, and residual risk.
5. **Follow-up tracker and closure evidence** demonstrating how actions are verified.
6. **Artefact updates** where justified: DFDs, architecture description, ADRs, requirements, and migration tasks.
7. **Practice-question gap log** recording concepts that need another pass.

### 15.2 Mastery criteria

You are ready to move on when you can demonstrate all of the following:

- [ ] Run a structured review against explicit criteria rather than personal preference.
- [ ] Explain the difference between a finding, threat, risk, issue, assumption, and unresolved question.
- [ ] Produce evidence-based findings with traceable locations, impact, severity rationale, owner, due date, and closure criteria.
- [ ] Produce a threat table tied to a DFD element or flow and identify relevant trust-boundary crossings.
- [ ] Distinguish designed, reported, implemented, tested, and operationally evidenced controls.
- [ ] Assess likelihood and impact with rationale; disclose uncertainty and avoid false precision.
- [ ] Maintain a risk register in which each material risk has a treatment, risk owner, action owner(s), due date, status, residual-risk plan, and revisit trigger.
- [ ] Explain who may accept residual risk, and record the authority and scope rather than inventing them.
- [ ] Define objective closure evidence and verify mitigation before closing findings or reducing current risk.
- [ ] Trace findings and risks to requirements, diagrams/flows, ADRs, and follow-up/migration work.
- [ ] State the limitations of the review and avoid unsupported security or compliance claims.

### 15.3 Completion gate

The Topic 05 gate is met when:

- [ ] Another person has reviewed the review report, threat table, and risk register.
- [ ] Findings trace to evidence or explicitly state which evidence is missing.
- [ ] Actions have named owners and due dates.
- [ ] Material risks have treatment, residual-risk handling, and review triggers.
- [ ] Risk acceptance, where used, is authorised, bounded, and time-limited or periodically reviewed under the actual governance process.
- [ ] Closure criteria and expected verification evidence are explicit.
- [ ] Practice questions have been attempted and gaps logged.
- [ ] Readiness is demonstrated: you can evaluate a design against criteria and risk and can explain why a reusable solution is or is not appropriate in its context.

Do not treat completion of this learning checklist as a production security approval. It confirms learning deliverables are present, not that any real system is safe.

---

## 16. Readiness for Topic 06

Topic 06 covers **reference architectures, standards, and reusable patterns**. The connection is direct: reviews often reveal recurring design choices, repeated gaps, and controls that may be reusable. Before standardising a response, however, the team must understand the context, evidence, and risk that made it useful.

You are ready for Topic 06 when you can:

- distinguish a recurring architectural pattern from a one-off recommendation;
- explain which context and constraints make a pattern applicable;
- use review findings and risk trends to identify where a standard or reference design might help;
- preserve justified exceptions and record the reason, risk, and owner;
- avoid declaring a local pattern or named framework mandatory without evidence of adoption;
- link a proposed standard or pattern change to an ADR and its consequences.

The key principle is **reuse with judgement**: a pattern may reduce known risks in one context while introducing costs, dependencies, or failure modes in another. Topic 06 will teach how to evaluate that fit.

---

## 17. Practice questions and answer key

### Questions

1. Why does “not shown in the DFD” not prove that a security control is absent?
2. Explain the difference between a finding and a risk using the partner-ingestion example.
3. What is the difference between finding severity and risk priority?
4. Why should planned mitigations not reduce the current risk assessment before verification?
5. What evidence might support a claim that file replay is handled correctly?
6. What are the limitations of a 1–5 likelihood × impact score?
7. What should a reviewer do when the risk-acceptance authority is unknown?
8. Why is STRIDE useful, and why is it not proof of threat-model completeness?
9. Name three secondary data flows that can be missed in a happy-path DFD.
10. What makes a finding ready to close?
11. How should the team handle a disputed finding that affects a release gate?
12. How should findings feed back into ADRs and architecture diagrams?

### Answer key

1. A diagram is a model and may omit implementation detail. The evidence supports an architecture-documentation gap; configuration, code, or test evidence is needed to establish whether the deployed control exists and works.
2. A finding is an observed gap against a criterion, such as sender identity not being evidenced. A risk is the possible harm that may result, such as an unauthorised file being accepted and corrupting downstream data.
3. Severity classifies the finding's significance under the review rubric. Risk priority ranks the risk's treatment urgency using impact, likelihood, exposure, uncertainty, timing, and dependencies.
4. A plan is not an implemented control. Keep current risk and forecast target residual risk separate until evidence supports a change.
5. Documented idempotency/replay semantics, automated repeated-file tests, duplicate detection results, reconciliation output, and operational monitoring may support the claim. The evidence must match the actual system and use case.
6. Ordinal values may not have equal intervals, scores can hide uncertainty, scales vary by team, and multiplication does not produce a calibrated probability or monetary loss. Use the score for ranking and document rationale.
7. Record the governance gap, identify the appropriate accountable sponsor or risk-governance function, and escalate before relying on acceptance. Do not invent authority.
8. STRIDE provides prompts for common threat categories. It is a mnemonic, not an exhaustive method and not a formally adopted repository standard unless separately established.
9. Logs/metrics, backups/restores, support exports, dead-letter queues, replay/backfills, notebooks, and control-plane operations are examples.
10. Agreed closure criteria have been met and appropriate evidence has been reviewed; status updates or verbal assurances alone may be insufficient.
11. Record each position and its evidence, identify what would resolve the disagreement, assign an owner/date, and escalate to the gate decision authority if unresolved. Do not force consensus or silently close the item.
12. Update diagrams when a confirmed flow/boundary/component changes; create or revise an ADR for a significant decision; link the finding/risk and preserve decision history; add migration tasks and verification steps where needed.

---

## Final learner checklist

Before marking this topic complete, confirm that your own review package contains:

- [ ] A review plan with scope, participants, criteria, artefact versions, and decision rights.
- [ ] A criteria-to-evidence matrix with uncertain or missing evidence clearly marked.
- [ ] A findings report with evidence locations, impact, severity rationale, owners, due dates, and closure criteria.
- [ ] A threat table tied to assets, DFD elements/flows, and trust boundaries.
- [ ] A risk register with current assessment, treatment, ownership, residual-risk handling, and revisit triggers.
- [ ] At least one explicit check across a DFD, an ADR, and a risk/finding record.
- [ ] A list of unresolved questions and evidence requests.
- [ ] A follow-up plan and criteria for verifying closure.
- [ ] A practice-question gap log and readiness decision for Topic 06.

The objective is not to make the register look complete. It is to make the architecture's important uncertainties visible, assign accountable people to resolve them, and retain enough evidence that another reviewer can understand the basis for the decision.
