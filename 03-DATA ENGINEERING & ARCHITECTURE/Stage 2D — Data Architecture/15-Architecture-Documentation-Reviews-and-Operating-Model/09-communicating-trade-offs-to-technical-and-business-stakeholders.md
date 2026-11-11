# Communicating Trade-offs to Technical and Business Stakeholders

> **Module:** Stage 2D — Data Architecture / 15 — Architecture Documentation, Reviews, and Operating Model  
> **Topic:** 09 of 09  
> **Learning progression:** Beginner → Intermediate → Advanced  
> **Scenario status:** Northbridge Bank is fictional. Every team, system, requirement, cost, metric, timeline, risk rating, forecast, decision, and outcome attributed to it is synthetic and exists only for learning. None is production evidence or a claim about a real institution.

## How to use this lesson

Read the beginner, intermediate, and advanced sections in order. Attempt the exercises before consulting their model answers. The goal is not to make an architecture sound attractive; it is to make a decision understandable and defensible. Tailor the emphasis, vocabulary, level of detail, and requested action to the audience, but **do not change the underlying facts, uncertainty, or risk**.

This lesson follows Topic 09 of the module roadmap. The roadmap's intended output is two briefs for one decision—one technical and one business-facing—with the same facts and different emphasis. It also calls for audience and concern analysis, an options/trade-off comparison, a Q&A set, and a decision-log update. Specific methods and Northbridge examples below are recommended learning content, not evidence that a process or organizational model is formally adopted by the repository.

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Identify stakeholders, their concerns, their decision authority, and the action each needs to take.
2. Explain why architecture communication matters to funding, governance, implementation, security, and operations.
3. Present a recommendation with context, requirements, alternatives, evidence, consequences, risks, uncertainty, and an explicit ask.
4. Translate technical mechanisms and measures into business implications without changing their meaning.
5. Compare options across cost, performance, scalability, reliability, security, privacy, complexity, maintainability, and time to delivery.
6. Distinguish verified facts, observed evidence, estimates, assumptions, hypotheses, opinions, and unresolved questions.
7. Communicate the same decision to technical and business audiences using one controlled fact base.
8. Explain architecture diagrams, ADRs, review findings, risk registers, and migration roadmaps at the appropriate level of detail.
9. Respond to objections and difficult questions using evidence, explicit uncertainty, and a clear path to resolve gaps.
10. Record the decision, conditions, dissent, follow-up actions, and communication outcomes in the decision log.
11. Defend a coherent architecture review package integrating Topics 01–09.

## 2. Prerequisites and relationship to earlier topics

The module roadmap identifies Topic 09 dependencies as Topics 04, 05, and 08, plus prerequisite P10. The wider package also reuses the audience/viewpoint work from Topic 03 and the ownership and pattern work from Topics 06–07.

| Prior topic or input | What it contributes | How Topic 09 uses it |
|---|---|---|
| [Topic 03 — Architecture description and viewpoints](03-architecture-description-and-viewpoints.md) | Stakeholders, concerns, views, scope, known gaps | Choose the right message and diagram for the audience; avoid repeating the whole architecture when one view answers the concern. |
| [Topic 04 — ADRs and decision log](04-architecture-decision-records-and-decision-log.md) | Context, options, criteria, decision, rationale, consequences, status | Ensure the brief explains why the choice was made and links to the durable decision record. |
| [Topic 05 — Design reviews, threat models, and risk registers](05-design-reviews-threat-models-and-risk-registers.md) | Evidence-based findings, threats, risk owners, treatments, residual risks | Communicate risk honestly, distinguish mitigated from accepted risk, and state who owns follow-up. |
| [Topic 06 — Reference architectures, standards, and reusable patterns](06-reference-architectures-standards-and-reusable-patterns.md) | Reuse rationale, applicability, adaptations, deviations, exceptions | Explain why a pattern fits this context and which adaptations or exceptions remain. |
| [Topic 07 — Team boundaries and operating model](07-team-boundaries-ownership-and-platform-operating-model.md) | Accountable owners, interfaces, support duties, decision rights | Make implementation, operation, escalation, and acceptance responsibilities explicit. |
| [Topic 08 — Migration roadmaps and modernization](08-migration-roadmaps-and-architecture-modernization.md) | Current/target state, phases, dependencies, checkpoints, cutover, rollback | Explain timing, transition risk, what is reversible, what must be proven, and what may delay delivery. |
| P10 — Evidence-based cost/performance reasoning | Measurement and estimation discipline | `Roadmap_ptree.md` describes P10 as evidence-based cost/performance reasoning and points to the cost-modeling and measured-optimization lessons. Label figures, units, ranges, measurement windows, assumptions, and evidence limits; do not invent a more formal prerequisite definition than the source provides. |

**Dependency rule:** a stakeholder brief is a presentation layer over the architecture package, not a replacement for it. If a diagram, ADR, review finding, risk register, ownership map, or roadmap is inconsistent, fix the source artefact or explicitly flag the discrepancy before publishing the brief.

## 3. Beginner level — foundations

### 3.1 Why architecture communication matters

Architecture work changes decisions about money, risk, delivery sequencing, customer experience, and operational responsibility. A technically sound design can still fail if a decision-maker misunderstands its cost, a security reviewer cannot find the threat rationale, an operations team discovers an unplanned support duty, or a business sponsor believes an estimate is a commitment.

Communication has four jobs:

1. **Orient:** establish the problem, scope, and decision to be made.
2. **Explain:** connect requirements and constraints to the alternatives and their consequences.
3. **Enable choice:** show the trade-offs, uncertainty, and decision rights.
4. **Preserve accountability:** record what was decided, by whom, under which conditions, and what must happen next.

A useful communication artifact is successful when its intended audience can accurately restate the decision, its principal trade-off, the remaining risk, and the requested action. Agreement is not the only measure of success: a stakeholder may disagree for a valid reason, and that disagreement should become visible rather than being concealed.

### 3.2 Core vocabulary

| Term | Meaning | Practical test |
|---|---|---|
| Audience | People who will read, hear, challenge, approve, fund, build, secure, or operate the design | Who is this for, and what do they need to do? |
| Stakeholder concern | A question or outcome important to a stakeholder | Can it be expressed as a question, requirement, or decision criterion? |
| Recommendation | The option proposed, with reasons and conditions | What do you recommend, and why is it better under these constraints? |
| Trade-off | A benefit gained at the expense of another property or constraint | What gets better, what gets worse, and who bears the consequence? |
| Evidence | Information supporting a claim, such as an observed measurement, test result, documented requirement, or traceable review finding | Can another person inspect the source and reproduce the interpretation? |
| Estimate | A calculated or judged value based on stated inputs and method | What range, assumptions, and confidence limits apply? |
| Assumption | A proposition temporarily treated as true because it has not been verified | What decision changes if this assumption is false? |
| Uncertainty | A known limitation in what can be predicted or established | What is unknown, how material is it, and how will it be reduced or managed? |
| Decision ask | The action required from the audience, with owner and deadline | Approve, fund, choose, accept risk, provide evidence, or defer? |
| Residual risk | Risk remaining after planned or existing controls | Who owns it, who may accept it, and until when? |
| Framing | Selecting the most relevant explanation and order for a particular audience | Does the emphasis help the audience decide without altering facts? |

### 3.3 A repeatable architecture-communication framework

Use this sequence for a short recommendation, decision memo, review meeting, or presentation:

1. **Decision first:** state the decision required and the deadline, if known.
2. **Context:** describe the problem, scope, business outcome, and relevant constraints.
3. **Recommendation:** name the preferred option and any conditions attached to it.
4. **Why:** connect requirements and decision criteria to evidence.
5. **Alternatives:** compare two or three genuine options, not a preferred option against straw men.
6. **Trade-offs:** explain benefits, costs, risks, operational consequences, and reversibility.
7. **Uncertainty:** separate facts, estimates, assumptions, unknowns, and validation work.
8. **Delivery and ownership:** identify dependencies, accountable owners, checkpoints, and next actions.
9. **Ask:** state exactly what the audience must approve, choose, provide, or accept.
10. **Traceability:** link to the ADR, diagrams, review findings, risk register, and migration roadmap.

The order can be shortened for a one-minute update or expanded for a steering committee, but the logic should remain intact.

### 3.4 Audience analysis: who needs what?

Stakeholders are not defined only by job title. Identify their decision rights, concerns, context, likely questions, and what evidence they can evaluate.

| Audience (illustrative) | Typical concern | Evidence that may help | Desired outcome |
|---|---|---|---|
| Executive sponsor | Business value, timing, cost exposure, strategic fit | Options, ranges, milestones, consequence of delay | Approve, reject, fund, or request a bounded investigation |
| Finance partner | Total cost, cost drivers, budget profile, sensitivity | Cost model, assumptions, ranges, operating-cost comparison | Validate funding envelope and conditions |
| Data/platform engineers | Interfaces, throughput, failure behavior, operability | Architecture views, test results, capacity assumptions, runbooks | Confirm feasibility and identify engineering work |
| Security/privacy reviewers | Data exposure, access boundaries, threat treatment, residual risk | Data-flow diagrams, threat model, control evidence, exception record | Approve within authority, require treatment, or escalate risk |
| Operations/SRE | Support load, alerting, recovery, change windows, handover | SLOs, runbooks, restore tests, ownership and escalation map | Accept operational readiness or list blockers |
| Domain/business owner | Data freshness, usability, service continuity, consumer impact | Service-level definition, migration sequence, consumer contract | Confirm business acceptance and transition tolerance |
| Architecture/governance forum | Alignment, exceptions, consistency, decision traceability | ADR, standards fit, review findings, risk register | Record decision, conditions, exception, or follow-up |

**How to use the table:** verify the actual audience and authority for the real decision. These roles are common examples, not claims about Northbridge Bank or a mandatory committee structure.

### 3.5 Technical versus business communication

The fact base remains constant. The explanation changes.

| Element | Technical brief | Business brief |
|---|---|---|
| Opening | Constraint, mechanism, decision, and system scope | Outcome, decision required, and business consequence |
| Main question | Can this work safely and reliably under stated conditions? | Is the outcome worth the cost, risk, time, and operational change? |
| Evidence | Measurements, design details, test method, failure modes, dependencies | Cost ranges, customer/service implications, delivery milestones, risk exposure |
| Vocabulary | Precise terms; define ambiguous terms such as “real-time” | Plain language; retain exact numbers and define technical terms when material |
| Detail | Interfaces, protocols, capacity, security controls, failure behavior | Options, cost drivers, consequences, choices, conditions, timing |
| Risks | Attack paths, failure modes, control gaps, residual risk | Business impact, likelihood/uncertainty, owner, mitigation, decision needed |
| Ask | Confirm design, supply evidence, approve technical choice, close finding | Approve funding/option, accept a defined risk, or authorize a pilot |
| Appendix | Full diagrams, ADR, test evidence, threat model | Technical appendix and traceable source artefacts available on request |

**Trade-off:** excessive detail obscures the decision; excessive simplification can make the decision false. Use progressive disclosure: lead with the decision, then make deeper evidence accessible.

### 3.6 Translating technical implications without distortion

Translation is not the same as spin. Keep the metric, unit, measurement scope, assumptions, and uncertainty visible.

| Technical statement | Accurate business-facing interpretation | Caveat that must remain visible |
|---|---|---|
| “The pilot measured p95 query latency of 3 seconds under workload W.” | “In the tested workload, 95% of measured queries completed within 3 seconds.” | This does not prove the same result for different concurrency, data volume, or production traffic. |
| “Configured recovery point objective (RPO) is 15 minutes.” | “The recovery design targets no more than 15 minutes of data loss in the specified failure scenario.” | An objective is not proof of achieved recovery; test results and scope matter. |
| “Availability target is 99.5% per month.” | “The target allows approximately 0.5% of the defined monthly interval to be unavailable.” | Do not imply measured performance or contract coverage unless verified. A 30-day month gives 216 minutes at 0.5%, but the measurement definition matters. |
| “A pilot showed 20% lower compute use for one workload.” | “That pilot workload used 20% less compute under the tested conditions.” | Do not extrapolate the result to all workloads or total cost without further evidence. |
| “The target design uses asynchronous replication.” | “The design prioritizes lower replication delay/decoupling under its assumptions but can have a non-zero lag during failure.” | State the actual lag/recovery behavior and the data-loss scenario; do not imply zero data loss. |

For each translation, ask: did I preserve the unit, denominator, time window, scope, confidence, and difference between target and observed result?

## 4. Intermediate level — compare options and support decisions

### 4.1 Build the argument from requirements to consequences

A recommendation should have a visible chain:

`Requirement or concern → criterion → evidence → option assessment → consequence → recommendation → decision ask`

For example, “choose managed streaming because it is modern” is not a defensible argument. A stronger argument names the required freshness, event volume, failure behavior, security constraints, operational skills, expected cost range, alternatives, and the evidence still needed. If a criterion cannot be measured yet, state the proxy or validation activity rather than manufacturing a result.

### 4.2 Establish a controlled fact base

Create one fact register before writing audience-specific versions.

| ID | Claim | Type | Value / statement | Source or basis | Scope / caveat | Owner / next check |
|---|---|---|---|---|---|---|
| F-01 | Existing ingestion is scheduled in batches | Scenario assumption | Current state is batch-oriented | Synthetic Northbridge scenario brief | No production inventory supplied | Architecture owner to validate |
| E-01 | Pilot freshness | Illustrative test evidence | p95 arrival-to-availability: 18 seconds in the pilot | Synthetic test summary | Workload and duration defined in the test plan; not production performance | Data engineering lead to reproduce |
| A-01 | Peak event volume | Assumption | 4,000 events/second | Synthetic planning input | Sensitivity range still needed | Capacity owner to validate |
| C-01 | Required freshness | Stated scenario requirement | 60 seconds for the selected alerting use case | Synthetic business requirement | Applies only to named use case, not every data product | Business owner to confirm |
| U-01 | Production cost | Unknown | No production-scale price estimate yet | Not yet measured | Must not be described as a known cost | Finance/platform team to estimate |

The evidence labels are part of the communication. “Scenario assumption” is not interchangeable with “observed result.” If source artefacts conflict, stop and reconcile them or disclose the conflict; do not quietly select the more persuasive value.

### 4.3 Compare genuine alternatives fairly

Use criteria tied to the actual decision. Keep raw evidence and interpretation visible. Weighted scoring can structure discussion but does not turn subjective judgments into objective truth.

**Illustrative Northbridge decision:** whether to modernize an alerting-data pipeline with (A) the current batch pattern, (B) a managed streaming pattern, or (C) a bounded streaming pilot followed by a gated rollout. These are candidate approaches for the exercise, not adopted technologies or real bank decisions.

Scenario assumptions:

- The selected use case has a stated freshness requirement of 60 seconds.
- Current batch processing is assumed to have a typical freshness of 10–20 minutes for this exercise; no production measurement is supplied.
- A synthetic pilot is assumed to have measured 18-second p95 arrival-to-availability under a defined test workload. The result does not establish production performance.
- Production-scale cost, security sign-off, and operational readiness remain unresolved.

| Criterion | Weight (illustrative) | A: Continue batch | B: Full streaming rollout now | C: Pilot then gated rollout |
|---|---:|---|---|---|
| Meets 60-second freshness need | 25% | Unlikely under stated assumption | Plausible; production proof needed | Testable before broad commitment |
| Delivery and reversibility | 15% | Low change, but does not resolve gap | Broad change; harder to reverse quickly | Smaller initial scope; explicit exit gate |
| Cost confidence | 15% | Existing cost baseline still needs validation | Weak until scale estimate is complete | Pilot can improve cost evidence; pilot itself costs money |
| Security/privacy readiness | 15% | Existing controls still require review | Must be proven before rollout | Security review can be a pilot/rollout gate |
| Operational readiness | 15% | Familiar operations assumed | New alerting, replay, on-call, and recovery duties | Readiness can be demonstrated before expansion |
| Long-term fit | 15% | May not fit the stated freshness need | Potentially strong if validated | Preserves option to stop or adapt based on evidence |

This table is qualitative; the weights are not empirically derived and the entries are not measured ratings. The defensible provisional conclusion is: **option C is the preferred learning-stage recommendation if the 60-second requirement is confirmed and the pilot can be safely isolated**, because it tests key uncertainties before broad rollout. It is not a production approval. If a pilot cannot be isolated safely, or if a verified existing alternative meets the requirement at materially lower risk, the recommendation should be revisited.

### 4.4 Explain the trade-off explicitly

Use a four-part sentence:

1. **Gain:** what the option improves.
2. **Cost:** what it consumes or makes harder.
3. **Risk:** what could go wrong and who is affected.
4. **Condition:** what must be true or tested for the recommendation to hold.

Example: “A bounded streaming pilot could test whether the alerting use case meets its 60-second freshness requirement. It adds engineering and operational work and does not yet establish production-scale cost or recovery behavior. We recommend proceeding only after access boundaries, replay controls, observability, ownership, and a rollback path are reviewed; wider rollout depends on measured acceptance criteria.”

### 4.5 Communicating costs, benefits, and uncertainty

Never present an estimate as a committed cost or a pilot result as a production guarantee. Use ranges when the underlying uncertainty warrants them, and state the model inputs.

| Claim type | Appropriate phrasing | Avoid |
|---|---|---|
| Verified measurement | “The test report records X under workload Y.” | “The system will always deliver X.” |
| Estimate | “The current estimate is X–Y, based on assumptions A and B.” | “It will cost X.” |
| Assumption | “For planning, we assume X; the owner will validate it by checkpoint Y.” | “X is the current state.” |
| Hypothesis | “We expect X; the pilot is designed to test it.” | “The pilot will prove X” before it runs |
| Unknown | “Production-scale cost is not yet known; this blocks funding approval beyond the pilot.” | Hiding the unknown in an appendix or excluding it from the ask |
| Risk | “If X occurs, consequence Y is possible; control Z reduces but does not eliminate the risk.” | “The design is secure” without scoped evidence |

For cost-benefit communication, include one-time migration effort, recurring platform cost, support/on-call load, training, coexistence, data reconciliation, and decommissioning where relevant. Do not cherry-pick the new platform's run cost while excluding the cost of operating both old and new systems during transition.

### 4.6 Visuals and documents: choose the right artifact

| Artifact | Best use | Required discipline |
|---|---|---|
| Context or container diagram | Explain scope, systems, actors, and major responsibilities | Match current/target state; include legend and scope; avoid detail irrelevant to the concern |
| Data-flow/trust-boundary diagram | Explain movement, exposure, control points, and dependencies | Show material flows and boundary crossings; link to threat findings |
| ADR summary | Explain a decision, alternatives, rationale, and consequences | Keep status, owner, assumptions, and revisit triggers current |
| Review findings and risk register | Explain what is unsafe, unresolved, or accepted | Distinguish finding severity from risk rating; show owner, treatment, due date, residual risk |
| Migration roadmap | Explain sequence, checkpoints, dependencies, and rollback | Avoid implying that a plan is feasible until dependencies and resource assumptions are validated |
| Executive decision brief | Support a specific choice or approval | Lead with the ask, decision criteria, material trade-offs, cost range, risk, and conditions |
| Technical appendix | Allow detailed challenge and implementation planning | Provide traceable evidence, test scope, interfaces, failure modes, and operational implications |
| Q&A / decision log | Preserve questions, answers, dissent, and outcomes | Record evidence links and unresolved follow-ups; do not make a verbal promise disappear |

## 5. Advanced level — stakeholder engagement and decision governance

### 5.1 Map influence, interest, concerns, and decision rights

Before a significant review, prepare a stakeholder map. Influence and interest are useful planning dimensions, but they do not replace formal authority or required control reviews.

| Stakeholder | Decision right (verify in context) | Likely challenge | Preparation |
|---|---|---|---|
| Business sponsor | Funding or business priority within delegated authority | “What outcome changes, and what happens if we delay?” | Explain requirement, options, milestones, uncertainty, and cost of delay without invented benefit figures. |
| Finance | Budget scrutiny or financial-model review | “What is included in total cost?” | Include migration, coexistence, training, support, recurring usage, and exit/decommissioning assumptions. |
| Security/privacy | Review or approval under the applicable governance process | “Which data crosses which boundary, and what residual risk remains?” | Bring data-flow views, threat model, control evidence, risk owner, and any exception request. |
| Engineering | Feasibility and implementation planning | “What load, failure, compatibility, and replay behavior is assumed?” | Provide interfaces, workload assumptions, test plans, dependencies, and failure-mode analysis. |
| Operations | Operational readiness acceptance where assigned | “Who is on call, what alerts fire, and how do we restore?” | Show runbooks, SLOs, restore/rollback evidence, ownership, escalation, and handover. |
| Governance/architecture forum | Decision or exception authority where established | “What standard or principle is being adapted, and why?” | Link pattern fit analysis, ADR, deviation record, risk treatment, expiry, and compensating controls. |

The table is an illustrative planning aid. For an actual organization, confirm authority from its operating model and governance records; do not infer it from job title.

### 5.2 Handle disagreement by separating facts, values, and preferences

Disagreement often persists because people are arguing at different levels.

- **Fact dispute:** “The pilot cannot sustain the required throughput.” Resolve with a reproducible test, defined workload, and agreed acceptance criterion.
- **Assumption dispute:** “Volume will double next year.” Identify the forecast owner, range, basis, and sensitivity analysis.
- **Value conflict:** “We prefer lower operating risk over faster delivery.” Make the priority explicit and show the consequence.
- **Preference:** “Our team prefers the existing tool.” Ask whether it implies a requirement, capability constraint, support concern, or simply familiarity.
- **Authority conflict:** “This team can accept the exception.” Verify the decision rights and escalate to the designated authority if unclear.

A good facilitator asks each participant to state the claim, its evidence, the consequence if wrong, and what would change their view. Record unresolved dissent and the agreed method for resolving it. Do not describe a stakeholder as “blocking” the decision merely because they raise a valid risk.

### 5.3 Recommendation strength and decision conditions

Use language that matches evidence strength.

| Strength | Appropriate language | Evidence condition |
|---|---|---|
| Strong recommendation | “Recommend option A because it meets criteria 1–3 with evidence X; residual risks Y remain.” | Critical criteria have adequate evidence; alternatives have been assessed fairly. |
| Conditional recommendation | “Recommend A if conditions X and Y are satisfied; otherwise revisit B.” | One or more material dependencies remain unresolved and have explicit gates. |
| Provisional hypothesis | “Pilot A to test whether X is true.” | Evidence is insufficient for broad commitment, but a bounded test is justified. |
| No recommendation yet | “Do not choose until evidence X is available; the options cannot currently be compared fairly.” | A missing fact could reverse the choice or create unacceptable risk. |

Do not use “approved,” “compliant,” “secure,” “production-ready,” “guaranteed,” or “zero risk” unless the relevant authority and evidence support the exact claim and scope.

### 5.4 Explain risk without either alarmism or minimization

A useful risk statement includes scenario, cause, consequence, likelihood or uncertainty, existing controls, residual risk, owner, treatment, trigger, and requested decision. Communicate the same substance in plain language and technical terms.

**Example — synthetic:** “If the new streaming pipeline replays an event more than once and the consumer is not idempotent, the alerting data may contain duplicate events. The engineering mitigation is idempotent processing plus replay tests. Until those tests pass, the risk remains open; the data-product owner is accountable for consumer acceptance, and the platform team owns the replay mechanism. Wider rollout is blocked until the agreed test evidence is reviewed.”

Do not hide the distinction between risk reduction and risk elimination. If a risk is accepted, state who has authority to accept it, what scope it covers, which compensating controls apply, when acceptance expires, and what triggers reconsideration. Communication does not itself authorize risk acceptance.

### 5.5 Advanced meeting design: pre-wire, decide, record, follow up

For a high-impact architecture decision:

1. Identify the actual decision-maker, required reviewers, affected owners, and consulted parties.
2. Send a short pre-read with the ask, options, key evidence, uncertainties, and links to source artefacts.
3. Ask stakeholders to submit objections and missing evidence before the meeting when practical.
4. Start the meeting with the decision and constraints; do not walk through every diagram by default.
5. Use the criteria and fact base already agreed in the ADR or review plan.
6. Separate new evidence from changed preferences. If a material fact changes, reopen the analysis rather than forcing a decision.
7. Record decision, conditions, dissent, risk acceptance (if authorized), owners, due dates, and revisit triggers.
8. Send the outcome in the same terms to all affected groups; update the ADR, risk register, roadmap, and ownership records as needed.
9. Test comprehension: ask a participant to restate the trade-off and what happens next.

### 5.6 AI, analytics, and retrieval-specific communication

For AI-enabled data products, avoid vague claims such as “the model is accurate” or “retrieval is secure.” Name the evaluated task, test set, metric, failure classes, data permissions, evaluation date, and known limitations. Distinguish retrieval quality from answer correctness; distinguish offline evaluation from production behavior; and explain how source freshness, access-control filtering, prompt injection, data leakage, and human review affect the intended use.

If the system is not evaluated for a particular user group, language, data class, or workload, say so. A business brief can state the consequence—such as “the assistant may omit or misstate information and must not be used as the sole basis for this decision”—while the technical appendix describes evaluation methods and failure cases. Do not promise that a guardrail eliminates a risk merely because it exists in a diagram.

## 6. Worked Northbridge Bank example: one decision, multiple audiences

### 6.1 Scenario and evidence register

**All values below are synthetic teaching inputs.** They are not real costs, measurements, forecasts, requirements, or decisions from an actual bank.

The hypothetical bank wants to improve freshness for one alerting-data use case. The current process is described for the exercise as batch-oriented. The scenario requirement is a maximum 60-second freshness target for that use case. A bounded pilot is being considered before any broad streaming rollout.

| ID | Statement | Classification | Scope and limitation |
|---|---|---|---|
| S-01 | The current path is batch-oriented and typically delivers data in 10–20 minutes | Scenario assumption | No production telemetry is supplied; validate the actual baseline. |
| R-01 | The selected alerting use case needs data available within 60 seconds | Synthetic stated requirement | Applies only to the named use case; business owner must confirm. |
| E-01 | A pilot measured p95 arrival-to-availability of 18 seconds | Synthetic test result | Only for the documented pilot workload and test window; does not prove production-scale performance. |
| A-01 | Planning peak is 4,000 events/second | Synthetic assumption | No verified capacity forecast; validate with a range and load test. |
| U-01 | Production-scale total cost is unknown | Explicit unknown | Must not be presented as a known amount; pilot cost and cost-model work are required. |
| U-02 | Security, privacy, replay, recovery, and on-call readiness are not yet approved for broad rollout | Scenario status assumption | Approval criteria and evidence must be defined by the relevant owners. |
| D-01 | A pilot followed by a gated rollout is the provisional recommendation | Recommendation | Conditional on safe isolation, access controls, replay/idempotency tests, operational readiness, and a credible cost range. |

### 6.2 Option summary

| Option | Benefit | Cost or downside | Key uncertainty | Provisional disposition |
|---|---|---|---|---|
| A — Continue batch | Lowest immediate change; familiar operation under the scenario assumption | Does not appear to meet the 60-second requirement if the 10–20 minute assumption holds | Actual baseline and whether a narrower batch change could meet the requirement | Retain only if requirement is revised or evidence shows a viable batch solution |
| B — Roll out streaming broadly now | Could address freshness more quickly across a larger scope | Larger initial blast radius; higher coordination and operational readiness burden | Production-scale cost, failure/replay behavior, controls, and ownership | Not recommended before material unknowns are resolved |
| C — Bounded pilot, then gated rollout | Learns about performance, cost, controls, and support before broad commitment | Adds pilot work and may delay full benefit; pilot needs isolation and exit criteria | Whether pilot conditions represent production use | Preferred provisional path if safe isolation and measurable gates are feasible |

The recommendation is not “streaming is always better.” It is that the bounded pilot is a more reversible way to test material uncertainties under the scenario's stated freshness requirement. If the pilot cannot be isolated safely, the recommendation changes.

### 6.3 Technical brief

**Decision requested:** authorize a bounded pilot for the named alerting-data use case, subject to agreed entry criteria. This is not a request to approve broad production rollout.

**Context and requirement.** The scenario describes a batch-oriented current path with assumed 10–20 minute freshness. The use-case requirement is 60 seconds. Those baseline figures require confirmation from actual telemetry and the business owner before a real decision.

**Evidence.** A synthetic pilot result reports p95 arrival-to-availability of 18 seconds under its documented workload. It is not production evidence and does not establish capacity at the assumed 4,000 events/second planning peak. Production-scale cost is unknown.

**Recommendation.** Run a bounded streaming pilot only after confirming isolation, data access boundaries, observability, idempotent/replay behavior, named operational ownership, and rollback. Define the workload, measurement window, success thresholds, and stop conditions before the test begins.

**Alternatives.** Continuing batch avoids immediate change but does not meet the stated requirement if the assumed baseline is confirmed. A broad rollout has a larger blast radius while cost, scale, recovery, and operating readiness remain unproven. A pilot is reversible only if the scope, data flows, consumers, and exit path are actually isolated.

**Acceptance gates.** Before recommending rollout, require: (1) agreed freshness measurement and workload; (2) repeatable load and failure/replay tests; (3) security/privacy review and closure or authorized acceptance of material findings; (4) cost range including coexistence and support; (5) on-call/runbook and recovery readiness; (6) data reconciliation and consumer acceptance; and (7) a tested rollback/disable path.

**Risks and limitations.** The pilot may not represent production load. Duplicate or out-of-order events may affect downstream results. Cost could rise at scale. Access-control or operational gaps may block rollout. The platform team owns the pilot mechanics in this illustrative model; the data-product owner owns consumer acceptance; security and operations reviewers act within their verified decision rights. Actual owners and authorities must be assigned in the real operating model.

**Ask.** Approve only the bounded pilot and its agreed test effort; defer the broad rollout decision until evidence and gates are reviewed. Record the decision and conditions in the ADR and decision log.

### 6.4 Business brief for the same decision

**Decision requested:** approve a limited pilot to test whether the alerting use case can receive data within 60 seconds, while keeping the full rollout decision open until cost, control, and operating evidence is available.

**Why this matters.** The exercise's assumed current process can take 10–20 minutes to make data available, which would not satisfy a 60-second requirement if the assumption is confirmed. A synthetic pilot reported 18-second p95 freshness under its test conditions. That is encouraging, but it is not proof of production performance.

**Options.** Continuing the current process avoids immediate change but may not meet the use case's stated need. Rolling out broadly now could expand the change before cost, recovery, access controls, and support responsibilities are proven. A limited pilot costs time and effort and may delay wider benefits, but it can test the main uncertainties before a larger commitment.

**Recommendation and conditions.** Approve a bounded pilot only if it can be isolated safely, with clear success and stop criteria. The pilot should measure freshness at the expected workload, test failure and replay behavior, confirm data protections and support ownership, and produce a production-scale cost range. No broad rollout is being requested today.

**What remains unknown.** Production-scale cost and performance are not yet established. Security/privacy and operational readiness are not yet approved for broad rollout. If the pilot fails its agreed criteria or the cost/risk case is not acceptable, the team should stop, redesign, or reconsider the alternatives.

**Decision needed.** Authorize the bounded pilot and the work needed to gather evidence. Schedule a separate rollout decision after the acceptance gates have been reviewed. The pilot approval must not be interpreted as accepting residual production risks or approving production expansion. Any acceptance of a narrowly scoped pilot-only risk must be separately authorized, time-bounded, and recorded; it does not carry over to production.

### 6.5 Fact-consistency check between briefs

| Fact or claim | Technical brief | Business brief | Consistent? |
|---|---|---|---|
| Current freshness | Assumed 10–20 minutes; baseline needs validation | Same assumption and caveat | Yes |
| Required freshness | 60 seconds for named use case | Same requirement and scope | Yes |
| Pilot result | 18-second p95 in synthetic test workload; not production proof | Same value, percentile, and limitation | Yes |
| Planning peak | 4,000 events/second assumption; needs validation | Not emphasized in main body; available in technical appendix | Yes, omission of detail is not contradiction |
| Production cost | Unknown | Unknown | Yes |
| Security/operations readiness | Not approved for broad rollout | Not yet approved for broad rollout | Yes |
| Recommendation | Bounded pilot with gates; no broad rollout approval | Same | Yes |
| Rollback and stop conditions | Explicit technical acceptance gates | Stop if criteria or cost/risk case fails | Yes |
| Risk acceptance | No production residual risk is accepted by the pilot decision; any pilot-only acceptance is separately scoped and time-bounded | Same limitation and scope | Yes |

A fact-consistency check is not merely a search for identical words. It checks that scope, units, dates, denominators, uncertainty, decision status, and consequences mean the same thing. Audience-specific omission is acceptable only if it does not conceal a material fact or alter the decision.

### 6.6 Illustrative decision-log update after a hypothetical meeting

The briefs above are **pre-decision** communications. The following is a separate, synthetic example of how the record could be updated after a hypothetical meeting; it is not a claim that a real decision occurred.

| Field | Example entry |
|---|---|
| Decision ID | ADR-009 (illustrative; replace with the repository's actual ID convention) |
| Log status | Decision recorded — bounded pilot authorized with conditions |
| Decision | Authorize only the isolated pilot for the named alerting-data use case; do not authorize broad rollout |
| Rationale | The 60-second requirement is a scenario input; the 18-second p95 result is limited synthetic pilot evidence; cost, production-scale capacity, and operational readiness remain unproven |
| Conditions | Confirm pilot isolation; define workload and thresholds before test; complete access-boundary review; test replay/idempotency and rollback; assign on-call and data-product owners; estimate total cost including coexistence |
| Risk acceptance | No production residual risk accepted. A separate, time-bounded acceptance may apply only to the pilot-only replay/duplicate-event risk described below, if the designated authority approves it |
| Dissent / unresolved questions | Peak workload representativeness and production-scale cost remain open; record any stakeholder dissent verbatim or as an attributed summary |
| Owners / follow-up | Assign named owners and due dates in the actual operating model before the entry is treated as complete |
| Revisit trigger | Any failed gate, unsafe isolation, unacceptable cost range, changed freshness requirement, or material new security/operational finding |
| Traceability | Link to the current/target diagrams, DFD and threat review, risk register, ownership matrix, migration roadmap, and technical/business briefs |

The entry must be updated to match the actual meeting outcome. Do not mark a decision approved, name an authority, or imply risk acceptance unless the relevant record supports it.

### 6.7 Example of a narrowly scoped risk-acceptance request

This is an **illustrative request template**, not an assertion that the request was approved. It demonstrates the roadmap's expectation that a steering-committee pack can state a risk-acceptance request explicitly.

| Field | Example request |
|---|---|
| Risk ID / scenario | R-PILOT-01 (synthetic): replay testing may create duplicate or out-of-order events in the isolated pilot output before consumer behavior is fully characterized |
| Scope requested | Test-only pilot environment and test-only consumers; no production alerting decisions, production writes, or downstream production feed may depend on this output |
| Existing/required controls | Isolated topic and credentials; synthetic or approved test data; explicit environment labels; monitoring; kill switch; replay test evidence; named test owner; immediate stop if isolation is breached |
| Residual risk being requested | A bounded chance of misleading pilot results or duplicate records within the isolated test output during replay experiments—not permission to tolerate duplicate production alerts |
| Proposed acceptance authority | The scenario must name an actually delegated risk authority. For this exercise only, assume a designated risk-review authority exists; verify real authority in an actual organization |
| Expiry | At the end of the pilot or the agreed review date, whichever occurs first; no automatic extension |
| Revisit / rejection triggers | Any route to production consumers, exposure of non-approved data, missing isolation evidence, uncontrolled replay, or failure to stop the test |
| Decision wording | “Approve / reject this limited pilot-only residual risk for the stated scope and expiry. This does not approve production rollout or accept any production residual risk.” |

If the minimum controls cannot be demonstrated, the correct recommendation is to **reject or defer the request**, not to use risk acceptance to bypass a missing safety boundary. A risk-acceptance request must identify the risk, scope, authority, controls, expiry, and stop conditions; it is not a generic statement that “the risk is low.”

## 7. Challenging stakeholder questions and evidence-based answers

The answers below are examples, not claims about a real bank. A good answer can be “we do not yet know,” provided it names the evidence needed, owner, and decision consequence.

| Question | Weak answer | Better answer structure |
|---|---|---|
| “Can you guarantee 60-second freshness?” | “Yes, the pilot achieved 18 seconds.” | “No production guarantee is justified yet. The pilot measured 18-second p95 under a defined workload. We need a representative load test and agreed production measurement before making a production claim.” |
| “What will this cost?” | “It should be inexpensive.” | “Production-scale cost is currently unknown. We will model compute, storage, network, support, coexistence, and migration costs; present a range with assumptions; and make broad rollout conditional on finance review.” |
| “Why not roll out now?” | “Streaming is the modern pattern.” | “The broad rollout has unresolved cost, replay, control, recovery, and ownership questions. A bounded pilot reduces the initial commitment if isolation and exit criteria are real. If those gates cannot be met, we should not proceed as proposed.” |
| “Does the pilot prove scalability?” | “It processed the test load.” | “It proves only the workload and duration in the test report. It does not establish the assumed peak, growth, failure recovery, or production concurrency unless those conditions were tested.” |
| “Is it secure?” | “Security is built in.” | “The design identifies controls, but broad rollout is not approved. We need the threat review, access-boundary evidence, control tests, findings disposition, and authorized residual-risk decision.” |
| “What if it fails during migration?” | “We can roll back.” | “Rollback is a claim to validate. The plan needs a tested disable/switch-back path, reconciliation of writes/events, explicit data-loss/duplication limits, owner, trigger, and recovery time evidence.” |
| “Who is accountable after launch?” | “The platform team owns it.” | “The operating model must name separate accountable owners for the service, data product, consumer acceptance, security decisions, and cost controls where applicable. The handover is a gate, not an assumption.” |
| “Can we remove the old system after the pilot?” | “Yes, once the new system works.” | “No. Decommissioning requires consumer inventory, reconciliation, retention/legal checks where applicable, backup/restore evidence, sign-off, and a rollback window or explicit retirement decision.” |
| “What would change your recommendation?” | “Nothing; this is the best design.” | “Evidence that batch can meet the requirement at acceptable cost, a failed pilot, an unsafe isolation design, unacceptable cost, or a material new control requirement could change the recommendation.” |
| “Can you approve the residual risk today?” | “The risk is low.” | “Risk acceptance depends on the designated authority, documented scope, residual-risk evidence, compensating controls, expiry, and review trigger. The current brief requests a pilot, not blanket risk acceptance.” |

### 7.1 A disciplined answer formula

Use **Answer → Evidence → Limitation → Next step**:

- **Answer:** respond directly to the question.
- **Evidence:** cite the specific artifact, measurement, requirement, or review finding.
- **Limitation:** state the scope or uncertainty that affects the answer.
- **Next step:** identify the test, owner, due date, decision, or escalation needed.

Do not answer a question you cannot support by substituting confidence, jargon, or a promise. A transparent evidence gap is more useful than false certainty.

## 8. Practical exercises

Try each exercise before reading the model answer. Use the scenario fact register in Section 6; do not invent new facts unless you label them as new assumptions. For broader topic coverage and scoring, also use the module [practice-question bank](practice-questions.md).

### Exercise 1 — Beginner: explain a technical decision to a non-technical audience

**Input:** “The pilot achieved p95 arrival-to-availability of 18 seconds, but production-scale capacity and cost are not yet validated.”

**Task:** Write a 3–5 sentence explanation for a business sponsor. Preserve the percentile, test scope, and unknowns. Include the decision implication.

**Expected output:** One short paragraph, no unexplained acronyms, no claim of production readiness.

**Model answer:**

> In the limited test, 95% of measured data arrivals became available within 18 seconds. That result applies only to the tested workload; it does not prove that the service will meet the same target at full production scale. Production capacity and total cost still need to be validated. We recommend using a bounded pilot to test those questions before deciding whether to expand the service.

**Validation criteria:**

- [ ] Preserves “p95” meaning rather than saying every event took 18 seconds.
- [ ] Identifies the result as a limited test, not production evidence.
- [ ] Names both capacity and cost as unresolved.
- [ ] Ends with a clear decision implication.

### Exercise 2 — Intermediate: produce technical and business briefs from one fact base

**Task:** Write two briefs for the same pilot decision. The technical brief must include workload assumptions, test scope, failure/replay tests, security/privacy gates, rollback, operational ownership, and links to ADR/risk evidence. The business brief must include the requirement, options, cost unknown, residual risk, pilot conditions, and explicit ask.

**Expected outputs:** Two briefs plus a fact-consistency table containing at least eight claims.

**Objective validation:**

1. Both briefs use the same 60-second requirement, 18-second synthetic p95 pilot result, 10–20 minute assumed baseline, and unknown production cost.
2. Neither brief calls the pilot a production guarantee.
3. Both describe the recommendation as a bounded pilot, not broad rollout approval.
4. Material risks and acceptance gates are not hidden from either audience.
5. Technical detail differs by audience, but scope and uncertainty do not.

**Model-answer outline:** Use Sections 6.3–6.5. A learner's wording can differ as long as all five checks pass.

### Exercise 3 — Advanced: defend a migration recommendation before competing stakeholders

**Scenario:** The business sponsor prioritizes freshness and asks for broad rollout quickly. Finance refuses an open-ended operating-cost commitment. Security asks for evidence on access boundaries and replay. Operations says on-call and recovery duties are not yet defined. Engineering says the pilot may not represent peak workload.

**Task:** Prepare a decision pack containing:

1. One-page executive brief with decision ask and recommendation strength.
2. Three-option comparison.
3. Technical appendix with pilot workload, failure/replay tests, and rollback criteria.
4. Risk summary with owner, treatment, residual risk, and decision authority.
5. An explicit, narrowly scoped risk-acceptance request with compensating controls, delegated authority, expiry, and rejection triggers—or a documented rationale for requesting no acceptance if the risk cannot be safely bounded.
6. Migration checkpoints and explicit stop/go criteria, including funding/cost conditions.
7. Ten anticipated questions and evidence-based answers.
8. Decision-log entry recording the decision, conditions, dissent, risk-acceptance outcome, and follow-up actions.

**Model position:** Recommend a bounded pilot conditionally, not a broad rollout. State that the recommendation depends on safe isolation, agreed test criteria, access/security review, replay/idempotency behavior, named operational ownership, and a credible cost range. If isolation or minimum controls cannot be established, defer the pilot and resolve the gap first. Record the sponsor's urgency as a priority, not as proof that the technical gates can be skipped.

**Validation criteria:**

- [ ] Recommendation strength matches evidence.
- [ ] All stakeholder concerns are acknowledged and assigned to an owner or decision authority.
- [ ] Any risk-acceptance request is bounded, time-limited, assigned to a verified authority, and explicit about compensating controls and rejection triggers; no request is used to bypass missing minimum controls.
- [ ] Cost and timeline are not invented; missing estimates have owners and due checkpoints.
- [ ] At least one condition could cause the recommendation to change.
- [ ] Stop/go gates are testable and have evidence requirements.
- [ ] The decision log preserves dissent and unresolved questions.

### Exercise 4 — Cross-audience fact consistency

Compare the following statements:

- Technical brief: “The pilot measured p95 freshness of 18 seconds under workload W; production-scale cost is unknown.”
- Business brief: “The platform will deliver alerts in under 20 seconds at production scale and lower operating costs.”

Identify the defects and rewrite the business statement.

**Model answer:** The business statement turns a limited pilot result into a production promise and asserts a cost benefit that is not evidenced. A corrected version is: “In a limited test, 95% of measured data arrivals became available within 18 seconds. Production-scale performance and cost remain unvalidated; the proposed pilot expansion is conditional on representative testing and a cost review.”

### Exercise 5 — Challenging questions

Answer at least five questions from Section 7 using the Answer → Evidence → Limitation → Next step method. For each answer, name the source artifact or state “evidence not yet available.”

**Expected output:** Q&A log with question, answer, evidence link/ID, limitation, action owner, due checkpoint, and whether the question changes the recommendation.

**Validation:** No answer invents a measurement, hides uncertainty, or implies approval from a person who lacks verified authority.

## 9. Reusable communication templates

### 9.1 Audience and concern analysis

```markdown
# Audience and Concern Analysis

Decision / topic:
Scope and version/date:

| Stakeholder/group | Decision authority (verified source) | Main concern/question | Required evidence | Likely objection | Desired action | Communication format | Owner |
|---|---|---|---|---|---|---|---|

Unresolved authority or consultation questions:
Assumptions about audience knowledge:
How comprehension will be checked:
```

### 9.2 One-page architecture decision brief

```markdown
# Architecture Decision Brief

Title / ID:
Status: Draft / For review / Decision requested / Decided
Decision owner and date:
Audience:

## Decision needed
What must be decided, by whom, and by when?

## Recommendation
Preferred option, strength of recommendation, conditions, and what would change it.

## Context and requirement
Problem, scope, business outcome, constraints, and linked requirements.

## Options considered
| Option | Benefits | Costs / downsides | Risks | Evidence / uncertainty | Reversibility |
|---|---|---|---|---|---|

## Evidence and assumptions
Separate verified facts, measurements, estimates, assumptions, unknowns, and opinions.

## Trade-offs and consequences
What improves, what worsens, who bears the consequence, and over what period?

## Risks and controls
Risk ID, owner, treatment, residual risk, expiry/review date, and acceptance authority if relevant.

## Delivery and operating implications
Dependencies, milestones, accountable owners, support duties, rollback, and handover.

## Decision ask and conditions
Specific approval/choice/funding/risk decision, entry criteria, deadline, and consequence of delay.

## Traceability
ADR, architecture views, review findings, risk register, pattern/exception record, ownership map, roadmap.

## Open questions and follow-ups
Question, owner, due date, evidence needed, and effect on recommendation.
```

### 9.3 Technical brief template

```markdown
# Technical Brief

Decision and scope:
Requirements and constraints:
Relevant architecture views and data/trust boundaries:
Options and evaluation criteria:
Measurements and test conditions:
Interfaces, capacity, failure modes, security/privacy implications:
Operational model, ownership, monitoring, recovery, and support:
Risks, existing controls, gaps, residual risk:
Assumptions and unknowns:
Recommendation and conditions:
Acceptance tests / go-no-go criteria:
Rollback / recovery plan:
Decision ask, owners, and due dates:
Links to ADR, risk register, and migration roadmap:
```

### 9.4 Business brief template

```markdown
# Business Brief

Decision requested:
Business outcome and scope:
What is known (with source and date):
What remains estimated or unknown:
Options and consequences:
Cost / time range and included/excluded items:
Customer, service, operational, security, and privacy implications:
Principal risks, mitigations, residual risk, and owner:
Recommendation and conditions:
What would change the recommendation:
Decision deadline and consequence of delay:
Approval requested / not requested:
Technical appendix and source artefacts:
```

### 9.5 Challenging-question log

```markdown
| ID | Question / objection | Direct answer | Evidence ID / source | Limitation or uncertainty | Action / owner / due date | Does this change the recommendation? |
|---|---|---|---|---|---|---|
```

### 9.6 Brief consistency review checklist

- [ ] Same decision, scope, status, and recommendation conditions in both versions.
- [ ] Same numerical values, units, percentiles, time windows, and denominators.
- [ ] Observed measurements remain distinct from targets and estimates.
- [ ] Cost assumptions include the same relevant scope; exclusions are visible.
- [ ] Risks and residual risks are not omitted if material to the decision.
- [ ] Unresolved dependencies, decision gates, and rollback conditions are consistent.
- [ ] Named owners and approval authority match the operating model.
- [ ] The business version is plain-language but not inaccurate.
- [ ] The technical version contains enough detail to challenge feasibility and controls.
- [ ] Claims trace to an ADR, diagram, test, review finding, risk record, or roadmap entry.
- [ ] A non-specialist can restate the decision and its main trade-off.
- [ ] A technical reviewer can reproduce the key evidence interpretation.

## 10. Common communication failures

| Failure | Why it fails | Correction |
|---|---|---|
| Lead with product or technology name | It obscures the problem and desired outcome | Lead with the requirement, constraint, and decision |
| Hide risks to secure approval | Creates later distrust and unowned exposure | State risk, treatment, residual risk, and acceptance authority |
| Present estimates as facts | Creates false confidence and bad commitments | Label estimate, basis, range, owner, and validation date |
| Use different facts in different briefs | Stakeholders make decisions from contradictory premises | Maintain one fact register and run a consistency check |
| Translate “p95” as “always” | Changes a statistical statement into a guarantee | Explain the percentile and test scope precisely |
| Say “secure,” “compliant,” or “production-ready” without evidence | Makes a broad claim beyond what the artifacts establish | State the tested scope, evidence, gaps, and approval status |
| Bury the decision ask | The audience may understand the content but not know what to do | Put the requested action, authority, and timing near the start and end |
| Offer only a preferred option | Prevents meaningful trade-off assessment | Present plausible alternatives and explain why each is or is not suitable |
| Use jargon to signal expertise | Reduces comprehension without improving accuracy | Define material terms and move deep detail to an appendix |
| Over-simplify a risk | Hides who is affected or what must be controlled | Translate mechanism into consequence while preserving conditions and limits |
| Treat disagreement as ignorance | Misses legitimate differences in risk tolerance or priorities | Separate facts, assumptions, values, preferences, and authority |
| Promise a date without validated dependencies | Turns a planning hypothesis into a false commitment | Communicate ranges, gates, critical dependencies, and what can change the date |
| Confuse recommendation with approval | Implies authority that may not exist | State decision status and the actual decision-maker explicitly |
| Use a diagram without scope or legend | Readers infer details that were never asserted | Label current/target state, boundaries, assumptions, and omitted detail |
| Fail to record the outcome | The same question returns and conditions are lost | Update the ADR, decision log, risk register, and roadmap after the meeting |

## 11. Integrating the full architecture review package

Topic 09 is the communication layer for the package assembled across the module. Use this traceability chain:

| Topic | Core artifact | Communication question |
|---|---|---|
| [01 — Context, container, component, deployment diagrams](01-context-container-component-and-deployment-diagrams.md) | Architecture views | What system is in scope and how is it structured? |
| [02 — Data flow and trust boundaries](02-data-flow-and-trust-boundary-diagrams.md) | Flow and boundary views | Where does data move, cross trust boundaries, or become exposed? |
| [03 — Architecture description and viewpoints](03-architecture-description-and-viewpoints.md) | Stakeholder/concern/view mapping | Which view answers each audience's concern? |
| [04 — ADRs and decision log](04-architecture-decision-records-and-decision-log.md) | Decision rationale and status | Why was this choice made, what alternatives were considered, and what would change it? |
| [05 — Design reviews, threat models, risk registers](05-design-reviews-threat-models-and-risk-registers.md) | Findings and risk treatment | What is unresolved, who owns it, and what risk remains? |
| [06 — Reference architectures, standards, reusable patterns](06-reference-architectures-standards-and-reusable-patterns.md) | Pattern fit and deviation/exception records | Why is the pattern appropriate here, and what has been adapted? |
| [07 — Team boundaries and operating model](07-team-boundaries-ownership-and-platform-operating-model.md) | Ownership and interface matrix | Who implements, operates, approves, supports, and escalates? |
| [08 — Migration roadmaps and modernization](08-migration-roadmaps-and-architecture-modernization.md) | Phases, dependencies, checkpoints, rollback | How do we move safely from current to target, and what must be proven at each gate? |
| [09 — Stakeholder communication](09-communicating-trade-offs-to-technical-and-business-stakeholders.md) | Technical and business briefs, Q&A, decision record | Can each audience make an informed decision from the same fact base? |

Before presenting, check that the current state is honest, target requirements trace to views, important decisions have rationale and alternatives, review findings have owners, risk acceptance is authorized and time-bounded where applicable, pattern deviations are explicit, team responsibilities are assigned, and migration phases have evidence-based checkpoints. Do not use a polished presentation to hide gaps in the underlying package.

## 12. Topic 09 mastery criteria

You have demonstrated mastery when you can:

- [ ] Identify stakeholders, concerns, decision authority, and desired action.
- [ ] Produce technical and business briefs for one decision from a shared fact register.
- [ ] Preserve metrics, units, scope, assumptions, uncertainty, risks, and decision status across versions.
- [ ] Translate technical implications into business consequences accurately.
- [ ] Compare genuine alternatives using relevant criteria and evidence.
- [ ] State recommendation strength, conditions, and what would change the recommendation.
- [ ] Answer challenging questions with evidence, limitations, and next actions.
- [ ] Record decisions, conditions, dissent, and follow-ups in the decision log.
- [ ] Link claims to the relevant architecture views, ADRs, findings, risks, ownership records, and roadmap.
- [ ] Obtain a non-specialist restatement of the trade-off and a technical review of the key evidence.
- [ ] Attempt the [module practice questions](practice-questions.md) and record remaining gaps.

## 13. Topic 09 completion gate

The Topic 09 gate is satisfied when all of the following are true:

- [ ] Technical brief and business brief exist for the same decision.
- [ ] A fact-consistency review passes; different emphasis does not change the facts.
- [ ] The recommendation, alternatives, consequences, risks, costs, and uncertainty are explicit.
- [ ] The decision ask, decision-maker, conditions, and timing are clear.
- [ ] The Q&A anticipates at least five difficult questions and answers them with traceable evidence or clearly marked evidence gaps.
- [ ] A non-specialist can restate the trade-off correctly.
- [ ] A technical reviewer can trace at least three material claims to their sources.
- [ ] The decision outcome and follow-ups are recorded in the decision log.
- [ ] [Practice questions](practice-questions.md) are attempted and learning gaps logged.

These are learning-gate criteria recommended by the module roadmap, not an external certification or proof that a real architecture is safe, compliant, funded, or production-ready.

## 14. Preparation for the final current-state-to-target-state architecture review

The final project integrates all nine topics. Your communication package should be a faithful summary of the underlying evidence, not an independent narrative with new facts. The project completion gate in the module roadmap also asks for a coherent current-to-target transition, documented decisions and trade-offs, risks and dependencies, a feasible migration plan, consistent technical and business briefs, reproducible critical-path calculation, traceability of claims to evidence, and a defense against reviewer questions.

For the final review, rehearse five things:

1. Explain the current problem and target outcome in two minutes without hiding a material limitation.
2. Defend the recommendation against at least two plausible alternatives.
3. Explain the largest residual risk, its owner, and the decision authority that may accept it.
4. Describe the next migration checkpoint, its entry/exit criteria, and rollback trigger.
5. Answer “What evidence would change your recommendation?” with specific tests, thresholds, or findings.

## 15. Final self-review

Before sharing any architecture recommendation, ask:

1. What decision am I asking this audience to make?
2. What are the most important facts, and where are they recorded?
3. Which statements are assumptions, estimates, hypotheses, opinions, or unknowns?
4. Have I presented the strongest plausible alternatives fairly?
5. What gets better, what gets worse, and who bears each consequence?
6. What material risk remains after planned controls?
7. What evidence could change the recommendation?
8. Do the technical and business versions tell the same factual story?
9. Are ownership, decision authority, dependencies, and deadlines verified rather than inferred?
10. Have I recorded the outcome, dissent, conditions, and follow-up actions?

If any answer is unclear, fix the source evidence or state the gap explicitly. A communication artifact should make the architecture easier to challenge and govern—not harder.
