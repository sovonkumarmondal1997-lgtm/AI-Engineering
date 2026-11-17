# Stage 2D Capstone Project — Enterprise Data Architecture Package (Integration)

> **Programme:** Applied AI Engineering Roadmap → Stage 2D — Data Architecture → Stage Overview → Stage Project  
> **Target repository path:** `Stage 2D — Data Architecture/00-Stage-2D-Overview/Projects/01-enterprise-data-architecture-capstone.md`  
> **Project type:** Integrated architecture consolidation, reconciliation, validation, audit, and defense; design-only, no deployment  
> **Level:** Advanced (assumes the module projects were completed)  
> **Recommended effort:** 40–50 focused hours (a 45.5-hour plan is given in Section 3.1); adjust to experience  
> **Status:** Complete proposed project specification. Not an official brief or rubric.

---

## Document control

| Field | Value |
|---|---|
| Document ID | 2D.0-P01 |
| Version | 2.0 — remediated after an independent audit of v1 (audit and re-audit results in Appendix F) |
| Date | 2026-10-22 |
| Audience | Learners finishing Stage 2D, reviewers, mentors |
| Scenario | Fictional Northbridge Bank; every fact, number, and target is illustrative |
| Companion tool | Appendix B (`arch_package_check.py`); structural checker only |
| Approval | No stakeholder, legal, security, or architecture-board approval is implied |

---

## 0. Orientation

### 0.1 What this project is about

Stage 2D taught sixteen subjects, from foundations to documentation and operating models. Each module project produced a deliverable about one slice of the architecture. In real organisations, slices rarely fit together on the first attempt: requirement IDs differ, retention periods contradict each other, a recovery target assumes storage behaviour that the storage design does not provide, and a latency budget ignores the serving layer.

This capstone is the **integration project**. You will consolidate your fifteen module-project deliverables into a single, internally consistent **Enterprise Data Architecture Package** for Northbridge Bank. You will find and resolve cross-module conflicts, trace every important requirement to decisions, designs, controls, and tests, run a structural consistency check, audit the package as an independent reviewer would, remediate the findings, and defend the result.

The deliverable is not a new design from scratch. It is the **architecture of record**: the single, reviewed, traceable description of what the organisation intends to build and why, and an honest list of what is not yet proven.

### 0.2 How this project relates to the module projects

| Project | Role in this capstone |
|---|---|
| P01 Current-state inventory | Input to the current-state baseline (Step 5) |
| P02 Requirements and decision pack | Seed of the master requirements register and ADR log (Steps 4, 11) |
| P03 Reference architecture pattern comparison | Input to pattern selection and target architecture (Steps 7, 11) |
| P04 Conceptual and logical data model | Input to domain, model, and key decisions (Step 6) |
| P05 Storage technology selection | Input to storage placement and replication assumptions (Steps 7, 9) |
| P06 Cross-system integration design | Input to contracts, flows, and coexistence (Steps 6, 7, 12) |
| P07 Enterprise lakehouse reference architecture | Core platform view (Step 7) |
| P08 Cloud platform comparison | Input to cloud placement (Step 10) |
| P09 Real-time risk monitoring | Streaming path and latency budget (Steps 7, 9) |
| P10 Sensitive data governance and access | Control architecture (Step 8) |
| P11 Metadata and lineage design | Metadata, lineage, quality, and master data (Step 8) |
| P12 Disaster recovery and resilience | Recovery tiers and objectives (Step 9) |
| P13 Capacity, cost, and performance | Capacity and cost envelope (Step 9) |
| P14 Analytics and AI data serving | Serving and AI access (Steps 7, 8) |
| P15 Current-to-target architecture review | Review method, operating model, roadmap (Step 12) |
| P16 Module capstone (Northbridge Financial Group) | Peer reference. It is a design-from-brief exercise for module 16. Reuse its templates and review method, not its scenario facts. |

If you did not complete a module project, create a minimal stand-in and label it `NOT VALIDATED`. Do not silently skip the dependency.

### 0.3 Source-of-truth rule

The module projects are your primary inputs. Their content is **SOURCE-DERIVED** when you reuse it. The scenario in Section 1 is an **ILLUSTRATIVE ASSUMPTION** shared with the module projects. If an approved brief, a mentor, or an official rubric conflicts with this document, that controlling source wins. Record the conflict in the reconciliation log (D16).

### 0.4 Evidence labels

Apply exactly one label to every requirement, decision rationale, test result, and claim of readiness.

| Label | Meaning | Required handling |
|---|---|---|
| **SOURCE-DERIVED** | Taken from a module project or lesson | Cite file and section |
| **CONFIRMED FACT** | Provided by an accountable owner in a real engagement | Record source, owner, date |
| **ILLUSTRATIVE ASSUMPTION** | Invented for the exercise | Never present as a real requirement; record impact if wrong |
| **PROPOSED REQUIREMENT** | Candidate requirement awaiting approval | Owner and acceptance method |
| **HYPOTHESIS** | Plausible but unproven | Test or keep visibly unresolved |
| **RECOMMENDATION** | Suggested practice | Compare against alternatives |
| **OPEN QUESTION** | Missing information that could change the design | Owner, due point, consequence |
| **VALIDATED** | Supported by completed evidence | Link evidence; state scope and limits |
| **NOT VALIDATED** | Described or planned without evidence | Never claim compliance or readiness |

A diagram shows that a view was documented, not that the system exists. A test plan shows intent, not success. A design-only project cannot claim operational readiness.

### 0.5 Expected outcomes

When complete you can:

1. Run an integration effort across many architecture artifacts and keep a single source of truth.
2. Detect and resolve cross-domain conflicts using explicit tests and recorded decisions.
3. Build and verify an end-to-end traceability chain from requirement to decision, view or control, test, and evidence.
4. Reconcile resilience, performance, privacy, and cost targets that pull in different directions.
5. Present trade-offs honestly to technical and executive audiences, including what is not proven.
6. Audit your own package against a rubric and remediate findings with evidence.

### 0.6 Definition of done

The project is done when all of the following hold. Each item maps to a deliverable in Section 2.

- [ ] Deliverables D01–D23 exist, are versioned, and carry owner, date, and status.
- [ ] The reconciliation log (D16) lists every conflict from Section 4 that applies, each with a resolution or an explicit accepted risk.
- [ ] The checker (Appendix B) runs against your registers with **zero ERROR findings**; every remaining WARN has a written justification.
- [ ] Every MUST requirement traces to a live decision, a view or control, and a test.
- [ ] No claim is labelled VALIDATED without linked evidence.
- [ ] The independent audit (Step 14) has no open Severity 1 finding and no open Severity 2 finding without an approved, time-boxed exception.
- [ ] The defense record (D22) exists with outcome and conditions.
- [ ] A handover pack (D23) lists what is proven, what is not, and what to do next.

---

## 1. Scenario: Northbridge Bank

**Status: ILLUSTRATIVE ASSUMPTION.** Northbridge Bank is a fictional mid-sized retail and business bank. Nothing here describes a real bank, regulator, vendor, or price. Where your module projects use different numbers, **your module numbers win**; record the difference in D16 rather than editing history.

### 1.1 Business context

Northbridge has grown by acquisition. It operates retail banking, business banking, lending, cards and payments, and risk and finance functions. Reporting is slow and contested, customer identity is inconsistent across products, risk signals arrive late, and the analytics estate is a mix of an ageing warehouse and newer lakehouse components. Leadership wants a trusted, governed, resilient data foundation and a cautious path to modernisation.

### 1.2 Business outcomes

| ID | Outcome | Evidence of success (to be defined in Step 4) |
|---|---|---|
| BO-01 | Trusted, reconciled enterprise reporting | Reconciliation to ledger within agreed tolerance; lineage for regulated reports |
| BO-02 | One governed customer identity view | Duplicate rate and conflict rate trend; steward-reviewed merges |
| BO-03 | Timely, correct risk signals | Agreed latency objective measured end to end; decision audit |
| BO-04 | Safe modernisation of the analytics estate | Wave plan, parallel-run reconciliation, tested rollback |
| BO-05 | Defensible cloud and cost posture | Cost model with sensitivity; recovery exercise; portability evidence |
| BO-06 | Governed analytics and AI access | Permission-aware serving; revocation and deletion evidence |
| BO-07 | Clear ownership and sustainable operations | RACI, service contracts, runbooks, on-call design |

### 1.3 Domains and platform shape

Use the six-domain split from your module projects (retail, business, lending, cards and payments, risk, finance) unless yours differs. Roughly twenty-five delivery teams share a central platform team. These are **assumptions**; reconcile the domain IDs with your P01 inventory in D03.

### 1.4 Recovery tiers (assumption carried from the disaster recovery module)

| Tier | Typical services | RTO | RPO |
|---|---|---|---|
| 1 | Risk alerting, event backbone, identity service | ≤ 2 h | ≤ 15 min |
| 2 | Core lakehouse, regulatory reporting | ≤ 8 h | ≤ 1 h |
| 3 | Sandbox, experimentation | ≤ 72 h | ≤ 24 h |

Your P12 numbers replace these if they differ. Appendix B encodes a dependency rule on top of whichever tiers you adopt.

### 1.5 In scope and out of scope

**In scope:** consolidation of module deliverables; reconciliation; a single target-state description; traceability; validation planning; audit; defense; handover.

**Out of scope:** deploying infrastructure; selecting vendors as a commercial exercise; legal advice; detailed physical schemas beyond what the modules produced; performance benchmarks you did not measure.

### 1.6 Stakeholders and decision rights

| Role | Concern | Decision right in this project |
|---|---|---|
| Executive sponsor (Head of Data) | Outcomes, funding, risk appetite | Approves scope and accepts residual risk |
| Chief Risk Officer delegate | Timeliness and correctness of risk signals | Approves risk-related requirements |
| CISO delegate | Access, encryption, threat posture | Approves control architecture |
| Privacy / DPO delegate | Lawful use, retention, erasure | Approves privacy design |
| Finance partner | Cost envelope, ledger reconciliation | Approves cost model and finance requirements |
| Platform lead | Feasibility, operability | Approves platform decisions |
| Domain owners | Meaning, quality, product contracts | Approve data-product contracts |
| SRE lead | Reliability, on-call load | Approves recovery and operational readiness |
| Enterprise architect (you) | Coherence, traceability | Owns the package; cannot approve other owners' requirements |

In a solo exercise, role-play each stakeholder explicitly in a stakeholder-concern table and mark approvals as **simulated**.

---

## 2. Deliverables and workspace

### 2.1 Deliverable catalogue

| ID | Deliverable | Produced in step | Primary sources |
|---|---|---|---|
| D01 | Charter and authority record | 1 | Brief; Section 1 |
| D02 | Input artifact register and freshness log | 2 | P01–P16 |
| D03 | Canonical glossary, ID scheme, and crosswalk | 3 | All |
| D04 | Master requirements and quality-attribute register | 4 | P02, P07, P09, P12, P13 |
| D05 | Consolidated current-state baseline | 5 | P01, P15 |
| D06 | Domain, data-product, model, and contract catalogue | 6 | P03, P04, P06, P14 |
| D07 | Integrated architecture description (views) | 7 | P03, P05, P06, P07, P09, P14 |
| D08 | Governance, security, and privacy control architecture | 8 | P10, P14 |
| D09 | Metadata, lineage, quality, and master-data architecture | 8 | P11 |
| D10 | Resilience, performance, capacity, and cost envelope | 9 | P05, P09, P12, P13 |
| D11 | Cloud and hybrid placement decision | 10 | P08, P10, P13 |
| D12 | ADR log and option-evaluation workbook | 11 | P02, P03, P15 |
| D13 | Risk, threat, and assumption registers | 12 | P10, P12, P15 |
| D14 | Operating model and service ownership | 12 | P07, P12, P15 |
| D15 | Migration and coexistence roadmap | 12 | P06, P15 |
| D16 | Reconciliation log | 3–11 (living) | Section 4 |
| D17 | Traceability registers and checker report | 13 | Appendix B |
| D18 | Validation plan and evidence pack | 13 | Section 8 |
| D19 | Independent audit report | 14 | Section 9 |
| D20 | Remediation log and revalidation record | 14 | D19 |
| D21 | Executive brief and technical summary | 15 | All |
| D22 | Defense record | 15 | Section 9.4 |
| D23 | Handover pack and retrospective | 16 | All |

### 2.2 Recommended workspace structure

Create this in your own working repository (not inside the course tree).

```text
northbridge-eda-package/
├── README.md                          # package index, version, status, how to read
├── 00-governance/
│   ├── D01-charter-and-authority.md
│   └── D02-input-artifact-register.md
├── 01-language/
│   ├── D03-glossary-id-scheme-crosswalk.md
│   └── D16-reconciliation-log.md
├── 02-requirements/
│   └── D04-master-requirements-and-quality-attributes.md
├── 03-baseline/
│   └── D05-current-state-baseline.md
├── 04-domain-model/
│   └── D06-domains-products-models-contracts.md
├── 05-architecture/
│   ├── D07-architecture-description.md
│   ├── D08-governance-security-privacy.md
│   ├── D09-metadata-lineage-quality-mdm.md
│   ├── D10-resilience-performance-capacity-cost.md
│   └── D11-cloud-placement.md
├── 06-decisions/
│   └── D12-adr-log/
│       ├── ADR-001-....md
│       └── option-evaluation.xlsx-or-csv
├── 07-risk-ops-migration/
│   ├── D13-risk-threat-assumption-registers.md
│   ├── D14-operating-model.md
│   └── D15-migration-roadmap.md
├── 08-verification/
│   ├── D17-traceability-and-checker-report.md
│   ├── D18-validation-plan-and-evidence.md
│   ├── D19-audit-report.md
│   └── D20-remediation-log.md
├── 09-communication/
│   ├── D21-executive-brief.md
│   ├── D22-defense-record.md
│   └── D23-handover-and-retrospective.md
├── registers/                          # machine-checkable CSVs (Appendix A)
│   ├── requirements.csv
│   ├── decisions.csv
│   ├── views.csv
│   ├── controls.csv
│   ├── tests.csv
│   ├── risks.csv
│   ├── tiers.csv
│   └── dependencies.csv
├── tools/
│   └── arch_package_check.py          # Appendix B
└── inputs/                             # read-only copies or links to P01–P16 outputs
```

Rules: one owner and one status per file; every file starts with a header block (ID, version, date, owner, status, sources); diagrams are text or exported images stored beside the file that references them; the `registers/` CSVs are the machine-readable source for IDs and links, and the Markdown files explain them.

---

## 3. Execution plan: initiation to closure

### 3.1 Effort plan

| Step | Name | Hours |
|---|---|---|
| 1 | Initiate and establish authority | 1.5 |
| 2 | Intake and inventory of module deliverables | 3.0 |
| 3 | Establish canonical language | 2.5 |
| 4 | Consolidate requirements | 3.5 |
| 5 | Consolidate the current-state baseline | 2.5 |
| 6 | Consolidate domains, models, and contracts | 3.5 |
| 7 | Integrate the target architecture views | 4.0 |
| 8 | Integrate cross-cutting control architecture | 3.5 |
| 9 | Reconcile resilience, performance, capacity, and cost | 3.5 |
| 10 | Decide cloud and hybrid placement | 2.0 |
| 11 | Consolidate decisions and evaluate options | 3.0 |
| 12 | Risk, threat, operating model, and migration | 4.0 |
| 13 | Traceability, automated checks, and validation planning | 3.0 |
| 14 | Independent audit and remediation | 2.5 |
| 15 | Communicate and defend | 2.5 |
| 16 | Close and hand over | 1.0 |
| | **Total** | **45.5** |

### 3.2 Dependency flow

```text
1 Initiate ─► 2 Intake ─► 3 Language ─► 4 Requirements ─► 5 Baseline
                                              │                │
                                              ▼                ▼
                                       6 Domains/models ─► 7 Target views
                                                              │
                         ┌────────────────────┬───────────────┼───────────────┐
                         ▼                    ▼               ▼               ▼
                   8 Controls          9 Resilience/    10 Cloud       11 Decisions
                                       cost envelope    placement
                         └────────────────────┴───────┬───────┴───────────────┘
                                                      ▼
                                   12 Risk, operating model, migration
                                                      ▼
                                   13 Traceability, checks, validation
                                                      ▼
                                   14 Audit and remediation
                                                      ▼
                                   15 Communicate and defend ─► 16 Close
```

Steps 8, 9, and 10 can be worked in parallel by a team. Step 11 can start collecting existing ADRs in parallel, but it closes only after Steps 8 to 10 have raised their decisions. Solo learners should follow the numeric order, because each step feeds the reconciliation log.

### Step 1 — Initiate and establish authority

**Purpose:** Fix scope, authority, and acceptance before touching content.

**Inputs:** Section 1; this document.

**Tasks**
1. Write the charter: purpose, outcomes (BO-01–BO-07), scope, exclusions, assumptions, success criteria, and the Definition of Done from Section 0.6.
2. Record sources of authority and the precedence rule from Section 0.3.
3. Create the stakeholder-concern table with decision rights from Section 1.6; mark every approval **simulated** if you are working alone.
4. Create the workspace from Section 2.2 and initialise version control.
5. Define status vocabulary: `DRAFT`, `IN REVIEW`, `APPROVED (simulated)`, `SUPERSEDED`.
6. Define change control: who may change what, and how changes are logged.

**Output D01.**

**Completion gate:** A reviewer can read D01 and state what is in scope, who decides, and when the work is complete, without asking you.

**Common failures:** Treating "design everything" as scope; omitting exclusions; leaving approval authority implicit.

### Step 2 — Intake and inventory of module deliverables

**Purpose:** Know exactly what you are integrating and how reliable each input is.

**Inputs:** Your P01–P16 deliverables.

**Tasks**
1. List every input artifact: project number, file, version, date, completeness (complete, partial, stand-in), and its internal ID scheme (for example `DOM-xx`, `RQ-xx`, `ADR-xx`).
2. For each input, extract the **claims that other modules depend on**: targets, retention periods, key choices, recovery tiers, latency budgets, volumes, region choices.
3. Record freshness: has a later module changed an assumption that an earlier module used?
4. Mark gaps. A missing module project becomes a stand-in labelled `NOT VALIDATED`.
5. Copy or link inputs read-only into `inputs/`.

**Output D02.**

**Completion gate:** Every one of P01–P16 appears in D02 with completeness, ID scheme, and at least three cross-module claims (or a note that none exist).

**Common failures:** Assuming modules agree; ignoring partial deliverables; losing version information.

### Step 3 — Establish canonical language

**Purpose:** Remove naming and ID collisions before any merge.

**Tasks**
1. Build the glossary: customer, party, account, product, exposure, event, data product, domain, tier, retention, erasure, golden record, and any term used inconsistently across modules.
2. For each term record the **meaning used by each module** and select one canonical meaning, with the rationale.
3. Define the package ID scheme (Section 5.1) and a crosswalk from each module's IDs to package IDs.
4. Start D16 (reconciliation log) and add every conflict found so far, using the template in Section 4.2.
5. Define the evidence-label vocabulary (Section 0.4) as mandatory.

**Output D03; D16 started.**

**Completion gate:** No term in D03 has two meanings; every legacy ID maps to exactly one package ID or is explicitly retired.

**Common failures:** Merging before agreeing on terms; creating a glossary of definitions copied from textbooks rather than reconciled usage.

### Step 4 — Consolidate requirements

**Purpose:** Produce one master requirements register that every later artifact traces to.

**Tasks**
1. Collect requirements and quality-attribute statements from P02, P07, P09, P10, P11, P12, P13, and P14.
2. Normalise each to a testable statement with measure, threshold, scope, and measurement method. Convert vague terms ("fast", "secure") into quality-attribute scenarios (Section 5.4).
3. Deduplicate. Where two modules state different thresholds for the same property, do not choose silently: log a conflict in D16 and choose by the method in Section 4.3.
4. Assign priority (MUST, SHOULD, COULD), owner, label, and source.
5. Identify requirements that conflict *by nature* (low latency vs. low cost; erasure vs. immutability) and flag them for Step 9 and Step 11.
6. Link every requirement to at least one business outcome (BO-01 to BO-07 from Section 1.2). Load the outcomes that apply into `registers/outcomes.csv`, and every requirement into `registers/requirements.csv` (Appendix A).

**Output D04; `outcomes.csv`; `requirements.csv`.**

**Completion gate:** Each MUST requirement has an owner, a business outcome, a measurable acceptance method, and a label. No two requirements state the same property with different thresholds unless a conflict is logged.

**Common failures:** Silent choice of one module's number; unowned requirements; requirements that cannot be tested.

### Step 5 — Consolidate the current-state baseline

**Purpose:** Establish what exists, separating observed fact from claim.

**Tasks**
1. Merge P01's inventory and P15's current-state findings into one baseline: systems, data stores, flows, owners, volumes, quality issues, controls.
2. Classify each statement as **observed**, **reported**, or **assumed**. Link to evidence.
3. Mark where modules disagree about current state (for example a store listed in P01 but absent in P15).
4. Identify the pain points that map to BO-01 through BO-07.
5. State the baseline's limits. Name what you could not observe.

**Output D05.**

**Completion gate:** Every system in the baseline has an owner, a classification, and an evidence reference, and every pain point links to at least one outcome.

**Common failures:** Treating documentation as observation; omitting shadow systems; mixing target-state intent into the baseline.

### Step 6 — Consolidate domains, models, and contracts

**Purpose:** Align business meaning, data products, entity models, and interface contracts.

**Tasks**
1. Reconcile the domain list, capability map, and data-product catalogue (P01, P03, P07, P14).
2. Reconcile the conceptual and logical model (P04) with data-product boundaries and contracts (P06, P07, P14).
3. Reconcile keys: business keys, surrogate keys, customer identity keys, and survivorship rules (P04, P06, P11).
4. For each data product record owner, contract version, schema, freshness, quality rules, classification, retention, and consumers.
5. Check that every contract field maps to a logical-model attribute, or is recorded as a deliberate exception.
6. Log every disagreement in D16.

**Output D06.**

**Completion gate:** Each data product has exactly one owner, one contract, one classification, and one retention rule; each entity has one canonical key strategy.

**Common failures:** Two modules using different keys for the same entity; contracts that ignore classification; unowned products.

### Step 7 — Integrate the target architecture views

**Purpose:** Produce one coherent description of the target state, with views for different concerns.

**Tasks**
1. Choose the architecture description approach (for example ISO/IEC/IEEE 42010-style viewpoints with C4-style diagrams). Record the choice.
2. Produce at minimum: system context; container/zone view (sources, ingestion, event backbone, lakehouse zones, serving, governance plane, operations plane); data-flow and trust-boundary view; deployment and recovery view; and an end-to-end flow catalogue.
3. For each of the five workload patterns (batch analytics, customer identity, real-time risk, serving and semantic access, optional governed AI retrieval) show which components they use and which they do *not* share, with a reason.
4. Show the interface between every pair of adjacent components (protocol, contract, direction, owner, failure behaviour).
5. Label each view with the requirements it realises (`registers/views.csv`).
6. Mark every unvalidated assumption on the diagram.

**Output D07; `views.csv`.**

**Completion gate:** Every MUST requirement is realised by at least one view or control; each diagram element has an owner; each trust boundary has a named control.

**Common failures:** One diagram that mixes logical and deployment concerns; hidden shared dependencies; no failure behaviour at interfaces.

### Step 8 — Integrate cross-cutting control architecture

**Purpose:** Make governance, security, privacy, metadata, lineage, quality, and master data one coherent plane rather than module-by-module add-ons.

**Tasks**
1. Merge classification, access, masking, encryption, key management, and audit design (P10, P14) into a single control architecture. Define the policy decision and enforcement points and where each applies (ingestion, storage, query, API, semantic layer, retrieval).
2. Reconcile privacy lifecycle: retention, legal hold, erasure, and consent against storage features that keep history (time travel, snapshots, backups, replay logs, lineage and audit stores). This is conflict RC-05 (Section 4.1) and has a worked example in Section 6.
3. Merge metadata, lineage, quality, and master-data design (P11) with ingestion, streaming, and promotion gates (P06, P07, P09).
4. Define lineage coverage targets by data class and flow type, including streaming and CDC.
5. Register each control in `registers/controls.csv` with the requirements it satisfies.

**Outputs D08, D09; `controls.csv`.**

**Completion gate:** Every classification level has an access, masking, encryption, retention, and erasure rule; every regulated report has lineage; the erasure approach covers every store that retains personal data.

**Common failures:** Access control defined for tables but not for APIs, semantic layers, or retrieval indexes; erasure that ignores backups and replay logs; lineage that stops at the streaming boundary.

### Step 9 — Reconcile resilience, performance, capacity, and cost

**Purpose:** Prove that targets are mutually achievable, or document the trade-off.

**Tasks**
1. Take recovery tiers (P12) and map each service to a tier. Record service dependencies in `tiers.csv` and `dependencies.csv`.
2. Check the dependency rule: a service must not depend on something that recovers later or may lose more data than the service itself tolerates. Resolve violations by raising the dependency's tier, adding a fallback, or relaxing the consumer's target with owner agreement.
3. Check replication and consistency assumptions from storage design (P05) against RPO, and replay retention from streaming (P09) against RPO and RTO.
4. Reconcile latency budget (P09) with the serving path (P14). Remember that component percentiles do not add; require direct end-to-end measurement.
5. Reconcile capacity and cost (P13) with tiers, retention, replication, and double-running during migration (Step 12). Build low, expected, and high scenarios. Show sensitivity to the two largest cost drivers.
6. State which targets are *unproven* and what measurement would prove them.

**Output D10.**

**Completion gate:** `tiers.csv` and `dependencies.csv` pass the checker; each target has a stated validation method; the cost envelope states assumptions and sensitivity.

**Common failures:** Tier 1 service depending on a Tier 3 store; summing percentiles; forgetting retention-driven storage growth and replication multipliers; omitting migration double-running cost.

### Step 10 — Decide cloud and hybrid placement

**Purpose:** Decide where each workload runs and why, using evidence rather than preference.

**Tasks**
1. Take the comparison (P08) and the constraints from governance (P10: residency, key custody) and cost (P13: egress, committed use).
2. For each workload decide: single cloud, hybrid, or multi-cloud, and for what reason (resilience, locality, regulatory, negotiating position, capability). Reject multi-cloud where the reason is only "avoid lock-in" without a tested exit plan.
3. Record portability evidence you actually have versus what you assume.
4. Record the failure behaviour if a region or provider is unavailable, consistent with Step 9.

**Output D11.**

**Completion gate:** Every workload has a placement, a reason, a residency check, a cost check, and a recovery check.

**Common failures:** Treating portability as free; ignoring egress; choosing multi-cloud without an operating model for it.

### Step 11 — Consolidate decisions and evaluate options

**Purpose:** Make the reasoning behind the architecture explicit, comparable, and revisable.

**Tasks**
1. Collect ADRs from P02, P03, P15, and new decisions raised by the reconciliation log. Renumber to package IDs.
2. For each significant decision, evaluate at least two real alternatives against weighted criteria (Section 7). Run sensitivity analysis on the weights.
3. Record consequences, risks, validation plan, and revisit triggers (template in Appendix C).
4. Mark superseded decisions and link replacements.
5. Write each decision to `registers/decisions.csv`, listing the requirements that drive it.

**Output D12; `decisions.csv`.**

**Completion gate:** Every decision has at least one driving requirement, a recorded alternative, a consequence, and a revisit trigger; no accepted decision contradicts another.

**Common failures:** Decisions recorded after the fact without alternatives; scores without sensitivity; decisions that contradict each other across modules.

### Step 12 — Risk, threat, operating model, and migration

**Purpose:** Make the architecture operable and deliverable.

**Tasks**
1. Merge risk and threat registers (P10, P12, P15). Threat-model the integrated flows, especially trust-boundary crossings and shared services such as identity and the policy plane.
2. Build the assumption register: every ILLUSTRATIVE ASSUMPTION or HYPOTHESIS that a decision depends on, with impact if wrong and validation path.
3. Define the operating model: platform versus domain responsibilities, service ownership, on-call, change control, data-product lifecycle, and platform support (P07, P12, P15).
4. Build the migration and coexistence roadmap in waves. For each wave define scope, entry and exit criteria, parallel-run reconciliation, rollback, consumer communication, and the interaction with DR coverage and cost while old and new run together.
5. Cross-check: every decision that creates a new service has an owner in the operating model; every wave has rollback.

**Outputs D13, D14, D15; `risks.csv`.**

**Completion gate:** Each risk has an owner and a response; each assumption has a validation path; every service has an owner and an on-call route; every wave has rollback and exit evidence.

**Common failures:** Risks without owners; a migration plan with no DR coverage during coexistence; platform services nobody operates.

### Step 13 — Traceability, automated checks, and validation planning

**Purpose:** Prove the package is internally consistent and plan how the unproven parts will be validated.

**Tasks**
1. Complete the registers in `registers/` (Appendix A).
2. Run the checker (Appendix B). Fix every ERROR. Write a justification for every WARN you keep.
3. Define fitness functions (Section 8.2) for properties that can be checked repeatedly.
4. Build the scenario-based test catalogue (Section 8.3) and the evidence matrix. Each test names what it would prove, who runs it, and what artifact is the evidence.
5. Run the tests that are possible in a design-only exercise (walkthroughs, tabletop exercises, calculation re-derivations) and record the evidence; keep the rest `PLANNED` and `NOT VALIDATED`.

**Outputs D17, D18.**

**Completion gate:** Checker exits 0; evidence references resolve to real files; no VALIDATED label lacks evidence.

**Common failures:** Treating a clean checker as approval; tests with no pass criteria; evidence that is a screenshot of a plan.

### Step 14 — Independent audit and remediation

**Purpose:** Find what you missed by changing perspective.

**Tasks**
1. Audit the package as if you had not written it. Use the rubric in Section 9.2 and the layered review in Section 9.1. If working with a peer, swap packages.
2. Record each finding with ID, severity (Section 9.3), location, evidence, and recommended fix in D19.
3. Remediate: fix, accept with approval and expiry, or reject with reasoning. Log in D20.
4. Re-run the checker and re-audit the changed areas. Do not close a finding without evidence of the fix.

**Outputs D19, D20.**

**Completion gate:** No open Severity 1; every Severity 2 is fixed or has an approved time-boxed exception; the re-run shows no new ERRORs.

**Common failures:** Auditing only formatting; closing findings by editing the finding; skipping revalidation.

### Step 15 — Communicate and defend

**Purpose:** Convey the recommendation and its limits to different audiences.

**Tasks**
1. Write the executive brief (two pages): outcome, recommendation, cost range with assumptions, top risks, what is proven and what is not, decisions needed.
2. Write the technical summary: views, key decisions, reconciliations, validation status.
3. Prepare answers to the review questions in Section 9.4 for each reviewer role.
4. Conduct the defense (with a mentor or in a recorded self-defense), and record outcome and conditions in D22.

**Outputs D21, D22.**

**Completion gate:** The brief states at least three things that are not yet proven; defense questions were answered with references to evidence.

**Common failures:** Overclaiming; hiding trade-offs; answering with tool names instead of reasoning.

### Step 16 — Close and hand over

**Purpose:** Leave a package someone else can use.

**Tasks**
1. Freeze the package at a version. Tag the repository.
2. Write the handover: what is proven; what is not; open questions; next three actions; owners; revisit dates for assumptions.
3. Run a short retrospective: which reconciliations were hardest, which module projects needed rework, what you would change in your own earlier deliverables.
4. Update D02 to show the final state of each input.

**Output D23.**

**Completion gate:** A newcomer can find the answer to "what do we believe, why, and how sure are we?" for any MUST requirement in under ten minutes.

---

## 4. Reconciliation catalogue

### 4.1 Known tension points

These are the conflicts most likely to appear when independently produced module deliverables are merged. Treat the list as a prompt, not a ceiling.

| ID | Tension | Modules involved | Conflict test | Resolution method |
|---|---|---|---|---|
| RC-01 | Requirement IDs, wording, and thresholds differ | P02, P07, P09, P12 | Same property, different threshold or ID | Single master register; Section 4.3 |
| RC-02 | Domain, entity, and product naming differ | P01, P03, P04, P14 | Same concept, different names; or same name, different meaning | Glossary and crosswalk (D03) |
| RC-03 | Customer identity keys and survivorship | P04, P06, P10, P11 | Different key for the same party; merge rules not matching privacy rules | One key strategy; steward-owned survivorship; audit of merges |
| RC-04 | Latency objective versus serving path and cost | P09, P13, P14 | Budget stages omit serving; percentiles summed | Direct end-to-end measurement plan; cost of low-latency path justified |
| RC-05 | Retention and erasure versus history-keeping storage | P07, P10, P11, P12 | Personal data persists in time travel, snapshots, backups, replay logs, lineage, or indexes after erasure | Worked example in Section 6 |
| RC-06 | Recovery tiers versus replication, lag, and replay | P05, P08, P09, P12 | Service RPO smaller than replication lag or replay retention | Dependency rule; adjust design or target with owner |
| RC-07 | Cloud placement versus residency and egress | P08, P10, P13 | Data or keys outside allowed region; egress unpriced | Placement table with residency and cost checks |
| RC-08 | Data contracts versus products and semantic layer | P03, P06, P07, P14 | Contract field absent from model; semantic metric defined twice | Contract-to-model mapping; single metric owner |
| RC-09 | Quality rules versus streaming validation and promotion gates | P07, P09, P11 | Same rule in two places with different thresholds | One rule catalogue; stated enforcement points |
| RC-10 | Access model versus APIs, semantic layer, and retrieval | P10, P14 | Policy enforced on tables but not on derived indexes or caches | Enforcement-point matrix |
| RC-11 | Lineage coverage versus streaming, CDC, and AI context | P06, P09, P11, P14 | Lineage stops at the event backbone or at the retrieval index | Coverage target by flow type |
| RC-12 | Ownership and on-call versus platform and domain split | P07, P12, P15 | Service with no operator, or two operators | Service-ownership table |
| RC-13 | Migration waves versus coexistence, DR, and double-running cost | P06, P12, P13, P15 | Old and new run together without DR cover or cost | Wave-level DR and cost row |
| RC-14 | Volume and growth assumptions differ | P05, P09, P13 | Different volumes used for storage, streaming, and cost | One volume baseline with scenarios |
| RC-15 | Pattern choice versus final platform commitment | P03, P07 | Pattern comparison chose one option; platform view implies another | Explicit ADR linking the two |
| RC-16 | Logical keys and partitioning versus performance | P04, P05, P13 | Key or partition choice conflicts with access pattern or skew | Access-pattern table and capacity check |

### 4.2 Reconciliation log template (D16)

| Field | Content |
|---|---|
| ID | `RC-NN` for catalogue items; `RX-NN` for new items found in your package |
| Tension | One sentence |
| Sources | Module projects and sections that disagree, with the exact conflicting values |
| Conflict test | The check that detects the conflict |
| Options | At least two resolutions |
| Chosen resolution | And the criterion used (Section 4.3) |
| Affected artifacts | Requirements, decisions, views, controls, tests |
| Approver (simulated if solo) | Role |
| Evidence | Link |
| Status | `OPEN`, `RESOLVED`, `ACCEPTED RISK`, `DEFERRED` |
| Revisit trigger | Condition for reopening |

### 4.3 How to choose between conflicting values

Apply in order and stop at the first rule that decides:

1. **Controlling source.** An approved brief or an accountable owner's confirmation beats any module assumption.
2. **Safety direction.** For recovery, security, and privacy, prefer the more protective value unless an owner accepts the cost in writing.
3. **Downstream dependence.** If other artifacts depend on one value, prefer it unless it is demonstrably infeasible.
4. **Evidence.** Prefer a value backed by calculation or measurement over an unlabelled assumption.
5. **Recency with traceability.** Prefer the later module only if it records why it changed the earlier value.
6. **Escalate.** If none decides, log as `OPEN` with owner and consequence; do not choose silently.

---

## 5. Models, identifiers, and traceability

### 5.1 Package ID scheme

| Prefix | Meaning | Format | Example |
|---|---|---|---|
| `RQ` | Requirement | `RQ-NNN` | `RQ-014` |
| `ADR` | Architecture decision | `ADR-NNN` | `ADR-003` |
| `VW` | Architecture view | `VW-NN` or `VW-NNN` | `VW-04` |
| `CT` | Control | `CT-NNN` | `CT-021` |
| `TS` | Test or validation | `TS-NNN` | `TS-009` |
| `SC` | Validation scenario (Section 8.3); each is implemented by one or more `TS` | `SC-NN` | `SC-05` |
| `RK` | Risk | `RK-NNN` | `RK-012` |
| `RC`/`RX` | Reconciliation item | `RC-NN`/`RX-NN` | `RC-05` |
| `D` | Deliverable | `DNN` | `D17` |
| `EV` | Evidence item | `EV-YYYY-NNN` | `EV-2026-004` |

IDs never change meaning and are never reused. Retired IDs stay in the crosswalk as `RETIRED`.

### 5.2 Traceability chain

```text
Business outcome (BO) ─► Requirement (RQ) ─► Decision (ADR) ─► View (VW) or Control (CT)
                                                    │                         │
                                                    └──────► Test (TS) ◄──────┘
                                                                 │
                                                                 ▼
                                                           Evidence (EV)
```

Rules enforced by Appendix B:

- Every requirement names a business outcome that exists; every outcome should be served by at least one MUST requirement (a WARN, to be justified if kept).
- Every MUST requirement has a live decision, a view or control, and a test that has not FAILED.
- Every non-rejected decision has at least one driving requirement.
- References must resolve; IDs must be unique and well-formed.
- A test labelled VALIDATED must have status PASSED and an evidence reference; a PASSED test must carry an evidence reference.
- A service must not depend on a service that recovers later or may lose more data than it tolerates.
- A service in a higher-priority tier (lower number) must not have a looser RTO or RPO than a service in a lower-priority tier.

### 5.3 What the checker does not prove

It does not judge whether a requirement is correct, whether a decision is good, whether a diagram is accurate, or whether evidence is genuine. It finds structural gaps. Human review is mandatory.

### 5.4 Quality-attribute scenario template

| Part | Content |
|---|---|
| Source | Who or what triggers the stimulus |
| Stimulus | The event |
| Artifact | The part of the system stimulated |
| Environment | Normal, degraded, peak, migration |
| Response | What the system does |
| Response measure | Threshold, percentile, scope, measurement point |
| Owner | Accountable role |
| Label | From Section 0.4 |

Example (illustrative): *A risk event is committed in the source system (stimulus) during normal peak load (environment); the alerting service (artifact) makes the alert queryable to an authorised user (response); the p95 of event-commit-to-queryable time is at most 5 seconds measured over a one-hour representative window, counting missing outputs as failures (measure).*

---

## 6. Worked reconciliation: erasure, immutability, and history

**Status: ILLUSTRATIVE.** Retention and erasure obligations vary by jurisdiction and contract. Confirm with the privacy/legal owner before applying anything below to a real system.

### 6.1 The conflict

| Source | Statement (illustrative) |
|---|---|
| Governance (P10) | Honour an erasure request within 30 days |
| Lakehouse (P07) | Table history is kept for 30 days to support audit and rollback |
| DR (P12) | Backups are immutable and retained for 35 days |
| Streaming (P09) | Event log is retained for 7 days for replay |
| Metadata (P11) | Lineage and audit records are kept for 7 years |
| Serving/AI (P14) | A retrieval index is rebuilt weekly from governed sources |

A request is received on day 0 and executed in the primary table on day 2. Section 6.2 step 5 shows that copies of the same personal data survive in history, backups, the event log, and the index for different lengths of time.

### 6.2 Reconciliation steps

1. **Inventory every store** that can hold the data (primary, history, snapshots, backups, event log, caches, indexes, exports, lineage, audit logs, non-production copies).
2. **Classify each store** by how erasure can be done: delete in place; rewrite; expire by age; not erasable (immutable). Note whether lineage and audit stores hold identifiers or only pseudonymous keys.
3. **Choose a pattern per store** (options, not mandates): delete and compact; rebuild index excluding the subject; shorten history for personal-data tables; per-subject encryption keys so destroying the key renders retained copies unreadable (crypto-shredding); or document a retention exception with a restore-time re-application of pending erasures.
4. **Define restore behaviour.** After restoring from a backup, pending erasures are replayed before data is exposed. Record this as a control and test it.
5. **Reconcile the numbers.** Compute, per store, the day on which the last readable copy disappears, and compare it with the obligation (day 30 here). Illustrative worst cases, with the erasure executed in the primary store on day 2:

   | Store | Rule | Last readable copy | Over day 30 by |
   |---|---|---|---|
   | Primary table | Deleted on day 2 | Day 2 | — |
   | Table history | 30-day history; the pre-delete version is superseded on day 2 | Day 32 | 2 days |
   | Event log | 7-day replay retention (unless a topic is compacted by key) | Day 7 at the latest | — (check compaction) |
   | Retrieval index | Weekly rebuild; next rebuild up to 7 days after day 2 | Day 9 | — |
   | Immutable backups | 35-day retention; a backup taken just before the erasure executes on day 2 | Day 37 | 7 days |
   | Lineage and audit | 7-year retention | Not erased | Compliant only if records hold pseudonymous keys, not direct identifiers; confirm with the privacy delegate |

   The two overruns (history, backups) need a mitigation: per-subject encryption keys (crypto-shredding) destroyed on day 2, shortened history for personal-data tables, or an approved documented exception with restore-time re-application of pending erasures. State the residual window and who accepted it.
6. **Record the decision** as an ADR, the controls in `controls.csv`, the tests (including a restore-then-erasure test) in `tests.csv`, and the open legal question as an OPEN QUESTION.

### 6.3 Evidence expected

- A store-by-store erasure matrix.
- An ADR with alternatives and consequences.
- A test design for restore-then-erasure.
- A statement of residual exposure and who accepted it.

### 6.4 Why this example matters

It crosses five modules, exposes a hidden assumption in each, and cannot be solved inside any one module. Use the same method for RC-04, RC-06, and RC-13.

---

## 7. Option evaluation method

### 7.1 Weighted decision matrix

1. List criteria drawn from MUST and SHOULD requirements and from constraints. Merge overlapping criteria.
2. Assign weights that sum to 100, with a written reason for each weight. Agree the weights *before* scoring options.
3. Score each option 1–5 per criterion using an anchored scale written in advance (for example, 5 = meets with margin and evidence; 3 = meets with assumptions; 1 = fails or unknown).
4. Compute the weighted total: `score(option) = Σ weight_i × score_i / 100`.
5. **Sensitivity.** Vary each weight by ±10 percentage points (renormalising the rest) and note whether the winner changes. If it does, the decision is weight-sensitive and needs an explicit owner call.
6. **Gate criteria.** Some criteria are pass/fail (for example, residency). An option failing a gate is excluded regardless of total.
7. Record unknowns as unknowns, not as mid scores.

### 7.2 Example (illustrative, no real products)

| Criterion | Weight | Option A: single-region primary with warm standby | Option B: active-active two regions |
|---|---|---|---|
| Meets Tier 1 RTO/RPO (gate) | pass/fail | pass (assumption) | pass |
| Cost envelope fit | 30 | 4 | 2 |
| Operational complexity | 25 | 4 | 2 |
| Consistency simplicity | 20 | 4 | 2 |
| Failure-isolation margin | 25 | 3 | 5 |
| **Weighted total** | 100 | 3.75 | 2.75 |

Computation for A: (30×4 + 25×4 + 20×4 + 25×3) / 100 = 3.75. For B: (30×2 + 25×2 + 20×2 + 25×5) / 100 = 2.75. Sensitivity: let the failure-isolation weight be `f` and scale the other three weights pro rata so that all weights still sum to 100 (they sum to 75 in the base case, so each is multiplied by `(100 − f) / 75`).

| `f` | A total | B total | Leader |
|---|---|---|---|
| 25 (base) | 3.75 | 2.75 | A |
| 40 | 3.60 | 3.20 | A |
| 50 | 3.50 | 3.50 | tie |
| 55 | 3.45 | 3.65 | B |

The winner flips at `f = 50`. This is a **weight-sensitive decision**: the choice depends on how much the business values failure isolation, so the owner must confirm that weight in writing, and the ADR must record the flip point. A also depends on its gate result being an unvalidated assumption.

---

## 8. Validation

### 8.1 Validation layers

| Layer | What it checks | Possible in a design-only project? |
|---|---|---|
| Structural | IDs, links, coverage, tier rules (Appendix B) | Yes |
| Calculation | Capacity, cost, latency budget arithmetic re-derived | Yes |
| Walkthrough | Scenarios stepped through the views by reviewers | Yes (simulated reviewers if solo) |
| Tabletop | Incident, recovery, and migration cutover rehearsed on paper | Yes |
| Experiment | Prototype, load test, restore drill | No — plan only, label `NOT VALIDATED` |

### 8.2 Fitness functions (automatable checks on the package)

| ID | Property | How to check |
|---|---|---|
| FF-01 | No duplicate or malformed IDs | Appendix B |
| FF-02 | No dangling references | Appendix B |
| FF-03 | MUST requirements fully traced | Appendix B |
| FF-04 | No VALIDATED claim without a PASSED test and evidence | Appendix B |
| FF-05 | Dependency recovery tiers and tier ordering consistent | Appendix B |
| FF-06 | Every data product has one owner, contract, classification, retention | Script over D06 table (extend Appendix B) |
| FF-07 | Every diagram element is listed in D07 with an owner | Review checklist |
| FF-08 | Every external number cites a source or a label | Search for unlabelled figures |
| FF-09 | Every requirement names an existing business outcome | Appendix B |

### 8.3 Minimum scenario-based test catalogue

Each scenario is implemented by at least one test in `tests.csv`. Start the test name with the scenario ID (for example `SC-05 restore-then-erasure tabletop`) so the mapping can be searched.

| ID | Scenario | Layers | Pass criteria (design-level) |
|---|---|---|---|
| SC-01 | Regulated report from source to dashboard | Walkthrough | Lineage and ownership identifiable at every hop |
| SC-02 | Duplicate customer detected, merged, then split | Walkthrough | Merge audit, downstream propagation, rollback path defined |
| SC-03 | Risk event: source commit to queryable alert | Calculation, walkthrough | Budget arithmetic correct; measurement point defined; failures counted |
| SC-04 | Consumer requests a column it is not entitled to | Walkthrough | Denied at every enforcement point, including derived stores |
| SC-05 | Erasure request with restore from backup | Tabletop | Pending erasures replayed before exposure |
| SC-06 | Loss of one region | Tabletop | Tier 1 and Tier 2 recovered inside targets given dependencies |
| SC-07 | Schema change by a producer | Walkthrough | Compatibility policy blocks or versions the change; consumers notified |
| SC-08 | Migration wave cutover and rollback | Tabletop | Rollback criteria and data reconciliation defined |
| SC-09 | Cost spike of 40% in the largest driver | Calculation | Impact quantified; response options listed |
| SC-10 | Key compromise on the policy plane | Tabletop | Blast radius and rotation steps described |
| SC-11 | AI retrieval of a document after access revoked | Walkthrough | Revocation takes effect inside the stated window |

### 8.4 Requirement-to-evidence matrix

| Requirement | Decision(s) | View/Control | Test(s) | Evidence | Status | Label |
|---|---|---|---|---|---|---|
| RQ-… | ADR-… | VW-…/CT-… | TS-… | EV-… | PLANNED / PASSED | VALIDATED / NOT VALIDATED |

The matrix is generated from the CSV registers; do not maintain it by hand in two places.

---

## 9. Audit and defense

### 9.1 Three review layers

1. **Self-check:** you run Appendix B and the checklist in Section 11.
2. **Independent audit:** a peer, mentor, or you in a different sitting reviews against Section 9.2.
3. **Defense:** a structured questioning session (Section 9.4).

The layers find different problems. A clean checker is the lowest bar, not the highest.

### 9.2 Audit rubric (100 points)

| Area | Points | Question |
|---|---|---|
| Scope and authority | 5 | Is it clear what is in scope, who decides, and what done means? |
| Requirements quality | 10 | Are MUST requirements testable, owned, and non-contradictory? |
| Reconciliation | 15 | Are cross-module conflicts found, logged, and resolved by stated rules? |
| Architecture coherence | 15 | Do views agree with each other and with the requirements? |
| Data and model integrity | 10 | One key, owner, contract, and retention per product and entity? |
| Governance, security, privacy | 10 | Are controls enforced at all access paths, including derived stores? |
| Resilience, performance, cost | 10 | Are targets mutually achievable or the trade-off explicit? |
| Decisions and evaluation | 5 | Alternatives, criteria, sensitivity, revisit triggers? |
| Operations and migration | 5 | Owners, on-call, waves, rollback, DR during coexistence? |
| Traceability and evidence | 10 | Does the chain hold and does evidence exist? |
| Honesty and communication | 5 | Are unproven claims labelled and limits stated? |
| **Total** | **100** | |

**Pass standard:** at least 80 points, with no area scoring below 50% of its points, and no open Severity 1 finding.

### 9.3 Finding severity

| Severity | Definition | Example |
|---|---|---|
| S1 | Invalidates a MUST requirement or makes a claim false | Tier 1 service depends on a store that recovers after its RTO; VALIDATED claim with no evidence |
| S2 | Material gap or contradiction needing correction before approval | Erasure ignores backups; two retention periods for one dataset |
| S3 | Weakness that reduces clarity or confidence | Missing alternative in an ADR |
| S4 | Cosmetic | Inconsistent heading style |

### 9.4 Review questions by role

| Role | Questions |
|---|---|
| Executive sponsor | What do I get, what does it cost at low/expected/high, what is not yet proven, what decision do you need from me? |
| Chief Risk delegate | How is alert latency measured and what happens when the measurement fails? What breaks if the backbone is down? |
| CISO delegate | Where is each trust boundary and which control sits on it? How is access revoked across every derived store? |
| Privacy delegate | Show me how an erasure request reaches every store, including backups. What is the residual exposure window and who accepted it? |
| Finance partner | What are the two largest cost drivers and how sensitive is the total to each? What is the double-running cost during migration? |
| SRE lead | Which tier is each service, what does it depend on, and where is the evidence the dependencies recover in time? Who is paged? |
| Platform lead | What did you decide not to build, and what do domain teams own versus the platform? |
| Peer architect | Which two decisions would you reverse first if an assumption fails? Which module project did you have to change after reconciliation? |

### 9.5 Defense record template (D22)

```markdown
# Defense Record — Northbridge Enterprise Data Architecture Package
- Package version:
- Date:
- Reviewer(s) and roles (simulated if applicable):
- Audit score and any area below threshold:

## Questions and responses
| # | Question | Role | Response summary | Evidence cited | Satisfactory? |
|---|----------|------|------------------|----------------|---------------|

## Findings
| ID | Severity | Description | Disposition | Owner | Due |

## Outcome
- [ ] Approved
- [ ] Approved with conditions (list, with owners and dates)
- [ ] Returned for rework (list what must change)

## Statement of unproven claims accepted by reviewers
```

---

## 10. Registers and templates

### 10.1 Assumption register

| ID | Assumption | Label | Impacted decisions | Impact if wrong | Validation path | Owner | Due |
|---|---|---|---|---|---|---|---|
| AS-001 | Tier 1 services can tolerate a 15-minute RPO | ILLUSTRATIVE ASSUMPTION | ADR-004 | Redesign of replication | Owner confirmation; replay-lag measurement | SRE lead | — |

### 10.2 Open-question log

| ID | Question | Why it matters | Owner | Needed by | Consequence if unresolved |
|---|---|---|---|---|---|

### 10.3 Risk register

| ID | Risk | Likelihood | Impact | Owner | Response (avoid, reduce, transfer, accept) | Trigger | Related items |
|---|---|---|---|---|---|---|---|

### 10.4 Dependency register

| ID | Dependency | Type (internal, vendor, regulatory, skill) | Needed by | Owner | Status |
|---|---|---|---|---|---|

### 10.5 Data-product catalogue entry (D06)

| Field | Content |
|---|---|
| Product ID and name | |
| Domain and accountable owner | One owner |
| Purpose and consumers | |
| Contract version and location | |
| Logical-model entities and keys | Canonical key strategy |
| Classification | |
| Freshness and quality commitments | Measurable |
| Retention and erasure approach | Links to the Section 6 matrix if personal data |
| Enforcement points | Where access policy applies |
| Status and lifecycle | |
| Source modules and conflicts | RC/RX references |

### 10.6 Service ownership table (D14)

| Service | Tier | Operating team | Escalation route | Dependencies | Runbook | Change authority | Data-product owners served |
|---|---|---|---|---|---|---|---|

---

## 11. Final quality checklist

**Scope and authority**
- [ ] D01 states scope, exclusions, decision rights, and done criteria.
- [ ] Every approval is real or explicitly marked simulated.

**Inputs and language**
- [ ] All of P01–P16 appear in D02 with completeness and ID scheme.
- [ ] D03 has one meaning per term; every legacy ID is mapped or retired.

**Requirements and traceability**
- [ ] Every MUST requirement is testable, owned, and labelled.
- [ ] Checker exits 0; each WARN is justified.
- [ ] No VALIDATED label without evidence.

**Architecture**
- [ ] Views agree with each other (names, boundaries, flows).
- [ ] Each of the five workload patterns shows shared and non-shared components with reasons.
- [ ] Each interface has protocol, contract, owner, and failure behaviour.

**Data, governance, metadata**
- [ ] One owner, contract, classification, and retention per data product.
- [ ] Access enforcement covers tables, APIs, semantic layer, caches, and retrieval indexes.
- [ ] Erasure addresses every store holding personal data, including backups and logs.
- [ ] Lineage coverage defined for streaming and CDC flows.

**Resilience, performance, cost**
- [ ] Every service has a tier; dependency rule passes.
- [ ] Latency claims rely on end-to-end measurement design, not summed percentiles.
- [ ] Cost shows low, expected, and high scenarios and sensitivity.

**Decisions, risk, operations, migration**
- [ ] Each ADR has alternatives, consequences, and a revisit trigger.
- [ ] Each risk has an owner; each assumption has a validation path.
- [ ] Each service has an operator and on-call route.
- [ ] Each wave has rollback and DR coverage.

**Communication**
- [ ] Executive brief lists what is not proven.
- [ ] Defense record and handover exist.

---

## 12. Practice and mastery exercises

1. **Conflict hunt.** Choose any two module projects. Find three genuine conflicts between them that are not in Section 4.1. Log them as `RX-NN` with a resolution.
2. **Tier break.** Edit `tiers.csv` so a Tier 1 service depends on a Tier 3 store. Predict the checker output, then run it. Fix the design three different ways and compare.
3. **Percentile trap.** Given five stage p95 values that sum to 4.2 s, explain why the end-to-end p95 may exceed or fall below 4.2 s. Design the measurement.
4. **Erasure walk.** Add a seventh store (an analytics export to a partner) to the Section 6 matrix and decide what is possible.
5. **Weight sensitivity.** Rework the Section 7.2 example with failure isolation weighted 50. Show when the winner flips.
6. **Cut the scope.** Remove the AI retrieval pattern. List every artifact that changes and every requirement that becomes untraced.
7. **Defend from the other side.** Write the three hardest questions a CISO delegate would ask and answer them with evidence references.
8. **Retrospective.** Identify which module project would most improve if rewritten now and list the changes.

---

## 13. Glossary

| Term | Meaning in this project |
|---|---|
| Architecture of record | The single reviewed, traceable architecture description the organisation relies on |
| Reconciliation | Detecting and resolving conflicts between artifacts produced separately |
| Traceability | A verifiable chain from requirement to decision, view or control, test, and evidence |
| Fitness function | A repeatable check on an architectural property |
| Crypto-shredding | Rendering retained encrypted copies unreadable by destroying the key |
| Simulated approval | A role-played sign-off in a solo exercise; carries no authority |
| Severity | The impact class of an audit finding (Section 9.3) |

---

## 14. Reference frameworks

Use these as vocabularies, not as compliance claims. Check their current editions yourself.

- ISO/IEC/IEEE 42010 — architecture description.
- TOGAF Architecture Development Method — enterprise architecture process.
- DAMA-DMBOK — data management body of knowledge.
- C4 model — container and component diagrams.
- arc42 — architecture documentation template.
- Evolutionary architecture and architectural fitness functions.
- Site reliability engineering practice for service levels and error budgets.

---

## Appendix A — Register files (CSV)

Semicolons separate multiple references in one cell. All files use a header row. Minimal working example for the Northbridge package (illustrative). The evidence references (`EV-…`) are placeholders: in your package they must resolve to real files, and a test is PASSED only after the check has actually been performed.

`registers/outcomes.csv`

```csv
id,name
BO-01,Trusted reconciled enterprise reporting
BO-02,One governed customer identity view
BO-03,Timely correct risk signals
BO-05,Defensible cloud and cost posture
BO-06,Governed analytics and AI access
BO-07,Clear ownership and sustainable operations
```

`registers/requirements.csv`

```csv
id,statement,priority,label,owner,outcome
RQ-001,Executive risk exposure report reconciles to the finance ledger within an agreed tolerance,MUST,PROPOSED REQUIREMENT,Head of Risk,BO-01
RQ-002,Alert visibility for risk events meets the agreed p95 latency objective,MUST,PROPOSED REQUIREMENT,Head of Risk,BO-03
RQ-003,Restricted customer attributes are accessible only to authorised roles,MUST,PROPOSED REQUIREMENT,CISO,BO-06
RQ-004,Tier 1 services recover within the agreed RTO and RPO,MUST,PROPOSED REQUIREMENT,Head of Technology,BO-07
RQ-005,Annual platform run cost stays inside the approved envelope,SHOULD,PROPOSED REQUIREMENT,Finance Partner,BO-05
RQ-006,Customer identity merges are auditable and reversible,MUST,PROPOSED REQUIREMENT,Data Steward,BO-02
```

`registers/decisions.csv`

```csv
id,title,status,drivers,label
ADR-001,Adopt a governed lakehouse as the analytical platform of record,ACCEPTED,RQ-001;RQ-005,RECOMMENDATION
ADR-002,Use an event backbone with a separate low-latency serving store for risk alerts,ACCEPTED,RQ-002,RECOMMENDATION
ADR-003,Enforce attribute-level access through central policy with tagged classifications,ACCEPTED,RQ-003,RECOMMENDATION
ADR-004,Adopt tiered recovery with warm standby for Tier 1 services,ACCEPTED,RQ-004;RQ-005,RECOMMENDATION
ADR-005,Keep merge history as an append-only audit with steward-approved survivorship,ACCEPTED,RQ-006,RECOMMENDATION
```

`registers/views.csv`

```csv
id,name,realises
VW-01,System context and container view,RQ-001;RQ-002
VW-02,Data-flow and trust-boundary view,RQ-003;RQ-006
VW-03,Deployment and recovery view,RQ-004;RQ-005
```

`registers/controls.csv`

```csv
id,name,satisfies
CT-001,Daily ledger-to-lakehouse reconciliation control,RQ-001
CT-002,Central policy decision point with attribute tags,RQ-003
CT-003,Quarterly restore drill,RQ-004
CT-004,Steward approval workflow for identity merges,RQ-006
```

`registers/tests.csv`

```csv
id,name,verifies,status,evidence_ref,label
TS-001,Reconciliation walkthrough on a sample close,RQ-001,PASSED,EV-2026-001,VALIDATED
TS-002,Latency budget tabletop review,RQ-002,PLANNED,,NOT VALIDATED
TS-003,Access-matrix review by CISO delegate,RQ-003,PASSED,EV-2026-002,VALIDATED
TS-004,Recovery dependency walk-through,RQ-004,PLANNED,,NOT VALIDATED
TS-005,Cost model sensitivity review,RQ-005,PLANNED,,NOT VALIDATED
TS-006,Merge-and-split walkthrough,RQ-006,PLANNED,,NOT VALIDATED
```

`registers/risks.csv`

```csv
id,description,related,owner
RK-001,Risk-alert latency objective is unproven until measured,RQ-002;ADR-002,Risk Platform Lead
RK-002,Tag coverage gaps leave restricted columns unlabelled,RQ-003;CT-002,Data Governance Lead
```

`registers/tiers.csv`

```csv
service,tier,rto_min,rpo_min
risk-alerting,1,120,15
event-backbone,1,60,5
identity-service,1,60,5
lakehouse-core,2,480,60
reporting,2,480,60
sandbox,3,4320,1440
```

`registers/dependencies.csv`

```csv
service,depends_on
risk-alerting,event-backbone
risk-alerting,identity-service
reporting,lakehouse-core
```

**Column rules**

| File | Required columns | ID pattern |
|---|---|---|
| `outcomes.csv` | id, name | `BO-NN` |
| `requirements.csv` | id, statement, priority (MUST/SHOULD/COULD), label, owner, outcome (one or more `BO-NN`, `;`-separated) | `RQ-NNN` |
| `decisions.csv` | id, title, status (PROPOSED/ACCEPTED/SUPERSEDED/REJECTED), drivers, label | `ADR-NNN` |
| `views.csv` | id, name, realises | `VW-NN` or `VW-NNN` |
| `controls.csv` | id, name, satisfies | `CT-NNN` |
| `tests.csv` | id, name, verifies, status (PLANNED/PASSED/FAILED/WAIVED), evidence_ref, label | `TS-NNN` |
| `risks.csv` | id, description, related, owner | `RK-NNN` |
| `tiers.csv` | service, tier, rto_min, rpo_min | lowercase-kebab service name |
| `dependencies.csv` | service, depends_on | — |

---

## Appendix B — Structural consistency checker

Save as `tools/arch_package_check.py`. Standard library only; Python 3.9 or later. Run with `python3 -I tools/arch_package_check.py --workspace registers` (the `-I` flag stops Python importing stray modules from the current directory). Exit codes: 0 no ERROR; 1 at least one ERROR (including missing or unreadable register files); 2 workspace directory not found.

```python
#!/usr/bin/env python3
"""Structural consistency checker for an enterprise data architecture package.

Reads CSV registers from a workspace directory and reports structural defects:
missing files/columns, duplicate or malformed IDs, dangling references,
untraced requirements, orphan decisions, unsupported VALIDATED claims, and
recovery-tier contradictions between a service and its dependencies.

It checks structure only. A clean run does NOT certify the architecture.
Standard library only (Python 3.9+).  Usage:
    python3 -I arch_package_check.py --workspace path/to/registers
Exit codes: 0 = no ERROR findings; 1 = at least one ERROR finding (this includes
missing or unreadable register files); 2 = the workspace directory does not exist.
Duplicate IDs: the first row with an ID is the authoritative one.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

LABELS = {"SOURCE-DERIVED", "CONFIRMED FACT", "ILLUSTRATIVE ASSUMPTION",
          "PROPOSED REQUIREMENT", "HYPOTHESIS", "RECOMMENDATION",
          "OPEN QUESTION", "VALIDATED", "NOT VALIDATED"}
PRIORITIES = {"MUST", "SHOULD", "COULD"}
DECISION_STATUS = {"PROPOSED", "ACCEPTED", "SUPERSEDED", "REJECTED"}
TEST_STATUS = {"PLANNED", "PASSED", "FAILED", "WAIVED"}

# file -> (required columns, ID column, ID regex)
SCHEMA = {
    "outcomes.csv": (["id", "name"], "id", r"^BO-\d{2}$"),
    "requirements.csv": (["id", "statement", "priority", "label", "owner", "outcome"], "id", r"^RQ-\d{3}$"),
    "decisions.csv": (["id", "title", "status", "drivers", "label"], "id", r"^ADR-\d{3}$"),
    "views.csv": (["id", "name", "realises"], "id", r"^VW-\d{2,3}$"),
    "controls.csv": (["id", "name", "satisfies"], "id", r"^CT-\d{3}$"),
    "tests.csv": (["id", "name", "verifies", "status", "evidence_ref", "label"], "id", r"^TS-\d{3}$"),
    "risks.csv": (["id", "description", "related", "owner"], "id", r"^RK-\d{3}$"),
    "tiers.csv": (["service", "tier", "rto_min", "rpo_min"], "service", r"^[a-z][a-z0-9-]*$"),
    "dependencies.csv": (["service", "depends_on"], None, None),
}


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, code, msg):
        self.items.append((level, code, msg))

    def count(self, level):
        return sum(1 for i in self.items if i[0] == level)


def split(cell):
    return [p.strip() for p in (cell or "").split(";") if p.strip()]


def load(ws, name, rep):
    cols, idcol, idre = SCHEMA[name]
    path = ws / name
    if not path.is_file():
        rep.add("ERROR", "FILE-MISSING", f"{name} not found")
        return None
    try:
        with path.open(newline="", encoding="utf-8-sig") as fh:  # utf-8-sig tolerates a spreadsheet BOM
            reader = csv.DictReader(fh)
            missing = [c for c in cols if c not in (reader.fieldnames or [])]
            if missing:
                rep.add("ERROR", "COLUMN-MISSING", f"{name}: missing column(s) {missing}")
                return None
            rows = [{k: (v or "").strip() for k, v in r.items() if k} for r in reader]
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        rep.add("ERROR", "FILE-UNREADABLE", f"{name}: {exc.__class__.__name__}: {exc}")
        return None
    seen = set()
    if idcol:
        for n, r in enumerate(rows, start=2):
            v = r[idcol]
            if not re.match(idre, v):
                rep.add("ERROR", "ID-FORMAT", f"{name} line {n}: '{v}' does not match {idre}")
            if v in seen:
                rep.add("ERROR", "ID-DUPLICATE", f"{name} line {n}: duplicate id '{v}'")
            seen.add(v)
    return rows


def index(rows, key="id"):
    """Map key -> row; the first row wins when a key is duplicated."""
    out = {}
    for r in rows:
        out.setdefault(r[key], r)
    return out


def check_labels(name, rows, rep):
    for r in rows:
        if r.get("label") and r["label"] not in LABELS:
            rep.add("ERROR", "LABEL-INVALID", f"{name} {r.get('id')}: label '{r['label']}' not in vocabulary")


def run(ws):
    rep = Report()
    t = {n: load(ws, n, rep) for n in SCHEMA}
    if any(v is None for v in t.values()):
        return rep
    out = index(t["outcomes.csv"])
    req = index(t["requirements.csv"])
    dec = index(t["decisions.csv"])
    views = index(t["views.csv"])
    ctl = index(t["controls.csv"])
    tst = index(t["tests.csv"])
    rsk = index(t["risks.csv"])
    known = {**req, **dec, **views, **ctl, **tst, **rsk}

    for name in ("requirements.csv", "decisions.csv", "tests.csv"):
        check_labels(name, t[name], rep)
    for r in t["requirements.csv"]:
        if r["priority"] not in PRIORITIES:
            rep.add("ERROR", "PRIORITY-INVALID", f"{r['id']}: priority '{r['priority']}'")
    for r in t["decisions.csv"]:
        if r["status"] not in DECISION_STATUS:
            rep.add("ERROR", "STATUS-INVALID", f"{r['id']}: decision status '{r['status']}'")
    for r in t["tests.csv"]:
        if r["status"] not in TEST_STATUS:
            rep.add("ERROR", "STATUS-INVALID", f"{r['id']}: test status '{r['status']}'")
        if r["label"] == "VALIDATED" and not r["evidence_ref"]:
            rep.add("ERROR", "VALIDATED-NO-EVIDENCE", f"{r['id']}: labelled VALIDATED without evidence_ref")
        if r["label"] == "VALIDATED" and r["status"] != "PASSED":
            rep.add("ERROR", "VALIDATED-NOT-PASSED", f"{r['id']}: labelled VALIDATED but status is {r['status']}")
        if r["status"] == "PASSED" and not r["evidence_ref"]:
            rep.add("ERROR", "PASSED-NO-EVIDENCE", f"{r['id']}: status PASSED without evidence_ref")
        if r["status"] == "PASSED" and r["label"] != "VALIDATED":
            rep.add("WARN", "PASSED-LABEL", f"{r['id']}: status PASSED but label is '{r['label']}'")

    # dangling references
    def refs(rows, col, targets, kind):
        for r in rows:
            for ref in split(r[col]):
                if ref not in targets:
                    rep.add("ERROR", "DANGLING-REF", f"{r['id']}.{col}: '{ref}' is not a known {kind}")
    refs(t["requirements.csv"], "outcome", out, "business outcome")
    refs(t["decisions.csv"], "drivers", req, "requirement")
    refs(t["views.csv"], "realises", req, "requirement")
    refs(t["controls.csv"], "satisfies", req, "requirement")
    refs(t["tests.csv"], "verifies", {**req, **dec, **ctl}, "requirement/decision/control")
    refs(t["risks.csv"], "related", known, "register item")

    # orphan decisions
    for d in t["decisions.csv"]:
        if d["status"] != "REJECTED" and not split(d["drivers"]):
            rep.add("ERROR", "ORPHAN-DECISION", f"{d['id']}: no driving requirement")
    superseded = {d["id"] for d in t["decisions.csv"] if d["status"] == "SUPERSEDED"}
    # tests that only verify superseded decisions do not count as coverage
    live_dec = {k for k, v in dec.items() if v["status"] in ("ACCEPTED", "PROPOSED")}

    # requirement coverage chain: requirement -> decision -> (view|control) -> test
    for q in req.values():
        rid = q["id"]
        decs = {d["id"] for d in t["decisions.csv"]
                if rid in split(d["drivers"]) and d["id"] in live_dec}
        viewc = [v["id"] for v in t["views.csv"] if rid in split(v["realises"])]
        ctlc = [c["id"] for c in t["controls.csv"] if rid in split(c["satisfies"])]
        verifiers = {x["id"] for x in t["tests.csv"]
                     if x["id"] in tst and tst[x["id"]] is x
                     and (rid in split(x["verifies"])
                          or any(d in split(x["verifies"]) for d in decs)
                          or any(c in split(x["verifies"]) for c in ctlc))}
        sev = "ERROR" if q["priority"] == "MUST" else "WARN"
        if not decs:
            rep.add(sev, "NO-DECISION", f"{rid} ({q['priority']}): no live decision is driven by it")
        if not viewc and not ctlc:
            rep.add(sev, "NO-REALISATION", f"{rid} ({q['priority']}): no view or control realises it")
        if not q["outcome"]:
            rep.add(sev, "NO-OUTCOME", f"{rid} ({q['priority']}): no business outcome")
        if not verifiers:
            rep.add(sev, "NO-TEST", f"{rid} ({q['priority']}): no test verifies it")
        else:
            states = {tst[v]["status"] for v in verifiers}
            if states == {"FAILED"}:
                rep.add(sev, "ONLY-FAILED", f"{rid} ({q['priority']}): every verifying test has FAILED")
            elif states <= {"WAIVED", "FAILED"}:
                rep.add("WARN", "ONLY-WAIVED", f"{rid}: no verifying test is PLANNED or PASSED (waived/failed only)")
    for o in out.values():
        if not any(o["id"] in split(q["outcome"]) and q["priority"] == "MUST" for q in req.values()):
            rep.add("WARN", "OUTCOME-NO-MUST", f"{o['id']}: no MUST requirement serves this outcome")
    for s in superseded:
        if not any(s in split(x["verifies"]) for x in t["tests.csv"]):
            continue
        rep.add("INFO", "TEST-ON-SUPERSEDED", f"{s} is SUPERSEDED but still referenced by a test; retarget it")

    # recovery-tier consistency
    tiers = {}
    tier_of = {}
    for r in t["tiers.csv"]:
        try:
            rto, rpo, tier = int(r["rto_min"]), int(r["rpo_min"]), int(r["tier"])
        except ValueError:
            rep.add("ERROR", "TIER-NUMERIC", f"tiers.csv {r['service']}: tier, rto_min and rpo_min must be integers")
            continue
        if rto < 0 or rpo < 0 or tier not in (1, 2, 3):
            rep.add("ERROR", "TIER-INVALID", f"tiers.csv {r['service']}: tier must be 1-3 and RTO/RPO must be >= 0")
            continue
        tiers.setdefault(r["service"], (rto, rpo))
        tier_of.setdefault(r["service"], tier)
    for a in tiers:
        for b in tiers:
            if tier_of[a] < tier_of[b] and (tiers[a][0] > tiers[b][0] or tiers[a][1] > tiers[b][1]):
                rep.add("ERROR", "TIER-ORDER", f"{a} is tier {tier_of[a]} but has a looser RTO/RPO than {b} (tier {tier_of[b]})")
    for r in t["dependencies.csv"]:
        s, d = r["service"], r["depends_on"]
        for x in (s, d):
            if x not in tiers:
                rep.add("ERROR", "DANGLING-REF", f"dependencies.csv: service '{x}' missing from tiers.csv")
        if s in tiers and d in tiers:
            if tiers[d][0] > tiers[s][0]:
                rep.add("ERROR", "TIER-RTO", f"{s} (RTO {tiers[s][0]} min) depends on {d} (RTO {tiers[d][0]} min): dependency recovers later than its consumer")
            if tiers[d][1] > tiers[s][1]:
                rep.add("ERROR", "TIER-RPO", f"{s} (RPO {tiers[s][1]} min) depends on {d} (RPO {tiers[d][1]} min): dependency may lose more data than its consumer tolerates")
    # dependency cycles (DFS)
    graph = {}
    for r in t["dependencies.csv"]:
        graph.setdefault(r["service"], []).append(r["depends_on"])
    state = {}

    def dfs(n, path):
        state[n] = 1
        for m in graph.get(n, []):
            if state.get(m) == 1:
                rep.add("ERROR", "DEP-CYCLE", "dependency cycle: " + " -> ".join(path + [n, m]))
            elif m not in state:
                dfs(m, path + [n])
        state[n] = 2
    for n in list(graph):
        if n not in state:
            dfs(n, [])
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workspace", required=True, help="directory containing the register CSV files")
    a = ap.parse_args(argv)
    ws = Path(a.workspace)
    if not ws.is_dir():
        print(f"workspace not found: {ws}", file=sys.stderr)
        return 2
    rep = run(ws)
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for lvl, code, msg in sorted(rep.items, key=lambda i: (order[i[0]], i[1], i[2])):
        print(f"{lvl:<5} {code:<22} {msg}")
    print(f"\nsummary: {rep.count('ERROR')} error(s), {rep.count('WARN')} warning(s), {rep.count('INFO')} info")
    print("note: structural check only; a clean result is not architecture approval.")
    return 1 if rep.count("ERROR") else 0


if __name__ == "__main__":
    sys.exit(main())
```

### B.1 Output on the sample registers above

The sample has no errors. It has one WARN: business outcome BO-05 is served only by a SHOULD requirement. In a real package you would either add a MUST requirement or record the justification in D17.

```text
WARN  OUTCOME-NO-MUST        BO-05: no MUST requirement serves this outcome

summary: 0 error(s), 1 warning(s), 0 info
note: structural check only; a clean result is not architecture approval.
```

### B.2 Output on a deliberately defective copy

The defects injected were: a MUST requirement with no decision, realisation, or test; a requirement citing an unknown outcome; a duplicate requirement ID (the first row stays authoritative); an orphan decision; a decision citing a missing requirement; a MUST requirement whose only test FAILED; a test labelled VALIDATED while only PLANNED; a PASSED and VALIDATED test with no evidence; Tier 1 services that recover later or lose more data than a dependency allows; a Tier 1 service with a looser objective than a Tier 2 service; and a dependency cycle.

```text
ERROR DANGLING-REF           ADR-007.drivers: 'RQ-099' is not a known requirement
ERROR DANGLING-REF           RQ-007.outcome: 'BO-09' is not a known business outcome
ERROR DEP-CYCLE              dependency cycle: risk-alerting -> event-backbone -> sandbox -> reporting -> event-backbone
ERROR ID-DUPLICATE           requirements.csv line 9: duplicate id 'RQ-002'
ERROR NO-DECISION            RQ-007 (MUST): no live decision is driven by it
ERROR NO-REALISATION         RQ-007 (MUST): no view or control realises it
ERROR NO-TEST                RQ-007 (MUST): no test verifies it
ERROR ONLY-FAILED            RQ-006 (MUST): every verifying test has FAILED
ERROR ORPHAN-DECISION        ADR-006: no driving requirement
ERROR PASSED-NO-EVIDENCE     TS-008: status PASSED without evidence_ref
ERROR TIER-ORDER             risk-alerting is tier 1 but has a looser RTO/RPO than archive (tier 2)
ERROR TIER-RPO               event-backbone (RPO 5 min) depends on sandbox (RPO 1440 min): dependency may lose more data than its consumer tolerates
ERROR TIER-RTO               event-backbone (RTO 60 min) depends on sandbox (RTO 4320 min): dependency recovers later than its consumer
ERROR VALIDATED-NO-EVIDENCE  TS-008: labelled VALIDATED without evidence_ref
ERROR VALIDATED-NOT-PASSED   TS-007: labelled VALIDATED but status is PLANNED
WARN  OUTCOME-NO-MUST        BO-05: no MUST requirement serves this outcome

summary: 15 error(s), 1 warning(s), 0 info
note: structural check only; a clean result is not architecture approval.
```

### B.3 Limits

- It cannot tell whether a link is meaningful, only that it exists.
- When an ID is duplicated, the first row is authoritative and later rows are ignored for link checking, so fix duplicates first.
- It counts a PLANNED test as coverage (a plan exists) but not a FAILED one; read the PLANNED count in D17 before claiming readiness.
- It does not parse Markdown deliverables; extend it (FF-06) if you maintain product tables as CSV.

---

## Appendix C — ADR template

```markdown
# ADR-NNN — <decision title>

- Status: PROPOSED | ACCEPTED | SUPERSEDED by ADR-NNN | REJECTED
- Date:
- Deciders (simulated if solo):
- Drivers: RQ-…, RQ-…

## Context
## Options considered
(at least two real alternatives)
## Evaluation
(criteria, weights, scores, sensitivity — Section 7)
## Decision
## Consequences
(positive, negative, operational)
## Risks and assumptions
(AS-…, RK-…)
## Validation plan
(TS-…)
## Revisit triggers
```

---

## Appendix D — Executive brief outline (two pages)

1. **Recommendation** in three sentences.
2. **Outcomes** it serves (BO-…) and how success will be measured.
3. **Cost range** (low / expected / high) with the two biggest drivers and assumptions.
4. **Risk** — top five, owners, responses.
5. **What is proven and what is not.**
6. **Decisions requested** and by when.
7. **Roadmap** — waves and rollback in one diagram.

---

## Appendix E — Mapping to Stage 2D modules

| Module | Topic | Used in step(s) |
|---|---|---|
| 01 | Foundations and principles | 1, 3, 5 |
| 02 | Requirements, constraints, decisions | 4, 11 |
| 03 | Patterns and reference architectures | 7, 11 |
| 04 | Conceptual, logical, physical modeling | 6 |
| 05 | Database and storage architecture | 7, 9 |
| 06 | Integration and interoperability | 6, 7, 12 |
| 07 | Enterprise platform and lakehouse | 7 |
| 08 | Cloud, hybrid, multi-cloud | 10 |
| 09 | Streaming and real-time | 7, 9 |
| 10 | Governance, security, privacy, compliance | 8, 10 |
| 11 | Metadata, lineage, quality, master data | 8 |
| 12 | Reliability, resilience, DR | 9 |
| 13 | Performance, scalability, cost | 9, 10 |
| 14 | Data access, serving, semantic, AI | 7, 8 |
| 15 | Documentation, reviews, operating model | 12, 14 |
| 16 | Case studies and capstone | 15 (method reference) |

---

## Appendix F — Change log and audit record

### F.1 Versions

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-10-22 | Initial complete specification (draft) |
| 2.0 | 2026-10-22 | Remediated after an independent-style audit of v1 (F.2 to F.4) |

### F.2 Audit of v1

Method: scripted checks (embedded code versus tested source, cross-references, deliverable and step consistency, arithmetic re-derivation); behavioural probes of the checker with crafted registers; manual review against the Stage 2D module projects and this document's own rules.

Result: **75 / 100 — returned for rework.** 17 findings: 4 Severity 1, 7 Severity 2, 6 Severity 3.

| Severity | Findings |
|---|---|
| S1 | F-01 wrong sensitivity claim in Section 7.2 (the winner actually flips at weight 50); F-02 checker counted a FAILED test as coverage; F-03 checker accepted a VALIDATED label on a test that was only PLANNED; F-04 v1 declared itself "audited" before any audit |
| S2 | F-05 effort total 46.0 versus actual 45.5; F-06 outcome-to-requirement link not enforced; F-07 erasure windows in Section 6 under-counted; F-08 duplicate-ID behaviour documented wrongly; F-09 checker mishandled a BOM and crashed on a non-UTF-8 file; F-10 `SC` scenario IDs outside the ID scheme; F-11 no templates for the data-product catalogue or service ownership table |
| S3 | F-12 title numbering; F-13 misleading parallelism of Steps 8 to 11; F-14 placeholder evidence unmarked in the sample; F-15 exit-code contract unclear; F-16 defect sample did not exercise new checks; F-17 tier values and tier ordering unchecked |

### F.3 Remediation

All 17 findings were fixed. The checker gained: first-row-wins duplicate handling, a `utf-8-sig` reader with an unreadable-file error, `outcomes.csv` and requirement-to-outcome checks, FAILED-only and VALIDATED-not-PASSED checks, and tier validity and ordering checks. Each fix was confirmed by a probe that failed before and passes after. The sample registers and the deliberately defective copy were rebuilt, and the outputs in Appendix B are captured from live runs. Correction recorded during remediation: the audit's first estimate of the backup overrun in Section 6 (5 days) was imprecise; with a backup taken immediately before erasure on day 2 the last readable copy disappears on day 37, 7 days over the obligation, and Section 6 uses that figure.

### F.4 Re-audit of v2

Scripted checks all pass: 34 balanced code fences; the embedded checker is identical to the tested source; the registers in Appendix A reproduce the output shown in B.1; all `Section N` references resolve; 16 steps, 23 deliverables, 16 reconciliation items, 11 scenarios, and 9 fitness functions are consistent; effort sums to 45.5 hours; rubric weights sum to 100.

Self re-audit score: **92 / 100**, no open Severity 1 or Severity 2 finding.

| Area | Max | Score |
|---|---|---|
| Scope and authority | 5 | 5 |
| Requirements quality | 10 | 9 |
| Reconciliation | 15 | 14 |
| Architecture coherence | 15 | 14 |
| Data and model integrity | 10 | 9 |
| Governance, security, privacy | 10 | 9 |
| Resilience, performance, cost | 10 | 9 |
| Decisions and evaluation | 5 | 5 |
| Operations and migration | 5 | 4 |
| Traceability and evidence | 10 | 9 |
| Honesty and communication | 5 | 5 |

### F.5 Known limitations (open, Severity 3)

1. This is a self-audit by the author. Run Step 14 with a peer or mentor before treating the score as independent.
2. The specification was not dry-run end to end against a learner's actual P01 to P16 deliverables. The reconciliation catalogue was derived from the module project structures and sampled figures, and may miss conflicts that only appear in full content; add them as `RX-NN` items.
3. The checker was verified by crafted probes, not a formal automated test suite. Fitness functions FF-06, FF-07, and FF-08 are manual.
4. The tier values in Section 1.4 are carried from the disaster-recovery module; if your P12 values differ, yours win.
