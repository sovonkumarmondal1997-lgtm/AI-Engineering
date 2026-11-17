# Project 06 — Cross-System Data Integration Design

> **Stage:** Stage 2D — Data Architecture
> **Module:** 2D.6 — Data Integration and Interoperability
> **Project type:** End-to-end integration architecture design exercise (a traceable, recomputable and partly executable design package; no connector configuration or code)
> **Roadmap source:** `roadmap-Data-Integration-and-Interoperability.md`, Section 7
> **Project file:** `Projects/06-cross-system-data-integration-design.md`

---

## 0. Document control

| Item | Value |
| --- | --- |
| Document | Project specification and worked reference, deliverables D1–D17 |
| Version | 1.1 (post-audit) |
| Date | 2026-10-21 |
| Status | Complete as a project specification and worked reference. **Every Northbridge value is illustrative. No source owner, partner, vendor, stakeholder or independent reviewer has confirmed anything in Section 6. The recommendation is conditional on eight open questions (OQ-01 to OQ-08).** |
| Audience | Learner running the project; independent reviewer auditing it |
| Scenario | *Northbridge Bank*, a fictional mid-sized retail and business bank (roadmap Section 7.2) |
| Evidence rule | Every fact-bearing row carries one of four labels: `Given`, `Assumed`, `Derived`, `Unknown` (Section 4.3) |
| Companion tool | Package checker, calculator and scenario runner, Appendix B (`check_integration_design.py`) |

**Change log**

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-10-21 | First complete design |
| 1.1 | 2026-10-21 | Post-audit (Section 7.7, FND-05 to FND-09): added the expected-volume field the roadmap's flow template requires; added an interface-exists gate so a candidate that needs a capability the source lacks cannot be eligible; corrected a coverage note that claimed another flow's controls caught fraud-store errors and added the weekly sample comparison (REC-23) that does; traced seven requirements to decisions; corrected a recovery-capacity phrase in the recommendation; added a hand-calculation section for reviewers (7.8); ran 60 mutation tests and a prose-versus-table audit; confirmed the embedded checker equals the tested one |

**Deliverable register** (version-dated; requirements precede the comparison, and the criteria were locked between them)

| ID | Deliverable | Section | Version date | Status |
| --- | --- | --- | --- | --- |
| DL-01 | D1 Project scope and assumptions | 6.1 | 2026-10-14 | Complete as an illustrative worked reference |
| DL-02 | D2 Stakeholder and system inventory | 6.2 | 2026-10-14 | Complete as an illustrative worked reference |
| DL-03 | D3 Source and target data inventory | 6.3 | 2026-10-15 | Complete as an illustrative worked reference |
| DL-04 | D4 Integration requirements register | 6.4 | 2026-10-16 | Complete as an illustrative worked reference |
| DL-05 | D5 Workload and freshness requirements | 6.5 | 2026-10-17 | Complete as an illustrative worked reference |
| DL-06 | D6 Integration pattern comparison matrix | 6.6 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-07 | D7 Pattern selection rationale per flow | 6.7 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-08 | D8 Logical integration architecture diagram | 6.8 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-09 | D9 Source-to-target data flow descriptions | 6.9 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-10 | D10 Data contracts and schema compatibility plan | 6.10 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-11 | D11 Idempotency and deduplication strategy | 6.11 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-12 | D12 Reconciliation and data validation plan | 6.12 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-13 | D13 Failure-mode and recovery matrix | 6.13 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-14 | D14 Security and governance considerations | 6.14 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-15 | D15 Operational validation requirements | 6.15 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-16 | D16 Architecture trade-off and risk register | 6.16 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-17 | D17 Final architecture recommendation | 6.17 | 2026-10-21 | Complete as an illustrative worked reference |

**Reading order.** Sections 1–5 explain the project and how to run it. Section 6 is a complete worked reference (D1–D17) whose tables the checker parses, recomputes and, for the idempotency and reconciliation parts, executes. Section 7 is the quality gate. Section 8 holds templates for a real organisation. Sections 9–11 cover pitfalls, hand-off and self-assessment. Appendix B is the checker.

---

## 1. Project overview

### 1.1 What this project is

A **cross-system data integration design** answers, for every flow of data between systems, six questions: *which mechanism moves it, under what contract, in what order and with what consistency, how repetition and failure are made safe, how anyone can prove the target matches the source, and who is told when it does not.* It sits between a business problem ("analytics slow the ledger, fraud sees events late, nobody trusts the numbers") and a build ("this connector, this schedule, this code").

This project produces that design for a fictional bank with four sources (a core ledger database, a cards platform, a SaaS CRM and a payment-network partner) and four consumers (an analytical platform, a fraud service, a contact-centre view and regulatory reporting). It is deliberately an **architecture-level exercise**. It names mechanism categories (log-based change capture, a keyed event stream, an incremental API poll, a manifest-gated file load), never products; it stops before connector configuration, code, infrastructure sizing, cloud mapping (2D.8), stream-processing design (2D.9) or platform build (2D.7).

What makes it more than a diagram is that large parts of the design are **recomputable and executable**. Extract times, API request counts, retry budgets, partition counts and retention, backlog catch-up, freshness and availability budgets, and federated-lookup load are written as numbers in Markdown tables and recomputed by a stdlib Python checker (Appendix B). The idempotent merge rules are run on small event sequences, including a replay, a duplicate and an out-of-order update. The reconciliation levels are run on injected defects. Contract changes are classified by rule, including a change that is structurally valid and semantically wrong. The candidate comparison is re-scored under five weight sets. A candidate that needs a source capability the source does not offer cannot be eligible.

```text
Scenario ─► systems, source capabilities, data assets ─► requirements and constraints ─► workload and freshness arithmetic
   ─► gates and criteria (locked) ─► candidates scored per flow ─► patterns selected, transformation location decided
   ─► mappings, ordering, late data ─► contracts and compatibility ─► identity, dedup, merge rules
   ─► reconciliation levels and coverage ─► failure modes, recovery, replay ─► security, monitoring, drills
   ─► walkthroughs (normal and failure) ─► risks, trade-offs, ADRs ─► recommendation and open items
```

### 1.2 Why organisations need it

| Situation | What goes wrong without a design | What this project provides |
| --- | --- | --- |
| Nightly full copies of a core database | The source is strained, the window is overrun, history is re-copied every night | Extract-time arithmetic against the window, and a change-based pattern chosen against the source's actual capabilities |
| A consumer needs data in seconds, the feed delivers it in hours | Decisions are made on stale data and nobody can say how stale | A freshness budget by stage with headroom, and a stream or poll pattern chosen to meet it |
| Producers change fields without telling anyone | Consumers break, or worse, silently compute wrong numbers | Contracts with owners, compatibility modes chosen from upgrade order, and a semantic-change gate that a registry cannot provide |
| Jobs restart and repeat | Duplicates and stale overwrites | Identity, version-guarded merges and deduplication windows at least as long as the replay horizon |
| "The row counts match" | Swapped accounts, drifted values and offsetting errors pass | Multi-level reconciliation, a matrix of what each level misses, and injection tests that prove it |
| Failure is handled when it happens | Each outage is a new incident | A failure matrix covering every component, backlog arithmetic, drills with pass criteria |

### 1.3 Business and architecture objectives

1. Meet each consumer's freshness target without straining any source.
2. Make every flow safe to retry, replay and restart: no loss, no duplication, no stale overwrite.
3. Make change safe: owned contracts, a stated compatibility mode, 30 days' notice for breaking changes, a semantic review where a registry cannot see.
4. Prove completeness and correctness with reconciliation whose blind spots are written down.
5. Make failure boring: detection, recovery, owners and drills for every component.
6. Carry classification, residency and lineage through every store, including landing and dead-letter.
7. Leave a trail a reviewer can follow in both directions, from requirement to decision and back.

### 1.4 What this project is not

- Not a product comparison, a connector tutorial or a pipeline implementation.
- Not a stream-processing design (2D.9), a platform build (2D.7) or a cloud mapping (2D.8).
- Not a production deployment. It must not be extended into one.
- Not evidence about any real bank. All scenario numbers are illustrative.

### 1.5 Success criteria

| Criterion | Evidence |
| --- | --- |
| Every flow has measurable freshness, throughput and correctness requirements; no requirement names a product | Section 6.4; checker refuses product names |
| Every decision has at least three eligible candidates including a simplest baseline, criteria locked first, gate failures recorded, and source capabilities cited | Section 6.6; checker verifies counts, weights, dates and capability links |
| Every contract covers structure, semantics, quality, delivery, ownership and a compatibility mode; a semantic break is handled | Section 6.10 |
| Every flow has identity, an idempotent rule, deduplication and reconciliation, with a coverage matrix that names undetected classes | Sections 6.11 and 6.12; scenarios and injections are executed |
| Every component has a failure scenario; at least ten overall; catch-up arithmetic checked | Section 6.13 |
| At least five normal and eight failure walkthroughs, including duplicate, out-of-order, replay, schema change, source outage and incomplete file | Section 6.17 |
| Each alert has an owner and an action; absence and staleness are monitored; a drill has pass criteria | Section 6.15 |
| An independent reviewer agrees the evidence supports the conclusions | **Not met by design** in the worked reference (VAL-12) |

---

## 2. How to use this file

| Mode | Purpose | What you do |
| --- | --- | --- |
| **A. Worked reference** | Learn the method by reading and re-running a complete example | Read Section 6 in order; run the checker; change one assumption (a standard, a rate, a window, a capability status) and watch derived cells and decisions respond; edit a scenario's rule and watch the outcome change; try to break a rule and read the error |
| **B. Real organisation** | Apply the method to your own estate | Copy the table headers from Section 8, fill them from your own systems and source documentation, replace every illustrative figure with measured or sourced values, mark every unverified source capability `Unknown` with an open question, run the checker and give the result to an independent reviewer |

**Rules for either mode.**

1. Keep the column headers exactly; the checker identifies tables by their header row.
2. A derived cell is written `~` when authoring. `python3 check_integration_design.py FILE --fill` replaces each `~` with the recomputed value; the plain check recomputes everything again and reports any mismatch.
3. Never write a source capability as `Yes` because it would be convenient. If it is not documented or tested, it is `Unknown`, and a candidate that needs it makes its decision conditional.
4. Do not edit scores after seeing the winner. If a score is wrong, record why and re-run the sensitivity test.
5. Keep the scope: when a decision needs a product, a price or a benchmark, write an open question for the later module.

---

## 3. Concepts applied

### 3.1 Topic-to-project mapping

| Module topic | What it teaches | Where this project uses it |
| --- | --- | --- |
| 1 Batch ETL/ELT and incremental ingestion | Full versus incremental, change markers, watermarks, lookback, deletes, atomic publication, ELT versus ETL | EXT worksheet, DEC-01 and DEC-05, DEC-07, ORD (lookback, atomic publication), SCN-13 and SCN-14 |
| 2 Change data capture and replication | Log-based versus query-based capture, snapshot-plus-stream seam, checkpoints, lag, retention expiry | DEC-01, CAP-02 to CAP-05, LAG-03 and LAG-04, FMX-01, DRL-01 |
| 3 APIs, files and managed connectors | Pagination, rate limits, retries, quotas, manifests, incomplete files, what a connector manages | API and RTY worksheets, DEC-04 to DEC-06, FMX-09 to FMX-12, SCN-09 to SCN-12 |
| 4 Streaming events and message contracts | Envelope, keys and partitions, ordering scope, retention and replay, poison messages, lag | STM and LAG worksheets, DEC-02 and DEC-03, CTR-02, ORD-02, FMX-13 |
| 5 Data contracts, registry, compatibility | Producer-owned contracts, backward/forward/full modes, semantic compatibility, expand-and-contract | CTR and CHG tables, the semantic-change gate, SEC-10 |
| 6 Virtualisation, federation, sharing | Source load and availability of live access, when materialisation is required | FED and AVC worksheets, CAN-20 against CAN-19, TRD-03 |
| 7 Idempotency, deduplication, reconciliation | Identity, version guards, dedup windows, reconciliation levels, independence, defect-to-control matrix | IDM, SCN, REC, DET, COV, INJ |
| 8 Pattern selection and failure handling | Requirements-to-pattern decisions, failure boundaries, backoff, replay, catch-up, monitoring, failure matrix | Section 6.6 to 6.7, FMX, OPS, DRL, WLK |

### 3.2 Practice-question arithmetic reused

The module's quantitative toolkit (roadmap Section 3.5) is the calculator:

| Formula | Project table |
| --- | --- |
| `extract_time = bytes ÷ throughput` | EXT |
| `changed_volume = rows × change fraction × row size` | WLD (CRM daily change) |
| `api_calls = ceil(records ÷ page_size)`; `api_duration = calls ÷ rate` | API |
| `retry_wait_total = Σ base × factor^i` | RTY |
| `backlog_growth = arrival − processing`; `catch_up = backlog ÷ (capacity − arrival)` | LAG |
| `partitions = ceil(peak ÷ per-partition) × headroom` | STM |
| `replay_retention = rate × size × days × replication` | STM |
| `chain_availability = A1 × A2 × … × An` | AVC |
| `reconciliation_delta = source total − target total` | INJ, REC |

The practice questions' calculation items map to the same tables: T1-Q4 to EXT, T2-Q4 to LAG, T3-Q4 to API and RTY, T4-Q4 to STM, T6-Q4 to AVC and FED, T7-Q4 to the INJ and REC tables, T8-Q3 to LAG and RTY. The code-reading item T7-Q3 is the version-guarded merge that the SCN scenarios execute.

### 3.3 Carry-in from earlier projects

| Earlier project | What this project takes from it |
| --- | --- |
| 01 Current-state inventory | The idea of an inventory with owners and an evidence label per row; the system and asset inventories follow it |
| 02 Requirements and decision pack | Measurable requirements and the requirement/constraint/assumption classification; the ADR structure with rejected options and revisit triggers |
| 03 Pattern comparison | Comparing every option against a baseline |
| 04 Logical data model | The entities behind the assets (ledger entries, accounts, customers) and the identifier rules from which each contract's key should come in a real engagement |
| 05 Storage selection | The ledger scale (8 TB, carried in as ASM-01), the landing and curated zones, the retention of raw data and the system-of-record rules this project depends on |

None of these is needed to run this file; each is cited so a real engagement can connect its own earlier outputs.

---

## 4. Project governance and conventions

### 4.1 Roles and decision rights (RACI)

R = does the work, A = accountable, C = consulted, I = informed.

| Activity | Architect (STK-12) | Sponsor (STK-01) | Source owners (STK-02 to 05) | Consumer owners (STK-06 to 09) | Security and Privacy (STK-10) | Integration Operations (STK-11) | Compliance and Audit (STK-14) | Reviewer (STK-13) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Scope and assumptions | R | A | C | C | C | C | C | I |
| Source capabilities | R | I | A | I | C | C | I | I |
| Requirements | R | A | C | A for own flow | C | C | C | I |
| Estimates | R | I | C | C | I | C | I | C |
| Criteria, gates and scoring | R | C | C | C | C | C | C | A for independence |
| Pattern selection and ADRs | R | A | C | C | C | C | C | C |
| Contracts and change control | R | I | A (producer) | C | C | C | C | C |
| Idempotency and reconciliation | R | I | C | C | C | C | A | C |
| Failure matrix and drills | R | I | C | C | C | A | C | C |
| Risk acceptance | R | A | C | C | C | C | C | I |
| Independent review | I | I | I | I | I | I | I | R and A |

### 4.2 Status, severity and notation

| Item | Values |
| --- | --- |
| Source capability status | Yes (documented or tested), No (documented absent), Unknown (an open question exists) |
| Open question status | Open, Closed |
| Risk rating | Score = likelihood × impact (each 1–5); High ≥ 15, Medium ≥ 8, Low otherwise |
| Finding severity | Blocking (stops use), Major (changes a decision or hides a gap), Minor (wording or evidence) |
| Walkthrough outcome | Pass, Pass with residual risk, Fail |
| Candidate gate result | `GT-nn:P` (passed) or `GT-nn:F` (failed) |
| Compatibility mode | BACKWARD, FORWARD, FULL, each optionally TRANSITIVE, or NONE |
| Units | Decimal: 1 GB = 10⁹ bytes, 1 TB = 1,000 GB = 10⁶ MB; 1 day = 86,400 s; money in integer minor units |

### 4.3 Evidence labels

| Label | Meaning |
| --- | --- |
| Given | Stated by the roadmap scenario (or, in Mode B, observed in the real organisation) |
| Assumed | Chosen by the author and registered; includes planning ranges and judgement scores |
| Derived | Computed from other cells by the checker |
| Unknown | Not known; an open question exists and nothing is built on it |

### 4.4 ID conventions

| Prefix | Meaning | Prefix | Meaning |
| --- | --- | --- | --- |
| STK | Stakeholder role | CTR, CHG | Contract, contract change |
| SYS | System | MAP | Mapping |
| CAP | Source capability | IDM | Identity and merge rule |
| AST | Data asset | SCN | State scenario |
| WLD | Workload line | REC, DET, COV, INJ | Reconciliation control, defect class, coverage line, injection test |
| REQ, CON, ASM, DEP | Requirement, constraint, assumption, dependency | ORD | Ordering line |
| STD | Standard | CMP, FMX | Component, failure mode |
| EXT, API, RTY | Batch, API and retry worksheets | OPS, DRL | Alert, drill |
| STM, LAG | Stream sizing, backlog | STR, SEC | Store or zone, security control |
| LAT, BUD | Latency component, budget path | WLK | Walkthrough |
| AVC, FED | Availability chain, federation load | RSK, TRD, OQ | Risk, trade-off, open question |
| GT, CRT, WS | Gate, criterion, weight set | VAL, FND, CH | Gate item, finding, challenge |
| DEC, CAN | Decision, candidate | DL, CNT, ADR | Deliverable, package count, decision record |
| FLW | Flow | | |

### 4.5 Confidentiality and handling

In Mode B the package describes real data volumes, source weaknesses and security controls. Treat it as confidential: store it in the architecture workspace, restrict edit rights to the author, and never paste real customer identifiers into sample rows. The worked reference contains none.

### 4.6 Suggested workspace layout (Mode B, optional)

```text
integration-design/
├── 06-cross-system-data-integration-design.md   # this package, tables filled in
├── check_integration_design.py                  # Appendix B
├── evidence/                                    # source documentation, rate exports, sandbox test results, partner correspondence
├── reviews/                                     # reviewer notes and signed gate items
└── adr/                                         # one record per decision, if kept separately
```

---

## 5. Execution plan

### 5.1 Timeline and effort (planning estimate, mid-sized organisation)

| Week | Steps | Output | Person-days |
| --- | --- | --- | --- |
| 1 | 1–4 | Scope, stakeholders, data inventory, source capability profile | 6–8 |
| 2 | 5–6 | Requirements register, workload and freshness arithmetic | 6–8 |
| 3 | 7–9 | Candidates, comparison, selection | 6–8 |
| 4 | 10–12 | Mappings, contracts, identity, deduplication, reconciliation | 8–11 |
| 5 | 13–16 | Failure matrix, ordering and consistency notes, security, monitoring | 7–9 |
| 6 | 17–19 | Logical architecture, walkthroughs, risks and trade-offs, ADRs | 5–7 |
| 7 | 20 and review | Final recommendation, independent review, challenge round | 3–5 |
| | | **Total** | **41–56** |

These are planning estimates for a team that already has source documentation; obtaining answers to the unknown source capabilities (partner, vendor, source owners) often sets the critical path rather than the design work.

### 5.2 Definitions of ready and done

- **Ready for a step:** its inputs exist, are labelled, and have owners.
- **Done for a step:** its output rows are filled, every derived cell is recomputed by the checker, and its validation row below passes.
- **Done for the project:** the completion gate in Section 7.5, with the independent-review item signed by a person who did not write the package.

### 5.3 The twenty steps

Each step has the roadmap's six elements plus the practitioner guidance that keeps the step honest.

**Step 1 — Define the problem, scope and outcomes** (D1)
- *Purpose:* fix what is decided and what is not.
- *Inputs:* the scenario or the sponsor's request.
- *Actions:* write the problem statement in business terms; list objectives and exclusions (product choice, connector configuration, code, sizing, cloud mapping, stream-processing design, platform build, metadata tooling); list labelled assumptions.
- *Questions to answer:* what will the sponsor decide from this package, and what is explicitly not decided?
- *Outputs:* scope and assumptions (6.1).
- *Validation:* a sponsor-role reviewer confirms scope and exclusions. State exclusions firmly; a design that drifts into configuration never finishes.

**Step 2 — Identify systems, stakeholders and consumers** (D2)
- *Purpose:* make every end of every flow accountable to a person.
- *Inputs:* scenario, organisation chart.
- *Actions:* register sources, targets, owners and consumers by role; include security, compliance and operations.
- *Questions:* who owns each system, who consumes each feed, who runs it, who can accept a risk?
- *Outputs:* system and stakeholder inventory (6.2).
- *Validation:* every flow end has an owner or the word `Unknown` with an open question.

**Step 3 — Inventory datasets, entities and events** (D3)
- *Purpose:* know what moves, and how a record is identified.
- *Inputs:* step 2 and the logical models of 2D.4.
- *Actions:* list assets with key, grain, sensitivity and owner.
- *Questions:* what identifies each record, and where does it come from?
- *Outputs:* source and target data inventory (6.3).
- *Validation:* each asset has a key, a system and a workload line. Identity of records is a design input, not an afterthought.

**Step 4 — Characterise source capabilities and constraints** (D2)
- *Purpose:* find what each source can support and at what load.
- *Inputs:* step 2, source documentation, source owners.
- *Actions:* record interfaces, change visibility, delete visibility, ordering, retention, limits and windows as capabilities with a status.
- *Questions:* what can the source do, who said so, and what is merely hoped?
- *Outputs:* source capability profile (6.2).
- *Validation:* each capability is `Yes`, `No` or `Unknown`; each `Unknown` has an open question. Do not invent source capabilities.

**Step 5 — Gather integration requirements** (D4)
- *Purpose:* state what each consumer must receive, how fast and how correctly.
- *Inputs:* steps 1–3.
- *Actions:* write measurable requirements (metric, target, method, source, priority); classify constraints, assumptions and dependencies with the 2D.2 tests.
- *Questions:* what is the percentile, the window, the tolerance, and how is it measured?
- *Outputs:* integration requirements register (6.4).
- *Validation:* each requirement is testable and sourced; no requirement names a product.

**Step 6 — Define volume, freshness, latency, throughput and availability** (D5)
- *Purpose:* quantify demand and test feasibility.
- *Inputs:* steps 3–5.
- *Actions:* apply the toolkit formulas with units and ranges: extract time, API pacing, retry budget, partitions and retention, backlog catch-up, freshness and availability budgets.
- *Questions:* which input dominates, and does the baseline already fail?
- *Outputs:* workload and freshness requirements (6.5).
- *Validation:* each figure has unit, formula and assumption; a chosen design passes and a rejected alternative fails.

**Step 7 — Identify candidate patterns per flow** (D6)
- *Purpose:* shortlist feasible options per flow.
- *Inputs:* steps 4–6.
- *Actions:* define gates from hard constraints; list at least three feasible candidates per decision plus the simplest adequate baseline; record the source capabilities each candidate requires.
- *Questions:* is each candidate feasible given what the source actually offers?
- *Outputs:* candidate list (6.6).
- *Validation:* gate failures are removed from scoring with reasons; a candidate that needs a capability the source lacks fails the interface gate.

**Step 8 — Compare patterns** (D6)
- *Purpose:* compare transparently.
- *Inputs:* steps 5–7.
- *Actions:* lock criteria and weights with a date before scoring; score eligible candidates 1–5; test the winner under alternative weight sets.
- *Questions:* where is the evidence weakest?
- *Outputs:* pattern comparison matrix (6.6).
- *Validation:* the same criteria for every candidate; criteria locked before the matrix date; weight-sensitive decisions are flagged.

**Step 9 — Select and justify the pattern per flow** (D7)
- *Purpose:* decide and record what is being accepted.
- *Inputs:* step 8.
- *Actions:* take the top-ranked eligible candidate; record the runner-up; make the decision conditional where it depends on an unknown capability or a weight-sensitive result.
- *Questions:* what are we accepting, and what would change the choice?
- *Outputs:* pattern selection rationale (6.7).
- *Validation:* each choice cites criteria and evidence; the selected candidate is rank 1 at the locked weights. Give specific rejection reasons; "too complex" is not a reason.

**Step 10 — Define mappings and transformation responsibility** (D9)
- *Purpose:* decide where each transformation happens and who owns it.
- *Inputs:* steps 3 and 9.
- *Actions:* write source-to-target mappings; decide ETL versus ELT; assign an owner to each transformation.
- *Questions:* who owns each transformation, and can a load be re-derived from the raw input?
- *Outputs:* mappings and flow descriptions (6.9).
- *Validation:* every contract field has a source or a rule; every mapping has an owner.

**Step 11 — Define data contracts and schemas** (D10)
- *Purpose:* make change controlled.
- *Inputs:* steps 9–10, topic 5.
- *Actions:* write a contract per feed (structure, semantics, quality, delivery, owner, compatibility mode, notice); classify sample changes, including a semantic one; define enforcement points.
- *Questions:* who may change what, with what notice, and what does a registry not catch?
- *Outputs:* data contracts and compatibility plan (6.10).
- *Validation:* semantics (units, null meaning) and ownership are present; the mode follows from upgrade order and replay; a structurally valid semantic break is identified and routed to a new version. Contracts include meaning, not only fields.

**Step 12 — Specify idempotency, deduplication and reconciliation** (D11, D12)
- *Purpose:* make repetition safe and prove completeness and correctness.
- *Inputs:* steps 3, 9, 11, topic 7.
- *Actions:* define identity, version rule, dedup scope and window, merge rule and side-effect handling; define reconciliation levels, grain, window, tolerance and independence; build the coverage matrix.
- *Questions:* what proves completeness and correctness, and what does each control not catch?
- *Outputs:* idempotency and deduplication strategy; reconciliation plan (6.11, 6.12).
- *Validation:* each flow has an identity, an idempotent rule and reconciliation; scenarios and injected defects are executed; the coverage matrix names the undetected classes and their compensating notes.

**Step 13 — Identify failure modes; define retries, checkpoints, replay and recovery** (D13)
- *Purpose:* define behaviour under failure before it happens.
- *Inputs:* steps 9–12, topic 8.
- *Actions:* list every component, including the scheduler, credentials and registry; for each failure scenario write detection, data impact, recovery, idempotency and reconciliation needs, owner and validation evidence; check recovery capacity with catch-up arithmetic.
- *Questions:* how is each failure detected and recovered, and who is responsible?
- *Outputs:* failure-mode and recovery matrix (6.13).
- *Validation:* every component has at least one scenario; at least ten overall; one backlog scenario has capacity arithmetic.

**Step 14 — Document ordering, consistency, late data and partial failure** (D9)
- *Purpose:* separate transport guarantees from business correctness.
- *Inputs:* steps 9, 12, 13.
- *Actions:* state ordering scope, lateness policy and atomic publication per flow; mark each guarantee documented, assumed or unknown.
- *Questions:* what can a consumer observe mid-failure?
- *Outputs:* consistency notes (6.9).
- *Validation:* each guarantee is marked; an unknown guarantee points at its open question.

**Step 15 — Define security, access and governance** (D14)
- *Purpose:* control who can reach what and prove it.
- *Inputs:* steps 9–11.
- *Actions:* define credentials, encryption, classification, residency, retention, lineage and audit; describe each store and zone, including landing and dead-letter.
- *Questions:* who can access what, and how is it audited?
- *Outputs:* security and governance considerations (6.14).
- *Validation:* each control traces to a requirement; no sensitive data is left unclassified in landing or dead-letter stores.

**Step 16 — Define operational validation, monitoring and alerting** (D15)
- *Purpose:* know before the consumer notices.
- *Inputs:* steps 13–14.
- *Actions:* define freshness, volume, lag, error, absence and reconciliation signals with thresholds, owners and actions; define failure drills with pass criteria.
- *Questions:* what tells us a flow has stopped, not only that it has failed?
- *Outputs:* operational validation requirements (6.15).
- *Validation:* each alert has an owner and an action; every flow has freshness, absence and reconciliation alerts.

**Step 17 — Create the logical architecture and data flow views** (D8, D9)
- *Purpose:* communicate the design.
- *Inputs:* steps 9–16.
- *Actions:* draw the logical view with a legend and version; write a per-flow description.
- *Questions:* is every element justified?
- *Outputs:* logical integration architecture (6.8, 6.9).
- *Validation:* no unexplained element; every system and flow appears in the diagram. Label the view's level (logical, not physical).

**Step 18 — Validate against normal and failure scenarios** (D17)
- *Purpose:* check that the design behaves as claimed.
- *Inputs:* step 17.
- *Actions:* walk at least five normal and eight failure scenarios, including a replay, a duplicate delivery, an out-of-order update, a schema change, a source outage and an incomplete file.
- *Questions:* does the design behave as claimed, and what residual risk remains?
- *Outputs:* validation results (6.17).
- *Validation:* each outcome is explained and cites evidence rows; no `Pass` where a cited calculation fails.

**Step 19 — Document trade-offs, assumptions, questions and rejected alternatives** (D16)
- *Purpose:* keep the limits honest.
- *Inputs:* steps 8–18.
- *Actions:* write the risk and trade-off register and the open questions with owners and triggers; write one ADR per decision.
- *Questions:* what would change the design?
- *Outputs:* trade-off and risk register (6.16, 6.17).
- *Validation:* each item links to a decision; each assumption has an owner and a way to be validated.

**Step 20 — Produce the final recommendation** (D17)
- *Purpose:* give the sponsor something to decide on.
- *Inputs:* all.
- *Actions:* assemble; summarise decisions, correctness claims, trade-offs, conditional items and next steps in one to two pages.
- *Questions:* what is decided and what remains open?
- *Outputs:* final architecture recommendation (6.17).
- *Validation:* a non-specialist can follow it in ten minutes; conditional decisions say what evidence would settle them.

---

## 6. Worked reference — Northbridge Bank

Everything in this section is an illustrative assumption or a derived figure. Tables whose first header cell is `ID` are read by the checker; a `~` is a derived cell the checker fills and verifies. The sequence follows the deliverables D1–D17.

### 6.1 D1 — Project scope and assumptions (Step 1)

**Problem statement.** Northbridge Bank's integrations have grown ad hoc. Nightly full copies strain the ledger, the fraud service sees card events hours late, schema changes break consumers without warning, duplicates appear after job restarts, and nobody can prove that source and target agree.

**Objective.** Produce a defensible cross-system integration design: a pattern per flow chosen against explicit requirements and source capabilities; contracts with owners and compatibility rules; stated ordering, consistency and late-data behaviour; idempotency, deduplication and reconciliation with their blind spots; failure, recovery and replay behaviour; security and governance; and operational validation. The design stops at the architecture level.

| Boundary | In scope | Out of scope (owner) |
| --- | --- | --- |
| Flows | S1 to T1, S2 to T2 and T1, S3 to T3 and T1, S4 to T1 and T4 | Any other source or consumer |
| Decisions | Pattern per flow, transformation location, contracts, correctness and recovery design, monitoring requirements | Product selection, connector configuration, code |
| Sizing | Arithmetic that tests feasibility against stated limits | Infrastructure sizing and capacity purchase (2D.8, 2D.13) |
| Streaming | Event contract, key, partition and retention requirements | Stream-processing design, state and delivery semantics in depth (2D.9) |
| Platform | Landing, quarantine and enforcement points the platform must provide | Platform build, tenancy, service model (2D.7) |
| Governance | Controls, classification carried with data, lineage points | Catalogue tooling, entity resolution, master data (2D.10, 2D.11) |

**Labelled assumptions.** Every number is illustrative. Evidence labels: `Given` (stated by the roadmap scenario), `Assumed` (chosen here and registered as an ASM row), `Derived` (computed by the checker), `Unknown` (not known; an open question exists). A source capability that is `Unknown` is never assumed to exist.

### 6.2 D2 — Stakeholder and system inventory (Steps 2 and 4)

| ID | Stakeholder role | Interest | Decision rights | Flows | Evidence |
| --- | --- | --- | --- | --- | --- |
| STK-01 | Chief Data Officer | Sponsor; accepts residual risk | Approves the recommendation and risk acceptance | all | Assumed |
| STK-02 | Head of Core Banking Platform | Owns the core ledger database (S1) | Approves any load on S1 and access to its log | FLW-01 | Assumed |
| STK-03 | Head of Cards Platform | Owns the cards platform (S2) | Owns the card event contract | FLW-02, FLW-03 | Assumed |
| STK-04 | Head of Customer Relationship Systems | Owns the CRM relationship (S3) | Owns the CRM contracts and vendor liaison | FLW-04, FLW-05 | Assumed |
| STK-05 | Head of Payments Partner Operations | Owns the partner relationship (S4) | Owns the settlement file contract | FLW-06 | Assumed |
| STK-06 | Head of Analytics Platform | Owns the analytical platform (T1) | Owns landing, curated layers and ELT logic | FLW-01, FLW-03, FLW-05, FLW-06 | Assumed |
| STK-07 | Head of Fraud Operations | Owns the fraud service (T2) | Owns fraud freshness and ordering needs | FLW-02 | Assumed |
| STK-08 | Head of Contact Centre | Owns the contact-centre view (T3) | Owns staleness tolerance for the view | FLW-04 | Assumed |
| STK-09 | Head of Regulatory Reporting | Owns regulatory reporting (T4) | Owns evidence requirements | FLW-06 | Assumed |
| STK-10 | Security and Privacy Officer | Credentials, encryption, residency, classification | Approves security controls and retention of raw copies | all | Assumed |
| STK-11 | Integration Operations Lead | Runs the flows and the on-call route | Approves operability and alert design | all | Assumed |
| STK-12 | Enterprise Data Architect | Author of this package | Recommends; owns the ADRs | all | Assumed |
| STK-13 | Independent Architecture Reviewer | Challenges evidence and conclusions | Agrees or rejects the evidence | all | Assumed |
| STK-14 | Compliance and Internal Audit Lead | Owns reconciliation evidence | Approves reconciliation design and exception handling | all | Assumed |

| ID | System | Role | Business purpose | Owner | Interfaces | Constraints | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SYS-01 | S1 Core ledger database | Source | Authoritative ledger entries and account changes | STK-02 | Read replica; readable transaction log | No reliable last-modified on all tables; peak about 2,000 changes per second | Given |
| SYS-02 | S2 Cards platform | Source | Card authorisation events | STK-03 | Event publication; REST API for corrections | About 20,000 authorisation events per second at peak | Given |
| SYS-03 | S3 SaaS customer-relationship system | Source | Customer profile and interaction records | STK-04 | Paginated REST API; weekly bulk export | 10 requests per second; a daily quota of unknown size; about 12 million records | Given |
| SYS-04 | S4 Payment-network partner | Source | Settlement of card payments | STK-05 | Daily file drop with manifest | Files arrive once a day; about 2,000,000 records and 2 GB per day | Given |
| SYS-05 | T1 Analytical platform | Target | Risk, finance and regulatory analytics | STK-06 | Landing zone; curated tables | Complete reconciled history; hourly and daily freshness | Given |
| SYS-06 | T2 Fraud service | Target | Real-time fraud decisions | STK-07 | Event consumer | p95 within 60 s; ordered per card | Given |
| SYS-07 | T3 Contact-centre customer view | Target | Current customer view for agents | STK-08 | Read store | Minutes of staleness acceptable | Given |
| SYS-08 | T4 Regulatory reporting | Target | Reconciled regulatory reports | STK-09 | Report inputs from T1; evidence reports | Reconciled to source; evidence retained | Given |

**Source capability profile.** Each capability is `Yes`, `No` or `Unknown`. An `Unknown` capability must be named by an open question and may not be relied on silently.

| ID | Capability | System | Status | Limit | Evidence |
| --- | --- | --- | --- | --- | --- |
| CAP-01 | Read replica available for extraction | SYS-01 | Yes | Sustained extract assumed 200 MB/s (ASM-04) | Given |
| CAP-02 | Transaction log readable by a capture process | SYS-01 | Yes | Peak 2,000 changes per second | Given |
| CAP-03 | Reliable last-modified column on all tables | SYS-01 | No | Some tables have none | Given |
| CAP-04 | Log retained long enough to recover a stalled reader | SYS-01 | Unknown | Retention period not stated | Unknown |
| CAP-05 | Peak change rate of 2,000 per second | SYS-01 | Yes | Used for lag arithmetic | Given |
| CAP-06 | Event publication | SYS-02 | Yes | About 20,000 events per second at peak | Given |
| CAP-07 | Events published in order per card | SYS-02 | Unknown | Ordering guarantee not stated | Unknown |
| CAP-08 | REST API for corrections | SYS-02 | Yes | Low volume | Given |
| CAP-09 | Paginated REST API | SYS-03 | Yes | 10 requests per second | Given |
| CAP-10 | Daily request quota | SYS-03 | Unknown | Size not stated | Unknown |
| CAP-11 | Modified-since filter on the API | SYS-03 | Unknown | Not stated | Unknown |
| CAP-12 | Weekly bulk export | SYS-03 | Yes | Full snapshot | Given |
| CAP-13 | Deleted records visible through the API | SYS-03 | Unknown | Not stated | Unknown |
| CAP-14 | Daily file drop with manifest | SYS-04 | Yes | Once a day | Given |
| CAP-15 | Manifest carries record count and checksum | SYS-04 | Unknown | Manifest content not stated | Unknown |
| CAP-16 | Partner can resend a file on request | SYS-04 | Unknown | Not stated | Unknown |
| CAP-17 | Outbound change notification from the CRM | SYS-03 | Unknown | Not stated | Unknown |
| CAP-18 | Record-level API for settlement data | SYS-04 | No | File drop only | Given |

### 6.3 D3 — Source and target data inventory and workload (Steps 3 and 6)

| ID | Asset | System | Key | Grain | Sensitivity | Owner | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AST-01 | Ledger entries and account changes | SYS-01 | entry_id | One row per change to a ledger entry | Financial | STK-02 | Given |
| AST-02 | Card authorisation events | SYS-02 | event_id, card_id | One event per authorisation action | Financial | STK-03 | Given |
| AST-03 | Customer profile and interaction records | SYS-03 | customer_id, interaction_id | One row per customer or per interaction | Personal | STK-04 | Given |
| AST-04 | Settlement records | SYS-04 | settlement_id | One record per settled payment | Financial | STK-05 | Given |

**Workload.** Decimal units; one day is 86,400 s. `~` marks a derived cell.

| ID | Workload line | Asset | Total records | Daily records | Record bytes | Peak per s | Avg per s | Peak factor | Daily GB | Total GB | Peak MB/s | Growth per yr | Horizon yr | Horizon GB per day | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WLD-01 | Ledger changes | AST-01 | 40000000000 | 5000000 | 200 | 2000 | 57.87 | 34.56 | 1.00 | 8,000.00 | 0.40 | 0.20 | 3 | 1.73 | Assumed |
| WLD-02 | Card events at the peak-rate profile | AST-02 | n/a | 1000000000 | 1000 | 20000 | 11,574.07 | 1.73 | 1,000.00 | n/a | 20.00 | 0.20 | 3 | 1,728.00 | Assumed |
| WLD-03 | CRM records, 3% changing per month | AST-03 | 12000000 | 12000 | 2000 | n/a | 0.14 | n/a | 0.02 | 24.00 | n/a | 0.20 | 3 | 0.04 | Assumed |
| WLD-04 | Settlement records | AST-04 | n/a | 2000000 | 1000 | n/a | 23.15 | n/a | 2.00 | n/a | n/a | 0.20 | 3 | 3.46 | Assumed |

Reading the table: the ledger totals 8 TB at 200 bytes a row (ASM-01, carried in from module 2D.5) and changes by about 5 million rows a day, so the daily change is 1 GB against an 8,000 GB base: moving only the change is roughly 8,000 times smaller than copying the table. Card events average 11,574 per second against a 20,000 per second peak, a peak factor of about 1.7; the 1 TB per day is the scenario's peak-rate profile, so event size is an assumption (1 KB, ASM-02). The CRM changes by 12 million × 3% ÷ 30 days = 12,000 records a day. Settlement is 2 GB a day (1,000 bytes a record, ASM-06).

### 6.4 D4 — Integration requirements register (Step 5)

The 2D.2 tests decide the type. A **requirement** is a measurable outcome someone owns and no requirement names a product. A **constraint** is fixed by an authority. An **assumption** might be wrong and names how it will be validated. A **dependency** is owed by another module or team.

| ID | Statement | Type | Flow | Metric | Target | Method | Source | Priority | Validated by | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-01 | Card events reach the fraud service quickly | Requirement | FLW-02 | End-to-end event availability at p95 | 60 s or less | Publish timestamp against fraud-store write time, 5-minute windows | Scenario | Must | BUD-01 | Given |
| REQ-02 | Card events for one card are applied in order | Requirement | FLW-02 | Out-of-order applications per card | 0 | Producer sequence check plus version-guarded apply | Scenario | Must | SCN-03 | Given |
| REQ-03 | Ledger changes arrive with no loss and no duplication | Requirement | FLW-01 | Daily control-total delta by business date, currency and entry type | Zero tolerance | Source-side control report against target | Scenario | Must | INJ-04 | Given |
| REQ-04 | Operational dashboards see ledger changes within the hour | Requirement | FLW-01 | Landing-to-curated age at p95 | 3,600 s or less | Change timestamp against curated commit time | Scenario | Must | BUD-03 | Given |
| REQ-05 | Regulatory data for a business day is complete the next morning | Requirement | FLW-01, FLW-03, FLW-05, FLW-06 | Time at which day D is reconciled in T1 | By 06:00 on D plus 1 | Reconciliation report timestamp | Scenario | Must | REC-02 | Given |
| REQ-06 | Settlement records are loaded within two hours of file arrival | Requirement | FLW-06 | Arrival-to-published age | 7,200 s or less | File arrival time against publish time | Scenario | Must | EXT-04 | Given |
| REQ-07 | Settlement records are neither lost nor duplicated | Requirement | FLW-06 | Control-total and count delta per file | Zero tolerance | Manifest against loaded rows | Scenario | Must | SCN-10 | Given |
| REQ-08 | The contact-centre view is at most minutes stale | Requirement | FLW-04 | Age of a customer record in the view at p95 | 900 s or less (assumption ASM-07) | Source modified time against view refresh | Assumed | Must | BUD-04 | Assumed |
| REQ-09 | The ledger feed is recoverable from any point in the last seven days | Requirement | FLW-01 | Replay horizon | 7 days or more | Replay drill from a retained position | Scenario | Must | LAG-04 | Given |
| REQ-10 | The fraud feed survives a consumer outage of one hour without data loss | Requirement | FLW-02 | Events lost across a one-hour outage | 0 and catch-up within 1,800 s | Outage drill | Scenario | Must | LAG-01 | Given |
| REQ-11 | Breaking contract changes are announced at least 30 days ahead | Requirement | all | Notice period of a breaking change | 30 days or more | Change log review | Scenario | Must | CHG-05 | Given |
| REQ-12 | Extraction from the CRM stays within its rate limit and quota | Requirement | FLW-04, FLW-05 | Request rate and daily requests | 10 requests per s or less; within the daily quota | Request counters | Scenario | Must | API-02 | Given |
| REQ-13 | Extraction never scans the ledger primary | Requirement | FLW-01 | Queries against the primary for extraction | 0 | Source query log review | Scenario | Must | EXT-01 | Given |
| REQ-14 | Every flow has an owner and an on-call route | Requirement | all | Flows without a named owner or route | 0 | Register review | Scenario | Must | OPS-01 | Given |
| REQ-15 | Reconciliation evidence is retained for audit | Requirement | FLW-01, FLW-05, FLW-06 | Evidence retention period | Set by OQ-07 | Evidence store review | Scenario | Must | REC-05 | Given |
| REQ-16 | Personal data stays in the stated jurisdiction | Requirement | all | Stores or sinks outside the jurisdiction | 0 | Deployment review | Scenario | Must | STR-01 | Given |
| REQ-17 | Each flow uses least-privilege credentials | Requirement | all | Credentials shared across flows or over-privileged | 0 | Access review | Scenario | Must | SEC-01 | Given |
| REQ-18 | Data is encrypted in transit and at rest | Requirement | all | Hops or stores without encryption | 0 | Configuration review | Scenario | Must | SEC-03 | Given |
| REQ-19 | Classification travels with data into landing and dead-letter stores | Requirement | all | Datasets in these stores without a label | 0 | Store audit | Scenario | Must | STR-02 | Given |
| REQ-20 | Lineage is registered for every flow | Requirement | all | Flows without a lineage record per run | 0 | Lineage record check | Scenario | Must | SEC-06 | Given |
| REQ-21 | Card events reach analytics hourly with no loss and no duplication | Requirement | FLW-03 | Hourly count and total delta | Zero tolerance | Stream offsets against landed files | Assumed | Must | REC-08 | Assumed |
| REQ-22 | Deleted CRM records disappear from analytics within seven days | Requirement | FLW-05 | Age of an undetected delete | 7 days or less | Weekly bulk export against curated keys | Assumed | Should | REC-14 | Assumed |
| CON-01 | The project stops at architecture design | Constraint | all | Product, code or sizing decisions in this package | 0 | Package review | Scenario | Must | VAL-01 | Given |
| CON-02 | The ledger primary must not be strained by integration | Constraint | FLW-01 | Extraction load on S1 | Read replica or log only | Source monitoring | Scenario | Must | EXT-01 | Given |
| CON-03 | The CRM rate limit is 10 requests per second | Constraint | FLW-04, FLW-05 | Request rate | 10 per s | Vendor terms | Scenario | Must | FED-01 | Given |
| CON-04 | The partner delivers one file a day with a manifest and no record-level API | Constraint | FLW-06 | Delivery interface | File drop only | Partner agreement | Scenario | Must | SCN-12 | Given |
| ASM-01 | The ledger holds 8 TB at 200 bytes a row | Assumption | FLW-01 | Total records and row size | 40 billion rows; 200 B | Confirm with the S1 owner | Carried in from module 2D.5 | Must | EXT-01 | Assumed |
| ASM-02 | An average card event is 1 KB | Assumption | FLW-02, FLW-03 | Event size | 1,000 bytes | Measure on a sample | Scenario volume | Must | STM-01 | Assumed |
| ASM-03 | A stream partition sustains 5 MB/s with 2 times headroom | Assumption | FLW-02 | Per-partition throughput | 5 MB/s | Load test in 2D.9 | Topic 4 example | Should | STM-01 | Assumed |
| ASM-04 | A replica extract sustains 200 MB/s inside a 4-hour window | Assumption | FLW-01 | Throughput and window | 200 MB/s; 14,400 s | Source test | Planning value | Must | EXT-01 | Assumed |
| ASM-05 | A CRM record is 2,000 bytes | Assumption | FLW-04, FLW-05 | Record size | 2,000 bytes | Sample the export | Planning value | Should | EXT-05 | Assumed |
| ASM-06 | A settlement record is 1,000 bytes and loads at 50 MB/s | Assumption | FLW-06 | Record size and load rate | 1,000 B; 50 MB/s | Load test | Scenario volume | Should | EXT-04 | Assumed |
| ASM-07 | Contact-centre staleness of 15 minutes is acceptable | Assumption | FLW-04 | Staleness target | 900 s | Confirm with the Head of Contact Centre | Scenario says minutes | Must | BUD-04 | Assumed |
| ASM-08 | A recovering fraud consumer can run at three times the arrival rate | Assumption | FLW-02 | Consumer capacity | 60,000 events per s | Capacity test | Planning value | Must | LAG-01 | Assumed |
| ASM-09 | Source and path availabilities are 0.995 (CRM), 0.999 (gateway), 0.9995 (network) | Assumption | FLW-04 | Availabilities | As stated | Vendor report | Planning value | Should | AVC-01 | Assumed |
| ASM-10 | 300 agents each look up a customer twice a minute | Assumption | FLW-04 | Lookup rate | 600 per minute | Contact-centre logs | Planning value | Should | FED-01 | Assumed |
| ASM-11 | Three retry waits with a base of 1 s and factor 2 fit the budget | Assumption | FLW-04, FLW-02 | Retry budget | 7 s | Retry test | Planning value | Should | RTY-01 | Assumed |
| ASM-12 | Stage latencies are planning values | Assumption | FLW-02, FLW-01, FLW-04 | Latency per stage | See LAT rows | Measure in a pilot | Planning value | Must | BUD-01 | Assumed |
| DEP-01 | Stream processing design is delivered by module 2D.9 | Dependency | FLW-02 | Design exists | Delivered | Module hand-off | Roadmap | Must | OQ-06 | Given |
| DEP-02 | Landing, quarantine and curated zones are delivered by module 2D.7 | Dependency | all | Zones exist | Delivered | Module hand-off | Roadmap | Must | OQ-08 | Given |
| DEP-03 | Connectivity, identity and service mapping come from module 2D.8 | Dependency | all | Mapping exists | Delivered | Module hand-off | Roadmap | Must | OQ-06 | Given |
| DEP-04 | Catalogue and lineage tooling come from module 2D.11 | Dependency | all | Tooling exists | Delivered | Module hand-off | Roadmap | Should | OQ-08 | Given |

**Standards used by the calculations.** Every threshold lives in one table so a reviewer can change it and re-run the checker. All are illustrative.

| ID | Standard | Key | Value | Unit | Evidence |
| --- | --- | --- | --- | --- | --- |
| STD-01 | Seconds per day | seconds_per_day | 86400 | s | Given |
| STD-02 | Minimum latency headroom | headroom_min | 0.10 | fraction | Assumed |
| STD-03 | Largest share of a source limit a design may use | fed_max_share | 0.5 | fraction | Assumed |
| STD-04 | Minimum notice for a breaking contract change | notice_days_min | 30 | d | Given |
| STD-05 | Sustained replica extract rate | ledger_extract_mb_s | 200 | MB/s | Assumed |
| STD-06 | Nightly extract window | ledger_window_s | 14400 | s | Assumed |
| STD-07 | CRM bulk export load rate | bulk_export_mb_s | 100 | MB/s | Assumed |
| STD-08 | Settlement load rate | settlement_load_mb_s | 50 | MB/s | Assumed |
| STD-09 | Landing write rate | landing_load_mb_s | 500 | MB/s | Assumed |
| STD-10 | CRM request rate limit | crm_rate_per_s | 10 | requests per s | Given |
| STD-11 | CRM request rate if the vendor halves it | crm_rate_halved_per_s | 5 | requests per s | Assumed |
| STD-12 | Stream per-partition throughput | partition_mb_s | 5 | MB/s | Assumed |
| STD-13 | Partition headroom factor | partition_headroom | 2 | factor | Assumed |
| STD-14 | Stream replication factor | replication_factor | 3 | factor | Assumed |
| STD-15 | Stream retention | stream_retention_days | 7 | d | Assumed |
| STD-16 | Target time to drain a backlog | catch_up_target_s | 1800 | s | Assumed |
| STD-17 | Fraud freshness target | fraud_p95_s | 60 | s | Given |
| STD-18 | Settlement deadline after arrival | settlement_deadline_s | 7200 | s | Given |

### 6.5 D5 — Workload and freshness requirements (Step 6)

Each worksheet recomputes the toolkit formulas of the roadmap. A **chosen** row must pass; a **rejected alternative** row must fail, which is the quantified reason it was rejected. `~` marks a derived cell.

**Batch extract and load time** (`extract_time = bytes ÷ throughput`).

| ID | Batch line | Flow | Variant | Workload | Basis | Volume GB | Throughput MB/s | Time s | Window s | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EXT-01 | Nightly full copy of the ledger from the replica | FLW-01 | Rejected alternative | WLD-01 | total | 8,000.00 | ledger_extract_mb_s | 40,000 | 14400 | Fail | Derived |
| EXT-02 | Daily changed volume moved by change capture | FLW-01 | Chosen | WLD-01 | daily | 1.00 | ledger_extract_mb_s | 5 | 14400 | Pass | Derived |
| EXT-03 | Hourly snapshot diff of the ledger on the replica | FLW-01 | Rejected alternative | WLD-01 | total | 8,000.00 | ledger_extract_mb_s | 40,000 | 3600 | Fail | Derived |
| EXT-04 | Daily settlement file load | FLW-06 | Chosen | WLD-04 | daily | 2.00 | settlement_load_mb_s | 40 | 3600 | Pass | Derived |
| EXT-05 | Weekly CRM bulk export load | FLW-05 | Chosen | WLD-03 | total | 24.00 | bulk_export_mb_s | 240 | 14400 | Pass | Derived |
| EXT-06 | Hourly card-event files written to landing (daily total) | FLW-03 | Chosen | WLD-02 | daily | 1,000.00 | landing_load_mb_s | 2,000 | 86400 | Pass | Derived |

The nightly full copy needs 40,000 s against a 14,400 s window, which is why the baseline is rejected on load and window alone. The settlement load uses 40 s of a 3,600 s budget, which leaves room for validation, quarantine and a retry inside the two-hour deadline.

**API request count and duration** (`api_calls = ceil(records ÷ page_size)`, `api_duration = api_calls ÷ allowed_rate`). Quota is unknown (CAP-10), so a chosen row that stays inside its window reads `Conditional (quota unknown)` until OQ-03 is answered.

| ID | API line | Flow | Variant | Workload | Basis | Page size | Rate per s | Runs per day | Requests per run | Pacing time s | Window s | Daily requests | Quota per day | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| API-01 | Full CRM pull every 30 minutes to meet the 15-minute view target | FLW-04 | Rejected alternative | WLD-03 | total | 1000 | crm_rate_per_s | 48 | 12,000 | 1,200 | 900 | 576,000 | Unknown | Fail | Derived |
| API-02 | Incremental CRM poll every 5 minutes | FLW-04 | Chosen | WLD-03 | per-run | 1000 | crm_rate_per_s | 288 | 1 | 0 | 300 | 288 | Unknown | Conditional (quota unknown) | Derived |
| API-03 | Daily incremental CRM pull for analytics | FLW-05 | Chosen | WLD-03 | daily | 1000 | crm_rate_per_s | 1 | 12 | 1 | 14400 | 12 | Unknown | Conditional (quota unknown) | Derived |
| API-04 | Daily incremental CRM pull if the vendor halves the rate | FLW-05 | Chosen | WLD-03 | daily | 1000 | crm_rate_halved_per_s | 1 | 12 | 2 | 14400 | 12 | Unknown | Conditional (quota unknown) | Derived |

A full CRM pull is 12,000 requests; at 10 requests per second that is 1,200 s, which cannot finish inside a 900 s staleness target, so a design that refreshes the whole CRM to stay fresh fails before quota is even considered.

**Retry budget** (`retry_wait_total = Σ base × factor^i`, before jitter).

| ID | Retry line | Base wait s | Factor | Waits | Total wait s | Budget s | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RTY-01 | CRM API call after a rate-limit or timeout response | 1 | 2 | 3 | 7 | 10 | Pass | Derived |
| RTY-02 | Fraud consumer retries on a failing event before dead-letter | 1 | 2 | 3 | 7 | 10 | Pass | Derived |

**Stream partitions and retention** (`partitions = ceil(peak ÷ per-partition) × headroom`; `retained = rate × size × days × replication`). Partitioning by a hot key concentrates load on one partition, so the skew check multiplies the hottest key's share by the stream rate.

| ID | Stream line | Flow | Variant | Workload | Rate basis | Event rate per s | Event bytes | MB per s | Per-partition MB/s | Headroom | Partitions | Hot key share | Skew check | Retention days | Replication factor | Retained TB | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| STM-01 | Card-event stream at the peak rate, keyed by card | FLW-02 | Chosen | WLD-02 | peak | 20,000.00 | 1,000 | 20.00 | 5 | 2 | 8 | 0.01 | Pass | 7 | 3 | 36.29 | Derived |
| STM-02 | Card-event stream retention at the average rate | FLW-02 | Chosen | WLD-02 | avg | 11,574.07 | 1,000 | 11.57 | 5 | 2 | 6 | 0.01 | Pass | 7 | 3 | 21.00 | Derived |
| STM-03 | Card-event stream keyed by merchant | FLW-02 | Rejected alternative | WLD-02 | peak | 20,000.00 | 1,000 | 20.00 | 5 | 2 | 8 | 0.30 | Fail | 7 | 3 | 36.29 | Derived |
| STM-04 | Ledger change stream at the peak rate | FLW-01 | Chosen | WLD-01 | peak | 2,000.00 | 200 | 0.40 | 5 | 2 | 2 | 0.05 | Pass | 7 | 3 | 0.73 | Derived |
| STM-05 | Ledger change stream retention at the average rate | FLW-01 | Chosen | WLD-01 | avg | 57.87 | 200 | 0.01 | 5 | 2 | 2 | 0.05 | Pass | 7 | 3 | 0.02 | Derived |

STM-01 reproduces the roadmap example (20 MB/s, 4 partitions, 8 with headroom, 36.288 TB for seven days at three copies at the sustained peak). STM-02 shows the same stream at its daily average, 21 TB. STM-03 shows why the key must be the card, not the merchant: a merchant holding 30% of the traffic would need 6 MB/s from one partition, above the 5 MB/s limit, whatever the partition count.

**Backlog and catch-up** (`backlog_growth_rate = arrival − processing`; `catch_up_time = backlog ÷ (capacity − arrival)`; `required capacity = arrival + backlog ÷ target`). `WLD-nn:peak` and `WLD-nn:avg` read the workload table.

| ID | Backlog line | Flow | Variant | Arrival per s | Capacity during incident per s | Incident s | Capacity after per s | Backlog records | Catch-up s | Target catch-up s | Required capacity per s | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LAG-01 | Fraud consumer down one hour, recovers at three times the arrival rate | FLW-02 | Chosen | WLD-02:peak | 0 | 3600 | 60000 | 72,000,000 | 1,800 | 1800 | 60,000 | Pass | Derived |
| LAG-02 | The same outage with a recovered capacity of 30,000 events per second | FLW-02 | Rejected alternative | WLD-02:peak | 0 | 3600 | 30000 | 72,000,000 | 7,200 | 1800 | 60,000 | Fail | Derived |
| LAG-03 | Ledger capture stalls for 30 minutes at the peak change rate | FLW-01 | Chosen | WLD-01:peak | 0 | 1800 | 6000 | 3,600,000 | 900 | 3600 | 3,000 | Pass | Derived |
| LAG-04 | Replay of seven days of ledger changes at the average rate | FLW-01 | Chosen | WLD-01:avg | 0 | 604800 | 2000 | 35,000,000 | 18,021 | 86400 | 463 | Pass | Derived |

During catch-up the fraud freshness target is missed: the consumer drains 72 million events over 1,800 s, so events from the outage window are scored late. The design accepts that and prevents loss; WLK-13 records it as a residual risk.

**Freshness budgets** (p95 seconds; headroom must be at least 10%, STD-02).

| ID | Latency component | Unit | Value | Evidence |
| --- | --- | --- | --- | --- |
| LAT-01 | Publish and broker append | s | 1 | Assumed |
| LAT-02 | Consumer fetch and deserialise | s | 2 | Assumed |
| LAT-03 | Write to the fraud store | s | 5 | Assumed |
| LAT-04 | Queue wait at the peak rate | s | 3 | Assumed |
| LAT-05 | Micro-batch interval of the baseline file path | s | 300 | Assumed |
| LAT-06 | File write and load of the baseline path | s | 30 | Assumed |
| LAT-07 | Change capture read from the ledger log | s | 5 | Assumed |
| LAT-08 | Transport and buffering | s | 5 | Assumed |
| LAT-09 | Landing micro-batch interval | s | 900 | Assumed |
| LAT-10 | Merge into curated tables | s | 120 | Assumed |
| LAT-11 | CRM poll interval | s | 300 | Assumed |
| LAT-12 | API fetch and apply | s | 30 | Assumed |
| LAT-13 | View refresh | s | 20 | Assumed |
| LAT-14 | Consumer outage of one hour (stress) | s | 3600 | Assumed |

| ID | Budget path | Components | Unit | Total | Target | Headroom | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BUD-01 | Fraud freshness p95, keyed-stream path (chosen) | LAT-01, LAT-02, LAT-03, LAT-04 | s | 11.0 | 60 | 81.7% | Pass | Derived |
| BUD-02 | Fraud freshness p95, five-minute file micro-batch (baseline) | LAT-01, LAT-05, LAT-06, LAT-03 | s | 336.0 | 60 | -460.0% | Fail | Derived |
| BUD-03 | Ledger to curated tables, hourly target (chosen) | LAT-07, LAT-08, LAT-09, LAT-10 | s | 1,030.0 | 3600 | 71.4% | Pass | Derived |
| BUD-04 | CRM current view, poll path (chosen) | LAT-11, LAT-12, LAT-13 | s | 350.0 | 900 | 61.1% | Pass | Derived |
| BUD-05 | Fraud freshness during a one-hour consumer outage (stress) | LAT-01, LAT-14 | s | 3,601.0 | 60 | -5901.7% | Fail | Derived |

**Availability of serial dependencies** (`chain_availability = A1 × A2 × … × An`).

| ID | Availability chain | Flow | Variant | Availabilities | Product | Target | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AVC-01 | Contact-centre view read live from the CRM API through the gateway and network | FLW-04 | Rejected alternative | 0.995, 0.999, 0.9995 | 99.351% | 99.5 | Fail | Derived |
| AVC-02 | Contact-centre view read from its own store through the gateway | FLW-04 | Chosen | 0.9995, 0.999 | 99.850% | 99.5 | Pass | Derived |

**Federated lookup load** (`requests per second = users × lookups per minute × requests per lookup ÷ 60`; a design may use at most half of a source limit, STD-03).

| ID | Federation line | Flow | Variant | Concurrent users | Lookups per user per min | Source requests per lookup | Requests per s | Source limit per s | Share of limit | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FED-01 | Agents query the CRM live for each customer lookup | FLW-04 | Rejected alternative | 300 | 2 | 1 | 10.00 | 10 | 100.0% | Fail | Derived |
| FED-02 | One poller refreshes the materialised view every five minutes | FLW-04 | Chosen | 1 | 0.2 | 1 | 0.00 | 10 | 0.0% | Pass | Derived |

### 6.6 D6 — Integration pattern comparison matrix (Steps 7 and 8)

**Order of work.** Gates and criteria are fixed first and dated. Candidates are screened by the gates, then the survivors are scored. Scores are integers from 1 (poor) to 5 (strong) and are recorded judgments, not measurements. For source impact, simplicity and cost, a higher score means *less* impact, *simpler* operation and *cheaper or more open*. Each candidate lists the source capabilities it **requires**: a candidate that requires a capability the source does not offer cannot be eligible, and one that requires an unknown capability makes the decision conditional on the open question that settles it.

**Gates.** A candidate that fails a gate is not scored for selection; it stays in the table with the reason.

| ID | Gate | Test | Decisions | Evidence |
| --- | --- | --- | --- | --- |
| GT-01 | Source-load safety | Extraction fits its window and the source's limits and does not scan a protected primary | DEC-01, DEC-04, DEC-05, DEC-06, DEC-07 | Given |
| GT-02 | Freshness feasibility | Meets the flow's freshness target with at least 10% headroom (STD-02) | DEC-01, DEC-02, DEC-03, DEC-04, DEC-05 | Derived |
| GT-03 | Change and delete visibility | Updates and deletes at the source become visible to the target | DEC-01, DEC-05 | Given |
| GT-04 | Replay and recovery horizon | Supports replay for the required recovery period without re-reading the source | DEC-01, DEC-02, DEC-03 | Given |
| GT-05 | Per-key ordering | Preserves the order of events for one card | DEC-02 | Given |
| GT-06 | Completeness evidence | Allows an independent check that everything arrived and nothing arrived twice | DEC-03, DEC-06 | Given |
| GT-07 | Jurisdiction, encryption and least privilege | Satisfies REQ-16, REQ-17 and REQ-18 | DEC-01, DEC-02, DEC-03, DEC-04, DEC-05, DEC-06, DEC-07 | Given |
| GT-08 | Reproducibility | The raw input is preserved so any load can be re-derived and audited | DEC-07 | Given |
| GT-09 | Interface exists | Every source interface the candidate needs is offered (status Yes) or not yet known (status Unknown, which makes the decision conditional) | DEC-01, DEC-02, DEC-03, DEC-04, DEC-05, DEC-06, DEC-07 | Given |

**Criteria.** Weights were fixed on 2026-10-18, before any candidate was scored (D6 is dated 2026-10-21).

| ID | Criterion | Weight | Question it answers | Locked on | Evidence |
| --- | --- | --- | --- | --- | --- |
| CRT-01 | C1 Freshness and throughput fit | 0.15 | Does it meet the freshness and volume of the flow? | 2026-10-18 | Assumed |
| CRT-02 | C2 Correctness controls | 0.15 | Can identity, deduplication and reconciliation be applied? | 2026-10-18 | Assumed |
| CRT-03 | C3 Source impact | 0.15 | How little load does it put on the source? | 2026-10-18 | Assumed |
| CRT-04 | C4 Change and delete visibility | 0.10 | Does it see updates and deletes? | 2026-10-18 | Assumed |
| CRT-05 | C5 Ordering and replay | 0.15 | Does it keep order and allow replay? | 2026-10-18 | Assumed |
| CRT-06 | C6 Operational simplicity | 0.10 | How little extra on-call and maintenance does it add? | 2026-10-18 | Assumed |
| CRT-07 | C7 Security, governance and contracts | 0.10 | Can access, classification and contracts be enforced? | 2026-10-18 | Assumed |
| CRT-08 | C8 Cost and lock-in | 0.10 | How low is the cost and how easily can it be replaced? | 2026-10-18 | Assumed |

**Weight sets for the sensitivity test.** `WS-00` equals the locked weights; the others are stress tests, not alternatives anyone has proposed.

| ID | Weight set | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | Purpose |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WS-00 | Locked weights | 0.15 | 0.15 | 0.15 | 0.10 | 0.15 | 0.10 | 0.10 | 0.10 | The scoring used for selection |
| WS-01 | Equal weights | 0.125 | 0.125 | 0.125 | 0.125 | 0.125 | 0.125 | 0.125 | 0.125 | Tests dependence on the chosen weights |
| WS-02 | Simplicity-heavy | 0.10 | 0.10 | 0.10 | 0.10 | 0.10 | 0.30 | 0.10 | 0.10 | A small operations team |
| WS-03 | Cost-heavy | 0.10 | 0.10 | 0.10 | 0.10 | 0.10 | 0.10 | 0.10 | 0.30 | A tight budget |
| WS-04 | Governance-heavy | 0.10 | 0.10 | 0.10 | 0.10 | 0.10 | 0.10 | 0.30 | 0.10 | A stricter regulator |

**Candidate matrix.** Gate cell: `GT-nn:P` passes, `GT-nn:F` fails. Total, Eligible and Rank are derived. Each decision has at least three eligible candidates and exactly one baseline (the simplest adequate option).

| ID | Candidate | Decision | Baseline | Requires | Gates | Gate failure reason | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | Total | Eligible | Rank | Limitation or risk | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAN-01 | Nightly full copy of the ledger tables from the replica | DEC-01 | Yes | CAP-01 | GT-01:F; GT-02:F; GT-03:P; GT-04:P; GT-07:P; GT-09:P | EXT-01: a full copy takes 40,000 s against a 14,400 s window, and a nightly cadence cannot meet the hourly target | 2 | 3 | 1 | 4 | 2 | 5 | 4 | 3 | 2.80 | No | - | Strains the replica and the network; history older than a day is re-copied each night | Derived |
| CAN-02 | Incremental extract driven by a last-modified column | DEC-01 | No | CAP-03 | GT-01:P; GT-02:P; GT-03:F; GT-04:P; GT-07:P; GT-09:F | CAP-03: the ledger has no reliable last-modified column on all tables, so changes and deletes would be missed | 3 | 2 | 3 | 1 | 2 | 4 | 3 | 4 | 2.70 | No | - | Silently misses rows on tables without the column | Given |
| CAN-03 | Log-based change capture with an initial snapshot and a retained change stream | DEC-01 | No | CAP-02, CAP-04 | GT-01:P; GT-02:P; GT-03:P; GT-04:P; GT-07:P; GT-09:P | none | 5 | 4 | 4 | 5 | 5 | 3 | 4 | 4 | 4.30 | Yes | 1 | Needs log access and a snapshot-to-stream seam procedure; log retention is unknown (CAP-04) | Assumed |
| CAN-04 | Hourly snapshot comparison on the replica | DEC-01 | No | CAP-01 | GT-01:F; GT-02:P; GT-03:P; GT-04:P; GT-07:P; GT-09:P | EXT-03: comparing 8,000 GB each hour takes 40,000 s against a 3,600 s window | 2 | 3 | 2 | 4 | 2 | 4 | 3 | 3 | 2.75 | No | - | Cost grows with table size, not with change volume | Derived |
| CAN-05 | Trigger-based change tables on the source | DEC-01 | No | CAP-01 | GT-01:P; GT-02:P; GT-03:P; GT-04:P; GT-07:P; GT-09:P | none | 4 | 3 | 2 | 4 | 3 | 3 | 3 | 4 | 3.20 | Yes | 3 | Adds write work to the ledger at 2,000 changes per second | Assumed |
| CAN-06 | Managed replication connector using the transaction log | DEC-01 | No | CAP-02 | GT-01:P; GT-02:P; GT-03:P; GT-04:P; GT-07:P; GT-09:P | none | 5 | 4 | 4 | 5 | 4 | 4 | 3 | 2 | 3.95 | Yes | 2 | Less control over seam, schema and replay behaviour; vendor dependence | Assumed |
| CAN-07 | Five-minute micro-batch of published events through files | DEC-02 | Yes | CAP-06 | GT-02:F; GT-04:P; GT-05:P; GT-07:P; GT-09:P | BUD-02: a five-minute batch path totals 336 s against 60 s | 2 | 3 | 4 | 3 | 2 | 5 | 3 | 4 | 3.15 | No | - | Hours-old data is avoided but minutes-old data still misses the target | Derived |
| CAN-08 | Keyed event stream consumed by the fraud service, with offsets and a retained log | DEC-02 | No | CAP-06, CAP-07 | GT-02:P; GT-04:P; GT-05:P; GT-07:P; GT-09:P | none | 5 | 4 | 4 | 3 | 5 | 3 | 4 | 4 | 4.10 | Yes | 1 | Needs an ordering guarantee from S2 (CAP-07 unknown); an extra component to operate | Assumed |
| CAN-09 | Direct calls from the cards platform to the fraud service | DEC-02 | No | CAP-06 | GT-02:P; GT-04:F; GT-05:P; GT-07:P; GT-09:P | No retained log: a one-hour fraud-service outage would lose about 72 million events (REQ-10) | 4 | 2 | 4 | 3 | 1 | 4 | 3 | 4 | 3.05 | No | - | The cards platform becomes coupled to the fraud service's availability | Given |
| CAN-10 | One shared queue read by competing consumers | DEC-02 | No | CAP-06 | GT-02:P; GT-04:P; GT-05:F; GT-07:P; GT-09:P | Competing consumers apply events for one card in any order, so per-card ordering (REQ-02) cannot be kept | 4 | 3 | 4 | 3 | 1 | 4 | 3 | 4 | 3.20 | No | - | Fast and simple but unordered | Given |
| CAN-11 | Managed streaming service with keyed partitions | DEC-02 | No | CAP-06, CAP-07 | GT-02:P; GT-04:P; GT-05:P; GT-07:P; GT-09:P | none | 5 | 4 | 4 | 3 | 5 | 4 | 4 | 2 | 4.00 | Yes | 2 | Higher cost and tied to one provider's behaviour; the ordering guarantee is still unknown | Assumed |
| CAN-12 | Push each event to the fraud service with a local buffer | DEC-02 | No | CAP-06 | GT-02:P; GT-04:P; GT-05:P; GT-07:P; GT-09:P | none | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3.15 | Yes | 3 | The buffer is a second, unshared retention mechanism | Assumed |
| CAN-13 | Daily export of card events to analytics | DEC-03 | Yes | CAP-06 | GT-02:F; GT-04:P; GT-06:P; GT-07:P; GT-09:P | A daily export is up to 86,400 s old against hourly dashboards | 1 | 4 | 4 | 3 | 3 | 5 | 4 | 4 | 3.40 | No | - | Misses the hourly freshness need | Derived |
| CAN-14 | Second consumer group writing hourly files to the landing zone with offset checkpoints | DEC-03 | No | CAP-06 | GT-02:P; GT-04:P; GT-06:P; GT-07:P; GT-09:P | none | 4 | 4 | 4 | 3 | 5 | 4 | 4 | 4 | 4.05 | Yes | 1 | Hourly files need compaction; late events land in the next file | Assumed |
| CAN-15 | Continuous micro-commits of events into curated tables | DEC-03 | No | CAP-06 | GT-02:P; GT-04:P; GT-06:P; GT-07:P; GT-09:P | none | 5 | 3 | 4 | 3 | 4 | 2 | 3 | 3 | 3.50 | Yes | 3 | Very small files and constant table maintenance | Assumed |
| CAN-16 | Copy the data from the fraud service's own store | DEC-03 | No | none | GT-02:P; GT-04:F; GT-06:F; GT-07:P; GT-09:P | The fraud store keeps only a short window and its contents are not the complete event record, so completeness cannot be proven | 3 | 2 | 3 | 2 | 1 | 3 | 2 | 3 | 2.35 | No | - | Couples analytics history to a store built for scoring | Given |
| CAN-17 | Managed sink connector from the stream to the landing zone | DEC-03 | No | CAP-06 | GT-02:P; GT-04:P; GT-06:P; GT-07:P; GT-09:P | none | 4 | 4 | 4 | 3 | 4 | 4 | 3 | 2 | 3.60 | Yes | 2 | Connector behaviour on duplicates and schema change is outside our control | Assumed |
| CAN-18 | Daily full CRM pull into the view store | DEC-04 | Yes | CAP-09 | GT-01:P; GT-02:F; GT-07:P; GT-09:P | API-01: refreshing the whole CRM takes 1,200 s of requests at 10 per second, beyond a 900 s target | 1 | 4 | 2 | 4 | 3 | 5 | 4 | 4 | 3.20 | No | - | A day of staleness at best | Derived |
| CAN-19 | Incremental poll every five minutes with a modified-since filter, into a materialised view | DEC-04 | No | CAP-09, CAP-11 | GT-01:P; GT-02:P; GT-07:P; GT-09:P | none | 5 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | 4.05 | Yes | 1 | Needs the modified-since filter (CAP-11 unknown) and a quota that fits (CAP-10 unknown) | Assumed |
| CAN-20 | Federated live lookups against the CRM at read time | DEC-04 | No | CAP-09 | GT-01:F; GT-02:P; GT-07:P; GT-09:P | FED-01: 300 agents making two lookups a minute use 10 requests per second, 100% of the CRM limit, and AVC-01 gives 99.351% availability against 99.5% | 5 | 2 | 1 | 5 | 1 | 3 | 2 | 3 | 2.65 | No | - | Every lookup depends on the CRM and its rate limit | Derived |
| CAN-21 | Change notifications pushed from the CRM into a queue, feeding the view | DEC-04 | No | CAP-17 | GT-01:P; GT-02:P; GT-07:P; GT-09:P | none | 5 | 3 | 5 | 4 | 3 | 2 | 3 | 3 | 3.60 | Yes | 3 | Depends on a notification feature that may not exist (CAP-17 unknown) and on delivery guarantees | Assumed |
| CAN-22 | Weekly bulk export only | DEC-04 | No | CAP-12 | GT-01:P; GT-02:F; GT-07:P; GT-09:P | A weekly export is up to 604,800 s old against a 900 s target | 1 | 4 | 5 | 3 | 3 | 5 | 4 | 5 | 3.65 | No | - | Unsuitable for a current view | Derived |
| CAN-23 | Poll every ten minutes with a daily full verification pull | DEC-04 | No | CAP-09, CAP-11 | GT-01:P; GT-02:P; GT-07:P; GT-09:P | none | 4 | 5 | 2 | 4 | 4 | 3 | 4 | 3 | 3.65 | Yes | 2 | A full pull each day uses 12,000 requests and may exceed the unknown quota | Assumed |
| CAN-24 | Weekly bulk export loaded as a full snapshot | DEC-05 | Yes | CAP-12 | GT-01:P; GT-02:F; GT-03:P; GT-07:P; GT-09:P | A weekly snapshot is up to 7 days old against the daily analytics need | 1 | 4 | 4 | 4 | 3 | 5 | 4 | 4 | 3.50 | No | - | Deletes appear only weekly | Derived |
| CAN-25 | Daily incremental API pull plus a weekly bulk export for delete detection and reconciliation | DEC-05 | No | CAP-09, CAP-11, CAP-12 | GT-01:P; GT-02:P; GT-03:P; GT-07:P; GT-09:P | none | 4 | 5 | 4 | 4 | 4 | 3 | 4 | 4 | 4.05 | Yes | 1 | Two feeds to align; relies on the modified-since filter (CAP-11 unknown) | Assumed |
| CAN-26 | Daily full API pull | DEC-05 | No | CAP-09 | GT-01:P; GT-02:P; GT-03:P; GT-07:P; GT-09:P | none | 3 | 4 | 2 | 4 | 3 | 4 | 4 | 3 | 3.30 | Yes | 4 | 12,000 requests a day against an unknown quota | Assumed |
| CAN-27 | Push notifications of changes, with a daily catch-up | DEC-05 | No | CAP-17 | GT-01:P; GT-02:P; GT-03:P; GT-07:P; GT-09:P | none | 5 | 3 | 5 | 3 | 3 | 2 | 3 | 3 | 3.50 | Yes | 3 | Depends on an unknown notification feature | Assumed |
| CAN-28 | Managed CRM connector operated by a third party | DEC-05 | No | CAP-09, CAP-12 | GT-01:P; GT-02:P; GT-03:P; GT-07:P; GT-09:P | none | 4 | 4 | 4 | 4 | 3 | 5 | 3 | 2 | 3.65 | Yes | 2 | Opaque handling of deletes and retries; vendor dependence | Assumed |
| CAN-29 | Scheduled load of the partner file with no validation | DEC-06 | Yes | CAP-14 | GT-01:P; GT-06:F; GT-07:P; GT-09:P | A file that arrives incomplete would load silently (SCN-12); there is no independent completeness check | 4 | 1 | 4 | 3 | 2 | 5 | 3 | 4 | 3.15 | No | - | Fast but unsafe for financial records | Given |
| CAN-30 | Manifest-gated load: detect arrival, validate count, checksum and control total, quarantine on mismatch, merge by settlement id | DEC-06 | No | CAP-14, CAP-15 | GT-01:P; GT-06:P; GT-07:P; GT-09:P | none | 5 | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 4.45 | Yes | 1 | Depends on the manifest carrying a count and a checksum (CAP-15 unknown) | Assumed |
| CAN-31 | Arrival-triggered manifest-gated load | DEC-06 | No | CAP-14, CAP-15 | GT-01:P; GT-06:P; GT-07:P; GT-09:P | none | 5 | 5 | 5 | 4 | 4 | 3 | 4 | 3 | 4.25 | Yes | 2 | Needs an arrival event and a fallback when the event is missed | Assumed |
| CAN-32 | Managed file-transfer service with built-in checksum verification | DEC-06 | No | CAP-14 | GT-01:P; GT-06:P; GT-07:P; GT-09:P | none | 4 | 4 | 5 | 3 | 3 | 5 | 4 | 2 | 3.80 | Yes | 3 | Does not check control totals or business rules; extra service to buy | Assumed |
| CAN-33 | Record-by-record ingestion through a partner API | DEC-06 | No | CAP-18 | GT-01:P; GT-06:P; GT-07:P; GT-09:F | CAP-18: the partner offers no record-level API | 5 | 3 | 4 | 4 | 3 | 2 | 3 | 3 | 3.45 | No | - | The interface does not exist | Given |
| CAN-34 | Transform in flight before loading, inside each integration job | DEC-07 | Yes | none | GT-01:P; GT-07:P; GT-08:F; GT-09:P | Only transformed rows are stored, so a defect in a transformation cannot be re-derived or audited from the raw input | 3 | 3 | 4 | 3 | 2 | 4 | 3 | 3 | 3.10 | No | - | Fixing a mapping means re-extracting from the source | Given |
| CAN-35 | Load raw to the landing zone, transform in the target (ELT) | DEC-07 | No | none | GT-01:P; GT-07:P; GT-08:P; GT-09:P | none | 4 | 4 | 4 | 4 | 5 | 4 | 4 | 4 | 4.15 | Yes | 1 | Raw personal and financial data sit in landing and must be protected and expired | Assumed |
| CAN-36 | Light conformance in flight, business logic in the target | DEC-07 | No | none | GT-01:P; GT-07:P; GT-08:P; GT-09:P | none | 4 | 4 | 4 | 4 | 4 | 3 | 5 | 4 | 4.00 | Yes | 2 | Two places hold transformation logic and must be kept consistent | Assumed |
| CAN-37 | Producers publish already-conformed business events | DEC-07 | No | none | GT-01:P; GT-07:P; GT-08:P; GT-09:P | none | 4 | 3 | 4 | 3 | 3 | 2 | 4 | 3 | 3.30 | Yes | 3 | Pushes work onto four source owners who may not agree | Assumed |
| CAN-38 | Transform with views on the source databases | DEC-07 | No | CAP-01 | GT-01:F; GT-07:P; GT-08:P; GT-09:P | Views on the ledger add read work to the system the integration must protect (CON-02) | 3 | 3 | 1 | 3 | 3 | 3 | 3 | 3 | 2.70 | No | - | Couples transformation logic to source release cycles | Given |

### 6.7 D7 — Pattern selection rationale per flow (Step 9)

**Decisions.** The checker recomputes the winner under every weight set and marks a decision weight-sensitive when the winner changes; such a decision carries a conditional note. A decision whose selected candidate requires an unknown source capability is also conditional on the question that settles it.

| ID | Decision | Flow | Requirements | Selected | Runner-up | Weight-sensitive | Conditional on | ADR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEC-01 | Pattern for ledger changes to analytics | FLW-01 | REQ-03, REQ-04, REQ-09, REQ-13, REQ-17, CON-02, ASM-01 | CAN-03 | CAN-06 | No | OQ-01: whether the ledger log is retained long enough to recover a stalled reader | ADR-01 |
| DEC-02 | Pattern for card events to the fraud service | FLW-02 | REQ-01, REQ-02, REQ-10, REQ-11, REQ-14, ASM-08 | CAN-08 | CAN-11 | Yes (WS-02) | OQ-02: whether the cards platform publishes in order per card; OQ-06: whether the team can operate a self-managed stream | ADR-02 |
| DEC-03 | Pattern for card events to analytics | FLW-03 | REQ-21 | CAN-14 | CAN-17 | No | none | ADR-03 |
| DEC-04 | Pattern for the current customer view | FLW-04 | REQ-08, REQ-12, CON-03 | CAN-19 | CAN-23 | No | OQ-04: whether the CRM API supports a modified-since filter; OQ-03: the daily quota | ADR-04 |
| DEC-05 | Pattern for CRM history to analytics | FLW-05 | REQ-12, REQ-22 | CAN-25 | CAN-28 | Yes (WS-02) | OQ-04: whether the CRM API supports a modified-since filter; OQ-03: the daily quota; OQ-06: whether the team can operate its own pull and merge | ADR-05 |
| DEC-06 | Pattern for settlement files | FLW-06 | REQ-06, REQ-07, REQ-15, CON-04 | CAN-30 | CAN-31 | No | OQ-05: whether the manifest carries a count and a checksum | ADR-06 |
| DEC-07 | Where transformation happens | FLW-01, FLW-03, FLW-05, FLW-06 | REQ-05, REQ-16, REQ-18, REQ-19, REQ-20, CON-01 | CAN-35 | CAN-36 | Yes (WS-04) | OQ-08: how long the raw copy in landing may be kept | ADR-07 |

**Summary of the choices.**

| Flow | Selected pattern | Why not the runner-up |
| --- | --- | --- |
| FLW-01 ledger to analytics | Log-based change capture with an initial snapshot and a retained change stream (CAN-03) | A managed connector (CAN-06) scores 3.95 against 4.30: it is simpler to run but gives less control of the seam and replay, and costs more |
| FLW-02 cards to fraud | Keyed event stream with offsets (CAN-08) | A managed streaming service (CAN-11) scores 4.00 against 4.10 and wins when operations simplicity carries 30% of the weight; the choice is therefore tied to OQ-06 |
| FLW-03 cards to analytics | Second consumer group writing hourly files (CAN-14) | A managed sink connector (CAN-17) scores 3.60 against 4.05 and hides duplicate handling |
| FLW-04 current customer view | Five-minute incremental poll into a materialised view (CAN-19) | Poll every ten minutes with a daily full verification (CAN-23) scores 3.65: it is safer on correctness but uses 12,000 extra requests a day against an unknown quota |
| FLW-05 CRM history | Daily incremental pull plus weekly bulk export (CAN-25) | A managed CRM connector (CAN-28) scores 3.65 against 4.05 and wins when simplicity carries 30% of the weight; the choice is therefore tied to OQ-06 |
| FLW-06 settlement files | Manifest-gated batch load (CAN-30) | An arrival-triggered gate (CAN-31) scores 4.25 against 4.45: the trigger adds a failure mode (a missed arrival event) for a saving of minutes inside a two-hour deadline |
| All landed flows | Load raw, transform in the target (CAN-35) | Light conformance in flight (CAN-36) scores 4.00 against 4.15 and wins when governance carries 30% of the weight |

**Reading the pattern for each flow.** Each flow's nearest **baseline** is the simplest adequate option; it appears in every decision and fails a quantified gate in each case (a full copy that overruns its window, a daily export against an hourly need, a daily full pull against a 15-minute target, a blind file load, an in-flight transformation that destroys the raw record). A baseline that passed would have been selected.

### 6.8 D8 — Logical integration architecture (Step 17)

This is a **logical** view: it shows systems, flows, mechanisms, contracts and control points, not products, hosts or networks. Version 1.1, 2026-10-21.

```text
D8-DIAGRAM v1.1 logical integration architecture. Legend: [SYS-nn] system; (FLW-nn) flow; ==> continuous; --> batch; {CTR-nn} contract; <RECON> control point.
Zones are logical. No product or service is implied.

 [SYS-01] Core ledger DB ==(FLW-01)==> change reader ==> {CTR-01} change stream (7-day retention) ==> landing -> curated   [SYS-05] Analytics platform (T1)
        (read replica + readable log)                                              ^ snapshot + stream seam               <RECON> counts, totals, key+version, invariant, independent extract

 [SYS-02] Cards platform ==(FLW-02)==> {CTR-02} keyed event stream (7-day retention) ==> fraud consumer ==> [SYS-06] Fraud service (T2)
        (event publication)                    |                                          <RECON> sequence gaps, counts
                                               +==(FLW-03)==> second consumer group --> hourly landing files --> [SYS-05]   <RECON> offsets vs files, totals

 [SYS-03] SaaS CRM ==(FLW-04)==> 5-minute incremental poll {CTR-03} ==> materialised view ==> [SYS-07] Contact-centre view (T3)
        (paginated API, 10 req/s)                                                              <RECON> weekly full comparison, sample records
          +--(FLW-05)--> daily incremental pull + weekly bulk export {CTR-04} --> landing -> curated [SYS-05]   <RECON> delete drift

 [SYS-04] Payment partner --(FLW-06)--> file arrival detector --> manifest gate {CTR-06} --> landing -> curated [SYS-05]
        (daily file + manifest)                         | mismatch                       | evidence report {CTR-07}
                                                        +--> quarantine (dead-letter)    +--> [SYS-08] Regulatory reporting (T4)

 Control points on every flow: contract check at publication and ingestion, dead-letter or quarantine store, monitoring (freshness, absence, volume),
 lineage record per run, reconciliation job with independent evidence.
```

### 6.9 D9 — Source-to-target flow descriptions (Steps 10 and 14)

**Flow inventory.** One row per flow; the pattern begins with the selected candidate from the comparison.

| ID | Flow | From | To | Asset | Pattern | Trigger | Expected volume | Freshness target | Transformation owner | Contract | Recovery | Decision | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FLW-01 | Ledger changes to analytics | SYS-01 | SYS-05 | AST-01 | CAN-03 Log-based change capture with an initial snapshot, a retained change stream and a version-guarded merge | Continuous capture; 15-minute landing batches; hourly curated merge | About 5,000,000 changes (1 GB) a day; peak 2,000 per s | Curated within 3,600 s at p95 | STK-06 | CTR-01 | Replay from the retained change stream for 7 days; beyond that re-seed from a snapshot and repeat the seam procedure | DEC-01 | Assumed |
| FLW-02 | Card events to the fraud service | SYS-02 | SYS-06 | AST-02 | CAN-08 Keyed event stream, one partition per card key, version-guarded apply | Continuous | About 1,000,000,000 events (1,000 GB) a day; peak 20,000 per s (20 MB/s) | p95 within 60 s | STK-07 | CTR-02 | Replay from the retained stream; consumer offsets; a one-hour outage drains in 1,800 s | DEC-02 | Assumed |
| FLW-03 | Card events to analytics | SYS-02 | SYS-05 | AST-02 | CAN-14 Second consumer group writing hourly files to landing with offset checkpoints | Hourly | About 1,000 GB a day landed in hourly files | Landed hourly; curated daily | STK-06 | CTR-02 | Replay from the stream within 7 days; merge by event id is idempotent | DEC-03 | Assumed |
| FLW-04 | Current customer view | SYS-03 | SYS-07 | AST-03 | CAN-19 Five-minute incremental poll with a modified-since filter into a materialised view | Every 5 minutes | About 12,000 changed records (0.02 GB) a day; about 42 per poll | View age within 900 s | STK-08 | CTR-03 | Re-read from the last watermark minus a lookback; the weekly bulk export can rebuild the whole view | DEC-04 | Assumed |
| FLW-05 | CRM history to analytics | SYS-03 | SYS-05 | AST-03 | CAN-25 Daily incremental pull plus a weekly bulk export for delete detection and reconciliation | Daily at 02:00; weekly export | About 12,000 changes a day; 12,000,000 records (24 GB) in the weekly export | Daily | STK-06 | CTR-04 | Re-run the day; the weekly export re-states the base | DEC-05 | Assumed |
| FLW-06 | Settlement files to analytics and regulatory reporting | SYS-04 | SYS-05, SYS-08 | AST-04 | CAN-30 Manifest-gated load with quarantine and a merge by settlement id | On file arrival, polled every 5 minutes from 06:00 | About 2,000,000 records (2 GB) a day in one file | Published within 7,200 s of arrival | STK-06 | CTR-05 | Quarantine a bad file; request a resend (CAP-16 unknown); reload is idempotent | DEC-06 | Assumed |

**Mappings and transformation responsibility** (Step 10). Where a transformation happens is decided by DEC-07: raw data are landed unchanged and business logic runs in the target. Every contract field has a source or rule; a field with no source is an error.

| ID | Mapping | Flow | Target field | Source field or rule | Where | Transformation owner | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MAP-01 | Ledger identity | FLW-01 | entry_id, account_id | Copied from the change record | Extract | STK-06 | Assumed |
| MAP-02 | Ledger amount | FLW-01 | amount_minor, currency | Integer minor units and ISO currency copied without conversion | Extract | STK-06 | Assumed |
| MAP-03 | Ledger type | FLW-01 | entry_type, change_type | Copied; a delete becomes a tombstone change type | Load | STK-06 | Assumed |
| MAP-04 | Ledger time | FLW-01 | posted_at | Converted to UTC at capture | Extract | STK-06 | Assumed |
| MAP-05 | Ledger version | FLW-01 | source_version | Commit sequence of the change in the source log | Extract | STK-06 | Assumed |
| MAP-06 | Ledger reversal link | FLW-01 | reversal_of | Copied when present; absent otherwise | Load | STK-06 | Assumed |
| MAP-07 | Card event identity | FLW-02 | event_id, card_id, producer_sequence | Copied; the sequence is per card | Extract | STK-07 | Assumed |
| MAP-08 | Card event content | FLW-02 | event_type, amount_minor, currency, event_time | Copied; event time in UTC | Extract | STK-07 | Assumed |
| MAP-09 | Card event merchant | FLW-02 | merchant_ref | Copied when present | Load | STK-07 | Assumed |
| MAP-10 | Landed card event | FLW-03 | event_id, card_id, event_type, amount_minor, currency, event_time, producer_sequence | Copied unchanged into the raw hourly file | Load | STK-06 | Assumed |
| MAP-11 | Landed card merchant | FLW-03 | merchant_ref | Copied when present | Load | STK-06 | Assumed |
| MAP-12 | View key and segment | FLW-04 | customer_id, segment | Key copied; segment translated through the CRM segment code table | Transform in target | STK-08 | Assumed |
| MAP-13 | View preferences | FLW-04 | preferred_channel, contact_flags | Channel translated through a code table; flags copied | Transform in target | STK-08 | Assumed |
| MAP-14 | View freshness | FLW-04 | source_modified_at | Copied; used as the version | Extract | STK-08 | Assumed |
| MAP-15 | Interaction identity | FLW-05 | interaction_id, customer_id, channel | Copied | Load | STK-06 | Assumed |
| MAP-16 | Interaction outcome | FLW-05 | outcome_code, started_at, duration_s | Outcome translated through a code table; times in UTC; duration in seconds | Transform in target | STK-06 | Assumed |
| MAP-17 | Interaction version | FLW-05 | source_modified_at | Copied; used as the version | Extract | STK-06 | Assumed |
| MAP-18 | Settlement identity | FLW-06 | settlement_id, payment_ref, partner_batch_id | Copied | Load | STK-06 | Assumed |
| MAP-19 | Settlement content | FLW-06 | amount_minor, currency, settled_at, status | Amount as integer minor units; status translated through a code table | Transform in target | STK-06 | Assumed |
| MAP-20 | Manifest | FLW-06 | file_name, record_count, control_total_minor, checksum | Copied from the manifest | Extract | STK-06 | Assumed |
| MAP-21 | Evidence report | FLW-06 | control_date, flow_id, source_total_minor, target_total_minor, delta_minor, tolerance_minor, status | Computed by the reconciliation job from independent source totals | Transform in target | STK-14 | Assumed |

**Ordering, consistency, late data and atomic publication** (Step 14). Each guarantee is marked `Documented`, `Assumed` or `Unknown`; an `Unknown` one points at the open question.

| ID | Ordering line | Flow | Ordering scope | Late data policy | Atomic publication | Guarantee source | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ORD-01 | Ledger changes | FLW-01 | Per entry id in source commit order; no cross-account order is promised | A change older than the applied version is ignored; a correction arrives as a new version | A 15-minute landing batch is visible to the merge only when fully committed | Assumed | Assumed |
| ORD-02 | Card events to fraud | FLW-02 | Per card id inside one partition, provided S2 publishes in order (OQ-02) | Events up to 24 h late are applied if their sequence is newer; older ones go to the dead-letter store and are counted | Not applicable: events apply individually | Unknown | Assumed |
| ORD-03 | Card events to analytics | FLW-03 | Per event-date partition; no order inside a file | Events up to 24 h after their hour are merged into their date; later ones are quarantined and reported | An hourly file is registered only after it is fully written and checksummed | Assumed | Assumed |
| ORD-04 | Customer view | FLW-04 | Per customer id by source modified time | Each poll re-reads the last 10 minutes (lookback) to catch late commits; older arrivals are ignored | A poll's batch applies to the view in one transaction | Assumed | Assumed |
| ORD-05 | CRM history | FLW-05 | Per interaction id by source modified time | The weekly export corrects anything the daily pulls missed | A daily batch publishes to curated tables only after its reconciliation counts pass | Assumed | Assumed |
| ORD-06 | Settlement files | FLW-06 | Per file in arrival order; no order inside a file is needed because the merge is by settlement id | An earlier-dated file arriving late is processed on its merits; corrections arrive as new files | A file is published whole or not at all | Assumed | Assumed |

**Transport guarantee versus business correctness.** The transports offer at-least-once delivery at best. Business correctness (no double effect, no stale overwrite, no silent loss) comes from the idempotent merge rules in 6.11 and the reconciliation in 6.12, not from the transport.

### 6.10 D10 — Data contracts and schema compatibility plan (Step 11)

**Contracts.** One per feed, owned by the producer. Compatibility modes use the roadmap's definitions: *backward* means a new-schema reader can read old data; *forward* means an old-schema reader can read new data; *full* means both. The mode must follow from who upgrades first and whether history is replayed.

| ID | Contract | Flow | Producer | Consumers | Schema ref | Key | Required fields | Optional fields | Semantics | Compatibility mode | Upgrade order | Replays history | Notice days | Quality and delivery | Owner | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CTR-01 | Ledger change | FLW-01 | SYS-01 | SYS-05 | ledger-change v1 | entry_id | entry_id, account_id, entry_type, amount_minor, currency, posted_at, change_type, source_version | reversal_of | amount_minor is an integer in minor currency units; posted_at is UTC; an absent reversal_of means the entry is not a reversal; change_type D is a delete tombstone, not a null row | FULL_TRANSITIVE | Either | Yes | 30 | Delivered at least once, in commit order per entry; completeness checked daily | STK-02 | Assumed |
| CTR-02 | Card event | FLW-02, FLW-03 | SYS-02 | SYS-06, SYS-05 | card-event v1 | event_id | event_id, card_id, event_type, amount_minor, currency, event_time, producer_sequence | merchant_ref | amount_minor is an integer in minor currency units; event_time is UTC; producer_sequence increases by one per card; an absent merchant_ref means the merchant is not known | FULL | Producer first | Yes | 30 | At least once; per-card order if S2 guarantees it (OQ-02); p95 within 60 s to the fraud service | STK-03 | Assumed |
| CTR-03 | CRM current customer | FLW-04 | SYS-03 | SYS-07 | crm-customer v1 | customer_id | customer_id, segment, preferred_channel, source_modified_at | contact_flags | source_modified_at is UTC; a missing contact_flags means no flag is set, a null value means flags are unknown; segment is a code from the CRM code table | FORWARD | Producer first | No | 30 | Polled every 5 minutes; view age within 900 s | STK-04 | Assumed |
| CTR-04 | CRM interaction history | FLW-05 | SYS-03 | SYS-05 | crm-interaction v1 | interaction_id | interaction_id, customer_id, channel, started_at, outcome_code, source_modified_at | duration_s | started_at is UTC; duration_s is in seconds and absent when the interaction is open; outcome_code is a code from the CRM code table | FULL | Producer first | Yes | 30 | Daily incremental; weekly full export for reconciliation | STK-04 | Assumed |
| CTR-05 | Settlement record | FLW-06 | SYS-04 | SYS-05, SYS-08 | settlement-record v1 | settlement_id | settlement_id, payment_ref, amount_minor, currency, settled_at, status, partner_batch_id | none | amount_minor is an integer in minor currency units; settled_at is UTC; a missing status is invalid and the file is quarantined | BACKWARD_TRANSITIVE | Consumers first | Yes | 30 | One file a day; complete only if the manifest agrees | STK-05 | Assumed |
| CTR-06 | Settlement manifest | FLW-06 | SYS-04 | SYS-05 | settlement-manifest v1 | file_name | file_name, record_count, control_total_minor, checksum | none | control_total_minor is the sum of amount_minor in the file, in minor currency units, per currency; a missing checksum means the manifest is incomplete (CAP-15 unknown) | BACKWARD | Consumers first | No | 30 | Arrives with or before the file | STK-05 | Assumed |
| CTR-07 | Reconciliation evidence report | FLW-01, FLW-06 | SYS-05 | SYS-08 | recon-evidence v1 | control_date | control_date, flow_id, source_total_minor, target_total_minor, delta_minor, tolerance_minor, status | none | Totals are integers in minor currency units for the control date in UTC; a missing total means the control could not run and the status is failed | BACKWARD | Consumers first | No | 30 | Issued daily; retained for the period set by OQ-07 | STK-14 | Assumed |

**Change classification.** The checker derives backward and forward effect from the kind of change, flags semantic changes separately (a change in meaning is never visible to a structural check), and tests the result against the contract's mode. `?` means the effect depends on consumer evidence.

| ID | Change | Contract | Change kind | Semantic | Backward | Forward | Class | Allowed by mode | Action | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CHG-01 | Add an optional merchant_category to card events | CTR-02 | add_optional | No | Y | Y | Full | Yes | Accept and announce; no consumer change needed | Assumed |
| CHG-02 | Add a required merchant_category to card events | CTR-02 | add_required | No | N | Y | Forward only | No | Staged: add as optional first and promote only when every consumer confirms | Assumed |
| CHG-03 | Rename card_id to payment_card_id | CTR-02 | rename | No | N | N | Breaking | No | New version with both fields during the notice period (expand and contract) | Assumed |
| CHG-04 | Widen amount_minor from a 32-bit to a 64-bit integer | CTR-01 | widen_type | No | Y | N | Backward only | No | Consumer-first staged rollout under a new version | Assumed |
| CHG-05 | Change amount_minor from minor units to major units, same name and type | CTR-01 | unit_change | Yes | Y | Y | Semantic break | No | New version with a new field name; reject the in-place change; consumers migrate during the notice period | Assumed |
| CHG-06 | Remove the optional reversal_of | CTR-01 | remove_optional | No | Y | ? | Needs consumer evidence | No | Consumer impact analysis first, then staged removal after notice | Assumed |
| CHG-07 | Add the entry type chargeback | CTR-01 | add_enum_value | No | Y | ? | Needs consumer evidence | No | Check that every consumer tolerates unknown values, then a staged release | Assumed |
| CHG-08 | Make an optional partner field required | CTR-05 | optional_to_required | No | N | Y | Forward only | No | Reject until the partner supplies a default; agree a new version with the partner | Assumed |
| CHG-09 | Add an optional field to the CRM customer record | CTR-03 | add_optional | No | Y | Y | Full | Yes | Accept; the tolerant reader ignores unknown fields | Assumed |
| CHG-10 | Reinterpret outcome code closed as resolved | CTR-04 | meaning_change | Yes | Y | Y | Semantic break | No | New version with a new code; consumers migrate during the notice period | Assumed |
| CHG-11 | Narrow duration_s from 64 to 32 bits | CTR-04 | narrow_type | No | N | N | Breaking | No | Reject in place; use a staged new version if it is ever needed | Assumed |
| CHG-12 | Add an optional control_date to the manifest | CTR-06 | add_optional | No | Y | Y | Full | Yes | Accept; consumers upgrade first | Assumed |

**Enforcement points and process.** Contracts are checked at three points: at publication (a producer cannot publish a version the registry rejects), at ingestion (a record that fails its contract goes to quarantine with its classification label), and in the change pipeline (a proposed change is classified as above before it can merge). A structural check cannot see CHG-05 or CHG-10, so a change that touches units, codes or time conventions needs a named reviewer from the consuming teams and a semantic test dataset, whatever the registry says. Breaking changes need 30 days' notice (STD-04, REQ-11); a deprecated field stays supported until usage reaches zero or the notice period ends, whichever is later.

### 6.11 D11 — Idempotency and deduplication strategy (Step 12)

Identity is a design input. For each flow the table names the business key, the event identity, the version used to refuse stale updates, the deduplication scope and window (which must be at least the replay horizon, or a replay can duplicate), and the merge rule. State size is `events per second × window × key bytes`.

| ID | Identity rule | Flow | Business key | Event id | Version field | Dedup scope | Dedup window h | Key bytes | Events per s | State GB | Merge rule | Side effects | Replay horizon h | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IDM-01 | Ledger change identity | FLW-01 | entry_id | change_id | source_version | entry_id | 168 | 24 | WLD-01:peak | 29.03 | upsert-version-guard | None: the load is analytical only | 168 | Assumed |
| IDM-02 | Card event identity at the fraud service | FLW-02 | event_id | event_id | producer_sequence | card_id | 24 | 16 | WLD-02:peak | 27.65 | upsert-version-guard | A fraud alert is keyed by event_id so a repeat sends no second alert | 24 | Assumed |
| IDM-03 | Card event identity in analytics | FLW-03 | event_id | event_id | producer_sequence | event_date partition | 168 | 16 | WLD-02:avg | 112.00 | append-dedup | None: the load is analytical only | 168 | Assumed |
| IDM-04 | Customer view identity | FLW-04 | customer_id | none | source_modified_at | customer_id | 24 | 12 | WLD-03:avg | 0.00 | upsert-version-guard | None: the view is read only | 24 | Assumed |
| IDM-05 | Interaction history identity | FLW-05 | interaction_id | none | source_modified_at | interaction_id | 168 | 16 | WLD-03:avg | 0.00 | upsert-version-guard | None: the load is analytical only | 168 | Assumed |
| IDM-06 | Settlement record identity | FLW-06 | settlement_id | settlement_id | none | settlement_id across all files | 720 | 16 | WLD-04:avg | 0.96 | append-dedup | The evidence report is issued once per control date | 720 | Assumed |
| IDM-07 | Settlement file identity | FLW-06 | file_name | file_name | none | file_name | 720 | 40 | 0.0000116 | 0.00 | manifest-gate | A quarantined file is never partly loaded | 720 | Assumed |

**Scenario runner.** Each scenario applies a sequence of events to a starting state under a stated rule and compares the result with what business correctness requires. A rule chosen for a flow must reproduce the expected state; a **rejected alternative** (a naive rule) must not, which is the evidence for rejecting it. State notation: `key=value@version` for upserts, `id=value` for appends, `published=…/quarantined=…` for file gates; events are `key:version:value`, `id:value` or `file:expected:actual:checksum`.

| ID | Scenario | Flow | Rule | Kind | Start state | Events | Expected final | Computed final | Outcome | Reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCN-01 | Card updates arrive in order | FLW-02 | upsert-version-guard | Normal | C1=100@1 | C1:2:90;C2:1:50 | C1=90@2;C2=50@1 | C1=90@2;C2=50@1 | Pass | Both updates apply |
| SCN-02 | A card update is delivered twice after a consumer restart | FLW-02 | upsert-version-guard | Failure | C1=90@2 | C1:2:90;C1:2:90 | C1=90@2 | C1=90@2 | Pass | The repeat changes nothing |
| SCN-03 | An older card update arrives after a newer one | FLW-02 | upsert-version-guard | Failure | C1=100@1 | C1:3:70;C1:2:90 | C1=70@3 | C1=70@3 | Pass | The stale update is refused |
| SCN-04 | The same arrival order under a last-arrival rule | FLW-02 | upsert-last-arrival | Rejected alternative | C1=100@1 | C1:3:70;C1:2:90 | C1=70@3 | C1=90@2 | Fail | The stale update overwrites the newer state |
| SCN-05 | Seven days of ledger changes are replayed after a long outage | FLW-01 | upsert-version-guard | Failure | E1=500@2;E2=300@1 | E1:1:400;E1:2:500;E2:1:300;E3:1:100 | E1=500@2;E2=300@1;E3=100@1 | E1=500@2;E2=300@1;E3=100@1 | Pass | Old versions are ignored, the missing entry is added |
| SCN-06 | A ledger hard delete is followed by a late older update | FLW-01 | upsert-version-guard | Failure | E4=50@1 | E4:3:DEL;E4:2:60 | E4=DEL@3 | E4=DEL@3 | Pass | The tombstone is kept and protects against the older update |
| SCN-07 | Landed card events are replayed under an append rule with no dedup | FLW-03 | append-naive | Rejected alternative | ev1=10 | ev1:10;ev2:20 | ev1=10;ev2=20 | ev1=10;ev1=10;ev2=20 | Fail | The replay duplicates ev1 |
| SCN-08 | Landed card events are replayed and one arrives twice, with dedup | FLW-03 | append-dedup | Failure | ev1=10 | ev1:10;ev2:20;ev2:20 | ev1=10;ev2=20 | ev1=10;ev2=20 | Pass | Each event id appears once |
| SCN-09 | A complete settlement file | FLW-06 | manifest-gate | Normal | none | F1:2000000:2000000:ok | published=F1/quarantined=- | published=F1/quarantined=- | Pass | The file publishes |
| SCN-10 | An incomplete settlement file is quarantined while a good one publishes | FLW-06 | manifest-gate | Failure | none | F2:2000000:1000000:ok;F3:2000000:2000000:ok | published=F3/quarantined=F2 | published=F3/quarantined=F2 | Pass | Only the complete file publishes |
| SCN-11 | A settlement file with a failed checksum | FLW-06 | manifest-gate | Failure | none | F4:100:100:bad | published=-/quarantined=F4 | published=-/quarantined=F4 | Pass | A count match is not enough; the checksum fails |
| SCN-12 | The incomplete file under a load-everything rule | FLW-06 | load-all | Rejected alternative | none | F2:2000000:1000000:ok | published=-/quarantined=F2 | published=F2/quarantined=- | Fail | Half a file is published as if complete |
| SCN-13 | A CRM poll overlaps and re-reads a record already applied | FLW-04 | upsert-version-guard | Normal | K1=a@1005 | K1:1005:a;K1:1006:b | K1=b@1006 | K1=b@1006 | Pass | The overlap is harmless |
| SCN-14 | The daily incremental overlaps the weekly export | FLW-05 | upsert-version-guard | Normal | I1=x@2001;I2=y@2002 | I1:2001:x;I2:2003:z;I3:2001:w | I1=x@2001;I2=z@2003;I3=w@2001 | I1=x@2001;I2=z@2003;I3=w@2001 | Pass | Existing rows are kept, newer versions win, the new row is added |

**What idempotency does not give.** Version guards stop stale overwrites only for keys that carry a version; a flow with no version (FLW-06) relies on the file gate and on reconciliation to catch a wrong replacement. Deduplication windows are finite: a replay older than its window can duplicate (the checker refuses a window shorter than the replay horizon). Side effects outside the target (alerts, evidence reports) are idempotent only because they are keyed by an identity (IDM-02, IDM-06).

### 6.12 D12 — Reconciliation and data validation plan (Step 12)

Reconciliation proves that source and target agree. No single level proves it, and each level misses something, so the plan states levels per flow, tolerances, and where independence is limited. Zero-tolerance flows (REQ-03, REQ-07, REQ-21) use a tolerance of zero for amounts in integer minor units; the tolerance is never used to absorb an unexplained difference.

| ID | Reconciliation | Flow | Level | Grain | Window | Tolerance | Independence | Frequency | Output | Owner | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REC-01 | Landed change counts against the source log range | FLW-01 | Count | table × business date | Previous business day | 0 | Independent | Daily | Count delta report | STK-14 | Assumed |
| REC-02 | Sum of amount_minor by business date, currency and entry type | FLW-01 | Total | business_date × currency × entry_type | Previous business day | 0 | Independent | Daily | Control-total report | STK-14 | Assumed |
| REC-03 | Entry id and version comparison of changed entries | FLW-01 | Key and version | entry_id × source_version | Last 24 hours | 0 | Independent | Daily | Mismatch list | STK-14 | Assumed |
| REC-04 | Debits equal credits per posting batch | FLW-01 | Domain invariant | posting batch | Previous business day | 0 | Independent | Daily | Invariant report | STK-14 | Assumed |
| REC-05 | Source ledger report against curated totals, issued as evidence | FLW-01 | Independent extract | business_date × currency | Previous business day | 0 | Independent | Daily | Evidence report (CTR-07) | STK-14 | Assumed |
| REC-06 | Producer sequence gaps per card | FLW-02 | Key and version | card_id × producer_sequence | Rolling hour | 0 | Shared logic | Hourly | Gap list | STK-11 | Assumed |
| REC-07 | Published against consumed event counts | FLW-02 | Count | partition × hour | Previous hour | 0 | Independent | Hourly | Count delta | STK-11 | Assumed |
| REC-08 | Stream offset ranges against landed file counts | FLW-03 | Count | hour × partition | Previous hour | 0 | Independent | Hourly | Delta report | STK-14 | Assumed |
| REC-09 | Stream amount totals against landed file totals | FLW-03 | Total | hour × currency | Previous hour | 0 | Independent | Hourly | Delta report | STK-14 | Assumed |
| REC-10 | Event id anti-join between the stream range and landed files | FLW-03 | Key coverage | event_id | Previous day | 0 | Independent | Daily | Missing and extra id lists | STK-14 | Assumed |
| REC-11 | Weekly full comparison of the view with the bulk export | FLW-04 | Key and version | customer_id × source_modified_at | Whole view | 0 | Independent | Weekly | Mismatch list | STK-14 | Assumed |
| REC-12 | Changed-record count against the poll log | FLW-04 | Count | day | Previous day | 0 | Shared logic | Daily | Count delta | STK-11 | Assumed |
| REC-13 | Changed CRM interactions against the daily pull log | FLW-05 | Count | day | Previous day | 0 | Shared logic | Daily | Count delta | STK-11 | Assumed |
| REC-14 | Bulk-export keys against curated keys, which detects missed deletes | FLW-05 | Key coverage | interaction_id | Whole table | 0 | Independent | Weekly | Missing and extra key lists | STK-14 | Assumed |
| REC-15 | Hash of canonicalised monthly partitions against the export | FLW-05 | Hash | monthly partition | Whole table | 0 | Independent | Weekly | Partition mismatch list | STK-14 | Assumed |
| REC-16 | Row count against the manifest count | FLW-06 | Count | file | Each file | 0 | Independent | Per file | Gate result | STK-14 | Assumed |
| REC-17 | Control total against the manifest total | FLW-06 | Total | file × currency | Each file | 0 | Independent | Per file | Gate result | STK-14 | Assumed |
| REC-18 | Settlement payment references against ledger entries | FLW-06 | Key coverage | payment_ref | Previous day | 0 | Independent | Daily | Unmatched list | STK-14 | Assumed |
| REC-19 | Partner statement totals against loaded totals, issued as evidence | FLW-06 | Independent extract | settlement date × currency | Previous day | 0 | Independent | Daily | Evidence report (CTR-07) | STK-14 | Assumed |
| REC-20 | Field-by-field comparison of a 1% sample of settlement rows with the partner file | FLW-06 | Record comparison | settlement_id | Per file sample | 0 | Independent | Per file | Sample diff | STK-14 | Assumed |
| REC-21 | Field-by-field comparison of a daily sample of 10,000 ledger entries with the source | FLW-01 | Record comparison | entry_id | Previous day sample | 0 | Independent | Daily | Sample diff | STK-14 | Assumed |
| REC-22 | Field-by-field comparison of a 1% sample of the view with the bulk export | FLW-04 | Record comparison | customer_id | Weekly sample | 0 | Independent | Weekly | Sample diff | STK-14 | Assumed |
| REC-23 | Field-by-field comparison of a weekly sample of fraud-store records with the landed events | FLW-02 | Record comparison | event_id | Weekly sample | 0 | Independent | Weekly | Sample diff | STK-14 | Assumed |

**What each level detects.** `Y` detects, `P` may detect depending on scope and logic, `N` does not. This is the matrix the coverage lines and the injection tests below are checked against.

| ID | Defect class | Count | Total | Hash | Key coverage | Key and version | Record comparison | Domain invariant | Independent extract | Sample | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DET-01 | A record applied twice | Y | Y | Y | P | P | Y | P | Y | P | Assumed |
| DET-02 | A source record missing in the target | Y | Y | Y | Y | Y | Y | P | Y | P | Assumed |
| DET-03 | An extra record in the target | Y | Y | Y | Y | Y | Y | P | Y | P | Assumed |
| DET-04 | Accounts swapped between two records, totals unchanged | N | N | Y | N | N | Y | P | P | P | Assumed |
| DET-05 | An old version overwrites newer state | N | P | P | N | Y | Y | P | P | P | Assumed |
| DET-06 | A consistently wrong transformation on both sides | N | P | N | N | N | N | P | P | N | Assumed |
| DET-07 | A source delete not applied in the target | Y | P | Y | Y | Y | Y | P | Y | P | Assumed |
| DET-08 | A duplicated side effect outside the target | N | N | N | N | N | N | N | P | N | Assumed |
| DET-09 | A value drifts in one field | N | Y | Y | N | N | Y | P | Y | P | Assumed |
| DET-10 | A truncated or incomplete file | Y | Y | Y | P | P | Y | P | Y | P | Assumed |
| DET-11 | An offsetting duplicate and omission | N | P | Y | Y | Y | Y | P | P | P | Assumed |

**Injection tests.** Each test builds a small source and target with one defect and applies one level exactly as written (`key:account:amount`, amounts in minor units). The result must equal the stated expectation and must not contradict the matrix above.

| ID | Injection | Flow | Defect | Level | Source rows | Target rows | Detected | Expected | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INJ-01 | A duplicate row, count | FLW-06 | DET-01 | Count | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-20:25000;T-101:A-20:25000;T-102:A-30:5000 | Yes | Yes | Derived |
| INJ-02 | A duplicate row, total | FLW-06 | DET-01 | Total | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-20:25000;T-101:A-20:25000;T-102:A-30:5000 | Yes | Yes | Derived |
| INJ-03 | A missing row, count | FLW-06 | DET-02 | Count | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-20:25000 | Yes | Yes | Derived |
| INJ-04 | A missing row, total | FLW-01 | DET-02 | Total | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-20:25000 | Yes | Yes | Derived |
| INJ-05 | A missing row, key coverage | FLW-06 | DET-02 | Key coverage | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-20:25000 | Yes | Yes | Derived |
| INJ-06 | An extra row, key coverage | FLW-06 | DET-03 | Key coverage | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000;T-103:A-40:100 | Yes | Yes | Derived |
| INJ-07 | Swapped accounts, count | FLW-01 | DET-04 | Count | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-30:25000;T-102:A-20:5000 | No | No | Derived |
| INJ-08 | Swapped accounts, total | FLW-01 | DET-04 | Total | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-30:25000;T-102:A-20:5000 | No | No | Derived |
| INJ-09 | Swapped accounts, key coverage | FLW-01 | DET-04 | Key coverage | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-30:25000;T-102:A-20:5000 | No | No | Derived |
| INJ-10 | Swapped accounts, record comparison | FLW-01 | DET-04 | Record comparison | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-30:25000;T-102:A-20:5000 | Yes | Yes | Derived |
| INJ-11 | A drifted amount, count | FLW-06 | DET-09 | Count | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-20:26000;T-102:A-30:5000 | No | No | Derived |
| INJ-12 | A drifted amount, total | FLW-06 | DET-09 | Total | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-20:26000;T-102:A-30:5000 | Yes | Yes | Derived |
| INJ-13 | A drifted amount, key coverage | FLW-06 | DET-09 | Key coverage | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-20:26000;T-102:A-30:5000 | No | No | Derived |
| INJ-14 | A missed delete, key coverage | FLW-05 | DET-07 | Key coverage | T-100:A-10:10000;T-101:A-20:25000 | T-100:A-10:10000;T-101:A-20:25000;T-103:A-40:100 | Yes | Yes | Derived |
| INJ-15 | A truncated file, count | FLW-06 | DET-10 | Count | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-20:25000 | Yes | Yes | Derived |
| INJ-16 | An offsetting duplicate and omission, count | FLW-01 | DET-11 | Count | T-200:A-1:10000;T-201:A-2:10000;T-202:A-3:20000 | T-200:A-1:10000;T-200:A-1:10000;T-202:A-3:20000 | No | No | Derived |
| INJ-17 | An offsetting duplicate and omission, key coverage | FLW-01 | DET-11 | Key coverage | T-200:A-1:10000;T-201:A-2:10000;T-202:A-3:20000 | T-200:A-1:10000;T-200:A-1:10000;T-202:A-3:20000 | Yes | Yes | Derived |
| INJ-18 | Swapped accounts, hash of canonicalised rows | FLW-05 | DET-04 | Hash | T-100:A-10:10000;T-101:A-20:25000;T-102:A-30:5000 | T-100:A-10:10000;T-101:A-30:25000;T-102:A-20:5000 | Yes | Yes | Derived |
| INJ-19 | An offsetting duplicate and omission, total | FLW-01 | DET-11 | Total | T-200:A-1:10000;T-201:A-2:10000;T-202:A-3:20000 | T-200:A-1:10000;T-200:A-1:10000;T-202:A-3:20000 | No | No | Derived |

INJ-07 to INJ-09 are the instructive set: counts, totals and key coverage all pass while two accounts are wrong, and only a field-level comparison (INJ-10) or a hash of the full rows (INJ-18) catches it. INJ-16 and INJ-19 show a duplicate and an omission cancelling in both count and total.

**Coverage matrix per flow.** The checker applies each flow's chosen levels to the matrix: *detected* means at least one chosen level is `Y`; *partial only* means the best level is `P`; *undetected* means no chosen level can find the class. Every undetected class needs a compensating note.

| ID | Coverage line | Flow | Controls | Detected | Partial only | Undetected | Compensating note | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| COV-01 | Ledger to analytics | FLW-01 | Count, Total, Key and version, Record comparison, Domain invariant, Independent extract | DET-01, DET-02, DET-03, DET-04, DET-05, DET-07, DET-09, DET-10, DET-11 | DET-06, DET-08 | none | Consistently wrong transformations (DET-06) and external side effects (DET-08) can pass; the independent extract (REC-05) and the quarterly review of the transformation rules by the ledger owner reduce but do not remove this, and the flow has no external side effects | Derived |
| COV-02 | Card events to fraud | FLW-02 | Count, Key and version, Record comparison | DET-01, DET-02, DET-03, DET-04, DET-05, DET-07, DET-09, DET-10, DET-11 | none | DET-06, DET-08 | A consistently wrong feature calculation is outside what these controls compare; a duplicated alert is caught only by the fraud service's own decision audit; value drift and swapped accounts are caught by the weekly sample comparison against the landed events (REC-23) | Derived |
| COV-03 | Card events to analytics | FLW-03 | Count, Total, Key coverage | DET-01, DET-02, DET-03, DET-07, DET-09, DET-10, DET-11 | DET-05, DET-06 | DET-04, DET-08 | The landed copy is unmapped (MAP-10), so swapped accounts cannot occur there; the flow has no external side effects | Derived |
| COV-04 | Current customer view | FLW-04 | Count, Key and version, Record comparison | DET-01, DET-02, DET-03, DET-04, DET-05, DET-07, DET-09, DET-10, DET-11 | none | DET-06, DET-08 | A consistently wrong code-table mapping would pass; the contact-centre owner reviews the segment and channel tables quarterly; the view has no external side effects | Derived |
| COV-05 | CRM history to analytics | FLW-05 | Count, Hash, Key coverage | DET-01, DET-02, DET-03, DET-04, DET-07, DET-09, DET-10, DET-11 | DET-05 | DET-06, DET-08 | A consistently wrong code-table mapping would pass; the code tables are reviewed quarterly; the flow has no external side effects | Derived |
| COV-06 | Settlement files | FLW-06 | Count, Total, Key coverage, Record comparison, Independent extract | DET-01, DET-02, DET-03, DET-04, DET-05, DET-07, DET-09, DET-10, DET-11 | DET-06, DET-08 | none | Wrong business logic shared by the load and the checks is the main remaining risk; the partner statement (REC-19) is the independent source | Derived |

### 6.13 D13 — Failure-mode and recovery matrix (Step 13)

Every component is listed, including the scheduler, the credential store and the contract registry, and every component has at least one failure scenario with detection, data impact, recovery, the idempotency and reconciliation needed to make recovery safe, an owner, and the evidence that the behaviour was validated.

| ID | Component | Flows | Owner | Evidence |
| --- | --- | --- | --- | --- |
| CMP-01 | Change reader on the ledger log | FLW-01 | STK-11 | Assumed |
| CMP-02 | Event stream (broker) | FLW-01, FLW-02, FLW-03 | STK-11 | Assumed |
| CMP-03 | Fraud stream consumer | FLW-02 | STK-07 | Assumed |
| CMP-04 | Landing store | FLW-01, FLW-03, FLW-05, FLW-06 | STK-06 | Assumed |
| CMP-05 | Scheduler and orchestrator | FLW-03, FLW-04, FLW-05, FLW-06 | STK-11 | Assumed |
| CMP-06 | Credential and secret store | all | STK-10 | Assumed |
| CMP-07 | Contract registry and change pipeline | all | STK-12 | Assumed |
| CMP-08 | CRM API extractor | FLW-04, FLW-05 | STK-11 | Assumed |
| CMP-09 | File arrival detector and manifest validator | FLW-06 | STK-11 | Assumed |
| CMP-10 | Dead-letter and quarantine store | all | STK-11 | Assumed |
| CMP-11 | Reconciliation job | all | STK-14 | Assumed |
| CMP-12 | Monitoring and alerting | all | STK-11 | Assumed |
| CMP-13 | Materialised customer view store | FLW-04 | STK-08 | Assumed |

| ID | Failure scenario | Component | Flow | Detection | Data impact | Recovery | Idempotency need | Reconciliation need | Owner | Validation evidence | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FMX-01 | The ledger log is purged before the reader catches up | CMP-01 | FLW-01 | Reader reports a missing position; lag alert | A gap of unread changes | Re-seed from a snapshot, then resume the stream at the seam | Version-guarded merge makes the overlap safe (SCN-05) | Key and version comparison for the gap (REC-03) | STK-11 | DRL-01 | Assumed |
| FMX-02 | A stream partition leader is lost | CMP-02 | FLW-02 | Broker health alert; consumer lag rises | A short delay; no loss with replication factor 3 | Leader election; consumers resume from committed offsets | Version-guarded apply (SCN-02) | Hourly published against consumed counts (REC-07) | STK-11 | SCN-02 | Assumed |
| FMX-03 | The fraud consumer crashes after applying an event but before committing its offset | CMP-03 | FLW-02 | Redelivery seen after restart | One event applied twice | Restart from the committed offset | Version-guarded apply and alert keyed by event id (SCN-02) | Sequence gap and count checks (REC-06, REC-07) | STK-07 | SCN-02 | Assumed |
| FMX-04 | The fraud consumer is down for one hour | CMP-03 | FLW-02 | Lag and absence alerts within 30 s | A backlog of 72 million events | Scale to 60,000 events per second; drain in 1,800 s | Version-guarded apply | Count check after the drain (REC-07) | STK-07 | LAG-01 | Assumed |
| FMX-05 | The landing store is unavailable during an hourly write | CMP-04 | FLW-03 | Write errors; missing-file alert | The hour is not published | Hold offsets; retry; re-run the hour | Merge by event id (SCN-08) | Offsets against files (REC-08) | STK-06 | SCN-08 | Assumed |
| FMX-06 | The scheduler misses the daily CRM pull | CMP-05 | FLW-05 | Absence alert at the deadline | A day of CRM changes is late | Manual trigger; the run is idempotent | Version-guarded merge (SCN-14) | Daily count against the pull log (REC-13) | STK-11 | DRL-02 | Assumed |
| FMX-07 | The CRM credential expires | CMP-06 | FLW-04 | Authentication errors; expiry warning 14 days earlier | The view stops refreshing and becomes stale | Rotate the secret; resume from the watermark | Version-guarded merge (SCN-13) | Weekly full comparison (REC-11) | STK-10 | DRL-02 | Assumed |
| FMX-08 | The contract registry is unavailable at publication | CMP-07 | FLW-02 | Publication validation errors | No new versions can be published; existing flows continue on cached schemas | Fail closed for new versions, open for existing ones; restore the registry | Not applicable | Not applicable | STK-12 | CHG-02 | Assumed |
| FMX-09 | The CRM answers with a rate-limit response | CMP-08 | FLW-04 | Error-rate alert on the extractor | A delayed poll | Bounded retry with backoff (RTY-01), then wait for the next poll | Version-guarded merge (SCN-13) | Daily count against the poll log (REC-12) | STK-11 | RTY-01 | Assumed |
| FMX-10 | A CRM page times out after the server returned data | CMP-08 | FLW-05 | Timeout alert | A page may be fetched twice | Re-request the page from the cursor | Version-guarded merge (SCN-14) | Daily count against the pull log (REC-13) | STK-11 | SCN-14 | Assumed |
| FMX-11 | A settlement file arrives incomplete | CMP-09 | FLW-06 | Manifest count mismatch | No load; the file is quarantined | Quarantine, alert, request a resend if available (CAP-16 unknown) | Merge by settlement id (SCN-10) | Count and total against the manifest (REC-16, REC-17) | STK-11 | SCN-10 | Assumed |
| FMX-12 | The settlement file does not arrive | CMP-09 | FLW-06 | Absence alert at 07:00 | Settlement is late | Escalate to the partner; never load the previous day's file | Not applicable | Daily partner statement (REC-19) | STK-05 | DRL-03 | Assumed |
| FMX-13 | A card event cannot be deserialised | CMP-10 | FLW-02 | Dead-letter depth alert | One event is unprocessed | Bounded retries (RTY-02), then dead-letter and continue; replay after a fix | Version-guarded apply on replay | Sequence gap check (REC-06) | STK-11 | RTY-02 | Assumed |
| FMX-14 | The reconciliation job fails silently | CMP-11 | all | Absence alert on the missing daily report | Defects go unseen | Alert, manual run, root-cause fix | Not applicable | Backfill the missed days | STK-14 | DRL-03 | Assumed |
| FMX-15 | The monitoring system itself is down | CMP-12 | all | Heartbeat from an independent channel | Blind to every other failure | Secondary heartbeat; manual checks until restored | Not applicable | Not applicable | STK-11 | DRL-02 | Assumed |
| FMX-16 | The view store fails | CMP-13 | FLW-04 | Health check | Agents see an unavailable or stale view | Rebuild from the bulk export, then catch up by poll | Version-guarded merge (SCN-13) | Weekly full comparison (REC-11) | STK-08 | AVC-02 | Assumed |
| FMX-17 | A structurally valid change alters the meaning of a field | CMP-07 | FLW-01 | Semantic test dataset fails in the change pipeline | Wrong amounts if released | Block the release; publish a new version (CHG-05) | Not applicable | Sample record comparison (REC-21) | STK-12 | CHG-05 | Assumed |
| FMX-18 | A stream offset reset replays events into analytics | CMP-02 | FLW-03 | Count mismatch against offsets | Duplicate landed events | Dedup on merge; re-run the hour | Merge by event id (SCN-08) | Offsets against files (REC-08) | STK-06 | SCN-08 | Assumed |

### 6.14 D14 — Security and governance considerations (Step 15)

**Stores and zones.** Classification is attached at the source contract and carried into every store, including the landing zone and the dead-letter and quarantine store, because those are where unlabelled personal and financial data tend to accumulate.

| ID | Store or zone | Holds | Classification | Retention | Encryption | Residency | Owner | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| STR-01 | Landing zone (raw, restricted) | AST-01, AST-02, AST-03, AST-04 | Restricted: personal and financial | Raw copy for 90 days (assumption pending OQ-08) | At rest and in transit | In the stated jurisdiction | STK-06 | Assumed |
| STR-02 | Dead-letter and quarantine store | AST-01, AST-02, AST-03, AST-04 | Restricted: personal and financial | 30 days, then deleted or reprocessed | At rest and in transit | In the stated jurisdiction | STK-11 | Assumed |
| STR-03 | Event stream | AST-01, AST-02 | Restricted: financial | 7 days | At rest and in transit | In the stated jurisdiction | STK-11 | Assumed |
| STR-04 | Curated tables | AST-01, AST-02, AST-03, AST-04 | Confidential, with attribute labels | Per retention class set in module 2D.10 | At rest and in transit | In the stated jurisdiction | STK-06 | Assumed |
| STR-05 | Customer view store | AST-03 | Restricted: personal | Current state only; deletes honoured | At rest and in transit | In the stated jurisdiction | STK-08 | Assumed |
| STR-06 | Reconciliation evidence store | none | Internal: control totals only | Set by OQ-07 | At rest and in transit | In the stated jurisdiction | STK-14 | Assumed |

| ID | Control | Flow | Requirement | Mechanism | Owner | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-01 | One service identity per flow with least privilege | all | REQ-17 | Read-only on the replica, log or API; write only to the flow's landing prefix; no shared credentials | STK-10 | Assumed |
| SEC-02 | Secrets in a managed store with rotation | all | REQ-17 | Rotation at most every 90 days; an expiry warning 14 days ahead | STK-10 | Assumed |
| SEC-03 | Encryption on every hop and in every store | all | REQ-18 | Transport encryption between all components; encryption at rest in landing, dead-letter, stream, curated and view stores | STK-10 | Assumed |
| SEC-04 | Classification carried with the data | all | REQ-19 | Label in the contract, copied into every message, file and table, including dead-letter payloads | STK-10 | Assumed |
| SEC-05 | Residency | all | REQ-16 | No store, replica or sink outside the stated jurisdiction; sinks reviewed before a flow is added | STK-10 | Assumed |
| SEC-06 | Lineage record per run | all | REQ-20 | Source, contract version, target, counts and reconciliation result written for each run | STK-12 | Assumed |
| SEC-07 | Access audit on landing and dead-letter stores | all | REQ-19 | Reads of restricted data are logged and reviewed monthly | STK-10 | Assumed |
| SEC-08 | Dead-letter payload handling | all | REQ-19 | Access limited to the integration on-call; payloads expire at 30 days | STK-11 | Assumed |
| SEC-09 | Reconciliation evidence integrity | FLW-01 | REQ-15 | Reports are write-once and hashed so an audit can show they were not altered | STK-14 | Assumed |
| SEC-10 | Contract change approval | all | REQ-11 | A breaking change needs producer approval, consumer sign-off and 30 days' notice before it merges | STK-12 | Assumed |

### 6.15 D15 — Operational validation requirements (Step 16)

Alerts exist for absence and staleness as well as errors, because a flow that silently stops produces no error. Every alert has an owner and an action.

| ID | Signal | Flow | Kind | Threshold | Alert | Owner | Action | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OPS-01 | Age of the newest curated ledger change | FLW-01 | Freshness | Over 2,700 s (75% of the 3,600 s target) | Page the integration on-call | STK-11 | Check the change reader, stream lag and landing writes; follow the lag runbook | Assumed |
| OPS-02 | Landing batches received | FLW-01 | Absence | No batch for 20 minutes | Page the integration on-call | STK-11 | Check the change reader heartbeat and source connectivity; start recovery if the log position is lost | Assumed |
| OPS-03 | Daily control-total delta | FLW-01 | Reconciliation | Any non-zero delta | Open an exception for the compliance lead | STK-14 | Run the key-and-version comparison, locate the difference, record the cause and the repair | Assumed |
| OPS-04 | Change reader lag | FLW-01 | Lag | Over 600 s | Notify the integration on-call | STK-11 | Check source write rate against reader capacity; add capacity if the backlog is growing | Assumed |
| OPS-05 | Fraud event age at the fraud store | FLW-02 | Freshness | p95 over 45 s (75% of 60 s) | Page the integration on-call and notify fraud operations | STK-11 | Check consumer lag and partition skew; scale the consumer | Assumed |
| OPS-06 | Events consumed per minute | FLW-02 | Absence | None for 30 s | Page the integration on-call | STK-11 | Check broker and consumer health; start the outage runbook | Assumed |
| OPS-07 | Producer sequence gaps per card | FLW-02 | Reconciliation | Any gap | Open an exception | STK-11 | Check whether the source skipped or the pipeline lost events; replay the range | Assumed |
| OPS-08 | Dead-letter depth | FLW-02 | Error | Above zero for 10 minutes | Notify the integration on-call | STK-11 | Inspect the payload, fix the cause, replay after the fix | Assumed |
| OPS-09 | Hourly landing file age | FLW-03 | Freshness | Hour file more than 20 minutes late | Notify the integration on-call | STK-11 | Check the consumer group, landing writes and offsets | Assumed |
| OPS-10 | Hourly files landed | FLW-03 | Absence | No file for 2 hours | Page the integration on-call | STK-11 | Check the consumer group and the stream; restart and re-run the missing hours | Assumed |
| OPS-11 | Hourly count and total delta | FLW-03 | Reconciliation | Any non-zero delta | Open an exception for the compliance lead | STK-14 | Compare offsets with files; identify missing or extra events; re-run the hour | Assumed |
| OPS-12 | Age of the oldest record in the view | FLW-04 | Freshness | Over 675 s (75% of 900 s) | Notify the integration on-call and the contact-centre owner | STK-11 | Check the poller, credentials and the CRM rate-limit state | Assumed |
| OPS-13 | Successful polls | FLW-04 | Absence | None for 15 minutes | Page the integration on-call | STK-11 | Check scheduler, credential expiry and CRM availability | Assumed |
| OPS-14 | Weekly view-to-export mismatch count | FLW-04 | Reconciliation | Any mismatch | Open an exception | STK-14 | Review the mismatches, repair the view, record the cause | Assumed |
| OPS-15 | Daily CRM pull completion | FLW-05 | Freshness | More than 2 hours after 02:00 | Notify the integration on-call | STK-11 | Check scheduler and API errors; trigger a manual run | Assumed |
| OPS-16 | Weekly bulk export received | FLW-05 | Absence | Not received by Monday 06:00 | Notify the integration on-call and the CRM owner | STK-11 | Contact the CRM owner; request the export; hold delete reconciliation until it arrives | Assumed |
| OPS-17 | Weekly delete drift | FLW-05 | Reconciliation | Any key present in curated tables but not in the export | Open an exception | STK-14 | Apply the deletes after review; record the cause | Assumed |
| OPS-18 | Settlement file age after arrival | FLW-06 | Freshness | Not published within 5,400 s (75% of 7,200 s) | Page the integration on-call | STK-11 | Check validation, quarantine and load; escalate before the deadline | Assumed |
| OPS-19 | Settlement file arrival | FLW-06 | Absence | No file by 07:00 | Notify the partner owner and the integration on-call | STK-05 | Contact the partner; do not load a previous file | Assumed |
| OPS-20 | Manifest or daily total mismatch | FLW-06 | Reconciliation | Any mismatch | Quarantine the file and open an exception | STK-14 | Inspect the quarantined file; request a resend or a corrected file; record the outcome | Assumed |
| OPS-21 | Daily record count against the trailing seven-day mean | all | Volume | More than 30% above or below | Notify the integration on-call | STK-11 | Check whether the source volume changed or a flow dropped data | Assumed |

**Failure drills.** Each drill has measurable pass criteria; a failed criterion means the recovery design is not yet proven.

| ID | Failure drill | Flow | Scenario | Pass criteria | Frequency | Owner | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DRL-01 | Lose the ledger log position and re-seed | FLW-01 | FMX-01 | Re-seed completes within 8 hours; control-total delta is 0; no duplicate rows in curated tables | Twice a year | STK-11 | Assumed |
| DRL-02 | Expire the CRM credential and miss a scheduled run | FLW-04 | FMX-07 | The expiry warning fires at least 14 days ahead; the missed run is detected within 15 minutes; recovery within 4 hours; view age back under 900 s | Twice a year | STK-11 | Assumed |
| DRL-03 | Deliver an incomplete settlement file and omit the next one | FLW-06 | FMX-11 | The incomplete file is quarantined within 10 minutes; nothing partial is published; the absence alert fires by 07:05; alerts are acknowledged within 15 minutes | Quarterly | STK-05 | Assumed |
| DRL-04 | Take the fraud consumer down for one hour | FLW-02 | FMX-04 | Zero events lost; the backlog drains within 1,800 s; no duplicate alerts; the lag alert fires within 30 s | Twice a year | STK-07 | Assumed |

### 6.16 D16 — Architecture trade-off and risk register (Step 19)

| ID | Risk | Likelihood | Impact | Score | Rating | Mitigation | Owner | Trigger | Decision | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RSK-01 | The CRM API has no modified-since filter or the quota is too small (CAP-10, CAP-11), so the freshness targets cannot be met | 3 | 4 | 12 | Medium | Test the API before build (OQ-03, OQ-04); the fallbacks are push notifications or a managed connector | STK-04 | The API review or the first quota test | DEC-04 | Open |
| RSK-02 | The ledger log is retained for too short a time to recover a stalled reader (CAP-04) | 3 | 4 | 12 | Medium | Confirm retention (OQ-01); run the re-seed drill (DRL-01); size the change stream retention to 7 days | STK-02 | The re-seed drill or a reader stall over four hours | DEC-01 | Open |
| RSK-03 | The cards platform does not publish in order per card (CAP-07), so per-card ordering fails | 3 | 5 | 15 | High | Confirm with the cards owner (OQ-02); the version guard (SCN-03) protects state but not alert timing | STK-03 | The ordering test result | DEC-02 | Open |
| RSK-04 | The partner manifest has no checksum (CAP-15), so corruption would pass the count check | 3 | 4 | 12 | Medium | Confirm with the partner (OQ-05); add a record-level sample comparison (REC-20) as a compensating control | STK-05 | The manifest review | DEC-06 | Open |
| RSK-05 | Reconciliation shares transformation logic with the load, so a common error passes both | 3 | 4 | 12 | Medium | Independent source totals (REC-05, REC-19); quarterly rule review | STK-14 | A rule change in the transformation | DEC-07 | Open |
| RSK-06 | A replay older than a dedup window duplicates data | 2 | 4 | 8 | Medium | Windows set at or above the replay horizon (IDM table); the checker refuses a shorter window | STK-11 | A change to retention or replay horizon | DEC-03 | Open |
| RSK-07 | A hot key skews a stream partition | 2 | 3 | 6 | Low | Partition by card (STM-01); monitor partition share; the skew check fails above 5 MB/s | STK-11 | A key exceeds 1% of traffic | DEC-02 | Open |
| RSK-08 | A semantic change passes the structural contract check | 3 | 5 | 15 | High | A semantic test dataset and a named consumer reviewer for unit, code and time changes (CHG-05, CHG-10) | STK-12 | Any change that touches units or codes | DEC-01 | Open |
| RSK-09 | Reconciliation evidence retention is undefined (OQ-07) | 4 | 3 | 12 | Medium | Compliance sets the period before the first audit | STK-14 | The first audit request | DEC-06 | Open |
| RSK-10 | The raw copy in the landing zone is kept longer than needed | 3 | 4 | 12 | Medium | 90-day default pending OQ-08; automatic expiry; access audit | STK-10 | A retention decision from privacy | DEC-07 | Open |
| RSK-11 | Two decisions change winner under a simplicity-heavy weighting | 3 | 3 | 9 | Medium | Recorded as conditional; decide with the operations review (OQ-06) | STK-12 | The operations review | DEC-02 | Open |

| ID | Trade-off | Accepted cost | Benefit | Revisit trigger | Decision |
| --- | --- | --- | --- | --- | --- |
| TRD-01 | Log-based capture of the ledger | Needs log access and a seam procedure | No scans of the ledger and changes within minutes | The log proves unavailable or too short (OQ-01) | DEC-01 |
| TRD-02 | A keyed stream for fraud | One more component to operate | 11 s freshness against 336 s for the baseline | The operations review prefers a managed service (OQ-06) | DEC-02 |
| TRD-03 | A materialised customer view instead of live federation | A copy of personal data in another store | Within the CRM rate limit and 99.85% availability against 99.351% | The CRM offers a bulk read path with a higher limit | DEC-04 |
| TRD-04 | A weekly export for delete detection | A deleted record may remain in analytics for up to seven days | Deletes are found without relying on an unknown API feature | The API shows deletes (CAP-13) | DEC-05 |
| TRD-05 | A manifest gate on settlement files | A bad file delays settlement until it is repaired | No partial or corrupt load of financial records | The partner provides a corrected resend within the deadline | DEC-06 |
| TRD-06 | Land raw data, transform in the target | Raw personal and financial data are kept for 90 days | Any load can be re-derived and audited | Privacy shortens the raw retention (OQ-08) | DEC-07 |

**Open questions.** Each unknown capability is named by an open question.

| ID | Open question | Owner | Needed by | Blocks | Evidence that settles it | Status |
| --- | --- | --- | --- | --- | --- | --- |
| OQ-01 | How long does the ledger keep its readable log, and is it long enough to recover a stalled reader? | STK-02 | Before DEC-01 is final | CAP-04, DEC-01 | Log retention setting and the observed peak log volume | Open |
| OQ-02 | Does the cards platform publish events in order for one card? | STK-03 | Before DEC-02 is final | CAP-07, DEC-02 | An ordering test on a sample of cards and the platform's documentation | Open |
| OQ-03 | What is the CRM's daily request quota? | STK-04 | Before DEC-04 is final | CAP-10, DEC-04, DEC-05 | The vendor agreement and a measured quota test | Open |
| OQ-04 | Does the CRM API support a modified-since filter, visible deletes or change notifications? | STK-04 | Before DEC-04 is final | CAP-11, CAP-13, CAP-17, DEC-04, DEC-05 | The API documentation and a test against a sandbox | Open |
| OQ-05 | Does the settlement manifest carry a record count and a checksum, and can the partner resend a file? | STK-05 | Before DEC-06 is final | CAP-15, CAP-16, DEC-06 | A sample manifest and the partner's written answer | Open |
| OQ-06 | Can the integration team operate a self-managed stream and connectors, or is a managed service needed? | STK-11 | Before DEC-02 is final | DEC-02, DEC-05 | A staffing review and an on-call readiness walkthrough | Open |
| OQ-07 | How long must reconciliation evidence be retained for audit? | STK-14 | Before the first audit | REQ-15, STR-06, DEC-06 | Written direction from compliance | Open |
| OQ-08 | How long may the raw copy in the landing zone be kept? | STK-10 | Before DEC-07 is final | STR-01, DEC-07 | A privacy decision on raw retention | Open |

### 6.17 D17 — Validation, completion status and final recommendation (Steps 18 and 20)

#### Normal and failure walkthroughs

Each walkthrough names the evidence rows that show the outcome. A `Pass` is not allowed when a cited calculation fails; an outcome with a residual risk says so.

| ID | Walkthrough | Flow | Kind | Category | Outcome | Evidence rows | Reading |
| --- | --- | --- | --- | --- | --- | --- | --- |
| WLK-01 | Ledger changes land and merge within the hour | FLW-01 | Normal | Normal run | Pass | BUD-03, EXT-02 | A changed volume of 1 GB a day moves in seconds and the path totals 1,030 s against 3,600 s |
| WLK-02 | A card event reaches the fraud service | FLW-02 | Normal | Normal run | Pass | BUD-01, SCN-01, STM-01 | 11 s against a 60 s target; 8 partitions keyed by card carry 20 MB per second |
| WLK-03 | Hourly card-event files land | FLW-03 | Normal | Normal run | Pass | EXT-06, SCN-08 | Daily landing needs 2,000 s of write time; replay and duplicates are absorbed by the merge |
| WLK-04 | The customer view refreshes every five minutes | FLW-04 | Normal | Normal run | Pass | BUD-04, API-02, SCN-13 | 350 s against 900 s; one request per poll; the overlap is harmless |
| WLK-05 | The daily CRM pull and weekly export align | FLW-05 | Normal | Normal run | Pass | EXT-05, API-03, SCN-14 | 12 requests a day; the weekly load takes 240 s |
| WLK-06 | A settlement file loads | FLW-06 | Normal | Normal run | Pass | EXT-04, SCN-09 | 40 s of load inside the two-hour deadline |
| WLK-07 | A card event is delivered twice | FLW-02 | Failure | Duplicate delivery | Pass | SCN-02, FMX-03 | The repeat changes nothing and no second alert is sent |
| WLK-08 | An older card update arrives after a newer one | FLW-02 | Failure | Out-of-order update | Pass | SCN-03, FMX-02 | The version guard refuses the stale update; the last-arrival rule would not (SCN-04) |
| WLK-09 | Seven days of ledger changes are replayed | FLW-01 | Failure | Replay | Pass | SCN-05, LAG-04 | The replay is idempotent and drains in about 18,000 s against a day |
| WLK-10 | A producer changes amount_minor from minor to major units | FLW-01 | Failure | Schema change | Pass | CHG-05, FMX-17 | The structural check passes; the semantic test dataset and the reviewer block it, and a new version is published |
| WLK-11 | The CRM API is unavailable for an hour | FLW-04 | Failure | Source outage | Pass with residual risk | RTY-01, API-02, FMX-09 | Polls retry within a 7 s budget and resume from the watermark; the residual risk is that view age exceeds 900 s during the outage |
| WLK-12 | A settlement file arrives with half its rows | FLW-06 | Failure | Incomplete file | Pass | SCN-10, FMX-11 | The file is quarantined and the good file publishes |
| WLK-13 | The fraud consumer is down for one hour | FLW-02 | Failure | Consumer outage | Pass with residual risk | LAG-01, FMX-04 | Nothing is lost and the backlog drains in 1,800 s; the residual risk is that events from the outage are scored late |
| WLK-14 | A card event cannot be deserialised | FLW-02 | Failure | Poison message | Pass | RTY-02, FMX-13 | Three retries total 7 s, then the event goes to dead-letter and the stream continues |
| WLK-15 | The CRM credential expires | FLW-04 | Failure | Credential expiry | Pass with residual risk | FMX-07, DRL-02 | The warning fires 14 days ahead; the residual risk is a stale view if the rotation is missed |
| WLK-16 | A ledger entry is hard-deleted | FLW-01 | Failure | Hard delete | Pass | SCN-06 | The tombstone is kept and a late older update is refused |
| WLK-17 | Card events arrive after their lateness window | FLW-03 | Failure | Late data | Pass with residual risk | ORD-03, SCN-08 | Late events are quarantined and reported; the residual risk is that analytics are incomplete until they are reprocessed |
| WLK-18 | A settlement file fails its checksum | FLW-06 | Failure | Incomplete file | Pass | SCN-11 | A matching count is not enough; the failed checksum quarantines the file |
| WLK-19 | The ledger log is purged before the reader catches up | FLW-01 | Failure | Source outage | Pass with residual risk | FMX-01, DRL-01 | Re-seed and the seam procedure recover the data; the residual risk is that log retention is unknown (OQ-01) |
| WLK-20 | Two accounts are swapped and totals still agree | FLW-01 | Failure | Reconciliation | Pass | INJ-10, INJ-09 | Count, total and key coverage pass; the field-level sample comparison catches it |
| WLK-21 | The CRM halves its rate limit | FLW-05 | Failure | Rate limit | Pass | API-04, RTY-01 | The daily pull needs 12 requests and takes about 2 s even at 5 per second |

#### Random trace

`python3 check_integration_design.py FILE --trace 3 --seed 2026` prints three requirements traced forward to the decision, flow, contract, controls and evidence, and three decisions traced back to requirements and flows. The recorded output is in section 7.3.

#### Package inventory

All counts are derived from the tables.

| ID | Package inventory | Count |
| --- | --- | --- |
| CNT-01 | Stakeholder roles | 14 |
| CNT-02 | Systems | 8 |
| CNT-03 | Source capabilities | 18 |
| CNT-04 | Data assets | 4 |
| CNT-05 | Requirements | 22 |
| CNT-06 | Constraints | 4 |
| CNT-07 | Assumptions | 12 |
| CNT-08 | Dependencies | 4 |
| CNT-09 | Flows | 6 |
| CNT-10 | Decisions | 7 |
| CNT-11 | Candidates | 38 |
| CNT-12 | Gates | 9 |
| CNT-13 | Contracts | 7 |
| CNT-14 | Contract changes | 12 |
| CNT-15 | Mappings | 21 |
| CNT-16 | Reconciliation controls | 23 |
| CNT-17 | Injection tests | 19 |
| CNT-18 | State scenarios | 14 |
| CNT-19 | Components | 13 |
| CNT-20 | Failure modes | 18 |
| CNT-21 | Alerts | 21 |
| CNT-22 | Walkthroughs | 21 |
| CNT-23 | Risks | 11 |
| CNT-24 | Open questions | 8 |

#### Architecture decision records

#### ADR-01 — Pattern for ledger changes to analytics (DEC-01)

- **Status.** Proposed; conditional on OQ-01.
- **Context.** The ledger holds 8,000 GB and changes by about 1 GB a day; peak write rate is 2,000 changes per second. The ledger has no reliable last-modified column (CAP-03), must not be scanned (CON-02), and its feed must be recoverable from any point in seven days (REQ-09) with zero tolerance on totals (REQ-03).
- **Decision.** CAN-03: log-based change capture with an initial snapshot and a retained change stream, merged by a version-guarded rule (IDM-01) and checked daily by counts, totals, key-and-version, an invariant, a sample comparison and an independent extract.
- **Rejected alternatives.** CAN-01, the nightly full copy, takes 40,000 s against a 14,400 s window (EXT-01). CAN-02 would miss changes on tables with no last-modified column (CAP-03). CAN-04, an hourly snapshot comparison, takes 40,000 s against 3,600 s (EXT-03). CAN-05, triggers, scores 3.20 against 4.30 because it adds write work to the ledger. CAN-06, a managed connector, scores 3.95: simpler to run, but less control of the seam and replay and a higher cost.
- **Assumptions and risks.** ASM-01, ASM-04. RSK-02 (log retention), RSK-08 (semantic changes), RSK-05.
- **Validation plan.** Run DRL-01 (lose the log position and re-seed), SCN-05 and SCN-06 (replay and delete), LAG-03 and LAG-04 (catch-up). Pass: re-seed within 8 hours, control-total delta 0, no duplicates.
- **Revisit triggers.** OQ-01 shows the log cannot be read or retained long enough; the ledger adds tables with no key; the change rate exceeds the reader's capacity (LAG-03).

#### ADR-02 — Pattern for card events to the fraud service (DEC-02)

- **Status.** Proposed; conditional on OQ-02 and OQ-06.
- **Context.** Fraud needs events within 60 s at p95 (REQ-01), in order per card (REQ-02), and must survive a one-hour consumer outage without loss (REQ-10) at 20,000 events per second.
- **Decision.** CAN-08: a keyed event stream, one partition per card key, 8 partitions at the peak (STM-01), seven days retained, consumed by a version-guarded applier (IDM-02) with offsets.
- **Rejected alternatives.** CAN-07, a five-minute file micro-batch, totals 336 s against 60 s (BUD-02). CAN-09, direct calls with no retained log, would lose about 72 million events in a one-hour outage. CAN-10, one shared queue with competing consumers, cannot keep per-card order. CAN-12, push with a local buffer, scores 3.15 against 4.10 and creates a second, unshared retention mechanism. CAN-11, a managed streaming service, scores 4.00 against 4.10 and wins under the simplicity-heavy weighting (WS-02), so the choice is conditional on OQ-06.
- **Assumptions and risks.** ASM-02, ASM-03, ASM-08. RSK-03 (ordering guarantee unknown), RSK-07 (hot key), RSK-11.
- **Validation plan.** DRL-04 (one-hour outage), SCN-02 and SCN-03 (duplicate and out-of-order), BUD-01 and LAG-01. Pass: zero loss, backlog drained within 1,800 s, no second alert.
- **Revisit triggers.** OQ-02 shows no per-card order; a hot key passes 1% of traffic; OQ-06 says the team cannot run a stream.

#### ADR-03 — Pattern for card events to analytics (DEC-03)

- **Status.** Proposed.
- **Context.** Analytics needs card events landed hourly with no loss and no duplication (REQ-21), replayable for seven days.
- **Decision.** CAN-14: a second consumer group on the same stream writes hourly files to the landing zone with offset checkpoints; the merge deduplicates by event id over a 168-hour window (IDM-03).
- **Rejected alternatives.** CAN-13, a daily export, is up to 86,400 s old against an hourly need. CAN-16, copying from the fraud store, holds only a short window and cannot prove completeness. CAN-15, continuous micro-commits, scores 3.50 against 4.05 because of the number of tiny files. CAN-17, a managed sink connector, scores 3.60 and hides duplicate handling.
- **Assumptions and risks.** ASM-02. RSK-06 (replay beyond the dedup window).
- **Validation plan.** SCN-07 and SCN-08 (replay with and without dedup), REC-08 to REC-10, EXT-06. Pass: no duplicate ids, hourly counts and totals equal.
- **Revisit triggers.** Retention or the replay horizon changes; the number of landed files per day passes the platform's comfortable limit.

#### ADR-04 — Pattern for the current customer view (DEC-04)

- **Status.** Proposed; conditional on OQ-03 and OQ-04.
- **Context.** Agents need a current customer view, minutes stale at most (REQ-08, ASM-07), from a CRM limited to 10 requests per second and a daily quota of unknown size (CON-03, CAP-10).
- **Decision.** CAN-19: an incremental poll every five minutes with a modified-since filter into a materialised view (IDM-04), with a weekly full comparison against the bulk export.
- **Rejected alternatives.** CAN-18, a full pull, needs 1,200 s of requests against a 900 s target (API-01). CAN-20, live federated lookups, use 10 requests per second, 100% of the CRM limit (FED-01), and give 99.351% availability against 99.5% (AVC-01). CAN-22, a weekly export alone, is up to a week stale. CAN-23, a ten-minute poll with a daily full verification, scores 3.65 against 4.05 and uses 12,000 extra requests a day against an unknown quota. CAN-21, push notifications, depends on a feature nobody has confirmed (CAP-17).
- **Assumptions and risks.** ASM-07, ASM-09, ASM-10. RSK-01 (no filter or too small a quota).
- **Validation plan.** API-02 and FED-02 against a sandbox; BUD-04; SCN-13; DRL-02. Pass: view age under 900 s at p95; request rate under 5 per second.
- **Revisit triggers.** OQ-04 shows no modified-since filter (fall back to CAN-21 or CAN-23); OQ-03 shows a quota under 1,000 requests a day.

#### ADR-05 — Pattern for CRM history to analytics (DEC-05)

- **Status.** Proposed; weight-sensitive; conditional on OQ-03, OQ-04 and OQ-06.
- **Context.** Analytics needs daily CRM history with deletes visible within seven days (REQ-22). The API may not show deletes (CAP-13 unknown).
- **Decision.** CAN-25: a daily incremental pull plus a weekly bulk export used to detect deleted records by key coverage (REC-14) and to reconcile the base.
- **Rejected alternatives.** CAN-24, a weekly snapshot alone, is up to seven days old. CAN-26, a daily full pull, scores 3.30 and needs 12,000 requests a day against an unknown quota. CAN-27, push notifications, depends on an unconfirmed feature. CAN-28, a managed connector, scores 3.65 against 4.05 and wins under the simplicity-heavy weighting (WS-02), so the choice is conditional on OQ-06.
- **Assumptions and risks.** ASM-05. RSK-01, RSK-11.
- **Validation plan.** API-03 and API-04, EXT-05, SCN-14, INJ-14. Pass: a deleted record is found by the weekly key comparison.
- **Revisit triggers.** OQ-04 shows deletes in the API; OQ-06 prefers a managed connector.

#### ADR-06 — Pattern for settlement files (DEC-06)

- **Status.** Proposed; conditional on OQ-05.
- **Context.** About 2,000,000 records (2 GB) arrive daily with a manifest; no loss, no duplication (REQ-07), loaded within two hours of arrival (REQ-06), reconciled for regulatory evidence.
- **Decision.** CAN-30: detect arrival, validate record count, checksum and control total against the manifest, quarantine on mismatch, and merge by settlement id (IDM-06, IDM-07); issue a daily evidence report (CTR-07).
- **Rejected alternatives.** CAN-29, loading with no validation, would publish half a file (SCN-12). CAN-33 needs a record-level partner API that does not exist (CAP-18). CAN-31, an arrival-triggered gate, scores 4.25 against 4.45 and adds a missed-event failure mode to save minutes inside a two-hour deadline. CAN-32, a managed file-transfer service, checks a checksum only and scores 3.80.
- **Assumptions and risks.** ASM-06. RSK-04 (manifest without a checksum), RSK-09.
- **Validation plan.** SCN-09 to SCN-11, DRL-03, INJ-15, REC-16 to REC-20. Pass: incomplete and corrupt files quarantined within 10 minutes; nothing partial published.
- **Revisit triggers.** OQ-05 shows no checksum (add a record-level sample as the main control); the partner moves to a record-level API.

#### ADR-07 — Where transformation happens (DEC-07)

- **Status.** Proposed; weight-sensitive; conditional on OQ-08.
- **Context.** Four flows land data that must be re-derivable and auditable (REQ-05, REQ-20) and classified as it moves (REQ-19).
- **Decision.** CAN-35: land raw data unchanged and transform in the target (ELT); each target field has a mapped source or rule (MAP table), owned by the target owner except evidence reports, owned by compliance.
- **Rejected alternatives.** CAN-34, transforming in flight, stores only transformed rows, so a defective mapping cannot be re-derived or audited. CAN-38, views on the source, adds read work to the ledger (CON-02). CAN-37, producers publish conformed events, scores 3.30 and moves work to four source owners. CAN-36, light conformance in flight, scores 4.00 against 4.15 and wins under the governance-heavy weighting (WS-04), so the choice is conditional on OQ-08.
- **Assumptions and risks.** RSK-05, RSK-10 (raw retention).
- **Validation plan.** Re-run one landed day through a corrected mapping and compare totals; SCN-08; REC-08. Pass: totals equal after the re-run.
- **Revisit triggers.** OQ-08 sets raw retention too short for replay; privacy requires masking before landing.

#### Recommendation summary (one page for the sponsor)

Northbridge should stop copying whole tables and trusting restarts. Read ledger changes from the transaction log and move only the change (about 1 GB a day instead of 8,000 GB), keeping a seven-day replayable stream so any point can be recovered. Give fraud a keyed event stream (11 s against a 60 s target, ordered per card) with a consumer that can run at three times the arrival rate, so a one-hour outage drains in 30 minutes. Land card events for analytics hourly from the same stream. Keep the contact-centre view in its own store refreshed every five minutes instead of querying the CRM live, which would use all of its rate limit. Load settlement files only through a manifest gate. Land raw data and transform in the target so every load can be re-derived and audited.

Correctness comes from three controls kept distinct: idempotent merge rules (a repeat or an older update changes nothing), deduplication windows at least as long as the replay horizon, and reconciliation at several levels with independent totals. The package states what each misses: a consistently wrong transformation or a duplicated external side effect can pass the internal checks, and the compensating controls are named.

**Conditional items** and what would settle them: ledger log retention (OQ-01, source owner), per-card publication order (OQ-02, cards owner), CRM quota and API features (OQ-03 and OQ-04, vendor sandbox test), settlement manifest content (OQ-05, partner), operations capacity for a self-managed stream (OQ-06), evidence retention (OQ-07, compliance) and raw retention (OQ-08, privacy). **Next step:** hand the zones, enforcement points and reconciliation hooks to module 2D.7, the connectivity and residency needs to 2D.8, and the stream contracts to 2D.9.

#### Completion gate status

The roadmap's gate (7.7) requires every item to hold. The author cannot satisfy the reviewer items, so the package is **not complete** until they are done.

| ID | Gate item | Status | Evidence in this file | Reason |
| --- | --- | --- | --- | --- |
| VAL-01 | D1 to D17 exist, version-dated, with consistent IDs | Met | Sections 6.1 to 6.17 and the deliverable register in section 0 | none |
| VAL-02 | Every flow has measurable freshness, throughput and correctness requirements and no requirement names a product | Met | REQ-01 to REQ-22; checker rule on product names | none |
| VAL-03 | At least three feasible candidates per flow including a simplest baseline, criteria fixed first, gate failures recorded, selection cites source-capability evidence | Met | CAN-01 to CAN-38; CAP table; criteria locked 2026-10-18 | none |
| VAL-04 | Each feed has a contract; a structurally valid but semantically breaking change is identified and handled | Met | CTR-01 to CTR-07; CHG-05 and CHG-10 | none |
| VAL-05 | Each flow has identity, an idempotent rule, deduplication and reconciliation with tolerance, independence and a coverage matrix naming undetected classes | Met | IDM, REC, DET, COV, INJ, SCN | none |
| VAL-06 | Every component has a failure scenario with detection, impact, recovery and owner; at least ten overall; catch-up arithmetic for a backlog | Met | CMP-01 to CMP-13; FMX-01 to FMX-18; LAG-01 | none |
| VAL-07 | All numeric claims have units, formulas, assumptions and an illustrative label; a reviewer reproduces three figures | Partly met | Section 6.5 and 7.8; the checker recomputes every figure | No human reviewer has reproduced three figures |
| VAL-08 | At least five normal and eight failure scenarios walked, including duplicate delivery, out-of-order, replay, schema change, source outage, incomplete file | Met | WLK-01 to WLK-21 | none |
| VAL-09 | Each control is traced to a requirement; no sensitive data is unclassified in landing or dead-letter stores | Met | SEC-01 to SEC-10; STR-01 to STR-06 | none |
| VAL-10 | Each alert has an owner and an action; absence and staleness are monitored; a drill with pass criteria is defined | Met | OPS-01 to OPS-21; DRL-01 to DRL-04 | none |
| VAL-11 | Trace tests pass and two reviewer challenges are answered from recorded evidence | Partly met | Section 7.3 and 7.6 | The challenges are author-prepared, not from a real reviewer |
| VAL-12 | An independent reviewer agrees the evidence supports the conclusions | Not met | none | No independent review has taken place |

---

## 7. Validation and quality assurance

### 7.1 Quality criteria and how each is verified

This table maps the roadmap's validation checks (Section 7.6) to the mechanism in this package.

| Roadmap check | How this package verifies it | Verified by |
| --- | --- | --- |
| Every in-scope data flow has a purpose and an owner | Each flow end is a system with an owner or `Unknown` plus an open question; each flow has an owner for its transformation, a contract, identity, reconciliation, ordering, mapping, failure, alert and walkthrough rows | Checker |
| Patterns match source capabilities and consumer requirements | Each candidate lists the capabilities it requires; one that needs a capability the source lacks fails the interface gate; one that needs an unknown capability makes its decision conditional; every decision cites requirements | Checker |
| Data contracts are clear and compatible with expected change | Each contract has semantics (units and null meaning), a mode that follows from upgrade order and replay, a notice period and an owner; sample changes are classified by rule, including a semantic break | Checker |
| Freshness, throughput and correctness requirements are measurable | Each requirement has a metric, target, method and source; derived arithmetic is recomputed | Checker |
| Duplicate processing and replay are considered | Every flow has an identity rule whose dedup window covers the replay horizon; merge scenarios are executed, including a replay, a duplicate and an out-of-order update; naive rules must fail | Checker (runs the scenarios) |
| Reconciliation detects meaningful discrepancies | Injected defects (missing, duplicate, value drift, swapped accounts, offsetting errors, truncation, missed delete) are run through each level and must match a detection matrix; the coverage matrix lists undetected classes per flow | Checker (runs the injections) |
| Failure scenarios have detection and recovery | Every component has a scenario; at least ten overall; each has detection, recovery, owner and validation evidence | Checker |
| Security and governance are addressed | Each control traces to a requirement; landing and dead-letter stores must list every sensitive asset and carry a classification | Checker |
| The architecture is internally consistent | Every system and flow appears in the diagram; every flow has a decision, a contract and a pattern that starts with the selected candidate | Checker |
| Recommendations are traceable | Random traces run in both directions | Checker (`--trace`) |

### 7.2 Running the checker

Python 3.9 or later; standard library only.

```bash
python3 check_integration_design.py 06-cross-system-data-integration-design.md           # verify
python3 check_integration_design.py 06-cross-system-data-integration-design.md --fill    # fill cells marked ~
python3 check_integration_design.py 06-cross-system-data-integration-design.md --trace 3 --seed 2026
```

Save the code in Appendix B as `check_integration_design.py`. Exit status 0 means every check passed.

### 7.3 What the checker verifies, and its recorded output

- **Structure:** table headers match the schema; IDs match their table; no duplicates, empty cells, placeholder text or product names; every ID mentioned exists.
- **Derived cells:** workload rates and volumes; batch time against the window; API requests, pacing and daily requests against the quota; retry budget; stream partitions, skew check and retained volume; backlog, catch-up and required capacity; latency and freshness budgets; serial availability; federated load; contract change effects and classes; state size; coverage lines; injection results; scenario outcomes; candidate totals, eligibility and ranks; decision weight-sensitivity; risk scores; package counts.
- **Discipline:** weights sum to one and equal the locked set; criteria are locked before D6 and D4 precedes D6; each decision has at least three eligible candidates and one baseline; the selected candidate is rank 1 and the runner-up rank 2; a candidate that requires a capability the source lacks fails the interface gate; a selected candidate that needs an unknown capability carries a conditional note; chosen designs pass their budgets and rejected alternatives fail theirs.
- **Correctness:** the dedup window covers the replay horizon; a merge rule has the identity it needs; every contract field is mapped; the detection matrix agrees with the executed injections; every flow has count or total control and a key-level or independent control; zero-tolerance flows use zero tolerance; undetected classes carry compensating notes; naive rules fail their scenarios.
- **Operations and governance:** every component has a failure mode; every flow has freshness, absence and reconciliation alerts; every alert has an owner and an action; drills have measurable pass criteria; landing and dead-letter stores list all sensitive assets.
- **Honesty:** at least one gate item must be unmet, an independent review cannot be marked met without a reviewer record, and the text may not claim approval or independent review.

Recorded output of the final run:

```text
Parsed: API=4, AST=4, AVC=2, BUD=5, CAN=38, CAP=18, CH=3, CHG=12, CMP=13, CNT=24, COV=6, CRT=8, CTR=7, DEC=7, DET=11, DL=17, DRL=4, EXT=6, FED=2, FLW=6, FMX=18, FND=9, GT=9, IDM=7, INJ=19, LAG=4, LAT=14, MAP=21, OPS=21, OQ=8, ORD=6, REC=23, REQ=42, RSK=11, RTY=2, SCN=14, SEC=10, STD=18, STK=14, STM=5, STR=6, SYS=8, TRD=6, VAL=12, WLD=4, WLK=21, WS=5
All checks passed
```

Recorded output of `--trace 3 --seed 2026`:

```text
Forward (requirement -> decision -> flow -> contract -> controls -> evidence):
  REQ-04 -> DEC-01 -> FLW-01 -> CTR-01 -> IDM-01,REC-01 -> WLK-01,WLK-09
  REQ-11 -> DEC-02 -> FLW-02 -> CTR-02 -> IDM-02,REC-06 -> WLK-02,WLK-07
  REQ-17 -> DEC-01 -> FLW-01 -> CTR-01 -> IDM-01,REC-01 -> WLK-01,WLK-09
Backward (decision -> requirements -> flows):
  DEC-05 <- REQ-12, REQ-22 <- FLW-05
  DEC-06 <- REQ-06, REQ-07, REQ-15, CON-04 <- FLW-06
  DEC-01 <- REQ-03, REQ-04, REQ-09, REQ-13, REQ-17, CON-02, ASM-01 <- FLW-01
```

### 7.4 Critical-error self-review

Before asking for review, read the package against these questions. Any "yes" is a defect to fix.

1. Is any source capability written `Yes` that nobody has documented or tested?
2. Does any pattern depend on a capability marked `No` or `Unknown` without a conditional note?
3. Is any freshness, volume or window claim made without a unit, a formula and a label?
4. Is a transport guarantee (at-least-once, ordered) used as if it were business correctness?
5. Is any deduplication window shorter than the longest replay the design allows?
6. Does any reconciliation rely on the same logic as the load, with no independent source, and is that stated?
7. Can a change in the meaning of a field pass every automated check, and who reviews it?
8. Is any component (scheduler, credentials, registry, monitoring itself) missing from the failure matrix?
9. Is any sensitive data held in landing or dead-letter stores without a classification?
10. Does the summary claim approval, a benchmark or an independent review that did not happen?

### 7.5 Project completion gate and status

The roadmap's gate (7.7) lists eleven items. The worked reference meets most and says plainly what it cannot.

| Gate area | Status | Note |
| --- | --- | --- |
| D1–D17 exist, version-dated, consistent IDs | Met | Section 0 and Section 6 |
| Requirements measurable, none names a product | Met | REQ-01 to REQ-22 |
| Pattern selection with baseline, gates, capability evidence | Met | 38 candidates, 7 decisions, criteria locked first |
| Contracts with a semantic break handled | Met | CTR-01 to CTR-07, CHG-05, CHG-10 |
| Correctness: identity, idempotency, dedup, reconciliation, coverage | Met | Executed scenarios and injections |
| Failure and recovery: every component, at least ten scenarios, catch-up arithmetic | Met | 13 components, 18 failure modes, LAG-01 |
| Quantification: a reviewer reproduces three figures | Partly met | Recomputed by the checker; no human reviewer has reproduced three figures |
| Validation: 5 normal and 8 failure scenarios | Met | 6 normal, 15 failure |
| Security and governance traced | Met | SEC and STR tables |
| Operations: alerts, absence, drill | Met | 21 alerts, 4 drills |
| Traceability, challenges, independent reviewer | **Not met** | Challenges are author-prepared; no independent review has taken place |

**Readiness decision.** *Not yet ready for approval.* The design is coherent and every figure is reproducible, but eight open questions and the independent review remain. Four of them (OQ-02, OQ-03, OQ-04, OQ-05) are answers only a source owner, vendor or partner can give and they decide whether the selected patterns hold. Proceed to module 2D.7 on the zones, enforcement points and reconciliation hooks, which do not depend on those answers, while the questions are put to their owners.

### 7.6 Anticipated reviewer challenges (author-prepared, not recorded reviewer objections)

| ID | Reviewer objection | Answer from recorded evidence | Evidence ids |
| --- | --- | --- | --- |
| CH-01 | Why copy CRM data into a view instead of querying the CRM live and avoiding a second copy of personal data? | A live design uses 10 requests per second, all of the CRM's limit, and has 99.351% serial availability against a 99.5% target; the view uses 0.003 requests per second and reads from its own store at 99.850% | FED-01, FED-02, AVC-01, AVC-02, TRD-03 |
| CH-02 | Five-minute batches are simple; why run a stream for fraud? | The five-minute path totals 336 s against a 60 s target; the stream path totals 11 s with 82% headroom | BUD-01, BUD-02 |
| CH-03 | Counts and totals reconcile every day; why add field-level comparison? | Swapped accounts leave count, total and key coverage unchanged; only a field-level comparison or a hash of full rows detects it | INJ-07, INJ-08, INJ-09, INJ-10, INJ-18 |

### 7.7 Findings from design review and audit

Findings 05 to 09 were found by the audit of version 1.0 and are closed in 1.1; findings 01 to 04 are open by nature.

| ID | Review area | Finding | Type | Severity | Status | Resolution |
| --- | --- | --- | --- | --- | --- | --- |
| FND-01 | Source capabilities | Eight source capabilities are unknown and five decisions depend on them | Evidence gap | Major | Open | CAP statuses; OQ-01 to OQ-05; every dependent decision is conditional |
| FND-02 | Independence | No independent reviewer has agreed the evidence | Process gap | Major | Open | Not closable by the author; VAL-12 |
| FND-03 | Retention | Evidence and raw-copy retention periods are not decided | Evidence gap | Minor | Open | OQ-07 and OQ-08; RSK-09, RSK-10 |
| FND-04 | Quantification | All rates, latencies, availabilities and capacities are planning values | Evidence gap | Minor | Open | Measure in a pilot before build (ASM-04 to ASM-12) |
| FND-05 | Template coverage | The roadmap's flow-inventory template requires an expected volume with units; the flow table had none | Missing content | Major | Closed | Added the Expected volume column for all six flows |
| FND-06 | Source capabilities | A candidate that needed a capability the source does not offer (the ledger last-modified column, the partner record API) had no gate it could fail | Design gap | Major | Closed | Added gate GT-09; the checker requires GT-09 to fail exactly when a required capability has status No |
| FND-07 | Correctness | The coverage note for the fraud flow said another flow's controls would catch mapping errors in the fraud store; those controls inspect the landed copy, not the fraud store | Unsupported claim | Major | Closed | Added the weekly sample comparison REC-23 and rewrote the note; undetected classes for the flow fell from four to two |
| FND-08 | Traceability | Seven requirements and constraints (contract notice, ownership, evidence retention, residency, least privilege, encryption, scope) were cited by no decision | Traceability gap | Major | Closed | Cited in the decisions they constrain (DEC-01, DEC-02, DEC-06, DEC-07) |
| FND-09 | Consistency | The recommendation said the fraud consumer had twice the capacity, but LAG-01 requires three times the arrival rate to drain in 1,800 s; DEC-05's conditional note omitted OQ-06 although ADR-05 relies on it | Inconsistency | Minor | Closed | Wording and note corrected |

### 7.8 Hand-calculation check for a reviewer

The roadmap asks a reviewer to reproduce at least three figures without the tool. Five are worked here; all use decimal units.

| Figure | Hand calculation | Result |
| --- | --- | --- |
| EXT-01 nightly full copy | 40 billion rows × 200 B = 8,000 GB; × 1,000 MB/GB ÷ 200 MB/s | 40,000 s, against 14,400 s: Fail |
| STM-01 stream sizing | 20,000 events/s × 1,000 B = 20 MB/s; ÷ 5 MB/s = 4; × 2 headroom = 8 partitions; 20 MB/s × 86,400 s × 7 d × 3 ÷ 10⁶ | 8 partitions; 36.29 TB |
| LAG-01 catch-up | Backlog 20,000/s × 3,600 s = 72,000,000; recovery rate 60,000 − 20,000 = 40,000/s | 1,800 s, equal to the target: Pass |
| API-01 full CRM pull | 12,000,000 ÷ 1,000 per page = 12,000 requests; ÷ 10 requests/s | 1,200 s, against 900 s: Fail |
| FED-01 live lookups | 300 users × 2 lookups/min × 1 request ÷ 60 | 10 requests/s, 100% of the limit: Fail |

Reproducing these, and two or three more a reviewer chooses at random, is the human half of VAL-07.

---

## 8. Templates and guides for a real organisation (Mode B)

### 8.1 Row templates

Copy the header exactly. Replace the example text. Keep `~` for derived cells.

```text
Capability: | ID | Capability | System | Status | Limit | Evidence |
Flow:       | ID | Flow | From | To | Asset | Pattern | Trigger | Expected volume | Freshness target | Transformation owner | Contract | Recovery | Decision | Evidence |
Workload:   | ID | Workload line | Asset | Total records | Daily records | Record bytes | Peak per s | Avg per s | Peak factor | Daily GB | Total GB | Peak MB/s | Growth per yr | Horizon yr | Horizon GB per day | Evidence |
Candidate:  | ID | Candidate | Decision | Baseline | Requires | Gates | Gate failure reason | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | Total | Eligible | Rank | Limitation or risk | Evidence |
Contract:   | ID | Contract | Flow | Producer | Consumers | Schema ref | Key | Required fields | Optional fields | Semantics | Compatibility mode | Upgrade order | Replays history | Notice days | Quality and delivery | Owner | Evidence |
Identity:   | ID | Identity rule | Flow | Business key | Event id | Version field | Dedup scope | Dedup window h | Key bytes | Events per s | State GB | Merge rule | Side effects | Replay horizon h | Evidence |
Reconcile:  | ID | Reconciliation | Flow | Level | Grain | Window | Tolerance | Independence | Frequency | Output | Owner | Evidence |
Failure:    | ID | Failure scenario | Component | Flow | Detection | Data impact | Recovery | Idempotency need | Reconciliation need | Owner | Validation evidence | Evidence |
```

The remaining tables use the headers shown in Section 6. A new table kind needs a new schema entry in the checker.

### 8.2 Interview guide for source, partner and consumer owners

1. What interfaces does the system offer for reading data, and where are they documented? Which have you tested?
2. How do you see changes: a log, a last-modified column, notifications? Are deletes visible? In what order are changes published?
3. What are the rate limits, quotas, windows and maintenance periods? What happens when a limit is exceeded?
4. How long are logs, events or files kept, and can a past period be re-sent?
5. How do you announce changes to fields, codes and meanings? Who approves them?
6. What does a consumer need: how fresh, how complete, how ordered, how reconciled, and what happens if it is late?
7. What would you do if the feed stopped for an hour? A day? Who gets called?
8. Which data are personal or financial, where may they be stored, and for how long?

### 8.3 Pre-review checklist

- [ ] Every source capability is `Yes` only with a document or a test behind it.
- [ ] Every `Unknown` has an open question with an owner and the evidence that settles it.
- [ ] Every number has a unit and an evidence label; no `~` remains; the checker prints "All checks passed".
- [ ] Every rejected candidate has a reason that cites a gate, a number or a capability.
- [ ] Every contract states units and what null or absent means.
- [ ] Every reconciliation level's blind spot is stated, and undetected classes have a compensating note.
- [ ] A person who did not write the package has agreed to review it.

---

## 9. Common pitfalls and project risks

| Pitfall | Why it hurts | Defence in this package |
| --- | --- | --- |
| Assuming a source capability | The design fails on the first test | Capability statuses; a candidate needing a `No` cannot be eligible; one needing an `Unknown` makes its decision conditional |
| Full copy because it is easy | The source is strained and the window overrun | Extract-time arithmetic against the window, quantified rejection |
| Trusting transport delivery for correctness | Duplicates and stale overwrites | Version-guarded merges; scenarios run a replay, a duplicate and an out-of-order update; naive rules must fail |
| A dedup window shorter than the replay | A replay duplicates data | The checker refuses a window below the replay horizon |
| "Counts match" as proof | Swapped accounts, drift and offsetting errors pass | Multi-level reconciliation, a detection matrix and executed injections |
| Reconciliation sharing the load's logic | A common error passes both | Independence stated per control; independent extracts; compensating notes |
| Structural compatibility as the only check | A change in meaning passes silently | A semantic-change gate, a semantic test dataset and a named reviewer |
| Federating a rate-limited source | The source limit and availability become the consumer's | Federated-load and availability arithmetic; materialised view |
| Missing components in the failure matrix | The scheduler or the credential store is the surprise | Component register; every component needs a scenario |
| Alerting on errors only | A silent stop is never noticed | Freshness, absence and reconciliation alerts required for every flow |
| Unclassified landing and dead-letter data | Sensitive data accumulates unlabelled | The checker requires both stores to list every sensitive asset and carry a label |
| Claiming approval or independence | False comfort | The checker refuses such claims; one gate item stays unmet until a reviewer signs |
| Growing into a build | The project never ends | Out-of-scope table in 6.1; open questions go to later modules |

---

## 10. Connection to subsequent modules

| Later module | What this project hands over | Where |
| --- | --- | --- |
| 2D.7 Enterprise data platform and lakehouse | Landing, quarantine and curated zones, contract enforcement points, reconciliation hooks, OQ-08 | 6.8, 6.14 |
| 2D.8 Cloud, hybrid and multi-cloud | Connectivity and residency needs (REQ-16, CON-03), managed-integration candidates (CAN-06, CAN-11, CAN-17, CAN-28, CAN-32), price assumptions to replace | 6.4, 6.6 |
| 2D.9 Streaming and real-time | Event contract CTR-02, key and partition requirements (STM), retention and replay requirements, freshness budgets, OQ-02 and OQ-06 | 6.5, 6.10 |
| 2D.10–2D.11 Governance, metadata, lineage, quality | Contracts, classification labels, lineage points (SEC-06), reconciliation evidence (CTR-07), identifier rules, OQ-07 | 6.10, 6.12, 6.14 |
| 2D.12 Reliability and disaster recovery | Failure matrix, replay and re-seed procedures, drills (DRL-01 to DRL-04) | 6.13, 6.15 |
| 2D.14 Data access, serving and AI data | Feeds, freshness targets and contracts for downstream products; the materialised-view pattern | 6.7, 6.10 |

**Open questions logged for 2D.7.** OQ-08 (raw retention in landing), DEP-02 (zones) and the enforcement points in SEC-04 and SEC-08.

---

## 11. Self-assessment rubric

Score each row 0 (absent), 1 (partial), 2 (adequate) or 3 (strong). A passing package scores at least 2 on every row and at least 24 of 30.

| # | Criterion | 3 means |
| --- | --- | --- |
| 1 | Scope and assumptions | Exclusions firm; every assumption registered and validated |
| 2 | Source capability evidence | Every capability `Yes`, `No` or `Unknown`; each unknown has an owner and a way to settle it |
| 3 | Requirements and quantification | Measurable; formulas, units and ranges; a reviewer reproduces three figures |
| 4 | Pattern comparison | Gates and weights locked first; baseline present; capability links; sensitivity tested; conditional decisions flagged |
| 5 | Contracts and compatibility | Owners, semantics, modes from upgrade order, notice, a semantic break handled |
| 6 | Idempotency and deduplication | Identity, version rules, windows at least as long as replay, side effects keyed; scenarios executed |
| 7 | Reconciliation | Levels, tolerances and independence per flow; blind spots stated; injections executed |
| 8 | Failure and recovery | Every component covered; detection, recovery, owners, catch-up arithmetic, drills with pass criteria |
| 9 | Security, governance and operations | Controls traced to requirements; classification through landing and dead-letter; absence and staleness alerts |
| 10 | Honesty and traceability | Open items visible; nothing claimed that did not happen; traces succeed both ways |

---

## Appendix A — Glossary

| Term | Meaning |
| --- | --- |
| At-least-once delivery | A transport promise that a message arrives one or more times, never zero |
| Backlog | Records waiting to be processed when arrival exceeds processing |
| Baseline | The simplest adequate option every comparison must include |
| Change data capture | Reading a source's changes, usually from its log, instead of re-reading its tables |
| Checkpoint (offset, watermark) | A recorded position from which processing resumes |
| Compatibility mode | The rule a contract change must satisfy: backward, forward or full |
| Control total | A count or sum compared across two systems to prove they agree |
| Data contract | A producer-owned agreement on structure, meaning, quality, delivery and change |
| Dead-letter store | Where messages that cannot be processed are kept for inspection and replay |
| Deduplication window | How far back the system remembers identities to refuse repeats |
| ELT | Land raw data first and transform in the target |
| Headroom | The fraction of a target left unused by a budget |
| Idempotent | Applying the same input more than once has the same effect as applying it once |
| Lookback | Re-reading a short period before the last watermark to catch late-committed changes |
| Manifest | A file that describes another file or batch (name, count, checksum, total) |
| Materialised view | A stored copy of query results kept up to date by a flow |
| Quarantine | A holding area for data that failed validation |
| Reconciliation | Proving that source and target agree, at one or more levels |
| Replay | Re-processing past events or changes from a retained position |
| Seam | The point where an initial snapshot hands over to a change stream |
| Tombstone | A record that marks a delete so late older updates cannot resurrect the row |
| Version guard | A rule that applies an update only if its version is newer than the stored one |
| Weight-sensitive | A decision whose winner changes under an alternative weighting |

---

## Appendix B — Package checker, calculator and scenario runner (`check_integration_design.py`)

Python 3.9 or later; standard library only. It reads the Markdown tables in this file, recomputes every derived cell, runs the merge scenarios and reconciliation injections, and checks the package.

```python
#!/usr/bin/env python3
"""Consistency checker, calculator and scenario runner for the cross-system data integration
design package (D1-D17).

Usage:
    python3 check_integration_design.py FILE            verify every table, derived cell and cross-reference
    python3 check_integration_design.py FILE --fill     rewrite derived cells (marked ~) in place
    python3 check_integration_design.py FILE --trace 3 --seed 2026   random traceability walks

Exit code 0 means every check passed; 1 means at least one error.
A derived cell holds ~ when authored; --fill replaces it with the recomputed value. The check mode
recomputes every derived cell independently from the input cells and compares.
"""
import argparse
import ast
import math
import operator
import random
import re
import sys
from pathlib import Path

SEPARATOR = re.compile(r"^:?-{3,}:?$")
ID_CELL = re.compile(r"^[A-Z]{2,4}-\d{2,3}$")
PREFIXES = ("STK|SYS|CAP|AST|WLD|STD|REQ|CON|ASM|DEP|FLW|GT|CRT|WS|DEC|CAN|EXT|API|RTY|STM|LAG|LAT|BUD|"
            "AVC|FED|CTR|CHG|MAP|IDM|REC|DET|COV|INJ|SCN|ORD|CMP|FMX|OPS|DRL|STR|SEC|WLK|RSK|TRD|OQ|"
            "VAL|DL|FND|CH|CNT|ADR")
ID_ANY = re.compile(rf"\b(?:{PREFIXES})-\d{{2,3}}\b")
EVIDENCE = {"Given", "Assumed", "Derived", "Unknown"}
SCHEMA = {
    "STK": ["ID", "Stakeholder role", "Interest", "Decision rights", "Flows", "Evidence"],
    "SYS": ["ID", "System", "Role", "Business purpose", "Owner", "Interfaces", "Constraints", "Evidence"],
    "CAP": ["ID", "Capability", "System", "Status", "Limit", "Evidence"],
    "AST": ["ID", "Asset", "System", "Key", "Grain", "Sensitivity", "Owner", "Evidence"],
    "WLD": ["ID", "Workload line", "Asset", "Total records", "Daily records", "Record bytes", "Peak per s",
            "Avg per s", "Peak factor", "Daily GB", "Total GB", "Peak MB/s", "Growth per yr", "Horizon yr",
            "Horizon GB per day", "Evidence"],
    "STD": ["ID", "Standard", "Key", "Value", "Unit", "Evidence"],
    "REQ": ["ID", "Statement", "Type", "Flow", "Metric", "Target", "Method", "Source", "Priority",
            "Validated by", "Evidence"],
    "FLW": ["ID", "Flow", "From", "To", "Asset", "Pattern", "Trigger", "Expected volume", "Freshness target",
            "Transformation owner", "Contract", "Recovery", "Decision", "Evidence"],
    "GT": ["ID", "Gate", "Test", "Decisions", "Evidence"],
    "CRT": ["ID", "Criterion", "Weight", "Question it answers", "Locked on", "Evidence"],
    "WS": ["ID", "Weight set", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "Purpose"],
    "DEC": ["ID", "Decision", "Flow", "Requirements", "Selected", "Runner-up", "Weight-sensitive",
            "Conditional on", "ADR"],
    "CAN": ["ID", "Candidate", "Decision", "Baseline", "Requires", "Gates", "Gate failure reason", "C1", "C2",
            "C3", "C4", "C5", "C6", "C7", "C8", "Total", "Eligible", "Rank", "Limitation or risk", "Evidence"],
    "EXT": ["ID", "Batch line", "Flow", "Variant", "Workload", "Basis", "Volume GB", "Throughput MB/s",
            "Time s", "Window s", "Verdict", "Evidence"],
    "API": ["ID", "API line", "Flow", "Variant", "Workload", "Basis", "Page size", "Rate per s", "Runs per day",
            "Requests per run", "Pacing time s", "Window s", "Daily requests", "Quota per day", "Verdict",
            "Evidence"],
    "RTY": ["ID", "Retry line", "Base wait s", "Factor", "Waits", "Total wait s", "Budget s", "Verdict",
            "Evidence"],
    "STM": ["ID", "Stream line", "Flow", "Variant", "Workload", "Rate basis", "Event rate per s",
            "Event bytes", "MB per s", "Per-partition MB/s", "Headroom", "Partitions", "Hot key share",
            "Skew check", "Retention days", "Replication factor", "Retained TB", "Evidence"],
    "LAG": ["ID", "Backlog line", "Flow", "Variant", "Arrival per s", "Capacity during incident per s",
            "Incident s", "Capacity after per s", "Backlog records", "Catch-up s", "Target catch-up s",
            "Required capacity per s", "Verdict", "Evidence"],
    "LAT": ["ID", "Latency component", "Unit", "Value", "Evidence"],
    "BUD": ["ID", "Budget path", "Components", "Unit", "Total", "Target", "Headroom", "Verdict", "Evidence"],
    "AVC": ["ID", "Availability chain", "Flow", "Variant", "Availabilities", "Product", "Target", "Verdict",
            "Evidence"],
    "FED": ["ID", "Federation line", "Flow", "Variant", "Concurrent users", "Lookups per user per min",
            "Source requests per lookup", "Requests per s", "Source limit per s", "Share of limit", "Verdict",
            "Evidence"],
    "CTR": ["ID", "Contract", "Flow", "Producer", "Consumers", "Schema ref", "Key", "Required fields",
            "Optional fields", "Semantics", "Compatibility mode", "Upgrade order", "Replays history",
            "Notice days", "Quality and delivery", "Owner", "Evidence"],
    "CHG": ["ID", "Change", "Contract", "Change kind", "Semantic", "Backward", "Forward", "Class",
            "Allowed by mode", "Action", "Evidence"],
    "MAP": ["ID", "Mapping", "Flow", "Target field", "Source field or rule", "Where", "Transformation owner",
            "Evidence"],
    "IDM": ["ID", "Identity rule", "Flow", "Business key", "Event id", "Version field", "Dedup scope",
            "Dedup window h", "Key bytes", "Events per s", "State GB", "Merge rule", "Side effects",
            "Replay horizon h", "Evidence"],
    "REC": ["ID", "Reconciliation", "Flow", "Level", "Grain", "Window", "Tolerance", "Independence",
            "Frequency", "Output", "Owner", "Evidence"],
    "DET": ["ID", "Defect class", "Count", "Total", "Hash", "Key coverage", "Key and version",
            "Record comparison", "Domain invariant", "Independent extract", "Sample", "Evidence"],
    "COV": ["ID", "Coverage line", "Flow", "Controls", "Detected", "Partial only", "Undetected",
            "Compensating note", "Evidence"],
    "INJ": ["ID", "Injection", "Flow", "Defect", "Level", "Source rows", "Target rows", "Detected",
            "Expected", "Evidence"],
    "SCN": ["ID", "Scenario", "Flow", "Rule", "Kind", "Start state", "Events", "Expected final",
            "Computed final", "Outcome", "Reading"],
    "ORD": ["ID", "Ordering line", "Flow", "Ordering scope", "Late data policy", "Atomic publication",
            "Guarantee source", "Evidence"],
    "CMP": ["ID", "Component", "Flows", "Owner", "Evidence"],
    "FMX": ["ID", "Failure scenario", "Component", "Flow", "Detection", "Data impact", "Recovery",
            "Idempotency need", "Reconciliation need", "Owner", "Validation evidence", "Evidence"],
    "OPS": ["ID", "Signal", "Flow", "Kind", "Threshold", "Alert", "Owner", "Action", "Evidence"],
    "DRL": ["ID", "Failure drill", "Flow", "Scenario", "Pass criteria", "Frequency", "Owner", "Evidence"],
    "STR": ["ID", "Store or zone", "Holds", "Classification", "Retention", "Encryption", "Residency",
            "Owner", "Evidence"],
    "SEC": ["ID", "Control", "Flow", "Requirement", "Mechanism", "Owner", "Evidence"],
    "WLK": ["ID", "Walkthrough", "Flow", "Kind", "Category", "Outcome", "Evidence rows", "Reading"],
    "RSK": ["ID", "Risk", "Likelihood", "Impact", "Score", "Rating", "Mitigation", "Owner", "Trigger",
            "Decision", "Status"],
    "TRD": ["ID", "Trade-off", "Accepted cost", "Benefit", "Revisit trigger", "Decision"],
    "OQ": ["ID", "Open question", "Owner", "Needed by", "Blocks", "Evidence that settles it", "Status"],
    "VAL": ["ID", "Gate item", "Status", "Evidence in this file", "Reason"],
    "DL": ["ID", "Deliverable", "Section", "Version date", "Status"],
    "FND": ["ID", "Review area", "Finding", "Type", "Severity", "Status", "Resolution"],
    "CH": ["ID", "Reviewer objection", "Answer from recorded evidence", "Evidence ids"],
    "CNT": ["ID", "Package inventory", "Count"],
}
MARKER = {v[1]: k for k, v in SCHEMA.items()}
DERIVED = {
    "WLD": ["Avg per s", "Peak factor", "Daily GB", "Total GB", "Peak MB/s", "Horizon GB per day"],
    "EXT": ["Volume GB", "Time s", "Verdict"],
    "API": ["Requests per run", "Pacing time s", "Daily requests", "Verdict"],
    "RTY": ["Total wait s", "Verdict"],
    "STM": ["Event rate per s", "Event bytes", "MB per s", "Partitions", "Skew check", "Retained TB"],
    "LAG": ["Backlog records", "Catch-up s", "Required capacity per s", "Verdict"],
    "BUD": ["Total", "Headroom", "Verdict"],
    "AVC": ["Product", "Verdict"],
    "FED": ["Requests per s", "Share of limit", "Verdict"],
    "CHG": ["Backward", "Forward", "Class", "Allowed by mode"],
    "IDM": ["State GB"],
    "COV": ["Controls", "Detected", "Partial only", "Undetected"],
    "INJ": ["Detected"],
    "SCN": ["Computed final", "Outcome"],
    "CAN": ["Total", "Eligible", "Rank"],
    "DEC": ["Weight-sensitive"],
    "RSK": ["Score", "Rating"],
    "CNT": ["Count"],
}
NEEDS_EVIDENCE = {k for k, v in SCHEMA.items() if "Evidence" in v}
PLACEHOLDER = re.compile(r"\b(TBD|TODO|FIXME|XXX|lorem|\?\?\?)\b", re.I)
VAGUE = re.compile(r"\b(too complex|not scalable|legacy technology|old technology|not modern|"
                   r"industry standard|best practice)\b", re.I)
PRODUCTS = re.compile(r"\b(kafka|debezium|fivetran|airbyte|airflow|snowflake|databricks|bigquery|redshift|"
                      r"postgres(?:ql)?|mysql|oracle|sql server|salesforce|spark|flink|confluent|mulesoft|"
                      r"informatica|talend|striim|goldengate|aws|azure|gcp|dbt)\b", re.I)
SAFE_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
            ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
            ast.UAdd: operator.pos}
LEVELS = ["Count", "Total", "Hash", "Key coverage", "Key and version", "Record comparison",
          "Domain invariant", "Independent extract", "Sample"]
MERGE_RULES = ("append-dedup", "upsert-version-guard", "manifest-gate")
NAIVE_RULES = ("append-naive", "upsert-last-arrival", "load-all")
CHANGE_KINDS = {  # kind: (backward ok, forward ok); ? means depends on consumer evidence
    "add_optional": ("Y", "Y"), "add_required": ("N", "Y"), "remove_optional": ("Y", "?"),
    "remove_required": ("Y", "N"), "rename": ("N", "N"), "widen_type": ("Y", "N"),
    "narrow_type": ("N", "N"), "add_enum_value": ("Y", "?"), "optional_to_required": ("N", "Y"),
    "meaning_change": ("Y", "Y"), "unit_change": ("Y", "Y"),
}
SEMANTIC_KINDS = ("meaning_change", "unit_change")
MODES = ("BACKWARD", "BACKWARD_TRANSITIVE", "FORWARD", "FORWARD_TRANSITIVE", "FULL", "FULL_TRANSITIVE", "NONE")


# ----------------------------------------------------------------------------- helpers
def safe_eval(expr):
    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPS:
            return SAFE_OPS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPS:
            return SAFE_OPS[type(node.op)](walk(node.operand))
        raise ValueError(f"unsupported expression: {expr!r}")
    return walk(ast.parse(expr.strip(), mode="eval"))


def num(cell):
    c = cell.strip().replace(",", "").replace("$", "").replace("%", "")
    try:
        return float(c)
    except ValueError:
        return None


def f0(x):
    return f"{x:,.0f}"


def f1(x):
    return f"{x:,.1f}"


def f2(x):
    return f"{x:,.2f}"


def f3(x):
    return f"{x:,.3f}"


def pct(x):
    return f"{x * 100:.1f}%"


def refs(cell):
    return ID_ANY.findall(cell)


def split_list(cell):
    return [x.strip() for x in re.split(r"[,;]", cell) if x.strip() and x.strip() not in ("none", "n/a")]


# ----------------------------------------------------------------------------- parsing
def parse(text):
    tables = {k: {} for k in SCHEMA}
    errors, prose, diagrams, adr, locations = [], [], {}, {}, {}
    in_fence, fence, prev, header, kind = False, [], None, None, None
    current_adr = None
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_fence and fence and re.match(r"D\d+-DIAGRAM", fence[0]):
                diagrams[fence[0].split()[0]] = "\n".join(fence)
            in_fence, fence, prev, header, kind = not in_fence, [], None, None, None
            continue
        if in_fence:
            fence.append(line)
            continue
        prose.append(line)
        m = re.match(r"^#{3,5}\s+(ADR-\d{2})\b", stripped)
        if m:
            current_adr = m.group(1)
            adr[current_adr] = {"line": number, "body": [stripped]}
            continue
        if re.match(r"^#{1,6}\s", stripped):
            current_adr = None
        elif current_adr is not None:
            adr[current_adr]["body"].append(stripped)
        if not stripped.startswith("|"):
            prev = header = kind = None
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(SEPARATOR.match(c) for c in cells):
            header, prev = prev, None
            kind = MARKER.get(header[1]) if header and len(header) > 1 and header[0] == "ID" else None
            if kind and header != SCHEMA[kind]:
                errors.append(f"line {number}: header of {kind} table differs from the schema")
                kind = None
            continue
        if header is None:
            prev = cells
            continue
        if kind is None:
            continue
        if len(cells) != len(header):
            errors.append(f"line {number}: {cells[0]} has {len(cells)} cells, expected {len(header)}")
            continue
        if not ID_CELL.match(cells[0]) or not cells[0].startswith(kind_prefixes(kind)):
            errors.append(f"line {number}: ID {cells[0]!r} is not valid in a {kind} table")
            continue
        row = dict(zip(header, cells))
        row["_line"] = number
        if cells[0] in tables[kind]:
            errors.append(f"line {number}: duplicate ID {cells[0]}")
        tables[kind][cells[0]] = row
        locations[number] = (kind, cells[0])
    return tables, "\n".join(prose), diagrams, adr, errors, locations


def kind_prefixes(kind):
    return {"REQ": ("REQ-", "CON-", "ASM-", "DEP-")}.get(kind, (kind + "-",))


# ----------------------------------------------------------------------------- calculator
class Ctx:
    def __init__(self, tables):
        self.t = tables

    def std(self, key):
        for r in self.t["STD"].values():
            if r["Key"] == key:
                v = num(r["Value"])
                if v is None:
                    raise ValueError(f"standard {key} is not numeric")
                return v
        raise KeyError(f"standard {key} is not defined")

    # ---- workloads
    def wld(self, wid):
        r = self.t["WLD"][wid]
        total, daily = num(r["Total records"]), num(r["Daily records"])
        size, peak = num(r["Record bytes"]), num(r["Peak per s"])
        sec = self.std("seconds_per_day")
        avg = daily / sec if daily is not None else None
        return {"row": r, "total": total, "daily": daily, "bytes": size, "peak": peak, "avg": avg,
                "growth": num(r["Growth per yr"]), "horizon": num(r["Horizon yr"]),
                "daily_gb": daily * size / 1e9 if daily is not None else None,
                "total_gb": total * size / 1e9 if total is not None else None}

    def token(self, cell):
        """Number or WLD-nn:peak|avg|daily|total|bytes token."""
        v = num(cell)
        if v is not None:
            return v
        m = re.match(r"^(WLD-\d+):(peak|avg|daily|total|bytes|daily_gb|total_gb)$", cell.strip())
        if not m:
            raise ValueError(f"cannot resolve {cell!r}")
        w = self.wld(m.group(1))
        key = {"peak": "peak", "avg": "avg", "daily": "daily", "total": "total", "bytes": "bytes",
               "daily_gb": "daily_gb", "total_gb": "total_gb"}[m.group(2)]
        if w[key] is None:
            raise ValueError(f"{cell} is not available")
        return w[key]

    def throughput(self, cell):
        v = num(cell)
        return v if v is not None else self.std(cell.strip())

    # ---- selection
    def weights(self, set_id=None):
        if set_id is None:
            return [num(r["Weight"]) for r in sorted(self.t["CRT"].values(), key=lambda r: r["ID"])]
        r = self.t["WS"][set_id]
        return [num(r[f"C{i}"]) for i in range(1, 9)]

    def can_total(self, cid, set_id=None):
        r = self.t["CAN"][cid]
        return sum(w * num(r[f"C{i + 1}"]) for i, w in enumerate(self.weights(set_id)))

    def can_gates(self, cid):
        out = {}
        for part in split_list(self.t["CAN"][cid]["Gates"]):
            g, _, v = part.partition(":")
            out[g.strip()] = v.strip()
        return out

    def eligible(self, cid):
        return all(v == "P" for v in self.can_gates(cid).values())

    def ranking(self, dec_id, set_id=None):
        cands = [c for c in self.t["CAN"].values() if c["Decision"] == dec_id and self.eligible(c["ID"])]
        return sorted(((self.can_total(c["ID"], set_id), c["ID"]) for c in cands),
                      key=lambda x: (-round(x[0], 6), x[1]))

    def path(self, bid):
        r = self.t["BUD"][bid]
        total = sum(num(self.t["LAT"][c]["Value"]) for c in split_list(r["Components"]))
        head = 1 - total / num(r["Target"])
        return total, head, "Pass" if head >= self.std("headroom_min") - 1e-9 else "Fail"


# ----------------------------------------------------------------------------- simulations
def parse_rows(cell):
    rows = []
    for part in cell.split(";"):
        part = part.strip()
        if not part or part == "none":
            continue
        k, acct, amt = [x.strip() for x in part.split(":")]
        rows.append((k, acct, int(amt)))
    return rows


def inject(level, src, tgt):
    s, t = parse_rows(src), parse_rows(tgt)
    if level == "Count":
        return len(s) != len(t)
    if level == "Total":
        return sum(r[2] for r in s) != sum(r[2] for r in t)
    if level == "Hash":
        return sorted(s) != sorted(t)
    if level == "Key coverage":
        sk, tk = [r[0] for r in s], [r[0] for r in t]
        return set(sk) != set(tk) or len(set(tk)) != len(tk) or len(set(sk)) != len(sk)
    if level == "Record comparison":
        return sorted(s) != sorted(t)
    raise ValueError(f"level {level!r} cannot be simulated")


def run_scenario(rule, start, events):
    """Apply events under a rule; return the normalised final state."""
    ev = [e.strip() for e in events.split(";") if e.strip() and e.strip() != "none"]
    if rule in ("append-dedup", "append-naive"):
        state = []
        for item in [s for s in start.split(";") if s.strip() and s.strip() != "none"]:
            state.append(item.strip())
        seen = {s.split("=")[0] for s in state}
        for e in ev:
            eid, val = e.split(":")
            if rule == "append-dedup" and eid in seen:
                continue
            state.append(f"{eid}={val}")
            seen.add(eid)
        return ";".join(sorted(state))
    if rule in ("upsert-version-guard", "upsert-last-arrival"):
        state = {}
        for item in [s for s in start.split(";") if s.strip() and s.strip() != "none"]:
            key, rest = item.strip().split("=")
            val, ver = rest.split("@")
            state[key] = (val, int(ver))
        for e in ev:
            key, ver, val = e.split(":")
            ver = int(ver)
            if rule == "upsert-version-guard" and key in state and ver <= state[key][1]:
                continue
            state[key] = (val, ver)
        return ";".join(f"{k}={v}@{n}" for k, (v, n) in sorted(state.items()))
    if rule in ("manifest-gate", "load-all"):
        published, quarantined = [], []
        for e in ev:
            name, expected, actual, chk = e.split(":")
            if rule == "load-all" or (expected == actual and chk == "ok"):
                published.append(name)
            else:
                quarantined.append(name)
        return f"published={','.join(sorted(published)) or '-'}/quarantined={','.join(sorted(quarantined)) or '-'}"
    raise ValueError(f"unknown rule {rule!r}")


# ----------------------------------------------------------------------------- derivers
def derive_row(kind, row, ctx):
    t = ctx.t
    out = {}
    sec = ctx.std("seconds_per_day")
    if kind == "WLD":
        w = ctx.wld(row["ID"])
        out["Avg per s"] = f2(w["avg"]) if w["avg"] is not None else "n/a"
        out["Peak factor"] = f2(w["peak"] / w["avg"]) if (w["peak"] is not None and w["avg"]) else "n/a"
        out["Daily GB"] = f2(w["daily_gb"]) if w["daily_gb"] is not None else "n/a"
        out["Total GB"] = f2(w["total_gb"]) if w["total_gb"] is not None else "n/a"
        out["Peak MB/s"] = f2(w["peak"] * w["bytes"] / 1e6) if w["peak"] is not None else "n/a"
        if w["daily_gb"] is not None:
            out["Horizon GB per day"] = f2(w["daily_gb"] * (1 + w["growth"]) ** w["horizon"])
        else:
            out["Horizon GB per day"] = "n/a"
    elif kind == "EXT":
        w = ctx.wld(row["Workload"])
        gb = w["total_gb"] if row["Basis"] == "total" else w["daily_gb"]
        secs = gb * 1000 / ctx.throughput(row["Throughput MB/s"])
        out["Volume GB"] = f2(gb)
        out["Time s"] = f0(secs)
        out["Verdict"] = "Pass" if secs <= num(row["Window s"]) else "Fail"
    elif kind == "API":
        w = ctx.wld(row["Workload"])
        if row["Basis"] == "total":
            records = w["total"]
        elif row["Basis"] == "per-run":
            records = w["daily"] / num(row["Runs per day"])
        else:
            records = w["daily"]
        reqs = math.ceil(records / num(row["Page size"]))
        pacing = reqs / ctx.throughput(row["Rate per s"])
        daily = reqs * num(row["Runs per day"])
        out["Requests per run"] = f0(reqs)
        out["Pacing time s"] = f0(pacing)
        out["Daily requests"] = f0(daily)
        quota = num(row["Quota per day"])
        if pacing > num(row["Window s"]):
            out["Verdict"] = "Fail"
        elif quota is None:
            out["Verdict"] = "Conditional (quota unknown)"
        else:
            out["Verdict"] = "Pass" if daily <= quota else "Fail"
    elif kind == "RTY":
        total = sum(num(row["Base wait s"]) * num(row["Factor"]) ** i for i in range(int(num(row["Waits"]))))
        out["Total wait s"] = f0(total)
        out["Verdict"] = "Pass" if total <= num(row["Budget s"]) else "Fail"
    elif kind == "STM":
        w = ctx.wld(row["Workload"])
        rate = w["peak"] if row["Rate basis"] == "peak" else w["avg"]
        mbs = rate * w["bytes"] / 1e6
        per = num(row["Per-partition MB/s"])
        out["Event rate per s"] = f2(rate)
        out["Event bytes"] = f0(w["bytes"])
        out["MB per s"] = f2(mbs)
        out["Partitions"] = f0(math.ceil(mbs / per) * num(row["Headroom"]))
        out["Skew check"] = "Pass" if num(row["Hot key share"]) * mbs <= per else "Fail"
        out["Retained TB"] = f2(mbs * sec * num(row["Retention days"]) * num(row["Replication factor"]) / 1e6)
    elif kind == "LAG":
        a = ctx.token(row["Arrival per s"])
        pi, inc, pa = num(row["Capacity during incident per s"]), num(row["Incident s"]), \
            num(row["Capacity after per s"])
        backlog = max(0.0, a - pi) * inc
        target = num(row["Target catch-up s"])
        if backlog == 0:
            catch = 0.0
        elif pa > a:
            catch = backlog / (pa - a)
        else:
            catch = None
        out["Backlog records"] = f0(backlog)
        out["Catch-up s"] = f0(catch) if catch is not None else "never"
        out["Required capacity per s"] = f0(a + backlog / target)
        out["Verdict"] = "Pass" if catch is not None and catch <= target else "Fail"
    elif kind == "BUD":
        total, head, verdict = ctx.path(row["ID"])
        out["Total"] = f1(total)
        out["Headroom"] = pct(head)
        out["Verdict"] = verdict
    elif kind == "AVC":
        p = 1.0
        for a in split_list(row["Availabilities"]):
            p *= float(a)
        out["Product"] = f"{p * 100:.3f}%"
        out["Verdict"] = "Pass" if p * 100 >= num(row["Target"]) - 1e-9 else "Fail"
    elif kind == "FED":
        rps = num(row["Concurrent users"]) * num(row["Lookups per user per min"]) \
            * num(row["Source requests per lookup"]) / 60
        share = rps / num(row["Source limit per s"])
        out["Requests per s"] = f2(rps)
        out["Share of limit"] = pct(share)
        out["Verdict"] = "Pass" if share <= ctx.std("fed_max_share") + 1e-9 else "Fail"
    elif kind == "CHG":
        b, f = CHANGE_KINDS[row["Change kind"]]
        out["Backward"], out["Forward"] = b, f
        if row["Change kind"] in SEMANTIC_KINDS or row["Semantic"] == "Yes":
            cls = "Semantic break"
        elif b == "Y" and f == "Y":
            cls = "Full"
        elif b == "Y" and f == "N":
            cls = "Backward only"
        elif b == "N" and f == "Y":
            cls = "Forward only"
        elif "?" in (b, f) and "N" not in (b, f):
            cls = "Needs consumer evidence"
        else:
            cls = "Breaking"
        out["Class"] = cls
        mode = t["CTR"][row["Contract"]]["Compatibility mode"]
        need_b = mode.startswith(("BACKWARD", "FULL"))
        need_f = mode.startswith(("FORWARD", "FULL"))
        ok = cls != "Semantic break" and (not need_b or b == "Y") and (not need_f or f == "Y")
        out["Allowed by mode"] = "Yes" if ok else "No"
    elif kind == "IDM":
        events_per_s = ctx.token(row["Events per s"])
        gb = events_per_s * num(row["Dedup window h"]) * 3600 * num(row["Key bytes"]) / 1e9
        out["State GB"] = f2(gb)
    elif kind == "COV":
        levels = sorted({r["Level"] for r in t["REC"].values() if r["Flow"] == row["Flow"]}, key=LEVELS.index)
        det, part, und = [], [], []
        for did, d in sorted(t["DET"].items()):
            states = [d[lv] for lv in levels]
            if "Y" in states:
                det.append(did)
            elif "P" in states:
                part.append(did)
            else:
                und.append(did)
        out["Controls"] = ", ".join(levels) if levels else "none"
        out["Detected"] = ", ".join(det) or "none"
        out["Partial only"] = ", ".join(part) or "none"
        out["Undetected"] = ", ".join(und) or "none"
    elif kind == "INJ":
        out["Detected"] = "Yes" if inject(row["Level"], row["Source rows"], row["Target rows"]) else "No"
    elif kind == "SCN":
        final = run_scenario(row["Rule"], row["Start state"], row["Events"])
        out["Computed final"] = final
        out["Outcome"] = "Pass" if final == row["Expected final"] else "Fail"
    elif kind == "CAN":
        out["Total"] = f2(ctx.can_total(row["ID"]))
        elig = ctx.eligible(row["ID"])
        out["Eligible"] = "Yes" if elig else "No"
        rank = "-"
        if elig:
            better = sum(1 for s, _ in ctx.ranking(row["Decision"]) if round(s, 6) > round(ctx.can_total(row["ID"]), 6))
            rank = str(better + 1)
        out["Rank"] = rank
    elif kind == "DEC":
        flips = []
        for ws in sorted(t["WS"]):
            ranking = ctx.ranking(row["ID"], ws)
            if ranking and ranking[0][1] != row["Selected"]:
                flips.append(ws)
        out["Weight-sensitive"] = ("Yes (" + ", ".join(flips) + ")") if flips else "No"
    elif kind == "RSK":
        score = num(row["Likelihood"]) * num(row["Impact"])
        out["Score"] = f0(score)
        out["Rating"] = "High" if score >= 15 else "Medium" if score >= 8 else "Low"
    elif kind == "CNT":
        out["Count"] = f0(count_of(row["Package inventory"], ctx))
    return out


COUNT_KEYS = {
    "Stakeholder roles": "STK", "Systems": "SYS", "Source capabilities": "CAP", "Data assets": "AST",
    "Requirements": "REQ-", "Constraints": "CON-", "Assumptions": "ASM-", "Dependencies": "DEP-",
    "Flows": "FLW", "Decisions": "DEC", "Candidates": "CAN", "Contracts": "CTR", "Contract changes": "CHG",
    "Mappings": "MAP", "Reconciliation controls": "REC", "Injection tests": "INJ",
    "State scenarios": "SCN", "Components": "CMP", "Failure modes": "FMX", "Alerts": "OPS",
    "Walkthroughs": "WLK", "Risks": "RSK", "Open questions": "OQ", "Gates": "GT",
}


def count_of(label, ctx):
    key = COUNT_KEYS[label.strip()]
    if key.endswith("-"):
        return sum(1 for rid in ctx.t["REQ"] if rid.startswith(key))
    return len(ctx.t[key])


# ----------------------------------------------------------------------------- checks
def check(tables, prose, diagrams, adr):
    errors = []
    err = errors.append
    ctx = Ctx(tables)
    t = tables

    minima = dict(STK=8, SYS=8, CAP=12, AST=4, WLD=4, STD=14, REQ=28, FLW=6, GT=7, CRT=8, WS=4, DEC=7,
                  CAN=24, EXT=4, API=3, RTY=2, STM=3, LAG=3, LAT=8, BUD=4, AVC=2, FED=1, CTR=6, CHG=10,
                  MAP=20, IDM=6, REC=12, DET=10, COV=6, INJ=10, SCN=10, ORD=6, CMP=10, FMX=12, OPS=14,
                  DRL=2, STR=5, SEC=8, WLK=18, RSK=8, TRD=5, OQ=6, VAL=10, DL=17, FND=4, CH=2, CNT=10)
    for kind, minimum in minima.items():
        if len(t[kind]) < minimum:
            err(f"table {kind} has {len(t[kind])} rows; at least {minimum} required")

    known = {rid for kind in t for rid in t[kind]} | set(adr)
    for kind, rows in t.items():
        for rid, row in rows.items():
            for col, cell in row.items():
                if col == "_line":
                    continue
                if PLACEHOLDER.search(cell):
                    err(f"{rid}: placeholder text in column {col}")
                if cell == "":
                    err(f"{rid}: empty cell in column {col}")
                if cell == "~" and col not in DERIVED.get(kind, []):
                    err(f"{rid}: column {col} is not a derived column")
                if col != "ID":
                    for ref in refs(cell):
                        if ref not in known:
                            err(f"{rid}: {col} references unknown ID {ref}")
                    if PRODUCTS.search(cell):
                        err(f"{rid}: {col} names a product ({PRODUCTS.search(cell).group(0)}); keep to categories")
            if "Evidence" in row and kind != "CH" and row["Evidence"] not in EVIDENCE:
                err(f"{rid}: Evidence must be one of {sorted(EVIDENCE)}, found {row['Evidence']!r}")
    if errors:
        return errors
    for kind in DERIVED:
        for rid, row in t[kind].items():
            try:
                expected = derive_row(kind, row, ctx)
            except (KeyError, ValueError, TypeError, ZeroDivisionError, AttributeError, IndexError) as exc:
                err(f"{rid}: cannot recompute derived cells ({type(exc).__name__}: {exc})")
                continue
            for col, val in expected.items():
                if row[col] == "~":
                    err(f"{rid}: derived cell {col} not filled (run --fill); expected {val}")
                elif row[col] != val:
                    err(f"{rid}: {col} is {row[col]!r}; recomputed {val!r}")
    if errors:
        return errors

    flows = set(t["FLW"])

    def flow_list(cell):
        out = []
        for x in split_list(cell):
            if x == "all":
                out.extend(flows)
            else:
                out.append(x)
        return out

    # ---- stakeholders, systems, capabilities, assets, workloads
    for sid, s in t["SYS"].items():
        if s["Role"] not in ("Source", "Target", "Both"):
            err(f"{sid}: role {s['Role']!r} invalid")
        if s["Owner"] not in t["STK"] and s["Owner"] != "Unknown":
            err(f"{sid}: owner {s['Owner']} is not a stakeholder or Unknown")
    for cid, c in t["CAP"].items():
        if c["Status"] not in ("Yes", "No", "Unknown"):
            err(f"{cid}: status {c['Status']!r} invalid")
        if c["System"] not in t["SYS"]:
            err(f"{cid}: system unknown")
        if c["Status"] == "Unknown" and not any(cid in o["Blocks"] for o in t["OQ"].values()):
            err(f"{cid}: unknown capability without an open question that names it")
    for aid, a in t["AST"].items():
        if a["System"] not in t["SYS"]:
            err(f"{aid}: system unknown")
        if a["Sensitivity"] not in ("Personal", "Financial", "Internal", "Public"):
            err(f"{aid}: sensitivity {a['Sensitivity']!r} invalid")
        if a["Owner"] not in t["STK"] and a["Owner"] != "Unknown":
            err(f"{aid}: owner invalid")
        if not any(r["Asset"] == aid for r in t["WLD"].values()):
            err(f"{aid}: no workload line")
        if not any(aid in f["Asset"] for f in t["FLW"].values()):
            err(f"{aid}: not carried by any flow")
    for wid, w in t["WLD"].items():
        if w["Asset"] not in t["AST"]:
            err(f"{wid}: asset unknown")
    for fid, f in t["FLW"].items():
        for end in ("From", "To"):
            for s in split_list(f[end]):
                if s not in t["SYS"]:
                    err(f"{fid}: {end} system {s} unknown")
                elif t["SYS"][s]["Owner"] == "Unknown" and not any(s in o["Blocks"] for o in t["OQ"].values()):
                    err(f"{fid}: {s} has an unknown owner and no open question")
        for a in split_list(f["Asset"]):
            if a not in t["AST"]:
                err(f"{fid}: asset {a} unknown")
        if f["Transformation owner"] not in t["STK"]:
            err(f"{fid}: transformation owner invalid")
        if f["Contract"] not in t["CTR"]:
            err(f"{fid}: contract unknown")
        dec = t["DEC"].get(f["Decision"])
        if dec is None:
            err(f"{fid}: decision unknown")
        elif not f["Pattern"].startswith(dec["Selected"]):
            err(f"{fid}: pattern must start with the selected candidate {dec['Selected']}")
        # coverage per flow
        for kind, label in (("IDM", "identity rule"), ("REC", "reconciliation control"), ("COV", "coverage line"),
                            ("ORD", "ordering line"), ("MAP", "mapping"), ("FMX", "failure mode"),
                            ("OPS", "alert"), ("CTR", "contract"), ("SCN", "state scenario")):
            if kind == "SCN" and fid not in ("FLW-01", "FLW-02", "FLW-03", "FLW-06"):
                continue
            if not any(fid in flow_list(r["Flow"]) for r in t[kind].values()):
                err(f"{fid}: no {label}")
        kinds = {r["Kind"] for r in t["OPS"].values() if fid in flow_list(r["Flow"])}
        for need in ("Freshness", "Absence", "Reconciliation"):
            if need not in kinds:
                err(f"{fid}: no {need} alert (alert on absence and staleness, not only errors)")
        if not any(fid in flow_list(r["Flow"]) for r in t["WLK"].values()):
            err(f"{fid}: no walkthrough")

    # ---- requirements and traceability
    for rid, r in t["REQ"].items():
        expected_type = {"REQ": "Requirement", "CON": "Constraint", "ASM": "Assumption",
                         "DEP": "Dependency"}[rid.split("-")[0]]
        if r["Type"] != expected_type:
            err(f"{rid}: ID prefix implies {expected_type} but type is {r['Type']}")
        if r["Priority"] not in ("Must", "Should", "Could"):
            err(f"{rid}: priority invalid")
        for f in flow_list(r["Flow"]):
            if f not in flows:
                err(f"{rid}: flow {f} unknown")
        if r["Type"] in ("Requirement", "Constraint"):
            if not any(rid in d["Requirements"] for d in t["DEC"].values()):
                err(f"{rid}: not cited by any decision")
            if not refs(r["Validated by"]):
                err(f"{rid}: no validation reference")
        if r["Type"] == "Assumption":
            if not [x for x in refs(r["Validated by"]) if x.split("-")[0] in
                    ("SCN", "INJ", "BUD", "LAG", "API", "EXT", "STM", "OQ", "FMX", "DRL", "AVC", "FED", "RTY", "IDM")]:
                err(f"{rid}: assumption without a validation reference")
    # ---- selection discipline
    if abs(sum(num(r["Weight"]) for r in t["CRT"].values()) - 1) > 1e-9:
        err("criteria weights do not sum to 1")
    for wsid, r in t["WS"].items():
        if abs(sum(num(r[f"C{i}"]) for i in range(1, 9)) - 1) > 1e-9:
            err(f"{wsid}: weights do not sum to 1")
    if "WS-00" not in t["WS"] or [num(t["WS"]["WS-00"][f"C{i}"]) for i in range(1, 9)] != ctx.weights():
        err("WS-00 must equal the locked criteria weights")
    d8 = next((r for r in t["DL"].values() if r["Deliverable"].startswith("D6 ")), None)
    d4 = next((r for r in t["DL"].values() if r["Deliverable"].startswith("D4 ")), None)
    for cid, c in t["CRT"].items():
        if d8 and c["Locked on"] > d8["Version date"]:
            err(f"{cid}: criteria locked after the comparison matrix date")
    if d4 and d8 and d4["Version date"] > d8["Version date"]:
        err("D4 requirements are dated after the D6 comparison")
    gate_dec = {g: set(refs(r["Decisions"])) for g, r in t["GT"].items()}
    for gid, ds in gate_dec.items():
        if not ds:
            err(f"{gid}: gate applies to no decision")
    for did, d in t["DEC"].items():
        cands = [c for c in t["CAN"].values() if c["Decision"] == did]
        elig = [c for c in cands if ctx.eligible(c["ID"])]
        if len(elig) < 3:
            err(f"{did}: {len(elig)} eligible candidates; at least 3 required")
        if sum(1 for c in cands if c["Baseline"] == "Yes") != 1:
            err(f"{did}: exactly one baseline (simplest adequate) candidate required")
        for f in flow_list(d["Flow"]):
            if f not in flows:
                err(f"{did}: flow {f} unknown")
        ranking = ctx.ranking(did)
        if ranking:
            if d["Selected"] not in t["CAN"] or t["CAN"][d["Selected"]]["Decision"] != did:
                err(f"{did}: selected candidate invalid")
            elif ranking[0][1] != d["Selected"]:
                err(f"{did}: selected {d['Selected']} is not rank 1 at the locked weights ({ranking[0][1]})")
            want = ranking[1][1] if len(ranking) > 1 else "none"
            if d["Runner-up"] != want:
                err(f"{did}: runner-up should be {want}")
        if d["Weight-sensitive"].startswith("Yes") and d["Conditional on"] in ("none", "n/a"):
            err(f"{did}: weight-sensitive decision without a conditional note")
        if d["ADR"] not in adr:
            err(f"{did}: ADR missing")
        for c in cands:
            gates = ctx.can_gates(c["ID"])
            applicable = {g for g, ds in gate_dec.items() if did in ds}
            if set(gates) != applicable:
                err(f"{c['ID']}: gates {sorted(gates)} differ from those applicable to {did} {sorted(applicable)}")
            failed = [g for g, v in gates.items() if v == "F"]
            if any(v not in ("P", "F") for v in gates.values()):
                err(f"{c['ID']}: gate result invalid")
            if failed and c["Gate failure reason"] in ("none", "n/a"):
                err(f"{c['ID']}: gate failure without a reason")
            if gates.get("GT-09") == "F" and not any(
                    t["CAP"][x]["Status"] == "No" for x in split_list(c["Requires"]) if x in t["CAP"]):
                err(f"{c['ID']}: GT-09 failed although every required capability is offered or unknown")
            if not failed and c["Gate failure reason"] not in ("none", "n/a"):
                err(f"{c['ID']}: a reason is given but no gate failed")
            for b in refs(c["Gate failure reason"]):
                kind = b.split("-")[0]
                if kind in ("BUD", "EXT", "API", "FED", "AVC", "LAG", "STM", "RTY"):
                    v = t[kind][b]["Verdict"] if "Verdict" in t[kind][b] else t[kind][b].get("Skew check")
                    if v == "Pass":
                        err(f"{c['ID']}: cites {b} as the failure reason but that row passes")
            if VAGUE.search(c["Gate failure reason"]) or VAGUE.search(c["Candidate"]):
                err(f"{c['ID']}: vague wording")
            for i in range(1, 9):
                s = num(c[f"C{i}"])
                if s is None or s != int(s) or not 1 <= s <= 5:
                    err(f"{c['ID']}: score C{i} must be an integer 1-5")
            # capability evidence
            for cap in split_list(c["Requires"]):
                if cap not in t["CAP"]:
                    err(f"{c['ID']}: requires unknown capability {cap}")
                    continue
                st = t["CAP"][cap]["Status"]
                if st == "No" and ctx.can_gates(c["ID"]).get("GT-09") != "F":
                    err(f"{c['ID']}: requires {cap}, which the source does not offer, but gate GT-09 is not failed")
                if st == "No" and ctx.eligible(c["ID"]):
                    err(f"{c['ID']}: eligible although it requires {cap}, which the source does not offer")
                if st == "Unknown" and c["Decision"] and d["Selected"] == c["ID"] \
                        and not refs(d["Conditional on"]):
                    err(f"{did}: selected candidate depends on unknown capability {cap} without a conditional note")
    # ---- quantitative discipline: chosen rows pass, rejected alternatives fail
    for kind in ("EXT", "API", "STM", "LAG", "AVC", "FED"):
        for rid, r in t[kind].items():
            if r["Flow"] not in flows and r["Flow"] != "all":
                err(f"{rid}: flow unknown")
            verdict = r.get("Verdict") or r.get("Skew check")
            if r["Variant"] not in ("Chosen", "Rejected alternative"):
                err(f"{rid}: variant invalid")
            elif r["Variant"] == "Chosen" and verdict not in ("Pass", "Conditional (quota unknown)"):
                err(f"{rid}: the chosen design fails its own budget ({verdict})")
            elif r["Variant"] == "Rejected alternative" and verdict == "Pass":
                err(f"{rid}: a rejected alternative should fail its budget (otherwise why reject it)")
            if verdict and verdict.startswith("Conditional") and not any(
                    c["Status"] == "Unknown" and c["ID"] in r["Evidence"] + " " + r.get("Quota per day", "")
                    for c in t["CAP"].values()) and r["Evidence"] != "Assumed":
                pass
    for bid, b in t["BUD"].items():
        if "(chosen)" in b["Budget path"] and b["Verdict"] != "Pass":
            err(f"{bid}: the chosen design's freshness budget must pass")
    for rid in ("RTY",):
        for k, r in t[rid].items():
            if r["Verdict"] != "Pass":
                err(f"{k}: retry budget exceeded")
    for bid in t["BUD"]:
        pass
    for bid, b in t["BUD"].items():
        for c in split_list(b["Components"]):
            if t["LAT"][c]["Unit"] != b["Unit"]:
                err(f"{bid}: component {c} unit differs")
    # ---- contracts
    for cid, c in t["CTR"].items():
        for fl in flow_list(c["Flow"]):
            if fl not in flows:
                err(f"{cid}: flow {fl} unknown")
        if c["Compatibility mode"] not in MODES:
            err(f"{cid}: mode invalid")
        mode = c["Compatibility mode"]
        if c["Upgrade order"] not in ("Consumers first", "Producer first", "Either"):
            err(f"{cid}: upgrade order invalid")
        if c["Upgrade order"] == "Consumers first" and not mode.startswith(("BACKWARD", "FULL")):
            err(f"{cid}: consumers upgrade first, which needs a backward-compatible mode")
        if c["Upgrade order"] == "Producer first" and not mode.startswith(("FORWARD", "FULL")):
            err(f"{cid}: the producer upgrades first, which needs a forward-compatible mode")
        if c["Upgrade order"] == "Either" and not mode.startswith("FULL"):
            err(f"{cid}: upgrade order is open, which needs a full mode")
        if c["Replays history"] == "Yes" and not mode.startswith(("BACKWARD", "FULL")):
            err(f"{cid}: new readers replay old data, which needs backward compatibility")
        if c["Replays history"] not in ("Yes", "No"):
            err(f"{cid}: replay flag invalid")
        notice = num(c["Notice days"])
        if notice is None or notice < ctx.std("notice_days_min"):
            err(f"{cid}: notice period below the {ctx.std('notice_days_min'):.0f}-day minimum")
        if c["Owner"] not in t["STK"]:
            err(f"{cid}: owner invalid")
        if not re.search(r"\b(null|absent|missing)\b", c["Semantics"], re.I):
            err(f"{cid}: semantics must say what null or absent means")
        if not re.search(r"\b(unit|minor|currency|UTC|timezone|time zone)\b", c["Semantics"], re.I):
            err(f"{cid}: semantics must state units or time conventions")
        if c["Key"] == "none" or not split_list(c["Required fields"]):
            err(f"{cid}: key or required fields missing")
        if c["Producer"] not in t["SYS"]:
            err(f"{cid}: producer unknown")
    sem = [c for c in t["CHG"].values() if c["Class"] == "Semantic break"]
    if not any(CHANGE_KINDS[c["Change kind"]] == ("Y", "Y") and c["Semantic"] == "Yes" for c in sem):
        err("no structurally valid but semantically breaking change is recorded")
    for cid, c in t["CHG"].items():
        if c["Semantic"] not in ("Yes", "No"):
            err(f"{cid}: semantic flag invalid")
        if (c["Change kind"] in SEMANTIC_KINDS) != (c["Semantic"] == "Yes"):
            err(f"{cid}: semantic flag disagrees with the change kind")
        if c["Allowed by mode"] == "No" and not re.search(
                r"new version|reject|staged|expand|dual|consumer", c["Action"], re.I):
            err(f"{cid}: change not allowed by the mode but the action does not route it through a safe process")
        if c["Allowed by mode"] == "Yes" and re.search(r"\breject\b", c["Action"], re.I):
            err(f"{cid}: change allowed by the mode but the action rejects it")
    # mapping coverage
    for cid, c in t["CTR"].items():
        mapped = set()
        for m in t["MAP"].values():
            if m["Flow"] in flow_list(c["Flow"]):
                mapped.update(split_list(m["Target field"]))
        for fld in split_list(c["Required fields"]) + split_list(c["Optional fields"]):
            if fld not in mapped:
                err(f"{cid}: field {fld} has no source or rule in the mappings for {c['Flow']}")
    for mid, m in t["MAP"].items():
        if m["Where"] not in ("Source side", "Extract", "Load", "Transform in target"):
            err(f"{mid}: where invalid")
        if m["Transformation owner"] not in t["STK"]:
            err(f"{mid}: owner invalid")
        if m["Flow"] not in flows:
            err(f"{mid}: flow unknown")
    # ---- idempotency
    for iid, i in t["IDM"].items():
        if i["Merge rule"] not in MERGE_RULES:
            err(f"{iid}: merge rule invalid")
        if i["Merge rule"] == "append-dedup" and i["Event id"] == "none":
            err(f"{iid}: append with dedup needs an event id")
        if i["Merge rule"] == "upsert-version-guard" and i["Version field"] == "none":
            err(f"{iid}: version-guarded upsert needs a version field")
        if num(i["Dedup window h"]) < num(i["Replay horizon h"]):
            err(f"{iid}: dedup window is shorter than the replay horizon, so a replay can duplicate")
        if i["Business key"] == "none":
            err(f"{iid}: business key missing")
    # ---- reconciliation
    for rid, r in t["REC"].items():
        if r["Level"] not in LEVELS:
            err(f"{rid}: level invalid")
        if r["Independence"] not in ("Independent", "Shared logic", "n/a"):
            err(f"{rid}: independence invalid")
        if r["Owner"] not in t["STK"]:
            err(f"{rid}: owner invalid")
        if r["Flow"] not in flows:
            err(f"{rid}: flow unknown")
    for fid, f in t["FLW"].items():
        lv = {r["Level"] for r in t["REC"].values() if r["Flow"] == fid}
        if not lv & {"Count", "Total"}:
            err(f"{fid}: no count or total control")
        if not lv & {"Key coverage", "Key and version", "Record comparison", "Independent extract"}:
            err(f"{fid}: no key-level or independent control")
    zero = {r["Flow"] for r in t["REQ"].values() if "zero tolerance" in r["Target"].lower()}
    for rid, r in t["REC"].items():
        if r["Flow"] in zero and r["Level"] in ("Total", "Record comparison") and num(r["Tolerance"]) != 0:
            err(f"{rid}: zero-tolerance flow with a non-zero tolerance")
    for cid, c in t["COV"].items():
        if c["Undetected"] != "none" and c["Compensating note"] in ("none", "n/a"):
            err(f"{cid}: undetected defect classes without a compensating note")
        if c["Flow"] not in flows:
            err(f"{cid}: flow unknown")
    for did, d in t["DET"].items():
        for lv in LEVELS:
            if d[lv] not in ("Y", "P", "N"):
                err(f"{did}: {lv} must be Y, P or N")
    for iid, i in t["INJ"].items():
        if i["Expected"] != i["Detected"]:
            err(f"{iid}: expected detection {i['Expected']} but the level gives {i['Detected']}")
        d = t["DET"].get(i["Defect"])
        if d is None:
            err(f"{iid}: defect class unknown")
            continue
        cell = d[i["Level"]]
        if cell == "Y" and i["Detected"] != "Yes":
            err(f"{iid}: the detection matrix says {i['Level']} detects this defect but the test does not")
        if cell == "N" and i["Detected"] != "No":
            err(f"{iid}: the detection matrix says {i['Level']} misses this defect but the test detects it")
    # defect classes must each be injected at least once with a detecting and a missing level where relevant
    if not any(i["Detected"] == "No" for i in t["INJ"].values()):
        err("no injection test shows a defect that a control misses")
    # ---- state scenarios
    for sid, s in t["SCN"].items():
        if s["Kind"] not in ("Normal", "Failure", "Rejected alternative"):
            err(f"{sid}: kind invalid")
        if s["Kind"] == "Rejected alternative":
            if s["Rule"] not in NAIVE_RULES:
                err(f"{sid}: a rejected alternative must use a naive rule")
            if s["Outcome"] != "Fail":
                err(f"{sid}: a rejected alternative should fail (otherwise why reject it)")
        else:
            rules = {i["Merge rule"] for i in t["IDM"].values() if i["Flow"] == s["Flow"]}
            if s["Rule"] not in rules:
                err(f"{sid}: rule {s['Rule']} is not the merge rule of {s['Flow']}")
            if s["Outcome"] != "Pass":
                err(f"{sid}: the chosen rule fails its scenario")
    # ---- ordering, components, failure modes, operations
    for oid, o in t["ORD"].items():
        if o["Guarantee source"] not in ("Documented", "Assumed", "Unknown"):
            err(f"{oid}: guarantee source invalid")
        if o["Guarantee source"] == "Unknown" and not refs(o["Late data policy"] + o["Ordering scope"]):
            err(f"{oid}: unknown guarantee without a referenced open question")
    for cid, c in t["CMP"].items():
        if c["Owner"] not in t["STK"]:
            err(f"{cid}: owner invalid")
        if not any(r["Component"] == cid for r in t["FMX"].values()):
            err(f"{cid}: component has no failure scenario")
    for fid, f in t["FMX"].items():
        if f["Component"] not in t["CMP"]:
            err(f"{fid}: component unknown")
        if f["Owner"] not in t["STK"]:
            err(f"{fid}: owner invalid")
        if f["Flow"] not in flows and f["Flow"] != "all":
            err(f"{fid}: flow unknown")
        if not refs(f["Validation evidence"]):
            err(f"{fid}: no validation evidence reference")
    for oid, o in t["OPS"].items():
        if o["Owner"] not in t["STK"]:
            err(f"{oid}: alert owner invalid")
        if o["Kind"] not in ("Freshness", "Volume", "Lag", "Error", "Absence", "Reconciliation", "Cost"):
            err(f"{oid}: kind invalid")
        if len(o["Action"]) < 12 or o["Action"] in ("none", "n/a"):
            err(f"{oid}: alert without an action")
    for did, d in t["DRL"].items():
        if d["Owner"] not in t["STK"]:
            err(f"{did}: owner invalid")
        if not re.search(r"\d", d["Pass criteria"]):
            err(f"{did}: pass criteria must be measurable")
    # ---- stores, controls
    sensitive = {a for a, r in t["AST"].items() if r["Sensitivity"] in ("Personal", "Financial")}
    for need in ("Landing", "Dead-letter"):
        rows = [r for r in t["STR"].values() if need.lower() in r["Store or zone"].lower()]
        if not rows:
            err(f"no {need} store is described")
        for r in rows:
            held = set(refs(r["Holds"]))
            if sensitive - held:
                err(f"{r['ID']}: {need} store does not list sensitive assets {sorted(sensitive - held)}")
    for sid, s in t["STR"].items():
        if s["Classification"] in ("none", "n/a", "Unclassified"):
            err(f"{sid}: store without a classification label")
        if s["Owner"] not in t["STK"]:
            err(f"{sid}: owner invalid")
    for sid, s in t["SEC"].items():
        if not [x for x in refs(s["Requirement"]) if x in t["REQ"]]:
            err(f"{sid}: control not traced to a requirement")
        if s["Owner"] not in t["STK"]:
            err(f"{sid}: owner invalid")
    # ---- walkthroughs
    normal = [w for w in t["WLK"].values() if w["Kind"] == "Normal"]
    fail = [w for w in t["WLK"].values() if w["Kind"] == "Failure"]
    if len(normal) < 5:
        err(f"{len(normal)} normal walkthroughs; at least 5 required")
    if len(fail) < 8:
        err(f"{len(fail)} failure walkthroughs; at least 8 required")
    cats = {w["Category"] for w in fail}
    for need in ("Duplicate delivery", "Out-of-order update", "Replay", "Schema change", "Source outage",
                 "Incomplete file"):
        if need not in cats:
            err(f"failure category {need!r} not walked")
    if len(t["FMX"]) < 10:
        err("fewer than ten failure modes")
    if not any(r["Kind"] == "Failure" and r["Rule"] in MERGE_RULES for r in t["SCN"].values()):
        err("no failure state scenario")
    for wid, w in t["WLK"].items():
        if w["Kind"] not in ("Normal", "Failure"):
            err(f"{wid}: kind invalid")
        if w["Flow"] not in flows and w["Flow"] != "all":
            err(f"{wid}: flow unknown")
        ev = refs(w["Evidence rows"])
        if not ev:
            err(f"{wid}: no evidence rows")
        for e in ev:
            kind = e.split("-")[0]
            if kind in t and e in t[kind]:
                r = t[kind][e]
                v = r.get("Outcome") or r.get("Verdict") or r.get("Skew check") or r.get("Detected")
                if kind == "SCN" and r["Kind"] == "Rejected alternative":
                    err(f"{wid}: cites {e}, a rejected alternative, as evidence of the design's behaviour")
                if w["Outcome"] == "Pass" and v in ("Fail", "Small files"):
                    err(f"{wid}: outcome Pass although {e} fails")
        if w["Outcome"] not in ("Pass", "Pass with residual risk", "Fail"):
            err(f"{wid}: outcome invalid")
        if w["Outcome"] != "Pass" and "residual" not in w["Reading"].lower():
            err(f"{wid}: outcome {w['Outcome']} without a stated residual risk")
    # ---- diagram
    diagram = diagrams.get("D8-DIAGRAM", "")
    if not diagram:
        err("D8-DIAGRAM fence missing")
    else:
        in_sys = set(re.findall(r"\[(SYS-\d{2})\]", diagram))
        in_flw = set(re.findall(r"\((FLW-\d{2})\)", diagram))
        for sid in t["SYS"]:
            if sid not in in_sys:
                err(f"{sid}: missing from D8-DIAGRAM")
        for fid in t["FLW"]:
            if fid not in in_flw:
                err(f"{fid}: missing from D8-DIAGRAM")
        for x in in_sys - set(t["SYS"]):
            err(f"D8-DIAGRAM mentions unknown system {x}")
    # ---- risks, ADRs, honesty
    for rid, r in t["RSK"].items():
        if r["Owner"] not in t["STK"]:
            err(f"{rid}: owner invalid")
        if r["Status"] not in ("Open", "Mitigated", "Accepted"):
            err(f"{rid}: status invalid")
        for k in ("Likelihood", "Impact"):
            v = num(r[k])
            if v is None or v != int(v) or not 1 <= v <= 5:
                err(f"{rid}: {k} must be an integer 1-5")
        if r["Rating"] == "High" and r["Status"] == "Mitigated":
            err(f"{rid}: a High risk cannot be Mitigated without re-rating")
        if not [x for x in refs(r["Decision"]) if x.startswith("DEC-")]:
            err(f"{rid}: not linked to a decision")
    for rid, r in t["TRD"].items():
        if not [x for x in refs(r["Decision"]) if x.startswith("DEC-")]:
            err(f"{rid}: not linked to a decision")
    for oid, o in t["OQ"].items():
        if o["Owner"] not in t["STK"]:
            err(f"{oid}: owner invalid")
        if o["Status"] not in ("Open", "Closed"):
            err(f"{oid}: status invalid")
    labels = ("Status", "Context", "Decision", "Rejected alternatives", "Assumptions and risks",
              "Validation plan", "Revisit triggers")
    for did, d in t["DEC"].items():
        block = adr.get(d["ADR"])
        if block is None:
            continue
        body = "\n".join(block["body"])
        for label in labels:
            if not re.search(rf"\*\*{re.escape(label)}\.?\*\*", body):
                err(f"{d['ADR']}: label {label!r} missing")
        if did not in body:
            err(f"{d['ADR']}: does not cite {did}")
        if d["Selected"] not in body:
            err(f"{d['ADR']}: does not name the selected candidate {d['Selected']}")
        if VAGUE.search(body):
            err(f"{d['ADR']}: vague wording ({VAGUE.search(body).group(0)})")
        if PRODUCTS.search(body):
            err(f"{d['ADR']}: names a product ({PRODUCTS.search(body).group(0)})")
    for vid, v in t["VAL"].items():
        if v["Status"] not in ("Met", "Partly met", "Not met"):
            err(f"{vid}: status invalid")
        if v["Status"] != "Met" and v["Reason"] in ("none", "n/a"):
            err(f"{vid}: not fully met without a reason")
        if "independent reviewer" in v["Gate item"].lower() and v["Status"] == "Met" \
                and "STK-13" not in v["Evidence in this file"]:
            err(f"{vid}: independent review marked Met without a reviewer record (STK-13)")
    if not any(v["Status"] != "Met" for v in t["VAL"].values()):
        err("every gate item is Met; the independent-review item cannot be met by the author")
    for fid, f in t["FND"].items():
        if f["Severity"] not in ("Blocking", "Major", "Minor"):
            err(f"{fid}: severity invalid")
        if f["Status"] not in ("Open", "Closed"):
            err(f"{fid}: status invalid")
    if re.search(r"\bsponsor[- ]approved\b|\bindependently reviewed\b", prose, re.I):
        err("prose claims an approval or independent review that did not happen")
    return errors


# ----------------------------------------------------------------------------- fill / trace
def fill(path):
    text = Path(path).read_text(encoding="utf-8")
    tables, _, _, _, errors, locations = parse(text)
    if errors:
        for m in errors:
            print(f"ERROR {m}")
        return 1
    ctx = Ctx(tables)
    lines, changed = text.split("\n"), 0
    for number, (kind, rid) in locations.items():
        if kind not in DERIVED:
            continue
        row = tables[kind][rid]
        if not any(row[c] == "~" for c in DERIVED[kind]):
            continue
        try:
            expected = derive_row(kind, row, ctx)
        except (KeyError, ValueError, TypeError, ZeroDivisionError, AttributeError, IndexError) as exc:
            print(f"ERROR {rid}: cannot recompute derived cells ({type(exc).__name__}: {exc})")
            return 1
        cells = [row[c] for c in SCHEMA[kind]]
        for i, col in enumerate(SCHEMA[kind]):
            if col in expected and row[col] == "~":
                cells[i] = expected[col]
        lines[number - 1] = "| " + " | ".join(cells) + " |"
        changed += 1
    Path(path).write_text("\n".join(lines), encoding="utf-8")
    print(f"filled derived cells in {changed} row(s)")
    return 0


def trace(tables, n, seed):
    rnd = random.Random(seed)
    t = tables
    reqs = [r for r in t["REQ"] if r.split("-")[0] in ("REQ", "CON")]
    print("Forward (requirement -> decision -> flow -> contract -> controls -> evidence):")
    for rid in rnd.sample(reqs, min(n, len(reqs))):
        decs = [d for d in t["DEC"].values() if rid in d["Requirements"]]
        for d in decs[:1]:
            fl = [x for x in re.split(r"[,;]\s*", d["Flow"]) if x in t["FLW"]] or \
                [f["ID"] for f in t["FLW"].values() if f["Decision"] == d["ID"]]
            f0_ = fl[0] if fl else None
            ctr = t["FLW"][f0_]["Contract"] if f0_ else "-"
            idm = [i["ID"] for i in t["IDM"].values() if i["Flow"] == f0_][:1]
            rec = [r["ID"] for r in t["REC"].values() if r["Flow"] == f0_][:1]
            evid = [w["ID"] for w in t["WLK"].values() if w["Flow"] == f0_][:2]
            print(f"  {rid} -> {d['ID']} -> {f0_} -> {ctr} -> {','.join(idm + rec)} -> {','.join(evid) or 'no walk'}")
    print("Backward (decision -> requirements -> flows):")
    for did in rnd.sample(sorted(t["DEC"]), min(n, len(t["DEC"]))):
        d = t["DEC"][did]
        print(f"  {did} <- {d['Requirements']} <- {d['Flow']}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file")
    ap.add_argument("--fill", action="store_true")
    ap.add_argument("--trace", type=int, metavar="N")
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    if args.fill:
        return fill(args.file)
    tables, prose, diagrams, adr, errors, _ = parse(Path(args.file).read_text(encoding="utf-8"))
    if errors:
        for m in errors:
            print(f"ERROR {m}")
        print(f"{len(errors)} structural error(s); fix them first")
        return 1
    if args.trace:
        return trace(tables, args.trace, args.seed)
    try:
        errors += check(tables, prose, diagrams, adr)
    except (KeyError, TypeError, ValueError, AttributeError, ZeroDivisionError, IndexError) as exc:
        errors.append(f"checker could not complete ({type(exc).__name__}: {exc}); "
                      f"a table is probably missing or malformed")
    print("Parsed: " + ", ".join(f"{k}={len(v)}" for k, v in sorted(tables.items()) if v))
    for m in errors:
        print(f"ERROR {m}")
    print(f"{len(errors)} error(s)" if errors else "All checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

---

*End of document. Version 1.1, 2026-10-21.*
