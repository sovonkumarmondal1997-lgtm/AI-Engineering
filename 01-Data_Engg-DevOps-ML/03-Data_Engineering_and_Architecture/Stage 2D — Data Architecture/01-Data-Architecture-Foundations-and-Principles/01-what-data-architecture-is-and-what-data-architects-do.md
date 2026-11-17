# 01 — What Data Architecture Is and What Data Architects Do

> **Stage:** 2D — Data Architecture  
> **Module:** 2D.1 — Data Architecture Foundations and Principles  
> **Position:** Lesson 01 of six, before role-boundary comparisons, business capabilities and ownership, architecture principles, lifecycle/governance, and frameworks/reference models.  
> **Purpose:** Learn to explain the discipline, identify its scope and deliverables, and reason from business need to defensible architecture decisions.

## How this lesson fits the roadmap

The Stage 2D project tree places this file in `Stage 2D — Data Architecture/01-Data-Architecture-Foundations-and-Principles/`. It is followed by lessons on data architecture versus neighbouring disciplines, business capabilities/domains/ownership, principles/quality attributes, lifecycle/governance, and frameworks/reference models. The module also contains [`practice-questions.md`](practice-questions.md) and the project [`Projects/01-current-state-data-architecture-inventory.md`](Projects/01-current-state-data-architecture-inventory.md).

The roadmap assumes Stage 2–2C data engineering experience: you have built or read a batch pipeline, a warehouse/lakehouse table design, and a streaming flow end to end; can work with SQL and basic relational/analytical stores; can read or draw simple data-flow diagrams; and can write a structured one-page note. If these are unfamiliar, revisit those prerequisites before treating the examples as operational designs. No enterprise-architecture certification or modeling-tool experience is required.

## 1. Learning objective

By the end, you should be able to:

- Explain data architecture's meaning, purpose, scope, and typical deliverables to a technical or business audience.
- Describe what a Data Architect is accountable for: understanding needs, defining cross-system structure and standards, making and recording decisions, reviewing designs, communicating trade-offs, and aligning work with governance.
- Distinguish an architecture from a diagram, a single design, documentation, a review, and implementation.
- Trace a business objective through business requirements and data requirements to an architecture decision, implementation, and business outcome—and trace the chain backward.
- Identify stakeholders, their concerns, and the evidence they need.
- Diagnose likely architectural problems without confusing symptoms with root causes.
- Write a one-page decision note with at least three genuine alternatives, explicit criteria, trade-offs, risks, assumptions, and a trigger for revisiting the decision.

**Completion outcome:** foundational competence to participate credibly in an architecture review, produce a reviewable current-state assessment, and defend a short decision record. This lesson alone does not make someone a senior enterprise architect.

## 2. Why this topic matters in real-world Data Architecture

Organizations build systems incrementally. A team may choose a database that meets its immediate need; another team may copy the same customer data into a reporting store; a third may define “active customer” differently; and a fourth may create a point-to-point feed because it is the fastest route to delivery. Each choice can look reasonable in isolation. Across the organization, the result can be inconsistent, duplicated, costly, difficult to change, and hard to govern.

Data architecture supplies the connecting view: what data exists, what it means, where it is stored, how it moves, who is accountable for it, how it may be used, and how the whole arrangement serves business goals. It makes important trade-offs explicit before local decisions become expensive enterprise constraints.

### 2.1 What data architecture is

**Data architecture is the organization-wide or cross-system structure and set of decisions that determine how data is represented, stored, integrated, governed, protected, maintained, and used to support business objectives.** It includes the relationships among data assets and the rules that make those relationships understandable and sustainable.

Think of it as a coherent set of decisions—not a particular product, diagram, database, or pipeline. It connects business meaning to data structures and technical arrangements, while accounting for constraints such as cost, risk, security, quality, availability, and change.

**Why it matters:** without a coherent view, systems may work individually while disagreeing or conflicting collectively.  
**How it works:** architects gather evidence about business needs and the existing estate, identify important cross-system relationships, define principles and target direction, record decisions, and work with delivery teams to check that implementations remain aligned.  
**When useful:** when data crosses teams or systems, when definitions conflict, when a platform or integration choice affects multiple consumers, or when the organization must explain data lineage and accountability.  
**Limitations:** architecture cannot remove every inconsistency by decree, and a target diagram does not itself create ownership, funding, implementation capacity, or reliable data.  
**Example:** a bank's reporting teams may each calculate “active customer” from different source events. Architecture work investigates the meaning, ownership, sources, transformations, and authorized uses before recommending how to align or explicitly distinguish the definitions.

### 2.2 Scope of data architecture

| Scope area | What the architect considers | Example question |
|---|---|---|
| Data assets | Important datasets, entities, events, files, reports, and products | What customer and transaction assets exist, and who uses them? |
| Data models and meaning | Definitions, relationships, identifiers, grain, and business rules | Does “customer” mean a person, an organization, or a customer relationship? |
| Storage | Where data persists and why a storage pattern fits | Is this operational data, analytical history, or a derived product? |
| Integration and movement | Interfaces, dependencies, exchange patterns, and data contracts | Which systems exchange this data, and what happens when its schema changes? |
| Platforms | Shared capabilities and their cross-system role | Which platform capabilities are shared, and which are local? |
| Governance and ownership | Accountability, decision rights, policies, and exceptions | Who can approve a definition change or a new use? |
| Quality and lineage | Fitness for use, transformations, dependencies, and evidence | Can a report be traced back to sources and transformations? |
| Security and privacy | Access, classification, permitted use, retention, and exposure | Who may access the data, for what purpose, and for how long? |

These areas interact. For example, a new analytics copy is not merely a storage decision: it may introduce new lineage obligations, access controls, retention concerns, duplicate definitions, and operating costs.

**What is not the primary scope of this lesson:** application code and the detailed logic of an individual pipeline. Such implementation matters, but the architectural concern is the cross-system structure, standards, constraints, and decisions that shape it. The full comparison with data engineering and solution architecture belongs in Lesson 02; do not try to settle every role boundary here.

### 2.3 Why organizations need an architect

An organization needs architecture when the consequences of a decision extend beyond the team making it. The Data Architect helps the organization:

1. **Connect business goals to data capabilities.** Data should serve a defined outcome rather than exist because a technology makes it easy to collect.
2. **Make definitions and responsibilities explicit.** A field name is not a shared definition; someone must be accountable for its meaning and change.
3. **Expose dependencies.** A local change may affect reports, models, regulatory evidence, or downstream consumers.
4. **Compare options consistently.** Teams can assess cost, risk, security, maintainability, and delivery speed against agreed criteria.
5. **Make change safer.** Known ownership, lineage, contracts, and decisions reduce surprise when a system changes.
6. **Preserve decision context.** Future teams can understand why a choice was made and when it should be revisited.

Architecture does not mean central approval for every small technical choice. Good architecture sets useful boundaries, clarifies decision rights, and lets teams make local decisions when their impact and risk are local.

### 2.4 What a Data Architect does

Typical responsibilities include:

- Discover business goals, capabilities, stakeholders, constraints, and existing data flows.
- Inventory important data assets, systems, interfaces, consumers, owners, and unknowns.
- Define target-state direction, cross-system structures, principles, standards, and reusable patterns.
- Evaluate alternatives and record the rationale, consequences, risks, and assumptions.
- Review proposed designs for alignment with requirements and enterprise constraints.
- Communicate with business owners, engineers, security/compliance, operations, and auditors.
- Identify governance needs and clarify who can decide, approve, or accept an exception.
- Track whether implementation matches the intent and update architecture as evidence changes.

A Data Architect is **not simply the person who picks technology products**. Product selection is one possible consequence of a decision, not the purpose of the role. A recommendation should follow from context, evidence, criteria, and trade-offs—not from personal preference or vendor familiarity.

### 2.5 Typical deliverables

| Deliverable | What it records | Why it is useful | Common failure mode |
|---|---|---|---|
| Current-state view | What is known about today's systems, data assets, interfaces, users, owners, and gaps | Establishes the baseline for change | Treating guesses as verified facts |
| Target-state view | Intended future relationships, capabilities, standards, and transitions | Makes direction and dependencies visible | Drawing an ideal end state without constraints or migration steps |
| Architecture principles | Durable decision guidance with rationale and implications | Keeps decisions consistent across teams | Vague slogans nobody can apply |
| Standards | Agreed conventions or requirements for recurring decisions | Reduces avoidable variation | Standards that are ignored or impossible to meet |
| Reference architecture | A reusable starting structure for a recurring class of problems | Speeds consistent design while allowing justified adaptation | Copying it without checking fit |
| Decision record | Context, options, criteria, choice, consequences, risks, and owner | Makes reasoning reviewable and reversible where possible | Recording only the chosen option |
| Architecture roadmap | Sequenced changes, dependencies, transition steps, and decision points | Connects target direction to delivery | A wish list with no owners or dependencies |

A deliverable is useful only if its audience can act on it and it is maintained as the system changes.

### 2.6 Architecture versus a diagram

A **diagram** is one way to communicate part of an architecture. An **architecture** is the underlying set of structures, relationships, principles, constraints, and decisions. A diagram can be attractive and still omit ownership, business meaning, security constraints, failure modes, or why a choice was made.

```text
Business objective
       |
       v
Business and data requirements
       |
       v
Architecture decisions <---- constraints, evidence, risks
       |
       v
Designs and implementation
       |
       v
Observed business outcome
       |
       +---- feedback and revised decisions ----+
```

This diagram shows a reasoning chain, not a required technology stack. The architecture is reflected in the decisions and relationships across the chain. A box-and-arrow picture alone is not proof that the architecture is sound.

### 2.7 Design, documentation, review, and implementation

These are distinct activities that support one another:

| Activity | Meaning | Typical output | Example |
|---|---|---|---|
| **Design** | Create a proposed structure or approach that satisfies requirements | Model, interface proposal, flow, or design specification | Propose a shared customer-data contract |
| **Documentation** | Record facts, decisions, relationships, and rationale | Inventory, diagram, standard, decision record | Record why a definition is authoritative and who owns it |
| **Review** | Assess a proposal or implementation against requirements, principles, constraints, and risks | Findings, conditions, approval or rejection recommendation | Identify missing lineage and unclear access controls |
| **Implementation** | Build, configure, migrate, and operate the chosen solution | Running systems, pipelines, controls, tests, and runbooks | Deliver the feed and enforce its contract |

One person may perform more than one activity in a small organization, but the activities remain conceptually different. A design can be documented badly; a well-documented design can be wrong; a review can identify a flaw without implementing the fix; and an implementation can diverge from an approved design. Architecture is continuous through delivery and change, not a one-time phase completed before engineers begin.

### 2.8 Beginner exercise: describe a system you know

Write exactly six sentences about a system you know. Do not invent answers to make the description look complete.

1. **What it holds:** name the main data assets and their broad meaning.
2. **Who uses it:** name user groups or consuming systems.
3. **Where data enters:** identify sources, events, files, or manual inputs.
4. **Where data leaves:** identify reports, APIs, downstream stores, or other consumers.
5. **Who is accountable:** name an accountable role if known; otherwise write “unknown—needs confirmation.”
6. **What you do not know:** list uncertainties such as retention, lineage, update frequency, quality rules, or access approval.

**Worked miniature example (illustrative):** “The service stores customer contact details and service interactions. Support agents and a reporting team use it. Data enters through customer updates and service events. A daily export feeds a reporting store. The accountable data owner is not yet confirmed. The export's retention period and transformation lineage are unknown.”

The last sentence is not a weakness: making uncertainty visible is more trustworthy than turning an assumption into a fact.

## 3. Prerequisite knowledge

### 3.1 Essential prerequisites

Before proceeding, you should be able to:

- Read or build a batch pipeline end to end.
- Understand a warehouse/lakehouse table design and a streaming flow at a basic practical level.
- Use SQL and understand basic relational and analytical stores.
- Read and draw simple box-and-arrow data-flow diagrams.
- Write a clear one-page structured note.

These are prerequisites because architecture reasons about real systems and their consequences. If a source, transformation, table, or consumer is unfamiliar, you may not yet have enough evidence to evaluate the proposed architecture.

### 3.2 Helpful, but not required

Exposure to a real organization's systems or a realistic case study helps connect abstract concepts to practice. Familiarity with data products and data mesh is helpful because later lessons discuss domains and ownership at organizational level. Basic awareness of data protection and regulatory concerns is also useful; detailed governance treatment belongs to later modules.

No prior certification, enterprise architecture framework experience, or modeling-tool experience is required.

## 4. Beginner-level learning sequence

Complete these steps in order.

### Step 1 — Define the discipline in your own words

Write a two- or three-sentence definition that includes structure, storage, movement, governance, use, and business goals. Avoid defining architecture as “choosing databases” or “drawing diagrams.”

**Check:** Can a non-technical colleague understand why architecture is needed without hearing a list of products?

### Step 2 — Identify the scope

Use the eight scope areas in Section 2.2 to classify the issues in a familiar system. Note both what is known and what requires evidence. Explain why a new copy of a dataset may affect quality, lineage, access, and cost—not only storage.

### Step 3 — Explain the role and deliverables

List the responsibilities in Section 2.4 and match each to a deliverable in Section 2.5. For example, an inventory supports discovery; a decision record supports traceability; a roadmap supports sequenced change. Do not assume that every organization uses identical document names.

### Step 4 — Explain architecture versus a diagram

Take a simple data-flow diagram and list the decisions or facts it does not communicate: ownership, definitions, constraints, security, risks, rationale, or unknowns. Add annotations or a decision record where useful.

### Step 5 — Complete the six-sentence system exercise

Use Section 2.8. Label uncertain statements. Ask a reviewer whether each sentence is understandable and whether facts are separated from assumptions.

### Step 6 — Deliver a two-minute explanation

Explain the definition, why the organization needs architecture, the architect's responsibilities, and two or three deliverables. Keep it business-oriented: describe decisions and outcomes rather than reciting technology names.

**Beginner demonstration:** explain data architecture and the role's deliverables in two minutes to a non-technical colleague.

## 5. Intermediate-level learning sequence

### 5.1 Trace business objective to outcome

Use the following chain:

**Business objective → business requirement → data requirement → architecture decision → implementation → business outcome**

Each link answers a different question:

| Link | Question | Illustrative banking example |
|---|---|---|
| Business objective | What result matters? | Improve the consistency of customer reporting |
| Business requirement | What must the business be able to do? | Produce a report using an agreed, explainable definition |
| Data requirement | What must be true of the data? | Definition, source, calculation, effective time, and lineage are known |
| Architecture decision | What cross-system arrangement supports it? | Establish accountable ownership and a governed definition/contract, while documenting legitimate use-specific variants |
| Implementation | What will teams build or change? | Update transformations, contracts, metadata, tests, and consuming reports |
| Business outcome | What observable result follows? | Reports can be reconciled and their meaning explained; measure this rather than assuming success |

The example is illustrative, not a claim about a real bank. A decision is not justified merely because it sounds modern; it must connect to a requirement and an outcome.

**Trace forward:** for each link, ask what it implies for the next.  
**Trace backward:** start from an implementation or an outcome and ask which requirement and decision justify it. If nobody can explain why a data copy exists, that is a discovery finding—not automatic proof that the copy should be deleted.

### 5.2 Distinguish local design from architecture decisions

A local design can implement a broader architecture decision. For example, an architecture standard may require a documented data contract and named owner; a delivery team then designs a particular interface and tests. The architect should not prescribe every implementation detail without reason. Conversely, a local choice becomes an architecture concern when it changes shared semantics, introduces an enterprise dependency, creates material risk, or conflicts with a standard.

The boundary depends on impact and accountability, not only on the technology involved.

### 5.3 Identify stakeholders and their expectations

Stakeholders may value different outcomes. An executive may prioritize value and risk; a business owner may prioritize correct business meaning; an engineer may need feasibility and unambiguous contracts; security/compliance may require evidence of permitted access and use; operations may need supportability; and auditors may require traceability.

A strong architect does not label one stakeholder “right” and the others “wrong.” They surface conflicts, identify non-negotiable constraints, and make trade-offs visible.

| Stakeholder | Likely concern | Useful evidence or artefact | Question to ask |
|---|---|---|---|
| Executive or sponsor | Value, cost, risk, delivery impact | Options summary, cost/risk implications, outcome measures | Which outcome matters most, and what risk is unacceptable? |
| Business/data owner | Correct meaning, accountability, usable data | Business definition, ownership register, examples of affected decisions | Who is accountable for the definition and its changes? |
| Data/solution engineers | Feasibility, clear contracts, dependencies | Data-flow view, interface contract, constraints, decision record | What must remain stable, and what can the team choose locally? |
| Security/compliance | Access, privacy, retention, policy adherence | Data classification, access model, retention evidence, lineage | What use is permitted, and what evidence is required? |
| Operations/platform team | Reliability, support, recovery, cost to run | Operational ownership, dependency map, failure and recovery assumptions | Who detects and resolves a failure? |
| Auditor or assurance function | Evidence, traceability, control operation | Lineage, approvals, versioned definitions, control evidence | Can the result be traced and independently checked? |

This table describes common expectations, not a universal organization chart. Validate actual decision rights and evidence standards in the organization being assessed.

### 5.4 Recognize common architectural problems

| Problem | Observable symptom | Candidate architectural cause(s) | First useful question |
|---|---|---|---|
| Duplicated data | Several copies of a dataset exist | No agreed sharing pattern, ownership, or copy lifecycle | Which copies serve distinct requirements, and who approves each? |
| Inconsistent definitions | Reports disagree about the same term | Definitions differ, rules are hidden in transformations, or use cases genuinely differ | What exact rule and time window does each report use? |
| Unclear ownership | Changes are delayed or disputed | Accountability is assigned to a system/team rather than a responsible role | Who is accountable for meaning, quality, and change approval? |
| Point-to-point integration sprawl | Many brittle feeds and dependencies | Local integrations grew without shared contracts or lifecycle management | Which dependencies are critical, and who owns each contract? |
| Uncontrolled copies | Sensitive or stale data appears in unexpected places | Copy creation, access, retention, and deletion are not governed | What is the purpose, permitted use, owner, and expiry of each copy? |
| Missing lineage | A result cannot be traced to source and transformation | Metadata is incomplete or transformations are not recorded | What is the smallest high-value lineage path we can verify end to end? |

These are hypotheses, not diagnoses. A duplicate may be justified for resilience or a distinct operational need. Two definitions may both be valid if they represent different business concepts. First gather evidence, then decide whether a pattern is a defect, an accepted trade-off, or a legitimate distinction.

### 5.5 Intermediate exercise: find five architectural problems

Use a one-page description of an organization or the banking case in Section 7. For each of five candidate problems, record:

1. Observed fact or reported symptom.
2. Affected stakeholder(s).
3. Candidate cause (label it a hypothesis).
4. Evidence currently available and evidence missing.
5. First question to ask.
6. Possible consequence if left unresolved.

**Worked example:** “Two dashboards report different active-customer counts” is the observation. The affected stakeholders may include business reporting, risk, operations, and assurance. Candidate causes include different definitions, different source coverage, different as-of times, or different transformations. The first question is not “Which dashboard is wrong?” but “What definition, population, time window, source, and transformation does each dashboard use?”

**Intermediate demonstration:** map a business request through to the architecture decisions it implies, and explain the impact on different stakeholders.

## 6. Advanced-level learning sequence

### 6.1 Separate symptoms from root causes

A symptom is an observable result; a root cause is a condition that produces or sustains it. “Reports disagree” is a symptom. Possible causes include divergent definitions, unowned business rules, different cut-off times, missing lineage, inconsistent source coverage, or stale copies. More than one cause may be present.

Use a disciplined hypothesis loop:

1. State the observation without interpretation.
2. List multiple plausible causes.
3. Identify evidence that would distinguish them.
4. Collect or request that evidence.
5. Update the hypothesis; record what remains unknown.
6. Only then propose a structural intervention.

**Failure mode:** immediately selecting a new master database can create migration cost without fixing the underlying definition or ownership problem.

### 6.2 Frame an architecture decision

A decision note should make the reasoning challengeable. Include:

- **Problem:** the observed issue and why it matters.
- **Context:** systems, stakeholders, scope, current state, and business objective.
- **Constraints:** mandatory policies, deadlines, capabilities, and limits.
- **Assumptions and unknowns:** what is believed but not yet verified.
- **Options:** at least three credible alternatives, including the status quo when appropriate.
- **Criteria:** how options will be judged and which criteria are mandatory.
- **Trade-offs:** what each option improves and what it costs or makes harder.
- **Recommendation:** the selected option and why it best fits the criteria.
- **Risks and mitigations:** what could go wrong, its consequence, and how to detect or reduce it.
- **Owner and revisit trigger:** who is accountable and what evidence or event would reopen the decision.

A decision record is not a sales pitch. It should include the strongest reason against the recommendation and state what evidence could change the outcome.

### 6.3 Manage assumptions and uncertainty

An **assumption** is a proposition temporarily treated as true for reasoning; an **unknown** is a question not yet answered; a **constraint** is a boundary the decision must respect; a **risk** is an uncertain event or condition with a possible consequence. Do not silently convert one category into another.

Maintain a small assumption log:

| Item | Type | Current statement | Validation method | Owner | Decision impact if false |
|---|---|---|---|---|---|
| Reporting needs a shared definition | Assumption | Core reporting needs a common baseline, while some use cases may need separate metrics | Interview report owners and compare use cases | Business owner | May change whether one definition or a family of definitions is appropriate |
| Lineage is incomplete | Reported claim / unverified | Stakeholders say no complete lineage statement is available | Trace one priority report through source and transformation evidence | Data architect with system owners | May change the size and urgency of remediation |
| A policy prohibits a proposed use | Constraint candidate | Policy interpretation needs confirmation | Ask the accountable compliance function and record the rule | Compliance owner | Could rule out an option entirely |

**Prioritize validation** by decision impact, uncertainty, and cost of being wrong. Validate high-impact assumptions early. Avoid spending weeks proving low-impact details before the key decision can be framed.

### 6.4 Reversible and difficult-to-reverse decisions

A **reversible decision** can be changed at relatively low cost and with limited disruption. A **difficult-to-reverse decision** creates migration cost, entrenched dependencies, contractual commitments, or broad consumer impact.

- Examples of more reversible choices may include a temporary reporting view, a pilot contract, or a time-limited adapter—provided rollback and data semantics are understood.
- Examples of harder-to-reverse choices may include making a shared identifier authoritative across many systems, migrating multiple critical consumers, or committing to a platform that creates significant dependency.

These are contextual examples, not fixed categories. A small proof of concept may be reversible in one environment and dangerous in another if it exposes sensitive data or becomes a production dependency.

**Rule of thumb:** make a reversible choice to learn when the cost of delay is high and the downside is bounded; slow down and validate when the decision is high-impact, difficult to reverse, or constrained by regulation or safety. Record a rollback or migration path where feasible.

### 6.5 Balance local and enterprise optimization

A team's local optimum may impose costs on other teams. For example, a bespoke customer extract might satisfy one dashboard quickly but create another definition, copy, access path, and maintenance burden. A shared service may improve consistency but add coordination, latency, or operational cost.

Resolve the tension by:

1. Defining the business outcome and the affected scope.
2. Separating mandatory constraints from preferences.
3. Measuring the local benefit and the enterprise-wide cost or risk.
4. Identifying whether the need is genuinely unique or can use a shared contract.
5. Choosing the lowest level that has enough information and accountability to decide.
6. Escalating only when the decision crosses domains, violates a standard, or carries enterprise-wide, hard-to-reverse, or high risk.
7. Recording any exception, owner, mitigation, and review date.

Enterprise-wide consistency is not an absolute goal: different use cases may legitimately require different views. The goal is intentional, explained variation rather than accidental inconsistency.

### 6.6 What evidence could change the decision?

Before finalizing a recommendation, ask:

- What evidence would show that our problem statement is wrong?
- What would make a rejected alternative better than the recommendation?
- Which assumption has the largest effect on cost, risk, or outcome?
- Can we test a small representative path before committing broadly?
- What measurable signal should trigger review?

Examples include evidence that definitions actually represent different business concepts, that a source system cannot support the required latency, that a policy forbids a proposed use, that migration costs exceed expected benefits, or that a lineage pilot reveals a much smaller gap than reported.

### 6.7 Complete worked decision note — reconciling “active customer” reporting

> **Status of case details:** The following is an illustrative training case. The only case premise taken from the roadmap is that a bank has customer data in five systems with different definitions of “active customer.” All additional details, option assessments, and sample scores below are assumptions for learning, not verified facts about a real bank. Replace them with evidence in an actual assessment.

#### Decision title

Choose an initial architecture approach for making customer activity reporting explainable across five systems.

#### Problem and context

**Reported premise:** customer data is held in five systems and the term “active customer” is defined differently. This creates a risk that reports are not comparable and that stakeholders cannot explain why counts differ.

**Illustrative assumptions to validate:** some reports are for operational management, some for risk, and some for executive reporting; definitions may differ because of business purpose, event coverage, time windows, or transformations; complete end-to-end lineage is not currently available. These assumptions must be tested rather than treated as facts.

#### Decision constraints and open questions

- Preserve legitimate differences in business meaning; do not force one metric if use cases genuinely differ.
- Identify an accountable business owner for each approved definition.
- Establish permitted access and handling before creating new copies of customer data.
- Make the result traceable to sources and transformations.
- Confirm delivery urgency, current system capabilities, costs, and applicable policies during discovery.

#### Alternatives considered

| Option | Description | Advantages | Trade-offs and risks |
|---|---|---|---|
| **A. Keep each definition independent and document differences** | Retain current calculations, document each meaning, source, and consumer, and explicitly label them | Lowest immediate change; preserves local use cases; useful if definitions are genuinely different | Does not by itself create a comparable enterprise view; documentation may become stale; inconsistent results may persist where a common meaning is required |
| **B. Establish a governed definition and contract, while retaining justified variants** | Assign a business owner to a common baseline where appropriate; document approved variants, source mappings, calculation rules, effective time, lineage, and consumer expectations | Balances comparability with legitimate variation; creates accountability and traceability; can be implemented incrementally | Requires stakeholder agreement, ownership, metadata and transformation changes; disputes may take time; a weak governance process could stall delivery |
| **C. Centralize all customer activity calculations in one new shared service/store** | Move or rebuild calculations in a central location and direct consumers to it | Potentially reduces duplicated logic; can create a common operational point for definitions and lineage | Higher migration and dependency cost; may create a bottleneck or single point of operational failure; cannot resolve semantic disagreement automatically; broad migration may be difficult to reverse |
| **D. Build a temporary reconciliation layer for priority reports** | Create a time-bounded mapping/reconciliation layer for a small set of high-value reports while discovery continues | Faster learning; limits initial scope; may expose the actual causes of disagreement | Can become a permanent shadow system; adds another transformation; must have an owner, expiry/review trigger, and controlled access |

These are genuine alternatives because they represent materially different scopes and commitments. Option A is not “do nothing” if it includes explicit documentation; Option D is not acceptable without a sunset or review condition.

#### Illustrative decision criteria

Mandatory criteria: approved data use and access; an accountable owner; explainable definitions; ability to trace the priority output to sources and transformations; and no unsupported claim that unlike metrics are equivalent.

Additional criteria: time to first useful result, total lifecycle cost, impact on current consumers, reversibility, operational complexity, and ability to scale to further reports.

#### Illustrative comparison

Scores below are **illustrative only**, from 1 (weak) to 5 (strong). They are not empirical measurements and must be replaced by evidence and stakeholder-agreed weights. A mandatory constraint cannot be compensated for by a high total score.

| Criterion | A: document variants | B: governed definition + variants | C: central service/store | D: temporary reconciliation |
|---|---:|---:|---:|---:|
| Time to first useful result | 4 | 3 | 1 | 5 |
| Explainability and traceability potential | 2 | 5 | 4 | 3 |
| Preserves legitimate business differences | 5 | 5 | 2 | 4 |
| Reversibility / bounded commitment | 5 | 4 | 1 | 5 |
| Enterprise consistency potential | 2 | 5 | 5 | 3 |
| Ease of initial delivery (higher score = easier) | 5 | 3 | 1 | 4 |

Interpretation: A is quick and preserves differences but may not resolve comparability. C could consolidate logic but has the highest commitment and cannot decide business semantics on its own. D can produce fast evidence but must not become an uncontrolled permanent layer. B is a balanced target if stakeholders confirm that a shared baseline is meaningful and can name accountable owners.

#### Recommendation

**Illustrative recommendation: choose Option B as the target direction, using a tightly scoped Option D pilot to validate the highest-priority report path before broader implementation.** This is a conditional recommendation, not a claim that a bank should always centralize definitions. First verify whether the use cases share a meaningful baseline, identify owners, trace one report end to end, and confirm policy and operational constraints. Preserve separately named variants when their business purpose genuinely differs.

#### Risks, mitigations, and ownership

| Risk | Potential consequence | Mitigation / evidence to gather | Proposed accountable role (confirm locally) |
|---|---|---|---|
| Stakeholders cannot agree on meaning | Work stalls or a misleading definition is imposed | Compare real decisions each metric supports; document variants and escalation path | Business data owner / domain authority |
| Source lineage is incomplete | Reports remain difficult to explain | Trace one priority output to source, transformations, and final calculation; record gaps | System owners with data architecture coordination |
| Pilot becomes a permanent shadow system | More duplication and maintenance burden | Set scope, owner, expiry/review date, and exit criteria before launch | Pilot sponsor and delivery owner |
| A new copy increases exposure | Unauthorized access or retention risk | Confirm classification, permitted purpose, access, retention, and deletion controls before copying | Data owner with security/compliance |
| A shared definition hides legitimate differences | Incorrect business interpretation | Require use-case review and versioned, explicit variants | Business owner(s) for affected uses |

#### Revisit trigger

Revisit the recommendation if the pilot shows that the definitions represent genuinely different business concepts, if a mandatory policy or source-system constraint rules out the proposed approach, if the priority lineage path cannot be established at reasonable cost, or if measured implementation cost/consumer impact materially exceeds the agreed threshold. The owner should set a calendar review date as well as these event-based triggers.

#### Why this is a defensible decision

The recommendation identifies a problem, compares more than three options, makes criteria explicit, distinguishes assumptions from verified facts, exposes the strongest trade-offs, assigns risks, and says what would change the decision. A reviewer can disagree with the recommendation while still understanding and challenging its reasoning. That is the purpose of a decision note.

**Advanced exercise:** write your own one-page note for a problem identified in the intermediate exercise. Include at least three real alternatives, context, constraints, criteria, trade-offs, recommendation, risks, assumptions, owner, and revisit trigger. Do not copy the worked recommendation if your evidence supports a different choice.

**Advanced demonstration:** produce a decision note a reviewer can challenge on its merits rather than because important information is missing.

## 7. Industry-application exercises — banking customer data

### 7.1 Case framing and assumptions

**Roadmap premise:** a bank has accumulated customer data in five systems, each with a different definition of “active customer.” The lesson must investigate this situation rather than assume the solution is simply to select a master database.

**Illustrative facts/assumptions for exercises only:**

- Assume the five systems serve different business processes; their actual names and functions are unknown.
- Assume at least some reports disagree; the existence and scale of that disagreement must be verified.
- Assume stakeholders may use activity measures for different decisions. Which decisions and which definitions are legitimate must be established through interviews and evidence.
- Assume lineage may be incomplete because the roadmap asks learners to consider a missing-lineage scenario; the actual state must be assessed.
- No actual customer counts, regulatory findings, technology products, policies, or bank-specific architecture are asserted here.

Keep three categories separate in your notes: **verified fact**, **stakeholder-reported claim**, and **assumption/hypothesis**.

### 7.2 How a Data Architect should approach the bank

1. **Clarify the business decisions.** Ask what “active customer” is used to decide, who consumes the measure, and what error would matter.
2. **Inventory the five systems.** Record purpose, data assets, interfaces, consumers, accountable owners, and known dependencies. Do not assume all systems hold equivalent records.
3. **Collect definitions as implemented.** For each definition, record the exact rule, event/source coverage, time window, effective date, exclusions, transformation, and report using it.
4. **Trace one high-value output end to end.** Follow a report from its source through ingestion, transformations, joins, filters, and final aggregation. Record missing links rather than guessing.
5. **Interview stakeholders separately and together.** Identify agreements, conflicts, decision rights, and evidence that would resolve disagreement.
6. **Form hypotheses about root causes.** Different business meanings, different data coverage, different as-of times, stale copies, and hidden logic are possible explanations—not conclusions.
7. **Frame options and constraints.** Consider documenting variants, establishing a governed baseline, a scoped reconciliation pilot, or a broader shared service. Evaluate each against evidence and requirements.
8. **Record the decision and transition.** Name owners, risks, migration implications, measures of success, and a revisit trigger.

### 7.3 Stakeholder expectation table

| Stakeholder | Likely concern | Evidence they may accept | Initial question |
|---|---|---|---|
| Executive sponsor | Whether inconsistent reporting affects decisions, risk, cost, or trust | Business impact statement, prioritized reports, options and trade-offs | Which decisions are blocked or weakened by the inconsistency? |
| Business/report owner | Meaning of “active” and fitness for a specific decision | Definition with examples, exclusions, time window, owner approval | What does active mean for this report, and why? |
| Owners of the five systems | Source semantics, operational constraints, change impact | Source definitions, interface contracts, change dependencies | Which source events and rules does your system represent? |
| Data engineering/delivery teams | Transformation logic, feasibility, dependencies, delivery effort | SQL/logic review, lineage trace, data contract, impact analysis | Where is the rule implemented, and which consumers depend on it? |
| Security/compliance | Authorized use, access, retention, sensitive-data exposure | Classification, purpose, access records, retention and lineage evidence | May this data be joined, copied, and used for this purpose? |
| Operations/platform team | Reliability, support burden, failure handling | Ownership, monitoring, dependency and recovery information | Who detects a broken feed and restores the data service? |
| Audit/assurance | Reproducibility and traceability of reported numbers | Versioned definitions, approvals, lineage, source-to-report evidence | Can an independent reviewer reproduce and explain the number? |

Validate the actual stakeholder set and authority model. “Likely concern” is a starting hypothesis, not a substitute for discovery.

### 7.4 First two weeks: assessment questions and plan

The roadmap specifically asks for the questions an architect would ask during the first two weeks. The following is a practical sequence; timing should adapt to access and urgency.

#### Days 1–3: establish the business problem

- Which business decisions use “active customer” today?
- Which reports or processes are highest priority, and why?
- What does each stakeholder mean by “active”? Are they describing one concept or several related concepts?
- What are the exact rules, time windows, exclusions, and as-of dates?
- What impact has been observed, and what is merely suspected?
- Who can approve the business definition, and who can approve an exception?
- What policy, contractual, privacy, security, or retention constraints apply? Who can authoritatively confirm them?

#### Days 4–7: map systems and evidence

- What are the five systems, their purposes, owners, and principal data assets?
- Which system creates or updates each relevant customer attribute or event?
- Where are definitions implemented—in source systems, transformation logic, reporting tools, or manual procedures?
- Which data feeds, extracts, joins, filters, and aggregations contribute to the priority report?
- What is the freshness and as-of-time behavior of each source and output?
- Which copies exist, why do they exist, who uses them, and when are they deleted or refreshed?
- Can we trace one selected report from its final number to source records and transformations? Where does the evidence stop?
- Which claims are documented, which are stakeholder-reported, and which are assumptions?

#### Days 8–10: test causes and frame options

- What evidence would distinguish a semantic difference from a data-quality or timing difference?
- Are definitions different by design, by accident, or because of undocumented historical changes?
- Which consumers need a common baseline, and which require a separate metric?
- What would it cost and risk to document current variants, create a governed baseline, run a temporary reconciliation pilot, or centralize calculations?
- What are the mandatory constraints and what are preferences?
- Which choice is reversible, and which creates broad dependencies?
- What evidence could make the recommended option wrong?

#### Days 11–14: validate and report

- Have the relevant business owners validated the recorded definitions and examples?
- Have system owners confirmed the source and transformation map—or explicitly identified what they cannot confirm?
- Have security/compliance and assurance stakeholders stated what evidence they require?
- Which five architectural issues are most material, and what evidence supports each?
- What is the smallest useful next step that reduces uncertainty without creating an uncontrolled new copy or permanent workaround?
- Who owns each action, when will it be reviewed, and what would trigger a change in direction?

**Expected first-two-week assessment output:** a current-state inventory for the scoped systems and report path; a definition comparison; a stakeholder expectation table; an evidence/unknowns log; five prioritized architectural findings; and a short decision note or recommendation for the next assessment step. Do not claim enterprise-wide completeness if only one report path has been traced.

### 7.5 Practical case scenarios

#### Scenario A — A product team wants a new datastore

**Questions before agreeing:** What business capability and requirement does it serve? Which data will it hold? Is the data already available elsewhere? Who owns its meaning and quality? Which systems will produce and consume it? What latency, availability, growth, security, privacy, retention, and cost constraints apply? How will lineage, access, operations, and retirement be handled? What alternatives were considered?

**What could proceed without a full architecture review?** A bounded, non-production experiment may be appropriate when it uses approved data, has no new sensitive-data exposure or enterprise dependency, can be rolled back, and stays within established standards. Confirm local decision rights. A production datastore that duplicates authoritative data, creates a new cross-domain contract, changes regulated use, or is difficult to reverse should receive proportionate review.

**Reasoning:** do not block every experiment, but do not mistake a prototype for a production architecture decision.

#### Scenario B — A regulator requests lineage and nobody can produce it

The missing capability is the ability to trace a specified data output to its source data and transformations with evidence that can be reviewed. The first step is not necessarily buying a catalog tool. Select one high-priority statement or report, identify its owner and consumers, trace the path with system owners, record verified links and gaps, and agree on evidence standards and responsibility for maintaining lineage. Use the pilot to learn whether the gap is missing metadata, undocumented logic, unclear ownership, or a combination.

**Trade-off:** a small manual trace can provide immediate clarity but may not scale. It is a useful first step if its scope and transition to a maintained capability are explicit.

#### Scenario C — Two senior engineers propose conflicting designs

Do not decide by seniority or count of supporters. Ask each engineer to state the problem, assumptions, constraints, options, criteria, expected benefits, failure modes, and consequences for consumers and operations. Compare both designs against the same agreed criteria; identify evidence that could resolve disputed claims; check standards and decision rights; document the selected option and rejected alternatives. If the disagreement concerns an enterprise-wide or difficult-to-reverse decision, use the appropriate review/approval path.

**Reasoning:** seniority may provide useful experience, but it is not a substitute for evidence and accountability.

### 7.6 Industry exercise deliverables

Complete all of the following using the case:

1. Describe the five-system problem while separating verified facts, reported claims, and assumptions.
2. Produce a stakeholder expectation table with concern and acceptable evidence.
3. Create a first-two-weeks question plan and identify who should answer each question.
4. Compare the five systems and at least one priority report path; mark unknowns explicitly.
5. Identify five architectural problems, affected stakeholders, candidate causes, missing evidence, and first questions.
6. Write a decision note with at least three alternatives and a revisit trigger.

## 8. Practical scenarios and case-based reasoning

Use these as short written drills. For each, answer: **What is known? What is unknown? Who is affected? What evidence would you request? What is the smallest defensible next step?**

### Scenario 1 — A product team requests a new datastore

Avoid beginning with a preferred product. First clarify the requirement, data ownership, existing alternatives, consumers, lifecycle, controls, and constraints. A team-level experiment may proceed within established guardrails; a production choice with broad dependencies needs a decision proportionate to its impact.

### Scenario 2 — Lineage cannot be produced

Treat “no lineage” as a reported condition to verify. Choose a priority output and trace it end to end. The smallest useful step is a bounded, evidence-based trace plus a list of gaps, owners, and a plan for maintaining the trace—not an unsupported assertion that a tool purchase alone will solve it.

### Scenario 3 — Senior engineers disagree

Create a common comparison framework. Record assumptions, criteria, trade-offs, risk, affected consumers, and evidence. Seek a small experiment if it can safely distinguish options. Escalate based on decision rights and impact, not personality.

### Scenario 4 — Reports disagree but both teams say their numbers are correct

They may be correct for different definitions, source coverage, or time windows. Compare the business purpose and exact calculation before labeling either result wrong. The outcome may be one shared baseline plus clearly named variants rather than one universal metric.

### Scenario 5 — A proposed target design ignores current constraints

Ask how the organization transitions from current to target state, what dependencies and migration steps exist, and what happens during coexistence. A target architecture without transition reasoning is incomplete as a delivery guide. The first useful deliverable may be a phased roadmap with decision points, not a larger diagram.

## 9. Expected outputs or deliverables

Before moving to the next lesson, produce these artifacts:

- [ ] **Two-minute explanation:** recorded or written, suitable for a non-technical colleague.
- [ ] **Six-sentence system description:** what it holds, who uses it, where data enters, where it leaves, who is accountable, and what remains unknown.
- [ ] **Stakeholder expectation table:** stakeholder, concern, and evidence they would accept.
- [ ] **Decision note:** at least three alternatives, criteria, trade-offs, recommendation, risks, assumptions/unknowns, owner, and revisit trigger.
- [ ] **Banking case assessment:** definition comparison, initial assessment questions, prioritized findings, and evidence gaps.
- [ ] **Practice questions:** answers to the Topic 01 section of `practice-questions.md`, with incorrect answers corrected.

The banking assessment is an application of the lesson and should use illustrative assumptions only where evidence is unavailable. Keep unknown owners or missing lineage explicit; do not fabricate completeness.

## 10. Common mistakes and misconceptions

1. **“The architect chooses the technology.”** Technology may be part of the decision, but the choice must follow requirements, constraints, evidence, and trade-offs.
2. **“Architecture is the diagram.”** Diagrams communicate structure; the architecture also includes semantics, standards, decision rationale, ownership, constraints, and risks.
3. **“The target state is the answer.”** A target without current-state evidence, transition steps, ownership, and constraints is not a practical plan.
4. **“Every duplicate is bad.”** Some copies support justified latency, resilience, analytical, or operational needs. Evaluate purpose, controls, and lifecycle.
5. **“There must be one definition of every term.”** A shared baseline can be valuable, but different business decisions may require different measures. Make differences intentional and explicit.
6. **“Reports disagree, so one must be wrong.”** Different source coverage, timing, populations, or business rules can explain the difference. Investigate before deciding.
7. **“The architect can solve governance alone.”** Architecture can expose decision rights and propose processes, but accountable business and control owners must participate.
8. **“Documentation proves the system is correct.”** Documentation may be stale or inaccurate. Verify important claims against implementation and responsible owners.
9. **“A review is implementation.”** A review assesses and records findings; delivery teams still implement changes and demonstrate that they work.
10. **“Architecture finishes before delivery.”** Architecture decisions must be checked and revised as implementation and evidence evolve.
11. **“Assumptions are facts once written down.”** Label assumptions, owners, validation methods, and decision impact.
12. **“A high option score overrides mandatory constraints.”** It does not. A policy or safety constraint can rule out an option regardless of its total score.
13. **“The most senior person should decide.”** Decision rights, evidence, criteria, and accountability should determine the process.
14. **“Centralization always improves consistency.”** It can reduce duplicated logic but also increase dependencies and bottlenecks; it does not automatically resolve semantic disagreements.

## 11. Mastery criteria

You have mastered this lesson when you can demonstrate all of the following without relying on memorized slogans:

- Define data architecture, its purpose, scope, and deliverables accurately.
- Explain why an organization needs an architectural view and distinguish architecture from a diagram.
- Describe the Data Architect's responsibilities without turning the role into a product selector or implementation owner for every detail.
- Describe a known system in six sentences and mark unknowns explicitly.
- Trace a business request to data requirements, architecture decisions, implementation, and measurable outcome; trace backward to test whether a decision has a valid reason.
- Distinguish design, documentation, review, and implementation and explain how they interact.
- Identify stakeholder concerns and state what evidence each stakeholder would accept.
- Identify five likely architectural problems and distinguish observed symptoms from candidate causes.
- Frame a decision using context, constraints, options, criteria, trade-offs, recommendation, risks, assumptions, owner, and revisit trigger.
- Explain how reversibility, uncertainty, and enterprise-wide consequences affect the timing and level of a decision.
- Apply the concepts to the banking/customer-data scenario without presenting invented details as verified facts.
- Defend the recommendation while acknowledging evidence that could change it.

Conceptual understanding is the ability to define and explain. Practical architectural competence is the ability to use evidence to analyze an ambiguous situation, compare alternatives, record a defensible decision, accept challenge, and revise the decision when the evidence changes.

## 12. Completion gate

Do not mark this lesson complete until each item is satisfied:

- [ ] The two-minute explanation has been delivered and a reviewer judged it clear.
- [ ] The six-sentence system description is complete and explicitly records unknowns.
- [ ] The stakeholder expectation table is complete and reviewed.
- [ ] The decision note includes at least three genuine alternatives, explicit trade-offs, risks, and a revisit trigger; a reviewer has challenged it.
- [ ] The banking case includes the stakeholder expectations and first-two-weeks assessment questions.
- [ ] Topic 01 practice questions have been answered and incorrect answers corrected.
- [ ] Facts, reported claims, and assumptions are distinguishable throughout the submitted artifacts.

**Completion rule:** if a required fact is unknown, mark it unknown and identify how it will be validated. Do not invent evidence to pass the gate. Once complete, carry the notes, worked scenario, decision record, and open questions into `module-2d1-notes.md` as prescribed by the module roadmap. The next lesson is `02-data-architecture-vs-data-engineering-and-solution-architecture.md`; its full comparison belongs there, not in this lesson.

---

## Quick self-check

Before you stop, answer aloud:

1. Why is a diagram not the same thing as an architecture?
2. What is the difference between a symptom and a candidate root cause?
3. Which evidence would you need before recommending a shared definition of “active customer”?
4. How can a local decision create enterprise-wide cost or risk?
5. What would make you reverse your recommendation?

If your answers name concrete evidence, stakeholders, consequences, and decision criteria—not just technology preferences—you are applying the lesson's intended reasoning discipline.
