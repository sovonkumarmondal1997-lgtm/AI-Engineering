# 07 — Retention, Archival, and Data Lifecycle Storage Tiers

> **Stage 2D — Data Architecture · Database and Storage Architecture**  
> **Audience:** Applied data architects and data engineers progressing from foundations to production design.  
> **Scope:** Vendor-neutral architecture, governance, lifecycle automation, cost economics, retrieval, holds, and verifiable disposition.

## 1. Learning objectives

By the end of this lesson, you should be able to:

1. Model a data lifecycle from creation through active use, infrequent use, archival, and disposition, including a legal hold that interrupts normal deletion.
2. Distinguish business, operational, contractual, legal/regulatory, investigation, and privacy-driven retention drivers.
3. Require a traceable source, accountable owner, review date, and approval status for each retention rule; route legal interpretation to the appropriate legal, privacy, compliance, or records authority.
4. Compare hot/active, warm/infrequent, and cold/archive tiers by access pattern, retrieval latency, storage price, retrieval/request costs, and operational constraints without assuming provider terminology is universal.
5. Explain why backup and archive have different objectives and controls.
6. Produce a retention schedule linking data class and purpose to minimum/maximum retention, source, owner, hold behavior, tier, deletion method, and verification evidence.
7. Design lifecycle automation with safe transitions, retrieval runbooks, metadata preservation, format readability, exception handling, and ownership.
8. Calculate monthly lifecycle cost, including storage, retrieval, requests, transitions, restores, and operational effort; calculate an illustrative break-even point.
9. Design auditable disposition across primary stores, replicas, snapshots, backups, derived datasets, exports, and downstream consumers, with explicit limitations for immutable backups and legal holds.
10. Resolve conflicts among minimum retention, maximum retention, legal holds, and operational requirements by recording unresolved decisions and preventing unsafe automation.
11. Define evidence-based checks—such as quarterly restore and deletion verification—with owners, scope, and measurable success criteria.

**Acronyms used:** RPO = Recovery Point Objective (the maximum tolerable data loss measured in time); RTO = Recovery Time Objective (the target time to restore a service); SLA = Service-Level Agreement; PII = Personally Identifiable Information; TTL = Time to Live; ADR = Architecture Decision Record; KMS = Key Management Service; WORM = Write Once, Read Many; ETL/ELT = Extract, Transform, Load / Extract, Load, Transform.

## 2. Why the topic matters in real-world data architecture

Data lifecycle design balances several objectives that can conflict:

- **Business value:** historical records may support customer service, analytics, dispute resolution, model evaluation, or audit trails.
- **Operational usability:** frequently queried data should meet latency and availability targets; rarely used data may tolerate slower retrieval.
- **Cost:** storage is only one cost. Retrieval, request volume, transition operations, restores, duplicated copies, indexing, and staff time can dominate total cost.
- **Recoverability:** backups and replicas help recover from failure, but they introduce additional copies that must be governed.
- **Privacy and minimisation:** retaining identifiable data longer than necessary can create exposure and conflict with approved maximum-retention rules.
- **Legal, regulatory, contractual, and investigation needs:** an organisation may need to preserve particular records, but the requirement and duration must be established from an applicable source and confirmed by the accountable authority.

Keeping everything forever on the fastest tier is usually expensive and may be unsafe. Deleting too early can undermine business operations or a confirmed preservation obligation. Deleting too late can violate an approved privacy or records policy. A defensible design makes the decision explicit, traceable, testable, and reversible where appropriate.

### 2.1 A simple lifecycle

```text
CREATE / INGEST -> ACTIVE USE -> INFREQUENT USE -> ARCHIVE
                       |               |              |
                       +---------------+--------------+
                                       |
                                       v
                         ELIGIBILITY / POLICY REVIEW
                                       |
                    approved conditions met; no blocker
                                       v
                            DISPOSITION WORKFLOW
                                       |
                         verified removal / approved
                         transformation / exception

ARCHIVE --authorised retrieval--> RESTORE TO CONTROLLED LOCATION
                                      |
                     validate and return to an approved use state
                     (the original retention clock does not reset
                      unless the approved policy explicitly says so)

LEGAL HOLD: an overlay/constraint on every in-scope state and copy;
            blocks disposition until authorised release and re-check.
```

This is a conceptual model, not a universal state machine. A legal hold can be applied at any relevant stage and must block affected disposition actions until the authorised release is recorded. A hold does not automatically mean that data must remain in the most expensive tier; preservation, access controls, and evidence must be designed separately.

### 2.2 The rule of authority

A retention value is not trustworthy merely because it appears in a spreadsheet or a default configuration. For every rule, record:

- **Source:** the specific policy, contract clause, confirmed legal interpretation, records schedule, approved business requirement, or privacy decision that supports it.
- **Owner:** the role accountable for the data class and policy; name the approving legal/privacy/compliance authority where interpretation is required.
- **Scope:** systems, fields, records, copies, derived outputs, regions, and time period covered.
- **Decision status:** approved, provisional, disputed, or blocked pending review.
- **Review date and change history:** who approved a change, why, when it takes effect, and which automation/configurations are affected.

This lesson does **not** prescribe legal retention periods. Legal and regulatory interpretation is jurisdiction-, record-, and organisation-specific. Confirm it with the appropriate legal, privacy, compliance, or records authority. If minimum and maximum retention requirements appear inconsistent, do not silently pick one: record the conflict and prevent automatic deletion or indefinite retention until the authorised decision is made.

## 3. Prerequisite knowledge

The roadmap identifies Modules 1–6 in Database and Storage Architecture and the requirements/volume work in the broader Data Architecture stage as prerequisites. In practical terms, be comfortable with:

- **Storage selection and layout (Topics 1–5):** operational versus analytical stores, object storage and file formats, warehouse/lakehouse table formats, partitioning, snapshots, indexes, and data layout.
- **Replication and consistency (Topic 6):** primary and replica copies, asynchronous lag, transaction boundaries, failure recovery, reconciliation, and the difference between a replica and an independent backup.
- **Requirements and volume estimation:** access frequency, data growth, retrieval latency, RPO/RTO, service objectives, data classification, and business ownership.
- **Basic economics:** multiplying volume by unit price, converting TB/GB carefully, estimating recurring and one-time costs, and stating assumptions.
- **Data governance fundamentals:** classification, lineage, access control, data ownership, change approval, and audit evidence.

**Dependency check:** lifecycle rules can require changes to format, table history, snapshots, replication, and query layout. After drafting a policy, revisit Topics 3–6 to verify that the chosen formats remain readable, table snapshots do not preserve prohibited data indefinitely, replicas follow the correct policy, and restore/retrieval still meets the required objectives.

## 4. Beginner-level learning sequence

### 4.1 Learn lifecycle stages and state transitions

| Stage | Meaning | Why it exists | Typical decision or control | Validation |
|---|---|---|---|---|
| Create / ingest | A record is first captured or generated | Establish provenance and start the lifecycle clock | Assign data class, purpose, owner, event timestamp, source, and policy version | Required metadata is present; clock-start rule is unambiguous |
| Active / hot | Data is regularly used by operational workloads | Meet low-latency access and high availability expectations | Keep in an access-appropriate store/tier; apply active security and backup controls | Measured latency and access pattern meet the workload target |
| Infrequent / warm | Access is occasional, but retrieval should remain reasonably quick | Reduce storage cost without unacceptable retrieval delay | Transition only after a documented access-pattern threshold | Test actual retrieval latency, charges, and application compatibility |
| Archive / cold | Data is rarely accessed but remains required and must remain retrievable | Lower recurring storage cost for long-lived history | Preserve catalog, schema, keys, provenance, and retrieval instructions | Sample records can be located, restored, parsed, and interpreted |
| Eligible for disposition | The approved retention condition appears satisfied | Avoid keeping data beyond an approved period | Evaluate holds, minimum retention, maximum retention, dependencies, and exceptions | Decision log shows why the record is or is not eligible |
| Delete / dispose | Approved copies are removed, anonymised, or otherwise disposed of according to policy | Meet minimisation and lifecycle obligations | Execute a scoped workflow and track asynchronous copy expiry where needed | Evidence confirms each in-scope system completed or has an approved exception |

A record can be restored from archive for a valid business purpose. Restoration does not automatically reset its original retention clock. If the business intends to create a new record or a new legal/business purpose, the owner must define that rule explicitly rather than silently restarting retention.

### 4.2 Understand retention drivers

Retention is not one universal timer. Different drivers answer different questions:

| Driver | Question it answers | Example (illustrative, not a legal claim) | Required evidence/owner |
|---|---|---|---|
| Business need | How long does the business need this record? | Keep a product-performance aggregate for a defined planning cycle | Business owner and approved purpose |
| Operational need | How far back must a service investigate incidents or reconcile operations? | Retain operational events long enough to support an approved troubleshooting window | Service owner, incident process, and operational requirement |
| Legal/regulatory obligation | What must be preserved, for how long, and under what scope? | A record class subject to a confirmed records schedule | Applicable source plus legal/compliance/records confirmation |
| Contractual obligation | What does an executed contract require? | Retain delivery evidence for a contractually defined period | Contract clause, contract owner, and legal confirmation where needed |
| Investigation / dispute | Must specified evidence be preserved for a case? | Preserve a scoped set of records under an authorised case hold | Case reference, authorised requester, scope, start/release authority |
| Privacy-driven maximum | When must identifiable data no longer be retained for the approved purpose? | Remove a direct identifier after an approved purpose-specific limit | Privacy decision, data owner, scope, and verified deletion path |

**Important distinction:** a minimum retention is a lower bound for keeping a defined record; a maximum retention is an upper bound for retaining a defined record or field for a defined purpose. A legal hold is a separate preservation constraint. Backup expiry is the policy for backup copies, not automatically the same as primary-record retention. Deletion verification is evidence that the disposition workflow achieved its stated scope; it is not itself a retention rule.

### 4.3 Compare storage tiers without assuming universal provider behavior

“Hot,” “warm,” and “cold” are useful architecture labels, not guaranteed product names or uniform technical categories. Compare actual service characteristics and contracts before selecting a tier.

| Dimension | Hot / active (conceptual) | Warm / infrequent (conceptual) | Cold / archive (conceptual) |
|---|---|---|---|
| Access frequency | Frequent or latency-sensitive | Occasional | Rare and planned |
| Retrieval latency | Usually low; often online | Usually online or with modest delay | May require a restore/re-hydration job and can take minutes or hours, depending on service |
| Storage cost per unit-month | Often highest of the three | Often lower | Often lowest |
| Access/retrieval cost | Often low incremental retrieval charge, but not guaranteed | May include retrieval charges | May include retrieval, minimum-duration, restore, or early-deletion charges |
| Request/operation cost | Requests may be priced or constrained | Request pricing may differ | Listing, retrieval, restore, and transition requests may have separate costs |
| Operational constraints | Optimised for interactive access | Test application timeout and access patterns | Catalog, restore workflow, retrieval approval, format readability, and service limits become critical |
| Typical fit | Current operational data and frequent analytics | Recent history with occasional access | Historical evidence or datasets rarely accessed but still required |
| Failure mode | Paying premium price for cold data | Unexpected reads erase savings | Unreadable, undiscoverable, or slow-to-restore archive; unexpected retrieval bill |

Do not choose a tier solely from the lowest advertised storage price. Measure or estimate the full access pattern, including the frequency and size of retrievals, request counts, restore delay, minimum storage duration, transition charges, egress where applicable, and staff time. Use provider-specific price sheets only when a real implementation is being evaluated; prices in this lesson are intentionally illustrative.

### 4.4 Distinguish archive from backup

| Property | Backup | Archive |
|---|---|---|
| Primary objective | Recover from loss, corruption, accidental changes, or operational failure | Preserve selected historical information for long-term retention and later retrieval |
| Typical selection | System state, databases, configuration, and data needed to restore a service | Records or datasets selected under a retention schedule |
| Recovery/retrieval | Restore a usable system or data state within recovery objectives | Find and retrieve specific historical records with enough context to interpret them |
| Retention | Usually governed by recovery design and backup rotation/expiry | Governed by approved record lifecycle, purpose, and preservation constraints |
| Integrity evidence | Restore tests, backup monitoring, recovery drills | Catalog, integrity checks, sample retrieval, schema/format validation, provenance |
| Discovery/record context | May not provide searchable record-level context | Should preserve identifiers, metadata, timestamps, policy references, and retrieval instructions where required |

A backup is not automatically an archive because it may expire, be difficult to search at record level, lack a retention classification, or restore an entire system rather than a specific historical record. An archive is not automatically a backup because it may not provide the recovery point, isolation, or restoration speed required for disaster recovery. A design may use both, with separate policies and explicit relationships between copies.

### 4.5 Beginner exercise: classify ten datasets

For each hypothetical dataset below, state its purpose, likely lifecycle stage, access pattern, candidate tier, retention driver(s), accountable owner, and one question that must be resolved before automation. Do not invent a legal period.

1. Current customer account state.
2. Raw application debug logs.
3. Settled transaction evidence.
4. A derived monthly aggregate used by analysts.
5. A feature table used by an online model.
6. A model evaluation dataset containing direct identifiers.
7. Historical product clickstream events.
8. Database backups.
9. An exported spreadsheet sent to a partner.
10. Records linked to an open investigation.

**Answer guidance:** there is no single tier or retention answer without workload and governance evidence. A strong answer names the owner and source, distinguishes raw records from derived data and backups, identifies copies/downstream recipients, and flags unresolved requirements. Records linked to an open investigation need hold evaluation; do not infer that every record in the dataset is automatically in scope.

## 5. Intermediate-level learning sequence

### 5.1 Build a retention schedule that can be operated

The schedule is the control plane for lifecycle policy. One row should describe a coherent class, purpose, scope, and policy. Split rows when fields have different maximum retention, when a dataset has different legal/business purposes, or when copies require distinct controls.

| Required field | What to record | Quality test |
|---|---|---|
| Data class / record scope | Dataset, record type, field scope, sensitivity, system of record, and covered copies | A reader can tell exactly what is in scope and what is not |
| Purpose | Approved business or operational purpose | Purpose is specific enough to justify keeping the data |
| Retention start event | Event that starts the clock, such as record creation, case closure, or end of relationship | Event is observable, timestamped, and consistent across systems |
| Minimum retention | Lower bound, or “not established—review required” | Value is sourced; the schedule states whether it is a confirmed obligation or a provisional business rule |
| Maximum retention | Upper bound for the record/field/purpose, or “not established—review required” | Privacy/records owner confirms scope and clock; it is not silently omitted |
| Source and citation | Policy ID/version, contract clause, approved requirement, or confirmed authority | Source can be opened and supports the actual scope and duration |
| Accountable owner | Business/data owner and approving legal/privacy/compliance/records authority as applicable | A role is accountable for decisions and review |
| Decision status / review date | Approved, provisional, conflict, blocked; next review and change history | Unresolved rules cannot flow into destructive automation |
| Legal-hold rule | Trigger, scope, authorised issuer/releaser, status source, and release evidence | Hold overrides normal disposition for in-scope records and copies |
| Storage tier / transition | Tier by stage, eligibility threshold, latency target, and exception behavior | Access objectives and all-in economics are considered |
| Deletion / disposition method | Delete, cryptographic erasure where appropriate, anonymise, or another approved method; include all copy types | Method is supported by each in-scope platform and meets policy intent |
| Backup/replica/snapshot behavior | Replica propagation, snapshot expiry, immutable backup limits, recovery copy rules | The schedule does not assume that primary deletion immediately removes every copy |
| Verification evidence | Job ID, inventory, tombstone/acknowledgement, query result, restore test, exception, and timestamp | Evidence proves the claimed scope and outcome, not merely that a job ran |
| Exception owner | Role and escalation path for inaccessible copies, failed jobs, conflicts, or vendor constraints | Exceptions have a deadline and cannot disappear into an unowned queue |

### 5.2 Worked retention schedule (illustrative)

The following is a design exercise, not a legal recommendation. Every duration is deliberately a placeholder until approved by the relevant authority.

| Data class | Purpose | Minimum | Maximum | Source / status | Owner | Hold rule | Tier | Disposition | Verification evidence |
|---|---|---|---|---|---|---|---|---|---|
| Operational service logs | Troubleshooting and reliability analysis | Not established; business owner to propose | Not established; privacy review needed if identifiers are present | Draft operational policy `OPS-LOG-DRAFT`; **provisional** | Service owner + privacy reviewer | Case-scoped hold only when authorised and logged | Hot while actively queried; warm after measured access decline | Delete or approved aggregation after decision; remove copies per inventory | Quarterly sample query, expiry-job record, copy inventory reconciliation |
| Settled transaction record | Transaction servicing and approved recordkeeping | Pending confirmed records schedule | Pending privacy/records review; possible field-specific maxima | **Blocked** pending legal/records and privacy review | Transaction data owner; legal/records authority | Preserve matching records under authorised case hold | Hot for operational period; warm/archive after access-pattern validation | Controlled disposition after minimum and maximum constraints reconciled | Policy approval ID, hold audit, retrieval test, deletion manifest |
| Direct customer identifier in an analytical feature set | Model feature generation for an approved purpose | No minimum established by this example | Field-level maximum pending privacy decision | **Blocked** until purpose, necessity, and maximum are confirmed | Feature owner + privacy owner | Hold applicability must be decided by authorised reviewer; hold scope documented | Keep only as long as approved purpose and access needs require; tiering does not extend permission | Remove field or transform data when approved; reprocess derived stores and exports | Field lineage report, transformation test, downstream acknowledgement, sample scan |
| Database backup | Recovery from corruption or service failure | Recovery design requirement, not a recordkeeping minimum by itself | Backup expiry policy to be approved separately | Backup/DR policy and service owner approval | Platform/recovery owner | Hold preservation must be designed if backups are in scope; never assume ordinary expiry may destroy held evidence | Recovery tier appropriate to RPO/RTO | Expire/rotate according to approved backup policy, subject to hold/retention constraints | Scheduled restore test, backup expiry report, exception log |

**Schedule rule:** “Not established” is a valid and important state. It is not equivalent to zero days, indefinite retention, or permission to delete. A policy engine should treat unresolved rules as blocked from irreversible disposition until the designated owner resolves them.

### 5.3 Lifecycle automation: what it should and should not do

A lifecycle engine may schedule tier transitions, evaluate eligibility, open disposition work items, and record evidence. It should not invent policy, resolve legal conflicts, or treat missing metadata as permission to delete.

A safe conceptual workflow is:

1. **Classify at ingestion:** attach data class, purpose, source event, owner, policy version, and lineage/copy identifiers. Reject or quarantine records with missing mandatory metadata according to a defined exception policy.
2. **Calculate eligibility:** derive age from the approved start event and apply the current approved policy version. Do not use object modification time unless the policy explicitly defines it as the clock.
3. **Check blockers:** query hold registry, legal/records status, unresolved conflict status, dependencies, and any required minimum-retention condition. If the hold system is unavailable or status is unknown, fail closed for destructive actions.
4. **Transition tier:** move only when access-pattern and retrieval objectives allow it. Preserve identity, checksum/integrity evidence, schema/version, encryption/key references, provenance, and catalog location.
5. **Notify/record:** emit an auditable transition event with policy version, actor/job, source/destination, timestamp, result, and exception details.
6. **Evaluate disposition:** when expiry is reached, generate a candidate list, apply hold and dependency checks, and require approval where policy calls for it. Separate candidate evaluation from irreversible deletion.
7. **Execute across copies:** fan out deletion or approved transformation to known replicas, snapshots, derived stores, search indexes, caches, exports, and downstream recipients. Track asynchronous completion explicitly.
8. **Verify and close:** reconcile the intended scope against inventory and system acknowledgements. Keep exceptions open with an owner and deadline; produce evidence suitable for audit.

**When automation is appropriate:** stable, approved rules with reliable metadata, a complete copy inventory, testable APIs, and a clear exception path. **When manual review is required:** unresolved minimum/maximum conflicts, uncertain hold scope, unknown copies, irreversible transformations, failed inventory checks, or policy changes with uncertain impact.

### 5.4 Archive retrieval and long-term readability

Cold data is useful only if the organisation can locate and interpret it later. An archive design should preserve:

- A catalog or manifest linking business identifiers to physical objects, partitions, versions, and locations.
- Schema and data dictionary versions, field definitions, units, timezone conventions, code sets, and semantic meaning.
- Format and table-format versions, compression/encoding details, and any required decoder or migration instructions.
- Provenance: source system, extraction time, transformation lineage, policy version, and integrity checksums or equivalent evidence.
- Encryption and key-management dependencies, access permissions, retrieval approvals, and a tested procedure for restoring data without exposing it unnecessarily.
- Links between records and associated metadata, legal holds, case identifiers, and derived datasets where appropriate.

Schema evolution can make old data technically readable but semantically wrong. For example, a field whose unit changes from cents to currency units, or whose meaning changes after a schema revision, can produce misleading historical analysis without a versioned definition. Archive validation must therefore test interpretation, not just file decompression.

**Retrieval runbook (minimum):** identify requester and purpose; authorise access; locate the manifest; confirm hold/privacy constraints; estimate retrieval cost and delay; retrieve to a controlled temporary location; validate checksum/schema/record counts; log access; deliver only the approved subset; securely remove temporary copies under the relevant policy. Test this path periodically with representative old records.

### 5.5 Lifecycle cost model

The required storage-only formula is:

```text
monthly_storage_cost = Σ (tier_volume × tier_price_per_unit_month)
```

For a useful decision, calculate total monthly lifecycle cost as:

```text
monthly_total_cost =
    monthly_storage_cost
  + retrieval_volume × retrieval_price_per_unit
  + request_count × request_price_per_request
  + transition_volume × transition_price_per_unit
  + restore_jobs × cost_per_restore_job
  + operational_hours × loaded_cost_per_hour
  + other applicable charges
```

The “other applicable charges” may include minimum-duration or early-deletion charges, data transfer/egress, replication, index/catalog services, encryption/key management, monitoring, and support. Avoid double-counting charges already included in a quoted unit price. Separate one-time migration cost from recurring monthly cost and state the analysis horizon.

#### Worked example: compare hot and archive economics

**All values below are illustrative assumptions, not provider quotations.** Use decimal units: 1 TB = 1,000 GB for this worksheet.

Assume a stable historical dataset of **100 TB**. Compare keeping it all in a hot tier with moving it all to an archive tier. Prices and access pattern are hypothetical:

| Cost input | Hot tier | Archive tier |
|---|---:|---:|
| Storage price | ₹20 per GB-month | ₹4 per GB-month |
| Monthly retrieval volume | 0.5 TB = 500 GB | 0.5 TB = 500 GB |
| Retrieval price | ₹0 per GB (assumed included) | ₹80 per GB |
| Request charges | ₹500/month | ₹500/month |
| Transition charge | ₹0/month | ₹0 for this steady-state comparison; migration excluded |
| Restore jobs | 0 | 2 jobs × ₹1,000 = ₹2,000/month |
| Operations | 2 hours × ₹800/hour = ₹1,600/month | 3 hours × ₹800/hour = ₹2,400/month |

**Hot monthly cost**

- Storage: 100 TB × 1,000 GB/TB × ₹20/GB-month = 100,000 GB × ₹20 = **₹2,000,000/month**.
- Retrieval: 500 GB × ₹0/GB = **₹0/month**.
- Requests: **₹500/month**.
- Restore jobs: **₹0/month**.
- Operations: 2 × ₹800 = **₹1,600/month**.
- **Total = ₹2,000,000 + ₹0 + ₹500 + ₹0 + ₹1,600 = ₹2,002,100/month.**

**Archive monthly cost**

- Storage: 100,000 GB × ₹4/GB-month = **₹400,000/month**.
- Retrieval: 500 GB × ₹80/GB = **₹40,000/month**.
- Requests: **₹500/month**.
- Restore jobs: 2 × ₹1,000 = **₹2,000/month**.
- Operations: 3 × ₹800 = **₹2,400/month**.
- **Total = ₹400,000 + ₹40,000 + ₹500 + ₹2,000 + ₹2,400 = ₹444,900/month.**

**Illustrative savings:** ₹2,002,100 − ₹444,900 = **₹1,557,200/month**. This comparison assumes the archive tier satisfies retrieval latency and availability requirements, and that the stated prices cover all listed costs. It excludes migration/transition costs and any minimum-duration or egress charges; include those for a real decision.

#### Break-even retrieval volume

For a simple break-even calculation, isolate costs that vary with retrieval. Assume the archive's monthly non-retrieval cost is ₹404,900 (₹400,000 storage + ₹500 requests + ₹2,000 restore jobs + ₹2,400 operations), and hot's monthly non-retrieval cost is ₹2,002,100. Under these assumptions, archive non-retrieval cost is already lower by ₹1,597,200/month. Archive retrieval costs ₹80/GB more than hot retrieval, because hot retrieval is assumed ₹0/GB.

```text
monthly_cost_difference_before_retrieval = hot_nonretrieval_cost - archive_nonretrieval_cost
                                      = ₹2,002,100 - ₹404,900
                                      = ₹1,597,200/month
break_even_retrieval_volume = monthly_cost_difference_before_retrieval
                              / (archive_retrieval_price - hot_retrieval_price)
                            = ₹1,597,200/month ÷ ₹80/GB
                            = 19,965 GB/month
```

At approximately **19,965 GB/month (19.965 TB/month)** of archive retrieval, the additional retrieval charge consumes the stated non-retrieval savings and total costs are equal, provided all other assumptions remain unchanged. Above that point, the hot option becomes cheaper in this simplified cost model. This is not a recommendation to move data hot: latency, recovery, security, and service objectives still matter. The worksheet also assumes request and restore-job costs do not change as retrieval volume rises; in production, model those as volume-dependent when appropriate.

#### Cost worksheet to reuse

| Variable | Unit | Value | Source / assumption |
|---|---|---:|---|
| Volume by tier | GB or TB, consistently converted |  | Inventory and measurement date |
| Storage price | currency / GB-month |  | Current provider quote or approved internal rate |
| Retrieval volume | GB/month |  | Query/access logs or scenario estimate |
| Retrieval price | currency / GB |  | Quote and billing unit verified |
| Requests | requests/month |  | Measured or forecast count |
| Request price | currency/request |  | Quote and billing unit verified |
| Transition volume | GB/month |  | Lifecycle policy simulation |
| Transition price | currency/GB or request |  | Quote; clarify both dimensions if applicable |
| Restore jobs | jobs/month |  | Restore plan and test frequency |
| Operations | hours/month |  | Estimated engineering/operations effort × loaded hourly cost |
| One-time migration | currency |  | Migration, validation, re-indexing, rollback provision |
| Minimum-duration/early-delete/egress | applicable unit |  | Contract/provider tariff; do not assume zero |

**Validation:** independently recompute every multiplication and sum, ensure the volume unit matches the price unit, confirm whether prices are monthly or per operation, separate one-time and recurring costs, and perform sensitivity analysis for access volume, tier price, restore delay, and staff effort.

## 6. Advanced-level learning sequence

### 6.1 Minimum retention, maximum retention, holds, and deletion are different controls

These controls must be represented separately because their semantics differ:

- **Minimum retention:** the defined record must not be disposed of before a specified condition/date, subject to the confirmed source and scope.
- **Maximum retention:** the defined record or field must not be retained beyond a specified condition/date for the approved purpose, subject to the confirmed source and scope.
- **Legal hold / preservation hold:** an authorised instruction to preserve specified evidence. It may suspend ordinary disposition for in-scope data while active. Scope and release authority must be explicit.
- **Backup expiry:** removes a recovery copy according to a separate recovery policy, unless a hold or approved retention requirement applies to that copy.
- **Deletion verification:** evidence that the disposition request completed across the defined systems/copies, with any known exceptions clearly recorded.

A hold is not a substitute for a retention schedule. It should have an issuer, case/reference, scope, effective timestamp, source, review cadence, authorised release process, and evidence of release. Avoid a vague “hold all data” flag unless the authorised scope truly covers all data. Equally, do not narrow a hold by technical convenience when the authority has defined a broader scope.

### 6.2 Handle minimum-versus-maximum conflicts safely

Suppose an approved records requirement appears to establish a long minimum retention for a transaction record, while an approved privacy rule establishes a shorter maximum retention for a field embedded in that record. A legal hold may also apply to the transaction or a specific subset.

Do not assume the whole record can be deleted, that the field can always be retained, or that anonymisation is automatically permissible. The correct design is to:

1. Record each requirement separately with exact source, scope, clock start, authority, version, and status.
2. Identify the conflict at the smallest meaningful scope (record, field, purpose, copy, and time period).
3. Mark the affected policy row **conflict—blocked for automated disposition** and assign a legal/privacy/records review owner and due date.
4. Prevent the lifecycle engine from deleting or retaining the disputed field by default. Use a safe, approved interim control, such as restricted access and isolation, only if authorised; do not use “retain forever” as a substitute for a decision.
5. Ask the authorised reviewers to decide whether a legally valid separation, masking, redaction, tokenisation, anonymisation, or other treatment is permissible while preserving the required evidence. These are options for review, not presumed solutions.
6. Document the approved decision, affected copies and derived data, effective date, implementation owner, test cases, and rollback/exception plan.
7. Update the policy version and test that all automated paths enforce the same rule.

A privacy-driven maximum must not be silently ignored because another rule has a longer minimum. A minimum must not be silently violated because a field has a shorter maximum. The conflict needs authoritative resolution; the system must make the conflict visible and block unsafe automation until then.

### 6.3 Deletion and erasure across the copy graph

Deletion is a distributed lifecycle operation, not a single `DELETE` statement. Build an inventory/lineage graph that includes, where applicable:

- System-of-record tables and operational replicas.
- Read replicas, search indexes, caches, materialized views, and change-data-capture (CDC) consumers.
- Warehouse/lakehouse tables, derived aggregates, feature stores, vector indexes, and model-serving stores where records or identifiers can persist.
- Table snapshots, time-travel history, versioned objects, soft-delete markers, and object versions.
- Backups, immutable/WORM copies, disaster-recovery replicas, and offline media.
- Exports, analyst workspaces, notebooks, local files, reports, partner transfers, and downstream consumers.
- Catalogs, metadata, logs, manifests, and audit records. These may need a different treatment from the underlying payload; do not assume every metadata record should be erased or retained without policy authority.

A robust workflow:

1. **Receive and validate request/trigger.** Authenticate the requester or source event; confirm the data subject/record identity and scope. Prevent ambiguous identifiers from triggering broad deletion.
2. **Resolve policy.** Determine approved purpose, retention minimum/maximum, hold status, applicable exception, and required approvals.
3. **Compute copy scope.** Use lineage and copy inventory to identify stores, snapshots, derived outputs, exports, and downstream recipients. Record gaps in inventory as exceptions.
4. **Plan disposition.** Decide which copies are deleted, transformed, access-restricted, or allowed to expire under an approved immutable-backup policy. Legal/privacy/records authority must approve any non-immediate path where required.
5. **Execute idempotently.** Use a stable request ID, durable work queue, retry-safe actions, per-system status, and a clear definition of completion. Avoid claiming success just because a message was emitted.
6. **Verify.** Check the primary store, replicas, snapshots/version history, derived stores, exports/consumers, and backup policy. Use system acknowledgements plus targeted queries or scans where technically feasible.
7. **Record evidence.** Preserve the request ID, policy version, scope, systems contacted, outcomes, timestamps, verification method, and exception approvals. Keep the audit evidence itself under its own approved policy.
8. **Close or escalate.** Close only when required scope is verified or when an authorised exception explicitly records what remains, why, until when, who owns it, and what compensating control applies.

**Immutable backups and delayed expiry:** a backup may be technically immutable for a defined period. If so, do not promise immediate physical erasure from that backup. Prevent normal use, restrict access, record the expiry date and hold interactions, and ensure the approved policy defines how restored data is reprocessed so deleted records are not silently reintroduced. If a legal hold applies, the authorised authority must determine whether the backup is in scope and how it is preserved. This lesson does not determine the legal answer.

**Cryptographic erasure**—destroying the key needed to decrypt data—can be a control in a designed encryption architecture, but it is not automatically equivalent to deletion in every context. Validate key granularity, key backups, plaintext copies, derived data, legal constraints, and evidence before relying on it.

### 6.4 Connect lifecycle design to Topics 3–6

| Earlier topic | Lifecycle dependency | Required review question |
|---|---|---|
| Topic 3 — object storage and file-format selection | Long retention depends on durable formats, metadata, integrity, encryption, versioning, and readable schemas | Can an authorised operator still locate, decrypt, parse, and interpret the record years later? How do object versions and lifecycle transitions affect disposition? |
| Topic 4 — warehouse/lakehouse/table-format design | Snapshots, time travel, table history, compaction, and derived tables can preserve data after a logical delete | Which table history/snapshot policies retain old values, and how does approved deletion propagate to those structures? |
| Topic 5 — partitioning, indexing, clustering, and data layout | Partition design can make age-based expiry efficient, but field-level erasure may cut across partitions | Does layout support safe, scoped disposition without deleting unrelated records or leaving copies in indexes? |
| Topic 6 — replication, consistency, and transaction boundaries | Asynchronous replicas, dual writes, event consumers, and reconciliation can delay or miss disposition | How is a deletion/hold event propagated, retried, deduplicated, ordered, and reconciled across stores? |

Use deletion tombstones or durable disposition events where they are needed to prevent late-arriving or replayed data from reappearing. Define tombstone retention separately: a minimal marker may need to persist long enough to coordinate downstream systems, but its contents and duration must also be policy-approved. A failed consumer must not cause a record to reappear without detection.

### 6.5 Quantify lifecycle transitions and verify restoreability

Before moving data, model the total transition cost and operational impact:

```text
transition_total_cost = data_moved × transition_price
                      + requests × request_price
                      + validation_compute_cost
                      + temporary_duplicate_storage_cost
                      + operator_hours × loaded_cost_per_hour
```

Check whether the transition changes object count, file size, metadata, encryption/key dependencies, table snapshots, query performance, or restore steps. Run a representative pilot, compare record counts/checksums, measure latency and costs, and keep a rollback path until acceptance criteria pass.

**Restore/readability test:** select representative records from each tier and age band; retrieve them using the documented runbook; validate checksums, schema version, record count, units/semantics, permissions, and target latency; confirm that keys and dependencies are available; record actual time and cost. The test should prove the business can use the data, not merely that the object can be downloaded.

### 6.6 Quarterly verification and control ownership

A quarterly cadence is an illustrative baseline, not a universal requirement. Set frequency from risk, volume, policy, and change rate. At minimum, assign named roles and success criteria for these controls:

| Control | Suggested owner | Evidence | Example success criterion (illustrative) |
|---|---|---|---|
| Archive restore/readability | Platform/data platform owner with data owner | Test record IDs, policy/schema version, checksum and semantic validation, duration and cost | All sampled records are retrieved and interpreted correctly within the approved retrieval objective; no undocumented dependency blocks access |
| Deletion propagation | Data owner + platform/integration owner | Disposition request IDs, copy inventory, per-system acknowledgements, sampled searches, exceptions | Every in-scope system reports completion or has an approved, time-bounded exception; no unowned failures |
| Hold enforcement | Legal operations/records owner + platform owner | Test hold, attempted disposition, blocked job, release event, audit trail | Held records are not disposed of by normal automation; authorised release is required and auditable |
| Retention schedule review | Data owner + legal/privacy/records authorities as needed | Source links, approval status, review dates, change log | No expired approval or unresolved conflict is treated as an approved automatic rule |
| Cost and retrieval review | FinOps/platform owner + data owner | Actual billing, retrieval metrics, restore jobs, operational hours | Forecast variance is explained; thresholds trigger review before surprise charges become material |
| Backup restore and expiry | Recovery/platform owner | Restore result, RPO/RTO observation, expiry/hold evidence | Restore meets approved recovery objective; expiry obeys approved backup and hold rules |

An equivalent risk-based cadence can be used if justified and approved. A test must have an owner, scope, timestamp, expected result, actual result, and remediation tracking. “Job succeeded” alone is not proof that a deletion or restore was correct.

### 6.7 Failure modes and safeguards

| Failure mode | Why it happens | Consequence | Preventive/detective control |
|---|---|---|---|
| Default retention is never reviewed | Policy is treated as a one-time configuration | Data accumulates indefinitely or becomes inconsistent with changed purposes/requirements | Scheduled policy review, owner, approval expiry/review date, change alerts, and inventory-based exceptions |
| Archive becomes unreadable after schema/format changes | Schema, codec, key, units, or semantics were not preserved | Data exists physically but cannot be trusted or interpreted | Versioned schemas/data dictionaries, dependency catalog, checksum plus semantic restore tests, migration plan |
| Backups are treated as archives | Recovery copies are assumed to satisfy record retrieval and retention needs | Records may expire unexpectedly or cannot be discovered at record level | Separate backup and archive schedules, purposes, evidence, and owners |
| Replica or snapshot missed during deletion | Copy graph is incomplete or async propagation fails | Deleted data persists or reappears after restore/replay | Lineage/copy inventory, durable deletion events, retries, reconciliation, snapshot/version policy, restore-time reapplication |
| Automation overrides a hold | Hold registry is unavailable, stale, or lower priority than TTL | Destruction of evidence that should be preserved | Fail-closed destructive path, hold precedence tests, signed/authorised release, audit alerts, independent control review |
| Retrieval charges erase storage savings | Decision uses storage price only and ignores access pattern | Budget overrun or inability to retrieve within service targets | All-in cost model, measured retrieval volume, cost alerts, break-even threshold, periodic tier review |
| Clock starts from the wrong timestamp | Modified time is substituted for a defined business event | Premature or delayed deletion | Explicit start event, source timestamp, time-zone and late-arrival rules, boundary tests |
| Missing metadata silently defaults to deletion | Policy engine interprets null as zero/expired | Uncontrolled data loss | Fail closed; quarantine or route to an owned exception queue |
| A restored backup reintroduces deleted data | Restore process does not replay disposition events or reconcile against deletion registry | Privacy or retention policy is violated after recovery | Restore-time tombstone/disposition replay, post-restore reconciliation, documented recovery gate |
| A derived dataset is overlooked | Lineage is incomplete or transformation loses source identifiers | Source deletion does not propagate to derived records | Lineage completeness checks, privacy-aware keys, downstream contracts, recomputation or approved transformation plan |

## 7. Industry-application exercises

### Exercise 1 — Classify and schedule

For each of the ten datasets in Section 4.5, create a retention-schedule row. Include purpose, start event, minimum and maximum status, source, owner, hold rule, tier, disposition, copy scope, and evidence. Use “not established” and “blocked” where the facts are missing. Do not manufacture legal durations.

**Answer guidance:** full credit requires traceable source/owner fields and explicit uncertainty. A tier choice without access-pattern reasoning is incomplete. Backup rows must refer to recovery objectives and backup expiry, not claim that backup policy establishes record retention.

### Exercise 2 — Compare tier economics

Using the worked example, verify the hot and archive totals, then calculate monthly cost if archive retrieval rises to **25 TB/month** under the same illustrative ₹80/GB retrieval rate. Assume request, restore, and operations costs remain unchanged only for this exercise.

**Answer guidance:** 25 TB = 25,000 GB. Retrieval cost = 25,000 × ₹80 = ₹2,000,000/month. Archive total = ₹400,000 storage + ₹2,000,000 retrieval + ₹500 requests + ₹2,000 restores + ₹2,400 operations = **₹2,404,900/month**. This exceeds the illustrative hot total of ₹2,002,100/month by ₹402,800/month. In real workloads, also re-estimate request counts, restore jobs, and operations; the constant-cost assumption is for arithmetic isolation only.

### Exercise 3 — Design the disposition workflow

A customer identifier appears in an operational database, an asynchronous read replica, a lakehouse table, a feature store, a search index, a daily export, and a backup set. A verified disposition trigger arrives, but one downstream consumer is offline and the backup is immutable until a documented expiry date. Describe the workflow from validation to closure.

**Answer guidance:** verify identity/scope and approved policy; check minimum/maximum and holds; create a durable request ID; enumerate every copy; delete/transform where approved; queue retries for the offline consumer; record immutable-backup limitation, access restrictions, expiry date, and approved exception; ensure restore-time reapplication prevents resurrection; reconcile each system; close only after verified completion or an authorised exception with owner/deadline. Do not claim instantaneous physical deletion from immutable copies.

### Exercise 4 — Hold-interruption test

A normal lifecycle job identifies records as expired. Before deletion executes, a hold is placed on a subset. Design the race-safe behavior and tests.

**Answer guidance:** eligibility and deletion must be separated; re-check hold status immediately before irreversible action; use a durable hold registry/event with clear consistency guarantees; fail closed if status is unavailable; scope the hold; log blocked items; test hold arrival before candidate creation, between candidate creation and execution, during retries, and before release. Verify that a hold release is authorised and does not itself delete data without re-evaluating all retention rules.

### Exercise 5 — Archive readability drill

A historical dataset can be downloaded but the schema registry has retired the old schema and one field's units changed. Define acceptance criteria for a restore test.

**Answer guidance:** restore only to a controlled location; recover the exact schema/data dictionary version; verify checksum, record count, null distribution or key invariants, units, timezone, code mappings, and semantic interpretation; document any migration; measure retrieval time/cost; reject the test if values can be decoded but not reliably interpreted.

### Exercise 6 — Lifecycle policy ADR

Write an Architecture Decision Record (ADR) comparing two options for a long-lived dataset: keep all history hot, or transition older data to archive. Include workload evidence, retention sources, owners, minimum/maximum status, hold behavior, all-in economics, retrieval objectives, failure modes, rollout, rollback, monitoring, and the reason rejected options are rejected.

**Answer guidance:** the decision must state assumptions and uncertainty, not only a price comparison. Include sensitivity analysis and specify what evidence would trigger a revisit. A legal/records policy conflict remains unresolved until an authorised reviewer decides it.

## 8. Practical scenarios and case-based reasoning

### Scenario A — Northbridge Bank (fictional illustrative organisation)

Northbridge Bank is a fictional organisation used only for architecture practice. It stores transaction records, operational logs, customer identifiers, analytical aggregates, backups, and investigation evidence across operational databases, replicas, a lakehouse, and object storage. No retention duration in this scenario should be interpreted as a legal requirement.

**Situation (explicit exercise assumptions):** the data platform team proposes moving older transaction records to a low-cost archive tier and deleting identifiers from an analytical feature dataset after an approved purpose-specific maximum. For this fictional exercise only, assume the authorised records schedule has confirmed a **seven-year minimum retention** for a defined transaction-record class; this is an illustrative scenario value, not a claim that any law universally requires seven years. An approved privacy policy also sets a **field-level maximum** for a direct customer identifier, but the scenario does not assign a numeric duration because its clock, scope, and applicability must be taken from that policy. An investigation team may issue a legal hold for a subset of records. The hold's scope may overlap the record, field, archive, or copies and must be determined by the authorised authority.

**Architecture response:**

1. Create separate schedule rows for the transaction record, direct identifier field, derived feature dataset, archive object, replica, backup, and export when their purposes or copy behaviors differ.
2. Record the alleged minimum-retention source and field-level maximum-retention source separately, including owner, version, scope, clock start, and confirmation status. Mark both as pending where not yet confirmed.
3. Mark the affected record/field scope **conflict—blocked for automatic disposition**. Assign legal/records and privacy reviewers with a due date. Do not infer a period or choose one requirement silently.
4. Implement a hold registry with authorised scope, case reference, issuer/releaser, timestamps, and durable status. Normal disposition checks it before candidate creation and again before destructive execution; unknown status blocks deletion.
5. For the archive transition, prove retrieval latency and all-in cost, preserve metadata/schema and integrity evidence, and test a sample restore. Moving data to archive does not itself extend or satisfy retention obligations.
6. Build a copy graph across primary tables, replicas, snapshots/time travel, feature store, lakehouse, exports, and backup sets. Test deletion/tombstone propagation and restore-time reconciliation.
7. Document backup expiry separately from archive retention. If immutable backup copies cannot be immediately modified, record the approved expiry path, access restrictions, hold interactions, and restore controls; seek authority approval where needed.
8. Run quarterly or risk-based restore, hold-enforcement, deletion-propagation, and schedule-review checks. Each check has an owner, measurable criteria, evidence, and remediation tracking.

**Decision:** no irreversible deletion of the conflicted record/field is enabled until the appropriate authorities resolve the conflict. Non-conflicted records may follow approved rules only when scope, hold status, and copy inventory are reliable. The tiering decision is made from access patterns and total cost, not storage price alone.

### Scenario B — Storage price is low, retrieval economics are not

A research team keeps 60 TB of historical data in an archive tier. The storage invoice is low, but quarterly analysis unexpectedly reads 18 TB in a month and incurs retrieval and restore costs. Analysts also wait longer than the workload can tolerate.

**Reasoning:** recalculate monthly total cost using actual retrieval volume and request counts; compare it with a warm tier or a hybrid design that keeps a small frequently queried index/summary warm. Do not automatically move all data hot. Evaluate whether the workload can use precomputed aggregates, selective restore, caching, or partition-level retrieval. Measure end-to-end latency and include the cost of operating the hybrid solution. Revisit the tier when access patterns change.

### Scenario C — Deletion succeeds in the primary store but data returns after recovery

A customer record is deleted from the primary database. A delayed replica and a backup restore later reintroduce it; the feature store still contains a derived row.

**Reasoning:** this is a lifecycle consistency failure across copies, not merely a failed SQL delete. Use durable disposition records/tombstones, consumer retries and deduplication, reconciliation against the disposition registry, explicit snapshot/backup rules, and restore-time reapplication. Verify derived-store lineage and either delete, transform, or rebuild derived data according to approved policy. Define a completion signal based on verified scope, not the primary database response.

### Scenario D — Hold arrives during a scheduled expiry run

An expiry job has created a deletion candidate list; an authorised hold then arrives for several records before the job executes.

**Reasoning:** the executor must re-check the current authoritative hold state at the point of irreversible action. If hold state is unavailable or cannot be proven fresh enough, fail closed. Hold creation must be durable and auditable; in-flight work must be cancelled or blocked for matching scope. Test concurrency and retry paths. A hold release should trigger re-evaluation, not unconditional deletion.

## 9. Expected outputs and deliverables

Produce these artifacts for a real or fictional system. They are expected outputs of the learning module, not separate files required for this lesson:

1. **Lifecycle state model:** states, transitions, clock-start event, legal-hold interrupt, exception states, and transition owners.
2. **Retention schedule:** every data class and field-level exception mapped to purpose, minimum/maximum, source, owner, status, review date, hold rule, tier, disposition, copy scope, and evidence.
3. **Tier decision matrix:** access frequency, latency/availability objectives, storage and retrieval prices, request/transition/restore charges, operational effort, and reason for selected tier.
4. **Cost worksheet:** explicit units, assumptions, monthly total cost, one-time migration cost, break-even retrieval volume, sensitivity analysis, and pricing source/date.
5. **Copy/lineage inventory:** primary stores, replicas, snapshots, backups, derived stores, indexes, exports, downstream consumers, and known gaps.
6. **Disposition runbook:** request validation, policy/hold checks, execution, retries, reconciliation, verification, exceptions, evidence, and closure conditions.
7. **Archive retrieval runbook:** authorisation, catalog lookup, schema/format recovery, key dependencies, integrity and semantic validation, retrieval timing/cost, and temporary-copy cleanup.
8. **Verification plan:** restore/readability, deletion propagation, hold enforcement, backup expiry, schedule review, cost monitoring, owners, cadence, success criteria, and remediation path.
9. **Architecture Decision Record:** selected lifecycle design, rejected alternatives, assumptions, risks, unresolved legal/privacy questions, dependencies on Topics 3–6, rollout, rollback, and revisit triggers.
10. **Practice answers:** worked arithmetic, scenarios, and explicit statements of what cannot be concluded until an authoritative source is confirmed.

### Minimum acceptance criteria for the deliverables

- Every retention rule has a source, owner, scope, status, and review date—or is explicitly marked unresolved and blocked.
- Minimum retention, maximum retention, legal hold, backup expiry, and deletion verification are separate concepts in both documentation and implementation.
- No automatic disposition occurs when hold status is unknown, the scope is ambiguous, or a required conflict is unresolved.
- Tier choice is justified by access pattern and all-in economics, not storage price alone.
- Archive restore tests prove semantic readability, not just file retrieval.
- Deletion coverage includes known replicas, snapshots, derived data, exports, downstream consumers, and backup limitations.
- Every failed or delayed copy action has an owner, status, next action, and deadline.
- The cost model is reproducible from stated units and assumptions.

## 10. Common mistakes and misconceptions

1. **“Cheapest storage is always best.”** Retrieval, restore, request, transition, latency, and staff costs may reverse the apparent savings.
2. **“Archive and backup mean the same thing.”** Backup is primarily for recovery; archive is for governed historical preservation and retrieval. Separate objectives and evidence.
3. **“If data is deleted from the primary database, it is gone.”** Replicas, snapshots, backups, derived tables, indexes, exports, and downstream consumers may retain it.
4. **“A legal hold just pauses the main database TTL.”** Holds need authoritative scope and must cover the appropriate copies and destructive workflows, including retries and restores.
5. **“A retention schedule can use one duration for every field in a dataset.”** Purpose, sensitivity, and maximum-retention requirements may differ at field level; split policy scope where needed.
6. **“The oldest timestamp is always the correct retention clock.”** The start event must be defined by the approved requirement; creation, settlement, case closure, or relationship end can mean different things.
7. **“A successful archive upload proves long-term recoverability.”** Metadata, schema, key access, format, semantics, catalog, and restore instructions can become unusable over time.
8. **“An unresolved conflict can be handled by retaining everything.”** Indefinite retention can also be unsafe. Record the conflict, restrict access if authorised, and obtain a decision from the accountable authority.
9. **“A deletion request must be completed instantly in every copy.”** Immutable backups, offline media, asynchronous systems, or authorised holds can constrain immediate physical deletion. Use an auditable workflow and do not misrepresent completion.
10. **“A job succeeded, so deletion is verified.”** A job status does not prove every system was in scope or every copy was removed. Reconcile inventory and collect per-system evidence.
11. **“A tombstone is harmless forever.”** Tombstones and audit metadata have their own retention, privacy, and security implications. Define minimal content, access, and duration.
12. **“Tier labels are identical across providers.”** Validate actual latency, restore behavior, minimum-duration charges, request pricing, and availability semantics for the selected service.
13. **“Backup expiry is the same as record retention.”** Backup rotation and record retention serve different purposes and may interact with holds. Document the relationship explicitly.
14. **“Deletion means anonymisation by default.”** Anonymisation, masking, tokenisation, or aggregation must be assessed against the approved purpose, re-identification risk, source requirements, and downstream copies; it is not a universal substitute for deletion.
15. **“Retention policy is a one-time configuration.”** Business purposes, data lineage, schema, legal interpretations, access patterns, and costs change. Review and test the policy over time.

## 11. Mastery criteria

You have mastered this topic when you can demonstrate all of the following without relying on unstated assumptions:

- Explain lifecycle states and why a hold interrupts normal disposition.
- Distinguish each retention driver and show the source, owner, scope, status, and review date for a rule.
- Explain minimum retention, maximum retention, hold, backup expiry, and deletion verification without conflating them.
- Compare hot/warm/cold options using actual workload access patterns, retrieval latency, all-in cost, and operational constraints.
- Explain why a backup is not automatically an archive and why an archive is not automatically a backup.
- Complete a schedule with field-level exceptions and a safe state for unresolved requirements.
- Reproduce the worked example's arithmetic and calculate a break-even point with correct units.
- Identify which costs are omitted from a simplified model and explain how to add them without double-counting.
- Trace a disposition request across primary stores, replicas, snapshots, backups, derived data, exports, and downstream consumers.
- Design hold-aware, retry-safe lifecycle automation that fails closed when required policy/hold information is unavailable.
- Explain how schema evolution, format changes, keys, and metadata affect long-term readability.
- Define restore, deletion, hold, and policy verification with owners, evidence, cadence, success criteria, and remediation.
- Identify dependencies on Topics 3–6 and update the architecture when retention or access patterns change.
- Explicitly state when a decision requires legal, privacy, compliance, records, or contract-owner confirmation instead of guessing a period.

## 12. Completion gate

Do not mark Topic 7 complete until the following checklist is satisfied:

- [ ] I can draw the lifecycle and show legal hold as a constraint that blocks normal disposition for its authorised scope.
- [ ] I have classified representative datasets and recorded purpose, source, owner, and unresolved requirements.
- [ ] I have a retention schedule with minimum and maximum retention separated, explicit clock-start events, hold rules, tier, disposition method, and verification evidence.
- [ ] I have documented that legal/regulatory durations require source confirmation and have not invented a universal or jurisdiction-specific period.
- [ ] I can explain backup versus archive and show their distinct owners, purposes, expiry/retention rules, and tests.
- [ ] I have compared tiers by access frequency, latency, storage, retrieval, requests, transition, restore, and operational costs.
- [ ] I have independently checked the worked cost arithmetic and can reproduce the break-even retrieval volume with units.
- [ ] I have a copy/lineage inventory and a disposition workflow covering replicas, snapshots, backups, derived stores, exports, and downstream consumers.
- [ ] I have tested hold enforcement, including a hold arriving during a scheduled deletion run and the fail-closed behavior when hold status is unknown.
- [ ] I have documented immutable-backup limitations, expiry behavior, and restore-time controls against reintroducing deleted data.
- [ ] I have an archive retrieval test that checks schema, semantics, integrity, keys, latency, and cost—not only object existence.
- [ ] I have owners, cadence, evidence, success criteria, and remediation for restore/deletion verification; quarterly checks or an approved risk-based equivalent are defined where appropriate.
- [ ] I have completed the exercises and written an ADR with assumptions, rejected alternatives, unresolved questions, and revisit triggers.
- [ ] I have revisited Topics 3–6 to ensure format/table history, layout, replication, and transaction/integration behavior support the lifecycle policy.

**Completion standard:** the design is ready for review when its rules are sourced and owned, its unresolved conflicts are visible and blocked from unsafe automation, its economics are reproducible, its copy scope is explicit, and its retrieval/deletion/hold controls have testable evidence. Completion of this lesson is not a substitute for legal, privacy, records, security, or compliance approval of a production retention policy.
