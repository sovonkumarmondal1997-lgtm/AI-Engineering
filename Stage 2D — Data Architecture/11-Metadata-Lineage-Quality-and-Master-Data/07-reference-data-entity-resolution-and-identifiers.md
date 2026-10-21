# Reference Data, Entity Resolution and Identifiers

**Stage:** 2D — Data Architecture  
**Module:** 11 — Metadata, Lineage, Quality and Master Data  
**Topic:** 07  
**Level:** Beginner → Intermediate → Advanced  
**Estimated effort:** 7–9 hours (roadmap recommendation)  
**Scenario:** Northbridge Bank, a fictional organization; all records and values in this document are synthetic.

> **Core distinction:** reference data defines allowed or mapped values; identifiers name entities within a defined scope; entity resolution judges whether records refer to the same real-world entity; master data management governs the resulting entity representation. These activities interact, but none is a substitute for another.

## 1. Purpose, scope, prerequisites, and outcomes

### 1.1 Purpose

This topic teaches how to govern shared code lists, design identifiers that remain interpretable across systems and time, and determine whether records describe the same entity. These capabilities underpin master data management (MDM), golden-record construction, consistent reporting, reliable joins, and cross-system operations.

A match is an evidence-based decision with uncertainty. It is not proof merely because two strings are similar. An identifier is an assigned label under a policy, not a claim that the entity is correctly understood. A golden record is a governed representation whose attributes may have different authoritative sources and survivorship rules.

### 1.2 Scope and boundaries

In scope: reference-data ownership and lifecycle; controlled vocabularies and mappings; identifier design, namespace and lifecycle; source-to-enterprise crosswalks; deterministic and probabilistic entity resolution; candidate generation, blocking, scoring, thresholding, evaluation, review, privacy, monitoring, and correction.

Out of scope: a vendor-specific product configuration, a universal matching algorithm, and a claim that one score or threshold is appropriate for every domain. Specific standards may govern particular reference lists; validate the applicable standard and version with the data owner rather than assuming one universal code set.

### 1.3 Prerequisites and sequence

The module roadmap specifies **Topic 04 and Topic 06 at Beginner level**, plus **P4: data dictionary, naming, keys, entities, and schema evolution**. Topic 04 supplies quality dimensions, critical data elements (CDEs), testable rules, thresholds, ownership, and remediation. Topic 06 supplies master domains, golden records, source provenance, attribute-level survivorship, synchronization, merge/unmerge, and stewardship. The roadmap recommends studying Topic 07's Beginner level before Topic 06's Advanced level, even though the files remain in numeric order.

Readiness checks:

- Explain uniqueness, referential integrity, validity, and completeness, and why a high aggregate quality score can hide a critical defect.
- Identify an entity, its attributes, business key, technical key, and relationships.
- Explain owner, steward, source system, lineage, idempotency, and reconciliation.
- Distinguish a duplicate record from two legitimate records with similar attributes.

### 1.4 Learning outcomes

By the end, you should be able to:

1. Govern reference lists with owners, versions, effective dates, deprecation rules, and consumer mappings.
2. Distinguish reference data, master data, transaction data, and metadata.
3. Define identifiers with explicit entity type, namespace, scope, lifecycle, non-reuse, and merge handling.
4. Design a source-to-enterprise identifier crosswalk.
5. Build a matching workflow from normalization through blocking, scoring, decisions, review, and publication.
6. Explain deterministic and probabilistic matching and their limitations.
7. Calculate precision, recall, false-positive/negative counts, F1, and blocking metrics using explicit denominators.
8. Choose review bands based on labelled evidence, business impact, and reviewer capacity—not intuition alone.
9. Preserve auditability, privacy, explainability, and downstream correctness during match changes, merges, and unmerges.
10. Deliver matching rules and evaluation, an identifier policy, and a reference-data governance/mapping package.

## 2. Beginner foundations and terminology

### 2.1 Four data categories that must not be confused

| Category | What it represents | Example | Typical control |
|---|---|---|---|
| Reference data | Governed values used to classify or constrain other data | Country code, currency code, account status | Approved code list, version, effective dates |
| Master data | Core business entities and their governed attributes | Customer, product, legal entity | Ownership, identity resolution, survivorship, lifecycle |
| Transaction data | Events or business activity involving entities | Payment, order, account posting | Event identity, time, reconciliation, transaction controls |
| Metadata | Information describing data and its context | Field definition, owner, source, lineage, classification | Catalogue, definitions, lineage and change management |

A country code such as `GB` is reference data; a customer record whose country attribute is `GB` is master or operational data depending on its purpose; a payment is transactional data; the definition and owner of the country field are metadata.

### 2.2 Key terms

- **Reference list / code list:** governed set of permitted codes and meanings.
- **Controlled vocabulary:** approved terms used consistently in a domain; it may include labels and relationships, not just short codes.
- **Enumeration:** finite set of values enforced by a schema or application. An enumeration may be locally coded and is not automatically governed enterprise reference data.
- **Canonical value:** the chosen internal representation used to harmonize equivalent source values.
- **Mapping / crosswalk:** governed correspondence between values or identifiers in different systems.
- **Identifier:** value assigned to distinguish an entity within a declared scope and lifecycle.
- **Natural/business identifier:** a value drawn from a business domain, such as an account number. It may be meaningful, mutable, or reusable unless policy prevents that.
- **Surrogate/technical identifier:** a generated identifier intended to be stable and usually non-semantic.
- **Namespace:** context that defines who issued an identifier, what kind it is, and where uniqueness applies.
- **Entity resolution:** deciding whether two or more records represent the same real-world entity.
- **Blocking / candidate generation:** selecting plausible pairs for comparison instead of comparing every record with every other record.
- **Match score:** evidence summary produced by a rule or model; not a probability unless calibrated and validated as one.
- **Threshold / review band:** decision boundaries used to route candidates to automatic match, manual review, or non-match.
- **Crosswalk:** mapping from a source identifier (including its source namespace) to an enterprise identifier.

**Analogy:** an identifier is like a reference number on a file; entity resolution is the process of deciding whether two files concern the same person or organization. The number does not itself prove the decision is correct.

### 2.3 Why names are poor identifiers

Names can be duplicated, misspelled, transliterated, changed, abbreviated, reordered, or shared by unrelated people. Email addresses and phone numbers can be shared, recycled, changed, or absent. Addresses are mutable and may describe a household, branch, or mailing destination rather than one entity. Even government-issued identifiers may have domain-specific scope, legal restrictions, data-quality problems, or lifecycle rules. Use such attributes as matching evidence only where lawful and appropriate; do not silently promote them into universal identifiers.

### 2.4 Entity, record, identifier, and match decision

One real-world entity can have many source records and many identifiers over time. A source record is a representation in one system. An identifier names an entity within its scope. A match decision links records based on evidence and a policy. A master record consolidates governed identity and attributes. Keep these as separate concepts and data structures so a match can be challenged without destroying source history.

## 3. Reference data concepts and governance

### 3.1 What reference data does

Reference data constrains, classifies, or translates values shared across business processes. Examples include country, currency, product type, legal entity type, channel, risk category, and lifecycle status. A reliable reference list improves valid-value enforcement, joins, reporting consistency, API contracts, and interoperability.

Without governance, one system might store `UK`, another `GB`, and another `826` for the same intended country. A join may fail, a report may split one category into three, or an invalid value may pass unnoticed. However, two codes that look different are not necessarily equivalent; the mapping must be approved by an accountable owner.

### 3.2 Reference data inventory and ownership

Every governed list should have a named business owner, steward, technical custodian, authoritative source, scope, definition, classification, consumers, and change process. Technical teams can enforce the list, but business owners decide what the values mean and whether mappings are semantically valid.

Suggested inventory fields:

| Field | Purpose |
|---|---|
| `reference_list_id` | Stable identity of the list, independent of its display name |
| `name`, `definition`, `domain` | Meaning and business context |
| `owner`, `steward`, `custodian` | Decision accountability, maintenance, implementation |
| `source_of_authority` | Where approved values originate |
| `version`, `valid_from`, `valid_to` | Version and effective period |
| `status` | Draft, approved, active, deprecated, retired |
| `classification`, `permitted_purpose` | Handling and use constraints |
| `consumer_contracts` | Systems and interfaces depending on the list |
| `change_ticket`, `approval_evidence` | Traceability and approval |

### 3.3 Code lists, controlled vocabularies, mappings, and enforcement

A code list maps a stable code to a defined meaning. A controlled vocabulary governs the permitted terms and their semantic relationships. An enumeration is a finite set accepted by a specific interface or schema. These overlap but are not interchangeable: a schema enumeration may be only a local technical constraint, while enterprise reference data requires ownership, versioning, semantic mapping, and consumer change management.

Valid-value enforcement can occur at several layers:

1. **Ingress:** reject, quarantine, or explicitly map unsupported source values.
2. **Storage:** enforce foreign keys or reference-list membership where feasible.
3. **Transformation:** apply versioned mappings and record the mapping version.
4. **Serving/API:** validate contract values and provide documented compatibility behavior.
5. **Monitoring:** track unmapped values, stale versions, deprecated-code usage, and distribution shifts.

Do not replace an invalid value with a default silently. A default can conceal source defects and change business meaning. Prefer quarantine, a documented exception, or an approved mapping.

### 3.4 Worked mapping: inconsistent country codes

The following is a fictional mapping policy for a synthetic integration. It is not an assertion that all code systems use these exact representations.

| Source system | Source code | Source meaning supplied | Canonical code | Decision |
|---|---|---|---|---|
| CRM-A | `UK` | United Kingdom | `GB` | Approved mapping under mapping version `country-map-v3` |
| LEDGER-B | `GB` | United Kingdom | `GB` | Direct canonical code |
| WEB-C | `826` | United Kingdom | `GB` | Approved only if source code-set/version confirms meaning |
| CRM-A | `XX` | Unknown/unclear | — | Quarantine for owner review; do not guess |

A mapping record should include source system, source code, source code-set version, canonical list/version, canonical code, effective dates, approval, and whether conversion is lossless. If one source value represents several canonical concepts, the mapping is ambiguous and requires business resolution rather than a one-to-one assumption.

**Example mapping table (SQL, illustrative):**

```sql
CREATE TABLE reference_mapping (
    mapping_id          INTEGER PRIMARY KEY,
    source_system       TEXT NOT NULL,
    source_list         TEXT NOT NULL,
    source_code         TEXT NOT NULL,
    source_version      TEXT NOT NULL,
    canonical_list      TEXT NOT NULL,
    canonical_code      TEXT NOT NULL,
    mapping_version     TEXT NOT NULL,
    valid_from          TEXT NOT NULL,
    valid_to            TEXT,
    approval_status     TEXT NOT NULL CHECK
        (approval_status IN ('DRAFT', 'APPROVED', 'RETIRED')),
    CHECK (valid_to IS NULL OR valid_to > valid_from),
    UNIQUE (source_system, source_list, source_code,
            source_version, mapping_version, valid_from)
);
```

This schema demonstrates core controls, not a complete temporal model. Production implementations should define timezone/date semantics, overlapping-period prevention, canonical-code foreign keys, transaction-time history, approvals, and concurrency behavior. ISO dates are used as text here for portability; a production database should use an appropriate date/time type.

### 3.5 Versioning, effective dates, deprecation, and historical interpretation

A code list changes when meanings are added, renamed, split, merged, deprecated, or retired. Overwriting a row can make historical transactions appear to have used a meaning that did not exist at the time. Preserve versions and effective periods so consumers can interpret values as they were valid when recorded.

- **Valid time:** when the code or mapping is true in the business domain.
- **Transaction/system time:** when the platform recorded the assertion or change.
- **Deprecation:** no longer recommended for new records; existing historical uses may remain valid.
- **Retirement:** no longer accepted for new use, subject to explicit historical and migration policy.
- **Replacement mapping:** a governed successor relationship; it may be one-to-one, one-to-many, or lossy.

Do not assume a retired code can always be replaced mechanically. If an old category splits into two new categories, historical records may not contain enough information to choose one. Record the conversion as lossy and preserve the original code and version.

### 3.6 Distribution and change management

Reference data can be distributed by API, database table, event, file, or versioned package. Choose based on freshness needs, consumer count, availability requirements, and operational capacity. Every delivery should communicate list identity, version, effective time, schema, change type, and compatibility policy. Consumers need a plan for unknown codes, cached versions, rollback, replay, and reconciliation.

A safe change sequence is: propose → assess semantics and consumers → approve → publish a new version → notify consumers → validate adoption → retire old values only under policy. For critical code lists, use backward-compatible additions where possible and avoid changing the meaning of an existing code in place.

### 3.7 Reference data quality rules

Connect the list to Topic 04 quality concepts and, where operational monitoring is required, Topic 05 observability. Define rules with population, denominator, threshold, severity, owner, response, and exception behavior.

Examples:

- Validity: every non-null `country_code` belongs to the permitted code set for the field's declared code-set version.
- Referential integrity: every product transaction code resolves to a valid list entry for its applicable time.
- Conformity: source values follow the required representation before mapping.
- Completeness: every in-scope record requiring a country has one.
- Timeliness: approved list changes reach critical consumers within the agreed window.
- Mapping coverage: percentage of distinct in-scope source codes with an approved mapping.

Formula: `mapping coverage = distinct in-scope source codes with an approved mapping / total distinct in-scope source codes × 100%`. If 96 of 100 observed codes are approved, coverage is `96 / 100 × 100% = 96%`. The denominator is the 100 distinct codes in the stated scope and observation window, not 100 records; four unmapped codes may occur in millions of rows and still represent a material semantic risk.

## 4. Identifier design and lifecycle

### 4.1 Identifier properties

An identifier policy should state:

- **Entity type:** what kind of thing is identified (customer, account, product, household, legal entity).
- **Uniqueness scope:** within a table, source system, issuing authority, enterprise, or global domain.
- **Stability:** whether it remains associated with the same entity through ordinary attribute changes.
- **Namespace:** issuer/system + entity type + identifier type, or an equivalent unambiguous scheme.
- **Non-reuse:** whether a retired value can ever be assigned to another entity (recommended: no for durable identity identifiers).
- **Mutability and semantics:** whether the identifier embeds business meaning that may change.
- **Lifecycle:** issuance, activation, aliasing, merge, split, suspension, retirement, and retention.
- **Governance:** issuer, approval, collision handling, audit, and access controls.

Uniqueness without scope is incomplete. `123` may identify a customer in CRM-A and a different customer in CRM-B. A globally unique value can still be wrong if it was assigned to the wrong entity. Stability does not imply that an identifier should be exposed to every consumer.

### 4.2 Natural/business keys versus surrogate keys

| Design | Advantages | Risks / limitations | Appropriate use |
|---|---|---|---|
| Natural/business key | Meaningful to users; may align with an external business process | May change, be reused, be sensitive, or have ambiguous scope | When semantics and issuing authority are governed and stability is adequate |
| Surrogate key | Usually stable and non-semantic; decouples identity from attributes | Requires crosswalks; may be meaningless outside its system; generation must be controlled | Internal primary key or enterprise identity |
| Composite key | Can express scope, such as `(source_system, source_customer_id)` | Every component must be preserved; system rename and normalization can break joins | Source-local identity when no single key is globally unique |
| External identifier | Supports exchange with an external authority | External rules, availability, legal use, and lifecycle may differ | Only for approved purpose and domain |

No identifier type is universally best. A natural key can be an excellent source-system key but a poor enterprise primary key. A surrogate key is not automatically stable if the platform regenerates it during migration. Avoid encoding mutable business attributes (such as postcode or customer type) into durable identifiers.

### 4.3 Namespace design

A readable composite representation might be `crm-a:customer:12345`, while an internal surrogate might be an opaque UUID. The namespace makes the issuer, entity type, and scope explicit. The literal format is a design choice; store components in separate fields when possible instead of relying only on parsing a string.

Recommended logical fields:

| Field | Example | Rule |
|---|---|---|
| `issuer_system` | `CRM-A` | Governed system identity, not a display label that may change silently |
| `entity_type` | `CUSTOMER` | Controlled vocabulary |
| `identifier_type` | `SOURCE_CUSTOMER_ID` | Explicit semantics |
| `identifier_value` | `12345` | Preserve representation as issued; normalize only under policy |
| `valid_from`, `valid_to` | Effective period | Explicit lifecycle semantics |
| `status` | `ACTIVE`, `RETIRED`, `REDIRECTED` | Controlled lifecycle state |

Do not drop leading zeros or coerce identifiers to numbers unless the issuing contract explicitly says the value is numeric and has no formatting significance. An identifier `00123` can differ from `123` in a source system.

### 4.4 Identifier reuse, changes, retirement, merge, and split

**Never reuse a durable enterprise identity identifier for a different entity.** Reuse makes historical facts, audit records, references, and delayed events point to the wrong entity. Retired identifiers should remain resolvable to their historical entity or status, subject to retention and privacy obligations.

A lifecycle policy should define:

1. **Issue:** authorized issuer allocates a unique value; collisions are rejected and audited.
2. **Activate:** entity passes minimum validation and ownership controls.
3. **Change:** source attributes or business identifiers change without silently changing enterprise identity.
4. **Alias/link:** multiple source identifiers may refer to one enterprise entity while preserving provenance.
5. **Merge:** two enterprise records are determined to represent one entity; designate a survivor or stable entity identity and preserve redirects/aliases.
6. **Split/unmerge:** reverse a wrong link or divide an incorrectly consolidated cluster; restore source-to-entity associations and recalculate dependent outputs.
7. **Retire:** stop new use while preserving necessary history and explicit resolution behavior.

If an external source reuses a customer number, represent the source identifier as a time-bounded assignment or include the source's generation/validity context. Do not assume `source_system + source_id` is unique forever if the source recycles IDs.

### 4.5 Source-to-enterprise crosswalk

A crosswalk links an identifier in its namespace to an enterprise identifier, with status, effective dates, evidence, and audit history. It should not erase the source identifier or rewrite history invisibly.

| source_system | source_entity_type | source_id | enterprise_id | status | valid_from | valid_to | decision_id |
|---|---|---|---|---|---|---|---|
| CRM-A | CUSTOMER | `C-104` | `ENT-00041` | ACTIVE | 2026-01-10 | — | `DEC-1001` |
| CARD-B | CUSTOMER | `00982` | `ENT-00041` | ACTIVE | 2026-02-02 | — | `DEC-1008` |
| WEB-C | CUSTOMER | `W-77` | `ENT-00041` | LINKED | 2026-03-14 | — | `DEC-1020` |

All values are synthetic. The rows assert an approved identity relationship under this example's assumptions, not that equal names alone prove a match.

Crosswalk controls:

- Enforce uniqueness over the correct namespace and validity scope; decide whether one active source identifier can map to more than one enterprise entity.
- Preserve prior assignments and decision IDs, including reason, rule/model version, reviewer, and evidence references.
- Support redirect resolution for retired or merged enterprise IDs.
- Reconcile source counts, unmapped records, duplicate mappings, and dangling targets.
- Propagate changes through lineage-aware impact analysis and consumer contracts.

### 4.6 Downstream identifier-change example

Suppose `ENT-00041` is incorrectly merged into `ENT-00017`. A consumer has stored `ENT-00041` in a fact table and a cache. A robust correction plan must update the crosswalk and redirect policy, emit a versioned correction/unmerge event, identify affected rows through lineage, reprocess or correct consumer state idempotently, invalidate caches, and reconcile counts. A silent overwrite can leave consumers disagreeing about identity.

Use stable event fields such as `event_id`, `event_type`, `entity_type`, `entity_id`, `previous_entity_id`, `new_entity_id`, `decision_id`, `effective_at`, `recorded_at`, `policy_version`, and `correlation_id`. Avoid placing raw sensitive matching attributes in general-purpose events; provide controlled references where authorized.

## 5. Entity-resolution fundamentals and workflow

### 5.1 What entity resolution decides

Entity resolution (record linkage) evaluates whether records from the same or different sources refer to the same real-world entity. It can identify duplicates within one source or link records across systems. It does not decide which attribute value is authoritative; that is a separate survivorship/master-data decision (Topic 06).

A match result should include the two record references, decision (`MATCH`, `NON_MATCH`, `REVIEW`), evidence/features, score or rule, threshold policy version, candidate-generation method, timestamp, and model/rule version. Store enough evidence to explain and reverse a decision without copying unnecessary sensitive fields into audit logs.

### 5.2 Matching workflow

1. **Define the entity and decision cost.** Customer versus household versus legal entity changes the matching rules.
2. **Select permitted fields.** Use purpose limitation, legal basis, access restrictions, and minimization.
3. **Profile and validate inputs.** Measure missingness, invalid values, distributions, and source-specific error patterns.
4. **Normalize representations.** Create comparison forms while preserving original values and provenance.
5. **Generate candidates / block.** Reduce comparisons, then measure the matches the blocking stage misses.
6. **Compare features.** Exact agreement, disagreement, string similarity, date distance, address components, and field reliability.
7. **Score and classify.** Apply explainable deterministic rules or a calibrated probabilistic model and decision bands.
8. **Review uncertain/high-impact cases.** Give stewards evidence, reason codes, and an override path.
9. **Cluster and enforce constraints.** Prevent invalid transitive merges and entity-type conflicts.
10. **Publish crosswalk/link changes.** Version decisions and propagate changes idempotently.
11. **Monitor and learn.** Sample decisions, measure errors, track drift, and test rule/model changes before rollout.

### 5.3 Normalization: useful but lossy

Normalization creates comparison representations, such as case-folding, trimming whitespace, standardizing punctuation, parsing address components, or normalizing phone formatting under a country context. Preserve raw values and transformation versions. A normalized string is not a replacement for the source value.

Synthetic name examples:

| Raw name | Comparison form (illustrative) | Caution |
|---|---|---|
| ` A. Sharma ` | `a sharma` | Initial may hide a different given name |
| `A Sharma` | `a sharma` | Exact normalized equality is weak identity evidence |
| `Anita Sharma` | `anita sharma` | Similarity to initial form depends on a justified rule |
| `Ana María López` | `ana maria lopez` | Accent folding may be useful but can collapse distinct forms |

A simplistic Python normalization helper:

```python
import re
import unicodedata

def normalize_name(value: str | None) -> str | None:
    """Return a comparison form; never overwrite the original value."""
    if value is None:
        return None
    text = unicodedata.normalize("NFKD", value.casefold())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None

assert normalize_name(" A. Sharma ") == "a sharma"
assert normalize_name(None) is None
```

This code uses only Python's standard library and targets Python 3.10+. It is illustrative, not a universal name standard: Unicode normalization, transliteration, token ordering, punctuation, honorifics, initials, and script conversion require domain-aware decisions. Accent folding may collapse meaningful distinctions. Avoid applying one normalization rule blindly across languages or identifiers. Do not normalize the original ID in a way that destroys leading zeros or issuer semantics.

### 5.4 Deterministic matching

Deterministic matching uses exact or rule-based conditions, for example: same valid source-issued unique identifier in the same namespace and time scope; or exact email plus another independently reliable field under an approved policy.

**Advantages:** explainable, fast, easy to test, suitable for high-confidence identifiers. **Limitations:** brittle to typos and missing data; exact values can be shared, recycled, mistyped, or incorrectly populated. A rule is only as trustworthy as the field semantics and source controls.

Use hard identifiers only when their authority, scope, uniqueness, validity period, and permitted use are understood. A national identifier or email should not be treated as a universal deterministic key without that validation.

### 5.5 Probabilistic matching

Probabilistic approaches combine evidence across fields, allowing partial agreement and disagreement. A Fellegi–Sunter-style model, for example, compares how likely observed agreements are among true matches versus non-matches. Supervised machine-learning models can also learn from labelled pairs. Both require representative labels, leakage-aware validation, calibration if scores are interpreted as probabilities, monitoring, and human accountability for high-impact outcomes.

Weighted scores are often used for teaching because they are transparent, but they are not inherently probabilistic. Correlated fields (for example, city and postcode) can double-count the same evidence. Missing values should not automatically count as agreement. A high score can reflect common names or correlated fields rather than identity certainty.

### 5.6 Explicit scoring example

Assume a deliberately simple score for a synthetic customer pair:

- normalized full name exact agreement: +35
- date of birth exact agreement: +30
- postcode exact agreement: +15
- phone exact agreement: +20
- explicit reliable disagreement on date of birth: −40
- missing field: 0 (no evidence either way)

Maximum positive score is 100. These weights are **illustrative only** and have not been empirically calibrated. The features may be correlated; the score is not a probability.

| Pair | Name | DOB | Postcode | Phone | DOB contradiction | Score | Illustrative outcome |
|---|---|---|---|---|---|---:|---|
| A | exact | exact | exact | exact | no | 100 | Auto-match candidate, only if policy and validation permit |
| B | exact | missing | exact | missing | no | 50 | Review band |
| C | similar, not exact | exact | different | missing | no | 30 (assume similarity feature not awarded in this example) | Non-match or review depending on calibrated policy |
| D | exact | different | exact | exact | yes | 30 | Contradiction override to review/non-match; do not let a sum hide it |

The table intentionally demonstrates that a numeric sum must not override hard constraints or contradiction rules. The precise treatment of pair C depends on the feature definition; the table awards zero for a merely similar name because this example defines points only for exact agreement.

A decision policy might route score `>= 90` to auto-match only after validation, `60–89` to manual review, and `< 60` to non-match, with explicit contradiction overrides. These boundaries are examples, not universal defaults. The row D score is 30 and the DOB contradiction rule still overrides the numeric band; the contradiction must be handled explicitly rather than relying on the score alone. A production design needs clear precedence, documented reason codes, and calibrated evaluation on labelled examples.

### 5.7 Match, non-match, and manual review

- **Match:** evidence meets the approved policy for linking records. Automatic merge should be reserved for cases whose measured risk is acceptable.
- **Non-match:** evidence supports keeping records separate, or a sufficiently strong contradiction applies. Do not confuse “insufficient evidence” with proven non-match.
- **Manual review:** uncertainty, conflicting evidence, or high impact requires a trained reviewer. The queue should display permitted evidence, missingness, reason codes, source quality, and policy version.

In many systems, use a third state such as `UNRESOLVED` for insufficient evidence rather than forcing a binary answer. The business action for each state must be defined: no link, provisional link, quarantine, or review. Reviewers need escalation rules, quality sampling, conflict-of-interest controls where appropriate, and an appeal/correction path.

## 6. Candidate generation, blocking, scoring, and thresholds

### 6.1 Why all-pairs matching does not scale

For `n` records, the number of unordered pairs in an all-pairs comparison is:

\[
P = \frac{n(n-1)}{2}
\]

where `P` is the number of pairs and `n` is the number of records. For `n = 1,000,000`, `P = 1,000,000 × 999,999 / 2 = 499,999,500,000`, approximately `5.0 × 10^11` pairs. This is often impractical and produces many obviously irrelevant comparisons.

### 6.2 Blocking and candidate generation

Blocking uses one or more keys or rules to limit comparison to plausible pairs, such as phonetic surname plus postcode prefix, exact phone suffix plus birth year, or source-provided stable identifiers. Candidate generation should optimize both reduction and recall. A single block key can miss a true match when the key is absent, misspelled, changed, or parsed differently.

Suppose 1,000,000 records are partitioned into 10,000 disjoint blocks of 100 records each. Within-block unordered pairs are:

\[
P_b = B \times \frac{s(s-1)}{2}
\]

where `B = 10,000` blocks and `s = 100` records per block. Therefore `P_b = 10,000 × (100 × 99 / 2) = 49,500,000`. Reduction versus all pairs is `1 − P_b/P = 1 − 49,500,000/499,999,500,000 ≈ 0.999901`, or about **99.9901% fewer comparisons**; the full all-pairs count is about 10,101 times larger. The arithmetic assumes disjoint, equal-sized blocks and only within-block comparisons. Real blocks vary in size, may overlap across passes, and can create duplicate candidates requiring deduplication.

**Reduction ratio** is commonly defined as `1 − candidate_pairs / all_possible_pairs`. Here it is about 99.9901%. It measures computational reduction, not match quality.

**Pair completeness** is `true matching pairs generated as candidates / all true matching pairs in the evaluation population`. If blocking generates candidates for 920 of 1,000 labelled true pairs, pair completeness is `920/1,000 = 92%`. The denominator is all known true pairs in that population, including those blocking failed to generate. This metric is crucial because a matcher cannot recover a true match that never becomes a candidate.

### 6.3 Multiple blocking passes and their trade-offs

Use multiple complementary passes where a single key is brittle: e.g., (1) normalized surname + postcode prefix; (2) phone + birth year; (3) exact source crosswalk or verified external key where permitted. Deduplicate candidates across passes while preserving which rules generated them. Measure pair completeness and reduction ratio for each pass and combined result.

Trade-offs: more passes usually improve candidate recall but increase cost, duplicate candidates, review load, and privacy exposure. Overly broad blocks create huge skew; overly narrow blocks miss true pairs. Watch block-size distributions, common-value blocks, null blocks, and source-specific coverage. Do not put every missing value into one shared block.

### 6.4 Cluster management and transitivity

Pairwise similarity is not automatically transitive. If A matches B and B matches C, it does not follow that A and C represent the same entity. This is a common source of over-merged clusters. Use cluster-level constraints, authoritative identifier conflicts, entity-type rules, maximum disagreement policies, and review of bridge records. Track cluster size, merge chains, reversals, and stability over time. For sensitive or high-impact domains, conservative linking may be safer than automatic connected-components clustering.

### 6.5 Threshold selection

Let `T_low` be the lower boundary and `T_high` the upper boundary, with `T_low < T_high`:

- score `>= T_high`: eligible for auto-match, subject to hard constraints and risk policy;
- `T_low <= score < T_high`: manual review;
- score `< T_low`: non-match or unresolved, depending on business policy.

Thresholds are chosen from labelled validation data, not borrowed as universal constants. Select a representative sample, label true match/non-match pairs under a documented adjudication protocol, separate training/tuning data from final test data, and evaluate thresholds by source, subgroup where lawful, missingness, and entity type. Estimate reviewer capacity and false-merge cost. A threshold that performs well on one source or period can fail after data formats or population patterns change.

### 6.6 Decision cost and review workload

False positives link distinct entities; false negatives fail to link records for the same entity. Costs are asymmetric and depend on context. A false customer merge may expose data or misdirect financial activity; a missed duplicate may fragment analytics or cause duplicate outreach. Set thresholds according to expected harm, reversibility, operational cost, and review capacity—not only aggregate accuracy.

Illustrative expected-cost formula:

`Expected cost = FP × C_FP + FN × C_FN + R × C_R`,

where `FP` is false-positive count, `FN` false-negative count, `R` number of manual-review cases, and each `C` is the cost per outcome in a common unit (for example, weighted cost points). If a test yields 3 false positives at 100 cost points each, 20 false negatives at 5 points each, and 50 reviews at 2 points each, expected cost is `3×100 + 20×5 + 50×2 = 300 + 100 + 100 = 500` points. The values are illustrative and require business-owner approval; they are not monetary estimates or a universal cost model.

## 7. Evaluation metrics and decision trade-offs

### 7.1 Confusion matrix for pair classification

Against labelled pairs:

| | Predicted match | Predicted non-match |
|---|---:|---:|
| True match | True positive (TP) | False negative (FN) |
| True non-match | False positive (FP) | True negative (TN) |

A labelled pair is a pair whose correct match status has been established under a defined adjudication process. Labels can be wrong or incomplete; document how labels were produced, disagreements resolved, and uncertain pairs treated.

### 7.2 Precision, recall, F1, false-positive rate

- **Precision** = `TP / (TP + FP)`. Denominator: all pairs predicted as matches. Of predicted matches, what fraction are correct?
- **Recall** = `TP / (TP + FN)`. Denominator: all true matches in the labelled evaluation set. What fraction did the matcher find?
- **F1** = `2 × precision × recall / (precision + recall)` when the denominator is non-zero. It is the harmonic mean of precision and recall and weights them equally; it does not encode business-specific error costs.
- **False-positive rate (FPR)** = `FP / (FP + TN)`. Denominator: all true non-match pairs. What fraction of true non-matches were incorrectly predicted as matches?
- **Accuracy** = `(TP + TN) / (TP + FP + FN + TN)`. Accuracy can be misleading when non-match pairs vastly outnumber true matches.

If a denominator is zero, report the metric as undefined/not estimable for that sample rather than silently reporting zero. For pair matching, the evaluation population and sampling strategy matter greatly: a randomly sampled set dominated by non-matches can make accuracy look high while precision or recall is poor.

### 7.3 Worked synthetic calculation

Suppose the labelled evaluation set contains 1,000 true matching pairs and the matcher proposes 900 pairs, of which 810 are true matches. Thus:

- `TP = 810`.
- `FP = 900 − 810 = 90`.
- `FN = 1,000 − 810 = 190` true matching pairs were not proposed.

Then:

\[
\text{Precision} = \frac{TP}{TP+FP} = \frac{810}{810+90} = \frac{810}{900} = 0.90 = 90\%
\]

\[
\text{Recall} = \frac{TP}{TP+FN} = \frac{810}{810+190} = \frac{810}{1000} = 0.81 = 81\%
\]

\[
F1 = \frac{2(0.90)(0.81)}{0.90+0.81} \approx 0.8526 = 85.3\%
\]

Interpretation: 90% of proposed matches were correct in this sample; the matcher found 81% of the true pairs. It still produced 90 false positives and missed 190 true pairs. Precision is not “the probability every future match is right”; it is an observed metric for this labelled sample and deployment distribution.

### 7.4 Why metrics need careful sampling

The number of possible non-match pairs is usually enormous. Labeling every pair is impractical. Use a documented evaluation design that includes likely matches, difficult negatives, different sources, missingness patterns, and realistic production traffic. If sampling is enriched for likely matches, correct for the sampling design before interpreting prevalence-dependent metrics. Keep a held-out test set and prevent leakage when multiple records from the same entity appear across splits.

Report metrics by relevant cohorts, source, time period, and data-quality condition. Small subgroup samples have uncertainty; do not rank groups based on noisy estimates without confidence intervals or adequate sample sizes. Keep a gold-standard labelled sample, record label provenance, and re-adjudicate disagreements.

### 7.5 Threshold evaluation table template

| Policy/model version | Threshold band | TP | FP | FN | Precision | Recall | Review rate | Pair completeness | FP/FN cost assumptions | Decision |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `ER-v1` | `T_high=...` | — | — | — | — | — | — | — | — | Pending evaluation |

For every metric, include the numerator, denominator, population, observation window, sample strategy, label version, and owner. A review rate is `reviewed-or-routed-to-review candidates / all candidates scored × 100%`; specify whether the numerator counts unique pairs or review tasks.

### 7.6 Metrics are not guarantees

Metrics measured on one labelled dataset do not guarantee performance on future data. Scores may drift because source systems change, population composition shifts, fields become missing, attackers manipulate attributes, or a code list changes. Monitor precision through adjudicated samples, recall through targeted audits and known-link tests, pair completeness at blocking, review outcomes, reversal rates, and downstream impact. Some true matches are never observable; acknowledge that recall estimates have uncertainty.

## 8. Advanced architecture, governance, and failure handling

### 8.1 Decision rights and stewardship

Define who owns entity semantics, who approves reference mappings, who can issue enterprise IDs, who can approve automated merges, who adjudicates review cases, and who can reverse decisions. Keep operational privileges separate where practical. A model team may tune features, but should not unilaterally decide business risk tolerance or permitted use of sensitive fields.

Minimum decision record:

- candidate record IDs and namespaces;
- outcome and reason code;
- evidence/features actually used (or controlled evidence references);
- candidate-generation pass and matching policy/model version;
- score and threshold band, if applicable;
- reviewer/approver and timestamps;
- effective time, recorded time, and correction history;
- downstream publication/correction status.

### 8.2 Merge, link, unmerge, and recovery

Do not equate a match decision with irreversible record destruction. Keep source records, crosswalks, decisions, and provenance. Prefer link/merge semantics that can be reversed. Before merging, check cluster constraints, high-risk conflicts, and impact. On unmerge, identify which source records belong to which entity, restore or allocate IDs according to policy, recalculate affected golden records, publish correction events, and reconcile consumers.

A merge event should be idempotent: replaying the same event must not create a second merge or duplicate side effect. Include a unique event/decision ID and monotonic version or sequence where required. Consumers should reject stale updates, process corrections, and support reconciliation. Use the lineage graph from Topic 03 to locate affected downstream assets, and Topic 05 observability to monitor propagation and consumer lag.

### 8.3 Matching and golden-record survivorship are separate

Entity resolution answers “which source records represent the same entity?” Survivorship answers “which attribute value should the governed master representation publish, and why?” A high-confidence match does not mean the source values agree, nor does it determine which address or status is authoritative.

For example, two records may match confidently while carrying different addresses. The master-data policy may choose an address from a verified source with valid effective dates, retain both mailing and residential addresses as separate roles, or send the conflict to a steward. Do not use match score as an attribute-quality or survivorship score. Preserve attribute-level provenance and status in line with Topic 06.

### 8.4 Privacy, security, and minimization

Matching can concentrate personal or sensitive attributes and create new linkability risks. Design controls before implementation:

- Establish lawful purpose and permitted use for each field and linkage activity.
- Use the minimum attributes necessary; avoid collecting sensitive fields “just in case.”
- Restrict access to raw values, match evidence, review queues, and exports by role and purpose.
- Encrypt data in transit and at rest, manage keys, and audit access.
- Tokenization or privacy-preserving record linkage may reduce exposure in some designs, but is not automatically anonymous and can leak equality/frequency patterns.
- Apply retention, deletion, consent/purpose, and residency requirements to source data, indexes, features, labels, logs, and derived links.
- Avoid exposing personal data in telemetry, debug logs, or broad change events.

Do not assume hashing makes identifiers safe: low-entropy values can be guessed, and deterministic hashes preserve equality and can enable linkage. Use keyed cryptographic constructions or approved privacy-preserving protocols only with security review; these methods do not eliminate governance obligations.

### 8.5 Bias, fairness, and sensitive attributes

Matching error rates can vary by language, script, naming convention, transliteration, age, geography, data access, or source quality. Missingness is not evenly distributed. Evaluate false-positive and false-negative rates across legally and ethically appropriate cohorts where collection and analysis are permitted. Avoid using protected or sensitive attributes as matching features unless there is an explicit lawful basis, necessity, proportionality, and review. Do not infer sensitive traits from names or addresses.

A fairness check should include cohort definitions, sample size, uncertainty, error severity, and remediation plan. If a cohort lacks adequate labels, report that uncertainty rather than asserting parity. A lower overall error rate can still hide serious harm in a small group.

### 8.6 Operational modes: batch, incremental, and near-real-time

- **Batch:** suitable for periodic deduplication or large backfills; requires reproducible snapshots, restartability, and reconciliation.
- **Incremental:** compare new/changed records against a maintained index; lower latency but requires correct invalidation and re-evaluation when relevant records change.
- **Near-real-time:** useful when downstream decisions require low latency; increases availability, ordering, consistency, and operational complexity.

Choose based on business latency, error cost, source update rate, review capacity, and recovery requirements. Re-run matching when rules or reference lists change, but version decisions so old and new outcomes can be compared. Do not silently overwrite historic decisions when a model is retrained.

### 8.7 Drift and monitoring

Monitor at least:

- input field completeness, validity, and source-level distributions;
- normalization failures and unparseable values;
- block sizes, candidate volume, reduction ratio, and pair completeness;
- score distributions and match/non-match/review rates;
- precision and false-positive/negative rates from adjudicated samples;
- manual review backlog, turnaround time, override rate, and reviewer disagreement;
- merge reversals, cluster-size changes, and identity churn;
- unmapped reference codes, deprecated-code use, and mapping coverage;
- downstream propagation lag, stale identifier references, and reconciliation failures.

Set thresholds from baselines and business risk. A sudden rise in match rate may indicate improved data, a source defect, a blocking change, or a model regression. Alerts should trigger investigation, not automatically imply the model is wrong. Record run IDs, input snapshots, policy versions, and reproducible evaluation artifacts.

### 8.8 Failure modes and controls

| Failure mode | Why it matters | Preventive/detective control | Recovery |
|---|---|---|---|
| Same-name false merge | Different people share common names | Require independent evidence; conservative bands; sample audits | Unmerge, correct crosswalks and downstream state |
| Address change causes missed match | One mutable field differs | Multiple blocking passes; temporal history; field reliability | Re-match affected population and review candidates |
| Source ID reused | Old events point to a new entity | Time-bounded ID assignments; non-reuse contract; source reconciliation | Split historical mappings and repair downstream links |
| Reference code overwritten | Past values acquire false meaning | Versioned lists and effective dates | Restore prior version; reprocess affected data |
| Block too narrow | True pairs never scored | Pair-completeness tests and multiple passes | Add blocking pass and backfill candidates |
| Block too broad | Cost and review queue spike | Block-size caps, skew monitoring, partition strategy | Isolate pathological blocks and process safely |
| Transitive cluster chain | Weak bridge links merge distinct entities | Cluster constraints, edge provenance, review | Split cluster and rebuild dependent records |
| Model drift | Historical thresholds no longer fit | Holdout/gold set, drift and error monitoring | Roll back or re-tune with governance approval |
| Sensitive fields leak | Expanded exposure and linkage risk | Minimization, role access, tokenization review, log hygiene | Contain, investigate, follow incident process |

### 8.9 Architecture decision record (ADR)

Record the decision to use deterministic rules, probabilistic scoring, human review, or a hybrid; the entity definition; source scope; permitted features; blocking passes; thresholds and overrides; expected metrics; costs and reviewer capacity; identifier strategy; reference-data authority; privacy controls; monitoring; rollback and unmerge; alternatives rejected; assumptions; and conditions that would trigger reassessment. State explicitly that thresholds and weights are validated for the target context, not universal truths.

## 9. Worked case and practical exercises

### 9.1 Worked case: synthetic Northbridge customer records

Assume three fictional systems contain these records:

| Record | Source ID | Name | DOB | Postcode | Phone | Notes |
|---|---|---|---|---|---|---|
| A | CRM-A:`C-104` | `Anita Sharma` | `1988-04-12` | `AB1 2CD` | `07000 111111` | Source has verified DOB |
| B | CARD-B:`00982` | `Anita Sharma` | `1988-04-12` | `AB1 2CD` | missing | Independent system; no phone |
| C | WEB-C:`W-77` | `Anita S.` | `1988-04-12` | `AB1 2EF` | `07000 111111` | Name abbreviated; postcode differs |
| D | CRM-A:`C-205` | `Anita Sharma` | `1978-04-12` | `AB1 2CD` | `07000 111111` | Same name and phone, DOB conflicts |

All values are synthetic. Records A and B share name, DOB, and postcode; this is strong evidence under the illustrative scoring policy, but still requires the target domain's validated rule and identity-risk policy. Record C may be a candidate through a second blocking pass (DOB + phone), but the name abbreviation and postcode difference require an explainable decision. Record D must not be auto-merged merely because several fields agree: the DOB conflict is material and should trigger review or non-match according to the approved policy.

Possible design:

1. Normalize names and phone formatting without replacing raw values.
2. Pass 1 blocks on normalized surname + postcode prefix; Pass 2 blocks on exact phone + DOB year; retain candidate-generation provenance.
3. Apply a hard contradiction rule for conflicting verified DOB values; route to review rather than allowing a weighted sum to hide the conflict.
4. Score remaining pairs using validated features and use conservative auto-match thresholds only where evaluation supports them.
5. Have a steward adjudicate ambiguous pairs, record evidence references and policy version, then write source-to-enterprise crosswalk links.
6. Build a golden record separately using Topic 06 survivorship rules per attribute.
7. Monitor link quality, review overrides, cluster size, downstream propagation, and unmerge rate.

### 9.2 Exercise A — Matching rules and evaluation (roadmap exercise)

**Scenario:** 100 synthetic customer records across three systems with labelled duplicate pairs.

**Tasks:**

1. Define the entity precisely (individual customer, household, or legal entity).
2. Profile missingness and invalid values for each source and field.
3. Define at least two normalization functions and explain their lossy behavior.
4. Create deterministic rules and probabilistic fallback features; specify hard contradictions.
5. Define at least two blocking passes and estimate all-pairs cost versus candidate count.
6. Label candidate pairs with a documented adjudication protocol; keep a held-out test set.
7. Evaluate thresholds using precision, recall, F1, FPR, review rate, and blocking pair completeness.
8. Analyze false positives and false negatives by cause and cohort where lawful and adequately sampled.
9. Propose threshold bands and show expected error cost and review workload.
10. Document model/rule versioning, correction, merge/unmerge, privacy, and monitoring.

**Deliverables:** matching rules; feature dictionary; blocking design; labelled evaluation table; metric calculations; error analysis; threshold decision; steward workflow; ADR. **Validation:** a reviewer can reproduce metrics from the labelled sample and explain why a high score is not certainty.

### 9.3 Exercise B — Identifier and reference-data policy (roadmap exercise)

**Scenario:** country and product codes differ across systems; one source reuses IDs after deletion.

**Tasks:**

1. Inventory each reference list, its owner, authority, version, effective dates, status, and consumers.
2. Create approved mappings for equivalent values; identify ambiguous/lossy mappings and unmapped values.
3. Define namespaces, identifier types, issuance authority, uniqueness scope, non-reuse, retirement, merge, split, and redirect rules.
4. Design a source-to-enterprise crosswalk with validity periods and decision provenance.
5. Specify reference data distribution, change approval, consumer compatibility, and rollback.
6. Define quality tests for valid values, mapping coverage, duplicates, dangling IDs, and effective-date conflicts.
7. Simulate an identifier reuse incident and a wrong merge; describe repair and downstream reconciliation.

**Deliverables:** reference-data inventory and mappings; identifier policy; crosswalk model; lifecycle state diagram; change/distribution plan; quality tests; ADR. **Validation:** reuse is prevented or safely scoped, mapping coverage is reported with its denominator, and ambiguous transformations are explicitly identified.

### 9.4 Python exercise: reproducible metric calculation

The following is a small, dependency-free helper for counts already computed against a labelled pair set. It does not perform entity resolution or validate labels.

```python
from math import isclose

def pair_metrics(tp: int, fp: int, fn: int, tn: int) -> dict[str, float | None]:
    for name, value in {"tp": tp, "fp": fp, "fn": fn, "tn": tn}.items():
        # bool is a subclass of int in Python; reject it because True/False
        # are not valid confusion-matrix counts.
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer count")

    precision_den = tp + fp
    recall_den = tp + fn
    fpr_den = fp + tn
    total = tp + fp + fn + tn

    precision = tp / precision_den if precision_den else None
    recall = tp / recall_den if recall_den else None
    fpr = fp / fpr_den if fpr_den else None
    accuracy = (tp + tn) / total if total else None
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None and recall is not None and precision + recall > 0
        else (0.0 if precision == 0 and recall == 0 else None)
    )
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": fpr,
        "accuracy": accuracy,
    }

m = pair_metrics(tp=810, fp=90, fn=190, tn=910)
assert isclose(m["precision"], 0.90)
assert isclose(m["recall"], 0.81)
assert isclose(m["f1"], 2 * 0.90 * 0.81 / (0.90 + 0.81))
assert isclose(m["false_positive_rate"], 90 / (90 + 910))
assert isclose(m["accuracy"], (810 + 910) / (810 + 90 + 190 + 910))
try:
    pair_metrics(tp=True, fp=0, fn=0, tn=0)
except ValueError:
    pass
else:
    raise AssertionError("Boolean values must not be accepted as counts")
```

Assumptions and limitations: the caller supplies valid, mutually exclusive counts from a defined labelled population. The main worked example establishes `TP=810`, `FP=90`, and `FN=190`, but those counts alone do not determine `TN`. **For this code demonstration only**, additionally assume the evaluation universe contains 1,000 true non-match pairs, of which 90 are false positives and 910 are true negatives. Under that explicitly added assumption, `FPR = 90/(90+910) = 9%` and `accuracy = (810+910)/(810+90+190+910) = 86%`. Do not infer TN from match counts alone; it depends on the defined evaluation universe. The helper returns `None` for undefined metrics and does not calculate confidence intervals, adjust for sampling, or handle uncertainty in labels. Run tests on a controlled environment before production use.

### 9.5 Suggested test cases

- A verified source ID agrees within its declared namespace and validity period.
- Same name but conflicting verified DOB: must not auto-merge under the stated policy.
- Missing DOB on both records: missingness must not count as agreement.
- True match missed by one block but recovered by another: pair completeness improves.
- Source ID reused after retirement: old and new validity periods remain distinguishable.
- Code mapping changes after an effective date: historical interpretation remains reproducible.
- Merge event replayed twice: consumer state remains unchanged after the second application.
- Wrong merge reversed: crosswalk and downstream consumers reconcile to the corrected entity state.

## 10. Expected deliverables and templates

### 10.1 Reference-data inventory and mapping package

| List ID | Definition | Owner | Steward | Authority | Version | Effective period | Consumer | Change process | Quality rule |
|---|---|---|---|---|---|---|---|---|---|
| `REF-...` | — | — | — | — | — | — | — | — | — |

Mapping detail should include source system/list/code/version, canonical list/code/version, effective period, mapping type (exact, approved equivalent, lossy, unmapped), approval, rationale, tests, and migration plan. Report mapping coverage with explicit population and distinct-code denominator.

### 10.2 Identifier policy template

- **Entity types in scope:**
- **Identifier types and semantics:**
- **Issuing authority and decision rights:**
- **Namespace syntax/components:**
- **Uniqueness scope and collision handling:**
- **Natural/business identifiers permitted:**
- **Surrogate/enterprise identifier strategy:**
- **Non-reuse and source-ID reuse controls:**
- **Issue, activate, change, alias, merge, split/unmerge, retire states:**
- **Crosswalk cardinality and effective-date rules:**
- **Redirect and downstream compatibility behavior:**
- **Privacy, access, retention, audit requirements:**
- **Reconciliation, monitoring, rollback, and owner:**

### 10.3 Matching design and evaluation package

- Entity definition and use-case-specific error costs.
- Permitted fields, provenance, data classification, and minimization rationale.
- Normalization rules and known information loss.
- Deterministic rules, probabilistic features, contradictions, and missing-value behavior.
- Candidate-generation/blocking passes, reduction ratio, and pair completeness.
- Threshold bands, hard overrides, review workflow, and review capacity.
- Label protocol, label quality, sampling design, train/validation/test separation.
- Confusion matrix and precision/recall/F1/FPR with denominators.
- Error analysis, uncertainty, cohort results, and known limitations.
- Rule/model version, deployment, rollback, drift monitoring, and re-evaluation cadence.

### 10.4 Steward review workflow

A minimal state machine is `CANDIDATE → AUTO_MATCH_ELIGIBLE | REVIEW_REQUIRED | NON_MATCH | UNRESOLVED`. `AUTO_MATCH_ELIGIBLE` must still pass hard constraints and deployment controls before a link is committed. Review outcomes should include `CONFIRMED_MATCH`, `CONFIRMED_NON_MATCH`, `INSUFFICIENT_EVIDENCE`, and `ESCALATED`. Store who decided, when, evidence references, rationale, policy version, and whether the decision was later reversed. Do not treat reviewer decisions as infallible; sample them and resolve disagreement.

### 10.5 Architecture decision record checklist

- Context and business outcome.
- Entity scope and source inventory.
- Options considered and rejected, with trade-offs.
- Identifier and reference-data design.
- Matching strategy, blocking, features, thresholds, and overrides.
- Measured evaluation and assumptions.
- Privacy/security/fairness controls.
- Operational mode, throughput/latency, review capacity, and cost.
- Merge/unmerge, replay, idempotency, reconciliation, and downstream impact.
- Monitoring, ownership, rollback, review date, and conditions for revisiting.

## 11. Common mistakes and misconceptions

| Mistake | Why it fails | Better practice |
|---|---|---|
| Treating a code as self-explanatory | Same code can mean different things in different lists or versions | Store list identity, version, meaning, and effective period |
| Overwriting reference codes | Historical meaning changes silently | Version lists and preserve effective-dated mappings |
| Mapping unknown values to a default | Conceals source defects and changes meaning | Quarantine, approve a mapping, or document an exception |
| Using names/emails as universal IDs | Not unique or stable | Govern identifier scope and use stable IDs with crosswalks |
| Reusing retired IDs | Corrupts history and delayed events | Non-reuse policy and time-bounded source assignments |
| Treating source ID as globally unique | Different systems can issue the same value | Include issuer, entity type, and validity scope |
| Treating match score as truth | Scores can be uncalibrated and evidence correlated | Validate labels, thresholds, hard constraints, and review bands |
| Comparing every possible pair | Computationally expensive | Block, measure pair completeness, use multiple passes |
| Measuring only accuracy | Class imbalance can hide false merges or misses | Precision, recall, FPR, costs, and cohort/error analysis |
| Ignoring pairs lost by blocking | Matcher cannot recover pairs it never sees | Measure pair completeness and audit missed-match pathways |
| Assuming A~B and B~C means A=C | Transitive chains can merge distinct entities | Cluster-level constraints and bridge-record review |
| One survivorship rule for every field | Source authority differs by attribute and purpose | Topic 06 attribute-level rules and provenance |
| Irreversible merge | Errors become hard to repair | Preserve source records, decisions, aliases, and unmerge paths |
| Logging raw personal attributes | Expands exposure and retention risk | Minimize evidence, control access, and log references safely |
| Ignoring drift and review capacity | Quality decays or queues become unmanageable | Monitor outcomes, re-evaluate, and size steward capacity |
| Treating labels as perfect ground truth | Labelers can disagree or have incomplete evidence | Record provenance, adjudicate conflicts, quantify uncertainty |

## 12. Mastery criteria and completion gate

### 12.1 Mastery criteria (roadmap-aligned)

You can:

- Distinguish entity resolution, identifier assignment, reference data, and master data maintenance.
- Design candidate generation/blocking and threshold bands, then compute precision and recall correctly.
- Define identifier lifecycle and reference-data versioning with non-reuse and merge handling.
- Explain deterministic versus probabilistic approaches, their trade-offs, and uncertainty.
- Show why matching score is not certainty and how manual review reduces selected risks.

### 12.2 Completion gate

- [ ] Matching design and evaluation have been reviewed; a reviewer can reproduce all metrics from labelled synthetic pairs.
- [ ] Reference-data inventory includes owner, versioning, effective dates, mappings, approvals, and historical interpretation.
- [ ] Identifier policy defines namespace, uniqueness scope, issuance, non-reuse, retirement, merge/split handling, and crosswalk rules.
- [ ] Review bands and false-match harm are discussed with explicit business assumptions.
- [ ] Blocking reduction and pair completeness are measured; missed candidates are addressed.
- [ ] Privacy, minimization, access, bias, retention, and auditability are included.
- [ ] Wrong-merge recovery, identifier-change propagation, idempotency, and reconciliation are defined.
- [ ] The design distinguishes matching from Topic 06 survivorship and golden-record construction.
- [ ] Known limitations, sampling limitations, drift triggers, and rollback are documented.
- [ ] Weakness “score = truth” is addressed by validated thresholds, review bands, and a correction path.

Reading the topic is not completion. The evidence is the reviewed deliverable package and reproducible calculations.

## 13. Revision checklist

Use this checklist after implementation changes or a matching-policy review.

- [ ] Entity definition and business purpose are still correct.
- [ ] Reference list owners, versions, mappings, and effective dates are current.
- [ ] Unknown/deprecated values are handled explicitly, not silently defaulted.
- [ ] Identifier namespaces and uniqueness constraints match actual source behavior.
- [ ] Reuse, merge, unmerge, split, redirect, and retirement paths are tested.
- [ ] Normalization retains originals and has documented language/domain limitations.
- [ ] Blocking pair completeness and reduction ratio are measured on representative labelled data.
- [ ] Scoring features, missingness, correlated evidence, contradictions, and threshold precedence are documented.
- [ ] Precision, recall, F1, FPR, and cost calculations use correct denominators and populations.
- [ ] Label quality, sampling design, uncertainty, and cohort performance are reviewed.
- [ ] Human review has capacity, training, escalation, audit, and correction processes.
- [ ] Sensitive fields are minimized; access, retention, logs, and derived links are governed.
- [ ] Monitoring detects drift, reversals, review backlog, unmapped codes, and propagation failures.
- [ ] Model/rule version, evaluation sample, decision records, and ADR are reproducible.
- [ ] Topic 04 quality rules and Topic 06 golden-record/provenance/synchronization requirements remain consistent.

## 14. Quick self-test

1. Why are reference data and master data different, even if both are governed?
2. Why must `source_system + source_id` sometimes include a validity period or generation?
3. What is the difference between precision and recall? State both denominators.
4. Why can a blocking strategy have excellent reduction ratio but unacceptable quality?
5. Why can a high pair score still be insufficient to auto-merge?
6. What must be preserved to support an auditable unmerge?
7. Why should reference-code changes be effective-dated and versioned?
8. How do you measure mapping coverage, and what exactly is its denominator?
9. Why is survivorship a separate decision from entity resolution?
10. Which privacy and bias risks arise when linking personal records?

A satisfactory answer explains the decision, denominator or evidence, failure mode, and operational control—not merely a definition.

## 15. Summary

Reference data gives systems shared, governed meanings for codes. Identifier architecture provides stable, scoped names for entities and preserves relationships across systems and time. Entity resolution evaluates whether records describe the same entity using normalization, candidate generation, evidence comparison, scoring, thresholds, and review. MDM then governs the resulting entity representation and attribute survivorship.

Build these as related but distinct capabilities. Version code lists, preserve source identifiers and crosswalk history, prevent identifier reuse, evaluate matching on labelled and representative data, measure both precision and recall, quantify the consequences of false matches and missed matches, and design for privacy, review, drift, and reversible correction. No score guarantees identity; trustworthy resolution depends on definitions, evidence, governance, measured error, and recoverable operations.
