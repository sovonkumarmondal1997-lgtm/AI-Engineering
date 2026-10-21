# Data Quality Dimensions and Critical Data Elements

> **Module:** Stage 2D — Data Architecture  
> **Module path:** `11-Metadata-Lineage-Quality-and-Master-Data/`  
> **Topic:** 04 — Data quality dimensions and critical data elements  
> **Level:** Beginner → Intermediate → Advanced  
> **Scenario:** Northbridge Bank, a fictional organisation; all data and values are synthetic  
> **Status of examples:** Thresholds and service expectations below are illustrative design choices, not universal industry standards.

## 1. Purpose, scope, prerequisites, and learning outcomes

### 1.1 Purpose

Data quality is the degree to which data are **fit for a stated use**. Quality is not an intrinsic label that a dataset permanently earns. A customer address might be sufficiently complete for broad regional analysis but unfit for a returned-mail workflow. A currency amount might be valid as a number yet unsafe for an exposure report if its currency code is wrong. A record can pass format checks and still describe reality incorrectly.

This topic establishes a practical way to decide what “good” means, identify the elements where failure matters most, convert business needs into executable controls, interpret results responsibly, and route defects to accountable people.

The roadmap positions this topic after:
1. business, technical, and operational metadata;
2. data catalogues, discovery, and classification; and
3. end-to-end lineage and impact analysis.

It also calls out freshness, availability, and service-level design as prerequisites (P8). This document uses that context but does not replace the later observability topic.

### 1.2 Scope

This document covers:

- quality dimensions and the differences between dimensions, rules, measurements, thresholds, and acceptance criteria;
- profiling, CDE identification, business-impact prioritisation, and ownership;
- field-, record-, dataset-, relationship-, and cross-system rules;
- measurement populations, null semantics, sampling, time windows, and score interpretation;
- preventive and detective controls, severity, quarantine, remediation, exceptions, and root-cause prevention;
- batch, incremental, and streaming quality controls;
- quality considerations for analytics, reporting, ML datasets, and AI knowledge sources;
- practical CDE, rule-inventory, and quality-report templates.

It does **not** prescribe one vendor, one universal score, one fixed threshold for every organisation, or a complete master-data-management design. Topic 05 should extend operational monitoring and quality service levels; Topics 06–07 should extend master data, identifiers, reference data, and entity resolution.

### 1.3 Prerequisites

Review the following concepts before proceeding:

| Prerequisite | Why it matters here | Practical readiness check |
|---|---|---|
| Topic 01: business, technical, and operational metadata | Rules need definitions, stable asset/field identifiers, ownership, and execution evidence | Describe a field’s meaning, physical type, owner, steward, and last refresh |
| Topic 02: catalogues, discovery, and classification | Quality metadata must be discoverable and classified appropriately | Find a synthetic field and explain its definition, classification, owner, and use |
| Topic 03: lineage and impact analysis | CDE prioritisation and root-cause analysis depend on source-to-consumer paths | Trace one report field upstream and list downstream consumers |
| P8: freshness, availability, and SLO design | A “fresh enough” rule must match the consumer’s time budget | Write an SLO with a population, time window, target, and response |
| Ownership, keys, contracts, and reconciliation | Quality rules need decision rights and reliable comparison keys | Explain who approves a rule and how duplicates or missing batches are reconciled |

### 1.4 Learning outcomes

After completing this topic, you should be able to:

1. define the main quality dimensions and distinguish overlapping failure types;
2. select CDEs by tracing business decisions, impact, exposure, and lineage;
3. turn a business requirement into an atomic, testable, versioned rule;
4. state the asset, population, denominator, null policy, measurement window, threshold, owner, severity, and response for each rule;
5. profile data and reproduce completeness, validity, uniqueness, and other metrics;
6. explain why a high aggregate score does not prove fitness for every use;
7. design a proportional control strategy for batch, incremental, and streaming data;
8. choose among rejection, quarantine, correction, and documented acceptance;
9. connect quality results to metadata, classification, lineage, observability, and governance; and
10. produce a CDE register, rule inventory, quality report, remediation plan, and decision record.

### 1.5 Roadmap alignment

The module roadmap specifically calls for:
- six foundational dimensions: completeness, validity, accuracy, consistency, uniqueness, and timeliness;
- CDE selection from business decisions and impact;
- atomic rules with owner, severity, threshold, and action;
- stated populations and reproducible scores;
- explicit treatment of accuracy;
- remediation and prevention, including fixing upstream causes;
- tiered controls rather than identical controls for every field;
- a CDE register, rule inventory, quality report/remediation plan, and an ADR for CDE selection and thresholds;
- Exercise A: CDE register and rules for a synthetic exposure report;
- Exercise B: measure synthetic customer data with duplicates and invalid dates, classify defects, identify causes, and calculate before/after results.

The broader module uses a fictional Northbridge Bank scenario and expects quality design to integrate with metadata, field-level lineage for CDEs, observability, master data, and a final enterprise architecture package. These are learning-design recommendations, not evidence that the repository’s previously empty topic or project files already contain such requirements.

---

## 2. Beginner foundations and terminology

### 2.1 Fitness for use

A quality claim needs a consumer, a decision, and a time context.

For example:

- **Use A — regional analytics:** a customer’s exact street address may be optional if only country-level reporting is required.
- **Use B — regulatory exposure report:** amount, currency, reporting date, and counterparty identity may need strict completeness, validity, reconciliation, and lineage.
- **Use C — customer notification:** a contact channel may need to be present, current, legally usable for that purpose, and deliverable.
- **Use D — ML training:** correct labels, representative coverage, leakage controls, and appropriate time cut-offs matter; a syntactically valid row can still be misleading.
- **Use E — AI retrieval/knowledge source:** content freshness, source authority, access permissions, provenance, and duplicate or contradictory documents may matter as much as field-level null checks.

**Why it matters:** quality targets should be justified by the consequences of failure. Applying the strictest possible rule to every field creates cost and unnecessary rejection. Applying one lenient rule to every use can let critical defects reach decisions.

### 2.2 Core terms

| Term | Meaning | Example |
|---|---|---|
| Data quality | Fitness of data for a specified use | Exposure data reconcile to an approved ledger snapshot |
| Quality dimension | A category of quality concern | Completeness |
| Quality rule / assertion | A testable statement about data | Every active exposure row has a non-null reporting date |
| Measurement / metric | A calculated observation of the rule or population | 998,700 of 1,000,000 eligible rows pass |
| Threshold / target | A decision boundary applied to a measurement | At least 99.5% pass, subject to a zero-tolerance critical exception |
| Business acceptance criterion | The condition under which a consumer or process may proceed | No unresolved critical exposure defects; lower-severity exceptions within an approved budget |
| Defect | A record, field, relationship, or dataset that violates a rule | Currency code `USX` is not in the approved currency reference |
| Profile | Summary of observed data characteristics | Null rate, distinct count, min/max, value frequencies |
| CDE | A data element whose failure has material business impact for one or more uses | Exposure amount used in a regulatory report |
| Control | A preventive, detective, or corrective mechanism | Reject unknown currency codes at ingestion |
| Exception | A reviewed, authorised deviation from a rule | One delayed source file accepted for internal analysis but excluded from regulatory output |
| Remediation | Action to correct a defect or its cause | Fix source mapping, repair affected records, replay affected partitions |
| Root cause | The underlying mechanism that produced defects | Currency mapping omitted a newly introduced source code |
| Evidence | Verifiable record of execution, result, and decision | Rule version, input snapshot, counts, failed keys, run ID, approver |

### 2.3 Dimension vs rule vs measurement vs threshold vs acceptance

These terms are related but not interchangeable.

| Layer | Question | Example |
|---|---|---|
| Business need | What decision must be safe? | Regulatory exposure must not be misstated by a missing currency |
| Dimension | What kind of quality is at risk? | Completeness, validity, accuracy |
| Rule | What exactly is tested? | Every in-scope exposure row has a currency code in the approved reference set |
| Measurement | What did the test observe? | 9,997 of 10,000 eligible rows passed |
| Threshold | What numerical or logical boundary applies? | Validity ≥ 99.9% for the batch |
| Acceptance criterion | Can the consumer proceed, given severity and context? | Do not publish if any critical currency defect remains, even if the percentage passes |

A rule may be binary (all keys unique) or rate-based (at least 99.5% of eligible rows have a date). A threshold may be numeric, logical, relative to a baseline, or based on a control limit. An acceptance criterion can combine multiple rules, severity overrides, freshness, reconciliation, and authorised exceptions.

**Important:** “99.9% valid” is not an acceptance criterion until the population, denominator, treatment of critical failures, measurement window, and consequence of failure are specified.

### 2.4 Quality dimensions

Dimensions are lenses for classifying risks. They often overlap; do not force every defect into only one dimension when multiple assertions are relevant.

| Dimension | Core question | Example test | Common limitation |
|---|---|---|---|
| **Completeness** | Is required data present for the intended population? | Active accounts have a non-null account identifier | A non-null placeholder such as `UNKNOWN` may still be incomplete semantically |
| **Validity** | Does the value satisfy type, range, format, domain, or rule constraints? | `currency_code` exists in the approved code set | Valid format does not prove the value is true |
| **Accuracy** | Does the value correctly represent the real-world entity or event? | Exposure amount agrees with the authoritative ledger for the same cut-off | Often needs an authoritative source, reconciliation, or sampled verification |
| **Uniqueness** | Is each intended entity/event represented according to the identity and grain policy? | One current record per `customer_id` in a current-state table | Multiple rows can be valid in history tables; duplicate identity must be defined |
| **Consistency** | Do related values agree within or across representations under the same semantics and time cut-off? | A reporting currency is consistent across detail and summary totals | Systems may legitimately differ because of timing, scope, or definitions |
| **Timeliness** | Is data available and current within the consumer’s allowed time? | Snapshot published by 06:00 local reporting time | A recent value can still be wrong or incomplete |
| **Integrity** | Are relationships and structural constraints preserved? | Every non-null `customer_id` in exposure rows references a known customer | Referential integrity cannot prove that the link is semantically correct |
| **Conformity** | Does data follow an agreed standard, representation, or contract? | Date is ISO-formatted; country code follows the agreed convention | Conformity overlaps validity; define it separately only when the standard itself matters |

Other useful dimensions in some contexts include plausibility/reasonableness, precision, stability, accessibility, and representativeness. Add a dimension only when it clarifies a business risk and leads to measurable assertions. A large list of vaguely defined dimensions adds little control value.

### 2.5 How to distinguish overlapping defects

A synthetic record has `amount = 1000`, `currency_code = 'USX'`, and `customer_id = 42`.

- `currency_code` is present: completeness passes.
- `USX` is not in the approved reference list: validity fails.
- The amount may be numerically accurate in source currency but wrong when interpreted as USD: accuracy/semantic correctness may fail.
- If another system stores `USD` for the same transaction and cut-off, consistency fails unless an approved mapping explains the difference.
- If `customer_id = 42` does not exist in the customer master, integrity fails.
- If the row arrives after the report cut-off, timeliness fails.

**Enterprise application:** store the failing rule IDs and dimensions rather than only a generic `bad_row = true`. One defect may have multiple downstream consequences, but deduplicate root-cause incidents so teams are not flooded with redundant alerts.

---

## 3. Critical data elements (CDEs) and business-impact analysis

### 3.1 Definition and purpose

A **critical data element** is a field or logically defined element whose failure could materially affect a business decision, key process, customer outcome, financial result, risk exposure, compliance obligation, or trusted product. Criticality is relative to a use and context. The same field can be critical for one report and ordinary for another.

A CDE is not automatically the most sensitive field, the most frequently used field, or the field with the highest null rate. Classification/sensitivity, business criticality, and measured quality are distinct metadata attributes:

- **Sensitivity/classification:** what handling and access controls does the data require?
- **Criticality:** how consequential is a failure for a business use?
- **Quality state:** how well does the current population meet defined requirements?

### 3.2 Identify CDEs from decisions, not from column names alone

Use this process:

1. **Name the decision or process.** Examples: calculate regulatory exposure, approve a credit limit, notify a customer, reconcile a settlement.
2. **Identify the consumer and acceptance conditions.** Who relies on the result? What errors would change the decision or breach an obligation?
3. **Trace the relevant outputs upstream.** Use Topic 03 lineage to connect report measures and dimensions to source fields, joins, transformations, and manual steps.
4. **Identify candidate fields and relationships.** Include keys, dates, amounts, units/currencies, status, reference codes, and derived fields.
5. **Assess impact.** Estimate plausible financial, operational, customer, regulatory, reputational, and model-risk consequences. Do not invent monetary values when none are known.
6. **Assess exposure and reach.** Consider frequency of use, number of consumers, downstream blast radius, volume, change rate, and whether defects are hard to detect.
7. **Assess detectability and recoverability.** A defect that is difficult to detect or expensive to reverse may deserve stronger controls.
8. **Assign accountable ownership.** Name a business CDE owner and the people responsible for rule stewardship and source remediation.
9. **Select tiered controls.** Decide which dimensions matter for this use, what evidence is required, where rules run, and what happens on failure.
10. **Review on change.** Reassess when definitions, lineage, use, regulation, source systems, classification, or consumer populations change.

A simple prioritisation aid is a risk score. It is a decision aid, not an objective truth:

\[
\text{Priority score} = \text{Impact} \times \text{Likelihood} \times \text{Exposure}
\]

If each factor uses a 1–5 ordinal scale, a score of 4×3×5 = 60 can help sort candidates. But ordinal values do not guarantee precise mathematical ratios. Record the rationale and use hard overrides for mandatory controls. A single “criticality score” must not erase mandatory obligations or expert judgement.

### 3.3 CDE register — synthetic example

The following thresholds are proposed for this fictional scenario only.

| CDE ID | Element / asset | Business use and consequence | Impact / priority rationale | Classification | Business owner | Steward / rule owner | Lineage / source | Required control posture |
|---|---|---|---|---|---|---|---|---|
| CDE-001 | `exposure.amount` in `gold.exposure_report` | Regulatory exposure; wrong amount may misstate reported exposure | Critical: financial and regulatory consequence; derived from multiple sources | Confidential (illustrative) | Head of Risk Reporting | Risk Data Steward | Ledger + rates → curated exposure → report; field-level lineage required | Reconcile to approved source/cut-off; block publication for unresolved material mismatch |
| CDE-002 | `exposure.currency_code` | Determines interpretation and conversion of amount | Critical: wrong code can multiply error through FX conversion | Internal/Confidential by policy | Head of Risk Reporting | Risk Data Steward | Ledger / rate mapping → exposure report | Required; approved code set; mapping version; unknown values quarantined |
| CDE-003 | `exposure.as_of_date` | Defines reporting cut-off and time consistency | Critical: stale or mixed snapshots can misstate totals | Internal | Head of Risk Reporting | Reporting Steward | Source snapshot → transformation → report | Required; one approved cut-off per report; stale batch blocks publication |
| CDE-004 | `customer.customer_id` | Joins customer, exposure, and communications | High: broken or duplicate keys distort counts and relationships | Confidential (if linkable under policy) | Customer Domain Owner | Customer Data Steward | CRM/core systems → customer curated asset | Non-null; uniqueness according to table grain; referential integrity |
| CDE-005 | `customer.contact_email` | Customer notification for eligible customers | High for notification use; not necessarily required for all analytics | Personal/confidential per policy | Customer Operations Owner | Customer Data Steward | CRM → customer 360 | Completeness conditional on contact eligibility and permission; format is not proof of deliverability |
| CDE-006 | `reference.currency_code` | Validates currencies and mappings | High: reference defects contaminate many consumers | Internal | Reference Data Owner | Reference Data Steward | Governed reference source → quality/catalogue consumers | Versioned, unique code set; changes reviewed and propagated |
| CDE-007 | `ml.customer_label` | Supervised model training label | High when label errors affect model decisions | Restricted according to dataset policy | Model/Data Product Owner | ML Data Steward | Source outcomes → label generation → training snapshot | Label definition/version, time cut-off, sampled verification, leakage and coverage checks |

**How to use this register:** replace role titles with named roles or accountable groups in the real operating model; record stable asset IDs and lineage references; link each CDE to its rules, exceptions, quality history, classification, and intended use. Do not store sensitive raw values in the register or broad quality reports.

### 3.4 CDE tiers and control depth

A practical tiering scheme:

- **Tier 1 — critical:** mandatory rule coverage for all relevant dimensions; deterministic controls where possible; strong evidence; field-level lineage; strict failure handling for high-consequence defects; named business acceptance authority.
- **Tier 2 — important:** automated controls for material risks; thresholds tied to use; quarantine or alerting based on severity; periodic review.
- **Tier 3 — supporting:** baseline schema/contract checks and profiling; sampled or lower-frequency checks where justified; explicit known limitations.

Tiers should reflect impact and use, not merely table size. Do not apply the same strictness to all columns by default. Conversely, do not use “non-CDE” as an excuse to ignore privacy, security, contractual, or structural requirements.

### 3.5 Ownership and accountability

Separate the roles so that no one assumes “the quality team owns the data”:

| Role | Accountability | Typical decision |
|---|---|---|
| Business CDE owner | Defines intended use, materiality, acceptance criteria, and risk appetite | Approves threshold and material exception |
| Data steward / rule owner | Maintains definition, rule logic, dimension, threshold rationale, and review cadence | Reviews rule change and false-positive trend |
| Source-system / domain owner | Corrects source process or data capture and prevents recurrence | Implements source validation or mapping fix |
| Data engineer / platform operator | Implements reliable execution, evidence, retries, quarantine, and monitoring | Ensures rule executes against the intended snapshot |
| Consumer / product owner | Defines consumer-specific fitness and decides whether output can be used | Accepts, restricts, or rejects output under policy |
| Risk/compliance/control owner | Advises or approves controls where formal obligations apply | Determines whether an exception is permissible |
| Incident commander / operations lead | Coordinates time-critical triage and communication | Escalates incident and tracks recovery |

A single person may fill more than one role in a small team, but the decision rights should still be explicit. For material exceptions, separate the person requesting an exception from the authorised approver where feasible.

---

## 4. Turning business requirements into testable rules

### 4.1 A rule specification must be executable and governable

Every rule should state:

1. **Rule ID and version**
2. **Asset and field/relationship** (stable identifier, not only display name)
3. **Intended use and population**
4. **Dimension(s)**
5. **Predicate** — exactly what passes or fails
6. **Measurement** — count, rate, delta, reconciliation difference, lag, distribution statistic, etc.
7. **Denominator and null policy**
8. **Threshold / acceptance condition**
9. **Measurement window and evaluation schedule**
10. **Severity and consumer impact**
11. **Accountable CDE/business owner and rule owner**
12. **Failure action** — block, quarantine, alert, correct, or accept by exception
13. **Evidence** — input snapshot/version, execution ID, rule version, counts, failed keys or secure reference
14. **Exception expiry and review** if exceptions are allowed

Avoid rules such as “customer data should be good” or “completeness should be high.” Those statements cannot be reproduced, tested, or audited.

### 4.2 Convert a requirement step by step

**Business statement:** “The exposure report must use valid currency codes.”

- **Decision:** report exposure by currency and convert with an approved rate.
- **Asset:** `gold.exposure_report`.
- **Population:** rows included in the reporting cut-off, excluding explicitly documented non-financial summary rows if any.
- **Dimension:** validity and conformity; accuracy may also be relevant to the mapping.
- **Predicate:** `currency_code` is non-null and matches an active code in the reference set effective at `as_of_date`.
- **Measurement:** count and percentage of eligible rows passing; list failed keys in a restricted issue store.
- **Threshold:** 100% valid for Tier 1 rows in the published report, because an unknown currency prevents safe interpretation. This is an illustrative business acceptance choice, not a universal standard.
- **Owner:** Head of Risk Reporting (business acceptance); Risk Data Steward (rule); source mapping owner (fix).
- **Failure response:** quarantine affected rows; block publication if any material row is unresolved; open an incident and check the upstream mapping version.
- **Evidence:** reference-set version, input snapshot ID, rule version, pass/fail counts, issue IDs, decision and approver.

This is testable because the population, predicate, threshold, owner, and action are explicit.

### 4.3 Rule granularity

| Level | Example | Why use it | Main trade-off |
|---|---|---|---|
| Field | `amount >= 0` for non-reversal exposure rows | Fast, local validation | Cannot prove cross-field semantics |
| Record | `start_date <= end_date` | Checks relationships within one record | Requires clear null semantics and business conditions |
| Dataset | Row count within a justified range; schema unchanged | Detects batch-level anomalies | May flag legitimate business variation |
| Key / uniqueness | One current row per `customer_id` | Protects entity grain and joins | Historical tables need composite/versioned keys |
| Relationship | Every non-null `customer_id` references a customer | Protects referential integrity | Orphan can be caused by late-arriving data |
| Cross-system | Source total equals curated total at the same cut-off | Reconciliation and accuracy evidence | Systems must share scope, time, currency, and exclusions |
| Time series / stream | Event-time lag within budget; no unexpected duplicate event IDs | Supports freshness and delivery semantics | Late arrivals and replay require explicit policy |
| Statistical / distribution | `amount` distribution or category mix remains within approved control limits | Detects unexpected shifts | Drift is a signal, not automatically a defect |

### 4.4 Rule inventory — synthetic example

All targets below are illustrative and must be approved for the actual business use.

| Rule ID | Asset / CDE | Dimension | Test / measurement | Population / denominator / window | Threshold or acceptance | Severity | Accountable owner / rule owner | Failure response |
|---|---|---|---|---|---|---|---|---|
| DQ-001 v1 | `gold.exposure_report.exposure_amount` / CDE-001 | Accuracy, integrity | Join by approved exposure key and compare amount after the governed FX mapping at the same cut-off; record unmatched keys and absolute delta | All in-scope exposure rows in one approved report snapshot; denominator is the in-scope row count and matched-key count is reported separately | Illustrative acceptance: 0 unmatched material keys and absolute delta ≤ 0.01 reporting-currency units per key after documented rounding; owner must approve/change the tolerance before production | Critical | Risk Reporting Owner / Risk Data Steward | Block report; quarantine affected slice; investigate source, join, FX and cut-off |
| DQ-002 v1 | `gold.exposure_report.currency_code` / CDE-002 | Validity, conformity | Non-null and member of effective-dated approved currency reference | All published Tier 1 exposure rows at the reporting cut-off; denominator is the Tier 1 row count | 100% valid rows | Critical | Risk Reporting Owner / Risk Data Steward | Quarantine; block publication while any material unknown remains |
| DQ-003 v1 | `gold.exposure_report.as_of_date` / CDE-003 | Completeness, consistency, timeliness | Non-null; all rows match approved reporting cut-off; snapshot age within schedule | All rows in one report snapshot; compare with the approved cut-off and publication deadline | 100% rows use one approved cut-off; published by agreed deadline | Critical | Risk Reporting Owner / Reporting Steward | Stop publication; alert operations; validate late-arriving inputs |
| DQ-004 v1 | `silver.customer.customer_id` / CDE-004 | Completeness, uniqueness | Non-null IDs; duplicate count at defined grain | All rows in the current-state customer snapshot; denominator is total rows for completeness and non-null IDs for duplicate-excess rate | 100% non-null; 0 duplicate excess rows in the current-state table | High | Customer Domain Owner / Customer Steward | Quarantine ambiguous duplicates; deduplicate only under approved survivorship rule |
| DQ-005 v1 | `silver.exposure.customer_id` → `silver.customer.customer_id` / CDE-004 | Integrity | Count exposure rows with non-null customer ID missing from customer snapshot | All exposure rows with non-null customer IDs at publication cut-off; denominator is non-null references, measured after the agreed lateness window | 0 unresolved orphans at publication cut-off | High | Customer Domain Owner / Integration Steward | Hold or quarantine orphan rows; distinguish late arrival from invalid key |
| DQ-006 v1 | `silver.customer.contact_email` / CDE-005 | Completeness, validity | For active customers eligible and permitted for email contact, measure usable-value completeness and syntax validity separately | Completeness denominator = all eligible/permitted active customers; syntax denominator = nonblank values; one customer snapshot | ≥ 98% usable-value completeness (proposed); syntax failures tracked separately; no claim of deliverability | Medium/High by use | Customer Operations Owner / Customer Steward | Route failures to steward; do not invent an email or bypass contact preferences |
| DQ-007 v1 | `ref.currency.currency_code` / CDE-006 | Uniqueness, validity, integrity | No duplicate active code; all codes conform to governed code policy; effective dates non-overlapping | All active currency reference records at release; uniqueness is checked per effective period and overlap is checked across intervals | 0 duplicate active keys; all active mappings approved | High | Reference Data Owner / Reference Steward | Reject reference release; rollback or repair mapping |
| DQ-008 v1 | `stream.transactions.event_id` | Uniqueness, timeliness | Count duplicate financial effects by stable event ID over a defined 24-hour idempotency horizon; calculate event-time-to-process-time lag over rolling 5-minute windows | Duplicate effects over each 24-hour idempotency horizon; lag percentile over each complete rolling 5-minute event window, with late-event policy stated | Illustrative acceptance: 0 duplicate financial effects; p99 lag ≤ 120 seconds in each complete 5-minute window. Set horizon/lag budget from consumer semantics before production | High | Payments Product Owner / Streaming Steward | Deduplicate by stable ID; alert on lag; replay only with idempotency |
| DQ-009 v1 | `ml.training.customer_label` / CDE-007 | Validity, accuracy, representativeness | Label domain check; reproducible stratified sample compared with adjudicated outcomes; coverage by approved cohort | All labels in the versioned training snapshot for domain checks; stratified sample frame and sample size are specified before adjudication; coverage denominator is defined per approved cohort | Illustrative acceptance: 100% labels in the approved domain; at least 98% agreement in the adjudicated sample; and a maximum-minus-minimum coverage-rate gap ≤ 5 percentage points across the approved cohorts, with cohort definitions and denominators specified in the test plan. Model owner must validate sample size and targets before use | High | Model Owner / ML Data Steward | Freeze dataset version; investigate label pipeline; re-evaluate training eligibility |
| DQ-010 v1 | `ai.knowledge_chunks` | Validity, timeliness, integrity | Required source ID, version, effective date, access policy; compare indexed version to approved source registry; review duplicate/contradiction candidates | All retrievable chunks in the index snapshot; denominator is retrievable chunks; compare source/version/ACL at publication and on each configured revalidation cycle | Illustrative acceptance: 100% of retrievable chunks have source ID/version and current ACL; source-class freshness target is explicitly registered (for example, policy content revalidated within 24 hours); expired/revoked restricted source not retrievable | High | Knowledge Product Owner / Content Steward | Unpublish or quarantine affected chunks; rebuild index and verify ACL propagation |

**Review notes:** DQ-001 needs a domain-specific tolerance and matching keys; it cannot be implemented responsibly from this table alone. DQ-006 uses an illustrative threshold and applies only to a clearly defined eligible population. DQ-008 requires an event-time policy, idempotency key, and horizon. DQ-009 requires a sampling design and label adjudication procedure. DQ-010 illustrates that AI knowledge quality includes provenance, permission, freshness, and semantic review, not just text non-null checks.

### 4.5 Threshold design

Thresholds may be:

- **Absolute:** exactly zero orphan keys; at least a defined completeness rate.
- **Business-logic based:** no negative amount except for approved reversal types.
- **Relative:** no worse than an approved baseline by more than a defined tolerance.
- **Statistical:** outside control limits triggers investigation.
- **Time-window based:** event lag p95/p99 within an agreed budget.
- **Hard gate plus rate:** a percentage threshold with a hard override for critical defect classes.

Use the least ambiguous threshold that protects the use. The rule owner should document why it is acceptable, which consumers rely on it, and how the target was chosen. Do not call a proposed target an industry standard without evidence.

---

## 5. Profiling, measuring, and interpreting quality

### 5.1 What profiling does

Profiling describes observed data before and during rule design. It helps answer “what is present?” but not by itself “is it correct?”

Useful profiling statistics include:
- row count and distinct key count;
- null, blank, sentinel, and whitespace-only counts;
- minimum, maximum, quantiles, mean, standard deviation, and value frequencies;
- format and domain distributions;
- duplicate groups and repeated event IDs;
- referential-integrity failures;
- timestamp lag and late-arrival rate;
- schema changes and missing/extra columns;
- distribution changes by source, cohort, time, or product;
- reconciliation counts and sums across systems.

Profiling must use the intended population and grain. For a current-state customer table, count one row per customer. For a customer history table, multiple rows per customer may be expected. Always document snapshot ID, filters, timezone, effective-date policy, and extraction completeness.

### 5.2 Nulls, blanks, and sentinel values

These states are not automatically equivalent:

- SQL `NULL`: unknown, unavailable, or absent according to the source contract;
- empty string `''`: a present string of zero length;
- whitespace-only string: technically non-empty but often unusable;
- sentinel such as `'UNKNOWN'`, `'N/A'`, or `0`: a value that may represent missingness or a real category;
- not applicable: the business condition means the field is legitimately not required;
- not yet arrived: data may be delayed rather than permanently missing.

Define the null policy per rule. For example, a null `contact_email` may be acceptable for a customer who is not eligible for email contact; it may be a defect for an eligible active customer. A blanket `COUNT(email)` denominator can accidentally exclude nulls because SQL `COUNT(column)` counts non-null values only.

### 5.3 Denominators and population definition

A rate is only interpretable when its denominator is explicit.

Common measures:

\[
\text{Completeness rate} =
\frac{\text{eligible rows with usable value}}{\text{eligible rows}}
\times 100\%
\]

\[
\text{Validity rate} =
\frac{\text{eligible non-missing values that pass validity}}{\text{eligible non-missing values}}
\times 100\%
\]

\[
\text{Row pass rate} =
\frac{\text{eligible rows passing every specified row rule}}{\text{eligible rows}}
\times 100\%
\]

These denominators answer different questions. Validity among non-missing values tells you how well present values conform; it does not penalise missing values. A separate completeness metric is needed. If there are zero eligible values, validity is **undefined / not applicable**, not 100%. Report numerator and denominator alongside the percentage.

### 5.4 Worked calculation: completeness and validity

Suppose a synthetic snapshot has 1,000,000 eligible customer rows.

- 40,000 rows have a missing email.
- 960,000 rows have a non-missing email.
- Of the non-missing emails, 8,000 fail the agreed syntax rule.

Completeness:

\[
(1{,}000{,}000 - 40{,}000) / 1{,}000{,}000 = 0.96 = 96.0\%
\]

Validity among present values:

\[
(960{,}000 - 8{,}000) / 960{,}000
= 952{,}000 / 960{,}000
\approx 99.17\%
\]

Valid non-missing email count is 952,000. The proportion of all eligible rows with a present and syntax-valid email is:

\[
952{,}000 / 1{,}000{,}000 = 95.2\%
\]

The third figure combines presence and validity; do not label it simply “validity” without explaining the definition. Also, email syntax does not prove ownership or deliverability. Those require a different evidence source and should not be inferred from a regular expression.

### 5.5 Worked calculation: uniqueness

Assume a current-state table has 1,000 rows, 10 null IDs, and 985 distinct non-null `customer_id` values.

- **Total rows:** 1,000.
- **Null ID rows:** 10.
- **Rows with non-null IDs:** 1,000 − 10 = 990.
- **Distinct non-null IDs:** 985.
- **Duplicate excess rows:** 990 − 985 = 5.

These counts reconcile. The number of **duplicate groups** is a separate measure and cannot be calculated from these totals alone. Rows **in duplicate groups** can exceed duplicate excess rows: a key appearing three times contributes 3 rows in a duplicate group but only 2 excess rows beyond the first occurrence. Report the metric name and denominator explicitly.

For current-state uniqueness, a common defect rate is:

\[
\text{Duplicate excess-row rate} =
\frac{\text{non-null rows} - \text{distinct non-null keys}}{\text{non-null rows}}
\times 100\%
\]

If null IDs are also defects, report their rate separately or include them in a row-level rule pass rate. For history tables, use a grain-appropriate key such as `(customer_id, valid_from)` or a surrogate record ID; do not incorrectly demand one row per customer across all history.

### 5.6 Sampling and accuracy

Accuracy is difficult because there may be no independent truth source. Possible approaches:

1. **Authoritative reconciliation:** compare to a governed system of record with aligned scope and cut-off.
2. **Independent reference:** compare address, code, or identity against a reliable source where permitted.
3. **Sampled manual verification:** draw a reproducible sample, verify against evidence, and record adjudication.
4. **Cross-source consistency proxy:** compare systems, but state that agreement is not proof if both systems share the same upstream error.
5. **Invariant checks:** verify accounting totals, conservation laws, or domain-specific equations; useful but not a complete substitute for truth.

Sampling needs a defined frame, selection method, sample size rationale, confidence interval or uncertainty statement where appropriate, reviewer guidance, and treatment of non-response. A convenience sample of easy records may not represent the population. Oversample high-risk cohorts if needed, but report weighted or stratified results correctly.

### 5.7 Distribution anomalies

A profile can identify sudden changes in category mix, null rate, numeric range, volume, or quantiles. A shift is a **signal to investigate**, not automatic proof of poor quality. It may reflect a genuine business event, seasonal pattern, new product, source migration, or changed capture behaviour.

Use:
- a comparable baseline window;
- stable filters and grain;
- cohort-aware comparisons;
- approved control limits or drift thresholds;
- alert suppression/aggregation for known events;
- a runbook that distinguishes expected change from data defects.

### 5.8 Quality scores and why one number is not enough

Per-rule pass rate, per-dimension rate, CDE-level status, and overall summaries can be useful, but only when the aggregation logic is visible.

**Do not assume** a weighted average can compensate for a critical failure. Example: if four rules score 100%, 100%, 100%, and 0%, an unweighted average is 75%. That number hides the fact that the currency rule failed completely. If the failed rule controls a critical report field, the output may be unusable even when the overall score looks acceptable.

Recommended report views:

- raw numerator/denominator and rate per rule;
- CDE × dimension status;
- critical-failure override status;
- data volume and freshness alongside quality;
- trend and comparison window;
- exception count, age, and expiry;
- lineage coverage and known blind spots;
- confidence/limitations of the measurement;
- consumer-specific acceptance status.

If an aggregate score is required for prioritisation, document weights and rationale, show the underlying rule results, and apply hard gates to critical failures. An aggregate score is a summary, not proof that the data are fit for every consumer.

---

## 6. Practical implementation examples

All examples use synthetic data. Code is illustrative and should be adapted to the target engine, SQL dialect, data contract, and operational requirements. Example thresholds are not universal standards.

### 6.1 SQL environment and input schema

**Environment:** SQLite 3 or a compatible SQL engine with minor dialect adjustments.  
**Dependencies:** SQLite only for the SQL example; no external packages.  
**Input schema:** synthetic `customer` and `exposure` tables.

```sql
CREATE TABLE customer (
    customer_id   INTEGER,
    status        TEXT NOT NULL,
    email         TEXT,
    birth_date    TEXT,
    updated_at    TEXT
);

CREATE TABLE exposure (
    exposure_id   INTEGER PRIMARY KEY,
    customer_id   INTEGER,
    amount        REAL,
    currency_code TEXT,
    as_of_date    TEXT
);

CREATE TABLE valid_currency (
    currency_code TEXT PRIMARY KEY,
    effective_from TEXT NOT NULL,
    effective_to   TEXT
);
```

Assumptions:
- `customer` is a current-state table; one non-null `customer_id` is expected per customer.
- `email` is required only for active customers eligible for email contact; this simple example uses `status = 'ACTIVE'` as the eligible population for demonstration. A production rule must include consent/eligibility and contact-policy logic if relevant.
- Dates are stored in ISO `YYYY-MM-DD` form. Production systems should use typed date/time columns and explicit timezone/cut-off rules where supported.
- `valid_currency` contains approved codes with effective dates. The demo query below uses a simple current code list; production must check effective-date overlap and reporting-date validity.
- `amount` can be negative only if the business definition explicitly permits reversals; this example does not enforce a universal non-negative rule.

### 6.2 SQL: profile nulls, blanks, and duplicates

```sql
SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_id_rows,
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) AS null_email_rows,
    SUM(CASE WHEN email IS NOT NULL AND TRIM(email) = '' THEN 1 ELSE 0 END)
        AS blank_email_rows,
    COUNT(DISTINCT customer_id) AS distinct_non_null_customer_ids
FROM customer;
```

**Business purpose:** distinguish missing identifiers from distinct keys and identify both SQL nulls and blank email strings.

**Expected output for the synthetic profile:** if 100 rows contain 3 null IDs, 12 null emails, 4 blank emails, and 95 distinct non-null IDs, the output should show `total_rows=100`, `null_id_rows=3`, `null_email_rows=12`, `blank_email_rows=4`, and `distinct_non_null_customer_ids=95`. This is an illustrative expected result, not an executed query result.

**Edge cases:**
- `COUNT(DISTINCT customer_id)` excludes nulls in SQLite and many SQL engines; always report nulls separately.
- If the table is empty, `COUNT(*)` returns 0 and the sums may be `NULL` depending on the engine/query. Use `COALESCE(SUM(...), 0)` if the report contract requires zero counts.
- If `email` contains tabs or unusual whitespace, `TRIM` behaviour may vary by engine; normalise whitespace explicitly if the source contract requires it.
- This profile does not prove an email is valid, deliverable, or permitted for a given use.

### 6.3 SQL: find duplicate identifiers

```sql
SELECT
    customer_id,
    COUNT(*) AS rows_per_id
FROM customer
WHERE customer_id IS NOT NULL
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY rows_per_id DESC, customer_id;
```

**Business purpose:** locate keys that occur more than once in a current-state table.

**Expected output:** only duplicated non-null IDs appear. For example, if ID `17` occurs three times, it appears once with `rows_per_id=3`.

**Interpretation:** the number of duplicate groups is not the same as the number of duplicate excess rows. Calculate both when the distinction matters. Null IDs are omitted from this query and must be checked by a separate rule.

**Production caution:** do not automatically delete duplicates. Determine whether the table is current state or history, define the grain, use source identifiers and survivorship rules, preserve evidence, and make remediation idempotent.

### 6.4 SQL: validate a code domain and referential integrity

```sql
-- Invalid or missing currency codes against a simple approved code list.
SELECT e.exposure_id, e.currency_code
FROM exposure AS e
LEFT JOIN valid_currency AS v
  ON e.currency_code = v.currency_code
WHERE e.currency_code IS NULL
   OR v.currency_code IS NULL;

-- Orphan exposure customer references.
SELECT e.exposure_id, e.customer_id
FROM exposure AS e
LEFT JOIN customer AS c
  ON e.customer_id = c.customer_id
WHERE e.customer_id IS NOT NULL
  AND c.customer_id IS NULL;
```

**Business purpose:** prevent unknown currency interpretation and identify exposure rows whose customer reference cannot be resolved.

**Expected output:** the first query returns rows with null or unapproved currency codes. The second returns non-null customer IDs absent from the customer table.

**Important assumptions and edge cases:**
- The simple currency join ignores effective dates. In production, use the reference record effective on the row’s `as_of_date` and ensure effective intervals do not overlap.
- A null `customer_id` is not counted as an orphan in the second query; it belongs to a separate completeness rule.
- A missing customer record may be caused by a late-arriving customer batch, deletion policy, bad key mapping, or a real source defect. Do not automatically classify every orphan as invalid without a lateness policy.
- `LEFT JOIN` may produce multiple matches if the reference table contains duplicate keys. Govern and validate reference uniqueness first.

### 6.5 SQL: completeness rate with explicit denominator and empty-data handling

```sql
WITH eligible AS (
    SELECT customer_id, email
    FROM customer
    WHERE status = 'ACTIVE'
),
counts AS (
    SELECT
        COUNT(*) AS eligible_rows,
        SUM(CASE
            WHEN email IS NOT NULL AND TRIM(email) <> '' THEN 1
            ELSE 0
        END) AS usable_email_rows
    FROM eligible
)
SELECT
    eligible_rows,
    COALESCE(usable_email_rows, 0) AS usable_email_rows,
    CASE
        WHEN eligible_rows = 0 THEN NULL
        ELSE 1.0 * COALESCE(usable_email_rows, 0) / eligible_rows
    END AS completeness_rate
FROM counts;
```

**Business purpose:** calculate the proportion of active customers with a non-null, non-blank email.

**Expected output:** for 80 eligible rows with 76 usable email values, `eligible_rows=80`, `usable_email_rows=76`, and `completeness_rate=0.95`. If no rows are eligible, the rate is `NULL` (undefined) rather than 100%.

**Interpretation:** the example uses `status='ACTIVE'` as a stand-in for eligibility. A production rule must define eligibility precisely, include allowed exceptions, and report numerator and denominator. SQL `TRIM` may need adaptation for tabs, non-breaking spaces, or Unicode whitespace.

### 6.6 SQL: measure dataset reconciliation

```sql
-- Illustrative counts by reporting cut-off.
SELECT as_of_date, COUNT(*) AS row_count, SUM(amount) AS total_amount
FROM exposure
GROUP BY as_of_date
ORDER BY as_of_date;
```

This query produces a profile by date, not a full reconciliation. To reconcile two systems, align:
- reporting cut-off and timezone;
- scope and exclusions;
- grain and keys;
- currency and unit;
- late-arrival policy;
- rounding and precision;
- duplicate handling.

Only then compare row counts, sums, and key-level differences. A matching total can conceal offsetting errors, so material CDEs may require key-level comparison as well as aggregate reconciliation.

### 6.7 Python: profile a synthetic dataset and compute metrics

**Environment:** Python 3.10+  
**Dependencies:** Python standard library only (`collections` and `datetime`). No pandas or third-party package is required.  
**Input schema:** list of dictionaries with `customer_id`, `status`, `email`, `birth_date`, `updated_at`.  
**Execution status:** the code below is a self-contained example. Its logic and expected results are checked as part of document validation; this statement does not imply it was executed in your production environment.

```python
from collections import Counter
from datetime import date
customers = [
    {"customer_id": 1, "status": "ACTIVE", "email": "a@example.test",
     "birth_date": "1988-03-10", "updated_at": "2026-10-20T05:00:00Z"},
    {"customer_id": 2, "status": "ACTIVE", "email": None,
     "birth_date": "2099-01-01", "updated_at": "2026-10-20T05:02:00Z"},
    {"customer_id": 2, "status": "ACTIVE", "email": "  ",
     "birth_date": "not-a-date", "updated_at": "2026-10-20T05:04:00Z"},
    {"customer_id": 3, "status": "INACTIVE", "email": "c@example.test",
     "birth_date": None, "updated_at": None},
]

def is_usable(value):
    return isinstance(value, str) and value.strip() != ""

def parse_iso_date(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None

total_rows = len(customers)
non_null_ids = [r["customer_id"] for r in customers
                if r.get("customer_id") is not None]
id_counts = Counter(non_null_ids)
duplicate_keys = {key: count for key, count in id_counts.items()
                  if count > 1}

eligible = [r for r in customers if r.get("status") == "ACTIVE"]
usable_emails = sum(is_usable(r.get("email")) for r in eligible)
completeness = (usable_emails / len(eligible)) if eligible else None

birth_dates = [r.get("birth_date") for r in customers]
missing_birth_dates = sum(v is None or v == "" for v in birth_dates)
invalid_birth_dates = sum(
    v is not None and v != "" and parse_iso_date(v) is None
    for v in birth_dates
)
future_birth_dates = sum(
    parse_iso_date(v) is not None and parse_iso_date(v) > date(2026, 10, 21)
    for v in birth_dates
)

print({
    "total_rows": total_rows,
    "duplicate_keys": duplicate_keys,
    "active_rows": len(eligible),
    "usable_active_emails": usable_emails,
    "active_email_completeness": completeness,
    "missing_birth_dates": missing_birth_dates,
    "invalid_birth_dates": invalid_birth_dates,
    "future_birth_dates": future_birth_dates,
})
```

**Expected output for the embedded synthetic rows:**

```text
{
  'total_rows': 4,
  'duplicate_keys': {2: 2},
  'active_rows': 3,
  'usable_active_emails': 1,
  'active_email_completeness': 0.3333333333333333,
  'missing_birth_dates': 1,
  'invalid_birth_dates': 1,
  'future_birth_dates': 1
}
```

**Interpretation:**
- Four records are present.
- `customer_id=2` appears twice; this is a duplicate in the assumed current-state grain.
- Three records are active; one has a usable email, so completeness is 1/3 or 33.3%.
- One birth date is missing, one is unparsable, and one parses but is in the future relative to the stated illustrative evaluation date.

**Edge cases and limits:**
- An empty `customers` list produces `total_rows=0`, no duplicates, `active_rows=0`, and `completeness=None`. This is intentional: a rate with a zero denominator is undefined.
- This parser checks ISO calendar validity, not whether a birth date is plausible for a customer or accurate against evidence.
- The example uses a fixed date for reproducibility. A production rule should pass a controlled evaluation date/time, use the correct business timezone, and record it in the result.
- Python’s `date.fromisoformat` accepts supported ISO date forms; strict canonical-format checks should compare the original string to the required representation if the exact wire format matters.
- `isfinite` is imported for use in numeric extensions but is not needed by this particular example; remove it if adapting the script.
- The example holds the whole dataset in memory. For large datasets, profile in the query engine or stream records in bounded batches.
- This is a profiling example, not a production remediation engine: it does not write issue records, mask sensitive values, track rule versions, or apply an approved survivorship policy.

### 6.8 Python: safe percentage helper

```python
def rate(numerator, denominator):
    if denominator < 0 or numerator < 0 or numerator > denominator:
        raise ValueError("Require 0 <= numerator <= denominator")
    if denominator == 0:
        return None
    return numerator / denominator

assert rate(76, 80) == 0.95
assert rate(0, 0) is None
assert rate(10, 20) == 0.5
```

This helper prevents common denominator errors. A production metric should also record numerator, denominator, filters, snapshot, rule version, and timestamp. Do not silently coerce a missing denominator to zero or a zero denominator to 100%.

### 6.9 Executable rule-testing strategy

For each rule, test at least:
- a known-good row;
- a known-bad row;
- null, blank, and sentinel cases;
- boundary values;
- empty population;
- duplicate/replay behaviour;
- late-arriving data;
- schema or reference-version changes;
- mixed valid and invalid batches;
- a case that should be an approved exception;
- a case where two systems agree but are both wrong (to challenge accuracy assumptions).

Seed defects in a controlled synthetic fixture. A rule that never fires may be correct, but it may also be untested or wired to the wrong population. Record the rule version and test fixture version.

---

## 7. Advanced rule architecture and governance

### 7.1 Where to place checks

| Layer | Primary purpose | Advantages | Risks / trade-offs |
|---|---|---|---|
| Source capture | Prevent invalid data close to entry | Prevents recurrence; feedback is timely | May not control external sources; can disrupt operational entry |
| Ingestion / contract boundary | Validate schema, required fields, domains, and batch integrity | Stops unexpected inputs before propagation | Strict rejection can delay downstream consumers |
| Curated transformation | Enforce business semantics, joins, mappings, and derivations | Has broader context than source | Defects may already have spread; transformation can hide raw evidence |
| Consumption / report | Verify fitness for a particular decision and cut-off | Consumer-specific acceptance | Late detection; repeated checks if upstream controls are weak |
| Continuous observation | Detect changes in freshness, volume, distribution, and rule results | Reveals drift between releases | Signals need triage; alert fatigue if thresholds are poor |

A critical use often needs layered defence: preventive validation at the boundary, transformation-level assertions, and a final publication gate. Do not assume that a rule at the final report compensates for missing upstream controls.

### 7.2 Batch, incremental, and streaming rules

**Batch**
- Run rules against an immutable batch or table snapshot.
- Validate expected delivery, row counts, schema, keys, and control totals.
- Separate “batch is empty” from “batch is complete but has zero eligible records.”
- Record input file IDs, partition/date, source watermark, rule version, and output decision.

**Incremental / CDC**
- Validate changed rows and also detect cross-row consequences: key collisions, deletions, referential integrity, and aggregate reconciliation.
- Make remediation idempotent; reprocessing the same change should not create duplicate effects.
- Account for late-arriving dimensions, deletes/tombstones, out-of-order updates, and schema evolution.
- Periodically run wider reconciliation because local checks can miss drift introduced by lost changes.

**Streaming**
- Define event-time vs processing-time and allowed lateness.
- Use stable event IDs and idempotent processing for duplicate delivery/replay.
- Evaluate freshness and lag over a specified window (for example p95/p99 lag over five-minute windows, if that matches the consumer).
- Quarantine or route invalid events to a dead-letter path with controlled access and replay policy.
- Do not use a simplistic “no duplicate ever” rule without defining the idempotency horizon and whether the producer can legitimately emit revisions.
- Monitor state-store expiry and replay effects; a replayed event must not silently double-count a financial measure.

A stream may temporarily contain late data that later arrive. The policy should state whether consumers receive provisional data, whether a window is reopened, and when a result is final.

### 7.3 Quality for analytics, reports, ML, and AI

| Use | Quality concerns beyond basic schema checks | Example acceptance design |
|---|---|---|
| Exploratory analytics | Missingness, outliers, cohort bias, documented limitations | Publish profile and caveats; block only defects that make analysis misleading |
| Regulatory / financial reporting | Completeness, accuracy, reconciliation, lineage, cut-off, reproducibility | Hard gate for material unresolved CDE defects; preserve signed evidence |
| ML training data | Label correctness, leakage, time alignment, representativeness, duplicate entities, feature/label consistency | Freeze versioned dataset; validate label quality and cohort coverage before training |
| ML feature data | Freshness, consistency between offline/online representations, missingness, drift | Feature-specific target and online/offline parity check |
| AI knowledge sources / retrieval | Source authority, freshness, provenance, permission/ACL propagation, contradictory versions, chunk integrity | Only approved source versions; recheck access after index build; remove expired/revoked content |
| Customer operations | Eligibility, consent/purpose, deliverability where relevant, current status | Route to human review; do not fabricate missing contact details |

Quality is not solely about whether values look plausible. A technically correct dataset can be unsuitable if it contains data not permitted for the intended use, uses stale definitions, or has lost provenance.

### 7.4 Quality metadata and lineage integration

Attach results to stable asset and rule identifiers, not just names. A quality result should include:

- asset ID and version/snapshot;
- field or relationship IDs;
- CDE ID and business use;
- rule ID/version and dimension;
- execution time, input time range, and run ID;
- numerator, denominator, metric, threshold, and pass/fail/unknown status;
- failed record identifiers or secure issue reference (avoid copying sensitive raw values into broad logs);
- owner, severity, action taken, exception ID/expiry;
- source/lineage references and confidence/coverage limitations.

Use lineage to answer:
- Which upstream field or transformation produced the failing CDE?
- Which reports, models, and consumers may be affected?
- Did the rule run before or after a transformation that could introduce the defect?
- Is the apparent root cause a source defect, mapping issue, stale reference set, late data, or bad join?
- Does a source fix require backfill or replay?

Lineage graphs can be incomplete or stale. Pair graph traversal with run-level evidence and disclose unknown segments, especially for CDEs.

### 7.5 Rule lifecycle

A governed rule moves through:
1. **Proposed:** requirement, use, CDE, owner, and risk recorded.
2. **Specified:** predicate, population, denominator, threshold, severity, and action agreed.
3. **Tested:** known-good/bad cases, edge cases, false-positive and false-negative checks.
4. **Approved:** business owner approves acceptance semantics; technical owner approves implementation.
5. **Deployed:** versioned code/config, runbook, alert routing, and evidence retention enabled.
6. **Observed:** execution success, runtime, failure rate, and issue outcomes tracked.
7. **Reviewed:** threshold and population reassessed after business/source changes.
8. **Retired:** no longer needed; deprecation reason and consumers recorded.

Rule coverage should be measured by **relevant CDE × dimension/use**, not simply the number of rules. Ten redundant rules on one field do not prove that all critical risks are covered.

### 7.6 False positives, false negatives, and control confidence

- **False positive:** the rule flags acceptable data, often because the population, reference, or business context is wrong.
- **False negative:** the rule passes a defect, often because the assertion is too weak, the source of truth is wrong, or the rule is not exercised.
- **Untested rule:** no evidence that it detects seeded defects.
- **Inconclusive measurement:** the check did not run, the source was unavailable, or the denominator was undefined. Do not record this as a pass.

Track the rate of actionable alerts, repeat incidents, rule test coverage, suppressed alerts, and control execution failures. A green dashboard is not meaningful if the check did not run or silently scanned only part of the data.

### 7.7 Cost, scale, and execution strategy

Full scans provide broad coverage but can be expensive on large tables. Alternatives include:
- incremental checks over changed partitions;
- partition-level checks plus periodic full reconciliation;
- approximate profiling for discovery, followed by exact checks for CDEs;
- stratified samples for manual accuracy review;
- pushed-down SQL predicates rather than exporting data;
- event-driven validation at ingestion.

Sampling is not a substitute for exact controls where the requirement is “zero critical invalid values.” It may be appropriate for accuracy verification or exploratory profiling if uncertainty is stated. Record which controls are exact, approximate, or sampled.

### 7.8 ADR: CDE selection and threshold policy

**Decision:** prioritise controls by intended use and business impact; use hard gates for explicitly critical failure classes and rate-based thresholds for appropriate lower-risk populations.

- **Context:** the platform has many assets and limited stewardship capacity; equal control depth creates cost and alert noise.
- **Options:** identical controls everywhere; only manual review; tiered automated rules with targeted manual verification.
- **Chosen approach:** tiered rules, automated repeatable checks, explicit accuracy evidence, field-level lineage for CDEs, and human approval for material exceptions.
- **Benefits:** directs effort to consequential defects, makes acceptance reproducible, and links failures to remediation.
- **Costs/risks:** CDE classification requires governance; automated checks can be wrong; strict gates can delay data; accuracy evidence may be expensive.
- **Guardrails:** each rule has an owner and action; aggregate scores never override critical failure; exceptions expire; sampling uncertainty is recorded; blind spots are explicit.
- **Revisit when:** business use, materiality, regulation, lineage, source systems, consumer count, or measured false-positive rates change.

---

## 8. Remediation, exceptions, and failure handling

### 8.1 A practical triage workflow

1. **Detect:** run a versioned rule against a known input snapshot.
2. **Confirm:** verify the rule ran successfully, the population is correct, and the failure is not caused by an empty/partial input or reference-data issue.
3. **Classify:** map the defect to dimension, CDE, severity, business use, and potential downstream impact.
4. **Contain:** block publication, quarantine affected rows, restrict retrieval, or label output provisional according to policy.
5. **Diagnose:** use lineage, run metadata, failed keys, source logs, and reference versions to locate the origin.
6. **Remediate:** correct at the source where possible; repair downstream data only under a controlled and traceable process.
7. **Recover:** replay/backfill affected partitions idempotently and re-run all dependent rules.
8. **Verify:** compare before/after metrics and prove the defect is resolved.
9. **Prevent:** add capture validation, contract tests, mapping tests, monitoring, or training as appropriate.
10. **Close:** record root cause, impact, owner, corrective action, residual risk, evidence, and approval.

### 8.2 Severity and action design

| Severity | Typical condition | Immediate response | Approval / closure |
|---|---|---|---|
| Critical | Could materially misstate a regulated/financial decision, violate a hard control, expose restricted content, or corrupt a high-impact model input | Block affected publication or access; page accountable owner; preserve evidence | Named business/control authority approves recovery or explicitly authorised exception |
| High | Material operational/customer impact or broad downstream propagation | Quarantine affected subset or hold dependent product; alert owner | Owner documents fix and validates downstream impact |
| Medium | Limited impact with a viable workaround | Create steward issue; flag affected records or product limitation | Owner agrees target date and verifies correction |
| Low | Cosmetic or low-impact defect not affecting current use | Record trend/backlog; fix by agreed priority | Steward confirms closure or accepted residual risk |

Severity is a consequence classification, not just the percentage of failed rows. A single wrong currency code can be critical even when 99.999% of records pass.

### 8.3 Choose a failure response deliberately

| Strategy | Use when | Benefits | Risks / safeguards |
|---|---|---|---|
| Reject entire batch | Input contract or batch integrity failure makes the whole load unsafe | Simple, clear boundary | Can delay all consumers; ensure retry and dead-letter evidence |
| Quarantine failed rows | Defects are isolatable and valid rows can be used safely | Limits blast radius | Can distort totals or joins; publish quarantined counts and ensure consumer contract permits partial data |
| Correct automatically | Transformation is deterministic, approved, reversible, and auditable | Fast recovery | Silent corruption if heuristic is wrong; record original value, rule/version, and correction reason |
| Route for stewardship | Requires business judgement, matching, or external evidence | Human review for ambiguous cases | Queue ageing and inconsistent decisions; use playbooks and SLAs |
| Accept with exception | Residual risk is understood, use is explicitly allowed, and authority approves | Preserves continuity | Normalises defects if exceptions never expire; scope, approver, expiry, compensating control, and consumer notice required |
| Block publication/access | Critical defect affects decision or policy boundary | Protects downstream decisions | Requires fallback and communication plan; do not bypass silently |

A quality score must not automatically choose the response. The acceptance policy should define hard failure classes and the authorised decision-maker.

### 8.4 Exception register

Every exception should include:
- exception ID and related rule/CDE;
- affected asset, snapshot, rows/partitions, and consumer/use;
- defect description and impact assessment;
- reason for temporary acceptance;
- compensating controls and scope restrictions;
- business/control approver;
- created time, expiry time, review date, and owner;
- remediation plan and ticket;
- evidence of consumer notification;
- closure evidence or renewed approval.

Exceptions should be bounded and visible. A permanent undocumented bypass is a control failure.

### 8.5 Common failure scenarios

| Failure scenario | Why a naive check misses it | Better response |
|---|---|---|
| `email` is non-null but equals `UNKNOWN` | Null-only completeness check passes | Define usable-value policy and sentinel list; report null and sentinel rates separately |
| Amount is valid numeric but wrong by a factor of 100 | Type/range validation passes | Reconcile units, currency, source and transformation; test conversion factors |
| All rows agree across two systems, but both inherited the same bad source | Cross-system consistency is mistaken for accuracy | Compare with an independent authoritative source or sampled evidence |
| Report score is 99.99%, but one critical currency is invalid | Aggregate hides severity | Apply critical-failure override and report CDE-level status |
| Duplicate keys appear after replay | Rule ignores idempotency and event IDs | Deduplicate by stable key; test replay and exactly-once effects, not just transport claims |
| Orphans appear because dimension arrives late | Referential rule has no lateness policy | Define allowed lateness and provisional state; recheck after the window |
| Quality rule is green because input was empty | Zero denominator is treated as success | Distinguish empty, missing, partial, and legitimately zero-eligible inputs |
| SQL `COUNT(column)` excludes nulls | Denominator silently excludes missing values | Use explicit `COUNT(*)` population and `CASE` expressions |
| Reference set contains overlapping effective dates | Simple membership test passes multiple matches | Validate effective-date intervals and enforce uniqueness per key/date |
| AI index retains a revoked source | Content quality ignores access and deletion propagation | Track source/version lineage; remove or block retrieval and verify ACLs after reindex |
| Downstream cleansing repeats every day | Root cause remains upstream | Correct source capture or mapping; measure recurrence |
| Rule fires continuously after a legitimate product launch | Static threshold ignores expected business changes | Review baseline, stratify by cohort, approve threshold changes with evidence |

---

## 9. Quality report — synthetic worked example

### 9.1 Dataset and run context

All values in this section are illustrative.

- **Asset:** `silver.customer`
- **Snapshot:** `customer_2026-10-20T05:00Z`
- **Grain:** current-state row per customer
- **Eligible population:** 1,000 active customers for email completeness; all 1,200 rows for identifier and birth-date checks
- **Rule version:** DQ demo v1
- **Owner:** Customer Domain Owner; execution operated by Data Platform
- **Limitations:** synthetic snapshot; no independent authoritative verification of identity or birth-date accuracy; no external email delivery check

### 9.2 Rule results

| Rule ID | Dimension | Population / denominator | Numerator or observed count | Metric | Illustrative target | Status | Action |
|---|---|---:|---:|---:|---|---|---|
| DQ-101 | Completeness: customer ID | 1,200 rows | 1,198 non-null IDs | 1,198 / 1,200 = 99.83% | 100% for current-state rows | Fail | Quarantine 2 missing-key rows; investigate source capture |
| DQ-102 | Uniqueness: customer ID | 1,198 non-null ID rows | 1,190 distinct non-null IDs | 8 duplicate excess rows (8 / 1,198 = 0.67%) | 0 duplicate excess rows | Fail | Identify duplicate groups; apply approved survivorship, no blind delete |
| DQ-103 | Completeness: usable email for eligible active customers | 1,000 eligible rows | 970 usable values | 970 / 1,000 = 97.0% | ≥ 98% proposed | Fail | Route eligible missing, blank, or sentinel values to steward; do not fabricate values |
| DQ-104 | Validity: email syntax among nonblank values | 980 nonblank values | 972 syntax passes | 972 / 980 = 99.18% | ≥ 99.5% proposed | Fail | Review eight syntax failures; syntax does not prove deliverability |
| DQ-105 | Validity: birth-date format | 1,190 non-null date values | 1,185 parseable valid dates | 1,185 / 1,190 = 99.58% | ≥ 99.5% proposed | Pass | Continue separate plausibility/accuracy checks |
| DQ-106 | Plausibility: birth date not after evaluation date | 1,185 parseable dates | 1,182 dates not in the future | 1,182 / 1,185 = 99.75% | 100% in this example | Fail | Review three future dates; do not auto-correct without evidence |
| DQ-107 | Referential integrity: exposure → customer | 5,000 non-null exposure customer references | 4,992 matched | 4,992 / 5,000 = 99.84% | 100% after agreed lateness window | Fail / pending | Distinguish late-arriving customer rows from invalid references |
| DQ-108 | Timeliness: snapshot publication | One scheduled run | Published 12 minutes after deadline | 12 minutes late | By 06:00 local deadline | Fail | Incident review; determine upstream cause and consumer impact |

For this illustrative snapshot, 1,200 customer rows contain 10 missing birth dates, 5 nonblank but unparsable dates, and 1,185 parseable dates. Thus 1,190 values are non-null and the format-validity denominator is 1,190. Of the 1,000 eligible active customers, 20 email values are missing or blank; 980 are nonblank, 972 pass syntax, and two of those syntax-passing values are known sentinel placeholders excluded from the 970 usable values. These figures reconcile the completeness and syntax metrics while keeping their meanings distinct. DQ-104 excludes missing/blank emails from the syntax denominator; DQ-103 captures their absence and sentinel placeholders in the usable-value metric. Do not combine the two without declaring a new combined metric.

### 9.3 Before/after remediation calculation

Suppose the customer ID rule initially sees 1,200 rows:
- 2 rows have null IDs;
- 8 duplicate excess rows exist among non-null IDs;
- after source correction, two missing IDs are resolved using authoritative evidence, and eight duplicate excess rows are merged/removed under an approved survivorship decision, a new validated snapshot has 1,192 rows, all IDs non-null and unique.

Before:
- completeness = (1,200 − 2) / 1,200 = 99.833...%;
- uniqueness on non-null rows = distinct non-null IDs / non-null rows = (1,198 − 8) / 1,198 = 1,190 / 1,198 ≈ 99.332%.

After:
- completeness = 1,192 / 1,192 = 100%;
- uniqueness = 1,192 / 1,192 = 100%.

The row count falls by eight because duplicate excess rows were resolved; the two null IDs were repaired rather than discarded. This is valid only if the source evidence supports the repairs and the grain is one row per customer. Reconcile the before/after count and record each merge/repair; otherwise a team could make metrics look better simply by dropping problematic records. Preserve source and target counts, duplicate group details, remediation decisions, and business sign-off.

### 9.4 How to read the report

- A `Pass` on DQ-105 does not mean birth dates are accurate; it only means they parse according to the rule.
- DQ-107 is not safely resolved until the allowed lateness window has elapsed and the references are rechecked.
- A report-level status should reflect hard gates: if a critical CDE fails, the report can be blocked even if most metrics pass.
- The report must state failed check execution separately from failed data. `NOT_RUN`, `INCONCLUSIVE`, `PASS`, `FAIL`, and `EXCEPTION_ACCEPTED` are not interchangeable.
- Store failed row identifiers in a restricted issue store and expose only aggregates to users who do not need record-level detail.

### 9.5 Suggested quality result schema

| Field | Meaning |
|---|---|
| `run_id` | Unique execution identifier |
| `asset_id`, `asset_version` | Stable asset identity and snapshot/version |
| `rule_id`, `rule_version` | Governed rule identity |
| `cde_id`, `dimension` | Criticality link and quality dimension |
| `population_definition` | Filters/grain and inclusion criteria |
| `numerator`, `denominator`, `metric_value` | Reproducible result |
| `threshold`, `status` | Decision boundary and outcome |
| `started_at`, `completed_at`, `input_watermark` | Execution and freshness evidence |
| `severity`, `owner_id`, `action_taken` | Accountability and response |
| `exception_id`, `expiry_at` | Authorised deviation if any |
| `lineage_ref`, `evidence_ref` | Upstream/downstream trace and evidence location |
| `limitations` | Sampling, coverage, known blind spots |

Do not store raw sensitive values in a widely visible quality result table. Keep detailed failed-row evidence in a controlled store and link to it through access-controlled references.

---

## 10. Hands-on exercises and expected deliverables

Use synthetic data only. The numbers below are teaching fixtures.

### Exercise A — CDE register and rules for the exposure report

**Scenario:** Northbridge Bank’s synthetic regulatory exposure report is questioned. Its data comes from a core ledger, customer domain, and currency/rates reference. Lineage shows a transformation and one manual spreadsheet step.

**Tasks**
1. Identify the report’s key business decisions and consumers.
2. Trace amount, currency, customer identity, and as-of date upstream.
3. Create a CDE register with at least six candidates.
4. Assign impact rationale, owner, classification, lineage reference, and control tier.
5. Write at least eight atomic rules across completeness, validity, accuracy, uniqueness, consistency, timeliness, integrity, and conformity where relevant.
6. For each rule, state population, numerator/denominator, threshold, severity, owner, failure action, and evidence.
7. Identify at least three blind spots or uncertainties in lineage and quality evidence.
8. Define a report publication gate and exception process.

**Expected deliverables**
- CDE register;
- rule inventory;
- source-to-report lineage references;
- quality acceptance criteria;
- ADR explaining prioritisation and threshold policy.

**Validation**
- Every CDE traces to a specific decision/use.
- Every rule can be tested without guessing the population or null policy.
- Every critical rule has a named accountable role, severity, action, and evidence.
- Accuracy is not inferred from syntax or cross-system agreement alone.
- Manual/unknown lineage segments are disclosed.

### Exercise B — Profile, measure, and remediate customer defects

**Scenario:** a synthetic customer table of approximately 1,000 rows contains duplicates, null IDs, invalid dates, blanks, and sentinel values.

**Tasks**
1. Define table grain and eligible populations.
2. Profile nulls, blanks, sentinels, distinct keys, duplicate groups, date parse failures, future dates, and distribution anomalies.
3. Compute completeness, validity, uniqueness, and row pass rates with explicit denominators.
4. Classify each defect by dimension and identify overlapping dimensions where appropriate.
5. Find likely root causes; separate observed facts from hypotheses.
6. Propose source corrections, controlled deduplication, and preventive controls.
7. Re-run the same rules on a new synthetic snapshot and calculate before/after changes.
8. Explain why a better percentage is not sufficient unless row counts and excluded records reconcile.

**Expected deliverables**
- profile summary;
- quality report with counts and rates;
- defect classification and root-cause note;
- remediation plan with owners and due dates;
- before/after evidence.

**Validation**
- Scores can be reproduced from counts.
- Empty datasets and zero denominators are handled explicitly.
- Duplicate groups are not confused with duplicate excess rows.
- Corrected data are not silently fabricated or dropped.
- Root-cause hypotheses are verified or clearly labelled as unconfirmed.

### Exercise C — Threshold and acceptance design

Design three consumer-specific acceptance policies for the same synthetic customer dataset:
1. exploratory analytics;
2. customer communication;
3. regulatory exposure reporting.

For each, explain which rules are hard gates, which use rate thresholds, how exceptions work, and why the policy differs. No target should be presented as universal.

### Exercise D — Streaming and incremental quality

A synthetic event stream can replay events, deliver events late, and receive updates out of order.

Define:
- stable event identity and idempotency horizon;
- event-time and processing-time measurements;
- allowed lateness and finalisation policy;
- duplicate and reconciliation rules;
- quarantine/dead-letter handling;
- replay validation and downstream recovery evidence.

Deliver a failure-mode table and runbook outline. Explain how the design changes if a consumer requires immediate provisional output.

### Exercise E — ML dataset or AI knowledge source

Choose either a synthetic ML training dataset or an AI retrieval knowledge base.

For ML, define label validity/accuracy, leakage, time alignment, cohort coverage, duplicate entities, and versioned snapshot acceptance.

For AI knowledge, define source authority, freshness, provenance, access policy, effective version, duplicate/contradictory content, deletion propagation, and retrieval verification.

Deliver a rule inventory and a decision record. State what is measurable automatically and what requires sampling or human review.

### Required deliverable pack

| Deliverable | Minimum contents | Review question |
|---|---|---|
| Dimension and rule standard | Definitions, rule schema, measurement conventions, null/denominator policy | Can two teams implement the same rule consistently? |
| CDE register | Business use, impact, owner, lineage, classification, tier, review date | Does each CDE trace to a consequential decision? |
| Rule inventory | Asset/CDE, dimension, predicate, population, metric, threshold, severity, owner, action, evidence | Can every rule be tested and acted upon? |
| Quality report | Snapshot, counts, rates, thresholds, statuses, exceptions, freshness, limitations | Can a reviewer reproduce and interpret the result? |
| Remediation plan | Defect, root cause, source fix, downstream recovery, owner, due date, verification | Does it prevent recurrence rather than only clean downstream data? |
| ADR | CDE prioritisation, threshold rationale, hard gates, exception policy, trade-offs | Are the choices defensible and revisitable? |

---

## 11. Common mistakes and misconceptions

| Mistake | Why it fails | Better practice |
|---|---|---|
| Treating quality as a universal property | Fitness depends on use, population, and time | State consumer, purpose, grain, and acceptance criteria |
| Treating a dimension as a rule | “Completeness” is not executable | Write a precise predicate and measurement |
| Treating threshold as business acceptance | A percentage may hide a critical defect | Add hard gates, severity overrides, and approval rules |
| Null-only completeness | Blank/sentinel values can be unusable | Define usable value semantics and eligibility |
| Ignoring the denominator | Scores cannot be compared or reproduced | Store population definition, numerator, and denominator |
| Reporting 100% when denominator is zero | No observations do not prove success | Return `NOT_APPLICABLE` or `INCONCLUSIVE` |
| Confusing duplicate groups with duplicate excess rows | Counts describe different things | Name the metric and state grain/key policy |
| Calling format validity “accuracy” | A plausible value may be wrong | Use authoritative comparison, reconciliation, or sampled verification |
| Using cross-system consistency as proof of truth | Systems may share the same upstream defect | Seek independent evidence and state limitations |
| Using one overall score | Critical CDE failures can be hidden | Report per rule, dimension, CDE, and consumer |
| Arbitrary thresholds | Creates noise or unsafe acceptance | Justify targets by impact, baseline, contract, and risk |
| Same controls for every field | Wastes effort and still misses critical risk | Tier controls by use and impact |
| Auto-deleting duplicates | Can destroy history or valid multi-valued relationships | Establish grain, survivorship, and recovery policy |
| Cleaning only downstream | Defects recur at the source | Fix capture, mapping, contract, or process root cause |
| Failing open when a check does not run | “Not checked” becomes “passed” | Separate execution status from data status |
| Unbounded quarantine | Delayed rows become invisible and distort datasets | Track age, volume, owners, and release conditions |
| Permanent exceptions | Temporary risk becomes normal practice | Add expiry, approver, compensating control, and review |
| Treating distribution drift as proof of defects | Real business changes can alter distributions | Investigate cohorts and compare with approved context |
| Profiling full data but validating a different subset | Metrics do not reflect production use | Reuse versioned population logic and test scope |
| Ignoring classification in quality logs | Failed values may expose sensitive data | Minimise raw values; use restricted evidence references |
| Assuming a green dashboard means quality is good | Rules may be stale, partial, or not executed | Show execution health, coverage, freshness, and test evidence |

---

## 12. Mastery criteria and completion gate

### 12.1 Mastery criteria

You demonstrate mastery when you can:

- define the dimensions precisely and explain overlaps;
- compute metrics with the population, numerator, denominator, null policy, and measurement window stated;
- identify CDEs from business decisions, impact, exposure, lineage, and detectability;
- write atomic, versioned rules with asset/CDE, dimension, threshold, owner, severity, action, and evidence;
- distinguish accuracy evidence from format validation and cross-system consistency;
- explain why one aggregate score cannot certify fitness for all uses;
- design a defensible response strategy for batch, incremental, and streaming defects;
- demonstrate source-level remediation and verify before/after results;
- connect quality results to metadata, classification, lineage, and downstream consumers;
- describe the limits of sampling, profiling, automated checks, and unknown lineage; and
- defend threshold and CDE choices in an ADR without presenting illustrative targets as universal standards.

### 12.2 Completion gate checklist

Do not mark this topic complete until all items pass review.

- [ ] CDE register reviewed; every CDE links to a business use and accountable owner.
- [ ] Rule inventory reviewed; every rule has a stable ID/version, asset/CDE, dimension, predicate, population, denominator/null policy, threshold, severity, owner, failure action, and evidence.
- [ ] Quality report includes reproducible numerator/denominator counts, status, snapshot, time window, exceptions, and limitations.
- [ ] At least one completeness, validity, uniqueness, and referential-integrity calculation has been reproduced.
- [ ] Accuracy handling is explicit and uses appropriate independent evidence or clearly stated limitations.
- [ ] Empty datasets, nulls, blanks, sentinel values, duplicates, and sampling are handled intentionally.
- [ ] Rule test fixtures include known-good and known-bad cases and key edge cases.
- [ ] Before/after remediation results are reconciled to input/output counts; records are not silently discarded.
- [ ] Critical failure overrides and exception authority/expiry are documented.
- [ ] At least three lineage/quality blind spots and compensating controls are recorded.
- [ ] Control depth is tiered by intended use and business impact, not uniformly applied.
- [ ] ADR explains CDE selection, thresholds, and trade-offs.
- [ ] The reviewer can explain why a high aggregate score may still mean the dataset is not fit for a critical use.

### 12.3 Review rubric

| Rating | Evidence |
|---|---|
| Not ready | Rules are vague, owners absent, scores cannot be reproduced, or accuracy is assumed |
| Developing | Basic dimensions and metrics exist, but population, severity, or remediation is incomplete |
| Competent | CDEs are use-linked; rules are testable; results reproducible; actions and owners clear |
| Advanced | Tiered controls, explicit uncertainty, robust edge-case tests, lineage-driven root cause, and defensible exception governance |
| Production-minded | Rule lifecycle, evidence retention, execution health, replay/idempotency, cost, access control, and periodic review are designed |

---

## 13. Revision checklist

Before finalising your own implementation, verify:

### Business and CDEs
- [ ] Every CDE is tied to a decision, consumer, and consequence.
- [ ] Impact rationale and criticality tier are documented.
- [ ] Business owner, steward/rule owner, and remediation owner are distinguishable.
- [ ] Classification, purpose, lineage, and asset IDs are linked.
- [ ] Review triggers are defined.

### Rules and metrics
- [ ] Dimension and rule are not conflated.
- [ ] Population, grain, filters, numerator, denominator, null policy, and time window are explicit.
- [ ] Threshold rationale is recorded and not misrepresented as universal.
- [ ] Accuracy is supported by appropriate evidence.
- [ ] Critical defects cannot be hidden by an average.
- [ ] Empty/partial input and failed rule execution are not treated as success.
- [ ] Rule versions and test fixtures are traceable.

### Operational controls
- [ ] Failure response, severity, escalation, and evidence are defined.
- [ ] Quarantine has ownership, retention, ageing, and release criteria.
- [ ] Auto-correction is deterministic, reversible, and auditable.
- [ ] Exceptions have scope, approver, expiry, and compensating controls.
- [ ] Source remediation and downstream replay/backfill are planned.
- [ ] Batch, incremental, and streaming semantics are explicit.
- [ ] Access controls prevent sensitive values leaking through logs and reports.

### Verification and governance
- [ ] SQL/Python examples and formulas are checked.
- [ ] Synthetic known-good and known-bad cases are tested.
- [ ] Before/after row counts reconcile.
- [ ] Quality report states limitations and lineage coverage.
- [ ] CDE register, rule inventory, report, remediation plan, and ADR are reviewed.
- [ ] Completion gate is signed off by the appropriate business and technical owners.

---

## 14. Practice questions

1. Explain why a value can be valid but inaccurate.
2. How does uniqueness differ between a current-state table and a history table?
3. Why should email completeness and email syntax validity use separate denominators?
4. What should a metric return when the eligible population is empty, and why?
5. How can two systems be consistent but both wrong?
6. What evidence is needed to call a numeric amount accurate?
7. Why is a CDE not simply the most sensitive or most frequently used field?
8. What information makes a quality rule testable and governable?
9. When should a failed row be quarantined instead of rejecting an entire batch?
10. Why can an aggregate quality score hide a critical failure?
11. How should late-arriving dimension data affect referential-integrity checks?
12. What makes a streaming duplicate rule dependent on idempotency and replay semantics?
13. Which controls should be exact, and when can sampling be justified?
14. How do classification and lineage affect storage of failed-row evidence?
15. What conditions make an exception acceptable, and when must it expire?
16. How can a rule be green while its execution is not trustworthy?
17. How would you validate a source-to-report currency conversion?
18. Which quality checks are needed for an ML label beyond format validation?
19. Why does an AI knowledge index need provenance and permission checks?
20. What evidence proves that remediation improved quality without simply dropping hard-to-fix records?

---

## 15. Summary and transition to Topic 05

The core discipline is to define **what must be true, for which data and use, how it is measured, who is accountable, and what happens when it is false**.

- Dimensions classify the concern; rules make the concern testable.
- Measurements require a declared population, denominator, null policy, and time window.
- Thresholds need a business rationale; acceptance may include hard gates and severity overrides.
- CDEs are selected from business impact and lineage, not from column names alone.
- Accuracy requires stronger evidence than format or domain validation.
- Quality results must retain execution status, evidence, limitations, and ownership.
- Remediation should address root causes and verify the recovery.
- Tier controls by intended use; never let one aggregate score conceal critical defects.

**Next topic:** `05-data-observability-and-quality-service-levels.md` extends this foundation into ongoing signals, freshness/volume/distribution monitoring, SLIs/SLOs, alerting, incidents, and quality service-level operations. Topic 04 defines what to test and what is acceptable; Topic 05 addresses how the organisation continuously detects change and responds.

---

## Source and assumption note

This document follows the intended learning sequence and Topic 04 scope in `roadmap-Metadata-Lineage-Quality-and-Master-Data.md`: quality as fitness for use; the six foundational dimensions; CDE identification; testable rules with thresholds and owners; population-aware metrics; remediation and prevention; explicit accuracy handling; tiered controls; quality report and ADR; and the two recommended hands-on exercises. It also aligns with the broader roadmap’s integration of metadata, classification, field-level lineage, observability, master data, and the Northbridge synthetic final-project scenario.

The roadmap explicitly notes that topic and project files were empty when it was written. Therefore the roadmap is treated as the intended scope, not as evidence that empty topic files already specify detailed implementation requirements. All organisations, assets, data, thresholds, scores, and examples in this document are illustrative and synthetic.
