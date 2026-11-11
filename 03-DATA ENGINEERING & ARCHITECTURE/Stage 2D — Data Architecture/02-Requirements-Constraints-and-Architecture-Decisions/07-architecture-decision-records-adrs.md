# 07 — Architecture Decision Records (ADRs)

> **Purpose:** Learn to capture significant architecture decisions so that a future reader can understand the problem, reproduce the reasoning, challenge the evidence, see what was accepted, and know when the decision should be revisited.
>
> **Source and repository note:** The authoritative module roadmap explicitly says the repository does **not** mandate an ADR template. The structure taught below is the practical structure proposed by that roadmap. Treat it as a recommended learning format, not a repository-wide standard. The roadmap also describes `Projects/02-requirements-and-architecture-decision-pack.md`, `practice-questions.md`, module/project READMEs, and the topic files as empty in the referenced repository state. This lesson follows the written roadmap and does not claim those empty files contain further instructions.

**Case-study convention:** Northbridge Bank is fictional. All additional dates, IDs, people, performance results, costs, statuses, and decisions in completed examples are illustrative teaching assumptions. They are not facts about a real organisation, verified vendor claims, or legal/regulatory advice. Replace them with evidence from the actual project before using an ADR operationally.

## 1. Learning objectives

By the end of this topic, you should be able to:

1. Explain what an architecture decision record (ADR) is, why it exists, and which decisions are important enough to record.
2. Distinguish an architecture decision from a design proposal, meeting note, requirement, recommendation, and ADR.
3. Write an ADR with clear context, decision drivers, options, outcome, rationale, consequences, rejected alternatives, assumptions, open issues, dependencies, and evidence references.
4. Represent rejected alternatives fairly and explain why they were not selected.
5. Link each decision to business objectives, requirements, measurable targets, constraints, assumptions, risks, criteria, comparison matrices, and related ADRs.
6. Manage decision ownership, review, status, dates, version history, and supersession without silently rewriting the past.
7. Handle conditional decisions, unresolved evidence, uncertainty, and revisit conditions.
8. Maintain a coherent decision log and check that related decisions do not contradict one another without an explicit resolution.
9. Review an ADR for completeness, traceability, evidence quality, and honest consequences.
10. Produce an ADR set, decision log, review checklist and notes, and a superseding example as part of the integrated requirements-and-architecture decision pack.

**Outcome standard:** a reader who was not present at the original discussion can understand what was decided, why, which alternatives were rejected, what the organisation accepts as a consequence, what evidence supports the decision, and what would trigger a review.

## 2. Why the topic matters in real-world Data Architecture

Data architecture decisions affect more than a diagram. They can shape data ownership, integration patterns, customer identity, retention, quality, lineage, service targets, operational responsibilities, cost, security, and the ability to change platforms later. Without a durable record, teams can re-argue the same choice, forget why a constraint mattered, mistake an old assumption for a current fact, or continue following a decision after its conditions have changed.

An ADR makes a significant decision **durable, reviewable, traceable, and revisable**.

### 2.1 What is an ADR?

An **architecture decision record** is a concise, structured record of one significant architecture decision: the context that made it necessary, the drivers and evidence used to evaluate it, the alternatives considered, the outcome, the rationale, the consequences, and the conditions under which it should be reviewed.

An ADR is not intended to capture every conversation or every implementation detail. Its purpose is to preserve the reasoning that matters to future design, operations, governance, and change.

### 2.2 Decision versus related artefacts

| Artefact | What it is | What it is not |
|---|---|---|
| Business objective | The outcome the organisation wants | A technology selection |
| Requirement | A statement of needed behaviour or quality, ideally sourced and testable | Proof that a particular design is best |
| Constraint / assumption / risk record | A structured statement of a boundary, unverified belief, or uncertain exposure | A substitute for the decision rationale |
| Design proposal | A suggested solution for review | An approved decision merely because it was written |
| Meeting note | A record of discussion, actions, and participants | Necessarily a clear or approved architecture decision |
| Recommendation | Advice about the preferred option, supported by analysis | The final decision unless the authority accepts it |
| Architecture decision | The choice made by the accountable decision-maker | The full durable explanation of the choice |
| ADR | A record of the decision, its context, rationale, alternatives, consequences, links, and lifecycle | A detailed build specification or a replacement for source requirements |

A meeting may produce a decision, but the meeting minutes alone may not capture the alternatives, evidence, rejected options, or conditions for review. An ADR should make these explicit. If the decision is not yet approved, the ADR must show that status rather than imply finality.

### 2.3 Which decisions deserve an ADR?

The roadmap advises recording a decision when it is hard to reverse, affects multiple teams or quality attributes, resolves a real trade-off, or is likely to be questioned later. Examples in Data Architecture may include:

- The high-level approach to the authoritative customer record.
- The freshness path for card transactions to a fraud case tool.
- The retention and storage-tiering approach.
- A choice that creates substantial vendor or technology lock-in.
- A decision that changes ownership, responsibilities, or an important service target.
- A decision that accepts a material risk or depends on a critical external commitment.

Do not create an ADR for every trivial variable name, small implementation detail, or routine task. Excessive records create ceremony and make important decisions harder to find. Use proportionality: record the decisions whose rationale and consequences need to survive beyond the current conversation or team.

### 2.4 ADRs are a lifecycle, not a one-time writing task

A typical lifecycle is:

1. **Proposed:** the decision is being evaluated or submitted for review.
2. **Accepted:** the accountable decision-maker has approved the outcome.
3. **Deprecated:** the decision is no longer recommended or applicable, but is not necessarily replaced by a specific successor.
4. **Superseded:** a newer ADR replaces the decision; link to the successor.

The roadmap’s suggested status vocabulary is practical guidance, not an enforced repository standard. Adapt status labels if the project has an established convention, but keep them unambiguous and consistent in the decision log.

An accepted ADR should not be silently edited to change its meaning. If material context or the outcome changes, create a new ADR that references the earlier one and mark the earlier record as superseded. Correct obvious typographical errors without changing meaning according to the repository’s normal version-control practice; material changes to rationale or outcome require a visible history.

### 2.5 How the seven topics fit together

The ADR is downstream of the work in Topics 1–6, but the process is iterative:

- **Topic 1:** stakeholder discovery and business requirements explain the problem and affected parties.
- **Topic 2:** functional and non-functional requirements make needs testable.
- **Topic 3:** volume, velocity, variety, retention, and growth estimates provide workload evidence.
- **Topic 4:** latency, throughput, freshness, and availability targets define measurable service expectations.
- **Topic 5:** constraints, assumptions, dependencies, risks, and open questions establish boundaries and uncertainty.
- **Topic 6:** decision criteria, gates, alternatives, comparison matrices, and sensitivity analysis support the recommendation.
- **Topic 7 (this lesson):** ADRs preserve the decision, rationale, consequences, evidence links, and revisit conditions.

If an assumption fails or a requirement changes, update the source artefact first and follow the traceability links forward. Do not patch the ADR alone while leaving the requirements or analysis inconsistent.

## 3. Prerequisite concepts

The roadmap lists **Modules 1–6 in this module** and **2D.1 Topic 5 (decision records and exceptions)** as prerequisites.

Before writing an ADR, you should understand:

- **Business objectives (BO IDs):** the outcomes and needs the decision supports.
- **Requirements (REQ IDs):** sourced, classified requirements and acceptance criteria.
- **Targets (TGT IDs):** measurable latency, freshness, throughput, availability, or other service targets, with scope and measurement method.
- **Estimates (EST IDs):** data volumes, rates, retention, growth, and documented assumptions.
- **Constraints (CON IDs):** verified boundaries or mandatory conditions.
- **Assumptions (ASM IDs):** unverified beliefs, each with an owner and validation method.
- **Dependencies (DEP IDs):** external systems, teams, interfaces, approvals, or commitments needed for an option to work.
- **Risks (RSK IDs):** uncertain events or conditions with impact, response, owner, and trigger.
- **Decision criteria (DC IDs):** gates and scored criteria derived from requirements, constraints, risks, or principles.
- **Alternative comparison:** evidence, ratings, weights where used, cost analysis, sensitivity, and trade-offs.
- **Traceability:** links from a business objective through requirements and criteria to a recommendation and ADR, and back again.

### Prerequisite check

Before recording a major decision, verify that you can answer:

1. What business problem is being solved, and what is outside scope?
2. Which requirements and service targets drive the choice?
3. Which constraints are hard gates, and which statements remain assumptions?
4. Which options were considered, and what evidence supports the comparison?
5. What trade-offs and residual risks does the recommendation accept?
6. Who has authority to approve the decision and accept the relevant risk?
7. What evidence or change would cause the decision to be revisited?

If the evidence is missing, record the gap and owner. Do not manufacture a fact to make the ADR appear complete.

## 4. Beginner-level learning sequence

### 4.1 Learn the purpose: preserve one significant decision

An ADR should capture one coherent architecture decision in enough detail that a future reader can understand and challenge it.

**Good scope:** “Choose the high-level freshness path for card transactions into the fraud case tool.”

**Poor scope:** “Decide the bank’s data platform, customer model, cloud, retention, ingestion, and reporting architecture.”

The second statement bundles several decisions with different drivers, owners, and lifecycles. It is difficult to review and almost impossible to supersede cleanly. Split independent decisions into separate ADRs and cross-link them where dependencies exist.

A single ADR may reference related decisions, but it should have one clear decision outcome.

### 4.2 Know when to write an ADR

Create one when a decision is architecturally significant, difficult to reverse, has consequences across teams or quality attributes, resolves a genuine trade-off, creates lock-in, or is likely to be revisited. The Northbridge integrated project requires ADRs for at least its major decision boundaries:

1. The freshness path for card transactions to the fraud case tool.
2. The approach to the authoritative customer record.
3. The retention and storage-tiering approach.

These are project decision boundaries, not a claim that one specific technology must be selected. Detailed schema design, vendor product selection beyond option categories, implementation, migration plans, detailed cost negotiation, and decisions reserved for later modules are outside the stated project scope.

### 4.3 Use the roadmap’s practical ADR structure

The authoritative roadmap proposes the following structure for study. **It is recommended, not repository-mandated.** Keep it if it serves the project; if the repository later adopts a template, follow the actual approved convention.

1. **Title and ID:** a unique identifier and concise decision title.
2. **Status:** Proposed, Accepted, Deprecated, or Superseded by another ADR.
3. **Date:** the record date, and where useful, the decision/effective date.
4. **Decision owner / deciders:** who owns and approves the outcome.
5. **Related artefacts:** requirement, constraint, assumption, risk, criterion, evidence, and related ADR IDs.
6. **Context:** the problem, business situation, scope, and why a decision is needed.
7. **Decision drivers (criteria):** the outcomes and requirements that matter most.
8. **Considered options:** realistic alternatives and their material pros/cons.
9. **Decision outcome:** a direct statement of what is selected, rejected, or conditionally approved.
10. **Rationale:** why the outcome best fits the drivers and evidence.
11. **Consequences:** positive, negative, and accepted trade-offs.
12. **Rejected alternatives and reasons:** why other credible options were not selected.
13. **Assumptions and conditions for revisiting:** what is uncertain and what would trigger reconsideration.
14. **Open issues and dependencies:** unresolved work, owner, and due date.
15. **Evidence references:** links to the comparison matrix, requirement register, risk register, tests, estimates, and review notes.

The roadmap’s compact template groups some of these fields together. The list above expands them for teaching clarity without asserting a mandatory schema. Projects may combine sections when the meaning remains explicit.

### 4.4 Context versus rationale

These sections answer different questions.

- **Context:** What problem exists, what is the scope, and why must a decision be made?
- **Rationale:** Why does the selected option best satisfy the drivers compared with the alternatives?

Weak context: “We need a better data platform.”

Stronger illustrative context: “Northbridge’s fraud analysts receive card-transaction data hours after the source activity, while the fraud-case workflow needs a defined, measurable freshness target. The decision covers the high-level delivery path to the case tool, not the bank-wide warehouse or detailed product selection.”

Weak rationale: “Event streaming is modern and scalable.”

Stronger rationale: “In the illustrative comparison, the event-driven option is recommended only if the source event contract, security review, and representative freshness test pass. It is preferred because the evidence indicates it can meet the approved freshness gate and provides growth headroom. The choice accepts higher operating complexity and estimated whole-life cost than the micro-batch alternative.”

The stronger rationale refers to criteria, evidence, gates, and accepted costs. In a real ADR, link the actual records and measurements rather than relying on this illustrative statement.

### 4.5 Why record rejected alternatives?

Recording only the chosen option hides the decision process. Rejected alternatives show that the team considered credible options, reveal which criteria mattered, and help future reviewers avoid repeating old analysis.

A fair alternative entry includes:

- What the option is, at the same scope as the selected option.
- Its strongest credible benefit.
- Its material weakness or constraint.
- Evidence or uncertainty behind the assessment.
- Why it was not selected in this context.
- What change could make it viable later, if applicable.

Avoid “rejected because it is old,” “not best practice,” or “not scalable” unless these claims are translated into evidence or defined criteria. A rejected option is not universally bad; it may simply fit this decision less well.

### 4.6 Beginner exercise: convert an informal decision email into an ADR

**Exercise prompt (illustrative):**

> “We should move fraud data to streaming. The team says it is faster. Batch is too slow. Let’s use the event platform and move on. We can sort out support later.”

Convert this into an ADR draft without inventing missing evidence.

**Answer guidance:**

- Set status to **Proposed** until the accountable decision-maker approves it.
- Context: the fraud workflow needs a defined freshness outcome; the current batch path is reported to be too slow, but the actual target and measurement must be linked.
- Drivers: the approved freshness target, security/access requirements, peak throughput, supportability, cost, and delivery constraints—only after confirming their IDs and status.
- Options: retain/minimally improve batch, managed micro-batch, event-driven path, as relevant to the project.
- Outcome: no final production selection can be claimed from the email alone. A conditional proposal or an open decision is more honest.
- Rationale: “faster” is not evidence. Request representative measurements, the comparison matrix, and the operational assessment.
- Consequences: continuous operations, monitoring, retries/replay, skills, and cost must be assessed, not deferred without an owner.
- Open issues: target, source event contract, security review, support owner, cost estimate, and decision authority.
- Revisit conditions: target changes, source dependency fails, or test results fail the agreed gate.

**Ability to demonstrate:** write a complete, readable ADR for a simple decision without converting informal preference into false approval or invented fact.

## 5. Intermediate-level learning sequence

### 5.1 Write context that stands alone

A reader should understand the problem a year later without needing the original meeting or chat. Include:

- The business problem and affected consumers.
- The scope and explicit exclusions.
- Why a decision is needed now.
- The requirements and constraints that shape the solution space.
- Relevant known facts versus assumptions and unknowns.
- The decision owner and relevant stakeholders.

Avoid copying every detail from the requirements register. Summarise what matters and link to the source artefacts.

### 5.2 Link decision drivers to requirements and quality targets

Drivers should be expressed as criteria, not vague adjectives. For example:

- `REQ-014`: fraud-case tool must receive transaction data within the approved freshness target.
- `TGT-003`: p95 freshness measured from source commit to visibility in the case tool.
- `CON-004`: existing identity provider must be used.
- `ASM-006`: source event contract can be delivered by the planned date; validation still required.
- `RSK-009`: late source integration may delay delivery.
- `DC-002`: whole-life cost including support and people.

These IDs are **illustrative examples**, not existing repository records. In the project, use consistent IDs that exist in the source artefacts. If an ID is not yet assigned, label it provisional and resolve it before final review.

A driver should be traceable to a business objective, requirement, constraint, risk, or approved architecture principle. The ADR should not invent a new requirement merely to justify the selected design.

### 5.3 Record options honestly and at comparable scope

For each option, record its description, evidence, strengths, weaknesses, dependencies, and eligibility. Use the Topic 6 comparison matrix as the analytical source.

An ADR should not repeat every row of a large spreadsheet. It should summarise the key discriminators and link to the full matrix. The reader must be able to reproduce the conclusion from the linked evidence.

If an option failed a mandatory gate, state that clearly. Do not call it an eligible alternative or allow its low cost to compensate for failure. If a requirement was formally changed, link to the approved change and explain how that changed the decision.

### 5.4 State the outcome as a decision

Weak outcome: “The team discussed streaming, batch, and micro-batch. More work is needed.”

This records discussion, not an outcome.

Clear outcomes include:

- **Accepted:** “Select Option B for the defined scope.”
- **Proposed:** “Option B is recommended, pending approval by the named decision-maker.”
- **Conditional:** “Authorise a bounded pilot only after condition X is verified; production approval remains open.”
- **No decision:** “No option currently passes the mandatory gates; reopen requirements or alternatives.”

Do not use “Accepted” if the approval has not occurred. Record the authority and approval evidence according to the project’s governance.

### 5.5 Write rationale against evidence, not preference

A sound rationale should answer:

1. Which gates were passed?
2. Which criteria were most discriminating?
3. What evidence supports the ratings?
4. What did sensitivity analysis show?
5. Why did the runner-up lose?
6. What trade-offs are being accepted?
7. Which assumptions or dependencies remain open?

Replace vague claims:

| Weak rationale | Better rationale pattern |
|---|---|
| “This is industry standard.” | Cite the relevant approved standard or explain the requirement it satisfies. |
| “It is more scalable.” | Link to workload assumptions and representative capacity evidence. |
| “It is cheaper.” | Link to a comparable TCO model and its time horizon. |
| “It is more secure.” | Identify the applicable control requirement and the evidence/review result. |
| “The team prefers it.” | Record the preference as a criterion only if stakeholders agree it matters; assess skills and support consequences. |

### 5.6 Document consequences explicitly

Consequences are not just benefits. Record:

- **Positive:** the expected improvements and who benefits.
- **Negative:** additional costs, complexity, constraints, or capabilities not provided.
- **Accepted trade-offs:** what the decision-maker knowingly gives up.
- **Operational consequences:** monitoring, incident response, replay, recovery, ownership, staffing, and runbooks.
- **Dependencies and risks:** what can still fail and who owns the response.
- **Follow-up actions:** action, owner, due date, validation evidence, and status.
- **Revisit conditions:** a measurable change or event that would make the decision invalid or less appropriate.

Do not state speculative benefits as guaranteed outcomes. Use “expected,” “estimated,” or “to be validated” where appropriate.

### 5.7 Link evidence and keep the record reviewable

Use stable links or repository paths to source records. Common references include:

- Business objective and stakeholder records.
- Requirements and acceptance criteria.
- Workload estimates and calculations.
- Service-target specifications and timing budgets.
- Constraint, assumption, dependency, and risk registers.
- Decision criteria, gate results, comparison matrix, TCO, and sensitivity analysis.
- Test results, security review, approvals, and operational assessment.
- Related ADRs and the decision log.

A link should identify the exact artefact or section needed, not merely point to a large folder. If evidence is unavailable, mark it as missing and assign an owner; do not cite an uninspected file as support.

### 5.8 Manage status, ownership, and history

A useful ADR identifies:

- **Author/maintainer:** who prepared and updates the record.
- **Decision owner/deciders:** who has authority to approve the choice.
- **Reviewers:** who assessed relevant technical, business, security, risk, or operational aspects.
- **Status:** Proposed, Accepted, Deprecated, or Superseded (or the repository’s documented equivalent).
- **Dates:** created, decided/accepted, and last reviewed as useful.
- **Related records:** prior and successor ADRs.
- **Review trigger:** the event or date that prompts reassessment.

Do not confuse authorship with decision authority. The person who writes an ADR may not have authority to accept a risk or approve a target change.

### 5.9 Intermediate exercise: write three ADRs from Topic 6 comparisons

Write ADRs for the three major Northbridge decision boundaries:

1. Freshness path for card transactions to the fraud case tool.
2. Approach to the authoritative customer record.
3. Retention and storage-tiering approach.

Use the same practical structure but make each decision independent and traceable. Do not make product-level choices that the project scope excludes.

**Answer guidance:**

- Use the Topic 6 comparison matrix as the source for options and rationale.
- Link the business objectives, requirements, targets, constraints, assumptions, risks, and criteria.
- State which alternatives were rejected and why.
- For the customer-record decision, distinguish the business question of authoritative ownership from later detailed data modelling.
- For retention/tiering, use the approved retention requirement and estimates; do not invent legal retention periods. The illustrative scenario mentions seven-year transaction retention as an assumption, so validate it before treating it as a requirement.
- If mandatory evidence or approval remains open, keep the ADR Proposed and record the conditions, evidence required, owner, due date, pass/fail criteria, and fallback explicitly. Use a separate “Conditional” status only if the project formally adopts that status vocabulary.
- Cross-link the three ADRs where one decision depends on another, but do not bundle unrelated outcomes into a single record.

**Ability to demonstrate:** ADRs that stand alone, link to evidence, show real alternatives, and honestly describe consequences and uncertainty.

## 6. Advanced-level learning sequence

### 6.1 Record high-impact decisions and conditions for revisiting

For decisions with high cost, lock-in, safety/security implications, or significant operational consequences, include the evidence that supports the choice, the sensitivity result, the residual risk, and the conditions under which the decision should be revisited.

A revisit condition should be concrete enough to act on. Examples:

- A validated peak event-rate estimate exceeds the capacity envelope used in the comparison.
- A mandatory freshness target changes or the measured service target is missed.
- The source system cannot provide the agreed event contract by the dependency date.
- The vendor withdraws a capability or changes a commitment on which the decision depended.
- A high-impact assumption is invalidated.
- A material security, privacy, operational, or policy constraint changes.
- The operating team cannot meet the agreed support model.

These are examples, not claims that such events have occurred at Northbridge.

### 6.2 Conditional decisions when evidence is missing

A conditional decision is useful when a next step can safely proceed but final commitment depends on specific evidence. It must state:

1. What is authorised now.
2. What is **not** authorised yet.
3. The missing evidence or condition.
4. The owner responsible for obtaining it.
5. The due date or decision deadline.
6. The pass/fail criteria and who verifies them.
7. The fallback if the condition is not met.
8. The ADR status and review trigger.

Do not hide a gate failure inside “we will validate later.” If a hard gate is mandatory for production, production approval remains blocked until it passes.

### 6.3 Capture uncertainty and confidence honestly

An ADR should distinguish:

- **Known fact:** supported by a named source or observation.
- **Measured result:** a measurement with workload, scope, date, and method.
- **Estimate:** a calculation based on stated inputs and assumptions.
- **Assumption:** an unverified belief being used to proceed.
- **Unknown/open issue:** a question without sufficient evidence.
- **Decision judgement:** an evaluation made by the accountable stakeholders using criteria and evidence.

If confidence is useful, describe what it means and how it was assessed. A numerical confidence percentage without a defensible method can create false precision. Prefer clear statements such as “moderate confidence; depends on an untested source contract” and name the validation step.

### 6.4 Handle close alternatives and tie-breaks

When two options score closely, record:

- The score margin and limitations of the model.
- Which criteria actually distinguish the options.
- Where evidence is weak or uncertain.
- The tie-break criterion and why it was agreed.
- Whether a pilot or additional test is worth the cost and delay.
- What would make the runner-up preferable.

Do not claim a tiny score difference proves superiority. If the decision is effectively a tie, say so and explain the authorised tie-break or the evidence still needed.

### 6.5 Maintain a coherent ADR set

A set of individually well-written ADRs can still be incoherent if they contradict one another. Maintain a decision log or index containing at least the ADR ID, title, status, date, owner, related/superseding ADR, and repository link.

Review for:

- Duplicate decisions with different outcomes.
- Contradictory assumptions or targets.
- A newer ADR that conflicts with an accepted ADR but does not supersede it.
- A superseded ADR still referenced as current guidance.
- A conditional ADR whose condition was never resolved.
- A decision with no accountable owner or no traceable source requirement.
- A risk accepted in one ADR but treated as eliminated in another without evidence.

A new ADR should reference the old one and state whether it supersedes, amends through a new decision, or depends on it. Keep the old record available as historical context.

### 6.6 Revisit or supersede an ADR without erasing history

When a requirement, assumption, dependency, constraint, or evidence base changes:

1. Update the source artefact first.
2. Identify every linked criterion, matrix, risk, and ADR affected.
3. Reassess gates and alternatives.
4. Determine whether the current decision remains valid.
5. If the outcome changes, create a new ADR with a new ID and a link to the prior ADR.
6. Mark the old ADR **Superseded by ADR-…** (or the repository’s equivalent).
7. Record why the decision changed, what evidence changed, and when the new decision takes effect.
8. Update the decision log and affected implementation guidance.
9. Verify that links from objectives/requirements to the current ADR resolve correctly.

If the earlier decision remains valid after review, record the review outcome where the project’s process expects it; do not create a needless replacement just to show that a review occurred.

### 6.7 Review an ADR using a checklist

A peer reviewer should ask:

- Is the problem and scope clear without the original meeting?
- Is the decision status accurate and the decision owner named?
- Are the drivers linked to requirements, constraints, or principles?
- Are the options credible and fairly described?
- Are rejected alternatives and reasons recorded?
- Does the rationale refer to evidence and criteria rather than adjectives?
- Are positive and negative consequences both present?
- Are assumptions, unknowns, dependencies, and risks visible?
- Are conditions for revisiting specific and actionable?
- Are references stable and sufficient to reproduce the reasoning?
- Does the ADR conflict with another accepted decision?
- Is the status log and supersession chain consistent?
- Is the record proportionate to the significance of the decision?

Review notes should identify the defect, severity, evidence, owner, and corrective action. A checklist is not a substitute for technical judgement; it helps ensure important questions are not skipped.

### 6.8 Communicate decisions proportionately

To communicate an accepted decision:

- Summarise the outcome, business reason, accepted trade-offs, and actions.
- Notify affected teams and owners.
- Link the ADR from the relevant architecture documentation or repository index.
- Update the decision log.
- Explain whether the decision is final, conditional, deprecated, or superseded.
- Make unresolved questions and deadlines visible.

If a team asks to skip ADRs “to go faster,” respond proportionately. A trivial, reversible implementation choice may not warrant an ADR. A cross-team, high-cost, hard-to-reverse decision may create more delay later if its rationale is lost. The aim is to minimise future rework and confusion, not maximise paperwork.

### 6.9 Advanced exercise: review and supersede a flawed ADR

Review this intentionally flawed example:

> **Title:** Use streaming  
> **Status:** Accepted  
> **Context:** Streaming is modern.  
> **Decision:** Use the event platform because it is best practice.  
> **Alternatives:** Batch was rejected because it is old.  
> **Consequences:** Better performance.  
> **References:** None.

Identify defects, rewrite the record, and create a superseding ADR when a named assumption later fails.

**Answer guidance:**

Defects include vague context, no decision owner/date, unsupported status, no traceability, no measurable drivers, no credible alternatives, no evidence, adjective-based rationale, no negative consequences, no assumptions or dependencies, no open issues, and no revisit conditions.

The rewrite should use the actual Topic 6 evidence. If it is unavailable, leave the ADR Proposed, record the evidence gap and any conditions explicitly, and do not imply approval. If the source event contract later proves unavailable, update the dependency/assumption record, reassess gates and alternatives, then create a new ADR if the outcome changes. Mark the prior ADR superseded rather than silently rewriting its decision history.

**Ability to demonstrate:** a coherent ADR set with a working status log, review practice, and an explicit supersession chain.

## 7. Industry-application exercises

Use the fictional Northbridge Bank scenario from the module roadmap. The stated scenario has a core banking system, cards platform, CRM, loan origination system, nightly warehouse extracts, an existing data lake, inconsistent customer counts across teams, fraud analysts receiving card transactions hours after the fact, and a request for clearer lineage and customer-data accountability. The scenario’s people, figures, and initial constraints are illustrative assumptions, not verified facts or legal conclusions.

### Exercise 7.1 — Write ADRs for the major decisions

Create an ADR for each required decision boundary:

- Freshness path for card transactions to the fraud case tool.
- Approach to the authoritative customer record.
- Retention and storage-tiering approach.

For each ADR:

- State context, scope, exclusions, decision drivers, and accountable decision-maker.
- Link requirements, measurable targets, constraints, assumptions, dependencies, risks, criteria, and comparison evidence.
- Record at least three credible alternatives in the underlying decision pack, including a baseline where appropriate.
- State the outcome and whether the ADR is Proposed (with conditions explicitly recorded) or Accepted.
- Explain the rationale and rejected alternatives.
- Record positive/negative consequences and accepted trade-offs.
- Name unresolved issues, owners, due dates, and revisit conditions.
- Link related ADRs without combining unrelated decisions.

**Answer guidance:** Use option categories rather than detailed vendor selection or implementation design, consistent with the project scope. If the actual evidence does not establish a winner, do not invent one; produce a Proposed ADR that makes the missing evidence and any conditions explicit.

### Exercise 7.2 — Build the decision log index

Create a decision log with the following fields:

| ADR ID | Title | Status | Date | Decision owner | Related IDs | Supersedes / superseded by | Review trigger | Link |
|---|---|---|---|---|---|---|---|---|
| ADR-001 | Card transaction freshness path | Proposed (conditions recorded) / Accepted | YYYY-MM-DD | Named role | REQ/TGT/CON/ASM/RSK/DC IDs | Link if applicable | Measurable trigger | Repository path |
| ADR-002 | Authoritative customer record | Proposed (conditions recorded) / Accepted | YYYY-MM-DD | Named role | Related IDs | Link if applicable | Measurable trigger | Repository path |
| ADR-003 | Retention and storage tiering | Proposed (conditions recorded) / Accepted | YYYY-MM-DD | Named role | Related IDs | Link if applicable | Measurable trigger | Repository path |

These IDs and titles are illustrative. Use the actual project IDs and statuses. The log must agree with the ADRs; do not leave a superseded ADR marked current in the index.

### Exercise 7.3 — Review a colleague’s or your earlier ADR

Use the review checklist in Section 6.7. Record:

- Review date and reviewer.
- ADR ID/version reviewed.
- Finding and severity.
- Evidence or section where the defect occurs.
- Required correction.
- Owner and due date.
- Resolution status and re-review result.

**Answer guidance:** Review both completeness and truthfulness. A polished ADR can still be defective if it misstates an assumption as a fact, hides a gate failure, cites unavailable evidence, or omits a material negative consequence.

### Exercise 7.4 — Supersede an earlier ADR

Start with an accepted ADR whose decision depends on a named assumption—for example, the source system will provide a stable event contract by a specific date. In this illustrative exercise, the assumption is later invalidated.

Create a successor ADR that:

1. Links to the previous ADR.
2. Describes the new evidence and its source.
3. Rechecks the mandatory gates and alternatives.
4. States whether the prior decision is superseded, deprecated, or still valid.
5. Explains the new outcome and consequences.
6. Records any interim fallback and owners.
7. Updates the decision log and traceability links.

**Answer guidance:** Do not merely change the old status and erase its rationale. The successor should explain why the original decision no longer holds. If no outcome change is justified, document the review outcome without pretending a supersession occurred.

### Exercise 7.5 — Integrated requirements and architecture decision pack

The module roadmap defines a project called the **Requirements and Architecture Decision Pack**. It is an integrated architecture analysis and decision-documentation project; it does **not** implement a data platform.

The roadmap’s intended project workflow connects:

1. Problem, stakeholders, business requirements.
2. Requirements register and acceptance criteria.
3. Workload estimates.
4. Service-target specification.
5. Constraint, assumption, dependency, and risk register.
6. Criteria and prioritisation.
7. Alternatives and trade-off analysis.
8. ADRs and decision log.
9. Traceability matrix.
10. Cross-document review, sponsor summary, and challenge round.

For the ADR part, ensure every major decision has rejected alternatives, consequences, revisit conditions, and links to the underlying analysis. Use consistent IDs across the artefacts and ensure the recommendation agrees with the comparison matrix and sensitivity results.

**Source limitation:** The roadmap identifies `Projects/02-requirements-and-architecture-decision-pack.md` and `practice-questions.md` as empty in the referenced repository state, while defining their intended role and required outputs. This lesson therefore teaches the prescribed workflow and exercises but does not claim to reproduce unprovided project-file instructions or unseen practice questions.

## 8. Practical scenarios and case-based reasoning

### Scenario 8.1 — A decision was made verbally in a meeting

**Situation:** A meeting ended with “we’ll use the event-driven option,” but no decision record exists. The meeting notes do not capture the criteria or evidence.

**What should you do?**

1. Capture only what the available notes and participants can substantiate.
2. Keep the ADR Proposed and record “decision confirmation required” as an open issue if approval and rationale are unclear.
3. Ask the decision owner to confirm the outcome and decision date.
4. Reconstruct the alternatives and rationale from the actual comparison matrix, requirements, and reviewers—not from memory alone.
5. Record gaps as open issues and assign owners.
6. Do not invent a reason, claim approval, or retroactively imply evidence existed.

**Acceptable result:** a transparent record that distinguishes confirmed facts from reconstructed context and unresolved questions. If the decision owner confirms the decision, update status and approval evidence according to the project process.

### Scenario 8.2 — An accepted ADR depends on a vendor capability that is withdrawn

**Situation:** A vendor withdraws a capability that the accepted decision relied on.

**Reasoning:**

- Record the change in the dependency/assumption/risk source artefact and cite the vendor communication or other evidence.
- Identify the affected requirements, criteria, alternatives, and related ADRs.
- Recheck feasibility gates and rerun the comparison where needed.
- If the decision changes, create a successor ADR and mark the previous ADR superseded.
- Record the interim mitigation, owner, due date, and operational exposure.
- Update the decision log and notify affected teams.

Do not silently edit the old ADR to make it appear the withdrawn capability was never part of the rationale. If the vendor statement is not verified, treat it as an open issue until confirmed.

### Scenario 8.3 — A team asks to skip ADRs to go faster

**Situation:** Engineers argue that writing ADRs slows delivery.

**Reasoning:** Use proportionality. Do not require a lengthy record for every small, reversible choice. For a significant decision affecting multiple teams, service targets, cost, security, or lock-in, a concise ADR can prevent repeated debate and costly rework. Explain the minimum information needed to preserve context, evidence, alternatives, consequences, ownership, and revisit conditions.

**Acceptable result:** a risk-based decision about the level of documentation, not an absolute rule to record everything or nothing.

### Scenario 8.4 — The preferred option is conditional

**Situation:** The comparison favours an option, but a required source interface or security review is unresolved.

**Reasoning:** Record the preferred option as conditional or proposed. State what work is authorised, what remains blocked, the condition and evidence required, the owner/date, and the fallback. If the unresolved item is a hard gate, do not record production approval.

### Scenario 8.5 — A reviewer says the rationale is “not objective”

**Situation:** A reviewer challenges the decision because the weighted model contains subjective ratings.

**Reasoning:** Acknowledge that weights and qualitative ratings involve judgement. Show the criterion definitions, evidence, rating anchors, stakeholder agreement on priorities, and sensitivity results. Explain the model’s limits. If the recommendation is fragile, gather more evidence or state the uncertainty. Do not claim that a score proves the answer is objectively correct.

### Scenario 8.6 — A new requirement conflicts with an accepted ADR

**Situation:** A stakeholder introduces a new mandatory freshness target after an ADR was accepted.

**Reasoning:** Update the requirement and target source records first, obtain the proper approval for the change, then trace the change through constraints, risks, criteria, gates, and alternatives. Review the ADR. If the old decision no longer satisfies the new requirement, create a successor ADR. Preserve the old record as history and explain the changed driver.

## 9. Expected outputs and deliverables

The Topic 7 roadmap prescribes these outputs:

- An **ADR set with a decision log**.
- A **review checklist and review notes**.
- A **superseding example**.
- Answers to the **Topic 7 practice questions**.

The integrated project also requires links between ADRs and the requirements, constraints, assumptions, risks, criteria, comparison matrix, sensitivity analysis, and business objectives.

### 9.1 Blank reusable ADR template

The following is the practical structure proposed by the roadmap, expanded slightly for teaching and review. It is not a repository-mandated template.

```markdown
# ADR-NNN: <short, decision-focused title>

- Status: Proposed | Accepted | Deprecated | Superseded by ADR-MMM
- Created: YYYY-MM-DD
- Decision date / effective date: YYYY-MM-DD or TBD
- Author / maintainer:
- Decision owner / deciders:
- Reviewers:
- Related: BO-…, REQ-…, TGT-…, EST-…, CON-…, ASM-…, DEP-…, RSK-…, DC-…, ADR-…
- Evidence: <links to registers, comparison matrix, tests, approvals>

## Context
<Problem, business situation, scope, exclusions, why a decision is needed.>

## Decision drivers (criteria)
<List the criteria and source IDs; distinguish mandatory gates from preferences.>

## Considered options
<Option A: description, strengths, weaknesses, dependencies, evidence.>
<Option B: description, strengths, weaknesses, dependencies, evidence.>
<Option C: description, strengths, weaknesses, dependencies, evidence.>

## Decision outcome
<State exactly what is selected, rejected, or conditionally authorised.>

## Rationale
<Explain why the outcome fits the drivers, evidence, gate results and sensitivity.>

## Consequences (positive, negative, accepted trade-offs)
<Expected benefits, costs, operational effects, limitations and residual risks.>

## Rejected alternatives and reasons
<Explain fairly why each credible alternative was not selected in this context.>

## Assumptions and conditions for revisiting
<Assumption IDs, confidence/evidence gaps, triggers, thresholds, review date.>

## Open issues and dependencies
<Issue/dependency, owner, due date, required evidence, fallback and status.>

## Approval and review history
<Who approved/reviewed, when, key comments and resolutions.>

## Supersession
<If applicable, prior ADR, successor ADR, reason and effective date.>
```

### 9.2 Completed illustrative ADR

The example below demonstrates the structure and internal logic. It is a **teaching example**, not a factual Northbridge decision. The scenario provides that fraud analysts receive card transactions hours after the fact, but it does not provide a validated freshness target, measured performance, vendor commitment, approved comparison matrix, or actual decision authority. Those missing details are labelled as assumptions or open items below.

# ADR-EX-001: Select a freshness-path approach for card transactions to the fraud case tool

- **Status:** Proposed — illustrative; not an approved Northbridge decision
- **Created:** 2026-10-20 (illustrative example date)
- **Decision date / effective date:** Pending accountable decision-maker confirmation
- **Author / maintainer:** Data architecture lead (illustrative role)
- **Decision owner / deciders:** Fraud product sponsor with platform and control-function review (illustrative governance assumption; confirm actual authority)
- **Reviewers:** Fraud operations, source-system owner, platform operations, security, compliance, and data architecture (illustrative roles)
- **Related:** `BO-EX-01`, `REQ-EX-01`, `TGT-EX-01`, `CON-EX-01`, `ASM-EX-01`, `DEP-EX-01`, `RSK-EX-01`, `DC-EX-01` (all provisional example IDs, not existing repository records)
- **Evidence:** Topic 6 comparison matrix and sensitivity analysis to be attached/linked; representative test and security review not yet available

## Context

The fictional Northbridge Bank scenario describes fraud analysts receiving card-transaction data hours after the underlying activity. The business problem is delayed fraud signals. This ADR considers only the **high-level freshness path from the card platform to the fraud case tool**. It does not select a bank-wide data platform, a vendor product, a detailed schema, or an implementation/migration plan.

The scenario says the card platform currently emits batch files every 15 minutes (an illustrative scenario assumption). It does not state a validated end-to-end freshness target or provide measured latency. Therefore, the final target and the option’s feasibility must be confirmed using the actual requirements and service-target artefacts before an Accepted production decision.

## Decision drivers (criteria)

| ID | Driver | Classification | Evidence / current state |
|---|---|---|---|
| `REQ-EX-01` | Deliver transaction data to the fraud case tool within the approved business freshness target | Hard gate only if the target is formally approved as mandatory | Target value and acceptance method are open; link to actual requirement and target before approval |
| `CON-EX-01` | Satisfy applicable security, access, audit, and data-handling constraints | Hard gate where confirmed mandatory by the responsible control owners | Actual control requirements and review evidence must be linked; no specific legal requirement is asserted here |
| `DC-EX-01` | Compare whole-life cost, operational support burden, peak throughput/headroom, delivery time, and reversibility | Scored preferences after hard gates, subject to approved priorities | Use the Topic 6 criteria register, matrix, TCO model, and sensitivity analysis; these are not supplied as verified results in this example |

## Considered options

### Option A — Retain or minimally improve the current batch path

- **Description:** Keep the current file-based approach and improve monitoring, scheduling, retry behaviour, and operational visibility where useful.
- **Potential strengths:** Lowest change scope; familiar operating model; may have lower initial cost.
- **Potential weaknesses:** May not meet a stricter end-to-end freshness target; batch windows and source constraints may limit improvement.
- **Evidence status:** Current scenario describes batch files every 15 minutes and fraud data arriving hours after the fact. No measured end-to-end timing or redesigned-path test is available here.
- **Disposition:** Do not mark feasible until measured against the approved target. If it fails a mandatory freshness gate, it is ineligible unless redesigned or the authorised owner formally changes the target.

### Option B — Managed micro-batch / short-interval ingestion

- **Description:** Retrieve or process data at short intervals using an appropriately managed ingestion path, subject to source capabilities and service limits.
- **Potential strengths:** May improve freshness while retaining some batch-style simplicity; may be easier to operate than a fully continuous path depending on the platform.
- **Potential weaknesses:** Freshness is bounded by the interval, processing time, source availability, and retry behaviour; frequent access may burden the source system.
- **Evidence status:** Illustrative alternative only. No verified source API/file capability, performance test, or cost estimate is provided.
- **Disposition:** Feasibility and cost remain open until tested and compared under the same workload and measurement boundary.

### Option C — Event-driven / continuous delivery

- **Description:** Publish card-transaction events to a durable event interface and process them continuously into the fraud case tool.
- **Potential strengths:** Could support lower delay and greater headroom if the source can publish events and the processing path is engineered appropriately.
- **Potential weaknesses:** Requires event-contract ownership, monitoring, retry/replay and idempotency handling, continuous operational support, and potentially higher cost/complexity.
- **Evidence status:** Illustrative alternative only. Source event publication, event-contract delivery, security review, measured freshness, and operational readiness are not verified.
- **Disposition:** Candidate for evaluation, not proven feasible and not approved for production.

## Decision outcome

**No final production architecture is selected by this example.** The proposed next step is to compare the three options against the approved freshness and control gates, then select only among options that pass every mandatory gate. A bounded proof of concept for the strongest candidate may be authorised by the actual decision owner if its scope, success criteria, time limit, and stop/go authority are approved.

Production approval remains open until:

1. The freshness target and measurement boundary are confirmed in the requirement/service-target records.
2. Security and access-control requirements are verified with the responsible reviewers.
3. Source/interface feasibility and required dependency commitments are confirmed.
4. The comparison matrix and sensitivity analysis are completed with evidence.
5. The authorised decision-maker approves the result and accepts documented residual risk.

## Rationale

The available scenario establishes a business problem—fraud signals arrive hours after activity—but does not establish that any one ingestion pattern meets the required target. Choosing event-driven delivery now would overstate the evidence. The defensible action is to evaluate real alternatives against the approved target and controls, using the Topic 6 gate-first method.

If event-driven delivery passes the gates and the evidence shows that its freshness benefit is worth its whole-life cost and operating burden, it may be recommended. If managed micro-batch meets the mandatory target with materially lower complexity and cost, it may be preferable. If neither passes, revisit the scope, source dependency, or approved target with the authorised stakeholders; do not select a failing option merely because it has the best score.

## Consequences (positive, negative, accepted trade-offs)

- **Positive:** preserves a traceable decision process and prevents an unsupported production selection; creates explicit evidence requirements for the next review.
- **Negative:** the production choice is delayed until target, dependency, and feasibility evidence is available.
- **Accepted trade-off:** the project accepts short-term decision work and a possible delay rather than claiming certainty unsupported by evidence.
- **Operational consequence:** the selected path must have a defined owner, monitoring, failure/recovery behaviour, and support model before production approval.
- **Residual risk:** source/interface constraints or the approved target may make all current alternatives infeasible. The risk remains open until feasibility evidence is available.

## Rejected alternatives and reasons

No option is declared finally rejected by this Proposed ADR. The options remain under evaluation until the gate and comparison evidence exists.

- **Option A:** may be rejected if it cannot meet a mandatory freshness target and no viable redesign exists. The current evidence is insufficient to assert that conclusion definitively.
- **Option B:** may be rejected if source limitations, measured delay, or operating costs make it infeasible or inferior under the agreed criteria.
- **Option C:** may be rejected if the source event contract, security/control gates, operational readiness, or whole-life cost is unacceptable. Its potential freshness advantage alone does not justify selection.

This section deliberately avoids a false claim that alternatives have already failed tests that have not been run.

## Assumptions and conditions for revisiting

- `ASM-EX-01` — **Assumption:** the card platform can support at least one candidate path beyond the current batch interface. **Confidence:** unverified. **Validation:** source-system owner confirms capabilities and provides interface evidence by a date agreed in the project. If false, remove or redesign affected alternatives.
- **Target condition:** if the approved freshness target changes, update the requirement and target records, rerun gate checks, and reassess the options.
- **Performance condition:** if representative end-to-end tests fail the target, the option is not eligible unless redesigned and retested.
- **Dependency condition:** if a required event contract or vendor/source commitment is not delivered by its agreed date, reassess the dependency and fallback.
- **Cost condition:** if the TCO range changes enough to alter the ranking or exceed the approved budget constraint, rerun the comparison and seek the required approval.

## Open issues and dependencies

| Item | Owner (role, illustrative) | Due date | Evidence needed | Status |
|---|---|---|---|---|
| Confirm approved freshness target and scope | Fraud product owner / requirements owner | To be agreed | Approved requirement and service-target record | Open |
| Confirm source interfaces and event-contract feasibility | Card platform owner | To be agreed | Interface description and dated commitment | Open |
| Verify applicable security/access controls | Security reviewer | To be agreed | Control review and recorded findings | Open |
| Complete comparable performance and failure tests | Data/platform engineering lead | To be agreed | Test workload, measurements, failures/recovery results | Open |
| Complete TCO, criteria matrix, and sensitivity analysis | Architecture lead with Finance/Operations | To be agreed | Linked Topic 6 artefacts | Open |
| Confirm decision authority and approval | Programme sponsor / governance owner | To be agreed | Recorded approval | Open |

## Approval and review history

- 2026-10-20 (illustrative): Drafted as a learning example; no real Northbridge approval is implied.
- Next review: after the required evidence is assembled or when any stated dependency/target condition changes.

## Supersession

None. If a final decision is made, update this Proposed record according to the project’s version-control process or create the approved ADR with a clear status/history. If an accepted decision later changes, create a successor ADR and mark the prior ADR Superseded by the new ID.

### Why this completed example is useful

It is complete in structure without pretending the source scenario contains evidence it does not contain. A real accepted ADR would replace provisional IDs, open conditions, and missing evidence with validated project artefacts and an explicit approval record.

### 9.3 Decision-review checklist

Use this checklist before accepting an ADR:

- [ ] The decision is significant enough to record and has one coherent outcome.
- [ ] Context and scope stand alone; exclusions are clear.
- [ ] Status, date, author/maintainer, decision owner, and reviewers are identified.
- [ ] Decision drivers trace to objectives, requirements, constraints, risks, or approved principles.
- [ ] Mandatory gates are distinguished from scored preferences.
- [ ] Considered options are credible, comparable, and fairly represented.
- [ ] Rejected alternatives and reasons are documented.
- [ ] The outcome is explicit and status accurately reflects approval.
- [ ] Rationale cites criteria and evidence rather than vague adjectives.
- [ ] Positive and negative consequences, accepted trade-offs, and residual risks are visible.
- [ ] Assumptions, unknowns, dependencies, and conditional approval requirements are recorded.
- [ ] Open issues have owners, due dates, required evidence, and status.
- [ ] Links to the requirements, constraints, risk register, comparison matrix, and sensitivity analysis work.
- [ ] Revisit conditions are actionable.
- [ ] Related ADRs are consistent; supersession is explicit.
- [ ] The decision log agrees with the ADR.
- [ ] A reader can reproduce the reasoning without relying on the author’s memory.

### 9.4 Review notes template

| Finding ID | ADR ID/version | Finding and severity | Evidence/location | Required correction | Owner | Due date | Status / re-review |
|---|---|---|---|---|---|---|---|
| REV-001 | ADR-… | Missing rejected alternative — material | Options section | Add fair alternative and evidence-based reason | Reviewer/author | YYYY-MM-DD | Open |
| REV-002 | ADR-… | Unlinked requirement — material | Drivers section | Add source ID and traceability link | Author | YYYY-MM-DD | Open |

These are illustrative rows. Use the project’s actual IDs and severity definitions if they exist.

### 9.5 Supersession example

**Earlier record:** `ADR-EX-010 — Use event-driven delivery` (illustrative) was Accepted based on the assumption that the card platform would provide a stable event contract by an agreed date.

**New evidence:** the source owner confirms that the required event contract will not be available within the approved delivery window. This statement is hypothetical; in a real project, link the actual confirmation.

**Correct action:**

1. Update the dependency and assumption records with the evidence.
2. Recheck the freshness gate, options, delivery constraints, and sensitivity analysis.
3. Create `ADR-EX-011 — Reassess card transaction freshness path` with the new context, options, outcome, rationale, and consequences.
4. If the new decision replaces the old one, set the old ADR status to “Superseded by ADR-EX-011” and link back from the successor.
5. Record why the prior choice no longer applies, what interim path is approved, who owns follow-up actions, and the next review trigger.
6. Update the decision log and notify affected teams.

The successor does not erase the old decision; it explains how new evidence changed the outcome.

## 10. Common mistakes and misconceptions

1. **Writing an ADR after implementation just to justify a favourite.** Record the real decision process and evidence. If documenting a historical decision, state that it is retrospective and identify gaps honestly.
2. **Recording only the selected option.** Include credible alternatives and reasons for rejection.
3. **Using adjectives as rationale.** Replace “modern,” “best practice,” “secure,” or “scalable” with evidence, criteria, and defined targets.
4. **Confusing context with rationale.** Context explains the problem; rationale explains why the chosen outcome fits the drivers better than alternatives.
5. **Combining many unrelated decisions in one ADR.** Keep one coherent outcome per record and link related decisions.
6. **Treating a proposal as an accepted decision.** Use status and approval evidence accurately.
7. **Hiding negative consequences.** Record cost, complexity, limitations, risks, and accepted sacrifices.
8. **Turning assumptions into facts.** Label uncertainty and link the validation action.
9. **Failing to link source artefacts.** Unlinked ADRs cannot be traced to objectives, requirements, constraints, or risks.
10. **Editing an accepted ADR to hide history.** Create a successor and preserve the prior record.
11. **Ignoring conditional decisions.** Name the missing evidence, owner, due date, gate, and fallback.
12. **Leaving the decision log stale.** The index and ADR status must agree.
13. **Treating an ADR as a detailed implementation design.** Keep the decision at the correct scope; implementation belongs in the relevant design/engineering artefacts.
14. **Inventing facts to fill gaps.** Mark unknowns as open questions; do not claim an empty or unavailable file supports the decision.
15. **Over-documenting trivial choices.** Use ADRs proportionately for significant decisions.
16. **Ignoring contradictions between ADRs.** Check the set as a whole and supersede explicitly when necessary.
17. **Recording no revisit conditions.** Important decisions should identify what evidence or change would make them stale.
18. **Claiming that a recommended template is a repository mandate.** The roadmap states that no template is mandated; its format is a practical proposal.

## 11. Mastery criteria

You have mastered Topic 7 when you can independently:

- Write standalone ADRs that explain context, drivers, options, outcome, rationale, consequences, rejected alternatives, assumptions, open issues, and evidence references.
- Explain why the decision deserves an ADR and keep its scope to one coherent outcome.
- Link each ADR to requirement, constraint, assumption, or risk IDs, and where relevant to objectives, targets, criteria, matrices, and related ADRs.
- Represent alternatives fairly and explain why they were not selected.
- Distinguish facts, measured results, estimates, assumptions, unknowns, and judgement.
- Record a decision as Proposed, Accepted, Deprecated, or Superseded without misrepresenting its approval status; when a proposal is conditional, record its conditions explicitly rather than silently adding a repository status.
- Identify the decision owner separately from the author and reviewers.
- State positive and negative consequences, accepted trade-offs, residual risks, and conditions for revisiting.
- Maintain a decision log whose status and supersession links agree with the ADR set.
- Review a flawed ADR and identify material defects with evidence and corrective actions.
- Supersede a prior decision without erasing its history.
- Communicate the decision to affected teams and a non-specialist sponsor without hiding material uncertainty.
- Support the integrated requirements-and-architecture decision pack and defend conclusions against reviewer challenges without unsupported claims.

### Self-review questions

1. What distinguishes an ADR from a requirement, proposal, decision, and meeting note?
2. Which decisions in the Northbridge pack deserve an ADR, and why?
3. Can a future reader understand the context without asking the original author?
4. Which source records support the drivers and rationale?
5. What alternatives were rejected, and what evidence supports those reasons?
6. Which assumptions or dependencies could invalidate the decision?
7. What consequences and risks are explicitly accepted?
8. Who owns the decision, and who is authorised to accept residual risk?
9. What would trigger a review or supersession?
10. Does the decision log agree with the ADR status and supersession chain?
11. Can you trace from a business objective to a current ADR and back?
12. Which part of your weakest ADR would you improve first, and what evidence is needed?

## 12. Completion gate

Do not mark Topic 7 complete until all checks pass:

- [ ] The ADR set has been reviewed; no ADR lacks rejected alternatives or consequences.
- [ ] Every ADR links to requirement, constraint, assumption, or risk IDs; relevant objective, target, criteria, and evidence links are present where applicable.
- [ ] Each ADR has a clear context, decision drivers, considered options, outcome, rationale, consequences, assumptions/revisit conditions, and open issues/dependencies.
- [ ] Decision status, owner, dates, approval evidence, and review history are accurate.
- [ ] The decision log shows status and supersession consistently.
- [ ] A superseding example has been completed without silently erasing the prior decision.
- [ ] A review checklist and review notes are completed, and material defects are corrected.
- [ ] The integrated project’s major decisions each have an ADR and a traceable evidence chain.
- [ ] A random trace from three ADRs back to business objectives, and from three business objectives forward to ADRs, succeeds as required by the integrated project gate.
- [ ] The recommendation, comparison matrix, sensitivity results, and ADR rationale do not contradict one another.
- [ ] Topic 7 practice questions have been answered and corrected using the actual source questions. The referenced roadmap says `practice-questions.md` is empty in the repository state it describes; obtain/populate the actual questions before marking that particular check complete.
- [ ] An independent reviewer agrees that the evidence supports the conclusions and that open issues are not presented as settled facts.

**Integrated project reminder:** Topic 7 completion is necessary but not sufficient for the whole module. The module’s project gate also requires version-dated D1–D13 artefacts with consistent IDs, measurable requirements, recomputable estimates, consistent targets, classified risks/assumptions/dependencies, at least three feasible alternatives per major decision, sensitivity analysis for the two least certain inputs, traceability, and a final recommendation that a non-specialist can understand. The module completion gate also requires all seven topic gates, corrected practice questions, the integrated project gate, and a review/challenge round.

**Completion standard:** a reviewer can follow the chain from business objective to requirement, constraint, criterion, evidence, decision, ADR, consequences, and review trigger. The record tells the truth about what was decided, why it was decided, what was rejected, what remains uncertain, and how the organisation will preserve and revisit the decision.
