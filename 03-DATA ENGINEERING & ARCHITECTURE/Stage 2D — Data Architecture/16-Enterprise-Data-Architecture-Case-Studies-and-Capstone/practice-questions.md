# Enterprise Data Architecture Case Studies and Capstone — Practice Questions

**Target:** `Stage 2D — Data Architecture/16-Enterprise-Data-Architecture-Case-Studies-and-Capstone/practice-questions.md`  
**Purpose:** Assess understanding, analysis, trade-off reasoning, validation, and defense across Case Studies 01–06 and Topics 07–08.

> **Source integrity.** The current accessible copies of all six case-study files and Topics 07–08 were inspected and are populated. The roadmap’s note that they were empty describes their state when the roadmap was authored, not the current copies inspected here. The current `Projects/16-enterprise-data-architecture-capstone.md` brief and any official rubric were not available for direct inspection. The accessible project-tree file is `Roadmap_ptree(20261020-184004).md`, rather than the exact filename `Roadmap_ptree.md`. The generation/audit template was inspected and its source-boundary, private-audit, revision, and verification conventions were applied.
>
> **Illustrative assumptions.** Names, example data, rates, target values, thresholds, and scenarios introduced in questions are practice assumptions, not verified business facts or official requirements. Where the case-study lessons themselves use illustrative scenarios, questions preserve that status. Once the real capstone brief is available, its wording and authorised rubric take precedence.

## How to use this document

1. Attempt each question before reading the answer key.
2. For architecture scenarios, state requirements, constraints, assumptions, alternatives, decision criteria, risks, and validation evidence.
3. A different architecture from the answer key can be strong if it meets the stated requirements and explains its trade-offs.
4. Record gaps in Section 4, revisit the named lesson or prerequisite, redo an exercise, and retest later.
5. Difficulty labels and the self-assessment guidance are learning aids, not official examination rules.

- **Beginner:** explain and identify.
- **Intermediate:** analyse and apply.
- **Advanced:** compare, evaluate, justify, and defend.

## 1. Questions

### A. Core Architecture Foundations

#### A-01 — Beginner — Requirement classification
A sponsor says: “We need trusted daily reporting from two existing source systems. The sources must remain in place. Reports should be available to operations managers.” Classify each clause as a business objective, functional requirement, constraint, or stakeholder/consumer statement; a clause may contain more than one classification. Identify at least four open questions.

#### A-02 — Intermediate — Facts, assumptions, and unknowns
A scenario names sources, consumers, and a desired outcome but says nothing about volume, freshness, retention, recovery objectives, budget, or deployment environment. Create a register separating confirmed facts, assumptions, constraints, risks, and open questions. Why must “use a cloud lakehouse” not be recorded as a fact unless the source says so?

#### A-03 — Intermediate — Quality attributes and conflicts
An illustrative platform must provide fresh data, exact financial reconciliation, and low operating cost. Explain why these goals differ, identify two plausible conflicts, and propose a process for resolving them without silently weakening a requirement.

#### A-04 — Advanced — Architecture decision record
Compare a central platform with governed shared data products against domain-owned platforms with federated standards and selected shared services. State the context, criteria, trade-offs, risks, and validation evidence for an ADR. Under what conditions could either design be reasonable?

#### A-05 — Advanced — Requirement traceability
Design a traceability chain for “a report must be reconciled to its source”: requirement record, architecture response, deliverable, test/evidence, result, and owner. How should the requirement be reported if evidence is not yet available?

### B. Case Study 01 — Banking Data Platform

#### B-01 — Beginner — End-to-end flow
Describe or draw a source-to-consumer flow for an illustrative banking data platform: sources, ingestion, validation, storage/processing, governed serving, and a report or analytical consumer. Mark ownership, classification, lineage, monitoring, and failure/quarantine paths. Do not assume a vendor.

#### B-02 — Intermediate — Reconciliation calculation
A daily source extract contains 1,200,000 records; the curated output contains 1,198,700. The pipeline reports success. Calculate the count difference and list the checks required before accepting the output. Why is count equality not a complete correctness proof?

#### B-03 — Intermediate — Governance and security
Propose controls for analytics over account, transaction, and customer data: classification, least privilege, separation of duties, masking/restricted views, audit, lineage, and retention. Distinguish ingestion controls from controls that must also be enforced at serving time.

#### B-04 — Advanced — Resilience and cost
A proposal synchronously replicates every dataset across two regions “for safety.” Challenge it. Identify requirements to clarify and compare synchronous replication, asynchronous replication, backup/restore, and replay for consistency, recovery, latency, and cost.

#### B-05 — Advanced — Architecture defense
A reviewer says, “A single central warehouse is simpler, so it is always the best banking architecture.” Respond using criteria. When might centralization fit, when might additional serving or domain components be justified, and what evidence is needed?

### C. Case Study 02 — Customer 360 and Master Data

#### C-01 — Beginner — Identity concepts
Explain the difference between a source customer record, an identity-resolution result, a mastered/golden record, and an analytical Customer 360 view. Why are they not synonyms?

#### C-02 — Intermediate — Matching strategies
Illustrative records: A has email `alex@example.test`, phone `+1-555-0100`, name `Alex Rivera`; B has the same email, phone `+1-555-0199`, name `A. Rivera`. Explain how deterministic and probabilistic matching could treat them. What evidence is needed before an automatic merge, and why may a shared email be insufficient?

#### C-03 — Intermediate — Survivorship
Three systems disagree about a customer’s phone number and address. Design field-level survivorship rules considering source authority, provenance, recency, validation, and ownership. Why is “latest update wins” unsafe as a universal rule?

#### C-04 — Advanced — False and missed matches
Compare the harms, detection, correction, audit, and downstream repair for a false merge versus a missed match. Which cases may be auto-resolved, and which should go to human review?

#### C-05 — Advanced — Consent and lineage
A customer withdraws consent for a specific purpose. Explain how to find affected records, derived data, views, caches, and consumers; apply policy; preserve an appropriate audit trail; and verify propagation. Which decisions depend on actual legal/policy requirements?

### D. Case Study 03 — Real-Time Fraud and Risk Platform

#### D-01 — Beginner — Event semantics
Define event time, processing time, ordering, late event, replay, and idempotency. Give an example of how confusing event time with processing time can distort a fraud/risk decision.

#### D-02 — Intermediate — Latency budget
**Illustrative assumption:** a decision must complete within 250 ms. Allocations are 35 ms for intake, 70 ms for feature/state lookup, 80 ms for scoring/policy, 25 ms for response delivery, and 20 ms safety margin. Calculate total allocation and remaining budget. If observed p99 is 285 ms, what does the arithmetic establish—and not establish?

#### D-03 — Intermediate — Duplicate and late events
A payment event is delivered twice and a related device-risk event arrives 90 seconds late. Design deduplication, event-time handling, state updates, replay, and idempotent downstream actions. Which choices require business semantics rather than only infrastructure configuration?

#### D-04 — Advanced — Capacity calculation
**Illustrative assumption:** normal traffic is 4,000 events/s, peak traffic is 3× normal, and target capacity includes 30% headroom above peak. Calculate target capacity. Why can that number not prove the latency objective is met?

#### D-05 — Advanced — Risk trade-offs
Explain consequences of false-positive and false-negative fraud decisions. Propose an evaluation plan beyond overall accuracy and describe degraded behaviour when a feature store or scoring service is unavailable. Why is neither “fail open” nor “fail closed” universally correct?

### E. Case Study 04 — Enterprise Lakehouse Modernization

#### E-01 — Beginner — Current state
What information should be collected to describe a current data estate before proposing a target? Why is a target diagram alone insufficient to justify modernization?

#### E-02 — Intermediate — Alternatives
Compare incremental improvement of the current platform, lakehouse migration, and hybrid coexistence. Define criteria before choosing and identify unknowns that could change the recommendation.

#### E-03 — Intermediate — Reconciliation calculation
During an illustrative migration, legacy revenue is 8,450,000 currency units and the new platform reports 8,427,500. Calculate absolute and percentage difference relative to legacy. List the investigation steps before deciding whether this is a defect, semantic difference, or timing issue.

#### E-04 — Advanced — Migration sequencing
Design a phased migration for dependent datasets and consumers. Include dependency order, parallel run, reconciliation, acceptance, rollback criteria, ownership, and decommissioning. How do you prevent conflicting sources of truth during coexistence?

#### E-05 — Advanced — Cutover defense
A team plans to switch every consumer over one weekend and immediately delete the old environment. Identify failure modes and propose safer cutover/rollback. What evidence is needed before decommissioning?

### F. Case Study 05 — Multi-Cloud Data Platform

#### F-01 — Beginner — Challenge the premise
List possible drivers for multi-cloud and conditions where single-cloud or hybrid may be preferable. Why does “avoid lock-in” not prove multi-cloud is worth the cost?

#### F-02 — Intermediate — Portability by layer
Assess portability across data/table formats, storage, compute, orchestration, identity, networking, governance/catalogue, observability, and managed services. Classify what is portable, needs adaptation, or is provider-dependent.

#### F-03 — Intermediate — Cross-cloud data security
Two cloud environments must exchange sensitive analytical data. Address connectivity, identity federation, encryption, key management, classification, transfer authorisation, audit, residency, integrity, and recovery. Why does encryption not itself authorise the transfer?

#### F-04 — Advanced — Transfer-cost calculation
**Illustrative assumption:** 18 TB/month crosses a cloud boundary; simplified charge is $0.07/GB; use decimal units (1 TB = 1,000 GB). Calculate monthly transfer charges before other costs. Why is this not a full TCO estimate?

#### F-05 — Advanced — Resilience alternatives
Compare multi-cloud active-active, active-passive recovery into a second cloud, and a primary cloud with tested backups/portable deployment artefacts. State conditions and evidence supporting each, including consistency, identity, recovery tests, operations, and cost.

### G. Case Study 06 — Governed RAG and Enterprise Knowledge

#### G-01 — Beginner — Knowledge lifecycle
Describe the lifecycle from document source and ingestion through parsing, chunking, metadata, embedding/indexing, retrieval, grounded answer generation, citation, monitoring, and update/deletion. Identify at least four points where lineage or freshness metadata should be maintained.

#### G-02 — Intermediate — Chunking and retrieval
Explain how chunk size, overlap, document structure, metadata filters, embedding choice, and retrieval strategy affect answer quality, latency, cost, and citation usefulness. Propose an evaluation method that does not assume one chunking strategy is best for every corpus.

#### G-03 — Intermediate — Permission-aware retrieval and revocation
A user loses access to a document after its chunks have been indexed. Explain how to prevent retrieval from continuing to expose the document. Distinguish index removal/refresh, authoritative permission checks, cache invalidation, and audit verification. Why is hiding the citation after generation insufficient?

#### G-04 — Advanced — Prompt injection
A retrieved document tells the model to ignore prior rules and disclose other documents. Explain the trust boundary, retrieval and prompt-handling controls, tool/action restrictions, output validation, and tests needed. Why must retrieved text be treated as data rather than authoritative instructions?

#### G-05 — Advanced — RAG validation
Design a test plan for retrieval relevance, groundedness, citation correctness, access control, freshness, deletion/revocation, prompt injection, latency, and failure handling. Explain how to distinguish retrieval failure from generation failure and retain diagnostic evidence without unnecessary sensitive-content logging.

### H. Capstone Requirements and Deliverables

#### H-01 — Beginner — Brief extraction
When you receive a capstone brief, what do you inspect before designing? List source-of-truth documents and extract business objective, functional/non-functional requirements, constraints, assumptions, dependencies, risks, open questions, stakeholders, and named deliverables.

#### H-02 — Intermediate — Requirement-to-deliverable mapping
Build a traceability row for this hypothetical requirement: “Sensitive data must be available only to authorised consumers.” Include source location, requirement ID, interpretation, architecture response, deliverable location, validation evidence, owner, and status. Label the example illustrative.

#### H-03 — Intermediate — Deliverable selection and dependencies
A hypothetical brief explicitly requires a context diagram, logical data-flow diagram, ADRs, migration plan, and validation evidence. Propose a work order and explain dependencies. Identify supporting artefacts you might recommend but must not label mandatory unless the brief says so.

#### H-04 — Advanced — Ambiguous brief
A brief says “near real-time” but gives no measurable freshness target; it also requires low cost and strong recovery without recovery objectives. Explain how to resolve ambiguity, questions to ask, how to record provisional assumptions, and what remains unverified until an authorised answer arrives.

#### H-05 — Advanced — Evidence plan
Design an evidence plan mapping each requirement to artefacts and tests. Include positive and negative tests, ownership, test data, source of acceptance criteria, evidence location, review status, and unavailable evidence. Why is a deliverable inventory not proof of requirement satisfaction?

### I. Capstone Validation and Defense

#### I-01 — Beginner — Verification versus validation
Explain verification, validation, and defense. Give one example of verification and one of validation for a data architecture. Why is completing an artefact not the same as validating the architecture?

#### I-02 — Intermediate — Unsupported claims
A design claims “99.99% availability,” “sub-second response,” and “full regulatory compliance,” but provides no definitions, measurement boundaries, tests, control mapping, or source references. For each claim, identify missing evidence and rewrite it to remain supportable.

#### I-03 — Intermediate — Finding and remediation
A logical diagram shows one mastered customer, while the data model permits two independently writable golden records. Write a finding with observation, evidence, impact, severity rationale, owner, corrective action, and revalidation test. Do not invent an official severity scale.

#### I-04 — Advanced — Defense under challenge
A reviewer asks: “Why did you choose this architecture instead of the simpler alternative, and what would make you change your mind?” Structure a defense using requirements, options, criteria, decision, trade-offs, residual risks, evidence, and revisit triggers. How should you respond if evidence is incomplete?

#### I-05 — Advanced — Missing official rubric
The actual capstone rubric is unavailable. What can you responsibly do to prepare, and what must you not do? Explain how to create a provisional supporting checklist without presenting its categories, weights, statuses, or pass thresholds as official.

### J. Cross-Case Architecture Comparison

#### J-01 — Beginner — Freshness versus correctness
Compare freshness and correctness needs in banking, fraud/risk, lakehouse modernization, and governed RAG. What must each define before “fresh enough” or “correct” can be tested? Why is one universal freshness target weak?

#### J-02 — Intermediate — Transfer a pattern carefully
A team proposes reusing the event-streaming pattern from Case 03 for a lakehouse migration in Case 04. Identify the original decision’s forces, compare the new case’s forces, state what transfers and what changes, and name validation evidence needed before adoption.

#### J-03 — Intermediate — Portability and governance
Compare portability in Case 05 with lineage and permission concerns in Case 06. Identify a shared governance principle and explain why portable file formats or embeddings do not automatically make identity, policy, metadata, or operations portable.

#### J-04 — Advanced — Decision matrix
Compare a centralized data platform, domain-oriented data products, multi-cloud, and a governed RAG serving layer using criteria such as correctness, freshness, latency, governance, resilience, portability, cost, and operational complexity. Treat these as potentially coexisting patterns at different architectural layers, not automatically as mutually exclusive options. How would you structure the comparison, avoid double-counting criteria, and prevent mandatory requirements from being hidden inside a weighted score?

#### J-05 — Advanced — Reject inappropriate transfer
One reviewer argues that active-active multi-cloud improves availability, so every case should use it. Another argues that Customer 360 needs a golden record, so every domain should centralize all data in one master. Refute both using scenario forces, costs, failure modes, ownership, and evidence.

### K. Integrated Capstone Questions

#### K-01 — Beginner — Choose relevant case lenses
An illustrative brief describes a regulated enterprise needing daily reporting, a unified customer view, and a knowledge assistant over internal documents. Which cases are directly relevant, which may apply only to selected concerns, and what is still needed before architecture scope is decided?

#### K-02 — Intermediate — One coherent architecture argument
Create a high-level architecture argument for K-01. Cover source ingestion, quality/reconciliation, customer identity, governed serving, document ingestion/retrieval, permissions, lineage, monitoring, resilience, and cost. Explain the boundary between shared platform capabilities and workload-specific components.

#### K-03 — Intermediate — Resolve competing goals
An illustrative capstone has four goals: fast fraud decisions, high-confidence customer matching, low-cost batch reporting, and permission-aware knowledge retrieval. Which goals need different paths or service levels? How should conflicts be resolved, and which assumptions need validation against the real brief?

#### K-04 — Advanced — Integrated failure scenario
During a release, an identity change creates incorrect customer links; a late risk event is replayed; a source dataset fails reconciliation; and a document permission is revoked while its chunks remain indexed. Produce a coordinated response covering containment, blast radius, rollback/correction, idempotent replay, downstream impact, permission enforcement, communication, evidence preservation, and revalidation.

#### K-05 — Advanced — Capstone defense and retest plan
Defend an architecture combining ideas from at least three case studies. Explain selected patterns, rejected alternatives, requirement coverage, evidence, residual risks, and redesign triggers. Finish with a retest plan for your three largest knowledge gaps.

## 1.1 Question-to-roadmap traceability matrix

The mapping below ties every question to the module roadmap’s learning outcomes and topic objectives. Objective descriptions are concise paraphrases of the roadmap, not separate official assessment criteria. Difficulty labels are instructional design choices. For the case studies, the mapping uses the relevant objectives in roadmap Sections E.1–E.6; Topics 07–08 map to Sections F.2 and G.2; cross-case and integrated questions map to the module outcomes in Section B and cross-case integration in Sections H–I.

| Question ID | Topic | Relevant learning objective | Difficulty |
|---|---|---|---|
| A-01 | Core foundations | Extract/classify business objectives, functional requirements, constraints, and stakeholders | Beginner |
| A-02 | Core foundations | Separate source facts, assumptions, constraints, risks, and unknowns | Intermediate |
| A-03 | Core foundations | Evaluate quality-attribute conflicts and make approved trade-offs explicit | Intermediate |
| A-04 | Core foundations | Compare architecture alternatives and document rationale, risks, and evidence | Advanced |
| A-05 | Core foundations | Trace a requirement through design, deliverables, tests, evidence, result, and owner | Advanced |
| B-01 | Case 01 — Banking | Map sources, ingestion, validation, storage/processing, serving, consumers, and controls | Beginner |
| B-02 | Case 01 — Banking | Evaluate reconciliation and data-quality evidence; distinguish counts from correctness | Intermediate |
| B-03 | Case 01 — Banking | Evaluate governance/security controls across ingestion and serving | Intermediate |
| B-04 | Case 01 — Banking | Evaluate resilience, recovery objectives, replication, replay, and cost trade-offs | Advanced |
| B-05 | Case 01 — Banking | Compare architecture alternatives using requirements and evidence | Advanced |
| C-01 | Case 02 — Customer 360 | Explain source records, identity resolution, golden records, and consumer views | Beginner |
| C-02 | Case 02 — Customer 360 | Evaluate entity-matching signals, uncertainty, and safe merge thresholds | Intermediate |
| C-03 | Case 02 — Customer 360 | Design field-level survivorship using authority, provenance, recency, and validation | Intermediate |
| C-04 | Case 02 — Customer 360 | Analyse false merges, missed matches, correction, ownership, and quality measures | Advanced |
| C-05 | Case 02 — Customer 360 | Trace consent/purpose changes through lineage and downstream use under actual policy | Advanced |
| D-01 | Case 03 — Fraud/risk | Explain event time, processing time, ordering, late events, replay, and idempotency | Beginner |
| D-02 | Case 03 — Fraud/risk | Translate latency requirements into a budget and interpret p99 evidence | Intermediate |
| D-03 | Case 03 — Fraud/risk | Design duplicate/late-event handling, replay safety, and business correction semantics | Intermediate |
| D-04 | Case 03 — Fraud/risk | Calculate peak capacity with headroom and identify required performance validation | Advanced |
| D-05 | Case 03 — Fraud/risk | Evaluate false-positive/false-negative trade-offs and degraded failure behaviour | Advanced |
| E-01 | Case 04 — Lakehouse modernization | Document evidence-based current state and limitations | Beginner |
| E-02 | Case 04 — Lakehouse modernization | Compare incremental, lakehouse, and hybrid alternatives against fixed criteria | Intermediate |
| E-03 | Case 04 — Lakehouse modernization | Calculate reconciliation variance and investigate semantic/timing causes | Intermediate |
| E-04 | Case 04 — Lakehouse modernization | Sequence migration, coexistence, acceptance, rollback, and decommissioning | Advanced |
| E-05 | Case 04 — Lakehouse modernization | Defend safe cutover using dependency, rollback, and exit evidence | Advanced |
| F-01 | Case 05 — Multi-cloud | Extract multi-cloud drivers and compare with single-cloud/hybrid alternatives | Beginner |
| F-02 | Case 05 — Multi-cloud | Assess portability and provider dependence by architectural layer | Intermediate |
| F-03 | Case 05 — Multi-cloud | Design cross-cloud transfer controls for identity, policy, security, and integrity | Intermediate |
| F-04 | Case 05 — Multi-cloud | Calculate an illustrative data-transfer charge and delimit TCO claims | Advanced |
| F-05 | Case 05 — Multi-cloud | Compare multi-cloud resilience alternatives against RTO/RPO, consistency, and cost | Advanced |
| G-01 | Case 06 — Governed RAG | Map source-to-answer lifecycle, lineage, versions, freshness, and deletion | Beginner |
| G-02 | Case 06 — Governed RAG | Evaluate chunking/retrieval trade-offs with representative-query evidence | Intermediate |
| G-03 | Case 06 — Governed RAG | Enforce current authorization and validate revocation across indexes/caches | Intermediate |
| G-04 | Case 06 — Governed RAG | Apply trust-boundary controls against prompt injection and unauthorized actions | Advanced |
| G-05 | Case 06 — Governed RAG | Validate relevance, grounding, citations, permissions, freshness, and failure handling | Advanced |
| H-01 | Topic 07 — Capstone requirements | Extract scope, constraints, requirements, risks, dependencies, and named deliverables from the controlling brief | Beginner |
| H-02 | Topic 07 — Capstone requirements | Trace a requirement to architecture response, deliverable, validation evidence, owner, and status | Intermediate |
| H-03 | Topic 07 — Capstone requirements | Sequence artefacts and distinguish required deliverables from recommendations | Intermediate |
| H-04 | Topic 07 — Capstone requirements | Resolve ambiguous targets through authorised clarification and explicit provisional assumptions | Advanced |
| H-05 | Topic 07 — Capstone requirements | Define requirement-specific validation criteria, tests, ownership, and evidence location | Advanced |
| I-01 | Topic 08 — Validation/defense | Distinguish verification, validation, and architecture defense | Beginner |
| I-02 | Topic 08 — Validation/defense | Audit unsupported performance, availability, and compliance claims | Intermediate |
| I-03 | Topic 08 — Validation/defense | Record a finding, evidence, impact, owner, corrective action, and revalidation | Intermediate |
| I-04 | Topic 08 — Validation/defense | Defend decisions and disclose incomplete evidence under reviewer challenge | Advanced |
| I-05 | Topic 08 — Validation/defense | Prepare responsibly when the official rubric is unavailable without inventing criteria | Advanced |
| J-01 | Cross-case comparison | Compare freshness/correctness forces and define measurable acceptance boundaries | Beginner |
| J-02 | Cross-case comparison | Transfer a pattern only after comparing original and new forces and validation needs | Intermediate |
| J-03 | Cross-case comparison | Compare portability with end-to-end governance, identity, lineage, and deletion needs | Intermediate |
| J-04 | Cross-case comparison | Structure an architecture decision matrix without false exclusivity or double-counting | Advanced |
| J-05 | Cross-case comparison | Reject inappropriate pattern transfer using scenario-specific forces and evidence | Advanced |
| K-01 | Integrated capstone | Select relevant case-study lenses while keeping scope and assumptions open | Beginner |
| K-02 | Integrated capstone | Integrate shared platform capabilities with workload-specific architecture paths | Intermediate |
| K-03 | Integrated capstone | Resolve competing workload goals through service levels, criteria, and owner approval | Intermediate |
| K-04 | Integrated capstone | Coordinate containment, correction, replay, reconciliation, access revocation, and revalidation | Advanced |
| K-05 | Integrated capstone | Defend an integrated design, explain alternatives/risks, and plan evidence-based retests | Advanced |

---

## 2. Answer Key and Worked Guidance

> These are answer guides, not single mandatory designs. A strong response is traceable to the question’s facts, makes assumptions explicit, evaluates alternatives against criteria, explains trade-offs, and proposes evidence. The actual capstone brief and authorised rubric take precedence once accessible.

### A. Core Architecture Foundations

**A-01.** “Trusted daily reporting” is the business objective; “daily” is also a frequency requirement that needs a defined delivery window and time zone. “From two existing source systems” establishes source scope. “The sources must remain in place” is a constraint. “Reports should be available” is a functional requirement, while “operations managers” identifies the consumer/stakeholder group. Define “trusted” and its acceptance evidence before treating it as testable. Open questions include report definitions, delivery window/time zone, source formats and change behaviour, volume/growth, freshness, consumer roles/sensitive fields, retention, recovery, ownership, budget, and acceptance method. Validate through source-owner and consumer agreement; do not assume a product/cloud.

**A-02.** Use separate fields for type, statement, source location, owner, confidence/status, and next action. Confirm only what the source states. “Cloud lakehouse” is a solution proposal unless mandated by the brief. Record it as an option/hypothesis and compare it with requirements and constraints. Unknown values remain open questions or explicit assumptions with an owner and validation date.

**A-03.** Freshness describes how recently data reflects relevant events; correctness includes semantic validity, completeness, consistency, and reconciliation; cost is the spend required to meet the service. Lower latency may require more stateful infrastructure; stronger reconciliation may delay publication. Clarify mandatory requirements, segment service levels only where legitimate, compare alternatives against agreed criteria, quantify where possible, record approved trade-offs in an ADR, and validate with tests. Do not turn a requirement into a preference without approval.

**A-04.** An ADR records context, confirmed requirements, constraints, alternatives, criteria, decision, rationale, consequences, risks, evidence, and revisit triggers. Centralization can fit when common governance, consistent semantics, shared operations, and scale dominate. Domain ownership can fit when autonomy, independent release cycles, and local semantics matter and federated governance is mature. Hybrid options are valid. Evidence includes workload/consumer analysis, data ownership, service levels, integration complexity, security, cost, and operational capability. No option is universally best.

**A-05.** Example chain: requirement ID/source statement → reconciliation control → data-flow/quality design → test of source/target counts, control totals, business aggregates, and exceptions → evidence artifact/result → named owner. If evidence is unavailable, mark “not yet verified” or the rubric’s actual equivalent, state why, assign remediation, and disclose the limitation. A diagram mentioning reconciliation is not proof that reconciliation works.

### B. Banking Data Platform

**B-01.** A reasonable logical flow is sources → controlled ingestion/landing → schema and quality checks → governed storage/processing → curated data products/warehouse/lakehouse → authorised serving → consumers. Attach ownership, classification/policy, lineage/run metadata, and metrics/alerts at relevant boundaries. Include reject/quarantine and replay/recovery paths. A logical flow does not mandate a vendor or deployment topology.

**B-02.** The curated output contains 1,300 fewer records than the source extract: `1,200,000 − 1,198,700 = 1,300` records. The difference may reflect legitimate filters, rejects, duplicates, or scope changes, but each disposition needs explanation. Check source/target control totals, unique keys, duplicates, nulls, schema and semantic transformations, quarantined rows, late arrivals, updates/deletes, business aggregates, run boundaries, lineage, and approvals. Equal counts can hide corrupted/swapped values; unequal counts are acceptable only when the contract and evidence explain them.

**B-03.** Use classification, purpose-based least privilege, role/attribute policies, service identities, appropriate separation of duties, encryption/key governance, masking/restricted views, access/change audit, lineage, and retention/deletion rules. Ingestion controls validate provenance, schema, classification, and quality. Serving must re-check current identity, purpose, row/column restrictions, and policy because permissions change. Exact legal controls depend on real obligations.

**B-04.** Clarify dataset criticality, recovery time/point, acceptable loss, consistency, failure domains, regional dependencies, and budget. Synchronous replication may reduce acknowledged-write loss but adds latency and can couple availability to both regions. Asynchronous replication reduces write-path latency but allows lag. Backup/restore may cost less but recover more slowly; replay can rebuild derived data only if durable complete source events and deterministic processing exist. Tier data by need and test recovery. Record cost, consistency, latency, and complexity in an ADR.

**B-05.** Centralization may simplify shared controls, discovery, semantics, and operations, but can create bottlenecks, broad blast radius, unclear ownership, and a one-size-fits-all serving path. Domain components may fit distinct latency, access, ownership, or operations needs, but increase integration/governance demands. Decide from requirements, domains, service levels, boundaries, skills, isolation, cost, and recovery evidence. Require explicit alternatives, not slogans.

### C. Customer 360 and Master Data

**C-01.** A source record is an operational system’s representation. An identity-resolution result determines whether records refer to the same entity and should retain evidence/status. A golden record is a governed representation with explicit survivorship and provenance. A Customer 360 view is consumer-oriented and may combine mastered attributes with current source facts. They differ in authority, lifecycle, write behaviour, provenance, and purpose.

**C-02.** Deterministic matching may use exact email equality if policy treats the email as reliable and unique. Probabilistic matching combines weighted signals; name similarity and phone mismatch increase uncertainty. Before auto-merge, check identifier verification/uniqueness, shared or household email, source trust, recency, aliases, conflicting strong identifiers, and false-merge cost. A reversible candidate link or manual review may be safer. A score is not a calibrated probability unless validated; thresholds require labelled examples and business-cost analysis.

**C-03.** Define field-level authority, source quality, verification, recency, allowed transformations, conflict handling, and provenance. Prefer a verified authoritative value over a newer unverified value where policy supports that; preserve losing values and history. “Latest wins” can promote typos, stale replay, untrusted sources, or malicious updates. Validate using conflict tests, historical replay, owner review, and correction scenarios.

**C-04.** A false merge combines unrelated people and can expose data or trigger wrong decisions; detect via conflicting strong identifiers, reports, anomalies, and review queues. Correct through controlled split/unmerge, before/after evidence, downstream remapping, and impact analysis. A missed match fragments a person’s view; detect through candidate queues and quality metrics, then merge under approved rules. Auto-resolve only where evidence and impact justify it; high-impact ambiguity requires review. Measure both false merges and missed matches.

**C-05.** Use consent/purpose metadata and lineage to find records, mastered attributes, derived datasets, views, caches, exports, and consumers. Apply the actual policy, invalidate affected paths, notify downstream owners, retain appropriate audit evidence, and test that use no longer violates policy. Depending on law and approved policy, the response may be stop-use, delete, suppress, or retain restricted evidence under another basis. No generic workflow guarantees compliance in every jurisdiction.

### D. Real-Time Fraud and Risk

**D-01.** Event time is when the business event occurred; processing time is when the system handles it. Ordering can mean source, partition, event-time, or causal order. A late event arrives after progress past its event-time window. Replay reprocesses retained events; idempotency makes repeated processing safe for defined effects. Misassigning late transactions to processing-time windows can distort velocity features. Define event contracts, clock assumptions, window/watermark policy, and correction semantics.

**D-02.** Allocated total: `35 + 70 + 80 + 25 + 20 = 230 ms`. Remaining against 250 ms: `250 − 230 = 20 ms`, assuming additive allocations and the same measurement boundary. Observed p99 of 285 ms exceeds target by 35 ms. Arithmetic reveals a budget issue, not its cause. Check whether allocations are p99 or averages, overlap, measurement boundaries, queue/network time, warm/cold paths, sampling, and tail correlation. Use traces and representative load tests.

**D-03.** Use stable event IDs/idempotency keys and a deduplication store/window aligned to replay/business semantics. Keep event and processing timestamps; define event-time windows, watermarks, late-event corrections, state/feature versions, and idempotent or compensatable actions. Whether a 90-second-late event reverses a prior decision is a business policy, not just a broker setting. Make replay observable, bounded, and safe with concurrent live traffic.

**D-04.** Peak: `4,000 × 3 = 12,000 events/s`. Add 30% headroom: `12,000 × 1.30 = 15,600 events/s`. This is a planning estimate, not proof of p99 latency, state-store performance, partition balance, dependency capacity, event-size handling, recovery behaviour, or cost. Validate with representative load, burst, skew, failure, and replay tests.

**D-05.** False positives block legitimate activity and increase friction/review work; false negatives allow harmful activity and losses. Evaluate precision, recall, false-positive/negative rates, calibration, relevant segments, latency, review capacity, and drift. Choose metrics with risk owners. On dependency failure, possible policies include conservative rules, step-up verification, manual review, bounded degradation, or fail open/closed by risk class. Define and test behaviour; overall accuracy alone can mislead on imbalanced data.

### E. Lakehouse Modernization

**E-01.** Collect systems/owners, consumers/critical reports, lineage, volumes/growth, formats/schemas, quality, SLAs, access, workloads, dependencies, costs, incidents, recovery, contracts, retention, and pain points. A target diagram does not prove migration feasibility, semantic equivalence, compatibility, cost benefit, operating readiness, or rollback. Validate with current-state evidence, gap analysis, workload options, migration waves, reconciliation, and owner acceptance.

**E-02.** Incremental improvement lowers change risk but may preserve structural limits. Lakehouse migration may unify data/processing but brings migration, format, governance, and skills risks. Hybrid coexistence permits phases but increases dual-run cost and source-of-truth complexity. Set criteria such as value, fit, correctness, migration risk, performance, skills, governance, recovery, and TCO before scoring. Unknowns include compatibility, semantic discrepancies, volume, contracts, downtime tolerance, and actual cost.

**E-03.** Absolute difference: `8,450,000 − 8,427,500 = 22,500`. Percentage: `22,500 / 8,450,000 × 100 ≈ 0.2663%` (about 0.27%). Investigate time-zone/period boundaries, snapshots, late data, currency/rounding, filters, joins, duplicate handling, null semantics, definitions, deletes/updates, and transformation versions. Reconcile at finer grains. A small percentage is not automatically acceptable; tolerance must come from an approved requirement or business owner.

**E-04.** Inventory dependencies and classify waves by risk/value. Establish contracts, backfill/incremental sync, parallel run, compare counts and business aggregates, test quality/access, obtain consumer sign-off, define cutover and rollback triggers, and retain a known-good legacy path until exit criteria pass. Avoid split-brain by defining one authoritative write path per entity/workload, replication direction, conflict policy, and owner. Decommission only after evidence and retention/recovery/dependency review.

**E-05.** Risks include incomplete reconciliation, hidden dependencies, cutover sequencing, access gaps, performance regressions, rollback incompatibility, untested recovery, and loss of comparison evidence. Prefer canary/wave cutover where feasible, parallel run, rehearsed rollback, contracts, monitoring, sign-off, and an agreed decision window. Keep the old platform until exit criteria and rollback feasibility are demonstrated. An authorised owner accepts residual risk; a date alone is not readiness evidence.

### F. Multi-Cloud

**F-01.** Possible drivers include verified regulatory/contractual constraints, specific resilience needs, acquisitions, required provider capabilities, placement needs, or negotiating leverage. A single cloud may be preferable when it meets requirements with lower cost, simpler identity/governance, less movement, and stronger operational focus. Multi-cloud adds networking, egress, identity, observability, skills, support, and consistency complexity. Turn “avoid lock-in” into a concrete requirement and compare lifecycle costs.

**F-02.** Assess each layer separately. Open formats and portable deployment artefacts help, but managed services may embed provider APIs, IAM semantics, catalogue features, query behaviour, event delivery, observability, and recovery procedures. Classify as portable, portable with adaptation, or provider-dependent; record migration effort and test evidence. File-format portability does not make orchestration, identity, policy, or operations portable.

**F-03.** Define classification and transfer purpose/authorisation first. Then specify trusted network paths, identity federation/least privilege, encryption, key ownership/rotation, destination controls, residency, audit, transfer integrity, retries, idempotency, and recovery. Encryption protects data under stated assumptions; it does not establish legal authority, business purpose, destination entitlement, or policy compliance. Validate with access, transfer, key, failure, and owner-approval evidence.

**F-04.** Decimal units: `18 TB × 1,000 GB/TB = 18,000 GB`. Charge: `18,000 × $0.07 = $1,260/month`. This excludes other network paths, ingress/egress differences, requests, storage, compute, replication, support, monitoring, taxes, and labour. The rate is illustrative, not a current provider quote; real estimates need applicable pricing and actual billable paths.

**F-05.** Active-active may suit strict availability/latency needs if consistency, duplicate processing, identity, routing, and operations are solved; it is usually most complex. Active-passive may meet recovery goals with less routine complexity but needs tested failover and data/dependency readiness. Primary cloud with tested backups/portable artefacts may suffice if recovery objectives allow. Compare verified RTO/RPO, criticality, consistency, provider failure modes, tests, staff readiness, TCO, and residual risk.

### G. Governed RAG and Enterprise Knowledge

**G-01.** Track source identity/version, ingestion run, parsing outcome, chunk IDs/source spans, metadata and ACL version, embedding/model/index version, retrieval trace, answer/citation mapping, and update/deletion state. Freshness can be measured from source modification to index visibility; lineage should trace a cited chunk back to source and processing version. Include quarantine/retry and removal paths. Embeddings are not authoritative source records.

**G-02.** Small chunks may improve precision but lose context and increase index size; large chunks preserve context but may dilute relevance and make citations less precise. Overlap reduces boundary loss but adds duplication/cost. Structure-aware parsing and metadata filters preserve sections and narrow scope. Evaluate representative queries with labelled relevance and measure retrieval precision/recall, groundedness, citation quality, latency, and cost. Segment by document/query type instead of optimizing one aggregate score.

**G-03.** Use current authoritative authorization checks or an equivalently reliable permission-aware retrieval mechanism, not only a stale ACL snapshot. Revoke access promptly, invalidate caches, remove/mark chunks for exclusion, refresh/rebuild as needed, and test with the formerly authorised identity. Ensure no alternate path exposes unfiltered chunks. Hiding the citation does not undo disclosure in the answer. Preserve enough audit metadata to verify propagation while minimizing sensitive logging.

**G-04.** Retrieved documents are untrusted content, not system-authority instructions. Keep policy/tool permissions outside retrieved text; delimit or label content; constrain tools through independent authorization; test with prompt-injection corpora; validate outputs and citations; monitor suspicious instructions. Prompt wording alone is not a security boundary. Test that injected content cannot change access rights, invoke unauthorized tools, or disclose out-of-scope data.

**G-05.** Test retrieval relevance, grounded support, citation/source correctness, permissions, revocation/deletion, freshness, injection, latency, timeouts, empty retrieval, and model/index failures. Use expected-document test sets and adversarial queries; separate retrieval metrics from generation metrics. Retain correlation IDs, policy/index/model versions, retrieved IDs/scores, and redacted or access-controlled traces. Avoid raw prompt/document logging when it exposes sensitive data; define retention and diagnostic access controls.

### H. Capstone Requirements and Deliverables

**H-01.** Inspect the current brief, rubric/evaluation instructions, appendices, linked project files, and authorised clarifications; verify version/date and precedence. Extract each category with source location and status. Include sponsor, data owners, operators, governance/security reviewers, and consumers as relevant. Deliverables explicitly named by the brief are confirmed requirements; extra diagrams/registers are recommendations unless required or adopted. Keep ambiguity visible.

**H-02.** Illustrative row: `REQ-SEC-01`; source: hypothetical brief paragraph 3; requirement: only authorised consumers access sensitive data; response: authenticated identities, least-privilege policy, sensitive-field controls, audit, and serving-time enforcement; deliverable: logical security/data-flow diagram plus access matrix; evidence: allowed/denied role and field tests, policy-change/revocation test, audit review; owner: security/data owner; status: not verified until tests pass. A diagram alone is not test evidence.

**H-03.** A plausible sequence is source/brief confirmation → requirement register → context and data-flow analysis → logical flow diagram → options and ADRs → migration plan → validation plan/evidence. Iteration is expected; an ADR can reveal missing requirements. Glossary, lineage matrix, threat model, and cost model may be useful supporting artefacts, but are not mandatory unless the brief says so or the project explicitly adopts them.

**H-04.** Ask the sponsor to define freshness boundary/measurement, acceptable stale behaviour, critical consumers, recovery time/point, failure scope, budget, and who can approve trade-offs. Record “near real-time” as ambiguous, not measurable. If a provisional assumption is needed, label it, name owner/date, describe consequence if wrong, and specify validation. Keep dependent design decisions conditional and compliance not verified until clarified and tested.

**H-05.** For each requirement, map source/ID to design response, artefact section, test method/data, acceptance criteria from the controlling source, owner, evidence location, and status. Include positive/negative and relevant failure/recovery tests. If evidence is unavailable, state reason, impact, owner, and next action. A deliverable inventory proves only that an artefact exists, not that its content is correct or requirement satisfied.

### I. Capstone Validation and Defense

**I-01.** Verification checks an artefact/implementation against specification and internal consistency, e.g. required diagrams exist and their flows agree. Validation checks whether the architecture meets the actual business need, e.g. workload evidence demonstrates the specified freshness target. Defense explains decisions, alternatives, limits, and evidence to a reviewer. Completion is not validation.

**I-02.** “99.99% availability” needs a defined service boundary, measurement window, numerator/denominator, exclusions, monitoring source, dependency assumptions, and evidence or a clearly labelled target. “Sub-second response” needs request boundary, percentile, load, data size, and test results. “Full compliance” needs applicable obligations, control mapping, approver, evidence, and any required independent review. Until then rewrite as proposed/unverified targets or claims, not proven outcomes.

**I-03.** Example finding: **Observation:** diagram shows one mastered customer while the model permits independent writes to two golden records. **Evidence:** cite diagram/model elements. **Impact:** conflicting masters, inconsistent views, unclear survivorship. **Severity rationale:** describe impact/scope under a locally agreed scheme; do not invent official labels. **Owner:** data-domain/architecture owner. **Action:** define one authoritative mastering path or explicit field/domain authority; revise model/permissions; repair conflicts and document policy. **Revalidation:** test concurrent updates, survivorship, duplicate-master prevention, lineage, and downstream consistency.

**I-04.** Restate requirements/constraints; compare viable alternatives against agreed criteria; explain decision and trade-offs; name rejected alternatives and why; identify residual risks/owners; show evidence/limits; state revisit triggers. If evidence is incomplete, say so, explain the consequence, assign remediation, and do not claim the requirement is met. A credible defense acknowledges uncertainty.

**I-05.** Responsible preparation includes reviewing Topics 07–08, building a provisional requirement/evidence matrix, using a supporting quality checklist, rehearsing decision explanations, and marking official criteria unavailable. Do not invent weights, gates, pass marks, official severity labels, or claim a provisional checklist reproduces the rubric. When the real rubric is accessible, copy its criteria faithfully, map evidence, and resolve ambiguity with the authorised source.

### J. Cross-Case Architecture Comparison

**J-01.** Banking needs correctness/traceability/reconciliation tied to report definitions. Fraud/risk needs bounded decision latency while handling late/duplicate events and risk trade-offs. Lakehouse modernization needs semantic equivalence and controlled cutover, not just a fresh target. Governed RAG needs source freshness, retrieval relevance, current permissions, and answer/source traceability. Each must define boundary, measurement, percentile/window where relevant, and acceptance owner. One target ignores different consequences and architectures.

**J-02.** Record why streaming was selected in Case 03: event pattern, latency, state, ordering, and response. Compare Case 04’s forces: batch/backfill, historical reconciliation, consumer cutover, coexistence, rollback. Streaming may help CDC/incremental sync but does not replace bulk backfill, reconciliation, semantic comparison, or migration governance. Validate end-to-end consistency, lag, replay, cutover, and rollback; choose batch/streaming/hybrid per requirement.

**J-03.** Multi-cloud portability asks whether identity, data, APIs, governance, and operations behave consistently across providers. Governed RAG asks whether current permissions and lineage survive chunks, indexes, caches, retrieval, and generation. Shared principle: policy and provenance must be explicit and tested end-to-end. File/embedding portability does not migrate ACL semantics, key ownership, source lineage, deletion behaviour, or runbooks.

**J-04.** First separate architectural dimensions: centralization versus domain ownership describes ownership/topology; multi-cloud describes deployment/provider placement; governed RAG is a workload-specific serving capability. They can coexist, so do not score them as if they were necessarily competing whole-system alternatives. Compare coherent end-to-end options or evaluate each dimension against the same requirements and interfaces. Define criteria before scoring; avoid counting “operational simplicity” and “low complexity” as separate benefits if they mean the same thing. Treat mandatory constraints as gates, not merely low weighted scores. Use weights only when the decision authority agrees them; otherwise compare qualitatively or use sensitivity analysis. Include lifecycle cost and people/operations, not just service price. Test realistic workload, governance, failure, and recovery cases.

**J-05.** Active-active multi-cloud improves availability only if dependencies, consistency, identity, routing, and recovery are designed and tested; it adds failure modes and cost. Customer 360 may need governed mastering for selected attributes, not central ownership of every source fact/domain. Evaluate actual risk, semantics, source authority, locality, ownership, recovery, and cost. Transfer a pattern only when forces match; record mismatches and validation in an ADR.

### K. Integrated Capstone

**K-01.** Banking/platform principles may apply to regulated ingestion, controls, reconciliation, and reporting; Customer 360 to identity/survivorship; governed RAG to document lifecycle, permissions, citations, freshness, and evaluation. Fraud/risk is relevant only if latency-sensitive risk decisions are in scope; lakehouse modernization or multi-cloud only if current estate, migration, provider constraints, or recovery justify them. Confirm scope, consumers, data classes, volume, freshness, obligations, service levels, budget, recovery, deployment constraints, and deliverables before committing.

**K-02.** Separate shared capabilities (identity, classification, lineage, observability, quality, and storage/compute where justified) from workload-specific paths. Batch reporting may prioritize reproducibility/reconciliation; Customer 360 needs entity resolution, survivorship, provenance, and correction; RAG needs document lifecycle, chunk/index versions, current permission enforcement, citations, and evaluation. Include ownership, recovery, cost, and operating boundaries. Validate each path with requirement-specific tests, not one platform-wide success claim.

**K-03.** Fast fraud decisions may need a latency-bounded streaming/stateful path; customer matching needs high-quality resolution and review; batch reporting may trade freshness for cost/reconciliation; RAG must enforce authorization and grounding at retrieval/generation. Resolve conflicts by clarifying mandatory requirements, defining workload-specific service levels, comparing options, quantifying consequences, and obtaining owner approval. Validate numeric targets against the actual brief.

**K-04.** Contain the identity change and suspend unsafe publication; use lineage to identify affected records/consumers; preserve versions/evidence. Prevent duplicate effects during replay with event IDs/idempotency and defined correction semantics. Quarantine the unreconciled dataset and reconcile before release. Enforce permission checks immediately and invalidate/rebuild affected index/cache paths, then test as the revoked user. Coordinate owners/communications, roll back or compensate where appropriate, document impact, retest, and resume only when evidence is accepted. Order/severity depend on actual impact and policy.

**K-05.** Tie every selected pattern to a requirement and the forces it addresses; compare alternatives and explain rejected options. Example: Case 01 governance/reconciliation for trusted reporting, Case 02 mastering for a justified identity requirement, Case 06 permission-aware retrieval for internal knowledge. Include ADRs, diagrams, test evidence, lineage, cost/operations, residual risks, and revisit triggers. State what remains unverified. Select three gaps, revisit lesson/prerequisite, redo an exercise, and retest after a delay.

---

## 3. Self-Assessment Guidance — Learning Aid Only

This is not an official course rubric. No official weights, pass mark, mandatory gate, or submission rule is assigned.

- **Strong:** answers the exact question; separates facts from assumptions; applies relevant concepts; explains trade-offs/risks; names validation evidence; acknowledges uncertainty.
- **Partial:** directionally reasonable but omits a material requirement, alternative, risk, assumption, or test.
- **Needs revision:** relies on unsupported claims, misses the main requirement, confuses concepts, calculates incorrectly, or names controls without explaining enforcement/validation.

For numerical questions, check formula, units, assumptions, intermediate arithmetic, result, and interpretation separately. For open-ended questions, do not penalize a different design solely because it differs from the key; assess fit to the stated forces and credibility of trade-offs/evidence. Optional tracking can count Strong/Partial/Needs revision by topic, but it is not an official score. The roadmap’s suggested 85% overall / 70% per-case readiness check is itself labelled recommended, not a repository requirement; this document does not elevate it to an official threshold.

## 4. Reusable Knowledge-Gap Log

Use one row per material gap. Record the actual reasoning failure, not simply “did not know.”

| Question ID | Topic / source file | Difficulty | Learner answer or evidence | Gap / error type | Corrective action | Relevant lesson or prerequisite | Retest date/result | Status |
|---|---|---|---|---|---|---|---|---|
| Example: D-03 | Streaming semantics | Intermediate | Described deduplication but omitted replay safety | Idempotency and correction semantics missing | Redraw event flow; add duplicate/late-event tests | `03-case-study-real-time-fraud-and-risk-platform.md`; prerequisite module 09 | To be completed | Open |
|  |  |  |  |  |  |  |  |  |

Suggested error types: requirement missed; assumption treated as fact; incorrect concept; wrong pattern for scenario; trade-off not evaluated; calculation error; failure mode omitted; governance/security gap; evidence missing; unsupported claim; weak defense.

### How to close a gap

1. **Diagnose:** name the reasoning failure.
2. **Return to source:** read the relevant section in the named case or Topic 07/08. If foundational, revisit the prerequisite module identified in the roadmap.
3. **Redo the exercise:** create a new answer, diagram, calculation, ADR, test plan, or finding without copying the key.
4. **Validate:** compare against the key points and record what changed.
5. **Retest later:** re-attempt after several days with a slightly altered scenario. Two consecutive failures should trigger redoing the relevant case exercise, consistent with the roadmap’s recommended method.
6. **Close only with evidence:** mark closed when the learner can explain reasoning and validation, not merely repeat a definition.

## 5. Completion Checklist

### 5.1 Per-topic completion

| Topic | Lesson reviewed | Beginner attempted | Intermediate completed | Advanced defended | Artefact/evidence produced | Gaps retested | Status |
|---|---|---|---|---|---|---|---|
| Case 01 — Banking | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | Not started |
| Case 02 — Customer 360 | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | Not started |
| Case 03 — Fraud/risk | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | Not started |
| Case 04 — Lakehouse modernization | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | Not started |
| Case 05 — Multi-cloud | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | Not started |
| Case 06 — Governed RAG | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | Not started |
| Topic 07 — Requirements/deliverables | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | Not started |
| Topic 08 — Validation/defense | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | Not started |

### 5.2 Module-level readiness

- [ ] Current six case-study files and Topics 07–08 reviewed.
- [ ] Confirmed source facts distinguished from illustrative scenario details.
- [ ] Beginner, intermediate, and advanced questions attempted across A–K.
- [ ] Calculations show formulas, units, assumptions, and interpretation.
- [ ] At least two cross-case comparisons identify matching and mismatching forces.
- [ ] Requirement-to-deliverable-to-evidence traceability chain produced.
- [ ] Verification versus validation explained and at least three decisions defended.
- [ ] Knowledge-gap log current; material gaps have corrective actions and retest evidence.
- [ ] Actual capstone brief and rubric obtained and checked before finalising a real submission plan.
- [ ] Official criteria copied from controlling source rather than inferred here.
- [ ] Deliverables checked against actual brief; recommendations not mislabelled mandatory.
- [ ] Data flow, governance, operations, resilience, and cost reviewed for consistency.
- [ ] Remaining risks, limitations, assumptions, and unavailable evidence disclosed.
- [ ] Mock defense completed and reviewer challenges logged.
- [ ] No topic remains in “Needs revision” under the learner’s chosen tracking method.

Reading alone is not mastery. A topic is ready when the learner can apply the method to a changed scenario, explain why alternatives were rejected, and identify evidence that would prove or disprove the decision.

## 6. Source and Assumption Register

| Source | Use | Integrity note |
|---|---|---|
| `Roadmap_ptree(20261020-184004).md` | Confirmed Stage 2D tree and expected target file | Accessible dated copy; exact `Roadmap_ptree.md` was not among the accessible current-turn files. |
| `roadmap-Enterprise-Data-Architecture-Case-Studies-and-Capstone(1).md` | Outcomes, prerequisites, sequence, case frames, cross-case method, practice-question integration, completion checklist | Historical empty-file notes were checked against current copies. |
| `source_audit/template(20261020-112311).txt` | Source analysis and private audit/revision conventions | Accessible copy inspected; applied as an audit-process reference, not as technical authority for answer content. |
| `01-case-study-banking-data-platform.md` | Banking flow, governance, reconciliation, resilience, alternatives | Current accessible copy populated; scenario explicitly illustrative. |
| `02-case-study-customer-360-and-master-data.md` | Identity, matching, survivorship, consent, quality | Current accessible copy populated; scenario and values illustrative. |
| `03-case-study-real-time-fraud-and-risk-platform.md` | Event semantics, latency, state, replay, risk trade-offs | Current accessible copy populated; targets illustrative. |
| `04-case-study-enterprise-lakehouse-modernization.md` | Current/target state, alternatives, migration, reconciliation, rollback | Current accessible copy populated; scenario details illustrative. |
| `05-case-study-multi-cloud-data-platform.md` | Portability, placement, network/identity, cost, resilience | Current accessible copy populated; scenario/pricing assumptions illustrative. |
| `06-case-study-governed-rag-and-enterprise-knowledge.md` | Document lifecycle, permission-aware retrieval, injection, evaluation | Current accessible copy populated; scenario details illustrative. |
| `07-capstone-requirements-and-architecture-deliverables.md` | Requirement extraction, traceability, deliverables, dependencies | Current copy populated; notes current brief was not directly inspected. |
| `08-capstone-validation-defense-and-review-rubric.md` | Verification/validation, evidence, findings, remediation, defense | Current copy populated; review framework explicitly illustrative. |

### What could not be confirmed

The current contents of `Projects/16-enterprise-data-architecture-capstone.md` and any official associated rubric were not available for direct inspection. No question claims a particular domain, vendor, numeric target, artefact, or rubric criterion is mandatory. Illustrative calculations test method only. Any real submission plan must be re-anchored to the controlling brief and authorised rubric.

## 7. Final Consistency and Audit Notes

- Questions use unique IDs A-01 through K-05; all 55 have answer guidance and an individual topic/objective/difficulty mapping in Section 1.1.
- Calculations appear in B-02, D-02, D-04, E-03, and F-04; formulas, assumptions/units, results, and interpretations are included. Arithmetic was independently recalculated during this audit.
- Open-ended questions recognise alternative architectures where requirements and evidence justify them.
- No official pass mark, rubric weight, mandatory threshold, or current capstone requirement is invented.
- The brief-access limitation is disclosed; the roadmap’s historical empty-file note is not treated as proof that current lesson files are empty.
- Lesson filenames are relative to the module directory when this document is placed at the requested target.
