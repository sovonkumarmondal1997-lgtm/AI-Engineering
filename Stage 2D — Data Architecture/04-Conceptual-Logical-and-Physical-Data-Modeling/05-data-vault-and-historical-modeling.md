# Data Vault and Historical Modeling

> **Module:** Stage 2D — Data Architecture, Module 4: Conceptual, Logical and Physical Data Modeling, Topic 5  
> **Level:** Beginner → Intermediate → Advanced  
> **Primary outcome:** Design and explain a defensible historical model, demonstrate point-in-time retrieval, and choose between Data Vault and simpler alternatives using explicit requirements and trade-offs.

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Explain why history is required for audit, regulatory evidence, reproducibility, error investigation and point-in-time reporting.
2. Distinguish current state, history of changes, and as-reported history (what the organisation believed at a point in time, including later corrections).
3. Explain the purpose and characteristics of Data Vault and correctly assign business keys, relationships and descriptive attributes to hubs, links and satellites.
4. Design a small Customer–Account vault for Northbridge Bank's core banking, cards and CRM sources.
5. Explain why business keys are separated from descriptive attributes and how source-qualified, composite or unstable keys affect identity.
6. Interpret load timestamps, record-source metadata and lineage without claiming they prove more than they do.
7. Separate satellites by source and/or rate of change when that improves isolation, loading or maintenance.
8. Describe a correct point-in-time retrieval strategy and explain the difference between business-valid time and record/load time.
9. Identify what a vault preserves and what it cannot infer automatically, including intent, missing history, source deletion semantics and cross-source identity.
10. Compare Data Vault with append-only lake/lakehouse history, relational history tables, Type 2 dimensions and event logs.
11. Explain how a consumer-oriented dimensional model can be derived from historical structures without making analysts query the vault directly.
12. Produce a decision record that recommends or rejects Data Vault for a stated scenario and documents at least one simpler alternative.

## 2. Why the topic matters in real-world Data Architecture

Operational systems are usually designed to serve current transactions, not to preserve every historical state needed for analytics, investigation or audit. A customer record may show only the latest address. A CRM correction may arrive weeks after the address was effective. A card system may identify a customer differently from core banking. If a report is rebuilt later from only current records, it may not reproduce what a decision-maker saw at the time.

Historical modeling makes these questions answerable—provided the source evidence was actually captured:

- **What is true now according to the selected rule and sources?**
- **What changed, and what source supplied the change?**
- **What did the bank's integrated data platform know by a given date?**
- **What did the bank later learn was valid for an earlier business date?**
- **Can a past report be reproduced using the data, rules and mappings available then?**

These questions are related but not identical. A model that retains received source states may show what the platform received; it does not automatically prove what a customer intended, what a source omitted, or whether two source identifiers represent the same person.

### 2.1 Three distinct historical views

| View | Question answered | Example | Important limitation |
|---|---|---|---|
| **Current state** | What is the latest accepted value under a defined selection rule? | CRM currently lists a customer's address as `12 Lake Road`. | “Latest” depends on source priority, freshness and conflict rules. |
| **History of changes** | Which states or change observations were captured over time? | The address changed from `10 Main Street` to `12 Lake Road`. | A missing source extract or unlogged update cannot be reconstructed merely by adding a history table. |
| **As-reported / as-known history** | What did the platform have recorded or believe by a past cutoff? | On 31 January, the platform had received `10 Main Street`; a retroactive correction arrived on 10 February. | Requires retained prior observations and a clear definition of “known by”; business-valid time alone is insufficient. |

A fourth useful question is **what was valid in the business at a particular time, based on the evidence available at another time**. That is the foundation of bi-temporal reasoning, introduced in Section 6.

### 2.2 Data Vault in one paragraph

Data Vault is a modeling approach for integrating data from multiple sources while preserving source identity, relationships and descriptive history. Its core constructs are **hubs** for business keys, **links** for relationships among business keys, and **satellites** for descriptive attributes and their changes. Load metadata and record-source metadata support traceability. The design can accommodate source change and parallel ingestion, but creates additional tables, joins, orchestration and consumer complexity. It is an option—not a universal default—and it does not, by itself, solve master-data identity, data quality, source completeness or business-valid-time semantics.

## 3. Prerequisite knowledge

The roadmap prerequisites are Modules 2–4 in this topic series, plus Stage 2D Topic 2 on data-platform layers and Topic 6 on change events.

Before continuing, make sure you can:

- identify entities, attributes, relationships, keys, cardinality and constraints;
- explain normalization and why descriptive facts should not be mixed indiscriminately with identity;
- state a dimensional fact table's grain and explain why a consumer model differs from an integration model;
- distinguish raw/landing, integrated and serving/consumption responsibilities;
- reason about change events and source-system behavior at a basic level.

If any prerequisite is weak, revisit the corresponding topic rather than memorizing Data Vault terminology without understanding the underlying modeling problem.

### 3.1 Terminology used in this lesson

- **Business key (BK):** a source- or domain-recognized identifier used to identify a business concept within a defined scope. It is not automatically globally unique or immutable.
- **Surrogate key / hash key:** a generated technical identifier used to join structures. A hash key is one implementation option; it is not a substitute for defining correct business-key semantics.
- **Load timestamp (`LoadTS`):** the time the integration process recorded/loaded an observation, using a documented clock and time zone.
- **Record source (`RecordSource`):** an identifier for the system, feed, file, topic or extract that supplied the record. A source name alone may be too coarse for audit needs.
- **Valid time:** when the fact is asserted to apply in the business domain.
- **Record/system time:** when the platform recorded or believed the assertion. This lesson uses `LoadTS` as a simple record-time proxy, while noting that production systems may need separate ingestion, processing and commit timestamps.
- **Satellite version:** a captured descriptive state for a hub or link, normally with load metadata and a source reference. A version is not necessarily a complete business event.

## 4. Beginner-level learning sequence

### 4.1 Start with the business question, not the table pattern

Consider Northbridge Bank. Core banking manages accounts and may hold a legal/customer address. Cards manages card relationships and may hold a card-service contact address. CRM manages interaction preferences and contact details. Their identifiers, update schedules and definitions may differ.

Suppose a regulator asks, “What customer address did the reporting platform have on 31 January, and what address did the bank later determine was effective on that date?” A current-state customer table cannot answer both questions. The architecture must retain the observations and their relevant time semantics.

### 4.2 The three core constructs

#### Hub: identity key for a business concept

A hub records a unique business key for a concept such as Customer or Account, plus technical/load metadata. It is intentionally not a wide row of mutable descriptive attributes.

Illustrative columns:

| Column | Purpose |
|---|---|
| `CustomerHK` | Stable technical join key generated under a documented algorithm. |
| `CustomerBK` | Business key in the explicitly defined key scope. |
| `LoadTS` | When this key was first recorded in this hub. |
| `RecordSource` | Source or feed that introduced the key. |

A hub generally records the existence of a key; it does not establish that the key is a globally unique human identity, that the person is active, or that the source's data is correct.

#### Link: relationship among business keys

A link records an association among hubs. For example, `CustomerAccount` records that a customer is associated with an account. Relationship attributes such as the customer's role on an account may be stored in a satellite attached to the link if they change over time or need source-specific history.

A link should represent a clearly defined relationship grain. In the simple `CustomerAccount` example, the grain is one source-scoped customer identity associated with one source-scoped account identity; the pair must be unique under that relationship definition. If the same customer/account pair can have multiple simultaneous relationship instances (for example, separately governed legal roles or independently effective agreements), the pair alone is not a sufficient key: model the distinct relationship type/instance in the link key or use a separate link, according to the business semantics. If a role is a single changing attribute of one relationship, a link satellite can historize it. Joint ownership, authorized-user status and beneficial ownership must not be collapsed into one ambiguous relationship without a documented rule.

#### Satellite: descriptive state and its history

A satellite stores descriptive attributes for a hub or link, alongside load and source metadata. Examples include customer name/address, account status/product, or a customer-account role. A new version is captured when the relevant descriptive state changes according to the chosen change-detection policy.

A satellite may be separated by source or by rate of change so that a frequent CRM preference change does not force unrelated core-banking attributes to be copied into every version. Satellite splits are a design decision: they add joins and must preserve a clear attribute ownership and temporal contract. Define a physical uniqueness rule for satellite versions—for example, parent hash key plus a sufficiently precise load/record timestamp, with a source sequence or deterministic tie-breaker where multiple versions can arrive in one timestamp. Do not assume timestamp precision alone guarantees uniqueness; preserve event/run identifiers when ordering or replay matters.

### 4.3 Place each element in the right construct

| Business element | Likely construct | Why |
|---|---|---|
| Customer number in a defined source/key scope | Customer hub business key | Identity reference, not a descriptive value. |
| Account number in a defined source/key scope | Account hub business key | Identity reference for an account. |
| Customer is an owner of an account | CustomerAccount link | Relationship between two business concepts. |
| Customer legal name and address received from CRM | CRM customer satellite | Descriptive attributes with source-specific history. |
| Account product/status received from core banking | Core account satellite | Descriptive account state from its owning source. |
| Owner/authorized-user role on an account | CustomerAccount link satellite, if in scope | Describes the relationship rather than the customer or account alone. |
| Card-to-account association | A separate link if the card/account relationship is modeled in scope | Do not overload CustomerAccount to represent a different relationship. |

### 4.4 Why separate business keys from descriptive attributes?

Identity and description change for different reasons. A customer may change address many times while the source customer number remains the same. If address, name and segment were embedded in the hub, every descriptive change would blur the hub's identity role and complicate key uniqueness. Separating them means:

1. the hub represents the scoped business key;
2. satellites preserve changing descriptive observations;
3. different sources can contribute different attribute sets without forcing a single wide record;
4. the platform can distinguish a new key from a new description of an existing key.

This separation does **not** mean the business key can never change. Key stability, reuse and cross-system identity require explicit policies, covered in Sections 5 and 6.

### 4.5 First exercise

For each item below, classify it as a hub key, link, hub satellite, link satellite, or a decision that needs clarification:

1. CRM customer number `C-1042`.
2. Account `A-9001`.
3. Customer `C-1042` is a joint owner of `A-9001`.
4. CRM email address.
5. The role “joint owner” becomes “authorized user” on a later date.
6. A card identifier is associated with an account.

**Self-check:** 1 and 2 are candidate hub keys within their declared key scopes; 3 is a CustomerAccount relationship; 4 is a customer descriptive attribute; 5 is a changing relationship attribute; 6 is a distinct card-account relationship. Item 1 is not enough to assert that the same person in core banking has the same identity.

## 5. Intermediate-level learning sequence

### 5.1 Northbridge Bank: define the key scope before drawing tables

Assume the three source systems provide these identifiers:

| Source | Source customer key | Example attributes supplied | Important caveat |
|---|---|---|---|
| Core banking | `CB-CustomerNo` | Legal name, KYC address, customer status | A number may be recycled after closure unless the source guarantees otherwise. |
| Cards | `CardCustomerId` | Card-service status, contact preference, card-account relationship | One card-system identity may be a proxy or sub-record, not necessarily a unique natural person. |
| CRM | `CRMContactId` | Preferred name, email, contact address, interactions | A CRM contact may be a duplicate, household contact or prospect. |

The example uses source-qualified business keys such as `CORE|C-1042`, `CARDS|P-771` and `CRM|C-1042`. This prevents accidental collisions when different systems reuse the same literal identifier. The separator and normalization rules must be unambiguous; if key components can contain the separator, use an escaped/length-prefixed encoding or structured key fields.

**Critical distinction:** source qualification solves a namespace collision; it does not resolve identity. `CORE|C-1042` and `CRM|C-1042` remain separate source identities until a governed identity-resolution process establishes a relationship between them. Do not merge them merely because the strings look alike, names match, or addresses match.

If the architecture needs a canonical enterprise customer, define the canonical identifier and mapping/survivorship process separately. That work belongs with master-data and identity-resolution governance. The vault can retain the source identities and the evidence of mappings; it cannot infer the correct person mapping automatically.

### 5.2 Coherent logical model

The following is a simplified teaching model. Exact key-generation, physical types and platform-specific implementation are deferred to physical design.

```text
H_Customer
  CustomerHK (technical key)
  CustomerBK (source-qualified business key)
  LoadTS
  RecordSource

H_Account
  AccountHK (technical key)
  AccountBK (source-qualified business key)
  LoadTS
  RecordSource

L_CustomerAccount
  CustomerAccountHK (technical key)
  CustomerHK
  AccountHK
  LoadTS
  RecordSource

S_Customer_CRM
  CustomerHK
  LoadTS
  RecordSource
  PreferredName
  Email
  ContactAddress
  ValidFrom (only if supplied/defined by source)
  SourceChangeId (if available)

S_Customer_Core
  CustomerHK
  LoadTS
  RecordSource
  LegalName
  KYCAddress
  CustomerStatus
  ValidFrom (only if supplied/defined by source)
  SourceChangeId (if available)

S_Account_Core
  AccountHK
  LoadTS
  RecordSource
  ProductCode
  AccountStatus
  OpenDate
  CloseDate (if provided and semantically defined)

S_CustomerAccount_Core
  CustomerAccountHK
  LoadTS
  RecordSource
  RelationshipRole
  ValidFrom (if supplied/defined)
  ValidTo (if supplied/defined)
```

`H_Customer` and `H_Account` contain identity keys, not the changing names, addresses, status or product attributes. `L_CustomerAccount` holds the customer–account association. Customer descriptive data is separated into source-specific satellites. Account details belong on account satellites. The role belongs to the relationship satellite because it describes how the customer relates to the account.

The cards system may require a separate `H_Card` and `L_CardAccount` if card identity and card-account association are in the agreed scope. These are sensible extensions, but the minimum roadmap exercise is Customer, Account, CustomerAccount and the relevant satellites. Do not add constructs merely to make the diagram look more elaborate.

### 5.3 Load metadata and record source: useful, but not magical

Every modeled record/version should have enough metadata to trace it to the ingestion context. At minimum, the roadmap calls for a load timestamp and record source.

| Metadata | What it supports | What it does not prove by itself |
|---|---|---|
| `LoadTS` | Ordering and cutoff by the time the platform loaded/recorded a row, if clocks and semantics are controlled. | When the business fact became true; when the source originally changed it; completeness of history; a trustworthy legal timestamp. |
| `RecordSource` | Identifying the supplying source/feed at a defined granularity. | The exact file, API page, partition, offset or batch unless the value points to that lineage. |
| `SourceChangeId` / source sequence, if available | Correlation with a source change event or extract record. | Correctness or completeness of source history. |
| `IngestionRunId` / file URI / topic-partition-offset, if retained | Trace from a vault row to a concrete load run or source artifact. | That the source artifact itself was accurate or authorized. |
| Hash diff / payload checksum, optional implementation detail | Efficient change detection or integrity checks when implemented consistently. | Business meaning, source authenticity, or a replacement for version history. |

For audit-grade lineage, maintain a load-run register that records source identifier, artifact or extraction window, extraction/ingestion times, run ID, code/version, row counts, rejects, checksums where appropriate, and reconciliation outcomes. Store sensitive source payloads only under applicable access, retention and privacy controls.

A `RecordSource='CRM'` field is helpful but often too coarse for an auditor asking which file or API response supplied a value. Record the level of lineage required by the business and regulation, and test that a row can actually be traced end-to-end.

### 5.4 Source differences and satellite design

Different systems may supply different attributes for what appears to be the same customer. Even after identity is resolved, values may disagree. For example, core banking's KYC address and CRM's preferred contact address can both be correct because they answer different business questions. Do not overwrite one with the other just because one source is newer.

A robust integration contract should define:

- attribute meaning and ownership (legal/KYC address versus preferred contact address);
- source-specific satellite boundaries;
- key scope and identity mapping policy;
- source priority or survivorship rules for a **derived consumer view**, if one is needed;
- how null, missing, withdrawn and explicitly cleared values differ;
- how source freshness and late arrival are represented;
- what to do when a source changes schema or semantics.

Separate satellites by source when sources have distinct attribute ownership, update schedules, security boundaries or lineage needs. Separate satellites by rate of change when a frequently changing group should not force unrelated attributes into new versions. Avoid both extremes: a single giant satellite can create noisy versions; one satellite per column can create unnecessary joins and operational overhead.

### 5.5 Capturing changes

A common change-capture pattern is:

1. ingest the source record or event and retain its lineage;
2. normalize the key using a documented, versioned rule;
3. identify the hub/link key and reject or quarantine ambiguous identities rather than silently merging them;
4. compare the descriptive payload with the prior captured state for that source and satellite;
5. insert a new satellite version when a meaningful change is detected, or record the observation separately if repeated identical observations are audit-significant;
6. preserve load metadata and any valid-time/source-change metadata available;
7. reconcile source counts and exceptions; document what the pipeline could not determine.

Many Data Vault implementations use hashes for technical keys and/or change detection. Hashing is an implementation choice, not the definition of the model. Canonicalization, null handling, character encoding, field ordering, algorithm version and collision risk must be understood. Do not assume hash equality proves business identity or that different hashes necessarily represent meaningful business changes.

A change-driven satellite often records only changed states. It does not automatically record every unchanged daily observation. If the audit question requires proof that a source was checked and returned the same value on each day, retain an observation/snapshot or source-run evidence in addition to change-only history.

### 5.6 Address history example: load time and valid time

Assume CRM supplies a customer address and explicitly states its business effective date. The values below are illustrative, not real Northbridge data.

| LoadTS (when platform received it) | ValidFrom (when CRM says it applies) | Address | Interpretation |
|---|---|---|---|
| `2026-01-05 09:00 UTC` | `2026-01-01` | `10 Main Street` | Initial address received on 5 January; source says effective from 1 January. |
| `2026-02-10 14:00 UTC` | `2026-01-01` | `12 Lake Road` | A retroactive correction received on 10 February; CRM now says the corrected address was effective from 1 January. |

The second row is not saying the customer moved on 10 February. It says the platform received a correction on that date about an earlier effective date. The two time dimensions answer different questions.

**Question A — What address did the platform have recorded by 31 January?** Use the load/record-time cutoff `LoadTS <= 2026-01-31 23:59:59 UTC`. The correction had not yet arrived, so the captured address is `10 Main Street`.

**Question B — Based on data received by 15 February, what address did CRM say was valid on 31 January?** First restrict observations to `LoadTS <= 2026-02-15 23:59:59 UTC`; then apply the source's business-valid-time rule for `2026-01-31`. The latest known correction says `12 Lake Road`, valid from 1 January.

Those are both legitimate answers to different questions. Never silently rewrite the first answer using the second and then claim it represents what was known on 31 January.

### 5.7 Point-in-time retrieval: logic and pseudo-SQL

The exact query depends on the satellite's time contract and whether the source supplies effective intervals or only point-in-time snapshots. For this worked example, treat each address as a temporal assertion with `ValidFrom`/`ValidTo` for business-valid time and `RecordFrom`/`RecordTo` for the interval during which the platform treated that assertion as its recorded belief. `RecordFrom` can be based on `LoadTS`; `RecordTo` may be derived in a view from the next superseding assertion or stored under a documented temporal policy. It is **not** the same as `ValidTo`. If two assertions can share a `LoadTS`, define a deterministic source sequence/record identifier and use it in supersession ordering; timestamp ordering alone is ambiguous in that case.

To ask what was known by a cutoff and what was valid on a business date, apply both interval predicates:

```sql
-- Illustrative pseudo-SQL over a bi-temporal assertion view.
-- :known_at = '2026-02-15 23:59:59 UTC'
-- :valid_at = '2026-01-31'
SELECT
    CustomerHK,
    ContactAddress,
    ValidFrom,
    ValidTo,
    RecordFrom,
    RecordTo,
    RecordSource
FROM V_CustomerAddress_Bitemporal
WHERE RecordFrom <= :known_at
  AND (RecordTo > :known_at OR RecordTo IS NULL)
  AND ValidFrom <= :valid_at
  AND (ValidTo > :valid_at OR ValidTo IS NULL);
```

Under the illustrative two-row timeline, the first assertion has `RecordFrom = 2026-01-05` and `RecordTo = 2026-02-10`; the corrected assertion has `RecordFrom = 2026-02-10` and an open `RecordTo`. Both assert `ValidFrom = 2026-01-01` and an open `ValidTo`. With `known_at = 31 January`, only `10 Main Street` is eligible. With `known_at = 15 February`, only the corrected `12 Lake Road` assertion is eligible for `valid_at = 31 January`.

This query is appropriate only when the temporal view's supersession and interval rules are implemented correctly. A source correction that affects only one of several effective periods must supersede only the relevant assertion/interval; it must not erase unrelated intervals. If the source provides only change snapshots, the pipeline must derive intervals from source semantics and ordered observations—or state that the available evidence cannot answer the question. Never derive business `ValidTo` from `LoadTS` merely because one is easier to compute. Preserve the prior record-time belief so an earlier as-known query remains reproducible.
**Important:** `LoadTS` is the platform's load/record time, not necessarily the exact time the source changed the value. If source event time, extraction time and load time differ, retain separate fields rather than pretending they are interchangeable.

**Worked result check (half-open intervals).** Use `RecordFrom <= known_at < RecordTo` and `ValidFrom <= valid_at < ValidTo`, treating a null end as open-ended. The illustrative assertions therefore yield:

| `known_at` cutoff | `valid_at` | Expected rows | Expected address | Reason |
|---|---|---:|---|---|
| 2026-01-31 23:59:59 UTC | 2026-01-31 | 1 | `10 Main Street` | The 10 February correction had not been recorded. |
| 2026-02-15 23:59:59 UTC | 2026-01-31 | 1 | `12 Lake Road` | The corrected assertion is known and is effective from 1 January. |
| 2026-02-15 23:59:59 UTC | 2026-03-01 | 1 | `12 Lake Road` | The example's corrected valid interval remains open-ended. |

These results depend on the explicitly stated assumption that the correction replaces the prior assertion for the entire effective interval beginning 1 January. If it only corrects a subset of dates, split the valid-time interval and supersede only that portion. The two-row example does not demonstrate a real source's completeness; it demonstrates the temporal query contract under the stated assumptions.

## 6. Advanced-level learning sequence

### 6.1 History of change versus history of belief

A change-history model answers which values were captured and when the system captured them. An as-reported history asks what the platform had recorded or reported by a past cutoff. A bi-temporal model additionally distinguishes business-valid time from record/system time.

| Time concept | Meaning | Example |
|---|---|---|
| Business-valid time | Period when the source asserts a fact applied in the business. | Address valid from 1 January. |
| Source event/change time | Time the source says it changed or emitted the change. | CRM audit event created 2 February. |
| Extraction/observation time | Time the integration read the source or artifact. | API extract taken 3 February. |
| Load/record time | Time the warehouse/vault recorded the row. | Row committed at 4 February 02:15 UTC. |
| Report/decision time | Time a consumer ran a report or made a decision. | Regulatory report produced 31 January using then-available data. |

Do not collapse these into one `DateUpdated` column. One timestamp is insufficient when a late-arriving correction, retroactive effective date, source delay or reprocessing could change the answer to “what was valid then?” versus “what did we know then?”

Bi-temporal requirements are not satisfied merely by storing `ValidFrom` and `LoadTS`. Define both dimensions, their interval semantics, the treatment of corrections/retractions, and a tested query contract. A Data Vault satellite commonly preserves load-time versions; valid-time columns and full bi-temporal behavior require explicit design when the business needs them.

### 6.2 Deletions, corrections, retractions and missing records

A missing row is ambiguous. It may mean a source deletion, a filtered extract, an outage, a changed access permission, a late feed, a failed pipeline or an actual business removal. Do not infer deletion simply because a record did not appear in today's extract unless the source contract says the extract is a complete snapshot and the reconciliation succeeded.

Choose and document a source-specific deletion strategy:

- **Explicit delete/tombstone event:** retain the event, source key, event time, load time and lineage. A satellite can capture status/deletion metadata if that fits the model; an event/observation structure may be appropriate where deletion evidence is central.
- **Complete snapshot comparison:** infer disappearance only after confirming snapshot completeness, scope, successful run and reconciliation. Record the inference and its evidence, not merely a fabricated source delete timestamp.
- **Soft deletion/status:** preserve the source's status and effective semantics; do not equate inactive, closed, suppressed and deleted.
- **Physical erasure/privacy request:** historical retention is constrained by legal, contractual and privacy obligations. Data Vault is not a reason to retain personal data indefinitely; define lawful retention, access, redaction/tokenization and deletion propagation policies.

**Correction** means an earlier value is replaced or amended; **retraction** means a previous assertion is withdrawn; **deletion** may mean a business entity ended or a source record was removed. These are different operations. Retain the received evidence and record the interpretation. The model cannot infer intent unless the source or a governed process supplies it.

### 6.3 Reused and unstable business keys

Suppose core banking uses customer number `C-1042`, closes the old customer, then reuses `C-1042` for a different person. A hub keyed only by `C-1042` would conflate two real-world identities if reuse is allowed by the source. The resulting satellites and links could attach the second person's attributes to the first person's history.

Defenses must follow source semantics, not guesswork:

1. establish whether the source guarantees a key is never reused;
2. if not, add a reliable source-provided generation/instance identifier or scope the key by a valid lifecycle identifier;
3. if no disambiguating field exists, quarantine the ambiguous reuse and obtain a governed identity rule—do not manufacture certainty;
4. retain the original source key and the mapping rule/version used at ingestion;
5. test key reuse and re-open/re-issue scenarios before declaring the hub stable.

Composite keys may be necessary, for example `(SourceSystem, CustomerNumber, CustomerGeneration)`. The combination must be semantically unique and reproducibly normalized. A generated hash of an ambiguous composite does not repair the ambiguity. Hash keys also require a stable canonical serialization (including null markers, type/encoding rules and component boundaries); do not concatenate components ambiguously (for example, `AB|C` versus `A|B|C`) or change canonicalization without a controlled migration/version policy. If a business identifier itself changes, model the new identifier and a governed relationship/mapping to the enduring entity when evidence supports it; do not assume the old and new keys are the same person without a rule.

### 6.4 Identity resolution and cross-source collisions

There are three different problems:

1. **Namespace collision:** two systems use the same string for unrelated entities. Source-qualified keys can prevent a technical collision.
2. **Duplicate identity:** two source keys represent the same real-world customer. This requires identity resolution and evidence.
3. **Conflicting attributes:** two sources report different values. This requires semantic definitions, ownership and/or survivorship rules.

Data Vault provides structures to retain source keys, relationships and observations. It does not automatically solve the second or third problem. If Northbridge establishes that `CORE|C-1042` and `CRM|C-1042` refer to the same enterprise customer, retain the governed mapping and its effective/record history. If the match is uncertain, preserve separate source identities and the unresolved status rather than prematurely collapsing them.

### 6.5 Satellites by source and rate of change

Satellite decomposition is a trade-off between change isolation and query complexity.

| Split strategy | Useful when | Cost / risk |
|---|---|---|
| By source | Attributes have different owners, meanings, update patterns, security requirements or lineage. | Consumers must understand which source satellite answers which question. |
| By rate of change | One attribute group changes much more frequently than another. | More joins and the risk that independently changing attributes are incorrectly treated as one synchronized state. |
| By both source and rate | A source has a distinct high-frequency group and the workload justifies isolation. | More tables, pipelines, metadata and testing; avoid splitting without a measurable reason. |
| One wide satellite | Attributes have similar ownership, lifecycle and change cadence. | Small changes can create broad versions; conflicting source semantics can be mixed. |

Satellite design must declare whether a row represents a full descriptive state, a changed attribute group, a source observation or an event. Point-in-time joins depend on that contract. A change in one satellite does not imply that every other satellite was re-observed at the same instant.

### 6.6 Lineage, auditability and reproducibility

A historical structure is useful for audit only if it is possible to explain how a row got there. A defensible lineage chain should connect:

`business question → consumer model/report → transformation version → vault row/version → load run → source artifact/event → source system and extraction window`.

Maintain operational controls for failed loads, duplicate delivery, out-of-order events, replay, late arrival, schema drift, row-count reconciliation and rejected records. Reprocessing should be idempotent or explicitly versioned so that replay does not silently create a false history. Preserve transformation/code version and relevant key-normalization/mapping versions when reproducibility requires them.

Load metadata improves traceability; it is not proof that the source's content was true or complete. An audit-ready platform also needs access controls, clock governance, retention policy, monitoring, evidence preservation and documented exception handling.

### 6.7 From vault to dimensional consumption

The vault is commonly an integration/history layer, not the analyst-facing layer. Analysts usually need stable business definitions, readable labels, known grain, conformed dimensions, measures and predictable query performance. They should not have to reconstruct every hub/link/satellite join for each report.

A downstream transformation can:

1. resolve approved identity mappings and source precedence for the specific use case;
2. choose a consistent point-in-time view of customer and account attributes;
3. derive customer/account dimensions and fact tables with explicit grain;
4. apply Type 1 or Type 2 dimension behavior where appropriate to the consumer requirement;
5. expose tested semantic definitions and document whether the report means “as was known then” or “currently corrected view of the past.”

For example, a regulatory report may need a reproducible as-reported customer dimension, while current portfolio analysis may need the latest corrected address or current segment. Those are different products and may need separate views, snapshots or versioned transformations. Do not claim a star schema can answer an as-reported question unless the required historical states and mapping rules are preserved upstream.

### 6.8 Alternatives and architectural trade-offs

Data Vault is one pattern among several. Choose the least complex approach that meets the required history, integration, lineage and consumer needs.

| Approach | Strengths | Typical gaps / risks | Consumer implications |
|---|---|---|---|
| **Data Vault (hubs, links, satellites)** | Explicit identity/relationship/descriptive separation; source-oriented integration; can preserve received states and lineage; supports incremental extension across sources. | More tables, joins, orchestration, modeling conventions and specialist skills; valid-time and identity semantics still need explicit design. | Usually requires curated downstream views or marts; raw vault queries are demanding. |
| **Append-only lake/lakehouse history** | Retains source files/events or append-only records; flexible for exploratory use; can preserve raw evidence close to source. | Raw history alone may lack canonical keys, relationship semantics, reliable deduplication, schema contracts or point-in-time query rules. Append-only does not guarantee immutability or completeness. | Analysts need transformation logic and clear contracts; quality varies unless governed. |
| **Relational history/audit tables** | Familiar SQL, constraints and straightforward current/history views for a limited domain; can be efficient for one stable application. | Cross-source integration and source-specific history may become bespoke; audit semantics can be inconsistent across systems. | Often simpler for one consumer; multiple source domains may require extensive custom joins and rules. |
| **Type 2 dimensional dimensions** | Straightforward analyst-facing history of dimension attributes; clear effective intervals and surrogate keys when modeled well. | Primarily a consumption pattern; often not a full source-integration/audit architecture; may not retain all source states or conflicting values. | Convenient for BI; less suitable as the only integration evidence layer when many sources and audit demands exist. |
| **Event logs / event sourcing** | Strong when domain events are first-class, ordered and meaningful; can reconstruct state by replay under defined semantics. | Requires complete event capture, event versioning, ordering/idempotency rules and domain ownership; snapshots/compaction may complicate reconstruction. | Consumers need projections; event payloads alone may not be a governed analytical model. |

### 6.9 Decision matrix: requirements to approach

| Scenario / requirement | Candidate approach | Benefits | Complexity | Consumer cost | Decision rationale |
|---|---|---|---|---|---|
| One stable operational source; one report; modest history needs | Relational history table or Type 2 dimension | Direct, familiar and easy to operate | Low–medium | Low for the known report | Prefer this unless cross-source integration, extensive lineage or parallel source onboarding creates a demonstrated need for a vault. |
| Core banking + cards + CRM; different keys and change rates; regulated historical evidence | Data Vault plus raw/source evidence and curated consumption models | Separates source identities and relationships; supports incremental integration and traceability | High | Medium–high unless marts/semantic views are provided | Strong candidate if evidence, source evolution and auditability justify the cost; pair with identity governance and explicit time semantics. |
| Early-stage exploratory analytics over files/events; semantics still changing | Append-only lake/lakehouse landing/history plus selective curated models | Preserves raw observations and supports discovery without prematurely imposing a full enterprise model | Low–medium initially | Medium; analysts must understand raw data | Prefer initially when requirements are unsettled; add a vault only when integration, governance and audit requirements justify it. |
| Event-driven domain with complete, authoritative business events | Event log plus projections; optionally vault for cross-domain integration | Captures meaningful transitions and supports replay when event contracts are reliable | Medium–high | Medium | Use event-centric design if events are the source of truth; do not assume events alone solve cross-source identity or analytical semantics. |
| Several systems, but no audit need, stable definitions, small team and one consumer | Relational integration/history or curated lakehouse tables | Lower operational and training cost | Low–medium | Low | Reject a vault unless a specific requirement demonstrates its incremental value. |

Use this matrix as a starting point, not a scoring substitute. Record which requirements are mandatory, which are preferences, the evidence for each, and the consequences of the rejected alternatives.

### 6.10 Three roadmap scenarios

#### Scenario A — Single-source operational reporting

A small team has one stable source system, one reporting consumer and no special requirement to reproduce historical beliefs. The source provides reliable audit fields and the business mainly needs current state plus a modest change history.

**Recommendation:** start with a relational history table or a Type 2 dimension if the requirement is analytical. A vault may add unnecessary tables, joins, load orchestration and specialist knowledge. Reconsider only if new sources, audit obligations or source-change patterns alter the requirements.

#### Scenario B — Multi-source regulated integration

Northbridge integrates core banking, cards and CRM. Source keys differ, attributes conflict or have distinct meanings, sources evolve independently, and the bank must explain what was received and what was known at a prior cutoff.

**Recommendation:** Data Vault is a credible candidate when paired with raw-source retention, load-run lineage, governed identity mapping, temporal contracts, reconciliation and downstream consumer models. It is not sufficient alone: it cannot infer intent, fill missing source history, prove source correctness or resolve duplicates without a governed process.

#### Scenario C — Exploratory analytics

A team is exploring new product data from frequently changing files and events; definitions and analytical questions are not yet stable. Immediate priorities are retaining observations, understanding the data and iterating quickly.

**Recommendation:** begin with a controlled append-only landing/history layer and a few curated analytical tables. Avoid a full vault until source integration patterns, lineage requirements and stable business concepts justify the additional modeling and operating cost. Raw append-only data still needs retention, schema, quality, access and reproducibility controls.

### 6.11 Industry exercise: Northbridge design

Deliver a concise architecture note containing:

1. A hub/link/satellite model for Customer, Account and CustomerAccount.
2. A key dictionary defining each business key's source, scope, uniqueness guarantee, reuse risk and normalization rule.
3. A satellite inventory showing attribute ownership, source, rate of change, change-detection policy and valid-time availability.
4. A metadata and lineage contract for `LoadTS`, `RecordSource`, load-run identifier and source artifact/change identifier.
5. Pseudo-SQL or precise query logic for the address as of 31 March, including the “known by” cutoff if as-reported history is required.
6. A description of the downstream dimensional model and the business question it serves; do not model the entire mart in this exercise.
7. A decision record comparing Data Vault with at least one simpler alternative.

## 7. Industry-application exercises

Complete these exercises in order. Keep the assumptions visible; do not hide unresolved source semantics inside a diagram.

### Exercise 1 — Classify and model

Given customer number, account number, legal name, contact address, account product, ownership role and a card-account relationship, assign each to a hub, link or satellite. State the grain and business meaning of every link and satellite.

**Acceptance test:** an independent reviewer can explain why each attribute belongs to the selected construct and identify any relationship whose meaning is ambiguous.

### Exercise 2 — Key collisions and identity

Core banking and CRM both supply `C-1042`, but no identity mapping is supplied. Create source-qualified keys and explain why that prevents a namespace collision without proving that the keys refer to the same person. Specify the evidence and governance required before creating an enterprise-customer mapping.

**Acceptance test:** no silent merge occurs; unresolved identity is visible and testable.

### Exercise 3 — Point-in-time address

Use the two-row address example in Section 5.6. Answer both questions: (a) what address was recorded by 31 January, and (b) what address was later asserted to be valid on 31 January using data received by 15 February. Write the cutoff predicates and explain why the answers differ.

**Acceptance test:** the as-known query excludes the 10 February correction; the later-known query includes it and uses its business-valid date.

### Exercise 4 — Deletion and correction

A CRM record disappears from an extract. List at least four possible explanations and define what evidence would allow the pipeline to treat it as a deletion. Then handle an explicit retroactive correction without overwriting the earlier as-known state.

**Acceptance test:** absence from a partial or failed extract is not treated as a source deletion; correction and deletion have distinct semantics.

### Exercise 5 — Select satellite boundaries

Propose satellite splits for stable KYC details, frequently changing CRM contact preferences and account status. State which source owns each attribute group and how consumers should join them at a point in time.

**Acceptance test:** each split has a stated reason; no split is justified only by “more tables is more normalized.”

### Exercise 6 — Choose an architecture

For each roadmap scenario in Section 6.10, choose a historical approach, reject at least one alternative and justify the decision with audit requirements, source count/change, team capability, complexity and consumer cost.

**Acceptance test:** the decision follows the requirements, not a blanket preference for Data Vault or for the simplest technology.

## 8. Practical scenarios and case-based reasoning

### Scenario 1 — Source reuses customer numbers after closure

**Situation:** core banking closes customer `C-1042`; months later, the source reuses `C-1042` for a different person.

**Reasoning:** if the hub's business key is only `C-1042`, both lifecycles collide. A load timestamp cannot distinguish the identities by itself. Investigate whether the source has a generation ID, immutable party ID, creation ID or another authoritative discriminator. If available, include it in the declared key scope. If not, quarantine ambiguity and obtain a business/governance rule; do not infer a new identity solely from a time gap or changed name.

**Evidence required:** source key contract, lifecycle fields, reuse policy, test records and approved key/mapping rule. A vault captures the implemented rule and observations; it cannot recover a discriminator the source never supplied.

### Scenario 2 — Regulator asks what the bank knew on a past date

**Situation:** on 31 January a report used `10 Main Street`; on 10 February CRM sent a correction stating that `12 Lake Road` had been effective since 1 January.

**Reasoning:** first establish whether the question means “what was recorded by the reporting cutoff?” or “what do we now believe was valid on that date?” The first uses a record/load-time cutoff before the correction arrived. The second uses a later knowledge cutoff and the business-valid-time rule. Retain the report version, transformation version, source lineage and identity mappings needed to reproduce the original report.

**What the model can answer:** what captured observations and governed rules support each answer. **What it cannot prove without more evidence:** the customer's actual residence, an unrecorded intent, or data that never reached the platform.

### Scenario 3 — A vault is proposed for one stable system

**Situation:** one stable source, one consumer, a small team, no regulatory history requirement and low change rate.

**Reasoning:** a relational history table or Type 2 dimension may meet the requirement with fewer moving parts. A vault imposes load orchestration, more tables, specialized conventions and downstream joins. Unless there is a specific planned integration or audit need with evidence, reject the vault and record the conditions that would trigger reconsideration.

### Scenario 4 — A late correction changes an old business date

**Situation:** a source reports on 10 February that an account relationship ended on 15 January. The platform had received no end date before then.

**Reasoning:** record time is 10 February; valid time may be 15 January. If the source's effective date is authoritative, a later-known view can show the relationship ended on 15 January. An as-known view before 10 February may still show it as open, subject to the platform's explicit “unknown end” semantics. Do not retroactively pretend the platform knew the end date in January.

### Scenario 5 — Conflicting source attributes

**Situation:** CRM says `12 Lake Road`, while core banking says `10 Main Street`.

**Reasoning:** first determine whether the fields mean the same thing. One may be a contact address and the other a KYC/legal address. If they are semantically comparable, use an explicit source-priority or survivorship rule in the consumer layer, preserve both source observations, and record the rule/version. “Newest timestamp wins” is unsafe when source clocks, effective dates or ownership differ.

## 9. Expected outputs and deliverables

Submit these artifacts for this lesson:

1. **Hub/link/satellite model** for Northbridge's in-scope Customer, Account and CustomerAccount concepts.
2. **Key dictionary** documenting business key meaning, source scope, uniqueness/reuse guarantees, composite-key rules and unresolved identity cases.
3. **Satellite inventory** with source, attribute definitions, rate of change, valid-time availability and change-capture policy.
4. **Metadata/lineage contract** defining `LoadTS`, `RecordSource`, source artifact/run references, time zone, clock semantics and exception handling.
5. **Point-in-time retrieval logic** that distinguishes a knowledge cutoff from a business-valid date and includes at least one tested correction case.
6. **Historical approach decision record** comparing Data Vault with at least one simpler alternative and addressing complexity and consumer cost.
7. **Consumer-layer derivation note** describing which dimensional/serving model is produced, its business grain, temporal interpretation and refresh requirements.
8. **Practice-question answers** with assumptions, reasoning and tests, not definitions alone.

### 9.1 Suggested decision-record template

```text
Decision ID / date:
Business scenario and accountable owner:
Questions the history must answer:
Required temporal view: current / change history / as-reported / bi-temporal
Sources and source-key guarantees:
Audit and lineage requirements:
Data volume, change rate and expected retention:
Team skills and operational constraints:
Options considered:
- Data Vault:
- Append-only lake/lakehouse history:
- Relational history or Type 2 dimension:
- Event log (if relevant):
Chosen approach and why:
Rejected alternative(s) and why:
Consumer model and expected query path:
Known limitations / assumptions / unresolved questions:
Deletion, correction and key-reuse policy:
Validation tests and acceptance evidence:
Triggers for revisiting the decision:
```

## 10. Common mistakes and misconceptions

1. **Assuming Data Vault is best for every platform.** Choose it only when source integration, change, lineage and history requirements justify the added cost.
2. **Mixing business keys with descriptive attributes.** Hubs identify scoped business keys; satellites retain descriptions and changes.
3. **Treating a source-local key as a global person identifier.** Source qualification prevents namespace collision; it does not resolve cross-source identity.
4. **Treating the vault as the analyst-facing layer.** Provide curated dimensions, facts, semantic definitions and predictable query paths.
5. **Losing load or source metadata.** Without it, lineage and as-known cutoffs may be impossible to defend.
6. **Confusing valid time with load time.** A correction received today may be valid for an earlier business date.
7. **Assuming a load timestamp proves when the source changed a value.** It proves only the timestamp's documented load/record event.
8. **Assuming a satellite automatically provides full bi-temporal history.** Valid-time semantics, record-time supersession and correction handling must be designed and tested.
9. **Interpreting a missing row as a deletion.** Require source contract, successful complete snapshot or explicit deletion evidence.
10. **Treating correction, deletion, closure and retraction as synonyms.** They have different business and temporal meanings.
11. **Ignoring reused or unstable identifiers.** A stable technical hash cannot fix an ambiguous business key.
12. **Assuming Data Vault performs identity resolution or survivorship.** These need governed rules and evidence.
13. **Splitting satellites without a reason.** Each split adds joins, pipeline logic and testing; use ownership and change-rate evidence.
14. **Assuming append-only means complete, immutable or audit-ready.** Retention, controls, source completeness and lineage still matter.
15. **Writing a point-in-time query without stating the time contract.** Specify which time axis is filtered, what “latest” means, and how corrections supersede prior assertions.
16. **Ignoring consumer cost.** A flexible integration model can be expensive to query; define downstream models and refresh behavior.
17. **Claiming a history model proves business intent.** It records evidence supplied and captured under a policy; intent must be explicitly recorded elsewhere.

## 11. Mastery criteria

You have mastered this topic when you can demonstrate all of the following without relying on memorized slogans:

- classify Customer and Account keys, CustomerAccount relationships and descriptive satellites correctly;
- explain why the hub key is separated from descriptive attributes;
- document source-qualified and composite business keys, including collision and reuse risks;
- explain exactly what `LoadTS` and `RecordSource` establish and what they do not establish;
- design satellite boundaries with explicit source ownership and change-rate rationale;
- reconstruct the address as of a business date using a specified knowledge cutoff;
- explain the difference between as-known history and a later corrected view of an earlier date;
- distinguish valid time, source event time, extraction time and load/record time when the use case requires them;
- handle source deletions, corrections and retractions without fabricating evidence;
- identify unresolved identity mappings and avoid silently merging source customers;
- describe how to derive a dimensional consumer model and why analysts should not be expected to reconstruct the vault on every query;
- compare Data Vault with at least one simpler alternative and state the consumer cost of the chosen approach;
- document assumptions, limitations, validation tests and the trigger for revisiting the architecture decision.

A reviewer should be able to trace every important modeling decision to a business question or a source contract, and to identify what evidence would falsify the assumption.

## 12. Completion gate

Do not mark this topic complete until all items below are satisfied.

- [ ] **Vault model reviewed:** the Customer hub, Account hub, CustomerAccount link and descriptive satellites have clear business-key scope, relationship meaning and attribute ownership.
- [ ] **Point-in-time retrieval reviewed:** the query/logic specifies both the business date and, when required, the knowledge/record-time cutoff; correction examples produce the expected results.
- [ ] **Temporal semantics reviewed:** valid time, load/record time, source event time and their limitations are explicitly distinguished where relevant.
- [ ] **Lineage reviewed:** every captured version can be traced to a source/feed and load run at the granularity required by the use case.
- [ ] **Identity risks reviewed:** source key collisions, key reuse, unstable identifiers and unresolved cross-source mappings are not silently treated as solved.
- [ ] **Deletion/correction handling reviewed:** missing records, explicit deletes, corrections and retractions have distinct, documented behavior.
- [ ] **Consumer derivation reviewed:** the target dimensional/serving model, temporal interpretation and refresh responsibilities are described.
- [ ] **Decision record reviewed:** the selected approach is justified against requirements, complexity, team capability and consumer costs.
- [ ] **At least one simpler alternative considered:** the record explains why it was accepted or rejected for the stated scenario.
- [ ] **Tests passed:** the single-source, regulated multi-source and exploratory scenarios have explicit recommendations; the address correction and key-reuse cases have been checked.

**Roadmap completion evidence:** a reviewed hub/link/satellite model, correct point-in-time retrieval logic, and a historical-approach decision record that includes at least one simpler alternative.

---

## Scope and assumptions

This lesson follows the roadmap's stated scope: hubs, links and satellites are the core constructs. The source-specific satellites, source-qualified/composite key examples, optional card structures, lineage run register, and bi-temporal query patterns are included only to make the required Northbridge exercise and its advanced history questions concrete. They are implementation/design extensions, not claims that every Data Vault must use every structure shown. Exact physical schema, platform-specific DDL, hash-key implementation, full master-data management and a complete dimensional mart are outside this topic's scope.

All Northbridge names, keys, addresses and dates in this lesson are illustrative. They are not actual bank records or evidence of a real production system.

## Appendix A — Practice answer key and verification cases

Use this answer key to check the exercises. These are the expected answers under the stated teaching assumptions; a production design may differ when its source contracts differ.

### A.1 Exercise 1 — Classify and model

| Item | Expected classification | Required qualification |
|---|---|---|
| Customer number | Customer hub business key | Scope it by source and any lifecycle/generation component needed for uniqueness. |
| Account number | Account hub business key | Scope it by source/account namespace; document reuse rules. |
| Customer associated with account | CustomerAccount link | Define relationship grain and whether one pair can have multiple concurrent instances. |
| Legal name / KYC address | Core-banking customer satellite, if that source owns these semantics | Preserve source and effective-time meaning when supplied. |
| CRM contact address / preference | CRM customer satellite | Do not treat as equivalent to legal/KYC address without a business rule. |
| Product/status | Account satellite from the owning source | Separate attributes by source/change cadence where justified. |
| Relationship role | CustomerAccount link satellite if it is a changing attribute of one relationship | If multiple concurrent role instances are independently meaningful, the link grain/key must represent them. |
| Card-account association | CardAccount link, with a Card hub if card identity is in scope | Do not encode it as CustomerAccount unless the domain definition explicitly says so. |

### A.2 Exercise 2 — Key collisions and identity

Expected source-qualified keys include `CORE|C-1042` and `CRM|C-1042`. They are distinct technical business-key values and prevent a namespace collision. They do **not** establish that the keys represent different people or the same person. Do not create a canonical customer mapping until an approved identity-resolution rule and supporting evidence exist. The mapping itself should be traceable and, when historical identity decisions matter, effective-/record-dated.

### A.3 Exercise 3 — Point-in-time address

- Known by 31 January, valid on 31 January: `10 Main Street`; the 10 February correction is outside the record-time cutoff.
- Known by 15 February, valid on 31 January: `12 Lake Road`; the correction is within the cutoff and its `ValidFrom` is 1 January.
- Both answers assume the correction supersedes the earlier assertion over the whole interval from 1 January. If the source correction applies only to a subinterval, the source's interval semantics must be represented instead.

### A.4 Exercise 4 — Deletion and correction

At least four explanations for a missing row are: partial extract, failed/incomplete pipeline, changed filter/access scope, delayed feed, source outage, or actual deletion. Treat absence as deletion only when there is an explicit delete/tombstone or a complete, reconciled snapshot whose contract defines absence as deletion. For a retroactive correction, retain the old assertion's record-time interval for earlier as-known queries and add/supersede the assertion under the documented temporal policy; do not overwrite evidence so that the old answer becomes unreproducible.

### A.5 Exercise 5 — Satellite boundaries

A defensible baseline is a core/KYC satellite for legally defined customer attributes, a CRM satellite for contact preferences, and an account satellite for account status. Separate further only if ownership, access, change-rate, lineage or load evidence justifies the extra joins and operations. Consumers must select each satellite's state using its own temporal contract; independent satellite changes do not imply a synchronized snapshot.

### A.6 Exercise 6 — Architecture selection

| Scenario | Expected recommendation | Why / caveat |
|---|---|---|
| Single stable source, one report, modest history | Relational history table or Type 2 dimension | Lower complexity and consumer cost; reconsider if integration/audit requirements grow. |
| Core banking + cards + CRM with regulated historical evidence | Data Vault is a credible candidate, paired with raw evidence, lineage, identity governance and curated consumer models | More source integration and traceability, but higher modeling/operating/query cost; the vault alone does not guarantee valid-time or as-reported correctness. |
| Exploratory files/events with unstable semantics | Controlled append-only landing/history plus selective curated tables | Enables exploration before committing to a full integration model; still requires retention, lineage, quality and access controls. |

A response that recommends Data Vault in all three scenarios, or that treats append-only storage as automatically audit-ready, does not pass. A decision must cite requirements and evidence, identify at least one simpler alternative, and name the consumer/query cost.

### A.7 Acceptance checks for the worked temporal query

1. With `known_at = 2026-01-31 23:59:59 UTC` and `valid_at = 2026-01-31`, the query returns exactly one row: `10 Main Street`.
2. With `known_at = 2026-02-15 23:59:59 UTC` and the same `valid_at`, it returns exactly one row: `12 Lake Road`.
3. The query does not use `LoadTS` as a substitute for `ValidFrom` or `ValidTo`.
4. The prior record-time assertion remains queryable after the correction.
5. If multiple assertions share a record timestamp, a deterministic source sequence/record identifier resolves ordering; otherwise the platform must flag the ambiguity rather than choose arbitrarily.
6. The key-reuse case cannot be resolved by timestamp or hashing alone; it needs a source guarantee, discriminator, or governed exception process.
