# Master Data Management and Entity Resolution

**Roadmap location:** Stage 2C — Data Engineering_3 / `08-Data-Platform-Architecture-and-Data-Products/`  
**Target:** `04-master-data-management-and-entity-resolution.md`  
**Practical project:** `experiments/04_entity_resolution/`  
**Level:** Beginner → Advanced

> **Syllabus alignment:** This lesson follows Topic 04 in `roadmap-Data-Platform-Architecture-and-Data-Products.md`. The project tree confirms the target lesson path. The roadmap's required sequence is: master-data fundamentals and MDM styles; standardise/clean → block → compare → classify → cluster → survivorship; deterministic versus probabilistic matching; similarity methods and blocking; evaluation and review; stable master IDs and operations; hierarchies, graph relationships, and privacy.

## 1. Learning objectives

By the end, you should be able to:

1. Distinguish master, transactional, and reference data and explain why duplicate identities distort business reporting.
2. Compare registry, consolidation, coexistence, and centralised MDM architectures.
3. Design and validate each stage of an entity-resolution pipeline.
4. Apply exact rules, similarity features, candidate generation, and a probabilistic decision framework.
5. Explain Fellegi–Sunter weights, match/non-match thresholds, and the uncertain region.
6. Evaluate matching on labelled pairs using precision, recall, and F1 while separately measuring blocking recall.
7. Construct a golden record with field-level survivorship and traceable provenance.
8. Maintain cross-reference mappings and stable master IDs through incremental updates, merges, splits, and reversals.
9. Operate review queues, stewardship, audit, privacy, deletion, and reproducible model releases.
10. Run the educational lab and interpret the real output without treating a small synthetic score as a production benchmark.

---

## 2. Prerequisites and terminology

### 2.1 Prerequisites

Helpful foundations are SQL, Python, relational keys, data quality, source-system integration, and basic classification metrics. The core lab runs on Python 3.10+ and the standard library. `rapidfuzz` is optional. Splink with DuckDB is an optional extension.

### 2.2 Essential terminology

| Term | Meaning |
|---|---|
| **Entity** | A real-world thing the organisation cares about: a person, product, supplier, location, or legal organisation. |
| **Record** | A source-system representation of an entity. One entity may have many records. |
| **Identity resolution / entity resolution** | Deciding which records refer to the same entity, and which do not. |
| **Record linkage** | Matching records across datasets; often used interchangeably with entity resolution, though entity resolution can also include within-source deduplication and cluster management. |
| **Duplicate** | Two or more records that represent the same real-world entity under the chosen business definition. |
| **Golden record / master record** | A governed consolidated view of selected attributes and their provenance for an entity. It is not automatically the perfect or universally authoritative truth. |
| **Cross-reference (xref)** | Mapping from a source record/key to a persistent master ID. |
| **Candidate pair** | A pair selected for comparison by blocking or indexing. |
| **Blocking / indexing** | Reducing pair comparisons by generating plausible candidates. |
| **Survivorship** | Choosing the field values and provenance that appear in the golden record. |
| **Stewardship** | Human governance for ambiguous matches, merges, splits, exceptions, and quality disputes. |
| **False merge** | Different real entities incorrectly combined. Often high-impact and difficult to unwind. |
| **False split** | One real entity represented by multiple master identities. |
| **m probability** | In Fellegi–Sunter, probability of an observed comparison outcome among true matches. |
| **u probability** | Probability of that comparison outcome among non-matches. |
| **Match weight** | Evidence contribution, commonly \(\log_2(m/u)\) for a comparison outcome. |

A record match is a business assertion, not just a string-similarity result. A high string score can be misleading for common names, shared household phone numbers, recycled email addresses, or data-entry errors.

---

## 3. Master data and MDM fundamentals

### 3.1 Master, transactional, and reference data

| Data class | What it describes | Examples | Typical characteristics |
|---|---|---|---|
| **Master data** | Core business entities reused across processes | Customer, product, supplier, location, legal entity | Relatively stable identity and descriptive attributes; shared across systems |
| **Transactional data** | Events or business activity | Order, payment, shipment, invoice, click | High volume; time-ordered; references master entities |
| **Reference data** | Controlled code sets and classifications | Currency code, country code, order-status enum, product category | Governed vocabulary; often low volume and versioned |

These categories overlap in lifecycle, but they serve different purposes. A customer master record may be referenced by thousands of orders; the orders are not themselves master data. A country code list is reference data, while a specific delivery address may be part of a location master.

### 3.2 The identity problem

The same customer can appear in a CRM, web account system, billing system, call-centre application, and loyalty platform with:
- Different source IDs.
- Spelling variants (`Rahul Banerjee` versus `Rahul Bannerjee`).
- Different name formats (`A. Sharma` versus `Ananya Sharma`).
- Missing email or phone values.
- Old versus current addresses.
- Conflicting dates or stale contact details.
- Shared or recycled identifiers.
- Inconsistent formats and local conventions.

If the organisation counts each record as a distinct customer, customer counts inflate, lifetime value fragments, communications may be duplicated, fraud patterns are missed, and consent or deletion requests may not propagate correctly.

### 3.3 What MDM does

**Master Data Management (MDM)** establishes the operating model, processes, technology, identity policies, and governance needed to create and maintain trusted master identities and attributes.

An MDM capability usually includes:
- Source ingestion and standardisation.
- Identity matching and duplicate detection.
- Golden-record construction and provenance.
- Source-to-master cross-reference mappings.
- Steward review, merge/split and exception workflows.
- Publishing master data to consuming systems.
- Audit, privacy, retention, and correction processes.

MDM is not synonymous with a single database or a fuzzy-matching model. A model can propose likely matches; MDM determines who may approve them, how identity is represented, which values survive, and how changes are propagated.

### 3.4 Golden record: purpose and limitations

A golden record is a governed best-available representation for a defined purpose. It may combine:
- Name from a source considered authoritative for legal identity.
- Email from the most recent verified contact event.
- Address from a trusted address-management system.
- Date of birth from a validated source.
- Consent status from the designated consent authority.

There is rarely one source that is best for every field. A golden record can still be wrong because source data is wrong, the match model made an error, the survivorship policy is inappropriate, or a value is stale. Preserve field-level provenance, source timestamps, rule/model version, and the ability to correct or reverse a decision.

---

## 4. MDM architecture styles

The four styles describe how master data is represented, controlled, and propagated. Real platforms often combine them by domain or maturity stage.

| Style | Identity/master data location | Source-system impact | Latency and consistency | Strengths | Trade-offs / best fit |
|---|---|---|---|---|---|
| **Registry** | Central index stores master IDs and links to source records; source attributes may remain in place | Low to moderate | Reads may federate to sources; source outages and latency can affect views | Fastest path to cross-system identity without copying all data | Harder to provide a fully self-contained golden record; source systems remain dependencies |
| **Consolidation** | Central analytical/master store copies and resolves source data; source systems remain systems of entry | Usually low | Central view updated by batch or streaming ingestion | Strong for analytics, reporting, and customer-360 views | Changes may be delayed; central store may not write back corrections |
| **Coexistence** | Central hub and source applications both maintain data, with synchronisation and agreed ownership | Moderate to high | Depends on sync topology and conflict rules | Supports operational and analytical uses with shared governance | Conflict resolution and bidirectional synchronisation are complex |
| **Centralised** | Central MDM is the authoritative create/update point for mastered entities | High | Can provide stronger central consistency if all writes go through the hub | Clear authority, strong controls, fewer conflicting write paths | Highest organisational and integration effort; source applications may need redesign |

### 4.1 How to choose

- Choose **registry** when source ownership must remain local and a cross-reference is the main requirement.
- Choose **consolidation** when the immediate goal is analytical identity resolution and source systems should not be changed.
- Choose **coexistence** when both central governance and source-local operations need to maintain data, and the organisation can implement conflict rules.
- Choose **centralised** when operational processes can reliably create/update master entities through one authority and the business requires tight control.

Consider ownership, data latency, consistency requirements, source-system change cost, write-back needs, scale, steward capacity, and the cost of identity mistakes. Avoid choosing the most centralised architecture merely because it sounds more controlled.

---

## 5. Entity-resolution pipeline

The roadmap's order is:

`Standardise/Clean → Block → Compare → Classify → Cluster → Survivorship`

Each stage has a separate purpose and should be observable.

<CodeBlock language="mermaid">
flowchart LR
    A[Source records] --> B[Standardise / clean]
    B --> C[Block / candidate generation]
    C --> D[Compare fields]
    D --> E[Classify: match / non-match / review]
    E --> F[Cluster accepted matches]
    F --> G[Survivorship and golden record]
    G --> H[Master IDs and cross-reference]
    E --> R[Human review queue]
    R -->|Approved match / rejection| F
    R -->|Need more evidence| X[Hold and investigate]
    H --> AU[Audit and publish]
</CodeBlock>

### 5.1 Standardise / clean

**Input:** source records and source metadata.  
**Work:** trim whitespace, normalise Unicode, case-fold text, standardise phone/address/date formats, map source-specific codes, preserve raw values, mark missing/invalid values, and apply field-specific normalisation.  
**Output:** canonical comparison fields plus original values and data-quality flags.  
**Failure modes:** destroying meaningful distinctions, removing accents incorrectly, confusing null with empty string, losing country codes, or overwriting the original source value.  
**Validation:** before/after distributions, null rates, parse failures, sample review, and reversible transformations.

Do not blindly normalise every field the same way. Names, phone numbers, addresses, email addresses, and identifiers have different semantics. Retain raw data and record the normalisation version.

### 5.2 Block / candidate generation

**Input:** standardised records.  
**Work:** select plausible pairs using one or more blocking rules.  
**Output:** a deduplicated set of candidate pairs.  
**Failure modes:** overly broad blocks produce too many comparisons; overly narrow blocks miss true matches.  
**Validation:** candidate count, reduction ratio, block-size distribution, and blocking recall against labelled truth.

Blocking is a recall gate: if a true pair never becomes a candidate, later scoring cannot recover it. Multi-pass blocking unions candidates from different rules, such as exact email, exact phone, postcode plus surname, or sorted-neighbourhood name keys.

### 5.3 Compare

**Input:** candidate pair.  
**Work:** compute field-level agreements and similarities, including missingness.  
**Output:** comparison vector, for example `email_exact=1`, `phone_exact=1`, `name_similarity=0.92`, `dob_exact=0`.  
**Failure modes:** treating missing-vs-missing as strong agreement, ignoring identifier reliability, or comparing inconsistent representations.  
**Validation:** inspect distributions for known matches and non-matches; verify feature direction and range.

### 5.4 Classify

**Input:** comparison vector and model/rules.  
**Work:** label pair as match, non-match, or uncertain/review.  
**Output:** decision, score/probability, model version, reason codes, and threshold policy.  
**Failure modes:** arbitrary thresholds, uncalibrated probabilities, ignoring class imbalance, or silently converting uncertain pairs to matches.  
**Validation:** labelled-pair precision/recall/F1, threshold curves, subgroup checks, and review outcomes.

### 5.5 Cluster

**Input:** accepted pair edges.  
**Work:** form groups of records that are asserted to represent one entity.  
**Output:** entity clusters and their membership.  
**Failure modes:** transitive over-merging. If A matches B and B matches C, a connected-component algorithm puts A, B, and C together even when A and C conflict.  
**Validation:** cluster-size distribution, within-cluster contradictions, bridge-edge checks, duplicate source-key constraints, and steward approval for risky merges.

A pair classifier is not automatically a safe clustering algorithm. Add cluster-level constraints and review workflows for high-impact domains.

### 5.6 Survivorship

**Input:** approved cluster, source priorities, field-specific rules, and provenance.  
**Work:** select each field value according to an explicit policy.  
**Output:** golden record, per-field source lineage, and the rule/model version used.  
**Failure modes:** one global source priority for every field, choosing the latest but unverified value, or overwriting consent based on recency.  
**Validation:** compare with authoritative sources, audit field provenance, measure missingness, and test deterministic repeatability.

---

## 6. Normalisation and similarity methods

### 6.1 Normalisation examples

| Field | Useful operations | Important caution |
|---|---|---|
| Name | Unicode normalisation, case-folding, punctuation/whitespace normalisation, tokenisation, optional phonetic key | Initials, transliteration, compound surnames, and culturally specific name order need care |
| Address | Standardise common street suffixes, parse unit/street/city/postcode, normalise postcode | Do not collapse apartment/unit numbers or treat a shared building as a person identity |
| Phone | Parse country code, remove formatting, validate length and region, store canonical E.164 where possible | The lab assumes an India-centric default country code for 10-digit numbers; numbers can be shared or recycled |
| Email | Trim whitespace and case-fold for this lab while preserving punctuation; apply a documented domain/local-part policy in production | Provider-specific dot/plus rules must not be assumed universal |
| Date | Parse to a consistent date representation and timezone where relevant | Date-of-birth errors and ambiguous day/month formats can create false matches |
| Identifier | Preserve issuer/source namespace and canonical format | `12345` in CRM is not necessarily the same ID as `12345` in billing |

### 6.2 Similarity measures

- **Levenshtein distance:** minimum insertions, deletions, and substitutions needed to transform one string into another. Often normalised to a similarity score. Useful for typographical variation; can be expensive if applied to all pairs.
- **Jaro–Winkler:** character-based similarity with a prefix boost; often useful for names, but not universally superior and can overvalue shared prefixes.
- **Token-based similarity:** compares word tokens, e.g. token-sort or token-set ratio. Useful for reordered words; token-set similarity can overstate similarity when one string has extra meaningful tokens.
- **Soundex / Metaphone:** phonetic encodings that group similar-sounding names. Useful for candidate generation, especially for English-oriented names; language and transliteration limitations matter.
- **Numeric tolerance:** compare numeric values within a domain-specific tolerance. For example, a measurement might match within ±0.1; customer age is not a stable identity feature.
- **Date tolerance:** compare dates exactly or within a justified tolerance when source semantics permit. Do not casually tolerate different dates of birth.
- **Geographic/address similarity:** compare parsed components, postcode, geocodes, or distance. A shared address is often supporting evidence, not proof that two people are identical.

The lab uses RapidFuzz's `WRatio` if installed and Python's `SequenceMatcher` as a fallback. This keeps the core example runnable, but the fallback is not claimed to be numerically identical to RapidFuzz. The teaching normaliser also reduces text to ASCII Latin characters; that can destroy information in multilingual names and is not suitable as a production normalisation policy. For production, preserve raw values, use locale-aware transformations, pin library versions, and evaluate the chosen measure on representative data.

### 6.3 Similarity is evidence, not identity

A name score of 0.95 is not a 95% probability that two records are the same person. Similarity is a feature. Probability requires a model and calibration against the population and candidate-generation process. Exact phone agreement can be strong evidence in one business domain and weak evidence in another if phone numbers are shared or recycled.

---

## 7. Deterministic and probabilistic matching

### 7.1 Deterministic rules

A deterministic rule might say:

- Match if a verified government/customer identifier agrees exactly.
- Otherwise match if email and date of birth agree and the name is compatible.
- Otherwise match if phone, date of birth, and postcode agree.
- Send conflicts or incomplete evidence to review.

**Advantages:** explainable, testable, stable, often high precision when identifiers are reliable.  
**Limitations:** brittle to missing or dirty fields; rule proliferation; may have low recall for messy records.

A source-specific ID only identifies a record within its namespace. Compare `(source_system, source_id)` for uniqueness; never assume a CRM key equals a billing key.

### 7.2 Probabilistic matching

Probabilistic matching combines multiple comparison outcomes into a score or probability. It is useful when no single identifier is reliable and records contain typos or missing attributes.

#### Fellegi–Sunter intuition

For a comparison outcome \(\gamma\), define:

- \(m(\gamma)=P(\gamma \mid M)\): probability of observing that outcome among true matches.
- \(u(\gamma)=P(\gamma \mid U)\): probability of observing that outcome among non-matches.
- Weight \(w(\gamma)=\log_2\left(\frac{m(\gamma)}{u(\gamma)}\right)\).

If two records agree on a rare, reliable identifier, the agreement may be much more common among true matches than non-matches, so its weight is high. Agreement on a common surname may have much less weight. Disagreement on a reliable field can contribute negative evidence.

Under a simplifying conditional-independence assumption, field weights can be summed. Real fields are often correlated (email and name embedded in email, postcode and address, etc.), so model assumptions and calibration need testing. Missingness should usually be modelled explicitly or handled as an informative comparison level rather than counted as agreement.

The lab's transparent score is **Fellegi–Sunter-inspired**, but its weights are hand-configured teaching constants. It does not estimate \(m\) and \(u\), and its score is not a calibrated probability. The optional Splink path demonstrates a library-based model workflow when installed.

### 7.3 Three-way threshold policy

For a score \(s\) with lower and upper thresholds \(L\) and \(H\):

- \(s \ge H\): accept as match only if the operational risk policy permits automatic merges.
- \(L \le s < H\): uncertain; place in the clerical review queue.
- \(s < L\): treat as non-match for this run.

Thresholds are selected from labelled data, error costs, and steward capacity—not from a universal value. In some high-risk domains, even high scores require approval. A score below threshold means “not auto-matched under this policy,” not necessarily “definitely different.”

### 7.4 False-merge and false-split trade-offs

| Outcome | Meaning | Typical cost |
|---|---|---|
| False merge | Different people/products/suppliers combined | Cross-customer data leakage, wrong consent handling, corrupted history, operational harm |
| False split | Same entity remains as multiple masters | Inflated counts, fragmented history, duplicate outreach, incomplete customer view |
| Review | Model defers decision | Steward time and latency, but safer for ambiguous evidence |

For a privacy-sensitive customer profile, a false merge may be far more expensive than a false split. For product catalogue deduplication, the cost profile may differ. Set thresholds from explicit loss and risk analysis.

---

## 8. Blocking and candidate generation

### 8.1 Why all-pairs matching fails

For \(n\) records, the number of unique within-dataset pairs is:

\[
\binom{n}{2} = \frac{n(n-1)}{2}
\]

For \(n=10{,}000{,}000\):

\[
\frac{10{,}000{,}000 \times 9{,}999{,}999}{2}
= 49{,}999{,}995{,}000{,}000
\]

That is approximately **50 trillion unique pairs** before string comparisons, feature construction, model scoring, and storage. The computational and operational costs are usually prohibitive. For scale intuition only, a hypothetical 99.9% reduction would still leave about 49,999,995,000 (roughly 50 billion) candidate pairs. That 99.9% reduction is an assumption, not a measured property of this lab; actual candidate counts depend on block sizes and overlap, and must be measured on representative data.

### 8.2 Blocking patterns

- Exact normalised email.
- Exact canonical phone.
- Postcode plus surname/phonetic surname.
- Birth year plus name prefix.
- Sorted-neighbourhood indexing on a key.
- Geographic region plus name token.
- Multiple passes whose candidate sets are unioned and deduplicated.

Blocking must balance reduction and recall. A block on exact email is cheap but misses records with changed/missing email. A broad postcode block can be huge. Multi-pass blocking improves coverage but can increase candidate volume and false candidates.

### 8.3 Measure blocking independently

\[
\text{Blocking recall} =
\frac{\text{true-match pairs generated as candidates}}
{\text{all true-match pairs in labelled truth}}
\]

\[
\text{Reduction ratio} =
1 - \frac{\text{candidate pairs}}{\text{all possible pairs}}
\]

Report both. A model can have excellent precision among candidates while missing many true pairs that blocking never generated. Candidate recall should be measured on a labelled sample and monitored when source distributions change.

The lab uses a union of exact email, exact phone, and postcode-plus-surname blocks. On the included small synthetic data, it generates 13 pairs from 210 possible pairs and includes all 11 ground-truth match pairs. This is a **measured result for this fixture only**, not a benchmark or a guarantee for other data.

---

## 9. Evaluation and threshold selection

### 9.1 Labelled pairs

Create a ground-truth set with:
- Confirmed matches.
- Confirmed non-matches.
- Difficult borderline cases.
- Representative source pairs and data-quality segments.
- Provenance of the label and adjudication process.

Split training, tuning, and evaluation data carefully. Random pair splits can leak records or entities across sets; prefer entity-aware splits where appropriate. Avoid evaluating only easy candidate pairs.

### 9.2 Metrics

Let:
- TP = predicted match and truly a match.
- FP = predicted match but actually different entities.
- FN = true match not accepted as a match.
- TN = predicted non-match and truly different entities.

\[
\text{Precision} = \frac{TP}{TP+FP}
\qquad
\text{Recall} = \frac{TP}{TP+FN}
\]

\[
F_1 = 2\cdot\frac{\text{Precision}\cdot\text{Recall}}
{\text{Precision}+\text{Recall}}
\]

Precision answers “of auto-matches, how many are correct?” Recall answers “of true matches, how many did we accept?” F1 balances both but does not encode business costs. Use precision-recall curves and expected cost when false merges and false splits have asymmetric impact.

### 9.3 Lab evaluation scope

The lab computes metrics on **candidate pairs** and reports blocking recall separately. In the report, `false_negatives_within_candidates` means true candidate pairs not automatically accepted; some may be in the review queue rather than definitively rejected. Do not interpret this as end-to-end recall without also accounting for blocking and adjudicated review outcomes.

### 9.4 Threshold tuning

1. Freeze a labelled evaluation set.
2. Score the same candidate pairs across a threshold grid.
3. Plot precision, recall, F1, review volume, and estimated error cost.
4. Choose the operating point based on the cost of false merges, false splits, and manual review.
5. Review error slices by source, language/script, missingness, geography, and entity type.
6. Re-evaluate after source changes, model changes, or blocking-rule changes.

The lab compares a conservative deterministic rule set with a configurable score threshold. The probabilistic score is intentionally not calibrated, so threshold results illustrate mechanics only.

### 9.5 Human review and active learning

A review queue should include:
- Source records and field-level comparison values.
- Match score/probability with an explanation.
- Reasons for disagreement and missing fields.
- Suggested action: merge, reject, request evidence, or defer.
- Reviewer identity, timestamp, reason code, and decision provenance.

**Active learning** prioritises uncertain or informative pairs for labels, then uses those labels to improve a trained model. Avoid training only on cases that humans happened to review: the sample can be biased toward difficult pairs. Retain random audit samples and measure model performance on independently adjudicated data.

---

## 10. Clustering, survivorship, and golden records

### 10.1 Pair decisions are not clusters

An accepted pair graph can be clustered using connected components or a clustering algorithm. But transitivity can amplify one false edge. If A matches B and B matches C, connected components merges all three even if A and C conflict. Production systems should apply cluster-level constraints, check contradictions, detect bridge edges, and require steward approval for risky merges.

The lab only uses pairs classified `match` as union edges; `review` edges do not directly merge clusters. The demonstration does not implement a complete enterprise cluster-conflict engine.

### 10.2 Field-level survivorship

A defensible survivorship policy is field-specific:

| Field | Example rule | Why |
|---|---|---|
| Legal name | Approved authoritative source priority, then recency | Name quality/authority may differ by source |
| Preferred display name | Most recently verified non-empty value | Reflects current preference |
| Email/phone | Latest verified value; retain verification timestamp | Recency without verification can choose a bad value |
| Postal address | Source priority plus effective date and verification | Address can change over time |
| Date of birth | Trusted/validated source; conflicts sent to review | Do not simply choose the longest or newest value |
| Consent | Designated consent authority and purpose-specific policy | Never infer permission from generic source priority |
| Product description | Product-domain authority or approved editorial source | Product data often has domain-specific ownership |

The lab's simplified rules are explicit in `resolver.py`: CRM source priority for name/postcode, most recent non-empty email/phone/address, and a date-of-birth tie-breaker based on the number of populated core attributes in each source record, followed by recency and source priority. This is a pedagogical proxy for record-level completeness, not proof that a DOB is correct. It records which source record supplied each value. Consent is not automatically resolved; conflicts are surfaced as a policy issue.

### 10.3 Cross-reference table

A typical cross-reference table is:

| source_system | source_record_id | master_id | valid_from | valid_to | decision_id |
|---|---|---|---|---|---|
| crm | C100 | M-000001 | 2026-01-05 | null | D-001 |
| web | W901 | M-000001 | 2026-02-10 | null | D-001 |
| billing | B551 | M-000001 | 2025-12-20 | null | D-001 |

The lab uses `record_id → master_id`; production should also capture source namespace, validity intervals, status, model/rule version, reviewer/decision ID, and merge/split history.

---

## 11. Stable IDs and incremental processing

### 11.1 Persistent master identity

A master ID is an identity key, not a row number or a hash of mutable attributes. Do not derive it from name/email/address: those fields change, and hashes can change with normalisation rules. Allocate a persistent ID when an entity is established and keep source-to-master mappings.

### 11.2 Incremental matching

When new records arrive:
1. Validate and standardise.
2. Match against existing master members and candidate indexes.
3. Auto-attach only when the evidence and cluster policy allow it.
4. Route ambiguous candidates to stewardship.
5. Allocate a new master ID only when no existing identity is sufficiently supported.
6. Update xref and golden record transactionally.
7. Record before/after state, decision, model version, and downstream publication status.

The lab adds `WEB-110` for an existing customer and `CRM-011` for a new customer. Its registry preserves all existing record-to-master assignments and attaches the known incremental record to the prior master ID. It allocates a new ID for the new entity.

### 11.3 Merges, splits, and reversals

- **Merge:** two masters are determined to represent one entity. Preserve both old IDs in the audit history; select a surviving/canonical ID by policy and maintain aliases/redirects. Do not erase the losing ID's history.
- **Split:** a prior cluster is found to contain different entities. Recompute memberships, issue/restore appropriate master IDs, repair xref mappings, and publish correction events downstream.
- **Reversal:** a steward or new evidence reverses a previous merge. Preserve the original decision and record a compensating decision rather than rewriting history.
- **Incremental reruns:** idempotent input processing and deterministic decision IDs prevent duplicate mappings or repeated ID allocation.

The core lab demonstrates stable assignment for a simple no-merge/no-split incremental case. If a component touches multiple existing master IDs, it preserves the old mappings and emits a stewardship conflict rather than silently merging identities. If one prior master ID now spans disconnected components, the largest component (with a deterministic tie-break) keeps the ID; other components receive new IDs and emit explicit split-review events. These are educational registry semantics, not a substitute for transactional master-data governance: production workflows must persist approvals, validity intervals, aliases, compensating events, and downstream corrections.

### 11.4 Reproducibility and audit

Persist:
- Raw source snapshot or immutable source reference.
- Normalisation version.
- Blocking rules and candidate generation version.
- Comparison feature definitions.
- Model/rule version and thresholds.
- Input dataset watermark/snapshot.
- Pair decisions and reason codes.
- Cluster memberships before/after.
- Survivorship policy version and field provenance.
- Reviewer, timestamp, and approval.
- Published events and downstream acknowledgement.

Without this, a later model rerun can change identity assignments without a clear explanation.

---

## 12. Operational governance, privacy, and auditability

### 12.1 Stewardship operating model

Define:
- Which decisions can auto-merge and which require review.
- Who can approve merges, splits, and overrides.
- Escalation for high-risk identity conflicts.
- Review queue priority, ageing, and service objectives.
- Appeals and correction workflow.
- Sampling/auditing of automated decisions.
- Model release approval and rollback.
- Source-owner responsibilities for poor data quality.

A high-impact false merge should have a clear rollback path, not just a ticket to “fix the data.”

### 12.2 PII and privacy controls

Entity resolution often processes names, emails, phone numbers, addresses, and dates of birth. Use:
- Purpose limitation and lawful basis/consent controls appropriate to jurisdiction.
- Least-privilege access, encryption in transit/at rest, audit logs, and secure secret handling.
- Minimise attributes used and retained; use synthetic or masked data in development.
- Segregate raw PII from derived match features and review exports.
- Restrict review queue access; avoid sending PII into public chat, logs, or general-purpose LLM prompts.
- Retention/deletion policies for source records, golden records, pair features, cached indexes, backups, and downstream copies.

### 12.3 Hashing is not automatic anonymisation

Hashing identifiers can reduce direct exposure but does not guarantee anonymity. Deterministic hashes of low-entropy values (phone numbers, emails) are vulnerable to dictionary attacks; plain unsalted hashes can be linkable across datasets. If privacy-preserving linkage is required, evaluate keyed HMACs, tokenisation, secret management, controlled linkage environments, or specialised privacy-preserving record linkage. These methods still need threat modelling and legal/security review.

### 12.4 Right-to-be-forgotten and derived data

Deletion is not just removing one source row. A governed workflow must identify:
- Source record and linked master identity.
- Whether other source records legitimately maintain the entity.
- Golden record attributes and derived features affected.
- Pairwise comparison tables, caches, embeddings, indexes, exports, and downstream consumers.
- Backups and retention exceptions.
- Audit evidence that can be retained without unlawfully retaining deleted PII.

Depending on the applicable legal basis and policy, an identity may need to be suppressed, de-linked, partially erased, or fully deleted. Do not blindly delete a master record if other valid records remain, and do not keep a hidden copy of erased PII in the audit trail. Retain only the minimum lawful evidence.

### 12.5 Hierarchies and graph relationships

Entity identity is not the same as a relationship:
- Two people in one household are related, not duplicates.
- A parent company and subsidiary are distinct legal entities with a hierarchy.
- A supplier and a brand may be related but not identical.
- A person may be associated with several addresses over time.

Represent relationships explicitly (household membership, parent/subsidiary, owns, supplied-by, located-at) with type, direction, effective dates, provenance, and confidence. Graph methods can help detect communities and inconsistent relationships, but graph proximity is not proof of identity. Avoid merging all nodes in a connected graph component.

---

## 13. Tools and build-versus-buy considerations

### 13.1 Tool roles

| Tool | Main role | Strengths | Considerations |
|---|---|---|---|
| **Splink** | Probabilistic record linkage using SQL backends such as DuckDB and Spark | Fellegi–Sunter-style modelling, comparison levels, blocking, parameter estimation, scalable SQL execution | Needs domain-appropriate settings, blocking, model diagnostics, and evaluation; API differs across versions |
| **`recordlinkage`** | Python toolkit for indexing, comparison, classification, and evaluation | Flexible research/engineering toolkit; supports blocking and sorted-neighbourhood indexing and several classifiers | pandas-oriented; assess scale and memory for large candidate sets |
| **`dedupe`** | Learning-based fuzzy matching/deduplication with human-labelled training examples | Useful when domain experts can label pairs and the model should learn comparison behavior | Training workflow and production integration need design; not a drop-in MDM governance platform |
| **`rapidfuzz`** | Fast string similarity/distance calculations | Levenshtein, Jaro/Jaro–Winkler, token metrics, extraction utilities | Similarity library, not a complete ER pipeline or trained match model |
| **DuckDB** | Local analytical SQL engine and Splink backend | Useful for local development and many medium/large linkage jobs | Workload size, RAM, candidate volume, and query plans still matter |
| **Spark** | Distributed execution backend for large linkage workloads | Cluster-scale processing and integration with data platforms | Operational complexity, shuffle cost, and model/blocking quality still matter |

These tools are not interchangeable. RapidFuzz scores strings; `recordlinkage` assembles a pipeline; `dedupe` learns from labels; Splink provides probabilistic linkage with SQL execution. None by itself replaces stewardship, stable ID management, survivorship policy, privacy, and publication workflows.

### 13.2 ML, embeddings, and LLM assistance

- **Supervised pair models** learn from labelled match/non-match pairs. They can outperform hand rules when labels are representative and the feature/model lifecycle is managed.
- **Embeddings** can retrieve semantically or linguistically similar records and help candidate generation, especially with multilingual text. Semantic similarity can confuse related but distinct entities; use structured evidence and evaluation.
- **LLM-assisted matching** can explain a pair, extract fields from unstructured records, or assist human reviewers. LLM output is not deterministic identity truth. Protect PII, constrain prompts, require structured outputs, audit versions, and never auto-merge solely because an LLM says “same person.”
- **Human-in-the-loop** review is a control, not a failure. High-risk uncertain pairs should remain unresolved until evidence or approval is available.

### 13.3 Commercial MDM products versus open source

Products such as Informatica MDM, Reltio, Profisee, and Semarchy provide commercial MDM capabilities whose scope varies by edition and deployment: data models, match/merge configuration, survivorship, stewardship UIs, workflow, integration, and governance. Open-source libraries can provide matching algorithms and flexible pipelines but generally require the team to build more of the surrounding operating system: persistent IDs, steward UX, audit, lifecycle management, access controls, and integration.

Build-versus-buy criteria:
- Number and complexity of domains.
- Operational versus analytical mastering needs.
- Existing enterprise platform and identity/access standards.
- Stewardship workflow requirements.
- Explainability and audit requirements.
- Integration and change-management effort.
- PII governance and regional constraints.
- Total cost of ownership, vendor lock-in, skills, support, and scale.

Do not compare a library's licence cost with a vendor's subscription alone. Compare the total cost of the complete capability and its operational risk.

---

## 14. Hands-on implementation

### 14.1 Project layout

```text
experiments/04_entity_resolution/
├── pyproject.toml
├── README.md
├── resolver.py
├── run_lab.py
├── splink_runner.py             # optional; not executed in this environment
├── data/
│   ├── source_records.json
│   └── incremental_records.json
├── reports/
│   └── run_report.json          # generated by run_lab.py
└── tests/
    └── test_resolver.py
```

The dataset is synthetic and includes source IDs, normalisation challenges, missing email, spelling variants, conflicting date of birth, and ground-truth entity labels. Ground truth is used only for evaluation; a production matcher must not use the label as a feature.

### 14.2 Setup and commands

Python 3.10+:

```bash
cd experiments/04_entity_resolution
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install -e ".[test]"
python run_lab.py
pytest -q
```

Optional RapidFuzz:

```bash
python -m pip install -e ".[fuzzy,test]"
```

Optional Splink + DuckDB extension:

```bash
python -m pip install -e ".[splink]"
python splink_runner.py
```

The optional Splink path uses the Splink 4 documented DuckDB registration pattern (`DuckDBAPI.register` followed by `Linker`) and is separate from the core lab. Splink and DuckDB were not installed in the execution environment used for the core lab, so the script was not run and its output is not claimed as verified. Consult the current Splink documentation and execute the optional path in a pinned environment before adopting it.

### 14.3 What the core lab does

1. Loads and standardises the synthetic customer records.
2. Generates candidates from exact email, exact phone, and postcode-plus-surname blocks.
3. Scores candidate pairs using an explicit deterministic rule and a configurable Fellegi–Sunter-inspired score.
4. Classifies pairs as match, non-match, or review.
5. Calculates candidate-level precision, recall, and F1, plus blocking recall.
6. Builds clusters from auto-match edges only.
7. Builds golden records with field-level provenance.
8. Creates a cross-reference map.
9. Runs incremental records and checks existing master IDs remain stable.
10. Writes `reports/run_report.json`.

### 14.4 Ten-record worked example

Consider these ten source records (abbreviated for readability):

| Record | Source | Name | Email | Phone ending | DOB | Postcode | Truth |
|---|---|---|---|---|---|---|---|
| CRM-001 | CRM | Ananya Sharma | ananya.sharma@… | 543210 | 1990-04-12 | 700016 | E1 |
| WEB-101 | Web | Ananya Sharma | same email, case variation | 543210 | 1990-04-12 | 700016 | E1 |
| BILL-201 | Billing | A. Sharma | missing | 543210 | 1990-04-12 | 700016 | E1 |
| CRM-002 | CRM | Rahul Banerjee | rahul.b@… | 456789 | 1985-11-03 | 700029 | E2 |
| WEB-102 | Web | Rahul Bannerjee | same email | 456789 | 1985-11-03 | 700029 | E2 |
| CRM-012 | CRM | Rahul Bannerjee | missing | 456789 | 1986-11-03 | 700029 | E11 |
| CRM-003 | CRM | Mira Das | mira.das@… | 001111 | 1992-07-21 | 700091 | E3 |
| BILL-203 | Billing | Meera Das | missing | 001111 | 1992-07-21 | 700091 | E3 |
| CRM-004 | CRM | Sanjay Roy | s.roy@… | 877777 | 1978-03-09 | 700156 | E4 |
| WEB-104 | Web | Sanjay Roy | same email | 877777 | 1978-03-09 | 700156 | E4 |

**Pair-by-pair reasoning**

- **CRM-001 ↔ WEB-101 — match:** email, phone, DOB, and postcode agree after normalisation; name agrees. Strong evidence.
- **CRM-001 ↔ BILL-201 — match:** billing lacks email and shortens the name, but phone, DOB, and postcode agree. Missing email is not a disagreement.
- **WEB-101 ↔ BILL-201 — match:** same corroborating phone/DOB/postcode evidence; name abbreviation is plausible.
- **CRM-002 ↔ WEB-102 — match:** exact normalised email, phone, DOB, postcode, and high name similarity despite a spelling variation.
- **CRM-002 ↔ CRM-012 — uncertain:** phone and postcode agree, but DOB conflicts and email is missing. The two records have very similar names, which can arise from a duplicate or a different person. The conservative threshold sends the pair to review rather than using it as an automatic cluster edge.
- **WEB-102 ↔ CRM-012 — uncertain for the same reason:** an exact-looking name and shared phone do not override the DOB conflict. Review requires evidence, not a guess.
- **CRM-003 ↔ BILL-203 — match candidate:** email is absent on billing, while phone, DOB, and postcode agree; the name variant is plausible. The system can accept this pair under the deterministic rule but a production policy might require review for higher-risk domains.
- **CRM-004 ↔ WEB-104 — match:** exact email, phone, DOB, postcode, and name agree.
- **CRM-001 ↔ CRM-002 — not a candidate:** they share no blocking key. This is not a scored non-match; blocking excluded it. A complete evaluation must count missed true pairs separately from classifier errors.

This example illustrates why a shared phone or a high name score alone is not proof. It also shows that **not generated** and **classified non-match** are different outcomes.

### 14.5 Survivorship result for E1

For the E1 cluster:
- Name: CRM-001 (`Ananya Sharma`) wins under CRM source priority.
- Email: WEB-101 wins under most-recent non-empty contact policy.
- Phone/address: latest non-empty source value wins in the simplified lab.
- DOB: most complete value, with recency as a tie-breaker.
- Provenance: every selected value records the source record ID and the rule used.
- Consent: values are surfaced as a set; the lab does not infer consent authority from source priority.

In production, email/phone should normally use verification status and source authority as well as recency. Consent requires a designated authoritative policy and purpose context.

### 14.6 Incremental run

`data/incremental_records.json` adds:
- `WEB-110`, which represents the existing Dev Patel entity.
- `CRM-011`, a new Tara Bose entity.

For this no-merge/no-split fixture, the registry preserves old record-to-master IDs, attaches `WEB-110` to the existing Dev Patel master, and allocates a new ID for Tara. Separate tests simulate a split and a proposed merge: a split-off component receives a distinct new ID plus a stewardship event, while a component that touches two existing master IDs keeps the old mappings and is flagged for review rather than silently merged.

---

## 15. Automated tests and expected results

### 15.1 What is tested

The 17 core tests verify:
- Reproducible dataset size, unique record IDs, and ground-truth entity count.
- Candidate generation reduces comparisons and preserves all known true pairs in this fixture.
- Deterministic matching, phone canonicalisation, email punctuation, and date normalisation.
- Precision/recall/F1 definitions, empty-denominator/unlabelled-pair behavior, and exact threshold boundaries.
- Ambiguous records are not auto-merged by review edges.
- Survivorship is deterministic and provenance is retained.
- Existing master IDs remain stable in a no-merge/no-split incremental run.
- Split handling assigns distinct IDs and emits a stewardship event.
- A proposed merge of two existing IDs is not silently applied.
- Invalid methods, thresholds, duplicate IDs, undefined blocking recall with no positive pairs, and the ten-million-record pair-count formula fail or calculate correctly.

### 15.2 Actual execution result

**Core implementation executed successfully.** In the available Python environment:

```text
17 passed
```

`python run_lab.py` reported:

```json
{
  "record_count": 21,
  "candidate_generation": {
    "record_count": 21,
    "labelled_record_count": 21,
    "unlabelled_record_count": 0,
    "all_possible_pairs": 210,
    "all_possible_labelled_pairs": 210,
    "all_ground_truth_match_pairs": 11,
    "candidate_true_pairs": 11,
    "blocking_recall": 1.0,
    "blocking_recall_defined": true,
    "candidate_pairs": 13,
    "reduction_ratio": 0.9381
  },
  "deterministic_metrics": {
    "candidate_pairs": 13,
    "labelled_candidate_pairs": 13,
    "unlabelled_candidate_pairs": 0,
    "candidate_ground_truth_match_pairs": 11,
    "predicted_matches": 11,
    "true_positives": 11,
    "false_positives": 0,
    "false_negatives_within_candidates": 0,
    "precision": 1.0,
    "recall_within_candidates": 1.0,
    "f1_within_candidates": 1.0,
    "precision_defined": true,
    "recall_defined": true,
    "f1_defined": true
  },
  "probabilistic_metrics": {
    "candidate_pairs": 13,
    "labelled_candidate_pairs": 13,
    "unlabelled_candidate_pairs": 0,
    "candidate_ground_truth_match_pairs": 11,
    "predicted_matches": 8,
    "true_positives": 8,
    "false_positives": 0,
    "false_negatives_within_candidates": 3,
    "precision": 1.0,
    "recall_within_candidates": 0.7273,
    "f1_within_candidates": 0.8421,
    "precision_defined": true,
    "recall_defined": true,
    "f1_defined": true
  },
  "review_queue_size": 5,
  "cluster_count": 13,
  "cross_reference_rows": 21,
  "report": "/mnt/data/experiments/04_entity_resolution/reports/run_report.json"
}
```

These are **actual results from the included synthetic fixture**, not benchmark results. The deterministic rules achieve perfect metrics on this small constructed candidate set; this does not establish generalisation. The conservative probabilistic-inspired threshold accepts fewer true pairs and leaves five pairs for review. Some deferred true pairs contribute to `false_negatives_within_candidates`, so the metric measures automatic acceptance, not final adjudicated resolution.

The optional Splink/DuckDB path was not executed because those packages were not installed. Its results are not included above.

### 15.3 Interpreting the result

- **Blocking:** 13 candidate pairs from 210 possible pairs (a reduction ratio of \(1 - 13/210 \approx 93.81\%\)); all 11 true match pairs are included in this small fixture.
- **Deterministic baseline:** accepts 11 true candidate pairs and no false candidate pairs for this dataset.
- **Probabilistic-inspired policy:** accepts 8 of 11 true pairs automatically; five pairs are deferred to review. The automatic-match precision is 1.0 on this fixture, but recall is lower.
- **Operational lesson:** a lower auto-match rate may be a valid choice when false merges are costly. Review capacity and the cost of unresolved identities must be measured too.

A small synthetic dataset is useful for checking code paths, not for estimating real-world match accuracy.

---

## 16. Common mistakes and misconceptions

1. Treating every repeated name as a duplicate.
2. Assuming source IDs are globally unique without source namespaces.
3. Treating missing-vs-missing fields as strong evidence.
4. Counting string similarity as match probability.
5. Using all-pairs comparison at large scale without candidate generation.
6. Measuring model recall but ignoring blocking recall.
7. Reporting only aggregate F1 when false merges have much higher cost than false splits.
8. Treating a review pair as a non-match or auto-match without recording the decision.
9. Clustering every connected component without checking transitive contradictions.
10. Using one source-priority order for all golden-record fields.
11. Recomputing master IDs from mutable attributes or row order.
12. Overwriting merge history instead of recording reversals and compensating events.
13. Treating hashing as anonymisation without a threat model.
14. Assuming graph proximity or household membership means identity.
15. Allowing an LLM to auto-merge identities without calibrated evidence and governance.
16. Evaluating only on easy labelled pairs or letting ground-truth labels leak into features.
17. Claiming optional integrations ran when their dependencies were unavailable.
18. Treating a successful test run on synthetic fixtures as production certification.

---

## 17. Practice questions with answers

### Q1. How does master data differ from transactional data?
**Answer:** Master data describes reusable core entities such as customers and products; transactional data records business events such as orders and payments that reference those entities.

### Q2. What is the difference between registry and consolidation MDM?
**Answer:** Registry primarily stores cross-system identity links while source attributes remain in source systems; consolidation copies and resolves data into a central view, usually without making that hub the operational write authority.

### Q3. Why can a golden record be wrong?
**Answer:** Source data may be wrong or stale, the match decision may be false, survivorship may select an inappropriate value, or policy may be incorrectly implemented. Provenance and reversibility are essential.

### Q4. Why does blocking affect recall?
**Answer:** Pairs excluded from candidate generation are never scored. A perfect classifier cannot recover a true pair it never sees.

### Q5. What are m and u in Fellegi–Sunter?
**Answer:** \(m\) is the probability of a comparison outcome among true matches; \(u\) is its probability among non-matches. The log ratio \(m/u\) measures how much the outcome supports a match.

### Q6. Why is exact phone agreement not always enough?
**Answer:** Phone numbers can be shared, recycled, or normalised incorrectly. They need corroborating evidence and a domain-appropriate reliability model.

### Q7. What is the difference between precision and recall?
**Answer:** Precision measures the correctness of accepted matches; recall measures the share of true matches accepted. Raising a threshold often increases precision while reducing recall, though actual curves depend on data and scoring.

### Q8. Why report blocking recall separately?
**Answer:** It separates candidate-generation misses from classification misses and shows whether the blocking strategy excludes genuine matches.

### Q9. Why can connected components be dangerous?
**Answer:** A single false-positive edge can join otherwise distinct clusters through transitivity. Cluster-level constraints and review are required for risky merges.

### Q10. What does survivorship decide?
**Answer:** Which source value is published for each golden-record field, using explicit field-level policies and retaining the selected value's provenance.

### Q11. How should master IDs behave when a cluster merges or splits?
**Answer:** Keep IDs persistent and preserve history. Select a canonical ID by policy on merge, record aliases/redirects, and use a governed split/reversal workflow with downstream correction events; do not silently rewrite the identity history.

### Q12. Why is a hash of an email not automatically anonymous?
**Answer:** Emails have a guessable space, so attackers can hash candidate emails and compare results. Deterministic hashes are also linkable. Use a threat model and appropriate controls such as keyed tokens/HMAC where suitable.

### Q13. What is active learning in entity resolution?
**Answer:** Selecting informative or uncertain pairs for human labels, then using the labels to improve the model. Evaluation still needs independent representative samples to avoid selection bias.

### Q14. What does the lab's score mean?
**Answer:** It is a hand-configured Fellegi–Sunter-inspired teaching score. It is not a trained or calibrated probability and must not be presented as one.

### Q15. Which tools serve different roles?
**Answer:** RapidFuzz computes string similarity; `recordlinkage` supplies indexing/comparison/classification components; `dedupe` learns from human labels; Splink implements probabilistic linkage with SQL backends. The complete MDM operating model remains a separate responsibility.

---

## 18. Completion checklist

- [ ] I can distinguish master, transactional, and reference data.
- [ ] I can compare registry, consolidation, coexistence, and centralised MDM.
- [ ] I can explain every stage from standardisation through survivorship.
- [ ] I can choose field-specific normalisation and similarity methods.
- [ ] I can distinguish deterministic rules, similarity scores, and calibrated probabilities.
- [ ] I can explain the Fellegi–Sunter m/u model and match-weight intuition.
- [ ] I can estimate all-pairs comparisons and design multi-pass blocking.
- [ ] I can measure blocking recall, precision, recall, and F1 separately.
- [ ] I can choose thresholds based on error costs and review capacity.
- [ ] I can explain transitive clustering risk and cluster-level controls.
- [ ] I can build a golden record with field-level provenance.
- [ ] I can maintain cross-reference mappings and stable master IDs.
- [ ] I can design merge, split, reversal, and incremental workflows.
- [ ] I can describe stewardship, audit, privacy, consent, and deletion propagation.
- [ ] I can distinguish the roles of Splink, `recordlinkage`, `dedupe`, and RapidFuzz.
- [ ] I can run the core lab and explain its limitations.

**Checkpoint:** You are ready to progress when you can defend the candidate-generation strategy, explain why every automatic match is accepted, account for every uncertain pair, reproduce the golden record, and show how master identity can be corrected without losing history.

---

## 19. Verified references and further reading

The module roadmap defines the syllabus. These official project/documentation sources were consulted for tool capabilities and current usage guidance:

- **Splink documentation — overview and probabilistic linkage:** https://moj-analytical-services.github.io/splink/  
- **Splink getting started:** https://moj-analytical-services.github.io/splink/getting_started.html  
- **Splink backend guide (DuckDB and Spark):** https://moj-analytical-services.github.io/splink/topic_guides/splink_fundamentals/backends/backends.html  
- **Python Record Linkage Toolkit documentation:** https://recordlinkage.readthedocs.io/en/stable/  
- **Record Linkage Toolkit indexing/blocking:** https://recordlinkage.readthedocs.io/en/stable/ref-index.html  
- **Record Linkage Toolkit classifiers:** https://recordlinkage.readthedocs.io/en/stable/ref-classifiers.html  
- **RapidFuzz usage documentation:** https://rapidfuzz.github.io/RapidFuzz/Usage/index.html  
- **RapidFuzz similarity functions:** https://rapidfuzz.github.io/RapidFuzz/Usage/fuzz.html  
- **Dedupe library repository and documentation links:** https://github.com/dedupeio/dedupe  
- **Informatica MDM documentation portal:** https://docs.informatica.com/  
- **Informatica Customer 360 guide (example of commercial stewardship workflows):** https://docs.informatica.com/master-data-management/customer-360/10-3/user-guide/introduction-to-informatica-mdm---customer-360/logging-in.html  

Tool APIs and commercial product capabilities vary by version, edition, and deployment. Use the relevant release documentation and test against your environment before production use.

---

# Appendix A — Complete runnable project files

The following source files are included in the downloadable `experiments/04_entity_resolution/` project bundle. The bundle is the executable source of truth; use it to preserve exact file boundaries and avoid copying formatting mistakes from a long lesson.

## A.1 `pyproject.toml`

```toml
[project]
name = "entity-resolution-mdm-lab"
version = "0.1.0"
description = "Educational MDM and entity-resolution lab"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
fuzzy = ["rapidfuzz>=3.6,<4"]
splink = ["splink>=4,<5", "duckdb>=1.0,<2", "pandas>=2.0,<3"]
test = ["pytest>=8,<9"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

## A.2 Core source code

The complete implementation is `resolver.py` and `run_lab.py` in the project bundle. The important API boundaries are:

```python
records = load_records(ROOT / "data/source_records.json")
baseline = classify_pairs(records, method="deterministic")
probabilistic = classify_pairs(records, method="probabilistic", low=3.0, high=9.0)
report = {
    "candidate_generation": candidate_recall(records),
    "deterministic_metrics": metrics(baseline),
    "probabilistic_metrics": metrics(probabilistic),
}
```

The score thresholds are teaching parameters, not universal defaults. Full source, fixtures, tests, and the optional Splink script are in the ZIP bundle.

## A.3 Optional Splink script

`splink_runner.py` is provided as an optional Splink 4 / DuckDB workflow using normalised fields and the documented DuckDB registration pattern. It was **not executed** in this environment because Splink and DuckDB are not installed; confirm behavior in a pinned environment before adopting it.

## A.4 Reproducibility

The project includes:
- `data/source_records.json`: synthetic base records with `entity_id` labels for evaluation.
- `data/incremental_records.json`: one existing-entity record and one new entity.
- `reports/run_report.json`: actual output from the successful core run.
- `tests/test_resolver.py`: 17 passing core tests.

The `entity_id` field is evaluation-only ground truth. It must not be passed to matching features or used to decide real matches.


# Appendix B — Exact file contents from the runnable lab

The files below are the executable source of truth in `experiments/04_entity_resolution/`. The core lab is standard-library Python; pytest is needed for tests. The Splink path is optional and was not executed in the validation run.

## B.1 `README.md`

````markdown
# Entity Resolution and MDM Lab

## Requirements
- Python 3.10+
- Core implementation uses only the standard library.
- Optional: `rapidfuzz` for faster similarity; Splink 4 + DuckDB + pandas for a separate probabilistic linkage demonstration.
- pytest for tests.

## Setup
```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

Optional fuzzy package:
```bash
python -m pip install -e ".[fuzzy,test]"
```

Run core demo:
```bash
python run_lab.py
pytest -q
```

Optional Splink path:
```bash
python -m pip install -e ".[splink]"
python splink_runner.py
```
Splink API is version-sensitive. The optional script is not part of the core test suite. It is included as an integration starting point, not represented as executed in environments without Splink and DuckDB.

## Ground truth
`data/source_records.json` has synthetic source records with `entity_id` labels used only for evaluation. Do not expose ground-truth labels to the matcher in production. `entity_id` is dropped by the optional Splink runner.

## Scope and caveats
The core probabilistic scorer is Fellegi–Sunter-inspired but uses explicit pedagogical weights rather than estimated m/u probabilities. It demonstrates feature agreement, candidate generation, threshold bands, review queues, clustering, survivorship, and ID stability. It is not a trained statistical model and should not be presented as production-calibrated.
````

## B.2 `pyproject.toml`

````toml
[project]
name = "entity-resolution-mdm-lab"
version = "0.1.0"
description = "Educational MDM and entity-resolution lab"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
fuzzy = ["rapidfuzz>=3.6,<4"]
splink = ["splink>=4,<5", "duckdb>=1.0,<2", "pandas>=2.0,<3"]
test = ["pytest>=8,<9"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
````

## B.3 `resolver.py`

````python
from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import defaultdict
from datetime import date, datetime
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_PRIORITY = {"crm": 3, "web": 2, "billing": 1}
DEFAULT_PHONE_COUNTRY_CODE = "91"  # This synthetic fixture is India-centric.


def norm_text(value):
    """Conservative Latin-script normalisation for this teaching fixture."""
    if value is None:
        return ""
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", value.casefold())).strip()


def norm_email(value):
    """Case-fold and remove whitespace, but preserve email-significant punctuation."""
    if value is None:
        return ""
    return re.sub(r"\s+", "", str(value).strip()).casefold()


def norm_phone(value, default_country_code=DEFAULT_PHONE_COUNTRY_CODE):
    """Canonicalise common Indian national/international forms without truncating country codes.

    This is deliberately not a global phone-number parser. Production code should use a
    country-aware library such as libphonenumber and retain the source country context.
    """
    digits = re.sub(r"\D", "", str(value or ""))
    if not digits:
        return ""
    if digits.startswith("00"):
        digits = digits[2:]
    if len(digits) == 10:
        return default_country_code + digits
    if len(digits) == 11 and digits.startswith("0"):
        return default_country_code + digits[1:]
    if len(digits) == 12 and digits.startswith(default_country_code):
        return digits
    return digits


def norm_postcode(value):
    return re.sub(r"\W", "", str(value or "").upper())


def norm_date(value):
    """Return ISO date for supported ISO date/datetime strings; invalid values become missing.

    Ambiguous locale formats (for example 03/04/2001) are intentionally not guessed.
    """
    if value is None or not str(value).strip():
        return ""
    raw = str(value).strip()
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError:
        pass
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return parsed.date().isoformat()
    except ValueError:
        return ""


def _validate_records(records):
    seen = set()
    for index, record in enumerate(records):
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError(f"record at index {index} has no non-empty record_id")
        if record_id in seen:
            raise ValueError(f"duplicate record_id: {record_id}")
        seen.add(record_id)


def name_similarity(a, b):
    a, b = norm_text(a), norm_text(b)
    if not a or not b:
        return 0.0
    try:
        from rapidfuzz.fuzz import WRatio
        return WRatio(a, b) / 100.0
    except ImportError:
        return SequenceMatcher(None, a, b).ratio()


def token_similarity(a, b):
    aa, bb = set(norm_text(a).split()), set(norm_text(b).split())
    return len(aa & bb) / len(aa | bb) if aa or bb else 0.0


def standardise(record):
    out = dict(record)
    out.update({
        "name_norm": norm_text(record.get("name", "")),
        "email_norm": norm_email(record.get("email", "")),
        "phone_norm": norm_phone(record.get("phone", "")),
        "address_norm": norm_text(record.get("address", "")),
        "postcode_norm": norm_postcode(record.get("postcode", "")),
        "dob_norm": norm_date(record.get("dob", "")),
    })
    return out


def load_records(path):
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise ValueError("records file must contain a JSON array of objects")
    _validate_records(records)
    return [standardise(r) for r in records]


def pair_key(a, b):
    return tuple(sorted((a["record_id"], b["record_id"])))


def pair_count(n):
    """Number of unique unordered pairs among n records."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("n must be a non-negative integer")
    return n * (n - 1) // 2


def candidate_pairs(records):
    """Union of exact-email, canonical-phone, and postcode-plus-surname blocks."""
    _validate_records(records)
    buckets = defaultdict(list)
    for r in records:
        if r.get("email_norm"):
            buckets[("email", r["email_norm"])].append(r)
        if r.get("phone_norm") and len(r["phone_norm"]) >= 8:
            buckets[("phone", r["phone_norm"])].append(r)
        name_tokens = r.get("name_norm", "").split()
        surname = name_tokens[-1] if name_tokens else ""
        if r.get("postcode_norm") and surname:
            buckets[("post_surname", r["postcode_norm"], surname)].append(r)
    pairs = {}
    for bucket in buckets.values():
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                pairs[pair_key(bucket[i], bucket[j])] = (bucket[i], bucket[j])
    return [pairs[k] for k in sorted(pairs)]


def pair_features(a, b):
    email_a, email_b = a.get("email_norm", ""), b.get("email_norm", "")
    phone_a, phone_b = a.get("phone_norm", ""), b.get("phone_norm", "")
    dob_a, dob_b = a.get("dob_norm", ""), b.get("dob_norm", "")
    postcode_a, postcode_b = a.get("postcode_norm", ""), b.get("postcode_norm", "")
    email_exact = bool(email_a and email_a == email_b)
    phone_exact = bool(phone_a and len(phone_a) >= 8 and phone_a == phone_b)
    dob_exact = bool(dob_a and dob_a == dob_b)
    postcode_exact = bool(postcode_a and postcode_a == postcode_b)
    ns = name_similarity(a.get("name", ""), b.get("name", ""))
    ts = token_similarity(a.get("name", ""), b.get("name", ""))
    address = name_similarity(a.get("address", ""), b.get("address", ""))
    return {
        "email_exact": email_exact, "phone_exact": phone_exact, "dob_exact": dob_exact,
        "postcode_exact": postcode_exact, "name_similarity": round(ns, 4),
        "name_token_similarity": round(ts, 4), "address_similarity": round(address, 4),
    }


def deterministic_decision(a, b):
    f = pair_features(a, b)
    # Illustrative rule only: one strong identifier plus corroborating evidence.
    strong = (
        (f["email_exact"] and (f["dob_exact"] or f["name_similarity"] >= 0.86))
        or (f["phone_exact"] and f["dob_exact"] and f["postcode_exact"])
        or (f["email_exact"] and f["phone_exact"])
    )
    return ("match" if strong else "non_match"), f


def fs_inspired_score(a, b):
    """Hand-configured Fellegi–Sunter-inspired score, not a trained probability.

    Actual Fellegi–Sunter weights use comparison-outcome probabilities, e.g. log2(m/u).
    These fixed constants are only a transparent teaching heuristic.
    """
    f = pair_features(a, b)
    score = 0.0
    score += 4.0 if f["email_exact"] else (-1.5 if a.get("email_norm") and b.get("email_norm") else 0.0)
    score += 3.5 if f["phone_exact"] else (-1.0 if a.get("phone_norm") and b.get("phone_norm") else 0.0)
    score += 2.0 if f["dob_exact"] else (-1.0 if a.get("dob_norm") and b.get("dob_norm") else 0.0)
    score += 1.5 if f["postcode_exact"] else (-0.4 if a.get("postcode_norm") and b.get("postcode_norm") else 0.0)
    score += 3.0 if f["name_similarity"] >= 0.96 else (1.5 if f["name_similarity"] >= 0.86 else (-1.0 if f["name_similarity"] < 0.55 else 0.0))
    score += 1.0 if f["address_similarity"] >= 0.88 else 0.0
    return round(score, 3), f


def decision_from_score(score, low, high):
    """Apply inclusive high threshold and exclusive low threshold consistently."""
    return "match" if score >= high else ("non_match" if score < low else "review")


def classify_pairs(records, low=3.0, high=9.0, method="probabilistic"):
    if method not in {"deterministic", "probabilistic"}:
        raise ValueError("method must be 'deterministic' or 'probabilistic'")
    try:
        low, high = float(low), float(high)
    except (TypeError, ValueError) as exc:
        raise ValueError("thresholds must be numeric") from exc
    if not math.isfinite(low) or not math.isfinite(high) or low < 0 or high < low:
        raise ValueError("thresholds must be finite, non-negative, and low <= high")
    out = []
    for a, b in candidate_pairs(records):
        if method == "deterministic":
            decision, feats = deterministic_decision(a, b)
            score = None
        else:
            score, feats = fs_inspired_score(a, b)
            decision = decision_from_score(score, low, high)
        left_entity, right_entity = a.get("entity_id"), b.get("entity_id")
        labelled = left_entity not in (None, "") and right_entity not in (None, "")
        out.append({
            "left_id": a["record_id"], "right_id": b["record_id"],
            "left_entity": left_entity, "right_entity": right_entity,
            "ground_truth_match": (left_entity == right_entity) if labelled else None,
            "score": score, "decision": decision, "features": feats,
        })
    return out


def metrics(pair_results):
    """Pair metrics on labelled candidates; undefined denominators are reported as null."""
    labelled = [r for r in pair_results if isinstance(r.get("ground_truth_match"), bool)]
    tp = sum(r["decision"] == "match" and r["ground_truth_match"] is True for r in labelled)
    fp = sum(r["decision"] == "match" and r["ground_truth_match"] is False for r in labelled)
    fn = sum(r["decision"] != "match" and r["ground_truth_match"] is True for r in labelled)
    truth_pairs = sum(r["ground_truth_match"] is True for r in labelled)
    predicted_pairs = sum(r["decision"] == "match" for r in labelled)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1_denominator = 2 * tp + fp + fn
    f1 = (2 * tp / f1_denominator) if f1_denominator else None
    return {
        "candidate_pairs": len(pair_results),
        "labelled_candidate_pairs": len(labelled),
        "unlabelled_candidate_pairs": len(pair_results) - len(labelled),
        "candidate_ground_truth_match_pairs": truth_pairs,
        "predicted_matches": predicted_pairs,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives_within_candidates": fn,
        "precision": round(precision, 4) if precision is not None else None,
        "recall_within_candidates": round(recall, 4) if recall is not None else None,
        "f1_within_candidates": round(f1, 4) if f1 is not None else None,
        "precision_defined": precision is not None,
        "recall_defined": recall is not None,
        "f1_defined": f1 is not None,
    }


def all_true_pairs(records):
    labelled = [r for r in records if r.get("entity_id") not in (None, "")]
    return sum(1 for i in range(len(labelled)) for j in range(i + 1, len(labelled))
               if labelled[i].get("entity_id") == labelled[j].get("entity_id"))


def candidate_recall(records):
    _validate_records(records)
    labelled = [r for r in records if r.get("entity_id") not in (None, "")]
    cands = candidate_pairs(records)
    found = {pair_key(a, b) for a, b in cands}
    truth = {pair_key(labelled[i], labelled[j]) for i in range(len(labelled))
             for j in range(i + 1, len(labelled))
             if labelled[i].get("entity_id") == labelled[j].get("entity_id")}
    return {
        "record_count": len(records),
        "labelled_record_count": len(labelled),
        "unlabelled_record_count": len(records) - len(labelled),
        "all_possible_pairs": pair_count(len(records)),
        "all_possible_labelled_pairs": pair_count(len(labelled)),
        "all_ground_truth_match_pairs": len(truth),
        "candidate_true_pairs": len(found & truth),
        "blocking_recall": round(len(found & truth) / len(truth), 4) if truth else None,
        "blocking_recall_defined": bool(truth),
        "candidate_pairs": len(found),
        "reduction_ratio": round(1 - len(found) / pair_count(len(records)), 4) if len(records) > 1 else None,
    }


def connected_components(records, decisions):
    """Build components from auto-match edges. Review edges never merge clusters.

    Connected components are a simple demonstration: transitive chains can still cause
    false merges, so production systems need cluster-level constraints and review policies.
    """
    _validate_records(records)
    ids = [r["record_id"] for r in records]
    parent = {x: x for x in ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    known = set(ids)
    for p in decisions:
        if p["decision"] == "match":
            if p["left_id"] not in known or p["right_id"] not in known:
                raise ValueError("decision references a record absent from the supplied record set")
            union(p["left_id"], p["right_id"])
    groups = defaultdict(list)
    for record_id in ids:
        groups[find(record_id)].append(record_id)
    return sorted([sorted(v) for v in groups.values()], key=lambda x: x[0])


def make_master_id_registry(records, previous_xref=None):
    """Assign stable IDs; surface merge conflicts and detect split components.

    Previous mappings for records outside this batch are retained as historical xrefs. For a
    split, the component containing the most previously mapped records keeps the old ID (ties
    break deterministically); other components receive new IDs and an explicit stewardship event.
    A component touching multiple old IDs is not silently merged: its existing mappings remain,
    new records are left unmapped, and a conflict event is emitted.
    """
    _validate_records(records)
    previous_xref = dict(previous_xref or {})
    comps = connected_components(records, classify_pairs(records, method="probabilistic"))
    old_mids_by_comp = [sorted({previous_xref[rid] for rid in comp if rid in previous_xref}) for comp in comps]
    component_indexes_by_mid = defaultdict(list)
    for index, mids in enumerate(old_mids_by_comp):
        for mid in mids:
            component_indexes_by_mid[mid].append(index)

    next_num = 1
    used_ids = set(previous_xref.values())
    for mid in used_ids:
        try:
            next_num = max(next_num, int(str(mid).split("-")[-1]) + 1)
        except ValueError:
            continue

    def allocate_id():
        nonlocal next_num
        while True:
            candidate = f"M-{next_num:06d}"
            next_num += 1
            if candidate not in used_ids:
                used_ids.add(candidate)
                return candidate

    # Choose one deterministic anchor component for every prior ID split across components.
    split_anchor = {}
    events = []
    for mid, indexes in sorted(component_indexes_by_mid.items()):
        if len(indexes) > 1:
            # If an old ID participates in a multi-master conflict component, keep its
            # historical mapping there and allocate new IDs to any other components.
            conflict_indexes = [i for i in indexes if len(old_mids_by_comp[i]) > 1]
            eligible_indexes = [i for i in indexes if old_mids_by_comp[i] == [mid]]
            if conflict_indexes:
                anchor = min(conflict_indexes, key=lambda i: (-sum(previous_xref.get(rid) == mid for rid in comps[i]), comps[i][0]))
            elif eligible_indexes:
                anchor = min(eligible_indexes, key=lambda i: (-sum(previous_xref.get(rid) == mid for rid in comps[i]), comps[i][0]))
            else:
                anchor = min(indexes, key=lambda i: comps[i][0])
            split_anchor[mid] = anchor

    registry = dict(previous_xref)  # Preserve historical xrefs outside this current batch.
    for i, comp in enumerate(comps):
        mids = old_mids_by_comp[i]
        if len(mids) > 1:
            events.append({
                "action": "merge_conflict_steward_review_required",
                "records": comp,
                "existing_master_ids": mids,
                "reason": "automatic component touches multiple previously distinct master IDs",
            })
            # Existing record mappings remain untouched; new records in this component stay unmapped.
            continue
        if len(mids) == 1:
            old_mid = mids[0]
            if old_mid in split_anchor and split_anchor[old_mid] != i:
                new_mid = allocate_id()
                for rid in comp:
                    registry[rid] = new_mid
                events.append({
                    "action": "split_detected_new_id_assigned_steward_review_required",
                    "old_master_id": old_mid,
                    "proposed_master_id": new_mid,
                    "records": comp,
                    "reason": "non-anchor split component receives a new ID; steward must confirm the split",
                })
            else:
                for rid in comp:
                    registry[rid] = old_mid
        else:
            new_mid = allocate_id()
            for rid in comp:
                registry[rid] = new_mid

    # Any current records without mappings belong to an unresolved merge conflict.
    return registry, events


def survivorship(records):
    """Field-specific, deterministic survivorship with field-level provenance.

    Name/postcode use source priority; contact/address use recency; DOB uses record-level
    completeness (count of populated core attributes), then recency and source priority.
    Consent is never inferred from recency or source priority.
    """
    if not records:
        raise ValueError("cannot build golden record from empty cluster")
    entity_records = sorted(records, key=lambda r: r["record_id"])

    def source_priority(record):
        return SOURCE_PRIORITY.get(str(record.get("source", "unknown")).casefold(), 0)

    def completeness(record):
        fields = ("name", "email", "phone", "address", "postcode", "dob")
        return sum(bool(record.get(field)) for field in fields)

    def best(field, mode):
        candidates = [r for r in entity_records if r.get(field) not in (None, "")]
        if not candidates:
            return None
        if mode == "source":
            winner = max(candidates, key=lambda r: (source_priority(r), r.get("updated_at", ""), r["record_id"]))
        elif mode == "recent":
            winner = max(candidates, key=lambda r: (r.get("updated_at", ""), source_priority(r), r["record_id"]))
        elif mode == "complete":
            winner = max(candidates, key=lambda r: (completeness(r), r.get("updated_at", ""), source_priority(r), r["record_id"]))
        else:
            raise ValueError(f"unknown survivorship mode: {mode}")
        return {"value": winner[field], "source_record_id": winner["record_id"], "rule": mode}

    return {
        "master_id": None,
        "name": best("name", "source"),
        "email": best("email", "recent"),
        "phone": best("phone", "recent"),
        "address": best("address", "recent"),
        "postcode": best("postcode", "source"),
        "dob": best("dob", "complete"),
        "source_record_ids": sorted(r["record_id"] for r in entity_records),
        "consent_values": sorted({r.get("consent", "unknown") for r in entity_records}),
        "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship",
    }


def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
````

## B.4 `run_lab.py`

````python
from pathlib import Path
import json
from resolver import ROOT, load_records, classify_pairs, metrics, candidate_recall, connected_components, survivorship, make_master_id_registry, save_json

def run():
    records = load_records(ROOT / "data/source_records.json")
    baseline = classify_pairs(records, method="deterministic")
    probabilistic = classify_pairs(records, method="probabilistic", low=3.0, high=9.0)
    stats = {
        "record_count": len(records),
        "candidate_generation": candidate_recall(records),
        "deterministic_metrics": metrics(baseline),
        "probabilistic_metrics": metrics(probabilistic),
        "uncertain_pairs": [p for p in probabilistic if p["decision"] == "review"],
        "clusters": connected_components(records, probabilistic),
    }
    xref, conflicts = make_master_id_registry(records)
    golden = []
    by_id = {r["record_id"]:r for r in records}
    for comp in stats["clusters"]:
        g = survivorship([by_id[rid] for rid in comp])
        mids = {xref.get(rid) for rid in comp}
        g["master_id"] = next(iter(mids)) if len(mids) == 1 else None
        golden.append(g)
    stats["cross_reference"] = [{"record_id":k,"master_id":v} for k,v in sorted(xref.items())]
    stats["identity_events"] = conflicts
    stats["golden_records"] = golden
    save_json(ROOT / "reports/run_report.json", stats)
    print(json.dumps({
        "record_count": stats["record_count"],
        "candidate_generation": stats["candidate_generation"],
        "deterministic_metrics": stats["deterministic_metrics"],
        "probabilistic_metrics": stats["probabilistic_metrics"],
        "review_queue_size": len(stats["uncertain_pairs"]),
        "cluster_count": len(stats["clusters"]),
        "cross_reference_rows": len(stats["cross_reference"]),
        "report": str(ROOT / "reports/run_report.json")
    }, indent=2))
    return stats

if __name__ == "__main__":
    run()
````

## B.5 `splink_runner.py`

````python
"""Optional Splink 4 / DuckDB demonstration.

Install with: python -m pip install -e '.[splink]'
This is separate from the standard-library core lab. It was not executed in the
validation environment because Splink and DuckDB were not installed.
"""
import json
from pathlib import Path

import pandas as pd
import splink.comparison_library as cl
from splink import DuckDBAPI, Linker, SettingsCreator, block_on

from resolver import ROOT, standardise

records = json.loads((ROOT / "data/source_records.json").read_text(encoding="utf-8"))
# Ground-truth labels are evaluation-only and must never enter matching features.
normalised = [standardise(record) for record in records]
df = pd.DataFrame(normalised).drop(columns=["entity_id"], errors="ignore")

settings = SettingsCreator(
    link_type="dedupe_only",
    unique_id_column_name="record_id",
    blocking_rules_to_generate_predictions=[
        block_on("email_norm"),
        block_on("phone_norm"),
        block_on("postcode_norm", "name_norm"),
    ],
    comparisons=[
        cl.ExactMatch("email_norm").configure(term_frequency_adjustments=True),
        cl.ExactMatch("phone_norm"),
        cl.ExactMatch("dob_norm"),
        cl.JaroWinklerAtThresholds("name_norm", [0.9, 0.7]),
        cl.JaroWinklerAtThresholds("address_norm", [0.9, 0.7]),
    ],
    retain_matching_columns=True,
    retain_intermediate_calculation_columns=True,
)

db_api = DuckDBAPI()
df_sdf = db_api.register(df, dataset_display_name="entity_resolution_source_records")
linker = Linker(df_sdf, settings)

# These are model-training operations. They need diagnostics and representative data;
# running them does not guarantee calibrated or unbiased match probabilities.
linker.training.estimate_u_using_random_sampling(max_pairs=1_000_000)
linker.training.estimate_parameters_using_expectation_maximisation(block_on("phone_norm"))

# This threshold is a starting point for inspection, not a production decision threshold.
predictions = linker.inference.predict(threshold_match_weight=3.0)
out = predictions.as_pandas_dataframe()
report_dir = ROOT / "reports"
report_dir.mkdir(parents=True, exist_ok=True)
out.to_csv(report_dir / "splink_predictions.csv", index=False)
print(f"Splink wrote {len(out)} scored candidate predictions to {report_dir / 'splink_predictions.csv'}")
````

## B.6 `tests/test_resolver.py`

````python
import pytest
from resolver import (
    ROOT, load_records, candidate_pairs, candidate_recall, classify_pairs, metrics,
    deterministic_decision, standardise, survivorship, make_master_id_registry,
    norm_email, norm_phone, norm_date, pair_count, decision_from_score,
)


def test_dataset_is_reproducible_and_has_ground_truth():
    records = load_records(ROOT / "data/source_records.json")
    assert len(records) == 21
    assert len({r["entity_id"] for r in records}) == 11
    assert len({r["record_id"] for r in records}) == len(records)


def test_candidate_generation_reduces_pairs_and_keeps_all_synthetic_true_pairs():
    records = load_records(ROOT / "data/source_records.json")
    result = candidate_recall(records)
    assert result["all_possible_pairs"] == 210
    assert result["candidate_pairs"] == 13
    assert result["all_ground_truth_match_pairs"] == 11
    assert result["candidate_true_pairs"] == 11
    assert result["blocking_recall"] == 1.0
    assert 0 < result["reduction_ratio"] < 1


def test_deterministic_pair_uses_explicit_rule_and_canonical_phone():
    a = standardise({"record_id":"a","name":"A B","email":"x@y.com","phone":"9876543210","dob":"2000-01-01","postcode":"700001"})
    b = standardise({"record_id":"b","name":"A B","email":"X@Y.COM","phone":"+91 98765 43210","dob":"2000-01-01T00:00:00Z","postcode":"700001"})
    decision, _ = deterministic_decision(a, b)
    assert decision == "match"
    assert a["phone_norm"] == b["phone_norm"]
    assert a["dob_norm"] == b["dob_norm"]


def test_email_normalisation_preserves_significant_punctuation():
    assert norm_email(" Jane.Doe+sales@Example.com ") == "jane.doe+sales@example.com"
    assert norm_email("jane.doe@example.com") != norm_email("janedoe@example.com")


def test_phone_normalisation_does_not_truncate_foreign_country_codes():
    assert norm_phone("9876543210") == norm_phone("+91 98765 43210")
    assert norm_phone("+1 9876543210") != norm_phone("+91 9876543210")


def test_date_normalisation_handles_iso_datetime_and_rejects_ambiguous_dates():
    assert norm_date("2000-01-01T23:30:00Z") == "2000-01-01"
    assert norm_date("2000-01-01") == "2000-01-01"
    assert norm_date("03/04/2001") == ""
    assert norm_date("not-a-date") == ""


def test_threshold_boundaries_are_consistent():
    assert decision_from_score(2.999, 3.0, 9.0) == "non_match"
    assert decision_from_score(3.0, 3.0, 9.0) == "review"
    assert decision_from_score(8.999, 3.0, 9.0) == "review"
    assert decision_from_score(9.0, 3.0, 9.0) == "match"


def test_pair_metrics_are_bounded_and_report_denominator_edge_cases():
    records = load_records(ROOT / "data/source_records.json")
    for method in ["deterministic", "probabilistic"]:
        result = metrics(classify_pairs(records, method=method))
        assert 0 <= result["precision"] <= 1
        assert 0 <= result["recall_within_candidates"] <= 1
        assert 0 <= result["f1_within_candidates"] <= 1
        assert result["unlabelled_candidate_pairs"] == 0

    no_predictions = metrics([{"ground_truth_match": True, "decision": "review"}])
    assert no_predictions["precision"] is None
    assert no_predictions["recall_within_candidates"] == 0.0
    assert no_predictions["f1_within_candidates"] == 0.0
    assert no_predictions["precision_defined"] is False

    no_positive_truth = metrics([{"ground_truth_match": False, "decision": "non_match"}])
    assert no_positive_truth["precision"] is None
    assert no_positive_truth["recall_within_candidates"] is None
    assert no_positive_truth["f1_within_candidates"] is None


def test_unlabelled_pairs_do_not_become_ground_truth_matches():
    records = [
        standardise({"record_id": "a", "email": "same@example.com"}),
        standardise({"record_id": "b", "email": "same@example.com"}),
    ]
    pairs = classify_pairs(records)
    assert len(pairs) == 1
    assert pairs[0]["ground_truth_match"] is None
    result = metrics(pairs)
    assert result["unlabelled_candidate_pairs"] == 1
    assert result["precision"] is None


def test_uncertain_pairs_are_not_auto_merged():
    records = load_records(ROOT / "data/source_records.json")
    decisions = classify_pairs(records, method="probabilistic")
    review = [p for p in decisions if p["decision"] == "review"]
    assert review
    from resolver import connected_components
    clusters = [set(c) for c in connected_components(records, decisions)]
    assert not any("CRM-012" in c and ("CRM-002" in c or "WEB-102" in c) for c in clusters)


def test_survivorship_is_deterministic_and_auditable():
    records = load_records(ROOT / "data/source_records.json")
    cluster = [r for r in records if r["entity_id"] == "E1"]
    g = survivorship(cluster)
    assert g["name"]["source_record_id"] == "CRM-001"
    assert g["email"]["source_record_id"] == "WEB-101"
    assert g["source_record_ids"] == ["BILL-201", "CRM-001", "WEB-101"]
    assert g["dob"]["rule"] == "complete"


def test_incremental_registry_preserves_existing_ids_without_merge_or_split():
    records = load_records(ROOT / "data/source_records.json")
    old_xref, old_events = make_master_id_registry(records)
    assert old_events == []
    incremental = load_records(ROOT / "data/incremental_records.json")
    all_records = records + incremental
    new_xref, events = make_master_id_registry(all_records, old_xref)
    for rid, mid in old_xref.items():
        assert new_xref[rid] == mid
    assert new_xref["WEB-110"] == old_xref["CRM-010"]
    assert new_xref["CRM-011"] not in set(old_xref.values())
    assert events == []


def test_split_gets_distinct_id_and_stewardship_event():
    records = load_records(ROOT / "data/source_records.json")
    # CRM-001 and WEB-101 form one component; unrelated CRM-003 is a separate component.
    subset = [r for r in records if r["record_id"] in {"CRM-001", "WEB-101", "CRM-003"}]
    previous = {"CRM-001": "M-000001", "WEB-101": "M-000001", "CRM-003": "M-000001"}
    registry, events = make_master_id_registry(subset, previous)
    assert registry["CRM-001"] == registry["WEB-101"] == "M-000001"
    assert registry["CRM-003"] != "M-000001"
    assert len({registry[r["record_id"]] for r in subset}) == 2
    assert any("split_detected" in event["action"] for event in events)


def test_merge_of_two_existing_master_ids_is_not_silent():
    records = load_records(ROOT / "data/source_records.json")
    subset = [r for r in records if r["record_id"] in {"CRM-001", "WEB-101"}]
    previous = {"CRM-001": "M-000001", "WEB-101": "M-000002"}
    registry, events = make_master_id_registry(subset, previous)
    assert registry["CRM-001"] == "M-000001"
    assert registry["WEB-101"] == "M-000002"
    assert any(event["action"] == "merge_conflict_steward_review_required" for event in events)


def test_invalid_method_thresholds_and_duplicate_ids_fail_explicitly():
    records = load_records(ROOT / "data/source_records.json")
    with pytest.raises(ValueError):
        classify_pairs(records, method="typo")
    with pytest.raises(ValueError):
        classify_pairs(records, low=10, high=3)
    duplicate = [standardise({"record_id": "x"}), standardise({"record_id": "x"})]
    with pytest.raises(ValueError, match="duplicate record_id"):
        candidate_pairs(duplicate)


def test_blocking_recall_is_undefined_without_labelled_true_pairs():
    records = [
        standardise({"record_id": "a", "entity_id": "E1", "email": "a@example.com"}),
        standardise({"record_id": "b", "entity_id": "E2", "email": "b@example.com"}),
    ]
    result = candidate_recall(records)
    assert result["all_ground_truth_match_pairs"] == 0
    assert result["blocking_recall"] is None
    assert result["blocking_recall_defined"] is False


def test_ten_million_pair_formula_and_invalid_sizes():
    assert pair_count(10_000_000) == 49_999_995_000_000
    assert pair_count(0) == 0
    assert pair_count(1) == 0
    with pytest.raises(ValueError):
        pair_count(-1)
    with pytest.raises(ValueError):
        pair_count(1.5)
````

## B.7 `data/source_records.json`

````json
[
  {
    "record_id": "CRM-001",
    "source": "crm",
    "source_id": "C100",
    "name": "Ananya Sharma",
    "email": "ananya.sharma@example.com",
    "phone": "+91 98765 43210",
    "address": "12 Park Street, Kolkata",
    "postcode": "700016",
    "dob": "1990-04-12",
    "updated_at": "2026-01-05",
    "consent": "active",
    "entity_id": "E1"
  },
  {
    "record_id": "WEB-101",
    "source": "web",
    "source_id": "W901",
    "name": "Ananya  Sharma",
    "email": "ANANYA.SHARMA@example.com",
    "phone": "9876543210",
    "address": "12 Park St, Kolkata",
    "postcode": "700016",
    "dob": "1990-04-12",
    "updated_at": "2026-02-10",
    "consent": "active",
    "entity_id": "E1"
  },
  {
    "record_id": "BILL-201",
    "source": "billing",
    "source_id": "B551",
    "name": "A. Sharma",
    "email": "",
    "phone": "+91-9876543210",
    "address": "12 Park Street",
    "postcode": "700016",
    "dob": "1990-04-12",
    "updated_at": "2025-12-20",
    "consent": "active",
    "entity_id": "E1"
  },
  {
    "record_id": "CRM-002",
    "source": "crm",
    "source_id": "C101",
    "name": "Rahul Banerjee",
    "email": "rahul.b@example.com",
    "phone": "+91 91234 56789",
    "address": "8 Lake Road, Kolkata",
    "postcode": "700029",
    "dob": "1985-11-03",
    "updated_at": "2026-02-01",
    "consent": "active",
    "entity_id": "E2"
  },
  {
    "record_id": "WEB-102",
    "source": "web",
    "source_id": "W902",
    "name": "Rahul Bannerjee",
    "email": "rahul.b@example.com",
    "phone": "9123456789",
    "address": "8 Lake Rd, Kolkata",
    "postcode": "700029",
    "dob": "1985-11-03",
    "updated_at": "2026-02-03",
    "consent": "active",
    "entity_id": "E2"
  },
  {
    "record_id": "CRM-003",
    "source": "crm",
    "source_id": "C102",
    "name": "Mira Das",
    "email": "mira.das@example.com",
    "phone": "+91 90000 11111",
    "address": "4 Salt Lake, Kolkata",
    "postcode": "700091",
    "dob": "1992-07-21",
    "updated_at": "2026-01-10",
    "consent": "active",
    "entity_id": "E3"
  },
  {
    "record_id": "BILL-203",
    "source": "billing",
    "source_id": "B553",
    "name": "Meera Das",
    "email": "",
    "phone": "9000011111",
    "address": "4 Sector I, Salt Lake",
    "postcode": "700091",
    "dob": "1992-07-21",
    "updated_at": "2026-01-12",
    "consent": "active",
    "entity_id": "E3"
  },
  {
    "record_id": "CRM-004",
    "source": "crm",
    "source_id": "C103",
    "name": "Sanjay Roy",
    "email": "s.roy@example.com",
    "phone": "+91 98888 77777",
    "address": "20 New Town",
    "postcode": "700156",
    "dob": "1978-03-09",
    "updated_at": "2026-01-20",
    "consent": "active",
    "entity_id": "E4"
  },
  {
    "record_id": "WEB-104",
    "source": "web",
    "source_id": "W904",
    "name": "Sanjay Roy",
    "email": "s.roy@example.com",
    "phone": "9888877777",
    "address": "20 New Town, Kolkata",
    "postcode": "700156",
    "dob": "1978-03-09",
    "updated_at": "2026-02-15",
    "consent": "active",
    "entity_id": "E4"
  },
  {
    "record_id": "CRM-005",
    "source": "crm",
    "source_id": "C104",
    "name": "Priya Sen",
    "email": "priya.sen@example.com",
    "phone": "+91 93333 22222",
    "address": "9 Ballygunge Place",
    "postcode": "700019",
    "dob": "1988-09-30",
    "updated_at": "2026-01-15",
    "consent": "active",
    "entity_id": "E5"
  },
  {
    "record_id": "WEB-105",
    "source": "web",
    "source_id": "W905",
    "name": "Priya Sen",
    "email": "priya.sen@example.com",
    "phone": "9333322222",
    "address": "9 Ballygunge Pl",
    "postcode": "700019",
    "dob": "1988-09-30",
    "updated_at": "2026-02-18",
    "consent": "active",
    "entity_id": "E5"
  },
  {
    "record_id": "CRM-006",
    "source": "crm",
    "source_id": "C105",
    "name": "Amit Ghosh",
    "email": "amit.ghosh@example.com",
    "phone": "+91 95555 66666",
    "address": "3 Howrah Road",
    "postcode": "711101",
    "dob": "1991-01-05",
    "updated_at": "2026-02-01",
    "consent": "active",
    "entity_id": "E6"
  },
  {
    "record_id": "WEB-106",
    "source": "web",
    "source_id": "W906",
    "name": "Amit Ghosh",
    "email": "amit.ghosh@example.com",
    "phone": "9555566666",
    "address": "3 Howrah Rd",
    "postcode": "711101",
    "dob": "1991-01-05",
    "updated_at": "2026-02-02",
    "consent": "active",
    "entity_id": "E6"
  },
  {
    "record_id": "CRM-007",
    "source": "crm",
    "source_id": "C106",
    "name": "Nisha Kapoor",
    "email": "nisha.k@example.com",
    "phone": "+91 96666 11111",
    "address": "7 Alipore",
    "postcode": "700027",
    "dob": "1994-06-11",
    "updated_at": "2026-02-01",
    "consent": "active",
    "entity_id": "E7"
  },
  {
    "record_id": "WEB-107",
    "source": "web",
    "source_id": "W907",
    "name": "Nisha Kapur",
    "email": "nisha.k@example.com",
    "phone": "9666611111",
    "address": "7 Alipore, Kolkata",
    "postcode": "700027",
    "dob": "1994-06-11",
    "updated_at": "2026-02-04",
    "consent": "active",
    "entity_id": "E7"
  },
  {
    "record_id": "CRM-008",
    "source": "crm",
    "source_id": "C107",
    "name": "Arjun Mehta",
    "email": "arjun.mehta@example.com",
    "phone": "+91 94444 33333",
    "address": "11 Camac Street",
    "postcode": "700017",
    "dob": "1989-02-14",
    "updated_at": "2026-01-09",
    "consent": "active",
    "entity_id": "E8"
  },
  {
    "record_id": "WEB-108",
    "source": "web",
    "source_id": "W908",
    "name": "Arjun Mehta",
    "email": "arjun.m@example.com",
    "phone": "9444433333",
    "address": "11 Camac St",
    "postcode": "700017",
    "dob": "1989-02-14",
    "updated_at": "2026-02-04",
    "consent": "active",
    "entity_id": "E8"
  },
  {
    "record_id": "CRM-009",
    "source": "crm",
    "source_id": "C108",
    "name": "Kavita Rao",
    "email": "kavita.rao@example.com",
    "phone": "+91 92222 44444",
    "address": "2 Behala",
    "postcode": "700034",
    "dob": "1993-12-01",
    "updated_at": "2026-01-11",
    "consent": "active",
    "entity_id": "E9"
  },
  {
    "record_id": "WEB-109",
    "source": "web",
    "source_id": "W909",
    "name": "Kavita Rao",
    "email": "kavita.rao@example.com",
    "phone": "9222244444",
    "address": "2 Behala",
    "postcode": "700034",
    "dob": "1993-12-01",
    "updated_at": "2026-02-11",
    "consent": "active",
    "entity_id": "E9"
  },
  {
    "record_id": "CRM-010",
    "source": "crm",
    "source_id": "C109",
    "name": "Dev Patel",
    "email": "dev.patel@example.com",
    "phone": "+91 91111 22222",
    "address": "5 Tollygunge",
    "postcode": "700033",
    "dob": "1987-08-19",
    "updated_at": "2026-01-13",
    "consent": "active",
    "entity_id": "E10"
  },
  {
    "record_id": "CRM-012",
    "source": "crm",
    "source_id": "C112",
    "name": "Rahul Bannerjee",
    "email": "",
    "phone": "+91 91234 56789",
    "address": "8 Lake Road, Kolkata",
    "postcode": "700029",
    "dob": "1986-11-03",
    "updated_at": "2026-03-05",
    "consent": "active",
    "entity_id": "E11"
  }
]
````

## B.8 `data/incremental_records.json`

````json
[
  {
    "record_id": "WEB-110",
    "source": "web",
    "source_id": "W910",
    "name": "Dev Patel",
    "email": "dev.patel@example.com",
    "phone": "9111122222",
    "address": "5 Tollygunge, Kolkata",
    "postcode": "700033",
    "dob": "1987-08-19",
    "updated_at": "2026-03-01",
    "consent": "active",
    "entity_id": "E10"
  },
  {
    "record_id": "CRM-011",
    "source": "crm",
    "source_id": "C110",
    "name": "Tara Bose",
    "email": "tara.bose@example.com",
    "phone": "+91 90000 22222",
    "address": "15 Gariahat Road",
    "postcode": "700019",
    "dob": "1995-05-06",
    "updated_at": "2026-03-02",
    "consent": "active",
    "entity_id": "E12"
  }
]
````

## B.9 `reports/run_report.json`

````json
{
  "record_count": 21,
  "candidate_generation": {
    "record_count": 21,
    "labelled_record_count": 21,
    "unlabelled_record_count": 0,
    "all_possible_pairs": 210,
    "all_possible_labelled_pairs": 210,
    "all_ground_truth_match_pairs": 11,
    "candidate_true_pairs": 11,
    "blocking_recall": 1.0,
    "blocking_recall_defined": true,
    "candidate_pairs": 13,
    "reduction_ratio": 0.9381
  },
  "deterministic_metrics": {
    "candidate_pairs": 13,
    "labelled_candidate_pairs": 13,
    "unlabelled_candidate_pairs": 0,
    "candidate_ground_truth_match_pairs": 11,
    "predicted_matches": 11,
    "true_positives": 11,
    "false_positives": 0,
    "false_negatives_within_candidates": 0,
    "precision": 1.0,
    "recall_within_candidates": 1.0,
    "f1_within_candidates": 1.0,
    "precision_defined": true,
    "recall_defined": true,
    "f1_defined": true
  },
  "probabilistic_metrics": {
    "candidate_pairs": 13,
    "labelled_candidate_pairs": 13,
    "unlabelled_candidate_pairs": 0,
    "candidate_ground_truth_match_pairs": 11,
    "predicted_matches": 8,
    "true_positives": 8,
    "false_positives": 0,
    "false_negatives_within_candidates": 3,
    "precision": 1.0,
    "recall_within_candidates": 0.7273,
    "f1_within_candidates": 0.8421,
    "precision_defined": true,
    "recall_defined": true,
    "f1_defined": true
  },
  "uncertain_pairs": [
    {
      "left_id": "WEB-101",
      "right_id": "BILL-201",
      "left_entity": "E1",
      "right_entity": "E1",
      "ground_truth_match": true,
      "score": 8.5,
      "decision": "review",
      "features": {
        "email_exact": false,
        "phone_exact": true,
        "dob_exact": true,
        "postcode_exact": true,
        "name_similarity": 0.9,
        "name_token_similarity": 0.3333,
        "address_similarity": 0.6875
      }
    },
    {
      "left_id": "CRM-003",
      "right_id": "BILL-203",
      "left_entity": "E3",
      "right_entity": "E3",
      "ground_truth_match": true,
      "score": 7.0,
      "decision": "review",
      "features": {
        "email_exact": false,
        "phone_exact": true,
        "dob_exact": true,
        "postcode_exact": true,
        "name_similarity": 0.8235,
        "name_token_similarity": 0.3333,
        "address_similarity": 0.6967
      }
    },
    {
      "left_id": "CRM-002",
      "right_id": "CRM-012",
      "left_entity": "E2",
      "right_entity": "E11",
      "ground_truth_match": false,
      "score": 8.0,
      "decision": "review",
      "features": {
        "email_exact": false,
        "phone_exact": true,
        "dob_exact": false,
        "postcode_exact": true,
        "name_similarity": 0.9655,
        "name_token_similarity": 0.3333,
        "address_similarity": 1.0
      }
    },
    {
      "left_id": "CRM-008",
      "right_id": "WEB-108",
      "left_entity": "E8",
      "right_entity": "E8",
      "ground_truth_match": true,
      "score": 8.5,
      "decision": "review",
      "features": {
        "email_exact": false,
        "phone_exact": true,
        "dob_exact": true,
        "postcode_exact": true,
        "name_similarity": 1.0,
        "name_token_similarity": 1.0,
        "address_similarity": 0.8462
      }
    },
    {
      "left_id": "WEB-102",
      "right_id": "CRM-012",
      "left_entity": "E2",
      "right_entity": "E11",
      "ground_truth_match": false,
      "score": 8.0,
      "decision": "review",
      "features": {
        "email_exact": false,
        "phone_exact": true,
        "dob_exact": false,
        "postcode_exact": true,
        "name_similarity": 1.0,
        "name_token_similarity": 1.0,
        "address_similarity": 0.9444
      }
    }
  ],
  "clusters": [
    [
      "BILL-201",
      "CRM-001",
      "WEB-101"
    ],
    [
      "BILL-203"
    ],
    [
      "CRM-002",
      "WEB-102"
    ],
    [
      "CRM-003"
    ],
    [
      "CRM-004",
      "WEB-104"
    ],
    [
      "CRM-005",
      "WEB-105"
    ],
    [
      "CRM-006",
      "WEB-106"
    ],
    [
      "CRM-007",
      "WEB-107"
    ],
    [
      "CRM-008"
    ],
    [
      "CRM-009",
      "WEB-109"
    ],
    [
      "CRM-010"
    ],
    [
      "CRM-012"
    ],
    [
      "WEB-108"
    ]
  ],
  "cross_reference": [
    {
      "record_id": "BILL-201",
      "master_id": "M-000001"
    },
    {
      "record_id": "BILL-203",
      "master_id": "M-000002"
    },
    {
      "record_id": "CRM-001",
      "master_id": "M-000001"
    },
    {
      "record_id": "CRM-002",
      "master_id": "M-000003"
    },
    {
      "record_id": "CRM-003",
      "master_id": "M-000004"
    },
    {
      "record_id": "CRM-004",
      "master_id": "M-000005"
    },
    {
      "record_id": "CRM-005",
      "master_id": "M-000006"
    },
    {
      "record_id": "CRM-006",
      "master_id": "M-000007"
    },
    {
      "record_id": "CRM-007",
      "master_id": "M-000008"
    },
    {
      "record_id": "CRM-008",
      "master_id": "M-000009"
    },
    {
      "record_id": "CRM-009",
      "master_id": "M-000010"
    },
    {
      "record_id": "CRM-010",
      "master_id": "M-000011"
    },
    {
      "record_id": "CRM-012",
      "master_id": "M-000012"
    },
    {
      "record_id": "WEB-101",
      "master_id": "M-000001"
    },
    {
      "record_id": "WEB-102",
      "master_id": "M-000003"
    },
    {
      "record_id": "WEB-104",
      "master_id": "M-000005"
    },
    {
      "record_id": "WEB-105",
      "master_id": "M-000006"
    },
    {
      "record_id": "WEB-106",
      "master_id": "M-000007"
    },
    {
      "record_id": "WEB-107",
      "master_id": "M-000008"
    },
    {
      "record_id": "WEB-108",
      "master_id": "M-000013"
    },
    {
      "record_id": "WEB-109",
      "master_id": "M-000010"
    }
  ],
  "identity_events": [],
  "golden_records": [
    {
      "master_id": "M-000001",
      "name": {
        "value": "Ananya Sharma",
        "source_record_id": "CRM-001",
        "rule": "source"
      },
      "email": {
        "value": "ANANYA.SHARMA@example.com",
        "source_record_id": "WEB-101",
        "rule": "recent"
      },
      "phone": {
        "value": "9876543210",
        "source_record_id": "WEB-101",
        "rule": "recent"
      },
      "address": {
        "value": "12 Park St, Kolkata",
        "source_record_id": "WEB-101",
        "rule": "recent"
      },
      "postcode": {
        "value": "700016",
        "source_record_id": "CRM-001",
        "rule": "source"
      },
      "dob": {
        "value": "1990-04-12",
        "source_record_id": "WEB-101",
        "rule": "complete"
      },
      "source_record_ids": [
        "BILL-201",
        "CRM-001",
        "WEB-101"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    },
    {
      "master_id": "M-000002",
      "name": {
        "value": "Meera Das",
        "source_record_id": "BILL-203",
        "rule": "source"
      },
      "email": null,
      "phone": {
        "value": "9000011111",
        "source_record_id": "BILL-203",
        "rule": "recent"
      },
      "address": {
        "value": "4 Sector I, Salt Lake",
        "source_record_id": "BILL-203",
        "rule": "recent"
      },
      "postcode": {
        "value": "700091",
        "source_record_id": "BILL-203",
        "rule": "source"
      },
      "dob": {
        "value": "1992-07-21",
        "source_record_id": "BILL-203",
        "rule": "complete"
      },
      "source_record_ids": [
        "BILL-203"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    },
    {
      "master_id": "M-000003",
      "name": {
        "value": "Rahul Banerjee",
        "source_record_id": "CRM-002",
        "rule": "source"
      },
      "email": {
        "value": "rahul.b@example.com",
        "source_record_id": "WEB-102",
        "rule": "recent"
      },
      "phone": {
        "value": "9123456789",
        "source_record_id": "WEB-102",
        "rule": "recent"
      },
      "address": {
        "value": "8 Lake Rd, Kolkata",
        "source_record_id": "WEB-102",
        "rule": "recent"
      },
      "postcode": {
        "value": "700029",
        "source_record_id": "CRM-002",
        "rule": "source"
      },
      "dob": {
        "value": "1985-11-03",
        "source_record_id": "WEB-102",
        "rule": "complete"
      },
      "source_record_ids": [
        "CRM-002",
        "WEB-102"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    },
    {
      "master_id": "M-000004",
      "name": {
        "value": "Mira Das",
        "source_record_id": "CRM-003",
        "rule": "source"
      },
      "email": {
        "value": "mira.das@example.com",
        "source_record_id": "CRM-003",
        "rule": "recent"
      },
      "phone": {
        "value": "+91 90000 11111",
        "source_record_id": "CRM-003",
        "rule": "recent"
      },
      "address": {
        "value": "4 Salt Lake, Kolkata",
        "source_record_id": "CRM-003",
        "rule": "recent"
      },
      "postcode": {
        "value": "700091",
        "source_record_id": "CRM-003",
        "rule": "source"
      },
      "dob": {
        "value": "1992-07-21",
        "source_record_id": "CRM-003",
        "rule": "complete"
      },
      "source_record_ids": [
        "CRM-003"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    },
    {
      "master_id": "M-000005",
      "name": {
        "value": "Sanjay Roy",
        "source_record_id": "CRM-004",
        "rule": "source"
      },
      "email": {
        "value": "s.roy@example.com",
        "source_record_id": "WEB-104",
        "rule": "recent"
      },
      "phone": {
        "value": "9888877777",
        "source_record_id": "WEB-104",
        "rule": "recent"
      },
      "address": {
        "value": "20 New Town, Kolkata",
        "source_record_id": "WEB-104",
        "rule": "recent"
      },
      "postcode": {
        "value": "700156",
        "source_record_id": "CRM-004",
        "rule": "source"
      },
      "dob": {
        "value": "1978-03-09",
        "source_record_id": "WEB-104",
        "rule": "complete"
      },
      "source_record_ids": [
        "CRM-004",
        "WEB-104"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    },
    {
      "master_id": "M-000006",
      "name": {
        "value": "Priya Sen",
        "source_record_id": "CRM-005",
        "rule": "source"
      },
      "email": {
        "value": "priya.sen@example.com",
        "source_record_id": "WEB-105",
        "rule": "recent"
      },
      "phone": {
        "value": "9333322222",
        "source_record_id": "WEB-105",
        "rule": "recent"
      },
      "address": {
        "value": "9 Ballygunge Pl",
        "source_record_id": "WEB-105",
        "rule": "recent"
      },
      "postcode": {
        "value": "700019",
        "source_record_id": "CRM-005",
        "rule": "source"
      },
      "dob": {
        "value": "1988-09-30",
        "source_record_id": "WEB-105",
        "rule": "complete"
      },
      "source_record_ids": [
        "CRM-005",
        "WEB-105"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    },
    {
      "master_id": "M-000007",
      "name": {
        "value": "Amit Ghosh",
        "source_record_id": "CRM-006",
        "rule": "source"
      },
      "email": {
        "value": "amit.ghosh@example.com",
        "source_record_id": "WEB-106",
        "rule": "recent"
      },
      "phone": {
        "value": "9555566666",
        "source_record_id": "WEB-106",
        "rule": "recent"
      },
      "address": {
        "value": "3 Howrah Rd",
        "source_record_id": "WEB-106",
        "rule": "recent"
      },
      "postcode": {
        "value": "711101",
        "source_record_id": "CRM-006",
        "rule": "source"
      },
      "dob": {
        "value": "1991-01-05",
        "source_record_id": "WEB-106",
        "rule": "complete"
      },
      "source_record_ids": [
        "CRM-006",
        "WEB-106"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    },
    {
      "master_id": "M-000008",
      "name": {
        "value": "Nisha Kapoor",
        "source_record_id": "CRM-007",
        "rule": "source"
      },
      "email": {
        "value": "nisha.k@example.com",
        "source_record_id": "WEB-107",
        "rule": "recent"
      },
      "phone": {
        "value": "9666611111",
        "source_record_id": "WEB-107",
        "rule": "recent"
      },
      "address": {
        "value": "7 Alipore, Kolkata",
        "source_record_id": "WEB-107",
        "rule": "recent"
      },
      "postcode": {
        "value": "700027",
        "source_record_id": "CRM-007",
        "rule": "source"
      },
      "dob": {
        "value": "1994-06-11",
        "source_record_id": "WEB-107",
        "rule": "complete"
      },
      "source_record_ids": [
        "CRM-007",
        "WEB-107"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    },
    {
      "master_id": "M-000009",
      "name": {
        "value": "Arjun Mehta",
        "source_record_id": "CRM-008",
        "rule": "source"
      },
      "email": {
        "value": "arjun.mehta@example.com",
        "source_record_id": "CRM-008",
        "rule": "recent"
      },
      "phone": {
        "value": "+91 94444 33333",
        "source_record_id": "CRM-008",
        "rule": "recent"
      },
      "address": {
        "value": "11 Camac Street",
        "source_record_id": "CRM-008",
        "rule": "recent"
      },
      "postcode": {
        "value": "700017",
        "source_record_id": "CRM-008",
        "rule": "source"
      },
      "dob": {
        "value": "1989-02-14",
        "source_record_id": "CRM-008",
        "rule": "complete"
      },
      "source_record_ids": [
        "CRM-008"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    },
    {
      "master_id": "M-000010",
      "name": {
        "value": "Kavita Rao",
        "source_record_id": "CRM-009",
        "rule": "source"
      },
      "email": {
        "value": "kavita.rao@example.com",
        "source_record_id": "WEB-109",
        "rule": "recent"
      },
      "phone": {
        "value": "9222244444",
        "source_record_id": "WEB-109",
        "rule": "recent"
      },
      "address": {
        "value": "2 Behala",
        "source_record_id": "WEB-109",
        "rule": "recent"
      },
      "postcode": {
        "value": "700034",
        "source_record_id": "CRM-009",
        "rule": "source"
      },
      "dob": {
        "value": "1993-12-01",
        "source_record_id": "WEB-109",
        "rule": "complete"
      },
      "source_record_ids": [
        "CRM-009",
        "WEB-109"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    },
    {
      "master_id": "M-000011",
      "name": {
        "value": "Dev Patel",
        "source_record_id": "CRM-010",
        "rule": "source"
      },
      "email": {
        "value": "dev.patel@example.com",
        "source_record_id": "CRM-010",
        "rule": "recent"
      },
      "phone": {
        "value": "+91 91111 22222",
        "source_record_id": "CRM-010",
        "rule": "recent"
      },
      "address": {
        "value": "5 Tollygunge",
        "source_record_id": "CRM-010",
        "rule": "recent"
      },
      "postcode": {
        "value": "700033",
        "source_record_id": "CRM-010",
        "rule": "source"
      },
      "dob": {
        "value": "1987-08-19",
        "source_record_id": "CRM-010",
        "rule": "complete"
      },
      "source_record_ids": [
        "CRM-010"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    },
    {
      "master_id": "M-000012",
      "name": {
        "value": "Rahul Bannerjee",
        "source_record_id": "CRM-012",
        "rule": "source"
      },
      "email": null,
      "phone": {
        "value": "+91 91234 56789",
        "source_record_id": "CRM-012",
        "rule": "recent"
      },
      "address": {
        "value": "8 Lake Road, Kolkata",
        "source_record_id": "CRM-012",
        "rule": "recent"
      },
      "postcode": {
        "value": "700029",
        "source_record_id": "CRM-012",
        "rule": "source"
      },
      "dob": {
        "value": "1986-11-03",
        "source_record_id": "CRM-012",
        "rule": "complete"
      },
      "source_record_ids": [
        "CRM-012"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    },
    {
      "master_id": "M-000013",
      "name": {
        "value": "Arjun Mehta",
        "source_record_id": "WEB-108",
        "rule": "source"
      },
      "email": {
        "value": "arjun.m@example.com",
        "source_record_id": "WEB-108",
        "rule": "recent"
      },
      "phone": {
        "value": "9444433333",
        "source_record_id": "WEB-108",
        "rule": "recent"
      },
      "address": {
        "value": "11 Camac St",
        "source_record_id": "WEB-108",
        "rule": "recent"
      },
      "postcode": {
        "value": "700017",
        "source_record_id": "WEB-108",
        "rule": "source"
      },
      "dob": {
        "value": "1989-02-14",
        "source_record_id": "WEB-108",
        "rule": "complete"
      },
      "source_record_ids": [
        "WEB-108"
      ],
      "consent_values": [
        "active"
      ],
      "consent_policy_note": "conflicting consent must be resolved by policy; this lab does not infer permission from survivorship"
    }
  ]
}
````

**Reproducibility note:** the report file is generated by `python run_lab.py`; timestamps and IDs in the synthetic fixture are fixed. Do not interpret fixture metrics as a production benchmark.
