# Project 05 — Storage Technology Selection and Logical Layout

> **Stage:** Stage 2D — Data Architecture
> **Module:** 2D.5 — Database and Storage Architecture
> **Project type:** Architecture selection and logical design exercise (a traceable, recomputable decision package; no physical design)
> **Roadmap source:** `roadmap-Database-and-Storage-Architecture.md`, Section 7
> **Project file:** `Projects/05-storage-technology-selection-and-logical-layout.md`

---

## 0. Document control

| Item | Value |
| --- | --- |
| Document | Project specification and worked reference, deliverables D1–D14 |
| Version | 1.1 (post-audit) |
| Date | 2026-10-21 |
| Status | Complete as a project specification and worked reference. **Every Northbridge value is illustrative. No stakeholder, legal authority or independent reviewer has confirmed anything in Section 6. The recommendation is conditional on five open questions (OQ-01, OQ-03, OQ-04, OQ-06, OQ-07).** |
| Audience | Learner running the project; independent reviewer auditing it |
| Scenario | *Northbridge Bank*, a fictional mid-sized retail and business bank (roadmap Section 7.2) |
| Evidence rule | Every fact-bearing row carries one of four labels: `Given`, `Assumed`, `Derived`, `Unknown` (Section 4.3) |
| Companion tool | Package checker and calculator, Appendix B (`check_storage_design.py`) |

**Change log**

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-10-21 | First complete design |
| 1.1 | 2026-10-21 | Post-audit (Section 7.7, FND-05 to FND-10): corrected four statements the numbers did not support; made the fraud serving-store collapse threshold consistent (25%); added a Limitation or risk column for all 32 candidates; added validation references for every requirement and constraint; stopped an independent review being marked Met without a reviewer record; fixed ADR block parsing; added a hand-calculation section for reviewers (7.8); ran 45 mutation tests and a prose-versus-table audit; confirmed the embedded checker equals the tested copy |

**Deliverable register** (version-dated; D3 precedes D6, and the criteria were locked between them)

| ID | Deliverable | Section | Version date | Status |
| --- | --- | --- | --- | --- |
| DL-01 | D1 Project scope and assumptions | 6.1 | 2026-10-14 | Complete as an illustrative worked reference |
| DL-02 | D2 Data asset inventory and stakeholders | 6.2 | 2026-10-14 | Complete as an illustrative worked reference |
| DL-03 | D3 Workload characterisation | 6.3 | 2026-10-16 | Complete as an illustrative worked reference |
| DL-04 | D4 Storage requirements and constraints register | 6.4 | 2026-10-16 | Complete as an illustrative worked reference |
| DL-05 | D5 Data volume and growth estimates | 6.5 | 2026-10-17 | Complete as an illustrative worked reference |
| DL-06 | D6 Technology category comparison matrix | 6.6 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-07 | D7 Storage technology selection rationale | 6.7 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-08 | D8 Logical storage architecture | 6.8 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-09 | D9 Data layout and access strategy | 6.9 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-10 | D10 Replication and consistency requirements | 6.10 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-11 | D11 Transaction boundary description | 6.11 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-12 | D12 Retention and storage-tier strategy | 6.12 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-13 | D13 Risk and trade-off register | 6.13 | 2026-10-21 | Complete as an illustrative worked reference |
| DL-14 | D14 Final architecture recommendation | 6.14 | 2026-10-21 | Complete as an illustrative worked reference |

**Reading order.** Sections 1–5 explain the project and how to run it. Section 6 is a complete worked reference (D1–D14) whose tables the checker parses and recomputes. Section 7 is the quality gate. Section 8 holds templates for a real organisation. Sections 9–11 cover pitfalls, hand-off and self-assessment. Appendix B is the checker.

---

## 1. Project overview

### 1.1 What this project is

A **storage technology selection and logical layout** is the decision record that answers, for every body of data an organisation keeps: *which kind of store holds it, in what format and arrangement, with what consistency and durability, and for how long.* It sits between a business problem ("analytics slow our payments at month-end") and a physical build ("this product, these instances, this schema").

This project produces that record for a fictional bank. It is deliberately a **logical architecture exercise**. It names categories (a relational store, an object store with an open table format, a time-series store), never products; it fixes how data are arranged (partition keys, sort order, prefixes) without writing DDL; and it stops before provider services, sizing of instances or pipelines. Those belong to modules 2D.6 to 2D.8.

What makes it different from a slide deck is that the decision is **recomputable**. Workload rates, growth, capacity, file counts, partition sizes, scan times, latency and freshness budgets, availability budgets, replication exposure, tier break-evens and cost are all written as numbers in Markdown tables. A stdlib Python checker (Appendix B) parses the tables, recomputes every derived cell from its inputs, re-scores the candidate matrix under five weight sets, walks the traceability graph and fails if anything disagrees.

```text
Scenario ─► workloads and access patterns ─► requirements and constraints ─► volumes and growth
   ─► gates and criteria (locked) ─► candidates scored ─► selection and system of record
   ─► layout, keys and partitions ─► consistency, replicas, transactions ─► retention, tiers, deletion
   ─► risks, trade-offs, ADRs ─► failure and access walks ─► recommendation and open items
```

### 1.2 Why organisations need it

| Situation | What goes wrong without a selection record | What this project provides |
| --- | --- | --- |
| Analytics and postings share a database | Month-end reports slow customer payments; the fix is argued by opinion | A workload profile, an isolation gate and a measured-or-estimated comparison of separation options |
| Technology is chosen first | Features drive the design; access patterns are discovered late | Access patterns listed before any candidate appears; criteria locked before scoring |
| A lake grows by copying | Nobody knows which copy is authoritative, retention differs per copy and erasure misses copies | A system-of-record register, a retention schedule with owners and a copy-by-copy deletion table |
| Cost is storage price only | Cheap archive tiers cost more once retrieval is counted | Break-even arithmetic that includes retrieval, fixed overhead and people |
| Consistency is "assumed" | A replica read after a failover shows a payment missing | An operation-to-guarantee table that says who provides each guarantee |

### 1.3 Business and architecture objectives

1. Keep payment posting fast and strongly consistent while analytics, fraud and risk read history without touching it.
2. Make every store's role explicit: system of record, derived copy, or transport.
3. Choose layouts that match real query shapes and prove it with arithmetic.
4. State, for every critical operation, the guarantee required, the consequence of failure and who provides it.
5. Make retention, tiering and deletion operable: sourced, owned, automated and verified, including copies and backups.
6. Leave a trail a reviewer can follow in both directions: requirement to decision and decision back to requirement.

### 1.4 What this project is not

- Not a product comparison, a vendor benchmark or a database administration tutorial.
- Not a physical design: no DDL, engine settings, index types or instance sizes.
- Not a cloud mapping (2D.8), a pipeline design (2D.6), a platform build (2D.7) or a disaster-recovery runbook (2D.12).
- Not evidence about any real bank. All scenario numbers are illustrative.

### 1.5 Success criteria

| Criterion | Evidence |
| --- | --- |
| Every workload has an access-pattern list, a classification and a measurable target | Section 6.3; checker rule: each workload has at least one access pattern |
| Every decision has at least three eligible candidates including a baseline, with criteria locked first | Section 6.6; checker verifies counts, weights and dates |
| Every estimate shows formula, unit, assumption and range | Section 6.5; checker recomputes every derived cell |
| Every layout element maps to an asset, a workload and an assumption | Section 6.9; checker enforces the links |
| Critical operations have a guarantee, a consequence and a provider | Section 6.10 |
| Every retention class has a source, owner and tier plan; every copy has a deletion path | Section 6.12 |
| At least five failure scenarios (including lag, zone loss, corruption and deletion) are walked | Section 6.14 |
| An independent reviewer agrees the evidence supports the conclusions | **Not met by design** in the worked reference (VAL-11) |

---

## 2. How to use this file

| Mode | Purpose | What you do |
| --- | --- | --- |
| **A. Worked reference** | Learn the method by reading and re-running a complete example | Read Section 6 in order; run the checker; change one assumption in the standards table (STD) or a growth rate and watch the derived cells and decisions respond; try to break a rule and read the error |
| **B. Real organisation** | Apply the method to your own estate | Copy the table headers from Section 8, fill them from your own workloads, replace every illustrative figure with measured or sourced values, keep the evidence labels honest, run the checker and give the result to an independent reviewer |

**Rules for either mode.**

1. Keep the column headers exactly; the checker identifies tables by their header row.
2. A derived cell is written `~` when authoring. `python3 check_storage_design.py FILE --fill` replaces each `~` with the recomputed value; the plain check recomputes everything again and reports any mismatch.
3. Mark unknown values `Unknown`, give them an open question and never size from them.
4. Do not edit scores after seeing the winner. If a score is wrong, record why and re-run the sensitivity test.
5. Keep the scope: when a decision needs a product, a price quote or a benchmark, write an open question for the later module.

---

## 3. Concepts applied

### 3.1 Topic-to-project mapping

| Module topic | What it teaches | Where this project uses it |
| --- | --- | --- |
| 1 OLTP, OLAP and separation | Classify by access pattern; separate only on evidence; synchronisation and freshness cost | Workload classes and the separation decision (6.3, DEC-01, ADR-01); the case where no separation is needed is the profile store (DEC-03) |
| 2 Relational, NoSQL, specialised | Selection matrix from access patterns; integrity enforced by the store or by the application; polyglot only when justified | Candidate matrices for ledger, profile, fraud window and telemetry (6.6); ADR-02, ADR-03, ADR-05, ADR-06 |
| 3 Object storage and file formats | Storage versus format versus layout; immutability; small files; file-count arithmetic | Landing and curated zones, media store, FIL worksheet, DEC-07, DEC-08 |
| 4 Warehouse, lakehouse, table formats | Layers (storage, table format, platform); snapshots and maintenance; erasure through time travel | DEC-04, the layer distinction in 6.7, snapshot expiry in COP-07 and RSK-06 |
| 5 Partitioning, indexing, clustering | Query patterns first; skew; partition size standards; validation experiments | PRT worksheet, LAY table, query walks QWK, validation plan in 6.9 |
| 6 Replication, consistency, transactions | Operation-to-guarantee mapping; lag budgets; RPO and RTO; outbox and idempotency; failure matrix | OPG, REP, BUD, TXB, failure scenarios FS |
| 7 Retention, archival, lifecycle tiers | Retention schedule with sources; tier economics; deletion across the copy graph; holds | RC, TP, BRK, COP, CST, FS-05, FS-07 |

### 3.2 Practice-question arithmetic reused

The module's quantitative problems (Q1–Q10 in `practice-questions.md`) are the building blocks of the calculator:

| Problem | Arithmetic | Project table |
| --- | --- | --- |
| Q1 Daily and retained volume | rate × size × days | WL (Daily GB), GRW |
| Q2 Average and peak write rate | per day ÷ 86,400 × peak factor | WL (Avg and Peak ops/s) |
| Q3 Compression and file count | raw ÷ ratio; MB ÷ target file size | FIL |
| Q4 Scan time after pruning | bytes × remaining fraction ÷ throughput | QWK |
| Q5 Storage, index and replica overhead | size × (1 + index) × copies | CAP |
| Q6 Retained volume with copies | rate × days × copies × (1 + overhead) | CAP (GRW-02:rate*90/365) |
| Q7 Replication lag exposure | rate × lag | REP (exposure columns) |
| Q8 Monthly cost across tiers | TB × price | CST |
| Q9 Archive break-even | (savings − fixed) ÷ retrieval price | BRK |
| Q10 Mixed retrieval scenarios | low, base and high retrieval | BRK (net low, base, high) |

### 3.3 Carry-in from earlier projects

| Earlier project | What this project takes from it |
| --- | --- |
| 01 Current-state inventory | The idea of an inventory with owners, sources and an evidence label per row; the asset inventory (6.2) follows it |
| 02 Requirements and decision pack | The requirement/constraint/assumption test and the ADR structure used in 6.4 and 6.14 |
| 03 Pattern comparison | The discipline of comparing every option against a baseline |
| 04 Logical data model | Ledger entries come from the Transaction and Account entities and profiles from the Party entities; a real engagement takes the identifier that joins stores (called the customer key here) from that model's identifier rules |

None of these is needed to run this file; each is cited so a real engagement can connect its own earlier outputs.

---

## 4. Project governance and conventions

### 4.1 Roles and decision rights (RACI)

R = does the work, A = accountable, C = consulted, I = informed.

| Activity | Architect (STK-12) | Sponsor (STK-01) | Workload owners | Security and Privacy (STK-09) | Legal and Records (STK-10) | Operations (STK-11) | Reviewer (STK-13) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Scope and assumptions | R | A | C | C | C | C | I |
| Workloads and access patterns | R | I | A | C | I | C | I |
| Requirements and constraints | R | A | C | C | C | C | I |
| Estimates | R | I | C | I | I | C | C |
| Criteria, gates and scoring | R | C | C | C | I | C | A for independence |
| Selection and ADRs | R | A | C | C | C | C | C |
| Layout and consistency | R | I | C | C | I | A for operability | C |
| Retention and deletion | R | I | C | C | A for sources | C | C |
| Risk acceptance | R | A | C | C | C | C | I |
| Independent review | I | I | I | I | I | I | R and A |

### 4.2 Status, severity and notation

| Item | Values |
| --- | --- |
| Open question status | Open, Closed |
| Risk rating | Score = likelihood × impact (each 1–5); High ≥ 15, Medium ≥ 8, Low otherwise |
| Finding severity | Blocking (stops use), Major (changes a decision or hides a gap), Minor (wording or evidence) |
| Failure outcome | Pass, Pass with residual risk, Fail |
| Candidate gate result | `GT-nn:P` (passed) or `GT-nn:F` (failed) |
| Guarantee source | System-provided, Architecture-provided, Assumption |
| Units | Decimal: 1 GB = 10⁹ bytes, 1 TB = 1,000 GB = 10⁶ MB; 1 day = 86,400 s; a month for availability = 30 days |

### 4.3 Evidence labels

| Label | Meaning |
| --- | --- |
| Given | Stated by the roadmap scenario (or, in Mode B, observed in the real organisation) |
| Assumed | Chosen by the author and registered; includes planning ranges and judgement scores |
| Derived | Computed from other cells by the checker |
| Unknown | Not known; an open question exists and nothing is sized from it |

### 4.4 ID conventions

| Prefix | Meaning | Prefix | Meaning |
| --- | --- | --- | --- |
| STK | Stakeholder role | LAY | Layout element |
| WL | Workload | AP | Access pattern |
| AST | Data asset | QWK | Query walk |
| REQ, CON, ASM, DEP | Requirement, constraint, assumption, dependency | OPG | Operation-to-guarantee row |
| STD | Standard (threshold or price) | REP | Replication line |
| GRW | Growth line | LAT, BUD | Latency component, budget path |
| CAP | Stored capacity row | AV | Availability budget |
| SEN | Sensitivity line | TXB | Transaction boundary |
| FIL | File arithmetic | RC, TP | Retention class, tier plan |
| PRT | Partition worksheet | BRK | Tier break-even |
| GT | Gate | CST, TCO | Cost line, total cost option |
| CRT, WS | Criterion, weight set | COP | Copy location |
| DEC | Decision | RSK, TRD | Risk, trade-off |
| CAN | Candidate | OQ | Open question |
| STO | Store | FS | Failure scenario |
| SOR | System-of-record entry | ADR | Architecture decision record |
| DL | Deliverable | VAL, FND, CH | Gate item, finding, challenge |
| CNT | Package inventory count | | |

### 4.5 Confidentiality and handling

In Mode B the package describes real data volumes, locations and weaknesses. Treat it as confidential: store it in the architecture workspace, restrict edit rights to the author, and never paste real customer identifiers into examples. The worked reference contains none.

### 4.6 Suggested workspace layout (Mode B, optional)

```text
storage-selection/
├── 05-storage-technology-selection-and-logical-layout.md   # this package, tables filled in
├── check_storage_design.py                                 # Appendix B
├── evidence/                                               # exports of rate data, size scans, quotes
├── reviews/                                                # reviewer notes and signed gate items
└── adr/                                                    # one record per decision, if kept separately
```

---

## 5. Execution plan

### 5.1 Timeline and effort (planning estimate, mid-sized organisation)

| Week | Steps | Output | Person-days |
| --- | --- | --- | --- |
| 1 | 1–3 | Scope, stakeholders, asset inventory | 5–7 |
| 2 | 4–7 | Workloads, access patterns, estimates, requirements register | 8–11 |
| 3 | 8–10 | Candidates, comparison, selection | 6–8 |
| 4 | 11–13 | Analytical approach, logical layout, partitions and indexes | 6–8 |
| 5 | 14–16 | Consistency, retention, risk and cost | 7–9 |
| 6 | 17–18 | ADRs, validation walks | 4–6 |
| 7 | 19 and review | Final summary, independent review, challenge round | 3–5 |
| | | **Total** | **39–54** |

These are planning estimates for a team that already has workload data; gathering rate and size evidence from scratch can double weeks 1–2.

### 5.2 Definitions of ready and done

- **Ready for a step:** its inputs exist, are labelled, and have owners.
- **Done for a step:** its output rows are filled, every derived cell is recomputed by the checker, and its validation row below passes.
- **Done for the project:** the completion gate in Section 7.5, with the independent-review item signed by a person who did not write the package.

### 5.3 The nineteen steps

Each step has the roadmap's six elements plus the practitioner guidance that keeps the step honest.

**Step 1 — Define the problem and scope** (D1)
- *Purpose:* fix what is decided and what is not.
- *Inputs:* the scenario or the sponsor's request.
- *Actions:* write a problem statement in business terms; list objectives; list exclusions (product choice, sizing, DDL, pipelines, cloud mapping); list labelled assumptions.
- *Questions to answer:* what decision will the sponsor take from this package? What is explicitly not decided?
- *Outputs:* scope and assumptions (6.1).
- *Validation:* a sponsor-role reviewer confirms scope and exclusions. State the exclusions firmly; a project that drifts into product selection never finishes.

**Step 2 — Identify stakeholders, consumers and workload owners** (D2)
- *Purpose:* make every workload accountable to a person.
- *Inputs:* scenario, organisation chart.
- *Actions:* register roles (not names); map each workload to an owner and its consumers; include security, privacy, legal and operations.
- *Questions:* who can accept a risk, who confirms a retention period, who runs the stores?
- *Outputs:* stakeholder and workload-owner list (6.2).
- *Validation:* every workload has an owner or the word `Unknown` with an open question.

**Step 3 — Inventory data assets and classify characteristics** (D2)
- *Purpose:* know what is stored before choosing where.
- *Inputs:* scenario, earlier models.
- *Actions:* list assets with category (structured, semi-structured, unstructured, time-series), size with unit, growth basis and range, owner, retention class, consumers and whether they hold personal data.
- *Questions:* what is this, where did it come from, who uses it?
- *Outputs:* data asset inventory (6.2).
- *Validation:* every asset has a category and a size with a unit, or `Unknown` plus an open question. Do not invent sizes.

**Step 4 — Characterise workloads** (D3)
- *Purpose:* classify by access pattern, not by system name.
- *Inputs:* steps 2–3.
- *Actions:* for each workload record class (OLTP, OLAP, mixed, specialised), daily operations or bytes, peak factor, target, consistency and availability.
- *Questions:* which are transactional, analytical, mixed or specialised, and what is the evidence?
- *Outputs:* workload characterisation (6.3).
- *Validation:* classification is justified by evidence; derived rates are recomputed (average and peak per second).

**Step 5 — Document access patterns and requirements** (D3)
- *Purpose:* describe the shapes that must be cheap.
- *Inputs:* step 4.
- *Actions:* list the top reads and writes as shapes ("by customer id", "range by date, group by segment"), their frequency, key columns and target.
- *Questions:* what does each workload need to be cheap, and which keys does it filter on?
- *Outputs:* access-pattern register (6.3).
- *Validation:* every workload has at least one access pattern; every pattern names a layout element, and its key columns appear in that element.

**Step 6 — Estimate volumes, growth, retention and peaks** (D5)
- *Purpose:* quantify capacity with ranges.
- *Inputs:* steps 3–5.
- *Actions:* write growth formulas with low, expected and high rates; cap by retention where data expire; compute stored capacity with index overhead and copies; compute file counts and partition sizes; find the dominant input.
- *Questions:* which input drives the total?
- *Outputs:* volume and growth estimates (6.5).
- *Validation:* each figure has unit, formula, assumption and range; the checker recomputes them; the sensitivity row names the dominant contributor.

**Step 7 — Record requirements, constraints, assumptions and risks** (D4)
- *Purpose:* separate what must be true from what is believed.
- *Inputs:* steps 1–6.
- *Actions:* classify with the 2D.2 tests; give every item an owner; give every assumption a way to be validated.
- *Questions:* which constraints eliminate options?
- *Outputs:* requirements and constraints register (6.4).
- *Validation:* no unclassified or ownerless item; every assumption has a validation reference; every requirement is cited by a decision.

**Step 8 — Identify candidate categories** (D6)
- *Purpose:* shortlist feasible options per decision.
- *Inputs:* steps 4–7, topics 1–2.
- *Actions:* define gates from hard constraints; list at least three feasible candidates per decision plus a minimal-change baseline.
- *Questions:* is each candidate relevant and feasible?
- *Outputs:* candidate list (6.6).
- *Validation:* gate failures are recorded with reasons and removed from scoring; each decision has exactly one baseline.

**Step 9 — Compare candidates** (D6)
- *Purpose:* compare transparently.
- *Inputs:* steps 5–8.
- *Actions:* lock criteria and weights (with a date) before scoring; score eligible candidates 1–5 with evidence; test the winner under alternative weight sets.
- *Questions:* where is the evidence weakest?
- *Outputs:* technology comparison matrix (6.6).
- *Validation:* same criteria and evidence standard for every candidate; criteria locked before the matrix date; weight-sensitive decisions are flagged.

**Step 10 — Select operational and analytical approaches** (D7)
- *Purpose:* decide separation and categories; name the system of record.
- *Inputs:* steps 1 and 9.
- *Actions:* take the top-ranked eligible candidate per decision; write the runner-up; register the system of record for each asset and the hand-off controls.
- *Questions:* is separation justified by evidence?
- *Outputs:* selection decisions (6.7).
- *Validation:* each choice cites workloads and requirements; the selected candidate is rank 1 at the locked weights.

**Step 11 — Determine the role of object storage, formats, warehouse, lakehouse and table formats** (D7)
- *Purpose:* assign layers without confusing them.
- *Inputs:* steps 9–10, topics 3–4.
- *Actions:* state, for every object-store-based store, what the storage layer, the table format and the platform each provide.
- *Questions:* what does each layer provide?
- *Outputs:* analytical storage approach (6.7, 6.8).
- *Validation:* no layer confusion; object stores name all three layers.

**Step 12 — Design the logical layout and organisation** (D8)
- *Purpose:* arrange the data so lifecycle and access control follow from the structure.
- *Inputs:* steps 10–11.
- *Actions:* define stores, zones, prefixes, tables, formats and access rules; draw the logical architecture with a legend and version; register authority.
- *Questions:* is every element traceable to a workload?
- *Outputs:* logical storage layout and diagram (6.8, 6.9).
- *Validation:* every store appears in the diagram and in the selection; every asset has a layout element.

**Step 13 — Evaluate partitioning, indexing, clustering and layout** (D9)
- *Purpose:* make access cheap without waste.
- *Inputs:* steps 5 and 12, topic 5.
- *Actions:* test candidate partition keys against size standards and skew; choose sort orders and indexes only where a pattern needs them; walk each scan through the layout; write validation experiments with pass criteria.
- *Questions:* what assumption makes this layout right?
- *Outputs:* data layout and access strategy (6.9).
- *Validation:* every layout element links to a query pattern; every accepted partition design passes the size standards; each rejected design has a reason.

**Step 14 — Define replication, consistency and transaction boundaries** (D10, D11)
- *Purpose:* decide what must never be lost or inconsistent.
- *Inputs:* steps 5 and 10, topic 6.
- *Actions:* write the operation-to-guarantee table; set replica-use rules; derive latency and freshness budgets; compute lag exposure; define transaction boundaries and reconciliations.
- *Questions:* what must never be lost, duplicated or shown stale?
- *Outputs:* consistency strategy and boundary description (6.10, 6.11).
- *Validation:* each guarantee ties to a business consequence and states whether the system or the architecture provides it; a strong guarantee never relies on an asynchronous replica.

**Step 15 — Define retention, archival and tier policies** (D12)
- *Purpose:* make lifecycle operable.
- *Inputs:* steps 6–7, topic 7.
- *Actions:* write the retention schedule (source, owner, legal flag, hold approach); design tier plans; compute break-even with retrieval and fixed costs; list every copy and its deletion path.
- *Questions:* who owns each class and where does its period come from?
- *Outputs:* retention and tier strategy (6.12).
- *Validation:* every class has a source and owner; tier stages respect minimum durations; deletion coverage includes replicas, snapshots, backups and derived copies.

**Step 16 — Evaluate security, governance, complexity and cost** (D12, D13)
- *Purpose:* count the cost of running it.
- *Inputs:* steps 9–15.
- *Actions:* sketch total cost with ranges including people and compute; record risks with owners and triggers; record accepted trade-offs.
- *Questions:* what does it cost to run and operate?
- *Outputs:* risk and trade-off register (6.13).
- *Validation:* numbers carry units and ranges and are labelled illustrative; people cost is present.

**Step 17 — Document alternatives, trade-offs and the recommendation** (D7, D14)
- *Purpose:* make the decision reviewable.
- *Inputs:* steps 9–16.
- *Actions:* write one ADR per decision (context, decision, rejected alternatives, assumptions, validation, revisit triggers).
- *Questions:* why not the runner-up?
- *Outputs:* recommendation and ADRs (6.14).
- *Validation:* rejection reasons cite criteria and evidence; "too complex" is not a reason.

**Step 18 — Validate against access patterns and failure scenarios** (D14)
- *Purpose:* check that the design behaves as claimed.
- *Inputs:* step 17.
- *Actions:* walk the top scans through the layout with arithmetic; walk node loss, zone loss, lag, corruption, deletion request, site loss, hold and small-file scenarios.
- *Questions:* does it behave as claimed, and what residual risk remains?
- *Outputs:* validation results (6.9, 6.14).
- *Validation:* each outcome is explained; no `Pass` where the cited quantification fails.

**Step 19 — Produce the final selection and summary** (D14)
- *Purpose:* give the sponsor something to decide on.
- *Inputs:* all.
- *Actions:* assemble; summarise decisions, cost range, conditional items and next steps in one to two pages.
- *Questions:* what is decided and what remains conditional?
- *Outputs:* final architecture summary (6.14).
- *Validation:* a non-specialist can follow it in ten minutes; conditional decisions say what evidence would settle them.

---

## 6. Worked reference — Northbridge Bank

Everything in this section is an illustrative assumption or a derived figure. Tables whose first header cell is `ID` are read by the checker; a `~` is a derived cell the checker fills and verifies. The sequence follows the deliverables D1–D14.

### 6.1 D1 — Project scope and assumptions (Steps 1 and 4)

**Problem statement.** Northbridge Bank's storage has grown ad hoc. Analytics slow the operational systems at month-end, history is expensive to query, retention is applied inconsistently, and nobody can state which store is authoritative for what.

**Objective.** Produce a defensible, workload-driven storage recommendation with a logical layout, a consistency strategy and a lifecycle plan. The project stops at the logical design: no product selection, instance sizing, physical schema, infrastructure automation or benchmarks.

| Boundary | In scope | Out of scope (owner) |
| --- | --- | --- |
| Decisions | Storage category per workload, separation, analytical approach, formats, layout, consistency, lifecycle | Product choice and instance sizing (2D.8); platform build (2D.7) |
| Data | Five asset groups in the scenario plus the legacy lake copies | Source-system redesign |
| Movement | Which store is authoritative and what guarantee each hand-off needs | Pipeline and interface design (2D.6); stream processing design (2D.9) |
| Controls | Retention, tiering, deletion coverage, legal-hold approach | Policy engines, classification tooling (2D.10) |
| Resilience | Replication, failure domains, recovery objectives, failure walks | DR runbooks and drills (2D.12) |

**Labelled assumptions.** Every number in this section is an illustrative assumption or a derived figure. The evidence labels are `Given` (stated by the roadmap scenario), `Assumed` (chosen here, registered as ASM-xx), `Derived` (computed from other cells by the checker) and `Unknown` (not known; an open question exists).

### 6.2 D2 — Stakeholders and data asset inventory (Steps 2 and 3)

| ID | Stakeholder role | Interest | Decision rights | Workloads | Evidence |
| --- | --- | --- | --- | --- | --- |
| STK-01 | Chief Data Officer | Sponsor; accepts residual risk and cost | Approves the recommendation and risk acceptance | none | Assumed |
| STK-02 | Head of Payments Operations | Owns posting and the ledger | Owns WL-01 targets and the ledger retention class | WL-01 | Assumed |
| STK-03 | Head of Digital Channels | Owns customer-profile service | Owns WL-02 targets and profile retention | WL-02 | Assumed |
| STK-04 | Head of Finance Reporting | Consumes regulatory and finance reports | Owns WL-03 targets | WL-03 | Assumed |
| STK-05 | Head of Fraud Operations | Consumes fraud analytics | Owns WL-04 targets | WL-04 | Assumed |
| STK-06 | Head of Risk Analytics | Consumes risk analytics | Owns WL-05 targets | WL-05 | Assumed |
| STK-07 | Head of Customer Service and Compliance Records | Owns documents and recordings | Owns WL-06 targets and media retention classes | WL-06 | Assumed |
| STK-08 | Head of Platform Engineering | Owns telemetry and runs the analytical platform | Owns WL-07 targets and telemetry retention | WL-07 | Assumed |
| STK-09 | Security and Privacy Officer | Access control, encryption, erasure | Approves deletion design and access model | none | Assumed |
| STK-10 | Legal and Records Manager | Authoritative source for retention periods | Confirms every retention source | none | Assumed |
| STK-11 | Storage Platform Operations Lead | Runs the stores day to day | Approves operability of each design element | none | Assumed |
| STK-12 | Enterprise Data Architect | Author of this package | Recommends; owns the ADRs | none | Assumed |
| STK-13 | Independent Architecture Reviewer | Challenges evidence and conclusions | Agrees or rejects the evidence | none | Assumed |
| STK-14 | Head of Cards Platform | Owns card-event data | Owns card-event retention and growth figures | WL-04 | Assumed |

| ID | Asset | Category | Purpose | Size TB | Growth basis | Rate low | Rate exp | Rate high | Owner | Retention class | Consumers | Personal data | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AST-01 | Ledger entries | Structured | Authoritative record of postings (rate: TB per year) | 8 | linear | 2 | 3 | 4.5 | STK-02 | RC-01 | WL-01, WL-03, WL-05 | Pseudonymous | Given |
| AST-02 | Card events | Semi-structured | Authorisations and events for fraud and risk (rate: TB per year) | 40 | linear | 20 | 25 | 35 | STK-14 | RC-03 | WL-04, WL-05 | Pseudonymous | Given |
| AST-03 | Customer profiles | Structured | Profile and contact data (rate: fraction per year) | 0.6 | compound | 0.08 | 0.10 | 0.12 | STK-03 | RC-05 | WL-02, WL-04 | Direct | Given |
| AST-04 | Documents and recordings | Unstructured | Customer documents and call recordings (rate: TB per year) | 120 | linear | 25 | 30 | 35 | STK-07 | RC-02, RC-06 | WL-06 | Direct | Given |
| AST-05 | Telemetry | Time-series | Platform metrics (rate: none; steady with 30-day retention) | 5 | steady | 0 | 0 | 0 | STK-08 | RC-04 | WL-07 | None | Given |
| AST-06 | Legacy lake copies | Semi-structured | Poorly organised copies in the three-year-old data lake; contents unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | RC-07 | none | Pseudonymous | Unknown |

The low and high growth rates are planning ranges (ASM-02), not scenario facts. AST-06 has no size and no owner; OQ-01 tracks both, and nothing is sized from it.

### 6.3 D3 — Workload characterisation (Steps 4 and 5)

Dated 2026-10-16, before the comparison matrix (D6, 2026-10-21). Classification is by access pattern, not by system name. `~` marks a derived cell.

| ID | Workload | Class | Owner | Asset | Daily ops | Daily GB | Peak factor | Avg ops/s | Peak ops/s | Avg MB/s | Target | Consistency | Availability | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WL-01 | Payment posting and ledger (W1) | OLTP | STK-02 | AST-01 | 2000000 | 8.22 | 8 | 23.15 | 185.19 | 0.095 | p99 under 100 ms | Strong | 99.95% monthly; no loss of acknowledged postings | Given |
| WL-02 | Customer profile lookups (W2) | OLTP | STK-03 | AST-03 | 30000000 | n/a | 6 | 347.22 | 2,083.33 | n/a | p99 under 50 ms by customer id; peak factor is ASM-01 | Strong for decisions, bounded staleness for display | 99.95% assumed with the ledger | Assumed |
| WL-03 | Regulatory and finance reporting (W3) | OLAP | STK-04 | AST-01 | n/a | n/a | n/a | n/a | n/a | n/a | Monthly and quarterly; complete by T+2 business days; internal run objective 4 h | Snapshot, reconciled to the ledger | 99.5% on business days | Given |
| WL-04 | Fraud analytics (W4) | Mixed | STK-05 | AST-02 | n/a | 68.49 | n/a | n/a | n/a | 0.793 | Recent events p95 within 60 s; 24 months of history | Bounded staleness | 99.5% on business days | Given |
| WL-05 | Risk analytics (W5) | OLAP | STK-06 | AST-01 | n/a | n/a | n/a | n/a | n/a | n/a | Daily batch over multi-year history; window 2 h | Snapshot | 99.5% on business days | Given |
| WL-06 | Documents and recordings (W6) | Specialised | STK-07 | AST-04 | n/a | 82.19 | n/a | n/a | n/a | 0.951 | Infrequent retrieval; long retention | Strong for holds | 99.5% assumed | Assumed |
| WL-07 | Operational telemetry (W7) | Specialised | STK-08 | AST-05 | n/a | 166.67 | 3 | n/a | n/a | 1.929 | High-rate time-ordered writes; 30-day retention; peak factor is ASM-01 | Eventual | 99.5% assumed | Assumed |

Reading the table: WL-01 averages 23.15 postings per second and peaks near 185 per second; the ledger's 3 TB per year of growth implies about 4.1 KB stored per posting, which is plausible for two entries plus indexes and audit data. WL-02 reads average 347 per second and peak near 2,083 per second under ASM-01. The fraud, document and telemetry rows give byte rates because their record counts are not in the scenario.

| ID | Access pattern | Workload | Type | Shape | Frequency | Access key | Target | Layout element | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AP-01 | Post a payment | WL-01 | Write | Two entries, balance update and outbox row in one transaction | 23 per second average, 185 at peak | posting_id, idempotency_key | p99 under 100 ms (BUD-01) | LAY-01 | Given |
| AP-02 | Balance and 30-day statement for an account | WL-01 | Range | By account, newest first, last 30 days | Continuous | account_id, posting_ts | p99 under 100 ms | LAY-01 | Assumed |
| AP-03 | Profile lookup by customer id | WL-02 | Point | One row by customer id | 347 per second average, 2,083 at peak | customer_id | p99 under 50 ms | LAY-02 | Given |
| AP-04 | Recent card events for one card | WL-04 | Point | Events for one card in the last hour | Per authorisation | card_id, event_ts | Fresh within 60 s at p95 (BUD-02) | LAY-03 | Given |
| AP-05 | Card history for one card over 24 months | WL-04 | Scan | Date range plus card filter | Analyst investigations | event_date, card_id | At most 300 s | LAY-05 | Assumed |
| AP-06 | Quarterly regulatory report | WL-03 | Scan | Three posting months, group by product and segment | Quarterly | posting_month | At most 14,400 s | LAY-06 | Given |
| AP-07 | Annual full-history reconciliation | WL-03 | Scan | All 84 posting months | Yearly | posting_month | At most 14,400 s | LAY-06 | Assumed |
| AP-08 | Daily risk batch over five years | WL-05 | Scan | Last 60 posting months | Daily | posting_month | At most 7,200 s | LAY-06 | Given |
| AP-09 | Daily card-event increment for risk features | WL-05 | Scan | One day of card events | Daily | event_date | At most 900 s | LAY-05 | Assumed |
| AP-10 | Retrieve one recording | WL-06 | Point | One object by call id | Infrequent | call_id | First byte within 60 s on the hot tier | LAY-08 | Assumed |
| AP-11 | Retrieve one document | WL-06 | Point | One object by document id | Infrequent | doc_id | First byte within 60 s on the hot tier | LAY-09 | Assumed |
| AP-12 | Look up media metadata | WL-06 | Point | One index row by call id or document id | Once per retrieval | call_id, doc_id | At most 10 s | LAY-10 | Assumed |
| AP-13 | Last-hour telemetry for one metric | WL-07 | Range | Metric id plus one-hour range | Continuous dashboards | metric_id, ts | At most 30 s | LAY-11 | Assumed |
| AP-14 | Land and replay card events | WL-04 | Write | Append original files; replay by ingest date | Continuous | source, ingest_date | Replay one day within 900 s | LAY-04 | Assumed |
| AP-15 | Refresh reporting marts | WL-03 | Range | Rebuild one reporting period | Monthly | reporting_period | Within the 4 h run objective | LAY-07 | Assumed |
| AP-16 | Occasional legacy lake read | WL-03 | Range | Ad hoc reads by finance of old copies | Rare | none | No target; read-only | LAY-12 | Unknown |

### 6.4 D4 — Storage requirements and constraints register (Step 7)

The 2D.2 tests decide the type: a **requirement** is a measurable outcome someone owns; a **constraint** is fixed by an authority and eliminates options; an **assumption** might be wrong and must name how it will be validated; a **dependency** is something another module or team must deliver.

| ID | Statement | Type | Measure | Class test | Owner | Workloads | Validated by | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-01 | Ledger availability is at least 99.95% per month | Requirement | 21.6 minutes of unavailability per 30-day month | Measurable and owned | STK-02 | WL-01 | AV-01 | Given |
| REQ-02 | No acknowledged posting is lost when a node or zone fails | Requirement | RPO 0 s for committed postings under node or zone loss | Measurable and owned | STK-02 | WL-01 | FS-01 | Given |
| REQ-03 | Posting latency p99 is under 100 ms | Requirement | Sum of the latency budget at most 90 ms (10% headroom) | Measurable and owned | STK-02 | WL-01 | BUD-01 | Given |
| REQ-04 | Profile point lookups answer in under 50 ms at p99 | Requirement | Peak 2,083 reads per second served within target | Measurable and owned | STK-03 | WL-02 | FS-02 | Given |
| REQ-05 | Fraud-relevant events are queryable within 60 s at p95 | Requirement | Freshness budget total at most 54 s (10% headroom) | Measurable and owned | STK-05 | WL-04 | BUD-02 | Given |
| REQ-06 | Fraud analysts can query 24 months of history for one card | Requirement | Query completes within 300 s | Measurable and owned | STK-05 | WL-04 | QWK-05 | Assumed |
| REQ-07 | Regulatory and finance reports finish by T+2 business days and reconcile to the ledger | Requirement | Report run within 4 h; control totals equal | Measurable and owned | STK-04 | WL-03 | QWK-01 | Given |
| REQ-08 | Ledger and transaction records are kept at least seven years | Requirement | Minimum 2,555 days from posting (legal confirmation required) | Source needs confirmation | STK-10 | WL-01, WL-03 | OQ-03 | Given |
| REQ-09 | Call recordings are kept five years | Requirement | Minimum 1,825 days (legal confirmation required) | Source needs confirmation | STK-07 | WL-06 | OQ-03 | Given |
| REQ-10 | Card event detail is kept three years, then summarised | Requirement | Detail 1,095 days; summary rule open | Source needs confirmation | STK-14 | WL-04, WL-05 | OQ-03 | Given |
| REQ-11 | Telemetry is kept 30 days | Requirement | Disposal at day 30 | Measurable and owned | STK-08 | WL-07 | PRT-07 | Given |
| REQ-12 | Analytics must not degrade ledger posting at month-end | Requirement | Ledger p99 unchanged while month-end reports run | Measurable and owned | STK-02 | WL-01, WL-03, WL-05 | FS-09 | Given |
| REQ-13 | Erasure requests are completed within 30 days, subject to retention obligations | Requirement | Every copy purged or beyond use within 30 days | Source needs confirmation | STK-09 | WL-02, WL-06 | FS-05 | Assumed |
| REQ-14 | Analytical platform availability is 99.5% on business days | Requirement | 216 minutes per 30-day month (calendar proxy) | Measurable and owned | STK-08 | WL-03, WL-04, WL-05 | AV-02 | Given |
| REQ-15 | Risk batch completes within its daily window | Requirement | Five-year scan within 7,200 s | Measurable and owned | STK-06 | WL-05 | QWK-03 | Given |
| REQ-16 | Access to sensitive attributes is fine-grained and audited | Requirement | Access role per attribute group; access log retained | Measurable and owned | STK-09 | WL-02, WL-06 | LAY-02, LAY-08 | Given |
| CON-01 | Personal data stays in the stated jurisdiction | Constraint | No store or backup outside the jurisdiction | Fixed by regulation | STK-09 | WL-02, WL-06 | GT-07 | Given |
| CON-02 | Data is encrypted at rest and in transit | Constraint | All stores and links | Fixed by policy | STK-09 | WL-01, WL-02, WL-06 | GT-07 | Given |
| CON-03 | Existing identity services provide authentication | Constraint | No new identity store | Fixed by architecture standard | STK-11 | WL-02 | GT-07 | Given |
| CON-04 | The project stops at the logical design | Constraint | No product, instance or DDL decisions | Fixed by scope | STK-01 | none | VAL-01 | Given |
| ASM-01 | Peak factor is 6 for profile reads and 3 for telemetry | Assumption | Planning values; measure the real peaks | Could be wrong | STK-12 | WL-02, WL-07 | OQ-02 | Assumed |
| ASM-02 | Growth ranges are low 20 percent below and high 20 to 50 percent above the expected rate | Assumption | See AST-01 to AST-04 rates | Could be wrong | STK-12 | none | SEN-01 | Assumed |
| ASM-03 | Compression is 5:1 for ledger history and 4:1 for card events | Assumption | Measure on a sample before sizing | Could be wrong | STK-08 | WL-01, WL-04 | FIL-01 | Assumed |
| ASM-04 | The bank has 3,000,000 customers and 400,000 merchants | Assumption | Used only to reject fine partition keys | Could be wrong | STK-12 | WL-04 | PRT-03 | Assumed |
| ASM-05 | The busiest day carries 2.5 times the average card-event volume | Assumption | Skew input for date partitions | Could be wrong | STK-05 | WL-04 | PRT-01 | Assumed |
| ASM-06 | Analytical scans sustain 2,000 MB/s aggregate; the telemetry store sustains 500 MB/s | Assumption | Idealised bound, not a benchmark | Could be wrong | STK-08 | WL-03, WL-04, WL-05 | QWK-01 | Assumed |
| ASM-07 | Sorting card events by card id lets one card's query read about 2% of the files in its date range | Assumption | Validate with file statistics on a sample | Could be wrong | STK-12 | WL-04 | QWK-05 | Assumed |
| ASM-08 | The operational ledger keeps a 24-month hot window | Assumption | Reporting and disputes rarely need older rows operationally | Could be wrong | STK-04 | WL-01, WL-03 | OQ-08 | Assumed |
| ASM-09 | Documents and recordings use one tier plan; their split of the 120 TB is unknown | Assumption | Whole asset treated as one class for cost | Could be wrong | STK-07 | WL-06 | OQ-01 | Assumed |
| ASM-10 | A profile read replica serves 1,500 reads per second | Assumption | Capacity planning input; measure | Could be wrong | STK-11 | WL-02 | FS-02 | Assumed |
| ASM-11 | Archive retrieval is 1,000, 6,000 or 18,000 GB per month (low, base, high) | Assumption | Retrieval planning range | Could be wrong | STK-07 | WL-06 | BRK-01 | Assumed |
| ASM-12 | Unit prices and the 150,000 dollar FTE cost are illustrative | Assumption | Replace with quotes in 2D.8 | Could be wrong | STK-12 | none | CST-01 | Assumed |
| ASM-13 | Snapshots are kept 7 days and backups 35 days | Assumption | Retention of recovery copies | Could be wrong | STK-11 | none | COP-07 | Assumed |
| ASM-14 | A zone-replica acknowledgement adds 8 ms and a remote-site acknowledgement adds 20 ms at p99 | Assumption | Latency inputs for the posting budget | Could be wrong | STK-11 | WL-01 | BUD-05 | Assumed |
| DEP-01 | Change capture and event transport are delivered by modules 2D.6 and 2D.9 | Dependency | Source-to-target flow exists | Owned elsewhere | STK-08 | WL-04 | OQ-06 | Given |
| DEP-02 | Service and region mapping is delivered by module 2D.8 | Dependency | Categories map to services | Owned elsewhere | STK-12 | none | none | Given |
| DEP-03 | Legal confirms every retention source | Dependency | Written confirmation per class | Owned elsewhere | STK-10 | none | OQ-03 | Given |

### 6.5 D5 — Data volume and growth estimates (Step 6)

**Standards used by the calculations.** Every numeric threshold lives in one table so a reviewer can change it and re-run the checker. All are illustrative.

| ID | Standard | Key | Value | Unit | Evidence |
| --- | --- | --- | --- | --- | --- |
| STD-01 | Seconds per day | seconds_per_day | 86400 | s | Given |
| STD-02 | Days per month for availability budgets | month_days | 30 | d | Assumed |
| STD-03 | Target compressed file size | target_file_mb | 256 | MB | Assumed |
| STD-04 | Small-file threshold | small_file_mb | 64 | MB | Assumed |
| STD-05 | Minimum average partition size | min_partition_gb | 1 | GB | Assumed |
| STD-06 | Maximum largest-partition size | max_partition_gb | 100 | GB | Assumed |
| STD-07 | Maximum skew ratio (largest over average) | max_skew | 3 | ratio | Assumed |
| STD-08 | Minimum latency headroom | headroom_min | 0.10 | fraction | Assumed |
| STD-09 | Analytical aggregate scan throughput | scan_mb_s | 2000 | MB/s | Assumed |
| STD-10 | Telemetry store scan throughput | tsdb_scan_mb_s | 500 | MB/s | Assumed |
| STD-11 | Erasure completion target | deletion_sla_days | 30 | d | Assumed |
| STD-12 | Minimum days in the cool tier | min_cool_days | 30 | d | Assumed |
| STD-13 | Minimum days in the archive tier | min_archive_days | 90 | d | Assumed |
| STD-14 | Materiality threshold for a tier move | materiality_usd | 100 | USD per month | Assumed |
| STD-15 | Operational database storage price | price_db | 100 | USD per TB-month | Assumed |
| STD-16 | Serving store price | price_serving | 60 | USD per TB-month | Assumed |
| STD-17 | Time-series store price | price_tsdb | 60 | USD per TB-month | Assumed |
| STD-18 | Object hot tier price | price_hot | 24 | USD per TB-month | Assumed |
| STD-19 | Object cool tier price | price_cool | 10 | USD per TB-month | Assumed |
| STD-20 | Object archive tier price | price_archive | 3 | USD per TB-month | Assumed |
| STD-21 | Fully loaded cost of one FTE | fte_cost_usd | 150000 | USD per year | Assumed |
| STD-22 | Cost range, low multiplier | cost_low_factor | 0.8 | factor | Assumed |
| STD-23 | Cost range, high multiplier | cost_high_factor | 1.5 | factor | Assumed |

**Growth projection.** Decimal units: 1 TB = 1,000 GB. A capped line limits the stored volume to what the retention period allows (rate × retention years). Formulas: linear `size + rate × years`; compound `size × (1 + rate)^years`; steady `size`.

| ID | Growth line | Asset | Horizon yr | Cap yr | Low TB | Exp TB | High TB | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GRW-01 | Ledger entries at the seven-year retention horizon | AST-01 | 7 | none | 22.00 | 29.00 | 39.50 | Derived |
| GRW-02 | Card events detail, capped at three years of ingest | AST-02 | 5 | 3 | 60.00 | 75.00 | 105.00 | Derived |
| GRW-03 | Customer profiles at five years | AST-03 | 5 | none | 0.88 | 0.97 | 1.06 | Derived |
| GRW-04 | Documents and recordings at five years, no disposal netted | AST-04 | 5 | none | 245.00 | 270.00 | 295.00 | Derived |
| GRW-05 | Telemetry at steady state | AST-05 | 5 | none | 5.00 | 5.00 | 5.00 | Derived |

**Stored capacity at the horizon.** `Logical source` states how each row derives from a growth line: `horizon` uses the horizon volume, `rate` uses the yearly growth, `SUM(...)` adds other rows. Stored = logical × (1 + overhead) × copies. Copies count every full copy that must be paid for (replicas, an independent backup, or both).

| ID | Dataset | Store | Logical source | Logical exp TB | Overhead | Copies | Stored low TB | Stored exp TB | Stored high TB | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAP-01 | AST-01 ledger hot window of 24 months, with indexes | STO-01 | GRW-01:rate*2 | 6.00 | 0.20 | 3 | 14.40 | 21.60 | 32.40 | Derived |
| CAP-02 | AST-01 ledger history in columnar files at 5:1 | STO-04 | GRW-01:horizon*0.2 | 5.80 | 0.05 | 2 | 9.24 | 12.18 | 16.59 | Derived |
| CAP-03 | AST-02 card events curated detail at 4:1 | STO-04 | GRW-02:horizon*0.25 | 18.75 | 0.05 | 2 | 31.50 | 39.38 | 55.12 | Derived |
| CAP-04 | AST-02 card events raw landing, 90 days | STO-04 | GRW-02:rate*90/365 | 6.16 | 0 | 1 | 4.93 | 6.16 | 8.63 | Derived |
| CAP-05 | AST-02 recent-events window, 7 days | STO-03 | GRW-02:rate*7/365 | 0.48 | 0.20 | 3 | 1.38 | 1.73 | 2.42 | Derived |
| CAP-06 | AST-03 customer profiles with indexes and read replicas | STO-02 | GRW-03:horizon*1 | 0.97 | 0.20 | 4 | 4.23 | 4.64 | 5.08 | Derived |
| CAP-07 | AST-04 documents and recordings | STO-05 | GRW-04:horizon*1 | 270.00 | 0 | 2 | 490.00 | 540.00 | 590.00 | Derived |
| CAP-08 | AST-05 telemetry | STO-06 | GRW-05:horizon*1 | 5.00 | 0.10 | 2 | 11.00 | 11.00 | 11.00 | Derived |
| CAP-09 | Consumption zone (marts and features), 10% of history and detail | STO-04 | SUM(CAP-02, CAP-03)*0.10 | 2.46 | 0.05 | 2 | 4.07 | 5.16 | 7.17 | Derived |

AST-06 is absent from the table because its size is unknown (OQ-01); adding an invented number would hide the gap.

**Sensitivity.** The checker totals the three cases and names the row that contributes most of the low-to-high spread.

| ID | Sensitivity line | Total low TB | Total exp TB | Total high TB | Dominant row | Share of spread | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SEN-01 | Total stored capacity at the horizon, all stores | 570.76 | 641.84 | 728.41 | CAP-07 | 63.4% | Derived |

**File arithmetic.** Raw GB per day comes from the workload row's byte rate. A commit that writes one file per interval produces files of (compressed GB per day) ÷ (commits per day).

| ID | File arithmetic | Workload | Raw GB/day | Ratio | Target file MB | Commits/day | Compressed GB/day | Files/day at target | MB per commit file | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FIL-01 | Card events curated, naive one-minute commits | WL-04 | 68.49 | 4 | 256 | 1440 | 17.12 | 66.9 | 11.9 | Small files | Derived |
| FIL-02 | Card events curated, commits sized to the target | WL-04 | 68.49 | 4 | 256 | 67 | 17.12 | 66.9 | 255.6 | OK | Derived |
| FIL-03 | Ledger history, hourly appends | WL-01 | 8.22 | 5 | 256 | 24 | 1.64 | 6.4 | 68.5 | OK | Derived |
| FIL-04 | Telemetry written as lake files, one-minute commits | WL-07 | 166.67 | 4 | 256 | 1440 | 41.67 | 162.8 | 28.9 | Small files | Derived |

**Partition worksheet.** Standards STD-05 to STD-07 decide acceptance. A key can pass the size standards and still be wrong for the queries; the reason column records both.

| ID | Partition worksheet | Layout | Dataset source | Compressed TB | Partitions | Avg GB | Skew ratio | Largest GB | Files at largest | Failed standards | Verdict | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRT-01 | Card events by event date (daily) | LAY-05 | GRW-02:horizon*0.25 | 18.75 | 1095 | 17.12 | 2.5 | 42.81 | 168 | none | Accept | Matches AP-05 and AP-09 date filters; skew from ASM-05 |
| PRT-02 | Card events by event month | LAY-05 | GRW-02:horizon*0.25 | 18.75 | 36 | 520.83 | 1.3 | 677.08 | 2,645 | max_partition_gb | Reject | Partitions too large; one-day increments (AP-09) would scan a whole month |
| PRT-03 | Card events by customer id | LAY-05 | GRW-02:horizon*0.25 | 18.75 | 3000000 | 0.006 | 12 | 0.075 | 1 | min_partition_gb, max_skew | Reject | Millions of tiny partitions (ASM-04); heavy customers skew the sizes |
| PRT-04 | Card events by merchant id | LAY-05 | GRW-02:horizon*0.25 | 18.75 | 400000 | 0.047 | 40 | 1.875 | 8 | min_partition_gb, max_skew | Reject | Tiny partitions and a few very large merchants (ASM-04) |
| PRT-05 | Ledger history by posting month | LAY-06 | GRW-01:horizon*0.2 | 5.80 | 84 | 69.05 | 1.3 | 89.76 | 351 | none | Accept | Matches month-based reporting; revisit when the largest partition passes 80 GB |
| PRT-06 | Ledger history by posting day | LAY-06 | GRW-01:horizon*0.2 | 5.80 | 2555 | 2.270 | 2 | 4.540 | 18 | none | Accept | Passes the size standards; not selected: 2,555 partitions to manage and no query needs day grain |
| PRT-07 | Telemetry by hour chunk | LAY-11 | GRW-05:horizon*1 | 5.00 | 720 | 6.944 | 2 | 13.89 | 55 | none | Accept | Matches AP-13; chunk drop implements 30-day disposal |
| PRT-08 | Telemetry by minute chunk | LAY-11 | GRW-05:horizon*1 | 5.00 | 43200 | 0.116 | 2 | 0.231 | 1 | min_partition_gb | Reject | Tiny chunks create metadata overhead without helping AP-13 |
| PRT-09 | Recent events by hashed card id (256 buckets) | LAY-03 | GRW-02:rate*7/365 | 0.48 | 256 | 1.873 | 2 | 3.746 | 15 | none | Accept | Even spread by hashing; corporate cards add skew |

### 6.6 D6 — Technology category comparison matrix (Steps 8 and 9)

**Order of work.** Gates and criteria are fixed first (dated), candidates are screened by the gates, and only gate-passing candidates are scored. Scores are integers from 1 (poor) to 5 (strong) and are judgments recorded with their evidence, not measurements. For cost and operational simplicity, a higher score means cheaper or simpler.

**Gates.** A candidate that fails a gate is not scored for selection; it stays in the table with its failure reason.

| ID | Gate | Test | Decisions | Evidence |
| --- | --- | --- | --- | --- |
| GT-01 | Isolation | Large scans never share compute or I/O with posting writes | DEC-01 | Given |
| GT-02 | Freshness headroom | Meets the 60 s p95 freshness for WL-04 with at least 10% headroom (STD-08) | DEC-01, DEC-05 | Derived |
| GT-03 | Atomic multi-row integrity | Multi-row atomic writes and uniqueness are enforced by the store itself | DEC-02 | Given |
| GT-04 | Latency headroom | The posting p99 budget keeps at least 10% headroom (STD-08) | DEC-02 | Derived |
| GT-05 | Point-lookup latency | Meets p99 under 50 ms at peak with at least 10% headroom | DEC-03 | Assumed |
| GT-06 | Row-level correction and deletion | Individual records can be deleted or corrected without rewriting the whole dataset, alone or through a table-format layer | DEC-04, DEC-08 | Given |
| GT-07 | Jurisdiction and encryption | Satisfies CON-01, CON-02 and CON-03 | DEC-01, DEC-02, DEC-03, DEC-04, DEC-05, DEC-06, DEC-07, DEC-08 | Given |
| GT-08 | Retention lock and holds | Enforceable per-object retention lock and legal hold | DEC-07 | Given |
| GT-09 | Time-ordered ingest and drop by time | Sustains the telemetry rate and expires data by dropping time chunks | DEC-06 | Given |

**Criteria.** Weights were fixed on 2026-10-17, before any candidate was scored (D6 is dated 2026-10-21).

| ID | Criterion | Weight | Question it answers | Locked on | Evidence |
| --- | --- | --- | --- | --- | --- |
| CRT-01 | C1 Workload fit | 0.25 | Does the category match the access pattern and data shape? | 2026-10-17 | Assumed |
| CRT-02 | C2 Consistency and transactions | 0.15 | Does it provide the guarantees the workload needs? | 2026-10-17 | Assumed |
| CRT-03 | C3 Scalability headroom | 0.10 | Does it absorb the high growth case without redesign? | 2026-10-17 | Assumed |
| CRT-04 | C4 Operational simplicity | 0.15 | How little extra on-call and maintenance does it add? | 2026-10-17 | Assumed |
| CRT-05 | C5 Governance and erasure | 0.15 | Can access, retention, holds and deletion be enforced? | 2026-10-17 | Assumed |
| CRT-06 | C6 Cost | 0.10 | How low is storage plus operating cost? | 2026-10-17 | Assumed |
| CRT-07 | C7 Openness and exit | 0.10 | How easily can data and engines be replaced? | 2026-10-17 | Assumed |

**Weight sets for the sensitivity test.** `WS-00` equals the locked weights; the others are stress tests, not alternatives anyone has proposed.

| ID | Weight set | C1 | C2 | C3 | C4 | C5 | C6 | C7 | Purpose |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WS-00 | Locked weights | 0.25 | 0.15 | 0.10 | 0.15 | 0.15 | 0.10 | 0.10 | The scoring used for selection |
| WS-01 | Equal weights | 0.142857 | 0.142857 | 0.142857 | 0.142857 | 0.142857 | 0.142857 | 0.142858 | Tests dependence on the chosen weights |
| WS-02 | Simplicity-heavy | 0.20 | 0.10 | 0.10 | 0.30 | 0.10 | 0.10 | 0.10 | A small operations team |
| WS-03 | Cost-heavy | 0.20 | 0.10 | 0.10 | 0.10 | 0.10 | 0.30 | 0.10 | A tight budget |
| WS-04 | Governance-heavy | 0.20 | 0.15 | 0.05 | 0.10 | 0.30 | 0.10 | 0.10 | A stricter regulator |

**Candidate matrix.** Gate cell: `GT-nn:P` passes, `GT-nn:F` fails. Total, Eligible and Rank are derived. Each decision has at least three eligible candidates and exactly one baseline (the minimal-change option).

| ID | Candidate | Decision | Baseline | Gates | Gate failure reason | C1 | C2 | C3 | C4 | C5 | C6 | C7 | Total | Eligible | Rank | Limitation or risk | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAN-01 | Keep analytics on the shared operational database | DEC-01 | Yes | GT-01:F; GT-02:P; GT-07:P | Month-end analytics already slow the operational systems (scenario evidence on WL-01 and WL-03), so isolation fails | 2 | 5 | 2 | 5 | 3 | 4 | 3 | 3.35 | No | - | Month-end contention persists and grows with history | Given |
| CAN-02 | Read replica of the operational database serves analytics | DEC-01 | No | GT-01:P; GT-02:P; GT-07:P | none | 3 | 4 | 3 | 4 | 3 | 3 | 2 | 3.20 | Yes | 3 | Long scans conflict with replication apply; history held at database prices | Assumed |
| CAN-03 | Separate analytical store fed by outbox and change events | DEC-01 | No | GT-01:P; GT-02:P; GT-07:P | none | 5 | 4 | 5 | 3 | 4 | 3 | 4 | 4.10 | Yes | 1 | Needs a change pipeline and reconciliation; analytics lag the ledger by minutes | Assumed |
| CAN-04 | Nightly batch extract to a separate analytical store | DEC-01 | No | GT-01:P; GT-02:F; GT-07:P | A nightly extract is up to 86,400 s stale against the 60 s fraud freshness target | 3 | 3 | 4 | 4 | 3 | 4 | 3 | 3.35 | No | - | Stale by up to a day; no intraday fraud use | Derived |
| CAN-05 | Replica for the recent window plus a separate store for history | DEC-01 | No | GT-01:P; GT-02:P; GT-07:P | none | 4 | 4 | 4 | 2 | 3 | 2 | 3 | 3.25 | Yes | 2 | Two analytical paths to run, secure and reconcile | Assumed |
| CAN-06 | Relational, single leader, synchronous zone replica and asynchronous DR replica | DEC-02 | Yes | GT-03:P; GT-04:P; GT-07:P | none | 5 | 5 | 3 | 4 | 4 | 4 | 3 | 4.20 | Yes | 1 | Single-leader write ceiling; site loss leaves a non-zero RPO (REP-02) | Given |
| CAN-07 | Distributed relational with synchronous multi-site commit | DEC-02 | No | GT-03:P; GT-04:F; GT-07:P | BUD-05: a synchronous remote-site acknowledgement raises the p99 budget to 92 ms, leaving 8% headroom against the required 10% | 4 | 5 | 5 | 2 | 4 | 2 | 3 | 3.65 | No | - | Every commit includes a remote round trip | Derived |
| CAN-08 | Document store for ledger entries | DEC-02 | No | GT-03:P; GT-04:P; GT-07:P | none | 3 | 2 | 4 | 3 | 3 | 3 | 3 | 2.95 | Yes | 3 | Cross-document integrity and uniqueness rest on application code | Assumed |
| CAN-09 | Distributed relational with synchronous commit across zones in one site | DEC-02 | No | GT-03:P; GT-04:P; GT-07:P | none | 4 | 5 | 5 | 2 | 4 | 2 | 3 | 3.65 | Yes | 2 | A cluster to operate; higher cost with no workload-driven gain | Assumed |
| CAN-10 | Existing relational profile store with read replicas | DEC-03 | Yes | GT-05:P; GT-07:P | none | 4 | 5 | 3 | 5 | 4 | 4 | 4 | 4.20 | Yes | 1 | Read capacity depends on replica count (ASM-10); limit changes must read the primary | Given |
| CAN-11 | Document store holding the profile as one aggregate | DEC-03 | No | GT-05:P; GT-07:P | none | 5 | 3 | 5 | 3 | 3 | 3 | 3 | 3.70 | Yes | 2 | Weaker cross-record consistency; a migration with no measured need | Assumed |
| CAN-12 | Relational store with an in-memory cache in front | DEC-03 | No | GT-05:P; GT-07:P | none | 5 | 3 | 4 | 3 | 3 | 3 | 4 | 3.70 | Yes | 2 | Cache invalidation and a stale-block failure mode | Assumed |
| CAN-13 | Object-store lake with plain files and no table format | DEC-04 | Yes | GT-06:F; GT-07:P | Plain files have no row-level delete or atomic multi-file commit, so erasure and corrections need whole-partition rewrites by custom jobs | 3 | 2 | 4 | 3 | 2 | 4 | 4 | 3.00 | No | - | No atomic commits or row-level change; small-file sprawl | Given |
| CAN-14 | Dedicated managed warehouse with proprietary storage | DEC-04 | No | GT-06:P; GT-07:P | none | 5 | 4 | 4 | 5 | 4 | 2 | 2 | 4.00 | Yes | 2 | Proprietary storage; higher cost per TB; harder to leave | Assumed |
| CAN-15 | Lakehouse: object storage, open table format and a query engine | DEC-04 | No | GT-06:P; GT-07:P | none | 4 | 4 | 5 | 3 | 4 | 4 | 5 | 4.05 | Yes | 1 | Table maintenance (compaction, snapshot expiry) is ours to run | Assumed |
| CAN-16 | Warehouse for hot data plus an external lake for history | DEC-04 | No | GT-06:P; GT-07:P | none | 4 | 4 | 4 | 2 | 3 | 3 | 3 | 3.35 | Yes | 3 | Two copies of history and two governance models | Assumed |
| CAN-17 | Lakehouse with 30-second micro-batch commits only | DEC-05 | Yes | GT-02:F; GT-07:P | BUD-03: capture, transport, a 30 s batch interval and a 20 s commit total 60 s, leaving 0% headroom | 3 | 4 | 4 | 4 | 4 | 4 | 5 | 3.85 | No | - | Zero freshness headroom (BUD-03); frequent commits create small files | Derived |
| CAN-18 | Operational database replica holds the recent window | DEC-05 | No | GT-02:P; GT-07:P | none | 3 | 4 | 2 | 4 | 3 | 3 | 3 | 3.20 | Yes | 3 | Fraud reads share replicas with other consumers; shallow retention | Assumed |
| CAN-19 | Key-based serving store fed from the event log with a 7-day window | DEC-05 | No | GT-02:P; GT-07:P | none | 5 | 3 | 5 | 3 | 3 | 3 | 3 | 3.70 | Yes | 1 | A second pipeline and store to operate; eventual consistency | Assumed |
| CAN-20 | In-memory store with persistence | DEC-05 | No | GT-02:P; GT-07:P | none | 5 | 2 | 3 | 3 | 3 | 2 | 3 | 3.25 | Yes | 2 | Memory cost per TB; durability and recovery behaviour need proof | Assumed |
| CAN-21 | Telemetry written as files in the lake | DEC-06 | Yes | GT-09:P; GT-07:P | none | 2 | 3 | 4 | 3 | 3 | 4 | 5 | 3.15 | Yes | 4 | Small files at high commit rates (FIL-04) | Derived |
| CAN-22 | Time-series store with time-chunk expiry | DEC-06 | No | GT-09:P; GT-07:P | none | 5 | 3 | 4 | 3 | 3 | 4 | 3 | 3.70 | Yes | 1 | Another engine to operate; weak joins to ledger data | Assumed |
| CAN-23 | General relational database | DEC-06 | No | GT-09:P; GT-07:P | none | 3 | 5 | 2 | 4 | 3 | 2 | 3 | 3.25 | Yes | 2 | Database prices for short-lived append-only data | Assumed |
| CAN-24 | Search and log index store | DEC-06 | No | GT-09:P; GT-07:P | none | 4 | 2 | 4 | 3 | 3 | 3 | 3 | 3.20 | Yes | 3 | Weak consistency; cost grows with indexed volume | Assumed |
| CAN-25 | File shares for documents and recordings | DEC-07 | Yes | GT-08:F; GT-07:P | The file-share category has no enforceable per-object retention lock or per-record legal hold | 3 | 3 | 2 | 4 | 1 | 3 | 3 | 2.75 | No | - | No object-level lock or hold; tiering is manual | Given |
| CAN-26 | Object storage with retention lock and lifecycle tiers | DEC-07 | No | GT-08:P; GT-07:P | none | 5 | 4 | 5 | 4 | 5 | 5 | 4 | 4.60 | Yes | 1 | Archive retrieval takes hours; search needs a separate index | Assumed |
| CAN-27 | Binary objects inside a relational database | DEC-07 | No | GT-08:P; GT-07:P | none | 2 | 5 | 2 | 3 | 3 | 1 | 3 | 2.75 | Yes | 3 | Database storage cost and backup size multiply | Assumed |
| CAN-28 | Managed content-management platform | DEC-07 | No | GT-08:P; GT-07:P | none | 4 | 4 | 3 | 3 | 5 | 2 | 2 | 3.50 | Yes | 2 | Higher cost; archive format tied to one product | Assumed |
| CAN-29 | Delimited and JSON text files | DEC-08 | Yes | GT-06:F; GT-07:P | Text files carry no enforced schema and no row-level delete, so corrections need whole-file rewrites | 2 | 2 | 3 | 3 | 2 | 2 | 5 | 2.55 | No | - | No schema enforcement; slow scans; whole-file rewrites | Given |
| CAN-30 | Row-oriented landing files plus columnar curated files in an open table format | DEC-08 | No | GT-06:P; GT-07:P | none | 5 | 4 | 5 | 3 | 4 | 4 | 5 | 4.30 | Yes | 1 | Two formats to maintain and a conversion step between zones | Assumed |
| CAN-31 | Columnar files and an open table format in every zone | DEC-08 | No | GT-06:P; GT-07:P | none | 4 | 4 | 5 | 4 | 4 | 4 | 5 | 4.20 | Yes | 2 | Malformed source records cannot be replayed exactly | Assumed |
| CAN-32 | A second columnar family with narrower engine support | DEC-08 | No | GT-06:P; GT-07:P | none | 4 | 4 | 5 | 3 | 4 | 4 | 3 | 3.85 | Yes | 3 | Fewer engines can read it | Assumed |

### 6.7 D7 — Storage technology selection rationale (Steps 10 and 11)

**Decisions.** The checker recomputes the winner under every weight set and marks a decision weight-sensitive when the winner changes; such a decision carries a conditional note and a revisit trigger.

| ID | Decision | Workloads | Requirements | Selected | Runner-up | Weight-sensitive | Conditional on | ADR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEC-01 | Separate analytical storage from the operational ledger | WL-01, WL-03, WL-04, WL-05 | REQ-12, REQ-14, REQ-15, CON-04 | CAN-03 | CAN-05 | No | none | ADR-01 |
| DEC-02 | Store for payment posting and the ledger | WL-01 | REQ-01, REQ-02, REQ-03, REQ-08, CON-01 | CAN-06 | CAN-09 | No | OQ-04: whether non-zero RPO on site loss is acceptable | ADR-02 |
| DEC-03 | Store for customer profile lookups | WL-02 | REQ-04, REQ-16, CON-03 | CAN-10 | CAN-11 | No | none | ADR-03 |
| DEC-04 | Analytical storage approach for history | WL-03, WL-04, WL-05 | REQ-06, REQ-07, REQ-10, REQ-13 | CAN-15 | CAN-14 | Yes (WS-02) | OQ-07: operations capacity to run table maintenance | ADR-04 |
| DEC-05 | Serving path for recent fraud events | WL-04 | REQ-05 | CAN-19 | CAN-20 | No | OQ-06: measured freshness of lakehouse micro-batch commits | ADR-05 |
| DEC-06 | Store for operational telemetry | WL-07 | REQ-11 | CAN-22 | CAN-23 | No | none | ADR-06 |
| DEC-07 | Store for documents and recordings | WL-06 | REQ-09, CON-02 | CAN-26 | CAN-28 | No | none | ADR-07 |
| DEC-08 | File and table formats in the analytical layer | WL-03, WL-04, WL-05 | REQ-07, REQ-10, REQ-13 | CAN-30 | CAN-31 | Yes (WS-02) | OQ-07: operations capacity to run table maintenance | ADR-08 |

**Summary of the choices.**

| Workload | Selected category | System of record | Why not the runner-up |
| --- | --- | --- | --- |
| WL-01 | Relational, single leader, synchronous zone replica, asynchronous DR replica (CAN-06) | STO-01 for 24 months, then STO-04 | A distributed in-zone relational option (CAN-09) scores 3.65 against 4.20: it adds a cluster to operate and costs more, with no latency or consistency gain the workload needs |
| WL-02 | Existing relational profile store with three read replicas (CAN-10) | STO-02 | A document store (CAN-11) improves fit but weakens consistency for limit and block changes and adds a migration |
| WL-03, WL-05 | Lakehouse history (CAN-15) | STO-04 | The managed warehouse (CAN-14) is simpler to run but scores lower on cost and exit; it wins only when simplicity carries 30% of the weight |
| WL-04 | Serving store for the recent window plus lakehouse history (CAN-19 with CAN-15) | STO-04 for history; STO-03 holds a derived 7-day copy | Persistent in-memory storage (CAN-20) has weaker consistency and costs more per TB |
| WL-06 | Object storage with retention lock and lifecycle tiers (CAN-26) | STO-05 | The managed content platform (CAN-28) governs well but costs more and ties the archive to one product |
| WL-07 | Time-series store (CAN-22) | STO-06 | A general relational database (CAN-23) would carry 5 TB of short-lived, append-only metrics at database prices |

**Layer distinction for the analytical path.** Storage holds bytes (an object store). A table format adds snapshots, schema tracking and atomic commits over files. A platform or engine plans queries and manages compute. This package selects the first two layers by category (CAN-15, CAN-30); the third is a 2D.7 decision. A set of files on its own is not a table, and a table format is not a database.

### 6.8 D8 — Logical storage architecture (Step 12)

Stores and ownership. Layers are named so storage, table format and platform are not confused.

| ID | Store | Category | Role | Authoritative for | Decision | Layers | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| STO-01 | Ledger operational store | Relational, single leader | Posts payments; holds the 24-month hot window | AST-01 for the last 24 months | DEC-02, DEC-01 | Database engine with its own storage | Derived |
| STO-02 | Customer profile store | Relational with three read replicas | Serves profile lookups; holds the only copy of direct personal data | AST-03 | DEC-03 | Database engine with its own storage | Derived |
| STO-03 | Recent-events serving store | Key-based low-latency store | Serves the last seven days of card events to fraud scoring; derived copy | none (derived from the event log) | DEC-05 | Database engine with its own storage | Derived |
| STO-04 | Lakehouse | Object storage with open table format | Landing, curated and consumption zones; ledger history and card-event history | AST-01 older than 24 months; AST-02 history | DEC-01, DEC-04, DEC-08 | storage: object store; table format: open table format; platform: query engine chosen in 2D.7 | Derived |
| STO-05 | Media object store | Object storage with retention lock | Documents and recordings with lifecycle tiers | AST-04 | DEC-07 | storage: object store with retention lock; table format: not applicable; platform: none (metadata index in STO-04) | Derived |
| STO-06 | Telemetry store | Time-series store | Short-retention metrics | AST-05 | DEC-06 | Database engine with its own storage | Derived |
| STO-07 | Event log | Log transport | Carries outbox and change events; not a system of record | none | Deferred to 2D.6 and 2D.9 | Transport only | Derived |

```text
D8-DIAGRAM v1.1 (2026-10-21) logical storage architecture. Legend: [STO-nn] store; --> flow; ==> hand-off of authority; (zone) logical zone.
Zones are logical. No product or service is implied.

 Payment services                          Customer app / branch / contact centre
        |                                              |
        v                                              v
 [STO-01] Ledger store  ----sync---->  zone replica     [STO-02] Profile store --async--> 3 read replicas
   (24-month hot window)  --async--->  DR replica              |  (only copy of direct personal data)
        | outbox rows                                          |
        v                                                      |
 [STO-07] Event log (transport; design in 2D.6/2D.9) <---------+ change events
        |                         |
        | change events           | card events
        v                         v
 [STO-04] Lakehouse                                  [STO-03] Recent-events store (7-day window)
   (landing)  original files, immutable, 90 days            ^
   (curated)  ledger_history, card_events, media_index      | fraud scoring reads (WL-04)
   (consumption)  regulatory and risk marts
   (quarantine)  legacy lake copies, read-only
        ^
        | ==> ledger partitions hand over at month 24 after control totals match (TXB-04)
        |
 Finance, risk and fraud analysts (WL-03, WL-04 history, WL-05)

 [STO-05] Media object store (retention lock, lifecycle tiers)   <--- call recording and document intake
   metadata index lives in [STO-04] curated zone
 [STO-06] Telemetry store  <--- platform metrics
```

**System-of-record register.** Exactly one store is authoritative for a record at any time; the hand-off needs a stated control.

| ID | Authority record | Data | Store | Valid for | Hand-off control | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SOR-01 | Ledger entries posted in the last 24 months | AST-01 | STO-01 | Months 0 to 24 | At month 24 the lakehouse copy is verified against control totals before the partition is detached (TXB-04) | Assumed |
| SOR-02 | Ledger entries older than 24 months | AST-01 | STO-04 | Months 24 to 84 | Control totals recorded at hand-off; the partition is immutable afterwards | Assumed |
| SOR-03 | Customer profiles and direct personal data | AST-03 | STO-02 | Relationship plus retention | Erasure workflow TXB-05 is the only deletion path | Assumed |
| SOR-04 | Card event history | AST-02 | STO-04 | Ingest to day 1,095 | Landing files are immutable; the cards platform keeps only a short replay window (OQ-01) | Assumed |
| SOR-05 | Documents and recordings | AST-04 | STO-05 | Whole life of the object | Retention lock and hold flag on the object itself | Assumed |
| SOR-06 | Telemetry | AST-05 | STO-06 | 30 days | Time-chunk expiry | Assumed |
| SOR-07 | Legacy lake copies | AST-06 | STO-04 | Until rationalised | No authority claimed; quarantined read-only until a governed copy is proven (OQ-01) | Unknown |

### 6.9 D9 — Data layout and access strategy (Step 13)

Every element names the asset, store, workloads, a stated assumption and at least one access pattern from D3. Physical details (DDL, engine settings, index types) are out of scope; the names below are logical keys.

| ID | Layout element | Asset | Store | Workloads | Organisation | Format | Keys | Partition ref | Cluster or index | Retention class | Assumptions | Governance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LAY-01 | Ledger entries, 24-month hot window | AST-01 | STO-01 | WL-01 | Monthly range partitions by posting date; they are lifecycle units for hand-off, not a speed device | Relational rows | posting_id, account_id, posting_ts, idempotency_key | none | Primary key on posting_id; unique index on idempotency_key; index on account_id and posting_ts descending | RC-01 | ASM-08, ASM-14 | Service roles; no analytical access path; access audited |
| LAY-02 | Customer profile | AST-03 | STO-02 | WL-02 | One table, no partitioning (about 1 TB at five years) | Relational rows | customer_id | none | Primary key on customer_id | RC-05 | ASM-01, ASM-10 | Direct personal data lives only here; other stores hold a customer key |
| LAY-03 | Recent card events window | AST-02 | STO-03 | WL-04 | Partition key is hashed card_id (256 buckets); rows ordered by event_ts descending; 7-day expiry | Key-based rows | card_id, event_ts | PRT-09 | Clustering by event_ts | RC-03 | ASM-05 | Pseudonymous keys only; expiry removes data after 7 days |
| LAY-04 | Card events landing zone | AST-02 | STO-04 | WL-04, WL-05 | landing/cards/ingest_date=YYYY-MM-DD/ ; files are immutable | Original row-oriented files | source, ingest_date | none | none | RC-03 | ASM-03 | Write-once; read by the load job only; expires at 90 days |
| LAY-05 | Card events curated | AST-02 | STO-04 | WL-04, WL-05 | curated/card_events/event_date=YYYY-MM-DD/ ; sorted by card_id inside each date | Columnar files in an open table format | event_date, card_id, customer_key | PRT-01 | Sort order by card_id for file skipping | RC-03 | ASM-03, ASM-05, ASM-07 | Row-level delete through the table format; access by analyst role |
| LAY-06 | Ledger history | AST-01 | STO-04 | WL-03, WL-05 | curated/ledger_history/posting_month=YYYY-MM/ ; sorted by account_id | Columnar files in an open table format | posting_month, account_id, posting_date | PRT-05 | Sort order by account_id | RC-01 | ASM-03, ASM-08 | Immutable after hand-off; corrections as dated adjustments |
| LAY-07 | Regulatory and risk marts | AST-01 | STO-04 | WL-03, WL-05 | consumption/marts/reporting_period=YYYY-MM/ | Columnar files in an open table format | reporting_period | none | none | RC-01 | ASM-03 | Reproducible from LAY-06; pinned table snapshot per report |
| LAY-08 | Call recordings | AST-04 | STO-05 | WL-06 | recordings/YYYY/MM/DD/call_id ; tags carry retention class and hold flag | Original audio objects, immutable | call_id | none | Metadata index in LAY-10 | RC-02 | ASM-09, ASM-11 | Retention lock; hold flag; access by compliance role and logged |
| LAY-09 | Documents | AST-04 | STO-05 | WL-06 | documents/class/YYYY/MM/doc_id ; tags carry retention class and hold flag | Original document objects, immutable | doc_id | none | Metadata index in LAY-10 | RC-06 | ASM-09, ASM-11 | Retention lock; hold flag; classification tag drives access |
| LAY-10 | Media metadata index | AST-04 | STO-04 | WL-06 | curated/media_index/ ; one row per object, refreshed within one hour | Columnar files in an open table format | call_id, doc_id | none | none | RC-02 | ASM-09 | Holds no content; row deleted when the object is disposed |
| LAY-11 | Telemetry chunks | AST-05 | STO-06 | WL-07 | One-hour time chunks keyed by metric_id; expired by dropping chunks | Time-series rows | metric_id, ts | PRT-07 | Time ordering inside a chunk | RC-04 | ASM-01 | Platform roles; no personal data |
| LAY-12 | Legacy lake quarantine | AST-06 | STO-04 | WL-03 | quarantine/legacy/ ; read-only, no new writes | As found | none | none | none | RC-07 | ASM-09 | Access by named reviewers only until contents are classified |

**Choices and rejected alternatives.**

- **Card events by date, not by customer, merchant or month** (PRT-01 against PRT-02 to PRT-04). A customer key creates 3 million tiny partitions; a merchant key adds extreme skew; a month key is 520 GB per partition and makes the daily increment (AP-09) scan a whole month.
- **Ledger history by month, not by day** (PRT-05 against PRT-06). Reports are monthly; day partitions add 2,555 objects to manage without helping any pattern. Trigger: revisit when the largest partition exceeds 80 GB.
- **Sorting within files supplies the card filter** (ASM-07). Partition pruning removes dates; sort order and file statistics remove files within the date range. QWK-05 and QWK-06 quantify the difference.
- **Indexes only where a point or range pattern needs them.** LAY-01 has three, each tied to AP-01 or AP-02. LAY-02 has only its key. Every extra index slows postings and enlarges every replica.

**Validation plan for the layout.** Before any build, run each experiment on a representative sample and record the result against the pass criterion.

| Experiment | Question | Pass criterion |
| --- | --- | --- |
| Pruning check | Does a 24-month card query touch only the expected dates? | Partitions read equal 730 of 1,095 |
| File-skipping check | How much of a date range does one card's query read? | Bytes read at most 5% of the range (assumed 2%) |
| Small-file check | Is the median curated file at least 64 MB after compaction? | Median at or above STD-04 |
| Skew check | What is the largest partition against the average? | At most 3.0 (STD-07) |
| Index cost check | Do the three ledger indexes keep posting p99 inside BUD-01? | Total at most 90 ms |

**Query walks.** The estimated time is (dataset TB × 10^6 MB × partition fraction × within-partition fraction) ÷ throughput. It is an idealised bound that ignores startup, decoding and concurrency. A chosen layout must pass; a rejected alternative is shown to fail.

| ID | Query walk | Access pattern | Variant | Dataset source | Dataset TB | Partition fraction | Within-partition fraction | Throughput MB/s | Est time s | Target s | Outcome | Reading |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QWK-01 | Quarterly report reads 3 of 84 posting months | AP-06 | Chosen | GRW-01:horizon*0.2 | 5.80 | 3/84 | 1 | scan_mb_s | 103.6 | 14400 | Pass | Month partitions cut the scan to about 3.6% of the history |
| QWK-02 | Annual reconciliation reads all 84 months | AP-07 | Chosen | GRW-01:horizon*0.2 | 5.80 | 1 | 1 | scan_mb_s | 2,900.0 | 14400 | Pass | A full scan still fits the run objective |
| QWK-03 | Daily risk batch reads the last 60 months | AP-08 | Chosen | GRW-01:horizon*0.2 | 5.80 | 60/84 | 1 | scan_mb_s | 2,071.4 | 7200 | Pass | Fits the window with about 3.5 times headroom; if growth reaches the high case the margin narrows |
| QWK-04 | Daily increment reads one day of card events | AP-09 | Chosen | GRW-02:horizon*0.25 | 18.75 | 1/1095 | 1 | scan_mb_s | 8.6 | 900 | Pass | Daily partitions make the increment a few seconds of scan |
| QWK-05 | One card over 24 months, sorted by card id | AP-05 | Chosen | GRW-02:horizon*0.25 | 18.75 | 24/36 | 0.02 | scan_mb_s | 125.0 | 300 | Pass | Pruning removes a third; sort order removes 98% of the rest (ASM-07) |
| QWK-06 | One card over 24 months, no sort order | AP-05 | Rejected alternative | GRW-02:horizon*0.25 | 18.75 | 24/36 | 1 | scan_mb_s | 6,250.0 | 300 | Fail | Reads the whole 24-month range; fails the 300 s target by an order of magnitude |
| QWK-07 | Last-hour telemetry for one metric | AP-13 | Chosen | GRW-05:horizon*1 | 5.00 | 1/720 | 0.1 | tsdb_scan_mb_s | 1.4 | 30 | Pass | One chunk, one metric: far inside the target |
| QWK-08 | Full ledger history scanned for a card-sized question | AP-05 | Rejected alternative | GRW-01:horizon*0.2 | 5.80 | 1 | 1 | scan_mb_s | 2,900.0 | 300 | Fail | Using the ledger history for card questions would scan the entire history; shows why AST-02 has its own layout |

### 6.10 D10 — Replication and consistency requirements (Step 14)

**Guarantee source.** `System-provided` means the store's documented behaviour gives it. `Architecture-provided` means this design supplies it with a mechanism that must be built and tested. `Assumption` means it is believed but unverified and carries a validation reference.

| ID | Operation guarantee | Workload | Class | Required guarantee | Business consequence | Replica rule | Replica line | Provided by | Staleness budget s | Validation | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OPG-01 | Post a payment | WL-01 | Strong | All entries and the balance commit together or not at all; a repeated idempotency key returns the first result | Wrong balances or a double payment | Primary only | none | System-provided | n/a | TXB-01 | Given |
| OPG-02 | Acknowledged posting survives node or zone loss | WL-01 | Strong | Acknowledgement only after the zone replica has the record | Customer told a payment succeeded and then it disappears | Sync replica only | REP-01 | System-provided | n/a | FS-01 | Given |
| OPG-03 | Balance check for authorisation | WL-01 | Strong | Sees every committed posting | Overdraft or false decline | Primary only | none | System-provided | n/a | AP-02 | Given |
| OPG-04 | Statement for the customer app | WL-01 | Strong | Includes the customer's own latest posting | Customer sees a payment missing | Sync replica only | REP-01 | System-provided | n/a | AP-02 | Assumed |
| OPG-05 | Profile display | WL-02 | Bounded staleness | Shows data at most 5 s old | Minor confusion after an update | Async replica within 5 s | REP-03 | System-provided | 5 | FS-02 | Assumed |
| OPG-06 | Profile read that gates a limit or block | WL-02 | Strong | Reads the latest committed change | A blocked card still approves | Primary only | none | Architecture-provided | n/a | FS-02 | Assumed |
| OPG-07 | Fraud lookup of recent events | WL-04 | Bounded staleness | Event visible within 60 s at p95 | A fraudulent transaction is not recognised | Serving replicas within 2 s | REP-04 | Architecture-provided | 60 | BUD-02 | Assumed |
| OPG-08 | Regulatory report totals | WL-03 | Snapshot | One pinned table snapshot, reconciled to ledger control totals | A misstated filing | Snapshot pinned per report | none | System-provided | n/a | QWK-01 | Assumed |
| OPG-09 | Ledger archival hand-off | WL-03 | Snapshot | Detach the operational partition only after totals match | Lost or duplicated history | Snapshot pinned per partition | none | Architecture-provided | n/a | TXB-04 | Assumed |
| OPG-10 | Erasure request propagation | WL-02 | Eventual | Every copy purged or beyond use within 30 days | A regulatory breach | Any replica | none | Architecture-provided | n/a | FS-05 | Assumed |
| OPG-11 | Legal hold visible to disposal | WL-06 | Strong | The hold flag is read at execution time | An object under hold is deleted | Primary only | none | Architecture-provided | n/a | FS-07 | Assumed |
| OPG-12 | Risk batch input | WL-05 | Snapshot | One consistent as-of view of history | Risk figures computed from mixed days | Snapshot pinned per run | none | System-provided | n/a | QWK-03 | Assumed |

**Replication topology, lag budgets and recovery objectives.** The exposure columns multiply the posting rate by the lag budget (records that fall inside the lag window). They are planning proxies for an RPO conversation, not guarantees.

| ID | Replication line | Store | Replica | Mode | Placement | Lag budget s | RPO s | RTO min | Rate basis | Exposure avg records | Exposure peak records | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REP-01 | Ledger zone replica | STO-01 | Standby in a second zone | Sync | Same site, different zone | 0 | 0 | 5 | WL-01 | 0.0 | 0.0 | Assumed |
| REP-02 | Ledger DR replica | STO-01 | Standby at a second site in the same jurisdiction | Async | Different site | 30 | 30 | 30 | WL-01 | 694.4 | 5,555.6 | Assumed |
| REP-03 | Profile read replicas | STO-02 | Three read replicas, one per zone | Async | Three zones | 5 | 5 | 10 | n/a | n/a | n/a | Assumed |
| REP-04 | Serving store copies | STO-03 | Three copies inside the cluster | Async | Three zones | 2 | 2 | 5 | n/a | n/a | n/a | Assumed |

REP-02 is the open conflict in this design. A site loss can lose up to the exposure shown for the peak rate, which contradicts REQ-02 if REQ-02 is read to cover site loss. BUD-05 shows that making REP-02 synchronous breaks the posting latency headroom. The decision belongs to the sponsor (OQ-04); the package records the exposure and the options rather than hiding them (RSK-01).

**Latency and freshness budgets.** Values are p99 milliseconds for the posting path and p95 seconds for the fraud path. Headroom must be at least 10% (STD-08).

| ID | Latency component | Unit | Value | Evidence |
| --- | --- | --- | --- | --- |
| LAT-01 | Application service processing | ms | 30 | Assumed |
| LAT-02 | Network and connection handling | ms | 10 | Assumed |
| LAT-03 | Ledger execution including index maintenance | ms | 25 | Assumed |
| LAT-04 | Outbox row write | ms | 2 | Assumed |
| LAT-05 | Synchronous zone-replica acknowledgement | ms | 8 | Assumed |
| LAT-06 | Response serialisation | ms | 5 | Assumed |
| LAT-07 | Change capture | s | 5 | Assumed |
| LAT-08 | Transport through the event log | s | 5 | Assumed |
| LAT-09 | Apply to the serving store | s | 10 | Assumed |
| LAT-10 | Micro-batch interval, lakehouse path | s | 30 | Assumed |
| LAT-11 | Table commit and reader visibility | s | 20 | Assumed |
| LAT-12 | Apply lag under stress | s | 120 | Assumed |
| LAT-13 | Synchronous remote-site acknowledgement | ms | 20 | Assumed |

| ID | Budget path | Components | Unit | Total | Target | Headroom | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BUD-01 | Ledger posting p99, chosen design | LAT-01, LAT-02, LAT-03, LAT-04, LAT-05, LAT-06 | ms | 80.0 | 100 | 20.0% | Pass | Derived |
| BUD-02 | Fraud freshness p95, serving-store path (chosen) | LAT-07, LAT-08, LAT-09 | s | 20.0 | 60 | 66.7% | Pass | Derived |
| BUD-03 | Fraud freshness p95, lakehouse micro-batch only (baseline) | LAT-07, LAT-08, LAT-10, LAT-11 | s | 60.0 | 60 | 0.0% | Fail | Derived |
| BUD-04 | Fraud freshness under a 120 s apply-lag stress | LAT-07, LAT-08, LAT-12 | s | 130.0 | 60 | -116.7% | Fail | Derived |
| BUD-05 | Ledger posting p99 with synchronous remote-site commit | LAT-01, LAT-02, LAT-03, LAT-04, LAT-13, LAT-06 | ms | 92.0 | 100 | 8.0% | Fail | Derived |

**Availability budgets.** Allowed minutes = (1 − target) × 30 days × 1,440 minutes. The analytical figure uses a calendar month as a proxy for "business days", which is stricter than the stated wording.

| ID | Availability line | Target | Allowed min per month | Events per month | RTO min | Consumed min | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AV-01 | Ledger posting service | 99.95 | 21.6 | 1 | 5 | 5.0 | Pass | Assumed |
| AV-02 | Analytical platform | 99.5 | 216.0 | 1 | 60 | 60.0 | Pass | Assumed |

### 6.11 D11 — Transaction boundary description (Step 14)

| ID | Transaction boundary | Scope | Atomic unit | Mechanism | Failure handling | Reconciliation | Provided by | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TXB-01 | Posting transaction | STO-01 only | Debit entry, credit entry, balance update, outbox row and idempotency key | One local ACID transaction in the ledger store | A failure rolls back everything; a client retry with the same key returns the original result | Daily control totals: debits equal credits per day and per account | System-provided | Assumed |
| TXB-02 | Outbox publication | STO-01 to STO-07 | One outbox row published at least once | A relay reads unsent rows, publishes, then marks them sent | A relay restart republishes; consumers deduplicate on posting_id | Hourly comparison of sent counts with consumer applied counts | Architecture-provided | Assumed |
| TXB-03 | Analytical apply | STO-07 to STO-04 and STO-03 | One event applied once per target | Idempotent upsert by posting_id or event_id; the target records the last committed position | Replay from the last committed position; duplicates are ignored | Daily row counts and amount totals against the ledger | Architecture-provided | Assumed |
| TXB-04 | Ledger archival hand-off | STO-01 to STO-04 | One month partition | Copy, verify control totals, record in the hand-off register, then detach | A failure before detach leaves the ledger authoritative; nothing is deleted until verification passes | Hand-off register compared with both stores quarterly | Architecture-provided | Assumed |
| TXB-05 | Erasure request workflow | STO-02 and every copy in COP | One request across all locations | A saga: act in each location, record in a deletion ledger, close when all confirm | Retry per location; a request unresolved after 20 days escalates to the Security and Privacy Officer | Weekly report of open requests against the 30-day target; the deletion ledger is replayed after any restore | Architecture-provided | Assumed |
| TXB-06 | Disposal run | STO-05 | A candidate list executed in two steps | Build the list, re-check holds at execution time, delete, verify | If hold status is unknown the object is skipped; a rerun is idempotent | Disposal log compared with the candidate list | Architecture-provided | Assumed |

**No distributed transaction is used.** TXB-01 is the only atomic multi-record boundary, and it lives inside one store. Everything that crosses a store (TXB-02 to TXB-06) uses a retryable, idempotent step plus a reconciliation, because dual writes cannot be made atomic and any step can fail between two writes.

### 6.12 D12 — Retention and storage-tier strategy (Step 15)

**Principles.** A retention source is a legal or business statement from a named authority, not a number someone remembers. Minimum retention, maximum retention, a legal hold and deletion are four different controls. Every figure below is illustrative; the `Legal confirmation` column stays `Required` for every class because no confirmation exists in this package.

| ID | Retention class | Assets | Min retain d | Disposal rule | Source | Legal confirmation | Owner | Hold approach | Tier plan | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RC-01 | Ledger and transaction records | AST-01 | 2555 | Dispose of a month partition in the month after day 2,555 unless a hold applies | REQ-08 (scenario statement; legal source to be cited) | Required | STK-02 | A hold flag on the table partition suspends disposal and the audit trail records who set it | TP-01 | Given |
| RC-02 | Call recordings | AST-04 | 1825 | Dispose of an object after day 1,825 unless a hold applies | REQ-09 (scenario statement) | Required | STK-07 | Hold flag on the object; checked again at execution time (TXB-06) | TP-02 | Given |
| RC-03 | Card event detail | AST-02 | 1095 | Dispose of detail after day 1,095 once the summary is produced; summary rule is open | REQ-10 (scenario statement) | Required | STK-14 | Hold flag on the date partition suspends disposal | TP-03 | Given |
| RC-04 | Operational telemetry | AST-05 | 30 | Drop the time chunk after day 30 | REQ-11 (scenario statement) | Not applicable | STK-08 | No holds expected; a hold request would be refused by policy | TP-04 | Given |
| RC-05 | Customer profile data | AST-03 | 2555 | Seven years after the relationship ends, unless erased earlier where no obligation applies | Assumption pending OQ-03 | Required | STK-03 | Hold flag on the customer key suspends erasure and disposal | TP-05 | Assumed |
| RC-06 | Customer documents | AST-04 | 2555 | Dispose of an object after day 2,555 unless a hold applies | Assumption pending OQ-03 | Required | STK-07 | Hold flag on the object; checked again at execution time | TP-06 | Assumed |
| RC-07 | Legacy lake copies | AST-06 | 0 | Delete only after a governed copy is proven and the contents are classified | Policy decision after OQ-01 | Required | STK-11 | Any discovered hold marks the folder read-only and blocks deletion | TP-07 | Unknown |

**Tier plans.** Stage lengths are in days from the clock start. A stage must respect the minimum storage duration of its tier (STD-12, STD-13). The tiers cover at least the minimum retention.

| ID | Tier plan | Class | Hot d | Cool d | Archive d | Total d | Disposal | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TP-01 | Ledger history stays on the hot object tier (BRK-02 rejects archive) | RC-01 | 2555 | 0 | 0 | 2,555 | Month partition dropped after day 2,555 | Derived |
| TP-02 | Recordings: hot for 90 days, cool to day 365, archive to day 1,825 | RC-02 | 90 | 275 | 1460 | 1,825 | Object deleted after day 1,825 | Derived |
| TP-03 | Card event detail stays hot (BRK-03 rejects the cool move) | RC-03 | 1095 | 0 | 0 | 1,095 | Date partition dropped after day 1,095 | Derived |
| TP-04 | Telemetry stays in its own store | RC-04 | 30 | 0 | 0 | 30 | Time chunk dropped at day 30 | Derived |
| TP-05 | Profile data stays in the operational store | RC-05 | 2555 | 0 | 0 | 2,555 | Erasure workflow after the retention period | Derived |
| TP-06 | Documents: hot for 90 days, cool to day 365, archive to day 2,555 | RC-06 | 90 | 275 | 2190 | 2,555 | Object deleted after day 2,555 | Derived |
| TP-07 | Legacy copies are not tiered | RC-07 | 0 | 0 | 0 | 0 | Deleted after classification | Derived |

**Tier break-even.** Savings = TB × (from price − to price). Net = savings − fixed cost − retrieval price × retrieved GB. A move is recommended when the base net is at least the materiality threshold (STD-14); it is recommended with a trigger when the high case turns negative. Terms such as transition fees and restore delay are excluded here and would lower the break-even in practice.

| ID | Tier break-even | Dataset | TB | From price | To price | Fixed USD/mo | Retrieval USD/GB | Savings USD/mo | Break-even GB/mo | Retrieval low GB | Retrieval base GB | Retrieval high GB | Net low | Net base | Net high | Decision | Plan | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BRK-01 | Media older than one year, cool to archive (one copy) | AST-04 | 240 | price_cool | price_archive | 120 | 0.08 | 1,680 | 19,500 | 1000 | 6000 | 18000 | 1,480 | 1,080 | 120 | Move | TP-02 | Derived |
| BRK-02 | Ledger history, hot to archive (one copy) | AST-01 | 5.8 | price_hot | price_archive | 120 | 0.08 | 122 | 22 | 5800 | 17400 | 124200 | -462 | -1,390 | -9,934 | Keep | TP-01 | Derived |
| BRK-03 | Card event detail in months 25 to 36, hot to cool (one copy) | AST-02 | 6.25 | price_hot | price_cool | 0 | 0.01 | 88 | 8,750 | 0 | 6250 | 18750 | 88 | 25 | -100 | Keep | TP-03 | Derived |

The ledger result is the instructive one: the fixed archive overhead consumes almost all of the storage saving (120 of 122 dollars) before a single byte is retrieved, and because reports scan the history every month, the retrieval charge turns the base case negative.

**Cost lines.** Monthly storage cost at the horizon, expected case, from the stored capacity in 6.5. The media rows split the one capacity row by tier using the tier plan.

| ID | Cost line | Store | Volume source | Stored TB | Price key | Price | Monthly USD | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CST-01 | Ledger hot window with two replicas | STO-01 | CAP-01 | 21.60 | price_db | 100.00 | 2,160 | Derived |
| CST-02 | Ledger history, hot object tier | STO-04 | CAP-02 | 12.18 | price_hot | 24.00 | 292 | Derived |
| CST-03 | Card events curated, hot object tier | STO-04 | CAP-03 | 39.38 | price_hot | 24.00 | 945 | Derived |
| CST-04 | Card events landing, hot object tier | STO-04 | CAP-04 | 6.16 | price_hot | 24.00 | 148 | Derived |
| CST-05 | Recent-events serving store | STO-03 | CAP-05 | 1.73 | price_serving | 60.00 | 104 | Derived |
| CST-06 | Profile store with three read replicas | STO-02 | CAP-06 | 4.64 | price_db | 100.00 | 464 | Derived |
| CST-07 | Media, hot tier | STO-05 | TIER:CAP-07:TP-02:hot | 14.79 | price_hot | 24.00 | 355 | Derived |
| CST-08 | Media, cool tier | STO-05 | TIER:CAP-07:TP-02:cool | 45.21 | price_cool | 10.00 | 452 | Derived |
| CST-09 | Media, archive tier | STO-05 | TIER:CAP-07:TP-02:archive | 480.00 | price_archive | 3.00 | 1,440 | Derived |
| CST-10 | Telemetry store | STO-06 | CAP-08 | 11.00 | price_tsdb | 60.00 | 660 | Derived |
| CST-11 | Consumption zone | STO-04 | CAP-09 | 5.16 | price_hot | 24.00 | 124 | Derived |

**Total cost of ownership sketch.** Storage is the smallest line. People and compute decide the total, which is why the range overlaps across options. The recommended option's storage equals 12 times the monthly cost lines above.

| ID | Option | Storage USD/yr | Compute USD/yr | FTE | People USD/yr | Migration USD/yr | Expected USD/yr | Low USD/yr | High USD/yr | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TCO-01 | A Baseline: minimal change (shared database and the current lake) | 150000 | 120000 | 3.0 | 450,000 | 0 | 720,000 | 576,000 | 1,080,000 | Assumed |
| TCO-02 | B Recommended: separated stores and a lakehouse | 85728 | 140000 | 2.5 | 375,000 | 90000 | 690,728 | 552,582 | 1,036,092 | Assumed |
| TCO-03 | C Consolidate on one managed warehouse platform | 110000 | 210000 | 2.0 | 300,000 | 150000 | 770,000 | 616,000 | 1,155,000 | Assumed |

Compute, FTE and migration figures are assumptions (ASM-12) that stand in for numbers 2D.8 and 2D.13 will supply. Migration is a one-off amount spread over three years. The point of the sketch is the structure and the overlap of the ranges, not a prediction.

**Deletion coverage across the copy graph.** Purge days is the time to purge or put the copy beyond use once a request is eligible. A copy that cannot meet the 30-day target must be beyond use through a deletion ledger replayed after any restore. Pseudonymous assets are included because erasure also means severing the link between a person and their keys.

| ID | Copy location | Asset | Type | Purge days | Purge mechanism | Beyond use | Meets SLA | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| COP-01 | Profile table in STO-02 | AST-03 | Primary | 7 | Delete or pseudonymise through the erasure workflow (TXB-05) | No | Yes | Assumed |
| COP-02 | Profile read replicas | AST-03 | Replica | 7 | Replicated deletion | No | Yes | Assumed |
| COP-03 | Profile backups | AST-03 | Backup | 35 | Ages out at backup retention; the deletion ledger is replayed after any restore | Yes | Beyond-use | Assumed |
| COP-04 | Recent-events store window | AST-02 | Derived | 7 | Seven-day expiry; delete by key on request | No | Yes | Assumed |
| COP-05 | Serving store copies | AST-02 | Replica | 7 | Same expiry on every copy | No | Yes | Assumed |
| COP-06 | Landing zone original files | AST-02 | Primary | 90 | Files hold pseudonymous keys only; the linking key is destroyed at erasure and recorded in the deletion ledger; files expire at day 90 | Yes | Beyond-use | Assumed |
| COP-07 | Curated table snapshots | AST-02 | Snapshot | 7 | Snapshots expire after the 7-day rollback window | No | Yes | Assumed |
| COP-08 | Curated card events | AST-02 | Derived | 14 | Row-level delete through the table format, then snapshot expiry | No | Yes | Assumed |
| COP-09 | Lakehouse backups | AST-02 | Backup | 35 | Ages out at backup retention; the deletion ledger is replayed after any restore | Yes | Beyond-use | Assumed |
| COP-10 | Event log topics | AST-02 | Log | 7 | Topic retention expiry | No | Yes | Assumed |
| COP-11 | Ledger hot window in STO-01 | AST-01 | Primary | 7 | The ledger rows stay under REQ-08; the person link is severed in STO-02 | No | Yes | Assumed |
| COP-12 | Ledger zone and DR replicas | AST-01 | Replica | 7 | Replicated change of the same key mapping | No | Yes | Assumed |
| COP-13 | Ledger history in STO-04 | AST-01 | Derived | 7 | Rows stay under REQ-08; only the link to the person is severed | No | Yes | Assumed |
| COP-14 | Ledger backups | AST-01 | Backup | 35 | Ages out at backup retention; the deletion ledger is replayed after any restore | Yes | Beyond-use | Assumed |
| COP-15 | Recording and document objects | AST-04 | Primary | 30 | Delete the object and all versions once no retention obligation applies | No | Yes | Assumed |
| COP-16 | Second copy of media objects | AST-04 | Replica | 30 | Delete with the object | No | Yes | Assumed |
| COP-17 | Media metadata index rows | AST-04 | Derived | 7 | Delete the row when the object is disposed | No | Yes | Assumed |
| COP-18 | Media backups | AST-04 | Backup | 35 | Ages out at backup retention; the deletion ledger is replayed after any restore | Yes | Beyond-use | Assumed |
| COP-19 | Legacy lake quarantine files | AST-06 | Primary | 30 | Delete or rewrite files after classification | No | Yes | Assumed |
| COP-20 | Legacy lake backups | AST-06 | Backup | 35 | Ages out at backup retention; the deletion ledger is replayed after any restore | Yes | Beyond-use | Assumed |

**Legal holds.** A hold is a flag on the smallest unit disposal acts on (object, partition or customer key). The disposal run re-reads holds at execution time (TXB-06). If hold status cannot be read, the run skips the item. Retention classes with an expiring clock pause that clock while a hold is active.

### 6.13 D13 — Risk and trade-off register (Step 16)

| ID | Risk | Likelihood | Impact | Score | Rating | Mitigation | Owner | Trigger | Decision | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RSK-01 | A site loss can lose acknowledged postings inside the DR lag window (about 5,556 at peak, REP-02), which conflicts with REQ-02 | 3 | 5 | 15 | High | Sponsor decides (OQ-04): accept, replay from upstream channels with reconciliation, or fund a lower-latency site design | STK-02 | A site-loss exercise or the answer to OQ-04 | DEC-02 | Open |
| RSK-02 | Retention periods in this package are not legally confirmed | 4 | 4 | 16 | High | Legal confirms every class (OQ-03) before any disposal rule runs | STK-10 | First scheduled disposal run | DEC-04 | Open |
| RSK-03 | The legacy lake holds unclassified personal data (AST-06) | 4 | 4 | 16 | High | Quarantine read-only; classify before any migration (OQ-01) | STK-09 | Any access request to the legacy copies | DEC-04 | Open |
| RSK-04 | The serving store adds a second pipeline and on-call load | 3 | 3 | 9 | Medium | Re-measure micro-batch freshness (OQ-06); collapse the store into the lakehouse path if it shows the gate margin plus 15 points | STK-08 | OQ-06 shows at least 25% headroom | DEC-05 | Open |
| RSK-05 | Frequent commits create small files that slow reads (FIL-01) | 3 | 3 | 9 | Medium | Scheduled compaction to the target size; alert on median file size | STK-08 | Median file under 64 MB | DEC-08 | Open |
| RSK-06 | Time-travel snapshots keep erased data for the rollback window | 3 | 4 | 12 | Medium | Seven-day snapshot expiry; deletion ledger; legal view on pseudonymous data (OQ-05) | STK-09 | Any extension of the snapshot window | DEC-04 | Open |
| RSK-07 | Peak factors for profile reads and telemetry are planning values | 3 | 3 | 9 | Medium | Measure real peaks (OQ-02) before sizing replicas | STK-03 | Measured peak above the planning value | DEC-03 | Open |
| RSK-08 | Two decisions change winner under a simplicity-heavy weighting | 3 | 3 | 9 | Medium | Record the conditional notes; assess operations capacity (OQ-07) | STK-12 | Platform team size falls below the planning assumption | DEC-04 | Open |
| RSK-09 | Backups hold erased data for up to 35 days | 3 | 4 | 12 | Medium | Beyond-use controls and replay of the deletion ledger on restore | STK-09 | A restore is performed | DEC-03 | Open |
| RSK-10 | Switching to the warehouse option later would lock data into one platform | 2 | 3 | 6 | Low | Keep exports in open formats; document an exit plan in the ADR | STK-12 | DEC-04 flips to CAN-14 | DEC-04 | Accepted |

| ID | Trade-off | Accepted cost | Benefit | Revisit trigger | Decision |
| --- | --- | --- | --- | --- | --- |
| TRD-01 | Separate analytical store | Analytics are minutes behind the ledger and a change pipeline must be run | Month-end load no longer reaches posting | Replica lag stays inside the lag budget for two quarters | DEC-01 |
| TRD-02 | Asynchronous DR replica | A non-zero RPO if a whole site is lost | Posting latency keeps 20% headroom | OQ-04 outcome | DEC-02 |
| TRD-03 | Extra serving store for fraud | One more store to run | 67% freshness headroom against 0% without it | Measured micro-batch headroom reaches 25% | DEC-05 |
| TRD-04 | Lakehouse over a managed warehouse | More table maintenance to own | Lower cost per TB and an easier exit | Operations capacity falls (OQ-07) | DEC-04 |
| TRD-05 | Archive tier for aged media only | Retrieval takes hours and costs per GB | Saves about 1,080 dollars a month at the base case (BRK-01) | Retrieval passes the break-even in BRK-01 | DEC-07 |
| TRD-06 | Direct personal data kept in one store | Joins need a key mapping | Erasure touches one primary store instead of every dataset | Legal view on pseudonymous data (OQ-05) | DEC-08 |

**Open questions.**

| ID | Open question | Owner | Needed by | Blocks | Evidence that settles it | Status |
| --- | --- | --- | --- | --- | --- | --- |
| OQ-01 | What is the size, content and owner of the legacy lake copies, and how is the 120 TB split between documents and recordings? | STK-11 | Before D14 sign-off | AST-06, DEC-04, DEC-07 | A scan of the lake and a count of media objects by type | Open |
| OQ-02 | What are the measured peak factors for profile reads and telemetry? | STK-08 | Before sizing replicas | DEC-03, DEC-06 | One month of rate data at one-minute resolution | Open |
| OQ-03 | What are the legally confirmed retention periods for profiles, documents and card-event summaries? | STK-10 | Before the first disposal run | DEC-04, DEC-07, DEC-08 | Written confirmation per retention class | Open |
| OQ-04 | Is a non-zero RPO acceptable if a whole site is lost? | STK-01 | Before DEC-02 is final | DEC-02 | A sponsor decision citing the exposure in REP-02 | Open |
| OQ-05 | Do pseudonymous keys count as personal data for erasure? | STK-09 | Before DEC-08 is final | DEC-08, DEC-04 | A written privacy opinion | Open |
| OQ-06 | Does lakehouse micro-batching meet the fraud freshness gate with compaction running? | STK-08 | Before DEC-05 is final | DEC-05 | A timed test of commit visibility under realistic load | Open |
| OQ-07 | Can the platform team operate table maintenance, or is a managed warehouse safer? | STK-11 | Before DEC-04 is final | DEC-04, DEC-08 | A staffing review and a maintenance runbook walk-through | Open |
| OQ-08 | Do reports and disputes need more than 24 months of operational ledger rows? | STK-04 | Before DEC-02 is final | DEC-02 | A query-age analysis of the last two years | Open |

### 6.14 D14 — Validation, completion status and final recommendation (Steps 17 to 19)

#### Failure scenarios and validation walks

Each scenario states the behaviour the design provides and cites the quantified evidence. An outcome of `Pass` is not allowed when the cited quantification fails.

| ID | Failure scenario | Category | Trigger | Behaviour by design | Quantified by | Outcome | Requirements | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FS-01 | Ledger primary node fails | Node loss | The primary host stops | The zone replica is promoted; postings in flight are retried with the same idempotency key; RPO is 0 s and recovery takes 5 minutes | AV-01, BUD-01 | Pass | REQ-01, REQ-02 | none |
| FS-02 | Loss of one availability zone | Zone loss | Zone A is unavailable | The ledger fails over as in FS-01; two of three profile replicas remain, 2 x 1,500 = 3,000 reads per second against a 2,083 peak (WL-02); the serving store keeps two of three copies | AV-01 | Pass with residual risk | REQ-01, REQ-04 | The 1,500 reads per second per replica is an assumption (ASM-10) that must be measured |
| FS-03 | Apply lag grows to 120 s on the fraud path | Replica lag | The event consumer stalls | An alert fires at 45 s (75% of the budget); scoring falls back to conservative rules on last-known features; the backlog is drained in order | BUD-04 | Pass with residual risk | REQ-05 | During the lag the 60 s freshness target is missed; the fallback rules accept more false positives |
| FS-04 | A compaction job corrupts a curated table | Corruption | A job rewrites a date partition with a dropped column | The table snapshot before the job is restored within the 7-day window; a corrupted ledger is restored from backup and reconciled with control totals | COP-07 | Pass | REQ-07 | none |
| FS-05 | A customer asks for erasure | Deletion request | An eligible erasure request arrives | The workflow (TXB-05) acts in each copy; replicas, snapshots and landing files are purged or beyond use within 30 days; backups are beyond use and age out by day 35 | COP-01, COP-03, COP-06, COP-08, COP-09 | Pass with residual risk | REQ-13 | Backups hold the data for up to 35 days (beyond use); whether pseudonymous keys need separate erasure is OQ-05 |
| FS-06 | Loss of the primary site | Site loss | Site 1 is unavailable | The DR replica, which stays inside the jurisdiction (CON-01), is promoted in about 30 minutes; acknowledged postings inside the lag window may be lost | REP-02 | Pass with residual risk | REQ-02, CON-01 | Up to the peak-rate exposure in REP-02 can be lost; this contradicts REQ-02 if it covers site loss (RSK-01, OQ-04) |
| FS-07 | A legal hold arrives during a disposal run | Hold | A hold is set on recordings after the candidate list is built | The run re-reads holds at execution time, skips held objects and logs them; a rerun is idempotent | TXB-06 | Pass | REQ-09 | none |
| FS-08 | Streaming commits produce small files | Small files | One-minute commits against the curated table | Commit size is raised to hourly or compaction runs daily to reach the target; an alert fires when the median file falls under 64 MB | FIL-01, FIL-02 | Pass with residual risk | REQ-07 | Until compaction runs the table reads slowly; the design depends on the compaction job being reliable (RSK-05) |
| FS-09 | Month-end reports run while payments are posted | Contention | A quarterly report and the daily risk batch start together | Both read STO-04 only; the ledger has no analytical access path; the ledger budget is unchanged | QWK-01, QWK-03, BUD-01 | Pass | REQ-12 | none |

#### Random trace

`python3 check_storage_design.py FILE --trace 3 --seed 2026` prints three requirements traced forward to decisions, stores, layout and evidence, and three decisions traced back to requirements and workloads. The roadmap's gate asks for three backward and three forward traces; the checker's answer is recorded in section 7.3.

#### Package inventory

All counts are derived from the tables.

| ID | Package inventory | Count |
| --- | --- | --- |
| CNT-01 | Stakeholder roles | 14 |
| CNT-02 | Workloads | 7 |
| CNT-03 | Data assets | 6 |
| CNT-04 | Requirements | 16 |
| CNT-05 | Constraints | 4 |
| CNT-06 | Assumptions | 14 |
| CNT-07 | Dependencies | 3 |
| CNT-08 | Gates | 9 |
| CNT-09 | Candidates | 32 |
| CNT-10 | Decisions | 8 |
| CNT-11 | Stores | 7 |
| CNT-12 | Layout elements | 12 |
| CNT-13 | Access patterns | 16 |
| CNT-14 | Query walks | 8 |
| CNT-15 | Failure scenarios | 9 |
| CNT-16 | Retention classes | 7 |
| CNT-17 | Copy locations | 20 |
| CNT-18 | Risks | 10 |
| CNT-19 | Open questions | 8 |

#### Architecture decision records

#### ADR-01 — Separate analytical storage from the operational ledger (DEC-01)

- **Status.** Proposed; Accepted when the independent reviewer agrees the evidence (not yet done).
- **Context.** WL-01 needs strong consistency and p99 under 100 ms; WL-03, WL-04 history and WL-05 scan years of data. Month-end analytics already slow the operational systems (REQ-12). Isolation must hold without making fraud data stale.
- **Decision.** CAN-03: a separate analytical store fed by outbox and change events. The ledger store (STO-01) is the system of record for 24 months; STO-04 holds history and becomes authoritative after hand-off (SOR-01, SOR-02).
- **Rejected alternatives.** CAN-01 keeps analytics on the shared database and fails gate GT-01, as the scenario already shows. CAN-04, a nightly extract, is up to 86,400 s stale against the 60 s fraud target and fails GT-02. CAN-05 keeps a replica for the recent window and a separate store for history; it scores 3.25 against 4.10 because it runs two analytical paths. CAN-02, a read replica for analytics, scores 3.20: long scans on a replica compete with replication apply, and seven years of history on database storage costs about four times the object tier.
- **Assumptions and risks.** ASM-06 (scan throughput), ASM-08 (24-month hot window). RSK-04 (extra pipeline), RSK-01 (DR exposure).
- **Validation plan.** Run QWK-01 to QWK-03 on a sample; run the month-end scenario (FS-09) and confirm the ledger p99 does not move. Pass: ledger p99 unchanged within measurement noise and every walk inside its target.
- **Revisit triggers.** Lag exceeds the budget for two quarters; the 24-month window proves too short (OQ-08); a workload appears that needs fresh analytical joins.

#### ADR-02 — Store for payment posting and the ledger (DEC-02)

- **Status.** Proposed; conditional on OQ-04.
- **Context.** WL-01 is the highest-consequence workload: atomic double entry, uniqueness of the idempotency key, 23 postings per second on average and 185 at peak, 99.95% availability.
- **Decision.** CAN-06: a relational store with one leader, a synchronous replica in a second zone (REP-01) and an asynchronous replica at a second site (REP-02). Posting is one local transaction (TXB-01).
- **Rejected alternatives.** CAN-07, synchronous multi-site commit, fails gate GT-04 because BUD-05 totals 92 ms and leaves 8% headroom. CAN-09, synchronous commit across zones of one distributed relational cluster, scores 3.65 against 4.20: it passes every gate but scores 2 on operational simplicity (against 4) and 2 on cost (against 4), and one site already gives the required zone resilience. CAN-08, a document store, scores 2.95: uniqueness and multi-record atomicity would be enforced in application code.
- **Assumptions and risks.** ASM-14 (replication latency), ASM-08. RSK-01: site loss can lose acknowledged postings inside the DR lag window.
- **Validation plan.** Walk FS-01, FS-02 and FS-06; confirm BUD-01 with measured latencies. Pass: RPO 0 s on node and zone loss; p99 inside 90 ms.
- **Revisit triggers.** OQ-04 requires zero RPO on site loss; measured p99 exceeds 90 ms; sustained peak above twice the planning peak.

#### ADR-03 — Store for customer profile lookups (DEC-03)

- **Status.** Proposed.
- **Context.** WL-02 is 30 million point reads a day (peak 2,083 per second) on 0.6 TB, p99 under 50 ms. Limit and block changes must be visible immediately.
- **Decision.** CAN-10: keep the existing relational store and serve display reads from three replicas (REP-03); reads that gate a limit or block go to the primary (OPG-06).
- **Rejected alternatives.** CAN-11, a document store, scores 3.70 against 4.20: it fits the read shape but weakens consistency on limit changes and needs a migration with no workload evidence that the current store misses the target. CAN-12 adds an in-memory cache, scoring 3.70: a cache adds invalidation and a stale-block failure mode (OPG-06) for a load the replicas already carry.
- **Assumptions and risks.** ASM-01 (peak factor), ASM-10 (replica capacity). RSK-07.
- **Validation plan.** Measure real peak reads (OQ-02); load-test one replica to confirm 1,500 reads per second. Pass: p99 under 50 ms at the measured peak with one zone down.
- **Revisit triggers.** Measured p99 over 45 ms at peak; peak above 4,000 reads per second.

#### ADR-04 — Analytical storage approach for history (DEC-04)

- **Status.** Proposed; weight-sensitive, conditional on OQ-07.
- **Context.** WL-03, WL-04 history and WL-05 scan seven years of ledger history and three years of card events; corrections and erasure must work row by row (GT-06); open formats reduce lock-in.
- **Decision.** CAN-15: a lakehouse of object storage, an open table format and a query engine chosen in 2D.7.
- **Rejected alternatives.** CAN-13, plain files, fails gate GT-06. CAN-14, a managed warehouse, scores 4.00 against 4.05 and wins under the simplicity-heavy weights (WS-02): it is simpler to run but costs more per TB and is harder to leave. CAN-16 splits data between a warehouse and an external lake and scores 3.35 because it duplicates governance.
- **Assumptions and risks.** ASM-03, ASM-06, ASM-07. RSK-05 (small files), RSK-06 (snapshots keep erased data), RSK-08, RSK-10.
- **Validation plan.** Run QWK-01 to QWK-06; time table maintenance on a sample; rehearse snapshot expiry. Pass: every chosen walk inside target and maintenance inside its window.
- **Revisit triggers.** OQ-07 shows the team cannot run maintenance; total cost of ownership of option C falls below option B (TCO-03 against TCO-02).

#### ADR-05 — Serving path for recent fraud events (DEC-05)

- **Status.** Proposed; conditional on OQ-06.
- **Context.** WL-04 needs events within 60 s at p95 plus 24 months of history. The baseline path through the lakehouse totals 60 s (BUD-03) and has no headroom.
- **Decision.** CAN-19: a key-based serving store fed from the event log, holding a 7-day window (BUD-02: 20 s, 66.7% headroom). History stays in the lakehouse.
- **Rejected alternatives.** CAN-17, lakehouse micro-batch only, fails gate GT-02 on BUD-03. CAN-20, an in-memory store, scores 3.25 against 3.70 and has weaker durability. CAN-18, an operational database replica for the window, scores 3.20 and would put fraud reads on the same replicas that serve profile display.
- **Assumptions and risks.** ASM-05, DEP-01. RSK-04, TRD-03.
- **Validation plan.** Measure lakehouse commit visibility under load (OQ-06); walk FS-03. Pass: the serving path stays under 54 s end to end including a stress case warning at 45 s.
- **Revisit triggers.** OQ-06 shows at least 25% headroom on the lakehouse path; this collapses the serving store (TRD-03).

#### ADR-06 — Store for operational telemetry (DEC-06)

- **Status.** Proposed.
- **Context.** WL-07 writes 167 GB a day (about 1.9 MB per second) with 30-day retention and time-range reads.
- **Decision.** CAN-22: a time-series store that expires data by dropping hourly chunks (PRT-07).
- **Rejected alternatives.** CAN-21, files in the lake, produces 28.9 MB files at one-minute commits (FIL-04) and scores 3.15. CAN-23, a general relational database, scores 3.25 and carries append-only short-lived data at database prices. CAN-24 scores 3.20 and has weaker consistency than the workload needs for alert accuracy.
- **Assumptions and risks.** ASM-01 (peak factor), ASM-06. RSK-07.
- **Validation plan.** Run QWK-07; confirm chunk drop frees space within one hour of day 30. Pass: last-hour query under 30 s; expiry within an hour of the deadline.
- **Revisit triggers.** Retention extends past 90 days; analysts need joins with ledger data.

#### ADR-07 — Store for documents and recordings (DEC-07)

- **Status.** Proposed.
- **Context.** WL-06 holds 120 TB growing 30 TB a year with infrequent retrieval, five-year (recordings) and assumed seven-year (documents) retention and legal holds.
- **Decision.** CAN-26: object storage with a retention lock, a hold flag and lifecycle tiers (TP-02, TP-06); the metadata index lives in the lakehouse (LAY-10).
- **Rejected alternatives.** CAN-25, file shares, fails gate GT-08. CAN-28, a managed content platform, scores 3.50 against 4.60: it governs well but costs more and ties the archive to one product. CAN-27, objects in a relational database, scores 2.75 and multiplies database storage cost.
- **Assumptions and risks.** ASM-09, ASM-11. RSK-02.
- **Validation plan.** Walk FS-07 and the break-even BRK-01. Pass: held objects survive a disposal run; base-case net savings stay above the materiality threshold.
- **Revisit triggers.** Retrieval passes 19,500 GB a month (BRK-01); Legal changes a retention period (OQ-03).

#### ADR-08 — File and table formats in the analytical layer (DEC-08)

- **Status.** Proposed; weight-sensitive, conditional on OQ-07.
- **Context.** Landing must preserve source data exactly for replay; curated data must scan fast, carry a schema and support row-level delete.
- **Decision.** CAN-30: row-oriented original files in the landing zone and columnar files in an open table format for curated and consumption zones.
- **Rejected alternatives.** CAN-29, text files, fails gate GT-06. CAN-31, columnar files in every zone, scores 4.20 against 4.30 and wins under simplicity-heavy weights; it loses exact replay of malformed source records. CAN-32, a second columnar family, scores 3.85 because fewer engines read it.
- **Assumptions and risks.** ASM-03, ASM-07. RSK-05, RSK-06.
- **Validation plan.** Replay one landing day into curated and compare totals; run FIL-02 sizing. Pass: replay totals equal; median curated file at or above 64 MB.
- **Revisit triggers.** OQ-07 outcome; an engine in 2D.7 cannot read the table format.

#### Recommendation summary (one page for the sponsor)

Northbridge should stop asking one database to do everything. Keep payments on the relational ledger store with a synchronous zone replica (nothing acknowledged is lost if a node or zone fails). Move history, reports and risk work to a lakehouse built on object storage and an open table format, fed by events so month-end analytics cannot reach the ledger. Give fraud scoring a small seven-day serving store because the lakehouse path alone leaves no latency headroom. Keep direct personal data in one profile store so erasure touches one primary location. Put documents and recordings on object storage with retention locks and tier aged media to archive, but keep ledger history on the hot tier because reports read it monthly.

Cost sketch (illustrative): storage is a small share of the total; people and compute dominate, and the ranges of the three options overlap (section 6.12). The benefits are isolation, lower risk and an easier exit rather than a lower bill.

**Conditional items** and what would settle them: the DR exposure (OQ-04, sponsor decision), retention periods (OQ-03, Legal), the serving store (OQ-06, a timed commit test), warehouse versus lakehouse (OQ-07, operations review), the legacy lake (OQ-01, a content scan). **Next step:** hand the store and system-of-record rules and freshness needs to module 2D.6 (integration) and the category and constraint set to module 2D.8 (cloud mapping).

#### Completion gate status

The roadmap's gate (7.7) requires every item to hold. The author cannot satisfy the reviewer items, so the package is **not complete** until they are done.

| ID | Gate item | Status | Evidence in this file | Reason |
| --- | --- | --- | --- | --- |
| VAL-01 | D1 to D14 exist, version-dated, with consistent IDs | Met | Sections 6.1 to 6.14 and the deliverable table in section 0 | none |
| VAL-02 | Workload analysis before technology | Met | WL-01 to WL-07 dated before D6; every workload has access patterns | none |
| VAL-03 | At least three feasible candidates per decision with criteria fixed first | Met | CAN-01 to CAN-32; criteria locked 2026-10-17 | none |
| VAL-04 | Estimates show formula, unit, assumption, range; a reviewer reproduces three figures | Partly met | Sections 6.5 and 6.12; the checker reproduces every figure | No human reviewer has reproduced three figures |
| VAL-05 | Logical layout maps to asset, workload and assumption | Met | LAY-01 to LAY-12 | none |
| VAL-06 | Consistency strategy with business consequence and failure analysis | Met | OPG-01 to OPG-12, REP, BUD, FS | none |
| VAL-07 | Lifecycle plan with source, owner, tiers, deletion coverage and holds | Partly met | RC, TP, BRK, COP | Retention sources are not legally confirmed (OQ-03) |
| VAL-08 | Top access patterns and five failure scenarios walked, with outcomes | Met | QWK-01 to QWK-08; FS-01 to FS-09 | none |
| VAL-09 | Recommendation readable by a non-specialist in ten minutes | Partly met | The one-page summary above | Not tested with a non-specialist reader |
| VAL-10 | Traceability succeeds in both directions | Met | Checker trace output in section 7.3 | none |
| VAL-11 | An independent reviewer agrees the evidence supports the conclusions | Not met | none | No independent review has taken place |
| VAL-12 | Challenge round: two objections answered from recorded evidence | Partly met | Section 7.6 | The objections are author-prepared, not from a real reviewer |

---

## 7. Validation and quality assurance

### 7.1 Quality criteria and how each is verified

This table maps the roadmap's validation checks (Section 7.6) to the mechanism in this package.

| Roadmap check | How this package verifies it | Verified by |
| --- | --- | --- |
| Every in-scope asset has a documented requirement | Each asset needs an owner (or `Unknown` plus an open question), a retention class, a growth line or capacity row, a layout element, a system-of-record entry and, for personal data, copy-location rows | Checker |
| Workloads characterised before technologies selected | D3 dated before D6; criteria locked before D6; every decision cites workloads | Checker (dates and references) |
| Technologies fit stated access patterns | Every access pattern names a layout element and its keys must appear there; every scan has a passing walk on the chosen layout; rejected alternatives must fail their own target | Checker |
| Quantitative estimates include units and assumptions | Every derived cell is recomputed from inputs; standards are in one table | Checker; a human should still reproduce three figures (VAL-04) |
| Layout choices have a rationale | Every layout element has an access pattern and an assumption; accepted partitions pass the size standards | Checker |
| Replication and consistency match correctness | Strong guarantees may not use asynchronous replicas; bounded staleness must be at least the replica lag; assumed guarantees need a validation reference | Checker |
| Retention and archival match business needs | Every class has a source, owner, legal flag, hold approach and tier plan that covers the minimum retention and respects minimum tier durations; break-even decisions must agree with the tier plan | Checker |
| Operational complexity and cost accounted for | Cost lines tie to capacity; the recommended option's storage equals 12 × the cost lines; people cost is mandatory | Checker |
| Trade-offs and rejected alternatives documented | Every decision has an ADR with seven labelled parts that cites the decision and the selected candidate; vague rejection wording is refused | Checker |
| Logical architecture internally consistent and traceable | Every store appears in the diagram and is cited by a decision; random traces run in both directions | Checker (`--trace`) |

### 7.2 Running the checker

Python 3.9 or later; standard library only.

```bash
python3 check_storage_design.py 05-storage-technology-selection-and-logical-layout.md           # verify
python3 check_storage_design.py 05-storage-technology-selection-and-logical-layout.md --fill    # fill cells marked ~
python3 check_storage_design.py 05-storage-technology-selection-and-logical-layout.md --trace 3 --seed 2026
```

Save the code in Appendix B as `check_storage_design.py`. Exit status 0 means every check passed.

### 7.3 What the checker verifies, and its recorded output

- **Structure:** table headers match the schema; IDs match their table; no duplicate IDs; no empty cells or placeholder text; every ID mentioned exists.
- **Derived cells:** workload rates; growth with caps; stored capacity; sensitivity and the dominant row; file counts and sizes; partition size, skew and acceptance; query-walk times and outcomes; candidate totals, eligibility and ranks; decision weight-sensitivity; lag exposure; latency, freshness and availability budgets; tier totals; deletion-SLA coverage; cost lines; break-even and decisions; total cost of ownership; risk scores; package counts.
- **Discipline:** weights sum to one and equal the locked set; criteria are locked before D6; every decision has at least three eligible candidates and one baseline; the selected candidate is rank 1 and the runner-up is rank 2; every gate failure has a reason and a cited budget must actually fail; scores are integers from 1 to 5.
- **Consistency and lifecycle:** the rules listed in 7.1.
- **Honesty:** at least one gate item must be unmet, no legal confirmation may be marked `Confirmed`, and the text may not claim approval or independent review.

Recorded output of the final run:

```text
Parsed: AP=16, AST=6, AV=2, BRK=3, BUD=5, CAN=32, CAP=9, CH=3, CNT=19, COP=20, CRT=7, CST=11, DEC=8, DL=14, FIL=4, FND=10, FS=9, GRW=5, GT=9, LAT=13, LAY=12, OPG=12, OQ=8, PRT=9, QWK=8, RC=7, REP=4, REQ=37, RSK=10, SEN=1, SOR=7, STD=23, STK=14, STO=7, TCO=3, TP=7, TRD=6, TXB=6, VAL=12, WL=7, WS=5
All checks passed
```

Recorded output of `--trace 3 --seed 2026`:

```text
Forward (requirement -> decision -> store -> layout -> evidence):
  REQ-04 -> DEC-03 -> STO-02 -> LAY-02 -> FS-02
  REQ-11 -> DEC-06 -> STO-06 -> LAY-11 -> QWK-07
  CON-01 -> DEC-02 -> STO-01 -> LAY-01 -> FS-06
Backward (decision -> requirements and workloads):
  DEC-02 <- REQ-01, REQ-02, REQ-03, REQ-08, CON-01 <- WL-01
  DEC-08 <- REQ-07, REQ-10, REQ-13 <- WL-03, WL-04, WL-05
  DEC-05 <- REQ-05 <- WL-04
```

### 7.4 Critical-error self-review

Before asking for review, read the package against these questions. Any "yes" is a defect to fix.

1. Does any technology appear in the package before its workload is characterised?
2. Is any size, rate or price stated without a unit or a label?
3. Does any decision rest on an average where a peak governs?
4. Is any strong guarantee supported by an asynchronous replica?
5. Is any copy (replica, snapshot, backup, derived table, log) missing from the deletion table?
6. Is any retention period sourced from memory rather than a named authority?
7. Is any "rejected" alternative rejected for a reason that does not cite a criterion, a number or a gate?
8. Does a cheaper tier look attractive only because retrieval, fixed overhead or restore time was left out?
9. Is a conditional decision presented as settled?
10. Does the summary claim approval, a benchmark or an independent review that did not happen?

### 7.5 Project completion gate and status

The roadmap's gate (7.7) lists eleven items. The worked reference meets most and says plainly what it cannot.

| Gate area | Status | Note |
| --- | --- | --- |
| D1–D14 exist, version-dated, consistent IDs | Met | Section 0 and Section 6 |
| Workload analysis | Met | WL and AP tables |
| Technology comparison | Met | 32 candidates, 8 decisions, criteria locked first |
| Quantification | Partly met | Recomputed by the checker; no human reviewer has reproduced three figures |
| Logical layout | Met | LAY table, storage versus table format versus platform distinguished |
| Consistency strategy | Met | OPG, REP, BUD, TXB, FS |
| Lifecycle plan | Partly met | Retention sources are illustrative and not legally confirmed |
| Validation | Met | 8 query walks and 9 failure scenarios |
| Recommendation | Partly met | Not tested with a non-specialist |
| Traceability | Met | Section 7.3 |
| Independent reviewer agrees | **Not met** | By design; the author cannot satisfy it |

**Readiness decision.** *Not yet ready for approval.* The recommendation is coherent and every number is reproducible, but five conditional items (OQ-01, OQ-03, OQ-04, OQ-06, OQ-07) and the independent review remain. Proceed to module 2D.6 on the system-of-record rules and freshness targets, which do not depend on the open items, while the sponsor decides OQ-04.

### 7.6 Anticipated reviewer challenges (author-prepared, not recorded reviewer objections)

| ID | Reviewer objection | Answer from recorded evidence | Evidence ids |
| --- | --- | --- | --- |
| CH-01 | Why add a fraud serving store when the lakehouse already ingests card events? | The lakehouse path totals 60 s against a 60 s target and leaves 0% headroom, while the serving path totals 20 s; the decision is conditional on a timed test | BUD-02, BUD-03, OQ-06 |
| CH-02 | Why not archive the ledger history; it is 7 years old? | Reports scan it monthly; the fixed archive overhead takes 120 of the 122 dollars saved before any retrieval, and the base-case retrieval turns the result to a loss of 1,390 dollars a month | BRK-02, TP-01 |
| CH-03 | The DR replica can lose acknowledged postings. Why accept that? | It is not accepted yet. Synchronous commit to the second site leaves 8% headroom against 10% (BUD-05); the exposure is about 694 postings on average and 5,556 at peak (REP-02); the sponsor must decide (OQ-04) | BUD-05, REP-02, OQ-04 |

### 7.7 Findings from design review and audit

Findings 05 to 10 were found by the audit of version 1.0 and are closed in 1.1; findings 01 to 04 are open by nature.

| ID | Review area | Finding | Type | Severity | Status | Resolution |
| --- | --- | --- | --- | --- | --- | --- |
| FND-01 | Consistency | Site loss can lose acknowledged postings inside the DR lag window, which conflicts with REQ-02 | Design conflict | Major | Open | Recorded as RSK-01 and OQ-04; needs a sponsor decision |
| FND-02 | Lifecycle | No retention source is legally confirmed | Evidence gap | Major | Open | OQ-03; RSK-02 |
| FND-03 | Independence | No independent reviewer has agreed the evidence | Process gap | Major | Open | Not closable by the author; VAL-11 |
| FND-04 | Cost | All prices, FTE cost and compute figures are illustrative | Evidence gap | Minor | Open | Replace with quotes in 2D.8 and 2D.13 (ASM-12) |
| FND-05 | Prose accuracy | Four statements did not match the recomputed numbers: the media archive saving was given as about 1,500 dollars a month (the base-case net is 1,080); the ledger archive reasoning said the fixed overhead "exceeds" the saving (it takes 120 of 122 dollars), here and in CH-02; and ADR-02 asserted "about twice the cost" with no figure behind it | Unsupported claim | Major | Closed | Corrected in TRD-05, 6.12, CH-02 and ADR-02; the audit now compares quoted scores and counts with the tables |
| FND-06 | Consistency | The trigger for collapsing the fraud serving store was 10% headroom in RSK-04 but 25% in TRD-03 and ADR-05 | Inconsistency | Major | Closed | All three use 25% (the 10% gate plus a 15-point margin) |
| FND-07 | Template coverage | The roadmap comparison template asks for limitations and risks per candidate; the matrix had none | Missing content | Major | Closed | Added the Limitation or risk column for all 32 candidates |
| FND-08 | Traceability | Constraints and several requirements had no validation reference | Checker gap | Major | Closed | Rule added: every requirement and constraint cites a validation; each now cites a gate, layout element, walk or open question |
| FND-09 | Honesty | Mutation M18 showed an independent review could be marked Met with no reviewer record | Checker gap | Major | Closed | Rule added: Met needs a record that names the reviewer role (STK-13) |
| FND-10 | Checker parsing | ADR blocks did not end at deeper headings, so later text could satisfy an earlier ADR's required labels | Checker gap | Minor | Closed | Any heading ends the block; the ADR heading text counts for citations |

### 7.8 Hand-calculation check for a reviewer

The roadmap asks a reviewer to reproduce at least three figures without the tool. Four are worked here so the arithmetic can be checked by hand; all use decimal units.

| Figure | Hand calculation | Result |
| --- | --- | --- |
| CAP-01 stored capacity (expected) | Ledger growth 3 TB per year × 2 years = 6 TB; × (1 + 0.20 index overhead) = 7.2 TB; × 3 copies | 21.6 TB |
| QWK-05 one-card query time | 18.75 TB × 1,000,000 MB/TB = 18,750,000 MB; × (24 ÷ 36) × 0.02 = 250,000 MB; ÷ 2,000 MB/s | 125 s |
| BRK-01 archive break-even | Savings 240 TB × (10 − 3) = 1,680 dollars per month; less 120 fixed = 1,560; ÷ 0.08 dollars per GB | 19,500 GB per month |
| BUD-03 baseline freshness | 5 s capture + 5 s transport + 30 s batch interval + 20 s commit and visibility, against 60 s: headroom 0% | 60 s, Fail |

Reproducing these four figures, and the two or three more a reviewer chooses at random, is the human half of VAL-04.

---

## 8. Templates and guides for a real organisation (Mode B)

### 8.1 Row templates

Copy the header exactly. Replace the example text. Keep `~` for derived cells.

```text
Workload:   | ID | Workload | Class | Owner | Asset | Daily ops | Daily GB | Peak factor | Avg ops/s | Peak ops/s | Avg MB/s | Target | Consistency | Availability | Evidence |
Asset:      | ID | Asset | Category | Purpose | Size TB | Growth basis | Rate low | Rate exp | Rate high | Owner | Retention class | Consumers | Personal data | Evidence |
Candidate:  | ID | Candidate | Decision | Baseline | Gates | Gate failure reason | C1 | C2 | C3 | C4 | C5 | C6 | C7 | Total | Eligible | Rank | Evidence |
Layout:     | ID | Layout element | Asset | Store | Workloads | Organisation | Format | Keys | Partition ref | Cluster or index | Retention class | Assumptions | Governance |
Copy:       | ID | Copy location | Asset | Type | Purge days | Purge mechanism | Beyond use | Meets SLA | Evidence |
Retention:  | ID | Retention class | Assets | Min retain d | Disposal rule | Source | Legal confirmation | Owner | Hold approach | Tier plan | Evidence |
```

The remaining tables use the headers shown in Section 6. A new table kind needs a new schema entry in the checker.

### 8.2 Interview guide for workload and data owners

1. What business outcome does this workload serve, and what happens when it is slow, wrong or unavailable?
2. What are the five most frequent reads and the five most important writes? What keys do they use?
3. What are the average and the busiest-hour rates for the last twelve months? Where is that data?
4. How fresh must results be, and how wrong may they be for how long?
5. How big is the data now, how fast does it grow, and which part could be deleted tomorrow?
6. Who decides how long each kind of data is kept, and where is it written down?
7. Which copies exist (replicas, extracts, snapshots, backups, test copies)?
8. What would you do if this store was unavailable for an hour? A day?

### 8.3 Pre-review checklist

- [ ] Every number has a unit and an evidence label.
- [ ] No `~` remains; the checker prints "All checks passed".
- [ ] Every `Unknown` has an open question with an owner.
- [ ] Every retention row names a source and a person in Legal or Records.
- [ ] Every rejected candidate has a reason citing a gate, a number or a criterion.
- [ ] The conditional decisions say what would settle them.
- [ ] A person who did not write the package has agreed to review it.

---

## 9. Common pitfalls and project risks

| Pitfall | Why it hurts | Defence in this package |
| --- | --- | --- |
| Choosing the technology first | Requirements are bent to fit the product | Gates and criteria are locked before candidates are scored; workloads are dated before the matrix |
| Scoring after seeing the winner | The decision becomes a rationalisation | Weights locked with a date; a stress test under four other weight sets |
| Averages hiding peaks | Capacity and latency fail at the busiest hour | Peak factors are explicit inputs; budgets use p99 and p95 |
| Mixing decimal and binary units | Capacity is off by about 10% | Decimal units fixed in the standards table |
| Partitioning by a high-cardinality key | Millions of tiny partitions, metadata overload | Size and skew standards applied mechanically (PRT) |
| A fast layout for the wrong query | The common query still scans everything | Walks with arithmetic, including a rejected alternative that must fail |
| Treating a replica as a backup, or lag as RPO | Data loss on the day it matters | Replica rules per operation; lag exposure shown as a proxy, not a guarantee |
| Dual writes across stores | Silent divergence | Local transaction plus outbox, idempotent apply and reconciliation |
| Archive chosen on storage price | Retrieval and overhead exceed the saving | Break-even with fixed and retrieval costs; ledger history stays hot |
| Erasure that misses copies | Regulatory breach | Copy-by-copy table with a 30-day check and beyond-use rules |
| Retention periods from memory | Over- or under-retention | Source and owner per class; `Required` legal flag until confirmed |
| Unknowns hidden by averages | A confident number from nothing | `Unknown` is allowed; sizing from it is not |
| Claiming approval that did not happen | False comfort | The checker refuses such claims; one gate item must stay unmet until a reviewer signs |
| Letting the project grow into a build | It never ends | Out-of-scope table in 6.1; open questions go to later modules |

---

## 10. Connection to subsequent modules

| Later module | What this project hands over | Where |
| --- | --- | --- |
| 2D.6 Data integration and interoperability | System-of-record rules (SOR), hand-off controls, freshness targets (BUD), transaction boundaries TXB-02 to TXB-04, DEP-01 | 6.8, 6.10, 6.11 |
| 2D.7 Enterprise data platform and lakehouse | Zones, layers (storage, table format, platform), maintenance needs (FIL, RSK-05), OQ-07 | 6.7, 6.8, 6.9 |
| 2D.8 Cloud, hybrid and multi-cloud | Category and constraint set (CON-01 to CON-03), replication placement, price assumptions to replace (ASM-12) | 6.4, 6.10, 6.12 |
| 2D.9 Streaming and real-time | Event log role (STO-07), serving-store role, freshness budget BUD-02 and BUD-03 | 6.8, 6.10 |
| 2D.10 Governance, metadata and lifecycle | Retention schedule, holds, deletion ledger and beyond-use rules, access requirements | 6.12 |
| 2D.12 Reliability and disaster recovery | Replication lines, RPO and RTO, FS-01 to FS-06, RSK-01 | 6.10, 6.14 |
| 2D.13 Performance, scalability and cost | Layout assumptions, validation experiments, cost sketch | 6.9, 6.12 |
| 2D.14 Data access, serving and AI data | Stores and layouts that serve analytics and features, the serving-store pattern | 6.8, 6.9 |

**Open questions logged for 2D.6.** OQ-01 (legacy lake contents), OQ-06 (freshness test) and DEP-01 (change capture and transport).

---

## 11. Self-assessment rubric

Score each row 0 (absent), 1 (partial), 2 (adequate) or 3 (strong). A passing package scores at least 2 on every row and at least 24 of 30.

| # | Criterion | 3 means |
| --- | --- | --- |
| 1 | Scope and assumptions | Exclusions firm; every assumption registered and validated |
| 2 | Workload evidence | Classification justified by rates, shapes and targets, not names |
| 3 | Quantification | Formulas, units, ranges and a named dominant input; a reviewer reproduces three figures |
| 4 | Candidate comparison | Gates and weights locked first; baseline present; sensitivity tested; weight-sensitive decisions flagged |
| 5 | Selection and authority | Every store has a role; one authority per record; hand-offs controlled |
| 6 | Layout and access | Every element tied to a pattern and an assumption; walks prove it; rejected designs fail |
| 7 | Consistency and transactions | Guarantees tied to consequences and to a provider; failure analysis done |
| 8 | Lifecycle | Sources, owners, tiers with break-even, deletion across all copies, holds |
| 9 | Risk, trade-offs and ADRs | Specific rejection reasons; conditional items name what settles them |
| 10 | Honesty and traceability | Open items visible; nothing claimed that did not happen; traces succeed both ways |

---

## Appendix A — Glossary

| Term | Meaning |
| --- | --- |
| Access pattern | The shape of a read or write: the keys, filters, ranges, ordering and frequency |
| Archive tier | A very cheap object tier with long minimum duration, retrieval charges and delay |
| Baseline | The minimal-change option every comparison must include |
| Beyond use | A copy that still exists but cannot be read or restored without the deletion being replayed |
| Clustering (sort order) | Keeping related values physically close so files can be skipped |
| Compaction | Rewriting many small files into fewer files near the target size |
| Control total | A sum or count compared across two systems to prove they agree |
| Deletion ledger | A record of erasures replayed after any restore so erased data do not return |
| Dominant input | The input that contributes most of the spread between low and high totals |
| Exposure (lag) | Records inside the lag window; a planning proxy for RPO, not a guarantee |
| Gate | A pass-or-fail test a candidate must meet before it is scored |
| Headroom | The fraction of a target left unused by a budget |
| Idempotency key | A key that makes a repeated request return the first result |
| Lakehouse | Object storage plus an open table format plus a query engine |
| Legal hold | A flag that suspends disposal of specific data |
| Outbox | A table written in the same transaction as the business data and relayed to a log |
| Partition | A subset of a table separated by a key so unneeded subsets can be skipped |
| Peak factor | The ratio of the busiest rate to the average rate |
| RPO, RTO | Maximum tolerable data loss and maximum tolerable recovery time |
| Retention class | A group of data sharing a source, owner, minimum period and disposal rule |
| Skew ratio | The largest partition divided by the average partition |
| Snapshot | A consistent version of a table that a reader can pin |
| System of record | The one store whose version of a record is authoritative |
| Table format | A metadata layer over files that gives snapshots, schema tracking and atomic commits |
| Tier plan | The days a class spends in each storage tier |
| Time travel | Reading an earlier snapshot; it also retains deleted data until snapshots expire |
| Weight-sensitive | A decision whose winner changes under an alternative weighting |

---

## Appendix B — Package checker and calculator (`check_storage_design.py`)

Python 3.9 or later; standard library only. It reads the Markdown tables in this file, recomputes every derived cell, and checks the package.

```python
#!/usr/bin/env python3
"""Consistency checker and calculator for the storage technology selection and logical layout
package (D1-D14).

Usage:
    python3 check_storage_design.py FILE            verify every table, derived cell and cross-reference
    python3 check_storage_design.py FILE --fill     rewrite derived cells (marked ~) in place
    python3 check_storage_design.py FILE --trace 3 --seed 2026   random traceability walks

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
PREFIXES = ("STK|WL|AST|REQ|CON|ASM|DEP|GRW|CAP|SEN|FIL|PRT|AP|LAY|QWK|STD|CRT|WS|GT|DEC|CAN|STO|SOR|"
            "OPG|REP|LAT|BUD|TXB|RC|TP|COP|CST|BRK|AV|TCO|RSK|TRD|OQ|FND|CH|VAL|DL|FS|ADR|CNT|RV")
ID_ANY = re.compile(rf"\b(?:{PREFIXES})-\d{{2,3}}\b")
EVIDENCE = {"Given", "Assumed", "Derived", "Unknown"}
SCHEMA = {
    "STK": ["ID", "Stakeholder role", "Interest", "Decision rights", "Workloads", "Evidence"],
    "WL": ["ID", "Workload", "Class", "Owner", "Asset", "Daily ops", "Daily GB", "Peak factor",
           "Avg ops/s", "Peak ops/s", "Avg MB/s", "Target", "Consistency", "Availability", "Evidence"],
    "AST": ["ID", "Asset", "Category", "Purpose", "Size TB", "Growth basis", "Rate low", "Rate exp",
            "Rate high", "Owner", "Retention class", "Consumers", "Personal data", "Evidence"],
    "REQ": ["ID", "Statement", "Type", "Measure", "Class test", "Owner", "Workloads", "Validated by",
            "Evidence"],
    "STD": ["ID", "Standard", "Key", "Value", "Unit", "Evidence"],
    "GRW": ["ID", "Growth line", "Asset", "Horizon yr", "Cap yr", "Low TB", "Exp TB", "High TB",
            "Evidence"],
    "CAP": ["ID", "Dataset", "Store", "Logical source", "Logical exp TB", "Overhead", "Copies",
            "Stored low TB", "Stored exp TB", "Stored high TB", "Evidence"],
    "SEN": ["ID", "Sensitivity line", "Total low TB", "Total exp TB", "Total high TB", "Dominant row",
            "Share of spread", "Evidence"],
    "FIL": ["ID", "File arithmetic", "Workload", "Raw GB/day", "Ratio", "Target file MB", "Commits/day",
            "Compressed GB/day", "Files/day at target", "MB per commit file", "Verdict", "Evidence"],
    "PRT": ["ID", "Partition worksheet", "Layout", "Dataset source", "Compressed TB", "Partitions",
            "Avg GB", "Skew ratio", "Largest GB", "Files at largest", "Failed standards", "Verdict",
            "Reason"],
    "AP": ["ID", "Access pattern", "Workload", "Type", "Shape", "Frequency", "Access key", "Target",
           "Layout element", "Evidence"],
    "LAY": ["ID", "Layout element", "Asset", "Store", "Workloads", "Organisation", "Format", "Keys",
            "Partition ref", "Cluster or index", "Retention class", "Assumptions", "Governance"],
    "QWK": ["ID", "Query walk", "Access pattern", "Variant", "Dataset source", "Dataset TB",
            "Partition fraction", "Within-partition fraction", "Throughput MB/s", "Est time s",
            "Target s", "Outcome", "Reading"],
    "CRT": ["ID", "Criterion", "Weight", "Question it answers", "Locked on", "Evidence"],
    "WS": ["ID", "Weight set", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "Purpose"],
    "GT": ["ID", "Gate", "Test", "Decisions", "Evidence"],
    "DEC": ["ID", "Decision", "Workloads", "Requirements", "Selected", "Runner-up", "Weight-sensitive",
            "Conditional on", "ADR"],
    "CAN": ["ID", "Candidate", "Decision", "Baseline", "Gates", "Gate failure reason", "C1", "C2", "C3",
            "C4", "C5", "C6", "C7", "Total", "Eligible", "Rank", "Limitation or risk", "Evidence"],
    "STO": ["ID", "Store", "Category", "Role", "Authoritative for", "Decision", "Layers", "Evidence"],
    "SOR": ["ID", "Authority record", "Data", "Store", "Valid for", "Hand-off control", "Evidence"],
    "OPG": ["ID", "Operation guarantee", "Workload", "Class", "Required guarantee",
            "Business consequence", "Replica rule", "Replica line", "Provided by", "Staleness budget s",
            "Validation", "Evidence"],
    "REP": ["ID", "Replication line", "Store", "Replica", "Mode", "Placement", "Lag budget s", "RPO s",
            "RTO min", "Rate basis", "Exposure avg records", "Exposure peak records", "Evidence"],
    "LAT": ["ID", "Latency component", "Unit", "Value", "Evidence"],
    "BUD": ["ID", "Budget path", "Components", "Unit", "Total", "Target", "Headroom", "Verdict",
            "Evidence"],
    "AV": ["ID", "Availability line", "Target", "Allowed min per month", "Events per month", "RTO min",
           "Consumed min", "Verdict", "Evidence"],
    "TXB": ["ID", "Transaction boundary", "Scope", "Atomic unit", "Mechanism", "Failure handling",
            "Reconciliation", "Provided by", "Evidence"],
    "RC": ["ID", "Retention class", "Assets", "Min retain d", "Disposal rule", "Source",
           "Legal confirmation", "Owner", "Hold approach", "Tier plan", "Evidence"],
    "TP": ["ID", "Tier plan", "Class", "Hot d", "Cool d", "Archive d", "Total d", "Disposal",
           "Evidence"],
    "COP": ["ID", "Copy location", "Asset", "Type", "Purge days", "Purge mechanism", "Beyond use",
            "Meets SLA", "Evidence"],
    "CST": ["ID", "Cost line", "Store", "Volume source", "Stored TB", "Price key", "Price",
            "Monthly USD", "Evidence"],
    "BRK": ["ID", "Tier break-even", "Dataset", "TB", "From price", "To price", "Fixed USD/mo",
            "Retrieval USD/GB", "Savings USD/mo", "Break-even GB/mo", "Retrieval low GB",
            "Retrieval base GB", "Retrieval high GB", "Net low", "Net base", "Net high", "Decision",
            "Plan", "Evidence"],
    "TCO": ["ID", "Option", "Storage USD/yr", "Compute USD/yr", "FTE", "People USD/yr",
            "Migration USD/yr", "Expected USD/yr", "Low USD/yr", "High USD/yr", "Evidence"],
    "RSK": ["ID", "Risk", "Likelihood", "Impact", "Score", "Rating", "Mitigation", "Owner", "Trigger",
            "Decision", "Status"],
    "TRD": ["ID", "Trade-off", "Accepted cost", "Benefit", "Revisit trigger", "Decision"],
    "OQ": ["ID", "Open question", "Owner", "Needed by", "Blocks", "Evidence that settles it",
           "Status"],
    "FS": ["ID", "Failure scenario", "Category", "Trigger", "Behaviour by design", "Quantified by",
           "Outcome", "Requirements", "Residual risk"],
    "VAL": ["ID", "Gate item", "Status", "Evidence in this file", "Reason"],
    "DL": ["ID", "Deliverable", "Section", "Version date", "Status"],
    "FND": ["ID", "Review area", "Finding", "Type", "Severity", "Status", "Resolution"],
    "CH": ["ID", "Reviewer objection", "Answer from recorded evidence", "Evidence ids"],
    "CNT": ["ID", "Package inventory", "Count"],
}
MARKER = {v[1]: k for k, v in SCHEMA.items()}
# derived columns per kind: cell value "~" means compute; the check recomputes and compares
DERIVED = {
    "WL": ["Daily GB", "Avg ops/s", "Peak ops/s", "Avg MB/s"],
    "GRW": ["Low TB", "Exp TB", "High TB"],
    "CAP": ["Logical exp TB", "Stored low TB", "Stored exp TB", "Stored high TB"],
    "SEN": ["Total low TB", "Total exp TB", "Total high TB", "Dominant row", "Share of spread"],
    "FIL": ["Raw GB/day", "Compressed GB/day", "Files/day at target", "MB per commit file", "Verdict"],
    "PRT": ["Compressed TB", "Avg GB", "Largest GB", "Files at largest", "Failed standards", "Verdict"],
    "QWK": ["Dataset TB", "Est time s", "Outcome"],
    "DEC": ["Weight-sensitive"],
    "CAN": ["Total", "Eligible", "Rank"],
    "REP": ["Exposure avg records", "Exposure peak records"],
    "BUD": ["Total", "Headroom", "Verdict"],
    "AV": ["Allowed min per month", "Consumed min", "Verdict"],
    "TP": ["Total d"],
    "COP": ["Meets SLA"],
    "CST": ["Stored TB", "Price", "Monthly USD"],
    "BRK": ["Savings USD/mo", "Break-even GB/mo", "Net low", "Net base", "Net high", "Decision"],
    "TCO": ["People USD/yr", "Expected USD/yr", "Low USD/yr", "High USD/yr"],
    "RSK": ["Score", "Rating"],
    "CNT": ["Count"],
}
NEEDS_EVIDENCE = {k for k, v in SCHEMA.items() if "Evidence" in v}
PLACEHOLDER = re.compile(r"\b(TBD|TODO|FIXME|XXX|lorem|\?\?\?)\b", re.I)
VAGUE = re.compile(r"\b(too complex|not scalable|legacy technology|old technology|not modern|"
                   r"industry standard|best practice)\b", re.I)
SAFE_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
            ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
            ast.UAdd: operator.pos}


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
    """Parse a plain number cell; returns None for n/a, ~, Unknown or non-numeric text."""
    c = cell.strip().replace(",", "").replace("$", "").replace("%", "")
    try:
        return float(c)
    except ValueError:
        return None


def f2(x):
    return f"{x:,.2f}"


def f1(x):
    return f"{x:,.1f}"


def f0(x):
    return f"{x:,.0f}"


def f3(x):
    return f"{x:,.3f}"


def pct(x):
    return f"{x * 100:.1f}%"


def refs(cell):
    return ID_ANY.findall(cell)


def split_list(cell):
    return [x.strip() for x in re.split(r"[,;]", cell) if x.strip() and x.strip() not in ("none", "n/a")]


def close(a, b, tol=0.006):
    return abs(a - b) <= tol * max(1.0, abs(b)) or abs(a - b) < 0.0051


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
        if not ID_CELL.match(cells[0]) or not cells[0].startswith(kind_prefixes(kind, cells[0])):
            errors.append(f"line {number}: ID {cells[0]!r} is not valid in a {kind} table")
            continue
        row = dict(zip(header, cells))
        row["_line"] = number
        if cells[0] in tables[kind]:
            errors.append(f"line {number}: duplicate ID {cells[0]}")
        tables[kind][cells[0]] = row
        locations[number] = (kind, cells[0])
    return tables, "\n".join(prose), diagrams, adr, errors, locations


def kind_prefixes(kind, cell):
    return {"REQ": ("REQ-", "CON-", "ASM-", "DEP-"), "BUD": ("BUD-",)}.get(kind, (kind + "-",))


# ----------------------------------------------------------------------------- calculator
class Ctx:
    def __init__(self, tables):
        self.t = tables

    # ---- standards
    def std(self, key):
        for r in self.t["STD"].values():
            if r["Key"] == key:
                v = num(r["Value"])
                if v is None:
                    raise ValueError(f"standard {key} is not numeric")
                return v
        raise KeyError(f"standard {key} is not defined")

    def price(self, key):
        return self.std(key)

    # ---- assets
    def asset(self, aid):
        r = self.t["AST"][aid]
        basis = r["Growth basis"]
        return {"row": r, "size": num(r["Size TB"]), "basis": basis,
                "rates": [num(r["Rate low"]), num(r["Rate exp"]), num(r["Rate high"])]}

    def retention_days(self, aid):
        rc = self.t["RC"].get(self.t["AST"][aid]["Retention class"].split(",")[0].strip())
        return num(rc["Min retain d"]) if rc else None

    def growth(self, a, horizon, cap):
        out = []
        for rate in a["rates"]:
            if a["basis"] == "linear":
                g = a["size"] + rate * horizon
                if cap is not None:
                    g = min(g, rate * cap)
            elif a["basis"] == "compound":
                g = a["size"] * (1 + rate) ** horizon
            else:
                g = a["size"]
            out.append(g)
        return out

    def grw(self, gid):
        r = self.t["GRW"][gid]
        a = self.asset(r["Asset"])
        cap = num(r["Cap yr"])
        return self.growth(a, num(r["Horizon yr"]), cap), a

    def triple(self, source):
        """Source formula -> (low, exp, high) logical TB."""
        m = re.match(r"^(GRW-\d+):(horizon|rate)\*(.+)$", source.strip())
        if m:
            gid, what, factor = m.groups()
            vals, a = self.grw(gid)
            if what == "rate":
                vals = a["rates"]
            k = safe_eval(factor)
            return [v * k for v in vals]
        m = re.match(r"^SUM\(([A-Z0-9,\- ]+)\)\*(.+)$", source.strip())
        if m:
            ids = [x.strip() for x in m.group(1).split(",")]
            k = safe_eval(m.group(2))
            parts = [self.triple(self.t["CAP"][i]["Logical source"]) for i in ids]
            return [sum(p[j] for p in parts) * k for j in range(3)]
        raise ValueError(f"unsupported source formula {source!r}")

    def cap(self, cid):
        r = self.t["CAP"][cid]
        logical = self.triple(r["Logical source"])
        ov, copies = num(r["Overhead"]), num(r["Copies"])
        stored = [v * (1 + ov) * copies for v in logical]
        return {"logical": logical, "stored": stored, "overhead": ov, "copies": copies, "row": r}

    def dataset_exp(self, source):
        return self.triple(source)[1]

    def wl_daily_gb(self, wid):
        r = self.t["WL"][wid]
        a = self.asset(r["Asset"])
        if a["basis"] == "linear":
            return a["rates"][1] * 1000 / 365
        if a["basis"] == "steady":
            days = self.retention_days(r["Asset"])
            return a["size"] * 1000 / days
        return None

    def expr(self, cell):
        return safe_eval(cell.replace(",", ""))

    def throughput(self, cell):
        v = num(cell)
        return v if v is not None else self.std(cell.strip())

    # ---- selection
    def weights(self, set_id=None):
        if set_id is None:
            return [num(r["Weight"]) for r in sorted(self.t["CRT"].values(), key=lambda r: r["ID"])]
        r = self.t["WS"][set_id]
        return [num(r[f"C{i}"]) for i in range(1, 8)]

    def can_total(self, cid, set_id=None):
        r = self.t["CAN"][cid]
        w = self.weights(set_id)
        return sum(wi * num(r[f"C{i + 1}"]) for i, wi in enumerate(w))

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
        scored = sorted(((self.can_total(c["ID"], set_id), c["ID"]) for c in cands), key=lambda x: (-round(x[0], 6), x[1]))
        return scored

    def path_total(self, bid):
        r = self.t["BUD"][bid]
        comps = [c for c in split_list(r["Components"])]
        return sum(num(self.t["LAT"][c]["Value"]) for c in comps)

    def path_verdict(self, bid):
        r = self.t["BUD"][bid]
        total, target = self.path_total(bid), num(r["Target"])
        head = 1 - total / target
        return total, head, "Pass" if head >= self.std("headroom_min") - 1e-9 else "Fail"


# ----------------------------------------------------------------------------- derivers
def derive_row(kind, row, ctx):
    """Return {column: expected text} for the derived columns of a row."""
    t = ctx.t
    out = {}
    if kind == "WL":
        daily = num(row["Daily ops"])
        if row["Daily GB"] == "n/a":
            gb = None
        else:
            gb = ctx.wl_daily_gb(row["ID"])
            if gb is None:
                raise ValueError("Daily GB cannot be derived from this asset's growth basis")
        out["Daily GB"] = "n/a" if gb is None else f2(gb)
        pf = num(row["Peak factor"])
        if daily is None:
            out["Avg ops/s"] = out["Peak ops/s"] = "n/a"
        else:
            avg = daily / ctx.std("seconds_per_day")
            out["Avg ops/s"] = f2(avg)
            out["Peak ops/s"] = f2(avg * pf)
        out["Avg MB/s"] = "n/a" if gb is None else f3(gb * 1000 / ctx.std("seconds_per_day"))
    elif kind == "GRW":
        vals, _ = ctx.grw(row["ID"])
        out["Low TB"], out["Exp TB"], out["High TB"] = (f2(v) for v in vals)
    elif kind == "CAP":
        c = ctx.cap(row["ID"])
        out["Logical exp TB"] = f2(c["logical"][1])
        out["Stored low TB"], out["Stored exp TB"], out["Stored high TB"] = (f2(v) for v in c["stored"])
    elif kind == "SEN":
        caps = [ctx.cap(i) for i in sorted(t["CAP"])]
        lo, ex, hi = (sum(c["stored"][j] for c in caps) for j in range(3))
        out["Total low TB"], out["Total exp TB"], out["Total high TB"] = f2(lo), f2(ex), f2(hi)
        spreads = sorted(((c["stored"][2] - c["stored"][0], c["row"]["ID"]) for c in caps), reverse=True)
        out["Dominant row"] = spreads[0][1]
        out["Share of spread"] = pct(spreads[0][0] / (hi - lo)) if hi > lo else "n/a"
    elif kind == "FIL":
        raw = ctx.wl_daily_gb(row["Workload"])
        ratio, commits = num(row["Ratio"]), num(row["Commits/day"])
        comp = raw / ratio
        out["Raw GB/day"] = f2(raw)
        out["Compressed GB/day"] = f2(comp)
        out["Files/day at target"] = f1(comp * 1000 / num(row["Target file MB"]))
        mb = comp * 1000 / commits
        out["MB per commit file"] = f1(mb)
        out["Verdict"] = "Small files" if mb < ctx.std("small_file_mb") else "OK"
    elif kind == "PRT":
        tb = ctx.dataset_exp(row["Dataset source"])
        parts, skew = num(row["Partitions"]), num(row["Skew ratio"])
        avg = tb * 1000 / parts
        largest = avg * skew
        out["Compressed TB"] = f2(tb)
        out["Avg GB"] = f"{avg:,.3f}" if avg < 10 else f2(avg)
        out["Largest GB"] = f"{largest:,.3f}" if largest < 10 else f2(largest)
        out["Files at largest"] = f0(math.ceil(largest * 1000 / ctx.std("target_file_mb")))
        failed = []
        if avg < ctx.std("min_partition_gb"):
            failed.append("min_partition_gb")
        if largest > ctx.std("max_partition_gb"):
            failed.append("max_partition_gb")
        if skew > ctx.std("max_skew"):
            failed.append("max_skew")
        out["Failed standards"] = ", ".join(failed) if failed else "none"
        out["Verdict"] = "Reject" if failed else "Accept"
    elif kind == "QWK":
        tb = ctx.dataset_exp(row["Dataset source"])
        pf, wf = ctx.expr(row["Partition fraction"]), ctx.expr(row["Within-partition fraction"])
        secs = tb * 1e6 * pf * wf / ctx.throughput(row["Throughput MB/s"])
        out["Dataset TB"] = f2(tb)
        out["Est time s"] = f1(secs)
        out["Outcome"] = "Pass" if secs <= num(row["Target s"]) else "Fail"
    elif kind == "DEC":
        flips = []
        for ws in sorted(t["WS"]):
            ranking = ctx.ranking(row["ID"], ws)
            if ranking and ranking[0][1] != row["Selected"]:
                flips.append(ws)
        out["Weight-sensitive"] = ("Yes (" + ", ".join(flips) + ")") if flips else "No"
    elif kind == "CAN":
        out["Total"] = f2(ctx.can_total(row["ID"]))
        elig = ctx.eligible(row["ID"])
        out["Eligible"] = "Yes" if elig else "No"
        rank = "-"
        if elig:
            ranking = ctx.ranking(row["Decision"])
            better = sum(1 for s, _ in ranking if round(s, 6) > round(ctx.can_total(row["ID"]), 6))
            rank = str(better + 1)
        out["Rank"] = rank
    elif kind == "REP":
        base = row["Rate basis"]
        lag = num(row["Lag budget s"])
        if base == "n/a":
            out["Exposure avg records"] = out["Exposure peak records"] = "n/a"
        else:
            w = t["WL"][base]
            avg = num(w["Avg ops/s"]) if num(w["Avg ops/s"]) is not None else None
            daily = num(w["Daily ops"])
            avg = daily / ctx.std("seconds_per_day")
            peak = avg * num(w["Peak factor"])
            out["Exposure avg records"] = f1(avg * lag)
            out["Exposure peak records"] = f1(peak * lag)
    elif kind == "BUD":
        total, head, verdict = ctx.path_verdict(row["ID"])
        out["Total"] = f1(total)
        out["Headroom"] = pct(head)
        out["Verdict"] = verdict
    elif kind == "AV":
        allowed = (1 - num(row["Target"]) / 100) * ctx.std("month_days") * 1440
        consumed = num(row["Events per month"]) * num(row["RTO min"])
        out["Allowed min per month"] = f1(allowed)
        out["Consumed min"] = f1(consumed)
        out["Verdict"] = "Pass" if consumed <= allowed else "Fail"
    elif kind == "TP":
        out["Total d"] = f0(num(row["Hot d"]) + num(row["Cool d"]) + num(row["Archive d"]))
    elif kind == "COP":
        days, sla = num(row["Purge days"]), ctx.std("deletion_sla_days")
        if days <= sla:
            out["Meets SLA"] = "Yes"
        elif row["Beyond use"] == "Yes" and "deletion ledger" in row["Purge mechanism"].lower():
            out["Meets SLA"] = "Beyond-use"
        else:
            out["Meets SLA"] = "No"
    elif kind == "CST":
        tb = cst_volume(row["Volume source"], ctx)
        price = ctx.price(row["Price key"])
        out["Stored TB"] = f2(tb)
        out["Price"] = f2(price)
        out["Monthly USD"] = f0(tb * price)
    elif kind == "BRK":
        tb = num(row["TB"])
        p_from, p_to = ctx.price(row["From price"]), ctx.price(row["To price"])
        fixed, retr = num(row["Fixed USD/mo"]), num(row["Retrieval USD/GB"])
        savings = tb * (p_from - p_to)
        out["Savings USD/mo"] = f0(savings)
        out["Break-even GB/mo"] = f0((savings - fixed) / retr) if savings > fixed and retr > 0 else "none"
        nets = [savings - fixed - retr * num(row[k]) for k in ("Retrieval low GB", "Retrieval base GB", "Retrieval high GB")]
        out["Net low"], out["Net base"], out["Net high"] = (f0(n) for n in nets)
        mat = ctx.std("materiality_usd")
        if nets[1] < mat:
            decision = "Keep"
        elif nets[2] < 0:
            decision = "Move with trigger"
        else:
            decision = "Move"
        out["Decision"] = decision
    elif kind == "TCO":
        people = num(row["FTE"]) * ctx.std("fte_cost_usd")
        total = num(row["Storage USD/yr"]) + num(row["Compute USD/yr"]) + people + num(row["Migration USD/yr"])
        out["People USD/yr"] = f0(people)
        out["Expected USD/yr"] = f0(total)
        out["Low USD/yr"] = f0(total * ctx.std("cost_low_factor"))
        out["High USD/yr"] = f0(total * ctx.std("cost_high_factor"))
    elif kind == "RSK":
        score = num(row["Likelihood"]) * num(row["Impact"])
        out["Score"] = f0(score)
        out["Rating"] = "High" if score >= 15 else "Medium" if score >= 8 else "Low"
    elif kind == "CNT":
        out["Count"] = f0(count_of(row["Package inventory"], ctx))
    return out


def cst_volume(source, ctx):
    t = ctx.t
    m = re.match(r"^TIER:(CAP-\d+):(TP-\d+):(hot|cool|archive)$", source.strip())
    if m:
        cid, tpid, tier = m.groups()
        c = ctx.cap(cid)
        gid = re.match(r"^(GRW-\d+):", c["row"]["Logical source"]).group(1)
        _, a = ctx.grw(gid)
        tp = t["TP"][tpid]
        rate = a["rates"][1]
        hot = rate * num(tp["Hot d"]) / 365
        cool = rate * num(tp["Cool d"]) / 365
        logical = c["logical"][1]
        part = {"hot": hot, "cool": cool, "archive": logical - hot - cool}[tier]
        return part * (1 + c["overhead"]) * c["copies"]
    m = re.match(r"^(CAP-\d+)$", source.strip())
    if m:
        return ctx.cap(m.group(1))["stored"][1]
    raise ValueError(f"unsupported volume source {source!r}")


COUNT_KEYS = {
    "Stakeholder roles": "STK", "Workloads": "WL", "Data assets": "AST", "Requirements": "REQ-",
    "Constraints": "CON-", "Assumptions": "ASM-", "Dependencies": "DEP-", "Candidates": "CAN",
    "Decisions": "DEC", "Stores": "STO", "Layout elements": "LAY", "Access patterns": "AP",
    "Query walks": "QWK", "Failure scenarios": "FS", "Retention classes": "RC", "Copy locations": "COP",
    "Risks": "RSK", "Open questions": "OQ", "Gates": "GT",
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

    def need(kind, minimum=1):
        if len(t[kind]) < minimum:
            err(f"table {kind} has {len(t[kind])} rows; at least {minimum} required")

    for kind, minimum in (("STK", 8), ("WL", 7), ("AST", 6), ("REQ", 15), ("STD", 20), ("GRW", 4), ("CAP", 8),
                          ("SEN", 1), ("FIL", 3), ("PRT", 6), ("AP", 10), ("LAY", 10), ("QWK", 6), ("CRT", 7),
                          ("WS", 4), ("GT", 7), ("DEC", 8), ("CAN", 24), ("STO", 6), ("SOR", 6),
                          ("OPG", 8), ("REP", 4), ("LAT", 8), ("BUD", 4), ("AV", 2), ("TXB", 4), ("RC", 7),
                          ("TP", 5), ("COP", 12), ("CST", 8), ("BRK", 3), ("TCO", 3), ("RSK", 8),
                          ("TRD", 5), ("OQ", 6), ("FS", 8), ("VAL", 10), ("DL", 14), ("FND", 4), ("CH", 2),
                          ("CNT", 10)):
        need(kind, minimum)

    # ---- placeholders, evidence labels, derived cells, reference integrity
    known = {rid for kind in t for rid in t[kind]}
    known |= set(adr)
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
                if col not in ("ID",):
                    for ref in refs(cell):
                        if ref not in known:
                            err(f"{rid}: {col} references unknown ID {ref}")
            if kind in NEEDS_EVIDENCE and "Evidence" in row and row["Evidence"] not in EVIDENCE:
                if not (kind == "CH"):
                    err(f"{rid}: Evidence must be one of {sorted(EVIDENCE)}, found {row['Evidence']!r}")
    if errors:
        return errors
    for kind in DERIVED:
        for rid, row in t[kind].items():
            try:
                expected = derive_row(kind, row, ctx)
            except (KeyError, ValueError, TypeError, ZeroDivisionError, AttributeError) as exc:
                err(f"{rid}: cannot recompute derived cells ({type(exc).__name__}: {exc})")
                continue
            for col, val in expected.items():
                if row[col] == "~":
                    err(f"{rid}: derived cell {col} not filled (run --fill); expected {val}")
                elif row[col] != val:
                    err(f"{rid}: {col} is {row[col]!r}; recomputed {val!r}")
    if errors:
        return errors

    # ---- stakeholders, workloads, assets
    for wid, w in t["WL"].items():
        if w["Owner"] not in t["STK"] and w["Owner"] != "Unknown":
            err(f"{wid}: owner {w['Owner']} is not a stakeholder")
        if w["Class"] not in ("OLTP", "OLAP", "Mixed", "Specialised"):
            err(f"{wid}: class {w['Class']!r} invalid")
        if w["Asset"] not in t["AST"]:
            err(f"{wid}: asset {w['Asset']} unknown")
        if not any(a["Workload"] == wid for a in t["AP"].values()):
            err(f"{wid}: no access pattern listed")
        if not any(wid in split_list(r["Workloads"]) for r in t["DEC"].values()):
            err(f"{wid}: not cited by any decision")
    for aid, a in t["AST"].items():
        if a["Category"] not in ("Structured", "Semi-structured", "Unstructured", "Time-series"):
            err(f"{aid}: category {a['Category']!r} invalid")
        if a["Growth basis"] not in ("linear", "compound", "steady", "Unknown"):
            err(f"{aid}: growth basis {a['Growth basis']!r} invalid")
        if a["Personal data"] not in ("Direct", "Pseudonymous", "None"):
            err(f"{aid}: personal data flag {a['Personal data']!r} invalid")
        unknown_size = num(a["Size TB"]) is None
        if unknown_size and not refs(a["Evidence"] + a["Purpose"] + a["Consumers"]) and not any(
                aid in r["Blocks"] for r in t["OQ"].values()):
            err(f"{aid}: unknown size without an open question")
        for rc in split_list(a["Retention class"]):
            if rc not in t["RC"]:
                err(f"{aid}: retention class {rc} unknown")
        for w in split_list(a["Consumers"]):
            if w not in t["WL"]:
                err(f"{aid}: consumer {w} is not a workload")
        if a["Owner"] not in t["STK"] and a["Owner"] != "Unknown":
            err(f"{aid}: owner {a['Owner']} is not a stakeholder or Unknown")
        if not any(r["Asset"] == aid for r in t["LAY"].values()):
            err(f"{aid}: no layout element")
        if not any(aid in r["Data"] for r in t["SOR"].values()):
            err(f"{aid}: no system-of-record entry")
        if not unknown_size and not any(aid in c["Dataset"] or aid in c["Evidence"] for c in t["CAP"].values()) \
                and not any(g["Asset"] == aid for g in t["GRW"].values()):
            err(f"{aid}: no growth line or capacity row")
        if a["Personal data"] != "None" and not any(c["Asset"] == aid for c in t["COP"].values()):
            err(f"{aid}: personal data without copy-location rows")
    for gid, g in t["GRW"].items():
        if g["Asset"] not in t["AST"]:
            err(f"{gid}: asset unknown")

    # ---- requirements and traceability
    for rid, r in t["REQ"].items():
        if r["Type"] not in ("Requirement", "Constraint", "Assumption", "Dependency"):
            err(f"{rid}: type {r['Type']!r} invalid")
        expected_type = {"REQ": "Requirement", "CON": "Constraint", "ASM": "Assumption",
                         "DEP": "Dependency"}[rid.split("-")[0]]
        if r["Type"] != expected_type:
            err(f"{rid}: ID prefix implies {expected_type} but type is {r['Type']}")
        if r["Owner"] not in t["STK"] and r["Owner"] != "Unknown":
            err(f"{rid}: owner {r['Owner']} is not a stakeholder")
        for w in split_list(r["Workloads"]):
            if w not in t["WL"]:
                err(f"{rid}: workload {w} unknown")
        if r["Type"] == "Assumption":
            vb = [x for x in refs(r["Validated by"]) if x.split("-")[0] in ("QWK", "FS", "OQ", "BUD", "PRT", "BRK", "FIL", "SEN", "AV", "CST", "COP")]
            if not vb:
                err(f"{rid}: assumption without a validation reference")
        if r["Type"] in ("Requirement", "Constraint") and not any(
                rid in d["Requirements"] for d in t["DEC"].values()):
            err(f"{rid}: not cited by any decision")
        if r["Type"] in ("Requirement", "Constraint") and not refs(r["Validated by"]):
            err(f"{rid}: no validation reference")
    decided_reqs = {x for d in t["DEC"].values() for x in refs(d["Requirements"])}
    for rid in t["REQ"]:
        if rid.split("-")[0] in ("REQ", "CON") and rid not in decided_reqs:
            err(f"{rid}: no decision traces back to it")

    # ---- selection discipline
    crt_sum = sum(num(r["Weight"]) for r in t["CRT"].values())
    if abs(crt_sum - 1) > 1e-9:
        err(f"criteria weights sum to {crt_sum}, expected 1")
    for wsid, r in t["WS"].items():
        s = sum(num(r[f"C{i}"]) for i in range(1, 8))
        if abs(s - 1) > 1e-9:
            err(f"{wsid}: weights sum to {s}")
    base = t["WS"].get("WS-00")
    if base is None:
        err("WS-00 (the locked weights) is missing")
    elif [num(base[f"C{i}"]) for i in range(1, 8)] != ctx.weights():
        err("WS-00 differs from the weights in the criteria table")
    dl = {r["Deliverable"].split(" ")[0]: r for r in t["DL"].values()}
    d3 = next((r for r in t["DL"].values() if r["Deliverable"].startswith("D3")), None)
    d6 = next((r for r in t["DL"].values() if r["Deliverable"].startswith("D6")), None)
    for cid, c in t["CRT"].items():
        if d6 and c["Locked on"] > d6["Version date"]:
            err(f"{cid}: criteria locked after the comparison matrix date")
    if d3 and d6 and d3["Version date"] > d6["Version date"]:
        err("D3 workload characterisation is dated after D6 comparison")
    gate_dec = {g: set(refs(r["Decisions"])) for g, r in t["GT"].items()}
    for did, d in t["DEC"].items():
        cands = [c for c in t["CAN"].values() if c["Decision"] == did]
        elig = [c for c in cands if ctx.eligible(c["ID"])]
        if len(elig) < 3:
            err(f"{did}: {len(elig)} eligible candidates; at least 3 required")
        if not any(c["Baseline"] == "Yes" for c in cands):
            err(f"{did}: no baseline (minimal-change) candidate")
        if sum(1 for c in cands if c["Baseline"] == "Yes") > 1:
            err(f"{did}: more than one baseline candidate")
        ranking = ctx.ranking(did)
        if not ranking:
            err(f"{did}: no eligible candidate")
            continue
        if d["Selected"] not in t["CAN"] or t["CAN"][d["Selected"]]["Decision"] != did:
            err(f"{did}: selected candidate {d['Selected']} is not a candidate of this decision")
        elif ranking[0][1] != d["Selected"]:
            err(f"{did}: selected {d['Selected']} is not rank 1 at the locked weights ({ranking[0][1]})")
        want_runner = ranking[1][1] if len(ranking) > 1 else "none"
        if d["Runner-up"] != want_runner:
            err(f"{did}: runner-up should be {want_runner}")
        if d["Weight-sensitive"].startswith("Yes") and d["Conditional on"] in ("none", "n/a"):
            err(f"{did}: weight-sensitive decision without a conditional note")
        if not d["ADR"] in adr:
            err(f"{did}: ADR {d['ADR']} missing")
        for w in split_list(d["Workloads"]):
            if w not in t["WL"]:
                err(f"{did}: workload {w} unknown")
        for c in cands:
            gates = ctx.can_gates(c["ID"])
            applicable = {g for g, ds in gate_dec.items() if did in ds}
            if set(gates) != applicable:
                err(f"{c['ID']}: gates {sorted(gates)} differ from the gates applicable to {did} {sorted(applicable)}")
            for g, v in gates.items():
                if v not in ("P", "F"):
                    err(f"{c['ID']}: gate result {v!r} invalid")
            failed = [g for g, v in gates.items() if v == "F"]
            if failed and c["Gate failure reason"] in ("none", "n/a"):
                err(f"{c['ID']}: gate failure without a reason")
            if not failed and c["Gate failure reason"] not in ("none", "n/a"):
                err(f"{c['ID']}: a reason is given but no gate failed")
            for b in refs(c["Gate failure reason"]):
                if b.startswith("BUD-") and t["BUD"][b]["Verdict"] != "Fail":
                    err(f"{c['ID']}: cites {b} as the failure reason but that budget passes")
            if VAGUE.search(c["Gate failure reason"]) or VAGUE.search(c["Candidate"]):
                err(f"{c['ID']}: vague rejection wording")
            for i in range(1, 8):
                s = num(c[f"C{i}"])
                if s is None or s != int(s) or not 1 <= s <= 5:
                    err(f"{c['ID']}: score C{i} must be an integer 1-5")
            if not refs(c["Gate failure reason"] + c["Candidate"] + c["Evidence"]) and False:
                pass
    for gid, g in t["GT"].items():
        for d in gate_dec[gid]:
            if d not in t["DEC"]:
                err(f"{gid}: decision {d} unknown")
        if not gate_dec[gid]:
            err(f"{gid}: gate applies to no decision")

    # ---- stores and diagram
    diagram = diagrams.get("D8-DIAGRAM", "")
    if not diagram:
        err("D8-DIAGRAM fence missing")
    else:
        in_diagram = set(re.findall(r"\[(STO-\d{2})\]", diagram))
        for sid in t["STO"]:
            if sid not in in_diagram:
                err(f"{sid}: missing from D8-DIAGRAM")
        for sid in in_diagram - set(t["STO"]):
            err(f"D8-DIAGRAM mentions unknown store {sid}")
    cited_decisions = {x for s in t["STO"].values() for x in refs(s["Decision"])}
    for did in t["DEC"]:
        if did not in cited_decisions:
            err(f"{did}: no store cites this decision")
    for sid, s in t["STO"].items():
        if not refs(s["Decision"]) and "Deferred" not in s["Decision"]:
            err(f"{sid}: store has neither a decision nor a deferral")
        for layer in ("storage", "table format", "platform"):
            if "Layers" in s and s["Category"].startswith("Object") and layer not in s["Layers"].lower():
                err(f"{sid}: object-store layers must name storage, table format and platform")
    for sid, r in t["SOR"].items():
        if r["Store"] not in t["STO"]:
            err(f"{sid}: store {r['Store']} unknown")
    sor_assets = {}
    for r in t["SOR"].values():
        for a in refs(r["Data"]):
            sor_assets.setdefault(a, []).append(r)

    # ---- layout and access
    for lid, l in t["LAY"].items():
        if l["Asset"] not in t["AST"]:
            err(f"{lid}: asset unknown")
        if l["Store"] not in t["STO"]:
            err(f"{lid}: store unknown")
        for w in split_list(l["Workloads"]):
            if w not in t["WL"]:
                err(f"{lid}: workload {w} unknown")
        if l["Partition ref"] not in ("none", "n/a"):
            for p in refs(l["Partition ref"]):
                if p.startswith("PRT-") and t["PRT"][p]["Verdict"] != "Accept":
                    err(f"{lid}: partition worksheet {p} was rejected")
        if not refs(l["Assumptions"]):
            err(f"{lid}: no stated assumption")
        if not any(lid == a["Layout element"] for a in t["AP"].values()):
            err(f"{lid}: no access pattern justifies this layout element")
        if l["Retention class"] not in t["RC"]:
            err(f"{lid}: retention class unknown")
    for pid, a in t["AP"].items():
        if a["Workload"] not in t["WL"]:
            err(f"{pid}: workload unknown")
        if a["Type"] not in ("Point", "Range", "Scan", "Write"):
            err(f"{pid}: type {a['Type']!r} invalid")
        lay = t["LAY"].get(a["Layout element"])
        if lay is None:
            err(f"{pid}: layout element unknown")
            continue
        for key in split_list(a["Access key"]):
            if key != "none" and key.lower() not in lay["Keys"].lower():
                err(f"{pid}: access key {key!r} is not among the keys of {lay['ID']}")
        if a["Type"] == "Scan" and not any(
                q["Access pattern"] == pid and q["Variant"] == "Chosen" for q in t["QWK"].values()):
            err(f"{pid}: scan pattern without a chosen-layout query walk")
    prt_used = {p for l in t["LAY"].values() for p in refs(l["Partition ref"])}
    if not any(p["Verdict"] == "Reject" for p in t["PRT"].values()):
        err("no rejected partition design is documented")
    for pid, p in t["PRT"].items():
        if p["Verdict"] == "Accept" and pid not in prt_used and "not selected" not in p["Reason"]:
            err(f"{pid}: accepted worksheet is used by no layout element and is not marked 'not selected'")
        if p["Verdict"] == "Reject" and not p["Reason"]:
            err(f"{pid}: rejected without a reason")
    for qid, q in t["QWK"].items():
        if q["Variant"] not in ("Chosen", "Rejected alternative"):
            err(f"{qid}: variant {q['Variant']!r} invalid")
        if q["Variant"] == "Chosen" and q["Outcome"] != "Pass":
            err(f"{qid}: chosen layout fails its target")
        if q["Variant"] == "Rejected alternative" and q["Outcome"] != "Fail":
            err(f"{qid}: a rejected alternative should fail its target (otherwise why reject it)")

    # ---- consistency, replication, budgets
    classes = ("Strong", "Bounded staleness", "Eventual", "Snapshot")
    for oid, o in t["OPG"].items():
        if o["Class"] not in classes:
            err(f"{oid}: class {o['Class']!r} invalid")
        if o["Provided by"] not in ("System-provided", "Architecture-provided", "Assumption"):
            err(f"{oid}: provided-by {o['Provided by']!r} invalid")
        if o["Provided by"] == "Assumption" and not refs(o["Validation"]):
            err(f"{oid}: assumed guarantee without validation")
        rl = o["Replica line"]
        rule = o["Replica rule"]
        if o["Class"] == "Strong" and rule not in ("Primary only", "Sync replica only"):
            err(f"{oid}: strong guarantee with replica rule {rule!r}")
        if o["Class"] == "Snapshot" and not rule.startswith("Snapshot"):
            err(f"{oid}: snapshot guarantee needs a snapshot rule")
        if rl != "none":
            rep = t["REP"].get(rl)
            if rep is None:
                err(f"{oid}: replica line {rl} unknown")
                continue
            lag = num(rep["Lag budget s"])
            stale = num(o["Staleness budget s"])
            if o["Class"] == "Strong" and rep["Mode"] != "Sync":
                err(f"{oid}: strong guarantee relies on an asynchronous replica")
            if o["Class"] in ("Bounded staleness", "Eventual") and stale is not None and lag > stale:
                err(f"{oid}: replica lag budget {lag}s exceeds the staleness budget {stale}s")
        elif o["Class"] in ("Bounded staleness",):
            err(f"{oid}: bounded staleness needs a replica line")
    for rid, r in t["REP"].items():
        if r["Store"] not in t["STO"]:
            err(f"{rid}: store unknown")
        if r["Mode"] not in ("Sync", "Async"):
            err(f"{rid}: mode {r['Mode']!r} invalid")
        if r["Mode"] == "Sync" and num(r["Lag budget s"]) != 0:
            err(f"{rid}: synchronous replica must have a zero lag budget")
        if r["Mode"] == "Sync" and num(r["RPO s"]) != 0:
            err(f"{rid}: synchronous replica must have RPO 0")
        if r["Mode"] == "Async" and num(r["RPO s"]) < num(r["Lag budget s"]):
            err(f"{rid}: RPO is below the lag budget")
    for aid, a in t["AV"].items():
        pass
    for bid, b in t["BUD"].items():
        for c in split_list(b["Components"]):
            if c not in t["LAT"]:
                err(f"{bid}: component {c} unknown")
            elif t["LAT"][c]["Unit"] != b["Unit"]:
                err(f"{bid}: component {c} unit differs from the budget unit")
    for bid in ("BUD-01", "BUD-02"):
        if bid in t["BUD"] and t["BUD"][bid]["Verdict"] != "Pass":
            err(f"{bid}: the chosen design's budget must pass")
    for avid, a in t["AV"].items():
        if a["Verdict"] != "Pass":
            err(f"{avid}: availability budget not met")
    for tid, x in t["TXB"].items():
        if x["Provided by"] not in ("System-provided", "Architecture-provided", "Assumption"):
            err(f"{tid}: provided-by invalid")

    # ---- retention, tiers, deletion, cost
    for rcid, rc in t["RC"].items():
        if rc["Owner"] not in t["STK"]:
            err(f"{rcid}: owner {rc['Owner']} is not a stakeholder")
        if rc["Legal confirmation"] not in ("Required", "Confirmed", "Not applicable"):
            err(f"{rcid}: legal confirmation flag invalid")
        if rc["Legal confirmation"] == "Confirmed":
            err(f"{rcid}: no legal confirmation exists in this illustrative package")
        if rc["Tier plan"] not in t["TP"]:
            err(f"{rcid}: tier plan unknown")
        for a in refs(rc["Assets"]):
            if rc["ID"] not in t["AST"].get(a, {"Retention class": ""})["Retention class"]:
                err(f"{rcid}: lists {a} but the asset does not use this class")
        if "hold" not in rc["Hold approach"].lower():
            err(f"{rcid}: hold approach must mention holds")
    used_rc = {x for a in t["AST"].values() for x in split_list(a["Retention class"])}
    for rcid in t["RC"]:
        if rcid not in used_rc:
            err(f"{rcid}: used by no asset")
    for tpid, tp in t["TP"].items():
        c = t["RC"].get(tp["Class"])
        if c is None:
            err(f"{tpid}: class unknown")
            continue
        total = num(tp["Total d"])
        if c["Tier plan"] != tpid:
            err(f"{tpid}: class {c['ID']} points at {c['Tier plan']}")
        if total < num(c["Min retain d"]):
            err(f"{tpid}: tiers cover {total:.0f} days, below the minimum retention {c['Min retain d']}")
        if num(tp["Cool d"]) > 0 and num(tp["Cool d"]) < ctx.std("min_cool_days"):
            err(f"{tpid}: cool stage shorter than the minimum storage duration")
        if num(tp["Archive d"]) > 0 and num(tp["Archive d"]) < ctx.std("min_archive_days"):
            err(f"{tpid}: archive stage shorter than the minimum storage duration")
    for bid, b in t["BRK"].items():
        tp = t["TP"].get(b["Plan"])
        if tp is None:
            err(f"{bid}: plan unknown")
            continue
        stage_days = num(tp["Archive d"]) if b["To price"] == "price_archive" else num(tp["Cool d"])
        if b["Decision"] == "Keep" and stage_days > 0:
            err(f"{bid}: break-even says keep, but plan {tp['ID']} uses the cheaper tier")
        if b["Decision"].startswith("Move") and stage_days == 0:
            err(f"{bid}: break-even says move, but plan {tp['ID']} does not")
    for cid, c in t["COP"].items():
        if c["Asset"] not in t["AST"]:
            err(f"{cid}: asset unknown")
        if c["Type"] not in ("Primary", "Replica", "Snapshot", "Backup", "Derived", "Cache", "Log"):
            err(f"{cid}: type {c['Type']!r} invalid")
        if c["Beyond use"] not in ("Yes", "No"):
            err(f"{cid}: beyond-use flag invalid")
        if c["Meets SLA"] == "No":
            err(f"{cid}: copy purge ({c['Purge days']} d) exceeds the deletion SLA without a beyond-use mechanism")
    for aid, a in t["AST"].items():
        if a["Personal data"] == "None":
            continue
        types = {c["Type"] for c in t["COP"].values() if c["Asset"] == aid}
        for need_type in ("Primary", "Backup"):
            if need_type not in types:
                err(f"{aid}: no {need_type} copy row")
        lay_stores = {l["Store"] for l in t["LAY"].values() if l["Asset"] == aid}
        if any(r["Store"] in lay_stores for r in t["REP"].values()) and "Replica" not in types:
            err(f"{aid}: its store is replicated but no Replica copy row exists")
    cst_total = sum(num(c["Monthly USD"]) for c in t["CST"].values())
    caps_costed = {c["Volume source"].split(":")[1] if c["Volume source"].startswith("TIER") else c["Volume source"]
                   for c in t["CST"].values()}
    for cid in t["CAP"]:
        if cid not in caps_costed:
            err(f"{cid}: capacity row has no cost line")
    for oid, o in t["TCO"].items():
        if "Recommended" in o["Option"]:
            if abs(num(o["Storage USD/yr"]) - cst_total * 12) > 12:
                err(f"{oid}: storage {o['Storage USD/yr']} differs from 12 x the cost lines ({cst_total * 12:,.0f})")
    if sum(1 for o in t["TCO"].values()) < 3 or not any("Baseline" in o["Option"] for o in t["TCO"].values()):
        err("TCO must compare at least three options including the baseline")
    for oid, o in t["TCO"].items():
        if num(o["FTE"]) <= 0:
            err(f"{oid}: people cost missing")

    # ---- failure scenarios, risks, questions
    cats = {f["Category"] for f in t["FS"].values()}
    for need_cat in ("Replica lag", "Zone loss", "Corruption", "Deletion request"):
        if need_cat not in cats:
            err(f"failure category {need_cat!r} is not covered")
    for fid, f in t["FS"].items():
        if f["Outcome"] not in ("Pass", "Pass with residual risk", "Fail"):
            err(f"{fid}: outcome {f['Outcome']!r} invalid")
        verdicts = []
        for q in refs(f["Quantified by"]):
            kind = q.split("-")[0]
            if kind in ("BUD", "AV", "QWK", "FIL", "PRT", "BRK", "COP"):
                v = t[kind][q].get("Verdict") or t[kind][q].get("Outcome") or t[kind][q].get("Meets SLA")
                verdicts.append((q, v))
        failing = [q for q, v in verdicts if v in ("Fail", "Small files", "Reject", "No")]
        if failing and f["Outcome"] == "Pass":
            err(f"{fid}: outcome Pass although {failing} fails in the quantification")
        if f["Outcome"] != "Pass" and f["Residual risk"] in ("none", "n/a"):
            err(f"{fid}: outcome {f['Outcome']} without a stated residual risk")
        if f["Category"] == "Deletion request":
            pii = [a for a in t["AST"].values() if a["Personal data"] != "None"]
            if not any(r.startswith("COP-") for r in refs(f["Quantified by"])):
                err(f"{fid}: deletion scenario does not cite copy-location rows")
            _ = pii
    ratings = {}
    for rid, r in t["RSK"].items():
        if r["Owner"] not in t["STK"]:
            err(f"{rid}: owner {r['Owner']} is not a stakeholder")
        if r["Status"] not in ("Open", "Mitigated", "Accepted"):
            err(f"{rid}: status invalid")
        for k in ("Likelihood", "Impact"):
            v = num(r[k])
            if v is None or v != int(v) or not 1 <= v <= 5:
                err(f"{rid}: {k} must be an integer 1-5")
        if r["Rating"] == "High" and r["Status"] == "Mitigated":
            err(f"{rid}: a High-rated risk cannot be marked Mitigated without re-rating")
    for oid, o in t["OQ"].items():
        if o["Owner"] not in t["STK"]:
            err(f"{oid}: owner {o['Owner']} is not a stakeholder")
        if o["Status"] not in ("Open", "Closed"):
            err(f"{oid}: status invalid")
    for kind, minimum_ref in (("RSK", "Decision"), ("TRD", "Decision")):
        for rid, r in t[kind].items():
            if not any(x.startswith("DEC-") for x in refs(r[minimum_ref])):
                err(f"{rid}: not linked to a decision")

    # ---- ADRs
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
        if VAGUE.search(body):
            err(f"{d['ADR']}: vague wording ({VAGUE.search(body).group(0)})")
        if d["Selected"] not in body:
            err(f"{d['ADR']}: does not name the selected candidate {d['Selected']}")

    # ---- completion gate honesty and prose counts
    for vid, v in t["VAL"].items():
        if v["Status"] not in ("Met", "Partly met", "Not met"):
            err(f"{vid}: status invalid")
        if v["Status"] != "Met" and v["Reason"] in ("none", "n/a"):
            err(f"{vid}: not fully met without a reason")
        if "independent reviewer" in v["Gate item"].lower() and v["Status"] == "Met" \
                and "STK-13" not in v["Evidence in this file"]:
            err(f"{vid}: independent review marked Met without a record signed by the reviewer role (STK-13)")
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
        except (KeyError, ValueError, TypeError, ZeroDivisionError, AttributeError) as exc:
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
    print("Forward (requirement -> decision -> store -> layout -> evidence):")
    for rid in rnd.sample(reqs, min(n, len(reqs))):
        decs = [d for d in t["DEC"].values() if rid in d["Requirements"]]
        for d in decs[:1]:
            stores = [s["ID"] for s in t["STO"].values() if d["ID"] in s["Decision"]]
            lays = [l["ID"] for l in t["LAY"].values() if l["Store"] in stores]
            evid = [q["ID"] for q in t["QWK"].values() if t["AP"][q["Access pattern"]]["Layout element"] in lays]
            fs = [f["ID"] for f in t["FS"].values() if rid in f["Requirements"]]
            print(f"  {rid} -> {d['ID']} -> {','.join(stores)} -> {','.join(lays[:3])} -> {','.join(evid[:2] + fs[:2]) or 'no walk'}")
    print("Backward (decision -> requirements and workloads):")
    for did in rnd.sample(sorted(t["DEC"]), min(n, len(t["DEC"]))):
        d = t["DEC"][did]
        print(f"  {did} <- {d['Requirements']} <- {d['Workloads']}")
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
