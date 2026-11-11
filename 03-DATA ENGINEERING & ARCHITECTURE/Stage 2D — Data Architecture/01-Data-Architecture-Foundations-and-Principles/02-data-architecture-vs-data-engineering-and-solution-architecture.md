# Data Architecture vs Data Engineering and Solution Architecture

> **Stage:** Stage 2D — Data Architecture  
> **Module:** 01 — Data Architecture Foundations and Principles  
> **Lesson:** 02  
> **Filename:** `02-data-architecture-vs-data-engineering-and-solution-architecture.md`  
> **Prerequisites:** Lesson 01, [*What data architecture is and what data architects do*](01-what-data-architecture-is-and-what-data-architects-do.md); practical data engineering experience  
> **Purpose:** Learn to allocate decisions clearly across three collaborating disciplines without creating silos or leaving decisions ownerless.

---

## 1. Learning objective

By the end of this lesson, you should be able to distinguish the **purpose, scope, authority, deliverables, and accountability** of:

- **Data architecture:** structure, standards, and decisions for data across systems and the organisation.
- **Data engineering:** building, operating, and improving data pipelines and data platforms.
- **Solution architecture:** designing how a specific solution, end to end across components, meets a defined business need.

You will practise assigning who **decides**, who is **accountable**, who must be **consulted**, who **approves** where a formal control requires approval, and who is **informed**. You will also learn how the three disciplines collaborate across requirements, design, review, implementation, operations, and change.

The objective is not to establish a universal hierarchy. It is to make each decision explicit, place it with the role that has suitable information and accountability, and escalate only when the decision crosses agreed risk or organisational boundaries.

### Evidence of learning

You should be able to produce and explain:

1. A comparison table of the three disciplines.
2. A classification of twenty representative tasks, including tasks that require collaboration.
3. A RACI-style table covering six realistic decisions with no unassigned decision.
4. A one-page working agreement that a delivery team could actually follow.
5. Answers to the Topic 02 section of [`practice-questions.md`](practice-questions.md).

---

## 2. Why this topic matters in real-world Data Architecture

Most architecture friction is **boundary friction**. It appears when two teams believe they own the same decision, nobody believes they own it, or a role imposes constraints without understanding delivery realities.

For example, a solution architect may choose a direct connection between a customer-onboarding application and a risk platform to meet a launch date. The design may work for that release but create a new dependency that every later consumer must manage. A data architect may identify the cross-system consequences, while data engineers assess the implementation and operational cost. The best outcome comes from a timely, evidence-based decision—not from automatically letting one title overrule the others.

### What boundary friction costs

| Failure | Immediate effect | Possible organisational consequence |
|---|---|---|
| Two roles independently decide the same thing | Conflicting designs or repeated work | Delay, rework, unclear accountability |
| Nobody owns a decision | Work stalls or defaults silently | Unmanaged risk and late escalation |
| Architecture prescribes implementation details without need | Engineers lose flexibility | Slower delivery and brittle designs |
| Engineers bypass a relevant shared standard | Local progress appears faster | Integration inconsistency and duplicated controls |
| A solution is optimised only for one project | Local requirements are met | Enterprise costs or dependencies increase |
| A committee must approve every small choice | Decisions queue for review | Delivery becomes slow without proportional risk reduction |

### Core principle

**A role boundary is a decision rule, not a wall.** The data architect should not dictate every implementation detail; the data engineer should not silently establish enterprise-wide standards through a local implementation; and the solution architect should not optimise a single solution while ignoring material cross-system consequences.

Use role boundaries to clarify decisions, not to prevent collaboration.

---

## 3. Prerequisite knowledge

The roadmap specifies **Module 1 (role and scope)** and **practical data engineering experience** as prerequisites.

You should already be able to:

- Explain, at a basic level, what data architecture is and what a Data Architect does.
- Read a simple data-flow diagram.
- Recognise a pipeline, a data platform, and an end-to-end application solution.
- Describe a business need in plain language.
- Write a short structured explanation of a decision.

You do **not** need to have held any of these job titles. You can use a system you have built, studied, or encountered in a case study.

### Vocabulary used in this lesson

| Term | Meaning in this lesson |
|---|---|
| Decision owner | The role authorised to make a specific decision within an agreed boundary |
| Accountable | The role answerable for the decision or outcome; in the RACI tables below, exactly one `A` is assigned per decision |
| Responsible | The role that performs the work or produces the decision input |
| Consulted | A role whose input is requested before the decision is finalised |
| Informed | A role that receives the decision or status; it does not have a veto merely because it is informed |
| Approver | A role that must formally approve under a policy, delegated authority, or control; approval is not automatically the same as designing the solution |
| Escalation | Moving a decision to a higher or cross-functional authority because it exceeds the agreed local boundary |

**Important:** Organisations use titles and governance structures differently. The allocation examples in this lesson are a defensible starting model, not a claim that every organisation must use identical job titles. Adapt the model to documented authority, regulation, and actual accountability.

---

## 4. Beginner-level learning sequence

### 4.1 Define the three disciplines

#### Data architecture

**What it is:** The structure, standards, and decisions for data across systems and the organisation.

**Why it matters:** Data is created and consumed by multiple teams. Without shared decisions about meaning, interfaces, ownership, and constraints, each team can build something locally reasonable that does not work well as part of the whole.

**How it works:** A Data Architect understands business needs and current systems, identifies cross-system implications, defines or adapts standards, compares architectural options, records decisions, and reviews designs against agreed principles and requirements.

**Typical decisions:** What constitutes an enterprise data-sharing contract? Which data definitions must be consistent across consumers? What cross-system pattern is acceptable? Which exceptions require review?

**Typical deliverables:** Architecture principles, standards, current-state and target-state views, reference architectures, decision records, cross-system models, and architecture roadmaps.

**When it is especially useful:** When a decision affects several systems, domains, teams, consumers, or long-lived enterprise constraints.

**Trade-offs and failure modes:** A cross-system view adds coordination cost. If it becomes too prescriptive, it slows delivery; if it is only aspirational, teams may ignore it. Architecture must be proportionate to impact and grounded in evidence.

**Example:** Five systems define “active customer” differently. The data architect coordinates the decision about whether a shared definition is needed, where it applies, who owns it, and how consumers discover the meaning. The architect does not independently invent the business definition.

#### Data engineering

**What it is:** Building, operating, and improving data pipelines and data platforms.

**Why it matters:** Architectural intentions have no operational value unless data can be ingested, validated, transformed, served, monitored, and recovered reliably.

**How it works:** Data engineers implement ingestion and transformation, define pipeline behaviour, test data quality, manage retries and failures, instrument operations, and improve performance and maintainability. They provide evidence about feasibility, complexity, and operating cost to architecture decisions.

**Typical decisions:** How should a pipeline handle retries? What tests detect malformed records? How should a job be partitioned within platform constraints? How should an ingestion component expose operational metrics?

**Typical deliverables:** Running pipelines, transformations, data-platform components, tests, deployment configuration, operational dashboards, runbooks, and implementation documentation.

**When it is especially useful:** When a decision concerns the reliable construction and operation of data movement or data processing, within agreed architectural boundaries.

**Trade-offs and failure modes:** Engineering optimises for feasibility, correctness, operability, and delivery. If a team makes cross-system choices without checking shared constraints, a locally sound implementation can become an enterprise problem. Conversely, architecture that ignores engineering evidence can prescribe an infeasible design.

**Example:** A data engineer implements deduplication and retry handling for onboarding events, then reports the actual delivery guarantees and failure modes so the risk-platform design can rely on them accurately.

#### Solution architecture

**What it is:** Designing how a specific solution, end to end across components, meets a defined business need.

**Why it matters:** A business outcome usually requires multiple components to work together—not merely a data pipeline. A solution view makes interfaces, dependencies, user journeys, operational responsibilities, and non-functional needs coherent for a particular initiative.

**How it works:** A Solution Architect translates the business need into a solution structure, identifies components and interactions, compares implementation approaches, and coordinates relevant specialists. The role connects the particular solution to shared standards and constraints.

**Typical decisions:** Which components participate in customer onboarding? Where should validation occur in this solution? How does the application interact with a risk platform? What is the end-to-end failure response?

**Typical deliverables:** Solution context and component diagrams, integration views, interface decisions, solution design documents, and end-to-end non-functional requirement mappings.

**When it is especially useful:** When delivering a bounded product, business capability, or change that spans application, data, and platform components.

**Trade-offs and failure modes:** The solution architect must keep the solution coherent and deliverable. Optimising only for one release can create avoidable enterprise dependencies; trying to settle every enterprise-wide concern inside a single project can also make the design unnecessarily heavy.

**Example:** For customer onboarding, the solution architect maps the onboarding application, identity checks, customer records, event publication, and risk platform into one end-to-end flow. Cross-system data contracts and shared standards are handled with the relevant owners.

### 4.2 Compare scope, decisions, deliverables, and accountability

| Dimension | Data architecture | Data engineering | Solution architecture |
|---|---|---|---|
| Primary purpose | Keep data structures, standards, and cross-system decisions coherent | Build and operate data pipelines and platforms | Make one defined solution work end to end |
| Typical scope | Cross-system, cross-team, domain, or enterprise | Pipeline, data product implementation, platform component, operational workflow | A product, initiative, or bounded business solution |
| Typical decisions | Shared data contracts, enterprise standards, cross-system patterns, exceptions | Transformation logic, pipeline reliability, tests, implementation details within constraints | Component interactions, end-to-end flow, solution-level integration choices |
| Typical deliverables | Principles, standards, architecture views, reference patterns, decision records | Code, pipelines, tests, deployment assets, runbooks, operational evidence | Solution design, component/interface views, end-to-end decision record |
| Main accountability | Coherence and defensibility of data-related decisions within delegated authority | Correct, reliable, maintainable implementation and operation | Coherent solution meeting its agreed business and non-functional needs |
| Evidence emphasised | Cross-system impact, definitions, standards, dependencies, risk | Feasibility, test results, operational metrics, failure behaviour, cost | End-to-end requirements, interface behaviour, component fit, user/business outcome |
| Typical boundary | Should not prescribe unnecessary code-level details | Should not silently define enterprise-wide standards through local code | Should not treat a local deadline as permission to ignore material shared constraints |

No row means that a discipline works alone. The table identifies the **primary lens** through which each role contributes.

### 4.3 A simple decision rule

Ask three questions:

1. **Does the decision establish or change a shared data rule across systems or teams?** Data architecture should lead or coordinate the cross-system decision.
2. **Does it determine how a data pipeline or platform component is built and operated within agreed boundaries?** Data engineering should normally lead.
3. **Does it determine how components combine to meet one solution's end-to-end need?** Solution architecture should normally lead.

If more than one answer is yes, identify the **decision being made** more precisely. A single meeting may contain several decisions with different owners. For example, selecting an event format, implementing a retry policy, and deciding the overall onboarding flow are related but not identical decisions.

**Worked example — partitioning scheme versus enterprise data-sharing standard**

- A pipeline partitioning scheme, within an agreed platform and data contract, is normally a data-engineering decision. Engineers have the operational evidence and are accountable for implementation.
- An enterprise data-sharing standard is normally a data-architecture decision because it affects multiple producers and consumers.
- If partitioning changes the contract or has material cross-platform implications, the engineer brings the decision to the appropriate architecture boundary rather than deciding unilaterally.

### 4.4 Why this is not a strict hierarchy

The disciplines have different scopes and accountabilities. A Data Architect does not automatically outrank a Data Engineer on every implementation choice; a Data Engineer does not automatically own shared enterprise standards; and a Solution Architect does not automatically own every cross-system data decision.

A useful model is **bounded authority plus collaboration**:

```text
Business need and constraints
            |
            v
  Solution architecture ------------------+
  (end-to-end solution)                    |
            |                              |
            v                              v
  Data architecture <--------------> Data engineering
  (shared data decisions)            (build and operate)
            |                              |
            +------------+-----------------+
                         v
             Reviewed implementation
             and measured outcome
```

The arrows represent collaboration, not a reporting hierarchy. The exact decision owner depends on the question, the impact, and the organisation's delegated authority.

### 4.5 Exercise: classify twenty representative tasks

For each task, choose the **primary** discipline and mark where consultation or collaboration is required. The answers below are model allocations; they should be adapted if an organisation has formally assigned a different decision authority.

| # | Task | Primary discipline | Collaboration and reasoning |
|---:|---|---|---|
| 1 | Define a shared enterprise standard for customer identifiers | Data architecture | Data engineering validates implementability; solution architecture checks impact on the solution |
| 2 | Implement a retry policy for a failed ingestion job | Data engineering | Consult platform operations and solution architecture if retries affect end-to-end latency or duplicate side effects |
| 3 | Draw the end-to-end component view for a new onboarding capability | Solution architecture | Data architecture reviews shared data flows; engineering validates feasibility |
| 4 | Decide whether several domains need a common definition for a shared data element | Data architecture coordinates the cross-domain decision; the designated business/data owner is accountable for the business meaning | Business/data owners establish meaning; engineering and solution teams assess consequences |
| 5 | Add unit and data-quality tests to a transformation | Data engineering | Consult consumers on expected semantics and failure handling |
| 6 | Decide how the onboarding application, identity service, and risk platform interact | Solution architecture | Data architecture reviews data contracts; engineering reviews integration feasibility |
| 7 | Publish an organisation-wide data-sharing principle | Data architecture | Consult business, security, engineering, and solution architecture; approval follows governance policy |
| 8 | Tune a pipeline's batch size based on measured throughput | Data engineering | Escalate if it changes service commitments, platform boundaries, or shared costs materially |
| 9 | Decide where a solution performs a user-facing validation step | Solution architecture | Engineers and business representatives confirm feasibility and user impact |
| 10 | Create a reusable ingestion component and its tests | Data engineering | Architecture consultation is appropriate if it is intended to become a shared standard |
| 11 | Coordinate and obtain approval for an exception to a cross-system data standard | Data architecture coordinates the assessment; the formally delegated exception authority makes the approval decision | Engineering supplies impact evidence; solution architecture explains the solution need; the exception approver is explicit |
| 12 | Design a solution-level response when the risk platform is unavailable | Solution architecture | Engineering defines actual retry/recovery behaviour; architecture checks shared data implications |
| 13 | Implement schema validation for incoming onboarding events | Data engineering | The schema owner and data architect clarify contract rules |
| 14 | Define the cross-team data contract's compatibility and versioning rules for an agreed business meaning | Data architecture coordinates cross-system contract rules; the business/data owner remains accountable for meaning | Producer and consumer engineers co-design the contract; the business/data owner confirms the agreed semantics |
| 15 | Select a streaming technology for a particular pipeline within an approved platform boundary | Data engineering | Consult solution architecture on end-to-end needs and data architecture on cross-system standards; escalate if the choice creates a new enterprise standard or material lock-in |
| 16 | Decide whether a new datastore creates a duplicate source of truth across domains | Data architecture | Solution architecture explains the need; engineers provide migration, replication, and operational evidence |
| 17 | Implement monitoring and alerting for pipeline failures | Data engineering | Solution operations define response needs; architects review only material service or shared-control implications |
| 18 | Compare an end-to-end solution against business requirements and quality attributes | Solution architecture | Engineering supplies measured evidence; data architecture checks cross-system principles |
| 19 | Decide whether a reusable ingestion framework should become an organisational default | Data architecture coordinates; the formally delegated platform/architecture authority owns the final organisation-wide adoption decision unless authority is explicitly delegated to the Data Architect | Engineering supplies adoption and operating evidence; solution teams supply use cases; governance defines exception handling |
| 20 | Change a shared customer event contract in a way that affects several consuming teams | Data architecture | Producers and consumers jointly assess compatibility; solution architecture maps end-to-end impact; engineers plan implementation |

**How to use the exercise:** Do not grade yourself only on whether your label matches the model answer. Explain the boundary. A strong answer identifies the decision's scope, the evidence needed, who is accountable, and what condition would trigger escalation. If a task combines two decisions, split it instead of forcing one role to own everything.

---

## 5. Intermediate-level learning sequence

### 5.1 Decision ownership: decide, contribute, approve, inform

A useful decision process separates four questions:

- **Who owns the decision?** One named role is accountable for bringing it to a defensible conclusion.
- **Who contributes?** Responsible and consulted roles supply evidence, constraints, and implementation knowledge.
- **Who must approve?** A formal policy or delegated authority may require an approval. This is a distinct control and should be explicit.
- **Who needs to know?** Informed parties need the outcome and its implications, not necessarily a vote.

This prevents a common mistake: treating attendance at a meeting as shared accountability. Several people may contribute, but if all are equally accountable for the final decision, it may be unclear who must resolve a disagreement.

### 5.2 RACI-style definitions

| Letter | Meaning | Practical test |
|---|---|---|
| **R — Responsible** | Performs the work or produces the analysis | Who creates the artefact, tests the option, or executes the action? |
| **A — Accountable** | Answerable for the decision/outcome | Who makes sure the decision is made and defensible? |
| **C — Consulted** | Provides input before the decision is final | Whose knowledge or constraints must be considered? |
| **I — Informed** | Receives the decision or progress | Who needs to know but does not need to shape the decision directly? |

This lesson uses one `A` per decision. For an ordinary delegated decision, the `A` should be the role with authority to settle it within the stated boundary. A formal approver may be recorded separately when approval is a control over a recommendation; if the approver actually holds the final decision authority, make that authority explicit and do not imply that the recommending role can overrule it. If governance genuinely assigns collective accountability, document the policy and decision mechanism rather than listing several unexplained `A` roles. For composite decisions, split business meaning, technical contract rules, implementation, and formal risk/exception approval into linked decisions when their authority differs.

### 5.3 Six-decision RACI-style table

**Scenario context:** A hypothetical bank is delivering customer onboarding that supplies data to a risk platform. The role assignments below are illustrative. “Data owner” means the business role accountable for the meaning and use of a data asset; it is not automatically identical to any of the three architecture/engineering roles.

| Decision | A — Accountable decision role | R — Responsible work | C — Consulted | I — Informed | Formal approver / final authority, if separate |
|---|---|---|---|---|---|
| 1. Establish the technical contract, compatibility rules, and versioning approach for an agreed onboarding-to-risk data meaning | Data Architect, within delegated architecture authority | Data engineering representatives draft and validate the contract and compatibility tests | Solution Architect, customer data owner, risk representative, security/compliance where relevant | Affected consumer teams and operations | None assumed; verify policy. If a separate approver has final decision authority, replace A with that authority |
| 2. Choose the pipeline's retry, deduplication, and dead-letter handling within approved constraints | Data Engineering Lead | Data engineers implement and test | Solution Architect, platform operations, Data Architect if shared contract semantics are affected | Product owner and dependent consumers | None assumed; verify policy. If a separate approver has final decision authority, replace A with that authority |
| 3. Choose the end-to-end interaction among onboarding, identity checks, and the risk platform | Solution Architect | Solution and integration engineers produce the design | Data Architect, Data Engineering Lead, security, operations, business owner | Delivery teams and affected stakeholders | None assumed; verify policy. If a separate approver has final decision authority, replace A with that authority |
| 4. Select a pipeline partitioning strategy within the approved platform boundary | Data Engineering Lead | Data engineers benchmark and implement | Platform specialist, Solution Architect if latency is affected | Data Architect and operations | None assumed; verify policy. If a separate approver has final decision authority, replace A with that authority |
| 5. Approve a time-limited exception to an enterprise data-sharing standard | Named delegated exception authority; insert the actual role/body specified by organisational governance | Data Architect prepares the impact assessment and record | Data Engineering Lead, Solution Architect, relevant data owner, security/compliance as applicable | Affected teams and architecture governance | Same delegated authority as A; approval is the decision control, not a separate second decision |
| 6. Decide whether a successful local ingestion framework becomes an organisation-wide default | Delegated platform/architecture authority; the Data Architect coordinates the recommendation unless explicitly delegated final authority | Data Architect prepares the assessment; data engineering supplies adoption, reliability, and operating evidence | Solution Architects, platform operations, security, representative consuming teams | Affected engineering teams | The delegated platform/architecture authority (same as A) if formal approval is required |

**Why the assignments differ:** The accountable role follows the precise decision boundary and the organisation's delegated authority. Data architecture leads technical cross-system contract rules, while the designated business/data owner remains accountable for the meaning of the data; these are related but distinct decisions. Retry behaviour and partitioning are implementation/operational decisions, so engineering leads them within constraints. End-to-end component interactions belong to solution architecture. For an organisation-wide default, the delegated platform/architecture authority is accountable for the adoption decision unless that authority has explicitly delegated the final decision to the Data Architect; the Data Architect coordinates the recommendation and engineering supplies evidence. The formal-approver column records required approval separately. An exception approval belongs to the authority explicitly delegated by governance; a role must not be shown as the approver merely because it prepared the assessment.

### 5.4 Collaboration across the delivery lifecycle

| Lifecycle point | Data architecture contribution | Data engineering contribution | Solution architecture contribution | Useful shared artefact |
|---|---|---|---|---|
| Requirements | Identify cross-system data needs and shared constraints | Estimate feasibility and operational implications | Translate the business need into an end-to-end solution requirement | Requirements and constraints summary |
| Design | Define or interpret shared standards and data contracts | Design pipeline/platform implementation within boundaries | Connect components and interfaces into a coherent solution | Architecture views and contract draft |
| Review | Assess cross-system impact and standards | Validate feasibility, failure handling, and operability | Check end-to-end fit and requirement coverage | Review comments and decision record |
| Implementation | Clarify intent and resolve material architecture questions | Build, test, deploy, and instrument data components | Coordinate solution integration and component fit | Implementation plan and interface specifications |
| Operations | Review recurring cross-system issues and exceptions | Monitor, troubleshoot, and improve pipeline/platform reliability | Coordinate end-to-end service behaviour and incident dependencies | Runbooks, dashboards, incident review |
| Change | Assess shared impact and standards/contract compatibility | Implement compatible changes and migrations | Assess solution-level impact and rollout sequence | Change proposal, compatibility plan, decision log |

This table is a collaboration model, not a rule that every role must attend every activity. Involve roles when the decision affects their scope or accountability.

### 5.5 Overlap areas: clarify the decision inside the topic

#### Data modeling

A data model may have both enterprise and implementation concerns. Data architecture can lead shared semantics and cross-domain consistency; solution architecture maps the model to the needs of a specific solution; data engineering implements tables, schemas, transformations, and constraints. The model's intended audience and impact determine the lead.

**Failure mode:** “The architect owns all data modeling” is too broad. It may turn a shared vocabulary decision into micromanagement of table implementation. The opposite claim—“the table is code, so only engineering decides”—can ignore consumers and shared semantics.

#### Integration design

Solution architecture normally leads the end-to-end interaction of components. Data architecture addresses shared data contracts, cross-system integration standards, and broader duplication or coupling concerns. Data engineering implements and operates data movement.

**Failure mode:** A point-to-point link is approved because it is simple for one release, without asking whether it creates repeated dependencies, inconsistent transformations, or unclear ownership.

#### Technology selection

A technology decision is not assigned by product category alone. Ask whether it is a local implementation choice, a solution-level component choice, or an enterprise-wide platform/standard decision. Engineers usually lead technical evaluation for a pipeline; solution architecture evaluates end-to-end fit; data architecture is involved when the choice changes cross-system patterns, data contracts, governance, or long-term shared constraints.

**Failure mode:** The architect chooses a product because it is fashionable, or engineers standardise a tool through repeated local adoption without a transparent decision.

#### Non-functional requirements

Performance, reliability, security, privacy, maintainability, and cost affect all three disciplines. Solution architecture coordinates end-to-end requirements; engineering provides measured component behaviour and implements controls; data architecture addresses cross-system implications and consistent data-related standards. The business or designated risk owner may set priorities or accept residual risk under governance.

**Failure mode:** “The platform is fast” is accepted as proof of end-to-end latency. Component metrics do not automatically demonstrate the complete solution meets its service target.

#### Standards

A shared standard should have an owner, rationale, scope, and a way to request exceptions. Data architecture typically coordinates data standards; engineering contributes operational evidence and reusable implementations; solution architecture ensures a particular solution can comply or documents its conflict. Formal approval follows the organisation's delegated governance process.

**Failure mode:** Standards exist in documents but are not discoverable, testable, or maintained. Alternatively, every project creates a new “standard” with no cross-team review.

### 5.6 Three recurring conflicts and how to resolve them

#### Conflict A: Architecture specifies too much detail

**Symptom:** A design mandates class names, internal function structure, or a specific implementation technique even though the architecture requirement can be met in several ways.

**Why it matters:** The team loses engineering autonomy, and the design may become stale as implementation evidence changes.

**Resolution:** Ask which requirement or risk demands the prescription. If the choice is local, reversible, and inside approved boundaries, leave it to engineering. Retain architectural constraints where interoperability, risk, compliance, or long-term cross-system impact justifies them.

**Useful evidence:** A named requirement, an interface contract, a measurable quality target, or a documented risk—not “architecture prefers it.”

#### Conflict B: Engineers bypass standards

**Symptom:** A team implements a new schema or integration pattern without checking a relevant shared standard.

**Why it matters:** Consumers may need special-case handling; controls and definitions can diverge; later reuse becomes harder.

**Resolution:** First determine whether the standard is applicable, current, and proportionate. If it is, identify the conflict and seek a timely decision or exception. If the standard is impractical, use the evidence to improve it. Do not assume every deviation is malicious or every standard is correct.

**Useful evidence:** The applicable standard, affected consumers, compatibility analysis, operational consequences, and an explicit exception owner if needed.

#### Conflict C: Solution architecture optimises locally

**Symptom:** A solution chooses a fast direct integration because it meets its own deadline, while imposing cost or coupling on other teams.

**Why it matters:** Local delivery success may create enterprise-wide maintenance, security, duplication, or change costs.

**Resolution:** Compare options against both the solution's deadline and the wider impact. A local exception may be justified, but record the scope, compensating controls, owner, expiry/revisit trigger, and cost of later removal.

**Useful evidence:** Number of affected consumers, expected changes, delivery time, operating cost, failure modes, and reversibility.

### 5.7 Intermediate exercise: establish decision rights

For the onboarding-to-risk scenario:

1. List six decisions that must be made.
2. Assign one accountable role to each decision.
3. List the evidence required from other roles.
4. Identify any formal approver separately from the decision owner.
5. State who must be informed and when.
6. Review the table for two failure conditions:
   - A decision has no accountable role.
   - Two roles both believe they can make the final decision without a defined tie-breaker.

**Ability to demonstrate:** Allocate roles consistently and explain why the decision belongs at that boundary.

---

## 6. Advanced-level learning sequence

### 6.1 Decide at the lowest level with adequate information and accountability

The lowest appropriate level is the team or role closest to the work **that also has the authority and accountability to accept the consequences**. Proximity alone is insufficient: a team may understand its pipeline deeply but not be authorised to redefine a shared enterprise contract.

Use this decision test:

1. Is the impact contained within the team's approved boundary?
2. Does the decision preserve relevant standards, contracts, and controls?
3. Does the accountable role have enough evidence and authority?
4. Is the decision sufficiently reversible?
5. Would another team, domain, or risk owner bear a material consequence?

If the impact is contained and the answer to the first four questions is yes, local decision-making is usually appropriate. If the fifth is yes, consult affected parties and consider escalation according to the agreed rules.

### 6.2 When escalation is justified

Escalate when one or more of these conditions applies:

- **Enterprise-wide impact:** the decision changes a standard, shared contract, common platform boundary, or behaviour used by several domains.
- **Difficult-to-reverse commitment:** migration, lock-in, broad consumer breakage, or a long-lived data-model commitment makes reversal costly.
- **High risk:** security, privacy, regulatory, financial, or material service risk exceeds delegated authority.
- **Unresolved cross-team conflict:** affected teams cannot agree after evidence and trade-offs are made explicit.
- **Policy exception:** the proposed choice violates a mandatory standard or control and requires a named approver.
- **Insufficient authority:** no participating role has authority to accept the consequence.

Do not escalate simply because a decision is technically interesting or because senior people prefer to be informed. Escalation should move the decision to the smallest forum with the authority to resolve it.

### 6.3 Working agreement: a practical example

The following one-page agreement is an illustrative starting point for a programme delivering customer-onboarding data to a risk platform. It should be adapted and approved by the organisation's actual accountable leaders.

#### Purpose

Deliver the onboarding-to-risk capability quickly while preserving shared data meaning, supportability, security controls, and clear ownership.

#### Decision boundaries

1. **Data architecture leads** decisions about shared data contracts, enterprise data standards, cross-system data definitions, and exceptions within its delegated authority.
2. **Data engineering leads** pipeline implementation, transformation logic, tests, retries, monitoring, and performance tuning inside approved contracts and platform boundaries.
3. **Solution architecture leads** end-to-end component interactions, solution-level integration design, and coordination of requirements across components.
4. A decision that spans boundaries must be split into explicit decisions or assigned one accountable owner with named contributors. “Everyone owns it” is not an acceptable default.
5. Business meaning and risk acceptance remain with the designated business/data/risk authority, not automatically with an architecture or engineering role.

#### Required shared artefacts

- A concise solution context and data-flow view.
- A versioned data contract with named producer and consumer contacts.
- A decision log for cross-boundary choices and exceptions.
- A list of assumptions, open questions, and evidence still required.
- Operational acceptance evidence for material pipeline and end-to-end requirements.

#### Review expectations

- Teams may make reversible implementation decisions within agreed boundaries without a full architecture review.
- Cross-team contracts, new shared standards, and material changes to common patterns receive a focused review before commitment.
- Reviewers state the requirement or risk behind a requested change. They do not block work solely on personal preference.
- Engineering participates early enough to challenge infeasible designs before implementation is committed.
- Solution architecture brings end-to-end consequences; data architecture brings cross-system data implications; engineering brings feasibility and operating evidence.

#### Escalation path

1. The decision owner documents the decision, alternatives, impact, and unresolved disagreement.
2. The three leads attempt a time-boxed resolution using agreed criteria and evidence.
3. If the decision affects enterprise standards, mandatory controls, or risk beyond delegated authority, escalate to the named architecture/governance or risk authority.
4. The accountable authority records the decision, accepted risks, any conditions, and the review date.
5. Work continues on independent tasks; escalation does not automatically stop unrelated delivery.

#### Change and exceptions

An exception must state the standard being varied, reason, scope, affected consumers, risks, compensating controls, owner, expiry or revisit trigger, and removal/migration plan where relevant. An exception is not a permanent undocumented precedent.

#### Measures that the agreement is working

- Every material decision has one accountable owner.
- Reviews identify risks early rather than after implementation.
- Reusable contracts and standards are discoverable.
- Exceptions are time-bounded and reviewed.
- Delivery teams can explain why a decision was made and how to challenge it.
- The same cross-boundary dispute does not recur because no decision record or standard was maintained.

### 6.4 Avoid three governance failure modes

#### Ivory-tower architecture

**Definition:** Architecture is produced far from delivery, with little understanding of operational constraints or implementation evidence.

**Signals:** Designs arrive late; engineers repeatedly discover infeasibility; exceptions are common; the architect cannot explain real failure modes.

**Correction:** Involve engineers and solution architects early, inspect current-state evidence, review implementation feedback, and keep constraints tied to requirements or risks.

#### Architecture by committee

**Definition:** Every decision requires broad consensus, even when a clear owner has delegated authority.

**Signals:** Repeated meetings without a decision, low-risk choices escalate, and accountability is hidden behind “we all agreed.”

**Correction:** Name one accountable owner per decision, define who must be consulted, set time limits, and escalate only when criteria are met. Consultation is not universal veto power.

#### Unowned decisions

**Definition:** A choice is made implicitly, postponed indefinitely, or assumed to belong to another team.

**Signals:** Teams use different standards, undocumented defaults become permanent, and no one can explain who accepted the risk.

**Correction:** Maintain a decision log with decision, owner, date, status, evidence, affected parties, and revisit trigger. If ownership is unclear, assign a temporary decision facilitator and resolve formal authority explicitly before an irreversible commitment.

### 6.5 One person wearing three hats

In a startup or small team, one person may perform data architecture, data engineering, and solution architecture. The roles do not disappear; they are **separate responsibilities even when one individual performs them**.

Use a deliberate “hat switch”:

1. Write the decision in one sentence.
2. State which role is leading and why.
3. Record the evidence and options from each relevant perspective.
4. Identify the risk of self-review or confirmation bias.
5. For material, hard-to-reverse, security-sensitive, or cross-team decisions, obtain an independent review from a qualified peer, adviser, or designated approver.
6. Record dissent and revisit conditions instead of pretending that one person has independently agreed with themselves.

**Trade-off:** This adds a small amount of process to a small team. The alternative is hidden self-approval, which can allow a preferred design to escape challenge.

### 6.6 Advanced exercise: write a working agreement

Draft a one-page agreement for a data programme. It must specify:

- Scope and purpose.
- The decision boundary for each discipline.
- One accountable role for each recurring decision type.
- Required shared artefacts.
- Review triggers and a proportionate review path.
- An escalation path and time limit.
- Exception documentation and revisit conditions.
- How the agreement will be evaluated and changed.

Ask a reviewer to identify any decision that has no owner, more than one implied final owner, or an escalation rule based only on seniority.

**Ability to demonstrate:** A working agreement that a delivery team can follow without turning routine engineering into a committee process.

---

## 7. Industry-application exercises

### 7.1 Banking scenario: customer onboarding data feeding a risk platform

**Scenario statement:** A bank is delivering a customer-onboarding capability that supplies customer information to a risk platform. The solution needs clear interfaces and reliable data handling. The roadmap calls for applying role boundaries and RACI to this context.

**Illustrative facts and assumptions for this lesson only:** The bank has an onboarding application, a customer data store, and a risk platform. A delivery deadline is approaching. Some interfaces or definitions may be undocumented. These are teaching assumptions, not verified facts about a real bank. Confirm every assumption during an actual assessment.

#### Step A — Describe the decision landscape

| Concern | Data architecture lens | Data engineering lens | Solution architecture lens |
|---|---|---|---|
| Meaning of customer data | Is the shared meaning and contract explicit? | Can the data be validated and transformed correctly? | Does the end-to-end solution use the data consistently? |
| Integration | Are cross-system standards and dependencies coherent? | Can the chosen flow be operated and recovered? | Do components interact correctly for onboarding and risk assessment? |
| Reliability | Are shared requirements and dependencies visible? | Are retries, replay, monitoring, and data correctness implemented? | What happens to the user journey when a component fails? |
| Change | Which consumers and standards are affected? | How can schemas and pipelines be migrated safely? | What is the end-to-end rollout and compatibility plan? |
| Accountability | Who owns the cross-system decision? | Who owns implementation and operational evidence? | Who owns the end-to-end solution design? |

The table is not a substitute for evidence. It tells the team which questions to ask and which role should bring the corresponding analysis.

#### Step B — Example first review

Suppose the solution architect proposes a direct point-to-point integration to meet the deadline. The data architect raises a concern about future consumers. The data engineering lead asks whether the proposed interface supports retries, schema changes, and operational monitoring.

Do not settle the disagreement by job title. Ask:

1. What business outcome and deadline must be met?
2. What existing contracts, standards, or platform constraints apply?
3. How many current and likely future consumers are affected?
4. What failure and recovery behaviour is required?
5. What is the implementation and operating cost of each viable option?
6. What is the cost of later changing or removing the point-to-point link?
7. Which decision is local, and which has cross-system consequences?
8. Who has delegated authority to accept any exception?

The solution architect owns the end-to-end design decision within the agreed boundary. The data architect owns or coordinates cross-system data architecture concerns within delegated authority. Engineering provides implementation and operational evidence. If the choice changes a shared standard or exceeds risk authority, escalate according to the working agreement.

### 7.2 Scenario: a solution architect proposes point-to-point integration under deadline pressure

| Decision element | Analysis |
|---|---|
| Decision | Use direct point-to-point integration for onboarding-to-risk data, or choose another integration arrangement |
| Participants | Solution Architect, Data Architect, Data Engineering Lead, business/product owner, operations; security/compliance if relevant |
| Accountable role | Solution Architect for the end-to-end solution choice, unless a shared standard exception or enterprise decision is required |
| Evidence required | Deadline and business need; interface/contract requirements; consumer count; failure and recovery behaviour; operational support cost; security/control implications; reversibility |
| Constraints | Delivery date, existing platform, approved standards, data sensitivity, risk-platform needs |
| Trade-offs | Direct integration may be faster and simpler now; a more reusable arrangement may reduce future coupling but require more initial work |
| Escalation conditions | The design violates a mandatory standard, creates a shared pattern, affects several teams, or accepts risk outside delegated authority |

**Reasoning:** The deadline is a real constraint, not an automatic override. If the direct integration is contained, acceptable, and reversible, it may be a reasonable bounded choice. If it creates a shared dependency or violates a standard, the accountable authority must explicitly accept or reject the exception.

### 7.3 Scenario: engineers select a streaming technology

| Decision element | Analysis |
|---|---|
| Decision | Choose a streaming technology for the data flow |
| Participants | Data Engineering Lead, engineers, Solution Architect, Data Architect, platform owner/operations, security as needed |
| Accountable role | Data Engineering Lead for a pipeline-level choice within an approved platform boundary; delegated platform/architecture authority if it establishes or changes an organisation-wide standard |
| Evidence required | Throughput and latency needs, delivery semantics, ordering and replay needs, operational maturity, skills, integration fit, cost, support model |
| Constraints | Approved platform, team capability, existing consumers, service requirements, security and operational controls |
| Trade-offs | A team-optimised choice may improve local fit but increase platform diversity and operating burden; a standard choice may simplify operations but fit the use case less well |
| Escalation conditions | The choice introduces a new shared platform, material lock-in, cross-domain contract implications, or enterprise-level support/cost obligations |

**Reasoning:** “Streaming technology” does not automatically mean “architect's decision.” The boundary depends on the scope of the commitment. Engineers should lead a local evaluation; enterprise-wide adoption requires broader authority and evidence.

### 7.4 Scenario: a reusable ingestion framework becomes a de facto standard

| Decision element | Analysis |
|---|---|
| Decision | Whether and under what conditions the framework becomes an organisational default |
| Participants | Framework maintainers, Data Engineering Lead, Data Architect, Solution Architects, platform operations, security, representative consuming teams |
| Accountable role | Delegated platform/architecture authority for the organisational adoption decision, unless final authority has explicitly been delegated to the Data Architect; the Data Architect coordinates the recommendation |
| Evidence required | Actual adoption, reliability and incident history, maintenance ownership, supported use cases, extension points, compatibility, security posture, cost, migration effort |
| Constraints | Existing workloads, support capacity, team autonomy, platform standards, backward compatibility |
| Trade-offs | Formalising a successful framework can improve reuse and consistency but may freeze immature assumptions; allowing unconstrained adoption preserves flexibility but can create unsupported variants |
| Escalation conditions | The framework affects multiple domains, becomes a mandatory standard, imposes migration costs, or requires funding/support commitments beyond its maintainers |

**Reasoning:** Repeated use does not automatically make a component a well-governed standard. The organisation should evaluate evidence, define support ownership and applicability, and document how teams can request exceptions.

### 7.5 Scenario: teams disagree over a cross-team data contract

| Decision element | Analysis |
|---|---|
| Decision | Define or change the contract, compatibility rules, and change process |
| Participants | Data Architect, producer and consumer engineering leads, Solution Architect, relevant data/business owner, operations and security where relevant |
| Accountable role | Data Architect for the cross-system contract within delegated authority; business/data owner remains accountable for business meaning where that authority is assigned to them |
| Evidence required | Current schema and semantics, consumer inventory, compatibility needs, change frequency, versioning/migration plan, data-quality failures, service requirements |
| Constraints | Existing consumers, backward compatibility, delivery deadlines, governance requirements |
| Trade-offs | A strict shared contract improves predictability but can slow change; permissive contracts speed local changes but push ambiguity and defensive coding onto consumers |
| Escalation conditions | Teams cannot agree on semantics, a breaking change affects critical consumers, or the decision requires business-risk acceptance beyond the architect's authority |

**Reasoning:** Separate semantic ownership from technical contract coordination. The data architect should not invent business meaning; engineers should not resolve a business definition solely through schema design. If a contract decision contains multiple questions, split them into semantic, compatibility, and implementation decisions with explicit owners.

### 7.6 Scenario: one startup employee performs all three roles

| Decision element | Analysis |
|---|---|
| Decision | How to make and review a cross-boundary decision when one person designs the solution, builds the pipeline, and defines data standards |
| Participants | The individual wearing the three roles; a founder/business owner; independent technical or security reviewer when warranted |
| Accountable role | The role delegated authority for the particular decision; the person must record which “hat” is leading |
| Evidence required | Requirements, options, constraints, expected operating behaviour, standards affected, risks, and a short written rationale |
| Constraints | Limited staff, speed, budget, access to reviewers |
| Trade-offs | Combining roles reduces coordination overhead but increases self-review and confirmation-bias risk; independent review costs time but improves challenge and accountability |
| Escalation conditions | High-impact or hard-to-reverse decision, sensitive data, material security risk, an external contractual/regulatory obligation, or lack of authority to accept the risk |

**Reasoning:** Role clarity is about responsibilities and decision logic, not the number of people. One person can perform several roles but should not treat a preferred implementation as independent validation. Use a lightweight decision record and obtain outside review when impact warrants it.

### 7.7 Industry-application exercise: produce the RACI and escalation path

Using the banking scenario:

1. Select six decisions from the cases above.
2. Complete a RACI-style table with one accountable role for each decision.
3. Mark required approvers separately where policy requires them.
4. State the evidence each consulted role must supply.
5. Define the escalation trigger and destination.
6. Explain what can be decided locally without a full review.
7. Review the table with another person and remove unowned decisions or ambiguous final authority.

---

## 8. Practical scenarios and case-based reasoning

Use the following method for any boundary dispute:

1. **State the decision precisely.** Avoid vague statements such as “we need to agree on architecture.”
2. **Identify scope.** Is the impact local to one pipeline, end-to-end within one solution, or cross-system/enterprise?
3. **Name the accountable role.** Use delegated authority, not seniority or meeting attendance.
4. **List evidence and constraints.** Separate verified facts from assumptions.
5. **Identify contributors and approvers.** Consultation supplies knowledge; approval enforces a defined control.
6. **Compare options and consequences.** Include delivery, operation, change, and risk.
7. **Decide or escalate.** Escalate only when the trigger is met.
8. **Record the result.** Capture owner, rationale, accepted risks, and revisit conditions.

### Scenario A: a solution architect proposes point-to-point integration

**Question:** Who decides, and on what grounds?

**Model reasoning:** The Solution Architect is accountable for the end-to-end solution design within the agreed boundaries. The Data Architect evaluates shared data-contract, duplication, and cross-system implications. Data Engineering evaluates feasibility, failure handling, and operational cost. If point-to-point integration violates a shared standard or creates a material enterprise dependency, it cannot be treated as a purely local decision; the exception or enterprise decision must go to the delegated authority. The decision should be based on requirements and evidence, not on who is most senior.

### Scenario B: an ingestion framework becomes a de facto standard

**Question:** How should it be governed?

**Model reasoning:** Treat adoption as evidence to evaluate, not as automatic approval. Assess reliability, maintenance, supported use cases, compatibility, security, operating cost, and the cost of migration. Name an accountable owner for the framework and a decision authority for organisational adoption. Define the default's scope, exception route, support expectations, and review trigger. Engineering maintains implementation evidence; data architecture or delegated platform governance coordinates the cross-team standard decision.

### Scenario C: a startup has one person doing all three roles

**Question:** How do you keep decisions honest?

**Model reasoning:** Separate the hats in the decision record. State whether the decision is an end-to-end solution choice, a shared data rule, or an implementation detail. Write alternatives and constraints before choosing. Seek independent review when the decision is hard to reverse or carries material security, regulatory, financial, or cross-team impact. This preserves speed while reducing the risk of undocumented self-approval.

### Scenario D: a cross-team data contract has no clear owner

**Question:** What is the first useful step?

**Model reasoning:** Do not begin by debating a schema format. Inventory producer and consumer teams, record the current semantics and known dependencies, identify the business/data owner of the meaning, and assign an accountable role for contract coordination. Mark unknowns explicitly. Agree a temporary change-control rule while the ownership gap is resolved. Escalate if no authority can assign ownership or if a breaking change cannot be safely delayed.

### Scenario E: an engineer says architecture review is slowing delivery

**Question:** How should the complaint be evaluated?

**Model reasoning:** Inspect the review trigger and actual delay. If routine reversible implementation choices are being reviewed, narrow the boundary. If the review concerns shared contracts, mandatory controls, or difficult-to-reverse enterprise decisions, the review may be justified—but should be time-boxed and evidence-based. Track avoidable rework, decision latency, exceptions, and recurring disputes to improve the process.

---

## 9. Expected outputs or deliverables

Complete and retain these artefacts:

### Deliverable 1 — Comparison table

A table comparing data architecture, data engineering, and solution architecture across purpose, scope, decisions, deliverables, and accountability. The table must use the definitions in this lesson and include at least one example of overlap.

### Deliverable 2 — Twenty-task classification exercise

Classify all twenty tasks in Section 4.5. For each, explain the primary discipline and any necessary collaborators. A label without reasoning is incomplete.

### Deliverable 3 — RACI-style decision table

Create a table for six realistic decisions. Each row must include one accountable role, responsible work, consulted roles, and informed roles. If formal approval is required, record the approver separately and identify the policy or delegated authority.

### Deliverable 4 — One-page working agreement

Include the purpose, decision boundaries, shared artefacts, review triggers, escalation path, exception handling, and signs that the agreement is working. It must be concise enough for a delivery team to use.

### Deliverable 5 — Topic 02 practice questions

Answer the Topic 02 section of [`practice-questions.md`](practice-questions.md). Correct each wrong answer and attempt it again. If the file is not yet populated, record that the questions are unavailable rather than claiming to have completed them.

### Suggested review questions for your artefacts

- Can a reader tell who makes the final decision?
- Is the accountable role appropriate to the scope and delegated authority?
- Are the consulted roles asked for specific evidence?
- Are implementation details being over-prescribed?
- Are enterprise standards being bypassed without an explicit exception?
- Is any role being made accountable for a business decision it does not own?
- Does the escalation path have a trigger, destination, and expected record?
- Could a team make routine, reversible choices without waiting for a committee?

---

## 10. Common mistakes and misconceptions

### Mistake 1: Treating the three disciplines as a hierarchy

**Why it is wrong:** Their authority differs by decision boundary, not by universal rank.

**Correction:** Assign accountability per decision and use delegated authority for exceptions and high-risk choices.

### Mistake 2: Assuming data architecture means “senior data engineering”

**Why it is wrong:** Engineering builds and operates pipelines and platforms; data architecture addresses shared data structure, standards, and cross-system decisions. Experience in engineering is valuable evidence, but it does not by itself settle enterprise ownership or business meaning.

**Correction:** State the decision and its scope before assigning the role.

### Mistake 3: Letting architects design down to implementation detail

**Why it is wrong:** Unnecessary prescription constrains engineering choices and can age faster than the architecture.

**Correction:** Require a traceable reason—such as interoperability, risk, or a measurable quality requirement—for a constraint. Leave choices inside the boundary to the implementation owner.

### Mistake 4: Allowing engineers to define enterprise standards by default

**Why it is wrong:** A reusable component may be technically sound without being suitable as an organisational default. Cross-team adoption introduces support, compatibility, governance, and migration responsibilities.

**Correction:** Bring evidence from implementation into a transparent cross-system decision with a named authority.

### Mistake 5: Confusing consultation with approval

**Why it is wrong:** Consultation gathers information; approval exercises a defined control. Treating every consulted person as a veto holder creates hidden governance.

**Correction:** Identify the decision owner, required consulted roles, and formal approver separately.

### Mistake 6: Assigning multiple `A` roles because the decision is complex

**Why it is wrong:** Complexity increases the need for clear accountability. It does not automatically justify ambiguity.

**Correction:** Split a composite problem into separate decisions or name one accountable role with explicit contributors. If a governance body has collective authority, document its formal decision mechanism.

### Mistake 7: Escalating based on seniority or disagreement alone

**Why it is wrong:** Seniority does not establish relevant authority, and disagreement can often be resolved locally with evidence.

**Correction:** Escalate for cross-system impact, high risk, difficult reversibility, policy exceptions, or lack of delegated authority.

### Mistake 8: Treating a working agreement as permanent

**Why it is wrong:** Team boundaries, systems, and risk profiles change.

**Correction:** Review the agreement after material organisational changes, recurring disputes, major incidents, or evidence that the review process is too heavy or too weak.

### Mistake 9: Treating role boundaries as a reason not to collaborate

**Why it is wrong:** The accountable owner needs evidence from other disciplines. A clean boundary without collaboration produces technically or organisationally incomplete decisions.

**Correction:** Keep one final owner while explicitly requiring the input necessary to make the decision responsibly.

---

## 11. Mastery criteria

You have mastered this lesson when you can demonstrate all of the following without relying on memorised labels alone.

- [ ] **Definitions:** Distinguish the purpose and scope of data architecture, data engineering, and solution architecture.
- [ ] **Deliverables:** Name typical deliverables and explain what each is intended to achieve.
- [ ] **Authority:** Explain the difference between decision ownership, responsibility, consultation, information, and formal approval.
- [ ] **Classification:** Classify twenty tasks, justify each primary assignment, and identify collaboration where needed.
- [ ] **RACI:** Produce a six-decision RACI-style table with one accountable role per decision and no unowned decision.
- [ ] **Overlap:** Resolve examples involving data modeling, integration design, technology selection, non-functional requirements, and standards.
- [ ] **Conflict resolution:** Explain how to handle over-prescriptive architecture, bypassed standards, and local optimisation.
- [ ] **Escalation:** Apply the lowest-appropriate-level principle and identify enterprise-wide, difficult-to-reverse, high-risk, and authority-related triggers.
- [ ] **Working agreement:** Produce an agreement that defines decision boundaries, shared artefacts, review, escalation, and exception handling.
- [ ] **Industry application:** Apply the model to the onboarding-to-risk banking scenario and defend decisions using evidence.
- [ ] **Role ambiguity:** Explain how one person can perform three roles while preserving explicit decision logic and independent review where warranted.
- [ ] **Communication:** Explain the three disciplines to a colleague and answer a challenge about a disputed decision.

A strong answer explains not only **who** leads, but **why**, what evidence is needed, which constraints apply, and when the decision must be revisited or escalated.

---

## 12. Completion gate

Do not mark this lesson complete until all of the following are true:

- [ ] Comparison table completed and reviewed.
- [ ] Twenty-task classification completed with reasoning and collaboration noted.
- [ ] RACI-style table completed for six decisions.
- [ ] A reviewer cannot find a decision without an accountable role.
- [ ] Any formal approver is identified separately where required.
- [ ] One-page working agreement completed and reviewed.
- [ ] Banking scenario and escalation path discussed or written up.
- [ ] Topic 02 practice questions answered; incorrect answers corrected and re-attempted.

### Final self-check

Before moving to Lesson 03, answer these questions in your own words:

1. Why is it inaccurate to say that one of the three disciplines always outranks the others?
2. What evidence would justify escalating a pipeline-level technology choice?
3. When does a shared data contract become more than an implementation detail?
4. How can a team keep decision ownership clear while consulting several experts?
5. What process prevents a useful engineering framework from becoming an unmanaged de facto enterprise standard?
6. How should a one-person startup handle decisions when one person wears all three hats?

If you cannot answer a question with a concrete example and a defensible decision rule, revisit the relevant section and correct the gap.

---

**Lesson boundary:** This lesson establishes role boundaries and collaboration. The next lessons build on this foundation by examining business capabilities, domains, and data ownership; this lesson does not replace those later topics.
