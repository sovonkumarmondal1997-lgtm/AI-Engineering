# 06 — Architecture Trade-offs and Decision Criteria

> **Purpose:** Learn to frame an architecture decision, eliminate options that fail non-negotiable requirements, compare credible alternatives using evidence, test whether the recommendation survives uncertainty, and communicate the choice without hiding what it sacrifices.
>
> **Case-study convention:** Northbridge Bank is fictional. All Northbridge figures, targets, costs, ratings, weights, and vendor statements in this lesson are illustrative teaching inputs—not facts about a real bank, verified vendor commitments, or legal/regulatory requirements. Replace them with validated project evidence before making a real decision.

## 1. Learning objectives

By the end of this topic, you should be able to:

1. Define an architecture problem and its decision scope, including what is and is not being decided, the deadline, and the accountable decision-maker.
2. Derive decision criteria from validated business requirements, measurable quality targets, constraints, assumptions, dependencies, risks, and architecture principles.
3. Distinguish **hard gates** from **scored preferences** and eliminate infeasible options before comparing scores.
4. Generate at least three credible alternatives, including a “do nothing/minimal change” baseline, without weakening alternatives to make a favourite win.
5. Build a comparison matrix in which each rating is supported by evidence, a calculation, a test, or an explicitly labelled judgement.
6. Use quantitative and qualitative methods—including weighted scoring—while explaining their limitations.
7. Compare whole-life costs, including implementation, operations, people, migration, support, and exit costs.
8. Analyse trade-offs among freshness, latency, throughput, availability, security, privacy, scalability, maintainability, delivery time, operational burden, and cost where relevant.
9. Test sensitivity to changed weights and uncertain inputs; identify when the ranking changes and what evidence would change the decision.
10. Assess reversibility, lock-in, staged commitment, and long-term consequences.
11. Recommend a decision to technical and business audiences, stating the benefits, sacrifices, residual risks, assumptions, and conditions that would reverse the recommendation.
12. Produce the decision statement, evidence-backed comparison matrix, sensitivity analysis, recommendation, and answers to the Topic 6 practice questions.

**Outcome standard:** a recommendation is not “Option B scored highest.” It is a reasoned statement of which feasible option best meets the agreed priorities, why the evidence supports it, what is being accepted or sacrificed, and when the conclusion must be revisited.

## 2. Why the topic matters in real-world Data Architecture

Architecture decisions are choices under competing demands. A design that improves freshness may increase operational complexity and cost. A design that minimises spend may deliver data too late for a business decision. A highly available service may require redundancy, tested recovery, additional support skills, and more complex failure handling. A standardised platform may simplify governance but limit some domain-specific needs.

There is rarely one option that maximises every quality attribute at once. Architecture work therefore requires transparent choices—not a search for a supposedly perfect technology.

### 2.1 What is an architecture trade-off?

A **trade-off** is the consequence of favouring one objective over another when the alternatives cannot satisfy every objective equally. A trade-off should name:

- **Gain:** what improves and for whom.
- **Sacrifice:** what worsens, costs more, becomes harder, or remains unavailable.
- **Evidence:** why the expected gain or sacrifice is credible.
- **Exposure:** which assumptions or risks could change the outcome.
- **Acceptance:** who has authority to accept the residual consequence.
- **Reversal condition:** what measurable change or new evidence would justify reopening the choice.

Example: an event-driven ingestion path might reduce transaction-to-consumer delay relative to a nightly batch, but require continuously operated consumers, event-schema governance, replay/idempotency handling, monitoring, and more demanding incident response. The comparison is incomplete if it reports only latency.

### 2.2 Decision, option, criterion, rating, and recommendation

| Term | Meaning | Practical question |
|---|---|---|
| Decision | A bounded choice that needs an accountable outcome | What exactly must be decided now? |
| Alternative/option | A credible way to satisfy the decision scope | What could we actually implement and operate? |
| Criterion | A property used to judge an option | What matters, and why? |
| Hard gate | A non-negotiable condition for eligibility | Does this option meet every must-have? |
| Evidence | A source, measurement, calculation, test, contract, or reasoned estimate | What supports this claim? |
| Rating | A value assigned against a defined scale | How well does the evidence meet this criterion? |
| Weight | The relative importance of a scored criterion | How much should this criterion influence the comparison? |
| Recommendation | A reasoned proposal based on gates, evidence, priorities, and uncertainty | Which feasible option best fits the decision context? |
| Decision authority | Person or governance body empowered to approve or accept the decision | Who makes the final call and accepts residual risk? |

A criterion is not the same as a solution. “Use streaming” is a proposed solution; “make fraud-case data available within the agreed freshness target” is a criterion derived from a business requirement. Selecting a technology first and inventing criteria afterward reverses the reasoning process.

### 2.3 The decision sequence

Use this order:

1. Establish the decision and business outcome.
2. Confirm requirements, measurable targets, constraints, assumptions, dependencies, and risks from Topics 1–5.
3. Agree on criteria and distinguish gates from preferences **before scoring**.
4. Generate realistic options, including the baseline.
5. Test every option against hard gates; remove or explicitly redesign infeasible options.
6. Collect evidence and compare eligible options.
7. Quantify cost and measurable performance where possible; label qualitative judgements honestly.
8. Run sensitivity and uncertainty analysis.
9. Recommend an option, document accepted trade-offs and reversal conditions, and pass the outcome into Topic 7 ADRs.

If analysis reveals a missing requirement or criterion, return to the source requirement or stakeholder discussion and update the traceability chain. Do not silently patch the scorecard to make the current winner remain the winner.

### 2.4 How this topic fits the roadmap

This topic depends on Modules 1–5 in `02-Requirements-Constraints-and-Architecture-Decisions/`: stakeholder discovery and business requirements; functional and non-functional requirements; data volume, velocity, variety, and growth estimation; latency, throughput, freshness, and availability targets; and constraints, assumptions, dependencies, and risks. It also builds on 2D.1 Topic 4’s quality-attribute trade-offs and Topic 6’s framework-suitability criteria.

The next topic, **07 — Architecture Decision Records (ADRs)**, records the decision context, drivers, options, outcome, rationale, consequences, and links to supporting evidence. This lesson produces the inputs for an ADR; it does not replace the ADR.

## 3. Prerequisite concepts

Before beginning, be comfortable with the following:

- **Business need and requirement:** a validated outcome or testable condition, with a source and priority.
- **Non-functional requirement / quality attribute:** a property such as latency, freshness, availability, security, privacy, or maintainability. Prefer measurable targets over adjectives such as “fast” or “highly available.”
- **Data sizing:** expected and peak volume, event rate, retention, growth, and their assumptions. A design that works only at average load may be infeasible at peak.
- **Service target:** a defined indicator, target, time window, scope, and measurement method.
- **Constraint:** a boundary that an option must respect unless the authorised owner changes it.
- **Assumption:** an unverified belief being used for planning or evaluation.
- **Dependency:** a system, team, contract, data source, approval, or capability required for the option to work.
- **Risk:** uncertain event or condition that may affect objectives, with likelihood, impact, owner, and response.
- **Evidence quality:** the distinction between measured results, documented commitments, estimates, opinions, and unknowns.
- **Traceability:** links from stakeholder needs to requirements, criteria, options, decisions, and follow-up actions.

### Prerequisite check

For the decision you are about to analyse, can you answer these questions?

1. Which business outcome is being optimised or protected?
2. Which requirements are mandatory, and which are preferences?
3. What measurable targets and peak-load estimates apply?
4. Which constraints are verified, and which claims are assumptions?
5. Which dependencies could make an option impossible or unreliable?
6. Who owns the decision and who accepts residual business risk?

If these answers are missing, mark them as open questions and assign owners. Do not convert missing evidence into confident ratings.

## 4. Beginner-level learning sequence

### 4.1 Define the decision before discussing solutions

A decision statement should name the question, scope, exclusions, deadline, decision-maker, and affected stakeholders.

**Weak:** “We need a modern data platform.”

This does not define the business problem, the scope, or success.

**Stronger illustrative example:**

> By 30 November, decide how the fraud-case tool will receive authorised card-transaction events for the first production release. The decision covers ingestion and delivery to the case tool; it does not select the bank-wide analytics warehouse. The decision must meet the approved freshness and security gates. The accountable platform decision owner will recommend an option to the fraud product sponsor and security reviewer.

The date and roles above are illustrative. In a real project, use the agreed project plan and governance.

Define the boundary explicitly. If the decision is only about the ingestion path, do not quietly compare entire cloud providers, enterprise-wide data models, and dashboard products at the same time.

### 4.2 Derive criteria from requirements and constraints

A **decision criterion** is a testable or assessable property that distinguishes acceptable options in relation to the outcome. Every criterion should trace to a requirement, constraint, risk, or approved architecture principle.

Common criterion classes:

| Class | Purpose | Example |
|---|---|---|
| Requirement-based gate | Enforce a must-have | Must satisfy approved data-access and audit requirements |
| Quality-based criterion | Compare how well options meet quality needs | Measured p95 freshness, throughput headroom, recovery capability |
| Cost | Compare whole-life financial burden | Three-year build, run, support, people, migration, exit |
| Time | Compare delivery or time to value | Time to a production-ready release, including dependencies |
| Risk | Compare uncertainty and consequence | Dependency concentration, vendor commitment, operational failure modes |
| Operability | Compare ability to run and support | On-call complexity, observability, replay, recovery, skills |
| Strategic fit | Compare alignment with approved direction | Existing platform standards and reusable capabilities |

Not every criterion belongs in every decision. Keep criteria that discriminate among options or protect an important outcome. If a criterion is identical for all options, record that fact, but it may not need a weight in the ranking. Do not omit a criterion simply because the preferred option performs poorly against it.

### 4.3 Hard gates versus scored preferences

A **hard gate** is a non-negotiable eligibility condition. If an option fails it, the option is not eligible for scoring unless the authorised owner formally changes the requirement or the option is redesigned and retested.

A **scored preference** is a dimension on which eligible options may perform better or worse. Cost, implementation speed, ease of operation, or additional performance headroom may be scored if no mandatory threshold has been breached.

| Statement | Classification | Treatment |
|---|---|---|
| “The path must meet the approved security and access-control requirements.” | Hard gate, if formally approved as mandatory | Verify with security evidence before scoring |
| “The target is p95 freshness of at most 30 seconds.” | Hard gate if the target is approved and mandatory | Measure or prove feasibility; failing option is ineligible |
| “Prefer lower three-year cost, all else equal.” | Scored preference | Compare whole-life costs |
| “The team would rather use the platform it already knows.” | Preference / possible operability evidence | Assess skills and support impact; do not silently treat it as a veto |
| “The vendor says its product can handle the load.” | Unverified claim until supported | Request test results, contract evidence, or a representative proof of concept |
| “We do not yet know the source event rate at peak.” | Open question / uncertainty | Assign owner, estimate a range, and validate |
| “The source team must publish a stable event contract.” | Dependency | Identify owner, commitment date, interface, and failure consequence |
| “The source team may miss the contract date.” | Risk | Assess likelihood and impact; define mitigation and trigger |

A gate is not a very heavily weighted criterion. If a mandatory privacy condition receives a high but finite score weight, a cheap option could still win despite violating the condition. That is a modelling error.

**Why include a baseline?** “Do nothing” or “minimal change” reveals the cost and consequences of continuing as-is. It may be infeasible if the current state already violates a mandatory target, but it remains a useful reference. State whether the baseline is eligible or only a comparator.

### 4.4 Generate at least three credible alternatives

Alternatives must be technically and organisationally plausible, fairly described, and evaluated at comparable scope. A useful set might include:

- **Option A — Baseline/minimal change:** retain the current scheduled extract and make only limited reliability improvements.
- **Option B — Managed micro-batch:** use a managed ingestion service on short intervals, with explicit delay, retries, and monitoring.
- **Option C — Event-driven path:** publish transaction events to a durable event channel and process them continuously into the case tool.

These are illustrative patterns, not a prescribed technology choice. Real options must be grounded in source capabilities, team skills, approved platforms, security requirements, delivery constraints, and representative tests. If the baseline cannot meet an approved freshness gate, mark it **infeasible** instead of assigning it a low score and allowing it to compete.

Do not make Option A intentionally weak, Option B artificially expensive, or Option C magically perfect. Give each alternative the strongest credible design within the same decision scope.

### 4.5 Beginner exercise: frame the fraud-path decision

**Task:** For “How should the fraud-case tool receive card transactions?”, write:

1. One decision statement with scope and exclusions.
2. Five criteria derived from business needs or constraints.
3. Three alternatives, including a baseline.
4. At least two hard gates.
5. The decision-maker and the evidence needed to assess feasibility.

**Answer guidance (illustrative):**

- Decision: choose the ingestion/delivery pattern for card transactions into the fraud-case tool for a defined release.
- Criteria: freshness; peak throughput/headroom; security/auditability; whole-life cost; operability/delivery time.
- Alternatives: minimal change, managed micro-batch, event-driven delivery.
- Gates: approved security/access requirements; the approved freshness target if formally mandatory; source interface feasibility.
- Evidence: source event-rate estimate, end-to-end freshness measurement, security review, dependency commitment, support-capability assessment, and comparable cost model.

The exact gate status must come from the real requirements register. The example does not make the illustrative 30-second target a universal bank requirement.

**Ability to demonstrate:** frame a bounded decision and list feasible alternatives with criteria, rather than jumping directly to a product or architecture pattern.

## 5. Intermediate-level learning sequence

### 5.1 Build a comparison matrix with evidence in each cell

The matrix uses criteria as rows and alternatives as columns. Each cell should contain the evidence or a reference to it, not merely a rating. A score without a reason is not auditable.

Recommended sequence:

1. Record the criterion definition, source requirement, and whether it is a gate or scored criterion.
2. Agree the rating scale and weights before viewing totals.
3. Record raw evidence: measurements, test results, cost calculations, commitments, or labelled estimates.
4. Apply hard gates to every option.
5. Score only eligible options.
6. Calculate totals and verify arithmetic independently.
7. Explain what the totals do and do not mean.

### 5.2 Define a rating scale before scoring

For this worked example, use a 1–5 ordinal scale:

| Rating | Meaning for a scored preference |
|---:|---|
| 1 | Poor fit; material weakness relative to the criterion |
| 2 | Below desired level; meaningful mitigation needed |
| 3 | Acceptable; meets the defined expected level |
| 4 | Strong fit; exceeds the expected level with evidence |
| 5 | Very strong fit; materially exceeds the expected level with evidence |

This scale is **illustrative**. It is not a universal measurement unit. A “4” for operability is not necessarily equal to a “4” for cost. Document criterion-specific anchors where possible—for example, define what cost bands correspond to ratings 1–5 before rating options.

Use `N/A` or “not evidenced” when a rating cannot be justified. Do not quietly turn missing evidence into a middle score. Depending on decision criticality, the correct response may be to gather evidence, use a range, run a pilot, or make a conditional decision.

### 5.3 Weighted scoring: formula and limits

When criteria are genuinely tradeable, a weighted model can help make priorities visible.

\[
\text{Score(option)}=\sum_{i=1}^{n} w_i r_i(\text{option}), \qquad \sum_{i=1}^{n} w_i=1
\]

Where:

- \(w_i\) is the weight for criterion \(i\), expressed as a fraction.
- \(r_i\) is the option’s rating for that criterion on the agreed scale.
- The weights sum to 1 (or 100%).
- Hard gates are evaluated separately and are not rescued by a high total score.

Weights should reflect business priorities and risk appetite, not the architect’s favourite technology. Agree them with the accountable stakeholders before scoring. A scoring model can clarify a judgement; it cannot make subjective inputs objective.

Limitations to state explicitly:

- Weights express judgement and can be contested.
- Correlated criteria can double-count one benefit—for example, “freshness” and “latency” may overlap if both measure the same end-to-end delay.
- An aggregate score can hide a severe weakness; always show criterion-level results and gates.
- Ratings on an ordinal scale are not precise physical measurements. Multiplication and addition are a decision aid, not proof of mathematical objectivity.
- Small differences may be noise, especially when evidence is uncertain.
- The model may omit an important criterion; the matrix must be reviewed for completeness.
- Scores should not be tuned after seeing which option wins.

### 5.4 Worked illustrative comparison: Northbridge Bank fraud-case ingestion

**Decision question:** Which ingestion pattern should deliver authorised card-transaction events to the fraud-case tool?

**Illustrative requirements and assumptions for this exercise only:**

- A provisional target of p95 freshness at or below 30 seconds is being used to demonstrate the method. In a real decision, confirm whether this target is approved and mandatory.
- Security and access-control requirements are mandatory and must be reviewed against actual bank policies.
- A source interface and stable event contract are required for the event-driven option.
- Costs and performance below are hypothetical planning estimates, not vendor quotes or measured production results.
- For teaching purposes, assume an initial feasibility review finds the baseline and the managed micro-batch option do not meet the provisional 30-second target, while the event-driven option may meet it but needs a representative test. This is not evidence that any real product will perform that way.

#### Step 1 — Gate assessment before scoring

| Gate | Baseline / minimal change | Managed micro-batch | Event-driven |
|---|---|---|---|
| Approved security and access controls | Unverified; must review | Unverified; must review | Unverified; must review |
| Provisional p95 freshness ≤ 30 s | **Fails** in this illustrative case | **Fails** in this illustrative case | **Not yet proven**; test required |
| Source/interface feasibility | Existing interface assumed, validate | Short-interval access assumed, validate | Stable event contract required; dependency open |
| Eligible for weighted scoring now? | No, if 30 s is a mandatory gate | No, if 30 s is a mandatory gate | Not yet; first prove all gates |

The table deliberately does not score infeasible options. If the 30-second target is only a preference and stakeholders formally agree a different target, that is a requirements decision—not an analyst’s quiet adjustment to save an option.

The event-driven option is not automatically eligible merely because it is promising. It must pass the required tests and security review. Until then, its ranking is provisional.

#### Step 2 — Illustrative cost evidence

Assume the following **hypothetical three-year total cost of ownership (TCO)** estimates, in thousands of currency units. They include initial build, recurring run/support and people costs, migration, and exit cost. The numbers are not sourced from real quotes.

| Cost component (illustrative, thousands of currency units) | Baseline / minimal change | Managed micro-batch | Event-driven |
|---|---:|---:|---:|
| Initial build **plus initial migration, combined** | 80 | 120 | 180 |
| Three-year run, support, and people | 150 | 180 | 240 |
| Exit cost at end of horizon (excluding initial migration) | 20 | 25 | 30 |
| **Three-year TCO** | **250** | **325** | **450** |

For this table, the combined first row is a single cost input; do not add migration a second time. The calculation is:

\[
TCO_3 = (build + initial\ migration) + (three\text{-}year\ run/support/people) + exit
\]

Therefore: baseline = 80 + 150 + 20 = 250; managed micro-batch = 120 + 180 + 25 = 325; event-driven = 180 + 240 + 30 = 450 (all in thousands of illustrative currency units). The table groups the recurring components into a three-year total for simplicity. In a real model, show year-by-year costs, assumptions about growth and staffing, discounting if required by the organisation’s finance method, and uncertainty ranges. Do not compare one option’s licence-only cost with another option’s fully loaded cost.

The lowest TCO does not make an option acceptable if it fails a mandatory requirement. Conversely, a more expensive option is not automatically better: the extra cost needs to buy a business-relevant benefit that matters under the agreed criteria.

#### Step 3 — A separate, explicitly changed hypothetical in which scoring is permitted

The initial gate table is a **30-second freshness scenario**: baseline and managed micro-batch fail, and event-driven is unproven. They must not be scored as eligible under that scenario.

To demonstrate weighted-score arithmetic without violating that rule, use a **separate hypothetical**: the authorised business owner has formally changed the minimum freshness gate to p95 ≤ 60 seconds for this teaching scenario, and a representative test/security review is assumed to have confirmed that all three options pass the revised gates. These are illustrative assumptions, not facts about Northbridge or an implied recommendation. If an option must be redesigned to pass, its costs, delivery estimate, evidence, and ratings must be recalculated before scoring.

The ratings below are supported by the illustrative evidence and criterion-specific anchors in the following table. They are teaching inputs, not real measurements or commitments.

| Scored criterion | Weight | Baseline / minimal change | Managed micro-batch | Event-driven |
|---|---:|---:|---:|---:|
| Whole-life cost | 0.25 | 5 | 4 | 2 |
| Delivery time | 0.15 | 5 | 4 | 2 |
| Freshness/headroom beyond the revised 60-second gate | 0.25 | 2 | 3 | 5 |
| Operability / supportability | 0.20 | 4 | 4 | 2 |
| Scalability / future growth | 0.15 | 2 | 3 | 5 |
| **Weight total** | **1.00** |  |  |  |

**Illustrative rating anchors and evidence rationale**

| Criterion | Pre-agreed illustrative rating anchor | Baseline evidence / rating | Managed micro-batch evidence / rating | Event-driven evidence / rating |
|---|---|---|---|---|
| Three-year TCO | 5 ≤ 250k; 4 = 251–325k; 3 = 326–400k; 2 = 401–500k; 1 > 500k | TCO model = 250k → **5** | TCO model = 325k → **4** | TCO model = 450k → **2** |
| Delivery time | 5 ≤ 4 months; 4 = >4–6 months; 3 = >6–8 months; 2 = >8–10 months; 1 >10 months | Assumed 4-month plan → **5** | Assumed 6-month plan → **4** | Assumed 9-month plan → **2** |
| p95 freshness | 5 ≤15 s; 4 = >15–30 s; 3 = >30–45 s; 2 = >45–60 s; 1 >60 s (gate fail) | Assumed test result 55 s → **2** | Assumed test result 40 s → **3** | Assumed test result 15 s → **5** |
| Operability / supportability | 5 = established support model and low incremental burden; 4 = existing team/runbooks and manageable incremental work; 3 = moderate new work with training/runbooks required; 2 = substantial new operational burden or key recovery work unproven; 1 = unsupported/unacceptable burden | Existing runbook/team, with manual reconciliation burden noted → **4** (illustrative judgement) | Managed scheduling, established support, some pipeline operations → **4** (illustrative judgement) | New on-call, replay/idempotency, and incident-response duties not yet proven → **2** (illustrative judgement) |
| Scalability / future growth | Tested sustainable peak capacity / forecast peak: 5 ≥3.5×; 4 = 2.5–<3.5×; 3 = 1.5–<2.5×; 2 = 1.0–<1.5×; 1 <1.0× (gate fail if required capacity is missed) | Assumed load test 1.2× forecast peak → **2** | Assumed load test 2.0× forecast peak → **3** | Assumed load test 4.0× forecast peak → **5** |

All values in this evidence table are invented for the exercise and explicitly labelled as assumptions. In a real decision, replace them with reportable test outputs, approved plans, support-model evidence, and a finance-reviewed cost model. The ordinal rating scale is a structured judgement aid; it does not make the inputs objectively comparable.
**Calculation for baseline:**

\[
(0.25 \times 5)+(0.15 \times 5)+(0.25 \times 2)+(0.20 \times 4)+(0.15 \times 2)
=1.25+0.75+0.50+0.80+0.30=3.60
\]

**Calculation for managed micro-batch:**

\[
(0.25 \times 4)+(0.15 \times 4)+(0.25 \times 3)+(0.20 \times 4)+(0.15 \times 3)
=1.00+0.60+0.75+0.80+0.45=3.60
\]

**Calculation for event-driven:**

\[
(0.25 \times 2)+(0.15 \times 2)+(0.25 \times 5)+(0.20 \times 2)+(0.15 \times 5)
=0.50+0.30+1.25+0.40+0.75=3.20
\]

Under these illustrative weights, baseline and managed micro-batch tie at 3.60, with event-driven at 3.20. This does **not** prove the baseline is preferable in the original 30-second scenario, because baseline and micro-batch failed that gate. The scores apply only to the separate hypothetical with an authorised 60-second gate and assumed verified gate passage. Never use a weighted total to erase an earlier hard-gate failure, and do not reuse the scores if the target, design, or evidence changes.

The numbers also demonstrate that weights matter. If freshness is mandatory, it should be a gate. If freshness is a scored preference after the minimum target is met, the weight reflects how much additional freshness matters relative to cost, delivery time, and operability.

### 5.5 Evidence strength and fair comparison

Use a consistent evidence hierarchy, while considering context:

1. Representative production-like test or measured operational data.
2. Validated proof of concept or benchmark using documented workload and configuration.
3. Contractual commitment or formally approved service specification, with scope and exclusions understood.
4. Detailed engineering estimate supported by explicit assumptions.
5. Expert judgement with rationale.
6. Unsupported assertion or marketing claim.

This is not an absolute rule that a contract always outranks a test: the evidence answers different questions. A contract may define an obligation; a test demonstrates behaviour under a particular workload. Record what each source does and does not prove.

Fair comparison requires:

- Same workload, time horizon, and scope.
- Same target definitions and measurement boundaries.
- Same cost categories and growth assumptions.
- Equivalent implementation maturity; do not compare a fully engineered incumbent with an imaginary perfect new platform.
- Visible gaps, exclusions, and dependencies.
- An explicit distinction between observed fact, estimate, assumption, and unknown.

### 5.6 Quantify where possible; keep qualitative judgements labelled

Useful quantitative comparisons include:

- p50/p95/p99 latency or freshness under a defined workload.
- Sustained and peak throughput, queue growth, and headroom.
- Availability and recovery behaviour under defined failure conditions.
- Build, run, support, staffing, migration, and exit costs.
- Time to first production value, including approvals and dependency lead times.
- Retention, storage, network, and processing growth where relevant.

Use qualitative assessment for factors that cannot yet be measured reliably, such as the quality of an upgrade path or fit with a team’s operating model. Define what “strong fit” means and identify the reviewer. Do not give a qualitative score the appearance of measured precision.

### 5.7 Intermediate exercise: compare three options

**Task:** Build a matrix for the fraud path with at least three alternatives. Include:

- The decision statement and scope.
- At least two hard gates.
- Four or more scored criteria, each linked to a requirement, constraint, or principle.
- Rating definitions and weights that sum to 1.
- Evidence for each rating.
- A cost model covering build, run, people, migration, and exit.
- A short conclusion explaining the result and the model’s limitations.

**Answer guidance:** First decide whether each option passes every gate. If an option fails, mark it ineligible and explain whether redesign or authorised requirement change could make it feasible. For eligible options, show raw evidence before ratings, calculate totals transparently, and explain the result in prose. If evidence is weak, show a range or identify the test needed; do not make up a precise score.

**Ability to demonstrate:** every rating can be traced to evidence, and the conclusion is expressed as a decision argument rather than a naked number.

## 6. Advanced-level learning sequence

### 6.1 Make conflicting quality attributes explicit

A trade-off analysis must show what each option gives up.

| Dimension | Possible gain | Possible sacrifice or exposure | Evidence to seek |
|---|---|---|---|
| Lower latency / fresher data | Earlier decisions, faster response | More continuous processing, higher run cost, more complex recovery | End-to-end p95/p99 tests; operations model |
| Higher throughput / scalability | Handles growth and peaks | Extra capacity cost, partitioning/rebalancing complexity | Peak-load tests; growth and headroom model |
| Higher availability | Reduced service interruption | Redundancy cost, more failure modes, operational complexity | Dependency analysis; failure and recovery tests |
| Stronger security/privacy controls | Reduced exposure and better controlled access | Additional design, approval, and operational effort | Threat model, access tests, approved control evidence |
| Faster delivery | Earlier business value | Less time for migration, testing, automation, or simplification if unmanaged | Delivery plan, dependency commitments, quality gates |
| Lower cost | Less spend | Less headroom, slower delivery, reduced resilience, or higher manual effort | Whole-life cost model and explicit target impact |
| Maintainability | Easier change and support | Upfront standardisation or refactoring cost | Support model, skills review, change/upgrade test |
| Lower operational complexity | Fewer components and failure paths | May constrain flexibility or peak performance | Runbook review, incident simulation, dependency map |

Do not imply that every pair always conflicts. The actual relationship depends on the design, workload, and context. The point is to test the relationship with evidence and state the trade-off where one exists.

### 6.2 Sensitivity analysis: test whether the recommendation survives

A recommendation based on uncertain weights or estimates may be fragile. **Sensitivity analysis** varies one input at a time—or selected combinations—to determine whether the preferred option changes.

Use this sequence:

1. Identify the least certain and most decision-sensitive inputs.
2. Define plausible low, base, and high values, with sources or rationale.
3. Recalculate scores or feasibility for each case.
4. Identify the value or threshold at which the ranking changes.
5. Explain whether that threshold is plausible.
6. Decide what evidence to gather, what contingency to plan, or whether to choose a more robust option.

Pseudocode:

```text
for each uncertain input x:
    for x_value in [low, base, high]:
        update affected evidence or criterion ratings
        recheck hard gates
        recompute scores for eligible options
        record preferred option and score margin
report the assumptions and thresholds that change the recommendation
```

If an input affects a hard gate, recheck feasibility first. A sensitivity test must not allow a weighted score to rescue an option that fails a non-negotiable requirement.

### 6.3 Worked sensitivity example: changing priorities

Consider a **separate illustrative decision** in which all three options have already passed the mandatory gates. Use the intermediate ratings for cost, delivery, freshness, operability, and scalability.

**Base weights:**

- Cost 25%
- Delivery time 15%
- Freshness/headroom 25%
- Operability 20%
- Scalability 15%

The base scores are baseline 3.60, managed micro-batch 3.60, event-driven 3.20. These values are illustrative and depend on the ratings.

Now suppose stakeholder discovery establishes that additional freshness and growth headroom are much more important than initial cost and delivery speed. An illustrative revised weight set is:

| Criterion | Base weight | Revised weight |
|---|---:|---:|
| Cost | 0.25 | 0.10 |
| Delivery time | 0.15 | 0.10 |
| Freshness/headroom | 0.25 | 0.40 |
| Operability | 0.20 | 0.15 |
| Scalability | 0.15 | 0.25 |
| **Total** | **1.00** | **1.00** |

Revised scores:

- **Baseline:** \(0.10(5)+0.10(5)+0.40(2)+0.15(4)+0.25(2)=0.50+0.50+0.80+0.60+0.50=2.90\)
- **Managed micro-batch:** \(0.10(4)+0.10(4)+0.40(3)+0.15(4)+0.25(3)=0.40+0.40+1.20+0.60+0.75=3.35\)
- **Event-driven:** \(0.10(2)+0.10(2)+0.40(5)+0.15(2)+0.25(5)=0.20+0.20+2.00+0.30+1.25=3.95\)

Under the revised illustrative priorities, event-driven ranks first (3.95), managed micro-batch second (3.35), and baseline third (2.90). The recommendation changes because the agreed priority weights changed—not because the technology changed.

This is a useful finding only if the new weights are justified by stakeholder outcomes and recorded before the result is used. Do not change weights merely to make the desired option win. The revised ranking still depends on the assumed ratings, the hard-gate status, and real evidence.

### 6.4 Sensitivity to uncertain performance or cost

Weights are only one source of uncertainty. Inputs such as event rate, cloud consumption, vendor support cost, source-system availability, or achievable p95 freshness may be uncertain.

Use ranges rather than false precision. Example:

| Input | Illustrative low / base / high | Why it matters | Validation |
|---|---|---|---|
| Peak event rate | 0.7× / 1.0× / 1.8× of planning estimate | Could affect throughput, cost, and gate feasibility | Source telemetry and peak-window analysis |
| Event-driven support effort | 0.8× / 1.0× / 1.5× of estimate | Could change TCO and operability rating | Staffing plan, pilot, support review |
| Source contract delivery | On time / 1 month late / 3 months late | Could change delivery feasibility | Named source owner and dated commitment |
| Achievable p95 freshness | 15 s / 30 s / 60 s | May pass or fail a hard target | Representative end-to-end test |

The multipliers and times are illustrative. Replace them with a defensible range and source. When an estimate crosses a gate, do not average the good and bad cases into one comfortable score. Report the probability or range if it can be supported, otherwise state that feasibility remains unresolved.

### 6.5 Robustness: choose an option that works across plausible cases

If being wrong is costly, prefer a robust option that remains acceptable across plausible conditions over an option that is best only under optimistic assumptions—provided the robust option’s additional cost is justified.

Robustness does not mean “always choose the safest” or “always choose the most flexible.” It means examining plausible scenarios and choosing deliberately:

- If peak load is higher than expected, does the option still pass?
- If the source contract is late, can delivery proceed in stages?
- If the platform price changes, does the business case remain acceptable?
- If the operating team cannot support the design, what is the fallback?
- If a mandatory target changes, which options become feasible or infeasible?

Possible responses include gathering more evidence, running a pilot, staging the rollout, defining a fallback, negotiating a dependency, or delaying an irreversible commitment. Make the cost of delay explicit: waiting for perfect evidence may also have a business cost.

### 6.6 Reversibility, lock-in, and long-term consequences

A decision is **reversible** when the organisation can change it at acceptable cost and risk. A decision is **hard to reverse** when migration, retraining, contract exit, data conversion, integration changes, or operational transition are costly or risky.

Assess:

- **Exit cost:** licences/termination, data extraction, migration engineering, parallel running, and decommissioning.
- **Lock-in:** proprietary interfaces, data formats, operational tools, or contracts that make switching harder.
- **Skills:** whether the organisation can recruit, train, and retain the people needed to operate it.
- **Upgrade path:** how components evolve and whether changes can be tested safely.
- **Vendor viability and dependency:** what happens if support, product direction, or commercial terms change.
- **Regulatory and policy change:** whether controls and evidence can adapt; do not invent specific legal obligations.
- **Migration and coexistence:** how old and new paths run together, reconcile records, and roll back.

When uncertainty is high and the decision is hard to reverse, consider a staged commitment, a time-boxed pilot, an exit test, portability requirements, or an architecture boundary that preserves options. A pilot is useful only if its workload, success criteria, decision deadline, and stop/go authority are defined.

### 6.7 Cost-benefit analysis and the cost of doing nothing

A credible cost-benefit analysis states benefits in measurable terms where possible and includes the cost of delay and the baseline.

Potential benefit measures include:

- Reduced manual handling time.
- Reduced delay before a business decision.
- Lower expected incident loss, if the estimate is supportable.
- Reduced reconciliation effort or duplicate processing.
- Faster delivery of an agreed capability.
- Avoided capacity or support costs.

Do not convert a speculative benefit into a precise financial figure without evidence. Show the model and uncertainty.

A practical TCO model is:

\[
TCO_n = build\_cost + \sum_{t=1}^{n}(run\_cost_t + support\_cost_t) + migration\_cost + exit\_cost
\]

Use this expanded form when migration is a separate cost category. If the estimate records build and migration together as a single combined input, do **not** add `migration_cost` again. Define the cost boundary of every row and include people, parallel running, support, migration, and exit where applicable without double-counting.

**Cost of doing nothing** may include continued manual work, missed business outcomes, technical debt, incident exposure, or the opportunity cost of delayed capability. It may also avoid near-term spend. Compare both sides; do not assume the baseline is either free or unacceptable.

### 6.8 Stakeholder disagreement and decision authority

Stakeholders may reasonably rank outcomes differently. Operations may favour simpler support; a fraud product owner may favour freshness; Finance may focus on whole-life cost; Security may require a control to be non-negotiable; a source-system owner may be unable to commit to a proposed interface.

Resolve disagreements in this order:

1. Separate mandatory constraints from preferences.
2. Trace each criterion to the requirement, risk, or principle it protects.
3. Ask the accountable owner to clarify business consequences and priority.
4. Record the evidence and the unresolved disagreement.
5. Use agreed weights only for tradeable criteria.
6. Escalate conflicts that require changing a mandatory target, accepting risk, or changing scope to the authorised decision-maker.
7. Record the decision, dissent where material, conditions, owner, and review trigger.

A scoring model does not transfer decision authority to a spreadsheet. The accountable decision-maker owns the outcome and must explicitly accept material residual risk within their authority.

### 6.9 Communicate to two audiences

**Technical reviewer version** should include:

- Decision scope and gate results.
- Options and comparable assumptions.
- Criteria, rating anchors, weights, evidence, and calculation.
- Sensitivity and uncertainty results.
- Operational consequences, dependencies, failure modes, and reversibility.
- Tests and actions required before implementation.

**Business sponsor version** should include:

- Business outcome and recommendation.
- Expected benefit and whole-life cost range.
- What the selected option gains and sacrifices.
- Main uncertainty and residual risk.
- Decisions or commitments needed from the sponsor.
- What would cause the recommendation to change.

Both versions must be consistent. The business version can be shorter, but it must not hide a material caveat found in the technical analysis.

### 6.10 Advanced exercise

Repeat the intermediate comparison using low/base/high ranges for at least two uncertain inputs. Run a sensitivity analysis on the two least certain inputs, then write:

1. A technical recommendation with criteria, evidence, feasibility, sensitivity, and residual risk.
2. A business recommendation with outcomes, cost, accepted trade-offs, and decisions required.
3. The condition under which the runner-up becomes preferable.
4. A reversibility or staged-commitment proposal if the evidence is insufficient for an irreversible decision.

**Answer guidance:** Recheck hard gates in every scenario. Identify which input drives a ranking change, show the threshold, and state whether it is plausible. If the preferred option changes often across plausible cases, the decision is fragile; gather evidence, revise the scope, or prefer a robust staged option. If the same option remains feasible and preferred across the plausible range, the recommendation is more robust—but still depends on the validity of the range and criteria.

**Ability to demonstrate:** the recommendation explains why it is preferred, the assumptions under which it is preferred, the trade-offs accepted, and the evidence or condition that would change it.

## 7. Industry-application exercises

Use the fictional **Northbridge Bank** decision set. The values below are placeholders for teaching. The actual project must use validated requirements, estimates, constraints, and decision authority.

### Exercise 7.1 — Establish decision criteria and prioritisation

Produce the architecture decision criteria and prioritisation method for the Northbridge decision set.

Your work must include:

- A decision statement and scope.
- A list of requirements, constraints, assumptions, dependencies, and risks that affect the decision.
- Criteria with unique IDs, definitions, source links, gate/scored classification, evidence required, owner, and priority.
- Hard gates with pass/fail evidence and a named approver.
- A rating scale and rationale for any weights.
- A record of criteria excluded from scoring because they do not discriminate, with justification.
- A process for resolving disputed weights or mandatory status.

**Answer guidance:** Each criterion should trace to a source requirement, constraint, risk, or approved principle. Do not label a preference as a gate without authority. Do not score a gate. If two criteria overlap, combine them or explain why both are needed.

### Exercise 7.2 — Compare alternatives and write the trade-off analysis

Choose one major Northbridge architecture decision. Compare at least three credible alternatives, including a baseline where appropriate.

Deliver:

1. A decision statement.
2. A feasibility/gate table.
3. A comparison matrix with evidence for each rating.
4. A whole-life cost comparison.
5. A narrative of gains, sacrifices, and residual risks for each serious candidate.
6. A recommendation that explains why the option best fits the agreed priorities.
7. The conditions under which the runner-up would be selected.

**Answer guidance:** An alternative that fails a mandatory gate must be eliminated or redesigned before scoring. If all alternatives fail, do not choose the least-bad score; revisit the requirement, scope, or solution space with the authorised stakeholders.

### Exercise 7.3 — Sensitivity analysis on the two least certain inputs

Identify the two least certain decision inputs, such as peak event rate, achievable freshness, support effort, or dependency lead time.

For each input:

- Record low/base/high values and source.
- Explain which criteria and gates it affects.
- Recalculate feasibility and scores.
- Identify any ranking reversal or gate failure.
- State the threshold at which the recommendation changes.
- Define the validation action, owner, due date, and decision consequence.

**Answer guidance:** Do not vary weights alone if the real uncertainty is performance or cost. Do not present arbitrary ranges as facts. If you cannot support numerical probabilities, use scenario ranges and state the evidence gap.

### Exercise 7.4 — Northbridge trade-off decision pack

Prepare a concise decision pack containing:

- **Decision statement:** question, scope, exclusions, deadline, decision-maker.
- **Decision criteria register:** source traceability, gate/scored classification, priority, evidence, and owner.
- **Alternative descriptions:** same scope, realistic implementation assumptions.
- **Gate results:** pass/fail/unverified, with evidence.
- **Comparison matrix:** raw evidence and ratings.
- **TCO and benefits:** build, run, people, migration, exit, cost of delay, and doing-nothing baseline.
- **Sensitivity analysis:** at least two uncertain inputs and any weight change justified by stakeholder priorities.
- **Recommendation:** preferred feasible option, runner-up, evidence, assumptions, and conditions.
- **Trade-offs:** what is gained, sacrificed, and accepted.
- **Residual risk and actions:** owner, due date, trigger, escalation path.
- **ADR hand-off:** the decision context, drivers, options, outcome, rationale, consequences, links, and review trigger for Topic 7.

All numerical values must be labelled as measured, contracted, estimated, or illustrative. The completed pack should be reviewable by someone who did not participate in the analysis.

## 8. Practical scenarios and case-based reasoning

### Scenario 8.1 — The cheapest option narrowly misses freshness

**Situation:** The lowest-cost option misses an approved freshness target by a small margin.

**Questions:**
1. Should the option be gated, scored, or should the target be negotiated?
2. Who can authorise a target change?
3. What evidence is needed before deciding?

**Reasoning:** First determine whether the target is formally mandatory. If it is a hard gate, the option is ineligible until redesigned or the authorised owner changes the requirement. A small miss is still a miss; weighted scoring cannot cancel it. If the target is a preference rather than a must-have, compare the business impact of the delay against cost and other criteria. Negotiation is a requirements/governance action, not a hidden adjustment to the scorecard.

Before recommending a change, quantify the effect on the decision or risk if possible, identify affected consumers and business windows, document the reason, and obtain approval from the right authority. Do not invent regulatory consequences or claim that a delay is harmless without evidence.

**Acceptable answer:** explicitly classifies the target, identifies decision authority, proposes evidence and a documented path, and does not treat the small miss as automatically acceptable.

### Scenario 8.2 — Two options score within 3%

**Situation:** Two feasible options have totals within 3% of one another. Treat “3%” as a scenario trigger for investigating a near-tie, not as a statistically meaningful percentage difference: a weighted total built from ordinal ratings is not a ratio-scale measurement. Compare the absolute score margin, criterion-level results, and uncertainty.

**Questions:**
1. Is the difference meaningful given the rating scale and evidence uncertainty?
2. Which criteria drive the difference?
3. What further evidence would discriminate between the options?

**Reasoning:** A small score difference is not proof of superiority. Inspect criterion-level differences, evidence quality, and uncertainty. Recheck for correlated criteria and arbitrary weights. Consider a targeted proof of concept, cost clarification, operational exercise, or a reversibility advantage. If no evidence meaningfully distinguishes the options, report a near-tie and use legitimate tie-breakers agreed in advance—such as lower lock-in, lower downside under uncertainty, or easier reversal—provided they trace to approved criteria.

**Acceptable answer:** avoids false precision, identifies evidence gaps, and explains whether further testing is worth its cost and delay.

### Scenario 8.3 — Preferred option depends on an uncommitted vendor

**Situation:** The highest-ranked option requires a vendor capability or service commitment that has not yet been contractually or operationally confirmed.

**Questions:**
1. Is the option feasible now?
2. How should the decision be structured?
3. What is the fallback if the commitment does not arrive?

**Reasoning:** Mark the dependency as unverified; do not treat a sales statement as a binding commitment. If the capability is a hard gate, the option remains ineligible until evidence is obtained. If conditional planning is appropriate, state the condition precedent, accountable owner, evidence required, due date, and expiry/review date. Define the fallback and what happens to delivery if the condition fails.

A conditional decision might say: “Proceed to a bounded pilot only after the vendor’s required capability and support terms are verified; do not approve production commitment until the gate is passed. If the commitment is not confirmed by the agreed date, reassess the runner-up and update the ADR.” The exact condition and date must be agreed by the project.

**Acceptable answer:** distinguishes a conditional next step from an unconditional production decision, names the dependency owner and evidence, and includes a fallback.

### Scenario 8.4 — All options fail a hard gate

**Situation:** Each candidate fails at least one mandatory requirement.

**Reasoning:** Do not rank the least-bad option as if it were compliant. Check whether the requirement is correctly understood, whether the scope can be changed, whether a candidate can be redesigned, or whether an additional alternative is needed. Escalate a proposed requirement change to the authorised owner. Record the consequence of delay and do not proceed with an unapproved exception.

### Scenario 8.5 — A stakeholder wants weights changed after seeing the winner

**Situation:** A stakeholder proposes changing the weights only after seeing that their preferred option lost.

**Reasoning:** Ask for the underlying business rationale. If the original weights misrepresented a genuine priority, return to the accountable stakeholders, document the rationale, revise the criteria/weights transparently, and rerun the analysis for all options. If no substantive reason exists, do not change weights to force a result. Preserve both versions and explain the effect.

### Scenario 8.6 — A new estimate changes the preferred option

**Situation:** Updated source telemetry raises the peak event-rate estimate substantially.

**Reasoning:** Update the source estimate first, then reassess throughput, cost, freshness, gates, risk, criteria ratings, and ranking. Do not patch the ADR or score alone. Trace the changed estimate through the decision artefacts and determine whether the prior recommendation remains valid.

## 9. Expected outputs and deliverables

Complete and retain the following artefacts. The templates are illustrative working formats; use the project’s established naming and governance where defined.

### 9.1 Decision statement template

```text
Decision ID:
Decision question:
Business outcome:
Scope / included:
Out of scope:
Deadline:
Accountable decision-maker:
Required reviewers / risk acceptors:
Requirements and constraints referenced:
Alternatives to evaluate:
Hard gates:
Scored criteria:
Evidence gaps:
Next review date / trigger:
```

### 9.2 Decision-criteria register

| ID | Criterion and definition | Source requirement / constraint / principle | Gate or scored? | Priority / weight | Evidence required | Rating anchors | Owner | Status / notes |
|---|---|---|---|---|---|---|---|---|
| DC-01 | p95 freshness from source commit to case-tool visibility | Link to approved service target | Gate if formally mandatory; otherwise scored | Set by authority | Representative end-to-end test with timestamps | Pass/fail for gate; defined scale if scored | Product/platform owner | Illustrative row |
| DC-02 | Three-year TCO including build/run/people/migration/exit | Business case / budget boundary | Scored unless an approved budget is a hard cap | Agree before scoring | Finance-reviewed cost model and range | Criterion-specific bands | Finance / delivery lead | Illustrative row |
| DC-03 | Operability and support readiness | Operational requirements / risk register | Gate only if a mandatory support requirement exists; otherwise scored | Agree before scoring | Runbook, on-call, recovery and skills review | Defined operational anchors | Operations lead | Illustrative row |
| DC-04 | Peak throughput and growth headroom | Data-rate estimate and capacity target | Gate if approved capacity threshold is mandatory; otherwise scored | Agree before scoring | Representative load test and forecast | Defined capacity bands | Data/platform engineer | Illustrative row |

Do not copy the example weights into a real decision without stakeholder agreement. The example leaves weights open because they must follow the actual priorities and scope.

### 9.3 Alternative and gate register

| Option ID | Description at comparable scope | Key dependencies | Gate | Evidence | Result | Remediation / decision |
|---|---|---|---|---|---|---|
| ALT-A | Baseline / minimal change | Existing source interface and current operating model | Approved freshness target | Measured end-to-end timing | Pass / fail / unverified | Redesign, formally renegotiate target, or eliminate |
| ALT-B | Managed micro-batch | Source query/API capacity, schedule and service limits | Security/access requirements | Security review and representative test | Pass / fail / unverified | Action and owner |
| ALT-C | Event-driven | Stable event contract, event channel, support capability | Security and performance requirements | Contract evidence, load test, failure/replay test | Pass / fail / unverified | Action and owner |

Use actual alternatives in the project. “Pass,” “fail,” and “unverified” are distinct states; unverified is not a pass.

### 9.4 Comparison matrix

| Criterion | Weight / gate | Option A: evidence + rating | Option B: evidence + rating | Option C: evidence + rating | Confidence / caveat |
|---|---|---|---|---|---|
| Gate: approved security/access | Pass/fail/unverified | Evidence link | Evidence link | Evidence link | Reviewer and date |
| Gate: mandatory freshness | Pass/fail/unverified | Measurement and scope | Measurement and scope | Measurement and scope | Test conditions |
| Cost | Weight and defined scale | TCO + rating | TCO + rating | TCO + rating | Estimate range |
| Operability | Weight and defined scale | Evidence + rating | Evidence + rating | Evidence + rating | Qualitative or measured |
| Scalability | Weight and defined scale | Load evidence + rating | Load evidence + rating | Load evidence + rating | Growth assumptions |

Every scored cell should contain or link to raw evidence and explain how the rating was derived. A score-only matrix is incomplete.

### 9.5 Sensitivity analysis register

| Input / weight | Base value | Low case | High case | Affected gates/criteria | Ranking or feasibility change? | Threshold / finding | Validation action, owner, due date |
|---|---|---|---|---|---|---|---|
| Peak event rate | Source-backed estimate | Plausible lower case | Plausible upper case | Capacity, freshness, cost | Record result | Threshold where gate fails or ranking changes | Source owner / date |
| Support effort | Estimate | Lower effort | Higher effort | TCO, operability | Record result | Break-even or ranking threshold | Operations lead / date |
| Freshness weight | Stakeholder-approved base | Agreed lower priority | Agreed higher priority | Scored freshness | Recompute all eligible options | Point of reversal | Decision owner / date |

### 9.6 Recommendation template

```text
Recommendation:
Preferred feasible option:
Runner-up:
Decision scope and exclusions:
Hard-gate results:
Business outcome expected:
Evidence that most strongly supports the recommendation:
Scoring method and limitations:
Whole-life cost / benefit range:
Accepted trade-offs (gains and sacrifices):
Key assumptions and dependencies:
Residual risks and owners:
Sensitivity results:
Conditions that would reverse the recommendation:
Fallback / staged commitment:
Decision authority and approvals:
ADR to create/update:
Review trigger and date:
```

### 9.7 Required Topic 6 deliverables

- Decision statement with scope and criteria.
- Comparison matrix with evidence.
- Sensitivity analysis.
- Recommendation for technical and business audiences.
- Answers to Topic 6 practice questions.
- For the Northbridge industry exercise: criteria and prioritisation method, major-decision trade-off analysis, and sensitivity analysis for the two least certain inputs.

The module roadmap names `practice-questions.md` in the project tree, but the file's actual question text must be inspected in the working repository. Do not claim to have answered unseen questions. Where that file is unavailable or empty, complete the prescribed scenarios and exercises in this lesson and record the source gap; obtain the actual practice questions before marking that specific deliverable complete.

## 10. Common mistakes and misconceptions

1. **Constructing straw-man alternatives.** Making the favourite polished and competitors deliberately weak invalidates the comparison. Define options at comparable scope and give each a credible implementation.
2. **Treating scores as precise measurements.** A weighted total is a structured judgement based on inputs, not objective truth. Show raw evidence, uncertainty, and criterion-level results.
3. **Choosing weights after seeing the totals.** Agree priorities before scoring. If priorities genuinely change, record why and rerun every option.
4. **Ignoring people, migration, and exit costs.** Licence or cloud spend alone is not TCO. Include implementation, operations, support, skills, migration, parallel running, and exit costs without double-counting.
5. **Ignoring reversibility.** A high-scoring option may create unacceptable lock-in. Estimate exit cost and consider staged commitment.
6. **Omitting what the chosen option gives up.** State gains, sacrifices, residual risks, and who accepts them.
7. **Scoring an option that fails a hard gate.** A gate must be checked first; a high score cannot compensate for a mandatory failure.
8. **Confusing an assumption with evidence.** Label estimates and claims; assign owners and validation actions.
9. **Using a single point estimate when uncertainty matters.** Show plausible ranges and identify the ranking/gate thresholds.
10. **Double-counting correlated criteria.** Avoid separately weighting two labels for the same underlying benefit without a clear reason.
11. **Using inconsistent boundaries.** Compare the same workload, time horizon, data boundary, measurement window, and cost scope.
12. **Treating an unverified option as feasible.** “Not tested” or “vendor says so” is not a pass.
13. **Letting the spreadsheet make the decision.** The accountable decision-maker owns the choice and risk acceptance.
14. **Hiding disagreements.** Record material dissent, the rationale, the authority that resolved it, and any accepted consequence.
15. **Updating only the ADR or scorecard.** When a source requirement, estimate, or assumption changes, update the source artefact and follow traceability links forward.
16. **Inventing legal requirements.** Refer to actual applicable policies and obtain qualified review. This lesson provides no jurisdiction-specific legal conclusion.
17. **Treating “do nothing” as free.** Baseline operations, risk, manual effort, and opportunity cost still exist.
18. **Confusing conditional approval with production approval.** State condition precedents, owners, dates, fallback, and what remains prohibited until gates pass.

## 11. Mastery criteria

You have mastered this topic when you can independently:

- Frame a bounded architecture decision with scope, exclusions, deadline, and decision authority.
- Derive every criterion from a requirement, constraint, risk, or approved principle.
- Separate hard gates from scored preferences and justify the classification.
- Generate at least three credible alternatives, including an appropriate baseline.
- Assess feasibility before scoring and refuse to rank a gate-failing option as eligible.
- Define a rating scale, explain any weights, and show that weights sum to 1.
- Trace every rating to evidence and explain the evidence’s limitations.
- Compare whole-life costs without omitting people, migration, support, or exit costs.
- Explain the gains, sacrifices, and residual risks of each serious candidate.
- Run sensitivity analysis on both priorities and uncertain inputs; identify a ranking reversal or explain why none occurs within the tested range.
- Assess reversibility, lock-in, and long-term operational consequences.
- Write a recommendation for technical and business audiences with assumptions, accepted trade-offs, and reversal conditions.
- Trace the recommendation into the Topic 7 ADR and identify which upstream artefact must change if evidence changes.

### Self-review questions

Before submitting, answer these questions in your own words:

1. Why is an option that misses a hard constraint not an eligible scored alternative?
2. Why include the baseline even if it may be infeasible?
3. Which criteria genuinely discriminate between your options, and which are identical?
4. Where is the evidence weakest, and what action will improve it?
5. Which two inputs are least certain? What happens to feasibility and ranking at their plausible limits?
6. Under what assumptions is the preferred option best?
7. What would make you choose the runner-up?
8. What are you explicitly accepting, and who has authority to accept it?
9. What evidence, threshold, or stakeholder priority would reverse the decision?
10. What source artefact and ADR links must be updated if an assumption is invalidated?

## 12. Completion gate

Do not mark Topic 6 complete until all checks pass:

- [ ] Every criterion traces to a requirement, constraint, risk, or approved architecture principle.
- [ ] The decision statement defines scope, exclusions, deadline, and decision authority.
- [ ] At least three credible alternatives are described fairly, including a baseline where appropriate.
- [ ] Hard gates are explicit, and every option’s gate result is supported by evidence or marked unverified.
- [ ] Infeasible options are not scored as eligible.
- [ ] The comparison matrix contains evidence for every rating.
- [ ] The rating scale is defined, weights sum to 1 where weighted scoring is used, and calculation has been independently checked.
- [ ] Weighted-scoring limitations, possible double-counting, and score uncertainty are discussed.
- [ ] Cost analysis includes build, run, support, people, migration, and exit costs, with assumptions visible.
- [ ] Sensitivity analysis is completed, including at least two uncertain inputs for the Northbridge industry exercise; ranking reversals and gate changes are recorded.
- [ ] The recommendation states assumptions, accepted trade-offs, residual risks, and reversal conditions.
- [ ] A technical recommendation and a business-facing recommendation are consistent.
- [ ] The Topic 6 practice questions have been answered and corrected using the actual source questions; if the source file is unavailable or empty, that limitation remains explicitly open.
- [ ] The output is ready to feed Topic 7’s ADR: context, drivers, options, outcome, rationale, consequences, evidence links, and review trigger.

**Completion standard:** the preferred option is justified by traceable requirements, explicit gates, credible alternatives, evidence-backed comparisons, and sensitivity analysis. The recommendation states not only why it is preferred, but also what is sacrificed, what remains uncertain, who accepts the residual risk, and what would cause the decision to change.
