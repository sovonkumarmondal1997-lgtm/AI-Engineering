# Project 04 — Enterprise Conceptual and Logical Data Model

> **Stage:** Stage 2D — Data Architecture
> **Module:** 2D.4 — Conceptual, Logical and Physical Data Modeling
> **Project type:** Enterprise modeling exercise (a validated, traceable model package; no physical design)
> **Roadmap source:** `roadmap-Conceptual-Logical-and-Physical-Data-Modeling.md`, Section 7
> **Project file:** `Projects/04-enterprise-conceptual-and-logical-data-model.md`

---

## 0. Document control

| Item | Value |
| --- | --- |
| Document | Project specification and worked reference, deliverables D1–D14 |
| Version | 1.1 (post-audit) |
| Date | 2026-10-21 |
| Status | Complete as a project specification and worked reference. **Every Northbridge value is illustrative. No stakeholder or independent reviewer has confirmed anything in Section 6. Rule status `Confirmed` means only that a recorded (hypothetical) statement supports the rule.** |
| Audience | Learner running the project; independent reviewer auditing it |
| Scenario | *Northbridge Bank*, a fictional mid-sized retail and business bank (roadmap Section 7.2) |
| Evidence rule | Every row carries an evidence label (Section 4.3) where it states a fact or a claim |
| Companion tool | Model checker and scenario runner, Appendix B (`check_data_model.py`) |

**Change log**

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-10-21 | First complete design |
| 1.1 | 2026-10-21 | Post-audit: renamed `date_of_birth` to `birth_date` (it violated the date naming rule); rewrote 13 dictionary definitions that restated the element name; added the scope boundary, relationship naming convention, compatibility convention with consumer inventory, and readiness decision that the module's checklists require; corrected the count of provisional rules in FND-06; hardened the checker (leaf dependencies projected from the root, homonym contexts compared with the glossary, primary-key consistency, attribute names validated inside rule specs, stop on structural errors, clear failure on malformed tables); confirmed the embedded checker equals the tested one |

**Reading order.** Sections 1–5 explain the project and how to run it. Section 6 is a complete,
executable worked reference (D1–D14). Section 7 is the quality gate. Section 8 holds templates for a
real organisation. Sections 9–11 cover pitfalls, hand-off and self-assessment. Appendix B is the
checker, which runs the model's rules against test data.

---

## 1. Project overview

### 1.1 What this project is

An **enterprise conceptual and logical data model** is a shared, precise statement of what an
organisation's core data means: the things the business tracks, how they relate, which rules hold, and
how each element is defined, named and owned. It is the step between a business problem ("reports
disagree about what a customer is") and a physical design ("which tables and which engine").

This project builds that model for customer, account and transaction data, and — unlike a diagram
exercise — makes it **testable**. The business rules are written in a small, precise rule language;
the model is loaded with a synthetic dataset; and each rule is exercised by valid and invalid
scenarios that the checker runs.

```text
Business problem ─► terms, rules and requirements ─► conceptual model ─► logical model
        ─► keys, relationships, normalisation ─► naming standard and dictionary
        ─► scenarios that accept and reject ─► review ─► final package with deferred decisions
```

### 1.2 Why organisations need it

| Situation | What goes wrong without it | What the model provides |
| --- | --- | --- |
| Each system defines "customer" differently | Reports disagree; the regulator asks for definitions | A glossary with context-specific meanings and one enterprise definition |
| Joint accounts and name changes are handled by workarounds | History is lost; counts are wrong | Associative entities and valid intervals, with rules that reject bad data |
| A platform migration starts from table names | Old structure and old mistakes are copied | A logical model whose rules a domain expert can check |
| Definitions live in people's heads | New staff, integrations and reports re-invent meaning | A dictionary with non-circular definitions, owners and traceability |

### 1.3 Business and modeling objectives

**Business objective (roadmap).** Give the organisation a shared, precise understanding of its core
customer, account and transaction data so that reports, integrations and later platform design start
from agreed meanings.

**Modeling objectives.** Analyse the domain, identify entities and relationships, define business
rules, produce conceptual and logical models, and validate them.

### 1.4 What this project is not

| It is not | Because |
| --- | --- |
| A physical schema | No engine, data types, indexes, partitioning or DDL; those are deferred to module 2D.5 |
| A dimensional, Data Vault or event design | Needs are noted (Step 13); structures belong to later modules |
| A tooling or platform choice | The model is vendor-neutral |
| A source of facts about a real bank | Every Northbridge value is an illustrative assumption |

### 1.5 Success criteria

The package succeeds when a domain expert can check its rules, another architect can reuse its
definitions, an independent reviewer completes the Topic 8 checklist with no open blocking or major
finding, and the checker runs every scenario with an explained outcome (roadmap Section 7.7).

---

## 2. How to use this file

| | Mode A — Worked reference | Mode B — Real or realistic organisation |
| --- | --- | --- |
| Purpose | Study a complete, executable example; critique it | Produce your own model package |
| Facts | The roadmap scenario only; everything else is invented | Your stakeholders, documents and systems |
| What you do | Read Section 6; run the checker; try breaking a rule | Follow Section 5; use Section 8; produce your own D1–D14 |
| Output | Understanding and a critique list | A reviewed D1–D14 and a met completion gate |

**Rules in both modes**

1. **Write rules as sentences first, then model them.** Every rule has a source, a representation and tests.
2. **Never fill a gap with an invented rule.** Mark it `Assumed` or `Open` and ask the domain expert.
3. **Conceptual means no data types and no platform terms.** The logical model adds precision, not technology.
4. **One term, one meaning per context.** Homonyms and synonyms are registered.
5. **Resolve every many-to-many** with an associative entity that carries the relationship's own attributes.
6. **Do not design physical structures.** List them as deferred.
7. **Keep test data synthetic.** The dataset contains no real person or account.

> **Honesty note for Mode A.** The roadmap names the scenario, the candidate entities and four
> illustrative assumptions. All interview statements, rules, definitions, owners and test data in
> Section 6 were invented for the exercise and are labelled `Illustrative assumption`. The status
> `Confirmed` on a rule means that a recorded hypothetical statement supports it; nobody has validated
> it. `Open` rules are provisional: their scenarios pass under the stated assumption, not under a
> business decision.

---

## 3. Concepts applied

| Concept (lesson) | Where it is applied |
| --- | --- |
| Conceptual, logical and physical levels; transformation; traceability; deferred decisions ([Topic 1](../01-conceptual-logical-and-physical-models.md)) | D6 and D7; the conceptual-to-logical mapping CLM; the physical-term scan; deferred decisions DF |
| Entities, relationships, cardinality, keys, constraints, supertypes and time-dependent relationships ([Topic 2](../02-entities-relationships-cardinality-and-constraints.md)) | D4 to D9; the rules register; the executable scenarios |
| Normalisation, functional dependencies, lossless joins, dependency preservation ([Topic 3](../03-normalization-and-relational-modeling.md)) | Section 6.9: dependency tables, candidate keys and normal forms computed, decomposition proofs |
| Dimensional modeling and grain ([Topic 4](../04-dimensional-modeling-facts-dimensions-and-grain.md)) | Grain statements for every entity; analytical needs NE-05 and NE-06 (structures deferred) |
| Data Vault and historical modeling ([Topic 5](../05-data-vault-and-historical-modeling.md)) | Valid-interval history; the record-time gap (OQ-11); needs NE-01 to NE-04 and NE-08 (structures deferred) |
| Event modeling and domain-driven design ([Topic 6](../06-event-modeling-and-domain-driven-design.md)) | Bounded contexts BCX; homonym register; event need NE-07 |
| Schema evolution and backward compatibility ([Topic 7](../07-schema-evolution-and-backward-compatibility.md)) | Change classifications CH-01 to CH-07; interval and naming conventions designed for change |
| Model review, naming standards and data dictionaries ([Topic 8](../08-model-review-naming-standards-and-data-dictionaries.md)) | D11 naming standard (checked by its own patterns); D12 dictionary; review RV and findings FND |

**Roadmap project parts**

| Project part | Topics | Steps | Deliverables |
| --- | --- | --- | --- |
| Conceptual to logical transformation | 1 | 9–11 | D6, D7 |
| Entities, relationships, constraints | 2 | 5–8 | D4, D5, D8, D9 |
| Normalisation decisions | 3 | 12 | D9 |
| Analytical, historical and event needs | 4, 5, 6 | 13 | D10 |
| Change considerations | 7 | 13 | D10 |
| Naming, dictionary, review | 8 | 14–16 | D11, D12, D13 |

**Coverage of the module's practice exercises** (`practice-questions.md`, Section F)

| Exercise | How this project covers it |
| --- | --- |
| F0 level classification | The checker scans the conceptual model for physical terms; deferred decisions are listed (DF) |
| F1 rule register (at least 12 rules) | 32 rules with source, representation, tests and status (Section 6.5) |
| F2 entity and relationship inventory | Candidate decisions (D4), conceptual relationships (D6), logical relationships (D8) |
| F3 dependency and decomposition proof | Section 6.9: two legacy relations decomposed, with machine-checked proofs |
| F5, F6 history and event design | Needs only (NE); the exercises themselves belong to later modules |
| F7 compatibility | Change classification CH-01 to CH-07 |
| F8 formal review | Checklist RV and findings FND |
| F9 integrated package | This project |

**Carry-in from earlier modules.** Ownership gaps and the authority of each concept come from Module 2D.1
(Project 01, [inventory](../../01-Data-Architecture-Foundations-and-Principles/Projects/01-current-state-data-architecture-inventory.md));
the requirement and decision-record method from Module 2D.2
([Project 02](../../02-Requirements-Constraints-and-Architecture-Decisions/Projects/02-requirements-and-architecture-decision-pack.md));
and the domain-ownership direction from Module 2D.3
([Project 03](../../03-Data-Architecture-Patterns-and-Reference-Architectures/Projects/03-reference-architecture-pattern-comparison.md)).
Those projects use their own illustrative models; this project's identifiers are independent.

---

## 4. Project governance and conventions

### 4.1 Roles and decision rights (RACI)

`R` responsible, `A` accountable (exactly one per row), `C` consulted, `I` informed.

| Activity or decision | Sponsor (STK-01) | Lead modeler (STK-13) | Domain owners (STK-02 to STK-04) | Domain expert (STK-11) | Control functions (STK-07, STK-09) | Independent reviewer (STK-12) |
| --- | --- | --- | --- | --- | --- | --- |
| Approve scope and exclusions | A | R | C | C | C | I |
| Confirm definitions and rules | I | R | C | A | C | I |
| Confirm ownership | C | R | A | C | C | I |
| Approve the naming standard | I | R | C | C | A | C |
| Accept the conceptual model | C | R | A | C | C | I |
| Accept the logical model | C | R | C | C | A | C |
| Independent review of the package | I | C | I | I | I | A |

The modeler proposes and records; the domain expert confirms meaning; the governance function owns the
standard. The modeler never confirms their own rule.

### 4.2 Status, severity and notation

**Rule status.** `Confirmed` (a recorded statement supports it, and in Mode B the stakeholder has confirmed it),
`Assumed` (a modeling assumption to be validated) and `Open` (unresolved; a provisional version may be
modelled and is labelled).

**Candidate decision.** `Accept` (drawn in the conceptual model), `Relationship` (shown as a conceptual
relationship and resolved into an entity logically), `Refinement` (appears only logically), `Reject`, `Open`.

**Cardinality notation.** `min..max` at each end: `1` exactly one, `0..1` optional one, `0..*` zero or many,
`1..*` one or many. "Parents per child" is read from the child's side of the foreign key.

**Valid intervals.** `[valid_from, valid_to)`: the start is included, the end is excluded, and an absent end
means the fact still holds. This convention is Assumption ASM-01.

**Logical domains.** `Identifier`, `Code`, `Text`, `Date`, `Timestamp`, `Amount`, `Quantity`, `Flag`. They state
the nature of the value, not a platform type.

**Review severity** (Topic 8). `Blocking` prevents safe approval; `Major` must be corrected before final approval
unless an authorised, time-bound waiver exists; `Minor` is tracked. Defect types: `Semantic`, `Structural`,
`Naming`, `Documentation`.

### 4.3 Evidence labels

| Label | Meaning |
| --- | --- |
| Verified fact | Supported by inspected evidence or a confirmed source |
| Stakeholder statement | What a person said; not independently verified |
| Illustrative assumption | A value invented for learning or planning |
| Inference | A reasoned interpretation, open to challenge |
| Open question | A matter not yet resolved |

### 4.4 ID conventions

IDs are numbered (two digits; three for the longest tables), stable and never reused. Cross-references use IDs
only, which makes traceability machine-checkable.

| Prefix | Object | Prefix | Object |
| --- | --- | --- | --- |
| STK, CM, INT | Stakeholder, consumer use, interview statement | KY, RL | Key, logical relationship |
| REQ, PRC, BCX | Requirement, process, bounded context | FD, LR, DP, NF | Dependency, relation, decomposition step, normal form |
| GL, SY, HM | Glossary term, synonym, homonym | MD, OQ, ASM | Modeling decision, open question, assumption |
| CE, CR, CLM | Candidate entity, conceptual relationship, conceptual-to-logical mapping | NE, DF, CH | Need, deferred decision, change scenario |
| AU | Authority and ownership entry | NS, DD | Naming rule, dictionary entry |
| BR | Business rule | DAT, SCN | Test data row, scenario |
| LE, AT | Logical entity, attribute | RV, FND, TR, VL | Review area, finding, trace row, validation entry |

### 4.5 Confidentiality and handling

The test dataset is synthetic. Do not copy real customer, account or transaction data into the package.
Record roles, not named individuals, in shared artefacts. Mark the package with the organisation's
classification and record the version and date on every artefact.

### 4.6 Suggested workspace layout (Mode B, optional)

```text
northbridge-data-model/                     # replace with the organisation name
├── 00-scope/            d1-scope.md, d2-stakeholders-and-requirements.md
├── 01-language/         d3-glossary.md, d11-naming-standard.md
├── 02-model/            d4-entities.md, d6-conceptual.md, d7-logical.md, d8-relationships.md, d9-keys-and-normalisation.md
├── 03-rules/            d5-rules-register.md, test-data.md, scenarios.md
├── 04-documentation/    d12-dictionary.md
├── 05-decisions/        d10-decisions-and-open-questions.md
├── 06-review/           d13-validation-and-review.md, findings.md
├── 07-summary/          d14-summary.md
└── tools/               check_data_model.py (adapt header names)
```

Rationale: language, model, rules, documentation, decisions and review are kept in separate layers so each can be
reviewed and versioned independently. Keep one source of truth per definition; the dictionary, the diagram and
the rules must never be edited separately.

---

## 5. Execution plan

### 5.1 Timeline and effort (planning estimate, mid-sized organisation)

| Week | Steps | Main outcome | Effort (person-days, indicative) |
| --- | --- | --- | --- |
| 1 | 1, 2, 3, 4 | Scope; stakeholders and consumers; verbatim statements, terms and rules; process and boundary map | 6–8 |
| 2 | 5, 6, 7, 8 | Entities, attributes, relationships, assumption and open-question log | 7–9 |
| 3 | 9, 10 | Conceptual model validated by walk-through | 4–5 |
| 4 | 11, 12, 13 | Logical model; keys and normalisation; history, analytical and event needs | 7–9 |
| 5 | 14, 15 | Naming standard, glossary and dictionary | 5–7 |
| 6 | 16, 17, 18 | Review; scenario runs; revisions | 6–8 |
| 7 | 19 | Final package, summary and challenge round | 3–4 |

Total indicative effort: **38–50 person-days**, plus about one day per interviewed stakeholder group. These are
planning figures, not measured results.

### 5.2 Definitions of ready and done

| | Criteria |
| --- | --- |
| **Ready** | Sponsor named; scope question agreed; access to stakeholders and a domain expert; a place to keep the package under version control |
| **Done** | Completion gate (Section 7.5) fully met; D1–D14 dated; independent reviewer has completed the Topic 8 checklist |

### 5.3 The nineteen steps

Each step lists purpose, inputs, actions, the questions to answer, outputs and validation, with pitfalls
and the lessons it draws on.

#### Step 1 — Define the problem, objectives and modeling scope

- **Purpose:** state what is modelled and what is not.
- **Inputs:** scenario, sponsor goals.
- **Actions:** write the scope statement, exclusions and labelled assumptions; state that the project stops at the logical model.
- **Questions:** What is modelled and what is not?
- **Output:** D1.
- **Validation:** the sponsor-role reviewer confirms scope; exclusions are as firm as inclusions.
- **Pitfalls:** scope that includes physical design or ETL.
- **Draws on:** Topic 1 (5.1).

#### Step 2 — Identify stakeholders and model consumers

- **Purpose:** know who uses the model and for what.
- **Inputs:** scenario, organisation context.
- **Actions:** build the stakeholder register; map each consumer to a stated use; include governance, compliance and data engineering.
- **Questions:** Who uses the model and for what?
- **Output:** stakeholder and consumer list (D2 part).
- **Validation:** each consumer has a stated use.
- **Pitfalls:** treating only the sponsor as a consumer.
- **Draws on:** Topic 1, Topic 8.

#### Step 3 — Gather requirements, terms and rules

- **Purpose:** collect the meaning the business already uses.
- **Inputs:** interviews and documents.
- **Actions:** record statements verbatim before interpreting them; extract terms and draft rules; list words that mean different things.
- **Questions:** Which words mean different things?
- **Output:** requirements summary; term list; draft rules (D2, D3 part, D5 part).
- **Validation:** each rule has a source.
- **Pitfalls:** merging a quote with its interpretation.
- **Draws on:** Topic 1 (5.2), Topic 6 (5.2).

#### Step 4 — Identify processes and domain boundaries

- **Purpose:** explain why one word means different things.
- **Inputs:** Steps 1–3; Module 2D.1 Topic 3.
- **Actions:** map processes to bounded contexts; record the local term for the party in each; register homonyms.
- **Questions:** Where do meanings change?
- **Output:** process and boundary map (D1 part).
- **Validation:** boundaries explain each term conflict.
- **Pitfalls:** forcing one universal Customer.
- **Draws on:** Topic 6 (5.1, 5.2).

#### Step 5 — Identify candidate entities and their meanings

- **Purpose:** decide what is a thing the business tracks.
- **Inputs:** Steps 3–4.
- **Actions:** extract candidates; define each from the business view with inclusions and exclusions; decide Accept, Relationship, Refinement, Reject or Open.
- **Questions:** Is each a thing the business tracks?
- **Output:** entity inventory (D4).
- **Validation:** each definition is free of circularity.
- **Pitfalls:** treating every noun as an entity; naming entities after system tables.
- **Draws on:** Topic 2 (4.1–4.3).

#### Step 6 — Identify attributes; separate identifiers from descriptors

- **Purpose:** say what each fact is and what identifies an instance.
- **Inputs:** Step 5.
- **Actions:** list attributes with their logical domain, requiredness and allowed values; choose stable identifiers.
- **Questions:** What identifies an instance, and is it stable?
- **Output:** attribute inventory (D7 part).
- **Validation:** every entity has an identifier.
- **Pitfalls:** using a mutable value, such as a name, as an identifier.
- **Draws on:** Topic 2 (5.2).

#### Step 7 — Define relationships, cardinality, optionality and constraints

- **Purpose:** make every link unambiguous in both directions.
- **Inputs:** Steps 5–6.
- **Actions:** write both-direction statements with minimum and maximum; resolve many-to-many relationships with associative entities.
- **Questions:** What are the minimum and maximum in each direction?
- **Output:** relationship inventory (D8); rules register (D5 part).
- **Validation:** no relationship lacks both directions.
- **Pitfalls:** an unqualified line between two boxes.
- **Draws on:** Topic 2 (4.4, 4.5, 5.1).

#### Step 8 — Resolve ambiguities; record assumptions and questions

- **Purpose:** keep unresolved matters visible.
- **Inputs:** Steps 3–7.
- **Actions:** list interpretations; ask the domain expert or assume and flag; record owner and status.
- **Questions:** Which ambiguity changes the structure?
- **Output:** assumption and open-question log (D10 part).
- **Validation:** each item has an owner and a status.
- **Pitfalls:** hiding a design decision inside the diagram.
- **Draws on:** Topic 2 (6.1, 6.9).

#### Step 9 — Create the conceptual model

- **Purpose:** give business readers one view of the core concepts.
- **Inputs:** Steps 5–8.
- **Actions:** draw concepts and relationships with business terms; no data types, keys or platform terms.
- **Questions:** Can a business reader follow it?
- **Output:** conceptual model (D6).
- **Validation:** terms match the glossary.
- **Pitfalls:** join tables or column names in the conceptual view.
- **Draws on:** Topic 1 (4.2, 6.4).

#### Step 10 — Validate the conceptual model

- **Purpose:** test it with realistic cases before refining.
- **Inputs:** Step 9; requirements.
- **Actions:** walk through scenarios with stakeholders; record findings.
- **Questions:** Does it express the rules without distortion?
- **Output:** validation notes.
- **Validation:** findings are addressed or logged.
- **Pitfalls:** judging by diagram aesthetics.
- **Draws on:** Topic 1 (6.6).

#### Step 11 — Transform to the logical model

- **Purpose:** add the precision the rules need.
- **Inputs:** Steps 9–10.
- **Actions:** add attributes, identifiers and foreign keys; resolve relationships; map every conceptual element to a logical one or document the refinement.
- **Questions:** What new information is needed?
- **Output:** logical model (D7); conceptual-to-logical mapping.
- **Validation:** every concept traces forward.
- **Pitfalls:** quietly adding or dropping an entity.
- **Draws on:** Topic 1 (5.3).

#### Step 12 — Define keys, integrity and normalisation decisions

- **Purpose:** make each fact stored once and each key a candidate key.
- **Inputs:** Step 11.
- **Actions:** define primary, alternate and foreign keys; state functional dependencies; compute candidate keys and normal forms; prove decompositions are lossless and preserve dependencies.
- **Questions:** Is each fact stored once?
- **Output:** key and constraint definitions (D9); normalisation notes.
- **Validation:** lossless-join and dependency checks pass.
- **Pitfalls:** deriving a dependency from sample data.
- **Draws on:** Topic 3, Topic 2 (5.3, 5.4).

#### Step 13 — Evaluate historical, analytical and event needs

- **Purpose:** note what the logical model must allow for without designing it.
- **Inputs:** Steps 3, 11; Topics 4–7.
- **Actions:** record which attributes and relationships need history, which analytical grain is implied and which events matter; list anticipated changes and classify them.
- **Questions:** What must the logical model allow for?
- **Output:** needs note and change considerations (D10 part).
- **Validation:** adjustments do not exceed scope.
- **Pitfalls:** designing vaults, stars or event streams here.
- **Draws on:** Topics 4–7.

#### Step 14 — Define naming conventions and definitions

- **Purpose:** one term, one meaning.
- **Inputs:** Steps 5–12.
- **Actions:** write the naming standard as testable patterns with good and poor examples; finalise definitions; run the synonym and homonym check.
- **Questions:** Are terms unique and meaningful?
- **Output:** naming standard (D11); glossary (D3).
- **Validation:** the synonym/homonym check is clean.
- **Pitfalls:** a standard that nothing checks.
- **Draws on:** Topic 8 (4.2, 4.3).

#### Step 15 — Create the data dictionary

- **Purpose:** make the model reusable.
- **Inputs:** Steps 11–14.
- **Actions:** populate an entry for every entity and attribute with a definition that adds information beyond the name, constraints, allowed values, source, owner and steward.
- **Questions:** Is each entry complete and non-circular?
- **Output:** data dictionary (D12).
- **Validation:** coverage is 100% and a sample audit passes.
- **Pitfalls:** definitions that restate the name.
- **Draws on:** Topic 8 (4.4, 5.1, 5.2).

#### Step 16 — Review for completeness, consistency, redundancy and semantics

- **Purpose:** find defects that change meaning.
- **Inputs:** Steps 9–15.
- **Actions:** apply the Topic 8 checklist; log findings with type and severity.
- **Questions:** Any defect that changes meaning?
- **Output:** review findings.
- **Validation:** findings are classified by severity.
- **Pitfalls:** treating cosmetic and semantic findings alike.
- **Draws on:** Topic 8 (5.3–5.5).

#### Step 17 — Validate against scenarios and edge cases

- **Purpose:** show the model accepts what it should and rejects what it should.
- **Inputs:** the model, the dataset and the scenario set.
- **Actions:** run at least 20 scenarios, at least 8 invalid; explain every outcome.
- **Questions:** Does the model accept and reject correctly?
- **Output:** scenario results (D13).
- **Validation:** all outcomes are explained.
- **Pitfalls:** only valid cases.
- **Draws on:** Topic 2 (6.8).

#### Step 18 — Revise

- **Purpose:** correct the package and keep it consistent.
- **Inputs:** Steps 16–17.
- **Actions:** correct the model, glossary and dictionary together; update traceability; re-run key scenarios; keep a change log.
- **Questions:** Do changes ripple?
- **Output:** revised package; change log.
- **Validation:** key scenarios are re-run.
- **Pitfalls:** editing the diagram without the dictionary.
- **Draws on:** Topic 8 (6.2).

#### Step 19 — Prepare the final package and decision summary

- **Purpose:** hand over a reviewable package.
- **Inputs:** all artefacts.
- **Actions:** assemble D1–D14; summarise key decisions, open items and deferred physical decisions.
- **Questions:** What must the next module decide?
- **Output:** D14.
- **Validation:** a reviewer confirms traceability.
- **Pitfalls:** hiding open questions.
- **Draws on:** Topic 1 (5.6), Topic 8.

---

## 6. Worked reference — Northbridge Bank

> **Everything in this section is illustrative.** Only the scenario in 6.1 and the candidate entities come
> from the roadmap. Every other value is `Illustrative assumption`, `Inference` or `Open question`. No real
> person, account or product is used. The tables below are the model: the checker (Appendix B) reads them,
> loads the test data, and runs every rule and scenario. Run it after any edit.

**Deliverable map**

| Deliverable | Section | Deliverable | Section |
| --- | --- | --- | --- |
| D1 Scope and assumptions | 6.1 | D8 Relationship and cardinality definitions | 6.8 |
| D2 Stakeholders and requirements | 6.2 | D9 Key and integrity constraint definitions | 6.9 |
| D3 Business glossary | 6.3 | D10 Modeling decisions and unresolved questions | 6.10 |
| D4 Entity inventory | 6.4 | D11 Naming standards | 6.11 |
| D5 Business rules and constraints register | 6.5 | D12 Data dictionary | 6.12 |
| D6 Conceptual data model | 6.6 | D13 Validation and review findings | 6.13 |
| D7 Logical data model | 6.7 | D14 Final project summary | 6.14 |

### 6.1 D1 — Project scope and assumptions (Steps 1 and 4)

**Scenario (roadmap).** Northbridge is a fictional mid-sized retail and business bank. Customer, account and
transaction data are spread across a core banking system, a cards platform and a CRM, each with its own
definition of "customer" and "account". Reports disagree, and a regulator has asked for clearer definitions and
accountability for customer and account data.

| Element | Statement |
| --- | --- |
| Business problem | No agreed enterprise definition of customer, account, holding relationship, product and transaction; relationships and rules differ by system |
| Objective | A validated, traceable model package whose rules a domain expert can check and whose definitions another architect can reuse |
| In scope | Conceptual and logical models for party, customer role, account, account holding, product, branch, transaction, address and contact; business rules; glossary; naming standard; dictionary; review and validation |
| Out of scope | Physical design; loan servicing and collections detail; card authorisation detail; marketing data; security implementation; ETL; reporting design; full historical and event modeling (only needs that affect the logical design are noted) |
| Level | Conceptual and logical; vendor-neutral; no data types beyond logical domains |
| Labelled assumptions | ASM-01 to ASM-05; the roadmap's four illustrative assumptions (a customer can be a person or an organisation; an account can have several holders with roles; closed accounts are retained; a legal name can change) |

**Business processes in scope and the contexts they run in** (Step 4)

| ID | Business process | In scope | Bounded context | Entities touched | Evidence |
| --- | --- | --- | --- | --- | --- |
| PRC-01 | Customer onboarding | Yes | BCX-01; BCX-05 | Party, Person, Organisation, PartyName, PartySourceIdentifier, CustomerRole, Address, ContactPoint | Illustrative assumption |
| PRC-02 | Account opening and holding | Yes | BCX-02; BCX-05 | Account, AccountHolding, Product, Branch, Guardianship | Illustrative assumption |
| PRC-03 | Product subscription | Partly: an account is opened under one product; other subscriptions are open (OQ-05) | BCX-02; BCX-05 | Product, ProductBundleComponent, Account | Illustrative assumption |
| PRC-04 | Payment and transaction posting | Yes | BCX-02; BCX-03 | Transaction, Account | Illustrative assumption |

**Bounded contexts and the local word for the party.** Boundaries explain why two teams use one word for two things.

| ID | Bounded context | Local term for the party | Meaning | Source system | Evidence |
| --- | --- | --- | --- | --- | --- |
| BCX-01 | CRM and relationship management | Contact | A person or organisation managed for communication, not necessarily a bank customer | CRM | Illustrative assumption |
| BCX-02 | Retail core banking | Account holder | A party that holds a deposit account under retail rules | Core banking system | Illustrative assumption |
| BCX-03 | Cards | Cardholder | A person authorised to use a card, who may not own the card account | Cards platform | Illustrative assumption |
| BCX-04 | Lending | Applicant | A party named on a loan application, who may not yet be a customer | Loan origination system | Illustrative assumption |
| BCX-05 | Enterprise model (this project) | Party and customer role | A real-world person or organisation, and the period during which it acts as a customer | Not applicable: the model is the target | Illustrative assumption |

**Assumptions**

| ID | Assumption | Status | Affects | Validation | Evidence |
| --- | --- | --- | --- | --- | --- |
| ASM-01 | Valid periods are start-inclusive and end-exclusive, and an absent end means the fact still holds | Assumed | All entities with valid_from and valid_to | Confirm with the compliance officer and the data engineering lead | Illustrative assumption |
| ASM-02 | A Party is exactly one of PERSON or ORGANISATION, and no third kind exists in scope | Assumed | Party; Person; Organisation | Confirm with the retail domain expert | Illustrative assumption |
| ASM-03 | Product bundles exist and are limited to bundle-capable products | Assumed | Product; ProductBundleComponent | Confirm with the retail domain owner (OQ-09) | Illustrative assumption |
| ASM-04 | Closed accounts are retained indefinitely at the logical level; retention periods are decided elsewhere | Assumed | Account; AccountHolding; Transaction | Confirm with compliance | Illustrative assumption |
| ASM-05 | The three source systems are core banking, cards and CRM; lending is out of detail | Assumed | PartySourceIdentifier | Confirm the systems list | Illustrative assumption |

### 6.2 D2 — Stakeholders and requirements summary (Steps 2 and 3)

| ID | Stakeholder (role) | Group | Interest | Evidence |
| --- | --- | --- | --- | --- |
| STK-01 | Chief data officer | Sponsor | A shared, precise understanding of customer, account and transaction data | Illustrative assumption |
| STK-02 | Head of retail | Business owner | Retail customer and deposit-account definitions | Illustrative assumption |
| STK-03 | Head of lending | Business owner | Applicant and borrower identity reuse | Illustrative assumption |
| STK-04 | Head of cards | Business owner | Cardholder identity linked to parties and accounts | Illustrative assumption |
| STK-05 | Finance lead | Consumer | Consistent counts of customers and accounts | Illustrative assumption |
| STK-06 | Risk lead | Consumer | Joins across customers, accounts and transactions | Illustrative assumption |
| STK-07 | Compliance officer | Control function | Evidence of who holds which account and when | Illustrative assumption |
| STK-08 | Data engineering lead | Consumer | A logical model to hand to physical design and integration | Illustrative assumption |
| STK-09 | Data governance lead | Control function | Definitions, owners and naming that survive change | Illustrative assumption |
| STK-10 | Report authors representative | Consumer | Stable definitions to build reports on | Illustrative assumption |
| STK-11 | Domain expert, retail operations (role-played) | Domain expert | Rules as operations actually apply them | Illustrative assumption |
| STK-12 | Independent reviewer | Review | Evidence that the model and its rules hold | Illustrative assumption |
| STK-13 | Lead modeler | Author | A reproducible, validated model package | Illustrative assumption |

**Model consumers and their stated use** (each consumer has a use)

| ID | Consumer | Model use | Entities used | Evidence |
| --- | --- | --- | --- | --- |
| CM-01 | STK-02 | Agree what a customer and an account holder are for retail reporting | Party, CustomerRole, AccountHolding | Illustrative assumption |
| CM-02 | STK-03 | Identify applicants who are already known parties and reuse their identity | Party, CustomerRole, PartySourceIdentifier | Illustrative assumption |
| CM-03 | STK-04 | Link cardholder identities to parties and accounts | Party, PartySourceIdentifier, Account | Illustrative assumption |
| CM-04 | STK-05 | Count customers and accounts on one definition | CustomerRole, Account | Illustrative assumption |
| CM-05 | STK-06 | Join customers, accounts and transactions for exposure | Party, Account, AccountHolding, Transaction | Illustrative assumption |
| CM-06 | STK-07 | Show who held an account, under which name, on a given date | AccountHolding, PartyName, Guardianship | Illustrative assumption |
| CM-07 | STK-08 | Use the logical model as the input to physical design and integration | All logical entities | Illustrative assumption |
| CM-08 | STK-09 | Own definitions, owners and the naming standard | Dictionary, glossary | Illustrative assumption |
| CM-09 | STK-10 | Build reports on stable, documented definitions | Account, Transaction, CustomerRole | Illustrative assumption |

**Interview and workshop statements** (hypothetical; recorded verbatim before interpretation)

| ID | Stakeholder | Verbatim statement (hypothetical) | Classification | Extracted terms and rules | Evidence |
| --- | --- | --- | --- | --- | --- |
| INT-01 | STK-02 | "A customer is anyone who holds an account with us, but marketing counts anyone with a contact record." | Conflict | Terms: customer, contact. Homonym across contexts (HM-01). | Illustrative assumption |
| INT-02 | STK-04 | "In cards, the customer is the cardholder, and the cardholder is not always the person who owns the account." | Conflict | Terms: cardholder, account owner. Homonym (HM-01). | Illustrative assumption |
| INT-03 | STK-07 | "The regulator wants to know who holds each account and who held it on a given date." | Need | Rule: holders are recoverable at any past date (REQ-04). | Illustrative assumption |
| INT-04 | STK-11 | "An account can have several holders, and each holder has a role such as primary or joint." | Rule | Rule: many holders per account, each with a role (REQ-03). | Illustrative assumption |
| INT-05 | STK-11 | "People change their legal name, and the regulator needs the name that applied when a transaction was posted." | Rule | Rule: legal-name history with dates (REQ-05). | Illustrative assumption |
| INT-06 | STK-02 | "Companies bank with us too, so a customer can be a person or an organisation." | Rule | Rule: a Party is a person or an organisation (REQ-02). | Illustrative assumption |
| INT-07 | STK-11 | "We keep closed accounts; nothing is deleted when an account closes." | Rule | Rule: closed accounts are retained with a closing date (REQ-06). | Illustrative assumption |
| INT-08 | STK-07 | "A minor can only hold an account jointly with a guardian who has authority; whether a minor may hold alone is not decided." | Open question | Rule: minor holders need guardian authority (REQ-09); open (OQ-01). | Illustrative assumption |
| INT-09 | STK-05 | "Finance counts a customer as active if they have an open account; risk counts anyone with activity in twelve months." | Conflict | Term: active customer has two meanings (REQ-14, OQ-06). | Illustrative assumption |
| INT-10 | STK-08 | "Each system numbers customers its own way; we need one identifier and a map back to the source numbers." | Need | Rule: one Party identifier with source mappings (REQ-08). | Illustrative assumption |
| INT-11 | STK-11 | "Every transaction belongs to exactly one account and cannot exist without it." | Rule | Rule: mandatory single account per transaction (REQ-07). | Illustrative assumption |
| INT-12 | STK-09 | "Names should mean one thing. If two teams use the same word differently, give them different names." | Need | Rule: one term, one meaning (REQ-12). | Illustrative assumption |
| INT-13 | STK-11 | "A product can be sold as a bundle of other products, but a bundle cannot contain itself." | Rule | Rule: acyclic bundles (REQ-11); bundle scope open (OQ-09). | Illustrative assumption |
| INT-14 | STK-11 | "An account may be assigned to a branch, but accounts being opened may not have one yet." | Rule | Rule: optional branch (REQ-10). | Illustrative assumption |

**Requirements**

| ID | Requirement statement | Priority | Source | Satisfied by | Evidence |
| --- | --- | --- | --- | --- | --- |
| REQ-01 | The enterprise shall publish one definition each of party, customer, account, account holding, product and transaction | Must | STK-01; INT-01 | GL-01; GL-07; GL-15; GL-17; GL-20; GL-24; BR-01 | Illustrative assumption |
| REQ-02 | The model shall represent customers that are persons and customers that are organisations | Must | INT-06 | BR-02; BR-03 | Illustrative assumption |
| REQ-03 | The model shall let an account have several holders, each with a role and a period | Must | INT-04 | BR-17; BR-20 | Illustrative assumption |
| REQ-04 | The model shall let the holders of an account on any past date be recovered | Must | INT-03 | BR-18; BR-19 | Illustrative assumption |
| REQ-05 | The model shall let the legal name of a party on any past date be recovered | Must | INT-05 | BR-04; BR-05 | Illustrative assumption |
| REQ-06 | The model shall retain closed accounts with their closing date | Must | INT-07 | BR-14 | Illustrative assumption |
| REQ-07 | The model shall tie every transaction to exactly one account | Must | INT-11 | BR-28 | Illustrative assumption |
| REQ-08 | The model shall map each source-system customer identifier to one party | Must | INT-10 | BR-06 | Illustrative assumption |
| REQ-09 | The model shall allow a minor to hold an account only under a guardian with authority | Should | INT-08 | BR-21; BR-22; BR-23 | Illustrative assumption |
| REQ-10 | The model shall allow an account to have no branch while it is being opened | Should | INT-14 | BR-13 | Illustrative assumption |
| REQ-11 | The model shall prevent a product bundle from containing itself directly or indirectly | Should | INT-13 | BR-25; BR-26; BR-27 | Illustrative assumption |
| REQ-12 | Each business term shall have one meaning within a context, and homonyms shall be distinguished | Must | INT-12; INT-01; INT-02 | GL-07; HM-01; SY-01; NS-12 | Illustrative assumption |
| REQ-13 | Every logical entity and attribute shall have a dictionary entry with a non-circular definition and an owner or an explicit unknown | Must | STK-09 | DD-001; NS-01 | Illustrative assumption |
| REQ-14 | Customer status shall have one governed vocabulary with documented definitions | Should | INT-09 | BR-07; GL-28 | Illustrative assumption |

**Success criteria (proposed, pending stakeholder validation).** (1) A domain expert classifies ten sample instances
into the same entities as the modeler. (2) Every rule has a valid and an invalid scenario that the checker runs with
an explained outcome. (3) Every term has one meaning per context. (4) Every logical element has a dictionary entry.
(5) The independent reviewer closes all blocking and major findings.

### 6.3 D3 — Business glossary (Step 14)

One term, one meaning per context. The enterprise context defines the model's terms; the other contexts record
what local teams mean, so that translation at the boundary is explicit.

| ID | Glossary term | Definition | Context | Preferred term | Synonyms | Source | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GL-01 | Party | A real-world person or organisation that the bank knows about, whatever role it plays towards the bank. | ENTERPRISE | Party | none | INT-06 | Illustrative assumption |
| GL-02 | Person | A Party that is an individual human being. | ENTERPRISE | Person | none | INT-06 | Illustrative assumption |
| GL-03 | Organisation | A Party that is a company, partnership or other legal body. | ENTERPRISE | Organisation | legal entity | INT-06 | Illustrative assumption |
| GL-04 | Party Name | A legal name carried by a Party during a stated period, kept so that past names can be recovered. | ENTERPRISE | Party Name | none | INT-05 | Illustrative assumption |
| GL-05 | Party Source Identifier | The identifier by which one source system refers to a Party, mapped to the enterprise Party. | ENTERPRISE | Party Source Identifier | none | INT-10 | Illustrative assumption |
| GL-06 | Customer Role | A period during which a Party is treated by the bank as a customer, with the status in force. | ENTERPRISE | Customer Role | none | INT-01 | Illustrative assumption |
| GL-07 | Customer | A Party during a period in which it holds a customer role with the bank. Excludes parties that are only contacts or applicants. | ENTERPRISE | Customer | client | INT-01 | Illustrative assumption |
| GL-08 | Customer | A person or organisation held as a contact record for communication, whether or not it banks with the bank. | CRM | Contact | none | INT-01 | Illustrative assumption |
| GL-09 | Customer | A party that holds at least one deposit account with the bank under retail rules. | RETAIL_CORE | Account holder | none | INT-01 | Illustrative assumption |
| GL-10 | Customer | The person authorised to use a card, who is not always the owner of the card account. | CARDS | Cardholder | none | INT-02 | Illustrative assumption |
| GL-11 | Address | A postal location recorded once, independent of the parties that use it. | ENTERPRISE | Address | none | Unknown | Illustrative assumption |
| GL-12 | Party Address | The use of an address by a party for one purpose during one period. | ENTERPRISE | Party Address | none | Unknown | Illustrative assumption |
| GL-13 | Contact Point | A method for reaching a party, such as an email address or telephone number, with its verification state. | ENTERPRISE | Contact Point | none | Unknown | Illustrative assumption |
| GL-14 | Branch | A physical or administrative location of the bank through which accounts can be serviced. | ENTERPRISE | Branch | none | INT-14 | Illustrative assumption |
| GL-15 | Product | A deposit, loan or card offering that the bank defines and sells. | ENTERPRISE | Product | none | REQ-01 | Illustrative assumption |
| GL-16 | Product Bundle Component | The inclusion of one product inside a bundle product, with the quantity included. | ENTERPRISE | Product Bundle Component | none | INT-13 | Illustrative assumption |
| GL-17 | Account | A relationship through which the bank holds and tracks money for its holders, opened under one product, with its own lifecycle. | ENTERPRISE | Account | none | INT-04 | Illustrative assumption |
| GL-18 | Account | A deposit account administered by the retail core banking system. | RETAIL_CORE | Deposit account | none | INT-01 | Illustrative assumption |
| GL-19 | Account | A card account against which card spending is accumulated and billed. | CARDS | Card account | none | INT-02 | Illustrative assumption |
| GL-20 | Account Holding | The fact that one party holds one account in one holder role during one period. | ENTERPRISE | Account Holding | account owner | INT-04 | Illustrative assumption |
| GL-21 | Holder Role | The position a party has on an account, such as primary, joint or sole holder. | ENTERPRISE | Holder Role | none | INT-04 | Illustrative assumption |
| GL-22 | Guardianship | The authority of one party to act for a minor party during a period, with its evidence. | ENTERPRISE | Guardianship | none | INT-08 | Illustrative assumption |
| GL-23 | Minor | A person who is under 18 years old on the date being considered. | ENTERPRISE | Minor | none | INT-08 | Illustrative assumption |
| GL-24 | Transaction | A single monetary movement recorded against exactly one account. | ENTERPRISE | Transaction | none | INT-11 | Illustrative assumption |
| GL-25 | Posting | The act of recording a transaction against an account so that it affects the account position. | ENTERPRISE | Posting | none | INT-05 | Illustrative assumption |
| GL-26 | Valid Interval | The period from a start date, included, to an end date, excluded, during which a fact was true in the business. | ENTERPRISE | Valid Interval | none | ASM-01 | Illustrative assumption |
| GL-27 | Source System | An operational system, such as core banking, cards or CRM, that issues its own identifiers for parties. | ENTERPRISE | Source System | none | INT-10 | Illustrative assumption |
| GL-28 | Customer Status | The state of a customer role from a governed list. The meaning of active customer is not yet agreed. | ENTERPRISE | Customer Status | none | INT-09 | Illustrative assumption |

**Synonym register**

| ID | Synonym | Preferred term | Contexts | Equivalence evidence | Decision |
| --- | --- | --- | --- | --- | --- |
| SY-01 | client | Customer | ENTERPRISE | Used interchangeably by retail staff in interviews; no distinct rule found | Use Customer; retire client in the model |
| SY-02 | account owner | Account Holding | ENTERPRISE | Describes the holder side of the relationship, not the account | Use Account Holding; account owner is not a model term |
| SY-03 | legal entity | Organisation | ENTERPRISE | Same set of parties where the source uses the term | Use Organisation |

**Homonym register**

| ID | Homonym | Contexts | Disambiguating names | Decision |
| --- | --- | --- | --- | --- |
| HM-01 | Customer | ENTERPRISE; CRM; RETAIL_CORE; CARDS | Customer (enterprise); Contact (CRM); Account holder (retail); Cardholder (cards) | Keep the enterprise Customer for the role; translate local terms at the context boundary |
| HM-02 | Account | ENTERPRISE; RETAIL_CORE; CARDS | Account (enterprise); Deposit account (retail); Card account (cards) | The enterprise Account is wider than a card account; mappings are recorded per context |

### 6.4 D4 — Entity inventory (Step 5)

Candidates were taken from the roadmap and from the interview statements. `Accept` entities appear in the
conceptual model; `Relationship` candidates appear as conceptual relationships and become entities when resolved;
`Refinement` appears only in the logical model.

| ID | Candidate entity | Decision | Business definition | Business purpose | Source | Key relationships | Ownership | Open questions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CE-01 | Party | Accept | A real-world person or organisation that the bank knows about, whatever role it plays towards the bank. | Gives one identity to every individual or organisation | INT-06; INT-10 | Is known by Legal Name; acts as Customer Role; holds Account | Unknown (candidate STK-09) | OQ-08 | Illustrative assumption |
| CE-02 | Person | Accept | The specialisation of a Party that is an individual human being, with facts that only apply to individuals. | Holds individual-only facts such as date of birth | INT-06 | Specialises Party | Unknown (candidate STK-09) | OQ-07 | Illustrative assumption |
| CE-03 | Organisation | Accept | The specialisation of a Party that is a company or other legal body, with facts that only apply to organisations. | Holds organisation-only facts such as registration number | INT-06 | Specialises Party | Unknown (candidate STK-09) | none | Illustrative assumption |
| CE-04 | Legal Name | Accept | A name by which a Party is recognised in law, together with the period during which it was in force. | Lets the name that applied on a past date be recovered | INT-05 | Names a Party | Unknown (candidate STK-09) | none | Illustrative assumption |
| CE-05 | Customer Role | Accept | A period during which a Party is treated by the bank as a customer, with the status in force. | Separates being a customer from being a party | INT-01; INT-09 | Played by a Party | Unknown (candidate STK-02) | OQ-06 | Illustrative assumption |
| CE-06 | Account | Accept | A relationship through which the bank holds and tracks money for its holders, opened under one product, with its own lifecycle. | Carries balances and transactions for holders | INT-04; INT-07 | Held by Parties; opened under a Product; serviced by a Branch | Unknown (candidate STK-02) | OQ-02 | Illustrative assumption |
| CE-07 | Product | Accept | A deposit, loan or card offering that the bank defines and sells, under which accounts are opened. | Governs the terms under which accounts exist | REQ-01; INT-13 | Account is opened under it; may contain other Products | Unknown (candidate STK-02) | OQ-05; OQ-09 | Illustrative assumption |
| CE-08 | Branch | Accept | A physical or administrative location of the bank through which accounts can be serviced. | Identifies where an account is serviced | INT-14 | Services Accounts | Unknown (candidate STK-02) | OQ-10 | Illustrative assumption |
| CE-09 | Transaction | Accept | A single monetary movement recorded against exactly one account, with its direction and status. | Records what happened to an account | INT-11 | Posted to an Account | Unknown (candidate STK-02) | OQ-03 | Illustrative assumption |
| CE-10 | Address | Accept | A postal location recorded once, independent of the parties that use it. | Allows shared addresses and address history | Unknown | Used by Parties | Unknown (candidate STK-02) | OQ-04 | Illustrative assumption |
| CE-11 | Contact Point | Accept | A way of reaching a Party, such as an email address or telephone number, with its verification state. | Supports contact and verification | Unknown | Reaches a Party | Unknown (candidate STK-02) | none | Illustrative assumption |
| CE-12 | Customer | Reject | Rejected as a separate entity: customer is a role that a Party plays for a period, modelled as Customer Role, because a Party can leave and return. | Avoids duplicating the Party for each role | INT-01; INT-09 | Replaced by Customer Role | Not applicable | none | Illustrative assumption |
| CE-13 | Account Holding | Relationship | The conceptual relationship in which a Party holds an Account with a role and a period; resolved into an entity at the logical level. | Records who holds which account in which role | INT-04 | Party holds Account | Unknown (candidate STK-02) | none | Illustrative assumption |
| CE-14 | Guardianship | Relationship | The conceptual relationship in which one Party is guardian of another; resolved into an entity because it carries authority and evidence. | Records authority over a minor | INT-08 | Party is guardian of Party | Unknown (candidate STK-07) | OQ-01 | Illustrative assumption |
| CE-15 | Product Bundle | Relationship | The conceptual relationship in which a Product is composed of other Products. | Allows products sold together | INT-13 | Product is composed of Product | Unknown (candidate STK-02) | OQ-09 | Illustrative assumption |
| CE-16 | Party Address | Relationship | The conceptual relationship in which a Party is located at an Address for a purpose and a period. | Allows addresses to be shared and to change | Unknown | Party is located at Address | Unknown (candidate STK-02) | OQ-04 | Illustrative assumption |
| CE-17 | Party Source Identifier | Refinement | A logical-level mapping from a source system's identifier to a Party; not drawn conceptually. | Ties records from several systems to one Party | INT-10 | Maps to Party | Unknown (candidate STK-09) | OQ-08 | Illustrative assumption |
| CE-18 | Product Subscription | Open | Whether the enterprise model needs a concept for subscribing to products other than through opening an account is not yet decided. | Would cover cards and services that are not accounts | Roadmap process list | Unknown | Unknown | OQ-05 | Illustrative assumption |

**Authority and ownership of each concept** (unknown where not known)

| ID | Concept | Authoritative source | Accountable owner | Resolution action | Evidence |
| --- | --- | --- | --- | --- | --- |
| AU-01 | Party identity | Unknown (candidates: core banking, CRM) | Unknown (candidate STK-09) | Identity-resolution workshop; decide the authority and merge rules (OQ-08) | Illustrative assumption |
| AU-02 | Legal name | Unknown (candidate: core banking) | Unknown (candidate STK-09) | Confirm which source holds the legally relevant name | Illustrative assumption |
| AU-03 | Customer role and status | Unknown | Unknown (candidate STK-02) | Agree the meaning of active customer first (OQ-06) | Illustrative assumption |
| AU-04 | Account and account holding | Core banking system (assumed) | Unknown (candidate STK-02) | Confirm with the retail domain owner | Illustrative assumption |
| AU-05 | Product | Unknown | Unknown (candidate STK-02) | Locate the product catalogue | Illustrative assumption |
| AU-06 | Branch | Unknown | Unknown (candidate STK-02) | Locate the branch master | Illustrative assumption |
| AU-07 | Transaction | Core banking system (assumed) | Unknown (candidate STK-02) | Confirm posting authority | Illustrative assumption |
| AU-08 | Guardianship | Unknown | Unknown (candidate STK-07) | Decide whether guardianship is recorded at all (OQ-01) | Illustrative assumption |

### 6.5 D5 — Business rules and constraints register (Steps 3, 7 and 8)

Rules are written as sentences first. `Spec` is a precise, machine-checkable statement of the same rule; the
checker runs it. `Representation` says where the rule is enforced in the model: `Structure` (keys, requiredness,
references, allowed values), `Constraint` (a cross-attribute or cross-row condition) or `Procedure`.

**Spec language**

| Spec | Meaning | Example |
| --- | --- | --- |
| `key(all)` | Every entity's primary key is present and unique | BR-01 |
| `required(E.a, ...)` | The attributes are never null | `required(PartyName.legal_name)` |
| `unique(E: a, b)` | The combination is unique where all parts are present | `unique(Product: product_code)` |
| `fk(E.a -> F.b)` | A non-null value must exist in the target | `fk(Account.product_id -> Product.product_id)` |
| `domain(E.a)` | The value is one of the attribute's allowed values | `domain(Account.account_status_code)` |
| `check(E: expression)` | A row-level condition; unknown results pass, as in SQL | `check(Transaction: transaction_amount > 0)` |
| `no_overlap(E by k from f to t)` | Intervals `[f, t)` of the same key never overlap | BR-19 |
| `acyclic(E: parent -> child)` | The graph has no cycle, including a self-loop | BR-27 |
| `min_children(P.k <- C.fk >= n)` | Every parent has at least n children | BR-20 |
| `forbid(a=E; join b=F on ...; where ...)` | No joined row satisfies the condition | BR-26 |
| `require_exists(a=E; join ...; when ...; exists c=G where ...)` | When the condition holds, a matching row must exist | BR-23 |

| ID | Rule text | Source | Representation | Spec | Valid example | Invalid example | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BR-01 | Every instance of every entity is identified by its own unique identifier, which is always present. | REQ-01; INT-10 | Structure | key(all) | Party P101 appears once | Two Party rows share P101 | Confirmed | Illustrative assumption |
| BR-02 | A Party is exactly one type, PERSON or ORGANISATION, and records its creation date. | REQ-02; INT-06 | Structure | required(Party.party_type_code, Party.created_date) & domain(Party.party_type_code) | Party typed PERSON | Party with no type | Confirmed | Illustrative assumption |
| BR-03 | A Party has the specialisation record that matches its type, and never both. | REQ-02; ASM-02 | Constraint | fk(Person.party_id -> Party.party_id, Organisation.party_id -> Party.party_id) & require_exists(a=Party; when a.party_type_code = 'PERSON'; exists p=Person where p.party_id = a.party_id) & require_exists(a=Party; when a.party_type_code = 'ORGANISATION'; exists o=Organisation where o.party_id = a.party_id) & forbid(a=Person; join p=Party on p.party_id = a.party_id; where p.party_type_code <> 'PERSON') & forbid(a=Organisation; join p=Party on p.party_id = a.party_id; where p.party_type_code <> 'ORGANISATION') | Person row for a PERSON Party | Person row for an ORGANISATION Party | Assumed | Illustrative assumption |
| BR-04 | Every legal name belongs to a Party, states the name and the date it started, and no two names of a Party start on the same day. | REQ-05; INT-05 | Structure | required(PartyName.party_id, PartyName.legal_name, PartyName.valid_from) & fk(PartyName.party_id -> Party.party_id) & unique(PartyName: party_id, valid_from) | Name with a start date | Name with no text | Confirmed | Illustrative assumption |
| BR-05 | A legal name's end date is later than its start date, and the names of one Party never overlap in time. | REQ-05; ASM-01 | Constraint | check(PartyName: valid_to is null or valid_to > valid_from) & no_overlap(PartyName by party_id from valid_from to valid_to) | Name ends the day the next begins | Two names valid on the same day | Assumed | Illustrative assumption |
| BR-06 | Each source-system identifier maps to exactly one Party, and a Party can have identifiers from several systems. | REQ-08; INT-10 | Structure | required(PartySourceIdentifier.party_id, PartySourceIdentifier.source_system_code, PartySourceIdentifier.source_party_identifier) & fk(PartySourceIdentifier.party_id -> Party.party_id) & domain(PartySourceIdentifier.source_system_code) & unique(PartySourceIdentifier: source_system_code, source_party_identifier) | Same Party known to CORE_BANKING and CRM | One core identifier mapped to two Parties | Confirmed | Illustrative assumption |
| BR-07 | A customer role belongs to a Party and states a status from the governed list and the date it started. | REQ-14; INT-09 | Structure | required(CustomerRole.party_id, CustomerRole.customer_status_code, CustomerRole.valid_from) & fk(CustomerRole.party_id -> Party.party_id) & domain(CustomerRole.customer_status_code) | Status ACTIVE from a date | Status outside the list | Assumed | Illustrative assumption |
| BR-08 | A customer-role period ends after it starts, and a Party's customer-role periods never overlap. | REQ-14; ASM-01 | Constraint | check(CustomerRole: valid_to is null or valid_to > valid_from) & no_overlap(CustomerRole by party_id from valid_from to valid_to) | Role closed, later reopened | Two roles active at once | Assumed | Illustrative assumption |
| BR-09 | A party address names an existing Party and Address, a purpose and a start date; an address states its lines, locality and country. | REQ-01; ASM-01 | Structure | required(PartyAddress.party_id, PartyAddress.address_id, PartyAddress.address_type_code, PartyAddress.valid_from, Address.address_line_text, Address.locality_name, Address.country_code) & fk(PartyAddress.party_id -> Party.party_id, PartyAddress.address_id -> Address.address_id) & domain(PartyAddress.address_type_code, Address.country_code) | Mailing address for a Party | Address type outside the list | Assumed | Illustrative assumption |
| BR-10 | A Party has at most one address of each type at any time, and a use ends after it starts. | OQ-04 | Constraint | check(PartyAddress: valid_to is null or valid_to > valid_from) & no_overlap(PartyAddress by party_id, address_type_code from valid_from to valid_to) | Residential and mailing addresses together | Two residential addresses at once | Open | Illustrative assumption |
| BR-11 | A contact point belongs to a Party and states its kind, its value and whether it is verified. | REQ-01 | Structure | required(ContactPoint.party_id, ContactPoint.contact_type_code, ContactPoint.contact_value_text, ContactPoint.is_verified) & fk(ContactPoint.party_id -> Party.party_id) & domain(ContactPoint.contact_type_code) | Verified email | Contact kind outside the list | Assumed | Illustrative assumption |
| BR-12 | An account is opened under one existing product, has a unique number, a status from the governed list and a currency. | REQ-01; REQ-06 | Structure | required(Account.account_number, Account.product_id, Account.account_status_code, Account.currency_code) & fk(Account.product_id -> Product.product_id) & domain(Account.account_status_code, Account.currency_code) & unique(Account: account_number) | Open account under a product | Status DORMANT, which is not in the list | Assumed | Illustrative assumption |
| BR-13 | An account has zero or one servicing branch; when a branch is named it must exist. | REQ-10; INT-14 | Structure | fk(Account.branch_id -> Branch.branch_id) | Account with no branch while being opened | Account naming an unknown branch | Confirmed | Illustrative assumption |
| BR-14 | Closed accounts are retained; only a closed account has a closing date, and it is not before the opening date. | REQ-06; INT-07 | Constraint | check(Account: (account_status_code = 'CLOSED' and closed_date is not null) or (account_status_code <> 'CLOSED' and closed_date is null)) & check(Account: closed_date is null or opened_date is null or closed_date >= opened_date) | Closed account with a closing date | Closed account with no closing date | Confirmed | Illustrative assumption |
| BR-15 | An account that has left the pending status has an opening date. | REQ-06; ASM-01 | Constraint | check(Account: account_status_code = 'PENDING' or opened_date is not null) | Pending account with no opening date | Open account with no opening date | Assumed | Illustrative assumption |
| BR-16 | A branch has a name and a status from the governed list. | REQ-10 | Structure | required(Branch.branch_name, Branch.branch_status_code) & domain(Branch.branch_status_code) | Open branch with a name | Branch with an unknown status | Assumed | Illustrative assumption |
| BR-17 | An account holding names one existing Party, one existing account, a holder role and a start date, and the same combination does not start twice. | REQ-03; INT-04 | Structure | required(AccountHolding.party_id, AccountHolding.account_id, AccountHolding.holder_role_code, AccountHolding.valid_from) & fk(AccountHolding.party_id -> Party.party_id, AccountHolding.account_id -> Account.account_id) & domain(AccountHolding.holder_role_code) & unique(AccountHolding: account_id, party_id, holder_role_code, valid_from) | Two Parties hold one account | Holding with no role | Confirmed | Illustrative assumption |
| BR-18 | A holding's end date, when present, is later than its start date. | REQ-04; ASM-01 | Constraint | check(AccountHolding: valid_to is null or valid_to > valid_from) | Open-ended holding | End date before start date | Assumed | Illustrative assumption |
| BR-19 | The same Party cannot hold the same account in the same role over overlapping periods. | REQ-04; ASM-01 | Constraint | no_overlap(AccountHolding by party_id, account_id, holder_role_code from valid_from to valid_to) | Role ended on the day the next period starts | Historical period overlapping an open-ended one | Assumed | Illustrative assumption |
| BR-20 | Every account has at least one holding. | REQ-03; OQ-02 | Constraint | min_children(Account.account_id <- AccountHolding.account_id >= 1) | Account with a primary holder | Account with no holder | Assumed | Illustrative assumption |
| BR-21 | A guardianship names a guardian and a minor who exist, the kind of authority, a start date and its evidence. | REQ-09; INT-08 | Structure | required(Guardianship.guardian_party_id, Guardianship.minor_party_id, Guardianship.authority_type_code, Guardianship.valid_from, Guardianship.evidence_reference_text) & fk(Guardianship.guardian_party_id -> Party.party_id, Guardianship.minor_party_id -> Party.party_id) & domain(Guardianship.authority_type_code) | Guardianship with evidence | Guardianship with no evidence | Assumed | Illustrative assumption |
| BR-22 | A guardianship ends after it starts, and a Party is never its own guardian. | REQ-09 | Constraint | check(Guardianship: (valid_to is null or valid_to > valid_from) and guardian_party_id <> minor_party_id) | Guardian different from minor | Party guardian of itself | Assumed | Illustrative assumption |
| BR-23 | A holder who is under 18 on the date a holding starts needs a guardianship with transact authority in force on that date. | OQ-01; INT-08 | Constraint | require_exists(a=AccountHolding; join p=Person on p.party_id = a.party_id; when age_years(p.birth_date, a.valid_from) < 18; exists g=Guardianship where g.minor_party_id = a.party_id and g.authority_type_code = 'TRANSACT' and g.valid_from <= a.valid_from and (g.valid_to is null or g.valid_to > a.valid_from)) | Minor joint holder with an authorised guardian | Minor holder with no guardianship in force | Open | Illustrative assumption |
| BR-24 | A product has a unique code, a name, a category and a bundle capability flag. | REQ-01 | Structure | required(Product.product_code, Product.product_name, Product.product_category_code, Product.is_bundle_capable) & domain(Product.product_category_code) & unique(Product: product_code) | Product with a new code | Two products with one code | Assumed | Illustrative assumption |
| BR-25 | A bundle component names two existing products and a quantity greater than zero. | REQ-11; INT-13 | Structure | required(ProductBundleComponent.bundle_product_id, ProductBundleComponent.component_product_id, ProductBundleComponent.component_quantity) & fk(ProductBundleComponent.bundle_product_id -> Product.product_id, ProductBundleComponent.component_product_id -> Product.product_id) & check(ProductBundleComponent: component_quantity > 0) | Quantity of one | Quantity of zero | Assumed | Illustrative assumption |
| BR-26 | Only a bundle-capable product can contain components. | REQ-11; ASM-03 | Constraint | forbid(a=ProductBundleComponent; join b=Product on b.product_id = a.bundle_product_id; where b.is_bundle_capable = false) | Components inside a bundle-capable product | Components inside a stand-alone product | Assumed | Illustrative assumption |
| BR-27 | A product never contains itself, directly or through other products. | REQ-11; INT-13 | Constraint | check(ProductBundleComponent: bundle_product_id <> component_product_id) & acyclic(ProductBundleComponent: bundle_product_id -> component_product_id) | Bundle of two simple products | Bundle that contains itself | Confirmed | Illustrative assumption |
| BR-28 | Every transaction belongs to exactly one existing account. | REQ-07; INT-11 | Structure | required(Transaction.account_id) & fk(Transaction.account_id -> Account.account_id) | Transaction on an existing account | Transaction with no account | Confirmed | Illustrative assumption |
| BR-29 | A transaction states a positive amount, a currency, a direction and a status from the governed lists. | REQ-07; ASM-01 | Structure | required(Transaction.transaction_amount, Transaction.currency_code, Transaction.debit_credit_code, Transaction.transaction_status_code) & domain(Transaction.currency_code, Transaction.debit_credit_code, Transaction.transaction_status_code) & check(Transaction: transaction_amount > 0) | Debit of 250.00 | Amount of zero | Assumed | Illustrative assumption |
| BR-30 | A posted transaction has a posting timestamp. | REQ-07; ASM-01 | Constraint | check(Transaction: transaction_status_code <> 'POSTED' or posted_at_timestamp is not null) | Pending transaction with no timestamp | Posted transaction with no timestamp | Assumed | Illustrative assumption |
| BR-31 | A transaction is expressed in the currency of its account. | OQ-03 | Constraint | forbid(a=Transaction; join b=Account on b.account_id = a.account_id; where a.currency_code <> b.currency_code) | Transaction in the account currency | Transaction in another currency | Open | Illustrative assumption |
| BR-32 | A reversal refers to another transaction on the same account and never to itself. | REQ-07; ASM-01 | Constraint | fk(Transaction.reverses_transaction_id -> Transaction.transaction_id) & check(Transaction: reverses_transaction_id is null or reverses_transaction_id <> transaction_id) & forbid(a=Transaction; join b=Transaction on b.transaction_id = a.reverses_transaction_id; where a.account_id <> b.account_id) | Reversal on the same account | Reversal of a transaction on another account | Assumed | Illustrative assumption |

Three rules are `Open` (BR-10, BR-23 and BR-31) and BR-20 depends on a provisional answer (OQ-02): their scenarios pass
under a provisional assumption, not under a business decision (see FND-06).

### 6.6 D6 — Conceptual data model (Steps 9 and 10)

The conceptual model uses business words, shows many-to-many relationships directly, and contains no data types,
keys or platform terms. The checker scans it for physical terms.

**Scope boundary.** The model covers parties and their names, addresses and contact points; customer roles; accounts, products and branches; account holdings and guardianship; and transactions. It excludes loan servicing and collections, card authorisation detail, marketing and consent data, security implementation, ETL and reporting design.

**Concepts.** The accepted candidates in D4 (CE-01 to CE-11).

**Relationships**

| ID | Concept A | Relationship phrase (A to B) | Concept B | Reverse phrase (B to A) | Cardinality A to B | Cardinality B to A | Optionality | Business rule | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CR-01 | Party | may be specialised as | Person | is a kind of | 0..1 | 1 | A Person is always a Party | BR-03 | Illustrative assumption |
| CR-02 | Party | may be specialised as | Organisation | is a kind of | 0..1 | 1 | An Organisation is always a Party | BR-03 | Illustrative assumption |
| CR-03 | Party | is known by | Legal Name | names | 1..* | 1 | Every Party has at least one legal name | BR-04 | Illustrative assumption |
| CR-04 | Party | acts as | Customer Role | is played by | 0..* | 1 | A Party need not ever be a customer | BR-07 | Illustrative assumption |
| CR-05 | Party | holds | Account | is held by | 0..* | 1..* | A Party may hold no account; every account has a holder | BR-17 | Illustrative assumption |
| CR-06 | Party | is located at | Address | is used by | 0..* | 0..* | Both sides optional | BR-09 | Illustrative assumption |
| CR-07 | Party | is reachable at | Contact Point | reaches | 0..* | 1 | A Party may have no contact point | BR-11 | Illustrative assumption |
| CR-08 | Party | is guardian of | Party | has as guardian | 0..* | 0..* | Both sides optional | BR-21 | Illustrative assumption |
| CR-09 | Account | is opened under | Product | is the basis of | 1 | 0..* | Every account has one product | BR-12 | Illustrative assumption |
| CR-10 | Account | is serviced by | Branch | services | 0..1 | 0..* | An account may have no branch | BR-13 | Illustrative assumption |
| CR-11 | Transaction | is posted to | Account | receives | 1 | 0..* | Every transaction has one account | BR-28 | Illustrative assumption |
| CR-12 | Transaction | reverses | Transaction | is reversed by | 0..1 | 0..1 | Most transactions reverse nothing | BR-32 | Illustrative assumption |
| CR-13 | Product | is composed of | Product | is part of | 0..* | 0..* | Most products are not bundles | BR-27 | Illustrative assumption |

```text
D6-DIAGRAM  Northbridge conceptual model | v1.1 | 2026-10-21 | ILLUSTRATIVE
Legend:  [CE-nn Concept]   a line carries a verb phrase; min..max is shown at the far end of each direction
         Specialisation: a Person and an Organisation are each a kind of Party

 [CE-04 Legal Name] <-- is known by 1..* ------ [CE-01 Party] ------ acts as 0..* ----> [CE-05 Customer Role]
                                                  |  |   |   |
                              may be specialised  |  |   |   +-- is reachable at 0..* --> [CE-11 Contact Point]
                              +-------------------+  |   +------ is located at 0..*:0..* --> [CE-10 Address]
                              v                      |
 [CE-02 Person]   [CE-03 Organisation]               +-- is guardian of 0..*:0..* --> (Party)
                                                      |
                                      holds 0..*  :  is held by 1..*
                                                      v
 [CE-08 Branch] <-- is serviced by 0..1 ---- [CE-06 Account] ---- is opened under 1 ----> [CE-07 Product]
                                                      ^                                     |
                                       is posted to 1 |                  is composed of 0..*:0..* --> (Product)
                                          [CE-09 Transaction] -- reverses 0..1:0..1 --> (Transaction)
```

**Validation notes (Step 10).** The conceptual model was walked through five scenarios with the domain expert role:
(1) a joint account with two holders and different roles; (2) a person who changes legal name; (3) a minor who
holds jointly with a guardian; (4) a closed account whose transactions remain; (5) a bundle that must not contain
itself. All five are expressible without distortion. Two findings were logged as open questions rather than
resolved by assumption (OQ-01, OQ-09). Walk-throughs by real stakeholders have not taken place (VL-02).

### 6.7 D7 — Logical data model (Steps 6, 11)

The logical model adds identifiers, attributes, keys and resolved relationships. It uses logical domains only.
Each entity has a **grain statement**: one sentence saying what one row is.

| ID | Entity | Conceptual source | Supertype | Grain statement | Primary key | Refinement note |
| --- | --- | --- | --- | --- | --- | --- |
| LE-01 | Party | CE-01 | none | One row per real-world person or organisation known to the bank, whatever role it plays | party_id | Same as the conceptual Party |
| LE-02 | Person | CE-02 | Party | One row per Party of type PERSON | party_id | Specialisation of Party |
| LE-03 | Organisation | CE-03 | Party | One row per Party of type ORGANISATION | party_id | Specialisation of Party |
| LE-04 | PartyName | CE-04 | none | One row per legal name of a Party and the period during which it was in force | party_name_id | Conceptual Legal Name, refined with a valid interval |
| LE-05 | PartySourceIdentifier | CE-17 | none | One row per identifier that a source system uses for a Party | party_source_identifier_id | Added at the logical level to map source identities to one Party |
| LE-06 | CustomerRole | CE-05 | none | One row per period during which a Party acted as a customer, with the status in force | customer_role_id | Conceptual Customer Role, refined with status and period |
| LE-07 | Address | CE-10 | none | One row per distinct postal address, independent of who uses it | address_id | Same as the conceptual Address |
| LE-08 | PartyAddress | CE-16 | none | One row per use of an Address by a Party in one address type for one period | party_address_id | Resolves the conceptual many-to-many between Party and Address |
| LE-09 | ContactPoint | CE-11 | none | One row per contact method held for a Party | contact_point_id | Same as the conceptual Contact Point |
| LE-10 | Branch | CE-08 | none | One row per bank branch | branch_id | Same as the conceptual Branch |
| LE-11 | Product | CE-07 | none | One row per product the bank offers | product_id | Same as the conceptual Product |
| LE-12 | ProductBundleComponent | CE-15 | none | One row per component product inside a bundle product | product_bundle_component_id | Resolves the conceptual recursive many-to-many between Product and Product |
| LE-13 | Account | CE-06 | none | One row per account relationship opened under a product | account_id | Same as the conceptual Account |
| LE-14 | AccountHolding | CE-13 | none | One row per Party, account, holder role and start date | account_holding_id | Resolves the conceptual many-to-many between Party and Account |
| LE-15 | Guardianship | CE-14 | none | One row per guardian, minor and period of authority | guardianship_id | Resolves the conceptual recursive many-to-many between Party and Party |
| LE-16 | Transaction | CE-09 | none | One row per monetary movement recorded against exactly one account | transaction_id | Same as the conceptual Transaction |

```text
D7-DIAGRAM  Northbridge logical model | v1.1 | 2026-10-21 | ILLUSTRATIVE
Legend:  [LE-nn Entity]  1 = exactly one, 0..1 = optional, 0..* = zero or many; arrows point from parent to child

 [LE-01 Party] --1:0..1--> [LE-02 Person]            [LE-01 Party] --1:0..1--> [LE-03 Organisation]
 [LE-01 Party] --1:1..*--> [LE-04 PartyName]         [LE-01 Party] --1:0..*--> [LE-05 PartySourceIdentifier]
 [LE-01 Party] --1:0..*--> [LE-06 CustomerRole]      [LE-01 Party] --1:0..*--> [LE-09 ContactPoint]
 [LE-01 Party] --1:0..*--> [LE-08 PartyAddress] <--0..*:1-- [LE-07 Address]
 [LE-01 Party] --1:0..*--> [LE-14 AccountHolding] <--1..*:1-- [LE-13 Account]
 [LE-01 Party] --1:0..* (guardian)--> [LE-15 Guardianship] <--1:0..* (minor)-- [LE-01 Party]
 [LE-11 Product] --1:0..*--> [LE-13 Account] <--0..*:0..1-- [LE-10 Branch]
 [LE-11 Product] --1:0..* (bundle)--> [LE-12 ProductBundleComponent] <--0..*:1 (component)-- [LE-11 Product]
 [LE-13 Account] --1:0..*--> [LE-16 Transaction] --0..1:0..1 (reverses)--> [LE-16 Transaction]
```

**Attribute inventory.** Every attribute states its role, logical domain, requiredness, allowed values, the key
it references and the rules that constrain it.

| ID | Entity | Attribute | Role | Logical domain | Required | Allowed values | References | Related rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AT-001 | Party | party_id | Identifier | Identifier | Y | none | none | BR-03, BR-04, BR-06, BR-07, BR-09, BR-11, BR-17, BR-21 |
| AT-002 | Party | party_type_code | Descriptive | Code | Y | PERSON, ORGANISATION | none | BR-02, BR-03 |
| AT-003 | Party | created_date | Descriptive | Date | Y | none | none | BR-02 |
| AT-004 | Person | party_id | Identifier | Identifier | Y | none | Party.party_id | BR-03, BR-23 |
| AT-005 | Person | birth_date | Descriptive | Date | N | none | none | BR-23 |
| AT-006 | Organisation | party_id | Identifier | Identifier | Y | none | Party.party_id | BR-03 |
| AT-007 | Organisation | registration_number | Descriptive | Text | N | none | none | none |
| AT-008 | PartyName | party_name_id | Identifier | Identifier | Y | none | none | none |
| AT-009 | PartyName | party_id | Reference | Identifier | Y | none | Party.party_id | BR-04, BR-05 |
| AT-010 | PartyName | legal_name | Descriptive | Text | Y | none | none | BR-04 |
| AT-011 | PartyName | valid_from | Descriptive | Date | Y | none | none | BR-04, BR-05 |
| AT-012 | PartyName | valid_to | Descriptive | Date | N | none | none | BR-05 |
| AT-013 | PartySourceIdentifier | party_source_identifier_id | Identifier | Identifier | Y | none | none | none |
| AT-014 | PartySourceIdentifier | party_id | Reference | Identifier | Y | none | Party.party_id | BR-06 |
| AT-015 | PartySourceIdentifier | source_system_code | Descriptive | Code | Y | CORE_BANKING, CARDS, CRM | none | BR-06 |
| AT-016 | PartySourceIdentifier | source_party_identifier | Descriptive | Text | Y | none | none | BR-06 |
| AT-017 | CustomerRole | customer_role_id | Identifier | Identifier | Y | none | none | none |
| AT-018 | CustomerRole | party_id | Reference | Identifier | Y | none | Party.party_id | BR-07, BR-08 |
| AT-019 | CustomerRole | customer_status_code | Descriptive | Code | Y | ACTIVE, INACTIVE, CLOSED | none | BR-07 |
| AT-020 | CustomerRole | valid_from | Descriptive | Date | Y | none | none | BR-07, BR-08 |
| AT-021 | CustomerRole | valid_to | Descriptive | Date | N | none | none | BR-08 |
| AT-022 | Address | address_id | Identifier | Identifier | Y | none | none | BR-09 |
| AT-023 | Address | address_line_text | Descriptive | Text | Y | none | none | BR-09 |
| AT-024 | Address | locality_name | Descriptive | Text | Y | none | none | BR-09 |
| AT-025 | Address | postal_code | Descriptive | Code | N | none | none | none |
| AT-026 | Address | country_code | Descriptive | Code | Y | IN, GB, US | none | BR-09 |
| AT-027 | PartyAddress | party_address_id | Identifier | Identifier | Y | none | none | none |
| AT-028 | PartyAddress | party_id | Reference | Identifier | Y | none | Party.party_id | BR-09, BR-10 |
| AT-029 | PartyAddress | address_id | Reference | Identifier | Y | none | Address.address_id | BR-09 |
| AT-030 | PartyAddress | address_type_code | Descriptive | Code | Y | RESIDENTIAL, MAILING, REGISTERED | none | BR-09, BR-10 |
| AT-031 | PartyAddress | valid_from | Descriptive | Date | Y | none | none | BR-09, BR-10 |
| AT-032 | PartyAddress | valid_to | Descriptive | Date | N | none | none | BR-10 |
| AT-033 | ContactPoint | contact_point_id | Identifier | Identifier | Y | none | none | none |
| AT-034 | ContactPoint | party_id | Reference | Identifier | Y | none | Party.party_id | BR-11 |
| AT-035 | ContactPoint | contact_type_code | Descriptive | Code | Y | EMAIL, PHONE | none | BR-11 |
| AT-036 | ContactPoint | contact_value_text | Descriptive | Text | Y | none | none | BR-11 |
| AT-037 | ContactPoint | is_verified | Descriptive | Flag | Y | none | none | BR-11 |
| AT-038 | Branch | branch_id | Identifier | Identifier | Y | none | none | BR-13 |
| AT-039 | Branch | branch_name | Descriptive | Text | Y | none | none | BR-16 |
| AT-040 | Branch | branch_status_code | Descriptive | Code | Y | OPEN, CLOSED | none | BR-16 |
| AT-041 | Product | product_id | Identifier | Identifier | Y | none | none | BR-12, BR-25, BR-26 |
| AT-042 | Product | product_code | Descriptive | Code | Y | none | none | BR-24 |
| AT-043 | Product | product_name | Descriptive | Text | Y | none | none | BR-24 |
| AT-044 | Product | product_category_code | Descriptive | Code | Y | DEPOSIT, LOAN, CARD | none | BR-24 |
| AT-045 | Product | is_bundle_capable | Descriptive | Flag | Y | none | none | BR-24, BR-26 |
| AT-046 | ProductBundleComponent | product_bundle_component_id | Identifier | Identifier | Y | none | none | none |
| AT-047 | ProductBundleComponent | bundle_product_id | Reference | Identifier | Y | none | Product.product_id | BR-25, BR-26, BR-27 |
| AT-048 | ProductBundleComponent | component_product_id | Reference | Identifier | Y | none | Product.product_id | BR-25, BR-27 |
| AT-049 | ProductBundleComponent | component_quantity | Descriptive | Quantity | Y | none | none | BR-25 |
| AT-050 | Account | account_id | Identifier | Identifier | Y | none | none | BR-17, BR-20, BR-28, BR-31 |
| AT-051 | Account | account_number | Descriptive | Text | Y | none | none | BR-12 |
| AT-052 | Account | product_id | Reference | Identifier | Y | none | Product.product_id | BR-12 |
| AT-053 | Account | branch_id | Reference | Identifier | N | none | Branch.branch_id | BR-13 |
| AT-054 | Account | account_status_code | Descriptive | Code | Y | PENDING, OPEN, SUSPENDED, CLOSED | none | BR-12, BR-14, BR-15 |
| AT-055 | Account | currency_code | Descriptive | Code | Y | INR, GBP, USD | none | BR-12, BR-31 |
| AT-056 | Account | opened_date | Descriptive | Date | N | none | none | BR-14, BR-15 |
| AT-057 | Account | closed_date | Descriptive | Date | N | none | none | BR-14 |
| AT-058 | AccountHolding | account_holding_id | Identifier | Identifier | Y | none | none | none |
| AT-059 | AccountHolding | party_id | Reference | Identifier | Y | none | Party.party_id | BR-17, BR-19, BR-23 |
| AT-060 | AccountHolding | account_id | Reference | Identifier | Y | none | Account.account_id | BR-17, BR-19, BR-20 |
| AT-061 | AccountHolding | holder_role_code | Descriptive | Code | Y | PRIMARY_HOLDER, JOINT_HOLDER, SOLE_HOLDER | none | BR-17, BR-19 |
| AT-062 | AccountHolding | valid_from | Descriptive | Date | Y | none | none | BR-17, BR-18, BR-19, BR-23 |
| AT-063 | AccountHolding | valid_to | Descriptive | Date | N | none | none | BR-18, BR-19, BR-23 |
| AT-064 | Guardianship | guardianship_id | Identifier | Identifier | Y | none | none | none |
| AT-065 | Guardianship | guardian_party_id | Reference | Identifier | Y | none | Party.party_id | BR-21, BR-22 |
| AT-066 | Guardianship | minor_party_id | Reference | Identifier | Y | none | Party.party_id | BR-21, BR-22, BR-23 |
| AT-067 | Guardianship | authority_type_code | Descriptive | Code | Y | TRANSACT, CONSENT_ONLY | none | BR-21, BR-23 |
| AT-068 | Guardianship | valid_from | Descriptive | Date | Y | none | none | BR-21, BR-22, BR-23 |
| AT-069 | Guardianship | valid_to | Descriptive | Date | N | none | none | BR-22, BR-23 |
| AT-070 | Guardianship | evidence_reference_text | Descriptive | Text | Y | none | none | BR-21 |
| AT-071 | Transaction | transaction_id | Identifier | Identifier | Y | none | none | BR-32 |
| AT-072 | Transaction | account_id | Reference | Identifier | Y | none | Account.account_id | BR-28, BR-31, BR-32 |
| AT-073 | Transaction | transaction_amount | Descriptive | Amount | Y | none | none | BR-29 |
| AT-074 | Transaction | currency_code | Descriptive | Code | Y | INR, GBP, USD | none | BR-29, BR-31 |
| AT-075 | Transaction | debit_credit_code | Descriptive | Code | Y | DEBIT, CREDIT | none | BR-29 |
| AT-076 | Transaction | transaction_status_code | Descriptive | Code | Y | PENDING, POSTED, REVERSED | none | BR-29, BR-30 |
| AT-077 | Transaction | posted_at_timestamp | Descriptive | Timestamp | N | none | none | BR-30 |
| AT-078 | Transaction | reverses_transaction_id | Reference | Identifier | N | none | Transaction.transaction_id | BR-32 |

**Mapping from the conceptual to the logical model.** Every conceptual element appears in the logical model and
every logical element traces back or is a documented refinement.

| ID | Conceptual element | Logical element(s) | Refinement | Reason |
| --- | --- | --- | --- | --- |
| CLM-01 | CE-01 | LE-01 | Same | Party is carried over unchanged |
| CLM-02 | CE-02 | LE-02 | Same | Person is carried over as a specialisation table |
| CLM-03 | CE-03 | LE-03 | Same | Organisation is carried over as a specialisation table |
| CLM-04 | CE-04 | LE-04 | Same | Legal Name becomes PartyName with a valid interval |
| CLM-05 | CE-05 | LE-06 | Same | Customer Role becomes CustomerRole with status and period |
| CLM-06 | CE-06 | LE-13 | Same | Account is carried over |
| CLM-07 | CE-07 | LE-11 | Same | Product is carried over |
| CLM-08 | CE-08 | LE-10 | Same | Branch is carried over |
| CLM-09 | CE-09 | LE-16 | Same | Transaction is carried over |
| CLM-10 | CE-10 | LE-07 | Same | Address is carried over |
| CLM-11 | CE-11 | LE-09 | Same | Contact Point becomes ContactPoint |
| CLM-12 | CE-17 | LE-05; RL-04 | Added | Logical refinement: a mapping from source identifiers to the Party |
| CLM-13 | CR-01 | RL-01 | Same | Specialisation becomes a shared-key reference |
| CLM-14 | CR-02 | RL-02 | Same | Specialisation becomes a shared-key reference |
| CLM-15 | CR-03 | RL-03 | Same | One-to-many reference from PartyName to Party |
| CLM-16 | CR-04 | RL-05 | Same | One-to-many reference from CustomerRole to Party |
| CLM-17 | CR-05 | LE-14; RL-11; RL-12 | Resolved | Many-to-many resolved by the AccountHolding associative entity |
| CLM-18 | CR-06 | LE-08; RL-06; RL-07 | Resolved | Many-to-many resolved by the PartyAddress associative entity |
| CLM-19 | CR-07 | RL-08 | Same | One-to-many reference from ContactPoint to Party |
| CLM-20 | CR-08 | LE-15; RL-13; RL-14 | Resolved | Recursive many-to-many resolved by the Guardianship associative entity |
| CLM-21 | CR-09 | RL-09 | Same | Mandatory reference from Account to Product |
| CLM-22 | CR-10 | RL-10 | Same | Optional reference from Account to Branch |
| CLM-23 | CR-11 | RL-17 | Same | Mandatory reference from Transaction to Account |
| CLM-24 | CR-12 | RL-18 | Same | Optional self-reference on Transaction |
| CLM-25 | CR-13 | LE-12; RL-15; RL-16 | Resolved | Recursive many-to-many resolved by the ProductBundleComponent associative entity |

### 6.8 D8 — Relationship and cardinality definitions (Step 7)

Each relationship is stated in words in both directions. "Parents per child" is the number of parents a child row
has through this foreign key; "Children per parent" is the number of child rows a parent can have. A required foreign
key means the parent side is exactly one; an optional one means zero or one.

| ID | Parent entity | Child entity | Verb phrase (parent to child) | Reverse phrase (child to parent) | Parents per child | Children per parent | Foreign key | Business rule | Validation scenario |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-01 | Party | Person | is specialised as | is a kind of | 1 | 0..1 | party_id | BR-03 | SCN-15 |
| RL-02 | Party | Organisation | is specialised as | is a kind of | 1 | 0..1 | party_id | BR-03 | SCN-15 |
| RL-03 | Party | PartyName | is known by | names | 1 | 1..* | party_id | BR-04 | SCN-37 |
| RL-04 | Party | PartySourceIdentifier | is identified in source systems by | identifies | 1 | 0..* | party_id | BR-06 | SCN-34 |
| RL-05 | Party | CustomerRole | acts as a customer through | is played by | 1 | 0..* | party_id | BR-07 | SCN-37 |
| RL-06 | Party | PartyAddress | uses addresses through | is used by | 1 | 0..* | party_id | BR-09 | SCN-40 |
| RL-07 | Address | PartyAddress | is used through | refers to | 1 | 0..* | address_id | BR-09 | SCN-40 |
| RL-08 | Party | ContactPoint | can be reached through | reaches | 1 | 0..* | party_id | BR-11 | SCN-42 |
| RL-09 | Product | Account | is the basis of | is opened under | 1 | 0..* | product_id | BR-12 | SCN-12 |
| RL-10 | Branch | Account | services | is serviced by | 0..1 | 0..* | branch_id | BR-13 | SCN-32 |
| RL-11 | Party | AccountHolding | participates in | is held by | 1 | 0..* | party_id | BR-17 | SCN-15 |
| RL-12 | Account | AccountHolding | is held through | holds | 1 | 1..* | account_id | BR-17; BR-20 | SCN-35 |
| RL-13 | Party | Guardianship | is guardian in | has as guardian | 1 | 0..* | guardian_party_id | BR-21 | SCN-46 |
| RL-14 | Party | Guardianship | is the minor in | has as minor | 1 | 0..* | minor_party_id | BR-21 | SCN-46 |
| RL-15 | Product | ProductBundleComponent | is the bundle in | belongs to bundle | 1 | 0..* | bundle_product_id | BR-25 | SCN-29 |
| RL-16 | Product | ProductBundleComponent | is the component in | includes component | 1 | 0..* | component_product_id | BR-25 | SCN-29 |
| RL-17 | Account | Transaction | receives | is posted to | 1 | 0..* | account_id | BR-28 | SCN-21 |
| RL-18 | Transaction | Transaction | is reversed by | reverses | 0..1 | 0..1 | reverses_transaction_id | BR-32 | SCN-34 |

**Reading examples.** `Account` to `AccountHolding`: *an Account is held through one or more AccountHoldings*; *each
AccountHolding holds exactly one Account*. `Branch` to `Account`: *a Branch services zero or many Accounts*; *an
Account is serviced by zero or one Branch*. The two Guardianship rows give the same table two distinct roles of Party
(guardian and minor), which is why the foreign keys are named for the role.

### 6.9 D9 — Key and integrity constraint definitions (Step 12)

**Keys.** Every entity has a primary key. Alternate keys carry uniqueness rules. Foreign keys carry referential rules
and are enforced by the business rules in 6.5. Deletion policy: nothing in this model is physically deleted when
a business fact ends; closing an account or ending a holding sets an end date or a status (BR-14, BR-18). The
mechanism that generates identifiers is deferred (DF-03).

| ID | Entity | Key kind | Attributes | References | Rule |
| --- | --- | --- | --- | --- | --- |
| KY-01 | Party | Primary | party_id | none | BR-01 |
| KY-02 | Person | Primary | party_id | none | BR-01 |
| KY-03 | Person | Foreign | party_id | Party.party_id | BR-03 |
| KY-04 | Organisation | Primary | party_id | none | BR-01 |
| KY-05 | Organisation | Foreign | party_id | Party.party_id | BR-03 |
| KY-06 | PartyName | Primary | party_name_id | none | BR-01 |
| KY-07 | PartyName | Alternate | party_id, valid_from | none | BR-04 |
| KY-08 | PartyName | Foreign | party_id | Party.party_id | BR-04 |
| KY-09 | PartySourceIdentifier | Primary | party_source_identifier_id | none | BR-01 |
| KY-10 | PartySourceIdentifier | Alternate | source_system_code, source_party_identifier | none | BR-06 |
| KY-11 | PartySourceIdentifier | Foreign | party_id | Party.party_id | BR-06 |
| KY-12 | CustomerRole | Primary | customer_role_id | none | BR-01 |
| KY-13 | CustomerRole | Foreign | party_id | Party.party_id | BR-07 |
| KY-14 | Address | Primary | address_id | none | BR-01 |
| KY-15 | PartyAddress | Primary | party_address_id | none | BR-01 |
| KY-16 | PartyAddress | Foreign | party_id | Party.party_id | BR-09 |
| KY-17 | PartyAddress | Foreign | address_id | Address.address_id | BR-09 |
| KY-18 | ContactPoint | Primary | contact_point_id | none | BR-01 |
| KY-19 | ContactPoint | Foreign | party_id | Party.party_id | BR-11 |
| KY-20 | Branch | Primary | branch_id | none | BR-01 |
| KY-21 | Product | Primary | product_id | none | BR-01 |
| KY-22 | Product | Alternate | product_code | none | BR-24 |
| KY-23 | ProductBundleComponent | Primary | product_bundle_component_id | none | BR-01 |
| KY-24 | ProductBundleComponent | Foreign | bundle_product_id | Product.product_id | BR-25 |
| KY-25 | ProductBundleComponent | Foreign | component_product_id | Product.product_id | BR-25 |
| KY-26 | Account | Primary | account_id | none | BR-01 |
| KY-27 | Account | Alternate | account_number | none | BR-12 |
| KY-28 | Account | Foreign | product_id | Product.product_id | BR-12 |
| KY-29 | Account | Foreign | branch_id | Branch.branch_id | BR-13 |
| KY-30 | AccountHolding | Primary | account_holding_id | none | BR-01 |
| KY-31 | AccountHolding | Alternate | account_id, party_id, holder_role_code, valid_from | none | BR-17 |
| KY-32 | AccountHolding | Foreign | party_id | Party.party_id | BR-17 |
| KY-33 | AccountHolding | Foreign | account_id | Account.account_id | BR-17 |
| KY-34 | Guardianship | Primary | guardianship_id | none | BR-01 |
| KY-35 | Guardianship | Foreign | guardian_party_id | Party.party_id | BR-21 |
| KY-36 | Guardianship | Foreign | minor_party_id | Party.party_id | BR-21 |
| KY-37 | Transaction | Primary | transaction_id | none | BR-01 |
| KY-38 | Transaction | Foreign | account_id | Account.account_id | BR-28 |
| KY-39 | Transaction | Foreign | reverses_transaction_id | Transaction.transaction_id | BR-32 |

**Functional dependencies.** For each entity the primary key and each alternate key determine every other attribute. The two
legacy relations at the end are extract layouts used to demonstrate decomposition; their dependencies are assumptions
to be confirmed.

| ID | Relation | Determinant | Dependent | Source |
| --- | --- | --- | --- | --- |
| FD-01 | Party | party_id | party_type_code, created_date | Primary key |
| FD-02 | Person | party_id | birth_date | Primary key |
| FD-03 | Organisation | party_id | registration_number | Primary key |
| FD-04 | PartyName | party_name_id | party_id, legal_name, valid_from, valid_to | Primary key |
| FD-05 | PartyName | party_id, valid_from | party_name_id, legal_name, valid_to | Alternate key (BR-04) |
| FD-06 | PartySourceIdentifier | party_source_identifier_id | party_id, source_system_code, source_party_identifier | Primary key |
| FD-07 | PartySourceIdentifier | source_system_code, source_party_identifier | party_source_identifier_id, party_id | Alternate key (BR-06) |
| FD-08 | CustomerRole | customer_role_id | party_id, customer_status_code, valid_from, valid_to | Primary key |
| FD-09 | Address | address_id | address_line_text, locality_name, postal_code, country_code | Primary key |
| FD-10 | PartyAddress | party_address_id | party_id, address_id, address_type_code, valid_from, valid_to | Primary key |
| FD-11 | ContactPoint | contact_point_id | party_id, contact_type_code, contact_value_text, is_verified | Primary key |
| FD-12 | Branch | branch_id | branch_name, branch_status_code | Primary key |
| FD-13 | Product | product_id | product_code, product_name, product_category_code, is_bundle_capable | Primary key |
| FD-14 | Product | product_code | product_id, product_name, product_category_code, is_bundle_capable | Alternate key (BR-24) |
| FD-15 | ProductBundleComponent | product_bundle_component_id | bundle_product_id, component_product_id, component_quantity | Primary key |
| FD-16 | Account | account_id | account_number, product_id, branch_id, account_status_code, currency_code, opened_date, closed_date | Primary key |
| FD-17 | Account | account_number | account_id, product_id, branch_id, account_status_code, currency_code, opened_date, closed_date | Alternate key (BR-12) |
| FD-18 | AccountHolding | account_holding_id | party_id, account_id, holder_role_code, valid_from, valid_to | Primary key |
| FD-19 | AccountHolding | account_id, party_id, holder_role_code, valid_from | account_holding_id, valid_to | Alternate key (BR-17) |
| FD-20 | Guardianship | guardianship_id | guardian_party_id, minor_party_id, authority_type_code, valid_from, valid_to, evidence_reference_text | Primary key |
| FD-21 | Transaction | transaction_id | account_id, transaction_amount, currency_code, debit_credit_code, transaction_status_code, posted_at_timestamp, reverses_transaction_id | Primary key |
| FD-22 | LegacyPaymentRow | transaction_id | account_id, posted_at_timestamp, transaction_amount, currency_code | Assumed: a transaction belongs to one account (BR-28) |
| FD-23 | LegacyPaymentRow | account_id | account_number, product_code, branch_id | Assumed: account facts depend on the account |
| FD-24 | LegacyPaymentRow | product_code | product_name | Assumed: a product code names one product (BR-24) |
| FD-25 | LegacyPaymentRow | branch_id | branch_name | Assumed: a branch identifier names one branch |
| FD-26 | LegacyHoldingRow | account_id, party_id, holder_role_code, valid_from | valid_to, party_legal_name | Assumed: a holding start fixes its end (BR-17) |
| FD-27 | LegacyHoldingRow | party_id | party_legal_name | Assumed for the extract date only: the current legal name (see MD-03) |

**Relations used in decomposition proofs**

| ID | Relation | Relation attributes | Role | Note |
| --- | --- | --- | --- | --- |
| LR-01 | LegacyPaymentRow | transaction_id, account_id, account_number, product_code, product_name, branch_id, branch_name, posted_at_timestamp, transaction_amount, currency_code | Root | One row per transaction in a legacy extract that repeats account, product and branch facts |
| LR-02 | LegacyTransaction | transaction_id, account_id, posted_at_timestamp, transaction_amount, currency_code | Leaf | Becomes the Transaction entity |
| LR-03 | LegacyAccountDetail | account_id, account_number, product_code, product_name, branch_id, branch_name | Intermediate | Account facts with product and branch facts |
| LR-04 | LegacyAccount | account_id, account_number, product_code, branch_id, branch_name | Intermediate | Account facts with branch facts |
| LR-05 | LegacyProduct | product_code, product_name | Leaf | Becomes the Product entity |
| LR-06 | LegacyAccountCore | account_id, account_number, product_code, branch_id | Leaf | Becomes the Account entity |
| LR-07 | LegacyBranch | branch_id, branch_name | Leaf | Becomes the Branch entity |
| LR-08 | LegacyHoldingRow | account_id, party_id, party_legal_name, holder_role_code, valid_from, valid_to | Root | One row per holding in a legacy extract that repeats the holder's current name |
| LR-09 | LegacyHolding | account_id, party_id, holder_role_code, valid_from, valid_to | Leaf | Becomes the AccountHolding entity |
| LR-10 | LegacyPartyName | party_id, party_legal_name | Leaf | Becomes PartyName, with a valid interval added because the name changes |

**Decomposition steps.** For each step the checker confirms that the children cover the parent, that the stated common
attributes are the intersection, that the intersection determines one child under the dependencies (a lossless join),
that every leaf is in BCNF, and that every dependency of the root is preserved in some leaf.

| ID | Parent relation | Child 1 | Child 2 | Common attributes | Justification |
| --- | --- | --- | --- | --- | --- |
| DP-01 | LegacyPaymentRow | LegacyTransaction | LegacyAccountDetail | account_id | account_id determines every attribute of LegacyAccountDetail, directly or through product_code and branch_id |
| DP-02 | LegacyAccountDetail | LegacyAccount | LegacyProduct | product_code | product_code determines product_name |
| DP-03 | LegacyAccount | LegacyAccountCore | LegacyBranch | branch_id | branch_id determines branch_name |
| DP-04 | LegacyHoldingRow | LegacyHolding | LegacyPartyName | party_id | party_id determines party_legal_name |

**Candidate keys and normal forms** (computed by the checker from the dependencies above)

| ID | Relation | Candidate keys | Normal form | Note |
| --- | --- | --- | --- | --- |
| NF-01 | LegacyPaymentRow | (transaction_id) | below 3NF | Derived by the checker from the stated dependencies |
| NF-02 | LegacyTransaction | (transaction_id) | BCNF | Derived by the checker from the stated dependencies |
| NF-03 | LegacyProduct | (product_code) | BCNF | Derived by the checker from the stated dependencies |
| NF-04 | LegacyAccountCore | (account_id) | BCNF | Derived by the checker from the stated dependencies |
| NF-05 | LegacyBranch | (branch_id) | BCNF | Derived by the checker from the stated dependencies |
| NF-06 | LegacyHoldingRow | (account_id, holder_role_code, party_id, valid_from) | below 3NF | Derived by the checker from the stated dependencies |
| NF-07 | LegacyHolding | (account_id, holder_role_code, party_id, valid_from) | BCNF | Derived by the checker from the stated dependencies |
| NF-08 | LegacyPartyName | (party_id) | BCNF | Derived by the checker from the stated dependencies |
| NF-09 | Party | (party_id) | BCNF | Derived by the checker from the stated dependencies |
| NF-10 | PartyName | (party_id, valid_from); (party_name_id) | BCNF | Derived by the checker from the stated dependencies |
| NF-11 | Account | (account_id); (account_number) | BCNF | Derived by the checker from the stated dependencies |
| NF-12 | AccountHolding | (account_holding_id); (account_id, holder_role_code, party_id, valid_from) | BCNF | Derived by the checker from the stated dependencies |
| NF-13 | Transaction | (transaction_id) | BCNF | Derived by the checker from the stated dependencies |

**Reading the results.** The legacy payment extract has key `transaction_id` but is below third normal form: account,
product and branch facts depend on non-key attributes, producing update anomalies. Three lossless steps give four
BCNF relations that become `Transaction`, `Account`, `Product` and `Branch`. The legacy holding extract repeats the
holder's current legal name on every holding; the dependency from `party_id` to the name is a partial dependency of the
key and the name is not prime. Splitting it gives `AccountHolding` and a name relation, and the logical model then
adds a valid interval to the name because, over time, the dependency `party_id` to name is false (MD-03).
All sixteen entities are in BCNF under their stated dependencies. **No denormalisation is recorded**; any
physical denormalisation is deferred (DF-08).

**Why the combined extract is not decomposed by dependencies alone.** The raw extract that joins holders to payments
has one row per transaction per holder. Splitting holders from transactions needs a multi-valued dependency, which is
outside the Topic 3 scope of functional dependencies and BCNF. The model reaches the same structure by recognising
`AccountHolding` as an associative entity from the business rule (INT-04), not from a dependency proof.

### 6.10 D10 — Modeling decisions and unresolved questions (Steps 8 and 13)

**Modeling decisions** (each has alternatives, rationale, consequences and a revisit trigger; none is approved)

| ID | Decision statement | Alternatives considered | Rationale | Consequences | Revisit trigger | Status |
| --- | --- | --- | --- | --- | --- | --- |
| MD-01 | Model customer as a role of a Party with its own period, not as a subtype or a separate entity | Customer as a subtype of Party; Customer as an independent entity with its own identifier; no customer concept at all | A Party can leave and later return as a customer, can be a guardian or a contact without being a customer, and must not be duplicated per role (Topic 2, section 5.5). | Customer counts come from CustomerRole periods; the meaning of active customer must be agreed separately (OQ-06). | A decision that a Party can be a customer only once for life | Proposed |
| MD-02 | Resolve Party-to-Account many-to-many with AccountHolding carrying role and valid interval | A customer identifier on Account; three holder columns on Account; a holder list in one text field | Joint holding is stated by the business (INT-04); the relationship has its own role and dates, and a single foreign key would lose joint holders. | Account has no holder column; every holder query goes through AccountHolding; overlap and minimum-holder rules are needed (BR-19, BR-20). | Evidence that accounts never have more than one holder | Proposed |
| MD-03 | Keep legal-name history in PartyName with valid intervals and derive the current name | A single mutable legal_name on Party; a name snapshot on each Transaction; both | The regulator asks for the name in force at the time (INT-05); a single mutable name cannot answer an as-of question. | The current name is a query, not a column; transaction snapshots are not stored (a snapshot may be reconsidered if audit requires it). | An audit requirement for a stored snapshot on each transaction | Proposed |
| MD-04 | Use a governed Party identifier and map source identifiers in PartySourceIdentifier | Use the core banking customer number; use a natural key such as national identifier; one identifier per source | Each system numbers customers its own way (INT-10); natural keys can change, repeat across sources or be private. | Identity resolution is a separate process and its authority is unknown (OQ-08); a wrong mapping redirects history. | A decision on the authority and merge rules for Party identity | Proposed |
| MD-05 | Specialise Party into Person and Organisation using shared-key tables | One Party table with nullable person and organisation columns; separate unrelated Person and Organisation entities | A customer can be a person or an organisation (INT-06); both can hold accounts and both need a common identity. | Party type and specialisation record must agree (BR-03); a third kind of party would need a new subtype. | A requirement for a party that is both a person and an organisation | Proposed |
| MD-06 | Record transaction amount as a positive magnitude with a separate debit-or-credit direction | A signed amount; separate debit and credit amount columns | A positive amount with an explicit direction avoids sign-convention errors between systems and makes the rule amount > 0 testable. | Aggregations must apply the direction; a reversal is a separate transaction that references the original. | A source that cannot supply direction separately | Proposed |
| MD-07 | Use start-inclusive, end-exclusive intervals for every valid period and leave the end absent while open | Inclusive end dates; sentinel end dates such as 9999-12-31 | Adjacent periods then meet without overlap, and absence of an end is not mistaken for a real date (Topic 2, section 5.6). | Every period rule and as-of query uses the same convention; sources with inclusive ends must be translated. | A regulatory convention that requires inclusive end dates | Proposed |
| MD-08 | Keep Address as an entity shared through PartyAddress rather than columns on Party | Address columns on Party; one address text field | Addresses can be shared and change over time, and the roadmap lists address among attributes that need history. | Address queries need a join; the meaning of one address per type is still open (OQ-04). | Evidence that parties never share addresses and need no address history | Proposed |
| MD-09 | Defer bundles and non-account subscriptions: include ProductBundleComponent as an assumption, treat subscription beyond accounts as open | Remove bundles; model a general ProductSubscription entity now | The business mentioned bundles (INT-13) but their scope is not confirmed (OQ-09); a subscription entity would be designed without a rule behind it. | BR-26 and BR-27 are exercised on an assumed structure; a confirmed no-bundle answer removes it. | A confirmed answer to OQ-09 or OQ-05 | Proposed |

**Open questions** (each has an owner, a status and a provisional assumption; none is hidden in the diagram)

| ID | Open question | Affects | Owner | Status | Provisional assumption |
| --- | --- | --- | --- | --- | --- |
| OQ-01 | May a minor hold an account independently, without a guardian? | BR-23; Guardianship; AccountHolding | STK-07 | Open | A minor holder needs a guardianship with transact authority in force (BR-23) |
| OQ-02 | May an account exist in a non-operational state with no holder? | BR-20; Account | STK-11 | Provisional | No: every account has at least one holding (BR-20) |
| OQ-03 | May a transaction be recorded in a currency other than its account's currency? | BR-31; Transaction | STK-05 | Provisional | No: the currencies must match (BR-31) |
| OQ-04 | How many addresses of one type may a party have at the same time? | BR-10; PartyAddress | STK-11 | Provisional | One at a time (BR-10) |
| OQ-05 | Is subscription to products other than through opening an account in scope? | Product; process PRC-03 | STK-01 | Open | Out of scope; an account is opened under one product |
| OQ-06 | What is the single meaning of active customer? | customer_status_code; BR-07 | STK-05 | Open | Statuses ACTIVE, INACTIVE and CLOSED exist; their definitions are pending |
| OQ-07 | Is date of birth mandatory for every person? | Person.birth_date; BR-23 | STK-07 | Open | Optional; the minor rule cannot be applied when it is absent |
| OQ-08 | What are the identity-resolution authority and the merge and split rules for parties? | Party; PartySourceIdentifier | STK-09 | Open | Identifiers are mapped one to one; no merge rule is modelled |
| OQ-09 | Are product bundles in scope? | ProductBundleComponent; BR-25 to BR-27 | STK-02 | Open | Bundles are included as an assumption |
| OQ-10 | Does branch assignment need history? | Account.branch_id | STK-02 | Provisional | No: the current branch only |
| OQ-11 | Does the regulator need record time, meaning what the bank knew on a past date? | All valid-interval entities | STK-07 | Open | Not modelled; valid time only |

**Needs that affect the logical design** (Step 13: needs are noted, not designed)

| ID | Need | Need type | Entities and attributes affected | Model adjustment | Deferred design |
| --- | --- | --- | --- | --- | --- |
| NE-01 | Recover the legal name in force on a past date | History | PartyName | Separate entity with a valid interval; current name is derived | Slowly changing or vault structures belong to modules 2D.5 to 2D.7 |
| NE-02 | Recover the address a Party used on a past date | History | PartyAddress | Associative entity with a valid interval | Physical history storage |
| NE-03 | Recover holders and roles of an account on a past date | History | AccountHolding | Associative entity with role and valid interval | Physical history storage and indexing |
| NE-04 | Recover customer status on a past date | History | CustomerRole | Entity with status and valid interval | Physical history storage |
| NE-05 | Report transactions at the grain of one posted transaction | Analytical | Transaction | Transaction carries account, amount, direction, status and posting time; no balance is stored | Fact grain, dimensions and conformed dimensions |
| NE-06 | Report month-end account balances | Analytical | Transaction; Account | Balance is derived from transactions and is not a logical attribute | Periodic snapshot design |
| NE-07 | Signal that a holder role changed | Event | AccountHolding | Holding rows carry valid_from and valid_to so that a change is detectable; no event entity is added | Event contract, ownership and delivery |
| NE-08 | Answer what the bank knew on a past date | History | All valid-interval entities | Not modelled: only business validity is stored (OQ-11) | Bitemporal or vault design if the regulator requires it |

**Compatibility convention.** V1 is the deployed contract and V2 the proposed one. A change is *backward compatible* when readers built for V2 can still read V1 data, and *forward compatible* when readers built for V1 can read V2 data; both are tested, because compatibility is directional. The consumer inventory is the consumer table in 6.2 (CM-01 to CM-09); each change names the consumers affected. Migration follows expand, migrate, contract: a new element is added beside the old one, consumers move and are verified, and only then is the old one retired. Rollback means keeping the old element until the last consumer is verified, and, for a semantic change, a forward fix rather than a silent revert.

**Anticipated schema changes** (Topic 7 classification; each lists a first action)

| ID | Change scenario | Classification | Consumers affected | First action | Dictionary or rule impact |
| --- | --- | --- | --- | --- | --- |
| CH-01 | Add the holder role POWER_OF_ATTORNEY to holder_role_code | Often breaking for consumers that treat the list as closed | Reports and mappings that switch on role | Inventory consumers, test unknown-value handling, then add | Update BR-17 domain and the dictionary entry |
| CH-02 | Make Person.birth_date mandatory | Breaking: tightens a constraint on existing and new data | Onboarding workflows and loads | Profile missing values and agree a remediation before enforcing | Change BR for Person; resolve OQ-07 |
| CH-03 | Rename account_number to account_reference | Breaking: a removal plus an addition | Every reader of the field | Introduce the new name beside the old, migrate readers, then retire | Dictionary history note; naming rule check |
| CH-04 | Redefine ACTIVE customer status | Silently breaking: same values, new meaning | All counts of customers | Create a new status or version; never redefine in place | Glossary, dictionary and BR-07 update |
| CH-05 | Add an optional attribute to Address | Typically compatible for tolerant readers | Readers that reject unknown fields | Test old readers against new records | New dictionary entry and naming check |
| CH-06 | Change transaction_amount from units to minor units | Semantically breaking even if the type is unchanged | All aggregations and reconciliations | Add an explicit unit, convert in a new field, reconcile, then retire | Dictionary unit note; BR-29 review |
| CH-07 | Add GBP-like currencies to currency_code | Often breaking for closed-set consumers | Currency conversions and reports | Check consumer handling of unknown values | BR-12 and BR-29 domain update |

**Deferred physical decisions** (listed, not made)

| ID | Deferred decision | Reason | Receiving module |
| --- | --- | --- | --- |
| DF-01 | Target database platform and engine | Product selection is not a logical decision | 2D.5 |
| DF-02 | Physical data types, lengths, precision and scale | Depend on the engine and the data profile | 2D.5 |
| DF-03 | How identifiers are generated and stored | The logical model fixes identity rules, not the mechanism | 2D.5 |
| DF-04 | Indexes and uniqueness enforcement mechanisms | Depend on query workload | 2D.5 |
| DF-05 | Partitioning and clustering of Transaction and history entities | Depend on volume and access patterns | 2D.5 |
| DF-06 | Storage format and compression | Depend on the platform | 2D.5; 2D.7 |
| DF-07 | Whether referential integrity is enforced in the store or at ingestion | Depends on platform capabilities | 2D.5; 2D.6 |
| DF-08 | Physical denormalisation of the history entities | No denormalisation is recorded at the logical level | 2D.5 |
| DF-09 | Time-zone storage for timestamps | Physical representation of the logical Timestamp | 2D.5 |
| DF-10 | Masking and encryption of personal data | Security implementation is out of scope | 2D.10 |
| DF-11 | Dimensional and vault structures for analytics and history | The needs note records requirements only | 2D.5 to 2D.7; 2D.14 |
| DF-12 | Interface contracts and mappings from source systems | Integration design | 2D.6 |

### 6.11 D11 — Naming standards (Step 14)

The standard is written as patterns that the checker applies to every entity and attribute. The alternation
separator `//` stands for the regular-expression `|`. A rule's good example must match its pattern and its poor example
must not (for `deny:` rules, the reverse); the checker verifies that too.

| ID | Naming rule | Applies to | Pattern | Good example | Poor example |
| --- | --- | --- | --- | --- | --- |
| NS-01 | Entity names are PascalCase business nouns | entity | `^[A-Z][a-z0-9]+([A-Z][a-z0-9]+)*$` | AccountHolding | account_holding |
| NS-02 | Entity names are singular | deny:entity | `[^s]s$` | Branch | Accounts |
| NS-03 | Attribute names are snake_case | attr:any | `^[a-z][a-z0-9]*(_[a-z0-9]+)*$` | valid_from | ValidFrom |
| NS-04 | Identifiers and references end in _id | attr:Identifier | `_id$` | account_id | id |
| NS-05 | Dates end in _date; interval boundaries are valid_from and valid_to | attr:Date | `(_date$ // ^valid_from$ // ^valid_to$)` | opened_date | opened_dt |
| NS-06 | Timestamps end in _timestamp | attr:Timestamp | `_timestamp$` | posted_at_timestamp | posted_time |
| NS-07 | Amounts end in _amount | attr:Amount | `_amount$` | transaction_amount | amt |
| NS-08 | Quantities end in _quantity | attr:Quantity | `_quantity$` | component_quantity | qty |
| NS-09 | Codes end in _code | attr:Code | `_code$` | account_status_code | status |
| NS-10 | Flags start with is_ or has_ | attr:Flag | `^(is // has)_` | is_verified | verified_flag |
| NS-11 | Text attributes end in _name, _text, _number or _identifier | attr:Text | `(_name // _text // _number // _identifier)$` | legal_name | legal |
| NS-12 | Generic names are not used on their own | deny:attr | `^(id // status // type // value // data // flag // date // time // amount // code // name)$` | account_status_code | status |
| NS-13 | Unapproved abbreviations are not used | deny:attr | `(^ // _)(cust // acct // amt // dt // cd // nbr // num // txn // desc // addr)(_ // $)` | account_number | acct_nbr |
| NS-14 | A foreign key ends with the name of the key it references | fk | n/a | guardian_party_id | guardian_ref |

**Relationships.** A relationship is named by a verb phrase in each direction (D8), for example *an Account is held through AccountHolding* and *an AccountHolding holds exactly one Account*. Foreign keys take the name of the key they reference, with a role prefix when a table references the same entity twice (`guardian_party_id`, `minor_party_id`). Suffixes are fixed by the patterns above.

**Case.** Entities use PascalCase and attributes use snake_case in the logical model. A physical platform may require
another style; document the mapping and do not let physical limits change the business definition. Abbreviations are not
approved in this model. Interval boundaries `valid_from` and `valid_to` are the only date names that do not end in
`_date`, by design (ASM-01).

### 6.12 D12 — Data dictionary (Step 15)

One entry for every logical entity and attribute (94 entries). Definitions add information beyond the name. Owners
are **proposals** ("candidate") because nobody has accepted accountability; stewards are unknown. Source is the
requirement or statement that supports the element.

| ID | Element | Kind | Business definition | Technical description | Constraints | Allowed values | Source | Owner | Steward | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DD-001 | Party | Entity | A real-world person or organisation that the bank knows about, whatever role it plays towards the bank. Excludes the roles themselves, such as customer or guardian, which are recorded separately. | Logical entity. Grain: One row per real-world person or organisation known to the bank, whatever role it plays. | Identified by party_id | none | REQ-01; INT-06 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-002 | Person | Entity | The specialisation of a Party that is an individual human being. Holds facts that only apply to individuals, such as date of birth. | Logical entity. Grain: One row per Party of type PERSON. | Identified by party_id | none | REQ-02 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-003 | Organisation | Entity | The specialisation of a Party that is a company, partnership or other legal body. Holds facts that only apply to organisations, such as registration number. | Logical entity. Grain: One row per Party of type ORGANISATION. | Identified by party_id | none | REQ-02 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-004 | PartyName | Entity | A legal name that a Party has carried, together with the period during which that name was in force. Allows the name that applied on a past date to be recovered. | Logical entity. Grain: One row per legal name of a Party and the period during which it was in force. | Identified by party_name_id | none | REQ-05; INT-05 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-005 | PartySourceIdentifier | Entity | The identifier by which one source system refers to a Party, kept so that records from the core banking, cards and CRM systems can be tied to one Party. Does not prove identity by itself. | Logical entity. Grain: One row per identifier that a source system uses for a Party. | Identified by party_source_identifier_id | none | REQ-08; INT-10 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-006 | CustomerRole | Entity | A period during which a Party was treated by the bank as a customer, with the customer status in force. A Party can leave and later return to the role. | Logical entity. Grain: One row per period during which a Party acted as a customer, with the status in force. | Identified by customer_role_id | none | REQ-14; INT-09 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-007 | Address | Entity | A postal location recorded once, independent of the Parties that use it, so that shared addresses are held a single time. | Logical entity. Grain: One row per distinct postal address, independent of who uses it. | Identified by address_id | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-008 | PartyAddress | Entity | The use of an Address by a Party for one purpose, such as residence or mailing, during one period. Carries the type and the dates because they describe the relationship, not the Address. | Logical entity. Grain: One row per use of an Address by a Party in one address type for one period. | Identified by party_address_id | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-009 | ContactPoint | Entity | A way of reaching a Party, such as an email address or telephone number, with its verification state. Excludes consent and marketing preferences, which are outside this model. | Logical entity. Grain: One row per contact method held for a Party. | Identified by contact_point_id | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-010 | Branch | Entity | A physical or administrative location of the bank through which accounts can be serviced. | Logical entity. Grain: One row per bank branch. | Identified by branch_id | none | REQ-10; INT-14 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-011 | Product | Entity | A deposit, loan or card offering that the bank defines and sells, under which accounts are opened. May itself be a bundle of other products. | Logical entity. Grain: One row per product the bank offers. | Identified by product_id | none | REQ-01 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-012 | ProductBundleComponent | Entity | The inclusion of one product as a component inside a bundle product, with the quantity included. Makes the bundle structure explicit and checkable for cycles. | Logical entity. Grain: One row per component product inside a bundle product. | Identified by product_bundle_component_id | none | REQ-11; INT-13 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-013 | Account | Entity | A relationship through which the bank holds and tracks money or credit for its holders, opened under one product and with its own lifecycle. Excludes card accounts and loan facilities administered elsewhere. | Logical entity. Grain: One row per account relationship opened under a product. | Identified by account_id | none | REQ-01; REQ-06 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-014 | AccountHolding | Entity | The fact that one Party holds one Account in one holder role during one period. Resolves the many-to-many between Parties and Accounts and keeps the role and dates of each holder. | Logical entity. Grain: One row per Party, account, holder role and start date. | Identified by account_holding_id | none | REQ-03; INT-04 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-015 | Guardianship | Entity | The authority of one Party, the guardian, to act for another Party, the minor, during a period, with the type of authority and the evidence on which it rests. | Logical entity. Grain: One row per guardian, minor and period of authority. | Identified by guardianship_id | none | REQ-09; INT-08 | Unknown (candidate STK-07) | Unknown | Illustrative assumption |
| DD-016 | Transaction | Entity | A single monetary movement recorded against exactly one Account, with its amount, direction, status and posting time. Excludes authorisation messages and card-network detail. | Logical entity. Grain: One row per monetary movement recorded against exactly one account. | Identified by transaction_id | none | REQ-07; INT-11 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-017 | Party.party_id | Attribute | Governed identifier of a Party within the enterprise model. Stays the same when names, addresses or roles change; source-system numbers are mapped to it, never used instead of it. | Logical identifier; representation deferred (DF-03) | Required; rules BR-03, BR-04, BR-06, BR-07, BR-09, BR-11, BR-17, BR-21 | none | REQ-01; INT-06 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-018 | Party.party_type_code | Attribute | Classification of a Party as an individual or as an organisation. Decides which specialisation record must exist. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-02, BR-03 | PERSON, ORGANISATION | REQ-01; INT-06 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-019 | Party.created_date | Attribute | Calendar date on which the bank first recorded the Party. Not the date the Party was born or incorporated. | Calendar date without time of day | Required; rules BR-02 | none | REQ-01; INT-06 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-020 | Person.party_id | Attribute | Identifier of the Party that this individual record specialises. Shares the identity of the Party and cannot exist without it. | Logical identifier; representation deferred (DF-03) | Required; references Party.party_id; rules BR-03, BR-23 | none | REQ-02 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-021 | Person.birth_date | Attribute | Calendar date on which the individual was born, as evidenced to the bank. Used to decide whether the individual is a minor on a given date. Optional until the business decides whether it is mandatory (OQ-07). | Calendar date without time of day | Optional; rules BR-23 | none | REQ-02 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-022 | Organisation.party_id | Attribute | Identifier of the Party that this organisation record specialises. Shares the identity of the Party and cannot exist without it. | Logical identifier; representation deferred (DF-03) | Required; references Party.party_id; rules BR-03 | none | REQ-02 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-023 | Organisation.registration_number | Attribute | Number under which the organisation is registered with its registering authority. Not unique across authorities and not an identifier of the Party. | Logical text value; length and encoding deferred (DF-02) | Optional | none | REQ-02 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-024 | PartyName.party_name_id | Attribute | Identifier of one legal-name record, distinguishing it from other names of the same Party. | Logical identifier; representation deferred (DF-03) | Required | none | REQ-05; INT-05 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-025 | PartyName.party_id | Attribute | Identifier of the Party that carries this legal name during the stated period. | Logical identifier; representation deferred (DF-03) | Required; references Party.party_id; rules BR-04, BR-05 | none | REQ-05; INT-05 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-026 | PartyName.legal_name | Attribute | Full name of the Party as recognised in law during the stated period. Excludes nicknames and marketing names. | Logical text value; length and encoding deferred (DF-02) | Required; rules BR-04 | none | REQ-05; INT-05 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-027 | PartyName.valid_from | Attribute | First calendar date on which this legal name was in force. The period is closed at the start and open at the end. | Calendar date without time of day | Required; rules BR-04, BR-05 | none | REQ-05; INT-05 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-028 | PartyName.valid_to | Attribute | Calendar date on which this legal name stopped being in force, exclusive. Absent while the name is still current. | Calendar date without time of day | Optional; rules BR-05 | none | REQ-05; INT-05 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-029 | PartySourceIdentifier.party_source_identifier_id | Attribute | Governed identifier that distinguishes one mapping between a source system's identifier and a Party from every other mapping. | Logical identifier; representation deferred (DF-03) | Required | none | REQ-08; INT-10 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-030 | PartySourceIdentifier.party_id | Attribute | Identifier of the Party to which the source system's own identifier is mapped. | Logical identifier; representation deferred (DF-03) | Required; references Party.party_id; rules BR-06 | none | REQ-08; INT-10 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-031 | PartySourceIdentifier.source_system_code | Attribute | Code of the source system that issued the identifier, so that the same string issued by two systems is not confused. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-06 | CORE_BANKING, CARDS, CRM | REQ-08; INT-10 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-032 | PartySourceIdentifier.source_party_identifier | Attribute | Identifier as the named source system holds it. Unique only within that source system. | Logical text value; length and encoding deferred (DF-02) | Required; rules BR-06 | none | REQ-08; INT-10 | Unknown (candidate STK-09) | Unknown | Illustrative assumption |
| DD-033 | CustomerRole.customer_role_id | Attribute | Governed identifier that distinguishes one period of customer status for a Party from every other period. | Logical identifier; representation deferred (DF-03) | Required | none | REQ-14; INT-09 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-034 | CustomerRole.party_id | Attribute | Identifier of the Party that acted as a customer during the period. | Logical identifier; representation deferred (DF-03) | Required; references Party.party_id; rules BR-07, BR-08 | none | REQ-14; INT-09 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-035 | CustomerRole.customer_status_code | Attribute | Status of the customer relationship during the period, from a governed list. Does not express credit risk or marketing consent. Meaning of active is pending (OQ-06). | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-07 | ACTIVE, INACTIVE, CLOSED | REQ-14; INT-09 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-036 | CustomerRole.valid_from | Attribute | First calendar date of the customer-role period. | Calendar date without time of day | Required; rules BR-07, BR-08 | none | REQ-14; INT-09 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-037 | CustomerRole.valid_to | Attribute | Calendar date on which the customer-role period ended, exclusive. Absent while the Party remains a customer. | Calendar date without time of day | Optional; rules BR-08 | none | REQ-14; INT-09 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-038 | Address.address_id | Attribute | Governed identifier that distinguishes one recorded postal location from every other, whoever uses it. | Logical identifier; representation deferred (DF-03) | Required; rules BR-09 | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-039 | Address.address_line_text | Attribute | Street-level lines that locate the premises, written as the postal service expects. Excludes the locality and country. | Logical text value; length and encoding deferred (DF-02) | Required; rules BR-09 | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-040 | Address.locality_name | Attribute | Name of the town, city or district in which the premises lie. | Logical text value; length and encoding deferred (DF-02) | Required; rules BR-09 | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-041 | Address.postal_code | Attribute | Code assigned by the postal service to the delivery area. Optional because some countries and addresses have none. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Optional | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-042 | Address.country_code | Attribute | Code of the country where the premises lie, taken from a governed country list so that values compare across systems. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-09 | IN, GB, US | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-043 | PartyAddress.party_address_id | Attribute | Governed identifier that distinguishes one use of a postal location by a Party for one purpose and period. | Logical identifier; representation deferred (DF-03) | Required | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-044 | PartyAddress.party_id | Attribute | Identifier of the Party that uses the address during the period. | Logical identifier; representation deferred (DF-03) | Required; references Party.party_id; rules BR-09, BR-10 | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-045 | PartyAddress.address_id | Attribute | Identifier of the address that the Party uses during the period. | Logical identifier; representation deferred (DF-03) | Required; references Address.address_id; rules BR-09 | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-046 | PartyAddress.address_type_code | Attribute | Purpose for which the Party uses the address, such as residential, mailing or registered office. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-09, BR-10 | RESIDENTIAL, MAILING, REGISTERED | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-047 | PartyAddress.valid_from | Attribute | First calendar date on which the Party used the address for this purpose. | Calendar date without time of day | Required; rules BR-09, BR-10 | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-048 | PartyAddress.valid_to | Attribute | Calendar date on which the Party stopped using the address for this purpose, exclusive. Absent while still in use. | Calendar date without time of day | Optional; rules BR-10 | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-049 | ContactPoint.contact_point_id | Attribute | Identifier of one contact method held for a Party. | Logical identifier; representation deferred (DF-03) | Required | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-050 | ContactPoint.party_id | Attribute | Identifier of the Party that can be reached through this contact method. | Logical identifier; representation deferred (DF-03) | Required; references Party.party_id; rules BR-11 | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-051 | ContactPoint.contact_type_code | Attribute | Kind of contact method, such as email or telephone, which decides how the value is read. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-11 | EMAIL, PHONE | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-052 | ContactPoint.contact_value_text | Attribute | The email address or telephone number itself, as given by the Party. Sensitive personal data. | Logical text value; length and encoding deferred (DF-02) | Required; rules BR-11 | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-053 | ContactPoint.is_verified | Attribute | True when the bank has confirmed that the contact method works and belongs to the Party; false otherwise. | True or false | Required; rules BR-11 | none | Unknown | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-054 | Branch.branch_id | Attribute | Governed identifier that distinguishes one bank location from every other, independent of its name. | Logical identifier; representation deferred (DF-03) | Required; rules BR-13 | none | REQ-10; INT-14 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-055 | Branch.branch_name | Attribute | Name by which the bank and its customers refer to the location where accounts are serviced. | Logical text value; length and encoding deferred (DF-02) | Required; rules BR-16 | none | REQ-10; INT-14 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-056 | Branch.branch_status_code | Attribute | Whether the branch is open for servicing accounts or closed. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-16 | OPEN, CLOSED | REQ-10; INT-14 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-057 | Product.product_id | Attribute | Identifier of one product definition within the enterprise model. | Logical identifier; representation deferred (DF-03) | Required; rules BR-12, BR-25, BR-26 | none | REQ-01 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-058 | Product.product_code | Attribute | Short business code by which the product is catalogued and sold. Unique across the product catalogue. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-24 | none | REQ-01 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-059 | Product.product_name | Attribute | Customer-facing name under which the product is marketed and described in contracts. | Logical text value; length and encoding deferred (DF-02) | Required; rules BR-24 | none | REQ-01 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-060 | Product.product_category_code | Attribute | Broad family of the product, namely deposit, loan or card, used to route governance and reporting. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-24 | DEPOSIT, LOAN, CARD | REQ-01 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-061 | Product.is_bundle_capable | Attribute | True when the product may contain other products as components; false when it is sold only on its own. | True or false | Required; rules BR-24, BR-26 | none | REQ-01 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-062 | ProductBundleComponent.product_bundle_component_id | Attribute | Governed identifier that distinguishes one inclusion of a component product inside a bundle from every other inclusion. | Logical identifier; representation deferred (DF-03) | Required | none | REQ-11; INT-13 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-063 | ProductBundleComponent.bundle_product_id | Attribute | Identifier of the product that acts as the bundle and contains the component. | Logical identifier; representation deferred (DF-03) | Required; references Product.product_id; rules BR-25, BR-26, BR-27 | none | REQ-11; INT-13 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-064 | ProductBundleComponent.component_product_id | Attribute | Identifier of the product that is included inside the bundle. | Logical identifier; representation deferred (DF-03) | Required; references Product.product_id; rules BR-25, BR-27 | none | REQ-11; INT-13 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-065 | ProductBundleComponent.component_quantity | Attribute | Number of units of the component included in one unit of the bundle. Must be greater than zero. | Whole number of units | Required; rules BR-25 | none | REQ-11; INT-13 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-066 | Account.account_id | Attribute | Governed identifier of an Account within the enterprise model, independent of the account number shown to customers. | Logical identifier; representation deferred (DF-03) | Required; rules BR-17, BR-20, BR-28, BR-31 | none | REQ-01; REQ-06 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-067 | Account.account_number | Attribute | Number by which the bank and its customers refer to the account. Unique, but may change on migration, so it does not replace the identifier. | Logical text value; length and encoding deferred (DF-02) | Required; rules BR-12 | none | REQ-01; REQ-06 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-068 | Account.product_id | Attribute | Identifier of the product under which the account was opened. | Logical identifier; representation deferred (DF-03) | Required; references Product.product_id; rules BR-12 | none | REQ-01; REQ-06 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-069 | Account.branch_id | Attribute | Identifier of the branch that services the account. Absent while the account has no designated branch. | Logical identifier; representation deferred (DF-03) | Optional; references Branch.branch_id; rules BR-13 | none | REQ-01; REQ-06 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-070 | Account.account_status_code | Attribute | Position of the account in its lifecycle: pending, open, suspended or closed. Does not express credit quality or card authorisation state. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-12, BR-14, BR-15 | PENDING, OPEN, SUSPENDED, CLOSED | REQ-01; REQ-06 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-071 | Account.currency_code | Attribute | Code of the currency in which the balance is kept, taken from the governed currency list. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-12, BR-31 | INR, GBP, USD | REQ-01; REQ-06 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-072 | Account.opened_date | Attribute | Calendar date on which the account became open for use. Excludes the date of application and the date of first funding. | Calendar date without time of day | Optional; rules BR-14, BR-15 | none | REQ-01; REQ-06 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-073 | Account.closed_date | Attribute | Calendar date on which the account was closed. Present only for closed accounts, which are retained. | Calendar date without time of day | Optional; rules BR-14 | none | REQ-01; REQ-06 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-074 | AccountHolding.account_holding_id | Attribute | Governed identifier that distinguishes one holding of an account by a Party in a role and period from every other holding. | Logical identifier; representation deferred (DF-03) | Required | none | REQ-03; INT-04 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-075 | AccountHolding.party_id | Attribute | Identifier of the Party that holds the account in the stated role. | Logical identifier; representation deferred (DF-03) | Required; references Party.party_id; rules BR-17, BR-19, BR-23 | none | REQ-03; INT-04 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-076 | AccountHolding.account_id | Attribute | Reference to the account being held, which must already exist before the holding can start. | Logical identifier; representation deferred (DF-03) | Required; references Account.account_id; rules BR-17, BR-19, BR-20 | none | REQ-03; INT-04 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-077 | AccountHolding.holder_role_code | Attribute | Role the Party has on the account, such as primary, joint or sole holder. Describes the relationship, not the Party. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-17, BR-19 | PRIMARY_HOLDER, JOINT_HOLDER, SOLE_HOLDER | REQ-03; INT-04 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-078 | AccountHolding.valid_from | Attribute | First calendar date on which the Party held the account in this role. | Calendar date without time of day | Required; rules BR-17, BR-18, BR-19, BR-23 | none | REQ-03; INT-04 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-079 | AccountHolding.valid_to | Attribute | Calendar date on which the Party stopped holding the account in this role, exclusive. Absent while the holding continues. | Calendar date without time of day | Optional; rules BR-18, BR-19, BR-23 | none | REQ-03; INT-04 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-080 | Guardianship.guardianship_id | Attribute | Governed identifier that distinguishes one record of guardian authority over a minor from every other record. | Logical identifier; representation deferred (DF-03) | Required | none | REQ-09; INT-08 | Unknown (candidate STK-07) | Unknown | Illustrative assumption |
| DD-081 | Guardianship.guardian_party_id | Attribute | Identifier of the Party that holds the authority to act for the minor. | Logical identifier; representation deferred (DF-03) | Required; references Party.party_id; rules BR-21, BR-22 | none | REQ-09; INT-08 | Unknown (candidate STK-07) | Unknown | Illustrative assumption |
| DD-082 | Guardianship.minor_party_id | Attribute | Identifier of the Party for whom the guardian is authorised to act. | Logical identifier; representation deferred (DF-03) | Required; references Party.party_id; rules BR-21, BR-22, BR-23 | none | REQ-09; INT-08 | Unknown (candidate STK-07) | Unknown | Illustrative assumption |
| DD-083 | Guardianship.authority_type_code | Attribute | Extent of the guardian's authority: to transact on the minor's behalf or to give consent only. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-21, BR-23 | TRANSACT, CONSENT_ONLY | REQ-09; INT-08 | Unknown (candidate STK-07) | Unknown | Illustrative assumption |
| DD-084 | Guardianship.valid_from | Attribute | First calendar date on which the guardian's authority was in force. | Calendar date without time of day | Required; rules BR-21, BR-22, BR-23 | none | REQ-09; INT-08 | Unknown (candidate STK-07) | Unknown | Illustrative assumption |
| DD-085 | Guardianship.valid_to | Attribute | Calendar date on which the guardian's authority ended, exclusive. Absent while the authority continues. | Calendar date without time of day | Optional; rules BR-22, BR-23 | none | REQ-09; INT-08 | Unknown (candidate STK-07) | Unknown | Illustrative assumption |
| DD-086 | Guardianship.evidence_reference_text | Attribute | Reference to the document or case file on which the authority rests. Does not contain the document itself. | Logical text value; length and encoding deferred (DF-02) | Required; rules BR-21 | none | REQ-09; INT-08 | Unknown (candidate STK-07) | Unknown | Illustrative assumption |
| DD-087 | Transaction.transaction_id | Attribute | Governed identifier that distinguishes one monetary movement from every other, whichever account it belongs to. | Logical identifier; representation deferred (DF-03) | Required; rules BR-32 | none | REQ-07; INT-11 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-088 | Transaction.account_id | Attribute | Identifier of the single account against which the transaction is recorded. | Logical identifier; representation deferred (DF-03) | Required; references Account.account_id; rules BR-28, BR-31, BR-32 | none | REQ-07; INT-11 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-089 | Transaction.transaction_amount | Attribute | Size of the movement as a positive magnitude in the transaction currency. The direction is given separately by the debit or credit code. | Decimal magnitude in the stated currency; precision and scale deferred (DF-02) | Required; rules BR-29 | none | REQ-07; INT-11 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-090 | Transaction.currency_code | Attribute | Code of the currency in which the amount is expressed, taken from the governed currency list. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-29, BR-31 | INR, GBP, USD | REQ-07; INT-11 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-091 | Transaction.debit_credit_code | Attribute | Direction of the movement: debit takes money out of the account, credit puts money in. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-29 | DEBIT, CREDIT | REQ-07; INT-11 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-092 | Transaction.transaction_status_code | Attribute | Position of the transaction in its lifecycle: pending, posted or reversed. | Logical code from a governed or business-defined list; representation deferred (DF-02) | Required; rules BR-29, BR-30 | PENDING, POSTED, REVERSED | REQ-07; INT-11 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-093 | Transaction.posted_at_timestamp | Attribute | Instant at which the transaction was posted to the account, with time zone defined by the dictionary. Present once the transaction is posted. | Instant with a time zone defined in this dictionary; storage deferred (DF-09) | Optional; rules BR-30 | none | REQ-07; INT-11 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |
| DD-094 | Transaction.reverses_transaction_id | Attribute | Identifier of the earlier transaction that this transaction cancels. Absent for ordinary transactions. | Logical identifier; representation deferred (DF-03) | Optional; references Transaction.transaction_id; rules BR-32 | none | REQ-07; INT-11 | Unknown (candidate STK-02) | Unknown | Illustrative assumption |

### 6.13 D13 — Model validation and review findings (Steps 16, 17 and 18)

#### Test data (synthetic)

The base dataset is valid: the checker confirms that it violates no rule. Scenarios change it with `add`, `set` and
`remove` operations, separated by ` + `; a `Query` scenario asks what was true on a date.

| ID | Entity | Attributes (key=value) |
| --- | --- | --- |
| DAT-01 | Party | party_id=P101; party_type_code=PERSON; created_date=2020-01-10 |
| DAT-02 | Party | party_id=P102; party_type_code=PERSON; created_date=2020-02-01 |
| DAT-03 | Party | party_id=P103; party_type_code=ORGANISATION; created_date=2021-06-01 |
| DAT-04 | Party | party_id=P104; party_type_code=PERSON; created_date=2022-11-15 |
| DAT-05 | Party | party_id=P105; party_type_code=PERSON; created_date=2022-11-15 |
| DAT-06 | Person | party_id=P101; birth_date=1985-03-14 |
| DAT-07 | Person | party_id=P102; birth_date=1990-07-21 |
| DAT-08 | Person | party_id=P104; birth_date=2012-05-01 |
| DAT-09 | Person | party_id=P105; birth_date=1982-11-02 |
| DAT-10 | Organisation | party_id=P103; registration_number=REG7781 |
| DAT-11 | PartyName | party_name_id=N1; party_id=P101; legal_name=Mira Rao; valid_from=2020-01-10; valid_to=2024-03-01 |
| DAT-12 | PartyName | party_name_id=N2; party_id=P101; legal_name=Mira R. Rao; valid_from=2024-03-01; valid_to=null |
| DAT-13 | PartyName | party_name_id=N3; party_id=P102; legal_name=Dev Patel; valid_from=2020-02-01; valid_to=null |
| DAT-14 | PartyName | party_name_id=N4; party_id=P103; legal_name=Harbor Trading Ltd; valid_from=2021-06-01; valid_to=null |
| DAT-15 | PartyName | party_name_id=N5; party_id=P104; legal_name=Anaya Rao; valid_from=2022-11-15; valid_to=null |
| DAT-16 | PartyName | party_name_id=N6; party_id=P105; legal_name=Kiran Rao; valid_from=2022-11-15; valid_to=null |
| DAT-17 | PartySourceIdentifier | party_source_identifier_id=S1; party_id=P101; source_system_code=CORE_BANKING; source_party_identifier=C9001 |
| DAT-18 | PartySourceIdentifier | party_source_identifier_id=S2; party_id=P101; source_system_code=CRM; source_party_identifier=X55 |
| DAT-19 | PartySourceIdentifier | party_source_identifier_id=S3; party_id=P102; source_system_code=CORE_BANKING; source_party_identifier=C9002 |
| DAT-20 | PartySourceIdentifier | party_source_identifier_id=S4; party_id=P101; source_system_code=CARDS; source_party_identifier=K77 |
| DAT-21 | CustomerRole | customer_role_id=R1; party_id=P101; customer_status_code=ACTIVE; valid_from=2020-01-10; valid_to=null |
| DAT-22 | CustomerRole | customer_role_id=R2; party_id=P102; customer_status_code=ACTIVE; valid_from=2020-02-01; valid_to=null |
| DAT-23 | CustomerRole | customer_role_id=R3; party_id=P103; customer_status_code=ACTIVE; valid_from=2021-06-01; valid_to=null |
| DAT-24 | CustomerRole | customer_role_id=R4; party_id=P105; customer_status_code=ACTIVE; valid_from=2022-11-15; valid_to=null |
| DAT-25 | Address | address_id=AD1; address_line_text=12 Lake Road; locality_name=Mumbai; postal_code=400001; country_code=IN |
| DAT-26 | Address | address_id=AD2; address_line_text=5 Park Street; locality_name=Pune; postal_code=411001; country_code=IN |
| DAT-27 | PartyAddress | party_address_id=PA1; party_id=P101; address_id=AD1; address_type_code=RESIDENTIAL; valid_from=2020-01-10; valid_to=null |
| DAT-28 | PartyAddress | party_address_id=PA2; party_id=P101; address_id=AD2; address_type_code=MAILING; valid_from=2020-01-10; valid_to=null |
| DAT-29 | ContactPoint | contact_point_id=CP1; party_id=P101; contact_type_code=EMAIL; contact_value_text=mira@example.test; is_verified=true |
| DAT-30 | Branch | branch_id=B01; branch_name=Central Branch; branch_status_code=OPEN |
| DAT-31 | Branch | branch_id=B02; branch_name=North Branch; branch_status_code=OPEN |
| DAT-32 | Product | product_id=PR1; product_code=DEP_STD; product_name=Everyday Current Account; product_category_code=DEPOSIT; is_bundle_capable=false |
| DAT-33 | Product | product_id=PR2; product_code=DEP_SAV; product_name=Savings Account; product_category_code=DEPOSIT; is_bundle_capable=false |
| DAT-34 | Product | product_id=PR3; product_code=BND_ESS; product_name=Essentials Bundle; product_category_code=DEPOSIT; is_bundle_capable=true |
| DAT-35 | ProductBundleComponent | product_bundle_component_id=PBC1; bundle_product_id=PR3; component_product_id=PR1; component_quantity=1 |
| DAT-36 | ProductBundleComponent | product_bundle_component_id=PBC2; bundle_product_id=PR3; component_product_id=PR2; component_quantity=1 |
| DAT-37 | Account | account_id=A800; account_number=ACC800; product_id=PR1; branch_id=B01; account_status_code=OPEN; currency_code=INR; opened_date=2020-02-01 |
| DAT-38 | Account | account_id=A801; account_number=ACC801; product_id=PR1; account_status_code=PENDING; currency_code=INR |
| DAT-39 | Account | account_id=A802; account_number=ACC802; product_id=PR2; branch_id=B02; account_status_code=CLOSED; currency_code=INR; opened_date=2019-05-01; closed_date=2023-12-31 |
| DAT-40 | Account | account_id=A803; account_number=ACC803; product_id=PR1; branch_id=B01; account_status_code=OPEN; currency_code=INR; opened_date=2021-06-15 |
| DAT-41 | Account | account_id=A804; account_number=ACC804; product_id=PR1; branch_id=B01; account_status_code=OPEN; currency_code=INR; opened_date=2023-01-01 |
| DAT-42 | AccountHolding | account_holding_id=H1; party_id=P101; account_id=A800; holder_role_code=PRIMARY_HOLDER; valid_from=2020-02-01; valid_to=null |
| DAT-43 | AccountHolding | account_holding_id=H2; party_id=P102; account_id=A800; holder_role_code=JOINT_HOLDER; valid_from=2020-02-01; valid_to=null |
| DAT-44 | AccountHolding | account_holding_id=H3; party_id=P101; account_id=A801; holder_role_code=SOLE_HOLDER; valid_from=2024-05-10; valid_to=null |
| DAT-45 | AccountHolding | account_holding_id=H4; party_id=P103; account_id=A803; holder_role_code=SOLE_HOLDER; valid_from=2021-06-15; valid_to=null |
| DAT-46 | AccountHolding | account_holding_id=H5; party_id=P105; account_id=A804; holder_role_code=PRIMARY_HOLDER; valid_from=2023-01-01; valid_to=null |
| DAT-47 | AccountHolding | account_holding_id=H6; party_id=P104; account_id=A804; holder_role_code=JOINT_HOLDER; valid_from=2023-01-01; valid_to=null |
| DAT-48 | AccountHolding | account_holding_id=H7; party_id=P102; account_id=A802; holder_role_code=SOLE_HOLDER; valid_from=2019-05-01; valid_to=2023-12-31 |
| DAT-49 | Guardianship | guardianship_id=G1; guardian_party_id=P105; minor_party_id=P104; authority_type_code=TRANSACT; valid_from=2022-12-01; valid_to=null; evidence_reference_text=Case file 118 |
| DAT-50 | Transaction | transaction_id=T1; account_id=A800; transaction_amount=250.00; currency_code=INR; debit_credit_code=DEBIT; transaction_status_code=POSTED; posted_at_timestamp=2024-03-05T10:15:00 |
| DAT-51 | Transaction | transaction_id=T2; account_id=A800; transaction_amount=500.00; currency_code=INR; debit_credit_code=CREDIT; transaction_status_code=POSTED; posted_at_timestamp=2024-03-06T09:00:00 |
| DAT-52 | Transaction | transaction_id=T3; account_id=A800; transaction_amount=250.00; currency_code=INR; debit_credit_code=CREDIT; transaction_status_code=POSTED; posted_at_timestamp=2024-03-07T11:00:00; reverses_transaction_id=T1 |
| DAT-53 | Transaction | transaction_id=T4; account_id=A802; transaction_amount=75.50; currency_code=INR; debit_credit_code=DEBIT; transaction_status_code=POSTED; posted_at_timestamp=2023-11-20T14:30:00 |
| DAT-54 | Transaction | transaction_id=T5; account_id=A803; transaction_amount=1200.00; currency_code=INR; debit_credit_code=CREDIT; transaction_status_code=PENDING |

#### Scenario results

52 scenarios were run: 11 valid and 37 invalid mutations, and 4 history queries. **Expected** is what the business
rule says should happen; **Observed** is what the model produced when the checker ran it. They match for every
scenario, and the explanation says why. Scenarios that exercise `Open` rules are provisional (BR-10, BR-23, BR-31).

| ID | Scenario | Kind | Operations | Rule reference | Expected outcome | Expected rules | Observed outcome | Observed rules | Explanation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCN-01 | Two Parties hold one account in different roles | Mutation | add AccountHolding{account_holding_id=H8,party_id=P105,account_id=A800,holder_role_code=JOINT_HOLDER,valid_from=2024-01-01} | BR-01; BR-17; BR-19 | Accept | none | Accept | none | Joint holding is supported; the new holding has its own role and start date. |
| SCN-02 | One Party opens a second account and holds it | Mutation | add Account{account_id=A805,account_number=ACC805,product_id=PR1,account_status_code=PENDING,currency_code=INR} + add AccountHolding{account_holding_id=H9,party_id=P102,account_id=A805,holder_role_code=SOLE_HOLDER,valid_from=2025-01-05} | BR-02; BR-12; BR-17; BR-20 | Accept | none | Accept | none | A Party may hold many accounts; the pending account has its holder from the start. |
| SCN-03 | Account being opened has no designated branch | Mutation | add Account{account_id=A806,account_number=ACC806,product_id=PR2,account_status_code=PENDING,currency_code=INR} + add AccountHolding{account_holding_id=H10,party_id=P105,account_id=A806,holder_role_code=SOLE_HOLDER,valid_from=2025-02-01} | BR-13; BR-15 | Accept | none | Accept | none | Branch assignment is optional; a pending account needs no opening date. |
| SCN-04 | Legal name changes and history is kept | Mutation | set DAT-13.valid_to=2025-01-01 + add PartyName{party_name_id=N7,party_id=P102,legal_name=Dev K. Patel,valid_from=2025-01-01} | BR-04; BR-05 | Accept | none | Accept | none | The old name ends the day the new one starts; intervals are start-inclusive, end-exclusive. |
| SCN-05 | Account closes and everything is retained | Mutation | set DAT-40.account_status_code=CLOSED + set DAT-40.closed_date=2025-01-01 | BR-14 | Accept | none | Accept | none | Closed accounts are retained; the closing date is present and not before the opening date. |
| SCN-06 | Minor becomes a joint holder with an authorised guardian | Mutation | add AccountHolding{account_holding_id=H11,party_id=P104,account_id=A800,holder_role_code=JOINT_HOLDER,valid_from=2024-02-01} | BR-17; BR-23 | Accept | none | Accept | none | Guardianship G1 gives transact authority on the start date. |
| SCN-07 | Bundle with two components | Mutation | add Product{product_id=PR4,product_code=BND_PLUS,product_name=Plus Bundle,product_category_code=DEPOSIT,is_bundle_capable=true} + add ProductBundleComponent{product_bundle_component_id=PBC3,bundle_product_id=PR4,component_product_id=PR1,component_quantity=1} + add ProductBundleComponent{product_bundle_component_id=PBC9,bundle_product_id=PR4,component_product_id=PR2,component_quantity=1} | BR-24; BR-25; BR-26; BR-27 | Accept | none | Accept | none | A bundle-capable product may contain another product. |
| SCN-08 | Reversal of a transaction on the same account | Mutation | add Transaction{transaction_id=T6,account_id=A800,transaction_amount=500.00,currency_code=INR,debit_credit_code=DEBIT,transaction_status_code=POSTED,posted_at_timestamp=2024-03-08T09:00:00,reverses_transaction_id=T2} | BR-28; BR-29; BR-30; BR-32 | Accept | none | Accept | none | A reversal references an earlier transaction on the same account. |
| SCN-09 | Same Party known to a second source system | Mutation | add PartySourceIdentifier{party_source_identifier_id=S5,party_id=P102,source_system_code=CRM,source_party_identifier=X56} | BR-06 | Accept | none | Accept | none | A Party may have identifiers from several systems. |
| SCN-10 | Role ends and a new period of the same role starts the same day | Mutation | set DAT-42.valid_to=2024-06-01 + add AccountHolding{account_holding_id=H12,party_id=P101,account_id=A800,holder_role_code=PRIMARY_HOLDER,valid_from=2024-06-01} | BR-18; BR-19 | Accept | none | Accept | none | Adjacent periods do not overlap under the start-inclusive, end-exclusive convention. |
| SCN-11 | Second customer-role period after the first ended | Mutation | set DAT-22.valid_to=2023-01-01 + add CustomerRole{customer_role_id=R5,party_id=P102,customer_status_code=ACTIVE,valid_from=2024-01-01} | BR-07; BR-08 | Accept | none | Accept | none | A Party can leave and later return to the customer role. |
| SCN-12 | Duplicate Party identifier | Mutation | add Party{party_id=P101,party_type_code=PERSON,created_date=2025-01-01} | BR-01 | Reject | BR-01 | Reject | BR-01 | Two Party rows share P101; an identifier identifies one instance only. |
| SCN-13 | Party with no type | Mutation | add Party{party_id=P106,created_date=2025-01-01} | BR-02 | Reject | BR-02 | Reject | BR-02 | The Party type is mandatory. |
| SCN-14 | Person record for an organisation Party | Mutation | add Person{party_id=P103,birth_date=1970-01-01} | BR-03 | Reject | BR-03 | Reject | BR-03 | An ORGANISATION Party cannot also be a Person. |
| SCN-15 | Holding refers to an account that does not exist | Mutation | add AccountHolding{account_holding_id=H13,party_id=P102,account_id=A999,holder_role_code=JOINT_HOLDER,valid_from=2025-01-01} | BR-17 | Reject | BR-17 | Reject | BR-17 | The account reference must resolve. |
| SCN-16 | Holding has no holder role | Mutation | add AccountHolding{account_holding_id=H14,party_id=P102,account_id=A803,valid_from=2025-01-01} | BR-17 | Reject | BR-17 | Reject | BR-17 | The role is mandatory for a holding. |
| SCN-17 | Holding ends before it starts | Mutation | add AccountHolding{account_holding_id=H15,party_id=P105,account_id=A800,holder_role_code=JOINT_HOLDER,valid_from=2025-02-01,valid_to=2025-01-01} | BR-18 | Reject | BR-18 | Reject | BR-18 | The end date must be later than the start date. |
| SCN-18 | Holding with a zero-length period | Mutation | add AccountHolding{account_holding_id=H16,party_id=P105,account_id=A800,holder_role_code=JOINT_HOLDER,valid_from=2025-02-01,valid_to=2025-02-01} | BR-18 | Reject | BR-18 | Reject | BR-18 | Under a start-inclusive, end-exclusive interval a zero-length period holds nothing. |
| SCN-19 | Historical holding overlaps an open-ended one | Mutation | add AccountHolding{account_holding_id=H17,party_id=P101,account_id=A800,holder_role_code=PRIMARY_HOLDER,valid_from=2021-01-01,valid_to=2022-01-01} | BR-19 | Reject | BR-19 | Reject | BR-19 | The same Party, account and role cannot have overlapping periods. |
| SCN-20 | Transaction with no account | Mutation | add Transaction{transaction_id=T7,transaction_amount=10.00,currency_code=INR,debit_credit_code=DEBIT,transaction_status_code=PENDING} | BR-28 | Reject | BR-28 | Reject | BR-28 | A transaction cannot exist without its account. |
| SCN-21 | Transaction on an unknown account | Mutation | add Transaction{transaction_id=T8,account_id=A999,transaction_amount=10.00,currency_code=INR,debit_credit_code=DEBIT,transaction_status_code=PENDING} | BR-28 | Reject | BR-28 | Reject | BR-28 | The account reference must resolve. |
| SCN-22 | Transaction with a zero amount | Mutation | add Transaction{transaction_id=T9,account_id=A800,transaction_amount=0,currency_code=INR,debit_credit_code=DEBIT,transaction_status_code=PENDING} | BR-29 | Reject | BR-29 | Reject | BR-29 | The amount is a positive magnitude. |
| SCN-23 | Posted transaction with no posting timestamp | Mutation | add Transaction{transaction_id=T10,account_id=A800,transaction_amount=10.00,currency_code=INR,debit_credit_code=DEBIT,transaction_status_code=POSTED} | BR-30 | Reject | BR-30 | Reject | BR-30 | A posted transaction must say when it was posted. |
| SCN-24 | Minor holder with no guardianship in force | Mutation | add AccountHolding{account_holding_id=H18,party_id=P104,account_id=A800,holder_role_code=JOINT_HOLDER,valid_from=2022-06-01} | BR-23 | Reject | BR-23 | Reject | BR-23 | The minor holds before guardianship G1 starts (provisional rule, open question OQ-01). |
| SCN-25 | Bundle cycle through two products | Mutation | add Product{product_id=PR5,product_code=BND_A,product_name=Bundle A,product_category_code=DEPOSIT,is_bundle_capable=true} + add Product{product_id=PR6,product_code=BND_B,product_name=Bundle B,product_category_code=DEPOSIT,is_bundle_capable=true} + add ProductBundleComponent{product_bundle_component_id=PBC4,bundle_product_id=PR5,component_product_id=PR6,component_quantity=1} + add ProductBundleComponent{product_bundle_component_id=PBC5,bundle_product_id=PR6,component_product_id=PR5,component_quantity=1} | BR-27 | Reject | BR-27 | Reject | BR-27 | Bundle A contains B and B contains A: an indirect cycle. |
| SCN-26 | Bundle that contains itself | Mutation | add ProductBundleComponent{product_bundle_component_id=PBC6,bundle_product_id=PR3,component_product_id=PR3,component_quantity=1} | BR-27 | Reject | BR-27 | Reject | BR-27 | A product never contains itself. |
| SCN-27 | Stand-alone product used as a bundle | Mutation | add ProductBundleComponent{product_bundle_component_id=PBC7,bundle_product_id=PR1,component_product_id=PR2,component_quantity=1} | BR-26 | Reject | BR-26 | Reject | BR-26 | Only bundle-capable products may contain components. |
| SCN-28 | Bundle component with a zero quantity | Mutation | add ProductBundleComponent{product_bundle_component_id=PBC8,bundle_product_id=PR3,component_product_id=PR1,component_quantity=0} | BR-25 | Reject | BR-25 | Reject | BR-25 | The component quantity must be greater than zero. |
| SCN-29 | Overlapping legal names | Mutation | add PartyName{party_name_id=N8,party_id=P101,legal_name=Mira Rao-Shah,valid_from=2023-01-01} | BR-05 | Reject | BR-05 | Reject | BR-05 | Two names of one Party are in force at the same time. |
| SCN-30 | Legal name record with no name | Mutation | set DAT-13.legal_name=null | BR-04 | Reject | BR-04 | Reject | BR-04 | A name record must state the name. |
| SCN-31 | Closed account with no closing date | Mutation | set DAT-39.closed_date=null | BR-14 | Reject | BR-14 | Reject | BR-14 | A closed account must say when it closed. |
| SCN-32 | Open account with a closing date | Mutation | set DAT-37.closed_date=2025-01-01 | BR-14 | Reject | BR-14 | Reject | BR-14 | Only a closed account has a closing date. |
| SCN-33 | Open account with no opening date | Mutation | set DAT-37.opened_date=null | BR-15 | Reject | BR-15 | Reject | BR-15 | An account that has left the pending status needs an opening date. |
| SCN-34 | Account status outside the governed list | Mutation | set DAT-37.account_status_code=DORMANT | BR-12 | Reject | BR-12 | Reject | BR-12 | DORMANT is not an allowed status; adding it is a governed change (see CH-01). |
| SCN-35 | Account naming an unknown branch | Mutation | set DAT-37.branch_id=B99 | BR-13 | Reject | BR-13 | Reject | BR-13 | A named branch must exist. |
| SCN-36 | Account with no holder | Mutation | add Account{account_id=A807,account_number=ACC807,product_id=PR1,account_status_code=PENDING,currency_code=INR} | BR-20 | Reject | BR-20 | Reject | BR-20 | Every account has at least one holding (provisional for pending accounts, OQ-02). |
| SCN-37 | Reversal of a transaction on another account | Mutation | add Transaction{transaction_id=T11,account_id=A803,transaction_amount=250.00,currency_code=INR,debit_credit_code=CREDIT,transaction_status_code=POSTED,posted_at_timestamp=2024-03-09T09:00:00,reverses_transaction_id=T1} | BR-32 | Reject | BR-32 | Reject | BR-32 | A reversal must stay on the same account as the original. |
| SCN-38 | Transaction in another currency than its account | Mutation | add Transaction{transaction_id=T12,account_id=A800,transaction_amount=10.00,currency_code=GBP,debit_credit_code=DEBIT,transaction_status_code=PENDING} | BR-31 | Reject | BR-31 | Reject | BR-31 | Provisional rule: currency must match the account (open question OQ-03). |
| SCN-39 | Source identifier mapped to two Parties | Mutation | add PartySourceIdentifier{party_source_identifier_id=S6,party_id=P102,source_system_code=CORE_BANKING,source_party_identifier=C9001} | BR-06 | Reject | BR-06 | Reject | BR-06 | C9001 in the core banking system already maps to P101. |
| SCN-40 | Customer status outside the governed list | Mutation | add CustomerRole{customer_role_id=R6,party_id=P104,customer_status_code=PROSPECT,valid_from=2023-01-01} | BR-07 | Reject | BR-07 | Reject | BR-07 | PROSPECT is a CRM concept and is not an enterprise customer status. |
| SCN-41 | Overlapping customer-role periods | Mutation | add CustomerRole{customer_role_id=R7,party_id=P101,customer_status_code=INACTIVE,valid_from=2021-01-01,valid_to=2022-01-01} | BR-08 | Reject | BR-08 | Reject | BR-08 | A Party cannot be in two customer-role periods at once. |
| SCN-42 | Address type outside the governed list | Mutation | add PartyAddress{party_address_id=PA3,party_id=P102,address_id=AD1,address_type_code=HOLIDAY,valid_from=2025-01-01} | BR-09 | Reject | BR-09 | Reject | BR-09 | HOLIDAY is not an allowed address type. |
| SCN-43 | Two residential addresses at once | Mutation | add PartyAddress{party_address_id=PA4,party_id=P101,address_id=AD2,address_type_code=RESIDENTIAL,valid_from=2023-01-01} | BR-10 | Reject | BR-10 | Reject | BR-10 | Provisional rule: one address per type at a time (open question OQ-04). |
| SCN-44 | Contact point of an unknown kind | Mutation | add ContactPoint{contact_point_id=CP2,party_id=P102,contact_type_code=FAX,contact_value_text=0000,is_verified=false} | BR-11 | Reject | BR-11 | Reject | BR-11 | FAX is not an allowed contact kind. |
| SCN-45 | Branch with an unknown status | Mutation | add Branch{branch_id=B03,branch_name=East Branch,branch_status_code=PLANNED} | BR-16 | Reject | BR-16 | Reject | BR-16 | PLANNED is not an allowed branch status. |
| SCN-46 | Guardianship with no evidence | Mutation | add Guardianship{guardianship_id=G2,guardian_party_id=P101,minor_party_id=P104,authority_type_code=CONSENT_ONLY,valid_from=2024-01-01} | BR-21 | Reject | BR-21 | Reject | BR-21 | Evidence for the authority is mandatory. |
| SCN-47 | A Party as its own guardian | Mutation | add Guardianship{guardianship_id=G3,guardian_party_id=P104,minor_party_id=P104,authority_type_code=TRANSACT,valid_from=2024-01-01,evidence_reference_text=Case file 119} | BR-22 | Reject | BR-22 | Reject | BR-22 | A Party is never its own guardian. |
| SCN-48 | Two products with one code | Mutation | add Product{product_id=PR7,product_code=DEP_STD,product_name=Duplicate Code,product_category_code=DEPOSIT,is_bundle_capable=false} | BR-24 | Reject | BR-24 | Reject | BR-24 | Product codes are unique. |
| SCN-49 | Legal name in force before the change | Query | asof PartyName where party_id=P101 date=2024-02-01 return legal_name | BR-05 | Mira Rao | n/a | Mira Rao | n/a | History lookup returns the name in force on the date. |
| SCN-50 | Legal name on the day of the change | Query | asof PartyName where party_id=P101 date=2024-03-01 return legal_name | BR-05 | Mira R. Rao | n/a | Mira R. Rao | n/a | The old interval is end-exclusive, so the new name applies on the change date. |
| SCN-51 | Holders of an account at a past date | Query | asof AccountHolding where account_id=A800 date=2021-01-01 return party_id | BR-17; BR-19 | P101,P102 | n/a | P101,P102 | n/a | Both holders were in force on the date. |
| SCN-52 | Holders before the account existed | Query | asof AccountHolding where account_id=A800 date=2019-01-01 return party_id | BR-17 | none | n/a | none | n/a | No holding was in force before the first start date. |

#### Traceability (requirement to rule to element to scenario)

| ID | Requirement | Rule | Logical element | Dictionary entry | Scenario |
| --- | --- | --- | --- | --- | --- |
| TR-01 | REQ-01 | BR-24 | Product.product_code | Product.product_code | SCN-48 |
| TR-02 | REQ-02 | BR-02 | Party.party_type_code | Party.party_type_code | SCN-13 |
| TR-03 | REQ-03 | BR-17 | AccountHolding.holder_role_code | AccountHolding.holder_role_code | SCN-16 |
| TR-04 | REQ-04 | BR-19 | AccountHolding.valid_from | AccountHolding.valid_from | SCN-19 |
| TR-05 | REQ-05 | BR-05 | PartyName.valid_from | PartyName.valid_from | SCN-29 |
| TR-06 | REQ-06 | BR-14 | Account.closed_date | Account.closed_date | SCN-31 |
| TR-07 | REQ-07 | BR-28 | Transaction.account_id | Transaction.account_id | SCN-20 |
| TR-08 | REQ-08 | BR-06 | PartySourceIdentifier.source_party_identifier | PartySourceIdentifier.source_party_identifier | SCN-39 |
| TR-09 | REQ-09 | BR-23 | Guardianship.authority_type_code | Guardianship.authority_type_code | SCN-24 |
| TR-10 | REQ-10 | BR-13 | Account.branch_id | Account.branch_id | SCN-35 |
| TR-11 | REQ-11 | BR-27 | ProductBundleComponent.component_product_id | ProductBundleComponent.component_product_id | SCN-25 |
| TR-12 | REQ-14 | BR-07 | CustomerRole.customer_status_code | CustomerRole.customer_status_code | SCN-40 |

**Recorded random traces** (author-run with `--trace`; not independently reviewed)

```text
Party.party_type_code <- BR-02 <- REQ-02: The model shall represent customers that are persons and cus...
Account.closed_date <- BR-14 <- REQ-06: The model shall retain closed accounts with their closing da...
Guardianship.authority_type_code <- BR-23 <- REQ-09: The model shall allow a minor to hold an account only under ...
REQ-09 -> BR-23 -> Guardianship.authority_type_code -> SCN-24
REQ-11 -> BR-27 -> ProductBundleComponent.component_product_id -> SCN-25
REQ-02 -> BR-02 -> Party.party_type_code -> SCN-13
```

#### Topic 8 review checklist (author self-review)

| ID | Review area | Result | Evidence or finding |
| --- | --- | --- | --- |
| RV-01 | Scope and traceability | Pass | Every logical entity maps to a conceptual element or a documented refinement (CLM); every requirement reaches a rule and a scenario (TR). |
| RV-02 | Entities | Pass | All 16 entities have non-circular definitions and a one-row grain statement. |
| RV-03 | Attributes | Pass | Every attribute has a domain, requiredness and a dictionary entry; the checker enforces coverage. |
| RV-04 | Keys | Pass | Every entity has a primary key that is a candidate key under its dependencies; alternate keys have uniqueness rules. |
| RV-05 | Relationships | Pass | Every relationship has both-direction phrases and cardinality; no many-to-many remains. |
| RV-06 | Constraints and rules | Pass | Every required attribute, foreign key, allowed-value list and alternate key is enforced by a rule; every enforceable rule has an invalid scenario. |
| RV-07 | Normalisation | Pass | All entities are in BCNF under their stated dependencies; the legacy decompositions are lossless and preserve dependencies. |
| RV-08 | Naming | Pass | The naming standard's patterns are applied to every entity and attribute and their examples behave as stated. |
| RV-09 | Dictionary | Pass | Coverage is 100% of entities and attributes; definitions pass the circularity check. |
| RV-10 | Assumptions and open questions | Pass | Eleven open questions have owners, statuses and provisional assumptions; provisional rules are labelled Open. |
| RV-11 | History and temporal meaning | Finding | Only valid time is modelled; record time is an open question (OQ-11), logged as FND-02. |
| RV-12 | Schema evolution | Pass | Seven anticipated changes are classified with a first action (CH-01 to CH-07). |
| RV-13 | Cross-model consistency | Pass | Homonyms are registered with context-specific definitions; no term has two meanings in one context. |
| RV-14 | Governance and approval | Finding | No independent review has happened; approval is not claimed (FND-05). |

#### Findings

| ID | Model element | Defect type | Severity | Impact | Correction | Owner | Acceptance test | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FND-01 | Person.birth_date | Semantic | Major | The minor-holder rule (BR-23) cannot be applied to a person whose date of birth is absent | Decide whether date of birth is mandatory for persons who hold accounts (OQ-07); until then treat a missing date as needing review | STK-07 | A holding for a person with no date of birth is rejected or routed to review | Open |
| FND-02 | Valid-interval entities | Semantic | Major | Only business validity is stored; the regulator may ask what the bank knew on a past date | Decide whether record time is required (OQ-11) and, if so, extend the history entities | STK-07 | A query for a past belief returns the value the bank held then | Open |
| FND-03 | CustomerRole.customer_status_code | Semantic | Major | Active customer has two meanings (finance and risk) so counts stay inconsistent until the status vocabulary is defined | Agree definitions for ACTIVE, INACTIVE and CLOSED with finance and risk (OQ-06) | STK-05 | Both functions derive the same count from the same data | Open |
| FND-04 | Address; ContactPoint | Documentation | Minor | No requirement or stakeholder statement supports these entities; their source is Unknown | Confirm the need with the retail domain expert or remove them from scope | STK-11 | Each entity cites a source or is removed | Open |
| FND-05 | Whole package | Documentation | Major | No independent review has taken place, so no approval can be claimed | Run the Topic 8 review with an independent reviewer (VL-06) | STK-12 | Blocking and major findings are closed and the approver records a decision | Open |
| FND-06 | BR-10; BR-20; BR-23; BR-31 | Semantic | Major | Four rules are provisional (BR-10, BR-23 and BR-31 are Open and BR-20 depends on OQ-02): scenarios pass under the assumption but no business decision backs them | Obtain decisions for OQ-01 to OQ-04 and update the rules and scenarios together | STK-11 | Each rule is Confirmed or removed, and its scenarios re-run | Open |
| FND-07 | Person.birth_date (draft name date_of_birth) | Naming | Minor | The draft attribute name violated the date naming rule (dates end in _date), found when the naming standard was applied to every attribute | Renamed to birth_date throughout the logical model, dictionary and rules | STK-13 | The checker applies the naming patterns to every attribute with no violation | Closed |
| FND-08 | Dictionary entries for 13 identifiers and descriptors | Documentation | Major | Thirteen draft definitions only restated the element name, which the circularity check rejects | Rewrote each definition to say what the element distinguishes, includes or excludes | STK-13 | The checker finds no circular or thin definition in 100% of entries | Closed |

#### Validation log

No independent review has taken place for this worked reference. The author's self-review used the checker and the
checklist above.

| ID | Subject | Reviewer role | Review method | Planned week | Recorded response | Status |
| --- | --- | --- | --- | --- | --- | --- |
| VL-01 | Glossary, synonyms and homonyms (GL, SY, HM) | STK-09; STK-02; STK-04 | Walk-through of each homonym with the context owner | 3 | Not yet recorded | Planned |
| VL-02 | Conceptual model and candidate decisions (CE, CR) | STK-11; STK-02 | Scenario walk-through of the conceptual model | 4 | Not yet recorded | Planned |
| VL-03 | Business rules (BR) and scenarios (SCN) | STK-11; STK-07 | Review each rule's valid and invalid example with a domain expert | 6 | Not yet recorded | Planned |
| VL-04 | Logical model, keys and normalisation (LE, AT, KY, FD) | STK-08; STK-12 | Dependency and decomposition review | 6 | Not yet recorded | Planned |
| VL-05 | Naming standard and dictionary (NS, DD) | STK-09; STK-12 | Sample audit of 20% of dictionary entries | 7 | Not yet recorded | Planned |
| VL-06 | Whole package against the Topic 8 checklist | STK-12 | Independent review; blocking and major findings must close | 8 | Not yet recorded | Planned |

### 6.14 D14 — Final project summary (Step 19)

**Northbridge Bank — Enterprise conceptual and logical data model. Version 1.1, 2026-10-21. ILLUSTRATIVE.**

**Scope.** Customer, account and transaction data for four processes: onboarding, account opening and holding,
product subscription (accounts only) and transaction posting. Physical design, loan servicing, card authorisation,
marketing, security implementation, ETL and reporting are excluded.

**The model.** Eleven business concepts (Party with Person and Organisation, Legal Name, Customer Role, Account,
Product, Branch, Transaction, Address and Contact Point) and thirteen conceptual relationships became sixteen logical
entities with seventy-eight attributes and eighteen relationships. Four many-to-many relationships are resolved
by associative entities that carry the relationship's own facts: account holding, party address, guardianship and
product bundle component.

**Key decisions.** Customer is a role with its own period, not a subtype of Party (MD-01); joint holdings are
modelled by an associative entity with role and period (MD-02); legal names are kept with valid intervals (MD-03); a
governed Party identifier is mapped to source identifiers (MD-04); and every valid period is start-inclusive and
end-exclusive (MD-07).

**Evidence.** Thirty-two rules, all executable, with 52 scenarios: 37 invalid cases are rejected for the stated rule and
11 valid cases are accepted. All sixteen entities are in BCNF; two legacy relations decompose losslessly with
dependencies preserved. The dictionary covers every entity and attribute.

**Open items and risks.** Eleven open questions remain, notably whether a minor may hold alone (OQ-01), what "active
customer" means (OQ-06) and whether record time is required (OQ-11). Four rules are provisional (FND-06). No independent
review has taken place (FND-05).

**Deferred physical decisions.** Twelve decisions, including platform, data types, identifier generation, indexing,
partitioning, referential enforcement and masking, go to modules 2D.5 to 2D.7 and 2D.10 (DF-01 to DF-12).

**Caveats and limits.** Every definition, rule and number is illustrative; nobody has confirmed any rule. Scenarios
prove that the model behaves as its rules say, not that the rules are right. Interval and naming conventions are
assumptions that need confirmation.

---


## 7. Validation and quality assurance

### 7.1 Quality criteria and how each is verified

| Check | How to verify | Automated? |
| --- | --- | --- |
| Models align with scope and requirements | Each requirement reaches a rule, an element and a scenario; each element traces to a requirement or a documented refinement | Yes |
| Entity definitions meaningful and unambiguous | Two reviewers independently classify ten sample instances the same way | No (Step 10, Step 16) |
| Definitions are not circular | A definition must carry at least four distinctive words beyond the name and its entity | Yes |
| Relationships and cardinalities reflect business rules | Both-direction phrases, minimum and maximum, a rule and a scenario for each relationship | Yes |
| Keys and constraints support identification and integrity | Every entity has a primary key that is a candidate key; every required attribute, foreign key, allowed-value list and alternate key is enforced by a rule | Yes |
| Normalisation justified | Dependencies, candidate keys, normal forms, lossless-join and dependency-preservation checks | Yes |
| Conceptual and logical models consistent | Every conceptual element maps forward; every logical element maps back or is a documented refinement; the conceptual model contains no physical terms | Yes |
| Naming and definitions consistent | Naming patterns applied to every name; glossary has no duplicate term in a context; synonym and homonym registers resolve | Yes |
| Assumptions and open questions documented | Each has an owner and a status; provisional rules are labelled `Open` | Partly |
| Scenarios can be expressed | At least 20 scenarios, at least 8 invalid, all with explained outcomes; the base data violates no rule | Yes |
| Stakeholder review findings addressed | Each finding resolved or recorded as accepted or deferred with a reason | No |

### 7.2 Running the checker

Extract Appendix B to `check_data_model.py`, then run from the repository root:

```bash
python3 check_data_model.py "Stage 2D — Data Architecture/04-Conceptual-Logical-and-Physical-Data-Modeling/Projects/04-enterprise-conceptual-and-logical-data-model.md"
python3 check_data_model.py FILE --derive
python3 check_data_model.py FILE --trace 3 --seed 2026
```

The checker exits `0` when every check passes and `1` otherwise. `--derive` prints the recomputed scenario outcomes and
normal forms. **Try breaking a rule:** change a spec in 6.5 (for example, delete the `no_overlap` item of BR-19) and
run the checker; the scenarios that depended on the rule now disagree with their expectations, and the checker
reports which ones. In Mode B, keep the table header names or adapt the `KINDS` mapping at the top of the script.

### 7.3 What the checker verifies

- **Structure:** unique IDs, no empty cells, valid evidence labels, every ID reference resolves to a defined item.
- **Language:** glossary terms are unique per context; synonyms resolve to glossary terms; homonyms have distinct definitions in at least two contexts; every logical entity has a glossary term; definitions are not circular.
- **Conceptual model:** the diagram shows exactly the accepted candidates; relationships have both-direction phrases and valid cardinalities; no physical or platform term appears.
- **Mapping:** every conceptual element maps to logical elements and every logical element maps back or is a documented refinement.
- **Logical model:** every entity has a primary key made of its own attributes; identifiers are required; each foreign key references a key, has a relationship definition and agrees with the relationship's minimum participation; no many-to-many remains.
- **Naming:** every pattern compiles, behaves as its examples state, and holds for every entity and attribute; foreign keys end with the referenced key name.
- **Dictionary:** exact coverage of entities and attributes, with no extra entries; each definition carries enough distinct content.
- **Rules:** each spec parses and uses real attributes; every required attribute, foreign key, allowed-value list and alternate key is covered by a rule; every confirmed rule has a valid and an invalid scenario; every enforceable rule has an invalid scenario.
- **Execution:** the base dataset violates no rule; every scenario's observed outcome and violated rules are recomputed and must equal the expected ones.
- **Normalisation:** candidate keys and normal forms are recomputed from the dependencies; the declared keys are candidate keys; every entity is in BCNF; decompositions are lossless; leaves are in BCNF; dependencies are preserved.
- **Traceability:** every requirement is satisfied by something that exists; rule-based requirements have a trace row to an element, a dictionary entry and a scenario.

### 7.4 Critical-error list (self-review)

| Critical error | How this package guards against it |
| --- | --- |
| A definition restates the name | Circularity check on every glossary, candidate and dictionary entry |
| A physical term appears in the conceptual model | Term scan over the conceptual tables and diagram |
| A relationship lacks one direction or a minimum | Both phrases and cardinality required; participation agrees with the foreign key |
| A many-to-many is left unresolved | A foreign key cannot allow many parents; associative entities are used and mapped |
| A rule exists only in prose | Every rule has a spec; every structural declaration is covered by a rule |
| A rule has no invalid test | Checker requires an invalid scenario for each enforceable rule |
| The base data hides a rule violation | The base dataset is checked against every rule before scenarios run |
| An unconfirmed rule is presented as confirmed | Status vocabulary; four provisional rules are labelled and logged as FND-06 |
| Naming rules that nothing checks | Patterns are applied to every name, and their examples are self-tested |
| Normal form asserted without a proof | Candidate keys and normal forms are recomputed; decompositions are checked |
| A physical decision slips in | Deferred decisions are listed (DF-01 to DF-12); the conceptual scan blocks platform terms |

### 7.5 Project completion gate (roadmap Section 7.7) and worked-reference status

| Gate item | Mode A status (Northbridge worked reference) | Mode B requirement |
| --- | --- | --- |
| D1–D14 exist, version-dated, consistent IDs | Met: Section 6, version 1.1, checker passes | Met for your own set |
| Conceptual model: non-circular definitions, named relationships, no data types or platform terms | Met: enforced by the checker | Met |
| Logical model: identifiers; both-direction cardinality and optionality; many-to-many resolved; no unexplained redundancy | Met: enforced by the checker; no redundancy recorded | Met |
| Business rules: source, representation, valid and invalid test; assumed and open rules labelled | Met for all 32 rules; four are provisional | Met |
| Data dictionary: 100% of entities and attributes; sample without circular or empty definitions | Met for 100% (94 of 94), checked automatically | Met, plus a human sample audit |
| Validation evidence: at least 20 scenarios with explained outcomes | Met: 52 scenarios executed; **not confirmed by a stakeholder** | Required |
| Traceability: random trace of three elements back and three requirements forward | Met by the checker; **not witnessed by a reviewer** | Required |
| Consistency: conceptual and logical models differ only by documented refinement | Met: mapping CLM, enforced | Met |
| Final review: independent reviewer completes the Topic 8 checklist; blocking and major findings resolved | **Not met by design** (FND-05); the author's self-review is in 6.13 | Required |
| Deferred decisions: physical decisions listed, not made | Met: DF-01 to DF-12 | Met |

**Readiness decision (module checklist).** *Not yet ready* in the module's terms, because the package cannot yet be independently reviewed. There are no blocking defects; four major findings are open with owners (FND-01, FND-02, FND-03, FND-05) and one more major finding concerns provisional rules (FND-06). A reviewer could rate it *conditionally ready* once owners and remediation dates are approved.

### 7.6 Anticipated reviewer challenges (author-prepared, not recorded reviewer objections)

| Challenge | Answer using recorded evidence |
| --- | --- |
| "Why is customer a role and not a subtype of Party? Subtypes are simpler." | A Party can leave and later return as a customer (MD-01); the model allows two separate periods (SCN-11) and refuses overlapping ones (SCN-41). A subtype would force one lifetime row per Party. The enterprise Customer is also distinct from the CRM contact, the retail account holder and the cardholder (HM-01). |
| "A minor rule is in the model although the business has not decided." | It is labelled `Open` (BR-23), its scenarios say they run under a provisional assumption (SCN-24), and the question is logged with an owner (OQ-01, FND-06). The scenario that accepts a guarded minor (SCN-06) and the one that rejects an unguarded one show the effect of the choice, so the decision can be taken with evidence. |
| "Storing legal-name history is over-engineering; put the name on the transaction." | The regulator asks for the name in force on a past date (INT-05). A name stored once per Party cannot answer an as-of question; a snapshot on every transaction duplicates a fact (MD-03). The history queries show the boundary day returning the new name (SCN-50). |

---

## 8. Templates and guides for a real organisation (Mode B)

Placeholders use the form `XXX-nn`; replace them with real IDs.

### 8.1 Row templates

**Candidate entity**

| ID | Candidate entity | Decision | Business definition | Business purpose | Source | Key relationships | Ownership | Open questions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CE-nn | name | Accept / Relationship / Refinement / Reject / Open | what it is, with inclusions and exclusions | why it is tracked | interview or document ID | related concepts | owner or Unknown | OQ-nn | evidence label |

**Business rule** (write the sentence first, then the spec)

| ID | Rule text | Source | Representation | Spec | Valid example | Invalid example | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BR-nn | one testable sentence | INT-nn or REQ-nn | Structure / Constraint / Procedure | a spec from Section 6.5 | an accepted case | a rejected case | Confirmed / Assumed / Open | evidence label |

**Scenario**

| ID | Scenario | Kind | Operations | Rule reference | Expected outcome | Expected rules | Observed outcome | Observed rules | Explanation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SCN-nn | what is tried | Mutation / Query | add, set or remove operations | BR-nn | Accept / Reject | BR-nn or none | filled by the checker | filled by the checker | why |

**Review finding**

| ID | Model element | Defect type | Severity | Impact | Correction | Owner | Acceptance test | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FND-nn | location | Semantic / Structural / Naming / Documentation | Blocking / Major / Minor | why it matters | what to change | role | how closure is shown | Open / Closed |

### 8.2 Domain-expert interview guide

| Topic | Questions that produce rules |
| --- | --- |
| Identity | What identifies a person or organisation, and does it ever change or repeat across systems? |
| Roles | Can the same party be a customer, a guardian and a contact? When does each role start and end? |
| Accounts | Who can hold an account, in which roles, and what happens when a holder leaves? |
| History | Which facts must be recoverable for a past date, and which date counts: when it was true or when we learned it? |
| Closure | What is kept when something closes, and for how long? |
| Meaning | When two teams use the same word, what does each mean? |

Always ask: *Can you give me an example that must be accepted and one that must be rejected?*

### 8.3 Pre-review checklist

- Scope, exclusions and level are stated; no physical decision is made.
- Every term has one meaning per context; homonyms and synonyms are registered.
- Every conceptual element maps forward; every logical element maps back or is a documented refinement.
- Every rule has a source, a spec and valid and invalid scenarios; open rules are labelled.
- Every entity has a grain statement, a key and a dictionary entry; names follow the standard.
- Dependencies, candidate keys and normal forms are computed; any denormalisation is recorded.
- Open questions have owners; deferred decisions are listed; the checker passes.

---

## 9. Common pitfalls and project risks

| Pitfall | Why it harms | Prevention |
| --- | --- | --- |
| Naming entities after system tables | Copies old structure and old errors | Define entities from the business view |
| One universal Customer | Merges unlike meanings | Contexts, homonym register, customer role |
| Putting a role on the Party | The same Party plays several roles over time | Model roles as relationships or role entities |
| A foreign key where a many-to-many exists | Joint holders cannot be represented | Associative entity with its own attributes |
| Using a mutable value as an identifier | References break on change | Governed identifier, source identifiers mapped |
| Current state only | The past cannot be recovered | Valid intervals and an as-of query |
| Definitions that restate the name | The dictionary adds no information | Circularity check; write what it includes and excludes |
| Rules only in prose | They are not testable | Spec plus valid and invalid scenarios |
| Inventing a rule to fill a gap | Hides a business decision | Mark `Assumed` or `Open`; ask the owner |
| Data types and indexes in the logical model | Technology leaks into meaning | Logical domains only; list physical decisions as deferred |
| Normal form asserted from sample data | Samples do not prove dependencies | State dependencies from rules; compute keys |
| Approval by silence | No accountability | Independent review with recorded findings |

**Project-level risks**

| Risk | Early sign | Response |
| --- | --- | --- |
| Domain expert unavailable | Rules stay `Open` | Log the question with an owner; do not assume silently |
| Scope creep into design | Types, indexes or tables appear | Move them to the deferred list |
| Model and dictionary drift | The diagram and the dictionary disagree | One source of truth; run the checker before each release |
| Rules multiply without tests | Rules lack invalid scenarios | The checker blocks it |

---

## 10. Connection to subsequent modules

The package is a **logical baseline**, not a physical design.

| Later module | Reusable inputs from this project | Decisions that belong to that module |
| --- | --- | --- |
| 2D.5 Database and storage architecture | Logical model, keys, constraints, grain statements, volume-relevant entities (Transaction, history entities) | Engine, data types, indexing, partitioning, storage format, physical denormalisation (DF-01 to DF-09) |
| 2D.6 Data integration and interoperability | Glossary, identifiers, source-identifier mapping, relationship rules | Interfaces, mappings, change-data-capture and batch choices (DF-12) |
| 2D.7 Enterprise data platform and lakehouse | Entity scope, bounded contexts | Layers, zones, platform components (DF-11) |
| Dimensional and historical modeling (2D.5 to 2D.7, 2D.14) | Needs NE-01 to NE-08, identifiers, relationships | Fact grain, dimensional design, vault structures |
| 2D.10 and 2D.11 Governance, metadata, lineage | Glossary, dictionary, authority gaps (AU) | Classification, policy, lineage tooling, stewardship model (DF-10) |
| 2D.15 Schema evolution and reviews | Naming standard, compatibility questions (CH), review findings | Change governance, review board process |

**Open questions to carry into module 2D.5:** OQ-01 to OQ-11 (notably OQ-06 and OQ-11), the provisional rules
BR-10, BR-20, BR-23 and BR-31, and the deferred decisions DF-01 to DF-12.

---

## 11. Self-assessment rubric

Score each criterion 0 (absent), 1 (partial) or 2 (complete). Pass requires at least 90% of the maximum and no zero.

| # | Criterion | Evidence |
| --- | --- | --- |
| 1 | Scope names exclusions and level; no physical decision is made | D1, DF |
| 2 | Consumers have stated uses; statements are recorded verbatim before interpretation | D2 |
| 3 | Terms have one meaning per context; homonyms and synonyms are registered | D3, checker |
| 4 | Candidates are accepted or rejected with definitions free of circularity | D4, checker |
| 5 | Every rule has a source, a spec and valid and invalid scenarios; open rules are labelled | D5, checker |
| 6 | The conceptual model has no data types or platform terms and is readable by the business | D6, checker |
| 7 | Every logical entity has a key, a grain statement and resolved relationships | D7, D8, checker |
| 8 | Keys and integrity are defined and enforced by rules | D9, checker |
| 9 | Dependencies, keys, normal forms and decompositions are computed and justified | D9, checker |
| 10 | Needs, anticipated changes, open questions and deferred decisions are visible | D10 |
| 11 | The naming standard is testable and applied to every name | D11, checker |
| 12 | The dictionary covers every element with non-circular definitions | D12, checker |
| 13 | At least 20 scenarios, at least 8 invalid, run with explained outcomes | D13, checker |
| 14 | Traceability works in both directions | D13, checker |
| 15 | Findings have type, severity, owner and acceptance test | D13 |
| 16 | The summary states decisions, open items, deferred items and limits | D14 |
| 17 | An independent reviewer completes the Topic 8 checklist | Reviewer note |

---

## Appendix A — Glossary of modeling terms

| Term | Meaning in this project |
| --- | --- |
| Associative entity | An entity that resolves a many-to-many relationship and carries the relationship's own attributes |
| Candidate key | A minimal set of attributes that determines every attribute of an entity |
| Cardinality | The minimum and maximum number of related instances in one direction |
| Functional dependency | A statement that the values of some attributes determine the values of others |
| Grain statement | One sentence saying what one row of an entity represents |
| Lossless decomposition | A split of a relation whose parts can be joined back without gaining or losing rows |
| Optionality | Whether a relationship or attribute must be present (minimum one) or may be absent (minimum zero) |
| Valid interval | The period during which a fact was true in the business, start-inclusive and end-exclusive |

---

## Appendix B — Model checker and scenario runner (`check_data_model.py`)

Python 3.9 or later; standard library only. It reads the Markdown tables in this file, validates the model, loads the
test data, and runs every rule and scenario.

```python
#!/usr/bin/env python3
"""Consistency checker and executable validator for the enterprise conceptual and logical
data model package (D1-D14).

Usage:
    python3 check_data_model.py FILE
    python3 check_data_model.py FILE --derive
    python3 check_data_model.py FILE --trace 3 --seed 2026

Exit code 0 means every check passed; 1 means at least one error.
`--derive` prints the recomputed derived cells (scenario outcomes, candidate keys, normal forms).
"""
import argparse
import ast
import itertools
import random
import re
import sys
from pathlib import Path

ID_CELL = re.compile(r"^[A-Z]{2,4}-\d{2,3}$")
PREFIXES = ("STK|CM|INT|REQ|PRC|BCX|GL|SY|HM|CE|AU|BR|CR|CLM|LE|AT|KY|RL|FD|LR|DP|NF|MD|OQ|ASM|NE|"
            "DF|CH|NS|DD|DAT|SCN|RV|FND|TR|VL")
ID_ANY = re.compile(rf"\b(?:{PREFIXES})-\d{{2,3}}\b")
SEPARATOR = re.compile(r"^:?-{3,}:?$")
EVIDENCE = {"Verified fact", "Stakeholder statement", "Illustrative assumption", "Inference",
            "Open question"}
RULE_STATUS = {"Confirmed", "Assumed", "Open"}
SEVERITY = {"Blocking", "Major", "Minor"}
DEFECT_TYPES = {"Semantic", "Structural", "Naming", "Documentation"}
DOMAINS = {"Identifier", "Code", "Text", "Date", "Timestamp", "Amount", "Quantity", "Flag"}
CARD = re.compile(r"^(0|1)\.\.(1|\*)$|^1$")
PHYSICAL_TERMS = re.compile(
    r"\b(varchar|bigint|integer|numeric\(|decimal\(|boolean type|index|indexes|partition|partitioned|"
    r"tablespace|ddl|postgres(?:ql)?|mysql|oracle|sql server|snowflake|bigquery|redshift|"
    r"databricks|parquet|clustered|b-tree|shard|primary key constraint)\b", re.I)
STOP = set("a an the of or and to in on for by with as is are be that this which its it at from "
           "into per each any one not no than who whose when where also may can must does do".split())

KINDS = {
    "Stakeholder (role)": "STK", "Model use": "CM", "Verbatim statement (hypothetical)": "INT",
    "Requirement statement": "REQ", "Business process": "PRC", "Bounded context": "BCX",
    "Glossary term": "GL", "Preferred term": "SY", "Homonym": "HM", "Candidate entity": "CE",
    "Authoritative source": "AU", "Rule text": "BR", "Relationship phrase (A to B)": "CR",
    "Logical element(s)": "CLM", "Grain statement": "LE", "Logical domain": "AT",
    "Key kind": "KY", "Parent entity": "RL", "Determinant": "FD", "Relation attributes": "LR",
    "Common attributes": "DP", "Candidate keys": "NF", "Alternatives considered": "MD",
    "Open question": "OQ", "Assumption": "ASM", "Need type": "NE", "Deferred decision": "DF",
    "Change scenario": "CH", "Naming rule": "NS", "Technical description": "DD",
    "Attributes (key=value)": "DAT", "Operations": "SCN", "Review area": "RV",
    "Defect type": "FND", "Logical element": "TR", "Planned week": "VL",
}
NEEDS_LABEL = {"STK", "CM", "INT", "REQ", "PRC", "BCX", "GL", "CE", "AU", "BR", "ASM", "DD"}


# ----------------------------------------------------------------------------- parsing
def refs(cell):
    return ID_ANY.findall(cell)


def parse(text):
    tables = {kind: {} for kind in set(KINDS.values())}
    errors, prose, diagrams = [], [], {}
    in_fence, fence, prev, header = False, [], None, None
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_fence and fence and re.match(r"D\d+-DIAGRAM", fence[0]):
                diagrams[fence[0].split()[0]] = "\n".join(fence)
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
            errors.append(f"line {number}: {cells[0]} has {len(cells)} cells, expected {len(header)}")
            continue
        row = dict(zip(header, cells))
        row["_line"] = number
        if cells[0] in tables[kind]:
            errors.append(f"line {number}: duplicate ID {cells[0]}")
        tables[kind][cells[0]] = row
    return tables, "\n".join(prose), diagrams, errors


def split_list(cell):
    return [x.strip() for x in cell.split(",") if x.strip() and x.strip() not in ("none", "n/a")]


def words(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower().replace("_", " "))]


# ----------------------------------------------------------------------------- expression language
class Row(dict):
    pass


def parse_value(text):
    t = text.strip()
    if t == "null":
        return None
    if t in ("true", "false"):
        return t == "true"
    if re.fullmatch(r"-?\d+(\.\d+)?", t):
        return float(t)
    return t


def age_years(dob, ref):
    if dob is None or ref is None:
        return None
    y1, m1, d1 = (int(x) for x in str(dob)[:10].split("-"))
    y2, m2, d2 = (int(x) for x in str(ref)[:10].split("-"))
    return y2 - y1 - ((m2, d2) < (m1, d1))


def tri_and(values):
    if any(v is False for v in values):
        return False
    return None if any(v is None for v in values) else True


def tri_or(values):
    if any(v is True for v in values):
        return True
    return None if any(v is None for v in values) else False


def compile_expr(expr):
    e = expr.strip()
    e = re.sub(r"([A-Za-z_][\w\.]*) is not null", r"notnull(\1)", e)
    e = re.sub(r"([A-Za-z_][\w\.]*) is null", r"isnull(\1)", e)
    e = e.replace("<>", "!=")
    e = re.sub(r"(?<![<>!=])=(?!=)", "==", e)
    return ast.parse(e, mode="eval")


def eval_expr(tree, env):
    """Three-valued evaluation. env maps names/aliases to dict rows or values."""
    def lookup(node):
        if isinstance(node, ast.Name):
            if node.id in env and not isinstance(env[node.id], dict):
                return env[node.id]
            for row in env.values():
                if isinstance(row, dict) and node.id in row:
                    return row[node.id]
            if node.id in ("true", "false"):
                return node.id == "true"
            return None  # attribute absent from the row; names are validated separately
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            return env[node.value.id].get(node.attr)
        raise ValueError("bad reference")

    def go(node):
        if isinstance(node, ast.Expression):
            return go(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, (ast.Name, ast.Attribute)):
            return lookup(node)
        if isinstance(node, ast.Tuple):
            return tuple(go(x) for x in node.elts)
        if isinstance(node, ast.BoolOp):
            vals = [go(v) for v in node.values]
            return tri_and(vals) if isinstance(node.op, ast.And) else tri_or(vals)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            v = go(node.operand)
            return None if v is None else (not v)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            v = go(node.operand)
            return None if v is None else -v
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            args = [go(a) for a in node.args]
            if node.func.id == "isnull":
                return args[0] is None
            if node.func.id == "notnull":
                return args[0] is not None
            if node.func.id == "age_years":
                return age_years(*args)
            raise ValueError("unknown function")
        if isinstance(node, ast.Compare):
            left = go(node.left)
            result = True
            for op, comp in zip(node.ops, node.comparators):
                right = go(comp)
                if isinstance(op, (ast.In, ast.NotIn)):
                    if left is None:
                        return None
                    ok = left in right
                    ok = ok if isinstance(op, ast.In) else not ok
                else:
                    if left is None or right is None:
                        return None
                    try:
                        ok = {ast.Eq: left == right, ast.NotEq: left != right, ast.Lt: left < right,
                              ast.LtE: left <= right, ast.Gt: left > right,
                              ast.GtE: left >= right}[type(op)]
                    except TypeError:
                        return None
                result = result and ok
                left = right
            return result
        raise ValueError(f"unsupported expression node {type(node).__name__}")
    return go(tree)


# ----------------------------------------------------------------------------- model
class Model:
    def __init__(self, t):
        self.t = t
        self.entities = {r["Entity"]: lid for lid, r in t["LE"].items()}
        self.attrs = {}
        for aid, r in t["AT"].items():
            self.attrs.setdefault(r["Entity"], []).append(r)
        self.pk = {}
        self.alt = {}
        self.fk = []
        for kid, k in t["KY"].items():
            cols = split_list(k["Attributes"])
            if k["Key kind"] == "Primary":
                self.pk[k["Entity"]] = cols
            elif k["Key kind"] == "Alternate":
                self.alt.setdefault(k["Entity"], []).append(cols)
            elif k["Key kind"] == "Foreign":
                self.fk.append((k["Entity"], cols[0], k["References"]))

    def attr_names(self, entity):
        return [a["Attribute"] for a in self.attrs.get(entity, [])]

    def allowed(self, entity, attr):
        for a in self.attrs.get(entity, []):
            if a["Attribute"] == attr:
                return split_list(a["Allowed values"])
        return []


def load_dataset(t):
    data = {}
    for did, r in t["DAT"].items():
        row = {"_id": did}
        for part in r["Attributes (key=value)"].split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
                row[k.strip()] = parse_value(v)
        data.setdefault(r["Entity"], []).append(row)
    return data


def apply_operations(t, data, ops_text):
    data = {e: [dict(r) for r in rows] for e, rows in data.items()}
    for op in [o.strip() for o in ops_text.split(" + ")]:
        if not op or op == "none":
            continue
        m = re.match(r"add (\w+)\{(.*)\}$", op)
        if m:
            row = {"_id": "new"}
            for part in m.group(2).split(","):
                k, v = part.split("=", 1)
                row[k.strip()] = parse_value(v)
            data.setdefault(m.group(1), []).append(row)
            continue
        m = re.match(r"set (DAT-\d+)\.(\w+)=(.*)$", op)
        if m:
            for rows in data.values():
                for r in rows:
                    if r["_id"] == m.group(1):
                        r[m.group(2)] = parse_value(m.group(3))
            continue
        m = re.match(r"remove (DAT-\d+)$", op)
        if m:
            for e in data:
                data[e] = [r for r in data[e] if r["_id"] != m.group(1)]
            continue
        raise ValueError(f"bad operation: {op}")
    return data


def interval_overlap(a, b):
    f1, t1, f2, t2 = a[0], a[1], b[0], b[1]
    inf = "9999-12-31"
    return f1 < (t2 or inf) and f2 < (t1 or inf)


def run_rule_items(model, data, spec):
    """Return a list of violation messages for one BR spec string."""
    out = []
    for item in [s.strip() for s in spec.split(" & ") if s.strip()]:
        m = re.match(r"^(\w+)\((.*)\)$", item, re.S)
        if not m:
            raise ValueError(f"bad spec item: {item}")
        name, args = m.group(1), m.group(2).strip()
        if name == "key":
            for entity in model.entities:
                pk = model.pk[entity]
                seen = set()
                for r in data.get(entity, []):
                    vals = tuple(r.get(c) for c in pk)
                    if None in vals:
                        out.append(f"{entity}: missing identifier")
                    elif vals in seen:
                        out.append(f"{entity}: duplicate identifier {vals}")
                    seen.add(vals)
        elif name == "required":
            for ref in split_list(args):
                e, a = ref.split(".")
                for r in data.get(e, []):
                    if r.get(a) is None:
                        out.append(f"{ref} is missing")
        elif name == "unique":
            e, cols = args.split(":")
            cols = split_list(cols)
            seen = set()
            for r in data.get(e.strip(), []):
                vals = tuple(r.get(c) for c in cols)
                if None in vals:
                    continue
                if vals in seen:
                    out.append(f"{e.strip()}: duplicate {vals}")
                seen.add(vals)
        elif name == "fk":
            for pair in split_list(args):
                src, dst = [x.strip() for x in pair.split("->")]
                se, sa = src.split(".")
                de, da = dst.split(".")
                targets = {r.get(da) for r in data.get(de, [])}
                for r in data.get(se, []):
                    if r.get(sa) is not None and r.get(sa) not in targets:
                        out.append(f"{src}={r.get(sa)} has no {dst}")
        elif name == "domain":
            for ref in split_list(args):
                e, a = ref.split(".")
                allowed = model.allowed(e, a)
                for r in data.get(e, []):
                    if r.get(a) is not None and str(r.get(a)) not in allowed:
                        out.append(f"{ref}={r.get(a)} not allowed")
        elif name == "check":
            e, expr = args.split(":", 1)
            tree = compile_expr(expr)
            for r in data.get(e.strip(), []):
                if eval_expr(tree, {"row": r}) is False:
                    out.append(f"{e.strip()} row violates {expr.strip()}")
        elif name == "no_overlap":
            m2 = re.match(r"(\w+) by ([\w, ]+) from (\w+) to (\w+)", args)
            e, keys, f, to = m2.group(1), split_list(m2.group(2)), m2.group(3), m2.group(4)
            groups = {}
            for r in data.get(e, []):
                if r.get(f) is None:
                    continue
                groups.setdefault(tuple(r.get(k) for k in keys), []).append((r[f], r.get(to)))
            for key, spans in groups.items():
                for a, b in itertools.combinations(spans, 2):
                    if interval_overlap(a, b):
                        out.append(f"{e} {key}: overlapping intervals")
        elif name == "acyclic":
            e, rest = args.split(":", 1)
            parent, child = [x.strip() for x in rest.split("->")]
            graph = {}
            for r in data.get(e.strip(), []):
                graph.setdefault(r.get(parent), set()).add(r.get(child))
            state = {}

            def visit(n):
                state[n] = 1
                for nxt in graph.get(n, ()):
                    if state.get(nxt) == 1 or (state.get(nxt) is None and visit(nxt)):
                        return True
                state[n] = 2
                return False
            if any(state.get(n) is None and visit(n) for n in list(graph)):
                out.append(f"{e.strip()}: cycle")
        elif name == "min_children":
            m2 = re.match(r"(\w+)\.(\w+) <- (\w+)\.(\w+) >= (\d+)(?: where (.*))?$", args)
            pe, pk, ce, cfk, n, where = m2.groups()
            tree = compile_expr(where) if where else None
            for pr in data.get(pe, []):
                if tree is not None and eval_expr(tree, {"row": pr}) is not True:
                    continue
                count = sum(1 for c in data.get(ce, []) if c.get(cfk) == pr.get(pk))
                if count < int(n):
                    out.append(f"{pe} {pr.get(pk)} has {count} {ce}")
        elif name in ("forbid", "require_exists"):
            secs = {}
            for s in args.split(";"):
                s = s.strip()
                if s.startswith("a="):
                    secs["a"] = s[2:]
                elif s.startswith("join "):
                    mj = re.match(r"join (\w+)=(\w+) on (.*)$", s)
                    secs["join"] = (mj.group(1), mj.group(2), compile_expr(mj.group(3)))
                elif s.startswith("where "):
                    secs["where"] = compile_expr(s[6:])
                elif s.startswith("when "):
                    secs["when"] = compile_expr(s[5:])
                elif s.startswith("exists "):
                    me = re.match(r"exists (\w+)=(\w+) where (.*)$", s)
                    secs["exists"] = (me.group(1), me.group(2), compile_expr(me.group(3)))
            for ra in data.get(secs["a"].split()[0], []):
                combos = [{"a": ra}]
                if "join" in secs:
                    alias, ent, on = secs["join"]
                    combos = [{"a": ra, alias: rb} for rb in data.get(ent, [])
                              if eval_expr(on, {"a": ra, alias: rb}) is True]
                for env in combos:
                    if name == "forbid":
                        if eval_expr(secs["where"], env) is True:
                            out.append(f"{secs['a']} row matches forbidden condition")
                    else:
                        if eval_expr(secs["when"], env) is not True:
                            continue
                        alias, ent, cond = secs["exists"]
                        if not any(eval_expr(cond, {**env, alias: rc}) is True for rc in data.get(ent, [])):
                            out.append(f"{secs['a']} row lacks required {ent}")
        else:
            raise ValueError(f"unknown spec {name}")
    return out


def spec_problems(model, spec):
    """Check that every attribute name used inside a spec exists on its entity."""
    problems = []
    for item in [s.strip() for s in spec.split(" & ") if s.strip()]:
        m = re.match(r"^(\w+)\((.*)\)$", item, re.S)
        name, args = m.group(1), m.group(2).strip()

        def names(expr, aliases):
            tree = compile_expr(expr)
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                    ent = aliases.get(node.value.id)
                    if ent is None or node.attr not in model.attr_names(ent):
                        problems.append(f"{node.value.id}.{node.attr}")
                elif isinstance(node, ast.Name) and node.id not in ("true", "false", "isnull", "notnull", "age_years") \
                        and node.id not in aliases and "" in aliases:
                    if node.id not in model.attr_names(aliases[""]):
                        problems.append(node.id)
        if name == "check":
            e, expr = args.split(":", 1)
            names(expr, {"": e.strip()})
        elif name == "min_children":
            m2 = re.match(r"(\w+)\.(\w+) <- (\w+)\.(\w+) >= (\d+)(?: where (.*))?$", args)
            if m2.group(6):
                names(m2.group(6), {"": m2.group(1)})
        elif name in ("forbid", "require_exists"):
            aliases, ents = {}, {}
            for s in args.split(";"):
                s = s.strip()
                if s.startswith("a="):
                    aliases["a"] = s[2:].split()[0]
                elif s.startswith("join "):
                    mj = re.match(r"join (\w+)=(\w+) on (.*)$", s)
                    aliases[mj.group(1)] = mj.group(2)
            for s in args.split(";"):
                s = s.strip()
                if s.startswith("exists "):
                    me = re.match(r"exists (\w+)=(\w+) where (.*)$", s)
                    aliases[me.group(1)] = me.group(2)
            for s in args.split(";"):
                s = s.strip()
                for pre in ("join ", "where ", "when ", "exists "):
                    if s.startswith(pre):
                        expr = s.split(" on ", 1)[1] if pre == "join " else (s.split(" where ", 1)[1] if pre == "exists " else s[len(pre):])
                        names(expr, aliases)
    return problems


def evaluate_rules(model, data):
    violated = {}
    for bid, br in model.t["BR"].items():
        if br["Spec"] in ("procedure", "n/a"):
            continue
        msgs = run_rule_items(model, data, br["Spec"])
        if msgs:
            violated[bid] = msgs
    return violated


def asof(data, op):
    m = re.match(r"asof (\w+) where (\w+)=(\S+) date=(\S+) return (\w+)$", op)
    entity, key, val, date, ret = m.groups()
    want = parse_value(val)
    hits = [r for r in data.get(entity, []) if r.get(key) == want and r.get("valid_from") is not None
            and r["valid_from"] <= date and (r.get("valid_to") is None or date < r["valid_to"])]
    return ",".join(sorted(str(h.get(ret)) for h in hits)) if hits else "none"


def run_scenario(model, base, scn):
    ops = scn["Operations"]
    if scn["Kind"] == "Query":
        return asof(base, ops), ""
    data = apply_operations(model.t, base, ops)
    violated = evaluate_rules(model, data)
    if not violated:
        return "Accept", "none"
    return "Reject", ", ".join(sorted(violated))


# ----------------------------------------------------------------------------- normalisation
def parse_fds(t, relation):
    fds = []
    for r in t["FD"].values():
        if r["Relation"] == relation:
            fds.append((frozenset(split_list(r["Determinant"])), frozenset(split_list(r["Dependent"]))))
    return fds


def closure(attrs, fds):
    result = set(attrs)
    changed = True
    while changed:
        changed = False
        for lhs, rhs in fds:
            if lhs <= result and not rhs <= result:
                result |= rhs
                changed = True
    return result


def candidate_keys(all_attrs, fds):
    attrs = sorted(all_attrs)
    keys = []
    for size in range(1, len(attrs) + 1):
        for combo in itertools.combinations(attrs, size):
            s = set(combo)
            if closure(s, fds) >= set(attrs) and not any(k <= s for k in keys):
                keys.append(frozenset(s))
    return keys


def normal_form(all_attrs, fds):
    keys = candidate_keys(all_attrs, fds)
    prime = set().union(*keys) if keys else set()
    bcnf, third = True, True
    for lhs, rhs in fds:
        for a in rhs - lhs:
            if not closure(lhs, fds) >= set(all_attrs):
                bcnf = False
                if a not in prime:
                    third = False
    return keys, "BCNF" if bcnf else ("3NF" if third else "below 3NF")


def projected_bcnf(leaf, root_fds):
    attrs = sorted(leaf)
    for size in range(1, len(attrs)):
        for combo in itertools.combinations(attrs, size):
            x = set(combo)
            cl = closure(x, root_fds) & set(leaf)
            if cl - x and cl != set(leaf):
                return False
    return True


def fds_of(t, rel):
    """Dependencies of a relation: its own rows, or the root's dependencies projected onto it."""
    own = parse_fds(t, rel)
    if own:
        return own
    parent_of = {}
    for d in t["DP"].values():
        parent_of[d["Child 1"]] = d["Parent relation"]
        parent_of[d["Child 2"]] = d["Parent relation"]
    root = rel
    while root in parent_of:
        root = parent_of[root]
    if root == rel:
        return own
    root_fds = parse_fds(t, root)
    attrs = sorted(relation_attrs(t, rel))
    projected = []
    for size in range(1, len(attrs)):
        for combo in itertools.combinations(attrs, size):
            x = frozenset(combo)
            rhs = (closure(x, root_fds) & set(attrs)) - x
            if rhs:
                projected.append((x, frozenset(rhs)))
    return projected


def relation_attrs(t, name):
    for r in t["LR"].values():
        if r["Relation"] == name:
            return frozenset(split_list(r["Relation attributes"]))
    if name in {r["Entity"] for r in t["LE"].values()}:
        return frozenset(a["Attribute"] for a in t["AT"].values() if a["Entity"] == name)
    return None


# ----------------------------------------------------------------------------- checks
def check(t, prose, diagrams):
    errors = []

    def err(rid, msg):
        errors.append(f"{rid}: {msg}")

    model = Model(t)
    defined = set().union(*(set(v) for v in t.values()))
    for kind, rows in t.items():
        for rid, row in rows.items():
            for col, val in row.items():
                if col != "_line" and not val:
                    err(rid, f"empty cell in '{col}'")
            if kind in NEEDS_LABEL and row.get("Evidence") not in EVIDENCE:
                err(rid, f"evidence label '{row.get('Evidence')}' is invalid")
    for token in sorted(set(ID_ANY.findall(prose)) - defined):
        err(token, "referenced but never defined")

    # --- requirements, consumers, interviews
    for rid, r in t["REQ"].items():
        if r["Priority"] not in ("Must", "Should", "Could"):
            err(rid, "invalid priority")
        if not refs(r["Source"]):
            err(rid, "needs a source")
    for cid, c in t["CM"].items():
        if c["Consumer"] not in t["STK"] or not c["Model use"].strip():
            err(cid, "each consumer needs a stakeholder and a stated use")
    for iid, i in t["INT"].items():
        if i["Stakeholder"] not in t["STK"]:
            err(iid, "unknown stakeholder")

    # --- glossary
    seen = {}
    for gid, g in t["GL"].items():
        key = (g["Glossary term"].lower(), g["Context"])
        if key in seen:
            err(gid, f"term '{g['Glossary term']}' defined twice in context {g['Context']}")
        seen[key] = gid
        toks = [w for w in words(g["Definition"]) if w not in STOP and w not in words(g["Glossary term"])]
        if len(toks) < 4:
            err(gid, "definition is circular or too thin")
    terms = {g["Glossary term"].lower() for g in t["GL"].values()}
    for sid, s in t["SY"].items():
        if s["Preferred term"].lower() not in terms:
            err(sid, "preferred term is not in the glossary")
    for hid, h in t["HM"].items():
        contexts = {g["Context"] for g in t["GL"].values() if g["Glossary term"].lower() == h["Homonym"].lower()}
        defs = {g["Definition"] for g in t["GL"].values() if g["Glossary term"].lower() == h["Homonym"].lower()}
        if len(contexts) < 2 or len(defs) < 2:
            err(hid, "a homonym must have distinct definitions in at least two contexts")
        if {x.strip() for x in h["Contexts"].split(";")} != contexts:
            err(hid, f"listed contexts differ from the glossary contexts {sorted(contexts)}")
    for lid, l in t["LE"].items():
        spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", l["Entity"]).lower()
        if spaced not in terms:
            err(lid, f"logical entity {l['Entity']} has no glossary term '{spaced}'")

    # --- conceptual model
    accepted = {c for c, r in t["CE"].items() if r["Decision"] == "Accept"}
    for cid, c in t["CE"].items():
        if c["Decision"] not in ("Accept", "Relationship", "Refinement", "Reject", "Open"):
            err(cid, "invalid decision")
        toks = [w for w in words(c["Business definition"]) if w not in STOP and w not in words(c["Candidate entity"])]
        if c["Decision"] in ("Accept", "Relationship") and len(toks) < 4:
            err(cid, "definition is circular or too thin")
    conceptual_text = " ".join(" ".join(v for k, v in r.items() if k != "_line")
                               for kind in ("CE", "CR") for r in t[kind].values())
    conceptual_text += " " + diagrams.get("D6-DIAGRAM", "")
    m = PHYSICAL_TERMS.search(conceptual_text)
    if m:
        err("D6", f"physical or platform term in the conceptual model: {m.group()}")
    for crid, c in t["CR"].items():
        for col in ("Concept A", "Concept B"):
            if c[col] not in {r["Candidate entity"] for r in t["CE"].values()}:
                err(crid, f"{col} '{c[col]}' is not a candidate entity")
        for col in ("Cardinality A to B", "Cardinality B to A"):
            if not re.match(r"^(0|1)\.\.(1|\*)$|^1$", c[col]):
                err(crid, f"invalid {col}")
        if c["Reverse phrase (B to A)"] in ("", "n/a"):
            err(crid, "needs both-direction statements")
    shown = set(re.findall(r"\bCE-\d{2,3}\b", diagrams.get("D6-DIAGRAM", "")))
    if shown != accepted:
        err("D6", f"diagram entities {sorted(shown ^ accepted)} differ from accepted candidates")
    shown_l = set(re.findall(r"\bLE-\d{2,3}\b", diagrams.get("D7-DIAGRAM", "")))
    if shown_l != set(t["LE"]):
        err("D7", f"diagram entities {sorted(shown_l ^ set(t['LE']))} differ from logical entities")

    # --- conceptual to logical consistency
    mapped_c, mapped_l = set(), set()
    for mid, c in t["CLM"].items():
        mapped_c.update(refs(c["Conceptual element"]))
        mapped_l.update(refs(c["Logical element(s)"]))
        if c["Refinement"] not in ("Same", "Split", "Resolved", "Added", "Merged"):
            err(mid, "invalid refinement type")
    conceptual_all = accepted | set(t["CR"])
    for c in sorted(conceptual_all - mapped_c):
        err(c, "conceptual element has no logical mapping")
    for l in sorted((set(t["LE"]) | set(t["RL"])) - mapped_l):
        err(l, "logical element has no conceptual mapping or documented refinement")

    # --- logical structure
    for entity, lid in model.entities.items():
        if entity not in model.pk:
            err(lid, "entity has no primary key")
            continue
        names = model.attr_names(entity)
        if not set(model.pk[entity]) <= set(names):
            err(lid, "primary key attributes are not attributes of the entity")
        for a in model.attrs.get(entity, []):
            if a["Logical domain"] not in DOMAINS or a["Required"] not in ("Y", "N"):
                err(a["ID"] if "ID" in a else lid, "invalid domain or requiredness")
            if a["Attribute"] in model.pk[entity] and a["Required"] != "Y":
                err(lid, f"identifier {a['Attribute']} must be required")
    fk_attrs = {(e, a) for e, a, _ in model.fk}
    for aid, a in t["AT"].items():
        has_ref = a["References"] != "none"
        if has_ref != ((a["Entity"], a["Attribute"]) in fk_attrs):
            err(aid, "References and the foreign-key declaration disagree")
        if has_ref:
            e2, a2 = a["References"].split(".")
            if (e2 not in model.entities) or a2 not in model.attr_names(e2) or \
                    a2 not in model.pk.get(e2, []) + [x for k in model.alt.get(e2, []) for x in k]:
                err(aid, f"reference {a['References']} is not a key")
    for rid, r in t["RL"].items():
        parent, child = r["Parent entity"], r["Child entity"]
        fkcol = r["Foreign key"]
        if parent not in model.entities or child not in model.entities:
            err(rid, "unknown parent or child entity")
            continue
        if r["Parents per child"] not in ("1", "0..1"):
            err(rid, "a child has one parent (1) or at most one (0..1) through a foreign key")
        if not re.match(r"^(0|1)\.\.(1|\*)$|^1$", r["Children per parent"]):
            err(rid, "invalid Children per parent")
        decl = [x for x in model.fk if x[0] == child and x[1] == fkcol]
        if not decl or not decl[0][2].startswith(parent + "."):
            err(rid, f"foreign key {child}.{fkcol} does not reference {parent}")
            continue
        required = next(a["Required"] for a in model.attrs[child] if a["Attribute"] == fkcol)
        if (r["Parents per child"] == "1") != (required == "Y"):
            err(rid, "minimum participation and the foreign key's requiredness disagree")
        if not r["Verb phrase (parent to child)"].strip() or not r["Reverse phrase (child to parent)"].strip():
            err(rid, "needs both-direction statements")
    for e, a, ref in model.fk:
        if not any(r["Child entity"] == e and r["Foreign key"] == a for r in t["RL"].values()):
            err(f"{e}.{a}", "foreign key has no relationship definition")

    for lid, l in t["LE"].items():
        if split_list(l["Primary key"]) != model.pk.get(l["Entity"]):
            err(lid, "primary key in the entity table differs from the key definitions")
    # --- keys
    for kid, k in t["KY"].items():
        cols = split_list(k["Attributes"])
        if k["Entity"] not in model.entities or not set(cols) <= set(model.attr_names(k["Entity"])):
            err(kid, "key attributes are not attributes of the entity")

    # --- naming standard
    ns = {n: r for n, r in t["NS"].items()}
    for nid, n in ns.items():
        if n["Pattern"] == "n/a":
            continue
        try:
            pat = re.compile(n["Pattern"].strip("`").replace(" // ", "|"))
        except re.error:
            err(nid, "pattern is not a valid expression")
            continue
        deny = n["Applies to"].startswith("deny")
        if bool(pat.search(n["Good example"])) == deny or bool(pat.search(n["Poor example"])) != deny:
            err(nid, "the rule's good and poor examples do not behave as stated")
    for entity, lid in model.entities.items():
        for nid, n in ns.items():
            if n["Pattern"] == "n/a":
                continue
            pat, scope = re.compile(n["Pattern"].strip("`").replace(" // ", "|")), n["Applies to"]
            if scope == "entity" and not pat.search(entity):
                err(entity, f"violates {nid}")
            if scope == "deny:entity" and pat.search(entity):
                err(entity, f"violates {nid}")
    for aid, a in t["AT"].items():
        for nid, n in ns.items():
            if n["Pattern"] == "n/a":
                continue
            pat, scope = re.compile(n["Pattern"].strip("`").replace(" // ", "|")), n["Applies to"]
            name = a["Attribute"]
            if scope == "attr:any" and not pat.search(name):
                err(aid, f"{a['Entity']}.{name} violates {nid}")
            elif scope == f"attr:{a['Logical domain']}" and not pat.search(name):
                err(aid, f"{a['Entity']}.{name} violates {nid}")
            elif scope == "deny:attr" and pat.search(name):
                err(aid, f"{a['Entity']}.{name} violates {nid}")
        if a["References"] != "none" and not a["Attribute"].endswith(a["References"].split(".")[1]):
            err(aid, "a foreign key name must end with the referenced key name")

    # --- dictionary coverage and definition quality
    expected = set(model.entities) | {f"{a['Entity']}.{a['Attribute']}" for a in t["AT"].values()}
    present = {d["Element"] for d in t["DD"].values()}
    for missing in sorted(expected - present):
        err("DD", f"no dictionary entry for {missing}")
    for extra in sorted(present - expected):
        err("DD", f"dictionary entry {extra} matches no logical element")
    for did, d in t["DD"].items():
        base = d["Element"].split(".")[-1]
        toks = [w for w in words(d["Business definition"]) if w not in STOP and w not in words(base)
                and w not in words(d["Element"])]
        if len(toks) < 4:
            err(did, f"definition of {d['Element']} is circular or too thin")
        if d["Owner"] != "Unknown" and not d["Owner"].startswith("STK") and not d["Owner"].startswith("Unknown"):
            err(did, "owner must be a stakeholder or Unknown")

    # --- rules register
    structural_required, fk_cov, uniq_cov, dom_cov = set(), set(), set(), set()
    for bid, b in t["BR"].items():
        if b["Status"] not in RULE_STATUS:
            err(bid, "invalid status")
        if b["Representation"] not in ("Structure", "Constraint", "Procedure"):
            err(bid, "invalid representation")
        if b["Status"] != "Open" and not refs(b["Source"]):
            err(bid, "a rule that is not open needs a source ID")
        spec = b["Spec"]
        if spec not in ("procedure", "n/a"):
            try:
                run_rule_items(model, {}, spec)
                for p in spec_problems(model, spec):
                    err(bid, f"spec uses unknown attribute {p}")
            except Exception as exc:  # noqa: BLE001
                err(bid, f"spec cannot be evaluated: {exc}")
            for item in spec.split(" & "):
                name = item.split("(")[0].strip()
                body = item[item.find("(") + 1:-1]
                if name == "required":
                    structural_required.update(split_list(body))
                elif name == "fk":
                    fk_cov.update(x.split("->")[0].strip() for x in split_list(body))
                elif name == "unique":
                    e, cols = body.split(":")
                    uniq_cov.add((e.strip(), tuple(split_list(cols))))
                elif name == "domain":
                    dom_cov.update(split_list(body))
    for aid, a in t["AT"].items():
        ref = f"{a['Entity']}.{a['Attribute']}"
        if a["Required"] == "Y" and a["Attribute"] not in model.pk[a["Entity"]] and ref not in structural_required:
            err(aid, f"{ref} is required but no rule enforces it")
        if a["References"] != "none" and ref not in fk_cov:
            err(aid, f"{ref} is a foreign key but no rule enforces it")
        if a["Allowed values"] != "none" and ref not in dom_cov:
            err(aid, f"{ref} has allowed values but no rule enforces them")
    for e, groups in model.alt.items():
        for cols in groups:
            if (e, tuple(cols)) not in uniq_cov:
                err(e, f"alternate key {cols} has no uniqueness rule")

    # --- fixture and scenarios
    base = load_dataset(t)
    for bid, msgs in evaluate_rules(model, base).items():
        err("DAT", f"base dataset violates {bid}: {msgs[0]}")
    scenarios = t["SCN"]
    invalid = 0
    for sid, s in scenarios.items():
        if s["Kind"] not in ("Mutation", "Query"):
            err(sid, "invalid kind")
            continue
        outcome, rules = run_scenario(model, base, s)
        if outcome != s["Observed outcome"] or (s["Kind"] == "Mutation" and rules != s["Observed rules"]):
            err(sid, f"observed ({s['Observed outcome']}, {s['Observed rules']}) != computed ({outcome}, {rules})")
        if s["Expected outcome"] != s["Observed outcome"]:
            err(sid, f"expected {s['Expected outcome']} but the model produced {s['Observed outcome']}")
        if s["Kind"] == "Mutation" and s["Expected rules"] != s["Observed rules"]:
            err(sid, f"expected rules {s['Expected rules']} but observed {s['Observed rules']}")
        if s["Expected outcome"] == "Reject":
            invalid += 1
        if not refs(s["Rule reference"]):
            err(sid, "needs a rule reference")
    if len(scenarios) < 20 or invalid < 8:
        err("SCN", f"need at least 20 scenarios and 8 invalid ones; have {len(scenarios)} and {invalid}")
    for bid, b in t["BR"].items():
        if b["Status"] == "Confirmed":
            rel = [s for s in scenarios.values() if bid in refs(s["Rule reference"])]
            if not any(s["Expected outcome"] == "Accept" for s in rel) or \
                    not any(s["Expected outcome"] == "Reject" for s in rel):
                err(bid, "a confirmed rule needs at least one valid and one invalid scenario")
        elif b["Spec"] not in ("procedure", "n/a"):
            rel = [s for s in scenarios.values() if bid in refs(s["Rule reference"])]
            if not any(s["Expected outcome"] == "Reject" for s in rel):
                err(bid, "an enforceable rule needs at least one invalid scenario")

    # --- normalisation
    for lid, l in t["LR"].items():
        l["_attrs"] = frozenset(split_list(l["Relation attributes"]))
    for nid, n in t["NF"].items():
        rel = n["Relation"]
        attrs = relation_attrs(t, rel)
        fds = fds_of(t, rel)
        if attrs is None:
            err(nid, f"unknown relation {rel}")
            continue
        keys, form = normal_form(attrs, fds)
        keytxt = "; ".join(sorted("(" + ", ".join(sorted(k)) + ")" for k in keys))
        if n["Candidate keys"] != keytxt or n["Normal form"] != form:
            err(nid, f"stated ({n['Candidate keys']}, {n['Normal form']}) != computed ({keytxt}, {form})")
    for entity in model.entities:
        attrs = frozenset(model.attr_names(entity))
        fds = parse_fds(t, entity)
        keys, form = normal_form(attrs, fds)
        if frozenset(model.pk[entity]) not in keys:
            err(entity, "the declared primary key is not a candidate key under the stated dependencies")
        for alt in model.alt.get(entity, []):
            if frozenset(alt) not in keys:
                err(entity, f"alternate key {alt} is not a candidate key under the stated dependencies")
        if form != "BCNF":
            err(entity, f"entity is {form}, not BCNF; justify or decompose")
    children = {d["Child 1"] for d in t["DP"].values()} | {d["Child 2"] for d in t["DP"].values()}
    parent_of = {}
    for d in t["DP"].values():
        parent_of[d["Child 1"]] = d["Parent relation"]
        parent_of[d["Child 2"]] = d["Parent relation"]

    def root_of(rel):
        while rel in parent_of:
            rel = parent_of[rel]
        return rel
    for did, d in t["DP"].items():
        p, c1, c2 = d["Parent relation"], d["Child 1"], d["Child 2"]
        pa, a1, a2 = (relation_attrs(t, x) for x in (p, c1, c2))
        if None in (pa, a1, a2):
            err(did, "unknown relation in the decomposition step")
            continue
        if a1 | a2 != pa:
            err(did, "children do not cover the parent's attributes")
        common = a1 & a2
        if set(split_list(d["Common attributes"])) != set(common):
            err(did, "stated common attributes differ from the intersection")
        root_fds = parse_fds(t, root_of(p))
        cl = closure(common, root_fds) & pa
        if not (cl >= a1 or cl >= a2):
            err(did, "the decomposition is not lossless under the stated dependencies")
    for root in sorted({root_of(d["Parent relation"]) for d in t["DP"].values()}):
        rfds = parse_fds(t, root)
        root_leaves = collect_leaves(t, root)
        for leaf in root_leaves:
            la = relation_attrs(t, leaf)
            if not projected_bcnf(la, rfds):
                err(leaf, "leaf relation is not in BCNF under the projected dependencies")
        for lhs, rhs in rfds:
            z = set(lhs)
            changed = True
            while changed:
                changed = False
                for leaf in root_leaves:
                    la = relation_attrs(t, leaf)
                    add = closure(z & la, rfds) & la
                    if not add <= z:
                        z |= add
                        changed = True
            if not rhs <= z:
                err(root, f"dependency {sorted(lhs)} -> {sorted(rhs)} is not preserved")

    # --- traceability and coverage
    traced_reqs = {x["Requirement"] for x in t["TR"].values()}
    for rid, r in t["REQ"].items():
        sat = refs(r["Satisfied by"])
        if not sat:
            err(rid, "requirement is satisfied by nothing")
        if any(s.startswith("BR-") for s in sat) and rid not in traced_reqs:
            err(rid, "a rule-based requirement needs a traceability row")
    for trid, r in t["TR"].items():
        if r["Requirement"] not in t["REQ"] or r["Rule"] not in t["BR"]:
            err(trid, "requirement or rule does not exist")
        if r["Scenario"] not in t["SCN"]:
            err(trid, "scenario does not exist")
        elem = r["Logical element"]
        if elem not in expected:
            err(trid, f"logical element {elem} does not exist")
        elif elem not in present:
            err(trid, "logical element is not in the dictionary")
    for r in t["FND"].values():
        if r["Defect type"] not in DEFECT_TYPES or r["Severity"] not in SEVERITY or r["Status"] not in ("Open", "Closed"):
            err(r["ID"], "invalid defect type, severity or status")
        if r["Status"] == "Closed" and r["Severity"] in ("Blocking", "Major") and not r["Acceptance test"]:
            err(r["ID"], "a closed blocking or major finding needs an acceptance test")
    for oid, o in t["OQ"].items():
        if o["Status"] not in ("Open", "Provisional", "Resolved") or o["Owner"] == "":
            err(oid, "invalid status or owner")
    for rid, r in t["RV"].items():
        if r["Result"] not in ("Pass", "Finding", "Not applicable"):
            err(rid, "invalid result")
    return errors


def collect_leaves(t, root):
    parents = {d["Parent relation"] for d in t["DP"].values()}
    out, stack = [], [root]
    while stack:
        r = stack.pop()
        if r not in parents:
            out.append(r)
            continue
        for d in t["DP"].values():
            if d["Parent relation"] == r:
                stack.extend([d["Child 1"], d["Child 2"]])
    return out


# ----------------------------------------------------------------------------- derive / trace
def derive(t):
    model = Model(t)
    base = load_dataset(t)
    for sid, s in t["SCN"].items():
        outcome, rules = run_scenario(model, base, s)
        print(f"SCN {sid} outcome={outcome} rules={rules}")
    for nid, n in t["NF"].items():
        attrs = relation_attrs(t, n["Relation"])
        keys, form = normal_form(attrs, fds_of(t, n["Relation"]))
        print(f"NF {nid} {n['Relation']} keys={'; '.join(sorted('(' + ', '.join(sorted(k)) + ')' for k in keys))} form={form}")


def trace(t, count, seed):
    rng = random.Random(seed)
    for trid in rng.sample(sorted(t["TR"]), min(count, len(t["TR"]))):
        r = t["TR"][trid]
        print(f"{r['Logical element']} <- {r['Rule']} <- {r['Requirement']}: "
              f"{t['REQ'][r['Requirement']]['Requirement statement'][:60]}...")
    for rid in rng.sample(sorted(t["REQ"]), min(count, len(t["REQ"]))):
        hit = next((x for x in t["TR"].values() if x["Requirement"] == rid), None)
        if hit:
            print(f"{rid} -> {hit['Rule']} -> {hit['Logical element']} -> {hit['Scenario']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file")
    ap.add_argument("--derive", action="store_true")
    ap.add_argument("--trace", type=int, metavar="N")
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    tables, prose, diagrams, errors = parse(Path(args.file).read_text(encoding="utf-8"))
    if args.derive:
        derive(tables)
        return 0
    if args.trace:
        trace(tables, args.trace, args.seed)
        return 0
    if errors:
        for m in errors:
            print(f"ERROR {m}")
        print(f"{len(errors)} structural error(s); fix them first")
        return 1
    try:
        errors += check(tables, prose, diagrams)
    except (KeyError, TypeError, ValueError, AttributeError, ZeroDivisionError) as exc:
        errors.append(f"checker could not complete ({type(exc).__name__}: {exc}); "
                      f"a table is probably missing or malformed")
    print("Parsed: " + ", ".join(f"{k}={len(v)}" for k, v in sorted(tables.items())))
    for m in errors:
        print(f"ERROR {m}")
    print(f"{len(errors)} error(s)" if errors else "All checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

---

*End of document. Version 1.1, 2026-10-21.*
