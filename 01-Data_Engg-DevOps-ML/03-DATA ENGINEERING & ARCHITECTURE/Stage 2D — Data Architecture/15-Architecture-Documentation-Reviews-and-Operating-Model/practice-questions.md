# Practice Questions — Architecture Documentation, Reviews and Operating Model

**Module:** Stage 2D — Data Architecture / 15 — Architecture Documentation, Reviews and Operating Model  
**Assessment type:** Progressive knowledge check, artefact critique, applied reasoning, and integrated architecture review  
**Scenario convention:** Northbridge Bank is fictional. Unless a question explicitly labels an item as a supplied fact, all numbers, team names, outcomes, constraints, and architecture choices are synthetic assessment assumptions.

> **Source alignment.** This assessment follows the module roadmap's nine-topic sequence, cross-topic dependency map, learning outcomes, recommended study method, and project guide. The roadmap says the module `practice-questions.md` and final-project files were empty when the roadmap was authored; therefore the scenario and assessment are proposed learning material, not pre-existing repository requirements. The roadmap's recommended readiness threshold is an average of at least 85% across the full set, no topic below 70%, completion of the integrated exercise, and closure of old unresolved learning gaps. These are study recommendations, not external certification requirements.

## Table of contents

1. [Purpose and learning outcomes](#purpose-and-learning-outcomes)
2. [How to use the assessment](#how-to-use-the-assessment)
3. [Coverage map](#coverage-map)
4. [Topic 01 — Diagrams](#topic-01-context-container-component-and-deployment-diagrams)
5. [Topic 02 — Data flow and trust boundaries](#topic-02-data-flow-and-trust-boundary-diagrams)
6. [Topic 03 — Architecture description and viewpoints](#topic-03-architecture-description-and-viewpoints)
7. [Topic 04 — ADRs and decision log](#topic-04-architecture-decision-records-and-decision-log)
8. [Topic 05 — Reviews, threats and risks](#topic-05-design-reviews-threat-models-and-risk-registers)
9. [Topic 06 — Reference architectures and patterns](#topic-06-reference-architectures-standards-and-reusable-patterns)
10. [Topic 07 — Ownership and operating model](#topic-07-team-boundaries-ownership-and-platform-operating-model)
11. [Topic 08 — Migration and modernization](#topic-08-migration-roadmaps-and-architecture-modernization)
12. [Topic 09 — Stakeholder communication](#topic-09-communicating-trade-offs-to-technical-and-business-stakeholders)
13. [Cross-topic integration assessment](#cross-topic-integration-assessment)
14. [Integrated architecture-review exercise](#integrated-architecture-review-exercise-northbridge-bank)
15. [Scoring rubric and readiness criteria](#scoring-rubric-and-readiness-criteria)
16. [Gap log and retest procedure](#gap-log-and-retest-procedure)
17. [Complete answer key and model solutions](#complete-answer-key-and-model-solutions)
18. [Final assessment completion checklist](#final-assessment-completion-checklist)

## 1. Purpose and learning outcomes

Use this file to check whether you can **produce, critique, connect, and defend** architecture artefacts—not merely define terms. The assessment tests whether you can:

1. Create and interpret context, container, component, and deployment diagrams.
2. Document data flows and trust boundaries.
3. Explain architecture descriptions, views, and viewpoints.
4. Create and maintain architecture decision records (ADRs) and a decision log.
5. Conduct structured design reviews and identify relevant threats and risks.
6. Evaluate reference architectures, standards, and reusable patterns.
7. Define team boundaries, ownership responsibilities, and operating-model considerations.
8. Assess current-state architecture and plan migration toward a target state.
9. Communicate architecture trade-offs to technical and business stakeholders.
10. Integrate the preceding capabilities into a coherent architecture review and modernization package.

## 2. How to use the assessment

1. Complete the relevant lesson before attempting its topic section. Follow the recommended sequence: structure → data movement and trust → viewpoints → decisions → review and risk → reuse → ownership → migration → communication.
2. Answer each topic section **before** opening its answer-key section. If practical, ask a peer to score artefacts without showing them the model answer first.
3. For scenario questions, separate **supplied facts**, **reported information**, **assumptions**, **inferences**, and **open questions**. Do not silently promote an assumption to a fact.
4. A model answer is a defensible example, not necessarily the only valid architecture. Alternative answers can receive full credit if they meet the requirements, expose assumptions, address trade-offs, and explain what evidence would change the conclusion.
5. Record errors in the gap log in Section 16. Revisit the relevant lesson and redo the task with a changed scenario; do not simply memorize the model answer.
6. Complete the cross-topic assessment and integrated architecture-review exercise before using the readiness criteria.

### Answer-quality scale for open-ended work

| Rating | Meaning | Typical evidence |
|---|---|---|
| 0 — Missing/unsafe | No usable answer or materially incorrect reasoning | Key boundary omitted; unsupported claim presented as fact; unsafe cutover recommendation |
| 1 — Partial | Some correct concepts, but important omissions or ambiguity | Diagram names components but omits flow direction; ADR lists options without consequences |
| 2 — Competent | Correct, traceable, and usable with minor gaps | Evidence labels, owners, assumptions, and criteria are mostly explicit |
| 3 — Strong | Complete, internally consistent, and defensible | Alternatives and trade-offs compared; dependencies and verification evidence linked |
| 4 — Excellent | Strong artefact plus thoughtful uncertainty and feedback handling | Clear revisit triggers, residual risks, dissent path, and evidence that would reverse the recommendation |

Use the question-specific marks and acceptance criteria as the primary scoring basis; this scale helps calibrate judgement on open-ended responses.

## 3. Coverage map

| Section | Topic | Beginner | Intermediate | Advanced | Primary evidence tested |
|---|---|---|---|---|---|
| 4 | 01. Context, container, component, deployment | Q1–Q2 | Q3–Q4 | Q5 | Diagram level, consistency, deployment mapping |
| 5 | 02. Data flow and trust boundaries | Q1–Q2 | Q3–Q4 | Q5 | Flow inventory, boundary crossings, threat reasoning |
| 6 | 03. Architecture description and viewpoints | Q1–Q2 | Q3–Q4 | Q5 | Stakeholder concerns, view coverage, correspondence |
| 7 | 04. ADRs and decision log | Q1–Q2 | Q3–Q4 | Q5 | Decision rationale, alternatives, status, revisit triggers |
| 8 | 05. Design reviews, threat models, risk registers | Q1–Q2 | Q3–Q4 | Q5 | Evidence-based findings, threats, risk treatment |
| 9 | 06. Reference architectures, standards, reusable patterns | Q1–Q2 | Q3–Q4 | Q5 | Applicability, comparison, justified deviation |
| 10 | 07. Team boundaries, ownership, operating model | Q1–Q2 | Q3–Q4 | Q5 | Accountability, RACI, interfaces, operations |
| 11 | 08. Migration roadmaps and modernization | Q1–Q2 | Q3–Q4 | Q5 | Gap analysis, dependencies, critical path, rollback |
| 12 | 09. Communicating trade-offs | Q1–Q2 | Q3–Q4 | Q5 | Audience fit, evidence, consistency, challenge handling |
| 13 | Cross-topic integration | — | Q1–Q2 | Q3–Q4 | Traceability across artefacts |
| 14 | Integrated architecture review | — | All tasks | Defense and consistency | Full package and evidence register |

## 4. Topic 01 — Context, container, component, and deployment diagrams

**Marks: 20.** Q1 = 2; Q2 = 3; Q3 = 4; Q4 = 6; Q5 = 5.

### Q1 — Beginner: multiple choice (2 marks)
Which statement best describes the purpose of a **system context diagram**?

A. It proves that the production network configuration is correct.  
B. It replaces deployment and data-flow diagrams.  
C. It lists every class, function, and internal module.  
D. It shows the system of interest, its users or external actors, and important external systems or relationships.

### Q2 — Beginner: explain the levels (3 marks)
In your own words, distinguish a **context**, **container**, **component**, and **deployment** diagram. Give one question each diagram should help a reader answer.

### Q3 — Intermediate: diagram defect review (4 marks)
A proposed diagram set has these defects:

- The context diagram names a “Risk Reporting Platform” but shows no users or external systems.
- The container diagram shows a batch scheduler and a warehouse, but not the source systems that send data.
- The component diagram uses a component called `PolicyEnricher`; the container diagram has no container in which it runs.
- The deployment diagram shows a production database but no environment, network, or hosting boundary.

Identify four defects and state the correction or follow-up evidence needed for each.

### Q4 — Intermediate: produce a mini diagram specification (6 marks)
**Synthetic scenario:** Northbridge's risk analysts use a reporting portal. The portal queries a risk-serving API, which reads a curated risk data store. A scheduled ingestion service receives files from a core banking source and writes to a raw landing area; a transformation job creates curated risk data. An identity provider authenticates analysts. These are scenario facts for this question, not claims about a real bank.

Provide a compact element-and-relationship specification for (a) a context diagram and (b) a container diagram. Include direction and purpose for at least four relationships. State at least two deployment details that must remain open until evidence is collected.

### Q5 — Advanced: consistency and evidence (5 marks)
A diagram author says, “The architecture is validated because the diagram looks complete.” Explain why that claim is insufficient. Give a five-point diagram-review checklist and explain how a finding should be traced into another module artefact.

## 5. Topic 02 — Data-flow and trust-boundary diagrams

**Marks: 20.** Q1 = 2; Q2 = 3; Q3 = 4; Q4 = 6; Q5 = 5.

### Q1 — Beginner: multiple choice (2 marks)
What does a trust boundary indicate in a data-flow diagram?

A. A change in trust, control, identity, administrative, or security domain that warrants explicit review of crossing flows.  
B. A physical firewall only.  
C. A point where data is always encrypted and therefore safe.  
D. A data-retention period.

### Q2 — Beginner: name a flow (3 marks)
List five useful attributes of a data-flow inventory entry. Explain why “data goes to the platform” is not an adequate flow description.

### Q3 — Intermediate: flow and boundary critique (4 marks)
A diagram shows a file moving from “External Partner” to “Lakehouse” and then to “Dashboard.” It does not show protocol, identity, validation, storage zone, sensitivity, or boundary crossings. Identify at least four questions or omissions that prevent a meaningful security review.

### Q4 — Intermediate: threat-oriented flow table (6 marks)
Using the synthetic Northbridge scenario in Topic 01, construct a table with at least three flows. Include source, destination, data or purpose, trust-boundary crossing, and one security/reliability question per flow. You may state assumptions, but label them.

### Q5 — Advanced: threat analysis (5 marks)
A team claims that encryption in transit eliminates the risk of a cross-boundary data flow. Critique the claim. Describe three other control areas or failure modes to examine, and explain how the result should be recorded and linked to a risk register.

## 6. Topic 03 — Architecture description and viewpoints

**Marks: 20.** Q1 = 2; Q2 = 3; Q3 = 4; Q4 = 6; Q5 = 5.

### Q1 — Beginner: multiple choice (2 marks)
A **viewpoint** is best understood as:

A. A single vendor's reference architecture.  
B. A diagram file extension.  
C. A reusable specification for constructing and interpreting a view to address a class of stakeholder concerns.  
D. A list of project milestones.

### Q2 — Beginner: views and concerns (3 marks)
Distinguish architecture **description**, **view**, and **viewpoint**. Give one example of a stakeholder concern and a suitable view to address it.

### Q3 — Intermediate: concern-to-view mapping (4 marks)
For each stakeholder, propose a useful view and state the question it should answer: (1) security reviewer, (2) operations lead, (3) finance lead, (4) data-product consumer. Explain one risk of using a single diagram for all four.

### Q4 — Intermediate: description outline (6 marks)
Create a short architecture-description outline for a governed data platform. Include purpose/scope, stakeholders and concerns, views, assumptions/constraints, decisions, risks, and a method for navigating between artefacts. Show at least four traceability links.

### Q5 — Advanced: completeness versus volume (5 marks)
A package contains 40 diagrams but has no stakeholder matrix, no legend, no status/date, and no links to decisions or risks. Evaluate the package. Define a practical review method for view completeness and correspondence without treating diagram count as a quality metric.

## 7. Topic 04 — Architecture decision records and decision log

**Marks: 20.** Q1 = 2; Q2 = 3; Q3 = 4; Q4 = 6; Q5 = 5.

### Q1 — Beginner: multiple choice (2 marks)
Which is the strongest reason to record an ADR?

A. To replace architecture diagrams.  
B. To prevent stakeholders from challenging the decision.  
C. To prove the chosen option is permanently correct.  
D. To preserve context, alternatives, rationale, consequences, status, and conditions that could reopen a material decision.

### Q2 — Beginner: identify missing fields (3 marks)
An ADR contains only “Decision: use streaming because it is modern.” Name three material omissions and explain why each matters.

### Q3 — Intermediate: option comparison (4 marks)
**Synthetic assumptions:** a risk-reporting feed currently runs every night. The business asks whether to modernize it to streaming. No measured latency requirement or workload profile has been supplied. Compare (a) retaining batch with improvements and (b) introducing streaming. State the evidence needed before deciding; do not assume streaming is automatically superior.

### Q4 — Intermediate: draft an ADR (6 marks)
Draft a concise ADR for a hypothetical decision to standardize the ingestion interface for a new data product. Include ID/title, status, context, constraints, at least two alternatives, decision, rationale, consequences, risks, owner, and revisit triggers. Label any invented scenario details as assumptions.

### Q5 — Advanced: decision-log audit (5 marks)
A decision log has three records with the same ID; one ADR is marked “accepted” while the log says “superseded”; an exception has no expiry; and a major assumption changed. Specify the corrections and the traceability checks required. Explain when to supersede, revise, or reopen an ADR.

## 8. Topic 05 — Design reviews, threat models, and risk registers

**Marks: 20.** Q1 = 2; Q2 = 3; Q3 = 4; Q4 = 6; Q5 = 5.

### Q1 — Beginner: multiple choice (2 marks)
Which is the best description of a review finding?

A. A criterion-linked observation supported by evidence, with severity, owner, action, and closure condition.  
B. A threat category that automatically proves a vulnerability exists.  
C. A personal preference with no evidence.  
D. A risk score without a scenario.

### Q2 — Beginner: distinguish terms (3 marks)
Distinguish an **asset**, **threat**, **vulnerability/control gap**, **risk**, **mitigation**, and **residual risk**. Use one data-platform example.

### Q3 — Intermediate: review finding (4 marks)
A reviewer observes that a target-state DFD shows customer data moving from an ingestion zone to an analytics zone, but the flow has no classification, authorization, validation, or destination-owner information. Write one evidence-based finding with severity rationale, owner role, action, and closure evidence. Do not claim a breach has occurred.

### Q4 — Intermediate: threat and risk register (6 marks)
For a hypothetical file-ingestion flow crossing an external trust boundary, identify three plausible threat scenarios and create two risk-register entries. Each entry must include scenario, likelihood and impact scales (if used), treatment, owner, due/review date, status, and residual-risk statement. Explicitly state that ordinal scores are prioritization aids, not precise probabilities.

### Q5 — Advanced: acceptance and closure (5 marks)
A product lead asks to accept a high-impact risk “until later” because the release date is near. Explain what a defensible acceptance record needs, who should have authority under the local governance model, and how closure should be verified. If authority is unknown, say what must be clarified rather than inventing a policy.

## 9. Topic 06 — Reference architectures, standards, and reusable patterns

**Marks: 20.** Q1 = 2; Q2 = 3; Q3 = 4; Q4 = 6; Q5 = 5.

### Q1 — Beginner: multiple choice (2 marks)
Which statement is correct?

A. Any published architecture is mandatory for every project.  
B. Reuse removes the need to assess applicability.  
C. A standard states requirements or agreed rules within a defined scope; a pattern describes a reusable solution shape; a reference architecture gives a broader structural starting point; a technology choice selects a specific implementation option.  
D. A design pattern, reference architecture, standard, and technology choice are interchangeable terms.

### Q2 — Beginner: classify examples (3 marks)
Classify each as most closely a **reference model**, **reference architecture**, **design pattern**, **standard**, or **technology choice**, and explain that classification: (a) a conceptual taxonomy of platform capabilities, (b) a proposed arrangement of ingestion/storage/serving layers, (c) a repeatable quarantine-and-replay approach for failed files, (d) an organization-approved rule for classifying sensitive data, (e) selecting a specific managed streaming service. State where classification could depend on context.

### Q3 — Intermediate: compare patterns (4 marks)
**Synthetic assumptions:** one source delivers a daily file and has no real-time requirement; another source emits fraud events for a decision that must occur within seconds. Explain why one ingestion pattern may not fit both. Identify at least four evaluation criteria and one evidence item for each.

### Q4 — Intermediate: deviation/exception record (6 marks)
A reusable pattern expects centrally managed ingestion, but a constrained legacy source cannot yet use the shared interface. Draft a deviation/exception record with scope, reason, alternatives, risk, compensating controls, accountable approver (role, not invented named person), owner, expiry/review date, remediation plan, and evidence required for closure. Label the pattern as illustrative unless an approved repository standard is supplied.

### Q5 — Advanced: reuse judgement (5 marks)
A team proposes adopting a vendor reference architecture without comparing alternatives because “it is the industry standard.” Critique the reasoning. Give a repeatable selection procedure and describe conditions that would justify bespoke design or a justified adaptation.

## 10. Topic 07 — Team boundaries, ownership, and platform operating model

**Marks: 20.** Q1 = 2; Q2 = 3; Q3 = 4; Q4 = 6; Q5 = 5.

### Q1 — Beginner: multiple choice (2 marks)
Which statement best distinguishes a named owner from clear accountability?

A. A name in a spreadsheet proves the operational duties are defined.  
B. Ownership is unnecessary when a platform is managed.  
C. Every component must have two equally accountable teams.  
D. Clear accountability identifies the decision or outcome the role is answerable for, its authority, interfaces, and operational duties; a name alone may not.

### Q2 — Beginner: assign component ownership (3 marks)
Using illustrative teams **Platform Engineering**, **Risk Analytics**, and **Security & Governance**, assign a primary accountable party to each: shared ingestion service, risk data product, access policy, and risk report business definition. Give one reason per assignment and flag any responsibility requiring joint work without creating ambiguous accountability.

### Q3 — Intermediate: RACI and decision rights (4 marks)
Create a compact RACI for: approve a shared platform interface change; define a domain data product's business semantics; respond to a platform incident; accept a material security risk. Use R = responsible, A = accountable, C = consulted, I = informed. Keep one A per activity and state where local governance must determine the actual authority.

### Q4 — Intermediate: interface contract (6 marks)
Write an interface agreement between a platform team and a domain data-product team. Include service offered, input/output contract, service expectations, support hours or escalation assumptions, change notice, incident handoff, ownership, dependencies, and review cadence. Label assumptions.

### Q5 — Advanced: boundary failure analysis (5 marks)
A data pipeline fails. The platform team says the domain owns the pipeline; the domain says the platform owns scheduling and recovery. The runbook names neither team, and the risk register has no owner. Identify the ownership defects and propose a correction that separates component ownership, operational responsibility, incident command, risk ownership, and decision rights.

## 11. Topic 08 — Migration roadmaps and architecture modernization

**Marks: 20.** Q1 = 2; Q2 = 3; Q3 = 4; Q4 = 6; Q5 = 5.

### Q1 — Beginner: multiple choice (2 marks)
What makes a migration roadmap more than a list of desired future components?

A. It shows a justified path from evidenced current state to target state, including gaps, dependencies, sequencing, owners, checkpoints, risks, and cutover/rollback conditions where relevant.  
B. It uses optimistic dates.  
C. It assumes all legacy systems can be retired immediately.  
D. It omits temporary coexistence to keep the diagram simple.

### Q2 — Beginner: current-to-target gap (3 marks)
**Synthetic scenario:** current ingestion is manually operated and has incomplete ownership metadata; target ingestion is monitored, access-controlled, and owned. Name three gaps and one migration activity for each. State what evidence would verify closure.

### Q3 — Intermediate: dependency and critical path (4 marks)
Calculate the critical path for the following illustrative tasks. Durations are working days; finish-to-start dependencies apply; there are no resource constraints or calendar exceptions.

| Task | Duration | Predecessor(s) |
|---|---:|---|
| A — inventory source flows | 3 | — |
| B — define target contract | 2 | A |
| C — implement landing and validation | 4 | B |
| D — build reconciliation tests | 3 | B |
| E — parallel run and compare | 5 | C, D |
| F — cutover decision checkpoint | 1 | E |

Show earliest finish times, critical path, and total duration. Explain why the result is not a production commitment.

### Q4 — Intermediate: cutover and rollback plan (6 marks)
Create a concise cutover plan for migrating a regulatory report from a legacy warehouse to a new curated data product. Include coexistence, reconciliation, acceptance thresholds to be agreed before execution, decision authority, rollback trigger, rollback procedure, service-continuity safeguard, and decommissioning gate. Do not invent a real regulatory threshold.

### Q5 — Advanced: sequencing under constraints (5 marks)
The target architecture depends on an unowned upstream feed, an unresolved access-control design, and a reference-pattern exception. The business requests a fixed date. Explain how you would sequence work, manage uncertainty, define checkpoints, and decide whether to proceed, replan, or stop. Link at least three dependencies to Topics 04–07.

## 12. Topic 09 — Communicating trade-offs to technical and business stakeholders

**Marks: 20.** Q1 = 2; Q2 = 3; Q3 = 4; Q4 = 6; Q5 = 5.

### Q1 — Beginner: multiple choice (2 marks)
Which is the best practice when producing technical and business briefs for the same architecture decision?

A. Change numerical claims to match each audience's preferences.  
B. Hide residual risk from the business brief.  
C. Keep the underlying facts, assumptions, uncertainties, and decision consistent while changing emphasis, terminology, and detail.  
D. Present estimates as measured results if they make the recommendation clearer.

### Q2 — Beginner: translate accurately (3 marks)
Translate this technical statement for a business sponsor without overstating it: “The proposed design adds a validation stage and a replay path; measured end-to-end latency is not yet available.” Include the operational benefit and the uncertainty.

### Q3 — Intermediate: two briefs, one fact base (4 marks)
**Synthetic assumptions for both briefs:** Option A retains nightly batch with improved validation; Option B introduces streaming. No verified requirement demands sub-minute freshness. Streaming has higher implementation complexity in this scenario, but actual cost and latency measurements are unavailable. No comparative cost estimate or source-capability evidence has been supplied; do not invent either.

State a provisional recommendation and draft one technical sentence and one business sentence that preserve the same facts and uncertainty. Add a short fact-consistency check comparing the recommendation/status, assumptions, costs/estimates (including the absence of an estimate), risks, dependencies, and confidence level. The audience framing may differ; the underlying fact base must not.

### Q4 — Intermediate: decision brief (6 marks)
Write a compact decision brief with decision needed, context, options, recommendation strength, evidence, assumptions, trade-offs, risks, owner, next action, and revisit trigger. Include separate technical and business implications without changing the underlying facts.

### Q5 — Advanced: challenging stakeholder questions (5 marks)
A finance stakeholder asks, “Can you guarantee this will cut costs by 30%?” A security reviewer asks, “Does the diagram prove access is safe?” Answer both using evidence-based language. Identify what evidence would be needed to strengthen either claim and what you would not promise yet.

## 13. Cross-topic integration assessment

**Marks: 20.** Four questions, 5 marks each. Use the Northbridge scenario and state assumptions explicitly.

### Q1 — Intermediate: traceability chain (5 marks)
A target-state diagram adds a curated risk store, an ADR chooses the storage pattern, the threat model identifies a broad-access risk, the ownership matrix names no risk owner, and the migration roadmap schedules cutover. Identify the broken links and give a minimum repair plan across Topics 01–08.

### Q2 — Intermediate: constraint changes (5 marks)
A previously assumed source interface is now confirmed to be file-only, not event-stream capable. Which artefacts may need revision? Give at least five, and explain how the change propagates through decisions, risk, ownership, roadmap, and stakeholder communication.

### Q3 — Advanced: review finding to stakeholder decision (5 marks)
A review finds that a sensitive-data flow crosses a trust boundary without evidence of destination authorization. Outline the chain from finding to threat/risk record, ADR or design change, accountable owner, migration checkpoint, and business/technical communication. Do not assert an incident occurred.

### Q4 — Advanced: evidence challenge (5 marks)
A stakeholder claims, “The target architecture is secure, the migration is low risk, and the standard guarantees success.” Build a concise challenge response that separates facts, assumptions, unresolved questions, evidence needed, and decision implications. Identify at least three unsupported inferences.

## 14. Integrated architecture-review exercise — Northbridge Bank

**Marks: 100.** Suggested time: 6–8 hours. This is a proposed learning exercise aligned with the roadmap's final current-state-to-target-state architecture review. It is not a specification from the repository's currently empty project file.

### 14.1 Scenario inputs

Northbridge Bank is fictional. The following are **synthetic assumptions for this assessment**, not observed facts about a real organization:

| Item | Scenario input | Evidence status |
|---|---|---|
| Data estate | Approximately 300 pipelines: 120 on legacy warehouse ETL, 100 on a partially adopted lakehouse, and 80 team-built pipelines | Assumption supplied for exercise; not independently verified |
| Documentation | Existing architecture documentation is outdated; some pipeline ownership is recorded | Assumption supplied for exercise |
| Business goals | Move toward a governed lakehouse, preserve regulatory/risk reporting continuity, and support a permission-aware AI assistant for policy knowledge | Stated exercise goals |
| Constraints | Data must remain in-country; platform team capacity is limited; budget ceiling and exact regulatory dates are unspecified | Constraint supplied / details open |
| Known concerns | Undocumented flows, unowned pipelines, unclear access boundaries, legacy dependencies | Scenario concerns; validate before treating as confirmed defects |
| Stakeholders | Sponsor, risk and finance leaders, platform team, security, operations, internal audit, domain data owners | Proposed stakeholder set |
| Delivery scope | Documentation and migration planning only; no production deployment is authorized by this exercise | Explicit exercise scope |

### 14.2 Learner tasks and marks

| Task | Marks | Expected evidence |
|---|---:|---|
| A. Fact, assumption, and question register | 5 | Labels and verification plan; no assumption silently promoted to fact |
| B. Current-state and target-state views | 10 | Context/container/component/deployment views or structured equivalents; legends and evidence labels |
| C. Data-flow and trust-boundary analysis | 10 | Flow inventory, crossings, sensitive data, control questions, and unresolved evidence |
| D. Stakeholder concerns and viewpoints | 5 | Concern-to-view matrix; no material stakeholder concern left without a view or explicit deferral |
| E. ADRs and decision log | 10 | At least two material decisions, genuine alternatives, consequences, status, and revisit triggers |
| F. Review findings, threat model, and risk register | 10 | Evidence-linked findings; threat scenarios; risks with treatment, owner, and review/expiry as appropriate |
| G. Reference-pattern evaluation | 8 | Consistent criteria, alternatives, assumptions, recommendation, adaptations/deviations/exceptions where needed |
| H. Ownership and operating model | 8 | One accountable party per relevant component/decision/activity; interfaces, incident and escalation responsibilities |
| I. Migration roadmap | 12 | Gap analysis, phases, dependencies, milestones, checkpoints, critical path where durations are stated, cutover/rollback, decommissioning gate |
| J. Technical and business briefs | 8 | Audience-specific framing; consistent facts, estimates, assumptions, risks, and recommendation strength |
| K. Evidence register and cross-artefact consistency | 8 | Claims trace to evidence or are labeled assumptions; IDs/links align; no contradictory states |
| L. Reviewer defense | 6 | Answers five challenge prompts with evidence, uncertainty, and what would change the recommendation |
| **Total** | **100** | |

### 14.3 Required reviewer challenges

1. Which three claims in the package have the weakest evidence, and what would validate them?
2. What would make you change the target architecture or reopen an ADR?
3. Which trust-boundary crossing has the most material unresolved risk, and who owns its treatment?
4. What must be true before the first production cutover, and what causes rollback?
5. What would a business sponsor misunderstand if they read only the technical brief—or vice versa?

### 14.4 Integrated-exercise acceptance criteria

- Every material current-state element is labeled observed, reported, assumed, or unknown and has an evidence source or verification action.
- Current-state and target-state views are consistent across abstraction levels; target elements trace to requirements or goals.
- Every material flow has a source, destination, purpose/data description, and reviewed boundary crossings.
- Stakeholder concerns map to views or are explicitly deferred with a reason.
- Material decisions show real alternatives, rationale, consequences, status, and revisit triggers.
- Review findings are criterion-linked and evidence-based; threats are scenarios, not unsupported assertions that a vulnerability or incident exists.
- Risks have treatment, owner, status, and review/expiry where acceptance is time-bounded.
- Reuse is justified by applicability; deviations and exceptions are visible and governed.
- Each relevant component, decision, risk, and operational activity has an accountable party; interfaces and handoffs are explicit.
- The roadmap accounts for dependencies, coexistence, reconciliation, acceptance checkpoints, rollback conditions, and decommissioning criteria.
- Technical and business briefs share the same underlying fact base and disclose material uncertainty.
- A reviewer can trace three claims to evidence and reproduce any stated critical-path calculation.

## 15. Scoring rubric and readiness criteria

### 15.1 Marks and totals

| Component | Marks available |
|---|---:|
| Nine topic sections (20 each) | 180 |
| Cross-topic integration | 20 |
| Integrated architecture-review exercise | 100 |
| **Overall** | **300** |

Topic sections have five questions totaling 20 marks each. Use the per-question marks shown. For the integrated exercise, use the 100-mark task rubric in Section 14.2. Do not award points merely for length; score correctness, traceability, explicit assumptions, usable artefacts, and defensible reasoning.

### 15.2 Scoring open-ended answers and artefacts

For a question with a specified mark value, allocate marks across its required elements. Full credit requires correctness and all material elements. Partial credit is appropriate when the core idea is correct but a relevant assumption, dependency, owner, consequence, evidence item, or safety condition is missing. A materially unsafe or unsupported conclusion should not receive full credit even if terminology is polished.

For practical artefacts, score these dimensions as applicable:

1. **Correctness:** concepts and dependencies are technically coherent.
2. **Completeness:** required fields, flows, actors, alternatives, risks, owners, or checkpoints are present.
3. **Traceability:** claims link to evidence, requirements, decisions, risks, and actions.
4. **Consistency:** diagrams, ADRs, risk records, ownership, roadmap, and briefs agree.
5. **Uncertainty discipline:** assumptions, estimates, open questions, and limitations are labeled.
6. **Actionability:** owner, next action, acceptance evidence, and review date/trigger are clear.

### 15.3 Recommended readiness threshold

The module roadmap recommends readiness before the final project when all of the following hold:

- [ ] Average at least **85%** across the full assessment set.
- [ ] No topic section below **70%** (at least **14/20** in each topic).
- [ ] Integrated exercise completed.
- [ ] Gap log has no unresolved items older than one week.
- [ ] All nine topic gates and relevant practical artefacts are completed and reviewed.

For the 300-mark assessment, 85% is **255/300**. The integrated exercise is still a separate completion condition; a high total score does not compensate for a missing package or a serious safety/traceability defect. These thresholds are recommended study guidance from the module roadmap, not mandatory certification or proof of production competence.

### 15.4 Topic score sheet

| Topic | Score | Available | % | At least 70%? | Retest needed? |
|---|---:|---:|---:|---|---|
| 01. Diagrams | | 20 | | | |
| 02. Data flow/trust | | 20 | | | |
| 03. Description/viewpoints | | 20 | | | |
| 04. ADRs | | 20 | | | |
| 05. Review/threat/risk | | 20 | | | |
| 06. Patterns/standards | | 20 | | | |
| 07. Ownership/operating model | | 20 | | | |
| 08. Migration | | 20 | | | |
| 09. Communication | | 20 | | | |
| Cross-topic integration | | 20 | | n/a | |
| Integrated exercise | | 100 | | n/a | |
| **Total** | | **300** | | | |

## 16. Gap log and retest procedure

### 16.1 Gap log template

| Date | Question / artefact | Topic | Error type | Incorrect reasoning or omission | Missing concept | Corrective study/action | Retest date | Retest result | Closed by / evidence |
|---|---|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | Q__ / artefact ID | Topic __ | e.g. missing boundary | | | Re-read section __; redo exercise with new scenario | YYYY-MM-DD | Not attempted / partial / pass | |

Suggested error categories from the roadmap include: wrong diagram level; missing flow or boundary; decision without alternatives; finding without evidence; ownership ambiguity; migration infeasibility; and audience mismatch. Add other categories when useful.

### 16.2 Retest procedure

1. Explain the original error in one sentence without copying the answer key.
2. Revisit the exact lesson subsection and identify the rule or reasoning that was missed.
3. Redo the exercise with at least one changed condition, data flow, stakeholder, or constraint.
4. Ask a peer to review the new artefact if possible.
5. Record the retest result and evidence in the gap log.
6. If the same concept fails twice, redo the topic's practical exercise before continuing.
7. Before the integrated project, close old unresolved gaps; the roadmap recommends no unresolved learning gaps older than one week.

## 17. Complete answer key and model solutions

**Study instruction:** attempt Sections 4–14 before reading below. For open-ended tasks, use the criteria and model artefacts as a calibration guide, not a script to copy.

### 17.1 Topic 01 answers

**Q1 — D.** A context view establishes the system of interest and its external actors/systems. A list of classes/modules is too detailed (C); a context view does not prove deployed network configuration (A); and it complements rather than replaces deployment and data-flow views (B).

**Q2 — Model answer.** Context: who/what interacts with the system? Container: what major deployable/executable/data-store units make up the solution and how do they communicate? Component: what responsibilities exist inside a container and how do components collaborate? Deployment: where and in what runtime/network/environment do relevant software and data components run? Credit 0.75 per correctly distinguished level and useful question, capped at 3.

**Q3 — Model corrections.** (1) Add users/external systems and relationships to context; validate actor/system boundaries with stakeholders. (2) Show sources and ingestion interfaces on container view or explicitly scope them out with rationale. (3) Map `PolicyEnricher` to a containing container and check naming/correspondence. (4) Add environment/hosting/network or deployment-zone context at the appropriate level; mark unknowns rather than inventing topology. One mark per material defect and correction.

**Q4 — Model specification (6 marks).** Keep the two abstraction levels distinct and choose the same system boundary throughout.

- **Context view:** system of interest = `Risk Reporting Platform` (which contains the portal, API and data stores). External elements: Risk Analyst, Core Banking Source, Identity Provider. Directed relationships: `Risk Analyst → Risk Reporting Platform` (request/view risk reports); `Core Banking Source → Risk Reporting Platform` (provide scheduled risk extract); `Risk Reporting Platform → Identity Provider` (request authentication/identity validation); `Identity Provider → Risk Reporting Platform` (return authentication result/identity assertion, subject to the actual protocol). Do **not** draw the portal-to-API or API-to-store relationships as context relationships; those are internal to the system boundary.
- **Container view:** include Reporting Portal, Risk-serving API, File Ingestion Service, Raw Landing Store, Transformation Job, and Curated Risk Store. Show a separate `Scheduler` container only if evidence or the scenario establishes that scheduling runs as a distinct unit; if scheduling is embedded in the ingestion service, do not invent a separate container. Directed relationships: `Risk Analyst → Reporting Portal` (interact with reports); `Reporting Portal → Risk-serving API` (submit report query); `Risk-serving API → Curated Risk Store` (read curated risk data); `Core Banking Source → File Ingestion Service` (deliver scheduled file); `Scheduler → File Ingestion Service` (trigger scheduled ingestion, only if the scheduler is a separate unit); `File Ingestion Service → Raw Landing Store` (write received file); `Transformation Job → Raw Landing Store` (read input) and `Transformation Job → Curated Risk Store` (write transformed data). Show the identity-provider interaction at the appropriate container boundary if known.
- **Deployment details still open:** cloud/on-premises location; network/security zones and connectivity; runtime placement; key-management boundary; environment topology. Do not invent these without deployment evidence.

Suggested scoring: 1.5 marks for a coherent context view; 2.5 for a coherent container view; 1 for correctly directed and purpose-labelled relationships; 1 for explicit unknown deployment details. Full credit requires consistent system boundaries, no abstraction-level mixing, and labeled unknowns.

**Q5 — Model answer/checklist.** A visually complete diagram may be stale, ambiguous, inconsistent with implementation, or unsupported by evidence. Checklist: (1) correct scope and audience; (2) named elements and legend/notation; (3) relationships have direction and purpose; (4) cross-level consistency and traceability; (5) evidence/status/date and open questions; (6) boundaries/dependencies represented where material; (7) links to flows, ADRs, findings, risks, and owners. A finding should identify the criterion, evidence/location, severity, action, owner, due date, and closure evidence; update affected diagrams/DFD and link the ADR or risk record where relevant. Any five well-explained checks earn full credit.

### 17.2 Topic 02 answers

**Q1 — A.** Trust boundaries represent meaningful changes in trust/control/security/administrative domain. They are not limited to physical firewalls (B); a boundary does not guarantee encryption or safety (C); and a retention period is a different concern (D).

**Q2 — Model answer.** Useful fields: flow ID/name, source, destination, direction, data class/content, purpose, protocol/interface, frequency/volume, identity/authorization, transformation/validation, storage/retention, boundary crossings, owner, failure/retry behavior, lineage reference. “Data goes to the platform” lacks identifiable source/destination, payload, direction, purpose, control, and review scope. Scoring: 1.5 marks for five useful fields (0.3 each) and 1.5 marks for explaining why vague source, destination, payload, direction, purpose, or control details prevent review.

**Q3 — Model answer.** Questions include: what exact external partner and destination service/store? Is the flow file/API/stream and over what interface? What data classification/sensitivity applies? How is sender and receiver authenticated/authorized? What validation, malware/schema checks, quarantine, and replay exist? Which administrative/network/security boundaries are crossed? What are retention and deletion expectations? Who owns failures? Any four distinct points earn full credit.

**Q4 — Example flow table.** All flows below are illustrative assumptions.

| ID | Source → destination | Data/purpose | Boundary crossing | Security/reliability question |
|---|---|---|---|---|
| F-01 | Core Banking Source → File Ingestion | Scheduled risk-reporting extract | Source administration → platform ingestion zone | How are sender identity, file integrity, schema, and duplicate delivery verified? |
| F-02 | File Ingestion → Raw Landing | Original extract for controlled processing | Ingestion service → storage/security zone | Who can write/read; is quarantine and retention defined? |
| F-03 | Raw Landing Store → Transformation Job | Raw extract read for transformation | Storage zone → processing identity | Is the job authorized to read only the required data and are failed reads/retries logged? |
| F-04 | Transformation Job → Curated Risk Store | Validated/standardized risk data | Processing identity → curated-data access domain | Are service identities least-privileged and quality failures observable? |
| F-05 (optional) | Analyst → Reporting Portal/API | Authenticated query | User/device → application boundary | How are user identity and data entitlements enforced? |

Six marks require at least three coherent flows, boundaries, and questions; deduct for unlabeled assumptions or vague source/destination.

**Q5 — Model answer.** Encryption in transit does not prove the sender is legitimate, the receiver is authorized, data is classified correctly, content is valid, data is safe after arrival, keys are protected, replay/duplication is controlled, logs are sufficient, or retention is appropriate. Examine identity and authorization; validation/content integrity; destination access and retention; key management; monitoring/retry/replay; and data minimization. Record an evidence-linked finding/threat scenario and a risk with likelihood/impact rationale, treatment, owner, due/review date, and residual risk. Do not assert an incident or exploit without evidence.

### 17.3 Topic 03 answers

**Q1 — C.** A viewpoint defines a reusable way to construct/interpret views for a class of concerns. It is not a vendor architecture (A), file extension (B), or project milestone list (D).

**Q2 — Model answer (3 marks).** Architecture description: the organized description of the system and its architecture-related information. View: a representation addressing selected concerns for a stakeholder/audience. Viewpoint: conventions, model kinds, and rules used to create/interpret a class of views. Example: a security reviewer concerned about access and trust crossings may need data-flow/trust-boundary and identity/access views. **Scoring:** 1.5 marks for correctly distinguishing the three terms; 1 mark for a relevant stakeholder concern and suitable view; 0.5 for explaining why that view addresses the concern.

**Q3 — Model answer.** Security: DFD/trust-boundary and identity/control view; question: where sensitive data crosses boundaries and what controls apply? Operations: deployment/dependency/observability view; question: where are failure domains and recovery ownership? Finance: cost drivers/usage/option trade-off view; question: what assumptions drive cost and what is uncertain? Consumer: data-product contract/lineage/freshness view; question: what data is available, with what semantics and service expectations? A single diagram often overloads detail and fails to answer all concerns clearly.

**Q4 — Model outline.** Sections: purpose/scope; status/version/date; system context; stakeholder/concern matrix; current/target view catalogue; assumptions/constraints/dependencies; data flows and trust boundaries; decision/ADR index; review findings/threats/risks; reference-pattern assessments and deviations; ownership/operating model; migration roadmap; open questions; evidence register. Traceability examples: requirement R-01 → target view V-03 → ADR-02; flow F-04 → threat T-02 → risk RK-03; finding FN-05 → owner action → migration checkpoint CP-02; stakeholder concern C-OPS-01 → deployment view V-04. Full credit for usable outline and at least four traceability links.

**Q5 — Model answer.** Quantity does not establish relevance, accuracy, or consistency. Request a concern-to-view matrix; test each view's purpose/audience, scope, legend, status, evidence, and coverage; verify relationships across views and links to decisions/risks/flows; ask a representative reader to answer their questions using the package. Findings should be recorded with evidence and ownership. A 40-diagram package may be less useful than a small coherent set.

### 17.4 Topic 04 answers

**Q1 — D.** ADRs preserve context, alternatives, rationale, consequences, status, and revisit conditions. They do not replace diagrams (A), block challenge (B), or make a decision permanently correct (C).

**Q2 — Model answer.** Missing context/requirements, constraints and assumptions; alternatives and evaluation criteria; rationale/evidence; consequences/trade-offs; status/owner/date; risks; revisit triggers. Any three with explanation earn full credit.

**Q3 — Model answer.** Batch improvements may fit a nightly need, have lower change/operational complexity, and permit better validation/reconciliation; streaming may improve freshness but introduces event processing, ordering/duplication/replay, monitoring, and skills/cost implications. Missing evidence: freshness requirement and business consequence; source capability; event volume/bursts; latency measurements; failure/replay needs; team readiness; cost model; reporting correctness requirements. A provisional recommendation may retain batch until a verified requirement or evidence justifies streaming; a different answer is acceptable if the assumptions and decision criteria support it.

**Q4 — Model ADR skeleton.**

- **ID/title:** ADR-ING-01 — Standardize the new data-product ingestion interface.
- **Status/owner/date:** Proposed; owner role: Data Platform Architecture; date to be set.
- **Context:** New product needs an ingestion interface; details below are hypothetical.
- **Constraints/assumptions:** Existing source supports a scheduled file or API (must verify); shared interface should expose validation, failure, and ownership semantics.
- **Options:** A) shared ingestion contract; B) bespoke pipeline; C) defer and continue current mechanism.
- **Decision/rationale:** Choose A provisionally if source compatibility, required freshness, and security controls are demonstrated; otherwise revise. Criteria: security, operability, consumer contract, cost, team capability.
- **Consequences:** Reuse and consistent support; initial adoption work; possible adaptation for legacy sources.
- **Risks:** Source incompatibility, unclear ownership, migration effort.
- **Revisit triggers:** source cannot meet contract; measured latency/cost misses agreed threshold; security finding remains open.
- **Links:** relevant diagrams, DFD, review findings, pattern assessment, ownership matrix, migration checkpoint.

Full credit requires alternatives and conditional rationale rather than a bare conclusion.

**Q5 — Model answer.** Assign stable unique IDs; establish one authoritative status and reconcile ADR/log; record supersession links; add exception owner, scope, approval authority, compensating controls, expiry/review date, and closure condition; update impacted views, risks, patterns, ownership, roadmap, and briefs when assumptions change. Revise an ADR for a correction that does not change the underlying decision; supersede it when a new decision replaces it; reopen/reconsider when a material assumption, constraint, requirement, risk, or evidence changes. Do not erase history.

### 17.5 Topic 05 answers

**Q1 — A.** A finding is a criterion-linked observation supported by evidence and made actionable through an owner, action, severity, and closure condition. A threat category alone does not prove a vulnerability (B); personal preference is not evidence (C); and a risk score without a scenario is incomplete (D).

**Q2 — Model answer.** Asset: valuable data/service/process (e.g., customer risk data). Threat: possible harmful event/actor/action (e.g., unauthorized access). Vulnerability/control gap: weakness enabling the scenario (e.g., destination authorization not evidenced). Risk: uncertain event and consequences (e.g., unauthorized disclosure due to broad access). Mitigation: control/action reducing likelihood or impact. Residual risk: risk remaining after controls. Scoring: 0.5 mark for each correctly distinguished term (3 marks total); the example must be coherent for full credit.

**Q3 — Example finding.** **ID:** FND-01. **Proposed review criterion for this exercise (not an asserted external rule):** sensitive-data flows should have documented classification, authorization, validation, and ownership. **Evidence:** target-state DFD flow `F-07` shows movement from ingestion to analytics but has no linked classification/control/owner record (diagram version/date must be supplied). **Severity:** major/provisional because sensitive-data access and accountable control cannot yet be reviewed; final severity depends on classification and existing control evidence. **Action:** identify data class and destination owner; document identity/authorization and validation controls; link evidence. **Owner:** relevant data-product owner with platform/security participation; one accountable role must be assigned. **Closure:** approved flow record, control configuration/test evidence, and reviewer sign-off. This is not a claim of a breach.

**Q4 — Model entries.** Three distinct threat scenarios are: (1) a forged or compromised sender submits a malicious/malformed file; (2) an attacker or faulty client replays a valid file, causing duplicate or stale reporting; (3) an unauthorized principal reads raw data after ingestion because storage permissions are too broad. The table records two of these as risk entries; the third may be recorded as a separate threat or added as another risk if the learner justifies the scope. Scores and dates below are synthetic, illustrative planning values, not measured probabilities or real policy deadlines. Ordinal scores prioritize attention; they are not precise probabilities.

| Risk | Scenario | Likelihood / impact | Treatment | Owner | Review/status | Residual risk |
|---|---|---|---|---|---|---|
| RK-01 | Forged or malformed file crosses external boundary and enters processing because sender verification or validation/quarantine is ineffective | L=3, I=4 (illustrative) | Mitigate: sender authentication, integrity verification, schema/content checks, quarantine, monitored replay | Ingestion Service Owner (illustrative accountable role; confirm actual assignment) | 2026-11-15 review date (illustrative; must be before the relevant launch gate); Open | Novel malformed content or control bypass remains possible; test and monitor |
| RK-02 | Unauthorized principal reads raw data after ingestion due to over-broad storage permissions | L=2, I=5 (illustrative) | Mitigate: least privilege, access review, audit, sensitive-data controls | Raw Data Product Owner (illustrative accountable role; confirm whether local governance assigns this to a distinct access-control owner) | 2026-11-22 review date (illustrative; revise to match the test plan); Open | Misconfiguration and privileged-access risk remain; monitor and periodically review |

Suggested scoring: 1.5 marks for three distinct plausible threat scenarios; 2.25 marks per risk entry for a coherent scenario, stated scoring rationale, treatment, single accountable owner, review date/status, and residual risk. Accept different dates if explicitly labeled as synthetic and sequenced sensibly. Do not treat the illustrative dates or ordinal scores as policy or measured evidence.

**Q5 — Model answer.** A defensible acceptance records the risk scenario, impact, likelihood rationale, existing controls, residual risk, alternatives, compensating controls, business rationale, accepting authority, accountable owner, explicit scope, expiry/review date, and closure/revisit trigger. The local governance model must define who may accept that level of risk; if it is not supplied, mark approval authority as an open question and escalate rather than inventing a policy. Closure requires evidence that agreed treatment is implemented/tested, or a renewed authorized acceptance; a ticket marked “done” alone is insufficient.

### 17.6 Topic 06 answers

**Q1 — C.** A standard defines requirements or agreed rules within scope; a pattern is a reusable solution shape; a reference architecture is a broader structural starting point; and a technology choice selects an implementation option. Publication does not make an architecture universally mandatory (A), reuse does not remove applicability assessment (B), and the terms are not interchangeable (D).

**Q2 — Model classifications.** (a) Reference model: a conceptual taxonomy of capabilities/relationships, often technology-neutral. (b) Reference architecture: a proposed structural arrangement of capabilities/components/relationships that can guide a solution. (c) Design pattern: repeatable quarantine-and-replay solution shape. (d) Standard: an approved rule within the organization's defined scope, if the scenario explicitly says it is organization-approved. (e) Technology choice: a specific managed service selection. Classification can vary by how an artefact is authored and governed; do not infer that (d) is adopted in the actual repository—it is hypothetical in the question. Scoring: 0.6 mark per defensible classification with a reason; accept an alternative classification when the learner explains the context.

**Q3 — Model answer.** Daily file: batch is plausibly sufficient, simpler to reconcile, and may be easier to operate. Fraud event: streaming or event-driven processing may be justified by a verified seconds-level decision requirement, but introduces event-time, duplicate/order, replay, observability, and operational complexity. Criteria/evidence examples: freshness (business SLA/measurement); source capability (interface contract); throughput/burst (load profile); correctness/reconciliation (test results); security (flow/control review); operating skills (team capability assessment); cost (unit-cost model). Alternative choices can be defended if requirements and evidence support them.

**Q4 — Model deviation/exception.** Include ID; pattern/rule reference and version; scope/component; requested deviation; reason and evidence; alternatives considered; affected requirements/risks; compensating controls; accountable approver role per local governance; owner; start/expiry/review date; migration/remediation plan; monitoring; closure evidence. Example: allow a temporary file adapter for one named legacy source while shared ingestion is unavailable; isolate access, validate/quarantine, log and reconcile files, restrict scope, review monthly (illustrative), and expire when adapter migration passes acceptance. Do not imply that the pattern is an adopted standard unless evidence says so.

**Q5 — Model answer.** Procedure: clarify requirements/constraints and decision criteria; establish candidate options; verify reference applicability and assumptions; compare options against the same criteria with evidence and uncertainty; assess security/governance/scale/reliability/interoperability/cost/operability/team capability; record rationale, consequences, deviations, and revisit triggers in ADR; obtain appropriate review/approval. Bespoke design may be justified where no pattern fits a material constraint, where reuse creates unacceptable risk/cost, or where an existing pattern cannot meet verified requirements. Bespoke design also creates maintenance and review costs that must be explicit.

### 17.7 Topic 07 answers

**Q1 — D.** Accountability means being answerable for an outcome or decision with authority and clear scope. A name alone does not define duties (A); managed platforms still need ownership (B); and each work item should not have two equally accountable parties (C).

**Q2 — Example assignments.** Shared ingestion service → Platform Engineering accountable for platform service operation and shared interface; Risk data product → Risk Analytics accountable for product semantics/quality/consumer contract; access policy → Security & Governance accountable for policy design only if local governance grants that authority; risk report business definition → Risk Analytics or the designated risk business owner. Operational implementation may be shared, but name one A per item. If local policy or role authority is unknown, mark it for confirmation. Scoring: 0.5 mark for each of the four defensible primary assignments (2 marks) and 1 mark for reasons plus explicit handling of uncertain authority without duplicate A assignments.

**Q3 — Example RACI.**

| Activity | Platform Engineering | Domain/Data Product | Security & Governance | Operations / incident lead | Business risk owner | Designated risk-acceptance authority (role to identify if distinct) |
|---|---|---|---|---|---|---|
| Approve shared interface change | A/R | C | C when control impact | C | I | I |
| Define domain product semantics | C | A/R | C for sensitive classifications | I | C | I |
| Respond to platform incident | R | R for product-impact triage | C | A (proposed incident-command role; confirm locally) | I; consult if agreed severity criteria trigger | I |
| Accept material security risk | C | R for remediation context | R/C for risk assessment | C | C unless formally delegated authority is confirmed | A (role must be identified from local governance before any acceptance is valid) |

This is an illustrative proposed allocation, not an assertion about actual local authority. It assigns one A per row while making unresolved authority explicit: for risk acceptance, the **identity and delegation of the A role must be verified before the record can be approved**. If local governance gives that authority to the business risk owner, move the A to that column rather than adding a second A. If the authority cannot be established, risk acceptance remains blocked and the operating-model gap must be escalated. **Scoring:** 1 mark per activity row; full credit for one accountable role, sensible R/C/I assignments, and an explicit note that the designated risk-acceptance authority must be confirmed before any risk acceptance is valid.

**Q4 — Model interface agreement.** Define provider/consumer; service purpose; input/output schemas and semantic versioning; authentication/authorization; freshness/availability expectations; data-quality/validation behavior; error/retry/replay; monitoring and support hours; incident severity and escalation; change notice/deprecation; upstream dependencies; data owner and platform owner; service-level metrics; review cadence; exception handling. Label service targets and hours as proposed until agreed. Award for contract clarity and operational handoffs.

**Q5 — Model answer.** Defects: disputed component boundary; scheduling/recovery responsibility unclear; runbook lacks named roles; no accountable risk owner; no incident commander/escalation path; possibly unclear monitoring and service expectations. Repair: designate accountable owner per component and risk; split platform scheduling/service duties from domain data logic where appropriate; define RACI for failure triage, recovery, data correction, and communications; define incident command and escalation; update runbook, service/interface contract, ownership matrix, risk register, and ADR if boundary changes; verify through tabletop or failure test. A named owner alone is insufficient if authority and duties remain ambiguous.

### 17.8 Topic 08 answers

**Q1 — A.** A roadmap describes a justified path from evidenced current state to target, with gaps, dependencies, sequencing, owners, checkpoints, risks, and relevant cutover/rollback controls. Optimistic dates (B), immediate retirement assumptions (C), and omitting coexistence (D) do not establish a credible transition.

**Q2 — Model answer.** Gaps/activities/evidence: (1) manual operation → automate/orchestrate with retries and alerting → run history, failure injection, alert test; (2) incomplete ownership metadata → assign accountable component/product owners and publish interfaces → reviewed ownership matrix and contact/escalation test; (3) access controls undocumented → classify data and define identity/authorization → approved control mapping and access test evidence. More than one activity may be needed per gap.

**Q3 — Critical path calculation.** Earliest-finish calculation with finish-to-start dependencies:

| Task | Duration | Predecessor(s) | Earliest start | Earliest finish |
|---|---:|---|---:|---:|
| A | 3 | — | 0 | 3 |
| B | 2 | A | 3 | 5 |
| C | 4 | B | 5 | 9 |
| D | 3 | B | 5 | 8 |
| E | 5 | C, D | max(9, 8) = 9 | 14 |
| F | 1 | E | 14 | 15 |

Paths: A–B–C–E–F = 3+2+4+5+1 = **15 working days**; A–B–D–E–F = 3+2+3+5+1 = **14 working days**. The critical path is A–B–C–E–F (15 days); the D branch has one working day of total slack in this simplified network. This is not a production commitment because estimates, resource contention, calendars, approval lead times, defects, data volumes, environment availability, and unlisted dependencies are excluded.

**Q4 — Model cutover plan.** Before cutover: establish baseline, owner, source-to-target mapping, data reconciliation method, agreed business acceptance thresholds, security/operational readiness, backup/recovery and rollback rehearsal, monitoring, support coverage, and decision authority. Run legacy and target in parallel; compare record counts, totals, key distributions, timeliness, and business-defined results; investigate discrepancies. Cutover only after named approvers confirm acceptance and no unresolved blocker-level risk. Roll back if reconciliation exceeds agreed tolerance, data freshness/availability fails, security control fails, or regulatory/risk reporting continuity is threatened. Rollback steps: stop or reverse routing, preserve evidence, restore prior serving path, reconcile late/duplicate writes, communicate status, and validate service recovery. Decommission only after agreed stable period, downstream dependency check, retention/legal hold review, restore/archival evidence, and explicit approval. Exact thresholds and authority must be agreed, not invented.

**Q5 — Model answer.** First map prerequisites: identify the upstream feed owner and contract; resolve access design with evidence and accountable security/data authority; decide the pattern exception with scope, compensating controls, expiry, and owner. Sequence discovery and decisions before dependent build/cutover; use bounded experiments and early checkpoints; keep legacy serving active until reconciliation and acceptance pass; define no-go/rollback conditions. Replan if dependencies or resource estimates invalidate dates; stop before a high-risk transition if required controls or owners remain unresolved. Link to Topic 04 ADRs/revisit triggers, Topic 05 risks/findings, Topic 06 pattern deviation, and Topic 07 ownership/interface agreements. A business date is a constraint to manage, not proof that the plan is feasible.

### 17.9 Topic 09 answers

**Q1 — C.** Audience-specific framing can change emphasis, terminology, and detail, but not the underlying facts, assumptions, uncertainties, or decision. Changing claims to suit preferences (A), hiding residual risk (B), or presenting estimates as measurements (D) would distort the evidence.

**Q2 — Model translation.** “The design adds an automated check before data is accepted and a controlled way to retry failed inputs. That may improve detection and recovery, but we have not yet measured end-to-end processing time, so we cannot promise a freshness improvement until a representative test is run.” Full credit preserves both possible benefit and uncertainty.

**Q3 — Model answer.** A defensible provisional recommendation is to improve batch first if the existing nightly cadence meets the business need, while gathering evidence on freshness, cost, and source capability before committing to streaming. Technical sentence: “Option A retains batch and adds validation; no verified sub-minute freshness requirement, source-capability evidence, or comparative cost/latency measurements are currently available, so streaming's operational and performance benefit remains unproven.” Business sentence: “Improving the nightly process may reduce avoidable errors with less change complexity; we should not commit to streaming cost or faster business outcomes until the freshness need and measured alternatives are confirmed.”

| Fact to compare | Technical brief | Business brief | Consistency check |
|---|---|---|---|
| Current cadence | Nightly batch | Nightly reporting process | Same cadence; no claim of real-time service |
| Recommendation | Provisional batch improvement plus evidence-gathering | Same provisional recommendation | Same option/status |
| Costs/performance | No comparative measurements supplied | No cost saving or latency improvement promised | Absence of evidence stated in both |
| Main uncertainty | Source capability, workload, latency requirement | Whether faster freshness is worth additional complexity/cost | Different emphasis, same underlying unknowns |

**Scoring:** 1.5 marks for a usable technical brief, 1.5 for a usable business brief, and 1 for the fact-consistency check. Other recommendations can score well if they preserve the stated assumptions, compare defensible criteria, and state what evidence would change the recommendation.

**Q4 — Model decision brief.** Include decision requested; decision owner and date; context and constraints; options; recommendation strength (e.g. provisional); evidence vs assumptions; comparison criteria; business and technical consequences; risks and residual uncertainty; dependencies; implementation/validation next steps; accountable owners; revisit triggers. Use identical figures and status labels across audience versions. Full credit for a concise, decision-oriented brief rather than a generic architecture description.

**Q5 — Model answer.** Finance: “We cannot guarantee a 30% reduction from current evidence. We need a comparable baseline, scoped cost model, workload assumptions, implementation/operating costs, and measured pilot or usage data; we can state a scenario estimate only with its assumptions and range.” Security: “A diagram shows intended structure and flows; it does not prove deployed authorization is correct. We need policy/configuration evidence, identity mappings, tests, logs, and review of relevant trust-boundary crossings.” Do not promise savings, security, compliance, or delivery dates without evidence. Explain what evidence would change recommendation strength.

### 17.10 Cross-topic integration answers

**Q1 — Traceability chain.** Broken links: target store must trace to requirements and consistent views; ADR must cite options/criteria and link to diagrams; threat must map to a concrete flow/asset/control gap; risk lacks accountable owner and treatment; roadmap cutover lacks acceptance and rollback tied to risk closure. Repair: update view and DFD IDs; record finding/threat/risk with evidence, owner, treatment, and due/review date; update ADR consequences/controls; assign owner via Topic 07 matrix; add checkpoint and no-go/rollback conditions to roadmap; ensure stakeholder briefs reflect same risk and status.

**Q2 — Constraint changes.** Revisit at least: current/target context/container diagrams; data-flow inventory and DFD; architecture description/viewpoint coverage; ADR option assessment/status; threat model/risk register; pattern comparison/deviation record; ownership/interface contract; migration gap analysis/dependencies/critical path; stakeholder briefs and decision log. Propagation: file-only source may invalidate streaming assumptions, change validation and latency expectations, alter risks/ownership, require a pattern adaptation, change phase estimates/checkpoints, and require corrected communication. Update all affected artefacts and preserve decision history.

**Q3 — Model chain.** Record the DFD flow ID and evidence as a review finding against the applicable control criterion; assess threat scenario and risk impact without asserting a breach; identify current controls and missing evidence; assign accountable risk/control owner and treatment; decide whether to change design/ADR or gather evidence; define acceptance tests and a migration gate; update ownership and runbook; communicate facts, uncertainty, next action, and residual risk consistently to technical/business audiences.

**Q4 — Model challenge response.** “Those statements exceed the evidence available. The target diagram describes intended architecture, not tested controls; migration risk depends on unresolved dependencies, ownership, validation, and rollback readiness; a reference pattern does not guarantee outcomes. We need deployment/configuration evidence, threat and risk treatment, ownership confirmation, pattern applicability assessment, reconciliation results, and a rehearsed rollback plan. Until then, security and migration readiness remain open decisions.” Unsupported inferences include: diagram proves security; low risk follows from a target design; standard guarantees success; and planned dates prove feasibility. Full credit distinguishes facts/assumptions/questions and identifies decision consequences.

### 17.11 Integrated exercise model solution outline

This is a **solution outline**, not a single mandated target architecture. Alternative designs may be valid if they satisfy the scenario, state assumptions, show trade-offs, and preserve traceability.

#### A. Facts/assumptions/open questions register (example)

| ID | Statement | Classification | Verification/action |
|---|---|---|---|
| E-01 | Scenario describes ~300 pipelines split 120/100/80 | Supplied exercise assumption | Validate against inventory before using for sizing or schedule |
| E-02 | Existing documentation is outdated | Supplied exercise assumption | Sample diagrams and compare with deployed configuration/owners |
| E-03 | Regulatory reporting must not be interrupted | Supplied exercise constraint | Confirm service window, business owner, acceptance criteria, and required continuity evidence |
| E-04 | Budget ceiling is not specified | Open question | Obtain finance-approved limit and cost scope |
| E-05 | All pipelines can be moved to one pattern | Unsupported assumption | Inventory source capabilities, consumer needs, and exceptions; do not assume uniform fit |
| E-06 | AI assistant must enforce document permissions | Supplied target goal | Define identity propagation, document ACL behavior, retrieval tests, and audit requirements |
| E-07 | The target must keep data “in-country,” but the jurisdiction and approved residency boundary are not named | Open question / constraint detail missing | Confirm the applicable jurisdiction and data-location scope with the authorized business, legal, and governance roles; do not infer a country |

#### B. Architecture views

A defensible package includes: context view for analysts, risk/reporting systems, source systems, platform, identity, and AI knowledge consumers; container view for ingestion, raw/curated zones, processing, metadata/catalog, governance/access enforcement, serving, observability, and legacy integration; component view for material internal responsibilities; deployment view only to the level supported by known topology. Label unknown hosting/network details. Keep the legacy warehouse and lakehouse both visible in current state; do not draw the target as if already deployed.

#### C. Data-flow and trust-boundary outline

Inventory source-to-ingestion, ingestion-to-raw, raw-to-curated, curated-to-reporting, identity-to-serving, and policy-document-to-index/retrieval flows as applicable. For each, state source, destination, purpose, sensitivity, interface, owner, and controls/evidence. Mark external-source, user/application, administrative, and data-zone boundaries as applicable. For the AI assistant, review permission propagation and whether retrieval can return documents the caller is not authorized to read. Treat these as review questions unless evidence establishes a defect.

#### D. Example ADRs

- **ADR-01 — Incremental migration rather than big-bang replacement.** Options: big bang, phased domain migration, retain legacy with targeted fixes. Provisional choice: phased migration because reporting continuity and incomplete inventory make a single cutover high risk. Consequences: coexistence and reconciliation cost; temporary dual operations; need for ownership and decommissioning gates. Revisit if validated dependencies or funding materially change.
- **ADR-02 — Select ingestion patterns by freshness and source capability.** Options: batch, streaming, hybrid. Choose per workload against measured freshness, source support, correctness, security, cost, and operability. Do not declare one pattern universal.

#### E. Review/threat/risk outline

Sample finding: “Flow F-12 crosses from source administration into the ingestion zone; sender identity and file-integrity evidence are not linked in the current package.” Severity should be provisional until sensitivity and control evidence are confirmed. Sample risks: unowned pipeline causes delayed recovery; incorrect reconciliation leads to reporting inconsistency; over-broad retrieval access exposes policy content. Each risk needs owner, treatment, review date, residual risk, and links to affected flows/decisions/checkpoints.

#### F. Reference pattern and deviation outline

Compare batch ingestion for daily extracts, streaming for verified low-latency events, and hybrid integration for sources with mixed capabilities. Use common criteria: requirement fit, source compatibility, security/governance, reliability, scaling, interoperability, cost, operability, and team skills. For a legacy source that cannot use the shared interface, record a scoped temporary adapter exception with compensating controls, accountable approver role, expiry/review, owner, and migration plan. No named pattern or standard is assumed to be formally adopted by the repository.

#### G. Ownership outline

Assign one accountable role per shared platform component, domain data product, architecture decision, risk, and operational activity. A plausible illustrative split: platform team owns shared ingestion/runtime service; domain team owns product semantics and data-quality outcomes; security/governance owns policy design or control review within its actual authority; operations/incident lead owns incident command if the operating model says so; business risk authority accepts material risk under the local governance model. Confirm actual decision rights rather than inferring them from team names.

#### H. Migration roadmap outline

1. **Discover and baseline:** inventory pipelines/flows, owners, dependencies, data classes, consumers, and service needs; evidence-label current state.
2. **Resolve blockers:** assign owners; confirm regulatory reporting acceptance criteria; decide access controls; resolve reference-pattern exceptions; record ADRs and risks.
3. **Build foundation:** implement shared controls, observability, metadata/lineage, validation, and target interfaces for a bounded pilot.
4. **Pilot and parallel run:** select a representative low-risk workload; reconcile counts, totals, key distributions, freshness, and business outcomes; test failure/replay and access controls.
5. **Wave migration:** sequence by value, risk, dependency readiness, source compatibility, and team capacity; retain coexistence where needed.
6. **Cutover checkpoint:** named business/technical/security/operations authorities confirm agreed acceptance criteria; stop or roll back on reconciliation failure, access-control failure, freshness/service breach, or unresolved blocker risk.
7. **Stabilize and decommission:** monitor agreed stable period; confirm downstream dependencies, archive/retention, recovery evidence, and approval before retiring legacy components.

Exact dates, cost, capacity, acceptance thresholds, and path durations remain open until measured or approved inputs are supplied. Any critical-path calculation must show task durations and dependencies and be independently reproducible.

#### I. Stakeholder communication consistency

Technical brief: describe components, flows, boundary controls, data contracts, dependencies, validation tests, migration gates, operational ownership, and open evidence. Business brief: explain reporting continuity, risk, decision needed, staged value, cost uncertainty, and no-go/rollback conditions. Both must use the same current-state assumptions, recommendation status, risk rating/status, cost estimate or absence of estimate, and delivery confidence.

#### J. Evidence register (example)

| Claim ID | Claim | Evidence/status | Artefact link | Owner/action |
|---|---|---|---|---|
| CL-01 | Current pipeline split is 120/100/80 | Scenario assumption; unverified | Current-state inventory | Data platform discovery lead to validate |
| CL-02 | Target can preserve reporting continuity | Not yet demonstrated | Migration roadmap / test plan | Risk reporting owner to define acceptance and approve evidence |
| CL-03 | Permission-aware AI retrieval meets access needs | Target requirement, not proven | DFD / threat model / ADR | Security and product owners to define and test access cases |
| CL-04 | Phased migration is lower risk than big bang | Provisional recommendation | ADR-01 / risk register | Architecture owner to revisit after dependency and cost evidence |

#### K. Reviewer-defense model response outline

1. **Weakest evidence:** the pipeline split is an unverified scenario assumption; reporting continuity is a goal not yet demonstrated by reconciliation evidence; permission-aware AI retrieval is a target requirement, not a tested control. Name the inventory, business acceptance test, and permission test needed to strengthen each claim.
2. **Reopen a decision:** revisit an ADR if source capability, freshness requirements, data-residency interpretation, cost/capacity estimates, risk treatment, or downstream dependencies materially change. Record new evidence, consequences, status, and any superseding decision rather than silently editing history.
3. **Most material trust-boundary risk:** identify the flow by its DFD ID and explain the possible consequence; do not assert a vulnerability or breach without evidence. Assign one accountable risk/control owner, treatment, review date, and closure evidence. If owner or control evidence is missing, record it as an open gap.
4. **Before production cutover:** require agreed reconciliation and business acceptance thresholds, authorization/control tests, operational support and incident ownership, dependency readiness, rollback rehearsal, and named decision authority. Roll back or stop if reconciliation fails, access control fails, service/freshness limits are breached, or continuity is threatened. The exact thresholds must be agreed, not invented.
5. **What one brief could obscure:** a technical-only brief may understate business consequences, cost uncertainty, and the decision requested; a business-only brief may omit control mechanisms, technical dependencies, and test evidence. Both must retain the same fact base, risk status, assumptions, estimate status, and recommendation strength.

These are model reasoning paths, not the only valid answers. Award full credit when the learner cites relevant artefacts/evidence, states uncertainty, identifies accountable action, and explains what would change the recommendation.

### 17.12 Integrated exercise scoring guidance

Award the task marks in Section 14.2. Within each task, use these general anchors:

- **Full marks:** all key elements present, internally consistent, evidence-linked, assumptions labeled, and actions/owners/acceptance criteria explicit.
- **Approximately half marks:** broadly correct direction but material gaps in traceability, ownership, evidence, alternatives, or safeguards.
- **Low/zero marks:** missing artefact or materially unsafe reasoning; claims unsupported by scenario; conflicting facts between briefs; critical dependency ignored; or cutover without acceptance/rollback controls.

Do not award full marks for a beautiful diagram or polished presentation if the underlying assumptions are concealed or the artefacts contradict each other.

## 18. Final assessment completion checklist

### Knowledge and topic gates

- [ ] Attempted all 45 topic questions before reading the answer key.
- [ ] Achieved at least 14/20 in each topic or completed and passed a retest.
- [ ] Reviewed every incorrect or partly correct answer and recorded its gap-log entry.
- [ ] Re-attempted failed concepts with a changed scenario, not only by memorizing the model answer.

### Integrated capability

- [ ] Completed cross-topic integration questions.
- [ ] Completed the integrated architecture-review exercise and evidence register.
- [ ] Produced current-state and target-state views with explicit evidence status.
- [ ] Linked material flows, decisions, findings, threats, risks, patterns, owners, migration checkpoints, and communication briefs.
- [ ] Verified technical and business briefs share the same facts and disclose material uncertainty.
- [ ] Reproduced any critical-path calculation and traced at least three claims to evidence.
- [ ] Defended the package against at least five reviewer questions.

### Readiness and governance

- [ ] Achieved the roadmap-recommended average of at least 85% (255/300) across the assessment.
- [ ] No topic remains below 70% (14/20).
- [ ] Integrated exercise completed; old unresolved learning gaps are closed or explicitly documented with a remediation plan and retest date.
- [ ] All nine topic gates and relevant artefacts have been reviewed by another person where practical.
- [ ] Remaining assumptions, limitations, and unresolved decisions are visible; no unsupported claim of production readiness is made.

**Readiness statement:** Passing this assessment is evidence of learning progress against this module's recommended outcomes. It does not, by itself, establish production competence, prove an architecture is secure/compliant, or replace project-specific review, testing, governance approval, or operational validation.
