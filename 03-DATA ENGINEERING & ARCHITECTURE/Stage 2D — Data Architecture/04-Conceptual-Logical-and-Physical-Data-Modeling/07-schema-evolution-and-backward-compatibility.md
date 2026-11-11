# Schema Evolution and Backward Compatibility

> **Stage:** 2D — Data Architecture  
> **Module:** 7 of 8 — Conceptual, Logical and Physical Data Modeling  
> **Level:** Foundational → intermediate → advanced  
> **Purpose:** Change data models and contracts safely across producers, consumers, stored records, analytical products and governance boundaries.

## Scope and roadmap alignment

This lesson follows Module 7 of `roadmap-Conceptual-Logical-and-Physical-Data-Modeling.md`. It depends on Modules 1–6 in this modeling sequence and Stage 2D.3 Topic 6 (contracts and compatibility). It also connects to Module 5 (historical records), Module 6 (event ownership and event contracts), Topic 8 (model review), and Topic 11 (lineage).

The roadmap requires change classification, consumer impact analysis, versioning, migration and rollout planning, validation, governance, semantic-change handling, historical-data strategy, and a deprecation plan for a widely consumed customer model.

This lesson is vendor-neutral. It does not assume a particular schema registry, broker, database, serialization format or cloud platform. Compatibility outcomes depend on contract rules and the direction of the producer/consumer version transition. All Northbridge Bank names and data are illustrative.

---

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Explain schema evolution and distinguish structural schema changes from business-rule and semantic changes.
2. Define backward compatibility, forward compatibility and breaking change while explicitly stating version direction and producer/consumer assumptions.
3. Classify additions, removals, renames, type changes, optionality changes, constraint changes, enumeration extensions and semantic changes.
4. Analyze impacts across producers, direct and transitive consumers, historical records, validation rules and operational processes.
5. Design a versioning and deprecation policy for a widely consumed data model.
6. Plan an expand-and-contract migration, including rollout order, dual read/write decisions, backfill, validation, rollback and final removal.
7. Test compatibility using old and new schemas, representative records, consumer contract tests and post-migration reconciliation.
8. Explain when tolerant readers and defaults help—and when they conceal a semantic defect.
9. Choose between normalizing old data in place, preserving historical shapes and using version-aware adapters.
10. Create an auditable change record with owners, dates, risk, approvals, tests and consumer notifications.

## 2. Why the topic matters in real-world Data Architecture

Data contracts are used by systems that often deploy independently. A producer may publish a new field while consumers are running older code; a warehouse may contain years of records with different shapes; a new regulatory rule may apply only to newly opened accounts; and an analyst may depend on an undocumented field in a scheduled script.

A change can be syntactically valid and still be unsafe. A numeric `balance` field might retain its type while changing from dollars to cents. Every parser still succeeds, but calculations become wrong. Likewise, adding a new enumeration value may be syntactically additive but break a consumer that assumes the status set is closed.

Schema evolution is a **system-wide change-management problem**, not merely a file-format operation. It requires understanding who produces and consumes a contract; which fields, values, constraints and meanings consumers assume; how old stored records are interpreted; which consumers depend indirectly on other consumers or curated models; how the transition is rolled out and verified; what happens if migration fails; and who authorizes deprecation and removal.

A safe process allows useful changes without demanding coordinated releases for every consumer. It also avoids promising that every change can be made independently. Some semantic or invariant changes genuinely require a coordinated migration.

## 3. Prerequisite knowledge

Review these concepts before proceeding:

- **Module 1:** conceptual, logical and physical models; distinguish a business concept from its representation.
- **Module 2:** entities, keys, relationships, optionality, constraints and business rules.
- **Module 3:** relational integrity, normalization and consequences of changing attributes or constraints.
- **Module 4:** fact grain, dimensions and analytical measures; a type or meaning change can alter metric correctness.
- **Module 5:** historical records, preserved history and point-in-time interpretation.
- **Module 6:** bounded contexts, event ownership, event contracts, event evolution and consumer semantics.
- **Stage 2D.3 Topic 6:** data-sharing contracts and compatibility.
- **Module 8:** review, naming standards, data dictionaries and approval.
- **Stage 2D.11:** lineage and dependency discovery.

A schema may be a relational table definition, event payload, file layout, API representation, curated data product or logical model contract. Apply the same impact-analysis discipline even when the physical implementation differs.

## 4. Beginner-level learning sequence

### 4.1 What is schema evolution?

**Schema evolution** is the controlled change of a data structure or its contract over time. It includes changes to field names, types, optionality, constraints, enumerations and field meaning. It also includes how producers write new records, how consumers read old and new records, and how stored history is handled.

Examples include adding `account_opening_channel`; changing an optional attribute to required; renaming `customer_status`; extending an enumeration with `SUSPENDED`; changing a monetary amount's unit from dollars to cents; and tightening a rule so new accounts require a verified tax-residency value. The last examples can be business-contract changes even when a schema validator accepts the representation.

### 4.2 Define compatibility precisely

Compatibility labels are ambiguous unless direction and assumptions are stated. This lesson uses the following conventional definitions for old schema `V1` and new schema `V2`.

| Term | Definition used in this lesson | Practical test |
|---|---|---|
| **Backward compatibility** | A consumer/reader implemented against new schema `V2` can correctly read data written according to old schema `V1`. | Can the new reader handle representative V1 records without losing or misinterpreting required meaning? |
| **Forward compatibility** | A consumer/reader implemented against old schema `V1` can correctly read data written according to new schema `V2`. | Can the old reader handle V2 records, including new fields and values, without failing or misinterpreting them? |
| **Full compatibility** | Both backward and forward compatibility hold under the declared rules and test cases. | Can new readers read old records and old readers read new records correctly? |
| **Breaking change** | A change that violates a required compatibility contract or forces affected producers/consumers to change in a coordinated way. | Does a deployed participant fail, reject data, lose required meaning, or produce incorrect results? |

These definitions focus on **reader/writer data compatibility**. Some organizations use “backward compatible” to mean that a new producer does not break old consumers. Because usage differs, every change record must state the exact convention and direction. Do not mix reader/writer compatibility with deployment sequencing without saying so.

A change is not universally compatible in isolation. Compatibility depends on schema rules, producer and consumer versions, validation behavior, actual data values and semantic assumptions. Passing a parser test is necessary in many cases but is not proof of semantic safety.

### 4.3 Additive does not mean safe

An optional field addition is often safe for an old reader that ignores unknown fields, and it is generally straightforward for a new reader to read old records if the field is genuinely optional. But “optional” is meaningful only if the consumer can correctly handle its absence.

Syntactically additive changes can still break consumers:

- adding `status = SUSPENDED` when a consumer rejects unknown enumeration values;
- adding `is_verified` and treating missing historical values as `false` when the real meaning is “unknown”;
- adding a field whose name looks familiar but whose unit or definition differs;
- making a field optional in storage while downstream code assumes it is never null;
- adding a new required business process while retaining the same schema.

Always test actual consumers and contract semantics.

### 4.4 First-pass change classification table

This is a **starting classification**, not an unconditional promise. Assume V1 is the deployed old contract, V2 is proposed, and compatibility is evaluated for both old and new readers. A reader that ignores unknown fields and a reader that rejects them can have different outcomes. The labels describe typical risk, not a universal guarantee: test each direction against the actual schema format, serializer/parser settings, stored data, consumer behavior and business semantics. A change may be structurally compatible but behaviorally or semantically breaking.

| Change | Typical classification | Producers, consumers and operational processes affected | Old records and constraints | Required first action |
|---|---|---|---|---|
| Add an optional field | Often backward-compatible for new readers; often forward-compatible for tolerant old readers | Producers add population logic; consumers, exports and downstream mappings may ignore or reject it | Old records lack the field; absence semantics and validation constraints must be defined | Test old readers with V2 records and new readers with V1 records |
| Add a required field | Usually breaking without staged migration | Producers and onboarding/update workflows must supply it; consumers and operational forms may reject absence | Backfill, unknown values and lifecycle-specific validation rules matter | Expand with optionality/default/derived value first, then enforce after evidence |
| Remove a field | Breaking for consumers that read it | Producers and consumers using the field; downstream views and scripts | Historical records may still contain it; readers may depend on it | Deprecate, migrate consumers, monitor usage, then remove |
| Rename a field | Breaking when implemented as remove + add | Writers, readers, mappings, reports and APIs | Old records retain old name unless adapted or rewritten | Introduce new representation, dual-read/write as appropriate, then contract |
| Widen a type | Often compatible, but depends on representation and consumers | Producers may emit values old readers cannot parse or represent | Existing values usually fit, but precision/scale and serialization may change | Test boundary values, precision, nulls and consumer limits |
| Narrow a type | Usually breaking | Writers, readers, validators and downstream aggregates | Existing values may not fit or may be truncated | Profile data; define reject/repair/exception behavior before rollout |
| Change optionality | Direction-dependent and often breaking | Producers and consumers relying on presence/absence | Old data may lack the field; constraints may reject it | Separate storage shape from business requirement; backfill or define unknown |
| Tighten a constraint | Often breaking for existing data or producers | Writers, validators, ingestion/onboarding workflows, migration jobs and consumers | Existing records may violate the new rule | Profile violations, remediate, stage enforcement and define exceptions |
| Loosen a constraint | May be structurally compatible but break assumptions | Consumers may assume values remain within the old range/set | Old checks and aggregations may be incomplete | Identify assumptions and test new allowed values |
| Add an enumeration value | Often breaks closed-set consumers | Producers, switch statements, mappings, dashboards, alerts and operational decision rules | Old records remain valid; constraints may reject the value and consumers may misclassify it | Test unknown-value handling and define business behavior |
| Remove/rename an enumeration value | Breaking unless mapped or versioned | Writers, readers, reports and historical interpreters | Old records may retain retired values indefinitely | Preserve historical meaning and define explicit mapping/deprecation |
| Change meaning, same type | **Silently breaking** | All consumers using the old business definition | Values look structurally identical but mean different things | Create a new field/contract version or explicit transition; update dictionary and consumers |
| Change unit or scale | **Semantically breaking**, even if type is unchanged/widened | Producers, consumers, metrics, alerts and historical comparisons | Values may be incomparable across time | Use explicit unit, conversion rule, versioned semantics and reconciliation |

### 4.5 Why rename and semantic changes are dangerous

A rename is normally a removal plus an addition from the perspective of a consumer that references the old name. A consumer cannot safely infer that `registered_address` and `mailing_address` mean the same thing simply because one replaces the other.

A semantic change can be worse because there may be no error. If `active_customer` changes from “has an open relationship” to “eligible for marketing,” old queries still run, but historical trends and decisions become invalid. Preserve the old definition and introduce a clearly defined new field or version, update the data dictionary, and notify consumers.

**Rule:** never silently redefine an existing field or enumeration value that is already part of a published contract.

## 5. Intermediate-level learning sequence

### 5.1 Consumer impact analysis

Do not start by editing the schema. Start by finding dependencies.

1. Identify the exact field, rule, enumeration, contract or meaning that will change.
2. Find direct consumers using lineage, contracts, metadata, code search and owner interviews.
3. Find **transitive consumers** that depend on a view, product, extract or event derived from the changed source.
4. Identify shadow consumers such as spreadsheets, scheduled scripts, manual extracts and external partner feeds.
5. Record the dependency type: reads the field, validates it, branches on it, aggregates it, persists it, or exposes it further.
6. Classify the effect for each consumer, including semantic impact.
7. Assign an owner and deadline for migration, test and sign-off.
8. Define validation, monitoring, rollback and removal criteria.

Absence of a registered dependency is not proof that a consumer does not exist. If lineage is incomplete, record that uncertainty as a risk and require discovery/monitoring before destructive changes.

### 5.2 Example impact-analysis table

**Proposed change:** rename `customer_status` to `relationship_status` in a Northbridge customer model, clarifying that the field describes whether the retail relationship is open. The new name does not mean CRM subscription status or Risk assessment outcome.

| Consumer | Dependency | Effect | Required action | Owner | Deadline / gate |
|---|---|---|---|---|---|
| Retail servicing API | Reads `customer_status` to display relationship state | Direct field reference breaks if old field disappears | Read new field; contract-test old and new representations during transition | Retail API owner | Before V2-only release |
| Lending eligibility pipeline | Uses status in eligibility rules | Potential semantic error if old mapping was broader than “relationship open” | Confirm business rule, map field and rerun historical decision tests | Lending data owner | Before production cutover |
| Risk analytical product | Derives a feature from status | Field rename plus possible meaning mismatch | Confirm whether Risk needs relationship state or a separate risk attribute; update dictionary | Risk product owner | Before model refresh using V2 |
| Finance regulatory extract | Selects the field for a controlled report | Potential reporting break and audit impact | Validate report totals and retain traceable mapping; obtain report owner approval | Finance reporting owner | Before regulatory reporting cycle |
| Operations spreadsheet/export | Reads old column name outside governed lineage | May fail silently or show blanks | Notify owner, provide sample V2 file and verify usage; keep compatibility view temporarily | Operations owner | Before deprecation end date |

This is an illustrative dependency set, not a claim that Northbridge has these actual systems. A real impact analysis must replace these roles with verified consumers and named accountable owners.

### 5.3 Versioning strategies

| Strategy | What it means | Advantages | Costs and risks | Use when |
|---|---|---|---|---|
| **Compatible in-place evolution** | One contract evolves under additive/compatibility rules | Minimizes parallel interfaces and coordinated releases | Semantic discipline and unknown-field handling still required | Changes preserve existing meaning and readers can tolerate them |
| **Versioned schema identifier** | Records reference a governed schema version or contract revision | Makes interpretation explicit and supports old records | Version management and reader selection required | Multiple shapes coexist and consumers need deterministic interpretation |
| **Parallel V1/V2 contracts** | Old and new representations are published or exposed concurrently | Allows gradual migration and clear consumer choice | Duplicate maintenance, reconciliation and retirement work | Rename, meaning change or coordinated transition needs a bridge |
| **Compatibility view/adapter** | Translation layer presents old shape to old consumers or new shape to new consumers | Isolates legacy consumers from source change | Adapter becomes another maintained dependency; mapping can conceal loss | Consumers cannot all migrate at once |
| **Major coordinated release** | Producer and required consumers change together | Clear cutover for tightly coupled systems | Release coupling, larger scope, operational risk | Invariants or semantics cannot safely coexist across versions |

A version number does not by itself guarantee compatibility. Document the schema identifier, semantic meaning, compatibility policy, support window and migration rules.

### 5.4 Safe expand-and-contract migration

**Expand-and-contract** is a staged migration pattern. It makes the new representation available before removing the old one. The exact steps depend on whether the change affects tables, files, events, APIs or derived data products.

#### Example: rename `customer_status` to `relationship_status`

1. **Baseline and approve.** Confirm field definition, owners, consumers, old/new semantics, data volumes, availability requirements and rollback criteria. Capture baseline counts, null rates and key business metrics.
2. **Expand the schema.** Add `relationship_status` while retaining `customer_status`. Define whether both are semantically identical during transition. If meaning changes, do not blindly copy values; define a mapping or separate field.
3. **Deploy producer support.** Populate the new field. If dual-writing, ensure both fields derive from one canonical value or governed mapping. Monitor mismatches. Dual-write introduces consistency risk; define how divergence is detected and repaired.
4. **Backfill historical records.** Populate the new representation where justified. Distinguish derivable values from unknown values. Do not invent history or silently convert unknown to false. Make backfill idempotent and checkpointed.
5. **Migrate readers.** Update direct and transitive consumers in a planned order. A temporary compatibility view or adapter may keep old readers working. Record contract-test results and owner sign-off.
6. **Validate and reconcile.** Compare row counts, key coverage, null/unknown rates, value distributions, business totals and representative record-level mappings. Check that old and new representations agree where they should.
7. **Observe the transition.** Monitor reads/writes to the old field, failures, mismatches, latency and downstream metrics for a defined period. Discover undocumented consumers where possible.
8. **Set a cutover gate.** Remove the old field only after required consumers have migrated or an explicitly approved exception exists, the deprecation window has elapsed, and rollback conditions are understood.
9. **Contract.** Stop old writes, retire adapters only when no longer needed, and remove the old field in a separately approved release. Keep historical interpretation and audit lineage available.
10. **Close and document.** Record final validation, consumer approvals, exceptions, incident learnings, dictionary definition and effective date of removal.

#### Rollback plan

Before cutover, specify what can be rolled back and for how long:

- If the new field is wrong but the old field is still authoritative, stop new writes or disable the new reader path, repair the mapping and replay/backfill safely.
- If consumers have written new-only values that cannot be represented in V1, a simple rollback may lose information. Preserve V2 data and use an adapter or forward-fix instead of destructive downgrade.
- If dual-write values diverge, stop promotion, reconcile against the agreed authority and repair before continuing.
- If the failure is semantic, reverting code alone may not repair decisions or reports already produced. Identify affected outputs and define correction/republication procedures.
- A rollback must not delete evidence of the failed attempt if audit or investigation requires it.

### 5.5 Defaults, optionality and tolerant readers

A **default** fills a missing value according to an explicit rule. A **tolerant reader** ignores or safely handles fields and values it does not recognize. Both are useful, but neither is a universal compatibility fix.

- Use a default only when it has a valid business meaning. `communication_preference = UNKNOWN` may be safer than assuming `OPTED_IN`.
- A parser default is not necessarily a historical fact. Preserve whether the value was supplied, derived or defaulted if that distinction matters.
- A tolerant reader should not silently map an unknown status to a misleading known status. It may preserve the raw value, route the record for review, or enter a safe unknown state.
- If a consumer ignores a new field that is essential to a business invariant, it may parse the record but still behave incorrectly.
- Requiredness must be evaluated at the correct lifecycle boundary. A new attribute may be mandatory for accounts opened after a regulation's effective date while legitimately absent from older accounts.
- Null, absent, empty string, `UNKNOWN`, and `NOT_APPLICABLE` are not interchangeable unless the contract explicitly defines them that way.

### 5.6 Backfill, dual reads and dual writes

| Technique | Purpose | Main risk | Control |
|---|---|---|---|
| **Backfill** | Transform or derive the new field for historical records | Incorrect inference, expensive scans, inconsistent partial completion | Profile first, checkpoint, make idempotent, track provenance and reconcile |
| **Dual write** | Write old and new representations during transition | One write succeeds while the other fails; values diverge | Single canonical derivation, transactional support where available, mismatch monitoring and repair |
| **Dual read** | Read new representation with fallback to old during migration | Different precedence rules can create inconsistent behavior | Define precedence, conflict detection, telemetry and removal deadline |
| **Adapter/compatibility view** | Present stable interface while physical representations change | Legacy contract remains alive indefinitely | Assign owner, scope, metrics and explicit retirement date |
| **Replay/reprocessing** | Re-evaluate records under a new mapping or logic | Side effects, duplicates or changed historical results | Isolate side effects, version transformation and compare before publishing |

Avoid dual reads and dual writes unless they solve a defined transition problem. They add complexity and should have an owner, monitoring and a removal criterion.

### 5.7 Historical records and old schema shapes

Stored data does not automatically change when a schema changes. Historical records may have old field names, missing newly introduced attributes, retired enumeration values, old units or precision, old semantic definitions, and values that violate newly tightened constraints.

Choose deliberately between:

1. **In-place upgrade:** rewrite historical records to the new representation. Useful when transformation is deterministic and original evidence can be preserved where required. Risk: losing source shape or obscuring historical semantics.
2. **Version-aware adapter:** interpret each record using its recorded schema/contract version and expose a normalized read model. Useful when history must remain faithful or conversion is ambiguous. Risk: adapters and version logic must be maintained.
3. **Curated canonical layer:** preserve raw historical representations and derive a versioned, normalized downstream model. Useful for audit and analytical integration. Risk: additional storage and transformation lineage.
4. **Mixed strategy:** normalize fields with safe deterministic transformations while retaining provenance or the original record for ambiguous changes.

Do not rewrite a past value using today's meaning without documenting that choice. If the unit changes from dollars to cents, convert only when the source version establishes the original unit. If an old record lacks a mandatory attribute and the value cannot be derived, represent it as unknown/not captured according to policy rather than fabricating a value.

## 6. Advanced-level learning sequence

### 6.1 Compatibility is contextual and directional

For a proposed V1 → V2 change, assess at least four dimensions:

1. **Reader/writer structural compatibility:** Can each reader parse and represent records written by each version?
2. **Consumer behavioral compatibility:** Does the consumer correctly handle values, unknown fields, enumerations, nulls and constraints?
3. **Business semantic compatibility:** Do field meanings, units, time basis and rules remain consistent?
4. **Historical compatibility:** Can old records still be interpreted correctly, and can new records be compared with old records without mixing definitions?

A change may pass dimension 1 and fail dimensions 2–4. A compatibility checker can detect some structural issues but generally cannot prove that a unit, status meaning or regulatory interpretation is correct.

#### Example compatibility test matrix

Assume the V2 schema adds optional field `preferred_language`; the status enumeration is later extended with `SUSPENDED`; and a separate amount migration changes dollars to cents. These are distinct changes and must not be collapsed into one “schema passes” result.

| Test | Reader | Record | Expected outcome | Interpretation |
|---|---|---|---|---|
| C1 | V2 reader | V1 record without `preferred_language` | Pass if the field is truly optional and absence is handled | Backward compatibility for the optional-field change |
| C2 | Tolerant V1 reader | V2 record containing `preferred_language` | Pass if unknown fields are ignored/preserved safely | Forward compatibility only for readers with this behavior |
| C3 | V1 closed-enumeration reader | V2 record with `SUSPENDED` | Fail or route to an explicit safe unknown-value path; never silently map to `OPEN` | The enum extension is not forward-compatible for this reader as currently implemented |
| C4 | V2 reader requiring a new field | V1 historical record missing that field | Fail unless an explicit valid absence/adapter rule exists | A required-field addition is not backward-compatible by default |
| C5 | Amount consumer using V1 dollar semantics | V2 record storing cents | Structural parse may pass, but semantic assertion must fail until conversion/version handling is applied | Type compatibility does not establish unit compatibility |

The expected result is part of the contract test, not an assumption about a particular vendor's compatibility checker. Run equivalent cases against representative production-shaped samples and each registered consumer contract.

### 6.2 Scenario 1 — New mandatory attribute for new accounts only

**Requirement:** A new regulation requires `tax_residency_declaration` for accounts opened on or after a stated effective date. Existing accounts may not have captured the declaration.

**Unsafe approach:** Make the field globally required immediately and reject all records that lack it. This can block updates to legacy accounts and falsely imply that old accounts failed a requirement that did not apply at creation.

**Safer design:**

1. Define the legal/business effective date, applicable account types and authoritative evidence.
2. Add the attribute as nullable/optional in the storage contract during rollout.
3. Update onboarding producers to collect and validate it for in-scope new accounts.
4. Keep existing accounts with no captured declaration as `UNKNOWN`/not captured if approved; do not assume `NO`.
5. Add lifecycle-aware validation: required for accounts opened after the effective date, not necessarily for all historical records.
6. Migrate consumers to handle the field and its absence semantics.
7. Backfill only from verified evidence; track provenance and avoid inferring legal declarations from unrelated attributes.
8. Reconcile new-account compliance after rollout and define exception handling.
9. Tighten enforcement at the applicable creation boundary only after producers and consumers are ready.
10. Record the policy, effective date, exceptions and validation evidence.

**Compatibility assessment:** a global requiredness change is likely breaking for old data and legacy writers. A staged, lifecycle-aware rule may preserve compatibility while meeting the new business requirement.

### 6.3 Scenario 2 — A new status enumeration value

**Requirement:** Northbridge adds `SUSPENDED` to an existing account status set (`PENDING`, `OPEN`, `CLOSED`).

Potential failures include an exhaustive switch statement throwing an error; a dashboard mapping unknown values to `OPEN`; a report excluding suspended accounts; a downstream system assuming every non-closed account can transact; or a constraint rejecting the new value.

**Safe response:**

1. Identify the semantic owner and define `SUSPENDED` precisely.
2. Decide whether it changes account behavior, reporting and legal obligations.
3. Find every consumer that branches on status, including transitive models and scripts.
4. Deploy consumers that can preserve and explicitly handle unknown/new values, or stage the new value behind a rollout gate.
5. Update validation constraints, mapping tables, metrics, alerts and business rules.
6. Test old consumers against a record containing `SUSPENDED`; test new consumers against records with old values.
7. Publish the effective date, contract version, migration guidance and owner.
8. Monitor unknown-value rates and verify that no consumer silently maps it to a wrong known status.

**Compatibility assessment:** the new value may be syntactically additive, but it is not safe for consumers that assume a closed enumeration. Unknown-value handling must be explicit.

### 6.4 Scenario 3 — Type widening while units change

**Requirement:** `transaction_amount` changes from a 32-bit integer of whole dollars to a wider numeric representation storing cents.

The new type may hold a larger range, but the unit changes. `125` in V1 means 125 dollars; `12500` in V2 means 125 dollars. A wider type does not preserve meaning automatically.

**Correct migration approach:**

- Prefer a new explicitly named field such as `transaction_amount_minor_units` or a new versioned contract, with `currency` and a documented unit/scale.
- Define conversion rules and rounding behavior. For currencies with different minor-unit conventions, do not assume all currencies have exactly two decimal places.
- Keep old and new representations side by side during migration.
- Convert only when the source version/unit is known; do not infer unit from magnitude.
- Test minimum/maximum values, precision, negative values, reversals, nulls and currency-specific scale.
- Compare totals after conversion using exact decimal/integer arithmetic and documented rounding.
- Migrate all consumers and analytical metrics, then deprecate the old field.
- Preserve lineage to explain which records were converted and under which rule.

**Compatibility assessment:** structurally this may be a widening; semantically it is breaking. Treat it as a contract migration, not a safe type-only edit.

### 6.5 Change pipeline: conceptual automated checks

A vendor-neutral change pipeline should run checks appropriate to the contract class:

1. **Change request validation:** owner, purpose, proposed diff, business definition, effective date, risk and migration plan are present.
2. **Schema syntax/structure check:** new schema is valid and naming/type rules are satisfied.
3. **Compatibility comparison:** evaluate old/new schema pairs under the declared backward/forward policy and report the direction tested.
4. **Sample-record tests:** parse representative V1 and V2 records, including nulls, unknown fields, retired values and boundary values.
5. **Consumer contract tests:** run registered consumer expectations against representative new records and historical samples.
6. **Semantic assertions:** verify units, definitions, enum handling, constraints and business rules; require domain-owner review where automation cannot prove meaning.
7. **Historical-shape tests:** ensure old records remain readable through the intended adapter/curated model.
8. **Lineage and notification check:** enumerate direct/transitive dependents, verify owners, and record notification dates and exceptions.
9. **Migration rehearsal:** estimate volume and runtime, exercise backfill/checkpoint/restart and validate rollback/forward-fix.
10. **Release gate:** require approvals for high-risk or regulated contracts; no destructive removal before deprecation criteria are met.
11. **Post-release reconciliation:** compare counts, key coverage, nulls, enum distributions, business totals and error rates.
12. **Evidence retention:** retain schema diff, test results, approvals, migration metrics, exceptions and final decision.

Automated structural checks should fail closed for clearly incompatible changes under a strict policy. Semantic changes need human review and explicit business approval; no generic compatibility checker can determine all meaning.

### 6.6 Governance policy by model class

| Contract class | Typical policy | Change control |
|---|---|---|
| Regulated/external interface | Strict; explicit versions and documented deprecation; semantic changes require approval | Formal impact analysis, consumer sign-off, retained evidence and rollback/forward-fix plan |
| Enterprise shared data product | Conservative additive evolution, explicit ownership, dependency discovery and deprecation windows | Automated compatibility checks plus review for semantic, constraint and enumeration changes |
| Internal tightly coupled model | May use coordinated releases if the dependency boundary is controlled | Release sequencing, integration tests and documented rollback |
| Exploratory analytics | More flexible, but provenance and version labels still matter | Communicate changes, retain reproducible snapshots or versioned models where needed |
| Historical/raw landing layer | Preserve source shape and source/version metadata unless governed normalization is intended | Version-aware interpretation, lineage and documented transformations |

Governance establishes who may change meaning, which compatibility promise applies, who must be notified, how exceptions are accepted and what evidence proves the migration was safe.

### 6.7 Independent deployment versus coordinated releases

Independent deployment is appropriate when the contract supports it—for example, optional additive fields, tolerant readers with defined unknown-value behavior, and unchanged semantics. It reduces release coupling but depends on disciplined contracts and tests.

Coordinated deployment may be unavoidable when a required field enforces a new invariant; a meaning or unit changes; an old representation cannot faithfully express new values; consumer behavior must change at the same effective time as the producer; or legal/regulatory policy requires a coordinated cutover.

The cost of lockstep release includes scheduling delay, larger release scope, complex rollback and coordination overhead. The cost of pretending releases are independent includes silent data corruption, consumer failures and unclear accountability. Make the choice explicit in the change record.

## 7. Industry-application exercises

Use fictional Northbridge Bank data.

### Exercise 1 — Classify twenty changes

Use V1 as the deployed contract and V2 as the proposed contract. For each case, classify backward compatibility (V2 reader reads V1 records) and forward compatibility (V1 reader reads V2 records) separately. The expected classifications below are conditional on the stated assumptions; a real decision must be tested against the actual format, validators and consumers.

| # | Proposed V1 → V2 change | Expected classification and reason | Minimum action |
|---:|---|---|---|
| 1 | Add optional `preferred_language`; old readers ignore unknown fields; new readers accept absence | Usually backward-compatible; forward-compatible only for tolerant old readers | Test both directions and absence semantics |
| 2 | Add required `tax_residency_declaration` to every record immediately | Usually breaks V2 readers on V1 records and V1 writers that omit it | Stage as optional; enforce only at the applicable lifecycle boundary |
| 3 | Add `tax_residency_declaration` required only for accounts opened after an effective date | Conditional; structurally optional for legacy records, but lifecycle validation and consumers must understand effective date | Add lifecycle rule, historical absence semantics and tests |
| 4 | Remove `middle_name` used by a registered consumer | Breaking for that consumer | Deprecate, migrate and verify before removal |
| 5 | Rename `customer_status` to semantically identical `relationship_status` | Breaking for direct name-based readers/writers despite same meaning | Expand with both names or adapter, migrate consumers, then contract |
| 6 | Rename `customer_status` to `marketing_eligibility` and change meaning | Breaking and semantic; not a safe rename | Define new concept, version contract and migrate business logic |
| 7 | Widen signed 32-bit integer to signed 64-bit integer | Often structurally compatible for old values; forward compatibility fails if V2 emits values old readers cannot represent | Test boundaries and consumer numeric limits |
| 8 | Narrow 64-bit integer to 32-bit integer | Potentially breaking because valid old values may overflow or truncate | Profile values and define reject/repair policy |
| 9 | Change decimal scale from dollars to cents while widening precision | Semantically breaking even if parse succeeds | New field/version, explicit unit, conversion and reconciliation |
| 10 | Change nullable field to non-null for all records | Usually breaking for historical nulls and legacy writers | Profile, remediate or preserve explicit unknown; stage enforcement |
| 11 | Change required field to optional | Often structurally permissive, but can break consumers that assume presence | Test null/absent behavior and downstream business rules |
| 12 | Tighten `country_code` constraint while old rows contain blanks | Breaks validation of existing rows; producers may also be rejected | Profile and remediate; separate old-data and new-write policy |
| 13 | Loosen maximum `transaction_amount` constraint | Structural change may pass, but consumers may overflow or reject larger values | Test ranges and downstream representations |
| 14 | Add enum value `SUSPENDED`; one consumer has an exhaustive switch | Not forward-compatible for that consumer; it may fail or misclassify | Update consumer or safe unknown handling before publishing value |
| 15 | Add enum value `SUSPENDED`; all readers preserve unknown values but do not apply new business behavior | Parsing may be compatible; behavioral compatibility is not established | Domain-owner review, consumer behavior tests and staged activation |
| 16 | Remove enum value `PENDING` from new writes while old records still contain it | Historical compatibility risk; consumers may still need to interpret old values | Keep historical mapping and define retirement/translation rules |
| 17 | Change `active_customer` definition without changing its type or name | Silently breaking; syntactic tests cannot detect it | Create new semantic field/version and update dictionary |
| 18 | Add `source_system` as optional metadata, but a consumer rejects unknown JSON properties | Forward compatibility fails for that consumer | Test actual parser policy; update reader or use versioned representation |
| 19 | Change timestamp from local time without zone to UTC instant | Semantically and potentially structurally breaking | Define time basis, conversion evidence, version and boundary tests |
| 20 | Add a default `false` for missing `is_verified`, although missing means “not captured” | Syntactically easy but semantically corrupting | Preserve UNKNOWN/not-captured distinction; do not fabricate historical fact |

For every case, add the real producer, direct and transitive consumers, historical-data effect, owner, deadline, tests and rollback/forward-fix gate. A classification is not complete until its assumptions are written down.

### Exercise 2 — Customer model with five consumers

Use the rename from `customer_status` to `relationship_status` in Section 5.2. Replace illustrative roles with a verified dependency list for a real project, or retain the fictional scenario and label it as such. Include five consumers, direct/transitive dependencies, effect, action, owner, deadline, contract tests and sign-off criteria.

### Exercise 3 — New mandatory attribute for new accounts

Design a lifecycle-aware migration for `tax_residency_declaration`. Include effective date, account eligibility, old-record semantics, collection/validation changes, backfill limitations, consumer changes, reconciliation and rollback.

### Exercise 4 — Enumeration extension

Add `SUSPENDED` to an account status enumeration. List consumer behaviors that could fail and design unknown-value tests. Include mapping, reports, alerts and any constraint changes.

### Exercise 5 — Type widening and unit change

Migrate `transaction_amount` from whole dollars to cents in a wider numeric representation. State why a type-only compatibility test is insufficient. Provide conversion examples, boundary tests, rounding policy and reconciliation.

### Exercise 6 — Deprecation notice

Write a dated deprecation notice for a renamed field. Include old/new names, definitions, effective dates, supported transition, consumer actions, test sample location, owner/contact role, support deadline, retirement criteria and rollback/exception route.

### Exercise 7 — Change pipeline

Define conceptual automated checks and human approval gates for a strict shared data product and a flexible exploratory dataset. Explain which checks can be automated and which require domain judgment.

## 8. Practical scenarios and case-based reasoning

### Scenario A — A regulation introduces a mandatory attribute

A new rule requires an attribute for new accounts only. Existing accounts lack it, and the source cannot recover the value for every historical account.

- Model the legal effective date and scope explicitly.
- Do not globally reject every old record because it lacks the new field.
- Distinguish `UNKNOWN`/not captured from a substantive negative value.
- Enforce the requirement at the relevant account-creation boundary.
- Backfill only from authoritative evidence.
- Validate compliance for in-scope new accounts and record exceptions.

### Scenario B — A producer adds an enumeration value

A producer starts publishing `SUSPENDED`. A consumer with an exhaustive switch fails; another maps unknown values to `OPEN`.

- Treat both consumers as affected even though the schema change is additive.
- Make unknown-value behavior explicit and safe; do not map unknown to a business state without authority.
- Deploy tolerant/updated consumers before enabling the new value if rollout requires it.
- Test all branches and reconcile counts after rollout.
- Document the enumeration owner, new value's meaning and effective date.

### Scenario C — A widened type changes units

A type widens but the producer now stores cents rather than dollars.

- Mark it as a semantic breaking change.
- Introduce explicit unit/scale metadata or a new field/version.
- Avoid guessing units from value magnitude.
- Validate exact conversions and totals; document rounding and currency-specific precision.
- Preserve historical interpretation and source-version lineage.

### Scenario D — An undocumented spreadsheet consumes the old field

Governed lineage shows no use of `customer_status`, but a business operations spreadsheet imports it every Monday.

- Treat missing lineage as uncertainty, not proof of no dependencies.
- Search code, query logs, exports, owners and observed access where available.
- Provide a compatibility view or temporary extension if necessary.
- Publish a deprecation notice and verify the spreadsheet migration.
- Do not remove the old field until approved retirement criteria are met.

### Scenario E — A constraint is tightened after years of imperfect data

A field must now contain a valid country code, but historical rows include blank and legacy values.

- Profile data before enforcing the new constraint.
- Separate producer validation for new records from remediation of old records.
- Define valid mappings and an exception bucket; do not silently invent codes.
- Stage enforcement, monitor rejection rates and document unresolved records.
- Decide whether the historical layer preserves source values while a curated layer exposes a normalized code.

## 9. Expected outputs and deliverables

### 9.1 Change classification table

Every proposed change must state old/new versions, compatibility direction, structural and semantic impact, affected parties, historical-data implications, required tests and decision.

### 9.2 Impact analysis and transition plan

| Field | Required evidence |
|---|---|
| Consumer/dependency | Verified consumer or explicitly labeled unknown |
| Dependency type | Read, write, validate, branch, aggregate, persist or re-publish |
| Effect | Failure, data loss, semantic drift, changed metric or no expected effect with evidence |
| Required action | Code, mapping, data migration, test, notice or approved exception |
| Owner | Accountable role/team |
| Deadline | Date or release gate |
| Validation | Contract test, sample test, reconciliation or business sign-off |
| Rollback/forward-fix | Conditions and procedure |

### 9.3 Compatibility and deprecation policy

Define compatibility by direction, model class, semantic-change rules, unknown-enumeration behavior, deprecation window, removal criteria, exception approval and retained evidence.

### 9.4 Schema evolution plan for the customer model

Include five consumers, dependency lineage, new/old field behavior, migration order, backfill, dual read/write decisions, validation thresholds, monitoring, rollback and removal gates.

### 9.5 Sample deprecation notice

**Illustrative notice — replace dates and roles before real use**

> **Subject:** Deprecation of `customer_status`; replacement with `relationship_status`  
> **Issued:** 2026-10-20  
> **Contract owner:** Retail Customer Data Product Owner  
> **Affected interface:** Northbridge Retail Customer Model, contract V2  
>
> **What is changing:** `customer_status` is deprecated in favor of `relationship_status`. The replacement field means “the lifecycle status of the retail banking relationship,” not CRM subscription status or Risk assessment outcome. No consumer should assume these concepts are interchangeable.
>
> **Availability:** The new field will be populated from 2026-11-02. During the transition, both fields will be exposed where the old field can be mapped without semantic loss. If a record cannot be mapped reliably, it will be flagged for review rather than assigned a fabricated value.
>
> **Consumer action:** Update readers, mappings, reports and tests to use `relationship_status`; verify that status values are handled explicitly. Validate the change with representative V1 and V2 records and confirm report/business totals remain correct.
>
> **Deprecation window:** Support for the old field is planned through 2027-01-15. Removal is conditional on consumer-owner sign-off, successful reconciliation, no known active dependencies, and approval at the contract review gate. The date is a planning target, not permission to remove the field if gates fail.
>
> **Validation and support:** Contract tests and sample records will be provided by the data product owner before the consumer migration deadline. Consumers must report mismatches and unknown dependencies before the cutover gate.
>
> **Rollback/exception:** If the new field produces incorrect values or a required consumer cannot migrate, pause removal, retain the compatibility representation and escalate to the contract owner. Any exception must identify an owner and a revised retirement date.
>
> **Retirement confirmation:** A separate notice will confirm actual removal after all gates are met.

The dates and roles above are illustrative. A real notice must use the organization's approved dates, support channel and authority.

### 9.6 Practice-question answers

Use these model answers to self-check the eight questions. They apply the definitions in Section 4.2; real implementations must still be tested against their actual contracts.

1. **Why is renaming a field normally breaking?** Consumers often bind to the old field name. Removing it makes those readers fail or return missing values; adding the new name does not automatically migrate consumers or historical records. Use a transition representation or adapter and remove the old name only after evidence-based retirement gates.
2. **Why can changing meaning be more dangerous than changing type?** A type change may trigger a parser or compile-time error. A semantic change can remain syntactically valid while silently changing metrics, eligibility decisions or historical comparisons. Introduce a new field/version or an explicitly governed semantic transition.
3. **What do backward and forward compatibility test here?** With V1 old and V2 new, backward compatibility means a V2 reader correctly reads V1 records. Forward compatibility means a V1 reader correctly reads V2 records. Some organizations use different deployment-oriented terminology, so every policy must state its convention and direction.
4. **How can an optional field addition break a consumer?** A consumer may reject unknown fields, validate against a closed schema, assume exact field sets, or need the new field for a business invariant. A new reader can also mishandle old records if it does not correctly handle absence.
5. **Why test unknown enumeration values?** A consumer may throw, drop the record, route it incorrectly or silently map it to a misleading known state. Tests must prove both parsing behavior and business behavior; preserving an unknown value alone does not implement the new status's rules.
6. **What is the difference between a default and an observed historical fact?** A default is an imposed rule for missing data; an observed fact is supported by source evidence. A default such as `false` must not be presented as proof that a customer was not verified when the actual historical state is unknown.
7. **What evidence is needed before removing an old field?** Verified dependency inventory including transitive/shadow consumers; owner sign-offs or approved exceptions; migration and contract-test results; successful reconciliation; monitoring showing no required old-field usage over the agreed window; historical interpretation plan; and an approved rollback/forward-fix and retirement decision.
8. **When should historical records be adapted rather than rewritten?** Prefer a version-aware adapter or curated layer when original shapes/meaning must be preserved, conversion is ambiguous, legal/audit evidence matters, or rewriting would erase provenance. In-place rewriting can be suitable for deterministic, lossless transformations when original evidence and lineage remain available and the migration is tested.

## 10. Common mistakes and misconceptions

1. **Treating “backward compatible” as self-explanatory.** Always state direction and whether you mean reader/writer or deployment compatibility.
2. **Calling every additive change safe.** Unknown fields, enumerations, required semantics and business rules can still break consumers.
3. **Assuming a type widening is always safe.** Range, precision, representation, language limits and units can change.
4. **Changing meaning without changing the field name.** This can silently corrupt reports and decisions.
5. **Renaming without a transition.** A rename behaves like remove-plus-add for consumers that reference the old name.
6. **Ignoring historical shapes.** Old records do not automatically acquire new fields or semantics.
7. **Treating missing as false or zero.** Absence, unknown, not applicable and negative values need distinct meanings where relevant.
8. **Using defaults to hide missing source evidence.** A parser default is not proof that a business fact existed.
9. **Assuming lineage is complete.** Spreadsheets, scripts and exports may be undocumented.
10. **Running dual writes without reconciliation.** Partial failures can create divergent representations.
11. **Planning rollback only as code deployment.** Data may already have been transformed or downstream outputs produced.
12. **Removing the old representation on a calendar date alone.** Removal requires evidence and an approved gate.
13. **Using a schema checker as a semantic oracle.** Automated tools cannot fully determine business meaning.
14. **Tightening constraints before profiling existing data.** Old rows may fail the new rule.
15. **Confusing versioning with compatibility.** A version number identifies a contract revision; it does not make a breaking change safe.
16. **Big-bang migration without a recovery path.** Large cutovers increase blast radius and complicate reconciliation.

## 11. Mastery criteria

You are ready to complete Module 7 when you can:

- [ ] State the exact backward- and forward-compatibility definitions and version direction used.
- [ ] Correctly classify the changes in Section 4.4, including semantic, constraint and enumeration changes.
- [ ] Explain why syntactic compatibility does not guarantee behavioral or business compatibility.
- [ ] Produce a consumer impact analysis with dependencies, effects, actions, owners and deadlines.
- [ ] Design a customer-model evolution plan with five consumers.
- [ ] Plan expand-and-contract migration with rollout order, backfill, dual-read/write decisions, validation, rollback and removal criteria.
- [ ] Handle a mandatory attribute for new accounts without fabricating historical values.
- [ ] Handle an added status value without silently misclassifying it.
- [ ] Handle a widened type whose units changed as a semantic migration.
- [ ] Define old-schema historical-data handling and an adapter or normalization strategy.
- [ ] Produce compatibility tests using V1/V2 schemas, representative records and consumer contracts.
- [ ] Define post-migration reconciliation checks and thresholds.
- [ ] Write a dated deprecation notice with support actions and retirement criteria.
- [ ] Distinguish automated pipeline checks from decisions requiring domain-owner review.

## 12. Completion gate

Do not mark this module complete until the evidence below has been reviewed and the practice questions have been answered and corrected.

- [ ] **Change classification reviewed:** add/remove/rename/retype/optionality/constraints/enumerations/semantic changes have direction-specific compatibility assessments.
- [ ] **Impact analysis reviewed:** producers, direct and transitive consumers, historical records, constraints and operational processes are addressed; unknown dependencies are recorded as risk.
- [ ] **Transition plan reviewed:** expand-and-contract sequence, rollout order, backfill, dual reads/writes, validation, rollback/forward-fix and final removal gates are explicit.
- [ ] **Compatibility and deprecation policy reviewed:** contract class, versioning, notification, support window, exceptions and removal criteria are defined.
- [ ] **Semantic-change case handled explicitly:** at least one same-type meaning change is treated as a potential silent break.
- [ ] **Historical-data approach reviewed:** old shapes, missing values, version-aware adapters and preservation of original meaning are addressed.
- [ ] **Testing evidence reviewed:** old/new schemas, representative sample records, consumer contract tests and post-migration reconciliation are specified.
- [ ] **Topic 7 practice questions answered and corrected.**

**Completion evidence:** a change classification table, consumer impact analysis, transition plan, compatibility/deprecation policy, five-consumer customer-model plan, sample deprecation notice and corrected practice-question answers.

**Final quality test:** another architect should be able to determine exactly which version directions were tested, which consumers may be affected, how old records will be interpreted, what proves the migration is correct, who approves removal, and how the system recovers if the change fails.
