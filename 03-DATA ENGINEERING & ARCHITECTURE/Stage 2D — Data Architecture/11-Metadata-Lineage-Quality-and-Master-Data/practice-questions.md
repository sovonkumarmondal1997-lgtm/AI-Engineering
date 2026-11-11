# Practice Questions — Metadata, Lineage, Quality and Master Data

> **Module:** Stage 2D — Data Architecture / `11-Metadata-Lineage-Quality-and-Master-Data/`  
> **Purpose:** Topic validation, integrated assessment, and readiness for `Projects/11-enterprise-metadata-and-lineage-design.md`  
> **Scenario:** Northbridge Bank is fictional. All records, values, targets, and systems in this document are synthetic and illustrative.  
> **Tooling:** Vendor-neutral. No commercial product is required.

## Source status and interpretation

The module roadmap states that the eight topic files, `practice-questions.md`, module overview files, and `Projects/11-enterprise-metadata-and-lineage-design.md` were empty when the roadmap was authored. This document therefore **creates** the question bank from the roadmap's recommended scope; it does not claim to reproduce an existing question set or project specification. The roadmap labels its exercises, scenarios, targets, and project shape as recommendations. If the topic or project files are later populated with explicit requirements, those files take precedence and this assessment should be reconciled with them.

The recommended numeric learning order is Topics 01–08. Topic 07's beginner material should be understood before Topic 06's advanced golden-record work because entity resolution and identifiers underpin survivorship. An optional preview of Topic 08 may follow Topic 02.

---

# Section A — Assessment guide

## A1. How to use this bank

1. **Before a topic:** skim its questions to identify unfamiliar terms; do not grade yourself yet.
2. **After a topic:** attempt its foundational and applied questions closed-book, then use the answer key to diagnose gaps.
3. **After Topics 1–3:** attempt a mixed foundation review covering metadata, catalogues, lineage, and impact.
4. **After Topics 4–5:** review quality dimensions, critical data elements (CDEs), observability, indicators, and service-level objectives (SLOs).
5. **After Topics 6–8:** review identifiers, matching, master data, survivorship, and interoperability.
6. **Before the final project:** complete the practical exercises and integrated scenarios, score the assessment, close material gaps, and verify topic gates.
7. **After the project:** reattempt missed questions without looking at the previous answers and use reviewer feedback to update the gap log.

### Closed-book and open-book modes

- **Closed-book mode** tests recall, distinctions, reasoning, and the ability to calculate from supplied inputs. Do not consult notes while answering.
- **Open-book mode** tests professional practice: cite the relevant topic file or roadmap section, state assumptions, and show evidence. Open-book does not mean copying a definition without applying it.
- For architecture questions, there may be more than one defensible answer. Full credit requires explicit constraints, alternatives, trade-offs, risks, ownership, and validation—not merely choosing the same option as the reference answer.
- For calculations, show formula, inputs, intermediate steps, units/denominator, result, and interpretation.

## A2. Answer quality and scoring

Use the following holistic **0–3 score for each Section B question**. Subparts are evidence used to assign that one question score; do not add a separate 0–3 score for every bullet or subpart. This keeps the primary question-bank denominator stable at 40 questions × 3 points = **120 points**.

| Score | Standard |
|---:|---|
| 0 | Missing, fundamentally incorrect, or unsafe conclusion |
| 1 | Partly correct; important distinction, evidence, or step missing |
| 2 | Correct core answer with adequate reasoning |
| 3 | Correct, well-reasoned, applied answer with assumptions, limitations, and validation where relevant |

`Section B score (%) = points earned across T01-Q1 through T08-Q5 / 120 × 100`

Calculate each topic score separately from its five questions (maximum 15 points per topic). Section C practical exercises are evidence-based completion gates, and Section D integrated scenarios use their explicit rubrics; **do not blend their points into the Section B percentage** unless a reviewer documents a weighting scheme before grading. This avoids changing the denominator or double-counting the same evidence. Record a one-sentence reason for every Section B question scored below 3.

**Recommended readiness guide from the module roadmap:** at least **85% overall** (at least 102/120 on this Section B scale), no topic below **70%**, all eight topic gates completed, the D1 integrated exercise completed, and no unresolved gap older than one week. These are **recommended study thresholds**, not universal industry standards or mandatory repository rules. A reviewer may set stricter thresholds for a high-risk use case.

## A3. Gap-log workflow

For every partly correct or incorrect answer:

1. Record the question ID, topic, and the specific misconception—not only “need more study.”
2. Revisit the mapped topic file and the corresponding roadmap learning objective.
3. Complete a small remediation task (e.g., redraw a lineage chain, rewrite a rule, or recompute matching metrics).
4. Set a reattempt date several days later and attempt the question without the answer key.
5. If the same question or concept fails twice, redo the topic's hands-on exercise and ask a reviewer to inspect the evidence.
6. Keep the gap open until a reattempt and its evidence are recorded.

Use the exact topic file names below to route remediation. Integrated questions map to multiple topic files and the final-project design.

## A4. Topic index and recommended evidence

| Topic | Main competency | Evidence to retain |
|---|---|---|
| 01 — Business, technical and operational metadata | Categorize, model, own, maintain metadata | Metadata inventory, schema, ownership and metadata-quality checks |
| 02 — Catalogues, discovery and classification | Make assets discoverable and appropriately classified | Logical catalogue design, persona journey, classification workflow |
| 03 — End-to-end lineage and impact analysis | Trace dependencies and assess change impact | Lineage diagram, edge register, impact report, blind-spot list |
| 04 — Quality dimensions and CDEs | Define measurable fitness-for-use rules | CDE register, rule inventory, computed quality report |
| 05 — Observability and quality service levels | Detect meaningful changes and operate SLOs | Indicator register, SLI/SLO table, alert and incident procedure |
| 06 — MDM and golden records | Govern entity values and lifecycle | Golden-record model, survivorship rules, sync and unmerge design |
| 07 — Reference data, entity resolution and identifiers | Govern codes/IDs and evaluate matching | Reference mappings, identifier policy, matching evaluation |
| 08 — Standards and interoperability | Preserve meaning when metadata moves between systems | Mapping specification, conformance report, compatibility tests |

---

# Section B — Topic-by-topic question bank

Attempt the questions before reading Section E. Each question lists its intended level and learning objective.

## Topic 01 — Business, technical and operational metadata

Source: `01-business-technical-and-operational-metadata.md`

### T01-Q1 — Classify metadata (Foundational)
**Objective:** Distinguish business, technical, and operational metadata.

Classify each item as primarily business, technical, or operational metadata, and state whether collection is usually human-led, automated, or mixed:

1. Definition of “active customer”
2. `customer_id` data type and nullability
3. Timestamp of the last successful load
4. Business owner and steward
5. Current row count and job status
6. Table storage location
7. Classification label and permitted purpose
8. Data-quality rule result for the latest run

### T01-Q2 — Model the inventory (Applied)
**Objective:** Design useful metadata fields and accountability.

Design a compact inventory for a synthetic `curated.customer` dataset. Include at least ten fields spanning all three metadata categories, an identifier for the asset, the source of each metadata value, a maintainer, and a refresh/maintenance policy. Explain how you represent unknown or stale metadata without silently treating it as valid.

### T01-Q3 — Ownership and lifecycle (Scenario)
**Objective:** Separate accountability from technical maintenance.

A scanner detects a new column `risk_band` in a customer table. The pipeline team knows the type and source table, but nobody knows its business definition or classification. Who should do what? Describe the discovery, review, approval, update, and retirement lifecycle. What should happen before the column is exposed to broad discovery?

### T01-Q4 — Metadata quality (Technical)
**Objective:** Define measurable metadata quality checks.

Define three metadata-quality checks for an inventory of 200 assets. At least one check must assess completeness and one must assess consistency. State numerator, denominator, exclusion rules, owner, and remediation. Explain why “metadata completeness = 100%” is meaningless unless required fields and eligible assets are defined.

### T01-Q5 — Architecture trade-off (Advanced)
**Objective:** Defend collection and governance choices.

Compare scanner-generated metadata, steward-curated metadata, and a hybrid approach. Discuss freshness, semantic correctness, operational cost, failure modes, ownership, and evidence. Recommend an approach for a large estate where schemas change daily but business definitions change less often.

---

## Topic 02 — Data catalogues, discovery and classification

Source: `02-data-catalogs-discovery-and-classification.md`

### T02-Q1 — Catalogue vs metastore (Foundational)
**Objective:** Distinguish platform metadata storage from user-facing discovery.

Explain the roles of a metastore, a metadata repository, and a user-facing catalogue. They may overlap in an implementation; describe the logical responsibilities rather than assuming three separate products.

### T02-Q2 — Persona journey (Applied)
**Objective:** Design a discovery workflow.

A risk analyst needs a trustworthy customer-exposure dataset, must determine its meaning and freshness, and then request access. Design the end-to-end catalogue journey from search through evaluation, classification review, access request, approval, and use. Identify the information the analyst needs at each step.

### T02-Q3 — Classification propagation (Scenario)
**Objective:** Preserve security context across derived assets.

A source field is classified as restricted. A transformation copies the field into a curated table and a dashboard extract. Explain how classification should be propagated or reassessed, what evidence is retained, and how you detect missing or downgraded labels. Do not assume every derived field automatically has identical sensitivity; state the assessment rule.

### T02-Q4 — Search relevance and stewardship (Applied)
**Objective:** Improve catalogue usability without confusing popularity with trust.

Define five catalogue fields or signals that improve search usefulness. Explain why popularity, recency, certification, owner, and quality signals should not be collapsed into one unexplained “trust score.” Propose a steward workflow for conflicting definitions of “active customer.”

### T02-Q5 — Architecture trade-off (Advanced)
**Objective:** Compare centralised and federated catalogue governance.

Compare a central catalogue team, domain-owned metadata with shared standards, and a hybrid model. Discuss consistency, domain autonomy, scale, accountability, duplication, classification enforcement, and how you would measure success. State which constraints would change your recommendation.

---

## Topic 03 — End-to-end lineage and impact analysis

Source: `03-end-to-end-lineage-and-impact-analysis.md`

### T03-Q1 — Dataset vs field lineage (Foundational)
**Objective:** Distinguish lineage granularity and evidence.

Explain dataset-level lineage and field-level lineage. Give one use case where dataset-level lineage is sufficient and one where field-level lineage is needed. Distinguish an observed lineage edge from an inferred or manually asserted edge.

### T03-Q2 — Draw the lineage (Applied)
**Objective:** Represent sources, transformations, targets, and consumers.

Use this synthetic flow:

- `core_ledger.exposure.amount`, `core_ledger.exposure.currency`
- joined with `reference.fx_rate.currency`, `reference.fx_rate.rate`
- transformed into `silver.exposure.amount_base`
- aggregated into `gold.customer_exposure.total_base`
- consumed by `regulatory_exposure_report`

Draw dataset-level edges and field-level derivations for `amount_base` and `total_base`. Label joins, calculations, aggregation, evidence source, and any unknown edge. State which lineage would need to be confirmed from code or execution logs.

### T03-Q3 — Schema-change impact (Scenario)
**Objective:** Perform downstream impact analysis.

`silver.customer.date_of_birth` is renamed to `birth_date` and its type changes from string to date. Describe how to identify downstream tables, quality rules, reports, matching logic, and consumers; classify impacts as confirmed or possible; name owners to notify; and define a validation and rollback plan. Explain the risk if field-level lineage is missing.

### T03-Q4 — Lineage coverage (Technical)
**Objective:** Measure coverage with an explicit denominator.

An inventory contains 120 in-scope datasets. For a defined source-to-report scope, 96 datasets have validated lineage and 18 have only inferred lineage; 6 have no lineage. Define and calculate (a) validated coverage and (b) any-known coverage, treating “validated” as only directly evidenced or reviewed lineage and “any-known” as validated plus inferred. Explain why the two metrics must be reported separately.

### T03-Q5 — Incomplete lineage and change safety (Advanced)
**Objective:** Design safe decisions under uncertainty.

A lineage graph reports no downstream dependency for a table, but the collection process does not inspect embedded SQL in two legacy applications. Can the table be declared safe to drop? Define the evidence required, uncertainty labels, fallback investigation, owner sign-off, and how the blind spot should be recorded. Also, if a report value on a known lineage path is wrong, explain how to locate the earliest demonstrated divergence using transformation/code versions, run evidence, and quality results; distinguish a hypothesis from a confirmed cause.

---

## Topic 04 — Data-quality dimensions and critical data elements

Source: `04-data-quality-dimensions-and-critical-data-elements.md`

### T04-Q1 — Dimension, rule, metric, threshold (Foundational)
**Objective:** Keep the quality concepts distinct.

Define a quality dimension, a testable rule, a metric, and a threshold. Give a single example using completeness and explain how each is different.

### T04-Q2 — Identify CDEs (Applied)
**Objective:** Link critical elements to business decisions.

For a customer-exposure report used for a regulatory filing, propose at least four candidate CDEs. For each, identify the business decision or obligation, owner, likely failure impact, quality dimensions, and lineage dependency. Explain why not every field in the report is automatically a CDE.

### T04-Q3 — Rule design (Technical)
**Objective:** Make quality rules testable and actionable.

Write five rules for synthetic customer-exposure data. Include at least one each for completeness, validity, uniqueness, consistency, and timeliness. For every rule specify the eligible population, formula or predicate, threshold, severity, owner, and response. Label the thresholds as illustrative assumptions.

### T04-Q4 — Quality calculations (Practical)
**Objective:** Calculate quality metrics with explicit denominators.

A synthetic batch has 1,000 eligible exposure rows:
- 970 have a non-null `customer_master_id`;
- 985 have a valid `currency_code`;
- 12 rows are involved in duplicate business-key groups; for this exercise, count each row in a duplicate group as a uniqueness failure;
- 8 rows have `amount_base < 0`, and the business rule states negative values are invalid for this specific report;
- 40 rows fail at least one of the four checks above.

Calculate completeness, validity, uniqueness, and non-negative amount validity as percentages. For each metric state the denominator. Explain why the 40-row “any failure” count cannot be obtained by simply adding the individual failure counts unless overlaps are known.

### T04-Q5 — Threshold and remediation trade-off (Advanced)
**Objective:** Align thresholds to risk and operational feasibility.

A proposed rule flags a report if any row lacks `customer_master_id`. The team argues that a 99% completeness threshold is “more practical.” Explain how to decide whether the threshold is acceptable. Discuss criticality, business tolerance, denominator, exception handling, upstream remediation, quarantine, waivers, and trend monitoring. Do not assume a numeric target is universally correct.

---

## Topic 05 — Data observability and quality service levels

Source: `05-data-observability-and-quality-service-levels.md`

### T05-Q1 — Signal, SLI, SLO, alert (Foundational)
**Objective:** Distinguish measurement, target, and operational response.

Define an observability signal, service-level indicator (SLI), service-level objective (SLO), and alert. Give a freshness example and explain why an alert condition is not itself an SLO.

### T05-Q2 — Freshness and budget (Calculation)
**Objective:** Evaluate a freshness SLO.

Illustrative requirement: a daily report must be published by 07:00 on 95% of business days in a 20-business-day measurement window. It is published by 07:00 on 18 days. Calculate observed compliance and whether the SLO is met. If a downstream report takes 12 minutes after its latest upstream dependency is ready, what latest upstream-ready time is required to meet 07:00, ignoring safety margin? Explain why a real design should add a margin and measure end-to-end freshness.

### T05-Q3 — Volume and distribution signals (Applied)
**Objective:** Select complementary indicators.

A daily customer feed normally contains 80,000–100,000 rows. Yesterday it contained 42,000 rows, while the job reported success. Propose a volume indicator, a distribution indicator, a freshness indicator, and an investigation sequence. Explain why a single row-count threshold may generate false alarms on holidays or planned business changes.

### T05-Q4 — Incident response (Scenario)
**Objective:** Connect detection to ownership and recovery.

A CDE quality check fails after a source schema change; the regulatory report is due in two hours. Design the response from detection through triage, blast-radius assessment, communication, mitigation, correction, backfill/replay if needed, validation, and closure. Include roles and evidence, not just technical steps.

### T05-Q5 — SLO feasibility and noisy alerts (Advanced)
**Objective:** Design realistic service levels across a dependency chain.

A target dataset depends on three sequential upstream jobs with p95 completion times of 20, 25, and 30 minutes; final transformation and publication take 15 minutes. Explain what can and cannot be concluded from these p95 figures alone. Propose how to set and validate an end-to-end freshness SLO, account for correlated delays and late data, and reduce noisy alerts without hiding real risk.

---

## Topic 06 — Master data management and golden records

Source: `06-master-data-management-and-golden-records.md`

### T06-Q1 — Master, reference, transaction, golden record (Foundational)
**Objective:** Distinguish related data concepts.

Define master data, reference data, transactional data, a golden record, and survivorship. Use customer, payment, and country-code examples. Explain why a golden record is governed and purpose-specific rather than automatically “the truth for every use.”

### T06-Q2 — Survivorship table (Applied)
**Objective:** Choose values per attribute and preserve provenance.

Use these synthetic records for the same already-reviewed customer entity:

| Source | Legal name | Address | Mobile | Verification status | Updated |
|---|---|---|---|---|---|
| Core | Asha Rao | 14 Lake Road | blank | legal name verified | 2026-09-01 |
| Cards | A. Rao | 14 Lake Rd | 9000000001 | mobile verified | 2026-10-10 |
| CRM | Asha R. | 91 Hill Street | 9000000002 | address verified | 2026-10-15 |

Assume the following rules: (1) legal name comes from the highest-priority verified legal-name source, with Core higher priority than Cards and CRM; (2) address comes from the most recently verified address, with the latest verification timestamp supplied by the steward; (3) mobile comes from the most recently verified mobile; (4) if verification timestamps are absent, do not use `Updated` as a substitute for verification time. Identify what can be selected and what must be sent to stewardship because the supplied data do not fully establish the required evidence. Explain why “most recently updated row wins” is not an acceptable universal rule.

### T06-Q3 — MDM style (Scenario)
**Objective:** Choose a style based on business and operational constraints.

Northbridge needs a consistent customer view for analytics within six months. Source systems cannot yet be changed, and operational applications can tolerate eventual consistency. Compare registry, consolidation, coexistence, and centralised/transactional styles. Recommend a staged approach and state what would cause you to change it.

### T06-Q4 — Merge, unmerge, synchronization (Applied)
**Objective:** Design reversible identity lifecycle operations.

Two customer records are incorrectly merged. Describe the minimum history, source links, decision evidence, identifier redirects, downstream notifications, and reconciliation required to unmerge safely. Explain how idempotent event handling helps consumers recover.

### T06-Q5 — MDM risk and governance (Advanced)
**Objective:** Address wrong merges, privacy, and source authority.

Design a stewardship and risk-control model for high-confidence automatic merges, uncertain matches, and conflicting critical attributes. Include access controls, audit trail, match thresholds, rollback/unmerge, KPIs, and cases where the golden record should not override source-level evidence. Explain how a wrong merge could affect analytics, ML features, or AI retrieval and how lineage/provenance helps repair affected outputs.

---

## Topic 07 — Reference data, entity resolution and identifiers

Source: `07-reference-data-entity-resolution-and-identifiers.md`

### T07-Q1 — Matching vs identifiers vs master data (Foundational)
**Objective:** Separate three distinct activities.

Explain entity resolution, identifier assignment, and master-data maintenance. Why is a name or email generally a weak long-term enterprise identifier? Explain namespaces and why identifiers should not be reused.

### T07-Q2 — Precision and recall (Calculation)
**Objective:** Compute and interpret matching quality.

On a labelled evaluation sample, there are 1,000 true duplicate pairs. A matcher proposes 900 pairs, of which 810 are true duplicates. Treat all 1,000 true pairs as the positive ground-truth set and assume the labelled sample is complete for this exercise.

Calculate:
- True positives (TP), false positives (FP), false negatives (FN)
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 = 2 × precision × recall / (precision + recall)

Show steps and explain the operational difference between a false positive and a false negative.

### T07-Q3 — Blocking cost (Calculation)
**Objective:** Estimate pair comparison reduction and its limitation.

For 1,000,000 records, all-pairs deduplication compares each unordered pair once. Blocking creates 10,000 non-overlapping blocks of exactly 100 records, and comparisons occur only within each block.

Calculate the number of all-pairs comparisons, the number after blocking, and the approximate reduction factor. State the important assumption and the principal recall risk of this blocking design.

### T07-Q4 — Identifier and reference-data policy (Applied)
**Objective:** Define stable identity and controlled code changes.

Design a policy for cross-system customer IDs and country codes. Include namespace, assignment authority, immutability/non-reuse, merge redirects, split/correction procedure, reference-list ownership, effective dates, retired codes, mappings, and consumer notification. Explain how a country code can be structurally valid but semantically wrong for a given effective date.

### T07-Q5 — Thresholds and error costs (Advanced)
**Objective:** Choose matching thresholds based on evidence and harm.

Propose high and low match-score thresholds for automatic merge, steward review, and non-match. You may use symbolic thresholds (`T_high`, `T_low`) instead of inventing universal numeric values. Explain how labelled evaluation data, precision/recall, false-merge costs, review capacity, subgroup error rates, and drift should influence the thresholds. Describe a cluster-level failure that can occur even when pairwise scores look reasonable.

---

## Topic 08 — Metadata standards and interoperability

Source: `08-metadata-standards-and-interoperability.md`

### T08-Q1 — Format vs semantics (Foundational)
**Objective:** Distinguish syntax compatibility from semantic equivalence.

Two tools exchange valid JSON. One interprets `owner` as the accountable business owner; the other interprets it as the pipeline operator. Explain why successful parsing does not establish interoperability. Name the kinds of identity, vocabulary, lifecycle, and semantic agreements needed.

### T08-Q2 — Mapping and loss analysis (Applied)
**Objective:** Design explicit crosswalk rules.

Source catalogue classification is `{Public, Internal, Restricted}`. Target quality tool classification is `{Open, Internal, Confidential, Restricted}`. Propose a mapping table and identify any source-to-target or round-trip ambiguity. Do not assume that `Restricted` means the same thing in both systems without a definition. State how unsupported or ambiguous values should be handled.

### T08-Q3 — Canonical vs point-to-point (Calculation and design)
**Objective:** Compare mapping growth and semantic governance.

For six systems, assume a directed mapping is needed for every ordered source-target pair in a point-to-point design. Calculate the number of mappings. For a canonical model, assume each system needs one inbound and one outbound mapping. Calculate the number of mappings and discuss the limitations of this simplified count.

### T08-Q4 — Versioning and conformance (Technical)
**Objective:** Define a safe contract evolution process.

A metadata exchange contract adds a required `classification_basis` field and changes the meaning of `owner`. Define a compatibility review, versioning/deprecation plan, mapping updates, conformance tests, rollout, reconciliation, and rollback. Explain why adding a required field and changing field semantics are different risks.

### T08-Q5 — Lossy mapping and audit evidence (Advanced)
**Objective:** Preserve lineage, provenance, classification, and identity.

A source system represents field-level lineage with transformation expressions and confidence, while the target supports only dataset-level edges. Design an exchange strategy. Identify what is lost, how loss is declared, what remains in the source of truth, and what tests and alerts detect regression. State when the target must reject the mapping or preserve a linked sidecar rather than silently dropping information.

---

# Section C — Practical and calculation exercises

Complete these exercises in a notebook, spreadsheet, or Markdown document. Retain the inputs, formulas, assumptions, results, and reviewer notes. All data are synthetic.

## C1 — Metadata inventory and completeness

Create a ten-asset inventory for a fictional customer dataset (one asset per row). Each row must identify an asset, category (business/technical/operational metadata represented), stable asset ID, source/evidence, owner or maintainer, update frequency, quality check, and lifecycle status.

Then define a required-field set for in-scope assets. If 10 assets are eligible and 8 have all required metadata fields populated and current, calculate the completeness rate. State whether an asset with a populated but stale owner field counts as complete; justify your policy.

## C2 — Catalogue entry and discovery

Write one catalogue entry for `gold.customer_exposure` including stable ID, description, domain, owner, steward, classification and basis, schema reference, CDEs, freshness, quality status, lineage link, certification status, known limitations, access workflow, and last-reviewed time.

Create two user journeys (risk analyst and data steward). For each, list the query, filters, evidence inspected, decision, and escalation path. Explain which fields can be harvested and which need human approval.

## C3 — Lineage and schema-change impact

Draw the C2 asset's lineage from at least two sources through one transformation and one aggregation to a report. Include one field-level derivation for a CDE. For each edge record: source, target, edge type, evidence, confidence/status, observed time, and known blind spots.

Change one upstream field's name or meaning. Produce an impact report listing confirmed affected fields, possible affected consumers, quality rules, owners to notify, tests, release/rollback plan, and unresolved uncertainty. Never equate “not found in lineage” with “no dependency” when collection coverage is incomplete.

## C4 — CDE rules and quality metrics

Use this synthetic batch of 1,000 eligible rows:

| Check | Failing rows |
|---|---:|
| `customer_master_id` non-null | 30 |
| `currency_code` in the effective reference list | 15 |
| unique exposure business key | 20 |
| `amount_base >= 0` for this specific report | 8 |

For this exercise, calculate each rule's pass rate independently using 1,000 as its denominator. Do not assume the failure sets are disjoint. If 55 distinct rows fail at least one rule, calculate the overall “passes all four checks” rate. Explain why the sum 30 + 15 + 20 + 8 is not the count of distinct failing rows.

## C5 — Freshness and service-level assessment

Illustrative SLO: publish by 07:00 on at least 95% of business days in a 20-day window. The actual publish times (local reporting timezone) are:

`06:42, 06:58, 07:03, 06:55, 06:49, 07:12, 06:51, 06:57, 06:59, 06:40, 06:53, 06:52, 07:01, 06:54, 06:56, 06:48, 06:50, 06:59, 06:46, 06:57`

Count on-time days, calculate compliance, and determine whether the illustrative SLO is met. Propose an alert and an incident response that distinguish an early warning from an SLO breach.

## C6 — Golden-record survivorship

Create a table with at least five synthetic source records for three entities. For each attribute, define a distinct survivorship rule, source authority, verification evidence, tie-break, provenance, and steward-review condition. Produce at least two sample golden records and one ambiguous case routed to stewardship. Include a wrong-merge/unmerge procedure and synchronization/reconciliation design.

## C7 — Entity-resolution evaluation

Use the data in T07-Q2 to calculate precision, recall, and F1. Then propose a threshold experiment with three candidate threshold settings. For each setting specify the expected direction of changes in false positives, false negatives, automatic merge volume, and steward workload; do not invent measured results without a labelled test. Identify a sampling strategy and a drift-monitoring plan.

## C8 — Metadata mapping and conformance

Define a source and target metadata model with at least eight mapped concepts across asset identity, schema, ownership, classification, lineage, quality result, timestamps, and provenance. For every mapping include transformation, version, loss/default/unsupported policy, and a test. Choose and justify an exchange channel (API, event, or bulk file) based on latency, volume, ordering, replay, security, and reconciliation needs. Include positive, negative, boundary, round-trip, and backward-compatibility tests. Explain why a mapping that “succeeds” syntactically may still fail semantically.

---

# Section D — Integrated architecture scenarios

All scenarios are fictional and synthetic. The roadmap's Northbridge Bank example is an illustrative scenario, not a production specification. **D1 is the required integrated exercise for this bank; D2–D5 are additional scenario drills** that deepen incident response and architecture-defence practice.

## D1 — Enterprise metadata and lineage design

Northbridge Bank has customer and exposure data in a core ledger, cards platform, and CRM. A lakehouse contains bronze, silver, and gold layers. A regulatory exposure report and a customer 360 dashboard consume the data. Metadata is split across a catalogue, a quality tool, and a lineage collector. Duplicate customer records are known to exist, but the duplicate rate is not yet measured.

Produce a concise architecture design that includes:

1. Scope, stakeholders, requirements, constraints, assumptions, and exclusions.
2. Metadata inventory and logical schema covering business, technical, and operational metadata.
3. Catalogue architecture, discovery journeys, classification, ownership, and stewardship.
4. Dataset- and field-level lineage for both reports; edge evidence and blind spots.
5. Impact analysis for a change to `currency_code` or an exposure calculation.
6. CDE register, rules, thresholds, owners, and remediation.
7. Observability indicators, SLIs/SLOs, alerts, incident response, and feasibility against upstream dependencies.
8. MDM approach, customer identifiers, reference data, matching evaluation, survivorship, synchronization, and wrong-merge recovery.
9. Metadata interoperability mapping, versioning, conformance, loss handling, and a justified API/event/bulk-file exchange pattern.
10. Batch and at least one incremental or streaming path where relevant: define event-time versus processing-time assumptions, lag/late-event handling, replay/idempotency, and lineage/quality evidence.
11. At least five architecture decision records (ADRs), each with context, decision, alternatives, consequences, risks, and revisit triggers.
12. Validation plan, measurable acceptance evidence, limitations, and an owned gap list.

State which elements are facts supplied by the scenario and which are assumptions you introduce. No paid infrastructure or real personal data is required.

## D2 — The report is late and wrong

At 06:50, an upstream customer feed is delayed. At 06:58, the exposure transformation completes, but a new `currency_code` value is not in the current reference mapping. The job succeeds technically; the report is due at 07:00. The catalogue still shows yesterday's freshness status, and field-level lineage for the conversion is incomplete.

Answer:

1. Which signals should detect the delay, invalid code, stale catalogue state, and incomplete lineage?
2. What is the difference between a successful job run and a trustworthy report?
3. Who owns triage, business impact assessment, reference-data correction, report release decision, and catalogue/lineage repair?
4. What should be quarantined, held, recomputed, or communicated? State assumptions.
5. How do you avoid silently mapping an unknown code to a plausible but wrong value?
6. What evidence is required before closure and backfill?
7. Which topic files should be revisited if the design failed to detect the issue?

## D3 — Customer merge dispute

Two synthetic customer records were automatically merged because name and postcode matched. A steward later finds different verified dates of birth and separate active accounts. The master ID has already been sent to downstream reports and an operational consumer.

Design the response and long-term control changes. Cover immediate risk containment, unmerge, source-to-master crosswalk correction, identifier redirects, downstream notifications and reconciliation, matching evaluation, blocking and threshold changes, provenance, steward review, lineage-based impact analysis, quality/observability signals, and regression testing. Explain why simply deleting the golden record is unsafe.

## D4 — Metadata interoperability failure

The catalogue sends a classification label, owner, asset ID, and field-level lineage to a quality tool. Parsing succeeds, but the quality tool maps “owner” to a pipeline operator, drops lineage confidence, and reuses an asset ID that collides with a local ID.

Identify structural, semantic, identity, and information-loss failures. Propose a mapping contract, namespace strategy, versioning and deprecation policy, conformance tests, reconciliation process, and monitoring. Compare point-to-point and canonical approaches under the scenario's assumptions; either may be defensible if trade-offs are explicit.

## D5 — Architecture defence

A review panel challenges the D1 design:

- “Why not put every field and every operational event into one giant catalogue record?”
- “If the lineage graph has no edge, why is that not proof of no dependency?”
- “Why not use 99% as the threshold for every quality rule?”
- “Why not auto-merge every pair above a single similarity score?”
- “Why do we need mapping tests if both tools use JSON?”

Answer each challenge with a clear principle, a concrete risk, a decision rule, and evidence you would show the reviewer.


# Section D.6 — Assessment traceability matrix

This matrix maps every assessed item to the relevant module learning outcome(s), the topic-specific objective or deliverable, difficulty, response type, answer/rubric, and source section. The module learning outcomes (MLOs) are those in the roadmap, Section 2: **MLO1** metadata categories; **MLO2** catalogue/discovery; **MLO3** lineage; **MLO4** impact analysis; **MLO5** quality/CDEs/rules; **MLO6** observability/SLOs; **MLO7** MDM/golden records; **MLO8** reference data/identifiers/entity resolution; **MLO9** standards/interoperability; **MLO10** coherent integrated architecture; **MLO11** complete and defend the final project. Source section references point to the corresponding lesson's numbered sections and subsections.

| ID | Topic file / integrated set | Specific objective assessed | MLO(s) | Difficulty | Type | Answer / rubric | Source section(s) |
|---|---|---|---|---|---|---|---|
| T01-Q1 | Topic 01 | Classify metadata and explain collection mode | 1 | Foundational | Classification | E1 / T01-Q1 | Topic 01 §§3.1–3.4 |
| T01-Q2 | Topic 01 | Model an inventory with source, owner, freshness and lifecycle | 1, 10 | Applied | Design | E1 / T01-Q2 | Topic 01 §§4.1–4.5, 5.1–5.5 |
| T01-Q3 | Topic 01 | Assign accountability and manage metadata lifecycle | 1, 10 | Scenario | Diagnosis/design | E1 / T01-Q3 | Topic 01 §§5.1–5.6 |
| T01-Q4 | Topic 01 | Define reproducible metadata-quality metrics and denominators | 1 | Technical | Metric design | E1 / T01-Q4 | Topic 01 §§5.4–5.5 |
| T01-Q5 | Topic 01 | Compare automated, curated and hybrid metadata collection | 1, 10 | Advanced | Architecture trade-off | E1 / T01-Q5 | Topic 01 §6 |
| T02-Q1 | Topic 02 | Distinguish catalogue, repository and metastore responsibilities | 2 | Foundational | Conceptual comparison | E2 / T02-Q1 | Topic 02 §§2.2–2.3 |
| T02-Q2 | Topic 02 | Design a risk-analyst discovery and access journey | 2, 10 | Applied | Workflow design | E2 / T02-Q2 | Topic 02 §§3.1–3.3, 5.9 |
| T02-Q3 | Topic 02 | Propagate/reassess classification with lineage evidence | 2, 9, 10 | Scenario | Governance design | E2 / T02-Q3 | Topic 02 §5.6 and §6 |
| T02-Q4 | Topic 02 | Improve search while separating popularity from trust | 2 | Applied | Design/diagnosis | E2 / T02-Q4 | Topic 02 §§3.3, 5.4–5.8 |
| T02-Q5 | Topic 02 | Compare centralized, federated and hybrid governance | 2, 10 | Advanced | Architecture trade-off | E2 / T02-Q5 | Topic 02 §6 and §7 |
| T03-Q1 | Topic 03 | Distinguish dataset/field lineage and evidence status | 3 | Foundational | Explanation | E3 / T03-Q1 | Topic 03 §§2.3, 3.2–3.5 |
| T03-Q2 | Topic 03 | Construct dataset and field derivations with assumptions | 3 | Applied | Diagram/derivation | E3 / T03-Q2 | Topic 03 §5 |
| T03-Q3 | Topic 03 | Perform schema-change impact analysis and plan validation | 3, 4 | Scenario | Impact analysis | E3 / T03-Q3 | Topic 03 §6 |
| T03-Q4 | Topic 03 | Calculate validated and any-known lineage coverage | 3 | Technical | Calculation | E3 / T03-Q4 | Topic 03 §7 and §10 |
| T03-Q5 | Topic 03 | Make safe decisions with incomplete lineage and investigate the earliest demonstrated root-cause divergence | 3, 4, 10 | Advanced | Risk decision/root-cause analysis | E3 / T03-Q5 | Topic 03 §§3.4–3.5, 6, 9 |
| T04-Q1 | Topic 04 | Distinguish dimension, rule, metric and threshold | 5 | Foundational | Explanation | E4 / T04-Q1 | Topic 04 §§2.2–2.4 |
| T04-Q2 | Topic 04 | Select CDEs from business impact and lineage | 5 | Applied | Prioritization | E4 / T04-Q2 | Topic 04 §3 |
| T04-Q3 | Topic 04 | Specify atomic, measurable, owned quality rules | 5 | Technical | Rule design | E4 / T04-Q3 | Topic 04 §4 |
| T04-Q4 | Topic 04 | Calculate four quality rates and combined pass rate | 5 | Practical | Calculation | E4 / T04-Q4 | Topic 04 §§5.3–5.8 |
| T04-Q5 | Topic 04 | Justify thresholds, exceptions and remediation across batch, incremental and streaming controls | 5, 10 | Advanced | Risk/governance analysis | E4 / T04-Q5 | Topic 04 §§4.5, 7.1–7.8, 8 |
| T05-Q1 | Topic 05 | Distinguish signal, SLI, SLO and alert | 6 | Foundational | Explanation | E5 / T05-Q1 | Topic 05 §§2.3–2.4, 5.1–5.3 |
| T05-Q2 | Topic 05 | Calculate SLO compliance and upstream cutoff | 6 | Calculation | Calculation | E5 / T05-Q2 | Topic 05 §§4.1, 5.2–5.6 |
| T05-Q3 | Topic 05 | Choose volume, distribution and freshness indicators | 6 | Applied | Monitoring design | E5 / T05-Q3 | Topic 05 §§3.1–3.6, 4.1–4.7 |
| T05-Q4 | Topic 05 | Design incident response with ownership and evidence | 6, 10 | Scenario | Incident design | E5 / T05-Q4 | Topic 05 §§6.5–6.9 |
| T05-Q5 | Topic 05 | Assess end-to-end feasibility from component p95s | 6 | Advanced | Quantitative reasoning | E5 / T05-Q5 | Topic 05 §5.10 and §6.4 |
| T06-Q1 | Topic 06 | Distinguish master, reference, transaction and golden record | 7 | Foundational | Conceptual comparison | E6 / T06-Q1 | Topic 06 §§2–3 |
| T06-Q2 | Topic 06 | Apply attribute-specific survivorship without inventing evidence | 7 | Applied | Worked decision | E6 / T06-Q2 | Topic 06 §§4.2, 6.3–6.6 |
| T06-Q3 | Topic 06 | Choose MDM style from constraints and migration path | 7, 10 | Scenario | Architecture trade-off | E6 / T06-Q3 | Topic 06 §5 |
| T06-Q4 | Topic 06 | Design reversible merge/unmerge and reconciliation | 7, 8, 10 | Applied | Lifecycle design | E6 / T06-Q4 | Topic 06 §§7.4, 8.1–8.5, 9.2 |
| T06-Q5 | Topic 06 | Govern match risk, privacy, thresholds, provenance and downstream analytics/ML/AI repair | 7, 8, 10 | Advanced | Governance design | E6 / T06-Q5 | Topic 06 §§7–10 |
| T07-Q1 | Topic 07 | Separate resolution, identifier assignment and MDM | 8, 7 | Foundational | Conceptual comparison | E7 / T07-Q1 | Topic 07 §§2.1–2.4, 4 |
| T07-Q2 | Topic 07 | Compute TP/FP/FN, precision, recall and F1 | 8 | Calculation | Calculation | E7 / T07-Q2 | Topic 07 §§7.1–7.4 |
| T07-Q3 | Topic 07 | Calculate pair counts and blocking trade-off | 8 | Calculation | Calculation | E7 / T07-Q3 | Topic 07 §§6.1–6.4 |
| T07-Q4 | Topic 07 | Design namespaced IDs and governed reference-code lifecycle | 8 | Applied | Policy design | E7 / T07-Q4 | Topic 07 §§3.5–3.7, 4.1–4.6 |
| T07-Q5 | Topic 07 | Select thresholds based on error costs and cluster risk | 8 | Advanced | Decision design | E7 / T07-Q5 | Topic 07 §§6.4–6.6, 7, 8 |
| T08-Q1 | Topic 08 | Distinguish syntax/format from semantic interoperability | 9 | Foundational | Explanation | E8 / T08-Q1 | Topic 08 §§2.3–2.4, 3.4–4.2 |
| T08-Q2 | Topic 08 | Map classification vocabularies and declare loss/ambiguity | 9 | Applied | Mapping design | E8 / T08-Q2 | Topic 08 §§5.3–5.6 |
| T08-Q3 | Topic 08 | Calculate direct vs canonical mapping counts | 9 | Calculation/design | Calculation and trade-off | E8 / T08-Q3 | Topic 08 §8.2 and §9.5 |
| T08-Q4 | Topic 08 | Plan contract versioning and conformance | 9 | Technical | Compatibility design | E8 / T08-Q4 | Topic 08 §6 and §9 |
| T08-Q5 | Topic 08 | Preserve or declare loss of field-level lineage/provenance | 9 | Advanced | Interoperability design | E8 / T08-Q5 | Topic 08 §§5.5, 7.3, 9.2–9.3 |
| C1 | Topic 01 | Build inventory and compute completeness | 1, 10 | Applied | Practical artefact/calculation | E9 / C1 | Topic 01 §§4, 5, 10 |
| C2 | Topic 02 | Create catalogue record and persona journeys | 2, 10 | Applied | Practical artefact | E9 / C2 | Topic 02 §§3–5, 10 |
| C3 | Topic 03 | Draw lineage and produce impact report | 3, 4, 10 | Applied | Practical artefact | E9 / C3 | Topic 03 §§5–6, 10 |
| C4 | Topic 04 | Calculate rule rates and union-of-failures result | 5, 10 | Practical | Calculation/artefact | E9 / C4 | Topic 04 §§5–6, 9–10 |
| C5 | Topic 05 | Calculate on-time compliance and define response | 6, 10 | Practical | Calculation/incident design | E9 / C5 | Topic 05 §§4–6, 8 |
| C6 | Topic 06 | Build survivorship and unmerge evidence | 7, 10 | Applied | Practical artefact | E9 / C6 | Topic 06 §§6–9, 13 |
| C7 | Topic 07 | Evaluate matching and design threshold experiment | 8, 10 | Applied | Calculation/design | E9 / C7 | Topic 07 §§6–9 |
| C8 | Topic 08 | Specify mappings, conformance tests and justified API/event/file exchange | 9, 10 | Applied | Practical artefact | E9 / C8 | Topic 08 §§5–9, 10 |
| D1 | Integrated Topics 01–08 | Integrate all capabilities, include a streaming/incremental path and exchange-pattern decision, and defend the final design | 1–11 | Advanced | Capstone design | E10 / D1 (30 points) | Roadmap §§7.3, 10.2–10.5; all lesson deliverable/gate sections |
| D2 | Integrated Topics 01–05, 08 | Diagnose late/incorrect report across quality, freshness, catalogue and lineage | 2–6, 9–10 | Advanced | Incident scenario | E10 / D2 (15 points) | Topics 02 §§5–6; 03 §6; 04 §8; 05 §6; 08 §7 |
| D3 | Integrated Topics 03–07 | Contain and reverse a wrong merge; repair downstream state | 3–8, 10 | Advanced | Incident/architecture scenario | E10 / D3 (15 points) | Topics 03 §6; 04 §8; 05 §6; 06 §§8–9; 07 §8 |
| D4 | Integrated Topics 01–03, 08 | Diagnose semantic, identity and information-loss failures | 1–4, 9–10 | Advanced | Interoperability scenario | E10 / D4 (15 points) | Topics 01 §4; 02 §4; 03 §3; 08 §§3–8 |
| D5 | Integrated Topics 01–08 | Defend design decisions and explain architecture principles | 1–11 | Advanced | Oral/written defence | E10 / D5 (10 points) | Roadmap §§7, 10–11; all topic trade-off, misconception and completion-gate sections |

## D.7 — Module learning-outcome coverage summary

| Roadmap learning outcome | Primary question coverage | Practical/integrated evidence |
|---|---|---|
| MLO1 — Explain/classify business, technical and operational metadata | T01-Q1–Q5 | C1, D1, D4 |
| MLO2 — Design catalogue and discovery | T02-Q1–Q5 | C2, D1, D2, D4 |
| MLO3 — Interpret/document lineage | T03-Q1–Q5 | C3, D1–D4 |
| MLO4 — Perform lineage-based impact analysis | T03-Q3, T03-Q5 | C3, D1–D3 |
| MLO5 — Define quality dimensions, CDEs and rules | T04-Q1–Q5 | C4, D1–D2 |
| MLO6 — Design observability and quality service levels | T05-Q1–Q5 | C5, D1–D3 |
| MLO7 — Explain MDM and golden records | T06-Q1–Q5 | C6, D1, D3 |
| MLO8 — Evaluate reference data, identifiers and entity resolution | T07-Q1–Q5 | C7, D1, D3 |
| MLO9 — Explain standards and interoperability | T08-Q1–Q5 | C8, D1, D2, D4–D5 |
| MLO10 — Integrate capabilities into coherent architecture | T01-Q2–Q5, T02-Q2/Q5, T03-Q3/Q5, T04-Q5, T05-Q4, T06-Q3/Q4, C1–C8 | D1–D5 |
| MLO11 — Complete and defend final project | Not measured by recall questions alone | D1 capstone, D5 defence, Section F4 checklist, reviewer sign-off |

---

# Section E — Answer key and evaluation rubrics

> Attempt Sections B–D before reading this section. The reference answers describe essential reasoning, not the only acceptable architecture. Alternative designs earn credit when their assumptions, trade-offs, risks, and validation are explicit.

## E1. Topic 01 answer key

### T01-Q1
1. Definition of “active customer”: **business**; business owner/steward-curated, possibly supported by glossary workflow.
2. Column type/nullability: **technical**; usually harvested automatically and reviewed on schema change.
3. Last successful load: **operational**; generated from job/run evidence.
4. Owner/steward: primarily **business/accountability metadata**; maintained by governance process, possibly synchronized from an identity/ownership registry.
5. Row count/job status: **operational**; automated, with checks for collection failure.
6. Storage location: **technical**; harvested, access-controlled.
7. Classification and permitted purpose: classification is governance/business context and can have technical enforcement metadata; human-approved policy plus propagated labels is a reasonable hybrid.
8. Latest quality result: **operational**; generated by a quality check, with rule definition and owner metadata linked.

Some items legitimately span categories. Award full credit when the learner identifies the primary category and explains the overlap rather than insisting the categories are mutually exclusive in every implementation.

### T01-Q2
A sound inventory has a stable asset ID; name/type/domain; business definition; owner and steward; classification/purpose; schema/columns/types/keys/location; source and collection timestamp; last refresh/run status; quality results; lineage references; lifecycle state; and update/retention policy. The source and freshness of each value matter. Unknown should be represented explicitly (`unknown`, `not assessed`, or `not collected`) with status and remediation—not replaced by a plausible default. A stale owner is not “current complete”; a metric should separately report populated and current/validated fields.

### T01-Q3
The scanner can record name, type, location, source, and observation time. The accountable domain owner and steward define meaning and classification; the security/governance role reviews classification where policy requires it; engineering confirms lineage and downstream dependencies. Before broad discovery or use, keep the column in a review/pending state or apply conservative access restrictions. Lifecycle: detect → register → assess → approve/annotate → publish → monitor → change/review → deprecate/retire, retaining history and evidence.

### T01-Q4
Acceptable checks include: required-field completeness = assets with all mandatory fields populated and current / eligible in-scope assets; definition consistency = assets whose business term references resolve to an approved glossary term / assets requiring such references; owner validity = assets with an active accountable owner / eligible assets. State whether retired assets are excluded and how unknown states are counted. With 200 assets, an example could be 184 with all required fields current: 184/200 = 92%. The number is only meaningful if scope and required fields are defined.

### T01-Q5
Scanners are timely and consistent for observable technical facts but cannot reliably infer business meaning or authority. Human curation supplies semantics and decision rights but can be stale and costly. A hybrid is suitable: automated technical/operational harvesting; human approval of business definitions, ownership, classification, and high-impact semantics; freshness and drift checks; audit trail and exception queues. Alternatives are acceptable if change rate, risk, scale, ownership, and operational costs are addressed.

**Common misconceptions:** every metadata field is manually curated; scanner output is always semantically correct; missing metadata equals “not applicable”; owner and pipeline operator are interchangeable.

## E2. Topic 02 answer key

### T02-Q1
A metastore commonly stores platform-facing schema/table metadata; a metadata repository stores or integrates metadata records and relationships; a catalogue provides discoverability, context, governance and access workflows. These are logical responsibilities and may share implementation. Do not award full credit for assuming the names always mean separate products.

### T02-Q2
A good journey includes search and filters; inspect definition, owner, certification/quality, freshness, classification, lineage and limitations; compare the asset against the analyst's use case; request access with purpose; route to an accountable approver; enforce access; and record outcome/expiry where relevant. A catalogue can aid discovery and requests but should not bypass policy enforcement.

### T02-Q3
Propagate classification as a default control signal, then reassess derived fields/assets based on content, transformation, joins, aggregation, purpose, and policy. Retain source label, derived label, decision basis, transformation/version, and reviewer/evidence. Detect missing tags via coverage/conformance checks and lineage-aware comparisons. A derived field may become less or differently sensitive, but downgrade needs a justified, governed decision—not an automatic assumption.

### T02-Q4
Useful signals: business definition, owner/steward, domain/tags, classification, freshness, quality status, lineage, certification, usage/popularity, schema and access route. Keep separate dimensions or explain weighting and limitations; popularity is not quality and recency is not authority. Resolve conflicting terms through domain ownership, proposal, impact assessment, approval, versioning, aliases/synonyms, and communication.

### T02-Q5
Central governance can improve consistency and simplify enforcement but may bottleneck and lack domain nuance. Federation improves local ownership and scale but risks divergent definitions and inconsistent controls. Hybrid commonly provides shared identity/schema/classification standards and platform enforcement, with domain stewards owning definitions and quality. Success metrics might include search success, metadata coverage/freshness, steward turnaround, classification coverage, and user-reported usefulness. Credit any justified option.

**Common misconceptions:** catalogue equals metastore; popular equals trustworthy; classification is a one-time tag; access approval equals technical enforcement.

## E3. Topic 03 answer key

### T03-Q1
Dataset lineage connects assets/jobs; field lineage connects source fields and transformation logic to target fields. Dataset lineage can support broad dependency discovery; field lineage is needed for a critical field's origin, a precise schema-change impact, or audit explanation. Evidence can be parsed SQL, job metadata, execution logs, or reviewed configuration. Inferred/manual edges must be labelled with evidence, confidence, and timestamp; never present them as observed facts.

### T03-Q2
Expected path: `core_ledger.exposure` and `reference.fx_rate` → join/convert → `silver.exposure.amount_base` → group/aggregate by customer → `gold.customer_exposure.total_base` → report. At field level, `amount_base = exposure.amount × fx_rate.rate` after joining on currency and applying an explicitly defined rate direction/effective-date rule. `total_base = SUM(amount_base)` grouped by customer under the stated aggregation filter. The prompt does not define rate direction, effective-date selection, or exclusions; a good answer marks these as assumptions requiring code/business confirmation. Edge evidence should distinguish declared transformation, observed run, and inferred dependency.

### T03-Q3
Search lineage graph and code/contract references; include downstream fields, rules, dashboards, reports, match logic, and consumers. Type change can affect parsing, null/invalid rates, date semantics, and query compatibility; rename affects references and mappings. Separate confirmed edges from possible dependencies and list the legacy/opaque blind spots. Notify source owner, transformation owner, quality owner, report owner, and consumers. Test schema compatibility, backfill, rule results, report totals, and rollback; do not release solely on a graph result if coverage is incomplete.

### T03-Q4
Validated coverage = 96 / 120 × 100 = **80%**. Any-known coverage = (96 + 18) / 120 × 100 = 114/120 = **95%**. Six datasets have no known lineage. Report inferred separately because confidence and evidence differ. A useful supplementary metric is inferred share among any-known edges/assets: 18/114 ≈ **15.8%**, if the denominator is explicitly stated.

### T03-Q5
No. “No edge found” is only meaningful if collection scope and coverage are sufficient. Check ingestion of embedded SQL, scheduler/job definitions, access logs, application queries, downstream ownership, and manual dependencies; conduct a controlled deprecation/usage observation if appropriate. Record the blind spot and confidence. Require owner sign-off and a rollback/retention window. If evidence remains incomplete, label the decision high risk rather than asserting no dependency. For a wrong report value, trace upstream from the symptom and compare expected versus observed outputs, transformation/code version, run inputs and timestamps, and quality results. Identify the earliest **demonstrated** divergence; an upstream suspect remains a hypothesis until corroborated by evidence. For a wrong report value, trace upstream from the symptom and compare expected versus observed outputs, transformation/code version, run inputs and timestamps, and quality results. Identify the earliest **demonstrated** divergence; an upstream suspect remains a hypothesis until corroborated by evidence.

**Common misconceptions:** all lineage is field-level; inferred edges are facts; missing edges prove no use; lineage alone proves a transformation is correct.

## E4. Topic 04 answer key

### T04-Q1
Dimension = aspect of fitness for use; rule = executable predicate or test; metric = measured result; threshold = decision boundary. Example: completeness dimension; rule “`customer_master_id` is non-null for every eligible report row”; metric “non-null eligible rows / all eligible rows”; threshold such as 100% for this critical field, if justified by the business requirement. Other thresholds may be acceptable when explicitly justified.

### T04-Q2
Candidates may include customer master ID, exposure amount, currency code, reporting date, customer risk category, and counterparty/customer identity. Each must connect to a report decision/obligation and have an owner, impact, dimension, and upstream lineage. Not every field is a CDE; prioritize fields whose failure materially changes a business or regulatory outcome.

### T04-Q3
A complete answer defines five independent tests, e.g. non-null master ID (completeness), currency in the effective reference list (validity), unique exposure business key (uniqueness), converted amount agrees with currency/rate/date rules (consistency), and source data arrives by an agreed cutoff (timeliness). Every rule needs population, expression, denominator, illustrative threshold, severity, owner, action, and evidence. Thresholds must be justified and not presented as universal.

### T04-Q4
- `customer_master_id` completeness = (1000 − 30)/1000 = **97.0%**.
- `currency_code` validity = (1000 − 15)/1000 = **98.5%**.
- Uniqueness = (1000 − 12)/1000 = **98.8%** under the question's defined row-failure convention.
- Non-negative amount validity = (1000 − 8)/1000 = **99.2%**.
- The question states that 40 rows fail at least one check, so rows passing all four = 1000 − 40 = 960. Overall all-check pass rate = 960/1000 × 100 = **96.0%**.
- Do not add the individual failure counts to estimate distinct failed rows because a row may fail multiple rules. The supplied union count (40) is the correct denominator for the combined pass calculation.

### T04-Q5
Decide from business tolerance, regulatory impact, known failure modes, data volume, exceptions, lineage, operational feasibility, and recovery options. A 99% threshold may permit a missing critical identifier in a report where each row must be attributable; a 100% rule may be necessary for a narrowly defined critical population, while other rules may tolerate controlled exceptions. Define eligible population and exception treatment, quarantine or waiver authority, upstream correction, trend, and review. Explain whether the same threshold and action should apply unchanged to batch, incremental/CDC, and streaming data, including late events and replay. “Practical” is not sufficient justification.

**Common misconceptions:** dimension and metric are synonyms; all dimensions use one threshold; adding failure counts gives unique bad rows; quality score alone explains business impact.

## E5. Topic 05 answer key

### T05-Q1
Signal = raw observation/event (e.g., load completion timestamp); SLI = measured indicator (e.g., fraction of business days published by 07:00); SLO = target for the SLI over a defined window (e.g., ≥95%); alert = operational notification triggered by a condition. Alert thresholds may provide early warning and need not equal the SLO breach boundary.

### T05-Q2
Compliance = 18/20 × 100 = **90%**, so the 95% SLO is **not met**. If the downstream step requires 12 minutes, latest upstream readiness is 07:00 − 00:12 = **06:48**, ignoring margin. A real design adds safety margin, accounts for queueing and variable duration, defines timezone/calendar/late-arriving data, and measures end-to-end publication time rather than only one upstream timestamp.

### T05-Q3
Volume SLI could compare row count with a seasonal/day-of-week baseline and alert on a justified deviation; distribution checks could compare customer status, region, or amount bands; freshness checks expected completion/cutoff. Investigate source arrival, partition completeness, business calendar/holiday, filters, upstream failures, schema changes, and downstream counts. A single fixed threshold may false-alarm on known calendar effects; avoid suppressing genuine anomalies by using documented calendars and baselines.

### T05-Q4
Detect and identify affected CDE/report; assign incident lead and domain/data owner; assess whether output is wrong or late and regulatory exposure; hold/quarantine affected output where risk warrants; notify consumers and stakeholders; fix upstream/schema/rule; replay/backfill idempotently; validate counts, quality, lineage, and report totals; release with approval; document root cause, timestamps, impact, and preventive actions. Exact roles depend on the operating model, but decision rights must be named.

### T05-Q5
Do not simply sum p95 values and call the result an end-to-end p95; component distributions and dependencies may be correlated, and p95s do not determine the combined percentile. The nominal durations sum to 90 minutes (20+25+30+15) only as a rough planning estimate under an additive sequential assumption, not a proven p95. Measure end-to-end completion across representative runs, define the business calendar and cutoff, set early warnings and breach handling, account for late events and upstream SLOs, and review alert precision/noise.

**Common misconceptions:** successful job means fresh/correct data; alert equals SLO; component p95s always add to end-to-end p95; row count alone detects quality failures.

## E6. Topic 06 answer key

### T06-Q1
Master data represents shared core entities (customer); reference data supplies controlled code lists (country code); transactional data records events (payment); golden record is a governed representation of an entity assembled under stated rules; survivorship determines which candidate value is retained per attribute. Authority is purpose- and rule-dependent, with provenance; it is not universal truth.

### T06-Q2
- **Legal name:** Core is the highest-priority source and explicitly says the legal name is verified, so select `Asha Rao` under rule 1.
- **Address:** CRM says its address is verified, but the required verification timestamp is not supplied. `Updated=2026-10-15` is not a substitute. Do not assert it wins; request verification evidence or steward decision.
- **Mobile:** Cards says its mobile is verified and CRM has a later `Updated` value but only the CRM verification status explicitly refers to address, not mobile. The mobile verification timestamps are absent. Under rule 3, no value can be selected solely from `Updated`; send to stewardship or request verified timestamps.
A correct answer preserves source, rule, evidence, and unresolved status. “Latest row wins” can overwrite an authoritative or verified value with a stale/unverified value.

### T06-Q3
For analytics in six months without source-system changes, a **consolidation** hub is a defensible near-term choice; a registry can be faster and less disruptive if query-time resolution is acceptable and source data can be linked reliably. Coexistence may fit a later phase when synchronization is needed; centralised/transactional MDM requires more source/process change. A staged registry/consolidation approach is acceptable if migration path, freshness, authority, and risks are explicit.

### T06-Q4
Retain immutable source-record references, match inputs and scores/rules, steward decision, before/after values, event/version IDs, master ID history, merge redirects, and downstream dissemination status. Unmerge must reverse crosswalks and reassign/restore identities without reusing IDs, publish correction events, reconcile consumers, and assess downstream reports through lineage. Idempotent consumers safely reprocess repeated events without duplicating effects.

### T06-Q5
High-confidence merges only after validation against labelled examples and conservative thresholds; ambiguous cases and critical-attribute conflicts go to stewardship; low-confidence pairs remain separate. Keep provenance, decisions, audit history, privacy controls, and unmerge procedure. Track precision/recall, false-merge incidents, steward backlog, resolution time, sync lag, and correction propagation. A wrong merge can contaminate analytics joins, ML features/training labels, and AI retrieval or entity linking; use lineage to identify affected outputs, correct/rebuild them, and retain evidence of the repair. Source-level views may remain authoritative for legal, fraud, or disputed evidence.

**Common misconceptions:** one survivorship rule fits every attribute; the latest update is always best; merge is irreversible; golden record should override all source views.

## E7. Topic 07 answer key

### T07-Q1
Entity resolution decides whether records refer to the same entity; identifier assignment creates or associates a stable distinguishing value; master-data maintenance governs the entity representation. Names and emails change, may be shared/reassigned, and can be inconsistently formatted. Namespace (e.g., `crm:customer:123`) prevents identical local IDs from colliding. IDs should not be reused because historical references would become ambiguous. Merge redirects and retirement must be explicit.

### T07-Q2
- TP = **810**.
- FP = proposed pairs − true proposed pairs = 900 − 810 = **90**.
- FN = true pairs − TP = 1000 − 810 = **190**.
- Precision = 810/900 = **0.90 = 90%**.
- Recall = 810/1000 = **0.81 = 81%**.
- F1 = 2 × 0.90 × 0.81 / (0.90 + 0.81) = 1.458/1.71 ≈ **0.853 = 85.3%**.
A false positive merges records that should remain separate; a false negative leaves true duplicates unresolved. The labelled sample must represent the intended population for the metrics to generalize.

### T07-Q3
All-pairs = n(n−1)/2 = 1,000,000 × 999,999 / 2 = **499,999,500,000** (about 5.0 × 10^11). Blocked = 10,000 × [100×99/2] = 10,000 × 4,950 = **49,500,000**. Reduction factor = 499,999,500,000 / 49,500,000 ≈ **10,101×** (approximately 10,000×). This assumes blocks are disjoint, each has exactly 100 records, and only within-block comparisons are made. True matches across blocks are never compared, creating a recall risk.

### T07-Q4
Policy should use stable namespaced IDs with a governed issuer, immutability/non-reuse, source-to-master crosswalks, redirect/merge history, and explicit correction/split process. Reference data needs owner, version, effective dates, approved changes, retired-code behaviour, mapping coverage, and consumer notification/reconciliation. A code may be in the allowed set but be invalid for a transaction date or domain; syntactic membership is not enough.

### T07-Q5
Set `T_high` for automatic merge only where labelled evaluation supports acceptable precision and risk; use `[T_low, T_high)` for review; below `T_low` remains unmatched/non-match under the policy. Tune on representative labelled data and compare false-merge harm against missed duplicates and review capacity. Monitor metrics by relevant subgroup and over time, re-evaluate on drift, and test cluster consistency. Pairwise A–B and B–C matches can transitively combine A and C even if A and C are not the same entity; cluster-level constraints and steward review may be needed.

**Common misconceptions:** score is probability without calibration; precision and recall have the same denominator; blocking has no effect on recall; reference-code validity is timeless.

## E8. Topic 08 answer key

### T08-Q1
JSON validates syntax/structure, not shared definitions. Interoperability requires stable asset identity/namespaces, semantic definitions, controlled vocabularies, ownership roles, classification mappings, lineage semantics, versioning, timestamps/timezones, provenance, and agreed loss/default behaviour. “Owner” needs a precise role definition.

### T08-Q2
A mapping cannot be final until both vocabularies are defined. One possible proposal (subject to semantics) is `Public → Open`, `Internal → Internal`, `Restricted → Restricted` only if the two restricted meanings are equivalent; `Confidential` may have no source equivalent. A reverse mapping from `Open` to `Public` may be reversible only if meanings and policy align. Never map ambiguous values to a less restrictive label by default. Preserve original value and mapping version; quarantine or reject unknown/ambiguous values or apply a documented conservative mapping with owner approval.

### T08-Q3
Point-to-point directed mappings: n(n−1) = 6×5 = **30**. Canonical: one inbound and one outbound per system = 2n = **12**. This is a simplified count; real complexity depends on semantic mismatch, versions, custom transformations, relationships, governance, and whether every pair truly needs bidirectional exchange. Canonical models reduce connection count but can become a bottleneck or force awkward common-denominator semantics. Direct mappings may be acceptable for few stable systems or unique semantics.

### T08-Q4
Assess consumers, required-field handling, semantics, security, and backward/forward compatibility. A new required field may break older producers/consumers that cannot supply or process it; changing `owner` semantics can silently misroute accountability even if parsing succeeds. Introduce a new version or a compatible transition according to the contract policy; define deprecation window, dual-read/write if needed, update mappings, run positive/negative/boundary/round-trip tests, reconcile counts/identities, monitor failures, and keep rollback. No single versioning policy is universal; justify it.

### T08-Q5
Target cannot represent field-level expressions/confidence directly, so information is lost. Options include keeping detailed lineage in source of truth and publishing a link/sidecar; mapping only dataset-level edges with an explicit declared loss and provenance; or rejecting the mapping if the target's consumers require the missing information. Test known field-level examples, edge counts, identity stability, confidence preservation in sidecar, and regression alerts. Never silently claim equivalent lineage.

**Common misconceptions:** valid JSON means equivalent meaning; every mapping can be round-tripped without loss; canonical mapping eliminates semantic governance; unknown values should be dropped.

---

## E9. Practical exercise solutions

### C1 — Metadata inventory and completeness
One acceptable design includes a stable asset ID; owner/steward; business definition; classification and basis; schema and keys; physical location; source/evidence; lineage references; latest load timestamp; quality status; lifecycle state; and maintenance cadence. Completeness = 8/10 × 100 = **80%** if eight eligible assets have all required fields current. A stale owner should not count as current completeness if the policy requires an active owner; report populated-but-stale separately from missing.

### C2 — Catalogue entry and discovery
A complete entry identifies the asset and explains purpose, ownership, classification, schema, CDEs, quality/freshness, lineage, certification, limitations, and access path. The analyst journey ends with an approved access decision and usable asset; the steward journey includes validating metadata, resolving definition conflicts, and reviewing stale/missing evidence. Scanner-harvested schema/run facts may be automated; business definitions, classification decisions, and certification normally require accountable review.

### C3 — Lineage and impact
There is no single correct diagram, but each edge must name its evidence and confidence. A strong impact report separates confirmed affected assets from possible consumers; includes field-level derivation for a CDE; names owners; tests schema compatibility, quality, and report reconciliation; and states blind spots. A “no dependency” claim is invalid if collectors do not cover all execution paths.

### C4 — CDE rules and quality metrics
Independent pass rates:
- Non-null ID: (1000−30)/1000 = **97.0%**.
- Valid currency: (1000−15)/1000 = **98.5%**.
- Unique key: (1000−20)/1000 = **98.0%**.
- Non-negative amount: (1000−8)/1000 = **99.2%**.

Given 55 distinct rows fail at least one rule, all-four pass rate = (1000−55)/1000 = **94.5%**. The sum of rule failure counts is 73, but that counts row-rule failures, not distinct rows; overlaps explain the difference.

### C5 — Freshness and SLO
On-time days are all values at or before 07:00. Late days: 07:03, 07:12, 07:01 = 3. On-time = 17/20 = **85%**, so the illustrative 95% SLO is **not met**. An early-warning alert may fire when upstream readiness is trending late or the estimated completion time approaches the cutoff; an SLO breach is assessed against the defined measurement window. Document timezone, business calendar, publication event, and incident response.

### C6 — Golden record
Full-credit submissions use attribute-specific rules, source authority, verification timestamps, provenance, and explicit ambiguity handling. They do not invent evidence for missing verification. Include reversible merge/unmerge, source crosswalk, consumer change events, idempotency, and reconciliation. Exact chosen source values depend on the synthetic records and declared rules.

### C7 — Entity resolution
Use T07-Q2's result: precision **90%**, recall **81%**, F1 approximately **85.3%**. Threshold experiments must be measured, not predicted as facts: increasing the auto-merge threshold generally reduces automatic merge volume and false positives but may increase false negatives and review workload; lowering it often increases recall/volume and can reduce precision. Effects depend on score distributions and review-band design. Validate with labelled, representative, time-aware samples; monitor drift and subgroup error rates.

### C8 — Interoperability
A good mapping specification has source/target concept, field, type, semantic definition, transformation, namespace/identity rule, version, loss/default/unsupported behaviour, and test evidence. Choose an API for request/response needs, events for asynchronous change propagation, or bulk files for high-volume periodic exchange only when ordering, replay, security, and reconciliation controls fit the use case. Tests include expected valid cases, invalid/unknown values, boundaries, round-trip where appropriate, compatibility, classification non-downgrade, identity collisions, and lineage/provenance preservation. A syntax-valid payload can still map owner roles incorrectly or lose lineage meaning.

---

## E10. Integrated scenario evaluation rubrics

### D1 — Enterprise metadata and lineage design (30 points)

| Criterion | Points | Full-credit evidence |
|---|---:|---|
| Scope, assumptions, requirements | 3 | Facts and assumptions separated; stakeholders and exclusions explicit |
| Metadata model and ownership | 3 | Three categories; stable IDs; source/freshness/lifecycle and accountable owners |
| Catalogue and classification | 3 | Persona journey, classification basis, access workflow, stewardship |
| Lineage and impact | 4 | Dataset/field paths, edge evidence, confidence, blind spots, reproducible impact |
| Quality and CDEs | 3 | Decision-linked CDEs, testable rules, denominator, thresholds and remediation |
| Observability and SLOs | 3 | Measurable SLIs/SLOs, dependency feasibility, alerts/incident ownership, and batch/streaming late-event/replay semantics where relevant |
| MDM, matching and identifiers | 4 | Attribute-level survivorship, labelled metrics, namespaces, unmerge/sync |
| Interoperability | 3 | Semantic mapping, versioning, explicit loss policy, conformance tests, and a justified API/event/bulk-file exchange pattern |
| ADRs, risks, validation | 4 | At least five useful ADRs; alternatives, risks, triggers and evidence |

Accept centralised, federated, hybrid, registry, consolidation, coexistence, canonical, or direct designs where the assumptions and consequences justify them. Do not award full credit for diagrams without validation evidence.

### D2 — The report is late and wrong (15 points)
Award up to 3 points each for: (1) distinct freshness/quality/catalogue/lineage signals; (2) correct distinction between technical success and fitness for use; (3) named accountable incident roles; (4) safe hold/quarantine/correction and communication; (5) evidence-based recovery and closure. Full credit rejects unknown currency codes from silent defaulting and explicitly handles lineage uncertainty.

### D3 — Customer merge dispute (15 points)
Award up to 3 points each for containment and impact; reversible unmerge and crosswalk correction; matching rule/threshold evaluation; downstream synchronization/reconciliation; and provenance, lineage, quality, and regression prevention. Deleting the record alone can break references and erase evidence.

### D4 — Interoperability failure (15 points)
Award up to 3 points each for correctly classifying structural/semantic/identity/loss failures; explicit mapping and namespace contract; versioning and compatibility; conformance and reconciliation; and trade-off analysis of direct versus canonical mapping.

### D5 — Architecture defence (10 points)
Award 2 points per challenge for a principle, concrete risk, decision rule, and supporting evidence. Answers should explain why oversized metadata records can mix lifecycle/grain and increase update coupling; absent lineage is not proof of no dependency; thresholds are risk-specific; similarity scores require labelled evaluation and review bands; and JSON syntax does not prove semantic compatibility.

For each integrated scenario, a defensible alternative earns credit. Unsupported assertions, unlabelled assumptions, hidden uncertainty, or “tool will handle it” answers should lose points.

---

# Section F — Readiness assessment and gap log

## F1. Topic readiness checklist

Mark **Ready** only when you can answer the corresponding questions and produce the evidence. Reading alone is not completion.

- [ ] **Topic 01:** classify metadata, design an inventory/schema, assign accountability, and measure metadata quality.
- [ ] **Topic 02:** design catalogue discovery, classification propagation, stewardship, and access workflow.
- [ ] **Topic 03:** draw end-to-end dataset/field lineage, label evidence and blind spots, and perform impact analysis.
- [ ] **Topic 04:** select CDEs, distinguish dimensions/rules/metrics/thresholds, and compute quality results with correct denominators.
- [ ] **Topic 05:** define signals/SLIs/SLOs/alerts, test freshness feasibility, and specify incident response.
- [ ] **Topic 06:** choose an MDM style, define attribute-level survivorship, preserve provenance, and design synchronization/unmerge.
- [ ] **Topic 07:** define identifiers and reference governance, blocking and thresholds, and compute precision/recall/F1.
- [ ] **Topic 08:** map metadata semantics, version contracts, report loss, and design conformance tests.
- [ ] **Integrated:** defend an architecture and its risks, alternatives, validation, and operating ownership.

## F2. Scorecard

Record scores from Section B and the relevant Section C/D evidence. Use the same scoring scale for every topic.

### Primary written-question score (Section B)

| Topic | Question IDs | Points earned | Points available | Score % | Topic gate/evidence reviewed? | Status |
|---|---|---:|---:|---:|---|---|
| 01 Metadata | T01-Q1–Q5 | | 15 | | | |
| 02 Catalogue | T02-Q1–Q5 | | 15 | | | |
| 03 Lineage | T03-Q1–Q5 | | 15 | | | |
| 04 Quality | T04-Q1–Q5 | | 15 | | | |
| 05 Observability | T05-Q1–Q5 | | 15 | | | |
| 06 MDM | T06-Q1–Q5 | | 15 | | | |
| 07 Reference/ER/IDs | T07-Q1–Q5 | | 15 | | | |
| 08 Interoperability | T08-Q1–Q5 | | 15 | | | |
| **Overall Section B** | **T01-Q1–T08-Q5 (40 questions)** | | **120** | | | |

**Calculation:** Section B overall score = total Section B points earned / 120 × 100. Topic score = points earned for that topic's five questions / 15 × 100. Because scores are discrete, a topic must earn at least 11/15 points (73.3%) to meet the recommended 70% floor; 10/15 is only 66.7%. Do not average topic percentages to produce the overall score; the equal five-question topic design already gives each topic 15 available points.

### Practical and integrated evidence (tracked separately)

| Evidence set | IDs | Points available | Completion/evidence status | Reviewer notes |
|---|---|---:|---|---|
| Practical exercises | C1–C8 | Not numerically scored by default | | Record artefacts and pass/gap decisions; do not invent a point denominator. |
| Integrated architecture scenarios | D1–D5 | 85 total (D1 30, D2 15, D3 15, D4 15, D5 10) | | Use explicit rubrics; keep these scores separate from the Section B percentage unless weights were declared in advance. |

Readiness requires both the recommended Section B score thresholds and completion of practical/integrated evidence. A high written score cannot compensate for an incomplete topic gate or a high-impact unresolved gap.

### Recommended readiness decision

- **Ready to begin the final project:** at least 85% overall; every topic at least 70%; all eight topic gates signed off; integrated exercise completed; no unresolved gap older than one week; no topic status is “Needs revision.”
- **Conditionally ready:** score thresholds met but evidence or a topic gate is incomplete. Finish the missing gate before treating the project as ready.
- **Not ready:** overall or topic threshold missed, repeated misconception remains, or a high-impact gap is unresolved. Remediate the relevant topic and reattempt.

These are the roadmap's recommended thresholds and process, not a universal benchmark.

## F3. Gap log template

| Question ID | Topic file | Score / issue | Specific misconception or evidence gap | Remediation action | Owner/reviewer | Reattempt date | Reattempt result | Closed? |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

Examples of actionable gaps:
- “T03-Q5: treated missing lineage as proof of no downstream use; inspect collector coverage, add blind-spot register, repeat impact analysis.”
- “T07-Q2: used all proposed pairs as recall denominator; recompute TP/FP/FN and explain each denominator.”
- “T08-Q2: mapped ambiguous classification to a less restrictive label; define semantics and conservative unknown-value handling.”

## F4. Final-project readiness checklist

Before starting `Projects/11-enterprise-metadata-and-lineage-design.md`, confirm:

- [ ] Project requirements are read if that file has been populated; if it remains empty, use the roadmap's proposed project shape and label it as a recommendation.
- [ ] All eight topic gates are completed and evidence reviewed by another person.
- [ ] Prerequisites P1–P12 have been checked; weak prerequisites have a remediation plan.
- [ ] Requirements, facts, assumptions, constraints, scope, and exclusions are recorded.
- [ ] Metadata inventory and schema have stable IDs, categories, owners, sources, lifecycle, and quality checks.
- [ ] Catalogue design supports at least one end-to-end persona journey and includes classification/access workflows.
- [ ] Lineage covers both reports at the appropriate dataset/field level; evidence, confidence, and blind spots are explicit. Include batch plus at least one streaming/incremental path where relevant, with event-time/processing-time, lag, late-event, replay/idempotency, and lineage implications.
- [ ] A representative change has a reproducible impact report with named owners and tests.
- [ ] CDEs trace to business decisions; rules are testable and have explicit denominators, thresholds, owners, and remediation.
- [ ] Observability indicators and SLOs are measurable and feasible against the dependency chain; incident response is defined.
- [ ] MDM and entity resolution include identifiers, per-attribute survivorship, provenance, synthetic-data evaluation, synchronization, and wrong-merge recovery.
- [ ] Interoperability mapping defines identity, semantics, versions, loss/default behaviour, conformance tests, and a justified API/event/bulk-file exchange pattern.
- [ ] At least five ADRs record context, decision, alternatives, consequences, risks, and revisit triggers.
- [ ] A validation report, risk register, limitations, and owned gap list exist.
- [ ] The design can be explained to a non-specialist in ten minutes and defended against at least five reviewer questions.
- [ ] Only synthetic data is used; no paid infrastructure or production access is required for this design exercise.

## F5. Suggested reattempt plan

1. Reattempt failed questions several days after remediation, closed-book first.
2. Require two consecutive successful attempts for a previously repeated misconception.
3. If a second attempt fails, redo the mapped topic exercise rather than memorizing the answer.
4. Ask a reviewer to inspect the artefact for design questions and calculations.
5. Re-run the scorecard and keep the previous score for trend comparison.
6. Do not start the final project solely because the average is high if one critical topic gate or a high-impact gap remains open.

---

# Appendix — Quick formulas and reviewer prompts

## Matching metrics

- `Precision = TP / (TP + FP)`
- `Recall = TP / (TP + FN)`
- `F1 = 2 × Precision × Recall / (Precision + Recall)`

Precision answers “of the proposed matches, what fraction is correct?” Recall answers “of all true matches in the labelled ground truth, what fraction did we find?” State the labelled sample and its limits.

## Pair-comparison count

- All unordered pairs: `n(n−1)/2`
- Within disjoint blocks: sum `b_i(b_i−1)/2` for each block of size `b_i`
- Blocking reduces work but can miss true pairs assigned to different blocks; measure pair completeness/recall.

## Quality and SLO formulas

- Rule pass rate: `eligible rows passing rule / eligible rows × 100`
- Completeness: `eligible records with required value / eligible records × 100`
- Coverage: `assets/fields with specified lineage status / eligible assets/fields × 100`
- SLO compliance: `successful observations / eligible observations × 100`
- Always define eligibility, exclusions, time window, timezone, and what counts as success.

## Reviewer prompts

1. Which claims are observed facts, and which are assumptions or inferred relationships?
2. What is the denominator and why is it appropriate?
3. What happens when metadata is missing, stale, conflicting, or untrusted?
4. What is the operational response when a rule or SLO fails?
5. Who owns the decision and who is notified?
6. What evidence would falsify the design's main assumption?
7. Which information is lost when metadata crosses system boundaries?
8. How can a wrong decision be reversed without erasing audit history?
9. What changes if the business risk, scale, latency, or governance model changes?
10. What evidence would convince a reviewer who did not build the solution?

---

## Completion statement

The question bank is designed to validate the eight topics and support the roadmap's proposed final project. It is a study aid, not a substitute for topic completion gates, peer review, or a populated project specification. When the source topic or project files gain explicit requirements, reconcile this assessment with them before treating it as authoritative.
