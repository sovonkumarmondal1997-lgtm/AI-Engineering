# Project 03 — Reference Architecture Pattern Comparison

> **Stage:** Stage 2D — Data Architecture
> **Module:** 2D.3 — Data Architecture Patterns and Reference Architectures
> **Project type:** Architecture evaluation (patterns compared against requirements; no implementation)
> **Roadmap source:** `roadmap-Data-Architecture-Patterns-and-Reference-Architectures.md`, Section 7
> **Project file:** `Projects/03-reference-architecture-pattern-comparison.md`

---

## 0. Document control

| Item | Value |
| --- | --- |
| Document | Project specification and worked reference, deliverables D1–D12 |
| Version | 1.1 (post-audit) |
| Date | 2026-10-21 |
| Status | Complete as a project specification and worked reference. **Every Northbridge value is illustrative. No stakeholder has reviewed or approved anything in Section 6; every decision record is `Proposed` and every decision is `Conditional`.** |
| Audience | Learner running the project; independent reviewer auditing it |
| Scenario | *Northbridge Bank*, a fictional mid-sized retail and business bank (roadmap Section 7.2) |
| Evidence rule | Every row carries an evidence label (Section 4.3); estimates carry an estimate label |
| Companion tool | Consistency checker, Appendix B (`check_pattern_comparison.py`) |

**Change log**

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-10-21 | First complete design |
| 1.1 | 2026-10-21 | Post-audit: corrected the sensitivity-ranking reading (daily volume and replay throughput have near-equal swings); ordered the sensitivity cases by decision; added organisational prerequisites to every option description (a roadmap gate item); corrected a mitigation reference; hardened the checker (three-digit IDs, stop on structural errors, clear failure on malformed tables, completeness check for options that become eligible under sensitivity, n/a ratings outside bands); confirmed the embedded checker equals the tested one |

**Reading order.** Sections 1–5 explain the project and how to run it. Section 6 is
a complete worked reference (D1–D12). Section 7 is the quality gate. Section 8 holds
templates for a real organisation. Sections 9–11 cover pitfalls, hand-off and
self-assessment. Appendix B is the checker.

---

## 1. Project overview

### 1.1 What this project is

A **reference architecture pattern comparison** is an architecture evaluation. It does
not list the strengths and weaknesses of fashionable patterns. It answers a decision
question: *for this organisation, with these workloads, constraints and capabilities,
which patterns should be used, which should be refused, and how should the chosen ones
fit together?*

The core idea of the module is that patterns operate on **different axes** and must not
be compared as if they answered the same question. "Lambda versus data mesh" is not a
decision; "how should we process card events?" and "who should own and operate data?"
are two decisions that happen to interact. This project therefore works in two layers:

```text
Layer 1 — one decision per axis (options compared against gates, then weighted criteria)
   DEC-01 operating model   DEC-02 analytical storage   DEC-03 processing
   DEC-04 metadata control  DEC-05 fraud interaction    DEC-06 analytical sharing
Layer 2 — one combination decision (axis choices assembled and tested end to end)
   DEC-07 combination: compatibility · end-to-end freshness · availability · cost · delivery
Output  — recommendation, parsimony test, rejected alternatives, revisit triggers,
          reference architecture view
```

### 1.2 Why organisations need it

| Situation | What goes wrong without it | What the comparison provides |
| --- | --- | --- |
| A vendor proposes "lakehouse + fabric + mesh" | Every fashionable pattern is bought; none is tied to a requirement | A parsimony test: each pattern names the requirement it serves, or it is removed |
| A central team has a long backlog | The bank reorganises into domain ownership by announcement | A queue calculation and a readiness assessment before any operating-model change |
| Best-of-each-axis choices are combined | The parts do not compose; the end-to-end target is missed | A combination decision with end-to-end gates |
| A decision is challenged later | The reasoning and the rejected options are lost | A decision record with rejected alternatives and observable revisit triggers |

### 1.3 Business problem and decisions

**Problem (roadmap).** The bank needs consistent, governed, timely data for regulatory
reporting, fraud detection, risk analytics and customer analytics, while reducing the
central team's bottleneck and improving accountability and discoverability.

| Decision | Pattern axis | Question |
| --- | --- | --- |
| DEC-01 | Operating model and ownership | Who owns, governs and operates data? |
| DEC-02 | Analytical storage | Where, and in what form, do analytical data live? |
| DEC-03 | Processing | How are card events processed and history rebuilt? |
| DEC-04 | Metadata and control | How are data found, related and governed? |
| DEC-05 | Interaction (fraud path) | How do card events reach the fraud consumers? |
| DEC-06 | Sharing (analytics) | How do domains share analytical data? |
| DEC-07 | Combination | Which assembled set of patterns is justified? |

### 1.4 What this project is not

| It is not | Because |
| --- | --- |
| A product selection | Options are pattern categories; no product is evaluated |
| A schema, storage or integration design | Those belong to modules 2D.4–2D.6 |
| A platform or cloud design | Those belong to modules 2D.7–2D.9 |
| A migration plan | Plans follow accepted decisions |
| A source of facts about a real bank | Every Northbridge value is an illustrative assumption |

### 1.5 Success criteria

The project succeeds when an independent reviewer can (1) recompute the figures, (2)
trace three recommendation elements back to requirements and three requirements forward to
decisions, (3) confirm that no option that failed a gate was rescued by a score, (4)
confirm that every pattern in the recommendation names a requirement, and (5) agree that
the conclusion follows from the evidence (roadmap Section 7.7).

---

## 2. How to use this file

| | Mode A — Worked reference | Mode B — Real or realistic organisation |
| --- | --- | --- |
| Purpose | Study a complete example; critique it | Produce your own comparison |
| Facts | Roadmap scenario only; all numbers illustrative | Your stakeholders, documents and measurements |
| What you do | Read Section 6; run the checker; challenge the example | Follow Section 5; use Section 8; produce your own D1–D12 |
| Output | Understanding and a critique list | A reviewed D1–D12 and a met completion gate |

**Rules in both modes**

1. **Separate the axes.** Never compare patterns from different axes as alternatives for the same decision.
2. **Include a minimal-change baseline** for every decision.
3. **A gate failure removes an option; it is not a low score.** Record the reason.
4. **Fix criteria and weights before looking at totals,** and record the week.
5. **Rate from evidence.** Mark unknowns as unknown; never convert a missing measurement into a middle score.
6. **Describe every candidate at the same level of abstraction.** Label the final view as a reference architecture, not a blueprint.
7. **No pattern or product name inside a requirement.**
8. **Stop at the reference architecture.** Do not add implementation tasks that belong to later modules.

> **Honesty note for Mode A.** The roadmap supplies the scenario and a handful of figures.
> Everything else in Section 6 — queue figures, throughputs, costs, availabilities,
> ratings — was invented for the exercise and is labelled `Illustrative assumption`. The
> worked reference demonstrates the method and the traceability; it recommends nothing for
> any real bank. The module's own worked example (Topic 7) reaches a compatible
> staged-hybrid conclusion by a different route (scenario-level candidates A–F); this
> project derives its result axis by axis and tests it end to end.

---

## 3. Concepts applied

| Concept (lesson) | Where it is applied |
| --- | --- |
| Centralized, federated and domain-oriented models; responsibility and failure modes ([Topic 1](../01-centralized-federated-and-domain-oriented-architectures.md)) | DEC-01; OPT-01 to OPT-03; backlog queue model (EST-01 to EST-06); D7 responsibilities |
| Warehouse, lake and lakehouse; workload fit; data swamp risk ([Topic 2](../02-data-warehouse-data-lake-and-lakehouse-patterns.md)) | DEC-02; OPT-05 to OPT-08; workload map WL-01 to WL-05 |
| Lambda, Kappa, micro-batch; replay time and recovery ([Topic 3](../03-lambda-and-kappa-architectures.md)) | DEC-03; OPT-09 to OPT-12; replay-time estimates EST-09 and EST-10 |
| Data mesh principles, data products, readiness scoring and pilot stop criteria ([Topic 4](../04-data-mesh-principles-and-domain-data-products.md)) | DEC-01 (OPT-03, OPT-04); readiness table RD; pilot in Section 6.7 |
| Data fabric, metadata-driven control, minimum metadata ([Topic 5](../05-data-fabric-and-metadata-driven-architecture.md)) | DEC-04; OPT-13 to OPT-16; controls CTL |
| Event-driven and data-sharing patterns, contracts, delivery semantics ([Topic 6](../06-event-driven-and-data-sharing-patterns.md)) | DEC-05, DEC-06; OPT-17 to OPT-24 |
| Selecting and combining patterns; gates, sensitivity, parsimony, ADR, reference view ([Topic 7](../07-selecting-and-combining-architecture-patterns.md)) | DEC-07; Sections 6.5 to 6.11 |

**Roadmap project parts**

| Project part | Topics | Steps | Deliverables |
| --- | --- | --- | --- |
| Operating model and ownership options | 1, 4 | 5–12 | D3–D7 |
| Analytical storage options | 2 | 5–12 | D3–D7 |
| Batch/stream processing options | 3 | 5–12 | D3–D7 |
| Metadata, discovery and control | 5 | 5–12 | D3–D7 |
| Cross-system interaction | 6 | 5–12 | D3–D7 |
| Selection, combination, recommendation | 7 | 13–19 | D8–D12 |

**Carry-in from earlier modules.** The requirements, constraints and decision method come from
Module 2D.2 ([Project 02](../../02-Requirements-Constraints-and-Architecture-Decisions/Projects/02-requirements-and-architecture-decision-pack.md)),
and the current-state baseline from Module 2D.1
([Project 01](../../01-Data-Architecture-Foundations-and-Principles/Projects/01-current-state-data-architecture-inventory.md)).
Those projects use their own illustrative models; this project re-derives the figures it needs
and notes where a figure is reused (for example 4.6 GB per day of card-event volume, 4× peak
factor, 1.5 safety factor).

> **Repository note.** The roadmap and the module's file tree refer to a
> `practice-questions.md`. At the time of writing that file does not exist in this
> module's directory, so this project could not be cross-checked against its questions or
> rubric. It was checked against the roadmap's project section and the seven topic files.

---

## 4. Project governance and conventions

### 4.1 Roles and decision rights (RACI)

`R` responsible, `A` accountable (exactly one per row), `C` consulted, `I` informed.

| Activity or decision | Sponsor (STK-01) | Lead architect (STK-15) | Business owners (STK-02 to STK-06, STK-08) | Control functions (STK-09, STK-10) | Platform and central team (STK-13, STK-14) | Internal Audit (STK-11) |
| --- | --- | --- | --- | --- | --- | --- |
| Approve scope and exclusions | A | R | C | C | C | I |
| Confirm requirements and targets | C | R | A | C | C | I |
| Approve gates (binding constraints) | C | R | C | A | C | I |
| Approve criteria and weights before scoring | A | R | C | C | C | I |
| Validate estimates and readiness scores | I | R | C | C | A | I |
| Decide DEC-01 to DEC-07 | A | R | C | C | C | I |
| Accept a residual risk | A | C | C | C | C | I |
| Independent review of evidence against conclusions | I | C | I | I | I | A |

The architect recommends and records; the sponsor decides; control functions own the gates
that stem from their authority. The architect never approves their own exception.

### 4.2 Scales, rules and scoring

**Gates and eligibility.** A gate is a pass/fail test applied before scoring. A gate result is
`Pass`, `Fail` or `Pending` (not yet proven). An option is **eligible** if it has no `Fail`; a
`Pending` gate becomes a condition on the decision record. Only eligible options are scored.

**Ratings.** Ratings use a 1–5 ordinal scale (`1` poor, `3` acceptable, `5` very strong).
Numeric criteria are rated through bands (Section 6.5); the input is rounded half-up to a whole
number first. Judgement criteria use written anchors. Weights sum to 1 per decision and are
frozen before scoring: `Score(option) = Σ weight × rating`.

**Close-call rule.** A score difference below 0.15 (3% of the 5-point scale) is not a real
preference; the decision stays conditional and the missing evidence is named.

**Decision state.** `Final` only when no gate is `Pending` for the selected option and no
blocking unknown remains; otherwise `Conditional`. Decision-record status uses
`Proposed`, `Accepted`, `Deprecated` or `Superseded`; "Conditional" is a state, not a status.

**Risk scoring** (Module 2D.2 method; illustrative). Probability and impact use 1–5;
**exposure = probability × impact**. Bands: 1–4 lower, 5–9 moderate, 10–14 high, 15–25
very high. High and very high exposures need an owner, response, trigger and escalation.

**Weeks.** Weeks 1–8 are the pack; weeks 9 and later are post-pack follow-up.

### 4.3 Evidence labels

| Label | Meaning |
| --- | --- |
| Verified fact | Supported by inspected evidence or a confirmed source |
| Stakeholder statement | What a person said; not independently verified |
| Illustrative assumption | A value invented for learning or planning |
| Inference | A reasoned interpretation, open to challenge |
| Open question | A matter not yet resolved |

Estimate labels for worksheet inputs: `measured`, `sampled`, `stated`, `estimated`, `guessed`.

### 4.4 ID conventions

IDs are numbered (two digits; three for the longest tables), stable and never reused. Cross-references use IDs only, which makes the
traceability machine-checkable.

| Prefix | Object | Prefix | Object |
| --- | --- | --- | --- |
| STK | Stakeholder | OD | Conceptual description of an option |
| WL | Workload | TB | Timing-budget stage |
| REQ | Requirement | TCO | Cost components of an option |
| TGT | Service target | DL | Delivery estimate |
| CON, ASM, DEP, RSK, UNK | Constraint, assumption, dependency, risk, unknown | AV | Component availability |
| INP, EST, TN | Estimate input, computed estimate, sensitivity ranking | RD | Readiness dimension |
| DEC | Decision | GT, GR | Gate, gate result |
| OPT | Option (pattern) or combination | CRIT, AN, JA | Criterion, numeric band, judgement anchor |
| OI, SC, SEN | Option input, score, sensitivity case | FND, LIM | Finding, limitation or failure mode |
| PR, PT | Pattern role, parsimony test | ELM, CTL | View element, control |
| DR, ADR, TRG | Decision record row, record index, revisit trigger | TR, VL | Traceability row, validation entry |

### 4.5 Confidentiality and handling

Record roles, not named individuals. Do not copy customer records, credentials or connection
details into the pack. Mark the pack with the organisation's classification and record the
version and date on every artefact.

### 4.6 Suggested workspace layout (Mode B, optional)

```text
northbridge-pattern-comparison/             # replace with the organisation name
├── 00-scope/            d1-scope.md, stakeholders-and-workloads.md
├── 01-requirements/     d2-requirements-and-constraints.md, estimates.md
├── 02-candidates/       d3-pattern-inventory.md, d4-conceptual-descriptions.md
├── 03-evaluation/       d5-comparison-matrix.md, d6-tradeoffs.md, d7-org-and-governance.md, d8-register.md
├── 04-decision/         d9-recommendation.md, d10-reference-view.md, d11-decision-records/
├── 05-trace-and-review/ traceability.md, review-notes.md, validation-log.md
├── 06-summary/          d12-summary.md
└── tools/               check_pattern_comparison.py (adapt header names)
```

Rationale: candidates, evaluation, decision and review are kept in separate layers so each can be
reviewed and versioned independently. Keep one source of truth per number.

---

## 5. Execution plan

### 5.1 Timeline and effort (planning estimate, mid-sized organisation)

| Week | Steps | Main outcome | Effort (person-days, indicative) |
| --- | --- | --- | --- |
| 1 | 1, 2, 3 | Scope; stakeholders and consumers; measurable requirements | 5–7 |
| 2 | 4, 5 | Constraints and risks; decision list by axis | 4–6 |
| 3 | 6, 7 | Candidate inventory; conceptual descriptions | 5–7 |
| 4 | 8, 9 | Requirement mapping; **criteria and weights frozen** | 5–6 |
| 5 | 10, 11, 12 | Organisational, governance and quality assessments; scoring | 6–8 |
| 6 | 13, 14 | Failure modes; combination decision and parsimony test | 5–6 |
| 7 | 15, 16, 17 | Recommendation, rejected alternatives, triggers, reference view | 4–6 |
| 8 | 18, 19 | Traceability review; final summary and challenge round | 4–5 |

Total indicative effort: **38–51 person-days**, plus about one day per interviewed stakeholder group.
These are planning figures, not measured results.

### 5.2 Definitions of ready and done

| | Criteria |
| --- | --- |
| **Ready** | Sponsor named; decision boundaries agreed; access to stakeholders, current-state documents and source owners; the Module 2D.2 method available |
| **Done** | Completion gate (Section 7.5) fully met; D1–D12 dated; independent reviewer agrees the evidence supports the conclusions |

### 5.3 The nineteen steps

Each step lists purpose, inputs, actions, the questions to answer, outputs and validation, with
pitfalls and the lessons it draws on.

#### Step 1 — Define the problem and assessment scope

- **Purpose:** fix what is being decided and what is not.
- **Inputs:** scenario, sponsor goals.
- **Actions:** write the problem statement, objectives, in-scope and out-of-scope lists, the labelled assumptions; state that the project stops at the reference architecture.
- **Questions:** What is being decided? What is deliberately excluded?
- **Output:** D1.
- **Validation:** the sponsor-role reviewer confirms scope; exclusions are as firm as inclusions.
- **Pitfalls:** scope phrased as a technology; no exclusions.
- **Draws on:** Topic 7 (4.1, 4.2).

#### Step 2 — Identify stakeholders, consumers and outcomes

- **Purpose:** know who decides, who consumes and what outcome each needs.
- **Inputs:** scenario, organisation context.
- **Actions:** build a stakeholder register with decision rights; map each workload to a consumer and an outcome.
- **Questions:** Who decides? Who consumes? What outcome matters?
- **Output:** stakeholder register and workload table (D2 part).
- **Validation:** each workload has a consumer and an outcome; control functions are present.
- **Pitfalls:** omitting compliance, security or internal audit.
- **Draws on:** Topic 1, Topic 7.

#### Step 3 — Gather functional and non-functional requirements

- **Purpose:** state measurable, sourced requirements.
- **Inputs:** Steps 1–2; the Module 2D.2 method.
- **Actions:** write each requirement in the pattern *[capability] shall [behaviour] for [scope], measured by [metric]*; set targets; flag architecturally significant ones.
- **Questions:** Which requirements are architecturally significant?
- **Output:** requirements and targets (D2 part).
- **Validation:** each is testable and sourced; no requirement names a pattern or product.
- **Pitfalls:** "real-time"; embedding a solution.
- **Draws on:** Module 2D.2; Topic 7 (4.3).

#### Step 4 — Identify constraints, assumptions, dependencies, risks and unknowns

- **Purpose:** bound the problem.
- **Inputs:** Steps 1–3.
- **Actions:** classify each item with the Module 2D.2 tests; score risks; assign owners; give high-impact assumptions a validation method and week.
- **Questions:** Which constraints eliminate options?
- **Output:** register (D2 part).
- **Validation:** no unclassified or ownerless item.
- **Pitfalls:** a preference listed as a constraint.
- **Draws on:** Module 2D.2 Topic 5; Topic 7 (5.1).

#### Step 5 — Determine the architecture decisions required

- **Purpose:** separate the decisions by axis and note their coupling.
- **Inputs:** Steps 3–4.
- **Actions:** list decisions by axis (operating model, storage, processing, metadata, interaction, sharing); mark coupled decisions; add a combination decision.
- **Questions:** Which decisions are independent, which coupled?
- **Output:** decision list (D3 part).
- **Validation:** every architecturally significant requirement links to a decision.
- **Pitfalls:** comparing patterns from different axes as alternatives.
- **Draws on:** Topic 7 (4.5).

#### Step 6 — Select candidate patterns

- **Purpose:** shortlist viable options per axis, always with a baseline.
- **Inputs:** Step 5; Topics 1–6.
- **Actions:** list at least three options per decision including a minimal-change baseline; record why each is a candidate; list combinations for the combination decision.
- **Questions:** Is each candidate viable for the problem?
- **Output:** candidate inventory (D3).
- **Validation:** each candidate has a reason; non-viable ones are removed with a cause.
- **Pitfalls:** a straw-man baseline; a vendor bundle disguised as an option.
- **Draws on:** Topic 7 (5.3, 5.4).

#### Step 7 — Describe each candidate's conceptual architecture

- **Purpose:** make candidates comparable.
- **Inputs:** Step 6.
- **Actions:** describe components and responsibilities, data flow, ownership and operating model, and how the candidate fails at 3 a.m., at one level of abstraction.
- **Questions:** What does each part do and who runs it?
- **Output:** candidate descriptions (D4).
- **Validation:** consistent level of detail across candidates.
- **Pitfalls:** one candidate described as a design and another as a slogan.
- **Draws on:** Topics 1–6 pattern cards.

#### Step 8 — Map candidates to requirements and constraints

- **Purpose:** show fit and gaps.
- **Inputs:** Steps 3, 4, 7.
- **Actions:** define hard gates from requirements and constraints; evaluate every gate for every candidate with evidence.
- **Questions:** Which requirements does each satisfy, fail or leave open?
- **Output:** gate results (D5 part).
- **Validation:** gate failures are flagged and explained.
- **Pitfalls:** treating missing evidence as a pass or as a failure.
- **Draws on:** Topic 7 (5.1, 5.5).

#### Step 9 — Compare using explicit criteria

- **Purpose:** make the comparison fair before looking at totals.
- **Inputs:** Step 8; the comparison criteria in the roadmap.
- **Actions:** derive criteria and weights; define bands and anchors; **freeze them and record the week**; rate eligible options from evidence; compute scores and verify the arithmetic.
- **Questions:** Where is the evidence weakest?
- **Output:** comparison matrix (D5).
- **Validation:** criteria are fixed before scoring; ratings cite evidence; ineligible options carry no score.
- **Pitfalls:** tuning weights after seeing the winner.
- **Draws on:** Topic 7 (5.2, 5.6, 5.7, 5.8).

#### Step 10 — Evaluate organisation and operating-model implications

- **Purpose:** test whether the organisation can run the candidate.
- **Inputs:** Steps 7, 9; Topics 1 and 4.
- **Actions:** score readiness by dimension with evidence; compare prerequisites with the current state; assess roles, funding and decision rights.
- **Questions:** What must the organisation become?
- **Output:** organisational assessment (D7 part).
- **Validation:** prerequisites compared with the current state.
- **Pitfalls:** inferring readiness from a successful prototype.
- **Draws on:** Topic 4 (6.1, 6.2, 6.7), Topic 7 (5.11).

#### Step 11 — Evaluate governance, security, interoperability and ownership

- **Purpose:** show that accountability can be evidenced.
- **Inputs:** Steps 3, 9.
- **Actions:** map each regulatory or accountability need to a control, an owner and the evidence it produces.
- **Questions:** Can accountability be evidenced?
- **Output:** governance assessment (D7 part).
- **Validation:** each regulatory need has a control.
- **Pitfalls:** assuming a pattern provides compliance by itself.
- **Draws on:** Topics 1, 4, 5, 6.

#### Step 12 — Evaluate reliability, performance, scalability, complexity and cost

- **Purpose:** quantify what each candidate costs to run and recover.
- **Inputs:** Module 2D.2 estimates.
- **Actions:** compute queue, replay-time, timing-budget and availability figures with units and formulas; run sensitivity on the two least certain inputs and on the weights.
- **Questions:** What does it cost to run and recover? What changes the ranking?
- **Output:** quality-attribute assessment and trade-off analysis (D5, D6).
- **Validation:** numbers carry units and are labelled illustrative.
- **Pitfalls:** treating a burst result as sustained capacity.
- **Draws on:** Topics 2, 3, 6, 7 (6.1–6.3).

#### Step 13 — Identify failure modes, limitations and uncertainties

- **Purpose:** state honestly how each candidate fails.
- **Inputs:** Steps 9–12.
- **Actions:** list findings; write at least one "how this fails at 3 a.m." per candidate; log limitations with mitigations and owners.
- **Questions:** How does each candidate fail?
- **Output:** risk and limitation register (D8).
- **Validation:** each item links to a candidate and a finding.
- **Pitfalls:** listing generic risks that cite no finding.
- **Draws on:** Topics 1–6.

#### Step 14 — Decide single pattern or combination

- **Purpose:** assemble the axis choices and test them together.
- **Inputs:** Steps 9–13.
- **Actions:** define combinations; apply compatibility, end-to-end freshness, availability, cost and delivery gates; score eligible combinations; run the parsimony test for every pattern.
- **Questions:** What requirement does each pattern serve?
- **Output:** combination decision (D9 part).
- **Validation:** each pattern traces to a requirement; at least one pattern is removed by the parsimony test.
- **Pitfalls:** assuming the best option on each axis composes.
- **Draws on:** Topic 7 (5.9, 5.10, 6.5, 6.6).

#### Step 15 — Recommend and explain rejected alternatives

- **Purpose:** state the choice and why the runner-up lost.
- **Inputs:** Step 14.
- **Actions:** write the recommendation; record each rejected alternative with a specific reason; mark the decision `Final` or `Conditional`.
- **Questions:** Why not the runner-up?
- **Output:** recommendation (D9).
- **Validation:** reasons cite criteria and evidence.
- **Pitfalls:** "too complex" as a reason.
- **Draws on:** Topic 7 (6.7).

#### Step 16 — Document assumptions, trade-offs and revisit conditions

- **Purpose:** show what would change the answer.
- **Inputs:** Step 15.
- **Actions:** list assumptions, accepted trade-offs and observable triggers, each tied to an assumption.
- **Questions:** What would change the answer?
- **Output:** assumptions and triggers (D11 part).
- **Validation:** each trigger is observable and tied to an assumption.
- **Pitfalls:** triggers such as "if things change".
- **Draws on:** Topic 7 (6.4, 6.10).

#### Step 17 — Produce a reference architecture view

- **Purpose:** communicate the design at the reference level.
- **Inputs:** Steps 14–16.
- **Actions:** draw layers, domains, flows, control plane and interfaces; label the level; map every element to a requirement and a pattern.
- **Questions:** Is every element justified?
- **Output:** reference architecture view (D10).
- **Validation:** no unexplained element; the view matches the recommendation.
- **Pitfalls:** a diagram with components that no requirement demands.
- **Draws on:** Topic 7 (6.8).

#### Step 18 — Validate consistency and traceability

- **Purpose:** find contradictions before the sponsor does.
- **Inputs:** all artefacts.
- **Actions:** run the checker; trace requirement → criterion → decision → view in both directions; fix the source artefact first.
- **Questions:** Any contradiction?
- **Output:** review notes.
- **Validation:** random traces succeed.
- **Pitfalls:** patching the decision record instead of the source.
- **Draws on:** Topic 7 (6.9).

#### Step 19 — Prepare the final recommendation and review summary

- **Purpose:** give the sponsor and review board a readable readout.
- **Inputs:** all artefacts.
- **Actions:** write one to two pages: decision, rationale, trade-offs, conditions, risks and next steps.
- **Questions:** What is decided, why, and at what cost and risk?
- **Output:** D12.
- **Validation:** a non-specialist can follow it in ten minutes.
- **Pitfalls:** hiding conditions and limits.
- **Draws on:** Topic 7.

---

## 6. Worked reference — Northbridge Bank

> **Everything in this section is illustrative.** Only the scenario facts in 6.1 come from the
> roadmap. Every other value is `Illustrative assumption`, `Inference` or `Open question`. No
> person or product is named. No stakeholder has validated any row. Run the checker (Appendix B)
> after any edit.

**Deliverable map**

| Deliverable | Section | Deliverable | Section |
| --- | --- | --- | --- |
| D1 Scope and problem | 6.1 | D7 Organisational and governance implications | 6.7 |
| D2 Requirements and constraints | 6.2 | D8 Risk and limitation register | 6.8 |
| D3 Candidate inventory | 6.3 | D9 Recommended combination | 6.9 |
| D4 Conceptual descriptions | 6.4 | D10 Reference architecture view | 6.10 |
| D5 Comparison matrix | 6.5 | D11 Decision rationale and rejected alternatives | 6.11 |
| D6 Trade-off analysis | 6.6 | D12 Final summary | 6.13 |

### 6.1 D1 — Project scope and business problem (Step 1)

**Scenario facts (roadmap)**

- Northbridge is a fictional mid-sized retail and business bank with a core banking system, a cards platform, a CRM and a loan origination system.
- Nightly extracts feed an enterprise data warehouse. A data lake created three years ago holds copies of some sources and is poorly trusted.
- Four business domains (retail, lending, cards, risk) each have analysts and some engineering capability.
- A central data team of about 25 people serves the whole bank and has a long backlog.

| Element | Statement |
| --- | --- |
| Problem | Consistent, governed, timely data is needed for regulatory reporting, fraud detection, risk analytics and customer analytics; the central team is a bottleneck; accountability and discoverability are weak |
| Objectives | Choose, justify and record the patterns for operating model, storage, processing, metadata, interaction and sharing, and the combination |
| In scope | Pattern choice per axis; the combination; the recommended reference architecture at a conceptual level |
| Out of scope | Product selection; detailed schema design (2D.4); physical storage design (2D.5); integration implementation (2D.6); platform build (2D.7); cloud service mapping (2D.8); detailed streaming design (2D.9); implementation and migration plans |
| Level | Reference architecture, not an implementation blueprint |
| Time frame | Current state as of the assessment; a first release inside the regulatory milestone assumption (ASM-01) |
| Labelled assumptions | ASM-01 to ASM-11; the roadmap figures: p95 fraud freshness 60 s, 08:00–22:00; reporting reconciled by T+2 business days; 99.5% monthly availability on business days |
| Units | Decimal multiples; 86,400 seconds per day; 21 business days of 1,440 minutes per month |

### 6.2 D2 — Requirements and constraints summary (Steps 2, 3, 4)

**Stakeholders**

| ID | Stakeholder (role) | Group | Interest | Decision rights | Evidence |
| --- | --- | --- | --- | --- | --- |
| STK-01 | Chief data officer | Sponsor | One governed, timely view; delivery within budget | Decides DEC-01, DEC-02, DEC-03, DEC-04, DEC-05, DEC-06, DEC-07; accepts residual risk | Illustrative assumption |
| STK-02 | Head of retail | Business owner | Customer analytics; retail data meaning | Consulted on DEC-01 and DEC-06 | Illustrative assumption |
| STK-03 | Head of lending | Business owner | Loan data meaning and reporting | Consulted on DEC-01 and DEC-06 | Illustrative assumption |
| STK-04 | Head of cards | Business owner and source owner | Card platform change; card data meaning | Owns DEP-01; consulted on DEC-05 | Illustrative assumption |
| STK-05 | Head of risk | Business consumer | Daily exposure over large history | Consulted on DEC-02 and DEC-06 | Illustrative assumption |
| STK-06 | Head of fraud operations | Business consumer | Card events in time to act; historical features | Owns REQ-06 and REQ-07; consulted on DEC-03 and DEC-05 | Illustrative assumption |
| STK-07 | Finance lead | Business consumer | Reconciled figures; cost control | Consulted on DEC-02 | Illustrative assumption |
| STK-08 | Regulatory reporting lead | Business consumer | Reconciled, auditable returns | Owns REQ-01; consulted on DEC-02 and DEC-04 | Illustrative assumption |
| STK-09 | Compliance officer | Control function | Lineage, accountability, residency, regulator liaison | Authority over CON-01 and CON-05; consulted on DEC-04 | Illustrative assumption |
| STK-10 | Security lead | Control function | Access, identity, exposure of copies | Authority over CON-04 and the security gates; consulted on DEC-05 and DEC-06 | Illustrative assumption |
| STK-11 | Internal audit | Independent review | Evidence quality and traceability | Independent reviewer of evidence against conclusions | Illustrative assumption |
| STK-12 | Data science lead | Business consumer | Historical training data; feature reproducibility | Consulted on DEC-02 and DEC-03 | Illustrative assumption |
| STK-13 | Platform and engineering lead | Technology | Operable, supportable platform; replay and availability | Owns DEP-04; consulted on DEC-03, DEC-05 | Illustrative assumption |
| STK-14 | Central data team lead | Technology | Backlog, capacity, role in a federated model | Owns the backlog figures (ASM-04); consulted on DEC-01 | Illustrative assumption |
| STK-15 | Lead architect | Author | Reproducible, defensible decisions | Recommends; does not decide | Illustrative assumption |

**Workloads and consumers**

| ID | Workload | Characteristics | Consumer | Outcome | Requirements | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| WL-01 | Regulatory reporting | Monthly and quarterly; reconciled, auditable; batch | STK-08 | Returns complete, reconciled and evidenced by T+2 business days | REQ-01; REQ-02; REQ-03; REQ-04; REQ-05 | Illustrative assumption |
| WL-02 | Fraud detection | Card events within seconds to minutes; plus historical features | STK-06 | Analysts see card events in time to act; models retrain from reproducible history | REQ-06; REQ-07; REQ-08 | Illustrative assumption |
| WL-03 | Risk analytics | Daily exposure; large historical volumes | STK-05 | Exposure available each business morning | REQ-09 | Illustrative assumption |
| WL-04 | Customer analytics | Daily to weekly; mixed structured and semi-structured data | STK-02 | Segments refreshed daily under defined rules | REQ-10 | Illustrative assumption |
| WL-05 | Document and interaction data | Unstructured; search and retrieval | STK-09 | Records searchable and retrievable by authorised users | REQ-11 | Illustrative assumption |

**Requirements.** Requirements describe outcomes; none names a pattern or a product.

| ID | Requirement statement | Type | Quality attribute | Priority | Acceptance criterion | AC measurable | Verification method | Source | Architecturally significant | Regulatory or accountability need | Workload | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-01 | Regulatory returns shall be complete and reconciled to authoritative sources within the reporting deadline | NFR | Correctness and timeliness | Must | Reconciliation difference is 0 for 100% of in-scope returns in 3 consecutive cycles, delivered by T+2 business days | Y | Reconciliation test per cycle | STK-08 | Y | Y | WL-01 | Draft |
| REQ-02 | Each critical regulatory data flow shall have documented end-to-end lineage to source records | DR | Traceability | Must | Lineage covers at least 90% of critical regulatory flows by the regulatory milestone | Y | Lineage coverage audit | STK-09 | Y | Y | WL-01 | Draft |
| REQ-03 | Each sensitive customer data asset shall have a named accountable owner and steward | DR | Accountability | Must | 100% of assets on the approved sensitive-asset list have both, confirmed in writing | Y | Register inspection | STK-09 | Y | Y | WL-01 | Draft |
| REQ-04 | Access to sensitive customer data shall be policy-based, use existing identity services and be auditable | NFR | Security | Must | 100% of access paths pass authorisation tests and every grant is attributable in the audit log | Y | Access-path tests and log review | STK-10 | Y | Y | WL-01 | Draft |
| REQ-05 | Personal data shall remain in the permitted jurisdiction, including copies and backups | NFR | Residency | Must | 100% of stores, copies and backups in the inventory are located in the permitted jurisdiction | Y | Inventory inspection and audit | STK-09 | Y | Y | WL-01 | Draft |
| REQ-06 | Card events shall be visible to fraud analysts within the freshness target | NFR | Freshness | Must | p95 freshness is 60 s or less, 08:00–22:00, over a rolling 30 days | Y | Event-ID timestamp correlation | STK-06 | Y | N | WL-02 | Draft |
| REQ-07 | The fraud history shall be rebuildable within the recovery objective | NFR | Recoverability | Must | A recovery exercise rebuilds 3 years of card-event history in 12 hours or less | Y | Timed recovery exercise | STK-06 | Y | N | WL-02 | Draft |
| REQ-08 | The analytical platform shall be available on business days | NFR | Availability | Must | At least 99.5% of eligible minutes per month meet the availability condition | Y | Interval monitoring | STK-13 | Y | N | WL-02 | Draft |
| REQ-09 | Daily risk exposure shall be available by the start of the business day | NFR | Timeliness | Must | Exposure is published by 07:00 on at least 99% of business days over a rolling 30 days | Y | Publication timestamp log | STK-05 | N | N | WL-03 | Draft |
| REQ-10 | Customer analytics datasets shall refresh at least daily under defined segment rules | NFR | Timeliness | Should | Datasets are available by 08:00 on at least 95% of days over a rolling 30 days | Y | Publication timestamp log | STK-02 | N | N | WL-04 | Draft |
| REQ-11 | Documents and interaction records shall be searchable and retrievable by authorised users | NFR | Performance | Should | p95 response time is 5 s or less for the agreed query set | Y | Query benchmark | STK-09 | N | N | WL-05 | Draft |
| REQ-12 | Each shared dataset shall have a documented owner, definition, quality expectation and change-notification path | DR | Accountability | Must | 100% of datasets on the priority list have all four, reviewed by the owner | Y | Contract register inspection | STK-09 | Y | Y | all | Draft |
| REQ-13 | The central request backlog shall drain and clear in an agreed time | NFR | Throughput | Must | Forecast clearance is 78 weeks or less, with central demand below central capacity | Y | Queue forecast from the 8-week request log | STK-14 | Y | N | all | Draft |
| REQ-14 | The recommended combination shall stay within the sponsor's cost ceiling | NFR | Cost | Must | Three-year total cost of ownership is 2,000 thousand currency units or less (planning value pending UNK-02) | Y | Finance-reviewed cost model | STK-01 | Y | N | all | Draft |
| REQ-15 | The capability shall be delivered before the regulatory milestone | NFR | Delivery | Must | First production release within 12 months of programme start (planning value pending UNK-01) | Y | Delivery plan review | STK-09 | Y | N | all | Draft |
| REQ-16 | Existing lake data assets shall be inventoried and given a lifecycle decision | DR | Data governance | Should | 100% of lake datasets have an owner and a keep, repair, quarantine or retire decision within 6 months | Y | Inventory inspection | STK-13 | N | N | all | Draft |
| REQ-17 | Consumers shall be able to find and correctly interpret priority datasets | NFR | Discoverability | Should | At least 90% of 10 observed consumer tasks succeed without private guidance | Y | Observed task test | STK-02 | N | N | all | Draft |
| REQ-18 | Copies of sensitive data shall be inventoried, bounded in retention and deletable | DR | Privacy | Must | 100% of sensitive-data copies are inventoried and a deletion request reaches all copies within 30 days | Y | Copy inventory and deletion drill | STK-10 | Y | Y | all | Draft |
| REQ-19 | Registered consumers shall not be broken by unannounced changes to shared datasets | NFR | Change resilience | Should | 0 unannounced breaking changes per quarter for registered consumers | Y | Change log and contract tests | STK-14 | N | N | all | Draft |

**Targets**

| ID | Requirement | SLI definition | Target | Window | Scope and boundary | Method | Evidence | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TGT-01 | REQ-06 | Elapsed time from the card event timestamp to first visibility in the analyst tool | p95 <= 60 s | Rolling 30 days, 08:00–22:00 | Eligible card events; source wait is included | Event-ID correlation with synchronised clocks | Illustrative assumption | Low |
| TGT-02 | REQ-01 | Time from period end to a reconciled, evidenced return | <= 2 business days, reconciliation difference 0 | Each reporting cycle | In-scope returns | Reconciliation and publication log | Illustrative assumption | Low |
| TGT-03 | REQ-08 | Share of eligible business-day minutes in which the platform meets the availability condition | >= 99.5% (151.2 minutes allowance per month, EST-13) | Calendar month | Business days only; whole serving path | Interval monitoring | Illustrative assumption | Low |
| TGT-04 | REQ-07 | Elapsed time to rebuild 3 years of card-event history | <= 12 hours | Per recovery exercise | Fraud history and features | Timed recovery exercise | Illustrative assumption | Low |
| TGT-05 | REQ-02 | Share of critical regulatory flows with documented end-to-end lineage | >= 90% | At the regulatory milestone | Critical regulatory flows | Lineage coverage audit | Illustrative assumption | Low |
| TGT-06 | REQ-09 | Share of business days on which exposure publishes by 07:00 | >= 99% | Rolling 30 days | Risk exposure dataset | Publication timestamp log | Illustrative assumption | Low |
| TGT-07 | REQ-13 | Forecast weeks to clear the central backlog | <= 78 weeks | Reviewed monthly | Central request queue | Queue forecast, EST-04 to EST-06 | Illustrative assumption | Low |
| TGT-08 | REQ-11 | Response time of the agreed document query set | p95 <= 5 s | Rolling 30 days | Authorised users | Query benchmark | Illustrative assumption | Low |

**Constraints**

| ID | Constraint | Authority | Rationale | Fixed or negotiable | Challenge route | Linked | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CON-01 | Personal data remains in the permitted jurisdiction, including copies and backups | STK-09 | Data protection obligation (roadmap scenario) | Fixed | Only through the compliance function | REQ-05; GT-01; GT-12 | Active | Stakeholder statement |
| CON-02 | The core banking batch window ends at 02:30 | STK-13 | Operational dependency (roadmap scenario) | Fixed | Core engineering change | REQ-06; GT-11 | Active | Stakeholder statement |
| CON-03 | The central team can grow by no more than a modest number of people (planning value: 4) | STK-01 | Funding decision (roadmap scenario) | Fixed | Sponsor decision | REQ-13; GT-02 | Active | Stakeholder statement |
| CON-04 | Existing identity services must be used | STK-10 | Security architecture (roadmap scenario) | Fixed | Security architecture change | REQ-04; GT-01; GT-12 | Active | Stakeholder statement |
| CON-05 | A regulatory milestone date applies; the date is not supplied | STK-09 | Regulator request (roadmap scenario) | Fixed | Regulator correspondence only | REQ-15; ASM-01; UNK-01; GT-06; GT-10 | Active | Stakeholder statement |
| CON-06 | A cost ceiling is set by the sponsor; the value is not supplied | STK-01 | Funding decision | Fixed | Sponsor decision | REQ-14; ASM-02; UNK-02; GT-19 | Active | Stakeholder statement |

**Assumptions**

| ID | Assumption | Owner | Confidence | Impact if wrong | Validation method | Validation due (week) | Fallback | Linked | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASM-01 | The regulatory milestone allows 12 months from programme start | STK-09 | Low | High | Written confirmation from compliance | 2 | Re-run GT-06, GT-10 and GT-20 with the confirmed date (SEN-08) | UNK-01; DEC-02; DEC-04; DEC-07 | Open | Illustrative assumption |
| ASM-02 | The three-year cost ceiling is 2,000 thousand currency units | STK-01 | Low | High | Sponsor confirmation | 6 | Re-run GT-19 and the scores (SEN-24) | UNK-02; DEC-07 | Open | Illustrative assumption |
| ASM-03 | Domains can absorb 30% (federated hybrid) and 45% (domain-operated products) of requests | STK-14 | Low | High | Pilot measurement against the request log | 6 | Re-run DEC-01 (SEN-01, SEN-02) | INP-05; INP-06; DEC-01 | Open | Illustrative assumption |
| ASM-04 | The backlog is 120 requests, demand 14 and central capacity 12 requests per week | STK-14 | Low | High | Eight weeks of the request log | 3 | Re-run DEC-01 (SEN-03) | INP-01; INP-02; INP-03; DEC-01 | Open | Illustrative assumption |
| ASM-05 | A single stream path can replay history at 80 MB/s sustained | STK-13 | Low | High | Replay test on representative data | 6 | Re-run DEC-03 (SEN-12) | INP-11; DEC-03 | Open | Illustrative assumption |
| ASM-06 | The card platform owner can support change capture and, if needed, events | STK-04 | Low | High | Technical discussion and spike | 8 | Fall back to events (OPT-27) or relax the target through the sponsor | DEP-01; DEC-05; DEC-07 | Open | Illustrative assumption |
| ASM-07 | Steward-curated lineage can cover 91% of critical flows and incremental metadata 94% | STK-09 | Low | High | Sample of critical flows | 8 | Re-run DEC-04 (SEN-15) | REQ-02; DEC-04 | Open | Illustrative assumption |
| ASM-08 | Component availabilities are as stated by providers (AV table) | STK-13 | Low | High | Measure in a non-production trial | 8 | Re-run GT-18 and CRIT-34 | AV-01; DEC-07 | Open | Illustrative assumption |
| ASM-09 | The readiness scores in the RD table are accurate | STK-01 | Low | High | Evidence review with domain heads | 4 | Re-run GT-03 and GT-04 (SEN-04) | RD-01; DEC-01 | Open | Illustrative assumption |
| ASM-10 | Batch recompute sustains 300 MB/s | STK-13 | Medium | Medium | Recompute test on representative data | 6 | Re-run GT-08 (SEN-11) | INP-10; DEC-03 | Open | Illustrative assumption |
| ASM-11 | The processing, commit and publish stages fit their planning budgets (8 s, 4 s and 3 s) | STK-13 | Low | High | Timed non-production run | 8 | Re-run GT-07 and GT-17 (SEN-13) | TB-06; DEC-03; DEC-07 | Open | Illustrative assumption |

**Dependencies**

| ID | Dependency | Provider | Consumer | Owner | Needed by (week) | Failure consequence | Contingency | Linked | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEP-01 | The card platform owner supports change capture (or events) for card events | STK-04 | DEC-05 | STK-04 | 10 | The fraud feed cannot reach the freshness target | Use source-published events if committed; otherwise return the target to the sponsor | OPT-19; OPT-20; ASM-06 | Open | Illustrative assumption |
| DEP-02 | Security approves read access to the source change log | STK-10 | DEC-05 | STK-10 | 10 | The change-capture option is refused | Use source-published events | OPT-20; GT-12 | Open | Illustrative assumption |
| DEP-03 | Compliance defines the sensitive-asset list and the lineage evidence format | STK-09 | DEC-04 | STK-09 | 3 | REQ-02 and REQ-03 stay untestable | Proceed on a provisional list | REQ-02; REQ-03 | Open | Illustrative assumption |
| DEP-04 | The platform team supports shared controls during the transition | STK-13 | DEC-01 | STK-13 | 6 | Domains cannot operate under common controls | Keep operation central for longer | OPT-02; GT-01 | Open | Illustrative assumption |
| DEP-05 | Domain heads nominate owners for the pilot product | STK-02 | DEC-01 | STK-02 | 6 | The bounded pilot cannot start | Defer the pilot; stay with central operation | OPT-03; GT-03 | Open | Illustrative assumption |

**Risks** (cause–event–effect; horizon: until the linked decision record is accepted)

| ID | Risk | Owner | Probability | Impact | Exposure | Band | Horizon | Response | Trigger | Escalation | Linked | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RSK-01 | Because domain ownership is announced without funded capacity, it may become nominal, leaving the central backlog unchanged | STK-14 | 3 | 4 | 12 | High | Until ADR-01 is accepted | Require named owners, funded capacity and a support contact before delegation; measure absorption | Measured domain absorption under 20% after the pilot | STK-01 | OPT-02; ASM-03; SEN-01 | Open | Illustrative assumption |
| RSK-02 | Because the modelled serial availability margin is thin (about 5 basis points), a provider shortfall may breach the 99.5% target | STK-13 | 3 | 4 | 12 | High | Until ADR-01 is accepted | Measure component availability in a trial; keep the processing path simple | Measured serial availability under 99.5% | STK-01 | GT-18; ASM-08; OPT-26 | Open | Illustrative assumption |
| RSK-03 | Because the best option on each axis does not compose (63 s against 60 s), a team may adopt axis winners and miss the fraud target | STK-06 | 3 | 4 | 12 | High | Until ADR-01 is accepted | Gate the combination end to end, not axis by axis | Any proposal that bypasses GT-17 | STK-01 | OPT-30; GT-17; SEN-22 | Open | Illustrative assumption |
| RSK-04 | Because the regulatory milestone is unconfirmed, the 12-month assumption may be wrong and the selected combination late or over-built | STK-09 | 3 | 5 | 15 | Very high | Until ADR-01 is accepted | Obtain written confirmation of the date and evidence format | No written confirmation by the end of week 2 | STK-01 | ASM-01; UNK-01; CON-05 | Open | Illustrative assumption |
| RSK-05 | Because lake copies have no owner, untrusted data may continue to be used for reporting | STK-13 | 4 | 3 | 12 | High | Until REQ-16 is met | Inventory, quarantine or retire copies under an approved lifecycle review | Any report sourced from an unowned lake dataset | STK-01 | OPT-06; REQ-16 | Open | Illustrative assumption |
| RSK-06 | Because metadata ownership is weak, catalogue and lineage entries may be stale, giving false assurance | STK-09 | 3 | 3 | 9 | Moderate | Until ADR-01 is accepted | Assign metadata owners and measure freshness and coverage | Coverage or freshness below agreed thresholds | STK-01 | OPT-14; ASM-07 | Open | Illustrative assumption |
| RSK-07 | Because a vendor or team proposes extra patterns, scope may expand into a broad platform programme | STK-15 | 3 | 4 | 12 | High | Until ADR-01 is accepted | Apply the parsimony test to every added pattern | Any added pattern without a requirement | STK-01 | OPT-31; PT-01 | Open | Illustrative assumption |
| RSK-08 | Because stream replay may be slower than assumed, adopting a single stream path later could miss the 12-hour objective | STK-13 | 2 | 4 | 8 | Moderate | Until DEC-03 is revisited | Measure replay throughput before reconsidering OPT-11 | Measured replay at or above 135 MB/s | STK-01 | OPT-11; ASM-05; SEN-12 | Open | Illustrative assumption |
| RSK-09 | Because change capture and shared copies may create data outside the jurisdiction, residency could be breached | STK-09 | 2 | 5 | 10 | High | Until all decision records are accepted | Inventory every copy path; confirm support-access terms | Any copy path outside the jurisdiction | STK-01 | CON-01; REQ-05; REQ-18 | Open | Illustrative assumption |

**Unknowns**

| ID | Open question | Decisions affected | Blocks | Owner | Evidence needed | Due week | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UNK-01 | What is the exact regulatory milestone date and evidence format? | DEC-02; DEC-04; DEC-07 | Blocks decision | STK-09 | Regulator correspondence | 2 | Open |
| UNK-02 | What is the sponsor's cost ceiling? | DEC-07 | Blocks decision | STK-01 | Sponsor confirmation | 6 | Open |
| UNK-03 | What is the measured freshness baseline of the current fraud feed? | DEC-03; DEC-05 | Manageable gap | STK-06 | Timestamp correlation on 30 days of events | 3 | Open |
| UNK-04 | How well does the warehouse reconcile critical returns today? | DEC-02 | Manageable gap | STK-08 | Reconciliation of two cycles | 4 | Open |
| UNK-05 | Which lake datasets have owners, consumers and a lifecycle decision? | DEC-02 | Manageable gap | STK-13 | Lake inventory | 6 | Open |

**Estimation inputs.** `Low` and `High` are the low and high plausible value of each input; they are
not best- and worst-case bounds of an output. Confidence follows the label: `measured` and `sampled`
give High or Medium, `stated` Medium, `estimated` Low to Medium, `guessed` Low.

| ID | Input | Unit | Low | Expected | High | Estimate label | Basis and validation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| INP-01 | Central request backlog | requests | 90 | 120 | 150 | guessed | Illustrative; take from the request log (ASM-04) |
| INP-02 | Request arrival rate | requests/week | 12 | 14 | 16 | estimated | Illustrative; take from the request log (ASM-04) |
| INP-03 | Central capacity | requests/week | 10 | 12 | 13 | estimated | Illustrative; take from delivered requests (ASM-04) |
| INP-04 | Capacity uplift from better prioritisation (OPT-01) | fraction | 0.05 | 0.10 | 0.15 | guessed | Illustrative; no evidence supplied |
| INP-05 | Share of requests absorbed by domains under OPT-02 | fraction | 0.15 | 0.30 | 0.40 | guessed | Illustrative; pilot measurement (ASM-03) |
| INP-06 | Share of requests absorbed by domains under OPT-03 | fraction | 0.25 | 0.45 | 0.60 | guessed | Illustrative; pilot measurement (ASM-03) |
| INP-07 | Daily logical card-event volume | GB/day | 3.2 | 4.6 | 8.2 | estimated | Reused from the Module 2D.2 worksheet; validate by sampling |
| INP-08 | Annual volume growth | fraction/year | 0.05 | 0.15 | 0.25 | guessed | Illustrative; measure from 24 months of history |
| INP-09 | History retained for a rebuild | years | 3 | 3 | 3 | stated | REQ-07 |
| INP-10 | Batch recompute sustained throughput | MB/s | 200 | 300 | 400 | estimated | Illustrative; recompute test (ASM-10) |
| INP-11 | Stream replay sustained throughput | MB/s | 50 | 80 | 150 | guessed | Illustrative; replay test (ASM-05) |
| INP-12 | Card events per day for the fraud path | events/day | 1,600,000 | 2,000,000 | 2,600,000 | stated | Module 2D.2 scenario figure |
| INP-13 | Peak-to-average factor | ratio | 3 | 4 | 10 | guessed | Illustrative; derive from time-bucketed history |
| INP-14 | Capacity safety factor | ratio | 1.25 | 1.5 | 2.0 | estimated | Illustrative; justify with load tests |
| INP-15 | Platform availability target | fraction | 0.995 | 0.995 | 0.995 | stated | REQ-08 |
| INP-16 | Eligible minutes per month (21 business days × 1,440) | minutes | 30,240 | 30,240 | 30,240 | stated | Convention in Section 6.1 |

**Computed estimates.** Expressions use the IDs above; `**` means power. Results use four significant
digits. Clearance time is capped at 9,999 weeks to mean "the queue never drains".

| ID | Estimate | Expression | Unit | Expected | Interpretation |
| --- | --- | --- | --- | --- | --- |
| EST-01 | Central capacity under OPT-01 | `INP-03*(1+INP-04)` | requests/week | 13.2 | Capacity stays below demand (INP-02) |
| EST-02 | Backlog clearance under OPT-01 | `min(INP-01/max(EST-01-INP-02,0.001),9999)` | weeks | 9999 | The queue never drains: the central model alone does not fix the bottleneck |
| EST-03 | Central demand under OPT-02 | `INP-02*(1-INP-05)` | requests/week | 9.8 | Below central capacity, so the queue drains |
| EST-04 | Backlog clearance under OPT-02 | `min(INP-01/max(INP-03-EST-03,0.001),9999)` | weeks | 54.55 | Drains slowly; sensitive to domain absorption |
| EST-05 | Central demand under OPT-03 | `INP-02*(1-INP-06)` | requests/week | 7.7 | Lowest central demand, but relies on unproven domain capability |
| EST-06 | Backlog clearance under OPT-03 | `min(INP-01/max(INP-03-EST-05,0.001),9999)` | weeks | 27.91 | Fastest drain if domains absorb 45% |
| EST-07 | Year-1 annual logical card-event volume | `INP-07*365/1000` | TB/year | 1.679 | Base-year generation |
| EST-08 | Three-year cumulative logical volume | `EST-07*((1+INP-08)**INP-09-1)/INP-08` | TB | 5.83 | History to rebuild (REQ-07) |
| EST-09 | Rebuild time by batch recompute | `EST-08*1000000/INP-10/3600` | hours | 5.398 | Within the 12-hour objective |
| EST-10 | Rebuild time by single-path stream replay | `EST-08*1000000/INP-11/3600` | hours | 20.24 | Misses the 12-hour objective; replay throughput must reach about 135 MB/s |
| EST-11 | Peak card-event rate | `INP-12/86400*INP-13` | events/s | 92.59 | Rate the fraud path must absorb |
| EST-12 | Required throughput capacity | `EST-11*INP-14` | events/s | 138.9 | Capacity to demonstrate under load; peak factor dominates |
| EST-13 | Allowed downtime at the availability target | `(1-INP-15)*INP-16` | minutes/month | 151.2 | Total budget for all qualifying outages |

**Worked checks (reviewer recomputation).** (1) EST-07: 4.6 GB/day × 365 ÷ 1,000 = 1.679 TB/year.
(2) EST-08: 1.679 × (1.15³ − 1) ÷ 0.15 = 5.830 TB. (3) EST-10: 5.830 × 10⁶ MB ÷ 80 MB/s ÷ 3,600 =
20.2 hours, which exceeds 12 hours; the same volume at 300 MB/s takes 5.4 hours (EST-09).

**Sensitivity ranking (tornado).** Each input is moved alone from its low to its high value with all
others at the expected value. `Swing` is the absolute change in the output; rank 1 is the largest;
ties share a rank.

| ID | Output | Input | Output at low | Output at high | Swing | Rank |
| --- | --- | --- | --- | --- | --- | --- |
| TN-01 | EST-04 | INP-05 | 1200 | 33.33 | 1167 | 1 |
| TN-02 | EST-04 | INP-03 | 600 | 37.5 | 562.5 | 2 |
| TN-03 | EST-04 | INP-02 | 33.33 | 150 | 116.7 | 3 |
| TN-04 | EST-04 | INP-01 | 40.91 | 68.18 | 27.27 | 4 |
| TN-05 | EST-06 | INP-06 | 80 | 18.75 | 61.25 | 1 |
| TN-06 | EST-06 | INP-03 | 52.17 | 22.64 | 29.53 | 2 |
| TN-07 | EST-06 | INP-02 | 22.22 | 37.5 | 15.28 | 3 |
| TN-08 | EST-06 | INP-01 | 20.93 | 34.88 | 13.95 | 4 |
| TN-09 | EST-10 | INP-07 | 14.08 | 36.09 | 22 | 1 |
| TN-10 | EST-10 | INP-11 | 32.39 | 10.8 | 21.59 | 2 |
| TN-11 | EST-10 | INP-08 | 18.38 | 22.23 | 3.848 | 3 |

**Reading the ranking.** Domain absorption (INP-05, INP-06) dominates the backlog forecasts, and
it is a `guessed` input: it must be measured in a pilot before any operating-model change is
trusted. For the stream-rebuild time, daily volume (INP-07, an `estimated` input) and replay throughput
(INP-11, a `guessed` input) have nearly equal swings (22.0 and 21.6 hours): both must be sampled before the
12-hour objective is judged for a single stream path.

---

### 6.3 D3 — Candidate pattern inventory (Steps 5 and 6)

**Decisions by axis.** DEC-01 to DEC-06 are independent in their gates and criteria but coupled in
the end-to-end behaviour of the fraud path: DEC-03 (processing) requires an interaction option that
can feed it (DEC-05), and DEC-06 (shared interfaces) requires an ownership model (DEC-01). DEC-07
assembles one option per axis and tests them together.

| ID | Decision | Axis | Scope | Excluded | Decision-maker | Coupled with | Needed by (week) | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEC-01 | Who owns, governs and operates data | Operating model | Ownership, stewardship and operation of analytical data | Organisation design below team level; hiring plans | STK-01 | DEC-06 | 7 | Proposed |
| DEC-02 | Where analytical data live | Analytical storage | Reporting, historical and unstructured analytical workloads | Physical storage design (2D.5); product choice | STK-01 | DEC-03 | 7 | Proposed |
| DEC-03 | How card events are processed and history rebuilt | Processing | Fraud-path processing and rebuild | Detailed streaming design (2D.9) | STK-01 | DEC-05 | 7 | Proposed |
| DEC-04 | How data are found, related and governed | Metadata and control | Catalogue, lineage, ownership metadata, policy | Metadata tool selection; classification content | STK-01 | DEC-01 | 7 | Proposed |
| DEC-05 | How card events reach the fraud consumers | Interaction | Source-to-consumer delivery for the fraud path | Integration implementation (2D.6) | STK-01 | DEC-03 | 7 | Proposed |
| DEC-06 | How domains share analytical data | Sharing | Cross-domain analytical access | Schema and contract detail (2D.4, 2D.6) | STK-01 | DEC-01 | 7 | Proposed |
| DEC-07 | Which assembled set of patterns is justified | Combination | One option per axis, tested end to end | Implementation and migration plans | STK-01 | all | 7 | Proposed |

**Options.** `Role` marks the minimal-change baseline. `Requires` lists options of which at least one
must be in the same combination; `Conflicts` lists options that cannot coexist with it. Combinations
(OPT-25 to OPT-31) list their members.

| ID | Decision | Option | Option description | Role | Requires | Conflicts | Members | Why a candidate | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OPT-01 | DEC-01 | Improved centralised model | The central team keeps delivery and governance; prioritisation and service levels improve | Baseline | none | none | n/a | Minimal change; uses the existing team | Illustrative assumption |
| OPT-02 | DEC-01 | Federated hybrid | Central governance, platform and operation of shared pipelines; domains own definitions and stewardship and take a share of simple requests | Alternative | none | none | n/a | Balances domain knowledge and enterprise consistency; can be staged | Illustrative assumption |
| OPT-03 | DEC-01 | Domain-operated data products (staged) | Selected domains own and operate a few data products with contracts, under federated governance | Alternative | none | none | n/a | Strongest accountability and queue relief if domains can run products | Illustrative assumption |
| OPT-04 | DEC-01 | Full data-mesh-style operating model | All four mesh principles across all domains | Alternative | none | none | n/a | Highest autonomy; included so its readiness gate is tested, not assumed | Illustrative assumption |
| OPT-05 | DEC-02 | Remediate the current estate | Keep the nightly warehouse and the existing lake; remediation only | Baseline | none | none | n/a | Minimal change | Illustrative assumption |
| OPT-06 | DEC-02 | Governed warehouse core plus repaired lake | Warehouse is the governed reporting core; the lake is repaired only for proven workloads, each with an owner and a lifecycle | Alternative | none | none | n/a | Reuses assets and separates concerns | Illustrative assumption |
| OPT-07 | DEC-02 | Lakehouse-centred migration | Migrate analytical data to managed tables on shared storage | Alternative | none | none | n/a | Could unify varied workloads | Illustrative assumption |
| OPT-08 | DEC-02 | Warehouse only | Retire the lake; serve all workloads from the warehouse | Alternative | none | none | n/a | Fewest stores | Illustrative assumption |
| OPT-09 | DEC-03 | Scheduled batch | Process card data in nightly batches | Baseline | none | none | n/a | Minimal change | Illustrative assumption |
| OPT-10 | DEC-03 | Micro-batch with batch recompute | Short-interval incremental processing for the live view; history rebuilt by batch recompute from raw | Alternative | OPT-18; OPT-19; OPT-20 | none | n/a | Simpler than a stream path; improves freshness | Illustrative assumption |
| OPT-11 | DEC-03 | Single stream path with replay | One continuous path for live processing and replay from a retained log | Alternative | OPT-19; OPT-20 | OPT-12 | n/a | One logic path for live and rebuild | Illustrative assumption |
| OPT-12 | DEC-03 | Separate batch and speed paths | Provisional fresh results plus an authoritative batch result, reconciled | Alternative | OPT-19; OPT-20 | OPT-11 | n/a | Fresh view and authoritative history coexist | Illustrative assumption |
| OPT-13 | DEC-04 | Manual catalogue with curated lineage | A steward-curated catalogue; lineage maintained by hand for regulatory flows | Baseline | none | none | n/a | Minimal change | Illustrative assumption |
| OPT-14 | DEC-04 | Incremental catalogue and lineage | Minimum metadata, ownership and lineage for priority datasets, automated where tested | Alternative | none | none | n/a | Targets discoverability and regulatory evidence first | Illustrative assumption |
| OPT-15 | DEC-04 | Broad automated fabric programme | Automated discovery, lineage and policy across all sources | Alternative | none | none | n/a | Maximum automation | Illustrative assumption |
| OPT-16 | DEC-04 | Product-embedded metadata | Metadata only inside domain data products | Alternative | OPT-03; OPT-04 | none | n/a | Cheap if products exist | Illustrative assumption |
| OPT-17 | DEC-05 | Existing batch file feed | The card platform's 15-minute batch file | Baseline | none | none | n/a | Minimal change | Illustrative assumption |
| OPT-18 | DEC-05 | Short-interval file feed | The source emits files every 30 seconds | Alternative | none | none | n/a | Smallest change to the source | Illustrative assumption |
| OPT-19 | DEC-05 | Source-published events | The card platform publishes authorisation events to a durable channel | Alternative | none | none | n/a | Lowest delay; decouples consumers | Illustrative assumption |
| OPT-20 | DEC-05 | Change capture from the source store | Changes are captured from the source data store's log into a durable channel | Alternative | none | none | n/a | No change to the source application | Illustrative assumption |
| OPT-21 | DEC-06 | Shared database access | Consumers read the producer's tables directly | Baseline | none | none | n/a | Minimal change | Illustrative assumption |
| OPT-22 | DEC-06 | Scheduled export with manifest | Producers export bounded files with a completeness manifest | Alternative | none | none | n/a | Simple and reconcilable | Illustrative assumption |
| OPT-23 | DEC-06 | Managed data-product interface | Selected datasets are published with a contract, owner, quality and freshness expectations | Alternative | OPT-02; OPT-03; OPT-04 | none | n/a | Reuse and accountability for high-value datasets | Illustrative assumption |
| OPT-24 | DEC-06 | Events for all analytical consumers | Every analytical dataset is published as events | Alternative | OPT-19; OPT-20 | none | n/a | Maximum decoupling | Illustrative assumption |
| OPT-25 | DEC-07 | Minimal-change baseline | All six baselines together | Baseline | none | none | OPT-01; OPT-05; OPT-09; OPT-13; OPT-17; OPT-21 | Reference point | Illustrative assumption |
| OPT-26 | DEC-07 | Workload-led hybrid with change capture | Federated hybrid, governed warehouse with repaired lake, micro-batch, incremental metadata, change capture, managed interface for selected datasets | Alternative | none | none | OPT-02; OPT-06; OPT-10; OPT-14; OPT-20; OPT-23 | Each pattern serves a stated requirement | Illustrative assumption |
| OPT-27 | DEC-07 | Workload-led hybrid with source events | As OPT-26 but with source-published events | Alternative | none | none | OPT-02; OPT-06; OPT-10; OPT-14; OPT-19; OPT-23 | Tests the dependency on the card platform change | Illustrative assumption |
| OPT-28 | DEC-07 | Domain-product-first hybrid | As OPT-26 but with domain-operated products from the start | Alternative | none | none | OPT-03; OPT-06; OPT-10; OPT-14; OPT-20; OPT-23 | Tests whether to start with domain operation | Illustrative assumption |
| OPT-29 | DEC-07 | Lambda-based fraud path | As OPT-27 but with separate batch and speed paths | Alternative | none | none | OPT-02; OPT-06; OPT-12; OPT-14; OPT-19; OPT-23 | Tests a formal two-path design | Illustrative assumption |
| OPT-30 | DEC-07 | Axis winners combined | The top-ranked option of each axis, assembled | Alternative | none | none | OPT-02; OPT-06; OPT-10; OPT-14; OPT-18; OPT-23 | Tests whether axis winners compose | Illustrative assumption |
| OPT-31 | DEC-07 | Broad combination | Mesh, lakehouse, single stream path, Lambda, fabric, events for all | Alternative | none | none | OPT-04; OPT-07; OPT-11; OPT-12; OPT-15; OPT-19; OPT-24 | The over-engineered proposal to challenge | Illustrative assumption |

### 6.4 D4 — Conceptual architecture description per candidate (Step 7)

Every description is at the same level: components and responsibilities, flow, ownership and operating
model, and how the candidate fails at 3 a.m. (combinations are described by their members).

| ID | Option | Components and responsibilities | Data flow | Ownership and operating model | Organisational prerequisites | Failure at 3 a.m. | Level | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OD-01 | OPT-01 | Central team: ingestion, definitions, quality, access; prioritisation board | Requests queue to the central team; nightly delivery | Central ownership and operation | Central capacity and a clear prioritisation board | The queue grows unseen because demand exceeds capacity | Reference | Illustrative assumption |
| OD-02 | OPT-02 | Central governance forum and platform; domain stewards own definitions; central pipeline operation | Domains specify, central delivers; simple requests handled in domains | Federated decision rights; central on-call | Named domain stewards; an empowered forum; central platform support | A shared definition is disputed and escalation has no owner | Reference | Illustrative assumption |
| OD-03 | OPT-03 | Domain product teams: publish, operate, support products; platform provides paved path | Domain product to consumer through a contract | Domain owner and operator per product | Funded domain teams with engineering skills; a paved-path platform; on-call cover | A product's on-call is empty and consumers have no support route | Reference | Illustrative assumption |
| OD-04 | OPT-04 | All domains run products; self-service platform; computational governance | Product-to-product across all domains | Fully domain-operated | All four mesh principles operating: self-service platform, computational governance, funded products | Policy checks fail silently across many products at once | Reference | Illustrative assumption |
| OD-05 | OPT-05 | Existing warehouse and lake; remediation backlog | Nightly extracts to both stores | Central operation; unclear lake ownership | Remediation capacity; owners for lake data | A report is built on an untrusted lake copy | Reference | Illustrative assumption |
| OD-06 | OPT-06 | Warehouse as governed core; lake zones for named workloads with owners and lifecycle | Sources to warehouse; selected sources to lake zones; curated outputs back to consumers | Warehouse owned centrally; lake zones by workload owner | Owners per lake zone; a stated authority boundary; a reconciliation process | A lake zone drifts from the warehouse definition | Reference | Illustrative assumption |
| OD-07 | OPT-07 | Managed tables on shared storage; table maintenance; shared compute | All sources to managed tables; consumers query tables | Platform-owned tables; domain-owned content | Table-management skills; migration capacity; semantics fixed first | Table compaction lags and reports slow down | Reference | Illustrative assumption |
| OD-08 | OPT-08 | One warehouse for all workloads; document store outside | All sources to the warehouse | Central ownership | Central ownership; a separate store for documents | Unstructured and training workloads are forced into the wrong shape | Reference | Illustrative assumption |
| OD-09 | OPT-09 | Nightly batch jobs | Source files to warehouse once a day | Central operation | Operations cover for nightly jobs | The nightly job fails and the fraud view is a day stale | Reference | Illustrative assumption |
| OD-10 | OPT-10 | Micro-batch jobs for the live view; batch recompute from raw for history | Feed to short-interval jobs to the fraud view; raw retained for recompute | Platform operates; fraud owns meaning | Operations for incremental jobs; raw retention; an interaction option that feeds it | The micro-batch falls behind and freshness slips silently | Reference | Illustrative assumption |
| OD-11 | OPT-11 | One stream job; retained log; state store | Feed to log to stream job to outputs; replay re-reads the log | Platform operates continuous jobs | Stream operations skills; log retention and replay capacity; deterministic logic | A logic bug needs a replay that cannot finish inside the objective | Reference | Illustrative assumption |
| OD-12 | OPT-12 | Speed path; batch path; reconciliation job; serving merge | Feed to both paths; reconciliation compares | Two paths with two owners | Both batch and stream skills; a reconciliation owner | The two paths disagree and nobody owns the difference | Reference | Illustrative assumption |
| OD-13 | OPT-13 | Spreadsheet catalogue; steward-maintained lineage | Manual updates by stewards | Stewards | Stewards with time to maintain entries | The catalogue is stale after a reorganisation | Reference | Illustrative assumption |
| OD-14 | OPT-14 | Catalogue; minimum metadata; lineage capture for priority datasets; ownership register | Pipelines emit lineage; stewards approve metadata | Metadata owner and domain stewards | A metadata owner; stewards; lineage capture on priority pipelines | Lineage capture breaks silently on a changed job | Reference | Illustrative assumption |
| OD-15 | OPT-15 | Automated crawlers; inference; policy propagation across sources | Connectors harvest everything; rules propagate | Platform-owned metadata; unclear semantics owners | Metadata owners for every source; connector coverage; policy ownership | Automation propagates a wrong classification everywhere | Reference | Illustrative assumption |
| OD-16 | OPT-16 | Metadata inside each product contract | Product publishes its own metadata | Product owners | Domain products already in place | Datasets outside products have no metadata at all | Reference | Illustrative assumption |
| OD-17 | OPT-17 | Source batch file every 15 minutes; ingest job | File to ingest to consumers | Source team and central team | Source team supports the current file | A file arrives late and no one notices | Reference | Illustrative assumption |
| OD-18 | OPT-18 | Source emits a file every 30 seconds; ingest job | Small files to ingest | Source team | Source team changes file cadence; ingest handles the file volume | File count overwhelms the ingest job | Reference | Illustrative assumption |
| OD-19 | OPT-19 | Source publishes events; durable channel; contract and schema rules | Event to channel to consumers | Source domain owns the contract | Source team publishes and owns an event contract | A producer removes a field and breaks consumers | Reference | Illustrative assumption |
| OD-20 | OPT-20 | Log reader on the source store; durable channel; filter for minimisation | Log change to channel to consumers | Platform owns capture; source domain owns meaning | Security approves log access; platform operates capture; source domain owns meaning | Log retention expires during an outage and changes are lost | Reference | Illustrative assumption |
| OD-21 | OPT-21 | Consumers read producer tables | Direct queries | Producer owns schema; no contract | Producer tolerates reader workload | A schema change breaks readers without notice | Reference | Illustrative assumption |
| OD-22 | OPT-22 | Export job; manifest; consumer load | Producer exports bounded files | Producer owns export | Producers own exports and manifests | An export is incomplete and the manifest is not checked | Reference | Illustrative assumption |
| OD-23 | OPT-23 | Product interface; contract; quality and freshness checks; access workflow | Producer publishes curated dataset; consumers subscribe | Product owner per dataset | Dataset owners; contract checks; an access workflow; a domain ownership model | A contract check is bypassed and a breaking change ships | Reference | Illustrative assumption |
| OD-24 | OPT-24 | Event channel for every dataset; consumer-side stores | Every change published; each consumer builds state | Producers own many contracts | Producers own many event contracts; retention and deletion controls | Retention and deletion of sensitive payloads cannot be proven | Reference | Illustrative assumption |

### 6.5 D5 — Pattern comparison matrix (Steps 8, 9, 12)

**Rule.** Gates are evaluated first for every option; an option with a `Fail` is ineligible and is not
scored. Criteria, weights and bands were **frozen in week 4**; scoring was done in **week 5**.

#### Hard gates

| ID | Decision | Gate statement | Source | Operator | Threshold | Unit | Applies to |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GT-01 | DEC-01 | A named accountable owner and a support route exist for sensitive customer data | REQ-03; CON-04 | n/a | n/a | n/a | all |
| GT-02 | DEC-01 | The central backlog drains within the target | REQ-13; TGT-07 | <= | 78 | weeks | OPT-01; OPT-02; OPT-03 |
| GT-03 | DEC-01 | Readiness supports a bounded domain-operated pilot | REQ-12; ASM-09 | >= | 13 | points of 30 | OPT-03 |
| GT-04 | DEC-01 | Readiness supports enterprise-wide adoption | REQ-12; ASM-09 | >= | 21 | points of 30 | OPT-04 |
| GT-05 | DEC-02 | Regulatory returns can be reconciled and evidenced by T+2 | REQ-01; TGT-02 | n/a | n/a | n/a | all |
| GT-06 | DEC-02 | Delivered before the regulatory milestone | REQ-15; CON-05; ASM-01 | <= | 12 | months | all |
| GT-07 | DEC-03 | The processing-side time budget fits its share of the freshness target | REQ-06; TGT-01 | <= | 35 | seconds | all |
| GT-08 | DEC-03 | History can be rebuilt within the recovery objective | REQ-07; TGT-04 | <= | 12 | hours | all |
| GT-09 | DEC-04 | Lineage covers the critical regulatory flows | REQ-02; TGT-05 | >= | 90 | percent | all |
| GT-10 | DEC-04 | Delivered before the regulatory milestone | REQ-15; CON-05 | <= | 12 | months | all |
| GT-11 | DEC-05 | The interaction-side time budget fits its share of the freshness target | REQ-06; TGT-01; CON-02 | <= | 35 | seconds | all |
| GT-12 | DEC-05 | Meets residency, identity and access-control constraints | CON-01; CON-04 | n/a | n/a | n/a | all |
| GT-13 | DEC-06 | Consumers are isolated from the producer's physical schema and workload | REQ-19 | n/a | n/a | n/a | all |
| GT-14 | DEC-06 | Retention and deletion of shared sensitive copies are enforceable | REQ-18 | n/a | n/a | n/a | all |
| GT-15 | DEC-07 | The assembled patterns are compatible | Requires and Conflicts columns of the option table | >= | 1 | compatible | all |
| GT-16 | DEC-07 | Every member passes its own axis gates | Gates GT-01 to GT-14 | <= | 0 | failing members | all |
| GT-17 | DEC-07 | End-to-end fraud freshness fits the target | REQ-06; TGT-01 | <= | 60 | seconds | all |
| GT-18 | DEC-07 | Serial availability meets the platform target | REQ-08; TGT-03 | >= | 0.995 | fraction | all |
| GT-19 | DEC-07 | Three-year cost is within the ceiling | REQ-14; CON-06; ASM-02 | <= | 2000 | k currency | all |
| GT-20 | DEC-07 | Delivered before the regulatory milestone | REQ-15; CON-05 | <= | 12 | months | all |

The 60-second target is shared: 35 seconds for the interaction side (GT-11) and 35 for the processing
side (GT-07) are *per-axis* limits that are individually lenient, so the sum is tested again in GT-17.

#### Readiness assessment (Topic 4 method; illustrative scores, evidence required for 2 or 3)

| ID | Dimension | Score | Evidence needed | Evidence |
| --- | --- | --- | --- | --- |
| RD-01 | Domain boundaries and authoritative meaning | 2 | Approved domain map and ownership decisions | Illustrative assumption |
| RD-02 | Product ownership and funding | 1 | Named owners with allocated capacity and a run budget | Illustrative assumption |
| RD-03 | Consumer demand and adoption | 2 | Named pilot consumers and validated use cases | Illustrative assumption |
| RD-04 | Product contracts and quality | 1 | Contract template and executable quality checks | Illustrative assumption |
| RD-05 | Self-serve platform | 2 | Working publication, access, monitoring and support path | Illustrative assumption |
| RD-06 | Federated governance | 2 | Named representatives, decision rights and an exception process | Illustrative assumption |
| RD-07 | Automated enforcement | 0 | Demonstrated policy checks with auditable outcomes | Illustrative assumption |
| RD-08 | Skills and operating model | 1 | Skills inventory, enablement plan and on-call coverage | Illustrative assumption |
| RD-09 | Executive sponsorship and incentives | 2 | A sponsor with authority and incentives for reliable consumption | Illustrative assumption |
| RD-10 | Cost visibility and value measurement | 1 | Baseline cost and a method to measure outcomes | Illustrative assumption |

The total is 14 of 30. Under the Topic 4 heuristic (0–12 do not launch; 13–20 consider a small pilot only if
the entry gates are met; 21–30 broader adoption may be justified), 14 supports a bounded pilot (GT-03)
and does not support enterprise-wide adoption (GT-04). The heuristic is a teaching rule, not a benchmark.

#### Scored criteria (weights sum to 1 per decision; frozen in week 4)

| ID | Decision | Criterion | Weight | Source | Rating basis | Frozen in week | Weight rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CRIT-01 | DEC-01 | Backlog clearance time | 0.25 | REQ-13; TGT-07 | Numeric bands AN | 4 | The bottleneck is the stated operating-model problem |
| CRIT-02 | DEC-01 | Accountability clarity | 0.25 | REQ-03; REQ-12 | Judgement anchors JA | 4 | Accountability is the regulator-facing need |
| CRIT-03 | DEC-01 | Operational feasibility and readiness fit | 0.20 | RD table; DEP-04 | Judgement anchors JA | 4 | A model the organisation cannot run is not an improvement |
| CRIT-04 | DEC-01 | Cross-domain consistency | 0.15 | REQ-12 | Judgement anchors JA | 4 | Shared definitions must survive delegation |
| CRIT-05 | DEC-01 | Three-year cost | 0.15 | REQ-14; CON-06 | Numeric bands AN | 4 | Cost matters but differs less than outcomes |
| CRIT-06 | DEC-02 | Governed reporting and reconciliation | 0.20 | REQ-01; REQ-02 | Judgement anchors JA | 4 | Reporting correctness is gated; this rates the margin |
| CRIT-07 | DEC-02 | Workload fit for varied data | 0.30 | WL-02; WL-03; WL-05 | Judgement anchors JA | 4 | Fraud history, risk volumes and documents are real workloads |
| CRIT-08 | DEC-02 | Duplicate-truth risk and complexity | 0.15 | REQ-16 | Judgement anchors JA | 4 | Two stores need a clear authority boundary |
| CRIT-09 | DEC-02 | Three-year cost | 0.20 | REQ-14; CON-06 | Numeric bands AN | 4 | Budget is a binding concern |
| CRIT-10 | DEC-02 | Delivery time | 0.15 | REQ-15; CON-05 | Numeric bands AN | 4 | The milestone is a gate; speed beyond it has diminishing value |
| CRIT-11 | DEC-03 | Processing-side freshness headroom | 0.20 | REQ-06; TGT-01 | Numeric bands AN | 4 | The gate guarantees the minimum; headroom protects against drift |
| CRIT-12 | DEC-03 | Operational complexity | 0.30 | REQ-08; RD table | Judgement anchors JA | 4 | Complexity is the main cost of formal two-path or stream designs |
| CRIT-13 | DEC-03 | Three-year cost | 0.20 | REQ-14; CON-06 | Numeric bands AN | 4 | Budget is a binding concern |
| CRIT-14 | DEC-03 | Correctness and reconciliation burden | 0.20 | REQ-01; REQ-06 | Judgement anchors JA | 4 | Duplicate logic multiplies reconciliation work |
| CRIT-15 | DEC-03 | Skills fit | 0.10 | RD-08 | Judgement anchors JA | 4 | Skills are uneven across domains |
| CRIT-16 | DEC-04 | Discoverability and reuse | 0.30 | REQ-17 | Judgement anchors JA | 4 | Discoverability is a stated problem |
| CRIT-17 | DEC-04 | Control-evidence automation | 0.20 | REQ-02; REQ-04 | Judgement anchors JA | 4 | Evidence for audit should not rely on memory |
| CRIT-18 | DEC-04 | Metadata accuracy risk | 0.15 | RSK-06 | Judgement anchors JA | 4 | Wrong metadata is worse than none |
| CRIT-19 | DEC-04 | Three-year cost | 0.20 | REQ-14; CON-06 | Numeric bands AN | 4 | Budget is a binding concern |
| CRIT-20 | DEC-04 | Delivery time | 0.15 | REQ-15; CON-05 | Numeric bands AN | 4 | The milestone is a gate; speed beyond it has diminishing value |
| CRIT-21 | DEC-05 | Three-year cost | 0.25 | REQ-14; CON-06 | Numeric bands AN | 4 | Cost differs widely among the feeds |
| CRIT-22 | DEC-05 | Delivery time | 0.15 | REQ-15; DEP-01 | Numeric bands AN | 4 | Earlier fraud signals reduce exposure |
| CRIT-23 | DEC-05 | Operability | 0.25 | REQ-08; REQ-19 | Judgement anchors JA | 4 | The path is run around the clock |
| CRIT-24 | DEC-05 | Dependency exposure | 0.20 | DEP-01; DEP-02 | Judgement anchors JA | 4 | Dependence on another team is the largest delivery risk |
| CRIT-25 | DEC-05 | Privacy and payload exposure | 0.15 | REQ-05; REQ-18 | Judgement anchors JA | 4 | Copies of sensitive data must be minimal |
| CRIT-26 | DEC-06 | Change resilience | 0.25 | REQ-19 | Judgement anchors JA | 4 | Silent breaking changes are the main sharing failure |
| CRIT-27 | DEC-06 | Reuse and discoverability | 0.25 | REQ-12; REQ-17 | Judgement anchors JA | 4 | Reuse is the point of sharing |
| CRIT-28 | DEC-06 | Operational simplicity | 0.20 | REQ-08 | Judgement anchors JA | 4 | Each interface is an operational commitment |
| CRIT-29 | DEC-06 | Three-year cost | 0.15 | REQ-14; CON-06 | Numeric bands AN | 4 | Budget is a binding concern |
| CRIT-30 | DEC-06 | Privacy and deletion control | 0.15 | REQ-18 | Judgement anchors JA | 4 | Deletion must reach copies |
| CRIT-31 | DEC-07 | Three-year cost of the combination | 0.25 | REQ-14; CON-06 | Numeric bands AN | 4 | The sum of the parts is what the sponsor funds |
| CRIT-32 | DEC-07 | Delivery time of the combination | 0.15 | REQ-15; CON-05 | Numeric bands AN | 4 | Parallel streams; the slowest governs |
| CRIT-33 | DEC-07 | End-to-end freshness headroom | 0.15 | REQ-06; TGT-01 | Numeric bands AN | 4 | The gate guarantees the minimum; headroom protects against drift |
| CRIT-34 | DEC-07 | Availability margin | 0.10 | REQ-08; TGT-03 | Numeric bands AN | 4 | Serial availability is thin for every combination |
| CRIT-35 | DEC-07 | Organisational readiness fit | 0.20 | RD table; DEP-04; DEP-05 | Judgement anchors JA | 4 | A combination the organisation cannot run is not viable |
| CRIT-36 | DEC-07 | Operational complexity and diagnosability | 0.15 | REQ-08 | Judgement anchors JA | 4 | Incidents cross patterns and owners |

#### Numeric rating bands (inclusive bounds; inputs rounded half-up to a whole number first)

Units: CRIT-01 weeks; CRIT-05, 09, 13, 19, 21, 29, 31 thousands of currency units; CRIT-10, 20, 22, 32
months; CRIT-11 and 33 seconds of margin; CRIT-34 basis points of availability above the target.

| ID | Criterion | Rating | From | To |
| --- | --- | --- | --- | --- |
| AN-01 | CRIT-01 | 5 | 0 | 26 |
| AN-02 | CRIT-01 | 4 | 27 | 40 |
| AN-03 | CRIT-01 | 3 | 41 | 60 |
| AN-04 | CRIT-01 | 2 | 61 | 104 |
| AN-05 | CRIT-01 | 1 | 105 | inf |
| AN-06 | CRIT-05 | 5 | 0 | 120 |
| AN-07 | CRIT-05 | 4 | 121 | 200 |
| AN-08 | CRIT-05 | 3 | 201 | 300 |
| AN-09 | CRIT-05 | 2 | 301 | 450 |
| AN-10 | CRIT-05 | 1 | 451 | inf |
| AN-11 | CRIT-09 | 5 | 0 | 300 |
| AN-12 | CRIT-09 | 4 | 301 | 450 |
| AN-13 | CRIT-09 | 3 | 451 | 600 |
| AN-14 | CRIT-09 | 2 | 601 | 800 |
| AN-15 | CRIT-09 | 1 | 801 | inf |
| AN-16 | CRIT-10 | 5 | 0 | 4 |
| AN-17 | CRIT-10 | 4 | 5 | 6 |
| AN-18 | CRIT-10 | 3 | 7 | 9 |
| AN-19 | CRIT-10 | 2 | 10 | 12 |
| AN-20 | CRIT-10 | 1 | 13 | inf |
| AN-21 | CRIT-11 | 5 | 15 | inf |
| AN-22 | CRIT-11 | 4 | 10 | 14 |
| AN-23 | CRIT-11 | 3 | 6 | 9 |
| AN-24 | CRIT-11 | 2 | 3 | 5 |
| AN-25 | CRIT-11 | 1 | 0 | 2 |
| AN-26 | CRIT-13 | 5 | 0 | 200 |
| AN-27 | CRIT-13 | 4 | 201 | 300 |
| AN-28 | CRIT-13 | 3 | 301 | 450 |
| AN-29 | CRIT-13 | 2 | 451 | 600 |
| AN-30 | CRIT-13 | 1 | 601 | inf |
| AN-31 | CRIT-19 | 5 | 0 | 150 |
| AN-32 | CRIT-19 | 4 | 151 | 250 |
| AN-33 | CRIT-19 | 3 | 251 | 400 |
| AN-34 | CRIT-19 | 2 | 401 | 600 |
| AN-35 | CRIT-19 | 1 | 601 | inf |
| AN-36 | CRIT-20 | 5 | 0 | 4 |
| AN-37 | CRIT-20 | 4 | 5 | 6 |
| AN-38 | CRIT-20 | 3 | 7 | 9 |
| AN-39 | CRIT-20 | 2 | 10 | 12 |
| AN-40 | CRIT-20 | 1 | 13 | inf |
| AN-41 | CRIT-21 | 5 | 0 | 120 |
| AN-42 | CRIT-21 | 4 | 121 | 180 |
| AN-43 | CRIT-21 | 3 | 181 | 250 |
| AN-44 | CRIT-21 | 2 | 251 | 350 |
| AN-45 | CRIT-21 | 1 | 351 | inf |
| AN-46 | CRIT-22 | 5 | 0 | 4 |
| AN-47 | CRIT-22 | 4 | 5 | 6 |
| AN-48 | CRIT-22 | 3 | 7 | 8 |
| AN-49 | CRIT-22 | 2 | 9 | 10 |
| AN-50 | CRIT-22 | 1 | 11 | inf |
| AN-51 | CRIT-29 | 5 | 0 | 120 |
| AN-52 | CRIT-29 | 4 | 121 | 200 |
| AN-53 | CRIT-29 | 3 | 201 | 300 |
| AN-54 | CRIT-29 | 2 | 301 | 450 |
| AN-55 | CRIT-29 | 1 | 451 | inf |
| AN-56 | CRIT-31 | 5 | 0 | 1000 |
| AN-57 | CRIT-31 | 4 | 1001 | 1500 |
| AN-58 | CRIT-31 | 3 | 1501 | 1800 |
| AN-59 | CRIT-31 | 2 | 1801 | 2000 |
| AN-60 | CRIT-31 | 1 | 2001 | inf |
| AN-61 | CRIT-32 | 5 | 0 | 4 |
| AN-62 | CRIT-32 | 4 | 5 | 6 |
| AN-63 | CRIT-32 | 3 | 7 | 8 |
| AN-64 | CRIT-32 | 2 | 9 | 10 |
| AN-65 | CRIT-32 | 1 | 11 | inf |
| AN-66 | CRIT-33 | 5 | 25 | inf |
| AN-67 | CRIT-33 | 4 | 15 | 24 |
| AN-68 | CRIT-33 | 3 | 8 | 14 |
| AN-69 | CRIT-33 | 2 | 3 | 7 |
| AN-70 | CRIT-33 | 1 | 0 | 2 |
| AN-71 | CRIT-34 | 5 | 30 | inf |
| AN-72 | CRIT-34 | 4 | 20 | 29 |
| AN-73 | CRIT-34 | 3 | 10 | 19 |
| AN-74 | CRIT-34 | 2 | 1 | 9 |
| AN-75 | CRIT-34 | 1 | 0 | 0 |

#### Judgement anchors (ordinal; ratings 2 and 4 fall between the anchors)

| ID | Criterion | Anchor for 1 | Anchor for 3 | Anchor for 5 |
| --- | --- | --- | --- | --- |
| JA-01 | CRIT-02 | Owners unclear or contested for most sensitive assets | Owners clear for most; some contested | Attribute-level owners explicit and accepted |
| JA-02 | CRIT-03 | The organisation cannot run it | Runnable with training and central support | Runnable with today's skills |
| JA-03 | CRIT-04 | Definitions diverge across domains | Shared definitions with some drift | One governed definition per concept |
| JA-04 | CRIT-06 | Reconciliation and evidence are weak | Adequate with remediation | Controlled, reconciled and auditable |
| JA-05 | CRIT-07 | Serves few of the workloads | Serves most with workarounds | Serves all workloads naturally |
| JA-06 | CRIT-08 | Two stores with no authority boundary | Two stores with a stated boundary | One store of record per concept |
| JA-07 | CRIT-12 | Many moving parts and manual steps | Several components to run and monitor | Few components, established practice |
| JA-08 | CRIT-14 | Two logic paths to reconcile permanently | Some reconciliation needed | One path, one result |
| JA-09 | CRIT-15 | Skills do not exist and cannot be hired | Skills exist in part; training needed | Skills exist today |
| JA-10 | CRIT-16 | Consumers cannot find or interpret data | Consumers find priority data with help | Consumers self-serve with confidence |
| JA-11 | CRIT-17 | Evidence assembled by hand | Partly automated evidence | Evidence produced as a by-product |
| JA-12 | CRIT-18 | Metadata likely stale or wrong | Some stale entries expected | Metadata verified and owned |
| JA-13 | CRIT-23 | Fragile or unsupported | Moderate new work; runbooks needed | Established support model |
| JA-14 | CRIT-24 | Depends on an owner-less external change | Depends on an internal approval pending | No external dependency |
| JA-15 | CRIT-25 | Full records copied widely | Payload partly minimised | Minimal payload, bounded retention |
| JA-16 | CRIT-26 | Consumers coupled to physical schema | Changes announced, not enforced | Contracts enforced by checks |
| JA-17 | CRIT-27 | Consumers must ask the producer each time | Documented for priority consumers | Discoverable and self-service |
| JA-18 | CRIT-28 | Many interfaces to operate | A few interfaces to operate | A single simple mechanism |
| JA-19 | CRIT-30 | Deletion cannot be shown to reach copies | Deletion reaches most copies | Deletion enforced and evidenced |
| JA-20 | CRIT-35 | Needs capabilities that do not exist | Needs capabilities that can be built in the window | Fits current capability |
| JA-21 | CRIT-36 | Incidents cross many owners | Incidents cross a few owners | Single owner per incident |

#### Cost components (thousands of illustrative currency units; exit cost at the end of the three-year horizon)

| ID | Option | Build and migration | Three-year run and support | Exit | Total | Evidence | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TCO-01 | OPT-01 | 30 | 60 | 10 | 100 | Illustrative assumption | Planning estimate, not a quote |
| TCO-02 | OPT-02 | 70 | 130 | 20 | 220 | Illustrative assumption | Planning estimate, not a quote |
| TCO-03 | OPT-03 | 120 | 230 | 30 | 380 | Illustrative assumption | Planning estimate, not a quote |
| TCO-04 | OPT-04 | 300 | 520 | 80 | 900 | Illustrative assumption | Planning estimate, not a quote |
| TCO-05 | OPT-05 | 120 | 230 | 30 | 380 | Illustrative assumption | Planning estimate, not a quote |
| TCO-06 | OPT-06 | 150 | 280 | 50 | 480 | Illustrative assumption | Planning estimate, not a quote |
| TCO-07 | OPT-07 | 400 | 420 | 80 | 900 | Illustrative assumption | Planning estimate, not a quote |
| TCO-08 | OPT-08 | 170 | 310 | 40 | 520 | Illustrative assumption | Planning estimate, not a quote |
| TCO-09 | OPT-09 | 10 | 45 | 5 | 60 | Illustrative assumption | Planning estimate, not a quote |
| TCO-10 | OPT-10 | 70 | 130 | 20 | 220 | Illustrative assumption | Planning estimate, not a quote |
| TCO-11 | OPT-11 | 150 | 280 | 50 | 480 | Illustrative assumption | Planning estimate, not a quote |
| TCO-12 | OPT-12 | 220 | 330 | 50 | 600 | Illustrative assumption | Planning estimate, not a quote |
| TCO-13 | OPT-13 | 30 | 80 | 10 | 120 | Illustrative assumption | Planning estimate, not a quote |
| TCO-14 | OPT-14 | 90 | 170 | 20 | 280 | Illustrative assumption | Planning estimate, not a quote |
| TCO-15 | OPT-15 | 280 | 380 | 40 | 700 | Illustrative assumption | Planning estimate, not a quote |
| TCO-16 | OPT-16 | 40 | 100 | 10 | 150 | Illustrative assumption | Planning estimate, not a quote |
| TCO-17 | OPT-17 | 5 | 30 | 5 | 40 | Illustrative assumption | Planning estimate, not a quote |
| TCO-18 | OPT-18 | 40 | 70 | 10 | 120 | Illustrative assumption | Planning estimate, not a quote |
| TCO-19 | OPT-19 | 80 | 120 | 20 | 220 | Illustrative assumption | Planning estimate, not a quote |
| TCO-20 | OPT-20 | 70 | 100 | 20 | 190 | Illustrative assumption | Planning estimate, not a quote |
| TCO-21 | OPT-21 | 10 | 15 | 5 | 30 | Illustrative assumption | Planning estimate, not a quote |
| TCO-22 | OPT-22 | 30 | 60 | 10 | 100 | Illustrative assumption | Planning estimate, not a quote |
| TCO-23 | OPT-23 | 90 | 150 | 20 | 260 | Illustrative assumption | Planning estimate, not a quote |
| TCO-24 | OPT-24 | 200 | 190 | 30 | 420 | Illustrative assumption | Planning estimate, not a quote |

#### Delivery estimates (months to first production release)

| ID | Option | Delivery months | Evidence | Basis |
| --- | --- | --- | --- | --- |
| DL-01 | OPT-01 | 3 | Illustrative assumption | Team estimate, unvalidated |
| DL-02 | OPT-02 | 6 | Illustrative assumption | Team estimate, unvalidated |
| DL-03 | OPT-03 | 9 | Illustrative assumption | Team estimate, unvalidated |
| DL-04 | OPT-04 | 24 | Illustrative assumption | Team estimate, unvalidated |
| DL-05 | OPT-05 | 5 | Illustrative assumption | Team estimate, unvalidated |
| DL-06 | OPT-06 | 8 | Illustrative assumption | Team estimate, unvalidated |
| DL-07 | OPT-07 | 15 | Illustrative assumption | Team estimate, unvalidated |
| DL-08 | OPT-08 | 9 | Illustrative assumption | Team estimate, unvalidated |
| DL-09 | OPT-09 | 1 | Illustrative assumption | Team estimate, unvalidated |
| DL-10 | OPT-10 | 5 | Illustrative assumption | Team estimate, unvalidated |
| DL-11 | OPT-11 | 8 | Illustrative assumption | Team estimate, unvalidated |
| DL-12 | OPT-12 | 11 | Illustrative assumption | Team estimate, unvalidated |
| DL-13 | OPT-13 | 3 | Illustrative assumption | Team estimate, unvalidated |
| DL-14 | OPT-14 | 8 | Illustrative assumption | Team estimate, unvalidated |
| DL-15 | OPT-15 | 18 | Illustrative assumption | Team estimate, unvalidated |
| DL-16 | OPT-16 | 10 | Illustrative assumption | Team estimate, unvalidated |
| DL-17 | OPT-17 | 1 | Illustrative assumption | Team estimate, unvalidated |
| DL-18 | OPT-18 | 5 | Illustrative assumption | Team estimate, unvalidated |
| DL-19 | OPT-19 | 9 | Illustrative assumption | Team estimate, unvalidated |
| DL-20 | OPT-20 | 7 | Illustrative assumption | Team estimate, unvalidated |
| DL-21 | OPT-21 | 1 | Illustrative assumption | Team estimate, unvalidated |
| DL-22 | OPT-22 | 3 | Illustrative assumption | Team estimate, unvalidated |
| DL-23 | OPT-23 | 7 | Illustrative assumption | Team estimate, unvalidated |
| DL-24 | OPT-24 | 10 | Illustrative assumption | Team estimate, unvalidated |

#### Timing-budget stages (seconds; planning budgets, worst-case sequential, not measured p95)

For batch options the first stage is the maximum wait for the next file or interval, which is conservative.
A combination's budget is the sum of its members' stages.

| ID | Option | Stage | Seconds | Basis | Evidence |
| --- | --- | --- | --- | --- | --- |
| TB-01 | OPT-09 | batch interval wait | 86400 | Worst-case wait for the next nightly run | Illustrative assumption |
| TB-02 | OPT-09 | processing | 8 | Planning budget | Illustrative assumption |
| TB-03 | OPT-09 | target commit | 4 | Planning budget | Illustrative assumption |
| TB-04 | OPT-09 | publish | 3 | Planning budget | Illustrative assumption |
| TB-05 | OPT-10 | batch interval wait | 15 | Worst-case wait for the next micro-batch | Illustrative assumption |
| TB-06 | OPT-10 | processing | 8 | Planning budget | Illustrative assumption |
| TB-07 | OPT-10 | target commit | 4 | Planning budget | Illustrative assumption |
| TB-08 | OPT-10 | publish | 3 | Planning budget | Illustrative assumption |
| TB-09 | OPT-11 | processing | 8 | Planning budget | Illustrative assumption |
| TB-10 | OPT-11 | target commit | 4 | Planning budget | Illustrative assumption |
| TB-11 | OPT-11 | publish | 3 | Planning budget | Illustrative assumption |
| TB-12 | OPT-12 | processing | 8 | Speed-path planning budget | Illustrative assumption |
| TB-13 | OPT-12 | target commit | 4 | Planning budget | Illustrative assumption |
| TB-14 | OPT-12 | publish | 3 | Planning budget | Illustrative assumption |
| TB-15 | OPT-17 | source availability | 900 | Maximum wait for the next 15-minute file | Illustrative assumption |
| TB-16 | OPT-17 | transport | 3 | Planning budget | Illustrative assumption |
| TB-17 | OPT-17 | queue wait | 0 | Files are processed on arrival | Illustrative assumption |
| TB-18 | OPT-18 | source availability | 30 | Maximum wait for the next 30-second file | Illustrative assumption |
| TB-19 | OPT-18 | transport | 3 | Planning budget | Illustrative assumption |
| TB-20 | OPT-18 | queue wait | 0 | Files are processed on arrival | Illustrative assumption |
| TB-21 | OPT-19 | source availability | 5 | Event published at the card event | Illustrative assumption |
| TB-22 | OPT-19 | transport | 3 | Planning budget | Illustrative assumption |
| TB-23 | OPT-19 | queue wait | 4 | Planning budget | Illustrative assumption |
| TB-24 | OPT-20 | source availability | 6 | Capture lag from the source store's log | Illustrative assumption |
| TB-25 | OPT-20 | transport | 3 | Planning budget | Illustrative assumption |
| TB-26 | OPT-20 | queue wait | 4 | Planning budget | Illustrative assumption |

#### Component availability (illustrative provider statements, not measured)

A combination's serial availability is the product of its members' availabilities. Options on the
metadata axis and the operating-model axis carry no serving-path availability.

| ID | Option | Availability | Evidence | Basis |
| --- | --- | --- | --- | --- |
| AV-01 | OPT-05 | 0.9990 | Illustrative assumption | Provider statement, not measured |
| AV-02 | OPT-06 | 0.9990 | Illustrative assumption | Provider statement, not measured |
| AV-03 | OPT-07 | 0.9985 | Illustrative assumption | Provider statement, not measured |
| AV-04 | OPT-08 | 0.9990 | Illustrative assumption | Provider statement, not measured |
| AV-05 | OPT-09 | 0.9990 | Illustrative assumption | Provider statement, not measured |
| AV-06 | OPT-10 | 0.9990 | Illustrative assumption | Provider statement, not measured |
| AV-07 | OPT-11 | 0.9980 | Illustrative assumption | Provider statement, not measured |
| AV-08 | OPT-12 | 0.9975 | Illustrative assumption | Provider statement, not measured |
| AV-09 | OPT-17 | 0.9995 | Illustrative assumption | Provider statement, not measured |
| AV-10 | OPT-18 | 0.9990 | Illustrative assumption | Provider statement, not measured |
| AV-11 | OPT-19 | 0.9985 | Illustrative assumption | Provider statement, not measured |
| AV-12 | OPT-20 | 0.9985 | Illustrative assumption | Provider statement, not measured |
| AV-13 | OPT-21 | 0.9990 | Illustrative assumption | Provider statement, not measured |
| AV-14 | OPT-22 | 0.9995 | Illustrative assumption | Provider statement, not measured |
| AV-15 | OPT-23 | 0.9990 | Illustrative assumption | Provider statement, not measured |
| AV-16 | OPT-24 | 0.9980 | Illustrative assumption | Provider statement, not measured |

#### Gate results

`Value` is the number the gate tests, computed from its `Value source`: `TB` sum of timing stages;
`DL` delivery months (maximum for a combination); `TCO` summed cost; `AV` serial availability; `RD`
readiness total; `EST-nn` an estimate; `COMPAT` 1 if compatible; `AXIS` the number of members failing
their own axis gates; `stated` a given figure. `n/a` marks a qualitative gate. `Pending` means not yet
proven and becomes a decision condition. Numeric results are recomputed by the checker.

| ID | Gate | Option | Value | Value source | Result | Note |
| --- | --- | --- | --- | --- | --- | --- |
| GR-01 | GT-01 | OPT-01 | n/a | n/a | Pending | Owner and support route not yet confirmed with the domain heads |
| GR-02 | GT-01 | OPT-02 | n/a | n/a | Pending | Owner and support route not yet confirmed with the domain heads |
| GR-03 | GT-01 | OPT-03 | n/a | n/a | Pending | Owner and support route not yet confirmed with the domain heads |
| GR-04 | GT-01 | OPT-04 | n/a | n/a | Pending | Owner and support route not yet confirmed with the domain heads |
| GR-05 | GT-02 | OPT-01 | 9999 | EST-02 | Fail | Backlog forecast |
| GR-06 | GT-02 | OPT-02 | 54.5455 | EST-04 | Pass | Backlog forecast |
| GR-07 | GT-02 | OPT-03 | 27.907 | EST-06 | Pass | Backlog forecast |
| GR-08 | GT-03 | OPT-03 | 14 | RD | Pass | Sum of RD-01 to RD-10 |
| GR-09 | GT-04 | OPT-04 | 14 | RD | Fail | Sum of RD-01 to RD-10 |
| GR-10 | GT-05 | OPT-05 | n/a | n/a | Pending | Reconciliation baseline not yet measured (UNK-04) |
| GR-11 | GT-05 | OPT-06 | n/a | n/a | Pending | Reconciliation baseline not yet measured (UNK-04) |
| GR-12 | GT-05 | OPT-07 | n/a | n/a | Pending | Reconciliation baseline not yet measured (UNK-04) |
| GR-13 | GT-05 | OPT-08 | n/a | n/a | Pending | Reconciliation baseline not yet measured (UNK-04) |
| GR-14 | GT-06 | OPT-05 | 5 | DL | Pass | Delivery estimate |
| GR-15 | GT-06 | OPT-06 | 8 | DL | Pass | Delivery estimate |
| GR-16 | GT-06 | OPT-07 | 15 | DL | Fail | Delivery estimate |
| GR-17 | GT-06 | OPT-08 | 9 | DL | Pass | Delivery estimate |
| GR-18 | GT-07 | OPT-09 | 86415 | TB | Fail | Processing stages |
| GR-19 | GT-07 | OPT-10 | 30 | TB | Pass | Processing stages |
| GR-20 | GT-07 | OPT-11 | 15 | TB | Pass | Processing stages |
| GR-21 | GT-07 | OPT-12 | 15 | TB | Pass | Processing stages |
| GR-22 | GT-08 | OPT-09 | 5.39845 | EST-09 | Pass | Rebuild-time estimate |
| GR-23 | GT-08 | OPT-10 | 5.39845 | EST-09 | Pass | Rebuild-time estimate |
| GR-24 | GT-08 | OPT-11 | 20.2442 | EST-10 | Fail | Rebuild-time estimate |
| GR-25 | GT-08 | OPT-12 | 5.39845 | EST-09 | Pass | Rebuild-time estimate |
| GR-26 | GT-09 | OPT-13 | 91 | stated | Pass | Stated coverage (ASM-07) |
| GR-27 | GT-09 | OPT-14 | 94 | stated | Pass | Stated coverage (ASM-07) |
| GR-28 | GT-09 | OPT-15 | 96 | stated | Pass | Stated coverage (ASM-07) |
| GR-29 | GT-09 | OPT-16 | 85 | stated | Fail | Stated coverage (ASM-07) |
| GR-30 | GT-10 | OPT-13 | 3 | DL | Pass | Delivery estimate |
| GR-31 | GT-10 | OPT-14 | 8 | DL | Pass | Delivery estimate |
| GR-32 | GT-10 | OPT-15 | 18 | DL | Fail | Delivery estimate |
| GR-33 | GT-10 | OPT-16 | 10 | DL | Pass | Delivery estimate |
| GR-34 | GT-11 | OPT-17 | 903 | TB | Fail | Interaction stages |
| GR-35 | GT-11 | OPT-18 | 33 | TB | Pass | Interaction stages |
| GR-36 | GT-11 | OPT-19 | 12 | TB | Pass | Interaction stages |
| GR-37 | GT-11 | OPT-20 | 13 | TB | Pass | Interaction stages |
| GR-38 | GT-12 | OPT-17 | n/a | n/a | Pending | Security and compliance review not yet performed |
| GR-39 | GT-12 | OPT-18 | n/a | n/a | Pending | Security and compliance review not yet performed |
| GR-40 | GT-12 | OPT-19 | n/a | n/a | Pending | Security and compliance review not yet performed |
| GR-41 | GT-12 | OPT-20 | n/a | n/a | Pending | Security and compliance review not yet performed |
| GR-42 | GT-13 | OPT-21 | n/a | n/a | Fail | Consumers depend on the producer's physical schema and workload |
| GR-43 | GT-13 | OPT-22 | n/a | n/a | Pass | Consumers read bounded exports, not producer tables |
| GR-44 | GT-13 | OPT-23 | n/a | n/a | Pass | Consumers use a contract-governed interface |
| GR-45 | GT-13 | OPT-24 | n/a | n/a | Pass | Consumers use published events, not producer tables |
| GR-46 | GT-14 | OPT-21 | n/a | n/a | Pending | Copy inventory and deletion drill not yet performed |
| GR-47 | GT-14 | OPT-22 | n/a | n/a | Pending | Copy inventory and deletion drill not yet performed |
| GR-48 | GT-14 | OPT-23 | n/a | n/a | Pending | Copy inventory and deletion drill not yet performed |
| GR-49 | GT-14 | OPT-24 | n/a | n/a | Pending | Copy inventory and deletion drill not yet performed |
| GR-50 | GT-15 | OPT-25 | 1 | COMPAT | Pass | Requires and Conflicts columns |
| GR-51 | GT-15 | OPT-26 | 1 | COMPAT | Pass | Requires and Conflicts columns |
| GR-52 | GT-15 | OPT-27 | 1 | COMPAT | Pass | Requires and Conflicts columns |
| GR-53 | GT-15 | OPT-28 | 1 | COMPAT | Pass | Requires and Conflicts columns |
| GR-54 | GT-15 | OPT-29 | 1 | COMPAT | Pass | Requires and Conflicts columns |
| GR-55 | GT-15 | OPT-30 | 1 | COMPAT | Pass | Requires and Conflicts columns |
| GR-56 | GT-15 | OPT-31 | 0 | COMPAT | Fail | Requires and Conflicts columns |
| GR-57 | GT-16 | OPT-25 | 4 | AXIS | Fail | Members that fail their own axis gates |
| GR-58 | GT-16 | OPT-26 | 0 | AXIS | Pass | Members that fail their own axis gates |
| GR-59 | GT-16 | OPT-27 | 0 | AXIS | Pass | Members that fail their own axis gates |
| GR-60 | GT-16 | OPT-28 | 0 | AXIS | Pass | Members that fail their own axis gates |
| GR-61 | GT-16 | OPT-29 | 0 | AXIS | Pass | Members that fail their own axis gates |
| GR-62 | GT-16 | OPT-30 | 0 | AXIS | Pass | Members that fail their own axis gates |
| GR-63 | GT-16 | OPT-31 | 4 | AXIS | Fail | Members that fail their own axis gates |
| GR-64 | GT-17 | OPT-25 | 87318 | TB | Fail | Sum of members' timing stages |
| GR-65 | GT-17 | OPT-26 | 43 | TB | Pass | Sum of members' timing stages |
| GR-66 | GT-17 | OPT-27 | 42 | TB | Pass | Sum of members' timing stages |
| GR-67 | GT-17 | OPT-28 | 43 | TB | Pass | Sum of members' timing stages |
| GR-68 | GT-17 | OPT-29 | 27 | TB | Pass | Sum of members' timing stages |
| GR-69 | GT-17 | OPT-30 | 63 | TB | Fail | Sum of members' timing stages |
| GR-70 | GT-17 | OPT-31 | 42 | TB | Pass | Sum of members' timing stages |
| GR-71 | GT-18 | OPT-25 | 0.996504 | AV | Pass | Product of members' availabilities |
| GR-72 | GT-18 | OPT-26 | 0.995507 | AV | Pass | Product of members' availabilities |
| GR-73 | GT-18 | OPT-27 | 0.995507 | AV | Pass | Product of members' availabilities |
| GR-74 | GT-18 | OPT-28 | 0.995507 | AV | Pass | Product of members' availabilities |
| GR-75 | GT-18 | OPT-29 | 0.994013 | AV | Fail | Product of members' availabilities |
| GR-76 | GT-18 | OPT-30 | 0.996006 | AV | Pass | Product of members' availabilities |
| GR-77 | GT-18 | OPT-31 | 0.990536 | AV | Fail | Product of members' availabilities |
| GR-78 | GT-19 | OPT-25 | 730 | TCO | Pass | Sum of members' costs |
| GR-79 | GT-19 | OPT-26 | 1650 | TCO | Pass | Sum of members' costs |
| GR-80 | GT-19 | OPT-27 | 1680 | TCO | Pass | Sum of members' costs |
| GR-81 | GT-19 | OPT-28 | 1810 | TCO | Pass | Sum of members' costs |
| GR-82 | GT-19 | OPT-29 | 2060 | TCO | Fail | Sum of members' costs |
| GR-83 | GT-19 | OPT-30 | 1580 | TCO | Pass | Sum of members' costs |
| GR-84 | GT-19 | OPT-31 | 4220 | TCO | Fail | Sum of members' costs |
| GR-85 | GT-20 | OPT-25 | 5 | DL | Pass | Slowest member |
| GR-86 | GT-20 | OPT-26 | 8 | DL | Pass | Slowest member |
| GR-87 | GT-20 | OPT-27 | 9 | DL | Pass | Slowest member |
| GR-88 | GT-20 | OPT-28 | 9 | DL | Pass | Slowest member |
| GR-89 | GT-20 | OPT-29 | 11 | DL | Pass | Slowest member |
| GR-90 | GT-20 | OPT-30 | 8 | DL | Pass | Slowest member |
| GR-91 | GT-20 | OPT-31 | 24 | DL | Fail | Slowest member |

#### Option inputs and ratings

This table is the comparison matrix in long form: one row per option and criterion, with the input, the
rating and the evidence. Rows for options that are ineligible in the base case are included only so that
the sensitivity cases in Section 6.6 can score them if a gate result changes; they carry no base score.
`TBM` is the gate threshold minus the timing total; `AVM` is the availability above the gate threshold in
basis points; `judgement` is an ordinal rating with a written basis.

| ID | Decision | Option | Criterion | Input value | Unit | Value source | Rating | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OI-01 | DEC-01 | OPT-01 | CRIT-01 | 9999 | weeks | EST-02 | 1 | Estimate EST-02 |
| OI-02 | DEC-01 | OPT-01 | CRIT-02 | judgement | n/a | judgement | 2 | Central team owns everything; owners for sensitive assets stay unclear |
| OI-03 | DEC-01 | OPT-01 | CRIT-03 | judgement | n/a | judgement | 4 | Existing team and practices |
| OI-04 | DEC-01 | OPT-01 | CRIT-04 | judgement | n/a | judgement | 4 | One central definition set |
| OI-05 | DEC-01 | OPT-01 | CRIT-05 | 100 | k currency | TCO | 5 | Cost components table |
| OI-06 | DEC-01 | OPT-02 | CRIT-01 | 54.5455 | weeks | EST-04 | 3 | Estimate EST-04 |
| OI-07 | DEC-01 | OPT-02 | CRIT-02 | judgement | n/a | judgement | 4 | Domain stewards own definitions; the central forum resolves disputes |
| OI-08 | DEC-01 | OPT-02 | CRIT-03 | judgement | n/a | judgement | 4 | Operation stays central; domains take definition work only |
| OI-09 | DEC-01 | OPT-02 | CRIT-04 | judgement | n/a | judgement | 4 | Central governance keeps shared definitions |
| OI-10 | DEC-01 | OPT-02 | CRIT-05 | 220 | k currency | TCO | 3 | Cost components table |
| OI-11 | DEC-01 | OPT-03 | CRIT-01 | 27.907 | weeks | EST-06 | 4 | Estimate EST-06 |
| OI-12 | DEC-01 | OPT-03 | CRIT-02 | judgement | n/a | judgement | 4 | Product owners are accountable per dataset |
| OI-13 | DEC-01 | OPT-03 | CRIT-03 | judgement | n/a | judgement | 2 | Readiness is 14 of 30; domain skills are uneven; platform support is unproven |
| OI-14 | DEC-01 | OPT-03 | CRIT-04 | judgement | n/a | judgement | 3 | Contracts help but definitions can drift between domains |
| OI-15 | DEC-01 | OPT-03 | CRIT-05 | 380 | k currency | TCO | 2 | Cost components table |
| OI-16 | DEC-02 | OPT-05 | CRIT-06 | judgement | n/a | judgement | 3 | Reporting stays on the warehouse; trust unmeasured (UNK-04) |
| OI-17 | DEC-02 | OPT-05 | CRIT-07 | judgement | n/a | judgement | 3 | The lake exists but is untrusted for the fraud and document workloads |
| OI-18 | DEC-02 | OPT-05 | CRIT-08 | judgement | n/a | judgement | 2 | Two stores with unclear authority |
| OI-19 | DEC-02 | OPT-05 | CRIT-09 | 380 | k currency | TCO | 4 | Cost components table |
| OI-20 | DEC-02 | OPT-05 | CRIT-10 | 5 | months | DL | 4 | Delivery estimate table |
| OI-21 | DEC-02 | OPT-06 | CRIT-06 | judgement | n/a | judgement | 4 | Warehouse is the governed core with reconciliation |
| OI-22 | DEC-02 | OPT-06 | CRIT-07 | judgement | n/a | judgement | 4 | Lake zones serve fraud history and documents with owners |
| OI-23 | DEC-02 | OPT-06 | CRIT-08 | judgement | n/a | judgement | 3 | Two stores with a stated authority boundary |
| OI-24 | DEC-02 | OPT-06 | CRIT-09 | 480 | k currency | TCO | 3 | Cost components table |
| OI-25 | DEC-02 | OPT-06 | CRIT-10 | 8 | months | DL | 3 | Delivery estimate table |
| OI-26 | DEC-02 | OPT-07 | CRIT-06 | judgement | n/a | judgement | 4 | Managed tables can be governed if semantics are fixed first |
| OI-27 | DEC-02 | OPT-07 | CRIT-07 | judgement | n/a | judgement | 5 | Varied data on one managed foundation |
| OI-28 | DEC-02 | OPT-07 | CRIT-08 | judgement | n/a | judgement | 4 | One foundation if the old stores are retired |
| OI-29 | DEC-02 | OPT-07 | CRIT-09 | 900 | k currency | TCO | 1 | Cost components table |
| OI-30 | DEC-02 | OPT-07 | CRIT-10 | 15 | months | DL | 1 | Delivery estimate table |
| OI-31 | DEC-02 | OPT-08 | CRIT-06 | judgement | n/a | judgement | 4 | Single governed store |
| OI-32 | DEC-02 | OPT-08 | CRIT-07 | judgement | n/a | judgement | 2 | Unstructured and training workloads do not fit the warehouse |
| OI-33 | DEC-02 | OPT-08 | CRIT-08 | judgement | n/a | judgement | 4 | One store of record |
| OI-34 | DEC-02 | OPT-08 | CRIT-09 | 520 | k currency | TCO | 3 | Cost components table |
| OI-35 | DEC-02 | OPT-08 | CRIT-10 | 9 | months | DL | 3 | Delivery estimate table |
| OI-36 | DEC-03 | OPT-10 | CRIT-11 | 5 | seconds | TBM | 2 | Gate threshold minus the timing total |
| OI-37 | DEC-03 | OPT-10 | CRIT-12 | judgement | n/a | judgement | 4 | Few components; incremental jobs plus an existing batch recompute |
| OI-38 | DEC-03 | OPT-10 | CRIT-13 | 220 | k currency | TCO | 4 | Cost components table |
| OI-39 | DEC-03 | OPT-10 | CRIT-14 | judgement | n/a | judgement | 4 | Recompute from raw is the authoritative result |
| OI-40 | DEC-03 | OPT-10 | CRIT-15 | judgement | n/a | judgement | 4 | Batch and incremental skills exist |
| OI-41 | DEC-03 | OPT-11 | CRIT-11 | 20 | seconds | TBM | 5 | Gate threshold minus the timing total |
| OI-42 | DEC-03 | OPT-11 | CRIT-12 | judgement | n/a | judgement | 3 | Continuous operation, state and log retention to run |
| OI-43 | DEC-03 | OPT-11 | CRIT-13 | 480 | k currency | TCO | 2 | Cost components table |
| OI-44 | DEC-03 | OPT-11 | CRIT-14 | judgement | n/a | judgement | 3 | One path, but replay side effects need care |
| OI-45 | DEC-03 | OPT-11 | CRIT-15 | judgement | n/a | judgement | 2 | Stream state and replay skills are scarce |
| OI-46 | DEC-03 | OPT-12 | CRIT-11 | 20 | seconds | TBM | 5 | Gate threshold minus the timing total |
| OI-47 | DEC-03 | OPT-12 | CRIT-12 | judgement | n/a | judgement | 2 | Two paths, reconciliation and a serving merge to run |
| OI-48 | DEC-03 | OPT-12 | CRIT-13 | 600 | k currency | TCO | 2 | Cost components table |
| OI-49 | DEC-03 | OPT-12 | CRIT-14 | judgement | n/a | judgement | 2 | Two logic paths must be reconciled permanently |
| OI-50 | DEC-03 | OPT-12 | CRIT-15 | judgement | n/a | judgement | 2 | Needs both batch and stream skills |
| OI-51 | DEC-04 | OPT-13 | CRIT-16 | judgement | n/a | judgement | 2 | A spreadsheet catalogue is hard to search and keep current |
| OI-52 | DEC-04 | OPT-13 | CRIT-17 | judgement | n/a | judgement | 1 | Evidence is assembled by hand |
| OI-53 | DEC-04 | OPT-13 | CRIT-18 | judgement | n/a | judgement | 3 | Manual entries go stale after change |
| OI-54 | DEC-04 | OPT-13 | CRIT-19 | 120 | k currency | TCO | 5 | Cost components table |
| OI-55 | DEC-04 | OPT-13 | CRIT-20 | 3 | months | DL | 5 | Delivery estimate table |
| OI-56 | DEC-04 | OPT-14 | CRIT-16 | judgement | n/a | judgement | 4 | Priority datasets are described, owned and searchable |
| OI-57 | DEC-04 | OPT-14 | CRIT-17 | judgement | n/a | judgement | 3 | Lineage and ownership evidence partly automated |
| OI-58 | DEC-04 | OPT-14 | CRIT-18 | judgement | n/a | judgement | 4 | Owners approve metadata; freshness is measured |
| OI-59 | DEC-04 | OPT-14 | CRIT-19 | 280 | k currency | TCO | 3 | Cost components table |
| OI-60 | DEC-04 | OPT-14 | CRIT-20 | 8 | months | DL | 3 | Delivery estimate table |
| OI-61 | DEC-05 | OPT-18 | CRIT-21 | 120 | k currency | TCO | 5 | Cost components table |
| OI-62 | DEC-05 | OPT-18 | CRIT-22 | 5 | months | DL | 4 | Delivery estimate table |
| OI-63 | DEC-05 | OPT-18 | CRIT-23 | judgement | n/a | judgement | 4 | Simple files; file count must be managed |
| OI-64 | DEC-05 | OPT-18 | CRIT-24 | judgement | n/a | judgement | 2 | Needs the card platform to emit 30-second files (DEP-01) |
| OI-65 | DEC-05 | OPT-18 | CRIT-25 | judgement | n/a | judgement | 3 | Full file records, bounded retention |
| OI-66 | DEC-05 | OPT-19 | CRIT-21 | 220 | k currency | TCO | 3 | Cost components table |
| OI-67 | DEC-05 | OPT-19 | CRIT-22 | 9 | months | DL | 2 | Delivery estimate table |
| OI-68 | DEC-05 | OPT-19 | CRIT-23 | judgement | n/a | judgement | 2 | Contract, schema and replay duties fall on the source team |
| OI-69 | DEC-05 | OPT-19 | CRIT-24 | judgement | n/a | judgement | 2 | Needs the card platform to publish events (DEP-01) |
| OI-70 | DEC-05 | OPT-19 | CRIT-25 | judgement | n/a | judgement | 3 | Payload can be designed minimal |
| OI-71 | DEC-05 | OPT-20 | CRIT-21 | 190 | k currency | TCO | 3 | Cost components table |
| OI-72 | DEC-05 | OPT-20 | CRIT-22 | 7 | months | DL | 3 | Delivery estimate table |
| OI-73 | DEC-05 | OPT-20 | CRIT-23 | judgement | n/a | judgement | 3 | Capture lag, log retention and schema-change handling to monitor |
| OI-74 | DEC-05 | OPT-20 | CRIT-24 | judgement | n/a | judgement | 3 | Needs an internal approval for log access (DEP-02) |
| OI-75 | DEC-05 | OPT-20 | CRIT-25 | judgement | n/a | judgement | 2 | Log changes carry full records; filtering is needed |
| OI-76 | DEC-06 | OPT-22 | CRIT-26 | judgement | n/a | judgement | 3 | Layout changes are announced but not enforced |
| OI-77 | DEC-06 | OPT-22 | CRIT-27 | judgement | n/a | judgement | 2 | Consumers ask the producer for each export |
| OI-78 | DEC-06 | OPT-22 | CRIT-28 | judgement | n/a | judgement | 5 | One simple mechanism |
| OI-79 | DEC-06 | OPT-22 | CRIT-29 | 100 | k currency | TCO | 5 | Cost components table |
| OI-80 | DEC-06 | OPT-22 | CRIT-30 | judgement | n/a | judgement | 4 | Bounded exports are easy to delete |
| OI-81 | DEC-06 | OPT-23 | CRIT-26 | judgement | n/a | judgement | 5 | Contracts are checked before release |
| OI-82 | DEC-06 | OPT-23 | CRIT-27 | judgement | n/a | judgement | 5 | Discoverable with a documented contract |
| OI-83 | DEC-06 | OPT-23 | CRIT-28 | judgement | n/a | judgement | 3 | Contracts and checks to run for selected datasets |
| OI-84 | DEC-06 | OPT-23 | CRIT-29 | 260 | k currency | TCO | 3 | Cost components table |
| OI-85 | DEC-06 | OPT-23 | CRIT-30 | judgement | n/a | judgement | 4 | Access workflow and lifecycle in the contract |
| OI-86 | DEC-06 | OPT-24 | CRIT-26 | judgement | n/a | judgement | 4 | Event contracts, but many of them |
| OI-87 | DEC-06 | OPT-24 | CRIT-27 | judgement | n/a | judgement | 3 | Consumers must build their own state |
| OI-88 | DEC-06 | OPT-24 | CRIT-28 | judgement | n/a | judgement | 2 | Many channels and consumer stores to operate |
| OI-89 | DEC-06 | OPT-24 | CRIT-29 | 420 | k currency | TCO | 2 | Cost components table |
| OI-90 | DEC-06 | OPT-24 | CRIT-30 | judgement | n/a | judgement | 2 | Fan-out copies are hard to delete |
| OI-91 | DEC-07 | OPT-26 | CRIT-31 | 1650 | k currency | TCO | 3 | Cost components table |
| OI-92 | DEC-07 | OPT-26 | CRIT-32 | 8 | months | DL | 3 | Delivery estimate table |
| OI-93 | DEC-07 | OPT-26 | CRIT-33 | 17 | seconds | TBM | 4 | Gate threshold minus the timing total |
| OI-94 | DEC-07 | OPT-26 | CRIT-34 | 5.07495 | basis points | AVM | 2 | Serial availability above the gate threshold |
| OI-95 | DEC-07 | OPT-26 | CRIT-35 | judgement | n/a | judgement | 4 | Fits current capability with central operation |
| OI-96 | DEC-07 | OPT-26 | CRIT-36 | judgement | n/a | judgement | 3 | Incidents cross the source, capture, micro-batch and warehouse owners |
| OI-97 | DEC-07 | OPT-27 | CRIT-31 | 1680 | k currency | TCO | 3 | Cost components table |
| OI-98 | DEC-07 | OPT-27 | CRIT-32 | 9 | months | DL | 2 | Delivery estimate table |
| OI-99 | DEC-07 | OPT-27 | CRIT-33 | 18 | seconds | TBM | 4 | Gate threshold minus the timing total |
| OI-100 | DEC-07 | OPT-27 | CRIT-34 | 5.07495 | basis points | AVM | 2 | Serial availability above the gate threshold |
| OI-101 | DEC-07 | OPT-27 | CRIT-35 | judgement | n/a | judgement | 3 | Needs the card platform team to build event publication |
| OI-102 | DEC-07 | OPT-27 | CRIT-36 | judgement | n/a | judgement | 3 | Incidents cross the source, channel, micro-batch and warehouse owners |
| OI-103 | DEC-07 | OPT-28 | CRIT-31 | 1810 | k currency | TCO | 2 | Cost components table |
| OI-104 | DEC-07 | OPT-28 | CRIT-32 | 9 | months | DL | 2 | Delivery estimate table |
| OI-105 | DEC-07 | OPT-28 | CRIT-33 | 17 | seconds | TBM | 4 | Gate threshold minus the timing total |
| OI-106 | DEC-07 | OPT-28 | CRIT-34 | 5.07495 | basis points | AVM | 2 | Serial availability above the gate threshold |
| OI-107 | DEC-07 | OPT-28 | CRIT-35 | judgement | n/a | judgement | 2 | Needs domain operation of products before readiness is proven |
| OI-108 | DEC-07 | OPT-28 | CRIT-36 | judgement | n/a | judgement | 2 | Incidents cross domain product teams and the platform |
| OI-109 | DEC-07 | OPT-30 | CRIT-31 | 1580 | k currency | TCO | 3 | Cost components table |
| OI-110 | DEC-07 | OPT-30 | CRIT-32 | 8 | months | DL | 3 | Delivery estimate table |
| OI-111 | DEC-07 | OPT-30 | CRIT-33 | -3 | seconds | TBM | n/a | Gate threshold minus the timing total |
| OI-112 | DEC-07 | OPT-30 | CRIT-34 | 10.06 | basis points | AVM | 3 | Serial availability above the gate threshold |
| OI-113 | DEC-07 | OPT-30 | CRIT-35 | judgement | n/a | judgement | 4 | Fits current capability |
| OI-114 | DEC-07 | OPT-30 | CRIT-36 | judgement | n/a | judgement | 4 | Fewer moving parts in the feed |

#### Scores

Weighted score = Σ weight × rating. Ineligible options carry no score.

| ID | Decision | Option | Eligible | Weighted score | Rank | Scored in week |
| --- | --- | --- | --- | --- | --- | --- |
| SC-01 | DEC-01 | OPT-01 | No | n/a | n/a | 5 |
| SC-02 | DEC-01 | OPT-02 | Yes | 3.60 | 1 | 5 |
| SC-03 | DEC-01 | OPT-03 | Yes | 3.15 | 2 | 5 |
| SC-04 | DEC-01 | OPT-04 | No | n/a | n/a | 5 |
| SC-05 | DEC-02 | OPT-05 | Yes | 3.20 | 2 | 5 |
| SC-06 | DEC-02 | OPT-06 | Yes | 3.50 | 1 | 5 |
| SC-07 | DEC-02 | OPT-07 | No | n/a | n/a | 5 |
| SC-08 | DEC-02 | OPT-08 | Yes | 3.05 | 3 | 5 |
| SC-09 | DEC-03 | OPT-09 | No | n/a | n/a | 5 |
| SC-10 | DEC-03 | OPT-10 | Yes | 3.60 | 1 | 5 |
| SC-11 | DEC-03 | OPT-11 | No | n/a | n/a | 5 |
| SC-12 | DEC-03 | OPT-12 | Yes | 2.60 | 2 | 5 |
| SC-13 | DEC-04 | OPT-13 | Yes | 3.00 | 2 | 5 |
| SC-14 | DEC-04 | OPT-14 | Yes | 3.45 | 1 | 5 |
| SC-15 | DEC-04 | OPT-15 | No | n/a | n/a | 5 |
| SC-16 | DEC-04 | OPT-16 | No | n/a | n/a | 5 |
| SC-17 | DEC-05 | OPT-17 | No | n/a | n/a | 5 |
| SC-18 | DEC-05 | OPT-18 | Yes | 3.70 | 1 | 5 |
| SC-19 | DEC-05 | OPT-19 | Yes | 2.40 | 3 | 5 |
| SC-20 | DEC-05 | OPT-20 | Yes | 2.85 | 2 | 5 |
| SC-21 | DEC-06 | OPT-21 | No | n/a | n/a | 5 |
| SC-22 | DEC-06 | OPT-22 | Yes | 3.60 | 2 | 5 |
| SC-23 | DEC-06 | OPT-23 | Yes | 4.15 | 1 | 5 |
| SC-24 | DEC-06 | OPT-24 | Yes | 2.75 | 3 | 5 |
| SC-25 | DEC-07 | OPT-25 | No | n/a | n/a | 5 |
| SC-26 | DEC-07 | OPT-26 | Yes | 3.25 | 1 | 5 |
| SC-27 | DEC-07 | OPT-27 | Yes | 2.90 | 2 | 5 |
| SC-28 | DEC-07 | OPT-28 | Yes | 2.30 | 3 | 5 |
| SC-29 | DEC-07 | OPT-29 | No | n/a | n/a | 5 |
| SC-30 | DEC-07 | OPT-30 | No | n/a | n/a | 5 |
| SC-31 | DEC-07 | OPT-31 | No | n/a | n/a | 5 |


### 6.6 D6 — Architecture trade-off analysis (Step 12)

#### Sensitivity analysis

For each decision the least certain inputs were varied one at a time, then the weights were stressed.
Gates are rechecked in every case, so a weighted score can never rescue an option that fails a gate.
Kinds: `stage` replaces a timing stage for every option that has it; `oi` replaces a numeric option
input; `rating` replaces a judgement rating; `weight` replaces one weight and rescales the others
proportionally; `inp` replaces an estimation input and recomputes the estimates; `threshold` replaces a
gate threshold; `gatevalue` replaces a stated gate value for the named options.

| ID | Decision | Kind | Target | Value | Case | Winner | Winner score | Runner-up score | Interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SEN-01 | DEC-01 | inp | INP-05 | 0.15 | Domains absorb 15% of requests, not 30% | OPT-03 | 3.15 | n/a | Flip: OPT-02 fails GT-02 (clearance about 1,200 weeks); only OPT-03 remains |
| SEN-02 | DEC-01 | inp | INP-06 | 0.25 | Domains absorb 25% under domain-operated products, not 45% | OPT-02 | 3.60 | n/a | Flip: OPT-03 fails GT-02 (80 weeks against 78); OPT-02 remains |
| SEN-03 | DEC-01 | inp | INP-02 | 16 | Demand is 16 requests per week, not 14 | OPT-03 | 3.15 | n/a | Flip: OPT-02 fails GT-02 (150 weeks); only OPT-03 remains |
| SEN-04 | DEC-01 | threshold | GT-03 | 15 | The pilot readiness threshold is 15 points | OPT-02 | 3.60 | n/a | Flip: OPT-03 fails GT-03 at 15 points; OPT-02 remains |
| SEN-05 | DEC-01 | inp | INP-04 | 0.30 | Prioritisation lifts central capacity by 30% (beyond the plausible range) | OPT-02 | 3.60 | 3.15 | Stable: OPT-01 becomes eligible (75 weeks) but ranks level with OPT-03, behind OPT-02 |
| SEN-06 | DEC-01 | rating | OPT-03/CRIT-03 | 3 | Readiness fit of OPT-03 is better than assumed | OPT-02 | 3.60 | 3.35 | Stable: OPT-02 leads by 0.25 |
| SEN-07 | DEC-01 | weight | CRIT-01 | 0.45 | Backlog clearance carries a weight of 0.45 | OPT-02 | 3.44 | 3.38 | Stable but close: margin 0.06 is below the 0.15 close-call threshold |
| SEN-08 | DEC-02 | threshold | GT-06 | 15 | The regulatory milestone allows 15 months | OPT-06 | 3.50 | 3.25 | Stable: OPT-07 becomes eligible and ranks second (3.25) behind OPT-06 |
| SEN-09 | DEC-02 | rating | OPT-06/CRIT-07 | 3 | Workload fit of OPT-06 is weaker than assumed | tie | 3.20 | 3.20 | Flip point: OPT-06 and OPT-05 tie if workload fit is rated 3 |
| SEN-10 | DEC-02 | oi | OPT-06/CRIT-09 | 620 | OPT-06 cost rises about 30% | OPT-06 | 3.30 | 3.20 | Stable but close: margin 0.10 is below the 0.15 close-call threshold |
| SEN-11 | DEC-03 | inp | INP-10 | 120 | Batch recompute sustains 120 MB/s, not 300 | none | n/a | n/a | Flip: no option rebuilds history in 12 hours at 120 MB/s (13.5 hours) |
| SEN-12 | DEC-03 | inp | INP-11 | 150 | Stream replay sustains 150 MB/s, not 80 | OPT-10 | 3.60 | 3.10 | Stable: OPT-11 becomes eligible (10.8 hours) but ranks second (3.10) |
| SEN-13 | DEC-03 | stage | processing | 20 | The processing stage takes 20 s, not 8 | OPT-12 | 2.20 | n/a | Flip: OPT-10 fails GT-07 (42 s against 35 s); only OPT-12 remains |
| SEN-14 | DEC-03 | weight | CRIT-12 | 0.50 | Operational complexity carries a weight of 0.50 | OPT-10 | 3.71 | 2.43 | Stable: OPT-10 leads by 1.28 |
| SEN-15 | DEC-04 | gatevalue | GT-09/OPT-13 | 85 | Steward-curated lineage covers 85%, not 91% | OPT-14 | 3.45 | n/a | Flip: OPT-13 fails GT-09; only OPT-14 remains |
| SEN-16 | DEC-04 | oi | OPT-14/CRIT-19 | 400 | OPT-14 cost rises about 40% | OPT-14 | 3.45 | 3.00 | Stable: OPT-14 leads by 0.45 |
| SEN-17 | DEC-05 | rating | OPT-18/CRIT-24 | 1 | The card platform cannot commit to 30-second files | OPT-18 | 3.50 | 2.85 | Stable: OPT-18 stays first on its axis, but it still does not compose (OPT-30) |
| SEN-18 | DEC-05 | threshold | GT-11 | 30 | The interaction-side budget is 30 s, not 35 | OPT-20 | 2.85 | 2.40 | Flip: OPT-18 fails GT-11 (33 s against 30 s); OPT-20 ranks first of the rest |
| SEN-19 | DEC-05 | weight | CRIT-21 | 0.50 | Cost carries a weight of 0.50 | OPT-18 | 4.13 | 2.90 | Stable: OPT-18 stays first on its axis |
| SEN-20 | DEC-06 | oi | OPT-23/CRIT-29 | 400 | OPT-23 cost rises about 55% | OPT-23 | 4.00 | 3.60 | Stable: OPT-23 leads by 0.40 |
| SEN-21 | DEC-06 | rating | OPT-23/CRIT-28 | 2 | OPT-23 is operationally heavier than assumed | OPT-23 | 3.95 | 3.60 | Stable: OPT-23 leads by 0.35 |
| SEN-22 | DEC-07 | stage | batch interval wait | 10 | The micro-batch interval is 10 s, not 15 | OPT-26 | 3.25 | 3.05 | Stable: OPT-30 becomes eligible (58 s) but ranks second (3.05) behind OPT-26 |
| SEN-23 | DEC-07 | weight | CRIT-35 | 0.40 | Readiness fit carries a weight of 0.40 | OPT-26 | 3.44 | 2.92 | Stable: OPT-26 leads by 0.52 |
| SEN-24 | DEC-07 | threshold | GT-19 | 1600 | The cost ceiling is 1,600, not 2,000 | none | n/a | n/a | Flip: no combination meets a 1,600 ceiling; OPT-26 costs 1,650 |
| SEN-25 | DEC-07 | rating | OPT-26/CRIT-36 | 2 | OPT-26 is harder to diagnose than assumed | OPT-26 | 3.10 | 2.90 | Stable but not wide: OPT-26 leads by 0.20 |

**What the analysis says**

- **DEC-01.** The choice of OPT-02 depends on domain absorption (INP-05) and demand (INP-02), both
  `guessed` or `estimated`. OPT-02 passes the backlog gate only if domains absorb about 26% of requests or
  more; OPT-03 has the same threshold. Below it, the central backlog does not drain in time (SEN-01, SEN-02,
  SEN-03). The ranking itself is stable once both are eligible (SEN-06, SEN-07).
- **DEC-02.** OPT-06 leads by 0.30. A one-point change in its workload-fit rating produces a tie with the
  baseline (SEN-09), and a 30% cost rise narrows the margin to 0.10 (SEN-10): the decision is real but not
  wide. A longer milestone brings OPT-07 into play but does not make it win (SEN-08).
- **DEC-03.** OPT-10 leads clearly, but the *gate* is fragile: batch recompute below about 135 MB/s
  removes every option (SEN-11) and a processing stage above about 13 s removes OPT-10 (SEN-13). Single-path
  stream replay becomes eligible at 150 MB/s but still ranks second (SEN-12).
- **DEC-04.** OPT-14 leads by 0.45; the steward-curated baseline survives only if it keeps 90% lineage
  coverage (SEN-15).
- **DEC-05.** OPT-18 stays first on its axis in every non-gate case (SEN-17, SEN-19), but it does not compose
  with the processing choice (Section 6.9). Tightening the interaction budget to 30 s removes it (SEN-18).
- **DEC-06.** OPT-23 leads by at least 0.35 in every case.
- **DEC-07.** OPT-26 leads in every case where any combination is eligible (SEN-22, SEN-23, SEN-25). A cost
  ceiling below 1,650 removes every combination (SEN-24): the ceiling (UNK-02) is a blocking unknown.

#### Costs, reversibility and what is traded away

| Decision | Selected option | Three-year cost or key figure | Cost of the baseline | Reversibility | What is traded away |
| --- | --- | --- | --- | --- | --- |
| DEC-01 | OPT-02 | 220 thousand | OPT-01 costs 100 but its backlog never drains | High: delegation can be withdrawn | Slower backlog clearance than OPT-03 (about 55 weeks against 28); operation stays central |
| DEC-02 | OPT-06 | 480 thousand | OPT-05 costs 380 but ranks lower | Medium: lake zones can be retired | 100 thousand more than the baseline; two stores to keep reconciled |
| DEC-03 | OPT-10 | 220 thousand; rebuild 5.4 hours | OPT-09 costs 60 but misses the freshness gate | High: recompute is already needed | Margin of 5 s on the processing-side budget; no single replayable log |
| DEC-04 | OPT-14 | 280 thousand | OPT-13 costs 120 but ranks lower | High: metadata can be rebuilt | Less automation than a broad programme |
| DEC-05 | OPT-20 | 190 thousand | OPT-17 costs 40 but misses the freshness gate | Medium: capture can be switched off | Not the axis winner; depends on log access (DEP-02) and a platform change team |
| DEC-06 | OPT-23 | 260 thousand | OPT-21 costs 30 but fails isolation | Medium: contracts persist once consumers register | Contracts for selected datasets only; others stay on scheduled exports |
| DEC-07 | OPT-26 | 1,650 thousand; 43 s end to end; 99.55% | OPT-25 costs 730 but fails freshness and its members fail their gates | Medium | 920 thousand more than the baseline; 5 basis points of availability margin |

### 6.7 D7 — Organisational and governance implications (Steps 10 and 11)

#### Responsibilities under the recommended model

| Responsibility | Enterprise forum | Central platform team | Domain owner and steward | Control function |
| --- | --- | --- | --- | --- |
| Shared definitions and cross-domain conflicts | Decides | Records | Proposes | Consulted |
| Pipelines, platform and shared controls | Sets standards | Operates | Consumes | Assures |
| Meaning, quality and stewardship of domain data | Reviews | Supports | Accountable | Consulted |
| Access, classification and lifecycle policy | Adopts | Enforces | Applies | Owns |
| Fraud feed and processing | Reviews | Operates | Fraud owns meaning | Consulted |
| Selected data-product interfaces | Sets contract rules | Hosts | Owner per dataset | Consulted |

#### Prerequisites compared with the current state

| Prerequisite | Current state (assumed) | Gap | Action | Owner |
| --- | --- | --- | --- | --- |
| Named accountable owners for sensitive assets | Not evidenced | Large | Confirm owners (DEP-03, REQ-03) | STK-09 |
| Funded domain capacity for stewardship | Uneven skills; no funding line | Medium | Fund stewardship before delegating operation | STK-01 |
| Central platform support for shared controls | Exists; capacity unmeasured | Unknown | Measure and agree service levels (DEP-04) | STK-13 |
| Request log and baseline | Informal | Medium | Measure eight weeks (ASM-04) | STK-14 |
| Source-system change owner for the fraud feed | Not committed | Large | Technical discussion and spike (DEP-01, DEP-02) | STK-04 |
| Lake inventory and lifecycle | Not evidenced | Large | Inventory (REQ-16, UNK-05) | STK-13 |

#### Bounded pilot of one domain-operated product (entry gate for reconsidering OPT-03)

The recommended model does not hand operation to domains. It tests one product, to produce the evidence that
decides whether OPT-03 is reconsidered. Illustrative time box: 10 weeks, after week 8 of the pack.

| Element | Content |
| --- | --- |
| Product | Customer profile for analytics, owned by the retail domain, two named consumers |
| Entry criteria | Named owner and operator; two consumers validated; contract agreed; classification and access reviewed; support path agreed; baseline recorded; sponsor approves scope, budget and stop authority |
| Success measures | Domain absorbs at least 26% of the pilot domain's requests; freshness target met in at least 95% of windows; one breaking change blocked by contract tests; incident exercise closed; consumers confirm value |
| Stop criteria | No funded owner; controls cannot be shown; critical defect not contained; no consumer by the checkpoint; persistent manual platform work; cost beyond the envelope; sponsor withdraws authority |
| Decision at the end | Expand cautiously, revise and retest, or stop; the result is evidence for one product, not for the bank |

#### Controls for regulatory and accountability needs

Every requirement marked as a regulatory or accountability need has at least one control and an owner.

| ID | Need | Requirement | Control | Owner | Evidence produced | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| CTL-01 | Reconciled regulatory returns | REQ-01 | Per-cycle reconciliation of each return to authoritative sources, signed by the reporting lead | STK-08 | Signed reconciliation record per cycle | Illustrative assumption |
| CTL-02 | Lineage for critical flows | REQ-02 | Lineage coverage report on critical regulatory flows, reviewed each quarter | STK-09 | Coverage report and exception list | Illustrative assumption |
| CTL-03 | Accountable ownership | REQ-03 | Ownership register for sensitive assets with written acceptance by each owner | STK-09 | Register with acceptance dates | Illustrative assumption |
| CTL-04 | Policy-based access | REQ-04 | Access-path inventory, authorisation tests before release and quarterly access review | STK-10 | Test results and review record | Illustrative assumption |
| CTL-05 | Residency | REQ-05 | Environment and copy inventory with a jurisdiction field and an annual audit | STK-09 | Inventory and audit report | Illustrative assumption |
| CTL-06 | Dataset contracts | REQ-12 | Contract register with a change-notification workflow | STK-14 | Contract entries and notices | Illustrative assumption |
| CTL-07 | Copies and deletion | REQ-18 | Copy inventory and a half-yearly deletion drill | STK-10 | Drill record | Illustrative assumption |

### 6.8 D8 — Risk and limitation register (Step 13)

Risks, assumptions and dependencies are in Section 6.2. The findings below come from the evaluation; each
limitation cites one.

| ID | Finding statement | Option | Source of evidence | Confidence | Evidence |
| --- | --- | --- | --- | --- | --- |
| FND-01 | Central capacity stays below demand even with better prioritisation, so the backlog never drains | OPT-01 | EST-02; GR-05 | Low | Illustrative assumption |
| FND-02 | The federated hybrid drains the backlog in about 55 weeks if domains absorb 30% of requests | OPT-02 | EST-04; GR-06 | Low | Illustrative assumption |
| FND-03 | Readiness of 14 of 30 does not support enterprise-wide mesh adoption | OPT-04 | RD-01 to RD-10; GR-09 | Low | Illustrative assumption |
| FND-04 | Replaying three years of history through a single stream path takes about 20 hours at 80 MB/s | OPT-11 | EST-10; GR-24 | Low | Illustrative assumption |
| FND-05 | The top-ranked option of each axis, assembled, totals 63 s against the 60 s end-to-end gate | OPT-30 | GR-69; SC-30 | Medium | Illustrative assumption |
| FND-06 | The recommended combination has about 5 basis points of availability margin | OPT-26 | GR-72 | Low | Illustrative assumption |
| FND-07 | Migrating to a lakehouse takes 15 months against a 12-month assumption | OPT-07 | GR-16 | Low | Illustrative assumption |
| FND-08 | The Lambda-based combination fails the availability and cost gates | OPT-29 | GR-75; GR-82 | Low | Illustrative assumption |
| FND-09 | Steward-curated lineage reaches 91%, one point above the 90% gate | OPT-13 | GR-26 | Low | Illustrative assumption |
| FND-10 | The broad combination fails every combination gate except end-to-end freshness | OPT-31 | GR-56; GR-63; GR-77; GR-84; GR-91 | Medium | Illustrative assumption |

| ID | Option | Limitation or failure mode | Finding | Mitigation | Owner | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LIM-01 | OPT-02 | Domain ownership becomes nominal and the queue is unchanged | FND-02 | Named owners, funded capacity and measured absorption (RSK-01) | STK-14 | Open | Illustrative assumption |
| LIM-02 | OPT-10 | The micro-batch falls behind at 3 a.m. and freshness slips unnoticed | FND-05 | Alert on queue age; test the processing stage (ASM-11) | STK-13 | Open | Illustrative assumption |
| LIM-03 | OPT-20 | Log retention expires during an outage and changes are lost | FND-06 | Retain the log beyond the longest outage; reconcile source and target counts daily | STK-13 | Open | Illustrative assumption |
| LIM-04 | OPT-06 | A lake zone drifts from the warehouse definition | FND-07 | State the authority boundary per dataset; reconcile on a schedule | STK-13 | Open | Illustrative assumption |
| LIM-05 | OPT-14 | Lineage capture breaks silently after a job change | FND-09 | Coverage and freshness measures with alerts (RSK-06) | STK-09 | Open | Illustrative assumption |
| LIM-06 | OPT-23 | A contract check is bypassed and a breaking change ships | FND-02 | Release gate on contract tests; consumer inventory | STK-14 | Open | Illustrative assumption |
| LIM-07 | OPT-26 | Incidents cross the source, capture, processing and warehouse owners | FND-06 | Single incident coordinator; shared runbook | STK-13 | Open | Illustrative assumption |
| LIM-08 | OPT-11 | A logic fix needs a replay that cannot finish in the objective | FND-04 | Measure replay before reconsidering (TRG-05) | STK-13 | Open | Illustrative assumption |
| LIM-09 | OPT-30 | A team adopts axis winners and misses the fraud target | FND-05 | Gate combinations end to end (GT-17) | STK-06 | Open | Illustrative assumption |
| LIM-10 | OPT-31 | Scope expands into a broad platform programme | FND-10 | Parsimony test on every added pattern (PT-07 to PT-13) | STK-15 | Open | Illustrative assumption |

### 6.9 D9 — Recommended pattern combination (Steps 14 and 15)

**Recommendation.** Adopt **OPT-26, the workload-led hybrid with change capture**. It is the highest-ranked
eligible combination (3.25 against 2.90 and 2.30), and it is **Conditional**: several gates are still
`Pending`, the key assumptions are low-confidence, and two unknowns block final acceptance.

**Why the combination decision matters.** Every axis winner is in OPT-26 *except one*. The winner on the
interaction axis (OPT-18, 30-second files) cannot be combined with the winner on the processing axis
(OPT-10): together they total 63 s against the 60 s end-to-end gate (GT-17, OPT-30). OPT-20, the second-ranked
interaction option, composes (43 s). Picking the best option on each axis separately would have missed the
fraud target.

**Decision records per axis**

| ID | Decision | Axis winner | Selected option | Deviation reason | Rejected alternatives | Decision state | Missing evidence | Revisit trigger |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DR-01 | DEC-01 | OPT-02 | OPT-02 | None: the selected option is the axis winner | OPT-01 fails GT-02; OPT-03 ranks second and is tested by the pilot; OPT-04 fails GT-04 | Conditional | Request-log baseline (ASM-04); pilot absorption (ASM-03); owner confirmation (GT-01) | TRG-01; TRG-02; TRG-10 |
| DR-02 | DEC-02 | OPT-06 | OPT-06 | None: the selected option is the axis winner | OPT-05 ranks second; OPT-07 fails GT-06; OPT-08 ranks third on workload fit | Conditional | Reconciliation baseline (UNK-04); lake inventory (UNK-05); milestone (UNK-01) | TRG-03 |
| DR-03 | DEC-03 | OPT-10 | OPT-10 | None: the selected option is the axis winner | OPT-09 fails GT-07; OPT-11 fails GT-08; OPT-12 ranks second | Conditional | Timed run of the stages (ASM-11); recompute test (ASM-10) | TRG-06; TRG-05; TRG-11 |
| DR-04 | DEC-04 | OPT-14 | OPT-14 | None: the selected option is the axis winner | OPT-13 ranks second; OPT-15 fails GT-10; OPT-16 fails GT-09 | Conditional | Lineage coverage sample (ASM-07); sensitive-asset list (DEP-03) | TRG-08; TRG-03 |
| DR-05 | DEC-05 | OPT-18 | OPT-20 | OPT-18 with OPT-10 totals 63 s against 60 s (GT-17, OPT-30); OPT-20 is the highest-ranked interaction option that composes | OPT-17 fails GT-11; OPT-18 does not compose; OPT-19 ranks third and depends on a source change | Conditional | Card platform owner commitment (DEP-01); log-access approval (DEP-02); security review (GT-12) | TRG-07 |
| DR-06 | DEC-06 | OPT-23 | OPT-23 | None: the selected option is the axis winner | OPT-21 fails GT-13; OPT-22 ranks second and remains the default for other datasets; OPT-24 ranks third on privacy and complexity | Conditional | Copy inventory and deletion drill (GT-14); named dataset owners | TRG-01 |
| DR-07 | DEC-07 | OPT-26 | OPT-26 | None: the selected option is the top-ranked combination | OPT-27 ranks second; OPT-28 ranks third; OPT-25, OPT-29, OPT-30 and OPT-31 fail gates | Conditional | Milestone (UNK-01); cost ceiling (UNK-02); measured availability (ASM-08) | TRG-03; TRG-04; TRG-09 |

#### Pattern roles in the combination

| ID | Pattern | Option | Role in the architecture | Requirement served | Dependency | Incompatibility avoided | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PR-01 | Federated hybrid operating model | OPT-02 | Domains own definitions and stewardship; the central team operates shared pipelines; a forum resolves disputes | REQ-03; REQ-12; REQ-13 | DEP-04; DEP-05 | Avoids full mesh without readiness (GT-04) | Illustrative assumption |
| PR-02 | Governed warehouse core with repaired lake zones | OPT-06 | The warehouse serves reporting; lake zones serve fraud history and documents, each with an owner | REQ-01; REQ-11; REQ-16 | UNK-04; UNK-05 | Avoids two stores without an authority boundary | Illustrative assumption |
| PR-03 | Micro-batch with batch recompute | OPT-10 | A fresh fraud view; history rebuilt from raw inside the objective | REQ-06; REQ-07 | OPT-20 feed | Avoids two logic paths (OPT-12) and an unproven replay (OPT-11) | Illustrative assumption |
| PR-04 | Incremental catalogue and lineage | OPT-14 | Lineage, ownership and definitions for priority datasets | REQ-02; REQ-17 | DEP-03 | Avoids automation over unowned metadata (OPT-15) | Illustrative assumption |
| PR-05 | Change capture feed | OPT-20 | Delivers card events to the processing path | REQ-06; REQ-05 | DEP-01; DEP-02 | Avoids the 63 s failure of OPT-30 | Illustrative assumption |
| PR-06 | Managed interface for selected datasets | OPT-23 | A contracted interface for customer profile, transaction activity and risk exposure | REQ-12; REQ-19; REQ-18 | OPT-02 owners | Avoids shared-database coupling and events for every dataset | Illustrative assumption |

#### Parsimony test (every pattern must name a requirement)

| ID | Pattern considered | Option | Requirement claimed | Evidence available | Parsimony decision | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| PT-01 | Federated hybrid operating model | OPT-02 | REQ-03; REQ-13 | SC-02; EST-04 | Keep in staged form | Definitions and stewardship move first; operation stays central until the pilot shows capacity |
| PT-02 | Governed warehouse with repaired lake zones | OPT-06 | REQ-01; REQ-11 | SC-06 | Keep | Fraud history and documents need a lake zone; reporting needs the governed warehouse |
| PT-03 | Micro-batch with batch recompute | OPT-10 | REQ-06; REQ-07 | GR-19; GR-23 | Keep | The only processing option that passes both freshness and rebuild gates with one logic path |
| PT-04 | Incremental catalogue and lineage | OPT-14 | REQ-02; REQ-17 | SC-14 | Keep | Needed for regulatory lineage evidence and discoverability |
| PT-05 | Change capture feed | OPT-20 | REQ-06 | GR-37 | Keep in staged form | Needed to reach the freshness target; conditional on DEP-01 and DEP-02 |
| PT-06 | Managed interface for selected datasets | OPT-23 | REQ-12 | SC-23 | Keep in staged form | Selected datasets only; others stay on scheduled export |
| PT-07 | Full data-mesh-style operating model | OPT-04 | none claimed | GR-09 | Remove | No requirement needs it; readiness is 14 against a 21 gate |
| PT-08 | Domain-operated products as the initial model | OPT-03 | none claimed | SC-03; SEN-01 | Remove | Not in the initial target; one bounded pilot inside OPT-02 is the evidence gate |
| PT-09 | Lakehouse migration | OPT-07 | none claimed | GR-16 | Remove | No workload gap that OPT-06 does not serve; 15 months exceeds the milestone assumption |
| PT-10 | Separate batch and speed paths | OPT-12 | none claimed | GR-75; GR-82 | Remove | Two logic paths without a requirement for both; fails availability and cost in combination |
| PT-11 | Single stream path with replay | OPT-11 | none claimed | GR-24 | Remove | Replay of three years misses the 12-hour objective at the assumed throughput |
| PT-12 | Broad automated fabric programme | OPT-15 | none claimed | GR-32 | Remove | Delivery of 18 months exceeds the milestone; metadata owners not yet in place |
| PT-13 | Events for every analytical consumer | OPT-24 | none claimed | SC-24 | Remove | No consumer needs fan-out; deletion of sensitive copies cannot be shown |

### 6.10 D10 — Reference architecture view (Step 17)

**Level: reference architecture (conceptual), not an implementation blueprint.** The view shows layers,
flows and the control plane. It names no product, network or sizing.

```text
D10-DIAGRAM  Northbridge reference architecture (conceptual) | v1.1 | 2026-10-21 | ILLUSTRATIVE REFERENCE VIEW
Legend:  [ELM-nn name] element    ──►  data flow    ┄┄►  governs or describes    (OPT-nn) pattern from the recommendation

 SOURCES                     FRAUD PATH (new)                                          FRAUD CONSUMER
 [ELM-01 Cards platform]──►[ELM-05 Change capture (OPT-20)]──►[ELM-07 Micro-batch + recompute (OPT-10)]──►[ELM-08 Fraud analyst tool]

 SOURCES                     ANALYTICAL CORE
 [ELM-02 Core banking]──┐
 [ELM-03 CRM]───────────┼──►[ELM-06 Existing nightly ingestion]──►[ELM-09 Governed warehouse (OPT-06)]──►[ELM-17 Regulatory and finance reporting]
 [ELM-04 Loan origination]┘                               └──────►[ELM-10 Repaired lake zones (OPT-06)]
                                                                        │
                                  [ELM-11 Curated data products, selected datasets (OPT-23)]──►[ELM-18 Risk and customer analytics]

 OPERATING MODEL AND CONTROL PLANE
 [ELM-12 Domain stewardship and federated forum (OPT-02)]   [ELM-13 Central platform and shared controls (OPT-02)]
 [ELM-14 Priority catalogue and definitions (OPT-14)]┄┄► describes ELM-09, ELM-10, ELM-11
 [ELM-15 Lineage and quality evidence (OPT-14)]┄┄► tracks ELM-07, ELM-09, ELM-11
 [ELM-16 Access, classification and lifecycle policy]┄┄► controls ELM-05, ELM-09, ELM-10, ELM-11
```

**Reading the view.** The fraud path is the only new flow; the nightly ingestion into the warehouse is
unchanged. The lake zones receive data only for named workloads. Curated data products are limited to
selected datasets. The control plane applies to every store and to the new feed.

| ID | Element | Layer | Pattern option | Requirement | Owner | Justification | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ELM-01 | Cards platform | Source | none | REQ-06 | STK-04 | Existing source of card events | Illustrative assumption |
| ELM-02 | Core banking | Source | none | REQ-01 | STK-13 | Existing source; constrains the extraction window (CON-02) | Illustrative assumption |
| ELM-03 | CRM | Source | none | REQ-01 | STK-02 | Existing source of customer data | Illustrative assumption |
| ELM-04 | Loan origination | Source | none | REQ-01 | STK-03 | Existing source of loan data | Illustrative assumption |
| ELM-05 | Change capture | Ingestion | OPT-20 | REQ-06 | STK-13 | Reaches the 60-second target without changing the source application | Illustrative assumption |
| ELM-06 | Existing nightly ingestion | Ingestion | none | REQ-01 | STK-14 | Retained unchanged for reporting; no new pattern | Illustrative assumption |
| ELM-07 | Micro-batch processing with batch recompute | Processing | OPT-10 | REQ-07 | STK-13 | Fresh fraud view and a rebuild inside 12 hours | Illustrative assumption |
| ELM-08 | Fraud analyst tool | Consumer | none | REQ-06 | STK-06 | The consumer whose outcome drives the freshness target | Illustrative assumption |
| ELM-09 | Governed warehouse | Storage | OPT-06 | REQ-01 | STK-08 | Governed, reconciled reporting core | Illustrative assumption |
| ELM-10 | Repaired lake zones | Storage | OPT-06 | REQ-11 | STK-13 | Serves fraud history and documents with owners and lifecycle | Illustrative assumption |
| ELM-11 | Curated data products for selected datasets | Sharing | OPT-23 | REQ-12 | STK-14 | Contracted interface for high-value datasets | Illustrative assumption |
| ELM-12 | Domain stewardship and federated forum | Operating model | OPT-02 | REQ-03 | STK-01 | Accountability for meaning and quality; resolves disputes | Illustrative assumption |
| ELM-13 | Central platform and shared controls | Operating model | OPT-02 | REQ-13 | STK-13 | Operates shared pipelines and controls while the backlog drains | Illustrative assumption |
| ELM-14 | Priority catalogue and definitions | Control plane | OPT-14 | REQ-17 | STK-09 | Discoverability for priority datasets | Illustrative assumption |
| ELM-15 | Lineage and quality evidence | Control plane | OPT-14 | REQ-02 | STK-09 | Regulatory lineage evidence | Illustrative assumption |
| ELM-16 | Access, classification and lifecycle policy | Control plane | none | REQ-04 | STK-10 | Policy-based access and residency across every store | Illustrative assumption |
| ELM-17 | Regulatory and finance reporting | Consumer | none | REQ-01 | STK-08 | Consumer of reconciled returns | Illustrative assumption |
| ELM-18 | Risk and customer analytics | Consumer | none | REQ-09 | STK-05 | Consumers of curated datasets | Illustrative assumption |

### 6.11 D11 — Decision rationale and rejected alternatives (Steps 15 and 16)

Status vocabulary: `Proposed`, `Accepted`, `Deprecated`, `Superseded`. "Conditional" is a decision state recorded
beside the status. No record claims approval.

| ID | Decision record | Status | Decision state | Selected combination | Decision owner | Related IDs | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADR-01 | Adopt a staged, workload-led hybrid reference architecture | Proposed | Conditional | OPT-26 | STK-01 | DEC-07; REQ-06; REQ-07; REQ-12; REQ-13; GT-17; DR-01; DR-07 | SC-26; SEN-22 to SEN-25 |
| ADR-02 | Contingency: source-published events if change capture is refused | Proposed | Conditional | OPT-27 | STK-01 | DEP-01; DEP-02; GT-12; DR-05 | SC-27 |

#### ADR-01 — Adopt a staged, workload-led hybrid reference architecture

- **Status:** Proposed · **Decision state:** Conditional · **Created:** 2026-10-21 · **Effective date:** TBD
- **Author:** STK-15 · **Decision owner:** STK-01 · **Reviewers (planned):** STK-04, STK-06, STK-09, STK-10, STK-13, STK-14
- **Related:** DEC-01 to DEC-07, REQ-01, REQ-06, REQ-07, REQ-12, REQ-13, CON-01, CON-04, ASM-01 to ASM-11, DEP-01, DEP-02, RSK-03, GT-17, OPT-26
- **Evidence:** SC-02, SC-06, SC-10, SC-14, SC-20, SC-23, SC-26; GR-69; FND-01 to FND-10; SEN-01 to SEN-25

**Context.** Northbridge has a long central backlog, a warehouse and a poorly trusted lake, four domains of
uneven capability, a fraud team that sees card events late, and a regulator-driven need for lineage and
accountability. The decision is which patterns to adopt on each axis and how they fit together. It excludes
products, schemas, physical storage, integration implementation, cloud mapping and migration plans.

**Decision drivers.** Gates GT-01 to GT-20 (frozen with the criteria in week 4): backlog drain, readiness,
milestone delivery, freshness budgets, rebuild objective, lineage coverage, isolation, compatibility,
end-to-end freshness, availability and cost. Scored criteria CRIT-01 to CRIT-36 with weights fixed before
scoring.

**Considered options.** Six axis decisions with 24 options, and seven combinations (OPT-25 to OPT-31). Each
decision includes a minimal-change baseline.

**Decision outcome.** Prefer **OPT-26** conditionally: OPT-02, OPT-06, OPT-10, OPT-14, OPT-20 and OPT-23.
**Authorised now:** the request-log baseline, the bounded pilot, the lake inventory, the technical spike and
security review for change capture, the lineage sample, and a non-production timing run. **Not authorised:**
production build commitment, delegation of operation to domains, retirement of the lake, or contract spend.

**Rationale.** OPT-26 is the top-ranked eligible combination (3.25 against 2.90 for OPT-27 and 2.30 for
OPT-28). It passes the end-to-end freshness gate at 43 s, the availability gate at 99.55%, the cost gate at
1,650 thousand and the delivery gate at 8 months. The axis winners combined (OPT-30) fail the end-to-end gate at
63 s. Every pattern in the combination names a requirement (PT-01 to PT-06), and seven patterns were removed
(PT-07 to PT-13).

**Consequences.** Positive: a fraud feed inside the target without changing the source application; a drainable
backlog if domains absorb enough; governed reporting retained; lineage evidence for regulated flows; no premature
mesh. Negative: a thin availability margin (5 basis points); a 5-second margin on the processing side; transitional
duplication between the warehouse and lake zones; domain stewardship needs funded capacity. Accepted trade-offs:
920 thousand more than the baseline; the interaction-axis winner (OPT-18) is not used.

**Rejected alternatives.** OPT-25 fails the combination gates. OPT-27 is credible and is the contingency (ADR-02).
OPT-28 starts domain operation before readiness is shown. OPT-29 fails availability and cost. OPT-30 fails
end-to-end freshness. OPT-31 fails most gates and is the proposal the parsimony test removes.

**Assumptions and conditions for revisiting.** ASM-01 to ASM-11 (all high-impact ones are tied to a trigger in
the table below). Reopen if any trigger fires.

**Open issues and dependencies.** UNK-01 and UNK-02 block final acceptance; DEP-01, DEP-02, DEP-03, DEP-04 and
DEP-05 are open; RSK-04 is very high and escalated to STK-01. Gate results for security, residency, ownership and
deletion are `Pending`.

**Approval and review history.** None. No reviewer has seen this record.

**Supersession.** None. ADR-02 would supersede it for the fraud feed only if its trigger fires and it is accepted.

#### Observable revisit triggers

Each trigger is tied to an assumption and to the decision it reopens. Thresholds come from the gates and the
sensitivity cases above.

| ID | Trigger | Observable threshold | Assumption | Decision | Reopens |
| --- | --- | --- | --- | --- | --- |
| TRG-01 | Measured domain absorption is too low | Under 26% of requests absorbed after the pilot (the backlog gate fails below about 25.3%; SEN-01, SEN-02) | ASM-03 | DEC-01 | Operating model; stronger central operation or a revised pilot |
| TRG-02 | Demand exceeds the drainable level | More than 15 requests per week over eight weeks (SEN-03) | ASM-04 | DEC-01 | Operating model and central capacity |
| TRG-03 | The confirmed milestone is short | Under 8 months (OPT-06, OPT-14 and the combination exceed it; GT-06, GT-10, GT-20) | ASM-01 | DEC-07 | Storage, metadata and combination choices |
| TRG-04 | The confirmed cost ceiling is low | Under 1,650 thousand (SEN-24) | ASM-02 | DEC-07 | Combination; scope reduction |
| TRG-05 | Stream replay is faster than assumed | Measured replay at or above 135 MB/s (SEN-12) | ASM-05 | DEC-03 | Processing; single stream path becomes eligible |
| TRG-06 | Batch recompute is slower than needed | Measured recompute below 135 MB/s (SEN-11) | ASM-10 | DEC-03 | Processing; the rebuild objective or capacity |
| TRG-07 | The card platform owner declines | Change capture and events both refused (GT-12, DEP-01) | ASM-06 | DEC-05 | Interaction; return the target to the sponsor |
| TRG-08 | Steward-curated lineage is too thin | Sampled coverage under 90% (SEN-15) | ASM-07 | DEC-04 | Metadata |
| TRG-09 | Serial availability is below target | Measured under 99.5% (GT-18) | ASM-08 | DEC-07 | Combination and processing path |
| TRG-10 | Readiness is overstated | Evidence review gives under 13 of 30 (SEN-04) | ASM-09 | DEC-01 | Pilot; operating model |
| TRG-11 | The processing stage is slower than budgeted | Measured above 13 s (SEN-13) | ASM-11 | DEC-03 | Processing; the freshness budget |

### 6.12 Traceability and review (Step 18)

Each row walks one architecturally significant requirement to a gate or criterion, the decision, the
selected option and the element in the view. The checker confirms the chain and that the selected option and
element agree with the decision records.

| ID | Requirement | Criterion or gate | Decision | Selected option | Element |
| --- | --- | --- | --- | --- | --- |
| TR-01 | REQ-01 | GT-05; CRIT-06 | DEC-02 | OPT-06 | ELM-09 |
| TR-02 | REQ-02 | GT-09; CRIT-16 | DEC-04 | OPT-14 | ELM-15 |
| TR-03 | REQ-03 | GT-01; CRIT-02 | DEC-01 | OPT-02 | ELM-12 |
| TR-04 | REQ-04 | CRIT-17 | DEC-04 | OPT-14 | ELM-16 |
| TR-05 | REQ-05 | GT-12; CRIT-25 | DEC-05 | OPT-20 | ELM-05 |
| TR-06 | REQ-06 | GT-07; CRIT-11 | DEC-03 | OPT-10 | ELM-07 |
| TR-07 | REQ-06 | GT-11; CRIT-21 | DEC-05 | OPT-20 | ELM-05 |
| TR-08 | REQ-07 | GT-08; CRIT-14 | DEC-03 | OPT-10 | ELM-07 |
| TR-09 | REQ-08 | GT-18; CRIT-34 | DEC-07 | OPT-26 | ELM-13 |
| TR-10 | REQ-12 | GT-13; CRIT-26 | DEC-06 | OPT-23 | ELM-11 |
| TR-11 | REQ-13 | GT-02; CRIT-01 | DEC-01 | OPT-02 | ELM-12 |
| TR-12 | REQ-14 | GT-19; CRIT-31 | DEC-07 | OPT-26 | ELM-13 |
| TR-13 | REQ-15 | GT-20; CRIT-32 | DEC-07 | OPT-26 | ELM-13 |
| TR-14 | REQ-18 | GT-14; CRIT-30 | DEC-06 | OPT-23 | ELM-11 |

**Recorded random traces** (author-run with `--trace`; not independently reviewed)

```text
ELM-15 -> OPT-14 -> DEC-04 -> GT-09 -> REQ-02: Each critical regulatory data flow shall have documented end...
ELM-07 -> OPT-10 -> DEC-03 -> GT-07 -> REQ-06: Card events shall be visible to fraud analysts within the fr...
ELM-13 -> OPT-26 -> DEC-07 -> GT-18 -> REQ-08: The analytical platform shall be available on business days...
REQ-12 -> GT-13 -> DEC-06 -> OPT-23 -> ELM-11
REQ-14 -> GT-19 -> DEC-07 -> OPT-26 -> ELM-13
REQ-02 -> GT-09 -> DEC-04 -> OPT-14 -> ELM-15
```

**Review notes and validation log.** No independent review has taken place for this worked reference. The
author's self-review used the checker and the critical-error list in Section 7.4.

| ID | Subject | Reviewer role | Review method | Planned week | Recorded response | Status |
| --- | --- | --- | --- | --- | --- | --- |
| VL-01 | Requirements and targets (REQ-01 to REQ-19, TGT-01 to TGT-08) | STK-06; STK-09 | Walk-through of each Must against its acceptance criterion | 7 | Not yet recorded | Planned |
| VL-02 | Estimates and timing budgets (EST-01 to EST-13, TB-01 to TB-26) | STK-13; STK-14 | Reviewer recomputes at least three figures | 7 | Not yet recorded | Planned |
| VL-03 | Readiness scores (RD-01 to RD-10) | STK-02; STK-03; STK-04; STK-05 | Evidence review with the domain heads | 7 | Not yet recorded | Planned |
| VL-04 | Criteria and weights frozen before scoring (CRIT-01 to CRIT-36) | STK-11 | Confirm the freeze week precedes the scoring week | 7 | Not yet recorded | Planned |
| VL-05 | Controls (CTL-01 to CTL-07) | STK-09; STK-10 | Check each control against the obligation | 8 | Not yet recorded | Planned |
| VL-06 | Decision record ADR-01 and the view | STK-11 | Independent challenge of the evidence | 8 | Not yet recorded | Planned |

### 6.13 D12 — Final recommendation and review summary (Step 19)

**Northbridge Bank — Reference architecture pattern comparison. Version 1.1, 2026-10-21. ILLUSTRATIVE.**

**Problem.** Reporting, fraud, risk and customer analytics need consistent, governed, timely data. The central
team has a long backlog, the lake is poorly trusted, and accountability and discoverability are weak.

**What was decided, and not decided.** Six axis decisions and one combination decision were analysed. A staged,
workload-led hybrid (OPT-26) is preferred. **Nothing is approved:** some gates are still pending, the key
assumptions are low-confidence, and two unknowns block final acceptance (the regulatory milestone date and the
cost ceiling).

| Axis | Preferred option | Why | Main condition |
| --- | --- | --- | --- |
| Operating model | Federated hybrid (OPT-02) | The only eligible model that clears the backlog and fits today's readiness (14 of 30) | Domains absorb at least 26% of requests; owners and funded capacity |
| Storage | Governed warehouse with repaired lake zones (OPT-06) | Serves reporting and the fraud, risk and document workloads without a 15-month migration | Reconciliation baseline; lake inventory |
| Processing | Micro-batch with batch recompute (OPT-10) | Meets freshness and the 12-hour rebuild with one logic path | Timed stages; recompute of at least 135 MB/s |
| Metadata | Incremental catalogue and lineage (OPT-14) | Reaches 94% lineage inside the milestone | Sensitive-asset list; sampled coverage |
| Fraud interaction | Change capture (OPT-20) | Composes with the processing choice at 43 s | Card platform owner and security approval |
| Sharing | Managed interface for selected datasets (OPT-23) | Contracts, ownership and reuse for high-value datasets | Dataset owners; deletion drill |

**Key points.** The best option on every axis does not compose: the interaction winner and the processing winner
total 63 s against a 60 s target, so the combination was tested end to end. Full mesh, a lakehouse migration,
Lambda, a single stream path, a broad fabric programme and events for every consumer were considered and
removed, each for a stated reason. A bounded pilot of one domain-operated product is the evidence gate for
reconsidering domain-operated products.

**Key figures (illustrative).** Backlog clearance about 55 weeks (EST-04); rebuild 5.4 hours by recompute
against 20.2 hours by single-path replay (EST-09, EST-10); end-to-end freshness 43 s against 60 s; serial
availability 99.55% against 99.5%; three-year cost 1,650 thousand against a 2,000 ceiling.

**Accepted trade-offs.** 920 thousand more than the baseline; a thin availability margin; the interaction-axis
winner is not used; transitional duplication between the warehouse and lake zones.

**Top risks.** Regulatory milestone unconfirmed (RSK-04, exposure 15, very high); domain ownership becomes nominal
(RSK-01); thin availability margin (RSK-02); axis winners adopted separately (RSK-03); scope expansion (RSK-07).

**What would change the answer.** Domain absorption under 26%; a milestone under 8 months; a cost ceiling under
1,650 thousand; batch recompute under 135 MB/s; a card platform owner who declines both feeds.

**Caveats and limits.** Every figure is illustrative and no stakeholder has validated any row. Sensitivity moved
inputs one at a time. Ratings for operability, dependencies, ownership and diagnosability are anchored
judgements. This is a reference architecture for modules 2D.4 onward, not an implementation blueprint.


---

## 7. Validation and quality assurance

### 7.1 Quality criteria and how each is verified

| Check | How to verify | Automated? |
| --- | --- | --- |
| Candidate patterns are relevant to the problem | Each candidate has a stated reason; each kept pattern names a requirement | Yes (parsimony table) |
| Requirements and constraints documented with IDs and sources | Register present; sources are stakeholders | Partly |
| No requirement embeds a pattern or product | Scan requirement text for pattern and product terms | Yes |
| Each candidate evaluated against consistent criteria | The same gates and criteria apply to every option of a decision | Yes (gate results and inputs complete) |
| Important trade-offs acknowledged | Section 6.6 states what each selected option gives up | No |
| Organisational and governance implications considered | Readiness, prerequisites and controls are present | Partly |
| Pattern combinations have a clear purpose | Each member traces to a requirement; one or more removed | Yes |
| Recommendation follows from the analysis | The recommended combination is the top-ranked eligible one; selected options equal its members | Yes |
| Rejected alternatives have specific reasons | Each decision record lists them with a gate or rank | Partly |
| Assumptions and uncertainties are visible | Every high-impact assumption has a trigger | Yes |
| The view is consistent with the recommendation | Every element is in the table and vice versa; every element maps to a requirement and a member pattern | Yes |
| Numbers are consistent | All estimates, gate values, scores and sensitivity cases are recomputed | Yes |
| Criteria were fixed before scoring | Freeze week precedes scoring week | Yes |
| No option that failed a gate is scored | Eligibility is recomputed; ineligible options carry no score | Yes |

### 7.2 Running the checker

Extract Appendix B to `check_pattern_comparison.py`, then run from the repository root:

```bash
python3 check_pattern_comparison.py "Stage 2D — Data Architecture/03-Data-Architecture-Patterns-and-Reference-Architectures/Projects/03-reference-architecture-pattern-comparison.md"
python3 check_pattern_comparison.py FILE --derive
python3 check_pattern_comparison.py FILE --trace 3 --seed 2026
```

The checker exits `0` when every check passes and `1` otherwise. `--derive` prints the recomputed derived
values for review or repair. For a real project (Mode B), keep the table header names or adapt the `KINDS`
mapping at the top of the script.

### 7.3 What the checker verifies

- **Structure:** unique IDs, no empty cells, valid evidence and estimate labels, every ID reference resolves to a defined item.
- **Requirements:** types, priorities, a measurable criterion on every Must, at least 90% of Musts measurable, no pattern or product terms.
- **Estimates:** every expression is recomputed and compared with the stated value; the sensitivity ranking is recomputed.
- **Options:** one baseline and at least three options per decision; requires and conflicts resolve; members of combinations exist; every plain option has a description, cost and delivery estimate.
- **Gates:** each gate applies to the stated options; every numeric value is recomputed from its source (timing stages, delivery, cost, availability, readiness, estimates, compatibility, failing members); results follow thresholds.
- **Criteria:** weights sum to 1; bands are contiguous; ratings follow the bands; scores and ranks are recomputed; only eligible options are scored; criteria are frozen before scoring.
- **Sensitivity:** every case is re-run with gates rechecked, and options that become eligible must have complete inputs.
- **Recommendation:** each axis winner is recomputed; a selected option that is not the winner must cite a combination gate; the selected options equal the members of the top-ranked combination; pattern roles and the parsimony test match.
- **View and controls:** the diagram elements equal the element table; each element traces to a requirement and to a recommended pattern; each regulatory need has a control and an owner.
- **Traceability:** every architecturally significant requirement is traced; the chain agrees with the decision records.

### 7.4 Critical-error list (self-review)

| Critical error | How this pack guards against it |
| --- | --- |
| A requirement embeds a pattern or product | Term scan on requirement text |
| A Must has no measurable criterion | Checker; REQ-14 and REQ-15 are measurable in form, pending UNK-02 and UNK-01 |
| Axes compared as if they answered one question | Decisions DEC-01 to DEC-06 are separate; combination is DEC-07 |
| An option that fails a gate stays eligible or is scored | Gate results recomputed; ineligible options carry no score |
| Criteria or weights changed after scoring | Frozen in week 4; scored in week 5 |
| Axis winners assumed to compose | GT-15 to GT-20 test the assembled combination; OPT-30 fails GT-17 |
| A pattern in the recommendation with no requirement | Parsimony test; checker requires a Keep entry and requirement for each member |
| Over-engineered proposal accepted | OPT-31 fails; seven patterns removed (PT-07 to PT-13) |
| Unit or arithmetic error | All estimates, values and scores recomputed |
| A high-impact assumption with no trigger | Checker requires a trigger per high-impact assumption |
| A decision record claims approval | All statuses are `Proposed`; the checker rejects `Accepted` |
| The view contains an unexplained element | Element table requires a requirement and a justification |

### 7.5 Project completion gate (roadmap Section 7.7) and worked-reference status

| Gate item | Mode A status (Northbridge worked reference) | Mode B requirement |
| --- | --- | --- |
| D1–D12 exist, version-dated, consistent IDs | Met: Section 6, version 1.1, checker passes | Met for your own set |
| Requirements measurable and sourced; no pattern or product | Met: all Musts measurable in form; term scan passes; two parameters pending named unknowns | Met with confirmed parameters |
| At least three feasible candidates including a baseline; gate failures recorded with reasons | Met: each decision has at least three options and a baseline; failures in the gate-result table | Met |
| Criteria and weights fixed and dated before scoring; sensitivity states whether the ranking changes | Met: week 4 and week 5; SEN-01 to SEN-25 | Met |
| Each candidate has costs, failure modes and organisational prerequisites | Met: cost components, 3 a.m. failures, readiness and prerequisites | Met |
| Every pattern traces to a requirement; at least one removed by the parsimony test | Met: PT-01 to PT-13 | Met |
| Each regulatory or accountability need maps to a control and an owner | Met: CTL-01 to CTL-07 | Met |
| Every numeric claim has units, formula, assumption and an illustrative label | Met: enforced by the checker | Met |
| The view is consistent and has no unexplained element | Met: enforced by the checker | Met |
| Random trace from three recommendation elements to requirements and from three requirements to decisions | Met by the checker; **not witnessed by a reviewer** | Required |
| Two reviewer challenges answered from recorded evidence; independent reviewer agrees | Challenge answers prepared below by the author; **independent agreement not obtained** | Required |

### 7.6 Anticipated reviewer challenges (author-prepared, not recorded reviewer objections)

| Challenge | Answer using recorded evidence |
| --- | --- |
| "The fraud team prefers the 30-second file feed: it ranks first on its axis, is cheaper and is faster to deliver." | On its own it does rank first (SC-18). But with the processing choice it totals 63 s against the 60 s gate (GR-69, FND-05), so the combination fails. It would compose only with a 10-second micro-batch interval (SEN-22), and even then it ranks second (3.05 against 3.25). |
| "Full mesh is the strategic direction; why defer it?" | Readiness is 14 of 30 against a 21-point gate (GR-09, FND-03). The backlog gate also fails if domains absorb under about 26% of requests (SEN-01, SEN-02, TRG-01), and absorption is a `guessed` input. A bounded pilot produces the evidence; it is the entry gate for reconsidering OPT-03. |
| "Your availability and rebuild figures rest on assumed numbers." | Correct, and they are labelled so (ASM-05, ASM-08, ASM-10). The sensitivity cases show where each result flips (135 MB/s, SEN-11 and SEN-12; availability, GT-18), and each has a trigger (TRG-05, TRG-06, TRG-09). |

---

## 8. Templates and guides for a real organisation (Mode B)

Placeholders use the form `XXX-nn`; replace them with real IDs.

### 8.1 Row templates

**Option**

| ID | Decision | Option | Option description | Role | Requires | Conflicts | Members | Why a candidate | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OPT-nn | DEC-nn | short name | what it is, in one sentence | Baseline / Alternative | options or none | options or none | members, or n/a | reason it is credible | evidence label |

**Gate and gate result**

| ID | Decision | Gate statement | Source | Operator | Threshold | Unit | Applies to |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GT-nn | DEC-nn | a testable must-have | requirement or constraint IDs | <= / >= / n/a | number or n/a | unit | all or option IDs |

| ID | Gate | Option | Value | Value source | Result | Note |
| --- | --- | --- | --- | --- | --- | --- |
| GR-nn | GT-nn | OPT-nn | number or n/a | TB / DL / TCO / AV / RD / EST-nn / stated / n/a | Pass / Fail / Pending | evidence |

**Pattern card (one per candidate, same level of detail)**

| Field | Content |
| --- | --- |
| Problem addressed | The recurring problem, in business terms |
| Structure | Components and responsibilities |
| Data flow | How data move |
| Forces improved and weakened | What it gives and what it costs |
| Prerequisites | Ownership, skills, platform, governance |
| Failure modes | At least one "how this fails at 3 a.m." |
| Use when / avoid when | Conditions of fit |
| Review signals | Observable measures of health |

**Decision record row and revisit trigger**

| ID | Decision | Axis winner | Selected option | Deviation reason | Rejected alternatives | Decision state | Missing evidence | Revisit trigger |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DR-nn | DEC-nn | OPT-nn | OPT-nn | none, or the gate that forced a different choice | options with a gate or rank reason | Conditional / Final | evidence, owner, week | TRG-nn |

| ID | Trigger | Observable threshold | Assumption | Decision | Reopens |
| --- | --- | --- | --- | --- | --- |
| TRG-nn | what changes | a measurable value | ASM-nn | DEC-nn | what is reconsidered |

**Parsimony row**

| ID | Pattern considered | Option | Requirement claimed | Evidence available | Parsimony decision | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| PT-nn | pattern | OPT-nn | REQ-nn or none claimed | evidence IDs | Keep / Keep in staged form / Remove | specific reason |

### 8.2 Inputs to collect in a real assessment

1. Request logs for the central team (arrivals, completions, age) for at least eight weeks.
2. Freshness timestamps for the current fraud feed and the card platform's emission cadence.
3. Reconciliation results for two reporting cycles.
4. A lake inventory: datasets, owners, consumers, last use, classification.
5. The sensitive-asset list and the lineage evidence format agreed with compliance.
6. Provider availability statements and any measured availability for each component.
7. A replay or recompute test on representative data volumes.
8. Cost estimates as ranges, including build, run, support, training and exit.

### 8.3 Decision-pack checklist before review

- Scope states exclusions and the level (reference, not blueprint).
- Decisions are separated by axis; coupling and a combination decision are explicit.
- Every decision has a baseline and at least three options; failures cite a gate.
- Gates are defined before weights; weights are frozen and dated before scoring.
- Every number has a formula, units and an evidence label.
- Sensitivity covers the least certain inputs and states flip points.
- Every pattern in the recommendation names a requirement; at least one was removed.
- Every regulatory need has a control and an owner; every element in the view has a requirement.
- The checker passes; a reviewer has traced three elements back and three requirements forward.

---

## 9. Common pitfalls and project risks

| Pitfall | Why it harms | Prevention |
| --- | --- | --- |
| Comparing patterns from different axes ("Lambda versus mesh") | The comparison answers no real question | One decision per axis, then a combination decision |
| Choosing the best option on each axis | The parts may not compose | Test the assembled combination end to end |
| Treating a pattern name as a requirement | The solution is fixed before the need is understood | Describe outcomes; scan requirements for pattern terms |
| Scoring an option that failed a gate | Hides a mandatory failure | Gate first; ineligible options carry no score |
| Weights changed after seeing the winner | Destroys trust in the comparison | Freeze week recorded and checked |
| Inferring readiness from a prototype | Overstates capability | Score readiness with evidence; run a bounded pilot |
| Declaring a pattern adopted by renaming teams | No change in ownership or capacity | Entry criteria, funding and stop criteria |
| Burst throughput presented as capacity | Under-sized recovery and replay | Use sustained throughput and a replay-time calculation |
| Ignoring the source cadence | The target is unreachable | Include source wait in the timing budget |
| Universal patterns ("events for everything") | Cost, privacy and complexity without a requirement | Parsimony test per pattern |
| A weak baseline | Makes any change look good | Give the baseline its strongest credible design |
| Reporting a score as proof | Hides ordinal and judgemental inputs | Show criterion-level ratings, gates and sensitivity |

**Project-level risks**

| Risk | Early sign | Response |
| --- | --- | --- |
| Stakeholders unavailable | Interviews slip a week | Record the gap as an unknown with an owner; do not invent a position |
| Scope creep into design | Options acquire product names or schemas | Return to pattern categories; defer to later modules |
| Evidence not available | Request logs or timestamps are not supplied | Mark the decision conditional; name the evidence, owner and week |
| Numbers drift between artefacts | The estimates and the decision record disagree | One source of truth; run the checker before every release |

---

## 10. Connection to subsequent modules

The comparison is a **decision baseline at the reference level**, not a design.

| Later module | What it takes from this project |
| --- | --- |
| 2D.4 Conceptual, logical and physical modeling | Domain boundaries and the scope of the selected data products (OPT-23, ELM-11) define model boundaries |
| 2D.5 Database and storage architecture | The storage and layer decision (OPT-06) and the estimates (EST-07 to EST-10) are the input |
| 2D.6 Data integration and interoperability | The interaction choice (OPT-20), the contract rules (CTL-06) and the freshness budgets are the input |
| 2D.7 Enterprise data platform and lakehouse | The platform operating model and control plane (ELM-12 to ELM-16) |
| 2D.8 Cloud, hybrid and multi-cloud | Residency and cost constraints (CON-01, CON-06) bound service mapping |
| 2D.9 Streaming and real-time | The processing decision (OPT-10) and the conditions under which a stream path returns (TRG-05) frame detailed design |
| 2D.10 Governance, security, privacy, compliance | The governance model and control mapping (CTL-01 to CTL-07) |
| 2D.15 Documentation and reviews | The comparison, the decision record and the view are review artefacts |

**Open questions to carry into module 2D.4:** UNK-01 to UNK-05; which datasets the managed interface covers
first; the authority boundary between the warehouse and each lake zone; and the outcome of the bounded pilot.

---

## 11. Self-assessment rubric

Score each criterion 0 (absent), 1 (partial) or 2 (complete). Pass requires at least 90% of the maximum and no zero.

| # | Criterion | Evidence |
| --- | --- | --- |
| 1 | Scope names exclusions, the decisions and the level of the output | D1 |
| 2 | Every workload has a consumer and an outcome; control functions are present | D2 |
| 3 | Requirements are measurable, sourced and free of pattern or product terms | D2, checker |
| 4 | Constraints, assumptions, dependencies, risks and unknowns are classified, owned and traced | D2, checker |
| 5 | Decisions are separated by axis; coupling is explicit; a combination decision exists | D3 |
| 6 | Each decision has a baseline and at least three options described at the same level | D3, D4 |
| 7 | Gates are evaluated before scoring; failures cite a reason | D5, checker |
| 8 | Criteria and weights are fixed and dated before scoring | D5, checker |
| 9 | Estimates carry formulas, units, labels and a sensitivity ranking | D2, checker |
| 10 | Sensitivity covers the least certain inputs and states flip points | D6 |
| 11 | Readiness, prerequisites and controls are compared with the current state | D7 |
| 12 | Every option has a "fails at 3 a.m." and a limitation tied to a finding | D4, D8 |
| 13 | Every pattern in the recommendation names a requirement; at least one is removed | D9, checker |
| 14 | Rejected alternatives have specific reasons; revisit triggers are observable and tied to assumptions | D11, checker |
| 15 | The view has no unexplained element and agrees with the recommendation | D10, checker |
| 16 | Traceability passes in both directions | Traceability table, checker |
| 17 | The summary states conditions and limits and can be read in ten minutes | D12 |
| 18 | An independent reviewer agrees the evidence supports the conclusions | Reviewer note |

---

## Appendix A — Glossary

| Term | Meaning in this project |
| --- | --- |
| Axis | A dimension on which patterns are chosen (operating model, storage, processing, metadata, interaction, sharing) |
| Baseline | The minimal-change option for a decision; always included |
| Combination | One option per axis, assembled and tested end to end |
| Conditional decision | A decision whose preferred option depends on named missing evidence; a state, not a status |
| Gate | A pass/fail eligibility test applied before scoring |
| Parsimony test | Asking of each pattern which requirement it serves, and removing it if none |
| Reference architecture | A reusable, logical template for a class of problems; more concrete than a pattern, less specific than a blueprint |
| Sustained throughput | The rate a process can keep up without backlog growth; not the burst rate |
| Tornado | A ranking of inputs by their effect on an output when varied alone |

---

## Appendix B — Consistency checker (`check_pattern_comparison.py`)

Python 3.9 or later; standard library only. It reads the Markdown tables in this file.

```python
#!/usr/bin/env python3
"""Consistency checker for the reference architecture pattern comparison (D1-D12).

Usage:
    python3 check_pattern_comparison.py FILE
    python3 check_pattern_comparison.py FILE --derive
    python3 check_pattern_comparison.py FILE --trace 3 --seed 2026

Exit code 0 means every check passed; 1 means at least one error.
`--derive` prints the recomputed value of every derived cell (estimates, gate
results, scores, sensitivity outcomes) as Markdown rows, for review or repair.
"""
import argparse
import ast
import math
import operator
import random
import re
import sys
from pathlib import Path

ID_CELL = re.compile(r"^[A-Z]{2,4}-\d{2,3}$")
PREFIXES = ("STK|WL|REQ|TGT|CON|ASM|DEP|RSK|UNK|INP|EST|TN|DEC|OPT|OD|TB|TCO|DL|AV|RD|GT|"
            "GR|CRIT|AN|JA|OI|SC|SEN|FND|LIM|PR|PT|ELM|CTL|DR|TRG|TR|VL|ADR")
ID_ANY = re.compile(rf"\b(?:{PREFIXES})-\d{{2,3}}\b")
SEPARATOR = re.compile(r"^:?-{3,}:?$")
EVIDENCE = {"Verified fact", "Stakeholder statement", "Illustrative assumption",
            "Inference", "Open question"}
ESTIMATE_LABELS = {"measured", "sampled", "stated", "estimated", "guessed"}
LEVEL = {"Low", "Medium", "High"}
CLOSE_CALL = 0.15
PATTERN_TERMS = re.compile(
    r"\b(data mesh|mesh|lakehouse|lambda|kappa|data fabric|fabric|data lake|warehouse|"
    r"event[- ]driven|event bus|micro-?batch|streaming|cdc|kafka|kinesis|pulsar|snowflake|"
    r"redshift|bigquery|databricks|spark|flink|airflow|dbt|hadoop|s3|aws|azure|gcp|oracle|"
    r"postgres(?:ql)?|mysql|mongodb|cassandra|sql|etl|mdm)\b", re.I)

# A table is recognised by one header that only that table has (first match wins).
KINDS = {
    "Stakeholder (role)": "STK", "Workload": "WL", "Requirement statement": "REQ",
    "SLI definition": "TGT", "Constraint": "CON", "Impact if wrong": "ASM",
    "Failure consequence": "DEP", "Probability": "RSK", "Blocks": "UNK",
    "Estimate label": "INP", "Expression": "EST", "Swing": "TN", "Axis": "DEC",
    "Option description": "OPT", "Failure at 3 a.m.": "OD", "Stage": "TB",
    "Build and migration": "TCO", "Delivery months": "DL", "Availability": "AV",
    "Dimension": "RD", "Gate statement": "GT", "Gate": "GR", "Rating basis": "CRIT",
    "From": "AN", "Anchor for 1": "JA", "Input value": "OI", "Eligible": "SC",
    "Winner": "SEN", "Finding statement": "FND", "Limitation or failure mode": "LIM",
    "Role in the architecture": "PR", "Parsimony decision": "PT", "Layer": "ELM",
    "Control": "CTL", "Axis winner": "DR", "Observable threshold": "TRG",
    "Criterion or gate": "TR", "Planned week": "VL", "Decision record": "ADR",
}
NEEDS_LABEL = {"STK", "WL", "CON", "ASM", "DEP", "RSK", "TGT", "TB", "TCO", "DL", "AV",
               "RD", "OPT", "OD", "FND", "LIM", "PR", "ELM", "CTL"}


# ----------------------------------------------------------------------------- parsing
def num(text):
    t = text.replace(",", "").replace("`", "").strip()
    if t == "inf":
        return math.inf
    try:
        return float(t)
    except ValueError:
        return None


def refs(cell):
    return ID_ANY.findall(cell)


def parse(text):
    tables = {kind: {} for kind in set(KINDS.values())}
    errors, prose, diagrams = [], [], []
    in_fence, fence, prev, header = False, [], None, None
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_fence and fence and fence[0].startswith("D10-DIAGRAM"):
                diagrams.append("\n".join(fence))
            in_fence, fence, prev, header = not in_fence, [], None, None
            continue
        if in_fence:
            fence.append(line)
            continue
        prose.append(line)
        if not stripped.startswith("|"):
            prev = header = None
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(SEPARATOR.match(c) for c in cells):
            header, prev = prev, None
            continue
        if header is None:
            prev = cells
            continue
        kind = next((KINDS[h] for h in header if h in KINDS), None)
        if kind is None or not ID_CELL.match(cells[0]):
            continue
        if len(set(header)) != len(header):
            errors.append(f"line {number}: duplicate column names in the table of {cells[0]}")
            continue
        if len(cells) != len(header):
            errors.append(f"line {number}: {cells[0]} has {len(cells)} cells, "
                          f"expected {len(header)}")
            continue
        row = dict(zip(header, cells))
        row["_line"] = number
        if cells[0] in tables[kind]:
            errors.append(f"line {number}: duplicate ID {cells[0]}")
        tables[kind][cells[0]] = row
    return tables, "\n".join(prose), diagrams, errors


# ----------------------------------------------------------------------------- expressions
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.Pow: operator.pow}
FUNCS = {"max": max, "min": min}


def evaluate(expression, env):
    def go(node):
        if isinstance(node, ast.Expression):
            return go(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            return env[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](go(node.left), go(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -go(node.operand)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id in FUNCS and not node.keywords:
            return FUNCS[node.func.id](*[go(a) for a in node.args])
        raise ValueError(f"unsupported expression: {expression}")
    cleaned = re.sub(r"\b([A-Z]{3})-(\d{2,3})\b", r"\1_\2", expression.replace("`", ""))
    return go(ast.parse(cleaned, mode="eval"))


def estimates(tables, column="Expected", override=None):
    env = {k.replace("-", "_"): num(v[column]) for k, v in tables["INP"].items()}
    if override:
        env.update({k.replace("-", "_"): v for k, v in override.items()})
    out, pending = {}, dict(tables["EST"])
    for _ in range(len(pending) + 1):
        for eid in list(pending):
            try:
                value = evaluate(pending[eid]["Expression"], env)
            except KeyError:
                continue
            env[eid.replace("-", "_")] = out[eid] = value
            del pending[eid]
    return out, pending


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol * max(abs(a), abs(b), 1e-9)


def half_up(x):
    return int(math.floor(x + 0.5))


def fmt(value, digits=4):
    return f"{float(f'{value:.{digits}g}'):g}"


# ----------------------------------------------------------------------------- engine
class Engine:
    def __init__(self, tables):
        self.t = tables
        self.bands = {}
        for row in tables["AN"].values():
            self.bands.setdefault(row["Criterion"], []).append(
                (int(row["Rating"]), num(row["From"]), num(row["To"])))

    # --- structure
    def options(self, decision):
        return [o for o, r in self.t["OPT"].items() if r["Decision"] == decision]

    def members(self, option):
        cell = self.t["OPT"][option]["Members"]
        return refs(cell) if cell != "n/a" else [option]

    def is_combo(self, option):
        return self.t["OPT"][option]["Members"] != "n/a"

    def decision_of(self, option):
        return self.t["OPT"][option]["Decision"]

    def gates(self, decision):
        return [g for g, r in self.t["GT"].items() if r["Decision"] == decision]

    def applies(self, gate, option):
        cell = self.t["GT"][gate]["Applies to"]
        return cell == "all" or option in refs(cell)

    def gate_row(self, gate, option):
        for gid, r in self.t["GR"].items():
            if r["Gate"] == gate and r["Option"] == option:
                return gid, r
        return None, None

    # --- quantities (aggregate over members for combinations)
    def tb_sum(self, option, ov):
        total = 0.0
        for m in self.members(option):
            for row in self.t["TB"].values():
                if row["Option"] == m:
                    seconds = num(row["Seconds"])
                    if ov.get("stage") and row["Stage"] == ov["stage"][0]:
                        seconds = ov["stage"][1]
                    total += seconds
        return total

    def tco(self, option):
        return sum(num(r["Total"]) for m in self.members(option)
                   for r in self.t["TCO"].values() if r["Option"] == m)

    def months(self, option):
        values = [num(r["Delivery months"]) for m in self.members(option)
                  for r in self.t["DL"].values() if r["Option"] == m]
        return max(values) if values else None

    def avail(self, option):
        product = 1.0
        for m in self.members(option):
            for r in self.t["AV"].values():
                if r["Option"] == m:
                    product *= num(r["Availability"])
        return product

    def readiness(self):
        return sum(num(r["Score"]) for r in self.t["RD"].values())

    def compat(self, option):
        members = set(self.members(option))
        for m in members:
            req = self.t["OPT"][m]["Requires"]
            if req != "none" and not (set(refs(req)) & members):
                return 0
            if set(refs(self.t["OPT"][m]["Conflicts"])) & members:
                return 0
        return 1

    def axis_failures(self, option, ov):
        failed = 0
        for m in self.members(option):
            if m not in self.eligible(self.decision_of(m), ov):
                failed += 1
        return failed

    def tb_gate_threshold(self, decision, ov):
        for g in self.gates(decision):
            for r in self.t["GR"].values():
                if r["Gate"] == g and r["Value source"] == "TB":
                    return ov.get("threshold", {}).get(g, num(self.t["GT"][g]["Threshold"]))
        return None

    def av_gate_threshold(self, decision, ov):
        for g in self.gates(decision):
            for r in self.t["GR"].values():
                if r["Gate"] == g and r["Value source"] == "AV":
                    return ov.get("threshold", {}).get(g, num(self.t["GT"][g]["Threshold"]))
        return None

    def source_value(self, source, option, ov, stated=None, gate=None):
        if source == "TB":
            return self.tb_sum(option, ov)
        if source == "DL":
            return self.months(option)
        if source == "TCO":
            return self.tco(option)
        if source == "AV":
            return self.avail(option)
        if source == "RD":
            return self.readiness()
        if source == "COMPAT":
            return self.compat(option)
        if source == "AXIS":
            return self.axis_failures(option, ov)
        if source.startswith("EST-"):
            values, _ = estimates(self.t, "Expected", ov.get("inp"))
            return values[source]
        if source == "stated":
            override = ov.get("gatevalue", {})
            if gate in override and option in override[gate][0]:
                return override[gate][1]
            return stated
        return None

    # --- gates
    def gate_result(self, gate, option, ov):
        gid, row = self.gate_row(gate, option)
        g = self.t["GT"][gate]
        if row is None:
            return None, None
        if g["Operator"] == "n/a":
            return None, row["Result"]
        value = self.source_value(row["Value source"], option, ov, num(row["Value"]), gate)
        threshold = ov.get("threshold", {}).get(gate, num(g["Threshold"]))
        ok = value <= threshold + 1e-12 if g["Operator"] == "<=" else value >= threshold - 1e-12
        return value, "Pass" if ok else "Fail"

    def eligible(self, decision, ov):
        out = []
        for o in self.options(decision):
            results = []
            for g in self.gates(decision):
                if self.applies(g, o):
                    results.append(self.gate_result(g, o, ov)[1])
            if "Fail" not in results:
                out.append(o)
        return out

    # --- criteria
    def weights(self, decision, ov):
        crit = {c: num(r["Weight"]) for c, r in self.t["CRIT"].items()
                if r["Decision"] == decision}
        if "weight" in ov and ov["weight"][0] in crit:
            target, new = ov["weight"]
            rest = sum(w for c, w in crit.items() if c != target)
            crit = {c: (new if c == target else w * (1 - new) / rest) for c, w in crit.items()}
        return crit

    def band(self, criterion, value):
        x = half_up(value)
        for rating, lo, hi in self.bands[criterion]:
            if lo <= x <= hi:
                return rating
        return None

    def resolved_input(self, row, ov):
        source, option, criterion = row["Value source"], row["Option"], row["Criterion"]
        if "oi" in ov and ov["oi"][:2] == (option, criterion):
            return ov["oi"][2]
        decision = row["Decision"]
        if source == "TBM":
            return self.tb_gate_threshold(decision, ov) - self.tb_sum(option, ov)
        if source == "AVM":
            return (self.avail(option) - self.av_gate_threshold(decision, ov)) * 10000
        if source == "stated":
            return num(row["Input value"])
        return self.source_value(source, option, ov)

    def rating(self, row, ov):
        if "rating" in ov and ov["rating"][:2] == (row["Option"], row["Criterion"]):
            return ov["rating"][2]
        if row["Value source"] == "judgement":
            return int(row["Rating"])
        return self.band(row["Criterion"], self.resolved_input(row, ov))

    def scores(self, decision, ov=None):
        ov = ov or {}
        weights = self.weights(decision, ov)
        result = {}
        for option in self.eligible(decision, ov):
            rows = [r for r in self.t["OI"].values()
                    if r["Decision"] == decision and r["Option"] == option]
            if {r["Criterion"] for r in rows} != set(weights):
                result[option] = None
                continue
            ratings = [self.rating(r, ov) for r in rows]
            result[option] = None if None in ratings else sum(
                weights[r["Criterion"]] * x for r, x in zip(rows, ratings))
        return result


def outcome(scores):
    ranked = sorted(((round(s, 2), o) for o, s in scores.items() if s is not None), reverse=True)
    if not ranked:
        return "none", None, None
    if len(ranked) == 1:
        return ranked[0][1], ranked[0][0], None
    if ranked[0][0] == ranked[1][0]:
        return "tie", ranked[0][0], ranked[1][0]
    return ranked[0][1], ranked[0][0], ranked[1][0]


def parse_override(row):
    kind, target, value = row["Kind"], row["Target"], row["Value"]
    if kind == "stage":
        return {"stage": (target, num(value))}
    if kind == "oi":
        option, criterion = target.split("/")
        return {"oi": (option, criterion, num(value))}
    if kind == "rating":
        option, criterion = target.split("/")
        return {"rating": (option, criterion, int(value))}
    if kind == "weight":
        return {"weight": (target, num(value))}
    if kind == "inp":
        return {"inp": {target: num(value)}}
    if kind == "threshold":
        return {"threshold": {target: num(value)}}
    if kind == "gatevalue":
        gate, options = target.split("/")
        return {"gatevalue": {gate: (options.split(";"), num(value))}}
    raise ValueError(f"unknown sensitivity kind {kind}")


def sen_cell(x):
    return "n/a" if x is None else f"{x:.2f}"


# ----------------------------------------------------------------------------- checks
def check(tables, prose, diagrams):
    errors = []

    def err(rid, message):
        errors.append(f"{rid}: {message}")

    t = tables
    engine = Engine(t)
    defined = set().union(*(set(v) for v in t.values()))
    # 1. generic
    for kind, rows in t.items():
        for rid, row in rows.items():
            for column, value in row.items():
                if column != "_line" and not value:
                    err(rid, f"empty cell in '{column}'")
            if kind in NEEDS_LABEL and row.get("Evidence") not in EVIDENCE:
                err(rid, f"evidence label '{row.get('Evidence')}' is invalid")
    for token in sorted(set(ID_ANY.findall(prose)) - defined):
        err(token, "referenced but never defined")

    # 2. stakeholders, workloads, requirements, targets
    for did, d in t["DEC"].items():
        maker = d["Decision-maker"]
        if maker not in t["STK"] or did not in t["STK"][maker]["Decision rights"]:
            err(did, f"decision-maker {maker} does not hold the decision right")
    for wid, w in t["WL"].items():
        if w["Consumer"] not in t["STK"] or not refs(w["Requirements"]):
            err(wid, "needs a stakeholder consumer and linked requirements")
    musts = []
    for rid, r in t["REQ"].items():
        if r["Type"] not in ("FR", "NFR", "DR") or r["Priority"] not in ("Must", "Should", "Could"):
            err(rid, "invalid type or priority")
        if r["Architecturally significant"] not in ("Y", "N") or r["AC measurable"] not in ("Y", "N") \
                or r["Regulatory or accountability need"] not in ("Y", "N"):
            err(rid, "Y/N fields must be Y or N")
        if PATTERN_TERMS.search(r["Requirement statement"]):
            err(rid, f"pattern or product term in requirement: "
                     f"{PATTERN_TERMS.search(r['Requirement statement']).group()}")
        if r["Workload"] != "all" and r["Workload"] not in t["WL"]:
            err(rid, "unknown workload")
        if r["Priority"] == "Must":
            musts.append(rid)
            if r["AC measurable"] == "Y" and not re.search(r"\d", r["Acceptance criterion"]):
                err(rid, "criterion marked measurable but contains no number")
    if musts and sum(t["REQ"][m]["AC measurable"] == "Y" for m in musts) / len(musts) < 0.9:
        err("REQ", "fewer than 90% of Musts have a measurable criterion")
    for tid, g in t["TGT"].items():
        if g["Requirement"] not in t["REQ"]:
            err(tid, "unknown requirement")

    # 3. registers
    for kind in ("CON", "ASM", "DEP", "RSK"):
        for rid, row in t[kind].items():
            if row["Status"] not in ("Active", "Open", "Monitoring", "Closed"):
                err(rid, f"invalid status {row['Status']}")
    for cid, c in t["CON"].items():
        if c["Fixed or negotiable"] not in ("Fixed", "Negotiable"):
            err(cid, "must be Fixed or Negotiable")
    for aid, a in t["ASM"].items():
        if a["Confidence"] not in LEVEL or a["Impact if wrong"] not in LEVEL \
                or a["Owner"] not in t["STK"] or num(a["Validation due (week)"]) is None:
            err(aid, "needs levels, a stakeholder owner and a numeric validation week")
    for did, d in t["DEP"].items():
        if d["Owner"] not in t["STK"] or num(d["Needed by (week)"]) is None:
            err(did, "needs a stakeholder owner and a numeric needed-by week")
    for rid, r in t["RSK"].items():
        p, i, e = num(r["Probability"]), num(r["Impact"]), num(r["Exposure"])
        if not (p in range(1, 6) and i in range(1, 6)) or e != p * i:
            err(rid, f"exposure {r['Exposure']} != {r['Probability']} x {r['Impact']}")
            continue
        band = "Lower" if e <= 4 else "Moderate" if e <= 9 else "High" if e <= 14 else "Very high"
        if r["Band"] != band:
            err(rid, f"band {r['Band']} != {band}")
        if r["Owner"] not in t["STK"]:
            err(rid, "needs a stakeholder owner")
        if e >= 10:
            for column in ("Response", "Trigger", "Escalation"):
                if r[column].lower() in ("none", "n/a"):
                    err(rid, f"high exposure needs '{column}'")
        if e >= 15 and r["Escalation"] not in t["STK"]:
            err(rid, "very high exposure must name an escalation authority")
    for uid, u in t["UNK"].items():
        if u["Blocks"] not in ("Blocks decision", "Manageable gap") or u["Owner"] not in t["STK"]:
            err(uid, "invalid 'Blocks' value or owner")

    # 4. estimates
    for iid, row in t["INP"].items():
        if row["Estimate label"] not in ESTIMATE_LABELS:
            err(iid, f"invalid estimate label {row['Estimate label']}")
        low, exp, high = (num(row[c]) for c in ("Low", "Expected", "High"))
        if None in (low, exp, high) or not low <= exp <= high:
            err(iid, "Low <= Expected <= High must hold and be numeric")
    values, unresolved = estimates(t)
    for eid in unresolved:
        err(eid, "cannot be evaluated")
    for eid, value in values.items():
        stated = num(t["EST"][eid]["Expected"])
        if stated is None or not close(stated, value):
            err(eid, f"stated {t['EST'][eid]['Expected']} != computed {value:.6g}")
    for output in {r["Output"] for r in t["TN"].values()}:
        swings = {}
        for iid, row in t["INP"].items():
            lo, hi = num(row["Low"]), num(row["High"])
            if lo == hi:
                continue
            a = estimates(t, "Expected", {iid: lo})[0].get(output)
            b = estimates(t, "Expected", {iid: hi})[0].get(output)
            if a is not None and b is not None and abs(b - a) > 1e-9:
                swings[iid] = (a, b, abs(b - a))
        rows = {r["Input"]: (rid, r) for rid, r in t["TN"].items() if r["Output"] == output}
        if set(rows) != set(swings):
            err(output, f"tornado inputs {sorted(rows)} differ from computed {sorted(swings)}")
        for iid, (a, b, s) in swings.items():
            if iid in rows:
                rid, r = rows[iid]
                rank = 1 + sum(1 for x in swings.values() if x[2] > s * (1 + 1e-9))
                for column, value in (("Output at low", a), ("Output at high", b), ("Swing", s)):
                    if not close(num(r[column]), value):
                        err(rid, f"{column} {r[column]} != computed {value:.5g}")
                if int(r["Rank"]) != rank:
                    err(rid, f"rank {r['Rank']} != computed {rank}")

    # 5. decisions, options
    axes_with_options = [d for d in t["DEC"] if d != "DEC-07"]
    for oid, o in t["OPT"].items():
        if o["Decision"] not in t["DEC"] or o["Role"] not in ("Baseline", "Alternative"):
            err(oid, "invalid decision or role")
        for column in ("Requires", "Conflicts"):
            if o[column] != "none" and not set(refs(o[column])) <= set(t["OPT"]):
                err(oid, f"unknown option in '{column}'")
        if o["Members"] != "n/a":
            members = refs(o["Members"])
            if o["Decision"] != "DEC-07" or not set(members) <= set(t["OPT"]):
                err(oid, "only DEC-07 options may list members, and they must exist")
            elif any(engine.decision_of(m) not in axes_with_options for m in members):
                err(oid, "members must belong to the axis decisions")
        elif o["Decision"] == "DEC-07":
            err(oid, "a combination option must list its members")
    for decision in t["DEC"]:
        opts = [r for r in t["OPT"].values() if r["Decision"] == decision]
        if sum(r["Role"] == "Baseline" for r in opts) != 1 or len(opts) < 3:
            err(decision, "needs exactly one baseline and at least three options")
    plain = [o for o in t["OPT"] if not engine.is_combo(o)]
    described = {r["Option"] for r in t["OD"].values()}
    for oid in plain:
        if oid not in described:
            err(oid, "has no conceptual description")
        if not any(r["Option"] == oid for r in t["TCO"].values()):
            err(oid, "has no cost components")
        if not any(r["Option"] == oid for r in t["DL"].values()):
            err(oid, "has no delivery estimate")
    for tid, row in t["TCO"].items():
        total = sum(num(row[c]) for c in ("Build and migration", "Three-year run and support", "Exit"))
        if num(row["Total"]) != total:
            err(tid, f"total {row['Total']} != {total:g}")

    # 6. criteria
    for decision in t["DEC"]:
        weights = [num(r["Weight"]) for r in t["CRIT"].values() if r["Decision"] == decision]
        if not close(sum(weights), 1.0, 1e-9):
            err(decision, f"weights sum to {sum(weights):.4f}, not 1")
    numeric = {r["Criterion"] for r in t["AN"].values()}
    for crit, bands in engine.bands.items():
        ordered = sorted(bands, key=lambda b: b[1])
        if crit not in t["CRIT"] or sorted(b[0] for b in bands) != [1, 2, 3, 4, 5]:
            err(crit, "bands must cover ratings 1 to 5 once for a known criterion")
        elif ordered[0][1] != 0 or ordered[-1][2] != math.inf:
            err(crit, "bands must start at 0 and end at inf")
        else:
            for (_, _, hi), (_, lo, _) in zip(ordered, ordered[1:]):
                if lo != hi + 1:
                    err(crit, f"gap or overlap between {hi} and {lo}")
    judged = {r["Criterion"] for r in t["JA"].values()}
    for crit in t["CRIT"]:
        if (crit in numeric) == (crit in judged):
            err(crit, "needs exactly one of numeric bands or judgement anchors")

    # 7. gates
    for gid, g in t["GT"].items():
        if g["Decision"] not in t["DEC"] or g["Operator"] not in ("<=", ">=", "n/a"):
            err(gid, "invalid decision or operator")
        if g["Applies to"] != "all" and not set(refs(g["Applies to"])) <= set(engine.options(g["Decision"])):
            err(gid, "'Applies to' must be 'all' or options of the decision")
        for opt in engine.options(g["Decision"]):
            gr_id, row = engine.gate_row(gid, opt)
            if engine.applies(gid, opt) != (row is not None):
                err(gid, f"{opt}: gate result presence does not match 'Applies to'")
                continue
            if row is None:
                continue
            if row["Result"] not in ("Pass", "Fail", "Pending"):
                err(gr_id, f"invalid result {row['Result']}")
            if g["Operator"] == "n/a":
                if row["Value"] != "n/a" or row["Value source"] != "n/a":
                    err(gr_id, "a qualitative gate has value and source n/a")
                continue
            if row["Value source"] in ("n/a", "judgement"):
                err(gr_id, "a numeric gate needs a numeric value source")
                continue
            value, expected = engine.gate_result(gid, opt, {})
            stated = num(row["Value"])
            if value is None or stated is None or not close(stated, value, 1e-3):
                err(gr_id, f"value {row['Value']} != source {row['Value source']} = {value}")
            if row["Result"] != expected:
                err(gr_id, f"result {row['Result']} != computed {expected}")

    # 8. eligibility, option inputs, scores
    for oid, o in t["OI"].items():
        if o["Value source"] == "judgement":
            if o["Input value"] != "judgement" or o["Rating"] not in {"1", "2", "3", "4", "5"}:
                err(oid, "a judgement row needs a rating from 1 to 5")
            continue
        value = engine.resolved_input(o, {})
        if value is None or not close(num(o["Input value"]), value, 2e-3):
            err(oid, f"input {o['Input value']} != source {o['Value source']} = {value}")
            continue
        band = engine.band(o["Criterion"], value)
        if str(band if band is not None else "n/a") != o["Rating"]:
            err(oid, f"rating {o['Rating']} != band {band}")
    for decision in t["DEC"]:
        eligible = set(engine.eligible(decision, {}))
        scores = engine.scores(decision)
        ranked = sorted((round(s, 2) for s in scores.values() if s is not None), reverse=True)
        rows = {r["Option"]: (sid, r) for sid, r in t["SC"].items() if r["Decision"] == decision}
        if set(rows) != set(engine.options(decision)):
            err(decision, "score table must list every option")
        frozen = [num(c["Frozen in week"]) for c in t["CRIT"].values() if c["Decision"] == decision]
        for option, (sid, r) in rows.items():
            if (r["Eligible"] == "Yes") != (option in eligible):
                err(sid, f"eligibility {r['Eligible']} != computed {option in eligible}")
                continue
            if option in eligible:
                if scores.get(option) is None:
                    err(sid, "eligible option lacks complete option inputs")
                    continue
                score = round(scores[option], 2)
                if num(r["Weighted score"]) != score:
                    err(sid, f"score {r['Weighted score']} != computed {score:.2f}")
                if int(r["Rank"]) != 1 + sum(1 for x in ranked if x > score):
                    err(sid, "rank does not match the scores")
            elif r["Weighted score"] != "n/a" or r["Rank"] != "n/a":
                err(sid, "an ineligible option must not carry a score")
            if num(r["Scored in week"]) <= max(frozen):
                err(sid, "scored before the criteria were frozen")

    # 9. sensitivity
    for sid, s in t["SEN"].items():
        scores = engine.scores(s["Decision"], parse_override(s))
        for option, value in scores.items():
            if value is None:
                err(sid, f"{option} becomes eligible but has no complete option inputs")
        winner, top, second = outcome(scores)
        for column, got in (("Winner", winner), ("Winner score", sen_cell(top)),
                            ("Runner-up score", sen_cell(second))):
            if s[column] != got:
                err(sid, f"{column} {s[column]} != computed {got}")

    # 10. records, recommendation, patterns
    recommended = None
    top7 = outcome(engine.scores("DEC-07"))
    if top7[0] in t["OPT"]:
        recommended = top7[0]
    for did, r in t["DR"].items():
        decision = r["Decision"]
        winner = outcome(engine.scores(decision))[0]
        if decision not in t["DEC"] or r["Axis winner"] != winner:
            err(did, f"axis winner {r['Axis winner']} != computed {winner}")
        if r["Selected option"] not in engine.options(decision):
            err(did, "selected option does not belong to the decision")
            continue
        if r["Selected option"] != r["Axis winner"]:
            cited = set(refs(r["Deviation reason"]))
            if not any(g in t["GT"] and t["GT"][g]["Decision"] == "DEC-07" for g in cited):
                err(did, "a selected option that is not the axis winner must cite a DEC-07 gate")
        if recommended and decision != "DEC-07" and r["Selected option"] not in engine.members(recommended):
            err(did, f"selected option is not a member of the recommended combination {recommended}")
        if r["Decision state"] not in ("Conditional", "Final"):
            err(did, "invalid decision state")
        elif r["Decision state"] == "Final":
            pending = [g for g in engine.gates(decision) if engine.applies(g, r["Selected option"])
                       and engine.gate_result(g, r["Selected option"], {})[1] == "Pending"]
            blocking = [u for u, x in t["UNK"].items() if decision in x["Decisions affected"]
                        and x["Blocks"] == "Blocks decision"]
            if pending or blocking:
                err(did, f"cannot be Final with pending gates {pending} or blocking unknowns {blocking}")
    for decision in t["DEC"]:
        if not any(r["Decision"] == decision for r in t["DR"].values()):
            err(decision, "has no decision record")
    if recommended:
        picked = {r["Selected option"] for r in t["DR"].values() if r["Decision"] != "DEC-07"}
        if picked != set(engine.members(recommended)):
            err("DR", f"selected options {sorted(picked)} differ from {recommended} members")
        roles = {r["Option"]: r for r in t["PR"].values()}
        if set(roles) != set(engine.members(recommended)):
            err("PR", "pattern roles must cover exactly the recommended members")
        keep = {r["Option"] for r in t["PT"].values()
                if r["Parsimony decision"].startswith("Keep") and r["Option"] != "none"}
        for opt in engine.members(recommended):
            if opt not in keep:
                err(opt, "recommended pattern has no 'Keep' entry in the parsimony test")
    for pid, r in t["PR"].items():
        if r["Option"] not in t["OPT"] or not set(refs(r["Requirement served"])) <= set(t["REQ"]) \
                or not refs(r["Requirement served"]):
            err(pid, "needs an option and requirements")
    if not any(r["Parsimony decision"] == "Remove" for r in t["PT"].values()):
        err("PT", "at least one pattern must be removed by the parsimony test")
    for pid, r in t["PT"].items():
        if r["Parsimony decision"] not in ("Keep", "Keep in staged form", "Remove"):
            err(pid, "invalid parsimony decision")
        if r["Parsimony decision"].startswith("Keep") and not refs(r["Requirement claimed"]):
            err(pid, "a kept pattern must trace to a requirement")

    # 11. view and controls
    if len(diagrams) != 1:
        err("diagram", f"expected one D10-DIAGRAM block, found {len(diagrams)}")
    else:
        shown = set(re.findall(r"\bELM-\d{2}\b", diagrams[0]))
        if shown != set(t["ELM"]):
            err("diagram", f"diagram elements {sorted(shown ^ set(t['ELM']))} differ from the element table")
    for eid, e in t["ELM"].items():
        if e["Pattern option"] != "none" and e["Pattern option"] not in t["OPT"]:
            err(eid, "unknown pattern option")
        if not refs(e["Requirement"]) or not set(refs(e["Requirement"])) <= set(t["REQ"]):
            err(eid, "every element must trace to a requirement")
        if recommended and e["Pattern option"] != "none" and e["Pattern option"] not in engine.members(recommended):
            err(eid, "element belongs to a pattern outside the recommendation")
    for rid, r in t["REQ"].items():
        if r["Regulatory or accountability need"] == "Y" and not any(rid in refs(c["Requirement"]) for c in t["CTL"].values()):
            err(rid, "a regulatory or accountability need has no control")
    for cid, c in t["CTL"].items():
        if c["Owner"] not in t["STK"] or not set(refs(c["Requirement"])) <= set(t["REQ"]):
            err(cid, "needs a stakeholder owner and existing requirements")
    for tid, r in t["TRG"].items():
        if r["Assumption"] not in t["ASM"] or r["Decision"] not in t["DEC"]:
            err(tid, "a trigger must tie to an existing assumption and decision")
    for aid, a in t["ASM"].items():
        if a["Impact if wrong"] == "High" and not any(r["Assumption"] == aid for r in t["TRG"].values()):
            err(aid, "a high-impact assumption has no revisit trigger")

    for aid, a in t["ADR"].items():
        if a["Status"] not in ("Proposed", "Accepted", "Deprecated", "Superseded") \
                or a["Decision state"] not in ("Conditional", "Final"):
            err(aid, "invalid status or decision state")
        if a["Status"] == "Accepted":
            err(aid, "Accepted needs a recorded approval; none exists in this pack")

    # 12. traceability
    traced = set()
    for trid, r in t["TR"].items():
        req, dec = r["Requirement"], r["Decision"]
        traced.add(req)
        gates = set(refs(r["Criterion or gate"]))
        owner = {**t["GT"], **t["CRIT"]}
        if req not in t["REQ"] or dec not in t["DEC"] or not gates \
                or any(g not in owner or owner[g]["Decision"] != dec for g in gates):
            err(trid, "criterion or gate must exist and belong to the decision")
        dr = next((x for x in t["DR"].values() if x["Decision"] == dec), None)
        if dr is None or r["Selected option"] != dr["Selected option"]:
            err(trid, "selected option differs from the decision record")
        el = t["ELM"].get(r["Element"])
        allowed = {r["Selected option"], "none"}
        if r["Selected option"] in t["OPT"] and engine.is_combo(r["Selected option"]):
            allowed |= set(engine.members(r["Selected option"]))
        if el is None or el["Pattern option"] not in allowed:
            err(trid, "element missing or belongs to a different pattern")
    for rid, req in t["REQ"].items():
        if req["Architecturally significant"] == "Y" and rid not in traced:
            err(rid, "architecturally significant requirement has no trace")
    for kind, column in (("FND", "Option"), ("LIM", "Option")):
        for rid, r in t[kind].items():
            if r.get(column) not in t["OPT"] and r.get(column) != "all":
                err(rid, "unknown option")
    for lid, l in t["LIM"].items():
        if l["Owner"] not in t["STK"] or not refs(l["Finding"]):
            err(lid, "needs an owner and a finding")
    return errors


# ----------------------------------------------------------------------------- derive and trace
def derive(tables):
    t = tables
    engine = Engine(t)
    values, _ = estimates(t)
    for eid in sorted(values):
        print(f"EST {eid} Expected = {fmt(values[eid])}")
    for output in sorted({r["Output"] for r in t["TN"].values()}):
        rows = []
        for iid, row in t["INP"].items():
            lo, hi = num(row["Low"]), num(row["High"])
            if lo == hi:
                continue
            a = estimates(t, "Expected", {iid: lo})[0].get(output)
            b = estimates(t, "Expected", {iid: hi})[0].get(output)
            if a is not None and b is not None and abs(b - a) > 1e-9:
                rows.append((iid, a, b, abs(b - a)))
        for iid, a, b, s in sorted(rows, key=lambda x: -x[3]):
            rank = 1 + sum(1 for x in rows if x[3] > s * (1 + 1e-9))
            print(f"TN {output} {iid} low={fmt(a)} high={fmt(b)} swing={fmt(s)} rank={rank}")
    for gid in sorted(t["GR"]):
        r = t["GR"][gid]
        g = t["GT"][r["Gate"]]
        if g["Operator"] == "n/a":
            continue
        value, result = engine.gate_result(r["Gate"], r["Option"], {})
        print(f"GR {gid} {r['Gate']} {r['Option']} value={fmt(value, 6)} result={result}")
    for decision in t["DEC"]:
        scores = engine.scores(decision)
        ranked = sorted((round(s, 2) for s in scores.values() if s is not None), reverse=True)
        eligible = set(engine.eligible(decision, {}))
        for sid, r in t["SC"].items():
            if r["Decision"] != decision:
                continue
            o = r["Option"]
            if o in eligible and scores.get(o) is not None:
                s = round(scores[o], 2)
                print(f"SC {sid} {o} eligible=Yes score={s:.2f} rank={1 + sum(1 for x in ranked if x > s)}")
            else:
                print(f"SC {sid} {o} eligible={'Yes' if o in eligible else 'No'} score=n/a rank=n/a")
    for sid, s in t["SEN"].items():
        scores = engine.scores(s["Decision"], parse_override(s))
        w, top, second = outcome(scores)
        print(f"SEN {sid} winner={w} top={sen_cell(top)} second={sen_cell(second)}")


def trace(tables, count, seed):
    t = tables
    rng = random.Random(seed)
    for trid in rng.sample(sorted(t["TR"]), min(count, len(t["TR"]))):
        r = t["TR"][trid]
        print(f"{r['Element']} -> {r['Selected option']} -> {r['Decision']} -> "
              f"{r['Criterion or gate'].split(';')[0].strip()} -> {r['Requirement']}: "
              f"{t['REQ'][r['Requirement']]['Requirement statement'][:60]}...")
    reqs = sorted(k for k, v in t["REQ"].items() if v["Architecturally significant"] == "Y")
    for rid in rng.sample(reqs, min(count, len(reqs))):
        hit = next((r for r in t["TR"].values() if r["Requirement"] == rid), None)
        if hit:
            print(f"{rid} -> {hit['Criterion or gate'].split(';')[0].strip()} -> {hit['Decision']} "
                  f"-> {hit['Selected option']} -> {hit['Element']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file")
    parser.add_argument("--derive", action="store_true")
    parser.add_argument("--trace", type=int, metavar="N")
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    tables, prose, diagrams, errors = parse(Path(args.file).read_text(encoding="utf-8"))
    if args.derive:
        derive(tables)
        return 0
    if args.trace:
        trace(tables, args.trace, args.seed)
        return 0
    if errors:  # structural problems: later checks would run on partial data
        for message in errors:
            print(f"ERROR {message}")
        print(f"{len(errors)} structural error(s); fix them first")
        return 1
    try:
        errors += check(tables, prose, diagrams)
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        errors.append(f"checker could not complete ({type(exc).__name__}: {exc}); "
                      f"a table is probably missing or malformed")
    print("Parsed: " + ", ".join(f"{k}={len(v)}" for k, v in sorted(tables.items())))
    for message in errors:
        print(f"ERROR {message}")
    print(f"{len(errors)} error(s)" if errors else "All checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

---

*End of document. Version 1.1, 2026-10-21.*
