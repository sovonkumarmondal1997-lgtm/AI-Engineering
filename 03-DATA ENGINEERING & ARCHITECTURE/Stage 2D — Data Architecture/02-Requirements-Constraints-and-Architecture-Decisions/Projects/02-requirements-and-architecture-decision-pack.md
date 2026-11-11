# Project 02 — Requirements and Architecture Decision Pack

> **Stage:** Stage 2D — Data Architecture
> **Module:** 2D.2 — Requirements, Constraints and Architecture Decisions
> **Project type:** Integrated architecture analysis and decision documentation (no implementation)
> **Roadmap source:** `roadmap-Requirements-Constraints-and-Architecture-Decisions.md`, Section 7
> **Project file:** `Projects/02-requirements-and-architecture-decision-pack.md`

---

## 0. Document control

| Item | Value |
| --- | --- |
| Document | Project specification and worked reference, deliverables D1–D13 |
| Version | 1.1 (post-audit) |
| Date | 2026-10-21 |
| Status | Complete as a project specification and worked reference. **Every Northbridge value is illustrative. No stakeholder has reviewed or approved anything in Section 6; every ADR status is `Proposed`.** |
| Audience | Learner running the project; independent reviewer auditing it |
| Scenario | *Northbridge Bank*, a fictional mid-sized retail and business bank (roadmap Section 7.2) |
| Evidence rule | Every row carries an evidence label (Section 4.3); estimates carry an estimate label |
| Companion tool | Consistency checker, Appendix B (`check_decision_pack.py`) |

**Change log**

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-10-21 | First complete design |
| 1.1 | 2026-10-21 | Post-audit: corrected the DEC-02 weight flip point (0.407, not 0.42), a sensitivity miscount, BO-04's source list and a stakeholder rights range; added the roadmap-required Status columns (D8) and weight rationale (D9); disclosed tier-model simplifications; corrected the wording on which gates are pending; added checker rules for objective sources and register status; confirmed the embedded checker equals the tested one |

**Reading order.** Sections 1–5 explain the project and how to run it. Section 6
is a complete, internally consistent worked reference (D1–D13). Section 7 is the
quality gate. Section 8 holds templates for a real organisation. Sections 9–11
cover pitfalls, hand-off and self-assessment. Appendix B is the checker.

---

## 1. Project overview

### 1.1 What this project is

A **requirements and architecture decision pack** is the auditable bundle of
evidence that turns a vague business request into *measurable requirements*, and
those requirements into *recorded, defensible architecture decisions*. It is the
working core of a Data Architect's role: the reader can walk from any decision
back to the business objective that justified it, and from any objective forward
to the decisions it drives.

The pack covers seven activities in one chain:

```text
Business objective (BO) ─► Requirement (REQ) ─► Target (TGT) / Estimate (EST)
        ─► Constraint (CON) · Assumption (ASM) · Dependency (DEP) · Risk (RSK) · Unknown (UNK)
        ─► Decision criterion (CRIT / GT) ─► Alternatives (OPT) ─► Trade-off (SC, SEN)
        ─► Architecture decision record (ADR)
```

### 1.2 Why organisations need it

| Situation | What goes wrong without the pack | What the pack provides |
| --- | --- | --- |
| A sponsor says "we need real-time data" | A technology is chosen first and justified afterwards | A measurable target, a timing budget and options that must pass gates |
| Several functions disagree on a number | Each team optimises locally; the disagreement persists | Recorded conflicts, definition owners and a decision with rejected alternatives |
| A regulator asks for lineage and accountability by a date | Work is scoped to the loudest voice, not the binding constraint | A constraint-driven gate and a traceable path from the obligation to the decision |
| A decision is challenged a year later | Nobody remembers the context, the alternatives or the assumptions | ADRs with context, evidence, rejected options and revisit triggers |

### 1.3 Business problem and decisions (from the roadmap)

**Problem.** Inconsistent customer data, slow availability of fraud signals, and
weak ability to evidence lineage and accountability.

**Architectural question.** Choose, and justify, the high-level approach for
consolidating customer and transaction data so that risk, finance, compliance and
fraud teams can work from a consistent, timely and governed view, **stopping at
decisions and their evidence**.

**Required decision boundaries** (roadmap Section 7.2), each at option-category level:

| Decision | Question |
| --- | --- |
| DEC-01 | How should card transactions reach the fraud case tool (the freshness path)? |
| DEC-02 | What approach should establish the authoritative customer record? |
| DEC-03 | What retention and storage-tiering approach should apply to transaction history? |

### 1.4 What this project is not

| It is not | Because |
| --- | --- |
| A platform design or build | Patterns, models, storage, integration, platform and cloud belong to modules 2D.3–2D.8 |
| A product selection | Options are categories; no vendor or product is evaluated |
| A migration or delivery plan | Plans follow accepted decisions |
| A source of facts about any real bank | Every Northbridge value is an illustrative assumption |

### 1.5 Success criteria

The pack is successful when an independent reviewer can (1) recompute the
figures, (2) trace three ADRs back to business objectives and three objectives
forward to ADRs, (3) agree that no option that fails a gate was rescued by a score,
and (4) agree that the evidence supports the conclusions (roadmap Section 7.7).

---

## 2. How to use this file

| | Mode A — Worked reference | Mode B — Real or realistic organisation |
| --- | --- | --- |
| Purpose | Study a complete example; critique it | Produce your own decision pack |
| Facts | Roadmap scenario only; all numbers illustrative | Your stakeholders, documents and measurements |
| What you do | Read Section 6; run the checker; challenge the example | Follow Section 5; use Section 8; produce your own D1–D13 |
| Output | Understanding and a critique list | A reviewed D1–D13 and a met completion gate |

**Rules in both modes**

1. **Requirements describe outcomes, not technology.** A technology name inside a requirement is a defect unless a business reason is recorded.
2. **Fix criteria and weights before scoring.** Record the freeze point; never tune after seeing totals.
3. **Gates are not weights.** A failed gate removes an option; a high score cannot restore it.
4. **Mark unknowns as unknown.** Never fill a gap with an invented fact.
5. **Show formulas, units and an evidence label for every number.** State decimal multiples (1 GB = 10⁹ bytes).
6. **Do not design or build.** Stop at decisions, evidence and conditions.

> **Honesty note for Mode A.** The roadmap supplies a handful of scenario facts and
> five illustrative starting figures. Everything else in Section 6 — other numbers,
> interview statements, costs, ratings — was invented for the exercise and is
> labelled `Illustrative assumption`. The worked reference demonstrates the
> method and the traceability; it recommends nothing for any real bank.

---

## 3. Concepts applied

| Concept (lesson) | Where it is applied |
| --- | --- |
| Stakeholder discovery, request → need, conflicts, hidden stakeholders ([Topic 1](../01-stakeholder-discovery-and-business-requirements.md)) | Steps 1–3; D1–D3; interview records INT; conflict log CF |
| Functional versus non-functional requirements, acceptance criteria, architecturally significant requirements ([Topic 2](../02-functional-and-non-functional-requirements.md)) | Steps 4–5; D4; the REQ register |
| Volume, velocity, variety, growth, peak and sensitivity ([Topic 3](../03-data-volume-velocity-variety-and-growth-estimation.md)) | Step 6; D6; INP / EST worksheet and tornado |
| Latency, throughput, freshness, availability, timing budgets ([Topic 4](../04-latency-throughput-freshness-and-availability-targets.md)) | Step 7; D7; TGT specification; TB timing budgets; availability composition |
| Constraints, assumptions, dependencies, risks, unknowns ([Topic 5](../05-constraints-assumptions-dependencies-and-risks.md)) | Step 8; D8; CON / ASM / DEP / RSK / UNK registers |
| Trade-offs, gates, weighted criteria, sensitivity, reversibility ([Topic 6](../06-architecture-trade-offs-and-decision-criteria.md)) | Steps 9–13; D9–D11 |
| Architecture decision records ([Topic 7](../07-architecture-decision-records-adrs.md)) | Steps 14–15; D12; D5 traceability |

**Roadmap project parts**

| Project part | Topics | Steps | Deliverables |
| --- | --- | --- | --- |
| Problem, stakeholders, business requirements | 1 | 1–3 | D1, D2, D3 |
| Requirements register, acceptance criteria | 2 | 4–5 | D4 |
| Estimation worksheet | 3 | 6 | D6 |
| Service-target specification | 4 | 7 | D7 |
| Constraints, assumptions, dependencies, risks | 5 | 8 | D8 |
| Criteria, alternatives, trade-off analysis | 6 | 9–13 | D9, D10, D11 |
| ADRs and decision log | 7 | 14 | D12 |
| Traceability, review, summary | 1–7 | 15–17 | D5, D13 |

**Carry-in from Module 2D.1.** The current-state inventory is the baseline for this
pack ([Project 01](../../01-Data-Architecture-Foundations-and-Principles/Projects/01-current-state-data-architecture-inventory.md)).
Its worked reference uses a separate illustrative model, so references below are
by topic, not by identifier.

| 2D.1 inventory finding (topic) | Where it enters this pack |
| --- | --- |
| Functions report different customer counts | BO-01, REQ-01, DEC-02 |
| Regulator asks for evidence of origin and accountability | BO-03, REQ-03, REQ-04, CON-04 |
| Customer attributes held in several systems with no designated authoritative source | DEC-02, RSK-05 |
| Departmental databases and spreadsheets carry reporting data | Out of scope here; open question for module 2D.3 |
| Warehouse and lake have overlapping roles | Out of scope here; open question for module 2D.3 |

---

## 4. Project governance and conventions

### 4.1 Roles and decision rights (RACI)

`R` responsible, `A` accountable (exactly one per row), `C` consulted, `I` informed.

| Activity or decision | Sponsor (STK-01) | Lead architect (STK-15) | Business owners (STK-02 to STK-05, STK-11) | Control functions (STK-06, STK-07, STK-12) | Engineering (STK-08, STK-13) | Internal Audit (STK-10) |
| --- | --- | --- | --- | --- | --- | --- |
| Approve scope and exclusions | A | R | C | C | C | I |
| Confirm business requirements | C | R | A | C | C | I |
| Approve binding constraints | C | R | C | A | C | I |
| Validate estimates and targets | I | R | C | C | A | I |
| Approve gates and criteria weights (before scoring) | A | R | C | C | C | I |
| Decide DEC-01, DEC-02, DEC-03 | A | R | C | C | C | I |
| Accept a residual risk | A | C | C | C | C | I |
| Independent review of evidence against conclusions | I | C | I | I | I | A |

The architect *recommends and records*; the sponsor *decides*; control functions
hold authority over their constraints. The architect never approves their own
exception (Module 2D.1, Lesson 05).

### 4.2 Scales, priorities and scoring rules

**Priority (Must / Should / Could).** Priority is a decision, not a property of the
sentence. Every requirement records the rule used.

| Rule | Meaning |
| --- | --- |
| M1 | Must: failure prevents the agreed business outcome |
| M2 | Must: failure violates a confirmed binding constraint |
| M3 | Must: failure removes an essential control |
| S1 | Should: materially improves the outcome; a controlled first release can proceed without it |
| C1 | Could: useful if capacity and budget allow |

**Risk scoring** (Topic 5; illustrative scales, to be agreed in a real project).
Probability and impact use 1–5. **Exposure = probability × impact** (1–25).

| Exposure | Band | Required response |
| --- | --- | --- |
| 1–4 | Lower | Monitor or accept with a named owner |
| 5–9 | Moderate | Proportionate action and review date |
| 10–14 | High | Owner, response, trigger and an explicit decision authority |
| 15–25 | Very high | Escalate to the designated decision authority |

Weeks 9 and later are post-pack follow-up weeks used for conditions that cannot close inside the eight-week pack. Every risk records its assessment horizon. Exposure is a prioritisation aid, not a
probability or a monetary loss.

**Weighted scoring** (Topic 6). Ratings use a 1–5 ordinal scale
(`1` poor, `3` acceptable, `5` very strong). Weights sum to 1 per decision.
`Score(option) = Σ weight × rating`. Numeric criteria are rated through
pre-agreed bands (Section 6.8); inputs are rounded half-up to a whole number
before banding. Judgement criteria use the written anchors in Section 6.8.

**Close-call rule.** A score difference below 0.15 (3% of the 5-point scale) is not
treated as a real preference; the decision stays conditional and the missing
evidence is named.

**Decision state.** A decision is **Final** only when every gate has passed (no
`Pending`), and no blocking unknown remains. Otherwise it is **Conditional**.

### 4.3 Evidence labels

| Label | Meaning |
| --- | --- |
| Verified fact | Supported by inspected evidence or a confirmed source |
| Stakeholder statement | What a person said; not independently verified |
| Illustrative assumption | A value invented for learning or planning |
| Inference | A reasoned interpretation, open to challenge |
| Open question | A matter not yet resolved |

**Estimate labels** (worksheet inputs): `measured`, `sampled`, `stated`,
`estimated`, `guessed`. Prefer `measured` over `guessed`; validate the highest-impact
`guessed` inputs first.

### 4.4 ID conventions

IDs are two-digit, stable and never reused. Cross-references use IDs only, so
traceability is machine-checkable.

| Prefix | Object | Prefix | Object |
| --- | --- | --- | --- |
| STK | Stakeholder | CRIT | Scored criterion |
| INT | Interview or workshop statement | GT | Hard gate |
| CF | Conflict | GR | Gate result |
| BO | Business objective | AN | Numeric rating band |
| REQ | Requirement | JA | Judgement rating anchor |
| TGT | Service target | OPT | Alternative (option) |
| INP | Estimation input | TCO | Cost components of an option |
| EST | Computed estimate | DL | Delivery estimate of an option |
| TN | Sensitivity ranking (tornado) | TB | Timing-budget stage |
| FACT | Supplied fact | OI | Option input and rating |
| CON | Constraint | SC | Score and eligibility |
| PREF | Preference | SEN | Sensitivity case |
| ASM | Assumption | DEC | Decision |
| DEP | Dependency | ADR | Architecture decision record |
| RSK | Risk | TR | Traceability row |
| UNK | Unknown | VL | Validation-log entry |

### 4.5 Confidentiality and handling

- Record roles, not named individuals.
- Do not copy customer records, credentials or connection details into the pack.
- Mark the pack with the organisation's classification; record the version and date on every artefact.

### 4.6 Suggested workspace layout (Mode B, optional)

```text
northbridge-decision-pack/                  # replace with the organisation name
├── 00-scope/            d1-scope.md, d2-stakeholders.md, interviews/
├── 01-requirements/     d3-business-requirements.md, d4-requirements-register.md
├── 02-quantification/   d6-estimation-worksheet.md, d7-service-targets.md
├── 03-risk/             d8-register.md
├── 04-decisions/        d9-criteria.md, d10-alternatives.md, d11-tradeoffs.md, adr/
├── 05-trace-and-review/ d5-traceability.md, review-notes.md, validation-log.md
├── 06-summary/          d13-summary.md
└── tools/               check_decision_pack.py (adapt header names)
```

Rationale: facts, quantification, risk, decisions and review are kept in separate
layers so that each can be reviewed and versioned independently. Keep one source
of truth per item; never copy a number between files by hand.

---

## 5. Execution plan

### 5.1 Timeline and effort (planning estimate, mid-sized organisation)

| Week | Steps | Main outcome | Effort (person-days, indicative) |
| --- | --- | --- | --- |
| 1 | 1, 2, 3 | Signed scope; stakeholder register; interview records | 5–7 |
| 2 | 4, 5 | Requirements register; acceptance criteria | 4–6 |
| 3 | 6, 7 | Estimation worksheet; service-target specification | 5–7 |
| 4 | 8, 9 | Constraint/assumption/risk register; **criteria and weights frozen** | 5–6 |
| 5 | 10, 11, 12 | Alternatives; gate results; scoring; trade-off analysis | 6–8 |
| 6 | 13, 14 | Recommendation; ADRs | 4–6 |
| 7 | 15, 16 | Traceability matrix; review and fixes | 4–5 |
| 8 | 17 | Final summary; challenge round | 3–4 |

Total indicative effort: **36–49 person-days**, plus about one day per interviewed
stakeholder group. These are planning figures, not measured results; re-plan after
Week 1.

### 5.2 Definitions of ready and done

| | Criteria |
| --- | --- |
| **Ready** | Sponsor named; decision boundaries agreed; a route to stakeholders, documents and source-system owners; confidentiality rules agreed |
| **Done** | Completion gate (Section 7.5) fully met; D1–D13 dated; independent reviewer agrees the evidence supports the conclusions |

### 5.3 The seventeen steps

Each step lists purpose, inputs, actions, the questions to answer, outputs and
validation, with pitfalls and the lessons it draws on.

#### Step 1 — Define the problem, objectives and boundaries

- **Purpose:** fix what is being decided and what is not.
- **Inputs:** scenario or request, sponsor goals, time and budget context.
- **Actions:** write the problem statement, objectives, in-scope and out-of-scope lists, the decision boundaries and labelled assumptions.
- **Questions:** What is being decided? What is deliberately excluded? Who sponsors it?
- **Output:** D1.
- **Validation:** the sponsor-role reviewer confirms scope; exclusions are as firm as inclusions.
- **Pitfalls:** scope phrased as a technology ("build a platform"); no exclusions.
- **Draws on:** Topic 1 (4.5, 5.6).

#### Step 2 — Identify stakeholders and decision responsibilities

- **Purpose:** know who decides, who is affected and who is missing.
- **Inputs:** organisation context, governance documents.
- **Actions:** build a register with role, interest, influence, decision rights, elicitation technique; add control functions and hidden stakeholders.
- **Questions:** Who has authority over each constraint? Who is affected but not in the room?
- **Output:** D2.
- **Validation:** every decision in Step 13 has a named decision-maker; control functions (risk, compliance, security, audit) are present.
- **Pitfalls:** omitting the data protection function, the product owner of a source system, or a consumer who reports a competing number.
- **Draws on:** Topic 1 (5.1, 6.3).

#### Step 3 — Gather and document business requirements

- **Purpose:** separate need from request and record success criteria.
- **Inputs:** interviews and workshops (record verbatim first).
- **Actions:** capture statements, classify them, ask why until the outcome is clear, write business objectives, log conflicts and open questions.
- **Questions:** What outcome is wanted? What does success look like? Where do stakeholders disagree?
- **Output:** D3 (BO register, interview records, conflict log).
- **Validation:** each BO has a source, a success criterion and no embedded solution.
- **Pitfalls:** treating "real-time" as a requirement; merging quote and interpretation.
- **Draws on:** Topic 1 (4.3–4.5, 5.3, 6.1, 6.6).

#### Step 4 — Identify functional and non-functional requirements

- **Purpose:** state explicit, classified, prioritised requirements.
- **Inputs:** Step 3 outputs.
- **Actions:** write each requirement in the pattern *[capability] shall [behaviour/quality] for [scope] under [conditions], measured by [metric], verified by [method]*; classify; prioritise using the rules in 4.2; flag architecturally significant requirements.
- **Questions:** Which requirements shape the architecture? Which conflict?
- **Output:** D4 (REQ register).
- **Validation:** types are distinct; each is sourced; no requirement names a technology.
- **Pitfalls:** making everything "Must"; mixing functional and non-functional obligations in one sentence.
- **Draws on:** Topic 2 (5.1, 5.5, 6.1, 6.2).

#### Step 5 — Define measurable acceptance criteria

- **Purpose:** make each important requirement testable.
- **Inputs:** Step 4 register.
- **Actions:** for each requirement define metric, target, scope, method and accepting role; mark requirements that cannot yet be tested and name what blocks them.
- **Questions:** How will each Must be tested, by whom, on what data?
- **Output:** acceptance criteria (columns of D4).
- **Validation:** every Must is testable; untestable ones are `Draft` with a blocking unknown.
- **Pitfalls:** a number without a method; a target nobody can measure.
- **Draws on:** Topic 2 (5.2, 5.3).

#### Step 6 — Estimate volume, rates, variety, retention and growth

- **Purpose:** quantify capacity inputs with ranges and evidence labels.
- **Inputs:** requirements, scenario figures, samples.
- **Actions:** list inputs with units and low/expected/high values; write each estimate as a formula; compute; rank inputs by their effect on key outputs (tornado); state interpretation.
- **Questions:** Which input matters most? Which is a guess?
- **Output:** D6 (INP, EST, TN).
- **Validation:** a reviewer recomputes at least three figures; units are consistent.
- **Pitfalls:** double-counting copies; confusing logical and physical volume; using an average peak.
- **Draws on:** Topic 3.

#### Step 7 — Define latency, throughput, freshness and availability targets

- **Purpose:** turn vague words into measurable service targets.
- **Inputs:** requirements and estimates.
- **Actions:** write each target with indicator, percentile, threshold, window, scope, boundary and method; build the timing budget; compose availability across dependencies.
- **Questions:** Is each target measurable? Is it achievable given the source cadence?
- **Output:** D7 (TGT, TB, availability estimates).
- **Validation:** stage budgets sum; availability composition is checked against the target.
- **Pitfalls:** averages instead of percentiles; ignoring the source batch cadence; "always available".
- **Draws on:** Topic 4.

#### Step 8 — Record constraints, assumptions, dependencies, risks and unknowns

- **Purpose:** bound the problem and expose what could invalidate a decision.
- **Inputs:** Steps 1–7.
- **Actions:** classify each item (fact, constraint, preference, assumption, dependency, risk, unknown); assign owners; score risks; set validation methods and dates for assumptions.
- **Questions:** What would invalidate a decision? Which unknown blocks a decision?
- **Output:** D8.
- **Validation:** no unclassified or ownerless item; every high-exposure risk has an owner, response and trigger; every high-impact assumption has a validation method and date.
- **Pitfalls:** treating a preference as a constraint; hiding an unknown inside an assumption.
- **Draws on:** Topic 5.

#### Step 9 — Establish decision criteria and prioritisation method

- **Purpose:** make the comparison fair before looking at options.
- **Inputs:** Steps 4–8.
- **Actions:** derive hard gates and scored criteria from requirements and constraints; set weights and rating bands; **freeze them and record the week**.
- **Questions:** Which criteria discriminate? Which are gates?
- **Output:** D9.
- **Validation:** each criterion traces to a REQ, CON or TGT; weights sum to 1; the freeze week precedes the scoring week.
- **Pitfalls:** a "heavy weight" used as a gate; changing weights after scoring.
- **Draws on:** Topic 6 (4.2, 4.3, 5.2, 5.3).

#### Step 10 — Identify plausible alternatives

- **Purpose:** compare real options, not straw men.
- **Inputs:** Steps 4–9.
- **Actions:** generate at least three feasible alternatives per decision, including a minimal-change baseline; describe each at option-category level and at comparable scope.
- **Questions:** Is each feasible within scope and constraints?
- **Output:** D10 (OPT).
- **Validation:** options that fail a gate are removed with a reason, not low-scored.
- **Pitfalls:** an intentionally weak baseline; a vendor product disguised as an option.
- **Draws on:** Topic 6 (4.4).

#### Step 11 — Compare alternatives

- **Purpose:** apply gates, then rate eligible options from evidence.
- **Inputs:** Steps 9–10.
- **Actions:** evaluate every gate for every option; record evidence; rate only eligible options with the frozen bands and anchors; compute weighted scores and verify arithmetic independently.
- **Questions:** Where is the evidence weakest?
- **Output:** gate results, option inputs, scores (D10).
- **Validation:** ratings cite evidence; ineligible options carry no score.
- **Pitfalls:** rating from impression; scoring an option that failed a gate.
- **Draws on:** Topic 6 (5.1, 5.4, 5.5).

#### Step 12 — Evaluate trade-offs, cost, risk, uncertainty and operations

- **Purpose:** test whether the ranking survives plausible change.
- **Inputs:** Step 11.
- **Actions:** sketch whole-life cost; vary the two least certain inputs and the weights; note reversibility and lock-in; identify flip points.
- **Questions:** What changes the ranking? What is traded away?
- **Output:** trade-off analysis (D11).
- **Validation:** sensitivity shows stability or the flip point; recheck gates after each change.
- **Pitfalls:** a weighted score rescuing an option that fails a gate under changed inputs.
- **Draws on:** Topic 6 (6.1–6.7).

#### Step 13 — Select and justify the preferred alternative

- **Purpose:** state a choice, its assumptions and the accepted trade-offs.
- **Inputs:** Steps 11–12.
- **Actions:** name the preferred option; mark the decision **Final** or **Conditional**; for conditional decisions list what is authorised now, what is not, the missing evidence, owner, date and fallback.
- **Questions:** What are we accepting? What would reverse the decision?
- **Output:** recommendation (D11).
- **Validation:** decision-maker identified; conditions explicit.
- **Pitfalls:** hiding a gate failure inside "we will validate later".
- **Draws on:** Topic 6 (6.8), Topic 7 (6.2).

#### Step 14 — Write ADRs

- **Purpose:** preserve the reasoning so a reader can reproduce it.
- **Inputs:** Step 13.
- **Actions:** one ADR per major decision using the structure in Topic 7; use the status vocabulary Proposed, Accepted, Deprecated, Superseded; keep a decision log.
- **Questions:** Could a reader reproduce the reasoning without the original meeting?
- **Output:** D12.
- **Validation:** Topic 7 checklist passed; no approval claimed without evidence.
- **Pitfalls:** one ADR for several decisions; omitting rejected alternatives.
- **Draws on:** Topic 7.

#### Step 15 — Link decisions to evidence

- **Purpose:** prove the chain from objective to ADR and back.
- **Inputs:** Steps 3–14.
- **Actions:** build the traceability matrix; run the checker; fix the source artefact first if a link reveals a gap.
- **Questions:** Can you walk ADR → BO and BO → ADR?
- **Output:** D5.
- **Validation:** a random trace test passes in both directions.
- **Pitfalls:** patching the ADR instead of the source artefact.
- **Draws on:** Topic 1 (6.5), Topic 2 (9.2).

#### Step 16 — Review for consistency and traceability

- **Purpose:** find contradictions before the sponsor does.
- **Inputs:** all artefacts.
- **Actions:** cross-check units and numbers across worksheet, targets and ADRs; apply the critical-error list in Section 7.4; record review notes and fixes.
- **Questions:** Is any unresolved contradiction presented as settled?
- **Output:** review notes (6.13).
- **Validation:** a reviewer finds no unflagged contradiction.
- **Pitfalls:** reviewing format instead of reasoning.
- **Draws on:** Topics 2, 6, 7.

#### Step 17 — Prepare the recommendation and summary

- **Purpose:** give the sponsor a readable decision readout.
- **Inputs:** all artefacts.
- **Actions:** write one to two pages: what is decided, why, at what cost and risk, what is conditional, what is open.
- **Questions:** What is decided, why, what is traded away?
- **Output:** D13.
- **Validation:** a non-specialist can follow it in ten minutes.
- **Pitfalls:** hiding conditions and limits.
- **Draws on:** Topics 6, 7.

---

## 6. Worked reference — Northbridge Bank

> **Everything in this section is illustrative.** Only the facts in 6.1 come from
> the roadmap scenario. Every other value is `Illustrative assumption`, `Inference`
> or `Open question`. No person or product is named. No stakeholder has validated
> any row. Run the checker (Appendix B) after any edit.

**Deliverable map**

| Deliverable | Section | Deliverable | Section |
| --- | --- | --- | --- |
| D1 Scope and problem | 6.1 | D8 Constraint/assumption/risk register | 6.6 |
| D2 Stakeholder register | 6.2 | D9 Criteria and prioritisation | 6.7 |
| D3 Business requirements | 6.3 | D10 Alternatives comparison | 6.8 |
| D4 Requirements register | 6.4 | D11 Trade-off analysis | 6.9 |
| D6 Estimation worksheet | 6.5 | D12 ADRs | 6.10 |
| D7 Service targets | 6.5 | D5 Traceability matrix | 6.11 |
|  |  | D13 Final summary | 6.12 |

### 6.1 D1 — Project scope and business problem (Step 1)

**Facts supplied by the roadmap scenario**

| ID | Statement | Source | Evidence |
| --- | --- | --- | --- |
| FACT-01 | The bank operates a core banking system, a separate cards platform, a CRM and a loan origination system | Roadmap scenario | Stakeholder statement |
| FACT-02 | Nightly extracts feed an enterprise data warehouse; a data lake created three years ago holds copies of some sources | Roadmap scenario | Stakeholder statement |
| FACT-03 | Risk, finance, marketing and compliance report different customer counts | Roadmap scenario | Stakeholder statement |
| FACT-04 | Fraud analysts see card transactions hours after the fact; the card platform emits batch files every 15 minutes today | Roadmap scenario | Stakeholder statement |
| FACT-05 | A regulator has asked for clearer evidence of lineage and customer-data accountability within a stated period | Roadmap scenario | Stakeholder statement |

| Element | Statement |
| --- | --- |
| Problem | Customer data is inconsistent across functions; fraud signals arrive late; the bank cannot readily evidence lineage and accountability |
| Objectives | BO-01 to BO-06 (6.3) |
| In scope | Customer, account and card-transaction data; consolidation and timeliness requirements; capacity and service targets at order-of-magnitude level; constraints and risks; high-level decisions |
| Out of scope | Detailed schema design; vendor product selection beyond option categories; implementation; migration plans; detailed cost negotiation; patterns (2D.3), modeling (2D.4), storage (2D.5), integration (2D.6), platform (2D.7), cloud (2D.8) |
| Decisions | DEC-01, DEC-02, DEC-03 (table below) |
| Labelled assumptions | ASM-01 to ASM-08 (6.6); roadmap starting figures INP-01, INP-02, INP-13 |
| Units | Decimal multiples; 365 days per year; 86,400 seconds per day; a 30-day month of 43,200 minutes |

**Decision boundaries**

| ID | Decision | Scope | Excluded | Decision-maker | Consulted | Needed by (week) | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DEC-01 | Freshness path for card transactions to the fraud case tool | Delivery of eligible card authorisations to the case tool for the first production release | The enterprise warehouse; the case-tool product; other card events | STK-01 | STK-05; STK-07; STK-08; STK-13 | 6 | Proposed |
| DEC-02 | Approach to the authoritative customer record | How a single governed customer identity and count are established | Schema design; vendor selection; data-quality tooling | STK-01 | STK-02; STK-03; STK-04; STK-06; STK-11; STK-12 | 6 | Proposed |
| DEC-03 | Retention and storage-tiering approach for transaction history | Placement of seven years of transaction records across tiers | Product selection; backup design; archive tooling | STK-01 | STK-06; STK-07; STK-04; STK-05 | 6 | Proposed |

### 6.2 D2 — Stakeholder register (Step 2)

| ID | Stakeholder (role) | Group | Interest | Influence | Decision rights | Elicitation technique | Key question | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| STK-01 | Chief data officer | Sponsor | One governed view; budget and delivery | High | Decides DEC-01, DEC-02, DEC-03; accepts residual risk; approves scope | Sponsor interview | Which outcome matters most if all three cannot be met? | Illustrative assumption |
| STK-02 | Head of retail | Business owner | One answer to how many customers exist | High | Consulted on DEC-02; owns retail customer definition | Interview | Which definition would you defend to the board? | Illustrative assumption |
| STK-03 | Head of risk | Business consumer | Exposure reports using a consistent customer count | Medium | Consulted on DEC-02; owns risk reporting requirements | Interview and report review | Which report breaks when counts differ? | Illustrative assumption |
| STK-04 | Head of finance | Business consumer | Financial reporting count; cost control | Medium | Consulted on DEC-02 and DEC-03; owns the finance count definition | Interview and report review | What does your count exclude and why? | Illustrative assumption |
| STK-05 | Head of fraud operations | Business owner | Card signals before the next attempt | High | Owns requirements REQ-05 to REQ-09; consulted on DEC-01 and DEC-03 | Interview and observation of analysts | What delay changes a fraud decision? | Illustrative assumption |
| STK-06 | Compliance officer | Control function | Lineage, accountability, retention, regulator liaison | High | Authority over CON-02 and CON-04; consulted on DEC-02 and DEC-03 | Interview and document review | What exact evidence will the regulator accept and by when? | Illustrative assumption |
| STK-07 | Security lead | Control function | Access control, identity, exposure of copies | High | Authority over CON-05 and the security gate; consulted on DEC-01 and DEC-03 | Interview and policy review | Which access paths need your approval? | Illustrative assumption |
| STK-08 | Engineering leads (core, cards, CRM, data platform) | Technology | Feasible, operable solutions; protect the batch window | High | Owns feasibility estimates; consulted on DEC-01 | Technical workshop | What can each source system emit today? | Illustrative assumption |
| STK-09 | Operations lead | Operations | Runbooks, support load, batch window | Medium | Owns CON-03 operations; consulted on operability ratings | Interview | What breaks most often in the nightly flow? | Illustrative assumption |
| STK-10 | Internal audit | Independent review | Evidence quality and traceability | Medium | Independent reviewer of evidence against conclusions | Interview | Which evidence would you accept for lineage? | Illustrative assumption |
| STK-11 | Head of marketing | Business consumer (hidden) | Customer count used for campaigns | Medium | Consulted on DEC-02; owns the marketing count definition | Interview and report review | Which customers do you count and why? | Inference |
| STK-12 | Data protection officer | Control function (hidden) | Residency, privacy, lawful use of copies | High | Authority over CON-01; consulted on DEC-02 | Interview and policy review | Which copies and backups need your approval? | Inference |
| STK-13 | Card platform product owner | Source owner (hidden) | Changes to the card platform; vendor commitments | High | Owns DEP-01 and DEP-05; consulted on DEC-01 | Technical workshop | What change can you commit to, and when? | Inference |
| STK-14 | Architecture review board | Governance forum | Consistency with principles; recorded decisions | Medium | Reviews ADRs | Review meeting | Which principle does this decision bend? | Illustrative assumption |
| STK-15 | Lead architect | Author | Reproducible, defensible decisions | Medium | Recommends; does not decide | Self-review | Could a stranger reproduce this reasoning? | Illustrative assumption |

### 6.3 D3 — Business requirements (Step 3)

**Interview and workshop statements** (hypothetical; recorded verbatim before interpretation)

| ID | Stakeholder | Verbatim statement (hypothetical) | Classification | Interpretation (kept separate) | Evidence |
| --- | --- | --- | --- | --- | --- |
| INT-01 | STK-05 | "We need real-time customer data." | Request | Fraud analysts need card events fast enough to act; the delay that matters is unknown | Illustrative assumption |
| INT-02 | STK-05 | "By the time a transaction shows up in our case tool, the card has often been used again." | Need | Freshness target is tied to the next transaction attempt | Illustrative assumption |
| INT-03 | STK-03 | "My exposure report must use the same customer count finance quotes." | Need | Risk and finance must agree a definition | Illustrative assumption |
| INT-04 | STK-04 | "Finance excludes closed accounts from its count and I will not change that." | Conflict | A definition owner defends a population boundary | Illustrative assumption |
| INT-05 | STK-11 | "Marketing counts anyone we can email." | Conflict | A third population boundary exists | Illustrative assumption |
| INT-06 | STK-06 | "The regulator wants to see where customer data comes from and who answers for it, and there is a date." | Constraint | A binding obligation with a milestone; date not supplied | Illustrative assumption |
| INT-07 | STK-07 | "Personal data stays in-country and everything goes through our existing identity provider." | Constraint | Residency and identity constraints | Illustrative assumption |
| INT-08 | STK-01 | "I would like to reuse the event platform the lake team trialled last year." | Preference | A sponsor technology preference; not a constraint | Illustrative assumption |
| INT-09 | STK-08 | "The card platform can only drop files today; events would need a change from the product team." | Dependency | Event-based options depend on the card platform owner | Illustrative assumption |
| INT-10 | STK-09 | "Nothing may touch core banking before its batch finishes at 02:30." | Constraint | Extraction timing constraint | Illustrative assumption |
| INT-11 | STK-02 | "I do not care how it is built; I want one answer to how many customers we have." | Need | Outcome is a single governed count | Illustrative assumption |
| INT-12 | STK-06 | "Keep transaction records seven years; auditors sometimes ask for older ones." | Constraint | Seven-year retention; possible extension unconfirmed | Illustrative assumption |
| INT-13 | STK-12 | "Copies of personal data outside the permitted jurisdiction, backups included, are not acceptable." | Constraint | Residency covers backups and copies | Illustrative assumption |
| INT-14 | STK-05 | "Investigators usually look back two years, sometimes more." | Assumption | Interactive look-back of about 24 months, unmeasured | Illustrative assumption |

**Conflict log**

| ID | Conflict | Parties | Interests | Evidence needed | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| CF-01 | Three or more definitions of a customer exist (INT-03, INT-04, INT-05, INT-11) | STK-02; STK-03; STK-04; STK-11 | Each protects a reporting purpose and population boundary | Written definitions and sample counts per definition | STK-01 | Open |
| CF-02 | Sponsor prefers a technology while gates and options are still open (INT-08, PREF-01) | STK-01; STK-08 | Reuse and speed versus fit to the freshness gate | Gate results and operability evidence for each option | STK-15 | Open |
| CF-03 | Interactive look-back of two years versus "sometimes more" (INT-14) | STK-05; STK-06 | Investigator speed versus cost of keeping data interactive | Query-log sample (ASM-04) | STK-05 | Open |

**Business objectives**

| ID | Business objective | Source | Success criterion (proposed) | Priority | Open questions | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| BO-01 | One governed, reproducible customer count and definition used by risk, finance, marketing and compliance | STK-02; STK-03; STK-04; STK-11 (INT-03, INT-04, INT-05, INT-11) | For any approved definition and as-of date, counts published to the four functions reconcile exactly, and each definition has a named owner | Must | Which definitions are approved? (UNK-04) | Illustrative assumption |
| BO-02 | Fraud analysts see card transactions in time to act before the customer's next attempt | STK-05 (INT-01, INT-02) | Eligible card authorisations are visible in the case tool within the validated freshness target (TGT-01) | Must | What delay actually changes a decision? What fields does the case tool need? (UNK-05) | Illustrative assumption |
| BO-03 | Evidence of lineage and an accountable owner for customer data by the regulatory milestone | STK-06 (INT-06) | For sampled customer attributes, owner and lineage to source are evidenced on request before the milestone | Must | What is the exact milestone and evidence format? (UNK-01) | Illustrative assumption |
| BO-04 | Seven years of transaction records retained, retrievable and affordable | STK-06; STK-05; STK-04 (INT-12, INT-14) | Records are retrievable within stated times; storage cost stays within the approved budget | Must | Will retention be extended? What look-back covers most queries? | Illustrative assumption |
| BO-05 | Personal data stays in the permitted jurisdiction and under the existing identity and access controls | STK-07; STK-12 (INT-07, INT-13) | No store, replica or backup of personal data outside the jurisdiction; all access uses the existing identity provider | Must | Are vendor-support access paths covered? | Illustrative assumption |
| BO-06 | Delivery within the sponsor's budget ceiling without disrupting the core banking batch | STK-01; STK-09 (INT-10) | Spend within the ceiling; the core batch completes by 02:30 on every business day during and after rollout | Must | What is the ceiling? (UNK-03) | Illustrative assumption |

### 6.4 D4 — Functional and non-functional requirements register (Steps 4 and 5)

Type codes: `FR` functional, `NFR` non-functional, `DR` data. AC = acceptance criterion;
"AC measurable" records whether the criterion is testable *in form* (parameter values
still pending are named in the status).

| ID | Requirement statement | Type | Quality attribute | BO | Priority | Priority rule | Acceptance criterion | AC measurable | Verification method | Accepting role | Source | Status | Architecturally significant | Linked IDs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-01 | The consolidated customer view shall publish one customer count per approved definition to risk, finance, marketing and compliance | FR | n/a | BO-01 | Must | M1 | For a chosen definition and as-of timestamp, the counts delivered to all four functions differ by 0 | Y | Reconciliation test on a chosen as-of date | STK-02 | STK-02; STK-03 | Draft | Y | TGT-08; CF-01 |
| REQ-02 | Every published customer count shall state its definition version and as-of timestamp | FR | n/a | BO-01 | Must | M1 | 100% of 30 sampled published counts carry both fields | Y | Sample inspection | STK-03 | STK-03; STK-04 | Draft | N | TGT-08 |
| REQ-03 | Each in-scope customer attribute shall have a named accountable owner and a named authoritative source | DR | n/a | BO-03 | Must | M2 | The ownership register lists both for 100% of attributes on the list approved by Compliance | Y | Register inspection | STK-06 | STK-06 | Draft | Y | CON-04; DEP-03 |
| REQ-04 | For any published customer attribute value, the consolidated view shall supply lineage to the source records and transformations applied | FR | n/a | BO-03 | Must | M2 | Lineage is produced for 100% of 25 sampled values, each within 4 working hours of request | Y | Sampled lineage requests | STK-06 | STK-06 | Draft | Y | TGT-09; CON-04 |
| REQ-05 | Eligible card authorisations shall reach the fraud case tool with the fields the analysts need to open a case | FR | n/a | BO-02 | Must | M1 | 100% of 200 test events contain every field on the approved field list | Y | Test-event inspection | STK-05 | STK-05 | Draft | N | UNK-05; DEP-05 |
| REQ-06 | Eligible card authorisations shall be visible in the case tool within the freshness target | NFR | Freshness | BO-02 | Must | M1 | p95 freshness is 30 s or less during 08:00–20:00 local time over a rolling 30 days | Y | Timestamp correlation of event IDs | STK-05 | STK-05 | Draft | Y | TGT-01; ASM-02; DEP-01; DEP-02 |
| REQ-07 | Eligible card authorisations shall be visible within a relaxed target outside the staffed hours | NFR | Freshness | BO-02 | Should | S1 | p95 freshness is 300 s or less outside 08:00–20:00 over a rolling 30 days | Y | Timestamp correlation of event IDs | STK-05 | STK-05 | Draft | N | TGT-02 |
| REQ-08 | The card-transaction delivery path shall be available | NFR | Availability | BO-02 | Must | M1 | At least 99.9% of 1-minute intervals in each rolling 30 days have no undelivered backlog older than 5 minutes | Y | Interval monitoring | STK-05 | STK-05 | Draft | Y | TGT-03; RSK-02 |
| REQ-09 | Card authorisations delivered to the case tool shall be complete | NFR | Completeness | BO-02 | Must | M1 | At least 99.99% of eligible source authorisations are present in the case tool within 24 hours, measured daily with missing and duplicate counts reported separately | Y | Daily source-to-target reconciliation | STK-05 | STK-05 | Draft | N | TGT-04 |
| REQ-10 | The delivery path shall sustain peak card-event load with headroom | NFR | Throughput | BO-02 | Must | M1 | A load test sustains at least 138.9 events/s (EST-13) for 30 minutes with no growth in backlog | Y | Load test with realistic payloads | STK-08 | STK-08 | Draft | Y | TGT-05; EST-13; ASM-03 |
| REQ-11 | Personal data shall be stored and processed only in the permitted jurisdiction, including replicas and backups | NFR | Residency | BO-05 | Must | M2 | 100% of stores, replicas and backups in the environment inventory are located in the permitted jurisdiction | Y | Inventory inspection and audit | STK-12 | STK-12; STK-07 | Draft | Y | CON-01; RSK-07 |
| REQ-12 | Access to consolidated customer and card data shall use the existing identity provider with role-based authorisation | NFR | Security | BO-05 | Must | M2 | 100% of access paths in the access-path inventory pass authentication and authorisation tests before release | Y | Access-path tests | STK-07 | STK-07 | Draft | Y | CON-05 |
| REQ-13 | All access to personal data in the consolidated view shall be logged and the logs retained | NFR | Auditability | BO-05 | Must | M3 | Log retention equals the period set by Compliance policy (value pending UNK-02) and 100% of 50 sampled access events are logged | Y | Policy comparison and sample test | STK-06 | STK-06 | Draft | N | UNK-02 |
| REQ-14 | Transaction records shall be retained for seven years from posting date | DR | n/a | BO-04 | Must | M2 | In a sample of 50 records aged up to 7 years, 100% are present and none is deleted before 7 years | Y | Retention audit | STK-06 | STK-06 | Draft | Y | CON-02; INP-13 |
| REQ-15 | Any in-scope transaction record younger than seven years shall be retrievable on request | NFR | Retrievability | BO-04 | Must | M2 | 100% of retrieval requests in a test of 20 are completed within 24 hours | Y | Retrieval test across all ages | STK-06 | STK-06 | Draft | Y | TGT-06; ASM-08 |
| REQ-16 | Transaction records younger than 24 months shall be available for interactive investigator queries | NFR | Performance | BO-04 | Must | M1 | p95 query time is 5 s or less for the agreed investigator query set on data aged under 24 months | Y | Query benchmark on the agreed set | STK-05 | STK-05 | Draft | Y | TGT-07; ASM-04 |
| REQ-17 | Programme cost shall remain within the sponsor's budget ceiling | NFR | Cost | BO-06 | Must | M1 | Three-year total cost of ownership is at or below the ceiling value (pending UNK-03) | Y | Finance-reviewed cost model | STK-04 | STK-01 | Draft | Y | CON-06; UNK-03 |
| REQ-18 | Lineage and ownership capability shall be operational by the regulatory milestone | NFR | Delivery | BO-03 | Must | M2 | The evidence pack is accepted by Compliance before the milestone date (pending UNK-01) | Y | Compliance acceptance of the evidence pack | STK-06 | STK-06 | Draft | Y | CON-04; ASM-01; UNK-01 |
| REQ-19 | Every component on the card path shall have an assigned operational owner and a runbook before go-live | NFR | Operability | BO-06 | Should | S1 | 100% of components have a named owner and a runbook reviewed by Operations | Y | Pre-go-live checklist | STK-09 | STK-09 | Draft | N | none |
| REQ-20 | Analysts shall be able to look up the customer record linked to a card transaction when opening a case | FR | n/a | BO-02 | Should | S1 | For 100 sampled cases, the linked customer record is shown in 95% or more | Y | Case walkthrough | STK-05 | STK-05 | Draft | N | RSK-05 |
| REQ-21 | Card transactions with an unresolvable customer identifier shall be rare | NFR | Data quality | BO-01 | Should | S1 | At most 0.1% of daily card transactions have no resolvable customer identifier | Y | Daily exception report | STK-02 | STK-02 | Draft | N | ASM-06 |
| REQ-22 | Published customer attributes shall have a documented data contract with definition, owner and change notification | DR | n/a | BO-03 | Should | S1 | 100% of attributes on the Compliance-approved list have a contract entry reviewed by the owner | Y | Contract register inspection | STK-06 | STK-06 | Draft | N | DEP-03 |
| REQ-23 | Stewards could view ownership and lineage status in a self-service report | FR | n/a | BO-03 | Could | C1 | Deferred; no acceptance test defined yet | N | none | STK-06 | STK-06 | Draft | N | none |
| REQ-24 | Extraction from core banking shall not delay the core batch completion beyond 02:30 | NFR | Operational impact | BO-06 | Must | M2 | The core batch completes by 02:30 on 100% of business days in a 30-day trial | Y | Batch completion log comparison | STK-09 | STK-09 | Draft | Y | CON-03; RSK-09 |

**Architecturally significant requirements.** REQ-01, 03, 04, 06, 08, 10, 11, 12, 14,
15, 16, 17, 18 and 24 can eliminate whole classes of options. They are candidate
implications, not decisions: REQ-06 and REQ-10 shape DEC-01; REQ-01, 03, 04 and 18
shape DEC-02; REQ-14, 15 and 16 shape DEC-03; REQ-11, 12, 17 and 24 apply to all three.

### 6.5 D6 and D7 — Estimation worksheet and service targets (Steps 6 and 7)

#### 6.5.1 Estimation inputs (D6)

**Confidence follows the label:** `measured` and `sampled` give High or Medium confidence, `stated` Medium, `estimated` Low to Medium and `guessed` Low.

**Case convention.** `Low case` is the low-volume bounding case and `High case` the
high-volume bounding case, with every input moved together. They are stress bounds,
not statistical intervals. For non-volume inputs (compression, price) the low case
uses the value that gives the lower stored volume or cost.

| ID | Input | Unit | Low case | Expected | High case | Estimate label | Basis and validation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| INP-01 | Retail customers | customers | 2,700,000 | 3,000,000 | 3,300,000 | stated | Roadmap scenario (about 3 million); validate against the customer master count (UNK-04) |
| INP-02 | Card transactions per day | records/day | 1,600,000 | 2,000,000 | 2,600,000 | stated | Roadmap scenario (about 2 million); validate from source counts (ASM-03) |
| INP-03 | Average serialised card-transaction size | bytes | 400 | 500 | 650 | estimated | Illustrative; sample from representative records (ASM-05) |
| INP-04 | Other card events per day | events/day | 3,500,000 | 5,000,000 | 7,000,000 | guessed | Illustrative; event types and counts unknown |
| INP-05 | Average other-event size | bytes | 600 | 700 | 900 | guessed | Illustrative; sample |
| INP-06 | Customer-profile changes per day | changes/day | 70,000 | 100,000 | 150,000 | guessed | Illustrative; take from CRM change history |
| INP-07 | Average profile-change record size | bytes | 800 | 1,000 | 1,400 | guessed | Illustrative; sample |
| INP-08 | Annual volume growth | fraction/year | 0.05 | 0.15 | 0.25 | guessed | Illustrative; measure from 24 months of history (ASM-07) |
| INP-09 | Peak-to-average factor (one-minute window) | ratio | 3 | 4 | 10 | guessed | Illustrative; derive from time-bucketed history (ASM-03) |
| INP-10 | Compression ratio (uncompressed ÷ compressed) | ratio | 3.0 | 2.0 | 1.5 | guessed | Illustrative; test on representative data |
| INP-11 | Retained copies per layer | copies | 2 | 2 | 3 | stated | Illustrative copy policy; confirm with resilience owner |
| INP-12 | Metadata and index overhead on top of copies | fraction | 0.05 | 0.10 | 0.20 | guessed | Illustrative; measure |
| INP-13 | Retention period | years | 7 | 7 | 7 | stated | Constraint CON-02 |
| INP-14 | Retained layers (raw and processed) | layers | 2 | 2 | 2 | estimated | Illustrative simplification: same volume in both layers |
| INP-15 | Capacity safety factor | ratio | 1.25 | 1.5 | 2.0 | estimated | Illustrative; justify with load tests |
| INP-16 | Average customer record size | bytes | 1,500 | 2,000 | 3,000 | estimated | Illustrative; sample |
| INP-17 | Interactive (standard) tier price | currency/TB-month | 20 | 23 | 26 | guessed | Placeholder, not a quote |
| INP-18 | Infrequent-access tier price | currency/TB-month | 10 | 12.5 | 15 | guessed | Placeholder, not a quote |
| INP-19 | Archive tier price | currency/TB-month | 3 | 4 | 5 | guessed | Placeholder, not a quote |
| INP-20 | Availability: source capture or publication | fraction | 0.9995 | 0.9995 | 0.9995 | stated | Illustrative provider statement; not measured |
| INP-21 | Availability: transport and queue | fraction | 0.9995 | 0.9995 | 0.9995 | stated | Illustrative provider statement; not measured |
| INP-22 | Availability: processing | fraction | 0.999 | 0.999 | 0.999 | stated | Illustrative provider statement; not measured |
| INP-23 | Availability: target store | fraction | 0.9995 | 0.9995 | 0.9995 | stated | Illustrative provider statement; not measured |
| INP-24 | Availability: case-tool integration | fraction | 0.9995 | 0.9995 | 0.9995 | stated | Illustrative provider statement; not measured |
| INP-25 | Availability: second processing instance | fraction | 0.999 | 0.999 | 0.999 | stated | Illustrative; assumes independent failure |
| INP-26 | Availability target (TGT-03) | fraction | 0.999 | 0.999 | 0.999 | stated | REQ-08 |
| INP-27 | Eligible minutes in a 30-day month | minutes | 43,200 | 43,200 | 43,200 | stated | 30 × 24 × 60 |
| INP-28 | Components in series on the card path | components | 5 | 5 | 5 | stated | INP-20 to INP-24 |

#### 6.5.2 Computed estimates (D6)

Expressions use the IDs above; `**` means power. Results use four significant digits.

| ID | Estimate | Expression | Unit | Low case | Expected | High case | Interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EST-01 | Daily logical volume, card transactions | `INP-02*INP-03/1000000000` | GB/day | 0.64 | 1 | 1.69 | 1.0 GB/day expected, before copies, overhead and retention |
| EST-02 | Daily logical volume, other card events | `INP-04*INP-05/1000000000` | GB/day | 2.1 | 3.5 | 6.3 | Largest feed and the most uncertain |
| EST-03 | Daily logical volume, profile changes | `INP-06*INP-07/1000000000` | GB/day | 0.056 | 0.1 | 0.21 | Small |
| EST-04 | Total daily logical volume | `EST-01+EST-02+EST-03` | GB/day | 2.796 | 4.6 | 8.2 | Sum of three feeds |
| EST-05 | Year-1 annual logical volume | `EST-04*365/1000` | TB/year | 1.021 | 1.679 | 2.993 | Generation in the base year |
| EST-06 | Year-7 annual logical volume | `EST-05*(1+INP-08)**(INP-13-1)` | TB/year | 1.368 | 3.884 | 11.42 | Annual rate in Year 7, not a cumulative total |
| EST-07 | Cumulative 7-year logical volume | `EST-05*((1+INP-08)**INP-13-1)/INP-08` | TB | 8.309 | 18.58 | 45.11 | Sum of Years 1 to 7 under compound growth |
| EST-08 | Physical multiplier | `INP-14*INP-11*(1+INP-12)/INP-10` | ratio | 1.4 | 2.2 | 4.8 | Layers × copies × overhead ÷ compression |
| EST-09 | Cumulative 7-year physical volume | `EST-07*EST-08` | TB | 11.63 | 40.88 | 216.6 | Order of magnitude for storage planning; the high case is a stress bound |
| EST-10 | Average event rate, all feeds | `(INP-02+INP-04+INP-06)/86400` | events/s | 59.84 | 82.18 | 112.8 | Full-day average, evenly spread |
| EST-11 | Peak event rate, all feeds | `EST-10*INP-09` | events/s | 179.5 | 328.7 | 1128 | The peak factor dominates |
| EST-12 | Peak card-transaction rate | `INP-02/86400*INP-09` | events/s | 55.56 | 92.59 | 300.9 | Rate the fraud path must absorb |
| EST-13 | Required throughput capacity | `EST-12*INP-15` | events/s | 69.44 | 138.9 | 601.9 | Capacity to demonstrate under load (REQ-10) |
| EST-14 | Peak card-transaction payload rate | `EST-12*INP-03/1000` | kB/s | 22.22 | 46.30 | 195.6 | Payload only, before framing and retries |
| EST-15 | Extra volume if retention moves from 7 to 10 years | `(((1+INP-08)**10-1)/((1+INP-08)**7-1)-1)*100` | % | 54.48 | 83.47 | 120.6 | Growth makes a longer window cost more than the 43% a flat stream implies |
| EST-16 | Customer-record snapshot volume | `INP-01*INP-16/1000000000` | GB | 4.05 | 6 | 9.9 | Customer data is small; volume does not discriminate DEC-02 |
| EST-17 | Year-7 generation, physical | `EST-05*(1+INP-08)**6*EST-08` | TB | 1.915 | 8.544 | 54.80 | Newest year |
| EST-18 | Year-6 generation, physical | `EST-05*(1+INP-08)**5*EST-08` | TB | 1.823 | 7.430 | 43.84 | Second newest year |
| EST-19 | Years 1 to 5 generation, physical | `EST-05*((1+INP-08)**5-1)/INP-08*EST-08` | TB | 7.895 | 24.91 | 117.9 | Oldest five years |
| EST-20 | Monthly storage cost, OPT-09 (all standard) | `(EST-19+EST-18+EST-17)*INP-17` | currency/month | 232.7 | 940.2 | 5630 | Baseline at the end of Year 7 |
| EST-21 | Monthly storage cost, OPT-10 (standard, then archive) | `(EST-17+EST-18)*INP-17+EST-19*INP-19` | currency/month | 98.45 | 467.0 | 3154 | Years 6 and 7 interactive; Years 1 to 5 archive |
| EST-22 | Monthly storage cost, OPT-11 (three tiers) | `EST-17*INP-17+EST-18*INP-18+EST-19*INP-19` | currency/month | 80.21 | 389.0 | 2672 | Year 7 standard, Year 6 infrequent, Years 1 to 5 archive |
| EST-23 | Cost reduction of OPT-10 against OPT-09 | `(1-EST-21/EST-20)*100` | % | 57.69 | 50.33 | 43.98 | Saving shrinks as volume grows because the interactive tier carries more |
| EST-24 | Cost reduction of OPT-11 against OPT-09 | `(1-EST-22/EST-20)*100` | % | 65.52 | 58.63 | 52.54 | About eight points more than OPT-10 |
| EST-25 | Serial availability of the card path | `INP-20*INP-21*INP-22*INP-23*INP-24` | fraction | 0.997003 | 0.997003 | 0.997003 | 99.70%, below the 99.9% target |
| EST-26 | Allowed downtime at the target | `(1-INP-26)*INP-27` | minutes/30 days | 43.2 | 43.2 | 43.2 | Total budget for all qualifying outages |
| EST-27 | Availability with a second processing instance | `INP-20*INP-21*(1-(1-INP-22)*(1-INP-25))*INP-23*INP-24` | fraction | 0.998001 | 0.998001 | 0.998001 | 99.80%; redundancy alone does not close the gap |
| EST-28 | Per-component availability needed for the target | `INP-26**(1/INP-28)` | fraction | 0.9998 | 0.9998 | 0.9998 | Five equal components must each reach about 99.98% |
| EST-29 | Modelled downtime of the serial path | `(1-EST-25)*INP-27` | minutes/30 days | 129.4 | 129.4 | 129.4 | About three times the allowance in EST-26 |

**Modelling notes.** The physical multiplier (EST-08) is applied uniformly to every tier and layer, which is a simplification: a real archive tier may hold fewer layers or copies. EST-20 to EST-22 are monthly run-rates at the end of Year 7; they exclude retrieval fees, lifecycle-management effort and the one-off cost of moving data.

**Worked checks (reviewer recomputation).** (1) EST-01: 2,000,000 × 500 = 1,000,000,000
bytes = 1.0 GB/day. (2) EST-12: 2,000,000 ÷ 86,400 × 4 = 92.59 events/s; EST-13 =
92.59 × 1.5 = 138.9 events/s. (3) EST-25: 0.9995⁴ × 0.999 = 0.997003.

#### 6.5.3 Sensitivity ranking (tornado)

Each input is moved alone from its low to its high case while all others stay at the
expected case. `Swing` is the absolute difference in the output. Rank 1 is the largest
swing; ties share a rank. Inputs with zero swing are omitted (INP-01, INP-09, INP-13,
INP-14 and others for EST-09; all others for EST-13).

| ID | Output | Input | Output at low | Output at high | Swing | Rank |
| --- | --- | --- | --- | --- | --- | --- |
| TN-01 | EST-09 | INP-10 | 27.25 | 54.5 | 27.25 | 1 |
| TN-02 | EST-09 | INP-08 | 30.07 | 55.68 | 25.6 | 2 |
| TN-03 | EST-09 | INP-04 | 31.55 | 53.32 | 21.77 | 3 |
| TN-04 | EST-09 | INP-11 | 40.88 | 61.32 | 20.44 | 4 |
| TN-05 | EST-09 | INP-05 | 36.44 | 49.77 | 13.33 | 5 |
| TN-06 | EST-09 | INP-12 | 39.02 | 44.59 | 5.574 | 6 |
| TN-07 | EST-09 | INP-03 | 39.1 | 43.54 | 4.443 | 7 |
| TN-08 | EST-09 | INP-02 | 39.1 | 43.54 | 4.443 | 7 |
| TN-09 | EST-09 | INP-06 | 40.61 | 41.32 | 0.7109 | 9 |
| TN-10 | EST-09 | INP-07 | 40.7 | 41.23 | 0.5332 | 10 |
| TN-11 | EST-13 | INP-09 | 104.2 | 347.2 | 243.1 | 1 |
| TN-12 | EST-13 | INP-15 | 115.7 | 185.2 | 69.44 | 2 |
| TN-13 | EST-13 | INP-02 | 111.1 | 180.6 | 69.44 | 2 |

**Validation priority.** For storage, the compression ratio (INP-10) and growth
(INP-08) matter most, and the third, other-event volume (INP-04), is a `guessed` input
and should be sampled first. For throughput, the peak factor (INP-09) dominates:
derive it from time-bucketed history before relying on EST-13.

#### 6.5.4 Service-target specification (D7)

| ID | Requirement | Consumer | SLI definition | Target | Window | Scope and boundary | Method | Exclusions | Acceptance test | Evidence | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TGT-01 | REQ-06 | Fraud analyst | Elapsed time from authorisation timestamp to first visibility of the event in the case tool | p95 <= 30 s | Rolling 30 days, 08:00–20:00 local time | Eligible card authorisations; boundary starts at authorisation, so source wait is included | Event-ID correlation of source and consumer timestamps with synchronised clocks | Test and replayed events; agreed maintenance | Representative peak workload with p95 computed over a sufficient sample | Illustrative assumption | Low |
| TGT-02 | REQ-07 | Fraud analyst | Same as TGT-01 | p95 <= 300 s | Rolling 30 days, outside 08:00–20:00 | Eligible card authorisations | Same as TGT-01 | Same as TGT-01 | Same as TGT-01 | Illustrative assumption | Low |
| TGT-03 | REQ-08 | Fraud operations | Share of 1-minute intervals with no undelivered backlog older than 5 minutes | >= 99.9% of intervals (43.2 minutes allowance per 30 days) | Rolling 30 days | Whole delivery path from capture to case tool | Interval monitoring of queue age | Agreed maintenance, measured and applied consistently | Operate in test for 30 days with fault injection | Illustrative assumption | Low |
| TGT-04 | REQ-09 | Fraud operations | Share of eligible source authorisations present in the case tool within 24 hours | >= 99.99% | Daily, reported monthly | Eligible authorisations; missing and duplicates counted separately | Source-to-target ID reconciliation | Declined test traffic | Reconciliation on one full day of production-like data | Illustrative assumption | Low |
| TGT-05 | REQ-10 | Engineering | Sustained event rate with no backlog growth | >= 138.9 events/s (EST-13) | 30-minute test, repeated | Realistic payload sizes and downstream writes | Load test | None | Load test passes at the target rate | Illustrative assumption | Low |
| TGT-06 | REQ-15 | Compliance | Time from retrieval request to record availability | 100% of requests <= 24 h | Per request | Any in-scope record younger than 7 years | Retrieval drill across record ages | None | Drill of 20 requests | Illustrative assumption | Low |
| TGT-07 | REQ-16 | Investigator | Query response time on the agreed query set | p95 <= 5 s | Rolling 30 days | Data aged under 24 months | Query benchmark | Ad hoc queries outside the set | Benchmark on the agreed set | Illustrative assumption | Low |
| TGT-08 | REQ-01 | Risk, finance, marketing, compliance | Share of business days on which the daily count publishes on time | >= 99% of business days by 07:00 local time | Rolling 30 business days | All four consumers; starts after the core batch ends at 02:30 | Publication timestamp log | Declared bank holidays | Dry run over 20 business days | Illustrative assumption | Low |
| TGT-09 | REQ-04 | Compliance | Time to produce a lineage report for a sampled value | <= 4 working hours | Per request | Published customer attribute values | Timed sample of lineage requests | None | 25 sampled requests | Illustrative assumption | Low |

#### 6.5.5 Timing budgets and availability gap

**Timing budget (D7).** Each option's stage budget is a worst-case sequential model, not a measured p95
(percentiles of stages do not add). For batch options the first stage is the maximum
wait for the next file, which is conservative; using 0.95 × the interval would still
leave OPT-02 at 75 s (57 + 18), above 30 s. Margin = 30 s − total.

| ID | Option | Stage | Seconds | Basis | Evidence |
| --- | --- | --- | --- | --- | --- |
| TB-01 | OPT-01 | source availability | 900 | Maximum wait for the next 15-minute file (FACT-04) | Illustrative assumption |
| TB-02 | OPT-01 | transport | 3 | Planning budget | Illustrative assumption |
| TB-03 | OPT-01 | queue wait | 0 | Files are processed on arrival | Illustrative assumption |
| TB-04 | OPT-01 | processing | 8 | Planning budget | Illustrative assumption |
| TB-05 | OPT-01 | target commit | 4 | Planning budget | Illustrative assumption |
| TB-06 | OPT-01 | publish | 3 | Planning budget | Illustrative assumption |
| TB-07 | OPT-02 | source availability | 60 | Maximum wait for the next one-minute batch | Illustrative assumption |
| TB-08 | OPT-02 | transport | 3 | Planning budget | Illustrative assumption |
| TB-09 | OPT-02 | queue wait | 0 | Batches are processed on arrival | Illustrative assumption |
| TB-10 | OPT-02 | processing | 8 | Planning budget | Illustrative assumption |
| TB-11 | OPT-02 | target commit | 4 | Planning budget | Illustrative assumption |
| TB-12 | OPT-02 | publish | 3 | Planning budget | Illustrative assumption |
| TB-13 | OPT-03 | source availability | 5 | Event published at authorisation | Illustrative assumption |
| TB-14 | OPT-03 | transport | 3 | Planning budget | Illustrative assumption |
| TB-15 | OPT-03 | queue wait | 4 | Planning budget | Illustrative assumption |
| TB-16 | OPT-03 | processing | 8 | Planning budget | Illustrative assumption |
| TB-17 | OPT-03 | target commit | 4 | Planning budget | Illustrative assumption |
| TB-18 | OPT-03 | publish | 3 | Planning budget | Illustrative assumption |
| TB-19 | OPT-04 | source availability | 6 | Capture lag from the data store's change log | Illustrative assumption |
| TB-20 | OPT-04 | transport | 3 | Planning budget | Illustrative assumption |
| TB-21 | OPT-04 | queue wait | 4 | Planning budget | Illustrative assumption |
| TB-22 | OPT-04 | processing | 8 | Planning budget | Illustrative assumption |
| TB-23 | OPT-04 | target commit | 4 | Planning budget | Illustrative assumption |
| TB-24 | OPT-04 | publish | 3 | Planning budget | Illustrative assumption |

Totals: OPT-01 918 s; OPT-02 78 s; OPT-03 27 s (margin 3 s); OPT-04 28 s (margin 2 s).

**Availability gap.** The serial model (EST-25) gives 99.70%, against a 99.9% target
(EST-26 allows 43.2 minutes per 30 days; the model implies about 129.4 minutes,
EST-29). Adding a second processing instance only reaches 99.80% (EST-27). To hit the
target with five serial components, each needs about 99.98% (EST-28). TGT-03 is
therefore a **provisional hypothesis** with a validation plan (RSK-02), not a
demonstrated service level.

### 6.6 D8 — Constraints, assumptions, dependencies, risks and unknowns (Step 8)

**Preference**

| ID | Preference | Sponsor | Fixed or negotiable | Treatment | Evidence |
| --- | --- | --- | --- | --- | --- |
| PREF-01 | Reuse the event platform the lake team trialled (INT-08) | STK-01 | Negotiable | Assessed as operability and dependency evidence for OPT-03 and OPT-04; never a gate (CF-02) | Stakeholder statement |

**Constraints**

| ID | Constraint | Authority | Rationale | Fixed or negotiable | Challenge route | Linked | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CON-01 | Personal data remains in the permitted jurisdiction, including replicas and backups | STK-12 | Data protection obligation (INT-07, INT-13) | Fixed | Only through the data protection function | REQ-11; GT-02; GT-06 | Active | Stakeholder statement |
| CON-02 | Transaction records are retained for seven years | STK-06 | Records-retention obligation (INT-12) | Fixed | Compliance policy change | REQ-14; GT-07; INP-13 | Active | Stakeholder statement |
| CON-03 | The core banking batch window ends at 02:30 | STK-09 | Operational dependency (INT-10, FACT-02) | Fixed | Core engineering change | REQ-24; TGT-08 | Active | Stakeholder statement |
| CON-04 | A regulatory milestone date applies; the date is not supplied | STK-06 | Regulator request (FACT-05) | Fixed | Regulator correspondence only | REQ-18; ASM-01; UNK-01; GT-05 | Active | Stakeholder statement |
| CON-05 | The existing identity provider must be used | STK-07 | Security architecture (INT-07) | Fixed | Security architecture change | REQ-12; GT-02; GT-06 | Active | Stakeholder statement |
| CON-06 | A programme budget ceiling is set by the sponsor; the value is not supplied | STK-01 | Funding decision | Fixed | Sponsor decision | REQ-17; UNK-03 | Active | Stakeholder statement |

**Assumptions**

| ID | Assumption | Owner | Confidence | Impact if wrong | Validation method | Validation due (week) | Fallback | Linked | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ASM-01 | The regulatory milestone is 9 months from programme start | STK-06 | Low | High | Written confirmation from Compliance | 2 | Re-run GT-05 with the confirmed date (SEN-12) | UNK-01; DEC-02 | Open | Illustrative assumption |
| ASM-02 | The card platform's data store change log can be read without changing the platform application | STK-08 | Low | High | Technical spike with the card platform owner | 10 | Fall back to OPT-03 if DEP-01 is committed | DEC-01; DEP-02 | Open | Illustrative assumption |
| ASM-03 | The peak-to-average factor is 4 and the card-transaction average is 2,000,000 per day | STK-08 | Low | High | Time-bucketed history of 90 days | 3 | Recompute EST-12, EST-13 and re-test TGT-05 | INP-02; INP-09; EST-13 | Open | Illustrative assumption |
| ASM-04 | A 24-month interactive look-back covers at least 90% of investigator queries | STK-05 | Low | Medium | Query-log sample of 90 days | 4 | Widen the interactive window and re-run DEC-03 gates | REQ-16; DEC-03 | Open | Illustrative assumption |
| ASM-05 | The average card-transaction record is 500 bytes serialised | STK-08 | Medium | Low | Sample of 10,000 records | 3 | Update INP-03 and recompute | INP-03 | Open | Illustrative assumption |
| ASM-06 | The CRM holds a current identity and contact record for at least 95% of retail customers | STK-02 | Low | High | Match test against the core customer list | 6 | Re-rate OPT-08 coverage (SEN-10) | DEC-02; REQ-21 | Open | Illustrative assumption |
| ASM-07 | Annual volume growth is 15% | STK-08 | Low | High | Growth from 24 months of history | 4 | Re-run DEC-03 scoring (SEN-16, SEN-17) | INP-08; DEC-03 | Open | Illustrative assumption |
| ASM-08 | Archive-tier retrieval completes within 12 hours | STK-08 | Low | High | Retrieval test with the storage owner | 10 | Keep OPT-09 if retrieval exceeds 24 hours (SEN-19) | REQ-15; DEC-03 | Open | Illustrative assumption |

**Dependencies**

| ID | Dependency | Provider | Consumer | Owner | Needed by (week) | Failure consequence | Contingency | Linked | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEP-01 | The card platform publishes authorisation events at authorisation time | STK-13 | DEC-01 (OPT-03) | STK-13 | 10 | OPT-03 cannot start; delivery slips | Use OPT-04 if DEP-02 is met | OPT-03; RSK-01 | Open | Illustrative assumption |
| DEP-02 | Security approves read access to the card platform's change log | STK-07 | DEC-01 (OPT-04) | STK-07 | 10 | OPT-04 is refused | Use OPT-03 if DEP-01 is committed | OPT-04; ASM-02; GT-02 | Open | Illustrative assumption |
| DEP-03 | Compliance defines the in-scope attribute list and the lineage evidence format | STK-06 | DEC-02 | STK-06 | 3 | REQ-03 and REQ-04 stay untestable | Proceed on a provisional list | REQ-03; REQ-04; REQ-22 | Open | Illustrative assumption |
| DEP-04 | Environments are provisioned in the permitted jurisdiction | STK-08 | DEC-01, DEC-02, DEC-03 | STK-08 | 10 | Non-production tests cannot run | Provision a restricted test enclave | CON-01; REQ-11 | Open | Illustrative assumption |
| DEP-05 | The case tool exposes an ingestion interface that accepts the event rate | STK-13 | DEC-01 | STK-13 | 10 | No option can deliver to the tool | Escalate to the case-tool owner | REQ-05; TGT-05 | Open | Illustrative assumption |

**Risks** (cause–event–effect; horizon: until the linked ADR is accepted)

| ID | Risk | Owner | Probability | Impact | Exposure | Band | Horizon | Response | Trigger | Escalation | Linked | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RSK-01 | Because log-level access to the card platform's data store is not yet approved or tested (DEP-02, ASM-02), the selected capture approach may be refused or unsupported, delaying the fraud release | STK-08 | 3 | 4 | 12 | High | Until ADR-01 is accepted | Run the spike and submit the security review early; keep OPT-03 as fallback | Spike fails or security declines by week 10 | STK-01 | DEC-01; DEP-02; DEP-01 | Open | Illustrative assumption |
| RSK-02 | Because modelled serial availability (EST-25) is below the target (TGT-03), the path may exceed its monthly allowance, leaving fraud signals undelivered | STK-05 | 4 | 3 | 12 | High | Until ADR-01 is accepted | Treat TGT-03 as provisional; validate component availability; agree a fall-back procedure | Measured availability under 99.9% in test | STK-01 | TGT-03; EST-25; EST-26 | Open | Illustrative assumption |
| RSK-03 | Because definition owners hold conflicting positions (CF-01, UNK-04), the registry approach may be rejected, causing rework | STK-01 | 3 | 4 | 12 | High | Until ADR-02 is accepted | Definition workshop; record each definition with its owner before design | A definition owner withholds sign-off at week 6 | STK-01 | CF-01; UNK-04; DEC-02 | Open | Illustrative assumption |
| RSK-04 | Because the regulatory milestone date is unconfirmed (UNK-01), the 9-month planning assumption may be wrong, so the selected approach may be late or over-built | STK-06 | 3 | 5 | 15 | Very high | Until ADR-02 is accepted | Obtain written confirmation of date and evidence format | No written confirmation by the end of week 2 | STK-01 | ASM-01; UNK-01; CON-04 | Open | Illustrative assumption |
| RSK-05 | Because CRM coverage is assumed, not measured (ASM-06), identity matching may be less complete than assumed, producing missed or false links | STK-02 | 3 | 4 | 12 | High | Until ADR-02 is accepted | Match test on a sample; re-rate options with results | Match rate under 95% | STK-01 | ASM-06; DEC-02; REQ-21 | Open | Illustrative assumption |
| RSK-06 | Because growth is unmeasured (ASM-07), storage cost may exceed the forecast and the preferred tiering may no longer rank first | STK-04 | 3 | 3 | 9 | Moderate | Until ADR-03 is accepted | Measure growth; re-run SEN-16 and SEN-17 | Measured growth above 20% | STK-01 | ASM-07; INP-08; DEC-03 | Open | Illustrative assumption |
| RSK-07 | Because backups or vendor-support access might create copies outside the jurisdiction, residency could be breached | STK-12 | 2 | 5 | 10 | High | Until all ADRs are accepted | Inventory every copy path; confirm support access terms | Any copy path outside the jurisdiction | STK-01 | CON-01; REQ-11 | Open | Illustrative assumption |
| RSK-08 | Because knowledge of the core extract rests with one engineer, absence could delay extraction work | STK-09 | 3 | 3 | 9 | Moderate | Until delivery planning starts | Document the extract; name a deputy | The engineer is unavailable for over two weeks | STK-08 | CON-03; REQ-24 | Open | Illustrative assumption |
| RSK-09 | Because change capture or extraction might load the core platform near the batch window, the core batch could finish after 02:30 | STK-09 | 2 | 4 | 8 | Moderate | During the 30-day trial | Schedule extraction after the batch; measure load in test | Batch completion later than 02:30 in test | STK-08 | CON-03; REQ-24 | Open | Illustrative assumption |

**Unknowns**

| ID | Open question | Decisions affected | Blocks | Owner | Evidence needed | Due week | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UNK-01 | What is the exact regulatory milestone date and evidence format? | DEC-02 | Blocks decision | STK-06 | Regulator correspondence | 2 | Open |
| UNK-02 | What log retention period does Compliance require? | DEC-01; DEC-02 | Manageable gap | STK-06 | Compliance policy | 6 | Open |
| UNK-03 | What is the sponsor's budget ceiling? | DEC-01; DEC-02; DEC-03 | Blocks decision | STK-01 | Sponsor confirmation | 6 | Open |
| UNK-04 | Which customer definitions will be approved, and who owns each? | DEC-02 | Manageable gap | STK-01 | Definition workshop output | 6 | Open |
| UNK-05 | Which fields does the case tool need to open a case? | DEC-01 | Manageable gap | STK-05 | Approved field list | 3 | Open |

### 6.7 D9 — Decision criteria and prioritisation method (Step 9)

**Rule.** Gates are evaluated first. An option is **eligible** if no gate result is
`Fail`; `Pending` gates become ADR conditions. Only eligible options are scored.
Weights and bands are frozen in **week 4**; scoring happens in **week 5**.

**Hard gates**

| ID | Decision | Gate statement | Source | Operator | Threshold | Unit | Value source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GT-01 | DEC-01 | Stage-budget total meets the freshness target | REQ-06; TGT-01 | <= | 30 | seconds | TB |
| GT-02 | DEC-01 | Meets residency, identity and access-control constraints | CON-01; CON-05 | n/a | n/a | n/a | n/a |
| GT-03 | DEC-01 | Source interface is feasible within the programme | ASM-02; DEP-01; DEP-02 | n/a | n/a | n/a | n/a |
| GT-04 | DEC-02 | Can produce one governed, reproducible customer count | REQ-01; BO-01 | n/a | n/a | n/a | n/a |
| GT-05 | DEC-02 | Delivered before the regulatory milestone | REQ-18; CON-04; ASM-01 | <= | 9 | months | DL |
| GT-06 | DEC-02 | Meets residency, identity and access-control constraints | CON-01; CON-05 | n/a | n/a | n/a | n/a |
| GT-07 | DEC-03 | Retains transaction detail for the full retention period | REQ-14; CON-02 | >= | 7 | years | stated |
| GT-08 | DEC-03 | Worst-case retrieval time within the retrieval target | REQ-15; TGT-06 | <= | 24 | hours | stated |
| GT-09 | DEC-03 | Data aged under 24 months stays interactive | REQ-16; TGT-07 | >= | 24 | months | stated |

**Scored criteria** (weights sum to 1 per decision)

| ID | Decision | Criterion | Weight | Source | Rating basis | Frozen in week | Weight rationale |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CRIT-01 | DEC-01 | Freshness headroom (seconds of margin under the target) | 0.25 | REQ-06; TGT-01 | Numeric bands AN | 4 | The gate guarantees the minimum; headroom is valuable but secondary to cost and delivery |
| CRIT-02 | DEC-01 | Three-year total cost of ownership | 0.25 | REQ-17; CON-06 | Numeric bands AN | 4 | Budget is a binding concern for the sponsor (CON-06) and the options differ widely |
| CRIT-03 | DEC-01 | Delivery time to first production release | 0.15 | BO-02; REQ-18 | Numeric bands AN | 4 | A faster release shortens the period of late fraud signals |
| CRIT-04 | DEC-01 | Operability and supportability | 0.20 | REQ-19; STK-09 | Judgement anchors JA | 4 | Fraud operations must run the path continuously; support burden is a lasting cost |
| CRIT-05 | DEC-01 | Exposure to external dependencies | 0.15 | DEP-01; DEP-02; RSK-01 | Judgement anchors JA | 4 | A dependency on an uncommitted external change is the largest delivery risk (RSK-01) |
| CRIT-06 | DEC-02 | Delivery time | 0.20 | REQ-18; CON-04 | Numeric bands AN | 4 | The milestone is a gate; further speed lowers regulatory risk but has diminishing value |
| CRIT-07 | DEC-02 | Three-year total cost of ownership | 0.20 | REQ-17; CON-06 | Numeric bands AN | 4 | Budget matters, but the options differ less than in DEC-01 |
| CRIT-08 | DEC-02 | Expected identity-linkage coverage | 0.25 | REQ-01; REQ-21; ASM-06 | Judgement anchors JA | 4 | A weak linkage defeats the objective of one governed count (BO-01) |
| CRIT-09 | DEC-02 | Ownership and operating clarity | 0.20 | REQ-03; REQ-22 | Judgement anchors JA | 4 | Accountability is the regulator's concern (BO-03) |
| CRIT-10 | DEC-02 | Reversibility and lock-in | 0.15 | BO-01; BO-03 | Judgement anchors JA | 4 | The least certain inputs argue for an option that is easy to unwind |
| CRIT-11 | DEC-03 | Storage cost reduction against the baseline | 0.40 | REQ-17; CON-06 | Numeric bands AN | 4 | Cost is the main reason to tier; all eligible options already meet retention and retrieval gates |
| CRIT-12 | DEC-03 | Operational simplicity | 0.30 | REQ-19 | Judgement anchors JA | 4 | More tiers mean more rules to run and monitor |
| CRIT-13 | DEC-03 | Retrieval-cost and lock-in exposure | 0.30 | REQ-15; BO-04 | Judgement anchors JA | 4 | Retrieval fees and delay are the main downside of colder tiers |

**Numeric rating bands** (inclusive bounds; inputs rounded half-up to a whole number first)

| ID | Criterion | Rating | From | To |
| --- | --- | --- | --- | --- |
| AN-01 | CRIT-01 | 5 | 10 | inf |
| AN-02 | CRIT-01 | 4 | 6 | 9 |
| AN-03 | CRIT-01 | 3 | 3 | 5 |
| AN-04 | CRIT-01 | 2 | 1 | 2 |
| AN-05 | CRIT-01 | 1 | 0 | 0 |
| AN-06 | CRIT-02 | 5 | 0 | 250 |
| AN-07 | CRIT-02 | 4 | 251 | 325 |
| AN-08 | CRIT-02 | 3 | 326 | 400 |
| AN-09 | CRIT-02 | 2 | 401 | 500 |
| AN-10 | CRIT-02 | 1 | 501 | inf |
| AN-11 | CRIT-03 | 5 | 0 | 4 |
| AN-12 | CRIT-03 | 4 | 5 | 6 |
| AN-13 | CRIT-03 | 3 | 7 | 8 |
| AN-14 | CRIT-03 | 2 | 9 | 10 |
| AN-15 | CRIT-03 | 1 | 11 | inf |
| AN-16 | CRIT-06 | 5 | 0 | 3 |
| AN-17 | CRIT-06 | 4 | 4 | 6 |
| AN-18 | CRIT-06 | 3 | 7 | 8 |
| AN-19 | CRIT-06 | 2 | 9 | 10 |
| AN-20 | CRIT-06 | 1 | 11 | inf |
| AN-21 | CRIT-07 | 5 | 0 | 300 |
| AN-22 | CRIT-07 | 4 | 301 | 400 |
| AN-23 | CRIT-07 | 3 | 401 | 550 |
| AN-24 | CRIT-07 | 2 | 551 | 750 |
| AN-25 | CRIT-07 | 1 | 751 | inf |
| AN-26 | CRIT-11 | 5 | 60 | inf |
| AN-27 | CRIT-11 | 4 | 50 | 59 |
| AN-28 | CRIT-11 | 3 | 40 | 49 |
| AN-29 | CRIT-11 | 2 | 25 | 39 |
| AN-30 | CRIT-11 | 1 | 0 | 24 |

Units: CRIT-01 seconds; CRIT-02 and CRIT-07 thousands of currency units; CRIT-03 and
CRIT-06 months; CRIT-11 percent.

**Judgement anchors** (ordinal; ratings 2 and 4 fall between the anchors)

| ID | Criterion | Anchor for 1 | Anchor for 3 | Anchor for 5 |
| --- | --- | --- | --- | --- |
| JA-01 | CRIT-04 | Unsupported or unacceptable burden | Moderate new work; runbooks and training required | Established support model, low incremental burden |
| JA-02 | CRIT-05 | External dependency with no owner or commitment | Dependency inside the bank's control with approval pending | No external dependency |
| JA-03 | CRIT-08 | Large known gaps in coverage | Most customers covered; gaps for some segments | Near-complete coverage across all source systems |
| JA-04 | CRIT-09 | Owners contested or unclear for most attributes | Owners clear for most attributes; some contested | Attribute-level owners explicit and accepted |
| JA-05 | CRIT-10 | Hard to unwind; sources re-pointed | Reversible with moderate rework | Easily retired; sources unchanged |
| JA-06 | CRIT-12 | Many moving parts and manual steps | Several lifecycle rules to run and monitor | A single tier and one set of rules |
| JA-07 | CRIT-13 | Large or unknown retrieval fees and long lock-in | Some retrieval fees and delay; manageable lock-in | No retrieval fees; no lifecycle lock-in |

### 6.8 D10 — Architecture alternatives and comparison (Steps 10 and 11)

**Alternatives** (option categories only)

| ID | Decision | Option | Option description | Role |
| --- | --- | --- | --- | --- |
| OPT-01 | DEC-01 | Retain current batch | Keep the 15-minute batch file with reliability improvements | Baseline |
| OPT-02 | DEC-01 | Managed short-interval batch | Move the source to one-minute batches ingested by a managed service | Alternative |
| OPT-03 | DEC-01 | Source-published events | The card platform publishes authorisation events to a durable event channel | Alternative |
| OPT-04 | DEC-01 | Log-based change capture | Capture changes from the card platform's data store log into a durable event channel without changing the application | Alternative |
| OPT-05 | DEC-02 | Document definitions only | Keep source-defined customer data; document definitions and mappings | Baseline |
| OPT-06 | DEC-02 | Identity registry | A cross-reference index links source records to one enterprise identifier; sources stay authoritative per attribute | Alternative |
| OPT-07 | DEC-02 | Central customer master | A new authoritative customer store that all sources synchronise with | Alternative |
| OPT-08 | DEC-02 | Designate the CRM as system of record | The CRM becomes authoritative; other systems synchronise from it | Alternative |
| OPT-09 | DEC-03 | Single tier | Keep all seven years in the interactive tier | Baseline |
| OPT-10 | DEC-03 | Two tiers | Latest two years interactive; Years 1 to 5 in archive | Alternative |
| OPT-11 | DEC-03 | Three tiers | Latest year interactive; previous year infrequent-access; Years 1 to 5 in archive | Alternative |
| OPT-12 | DEC-03 | Shorter detail retention | Keep detail for five years and summaries after that | Alternative |

**Cost components** (thousands of illustrative currency units; exit cost at the end of the three-year horizon)

| ID | Option | Build and migration | Three-year run and support | Exit | Total | Evidence | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TCO-01 | OPT-01 | 80 | 150 | 20 | 250 | Illustrative assumption | Planning estimate, not a quote |
| TCO-02 | OPT-02 | 120 | 180 | 25 | 325 | Illustrative assumption | Planning estimate, not a quote |
| TCO-03 | OPT-03 | 180 | 240 | 30 | 450 | Illustrative assumption | Planning estimate, not a quote |
| TCO-04 | OPT-04 | 150 | 210 | 25 | 385 | Illustrative assumption | Planning estimate, not a quote |
| TCO-05 | OPT-05 | 40 | 40 | 10 | 90 | Illustrative assumption | Planning estimate, not a quote |
| TCO-06 | OPT-06 | 200 | 260 | 40 | 500 | Illustrative assumption | Planning estimate, not a quote |
| TCO-07 | OPT-07 | 420 | 420 | 80 | 920 | Illustrative assumption | Planning estimate, not a quote |
| TCO-08 | OPT-08 | 140 | 190 | 30 | 360 | Illustrative assumption | Planning estimate, not a quote |

**Delivery estimates** (months to first production release)

| ID | Option | Delivery months | Evidence | Basis |
| --- | --- | --- | --- | --- |
| DL-01 | OPT-01 | 4 | Illustrative assumption | Team estimate, unvalidated |
| DL-02 | OPT-02 | 6 | Illustrative assumption | Team estimate, unvalidated |
| DL-03 | OPT-03 | 9 | Illustrative assumption | Depends on DEP-01, not committed |
| DL-04 | OPT-04 | 7 | Illustrative assumption | Depends on DEP-02 approval |
| DL-05 | OPT-05 | 3 | Illustrative assumption | Team estimate, unvalidated |
| DL-06 | OPT-06 | 8 | Illustrative assumption | One month of margin against ASM-01 |
| DL-07 | OPT-07 | 14 | Illustrative assumption | Large migration |
| DL-08 | OPT-08 | 6 | Illustrative assumption | Depends on ASM-06 |

**Gate results.** `Value` is the number the gate tests; `n/a` marks a qualitative gate.
`Pending` means the gate is not yet proven and becomes an ADR condition. Numeric results are
recomputed by the checker.

| ID | Gate | Option | Value | Result | Note |
| --- | --- | --- | --- | --- | --- |
| GR-01 | GT-01 | OPT-01 | 918 | Fail | Total of TB-01 to TB-06 |
| GR-02 | GT-01 | OPT-02 | 78 | Fail | Total of TB-07 to TB-12 |
| GR-03 | GT-01 | OPT-03 | 27 | Pass | Total of TB-13 to TB-18; to be confirmed by test |
| GR-04 | GT-01 | OPT-04 | 28 | Pass | Total of TB-19 to TB-24; to be confirmed by test |
| GR-05 | GT-02 | OPT-01 | n/a | Pending | Security review not yet performed |
| GR-06 | GT-02 | OPT-02 | n/a | Pending | Security review not yet performed |
| GR-07 | GT-02 | OPT-03 | n/a | Pending | Security review not yet performed |
| GR-08 | GT-02 | OPT-04 | n/a | Pending | Security review not yet performed; log access is the main concern (DEP-02) |
| GR-09 | GT-03 | OPT-01 | n/a | Pass | Interface exists today (FACT-04) |
| GR-10 | GT-03 | OPT-02 | n/a | Pending | Source must emit one-minute batches |
| GR-11 | GT-03 | OPT-03 | n/a | Pending | DEP-01 uncommitted |
| GR-12 | GT-03 | OPT-04 | n/a | Pending | ASM-02 and DEP-02 unvalidated |
| GR-13 | GT-04 | OPT-05 | n/a | Fail | Definitions are documented but records are not linked, so no reconciled count can be produced |
| GR-14 | GT-04 | OPT-06 | n/a | Pending | Proof by pilot on a sample |
| GR-15 | GT-04 | OPT-07 | n/a | Pending | Proof by pilot on a sample |
| GR-16 | GT-04 | OPT-08 | n/a | Pending | Depends on CRM coverage (ASM-06) |
| GR-17 | GT-05 | OPT-05 | 3 | Pass | DL-05 |
| GR-18 | GT-05 | OPT-06 | 8 | Pass | DL-06; one month of margin |
| GR-19 | GT-05 | OPT-07 | 14 | Fail | DL-07 exceeds the milestone assumption |
| GR-20 | GT-05 | OPT-08 | 6 | Pass | DL-08 |
| GR-21 | GT-06 | OPT-05 | n/a | Pending | Security and data protection review not yet performed |
| GR-22 | GT-06 | OPT-06 | n/a | Pending | Security and data protection review not yet performed |
| GR-23 | GT-06 | OPT-07 | n/a | Pending | Security and data protection review not yet performed |
| GR-24 | GT-06 | OPT-08 | n/a | Pending | Security and data protection review not yet performed |
| GR-25 | GT-07 | OPT-09 | 7 | Pass | Seven years kept (CON-02) |
| GR-26 | GT-07 | OPT-10 | 7 | Pass | Seven years kept |
| GR-27 | GT-07 | OPT-11 | 7 | Pass | Seven years kept |
| GR-28 | GT-07 | OPT-12 | 5 | Fail | Detail kept for five years only; violates CON-02 |
| GR-29 | GT-08 | OPT-09 | 0 | Pass | Interactive tier |
| GR-30 | GT-08 | OPT-10 | 12 | Pass | Archive retrieval assumed 12 hours (ASM-08) |
| GR-31 | GT-08 | OPT-11 | 12 | Pass | Archive retrieval assumed 12 hours (ASM-08) |
| GR-32 | GT-08 | OPT-12 | 12 | Pass | Archive retrieval assumed 12 hours (ASM-08) |
| GR-33 | GT-09 | OPT-09 | 84 | Pass | All seven years interactive |
| GR-34 | GT-09 | OPT-10 | 24 | Pass | Latest two years interactive |
| GR-35 | GT-09 | OPT-11 | 24 | Pass | Latest two years interactive |
| GR-36 | GT-09 | OPT-12 | 24 | Pass | Latest two years interactive |

**Option inputs and ratings (eligible options only).** The table below is the comparison matrix in long form: one row per option and criterion, with the input, the rating and the evidence. Numeric inputs come from the
`Value source`: `TBM` is the gate threshold minus the stage-budget total; `TCO` and `DL` come
from the tables above; `EST-nn` is the computed estimate at the expected case; `stated` is
the value given here; `judgement` is an ordinal rating with a written basis.

| ID | Decision | Option | Criterion | Input value | Unit | Value source | Rating | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OI-01 | DEC-01 | OPT-03 | CRIT-01 | 3 | seconds | TBM | 3 | Margin 3 s (30 − 27) |
| OI-02 | DEC-01 | OPT-03 | CRIT-02 | 450 | k currency | TCO | 2 | TCO-03 |
| OI-03 | DEC-01 | OPT-03 | CRIT-03 | 9 | months | DL | 2 | DL-03 |
| OI-04 | DEC-01 | OPT-03 | CRIT-04 | judgement | n/a | judgement | 2 | The card platform team would also run the publisher, replay and duplicate handling; recovery not yet proven |
| OI-05 | DEC-01 | OPT-03 | CRIT-05 | judgement | n/a | judgement | 2 | Depends on another team's uncommitted change (DEP-01) |
| OI-06 | DEC-01 | OPT-04 | CRIT-01 | 2 | seconds | TBM | 2 | Margin 2 s (30 − 28) |
| OI-07 | DEC-01 | OPT-04 | CRIT-02 | 385 | k currency | TCO | 3 | TCO-04 |
| OI-08 | DEC-01 | OPT-04 | CRIT-03 | 7 | months | DL | 3 | DL-04 |
| OI-09 | DEC-01 | OPT-04 | CRIT-04 | judgement | n/a | judgement | 3 | Moderate new work: capture-lag monitoring, schema-change handling, log retention |
| OI-10 | DEC-01 | OPT-04 | CRIT-05 | judgement | n/a | judgement | 3 | Approval inside the bank pending (DEP-02) |
| OI-11 | DEC-02 | OPT-06 | CRIT-06 | 8 | months | DL | 3 | DL-06 |
| OI-12 | DEC-02 | OPT-06 | CRIT-07 | 500 | k currency | TCO | 3 | TCO-06 |
| OI-13 | DEC-02 | OPT-06 | CRIT-08 | judgement | n/a | judgement | 4 | Links records from all four source systems including business customers; match rate unproven |
| OI-14 | DEC-02 | OPT-06 | CRIT-09 | judgement | n/a | judgement | 4 | Attribute-level owners are explicit by design |
| OI-15 | DEC-02 | OPT-06 | CRIT-10 | judgement | n/a | judgement | 4 | The index can be retired; sources are unchanged |
| OI-16 | DEC-02 | OPT-08 | CRIT-06 | 6 | months | DL | 4 | DL-08 |
| OI-17 | DEC-02 | OPT-08 | CRIT-07 | 360 | k currency | TCO | 4 | TCO-08 |
| OI-18 | DEC-02 | OPT-08 | CRIT-08 | judgement | n/a | judgement | 3 | CRM assumed to cover most retail customers; business and card-only customers uncertain (ASM-06) |
| OI-19 | DEC-02 | OPT-08 | CRIT-09 | judgement | n/a | judgement | 3 | The CRM owner would become accountable for attributes created elsewhere; contested |
| OI-20 | DEC-02 | OPT-08 | CRIT-10 | judgement | n/a | judgement | 2 | Sources are re-pointed to synchronise from the CRM; hard to unwind |
| OI-21 | DEC-03 | OPT-09 | CRIT-11 | 0 | percent | stated | 1 | Baseline: no reduction by definition |
| OI-22 | DEC-03 | OPT-09 | CRIT-12 | judgement | n/a | judgement | 5 | One tier and one rule set |
| OI-23 | DEC-03 | OPT-09 | CRIT-13 | judgement | n/a | judgement | 5 | No retrieval fees; nothing to unwind |
| OI-24 | DEC-03 | OPT-10 | CRIT-11 | 50.33 | percent | EST-23 | 4 | EST-23 at the expected case rounds to 50 |
| OI-25 | DEC-03 | OPT-10 | CRIT-12 | judgement | n/a | judgement | 4 | Two tiers and one transition rule |
| OI-26 | DEC-03 | OPT-10 | CRIT-13 | judgement | n/a | judgement | 3 | Archive retrieval delay and fees; manageable lock-in |
| OI-27 | DEC-03 | OPT-11 | CRIT-11 | 58.63 | percent | EST-24 | 4 | EST-24 at the expected case rounds to 59 |
| OI-28 | DEC-03 | OPT-11 | CRIT-12 | judgement | n/a | judgement | 3 | Three tiers and two transition rules to run and monitor |
| OI-29 | DEC-03 | OPT-11 | CRIT-13 | judgement | n/a | judgement | 2 | Adds infrequent-access minimum-duration and retrieval charges (unquantified) |

**Scores.** Weighted score = Σ weight × rating. Ineligible options carry no score.

| ID | Decision | Option | Eligible | Weighted score | Rank | Scored in week |
| --- | --- | --- | --- | --- | --- | --- |
| SC-01 | DEC-01 | OPT-01 | No | n/a | n/a | 5 |
| SC-02 | DEC-01 | OPT-02 | No | n/a | n/a | 5 |
| SC-03 | DEC-01 | OPT-03 | Yes | 2.25 | 2 | 5 |
| SC-04 | DEC-01 | OPT-04 | Yes | 2.75 | 1 | 5 |
| SC-05 | DEC-02 | OPT-05 | No | n/a | n/a | 5 |
| SC-06 | DEC-02 | OPT-06 | Yes | 3.60 | 1 | 5 |
| SC-07 | DEC-02 | OPT-07 | No | n/a | n/a | 5 |
| SC-08 | DEC-02 | OPT-08 | Yes | 3.25 | 2 | 5 |
| SC-09 | DEC-03 | OPT-09 | Yes | 3.40 | 2 | 5 |
| SC-10 | DEC-03 | OPT-10 | Yes | 3.70 | 1 | 5 |
| SC-11 | DEC-03 | OPT-11 | Yes | 3.10 | 3 | 5 |
| SC-12 | DEC-03 | OPT-12 | No | n/a | n/a | 5 |

OPT-01 and OPT-02 are ineligible because they fail GT-01, not because they score low;
OPT-05 fails GT-04, OPT-07 fails GT-05 and OPT-12 fails GT-07. Margins between first and
second place are 0.50 (DEC-01), 0.35 (DEC-02) and 0.30 (DEC-03), all above the 0.15
close-call threshold.

### 6.9 D11 — Trade-off analysis and recommendation (Steps 12 and 13)

#### 6.9.1 Sensitivity analysis

The two least certain inputs per decision were varied one at a time, then the weights were
stressed. Gates are rechecked in every case. Kinds: `stage` replaces a stage duration for
every option; `oi` replaces a numeric option input; `rating` replaces a judgement rating;
`weight` replaces one weight and rescales the others proportionally; `inp` replaces an
estimation input and recomputes the estimates; `threshold` replaces a gate threshold;
`gatevalue` replaces a gate value for the named options.

| ID | Decision | Kind | Target | Value | Case | Winner | Winner score | Runner-up score | Interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SEN-01 | DEC-01 | stage | processing | 6 | Processing budget is 6 s | OPT-04 | 3.00 | 2.25 | Ranking stable; more headroom helps OPT-04 |
| SEN-02 | DEC-01 | stage | processing | 10 | Processing budget is 10 s | OPT-04 | 2.50 | 2.00 | Stable but OPT-04 has no margin left |
| SEN-03 | DEC-01 | stage | processing | 12 | Processing budget is 12 s | none | n/a | n/a | Flip: both options fail GT-01 and the target itself must be revisited |
| SEN-04 | DEC-01 | oi | OPT-04/CRIT-02 | 501 | OPT-04 cost rises 30% | tie | 2.25 | 2.25 | Flip point: OPT-04 and OPT-03 tie |
| SEN-05 | DEC-01 | oi | OPT-04/CRIT-02 | 270 | OPT-04 cost falls 30% | OPT-04 | 3.00 | 2.25 | Stable |
| SEN-06 | DEC-01 | rating | OPT-04/CRIT-04 | 2 | OPT-04 operability is as weak as OPT-03 | OPT-04 | 2.55 | 2.25 | Stable |
| SEN-07 | DEC-01 | oi | OPT-03/CRIT-03 | 6 | OPT-03 delivered in 6 months | OPT-04 | 2.75 | 2.55 | Stable even if DEP-01 is committed early |
| SEN-08 | DEC-01 | weight | CRIT-01 | 0.50 | Freshness headroom weight is 0.50 | tie | 2.50 | 2.50 | Flip point at weight 0.50 |
| SEN-09 | DEC-01 | weight | CRIT-01 | 0.60 | Freshness headroom weight is 0.60 | OPT-03 | 2.60 | 2.40 | Flips beyond 0.50 |
| SEN-10 | DEC-02 | rating | OPT-08/CRIT-08 | 2 | CRM coverage assumption fails (ASM-06) | OPT-06 | 3.60 | 3.00 | Stable; the gap widens |
| SEN-11 | DEC-02 | oi | OPT-06/CRIT-07 | 650 | OPT-06 cost rises 30% | OPT-06 | 3.40 | 3.25 | Stable; margin below 0.15 |
| SEN-12 | DEC-02 | threshold | GT-05 | 6 | Milestone is 6 months, not 9 | OPT-08 | 3.25 | n/a | Flip: OPT-06 fails GT-05; only OPT-08 is eligible |
| SEN-13 | DEC-02 | weight | CRIT-07 | 0.40 | Cost weight is 0.40 | OPT-06 | 3.45 | 3.44 | Near-tie, within noise |
| SEN-14 | DEC-02 | weight | CRIT-07 | 0.50 | Cost weight is 0.50 | OPT-08 | 3.53 | 3.38 | Flips beyond roughly 0.41 |
| SEN-15 | DEC-02 | rating | OPT-06/CRIT-08 | 3 | Match rate is worse than assumed | OPT-06 | 3.35 | 3.25 | Stable; margin below 0.15 |
| SEN-16 | DEC-03 | inp | INP-08 | 0.05 | Growth is 5% | OPT-10 | 3.70 | 3.50 | Stable |
| SEN-17 | DEC-03 | inp | INP-08 | 0.25 | Growth is 25% | OPT-09 | 3.40 | 3.30 | Flip: the baseline wins |
| SEN-18 | DEC-03 | inp | INP-19 | 8 | Archive price is twice the expected | OPT-09 | 3.40 | 3.30 | Flip: the baseline wins |
| SEN-19 | DEC-03 | gatevalue | GT-08/OPT-10;OPT-11 | 30 | Archive retrieval takes 30 hours | OPT-09 | 3.40 | n/a | Flip: OPT-10 and OPT-11 fail GT-08; only the baseline is eligible |

**What the analysis says**

- **DEC-01.** OPT-04 ranks first except under three conditions: the processing stage reaches
  12 s, where both options fail the gate (SEN-03); the freshness-headroom weight reaches 0.50
  or more, where the options tie and then reverse (SEN-08, SEN-09); or the OPT-04 cost reaches
  501 or more, where they tie (SEN-04). The processing-stage
  budget (a `guessed` input) and the OPT-04 cost (an `estimated` input) are the two least
  certain inputs.
- **DEC-02.** OPT-06 ranks first unless the milestone is shorter than 8 months (SEN-12) or
  the cost weight exceeds roughly 0.41 (SEN-14). The milestone date (ASM-01) and CRM coverage
  (ASM-06) are the two least certain inputs.
- **DEC-03.** OPT-10 ranks first at the expected case, but loses to the baseline at 25%
  growth or at twice the archive price, and loses its eligibility if archive retrieval takes
  30 hours. Banded ratings create a cliff: 44.98% savings at 25% growth rounds to 45 and
  drops a band.

#### 6.9.2 Cost, benefit and reversibility

| Decision | Preferred option | Three-year cost or monthly cost | Cost of the baseline | Reversibility | What is traded away |
| --- | --- | --- | --- | --- | --- |
| DEC-01 | OPT-04 | 385k total cost of ownership | OPT-01 costs 250k but fails the freshness gate, so it is not an alternative | Medium: the capture can be switched off; consumers of the event channel would need re-pointing | 135k more than the failed baseline; operational burden of capture-lag monitoring; a thin 2 s margin |
| DEC-02 | OPT-06 | 500k total cost of ownership | OPT-05 costs 90k but cannot produce a reconciled count | High: the index can be retired and sources are unchanged | 140k more than OPT-08; a one-month delivery margin against the milestone assumption |
| DEC-03 | OPT-10 | About 467 currency units per month at Year 7 | OPT-09 costs about 940 per month | Medium: data can be moved back to the interactive tier at a retrieval cost | Retrieval delay for records older than two years; ranking is sensitive to growth and price |

#### 6.9.3 Recommendation

| Decision | Recommendation | Decision state | Missing evidence (owner, week) | Fallback |
| --- | --- | --- | --- | --- |
| DEC-01 | Prefer OPT-04, log-based change capture | Conditional | Security approval of log access (STK-07, 10); non-production p95 freshness at or above EST-13 load (STK-08, 10); budget ceiling (STK-01, 6) | OPT-03 if DEP-01 is committed; otherwise return the target to the sponsor and fraud operations as a requirements decision |
| DEC-02 | Prefer OPT-06, identity registry | Conditional | Milestone date (STK-06, 2); match-rate pilot (STK-02, 6); definitions and owners (STK-01, 6); budget ceiling (STK-01, 6) | OPT-08 if the milestone is shorter than 8 months |
| DEC-03 | Prefer OPT-10, two tiers | Conditional | Measured growth (STK-08, 4); tier prices (STK-04, 6); archive retrieval test (STK-08, 10); 24-month look-back evidence (STK-05, 4) | OPT-09, the single tier |

All three are **Conditional**. DEC-01 and DEC-02 still have `Pending` gates; DEC-03's gates
pass, but only on low-confidence assumptions (ASM-04, ASM-08). A blocking unknown remains for
all three (UNK-03, and UNK-01 for DEC-02). Nothing here is approved.

### 6.10 D12 — Architecture decision records (Step 14)

Status vocabulary: `Proposed`, `Accepted`, `Deprecated`, `Superseded`. "Conditional" is a
decision state recorded beside the status, not a status. No ADR claims approval.

#### Decision log

| ID | Decision | Title | Status | Decision state | Selected option | Decision owner | Related IDs | Open conditions | Revisit trigger | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADR-01 | DEC-01 | Deliver card authorisations by log-based change capture | Proposed | Conditional | OPT-04 | STK-01 | BO-02; REQ-06; TGT-01; EST-13; CON-05; ASM-02; DEP-02; RSK-01; GT-01; CRIT-01 | Security approval; non-production freshness test; budget ceiling; availability target validated | Processing stage above 10 s; OPT-04 cost 501k or more; freshness weight 0.50 or more | SC-04; SEN-01 to SEN-09 |
| ADR-02 | DEC-02 | Establish the authoritative customer record through an identity registry | Proposed | Conditional | OPT-06 | STK-01 | BO-01; BO-03; REQ-01; REQ-03; CON-04; ASM-01; ASM-06; RSK-04; GT-05; CRIT-06 | Milestone date; match-rate pilot; definitions and owners; budget ceiling | Milestone under 8 months; cost weight about 0.41 or more | SC-06; SEN-10 to SEN-15 |
| ADR-03 | DEC-03 | Tier transaction history across interactive and archive storage | Proposed | Conditional | OPT-10 | STK-01 | BO-04; REQ-14; REQ-15; REQ-16; CON-02; ASM-04; ASM-07; ASM-08; GT-07; CRIT-11 | Measured growth; tier prices; archive retrieval test; look-back evidence | Growth 25% or more; archive price doubles; retrieval over 24 hours | SC-10; SEN-16 to SEN-19 |
| ADR-04 | DEC-01 | Contingency: relax the freshness target or adopt source-published events | Proposed | Conditional | OPT-03 | STK-01 | BO-02; REQ-06; DEP-01; GT-01 | Not started; opened only if ADR-01's security or freshness condition fails | Failure of an ADR-01 condition | none |

#### ADR-01 — Deliver card authorisations by log-based change capture

- **Status:** Proposed · **Decision state:** Conditional · **Created:** 2026-10-21 · **Effective date:** TBD
- **Author:** STK-15 · **Decision owner:** STK-01 · **Reviewers (planned):** STK-05, STK-07, STK-08, STK-13, STK-14
- **Related:** BO-02, REQ-06, REQ-10, TGT-01, TGT-05, EST-13, CON-05, ASM-02, DEP-01, DEP-02, RSK-01, RSK-02, GT-01, GT-02, GT-03, CRIT-01 to CRIT-05
- **Evidence:** SC-03, SC-04; TB-13 to TB-24; TCO-03, TCO-04; SEN-01 to SEN-09

**Context.** Fraud analysts see card transactions hours after the fact; the card platform
emits a batch file every 15 minutes (FACT-04). The decision is how eligible card
authorisations reach the case tool for the first release. It excludes the warehouse and the
case-tool product.

**Decision drivers.** Gates: GT-01 (stage budget at most 30 s), GT-02 (residency and
identity), GT-03 (source feasibility). Scored: CRIT-01 headroom 0.25, CRIT-02 cost 0.25,
CRIT-03 delivery 0.15, CRIT-04 operability 0.20, CRIT-05 dependency exposure 0.15. Frozen in
week 4.

**Considered options.** OPT-01 retain batch (budget 918 s); OPT-02 one-minute batches (78 s);
OPT-03 source-published events (27 s, cost 450k, 9 months); OPT-04 log-based capture (28 s,
cost 385k, 7 months).

**Decision outcome.** Prefer OPT-04, conditionally. **Authorised now:** a non-production
technical spike and submission of the security review. **Not authorised:** a production build
commitment or contract spend.

**Rationale.** OPT-01 and OPT-02 fail GT-01 and are not scored. OPT-03 and OPT-04 pass on
budget; OPT-04 scores 2.75 against 2.25 because it is cheaper (385k against 450k), faster to
deliver (7 months against 9) and depends on an internal approval rather than another team's
uncommitted change. The ranking holds in SEN-01, SEN-02, SEN-05, SEN-06 and SEN-07.

**Consequences.** Positive: no change to the card platform application; earliest credible
release. Negative: a margin of only 2 s; operational duties for capture lag and log
retention. Accepted trade-offs: 135k more than the failed baseline; reliance on an
unvalidated change log (ASM-02).

**Rejected alternatives.** OPT-01 fails GT-01 by about 900 s. OPT-02 fails GT-01 (78 s even
at one-minute batches). OPT-03 is credible but ranks second and depends on DEP-01.

**Assumptions and conditions for revisiting.** ASM-02 (low confidence). Reopen if the
processing stage exceeds 10 s (SEN-02, SEN-03), if the OPT-04 cost reaches 501k (SEN-04), if
the freshness weight reaches 0.50 (SEN-08), or if DEP-01 is committed early and OPT-03 is
re-rated.

**Open issues and dependencies.** DEP-02 security approval (STK-07, week 10); UNK-03 budget
ceiling (STK-01, week 6); TGT-03 stays provisional because EST-25 is below the target (RSK-02).
Fallback: ADR-04.

**Approval and review history.** None. No reviewer has seen this record.

**Supersession.** None. ADR-04 would supersede this record only if it is accepted.

#### ADR-02 — Establish the authoritative customer record through an identity registry

- **Status:** Proposed · **Decision state:** Conditional · **Created:** 2026-10-21 · **Effective date:** TBD
- **Author:** STK-15 · **Decision owner:** STK-01 · **Reviewers (planned):** STK-02, STK-03, STK-04, STK-06, STK-11, STK-12
- **Related:** BO-01, BO-03, REQ-01, REQ-03, REQ-04, REQ-18, CON-04, ASM-01, ASM-06, RSK-03, RSK-04, RSK-05, GT-04, GT-05, GT-06, CRIT-06 to CRIT-10
- **Evidence:** SC-06, SC-08; DL-05 to DL-08; TCO-05 to TCO-08; SEN-10 to SEN-15

**Context.** Four functions report different customer counts (FACT-03) and the regulator
wants evidence of origin and accountability (FACT-05). The decision is the approach that
establishes one governed customer identity and count. It excludes schema design and vendor
selection. Customer data is small (EST-16, about 6 GB), so volume does not discriminate.

**Decision drivers.** Gates: GT-04, GT-05 (delivery within 9 months), GT-06. Scored:
CRIT-06 delivery 0.20, CRIT-07 cost 0.20, CRIT-08 coverage 0.25, CRIT-09 ownership clarity
0.20, CRIT-10 reversibility 0.15.

**Considered options.** OPT-05 document definitions only; OPT-06 identity registry; OPT-07
central customer master; OPT-08 designate the CRM.

**Decision outcome.** Prefer OPT-06, conditionally. **Authorised now:** definitions
workshop and a match-rate pilot on a sample. **Not authorised:** a build commitment.

**Rationale.** OPT-05 fails GT-04 (no reconciled count); OPT-07 fails GT-05 (14 months).
OPT-06 scores 3.60 against 3.25 for OPT-08, driven by coverage, ownership clarity and
reversibility, at 140k more cost.

**Consequences.** Positive: sources remain authoritative per attribute; attribute-level
owners are explicit. Negative: a new index to operate; one month of delivery margin.
Accepted trade-offs: higher cost than OPT-08; reliance on a match rate not yet measured.

**Rejected alternatives.** OPT-05 cannot satisfy REQ-01. OPT-07 is too slow and costly (920k).
OPT-08 ranks second and becomes the choice if the milestone is under 8 months (SEN-12) or the
cost weight exceeds about 0.41 (SEN-14).

**Assumptions and conditions for revisiting.** ASM-01 and ASM-06 (low confidence). Reopen if
the confirmed milestone is under 8 months, if the match pilot falls below the assumed
coverage, or if the cost weight is raised.

**Open issues and dependencies.** UNK-01 (STK-06, week 2); UNK-03 (STK-01, week 6); UNK-04
(STK-01, week 6); DEP-03 (STK-06, week 3); RSK-03 and RSK-04.

**Approval and review history.** None.

**Supersession.** None.

#### ADR-03 — Tier transaction history across interactive and archive storage

- **Status:** Proposed · **Decision state:** Conditional · **Created:** 2026-10-21 · **Effective date:** TBD
- **Author:** STK-15 · **Decision owner:** STK-01 · **Reviewers (planned):** STK-04, STK-05, STK-06, STK-07
- **Related:** BO-04, REQ-14, REQ-15, REQ-16, CON-02, TGT-06, TGT-07, ASM-04, ASM-07, ASM-08, RSK-06, GT-07, GT-08, GT-09, CRIT-11 to CRIT-13
- **Evidence:** SC-09 to SC-11; EST-09, EST-17 to EST-24; TN-01 to TN-10; SEN-16 to SEN-19

**Context.** Seven years of transaction records must be kept (CON-02). The expected cumulative
physical volume is about 41 TB (EST-09), with a wide range (12–217 TB). The decision is how to
place it across tiers. It excludes product selection and backup design.

**Decision drivers.** Gates: GT-07 (seven years), GT-08 (retrieval within 24 h), GT-09
(24 months interactive). Scored: CRIT-11 cost reduction 0.40, CRIT-12 operational simplicity
0.30, CRIT-13 retrieval-cost and lock-in exposure 0.30.

**Considered options.** OPT-09 single tier; OPT-10 two tiers; OPT-11 three tiers; OPT-12
shorter detail retention.

**Decision outcome.** Prefer OPT-10, conditionally. **Authorised now:** collecting growth and
price evidence and a retrieval test. **Not authorised:** configuring lifecycle rules in
production.

**Rationale.** OPT-12 fails GT-07. Among eligible options, OPT-10 scores 3.70 against 3.40
(OPT-09) and 3.10 (OPT-11): it saves about 50% against the baseline, while OPT-11 adds eight
points of saving at the same rating but more complexity and lock-in.

**Consequences.** Positive: about half the monthly storage cost (467 against 940 currency
units at Year 7). Negative: retrieval delay for records older than two years; lifecycle rules
to monitor. Accepted trade-offs: operational simplicity; sensitivity to growth and price.

**Rejected alternatives.** OPT-09 is simplest but costs about twice as much. OPT-11 is cheaper
but adds a tier and unquantified charges. OPT-12 violates the retention constraint.

**Assumptions and conditions for revisiting.** ASM-04, ASM-07, ASM-08 (all low confidence).
Reopen if growth reaches 25% (SEN-17), the archive price doubles (SEN-18) or retrieval exceeds
24 hours (SEN-19).

**Open issues and dependencies.** Growth measurement (STK-08, week 4); look-back evidence
(STK-05, week 4); tier prices (STK-04, week 6); retrieval test (STK-08, week 10); UNK-03.

**Approval and review history.** None.

**Supersession.** None.

#### ADR review checklist (applied to the three records above)

| Check | ADR-01 | ADR-02 | ADR-03 |
| --- | --- | --- | --- |
| Problem and scope clear without the original meeting | Yes | Yes | Yes |
| Status accurate; decision owner named | Yes | Yes | Yes |
| Drivers linked to requirements, constraints or targets | Yes | Yes | Yes |
| Options credible and fairly described | Yes | Yes | Yes |
| Rejected alternatives and reasons recorded | Yes | Yes | Yes |
| Rationale cites evidence, not adjectives | Yes | Yes | Yes |
| Positive and negative consequences present | Yes | Yes | Yes |
| Assumptions, unknowns and dependencies visible | Yes | Yes | Yes |
| Revisit conditions specific and actionable | Yes | Yes | Yes |
| No approval claimed without evidence | Yes | Yes | Yes |

This is the author's self-check, not an independent review.

### 6.11 D5 — Requirement traceability matrix (Step 15)

Each row walks one business objective to its requirements, targets and estimates, its
constraints, assumptions, dependencies, risks and unknowns, its criteria and gates, and the
decisions that depend on it. The checker confirms that every requirement appears in the row of
its objective and that every objective reaches an ADR.

| ID | BO | REQ | TGT and EST | CON, ASM, DEP, RSK, UNK | CRIT and GT | ADR |
| --- | --- | --- | --- | --- | --- | --- |
| TR-01 | BO-01 | REQ-01; REQ-02; REQ-21 | TGT-08; EST-16 | ASM-06; RSK-03; RSK-05; UNK-04 | CRIT-06; CRIT-07; CRIT-08; CRIT-09; CRIT-10; GT-04 | ADR-02 |
| TR-02 | BO-02 | REQ-05; REQ-06; REQ-07; REQ-08; REQ-09; REQ-10; REQ-20 | TGT-01; TGT-02; TGT-03; TGT-04; TGT-05; EST-12; EST-13; EST-25 | ASM-02; ASM-03; ASM-05; DEP-01; DEP-02; DEP-05; RSK-01; RSK-02; UNK-05 | CRIT-01; CRIT-02; CRIT-03; CRIT-04; CRIT-05; GT-01; GT-03 | ADR-01; ADR-04 |
| TR-03 | BO-03 | REQ-03; REQ-04; REQ-18; REQ-22; REQ-23 | TGT-09 | CON-04; ASM-01; DEP-03; RSK-04; UNK-01 | GT-05 | ADR-02 |
| TR-04 | BO-04 | REQ-14; REQ-15; REQ-16 | TGT-06; TGT-07; EST-09; EST-15; EST-23; EST-24 | CON-02; ASM-04; ASM-07; ASM-08; RSK-06 | CRIT-11; CRIT-12; CRIT-13; GT-07; GT-08; GT-09 | ADR-03 |
| TR-05 | BO-05 | REQ-11; REQ-12; REQ-13 | none | CON-01; CON-05; DEP-04; RSK-07; UNK-02 | GT-02; GT-06 | ADR-01; ADR-02; ADR-03 |
| TR-06 | BO-06 | REQ-17; REQ-19; REQ-24 | none | CON-03; CON-06; RSK-08; RSK-09; UNK-03 | CRIT-02; CRIT-07 | ADR-01; ADR-02; ADR-03 |

**Recorded random traces** (author-run, using `--trace`; not independently reviewed)

```text
ADR-01 <- BO-02: Fraud analysts see card transactions in time to act before t... <- REQ-05 <- STK-05
ADR-02 <- BO-01: One governed, reproducible customer count and definition use... <- REQ-01 <- STK-02; STK-03
ADR-04 <- BO-02: Fraud analysts see card transactions in time to act before t... <- REQ-05 <- STK-05
BO-02 -> REQ-05 -> TGT-01 -> CRIT-01 -> ADR-01; ADR-04
BO-05 -> REQ-11 -> none -> GT-02 -> ADR-01; ADR-02; ADR-03
BO-04 -> REQ-14 -> TGT-06 -> CRIT-11 -> ADR-03
```

### 6.12 D13 — Final requirements and architecture decision summary (Step 17)

**Northbridge Bank — Requirements and architecture decision pack. Version 1.1, 2026-10-21. ILLUSTRATIVE.**

**Problem.** Customer data is inconsistent across functions, fraud signals reach analysts
hours late, and the bank cannot readily evidence lineage and accountability to a regulator
that has asked for it by a date.

**What was decided, and not decided.** Three high-level decisions were analysed, each at
option-category level. Each has a preferred option, but **all three are conditional and
nothing is approved**: some gates are still pending, key assumptions are low-confidence, and two
unknowns block final acceptance (the budget ceiling for all three, and the regulatory milestone
date for the customer-record decision).

| Decision | Preferred option | Why | Main condition |
| --- | --- | --- | --- |
| Card transactions to the fraud case tool | Log-based change capture (OPT-04) | The only alternative besides source-published events that meets the 30-second target on paper; cheaper and faster to deliver | Security approval and a measured freshness test |
| Authoritative customer record | Identity registry (OPT-06) | Best coverage, ownership clarity and reversibility; meets a 9-month milestone assumption | Confirm the milestone date; run a match-rate pilot |
| Retention and tiering | Two tiers (OPT-10) | About half the storage cost of a single tier while meeting retention and retrieval gates | Measure growth and tier prices; test archive retrieval |

**Key targets (illustrative, unvalidated).** p95 freshness at most 30 s for card
authorisations 08:00–20:00 (TGT-01); 138.9 events/s sustained capacity (EST-13); seven-year
retention with 24-hour retrieval (TGT-06); 24 months interactive at p95 5 s (TGT-07).

**Key figures.** About 4.6 GB per day of logical data (EST-04); about 41 TB physical over
seven years at the expected case, with a stress range of 12–217 TB (EST-09).

**Accepted trade-offs.** A thin 2-second freshness margin; 135k more than the failed
baseline for the fraud path; 140k more than the CRM option for the customer record; retrieval
delay for records older than two years.

**Top risks.** Regulatory milestone unconfirmed (RSK-04, exposure 15, very high); log access
refused or unsupported (RSK-01); modelled availability of 99.70% against a 99.9% target
(RSK-02); definition owners disagree (RSK-03); identity matching weaker than assumed (RSK-05).

**What would change the answer.** Processing time above 10 s; a milestone under 8 months;
growth at 25% or archive prices doubling; a freshness weight of 0.50 or more.

**Caveats and limits.** Every figure is illustrative. No stakeholder has validated any row.
Sensitivity covered the least certain inputs one at a time, not every combination. Ratings
for operability, dependencies, coverage, ownership and reversibility are judgements, anchored
but not measured. This pack is a decision baseline for modules 2D.3 onward, not a design.

### 6.13 Review notes and validation log (Step 16)

Status shows that **no independent review has taken place** for this worked reference. The
author's self-review used the checker and the critical-error list in Section 7.4.

| ID | Subject | Reviewer role | Review method | Planned week | Recorded response | Status |
| --- | --- | --- | --- | --- | --- | --- |
| VL-01 | Business objectives and requirements (BO-01 to BO-06, REQ-01 to REQ-24) | STK-05; STK-06 | Walk-through of each Must against its acceptance criterion | 7 | Not yet recorded | Planned |
| VL-02 | Estimation worksheet (EST-01 to EST-29) | STK-08; STK-04 | Reviewer recomputes at least three figures | 7 | Not yet recorded | Planned |
| VL-03 | Targets and timing budgets (TGT-01 to TGT-09, TB-01 to TB-24) | STK-08; STK-05 | Feasibility challenge against source cadence | 7 | Not yet recorded | Planned |
| VL-04 | Register (CON, ASM, DEP, RSK, UNK) | STK-07; STK-12 | Classification test on a sample of ten items | 7 | Not yet recorded | Planned |
| VL-05 | Criteria, gates and scoring (D9, D10) | STK-14 | Confirm criteria were frozen before scoring | 7 | Not yet recorded | Planned |
| VL-06 | ADR-01 to ADR-03 | STK-10 | Independent challenge against the ADR checklist | 8 | Not yet recorded | Planned |

---

## 7. Validation and quality assurance

### 7.1 Quality criteria and how each is verified

| Check | How to verify | Automated? |
| --- | --- | --- |
| Business requirements traceable to stakeholder needs | Each BO cites a stakeholder and an interview statement; sample five | Yes (references) |
| Functional and non-functional requirements distinguishable | Type field present; no sentence mixes both | Partly (type values) |
| Important requirements have measurable acceptance criteria | Every Must has a measurable criterion containing a number | Yes |
| No requirement embeds a technology | Scan requirement text for technology terms | Yes |
| Estimates carry units, formulas, assumptions, interpretation | Reviewer recomputes three figures | Yes (all recomputed) |
| Targets measurable and internally consistent | Timing budget sums; availability composition checked | Yes |
| Constraints, assumptions, dependencies, risks classified correctly | Topic 5 tests on ten items | Partly (field completeness, exposure) |
| Alternatives feasible within scope | Each option passes all gates or is removed with a reason | Yes |
| Criteria and weights fixed before scoring | Freeze week precedes scoring week | Yes |
| Recommendation follows from evidence and sensitivity | Scores recomputed; sensitivity recomputed | Yes |
| ADRs explain context, decision, rationale, consequences | Topic 7 checklist | Partly (index consistency) |
| No unresolved contradiction presented as settled | Cross-document read | Partly (global ID check) |
| Traceability both directions | Trace test | Yes |

### 7.2 Running the checker

Extract Appendix B to `check_decision_pack.py`, then run:

```bash
python3 check_decision_pack.py "Stage 2D — Data Architecture/02-Requirements-Constraints-and-Architecture-Decisions/Projects/02-requirements-and-architecture-decision-pack.md"
python3 check_decision_pack.py FILE --trace 3 --seed 2026
python3 check_decision_pack.py FILE --report
```

The checker exits `0` when every check passes and `1` otherwise. `--report` prints the
recomputed estimates, scores and sensitivity cases for review. For a real project (Mode B),
keep the header names or adapt the `KINDS` mapping at the top of the script.

### 7.3 What the checker verifies

- **Structure:** unique IDs, no empty cells, valid evidence and estimate labels, every ID reference resolves to a defined item.
- **Requirements:** types, priorities, a measurable criterion on every Must, at least 90% of Musts measurable, no technology terms, objective links.
- **Estimates:** every expression is recomputed for the low, expected and high cases and compared with the stated values; the tornado is recomputed.
- **Targets:** timing budgets sum to the stated totals; gate values match their sources.
- **Registers:** risk exposure and band; owners, responses and triggers for high exposure; owners and validation weeks for assumptions.
- **Decisions:** weights sum to 1; bands are contiguous; ratings follow the bands; gate results follow their thresholds; only options with no failed gate are scored; scores and ranks are recomputed; criteria are frozen before scoring.
- **Sensitivity:** every case is re-run, with gates rechecked, and compared with the stated winner and scores.
- **Traceability:** every requirement appears in its objective's row; every objective reaches an ADR; every ADR is reachable; decision owners hold the decision rights.

### 7.4 Critical-error list (self-review, mapped to the practice-question criteria)

| Critical error | How this pack guards against it |
| --- | --- |
| A requirement embeds a technology | Technology scan of requirement and objective text |
| A Must has no measurable criterion | Checker; REQ-13 and REQ-17 are measurable in form, pending UNK-02 and UNK-03 |
| Unit or arithmetic error | All estimates recomputed |
| Misclassified constraint, assumption, dependency or risk | Section 4.3 classification test; PREF-01 kept apart from constraints |
| An option that fails a gate stays eligible | Gate results recomputed; scores only for eligible options |
| Criteria or weights changed after scoring | Frozen in week 4; scored in week 5 |
| Recommendation ignores sensitivity | Section 6.9.1 states every flip point |
| An ADR claims approval or erases history | All statuses are `Proposed`; supersession path recorded |
| A high-exposure risk or high-impact assumption has no owner or action | Checker |
| Contradictions presented as settled | Global ID check; every decision is Conditional |

### 7.5 Project completion gate (roadmap Section 7.7) and worked-reference status

| Gate item | Mode A status (Northbridge worked reference) | Mode B requirement |
| --- | --- | --- |
| D1–D13 exist, version-dated, consistent IDs | Met: Section 6, version 1.1, checker passes | Met for your own set |
| At least 90% of Musts have a measurable criterion; no technology in requirements | Met: all Musts measurable in form; technology scan passes. Several parameter values are pending named unknowns | Met with confirmed parameters |
| Every estimate has unit, formula, assumption, evidence label; reviewer recomputes three | Met by the checker; **independent recomputation not performed** | Required |
| Each target names indicator, percentile, window, scope, method; budget sums | Met | Met |
| Every item classified; every high-exposure risk has owner, response, trigger; high-impact assumptions have validation | Met | Met |
| At least three alternatives per decision including a baseline, compared on criteria set before scoring | Met (four per decision) | Met |
| Sensitivity on the two least certain inputs; ranking change stated | Met (SEN-01 to SEN-19) | Met |
| ADR per major decision with rejected alternatives, consequences, revisit conditions; conditional decisions name missing evidence | Met; all conditional | Met |
| Random trace from three ADRs to objectives and three objectives to ADRs | Met by the checker; **not witnessed by a reviewer** | Required |
| Final recommendation readable by a non-specialist in ten minutes; states limits | Written to that standard; **reader test not performed** | Required |
| Independent reviewer agrees the evidence supports the conclusions | **Not met by design** | Required |

### 7.6 Anticipated reviewer challenges (author-prepared, not recorded reviewer objections)

| Challenge | Answer using recorded evidence |
| --- | --- |
| "Why not take the cheapest option, OPT-01?" | It fails GT-01 by about 900 s (GR-01); a low cost cannot rescue a failed gate. |
| "Your operability rating favours OPT-04 without data." | The rating is a judgement (OI-09). SEN-06 sets OPT-04 operability equal to OPT-03's and OPT-04 still ranks first (2.55 against 2.25). |
| "Why is the identity registry better than the CRM?" | Coverage, ownership clarity and reversibility (OI-13 to OI-15). SEN-14 shows the CRM wins if cost carries a weight above roughly 0.41, so the choice rests on that priority being agreed with the sponsor. |

---

## 8. Templates and guides for a real organisation (Mode B)

Placeholders use the form `XXX-nn`; replace them with real IDs.

### 8.1 Row templates

**Requirement**

| ID | Requirement statement | Type | Quality attribute | BO | Priority | Priority rule | Acceptance criterion | AC measurable | Verification method | Accepting role | Source | Status | Architecturally significant | Linked IDs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-nn | The [capability] shall [behaviour or quality] for [scope] under [conditions] | FR / NFR / DR | attribute or n/a | BO-nn | Must / Should / Could | M1 to M3, S1, C1 | metric, threshold, scope, window | Y / N | test, inspection, reconciliation | role | stakeholder | Draft / Validated / Changed | Y / N | IDs |

**Estimation input and estimate**

| ID | Input | Unit | Low case | Expected | High case | Estimate label | Basis and validation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| INP-nn | quantity | unit | value | value | value | measured / sampled / stated / estimated / guessed | source and how it will be validated |

| ID | Estimate | Expression | Unit | Low case | Expected | High case | Interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EST-nn | quantity | `INP-nn*INP-nn/1000000000` | unit | value | value | value | architecture implication |

**Risk (cause–event–effect)**

> Because **[cause or condition]**, **[uncertain event]** may occur, resulting in **[effect on an objective]**.

**Change-impact record.** When a requirement, constraint or estimate changes, list: the
changed item; every register row that cites it; every criterion and gate it touches; the
options whose gate results or ratings change; the ADRs to reopen; and the owner and date.

**Interview record.** Verbatim statements first; classification second; interpretation
third; follow-ups last. Never merge a quote with its interpretation.

### 8.2 Elicitation guide (by stakeholder group)

| Group | Questions that produce evidence |
| --- | --- |
| Sponsor | Which outcome matters most if not all can be met? What is the ceiling and the deadline? Which choices are already made? |
| Business owners | What decision does this data support? What delay or error changes it? Who else uses the number? |
| Control functions | Which obligation applies, from which authority, by when? What evidence will you accept? |
| Engineering | What can each source emit today? Which interfaces exist, and who owns a change? |
| Operations | What breaks most often? Which windows are untouchable? |
| Audit | Which evidence would you accept for lineage and ownership? |

Always ask: *Who else is affected? What would you show me to prove it? What are you least sure about?*

### 8.3 Decision-pack checklist before review

- Scope states exclusions; decision-makers are named.
- Every Must has a metric, target, scope, method and accepting role.
- No requirement names a technology.
- Every estimate shows formula, units, assumption, label and range.
- Gates are defined before weights; weights are frozen and dated before scoring.
- Every option fails or passes each gate with evidence.
- Sensitivity covers the two least certain inputs and states flip points.
- Every ADR lists rejected alternatives, consequences and revisit conditions.
- The checker passes; a reviewer has traced three ADRs back and three objectives forward.

---

## 9. Common pitfalls and project risks

| Pitfall | Why it harms | Prevention |
| --- | --- | --- |
| Treating a request as a requirement | A solution is baked in before the need is understood | Why-ladder; record the verbatim statement first |
| Adjectives instead of numbers ("fast", "real-time") | Nothing can be tested | Percentile, threshold, window, scope, method |
| Putting a technology in a requirement | Eliminates options without a business reason | Technology scan; describe outcomes |
| Using a batch interval to hide latency | The source wait is excluded from the target | Name the boundary; include source wait |
| Confusing logical, physical and capacity | Budgets are wrong by multiples | Separate rows for layers, copies, overhead |
| Using the average peak | Under-sized or over-sized capacity | Peak factor from time-bucketed history |
| Giving a mandatory condition a weight | A cheap option can violate it and still win | Gates first; weights only for eligible options |
| Changing weights after seeing the winner | Destroys trust in the comparison | Freeze weeks recorded and checked |
| A weak baseline | Makes any change look good | Give the baseline its strongest credible design |
| Reporting a score as proof | Hides ordinal and judgemental inputs | Show criterion-level ratings, gates and sensitivity |
| ADR written after the fact with no rejected options | The reasoning cannot be reproduced | Write alongside the comparison; link evidence |
| Claiming approval without evidence | Misleads readers and auditors | Status `Proposed` until a recorded approval exists |

**Project-level risks**

| Risk | Early sign | Response |
| --- | --- | --- |
| Stakeholders unavailable | Interviews slip a week | Record the gap as an unknown with an owner; do not invent a position |
| Scope creep into design | Options acquire product names or schemas | Return to option categories; defer to later modules |
| Unknowns block the decision | A blocking unknown is still open at the criteria freeze | Make the decision conditional; name the owner and date |
| Numbers drift between artefacts | The worksheet and the ADR disagree | One source of truth; run the checker before every release |

---

## 10. Connection to subsequent modules

The pack is a **decision baseline**, not a design. It supports later work without
absorbing it.

| Later module | What it takes from this pack |
| --- | --- |
| 2D.3 Patterns and reference architectures | Criteria, targets and constraints are the filter for patterns; ADRs record pattern decisions |
| 2D.4 Conceptual, logical and physical modeling | BO-01 and the customer-record decision define entities and quality needs |
| 2D.5 Storage architecture | EST-05 to EST-24, ADR-03 and the retention constraint feed storage selection |
| 2D.6 Integration | TGT-01, TGT-04, TGT-05, EST-13 and the source constraints drive integration choices |
| 2D.7 Enterprise platform | Capacity, service levels and the dependency map shape platform scope |
| 2D.8 Cloud and hybrid | CON-01, CON-06 and the cost model bound cloud options |
| 2D.15 Architecture reviews | The decision log, traceability matrix and validation log are review inputs |

**Open questions to carry into module 2D.3:** UNK-01 to UNK-05; the role boundary between
the warehouse and the lake (from Module 2D.1); and the availability gap in RSK-02.

---

## 11. Self-assessment rubric

Score each criterion 0 (absent), 1 (partial) or 2 (complete). Pass requires at least 90%
of the maximum and no zero.

| # | Criterion | Evidence |
| --- | --- | --- |
| 1 | Scope names exclusions and the decision boundaries | D1 |
| 2 | Stakeholders include control functions and hidden stakeholders; every decision has a decision-maker | D2 |
| 3 | Statements recorded verbatim before interpretation; conflicts logged | D3 |
| 4 | Requirements are typed, prioritised with a rule, free of technology and testable | D4, checker |
| 5 | Estimates show formula, units, labels, ranges and a sensitivity ranking | D6, checker |
| 6 | Targets name indicator, percentile, window, scope and method; budgets sum | D7, checker |
| 7 | Items classified; owners, responses, triggers and validation set | D8, checker |
| 8 | Gates and weights fixed before scoring | D9, checker |
| 9 | At least three real options per decision including a baseline | D10 |
| 10 | Failed-gate options are not scored | D10, checker |
| 11 | Sensitivity covers the two least certain inputs and states flip points | D11 |
| 12 | ADRs hold rejected alternatives, consequences and revisit conditions; no unsupported approval | D12 |
| 13 | Traceability passes in both directions | D5, checker |
| 14 | Summary states conditions and limits and can be read in ten minutes | D13 |
| 15 | An independent reviewer agrees the evidence supports the conclusions | Reviewer note |

---

## Appendix A — Glossary

| Term | Meaning in this project |
| --- | --- |
| Acceptance criterion | A pass/fail condition with a metric, target, scope and method |
| Architecturally significant requirement | A requirement likely to change the solution structure or remove whole classes of options |
| Conditional decision | A decision whose preferred option depends on named missing evidence; a state, not a status |
| Constraint | A confirmed limit the solution must respect, with an authority and a flexibility |
| Gate | A pass/fail eligibility test applied before scoring |
| Preference | A desired outcome that can be traded off; never a gate |
| SLI, SLO | The measured signal and the target for that signal over a window |
| Stage budget | The planned duration of one step in a pipeline; a worst-case sequential model, not a measured percentile |
| Tornado | A ranking of inputs by their effect on an output when varied alone |

---

## Appendix B — Consistency checker (`check_decision_pack.py`)

Python 3.9 or later; standard library only. It reads the Markdown tables in this file.

```python
#!/usr/bin/env python3
"""Consistency checker for the requirements and architecture decision pack (D1-D13).

Usage:
    python3 check_decision_pack.py FILE
    python3 check_decision_pack.py FILE --report
    python3 check_decision_pack.py FILE --trace 3 --seed 2026

Exit code 0 means every check passed; 1 means at least one error.
"""
import argparse
import ast
import math
import operator
import random
import re
import sys
from pathlib import Path

ID_CELL = re.compile(r"^[A-Z]{2,4}-\d{2}$")
PREFIXES = ("STK|INT|CF|BO|REQ|TGT|EST|INP|TN|TB|FACT|CON|PREF|ASM|DEP|RSK|UNK|GT|GR|"
            "CRIT|AN|JA|OPT|TCO|DL|OI|SC|SEN|DEC|ADR|TR|VL")
ID_ANY = re.compile(rf"\b(?:{PREFIXES})-\d{{2}}\b")
SEPARATOR = re.compile(r"^:?-{3,}:?$")
EVIDENCE = {"Verified fact", "Stakeholder statement", "Illustrative assumption",
            "Inference", "Open question"}
ESTIMATE_LABELS = {"measured", "sampled", "stated", "estimated", "guessed"}
LEVEL = {"Low", "Medium", "High"}
STATUS = {"Proposed", "Accepted", "Deprecated", "Superseded"}
TECH_TERMS = re.compile(
    r"\b(kafka|kinesis|pulsar|rabbitmq|snowflake|redshift|bigquery|databricks|spark|flink|"
    r"airflow|dbt|hadoop|s3|aws|azure|gcp|oracle|postgres(?:ql)?|mysql|mongodb|cassandra|"
    r"sql|etl|mdm|cdc|lakehouse|data lake|warehouse|streaming|micro-?batch)\b", re.I)
CLOSE_CALL = 0.15
CASES = ("Low case", "Expected", "High case")

# A table is recognised by one header that only that table has.
KINDS = {
    "Stakeholder (role)": "STK", "Verbatim statement (hypothetical)": "INT",
    "Conflict": "CF", "Business objective": "BO", "Requirement statement": "REQ",
    "Estimate label": "INP", "Expression": "EST", "Swing": "TN",
    "SLI definition": "TGT", "Stage": "TB", "Statement": "FACT",
    "Preference": "PREF", "Constraint": "CON", "Impact if wrong": "ASM",
    "Failure consequence": "DEP", "Probability": "RSK", "Blocks": "UNK",
    "Gate statement": "GT", "Rating basis": "CRIT", "From": "AN",
    "Anchor for 1": "JA", "Option description": "OPT", "Build and migration": "TCO",
    "Delivery months": "DL", "Gate": "GR", "Input value": "OI", "Eligible": "SC",
    "Winner": "SEN", "Decision-maker": "DEC", "Selected option": "ADR",
    "CRIT and GT": "TR", "Planned week": "VL",
}
NEEDS_LABEL = {"STK", "INT", "BO", "FACT", "PREF", "CON", "ASM", "DEP", "RSK", "TGT",
               "TB", "TCO", "DL"}


# ----------------------------------------------------------------------------- parsing
def num(text):
    """Parse a number from a table cell; return None for n/a or non-numeric text."""
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
    errors, prose = [], []
    in_fence, prev, header = False, None, None
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence, prev, header = not in_fence, None, None
            continue
        if in_fence:
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
    return tables, "\n".join(prose), errors


# ----------------------------------------------------------------------------- expressions
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.Pow: operator.pow}


def evaluate(expression, env):
    """Evaluate +, -, *, /, ** over numbers and names only."""
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
        raise ValueError(f"unsupported expression: {expression}")
    cleaned = re.sub(r"\b([A-Z]{3})-(\d{2})\b", r"\1_\2", expression.replace("`", ""))
    return go(ast.parse(cleaned, mode="eval"))


def estimates(tables, case, override=None):
    """Return {id: value} for inputs and estimates in one case column."""
    env = {}
    for iid, row in tables["INP"].items():
        env[iid.replace("-", "_")] = num(row[case])
    if override:
        env.update({k.replace("-", "_"): v for k, v in override.items()})
    out = {}
    pending = dict(tables["EST"])
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


# ----------------------------------------------------------------------------- decision engine
class Engine:
    def __init__(self, tables):
        self.t = tables
        self.bands = {}
        for row in tables["AN"].values():
            self.bands.setdefault(row["Criterion"], []).append(
                (int(row["Rating"]), num(row["From"]), num(row["To"])))

    def tb_sum(self, option, stage_override=None):
        total = 0.0
        for row in self.t["TB"].values():
            if row["Option"] == option:
                seconds = num(row["Seconds"])
                if stage_override and row["Stage"] == stage_override[0]:
                    seconds = stage_override[1]
                total += seconds
        return total

    def months(self, option):
        for row in self.t["DL"].values():
            if row["Option"] == option:
                return num(row["Delivery months"])
        return None

    def tco(self, option):
        for row in self.t["TCO"].values():
            if row["Option"] == option:
                return num(row["Total"])
        return None

    def band(self, criterion, value):
        x = half_up(value)
        for rating, lo, hi in self.bands[criterion]:
            if lo <= x <= hi:
                return rating
        return None

    def gate_value(self, gate, option, ov):
        row = self.t["GT"][gate]
        source = row["Value source"]
        if source == "TB":
            return self.tb_sum(option, ov.get("stage"))
        if source == "DL":
            return self.months(option)
        if source == "stated":
            override = ov.get("gatevalue", {})
            if gate in override and option in override[gate][0]:
                return override[gate][1]
            for g in self.t["GR"].values():
                if g["Gate"] == gate and g["Option"] == option:
                    return num(g["Value"])
        return None

    def gate_result(self, gate, option, ov):
        row = self.t["GT"][gate]
        value = self.gate_value(gate, option, ov)
        if row["Operator"] == "n/a" or value is None:
            for g in self.t["GR"].values():
                if g["Gate"] == gate and g["Option"] == option:
                    return g["Result"]
            return "Pending"
        threshold = ov.get("threshold", {}).get(gate, num(row["Threshold"]))
        ok = value <= threshold if row["Operator"] == "<=" else value >= threshold
        return "Pass" if ok else "Fail"

    def options(self, decision):
        return [o for o, r in self.t["OPT"].items() if r["Decision"] == decision]

    def eligible(self, decision, ov):
        gates = [g for g, r in self.t["GT"].items() if r["Decision"] == decision]
        return [o for o in self.options(decision)
                if all(self.gate_result(g, o, ov) != "Fail" for g in gates)]

    def weights(self, decision, ov):
        crit = {c: num(r["Weight"]) for c, r in self.t["CRIT"].items()
                if r["Decision"] == decision}
        if "weight" in ov and ov["weight"][0] in crit:
            target, new = ov["weight"]
            rest = sum(w for c, w in crit.items() if c != target)
            crit = {c: (new if c == target else w * (1 - new) / rest)
                    for c, w in crit.items()}
        return crit

    def resolved_input(self, row, ov):
        source = row["Value source"]
        option, criterion = row["Option"], row["Criterion"]
        if "oi" in ov and ov["oi"][:2] == (option, criterion):
            return ov["oi"][2]
        if source == "TBM":
            gate = next(g for g, r in self.t["GT"].items()
                        if r["Decision"] == row["Decision"] and r["Value source"] == "TB")
            threshold = ov.get("threshold", {}).get(gate, num(self.t["GT"][gate]["Threshold"]))
            return threshold - self.tb_sum(option, ov.get("stage"))
        if source == "TCO":
            return self.tco(option)
        if source == "DL":
            return self.months(option)
        if source.startswith("EST-"):
            values, _ = estimates(self.t, "Expected", ov.get("inp"))
            return values[source]
        if source == "stated":
            return num(row["Input value"])
        return None

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
            result[option] = sum(weights[r["Criterion"]] * self.rating(r, ov) for r in rows)
        return result


def outcome(scores):
    """Return (winner, winner_score, runner_up_score) with ties after 2-decimal rounding."""
    ranked = sorted(((round(s, 2), o) for o, s in scores.items() if s is not None),
                    reverse=True)
    if not ranked:
        return "none", None, None
    if len(ranked) == 1:
        return ranked[0][1], ranked[0][0], None
    if ranked[0][0] == ranked[1][0]:
        return "tie", ranked[0][0], ranked[1][0]
    return ranked[0][1], ranked[0][0], ranked[1][0]


def parse_override(row, t):
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


# ----------------------------------------------------------------------------- checks
def check(tables, prose):
    errors = []

    def err(rid, message):
        errors.append(f"{rid}: {message}")

    t = tables
    defined = set().union(*(set(v) for v in t.values()))
    # 1. generic row checks
    for kind, rows in t.items():
        for rid, row in rows.items():
            for column, value in row.items():
                if column == "_line":
                    continue
                if not value:
                    err(rid, f"empty cell in '{column}'")
            if kind in NEEDS_LABEL and row.get("Evidence") not in EVIDENCE:
                err(rid, f"evidence label '{row.get('Evidence')}' is invalid")
    for token in sorted(set(ID_ANY.findall(prose)) - defined):
        err(token, "referenced but never defined")

    # 2. stakeholders, decisions
    for did, d in t["DEC"].items():
        maker = d["Decision-maker"]
        if maker not in t["STK"] or did not in t["STK"][maker]["Decision rights"]:
            err(did, f"decision-maker {maker} does not hold the decision right")
    for iid, i in t["INT"].items():
        if i["Stakeholder"] not in t["STK"]:
            err(iid, "unknown stakeholder")

    # 3. requirements
    musts = []
    for rid, r in t["REQ"].items():
        if r["Type"] not in ("FR", "NFR", "DR"):
            err(rid, f"invalid type {r['Type']}")
        if r["BO"] not in t["BO"]:
            err(rid, "unknown business objective")
        rule = {"Must": ("M1", "M2", "M3"), "Should": ("S1",), "Could": ("C1",)}.get(r["Priority"])
        if rule is None or r["Priority"] and r["Priority rule"] not in rule:
            err(rid, f"priority '{r['Priority']}' and rule '{r['Priority rule']}' do not match")
        if r["Status"] not in ("Draft", "Validated", "Changed"):
            err(rid, f"invalid status {r['Status']}")
        if r["Architecturally significant"] not in ("Y", "N") or r["AC measurable"] not in ("Y", "N"):
            err(rid, "Y/N fields must be Y or N")
        if TECH_TERMS.search(r["Requirement statement"]):
            err(rid, f"technology term in requirement: {TECH_TERMS.search(r['Requirement statement']).group()}")
        if r["Priority"] == "Must":
            musts.append(rid)
            if r["AC measurable"] == "Y" and not re.search(r"\d", r["Acceptance criterion"]):
                err(rid, "acceptance criterion marked measurable but contains no number")
    for bid, b in t["BO"].items():
        source = b["Source"]
        owners = set(refs(source)) & set(t["STK"])
        for iid in set(refs(source)) & set(t["INT"]):
            if t["INT"][iid]["Stakeholder"] not in owners:
                err(bid, f"{iid} is by {t['INT'][iid]['Stakeholder']}, who is not cited as a source")
        if TECH_TERMS.search(b["Business objective"] + " " + b["Success criterion (proposed)"]):
            err(bid, "technology term in business objective")
    if musts:
        share = sum(t["REQ"][m]["AC measurable"] == "Y" for m in musts) / len(musts)
        if share < 0.9:
            err("REQ", f"only {share:.0%} of Musts have a measurable criterion")
    for tid, g in t["TGT"].items():
        if g["Requirement"] not in t["REQ"]:
            err(tid, "unknown requirement")

    # 4. estimates
    for iid, row in t["INP"].items():
        if row["Estimate label"] not in ESTIMATE_LABELS:
            err(iid, f"invalid estimate label {row['Estimate label']}")
        if any(num(row[c]) is None for c in CASES):
            err(iid, "case values must be numeric")
    for case in CASES:
        values, unresolved = estimates(t, case)
        for eid in unresolved:
            err(eid, f"cannot be evaluated in '{case}'")
        for eid, value in values.items():
            stated = num(t["EST"][eid][case])
            if stated is None or not close(stated, value):
                err(eid, f"{case}: stated {t['EST'][eid][case]} != computed {value:.6g}")
    base_env = {k.replace("-", "_"): num(v["Expected"]) for k, v in t["INP"].items()}
    for output in {r["Output"] for r in t["TN"].values()}:
        swings = {}
        for iid, row in t["INP"].items():
            lo, hi = num(row["Low case"]), num(row["High case"])
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
            if iid not in rows:
                continue
            rid, r = rows[iid]
            rank = 1 + sum(1 for x in swings.values() if x[2] > s * (1 + 1e-9))
            for column, value in (("Output at low", a), ("Output at high", b), ("Swing", s)):
                if not close(num(r[column]), value):
                    err(rid, f"{column} {r[column]} != computed {value:.5g}")
            if int(r["Rank"]) != rank:
                err(rid, f"rank {r['Rank']} != computed {rank}")
    del base_env

    # 5. registers
    for kind in ("CON", "ASM", "DEP", "RSK"):
        for rid, row in t[kind].items():
            if row["Status"] not in ("Active", "Open", "Monitoring", "Closed"):
                err(rid, f"invalid status {row['Status']}")
    for cid, c in t["CON"].items():
        if c["Fixed or negotiable"] not in ("Fixed", "Negotiable"):
            err(cid, "must be Fixed or Negotiable")
    for pid, p in t["PREF"].items():
        if p["Fixed or negotiable"] != "Negotiable":
            err(pid, "a preference must be negotiable")
    for aid, a in t["ASM"].items():
        if a["Confidence"] not in LEVEL or a["Impact if wrong"] not in LEVEL:
            err(aid, "confidence and impact must be Low, Medium or High")
        if a["Owner"] not in t["STK"] or num(a["Validation due (week)"]) is None:
            err(aid, "needs a stakeholder owner and a numeric validation week")
    for did, d in t["DEP"].items():
        if d["Owner"] not in t["STK"] or num(d["Needed by (week)"]) is None:
            err(did, "needs a stakeholder owner and a numeric needed-by week")
    for rid, r in t["RSK"].items():
        p, i = num(r["Probability"]), num(r["Impact"])
        exposure = num(r["Exposure"])
        if not (p in range(1, 6) and i in range(1, 6)) or exposure != p * i:
            err(rid, f"exposure {r['Exposure']} != {r['Probability']} x {r['Impact']}")
            continue
        band = "Lower" if exposure <= 4 else "Moderate" if exposure <= 9 else \
            "High" if exposure <= 14 else "Very high"
        if r["Band"] != band:
            err(rid, f"band {r['Band']} != {band}")
        if r["Owner"] not in t["STK"]:
            err(rid, "needs a stakeholder owner")
        if exposure >= 10:
            for column in ("Response", "Trigger", "Escalation"):
                if r[column].lower() in ("none", "n/a"):
                    err(rid, f"high exposure needs '{column}'")
        if exposure >= 15 and r["Escalation"] not in t["STK"]:
            err(rid, "very high exposure must name an escalation authority")
    for uid, u in t["UNK"].items():
        if u["Blocks"] not in ("Blocks decision", "Manageable gap"):
            err(uid, "invalid 'Blocks' value")
        if u["Owner"] not in t["STK"]:
            err(uid, "needs a stakeholder owner")
    for cfid, c in t["CF"].items():
        if c["Owner"] not in t["STK"]:
            err(cfid, "needs a stakeholder owner")

    # 6. criteria, gates, bands
    for decision in t["DEC"]:
        weights = [num(r["Weight"]) for r in t["CRIT"].values() if r["Decision"] == decision]
        if not close(sum(weights), 1.0, 1e-9):
            err(decision, f"weights sum to {sum(weights):.4f}, not 1")
    engine = Engine(t)
    numeric_criteria = {r["Criterion"] for r in t["AN"].values()}
    for crit, bands in engine.bands.items():
        if crit not in t["CRIT"]:
            err(crit, "bands for an unknown criterion")
            continue
        ordered = sorted(bands, key=lambda b: b[1])
        if sorted(b[0] for b in bands) != [1, 2, 3, 4, 5]:
            err(crit, "bands must cover ratings 1 to 5 once")
        if ordered[0][1] != 0 or ordered[-1][2] != math.inf:
            err(crit, "bands must start at 0 and end at inf")
        for (_, _, hi), (_, lo, _) in zip(ordered, ordered[1:]):
            if lo != hi + 1:
                err(crit, f"gap or overlap between {hi} and {lo}")
    for crit, row in t["CRIT"].items():
        has_bands = crit in numeric_criteria
        judged = any(r["Criterion"] == crit for r in t["JA"].values())
        if has_bands == judged:
            err(crit, "needs exactly one of numeric bands or judgement anchors")
    for gid, g in t["GT"].items():
        if g["Operator"] not in ("<=", ">=", "n/a") or g["Value source"] not in ("TB", "DL", "stated", "n/a"):
            err(gid, "invalid operator or value source")
    for oid, o in t["OPT"].items():
        if o["Decision"] not in t["DEC"] or o["Role"] not in ("Baseline", "Alternative"):
            err(oid, "invalid decision or role")
    for decision in t["DEC"]:
        opts = [r for r in t["OPT"].values() if r["Decision"] == decision]
        if sum(r["Role"] == "Baseline" for r in opts) != 1 or len(opts) < 3:
            err(decision, "needs exactly one baseline and at least three options")
    for tid, row in t["TCO"].items():
        total = sum(num(row[c]) for c in ("Build and migration", "Three-year run and support", "Exit"))
        if num(row["Total"]) != total:
            err(tid, f"total {row['Total']} != {total:g}")

    # 7. gate results, eligibility, option inputs, scores
    for gid, g in t["GT"].items():
        for opt in engine.options(g["Decision"]):
            rows = [r for r in t["GR"].values() if r["Gate"] == gid and r["Option"] == opt]
            if len(rows) != 1:
                err(gid, f"{opt} has {len(rows)} gate results, expected 1")
                continue
            r = rows[0]
            rid = next(k for k, v in t["GR"].items() if v is r)
            if r["Result"] not in ("Pass", "Fail", "Pending"):
                err(rid, f"invalid result {r['Result']}")
            if g["Operator"] == "n/a":
                if r["Value"] != "n/a":
                    err(rid, "a qualitative gate has value n/a")
                continue
            value = engine.gate_value(gid, opt, {})
            stated = num(r["Value"])
            if stated is None or value is None or not close(stated, value, 1e-9):
                err(rid, f"value {r['Value']} != source {value}")
            expected = engine.gate_result(gid, opt, {})
            if r["Result"] != expected:
                err(rid, f"result {r['Result']} != computed {expected}")
    for decision in t["DEC"]:
        eligible = set(engine.eligible(decision, {}))
        scores = engine.scores(decision)
        sc_rows = {r["Option"]: (sid, r) for sid, r in t["SC"].items() if r["Decision"] == decision}
        if set(sc_rows) != set(engine.options(decision)):
            err(decision, "score table must list every option")
        ranked = sorted((round(s, 2) for s in scores.values() if s is not None), reverse=True)
        for option, (sid, r) in sc_rows.items():
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
            frozen = [num(c["Frozen in week"]) for c in t["CRIT"].values()
                      if c["Decision"] == decision]
            if num(r["Scored in week"]) <= max(frozen):
                err(sid, "scored before the criteria were frozen")
        top = sorted(ranked, reverse=True)
        if len(top) > 1 and top[0] - top[1] < CLOSE_CALL:
            state = {a["Decision"]: a["Decision state"] for a in t["ADR"].values()}
            if state.get(decision) == "Final":
                err(decision, "a close call cannot be Final")
    for oid, o in t["OI"].items():
        eligible = engine.eligible(o["Decision"], {})
        if o["Option"] not in eligible:
            err(oid, "inputs belong to eligible options only")
            continue
        if o["Value source"] == "judgement":
            if o["Input value"] != "judgement" or o["Rating"] not in {"1", "2", "3", "4", "5"}:
                err(oid, "a judgement row needs a rating from 1 to 5")
            continue
        value = engine.resolved_input(o, {})
        if value is None or not close(num(o["Input value"]), value):
            err(oid, f"input {o['Input value']} != source {o['Value source']} = {value}")
            continue
        if engine.band(o["Criterion"], value) != int(o["Rating"]):
            err(oid, f"rating {o['Rating']} != band {engine.band(o['Criterion'], value)}")

    # 8. sensitivity
    for sid, s in t["SEN"].items():
        ov = parse_override(s, t)
        scores = engine.scores(s["Decision"], ov)
        winner, top, second = outcome(scores)
        fmt = lambda x: "n/a" if x is None else f"{x:.2f}"
        for column, got in (("Winner", winner), ("Winner score", fmt(top)),
                            ("Runner-up score", fmt(second))):
            if s[column] != got:
                err(sid, f"{column} {s[column]} != computed {got}")

    # 9. ADRs and traceability
    for aid, a in t["ADR"].items():
        if a["Status"] not in STATUS or a["Decision state"] not in ("Conditional", "Final"):
            err(aid, "invalid status or decision state")
        if a["Selected option"] not in engine.options(a["Decision"]):
            err(aid, "selected option does not belong to the decision")
            continue
        contingency = a["Title"].startswith("Contingency")
        scores = engine.scores(a["Decision"])
        if not contingency:
            if scores.get(a["Selected option"]) is None or \
                    round(scores[a["Selected option"]], 2) != max(round(s, 2) for s in scores.values()):
                err(aid, "selected option is not the top-ranked eligible option")
            pending = [g for g in t["GT"] if t["GT"][g]["Decision"] == a["Decision"]
                       and engine.gate_result(g, a["Selected option"], {}) == "Pending"]
            blocking = [u for u, r in t["UNK"].items()
                        if a["Decision"] in r["Decisions affected"] and r["Blocks"] == "Blocks decision"]
            if a["Decision state"] == "Final" and (pending or blocking):
                err(aid, f"cannot be Final with pending gates {pending} or blocking unknowns {blocking}")
        if a["Status"] == "Accepted":
            err(aid, "Accepted needs a recorded approval; none exists in this pack")
    for decision in t["DEC"]:
        if not any(a["Decision"] == decision for a in t["ADR"].values()):
            err(decision, "has no ADR")
    reach = {}
    for trid, tr in t["TR"].items():
        bo = tr["BO"]
        reach[bo] = tr
        for req in refs(tr["REQ"]):
            if t["REQ"][req]["BO"] != bo:
                err(trid, f"{req} belongs to {t['REQ'][req]['BO']}, not {bo}")
        if not refs(tr["ADR"]):
            err(trid, "objective reaches no ADR")
    for bo in t["BO"]:
        if bo not in reach:
            err(bo, "has no traceability row")
    for rid, r in t["REQ"].items():
        if rid not in refs(reach.get(r["BO"], {"REQ": ""})["REQ"]):
            err(rid, "missing from its objective's traceability row")
    seen = " ".join(" ".join(tr[c] for c in ("TGT and EST", "CON, ASM, DEP, RSK, UNK",
                                              "CRIT and GT", "ADR"))
                    for tr in t["TR"].values())
    covered = set(refs(seen))
    for kind in ("TGT", "CON", "ASM", "DEP", "RSK", "UNK", "CRIT", "GT", "ADR"):
        for item in t[kind]:
            if item not in covered:
                err(item, "does not appear in the traceability matrix")
    return errors


# ----------------------------------------------------------------------------- reports
def report(tables):
    t = tables
    engine = Engine(t)
    for case in CASES:
        values, _ = estimates(t, case)
        print(case, {k: float(f"{v:.4g}") for k, v in values.items()})
    for decision in t["DEC"]:
        print(decision, {o: (None if s is None else round(s, 2))
                         for o, s in engine.scores(decision).items()})
    for sid, s in t["SEN"].items():
        scores = engine.scores(s["Decision"], parse_override(s, t))
        print(sid, outcome(scores), {o: None if v is None else round(v, 3) for o, v in scores.items()})
    # flip point of a weight by bisection
    for sid in ("SEN-08", "SEN-14"):
        s = t["SEN"][sid]
        lo, hi = 0.0, 0.99
        base = outcome(engine.scores(s["Decision"]))[0]
        for _ in range(60):
            mid = (lo + hi) / 2
            row = dict(s, Value=str(mid))
            if outcome(engine.scores(s["Decision"], parse_override(row, t)))[0] == base:
                lo = mid
            else:
                hi = mid
        print(f"flip point for {s['Target']} in {s['Decision']}: {hi:.3f}")


def trace(tables, count, seed):
    t = tables
    rng = random.Random(seed)
    for aid in rng.sample(sorted(t["ADR"]), min(count, len(t["ADR"]))):
        rows = [r for r in t["TR"].values() if aid in refs(r["ADR"])]
        for r in rows[:1]:
            print(f"{aid} <- {r['BO']}: {t['BO'][r['BO']]['Business objective'][:60]}... "
                  f"<- {r['REQ'].split(';')[0].strip()} <- {t['REQ'][r['REQ'].split(';')[0].strip()]['Source']}")
    for bo in rng.sample(sorted(t["BO"]), min(count, len(t["BO"]))):
        row = next(r for r in t["TR"].values() if r["BO"] == bo)
        print(f"{bo} -> {row['REQ'].split(';')[0].strip()} -> "
              f"{row['TGT and EST'].split(';')[0].strip()} -> {row['CRIT and GT'].split(';')[0].strip()} "
              f"-> {row['ADR']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--trace", type=int, metavar="N")
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    tables, prose, errors = parse(Path(args.file).read_text(encoding="utf-8"))
    if args.report:
        report(tables)
        return 0
    if args.trace:
        trace(tables, args.trace, args.seed)
        return 0
    errors += check(tables, prose)
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
