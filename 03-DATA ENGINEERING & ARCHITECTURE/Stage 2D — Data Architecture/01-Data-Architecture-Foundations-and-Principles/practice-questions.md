# Practice Questions — Data Architecture Foundations and Principles

> **Stage:** Stage 2D — Data Architecture  
> **Module:** `01-Data-Architecture-Foundations-and-Principles/`  
> **Scope:** Lessons 01–06 plus integrated banking case study  
> **Purpose:** Test both conceptual understanding and practical architectural competence.

## How to use this assessment

This assessment follows the learning objectives, exercises, expected deliverables, mastery criteria, completion gates, and module-wide expectations in `roadmap-Data-Architecture-Foundations-and-Principles.md`. The project tree places this file beside the six lesson files and the current-state inventory project.

Work in this order:

1. Answer the questions for a lesson **closed-book**.
2. Label each answer **correct**, **partly correct**, or **wrong**.
3. Compare it with the answer outline. The outline gives essential reasoning, not the only acceptable wording or design.
4. Correct every partly correct or wrong answer in writing and re-attempt it after a delay of several days.
5. For scenario and artifact questions, preserve your assumptions, evidence, alternatives, trade-offs, accountable roles, and revisit triggers.
6. Have a reviewer challenge your advanced answers and the integrated case. Record the challenge and your response.

A correct definition alone does not prove applied competence. For decision questions, full credit requires a defensible conclusion grounded in facts, stated assumptions, criteria, options, trade-offs, and evidence.

### Source and scope discipline

- The roadmap explicitly prescribes the six lesson topics and the assessment competencies below.
- The roadmap's Topic 06 says that no specific framework or reference model was originally named as a mandatory requirement. The lesson file names **TOGAF Standard, 10th Edition** and **DAMA-DMBOK** as lesson-selected examples, not as frameworks mandated by the original roadmap. Questions F6.4–F6.8 assess those examples only as covered in that lesson. Do not claim the roadmap itself required them.
- The Northbridge Bank case is fictional and illustrative, consistent with the source roadmap. Any added numbers or operational details are labelled assumptions.
- Regulatory or compliance conclusions must not be invented. Identify what evidence and accountable specialist input would be required.

## Assessment map

| Section | Lesson file | Main evidence |
|---|---|---|
| A | `01-what-data-architecture-is-and-what-data-architects-do.md` | Explanation, stakeholder table, root-cause hypotheses, decision note |
| B | `02-data-architecture-vs-data-engineering-and-solution-architecture.md` | Discipline comparison, classification, RACI, working agreement |
| C | `03-business-capabilities-domains-and-data-ownership.md` | Capability/domain map, capability–system–asset matrix, ownership register, contested ownership decisions |
| D | `04-architecture-principles-and-quality-attributes.md` | Principles, measurable quality requirements, option evaluation, exception record |
| E | `05-data-architecture-lifecycle-and-governance.md` | Lifecycle diagram, decision-rights table, review flow, decision/exception records, governance measures |
| F | `06-enterprise-data-architecture-frameworks-and-reference-models.md` | Term classification, comparison, adoption plan, deviation record |
| G | Integrated case | Current-state reasoning and a reviewable architecture decision record |

---

## Section A — Lesson 01: What Data Architecture Is and What Data Architects Do

**Lesson file:** `01-what-data-architecture-is-and-what-data-architects-do.md`

### A1. Recall and explanation

#### A1.1 — Define the discipline
- **Competency:** Definition, scope, deliverables
- **Level:** Beginner — recall/understanding
- **Task:** Define data architecture in your own words. Name at least five concerns in its scope and three things it is not identical to.
- **Expected evidence:** A concise definition and examples.
- **Scoring basis:** 0–2 points — short-answer rubric.

**Answer outline:** Data architecture concerns the organisation's data structure and how data is stored, moved, governed, and used in service of business goals. Relevant concerns include data assets, models, storage, integration, platforms, governance, quality, and security. It is not merely diagrams, a technology shopping list, individual pipeline code, or a one-time design activity.

#### A1.2 — Architect responsibilities and deliverables
- **Competency:** Role and outputs
- **Level:** Beginner — understanding
- **Task:** List five responsibilities of a Data Architect and five typical deliverables. Explain why each deliverable supports a decision or activity.
- **Expected evidence:** Responsibility/output table.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Responsibilities can include understanding business needs, defining structure and standards, making and recording decisions, reviewing designs, communicating, and aligning with governance. Deliverables may include current- and target-state views, principles, standards, reference architectures, decision records, and roadmaps. Full credit links each to an actual user or decision; merely listing document names is incomplete.

#### A1.3 — Architecture, design, documentation, review, implementation
- **Competency:** Distinguishing adjacent activities
- **Level:** Beginner/intermediate — comparison
- **Task:** Explain the difference between architecture, design, documentation, review, and implementation. Give one example where a diagram exists but the architecture decision remains unresolved.
- **Expected evidence:** Comparison table and example.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Design creates a structure; documentation records it; review assesses it; implementation builds it. Architecture is the broader set of structures, principles, decisions, and trade-offs that connect business needs to systems. A diagram without agreed requirements, alternatives, rationale, accountable decision, or implementation consequences does not establish that a sound decision was made.

#### A1.4 — Trace a business objective
- **Competency:** Objective-to-outcome traceability
- **Level:** Intermediate — application
- **Task:** Trace “reduce inconsistent customer reporting” through business requirement, data requirement, architecture decision, implementation, and measurable outcome.
- **Expected evidence:** A six-step chain with one verification method per step.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** A defensible chain might be: reports must use consistent customer counts → define “customer” and the reporting population, with owner and effective-date semantics → choose and govern a canonical definition or explicitly scoped measures → implement mappings/controls and update consumers → compare report results and definition conformance over an agreed period. A tool choice alone is not a complete chain. Targets and system details must be labelled assumptions if not supplied.

#### A1.5 — Stakeholder expectations
- **Competency:** Stakeholder analysis
- **Level:** Intermediate — artifact creation
- **Task:** Build a stakeholder table for a bank trying to reconcile customer reporting. Include executive, business owner, engineering, security/compliance, operations, and audit perspectives. For each, state a concern and acceptable evidence.
- **Expected evidence:** Table with stakeholder, concern, evidence.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Executives may require cost/risk/value evidence; business owners require correct capability definitions and accountable ownership; engineers require feasible contracts and implementation clarity; security/compliance require evidence of relevant controls and data handling; operations require supportability and recovery evidence; audit requires traceable sources, decisions, and lineage evidence. Accept equivalent stakeholder groupings if the concerns and evidence are concrete.

### A2. Scenario and root-cause analysis

#### A2.1 — Symptom versus cause
- **Competency:** Root-cause hypotheses
- **Level:** Intermediate — analysis
- **Task:** Five reports disagree on active-customer counts. List at least four plausible causes and the evidence needed to test each. Do not declare a cause without evidence.
- **Expected evidence:** Hypothesis/evidence table.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Candidates include different definitions of “active,” inconsistent as-of dates, duplicate or missing records, divergent source copies, inconsistent exclusion rules, late or failed data refreshes, and unclear ownership. Evidence could include metric definitions, SQL/report logic, source-to-report lineage, refresh timestamps, duplicate analysis, change history, and owner interviews. The symptom itself does not prove which cause is present.

#### A2.2 — New datastore request
- **Competency:** Architectural diagnosis and uncertainty
- **Level:** Intermediate — scenario
- **Task:** A product team asks for a new datastore and says “the current database is too slow.” State the first questions you would ask, what evidence you would seek, and which decisions might be local versus needing review.
- **Expected evidence:** Questions, evidence list, provisional decision boundary.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Ask what workload and users are affected, what “slow” means, measured latency and load, data sensitivity, source of truth, integration and downstream consumers, operational ownership, cost, and reversibility. Seek workload metrics, requirements, incident evidence, data flows, and current constraints. A reversible local tuning decision may be local; a new system of record, cross-domain copy, security boundary, or enterprise standard may require review. Do not assume the correct answer is “buy a new database.”

#### A2.3 — Missing lineage statement
- **Competency:** Architectural capability diagnosis
- **Level:** Intermediate — scenario
- **Task:** A regulator asks for a lineage statement, and no team can produce one. Identify the likely missing capability and propose the smallest useful first step without claiming that one document solves the whole problem.
- **Expected evidence:** Capability gap and staged first action.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Likely gaps include end-to-end lineage capture/maintenance, ownership, source inventories, documented flows, or governance for lineage. Start with a scoped inventory and trace a small set of material customer-data flows end to end, recording sources, transformations, consumers, evidence, and unknowns. Assign an owner and expand based on risk. Do not invent a regulatory interpretation or promise full lineage from a diagram alone.

#### A2.4 — Conflicting senior engineers
- **Competency:** Evidence-based decision framing
- **Level:** Advanced — evaluation
- **Task:** Two senior engineers propose conflicting designs. Provide a decision structure that avoids choosing by seniority.
- **Expected evidence:** Decision-note outline with criteria.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Define context/problem, requirements and constraints, options, decision criteria tied to business drivers/quality attributes, evidence, trade-offs, risks, recommendation, owner, and revisit trigger. Invite both engineers to provide comparable evidence. Seniority may inform experience but is not a substitute for explicit criteria.

#### A2.5 — Reversible versus costly-to-reverse decisions
- **Competency:** Uncertainty and decision timing
- **Level:** Advanced — reasoning
- **Task:** Explain how reversibility, cost of being wrong, and uncertainty affect whether to decide now, test first, or defer. Give one example of each.
- **Expected evidence:** Three examples and decision logic.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Low-cost reversible choices can often be made locally with monitoring; high-cost or irreversible choices require stronger evidence and wider review; uncertain decisions may be tested with a time-bounded pilot if delay is acceptable. Full credit explains the downside of both premature commitment and unnecessary delay.

#### A2.6 — Five architectural problems and first diagnostic questions
- **Competency:** Problem classification and stakeholder impact
- **Level:** Intermediate — analysis
- **Task:** Using the banking scenario, identify five plausible architectural problems (not five technologies to buy). For each, name the stakeholder or capability affected, the first diagnostic question, and the evidence that would help distinguish the problem from a symptom.
- **Expected evidence:** Five-row problem/stakeholder/question/evidence table.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Suitable problems include inconsistent business definitions, unclear data ownership, unmanaged copies or point-to-point integration, missing lineage, and weak quality/operational controls. For each, connect the problem to an affected stakeholder and ask a question that tests it—for example, whether “active customer” has a signed definition and effective date; who is accountable for the definition; where copies are created; which transformations feed a report; or what quality and refresh evidence exists. Other problems are acceptable when tied to evidence. Do not treat the reported disagreement as proof that all five problems exist.

### A3. Decision-note exercise

#### A3.1 — Produce a one-page decision note
- **Competency:** Defensible architecture decision
- **Level:** Advanced — artifact creation
- **Task:** Choose a problem from A2. Produce a one-page note with problem, context, constraints, at least three genuine alternatives, criteria, trade-offs, risks, recommendation, accountable owner, assumptions, and a trigger that would reverse the decision.
- **Expected evidence:** One-page decision note.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** There is no single required recommendation. Full credit requires three plausible alternatives, criteria established before scoring, explicit trade-offs and risks, fact/assumption separation, a named accountable role, and a meaningful revisit trigger. “Use technology X because it is best” is insufficient.

### A4. Industry application and completion evidence

#### A4.1 — First two weeks of a bank assessment
- **Competency:** Scope, stakeholder discovery, evidence planning
- **Level:** Industry application — planning
- **Task:** For a bank with five systems that define “active customer” differently, list the questions you would ask during the first two weeks. Group them by business meaning, systems/flows, ownership, quality, governance, and evidence.
- **Expected evidence:** Prioritised question plan and stakeholder table.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Questions should establish the intended business outcome and population; each system's definition and source; time windows and exclusions; producers/consumers; owner/steward; lineage and copies; quality/incident evidence; current standards and decision rights; relevant constraints; and unknowns. The plan should distinguish discovery from premature target-state design.

#### A4.2 — Spoken explanation
- **Competency:** Explain scope and role to a non-technical colleague
- **Level:** Beginner — communication
- **Task:** Write a 90–120 second explanation of data architecture and the Data Architect's role. It must connect business needs to decisions and implementation without describing the architect as simply the person who chooses technology.
- **Expected evidence:** Script or recording reviewed by another person.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Strong answers describe the discipline, its business purpose, responsibilities, deliverables, collaboration with engineering and solution architecture, and the role of evidence and trade-offs. Reviewer clarity matters more than jargon.

#### A4.3 — Six-sentence description of a known system
- **Competency:** Current-state description and explicit unknowns
- **Level:** Beginner — artifact creation
- **Task:** Choose a system you know and describe it in exactly six sentences: (1) what data it holds, (2) who uses it, (3) where data enters, (4) where it leaves, (5) who is accountable for the data, and (6) what you do not know. Mark uncertain claims as reported, assumed, or unknown rather than inventing facts.
- **Expected evidence:** Six-sentence system description with source/uncertainty labels.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** The six sentences must cover the six requested facets in order or with clear labels. If accountability or a flow is unknown, state that explicitly and name how it would be validated. A polished description that silently guesses the owner or source-to-consumer flow is not correct.

---

## Section B — Lesson 02: Data Architecture vs Data Engineering and Solution Architecture

**Lesson file:** `02-data-architecture-vs-data-engineering-and-solution-architecture.md`

### B1. Definitions and classification

#### B2.1 — Compare the three disciplines
- **Competency:** Purpose, scope, deliverables, accountability
- **Level:** Beginner — comparison
- **Task:** Define data architecture, data engineering, and solution architecture in one sentence each. Compare their usual scope and deliverables.
- **Expected evidence:** Comparison table.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Data architecture addresses data structure, standards, and decisions across systems/organisation; data engineering builds, operates, and improves data pipelines/platforms; solution architecture designs how a specific end-to-end solution meets a business need. These are collaborating disciplines, not a universal hierarchy. Overlap is expected.

#### B2.2 — Classify responsibilities
- **Competency:** Responsibility allocation
- **Level:** Beginner/intermediate — classification
- **Task:** For each task below, identify the lead discipline, contributors, and whether the decision may require broader review. Justify each answer:
  1. Choose a partitioning strategy for one pipeline.
  2. Define an enterprise data-sharing standard.
  3. Design the end-to-end components for a new lending capability.
  4. Agree a customer data contract used by three domains.
  5. Implement retry logic for a failed ingestion job.
  6. Decide whether a new platform introduces an enterprise-wide data copy.
  7. Define a source-to-target transformation.
  8. Select measurable freshness targets for a business-critical data product.
  9. Decide how an individual pipeline is deployed.
  10. Resolve a conflict between a local delivery deadline and a cross-domain standard.
  11. Define the logical customer/account entities and shared identifiers used by several domains.
  12. Choose partitioning and platform-retention implementation settings within an already approved policy for a shared data platform rather than one pipeline.
  13. Select a streaming technology for a bounded use case and assess whether it creates an enterprise pattern.
  14. Set an enterprise-wide retention or data-sharing standard.
  15. Define the business meaning and eligibility rules for “active customer” for a specific reporting purpose.
  16. Approve an exception to a mandatory cross-domain data standard.
  17. Implement pipeline monitoring, alerting, and retry behaviour within an approved design.
  18. Plan the end-to-end migration of a legacy source into a governed analytical platform.
  19. Operate a production pipeline and coordinate incident recovery with consumers.
  20. Set schema-evolution and backward-compatibility rules for a data contract used by multiple domains.
- **Expected evidence:** Twenty-row classification table with lead, contributors, review tier, and rationale for every task.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Typical leads: (1) data engineering, with architecture input if standards or shared constraints apply; (2) data architecture/governance authority; (3) solution architecture with data architecture and engineering contributions; (4) shared, with accountable domain/data owners and architecture guidance; (5) data engineering; (6) data architecture plus security/operations/domain input and review if cross-domain/high-risk; (7) engineering with architecture/domain input where semantics/contracts are affected; (8) business/data owner sets need with architecture/engineering/operations validating feasibility; (9) engineering/solution delivery within standards; (10) use the agreed governance/escalation path, with decision authority determined by risk and scope; (11) business/data owners own business meaning, with data architecture coordinating cross-domain semantics and solution architecture/engineering contributing implementation feasibility; (12) engineering/platform lead for local settings, with architecture/operations/security review where shared platform standards, cost, or risk are affected; (13) engineering recommends based on technical fit, while data/solution architecture assess integration, reuse, and end-to-end fit; escalate if it becomes a cross-domain standard; (14) authorised architecture/governance authority with domain, security, legal/compliance, and operations input as relevant; (15) accountable business/data owner for the stated reporting purpose, with architecture facilitating cross-system alignment and engineering implementing the rule; (16) the authority defined by the exception policy, not the requester alone; (17) data engineering/operations within agreed operational standards; (18) solution architecture coordinates end-to-end design, with data architecture on shared data/standards and engineering on migration feasibility/build; (19) operations/data engineering own execution under the support model, with domain owners and consumers involved in impact decisions; (20) contract/data owner and architecture/governance define compatibility policy, while engineering implements and tests it. These are illustrative default allocations, not universal organisational assignments. Full credit requires a defensible accountable role, relevant contributors, and a review tier justified by scope, risk, reversibility, and local authority.

#### B2.3 — Shared accountability
- **Competency:** Overlap and collaboration
- **Level:** Intermediate — explanation
- **Task:** Explain why data modeling, integration design, technology selection, and non-functional requirements can involve all three disciplines. Give an example of how to collaborate without creating duplicate approval.
- **Expected evidence:** One example per overlap or a clear combined example.
- **Scoring basis:** 0–2 points — short-answer rubric.

**Answer outline:** Each area spans different scales: enterprise semantics/standards, build feasibility/operation, and end-to-end solution fit. A joint review can clarify the concern and decision owner while each role contributes evidence. Shared contribution does not mean every participant has veto or that accountability is unassigned.

### B2. RACI and working agreement

#### B2.4 — Build a RACI-style table
- **Competency:** Decision rights
- **Level:** Intermediate — artifact creation
- **Task:** Create a RACI-style table for six decisions in a banking data programme: enterprise data-sharing standard, pipeline retry policy, customer data contract, end-to-end lending solution design, platform-wide retention standard, and one pipeline's deployment configuration. Include data architecture, data engineering, solution architecture, business/data owner, and governance authority where relevant.
- **Expected evidence:** Table and short justification.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** RACI definitions must be stated consistently. Each decision needs exactly one clearly accountable role/authority in the table; several roles may be responsible or consulted. Enterprise-wide standards usually need an authorised governance/architecture owner; implementation details may be owned locally within standards; business semantics need accountable business/data ownership. There is no universal RACI independent of organisational policy, so assumptions must be stated.

#### B2.5 — Where does a standard end and project design begin?
- **Competency:** Boundary definition
- **Level:** Intermediate — reasoning
- **Task:** Give an example of an enterprise standard and a project-specific design that implements it. Identify what the project may decide locally and what it may not silently override.
- **Expected evidence:** Paired example with boundary.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** A standard might require named ownership and documented data contracts; the project chooses the schema tooling and deployment method within that requirement. It may not silently redefine ownership or bypass a mandatory control. Exceptions require the agreed process.

#### B2.6 — Cross-team data contract
- **Competency:** Ownership and collaboration
- **Level:** Intermediate — scenario
- **Task:** Three teams consume the same customer dataset. Who should own the contract, who contributes, and what should happen when one team requests a breaking change?
- **Expected evidence:** Roles, change path, evidence.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** The accountable data/domain owner or explicitly designated contract owner owns semantics and compatibility policy; producers and consumers contribute requirements and impact analysis; engineering implements versioning/testing; architecture/governance reviews cross-domain or material changes according to local rules. Notify consumers, assess impact, define transition, and record the decision.

### B3. Advanced boundary and failure-mode scenarios

#### B2.7 — Point-to-point integration dispute
- **Competency:** Local versus enterprise optimisation
- **Level:** Advanced — scenario/evaluation
- **Task:** A solution architect proposes point-to-point integration to meet a deadline; the data architect objects because several domains will reuse the data. Who decides and on what grounds?
- **Expected evidence:** Decision path, criteria, alternatives, risk.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** The title of the person alone does not settle it. Determine decision authority from the organisation's governance model. Compare deadline, reuse, coupling, supportability, change impact, security, and lifecycle cost. Consider a bounded point-to-point integration, reusable contract/service, or staged option. Escalate if the decision creates enterprise-wide consequences or violates a standard; document any accepted debt and revisit trigger.

#### B2.8 — Reusable ingestion framework becomes a de facto standard
- **Competency:** Governance of emergent standards
- **Level:** Advanced — analysis
- **Task:** Engineers created a reusable ingestion framework now used by several teams. What should happen before it becomes a de facto enterprise standard?
- **Expected evidence:** Assessment and governance steps.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Inventory actual use and outcomes; assess reliability, security, interoperability, operability, supported patterns, ownership, versioning, and limitations; consult consumers and architecture/governance; decide whether to endorse, adapt, constrain, or replace it; publish scope and conformance expectations; assign maintenance and change authority. Popularity alone does not prove suitability.

#### B2.9 — One person wears all three hats
- **Competency:** Role ambiguity
- **Level:** Advanced — working agreement
- **Task:** A start-up has one person performing data architecture, data engineering, and solution architecture. How can it maintain sound decisions without pretending the roles are held by different people?
- **Expected evidence:** One-page working agreement or concise process.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Separate the roles in the decision record even if one person fills them; state the hat and evidence used for each judgement; identify decisions that require founder/business-owner approval or external review; define minimum standards, conflict handling, peer challenge, and a revisit trigger. Role separation is conceptual and procedural, not necessarily staffing separation.

#### B2.10 — Working agreement
- **Competency:** Collaboration and escalation
- **Level:** Industry application — artifact creation
- **Task:** Write a one-page working agreement among data architecture, data engineering, and solution architecture. Cover shared artefacts, decision ownership, local decisions, review triggers, escalation, delivery engagement, and how role boundaries are revisited.
- **Expected evidence:** Working agreement.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** A strong agreement names decision categories, accountable roles, consulted roles, evidence expected, response time or escalation route, and how disagreements are recorded. It should prevent ivory-tower architecture, architecture by committee, and unowned decisions.

#### B2.11 — Signals of a healthy boundary
- **Competency:** Evaluate operating model
- **Level:** Advanced — analysis
- **Task:** Name three signals that role boundaries are working and three signals of silo formation.
- **Expected evidence:** Indicators with interpretation.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Healthy signals may include timely decisions with an owner, reusable standards applied with sensible exceptions, joint early design engagement, and fewer late surprises. Silo signals include architecture engaged only after design, engineering bypassing standards, duplicate artefacts, unresolved decisions, or every choice escalated. Indicators must be interpreted in context; raw counts alone can mislead.

---

## Section C — Lesson 03: Business Capabilities, Domains and Data Ownership

**Lesson file:** `03-business-capabilities-domains-and-data-ownership.md`

### C1. Core concepts and mapping

#### C3.1 — Distinguish the building blocks
- **Competency:** Capabilities, processes, domains, systems, assets
- **Level:** Beginner — classification
- **Task:** Define business capability, process, domain, system, and data asset. Use “customer onboarding” to give one example of each.
- **Expected evidence:** Five definitions and examples.
- **Scoring basis:** 0–2 points — short-answer rubric.

**Answer outline:** Capability is what the organisation can do; process is how work is performed; domain is a bounded area of business knowledge/responsibility with consistent vocabulary; system is an implementation that supports activity; data asset is a meaningful dataset/entity/collection used or managed. Examples must not collapse capability into a system name.

#### C3.2 — Owner versus steward
- **Competency:** Accountability
- **Level:** Beginner — explanation
- **Task:** Distinguish data owner, data steward, producer, and consumer. Why is “the CRM team owns customer data” insufficient as an ownership statement?
- **Expected evidence:** Role table and explanation.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Owner is accountable for meaning/decisions; steward looks after definitions and quality; producer creates or supplies data; consumer uses it. “CRM team” may be a system/technical group rather than an accountable business role and may not own data across multiple systems. Name an accountable role or mark ownership unknown.

#### C3.3 — Capability-to-system-to-asset map
- **Competency:** Traceability
- **Level:** Intermediate — artifact creation
- **Task:** Build a small matrix for three capabilities (customer onboarding, account servicing, credit-risk assessment), at least three systems, and at least five data assets. Identify systems serving multiple capabilities, assets without a confirmed owner, and capability gaps.
- **Expected evidence:** Capability map/matrix plus gap notes.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** The map must start from business capabilities rather than reproduce only the system inventory. Each asset links to a domain/system where known; unknowns are explicit. Multiple systems may support a capability, and a capability with no known supporting system is a finding, not a reason to invent one.

#### C3.4 — Domain boundaries
- **Competency:** Semantic boundaries
- **Level:** Intermediate — analysis
- **Task:** Two business units use “customer” differently. Describe the evidence needed to decide whether they share one concept, use related concepts, or require distinct domain definitions.
- **Expected evidence:** Definition comparison and decision approach.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Compare scope, definition, lifecycle, identifiers, business use, ownership, legal/business meaning, and consumers. Similar labels do not prove equivalence. A reference/common model can help structure the discussion but cannot decide local semantics.

### C2. Ownership register and dependencies

#### C3.5 — Create an ownership register
- **Competency:** Ownership documentation
- **Level:** Intermediate — artifact creation
- **Task:** Create a ten-asset ownership register with fields for asset, domain, owner, steward, producers, consumers, status, and source/evidence type. At least two entries must explicitly show “unknown” or “disputed” ownership.
- **Expected evidence:** Ten rows and notes on gaps.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Every row has an owner or an explicit unknown; unknown is not silently filled with a guessed team. Producer/consumer roles are distinct from owner/steward. Sources and evidence types make the register reviewable.

#### C3.6 — Cross-domain dependencies
- **Competency:** Dependency risk
- **Level:** Intermediate — analysis
- **Task:** Identify three high-risk cross-domain dependencies in the banking scenario. Explain why each is risky and how a change should be communicated.
- **Expected evidence:** Dependency table.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Examples may include customer identity consumed by risk/marketing, account status used by finance/reporting, or transaction data consumed by fraud/risk. State assumptions, impact, owner, change notification, contract/versioning, and escalation. Risk depends on actual criticality and coupling.

#### C3.7 — Customer address entered in multiple places
- **Competency:** Contested ownership
- **Level:** Advanced — scenario
- **Task:** “Customer address” is entered during onboarding, changed in the mobile app, and corrected by operations. Who owns it?
- **Expected evidence:** Defensible ownership criteria and investigation plan.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Do not automatically assign ownership to the first system, last editor, or technical team. Determine which business role is accountable for the meaning and correctness of the address, who can authorize corrections, what types of address exist, and how source-of-authority rules work. Producers may differ from the owner. Record disputed/unknown status until confirmed.

#### C3.8 — Derived customer risk score
- **Competency:** Derived-data accountability
- **Level:** Advanced — scenario
- **Task:** A risk team creates a derived customer risk score that marketing consumes. Who is accountable, and what must be documented?
- **Expected evidence:** Ownership decision with dependencies and limitations.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** The risk domain is a plausible owner of score meaning/method, but the actual accountable role must be confirmed. Record definition, inputs, method/version, intended uses, limitations, quality expectations, producer, consumers, approval/change process, and any relevant internal restrictions. Marketing consumption does not automatically transfer ownership. Do not invent regulatory requirements.

#### C3.9 — Merger brings a different account definition
- **Competency:** Domain boundary and change
- **Level:** Advanced — scenario
- **Task:** A merger brings a second institution with a different definition of “account.” Describe how to identify and resolve the boundary issue without prematurely forcing one global definition.
- **Expected evidence:** Comparison plan and decision record outline.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Compare business semantics, lifecycle, identifiers, product/legal context, source systems, and consumers. Map equivalent, overlapping, and distinct concepts; identify translation and reporting implications; assign accountable owners; preserve differences where meaningful; record the decision and revisit trigger after integration changes.

#### C3.10 — Ownership changes after reorganisation
- **Competency:** Ownership continuity
- **Level:** Advanced — governance
- **Task:** A domain owner leaves and the organisation reorganises. What should happen to the ownership register and unresolved decisions?
- **Expected evidence:** Transition steps.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Mark the ownership as pending/unknown rather than leaving a departed person as active owner; assign an interim accountable role if authorised; notify consumers; transfer definitions, decisions, and open issues; confirm the successor; update related governance and records. Verify changes with the responsible authority.

#### C3.11 — Three contested ownership decisions
- **Competency:** Defended ownership and documentation
- **Level:** Industry application — artifact creation
- **Task:** Resolve three cases: (1) shared customer identity, (2) derived risk score, and (3) account data from a merger. For each, state evidence, ownership criteria, decision, alternatives, rationale, unresolved questions, and review trigger.
- **Expected evidence:** Three decision-log entries.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** There is no required universal owner. Full credit requires explicit criteria (who creates it, owns its meaning, bears the risk of error, and can fix it), named accountable roles or explicit unknowns, rationale, cross-domain effects, and revisitable decisions.

---

## Section D — Lesson 04: Architecture Principles and Quality Attributes

**Lesson file:** `04-architecture-principles-and-quality-attributes.md`

### D1. Principles, drivers, constraints, assumptions

#### D4.1 — Rewrite weak principles
- **Competency:** Actionable principles
- **Level:** Beginner/intermediate — artifact creation
- **Task:** Rewrite these five statements into useful principles with statement, rationale, and implications:
  1. “Use best-of-breed technology.”
  2. “Data must be good.”
  3. “Everything should be real time.”
  4. “Security is important.”
  5. “We should use a single system.”
- **Expected evidence:** Five principle records.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** A useful principle is durable, specific enough to distinguish options, has a rationale, and states implications. Possible directions: choose technology against agreed capability/operability criteria; define measurable quality checks for critical assets; use real-time processing only where freshness needs justify complexity/cost; apply controls proportionate to data sensitivity and access; identify an authoritative source for specified attributes while permitting governed replicas where justified. Alternative principles are acceptable if actionable and not disguised vendor preferences.

#### D4.2 — Distinguish driver, constraint, assumption
- **Competency:** Requirements reasoning
- **Level:** Beginner — classification
- **Task:** Classify each statement as business driver, constraint, or assumption, explaining any ambiguity:
  - “Risk reports must be available before the morning review.”
  - “The source system cannot be changed this quarter.”
  - “We believe the feed contains all transactions.”
  - “The bank wants to reduce reconciliation effort.”
  - “The existing network path must be retained.”
- **Expected evidence:** Classification and rationale.
- **Scoring basis:** 0–2 points — short-answer rubric.

**Answer outline:** Morning review availability is a requirement/driver depending on framing; source cannot change this quarter is a constraint; feed completeness is an assumption requiring validation; reducing reconciliation is a business driver; retaining the network path is a constraint if mandated, otherwise an assumption/preference to clarify. Full credit identifies ambiguity and asks what evidence or authority establishes it.

#### D4.3 — From objective to principle
- **Competency:** Business driver to architecture implication
- **Level:** Intermediate — application
- **Task:** For the objective “improve trust in customer and transaction reporting,” propose two principles and explain how each changes a design decision.
- **Expected evidence:** Two principle records.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Examples: important measures must have an agreed definition, accountable owner, and traceable lineage; critical data products must publish quality/freshness expectations and evidence. Implications should affect contracts, models, ownership, lineage, tests, or reporting rather than remain slogans.

### D2. Measurable quality requirements and evaluation

#### D4.4 — Convert vague quality claims to measures
- **Competency:** Measurable requirements
- **Level:** Intermediate — artifact creation
- **Task:** Convert these into measurable requirements: “fresh data,” “high availability,” “recover quickly,” and “good data quality.” Include target, measurement window, method, owner, and whether the value is evidence-based or an illustrative assumption.
- **Expected evidence:** Requirements table.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Each requirement needs a metric and verification method: maximum data age at a defined consumption point; availability percentage over a stated window and service boundary; recovery time and acceptable data loss; defined quality dimensions such as completeness/validity/uniqueness against an agreed population. Numeric targets cannot be invented as facts. Mark proposed numbers illustrative until validated with business, operations, and risk owners.

#### D4.5 — Six quality requirements for banking data
- **Competency:** Requirement specification
- **Level:** Industry application — artifact creation
- **Task:** Define six measurable quality-attribute requirements for customer and transaction data. Cover at least three different attributes. For each, give metric, target or “target to be agreed,” measurement method/window, owner, and evidence source.
- **Expected evidence:** Six-row table.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Possible attributes include freshness, availability, completeness, validity, reconciliation accuracy, recoverability, privacy/security, interoperability, or cost. Quality is determined by whether requirements are measurable and justified, not by the number chosen. If no target is supplied, state the gap rather than fabricate a requirement.

#### D4.6 — Evaluate two designs
- **Competency:** Evidence-based scorecard
- **Level:** Intermediate/advanced — evaluation
- **Task:** Compare two candidate designs against six requirements from D4.5. Define a consistent scoring method, provide evidence or mark it unknown, explain trade-offs, and identify what must be tested before approval.
- **Expected evidence:** Scorecard and recommendation.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Use the same criteria for both options, state weights/scale if used, separate evidence from estimates, and do not let a weighted score conceal a hard constraint. Full credit explains why the recommendation follows from business priorities and what uncertainties remain.

#### D4.7 — Real-time dashboard versus cost and complexity
- **Competency:** Attribute trade-offs
- **Level:** Advanced — scenario
- **Task:** The business requests real-time dashboards; platform engineering warns of cost and complexity. Identify competing attributes, propose at least three options, and state how to choose.
- **Expected evidence:** Options, criteria, trade-offs, validation plan.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Freshness/latency competes with cost, complexity, reliability, operability, and possibly consistency. Options may include batch with agreed freshness, micro-batch, streaming for selected events, or tiered freshness by use case. Decide from measured business need, delay consequences, volume, failure/recovery requirements, and cost evidence. Do not assume “real-time” is a precise requirement.

### D3. Principles conflict and exceptions

#### D4.8 — Single system of record exception
- **Competency:** Exception handling
- **Level:** Advanced — decision reasoning
- **Task:** A team requests an exception to a “single system of record” principle. Under what conditions might it be approved, and what must the exception record contain?
- **Expected evidence:** Conditions and record outline.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Approval requires a clear need, explicit scope, assessment of alternatives and risks, accountable owner, compensating controls, time limit or review date, and evidence that downstream consumers understand authority and conflict resolution. A second copy is not necessarily a second authority; clarify which system is authoritative for which attributes. Refuse if material risk cannot be mitigated or the request lacks a justified need.

#### D4.9 — Sensitive data copied to analytics sandbox
- **Competency:** Apply principles to a proposal
- **Level:** Industry application — analysis
- **Task:** Evaluate a proposal to copy sensitive customer data into an analytics sandbox. State which principles and quality/security concerns apply, what evidence is missing, and what alternatives you would compare.
- **Expected evidence:** Review note.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Check purpose, minimisation, access, retention, lineage, quality, auditability, approved environments, and relevant internal obligations. Compare masked/synthetic data, controlled views, restricted extracts, or a properly governed copy. Do not assert the copy is forbidden or permitted without actual policy/obligation evidence. A sound answer identifies the accountable approval path.

#### D4.10 — Principles nobody knows
- **Competency:** Principle governance
- **Level:** Advanced — root-cause analysis
- **Task:** An audit finds principles that nobody knew existed. What does this indicate, and how should the organisation respond?
- **Expected evidence:** Failure analysis and remediation.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Possible causes include poor publication/communication, no owner, no usable implications, stale principles, absent governance integration, or no conformance process. Validate which applies; review, simplify, retire, or republish principles; assign ownership; connect them to design/review workflows; and measure whether teams can apply them. Do not treat the audit finding as proof that every principle is wrong.

#### D4.11 — Resolve a principle conflict
- **Competency:** Prioritisation and defended trade-off
- **Level:** Advanced — artifact creation
- **Task:** Write a principles set of at most eight, resolve one conflict between two principles, and create one time-limited exception record. Explain which attribute dominates, for which data/use case, and why.
- **Expected evidence:** Principle set, conflict note, exception record.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Principles must have statement, rationale, and implications. The conflict resolution should be context-specific, evidence-based, and explicit about accepted risk. The exception needs owner, compensating control, expiry/review date, and a condition for refusal or reversal.

### D4. Quality-attribute vocabulary check

#### D4.12 — Distinguish the nine prescribed quality attributes
- **Competency:** Quality-attribute definitions and business-context application
- **Level:** Beginner/intermediate — classification and application
- **Task:** For each attribute—reliability, availability, scalability, performance, security, privacy, interoperability, maintainability, and cost efficiency—write a concise definition and one banking-data example. For at least four attributes, identify a plausible measurable indicator and explain why the indicator alone may not prove the business outcome.
- **Expected evidence:** Nine-row attribute/definition/example table, with four indicator notes.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Reliability concerns correct, dependable operation; availability concerns whether a service is usable when required; scalability concerns handling growth in load/data/users; performance concerns response time/throughput/resource behaviour; security concerns protecting systems/data from unauthorised access or change; privacy concerns appropriate handling of personal information and its uses; interoperability concerns exchanging and interpreting data across systems; maintainability concerns ability to understand, change, test, and operate the solution; cost efficiency concerns achieving required outcomes at justified lifecycle cost. Examples and metrics must fit the stated use case. Availability is not the same as correctness, throughput is not the same as latency, security is not interchangeable with privacy, and a metric such as uptime alone does not establish end-to-end data quality or business fitness.

---

## Section E — Lesson 05: Data Architecture Lifecycle and Governance

**Lesson file:** `05-data-architecture-lifecycle-and-governance.md`

### E1. Lifecycle and governance basics

#### E5.1 — Name lifecycle stages and artefacts
- **Competency:** Lifecycle understanding
- **Level:** Beginner — recall/application
- **Task:** List the seven lifecycle stages prescribed by the roadmap and name at least one output/artefact for each.
- **Expected evidence:** Stage-to-artefact table.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Discover/assess current state; analyse requirements; design target state; evaluate/approve; implement/align; operate/monitor; change/improve. Plausible outputs include scope/inventory, requirements, target view/options, decision record/approval, implementation/conformance evidence, monitoring findings, and change/lessons learned. Artefacts should be matched to stages and the sequence should include feedback.

#### E5.2 — Standard, policy, guideline
- **Competency:** Governance vocabulary
- **Level:** Beginner — comparison
- **Task:** Distinguish a standard, policy, and guideline. Explain mandatory versus advisory status and how a team can tell which applies.
- **Expected evidence:** Definitions and example.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** A policy states direction/required outcomes at a governing level; a standard specifies agreed requirements or rules; a guideline provides advice. Organisations may define these terms differently, so the local authority and document status must be checked. State scope, owner, approval status, mandatory/advisory status, and conformance method.

#### E5.3 — Why record decisions?
- **Competency:** Decision traceability
- **Level:** Beginner/intermediate — explanation
- **Task:** Explain why a material architecture decision needs a record. Name the minimum information that lets a future reviewer understand and challenge it. Explain why an exception record complements but does not replace the architecture decision record.
- **Expected evidence:** ADR-versus-exception comparison table and minimum-field list.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** An architecture decision record preserves context, options, criteria, rationale, trade-offs, risks, assumptions, decision owner/date, consequences, and revisit triggers. An exception record separately identifies the rule/principle being violated, scope, justification, risk, compensating controls, approving authority, owner, expiry/review trigger, remediation, and conformance evidence. The exception record does not replace the underlying decision record because the two answer different questions. Keep both lightweight enough to maintain.

### E2. Decision rights and review flow

#### E5.4 — Three-tier decision model
- **Competency:** Decision rights
- **Level:** Intermediate — artifact creation
- **Task:** Define a local/reviewed/escalated decision model with at least two examples per tier. State the risk/scope/reversibility criteria used to classify decisions.
- **Expected evidence:** Decision-tier table.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Local: low-risk, reversible, within existing standards and a team's authority. Reviewed: affects a shared platform, data contract, or several consumers. Escalated: high-risk, irreversible, enterprise-wide, contested, or outside approved standards. Exact thresholds are organisation-specific; define authority and rationale rather than relying on vague labels.

#### E5.5 — Architecture review process
- **Competency:** Review mechanics
- **Level:** Intermediate — process design
- **Task:** Design a review flow from submission to outcome. Include entry information, criteria, and the distinct outcomes approve, approve with conditions, reject, defer, return for revision, and escalate; also cover conditions, decision record, implementation conformance, and the change/review loop.
- **Expected evidence:** Flow diagram or numbered flow.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Submission and completeness check → classify risk/scope → evaluate against principles and quality requirements → record approve / approve with conditions / reject / defer / return for revision / escalate, distinguishing decision outcomes from routing actions → communicate owner/actions → implementation conformance check → monitor drift and feed lessons into standards. A review process should not be just an approval meeting.

#### E5.6 — Which changes require review?
- **Competency:** Proportional governance
- **Level:** Intermediate — classification
- **Task:** Classify these changes as local, reviewed, or escalated under a clearly stated policy: rename a local staging column; change a shared customer contract; introduce a new cross-domain copy of sensitive data; change a low-risk reversible job schedule; introduce an enterprise-wide storage standard.
- **Expected evidence:** Five-row classification table with rationale and assumptions.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Local column rename may be local if consumers/contracts are unaffected; shared contract change needs review; sensitive cross-domain copy may require escalated/security/governance review; local schedule change may be local if service targets are unaffected; enterprise-wide standard is escalated/authorised. Classification depends on actual impact, policy, and authority; note missing facts rather than pretending labels are universal.

#### E5.7 — Decision-rights table
- **Competency:** Explicit accountability
- **Level:** Intermediate — artifact creation
- **Task:** Create a decision-rights table for a bank's data programme. For each decision class, name the proposer, contributors/reviewers, accountable decision authority/approver, implementer, verifier, required evidence, outcome record, and escalation route.
- **Expected evidence:** Table and review-flow diagram.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Every decision class has a clear proposer, contributors/reviewers, one accountable decision authority, implementer, and verifier, with entry criteria, required evidence, response path, and record. Roles may overlap in a small organisation, but the hats and any independent challenge needed for high-risk decisions must remain explicit. Do not assign every decision to a central committee; preserve local autonomy for low-risk decisions and escalate material ones.

### E3. Conformance, exceptions, and measures

#### E5.8 — Conformance and drift
- **Competency:** Implementation conformance
- **Level:** Intermediate/advanced — explanation
- **Task:** Explain how an implemented system is checked against an approved design and how drift is detected. Give three evidence sources.
- **Expected evidence:** Control/measurement plan.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Compare implementation/configuration/data flows to approved views, standards, contracts, and decision conditions; use code/configuration review, platform metadata, tests, inventories, operational monitoring, or periodic review as appropriate. Record findings, owners, severity, and corrective action. Approval alone does not prove implementation conformance.

#### E5.9 — Design five governance measures
- **Competency:** Governance measurement
- **Level:** Advanced — artifact creation
- **Task:** Choose five measures from the roadmap and describe how to collect and interpret them: review turnaround time, proportion of changes reviewed, exception counts and age, conformance findings, and delivery-team feedback.
- **Expected evidence:** Five-row measures table.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Define each metric's numerator/denominator, start/end event, time window, source, owner, segmentation, and interpretation. Example: review turnaround from complete submission to decision; segment by risk tier and exclude/flag incomplete submissions consistently. Exception counts need age and category; raw counts can rise because reporting improved. Feedback should be collected consistently and triangulated with delivery and quality evidence.

#### E5.10 — Review queues take six weeks
- **Competency:** Diagnose governance bottlenecks
- **Level:** Advanced — scenario
- **Task:** Review queues take six weeks. Identify likely causes, what evidence would distinguish them, and at least three fixes with measures.
- **Expected evidence:** Root-cause table and improvement plan.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Possible causes include unclear entry criteria, unnecessary reviews, centralised authority, incomplete submissions, insufficient reviewers, meeting cadence, repeated debate due to missing records, and no service target. Inspect wait time versus active review time, queue by tier, rework, submission completeness, and review capacity. Fixes might include risk-tier routing, delegated local authority, published criteria/templates, time-bound escalation, office hours, and removal of redundant gates. Measure turnaround and conformance rather than simply reducing reviews.

#### E5.11 — Ten exceptions to the same standard
- **Competency:** Continuous improvement
- **Level:** Advanced — scenario
- **Task:** Ten exceptions to the same standard have been approved. What should change?
- **Expected evidence:** Diagnosis and governance response.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Repeated exceptions may indicate the standard is unrealistic, obsolete, poorly communicated, or mismatched to common contexts; alternatively, the same risk may be repeatedly accepted without control. Categorise reasons, risk, age, outcomes, and owners; assess whether to revise/retire the standard, add a supported pattern, change implementation, or refuse future exceptions. Update principles based on evidence and set a review trigger.

#### E5.12 — Team ships then asks approval
- **Competency:** Governance failure analysis
- **Level:** Advanced — scenario
- **Task:** A team ships first and asks for architecture approval afterward. What might this indicate, and how do you respond?
- **Expected evidence:** Causes, proportionate response, prevention.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Possible causes include late architecture engagement, slow review, unclear decision rights, incentives, or deliberate bypass. Establish facts and risk first; avoid assuming intent. Assess the implementation, document decision and any exception, remediate material risks, clarify the review trigger, and improve early engagement/turnaround. Do not retroactively rubber-stamp a design merely because it is live.

#### E5.13 — Bank review process including regulator-driven change
- **Competency:** Governance design
- **Level:** Industry application — artifact creation
- **Task:** Design an architecture review process for a bank's data programme that can handle regulator-driven change. Include intake, validated obligation/requirement, impact analysis, decision rights, review outcomes, implementation conformance, escalation, and feedback. Do not invent the content of any regulation.
- **Expected evidence:** Process flow, decision-rights table, decision-record fields.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Record the source and accountable interpretation of the requirement; map affected data, systems, domains, controls, and deadlines; classify risk and urgency; assign decision authority; record approve/conditions/reject/defer and rationale; track implementation evidence; review conformance and lessons. Escalation and time limits should be explicit. A framework is not a substitute for validating the actual obligation.

#### E5.14 — Critique governance with measures
- **Competency:** Evidence-based process evaluation
- **Level:** Advanced — evaluation
- **Task:** Given a process with late engagement, six-week reviews, stale standards, and recurring exceptions, identify three failure modes and propose improvements with measures.
- **Expected evidence:** Three findings, actions, and metrics.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Likely failure modes include gatekeeping/queueing, late engagement, unmaintained or uncheckable standards, and failure to learn from exceptions. Improvements should target causes and specify indicators such as turnaround by tier, percentage of material changes reviewed early, exception age/repetition, conformance findings, and delivery-team feedback.

#### E5.15 — From current state to target state and roadmap
- **Competency:** Gap analysis and lifecycle traceability
- **Level:** Intermediate — analysis and artifact creation
- **Task:** For one new data source, state the evidence needed to describe the current state, the decisions and requirements needed to define a target state, and how the gap becomes a prioritised roadmap. Identify the outputs at each step and distinguish verified current-state findings from proposed future-state choices. Explain what should trigger reassessment if a new requirement invalidates an earlier assumption or approved decision.
- **Expected evidence:** Current/target/gap/roadmap table with evidence labels and dependencies.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Current-state inputs include source/system inventory, existing flows/contracts, owners, quality/operational evidence, constraints, and known gaps. Target-state inputs include business outcomes, measurable requirements, principles, risk, dependencies, options, and decision authority. The gap should state what is missing or must change, why it matters, dependencies, sequencing, owner, and validation measure. A target design is a proposal, not a current-state fact; a roadmap should be prioritised by value, risk, dependency, and feasibility rather than by technology novelty alone. If a new requirement invalidates an assumption, reopen the affected requirement/decision, assess impact and urgency, record the change and authority, update target/gap/roadmap artefacts, and verify implementation consequences rather than silently continuing under the old decision.

---

## Section F — Lesson 06: Enterprise Data Architecture Frameworks and Reference Models

**Lesson file:** `06-enterprise-data-architecture-frameworks-and-reference-models.md`

### Source note for Section F

The source roadmap says no specific framework or reference model was originally prescribed by name. The lesson file introduces **TOGAF Standard, 10th Edition** and **DAMA-DMBOK 2nd Edition (2024 Revised Edition)** as selected teaching examples and links to primary publisher/owner pages. Questions below test the distinctions and evaluation method required by the roadmap; F6.4–F6.8 test accurate understanding of the lesson's named examples without recasting them as source-mandated.

### F1. Terminology and scope

#### F6.1 — Classify ten architecture artefacts
- **Competency:** Framework/reference terminology
- **Level:** Beginner — classification and justification
- **Task:** Define and distinguish framework, reference model, reference architecture, standard, and implementation blueprint. State which categories are generally more abstract and which are more implementation-specific, and explain why a single universal ordering is approximate. Then classify each of these ten described artefacts and justify the classification by purpose and authority, not just its title:
  1. A documented method that structures architecture work through concerns, views, and decision activities.
  2. An abstract model of party, account, and transaction concepts and their relationships.
  3. A reusable analytical-platform pattern for a class of data workloads.
  4. An internally approved rule requiring specified sensitive-data fields to be encrypted at rest.
  5. A concrete deployment design for one customer-analytics platform, including selected services and network settings.
  6. A catalogue of stakeholder concerns, viewpoints, architecture views, and governance stages.
  7. A shared vocabulary model relating business capabilities, domains, and data entities.
  8. A reusable event-ingestion pattern covering validation, replay, and error handling.
  9. An organisation-approved naming and schema-compatibility rule with a defined scope and conformance check.
  10. A project-specific implementation plan that names the chosen runtime, schemas, access configuration, and rollout sequence for one risk-scoring solution.
- **Expected evidence:** Ten-row classification table with artefact type, purpose, authority/status, rationale, and any ambiguity.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Likely primary classifications are: (1) framework; (2) reference model; (3) reference architecture; (4) standard because an authorised organisation has made it mandatory within a scope; (5) implementation blueprint; (6) framework or framework artefact depending on whether it is the method itself or a deliverable within one—explain the distinction; (7) reference model; (8) reference architecture; (9) standard; (10) implementation blueprint. A framework/reference model is generally more abstract than a project-specific implementation blueprint, but “abstractness” and “mandatory authority” are different dimensions, so no single ordering applies cleanly to all five categories. Titles do not determine category: a reference architecture can be adopted as an internal standard by an authorised governance decision, but that changes its local authority/status, not the original document's nature everywhere. Accept another classification for deliberately mixed examples only if the learner identifies the mixed roles and explains the evidence needed to disambiguate them.

#### F6.2 — Stakeholder, concern, viewpoint, view
- **Competency:** View vocabulary
- **Level:** Beginner — explanation
- **Task:** Define stakeholder, concern, viewpoint, and view. Give one operations view and one executive view for the same data platform.
- **Expected evidence:** Definitions and two examples.
- **Scoring basis:** 0–2 points — short-answer rubric.

**Answer outline:** A stakeholder has an interest; a concern is an issue important to them; a viewpoint specifies how to construct a representation for concerns; a view is the actual representation. Operations may need dependencies, alerts, recovery, and ownership; executives may need capability, investment, value, and risk. The views can differ while describing the same architecture.

#### F6.3 — Can a reference architecture become a standard?
- **Competency:** Purpose versus authority
- **Level:** Intermediate — reasoning
- **Task:** Explain when a reference architecture could be treated as an internal standard and why that does not make every published reference architecture mandatory.
- **Expected evidence:** Short explanation and example.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** An organisation can formally adopt some/all of a reference architecture as mandatory within a defined scope through its own authority and governance. The original reference remains guidance unless its status is changed by a valid authority or other applicable requirement. State scope, owner, approval status, and conformance mechanism.

#### F6.4 — TOGAF example
- **Competency:** Purpose and limitations of named lesson example
- **Level:** Intermediate — explanation
- **Task:** According to the lesson's primary-source-checked overview, what problem does the TOGAF Standard help structure? Explain two things it does not decide automatically for a bank.
- **Expected evidence:** Purpose, two limitations, source link.
- **Scoring basis:** 0–2 points — short-answer rubric.

**Answer outline:** TOGAF is an enterprise architecture standard/framework and method for structuring architecture development and practice; the ADM is a relevant method. It does not automatically determine the bank's business strategy, customer definitions, technology choice, data ownership, quality targets, or compliance. Use the exact primary sources linked in the lesson for identity/scope claims; local decisions require evidence and accountability.

#### F6.5 — DAMA-DMBOK example
- **Competency:** Purpose and limitations of named lesson example
- **Level:** Intermediate — explanation
- **Task:** Explain what DAMA-DMBOK provides and why it should not be treated as a physical data platform blueprint.
- **Expected evidence:** Short explanation.
- **Scoring basis:** 0–2 points — short-answer rubric.

**Answer outline:** It is a structured body of knowledge for data management that helps organise data-management concepts and practices. It does not by itself specify the bank's chosen cloud services, schemas, deployment sequence, or owner for each local asset. The organisation must map relevant knowledge areas to local roles, requirements, controls, and artefacts.

#### F6.6 — Complementary versus interchangeable
- **Competency:** Compare scope accurately
- **Level:** Intermediate — comparison
- **Task:** Explain why TOGAF and DAMA-DMBOK are not interchangeable, and describe a plausible reason to use one, both, or neither.
- **Expected evidence:** Comparison and conditional recommendation.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** They serve different primary purposes: enterprise architecture development/practice versus data-management knowledge. A bank may use a tailored architecture method and a data-management reference if both address actual gaps; use only one if only one need exists; use existing local practice if it already works and alternatives add no value. Do not compare unlike tools as if they solved exactly the same problem.

### F2. Evaluation and adaptation

#### F6.7 — Apply the seven evaluation criteria
- **Competency:** Framework selection
- **Level:** Intermediate — evaluation
- **Task:** Define and apply the roadmap's seven criteria: fit to problem, effort to adopt, skills required, flexibility, evidence of use, compatibility with existing practices, and regulatory alignment. State evidence you would collect for each.
- **Expected evidence:** Seven-row matrix.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Strong answers ask what business problem is addressed, estimate training/maintenance effort, inspect skills, test tailoring, seek credible use evidence, map existing practices/artefacts, and validate actual obligations with accountable specialists. Regulatory alignment is not a compliance guarantee. Scorecard values should be explained and caveated.

#### F6.8 — Interpret a comparison matrix
- **Competency:** Fair comparison and scorecard limits
- **Level:** Advanced — evaluation
- **Task:** The lesson's illustrative matrix gives TOGAF 3.45 and DAMA-DMBOK 3.40 for a combined mid-sized-bank need. Explain why this does not mean the options are equivalent or establish an objective ranking. Identify at least three limitations and one hard constraint that should not be hidden in a weighted score.
- **Expected evidence:** Critique of the matrix.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** The candidates have different purposes; scores/weights are illustrative assumptions; evidence is not independently measured; context and priorities affect weights; a weighted total can hide a disqualifying constraint. Examples of hard constraints include a mandatory internal process, lack of essential skills without a feasible plan, or inability to meet a required control. Do not present the scores as industry rankings.

#### F6.9 — Adopt, adapt, defer, ignore
- **Competency:** Tailored adoption plan
- **Level:** Advanced — artifact creation
- **Task:** For a mid-sized bank with limited architecture staff, propose at least one item to adopt, adapt, defer, and ignore from a candidate approach. For each, explain the need, rationale, owner, and evidence that would change the decision.
- **Expected evidence:** Adoption plan.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** There is no single required selection. Full credit maps each item to a real gap, preserves traceability to source concepts, identifies ownership and effort, and specifies measures/revisit triggers. “Adopt everything” without context is weak.

#### F6.10 — Copying a reference architecture
- **Competency:** Validate assumptions and deviations
- **Level:** Advanced — scenario
- **Task:** A team copies a published analytical data platform reference architecture without validating its assumptions. Identify the checks needed before adoption and provide three examples of justified deviations.
- **Expected evidence:** Assumption checklist and deviation list.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Check problem scope, volume/velocity, source capabilities, latency, data sensitivity, lineage, quality, operations, skills, legacy constraints, costs, and recovery needs. Deviations might include reusing an existing governed landing zone, using batch where measured freshness permits, or retaining a legacy interface during a phased migration. Each must preserve required outcomes or state the risk accepted and its controls.

#### F6.11 — Terminology mapping
- **Competency:** Adapt without semantic loss
- **Level:** Advanced — artifact creation
- **Task:** Two units use different terms for customer and account concepts. Design a mapping table that prevents false equivalence and shows how the organisation can adopt useful reference-model language without renaming every system.
- **Expected evidence:** Term mapping with equivalence status and owner.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Include source term/definition, local term/definition, equivalent/partial/distinct status, owner, affected artefacts, decision, and review trigger. Preserve genuine semantic differences; a reference model cannot decide local business meaning.

#### F6.12 — “Full framework compliance”
- **Competency:** Scope and adoption governance
- **Level:** Advanced — scenario
- **Task:** Leadership demands “full framework compliance” without naming the version, scope, intended outcome, or decision authority. What do you ask, and what do you propose?
- **Expected evidence:** Clarifying questions and a pilot/adoption approach.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Ask which framework/version/components, why, what business outcome, what current practice already meets the intent, what effort and skills are available, who approves adaptation, and how success is measured. Propose a time-bounded gap assessment/pilot with a minimum viable scope, measures, and an adoption decision. Do not promise compliance before scope is defined.

#### F6.13 — Reference architecture is too heavy
- **Competency:** Evidence-based adaptation
- **Level:** Advanced — scenario
- **Task:** A delivery team says the reference architecture is too heavy. How do you evaluate that claim?
- **Expected evidence:** Decision process and required evidence.
- **Scoring basis:** 0–4 points — scenario/analysis rubric.

**Answer outline:** Ask which components are challenged and what purpose each serves; compare requirements and local constraints; evaluate simpler alternatives and operational/control consequences; test assumptions; document deviations, risks, mitigations, authority, and revisit triggers. Neither copying everything nor removing components to meet a deadline is sufficient reasoning.

#### F6.14 — Adoption recommendation by organisation type
- **Competency:** Context-sensitive adaptation
- **Level:** Industry application — comparison
- **Task:** Explain how your recommendation would change for (a) a mid-sized bank with limited architecture staff, (b) a large regulated group, and (c) a start-up.
- **Expected evidence:** Three-column comparison.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** Mid-sized bank: small, useful subset and data-management coverage reference; large group: potentially more formal views, traceability, and federated decision paths; start-up: minimal principles, views, and decision records. These are tendencies, not rules. Specific risk and actual obligations can override size-based assumptions.

#### F6.15 — Deviation record
- **Competency:** Traceability of adaptation
- **Level:** Industry application — artifact creation
- **Task:** Complete a deviation record for a real or illustrative reference-architecture component. Include source/version, intended purpose, local evidence, alternatives, rationale, risks, compensating controls, decision authority, validation evidence, and review triggers.
- **Expected evidence:** Completed deviation record.
- **Scoring basis:** 0–10 points — artifact-production rubric.

**Answer outline:** The record must explain the reference's intent and why local conditions justify the deviation. It must not treat a written rationale as proof that the alternative is safe; evidence/testing is required. If assumptions fail, the record should trigger review.

---

## Section G — Integrated Final Assessment: Northbridge Bank

### G1. Case background

**The source roadmap's fictional scenario:** Northbridge Bank is a fictional mid-sized retail and business bank. Over fifteen years it has accumulated a core banking system, a separate cards platform, a CRM, a loan origination system, an enterprise data warehouse, a data lake created three years ago, and team-built reporting databases and spreadsheets. Risk, finance, marketing, and compliance report different customer counts. A regulator has asked for clearer evidence of where customer data comes from and who is accountable for it.

The roadmap also requires the learner to address a bank whose five systems use different definitions of **“active customer.”** Treat this as a related case condition: the exact five systems and their definitions are not enumerated by the roadmap.

**Illustrative assumptions added solely to make the assessment solvable:**
- The five systems with different active-customer definitions are assumed to include core banking, cards, CRM, loan origination, and the warehouse/reporting layer. This mapping is hypothetical and must be validated in a real assessment.
- The bank has not yet supplied authoritative definitions, data-flow evidence, quality targets, or a confirmed ownership register.
- The delivery deadline, costs, volumes, latency targets, platform capabilities, and specific regulatory obligation are unknown unless the learner explicitly labels a proposed value as an assumption.
- No framework is mandatory based on the original roadmap. The lesson file discusses TOGAF Standard, 10th Edition and DAMA-DMBOK as selected examples, not source-prescribed requirements.

### G2. Your role and task

You are the Data Architect coordinating an initial current-state assessment. The goal is to produce a trustworthy baseline and a defensible next decision—not to design a full target platform or claim compliance before the facts are known.

Complete the tasks below. You may recommend different outcomes from the model outline if your reasoning is evidence-based and traceable.

#### G7.1 — Problem statement and concerns
- **Competencies:** A1, D1
- **Level:** Industry application — analysis
- **Task:** Write a business problem statement and identify at least six architecture concerns. Separate observed facts from assumptions and unknowns.
- **Expected evidence:** Problem statement and concern/evidence table.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** The business problem is inconsistent customer reporting and inadequate traceability/accountability across a fragmented data landscape, with a regulator asking for clearer evidence. Source facts include the listed system types, different reported customer counts, and the request for lineage/accountability. Unknowns include definitions, flow details, actual data quality, owners, obligation scope, targets, and causes. Concerns may include semantics, ownership, lineage, quality, duplication, access/sensitivity, operational support, governance, and delivery cost. Do not claim that inconsistent reports prove a single root cause.

#### G7.2 — Stakeholders and evidence
- **Competencies:** A1, E1
- **Level:** Industry application — artifact creation
- **Task:** Build a stakeholder table covering head of data, retail/lending/cards domain owners, risk, finance, marketing, compliance, security, engineering, operations, and internal audit. State each concern and acceptable evidence.
- **Expected evidence:** Stakeholder expectation table.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** Business owners need definitions and accountability; risk/finance/marketing need metric semantics and reliable outputs; compliance needs validated obligation and traceable evidence; security needs access/data-handling evidence; engineering needs contracts, flows, and feasible changes; operations needs ownership, supportability, and recovery; audit needs evidence provenance and decision records. The head of data sponsors scope and decisions under the actual governance model. Avoid assuming a stakeholder has approval authority solely from job title.

#### G7.3 — Discipline boundaries
- **Competencies:** B1, B2
- **Level:** Industry application — classification
- **Task:** Allocate responsibilities for (a) defining active-customer semantics, (b) mapping source flows, (c) building transformation pipelines, (d) designing a reporting solution, (e) approving an enterprise data-sharing standard, and (f) operating the pipeline. State accountable role, contributors, and review triggers.
- **Expected evidence:** RACI-style table.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** Business/data owner should be accountable for business meaning; data architecture coordinates cross-system semantics, standards, and architecture decisions; engineering builds/operates pipelines; solution architecture designs the end-to-end reporting solution. Exact authority must follow the bank's decision model. Shared contributions are appropriate; no decision should be left without one accountable role.

#### G7.4 — Capability, domain, system, asset map
- **Competencies:** C1, C2
- **Level:** Industry application — artifact creation
- **Task:** Create a capability-to-system-to-asset map for customer onboarding, account servicing, card services, lending, risk assessment, finance reporting, and customer analytics. Identify at least five assets and three cross-domain dependencies.
- **Expected evidence:** Capability/domain map and matrix.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** The matrix should connect capabilities to relevant systems and assets such as customer identity/profile, account, card, loan, transaction, and active-customer measure. Exact system-to-asset links are assumptions until verified. Cross-domain dependencies may include customer identity used by lending/risk, transaction data used by risk/finance, and customer status used by marketing/reporting. Mark missing links and uncertain mappings explicitly.

#### G7.5 — Ownership and stewardship
- **Competencies:** C3
- **Level:** Industry application — artifact creation
- **Task:** Create an ownership register for at least eight assets. Include domain, owner, steward, producers, consumers, status, source/evidence type, and unresolved questions. At least two entries must show unknown or disputed ownership.
- **Expected evidence:** Register and three contested-ownership decision notes.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** Every entry has a confirmed accountable role or explicit unknown/disputed status. System teams are not automatically data owners. Customer identity, active-customer definition, and derived risk score may have different owners or owners that need confirmation. State who creates data, owns its meaning, bears the risk of error, and can correct it. Record producer/consumer dependencies.

#### G7.6 — Root-cause hypotheses
- **Competencies:** A2
- **Level:** Advanced — analysis
- **Task:** List five plausible reasons for inconsistent active-customer counts. For each, identify the evidence needed and how you would avoid treating a hypothesis as fact.
- **Expected evidence:** Hypothesis/evidence table.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** Different eligibility definitions, different time windows, source-system population differences, stale refreshes, duplicate/missing records, conflicting identifiers, and inconsistent exclusions are plausible. Evidence includes metric logic, business definitions, data samples, lineage, refresh metadata, reconciliation, and stakeholder validation. Use Observed/Reported/Assumed/Unverified labels and keep unresolved hypotheses open.

#### G7.7 — Principles and quality requirements
- **Competencies:** D1, D2
- **Level:** Industry application — artifact creation
- **Task:** Propose no more than eight actionable principles and six measurable quality requirements for the case. Clearly mark illustrative targets and explain how each would be measured.
- **Expected evidence:** Principles set and quality-requirements table.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** Principles may require named ownership for material assets, explicit definitions for shared metrics, traceable lineage for critical outputs, and documented exceptions. Quality requirements should specify metric, target/window, measurement method, owner, and evidence source. If no target is known, write “to be agreed” rather than inventing a fact. Prioritise attributes according to business use and risk.

#### G7.8 — Compare architecture alternatives
- **Competencies:** A3, D3
- **Level:** Advanced — decision analysis
- **Task:** Compare at least three approaches for reconciling active-customer reporting:
  1. Correct each report locally and retain separate definitions.
  2. Establish a governed common definition for a specified enterprise use while documenting legitimate domain-specific definitions.
  3. Build a centralised customer/metrics service or curated data product to publish governed definitions and outputs.

  You may add another option. Compare against semantic correctness, traceability, implementation effort, change impact, operational risk, and time to value. State assumptions and recommend a next step.
- **Expected evidence:** Options matrix and recommendation.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** No option is universally best. Local fixes may be fast but preserve inconsistency and repeated effort; a governed shared definition improves comparability but requires semantic ownership and careful scope; a central service/product may improve reuse and traceability but costs more and risks becoming a bottleneck or false source of truth if semantics are unresolved. A sensible first step is often to inventory definitions, establish owners, trace critical reports, and agree on the specific business question before choosing implementation. Full credit requires comparing genuine alternatives and identifying the evidence needed to decide.

#### G7.9 — Decision note
- **Competencies:** A3, D3
- **Level:** Advanced — artifact creation
- **Task:** Produce a concise architecture decision record for the next action you recommend. Include problem/context, options, criteria, decision, rationale, consequences, risks, assumptions, accountable owner, and revisit trigger.
- **Expected evidence:** Reviewable decision record.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** A defensible near-term decision could be to run a scoped, evidence-based assessment and define the active-customer metric before selecting a new platform. Another recommendation may earn full credit if it addresses the problem and evidence. The record should not claim that a technology platform resolves semantic ownership by itself.

#### G7.10 — Lifecycle and governance
- **Competencies:** E1, E2, E3
- **Level:** Industry application — process design
- **Task:** Map the recommended work to the seven architecture lifecycle stages. Define a local/reviewed/escalated decision model, review outcomes, conformance checks, exception handling, and five governance measures.
- **Expected evidence:** Lifecycle diagram, decision-rights table, review flow, measures list.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** Show discover/current-state assessment → requirements → target/option design → evaluate/approve → implement/align → operate/monitor → change/improve. Include feedback loops. Use local decisions for low-risk reversible changes, review for shared/cross-domain impacts, and escalation for high-risk/irreversible/enterprise-wide choices. Measures should define collection and interpretation, not just list metric names.

#### G7.11 — Framework or reference model relevance
- **Competencies:** F1, F2
- **Level:** Advanced — evaluation
- **Task:** Decide whether a framework or reference model would help this assessment. You may use the lesson's TOGAF and DAMA-DMBOK examples, another verified candidate, existing local practice, or no new framework. Explain fit, effort, skills, flexibility, evidence of use, compatibility, and regulatory alignment.
- **Expected evidence:** Evaluation matrix and adopt/adapt/defer/ignore plan.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** TOGAF may help structure architecture work and views; DAMA-DMBOK may help check data-management coverage and vocabulary. Either may be unnecessary if existing practices already support the needed decisions. Use the seven criteria, identify evidence gaps, and avoid claims of mandatory adoption or compliance. The source roadmap does not mandate specific names.

#### G7.12 — Current-state inventory evidence discipline
- **Competencies:** Module-wide project requirements
- **Level:** Industry application — artifact review
- **Task:** Design a current-state inventory plan using the roadmap's evidence labels: Observed, Reported, Assumed, and Unverified/Unknown. Include scope, stakeholder/system inventory, capability/domain inventory, data assets/ownership, data flows, principles/governance, quality assessment, gaps/risks, validation, and prioritised next steps.
- **Expected evidence:** Inventory plan mapped to the project's D1–D10 deliverables.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** Define scope and exclusions first; gather dated sources and stakeholder input; map capabilities/domains before systems; link assets and owners; trace flows including manual spreadsheets; record principles and whether they are practised; assess qualities against targets or mark “no target/no evidence”; link risks to findings; validate disagreements; and prioritise recommendations. Do not design the target state within the current-state inventory project.

#### G7.13 — Executive readout
- **Competencies:** A1, G2
- **Level:** Industry application — communication
- **Task:** Write a one-page executive summary of the assessment, including scope, top findings, top risks, recommended next steps, caveats, and open questions. Ensure a non-specialist can read it in about ten minutes.
- **Expected evidence:** One-page summary.
- **Scoring basis:** 0–4 points — integrated case rubric in Section G3.

**Model answer outline:** The summary must separate facts from assumptions, explain why findings matter to business outcomes, prioritise only a few actions, and trace recommendations to evidence. State scope limits and unknowns. Avoid technology catalogue language or unsupported compliance claims.

### G3. Integrated case scoring rubric

Score each G7 task on a 0–4 scale:

| Score | Standard |
|---:|---|
| 0 | Missing, irrelevant, or based on unsupported claims |
| 1 | Some relevant terminology, but major omissions or confused concepts |
| 2 | Partly correct; basic analysis present but weak evidence, traceability, or trade-off reasoning |
| 3 | Complete and defensible; facts/assumptions separated; options and ownership clear; material risks addressed |
| 4 | Review-ready; precise, traceable, evidence-led, explicit about uncertainty and alternatives, with useful measures and revisit triggers |

For the 13 tasks, the maximum is 52 points. **Recommended assessment-design threshold:** at least 39/52 (75%), with no score below 2 on G7.3, G7.5, G7.8, G7.9, G7.10, or G7.12. This is a recommended rubric threshold, not a threshold mandated by the roadmap. A reviewer may require revision regardless of total score if the evidence or accountability is inadequate.

**Critical errors requiring correction even if the score is high:**
- presenting assumptions as observed facts;
- leaving a material decision without an accountable role;
- assigning data ownership to a system/team without evidence of accountability;
- choosing an architecture alternative without criteria or meaningful trade-offs;
- claiming compliance or a framework mandate without a supported source;
- omitting the rationale, risk, owner, or revisit trigger from a material decision;
- designing a target state while presenting the work as a current-state inventory.

---

## Scoring method, partial credit, and critical errors

### Deterministic scoring rule for every question

Use the question's **Expected evidence** to select one scoring basis. Each question is scored once; do not double-count the same evidence across categories.

1. **Artifact-production submission — 0–10 points.** Use this when the expected evidence is a reviewable output such as a table, map, matrix, register, decision note, record, plan, diagram, flow, scorecard, agreement, or structured summary. If a question requests several related pieces as one submission, score the bundle once against the five dimensions below. The integrated G7 tasks use their separate 0–4 rubric instead.
2. **Scenario, analysis, evaluation, or decision reasoning without a distinct artifact — 0–4 points.** Use the scenario rubric below.
3. **Short answer, definition, explanation, or classification without a distinct artifact — 0–2 points.** Use the short-answer rubric below.

If a task could fit more than one category, use the highest-complexity category only when the stated expected evidence actually requires it: artifact first, then scenario/analysis, then short answer. Do not award full credit for terminology alone.

### Short-answer questions — 0–2 points
- **0:** incorrect, missing, or unrelated;
- **1:** partly correct but missing a material distinction, rationale, or limitation;
- **2:** correct, clear, and appropriately scoped.

### Scenario and analysis questions — 0–4 points
- **0:** unsupported conclusion or no answer;
- **1:** identifies a relevant concept but misses the decision problem;
- **2:** reasonable analysis with important omissions or assumptions left implicit;
- **3:** defensible reasoning, evidence needs, options/roles, and trade-offs;
- **4:** review-ready answer with traceability, uncertainty handling, consequences, and revisit triggers.

### Artifact-production questions — 0–10 points
- **Completeness (0–2):** all required fields/components are present.
- **Accuracy (0–2):** definitions, roles, and relationships are correct.
- **Traceability (0–2):** sources, assumptions, requirements, and decisions link together.
- **Clarity (0–2):** a reviewer can understand the artifact and use it.
- **Decision quality (0–2):** options, criteria, trade-offs, risk, owner, and revisit conditions are defensible.

Award partial credit for sound, explicit alternatives; do not require the exact model answer if another option is justified. For each lesson section, calculate the maximum by adding the scoring basis assigned to each question; calculate the achieved percentage as earned points divided by that section's maximum. The overall percentage is total earned points divided by the sum of all question maxima, multiplied by 100. The integrated G7 tasks retain their explicit 52-point maximum and are included once in the overall denominator.

### Question counts and maximum points

| Section | Questions | Maximum points |
|---|---:|---:|
| A — Lesson 01 | 15 | 118 |
| B — Lesson 02 | 11 | 72 |
| C — Lesson 03 | 11 | 84 |
| D — Lesson 04 | 12 | 106 |
| E — Lesson 05 | 15 | 126 |
| F — Lesson 06 | 15 | 90 |
| G — Integrated case | 13 | 52 |
| **Total** | **92** | **648** |

These maxima follow the per-question scoring basis shown beside each question. Section G is scored on its dedicated 13 × 4 rubric (52 points). Use the formula above for section and overall percentages; the 75%/85% bands below remain recommended assessment-design interpretations, not roadmap-mandated thresholds.

### Critical-error rule

A critical error is not merely a different architectural preference. It is a failure of evidence, accountability, or core concept—for example, inventing an owner, claiming compliance without evidence, or treating a reference architecture as mandatory without authority. Mark the relevant question **“not yet mastered”**, explain the issue, and require correction and re-attempt even if the numeric score would otherwise pass.

### Overall recommended interpretation

The following are assessment-design recommendations, not source-mandated numerical thresholds:
- **85–100%:** strong current evidence of module competence; still complete the project gate and peer challenge.
- **75–84%:** provisional pass; correct weak answers and re-attempt critical topics.
- **Below 75%:** revisit the indicated lessons and re-attempt.
- **Any critical error:** correct it before claiming mastery.

Do not use the overall percentage to bypass an unmet lesson completion gate or the current-state inventory project gate.

---

## Self-assessment and remediation guide

After marking answers, record the competency, error type, lesson to revisit, correction, and re-attempt date.

| Observed weakness | Revisit lesson | What to do before re-attempt |
|---|---|---|
| Defines architecture as diagrams or technology selection | `01-what-data-architecture-is-and-what-data-architects-do.md` | Restate the discipline, trace business objective to outcome, rewrite a decision note |
| Cannot distinguish symptoms from root causes | Lesson 01 | Build a hypothesis/evidence table and label unknowns |
| Confuses data architecture, engineering, and solution architecture | `02-data-architecture-vs-data-engineering-and-solution-architecture.md` | Reclassify tasks and complete a RACI with no unassigned accountable role |
| Assigns ownership to a system or fails to distinguish owner/steward | `03-business-capabilities-domains-and-data-ownership.md` | Build capability–system–asset map and mark unknown ownership explicitly |
| Forces one definition despite different business meanings | Lesson 03 | Compare definitions and record equivalent/overlapping/distinct status |
| Writes slogans instead of actionable principles | `04-architecture-principles-and-quality-attributes.md` | Rewrite five weak principles with rationale and implications |
| Lists quality attributes without measures | Lesson 04 | Define target, measurement window/method, owner, and evidence basis |
| Cannot defend trade-offs or exception decisions | Lesson 04 | Score two options and complete an exception record with review date |
| Confuses lifecycle with approval gates only | `05-data-architecture-lifecycle-and-governance.md` | Draw all seven stages with artefacts and feedback |
| Governance decisions have no owner or reviews are all centralised | Lesson 05 | Build a local/reviewed/escalated model and review flow |
| Cannot interpret governance metrics or recurring exceptions | Lesson 05 | Define five measures and diagnose a six-week queue / repeated exceptions |
| Confuses framework, reference model, reference architecture, standard, or blueprint | `06-enterprise-data-architecture-frameworks-and-reference-models.md` | Reclassify ten artefacts and explain authority versus purpose |
| Treats framework scores as objective rankings or claims compliance | Lesson 06 | Rebuild a weighted matrix with assumptions, evidence, hard constraints, and limitations |
| Copies a reference architecture without documenting deviations | Lesson 06 | Complete a deviation record and identify revisit triggers |
| Invents facts or cannot connect findings to recommendations | Current-state project in `Projects/01-current-state-data-architecture-inventory.md` | Label Observed/Reported/Assumed/Unverified; trace each risk and recommendation to evidence |
| Good terminology but weak practical decisions | Lessons 01–06, especially decision exercises | Rework the integrated case and ask a reviewer to challenge the rationale |

### Remediation loop

1. Identify the failed competency rather than rereading the whole module automatically.
2. Revisit the exact lesson section and redo the related artifact from a blank page.
3. Compare it with the answer outline and note the missing reasoning.
4. Re-attempt the question closed-book after several days.
5. Ask a reviewer to challenge the decision or artifact.
6. Log the corrected answer and any unresolved question for Module 2D.2.

---

## Module mastery checklist

The module roadmap requires evidence, not self-reported confidence. Check an item only when its evidence exists and has been reviewed.

- [ ] I can explain data architecture and the Data Architect's responsibilities; my explanation and Topic 01 decision note have been reviewed.
- [ ] I can distinguish data architecture, data engineering, and solution architecture; the comparison table and RACI have no unassigned decision.
- [ ] I can identify business capabilities, domains, and data ownership; the capability map, ownership register, and decision log are complete.
- [ ] I can define and apply principles and quality attributes; the principles set, measurable targets, trade-off analysis, and exception record are complete.
- [ ] I can explain the lifecycle and governance process; the lifecycle diagram, decision-rights table, record template, and governance critique are complete.
- [ ] I can evaluate and adapt frameworks/reference models; the comparison, adoption plan, and deviation record are complete.
- [ ] I can defend architecture decisions with evidence and explicit trade-offs; at least two written decision notes have survived a reviewer's challenge.
- [ ] I have completed the current-state data architecture inventory project deliverables D1–D10, validation log, and a short presentation to a reviewer.
- [ ] I answered every practice question, corrected every wrong answer, and re-attempted it after a delay.
- [ ] I have logged open questions for Module 2D.2.

## Module completion gate

The module is complete only when **all** of the following are true:

- [ ] All six topic completion gates are signed off.
- [ ] `practice-questions.md` has been answered; every wrong answer has been corrected and re-attempted.
- [ ] The current-state inventory project completion gate in `Projects/01-current-state-data-architecture-inventory.md` is met, including D1–D10, evidence labels, traceability checks, validation log, and final summary.
- [ ] The project has been presented and a reviewer has challenged it; responses do not introduce unsupported claims.
- [ ] Open questions are logged for the next module, `02-Requirements-Constraints-and-Architecture-Decisions/`.

**Final standard:** understanding means you can define and distinguish the concepts. Mastery means you can apply them to an ambiguous organisation, gather evidence, identify unknowns, make and defend decisions, record trade-offs, produce reviewable artifacts, and change your recommendation when the evidence changes.
