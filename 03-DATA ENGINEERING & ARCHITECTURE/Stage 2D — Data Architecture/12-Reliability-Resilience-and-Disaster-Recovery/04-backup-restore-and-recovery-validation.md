# Backup, Restore and Recovery Validation

> **Module:** Stage 2D — Data Architecture, Module 12: Reliability, Resilience and Disaster Recovery  
> **Topic:** 04 — Backup, restore and recovery validation  
> **Audience:** Beginner through advanced data architect, data engineer, platform engineer and data reliability practitioner  
> **Estimated study effort:** 6–8 hours as a planning estimate, not a requirement  
> **Scope note:** This is a vendor-neutral design-and-documentation lesson. The module roadmap states that topic files were empty when the roadmap was authored; therefore the examples, scenarios, thresholds and acceptance targets below are illustrative recommendations, not pre-existing repository requirements. No production restore or outage is required.

## Contents

- [1. Position in the roadmap](#1-position-in-the-roadmap)
- [2. Learning outcomes](#2-learning-outcomes)
- [3. Foundational terminology](#3-foundational-terminology)
- [4. Backup methods and recovery granularity](#4-backup-methods-and-recovery-granularity)
- [5. Recovery objectives: interval, data-loss exposure and restore time](#5-recovery-objectives-interval-data-loss-exposure-and-restore-time)
- [6. Define backup scope: protect the system needed to recover](#6-define-backup-scope-protect-the-system-needed-to-recover)
- [7. Backup frequency, retention, location and integrity](#7-backup-frequency-retention-location-and-integrity)
- [8. Database and lakehouse consistency](#8-database-and-lakehouse-consistency)
- [9. Ordered restoration and dependency graph](#9-ordered-restoration-and-dependency-graph)
- [10. Original environment versus clean environment](#10-original-environment-versus-clean-environment)
- [11. Recovery validation: technical and business layers](#11-recovery-validation-technical-and-business-layers)
- [12. Automated restore testing and evidence](#12-automated-restore-testing-and-evidence)
- [13. Complete example: backup-and-restore runbook for a fictional lakehouse](#13-complete-example-backup-and-restore-runbook-for-a-fictional-lakehouse)
- [14. Scenario: inconsistent recovery points across systems](#14-scenario-inconsistent-recovery-points-across-systems)
- [15. Advanced scenario: malicious deletion or corrupted data](#15-advanced-scenario-malicious-deletion-or-corrupted-data)
- [16. Retention, deletion, residency and encryption keys](#16-retention-deletion-residency-and-encryption-keys)
- [17. Failure modes and corrective actions](#17-failure-modes-and-corrective-actions)
- [18. Exercises and expected deliverables](#18-exercises-and-expected-deliverables)
- [19. Example recovery-focused ADR](#19-example-recovery-focused-adr)
- [20. Recovery validation checklist](#20-recovery-validation-checklist)
- [21. Common mistakes and misconceptions](#21-common-mistakes-and-misconceptions)
- [22. Glossary](#22-glossary)
- [23. Mastery criteria and completion gate](#23-mastery-criteria-and-completion-gate)
- [24. Further references within the project](#24-further-references-within-the-project)

## 1. Position in the roadmap

This is Topic 04 in `12-Reliability-Resilience-and-Disaster-Recovery/`.

The recommended learning sequence is:

1. `01-reliability-objectives-sli-slo-and-sla.md` — define measurable reliability objectives.
2. `02-failure-domains-and-blast-radius.md` — identify shared dependencies and correlated failures.
3. `03-high-availability-and-redundancy-patterns.md` — understand what redundancy and replication can and cannot protect against.
4. **This lesson** — define backup scope, restoration procedures and evidence that recovery produces usable, consistent data.
5. `05-rpo-rto-and-disaster-recovery-strategies.md` — select recovery objectives and an overall DR strategy.
6. `06-replay-reprocessing-and-backfill-architecture.md` — make restored data current without introducing duplicates or inconsistency.
7. `07-incident-response-runbooks-and-postmortems.md` — operationalise recovery and record lessons.
8. `08-business-continuity-and-resilience-testing.md` — rehearse and improve the end-to-end response.

### Prerequisites and cross-module dependencies

| Dependency | Why it matters here |
|---|---|
| Database replication, consistency and transaction boundaries | A restore point must represent a valid database state; logs and transactions may be needed for point-in-time recovery. |
| Retention, archival and data lifecycle | Backup retention must respect recovery needs, legal holds, deletion obligations and storage-tier retrieval times. |
| Idempotency, deduplication, reconciliation and integration failure handling | Restored pipelines may replay events; recovery must not double-count or silently omit data. |
| Platform control-plane/data-plane separation | Recovery may need identity, networking, catalogues and orchestration before data consumers can run. |
| Security, classification, keys and access control | A backup is unusable if encryption keys are lost, or dangerous if a compromised identity can delete every copy. |
| Topic 03 high availability | Replicas support availability, but can propagate logical corruption and malicious deletion. |
| Topics 05–08 | This lesson creates the technical foundation for RPO/RTO strategy, replay, incident response and testing. |

**Core principle:** a backup is a retained recovery input; **recoverability is a demonstrated capability** to restore the required data and service to a usable, consistent state within the required time.

## 2. Learning outcomes

After this lesson, you should be able to:

- Distinguish backup, replica, snapshot, archive, object versioning and point-in-time recovery.
- Choose full, incremental or differential methods where the technology supports them.
- Translate data-loss tolerance and service-restoration requirements into backup and validation design.
- Inventory data, metadata, configuration and security dependencies required to rebuild a platform.
- Design isolated, access-controlled and tamper-resistant backup storage.
- Restore databases and lakehouse tables without mixing incompatible metadata and data states.
- Estimate restore time using volume, effective throughput, rebuild work and validation time.
- Validate recovery at both technical and business levels.
- Explain how retention, deletion, encryption-key recovery and legal holds interact.
- Produce a runbook, measurable checklist, evidence record and recovery-focused architecture decision record (ADR).

## 3. Foundational terminology

| Term | Meaning | Important limitation |
|---|---|---|
| **Backup** | A retained copy or set of recovery artifacts intended to reconstruct data or a system after loss or damage. | Existence does not prove completeness, readability or recoverability. |
| **Restore** | The act of copying or reconstructing data/configuration from backup artifacts into a target environment. | Restore can finish while the recovered data is inconsistent or unusable. |
| **Recovery** | The wider process of restoring data, dependencies, service behaviour and business operations to an acceptable state. | Includes orchestration, security, validation, catch-up and consumer readiness. |
| **Recoverability** | Demonstrated ability to recover a defined scope to an acceptable state under defined conditions. | Must be supported by repeatable tests and evidence. |
| **Replica** | A second, usually continuously or frequently updated copy used for availability, scale or geographic resilience. | Deletion, corruption and hostile changes can replicate. |
| **Snapshot** | A point-in-time representation of a volume, database, filesystem, object set or table state. | May depend on the same control plane/storage system; may be crash-consistent rather than application-consistent. |
| **Archive** | Data retained for long-term preservation, often at lower cost and slower retrieval. | Retrieval, rehydration and validation may dominate recovery time. |
| **Versioning** | Retention of prior object or record versions after changes. | Version history may be deleted by privileged identities or expire under lifecycle rules. |
| **Point-in-time recovery (PITR)** | Reconstruction to a chosen time using a base backup plus logs, change records or equivalent history. | Requires a complete, compatible chain and an accurate target time; it cannot recover changes that were never captured. |
| **Consistency point** | A known time or transaction boundary at which related state can be interpreted coherently. | Independently timed copies can each be valid yet disagree with one another. |
| **Recovery point objective (RPO)** | Maximum tolerable amount of data loss, expressed as time between the recovery state and the failure/required point. | It is not automatically equal to the backup interval; log shipping, lag and capture gaps matter. |
| **Recovery time objective (RTO)** | Maximum tolerable elapsed time to restore the defined service/data scope to the required level. | Define when the clock starts and what “restored” means; copying bytes alone may not qualify. |
| **Recovery validation** | Checks that recovered data is technically sound and fit for the intended business use. | A checksum alone cannot establish business correctness. |

### Backup, replica, snapshot, archive and versioning comparison

| Mechanism | Primary purpose | Typical strength | Typical limitation / failure mode | Good fit |
|---|---|---|---|---|
| Replica | Availability and read scaling | Fast switch to another copy after certain node/zone failures | Logical deletion, corruption or bad writes propagate; replica lag can lose recent writes | Service continuity for infrastructure failures |
| Snapshot | Fast point-in-time capture/rollback | Efficient capture through copy-on-write or metadata references | Shared failure domain, dependency on source platform, incomplete application consistency | Rapid rollback or short-term recovery where separately protected |
| Backup | Recover after loss, corruption or deletion | Can preserve older known-good state in a separate security/failure domain | Missing scope, expired chain, inaccessible keys, untested restore | Disaster recovery, accidental deletion and corruption recovery |
| Archive | Long-term preservation | Cost-effective retention and compliance evidence | Slow retrieval, special tooling, stale formats or unavailable dependencies | Historical retention and infrequent access |
| Object versioning | Undo some object overwrites/deletions | Granular previous versions and audit trail | Version purge, lifecycle expiry or account compromise may remove versions | Recovery from accidental object changes |
| PITR/log backup | Recover to a selected point within retained history | Fine-grained recovery between base backups | Log gaps, wrong target time, incompatible base/log sequence | Databases and systems with transaction/change logs |

These mechanisms can complement one another. A snapshot may be the capture mechanism for a backup, but it should not be called an independent backup unless its protection, retention, access and failure domains meet the design requirement.

## 4. Backup methods and recovery granularity

### 4.1 Full backup

A **full backup** captures the defined protected scope at a point or over a controlled capture window.

- **Purpose:** provide a base from which to restore.
- **Mechanism:** copy all in-scope data or create a complete logical/physical backup.
- **Strengths:** simpler dependency chain; straightforward inventory and recovery reasoning.
- **Trade-offs:** can consume more time, network, storage and compute.
- **Use when:** scope is modest, restore simplicity is important, or the technology’s native backup method is full-oriented.
- **Limitations:** “full” means full only for the declared scope; it does not automatically include logs, catalogues, permissions, external dependencies or a consistent cross-system point.

### 4.2 Incremental backup

An **incremental backup** captures changes since the most recent relevant backup (commonly the last full or incremental, depending on the product).

- **Purpose:** reduce each backup window and transferred volume.
- **Restore path:** usually the base full plus each required incremental in the correct order; exact rules are technology-specific.
- **Strengths:** lower per-run data movement when change rates are modest.
- **Trade-offs:** longer restore chain, more metadata and greater sensitivity to a missing/corrupt segment.
- **Use when:** data changes gradually and backup windows or transfer costs are constrained.
- **Control:** verify chain completeness and test restoration from the actual retained chain, not merely the latest incremental file.

### 4.3 Differential backup

A **differential backup** captures changes since the most recent full backup.

- **Restore path:** base full plus the latest required differential, under the method’s supported semantics.
- **Strengths:** usually fewer restore steps than a long incremental chain.
- **Trade-offs:** differential size tends to grow until the next full backup.
- **Use when:** a compromise between daily backup volume and restore-chain complexity is appropriate.
- **Caution:** vendor terminology and implementations vary; confirm the exact recovery sequence for the selected system.

### 4.4 Logs and point-in-time recovery

For systems that support transaction logs or change logs, a recovery sequence may be:

1. Restore a compatible base backup.
2. Apply required incrementals or logs in order.
3. Stop at a verified target timestamp, transaction ID or log sequence.
4. Recover/roll forward transactions according to the engine’s documented semantics.
5. Validate that the target point is coherent and corresponds to the intended business boundary.

A PITR chain can fail because of missing log segments, expired retention, an incompatible base backup, clock ambiguity, log corruption, or a mistaken target timestamp. If the target is “just before the erroneous deletion,” identify the deletion’s transaction/time precisely and ensure the chosen target does not include it.

### 4.5 Snapshots and application consistency

A storage-level snapshot may be:

- **Crash-consistent:** resembles storage after an abrupt stop; the application may need journal/log recovery.
- **Filesystem-consistent:** filesystem structures are coordinated, but application-level transactions may not be.
- **Application-consistent:** the application/database has coordinated quiescing, checkpointing or backup APIs so the captured state respects its consistency guarantees.

Never assume a multi-volume or multi-service snapshot is atomic unless the platform explicitly guarantees it. A lakehouse table’s data files and transaction metadata must be captured as a compatible set.

## 5. Recovery objectives: interval, data-loss exposure and restore time

Backup design is not “run a job every night.” It is a fit between business tolerance, change capture, retention, restoration and proof.

### 5.1 Data-loss exposure from a backup interval

If only periodic full backups are available, and the most recent successful backup is \(I\) hours before a failure, the loss exposure at that failure can approach \(I\) hours. If failures are equally likely at any point between successful backups and the backup schedule has no gaps, the simple idealized average exposure is \(I/2\). These are planning approximations, not guarantees.

Real exposure also depends on:

- backup job failures or delays;
- data generated but not committed at capture time;
- transaction-log/change-log capture and shipping lag;
- replication lag, if replication is part of the recovery chain;
- consistency boundaries across multiple systems;
- whether corruption occurred before the backup and was not detected;
- whether the retained point is readable and restorable.

**Worked example — illustrative assumptions**

- A dataset is backed up every 6 hours.
- Every scheduled backup succeeds and is consistent.
- No transaction-log backup, continuous change capture or other recovery mechanism is available.
- A failure occurs at an arbitrary time between successful backups.

Then:

- **Maximum idealized loss exposure:** approaches 6 hours (just before the next successful backup).
- **Simple average exposure:** \(6/2 = 3\) hours.
- **Interpretation:** this design cannot support a 30-minute RPO by itself. It would need more frequent successful backups or a finer-grained mechanism, such as log/change capture, with its own lag and retention controls.

Do not report “RPO = backup interval” as a universal law. RPO is a requirement; achieved recovery-point age is an observed result. The design should demonstrate that the worst credible capture gap stays within the objective.

### 5.2 RTO is end-to-end, not transfer time

A realistic recovery-time budget can be expressed as:

\[
T_{\text{recovery}} =
T_{\text{detect/decide}} +
T_{\text{provision}} +
T_{\text{restore}} +
T_{\text{rebuild}} +
T_{\text{validate}} +
T_{\text{catch-up}} +
T_{\text{release}}
\]

Some activities can overlap, so a critical-path model is more accurate than simply summing every parallel task. For a conservative paper estimate, sum sequential stages and explicitly state which stages overlap. Compare the estimate with the RTO and include uncertainty/headroom.

### 5.3 Worked restore-time estimate

**Illustrative scenario:** restore 12 TiB of backup data to a clean environment.

Assumptions:

- Effective sustained end-to-end transfer throughput: **300 MiB/s**.
- For the estimate, \(1\text{ TiB}=1{,}048{,}576\text{ MiB}\).
- The 300 MiB/s figure is assumed to be measured after network/protocol overhead, throttling and ordinary transfer inefficiency; do not subtract those costs a second time.
- Data must be transferred once; compression/decompression and small-file metadata effects are represented only if already reflected in the effective throughput.
- Parallel stages are not assumed in the sequential estimate below.

Calculation:

- Data volume = \(12 \times 1{,}048{,}576 = 12{,}582{,}912\text{ MiB}\).
- Transfer seconds = \(12{,}582{,}912 / 300 = 41{,}943.04\text{ s}\).
- Transfer hours = \(41{,}943.04 / 3{,}600 \approx 11.65\text{ hours}\).

Add illustrative stage estimates:

| Stage | Estimated duration | Assumption |
|---|---:|---|
| Provision clean environment and access | 1.0 h | Infrastructure and identities are scripted and available |
| Transfer 12 TiB | 11.65 h | Sustained 300 MiB/s effective throughput |
| Rebuild table/catalogue metadata and indexes | 2.0 h | Work beyond the bulk transfer; no large unexpected rebuild |
| Technical and business validation | 2.0 h | Parallel checks fit within a two-hour validation window |
| Controlled catch-up/replay | 1.5 h | Replay volume is bounded and idempotent |
| Consumer smoke tests and release | 0.5 h | Limited consumer set and explicit approval |
| **Sequential planning total** | **18.65 h** | Sum of listed stages; assumes no overlap |

This estimate is not a benchmark or an RTO recommendation. If the objective were 12 hours, this design would not meet it under the stated assumptions. Possible design changes include higher verified effective throughput, staged/parallel restores, smaller recovery scope, pre-provisioned infrastructure, alternate capture formats, or a different recovery strategy. Validate improvements with measured tests; do not divide by a marketing peak bandwidth number.

**What the transfer estimate excludes unless explicitly included in measured throughput:** source read limits, decompression, encryption/decryption, request overhead, API throttles, small-file listing, retries, metadata commits, log replay, index rebuilds, access-policy repair, data-quality validation, consumer warm-up and release approvals.

## 6. Define backup scope: protect the system needed to recover

A platform can have intact data files but still be unrecoverable because its catalogue, schemas, encryption keys, pipeline code or permissions are missing. Create an inventory with an owner, recovery method, consistency requirement, retention, location, test and acceptance criteria for every critical component.

### 6.1 Representative lakehouse/data-platform backup inventory

| Component | What to protect | Capture/consistency considerations | Recovery validation |
|---|---|---|---|
| Source databases | Base backups, transaction logs, required configuration and database identities | Application-consistent backup; preserve log chain and target-time semantics | Database recovery checks, row/transaction counts, constraints |
| Object-store data | Data objects, object versions where required, manifests and relevant metadata | Preserve object identity, version IDs, encryption metadata and lifecycle behaviour | Object inventory, checksum sampling/full checksums where feasible |
| Lakehouse table data | Data files, manifests, transaction logs, snapshots and table-format metadata | Coordinate data and transaction-log retention; avoid restoring metadata that points to absent files | Table opens, snapshot/manifest checks, schema and row-level validation |
| Warehouse/marts | Table data, DDL, views, stored procedures, grants, workload settings | Capture dependencies and compatible engine/version details | Control totals, query results and access tests |
| Schemas/contracts | DDL, schema registry subjects/versions, event contracts and compatibility settings | Keep schema versions aligned with restored data and replay position | Schema compatibility and representative deserialization |
| Catalogue/metastore | Databases, tables, partitions, locations, classifications, ownership and properties | Catalogue references must match restored paths and table state | Resolve tables, compare object locations and metadata counts |
| Lineage and governance | Lineage metadata, classifications, ownership, policy definitions and audit evidence as required | Some lineage can be regenerated; preserve history that cannot be reconstructed | Critical lineage paths and policy enforcement checks |
| Pipeline definitions | Source code, deployment manifests, transformation logic, dependency lockfiles | Prefer version-controlled, immutable releases and reproducible builds | Build/test pipeline from restored source |
| Orchestration/control state | DAG/workflow definitions, schedules, offsets/checkpoints, task state where required | Decide whether state should be restored or safely reconstructed | Controlled resume, no duplicate or skipped processing |
| Configuration and IaC | Network, storage, compute, policies, service configuration and infrastructure code | Store versioned configuration outside the primary failure domain | Plan/diff review and environment conformance |
| Identity and access | Role/policy definitions, service identities, federation settings, emergency access procedure | Do not restore compromised credentials blindly; recreate/rotate secrets | Least-privilege access tests and audit trail |
| Secrets and encryption keys | Key IDs, key policy/rotation metadata, protected recovery material and escrow procedure where permitted | Secret material must be separately protected and tightly controlled; key loss can make backups unreadable | Authorized decrypt/unwrap test in isolated environment |
| Network/DNS/certificates | Private endpoints, routes, DNS records, certificate renewal/recovery process | Recovery may need alternate paths and valid trust roots | Connectivity and certificate checks |
| Monitoring/audit | Alert rules, dashboards, audit logs and recovery-job telemetry | Preserve incident and access evidence separately from compromised production | Alert delivery, audit query and evidence completeness |
| Consumers/contracts | API definitions, BI semantic models, downstream schedules and service configuration | Release only after dependencies and data contracts are validated | Representative consumer and downstream smoke tests |

A practical inventory should also identify data classification, residency, legal hold, deletion status, data owner, retention class, backup frequency, last known successful backup, recovery-point age, restore method, encryption dependency, isolation boundary and evidence location.

### 6.2 Do not treat every state item identically

Classify each component as one of:

1. **Must restore exactly:** regulated records, transaction history, critical curated data, audit evidence.
2. **Must reconstruct deterministically:** ephemeral compute, derived indexes, caches or temporary artifacts that can be rebuilt within the recovery budget.
3. **Must reconcile/replay:** event offsets, pipeline checkpoints, CDC positions and derived datasets that need catch-up.
4. **Must deliberately recreate or rotate:** credentials, tokens, certificates and potentially compromised identities.
5. **Must preserve under policy:** records under retention obligations, legal holds, or deletion restrictions.
6. **Must not resurrect:** data that has a valid, applicable deletion requirement, subject to legal hold and jurisdictional policy review.

This classification prevents blindly restoring every old configuration and every historical secret into a clean environment.

## 7. Backup frequency, retention, location and integrity

### 7.1 Frequency

Choose capture frequency from the tolerated loss window and demonstrated capture behaviour. More frequent backups may reduce potential loss but increase compute, transfer, storage and operational overhead. Logs or continuous change capture can reduce recovery-point age between full backups, but only if their chain is complete, monitored and retained long enough.

Track at least:

- scheduled versus successful backup runs;
- oldest and newest recoverable point;
- lag between source commit and protected copy;
- failed/missed jobs and time to repair;
- age of last successfully restore-tested backup;
- recovery-point age achieved in a test.

### 7.2 Retention

Retention should reflect business recovery windows, investigation latency, legal obligations, storage cost and the time required to detect silent corruption. A corruption discovered 45 days later cannot be recovered from a 30-day-only history unless another valid source exists.

Document retention by data class and copy type. Include full-backup dependency chains, logs, object versions, snapshots, manifests and catalogue history. Deleting a base backup while dependent incrementals are retained can leave an unusable chain.

### 7.3 Location and failure-domain separation

At least one recovery copy should be protected from the failure domains most likely to affect production. Consider separate accounts/projects/subscriptions, credentials, administrative domains, regions, networks and storage systems according to threat model and recovery needs.

A different region is not sufficient if the same compromised administrator can delete both regions. A separate account is not sufficient if production identities have write/delete permissions to the backup account. Separation must be enforced through identity and policy, not merely naming.

### 7.4 Immutable and offline protection

- **Immutable/WORM retention:** prevents modification/deletion during a defined retention window, subject to the storage system’s actual controls and administrative model.
- **Offline/air-gapped copy:** reduces direct attack paths, but can increase retrieval time and operational complexity.
- **Separate backup administration:** limits the ability of production credentials to destroy recovery copies.
- **MFA and privileged access controls:** protect administrative operations; use just-in-time access and approvals where practical.
- **Independent audit logs:** retain evidence of policy changes, deletes and restore activity outside the compromised administrative boundary.

Immutability does not guarantee correctness: a corrupted or maliciously altered dataset can be captured immutably. Preserve multiple recovery points, detect anomalies, and define how to select a known-good point. Verify retention locks and recovery access without weakening production protections.

### 7.5 Integrity of backup artifacts

Integrity controls may include checksums, signed manifests, object inventories, backup-tool verification, encryption/authentication checks, chain validation and restore tests. A successful upload or “job succeeded” status is only one signal. A checksum proves that bytes match the expected digest, not that the data is semantically correct or was clean when captured.

## 8. Database and lakehouse consistency

### 8.1 Databases

A database restore may require:

- a compatible base backup;
- ordered transaction logs or WAL/binlogs;
- engine version and configuration compatibility;
- encryption keys and credentials;
- correct recovery target timestamp or log sequence;
- application-aware backup coordination;
- handling of in-doubt transactions and replicas;
- validation of constraints, indexes, sequences and extensions.

If a backup is crash-consistent, the engine may need to replay logs or recover journals. The database reaching “ready” is not the same as application validation passing.

### 8.2 Lakehouse table formats

A lakehouse table often consists of data files plus transaction/manifest metadata. The metadata determines which files are part of a committed table snapshot. Restoring only data files can leave orphaned files or omit committed state; restoring only metadata can leave references to missing files.

Protect and restore a compatible set of:

- data files and required delete files;
- transaction logs, manifests, metadata JSON or equivalent table metadata;
- schema and partition/spec history where applicable;
- catalogue/metastore entries or a reproducible catalogue source;
- encryption/key metadata and object access policies;
- external dependencies and table-format/runtime compatibility information.

Use table-format-supported backup/export/restore procedures when available. Avoid ad hoc copying while writes continue unless the storage and table format guarantee a consistent capture. Record the chosen snapshot/commit IDs and object inventory as evidence.

### 8.3 Cross-system recovery points

A pipeline may depend on a source database, event log, lakehouse, catalogue, orchestration checkpoint and semantic model. Restoring each system to its latest individually available point can create a state that never existed as one coherent system.

Establish a recovery manifest that maps each component to a target time, transaction ID, offset, commit ID or version. Where atomic global snapshots are unavailable, document the consistency protocol: stop writers/consumers, capture boundaries, preserve offsets and watermarks, restore to compatible points, then reconcile or replay in a controlled way.

## 9. Ordered restoration and dependency graph

A common dependency order is:

1. **Incident authority and clean recovery identity** — establish incident ownership, approved target, emergency access and trusted credentials.
2. **Key and secret recovery** — recover required key material through the approved procedure; rotate/revoke credentials suspected compromised.
3. **Network and trust foundations** — routes, DNS, certificates, private endpoints and access to the recovery location.
4. **Infrastructure and policy** — provision from reviewed IaC; apply storage policies, encryption, logging and network controls.
5. **Identity and authorization** — recreate roles and service identities with least privilege; validate access before loading sensitive data.
6. **Storage and raw data** — restore base data, versions and required logs; preserve manifest/checksum evidence.
7. **Database engines and transaction recovery** — restore compatible base backups, apply logs and select the target point.
8. **Catalogue, metastore and table metadata** — restore or rebuild metadata only when its referenced data state is available and compatible.
9. **Schemas, contracts and governance metadata** — restore versions, classifications, policies and ownership.
10. **Pipeline code and orchestration definitions** — deploy a pinned, reviewed version; do not automatically resume old checkpoints until reconciled.
11. **Checkpoint/offset reconciliation and replay** — determine last committed work, deduplicate, replay or backfill where needed.
12. **Technical validation** — verify integrity, schema, constraints, referential integrity, counts and consistency.
13. **Business validation** — reconcile control totals, key reports, critical lineage paths and downstream outputs.
14. **Consumer release** — release read/write access and schedules only after explicit readiness approval.
15. **Monitoring and evidence closure** — confirm alerting, record actual recovery times and point age, and capture gaps/actions.

The exact order depends on architecture. For example, a catalogue may be needed to locate data, so a minimal catalogue bootstrap can precede data restore; the authoritative table metadata should still be reconciled with the restored data snapshot before consumers are enabled. Key recovery may require a separate security team and cannot be assumed instantaneous.

## 10. Original environment versus clean environment

| Approach | Benefits | Risks / trade-offs | Use when |
|---|---|---|---|
| Restore in place | May preserve endpoints and reduce reconfiguration | Can overwrite evidence, reintroduce compromise, or depend on damaged control plane | Incident is understood, environment is trusted and in-place restoration is supported |
| Restore to isolated clean environment | Limits contamination and supports validation before release | Needs capacity, network/identity setup, DNS cutover and more coordination | Ransomware, credential compromise, suspected malicious deletion or uncertain integrity |
| Restore to alternate region/account | Survives selected regional/account failure domains | Cross-region throughput, residency, key and network dependencies can slow recovery | Regional failure or isolation objective requires independent location |
| Rebuild from code + restore data | Reproducibility, cleaner configuration, reduced drift | IaC may be stale; versions, provider APIs and dependencies can change | Platform is code-managed and rebuild steps have been tested |
| Restore only a bounded dataset | Smaller blast radius and faster recovery | Downstream consistency and shared metadata may be missed | Isolated table/domain failure with known lineage and limited dependencies |

In suspected compromise, preserve forensic evidence and do not reconnect the clean environment to compromised credentials or untrusted automation until the incident team approves. A clean restore is not simply a copy into a new account: trust roots, access policies, secrets, software artifacts and data cleanliness must be assessed.

## 11. Recovery validation: technical and business layers

### 11.1 Technical validation

Use controls appropriate to the data and engine:

- **Artifact integrity:** checksum/hash or signed manifest comparison; report missing, extra and mismatched objects.
- **Completeness:** expected object/file counts, byte counts, partitions, date ranges and backup-chain coverage.
- **Schema:** column names/types/nullability, schema version, partition specification and compatibility.
- **Database consistency:** engine recovery status, constraints, indexes, sequences and transaction/log position.
- **Lakehouse consistency:** table opens, manifest/log validity, referenced files exist, commit/snapshot is the expected one.
- **Record counts:** compare with a trusted source or known baseline; counts alone are insufficient.
- **Referential integrity:** orphan rows, foreign-key or business-key relationships, dimension references and join coverage.
- **Temporal consistency:** watermarks, event-time bounds, transaction boundaries and CDC offsets.
- **Access/security:** only approved roles can read/write; encryption is active; audit events are emitted.
- **Repeatability:** validation output records exact backup ID, restore target, code version and parameters.

Checksums should be computed over canonical bytes or a well-defined representation. For row-level checks, specify ordering, null handling, collation, decimal precision and canonical serialization; otherwise two semantically identical datasets can produce different hashes or two differently represented datasets can be compared incorrectly.

### 11.2 Business validation

- Reconcile financial, operational or analytical control totals against a trusted independent source.
- Run representative critical reports and compare expected aggregates for the same time boundary.
- Verify data freshness and completeness against source watermarks.
- Exercise high-value downstream consumers, APIs, BI semantic models or feature pipelines.
- Check lineage from critical source entities through transformations to outputs.
- Validate data classification, masking, row/column access and deletion rules.
- Obtain data-owner sign-off for material discrepancies and document exceptions.

A restored dataset may pass byte checks yet contain a logically wrong value captured before the backup. A report may match an expected total while individual rows are missing and others duplicated. Use multiple independent checks and risk-based sampling.

### 11.3 Measurable acceptance criteria

The values below are example test thresholds to be adapted and approved; they are not universal standards.

| Check | Example pass criterion | Failure response |
|---|---|---|
| Backup chain | All required base/incremental/log artifacts present and verified | Stop restore sign-off; locate a valid chain or select another point |
| Object integrity | 100% of critical objects match the trusted manifest/checksum | Quarantine mismatches; investigate source and backup chain |
| Schema | No unexplained schema drift; expected schema version restored | Repair version/configuration or select compatible point |
| Required partitions | All required partitions and date ranges present | Restore missing partitions or document approved scope reduction |
| Referential integrity | Zero unexplained violations in critical relationships | Repair/replay/reconcile; do not release affected consumers |
| Control totals | Difference is zero or within an explicitly approved domain-specific tolerance | Investigate timing, filtering, duplication and source discrepancy |
| Recovery point | Achieved data point is within the approved RPO | Declare objective miss; assess business impact and corrective action |
| End-to-end elapsed time | Defined service is usable within the approved RTO | Record miss; adjust architecture/runbook/capacity |
| Security | No unapproved identities; keys accessible through approved controls; audit logs present | Block release; remediate access and key handling |
| Downstream smoke test | All named critical queries/jobs pass with expected outputs | Keep consumer release blocked for failed critical paths |
| Evidence | Required timestamps, IDs, results, approver and exceptions recorded | Test is incomplete until evidence is supplied |

## 12. Automated restore testing and evidence

Automate safe, repeatable checks where practical, but keep production data protected.

A restore test pipeline may:

1. Select a retained backup and record its ID, creation time, source version and expected recovery point.
2. Provision an isolated test target with bounded access and resource limits.
3. Retrieve keys through the approved workflow; never print secret material into logs.
4. Restore the backup and required logs/metadata.
5. Run integrity and structural checks.
6. Run business control queries and selected downstream smoke tests.
7. Record stage timestamps, durations, achieved recovery-point age, test versions and results.
8. Destroy or sanitize the test environment according to policy and retain approved evidence.
9. Open corrective actions for failures and rerun after remediation.

Automated tests must not overwrite production, weaken immutable retention, expose regulated data, or silently use privileged credentials. Prefer synthetic or masked data when the goal can be met without a production copy. If realistic data is necessary, document approval, access restrictions, encryption, residency and deletion of test copies.

### Example recovery-test evidence record

All details below are fictional and illustrative.

| Field | Example value |
|---|---|
| Test ID | `REC-2026-017` |
| Scope | Critical curated lakehouse tables `orders`, `payments`, `customers` plus catalogue and pipeline definitions |
| Backup set | `lakehouse-full-2026-10-20T00:00Z` + verified change/log chain to selected target |
| Recovery target | `2026-10-20T08:00:00Z` UTC, selected using documented commit/watermark mapping |
| Source environment | `prod-data-platform` (reference only; no production write performed) |
| Restore target | `recovery-test-017` isolated account/project |
| Operator / approver | Named role IDs in the controlled evidence system; do not store credentials here |
| Start / end | `2026-10-21T01:00Z` / `2026-10-21T16:20Z` (illustrative) |
| Measured elapsed time | 15 h 20 min (calculated from the example timestamps) |
| Artifact integrity | PASS — all required critical objects matched expected manifest |
| Schema / table metadata | PASS — expected schema and commit IDs recorded |
| Business reconciliation | PASS — approved control totals matched for the target period |
| Downstream tests | PASS — 8/8 named critical queries completed |
| RPO result | PASS only if the achieved recovery-point age was measured and met the approved objective; do not infer from this table’s target timestamp alone |
| RTO result | PASS only if the approved clock start, usable-service end point and RTO are defined and the measured duration meets it |
| Exceptions | None in this illustrative example |
| Evidence references | Checksums, logs, SQL outputs, object inventory, access audit, screenshots only if policy permits |
| Final decision | Accepted for the exercise; not evidence of a real restore having been executed |

Evidence must distinguish **planned**, **observed**, **calculated** and **approved** values. Do not label an assumed duration as measured. Store evidence in an access-controlled location separate from the environment whose compromise triggered the test.

## 13. Complete example: backup-and-restore runbook for a fictional lakehouse

### 13.1 Scenario and assumptions

Fictional company **Northbridge Retail** runs a lakehouse with:

- object storage for raw and curated data;
- a table format with transaction/manifest metadata;
- a catalogue/metastore;
- an event stream feeding ingestion pipelines;
- orchestration and checkpoints;
- a semantic model powering daily sales and inventory reports.

The objective is to recover a known-good curated state after accidental deletion or corruption. The numeric objectives and checks below are illustrative and must be replaced with business-approved values. No live system is used in this exercise.

### 13.2 Before an incident: backup design

1. **Classify scope.** Mark critical source data, curated tables, transaction metadata, schemas, catalogue definitions, pipeline code, orchestration definitions, checkpoints, IaC, access policies, keys and audit records.
2. **Define recovery points.** Set the required RPO per dataset and decide whether scheduled backups alone suffice or whether log/change capture is needed.
3. **Capture consistent state.** Use table-format-supported snapshots/export or coordinated writes/checkpoints. Record commit IDs, object manifests and source offsets.
4. **Protect history.** Retain base backup and all required incrementals/logs; verify that lifecycle rules cannot remove dependencies prematurely.
5. **Separate the copy.** Write to a separate security/administrative boundary with immutable retention or an offline copy appropriate to the threat model.
6. **Protect access.** Separate backup operator, production administrator and restore approver duties. Require strong authentication and audit all policy changes.
7. **Verify jobs.** Alert on failed or delayed capture, chain gaps, checksum failures, unexpected volume changes and insufficient retention.
8. **Test recovery.** Periodically restore to an isolated environment and record measured timings, point age, validation outcomes and findings.

### 13.3 Incident recovery procedure

**Phase A — Authorise and contain**

1. Declare the recovery event, assign incident lead, data owner, security owner and technical operator.
2. Record incident start time and define the RTO clock convention.
3. Preserve forensic and audit evidence. If malicious deletion or credential compromise is suspected, isolate the affected identities and automation.
4. Identify affected datasets, earliest known bad event, consumers and lineage-based blast radius.
5. Select a recovery target before the corruption/deletion boundary, accounting for time-zone and transaction/commit semantics.
6. Approve the recovery point and target environment; record rationale and known data-loss exposure.

**Phase B — Establish a trusted recovery environment**

7. Use a clean or isolated account/project when compromise is possible; do not trust production credentials by default.
8. Provision network, DNS, private endpoints, certificates and base infrastructure from a reviewed IaC version.
9. Recover required encryption keys through the approved recovery procedure. Confirm access without exposing key material. Rotate/revoke potentially compromised credentials.
10. Apply least-privilege roles and restore audit logging before loading sensitive data.

**Phase C — Restore data and metadata coherently**

11. Select the backup set and validate manifest, signatures/checksums, chain completeness, timestamps and retention eligibility.
12. Restore raw/object data or database base backup to the isolated target.
13. Apply incrementals/logs to the approved recovery point where supported; record the exact target transaction/time/offset.
14. Restore lakehouse transaction logs/manifests and metadata that correspond to the chosen data state. Confirm referenced files exist.
15. Restore or rebuild catalogue entries and schemas; reconcile table locations, schema versions, partitions and commit IDs.
16. Restore pipeline definitions from a pinned release and provision orchestration without blindly resuming stale checkpoints.
17. Reconcile stream offsets, watermarks and sink commit state. Determine what was committed before failure and what must be replayed. Use idempotency/deduplication controls.

**Phase D — Validate**

18. Verify backup artifacts and object inventories; report missing, extra and mismatched objects.
19. Run table-open, metadata-reference, schema, partition and temporal-boundary checks.
20. Run row counts, critical constraints, referential integrity and duplicate checks.
21. Compare business control totals and representative reports with a trusted independent source for the same recovery boundary.
22. Run named downstream smoke tests and verify critical lineage paths, data permissions and audit events.
23. Record achieved recovery-point age, total elapsed time, stage timings, exceptions and evidence links.
24. If any critical criterion fails, keep affected consumers blocked, select a new recovery point or remediate and repeat validation.

**Phase E — Release and learn**

25. Obtain data-owner and incident-lead approval against the explicit pass/fail checklist.
26. Enable consumers and schedules gradually; monitor freshness, errors, query behaviour and unexpected data changes.
27. Reconcile and replay any approved gap to bring data forward without duplicating transactions.
28. Confirm monitoring and backup schedules are active in the recovered environment.
29. Preserve evidence, record objective misses and open corrective actions with owner and due date.
30. After service stabilises, review whether the backup scope, retention, isolation, restore estimates or validation criteria need an ADR update.

### 13.4 Stop conditions

Stop and escalate rather than continue blindly if:

- backup chain or integrity verification fails;
- the recovery point cannot be mapped to a coherent data/metadata boundary;
- key material is unavailable or its provenance is uncertain;
- suspected compromised credentials still control the recovery environment;
- critical object/table references are missing;
- critical business control totals exceed approved tolerance;
- data residency, legal hold or deletion policy is unclear;
- recovery is likely to exceed the RTO and business owners have not approved a degraded plan.

## 14. Scenario: inconsistent recovery points across systems

### Situation

At 09:00 UTC, an ingestion defect writes duplicate payment events. A later job propagates them into the lakehouse and updates a semantic model. During recovery, the team finds:

- source database backup restored to 08:00;
- event-stream offset restored to 08:20;
- lakehouse transaction metadata restored to 08:10;
- catalogue snapshot restored to 08:30;
- semantic model restored to 08:45;
- orchestration checkpoint points to 08:25.

Each artifact may be individually valid, but the combined platform state does not represent a single coherent point. The catalogue may reference table state newer than the restored transaction metadata; the semantic model may contain duplicates not present in the restored curated table; the checkpoint may cause data to be skipped or reprocessed twice.

### Required reasoning

1. **Do not enable consumers.** Freeze writes and downstream refreshes while the recovery boundary is established.
2. **Map every state coordinate.** Record database transaction/log sequence, event offsets per partition, lakehouse commit/snapshot ID, catalogue version, semantic-model refresh watermark and pipeline checkpoint.
3. **Select a coherent target.** Choose a target before the earliest known bad write, if possible, and determine which logs and table snapshots can reconstruct that boundary.
4. **Restore dependencies coherently.** Restore table metadata compatible with its data files; align catalogue and semantic model to the selected table commit/watermark.
5. **Reconcile offsets.** Compare source events, sink commits and checkpoint state. A checkpoint alone is not proof that the sink committed the same work.
6. **Replay safely.** Use idempotent writes, stable event IDs, deduplication and reconciliation. Never assume replay is safe solely because the pipeline can restart.
7. **Validate across systems.** Compare event counts and payment control totals, verify no gaps/duplicates, and rerun representative reports.
8. **Document exceptions.** If a perfectly aligned point is impossible, record the exact inconsistency, estimated loss/duplication, business approval and follow-up reconciliation plan.

### Deliverable

Create a **recovery-point coordination table** listing each component, restored point, desired point, gap, recovery mechanism, validation method and accountable owner. Explain whether the state is recoverable by restoring older backups, applying logs, replaying events, rebuilding derived data or combining these techniques.

## 15. Advanced scenario: malicious deletion or corrupted data

### Situation

An attacker compromises a production automation credential and deletes curated data and some object versions. The same identity has write access to a backup bucket. A recent backup may have captured already-corrupted data; a replica has faithfully propagated deletion. The team must not assume the newest retained copy is clean.

### Response design

1. Declare a security incident; preserve audit logs and evidence before routine cleanup.
2. Revoke/disable compromised identities and automation paths. Establish trusted emergency access with independent approval.
3. Determine the earliest plausible compromise time from audit events, job history, data-quality signals and identity telemetry. Treat the boundary as uncertain if evidence is incomplete.
4. Inspect independent copies: immutable retention, separate-account backup, offline copy, object versions and database logs. Verify the copies are outside the attacker’s effective control.
5. Select a known-good point earlier than the earliest plausible corruption, while considering retention/legal holds and the business data-loss impact.
6. Build a clean recovery environment from reviewed IaC and trusted software artifacts. Recreate identities; do not restore compromised secrets as-is.
7. Restore key material through the approved key-recovery path and confirm that the restored data can be decrypted. A copy that cannot be decrypted is not a usable backup.
8. Restore and validate data plus table metadata/catalogue at a coherent point. Use independent integrity and business checks to detect corruption that was already present in the backup.
9. Reconcile lost legitimate changes from trusted logs/sources; replay only after idempotency and duplicate handling are established.
10. Release consumers only after security, data-owner and recovery approvers sign off.
11. Rotate affected credentials, reduce backup permissions, review immutability and retention policies, and open corrective actions.

### Key lessons

- A replica can improve availability while preserving the attacker’s deletion.
- An immutable backup can preserve a corrupted state if corruption preceded capture.
- Versioning is weaker if the same compromised identity can purge versions.
- A backup isolated from production still depends on keys, recovery credentials, compatible tooling and documented procedures.
- Recovery-point selection is a forensic and business decision, not merely “use the latest backup.”
- Recovery success includes trusted identity, data consistency, business correctness and an auditable release decision.

## 16. Retention, deletion, residency and encryption keys

Backup design must account for conflicting requirements:

- **Retention obligations:** some records must remain available for a defined period or legal hold.
- **Deletion obligations:** some personal or regulated data must be deleted when the lawful basis and policy require it, subject to applicable exceptions.
- **Backups and erasure:** immutable backup copies may not support immediate record-level deletion. Document the lawful policy for expiry, cryptographic erasure, tombstones, restore-time reapplication of deletions and legal holds. Do not assume that “in a backup” automatically exempts a record from deletion rules.
- **Restore-time deletion replay:** a restore can resurrect data deleted after the backup point. Maintain a protected deletion ledger/tombstone mechanism or a controlled process to reapply valid deletions before releasing data.
- **Residency:** cross-region copies, restore targets, logs and test environments must comply with approved data-location constraints.
- **Encryption:** document key IDs, key hierarchy, key policies, rotation and recovery roles. Do not put plaintext keys in backup manifests or runbook files.
- **Key compromise:** revoke/rotate keys where appropriate and determine whether historical backups remain decryptable under the approved recovery design.
- **Key loss:** if all usable key material is lost, ciphertext may be permanently unrecoverable; key backup/escrow must follow security and legal policy.
- **Evidence retention:** recovery logs may themselves contain sensitive metadata; restrict access and apply a retention policy.

Security/legal owners should approve the applicable rules. This lesson is not legal advice; jurisdiction-specific requirements must be confirmed for the actual platform.

## 17. Failure modes and corrective actions

| Failure mode | Why it happens | Detection signal | Corrective action |
|---|---|---|---|
| Backup job says success but artifacts are incomplete | Partial upload, scope omission, unreported file errors | Manifest mismatch, missing objects or restore failure | Validate artifacts, alert on scope/volume anomalies, test restore |
| Base backup or incremental chain is missing | Lifecycle policy deletes dependencies or copy job fails | Chain verification fails | Retain dependency graph; test the oldest and newest supported points |
| Backup contains corruption | Corruption predates capture or checks are weak | Business reconciliation fails despite checksum pass | Retain multiple points, anomaly detection, independent control totals |
| Replica/snapshot is mistaken for independent backup | Same account/storage/control plane | Both copies disappear or share corruption | Separate failure and administrative domains; immutable/offline copy |
| Encryption key unavailable | Key deletion, wrong region/tenant, policy changed | Decryption/unwrap failure | Test key recovery, separate authorization, document rotation and escrow |
| Restore slower than estimate | Throttling, small files, rebuild or validation underestimated | Stage timers exceed budget | Measure effective throughput; model critical path; reserve headroom |
| Metadata/data mismatch | Inconsistent capture across lakehouse files, logs and catalogue | Missing references, table-open failures | Coordinate snapshots and restore compatible metadata/data sets |
| Checkpoint/sink mismatch | Checkpoint advanced without sink commit or vice versa | Duplicate/gap reconciliation | Compare offsets to committed sink state; idempotent replay |
| Old deletion is resurrected | Restore point predates a valid deletion | Deletion ledger mismatch | Reapply approved tombstones/deletions before release |
| Backup account compromised | Shared credentials or permissions | Unexpected policy changes/deletes | Isolate administration, immutable retention, independent audit |
| Validation is too weak | Only a row count or “service starts” is checked | Reports wrong despite green health checks | Add independent control totals, schema, lineage and consumer tests |
| Restore test leaks sensitive data | Broad access or unmanaged test copy | Audit/scan findings | Isolate, mask where feasible, constrain identities and securely dispose |
| RTO reported inaccurately | Clock starts late or ends at data copy completion | Business service unavailable after “success” | Define clock boundaries and “usable” endpoint; record all stage timings |
| Retention policy creates a gap | Logs expire before the required PITR window | Desired point cannot be reconstructed | Align log retention to recovery needs; alert on recoverable-window shrinkage |

## 18. Exercises and expected deliverables

Complete the exercises on paper or in a non-production simulation. All figures are illustrative.

### Exercise 1 — Backup vs replica vs snapshot

For a critical payments dataset, compare backup, replica, snapshot, archive and object versioning. For each, state the failure it covers, the failure it does not cover, security boundary and recovery-time dependency.

**Expected deliverable:** completed comparison table plus a recommendation with at least three explicit assumptions.

### Exercise 2 — Backup-scope inventory

Using the inventory in Section 6, choose a representative pipeline and mark each component as restore exactly, reconstruct, reconcile/replay, recreate/rotate or preserve under policy.

**Acceptance criteria:** at least 12 component types; each has an owner, capture method, consistency requirement, retention/location, validation check and recovery dependency.

### Exercise 3 — Data-loss exposure

A successful backup completes every 4 hours. Assume no log backup, every run succeeds and failure time is uniformly distributed between backups.

- Estimate the maximum idealized exposure.
- Estimate average exposure.
- Explain why this does not prove a 30-minute RPO.

**Expected answer:** maximum approaches 4 hours; average is 2 hours under the stated idealized assumptions; the design cannot meet 30 minutes without a finer-grained capture/recovery mechanism and evidence that its lag remains within target.

### Exercise 4 — Restore-time estimate

A dataset is 8 TiB. The measured effective sustained throughput is 256 MiB/s, including protocol overhead and ordinary throttling. Rebuild takes 1.25 hours; validation takes 1.5 hours; catch-up takes 0.75 hours; provisioning takes 0.5 hours. Assume sequential stages.

Use \(1\text{ TiB}=1{,}048{,}576\text{ MiB}\).

- Volume = \(8 \times 1{,}048{,}576 = 8{,}388{,}608\text{ MiB}\).
- Transfer time = \(8{,}388{,}608 / 256 = 32{,}768\text{ s}\).
- Transfer hours = \(32{,}768 / 3{,}600 \approx 9.10\text{ h}\).
- Total = \(9.1022 + 1.25 + 1.5 + 0.75 + 0.5 \approx 13.10\text{ h}\).

**Acceptance criteria:** preserve units, avoid subtracting overhead twice, include all stages, and explain that real elapsed time may be higher if retries, metadata work or parallelism assumptions differ.

### Exercise 5 — Inconsistent recovery points

Complete the coordination table for the Section 14 scenario. Pick a target point and state which systems must be restored, rebuilt or replayed.

**Acceptance criteria:** no consumer release before data/metadata/checkpoint alignment; include event offset and sink-commit reconciliation; document residual gaps and owners.

### Exercise 6 — Malicious deletion

Design a recovery plan when production credentials can delete object versions and the latest backup may contain corruption.

**Acceptance criteria:** independent copy, credential isolation, clean environment, key recovery, known-good point selection, business validation, deletion reapplication and post-incident corrective actions are all addressed.

### Exercise 7 — Recovery validation

Choose five critical data-quality/business checks and specify source of truth, target boundary, formula or query, tolerance, owner and pass/fail rule.

**Acceptance criteria:** include at least one integrity check, one schema/structural check, one referential or completeness check, one business control total and one downstream smoke test.

### Exercise 8 — Recovery ADR

Write an ADR that compares at least two recovery designs (for example, daily full backups plus logs versus frequent snapshots plus independent immutable backup). Include consequences, costs, security boundary, recovery assumptions, evidence required and unresolved risks.

**Acceptance criteria:** recommendation follows from requirements and documented trade-offs, not vendor preference; no unmeasured RTO/RPO claim.

## 19. Example recovery-focused ADR

### ADR-004: Independent recoverable copies for the curated lakehouse

- **Status:** Proposed — illustrative teaching example
- **Context:** The lakehouse serves critical reporting. Replication improves availability but can propagate erroneous writes and deletion. The team needs a recoverable known-good point and proof that metadata and data can be restored together.
- **Decision drivers:** approved RPO/RTO; data volume and change rate; corruption-detection delay; data residency; key recovery; isolation from production credentials; restore-test evidence; cost and operational complexity.
- **Options considered:**
  1. Replica only.
  2. Snapshots retained in the production account.
  3. Coordinated table/database backups and required logs copied to an independently administered, protected recovery account, with a clean restore test.
  4. Offline/air-gapped copy in addition to Option 3 for higher-threat scenarios.
- **Decision:** Select Option 3 as the baseline for the fictional scenario, with Option 4 evaluated if the threat model or policy requires an additional offline boundary. The replica remains an availability control, not the backup strategy.
- **Design requirements:** capture compatible data and transaction metadata; preserve necessary logs; retain recoverable points long enough to cover detection delay; protect key recovery; keep production identities from deleting backup copies; record object manifests and commit IDs; restore into an isolated target; validate technically and with business controls.
- **Consequences:** additional storage, transfer, key-management and test costs; more runbook and access-control work; better separation from production failure modes; recoverability remains unproven until tests pass.
- **Assumptions to verify:** backup mechanism supports consistent capture; recovery account is administratively isolated; required encryption keys can be recovered; measured throughput supports the approved RTO.
- **Validation/evidence:** periodic isolated restore; complete backup-chain check; object/table metadata integrity; business control totals; downstream smoke tests; measured elapsed time and recovery-point age; approver sign-off.
- **Risks and mitigations:** delayed corruption detection (retain older points and anomaly signals); key loss (tested recovery); slow retrieval (measure throughput); metadata mismatch (capture commit IDs and restore compatible sets); accidental deletion resurrection (reapply approved deletion ledger).
- **Revisit when:** data volume, change rate, threat model, legal retention, platform format, RPO/RTO or restore-test results materially change.

## 20. Recovery validation checklist

Use this checklist for a design review or a non-production restore exercise. Mark N/A only with a documented reason.

### Scope and objectives
- [ ] Critical datasets, metadata, pipelines, checkpoints, configuration and key dependencies are inventoried.
- [ ] Data owner and recovery owner are named for each critical scope.
- [ ] Required recovery point and “usable service” endpoint are explicitly defined.
- [ ] RPO/RTO objectives are business-approved and not inferred from backup schedules.

### Backup design
- [ ] Backup method and exact restore chain are documented.
- [ ] Backup frequency and retained recovery window cover the stated objectives and corruption-detection delay.
- [ ] Full/incremental/differential semantics are verified for the selected technology.
- [ ] Database logs, lakehouse transaction metadata and catalogue state are included or reproducibly rebuilt.
- [ ] Backup copies are separated from relevant production failure and administrative domains.
- [ ] Immutability/offline controls and deletion permissions are tested.
- [ ] Key recovery, rotation and access procedures are documented without exposing secrets.
- [ ] Retention, residency, legal hold and deletion-resurrection controls are approved.

### Restore procedure
- [ ] Restore target is isolated and approved.
- [ ] Clean identities, networking, certificates, keys and infrastructure prerequisites are available.
- [ ] Backup IDs, timestamps, manifest/checksum and chain completeness are recorded before restore.
- [ ] Restore order and dependency owners are explicit.
- [ ] Recovery-point coordinates across systems are aligned or reconciled.
- [ ] Checkpoints, offsets and sink commits are reconciled before replay/resume.
- [ ] Stop conditions and escalation paths are clear.

### Validation and release
- [ ] Artifact integrity and completeness checks pass for critical scope.
- [ ] Schema, table metadata and referenced-file checks pass.
- [ ] Required partitions/date ranges and data watermarks are correct.
- [ ] Referential integrity, duplicate and completeness checks pass.
- [ ] Business control totals match an independent trusted source or approved tolerance.
- [ ] Critical reports, downstream jobs and lineage paths pass.
- [ ] Security, encryption, permissions and audit logging pass.
- [ ] Measured elapsed time and achieved recovery-point age are recorded against approved RTO/RPO.
- [ ] All critical failures are resolved or explicitly accepted by authorised owners before release.
- [ ] Evidence is retained in a protected location; findings have owners and due dates.

### Example pass/fail gate

A recovery exercise **passes** only when all critical checks in the approved scope pass, recovery point and elapsed time are measured against approved objectives, security controls are validated, business owners approve exceptions, and the evidence record is complete. “Backup job succeeded,” “files copied,” “database started,” or “table count matched” alone is not a pass.

## 21. Common mistakes and misconceptions

| Mistake | Why it is wrong | Better practice |
|---|---|---|
| “Replication is backup.” | Bad writes and deletes may replicate. | Retain independent known-good recovery points. |
| “A snapshot is always consistent.” | Storage snapshots may be crash-consistent or only locally atomic. | Use application/table-aware capture and record consistency guarantees. |
| “The backup job passed, so recovery works.” | A job status does not prove a full chain can be restored. | Run isolated restore and validation tests. |
| “A checksum proves business correctness.” | It only compares bytes to a trusted digest. | Combine integrity, structural and business checks. |
| “The latest backup is the best recovery point.” | It may include corruption or malicious changes. | Select a known-good point using incident evidence and business trade-offs. |
| “Backup interval equals RPO.” | Capture gaps, log lag and failed jobs alter actual exposure. | Measure achieved point age and verify worst-case capture gaps. |
| “Restore time is data size divided by network peak.” | Real throughput, metadata work, rebuild and validation dominate. | Use effective sustained throughput and stage-level measurements. |
| “Restoring files restores the lakehouse.” | Transaction metadata, catalogues and schemas may be missing or mismatched. | Restore compatible metadata/data state and verify table references. |
| “A clean environment can use old secrets.” | Credentials may be compromised or stale. | Recreate identities and rotate secrets under incident controls. |
| “Old backups can ignore deletion obligations.” | Restore may resurrect data subject to valid deletion requirements. | Apply the approved deletion ledger and legal policy before release. |
| “A passing row count proves correctness.” | Missing and duplicate rows can offset each other. | Add keys, control totals, date boundaries and independent reconciliation. |
| “We can restore later if needed.” | Missing keys, expired logs and undocumented dependencies may make recovery impossible. | Test the full procedure and preserve evidence. |

## 22. Glossary

- **Backup chain:** the base backup plus all required incremental/log artifacts for a particular restore.
- **Control total:** a business reconciliation value such as total payment amount, order count or inventory quantity.
- **Deletion ledger/tombstone:** protected record of deletions that must be respected when older state is restored.
- **Effective throughput:** observed end-to-end transfer rate under realistic constraints, not theoretical interface bandwidth.
- **Immutable retention:** policy that restricts modification/deletion for a defined period, within the storage system’s actual guarantees.
- **Known-good point:** a recovery point assessed as preceding or excluding the corruption/compromise, with sufficient evidence for the use case.
- **PITR:** point-in-time recovery using a compatible base plus retained history/logs.
- **Recovery manifest:** inventory of the exact recovery-point coordinates and artifacts selected for a coordinated restore.
- **Restore validation:** technical and business checks that determine whether restored state is complete, consistent, secure and fit for use.
- **RPO:** maximum acceptable data-loss interval.
- **RTO:** maximum acceptable time to restore the defined service to the agreed usable state.

## 23. Mastery criteria and completion gate

You have mastered this topic when you can:

- Explain why a replica, snapshot, archive and backup solve different problems.
- Calculate idealized data-loss exposure from backup intervals and state the assumptions.
- Estimate recovery time with correct units, effective throughput, rebuild, validation and catch-up.
- Produce a complete backup inventory including metadata, code, identity and key dependencies.
- Explain how to recover a database or lakehouse to a coherent point.
- Design restoration order and identify stop conditions.
- Define measurable technical and business validation with independent sources of truth.
- Explain how malicious deletion, key loss, retention and deletion obligations affect recovery.
- Document evidence without confusing assumptions with observed measurements.
- Defend a recovery design through an ADR and list unresolved risks.

### Completion checklist

- [ ] Backup-versus-replica-versus-snapshot comparison completed.
- [ ] Backup-scope inventory covers at least 12 component types.
- [ ] Backup-interval calculation independently reproduced.
- [ ] Restore-time calculation independently reproduced with units.
- [ ] Ordered restore procedure reviewed for dependency gaps.
- [ ] Inconsistent recovery-point scenario resolved on paper.
- [ ] Malicious deletion/corruption scenario includes security isolation and known-good point selection.
- [ ] Validation checklist has measurable pass/fail criteria and named owners.
- [ ] Example evidence record distinguishes illustrative values from observed facts.
- [ ] Recovery ADR compares alternatives and states assumptions and consequences.
- [ ] Gaps and corrective actions recorded.
- [ ] Readiness confirmed for Topic 05: RPO, RTO and disaster recovery strategies.

## 24. Further references within the project

Use the module roadmap as the source of the learning sequence. Related project topics include:

- `../05-Database-and-Storage-Architecture/06-replication-consistency-and-transaction-boundaries.md`
- `../05-Database-and-Storage-Architecture/07-retention-archival-and-data-lifecycle-storage-tiers.md`
- `../06-Data-Integration-and-Interoperability/07-idempotency-deduplication-and-reconciliation.md`
- `03-high-availability-and-redundancy-patterns.md`
- `05-rpo-rto-and-disaster-recovery-strategies.md`
- `06-replay-reprocessing-and-backfill-architecture.md`
- `07-incident-response-runbooks-and-postmortems.md`
- `08-business-continuity-and-resilience-testing.md`

**Final principle:** design for the recovery state the business needs, not merely the backup artifact the platform can produce. Recoverability is demonstrated by repeatable restoration, coherent state, measurable validation, controlled release and retained evidence.
