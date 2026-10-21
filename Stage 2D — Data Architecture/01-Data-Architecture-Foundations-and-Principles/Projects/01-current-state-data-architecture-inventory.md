# Project 01 — Current-State Data Architecture Inventory

> **Stage:** Stage 2D — Data Architecture
> **Module:** 2D.1 — Data Architecture Foundations and Principles
> **Project type:** Architecture assessment (baseline, not design)
> **Roadmap source:** `roadmap-Data-Architecture-Foundations-and-Principles.md`, Section 7
> **Project file:** `Projects/01-current-state-data-architecture-inventory.md`

---

## 0. Document control

| Item | Value |
| --- | --- |
| Document | Project specification and worked reference, deliverables D1–D10 |
| Version | 1.1 (post-audit) |
| Date | 2026-10-21 |
| Status | Complete as a project specification and worked reference. **The Northbridge content is illustrative; no stakeholder review has taken place.** |
| Audience | Learner running the project; reviewer challenging the work |
| Scenario | *Northbridge Bank*, a fictional mid-sized retail and business bank (roadmap Section 7.2) |
| Evidence rule | Every row is labelled **Observed**, **Reported**, **Assumed** or **Unknown** (Section 4.3) |
| Companion tool | Consistency checker, Appendix B (`check_inventory.py`) |

**Change log**

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-10-21 | First complete design |
| 1.1 | 2026-10-21 | Post-audit: renamed flow columns to `From`/`To` (duplicate `Source` header); hardened the checker (diagram detection, asset references, duplicate-header guard, clearer spot-check chain); corrected the flow-count narrative; removed an unsupported statement about a "candidate list" of assets; fixed RACI accountability; hedged F-06 and a framework claim |

**Reading order.** Sections 1–5 explain the project and how to run it. Section 6 is
a complete worked reference (D1–D10). Section 7 is the quality gate. Section 8
holds templates for running the project on a real organisation. Sections 9–11
cover pitfalls, hand-off and self-assessment.

---

## 1. Project overview

### 1.1 What this project is

A **current-state data architecture inventory** is a structured, evidence-based
picture of how an organisation's data is *produced, held, moved, governed and
used today*, together with the gaps and risks that picture reveals. It is the
baseline that every later architecture activity compares against.

It answers six questions, in this order:

1. What business capabilities and domains exist, and what data do they depend on?
2. Which systems produce, hold and consume that data?
3. Which data assets matter, and who is accountable for each?
4. How does data move between systems, by what method and how often?
5. Which principles, standards and governance arrangements exist, and are they practised?
6. Where does the current state fall short, what is the evidence, and what should happen next?

### 1.2 Why organisations commission it

| Trigger | Typical situation | What the inventory provides |
| --- | --- | --- |
| Regulatory enquiry | A regulator asks where customer data originates and who is accountable | Traceable asset → system → owner evidence and honest statements of what cannot yet be shown |
| Conflicting numbers | Risk, finance, marketing and compliance report different customer counts | A map of where each count is produced and which definitions and copies exist |
| Platform change | A migration, cloud move, merger or new platform is proposed | A "from" state for current-to-target comparison |
| Investment decisions | Funding is requested for data tooling | Evidence of which gaps are real and which are assumed |
| Audit finding | Internal audit reports unclear data ownership | A baseline against which closure is measured |

### 1.3 Business and architectural objectives

**Business objective:** give decision-makers a trustworthy picture of the
current data landscape so that investment, risk and change decisions rest on
evidence.

**Architectural objectives:**

- Document what exists, at a logical level, to an agreed scope.
- Make ownership, flows and dependencies visible.
- Assess the current state against stated principles and quality attributes.
- Identify gaps, risks and open questions, and recommend prioritised next steps.
- Create a baseline that requirements, target-state work and decision records can build on.

### 1.4 What this project is not

| It is not | Because |
| --- | --- |
| A technology catalogue | The unit of analysis is capability, domain, asset, flow and accountability, not product |
| A target-state design | Designing the target here hides the evidence; it belongs to modules 2D.2 and 2D.3 |
| A data profiling or data quality exercise | No customer-level data is read; only metadata and documented facts are collected |
| A schema, performance or tooling review | Explicitly out of scope (roadmap Section 7.2) |
| An audit opinion | The output is evidence-based observation, not assurance |

### 1.5 Success criteria

The project succeeds when a reviewer who did not do the work agrees that the
evidence supports the conclusions, and when a non-specialist can read the final
summary in ten minutes and understand its limits (roadmap Section 7.7).

---

## 2. How to use this file

The file supports two modes. Choose one before starting.

| | Mode A — Worked reference | Mode B — Real or realistic organisation |
| --- | --- | --- |
| Purpose | Study a complete, internally consistent example | Perform the assessment yourself |
| Source of facts | The Northbridge brief only; everything else is a labelled assumption | Documents, systems and interviews from your organisation |
| What you do | Read Section 6; run the checker; critique the example | Follow Section 5; use the templates in Section 8; produce your own D1–D10 |
| Output | Understanding and a critique list | A signed-off set of D1–D10 |

**Rules that apply in both modes**

1. **Never replace an unknown with an invented value.** `Unknown` is a valid, valuable finding.
2. **Do not design the target state.** Record recommendations as next steps only.
3. **Collect metadata only.** Do not copy personal or customer-level data into the inventory.
4. **If you substitute a real organisation,** mark what you observed versus what you assume, and respect confidentiality.

> **Honesty note for Mode A.** The Northbridge brief names only a handful of
> facts. All other values in Section 6 are *assessor hypotheses* to be verified,
> and carry the evidence label `Assumed` or `Unknown`. The worked reference
> shows the method, the structure and the traceability; it does not claim that
> a real bank looks like this.

---

## 3. Concepts applied

The project applies every lesson in the module. Use this table to see where
each concept reappears and to find the source lesson.

| Concept (lesson) | Where it is applied in the project |
| --- | --- |
| What data architecture is; scope; deliverables; distinguishing symptoms from root causes ([Lesson 01](../01-what-data-architecture-is-and-what-data-architects-do.md)) | Section 1 framing; Step 1 scope; Step 11 findings versus symptoms; the "five systems, different definitions of active customer" pattern behind F-01 and F-02 |
| Role boundaries and decision rights ([Lesson 02](../02-data-architecture-vs-data-engineering-and-solution-architecture.md)) | Section 4.1 project RACI; keeping out-of-scope items (schema design, tooling) with data engineering and solution architecture |
| Capabilities, domains, ownership ([Lesson 03](../03-business-capabilities-domains-and-data-ownership.md)) | Steps 3–6; D3 capability map and D4 ownership register; the ownership test; `UNKNOWN` as a legitimate status |
| Principles and quality attributes ([Lesson 04](../04-architecture-principles-and-quality-attributes.md)) | Steps 9–10; D6 principle lens; D7 assessment; target-versus-evidence discipline; drivers, constraints and assumptions kept apart |
| Lifecycle and governance ([Lesson 05](../05-data-architecture-lifecycle-and-governance.md)) | The project *is* lifecycle stage 1 (discover and assess current state); Step 9 documented versus practised; Step 13 validation; decision-record format for later hand-off |
| Frameworks and reference models ([Lesson 06](../06-enterprise-data-architecture-frameworks-and-reference-models.md)) | Section 4.5 documentation approach: adopt a minimal subset of framework ideas, adapt, defer, ignore; no claim of framework compliance |

**Mapping to the roadmap's project parts**

| Roadmap project part | Draws on | Steps | Deliverables |
| --- | --- | --- | --- |
| Scope, stakeholders, deliverables | Lessons 1, 2 | 1, 2 | D1, D2 |
| Capabilities, domains, ownership | Lesson 3 | 3–6 | D3, D4 |
| Flows and components | Lessons 1, 3 | 7, 8, 12 | D5 |
| Principles and quality assessment | Lesson 4 | 9, 10 | D6, D7 |
| Governance, gaps, recommendations | Lesson 5 | 9, 11, 13, 14 | D6, D8, D9, D10 |
| Choosing a documentation approach | Lesson 6 | 1, 12 | D1, D5 |

**Cross-check with practice question G7.12** (`practice-questions.md`): scope and
exclusions first (Step 1); dated sources and stakeholders (Step 2); capabilities
before systems (Steps 3–4); assets and owners (Steps 5–6); flows including
manual spreadsheets (Step 7); principles and whether practised (Step 9); quality
against targets or "no target / no evidence" (Step 10); risks linked to findings
(Step 11); validation of disagreements (Step 13); prioritised recommendations
(Step 14); no target-state design anywhere.

---

## 4. Project governance and conventions

### 4.1 Roles and decision rights (RACI)

`R` responsible, `A` accountable (one per row), `C` consulted, `I` informed.

| Decision or activity | Sponsor (ST-01) | Lead assessor (ST-14) | Domain owners (ST-02 to ST-04) | Engineering leads (ST-10) | Compliance (ST-08) | Internal Audit (ST-12) |
| --- | --- | --- | --- | --- | --- | --- |
| Approve scope and exclusions | A | R | C | C | C | I |
| Provide documents and access | A | C | R | R | R | I |
| Validate capability and system inventory | I | R | A | C | I | I |
| Confirm asset ownership | C | R | A | C | C | I |
| Accept findings as factually correct | C | R | A | C | C | I |
| Independent review of evidence against conclusions | I | C | I | I | I | A |
| Approve prioritised next steps | A | R | C | C | C | I |

The assessor *recommends and records*; the business *confirms ownership*. The
assessor must never assign ownership by inference from system custody (Lesson 03).

### 4.2 Assessment ratings, confidence and scoring

**Confidence**

| Level | Meaning |
| --- | --- |
| High | Supported by observed evidence and confirmed by the responsible person |
| Medium | Reported by a stakeholder or documented, not yet cross-checked |
| Low | Assumed, inferred or based on absence of evidence |

**Quality and principle ratings**

| Rating | Meaning |
| --- | --- |
| Meets | Evidence shows the stated target is satisfied |
| Partially meets | Evidence shows part of the target is satisfied |
| Does not meet | Evidence shows the target is not satisfied |
| Indicative concern | Symptoms are reported, but evidence is insufficient to rate against a target |
| Not rated (no target) | No target exists; recorded as a finding in itself |
| Not rated (no evidence) | A target may exist, but no evidence has been seen |

**Register scoring.** Impact and likelihood use a three-point scale
(`1` Low, `2` Medium, `3` High). Likelihood means *the likelihood that the
condition causes harm or blocks a decision within twelve months if left
unaddressed*. **Score = Impact × Likelihood** (1–9).

**Next-step priority** is derived mechanically from the highest score among the
register items a step addresses, and its effort (`S` ≤ 5 person-days,
`M` 6–15, `L` > 15):

| Priority | Rule |
| --- | --- |
| P1 | Highest score ≥ 6 and effort S or M |
| P2 | Highest score ≥ 6 and effort L; or highest score 3–5 and effort S or M |
| P3 | All other combinations |

### 4.3 Evidence rules

| Label | Definition | Example |
| --- | --- | --- |
| **Observed** | You saw it first-hand (system, configuration, log, document you read) | A job schedule you inspected |
| **Reported** | A stakeholder or document told you; you have not verified it | "Marketing reports its own customer count" (scenario) |
| **Assumed** | You inferred it; it needs verification | "The CRM holds communication preferences" |
| **Unknown** | No information; also used where a value cannot be established | Hosting model not provided |

Mandatory handling rules:

- **Row-level label.** Each inventory row carries one `Evidence` label. The label
  is the **weakest** label among the row's material claims.
- **Source.** Each row names its source (document ID, interview, or "Scenario brief").
- **Conflicts.** If two sources disagree, record both and mark the item
  `Disputed`; do not choose silently.
- **Staleness.** An old diagram is evidence of intent, not of current reality.
  Record author and date for every document.
- **Gaps.** A claim with no evidence is either removed or labelled `Unknown`.

### 4.4 Naming and ID conventions

IDs are stable, two-digit and never reused. Cross-references use IDs only, which
makes traceability machine-checkable (Appendix B).

| Prefix | Object | Prefix | Object |
| --- | --- | --- | --- |
| ST | Stakeholder | FLW | Data flow |
| DOC | Document request | CMP | Logical component |
| SYS | System (EXT = external party) | GOV | Governance item |
| CAP | Business capability | PL | Principle-lens row |
| DOM | Domain | QA | Quality-attribute assessment |
| AST | Data asset | F | Finding |
| R | Register item | N | Next step |
| VL | Validation-log entry | | |

### 4.5 Documentation approach (applying Lesson 06)

The roadmap leaves the choice of documentation approach to the learner. This
project uses a deliberately **minimal, adapted** approach:

| Framework idea (examples from Lesson 06) | Decision | Reason |
| --- | --- | --- |
| Separate business, data and technology views (a common idea in enterprise architecture frameworks; Lesson 06) | **Adopt** at logical level: business (capabilities, domains), data (assets, ownership), technology (systems, components) | Gives each audience a view without product detail |
| Knowledge-area checklist (data management bodies of knowledge) | **Adapt** as a *prompt* for Step 9 governance items (ownership, classification, quality, change control) | Prevents omissions without creating a checklist bureaucracy |
| Full architecture development method and artefact catalogue | **Defer** | Disproportionate for a baseline; revisit in module 2D.15 |
| Claims of framework compliance | **Ignore** | A framework does not confer compliance or prove a design sound |

This is a documentation choice, not a framework adoption. Use the organisation's
own vocabulary where it exists (Lesson 06: keep terminology consistent without
renaming everything).

### 4.6 Confidentiality and handling

- Store **metadata only**: names, roles, systems, classifications, definitions.
  Never copy customer records, credentials, connection strings or personal data into any artefact.
- Use roles, not named individuals, in shared artefacts, unless the organisation's policy says otherwise.
- Mark the document with the organisation's classification; restrict distribution to the review group.
- Record the document version and date on every artefact (completion gate requirement).

### 4.7 Suggested workspace layout (Mode B)

Use this layout for a real assessment. In Mode A, Section 6 contains all artefacts
inline, so no extra files are needed. **Creating this layout is optional and is not
part of this repository change.**

```text
northbridge-current-state-inventory/        # replace with the organisation name
├── 00-governance/
│   ├── d1-scope-and-assumptions.md         # D1, evidence rules, change log
│   ├── stakeholder-and-document-register.md
│   └── validation-log.md                   # Step 13
├── 01-inventories/
│   ├── systems.csv                         # D2
│   ├── capabilities-and-domains.csv        # D3
│   ├── data-assets.csv                     # D4
│   ├── ownership.csv                       # D4
│   ├── data-flows.csv                      # D5 source data
│   └── components.csv                      # Step 8
├── 02-views/
│   └── current-state-diagram.md            # D5 (text diagram, legend, version, date)
├── 03-assessment/
│   ├── principles-and-governance.md        # D6
│   ├── quality-attribute-assessment.md     # D7
│   └── gap-risk-register.csv               # D8
├── 04-findings/
│   ├── findings-and-next-steps.md          # D9
│   └── final-assessment-summary.md         # D10
├── 05-evidence/                            # dated source documents, interview notes
└── tools/
    └── check_inventory.py                  # Appendix B (adapt column names to your files)
```

Design rationale: separate *inventories* (facts) from *views* (pictures) from
*assessment* (judgement) from *findings* (decisions support), so that each layer
can be reviewed, versioned and challenged independently. Keep one source of truth
per item; the diagram and the inventory must never be edited separately.

---

## 5. Execution plan

### 5.1 Timeline and effort (planning estimate, mid-sized organisation)

| Week | Steps | Main outcome | Effort (person-days, indicative) |
| --- | --- | --- | --- |
| 1 | 1, 2 | Signed-off scope; stakeholder list; document requests issued | 3–4 |
| 2 | 3, 4, 5 | Capability map, system inventory, asset list drafted | 6–8 |
| 3 | 6, 7, 8 | Ownership, flows, components drafted | 6–8 |
| 4 | 9, 10, 11 | Governance observations, quality assessment, register | 5–7 |
| 5 | 12, 13 | Current-state view; validation sessions held | 5–6 |
| 6 | 14 and hand-off | Prioritised next steps; final summary; presentation | 3–4 |

Total indicative effort: **28–37 person-days** of assessor time, plus roughly
0.5–1 day per interviewed stakeholder. These are planning figures, not measured
results; re-estimate after Week 1.

### 5.2 Definition of ready and definition of done

| | Criteria |
| --- | --- |
| **Ready to start** | Sponsor named; scope question agreed; access route to documents and a named contact per system; confidentiality rules agreed |
| **Done** | Completion gate (Section 7.5) fully met; all deliverables D1–D10 dated; reviewer agrees evidence supports conclusions |

### 5.3 The fourteen steps

Throughout, label every statement **Observed**, **Reported**, **Assumed** or
**Unknown**. Never fill a gap with an invented fact.

#### Step 1 — Define assessment objective, scope and boundaries

- **Why it matters:** prevents unbounded work and mismatched expectations.
- **Inputs:** sponsor goals, time frame, access, regulatory or audit triggers.
- **Activities:**
  1. State the objective in one sentence and the decision it supports.
  2. List in-scope domains, systems and time frame; list explicit exclusions.
  3. Record assumptions, dependencies and the evidence rules (Section 4.3).
  4. Agree the level of detail (logical, not physical).
- **Output:** D1 Assessment scope and assumptions.
- **How to verify:** the sponsor confirms scope in writing; every exclusion is stated.
- **Pitfalls:** scope that reads as "everything about data"; omitting exclusions; skipping the time frame.
- **Draws on:** Lessons 01, 02.

#### Step 2 — Identify stakeholders and gather documentation

- **Why it matters:** stakeholders are sources of evidence and the reviewers of findings.
- **Inputs:** org charts, existing diagrams, policies, system lists.
- **Activities:**
  1. List stakeholders with role, interest and what each will validate.
  2. Issue a document request list (Section 8.2); log each request and its status.
  3. Record author and date for each received document.
  4. Log documents that do not exist as a finding input, not as a blocker.
- **Output:** stakeholder list; document register (part of D2).
- **How to verify:** each stakeholder has a role and a purpose; each document has a date and source.
- **Pitfalls:** treating old diagrams as current truth; interviewing only senior people.
- **Draws on:** Lessons 01, 02.

#### Step 3 — Inventory business capabilities and domains

- **Why it matters:** anchors data in business terms. Starting from the system list rebuilds the existing silos.
- **Inputs:** capability models, process lists, interviews.
- **Activities:**
  1. Build a two-level capability map using business language (not application names).
  2. Group capabilities into proposed domains by meaning and decision rights.
  3. Allow a capability to *relate* to several domains but have one primary domain.
- **Output:** capability and domain inventory (D3).
- **How to verify:** domain owners recognise their capabilities and boundaries.
- **Pitfalls:** naming capabilities after systems; forcing one domain per capability.
- **Draws on:** Lesson 03 (sections 4.1–4.6, 5.1).

#### Step 4 — Identify major data-producing and data-consuming systems

- **Why it matters:** defines the landscape the inventory covers.
- **Inputs:** system lists, CMDB extracts, interviews.
- **Activities:**
  1. List systems; tag role (system of record, consumer, copy, reporting).
  2. Map each capability to supporting systems or flag **"No system identified"**.
  3. Distinguish a system of record from copies and from reports.
- **Output:** system inventory and capability–system mapping (D2, D3).
- **How to verify:** every capability maps to a system or is explicitly flagged.
- **Pitfalls:** "more than one system" is not automatically a failure; the risk is unexamined duplication and unclear authority.
- **Draws on:** Lesson 03 (5.2, detecting gaps and overlaps).

#### Step 5 — Identify important data entities, datasets and assets

- **Why it matters:** shows what data matters.
- **Inputs:** data dictionaries, schemas, reports, interviews.
- **Activities:**
  1. Choose a **small set of important assets** and state how you chose (customer impact, regulatory use, number of consumers).
  2. For each, record domain, authoritative system, where else it is held, sensitivity (as classified or Unknown), refresh frequency, known quality concerns.
  3. Treat derived assets (a count, a score, a conformed table) as assets in their own right.
- **Output:** data asset inventory (D4).
- **How to verify:** each asset links to a system and a domain.
- **Pitfalls:** exhaustive lists with no prioritisation; asserting sensitivity not evidenced.
- **Draws on:** Lesson 03 (4.4, 5.2, 6.2).

#### Step 6 — Map ownership, stewardship and accountability

- **Why it matters:** reveals accountability gaps.
- **Inputs:** governance documents, role descriptions, interviews.
- **Activities:**
  1. For each asset record data owner, steward, producers, consumers, decision authority for change.
  2. Apply the ownership test (Lesson 03 quick reference): exact asset and meaning, capability, authoritative domain, who creates/consumes/corrects, who bears consequences, what evidence confirms the role.
  3. Use status `Confirmed`, `Proposed`, `Disputed` or `Unknown`. **A candidate role is a proposal, not an owner.**
- **Output:** ownership inventory (D4).
- **How to verify:** no asset has an unmarked owner field; unknowns are explicit and carry a resolution action.
- **Pitfalls:** inferring ownership from system custody; assuming the owner is the steward.
- **Draws on:** Lesson 03 (5.5, 5.6, 6.1–6.8).

#### Step 7 — Document ingestion, integration, movement and consumption

- **Why it matters:** shows how data flows and where copies arise.
- **Inputs:** integration lists, interface specifications, job inventories.
- **Activities:**
  1. Record each flow: source, target, assets moved, method (batch, API, stream, file, manual), frequency, known controls.
  2. **Include manual flows and spreadsheets**; they frequently carry the risk.
  3. Trace sample flows end to end with a system owner.
- **Output:** data flow inventory and draft diagram (D5 input).
- **How to verify:** at least three sample flows traced with a knowledgeable person; any missing flow is added.
- **Pitfalls:** documenting only automated pipelines; drawing flows from old diagrams without checking.
- **Draws on:** Lessons 01, 03.

#### Step 8 — Identify storage, processing and serving components

- **Why it matters:** locates where data rests and is transformed.
- **Inputs:** platform inventories, architecture documents.
- **Activities:**
  1. List stores, processing and serving layers at a **logical** level.
  2. Link each component to the assets it holds and the systems that host it.
- **Output:** component inventory.
- **How to verify:** each component links to the assets it holds; each asset is held by at least one component.
- **Pitfalls:** expanding into product configuration; omitting end-user computing.
- **Draws on:** Lessons 01, 06.

#### Step 9 — Document principles, standards and governance arrangements

- **Why it matters:** establishes the rules that apply, and shows whether they are applied.
- **Inputs:** policies, standards, forum charters, decision records.
- **Activities:**
  1. List each principle, standard, forum and decision right; cite the source document.
  2. Record separately whether each is **documented** and **practised**.
  3. Where none is evidenced, use the Lesson 04 principle set as an explicit *assessment lens*, stating that it is not adopted by the organisation.
- **Output:** principles and governance observations (D6).
- **How to verify:** each item cites a source; unapplied items are flagged.
- **Pitfalls:** treating a published policy as evidence of practice.
- **Draws on:** Lessons 04, 05.

#### Step 10 — Assess against quality attributes and business requirements

- **Why it matters:** turns description into assessment.
- **Inputs:** targets (if any), incident history, audit findings.
- **Activities:**
  1. Select the quality attributes that matter for the in-scope assets (Lesson 04 section 4.4).
  2. Record the target or **"none evidenced"**; rate using the scale in Section 4.2; record evidence and confidence.
  3. Treat drivers, constraints, assumptions and preferences as different things.
- **Output:** quality-attribute assessment (D7).
- **How to verify:** each rating cites evidence or is marked "Not rated (no evidence)".
- **Pitfalls:** rating against an invented target; averaging away tail problems.
- **Draws on:** Lesson 04 (4.4, 4.5, 5.2–5.5).

#### Step 11 — Identify gaps, risks, constraints, dependencies and open questions

- **Why it matters:** surfaces what needs action.
- **Inputs:** outputs of Steps 3–10.
- **Activities:**
  1. Write **findings** (facts with evidence and confidence), distinct from symptoms and opinions.
  2. Derive register items; link each to at least one finding; score using Section 4.2.
  3. Revisit scope if findings show it was wrong.
- **Output:** findings; gap, risk, dependency and open-questions register (D8).
- **How to verify:** every register item traces to a finding.
- **Pitfalls:** a risk without a finding is an opinion; do not include it.
- **Draws on:** Lessons 01 (6.1, 6.3), 04, 05.

#### Step 12 — Create the current-state view and supporting inventory

- **Why it matters:** provides the shared picture.
- **Inputs:** all prior artefacts.
- **Activities:**
  1. Produce a one-page logical diagram with legend, version and date; flows show direction, method and frequency.
  2. Consolidate the inventories; run the consistency checker.
- **Output:** current-state architecture view (D5) and consolidated inventory.
- **How to verify:** diagram elements trace to inventory entries and vice versa; no orphan items.
- **Pitfalls:** a diagram that contains elements not in the inventory; unreadable density.
- **Draws on:** Lessons 01, 06.

#### Step 13 — Validate with stakeholders

- **Why it matters:** corrects errors and builds ownership.
- **Inputs:** draft artefacts.
- **Activities:**
  1. Run review sessions per domain; walk through findings, not just diagrams.
  2. Record corrections and **disagreements**; do not silently resolve them.
  3. Update artefacts and the version history.
- **Output:** validation log.
- **How to verify:** each material finding has a reviewer and a recorded response.
- **Pitfalls:** validating only with the sponsor; recording approval without recording challenge.
- **Draws on:** Lesson 05 (5.4, 6.3).

#### Step 14 — Produce prioritised observations and next steps

- **Why it matters:** makes the work actionable.
- **Inputs:** validated register and findings.
- **Activities:**
  1. Define few, specific next steps; link each to register items.
  2. Rank using the priority rule (Section 4.2).
  3. Write the executive summary (D10), stating caveats and limits.
- **Output:** findings and next-steps summary (D9); final assessment summary (D10).
- **How to verify:** each recommendation traces to a gap or risk.
- **Pitfalls:** recommending a technology; recommending designs; hidden caveats.
- **Draws on:** Lessons 05, 06.

---

## 6. Worked reference — Northbridge Bank

> **Everything in this section is illustrative.** The Northbridge brief states
> only the facts in D1. All other values are `Assumed` or `Unknown` and must be
> verified in a real assessment. No person is named. No product is named. Run the
> checker (Appendix B) after any edit.

### 6.1 D1 — Assessment scope and assumptions (Step 1)

**Version:** 1.1 · **Date:** 2026-10-21 · **Sponsor:** Head of Data (ST-01)

**Facts stated in the brief (Reported):**

- Over fifteen years the bank accumulated a core banking system, a separate cards platform, a CRM, a loan origination system, an enterprise data warehouse, a data lake created three years ago, and team-built reporting databases and spreadsheets.
- Risk, finance, marketing and compliance each report different customer counts.
- A regulator has asked for clearer evidence of where customer data comes from and who is accountable for it.

| Element | Statement |
| --- | --- |
| Objective | Give the sponsor a trustworthy, evidence-labelled picture of customer, account and transaction data so the regulator's enquiry and conflicting customer counts can be addressed on evidence |
| Decision supported | Which gaps to close first, and which questions to put to accountable owners |
| In scope | Customer, account and transaction data across the ten systems in 6.2; their producers and consumers; flows into reporting and analytics; ownership and governance arrangements |
| Out of scope | Detailed schema design; performance tuning; tooling selection; target-state design; implementation; reading or profiling customer-level data; legal interpretation of the regulator's request |
| Time frame | Current state as of the assessment date; incidents and audit findings for the last twelve months where available |
| Level of detail | Logical (capability, domain, asset, flow, component); no physical configuration |
| Evidence rules | Section 4.3 |
| Deliverables | D1–D10 (sections 6.1–6.11) |

**Assumptions**

| ID | Assumption | Impact if false | Validation |
| --- | --- | --- | --- |
| A1 | The ten systems in 6.2 are the complete in-scope set | Missing flows and owners | Step 2 CMDB extract (DOC-01); Step 13 review |
| A2 | Core banking is the system of record for deposit accounts and posted transactions | Asset authority shifts | Step 6 interviews |
| A3 | Departmental reporting databases and spreadsheets are fed from the warehouse or the lake | Hidden direct extracts | Step 7 sample-flow tracing |
| A4 | Customer count variants differ by definition, scope, as-of date or defect | Misdirected remediation | Question R-12 |
| A5 | No enterprise principles or ownership policy exist until documents are received | Findings F-08, F-09 become void | Document requests DOC-07, DOC-08 |

### 6.2 D2 — Stakeholder, document and system inventory (Steps 2 and 4)

**Stakeholders**

| ID | Stakeholder (role) | Group | Interest in the assessment | Role in assessment | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- |
| ST-01 | Head of Data | Sponsor | Trusted picture for investment and risk decisions | Sponsor; approves scope and next steps | Assumed | Scenario brief, assumed stakeholder list |
| ST-02 | Retail domain owner | Business | Accountable for retail customer and account outcomes | Validates capabilities, assets, ownership for DOM-01 and DOM-02 | Assumed | Scenario brief, assumed stakeholder list |
| ST-03 | Lending domain owner | Business | Accountable for loan origination and servicing outcomes | Validates DOM-03 content | Assumed | Scenario brief, assumed stakeholder list |
| ST-04 | Cards domain owner | Business | Accountable for card products and card transactions | Validates DOM-04 content | Assumed | Scenario brief, assumed stakeholder list |
| ST-05 | Head of Risk | Business consumer | Reports its own customer count; uses customer risk rating | Provides evidence on AST-11 and its count | Reported | Scenario brief: risk reports a customer count |
| ST-06 | Head of Finance | Business consumer | Reports its own customer count; financial reporting | Provides evidence on finance reporting flows | Reported | Scenario brief: finance reports a customer count |
| ST-07 | Head of Marketing | Business consumer | Reports its own customer count; campaign segments | Provides evidence on marketing data | Reported | Scenario brief: marketing reports a customer count |
| ST-08 | Head of Compliance | Business consumer | Reports its own customer count; regulator liaison | Provides regulatory return evidence | Reported | Scenario brief: compliance reports a count and the regulator enquiry |
| ST-09 | Information Security lead | Control function | Classification, access and exposure of copies | Reviews sensitivity and access findings | Assumed | Scenario brief, assumed stakeholder list |
| ST-10 | Engineering leads (core, cards, CRM, loans, data platform) | Technology | Own technical operation of systems and flows | Provide interface and job inventories | Assumed | Scenario brief, assumed stakeholder list |
| ST-11 | Operations lead | Operations | Runs batch jobs, manual processes, incidents | Provides incident and manual-process evidence | Assumed | Scenario brief, assumed stakeholder list |
| ST-12 | Internal Audit | Independent review | Independent challenge of evidence | Reviews that evidence supports conclusions | Assumed | Scenario brief, assumed stakeholder list |
| ST-13 | Regulator (external) | External | Requested evidence of data origin and accountability | None directly; requirements arrive via ST-08 | Reported | Scenario brief: regulator enquiry |
| ST-14 | Lead assessor (Data Architect) | Assessor | Produces and defends the inventory | Performs the assessment | Assumed | Project role |

**Document request register** (status shows the worked reference holds no documents; every row would carry author and date when received)

| ID | Document requested | Requested from | Purpose | Status | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- |
| DOC-01 | Systems list or CMDB extract for in-scope systems | ST-10 | Confirms system set and owners (Step 4) | Requested, not received | Assumed | Assessor request list |
| DOC-02 | Business capability model and process list | ST-01 | Capability map (Step 3) | Requested, not received | Assumed | Assessor request list |
| DOC-03 | Existing architecture diagrams for core, EDW and lake | ST-10 | Flow and component evidence (Steps 7 and 8) | Requested, not received | Assumed | Assessor request list |
| DOC-04 | Interface and integration inventory; job schedules | ST-10 | Flow evidence (Step 7) | Requested, not received | Assumed | Assessor request list |
| DOC-05 | Data dictionary or glossary including customer definitions | ST-02 | Definition evidence for AST-04 and AST-13 | Requested, not received | Assumed | Assessor request list |
| DOC-06 | Report definitions for the four customer counts | ST-05 | Compare the four count variants | Requested, not received | Assumed | Assessor request list |
| DOC-07 | Data governance policies: ownership, classification, quality | ST-08 | Governance observations (Step 9) | Requested, not received | Assumed | Assessor request list |
| DOC-08 | Architecture principles, standards, decision records | ST-01 | Principles and decision rights (Step 9) | Requested, not received | Assumed | Assessor request list |
| DOC-09 | Regulator request and any previous responses | ST-08 | Exact scope of the enquiry (R-15) | Requested, not received | Assumed | Assessor request list |
| DOC-10 | Incident and data-quality issue logs, last twelve months | ST-11 | Quality-attribute evidence (Step 10) | Requested, not received | Assumed | Assessor request list |
| DOC-11 | Internal audit reports touching data | ST-12 | Known findings and targets | Requested, not received | Assumed | Assessor request list |
| DOC-12 | Register of end-user spreadsheets and departmental databases | ST-08 | Shadow-flow evidence (Step 7) | Requested, not received | Assumed | Assessor request list |

**System inventory** (`EXT-01` is an external party included for flow completeness)

| ID | System (logical name) | Capabilities supported | Role | Business owner | Technical owner | Main data held (domains) | Hosting | Lifecycle | Interfaces (flows) | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SYS-01 | Core Banking Platform | CAP-02; CAP-03; CAP-06; CAP-07 | System of record for deposit accounts and posted transactions (A2) | Unknown (candidate ST-02) | Unknown (candidate ST-10) | DOM-01; DOM-02 | Unknown | Active (assumed) | FLW-01; FLW-05; FLW-11 | Assumed | Scenario brief: system exists; role and data are hypotheses |
| SYS-02 | Cards Platform | CAP-02; CAP-05; CAP-06; CAP-07 | System of record for card accounts and card transactions | Unknown (candidate ST-04) | Unknown (candidate ST-10) | DOM-01; DOM-04 | Unknown | Active (assumed) | FLW-02; FLW-05 | Assumed | Scenario brief: system exists; role and data are hypotheses |
| SYS-03 | Customer Relationship Management (CRM) | CAP-02; CAP-10 | Holds customer contact, preference and interaction data; role versus core banking unverified | Unknown (candidate ST-02) | Unknown (candidate ST-10) | DOM-01 | Unknown | Active (assumed) | FLW-03; FLW-05; FLW-11; FLW-12; FLW-13 | Assumed | Scenario brief: system exists; role and data are hypotheses |
| SYS-04 | Loan Origination System | CAP-02; CAP-04; CAP-08 | System of record for loan applications; loan servicing system unverified | Unknown (candidate ST-03) | Unknown (candidate ST-10) | DOM-01; DOM-03 | Unknown | Active (assumed) | FLW-04; FLW-05 | Assumed | Scenario brief: system exists; role and data are hypotheses |
| SYS-05 | Enterprise Data Warehouse (EDW) | CAP-09; CAP-11; CAP-12 | Integrated reporting copy; not a system of record | Unknown (candidate ST-01) | Unknown (candidate ST-10) | DOM-01; DOM-02; DOM-03; DOM-04 | Unknown | Active (assumed) | FLW-01; FLW-02; FLW-03; FLW-04; FLW-06; FLW-07; FLW-09 | Assumed | Scenario brief: system exists; role and data are hypotheses |
| SYS-06 | Data Lake (created three years ago) | CAP-12 | Analytical copy; purpose versus EDW unverified | Unknown (candidate ST-01) | Unknown (candidate ST-10) | DOM-01; DOM-02; DOM-03; DOM-04 | Unknown | Active (assumed) | FLW-05; FLW-08 | Assumed | Scenario brief: system exists; role and data are hypotheses |
| SYS-07 | Risk reporting database (team-built) | CAP-08 | Departmental reporting copy | Unknown (candidate ST-05) | Unknown | DOM-01; DOM-02; DOM-03; DOM-05; DOM-06 | Unknown | Active (assumed) | FLW-06; FLW-10 | Assumed | Scenario brief: team-built databases exist; this instance is a hypothesis |
| SYS-08 | Finance reporting database (team-built) | CAP-11 | Departmental reporting copy | Unknown (candidate ST-06) | Unknown | DOM-01; DOM-02; DOM-03; DOM-06 | Unknown | Active (assumed) | FLW-07 | Assumed | Scenario brief: team-built databases exist; this instance is a hypothesis |
| SYS-09 | Marketing analytics database (team-built) | CAP-10 | Departmental reporting and segmentation copy | Unknown (candidate ST-07) | Unknown | DOM-01; DOM-06 | Unknown | Active (assumed) | FLW-08; FLW-12; FLW-13 | Assumed | Scenario brief: team-built databases exist; this instance is a hypothesis |
| SYS-10 | Compliance end-user spreadsheets | CAP-09 | Prepares regulatory return and compliance counts; end-user computing | Unknown (candidate ST-08) | Unknown | DOM-01; DOM-05; DOM-06 | Unknown | Active (assumed) | FLW-09; FLW-10; FLW-14 | Assumed | Scenario brief: spreadsheets exist; this instance is a hypothesis |
| EXT-01 | Regulator (external party) | None (external party) | Recipient of regulatory submissions | n/a (external) | n/a (external) | None (external party) | n/a (external) | n/a (external) | FLW-14 | Reported | Scenario brief: regulator enquiry |

### 6.3 D3 — Business capability and domain inventory (Steps 3 and 4)

The capability and domain model extends the ten-capability baseline of Lesson 03
with lending, cards, finance reporting and analytics to match the Northbridge
scenario. Domains are **proposals to validate**; a real bank may split, combine
or rename them.

**Domains**

| ID | Domain | Meaning and boundary | Candidate accountable role | Capabilities | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- |
| DOM-01 | Customer and Servicing | Customer identity, contact, preferences, onboarding facts, service and communication | ST-02 Retail domain owner (proposal) | CAP-01; CAP-02; CAP-10 | Assumed | Lesson 03 baseline, adapted; unvalidated |
| DOM-02 | Accounts and Transactions | Deposit account relationships, balances, posted transactions | ST-02 Retail domain owner (proposal) | CAP-03; CAP-06; CAP-07 | Assumed | Lesson 03 baseline, adapted; unvalidated |
| DOM-03 | Lending | Loan applications, decisions, loan accounts and schedules | ST-03 Lending domain owner (proposal) | CAP-04 | Assumed | Scenario brief: lending domain owner; boundary unvalidated |
| DOM-04 | Cards | Card products, card accounts, card authorisations and settlements | ST-04 Cards domain owner (proposal) | CAP-05 | Assumed | Scenario brief: cards domain owner; boundary unvalidated |
| DOM-05 | Risk and Compliance | Risk ratings, compliance counts, regulatory returns | ST-08 Head of Compliance (proposal) | CAP-08; CAP-09 | Assumed | Lesson 03 risk and reporting extension; unvalidated |
| DOM-06 | Finance and Management Reporting | Financial reporting, management information, enterprise analytics, derived measures | ST-06 Head of Finance (proposal) | CAP-11; CAP-12 | Assumed | Assessor hypothesis; unvalidated |

**Two-level capability map and system mapping**

| ID | L1 group | L2 capability | Domain | Supporting systems | Mapping note | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CAP-01 | Customer lifecycle | Acquire and onboard customers | DOM-01 | No system identified | **Mapping gap, not proof of absence:** onboarding may sit in the CRM, core or an unlisted system; confirm in Step 4 | Unknown | DOC-01 requested |
| CAP-02 | Customer lifecycle | Maintain customer information | DOM-01 | SYS-01; SYS-02; SYS-03; SYS-04 | Four systems each assumed to hold customer attributes; authority unknown (see F-04) | Assumed | Assessor hypothesis; DOC-01 and DOC-04 requested |
| CAP-03 | Account and product | Open and maintain deposit accounts | DOM-02 | SYS-01 | Single supporting system assumed | Assumed | Assessor hypothesis (A2) |
| CAP-04 | Account and product | Originate and service loans | DOM-03 | SYS-04 | Servicing system unverified | Assumed | Assessor hypothesis |
| CAP-05 | Account and product | Issue and manage cards | DOM-04 | SYS-02 | Single supporting system assumed | Assumed | Assessor hypothesis |
| CAP-06 | Payments and activity | Record and post transactions | DOM-02 | SYS-01; SYS-02 | Deposit and card transactions are separate event sources | Assumed | Assessor hypothesis |
| CAP-07 | Payments and activity | Manage balances and statements | DOM-02 | SYS-01; SYS-02 | Balance is derived under account rules; reconcile to posted events | Assumed | Assessor hypothesis |
| CAP-08 | Risk and control | Assess customer and credit risk | DOM-05 | SYS-04; SYS-07 | Credit decision in loans; risk rating in risk database | Assumed | Assessor hypothesis |
| CAP-09 | Risk and control | Meet regulatory reporting obligations | DOM-05 | SYS-05; SYS-10 | Cross-domain capability; reporting authority to confirm | Assumed | Scenario brief: regulator enquiry; systems hypothesised |
| CAP-10 | Insight and engagement | Manage customer communications and campaigns | DOM-01 | SYS-03; SYS-09 | Marketing consumes preferences; does not own them | Assumed | Assessor hypothesis |
| CAP-11 | Insight and engagement | Produce financial and management reporting | DOM-06 | SYS-05; SYS-08 | Counts produced here conflict with other functions | Assumed | Scenario brief: finance reports a count |
| CAP-12 | Insight and engagement | Provide enterprise analytics | DOM-06 | SYS-05; SYS-06 | Two analytical platforms assumed to coexist | Assumed | Scenario brief: warehouse and lake exist |

### 6.4 D4 — Data asset and ownership inventory (Steps 5 and 6)

**Selection rationale (Step 5).** Assets were chosen because they (a) concern
customer, account or transaction data, (b) feed the regulator question or the
conflicting counts, or (c) are held in more than one system. Fourteen assets
were chosen for this worked reference; any further assets are deferred and would
be added through change control on D1.

**Data asset inventory**

| ID | Asset | Description | Domain | Authoritative system | Held in | Sensitivity (as classified) | Refresh | Known quality concerns | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AST-01 | Customer identity and core profile | Name, date of birth, identification attributes | DOM-01 | Unknown | SYS-01; SYS-02; SYS-03; SYS-04; SYS-05; SYS-06 | Unknown (not classified in evidence) | Unknown | Copies in several systems may diverge (Assumed) | Assumed | Assessor hypothesis; DOC-05 requested |
| AST-02 | Customer contact details | Address, phone, email | DOM-01 | Unknown | SYS-01; SYS-02; SYS-03; SYS-04; SYS-05; SYS-06; SYS-09 | Unknown (not classified in evidence) | Unknown | Seven copies may diverge (Assumed) | Assumed | Assessor hypothesis; DOC-05 requested |
| AST-03 | Communication preference and consent | Channel and consent choices | DOM-01 | SYS-03 | SYS-03; SYS-05; SYS-06; SYS-09 | Unknown (not classified in evidence) | Unknown | None evidenced | Assumed | Assessor hypothesis |
| AST-04 | Customer segment and active-customer flag | Derived indicator of customer activity | DOM-01 | Unknown | SYS-03; SYS-05; SYS-09 | Unknown (not classified in evidence) | Unknown | Multiple definitions of active customer suspected (Assumed) | Assumed | Assessor hypothesis; Lesson 01 pattern |
| AST-05 | Deposit account and balance | Account record and balance | DOM-02 | SYS-01 | SYS-01; SYS-05; SYS-06 | Unknown (not classified in evidence) | Daily to EDW (Assumed) | None evidenced | Assumed | Assessor hypothesis (A2) |
| AST-06 | Posted deposit transaction | Posted monetary event | DOM-02 | SYS-01 | SYS-01; SYS-05; SYS-06; SYS-07; SYS-08 | Unknown (not classified in evidence) | Daily to EDW (Assumed) | None evidenced | Assumed | Assessor hypothesis (A2) |
| AST-07 | Card account and status | Card account record | DOM-04 | SYS-02 | SYS-02; SYS-05; SYS-06 | Unknown (not classified in evidence) | Daily to EDW (Assumed) | None evidenced | Assumed | Assessor hypothesis |
| AST-08 | Card transaction | Authorised and settled card events | DOM-04 | SYS-02 | SYS-02; SYS-05; SYS-06 | Unknown (not classified in evidence) | Daily to EDW (Assumed) | Authorisation versus settlement status semantics unverified | Assumed | Assessor hypothesis |
| AST-09 | Loan application and decision | Application and credit decision | DOM-03 | SYS-04 | SYS-04; SYS-05; SYS-06 | Unknown (not classified in evidence) | Daily to EDW (Assumed) | None evidenced | Assumed | Assessor hypothesis |
| AST-10 | Loan account and repayment schedule | Loan account state | DOM-03 | SYS-04 | SYS-04; SYS-05; SYS-06; SYS-07; SYS-08 | Unknown (not classified in evidence) | Daily to EDW (Assumed) | Servicing system of record unverified | Assumed | Assessor hypothesis |
| AST-11 | Customer risk rating | Derived rating used by risk | DOM-05 | SYS-07 | SYS-07; SYS-10 | Unknown (not classified in evidence) | Unknown | Model, version and approved use not evidenced | Assumed | Assessor hypothesis |
| AST-12 | Regulatory customer return | Customer data prepared for the regulator | DOM-05 | SYS-10 | SYS-10 | Unknown (not classified in evidence) | Per regulatory calendar (Unknown) | Prepared in spreadsheets; controls not evidenced | Assumed | Scenario brief: regulator enquiry; preparation method hypothesised |
| AST-13 | Customer count (reported measure) | Customer counts reported by four functions | DOM-06 | Unknown | SYS-07; SYS-08; SYS-09; SYS-10 | Unknown (not classified in evidence) | Unknown | Four reported variants differ (Reported) | Reported | Scenario brief: four functions report different counts |
| AST-14 | Conformed customer view (EDW) | Warehouse integrated customer data | DOM-01 | Unknown | SYS-05; SYS-07; SYS-08; SYS-10 | Unknown (not classified in evidence) | Daily (Assumed) | Derived copy; relation to sources unverified | Assumed | Assessor hypothesis |

**Ownership inventory.** Owner and steward are `Unknown` because the brief
supplies no accountable role. A *candidate role* is a proposal to put to the
domain, never a recorded owner. Every row has a resolution path in Section 6.9.

| Asset | Data owner | Candidate role (proposal) | Steward | Producers | Consumers | Change authority | Ownership status | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AST-01 | Unknown | ST-02 Retail domain owner (validate) | Unknown | SYS-03 | SYS-01; SYS-02; SYS-04; SYS-05; SYS-06 | Unknown | Unknown | Unknown | DOC-07 requested; ownership interview pending |
| AST-02 | Unknown | ST-02 Retail domain owner (validate) | Unknown | SYS-01; SYS-02; SYS-03; SYS-04 | SYS-05; SYS-06; SYS-09 | Unknown | Unknown | Unknown | DOC-07 requested; ownership interview pending |
| AST-03 | Unknown | ST-02 Retail domain owner (validate) | Unknown | SYS-03 | SYS-05; SYS-06; SYS-09 | Unknown | Unknown | Unknown | DOC-07 requested; ownership interview pending |
| AST-04 | Unknown | ST-02 Retail domain owner (validate) | Unknown | SYS-05; SYS-09 | SYS-03 | Unknown | Unknown | Unknown | DOC-05 requested; definition owner unknown |
| AST-05 | Unknown | ST-02 Retail domain owner (validate) | Unknown | SYS-01 | SYS-05; SYS-06 | Unknown | Unknown | Unknown | DOC-07 requested; ownership interview pending |
| AST-06 | Unknown | ST-02 Retail domain owner (validate) | Unknown | SYS-01 | SYS-05; SYS-06; SYS-07; SYS-08 | Unknown | Unknown | Unknown | DOC-07 requested; ownership interview pending |
| AST-07 | Unknown | ST-04 Cards domain owner (validate) | Unknown | SYS-02 | SYS-05; SYS-06 | Unknown | Unknown | Unknown | DOC-07 requested; ownership interview pending |
| AST-08 | Unknown | ST-04 Cards domain owner (validate) | Unknown | SYS-02 | SYS-05; SYS-06 | Unknown | Unknown | Unknown | DOC-07 requested; ownership interview pending |
| AST-09 | Unknown | ST-03 Lending domain owner (validate) | Unknown | SYS-04 | SYS-05; SYS-06 | Unknown | Unknown | Unknown | DOC-07 requested; ownership interview pending |
| AST-10 | Unknown | ST-03 Lending domain owner (validate) | Unknown | SYS-04 | SYS-05; SYS-06; SYS-07; SYS-08 | Unknown | Unknown | Unknown | DOC-07 requested; ownership interview pending |
| AST-11 | Unknown | ST-05 Head of Risk (validate) | Unknown | SYS-07 | SYS-10 | Unknown | Unknown | Unknown | DOC-07 requested; ownership interview pending |
| AST-12 | Unknown | ST-08 Head of Compliance (validate) | Unknown | SYS-10 | EXT-01 | Unknown | Unknown | Unknown | DOC-09 requested; accountability is the regulator's question |
| AST-13 | Unknown | ST-01 Head of Data as convenor (validate) | Unknown | SYS-07; SYS-08; SYS-09; SYS-10 | Unknown | Unknown | Unknown | Unknown | DOC-06 requested; four producers, no designated owner evidenced |
| AST-14 | Unknown | ST-10 Engineering leads as custodian only (validate) | Unknown | SYS-05 | SYS-07; SYS-08; SYS-10 | Unknown | Unknown | Unknown | DOC-07 requested; follows the owners of the source assets |

### 6.5 D5 — Current-state data flow and architecture view (Steps 7, 8, 12)

**Flow inventory**

| ID | From | To | Data (assets) | Method | Frequency | Control | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FLW-01 | SYS-01 | SYS-05 | AST-05; AST-06 | Batch ETL (assumed) | Daily (assumed) | Unknown | Assumed | Assessor hypothesis; DOC-04 requested |
| FLW-02 | SYS-02 | SYS-05 | AST-07; AST-08 | Batch file (assumed) | Daily (assumed) | Unknown | Assumed | Assessor hypothesis; DOC-04 requested |
| FLW-03 | SYS-03 | SYS-05 | AST-01; AST-02; AST-03 | Batch extract (assumed) | Daily (assumed) | Unknown | Assumed | Assessor hypothesis; DOC-04 requested |
| FLW-04 | SYS-04 | SYS-05 | AST-09; AST-10 | Batch extract (assumed) | Daily (assumed) | Unknown | Assumed | Assessor hypothesis; DOC-04 requested |
| FLW-05 | SYS-01; SYS-02; SYS-03; SYS-04 | SYS-06 | AST-01; AST-02; AST-03; AST-05; AST-06; AST-07; AST-08; AST-09; AST-10 | Unknown | Unknown | Unknown | Assumed | Scenario brief: lake exists; ingestion method is a hypothesis |
| FLW-06 | SYS-05 | SYS-07 | AST-14; AST-06; AST-10 | Extract (assumed) | Unknown | Unknown | Assumed | Assessor hypothesis (A3) |
| FLW-07 | SYS-05 | SYS-08 | AST-14; AST-06; AST-10 | Extract (assumed) | Unknown | Unknown | Assumed | Assessor hypothesis (A3) |
| FLW-08 | SYS-06 | SYS-09 | AST-02; AST-03 | Unknown | Unknown | Unknown | Assumed | Assessor hypothesis (A3) |
| FLW-09 | SYS-05 | SYS-10 | AST-14 | Manual extract to spreadsheet | Monthly (assumed) | None evidenced | Assumed | Assessor hypothesis (A3); DOC-12 requested |
| FLW-10 | SYS-07 | SYS-10 | AST-11; AST-13 | Manual copy between workbooks | Unknown | None evidenced | Assumed | Assessor hypothesis; DOC-12 requested |
| FLW-11 | SYS-03 | SYS-01 | AST-01; AST-02 | Unknown | Unknown | Unknown | Assumed | Existence and direction unverified |
| FLW-12 | SYS-03 | SYS-09 | AST-02; AST-03 | Unknown | Unknown | Unknown | Assumed | Assessor hypothesis |
| FLW-13 | SYS-09 | SYS-03 | AST-04 | Unknown | Unknown | Unknown | Assumed | Assessor hypothesis |
| FLW-14 | SYS-10 | EXT-01 | AST-12 | Manual submission | Per regulatory calendar (Unknown) | None evidenced | Assumed | Scenario brief: regulator enquiry; method is a hypothesis |

**Component inventory (logical)**

| ID | Component (logical) | Layer | Hosted in | Assets held | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- |
| CMP-01 | Operational transactional stores | Source | SYS-01; SYS-02; SYS-03; SYS-04 | AST-01; AST-02; AST-03; AST-04; AST-05; AST-06; AST-07; AST-08; AST-09; AST-10 | Assumed | Assessor hypothesis |
| CMP-02 | EDW staging area | Ingestion | SYS-05 | AST-01; AST-02; AST-03; AST-05; AST-06; AST-07; AST-08; AST-09; AST-10 | Assumed | Assessor hypothesis; DOC-03 requested |
| CMP-03 | EDW integrated model | Integrated store | SYS-05 | AST-01; AST-02; AST-03; AST-04; AST-05; AST-06; AST-07; AST-08; AST-09; AST-10; AST-14 | Assumed | Assessor hypothesis; DOC-03 requested |
| CMP-04 | EDW reporting marts and views | Serving | SYS-05 | AST-04; AST-14 | Assumed | Assessor hypothesis; DOC-03 requested |
| CMP-05 | Lake raw zone | Landing | SYS-06 | AST-01; AST-02; AST-03; AST-05; AST-06; AST-07; AST-08; AST-09; AST-10 | Assumed | Scenario brief: lake exists; zone structure is a hypothesis |
| CMP-06 | Lake curated zone | Analytical | SYS-06 | Unknown | Unknown | DOC-03 requested; existence unverified |
| CMP-07 | Departmental reporting databases | Departmental serving | SYS-07; SYS-08; SYS-09 | AST-02; AST-03; AST-04; AST-06; AST-10; AST-11; AST-13; AST-14 | Assumed | Scenario brief: team-built databases exist |
| CMP-08 | End-user spreadsheets | End-user computing | SYS-10 | AST-11; AST-12; AST-13; AST-14 | Assumed | Scenario brief: spreadsheets exist |
| CMP-09 | Batch integration and scheduling | Processing | SYS-05 | None (data in transit only: FLW-01 to FLW-04, FLW-06, FLW-07) | Assumed | Assessor hypothesis; DOC-04 requested |
| CMP-10 | Enterprise reporting and BI delivery | Serving | Unknown | Unknown | Unknown | DOC-03 requested; existence unverified |

**Current-state diagram (logical, version 1.1, 2026-10-21)**

```text
D5-DIAGRAM  Northbridge current-state data flow (logical) | v1.1 | 2026-10-21 | ILLUSTRATIVE
Legend:  [SYS-nn name] system   [EXT-nn] external party   ──FLW-nn──►  flow with ID
         (a) = automated or assumed automated   (m) = manual   (?) = method or existence unverified
         Arrow direction = direction of data movement. All flows are Assumed unless stated in 6.5.

 OPERATIONAL (assumed systems of record)       ANALYTICAL                   DEPARTMENTAL / END-USER
 ───────────────────────────────────────       ──────────────────           ─────────────────────────────────────
 [SYS-01 Core Banking]──FLW-01(a)──┐
 [SYS-02 Cards Platform]──FLW-02(a)┤
 [SYS-03 CRM]──────────FLW-03(a)───┼──►[SYS-05 EDW]──FLW-06(a)──►[SYS-07 Risk DB]──FLW-10(m)──┐
 [SYS-04 Loan Orig.]───FLW-04(a)───┘        │                                                   ▼
                                            ├──FLW-07(a)──►[SYS-08 Finance DB]     [SYS-10 Compliance spreadsheets]
                                            └──FLW-09(m)─────────────────────────────────────►   │
                                                                                                  └─FLW-14(m)─►[EXT-01 Regulator]
 [SYS-01]..[SYS-04]──FLW-05(?)──►[SYS-06 Data Lake]──FLW-08(?)──►[SYS-09 Marketing DB]

 Lateral flows among operational and departmental systems:
   [SYS-03 CRM]──FLW-11(?)──►[SYS-01 Core Banking]
   [SYS-03 CRM]──FLW-12(?)──►[SYS-09 Marketing DB]
   [SYS-09 Marketing DB]──FLW-13(?)──►[SYS-03 CRM]
```

**Reading the view.** Five of the fourteen flows have an unknown method (FLW-05,
FLW-08, FLW-11, FLW-12, FLW-13), and three are manual (FLW-09, FLW-10, FLW-14), all
touching the compliance spreadsheets that prepare the regulatory return. These are
the first places a lineage question is likely to stall.

### 6.6 D6 — Architecture principles and governance observations (Step 9)

**Governance observations.** The brief names no policy, standard or forum. Every
row is therefore `Unknown` pending the document requests; the *documented* and
*practised* columns are kept apart so that a published policy is never treated as
evidence of practice.

| ID | Item | Type | Documented? | Practised? | Evidence | Source | Finding |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GOV-01 | Enterprise data architecture principles | Principle | Unknown | Unknown | Unknown | DOC-08 requested | F-09 |
| GOV-02 | Data ownership and stewardship policy | Policy | Unknown | Unknown | Unknown | DOC-07 requested | F-08 |
| GOV-03 | Architecture review forum and decision rights | Forum | Unknown | Unknown | Unknown | DOC-08 requested | F-09 |
| GOV-04 | Data classification standard | Standard | Unknown | Unknown | Unknown | DOC-07 requested | F-09 |
| GOV-05 | Data quality standard and issue-management process | Standard | Unknown | Unknown | Unknown | DOC-07 and DOC-10 requested | F-09 |
| GOV-06 | End-user computing (spreadsheet) control policy | Policy | Unknown | Unknown | Unknown | DOC-12 requested | F-06 |
| GOV-07 | Architecture decision records and exception register | Record | Unknown | Unknown | Unknown | DOC-08 requested | F-09 |
| GOV-08 | Change control for interfaces and data definitions | Process | Unknown | Unknown | Unknown | DOC-04 requested | F-09 |
| GOV-09 | Regulatory evidence and lineage procedure | Procedure | Unknown | Unknown | Unknown | DOC-09 requested | F-03 |

**Principle lens.** Because no Northbridge principles are evidenced, the
illustrative principle set from Lesson 04 (section 6.4) is used as an *assessment
lens*. It is **not adopted** by Northbridge; adoption is a governance decision.

| ID | Reference principle | Observation | Rating | Evidence | Finding |
| --- | --- | --- | --- | --- | --- |
| PL-01 | P1 Accountable ownership | Regulator asks who is accountable; no owner evidenced for any asset | Indicative concern | Assumed | F-08 |
| PL-02 | P2 Quality by use | Four functions report different customer counts; no quality targets evidenced | Indicative concern | Reported | F-01 |
| PL-03 | P3 Evidence before claims | No quality measurements or tests supplied to the assessor | Not rated (no evidence) | Unknown | F-09 |
| PL-04 | P4 Minimise sensitive-data exposure | Customer data is assumed present in most of the ten systems, including spreadsheets | Indicative concern | Assumed | F-06 |
| PL-05 | P5 Explicit contracts for shared data | Interface specifications and change paths not evidenced | Not rated (no evidence) | Unknown | F-09 |
| PL-06 | P6 Lifecycle value over local optimisation | Team-built databases and two analytical platforms suggest local optimisation | Indicative concern | Reported | F-07 |
| PL-07 | P7 Controlled, reviewable deviations | No exception register evidenced | Not rated (no evidence) | Unknown | F-09 |

### 6.7 D7 — Quality-attribute assessment (Step 10)

No targets are evidenced. Per Lesson 04, "no target" is itself a finding, and the
assessor must not invent one.

| ID | Attribute | Scope | Target | Evidence summary | Rating | Confidence | Evidence | Finding |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA-01 | Semantic consistency | Customer count (AST-13) and active-customer flag (AST-04) | None evidenced | Four functions report different counts; cause not yet analysed | Indicative concern | Medium | Reported | F-01 |
| QA-02 | Traceability (lineage) | Regulatory customer return (AST-12) from source to submission | None evidenced | Regulator asks for origin evidence; no lineage artefact evidenced | Indicative concern | Low | Reported | F-03 |
| QA-03 | Accountability | All fourteen in-scope assets | None evidenced | No ownership policy or owner evidenced | Indicative concern | Low | Unknown | F-08 |
| QA-04 | Freshness | Data feeding reports (FLW-01 to FLW-09) | None evidenced | No refresh targets or measurements evidenced | Not rated (no evidence) | Low | Unknown | F-09 |
| QA-05 | Security and privacy | Customer data in SYS-07 to SYS-10 | None evidenced | Classification and access controls not evidenced | Not rated (no evidence) | Low | Unknown | F-06 |
| QA-06 | Reliability and recoverability | Manual flows FLW-09, FLW-10, FLW-14 | None evidenced | No incident history supplied; manual handling is a known failure mode | Indicative concern | Low | Assumed | F-10 |
| QA-07 | Interoperability and contract clarity | Interfaces FLW-01 to FLW-14 | None evidenced | Interface specifications not evidenced | Not rated (no evidence) | Low | Unknown | F-09 |
| QA-08 | Cost efficiency | EDW and lake | None evidenced | Overlapping platforms assumed; no cost data supplied | Not rated (no evidence) | Low | Unknown | F-07 |

**Drivers, constraints, assumptions and preferences** (Lesson 04 section 4.5)

| Type | Statement | Status |
| --- | --- | --- |
| Driver | The regulator expects evidence of data origin and accountability | Reported |
| Driver | Conflicting customer counts undermine management decisions | Reported |
| Constraint | None confirmed; any applicable regulation or policy must be identified by Compliance | Unknown |
| Assumption | Assumptions A1–A5 in 6.1 | Assumed |
| Preference | None stated | Unknown |

### 6.8 D8 — Findings and gap, risk, dependency and question register (Step 11)

**Findings** are statements of what the evidence shows, with confidence. They are
kept separate from symptoms (the conflicting counts) and from the register's
judgements.

| ID | Finding | Basis | Affects | Confidence | Evidence |
| --- | --- | --- | --- | --- | --- |
| F-01 | Four functions report different customer counts | Scenario brief | AST-13; AST-04; ST-05; ST-06; ST-07; ST-08 | Medium | Reported |
| F-02 | No agreed enterprise definition of "customer" or "active customer" is evidenced | Inference from F-01; DOC-05 not received | AST-04; AST-13; DOC-05 | Low | Assumed |
| F-03 | The regulator has asked for evidence of data origin and accountability; the ability to evidence it end to end is unverified | Scenario brief; no lineage artefact received | AST-12; CAP-09; ST-13; GOV-09 | Medium | Reported |
| F-04 | Customer identity and contact attributes are assumed to be held in at least four operational systems with no designated authoritative source | Inference from system roles | AST-01; AST-02; SYS-01; SYS-02; SYS-03; SYS-04 | Low | Assumed |
| F-05 | The customer onboarding capability has no identified supporting system | Capability–system mapping (6.3) | CAP-01 | Low | Assumed |
| F-06 | Team-built reporting databases and spreadsheets exist (reported); whether they sit outside governed integration, and what controls apply, is unevidenced | Scenario brief for existence; integration path and controls unknown | SYS-07; SYS-08; SYS-09; SYS-10; CMP-07; CMP-08 | Medium | Reported |
| F-07 | The warehouse and the lake coexist with overlapping analytical purposes; their roles and boundary are unevidenced | Scenario brief for coexistence | SYS-05; SYS-06; CMP-05 | Low | Reported |
| F-08 | No accountable owner or steward is evidenced for any of the fourteen in-scope assets | Ownership inventory (6.4) | AST-01; AST-14 | Low | Unknown |
| F-09 | No enterprise principles, ownership policy, classification standard, review forum or change-control process is evidenced | Governance observations (6.6); DOC-07 and DOC-08 not received | GOV-01; GOV-03; GOV-04 | Low | Unknown |
| F-10 | Regulatory-return data moves through manual flows with no controls evidenced | Flow inventory (6.5) | FLW-09; FLW-10; FLW-14 | Low | Assumed |

**Register.** Scoring per Section 4.2. Every row cites at least one finding.

| ID | Type | Title and description | Supporting finding(s) | Affected | Impact | Likelihood | Score | Confidence | Proposed owner | Next step | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-01 | Risk | Conflicting customer counts lead to inconsistent management and regulatory decisions | F-01; F-02 | AST-13; AST-04; CAP-09; CAP-11 | 3 | 3 | 9 | Medium | ST-01 | N-01 | Open |
| R-02 | Gap | No agreed enterprise definition of customer or active customer | F-02 | AST-04; AST-13 | 3 | 3 | 9 | Low | ST-01 | N-01 | Open |
| R-03 | Risk | The bank cannot evidence data origin and accountability to the regulator | F-03; F-08 | AST-12; CAP-09 | 3 | 2 | 6 | Low | ST-08 | N-02 | Open |
| R-04 | Gap | No designated authoritative source for customer identity and contact attributes | F-04 | AST-01; AST-02 | 3 | 3 | 9 | Low | ST-02 | N-03 | Open |
| R-05 | Gap | No accountable owner or steward evidenced for in-scope assets | F-08 | AST-01; AST-14 | 3 | 3 | 9 | Low | ST-01 | N-04 | Open |
| R-06 | Risk | Regulatory return prepared through manual spreadsheet flows without evidenced controls | F-06; F-10 | FLW-09; FLW-10; FLW-14; SYS-10 | 3 | 2 | 6 | Low | ST-08 | N-02; N-05 | Open |
| R-07 | Gap | Onboarding capability has no identified supporting system | F-05 | CAP-01 | 2 | 2 | 4 | Low | ST-02 | N-08 | Open |
| R-08 | Risk | Overlapping warehouse and lake increase cost and create divergent copies | F-07 | SYS-05; SYS-06 | 2 | 2 | 4 | Low | ST-10 | N-07 | Open |
| R-09 | Gap | No governance artefacts evidenced: principles, classification, forum, change control | F-09 | GOV-01; GOV-03; GOV-04 | 2 | 3 | 6 | Low | ST-01 | N-06 | Open |
| R-10 | Risk | Sensitive customer data in departmental databases and spreadsheets without evidenced classification or access control | F-06; F-09 | SYS-07; SYS-08; SYS-09; SYS-10 | 3 | 2 | 6 | Low | ST-09 | N-05 | Open |
| R-11 | Dependency | The assessment depends on timely access to documents and system owners | F-09 | DOC-01; DOC-07; ST-10 | 2 | 2 | 4 | Low | ST-01 | N-06 | Open |
| R-12 | Question | Do the four customer counts differ by definition, scope, as-of date or defect? | F-01 | AST-13; AST-04 | 2 | 3 | 6 | Medium | ST-05 | N-01 | Open |
| R-13 | Question | Is lineage available for the regulatory return from source to submission? | F-03; F-10 | AST-12; FLW-14 | 3 | 2 | 6 | Low | ST-08 | N-02 | Open |
| R-14 | Question | What is the intended role boundary between the warehouse and the lake? | F-07 | SYS-05; SYS-06 | 2 | 2 | 4 | Low | ST-10 | N-07 | Open |
| R-15 | Question | What are the regulator's response deadline and exact scope? | F-03 | ST-13; DOC-09 | 3 | 2 | 6 | Medium | ST-08 | N-02 | Open |

### 6.9 D9 — Findings and prioritised next steps (Step 14)

These are **recommendations as next steps only**. They do not describe a target
state, choose technology or assign ownership. Priority is derived by the rule in
Section 4.2.

| ID | Recommended next step | Addresses (register) | Max score | Effort | Priority | Owner (proposed) |
| --- | --- | --- | --- | --- | --- | --- |
| N-01 | Document the four customer-count definitions and bring ST-05 to ST-08 together to establish who decides the definition and who is accountable for the measure | R-01; R-02; R-12 | 9 | M | P1 | ST-01 |
| N-02 | Trace the regulatory customer return from source systems to submission with the compliance team, confirming deadline and scope of the enquiry | R-03; R-06; R-13; R-15 | 6 | M | P1 | ST-08 |
| N-03 | Confirm at attribute level which system is authoritative for customer identity and contact data | R-04 | 9 | M | P1 | ST-02 |
| N-04 | Put each in-scope asset to its candidate domain owner for confirmation and record the decision using the Lesson 03 ownership log | R-05 | 9 | M | P1 | ST-01 |
| N-05 | Inventory departmental databases and spreadsheets that hold customer data and check classification and access arrangements with Information Security | R-06; R-10 | 6 | L | P2 | ST-09 |
| N-06 | Obtain and review the governance documents and test whether they are practised | R-09; R-11 | 6 | S | P1 | ST-01 |
| N-07 | Clarify with platform owners the intended roles of the warehouse and the lake | R-08; R-14 | 4 | S | P2 | ST-10 |
| N-08 | Determine which system, if any, supports customer onboarding | R-07 | 4 | S | P2 | ST-02 |

**Resolution path for unknown ownership.** N-04 produces, for each of the
fourteen assets, a recorded owner and steward or an explicit `Unknown` with an
owner for resolving it and a review date. Where two domains claim the same asset,
apply the contested-ownership method in Lesson 03 section 6.8 rather than
choosing by seniority.

**Hand-off to decision records.** Each P1 step is expected to become an
architecture decision record (Lesson 05 section 9.1 template) in module 2D.2.

### 6.10 Validation log (Step 13)

Status shows that **no validation has taken place** for this worked reference.
The log shows the structure and the reviewers that would be required.

| ID | Finding | Reviewer role | Review method | Planned date | Recorded response | Status |
| --- | --- | --- | --- | --- | --- | --- |
| VL-01 | F-01 | ST-05; ST-06 | Joint walk-through of the four count definitions | Week 5 | Not yet recorded | Planned |
| VL-02 | F-03 | ST-08 | Review with the regulator liaison | Week 5 | Not yet recorded | Planned |
| VL-03 | F-04 | ST-02; ST-10 | Attribute-level review with the domain owner and engineering | Week 5 | Not yet recorded | Planned |
| VL-04 | F-06 | ST-09; ST-11 | Review with Information Security and Operations | Week 5 | Not yet recorded | Planned |
| VL-05 | F-08 | ST-01; ST-02 | Review of the ownership inventory | Week 5 | Not yet recorded | Planned |
| VL-06 | F-09 | ST-12 | Independent challenge of the evidence behind governance findings | Week 5 | Not yet recorded | Planned |

### 6.11 D10 — Final assessment summary (Step 14)

**Northbridge Bank — Current-state data architecture inventory. Version 1.1, 2026-10-21. ILLUSTRATIVE.**

**Purpose and scope.** To give the Head of Data a trustworthy picture of customer,
account and transaction data so the regulator's enquiry and the conflicting
customer counts can be handled on evidence. The assessment covers ten systems, six
proposed domains, twelve business capabilities and fourteen data assets at a
logical level. It excludes schema design, tooling, target-state design and any
reading of customer-level data.

**What the evidence shows.** The brief states that four functions report different
customer counts and that a regulator wants clearer evidence of data origin and
accountability. Beyond these facts and the existence of the listed systems, the
worked assessment holds no verified evidence: documents were requested and none
received; ownership and governance arrangements are unknown. The findings
therefore describe what is *reported* and what is *unknown*.

**Key findings.**

1. Four functions report different customer counts (F-01), and no agreed definition is evidenced (F-02).
2. The ability to evidence data origin and accountability to the regulator is unverified (F-03).
3. Customer attributes are assumed to be held in at least four systems with no designated authoritative source (F-04).
4. No accountable owner or steward is evidenced for any in-scope asset (F-08), and no governance artefact is evidenced (F-09).
5. Regulatory-return data is assumed to move through manual spreadsheet flows without evidenced controls (F-06, F-10).

**Top risks.** R-01 conflicting counts (score 9); R-04 no authoritative source for
customer attributes (9); R-05 no accountable owners (9); R-03, R-06 and R-10 (6 each).

**Recommended next steps (priority P1 first).** N-01 settle the customer-count
definition and its owner; N-02 trace the regulatory return end to end; N-03 confirm
the authoritative source for customer attributes; N-04 confirm asset ownership;
N-06 obtain and test governance documents. N-05, N-07 and N-08 follow (P2).

**Caveats and limits.** Most values are `Assumed` or `Unknown`; confidence is Low
to Medium throughout. No stakeholder has validated any finding. Ratings of
"indicative concern" are signals to investigate, not conclusions. The findings must
not be used to assert non-compliance. The assessment is a baseline, not a design.

---

## 7. Validation and quality assurance

### 7.1 Quality criteria and how each is verified

| Check | How to verify | Automated? |
| --- | --- | --- |
| Inventory complete for the declared scope | Every capability maps to a system or an explicit "No system identified"; every system has an owner or `Unknown` | Yes (checker) |
| Major systems and flows captured | Sample at least three flows end to end with a knowledgeable person; add any missing flow | No (Step 7 and 13) |
| Domains and ownership traceable | Pick five assets at random; trace asset → system → capability → domain → owner | Yes (`--spot-check`) |
| Views internally consistent | Every diagram element exists in the inventory and vice versa; names match | Yes (checker) |
| Assumptions and evidence distinguishable | Every row carries an evidence label; no unlabelled claim | Yes (checker) |
| Risks and gaps supported by findings | Every register item cites a finding that exists | Yes (checker) |
| Stakeholders reviewed material findings | Validation log shows reviewer and response per finding | No |
| Recommendations traceable | Each next step cites register items; priority matches the rule | Yes (checker) |
| No invented values | Unknowns are listed, not replaced | Yes (`--unknowns`) |
| Bidirectional links hold | System ↔ capability, system ↔ flow, domain ↔ capability, asset ↔ component | Yes (checker) |

### 7.2 Running the checker

Extract Appendix B to `check_inventory.py`, then run from the repository root:

```bash
python3 check_inventory.py "Stage 2D — Data Architecture/01-Data-Architecture-Foundations-and-Principles/Projects/01-current-state-data-architecture-inventory.md"
python3 check_inventory.py FILE --spot-check 5 --seed 2026
python3 check_inventory.py FILE --unknowns
```

The checker exits `0` when all checks pass and `1` otherwise. It reads Markdown
tables in this file, so any edit that breaks an ID reference is caught
immediately. For a real assessment (Mode B), keep the same header names in your
tables, or adapt the `KINDS` mapping at the top of the script.

### 7.3 Manual spot-check protocol

1. Choose five assets at random (use the `--spot-check` output or dice).
2. For each, follow the chain: asset → authoritative or primary system → capability → domain → owner.
3. Confirm each hop with the responsible person; record the date.
4. Any break in the chain is a defect to fix in the inventory, not a finding about the organisation, until confirmed.

**Recorded run at v1.1** (`--spot-check 5 --seed 2026`; chain built from the inventory only, **not** confirmed with stakeholders):

```text
AST-02 Customer contact details -> SYS-01 (first holder, authority Unknown) -> CAP-02 -> DOM-01 -> owner: Unknown
AST-06 Posted deposit transaction -> SYS-01 (authoritative) -> CAP-03, CAP-06, CAP-07 -> DOM-02 -> owner: Unknown
AST-09 Loan application and decision -> SYS-04 (authoritative) -> CAP-04 -> DOM-03 -> owner: Unknown
AST-12 Regulatory customer return -> SYS-10 (authoritative) -> CAP-09 -> DOM-05 -> owner: Unknown
AST-14 Conformed customer view (EDW) -> SYS-05 (first holder, authority Unknown) -> CAP-09, CAP-11, CAP-12 -> DOM-01 -> owner: Unknown
```

### 7.4 Review checklist for the challenger

- Is every claim labelled with an evidence type, and is the label the weakest of its claims?
- Could any value be an invention presented as fact?
- Does any recommendation describe a target state or a product?
- Would a different assessor, given the same evidence, reach the same findings?
- Which findings rest on absence of evidence rather than evidence of absence?

### 7.5 Project completion gate (roadmap Section 7.7) and worked-reference status

| Gate item | Mode A status (Northbridge worked reference) | Mode B requirement |
| --- | --- | --- |
| D1–D10 exist and are version-dated | Met: sections 6.1–6.11, v1.1, 2026-10-21 | Met for your own set |
| Every inventory row has a source and an evidence type | Met: enforced by the checker | Met |
| No unknown replaced by an invented one; unknowns listed | Met: `--unknowns` lists them | Met |
| Capability → system → asset → owner passes the five-asset spot check | Met by the checker; chain confirmed by interview is **not** performed | Met with stakeholder confirmation |
| Diagram and inventory consistent | Met: enforced by the checker | Met |
| Every register item and recommendation traces to a finding | Met: enforced by the checker | Met |
| At least two stakeholders reviewed material findings; responses recorded | **Not met by design:** the log is `Planned` | Required |
| Final summary readable by a non-specialist in ten minutes and states its limits | Written to that standard; reader test **not performed** | Required |
| A reviewer who did not do the work agrees the evidence supports the conclusions | **Not met by design** | Required |

---

## 8. Templates and guides for a real organisation (Mode B)

Placeholders use the form `XXX-nn`; replace them with real IDs.

### 8.1 Row templates

**System inventory**

| ID | System (logical name) | Capabilities supported | Role | Business owner | Technical owner | Main data held (domains) | Hosting | Lifecycle | Interfaces (flows) | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SYS-nn | name | CAP-nn | system of record / consumer / copy / reporting | role or Unknown | role or Unknown | DOM-nn | on-premises / cloud / vendor / Unknown | active / retiring / planned | FLW-nn | Observed / Reported / Assumed / Unknown | document ID or interview |

**Data asset**

| ID | Asset | Description | Domain | Authoritative system | Held in | Sensitivity (as classified) | Refresh | Known quality concerns | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AST-nn | name | meaning in business words | DOM-nn | SYS-nn or Unknown | SYS-nn | as classified, or Unknown | frequency | concern or "None evidenced" | label | source |

**Ownership**

| Asset | Data owner | Candidate role (proposal) | Steward | Producers | Consumers | Change authority | Ownership status | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AST-nn | role or Unknown | proposal | role or Unknown | SYS-nn | SYS-nn | role or Unknown | Confirmed / Proposed / Disputed / Unknown | label | source |

**Illustrative filled example (not part of the Northbridge data):**
`Owner = Head of Retail (Confirmed in interview, 2026-02-14); Steward = Customer Data Steward; Change authority = Retail Data Council; Status = Confirmed; Evidence = Reported; Source = interview note, ownership policy v3.`

**Flow**

| ID | From | To | Data (assets) | Method | Frequency | Control | Evidence | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FLW-nn | SYS-nn | SYS-nn | AST-nn | batch / API / stream / file / manual | schedule | reconciliation or None evidenced | label | source |

**Validation log**

| ID | Finding | Reviewer role | Review method | Planned date | Recorded response | Status |
| --- | --- | --- | --- | --- | --- | --- |
| VL-nn | F-nn | role | method | date | accepted / corrected / disputed, with detail | Planned / Held / Closed |

### 8.2 Document request list

Request these early; record author, date and status of each:

1. Systems list or CMDB extract and owner list.
2. Business capability model and process lists.
3. Architecture diagrams for core, warehouse, lake, integration.
4. Interface inventory, job schedules and data-sharing agreements.
5. Data dictionary or glossary, especially customer-related definitions.
6. Report definitions for any conflicting metrics.
7. Policies: ownership, classification, quality, retention, spreadsheet control.
8. Principles, standards, decision records and exception registers.
9. The triggering request (regulator letter, audit finding, board paper).
10. Incident and data-quality issue logs, last twelve months.
11. Internal audit and risk reports touching data.
12. Registers of departmental databases and end-user spreadsheets.

### 8.3 Interview guide (by group)

| Group | Questions that produce evidence |
| --- | --- |
| Domain owners | Which decisions does this data support? Who may change its definition? What happens when it is wrong? Which systems do you trust, and why? |
| Engineering leads | What does this system hold and feed? Which interfaces exist, who owns them, how are failures detected? What changes would you hesitate to make? |
| Risk, finance, marketing, compliance | Which counts and measures do you produce? From which source? Which definition? Where do you correct data? |
| Operations | Which manual steps exist? What breaks most often? Which spreadsheets are critical? |
| Security | How is data classified? Where are copies allowed? Who reviews access? |
| Internal audit | What have you already found? What evidence would you accept for ownership and lineage? |

Always ask: *Who else uses this? What would you show me to prove it? What are you
least sure about?* Record the answers with the evidence label `Reported`.

---

## 9. Common pitfalls and project risks

| Pitfall | Why it harms | Prevention |
| --- | --- | --- |
| Starting from the system list | Rebuilds existing silos; hides capability gaps | Build the capability map first (Step 3) |
| Inventing owners or classifications | Creates false assurance that surfaces during audit | Use `Unknown`; require evidence for `Confirmed` |
| Treating a policy document as practice | Documented is not practised | Separate the two columns; test practice by sampling |
| Omitting manual flows and spreadsheets | The risk is often there | Include them explicitly; request the end-user computing register |
| Exhaustive but shallow inventory | No one can review it | Prefer a small set of important assets and say how you chose |
| Designing the target state | Hides evidence; prejudices decisions | Record next steps only; hand design to 2D.2 and 2D.3 |
| Silent resolution of disagreements | Destroys trust in the record | Record disagreement in the validation log |
| Diagram and inventory drift | The picture contradicts the facts | One source of truth; run the checker before each release |
| Collecting customer-level data | Privacy and security exposure | Metadata only (Section 4.6) |
| Stakeholder fatigue | Evidence dries up | Sequence interviews; prepare questions; reuse documents |

**Project-level risks**

| Risk | Early sign | Response |
| --- | --- | --- |
| Documents not supplied | Requests unanswered after one week | Escalate through the sponsor; record the missing documents as a finding |
| Scope creep | New systems arrive in later weeks | Apply change control to D1; record the change |
| Disputed ownership | Two domains claim an asset | Use the Lesson 03 conflict method; record both claims |
| Politically sensitive finding | Reviewer resists a factual statement | Keep evidence and confidence visible; record the response without altering the finding |

---

## 10. Connection to the next modules

The inventory is a **baseline, not a design**. It supports later work without
absorbing it.

| Next module | What it takes from this project |
| --- | --- |
| 2D.2 Requirements, Constraints and Architecture Decisions | Gaps, risks and open questions become inputs to stakeholder discovery and requirement statements; quality-attribute gaps seed non-functional requirements; P1 next steps become decision records |
| 2D.3 and 2D.7 Patterns and platform | The diagram is the "from" in a current-to-target comparison; domain and ownership findings inform pattern choice |
| 2D.10 and 2D.11 Governance, metadata, master data | Ownership gaps, undefined classification and lineage questions feed these modules directly |
| 2D.15 Documentation, reviews, operating model | The validation log and checker become part of a repeatable review practice |

Carry forward to module 2D.2: the open questions R-12, R-13, R-14 and R-15, the
Assumptions A1–A5, and the unresolved ownership list from N-04.

---

## 11. Self-assessment rubric

Score each criterion 0 (absent), 1 (partial) or 2 (complete). Pass requires
at least 90% of the maximum and no zero.

| # | Criterion | Evidence |
| --- | --- | --- |
| 1 | Scope names exclusions and time frame | D1 |
| 2 | Every row has a source and one evidence label | Checker output |
| 3 | Capabilities are business-language and mapped, with explicit "no system" | D3 |
| 4 | Assets are prioritised, with the selection rationale stated | D4 |
| 5 | Ownership uses Confirmed, Proposed, Disputed, Unknown; no empty cell | D4 |
| 6 | Flows include manual and spreadsheet movement | D5 |
| 7 | Diagram and inventory pass the consistency check | Checker output |
| 8 | Governance separates documented from practised | D6 |
| 9 | Quality ratings cite evidence or "no target / no evidence" | D7 |
| 10 | Every register item traces to a finding | Checker output |
| 11 | Recommendations are next steps, not designs | D9 |
| 12 | Validation log records reviewer and response, including disagreement | Validation log |
| 13 | Summary states caveats and can be read in ten minutes | D10 |
| 14 | Independent reviewer confirms evidence supports conclusions | Reviewer note |

---

## Appendix A — Glossary

| Term | Meaning in this project |
| --- | --- |
| Asset | A bounded, meaningful collection of data (for example a verified customer contact set) |
| Authoritative system | The system whose version of an asset is treated as the truth; never inferred from custody |
| Capability | What the organisation can do, in business language |
| Domain | A bounded area of business meaning and responsibility |
| Evidence label | Observed, Reported, Assumed or Unknown |
| Finding | A statement of what the evidence shows, with confidence |
| Register item | A gap, risk, constraint, dependency or question traced to a finding |
| Steward | The role responsible for quality and definitions, distinct from the accountable owner |
| System of record | The system that holds the authoritative version of an asset |

---

## Appendix B — Consistency checker (`check_inventory.py`)

Python 3.9 or later; standard library only. It reads Markdown tables from this file.

```python
#!/usr/bin/env python3
"""Consistency checker for the current-state inventory (deliverables D2-D9).

Usage:
    python3 check_inventory.py FILE
    python3 check_inventory.py FILE --spot-check 5 --seed 2026
    python3 check_inventory.py FILE --unknowns

Exit code 0 means every check passed; 1 means at least one error.
"""
import argparse
import random
import re
import sys
from pathlib import Path

ID_CELL = re.compile(r"^[A-Z]{1,4}-\d{2}$")
ID_ANY = re.compile(r"\b[A-Z]{1,4}-\d{2}\b")
SEPARATOR = re.compile(r"^:?-{3,}:?$")
EVIDENCE = {"Observed", "Reported", "Assumed", "Unknown"}
RATINGS = {
    "Meets", "Partially meets", "Does not meet", "Indicative concern",
    "Not rated (no target)", "Not rated (no evidence)",
}
OWNERSHIP_STATUS = {"Confirmed", "Proposed", "Disputed", "Unknown"}
LEVELS = {"1", "2", "3"}

# A table is recognised by one header that only that table has.
KINDS = {
    "Stakeholder (role)": "ST", "Document requested": "DOC",
    "System (logical name)": "SYS", "L2 capability": "CAP",
    "Meaning and boundary": "DOM", "Authoritative system": "AST",
    "Data owner": "OWN", "Method": "FLW", "Component (logical)": "CMP",
    "Documented?": "GOV", "Reference principle": "PL", "Attribute": "QA",
    "Basis": "F", "Likelihood": "R", "Recommended next step": "N",
    "Reviewer role": "VL",
}
NEEDS_EVIDENCE = {"ST", "DOC", "SYS", "CAP", "DOM", "AST", "OWN", "FLW",
                  "CMP", "GOV", "PL", "QA", "F"}


def refs(cell):
    return ID_ANY.findall(cell)


def parse(text):
    """Return ({kind: {id: row}}, [diagram blocks], [parse errors])."""
    tables = {kind: {} for kind in set(KINDS.values())}
    diagrams, errors = [], []
    in_fence, fence, prev, header = False, [], None, None
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_fence and fence and fence[0].startswith("D5-DIAGRAM"):
                diagrams.append("\n".join(fence))
            in_fence, fence, prev, header = not in_fence, [], None, None
            continue
        if in_fence:
            fence.append(line)
            continue
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
        if kind is not None and len(set(header)) != len(header) and ID_CELL.match(cells[0]):
            errors.append(f"line {number}: duplicate column names in table of {cells[0]}")
            continue
        if kind is None or not ID_CELL.match(cells[0]):
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
    return tables, diagrams, errors


def check(tables, diagrams):
    errors = []

    def err(row_id, message):
        errors.append(f"{row_id}: {message}")

    sys_ids = set(tables["SYS"])
    ids = {k: set(v) for k, v in tables.items()}
    all_ids = set().union(*(ids[k] for k in ids if k != "OWN"))

    # 1. Generic row checks: no empty cells, evidence label, source, known IDs.
    for kind, rows in tables.items():
        for rid, row in rows.items():
            for column, value in row.items():
                if column == "_line":
                    continue
                if not value:
                    err(rid, f"empty cell in '{column}'")
                for token in refs(value):
                    if token not in all_ids:
                        err(rid, f"unknown reference {token} in '{column}'")
            if kind in NEEDS_EVIDENCE and row.get("Evidence") not in EVIDENCE:
                err(rid, f"evidence label '{row.get('Evidence')}' is invalid")
            if "Source" in row and not row["Source"]:
                err(rid, "missing source")

    # 2. Capabilities, systems, domains.
    for cid, cap in tables["CAP"].items():
        support = cap["Supporting systems"]
        if not refs(support) and not support.startswith("No system"):
            err(cid, "needs a system or an explicit 'No system identified'")
        if cap["Domain"] not in ids["DOM"]:
            err(cid, f"unknown domain {cap['Domain']}")
    for sid, system in tables["SYS"].items():
        if not sid.startswith("SYS-"):
            continue
        claimed = set(refs(system["Capabilities supported"]))
        actual = {c for c, cap in tables["CAP"].items()
                  if sid in refs(cap["Supporting systems"])}
        if claimed != actual:
            err(sid, f"capabilities {sorted(claimed)} do not match "
                     f"capability table {sorted(actual)}")
        domains = {a["Domain"] for a in tables["AST"].values()
                   if sid in refs(a["Held in"]) and a["Domain"] in ids["DOM"]}
        if set(refs(system["Main data held (domains)"])) != domains:
            err(sid, f"domains {sorted(refs(system['Main data held (domains)']))} "
                     f"do not match assets held {sorted(domains)}")
    for sid, system in tables["SYS"].items():
        touching = {f for f, flow in tables["FLW"].items()
                    if sid in refs(flow["From"]) + refs(flow["To"])}
        if set(refs(system["Interfaces (flows)"])) != touching:
            err(sid, f"interfaces do not match flows touching it {sorted(touching)}")
    for did, domain in tables["DOM"].items():
        actual = {c for c, cap in tables["CAP"].items() if cap["Domain"] == did}
        if set(refs(domain["Capabilities"])) != actual:
            err(did, f"capabilities do not match capability table {sorted(actual)}")

    # 3. Assets, ownership, flows, components.
    for aid, asset in tables["AST"].items():
        held = set(refs(asset["Held in"]))
        if not held or not held <= sys_ids:
            err(aid, "'Held in' must list known systems")
        authority = asset["Authoritative system"]
        if not authority.startswith("Unknown") and set(refs(authority)) - held:
            err(aid, "authoritative system must be one of the 'Held in' systems")
        if asset["Domain"] not in ids["DOM"] and not asset["Domain"].startswith("Multiple"):
            err(aid, f"unknown domain {asset['Domain']}")
    if set(tables["OWN"]) != ids["AST"]:
        err("OWN", f"ownership rows differ from assets: "
                   f"{sorted(set(tables['OWN']) ^ ids['AST'])}")
    for aid, own in tables["OWN"].items():
        if own["Ownership status"] not in OWNERSHIP_STATUS:
            err(aid, f"invalid ownership status '{own['Ownership status']}'")
        if own["Ownership status"] == "Confirmed" and own["Data owner"] == "Unknown":
            err(aid, "status Confirmed requires a named owner role")
        for column in ("Producers", "Consumers"):
            if not refs(own[column]) and not own[column].startswith("Unknown"):
                err(aid, f"'{column}' must list systems or Unknown")
    for fid, flow in tables["FLW"].items():
        sources, targets = refs(flow["From"]), refs(flow["To"])
        if not set(sources + targets) <= sys_ids:
            err(fid, "source and target must be known systems")
        for aid in refs(flow["Data (assets)"]):
            held = set(refs(tables["AST"][aid]["Held in"])) if aid in ids["AST"] else set()
            for target in targets:
                if target.startswith("SYS-") and target not in held:
                    err(fid, f"target {target} does not hold {aid}")
            if not any(s in held for s in sources if s.startswith("SYS-")):
                err(fid, f"no source holds {aid}")
    held_by_component = set()
    for cid, comp in tables["CMP"].items():
        hosts = set(refs(comp["Hosted in"]))
        for aid in (a for a in refs(comp["Assets held"]) if a.startswith("AST-")):
            held_by_component.add(aid)
            held = set(refs(tables["AST"][aid]["Held in"])) if aid in ids["AST"] else set()
            if hosts and not hosts & held:
                err(cid, f"{aid} is not held in any hosting system")
    for aid in sorted(ids["AST"] - held_by_component):
        err(aid, "asset is not held by any component")

    # 4. Findings, register, next steps, validation.
    cited = set()
    for rid, item in tables["R"].items():
        findings = refs(item["Supporting finding(s)"])
        cited.update(findings)
        if not findings or not set(findings) <= ids["F"]:
            err(rid, "must cite existing findings")
        impact, likelihood = item["Impact"], item["Likelihood"]
        if impact not in LEVELS or likelihood not in LEVELS:
            err(rid, "impact and likelihood must be 1, 2 or 3")
        elif item["Score"] != str(int(impact) * int(likelihood)):
            err(rid, f"score {item['Score']} != {impact} x {likelihood}")
    for fid in sorted(ids["F"] - cited):
        err(fid, "finding is not cited by any register item")
    addressed = {}
    for nid, step in tables["N"].items():
        linked = refs(step["Addresses (register)"])
        if not linked or not set(linked) <= ids["R"]:
            err(nid, "must address existing register items")
            continue
        for rid in linked:
            addressed.setdefault(rid, set()).add(nid)
        top = max(int(tables["R"][r]["Score"]) for r in linked)
        if step["Max score"] != str(top):
            err(nid, f"max score {step['Max score']} != {top}")
        effort = step["Effort"]
        if top >= 6 and effort in ("S", "M"):
            expected = "P1"
        elif (top >= 6 and effort == "L") or (3 <= top <= 5 and effort in ("S", "M")):
            expected = "P2"
        else:
            expected = "P3"
        if step["Priority"] != expected:
            err(nid, f"priority {step['Priority']} != derived {expected}")
    for rid, item in tables["R"].items():
        if set(refs(item["Next step"])) != addressed.get(rid, set()):
            err(rid, "next steps do not match the next-step table")
    for qid, row in tables["QA"].items():
        if row["Rating"] not in RATINGS:
            err(qid, f"invalid rating '{row['Rating']}'")
    for pid, row in tables["PL"].items():
        if row["Rating"] not in RATINGS:
            err(pid, f"invalid rating '{row['Rating']}'")

    # 5. Diagram consistency.
    if len(diagrams) != 1:
        err("diagram", f"expected exactly one D5-DIAGRAM block, found {len(diagrams)}")
    else:
        shown = {t for t in refs(diagrams[0])
                 if t.startswith(("SYS-", "EXT-", "FLW-"))}
        expected = {i for i in sys_ids | ids["FLW"]}
        for missing in sorted(expected - shown):
            err(missing, "missing from the diagram")
        for extra in sorted(shown - expected):
            err(extra, "appears in the diagram but not in the inventory")
    return errors


def spot_check(tables, count, seed):
    """Trace random assets: asset -> system -> capability -> domain -> owner."""
    rng = random.Random(seed)
    assets = sorted(tables["AST"])
    for aid in rng.sample(assets, min(count, len(assets))):
        asset, own = tables["AST"][aid], tables["OWN"].get(aid, {})
        held = refs(asset["Held in"])
        authority = refs(asset["Authoritative system"])
        system = (authority or held or ["?"])[0]
        basis = "authoritative" if authority else "first holder, authority Unknown"
        supporting = [c for c, cap in tables["CAP"].items()
                      if system in refs(cap["Supporting systems"])]
        in_domain = [c for c in supporting
                     if tables["CAP"][c]["Domain"] == asset["Domain"]]
        caps = in_domain or supporting or ["no capability"]
        print(f"{aid} {asset['Asset']} -> {system} ({basis}) -> "
              f"{', '.join(caps)} -> {asset['Domain']} -> "
              f"owner: {own.get('Data owner', '?')}")


def list_unknowns(tables):
    for kind, rows in tables.items():
        for rid, row in rows.items():
            for column, value in row.items():
                if column != "_line" and value.startswith("Unknown"):
                    print(f"{rid}\t{column}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file")
    parser.add_argument("--spot-check", type=int, metavar="N")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--unknowns", action="store_true")
    args = parser.parse_args()

    tables, diagrams, errors = parse(Path(args.file).read_text(encoding="utf-8"))
    if args.spot_check:
        spot_check(tables, args.spot_check, args.seed)
        return 0
    if args.unknowns:
        list_unknowns(tables)
        return 0
    errors += check(tables, diagrams)
    counts = ", ".join(f"{k}={len(v)}" for k, v in sorted(tables.items()))
    print(f"Parsed: {counts}")
    for message in errors:
        print(f"ERROR {message}")
    print(f"{len(errors)} error(s)" if errors else "All checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

---

*End of document. Version 1.1, 2026-10-21.*
