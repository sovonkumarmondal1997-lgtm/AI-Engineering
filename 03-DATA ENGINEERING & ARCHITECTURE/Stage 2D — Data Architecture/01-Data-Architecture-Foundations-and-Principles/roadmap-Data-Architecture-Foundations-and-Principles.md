# Roadmap — Module 2D.1: Data Architecture Foundations and Principles

This is the learning roadmap for the first module of Stage 2D, **Data
Architecture**. It tells you **what** to learn, **in what order**, **how** to
learn each topic, and **how to prove to yourself** that you have learned it
before you move on.

Stages 2, 2B and 2C taught you to build pipelines, tables, streams and
platforms. This stage asks a different question: *who decides what should be
built, on what basis, and how is that decision made, recorded and defended?*
A Data Architect is judged less on what they can build and more on the quality
of the decisions they make and the clarity with which they explain them.

> **Repository note.** The six topic files and `practice-questions.md` in this
> module currently exist but are empty, and the Stage 2D overview files are
> empty too. This roadmap is therefore the first written statement of the
> module's scope. It defines the learning sequence for each topic file; it does
> not claim that any topic file already contains this material. Where a topic
> file will need to name specific frameworks, that is flagged in Topic 06 and
> must be confirmed when the file is written.

---

## 1. Roadmap overview

### 1.1 What this module is

**Data Architecture Foundations and Principles** is the conceptual and
professional base of the whole stage. It covers what data architecture is,
what a Data Architect does and does not do, how that role differs from its
neighbours, how business capabilities and domains drive data ownership, how
principles and quality attributes turn goals into testable criteria, how
architecture is governed over its lifecycle, and how frameworks and reference
models help without dictating.

### 1.2 Why it sits first in Stage 2D

Every later module in this stage (requirements and decisions, patterns,
modeling, storage, integration, platform, cloud, streaming, governance,
metadata, resilience, performance, serving, documentation, case studies)
assumes the vocabulary, role boundaries and decision discipline built here.
Without this module, later topics become a catalogue of technologies instead
of a set of decisions with reasons.

### 1.3 How it contributes to the learning path

| This module provides | Later modules that rely on it |
| --- | --- |
| Role clarity and architectural vocabulary | All modules (shared language) |
| Business capabilities, domains, ownership | 2D.3 patterns (data mesh), 2D.10 governance, 2D.11 metadata and master data |
| Principles and quality attributes | 2D.2 requirements, 2D.12 resilience, 2D.13 performance and cost |
| Lifecycle and governance | 2D.2 decision records, 2D.15 reviews and operating model |
| Frameworks and reference models | 2D.3 reference architectures, 2D.7 platform, 2D.15 documentation |
| Current-state inventory (project) | 2D.2 requirements, 2D.3 patterns, 2D.15 current-to-target review |

### 1.4 Professional capabilities to develop

By the end of the module you should be able to:

- Explain data architecture, its scope and its deliverables to technical and
  business audiences.
- Place a decision correctly among data architecture, data engineering and
  solution architecture, and say who leads, contributes, reviews or approves.
- Identify business capabilities and domains, and assign defensible data
  ownership.
- Write architecture principles that are actionable, and quality attribute
  requirements that are measurable.
- Describe an architecture lifecycle and design a governance process that
  supports delivery rather than blocking it.
- Evaluate a framework or reference model for a specific organisation and adapt
  it instead of copying it.
- Produce a reviewable current-state data architecture inventory in which facts,
  reported information and assumptions are kept apart.

### 1.5 Understanding versus architectural competence

| | Understanding concepts | Making and defending decisions |
| --- | --- | --- |
| Question answered | "What is this?" | "What should we do here, and why?" |
| Evidence | Correct definitions, accurate comparisons | A written decision with context, options, criteria, trade-offs, risks, owner |
| Typical failure | Reciting terms without applying them | Choosing a favourite technology and justifying it afterwards |
| Test | Explain it to a peer | Defend it to a sceptical reviewer who has different priorities |

**Foundational understanding** is being able to define, distinguish and give
examples. **Practical architectural competence** is being able to take an
ambiguous organisational situation, gather evidence, frame the decision, weigh
trade-offs against stated criteria, record the result, and revise it when the
evidence changes. This module aims at competence, and uses understanding as the
first step.

### 1.6 Expected level at completion

You will not be a senior enterprise architect after one module. You will be
able to take part credibly in an architecture review, to produce a
current-state assessment that others can review, and to write a short decision
record with real alternatives and explicit trade-offs. You will know which
questions to ask and which claims to challenge.

---

## 2. Prerequisites

### 2.1 Essential prerequisites

- Completion of the Stage 2, 2B and 2C data engineering material to the level of
  having built or read a batch pipeline, a warehouse/lakehouse table design and
  a streaming flow end to end. You need concrete systems in mind, because
  architecture reasons *about* them.
- Working SQL and a basic understanding of relational and analytical stores
  (Stage 2 SQL and modeling topics).
- Ability to read and draw simple box-and-arrow diagrams of data flow.
- Ability to write clear structured prose (a one-page decision note).

### 2.2 Helpful prior knowledge

- Exposure to a real organisation's systems (any employer, project or
  case study) so abstract terms attach to something.
- Familiarity with Stage 2C module 08 (data platform architecture and data
  products), especially data mesh and data products. This module treats the same
  ideas at a higher, organisational level.
- Basic awareness of data protection and regulatory concerns (details come in
  module 2D.10).

### 2.3 Concepts you will learn during this module

- Business capability modeling and domain boundaries.
- Architecture principles, quality attributes and measurable criteria.
- Governance forums, decision rights and exception handling.
- The vocabulary of frameworks and reference models.

No prior certification, enterprise architecture framework experience or
modeling-tool experience is required.

---

## 3. Learning strategy and progression

### 3.1 The four levels

| Level | You should understand | You should practise | You should demonstrate |
| --- | --- | --- | --- |
| **1. Beginner** | Terminology, purpose, scope, simple examples | Defining terms in your own words; labelling examples | Accurate explanation without notes |
| **2. Intermediate** | How concepts relate; how they differ from neighbours | Comparing, mapping and classifying on realistic scenarios | A correct analysis of a described organisation |
| **3. Advanced** | Trade-offs, risks, failure modes, conflicting interests | Defining principles, scoring options, challenging weak decisions | A defended decision with explicit trade-offs and a revisit trigger |
| **4. Industry application** | How the concept behaves in a real, messy organisation | Applying it to a banking/financial-services scenario and producing artefacts | A reviewable artefact that a stakeholder could act on |

Advanced does **not** mean more terminology. It means more reasoning: what is
the alternative, what does this cost, who loses, what evidence supports it,
and what would make us change our mind.

### 3.2 The architect's study loop (use for every topic)

```text
Read → Restate in your own words → Apply to a scenario → Compare with a
neighbour concept → Decide and record → Have it challenged → Revise
```

1. **Read** the topic file once, fully.
2. **Restate** its core ideas in three or four sentences without looking.
3. **Apply** them to one scenario (use the shared scenario in Section 7.2).
4. **Compare** with the neighbouring concept named in the topic.
5. **Decide and record** a short answer: context, choice, alternatives,
   consequences.
6. **Have it challenged** by a peer, a mentor, or by yourself in the role of a
   sceptical reviewer.
7. **Revise** and keep the final version in your notes.

### 3.3 Suggested schedule

About **3 weeks at 6–8 hours per week**. Reasoning and writing take time.

| Week | Work |
| --- | --- |
| 1 | Topic 01 (what data architecture is) · Topic 02 (vs engineering and solution architecture) · Topic 03 (capabilities, domains, ownership) |
| 2 | Topic 04 (principles and quality attributes) · Topic 05 (lifecycle and governance) |
| 3 | Topic 06 (frameworks and reference models) · practice questions · project |

### 3.4 Working notes

Keep a `module-2d1-notes.md` (outside the repository's topic files) with, for
each topic: a one-paragraph summary, one worked scenario, one decision record,
and your open questions. These feed the project.

---

## 4. Detailed learning roadmap for each topic file

Each topic below uses the same twelve sub-headings. Levels are cumulative: do
Beginner before Intermediate, and so on.

---

### Module 1 — [What data architecture is and what data architects do](01-what-data-architecture-is-and-what-data-architects-do.md)

#### 1.1 Learning objective

Explain data architecture's meaning, purpose and scope; describe the Data
Architect's responsibilities and deliverables; and show how business needs flow
through data requirements and architecture decisions into implementation.

#### 1.2 Why this topic matters in real-world Data Architecture

Organisations build data systems incrementally, team by team. Without an
architectural view, each local decision is reasonable and the whole becomes
inconsistent, duplicated, costly and hard to govern. The Data Architect
provides the connecting view between what the business needs and what is
built, and makes the trade-offs explicit.

#### 1.3 Prerequisite knowledge

Stage 2–2C data engineering experience; none from this module.

#### 1.4 Beginner-level learning sequence

1. **Define** data architecture: the structure of an organisation's data,
   how it is stored, moved, governed and used, in service of business goals.
2. **Learn the scope:** data assets, models, storage, integration, platforms,
   governance, quality, security. Note what is *not* in scope (application
   code, individual pipeline logic).
3. **List the role's responsibilities:** understand needs, define structure
   and standards, make and record decisions, review designs, communicate,
   align with governance.
4. **List typical deliverables:** current-state and target-state views,
   principles, standards, reference architectures, decision records, roadmaps.
5. **Questions to answer:** Why does an organisation need an architect at all?
   What is the difference between a design and an architecture?
6. **Exercise:** For a system you know, write six sentences: what it holds,
   who uses it, where data enters, where it leaves, who is accountable, and
   what you do not know.

**Ability to demonstrate:** explain data architecture and the role's
deliverables in two minutes to a non-technical colleague.

#### 1.5 Intermediate-level learning sequence

1. **Trace the chain:** business objective → business requirement → data
   requirement → architecture decision → implementation → outcome. Practise
   going both directions.
2. **Distinguish four activities:** *design* (creating structure),
   *documentation* (recording it), *review* (assessing it), *implementation*
   (building it). Note who normally does each.
3. **Identify stakeholders** and their expectations: executives (cost, risk,
   value), business owners (capability), engineers (feasibility, clarity),
   security/compliance (control), operations (supportability), auditors
   (evidence).
4. **Classify typical problems:** duplicated data, unclear ownership, point-to-
   point integration sprawl, inconsistent definitions, uncontrolled copies.
5. **Questions to answer:** Which stakeholder would object to a given
   decision, and why? What artefact would you show each of them?
6. **Exercise:** Given a one-page organisation description, list five
   architectural problems, the stakeholder affected by each, and the first
   question you would ask.

**Ability to demonstrate:** map a business request through to the data
architecture decisions it implies.

#### 1.6 Advanced-level learning sequence

1. **Separate symptoms from causes.** "Reports disagree" is a symptom;
   unclear ownership, divergent definitions or unmanaged copies are candidate
   causes. Practise proposing and testing hypotheses.
2. **Frame a decision:** problem, context, constraints, options, criteria,
   trade-offs, recommendation, risks.
3. **Handle uncertainty:** state assumptions, decide what must be validated
   first, and identify reversible versus irreversible decisions.
4. **Balance local and enterprise optimisation:** when a team's best choice is
   not the organisation's best choice, and how to resolve it.
5. **Questions to answer:** What would make you reverse this decision? What is
   the cost of being wrong? Which decision can wait?
6. **Exercise:** Write a one-page decision note with three real alternatives for
   a problem from the intermediate exercise.

**Ability to demonstrate:** a decision note a reviewer can challenge on its
merits rather than on missing information.

#### 1.7 Industry-application exercises

- Describe how a Data Architect would approach a bank that has accumulated
  customer data in five systems with different definitions of "active
  customer".
- Produce a stakeholder expectation table (stakeholder, concern, evidence they
  would accept) for that problem.
- Write the questions you would ask in the first two weeks of an assessment.

#### 1.8 Practical scenarios and case-based reasoning

1. *Scenario:* A product team wants a new datastore. Which architecture
   questions do you ask before agreeing, and what could you accept without
   review?
2. *Scenario:* Regulators request a data lineage statement and nobody can
   produce one. What architectural capability is missing, and what is the
   smallest useful first step?
3. *Scenario:* Two senior engineers propose conflicting designs. How do you
   structure the comparison so the decision is not decided by seniority?

#### 1.9 Expected outputs or deliverables

- A two-minute spoken explanation (recorded or written).
- A stakeholder expectation table.
- One decision note with at least three alternatives.
- Answers to the Topic 01 section of [`practice-questions.md`](practice-questions.md).

#### 1.10 Common mistakes and misconceptions

- Treating the architect as the person who picks technology products.
- Equating architecture with diagrams; diagrams are one artefact, decisions are
  the substance.
- Producing an ideal design with no regard for current state or constraints.
- Assuming architecture is a one-time activity completed before delivery.

#### 1.11 Mastery criteria

- Defines the discipline, scope and deliverables accurately and distinctly from
  nearby roles.
- Traces a business request to architectural decisions and back.
- Names stakeholders and the evidence each would require.
- Writes a decision note with real alternatives and explicit trade-offs.

#### 1.12 Completion gate

- [ ] Two-minute explanation given and judged clear by a reviewer.
- [ ] Stakeholder table and decision note completed and reviewed.
- [ ] Topic 01 practice questions answered; incorrect answers corrected.

---

### Module 2 — [Data architecture vs data engineering and solution architecture](02-data-architecture-vs-data-engineering-and-solution-architecture.md)

#### 2.1 Learning objective

Distinguish the purpose, scope, authority, deliverables and accountability of
data architecture, data engineering and solution architecture; allocate
responsibility for a decision; and describe how the disciplines collaborate
without forming silos.

#### 2.2 Why this topic matters in real-world Data Architecture

Most architecture friction is boundary friction: duplicated effort, decisions
nobody owns, or an architect who is an obstacle. Clear, respectful boundaries
let each discipline make good decisions quickly and escalate only what needs it.

#### 2.3 Prerequisite knowledge

Module 1 (role and scope). Practical data engineering experience.

#### 2.4 Beginner-level learning sequence

1. **Define each discipline in one sentence:**
   - *Data architecture:* structure, standards and decisions for data across
     systems and the organisation.
   - *Data engineering:* building, operating and improving data pipelines and
     data platforms.
   - *Solution architecture:* designing how a specific solution, end to end
     across components, meets a defined business need.
2. **Contrast scope:** enterprise/cross-system vs platform/pipeline vs
   single solution.
3. **Contrast typical deliverables:** principles and reference models vs
   running pipelines and code vs a solution design.
4. **Questions to answer:** Which of the three would choose a partitioning
   scheme? Which would choose an enterprise data-sharing standard?
5. **Exercise:** Sort twenty example tasks into the three disciplines and mark
   any that you think belong to more than one.

**Ability to demonstrate:** give a correct, concise definition and typical
deliverable for each discipline.

#### 2.5 Intermediate-level learning sequence

1. **Compare decision authority:** who decides, who is consulted, who is
   informed, who approves. Build a RACI-style table for common decisions.
2. **Map collaboration points:** requirements, design, review, build,
   operate, change.
3. **Identify overlaps:** data modeling, integration design, technology
   selection, non-functional requirements, standards.
4. **Identify conflicts:** architect specifies too much detail; engineers
   bypass standards; solution architecture optimises one project.
5. **Questions to answer:** Where does a standard end and a project design
   begin? Who owns a cross-team data contract?
6. **Exercise:** Produce a RACI table for six decisions in a realistic project
   and justify any shared accountability.

**Ability to demonstrate:** allocate roles correctly for a described decision
and explain the reasoning.

#### 2.6 Advanced-level learning sequence

1. **Resolve responsibility conflicts** using principles: decide at the lowest
   level that has the information and accountability; escalate only
   enterprise-wide, irreversible or high-risk decisions.
2. **Communicate boundaries without silos:** shared artefacts, joint
   reviews, published guidance, explicit escalation paths, architects who
   engage in delivery.
3. **Handle role ambiguity** in small organisations where one person holds
   multiple roles: separate the *hats* even if not the people.
4. **Avoid failure modes:** ivory-tower architecture, architecture by
   committee, unowned decisions.
5. **Questions to answer:** How would you tell if boundaries are working? What
   signals indicate silo formation?
6. **Exercise:** Write a one-page working agreement between the three
   disciplines for a data programme.

**Ability to demonstrate:** a working agreement that a delivery team would
actually follow.

#### 2.7 Industry-application exercises

- Apply the RACI to the banking scenario in Section 7: customer onboarding data
  feeding a risk platform.
- Review a hypothetical design in which the data engineers have chosen a
  streaming technology; state what is a team decision and what is an
  architecture concern.
- Draft an escalation path for a disagreement between the disciplines.

#### 2.8 Practical scenarios and case-based reasoning

1. *Scenario:* A solution architect proposes a point-to-point integration for
   a deadline. The data architect objects. Who decides, and on what grounds?
2. *Scenario:* A data engineering team has built a reusable ingestion framework
   that now acts as a de facto standard. How should that be governed?
3. *Scenario:* A start-up has one person doing all three roles. How do you keep
   the decisions honest?

#### 2.9 Expected outputs or deliverables

- A comparison table of the three disciplines.
- A RACI-style decision table.
- A one-page working agreement.
- Answers to Topic 02 practice questions.

#### 2.10 Common mistakes and misconceptions

- Treating the three as a hierarchy rather than collaborating disciplines.
- Assuming data architecture means "senior data engineering".
- Letting architects design down to implementation detail.
- Allowing engineers to define enterprise standards by default.

#### 2.11 Mastery criteria

- Distinguishes scope, authority, deliverables and accountability accurately.
- Assigns decision roles consistently and can defend them.
- Names overlap areas and a way to resolve conflicts.

#### 2.12 Completion gate

- [ ] Comparison table, RACI table and working agreement complete.
- [ ] A reviewer cannot find a decision in your RACI without an accountable role.
- [ ] Topic 02 practice questions answered and corrected.

---

### Module 3 — [Business capabilities, domains and data ownership](03-business-capabilities-domains-and-data-ownership.md)

#### 3.1 Learning objective

Identify business capabilities and domains, relate them to systems and data
assets, and define and document data ownership and stewardship, including
cross-domain dependencies and conflicts.

#### 3.2 Why this topic matters in real-world Data Architecture

Data exists to serve business activity. Organising architecture around
business capabilities and domains, rather than around today's systems, makes
ownership meaningful, supports governance and gives a stable structure through
technology change.

#### 3.3 Prerequisite knowledge

Modules 1–2. Awareness of data mesh and data products from Stage 2C module 08.

#### 3.4 Beginner-level learning sequence

1. **Define a business capability:** what the organisation can do (for
   example, "manage customer onboarding"), independent of how or with which
   system.
2. **Define a business domain:** a bounded area of business knowledge and
   responsibility with a consistent vocabulary.
3. **Define the roles:** data *owner* (accountable), *steward* (looks after
   quality and definitions), *producer*, *consumer*.
4. **Define the relationships:** capability → process → system → data asset.
5. **Questions to answer:** Why is "the CRM team owns customer data" a weak
   statement? What is the difference between owner and steward?
6. **Exercise:** For a bank, list ten capabilities and three domains. Assign
   each capability to a domain.

**Ability to demonstrate:** distinguish capability, process, domain, system and
data asset, with an example of each.

#### 3.5 Intermediate-level learning sequence

1. **Build a capability map** at two levels (top-level and one level down).
2. **Map capabilities to systems and data assets** in a matrix; identify gaps
   (capability with no system) and overlaps (several systems for one
   capability).
3. **Identify domain boundaries** using vocabulary: where the same word means
   different things, there is probably a boundary.
4. **Document ownership** in a simple register: asset, domain, owner,
   steward, producers, consumers, status.
5. **Identify cross-domain dependencies:** who depends on whose data, and how
   changes are communicated.
6. **Questions to answer:** Where is the "customer" defined? Who is hurt if its
   definition changes?
7. **Exercise:** Produce a capability-to-system-to-asset map for part of the
   banking scenario and an ownership register for ten assets.

**Ability to demonstrate:** a traceable chain from capability to owner for each
significant data asset.

#### 3.6 Advanced-level learning sequence

1. **Resolve ownership conflicts:** shared data, derived data, data owned by
   one domain but produced by another, data without a natural owner.
2. **Decide ownership using criteria:** who creates it, who is accountable for
   its meaning, who bears the risk of error, who can fix it.
3. **Analyse enterprise-wide boundaries:** over-large domains (too general to
   own), over-small domains (coordination overhead), boundaries misaligned with
   organisation structure.
4. **Design the documentation:** ownership register, domain relationship map,
   decision log for contested ownership.
5. **Questions to answer:** When is shared ownership acceptable? What happens
   when an owner leaves or a unit is reorganised?
6. **Exercise:** Resolve three deliberately contested ownership cases and
   record the decisions with rationale.

**Ability to demonstrate:** a defended ownership decision for contested data,
recorded so it can be revisited.

#### 3.7 Industry-application exercises

- Build a capability and domain view for the banking scenario; show which
  domains produce and which consume customer, account and transaction data.
- Create an ownership register for a representative set of data assets, marking
  unknown owners explicitly.
- Identify the three highest-risk cross-domain dependencies.

#### 3.8 Practical scenarios and case-based reasoning

1. *Scenario:* "Customer address" is entered in onboarding, changed in the
   mobile app and corrected by operations. Who owns it?
2. *Scenario:* A risk team creates a derived "customer risk score" used by
   marketing. Who is accountable for it?
3. *Scenario:* A merger brings a second company with its own definition of
   "account". How do you identify the boundary issue?

#### 3.9 Expected outputs or deliverables

- Capability map and domain map.
- Capability–system–asset matrix.
- Ownership register.
- Ownership decision log for contested cases.
- Answers to Topic 03 practice questions.

#### 3.10 Common mistakes and misconceptions

- Mapping systems instead of capabilities.
- Naming a team as owner instead of an accountable role.
- Confusing steward and owner.
- Forcing one global definition where bounded definitions are legitimate.
- Treating the map as final instead of maintained.

#### 3.11 Mastery criteria

- Produces a consistent capability, domain and ownership view.
- Traces any data asset to an accountable owner or marks it unknown.
- Resolves conflicts with stated criteria.

#### 3.12 Completion gate

- [ ] Capability map, matrix and register complete.
- [ ] Every register entry has an owner or an explicit "unknown".
- [ ] Three contested cases resolved and recorded.
- [ ] Topic 03 practice questions answered and corrected.

---

### Module 4 — [Architecture principles and quality attributes](04-architecture-principles-and-quality-attributes.md)

#### 4.1 Learning objective

Define actionable architecture principles; connect business drivers and
constraints to quality attributes; express quality attributes as measurable
requirements; analyse conflicts between them; and evaluate and justify
deviations.

#### 4.2 Why this topic matters in real-world Data Architecture

Principles keep many independent decisions consistent. Quality attributes make
"good" concrete. Without measurable criteria, architecture debates become
opinion contests, and trade-offs are made implicitly rather than deliberately.

#### 4.3 Prerequisite knowledge

Modules 1–3. Basic familiarity with non-functional requirements.

#### 4.4 Beginner-level learning sequence

1. **Define an architecture principle:** a durable, shared statement that
   guides decisions, with a rationale and implications.
2. **Recognise a useful principle:** it is specific enough to decide between
   options, has a rationale, states implications, and could be violated.
3. **Define quality attributes:** reliability, availability, scalability,
   performance, security, privacy, interoperability, maintainability, cost
   efficiency, and others relevant to data.
4. **Define business driver, constraint, assumption** and distinguish them.
5. **Questions to answer:** Why is "use best-of-breed technology" a weak
   principle? What makes "data is owned by a named domain" actionable?
6. **Exercise:** Rewrite five vague statements into principle form
   (statement, rationale, implications).

**Ability to demonstrate:** identify the quality attribute at stake in a
described requirement.

#### 4.5 Intermediate-level learning sequence

1. **Translate objectives to principles:** business objective → principle →
   implication for design.
2. **Translate qualities to measures:** for example, availability as a target
   percentage over a window, freshness as a maximum data age, recovery as a
   maximum acceptable data loss and recovery time. Include how it will be
   measured and over what period.
3. **Link constraints and assumptions** to qualities (for example a regulatory
   constraint implying privacy and retention requirements).
4. **Evaluate a proposed architecture** against a set of principles and
   attributes using a simple scorecard with evidence.
5. **Questions to answer:** What would you measure to know this attribute is
   met? Which principle does this option violate?
6. **Exercise:** Define six measurable quality attribute requirements for the
   banking scenario and evaluate two candidate designs against them.

**Ability to demonstrate:** a measurable requirement set and an evidence-based
evaluation.

#### 4.6 Advanced-level learning sequence

1. **Analyse trade-offs:** performance versus cost, availability versus
   consistency, openness versus security, agility versus control, privacy
   versus analytical usefulness.
2. **Prioritise:** agree which attributes dominate for which data and
   capability; not every asset needs the same level.
3. **Handle exceptions:** a deviation record with the principle, the reason,
   the risk, the compensating control, an owner and an expiry or review date.
4. **Detect principle decay:** principles that nobody can apply, that conflict
   with each other, or are routinely bypassed.
5. **Questions to answer:** When should an exception be refused? Which two of
   your principles conflict, and which wins and when?
6. **Exercise:** Write a principles set of at most eight, resolve one conflict
   between two of them, and write one exception record.

**Ability to demonstrate:** defend a trade-off by showing the attribute
priorities, evidence and accepted risk.

#### 4.7 Industry-application exercises

- Produce a principles set and measurable quality targets for a bank's customer
  and transaction data, marking targets that are illustrative assumptions.
- Evaluate a proposal to copy sensitive data into an analytics sandbox against
  the principles.
- Write an exception record for a legitimate, time-limited deviation.

#### 4.8 Practical scenarios and case-based reasoning

1. *Scenario:* The business wants real-time dashboards; the platform team
   warns of cost and complexity. Which attributes conflict and how do you
   decide?
2. *Scenario:* A team requests an exception to the "single system of record"
   principle. Under what conditions do you approve?
3. *Scenario:* An audit finds principles that nobody knew existed. What does
   that tell you about the governance of principles?

#### 4.9 Expected outputs or deliverables

- A principles set (statement, rationale, implications).
- A quality attribute requirements table with measures.
- A scored evaluation of two options.
- An exception record.
- Answers to Topic 04 practice questions.

#### 4.10 Common mistakes and misconceptions

- Writing principles that are slogans.
- Listing quality attributes without measures.
- Treating all attributes as equally important.
- Granting exceptions informally and permanently.
- Setting precise-looking numbers without evidence.

#### 4.11 Mastery criteria

- Writes principles that decide between real options.
- States measurable quality targets, with the basis for each.
- Explains and justifies a trade-off between conflicting attributes.

#### 4.12 Completion gate

- [ ] Principles set reviewed; each has rationale and implications.
- [ ] Quality targets are measurable and have a stated measurement method.
- [ ] One trade-off analysis and one exception record completed.
- [ ] Topic 04 practice questions answered and corrected.

---

### Module 5 — [Data architecture lifecycle and governance](05-data-architecture-lifecycle-and-governance.md)

#### 5.1 Learning objective

Describe the data architecture lifecycle; design an architecture governance
process with clear decision rights, standards, reviews, exceptions and change
control; and evaluate whether governance supports or obstructs delivery.

#### 5.2 Why this topic matters in real-world Data Architecture

Architecture that is not governed drifts; governance that is heavy gets
bypassed. The lifecycle provides the sequence of activities; governance
provides the decision rights and the feedback that keep decisions consistent
without becoming a bottleneck.

#### 5.3 Prerequisite knowledge

Modules 1–4. Module 4's principles and exception handling are used directly.

#### 5.4 Beginner-level learning sequence

1. **List lifecycle stages:** discover and assess current state; analyse
   requirements; design target state; evaluate and approve; implement and
   align; operate and monitor; change and improve.
2. **Define governance:** who has the authority to decide what, how
   decisions are recorded, and how compliance is checked.
3. **Define standards, policies, guidelines** and distinguish mandatory from
   advisory.
4. **Questions to answer:** What is the difference between a standard and a
   guideline? Why does a decision need a record?
5. **Exercise:** Draw the lifecycle for a single change (new data source) and
   mark the artefact produced at each stage.

**Ability to demonstrate:** name lifecycle stages and the output of each.

#### 5.5 Intermediate-level learning sequence

1. **Current-state assessment and target-state design:** inputs, outputs,
   and how the gap drives a roadmap (details of the assessment are practised in
   the project).
2. **Decision rights:** which decisions are local, which need review, which
   need approval; who sits on the review forum and why.
3. **Review mechanics:** what is submitted, what criteria are applied
   (principles, quality attributes), what outcomes are possible (approve,
   approve with conditions, reject, defer).
4. **Conformance:** how implemented systems are checked against the approved
   design; how drift is detected.
5. **Decision records and exceptions:** a lightweight record format and
   registry.
6. **Questions to answer:** Which changes must go to review and which must
   not? How long should a review take?
7. **Exercise:** Define a three-tier decision model (local, reviewed,
   escalated) with examples, and draw the review flow.

**Ability to demonstrate:** a governance flow with explicit decision rights.

#### 5.6 Advanced-level learning sequence

1. **Design for proportionality:** light touch for low-risk, reversible
   changes; rigorous for high-risk, irreversible or enterprise-wide ones.
2. **Measure governance:** review turnaround time, proportion of changes
   reviewed, exception counts and age, conformance findings, and delivery
   teams' feedback.
3. **Escalation and conflict:** how disagreements between architecture and
   delivery are resolved, with time limits.
4. **Continuous improvement:** retire stale standards, update principles from
   exceptions, learn from incidents.
5. **Failure modes:** rubber-stamp reviews, gatekeeping, late engagement,
   unmaintained standards.
6. **Questions to answer:** How would you know governance is slowing delivery?
   Which standards should you remove?
7. **Exercise:** Evaluate a described governance process, identify three
   failure modes and propose changes with measures.

**Ability to demonstrate:** design and critique a governance process using
evidence.

#### 5.7 Industry-application exercises

- Design the architecture review process for a bank's data programme, including
  regulator-driven change.
- Define the contents of a decision record and exception register.
- Choose five governance measures and describe how you would collect them.

#### 5.8 Practical scenarios and case-based reasoning

1. *Scenario:* A team ships first and asks for architecture approval afterwards.
   What does this indicate and how do you respond?
2. *Scenario:* Review queues take six weeks. Identify likely causes and fixes.
3. *Scenario:* Ten exceptions to the same standard have been approved. What do
   you change?

#### 5.9 Expected outputs or deliverables

- Lifecycle diagram with artefacts.
- Decision-rights table.
- Review process flow and a decision record template.
- Governance measures list.
- Answers to Topic 05 practice questions.

#### 5.10 Common mistakes and misconceptions

- Treating governance as approval gates only.
- Applying the same rigour to every change.
- Engaging after design is complete.
- Writing standards that cannot be checked.
- Not recording decisions, so they are re-argued.

#### 5.11 Mastery criteria

- Describes the lifecycle and artefacts accurately.
- Designs proportionate governance with clear decision rights.
- Critiques a process using measurable indicators.

#### 5.12 Completion gate

- [ ] Lifecycle diagram, decision-rights table and record template complete.
- [ ] Governance critique reviewed by a peer.
- [ ] Topic 05 practice questions answered and corrected.

---

### Module 6 — [Enterprise data architecture frameworks and reference models](06-enterprise-data-architecture-frameworks-and-reference-models.md)

#### 6.1 Learning objective

Explain the purpose of frameworks and reference models; distinguish a
framework, reference architecture, reference model, standard and blueprint;
evaluate and adapt a framework for a particular organisation; and use reference
architectures as guidance rather than prescription.

#### 6.2 Why this topic matters in real-world Data Architecture

Frameworks give structure and a common language, saving an organisation from
inventing everything. Misused, they produce documentation for its own sake.
Competence here is knowing what a framework offers, what it costs, and which
part is worth adopting.

#### 6.3 Prerequisite knowledge

Modules 1–5.

> **Scope flag.** The repository currently names no specific framework or
> reference model anywhere in the course material, and the Topic 06 file is
> empty. This roadmap therefore teaches the *method* for evaluating frameworks
> and uses categories rather than asserting repository coverage. When the topic
> file is written, it should name the frameworks it covers (for example, widely
> known enterprise architecture frameworks and data management reference
> models), and this section should then be updated to refer to them by name.
> Until then, do not treat any named framework as a required element of this
> module.

#### 6.4 Beginner-level learning sequence

1. **Define each term, with an example of the kind of thing it is:**
   - *Framework:* a structured approach and vocabulary for organising
     architecture work (concerns, stakeholders, views, process).
   - *Reference model:* an abstract set of concepts and relationships that
     establishes common language.
   - *Reference architecture:* a reusable, more concrete architecture template
     for a class of problem.
   - *Standard:* a mandatory or agreed specification.
   - *Implementation blueprint:* a concrete design for a specific
     implementation.
2. **Learn the vocabulary of views:** stakeholder, concern, viewpoint, view.
3. **Questions to answer:** Which of the five terms is most abstract? Which is
   most specific? Can a reference architecture be a standard?
4. **Exercise:** Classify ten described artefacts into the five categories and
   justify each.

**Ability to demonstrate:** use the five terms correctly and consistently.

#### 6.5 Intermediate-level learning sequence

1. **See how a framework structures concerns:** stakeholders, viewpoints,
   views, process steps, deliverables.
2. **See how a reference model gives shared language:** map your organisation's
   terms to the model's terms.
3. **Evaluate suitability** with criteria: fit to problem, effort to adopt,
   skills required, flexibility, evidence of use, compatibility with existing
   practices, regulatory alignment.
4. **Identify benefits and limits:** consistency and completeness against
   overhead, abstraction and risk of ceremony.
5. **Questions to answer:** Which parts of a framework would a team of ten
   people actually use?
6. **Exercise:** Choose two candidate frameworks or reference models (from
   those your topic file names, or from material you source yourself) and
   compare them on your criteria for the banking scenario.

**Ability to demonstrate:** a structured, evidence-based comparison of two
options.

#### 6.6 Advanced-level learning sequence

1. **Adapt to context:** organisation size, industry, maturity, regulatory
   obligations, technical constraints. Decide what to adopt, adapt, defer or
   ignore, and record why.
2. **Avoid rigid templates:** use the framework to prompt questions, not to
   fill forms; keep only artefacts that someone will use.
3. **Use reference architectures as guidance:** state the deviations from the
   reference architecture, and the reason for each.
4. **Handle misalignment:** the framework's vocabulary conflicts with the
   organisation's; how to bridge it without renaming everything.
5. **Questions to answer:** What is the minimum viable use of this framework?
   Which artefact would you drop first?
6. **Exercise:** Produce a one-page adoption plan: what is adopted, adapted,
   deferred, and the measures of whether it helps.

**Ability to demonstrate:** a tailored adoption plan and a deviation record
against a reference architecture.

#### 6.7 Industry-application exercises

- Prepare an adoption recommendation for a mid-sized bank with limited
  architecture staff.
- Compare how the recommendation would change for a large regulated group and
  for a start-up.
- Review a reference architecture and list three deviations a real project
  would justifiably make.

#### 6.8 Practical scenarios and case-based reasoning

1. *Scenario:* Leadership wants "full framework compliance". What do you ask
   first, and what do you propose?
2. *Scenario:* A project team says the reference architecture is too heavy.
   How do you evaluate that claim?
3. *Scenario:* Two business units use different vocabularies for the same
   concepts. How can a reference model help, and what are its limits?

#### 6.9 Expected outputs or deliverables

- Term classification table.
- Framework/reference model comparison with criteria.
- Adoption plan (adopt, adapt, defer, ignore) with rationale.
- Deviation record against a reference architecture.
- Answers to Topic 06 practice questions.

#### 6.10 Common mistakes and misconceptions

- Treating a framework as the architecture.
- Treating compliance with a framework as the goal.
- Copying templates without a user for the artefact.
- Assuming a reference architecture fits every organisation.
- Claiming to follow a framework without being able to name the parts used.

#### 6.11 Mastery criteria

- Uses the five terms correctly.
- Compares options with explicit criteria and evidence.
- Produces a tailored adoption plan and justifies deviations.

#### 6.12 Completion gate

- [ ] Comparison, adoption plan and deviation record complete and reviewed.
- [ ] The frameworks named in your notes match those named in the topic file
      (once written), or the discrepancy is recorded.
- [ ] Topic 06 practice questions answered and corrected.

---

## 5. Module dependencies and recommended learning order

### 5.1 Recommended order

1. **Topic 01** first: it supplies the vocabulary and the role.
2. **Topic 02** next: it sets the boundaries of the role before you go deeper.
3. **Topic 03** next: business capabilities and domains give the structure that
   later topics refer to.
4. **Topic 04** after 03: principles and quality attributes are defined against
   business drivers and domain context.
5. **Topic 05** after 04: governance applies the principles and handles
   exceptions.
6. **Topic 06** last: evaluating frameworks needs all of the above as criteria.

### 5.2 Dependency table

| # | Topic file | Prerequisites within this module | Key learning outcome | Evidence required |
| --- | --- | --- | --- | --- |
| 1 | `01-what-data-architecture-is-and-what-data-architects-do.md` | None | Explain scope, role and deliverables; frame a decision | Two-minute explanation, stakeholder table, decision note |
| 2 | `02-data-architecture-vs-data-engineering-and-solution-architecture.md` | 1 | Allocate decision roles; avoid silos | Comparison table, RACI, working agreement |
| 3 | `03-business-capabilities-domains-and-data-ownership.md` | 1, 2 | Identify domains and assign ownership | Capability map, ownership register, decision log |
| 4 | `04-architecture-principles-and-quality-attributes.md` | 1, 3 | Write principles and measurable quality targets | Principles set, targets table, trade-off analysis, exception record |
| 5 | `05-data-architecture-lifecycle-and-governance.md` | 2, 3, 4 | Design proportionate governance | Lifecycle diagram, decision-rights table, record template |
| 6 | `06-enterprise-data-architecture-frameworks-and-reference-models.md` | 1–5 | Evaluate and adapt frameworks | Comparison, adoption plan, deviation record |

### 5.3 Concepts that reinforce one another

- Ownership (3) is enforced through decision rights (5) and recorded in
  decision records (5).
- Quality attributes (4) are the criteria used in reviews (5) and in
  framework evaluation (6).
- The role boundaries (2) determine who sits on review forums (5).
- Reference architectures (6) embody principles (4).

### 5.4 When to revisit earlier material

- After Topic 04, revisit Topic 03 and check that ownership of data used to
  measure quality attributes is assigned.
- After Topic 05, revisit Topic 02 and check the RACI against the governance
  decision rights.
- After Topic 06, revisit Topic 04 and check whether any principle merely
  restates a framework without serving your organisation.

Cross-references to later modules: requirements and decisions (module 2D.2),
patterns and reference architectures (2D.3), governance and compliance in depth
(2D.10), metadata and master data (2D.11), documentation and operating model
(2D.15).

---

## 6. Practice questions and knowledge validation

### 6.1 Role of `practice-questions.md`

[`practice-questions.md`](practice-questions.md) is the practice and validation
resource for this module. This roadmap defines *how to use it*; it does not
duplicate the questions. The file is currently empty and should be populated to
match the categories below. The roadmap will need no change if the categories
are respected.

### 6.2 Question categories and how to use them

| Category | Purpose | Topics | Use |
| --- | --- | --- | --- |
| Terminology and conceptual understanding | Check definitions and scope | 1–6 | Beginner closed-book recall |
| Comparison and distinction | Separate neighbouring concepts | 1–2, 6 | Beginner → intermediate |
| Scenario analysis | Apply concepts to described situations | 1–6 | Intermediate |
| Architecture decision justification | Choose and defend with criteria | 1, 4, 6 | Advanced |
| Trade-off analysis | Reason about conflicting attributes | 4, 5 | Advanced |
| Governance and ownership situations | Resolve contested ownership and process questions | 3, 5 | Intermediate → advanced |
| Framework selection and adaptation | Evaluate and tailor frameworks | 6 | Advanced → industry |

### 6.3 Strategy

1. Answer each topic's questions **after** the topic, closed-book first.
2. Mark every answer as *correct*, *partly correct* or *wrong*, and write the
   reason in one sentence.
3. Re-attempt wrong and partly correct answers after a delay of several days.
4. Keep scenario and justification answers as written text, not mental notes.
5. Have at least the advanced answers reviewed by another person.

### 6.4 What success looks like

| Level | Successful performance |
| --- | --- |
| Beginner | Correct, concise definitions; correct classification of examples; no confusion between neighbouring terms |
| Intermediate | Scenario answers identify the relevant concepts, stakeholders and relationships, and reach a defensible conclusion |
| Advanced | Answers state options, criteria, trade-offs, risks and a revisit trigger; challenges to the answer can be met with evidence |
| Industry application | Answers refer to a realistic organisation, separate fact from assumption, and produce an artefact another person could act on |

---

## 7. Project — Current-state data architecture inventory

Project file:
[`Projects/01-current-state-data-architecture-inventory.md`](Projects/01-current-state-data-architecture-inventory.md)
(currently empty; this section defines its intended content). The project
index is [`Projects/README.md`](Projects/README.md).

This is an **architecture assessment** project. It is not a list of
technologies. Its output is a structured, evidence-based picture of how an
organisation's data is currently produced, held, moved, governed and used,
with the gaps and risks that picture reveals.

How it connects to the topics:

| Project part | Draws on |
| --- | --- |
| Scope, stakeholders, deliverables | Topics 1, 2 |
| Capabilities, domains, ownership | Topic 3 |
| Principles and quality assessment | Topic 4 |
| Governance observations, recommendations | Topic 5 |
| Choosing a documentation approach | Topic 6 |

### 7.1 Project objective

**Business objective:** give decision-makers a trustworthy picture of the
current data landscape so that investment, risk and change decisions are made
on evidence.

**Architectural objectives:**

- Document what exists, at a logical level, to an agreed scope.
- Make ownership, flows and dependencies visible.
- Assess the current state against stated principles and quality attributes.
- Identify gaps, risks and open questions, and recommend prioritised next
  steps.
- Create a baseline that later work (requirements, target state, reference
  architectures, decision records) can build on.

### 7.2 Project scenario and scope

**Scenario (illustrative, not factual).** *Northbridge Bank* is a fictional
mid-sized retail and business bank. Over fifteen years it has accumulated a
core banking system, a separate cards platform, a CRM, a loan origination
system, an enterprise data warehouse, a data lake created three years ago, and
a number of team-built reporting databases and spreadsheets. Risk, finance,
marketing and compliance each report different customer counts. A regulator
has asked for clearer evidence of where customer data comes from and who is
accountable for it.

> Everything in this scenario is **an illustrative assumption**. You may
> substitute any real or realistic organisation (for example from a case study
> or your own workplace, subject to confidentiality), but must then mark what
> you actually observed versus what you assume.

**Boundaries:**

- *In scope:* customer, account and transaction data across the listed
  systems; their producers and consumers; flows into reporting and analytics;
  ownership and governance arrangements.
- *Out of scope:* detailed schema design, performance tuning, tooling
  selection, target-state design, and implementation.

**Stakeholders (assumed):** head of data, business domain owners (retail,
lending, cards), risk, finance, compliance, security, engineering leads,
operations, internal audit.

**Assessment scope statement (write this first):** which systems, which data
domains, which time frame, which level of detail, and what is deliberately
excluded.

### 7.3 Step-by-step execution plan

Throughout, label every statement as one of: **Observed** (you saw evidence),
**Reported** (a stakeholder told you), **Assumed** (you inferred it), or
**Unverified/Unknown**. Never fill a gap with an invented fact.

| Step | What to do | Why it matters | Information needed | Activity | Artefact / evidence | How to verify |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Define assessment objective, scope and boundaries | Prevents unbounded work and mismatched expectations | Sponsor goals, time, access | Draft scope statement; agree exclusions | Scope and assumptions document | Sponsor confirms scope in writing |
| 2 | Identify stakeholders and gather documentation | Sources of evidence and reviewers | Org charts, existing diagrams, policies | Stakeholder list; request documents; log gaps | Stakeholder list; document register | Each stakeholder has a role and a purpose; each document has a date and source |
| 3 | Inventory business capabilities and domains | Anchors data in business terms | Capability models, process lists, interviews | Build two-level capability map; group into domains | Capability and domain inventory | Domain owners recognise their capabilities |
| 4 | Identify major data-producing and data-consuming systems | Defines the landscape | System lists, CMDB extracts, interviews | List systems; tag role (producer, consumer, both) | System inventory | Every capability maps to a system or is flagged "no system" |
| 5 | Identify important data entities, datasets and assets | Shows what data matters | Data dictionaries, schemas, reports, interviews | List key entities and datasets with sensitivity and criticality (as reported) | Data asset inventory | Each asset links to a system and a domain |
| 6 | Map ownership, stewardship and accountability | Reveals accountability gaps | Governance docs, role descriptions, interviews | Record owner, steward, producers, consumers; mark unknown | Ownership inventory | No asset has an unmarked owner field; unknowns are explicit |
| 7 | Document ingestion, integration, movement and consumption | Shows how data flows and where copies arise | Integration lists, interface specs, job inventories | Draw logical flows between systems; note method (batch, API, stream, manual) and frequency | Data flow inventory and draft diagram | Sample flows traced end to end with a system owner |
| 8 | Identify storage, processing and serving components | Locates where data rests and is transformed | Platform inventories, architecture docs | List stores, processing and serving layers at a logical level | Component inventory | Each component links to the assets it holds |
| 9 | Document principles, standards and governance arrangements | Establishes the rules that apply | Policies, standards, forum charters, decision records | Collect and summarise; note whether they are applied | Principles and governance observations | Each item cites a source; unapplied items are flagged |
| 10 | Assess against quality attributes and business requirements | Turns description into assessment | Targets (if any), incident history, audit findings | Rate each attribute with evidence; note where no target exists | Quality-attribute assessment | Each rating cites evidence or is marked "no evidence" |
| 11 | Identify gaps, risks, constraints, dependencies and open questions | Surfaces what needs action | Outputs of steps 3–10 | Derive items; link each to a finding; rate impact and likelihood | Gap and risk register; open-questions list | Every item traces to at least one finding |
| 12 | Create the current-state view and supporting inventory | Provides the shared picture | All prior artefacts | Produce a logical current-state diagram and a consolidated inventory | Current-state architecture view | Diagram elements trace to inventory entries; no orphan items |
| 13 | Validate with stakeholders | Corrects errors and builds ownership | Draft artefacts | Review sessions; record corrections and disagreements | Validation log | Each material finding has a reviewer and a recorded response |
| 14 | Produce prioritised observations and next steps | Makes the work actionable | Validated register and findings | Rank by impact and effort; link to the gap or need | Findings and next-steps summary | Each recommendation traces to a gap or risk |

**Per-step guidance:**

1. **Scope.** Write down what you will *not* do. Revisit the scope at step 11
   if findings show it was wrong.
2. **Stakeholders and documents.** Record the date and author of each document;
   old diagrams are evidence of intent, not of current reality.
3. **Capabilities and domains.** Start from business language. If you start
   from the system list you will rebuild the existing silos.
4. **Systems.** Distinguish systems of record from copies and from reports.
5. **Assets.** Prefer a small set of important assets to an exhaustive list;
   say how you chose.
6. **Ownership.** "Unknown" is a valid and valuable finding.
7. **Flows.** Include manual flows and spreadsheets; they are frequently where
   the risk lives.
8. **Components.** Stay logical; do not expand into product configuration.
9. **Governance.** Note the difference between documented and practised.
10. **Quality.** Use the targets from Topic 04 if they exist; if not, record
    that no target exists, which is itself a finding.
11. **Gaps.** A risk without a supporting finding is an opinion; do not
    include it.
12. **View.** One page, understandable to a business reader, with a legend.
13. **Validation.** Record disagreements; do not silently resolve them.
14. **Recommendations.** Few, prioritised, and traceable.

### 7.4 Required project deliverables

| # | Deliverable | Purpose | Minimum content |
| --- | --- | --- | --- |
| D1 | Assessment scope and assumptions | Fixes boundaries and expectations | Objective, in/out of scope, time frame, assumptions, evidence rules (Observed/Reported/Assumed/Unknown) |
| D2 | Stakeholder and system inventory | Who and what is involved | Stakeholders with role and interest; systems with role, owner, status |
| D3 | Business capability and domain inventory | Business-aligned structure | Two-level capability map; domains; mapping to systems |
| D4 | Data asset and ownership inventory | Accountability for data | Asset, domain, system, sensitivity (as reported), owner, steward, producers, consumers |
| D5 | High-level current-state data flow or architecture diagram | Shared picture | Systems, flows, direction, method and frequency, legend, version and date |
| D6 | Architecture principles and governance observations | Rules and their application | Principles, standards, forums, decision rights; whether applied |
| D7 | Quality-attribute assessment | Evidence-based evaluation | Attribute, target (or none), evidence, rating, confidence |
| D8 | Gaps, risks, dependencies and unresolved questions register | Basis for action | ID, description, source finding, impact, likelihood, owner (if known), status |
| D9 | Findings and prioritised next steps | Decision support | Findings, priority, rationale, traceability to register |
| D10 | Final assessment summary | Executive-level readout | One to two pages: scope, key findings, top risks, next steps, caveats |

### 7.5 Suggested inventory fields

Include only fields that serve a purpose. Use `Unknown` where the value is not
known; never invent values. Add a `Source` and `Evidence type`
(Observed/Reported/Assumed) to every row.

**System inventory**

| Field | Purpose |
| --- | --- |
| System ID, name | Reference |
| Business capability supported | Links to business |
| Role (system of record / consumer / copy / reporting) | Distinguishes authority |
| Business owner, technical owner | Accountability |
| Main data held (domains) | Links to assets |
| Interfaces in / out | Supports flow mapping |
| Hosting (on-premises / cloud / vendor) | Context for risk |
| Lifecycle status (active, retiring, planned) | Planning |
| Source, evidence type, last verified | Traceability |

**Data asset inventory**

| Field | Purpose |
| --- | --- |
| Asset ID, name, description | Reference |
| Domain | Ownership alignment |
| Authoritative system | Where the truth lives |
| Sensitivity / criticality (as classified, or Unknown) | Risk context |
| Refresh frequency | Flow context |
| Known quality concerns | Assessment input |
| Source, evidence type | Traceability |

**Ownership inventory**

| Field | Purpose |
| --- | --- |
| Asset or domain | Subject |
| Data owner (role/person) | Accountability |
| Data steward | Quality and definitions |
| Producers, consumers | Dependencies |
| Decision authority for change | Governance |
| Ownership status (confirmed / disputed / unknown) | Gap identification |
| Source, evidence type | Traceability |

**Gap and risk register**

| Field | Purpose |
| --- | --- |
| ID, title, description | Reference |
| Type (gap / risk / constraint / dependency / question) | Classification |
| Supporting finding(s) | Traceability |
| Affected capability / asset / system | Scope |
| Impact, likelihood, confidence | Prioritisation |
| Proposed owner, next step | Action |
| Status | Tracking |

### 7.6 Validation and quality criteria

| Check | How to verify |
| --- | --- |
| Inventory is complete for the declared scope | Every in-scope capability has a system or an explicit "no system"; every in-scope system has an owner or "unknown" |
| Major systems and data flows captured | Sample at least three flows end to end with a knowledgeable person; any missing flow is added |
| Domains and ownership are traceable | Pick five assets at random and trace asset → system → domain → owner |
| Architecture views are internally consistent | Every diagram element exists in the inventory and vice versa; names match |
| Assumptions and evidence are distinguishable | Every row carries an evidence type; no unlabelled claims |
| Risks and gaps are supported by findings | Every register item cites a finding |
| Stakeholders reviewed material findings | Validation log shows reviewer and response for each |
| Recommendations are traceable | Each recommendation cites a gap, risk or need |

### 7.7 Project completion gate

The project is complete only when **all** of the following hold:

- [ ] D1–D10 exist and are version-dated.
- [ ] Every inventory row has a source and an evidence type.
- [ ] No unknown value has been replaced by an invented one; unknowns are listed.
- [ ] Capability → system → asset → owner traceability passes the five-asset
      spot check.
- [ ] The current-state diagram and inventory are consistent.
- [ ] Every register item and recommendation traces to a finding.
- [ ] At least two stakeholders (or two reviewers in that role) have reviewed
      the material findings and their responses are recorded.
- [ ] The final summary can be read by a non-specialist in ten minutes and
      states its limits.
- [ ] A reviewer who did not do the work agrees the evidence supports the
      conclusions.

### 7.8 Connection to the next stage

The inventory is deliberately a **baseline**, not a design. It supports later
work without absorbing it:

- **Requirements and decisions (2D.2):** gaps, risks and open questions become
  inputs to stakeholder discovery and requirement statements; quality-attribute
  findings seed non-functional requirements.
- **Target-state and reference architectures (2D.3, 2D.7):** the current-state
  view is the "from" in a current-to-target comparison; domain and ownership
  findings inform pattern choice.
- **Architecture decision records (2D.2, 2D.15):** each major recommendation
  becomes a decision with options and consequences, grounded in the evidence
  recorded here.
- **Governance, metadata and master data (2D.10, 2D.11):** ownership gaps and
  undefined sensitivity feed those modules directly.

Do not design the target state in this project. Record recommendations as next
steps only.

---

## 8. Final module completion checklist

Self-reported confidence is not enough. Each item requires the evidence listed.

| # | You can… | Evidence required |
| --- | --- | --- |
| 1 | Explain Data Architecture and the Data Architect's responsibilities | Recorded or written explanation reviewed by another person; Topic 01 decision note |
| 2 | Distinguish Data Architecture, Data Engineering and Solution Architecture | Comparison table and RACI reviewed with no unassigned decision |
| 3 | Identify business capabilities, domains and data ownership responsibilities | Capability map, ownership register and decision log |
| 4 | Define and apply architecture principles and quality attributes | Principles set, measurable targets table, trade-off analysis, exception record |
| 5 | Explain the architecture lifecycle and governance process | Lifecycle diagram, decision-rights table, record template, governance critique |
| 6 | Evaluate and adapt frameworks and reference models | Comparison, adoption plan, deviation record |
| 7 | Defend architecture decisions with evidence and explicit trade-offs | At least two written decision notes that survived a reviewer's challenge |
| 8 | Complete and present the current-state data architecture inventory | Deliverables D1–D10, validation log, and a short presentation to a reviewer |

Module complete when:

- [ ] All six topic completion gates are signed off.
- [ ] `practice-questions.md` answered; every wrong answer corrected and
      re-attempted.
- [ ] The project completion gate (Section 7.7) is met.
- [ ] You have presented the project and answered a reviewer's challenge
      questions without introducing unsupported claims.
- [ ] Open questions are logged for the next module (2D.2).

---

## 9. Where this module leads

Module 2D.2, **Requirements, Constraints and Architecture Decisions**, builds
directly on this module: it turns the stakeholders, quality attributes and
current-state findings you produced here into requirements, constraints and
formal architecture decision records.
