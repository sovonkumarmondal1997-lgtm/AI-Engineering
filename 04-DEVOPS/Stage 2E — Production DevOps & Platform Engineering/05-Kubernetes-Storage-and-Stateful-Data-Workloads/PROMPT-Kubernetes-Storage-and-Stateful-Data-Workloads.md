# PROMPT — Generate `SYLLABUS-Kubernetes-Storage-and-Stateful-Data-Workloads.md`

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a capable, long-context LLM. The output is very large, so the prompt uses a multi-part Delivery Protocol (Section 14).

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior DevOps Engineer and SRE with 15 years of production experience** running stateful data systems on Kubernetes. You have recovered databases from orphaned volumes, found out the hard way that a snapshot is not a backup, resized volumes under load, debugged `Multi-Attach` errors and zone-stuck pods, and written the runbooks others were paged with. You teach with **evidence over opinion, data-safety first, and every claim verifiable.**

You are also a careful technical author. You never invent a manifest field, a driver capability, a parameter, a default, or a version. When unsure, you say so and mark it `[VERIFY]`. You treat **data loss as the worst failure** and make every destructive step explicit.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 2E — Production DevOps & Platform Engineering / 05-Kubernetes-Storage-and-Stateful-Data-Workloads/` (module code **M05**)

Output file name: **`SYLLABUS-Kubernetes-Storage-and-Stateful-Data-Workloads.md`**

It must teach, **one after another, from beginner to advanced**, these 11 units in this exact order:

| # | Unit | Target file |
|---|---|---|
| 0 | Folder orientation | `README.md` |
| 1 | Volumes, PersistentVolumes, PersistentVolumeClaims | `01-volumes-persistentvolumes-and-persistentvolumeclaims.md` |
| 2 | StorageClasses, dynamic provisioning, CSI drivers | `02-storageclasses-dynamic-provisioning-and-csi-drivers.md` |
| 3 | Volume snapshots, cloning, expansion | `03-volume-snapshots-cloning-and-expansion.md` |
| 4 | StatefulSet storage patterns and stable identity | `04-statefulset-storage-patterns-and-stable-identity.md` |
| 5 | Running databases and brokers with operators | `05-running-databases-and-brokers-with-operators.md` |
| 6 | Storage performance: IOPS, throughput, latency | `06-storage-performance-iops-throughput-and-latency.md` |
| 7 | Data locality, zonal failure, volume affinity | `07-data-locality-zonal-failure-and-volume-affinity.md` |
| 8 | Storage troubleshooting and orphaned volumes | `08-storage-troubleshooting-and-orphaned-volumes.md` |
| 9 | Practice questions | `practice-questions.md` |
| 10 | Capstone project | `Projects/README.md` + `Projects/01-stateful-data-platform-with-snapshots-and-recovery.md` |

Do **not** add, merge, skip, or reorder units. This is the **teaching content itself**, not an outline.

# 3. LEARNER AND CONTEXT

- **Learner:** a data/AI engineer who completed Stages 0–2D and Stage 2E modules M01–M04. They know SQL databases and data pipelines from earlier stages, can operate Pods/Deployments/Services/probes/PDBs/RBAC (M03), and understand Services/DNS/NetworkPolicy (M04). They have **not** run production stateful workloads on Kubernetes.
- **Stage constraint — zero budget.** All hands-on work runs on a laptop (WSL2 Ubuntu primary, native Linux secondary; ~4 CPU, 8 GB RAM, 30 GB disk). **No cloud block storage, no managed databases, no paid storage products.**
- **Primary lab platform: `kind`.** Disk is the scarcest resource: every lab states its disk footprint, and the learner is reminded to delete clusters and PVC data. Honest fidelity limits to state explicitly and verify `[VERIFY]`:
  - kind's default `StorageClass` (a local-path-style provisioner) provides **node-local, host-backed** volumes: no replication, no cloud durability, no real zones, no `VolumeSnapshot` support, and typically no volume expansion.
  - A local volume's data lives **with the node (container)**; deleting the kind cluster deletes the data. This models mechanics, **not** durability.
  - To teach snapshots, cloning, and expansion, use the Kubernetes **CSI hostpath driver** (the reference/test driver) with the external-snapshotter CRDs and controller, installed from official sources `[VERIFY]` install steps and kind compatibility — and say plainly that it is a **teaching driver, not a production storage system**. Teach production drivers (cloud block/file CSI drivers, Ceph/Rook, Longhorn, OpenEBS, TopoLVM, local static provisioner) as **Awareness** with a comparison table, and an optional lab only where it fits the 8 GB budget (e.g., Longhorn/OpenEBS-class systems are often too heavy: mark `[VERIFY]` footprint and default to Awareness).
  - Zones: kind has no real zones. Simulate topology by labeling workers with `topology.kubernetes.io/zone` values and say clearly that it simulates **scheduling constraints**, not independent failure domains or cross-zone latency.
  - Performance: container-on-laptop disk numbers (WSL2 virtual disk, page cache, host filesystem) are **not** representative of production storage. Teach the *method* (fio), never quote numbers as expected values.
- **Tooling-map alignment and scope decisions** (state to the learner in the README):
  - **Core (hands-on):** PersistentVolume/PersistentVolumeClaim, StatefulSet, kubectl.
  - **Taught at working depth because this folder has dedicated modules, though the stage tooling map lists them as Awareness:** CSI (concepts + the hostpath driver lab), VolumeSnapshots, and **one database operator — CloudNativePG** (PostgreSQL) as the single hands-on operator (verify current install path, CRD versions, and its documented backup/recovery model `[VERIFY]`). A broker operator (e.g., Strimzi for Kafka) is **Awareness** with an architecture walkthrough and an optional minimal-footprint lab only if resources allow `[VERIFY]` — Kafka is memory-hungry; default to a single small node and mark it optional.
  - **Awareness only:** Rook/Ceph, Longhorn, OpenEBS, Portworx, cloud CSI drivers (EBS/PD/Azure Disk, EFS/Filestore/Azure Files), Velero and Kasten (backup — forward ref M13), MinIO as an S3-compatible local object store (may be used as a lab dependency for operator backups `[VERIFY]`), Vitess, Zalando/Percona/CrunchyData operators, Redis/MongoDB/MySQL operators, TopoLVM, SIG Storage Local Static Provisioner details, VolumeGroupSnapshot and VolumeAttributesClass (alpha/beta features `[VERSION-SENSITIVE]`), COSI.
  - **Key principle to teach repeatedly:** *Kubernetes gives you storage primitives and controllers; it does not give you database correctness.* A StatefulSet is not a highly-available database; a snapshot is not an application-consistent backup; a replica is not a backup; and an operator does not remove the need to test restores.
- **Domain flavor:** a stateful **data platform**: PostgreSQL (the system of record / feature store metadata), a Redis-style cache or a small queue with persistence, an object-store-like local volume for datasets/model artifacts, and an ETL job writing to PostgreSQL. Realistic needs: crash-consistent vs application-consistent backups, point-in-time recovery concepts, schema migrations on stateful sets, disk-full incidents, and node loss with data on a local volume.
- **Cross-module links:** M01 (images, non-root — `fsGroup`/UID interplay with volume permissions), M03 (StatefulSet/Job basics, PDBs, drain, probes, RBAC/PSS, etcd backup — **etcd snapshots do not contain PV data; this module covers that gap**), M04 (headless Services/DNS for StatefulSets, NetworkPolicy for databases), M06 (Helm/Kustomize — apply manifests directly here; flag where operators ship Helm charts), M09 (secrets: database credentials, encryption keys — use lab fakes and point forward), M10 (SLOs/incidents), M11 (storage and database observability), M12 (security), M13 (backup/DR — deep backup strategy, RPO/RTO programs, cross-region), M14 (multi-cluster), M15 (storage cost). State clearly what is **taught here vs. deferred**: snapshot/clone/expansion mechanics and a basic backup/restore drill are here; organization-wide DR programs, immutability, and cross-region replication are M13.

# 4. TEACHING MODEL — THE FOUR LEVELS (UNITS 1–8)

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Explains the concept, runs and reads basic commands/manifests, and can trace where the data physically lives. |
| **L2** | Intermediate — Working Practice | Configures storage correctly for a real data service and avoids common data-loss mistakes. |
| **L3** | Advanced — Production Engineering | Designs, secures, measures, and defends choices under constraints (durability, performance, availability, cost). |
| **L4** | Expert — Operating at Scale and Under Failure | Diagnoses storage/stateful failures, performs safe recovery, writes policy and automation, and plans safe change for a fleet. |

# 5. MANDATORY STRUCTURE FOR EACH UNIT 1–8

Use this exact skeleton, same headings, same order, in every unit. If a section is genuinely not applicable, write one sentence explaining why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours>  |  **Prerequisites:** <list>
**Core tools:** …  |  **Awareness:** …  |  **Last reviewed:** <date>  |  **Kubernetes/tool baseline assumed:** <ranges, [VERIFY]>

### N.0 Why this matters in production
(3–6 sentences; a concrete data-loss, outage, or cost incident this prevents. No hype.)

### N.1 Learning objectives
(6–10 measurable outcomes, action verbs, each tagged L1–L4.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception. At least one diagram — mermaid or ASCII — showing the object chain (Pod → PVC → PV → backing storage), the controllers/drivers that act on each step, and where the data physically lives.)

### N.3 Level 1 — Beginner
- First-principles explanation (what object does what; which controller/sidecar/driver reconciles it; where data lives)
- Guided lab: exact manifests/commands, expected output, how to read it
- "What just happened?" walkthrough (trace the objects, events, and the host path or device involved)
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Complete, runnable manifests for the stateful data-platform running example
- Pattern catalogue: pattern | when to use | when NOT to use
- Anti-pattern catalogue: bad config → how it loses data or breaks in production → corrected version
- Lab with observable before/after behavior (include a data-persistence proof: write → destroy pod → verify data)

### N.5 Level 3 — Advanced
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Durability, performance, availability, and security techniques
- Measurement/verification method (what to observe, which command/tool, how to avoid fooling yourself)
- Lab requiring a defended decision, not a copied manifest

### N.6 Level 4 — Expert
- Failure scenarios (symptom → hypothesis → test → root cause → fix → prevention) with an explicit **data-safety check** before every remediation step
- Policy-as-code and automation (validation scripts, admission policy sketches, CI checks of manifests, audit scripts)
- Fleet/organizational concerns: standards, ownership, change management, review checklists
- Edge cases and platform differences (kind vs production, WSL2, managed vs self-managed, cloud vs bare metal)

### N.7 SRE lens
- SLIs/SLOs relevant here (e.g., volume-attach latency, PVC-bound time, disk-usage headroom, replication lag, backup success/age, restore-test pass rate)
- Failure modes and blast radius
- Runbook snippet: alert → triage → mitigation → follow-up
- Cost and capacity notes

### N.8 Security lens
- Threats addressed (e.g., cross-tenant volume access, data exposure in snapshots/backups, unencrypted data at rest, overprivileged CSI/operator service accounts, hostPath escapes, credentials in manifests) and what is NOT addressed
- Controls and how to verify each with a concrete check

### N.9 Production checklist
(Checkbox list; every item verifiable by command or test.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | expected evidence | cleanup | stretch. Idempotent, safe to re-run, within the local resource baseline, each with its **disk footprint** and the **kind-simulation caveat** where relevant. Destructive steps carry a data-safety preface.)

### N.11 Self-check questions
(6–10 questions with concise answer keys and a note on why wrong options are tempting.)

### N.12 Evidence artifacts
(Exactly what files/captures/outputs the learner saves to prove completion.)

### N.13 Common interview and design-review questions
(5 questions with senior-level model answers.)

### N.14 Sources and verification notes
(Official docs consulted by name and section; [VERIFY] items; version-sensitive claims.)
```

# 6. MODULE-SPECIFIC CONTENT REQUIREMENTS

Minimum topics. Add depth, never remove.

## Unit 1 — Volumes, PersistentVolumes, PersistentVolumeClaims
- **L1:** why container filesystems are ephemeral; volume types overview (`emptyDir`, `hostPath`, `configMap`/`secret`/projected, `persistentVolumeClaim`, ephemeral inline volumes, CSI inline); the PV/PVC abstraction (supply vs request; binding as a 1:1 relationship); static provisioning walk-through; access modes (`ReadWriteOnce`, `ReadOnlyMany`, `ReadWriteMany`, `ReadWriteOncePod`) and what they actually guarantee; capacity semantics; `kubectl get pv,pvc`, `describe`; PVC phases (`Pending`, `Bound`, `Lost`); proving persistence across Pod deletion.
- **L2:** `volumeMode` (Filesystem vs Block); `persistentVolumeReclaimPolicy` (`Retain`/`Delete`; `Recycle` deprecated `[VERIFY]`) and the data-loss consequences of each; `volumeBindingMode` (`Immediate` vs `WaitForFirstConsumer`) introduced; PVC selectors and `volumeName` pre-binding; `mountOptions`; `subPath` and `subPathExpr` and their pitfalls (no live updates for configmaps via subPath, symlink considerations); `fsGroup`, `fsGroupChangePolicy`, `runAsUser` and permission-denied on mounted volumes (tie to M01 non-root); `emptyDir` with `medium: Memory` and `sizeLimit` (counts against memory); `hostPath` risks (node coupling, security) and why it is lab-only; PVC protection finalizers (`kubernetes.io/pvc-protection`, `pv-protection`) and "stuck Terminating" PVCs; reading storage-related events.
- **L3:** the **volume lifecycle** end to end (provision → bind → attach → mount → use → unmount → detach → release → reclaim) and which component owns each step (PV controller, attach/detach controller, kubelet, CSI node plugin); `Retain` workflow for recovering data by re-binding a Released PV (clear `claimRef`) — with data-safety warnings; access-mode semantics vs real backend capability (RWX needs a shared filesystem backend; an RWO volume can still be mounted by multiple pods on the same node `[VERIFY]` semantics; `ReadWriteOncePod` enforces single-pod); local volumes (`local` PV type with required `nodeAffinity`) and their failure semantics (node loss = data unavailable or lost); ephemeral volumes (generic ephemeral volumes, CSI ephemeral) for scratch (Spark shuffle, ETL temp) vs persistent; storage quotas (`requests.storage`, per-StorageClass quota — link M03 Unit 2) and `LimitRange` for PVC sizes; encrypting volumes at the storage layer (concept; backend-dependent); secrets and etcd (PV data is not in etcd — snapshotting etcd does not back up data; link M03 Unit 10).
- **L4:** PV/PVC governance at scale (naming, labels, ownership, annotations for backup/cost); policy-as-code (admission policy requiring StorageClass, size bounds, `Retain` for production classes, forbidding `hostPath` — Awareness via Kyverno/Gatekeeper/ValidatingAdmissionPolicy `[VERIFY]` syntax); audit script finding unbound/Released/Failed PVs and PVCs with no owner; data-recovery procedure from a `Released` PV; incident: "`Delete` reclaim policy removed a production volume when a namespace was deleted" and "pod could not read the volume after an image switched to non-root" → diagnose → fix → prevent.
- **Must include:** a lab showing write → delete Pod → data persists; a reclaim-policy lab contrasting `Delete` and `Retain` on **throwaway data** with evidence of what remained on the node (`docker exec` into the kind node to inspect the host path); an `fsGroup` permission lab with a non-root image; a "stuck Terminating PVC" lab with repair via finalizer reasoning (and the risk of force-removing finalizers).

## Unit 2 — StorageClasses, dynamic provisioning, CSI drivers
- **L1:** why dynamic provisioning exists; `StorageClass` fields (`provisioner`, `parameters`, `reclaimPolicy`, `volumeBindingMode`, `allowVolumeExpansion`, `mountOptions`, `allowedTopologies`); default StorageClass annotation and its pitfalls (zero or multiple defaults, `storageClassName: ""` semantics); the PVC → provisioner flow; inspecting kind's default class.
- **L2:** the **CSI architecture**: controller plugin (Deployment/StatefulSet: provisioner, attacher, resizer, snapshotter sidecars), node plugin (DaemonSet: node-driver-registrar, mount operations), `CSIDriver`, `CSINode`, `VolumeAttachment`, and the gRPC identity/controller/node services (concept); in-tree → CSI migration (concept; `[VERIFY]` status per plugin); `volumeBindingMode: WaitForFirstConsumer` and why it matters for topology-constrained storage; `reclaimPolicy` at class level; install the CSI hostpath driver on kind (official instructions, `<VERSION>` placeholders) and create a class from it; compare to the default local-path class via a feature/capability table.
- **L3:** driver capability matrix thinking (snapshots, clones, expansion, RWX, block mode, topology, volume health, fsGroup policy, `CSIDriver.spec.fsGroupPolicy` `[VERIFY]`); parameter design per class (disk type, replication, encryption — backend-specific, Awareness); storage-class taxonomy for a data platform (e.g., `fast-retain`, `standard-delete`, `shared-rwx`, `scratch`) with a decision record; CSI driver upgrades and sidecar version coupling with the Kubernetes version `[VERIFY]` compatibility matrices; driver failure semantics (what happens to running pods vs new attaches when the controller plugin is down; node plugin down); `CSIStorageCapacity` and capacity-aware scheduling `[VERIFY]`; NFS/SMB/object-gateway patterns for RWX (Awareness, trade-offs: locking, performance, single point of failure); object storage is not a filesystem (CSI-fuse mounts as Awareness with caveats); secrets for CSI drivers (provisioner/node-stage secrets — concept).
- **L4:** storage platform as a product (class catalog, self-service, quotas, SLAs, deprecation policy); changing a StorageClass for existing data is impossible in place (the immutability of most fields and `volumeName`/class on PVCs) → migration patterns (snapshot/clone, `pv-migrate`-style copy tools `[VERIFY]`, application-level replication); CSI incident analysis (`ProvisioningFailed`, `AttachVolume.Attach failed`, `MountVolume.SetUp failed`, orphaned `VolumeAttachment`s, node-plugin crashloops) with an event decoder table; privileged-component risk review (CSI node plugins run privileged with host mounts — threat-model them); policy to forbid unmanaged classes.
- **Must include:** a lab that installs the hostpath CSI driver, provisions volumes dynamically with `Immediate` vs `WaitForFirstConsumer`, shows the object chain (`PVC → PV → VolumeAttachment`/node plugin logs), and breaks the driver controller to observe which operations fail and which keep working — with the simulation caveat.

## Unit 3 — Volume snapshots, cloning, expansion
- **L1:** what a snapshot is (point-in-time reference of a volume, driver-implemented) and **what it is not** (not a backup if it lives with the volume/backend; not application-consistent by default); `VolumeSnapshot`, `VolumeSnapshotContent`, `VolumeSnapshotClass` (API group `snapshot.storage.k8s.io`, version `[VERIFY]`); the external-snapshotter CRDs + snapshot-controller (not installed by default); restore from snapshot via PVC `dataSource`; the idea of volume cloning (`dataSource` of kind PVC) and expansion (`allowVolumeExpansion`).
- **L2:** take a snapshot of the PostgreSQL volume, modify data, restore into a new PVC, verify; `deletionPolicy` (`Delete` vs `Retain`) and its consequences (deleting a VolumeSnapshot may delete the underlying snapshot); `readyToUse` semantics; pre-provisioned snapshots (importing an existing `VolumeSnapshotContent`); clone a PVC for a test environment (same namespace, same StorageClass, size ≥ source constraints `[VERIFY]`); **expand a PVC** online/offline (`spec.resources.requests.storage` increase; conditions `Resizing`, `FileSystemResizePending`; controller resize vs node filesystem resize); shrink is not supported — explain and the workaround (migrate); `kubectl describe pvc` conditions and events.
- **L3:** **crash-consistent vs application-consistent** snapshots; quiescing databases (PostgreSQL `pg_backup_start`/`pg_backup_stop` or `CHECKPOINT` + fsfreeze concepts `[VERIFY]` version-specific function names; why filesystem snapshots of a running PostgreSQL are *usually* crash-recoverable but not a substitute for tested logical/physical backups); hooks (Kasten/Velero hooks — Awareness; do not teach as available in core Kubernetes); snapshot of multiple volumes consistency (a PG data dir + WAL on separate volumes; `VolumeGroupSnapshot` `[VERSION-SENSITIVE]`, Awareness); snapshot storage location/cost/retention; snapshots vs backups vs replicas vs PITR — a comparison table with RPO/RTO reasoning (no numbers claimed); expansion for StatefulSets (the `volumeClaimTemplates` immutability problem and the manual PVC patch + StatefulSet recreate-with-orphan-cascade workaround `[VERIFY]` — and newer features if any `[VERSION-SENSITIVE]`); filesystem-resize behavior by FS type (ext4/xfs; xfs cannot shrink) `[VERIFY]`; clone vs snapshot-restore semantics and speed differences are backend-dependent.
- **L4:** snapshot lifecycle automation (a CronJob + script creating timestamped snapshots with retention pruning — **dry-run first**); restore-testing automation (restore into a scratch namespace, run integrity queries, report pass/fail, tear down); the "snapshots lived in the same failure domain as the volume" incident; the "expansion stuck in `FileSystemResizePending`" incident; guardrails (admission policy for snapshot classes; RBAC on who may delete `VolumeSnapshotContent`; deletion protection); handoff to M13 (offsite copies, immutability, cross-cluster restore) stated explicitly.
- **Must include:** a lab performing snapshot → destructive data change → restore → verification with integrity queries; a clone lab; a PVC online expansion lab with fs-resize proof (`df`); a StatefulSet volume-expansion lab following the documented workaround on throwaway data; and a written **"snapshot is not a backup"** reflection where the learner lists three failure scenarios the snapshot does not survive in this lab. Include the explicit statement that the hostpath driver snapshots live on the same node disk.

## Unit 4 — StatefulSet storage patterns and stable identity
- **L1:** what StatefulSet guarantees (stable network identity, stable per-replica storage via `volumeClaimTemplates`, ordered create/scale/update) and what it does **not** (data replication, failover, backups, consistency); headless Service and DNS records (`pod-0.svc.ns.svc.cluster.local`); PVC naming (`<template>-<sts>-<ordinal>`); `kubectl get sts,pods,pvc`; scale up/down and what happens to PVCs (they persist).
- **L2:** `podManagementPolicy` (`OrderedReady` vs `Parallel`), `updateStrategy` (`RollingUpdate` with `partition`, `OnDelete`), `minReadySeconds`, `persistentVolumeClaimRetentionPolicy` (`whenDeleted`/`whenScaled`: `Retain`/`Delete`) `[VERIFY]` stability and defaults; init containers for permission/bootstrap; `volumeClaimTemplates` immutability; data-directory layout gotchas (`lost+found` in the mount root breaks `initdb` → use a subdirectory/`PGDATA`); readiness and liveness for databases (don't kill a recovering database — link M03 Unit 3; startup probes); graceful termination for databases (SIGTERM semantics, `terminationGracePeriodSeconds` long enough to checkpoint, `preStop`), PDBs for quorum systems (link M03 Unit 5); anti-affinity/topology spread for replicas (link M03 Unit 7).
- **L3:** bootstrap and replication patterns (primary/replica with an init script is **fragile** — why operators exist); leader election/consensus awareness (etcd/ZooKeeper/Kafka KRaft/Raft) vs StatefulSet ordering; scaling stateful systems (rebalancing, resharding — application-level work StatefulSet does not do); rolling updates of a quorum system (one at a time, wait for health, `partition` canary); safe PVC retention policy choice per environment; **multi-volume pods** (data + WAL + logs) and failure atomicity; `ReadWriteOncePod` for single-writer protection; shared-nothing vs shared-storage designs; node drain and local-volume pods (pod cannot reschedule elsewhere — link Unit 7); DNS caching/TTL and client reconnect behavior after pod IP change; storage and sidecar interactions (backup sidecars, exporters).
- **L4:** the **StatefulSet failure catalogue**: node lost (pod stuck `Terminating`/`Unknown`; why Kubernetes will not force-delete a StatefulSet pod automatically — at-most-one semantics; the safe manual procedure `kubectl delete pod --force --grace-period=0` and **the data-corruption risk if the node is merely partitioned** `[VERIFY]` wording; node shutdown handling features `[VERSION-SENSITIVE]`); PVC deleted accidentally; `volumeClaimTemplates` change needed; stuck rolling update because a pod never becomes ready; ordinal gaps; migration of a StatefulSet to a different StorageClass (orphan-delete → recreate pattern, with backups first); a decision framework: StatefulSet by hand vs operator vs managed service vs "don't run it on Kubernetes" (state the honest trade-offs); standard StatefulSet templates and manifest policy checks.
- **Must include:** a lab with a 3-replica StatefulSet showing stable DNS and per-pod PVCs, a rolling update with `partition`, scale-down/scale-up proving PVC retention (and `persistentVolumeClaimRetentionPolicy` variants if feature is enabled `[VERIFY]`), and a simulated node loss on kind (stop a worker container) demonstrating the stuck-pod behavior and the **safe, documented recovery procedure with data checks** on throwaway data.

## Unit 5 — Running databases and brokers with operators
- **L1:** the operator pattern (CRDs + controllers encoding domain operations); why databases need more than StatefulSets (bootstrap, replication, failover, backups, upgrades, TLS, user management); custom resources as the user interface; operator maturity concept (install → lifecycle → backup/recovery → monitoring → autoscale → tuning); the **three honest questions**: should this run on Kubernetes at all, which operator, who is on call for it.
- **L2:** install **CloudNativePG** with official manifests/Helm per its docs `[VERIFY]` and create a 3-instance PostgreSQL `Cluster` on kind (reduced resources); inspect generated objects (pods, PVCs, Services `-rw`/`-ro`/`-r`, Secrets for credentials, `PodDisruptionBudget`); connect and write data; perform a planned switchover and observe client behavior; kill the primary pod and watch failover; read `Cluster` status and events; operator logs; resource requests suitable for an 8 GB laptop.
- **L3:** **backup and recovery with the operator**: continuous WAL archiving and base backups to an S3-compatible object store (local MinIO as lab dependency `[VERIFY]`) and **point-in-time recovery** into a new `Cluster` (`bootstrap.recovery`) `[VERIFY]` field names and the operator's current recommended backup mechanism (barman-cloud plugin vs in-tree — **check the current docs**; do not assume); `ScheduledBackup`; verifying restores; major/minor version upgrade procedures and risks; connection pooling (PgBouncer via the operator's `Pooler` `[VERIFY]`); TLS and credential rotation (forward ref M09); monitoring via the operator's metrics endpoint (forward ref M11); storage choices for PG (separate WAL volume option `[VERIFY]`), `shared_buffers`/memory vs container limits; fencing and split-brain protection concepts; synchronous vs asynchronous replication trade-offs (durability vs availability vs latency) — **taught as principles with the operator's field names `[VERIFY]`**; NetworkPolicy for the database namespace (link M04); PDBs and anti-affinity generated by the operator vs your own.
- **L3 (brokers — Awareness-weighted):** how a broker operator (e.g., Strimzi/Kafka) differs from a DB operator: partition rebalancing, ISR/KRaft quorum, persistent volumes per broker, rack awareness mapped to zones (concept), rolling restarts and `min.insync.replicas`, storage sizing/retention, JBOD concept; architecture walkthrough with an annotated sample `Kafka` custom resource `[VERIFY]` API version and KRaft mode status; optional minimal one-node lab only if resources allow, marked `[VERIFY]` footprint; Redis/RabbitMQ/NATS persistence trade-offs (Awareness).
- **L4:** operator evaluation framework (maintenance activity/governance, backup/PITR support, upgrade path, failover tested?, observability, security posture, license, escape hatch/exit strategy, community vs vendor support — all `[VERIFY]` per candidate); operator upgrade strategy and CRD management risk; blast radius of the operator (a cluster-wide controller with broad RBAC — threat-model); "operator deleted/crashed — what happens to the database?" (it keeps running; no failover); backup-of-the-operator-config (GitOps handoff M08); game-day design (failover, restore, node loss) with expected-vs-observed tables; incidents: "failover happened but clients kept the old connection," "WAL archiving failed silently and the volume filled," "restore worked but was never tested for the latest backup"; the **managed-database alternative** (what you buy vs operate) as a decision table (Awareness; no paid lab).
- **Must include:** a CloudNativePG lab: create → write data → kill primary → verify failover and data → take base backup + WAL to local object store → destroy the cluster → **PITR restore to a specific timestamp** into a new cluster → verify with row-level checks. Mark ⚠ DESTRUCTIVE steps and use a throwaway namespace/cluster. If any part cannot be reproduced on 8 GB, say so and provide a reduced variant.

## Unit 6 — Storage performance: IOPS, throughput, latency
- **L1:** the three performance dimensions (IOPS, throughput/bandwidth, latency) and how they relate (block size, queue depth, read/write mix, sequential vs random); why databases care about latency and fsync; Linux I/O basics (page cache, `O_DIRECT`, `fsync`, filesystem vs raw block); tools overview: `fio`, `iostat -x`, `iotop`, `dd` (and why `dd` is a poor benchmark), `pidstat`; reading `kubectl top` doesn't show disk I/O.
- **L2:** run `fio` inside a Pod against a PVC with carefully defined profiles (random 4k read/write, sequential 1M, mixed 70/30, fsync-heavy small writes) using `direct=1`, `ioengine`, `iodepth`, `runtime`, `ramp_time` `[VERIFY]` flag semantics; read `fio` output (IOPS, bandwidth, clat percentiles); `iostat -x` from the node container (`await`/`aqu-sz`/`%util` meaning, `%util` caveats on modern devices); the **page-cache trap** (benchmark measuring RAM); filesystem choice and mount options (ext4/xfs `noatime`) as concepts; PostgreSQL's own benchmark tool (`pgbench`) for application-level view; separate data and WAL volumes concept.
- **L3:** benchmarking methodology (define workload from the application, warm-up, steady-state, repeat N times, record environment, compare relative not absolute, control for noisy neighbors); latency percentiles vs averages; **throttling models** (cloud block storage IOPS/throughput caps, burst credits, per-volume vs per-instance limits — **Awareness; never state any provider's numbers**); local NVMe vs network block vs network file vs object storage trade-offs (latency, durability, cost, failure modes); StorageClass parameters for performance tiers (backend-specific, Awareness); database tuning interactions (checkpoint behavior, `fsync`/`synchronous_commit`, WAL placement, autovacuum I/O, shared memory vs cgroup limits `[VERIFY]`); noisy neighbors and I/O isolation (cgroup v2 `io.max` concept; Kubernetes has limited native I/O limiting — state honestly `[VERIFY]`); `emptyDir` on node disk vs memory for shuffle/scratch; ETL I/O patterns (large sequential writes, many small files, Parquet row-group sizing — link Stage 2C concepts); CPU throttling vs I/O wait confusion (link M03 Unit 2); ephemeral-storage requests/limits and eviction (`ephemeral-storage` resource, `DiskPressure`).
- **L4:** capacity and performance SLOs (p99 write latency, attach time, restore throughput), performance regression guard (a benchmark Job in CI against ephemeral kind with relative thresholds — **fidelity warning: kind laptop results are for regression detection of config mistakes only, not capacity planning**); capacity planning from growth data (disk-fill forecasting with a simple linear projection script, headroom policy, alert at thresholds; forward ref M11/M15); cost/performance tiering decisions (forward ref M15); diagnosing "database slow" end to end (app → DB → fsync → volume → node → backend) with a decision tree; incident: "p99 latency spike traced to a snapshot/backup job competing for I/O," "burst credits exhausted," "volume 100% full → database read-only/crash → recovery" (with safe-expansion procedure); chaos: fill a volume in lab and observe PG behavior.
- **Must include:** a reproducible `fio` benchmark harness (script + job files) running 4 profiles × N repetitions, output parsed into a median/p95 table, with a lab demonstrating the page-cache trap (same test with and without `direct=1`), a disk-full lab on throwaway data with recovery by expansion or cleanup, and an explicit "what these laptop numbers do NOT tell you" section.

## Unit 7 — Data locality, zonal failure, volume affinity
- **L1:** what a failure domain is (node, rack, zone, region); why storage is tied to topology (a cloud block volume lives in one zone; a local volume lives on one node); pod-to-volume co-location; PV `nodeAffinity` and topology labels (`topology.kubernetes.io/zone`, `kubernetes.io/hostname`); why a pod can be **`Pending` because its volume is in the wrong place**.
- **L2:** `volumeBindingMode: WaitForFirstConsumer` (delay binding until scheduling so volume is created where the pod lands) vs `Immediate` (the classic zone-mismatch failure); `allowedTopologies`; the scheduler's `VolumeBinding` plugin interplay with affinity/taints/topology spread (link M03 Unit 7); local PV with required nodeAffinity and the "node gone = data gone/unavailable" reality; reading scheduler events (`volume node affinity conflict`, `didn't find available persistent volumes to bind`); simulating zones on kind via worker labels.
- **L3:** designing for zonal failure: (a) **application-level replication across zones** (the correct answer for databases — one replica per zone, each with zonal volumes), (b) regional/replicated storage (Awareness: regional disks, replicated block systems like Ceph/Longhorn — cost/latency trade-offs), (c) shared network filesystems; why a single-zone volume + multi-zone pods is a trap; topology spread for stateful replicas (`DoNotSchedule` vs `ScheduleAnyway` effect on availability); storage-aware scheduling and capacity tracking `[VERIFY]`; data gravity and compute-follows-data (ETL jobs scheduled near data; cost of cross-zone transfer — forward ref M15); synchronous vs asynchronous cross-zone replication latency/RPO trade-offs; zone failure simulation methodology; quorum math for zone loss (3 zones, 3 replicas vs 5); rebalancing after zone recovery; reattach times and `Multi-Attach` errors during node failure (`VolumeAttachment` cleanup, the ~6-minute-class force-detach timers — **do not quote; describe the mechanism and tell the learner to check the controller-manager docs `[VERIFY]`**); local-volume node replacement procedures; PV node affinity immutability.
- **L4:** multi-zone architecture review checklist; zone-evacuation runbook (cordon/drain a "zone" in the lab; confirm quorum and data safety first); disaster scenarios by blast radius (pod, node, zone, region) with expected behavior and RTO/RPO reasoning tied to M13/M14; automated verification that each stateful replica is in a distinct zone and each PV matches its pod's zone (audit script); cost of replication vs risk analysis; policy-as-code (reject `Immediate` binding for zonal classes; require topology spread on StatefulSets); incident: "all three PostgreSQL replicas ended up in one zone after a node-pool change," "after a zone outage pods stayed Pending because volumes were bound to the dead zone" → diagnose → fix → prevent; honest discussion of what is **not** reproducible on one laptop.
- **Must include:** a lab labeling kind workers as zones `a/b/c`, creating zone-affine local/CSI volumes, demonstrating `Immediate` vs `WaitForFirstConsumer` mis-binding and its fix, running a 3-replica StatefulSet spread across the fake zones, then simulating loss of one "zone" (stop that worker container) and recording behavior: what stays available, what is `Pending`, and what the application-level replication (CloudNativePG from Unit 5 as optional integration) does — with the repeated statement that fake zones are scheduling simulations.

## Unit 8 — Storage troubleshooting and orphaned volumes
- **L1:** the systematic method (observe object states → read events → check the owning controller/driver → check the node → check the backend → fix safely → verify → document) with the **data-safety rule: before any destructive fix, confirm a restorable copy or that the data is disposable**; the status vocabulary (`PVC Pending/Bound/Lost`, `PV Available/Bound/Released/Failed`, `VolumeAttachment`, `FailedMount`, `FailedAttachVolume`, `ProvisioningFailed`, `FailedScheduling` with volume reasons); the troubleshooting toolkit (`kubectl describe`, `get events --sort-by`, `get pv,pvc,sc,volumeattachment`, CSI controller/node logs, `kubectl debug node`, `docker exec` into kind nodes, `df`, `lsblk`, `mount`).
- **L2:** decision trees for the top classes: PVC `Pending` (no matching class, no default class, provisioner down, quota, topology, `WaitForFirstConsumer` waiting for a pod — which is **normal**), pod `ContainerCreating` (attach/mount failures, `Multi-Attach`, permission/fsGroup, missing Secret for CSI), `Permission denied` on the volume, volume full, read-only filesystem after an error, expansion stuck, snapshot not `readyToUse`, StatefulSet pod stuck, slow I/O; PVC stuck `Terminating` (pvc-protection finalizer + pod still using it); PV stuck `Terminating`/`Released`; `Lost` PVC.
- **L3:** **orphaned volumes**: definitions and sources (deleted PVC with `Retain`, deleted namespace, failed provisioning leaving backend volumes, StatefulSet scale-down retention, abandoned snapshots/`VolumeSnapshotContent`, leftover `VolumeAttachment`s, node loss); discovery methods (cluster side: `kubectl get pv` filters for `Released`/`Available` without a recent claim, label/annotation audit; backend side: cloud-disk listings by tag — Awareness; kind side: host-path directories on nodes vs PV objects); **safe cleanup procedure** (identify owner → verify not referenced → snapshot/export if there is any doubt → quarantine with a label/annotation and a waiting period → delete → record); finalizer mechanics and the risks of `kubectl patch` removal; reconciling PV objects with backend volumes (concept); cost leakage (forward ref M15); `Multi-Attach` after node failure and `VolumeAttachment` cleanup; CSI sidecar/controller troubleshooting by reading logs for the specific RPC failing; node-level diagnosis (mounts, kernel messages `dmesg` for I/O errors, filesystem corruption indicators and when to run `fsck` — only on unmounted volumes with a backup; WSL2/kind caveats).
- **L4:** orphan-prevention programs (reclaim policy standards, TTL labels, ownership annotations, namespace-deletion guards, scale-down retention policy); automated orphan report (script/CronJob producing a table: PV, size, age, last-bound claim, owner label, recommended action) with a **dry-run default**; deletion-protection guardrails (admission policy preventing deletion of PVCs/PVs labeled `protect=true`, RBAC separation of delete rights); data-recovery drill from a `Released` PV and from a snapshot; troubleshooting at scale (JSONPath/`jq` across namespaces; audit logs for "who deleted this PVC"); post-incident review template for data-loss events; on-call handoff quality; "debugging when the CSI controller is down."
- **Must include:** a **storage troubleshooting gauntlet** of at least **12 provided broken scenarios** (e.g., no default StorageClass, wrong `storageClassName`, `WaitForFirstConsumer` misread as stuck, requested size exceeds quota, access-mode mismatch, `Released` PV never rebinding because of `claimRef`, `fsGroup`/permission failure, volume full, expansion on a class without `allowVolumeExpansion`, snapshot with missing CRDs/class, StatefulSet with PVC deleted, CSI controller scaled to zero, node affinity conflict, pvc-protection finalizer stuck, snapshot `Retain` content orphaned). Each has hidden cause, three-level hints, diagnosis rubric, safe fix (with the data-safety check stated), and prevention policy; answers in clearly separated answer-key sections. Plus an **orphan-audit lab** that creates orphans on purpose, finds them with the audit script, quarantines, and cleans up safely.

# 7. PRACTICE QUESTIONS (Unit 9)

At least **130 questions**: ≥ 12 per Units 1–8 plus ~20 cross-unit integration scenarios. Per unit:
- 3 × conceptual short-answer
- 3 × multiple choice (4 options; explain every distractor)
- 2 × output interpretation (given `kubectl describe pvc/pv/pod`, events, `fio`, `iostat`, CSI logs — what is wrong?)
- 2 × manifest review (find ≥ 3 defects, fix them, noting the data-loss risk of each)
- 1 × incident/troubleshooting scenario (symptom → diagnose → **data-safety check** → fix → prevent)
- 1 × design question with a rubric

Each question: ID, level (L1–L4), objective tested, time estimate, **model answer**, **common wrong answers**. Include "where does the data physically live?" tracing questions and "is this a backup?" classification questions (snapshot, replica, PITR archive, StatefulSet PVC, etcd snapshot, `Retain` PV). Include a scoring rubric (≥ 80% proceed; 60–79% remediate; < 60% repeat) and 8 "design-review" whiteboard prompts requiring written trade-off reasoning (e.g., operator vs managed DB, zonal failure design, StorageClass catalog, snapshot vs backup strategy, RWX need, local vs network volumes, capacity-headroom policy, orphan-prevention program). Test only taught content.

# 8. CAPSTONE PROJECT (Unit 10)

**Project:** *Stateful Data Platform with Snapshots and Recovery.*

Deliver `Projects/README.md` (index, grading, evidence submission) and the full spec.

**Scenario:** A data team runs PostgreSQL, a cache, and an ETL pipeline on Kubernetes with a hand-written StatefulSet, one default StorageClass, `Delete` reclaim everywhere, no snapshots, no tested backups, no disk alerts, and orphaned volumes accumulating. Last month a namespace deletion destroyed a volume; before that a full disk crashed the database; and nobody has ever restored from backup. The learner builds a stateful platform with **proven recovery**, locally.

**Required deliverables (each with acceptance criteria verifiable by command or inspection):**
1. kind cluster (1 control plane, 3 workers labeled as fake zones `a/b/c`) with bootstrap script, context safety checks, disk-footprint budget, and `versions.txt`.
2. CSI hostpath driver + snapshot CRDs/controller installed, with a documented StorageClass catalog (`fast-retain`, `standard-delete`, `scratch`) and a `VolumeSnapshotClass`; ADR for the catalog.
3. PostgreSQL via CloudNativePG: 3 instances spread across fake zones, non-root, resource-bounded, probes/PDB present (operator-generated or supplemented), NetworkPolicy restricting access to the app/ETL namespaces (link M04).
4. Application + ETL: a small FastAPI service and an ETL Job that write to PostgreSQL with idempotent writes and a verification query set (row counts/checksums).
5. Backups: continuous WAL archiving + base backups to a local S3-compatible store (MinIO or equivalent), `ScheduledBackup`; **PITR restore** into a new cluster to a chosen timestamp, verified with row-level checks.
6. Volume-level protection: scheduled VolumeSnapshots (with retention pruning script, dry-run default) of non-database data volumes; restore test namespace automation (`make restore-test`) that restores, runs integrity checks, reports pass/fail, and tears down.
7. Failure drills with recorded expected-vs-observed outcomes: primary pod kill, worker (node) loss, simulated zone loss, volume-full, accidental PVC deletion (recovered from `Retain`/snapshot/PITR), namespace deletion with protection guardrails, CSI controller down.
8. Capacity and performance: `fio` baseline harness, disk-fill forecasting script, disk-usage alert rule (Prometheus rule file validated syntactically; backend optional), expansion drill.
9. Governance: admission/policy examples (Awareness-level; ValidatingAdmissionPolicy or Kyverno/Gatekeeper sketches `[VERIFY]`) for required StorageClass, forbidden `hostPath`, protected PVCs; RBAC limiting delete rights on PVCs/PVs/snapshots.
10. Orphan audit: an audit script/CronJob with dry-run default producing a report; one deliberate orphan found and safely cleaned.
11. `Makefile` targets: `up`, `deploy`, `seed-data`, `backup`, `snapshot`, `restore-test`, `pitr-test`, `chaos`, `audit`, `verify`, `down`; `make verify` outputs a pass/fail report with evidence.
12. Documentation: architecture diagram (where every byte lives, per failure domain, simulated), ≥ 5 ADRs (storage classes, operator choice, backup method, zonal design, retention), runbooks for 5 incidents (volume full, failed failover/stuck StatefulSet pod, accidental PVC deletion, failed backup/WAL archive, orphaned volume cleanup), and a production-readiness review using the Unit 1–8 checklists.
13. A before/after results table (RPO achieved in drill, RTO measured for PITR and snapshot restore, failover time, backup size/duration, restore-test pass rate, orphaned volumes found, disk-headroom days) filled from the learner's **own** measurements. Provide the template; never fabricate results. State explicitly in the table notes that numbers come from a laptop lab and do not predict production.

**Include:** 6–7 milestones with time estimates; a 100-point rubric (Poor/Adequate/Strong/Exemplary descriptors, with heavy weighting for **proven restores**); stretch goals (second cluster as restore target — link M13; Strimzi mini-lab; Longhorn/OpenEBS comparison if resources allow; encryption-at-rest discussion); common failure points; self-review checklist; exact evidence folder structure; a **disk and RAM budget plan** for 4 CPU / 8 GB / 30 GB (what to scale down, when to delete data).

**Provide complete, runnable starter code and manifests:** the FastAPI service, ETL job, operator `Cluster`/`ScheduledBackup` manifests, StorageClass/VolumeSnapshotClass, scripts, Makefile, verification and chaos scripts, audit script. No `TODO: implement` in required deliverables. All credentials fake (`example-password-do-not-use`); note that proper secret handling is M09.

# 9. README ORIENTATION (Unit 0)

Include: purpose and audience; Gate In prerequisites (including M01–M04 outcomes consumed here and the stage's relevant prerequisites); module dependency graph and why order matters (PV/PVC → StorageClass/CSI → snapshots/expansion → StatefulSet → operators → performance → locality → troubleshooting); 6-week and 10-week pacing plans; tool matrix (Core / working-depth / Awareness matching Section 3) with install-verification commands; lab environment checklist (Docker disk usage, kind version, `kubectl` skew, free disk check before each lab, WSL2 virtual-disk growth notes and how to reclaim space); **disk/RAM budget guide**; **kind-vs-production fidelity table** (real / simulated / not reproducible: durability, replication, zones, attach/detach timing, snapshot independence, performance, backend failure, encryption-at-rest); glossary; the **"snapshot ≠ backup ≠ replica ≠ HA"** primer; module-to-exit-criteria mapping; evidence rules; how to use practice questions and the project; table linking M05 to M01–M04, M06, M08–M15, M17; a **safety section**: context hygiene, throwaway clusters/namespaces, never run lab destructive commands against a cluster with real data, never `kubectl patch` finalizers or force-delete on volumes you cannot restore, and treat backups/snapshots as sensitive data.

# 10. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block names its language and, for files, a first-line path comment (e.g., `# File: manifests/storage/storageclass-fast-retain.yaml`).
2. Every command is paired with **representative expected output**, labelled "example — yours will differ" (names, UIDs, sizes, timings vary), plus a short interpretation.
3. **Only real syntax.** Use apiVersions, kinds, fields, parameters, flags, and CLI subcommands you are confident exist. Anything that varies by Kubernetes version, CSI driver, operator version, or feature gate is tagged `[VERIFY: what/where]` or `[VERSION-SENSITIVE]`. State the apiVersion for every manifest (`v1`, `storage.k8s.io/v1`, `snapshot.storage.k8s.io/v1` `[VERIFY]`, `apps/v1`, `batch/v1`, `policy/v1`, `postgresql.cnpg.io/v1` `[VERIFY]`…) and mark ones you are not certain of. Never guess. For every install (CSI hostpath driver, external-snapshotter, CloudNativePG, MinIO, Strimzi) **point to the official install documentation and compatibility matrix** and use `<VERSION>` placeholders — never invent version numbers.
4. **Context and data safety:** every lab begins with a context check (`kubectl config current-context` asserted against the expected `kind-<name>`) and a free-disk check; every destructive command (`delete pvc/pv/ns`, finalizer patches, force deletes, `rm`, filesystem operations, cluster deletion) is labelled `⚠ DESTRUCTIVE — DATA LOSS`, names the target, states what data will be lost, shows a read-only or `--dry-run=server`/`kubectl diff` alternative first, and is used only on **throwaway data** created by the lab.
5. **Manifests follow standards taught** in M01/M03: pinned images (digest with tag comment), resource requests/limits (including `ephemeral-storage` where relevant), probes, non-root `securityContext` with `fsGroup` set deliberately, explicit ServiceAccount, labels — unless a deliberate anti-pattern labelled `# ANTI-PATTERN — DO NOT COPY` with the defect list, the data-loss consequence, and a fixed version beside it.
6. **No real secrets.** Fake credentials only (`example-password-do-not-use`); no backup credentials committed; forward-reference M09. Warn that snapshots and backups contain sensitive data and must be protected and deleted after labs.
7. **Defensive security only:** RBAC/volume-escape material (hostPath, privileged CSI node plugins) is for threat-modelling and auditing on the learner's own throwaway cluster; no exploit code.
8. **Scripts:** `set -euo pipefail`, quoted variables, explicit exit codes, context assertion, `--dry-run` default for anything that deletes or prunes (explicit `--apply` flag required), idempotent where possible; verification scripts exit non-zero on failure. Python: typed where practical, minimal dependencies, with tests.
9. **Resource realism:** every lab states approximate CPU/RAM/**disk** footprint and fits 4 CPU / 8 GB / 30 GB; never require more than 3 workers; never run PostgreSQL HA, MinIO, Kafka, a mesh, and an observability stack simultaneously; tell the learner when to delete data/clusters and how to verify reclaimed disk (including WSL2 virtual-disk caveats).
10. **Every lab ends with cleanup** (delete namespaces/PVCs/PVs/snapshots created by the lab, remove snapshot CRDs only if installed for the lab and with a warning about dependent resources, remove kubeconfig contexts, delete exported backups) and a verification that nothing stray remains — **including backend leftovers on kind nodes** (host-path directories).
11. **Every performance/capacity claim** is tied to a measurement command or labelled "typical range — measure yours". Never quote IOPS, latency, throughput, attach times, timeouts, or provider limits as fact without `[VERIFY]` or a derivation. Laptop-lab numbers are labelled as such.
12. Call out WSL2 vs native Linux differences (virtual disk, filesystem type of `/var/lib/docker`, I/O behavior, `fsync` semantics on virtual disks, space reclamation) wherever they alter outcomes.
13. Validate every manifest mentally against server-side dry-run semantics: PVC↔PV↔StorageClass names and access modes align, `volumeClaimTemplates` names match `volumeMounts`, selectors match labels, snapshot `source`/`dataSource` fields are correct (`apiGroup`, `kind`, `name`), operator CR fields exist for the stated version, namespaces consistent, and cross-file references resolve.

# 11. PEDAGOGY RULES

- **Follow the data:** for every feature, first show where the bytes live and which object/controller/driver moves, copies, or protects them; then show the configuration.
- **One running example** (stateful data platform) evolving through the folder: ephemeral → persistent → dynamically provisioned → snapshotted → identity-stable → operator-managed → measured → topology-aware → diagnosable → recoverable.
- **Show failure on purpose:** every unit has at least one lab where the learner loses (throwaway) data or availability and diagnoses/recovers it with evidence — always preceded by a stated data-safety plan.
- **Diagrams** for the PV/PVC/StorageClass chain, the CSI controller/node architecture, the volume lifecycle (provision → attach → mount → … → reclaim), snapshot/restore object flow, StatefulSet identity, operator control loop and failover, I/O stack (app → page cache → fs → block → device), zonal topology and volume binding, orphan discovery flow, and the "backup hierarchy" (snapshot < replica < PITR < offsite immutable).
- Plain, precise English; no filler or marketing; define acronyms at first use; consistent terms (*volume, claim, class, driver, snapshot, backup, replica, failover, recovery point, recovery time*).
- Honest trade-offs; avoid "always/never" without reasons and exceptions; stay vendor-neutral on storage products.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified before final submission.** You act as author first, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Authoring-time rules
- Base technical claims on **official documentation and specifications**: Kubernetes docs (Volumes, Persistent Volumes, Storage Classes, Volume Snapshots, Volume Snapshot Classes, CSI Volume Cloning, Expanding PVCs, StatefulSets, Ephemeral Volumes, Storage Capacity, Node-specific Volume Limits, Topology-aware scheduling), the CSI specification, Kubernetes CSI project docs (external-provisioner, external-snapshotter, external-resizer, csi-driver-host-path), the chosen operator's docs (CloudNativePG), PostgreSQL official documentation (continuous archiving and PITR, backup and restore, WAL), MinIO docs (Awareness/dependency), Strimzi/Kafka docs (Awareness), `fio` documentation, Linux kernel/filesystem docs (ext4/xfs), Kubernetes version-skew/deprecation policies, CIS Kubernetes Benchmark, NSA/CISA Kubernetes Hardening Guidance, Google SRE Book/Workbook. Cite by **document name and section/title**, not invented URLs; give a URL only if certain it is canonical, else mark `[VERIFY]`.
- **Do not fabricate:** versions, feature-gate states or graduation stages, API versions or fields, driver capabilities, operator CRD fields/behaviors, metric names, flags, defaults, timeouts, IOPS/latency/throughput numbers, provider limits or prices, benchmark results, CVE IDs, quotes, or tool behaviors. Derive numbers from stated commands or label `[ILLUSTRATIVE]`.
- Mark uncertainty with `[VERIFY]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, or `[ASSUMPTION]`.
- Keep a running **Claim Register** for every non-trivial factual claim.

## 12.2 Mandatory multi-pass self-audit (before delivering each part)

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 11 units, all Section 5 sections, all Section 6 topics, L1–L4, all "Must include" labs. | Any gap. |
| 2 | **Technical accuracy** | Every apiVersion/kind/field/parameter/flag/command is real and correctly used; descriptions of volume lifecycle, binding, snapshot, expansion, StatefulSet and operator behavior are correct; mentally execute each lab. | Invented or misused syntax/behavior. |
| 3 | **Executability** | YAML valid and internally consistent (class/claim/volume names, access modes, `volumeClaimTemplates` vs `volumeMounts`, snapshot sources, operator CR fields); scripts pass ShellCheck in principle; labs have steps, evidence, cleanup, disk footprint; manifests pass server-side dry-run once CRDs exist. | Broken or ambiguous step. |
| 4 | **Currency** | Version- and feature-sensitive items tagged; no deprecated/removed API or practice taught as current (e.g., `snapshot.storage.k8s.io/v1beta1`, in-tree cloud volume plugins as current, `Recycle` reclaim policy, `storage.k8s.io/v1beta1`, `kubectl` generators, annotation-based `volume.beta.kubernetes.io/storage-class`, assuming `persistentVolumeClaimRetentionPolicy` or `ReadWriteOncePod` behavior without version tags, assuming a backup mechanism for the operator without checking current docs). | Stale or untagged claim. |
| 5 | **Data-safety & security correctness** | No destructive step without data-safety preface; no overclaims (snapshot ≠ backup; replica ≠ backup; StatefulSet ≠ HA database; operator ≠ tested recovery; `Retain` ≠ backup; etcd snapshot ≠ PV data; hostpath CSI ≠ production storage; encrypted-at-rest ≠ encrypted backups); no insecure practice shown as good; sensitive-data handling for snapshots/backups stated. | Overclaim, unlabeled destructive step, or unlabeled insecure example. |
| 6 | **Fabrication scan** | Hunt for invented numbers, versions, CRD fields, parameters, metric names, outputs shown as measured, benchmark claims, citations, provider limits. | Any unsupported specific. |
| 7 | **Pedagogical consistency** | True beginner→advanced ramp; no concept used before introduced (e.g., no snapshot restore before PVC `dataSource`; no operator before StatefulSet); consistent terms; running example evolves coherently. | Undisclosed forward dependency; drift. |
| 8 | **Cross-consistency** | Questions test only taught content; capstone deliverables map to units; checklists match lessons; README matches content; the kind-fidelity table matches every lab caveat; the single-operator (CloudNativePG) and single-CSI-lab-driver decisions are applied consistently across Units 2, 3, 5, 7, and the capstone. | Orphan item; contradiction. |
| 9 | **Adversarial review** | As a skeptical staff SRE and a DBA: list the 10 most likely objections ("what would lose data, mislead, or fail on a real production cluster?") and resolve each. | Unresolved objection. |
| 10 | **Lab safety & feasibility** | Labs run on kind within 4 CPU / 8 GB / 30 GB, are idempotent and context-guarded, destroy only lab-created throwaway data, state disk footprint, use no paid resources, and clean up including node-level host paths. | Hidden cost, disk/RAM blowout, wrong-cluster risk, unprotected destructive step, leftover state. |

## 12.3 Audit artifacts inside the syllabus (final appendices)

**Appendix A — Claim Register:** `ID | Unit | Claim | Source (document + section) | Confidence (High/Med/Low) | Tag`. ≥ **80 entries**, covering every version-sensitive, feature-graduation, data-safety, and security-relevant claim.

**Appendix B — Audit Report:** `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk` for passes 1–10. Be candid; report real defects.

**Appendix C — Human Verification Checklist:** every `[VERIFY]` / `[VERSION-SENSITIVE]` item grouped by component (PV/PVC/StorageClass fields, CSI hostpath driver, external-snapshotter and snapshot CRD versions, volume expansion behavior, StatefulSet fields and retention policy, CloudNativePG CRD fields and backup/PITR mechanism, MinIO/object-store dependency, PostgreSQL backup functions/PITR docs, Strimzi/Kafka awareness items, fio flags, scheduler volume-binding behavior, kind node/host-path behavior), each with *what to check*, *where (official doc name)*, *how to test with one command*. Closable by a reviewer in under 6 hours.

**Appendix D — Known Limitations and Assumptions:** what is out of scope (production CSI/cloud storage specifics, Ceph/Rook/Longhorn deep dives, DR programs and immutability — M13, multi-cluster replication — M14, full observability — M11, secret management — M09), assumed Kubernetes/tool versions, kind fidelity limits, WSL2 caveats, anything unverified.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace a human running the labs on a real kind cluster, and that **no restore procedure should be trusted until the learner has executed it successfully**.

## 12.4 Trust rules
- If a pass finds a defect you cannot confidently fix, leave it visible as `OPEN` in Appendix B and list it in Appendix C. Never hide uncertainty.
- Never claim a command or manifest "was run/tested" unless it actually was. Use "expected output (representative)".
- Never claim verification against live documentation unless you consulted it; otherwise say "written from knowledge of the documentation; verify against current docs".

# 13. OUTPUT FORMAT

- **One Markdown document:** `SYLLABUS-Kubernetes-Storage-and-Stateful-Data-Workloads.md`.
- Begin with: title, abstract paragraph, metadata block (`Module: M05`, `Stage: 2E`, `Estimated total time`, `Last reviewed`, `Assumed tool baseline`), and a **linked table of contents** to all units and appendices.
- Then Units 0–10 in order, then Appendices A–E.
- Headings: `#` title, `##` units, `###`/`####` below; tables for comparisons; fenced code with language tags; mermaid for diagrams.
- Cross-link units with relative links to sibling target files.
- **Depth target:** Units 1–8 each ≥ 2,500 words of teaching text excluding code and manifests; ≥ 130 practice questions; capstone with complete code. **Do not compress to fit**—use the Delivery Protocol.
- No placeholder text, no "etc." in required lists, no "exercise left to the reader" for required deliverables.

# 14. DELIVERY PROTOCOL

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 0, Unit 1 |
| 2 | Units 2, 3 |
| 3 | Units 4, 5 |
| 4 | Units 6, 7 |
| 5 | Unit 8 |
| 6 | Unit 9 (practice questions) |
| 7 | Unit 10 (capstone, full code) |
| 8 | Appendices A–E, including the cross-part audit |

Rules:
- End each part with: `PART n/8 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-unit audit (passes 1–10, scoped) **before** printing each part; maintain the Claim Register throughout.
- Part 8 runs the cross-part audit (passes 7, 8, 9 especially) and lists every correction to earlier parts as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If nearing the length limit, stop at a clean section boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 8 print: "Concatenate Parts 1–8 in order into `SYLLABUS-Kubernetes-Storage-and-Stateful-Data-Workloads.md` and apply all listed corrections."

# 15. DEFINITION OF DONE

- [ ] All 11 units present in order; Units 1–8 each have L1–L4 and sections N.0–N.14.
- [ ] Every Section 6 topic taught at its stated level, with every kind-simulation limit stated honestly.
- [ ] Exactly one CSI lab driver (hostpath) and one hands-on operator (CloudNativePG) chosen and applied consistently; everything else is clearly Awareness.
- [ ] The "snapshot ≠ backup ≠ replica ≠ HA" distinction is taught, tested, and proven in labs; at least one **PITR restore** and one **snapshot restore** are executed with verification.
- [ ] ≥ 130 practice questions with model answers and distractor analysis, including "is this a backup?" classification and data-location tracing.
- [ ] Capstone has complete runnable code, acceptance criteria, rubric weighted toward proven restores, `make verify`, and a blank measurement template.
- [ ] Every lab has context guard, data-safety preface for destructive steps, steps, expected evidence, cleanup incl. node host-paths, and a disk footprint; all fit the local baseline.
- [ ] No fabricated versions, fields, parameters, metric names, capabilities, numbers, or citations; every uncertainty tagged.
- [ ] Appendices A–E present; Claim Register ≥ 80; passes 1–10 reported candidly.
- [ ] Running example evolves coherently across all units.
- [ ] Forward references (M01–M04, M06, M08–M15, M17) explicit and not half-taught; M13 handoff stated precisely.
- [ ] A human can close every open item in under 6 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/8**. Do not ask clarifying questions; record an `[ASSUMPTION]` where information is missing and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. Use one long conversation across all 8 parts so the Claim Register and running example stay consistent.
2. AI self-audit is not independent. Run the labs on a real kind cluster and close every `[VERIFY]` item against current official docs. **Do not trust any restore procedure until you have executed it yourself.**
3. Highest fabrication risk, check first:
   - CloudNativePG: CRD names and fields, and the current recommended backup/PITR mechanism. This has changed across versions.
   - The CSI hostpath driver install steps on kind.
   - The `snapshot.storage.k8s.io` API version and snapshot controller setup.
   - `persistentVolumeClaimRetentionPolicy` and node-shutdown feature stages.
   - The StatefulSet volume-expansion workaround.
   - Volume force-detach timing (the prompt tells the LLM not to quote numbers).
   - PostgreSQL backup function names across versions.
4. Scope decisions I made, which you can change:
   - The tooling map lists CSI, snapshots and database operators as Awareness, but this folder has dedicated modules for them. The prompt teaches them at working depth.
   - Exactly one lab CSI driver (hostpath, a teaching driver, not production storage) and exactly one hands-on operator (CloudNativePG) are used. Kafka/Strimzi and Longhorn/Ceph/Rook are Awareness or optional, because they will not fit 8 GB of RAM and 30 GB of disk.
5. Disk is the tightest constraint in this module, more than RAM. The prompt requires a disk footprint on every lab and cleanup that includes host-path leftovers on kind nodes. On WSL2 the virtual disk may not shrink on its own.
6. Many labs destroy data on purpose. The prompt requires a data-safety preface and throwaway data for each. Keep the real cluster and the lab cluster separate.
