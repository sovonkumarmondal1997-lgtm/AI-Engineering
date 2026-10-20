# 05 — Data Architecture Lifecycle and Governance

> **Stage:** Stage 2D — Data Architecture  
> **Module:** 01 — Data Architecture Foundations and Principles  
> **Lesson file:** `05-data-architecture-lifecycle-and-governance.md`  
> **Level:** Beginner → Intermediate → Advanced  
> **Source alignment:** This lesson follows Module 5 of `roadmap-Data-Architecture-Foundations-and-Principles.md`. The roadmap prescribes the lifecycle, governance, standards/policies/guidelines, current- and target-state assessment, decision rights, review mechanics, conformance, decision records, exceptions, proportionality, governance measures, escalation, continuous improvement, failure modes, a banking review-process exercise, a decision-record and exception-register exercise, five governance measures, three practical scenarios, and the listed deliverables and completion gate.

## 1. Learning objective

By the end of this lesson, you should be able to:

1. Describe the data architecture lifecycle and identify the principal artefact produced at each stage.
2. Design an architecture governance process with explicit decision rights, standards, reviews, exceptions, conformance checks, and change control.
3. Distinguish local decisions, decisions that require review, and decisions that require escalation or formal approval.
4. Explain how current-state assessment and target-state design expose gaps and inform a practical roadmap.
5. Define review inputs, evaluation criteria, outcomes, records, and implementation checks.
6. Design proportionate governance: low-risk, reversible choices should move quickly; high-risk, irreversible, cross-domain, or enterprise-wide choices should receive appropriate scrutiny.
7. Evaluate governance with evidence, including turnaround time, review coverage, exception counts and age, conformance findings, and delivery-team feedback.
8. Diagnose governance failure modes and propose measurable improvements.
9. Apply the concepts to a banking data programme without assuming that one invented organisational process or a particular regulatory obligation applies to every bank.

The core outcome is not a large approval bureaucracy. It is a repeatable decision system that makes important choices explicit, traceable, implementable, and revisitable while allowing routine work to proceed.

## 2. Why this topic matters in real-world Data Architecture

Data architecture decisions affect more than diagrams. They shape data ownership, integration contracts, storage and access patterns, data quality, operational responsibilities, costs, change impact, and the ability to explain why a platform behaves as it does. A decision made for one project can become a dependency for several domains. Without a lifecycle and governance, teams may make locally reasonable but mutually incompatible choices, undocumented exceptions can become permanent, and implementation can drift away from the design that was approved.

Governance can fail in the opposite direction too. If every schema change, table name, or low-risk pipeline adjustment waits for an enterprise committee, teams may delay delivery, bypass the process, or seek approval only after shipping. The roadmap expresses the central tension directly: **architecture without governance drifts; governance that is too heavy gets bypassed.**

### 2.1 Lifecycle versus governance

The **architecture lifecycle** describes the sequence of work through which an architecture is discovered, designed, decided, implemented, operated, and improved.

**Architecture governance** defines who may make which decisions, what evidence is needed, which principles and standards apply, how decisions are recorded, how exceptions are approved, and how conformance and outcomes are checked.

They are complementary, not interchangeable:

- The lifecycle answers, “What work happens next, and what output should exist?”
- Governance answers, “Who has authority, what rules and evidence apply, and how do we know the decision remains justified?”
- Delivery management coordinates scope, schedule, dependencies, and execution.
- Operational execution runs and supports the implemented data services, monitors service levels, responds to incidents, and performs routine changes within the approved design.

Governance does not replace competent design or delivery. It provides a reliable decision and feedback mechanism around them.

### 2.2 What governance protects—and what it must not suppress

A practical governance process should help an organisation:

- Make decision rights visible before a contentious decision appears.
- Apply architecture principles and quality attributes consistently.
- Surface cross-domain impacts and hidden dependencies early.
- Record the rationale behind choices so teams do not repeatedly reopen settled questions without new evidence.
- Make deviations visible, bounded, owned, and reviewable.
- Check whether implementation matches the approved intent.
- Learn from incidents, recurring exceptions, and changes in business needs.

It should not force every decision through the same forum, use review as a substitute for accountability, or reward document production rather than good outcomes.

### 2.3 Banking example: a new transaction data source

**Illustrative scenario, not a statement about any specific bank:** a bank wants to add a transaction-monitoring vendor feed to a data platform. The business wants useful data quickly. Data engineering needs a reliable ingestion path. The data owner must confirm meaning and permitted use. Platform engineering must assess integration and operations. Security, privacy, risk, or compliance specialists may need to contribute depending on the data and intended use. Architecture governance determines the route for the decision; it does not invent the business purpose or perform the engineering work.

A weak process says, “Build it, then ask the architecture board.” A better process identifies the requirement, classifies the decision, gathers the evidence proportionate to its risk, records the decision, implements against it, checks conformance, and revisits it when assumptions change.

## 3. Prerequisite knowledge

The roadmap names **Modules 1–4** as prerequisites, with direct reuse of Module 4’s architecture principles and exception handling.

You should already be able to work with:

- What data architecture is and how it differs from data engineering and solution architecture.
- Business capabilities, domains, and data ownership.
- Architecture principles, their rationale and implications.
- Quality attributes and measurable requirements.
- The idea that architecture choices involve trade-offs rather than a universally best technology.
- A basic exception record and the reason exceptions must not be informal and permanent.

If these ideas are not yet familiar, review the earlier lessons before treating the governance examples below as a policy to copy. The roles, review thresholds, time limits, and numeric examples in this lesson are teaching examples that an organisation would need to adapt.

### 3.1 Essential vocabulary

| Term | Meaning in this lesson | Practical use |
|---|---|---|
| Lifecycle stage | A phase of architecture work with a purpose and expected output | Shows what evidence or artefact should exist before the next activity |
| Governance | Decision rights, rules, review paths, records, conformance, and feedback | Determines who can decide and how decisions are controlled |
| Policy | A high-level organisational rule or required direction | States a mandatory expectation when formally adopted by the organisation |
| Standard | A specific, testable rule or approved way of doing something | Enables consistent implementation and conformance checks |
| Guideline | Advisory guidance that supports judgement but is not automatically mandatory | Helps teams choose well without requiring identical solutions |
| Architecture review | A structured evaluation of a proposed decision against agreed criteria | Finds material risks, conflicts, missing evidence, and cross-domain impacts |
| Decision record | A durable record of the context, options, decision, rationale, consequences, and status | Preserves the “why,” not just the selected technology |
| Exception | A time-bounded, explicitly authorised deviation from a policy, standard, or principle | Makes a necessary deviation visible and subject to compensating controls and review |
| Conformance | Evidence that an implementation aligns with the approved decision and applicable rules | Detects design-to-production drift |
| Change control | The method for deciding whether a changed requirement, assumption, constraint, or design invalidates an earlier decision | Keeps architecture aligned as conditions change |

A company may use these terms differently in its own policy system. The definitions above provide a consistent learning vocabulary, not a claim that every organisation uses identical terminology.

## 4. Beginner-level learning sequence

### 4.1 The seven lifecycle stages

The roadmap prescribes the following sequence:

1. Discover and assess current state.
2. Analyse requirements.
3. Design target state.
4. Evaluate and approve.
5. Implement and align.
6. Operate and monitor.
7. Change and improve.

The lifecycle is iterative, not a one-way waterfall. Operating evidence can send the team back to requirements or design. A new business requirement can trigger reassessment. A failed conformance check may require implementation correction or a revised decision.

```text
Business need / new data source
             |
             v
[1. Discover and assess current state]
             |  Artefact: inventory, context, constraints, known gaps
             v
[2. Analyse requirements]
             |  Artefact: requirements, quality targets, assumptions, risks
             v
[3. Design target state]
             |  Artefact: target design, options, interfaces, migration approach
             v
[4. Evaluate and approve]
             |  Artefact: review outcome, decision record, conditions/exceptions
             v
[5. Implement and align]
             |  Artefact: implemented change, tests, traceability, conformance evidence
             v
[6. Operate and monitor]
             |  Artefact: service measures, incidents, drift and outcome observations
             v
[7. Change and improve]
             |  Artefact: reassessment, revised decision, improvement backlog
             +-------------------------------> back to stage 1, 2, or 3
```

Governance operates across the lifecycle. It is especially visible at stage 4, but it also sets standards for discovery, clarifies decision rights during design, checks implementation at stage 5, and uses operational evidence during stages 6–7.

### 4.2 Lifecycle stages and their outputs

| Stage | Questions to answer | Typical outputs | Governance contribution |
|---|---|---|---|
| 1. Discover and assess current state | What exists today? Who owns the data? Which systems, interfaces, dependencies, constraints, and known problems matter? | Current-state inventory; context and dependency map; known issues and constraints | Confirms the right owners and impacted domains are involved; records evidence gaps |
| 2. Analyse requirements | What business outcome is needed? What data is required? What freshness, availability, quality, security, or cost expectations apply? | Requirements; measurable quality targets; assumptions; risks; acceptance criteria | Checks that material requirements and constraints are explicit, not inferred from a preferred solution |
| 3. Design target state | What options can satisfy the requirements? What changes to data flow, ownership, interfaces, and operations are needed? | Target-state design; options; trade-off analysis; migration and transition outline | Ensures applicable principles, standards, and cross-domain implications are considered |
| 4. Evaluate and approve | Is the proposal justified? Does it meet the criteria? Who has authority to accept residual risk or an exception? | Review outcome; decision record; conditions; exception record if required | Routes the decision to the correct authority and records rationale, conditions, and dissent if material |
| 5. Implement and align | Was the approved design implemented? Were conditions and tests completed? | Code/configuration; tests; implementation evidence; updated diagrams and records | Checks conformance and resolves deviations instead of assuming approval guarantees correct implementation |
| 6. Operate and monitor | Is the solution delivering the required outcomes? Are there incidents, cost changes, data-quality failures, or design drift? | Operational measures; incidents; findings; cost and reliability evidence | Makes operating evidence available to owners and reviewers; escalates material drift |
| 7. Change and improve | Have requirements, assumptions, technology, risks, or operating evidence changed? Is the decision still valid? | Reassessment; revised decision; standard update or retirement; improvement actions | Reopens decisions when a trigger is met and tracks closure of agreed actions |

These outputs do not need to be seven separate heavyweight documents. A small change may use a short ticket with linked evidence. A high-impact change may need a full decision pack. The important property is that the necessary information exists and is accessible.

### 4.3 Governance, implementation management, and operations

These functions cooperate but have different accountabilities.

| Function | Primary question | Typical responsibility | What it should not do |
|---|---|---|---|
| Architecture governance | Is the decision appropriate, authorised, justified, and traceable? | Define decision paths; review material choices; approve or escalate within delegated authority; manage exceptions; check conformance | Design every detail for the delivery team or run the pipeline |
| Delivery / implementation management | Can the approved change be delivered safely within scope, time, dependencies, and resources? | Plan work, coordinate teams, manage dependencies, track implementation, resolve delivery blockers | Quietly override an architecture decision because the schedule is tight |
| Operational execution | Does the service work reliably in production and meet agreed operational expectations? | Run jobs and services, monitor health, respond to incidents, manage operational changes and runbooks | Treat an unapproved material design change as merely an operational tweak |
| Business/data ownership | Is the data meaning, purpose, quality, access, and use appropriate for the domain? | Confirm business semantics, accountability, acceptable use, and ownership decisions | Delegate business accountability to the architecture forum |
| Security, privacy, risk, or compliance specialists | What domain-specific risks or obligations apply to this proposal? | Provide specialist assessment and evidence where relevant; identify required controls or escalation | Be presumed to have approved an issue they have not reviewed |

One person may hold more than one role in a small organisation, but the responsibilities still need to be explicit. Separating the responsibilities conceptually prevents a committee from becoming responsible for work it cannot actually perform.

### 4.4 Governance, policies, standards, and guidelines

Governance is the operating mechanism; policies, standards, and guidelines are different kinds of input to it.

| Instrument | Typical force | Example for a data programme | How to use it |
|---|---|---|---|
| Policy | Mandatory at the level and scope defined by the adopting organisation | “Sensitive data must be handled only through approved access paths.” | Identify the owner, scope, authority, and method for handling conflicts or exceptions |
| Standard | Specific and checkable; mandatory when formally adopted as such | “Every production data product must publish an owner, schema version, freshness objective, and support contact in the catalogue.” | Make it testable; define evidence and the process for approved deviation |
| Guideline | Advisory; allows judgement | “Prefer a managed ingestion service when it satisfies the workload’s needs.” | Explain when the recommendation is useful and when an alternative may be justified |
| Architecture principle | A durable decision rule that helps compare options | “Authoritative customer attributes should have a named system of record and accountable owner.” | State the rationale and implications; use it to decide between real options |
| Review criterion | A question or threshold applied during a decision | “Does the proposal introduce an unmanaged cross-domain dependency?” | Apply consistently and record findings |
| Exception | A recorded, authorised deviation from a specified rule | “A temporary duplicate feed is permitted during a migration, with reconciliation and a retirement date.” | Bound the deviation, name the owner, document controls and expiry, and review it |

**Standard versus guideline:** a standard is a rule the organisation can check and expects teams to follow within its stated scope; a guideline is advice that helps teams exercise judgement. A document does not become a standard merely because it is titled “standard.” Its authority, scope, owner, and conformance expectation must be clear.

**Why a decision needs a record:** decisions outlive meetings and often outlive the people who made them. A record preserves context, alternatives, rationale, assumptions, consequences, approval status, conditions, and review triggers. It also makes it possible to determine whether a new situation genuinely invalidates the decision or merely reopens an old debate.

### 4.5 Worked beginner example: requirement to reviewable outcome

**All organisation names, thresholds, and target values below are illustrative.**

**Business request:** “Make transaction-monitoring data available for an operational dashboard.”

**Step 1 — Discover and assess.** The team identifies the source vendor, current ingestion path, data owner, downstream consumers, existing authoritative records, operational dependencies, and data classification. Output: a short current-state inventory and dependency sketch.

**Step 2 — Analyse requirements.** The product owner clarifies that the dashboard is for operational triage, not final accounting. The team asks what “available quickly” means, what fields are needed, what quality checks are necessary, and what happens when the source is delayed. An illustrative requirement might be: “95% of accepted source events are visible to the dashboard within five minutes during the agreed operating window.” The value is a hypothesis until the business validates it and a measurement method is defined. Output: requirements and measurable acceptance criteria.

**Step 3 — Design target state.** The team compares a scheduled batch feed with a streaming/event-driven feed. It describes freshness, recovery, duplicate handling, cost, operational burden, and source limitations. Output: target design and a concise options comparison.

**Step 4 — Evaluate and approve.** The proposal is classified as reviewed because it crosses the source, platform, and consuming domain and introduces a new freshness objective. Reviewers check the applicable principles, quality targets, ownership, failure handling, and operations. The authorised decision-maker records the outcome and any conditions. Output: decision record, not merely meeting minutes.

**Step 5 — Implement and align.** Engineers implement the selected path, test schema compatibility, late and duplicate events, replay, alerting, access, and acceptance criteria. They link test evidence to the decision record. Output: implementation and conformance evidence.

**Step 6 — Operate and monitor.** The team observes measured freshness, failure rate, data-quality results, recovery behaviour, and cost. Output: operational evidence and any findings.

**Step 7 — Change and improve.** If volume grows, source delivery changes, the business starts using the feed for a different purpose, or the five-minute objective becomes uneconomic, the owner reassesses requirements and design. Output: a new decision version or linked decision record, with old rationale preserved.

The architecture decision is reviewable because a future reviewer can trace the business need, options, evidence, decision authority, implementation checks, observed results, and triggers for reconsideration.

### 4.6 Beginner exercise: draw one lifecycle

Choose a new data source that could plausibly be added to a bank's analytics platform. Draw the seven stages and label at least one artefact at each stage. Your artefacts may be short and linked; they do not need to be separate files.

Answer these questions:

1. Which stage identifies existing systems, data ownership, and dependencies?
2. Which stage converts “fast enough” into a measurable requirement?
3. Where are options compared and the decision authorised?
4. What evidence proves the implementation matches the approved design?
5. What operating signal would cause the architecture to be reassessed?

**Ability to demonstrate:** name all seven stages and explain the purpose and output of each.

## 5. Intermediate-level learning sequence

### 5.1 Current-state assessment, target-state design, and the gap

The roadmap asks you to understand the inputs and outputs of current-state assessment and target-state design, and how the gap drives a roadmap. The detailed assessment is practised in the module project, so this lesson focuses on how those assessments feed governance.

**Current-state assessment** establishes what exists and what is known about it. Inputs can include system and data-product inventories, interface contracts, data lineage, ownership records, operational metrics, known incidents, cost information, and constraints. Outputs should distinguish verified facts from assumptions and unknowns.

**Target-state design** describes the intended capabilities, data flows, ownership, interfaces, quality characteristics, operating model, and material transition choices needed to meet the requirements. It should not be only a diagram of preferred technology.

The **gap** is the difference between the current and target states. A useful gap statement identifies:
- the current condition and its evidence;
- the target condition and the requirement it supports;
- the change needed;
- dependencies and risks;
- a plausible sequence or roadmap item;
- an owner and a way to verify closure.

Example: “The current transaction feed has no documented owner and is refreshed daily; the approved dashboard requirement needs five-minute visibility. The gap is not simply ‘buy streaming technology.’ It includes source capability, ownership, event quality, duplicate handling, support coverage, and a tested freshness objective.” This framing prevents a solution choice from being mistaken for the requirement itself.

### 5.2 A three-tier decision model

The roadmap specifically asks for a three-tier model: **local, reviewed, and escalated**. These tiers are an example governance design, not a universal organisational policy. A bank or other organisation should define its own thresholds, authorities, and mandatory review obligations.

| Tier | Decision class | Typical examples | Decision authority | Minimum evidence | Expected route |
|---|---|---|---|---|---|
| Tier 1 — Local | Low-risk, reversible, within an approved pattern and existing ownership boundaries | A non-breaking field addition within a domain contract; a pipeline retry setting within an approved operational envelope | Named domain/data-product owner or delegated technical lead | Short change description, relevant standard check, tests, impact confirmation | Team records decision locally; no central meeting unless a trigger is hit |
| Tier 2 — Reviewed | Material change within a known domain or platform, with manageable cross-team effects | New source integration; a changed freshness target; a new data-sharing interface; a deviation from an approved pattern that does not cross the enterprise risk boundary | Designated architecture reviewer or review forum, with accountable domain and platform owners | Requirements, options, affected systems/consumers, principles and quality-attribute assessment, risks, implementation and rollback plan | Time-boxed review; approve, approve with conditions, reject, or defer |
| Tier 3 — Escalated | High-risk, hard-to-reverse, enterprise-wide, cross-domain, or beyond delegated authority | Changing the authoritative customer record; introducing a new enterprise-wide data-sharing pattern; a material sensitive-data use change; an unresolved risk acceptance outside local authority | Named enterprise/domain authority or formally empowered decision body; relevant accountable risk owners participate as required | Decision pack, alternatives, impacts, risks and residual risks, dependency map, specialist assessments where relevant, migration and recovery strategy | Escalation with decision deadline, recorded rationale, conditions and follow-up owner |

A decision is not escalated merely because it is technically interesting. It is escalated because its **impact, risk, irreversibility, reach, or authority boundary** justifies broader accountability.

#### 5.2.1 Classification questions

Ask the following before assigning a tier:

1. Does the change remain inside an approved architecture pattern and the team's authority?
2. Is it reversible without unacceptable cost, disruption, or data loss?
3. Does it change data meaning, ownership, authoritative source, access purpose, or consumer contract?
4. Does it create a cross-domain dependency or affect many consumers?
5. Does it introduce material reliability, privacy, security, financial, or operational risk?
6. Does it conflict with a mandatory policy or standard?
7. Is there a credible rollback or migration path?
8. Is the decision likely to set a precedent for other teams?

If an answer indicates a material boundary crossing, raise the tier or consult the relevant accountable owner. Do not hide an escalated decision inside a local ticket simply to save time.

### 5.3 Decision rights: who proposes, contributes, decides, and implements?

A decision-rights model avoids two common problems: everyone assumes someone else is accountable, or a committee is asked to approve work without being given authority to do so.

The following is a **sample responsibility model**. Actual titles and approval rights must be adapted to the organisation.

| Role | Proposes | Contributes evidence | Decides / approves | Implements | Verifies / monitors |
|---|---|---|---|---|---|
| Business/product owner | Business outcome and acceptance criteria | Use case, priority, service expectations | Accepts business outcome within delegated authority | Usually not the technical implementation | Confirms outcome remains useful |
| Data/domain owner | Domain data change and semantics | Definitions, quality expectations, ownership, consumers | Decides domain matters within delegated authority; participates in cross-domain decisions | May sponsor implementation | Monitors domain quality and ownership |
| Data architect / solution architect | Options and design recommendation | Principles, dependencies, trade-offs, target-state fit | Makes local design decisions only if delegated; otherwise recommends | Supports design alignment | Checks design conformance and revisits assumptions |
| Data/platform engineering lead | Technical implementation proposal | Feasibility, reliability, capacity, cost, operability | Approves technical details within delegated boundaries | Leads engineering implementation | Provides test and operational evidence |
| Architecture review forum | Usually does not originate the business need; may request alternatives | Cross-domain impacts, standards, quality attributes, precedent | Decides only the decisions formally delegated to it; otherwise recommends or escalates | No | Tracks conditions and portfolio-level drift |
| Security/privacy/risk/compliance specialist | May identify a concern or required assessment | Specialist analysis, applicable policy or obligation, control evidence | Approves only matters within their actual authority; may have defined veto/escalation rights under local policy | Implements or supports controls where assigned | Reviews relevant evidence and risk changes |
| Service/operator owner | Operational change or corrective action | Runbooks, support model, failure modes, monitoring, recovery evidence | Approves operational readiness within delegated authority | Runs and supports the service | Monitors production behaviour and incidents |
| Named decision authority / executive sponsor | May sponsor an enterprise decision | Business and risk context | Makes or ratifies escalated decisions within formally assigned authority | Delegates delivery | Ensures residual risk and actions have owners |

**Decision rights are not the same as attendance.** A specialist attending a meeting does not automatically approve the proposal. A forum cannot authorise a risk outside its delegated authority. Record who is accountable for the decision, who provided specialist advice, and who owns each implementation condition.

### 5.4 Review mechanics: evidence, criteria, and outcomes

A review should answer a decision question, not merely inspect a presentation.

#### 5.4.1 What a proposal should contain

A lightweight proposal can include:

1. **Decision question:** what precisely must be decided?
2. **Business outcome and requirements:** including measurable quality targets where relevant.
3. **Current state and affected scope:** systems, data domains, owners, consumers, interfaces, and dependencies.
4. **Options considered:** including a credible “do nothing / defer” option where useful.
5. **Recommended option and rationale:** why it best meets the stated criteria.
6. **Principles and standards:** which apply, how the proposal conforms, and whether an exception is requested.
7. **Quality attributes and trade-offs:** performance, freshness, reliability, scalability, security, maintainability, cost, and other relevant attributes—not every attribute in every review.
8. **Risks, assumptions, constraints, and unknowns:** state which are evidenced and which require validation.
9. **Implementation and migration:** sequencing, compatibility, rollback/recovery, testing, and operational ownership.
10. **Decision needed and deadline:** identify the authority and the cost of delay.
11. **Evidence links:** measurements, tests, diagrams, source contracts, cost estimates, or specialist assessments that support material claims.

The amount of evidence should match the decision's impact. A low-risk configuration change does not need a 30-page architecture paper; a change to the authoritative customer record should not be decided from a one-line chat message.

#### 5.4.2 Review criteria

Use agreed criteria consistently:

- Does the proposal meet the business and data requirements?
- Does it follow applicable principles and standards?
- Are quality attributes measurable, with a credible verification method?
- Are data ownership, semantics, consumers, and interfaces clear?
- Are important dependencies and failure modes addressed?
- Is the proposed operating and support model credible?
- Are cost and delivery trade-offs explicit?
- Are assumptions, unresolved questions, and residual risks visible?
- Is an exception needed, and who has authority to approve it?
- Is the decision reversible, and what evidence would trigger reconsideration?

Not every criterion needs a numerical score. Use quantitative scoring when it clarifies a real comparison, not to create a false appearance of objectivity.

#### 5.4.3 Possible review outcomes

| Outcome | Meaning | Required follow-through |
|---|---|---|
| Approve | Evidence supports the proposal within the reviewer's authority | Record rationale, scope, owner, and any review triggers |
| Approve with conditions | Direction is acceptable, but specific conditions must be met | Record each condition, accountable owner, due date, evidence, and whether it blocks release |
| Reject | The proposal does not meet criteria or is outside the authority's acceptable risk boundary | Record reasons and what a viable resubmission would need |
| Defer | The decision cannot responsibly be made yet because material evidence or an accountable decision-maker is missing | Record the missing evidence, owner, next decision date, and interim path |
| Escalate | The decision exceeds the current authority or has unresolved cross-domain/risk conflict | Send a complete decision pack to the named authority with a time limit |
| Return for revision | The proposal is incomplete or does not yet answer the decision question | Identify specific gaps; avoid vague “needs more detail” feedback |

A review outcome must be communicated to the proposer and stored in the decision record. Meeting minutes alone are insufficient if they do not clearly show the decision, authority, rationale, conditions, and owner.

### 5.5 Worked governance workflow

The following workflow is an illustrative operating model that can be implemented using a ticketing system, repository, architecture register, or lightweight workflow tool.

```text
1. Request raised
   |
   v
2. Triage: identify owner, scope, applicable standards, risk, reversibility
   |
   +--> Tier 1: local decision
   |       | record short rationale + tests
   |       v
   |    implement -> conformance check -> close
   |
   +--> Tier 2: reviewed decision
   |       | submit decision pack
   |       v
   |    reviewer/forum assesses criteria and evidence
   |       |
   |       +--> approve / approve with conditions
   |       +--> reject / return for revision / defer
   |       +--> escalate if authority or risk boundary is exceeded
   |       v
   |    implement -> verify conditions and conformance -> close
   |
   +--> Tier 3: escalated decision
           | complete impact/risk/option pack
           v
        named accountable authority decides or returns it
           |
           v
        record decision, residual risk, conditions and review triggers
           |
           v
        implement -> independent/assigned conformance evidence -> monitor
```

#### 5.5.1 Practical process rules

- **Engage early:** identify the decision path while options are still open, not after the design is complete.
- **Triage once, reclassify when evidence changes:** the initial tier is a hypothesis; new cross-domain or risk information can move a decision upward.
- **Publish a service expectation:** state the expected turnaround time for each review tier and how urgent decisions are handled. These targets are local operating choices, not universal standards.
- **Define the review clock:** start measuring when a submission is complete enough to review; record when it is returned for missing evidence and distinguish requester wait time from reviewer queue time. Publish both the target and the pause/resume rule so teams cannot improve the metric merely by relabelling delays.
- **Set targets from evidence:** there is no universal correct number of hours or days. Establish a baseline by tier and complexity, agree a target with delivery and risk stakeholders, monitor median and a high percentile, and revise the target if quality or risk outcomes deteriorate. If no baseline exists, mark the first target as a hypothesis and review it after a defined pilot.
- **Handle missed deadlines explicitly:** when a tier's target is missed, notify the proposer, name the blocker and next action, and route an unresolved decision to the named authority by the agreed escalation deadline. Escalation means obtaining a decision or a documented next step—not silently granting approval.
- **Batch thoughtfully:** combine related decisions when they share context, but do not hold an urgent independent decision hostage to an unrelated item.
- **Make outcomes explicit:** every review ends with an outcome, accountable decision-maker, conditions, owner, and next step.
- **Time-box disagreement:** if reviewers cannot agree by the defined deadline, document the positions and evidence, then escalate to the named authority.
- **Close the loop:** an approval is not complete until conditions and implementation checks have been verified or explicitly accepted by an authorised owner.

### 5.6 Decision records and exception registers

A **decision record** documents one architecture decision and its rationale. An **exception register** tracks authorised deviations and their continuing risk and review obligations. They are related but not interchangeable: a decision record may link to an exception record when a selected option deviates from a rule.

#### 5.6.1 Sample architecture decision record

All entries below are illustrative and intended to demonstrate the structure, not to prescribe a real bank's policy.

| Field | Example |
|---|---|
| Record ID / title | ADR-DA-017 — Ingestion pattern for transaction-monitoring feed |
| Status | Approved with conditions |
| Date / decision authority | Illustrative date; designated data-platform architecture authority |
| Decision owner | Named platform owner (role must be filled with an actual accountable person) |
| Decision question | Should the new feed use scheduled batch ingestion or event-driven ingestion? |
| Context | Operational dashboard requires more frequent updates than the current daily feed; source capabilities and downstream needs must be confirmed |
| Requirements / criteria | Freshness target to be validated; recoverability, duplicate handling, support burden, cost, access controls, and consumer compatibility |
| Options | A: scheduled batch; B: event-driven feed; C: retain current feed until source capability is confirmed |
| Evidence | Source delivery contract, representative volume profile, prototype results, cost estimate, consumer inventory, operational review; unavailable evidence must be marked as a gap |
| Decision | Select option B only if the source contract supports the required delivery behaviour and replay/duplicate controls pass acceptance tests |
| Rationale | Better alignment with the validated freshness need, provided operational and source constraints are met |
| Consequences | More operational complexity than batch; need for event monitoring, replay controls, idempotency, and support ownership |
| Conditions | Validate source event semantics; demonstrate duplicate/replay behaviour; publish ownership and support details before production release |
| Exception link | None if all standards are met; otherwise create a separate exception record before proceeding |
| Implementation owner | Named engineering lead |
| Conformance evidence | Test results, configuration review, access review as applicable, updated design, operational readiness checklist |
| Review triggers | Material volume change; source contract change; repeated freshness misses; new consumer purpose; cost outside agreed tolerance |
| Supersedes / related records | Link to any previous ingestion decision and related requirements |
| Review date / state | Set an actual date or event-based trigger; do not leave it blank after approval |

**How it is used:** engineers use the decision and conditions to guide implementation; reviewers use it to check conformance; operators use it to understand expected behaviour and triggers; future architects use it to understand why the choice was made and what evidence would justify changing it.

#### 5.6.2 Exception register template

| Field | What to record |
|---|---|
| Exception ID and status | Unique reference; proposed, approved, rejected, expired, or closed |
| Rule / principle being deviated from | Name the exact policy, standard, or principle and the version/scope where relevant |
| Requesting owner and affected scope | Accountable requester, systems, domains, consumers, and data involved |
| Reason and alternatives | Why conforming is infeasible or materially worse; alternatives considered |
| Risk and impact | Residual risk, affected quality attributes, downstream effects, and uncertainty |
| Compensating controls | Specific controls that reduce the risk, with evidence and an owner |
| Approval authority | Person or body with authority for this type of exception |
| Start, expiry, and review trigger | Time-bounded approval or explicit event-based review; avoid indefinite permission |
| Remediation / retirement plan | What will restore conformance, by whom, and by when |
| Evidence and monitoring | How controls and conditions are checked |
| Decision link | Link to the architecture decision record and implementation ticket |
| Review outcome | Renew, revise, close, or escalate; record why |

An exception is not approved merely because a delivery deadline exists. The decision-maker needs to understand the risk, alternatives, compensating controls, scope, owner, and end condition. If the organisation's policy or applicable obligation does not permit an exception, architecture governance cannot create permission by recording one.

### 5.7 Conformance: how implementation is checked

Conformance is the process of determining whether the implemented system aligns with the approved design and applicable standards. It is not the same as checking that an approval ticket exists.

A practical conformance plan answers:

- **What will be checked?** Interfaces, schemas, data ownership metadata, access paths, quality checks, retention settings, lineage, recovery behaviour, monitoring, or other relevant elements.
- **When?** During design, before release, at deployment, periodically in production, or after a material change.
- **What is the evidence?** Automated test results, configuration review, deployment manifests, catalogue records, operational metrics, or a focused manual review.
- **Who checks it?** An assigned engineer, architect, service owner, control owner, or independent reviewer depending on risk and local policy.
- **What happens when it fails?** Fix the implementation, seek a valid revised decision or exception, contain risk, or escalate. Do not silently reinterpret an approval.

Examples of drift include an unreviewed new consumer, a changed schema that breaks a contract, a production data path that bypasses the approved access model, an exception that has expired, or an implementation that cannot meet its approved freshness target.

Conformance should be risk-based. Automated checks are valuable for repeatable rules; manual review remains useful for context and trade-offs that cannot be reliably reduced to a test. A manual check with no evidence trail is difficult to repeat. An automated check that validates the wrong rule is consistently wrong.

### 5.8 Change control and reassessment

Architecture decisions depend on requirements, assumptions, constraints, technology, source behaviour, and operating evidence. When one of these changes materially, the team should ask whether the original decision remains valid.

**Reassessment triggers** can include:

- A business purpose or consumer population changes.
- A quality target is missed repeatedly or becomes materially more demanding.
- Data volume, velocity, or cost moves outside the assumptions used in the decision.
- A source contract, schema, ownership boundary, or authoritative system changes.
- A material incident reveals an unaddressed failure mode.
- A standard or principle changes.
- An exception reaches its expiry or its compensating control no longer works.
- A new dependency or cross-domain impact is discovered.
- A key assumption is disproved.

A changed requirement does not automatically mean the original architecture was wrong. It means the decision must be tested against the new context. Preserve the original record, record the new evidence, and create a superseding decision or linked change record. Do not silently overwrite the rationale that explains the previous state.

### 5.9 Intermediate exercise: design a three-tier model

Create a one-page governance model for a bank's data programme.

1. Define local, reviewed, and escalated decision tiers.
2. Give at least two examples for each tier.
3. Name the proposer, evidence contributors, decision authority, implementation owner, and conformance checker for each.
4. Define the minimum submission for reviewed and escalated decisions.
5. List all possible outcomes: approve, approve with conditions, reject, defer, return for revision, and escalate.
6. Draw the review flow and specify a turnaround expectation for each tier.
7. Explain what evidence could cause an initially local decision to be reclassified.

Do not use “the architecture board approves everything.” Make the boundary and authority explicit.

**Ability to demonstrate:** produce a governance flow in which a reader can identify the decision owner, required evidence, review path, outcomes, and implementation check without guessing.

## 6. Advanced-level learning sequence

### 6.1 Proportionality: rigour should follow risk

The roadmap's first advanced concept is proportionality: use a light touch for low-risk, reversible changes and rigorous review for high-risk, irreversible, or enterprise-wide decisions.

A proportional process does not mean “skip governance for small work.” It means **use the smallest control that reliably manages the risk**.

| Decision characteristic | Governance implication |
|---|---|
| Low impact, reversible, inside approved pattern | Local decision, concise record, automated checks where possible |
| Material but bounded impact, evidence available, reversible with manageable cost | Time-boxed review, options and trade-off evidence, conditions if needed |
| Cross-domain or enterprise-wide | Map affected owners and consumers; use broader review and named decision authority |
| Hard to reverse or costly to migrate | Examine transition and rollback strategy, long-term consequences, and evidence more carefully |
| Sensitive or high-impact data use | Involve the actual accountable specialist functions according to local policy and applicable obligations |
| Conflict with a mandatory rule | Do not treat it as a routine architecture preference; identify the authority and permitted path, if any |
| High uncertainty or missing evidence | Run a bounded experiment, defer, or escalate; do not manufacture certainty through a scorecard |

Risk classification should be based on impact and context, not only project size or technology novelty. A one-line change to an authoritative identifier may deserve more scrutiny than a large but isolated batch job.

### 6.2 Delegation versus broader review

A good governance design delegates decisions to the lowest level that has the context, competence, and authority to manage the consequences.

**Delegate when:**
- the decision stays within a documented approved pattern;
- the data owner and affected consumers are known;
- impact is bounded and reversible;
- applicable standards are clear and checkable;
- the team can supply evidence and own the outcome;
- no higher-authority risk acceptance is required.

**Require broader review or escalation when:**
- the decision changes enterprise semantics or an authoritative source;
- several domains or major consumers are affected;
- the choice creates a hard-to-reverse dependency or migration cost;
- there is a material unresolved conflict among requirements or principles;
- a policy, standard, or formally assigned decision boundary is crossed;
- residual risk exceeds the local owner's authority;
- the choice establishes a precedent that other domains are likely to copy.

Delegation is not abdication. The delegated team remains accountable for the decision and its evidence. Central governance retains responsibility for defining boundaries, making them visible, and checking whether the model is working.

### 6.3 How to resolve disagreements between architecture and delivery

Disagreement is normal. An architect may prefer a design that protects long-term interoperability; a delivery team may face a real deadline, legacy constraints, or a vendor limitation. Neither “architecture always wins” nor “delivery urgency always wins” is a sound decision rule.

Use a time-bounded resolution path:

1. **State the decision question.** Separate the business outcome from the preferred implementation.
2. **Make each position testable.** Identify the requirement, principle, constraint, risk, or cost each position is protecting.
3. **Identify common facts and disputed assumptions.** Mark evidence, estimates, and unknowns separately.
4. **Compare viable options.** Include a constrained or temporary option when appropriate, plus the cost of delay.
5. **Assess reversibility and blast radius.** What would happen if the decision proves wrong?
6. **Choose the authority based on the boundary.** A domain-level trade-off stays local only if the domain has authority over all affected consequences.
7. **Record the decision and dissent.** Capture why the chosen option is acceptable, what risks remain, and what evidence would reopen it.
8. **Set a deadline and owner.** An unresolved disagreement cannot remain indefinitely in an informal chat.
9. **Reassess from evidence.** If the agreed trigger occurs, reopen the decision rather than defending it as a matter of status.

The review forum should not decide business risk that belongs to a business or risk owner. It should expose the trade-off, ensure the right authority decides, and preserve the rationale.

### 6.4 Advanced worked scenario: disputed customer-data architecture

**Illustrative scenario.** A bank's customer domain owns an operational customer master. A marketing analytics team proposes a separate customer profile store to meet a new audience-segmentation deadline. The analytics team argues that a separate store is faster to query and allows it to iterate independently. The customer-domain architect objects that duplicate authoritative attributes could diverge, confusing downstream consumers. The platform team warns that keeping the second store fresh adds cost and operational failure modes. The scenario does not assume a particular bank policy or a specific regulatory rule; actual data-use, privacy, and control obligations must be determined by the organisation's accountable specialists.

#### The disputed decision

“May the marketing analytics team maintain a separate customer profile store, and if so, what data and authority may it contain?”

This is not simply a database choice. It affects authoritative ownership, duplicate attributes, data quality, consumer expectations, refresh behaviour, and cross-domain support.

#### Evidence requested

| Evidence | Why it matters | Illustrative finding |
|---|---|---|
| Business requirement and deadline | Clarifies whether the need is latency, analytical flexibility, or a specific business outcome | Segmentation needs a query-optimised view, but not necessarily a second authoritative customer master |
| Data element inventory | Separates copied identifiers/attributes from derived analytical features | Some attributes are authoritative source fields; other values are derived segments |
| Consumer and dependency map | Shows who might treat the new store as authoritative | Two downstream teams might reuse the profile unless the contract is explicit |
| Freshness and quality measurements | Tests whether synchronisation can meet actual need | Current batch process has not been measured against a validated target |
| Options and cost estimate | Avoids framing duplication as the only way to meet the deadline | A governed read model or derived data product may meet the query need with less semantic ambiguity |
| Operational and recovery design | Shows how stale or partial updates are detected and repaired | Proposed design lacks reconciliation and clear recovery ownership |
| Data-use and specialist assessment | Identifies whether the intended use and fields are permitted under applicable internal rules and obligations | Assessment remains an explicit dependency; no approval is assumed |
| Migration/rollback plan | Limits the impact if the choice is wrong | Team can begin with a bounded pilot and retire it if criteria fail |

#### Governance path

1. **Triage:** this is not a local decision because it may create a competing source of truth and affect other domains.
2. **Review:** the domain owner, platform lead, architecture reviewer, business owner, and relevant specialists examine the options and evidence.
3. **Clarify the semantic boundary:** the proposed store may contain derived features and a read-optimised projection, but it must not silently claim authority for fields owned by the customer domain.
4. **Compare options:** (A) duplicate and independently maintain a customer master; (B) build a read-optimised derived data product with explicit lineage and refresh behaviour; (C) improve access to the authoritative source; (D) defer the feature until required evidence is available.
5. **Resolve the conflict:** if a shared principle or enterprise boundary is at stake, escalate to the named authority rather than letting one team unilaterally set the precedent.
6. **Record the outcome:** include the decision, rejected options, rationale, conditions, accountable owner, implementation owner, and review triggers.
7. **Verify:** check that the implemented data product identifies its authoritative source, clearly labels derived attributes, measures freshness, handles reconciliation, and publishes ownership/support information.
8. **Revisit:** if consumers start treating the read model as authoritative, reconciliation fails, or the business use changes, trigger a new review.

#### Illustrative outcome

The authority approves a bounded, read-optimised derived data product, not an independently authoritative customer master, **subject to** confirmed data-use approval, documented field-level lineage, freshness and reconciliation tests, explicit ownership, and a consumer contract. If the conditions cannot be met, the release is deferred or the proposal is revised. The rationale is that the business query need can be served without unnecessarily splitting authority over core customer attributes.

This outcome is not universally correct. If evidence showed that the authoritative system could not meet a validated requirement and a separate authority was explicitly justified, another option might be defensible. The important lesson is that the governance path makes the trade-off, authority, evidence, conditions, and review trigger explicit.

### 6.5 Measuring governance effectiveness

The roadmap explicitly names these measures: **review turnaround time, proportion of changes reviewed, exception counts and age, conformance findings, and delivery teams' feedback.** Measures should be defined precisely enough that different people would calculate them consistently.

| Measure | Operational definition | How to collect it | What it can reveal | Interpretation caution |
|---|---|---|---|---|
| Review turnaround time | Elapsed business time from a complete submission to a recorded decision; report median and a high percentile, such as P90 | Timestamp intake completeness and final decision in the workflow system | Queues, unclear ownership, repeated rework, overloaded reviewers | A low average can hide very long waits; exclude or separately report time awaiting requester evidence |
| Proportion of changes reviewed | Number of changes that required review and received the required review divided by all changes classified as requiring review in the same period | Compare change/deployment records with the tier classification and review register | Under-review, late engagement, or excessive review scope | A high proportion is not automatically good if too many low-risk changes are classified as review-required |
| Exception count and age | Count active exceptions and measure age from approval to current date; segment by standard, owner, risk, and expiry | Exception register with status, owner, expiry, and review date | Repeated design gaps, weak standards, expired deviations, or unowned remediation | A rising count can reflect better discovery as well as worsening architecture; investigate causes |
| Conformance findings | Number and severity of implementation deviations found per review/release/period, with closure time and recurrence | Conformance checks, release reviews, production findings, and remediation tickets | Design-to-implementation drift and ineffective checks | More findings can initially mean detection improved; track severity, recurrence, and time to closure |
| Delivery-team feedback | Structured feedback on clarity, usefulness, timeliness, and rework caused or avoided by governance | Short periodic survey, retrospectives, and sampled interviews | Whether teams understand the process and can get decisions in time | Satisfaction alone does not prove sound decisions; triangulate with risk and conformance evidence |

#### 6.5.1 Avoid metric gaming

- Do not optimise turnaround time by issuing shallow approvals without reading the evidence.
- Do not maximise review coverage by sending every trivial decision to a committee.
- Do not treat zero exceptions as success; it may mean teams hide deviations or the process is inaccessible.
- Do not assume more conformance findings automatically mean worse implementation; detection may have improved.
- Do not rely only on team satisfaction; a popular shortcut may create unacceptable risk.
- Segment results by decision tier, complexity, and whether the submission was complete.
- Use a baseline and trend before setting numerical targets. A precise target without a baseline or reason can create false confidence.

### 6.6 Three failure modes and their fixes

The roadmap asks you to evaluate a governance process, identify three failure modes, and propose changes with measures. The following examples illustrate a disciplined diagnosis.

#### Failure mode A — Rubber-stamp review

**Symptom:** most proposals are approved quickly, but later incidents reveal unresolved dependencies or untested assumptions.

**Likely causes:** criteria are vague; reviewers lack evidence; meeting time is spent on slides; approval is treated as a formality.

**Changes:** require a clear decision question and evidence; record material assumptions and dissent; sample decisions for outcome quality; use targeted deep reviews for high-risk cases.

**Measures:** conformance findings and recurrence; proportion of reviews returned for missing evidence; incident links to architecture decisions; reviewer and delivery feedback.

#### Failure mode B — Gatekeeping and long queues

**Symptom:** review queues take six weeks, teams ship before approval, or reviewers are asked to approve after implementation.

**Likely causes:** all decisions follow one path; decision rights are unclear; submissions are incomplete; no service expectation exists; forum membership is too broad; low-risk decisions are not delegated.

**Changes:** introduce the three-tier model; define minimum evidence; publish review turnaround expectations; assign a triage owner; allow asynchronous review for suitable decisions; establish a time-bounded escalation path.

**Measures:** median/P90 turnaround by tier; percentage of complete submissions; late-review rate; delivery feedback; number and age of unresolved items.

#### Failure mode C — Stale standards and recurring exceptions

**Symptom:** ten teams receive exceptions to the same standard, or nobody can explain whether a standard is current.

**Likely causes:** standard is infeasible, outdated, unclear, or mismatched to actual workloads; exception owners are not tracked; lessons from approvals do not feed back into standards.

**Changes:** analyse the common root cause; decide whether the standard is still justified; revise or retire it if evidence supports that; define a migration path; keep temporary exceptions bounded; communicate the change and update automated checks.

**Measures:** recurring exception rate by standard; active exception age; expiry breaches; conformance findings; adoption of the revised standard; delivery impact after change.

### 6.7 How to decide which standards to retire or revise

A standard should not be removed simply because teams dislike it, nor retained solely because it has always existed. Review it when evidence shows repeated exceptions, inability to test conformance, outdated assumptions, disproportionate delivery cost, conflict with a more important requirement, or absence of a clear owner.

For each candidate standard, ask:

1. What risk or inconsistency was it created to prevent?
2. Is that risk still material and supported by evidence?
3. Is the standard specific enough to check?
4. Do recurring exceptions indicate a narrow edge case or a systemic mismatch?
5. Could the standard be clarified, scoped, automated, replaced by a guideline, or retired?
6. What migration or compatibility consequences would a change create?
7. Who is authorised to approve the change and communicate it?
8. How will the organisation measure whether the revised rule improves outcomes?

The output should be a recorded decision: retain, clarify, revise, narrow scope, replace, or retire. Include owner, effective date, transition plan if needed, and the measure used to evaluate the change.

### 6.8 Scenario analysis: three recurring governance problems

#### Scenario 1 — A team ships first and asks for approval afterwards

**What it indicates:** the team may have been blocked, decision rights may be unclear, the process may be too slow, or the team may have bypassed a known requirement. The fact of late review alone does not prove which cause applies.

**Response:**
1. Contain any immediate material risk and establish what actually shipped.
2. Determine the decision tier and whether the required authority was bypassed.
3. Compare the implementation with the applicable standards and approved design.
4. Record the actual deviation; do not backdate or pretend the review happened before release.
5. Decide whether to accept temporarily, remediate, roll back, or escalate based on authority and evidence.
6. Investigate the process cause separately from the individual action.
7. Track corrective actions and a measure such as late-review rate by tier.

**Resulting artefacts:** incident/change record where applicable, conformance finding, decision or exception record, and process-improvement action.

#### Scenario 2 — Review queues take six weeks

**What it indicates:** governance may be a delivery bottleneck, but the queue duration alone does not reveal the root cause. The team should separate time waiting for a reviewer from time spent collecting missing evidence or resolving a real design issue.

**Response:**
1. Break down elapsed time into intake completeness, queue wait, review, revision, and decision.
2. Segment by tier and proposal type.
3. Inspect whether local decisions are unnecessarily routed to the forum.
4. Check reviewer capacity, decision authority, agenda design, and quality of submissions.
5. Add a triage owner, minimum evidence checklist, published turnaround expectations, and escalation deadline.
6. Use asynchronous review where it preserves evidence and accountability.
7. Monitor P50/P90 turnaround, rework, late approvals, conformance findings, and delivery feedback after changes.

**Resulting artefacts:** queue analysis, revised tier model or workflow, named owners, and before/after measures.

#### Scenario 3 — Ten exceptions to the same standard have been approved

**What it indicates:** potentially a systemic design or standard problem, not ten independent one-off problems. However, exceptions may also be justified by distinct temporary circumstances, so examine their causes before changing the rule.

**Response:**
1. Group exceptions by reason, system, owner, risk, and expiry.
2. Identify whether they share a root cause or merely share a label.
3. Reassess the standard's intent, feasibility, scope, and evidence.
4. Evaluate whether a revised standard or approved pattern can manage the risk more directly.
5. Obtain the correct authority for the standard change.
6. Define transition steps for active exceptions; do not automatically erase their conditions.
7. Close, renew, or replace each exception explicitly.
8. Measure recurrence, exception age, expiry breaches, and conformance after the change.

**Resulting artefacts:** root-cause analysis, standard decision, updated standard or guideline, exception-register updates, and follow-up measures.

### 6.9 Industry-application exercise: bank architecture review process

Design a review process for a bank's data programme, including a **regulator-driven change** as required by the roadmap. Treat “regulator-driven” as a change trigger in the scenario, not as a claim about any particular regulation. The exact obligation, deadline, scope, and evidence must be supplied by the bank's accountable legal, compliance, risk, or regulatory-change function.

Your design must specify:

1. How a regulatory or policy change enters the architecture lifecycle.
2. How the bank confirms the authoritative interpretation, impacted data domains, systems, interfaces, consumers, and delivery deadline.
3. Which changes can be local, which require review, and which require escalation.
4. Who can provide specialist interpretation, who owns the architecture decision, and who approves residual risk or policy exceptions under the bank's actual authority model.
5. The evidence needed for options, data lineage, quality attributes, operational readiness, migration, and conformance.
6. The review outcomes and the way conditions and dissent are recorded.
7. How the implementation is checked against the approved decision.
8. How the bank detects a changed interpretation, missed milestone, failed control, or new downstream impact.
9. How the process avoids using a regulatory deadline as a blanket reason to skip governance.
10. What evidence will show that the governance process is both timely and effective.

**Deliverable:** a one-page workflow plus a role/decision-rights table and a sample decision record for the illustrative change. Clearly label unknowns and assumptions.

### 6.10 Industry-application exercise: five governance measures

Choose the five measures named in section 6.5. For each, document:

- operational definition and calculation;
- data source and collection method;
- accountable metric owner;
- reporting cadence;
- segmentation (at minimum, by decision tier where relevant);
- baseline period and known data-quality limitations;
- interpretation and possible gaming;
- action threshold or review question;
- how the measure will be used to improve governance.

Do not invent a target such as “all reviews must finish in 24 hours” without a baseline, risk rationale, and stakeholder agreement. You may propose an initial hypothesis, but label it as such and define how it will be validated.

**Ability to demonstrate:** critique governance with measurable evidence rather than relying on whether the process feels strict or friendly.

## 7. Industry-application exercises

Complete these exercises in the order below. They are aligned to the roadmap's explicit industry exercises and scenarios.

### Exercise A — Bank data-programme review process

Produce the workflow described in section 6.9. Include the regulator-driven change path, decision tiers, role boundaries, evidence, outcomes, conformance, and reassessment triggers. Do not claim compliance; the exercise demonstrates architecture governance design, not regulatory validation.

### Exercise B — Decision record and exception register

Create:
1. One filled architecture decision record for a meaningful data architecture choice.
2. One blank reusable decision-record template.
3. One exception register with at least one proposed or approved example, clearly labelled as a teaching scenario.
4. A link between the exception and the decision that relies on it.
5. A review trigger, accountable owner, evidence, and end condition.

Make it possible for someone who did not attend the meeting to understand what was decided and why.

### Exercise C — Five governance measures

Define and collect, or design the collection process for, the five measures in section 6.5. If you do not have real organisational data, create a small **synthetic dataset** and label it synthetic. Do not present synthetic numbers as observed performance.

### Exercise D — Three-tier decision model

Classify at least nine sample changes: three local, three reviewed, and three escalated. For each, explain the impact, reversibility, cross-domain reach, applicable standards, authority boundary, and evidence that could change the classification.

### Exercise E — Governance critique

Evaluate a hypothetical process with the following symptoms:
- all changes require the same committee;
- submissions often lack current-state information;
- teams report long queues;
- exceptions have no expiry;
- production changes are rarely checked against the approved design;
- no one knows who can decide a cross-domain dispute.

Identify at least three failure modes, distinguish symptoms from root causes, and propose changes with measures. Include at least one risk of overcorrecting (for example, delegating too broadly without clear boundaries).

## 8. Practical scenarios and case-based reasoning

The following scenarios are intended to be reasoned through using the lifecycle, decision tiers, and evidence-based governance process. Organisational details are illustrative.

### 8.1 A team ships first and asks for approval afterwards

**Context:** a delivery team deploys a new data path before a required architecture review and then requests retrospective approval.

**Stakeholders:** delivery lead, data/domain owner, architect, platform/service owner, the relevant decision authority, and specialist risk/control owners if the change affects their remit.

**Risks:** unreviewed dependencies, incorrect ownership, contract incompatibility, operational gaps, or an unapproved exception. The severity depends on what shipped and its impact; do not assume every late review has the same risk.

**Decision rights:** the team may explain and remediate the implementation but cannot retroactively manufacture approval. The authorised decision-maker determines the acceptable path within their authority. A risk outside that authority must be escalated.

**Required evidence:** actual implementation, affected consumers, tests and monitoring, applicable standard, impact assessment, release/change record, and the reason the process was bypassed.

**Governance steps:** establish facts; classify risk; contain material harm if necessary; check conformance; record deviation; decide rollback/remediation/temporary exception/escalation; investigate the process cause; track closure.

**Resulting artefacts:** deviation/conformance record, decision record, exception record if permitted and needed, and corrective action.

**Review conditions:** new evidence of impact, failed controls, recurrence, or an expiring exception triggers reassessment.

### 8.2 Review queues take six weeks

**Context:** the architecture review queue has a six-week elapsed time.

**Stakeholders:** proposers, reviewers, architecture governance owner, delivery managers, domain/platform owners, and the named escalation authority.

**Risks:** delayed business value, late engagement, pressure to bypass governance, and rushed decisions near release. Some complex proposals may legitimately require more analysis; the process should identify that rather than treating all waiting time as committee delay.

**Decision rights:** governance owner may redesign intake and routing within delegated authority; changes to decision rights or risk acceptance must be approved by the relevant authority.

**Required evidence:** timestamped intake and review events, submission completeness, tier, proposal type, revision count, reviewer capacity, outcome, and delivery-team feedback.

**Governance steps:** decompose queue time; segment by tier; identify rework and authority bottlenecks; delegate eligible low-risk decisions; publish service expectations; add triage and time-bounded escalation; reassess after implementation.

**Resulting artefacts:** queue analysis, updated workflow, decision-rights table, and measure baseline.

**Review conditions:** P90 turnaround, late reviews, rework, or conformance worsens after the change; adjust the model rather than assuming faster is always better.

### 8.3 Ten exceptions to the same standard

**Context:** ten approved exceptions refer to one standard.

**Stakeholders:** standard owner, exception owners, domain/platform teams, architecture governance, and risk/control owners where relevant.

**Risks:** a standard may be infeasible, vague, stale, or poorly scoped; alternatively, exceptions may be temporary and individually justified. The count alone cannot settle the question.

**Decision rights:** exception owners manage their approved conditions; the designated standard owner proposes revision; the authority that owns the standard approves changes; exceptions outside delegated risk boundaries are escalated.

**Required evidence:** reason, age, expiry, residual risk, compensating controls, systems affected, repeated causes, and conformance outcomes.

**Governance steps:** group and analyse exceptions; identify root cause; test whether the standard's purpose still matters; compare clarify/revise/narrow/replace/retire options; approve a standard change through the right authority; reconcile each active exception; communicate and verify the new rule.

**Resulting artefacts:** exception root-cause analysis, standard decision, updated standard or guideline, revised register, and follow-up measures.

**Review conditions:** recurrence, expiry breaches, failed controls, or new evidence about the underlying risk.

### 8.4 Banking scenario: a regulator-driven reporting change

**Illustrative scenario:** a bank receives an internally validated change request tied to a reporting obligation. The precise rule, interpretation, and due date are not supplied here and must not be inferred from this lesson.

**Context:** reporting fields and lineage may need to change across source systems, transformation logic, curated datasets, and a reporting consumer. Some systems may be owned by different domains.

**Stakeholders:** accountable business/reporting owner, data/domain owners, data architect, data engineering and platform teams, operational owner, and the bank's designated regulatory-change, legal, compliance, risk, or control specialists as applicable.

**Risks:** incorrect interpretation, incomplete lineage, inconsistent field meaning, missed delivery date, untested migration, unintended effects on other consumers, and a rushed implementation with insufficient evidence.

**Decision rights:** the responsible specialist function establishes the applicable interpretation under the bank's operating model; data owners confirm semantics and affected assets; architecture authority resolves cross-domain design decisions; the designated authority handles any risk acceptance or exception within its actual mandate.

**Required evidence:** validated change interpretation and deadline; current-state inventory and lineage; impacted domains and consumers; target requirements; options and trade-offs; source and transformation tests; migration/recovery plan; operational readiness; conformance evidence.

**Governance steps:**
1. Register the change and authoritative interpretation.
2. Trace impacted assets, owners, contracts, consumers, and dependencies.
3. Assess urgency and risk without treating urgency as automatic permission to bypass controls.
4. Classify decisions by tier; escalate cross-domain or authority-boundary issues.
5. Record the decision, conditions, residual risks, and timeline.
6. Implement with traceable tests and deployment controls.
7. Verify that the delivered outputs meet the validated requirement and approved design.
8. Monitor for interpretation changes, failures, and downstream effects.

**Resulting artefacts:** change impact map, requirements and evidence pack, decision record(s), implementation plan, conformance evidence, and monitoring/reassessment actions.

**Review conditions:** updated interpretation, changed deadline, source-data change, failed validation, missed target, new consumer impact, or a material assumption becoming false.

### 8.5 Banking scenario: real-time dashboard versus cost and complexity

This scenario appears in the previous lesson's trade-off context and is useful here because it demonstrates why governance must connect requirements, decision rights, and monitoring rather than merely approve a technology.

**Context:** business stakeholders request real-time or near-real-time dashboards; platform engineers warn that event-driven ingestion increases cost and operational complexity.

**Stakeholders:** business/product owner, data owner, data architect, platform/data engineering, service operations, finance/cost owner, and relevant specialist functions if the data use requires them.

**Risks:** over-engineering if the actual need is slower; stale or misleading information if the target is not met; added failure modes and support burden; cost that does not justify business value.

**Decision rights:** the business owner validates the freshness need; architecture compares patterns; platform/operations assess operability and cost; the decision authority is selected based on cross-domain impact and reversibility.

**Required evidence:** validated freshness target and consequence of delay; source delivery capabilities; representative volume; options; measured prototype or workload estimate; recovery design; service ownership; cost range and uncertainty.

**Governance steps:** state the decision question; compare batch, micro-batch, event-driven, or other viable patterns at the level needed; make quality-attribute trade-offs explicit; approve a bounded pilot if uncertainty is high; define acceptance criteria and review triggers; monitor actual freshness, incidents, and cost.

**Resulting artefacts:** options comparison, decision record, pilot acceptance criteria, implementation/conformance evidence, and post-release measurement.

**Review conditions:** target misses, volume growth, recurring operational incidents, cost outside agreed tolerance, or a changed business use.

### 8.6 Banking scenario: exception to a single system of record

**Context:** a domain requests a second copy of a core customer or account attribute because the current source is difficult to query or does not meet a consumer's latency needs.

**Stakeholders:** authoritative data owner, requesting domain, architecture authority, platform and service owners, affected consumers, and relevant specialist functions according to the data and intended use.

**Risks:** inconsistent values, ambiguous authority, reconciliation burden, stale consumers, unclear correction propagation, and a temporary workaround becoming permanent.

**Decision rights:** the owner of the authoritative data definition and the authority governing cross-domain semantics must be involved. A local team cannot independently redefine enterprise authority if it lacks that mandate.

**Required evidence:** exact attributes to be copied, purpose, authoritative source, consumer contract, freshness and consistency requirements, reconciliation method, correction propagation, operational owner, alternatives, and retirement condition.

**Governance steps:** determine whether the request is for a cache/read model/derived product or a competing authoritative record; compare alternatives; assess risk and reversibility; if deviation is justified and permitted, record a bounded exception with controls, owner, expiry, and exit plan; verify implementation; review at the trigger.

**Resulting artefacts:** decision record, exception record if a rule is genuinely violated, data contract, reconciliation evidence, and retirement/review plan.

**Review conditions:** divergence, new consumers, expired exception, change in source capability, failed reconciliation, or a change in the attribute's business meaning.

## 9. Expected outputs or deliverables

The roadmap specifies these deliverables:

- Lifecycle diagram with artefacts.
- Decision-rights table.
- Review process flow and a decision record template.
- Governance measures list.
- Answers to Topic 05 practice questions.

The exercises in this lesson operationalise those outputs. Use the following checklist to make them reviewable.

| Deliverable | Minimum contents | Quality test |
|---|---|---|
| Lifecycle diagram | Seven prescribed stages, arrows, feedback loop, artefact at each stage | A reader can identify what output exists before the next stage and where operational evidence returns to design |
| Decision-rights table | Local/reviewed/escalated tiers; proposer, contributors, decision authority, implementer, verifier | No material decision relies on ambiguous “team approval”; authority boundaries are explicit |
| Review flow | Intake, triage, evidence, review, outcomes, escalation, implementation, conformance, closure | The path covers approve, conditional approval, reject, defer, revision, and escalation |
| Decision record template | Question, context, requirements, options, evidence, decision, rationale, consequences, conditions, owners, links, triggers, status | Someone who missed the meeting can understand what was decided and why |
| Exception register | Exact rule, scope, reason, risk, controls, authority, owner, expiry/review trigger, remediation, evidence, decision link | No exception is informal, unowned, unbounded, or treated as automatically permissible |
| Governance measures list | Five roadmap measures with definitions, collection method, owner, cadence, caveats, and use | Metrics are calculable, interpretable, and not treated as targets without a baseline |
| Practice-question answers | Answers to Topic 05 questions, corrected after review | Answers explain reasoning and acknowledge assumptions rather than merely repeat terms |

### 9.1 Reusable decision record template

Copy and adapt this template. Keep fields that are relevant to the decision; mark genuinely inapplicable fields as “not applicable” with a reason rather than deleting important context without explanation.

```markdown
# Architecture Decision Record

- ID:
- Title:
- Workflow status: Proposed | In review | Awaiting evidence | Decision recorded | Implementing | Conformance check | Closed | Superseded
- Decision outcome (when decided): Approve | Approve with conditions | Reject | Defer | Return for revision | Escalate | Not applicable yet
- Date:
- Decision owner / authority:
- Proposer:
- Implementation owner:
- Reviewers / specialist contributors:
- Related requirements, standards, principles, and records:

## Decision question
What exact question needs a decision?

## Context and current state
What is true now? Which facts are verified, and which are assumptions?

## Requirements and constraints
List the business outcome, measurable quality targets, constraints, dependencies, and deadline.

## Options considered
For each option, state benefits, costs, risks, reversibility, and evidence.

## Evidence and gaps
Link tests, metrics, diagrams, cost estimates, source contracts, or specialist assessments.
List missing evidence and its owner.

## Decision and rationale
What was selected, by whom, and why? Why were material alternatives not selected?

## Consequences and residual risks
What becomes easier or harder? Which risks remain?

## Conditions and actions
| Action / condition | Owner | Due date | Evidence required | Release-blocking? | Status |
|---|---|---|---|---|---|

## Exception
- Is an exception required?
- Exact rule and scope:
- Linked exception ID:
- If none, why not?

## Conformance plan
What will be checked, by whom, when, and with what evidence?

## Review triggers
What changed fact, metric, incident, expiry, or assumption would reopen this decision?

## Related / superseding decisions
Links and relationship to earlier records.
```

### 9.2 Reusable exception-register row template

```markdown
| Exception ID | Rule / version | Scope | Requesting owner | Reason / alternatives | Risk and impact | Compensating controls | Approval authority | Status | Start date | Expiry / review trigger | Remediation / retirement owner and date | Evidence / monitoring | Linked ADR / implementation | Last review and outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EX-001 (illustrative) | [rule and version] | [systems, data, consumers] | [named role] | [reason and options considered] | [risk and residual risk] | [controls and verification] | [authorised role] | Proposed / approved / expired / closed | [date] | [date or event] | [owner and date] | [evidence links and cadence] | [ADR ID/link] | [date and outcome] |
```

The row is an illustrative example, not an approved exception. In an actual register, use one consistent column layout, a unique identifier, an explicit state, and a named approval authority; do not treat a proposed record as permission to proceed.

## 10. Common mistakes and misconceptions

The roadmap explicitly warns against treating governance as approval gates only, applying the same rigour to every change, engaging after design is complete, writing standards that cannot be checked, and failing to record decisions. The following expands those points into practical diagnostic guidance.

### 10.1 Treating governance as a committee meeting

**Mistake:** governance is equated with a monthly board meeting.

**Why it fails:** the board cannot replace clear delegated decision rights, standards, records, implementation checks, or operational feedback.

**Better practice:** define the full workflow, including local decisions, asynchronous review, escalation, exception management, conformance, and reassessment.

### 10.2 Applying identical rigour to every change

**Mistake:** a small reversible change and an enterprise-wide authority change need the same approval path.

**Why it fails:** low-risk work queues behind high-impact decisions, and teams learn to bypass the process.

**Better practice:** use explicit local/reviewed/escalated tiers, and reclassify when new evidence changes the risk.

### 10.3 Engaging architecture after design is complete

**Mistake:** architecture is invited only to approve a near-final implementation.

**Why it fails:** meaningful options may already be too expensive to change; review becomes a rubber stamp or creates late rework.

**Better practice:** identify the decision question and tier during discovery or early design. Seek review when options are still open.

### 10.4 Writing standards that cannot be checked

**Mistake:** a standard says “data should be high quality” or “use modern technology.”

**Why it fails:** the statement cannot reliably determine whether a design conforms.

**Better practice:** define scope, owner, specific expectation, evidence, and exception path. For quality, state a measure and method where appropriate.

### 10.5 Not recording decisions

**Mistake:** the rationale lives only in meeting minutes, chat, or someone's memory.

**Why it fails:** teams repeat old debates, lose context when staff change, and cannot distinguish an intentional trade-off from accidental drift.

**Better practice:** keep a concise decision record with context, options, rationale, consequences, authority, conditions, and review triggers.

### 10.6 Treating an exception as permanent approval

**Mistake:** an exception has no owner, expiry, controls, or retirement plan.

**Why it fails:** temporary deviation becomes the de facto standard without explicit risk acceptance.

**Better practice:** bound the scope, identify the actual authority, define compensating controls, track evidence, and set an expiry or review trigger. Never assume all rules are waivable.

### 10.7 Confusing attendance with authority

**Mistake:** a specialist attended the meeting, so the team assumes the specialist approved the proposal.

**Why it fails:** participation and formal decision rights are different.

**Better practice:** record the decision authority and distinguish advice, concurrence, approval, and risk acceptance according to the organisation's actual authority model.

### 10.8 Treating approval as proof of implementation correctness

**Mistake:** a ticket says “approved,” so no one checks production.

**Why it fails:** implementation may diverge, conditions may be missed, or assumptions may be false.

**Better practice:** define conformance evidence and owners before release, and check it at the appropriate point.

### 10.9 Measuring activity instead of effectiveness

**Mistake:** count meetings, pages, or approvals and conclude governance is effective.

**Why it fails:** activity does not show decision quality, delay, conformance, or user impact.

**Better practice:** use the five roadmap measures, segment them by tier, and interpret them together with risk and delivery evidence.

### 10.10 Using precise-looking targets without evidence

**Mistake:** declare that every review must finish in one day without knowing decision complexity, baseline turnaround, or capacity.

**Why it fails:** the metric can incentivise rubber-stamping or misclassifying decisions.

**Better practice:** establish a baseline, define measurement boundaries, identify the desired outcome, and validate any target with stakeholders.

### 10.11 Escalating every disagreement

**Mistake:** the central authority is asked to settle every local technical debate.

**Why it fails:** escalation loses meaning and central reviewers become a bottleneck.

**Better practice:** first clarify decision boundaries and use evidence; escalate only when impact, risk, irreversibility, cross-domain reach, or authority requires it.

### 10.12 Treating urgency as an exception by itself

**Mistake:** a deadline is used as the only justification to bypass a standard.

**Why it fails:** urgency does not remove the consequences of the design or grant authority to accept risk.

**Better practice:** state the deadline, evaluate a safe minimum path, involve the actual authority, record residual risk and controls, and set a short reassessment trigger. Where no permitted exception exists, escalate or change the delivery plan.

## 11. Mastery criteria

You have mastered this lesson when you can demonstrate all three outcomes prescribed by the roadmap:

1. **Describe the lifecycle and artefacts accurately.** Explain the seven stages in order, identify the main output of each, and show the feedback loop from operation to reassessment.
2. **Design proportionate governance with clear decision rights.** Create local/reviewed/escalated tiers, define proposal and approval authority, specify review evidence and outcomes, record decisions and exceptions, and show how implementation is checked.
3. **Critique a process using measurable indicators.** Use the five named governance measures, distinguish symptoms from causes, identify at least three failure modes, and propose changes with measures that could confirm or disconfirm improvement.

### 11.1 Self-assessment rubric

| Level | Evidence |
|---|---|
| Not yet demonstrated | Can repeat definitions but cannot show how a decision moves through the lifecycle or identify who has authority |
| Developing | Can draw the lifecycle and identify outputs, but tiers, evidence, exception controls, or conformance are incomplete |
| Competent | Produces a clear lifecycle diagram, decision-rights table, review flow, record template, and five calculable measures |
| Strong | Handles a cross-domain disagreement, explains trade-offs and residual risk, and sets review triggers without overstating certainty |
| Industry-ready for this lesson | Produces a coherent governance design, labels assumptions, explains escalation and exception boundaries, and critiques effectiveness using evidence rather than meeting volume |

This rubric evaluates the learning artefacts, not professional certification or proof of regulatory compliance.

### 11.2 Practice questions

Answer each question in your own words, then correct the answer against the lesson.

1. What is the difference between the architecture lifecycle and architecture governance?
2. Name the seven lifecycle stages and one artefact produced at each.
3. What is the difference between a policy, a standard, a guideline, a principle, and a decision record?
4. Why is a standard that cannot be checked difficult to govern?
5. What is the difference between a local, reviewed, and escalated decision?
6. What factors can move a decision from local to reviewed or escalated?
7. Who should propose, contribute to, approve, implement, and verify a material architecture decision?
8. What minimum information should a reviewer receive before deciding?
9. Explain the difference between approve, approve with conditions, reject, defer, return for revision, and escalate.
10. Why is an exception record not the same as an architecture decision record?
11. What evidence can establish implementation conformance?
12. Name the five governance measures specified by the roadmap and explain one limitation of each.
13. How would you investigate a six-week review queue?
14. What does a repeated set of exceptions to the same standard suggest, and what additional evidence is needed before changing the standard?
15. How should a team respond when a new requirement invalidates an earlier architecture assumption?
16. In the disputed customer-data scenario, why might a derived read model be preferable to an independently authoritative customer master? What evidence could justify another choice?
17. How can a bank govern a regulator-driven change without treating the deadline as blanket permission to skip controls?
18. Give an example of a governance metric that could be gamed and describe how you would detect the gaming.

### 11.3 Answer-quality checklist

For each answer, check whether it:

- uses the lesson's terminology accurately;
- distinguishes source facts, assumptions, and illustrative values;
- identifies accountable decision rights rather than vague “team approval”;
- explains why the process works, not only what its steps are;
- describes an artefact or evidence that would make the claim reviewable;
- recognises trade-offs and limitations;
- avoids claiming that the example is a universal policy or regulatory requirement.

## 12. Completion gate

Do not mark Topic 05 complete until every item below is satisfied.

- [ ] Lifecycle diagram, decision-rights table, and record template complete.
- [ ] Governance critique reviewed by a peer.
- [ ] Topic 05 practice questions answered and corrected.

Use the following detailed acceptance checks to verify the roadmap gate:

| Gate item | Pass condition | Evidence to retain |
|---|---|---|
| Lifecycle diagram | All seven stages are present, with an artefact at each stage and an explicit feedback loop | Diagram or one-page lifecycle document |
| Decision-rights table | Local, reviewed, and escalated decisions are distinguishable; proposer, contributors, authority, implementer, and verifier are named by role | Decision-rights table |
| Record template | Captures context, decision question, options, evidence, rationale, consequences, authority, conditions, conformance, and review triggers | Reusable architecture decision record template |
| Governance critique | A peer reviews the critique; findings are categorised and improvements have measures | Peer comments and revised critique |
| Practice questions | All 18 questions are answered and corrected; unsupported claims and unclear reasoning are fixed | Answer document and correction notes |

**Completion standard:** you can explain the lifecycle and artefacts, design a proportionate process with explicit decision rights, and evaluate whether governance supports or obstructs delivery using measurable evidence. Keep the final artefacts concise enough to use in practice and complete enough to be audited later.

---

## Scope and assumption note

This lesson's prescribed sequence and required deliverables come from Module 5 of `roadmap-Data-Architecture-Foundations-and-Principles.md`. The Stage 2D project tree places this file at `Stage 2D — Data Architecture/01-Data-Architecture-Foundations-and-Principles/05-data-architecture-lifecycle-and-governance.md`, alongside lessons 01–04 and 06, `practice-questions.md`, and the module's current-state inventory project.

Supporting explanations, tables, sample roles, workflow, and banking cases are instructional elaborations of the prescribed concepts. Organisational role names, thresholds, service times, target values, and scenario findings are illustrative unless explicitly described as roadmap requirements. No actual organisation's policy, legal interpretation, or regulatory compliance has been verified by this lesson.
