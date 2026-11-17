# Unit 1 — Recovery Time and Recovery Point Objectives

**Target file:** `01-recovery-time-and-recovery-point-objectives.md` | **Estimated time:** 12–16 hours | **Prerequisites:** Stage 0–2D; Stage 2E M01–M12, especially M05 (database backup/PITR), M07 (Terraform state), M08 (GitOps), M09 (Vault/OpenBao and key custody), M10 (incident management), M11 (observability), and M12 (supply-chain security).

**Core tools:** Python 3 standard library, shell, Git, existing M05 PostgreSQL/CloudNativePG lab, local object-store tooling if already configured, CSV/YAML/Markdown evidence. | **Awareness:** ISO 22301, DRII, NIST SP 800-34, cloud DR tiers, managed database recovery, multi-region replication. | **Last reviewed:** 2026-10-29 (authoring date; not evidence of live documentation review). | **Tool baseline assumed:** Python 3; other tool versions are installation-specific and version-sensitive; verify installed versions and current official documentation before using commands. | **Footprint:** calculations and Python exercises are negligible; optional database/object-store lab uses a tiny dataset and depends on the existing M05 setup; measure yours. | **Destructive labs:** yes — throwaway lab data only; never point a destructive command at a production context or an unverified namespace.

> **Safety and fidelity statement:** All example objectives and measurements are illustrative unless explicitly identified as learner-measured. Two `kind` clusters on one laptop are not two regions: they share host hardware and often network, power, disk, and other failure domains. A laptop drill rehearses workflow; it does not prove regional resilience or predict production RTO/RPO.

## 1.0 Why this matters in production

A team can have successful nightly backups and still lose more data than the business accepts if a failure occurs just before the next usable backup. A database or Pod can be running while the service remains unrecovered because credentials, registry access, model artifacts, DNS, verification, or traffic cutover are still unavailable. A replica can copy an accidental deletion or logical corruption almost immediately, so replication lag alone does not establish recoverability. RTO and RPO must therefore be negotiated against business impact, derived from the complete dependency chain, and tested with measured evidence. This unit turns recovery objectives from optimistic statements into explicit, testable requirements.

## 1.1 Learning objectives

By the end of this unit, the learner can:

1. [L1] Define disaster, RTO, RPO, MTD/MTPD, WRT, RTA, and RPA with explicit clock boundaries.
2. [L1] Calculate data-loss age from failure time and the latest verified recoverable business event.
3. [L1] Distinguish high availability, disaster recovery, backup, snapshot, and replication by the failure classes each addresses.
4. [L2] Complete a BIA-lite worksheet that scores downtime and data-loss impact separately without inventing monetary loss.
5. [L2] Build a recovery objectives register with owners, dependencies, consistency groups, mechanisms, targets, measurements, and evidence references.
6. [L2] Estimate mechanism-based RPO for periodic backups, WAL/archive recovery, asynchronous replication, queue replay, and logical corruption, documenting assumptions and limits.
7. [L2] Decompose RTO into measurable phases and estimate transfer time from dataset size and measured throughput.
8. [L3] Model dependency-implied recovery time and explain why independently restored state may be inconsistent even when each component passes its own test.
9. [L3] Compare backup-and-restore, pilot-light, warm-standby, and multi-site strategies against objectives, cost, complexity, and failure modes.
10. [L4] Govern objective gaps, exceptions, drill cadence, and evidence across a service portfolio, including compound security and trust-root failures.
11. [L4] Report measured RTA/RPA, confidence limits, remaining risks, and remediation without presenting a laptop simulation as production assurance.

## 1.2 Concept map and vocabulary

### Glossary

| Term | Precise definition | Common misconception / operational consequence |
|---|---|---|
| Disaster | An event that makes a service or its data unavailable or corrupt beyond what normal operations or high availability can handle. | It is not limited to a geographic event; logical corruption, identity loss, or destructive compromise may qualify. |
| RTO — Recovery Time Objective | Target maximum elapsed time from the explicitly chosen clock start (for example, service outage start or disaster declaration) until the service meets an agreed functional restoration criterion. | It is not simply the time until a process, Pod, or database starts. The clock boundary must be written down. |
| RPO — Recovery Point Objective | Target maximum tolerable data loss expressed as time between the failure point and the latest recoverable, valid state. | Backup interval alone is not proof of RPO. Durability, completion, retention, corruption detection, and business-event semantics matter. |
| MTD / MTPD | Maximum Tolerable Disruption / Maximum Tolerable Period of Disruption: the business-defined outer limit of disruption before consequences become unacceptable. Terminology varies by source; verify exact standard wording. | `RTO < MTD` is a sensible planning expectation, not a universal mathematical law. Include any required work-recovery time in the business-impact discussion. |
| WRT — Work Recovery Time | Time after technical restoration needed for verification, reconciliation, backlog catch-up, and return to an agreed usable operating state. | Teams may double-count or omit it. State whether the RTO endpoint is technical service restoration or business-ready recovery. |
| RTA — Actual/Achieved Recovery Time | Observed elapsed time using the documented start and end events during a drill or incident. Naming conventions vary. | A target is not an actual result. Do not substitute an estimate for a measured drill. |
| RPA — Actual/Achieved Recovery Point | Observed recovered-point age or equivalent lost-business-event measure at the failure boundary, using an explicitly documented method. | Wall-clock age may hide lost, duplicated, reordered, or unreconciled events. Record event IDs/offsets where relevant. |
| HA | High availability mechanisms that keep a service functioning through supported component failures, commonly within a defined failure domain. | HA does not guarantee near-zero RTO/RPO for every failure, and may not protect against logical corruption or loss of shared identity. |
| DR | The people, process, architecture, and procedures used to restore service after a disaster or significant failure-domain/logical event. | A second cluster is not a DR capability unless dependencies, data, credentials, capacity, and runbooks are recoverable. |
| Backup | A protected recoverable copy of data or state, retained so it can be restored after loss or corruption. | A successful backup job does not prove that the copy is complete, independent, decryptable, or restorable. |
| Snapshot | A point-in-time representation of state, often dependent on the underlying storage or platform. | A snapshot may share the failure domain and credentials of the source; it is not automatically an independent backup. |
| Replication | Copying state or changes to another target, synchronously or asynchronously. | Replication can rapidly copy deletion, corruption, or malicious changes. It is not a substitute for historical recovery points. |
| Consistency group | Components whose restored states must correspond to a mutually compatible point or be reconciled using explicit rules. | Restoring a database, object store, queue offset, and model registry independently can create a system that is individually healthy but collectively wrong. |
| Business Impact Analysis (BIA) | A structured assessment of how service disruption and data loss affect business outcomes over time. | Objective values should come from impact and feasibility analysis, not a generic tier table copied unchanged. |
| SLO / error budget | A service-level objective describes expected reliability over a measurement window; an error budget is the permitted unreliability under the SLO policy. | Whether disaster time consumes the error budget depends on the organization's policy. Treat “usually outside” as an assumption, not a universal rule. |
| Failure domain | A boundary within which shared infrastructure or dependencies can fail together, such as process, node, zone, region, account, identity plane, or operator. | Logical and security failures can cross physical boundaries. “Different cluster” does not mean independent failure domain. |
| Recovery point | The specific consistent, validated state selected for restoration, often identified by timestamp plus transaction/event/offset markers. | “Newest” is not always “correct”: after corruption, a clean earlier point may be necessary. |

### Recovery path and clocks

```text
Failure event at T0 (node / zone / region / logical / malicious / dependency / identity)
   | failure domain and business impact determine whether to declare a disaster
   v
Detect -> Declare -> Decide (fail over, restore, rebuild, or wait for dependency)
   |                    
   v
Recovery start -> recover trust roots/identity -> network/DNS -> storage/platform
   -> restore data and metadata to a compatible recovery point -> start applications
   -> verify correctness and security -> authorize traffic cutover
   -> reconcile/replay/catch up -> business-ready service

RTO clock: selected start event ------------------------------> agreed service-restored event
RPO:       failure boundary T0 - latest valid, recoverable, consistent state
WRT:       technical restore -------------------------------> verified/business-ready state
```

**Choose one RTO clock and keep it consistent.** This lesson's default measurement is *outage start to agreed functional service restoration*. If an organization instead starts the clock at formal declaration, record that explicitly and also preserve the outage-start timestamp; otherwise delayed declaration can make recovery appear artificially fast. RPO is measured relative to the failure boundary, not the time the incident was declared.

### Recovery timeline example

| Event | Timestamp `[ILLUSTRATIVE]` | Operational meaning |
|---|---:|---|
| Failure begins (T0) | 10:00 | Writes become unavailable or untrustworthy; this anchors RPO. |
| Detection | 10:03 | Alert confirms impact. |
| Declaration | 10:08 | Incident commander declares disaster; record separately from T0. |
| Decision | 10:12 | Choose restore rather than fail over to potentially corrupted replica. |
| Recovery starts | 10:15 | Recovery runbook begins. |
| Data restored | 10:42 | Database and required object data available in isolation. |
| Services up | 10:48 | Processes start, but no traffic yet. |
| Verification complete | 10:56 | Data, permissions, model, and smoke tests pass. |
| Traffic cutover | 11:00 | Approved traffic reaches recovered service. |
| Reconciliation/catch-up complete | 11:20 | Backlog and downstream consistency meet agreed threshold. |

If the agreed RTO endpoint is traffic cutover, RTA is 60 minutes (10:00–11:00). If the service definition requires reconciliation and catch-up, business-ready recovery is 80 minutes (10:00–11:20); that latter duration may be reported as end-to-end recovery or RTA plus WRT according to the organization's chosen definitions. Do not change endpoint after the drill to make a target pass.

### Failure classes and mechanism fit

| Failure class | Mechanisms that may help | Important limitation / test question |
|---|---|---|
| Process/component | Restart, health checks, HA | Can the restart loop recover without operator action? |
| Node | Replicas, scheduler rescheduling, replicated storage | Are replicas and storage actually independent of the failed node? |
| Zone | Zone-aware replicas and storage, traffic routing | Does the surviving zone have quota and capacity? |
| Region/site | Independent backups, tested rebuild, warm standby, replicated data | Can identity, keys, registry, DNS, quotas, and operators be recovered? A laptop simulation does not prove this. |
| Logical error (bad migration/deletion) | PITR, retained immutable versions, clean backups, replay/rebuild | Does the recovery point precede the bad change and remain retained? |
| Malicious/destructive action | Immutable/offline or separately controlled copies, isolated credentials, clean rebuild, key custody | Can the compromised workload identity delete backups or alter retention? Can the restored environment be trusted? |
| Dependency/provider outage | Cached artifacts, alternative dependency, documented degraded mode, recovery copy | Is the dependency truly optional? Can the system boot without the primary identity/registry service? |
| Platform/control-plane/identity failure | IaC/Git rebuild, etcd/platform recovery, independent trust-root/key escrow, offline runbooks | Is there a bootstrap path if the platform, secrets, or monitoring is unavailable? |

## 1.3 Level 1 — Beginner

### Targets, estimates, and observations

A **target** is a negotiated requirement (for example, RTO no more than 60 minutes). An **estimate** is a prediction based on assumptions or component timings. An **observation** is what a drill or incident actually measured. Keep them separate in records:

- Target RTO: `<= 60 min` — approved requirement.
- Estimated RTO: `52 min` — calculation based on measured throughput and assumed provisioning time.
- Measured RTA: `67 min` — drill result, which misses the target by 7 minutes.

Never relabel the estimate as a measured result. Record the dataset size, tool versions, environment, timing boundaries, and whether the trial was cold or warm.

### Worked scenario A: daily backup and a failure between backups

Assume a daily backup completed at 02:00 and the system fails at 23:30. The recovered backup contains data valid through 02:00. The wall-clock age is:

`23:30 - 02:00 = 21 hours 30 minutes`

If the RPO target is 4 hours, this recovery point misses the target by 17 hours 30 minutes. A “daily backup” does not imply a guaranteed 24-hour RPO in every case: completion failures, copy lag, unusable backups, and retention can make the actual worst case worse. Conversely, transaction logs or event replay may improve the recoverable point if they are durable and available.

### Worked scenario B: continuous WAL archive or asynchronous replication

Assume a failure occurs at 14:10 and the last *durable, verified, recoverable* WAL point represents 14:07:30. The age is 2 minutes 30 seconds. If the RPO target is 5 minutes, the point meets the time-based target, provided the database can actually recover to that point and the corresponding application state is consistent. A configured archive schedule is not proof; use the last recoverable archive position and measure archive lag. For asynchronous replication, a measured 40-second lag at failure suggests a small time window, but it does not account for unacknowledged/in-flight writes, replication breakage, or logical corruption replicated to the follower.

### Worked scenario C: process is running but recovery is incomplete

An inference API starts at 10:48, but it cannot load its signed model because the registry metadata was restored without the artifact, and its credentials point to the unavailable primary Vault. The process is alive; the agreed service is not functional. RTO should end only when the documented service-level test passes—for example, authenticated inference returns a valid response using the intended model version, and required data-integrity checks pass. If traffic cutover is part of the agreed endpoint, include it too.

### RPO arithmetic

For a simple time-based measurement:

`Observed recovery-point age = failure timestamp - timestamp of latest valid recoverable state`

Example `[ILLUSTRATIVE]`:

- Failure: `2026-10-29 10:00:00 UTC`
- Last verified valid event: `2026-10-29 09:54:30 UTC`
- Age: `5 minutes 30 seconds`
- RPO target: `5 minutes`
- Result: **FAIL**, by 30 seconds.

Use UTC or another explicit timezone consistently. For event streams, record the last acknowledged business-event ID, source offset, consumer offset, and checkpoint marker as well as timestamps. A five-minute-old checkpoint can still cause duplicates or gaps if replay semantics are incorrect.

### Guided mini-exercise: compute the recovered-point age

Use Python 3's standard library; no external dependencies are required.

```python
from datetime import datetime, timezone

failure = datetime.fromisoformat("2026-10-29T10:00:00+00:00")
last_valid = datetime.fromisoformat("2026-10-29T09:54:30+00:00")
rpo_target_seconds = 300

age_seconds = (failure - last_valid).total_seconds()
print(f"recovered_point_age_seconds={age_seconds:.0f}")
print(f"target_seconds={rpo_target_seconds}")
print(f"result={'PASS' if age_seconds <= rpo_target_seconds else 'FAIL'}")
```

Representative output (not executed here):

```text
recovered_point_age_seconds=330
target_seconds=300
result=FAIL
```

Check manually: 5 minutes 30 seconds equals 330 seconds; the target is 300 seconds. The recovered point is older than permitted. Change the last valid timestamp to `09:56:00+00:00`; the age becomes 240 seconds and passes this simple check. This arithmetic does not prove that the data is complete, clean, decryptable, or consistent.

### Beginner mistakes

| Mistake | Symptom | Reason | Correction |
|---|---|---|---|
| Start RTO at declaration even though requirement says outage start | Reported RTA looks shorter than user impact | Clock starts late | Capture T0 and declaration separately; use the agreed clock. |
| Treat a successful backup job as proof of recovery | Restore fails or data is incomplete | Job success may mean only that a process finished | Restore in isolation and verify content and application behavior. |
| Use replica lag as the only RPO evidence | Missing or corrupted business records despite low lag | Lag ignores logical corruption and some in-flight writes | Test failure classes and preserve historical clean points. |
| Stop timing when a Pod is Ready | Requests fail or return wrong data | Readiness may not check dependencies or semantics | Define and run functional verification before stopping the clock. |
| Use wall-clock timestamps only for a stream | Duplicate or skipped events after replay | Offset/checkpoint semantics are missing | Record event IDs, offsets, idempotency behavior, and reconciliation. |
| Restore every component to its newest available point | Database references absent objects or model artifacts | Independent points are inconsistent | Restore a consistency group or execute documented reconciliation. |

## 1.4 Level 2 — Intermediate

### A. BIA-lite for a data/ML platform

A BIA-lite is a practical worksheet, not a legal or financial certification. Score **downtime impact** and **data-loss impact** separately, using criteria your stakeholders can understand. The following scale is `[ILLUSTRATIVE]` and should be replaced or approved by the organization:

- **1 — Low:** temporary interruption has a small, reversible impact; work can wait or be rerun.
- **2 — Moderate:** users or teams are meaningfully delayed; manual workaround or reprocessing exists.
- **3 — High:** customer-facing or revenue-impacting work is impaired, important data must be reconciled, or a time-sensitive commitment is at risk.
- **4 — Critical:** prolonged loss threatens essential service, authoritative records, or obligations requiring immediate escalation. Regulatory data is an awareness category here; no legal conclusion is implied.

| Service/data class | Downtime impact `[ILLUSTRATIVE]` | Data-loss impact `[ILLUSTRATIVE]` | RPO reasoning | RTO reasoning |
|---|---:|---:|---|---|
| Customer-facing inference | 4 | 2–4 depending on request logging/state | Model can sometimes be reloaded, but request/audit state may not be reconstructible. | Depends on business tolerance, degraded mode, and model/identity availability. |
| PostgreSQL system of record | 4 | 4 | Usually low tolerance for losing committed business events; use durable backup/PITR or replication plus historical recovery. | Depends on restore throughput, consistency checks, and the authority to resume writes. |
| Datasets/curated objects | 2–3 | 2–4 | Rebuildable derived data may be reprocessed; unique source data needs stronger protection. | Rebuild time depends on volume, source retention, compute, and dependency access. |
| Model artifacts | 3 | 2–4 | Some models can be retrained, but retraining may be slow or nondeterministic; preserve exact released artifacts when required. | A known-good artifact may restore faster than retraining; registry and signature verification are dependencies. |
| Model registry metadata | 3–4 | 3–4 | Aliases, lineage, approvals, and artifact hashes must match; metadata loss can make artifacts unsafe to serve. | Requires restoring metadata and reconciling it with artifact inventory. |
| Orchestrator/metadata DB | 2–3 | 2–3 | Jobs can often be rerun, but duplicate side effects and lost schedules need handling. | Rebuild configuration from Git; restore state only where it is authoritative and needed. |
| Queue/stream and checkpoints | 3 | 3–4 | Depends on source retention, acknowledged offsets, replay safety, and event ordering. | Backlog catch-up can dominate WRT even after the service is technically up. |
| Internal analytics/training pipelines | 1–2 | 1–3 | Recompute is acceptable only if source data is retained and compute capacity exists. | Backlog and retraining duration should be modeled explicitly. |
| Regulatory/retained records | 3–4 | 4 | Retention and recovery rules require qualified review; do not infer compliance from this worksheet. | Evidence, approvals, and integrity checks may be part of functional restoration. |
| Git/GitOps and IaC | 3 | 2–3 | Git does not hold runtime data, but missing history/config blocks rebuild. Keep independent mirrors and protect credentials. | Bootstrap order, access, and pinned dependencies determine rebuild time. |
| Vault/OpenBao/trust roots | 4 | 4 | Lost keys or sealing material can make otherwise intact backups unusable. | Recovery must include trusted key custody and secure credential rotation. |
| Container registry/signed artifacts | 3 | 3 | Need compatible images, digests, signatures, provenance, and trusted verification keys. | A registry outage can block every downstream restore if no cache/mirror exists. |
| Observability and DR runbooks | 3 | 2 | Monitoring loss may not erase application data but removes signals needed to recover safely. | Restore minimum viable monitoring and offline runbooks early. |
| DNS/traffic routing | 4 | 1–2 | Usually not authoritative business data, but stale routing can send users to the wrong system. | TTLs, control-plane access, and rollback decisions affect the clock. |

**Tiering example — do not copy without a BIA.** The labels below are `[ILLUSTRATIVE]`, not approved objectives:

| Tier | Example criterion | Example objective range `[ILLUSTRATIVE]` | Required evidence |
|---|---|---|---|
| Tier 0 | Essential service or authoritative state with very low tolerance for interruption/data loss | RTO minutes to low hours; RPO seconds to minutes where technically justified | Repeated restore/failover drills, security and consistency checks, executive-approved residual risk |
| Tier 1 | High-impact service with limited workaround | RTO hours; RPO minutes to hours | Timed restore and dependency test, signed objective record |
| Tier 2 | Important internal service with reprocessing or manual workaround | RTO within a business day; RPO hours where source replay is possible | Verified backup, documented replay/rebuild, periodic drill |
| Tier 3 | Deferrable workload or reproducible derived output | RTO days may be acceptable; RPO may be “re-derive” if sources remain available | Rebuild/recompute evidence and confirmed source retention/capacity |

Do not assign a tier by technical convenience. Ask the business owner what breaks over 15 minutes, 4 hours, one business day, and several days; ask what data can be recreated and how long that takes; then test feasibility with engineering. Tighter objectives usually increase replication, standby capacity, automation, complexity, and operational practice. Stakeholders must approve both the target and the residual risk if the target is not achievable.

**Stakeholder agreement record template**

```yaml
service: inference-api
business_owner: "[name/role]"
technical_owner: "[team/role]"
impact_summary: "[impact during outage and on lost data]"
impact_scores: { downtime: 4, data_loss: 3 } # [ILLUSTRATIVE]
agreed_rto: "60 minutes"                  # [ILLUSTRATIVE]
agreed_rpo: "5 minutes"                   # [ILLUSTRATIVE]
rationale: "[why these values are tolerable and feasible]"
assumptions: ["source events retained for replay"]
approver: "[role/name]"
approval_date: "YYYY-MM-DD"
exceptions: []
review_date: "YYYY-MM-DD"
```

### B. Recovery objectives register

Use a register to connect business objectives to mechanisms and evidence. Below is a CSV-shaped schema followed by a small illustrative example. Values are not production approvals.

**Schema:** `system_id,description,owner,business_owner,tier,tier_rationale,rto_target_minutes,rpo_target_minutes,mtd_minutes,mtd_source_approval,recovery_mechanism,hard_dependencies,recovery_order,consistency_group,last_tested,measured_rta_minutes,measured_rpa_minutes,evidence_ref,status,assumptions,exception_expiry`

| system_id | Description | Tier | RTO/RPO `[ILLUSTRATIVE]` | Recovery mechanism | Hard dependencies / order | Consistency group | Last tested / RTA / RPA | Status |
|---|---|---:|---|---|---|---|---|---|
| `db-primary` | PostgreSQL system of record | 0 | 60m / 5m | Base backup + WAL/PITR; isolated restore | Keys/identity, storage; order 5 | `orders-v1` | `NOT TESTED` | UNTESTED |
| `object-data` | Source and curated objects | 1 | 120m / 30m | Versioned protected copy + manifest/hash checks | Object-store credentials; order 4 | `orders-v1` | `NOT TESTED` | UNTESTED |
| `model-artifacts` | Released model files | 1 | 120m / 60m | Copy/version retention + digest/signature verification | Registry, keys; order 6 | `model-release-v1` | `NOT TESTED` | UNTESTED |
| `model-registry` | Model versions, aliases, lineage | 1 | 90m / 30m | Metadata DB backup + artifact reconciliation | DB, artifacts, signing trust; order 7 | `model-release-v1` | `NOT TESTED` | UNTESTED |
| `orchestrator-meta` | Job and schedule metadata | 2 | 240m / 120m | Git rebuild plus state restore if needed | Git, DB, secrets; order 8 | `pipeline-v1` | `NOT TESTED` | UNTESTED |
| `queue-checkpoints` | Queue offsets and ETL checkpoints | 1 | 120m / 15m | Retained source replay + checkpoint recovery | Source retention, database; order 9 | `orders-v1` | `NOT TESTED` | UNTESTED |
| `gitops` | Deployment configuration | 1 | 60m / N/A | Git mirror and pinned IaC | Git access, trust roots; order 2 | `platform-v1` | `NOT TESTED` | UNTESTED |
| `vault-trust` | Secrets and recovery trust roots | 0 | 60m / N/A | Vault/OpenBao snapshot and separate key custody | Offline key material; order 1 | `platform-v1` | `NOT TESTED` | UNTESTED |
| `registry-images` | Container images and signatures | 1 | 90m / N/A | Protected registry backup/mirror; digest and signature checks | Trust keys, object store; order 3 | `platform-v1` | `NOT TESTED` | UNTESTED |
| `observability` | Minimal metrics/logs/alerts | 1 | 60m / N/A | Rebuild configs from Git; restore needed state | Git, platform, credentials; order 3–4 | `platform-v1` | `NOT TESTED` | UNTESTED |
| `dns-routing` | DNS and traffic control | 0 | 60m / N/A | Provider-neutral runbook and authorized access | Identity/provider access; order 10 | `platform-v1` | `NOT TESTED` | UNTESTED |
| `dr-runbooks` | Offline procedures/evidence index | 0 | 30m / N/A | Independent offline copy and versioned evidence | Independent access; order 0 | `platform-v1` | `NOT TESTED` | UNTESTED |
| `inference-api` | Customer-facing inference | 0 | 60m / 5m | Rebuild from Git; validate model/data before cutover | All required dependencies; order 11 | `model-release-v1` | `NOT TESTED` | UNTESTED |

For each real entry, fill in owners, approval, MTD source, actual test date, measured RTA/RPA, and a stable evidence reference. Use `UNTESTED`, `PASS`, or `GAP` consistently: `UNTESTED` means no acceptable test evidence; `PASS` means the most recent valid drill met the stated acceptance criteria; `GAP` means a target or control failed. An exception requires an owner, rationale, compensating control, expiry, and approver.

**Per-component vs end-to-end objectives.** A service's RTO cannot be shorter than a required hard dependency's recovery path unless a tested alternative or degraded mode removes that dependency. The end-to-end clock includes critical-path provisioning, data restoration, application start, verification, and cutover; some work can overlap, so model the dependency graph rather than blindly summing all durations. For state that must agree, an end-to-end RPO is not always the maximum or minimum of individual RPOs. Define consistency groups, common transaction/event IDs, queue offsets, replay windows, and reconciliation rules.

### C. Achievable RPO calculator (Python standard library)

This calculator is deliberately conservative and simple. It estimates a time window from declared inputs; it does **not** prove a backup is usable or provide a guarantee. Periodic backup worst-case loss can approach the backup interval plus completion/copy delay when a failure occurs just before the next recoverable copy. WAL and asynchronous replication use the measured age/lag of the last durable recoverable point supplied by the operator. Queue replay depends on source retention and offset/checkpoint semantics. Logical corruption needs a clean point before corruption; latest replication point may be unusable.

Save as `rpo_estimator.py`:

```python
#!/usr/bin/env python3
"""Transparent RPO-window estimator; estimates are not guarantees."""
import argparse


def estimate_rpo(mechanism: str, cadence_minutes: float = 0,
                 completion_delay_minutes: float = 0, measured_lag_minutes: float = 0,
                 retention_minutes: float | None = None,
                 corruption_age_minutes: float | None = None) -> tuple[float, str]:
    valid = {"periodic", "wal", "async-replication", "queue-replay", "logical-corruption"}
    if mechanism not in valid:
        raise ValueError(f"mechanism must be one of {sorted(valid)}")
    for name, value in (("cadence_minutes", cadence_minutes),
                        ("completion_delay_minutes", completion_delay_minutes),
                        ("measured_lag_minutes", measured_lag_minutes)):
        if value < 0:
            raise ValueError(f"{name} must be >= 0")
    if mechanism == "periodic":
        if cadence_minutes <= 0:
            raise ValueError("periodic mechanism requires cadence_minutes > 0")
        return cadence_minutes + completion_delay_minutes, "upper planning window; verify last durable copy and completion"
    if mechanism in {"wal", "async-replication"}:
        return measured_lag_minutes, "operator-supplied age/lag of last durable recoverable point; not a guarantee"
    if mechanism == "queue-replay":
        if retention_minutes is None or retention_minutes < 0:
            raise ValueError("queue-replay requires retention_minutes >= 0")
        if measured_lag_minutes > retention_minutes:
            raise ValueError("measured lag exceeds retained source history; replay point may be unavailable")
        return measured_lag_minutes, "valid only if source history, offsets, and replay semantics are verified"
    if retention_minutes is None or retention_minutes < 0:
        raise ValueError("logical-corruption requires retention_minutes >= 0")
    if corruption_age_minutes is None or corruption_age_minutes < 0:
        raise ValueError("logical-corruption requires corruption_age_minutes >= 0")
    if retention_minutes < corruption_age_minutes:
        raise ValueError("retention is shorter than corruption age; clean point may no longer exist")
    return corruption_age_minutes, "illustrative age of corruption boundary; clean restore point and detection delay govern"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mechanism", required=True,
                   choices=["periodic", "wal", "async-replication", "queue-replay", "logical-corruption"])
    p.add_argument("--cadence-minutes", type=float, default=0)
    p.add_argument("--completion-delay-minutes", type=float, default=0)
    p.add_argument("--measured-lag-minutes", type=float, default=0)
    p.add_argument("--retention-minutes", type=float)
    p.add_argument("--corruption-age-minutes", type=float)
    p.add_argument("--target-minutes", type=float)
    a = p.parse_args()
    if a.target_minutes is not None and a.target_minutes < 0:
        p.error("--target-minutes must be >= 0")
    try:
        estimate, caveat = estimate_rpo(a.mechanism, a.cadence_minutes,
            a.completion_delay_minutes, a.measured_lag_minutes,
            a.retention_minutes, a.corruption_age_minutes)
    except ValueError as exc:
        p.error(str(exc))
    print(f"estimated_window_minutes={estimate:g}")
    if a.target_minutes is not None:
        print(f"target_minutes={a.target_minutes:g}")
        print(f"result={'PASS_ESTIMATE_ONLY' if estimate <= a.target_minutes else 'FAIL'}")
    print(f"caveat={caveat}")

if __name__ == "__main__":
    main()
```

Representative commands/output (not executed here):

```bash
python rpo_estimator.py --mechanism periodic --cadence-minutes 60 --completion-delay-minutes 8 --target-minutes 30
# estimated_window_minutes=68
# target_minutes=30
# result=FAIL
# caveat=upper planning window; verify last durable copy and completion

python rpo_estimator.py --mechanism wal --measured-lag-minutes 2.5 --target-minutes 5
# estimated_window_minutes=2.5
# target_minutes=5
# result=PASS_ESTIMATE_ONLY
# caveat=operator-supplied age/lag of last durable recoverable point; not a guarantee
```

Hand-check: periodic cadence 60 plus completion delay 8 gives a planning window of 68 minutes; it misses 30 minutes. WAL age 2.5 minutes is below 5 minutes, but passes only as an estimate until a restore demonstrates that the archive is durable, decryptable, and replayable. For queue replay, retention is a hard boundary; if the required source history has expired, a numeric lag does not make the point recoverable. For logical corruption, the corruption-age input is only a simplified boundary; detection latency and the available clean backup/point-in-time history must be assessed separately.

Automated tests (save as `test_rpo_estimator.py` beside the script):

```python
import unittest
from rpo_estimator import estimate_rpo

class RpoTests(unittest.TestCase):
    def test_periodic_adds_delay(self):
        self.assertEqual(estimate_rpo("periodic", 60, 8)[0], 68)
    def test_periodic_requires_positive_cadence(self):
        with self.assertRaises(ValueError): estimate_rpo("periodic")
    def test_negative_lag_rejected(self):
        with self.assertRaises(ValueError): estimate_rpo("wal", measured_lag_minutes=-1)
    def test_wal_uses_measured_recoverable_age(self):
        self.assertEqual(estimate_rpo("wal", measured_lag_minutes=2.5)[0], 2.5)
    def test_queue_requires_retention(self):
        with self.assertRaises(ValueError): estimate_rpo("queue-replay", measured_lag_minutes=2)
    def test_queue_lag_cannot_exceed_retention(self):
        with self.assertRaises(ValueError): estimate_rpo("queue-replay", measured_lag_minutes=20, retention_minutes=10)
    def test_corruption_requires_clean_history_window(self):
        with self.assertRaises(ValueError): estimate_rpo("logical-corruption", retention_minutes=30, corruption_age_minutes=60)
    def test_unknown_mechanism_rejected(self):
        with self.assertRaises(ValueError): estimate_rpo("magic")

if __name__ == "__main__": unittest.main()
```

Run with `python -m unittest -v`. The tests verify calculator behavior, not real backup tooling.

### D. RTO decomposition estimator

Model sequential phases on the critical path and clearly identify overlap. For a simple first estimate, the script below assumes the listed phases are sequential; if provisioning and data staging overlap, use a dependency graph and replace the sum with a critical-path calculation. Transfer duration is `data size ÷ measured effective throughput`; use matching units. For example, 12 GiB at an effective 0.2 GiB/min takes 60 minutes. Effective throughput should be measured under realistic compression, encryption, contention, and restore load. A single average can hide tail latency; with enough observations, use distributions and a conservative percentile or worst credible scenario.

Save as `rto_estimator.py`:

```python
#!/usr/bin/env python3
"""Sequential critical-path RTO estimator. Estimates are not observations."""
import argparse

PHASES = ("detection", "decision", "provisioning", "application_start",
          "verification", "traffic_cutover", "dns_ttl", "reconciliation")

def estimate_rto(data_gib: float, throughput_gib_min: float, phases: dict[str, float], growth: float = 1.0) -> tuple[dict[str, float], float]:
    if data_gib < 0 or throughput_gib_min <= 0 or growth <= 0:
        raise ValueError("data_gib must be >= 0; throughput and growth must be > 0")
    for name in PHASES:
        if phases.get(name, 0) < 0:
            raise ValueError(f"{name} must be >= 0")
    values = {name: float(phases.get(name, 0)) for name in PHASES}
    values["data_restore"] = data_gib * growth / throughput_gib_min
    total = sum(values.values())
    return values, total

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data-gib", type=float, required=True)
    p.add_argument("--throughput-gib-min", type=float, required=True)
    p.add_argument("--growth", type=float, default=1.0, help="data-size multiplier; use 10 for 10x")
    p.add_argument("--target-minutes", type=float, required=True)
    for name in PHASES: p.add_argument(f"--{name.replace('_','-')}", type=float, default=0)
    a = p.parse_args()
    phases = {name: getattr(a, name) for name in PHASES}
    try: values, total = estimate_rto(a.data_gib, a.throughput_gib_min, phases, a.growth)
    except ValueError as exc: p.error(str(exc))
    for name, minutes in values.items(): print(f"{name}_minutes={minutes:.2f}")
    gap = total - a.target_minutes
    print(f"estimated_rto_minutes={total:.2f}")
    print(f"target_minutes={a.target_minutes:.2f}")
    print(f"gap_minutes={gap:.2f}")
    print(f"result={'PASS_ESTIMATE_ONLY' if gap <= 0 else 'FAIL'}")

if __name__ == "__main__": main()
```

Representative command (not executed here):

```bash
python rto_estimator.py --data-gib 12 --throughput-gib-min 0.2 --growth 1 --target-minutes 90 \
  --detection 3 --decision 4 --provisioning 8 --application-start 4 \
  --verification 10 --traffic-cutover 3 --dns-ttl 5 --reconciliation 12
```

Expected arithmetic: data restore = 12 / 0.2 = 60 minutes; other phases total 49 minutes; estimate = 109 minutes; target = 90; gap = +19; result `FAIL`. With `--growth 10`, data restore becomes 600 minutes and the total becomes 649 minutes. This demonstrates why data growth can invalidate a strategy even when today's restore meets a target. DNS propagation may overlap with other phases in a real system; only count it separately if it is actually on the critical path.

Tests (save as `test_rto_estimator.py`):

```python
import unittest
from rto_estimator import estimate_rto, PHASES

class RtoTests(unittest.TestCase):
    def test_transfer_calculation(self):
        vals, total = estimate_rto(12, .2, {})
        self.assertAlmostEqual(vals["data_restore"], 60)
        self.assertAlmostEqual(total, 60)
    def test_10x_growth(self):
        vals, _ = estimate_rto(12, .2, {}, growth=10)
        self.assertAlmostEqual(vals["data_restore"], 600)
    def test_phases_added(self):
        vals, total = estimate_rto(1, 1, {"detection": 2, "verification": 3})
        self.assertEqual(total, 6)
    def test_zero_data(self):
        vals, total = estimate_rto(0, 1, {})
        self.assertEqual(total, 0)
    def test_zero_throughput_rejected(self):
        with self.assertRaises(ValueError): estimate_rto(1, 0, {})
    def test_negative_data_rejected(self):
        with self.assertRaises(ValueError): estimate_rto(-1, 1, {})
    def test_negative_phase_rejected(self):
        with self.assertRaises(ValueError): estimate_rto(1, 1, {"verification": -1})
    def test_nonpositive_growth_rejected(self):
        with self.assertRaises(ValueError): estimate_rto(1, 1, {}, growth=0)

if __name__ == "__main__": unittest.main()
```

Run `python -m unittest -v`. For production planning, add provisioning variance, cold-start effects, key/identity recovery, throttling, consistency validation, retries, and explicit dependencies. Estimates should be compared against actual repeated measurements and the target, not treated as proof.

### E. Dependency-implied objectives and recovery order

A dependency graph is directed from a service to the components it requires. The recovery order is the reverse of that relation: recover dependencies before their consumers. The following standard-library script detects unknown dependencies and cycles, returns a valid dependency-first order, computes a simple sequential critical path, and flags a declared RTO shorter than the time implied by hard dependencies. It also calls out consistency groups for human review; it does not compute cross-system RPO automatically.

Save as `dependency_recovery.py`:

```python
from collections import defaultdict


def recovery_plan(graph: dict[str, list[str]], durations: dict[str, float], declared_rto: dict[str, float]):
    nodes = set(graph)
    for deps in graph.values(): nodes.update(deps)
    unknown = sorted({d for deps in graph.values() for d in deps if d not in graph})
    if unknown: raise ValueError(f"unknown dependency nodes: {unknown}")
    for n, duration in durations.items():
        if n not in nodes: raise ValueError(f"duration supplied for unknown node: {n}")
        if duration < 0: raise ValueError(f"negative duration for {n}")
    # DFS follows dependency edges, so dependencies are appended first.
    state, stack, order = {}, [], []
    def visit(node):
        mark = state.get(node, 0)
        if mark == 2: return
        if mark == 1:
            start = stack.index(node)
            raise ValueError("dependency cycle: " + " -> ".join(stack[start:] + [node]))
        state[node] = 1; stack.append(node)
        for dep in graph[node]: visit(dep)
        stack.pop(); state[node] = 2; order.append(node)
    for node in sorted(graph): visit(node)
    finish = {}
    for node in order:
        finish[node] = durations.get(node, 0) + max((finish[d] for d in graph[node]), default=0)
    violations = {n: (declared_rto[n], finish[n]) for n in declared_rto
                  if n in finish and declared_rto[n] < finish[n]}
    return order, finish, violations

if __name__ == "__main__":
    graph = {
        "inference": ["model-registry", "identity", "dns"],
        "model-registry": ["database", "artifacts", "identity"],
        "database": ["keys", "storage"],
        "artifacts": ["object-store", "keys"],
        "identity": ["keys"], "dns": [], "keys": [],
        "storage": [], "object-store": [],
    }
    durations = {"keys": 5, "storage": 10, "object-store": 12, "database": 20,
                 "artifacts": 15, "identity": 8, "dns": 4,
                 "model-registry": 10, "inference": 6}
    order, finish, violations = recovery_plan(graph, durations, {"inference": 40, "model-registry": 25})
    print("dependency_first_order=" + " -> ".join(order))
    print("implied_minutes=" + str(finish["inference"]))
    print("rto_violations=" + repr(violations))
```

Representative output will depend on deterministic sorting but should place `keys`, `storage`, and `object-store` before dependent services; `inference` has an implied path of 46 minutes under the example durations and therefore violates a 40-minute target. The exact order of independent nodes can differ without being wrong.

Tests:

```python
import unittest
from dependency_recovery import recovery_plan

class DependencyTests(unittest.TestCase):
    def test_dependency_first_order(self):
        order, finish, _ = recovery_plan({"app": ["db"], "db": []}, {"app": 2, "db": 3}, {})
        self.assertLess(order.index("db"), order.index("app"))
        self.assertEqual(finish["app"], 5)
    def test_unknown_dependency(self):
        with self.assertRaisesRegex(ValueError, "unknown dependency"):
            recovery_plan({"app": ["missing"]}, {}, {})
    def test_cycle_path_reported(self):
        with self.assertRaisesRegex(ValueError, "dependency cycle"):
            recovery_plan({"a": ["b"], "b": ["a"]}, {}, {})
    def test_rto_violation(self):
        _, _, violations = recovery_plan({"app": ["db"], "db": []}, {"app": 2, "db": 5}, {"app": 6})
        self.assertIn("app", violations)
    def test_negative_duration(self):
        with self.assertRaises(ValueError): recovery_plan({"db": []}, {"db": -1}, {})

if __name__ == "__main__": unittest.main()
```

Run `python -m unittest -v`. A dependency graph is only as good as its declarations: unknown hidden dependencies, conditional paths, shared bootstrap services, and parallelizable work must be discovered during drills. RPO cannot be calculated by taking a graph maximum unless the state semantics make that valid. For example, database transaction 900 may reference object manifest 42 while a queue checkpoint has already advanced beyond the event that created it. Use consistency-group markers, event IDs, offsets, and explicit reconciliation rules.

### F. Safe RTO/RPO measurement lab

Use the M05 local PostgreSQL/CloudNativePG and object-store setup only if it already works. Exact custom-resource fields and commands depend on the installed version and M05 lab; verify them against the local manifests and official documentation `[VERIFY]`. If that environment is unavailable, use a tool-neutral dataset and timing worksheet rather than improvising destructive commands.

1. **Preflight.** Confirm current Kubernetes context and namespace manually; print them and stop if they are not the lab-specific context/namespace. Use a dedicated namespace/name with an unmistakable `lab-dr-` prefix and a fresh synthetic dataset. Never use a broad delete command or production-like endpoint. Keep the runbook and evidence outside the resources you will remove.
2. **Create deterministic records.** Insert synthetic rows with monotonically increasing `event_id` and a UTC `created_at`. Include a known row count and aggregate. Create a tiny object file and a manifest containing its SHA-256 hash. Do not use real customer or sensitive data.
3. **Record the baseline.** Save failure-simulation timestamp, latest known-good event ID, object manifest hash, database row count, aggregate, and exact tool versions. Use UTC consistently.
4. **Back up.** Run the supported M05 backup/PITR or logical export procedure. Save command output and backup metadata. Confirm the backup is present and non-empty; do not treat file existence as integrity proof.
5. **Measure throughput.** Restore a representative tiny copy into an isolated target, record bytes transferred and elapsed time, then calculate effective throughput. Keep this measurement separate from a production estimate.
6. **Simulate loss safely.** Stop or remove only the specifically labelled throwaway workload/data after a context/name confirmation. Prefer an isolated restore target over deletion. If the exact safe operation is uncertain, do not execute it; simulate the loss by making the original unavailable to the test client.
7. **Restore.** Restore into a new isolated target. Record phase start/end times: provisioning, data transfer, application start, verification, cutover (if simulated), and reconciliation. Do not restore over the source.
8. **Verify.** Query row count, aggregate, latest valid event ID and referential integrity; compare the object SHA-256 hash to the manifest; run a small application smoke test. A mismatch is a failed recovery even if the database reports healthy.
9. **Calculate.** `RTA = agreed end timestamp - selected start timestamp`. `RPA = failure timestamp - timestamp of latest valid recovered event` for the time-based example; also record event-ID/offset gaps and duplicates. Compare each value to the illustrative target and mark pass/fail.
10. **Clean up.** Preserve evidence outside the lab resources, confirm the selected resources carry the lab label/name, and remove only those resources. If recovery fails, retain the isolated failed target for diagnosis and rebuild the lab from its known-good manifests; do not risk the original source.

**Example evidence table (fill with your own measurements):**

| Phase | Start UTC | End UTC | Duration seconds | Evidence reference |
|---|---|---|---:|---|
| Provision target | | | | |
| Restore database | | | | |
| Restore object data | | | | |
| Start application | | | | |
| Verify data/model | | | | |
| Cut over traffic (if included) | | | | |
| Reconcile/catch up | | | | |

The lab is a workflow and measurement exercise only. A single laptop shares hardware and failure domains; its measured times do not establish a production or regional-failure guarantee.

### G. Strategy selection

| Strategy | Benefit | Cost/complexity | Risk | Choose when |
|---|---|---|---|---|
| Backup and restore | Lowest steady-state footprint; clean historical points can protect against logical corruption | Longest recovery; restore throughput and bootstrap dependencies dominate | Backup may be unusable or too old; rebuild may miss undocumented state | RTO tolerates rebuild/restore and RPO is met by tested backup cadence/log retention |
| Pilot light | Critical core and data protection are prepared; scale up remaining capacity on demand | Ongoing minimal resources plus automation and regular tests | Cold dependencies, quota, secrets, or drift delay recovery | Moderate RTO with lower cost than full standby |
| Warm standby | Reduced startup time and more pre-provisioned capacity | Continuous capacity, replication, patching, and drift management | Replication may copy corruption; standby may be under-sized | Tighter RTO justified by business impact and tested failover path |
| Multi-site active/active or hot standby | Potentially fast continuity and capacity already running | Highest complexity, data-consistency burden, traffic fencing, and cost | Split brain, cross-site dependencies, inconsistent writes, correlated failures | Very tight objectives justify engineering and operating cost; failure modes are continuously tested |

Decision record must state the failure classes in scope, target RTO/RPO, data consistency model, identity/key recovery path, capacity assumptions, cutover authority, fencing/rollback procedure, test evidence, residual risks, and owner approval. Never choose active/active merely because it sounds resilient.

## 1.5 Level 3 — Advanced

### Design for consistency, security, scale, and cost

**Consistency first.** Identify authoritative versus derived state. A database and object store may require a common export marker, manifest version, transaction boundary, or reconciliation process. A queue checkpoint is meaningful only relative to retained source events and idempotent consumer behavior. Model registry metadata must point to the exact artifact digest that is restored and verified. When a single atomic snapshot across systems is impossible, define an application-level recovery protocol: freeze writes, capture markers, restore each component, reconcile missing/extra events, run invariant checks, then authorize writes and traffic.

**Dependency order.** Recovery commonly follows: offline runbooks and authority → identity/trust roots and keys → network/DNS access → storage/platform bootstrap → database and object data → registry and signed images → secrets/workload identity → applications → verification → traffic → backlog reconciliation. The exact order varies. Circular dependencies are a warning: for example, Vault needs a platform that needs credentials stored in Vault. Break the cycle with a minimal, protected bootstrap kit and tested offline custody procedures. M03's etcd mechanics, M07's Terraform-state recovery, M08's GitOps rebuild, and M09's Vault/key recovery are prerequisites; this unit coordinates them rather than re-teaching their mechanics.

**Security.** Use distinct backup identities and limit normal workloads to write only what they need; backup writers should not be able to change retention policy or delete historical copies. Store keys and recovery instructions independently from the system they unlock. Validate signature/provenance for restored container and model artifacts. After suspected compromise, do not blindly restore credentials or binaries from the compromised environment: rebuild cleanly, rotate credentials, preserve forensic evidence as appropriate, and validate trust before cutover. A checksum detects accidental change only if the expected checksum is protected independently; it does not establish authenticity by itself.

**Scale and capacity.** Estimate restore time from measured effective throughput and total bytes, including indexes, metadata, WAL, compression/decompression, encryption, and verification overhead. Measure with realistic concurrency and cold-cache conditions. Consider data growth, object count, API throttling, small-file overhead, and whether the recovery site has sufficient CPU, memory, storage, network, quotas, and registry capacity. A second cluster without capacity parity is a diagram, not a ready recovery site. Do not quote costs without actual assumptions and pricing inputs; compare resource units and operational burden.

### Trade-off table

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Frequent immutable backups + PITR | Historical clean recovery points and strong protection from deletion | Storage, archive management, key custody, restore-test effort | Missing/corrupt WAL or key loss breaks recovery chain | Logical corruption and data integrity are major concerns |
| Async replication plus independent backup | Lower potential loss during some failures plus historical rollback | Replication infrastructure and separate backup pipeline | Lag/in-flight writes and replicated corruption remain | Need faster failover but still require clean historical points |
| Rebuild from Git/IaC | Reduces dependence on fragile platform snapshots; repeatable configuration | Requires complete, pinned, accessible configuration and bootstrap credentials | Hidden/manual state or inaccessible repositories block rebuild | Infrastructure is declarative and stateful data is backed separately |
| Restore platform snapshot | May accelerate recovery of platform metadata | Snapshot compatibility, encryption keys, version coupling | Snapshot shares failure domain or is stale/inconsistent | Tested restore is compatible with the target version and environment |
| Warm standby | Reduces provisioning/start time | Continuous capacity and drift controls | Standby may not be usable under real load | RTO target and impact justify it |

### Verification: avoid false confidence

Use layered checks rather than a single green status:

1. **Artifact integrity:** size, hashes, object manifest, backup metadata, signature/provenance where applicable.
2. **Restore mechanics:** database starts, archive chain is complete, object files are readable, keys can decrypt the backup.
3. **Data correctness:** row counts, aggregates, referential-integrity queries, event-ID continuity, duplicate detection, checkpoint/offset consistency.
4. **Application correctness:** authenticated smoke tests, representative inference, expected model digest/version, read/write behavior under the agreed mode.
5. **Operational readiness:** alerting and dashboards restored, runbook reachable, access and escalation work, backups resume on the recovered primary.
6. **Security posture:** credentials rotated where necessary, backup immutability and least privilege remain effective, restored artifacts are trusted.

The evidence should include test inputs, commands or query identifiers, timestamps, expected/actual values, pass/fail, tool versions, and reviewer. A test suite that only checks whether a Pod is Running can produce a false pass.

### Exercise: defend a recovery design

Scenario `[ILLUSTRATIVE]`: the inference API has a 60-minute RTO and 5-minute RPO; PostgreSQL restores in 45 minutes, object/model artifacts restore in 20 minutes, identity and trust roots take 15 minutes, verification takes 12 minutes, and traffic cutover takes 5 minutes. Some work can overlap, but identity is a prerequisite for protected artifact access and verification is a prerequisite for cutover.

Write a one-page decision record answering:

- What is the critical path? Which tasks can overlap, and what evidence supports that assumption?
- Does a backup-and-restore design meet 60 minutes? If not, what is the smallest defensible architecture or process change?
- What consistency markers link database records, object manifests, model registry metadata, and queue offsets?
- How does the plan recover if the primary Vault or identity plane is unavailable?
- What test would reveal a replica that has copied logical corruption?
- What residual risk is accepted, by whom, and until what expiry date?

A strong answer shows calculations, dependencies, evidence, and trade-offs; it does not merely select “warm standby.”

## 1.6 Level 4 — Expert

### Failure scenarios and DR-process failure

| Symptom | Hypothesis | Test | Possible root cause | Fix and prevention |
|---|---|---|---|---|
| Backup job green; restore fails | Backup incomplete or dependent metadata missing | Restore into isolated clean target; inspect manifests and logs | Success signal measures upload, not end-to-end recoverability | Automated restore tests, integrity gates, alert on restore-test failure |
| Backup exists but cannot decrypt | Key custody failed with primary platform | Restore using the documented independent key path with primary key service unavailable | Key stored only in the system being recovered | Escrow and test key custody; rotate and audit access |
| RTO missed despite quick data restore | Bootstrap dependency or verification dominates | Time each phase and inspect dependency graph | Missing registry, identity, DNS, quota, or cutover approval | Reorder recovery, remove circular dependency, pre-authorize safe decisions |
| RPO appears to pass but records are wrong | Data points are inconsistent or business events are missing | Compare event IDs, offsets, transaction markers, object hashes | Components restored independently | Consistency groups and reconciliation tests; fail closed on invariant violations |
| Backup deleted during incident | Workload credential has excessive privilege | Negative-test deletion with a disposable object and scoped identity | Backup control plane shares credentials with workloads | Separate accounts/roles, immutable retention, alerting, independently administered copy |
| DR cluster cannot pull images | Registry or signing trust unavailable | Restore from mirror and verify digest/signature without primary registry | No independent image path or missing verification key | Mirror signed artifacts, escrow trust roots, test offline bootstrap |
| Recovery process stalls when monitoring is down | Monitoring is a hidden dependency | Run a drill with primary observability unavailable; use independent minimal signals | Metrics/logging were not included in recovery order | Offline runbook, minimal recovery dashboard/alerts, external status communication |
| Restored service fails after traffic cutover | Smoke tests did not represent real requests | Canary requests and invariant tests before broad cutover | Process health confused with functional correctness | Gate cutover on verified synthetic transactions and explicit rollback criteria |
| DR site is too small | Capacity assumption was never tested | Load restore and catch-up at representative scale | Quota, disk, CPU, or network shortfall | Capacity parity check, measured growth model, reservations or alternate strategy |
| Drill passes only with expert present | Runbook relies on undocumented knowledge | Cold-read exercise by a different operator | Procedure is ambiguous or credentials inaccessible | Runbook usability test, role rotation, evidence and contact list stored independently |

### Policy as code and readiness scoring

Represent recovery objectives and minimum controls in versioned machine-readable files. A policy validator should fail a change when a critical system has no owner, no approved objective, no named recovery mechanism, no dependency list, no recent test, or an expired exception. A drill report should be generated from timestamps and test outputs rather than hand-edited summary claims. Keep policy and evidence in a repository or storage location that remains accessible during a platform outage; the DR plan itself must be backed up and reachable when the platform is down.

A simple readiness score can weight controls by risk, but the score must not hide a critical failure. Example `[ASSUMPTION]`: score each control 0 (absent), 1 (documented only), 2 (tested once), 3 (repeatedly tested with evidence); weight trust-root recovery, immutable backups, and critical data verification more heavily. Always publish critical blockers separately—for example, “overall score 82/100, but key restore untested; Tier 0 recovery is not ready.” Do not allow a high average to compensate for an unrecoverable trust root.

### Governance and operating cadence

- **Ownership:** every system has a business owner for impact/objectives and a technical owner for mechanisms, tests, and remediation.
- **Approval:** objective changes and risk exceptions are recorded, dated, and reviewed; exceptions expire rather than becoming permanent by silence.
- **Cadence:** choose frequency based on criticality, change rate, threat model, and prior failures. Test after major changes to database versions, storage, identity, encryption, registry, deployment controllers, or backup tooling. The organization must define the cadence; this lesson does not prescribe a universal interval.
- **Drill types:** table-top for decisions and communications; restore test for data and tooling; platform rebuild for configuration/trust-root recovery; failover/failback for traffic and fencing; destructive-attack simulation using only harmless, isolated lab resources.
- **Evidence:** record RTA/RPA, verification outcomes, version baselines, decision points, deviations, and remediation owners. Keep secrets out of evidence bundles; hash or sign evidence where appropriate and protect the reference copy independently.
- **Postmortem:** compare actual impact with the BIA, targets with measured outcomes, identify system/process causes without blame, assign corrective actions, and re-test at least the important fixes.
- **Scope and assurance:** distinguish what was tested (single node, logical corruption, local restore) from what was not (real regional loss, provider control-plane outage, complete account compromise). A simulation cannot support a claim outside its failure domain.

### Platform differences and edge cases

- **kind / laptop:** excellent for learning repeatable mechanics and evidence capture; shared CPU, memory, disk, and host failure domain limit realism. Measure resource footprint and sequence components rather than running every stack simultaneously on an 8 GB machine.
- **WSL2:** filesystem, networking, clock, and host-resource behavior can differ from native Linux; record the environment and verify relevant behavior rather than generalizing one result.
- **Managed services:** provider restore guarantees, PITR windows, snapshots, identity, quotas, and region semantics vary by service and configuration. Read current official documentation and run account-specific tests; do not infer provider behavior from a local simulation.
- **Version changes:** database operators, backup clients, Kubernetes APIs, storage plugins, and encryption formats can change. Pin and record versions; test N-1/upgrade compatibility where required.
- **Logical corruption:** the best recovery point may be older than the latest backup; include detection latency and clean-point search time in planning.
- **Ransomware/destructive attack:** restoring quickly into the compromised trust environment can reintroduce compromise. Isolate, preserve evidence, rotate credentials, validate artifacts, and re-establish trust before opening traffic.
- **Failback:** failover is not complete recovery. Plan reconciliation of writes accepted during the event, fencing of the former primary, reverse replication or data movement, and a separately approved return-to-primary procedure.

## 1.7 SRE lens

### SLIs and SLOs for protection and recovery

Track protection capability as measurable indicators, not as a single “backup healthy” dashboard:

- **Backup success ratio:** successful eligible backup operations divided by scheduled/expected operations over a window.
- **Backup age:** time since the latest *verified recoverable* point, not merely latest job success; compare with the RPO target.
- **Restore-test pass rate:** successful restore tests divided by attempted tests, with failure reasons retained.
- **Measured RTA vs target:** actual elapsed time with defined clock boundaries; show percentile/distribution where enough drills exist.
- **Measured RPA vs target:** latest valid recovered point relative to failure boundary; include event/offset gaps.
- **Replication/archive lag:** useful signal, but not a substitute for restore or logical-corruption tests.
- **Drill recency:** elapsed time since a valid drill under a comparable configuration.
- **Evidence completeness:** required timestamps, integrity outputs, versions, approvals, and postmortem present.
- **Recoverability coverage:** proportion of in-scope state classes with a documented, tested mechanism.

Define alert thresholds from the approved objectives and normal behavior. For example, alert when the latest verified recovery point is older than the permitted RPO or when restore-test evidence becomes stale. A backup pipeline can be green while the recovery point is too old; therefore alert on age and verification, not only job status.

### Failure modes and blast radius

Ask “what becomes unrecoverable if this fails?” for each dependency: object store, database, key escrow, registry, Git mirror, identity provider, DNS account, CI credentials, and the evidence repository. A shared admin identity or shared storage account can turn a local failure into a platform-wide failure. Correlated dependencies—same account, same host, same key store, same network, same administrator—must be visible in the architecture and risk register.

### Runbook snippet

1. **Trigger:** a critical service is unavailable or state is suspected corrupt beyond normal HA recovery.
2. **Decide:** incident commander confirms scope, captures T0, assigns roles, and chooses failover versus clean restore; do not fail over blindly to a replica that may contain corruption.
3. **Execute:** use the approved dependency order; validate target context, keys, backup point, capacity, and artifact trust before restore/cutover.
4. **Verify:** run integrity, consistency, security, and functional checks; record measured RTA/RPA and evidence references.
5. **Communicate:** announce what is restored, what remains degraded, data-loss bounds, and next update time.
6. **Follow up:** resume protection on the recovered primary, reconcile backlog, preserve evidence, write a blameless postmortem, and track fixes to verified closure.

### Cost and capacity notes

Record storage growth, retained versions, WAL volume, object count, restore throughput, CPU/memory during decompression and verification, network limits, and required recovery-site capacity. Compare resource units and operational complexity; do not quote prices without actual pricing inputs. The cheapest backup is not necessarily the lowest-cost recovery if a long outage, manual rebuild, or data re-creation dominates. Conversely, active/active capacity can be unjustified if the BIA accepts a longer recovery window.

## 1.8 Security lens

| Threat | Control | Concrete negative test / evidence |
|---|---|---|
| Ransomware or destructive workload | Independent immutable/versioned copy; separate credentials; clean rebuild path | In a disposable bucket/lab identity, attempt to delete a protected test object and confirm denial or retention behavior; never test against real data. |
| Backup credential theft | Least privilege; separate backup administration; short-lived credentials where available | Use a scoped workload identity to attempt changing retention or deleting historical backup data; expect denial and an auditable event. |
| Backup tampering/deletion | Protected retention, independent audit logs, separate administrative boundary | Attempt a harmless modification to a disposable protected object and verify control behavior and alerting. Exact object-lock semantics are provider/configuration-specific `[VERIFY]`. |
| Secrets leaked into backups/evidence | Secret scanning, restricted access, encrypted storage, redaction | Seed a fake canary secret into a disposable test fixture; confirm the scanner catches it and evidence output does not expose real secrets. |
| Insider threat | Separation of duties, approval, immutable audit, independent copy | Confirm a normal operator cannot both alter backup retention and erase the independent copy; inspect audit records. |
| Key loss | Escrowed recovery material and documented custodians | Conduct a controlled restore with the primary key service unavailable, using only the approved lab escrow path. Never print keys. |
| Compromised signed artifact | Digest/signature/provenance verification; fail closed | Replace a disposable artifact with different bytes and confirm verification rejects it before serving. |
| Stale credentials after recovery | Credential rotation and trust re-binding | Confirm old lab credential is rejected after rotation and new credential works; document owner and rollback. |
| DR plan inaccessible during outage | Independent offline/runbook copy and tested access | Cold-read the runbook without using the primary platform or its identity provider. |

Security controls have limits. Immutability does not prove backup correctness; encryption does not protect a key stored beside the ciphertext; a signature is only useful if its verification key and trust policy are sound; and a backup does not prove the restored system is clean. Treat security recovery as a clean-trust problem, not only a data-copy problem.

## 1.9 Production checklist

- [ ] RTO start and end events are explicitly documented, approved, and used consistently in reports.
- [ ] RPO definition includes the failure boundary and identifies the valid business event/transaction/offset marker.
- [ ] BIA scores downtime and data-loss impact separately, with explicit criteria and named business owner.
- [ ] RTO/RPO/MTD and assumptions are approved; exception expiry and review date are populated.
- [ ] Recovery objectives register covers all critical state: database, object data, model registry/artifacts, queue/checkpoints, orchestrator, Git/IaC, identity/secrets, registry, observability, DNS, and runbooks.
- [ ] Hard dependencies, recovery order, circular dependencies, and consistency groups are recorded.
- [ ] Backup age is compared with RPO; backup job success alone is not used as readiness evidence.
- [ ] A clean restore has verified integrity, correctness, application function, security, and operational readiness.
- [ ] Restore throughput and each critical RTO phase have measured values and evidence references.
- [ ] Data growth, archive lag, source retention, and queue replay windows have been included in estimates.
- [ ] Workload credentials cannot delete or alter independent recovery copies; negative tests and audit evidence exist.
- [ ] Keys and trust roots can be recovered without relying on the primary system they unlock.
- [ ] Restored container/model artifacts are checked against expected digests and trust policy.
- [ ] Traffic cutover and rollback/fencing authority are documented and tested.
- [ ] Minimum observability and offline runbooks are available during a platform outage.
- [ ] The DR plan and evidence index are stored independently and can be accessed during an outage.
- [ ] Drill reports distinguish targets, estimates, and observations; gaps have owners and due dates.
- [ ] Laptop/`kind` limitations and untested failure domains are stated; no regional assurance is claimed from a local lab.

## 1.10 Hands-on lab set

All labs are safe to rerun only when the learner follows the preflight and isolation requirements. **Footprint:** Python-only labs are negligible; optional PostgreSQL/object-store labs require a tiny dataset and an already-working M05 setup. Measure yours. **Laptop-fidelity caveat for every lab:** two clusters on the same laptop are not two regions and share failure domains.

| ID | Goal and steps | Expected evidence | Cleanup / safety plan | Stretch |
|---|---|---|---|---|
| `M13-U1-LAB-01` | Calculate RPO for 5 timestamped failure/backup pairs; compare with a target and label each result. | `rpo-calculations.csv`, assumptions, representative script output. | No destructive action. Store files outside the test data folder. | Add event IDs and identify duplicate/gap risk. |
| `M13-U1-LAB-02` | Run the RPO calculator for periodic, WAL, async replication, queue replay, and logical-corruption examples; run all tests. | `rpo_estimator.py`, `test_rpo_estimator.py`, captured test output, limitations note. | Python-only; no production connection. | Add a JSON input format and schema validation. |
| `M13-U1-LAB-03` | Estimate RTO with measured tiny-file restore throughput; test 1× and 10× data growth. | `rto_estimator.py`, tests, phase timing worksheet, gap analysis. | Use synthetic files only; delete only a dedicated temp directory after checking its exact path. | Add repeated trials and p50/p95 estimates. |
| `M13-U1-LAB-04` | Build a dependency graph for database, keys, object store, registry, model registry, and inference; detect cycle and RTO violation examples. | `dependency_recovery.py`, test output, graph diagram, defended recovery order. | No cluster changes. | Add explicit parallelism and critical-path scheduling. |
| `M13-U1-LAB-05` | Use M05's isolated lab to create synthetic rows/object manifest, backup, restore into a separate target, and verify hashes/aggregates. | Phase timings, row counts, event IDs, hashes, RTA/RPA worksheet, post-lab notes. | **Destructive:** only throwaway `lab-dr-` resources. Verify context and names before any removal; prefer isolated restore over deleting source. If context is ambiguous, stop. Preserve evidence outside lab resources and rebuild from manifests if needed. | Repeat with a deliberately older clean point and compare recovery choices. |

### Lab acceptance gates

A lab passes only if the evidence is reproducible and its limits are stated. For the restore lab, require: baseline markers recorded before the simulated failure; isolated restore target; row count and aggregate match expected values; object hash matches the independent manifest; latest valid event/offset is recorded; RTA uses the chosen clock boundaries; RPA is calculated against the failure boundary; no secrets appear in artifacts; cleanup targets are proven to be lab-only. A failure is useful evidence: preserve it, identify the cause, remediate, and rerun rather than editing the result to pass.

## 1.11 Self-check questions

1. **A daily backup finished at 01:00; failure is at 20:00. What is the simple time-based RPA if the backup is the latest valid point?** Answer: 19 hours. Why tempting wrong answer: “24 hours” confuses schedule interval with observed point age.
2. **A Pod becomes Ready but authenticated inference fails because its model artifact is unavailable. Has RTO ended?** Answer: no, if the agreed functional criterion includes successful inference. Why tempting: readiness is an easy metric but may not represent user-visible behavior.
3. **What is the difference between RTO and RTA?** Answer: RTO is the target; RTA is observed elapsed recovery time under documented boundaries. Why tempting: both are durations, but one is prospective and one measured.
4. **Does a low asynchronous replication lag prove a clean recovery point after accidental deletion?** Answer: no; deletion can be replicated. Why tempting: low lag is mistaken for protection from logical errors.
5. **When does a five-minute-old recovery point fail a five-minute RPO?** Answer: when the true age exceeds five minutes under precise timestamps, or when the point is not valid/consistent/recoverable. Why tempting: rounded displays can conceal boundary failure.
6. **Why record outage start and declaration separately?** Answer: to avoid shifting the clock and under-reporting impact. Why tempting: declaration is easier to observe but may happen later.
7. **Can RTO be less than MTD?** Answer: it is a common planning expectation so recovery completes before disruption becomes intolerable; terminology and exact relationship depend on the adopted framework and business definitions. Why tempting: treating a planning relationship as a universal theorem.
8. **What must be added to a simple restore-throughput estimate?** Answer: provisioning, key/identity recovery, application start, verification, cutover, DNS where on critical path, and catch-up/reconciliation. Why tempting: bytes divided by throughput is measurable, but it is only one phase.
9. **Why can independently restoring a database and object store to their newest points be wrong?** Answer: the database may reference objects or manifests absent from that object-store point. Why tempting: each component's newest copy seems individually best.
10. **What does a consistency group provide?** Answer: a way to define related state that must be restored to compatible points or reconciled. Why tempting: individual health checks do not establish cross-system correctness.
11. **When is “re-derive” a reasonable RPO strategy?** Answer: when data is truly derived, authoritative sources and transformation versions are retained, and reprocessing time/capacity is acceptable. Why tempting: “derived” data may still be expensive or impossible to reproduce exactly.
12. **Why is an immutable backup not enough by itself?** Answer: it may be corrupt, incomplete, encrypted with a lost key, or impossible to restore in time. Why tempting: immutability protects retention, not usability.
13. **What should the recovery register contain beyond RTO/RPO?** Answer: owners, dependencies, mechanism, consistency group, last test, measured RTA/RPA, evidence, status, assumptions, exceptions, and expiry. Why tempting: targets alone do not show whether capability exists.
14. **How should disaster time count toward an SLO error budget?** Answer: according to the organization's written policy; there is no universal rule. Why tempting: teams often assume a convention is universal.
15. **What is the difference between WRT and RTO?** Answer: WRT covers verification/reconciliation/catch-up after technical restoration; exact boundaries must avoid gaps or double-counting. Why tempting: both may be part of the full time to business usability.
16. **Why can a local second cluster not prove regional resilience?** Answer: both clusters share laptop hardware and often power, network, disk, and host failure domains. Why tempting: separate cluster names look like separate sites.
17. **What does a queue replay test need to check?** Answer: source retention, offsets, checkpoint consistency, idempotency, ordering, duplicates/gaps, and catch-up capacity. Why tempting: an offset alone does not prove business correctness.
18. **Why measure throughput multiple times?** Answer: contention, cold caches, encryption, object count, and storage behavior vary; one average may hide slow tails. Why tempting: a single value makes the estimate easy to calculate.
19. **What should happen if a recovery key is stored only in the failed platform?** Answer: the recovery design has a circular dependency and is not ready; establish and test independent custody. Why tempting: normal operations can access the key, masking bootstrap failure.
20. **What is the right response when a drill misses its RTO?** Answer: record the gap honestly, identify critical-path causes, assign remediation, and re-test. Why tempting: teams may be tempted to redefine the endpoint after the fact.

## 1.12 Evidence artifacts

Save a small, reviewable evidence bundle with no secrets:

```text
evidence/M13-U1/
├── README.md                       # scope, environment, versions, limitations
├── bia-lite.csv                    # downtime/data-loss impact and rationale
├── stakeholder-objectives.yaml     # approvals, assumptions, exceptions
├── recovery-objectives-register.csv
├── recovery-dependency-graph.mmd    # or .txt ASCII graph
├── rpo_estimator.py
├── test_rpo_estimator.py
├── rpo-test-output.txt
├── rto_estimator.py
├── test_rto_estimator.py
├── rto-test-output.txt
├── dependency_recovery.py
├── test-dependency-output.txt
├── phase-timings.csv                # measured, not estimated, where available
├── integrity-results.txt            # row counts, aggregates, hashes, smoke tests
├── rta-rpa-calculation.md           # exact clock boundaries and calculations
├── gap-analysis.md                  # target vs estimate vs measured result
└── drill-report.md                  # findings, limitations, remediation owners
```

Every result must be labelled `MEASURED`, `ESTIMATED`, `ILLUSTRATIVE`, or `ASSUMPTION`. Include timestamps and timezone, failure and recovery-point markers, dataset size, throughput method, tool versions, verification commands/queries, pass/fail criteria, and reviewer. Do not include passwords, tokens, Vault contents, private keys, or real customer data. Hashing the bundle can show later change only if the reference hash is stored independently; a hash alone does not prove that the original result was correct.

## 1.13 Common interview and design-review questions

1. **How do you set RTO/RPO for a new data platform?**
   - **Model answer:** Start with a BIA involving business and technical owners. Score downtime and data-loss impact separately, identify authoritative versus derived state, determine whether data can be replayed/recomputed, map hard dependencies and consistency groups, estimate feasibility from measured restore and bootstrap times, negotiate residual risk/cost, then approve objectives in a register. Validate through restore/failover drills and report measured RTA/RPA separately from estimates.

2. **Why are backups and replication both needed?**
   - **Model answer:** Replication can reduce data loss and failover time for certain infrastructure failures, but it can copy logical corruption and deletion. Independent historical backups provide clean recovery points. The architecture should align each mechanism with failure classes and test both integrity and recovery time; neither mechanism alone covers every threat.

3. **How would you prove a five-minute RPO?**
   - **Model answer:** Define the failure boundary and business-event semantics, record durable backup/WAL/replication/offset positions, inject a controlled failure in isolated lab resources, restore to an isolated target, and verify the latest valid event/transaction plus cross-system consistency. Calculate point age without rounding away a failure. Repeat under relevant failure conditions and document limits; a configuration value or lag dashboard alone is not proof.

4. **A service has a 30-minute RTO, but its database restore takes 45 minutes. What do you do?**
   - **Model answer:** The current strategy cannot meet the target if the database is a hard sequential dependency. Confirm the target and measurement boundaries, measure restore variance and all critical-path phases, then compare options such as faster restore, pre-provisioned capacity, warm standby/replication plus independent backups, or an approved degraded mode. Present cost, consistency, security, and failure-mode trade-offs; seek explicit risk acceptance if the target cannot be met.

5. **How do you avoid false confidence from a successful DR drill?**
   - **Model answer:** Define the tested failure domain and acceptance criteria in advance; restore in isolation; verify artifact integrity, data invariants, application behavior, security, and operations; capture RTA/RPA and evidence; test dependencies and the DR process itself; use cold-read runbooks and repeat after material changes. State what was not tested. A local `kind` exercise cannot prove regional resilience.

## 1.14 Sources and verification notes

This lesson is aligned to the supplied M13 module prompt and its cross-module boundaries. It reuses rather than re-teaches M03 etcd mechanics, M05 database backup/PITR mechanics, M07 Terraform-state recovery, M08 GitOps rebuild, M09 trust-root/key custody, M10 incident management, M11 observability, and M12 supply-chain security.

Reference families to consult before applying this material in production:

- **NIST SP 800-34 Rev. 1**, *Contingency Planning Guide for Federal Information Systems* — contingency planning and recovery concepts. Verify exact definitions and applicable sections before attributing specific terminology.
- **ISO 22301**, business continuity management systems — awareness reference for business continuity terminology and governance. The standard is not reproduced here; verify the current edition and licensed text.
- **DRII** professional practices — awareness reference for business impact analysis and recovery planning. Verify current terminology and guidance.
- Official documentation for the installed PostgreSQL/CloudNativePG version, Kubernetes and storage driver, object-store implementation, Vault/OpenBao, GitOps controller, and any backup tooling used. Commands and fields are intentionally not prescribed where they depend on the M05 installation.
- Python 3 standard-library documentation for `argparse`, `datetime`, and `unittest` for the runnable calculator examples.

**Verification notes:**

- The date in the header is the authoring/review date only; it does not claim that live documentation was checked on that date.
- `RTO < MTD/MTPD` is presented as a planning expectation, not a universal mathematical rule. Verify the adopted framework's exact terminology and definitions.
- Whether disaster duration counts toward an SLO error budget depends on the organization's policy; this lesson marks any default assumption explicitly.
- Example scores, tiers, targets, timestamps, and sample outputs are `[ILLUSTRATIVE]` or representative, not measured production results.
- Tool versions, operator-specific fields, object-lock semantics, archive behavior, and exact backup commands are `[VERIFY]` against current official documentation and the learner's installed M05 environment.
- No cloud account, paid product, or real second region is required. Local labs are useful for process rehearsal but do not prove production or regional-failure behavior.
