# 06 — Master Data Management and Golden Records

> **Learning path:** Beginner → Intermediate → Advanced  
> **Module:** Stage 2D — Data Architecture / 11-Metadata-Lineage-Quality-and-Master-Data  
> **Recommended effort:** 7–9 hours (roadmap estimate)  
> **Scenario:** Northbridge Bank, a fictional enterprise; all records and numbers in this document are synthetic and illustrative.

## How to use this document

Work through the foundations and architecture patterns first. Then build the worked golden record using the explicit rules, not intuition. Complete both exercises and the completion gate. This topic is numbered 06 to preserve the repository's prescribed sequence; however, **study Topic 07 — Reference Data, Entity Resolution and Identifiers, Beginner level before attempting this document's Advanced level**. Matching, identifier lifecycle and thresholds are prerequisites to safe golden-record decisions. Full study remains in numeric file order.

The module roadmap is the scope authority. Its repository note says that topic files and the final-project files were empty when the roadmap was written; therefore, this document follows the roadmap's stated learning plan and deliverables without claiming to reproduce content from empty files. Architecture patterns are explained as common, vendor-neutral approaches. All systems, records, targets and outcomes below are illustrative, not evidence about real people or production systems.

## 1. Purpose, scope, prerequisites and learning outcomes

### 1.1 Purpose

Master data management (MDM) establishes and operates governed, reusable representations of important business entities across systems. A **golden record** is the best governed representation for a defined purpose, assembled or exposed from source records under explicit policies. It is not a guarantee of perfect truth, nor must it replace every source record.

Without MDM, the same customer, product, supplier or counterparty may be represented differently in CRM, onboarding, billing, risk, e-commerce, analytics and AI systems. Duplicate records distort counts and segmentation; conflicting addresses cause failed communication; inconsistent product codes break joins; and a mistaken identity merge can expose one person's information to another.

MDM is not merely a deduplication job. It combines domain modelling, identifiers, identity resolution, governance, attribute-level decisions, stewardship, lifecycle controls, synchronization and auditability.

### 1.2 Prerequisites and dependency order

| Prerequisite | Why it matters here | Expected prior capability |
|---|---|---|
| Topic 01 — metadata foundations | Every master attribute and source needs meaning, ownership and technical description | Distinguish business, technical and operational metadata; identify owner/steward |
| Topic 04 — data quality and critical data elements (CDEs) | Master attributes need measurable fitness rules and priority | Define dimensions, CDEs, rules, thresholds and remediation owners |
| P1 and related platform foundations | The roadmap names P1 as a prerequisite | Confirm prerequisite readiness using the parent roadmap; do not infer missing P1 details from this file |
| Topic 07 — Beginner level, before Topic 06 Advanced | Identity decisions depend on identifier and matching foundations | Explain reference data, identifiers, crosswalks, deterministic/probabilistic matching, thresholds and precision/recall |
| Topic 03/05 concepts as needed | Lineage and monitoring help trace source values and detect stale or failed synchronization | Follow source-to-consumer lineage and define freshness/quality signals |

**Sequence rule:** keep `06-master-data-management-and-golden-records.md` before `07-reference-data-entity-resolution-and-identifiers.md` in the repository. Within learning, complete Topic 07's Beginner section before Topic 06's Advanced section. This is a targeted dependency, not a renumbering instruction.

### 1.3 Learning outcomes

By the end, you should be able to:

1. Distinguish master data from transactional data, reference data, identifiers and metadata.
2. Identify master domains, owners, stewards, authoritative sources and permitted uses.
3. Select an MDM architecture pattern using business needs, latency, autonomy, disruption, cost and governance constraints.
4. Model a golden record with stable identity, source crosswalks, lifecycle status, versions and attribute-level provenance.
5. Define deterministic survivorship and conflict-resolution rules per attribute, including tie-breaks, missing values, uncertainty and steward review.
6. Explain matching evidence, false matches, missed matches and the boundary between a match decision and a master-data decision.
7. Design create, update, merge, link, unmerge, retirement and downstream change propagation.
8. Define quality controls, privacy/access policies, audit history, synchronization guarantees and operational KPIs.
9. Explain how entity consistency affects analytics, customer operations, ML features and AI retrieval.
10. Produce the roadmap's expected deliverables and defend the design in an ADR.

## 2. Beginner foundations and terminology

### 2.1 What counts as master data?

Master data describes relatively stable business entities and their important attributes that many processes or systems reuse. It changes, sometimes frequently, but it is not primarily a record of individual business events.

| Domain | Example entity | Typical attributes | Example consumers |
|---|---|---|---|
| Customer / party | Individual or organization | Master party ID, name, contact points, status, preferred language, verified address | CRM, service, billing, risk, analytics |
| Product | Product or SKU | Product ID, name, category, units, lifecycle status, regulated attributes | Catalog, inventory, pricing, reporting |
| Supplier | Supplier organization | Supplier ID, legal name, tax identifier, approved status, payment terms | Procurement, accounts payable, compliance |
| Counterparty | Legal entity in a financial relationship | Legal entity ID, jurisdiction, identifiers, relationship and risk attributes | Trading, risk, settlement, regulatory reporting |
| Location / asset (where governed as a domain) | Store, branch, facility | Stable ID, type, address, status, hierarchy | Operations, planning, reporting |

Not every organization treats every domain as master data. Classification depends on reuse, business impact, change ownership and governance requirements. A field's importance alone does not determine the whole dataset's domain.

### 2.2 Core terms

- **Master data domain:** a governed category of entities, such as customer or product.
- **Source record:** a record held by a source application, with that application's identifier and semantics.
- **Source of record:** the system in which a particular record or process is maintained. This does not automatically make every attribute in that system authoritative enterprise-wide.
- **Authoritative source for an attribute:** the source designated by policy to provide or verify a particular value under specified conditions.
- **MDM hub/service:** capability that links, reconciles, governs and/or distributes master data. It may be logical and distributed rather than one physical database.
- **Golden record:** the governed, purpose-specific representation of an entity, with selected attributes and traceable provenance.
- **Survivorship:** the policy and execution process that decides which candidate value becomes the mastered value for an attribute.
- **Crosswalk:** a mapping between source-system identifiers and a master identifier (or another namespace).
- **Entity resolution:** the process of determining whether records refer to the same real-world entity.
- **Merge:** an identity decision that brings records under one mastered identity, while retaining evidence and reversibility controls.
- **Link:** a relationship between records that preserves their separate identities; useful when relatedness is known but identity equivalence is not established.
- **Unmerge:** reversal/correction of an erroneous merge, including identity, attribute, history and downstream repair.
- **Data owner:** accountable business role for definitions, permitted use, policy and acceptable risk.
- **Data steward:** operational role that resolves exceptions, reviews quality and maintains domain rules.
- **Provenance:** evidence about where a value came from, how it was transformed or selected, when it was observed and why it won.

A golden record is not the same thing as a match score. A match score estimates how likely two source records are to refer to the same entity. The golden record is the governed result after identity, attribute and lifecycle rules have been applied.

### 2.3 Why multiple versions exist

Systems are built for different purposes and at different times. A CRM may optimize customer contact; an onboarding platform may capture verified legal identity; a card platform may store delivery addresses; a risk system may hold risk segmentation. Each has its own keys, data-entry controls, refresh cycles and correction paths. Mergers, migrations, human typos, delayed events and differing business definitions add divergence.

MDM makes these differences explicit rather than assuming all systems have the same semantics. It should not blindly overwrite source applications. It defines what to trust for which attribute, what to publish, who can correct it, and how conflicts are resolved.

## 3. Master data versus transactional, reference and metadata

| Type | Primary question | Example | Typical lifecycle | Relationship to MDM |
|---|---|---|---|---|
| Master data | Who or what does the business deal with? | Customer, product, supplier, counterparty | Create, update, merge/link, deactivate/retire | Main entities and attributes governed by MDM |
| Transactional data | What event or activity occurred? | Payment, order, trade, support interaction | Append, correct/reverse under event controls, retain per policy | References master IDs; should not be rewritten casually when master data changes |
| Reference data | Which controlled code or category applies? | Country code, currency, product category, status code | Version, approve, effective-date, retire | Often shared by master domains; mapping may be required across code sets |
| Metadata | What does this asset/field mean, who owns it, where did it come from? | Definition of `verified_address`, schema, steward, lineage | Register, version, harvest, review | Describes master data assets, lineage, quality rules, access and provenance |
| Identifier | How is an entity or record referred to in a namespace? | CRM customer number, master party ID | Assign, map, preserve, retire without unsafe reuse | Connects source records to mastered entities; is not itself proof of identity |

A country code is reference data, not a customer. A payment is a transaction, not a customer attribute. A source-system customer number is an identifier, not a master record. A field definition is metadata, not the field's value.

**Why the distinctions matter:** confusing these concepts leads to bad architecture. For example, changing a master customer ID must not rewrite immutable transaction history; instead, transaction records retain their original references and an identity crosswalk or controlled resolution layer explains how they map to the current master identity.

### 3.1 When a domain deserves MDM

Consider MDM when the entity is reused across multiple processes, inconsistent identities materially affect decisions, attribute ownership can be agreed, and there is a business case for the ongoing operating cost. A lightweight reference mapping or data-quality process may be enough when the data is low-risk, used once, or lacks a feasible stewardship model.

MDM adds value when it reduces duplicate work, improves compliance evidence, stabilizes analytics, supports customer service or enables consistent downstream decisions. It adds little if the organization merely centralizes a copy without resolving ownership, lifecycle, identity or synchronization.

## 4. Governance, ownership and authoritative sources

### 4.1 Accountability model

| Role | Accountable / responsible for | Example decision |
|---|---|---|
| Domain data owner | Domain policy, definition, risk acceptance, escalation | Which attributes qualify as verified legal identity? |
| Data steward | Day-to-day exception resolution, data quality, rule operation and documentation | Review two similar customer records in the ambiguous match band |
| Source-system owner | Source capture controls, source IDs, source data availability and correction path | Repair the original onboarding record after a confirmed error |
| MDM product/service owner | Hub availability, model, matching workflow, release and operational controls | Roll out a new survivorship rule with versioning and backfill plan |
| Privacy/security/compliance roles | Access, purpose, retention, residency and audit controls | Restrict full address exposure to authorized workflows |
| Consumer owner | Consumer mapping, idempotency, reconciliation and safe adoption | Apply master change version 42 without duplicating an update |

The business owns meaning and policy; technology implements and operates controls. MDM fails when “IT owns the customer” is used as a substitute for business accountability.

### 4.2 Authoritative source is attribute-specific

A single system may be authoritative for legal name but not preferred name; for a verified residential address but not a mailing address; or for risk classification but not marketing consent. Policy must specify the attribute, context, verification state, effective date, source eligibility and exception path.

A useful policy row contains:

| Field | Purpose |
|---|---|
| Attribute and business definition | Prevents semantically different fields from being conflated |
| Allowed sources and precedence | Makes eligibility explicit |
| Verification/evidence requirement | Distinguishes user-entered from verified values |
| Freshness/effective-time rule | Prevents stale values from winning solely due to source rank |
| Null/invalid handling | Defines whether absence can overwrite a value |
| Tie-break and conflict threshold | Makes outcome deterministic |
| Owner/steward and escalation SLA | Gives exceptions a destination |
| Provenance and audit fields | Makes each result explainable |

**Do not equate authoritative with newest, most complete, or globally highest-ranked.** A newer unverified address must not overwrite a verified address when the policy requires verification. A source with many filled fields may still have weak evidence. A system may be authoritative only for a specific business purpose or legal entity type.

### 4.3 Governance policy lifecycle

Propose a policy → approve with domain owner and relevant control functions → version it → test on synthetic or appropriately protected historical data → deploy with monitoring → review exception and quality metrics → change with a documented effective time. Keep the rule version used for each decision. A change in policy should not silently rewrite past decisions without a controlled migration and audit record.

## 5. MDM architecture patterns and decision criteria

These patterns are conventional architecture categories, not vendor product labels. Real implementations can combine them by domain or use case.

### 5.1 Registry / virtual MDM

**What it is:** a central index holds master identifiers, source crosswalks, match/link decisions and possibly selected metadata, while authoritative attributes remain in source systems. Consumers retrieve source data through a registry or federated access layer.

**How it works:** ingest source keys and match evidence → assign or resolve master IDs → maintain links to source records → query or join source values when needed.

**Use when:** source systems cannot be changed easily, rapid identity linking is needed, ownership remains distributed, or the initial goal is cross-system discovery and analytics.

**Trade-offs:** lower migration burden and less copied personal data, but query-time latency, source availability dependencies, inconsistent source updates and complex multi-source retrieval. A registry may know two records are linked without having a complete, materialized golden record.

### 5.2 Consolidation / analytical MDM

**What it is:** source data are copied into a hub or curated layer, matched and consolidated into mastered views, usually without writing corrections back to operational source systems.

**How it works:** extract source records → normalize and validate → match/link → select attributes → retain provenance → publish curated master views to analytics and reporting.

**Use when:** enterprise reporting, customer 360, deduplicated metrics or model features are the primary use cases and source applications should remain autonomous.

**Trade-offs:** strong analytics consistency and replayable processing; however, operational systems may remain inconsistent, and the consolidated view can become stale. It is not sufficient when a front-line process requires a correction to take effect across operational systems immediately.

### 5.3 Coexistence / bidirectional MDM

**What it is:** source applications and the MDM service can both originate or update data within governed permissions. The hub resolves, publishes and reconciles changes across participants.

**How it works:** authorized changes arrive with source/version metadata → policies decide whether to accept, reject, review or transform → master state changes → events or APIs publish changes → consumers acknowledge/apply and reconcile.

**Use when:** distributed operational teams need to maintain local workflows but require shared mastered values.

**Trade-offs:** broad operational utility but high complexity: concurrent edits, loops, conflict arbitration, stale events, partial failures and different consumer capabilities. Requires idempotency, versioning, loop prevention, retry policies and reconciliation.

### 5.4 Centralized / transactional MDM

**What it is:** the MDM service becomes the primary point of creation and maintenance for some or all mastered attributes. Source applications consume master values or invoke the master service for writes.

**How it works:** validate request at the master service → assign stable master ID → enforce domain policy → persist state and audit → publish committed changes → consumers update or query the master service.

**Use when:** consistent operational behavior is critical, new entities must be created once, and the organization can redesign source processes around the master service.

**Trade-offs:** strong control and consistent entry point, but larger organizational change, availability dependency, migration cost, and potential bottleneck. Centralization does not remove the need for source-specific ownership or purpose-specific values.

### 5.5 Coexistence and centralization are not the same

In coexistence, multiple systems may originate updates and the hub arbitrates them. In centralized MDM, the master service is the controlled write authority for defined attributes. A design can centralize legal identity while allowing local applications to own notes or workflow-specific preferences.

### 5.6 Federated / domain-oriented MDM

**What it is:** domains own their own master services but share contracts for identifiers, metadata, quality, access, and cross-domain relationships. A customer domain and product domain need not be one database.

**Use when:** domains have distinct semantics, ownership and operational requirements, but enterprise consumers need consistent linking and interoperability.

**Trade-offs:** preserves autonomy and scales organizationally; increases the need for shared identifier policy, domain contracts, cross-domain stewardship and consistent metadata. “Federated” does not mean “no standards.”

### 5.7 Pattern comparison

| Decision factor | Registry | Consolidation | Coexistence | Centralized / transactional | Federated |
|---|---|---|---|---|---|
| Main purpose | Link and resolve identity | Analytics/reporting consistency | Operational synchronization | Governed point of write | Domain autonomy with shared contracts |
| Source change required | Low | Low–moderate | Moderate–high | High | Depends on each domain |
| Operational consistency | Depends on live sources | Hub view consistent, sources may not be | Can be high if sync is reliable | Potentially high for governed attributes | Varies by domain contract |
| Latency | Query-time or registry latency | Batch or incremental freshness | Event/API design | API/event design | Domain-specific |
| Complexity | Lower hub complexity; query complexity | Pipeline and quality complexity | High conflict/sync complexity | Migration and availability complexity | Governance and cross-domain complexity |
| Main failure mode | Source unavailable or link wrong | Stale or misleading consolidated view | Divergent copies / update loops | Hub bottleneck or bypassed process | Inconsistent domain contracts |

### 5.8 Selection method

1. State the business use case: analytics, operations, regulatory reporting, customer service, fraud or AI.
2. Identify the attributes that must be consistent and the maximum acceptable staleness.
3. Inventory source systems, write ownership, APIs/events, identifiers and constraints.
4. Assess whether sources can be changed and who can resolve conflicts.
5. Choose the lightest pattern that meets the risk and latency needs.
6. Document rejected alternatives, operational failure modes, migration steps and success metrics in an ADR.

A common staged approach is registry first for low-disruption identity mapping, consolidation for trusted analytics, then coexistence or centralized entry for selected operational attributes if the business case justifies it. This is a scenario-dependent option, not a universal maturity ladder.

## 6. Golden-record modelling and attribute-level survivorship

### 6.1 Model principles

A robust golden-record model separates **entity identity**, **source-record identity**, **attribute value**, **provenance**, **match/merge decision**, **lifecycle state** and **publication state**. Do not flatten all of these into a single row without history.

Recommended logical entities:

- `master_entity`: stable master ID, domain, lifecycle status, created/updated times, current version.
- `source_record`: source system, source ID, source version, observed/effective timestamps, record status and source pointer.
- `crosswalk`: source system + source ID → master ID, link status, valid-from/to, decision ID.
- `master_attribute`: master ID, attribute name, selected value or protected reference, value status, effective time, rule version.
- `attribute_provenance`: selected source record/field, source event/version, evidence class, observed/effective time, selection reason and confidence/quality indicator.
- `identity_decision`: candidate pair, evidence, score or rule outcome, threshold version, decision (match/non-match/review/link), reviewer and time.
- `merge_event` / `unmerge_event`: prior and resulting identities, reason, decision, affected crosswalks, version and downstream repair status.
- `publication_outbox`: committed master version, event ID, publication status and retry metadata.

### 6.2 Example logical schema (illustrative SQL)

This SQL is illustrative and close to standard relational SQL, but types and constraints may need adjustment for a particular database. It intentionally stores provenance separately from the selected attribute value.

```sql
CREATE TABLE master_entity (
    master_id       VARCHAR(40) PRIMARY KEY,
    domain          VARCHAR(30) NOT NULL,
    status          VARCHAR(20) NOT NULL,
    version_no      BIGINT NOT NULL,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL,
    CHECK (status IN ('PROVISIONAL', 'ACTIVE', 'UNDER_REVIEW', 'MERGED', 'RETIRED', 'RESTRICTED'))
);

CREATE TABLE source_record (
    source_system   VARCHAR(40) NOT NULL,
    source_id       VARCHAR(100) NOT NULL,
    source_version  VARCHAR(100),
    observed_at     TIMESTAMP NOT NULL,
    effective_at    TIMESTAMP,
    record_status   VARCHAR(20) NOT NULL,
    PRIMARY KEY (source_system, source_id)
);

CREATE TABLE identity_decision (
    decision_id       VARCHAR(50) PRIMARY KEY,
    decision_type     VARCHAR(30) NOT NULL,
    outcome           VARCHAR(30) NOT NULL,
    left_source_system  VARCHAR(40),
    left_source_id      VARCHAR(100),
    right_source_system VARCHAR(40),
    right_source_id     VARCHAR(100),
    policy_version    VARCHAR(40) NOT NULL,
    evidence_ref      VARCHAR(200),
    decided_at        TIMESTAMP NOT NULL,
    reviewer_id       VARCHAR(80),
    CHECK (decision_type IN ('MATCHING', 'SURVIVORSHIP', 'CROSSWALK', 'MERGE', 'UNMERGE')),
    FOREIGN KEY (left_source_system, left_source_id)
      REFERENCES source_record(source_system, source_id),
    FOREIGN KEY (right_source_system, right_source_id)
      REFERENCES source_record(source_system, source_id)
);

CREATE TABLE crosswalk (
    source_system   VARCHAR(40) NOT NULL,
    source_id       VARCHAR(100) NOT NULL,
    master_id       VARCHAR(40) NOT NULL,
    link_status     VARCHAR(20) NOT NULL,
    valid_from      TIMESTAMP NOT NULL,
    valid_to        TIMESTAMP,
    decision_id     VARCHAR(50) NOT NULL,
    PRIMARY KEY (source_system, source_id, valid_from),
    FOREIGN KEY (source_system, source_id)
      REFERENCES source_record(source_system, source_id),
    FOREIGN KEY (master_id) REFERENCES master_entity(master_id),
    FOREIGN KEY (decision_id) REFERENCES identity_decision(decision_id),
    CHECK (link_status IN ('CONFIRMED', 'PROVISIONAL', 'SUPERSEDED'))
);

CREATE TABLE master_attribute (
    master_id       VARCHAR(40) NOT NULL,
    attribute_name  VARCHAR(80) NOT NULL,
    attribute_value VARCHAR(500),
    value_status    VARCHAR(20) NOT NULL,
    rule_version    VARCHAR(40) NOT NULL,
    effective_at    TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL,
    PRIMARY KEY (master_id, attribute_name),
    FOREIGN KEY (master_id) REFERENCES master_entity(master_id)
);

CREATE TABLE attribute_provenance (
    master_id       VARCHAR(40) NOT NULL,
    attribute_name  VARCHAR(80) NOT NULL,
    source_system   VARCHAR(40),
    source_id       VARCHAR(100),
    source_field    VARCHAR(100),
    source_version  VARCHAR(100),
    observed_at     TIMESTAMP,
    evidence_class  VARCHAR(40) NOT NULL,
    selection_reason VARCHAR(500) NOT NULL,
    decision_id     VARCHAR(50) NOT NULL,
    PRIMARY KEY (master_id, attribute_name, decision_id),
    FOREIGN KEY (master_id, attribute_name)
      REFERENCES master_attribute(master_id, attribute_name),
    FOREIGN KEY (source_system, source_id)
      REFERENCES source_record(source_system, source_id),
    FOREIGN KEY (decision_id) REFERENCES identity_decision(decision_id)
);
```

**Implementation notes:** this is a teaching schema, not a complete production DDL. Rejected candidate pairs belong in the identity-decision ledger, not in a crosswalk; a crosswalk represents an accepted or provisional mapping and its history. The example enforces basic source-record and decision references, but does not enforce non-overlapping crosswalk validity intervals, complete bitemporal history, optimistic concurrency, or all domain-specific state transitions. Production design should add those controls, event IDs, protected storage for sensitive values, and access controls. A source ID can be reused or rekeyed in some systems, so a production source-record key may need a source namespace plus source-record generation/version. `attribute_value` should be typed by domain or represented in a typed attribute model rather than forcing every value into `VARCHAR`.

### 6.3 Attribute-level survivorship

Survivorship selects the value for **one attribute at a time** from eligible candidates. A useful policy specifies:

1. Eligibility: which sources and record statuses can contribute?
2. Evidence: what verification or validation level is required?
3. Source precedence: is one source authoritative for this attribute and context?
4. Time: use effective time, observed time or a defined freshness window?
5. Quality: which checks must pass?
6. Missing/invalid handling: can null or invalid input ever clear a current value?
7. Tie-break: what happens when candidates remain equal?
8. Review threshold: when must a steward decide?
9. Provenance: what evidence and rule version are retained?

Example policy table:

| Attribute | Eligibility and policy | Tie-break / exception | Reason |
|---|---|---|---|
| Legal name | Prefer verified onboarding/legal evidence; reject unverified source values for legal-name use | If two verified values conflict, steward review; never auto-resolve solely by recency | Legal identity has high impact |
| Preferred display name | Use explicit current customer preference from an authorized channel | Effective time, then deterministic source ID only if equal; preserve history | Preference can legitimately differ from legal name |
| Residential address | Prefer the latest effective, verified address from an approved verification process; source rank is a guardrail, not sole criterion | Unverified update cannot replace verified current address; conflict in verification evidence goes to steward | Verification and effective time matter |
| Email | Require syntax validity; prefer verified, not-bounced address; recency applies only within same evidence class | If equal, source precedence then stable source key; do not treat missing as deletion | Contactability is not implied by completeness |
| Risk segment | Risk domain is authoritative for its defined segment and as-of time | If stale or missing, mark unknown/stale and escalate; do not infer from CRM | Domain-specific meaning and control |
| Marketing permission | Use the consent/permission system as source of record, with purpose and jurisdiction context | Do not merge contradictory permissions into broad consent; deny or suppress where policy requires pending resolution | Consent is purpose-specific and sensitive |

### 6.4 Deterministic rule order

A common deterministic pattern is **eligibility filter → evidence class → attribute-specific source precedence → effective-time rule → quality checks → tie-break → review fallback**. The order must be chosen deliberately: if source rank always wins before verification, a low-quality high-ranked value can beat a verified value. If recency always wins, stale corrections or unverified edits can overwrite stronger evidence.

A deterministic tie-break should be reproducible but must not invent business authority. A stable source key can make otherwise equivalent choices reproducible; it cannot make one value more truthful. If a tie is material, route it to stewardship instead of pretending a technical tie-break is a business decision.

### 6.5 Missing, invalid, deleted and conflicting values

- **Missing value:** usually means “no candidate value supplied,” not “clear the mastered value.”
- **Explicit deletion/withdrawal:** process as a distinct command with policy and audit evidence; do not infer deletion from a null field.
- **Invalid value:** exclude or quarantine according to rules; retain the failure reason and source provenance.
- **Conflicting verified values:** preserve both evidence paths and request review when no rule can safely arbitrate.
- **Stale value:** may remain valid for historical/as-of queries but should be marked stale for current use.
- **No eligible candidate:** represent unknown/unavailable explicitly. Do not manufacture a value from the “best-looking” record.

### 6.6 Confidence and uncertainty

Confidence is not one universal number. Keep separate indicators for (a) identity-match confidence, (b) attribute evidence/verification state, and (c) data-quality validity. A high match score does not prove the selected address is current; a verified address does not prove two records are the same person.

Possible statuses include `VERIFIED`, `SOURCE_ASSERTED`, `INFERRED`, `CONFLICTED`, `STALE`, `UNKNOWN`, and `PENDING_REVIEW`. Define them in the domain glossary. Do not expose a numeric “confidence” unless the score's meaning, calibration, evidence and decision threshold are documented. A percentage is not a guarantee of truth.

## 7. Identity, matching, identifiers and provenance

### 7.1 Identifiers are namespaces, not truth

A CRM ID identifies a record in CRM. A core banking ID identifies a record in that system. A master party ID identifies the enterprise mastered entity. These IDs can all refer to the same person, but that relationship must be supported by a resolution decision and stored in a crosswalk.

Prefer stable, opaque master identifiers that are not derived from mutable attributes such as name, phone or address. Do not reuse retired master IDs for a different entity. If an external business identifier changes, keep its history and mapping. If a master ID must be corrected or superseded, publish an explicit identity-change event and preserve old references through a controlled crosswalk or alias policy.

### 7.2 Matching workflow

1. **Normalize safely:** standardize case, whitespace, Unicode, phone formatting and address components without destroying original values. Store raw and normalized forms with lineage.
2. **Block candidates:** reduce comparisons using defensible keys or windows. Blocking reduces cost but can cause missed matches if the true pair never enters the candidate set.
3. **Evaluate evidence:** exact stable identifier, verified contact point, name/address similarity, date of birth or organization attributes as allowed and proportionate.
4. **Apply rules or score:** deterministic rules for strong evidence; probabilistic scoring for ambiguous combinations when calibrated and justified.
5. **Use thresholds:** high-confidence band may auto-link/merge only if the cost of false merge is acceptable; middle band goes to stewardship; low band remains separate. A “no match” decision is also evidence-based and can be revisited.
6. **Persist decision:** inputs, features or rules, threshold/rule version, evidence, decision, reviewer, time and reason.
7. **Monitor:** sample outcomes, measure precision/recall where labeled data exist, examine false merges/missed matches and review drift.

### 7.3 False matches and missed matches

A **false match** combines records for different entities. It can mix contact information, expose sensitive data, corrupt risk decisions and contaminate training labels. A **missed match** leaves duplicate records separate, causing fragmented service, overcounting and inconsistent features. These errors have different costs and should not be optimized as though they are interchangeable.

Thresholds should reflect business harm, not only aggregate accuracy. For high-impact customer identity, it may be preferable to route uncertain cases to review instead of increasing automatic merge coverage. Precision asks “of the pairs we declared matches, what fraction were correct?” Recall asks “of all true matching pairs, what fraction did we find?” Candidate-generation and labeling bias can make both metrics misleading; document the evaluation set and its limitations.

### 7.4 Merge versus link

- **Merge:** use when evidence and policy support the same entity. Source records are mapped to one master identity, and a merge decision is recorded. Source rows and historical references should not be physically erased merely because the identity was merged.
- **Link:** use when records are related but identity equivalence is not established, such as household members, parent/subsidiary organizations, account-to-party relationships or ambiguous candidate pairs. The relationship has a type and valid time; each entity retains its own master ID.
- **Do not merge:** when evidence conflicts, records represent distinct people with similar attributes, or policy prohibits automatic action.

### 7.5 Provenance is attribute-level and decision-level

For every selected attribute, retain at minimum the source system, source record ID, source field, source version/event, observed time, effective time if known, evidence class, selection rule version and reason. For identity resolution, retain candidate records, matching evidence, decision threshold/version, reviewer or automated policy and decision time.

Provenance should support a steward answering: “Why did this value win? What other candidates were considered? What evidence was available then? Which rule version ran? Which consumers received the decision?” Avoid storing unnecessary sensitive raw data in logs; store protected references or minimized evidence summaries when sufficient.

## 8. Master data lifecycle, synchronization and governance

### 8.1 Lifecycle states

A practical lifecycle may include `PROVISIONAL`, `ACTIVE`, `UNDER_REVIEW`, `MERGED`, `RETIRED` and `RESTRICTED`. Define transition rules per domain. Status names are examples, not universal requirements.

- **Create:** validate domain requirements, check candidate duplicates, assign master ID, record source crosswalk and initial provenance.
- **Update:** validate authorization, source eligibility, effective time and attribute policy; create a new master version and provenance entry.
- **Merge:** record decision, canonical survivor/redirect policy, crosswalk changes, affected master IDs, event ID and downstream repair plan.
- **Link:** create a typed relationship without collapsing identities.
- **Unmerge:** reverse the mistaken identity relationship, restore or reassign crosswalks, recompute affected attributes, emit correction events and reconcile consumers.
- **Retire/deactivate:** prevent new operational use as defined, retain required history, preserve references for transactions and audit.
- **Delete/anonymize:** apply applicable retention, legal-hold and privacy policy; propagate required deletions or tombstones to copies while preserving legally required audit evidence in appropriately minimized form.

### 8.2 Synchronization patterns

| Pattern | Good fit | Main risk / control |
|---|---|---|
| Scheduled batch | Analytics and lower-frequency consumers | Staleness; publish watermarks, lag indicators and full reconciliation |
| Change data capture (CDC) | Incremental propagation from source changes | Ordering, schema evolution, duplicate/replayed events; preserve source version and idempotency key |
| Domain events / outbox | Reliable publication after master commit | Event publication gap; write state and outbox atomically, retry and track delivery |
| API lookup | Current value on demand | Latency, availability dependency, load and authorization; cache with explicit freshness policy |
| Bulk snapshot + delta | Large consumers and recovery | Snapshot/delta race; define cutover watermark and replay protocol |

A master update is not complete operationally merely because the hub committed it. The design should define consumer expectations: immediate versus eventual consistency, maximum propagation lag, event ordering, duplicate delivery, retry, dead-letter handling, schema versioning, replay, reconciliation and ownership of a stuck consumer.

### 8.3 Example change event

```json
{
  "event_id": "evt-000042",
  "event_type": "master.customer.updated",
  "schema_version": 1,
  "master_id": "PTY-10482",
  "master_version": 42,
  "occurred_at": "2026-01-15T10:20:00Z",
  "changed_attributes": ["residential_address"],
  "reason_code": "VERIFIED_ADDRESS_CHANGE",
  "provenance_ref": "prov-addr-0091",
  "correlation_id": "corr-merge-0027"
}
```

The payload intentionally omits the full address. A consumer with authorization can retrieve the current value or a protected payload through an approved channel. This reduces sensitive data replicated in message logs. If consumers need the value inline, classify the event, encrypt appropriately, restrict subscriptions, set retention, and avoid placing personal data in headers or logs without need.

### 8.4 Consumer contract

Each consumer contract should define:

- which attributes it consumes and for what purpose;
- master ID and source crosswalk behavior;
- schema version compatibility and unknown-field handling;
- event ID/idempotency key and duplicate handling;
- master-version ordering or stale-update rejection;
- retry/backoff, dead-letter queue and replay procedure;
- expected propagation lag and alert threshold;
- reconciliation frequency and discrepancy ownership;
- merge/unmerge handling and historical-reference strategy;
- security classification, authorization and retention.

Consumers should generally apply an event idempotently: processing the same event twice has the same final effect as processing it once. They should reject or defer an older master version after a newer one has been applied, unless the consumer explicitly supports temporal replay. Never assume message delivery is exactly once end-to-end.

### 8.5 Reconciliation and observability

Monitor source-to-hub ingestion lag, match-review backlog, duplicate and false-merge rates, attribute rule failures, consumer lag, rejected events, version gaps, stale copies and reconciliation mismatches. A reconciliation job should compare stable keys and versions, not just row counts. Alert owners should have runbooks and the ability to replay safely.

### 8.6 Stewardship KPIs

Use metrics that connect to business risk and workflow capacity:

- duplicate candidate rate and confirmed duplicate rate;
- sampled match precision and recall, with evaluation-set caveats;
- false-merge and unmerge rates, severity-weighted where appropriate;
- percentage of CDE attributes with documented owner, rule and provenance;
- unresolved conflict count, age and criticality;
- steward queue throughput and median/p95 time to decision;
- source-to-master and master-to-consumer propagation lag;
- failed publication, replay and reconciliation rates;
- percentage of consumers that support merge/unmerge events and version checks.

A rising merge count alone is not proof of improvement. It may indicate more duplicates, a looser threshold, a source migration or an algorithm change. Track policy version and denominator.

## 9. Security, privacy, retention and auditability

MDM can concentrate sensitive attributes and cross-system relationships. A golden record may make it easier to infer a person's activity, so a hub should not automatically expose every mastered attribute to every consumer.

### 9.1 Controls to design

- **Purpose limitation:** consumers receive only attributes needed for an approved purpose. Marketing, service, fraud and legal workflows may have different permitted views.
- **Least privilege:** role- and attribute-level access; restrict sensitive source evidence, identity documents, contact details and steward tools.
- **Separation of duties:** policy authors, approvers, operators and reviewers should be separated where risk warrants it.
- **Encryption and secrets:** protect data in transit and at rest; use managed key practices appropriate to the platform; do not embed secrets in code or event payloads.
- **Data minimization:** keep only the provenance and evidence needed to explain decisions; prefer protected references to duplicated raw documents.
- **Retention and deletion:** define retention per attribute, source copy, event, audit and legal hold. Propagate deletion/tombstone obligations to downstream copies where required; distinguish deletion of a value from retention of a minimal decision audit trail.
- **Residency and transfer:** document where source records, golden attributes, matching features, backups and logs are processed or stored, according to applicable policy and law.
- **Auditability:** log who/what changed a value, which policy ran, what evidence was considered, what was published and whether consumers applied it. Protect audit logs from unauthorized alteration.
- **Sensitive matching features:** use only appropriate, authorized features; do not collect extra sensitive attributes merely because they improve a model score.

### 9.2 Wrong merge as a privacy and operational incident

If two different people are merged, the response is not simply “run unmerge.” Freeze risky downstream propagation where feasible, identify affected master versions and consumers through lineage, restrict exposure, preserve the decision evidence, execute a controlled unmerge, publish correction events, reconcile consumers and assess whether disclosure or regulatory response obligations apply. The exact response is governed by the organization's incident and privacy procedures.

## 10. Intermediate and advanced architecture decisions

### 10.1 Consistency, autonomy, latency and central control

A single hub can reduce divergence but adds a dependency and may constrain local workflows. A registry preserves source autonomy but often makes every query depend on multiple sources. Event-driven coexistence improves freshness but introduces ordering, retry, conflict and replay complexity. Batch consolidation is simpler and cheaper but may be too stale for operational decisions.

Architecture decisions should state the acceptable staleness by attribute and consumer. “Real time” is not a requirement until it is quantified and tied to a business outcome. Some attributes—such as marketing preference—may need rapid propagation; a historical reporting dimension may tolerate a daily update. Avoid paying for low latency everywhere when only a small subset of fields needs it.

### 10.2 Identity decisions have asymmetric risk

False merges can be more damaging than missed matches, especially when data is sensitive or drives account access, fraud, credit, health, legal or regulatory decisions. Choose automation thresholds by domain and consequence. Keep review bands, sampling, rollback, and a safe “unknown” state. Never use match score alone as the authority to overwrite critical attributes.

### 10.3 Performance and scale

Candidate generation, normalization, cross-system lookups, provenance history and downstream fan-out can dominate cost. Use blocking and incremental matching, but measure missed-match risk introduced by blocking. Partition by safe stable keys where useful; avoid using mutable PII as a permanent partition key. Cache only with defined invalidation and freshness behavior. Use a queue and steward capacity model when uncertain pairs are routed for review.

**Illustrative capacity calculation:** suppose a batch has 100,000 candidate pairs, of which 85% are auto-resolved, 12% require review and 3% are rejected. Review workload is 100,000 × 0.12 = 12,000 pairs. At two minutes per pair, that is 24,000 minutes ÷ 60 = **400 staff-hours**, before overhead, rework and escalations. These percentages and review time are hypothetical; production planning should use observed distributions and account for complexity bands.

### 10.4 Analytics, ML features and AI entity consistency

Stable mastered IDs and traceable crosswalks reduce duplicate counting and join fragmentation. A consistent product hierarchy improves metrics and feature joins. A governed customer identity can reduce duplicate feature rows, but a false merge can contaminate labels, combine unrelated histories and leak information across entities.

For ML, record entity-resolution version, feature timestamps, master version and point-in-time semantics. Prevent target leakage: a current golden attribute may not have been known at the prediction time. If a merge is corrected, identify affected training examples, feature tables, evaluation sets and model decisions. For AI retrieval and generation, use stable entity IDs, source citations/lineage, access-filtered retrieval and explicit ambiguity handling. The model should not treat two similar names as one entity without a supported resolution decision.

### 10.5 Build versus buy and operating model

Evaluate capabilities rather than product names: source connectors, matching configuration, steward workflow, provenance, lifecycle history, event/API integration, privacy controls, versioning, monitoring, exportability and cost at expected scale. Consider build effort, operational ownership, data portability and lock-in. A tool does not decide the business definition of customer or resolve governance disputes automatically.

### 10.6 Architecture decision record (ADR) template

```markdown
# ADR: MDM style for the customer domain

- Status: Proposed / Accepted / Superseded
- Context: business use cases, source systems, data sensitivity, constraints
- Decision drivers: latency, source autonomy, false-merge risk, audit, cost
- Options considered: registry, consolidation, coexistence, centralized
- Decision: selected pattern and scope by attribute/use case
- Survivorship: policy version, attribute-specific rules, review thresholds
- Identity: identifier namespace, crosswalk, merge/link/unmerge policy
- Synchronization: event/API/batch, idempotency, lag, replay, reconciliation
- Governance: owner, steward, escalation, quality and privacy controls
- Consequences: benefits, costs, failure modes, rejected alternatives
- Validation: synthetic test cases, metrics, rollout and rollback conditions
```

## 11. Worked synthetic example: Northbridge customer golden record

### 11.1 Scenario and limits

Northbridge Bank uses three fictional systems:

- **CORE:** onboarding and core account platform; has customer ID and verified identity attributes.
- **CARD:** card servicing; has a cardholder ID and delivery/contact data.
- **CRM:** customer relationship management; has a CRM contact ID, preferred display name and contact preferences.

The following rows are synthetic. They are **candidate records**; their presence in one table does not prove they refer to the same person. The matching decision is illustrative and would require approved evidence and review in a real system.

### 11.2 Source records

| Source | Source ID | Legal/display name | Date of birth | Email | Address | Evidence / timestamps |
|---|---|---|---|---|---|---|
| CORE | C-0081 | Asha Mehta | 1988-04-12 | asha.m@example.test | 14 Lake Road, Kolkata | Legal name and DOB verified during onboarding; email verification is assumed for this synthetic example; address verified 2025-11-10 |
| CARD | K-4419 | Asha M. | 1988-04-12 | asha.m@example.test | 14 Lake Rd, Kolkata | DOB and email copied from linked onboarding payload (not independent verification); address entered for card delivery, not separately verified; observed 2026-01-12 |
| CRM | R-2097 | Asha | 1988-04-12 | asha.alt@example.test | 22 Park Street, Kolkata | Preferred name entered by agent; DOB copied from CRM profile and not independently verified; address changed 2026-01-14 without verification evidence; email not verified |

`example.test` is a reserved example domain. No row represents a real person.

### 11.3 Match evidence and decision

Evidence supporting a possible match:

- exact date-of-birth values across three records, treated as consistency evidence rather than three independent confirmations because CARD copied the CORE onboarding payload and CRM's value is not independently verified;
- exact email in CORE and CARD, with CARD's value copied from the linked onboarding payload rather than independently verified;
- CARD's onboarding payload indicates a link to CORE's customer ID (assumed synthetic source lineage); and
- name variants are compatible but not sufficient by themselves.

Evidence requiring caution:

- CRM's alternate email is unverified;
- CRM's later address conflicts with CORE's verified address;
- common name plus date of birth alone would not be adequate proof; and
- a source link may be stale or misconfigured and should be validated.

**Illustrative outcome:** policy accepts CORE↔CARD as a high-confidence link because the trusted onboarding cross-reference and consistent attributes agree. The copied DOB/email values are not counted as independent confirmations; this is still only an illustrative policy outcome, not verified real-world identity. CRM remains a candidate pending review until a permitted stable cross-reference or additional evidence is verified. For teaching the attribute rules below, assume a steward later confirms CRM refers to the same customer using an authorized verification workflow. This assumption is explicit; the example does not claim a real-world identity has been verified.

Master ID assigned: `PTY-10482` (opaque synthetic ID). Crosswalks:

| Source system | Source ID | Initial relationship | Decision |
|---|---|---|---|
| CORE | C-0081 | Confirmed | Onboarding cross-reference and corroborating evidence |
| CARD | K-4419 | Confirmed | Trusted linked source record; corroborating DOB/email |
| CRM | R-2097 | Provisional, then confirmed after steward review | Initially uncertain; confirmed only under the stated synthetic assumption |

### 11.4 Survivorship table and selected attributes

| Attribute | Selected value | Winning source/provenance | Rule applied | Status / uncertainty |
|---|---|---|---|---|
| Legal name | Asha Mehta | CORE.C-0081 legal-name field; onboarding evidence `VERIFIED` | Verified legal evidence wins; CRM/CARD display labels are not legal-name candidates | Verified for this illustrative use; rule version `cust-v1` |
| Preferred display name | Asha | CRM.R-2097 preferred-name field | Explicit preference from authorized CRM workflow wins over legal name for display use | Source-asserted preference; review if customer disputes |
| Date of birth | 1988-04-12 | CORE.C-0081 DOB, corroborated by CARD and CRM | Use verified CORE value; corroboration supports identity but does not create three independent verified sources | Verified from CORE; other values are corroborating evidence |
| Email | asha.m@example.test | CORE.C-0081 email | Require verified contact value; unverified alternate email is not allowed to replace it | Verification is an explicit synthetic assumption for CORE; CARD is copied evidence, not independent corroboration |
| Residential address | 14 Lake Road, Kolkata | CORE.C-0081 address, verified 2025-11-10 | Most recent **eligible verified** address wins; newer unverified CRM address does not override | Verified as of 2025-11-10; not proof it remains current on every later date |
| Alternate email | asha.alt@example.test | CRM.R-2097, retained as candidate contact point | Do not collapse to primary email; require verification before primary promotion | Unverified / pending verification |
| Source identities | CORE:C-0081; CARD:K-4419; CRM:R-2097 | Crosswalk table | Preserve source namespace and mapping history | Confirmed only under the assumptions above |

Notice the policy does not choose the most recent record or the most complete row. It uses the right evidence for each attribute and preserves uncertainty where verification is missing.

### 11.5 Example golden-record JSON

```json
{
  "master_id": "PTY-10482",
  "domain": "customer",
  "status": "ACTIVE",
  "master_version": 17,
  "rule_version": "cust-v1",
  "attributes": {
    "legal_name": {
      "value": "Asha Mehta",
      "status": "VERIFIED",
      "provenance_ref": "prov-name-001",
      "reason": "Verified CORE legal-name evidence outranks display labels"
    },
    "preferred_display_name": {
      "value": "Asha",
      "status": "SOURCE_ASSERTED",
      "provenance_ref": "prov-display-003",
      "reason": "Authorized CRM preference applies to display context"
    },
    "date_of_birth": {
      "value": "1988-04-12",
      "status": "VERIFIED",
      "provenance_ref": "prov-dob-002",
      "reason": "Verified CORE value; other records corroborate"
    },
    "email": {
      "value": "asha.m@example.test",
      "status": "VERIFIED",
      "provenance_ref": "prov-email-001",
      "reason": "CORE email verification is assumed for this synthetic example; CARD copied the value from the onboarding payload"
    },
    "alternate_email": {
      "value": "asha.alt@example.test",
      "status": "PENDING_VERIFICATION",
      "provenance_ref": "prov-email-alt-003",
      "reason": "Retained as a candidate contact point; not eligible to replace the primary email"
    },
    "residential_address": {
      "value": "14 Lake Road, Kolkata",
      "status": "VERIFIED_AS_OF_DATE",
      "effective_at": "2025-11-10",
      "provenance_ref": "prov-address-004",
      "reason": "Only eligible verified candidate; newer CRM value is unverified. This does not prove currentness beyond the verification date"
    }
  },
  "source_crosswalk_refs": ["xw-core-0081", "xw-card-4419", "xw-crm-2097"]
}
```

In production, sensitive values and references should be protected according to purpose and role. A log or event may carry a provenance reference rather than duplicating a full address, date of birth or email. The JSON is illustrative; it is not a complete API contract.

### 11.6 Pseudocode for survivorship

The following is **language-neutral pseudocode**, not executable Python. It illustrates the rule order and intentionally routes critical unresolved conflicts to stewardship.

```text
function select_attribute(attribute, candidates, policy):
    eligible = candidates filtered by policy.eligibility
    eligible = eligible filtered by policy.validation

    if eligible is empty:
        return UNKNOWN with reason "no eligible candidate"

    if policy.requires_verified and no eligible candidate is verified:
        return PENDING_REVIEW or UNKNOWN according to policy

    eligible = keep candidates in the highest allowed evidence class
    eligible = keep candidates allowed by attribute-specific source policy
    eligible = apply effective-time/freshness rule defined by policy

    if one candidate remains:
        return its value plus provenance and policy version

    if remaining candidates materially conflict:
        return PENDING_REVIEW with candidate references and reasons

    apply documented deterministic tie-break only if policy permits it
    if tie-break cannot resolve safely:
        return PENDING_REVIEW

    return selected value plus source, timestamps, evidence and decision reason
```

**Inputs:** candidate values with source, source ID, verification status, validity, observed/effective time and quality results; a versioned attribute policy. **Outputs:** selected value/status plus provenance or an explicit unknown/review state. **Assumptions:** candidate identity has already passed the applicable resolution policy; attribute selection does not itself prove identity. **Error cases:** no eligible values, invalid data, contradictory verified evidence, missing timestamps, unsupported policy version, and source outage. **Tie-breaking:** only use a stable tie-break after business eligibility/evidence rules and only when a tie is safe; otherwise send to a steward. **Security:** minimize candidate data in logs and apply attribute-level authorization.

### 11.7 Python example: deterministic, review-aware selection

This example is executable Python 3 using only the standard library. It implements a deliberately small teaching policy for residential addresses. It is not a general-purpose MDM engine and does not perform entity matching.

```python
from dataclasses import dataclass
from datetime import date
from typing import Optional, Sequence

@dataclass(frozen=True)
class AddressCandidate:
    source: str
    source_id: str
    value: str
    verified: bool
    effective_date: Optional[date]

@dataclass(frozen=True)
class Selection:
    status: str
    value: Optional[str]
    source: Optional[str]
    source_id: Optional[str]
    reason: str

def choose_address(candidates: Sequence[AddressCandidate]) -> Selection:
    # Null/blank values are not deletion commands and cannot win.
    eligible = [c for c in candidates if c.value and c.value.strip()]
    eligible = [c for c in eligible if c.verified and c.effective_date is not None]

    if not eligible:
        return Selection("UNKNOWN", None, None, None,
                         "No nonblank, verified candidate with effective date")

    newest_date = max(c.effective_date for c in eligible)
    newest = [c for c in eligible if c.effective_date == newest_date]

    # Conflicting verified values at the same effective date need stewardship.
    distinct_values = {c.value.strip() for c in newest}
    if len(distinct_values) > 1:
        return Selection("PENDING_REVIEW", None, None, None,
                         "Conflicting verified values share the newest effective date")

    # Stable tie-break among equivalent values makes provenance deterministic.
    winner = sorted(newest, key=lambda c: (c.source, c.source_id))[0]
    return Selection("SELECTED", winner.value.strip(), winner.source,
                     winner.source_id,
                     "Newest eligible verified value; stable source-key tie-break")

if __name__ == "__main__":
    candidates = [
        AddressCandidate("CORE", "C-0081", "14 Lake Road, Kolkata", True,
                         date(2025, 11, 10)),
        AddressCandidate("CRM", "R-2097", "22 Park Street, Kolkata", False,
                         date(2026, 1, 14)),
    ]
    result = choose_address(candidates)
    assert result.status == "SELECTED"
    assert result.value == "14 Lake Road, Kolkata"
    assert result.source == "CORE"
    print(result)
```

The policy first filters for nonblank, verified candidates with an effective date. The newer CRM value is unverified and is therefore ineligible; it cannot win just because it is newer. If two different verified addresses share the newest effective date, the function returns `PENDING_REVIEW` rather than inventing authority. The source-key tie-break is used only when the remaining values are equivalent. A production implementation would add policy versioning, source eligibility, effective-time semantics, typed values, privacy controls, event history, metrics and tests for time zones and source corrections.

### 11.8 Merge, link, unmerge and downstream effects

**Initial merge:** CORE and CARD are linked to `PTY-10482` after the stated synthetic evidence passes policy. CRM is initially provisional; a steward later confirms it under the exercise assumption. Each decision has an ID, evidence reference and policy version. Original source IDs remain unchanged.

**Link instead of merge:** if the evidence only established that two CRM records represented members of the same household, create a `HOUSEHOLD_MEMBER_OF` relationship. Do not merge their identities.

**Wrong merge discovered:** suppose the steward later finds that CRM.R-2097 actually belonged to a different synthetic person because an imported cross-reference was wrong. Recovery must be a first-class workflow:

1. Place the affected identity/relationship into a controlled review state and stop unsafe propagation where feasible.
2. Record an unmerge decision referencing the original merge and the new evidence.
3. Create a new master ID for the distinct entity, or reactivate an ID only if evidence proves it belongs to that same historical entity; never reuse an ID for a different entity.
4. Reassign CRM.R-2097's crosswalk to the correct entity with valid-time history.
5. Recompute affected attributes and provenance for both master records; remove only values that came from the wrongly merged source, not unrelated valid history.
6. Publish versioned correction/unmerge events, with a correlation ID and minimal sensitive payload.
7. Consumers apply corrections idempotently, retain old-to-new identity mapping as policy requires, and reconcile references.
8. Use lineage to identify affected reports, extracts, ML feature tables, retrieval indexes and decisions; assess privacy/operational incident obligations.
9. Verify completion and close only when critical consumers are reconciled or have documented exceptions.

A merge is not safely reversible if the system overwrote source data, discarded provenance, reused identifiers or never recorded which consumers received the original decision. Reversibility is designed in advance, not improvised after an incident.

### 11.9 Consumer reconciliation example

Consumer `CUSTOMER_360` last applied master version 16. It receives version 17 twice because the event broker retries delivery. The consumer uses `event_id` for idempotency and stores the highest applied version per `master_id`; the duplicate does not create a second update. If version 19 arrives before version 18, the consumer either fetches the current master snapshot or queues the gap for ordered replay according to its contract. A nightly reconciliation compares master IDs and versions, flags stale copies, and triggers safe replay. On unmerge, the consumer processes an explicit correction event rather than assuming that a merge event can simply be deleted.

## 12. Data quality rules for master records and CDE prioritization

Master data quality is use-specific. Completeness alone is not quality; a verified but old address may be more trustworthy than a newer unverified one, while an address that is valid for a mailing purpose may not be valid as a residence.

| Attribute / CDE candidate | Example rule | Severity rationale | Owner / response |
|---|---|---|---|
| Master ID | Unique, immutable and never reassigned to a different entity | Critical identity integrity | MDM service owner; block commit |
| Crosswalk | One active mapping per source-record identity unless a documented temporal/link model permits otherwise | Prevents ambiguous joins | MDM owner; quarantine conflict |
| Legal name | Nonblank where required; source evidence and verification status recorded | Legal/reporting impact | Domain owner; steward review |
| Date of birth (if collected/allowed) | Valid date and consistent with required source policy; restrict use and access | Sensitive, identity-impacting | Owner + privacy control; reject or review |
| Address | Structure/format validation plus verification status and effective time | Delivery, residency, compliance use | Address steward; distinguish invalid from unverified |
| Consent/permission | Purpose, jurisdiction, source, effective time and status are explicit | Unauthorized contact/use risk | Consent owner; conservative policy on conflict |
| Product status | Valid code from effective-dated reference set | Sales, inventory and reporting impact | Product owner; reject unknown code |
| Publication version | Consumer version cannot silently move backward | Stale downstream decisions | Consumer owner; alert and reconcile |

Prioritize CDEs using impact, likelihood, detectability, regulatory/privacy sensitivity and downstream fan-out. A field used in a critical decision can be high priority even if it is rarely populated. Rules need a measurable condition, scope, threshold, owner, remediation path and monitoring. Tie quality checks to Topic 04's CDE register and Topic 05's monitoring/incident practices.

## 13. Exercises and expected deliverables

### Exercise A — Golden-record model (recommended roadmap exercise)

**Scenario:** Northbridge has customer records in CORE, CARD and CRM. Use approximately 20 synthetic rows across the three sources; include duplicates, incomplete values, conflicting addresses, different names, unverified contact points and at least one non-match pair.

**Tasks:**

1. Define the customer domain and distinguish master, transaction, reference and metadata fields.
2. Inventory source IDs, source-of-record boundaries, owner/steward and authoritative source by attribute.
3. Define golden-record attributes, statuses, source crosswalk, provenance, lifecycle and versioning.
4. Specify attribute-level survivorship including eligibility, verification, source precedence, time, null handling, tie-breaks and steward escalation.
5. Document identity evidence separately from attribute selection; classify uncertain pairs as review/link/non-match rather than forcing a merge.
6. Produce at least five sample outcomes and explain why each selected value won.

**Deliverables:** master-domain list; golden-record model; survivorship table; identity-decision register; sample golden-record records; steward flags.

**Validation:** every attribute has a definition, rule, source/provenance and uncertainty behavior. No rule assumes “latest wins” or “most complete wins” globally.

### Exercise B — Conflict resolution and synchronization (recommended roadmap exercise)

Apply the rules to five conflicts, including a newer unverified address, two conflicting verified values, a null update, an explicit deletion request and a wrong merge. Design the event/API/batch contract, consumer idempotency and version behavior, reconciliation, replay, merge/unmerge and privacy controls.

**Deliverables:** conflict log; synchronization diagram or sequence; sample change event; consumer contract; unmerge runbook; reconciliation checklist.

**Validation:** every decision is traceable to evidence and a rule version; downstream effects are identified; wrong-merge recovery is defined and testable.

### 13.1 Golden-record model deliverable template

| Model field | Required design answer |
|---|---|
| Domain / entity type | What entity does one master ID represent? |
| Master ID policy | Namespace, assignment, immutability, retirement and alias/crosswalk behavior |
| Source records | Source system, source ID, version, status, observed/effective time |
| Attributes | Definition, type, sensitivity, requiredness, effective-time semantics |
| Survivorship | Eligibility, evidence, source policy, time rule, null handling, tie-break, escalation |
| Provenance | Source field, source version/event, rule version, reason, decision ID |
| Identity decisions | Match evidence, thresholds, confidence meaning, reviewer, link/merge/non-match outcome |
| Lifecycle | Create/update/merge/link/unmerge/retire and state transitions |
| Quality | CDEs, rules, thresholds, owners, remediation and monitoring |
| Consumers | Purpose, fields, identifier mapping, latency, schema, idempotency and reconciliation |
| Security/privacy | Access, minimization, retention, residency, audit and deletion propagation |
| Operations | KPIs, SLOs, alert routing, recovery and stewardship capacity |

### 13.2 Survivorship and conflict log template

| Decision ID | Master ID / attribute | Candidate sources | Evidence and validation | Rule version | Outcome | Reason / uncertainty | Steward action | Consumer impact |
|---|---|---|---|---|---|---|---|---|
| `DEC-...` | `PTY-... / attribute` | `SYS:id; SYS:id` | `verified/unverified; valid/stale` | `rule-vN` | `selected/review/unknown` | `explainable rationale` | `none/review/approved` | `events/replay/reconciliation` |

### 13.3 Synchronization design checklist

- [ ] Master changes have a stable event ID and master version.
- [ ] State commit and publication are coordinated (for example, transactional outbox where appropriate).
- [ ] Consumers handle duplicate, delayed, out-of-order and replayed messages.
- [ ] Schema compatibility and event versioning are defined.
- [ ] Maximum propagation lag and monitoring are defined per use case.
- [ ] Snapshot/delta handoff and reconciliation are defined.
- [ ] Merge and unmerge events are explicit and idempotent.
- [ ] Consumers that cannot adopt master IDs have a supported crosswalk strategy.
- [ ] Sensitive values are minimized in payloads/logs; access and retention are defined.
- [ ] Failed consumers have an owner, runbook, retry policy and recovery evidence.

### 13.4 Stewardship model and KPI deliverable

Document the domain owner, steward queue, source-system responsibilities, approval rights, exception severity, escalation path and response targets. Define metrics with numerator, denominator, time window, owner and interpretation. Do not set universal targets without baseline data and business risk analysis.

### 13.5 ADR deliverable

Use the template in Section 10.6. The ADR must explain why the selected pattern fits the business use case, which attributes are centrally governed, how source autonomy is preserved or reduced, what happens on wrong merge, and how consumers reconcile changes.

## 14. Realistic failure modes and common misconceptions

| Mistake | Why it fails | Better practice |
|---|---|---|
| Treating the golden record as unquestionable truth | Rules can be wrong, sources stale and use cases different | State purpose, provenance, confidence and exceptions |
| One global source priority | Authority varies by attribute and context | Maintain attribute-specific policies |
| Latest-wins survivorship | Newest can be unverified, erroneous or late-arriving | Use evidence eligibility, effective time and freshness rules |
| Most-complete-record wins | Completeness does not establish correctness | Score each attribute under its own policy |
| Merge on name similarity alone | Common names and shared addresses create false matches | Use permitted corroborating evidence and review thresholds |
| Match score treated as identity proof | Score is a model/rule output with uncertainty | Store evidence, calibrated meaning, threshold version and decision |
| Merge physically deletes source records | Destroys traceability and makes unmerge difficult | Preserve source IDs, decisions, history and crosswalks |
| Link and merge treated as synonyms | Relationships are not identity equivalence | Model typed relationships separately |
| Null means delete | Partial updates can erase valid data accidentally | Distinguish absent, null, invalid and explicit deletion commands |
| Consumers assumed to update automatically | Events fail, consumers lag and schemas evolve | Contract, retries, idempotency, reconciliation and ownership |
| Only hub is monitored | Consumers can remain stale without detection | Monitor end-to-end propagation and consumer versions |
| Privacy considered after centralization | Hub increases exposure and inference risk | Purpose limitation, minimization, attribute access and deletion propagation by design |
| MDM treated as an IT-only project | Business definitions and stewardship remain unresolved | Business owner and steward approve semantics and conflict policies |
| Metrics use raw counts without denominators | Counts move with volume, thresholds and source migrations | Use defined rates, cohorts, policy versions and quality sampling |
| AI/ML assumes mastered identity is always correct | Wrong merges contaminate features, labels and retrieval | Version entity resolution, preserve lineage and support correction/backfill |

## 15. Mastery criteria and completion gate

### 15.1 Mastery criteria

You should be able to:

- explain MDM styles and select one with explicit decision criteria;
- distinguish master data, transactional data, reference data, identifiers, matching and metadata;
- define a golden-record model with source crosswalks, status, versioning and attribute provenance;
- define deterministic survivorship per attribute and explain null, invalid, stale, verified and conflicting values;
- explain why source precedence, recency, completeness and match score are not universal answers;
- distinguish merge, link, non-match and unmerge and design recovery from a wrong merge;
- design synchronization and consumer behavior for duplicates, ordering, replay, schema evolution and reconciliation;
- identify privacy/security risks and purpose-specific views of the golden record;
- connect master data CDEs to quality rules, observability, lineage, analytics and AI;
- deliver a defensible ADR and a stewardship/KPI model.

### 15.2 Completion gate

Do not mark Topic 06 complete until all items below are satisfied:

- [ ] Domain list and authoritative sources are documented, with ownership and stewardship.
- [ ] Golden-record model includes provenance and lifecycle status.
- [ ] Survivorship and conflict-resolution rules are defined per attribute.
- [ ] Sample outcomes are reproducible and explainable from stated rules.
- [ ] Match decisions distinguish evidence, confidence, identity and attribute selection.
- [ ] Wrong-merge recovery and unmerge are defined, including downstream consumers.
- [ ] Synchronization design covers publication, idempotency, replay and reconciliation.
- [ ] Privacy, purpose, access, retention and auditability are addressed.
- [ ] The ADR explains the chosen MDM pattern and rejected alternatives.
- [ ] You can state where the golden record is not authoritative.
- [ ] The “single rule for all attributes” weakness has been addressed with attribute-level survivorship.
- [ ] **Topic 07 Beginner level has been studied before Topic 06 Advanced-level work.**

### 15.3 Final-project integration

The module's proposed final project, `Projects/11-enterprise-metadata-and-lineage-design.md`, integrates all eight topics. Topic 06–07 contributions should include:

- customer master-data domain and authoritative-source inventory;
- golden-record model, attribute-level survivorship and provenance;
- identity matching rules, identifier namespace and source crosswalks;
- conflict log, quality/CDE rules and steward workflow;
- synchronization, consumer reconciliation and merge/unmerge design;
- links to lineage so a reviewer can trace a wrong report value to the source, rule, owner and affected consumers;
- interoperability mapping for the master ID, source identifiers, attribute metadata and policy/version fields.

The roadmap notes that the final-project files were empty when it was authored, so this is aligned guidance, not a claim that an existing project specification imposes additional requirements. If the project file later receives its own specification, that specification governs.

## 16. Revision checklist

Use this checklist when reviewing the document or revising your own design.

### Scope and semantics
- [ ] Master vs transactional vs reference vs metadata vs identifier are distinct.
- [ ] Domain and purpose are defined; not every field is assumed globally authoritative.
- [ ] Source-of-record and attribute-level authority are not conflated.

### Identity and survivorship
- [ ] Identity match evidence is separate from attribute survivorship.
- [ ] Rules are explicit, versioned, deterministic where safe, and have review fallbacks.
- [ ] Null, invalid, stale, verified, conflicting and explicit deletion cases differ.
- [ ] Provenance explains the selected value and the rule/evidence used.
- [ ] Confidence is qualified and not presented as certainty.

### Lifecycle and synchronization
- [ ] Create/update/merge/link/unmerge/retire transitions are defined.
- [ ] Stable identifiers and crosswalk history are preserved.
- [ ] Events and consumers handle duplicates, order, retries, replay and reconciliation.
- [ ] Wrong-merge correction includes downstream data, reports and ML/AI impact.

### Governance and risk
- [ ] Owner, steward, source owner and consumer responsibilities are named.
- [ ] CDEs, quality checks, KPIs and response paths are measurable.
- [ ] Purpose limitation, least privilege, retention, deletion, residency and audit are addressed.
- [ ] Trade-offs are justified against use cases and operational constraints.

### Learning sequence and deliverables
- [ ] Topic 07 Beginner dependency before Topic 06 Advanced is explicit.
- [ ] Golden-record model, survivorship table, conflict log, sync/unmerge design, stewardship/KPIs and ADR are present.
- [ ] Exercises use synthetic data and outcomes are reproducible.
- [ ] Completion gate can be evaluated by a reviewer without guessing intent.

## 17. Practice questions

1. Why is a golden record a governed view rather than guaranteed truth?
2. Give an example where the newest source value should not win.
3. How does a source-of-record designation differ from attribute-level authority?
4. When is a registry pattern preferable to consolidation? When would it be insufficient?
5. What information must be retained to explain why an attribute won?
6. How can blocking improve matching performance while reducing recall?
7. Explain the difference between a false match, a missed match, a link and a merge.
8. Why must a null update not automatically clear a current mastered value?
9. What makes unmerge a cross-system workflow rather than a database update?
10. How should a consumer process duplicate and out-of-order master events?
11. Which controls reduce the privacy risk of a centralized golden record?
12. How can wrong identity merges contaminate analytics, ML features and AI retrieval?
13. What metrics would you use to evaluate match quality and steward capacity, and what are their limitations?
14. Which parts of an MDM policy require business ownership rather than a technical default?
15. Explain why Topic 07 Beginner is a dependency for Topic 06 Advanced even though Topic 06 retains the lower numeric filename.

## 18. Summary

MDM creates governed consistency around important entities, but it cannot eliminate uncertainty or replace business accountability. Safe golden records depend on stable identifiers, explicit identity decisions, attribute-specific survivorship, provenance, lifecycle history, stewardship, quality controls, privacy protections and reliable synchronization. The strongest design is not the most centralized one by default; it is the least complex pattern that meets the business risk, consistency, autonomy and latency requirements—and that can explain, correct and propagate its decisions when the evidence changes.
