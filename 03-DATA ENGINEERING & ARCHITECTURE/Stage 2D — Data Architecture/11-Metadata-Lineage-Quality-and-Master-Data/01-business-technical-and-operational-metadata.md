# 01 — Business, Technical and Operational Metadata

> **Module:** Stage 2D — Data Architecture / `11-Metadata-Lineage-Quality-and-Master-Data/`  
> **Learning sequence:** Topic 01 of 8  
> **Level:** Beginner → Intermediate → Advanced  
> **Scenario:** Northbridge Bank — fictional; all records and measurements below are synthetic and illustrative.

## Document status and source-of-truth note

This lesson follows the Topic 01 scope in `roadmap-Metadata-Lineage-Quality-and-Master-Data.md`. The supplied roadmap says the eight topic files, module `README.md`, `practice-questions.md`, `Projects/README.md`, and `Projects/11-enterprise-metadata-and-lineage-design.md` were empty when the roadmap was authored. Therefore, the roadmap is the available instructional source of truth; this document does **not** claim to reproduce requirements from those empty files. The exercises, schema, thresholds, example roles, and architecture decisions in this lesson are recommended learning artefacts. If those repository files are later populated, reconcile this lesson with their contents.

## 1. Purpose, scope, prerequisites and learning outcomes

### 1.1 Purpose

Metadata is the descriptive and control layer that helps an organisation find, interpret, govern, operate, and safely change its data assets. This topic establishes the foundation for the rest of Module 2D.11: catalogues and discovery, lineage, quality, observability, master data, and metadata interoperability.

This lesson focuses on **business, technical, and operational metadata**; how they relate; how they are modelled and maintained; and how to measure their quality. It does not attempt to teach the later topics in full.

### 1.2 Scope

In scope:

- Metadata concepts, records, schemas, attributes, relationships, and repositories.
- Business, technical, and operational metadata and their interactions.
- Asset- and column-level metadata modelling.
- Collection, curation, derivation, lifecycle, accountability, and quality.
- Metadata security, versioning, scale, retention, and cost.
- Practical inventory, schema, quality indicators, responsibility matrix, and an architecture decision record (ADR).

Out of scope for detailed treatment: complete catalogue UX, full lineage algorithms, detailed data-quality engineering, master-data matching, and standards conformance. These are later topics in the module.

### 1.3 Prerequisites

The roadmap names P1, P4, and P6 as Topic 01 prerequisites:

| Prerequisite | Expected working knowledge | Quick check |
|---|---|---|
| P1 — Ownership and governance | Domains, data owners, stewards, decision rights | Explain who approves a definition versus who operates a pipeline. |
| P4 — Data modelling | Entities, attributes, keys, data types, data dictionaries, schema evolution | Describe a table, its columns, and its primary key. |
| P6 — Platform metadata | Catalogues, metastores, platform layers, tenancy | Explain where table schema metadata may be harvested from. |

Classification, policy enforcement, contracts, freshness/SLOs, streaming, portability, and ADRs also appear in the wider module roadmap. Review the relevant earlier module if those concepts are unfamiliar; do not assume vendor-specific knowledge.

### 1.4 Learning outcomes

After completing this topic, you should be able to:

1. Define business, technical, and operational metadata and classify individual metadata items with reasons.
2. Explain ownership and stewardship responsibilities.
3. Describe how metadata is created, harvested, curated, derived, updated, reviewed, deprecated, and retired.
4. Explain how metadata categories jointly support discovery, governance, troubleshooting, and operations.
5. Build a small metadata inventory and a metadata schema for tables and columns.
6. Identify missing, stale, conflicting, inaccurate, or inconsistent metadata and propose remediation.
7. Define measurable indicators for metadata completeness, accuracy, timeliness, and consistency.
8. Defend basic architecture choices around automation, mandatory fields, security, versioning, retention, and cost.

## 2. Beginner foundations and terminology

### 2.1 What is metadata?

**Metadata is information that describes a data asset and its context.** It can describe what the asset means, how it is structured and located, who is responsible, how it was produced, and how it is behaving.

- **What it is:** descriptive information about datasets, tables, columns, files, reports, pipelines, models, and other assets.
- **Why it matters:** without it, people cannot reliably discover assets, interpret fields, determine access suitability, understand dependencies, or diagnose failures.
- **How it works:** metadata is collected from systems, supplied by accountable people, or derived from observed events and rules; it is stored and connected in a metadata repository and surfaced through tools such as a catalogue.
- **When to use it:** whenever data must be found, understood, governed, monitored, audited, reused, or changed safely.
- **Trade-off:** metadata capture and maintenance require effort, but missing or misleading metadata create downstream search, risk, and operational costs.
- **Enterprise example:** an analyst sees a `customer` table. Metadata explains the meaning of “active customer,” its accountable owner, its columns and key, its classification, and when it was last refreshed.

A useful analogy is a library record. The summary and subject terms explain what a book is about; the shelf location and edition describe its structure and location; circulation history describes how it is used and whether it is available. These are different perspectives on one asset.

### 2.2 Core terms

| Term | Meaning | Example |
|---|---|---|
| Data asset | A managed object worth discovering or governing | Table, column, dashboard, pipeline, model |
| Metadata record | A record describing one asset or one related observation | Record for `curated.customer` |
| Attribute | A named property on a record | `owner_team`, `data_type`, `last_success_at` |
| Metadata schema | Rules defining fields, types, relationships, and requiredness | Table records must include a stable ID and source location |
| Metadata repository | A store that persists metadata records and relationships | Catalogue backend or metadata service |
| Identifier | Stable key used to refer to an asset | `urn:example:table:curated.customer` |
| Relationship | A typed link between records | Column belongs to table; pipeline reads table |
| Harvesting | Automated collection from a source system | Read table schema from a database catalogue |
| Curation | Human review or authoring of meaning and governance | Steward approves a definition |
| Derived metadata | Metadata calculated from other facts or observations | Usage tier derived from query logs |
| Freshness | How recently metadata was collected or reviewed relative to expectation | Last schema harvest 20 minutes ago |
| Completeness | Whether required metadata is present | 9 of 10 critical tables have owners |
| Accuracy | Whether metadata reflects reality | Recorded type matches the actual column type |
| Consistency | Whether representations agree across systems | Same asset has aligned classification in catalogue and policy registry |
| Deprecation | Marking an asset as no longer recommended while retaining context | Table scheduled for replacement |
| Retirement | Removing an asset from active use after dependencies and retention are addressed | Archive catalogue entry after approved shutdown |

### 2.3 Asset, record, schema, and repository are not the same thing

- An **asset** is the thing being described.
- A **metadata record** is the representation of that asset in the metadata system.
- A **metadata schema** defines what that representation can contain and how it relates to other records.
- A **metadata repository** stores records and supports retrieval, updates, and relationships.
- A **catalogue** is commonly the user-facing discovery and understanding experience over metadata. It may share storage with a repository, but its user experience and governance workflows are distinct responsibilities.

For example, a physical database table is an asset; its catalogue entry is a metadata record; the `TableAsset` schema specifies its fields; and the metadata repository persists the record. A catalogue page may present that record alongside lineage, quality, and access-request features.

### 2.4 Metadata supports the data lifecycle

```text
Design / create
      ↓ register asset + owner + intended meaning
Ingest / transform
      ↓ harvest schemas + capture pipeline relationships
Publish / discover
      ↓ expose definition + classification + location
Use / operate
      ↓ collect runs + freshness + quality + usage
Change / review
      ↓ compare versions + assess impact + reconcile conflicts
Deprecate / retire
      ↓ notify consumers + preserve required evidence + close access
```

Metadata is not a document written once after delivery. It should be created and updated as part of the asset lifecycle. Technical metadata often changes with deployments; operational metadata changes with each run; business definitions change when business policy or interpretation changes.

### 2.5 Why metadata is a platform capability

Metadata enables several functions, often through separate tools connected by shared identifiers:

- **Discovery:** search using business terms, technical names, and usage context.
- **Governance:** associate owners, stewards, purpose, classification, and approval workflows.
- **Lineage and impact analysis:** connect source assets, transformations, and consumers.
- **Troubleshooting:** combine a failed run with the schema version, dependencies, and owner.
- **Analytics:** clarify definitions and indicate whether a dataset is current and suitable.
- **Machine learning:** record dataset versions, feature definitions, training provenance, and model dependencies.
- **AI applications:** describe permitted knowledge sources, freshness, ownership, and sensitivity; metadata alone does not establish that content is correct or permitted.

## 3. Business, technical, and operational metadata

### 3.1 The three categories

| Category | Main question | Typical fields | Common sources | Typical maintainer |
|---|---|---|---|---|
| **Business** | What does it mean, why does it exist, and who is accountable? | Business definition, glossary term, domain, owner, steward, purpose, classification, criticality | Business owners, stewards, policy/governance systems | Business owner and steward |
| **Technical** | How is it structured, identified, stored, and connected? | Schema, columns, data types, location, format, keys, partitions, constraints, technical lineage | Database/catalogue APIs, file/table metadata, pipeline definitions | Engineers and automated harvesters |
| **Operational** | How has it behaved, run, refreshed, and been used? | Run status, execution history, refresh timestamp, row counts, quality outcomes, usage counts, runtime | Orchestrators, quality checks, logs, monitoring and query systems | Platform/pipeline operations; largely automated |

The categories are complementary, not competing stores of unrelated facts. Business metadata provides meaning; technical metadata provides structure; operational metadata provides observed state. A useful asset record joins them through stable identifiers.

### 3.2 Worked classification example: synthetic customer table

Assume Northbridge Bank has a table `gold.customer_profile`. This table and all values in this lesson are illustrative.

| Metadata item | Category | Why | Best source / maintenance method |
|---|---|---|---|
| “Customer profile used for approved customer analytics” | Business | Describes purpose in business terms | Owner authors; steward reviews |
| Domain = Customer | Business | Places the asset in a business domain | Governance registry or curated field |
| Owner team = Customer Data | Business / accountability | Names accountable business function | Governance workflow; periodic review |
| Classification = Confidential | Business / governance | Describes sensitivity under the organisation’s scheme | Policy registry or reviewed classification process |
| Column `customer_id` is `VARCHAR(36)` | Technical | Describes physical structure | Harvest from source system |
| Primary key = `customer_id` | Technical | Describes a structural constraint | Harvest constraint or register from model/contract |
| Location = `lakehouse/gold/customer_profile` | Technical | Describes where the asset is stored | Platform metadata or deployment manifest |
| Last successful refresh = `2026-10-20T23:00:00Z` | Operational | Describes a completed observed event | Pipeline run record |
| Rows written = `125000` | Operational | Describes a run outcome | Pipeline metrics |
| Quality check `customer_id_not_null` passed | Operational | Describes a measured check result | Quality runner |
| Queries in trailing 30 days = `420` | Operational | Describes observed use over a window | Query/usage telemetry |

**Nuance:** classification may be stored as a business/governance attribute even if a scanner suggests it from technical evidence. The same fact may have a technical source and a business meaning. Classify by the *question the field answers*, then record its source and authority separately. A lineage relationship may be modelled as technical metadata, while lineage evidence from a particular run may be operational. A metadata model should make these distinctions explicit rather than forcing every field into an oversimplified bucket.

### 3.3 Interactions by use case

| Use case | Business metadata contributes | Technical metadata contributes | Operational metadata contributes |
|---|---|---|---|
| Discovery | Meaning, synonyms, owner, domain | Names, columns, location | Recent use, refresh status |
| Governance | Classification, purpose, accountability | Actual storage and fields in scope | Access/usage observations and evidence of controls |
| Troubleshooting | Business impact and contact | Schema, dependencies, transformation structure | Failed run, timestamps, row counts, quality outcomes |
| Change management | Criticality and consumers’ meaning | Schema version and dependency graph | Last observed execution and affected run evidence |
| Analytics | Metric definitions and approved interpretation | Types, keys, joins | Freshness, volume anomalies, usage |
| ML/AI | Purpose, permitted use, owner | Dataset/feature structure and version references | Training run details, data-quality checks, freshness observations |

### 3.4 Common classification traps

1. **“It came from a database, so it is technical.”** The source does not determine the category. A curated business definition can live in a database and still be business metadata.
2. **“Quality score is always business metadata.”** A rule’s intent and business impact may be business metadata; the measured result for a particular run is operational metadata.
3. **“Lineage is only operational.”** Structural lineage relationships are often technical metadata; execution-specific lineage observations may be operational.
4. **“Classification is just a tag.”** It carries governance meaning and may drive policy. It needs an agreed vocabulary, provenance, review, and access controls.
5. **“A field exists, so its definition is known.”** A technical name and type do not establish the business meaning.

## 4. Intermediate metadata architecture and modelling

### 4.1 A logical metadata model

A metadata model describes assets, attributes, and relationships. Keep the model technology-neutral and define stable identifiers so separate tools can exchange records without relying only on display names.

```text
BusinessDomain ──owns/contains──> DataAsset (table)
BusinessTerm ──describes──> Column
DataAsset (table) ──contains──> Column
Pipeline ──reads──> DataAsset
Pipeline ──writes──> DataAsset
DataAsset ──classified-as──> Classification
DataAsset ──has-owner──> PersonOrTeam
PipelineRun ──execution-of──> Pipeline
PipelineRun ──produced-observation-for──> DataAsset
QualityRule ──evaluates──> DataAsset or Column
QualityResult ──result-of──> QualityRule
```

Relationships should be typed, directional where appropriate, and validated. Do not infer that two assets are the same because their names match. Prefer stable asset IDs, with names and locations treated as changeable attributes.

### 4.2 Asset-level versus column-level metadata

**Asset-level metadata** describes a table, file, dashboard, model, or pipeline as a whole. **Column-level metadata** describes an individual field and is important where meaning, classification, ownership, or quality varies within an asset.

| Field | Asset-level example | Column-level example |
|---|---|---|
| Stable ID | `urn:nb:table:gold.customer_profile` | `urn:nb:column:gold.customer_profile.customer_id` |
| Display name | Customer profile | Customer identifier |
| Business definition | Approved analytical profile of a customer | Stable identifier assigned by the customer master process |
| Owner / steward | Customer Data owner / steward | Same as table by inheritance, or an explicit specialist for a critical field |
| Classification | Confidential | Restricted if the field has stricter sensitivity under policy |
| Technical structure | Table format, location, partitioning | Type, nullability, key membership |
| Operational observations | Last refresh, row count, run status | Null rate, invalid-value count, column-level quality result |

Column records may inherit owner, domain, or classification from the parent asset, but inheritance must be explicit. Allow field-level overrides where needed and record the policy used. Otherwise, a table marked “internal” could accidentally hide a more sensitive field.

**Representation choice:** the inventory below models columns as separately identified child records with `parent_asset_id`, making relationships explicit. The compact JSON example later embeds column definitions inside the table record. Both are viable representations, but an implementation should choose a canonical representation or define a tested mapping between them; do not maintain two conflicting authoritative copies of the same column metadata.

### 4.3 Example metadata inventory

The following is an **illustrative starter inventory**, not observed Northbridge Bank data.

| Asset ID | Parent asset ID | Asset / field | Category | Metadata item | Value / state | Source | Maintainer | Status / gap |
|---|---|---|---|---|---|---|---|---|
| `urn:nb:table:gold.customer_profile` | — | `gold.customer_profile` | Business | Purpose | Customer analytics | Owner-curated | Customer Data owner | Reviewed |
| `urn:nb:table:gold.customer_profile` | — | `gold.customer_profile` | Business | Domain | Customer | Governance registry | Data steward | Present |
| `urn:nb:table:gold.customer_profile` | — | `gold.customer_profile` | Business | Classification | Confidential | Classification workflow | Steward + security reviewer | Confirm before production |
| `urn:nb:table:gold.customer_profile` | — | `gold.customer_profile` | Business | Description | Approved customer profile for analytics | Human-curated | Data steward | Draft: validate definition |
| `urn:nb:table:gold.customer_profile` | — | `gold.customer_profile` | Technical | Schema | `customer_id VARCHAR(36), status VARCHAR(20), created_at TIMESTAMP` | Schema harvest | Data platform | Illustrative schema |
| `urn:nb:table:gold.customer_profile` | — | `gold.customer_profile` | Technical | Primary key | `customer_id` | Constraint/model | Data engineer | Verify uniqueness semantics |
| `urn:nb:table:gold.customer_profile` | — | `gold.customer_profile` | Technical | Location | `lakehouse/gold/customer_profile` | Platform manifest | Platform engineer | Example location only |
| `urn:nb:table:gold.customer_profile` | — | `gold.customer_profile` | Operational | Last successful refresh | `2026-10-20T23:00:00Z` | Orchestrator | Pipeline automation | Synthetic observation |
| `urn:nb:table:gold.customer_profile` | — | `gold.customer_profile` | Operational | Rows written | `125000` | Pipeline metrics | Pipeline automation | Synthetic observation |
| `urn:nb:table:gold.customer_profile` | — | `gold.customer_profile` | Operational | Last quality run | `passed` | Quality runner | Quality automation | Synthetic observation |
| `urn:nb:column:gold.customer_profile.customer_id` | `urn:nb:table:gold.customer_profile` | `customer_id` | Business | Definition | Stable identifier for a customer profile | Glossary / steward | Customer steward | Review meaning against identifier policy |
| `urn:nb:column:gold.customer_profile.customer_id` | `urn:nb:table:gold.customer_profile` | `customer_id` | Technical | Type / nullable | `VARCHAR(36)` / no | Schema harvest | Data engineer | Illustrative |
| `urn:nb:column:gold.customer_profile.customer_id` | `urn:nb:table:gold.customer_profile` | `customer_id` | Operational | Null count last run | `0` | Quality runner | Quality automation | Synthetic observation |

A useful inventory makes missing information visible. Do not fill unknown fields with plausible guesses. Use explicit states such as `unknown`, `not_applicable`, `pending_review`, or `not_harvested`, and define what each means.

### 4.4 A metadata schema: fields and requiredness

A schema is a contract for metadata records. Requiredness should be defined by asset type and risk, not by a single universal checklist.

| Field | Category | Applies to | Type | Required? | Authoritative source | Maintainer / validation |
|---|---|---|---|---|---|---|
| `asset_id` | Cross-cutting | All assets | Stable namespaced string | Mandatory | Registration service / manifest | Platform validates uniqueness and immutability; do not derive identity only from mutable display names |
| `parent_asset_id` | Technical relationship | Child assets such as columns | Stable asset ID or null for root assets | Mandatory for child assets; null for roots | Metadata model / harvester | Must resolve to an existing parent; prevent orphan columns |
| `asset_type` | Technical | All assets | Enum | Mandatory | Registration template / harvester | Validate allowed values |
| `display_name` | Cross-cutting | All assets | String | Mandatory | Source name plus curated display label | Reject blank; do not use as stable ID |
| `description` | Business | Published assets | String | Mandatory for critical/published assets; optional draft | Owner/steward | Must describe purpose/meaning, not merely repeat name |
| `domain` | Business | Governed assets | Controlled term | Mandatory for in-scope assets | Domain registry | Validate term exists |
| `owner_team` | Business/accountability | All production assets | Team ID | Mandatory for production assets | Governance directory | Must resolve to active team |
| `steward_id` | Business/accountability | Critical/published assets | Person/team ID | Mandatory for critical assets; recommended otherwise | Stewardship registry | Confirm active assignment |
| `classification` | Business/governance | All assets in scope | Controlled enum | Mandatory before broad access | Policy/classification process | Validate allowed classification and inheritance |
| `source_system` | Technical | Physical datasets | String/ID | Mandatory where applicable | Connector/manifest | Reconcile with known systems |
| `location` | Technical | Physical assets | URI/path | Mandatory where applicable | Harvester / deployment config | Access-controlled; avoid leaking secrets in URIs |
| `schema_version` | Technical | Structured assets | Version/string | Mandatory if source supports versioning; otherwise capture fingerprint | Schema registry / harvester | Compare changes; retain history |
| `columns` | Technical | Tables/files | Collection | Mandatory when schema is discoverable | Harvester | Compare with live schema |
| `last_harvested_at` | Operational about metadata collection | Harvestable assets | UTC timestamp | Mandatory after first harvest | Harvester | Monitor age and failed harvests |
| `last_success_at` | Operational | Pipelines / produced datasets | UTC timestamp or null | Required for scheduled production assets | Orchestrator | Null means no recorded success; do not substitute attempt time |
| `row_count` | Operational | Tabular outputs | Non-negative integer or null | Optional/conditional | Pipeline or storage statistics | Include observation timestamp and measurement scope |
| `quality_results` | Operational | Assets with checks | Collection of rule results | Required for assets with defined checks | Quality runner | Store rule/version, run ID, result, time |
| `usage_window` / `usage_count` | Operational | Where telemetry is available | Window + integer | Optional | Query/access telemetry | Define window and privacy policy |
| `lifecycle_state` | Cross-cutting | All assets | Enum | Mandatory | Lifecycle workflow | `active`, `deprecated`, `retired` with transition rules |
| `reviewed_at` | Business/governance | Curated records | UTC timestamp | Mandatory after review | Steward workflow | Review SLA by criticality |

**Mandatory versus optional:** require fields that protect safety, accountability, identity, or reliable operation. Avoid requiring every nice-to-have field before a low-risk asset can be registered. A practical pattern is staged completeness:

1. **Registration minimum:** stable ID, type, source/location when applicable, owner/team, lifecycle state.
2. **Before production publication:** meaningful description, domain, classification, schema, and operating expectations.
3. **Critical asset gate:** named steward, approved definition, critical fields, quality rules, lineage expectations, review date, and escalation path.
4. **Optional enrichment:** usage insights, synonyms, examples, recommendations, and advanced statistics where available.

This reduces onboarding friction without treating undocumented critical assets as ready for use. If a required value is unknown, record the gap and block only the transitions that the risk policy requires—not necessarily the initial registration.

### 4.5 Metadata sources: harvested, curated, and derived

| Method | What it is good at | Weakness / control |
|---|---|---|
| Automated harvesting | Schemas, columns, types, locations, constraints, pipeline definitions, many run facts | May miss business meaning; permissions or API limits can create gaps; scanner results need timestamps and error status |
| Human curation | Definitions, purpose, ownership, stewardship, approved classification, business synonyms | Slow and subject to inconsistency; needs workflow, controlled vocabularies, review reminders |
| Derived metadata | Completeness scores, usage tiers, schema fingerprints, anomaly indicators, inferred relationships | Depends on inputs and logic; must record derivation rule/version, observation window, and confidence where inference is uncertain |
| Assisted suggestions | Candidate descriptions, glossary matches, classifications, relationship hints | Treat as proposals, not truth; steward approval and audit trail required for consequential labels |

A mature architecture combines all four. Automate repetitive facts, reserve human judgment for meaning and accountability, and make derived outputs reproducible. Record provenance: source system, collection method, collection time, author/reviewer, and derivation version where applicable.

## 5. Collection, maintenance, lifecycle and accountability

### 5.1 Metadata lifecycle

A recommended lifecycle is:

1. **Register:** allocate stable ID and asset type when the asset is created or first discovered.
2. **Harvest:** collect structural facts and available operational signals; record the harvest timestamp and failures.
3. **Curate:** assign business meaning, domain, owner, steward, purpose, and classification through controlled workflows.
4. **Validate:** check schema conformance, identifiers, references, required fields, and policy rules.
5. **Publish:** expose appropriate metadata to intended audiences; restrict sensitive metadata.
6. **Observe and update:** refresh on schema changes, pipeline deployments, run events, usage windows, or scheduled reviews.
7. **Review and reconcile:** resolve stale values, conflicting authorities, and changes to ownership or business meaning.
8. **Deprecate:** announce replacement, affected consumers, deadlines, and migration guidance.
9. **Retire:** remove from active discovery or mark as retired only after dependencies, retention, audit, and access consequences are handled.

Lifecycle state and physical existence are separate. An asset can be physically present but deprecated; a retired asset’s metadata may need to remain available for lineage and audit. Do not delete metadata history merely because a table was dropped.

### 5.2 Ownership, stewardship, and operations

- **Data owner:** accountable for business meaning, acceptable use, criticality, and decisions within the owner’s authority.
- **Data steward:** maintains definitions, glossary mappings, quality context, and review workflow; coordinates issue resolution.
- **Data/platform engineer:** maintains harvesting integrations, technical facts, registration automation, schema-change handling, and repository reliability.
- **Pipeline owner/operator:** ensures run status, freshness, row counts, and operational observations are captured and interpreted correctly.
- **Security/privacy or governance function:** defines classification vocabulary and access policy; reviews sensitive metadata and escalations.
- **Metadata platform owner:** accountable for service availability, integrations, schema/version compatibility, retention, cost, and operational runbooks.

One person may hold more than one role in a small team, but responsibilities should still be explicit. “The platform team owns metadata” is too vague: the platform team cannot unilaterally decide the business definition of an active customer.

### 5.3 Recommended responsibility matrix

Legend: **A** = accountable decision-maker; **R** = responsible for doing the work; **C** = consulted; **I** = informed. This is a recommended example, not a prescribed Northbridge organisation chart.

| Activity | Business owner | Steward | Data/platform engineer | Pipeline operator | Security/governance | Metadata platform owner |
|---|---|---|---|---|---|---|
| Approve business definition | A | R | C | I | C | I |
| Maintain glossary and synonyms | C | A/R | I | I | C | I |
| Harvest schema and location | I | C | A/R | C | C | C |
| Capture run metrics | I | I | C | A/R | I | C |
| Approve classification policy | C | R | C | I | A | I |
| Assign/replace asset owner | A | R | I | I | C | I |
| Resolve metadata conflicts | A for meaning | R | R for technical facts | C | A for policy conflict | C |
| Operate metadata repository | I | C | R | I | C | A |
| Set retention and access controls | C | C | R | I | A | R |
| Review critical metadata | A | R | C | C | C | I |

When a person leaves, ownership must be reassigned through an explicit workflow. Use a stable team identifier or role as a fallback only if policy allows it; do not let a dead individual account silently remain the owner forever.

### 5.4 Metadata quality

Metadata itself needs quality management. Four core indicators are:

- **Completeness:** proportion of required metadata fields populated for the defined population.
- **Accuracy:** proportion of audited metadata values that match authoritative reality.
- **Timeliness:** age of metadata relative to the expected update or harvest interval.
- **Consistency:** proportion of equivalent facts that agree across systems or representations.

Useful additional indicators include uniqueness of asset IDs, relationship validity, owner resolution rate, review coverage, and harvesting success rate.

#### Example indicator definitions (illustrative targets)

| Indicator | Definition | Example target (assumption only) | Measurement method | Owner / response |
|---|---|---|---|---|
| Critical-asset completeness | Critical assets with owner, description, domain, classification and current review date ÷ all in-scope critical assets | ≥ 98% | Daily inventory query | Steward lead investigates missing fields |
| Description accuracy | Audited descriptions confirmed accurate ÷ descriptions audited | ≥ 95% | Monthly sample reviewed by owners/stewards | Correct inaccurate descriptions; inspect source workflow |
| Harvest timeliness | Harvestable assets harvested within configured freshness window ÷ harvestable assets | ≥ 99% | Compare `last_harvested_at` to asset-specific SLA | Platform team retries failed scans and alerts owners |
| Cross-system consistency | Tested metadata mappings with no material conflict ÷ mappings tested | ≥ 99% | Reconciliation job | Route by field authority and log conflicts |
| Owner resolution | Production assets whose owner resolves to an active team/person ÷ production assets | 100% for critical assets | Directory lookup | Governance workflow assigns replacement owner |

Targets are illustrative and must be calibrated to criticality, system limits, and business need. A global target without a defined denominator, time window, exception policy, and response owner is not an actionable indicator.

**Example calculation:** if 47 of 50 critical assets have all five required fields, completeness is `47 / 50 × 100 = 94%`. Do not count a field as complete merely because it contains a placeholder like `TBD`; define acceptable values and exclusions.

### 5.5 Conflicts, stale metadata, and reconciliation

Conflicts happen when metadata sources disagree: a live table says `DECIMAL(12,2)` while the catalogue says `FLOAT`; a business owner changes a definition but an old copy remains; a scanner discovers a new column but its classification is unknown.

Use a field-level authority policy rather than declaring that one whole system always wins:

| Metadata field | Suggested authority | Reconciliation behaviour |
|---|---|---|
| Live physical schema | Source system / trusted harvester | Update technical record; retain prior schema version and change event |
| Business definition | Approved glossary / owner-steward workflow | Do not overwrite with generated text; flag disagreements for review |
| Classification | Approved governance process, with scanner suggestions as evidence | Apply conservative handling when uncertainty could expose sensitive data; route to policy owner |
| Run status / timestamp | Orchestrator run record | Append immutable run observation; distinguish attempt from successful completion |
| Usage count | Defined telemetry source and window | Record window and source; avoid merging counts with different definitions |
| Owner team | Governance directory / ownership workflow | Validate active team; alert if unresolved |

Reconciliation should preserve provenance, show the conflicting values, apply a documented rule, and record whether a human decision is needed. Never silently replace curated meaning with a machine-generated guess.

### 5.6 Schema drift and change handling

Schema drift is a change in a source structure or contract. It may be compatible (for example, adding an optional column) or breaking (renaming a required field, changing its type, or removing a key). The metadata system should:

1. Detect a schema fingerprint/version change.
2. Record the before/after schema and collection time.
3. Classify the change and identify impacted downstream assets using available lineage.
4. Notify the responsible owner and affected consumers for material changes.
5. Update technical metadata only after the source of truth is observed; update business metadata where meaning changed.
6. Run contract and quality checks; retain a clear audit trail.

A successful harvest does not imply the change is safe. Harvesting tells you what changed; contracts, lineage, tests, and ownership help determine whether the change is acceptable.

## 6. Advanced architecture decisions: scale, security, versioning and cost

### 6.1 Central repository versus federated sources

**Centralized metadata repository:** easier cross-domain search, consistent identifiers, and common controls; may create a central bottleneck and require careful integration with diverse systems.

**Federated domain metadata:** domains retain authority and local workflows; can fit domain autonomy, but introduces duplication, inconsistent semantics, and cross-domain discovery challenges.

**Common hybrid:** domain systems remain authoritative for particular fields, while a shared index or catalogue provides unified discovery and reconciled views. This is often a useful starting assumption when there are multiple domains, but it is not universally best. Decide based on ownership maturity, scale, autonomy, security boundaries, and interoperability needs.

### 6.2 Metadata as code

Metadata as code means version-controlled definitions and registration configuration are reviewed, tested, and deployed with data assets. It is particularly useful for stable definitions, ownership declarations, schema contracts, classification defaults, and pipeline relationships.

Benefits include reviewable changes, repeatability across environments, audit history, and less drift. Risks include stale declarations if deployment and live systems diverge, accidental publication of sensitive details, and confusing desired state with observed state.

A practical separation is:

- **Declared metadata:** what a repository or deployment manifest intends to create.
- **Observed metadata:** what a scanner or runtime actually sees.
- **Curated metadata:** what an accountable human has approved.

Reconcile these views; do not overwrite observed runtime facts with declarations merely because the file is version-controlled.

#### Example YAML manifest (illustrative configuration, not a vendor-specific API)

```yaml
asset_id: "urn:northbridge:table:gold.customer_profile"
asset_type: "table"
display_name: "Customer profile"
domain: "Customer"
owner_team: "customer-data"
steward_team: "customer-data-stewards"
classification: "Confidential"
description: >-
  Approved customer profile for analytics; see the glossary definition
  of customer and the documented inclusion rules.
lifecycle_state: "active"
criticality: "high"
```

**Purpose:** declares stable registration fields alongside a pipeline or data-product definition. **Inputs:** the manifest and an agreed schema/vocabulary. **Output:** a proposed metadata record after a registration process validates it. **Execution:** a deployment or CI job would parse the YAML, validate required fields and controlled values, compare it with existing records, then submit changes through the organisation’s metadata API. No such API is assumed or invoked here; this is a portable example, not executable by itself. **Validation and security:** reject unknown classifications and unresolved owner IDs; keep credentials outside the manifest; review changes; prevent a manifest from granting access by itself.

### 6.3 Versioning and repeatability

Version metadata schema definitions and curated definitions. Keep an audit history for changes that affect meaning, classification, ownership, or operational interpretation. For high-volume observations, keep run-level detail for a defined period and aggregate older data where allowed.

Recommended practices:

- Use stable IDs independent of mutable names and physical paths.
- Include schema/version identifiers or fingerprints when useful.
- Make registration idempotent: applying the same declaration twice should not create duplicate assets.
- Record who/what changed a record, when, why, and from which source.
- Test metadata schema migrations and interoperability mappings before production rollout.
- Distinguish a missing observation from a measured zero.

### 6.4 Scale and operational metadata volume

Structural metadata often changes relatively slowly; operational observations may be produced for every pipeline run, partition, quality rule, or usage window. Store and query them according to different access patterns.

**Illustrative scale calculation from the roadmap:** `50,000 tables × 40 columns = 2,000,000 column records`. If each column record has five retained versions, that is up to `10,000,000` versioned column-record rows, before relationships and operational observations. This is a scale illustration, not a prediction for a particular organisation.

Suppose, illustratively, 20,000 jobs each emit 24 run observations per day: `20,000 × 24 = 480,000` observations/day, or `175,200,000` per 365-day year. At an assumed average of 1.5 KB per stored observation before indexes/replicas, raw payload alone is about 262.8 GB/year. Actual storage varies substantially with encoding, indexes, replication, compression, and retained fields; this estimate is only a sizing exercise.

Design controls:

- Set retention by purpose: detailed run records, longer-lived aggregates, and durable audit evidence may have different policies.
- Keep enough detail for incident investigation and applicable obligations; do not shorten retention without checking requirements.
- Prefer incremental/event-driven updates where source systems support them, with periodic reconciliation scans to detect missed events.
- Tune harvest frequency to risk and change rate; avoid repeatedly scanning large production systems without a reason.
- Record failed scans and coverage gaps, not just successful results.
- Partition or index high-volume observations by time, asset, or run as justified by query patterns.
- Monitor ingestion cost, storage growth, query latency, and steward workload.

### 6.5 Security and privacy of metadata

Metadata is not automatically harmless. Names can reveal products, controls, customers, or investigations; schemas can expose the existence of sensitive fields; sample values, query text, and lineage can disclose sensitive information or operational topology.

Controls should include:

- Apply role- and purpose-appropriate access to metadata records and individual fields.
- Do not store secrets, credentials, access tokens, or raw personal data in descriptions or tags.
- Treat sample values and query text as potentially sensitive; avoid collecting them unless justified and approved.
- Apply classification inheritance cautiously, allowing stricter field-level labels where needed.
- Log access to sensitive metadata and restrict broad exports.
- Separate the ability to discover an asset from the ability to read its underlying data.
- Ensure metadata API credentials are least-privileged and rotated according to policy.

A catalogue can expose that a table exists without granting data access, but even asset existence may be restricted for some environments. Security design must define the boundary explicitly.

### 6.6 Automation versus curation: decision rule

Automate facts that systems can observe reliably; curate meaning and accountability; derive indicators with transparent logic; use machine-assisted suggestions only as proposals where errors have consequences.

| Metadata type | Default approach | Human review trigger |
|---|---|---|
| Column names/types/location | Automated harvest | Harvest conflict, unsupported type, schema drift |
| Run status and timestamps | Automated event capture | Missing events, clock anomalies, contradictory status |
| Business definition and purpose | Owner/steward curation | Definition change, ambiguity, conflicting domains |
| Classification | Policy workflow plus scanning suggestions | Any uncertain or high-impact classification |
| Completeness/usage score | Derived calculation | Metric logic changes or unexpected distribution |
| AI-generated description | Suggested draft | Always before treating as approved meaning for critical/published assets |

Measure not just how much is automated, but the error rate, steward acceptance rate, time to resolve conflicts, and proportion of important fields with verified provenance.

### 6.7 Architecture decision record (ADR) template and example

An ADR records a decision, alternatives, consequences, and conditions that would trigger reconsideration. It should not simply restate the selected technology.

#### ADR-001 — Separate declared, observed, and curated metadata

- **Status:** Proposed for this learning scenario.
- **Context:** Northbridge needs repeatable registration across a lakehouse, catalogue, orchestration, and quality systems. Live schemas and run facts change more frequently than business definitions. A single undifferentiated “last writer wins” rule could overwrite approved meaning or hide schema drift.
- **Decision:** Maintain one stable asset identity and distinguish declared metadata, observed metadata, and curated metadata by provenance and authority. Use field-level reconciliation rules. Preserve schema and decision history for material changes. Keep high-volume operational observations in a retention-managed store or logical partition separate from slower-changing asset descriptions.
- **Alternatives considered:** (A) one central record with last-write-wins; (B) independent tool-local records with no unified index; (C) hybrid shared identity and index with field-level authorities.
- **Rationale:** A is simple but can silently destroy meaning; B preserves local autonomy but makes discovery and consistency harder; C introduces reconciliation complexity but offers a clearer authority model and cross-tool discovery.
- **Consequences:** Requires stable identifiers, source provenance, conflict handling, retention rules, and operational ownership. The shared view may be temporarily stale during outages; it must display freshness and harvesting status.
- **Risks / mitigations:** Incorrect field authority → document and test precedence rules; sensitive metadata leakage → access controls and review; stale index → freshness SLO and reconciliation scans; cost growth → retention and aggregation policy.
- **Revisit when:** domain ownership changes materially, source connectors cannot support required freshness, cross-region policy prevents central indexing, or observed reconciliation cost exceeds agreed limits.
- **Evidence needed before production:** sample inventory, field-authority matrix, conflict test cases, security review, retention estimate, and a reviewer-approved operational runbook.

This ADR is illustrative. The module roadmap recommends documenting the metadata model, sources, maintenance responsibilities, and trade-offs in an ADR; it does not prescribe this particular decision.

## 7. Worked examples and step-by-step exercises

### 7.1 Example: diagnosing a stale customer mart

**Scenario (illustrative):** a risk analyst reports that `gold.customer_profile` has yesterday’s customer status. The catalogue says the table was refreshed at 23:00 UTC, but the dashboard’s data is older.

1. **Check operational metadata:** inspect the latest pipeline run ID, start/end times, terminal status, rows read/written, and failure/retry history. Confirm whether the timestamp means “attempted,” “completed,” or “successfully published.”
2. **Check technical metadata:** compare current schema fingerprint with the pipeline’s expected schema; verify source/target location and the transformation version.
3. **Check lineage/dependencies:** identify upstream source and downstream dashboard. If lineage is incomplete, explicitly mark the blind spot instead of assuming no dependency.
4. **Check business metadata:** confirm what “current customer status” means and who owns that definition. A pipeline can be green while business logic is wrong.
5. **Reconcile:** if a run succeeded but wrote zero rows unexpectedly, investigate operational volume; if a source field was renamed, investigate schema drift; if the source was delayed, inspect upstream freshness.
6. **Act and record:** assign the issue to the responsible owner/operator, record the root cause and corrective action, update affected metadata if needed, and add a check to prevent recurrence.

**Lesson:** no single metadata category solves the incident. Operational observations show what happened; technical metadata shows the structure and dependencies; business metadata explains the impact and accountability.

### 7.2 Example: measure completeness

Assume a synthetic inventory contains 15 assets, of which 10 are classified as critical. The policy says a critical asset is complete only if it has an active owner, meaningful description, domain, classification, and review date.

- 8 critical assets meet all five conditions.
- 1 has an owner but no meaningful description.
- 1 has a description and domain but no resolved owner.

Critical-asset completeness = `8 / 10 × 100 = 80%`.

Do not average field-level percentages and call that the same measure: an asset with one missing critical field may still be incomplete under the all-required-fields rule. Report both the overall measure and the per-field gaps to make remediation actionable.

### 7.3 Example: conflict policy

A scanner observes `status VARCHAR(20)` while the curated dictionary describes `status` as “approved customer lifecycle status.” The source system later changes the column to `VARCHAR(40)`.

- Update the observed physical type after a successful harvest.
- Preserve the prior schema version and record the change time.
- Do not erase the curated business definition merely because the technical record changed.
- Ask the steward whether the expanded type allows new business values or changes meaning.
- Update glossary mappings, validation rules, and consumers only when the meaning or contract requires it.

### 7.4 Hands-on Exercise A — Inventory 15 assets

**Scenario:** Northbridge cannot answer “what is in the customer mart and who owns it?” because the existing inventory is incomplete. **Goal:** distinguish categories and make gaps explicit. **Time recommendation:** 60–90 minutes.

Use synthetic assets from Northbridge Bank: source tables for core ledger, cards, and CRM; bronze/silver/gold customer tables; an exposure mart; two reports; one ingestion pipeline; one streaming feed; and one model-training dataset. You may define your own asset names, but label them illustrative.

For each of at least 15 assets, record:

- Stable ID, asset type, name, domain, and lifecycle state.
- At least two business, two technical, and two operational metadata items where applicable.
- Source or derivation method for each item.
- Owner, steward/maintainer, and review/harvest timestamp.
- Missing or conflicting fields and proposed remediation.

**Acceptance checks:** every record has a category or an explicit cross-cutting designation; no unknown value is silently guessed; every asset has an owner or a recorded ownership gap; observed facts have timestamps; and sensitive metadata is not exposed unnecessarily.

### 7.5 Hands-on Exercise B — Define metadata schema and indicators

**Scenario:** only 30% of in-scope catalogue assets have meaningful descriptions. **Goal:** define the fields, requiredness, sources, and maintainers for tables and columns, then design measurable indicators to improve metadata quality. **Time recommendation:** 90–120 minutes.

1. Establish the eligible asset population and calculate the current meaningful-description coverage; do not infer the denominator from the 30% statement alone if the asset count is unknown.
2. Select mandatory fields for registration, publication, and critical-asset readiness.
2. Mark each field’s category, type, source of authority, collection method, maintainer, and validation rule.
3. Define completeness, accuracy, timeliness, and consistency indicators with numerator, denominator, population, time window, target, exclusions, and response owner.
4. Propose a harvest schedule for slow-changing schema facts and high-volume run observations.
5. Describe how conflicts are detected, resolved, and audited.
6. Ask another person to review the inventory and schema. If no reviewer is available, record this as an unmet review gate rather than claiming independent review.

**Acceptance checks:** every mandatory field has a credible source; every indicator is reproducible; thresholds are labelled assumptions; and onboarding friction is discussed explicitly.

### 7.6 Hands-on Exercise C — Classify 20 metadata items

For each item, state category, reason, collection method (automated, human, derived, or hybrid), and any required security/quality control.

1. Business definition of “active customer.”
2. Table name.
3. Column data type.
4. Primary-key constraint.
5. Storage URI.
6. Business domain.
7. Owner team.
8. Steward assignment.
9. Classification label.
10. Pipeline run status.
11. Last successful refresh timestamp.
12. Rows read during a run.
13. Rows written during a run.
14. Last quality-check result.
15. Query count over the last 30 days.
16. Derived metadata completeness score.
17. A suggested glossary-term match generated by a model.
18. Approved glossary-term-to-column relationship.
19. Schema fingerprint before and after deployment.
20. Review date for a business definition.

**Self-check guidance:** items 1, 6–9, and 20 are generally business/governance-oriented; 2–5 and structural aspects of 18–19 are technical; 10–15 are operational observations; 16 is derived metadata; 17 is a suggestion pending review. Some items have mixed aspects, so explain the question being answered and record provenance rather than memorising labels.

## 8. Practical implementation examples

### 8.1 JSON metadata record

```json
{
  "asset_id": "urn:northbridge:table:gold.customer_profile",
  "asset_type": "table",
  "display_name": "Customer profile",
  "business": {
    "domain": "Customer",
    "description": "Approved customer profile for analytics",
    "owner_team": "customer-data",
    "steward_team": "customer-data-stewards",
    "classification": "Confidential"
  },
  "technical": {
    "location": "lakehouse/gold/customer_profile",
    "schema_version": "illustrative-v1",
    "columns": [
      {"name": "customer_id", "type": "VARCHAR(36)", "nullable": false},
      {"name": "status", "type": "VARCHAR(20)", "nullable": true},
      {"name": "created_at", "type": "TIMESTAMP", "nullable": false}
    ]
  },
  "operational": {
    "last_success_at": "2026-10-20T23:00:00Z",
    "row_count": 125000,
    "observation_source": "synthetic-example",
    "observed_at": "2026-10-20T23:02:00Z"
  },
  "lifecycle_state": "active"
}
```

**Purpose:** demonstrates a record with separate business, technical, and operational sections. **Input:** a chosen metadata schema and values from authoritative sources. **Output:** a serialized JSON example that can be inspected or validated by an implementation. **Execution:** save as a `.json` file and parse it with a standard JSON parser; the snippet alone does not register anything in a catalogue. **Assumptions:** field names and type conventions are illustrative, not a universal schema. A production contract should define timestamps, null semantics, allowed classifications, provenance, versioning, and required fields. **Security:** the location is a placeholder and must not contain credentials or sensitive query parameters.

### 8.2 Executable Python validation example (Python 3.10+)

This standard-library example checks a small subset of required fields and basic values. It is intentionally not a complete metadata schema validator and does not connect to a catalogue.

```python
from datetime import datetime, timedelta
from typing import Any

REQUIRED_TOP_LEVEL = {"asset_id", "asset_type", "display_name", "lifecycle_state"}
ALLOWED_STATES = {"active", "deprecated", "retired"}


def validate_metadata(record: Any) -> list[str]:
    """Return validation errors; an empty list means these checks passed."""
    if not isinstance(record, dict):
        return ["record must be an object/dictionary"]

    errors: list[str] = []
    missing = REQUIRED_TOP_LEVEL - record.keys()
    if missing:
        errors.append(f"Missing required fields: {', '.join(sorted(missing))}")

    for field in ("asset_id", "asset_type", "display_name"):
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")

    state = record.get("lifecycle_state")
    if not isinstance(state, str) or state not in ALLOWED_STATES:
        errors.append(f"lifecycle_state must be one of {sorted(ALLOWED_STATES)}")

    operational = record.get("operational", {})
    if operational is not None and not isinstance(operational, dict):
        errors.append("operational must be an object when provided")
    elif isinstance(operational, dict):
        row_count = operational.get("row_count")
        if row_count is not None and (
            not isinstance(row_count, int) or isinstance(row_count, bool) or row_count < 0
        ):
            errors.append("operational.row_count must be a non-negative integer")

        timestamp = operational.get("last_success_at")
        if timestamp is not None:
            if not isinstance(timestamp, str):
                errors.append("operational.last_success_at must be a string timestamp")
            else:
                normalized = timestamp[:-1] + "+00:00" if timestamp.endswith("Z") else timestamp
                try:
                    parsed = datetime.fromisoformat(normalized)
                    if parsed.tzinfo is None:
                        errors.append("operational.last_success_at must include a timezone")
                    elif parsed.utcoffset() != timedelta(0):
                        errors.append("operational.last_success_at must be expressed in UTC")
                except ValueError:
                    errors.append("operational.last_success_at must be ISO-8601 compatible")

    return errors


example = {
    "asset_id": "urn:northbridge:table:gold.customer_profile",
    "asset_type": "table",
    "display_name": "Customer profile",
    "lifecycle_state": "active",
    "operational": {
        "row_count": 125000,
        "last_success_at": "2026-10-20T23:00:00Z",
    },
}

problems = validate_metadata(example)
print("VALID" if not problems else "INVALID")
for problem in problems:
    print(f"- {problem}")
```

**Purpose:** catch missing identity fields, invalid or null lifecycle states, negative/non-integer row counts, malformed timestamps, timezone-naive timestamps, and non-UTC offsets for the field defined as UTC. **Inputs:** a Python dictionary representing one record. **Output:** a list of human-readable validation errors. **Execution:** save as `validate_metadata.py` and run with Python 3.10 or later; no third-party packages are required. For the `example` shown, expected output is `VALID`.

**Limitations and edge cases:** this is a demonstration validator, not production-grade validation. It does not enforce the full schema, controlled vocabulary for classification, field-level access rules, timestamp freshness, or uniqueness against a repository. It permits an absent `operational` object and treats an explicit null `operational` value as absent. In production, use a reviewed schema contract, structured error reporting, tests, and safe logging; do not log sensitive metadata values indiscriminately.

### 8.3 Minimal SQL for a metadata quality check

The following is **illustrative ANSI-style SQL** against a hypothetical `metadata_assets` table; column names and syntax may require adaptation to a particular SQL engine.

```sql
SELECT
    COUNT(*) AS total_assets,
    SUM(CASE
        WHEN owner_team IS NOT NULL
         AND TRIM(owner_team) <> ''
         AND description IS NOT NULL
         AND TRIM(description) <> ''
         AND domain IS NOT NULL
         AND TRIM(domain) <> ''
         AND classification IS NOT NULL
         AND TRIM(classification) <> ''
        THEN 1 ELSE 0
    END) AS complete_assets,
    100.0 * SUM(CASE
        WHEN owner_team IS NOT NULL
         AND TRIM(owner_team) <> ''
         AND description IS NOT NULL
         AND TRIM(description) <> ''
         AND domain IS NOT NULL
         AND TRIM(domain) <> ''
         AND classification IS NOT NULL
         AND TRIM(classification) <> ''
        THEN 1 ELSE 0
    END) / NULLIF(COUNT(*), 0) AS completeness_pct
FROM metadata_assets
WHERE lifecycle_state = 'active';
```

**Purpose:** calculate the percentage of active asset records that have four fields meaningfully populated (non-null and non-blank). **Input:** a table with the named columns. **Output:** total count, complete count, and percentage. **Execution:** run only after adapting it to the SQL dialect and table definition. `NULLIF` prevents division by zero; if there are no eligible active assets, the percentage is `NULL`, not zero. **Population assumption:** this simplified query assumes every active row in `metadata_assets` is in scope and is required to have all four fields. If the inventory includes assets for which a field is not applicable, add an explicit eligibility filter and apply the same eligibility rule to the denominator. **Important limitation:** this checks presence, not meaningfulness or accuracy. Production logic should validate that owners resolve to active teams, descriptions are useful, classifications are valid, and the denominator is restricted to the correct asset population. The example is not claimed to have been executed against a database.

## 9. Industry scenarios, trade-offs and failure modes

### 9.1 Onboarding 500 undocumented legacy tables

All figures are illustrative. A small steward team must choose among documenting everything before any release, prioritising critical assets, or generating automatic descriptions for all assets.

| Option | Advantages | Disadvantages / risks | Suitable when |
|---|---|---|---|
| Document every asset fully before onboarding | Strong completeness at launch | Slow, high manual effort, may delay useful discovery | Full coverage is a hard policy or release requirement |
| Register all assets, then enrich critical assets first | Early inventory, effort follows risk, gaps visible | Low-risk assets may remain thinly documented for a while | Most organisations can stage quality by risk and clearly mark readiness |
| Auto-generate descriptions for all | Fast initial coverage | Plausible but wrong definitions can be trusted by users | Use only as draft suggestions with provenance and review for consequential assets |

A reasonable starting recommendation is to register all discovered assets with stable IDs and technical facts, then prioritise human curation for critical and heavily used assets. Revisit if a specific obligation requires complete reviewed documentation before use.

### 9.2 Operational metadata retention

Keeping every per-run and per-partition observation forever improves historical analysis but increases storage and query cost. Aggregating old data lowers cost but may reduce forensic detail. Retention must reflect incident response, audit, regulatory, and operational needs; do not choose an arbitrary 90-day period without confirming those requirements.

A common design is detailed recent observations, longer-lived aggregates, and separately protected durable evidence where required. State the retention boundary and deletion/aggregation process in the architecture and runbooks.

### 9.3 Failure modes and mitigations

| Failure mode | Why it happens | Impact | Mitigation |
|---|---|---|---|
| Descriptions repeat names | No definition quality standard | Users cannot interpret meaning | Require purpose, scope, and important caveats; steward review |
| Metadata is captured only after delivery | No lifecycle integration | Records are incomplete and stale | Register in templates/pipelines and validate before publication |
| Stale operational facts look current | No observation timestamp or failed-harvest status | Users trust old freshness/row counts | Display `observed_at`, `last_harvested_at`, and collection status |
| No owner or owner has left | Accountability is not lifecycle-managed | Issues remain unresolved | Validate owner IDs and trigger reassignment workflow |
| Source schema disagrees with catalogue | Harvest failure or unhandled drift | Broken joins, transformations, or assumptions | Reconciliation, schema version history, alerts, impact analysis |
| Machine suggestion treated as truth | Confidence/provenance omitted | Incorrect definitions/classifications | Label as suggested; require review for critical fields |
| One global “source of truth” rule | Field authorities differ | Curated meaning may be overwritten by a scanner | Field-level authority and conflict workflow |
| Excessive mandatory fields | Registration friction encourages bypasses | Assets remain invisible or shadow systems emerge | Risk-based staged requirements and visible gaps |
| Too few mandatory fields | Assets are discoverable but unusable or unsafe | Poor trust and governance | Gate publication/criticality on minimum required metadata |
| Sensitive metadata is broadly searchable | Metadata treated as harmless | Information leakage | Field-level access, classification, audit, controlled exports |
| IDs based on names or paths | Names change or collide | Duplicate records and broken relationships | Stable IDs plus aliases and rename history |
| Operational store grows without bounds | No retention or aggregation policy | Cost and query degradation | Measure volume, set retention, aggregate, index by access pattern |

### 9.4 Metadata in ML and AI systems

Metadata helps document training datasets, features, models, and retrieval sources: purpose, owner, version, source lineage, permitted use, classification, quality checks, and observed refresh state. It supports reproducibility and investigation but does not guarantee model correctness, eliminate bias, or replace evaluation and access controls. For AI retrieval systems, metadata can help filter by source, date, access policy, and domain; correctness still depends on source quality, retrieval design, and application controls.

## 10. Required learning deliverables

The Topic 01 roadmap recommends five deliverables. Treat these as learning outputs aligned to the roadmap, not as requirements taken from the currently empty project file.

### D1 — Metadata inventory

- [ ] Inventory at least 15 illustrative assets or the number agreed with your reviewer.
- [ ] Classify business, technical, and operational items, noting mixed cases.
- [ ] Record source, maintainer, timestamps, and gaps.
- [ ] Include asset- and column-level records.
- [ ] Mark all invented values and assumptions.

### D2 — Metadata schema

- [ ] Define fields, types, asset applicability, category, source of authority, collection method, requiredness, maintainer, and validation rule.
- [ ] Distinguish registration minimum, publication requirements, critical-asset requirements, and optional enrichment.
- [ ] Define identifiers, relationships, lifecycle states, provenance, and versioning.
- [ ] Explain inheritance and overrides from asset to column.

### D3 — Metadata quality indicators

- [ ] Define completeness, accuracy, timeliness, and consistency.
- [ ] For each, document formula, numerator/denominator, population, time window, target, exclusions, source, owner, and response action.
- [ ] Label numerical targets as assumptions until agreed by stakeholders.
- [ ] Include an example calculation and at least one edge case (for example, an empty denominator).

### D4 — Ownership and stewardship matrix

- [ ] Name the accountable role for business meaning and policy decisions.
- [ ] Separate curation from technical harvesting and pipeline operations.
- [ ] Define ownership reassignment when people or teams change.
- [ ] Identify review cadence and escalation route for critical assets.

### D5 — Architecture decision record

- [ ] Document context, decision, alternatives, rationale, consequences, risks, mitigations, and revisit triggers.
- [ ] Cover metadata authority, collection/maintenance, repository topology or source integration, and operational retention where relevant.
- [ ] Trace the decision to requirements and assumptions.
- [ ] Have another person review the inventory and schema; if not done, record the gate as incomplete.

## 11. Common mistakes and misconceptions

1. **Metadata is just documentation.** It is also structured, versioned, queryable operational input to catalogues, governance, and automation.
2. **A catalogue is the metadata itself.** A catalogue is commonly the discovery experience; repositories and authoritative source systems may be separate.
3. **Every field belongs to exactly one category without nuance.** Use the category that best answers the field’s question and record source, authority, and provenance for mixed cases.
4. **Automated means accurate.** A scanner can accurately report a type while a curated definition is wrong, or fail to harvest entirely.
5. **Human-entered means trustworthy.** Curation still needs controlled terms, review, ownership, and evidence.
6. **A filled field is complete.** `TBD`, an inactive owner, or a description that repeats the name may be present but not useful.
7. **Last run time equals last successful refresh.** Attempt, completion, and successful publication are different events.
8. **One central tool can be the authority for everything.** Authority is often field-specific and may be distributed across systems.
9. **Metadata is safe to expose because it is not the data.** Names, schema, lineage, and query information can reveal sensitive facts.
10. **A green pipeline proves the data are fit for use.** Operational success does not prove business meaning or quality.
11. **Deleting an asset means deleting its metadata.** Retain the history needed for lineage, audit, and consumer migration.
12. **A numeric target is objective without a definition.** Every indicator needs a clear population, formula, window, and exception policy.

## 12. Mastery criteria and completion gate

### 12.1 Mastery criteria

You have demonstrated mastery of Topic 01 when you can:

- Correctly classify metadata items and justify ambiguous cases.
- Define a metadata schema for tables and columns, including sources and maintainers.
- Explain lifecycle and responsibility boundaries.
- Measure metadata completeness and freshness with reproducible formulas.
- Identify missing or inconsistent metadata and propose a reconciliation rule.
- Explain how the three categories work together in a troubleshooting scenario.
- Defend trade-offs around mandatory fields, automation, security, versioning, retention, and cost.

### 12.2 Completion gate

Complete each item before moving to Topic 02:

- [ ] Inventory and metadata schema created and reviewed by one other person.
- [ ] Every in-scope inventory item has a category and maintainer, or an explicit gap is recorded.
- [ ] Metadata sources are identified as automated, curated, derived, or hybrid.
- [ ] Mandatory fields have credible sources and validation rules.
- [ ] Completeness and freshness indicators are measurable and include denominators/time windows.
- [ ] You can explain how business, technical, and operational metadata combine in a troubleshooting case.
- [ ] Five weak descriptions that merely restate field names have been rewritten to explain meaning and purpose.
- [ ] Sensitive metadata exposure has been considered.
- [ ] Assumptions, illustrative values, and unresolved issues are clearly labelled.

If no independent reviewer is available, do not mark the review item complete; record it as pending. The roadmap explicitly expects review by another person and a measurable-indicator check.

### 12.3 Connection to the module final project

Topic 01 supplies the metadata inventory and schema used by later topics. Topic 02 builds catalogue and discovery design; Topic 03 adds lineage and impact analysis; Topics 04–05 add critical data elements, quality rules, observability, and service levels; Topics 06–07 add master data, identifiers, reference data, and entity resolution; Topic 08 addresses metadata standards and interoperability.

The module roadmap proposes a final Northbridge Bank design scenario involving customer and exposure domains, three illustrative source systems (core ledger, cards, CRM), a lakehouse with bronze/silver/gold layers, a catalogue, a quality tool, an orchestration tool, two critical reports, source-to-report lineage, quality and freshness expectations, customer master data, and interoperability. Those are **proposed illustrative assumptions** in the roadmap, not requirements from the currently empty project files. Topic 01 should contribute a well-identified inventory, schema, quality indicators, ownership matrix, and ADR that can be integrated into that wider design.

## 13. Concise revision checklist

Before you consider the topic complete, make sure you can answer “yes” to each:

- [ ] Can I explain metadata without defining it only as “data about data”?
- [ ] Can I distinguish business meaning, technical structure, and operational observations?
- [ ] Can I explain why the same asset needs all three categories?
- [ ] Can I distinguish asset records, metadata schemas, repositories, and catalogues?
- [ ] Can I model tables, columns, owners, terms, pipelines, runs, and quality results with stable IDs and typed relationships?
- [ ] Can I explain what should be harvested, curated, derived, and reviewed?
- [ ] Can I describe lifecycle transitions, deprecation, retirement, and owner reassignment?
- [ ] Can I measure completeness, accuracy, timeliness, and consistency reproducibly?
- [ ] Can I reconcile conflicting sources without silently overwriting approved meaning?
- [ ] Can I explain metadata security, metadata as code, versioning, retention, and cost trade-offs?
- [ ] Have I completed and reviewed the five Topic 01 deliverables?
- [ ] Have I passed the completion gate, or explicitly recorded what remains incomplete?

---

**End of Topic 01.** Do not proceed to the next lesson until the inventory, schema, indicators, responsibility matrix, ADR, and completion-gate evidence are ready for review.
