# Storage Troubleshooting and Orphaned Volumes

> **Stage:** Stage 2E — Production DevOps & Platform Engineering  
> **Module:** M05 — Kubernetes Storage and Stateful Data Workloads  
> **Unit:** 8 — Storage troubleshooting and orphaned volumes  
> **Target:** `08-storage-troubleshooting-and-orphaned-volumes.md`  
> **Lab:** Zero-budget `kind` on WSL2 Ubuntu or native Linux; at most three workers.

## Safety contract

**Data safety comes before availability, cleanup speed, or a green dashboard.** Before any destructive fix, establish either (a) a tested, restorable copy and supported recovery procedure, or (b) that all affected data is intentionally disposable. If ownership, backend state, filesystem health, or recoverability is uncertain, stop destructive actions and escalate.

- **Roadmap requirement** — explicitly required for Unit 8.
- **Engineering context** — practical guidance to apply using workload-specific judgment.
- **[VERIFY]** — check the official documentation for the exact Kubernetes version, CSI driver, provisioner, distribution, filesystem, or operator.

Sample output is labelled **Expected output (representative; not executed here)** unless explicitly stated otherwise. This lesson and its lab were not executed in a live cluster.

## 8.0 Why this matters in production

Storage incidents are deceptively dangerous. A Pod may be `Pending`, a PVC may be `Terminating`, or a PV may be `Released`; none of those statuses alone tells you whether the underlying data is safe to delete. Kubernetes objects describe intended and observed state. The backend may still contain a disk, a filesystem may be read-only, a CSI controller may be unavailable, or a retained volume may be the only copy of a customer's data.

A namespace may be deleted after a service is retired, but a PV using reclaim policy `Retain` can preserve the backend volume. That resource may be a recovery asset, an intentionally retained record, or a genuine orphan candidate. Deleting it based only on age can cause irreversible data loss; leaving it unowned forever can create cost and security exposure. The solution is a controlled evidence-and-ownership workflow, not a blanket cleanup command.

A PVC can remain `Pending` because of a missing StorageClass, an unhealthy provisioner, quota restrictions, topology mismatch, or normal `WaitForFirstConsumer` behavior while no schedulable consumer Pod exists. Status is a symptom. Events, controller logs, driver logs, node state, and backend inventory establish root cause.

The operating sequence is:

**Observe object states → read events → check the owning controller/driver → check the node → check the backend → fix safely → verify → document.**

Skipping directly to deletion or finalizer removal can hide the real failure and discard the only recoverable copy.

This unit follows M05 Units 1–7. Unit 1 (`01-volumes-persistentvolumes-and-persistentvolumeclaims.md`) covers PV/PVC lifecycle and reclaim policy. Unit 2 (`02-storageclasses-dynamic-provisioning-and-csi-drivers.md`) covers StorageClass and CSI architecture. Unit 3 (`03-volume-snapshots-cloning-and-expansion.md`) covers snapshots and expansion. Unit 4 (`04-statefulset-storage-patterns-and-stable-identity.md`) covers StatefulSet claim behavior. Unit 5 (`05-running-databases-and-brokers-with-operators.md`) covers application/operator recovery. Unit 6 (`06-storage-performance-iops-throughput-and-latency.md`) covers performance symptoms. Unit 7 (`07-data-locality-zonal-failure-and-volume-affinity.md`) covers topology conflicts. The capstone is `Projects/01-stateful-data-platform-with-snapshots-and-recovery.md`. M03 covers scheduling, quotas, RBAC, and audit foundations; M13 covers formal backup/DR; M15 covers cost governance. These are boundaries and cross-references, not replacement content.

## 8.1 Learning objectives

You will be able to:

1. Follow the read-only-first incident sequence and record auditable evidence.
2. Interpret PVC/PV states without assuming a status proves data is disposable.
3. Distinguish provisioning, scheduling, attachment, mounting, filesystem, permission, capacity, and application failures.
4. Use `kubectl`, events, CSI logs, node inspection, and backend inventory without exposing credentials.
5. Diagnose the 19 storage fault classes in Section 8.4.
6. Explain PVC protection and other finalizers and why forced removal is risky.
7. Define an orphaned backend resource and distinguish it from intentionally retained or temporarily detached storage.
8. Reconcile Kubernetes objects with backend disks, snapshots, attachments, and node-local directories.
9. Run a report-only orphan audit and understand false positives/negatives.
10. Quarantine a candidate, recheck references, pass a data-safety gate, and clean up only an approved lab resource.
11. Design ownership metadata, deletion controls, inventory reporting, and incident handoffs.
12. Complete the gauntlet and traceability review without claiming unrun tests.

## 8.2 Prerequisites and mental model

### Core objects and scope

| Object | Scope | Represents | Does not prove |
|---|---|---|---|
| PVC (`PersistentVolumeClaim`) | Namespaced | A workload's storage request and binding state | Backend bytes exist, are healthy, or safe to delete |
| PV (`PersistentVolume`) | Cluster-scoped | Provisioned or statically defined storage | Complete inventory of all backend resources |
| StorageClass (`SC`) | Cluster-scoped | Provisioning policy, parameters, reclaim policy, binding mode | Provisioner/driver health or support for every parameter |
| VolumeAttachment | Cluster-scoped | Attach/detach intent for applicable CSI drivers | Manual deletion safely detaches the backend volume |
| VolumeSnapshot | Namespaced CRD when installed | User-facing snapshot request/state | Tested restore or application-consistent backup |
| VolumeSnapshotContent | Cluster-scoped CRD when installed | Cluster representation of backend snapshot | Snapshot is unreferenced or safe to delete |
| CSI driver/sidecars | Driver-specific workloads | Provision, attach, mount, resize, snapshot integration | Uniform behavior across drivers |
| Backend disk/snapshot | Provider/storage-system scope | Actual resource and data | Kubernetes still has an object or owner record |

PVCs are namespaced; PVs, StorageClasses, and VolumeAttachments are cluster-scoped. Query separately for clarity and to make permission requirements obvious.

### Lifecycle concept map

```text
PVC + StorageClass
       |
       v
Provision or select PV ----> bind PVC
       |                         |
       v                         v
backend volume exists       Pod is scheduled
                                 |
                                 v
                       attach (if applicable)
                                 |
                                 v
                              mount
                                 |
                                 v
                         application I/O
                                 |
                                 v
                         unmount / detach
                                 |
                                 v
PVC deleted / claim released
       |
       +--> reclaimPolicy Delete: provisioner/backend cleanup may occur
       |
       +--> reclaimPolicy Retain: PV/data may remain for deliberate recovery
```

This is conceptual, not universal. Local PVs do not behave like cloud block volumes; some volumes do not require attachment; CSI capabilities differ.

### Fault-domain/component map

```text
Workload / Operator / StatefulSet
              |
              v
           Pod + PVC
              |
       +------+------+
       |             |
   Scheduler    PV/PVC controllers
       |             |
       +------v------+
             PV / SC
                |
       attach/detach controller ---- VolumeAttachment (when used)
                |
       CSI controller sidecars ---- CSI controller plugin
                |
       kubelet ---- CSI node plugin
                |
       node kernel / filesystem / mount
                |
       storage backend / disk / snapshot service
```

A mount error may be caused by missing backend storage, attachment, node plugin, unsupported filesystem, permissions, credentials, or a kernel I/O error. Identify the failing layer from evidence.

### Status vocabulary: symptom, not verdict

- **PVC `Pending`:** not yet bound. It may be expected under WFFC until a consuming Pod is schedulable; other causes include class, PV matching, provisioner, quota, or topology.
- **PVC `Bound`:** bound to a PV; not proof of successful mount, usable filesystem, free bytes/inodes, or application health.
- **PVC `Lost`:** Kubernetes has lost the expected bound PV relationship; it does not prove backend bytes are irrecoverable.
- **PV `Available`:** currently available for binding according to Kubernetes state; not proof of backend ownership.
- **PV `Bound`:** associated with a claim; verify that claim and its workload.
- **PV `Released`:** previous claim was released, but reclaim/reuse may need deliberate action. Not automatically reusable or safe to delete.
- **PV `Failed`:** failure condition; inspect events, controller/driver, and backend.
- **VolumeAttachment:** attach/detach intent for drivers that use it; interpret with backend state.
- **`FailedScheduling`:** no feasible placement; read the detailed reason.
- **`FailedAttachVolume` / `FailedMount`:** common storage event families; exact reason/message can vary.
- **`ProvisioningFailed`:** provisioning attempt failed; inspect PVC events and provisioner logs.

Events can expire, be aggregated, or omit backend detail. Preserve logs early. An event is evidence, not necessarily the complete diagnosis.

### Eight-step incident sequence

1. **Observe object states:** record context, namespace, names, UIDs, status, and recent changes.
2. **Read events:** correlate timestamps and reporting components.
3. **Check owning controller/driver:** identify the actual provisioner, CSI controller, node plugin, snapshot controller, or operator.
4. **Check the node:** inspect readiness, capacity, mounts, kernel errors, and kubelet/node-plugin logs where permitted.
5. **Check the backend:** reconcile stable IDs and lifecycle records with authoritative inventory.
6. **Fix safely:** choose the least destructive action supported by evidence.
7. **Verify:** check Kubernetes state and application data/health.
8. **Document:** record actions, avoided actions, residual risk, owner, and follow-up.

### Read-only-first toolkit

```bash
kubectl config current-context
kubectl version
kubectl get nodes -o wide
kubectl get pv
kubectl get pvc -A
kubectl get storageclass
kubectl get volumeattachment
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

For a workload:

```bash
kubectl -n <namespace> describe pod <pod-name>
kubectl -n <namespace> describe pvc <pvc-name>
kubectl get pv <pv-name> -o yaml
kubectl describe storageclass <storageclass-name>
kubectl -n <namespace> get events --sort-by=.metadata.creationTimestamp
```

The sort key is commonly supported; event retention and ordering vary. PVCs are namespaced, while PV/SC/VolumeAttachment are cluster-scoped.

Discover CSI components before inspecting logs:

```bash
kubectl get csidrivers
kubectl get pods -A -o wide
kubectl get deployments,statefulsets,daemonsets -A
```

After identifying the real driver and its namespace/container names:

```bash
kubectl -n <driver-namespace> logs <controller-pod> -c <controller-container> --since=30m
kubectl -n <driver-namespace> logs <node-plugin-pod> -c <node-plugin-container> --since=30m
```

Do not dump environment variables or Secret data. Redact credentials, tokens, volume handles, account IDs, and internal hostnames before external sharing.

Node-level read-only checks (run in the correct node environment):

```bash
df -h
df -i
lsblk
findmnt
mount
dmesg --ctime | tail -n 100
```

`dmesg` may be restricted/unavailable in containers or WSL2. `kubectl debug node/<node>` can create a debug Pod and require elevated permissions; **[VERIFY]** Kubernetes version, distribution policy, and debug profile. Alternatives include approved SSH/console access, node-agent diagnostics, or inspecting the exact kind node container through the installed runtime. Kind may use Docker, Podman, or nerdctl; do not assume Docker.

Do not run `fsck`, remount read-write, format, or delete files during initial diagnosis.

### Incident record template

```text
Incident ID:
Start time and timezone:
Cluster/context/Kubernetes version:
Namespace/object names/object UIDs:
Workload owner and impact:
Symptom and first observed event:
Recent changes:
PVC/PV/StorageClass/VolumeAttachment state:
CSI controller/node-plugin state:
Node/filesystem evidence:
Backend ID and authoritative inventory result:
Data-safety status: tested restore / disposable / uncertain (stop-work)
Actions taken:
Actions deliberately avoided:
Post-fix Kubernetes verification:
Application/data verification:
Recovery point and recovery time:
Residual risk:
Next owner / due date:
Follow-up prevention controls:
```

## 8.3 Level 1 — Beginner: systematic diagnosis

### Read events with a question in mind

**Expected output (representative; not executed here):**

```text
Warning  FailedScheduling  default-scheduler
0/4 nodes are available: ... volume node affinity conflict ...
```

This suggests a scheduling/volume-topology mismatch. Verify PV affinity, node labels, and Pod constraints before concluding.

**Expected output (representative; not executed here):**

```text
Warning  FailedMount  kubelet
MountVolume.SetUp failed for volume "data": ...
```

Kubelet reports a mount setup failure; the cause may be attachment, node plugin, filesystem, credentials, permissions, or backend state.

### Status-first table

| State | First question | Evidence | Do not assume |
|---|---|---|---|
| PVC Pending | Is a consumer Pod present? Is WFFC expected? | PVC describe, class, Pod events, provisioner logs | Storage is broken |
| PVC Bound, Pod ContainerCreating | Is attach/mount failing? | Pod events, PV, VolumeAttachment, CSI logs | Bound means mounted |
| PV Released | Is retention intentional? | claimRef, reclaim policy, owner, backend ID | It is orphaned |
| PVC Terminating | Is a Pod still using it? | Pod volume references, finalizers, controller logs | Finalizer is stale |
| PVC Lost | Is the PV missing, failed, or backend unavailable? | PVC/PV YAML, backend inventory | Data is irrecoverable |
| Read-only filesystem | Are kernel/filesystem errors present? | mount state, dmesg, backend health | Remounting RW is safe |
| Snapshot not ready | Are CRDs/controller/class/driver available? | snapshot objects/events and logs | Snapshot is a valid backup |
| Slow I/O | Is this latency, throughput, saturation, or capacity? | Unit 6 metrics, backend telemetry | It is a mount failure |

### Why WFFC can be normal

`WaitForFirstConsumer` delays binding/provisioning until a Pod uses the PVC so scheduling constraints can inform topology. A PVC can be Pending before a consumer Pod exists. If a consumer exists, inspect events for resource, affinity, taint/toleration, topology-spread, capacity, or driver problems. See Unit 2 and the official Kubernetes StorageClass documentation.

### Distinguish the failure stages

1. **Provisioning:** no usable PV created/selected.
2. **Binding:** PVC and PV are not bound.
3. **Scheduling:** no feasible node.
4. **Attachment:** backend/driver cannot attach (if applicable).
5. **Mount:** node cannot stage/publish or mount.
6. **Filesystem:** full, damaged, or read-only filesystem.
7. **Permissions:** UID/GID, ownership, mount options, or security policy.
8. **Application:** storage is mounted but application reports corruption, recovery, or consistency errors.
9. **Backend inventory:** resource exists without Kubernetes object, or an object references a missing resource.

A resize does not fix an attachment error; a permission change does not repair I/O errors; deleting a PV does not repair a CSI controller.

## 8.4 Level 2 — Intermediate: troubleshooting decision trees

Every case follows symptom → read-only checks → likely cause → distinguishing evidence → safe fix → verification → prevention. Establish data safety before mutation.

### 8.4.1 PVC Pending: no matching StorageClass

- **Symptom:** Pending; events suggest no matching PV or provisioning issue.
- **Checks:** `kubectl -n <ns> describe pvc <claim>`; `kubectl get sc`; inspect claim class, size, access mode, and volume mode.
- **Likely cause:** no matching static PV or the class uses an unavailable provisioner.
- **Distinguish:** compare claim requirements with PVs and actual class/provisioner.
- **Safe fix:** if no data exists, create a reviewed claim/class or matching static PV. Do not change bound storage semantics casually.
- **Verify/prevent:** intended PV binds and test Pod mounts; validate class names in CI.

### 8.4.2 No default StorageClass or wrong class name

- **Symptom:** claim omits class with no default, or names a nonexistent class.
- **Checks:** `kubectl get sc`; PVC YAML; `kubectl describe pvc`.
- **Distinguish:** omitted class differs from explicit `storageClassName: ""`; a typo is visible in the claim.
- **Safe fix:** correct the manifest after confirming intended policy. Changing the global default needs review.
- **Verify/prevent:** claim uses intended class; test environment config in CI.

### 8.4.3 Provisioner/CSI controller down

- **Symptom:** provisioning retries or fails.
- **Checks:** class provisioner; `kubectl get csidrivers`; controller Pods/events/logs.
- **Distinguish:** crashed controller vs backend authentication/capacity/parameter error.
- **Safe fix:** restore the actual controller or credentials via its runbook; do not install a random driver.
- **Verify/prevent:** provisioning succeeds and backend inventory matches PV; alert on controller health.

### 8.4.4 Quota or size policy

- **Symptom:** claim denied or unprovisioned with quota/policy events.
- **Checks:** `kubectl describe resourcequota -n <ns>`; LimitRange/admission events; requested size.
- **Distinguish:** namespace quota vs backend quota/capacity vs policy rejection.
- **Safe fix:** request approved quota/capacity or right-size an unprovisioned request only after confirming data needs.
- **Verify/prevent:** provisioning succeeds within policy; alert on quota headroom.

### 8.4.5 Topology/volume affinity

- **Symptom:** Pod Pending; volume node-affinity conflict or no eligible node.
- **Checks:** PV `spec.nodeAffinity`, node labels, Pod affinity, taints/tolerations, spread constraints, `allowedTopologies`.
- **Distinguish:** PV tied to a zone/hostname, class excludes nodes, or Pod constraints exclude compatible nodes.
- **Safe fix:** restore eligible capacity or recover via supported replica/backup workflow; never remove affinity to force a mount.
- **Verify/prevent:** Pod runs on compatible node and data is checked; use Unit 7 topology review.

### 8.4.6 WFFC waiting for consumer

- **Symptom:** PVC Pending; class uses WFFC.
- **Checks:** list Pods and describe claim/consumer.
- **Distinguish:** no consumer is normal; consumer with scheduling errors needs further diagnosis.
- **Safe fix:** create/repair intended consumer or address scheduling constraint; do not change binding mode blindly.
- **Verify/prevent:** claim binds after schedulable consumer; include consumer in smoke tests.

### 8.4.7 ContainerCreating: attach/mount failure

- **Symptom:** `FailedAttachVolume` or `FailedMount`.
- **Checks:** Pod events, PV/PVC, VolumeAttachment where applicable, CSI controller/node plugin logs.
- **Distinguish:** backend attach, stale attachment, plugin, filesystem, mount options, permissions, credentials.
- **Safe fix:** repair evidenced layer using driver runbook; do not delete PVC or force-detach by default.
- **Verify/prevent:** mount and application read/write succeed; monitor CSI errors.

### 8.4.8 Multi-Attach/stale attachment after node failure

- **Symptom:** replacement Pod cannot attach a volume previously used elsewhere.
- **Checks:** old node state, VolumeAttachment, Pod events, driver logs, backend attachment state.
- **Distinguish:** old node still owns attachment, backend detach pending, or backend restricts multi-node attachment.
- **Safe fix:** verify fencing/data safety; follow official driver/provider procedure. If uncertain, stop and escalate.
- **Verify/prevent:** backend confirms safe attachment and app data; rehearse node-loss recovery.
- **[VERIFY]:** no universal detach timeout or force-detach behavior exists.

### 8.4.9 Mount permission failure

- **Symptom:** process gets `Permission denied` on mounted data.
- **Checks:** `runAsUser`, `runAsGroup`, `fsGroup`, `fsGroupChangePolicy`; `id`, `stat`, `findmnt`; driver docs.
- **Distinguish:** ownership/mode, root-squash, SELinux/AppArmor, driver policy, or filesystem mismatch.
- **Safe fix:** adjust reviewed security context or permissions. Do not recursively `chown` unknown production data.
- **Verify/prevent:** intended non-root process can access only required paths; test images.
- **[VERIFY]:** fsGroup behavior varies by volume type, driver, and Kubernetes version.

### 8.4.10 Missing CSI Secret/invalid credentials

- **Symptom:** provisioning/attach/stage/mount fails with authentication symptoms.
- **Checks:** Secret references and namespace; verify Secret exists without printing data; controller/node logs.
- **Distinguish:** missing reference, expired credential, wrong key/namespace, insufficient backend permission, backend outage.
- **Safe fix:** restore/rotate via approved secret management; do not paste Secret YAML or env vars into tickets.
- **Verify/prevent:** operation succeeds; credential rotation and expiry alerts.

### 8.4.11 Volume full: bytes, inodes, backend capacity

- **Symptom:** writes fail with `No space left on device`.
- **Checks:** `df -h` (bytes), `df -i` (inodes), PVC capacity, backend metrics, application growth/retention.
- **Distinguish:** filesystem bytes vs inodes; PVC request vs filesystem size vs thin backend capacity; deleted-but-open files.
- **Safe fix:** application retention/cleanup or supported expansion after backup check; never `rm -rf` unknown data.
- **Verify/prevent:** bytes/inodes recover and writes succeed; alert on both and forecast growth.

### 8.4.12 Read-only filesystem after I/O error

- **Symptom:** writes fail; mount is read-only or kernel reports I/O/filesystem errors.
- **Checks:** preserve app logs and `dmesg` where permitted; inspect mount state, node and backend.
- **Distinguish:** protective read-only state after errors vs configured read-only mount vs permissions.
- **Safe fix:** stop unsafe writes and follow storage/filesystem recovery. Do not blindly remount read-write.
- **Verify/prevent:** qualified integrity checks and application recovery; monitor I/O errors.
- **Safety:** `fsck` only on an **unmounted** filesystem with an appropriate backup/recovery plan. Never run it on a mounted production filesystem.

### 8.4.13 PVC expansion stuck

- **Symptom:** request grew but capacity/filesystem size did not.
- **Checks:** `allowVolumeExpansion`, PVC conditions/events, CSI resizer/controller logs, filesystem size.
- **Distinguish:** class/backend unsupported; controller resize pending; node filesystem resize pending; driver error.
- **Safe fix:** follow exact backend expansion procedure; do not shrink as workaround.
- **Verify/prevent:** PVC capacity and `df -h` agree; test expansion against actual driver.
- **[VERIFY]:** online/offline expansion and version requirements are driver-specific.

### 8.4.14 Snapshot not ready

- **Symptom:** VolumeSnapshot never reaches ready.
- **Checks:** snapshot CRDs, controller, class, source claim/PV, events, snapshotter and driver logs.
- **Distinguish:** missing API/controller/class, unbound source, unsupported driver capability, credential/backend error.
- **Safe fix:** repair only compatible snapshot components; do not delete snapshots with unknown retention.
- **Verify/prevent:** restore to disposable target and validate application data; readiness alone is not a backup test.
- **[VERIFY]:** snapshot APIs are CRDs and require compatible controller/sidecar and CSI support.

### 8.4.15 StatefulSet Pod blocked by missing/pending/retained PVC

- **Symptom:** ordinal Pending; expected claim absent, pending, retained, or bound to incompatible PV.
- **Checks:** `volumeClaimTemplates`, claim name, Pod events, PV affinity, claim retention, operator status.
- **Distinguish:** claim never created, retained after scale-down/delete, provisioning failure, topology conflict.
- **Safe fix:** use documented StatefulSet/operator workflow; do not create an empty replacement for a database without verifying member identity/data.
- **Verify/prevent:** correct ordinal data and membership; document retention/scale-down.

### 8.4.16 PVC Terminating with pvc-protection

- **Symptom:** PVC remains Terminating with `kubernetes.io/pvc-protection`.
- **Checks:** find Pods in namespace referencing claim; inspect Pod termination and controller events.
- **Distinguish:** Pod still uses claim vs no references but controller/reconciliation issue.
- **Safe fix:** stop owning workload through its controller/operator and confirm references clear. Escalate if finalizer remains unexpectedly.
- **Verify/prevent:** deletion completes through normal flow; approved retirement process.
- **Do not patch finalizer first:** protection exists to prevent deleting a claim still used by a Pod.

### 8.4.17 PV Terminating or Released

- **Symptom:** PV is Terminating or `Released`.
- **Checks:** PV YAML, finalizers, claimRef, reclaim policy, CSI handle if any, events, backend inventory.
- **Distinguish:** claim still exists; Retain intentional; provisioner cleanup pending; backend deletion failed; stale object.
- **Safe fix:** establish ownership/backend state. For Retain, use reviewed recovery/rebind procedure. For Delete, verify actual cleanup. Do not remove finalizers just to clear status.
- **Verify/prevent:** Kubernetes/backend inventory reconciles; data recovered and checked if needed.
- **[VERIFY]:** claimRef/finalizer behavior depends on API version and provisioner.

### 8.4.18 PVC Lost or backend inventory mismatch

- **Symptom:** PVC Lost, PV missing/Failed, or backend inventory disagrees.
- **Checks:** object UIDs, claimRef, CSI handle, controller logs, audit logs, backend inventory, backup catalog.
- **Distinguish:** object deletion, backend deletion, stale metadata, failed operation, non-CSI PV.
- **Safe fix:** freeze cleanup; reconcile by stable ID with platform/backend owner; restore from verified replica/backup if required.
- **Verify/prevent:** data state is confirmed/documented; periodic inventory and deletion auditing.

### 8.4.19 Slow I/O

- **Symptom:** application latency rises or throughput falls.
- **Checks:** Unit 6 metrics, latency distribution, throughput, saturation/queue, filesystem capacity, backend telemetry, workload timeline.
- **Distinguish:** performance bottleneck vs mount error, full filesystem, throttling, network filesystem latency, database compaction/checkpoint.
- **Safe fix:** measured mitigation; avoid arbitrary tuning based on one sample.
- **Verify/prevent:** compare like-for-like measurements and app SLOs; establish baseline.
- **Cross-reference:** `06-storage-performance-iops-throughput-and-latency.md`.

### Compact cause/evidence table

| Symptom | Evidence raising confidence | Safe first action |
|---|---|---|
| PVC Pending | Events name class/provisioner/quota | Inspect claim, class, consumer and events |
| ContainerCreating | FailedAttach/FailedMount + CSI errors | Inspect Pod/PV/attachment and driver |
| Permission denied | UID/GID/mode/driver policy mismatch | Inspect security context and metadata |
| No space | `df -h` full or `df -i` exhausted | Distinguish bytes, inodes, backend |
| Read-only filesystem | Read-only mount plus kernel errors | Preserve evidence and stop unsafe writes |
| Snapshot not ready | Missing CRD/controller/class or driver error | Inspect snapshot chain |
| PV Released | Old claimRef and Retain policy | Inventory, quarantine, owner lookup |
| Slow I/O | Latency/queue/throughput telemetry | Baseline and isolate layers |


## 8.5 Level 3 — Advanced: orphan discovery and safe cleanup

### What is an orphaned volume?

A **candidate orphan** is a backend storage resource for which Kubernetes objects, workloads, and authoritative ownership records do not show a current intended owner. It is not safe to call a resource a true orphan until backend inventory and references have been reconciled.

Distinguish:
- **Intentionally retained:** kept under a documented retention/recovery policy.
- **Temporarily detached:** not attached to a node right now, but still owned by a workload/PV.
- **Released PV:** previous claim is gone, but data may be retained.
- **Failed provisioning residue:** a partial operation may have created backend resources without a completed PV.
- **True orphan candidate:** no workload, claim, snapshot/restore process, operator, attachment, or approved retention owner can be found.
- **Unknown:** evidence is incomplete. Unknown is not an orphan and must not be auto-deleted.

### Common sources of candidates

1. PVC deleted while PV reclaim policy is `Retain`.
2. Namespace deleted while backend data survives.
3. Failed provisioning leaves a backend volume or partial resource.
4. StatefulSet scale-down or claim-retention policy preserves claims.
5. Retained `VolumeSnapshotContent` or backend snapshots remain after user-facing snapshot deletion.
6. A stale `VolumeAttachment` remains after node failure.
7. Node loss interrupts detach/reconciliation.
8. Kubernetes PV inventory and backend disk inventory drift apart.
9. Manual backend changes remove a disk while Kubernetes still references it.
10. Controller/sidecar outage leaves cleanup incomplete.

### Kubernetes-side discovery

Inspect PV states but do not treat a phase as proof:

```bash
kubectl get pv -o wide
kubectl get pv -o yaml
kubectl get pvc -A -o wide
kubectl get volumeattachment
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

If snapshot APIs exist:

```bash
kubectl api-resources | grep -i snapshot
kubectl get volumesnapshots -A
kubectl get volumesnapshotcontents
kubectl get volumesnapshotclasses
```

If CRDs are absent, these queries may fail. Record that fact; do not install random CRDs during diagnosis.

Inspect PV fields where present: metadata UID/creation timestamp/labels/annotations; `spec.claimRef` including namespace/name/UID; reclaim policy; StorageClass; capacity/access modes/volume mode; `spec.csi.driver` and `volumeHandle` for CSI PVs; status phase/reason/message; finalizers and events. Not all PVs are CSI-backed; local, network filesystem, legacy, and manually provisioned PVs may use other identifiers.

### Auditable inventory with JSONPath and jq

```bash
kubectl get pv -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\t"}{.spec.storageClassName}{"\t"}{.spec.capacity.storage}{"\t"}{.spec.persistentVolumeReclaimPolicy}{"\t"}{.spec.claimRef.namespace}{"/"}{.spec.claimRef.name}{"\t"}{.spec.csi.driver}{"\t"}{.spec.csi.volumeHandle}{"\n"}{end}'
```

Missing fields may produce empty columns. That is not proof a PV is malformed; it may be non-CSI.

```bash
kubectl get pv -o json | jq -r '
  .items[] |
  [
    .metadata.name,
    (.spec.storageClassName // ""),
    (.spec.capacity.storage // ""),
    (.status.phase // ""),
    (.spec.persistentVolumeReclaimPolicy // ""),
    ((.spec.claimRef.namespace // "") + "/" + (.spec.claimRef.name // "")),
    (.spec.csi.driver // "non-CSI-or-unknown"),
    (.spec.csi.volumeHandle // ""),
    (.metadata.labels["storage.example.com/owner-team"] // "UNKNOWN"),
    (.metadata.creationTimestamp // "")
  ] | @tsv'
```

`storage.example.com/owner-team` is an illustrative organizational label, not a Kubernetes standard. Replace it with the approved key. This query is read-only and is not a deletion list.

### Backend-side reconciliation

The backend inventory is authoritative for whether a physical/logical disk or snapshot still exists. Reconcile Kubernetes PV identifiers with backend stable IDs, ownership tags, creation records, controller logs, and lifecycle audit records. Cloud-disk inventory is awareness-only; no paid cloud is required for the lab.

For kind, local provisioners may use a hostPath or directory inside a kind node container, but **do not guess the path**. Discover it from the actual provisioner configuration, PV attributes, container mounts, and official documentation. A path inside a node container is not necessarily the same path on the host. Different provisioners use different directories and cleanup semantics.

### Safe cleanup procedure — mandatory order

1. **Identify the resource and authoritative owner.** Record Kubernetes UID/name, backend stable ID, environment, and service/team owner.
2. **Confirm references.** Check Pods, PVCs, PVs, snapshots, restore jobs, attachments, operators, backup jobs, and backend workflows.
3. **Confirm data safety.** Require a tested/restorable copy or formal declaration that data is disposable. If uncertain, stop and escalate.
4. **Copy/verify if required.** Use a supported snapshot/export method and verify the copy. A snapshot may share a failure domain or account and is not automatically an independent backup.
5. **Quarantine.** Add a review label/annotation or external inventory state, owner/contact, reason, timestamp, and review deadline.
6. **Wait and recheck.** Re-run reference checks after the defined review period; verify no restore/retention workflow appeared.
7. **Approve exact cleanup.** A named reviewer authorizes the exact resource ID and backend operation. Use explicit apply and audit trail.
8. **Verify after deletion.** Check Kubernetes/backend inventories, capacity reclaimed, and residual objects.

Do not use age alone, PV phase alone, or detached status alone as a deletion criterion.

### Finalizers: why forced removal is dangerous

A finalizer can delay deletion until a controller completes cleanup or protection checks. `kubernetes.io/pvc-protection` helps prevent deleting a PVC while a Pod uses it. PV/CSI finalizers may coordinate backend deletion or track cleanup.

If a finalizer is forcibly removed, Kubernetes may forget the object before controller/backend work is complete. That can leave an orphan, break ownership tracking, or remove a useful recovery reference. A finalizer that remains after its condition is resolved may indicate controller or backend failure. Diagnose and restore the controller or follow the documented recovery process before considering manual intervention.

**[VERIFY]** Finalizer names and behavior depend on resource, Kubernetes release, and provisioner/driver. Check the exact API docs and controller implementation before modifying finalizers. This lesson does not recommend a generic finalizer-patching command.

### Recovering a PV with reclaim policy Retain

A retained PV can be a recovery asset. Its claim may be released while backend data remains. Recovery might involve verifying the backend ID, restoring a copy, deliberately handling the old claim reference, and binding a new claim under a controlled procedure. Exact steps depend on PV fields, API version, driver, claim UID, and whether the data is intended for reuse.

Safe principles:
- Record PV YAML and backend ID before changes.
- Verify no workload still references the data.
- Confirm data is recoverable and consistent.
- Test on a disposable PV first.
- Follow official Kubernetes reclaim/rebinding documentation and driver-specific recovery instructions.
- Never change `claimRef` or delete the PV just to make it `Available` without a reviewed plan.

### CSI controller and sidecar troubleshooting

Identify which operation failed from events/logs. Depending on architecture, components may include external-provisioner, external-attacher, external-resizer, snapshotter, CSI controller plugin, and node plugin. Not every deployment has all components.

```bash
kubectl get csidrivers
kubectl get pods -A -o wide
kubectl -n <driver-namespace> describe pod <driver-pod>
kubectl -n <driver-namespace> logs <driver-pod> -c <container> --since=30m
```

Look for timestamp, volume identifier, operation outcome, retry, and backend error. Do not invent CSI RPC names or infer the exact RPC solely from an event. Redact secrets and account identifiers. If the controller is down, already-mounted I/O may continue while new provisioning/attachment/resize/snapshot operations may fail; the exact split is driver- and operation-dependent. **[VERIFY]** Check the driver's official troubleshooting guide.

### Node-level filesystem checks and repair

Read-only checks (`df -h`, `df -i`, `findmnt`, `mount`, `lsblk`, `dmesg`) help establish whether a mount is read-only, full, or reporting I/O errors. Run them in the correct node context and understand container/WSL2 limits.

`fsck` is specialized repair. It must only run on an **unmounted** filesystem and with an appropriate backup/recovery plan. Never run it on a mounted production filesystem. If filesystem corruption or backend I/O errors are suspected, preserve evidence, stop unsafe writes, and engage the storage/filesystem owner.

### Cost leakage is not a deletion justification

Orphan candidates can incur storage, snapshot, and backup costs. M15 covers cost governance. Cost pressure should trigger inventory, ownership assignment, quarantine, and review—not unsafe deletion. A retained disk may be the only recovery copy.

## 8.6 Level 4 — Expert: prevention, automation, and recovery

### Orphan-prevention program

- **Reclaim policy by data class:** reviewed standards for scratch, development, staging, and production. Do not choose `Delete` for production solely to reduce orphan count.
- **Ownership metadata:** standardize labels/annotations for service, team, environment, cost center, data classification, ticket, and lifecycle owner.
- **TTL/age:** use age as a review signal, never proof of safe deletion.
- **Namespace retirement:** inventory claims, snapshots, operators, and backend resources before namespace deletion.
- **StatefulSet lifecycle:** document scale-down and claim-retention behavior; test in disposable environments.
- **Inventory reconciliation:** compare PVs/PVCs/snapshots/attachments with backend inventory by stable IDs.
- **Alerts/reports:** monitor long-lived Released/Failed PVs, old Available PVs, unbound claims, stale attachments, orphan-candidate snapshots, and provisioning/deletion errors. Use owner routing and deduplication.
- **Controller resilience:** monitor CSI controller/node plugin health, sidecar restarts, and backend API failures.
- **Restore validation:** measure successful restoration, not merely snapshot creation.
- **Audit trail:** preserve who changed/deleted a resource, when, identity, and authorizing change/incident.

### Report-only orphan audit script

This Python 3 script uses `kubectl` JSON output. It is deliberately **report-only** and does not delete Kubernetes or backend resources. A destructive tool would need backend-specific APIs, inventory joins, a trusted ownership model, approval integration, and verified backup/disposable-data attestations. Faking that support would be unsafe.

Save as `orphan_report.py` in personal lab notes:

```python
#!/usr/bin/env python3
"""Report-only PV inventory audit. No delete or backend mutation is implemented."""
import argparse
import datetime as dt
import json
import subprocess
import sys


def run_kubectl(*args):
    proc = subprocess.run(
        ["kubectl", *args, "-o", "json"],
        text=True, capture_output=True, check=False
    )
    if proc.returncode:
        raise RuntimeError(f"kubectl {' '.join(args)} failed: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def age_text(timestamp):
    if not timestamp:
        return "UNKNOWN"
    try:
        created = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        seconds = max(0, int((dt.datetime.now(dt.timezone.utc) - created).total_seconds()))
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        return f"{days}d{hours}h{rem // 60}m"
    except (ValueError, TypeError):
        return "UNKNOWN"


def path(obj, *keys, default=""):
    cur = obj
    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
    return default if cur is None else cur


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True, help="Expected kubectl context; mismatch aborts")
    parser.add_argument("--owner-label", default="storage.example.com/owner-team")
    parser.add_argument("--apply", action="store_true",
                        help="Unsupported: this tool is report-only and refuses mutation")
    args = parser.parse_args()

    if args.apply:
        print("REFUSED: report-only tool; no destructive apply operation exists.", file=sys.stderr)
        print("Use the documented human approval gate and backend-specific runbook.", file=sys.stderr)
        return 2

    proc = subprocess.run(["kubectl", "config", "current-context"],
                          text=True, capture_output=True, check=False)
    if proc.returncode:
        print(f"ERROR: cannot read context: {proc.stderr.strip()}", file=sys.stderr)
        return 2
    actual = proc.stdout.strip()
    if actual != args.context:
        print(f"REFUSED: expected context {args.context!r}, got {actual!r}", file=sys.stderr)
        return 2

    try:
        pvs = run_kubectl("get", "pv").get("items", [])
        pvcs = run_kubectl("get", "pvc", "-A").get("items", [])
        vas = run_kubectl("get", "volumeattachment").get("items", [])
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"AUDIT ERROR: {exc}", file=sys.stderr)
        return 2

    claims_by_uid = {path(p, "metadata", "uid"): p for p in pvcs}
    claims_by_name = {(path(p, "metadata", "namespace"), path(p, "metadata", "name")): p for p in pvcs}
    rows, review_count = [], 0

    for pv in pvs:
        meta, spec, status = pv.get("metadata") or {}, pv.get("spec") or {}, pv.get("status") or {}
        ref = spec.get("claimRef") or {}
        ns, cname, cuid = ref.get("namespace", ""), ref.get("name", ""), ref.get("uid", "")
        claim = claims_by_uid.get(cuid) if cuid else None
        if claim is None and ns and cname:
            claim = claims_by_name.get((ns, cname))
        phase = status.get("phase", "UNKNOWN")
        policy = spec.get("persistentVolumeReclaimPolicy", "UNKNOWN")
        csi = spec.get("csi") or {}
        owner = (meta.get("labels") or {}).get(args.owner_label, "UNKNOWN")
        evidence = [
            f"claimRef={ns}/{cname}" if ref else "claimRef=absent",
            "claimObject=present" if claim else ("claimObject=not-found-or-uid-mismatch" if ref else "claimObject=n/a"),
            "finalizers=" + ",".join(meta.get("finalizers") or []),
            "CSI handle present" if csi.get("volumeHandle") else "backend ID unknown/non-CSI",
        ]
        attach_count = sum(1 for va in vas if path(va, "spec", "source", "persistentVolumeName") == meta.get("name"))
        evidence.append(f"attachmentObjects={attach_count}")
        if phase == "Released":
            action = "QUARANTINE/REVIEW: verify owner, claimRef, retention, backend and recovery copy"
            review_count += 1
        elif phase in {"Failed", "Lost"}:
            action = "INVESTIGATE: preserve evidence and reconcile Kubernetes/backend"
            review_count += 1
        elif phase == "Available" and not ref:
            action = "REVIEW ONLY: verify no workload/backend owner; do not infer orphan"
        else:
            action = "NO AUTOMATIC ACTION: validate ownership and backend state"
        rows.append([
            meta.get("name", "UNKNOWN"), spec.get("storageClassName", ""),
            path(spec, "capacity", "storage"), phase, age_text(meta.get("creationTimestamp")),
            f"{ns}/{cname}" if ns or cname else "", owner, policy,
            csi.get("volumeHandle", "UNKNOWN"), ";".join(evidence), action
        ])

    headers = ["PV", "storage class", "capacity/size", "PV phase", "age", "last-bound claim",
               "owner label/team", "reclaim policy", "backend identifier (if available)",
               "evidence/references", "recommended action"]
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        print("| " + " | ".join(str(v).replace("|", r"\|").replace("\n", " ") for v in row) + " |")
    print(f"\nSummary: PVs={len(pvs)}; review candidates={review_count}; mode=REPORT-ONLY")
    print("Limitations: Kubernetes is not backend inventory; non-CSI IDs may be unavailable; driver mapping varies.")
    print("No deletion, detach, finalizer modification, or backend mutation was attempted.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"UNEXPECTED AUDIT FAILURE: {exc}", file=sys.stderr)
        sys.exit(2)
```

Run report-only:

```bash
python3 orphan_report.py --context kind-storage-troubleshooting-lab
```

The context must match exactly. Save output with a timestamp and compare it with backend inventory. The script is an inventory report, not a complete orphan classifier: it cannot reliably establish backend existence, database ownership, snapshot dependencies, all operator references, or every CSI driver's identifier mapping. It reports uncertainty rather than passing it.

### Human approval gate for destructive cleanup

Any future backend-specific cleanup workflow must require: explicit `--apply`; exact allow-listed IDs; exact context confirmation; second reviewer/change ID; no remaining Pod/PVC/PV/snapshot/restore/attachment/operator/backend workflow references; tested copy or explicit disposable declaration; supported backend operation; quarantine period/owner; pre/post inventory and audit trail.

The report script has no destructive implementation; `--apply` intentionally exits with refusal. Lab cleanup uses a manual, exact-target operation after the safety gate. This is preferable to pretending that deleting a PV object deletes a backend disk.

### Deletion-protection guardrails

Admission policy can reject deletion of PVCs/PVs labelled `protect=true`, but implementation is Kubernetes-version and policy-engine dependent.

- Label protected resources through an approved standard.
- Reject DELETE requests unless an auditable exception path is satisfied.
- Restrict `delete` rights on PVC/PV/snapshot objects.
- Log break-glass use and review it after the incident.

**[VERIFY]** `ValidatingAdmissionPolicy` availability/API and match conditions vary by Kubernetes release; Gatekeeper/Kyverno have their own schemas and versions. Labels/admission controls are not complete data protection: privileged actors or backend-console access can bypass them. Protect backend accounts too.

### Recovery drills

**Drill A — Released PV:** use a disposable static/local PV; record YAML, claimRef, reclaim policy, backend ID/path and marker. Confirm disposable status. Follow official reclaim/rebinding steps for the installed version; verify the recovered claim mounts expected content, not merely `Bound`.

**Drill B — Snapshot restore:** only if compatible CSI snapshot support is installed. Check source, class, content and readiness; restore to a new disposable claim; verify application records/checksums and consistency. Ready state alone is not proof of a valid backup.

**Drill C — CSI controller down:** capture context, Pod status, events/logs; determine which operations fail; check whether existing mounted I/O continues without assuming universal behavior; restore controller via approved operator/deployment runbook; test provisioning/attachment/resize/snapshot separately; reconcile leftovers.

### Troubleshooting at scale

- Use JSONPath/`jq` for inventories and preserve unknown fields.
- Join PV handles to backend inventory using stable IDs, not display names.
- Audit logs can identify who deleted a PVC/PV only if suitable audit policy and retention exist. **[VERIFY]** Check actual distribution configuration, sink, access and retention.
- Alert on trends and ownerless resources, with deduplication and maintenance suppression.
- Every quarantined resource needs an owner and review deadline.
- Handoff must include impact, timeline, evidence, data-safety status, actions taken/avoided, next owner, recovery point/time, and next decision.


## 8.7 Hands-on lab: orphan audit and safe cleanup

### Goal, budget, and fidelity

Create a disposable static local PV, bind a claim, write a marker, remove the claim under an explicit safety gate, and observe a PV retained with `Retain`. Run the report-only audit, quarantine the candidate, recheck references, then clean up exact lab resources.

This is a Kubernetes object-lifecycle exercise. A static local PV in `kind` does not represent a cloud disk or replicated backend. The local path is inside a kind node container and may be lost when the cluster is deleted.

**Estimated footprint:** one control plane plus one worker (within the three-worker limit), a tiny BusyBox Pod, small local directory and image cache. Plan approximately 1–2 GB temporary disk headroom as a conservative allowance, not a measured requirement. Keep other heavy M05 labs stopped. Check Linux free space and Windows host space under WSL2. Deleting files in WSL2 does not guarantee the host virtual disk immediately shrinks.

### 8.7.1 Preflight: context, disk, tools

```bash
set -euo pipefail
kind version
kubectl version --client
df -h
kind get clusters
kubectl config get-contexts
```

Expected context: `kind-storage-troubleshooting-lab`. Save as `kind-storage-lab.yaml`:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: storage-troubleshooting-lab
nodes:
  - role: control-plane
  - role: worker
```

Create only if absent:

```bash
if kind get clusters | grep -Fxq 'storage-troubleshooting-lab'; then
  echo "Cluster exists; inspect before reuse."
else
  kind create cluster --config kind-storage-lab.yaml
fi
kubectl config use-context kind-storage-troubleshooting-lab
```

Use this guard before mutations:

```bash
set -euo pipefail
EXPECTED_CONTEXT="kind-storage-troubleshooting-lab"
ACTUAL_CONTEXT="$(kubectl config current-context)"
if [[ "$ACTUAL_CONTEXT" != "$EXPECTED_CONTEXT" ]]; then
  printf 'Refusing to continue: expected context %s, got %s\n' \
    "$EXPECTED_CONTEXT" "$ACTUAL_CONTEXT" >&2
  exit 2
fi
df -h
kubectl get nodes -o wide
```

The guard catches an incorrect active context but cannot prove the cluster contains no unrelated work. Check cluster name, node names and ownership before each destructive step.

### 8.7.2 Create a disposable static local PV and claim

Discover node hostname labels and runtime container names:

```bash
kubectl get nodes -L kubernetes.io/hostname
docker ps --format '{{.Names}}'
```

Kind can use Docker, Podman or nerdctl. If not using Docker, use the installed provider's inspection commands. Set `LAB_NODE` to the exact `kubernetes.io/hostname` label for the worker and `LAB_CONTAINER` to its exact runtime container name. Verify the mapping first.

```bash
export LAB_CONTAINER="<exact-worker-container-name>"
docker ps --format '{{.Names}}' | grep -Fx -- "$LAB_CONTAINER"
docker exec "$LAB_CONTAINER" mkdir -p /mnt/storage-troubleshooting-lab
```

**⚠ DESTRUCTIVE — DATA LOSS RISK (DISPOSABLE LAB ONLY):** this changes the selected worker container's filesystem. Confirm it is the intended throwaway worker and contains no important data.

Create `orphan-lab.yaml`, replacing the hostname placeholder with the exact worker hostname:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: storage-orphan-lab
  labels:
    lab.example.com/disposable: "true"
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: storage-orphan-lab-pv
  labels:
    lab.example.com/disposable: "true"
    storage.example.com/owner-team: "learning-lab"
  annotations:
    storage.example.com/quarantine-reason: "Unit 8 retained-PV exercise"
spec:
  capacity:
    storage: 64Mi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: storage-orphan-lab-static
  local:
    path: /mnt/storage-troubleshooting-lab
  nodeAffinity:
    required:
      nodeSelectorTerms:
        - matchExpressions:
            - key: kubernetes.io/hostname
              operator: In
              values:
                - REPLACE_WITH_EXACT_NODE_HOSTNAME
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: storage-orphan-lab-claim
  namespace: storage-orphan-lab
  labels:
    lab.example.com/disposable: "true"
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  storageClassName: storage-orphan-lab-static
  resources:
    requests:
      storage: 32Mi
```

This is a static local PV: no dynamic provisioner is assumed. Verify the path exists inside the selected node and the hostname is correct. If the PV does not bind, inspect events rather than removing node affinity.

```bash
kubectl apply -f orphan-lab.yaml
kubectl -n storage-orphan-lab get pvc
kubectl get pv storage-orphan-lab-pv -o yaml
```

### 8.7.3 Write and verify a marker

Save as `marker-pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: storage-orphan-marker
  namespace: storage-orphan-lab
  labels:
    lab.example.com/disposable: "true"
spec:
  restartPolicy: Never
  containers:
    - name: marker
      image: busybox:1.36
      command: ["sh", "-c", "printf 'unit8-disposable-marker\n' > /data/marker.txt && cat /data/marker.txt && sleep 3600"]
      volumeMounts:
        - name: data
          mountPath: /data
      resources:
        requests:
          cpu: 10m
          memory: 16Mi
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: storage-orphan-lab-claim
```

```bash
kubectl apply -f marker-pod.yaml
kubectl -n storage-orphan-lab wait --for=condition=Ready pod/storage-orphan-marker --timeout=120s
kubectl -n storage-orphan-lab exec storage-orphan-marker -- cat /data/marker.txt
kubectl -n storage-orphan-lab get pod,pvc
kubectl get pv storage-orphan-lab-pv -o wide
```

**Expected output (representative; not executed here):**

```text
unit8-disposable-marker
```

If the Pod fails, inspect events, PV affinity, and path permissions. Do not proceed to claim deletion until the data is known to be disposable and the observed state is recorded.

### 8.7.4 Safety gate and retained-PV candidate

Record evidence:

```bash
kubectl -n storage-orphan-lab get pod storage-orphan-marker -o yaml > marker-pod-before.yaml
kubectl -n storage-orphan-lab get pvc storage-orphan-lab-claim -o yaml > claim-before.yaml
kubectl get pv storage-orphan-lab-pv -o yaml > pv-before.yaml
kubectl -n storage-orphan-lab describe pod storage-orphan-marker
```

Before deleting anything, confirm: correct context; exact lab names/labels; marker contains only disposable text; data is formally disposable; PV uses `Retain`; backend path may remain; evidence is saved.

Delete the marker Pod first so it no longer uses the claim.

**⚠ DESTRUCTIVE — DATA LOSS RISK (DISPOSABLE LAB ONLY):** deleting the exact Pod removes its runtime instance. Confirm target/context and disposable status.

```bash
kubectl config current-context
kubectl -n storage-orphan-lab get pod storage-orphan-marker -o wide
kubectl -n storage-orphan-lab delete pod storage-orphan-marker --wait=true
kubectl -n storage-orphan-lab get pods
```

Inspect references before claim deletion:

```bash
kubectl -n storage-orphan-lab get pods -o yaml
kubectl -n storage-orphan-lab get pvc storage-orphan-lab-claim -o yaml
kubectl get pv storage-orphan-lab-pv -o yaml
```

**⚠ DESTRUCTIVE — DATA LOSS RISK (DISPOSABLE LAB ONLY):** deleting this exact PVC creates the retained-PV exercise. The claim is removed; with `Retain`, PV/backend data may remain. Stop if ownership or disposability is uncertain.

```bash
kubectl config current-context
kubectl -n storage-orphan-lab get pvc storage-orphan-lab-claim
kubectl get pv storage-orphan-lab-pv -o wide
kubectl -n storage-orphan-lab delete pvc storage-orphan-lab-claim --wait=true
kubectl get pv storage-orphan-lab-pv -o yaml
```

**Expected observation (representative; not executed here):** the PV may become `Released` and retain the previous `claimRef`; the directory/marker may remain inside the worker container. Record actual results rather than claiming the lab ran.

### 8.7.5 Audit and quarantine

Save the `orphan_report.py` from Section 8.6 and run:

```bash
python3 orphan_report.py --context kind-storage-troubleshooting-lab
```

Save the output. The report may flag the PV for review; it must not classify it as a true orphan based only on phase.

Inspect the exact target before quarantine:

```bash
kubectl config current-context
kubectl get pv storage-orphan-lab-pv -o yaml
```

**⚠ DESTRUCTIVE — DATA LOSS RISK (DISPOSABLE LAB ONLY):** this mutates metadata, not data. Confirm the exact lab PV and context.

```bash
kubectl annotate pv storage-orphan-lab-pv \
  storage.example.com/quarantine-owner="learning-lab" \
  storage.example.com/quarantine-reason="unit8-retained-pv-exercise" \
  storage.example.com/quarantine-review-by="2026-11-04" --overwrite
kubectl label pv storage-orphan-lab-pv storage.example.com/quarantined="true" --overwrite
kubectl get pv storage-orphan-lab-pv -o yaml
```

The review date is illustrative. Quarantine is a review state, not proof that the resource is safe to delete.

### 8.7.6 Recheck references and clean exact resources

```bash
kubectl config current-context
kubectl -n storage-orphan-lab get pods,pvc
kubectl get pv storage-orphan-lab-pv -o yaml
kubectl get volumeattachment
kubectl api-resources | grep -i snapshot || true
```

Check snapshots if their CRDs exist. Confirm no operator, restore workflow, or external owner uses the lab resource. This lab did not install CSI drivers or create snapshots.

**Safety gate:** data is explicitly disposable; no production/shared resource is involved; evidence is saved; exact target is `storage-orphan-lab-pv`. If any condition is false, stop.

Deleting the Kubernetes PV does not necessarily delete the local directory. Backend path handling is separate and must be verified.

**⚠ DESTRUCTIVE — DATA LOSS RISK (DISPOSABLE LAB ONLY):** this removes the exact lab PV object and its Kubernetes reference. Check name, labels, context and references first.

```bash
kubectl config current-context
kubectl get pv storage-orphan-lab-pv -o yaml
kubectl delete pv storage-orphan-lab-pv
kubectl get pv storage-orphan-lab-pv
```

If the object remains, inspect status/events. Do not patch finalizers to force deletion.

Confirm the namespace contains no unrelated resources:

```bash
kubectl config current-context
kubectl -n storage-orphan-lab get all,pvc
kubectl get namespace storage-orphan-lab -o yaml
```

**⚠ DESTRUCTIVE — DATA LOSS RISK (DISPOSABLE LAB ONLY):** deleting the exact namespace removes remaining objects within it. Confirm the lab label and target.

```bash
kubectl delete namespace storage-orphan-lab --wait=true
kubectl get namespace storage-orphan-lab
```

Discover the exact worker container and inspect the directory read-only:

```bash
docker ps --format '{{.Names}}'
docker exec <exact-worker-container-name> ls -la /mnt/storage-troubleshooting-lab
docker exec <exact-worker-container-name> cat /mnt/storage-troubleshooting-lab/marker.txt
```

If the actual driver/path differs, stop. **[VERIFY]** path semantics depend on runtime, node container, and provisioner.

**⚠ DESTRUCTIVE — DATA LOSS RISK (DISPOSABLE LAB ONLY):** remove only the directory created for this lab, after verifying exact worker/path/content.

```bash
docker exec <exact-worker-container-name> rm -rf -- /mnt/storage-troubleshooting-lab
docker exec <exact-worker-container-name> test ! -e /mnt/storage-troubleshooting-lab
```

For Podman/nerdctl use the corresponding runtime command. Never copy this path to production.

### 8.7.7 Final residual scan and optional cluster deletion

```bash
kubectl config current-context
kubectl get pv | grep -F 'storage-orphan-lab' || true
kubectl get pvc -A | grep -F 'storage-orphan-lab' || true
kubectl get pods -A | grep -F 'storage-orphan' || true
kubectl get namespaces | grep -F 'storage-orphan-lab' || true
kubectl get volumeattachment
```

These targeted grep checks are not complete proof of absence; review full listings and backend path inventory. If the cluster had no pre-existing work, verify exact cluster/context before deleting it.

**⚠ DESTRUCTIVE — DATA LOSS RISK (THROWAWAY CLUSTER ONLY):** cluster deletion removes its objects and node containers, including remaining node-local lab data. Confirm it is the disposable cluster and evidence is saved.

```bash
kind get clusters
kubectl config current-context
kind delete cluster --name storage-troubleshooting-lab
kind get clusters
```

Check host disk usage afterward. WSL2 virtual disk files may not shrink automatically. Do not use broad `docker system prune` or delete unrelated container volumes.

### Lab acceptance criteria

- [ ] Correct context and free-disk evidence recorded.
- [ ] One worker, no paid storage, maximum three workers.
- [ ] PV/PVC and local path created with exact reviewed names.
- [ ] Marker written/read, or failure evidence captured honestly.
- [ ] PVC deletion preceded by data-safety gate.
- [ ] Retained PV and backend path inspected.
- [ ] Report-only audit output saved.
- [ ] Candidate quarantined and references rechecked.
- [ ] Exact PV and namespace cleanup verified.
- [ ] Backend leftovers checked using actual runtime/path.
- [ ] Unsupported or unrun behavior marked `[VERIFY]`/not reproduced.


## 8.8 Storage troubleshooting gauntlet

### How to use the gauntlet

The question section below deliberately does **not** reveal root causes. For each case, write down (1) first read-only checks, (2) hypothesis and confidence, (3) evidence that would confirm/disconfirm it, (4) data-safety decision, (5) safe fix, (6) post-fix verification, and (7) prevention. Hints are progressive. The answer key is separated after all 18 cases. Every snippet is **representative; not executed here**.

### Learner-facing incident cases

#### Case 1 — New PVC never binds

**Incident:** A developer deploys a small service; its claim is Pending.  
**Evidence:** `kubectl get sc` returns no classes; the PVC has no `storageClassName`; events say no matching PV was found.  
**Hints**
- Hint 1: Inspect the claim's requested size and access mode.
- Hint 2: Is any StorageClass available?
- Hint 3: Check for compatible static PVs before proposing a new class.
**Diagnosis rubric:** confidence rises if class inventory is empty and no static PV matches; lowers if a compatible PV/class exists.  
**Safe fix:** data-safety check first; if no data exists, create an approved class/provisioner or matching static PV. Do not set a global default without review.  
**Verify/prevent:** claim binds to intended PV and a test Pod mounts; add class validation to CI.

#### Case 2 — Almost-correct class name

**Incident:** A claim has retried provisioning without success after a deployment.  
**Evidence:** PVC YAML says `storageClassName: fast-stroage`; class inventory includes `fast-storage`.  
**Hints**
- Hint 1: Compare literal strings.
- Hint 2: Read PVC events and confirm class inventory.
- Hint 3: A class correction does not migrate data already bound elsewhere.
**Diagnosis rubric:** exact name mismatch confirms; a matching class and healthy provisioner lowers confidence.  
**Safe fix:** verify whether the claim has bound data; if not, correct the manifest to the intended class. If data exists, design migration instead of changing semantics casually.  
**Verify/prevent:** claim uses expected class; lint manifests against environment classes.

#### Case 3 — “Stuck” WFFC claim

**Incident:** A claim has been Pending since a manifest was applied.  
**Evidence:** StorageClass uses `WaitForFirstConsumer`; no Pod in the namespace references the claim.  
**Hints**
- Hint 1: Read the binding mode.
- Hint 2: Find a consuming Pod or controller.
- Hint 3: A Pending claim can be the intended WFFC state.
**Diagnosis rubric:** no consumer supports normal delay; a consumer with scheduling errors indicates a separate blocker.  
**Safe fix:** no destructive action; create/repair the intended consumer after confirming workload intent.  
**Verify/prevent:** claim binds once a schedulable consumer exists; include a consumer in smoke tests.

#### Case 4 — Claim exceeds policy

**Incident:** A large PVC does not provision in a team namespace.  
**Evidence:** namespace quota shows a storage request limit; events mention quota/policy rejection.  
**Hints**
- Hint 1: Inspect ResourceQuota and LimitRange.
- Hint 2: Separate namespace quota from backend capacity.
- Hint 3: Do not reduce a request without understanding the data requirement.
**Diagnosis rubric:** quota event plus exhausted quota confirms; backend capacity errors may coexist and must be separated.  
**Safe fix:** confirm data needs and obtain approved quota/capacity or revise an unprovisioned request under review.  
**Verify/prevent:** claim provisions within policy; monitor quota headroom.

#### Case 5 — Access mode/capability mismatch

**Incident:** A workload requiring shared access cannot mount its claim as expected.  
**Evidence:** claim requests `ReadWriteMany`; candidate PV advertises `ReadWriteOnce`; driver events mention unsupported capability.  
**Hints**
- Hint 1: Compare claim/PV access modes and volume mode.
- Hint 2: Access mode names are not a universal promise of filesystem semantics.
- Hint 3: Consult actual driver/backend capability documentation.
**Diagnosis rubric:** field mismatch supports; matching Kubernetes fields do not prove backend support.  
**Safe fix:** confirm data safety; choose supported storage or a reviewed migration. Do not rewrite a claim to hide a capability gap.  
**Verify/prevent:** disposable mount test and driver compatibility review pass.

#### Case 6 — Released PV refuses a new claim

**Incident:** A retained PV is visible but a new claim does not bind to it.  
**Evidence:** PV phase is `Released`; reclaim policy is `Retain`; `claimRef` names an old namespace/claim UID.  
**Hints**
- Hint 1: `Released` differs from `Available`.
- Hint 2: Confirm whether old claim and backend data still exist.
- Hint 3: Rebinding is a deliberate recovery workflow, not a status reset.
**Diagnosis rubric:** old claimRef and Retain support the hypothesis; an active owner or recovery hold means it is not orphaned.  
**Safe fix:** verify copy/disposable status and backend ID; test documented rebind steps on disposable storage. Do not clear claimRef blindly.  
**Verify/prevent:** new claim uses expected data and integrity is checked; document Retain recovery.

#### Case 7 — Non-root process cannot write

**Incident:** Pod starts but the application gets `Permission denied` under its data directory.  
**Evidence:** process runs as UID/GID 10001; mount exists; files are owned by another UID and mode does not grant access.  
**Hints**
- Hint 1: Inspect process identity and file metadata.
- Hint 2: Check `runAsUser`, `runAsGroup`, `fsGroup`, and driver policy.
- Hint 3: Root-squash, SELinux/AppArmor, or filesystem semantics may affect access.
**Diagnosis rubric:** ownership/mode mismatch supports; kernel I/O errors suggest a different fault.  
**Safe fix:** verify backup and path scope; adjust supported security context or permissions. Avoid recursive `chown` on unknown production data.  
**Verify/prevent:** non-root process can access only intended paths; test security context in CI.

#### Case 8 — “No space” despite a capacity dashboard

**Incident:** The application cannot create small files.  
**Evidence:** `df -h /data` shows some free bytes, but `df -i /data` shows zero free inodes.  
**Hints**
- Hint 1: Bytes and inodes are different resources.
- Hint 2: Inspect small-file growth and application retention.
- Hint 3: Also compare filesystem capacity with PVC request and backend/thin-provisioned capacity.
**Diagnosis rubric:** inode exhaustion supports; backend metrics may reveal a second constraint.  
**Safe fix:** confirm data safety and identify the owning application; use its cleanup/retention procedure or supported expansion. Do not delete arbitrary files.  
**Verify/prevent:** free inodes and writes recover; alert on bytes and inodes separately.

#### Case 9 — Resize request does not change filesystem

**Incident:** PVC request was increased but `df -h` still shows the old filesystem size.  
**Evidence:** StorageClass may not permit expansion; PVC has resize-related conditions/events.  
**Hints**
- Hint 1: Inspect `allowVolumeExpansion`.
- Hint 2: Separate controller-side resize from node filesystem resize.
- Hint 3: Check driver/backend support and resizer logs.
**Diagnosis rubric:** class policy or explicit unsupported error confirms; completed backend resize with pending node resize points elsewhere.  
**Safe fix:** verify backup and support; follow exact expansion or migration procedure. Do not shrink or recreate the data volume casually.  
**Verify/prevent:** PVC capacity and filesystem size agree; test expansion on the real backend.

#### Case 10 — Snapshot never becomes ready

**Incident:** A snapshot request remains not ready after creation.  
**Evidence:** snapshot class list is empty or events report a missing class/controller/capability.  
**Hints**
- Hint 1: Snapshot APIs are CRDs, not core API objects.
- Hint 2: Check source claim, controller, class, CSI snapshotter, and driver capability.
- Hint 3: Readiness alone is not a restore test.
**Diagnosis rubric:** missing CRD/controller/class or explicit driver error supports; verify source and backend logs too.  
**Safe fix:** preserve source data and install/repair only compatible components. Do not delete a snapshot whose retention is unknown.  
**Verify/prevent:** restore to a disposable target and validate application data; automate restore drills.

#### Case 11 — StatefulSet ordinal cannot start

**Incident:** `db-1` is Pending after a scale-down/namespace operation; expected claim is missing or retained.  
**Evidence:** event names `data-db-1`; StatefulSet has a `volumeClaimTemplates` entry; old claim inventory shows retained data.  
**Hints**
- Hint 1: Verify claim naming and ordinal identity.
- Hint 2: Inspect claim-retention policy and operator status.
- Hint 3: A new empty claim may start an empty database rather than recover the old member.
**Diagnosis rubric:** missing/retained claim and prior lifecycle records support; a healthy claim with correct PV suggests another cause.  
**Safe fix:** confirm member identity/data safety and use operator-approved restore/rejoin/rebind.  
**Verify/prevent:** correct data and database membership verified; document scale-down behavior.

#### Case 12 — CSI controller is unhealthy

**Incident:** New claims fail provisioning; an existing workload may still be running.  
**Evidence:** CSI controller Pods are not Ready; PVC events show provisioning retries.  
**Hints**
- Hint 1: Identify the actual provisioner and controller.
- Hint 2: Inspect crash logs, rollout changes, credentials, and backend API errors.
- Hint 3: Existing mounts and new provisioning need not fail identically.
**Diagnosis rubric:** controller outage correlated with failures supports; backend auth/capacity errors may be the root cause.  
**Safe fix:** preserve data and restore controller via its owning operator/deployment runbook; do not scale managed components arbitrarily.  
**Verify/prevent:** test provisioning and other operation types; alert on controller/sidecar health.

#### Case 13 — Pod blocked after node-pool change

**Incident:** Pod remains Pending following replacement of a node pool.  
**Evidence:** event mentions volume node affinity conflict; PV affinity names a hostname/zone no longer eligible.  
**Hints**
- Hint 1: Inspect PV `nodeAffinity`.
- Hint 2: Compare node labels and Pod constraints.
- Hint 3: Do not rewrite affinity to impersonate a data location.
**Diagnosis rubric:** no eligible node satisfying both PV and Pod constraints confirms; also inspect missing labels/provisioner errors.  
**Safe fix:** restore eligible capacity or recover via supported replica/backup workflow.  
**Verify/prevent:** mount and application data checked; use Unit 7 topology audit.

#### Case 14 — PVC deletion is blocked

**Incident:** PVC stays Terminating and has `kubernetes.io/pvc-protection`.  
**Evidence:** a Pod still references the claim in its volume list.  
**Hints**
- Hint 1: Search all Pods in the namespace.
- Hint 2: Check Pod termination and owning controller/operator.
- Hint 3: Protection may be functioning correctly.
**Diagnosis rubric:** live reference supports expected protection; no references plus a persistent finalizer calls for controller investigation.  
**Safe fix:** confirm data safety and stop workload through its owner; do not patch the finalizer first.  
**Verify/prevent:** normal deletion completes after references clear; retirement workflow checks active Pods.

#### Case 15 — Snapshot content remains after snapshot deletion

**Incident:** User-facing snapshot was removed, but VolumeSnapshotContent remains.  
**Evidence:** content has a `Retain` deletion policy and backend snapshot handle.  
**Hints**
- Hint 1: Inspect the VolumeSnapshotClass deletion policy.
- Hint 2: Find the snapshot owner/restore catalog and backend handle.
- Hint 3: Missing user-facing object does not prove the snapshot is unneeded.
**Diagnosis rubric:** Retain plus surviving content supports intentional retention or candidate orphan; restore/retention records decide.  
**Safe fix:** verify restorable copy or explicit disposal; quarantine and approve exact cleanup.  
**Verify/prevent:** Kubernetes and backend snapshot inventories reconcile; define retention ownership.

#### Case 16 — Multi-Attach after node failure

**Incident:** Replacement Pod cannot mount volume; event reports Multi-Attach.  
**Evidence:** old node is NotReady; a VolumeAttachment still names the old node; backend state has not been confirmed.  
**Hints**
- Hint 1: Establish whether the old node is truly fenced/offline.
- Hint 2: Compare Kubernetes attachment state with backend attachment state.
- Hint 3: An old object is not by itself proof that manual deletion is safe.
**Diagnosis rubric:** stale attachment and backend attachment evidence support; driver/backend may reject attach for other reasons.  
**Safe fix:** verify data integrity/fencing and follow official driver/provider detach procedure. Never delete VolumeAttachment as a generic fix.  
**Verify/prevent:** backend confirms safe attach; app data checked; rehearse node-loss recovery.

#### Case 17 — Filesystem turns read-only

**Incident:** Writes fail; application reports read-only filesystem.  
**Evidence:** `findmnt` shows `ro`; kernel log may show I/O errors.  
**Hints**
- Hint 1: Preserve app and kernel logs.
- Hint 2: Distinguish configured read-only mount from protective state after errors.
- Hint 3: Filesystem repair can worsen damage if mounted or lacking a recovery plan.
**Diagnosis rubric:** read-only mount plus kernel/backend errors supports; permissions alone do not explain I/O errors.  
**Safe fix:** stop unsafe writes and engage storage/filesystem owner. `fsck` only on an unmounted filesystem with a backup/recovery plan.  
**Verify/prevent:** qualified integrity and application checks; monitor I/O errors and test restore.

#### Case 18 — PVC Lost/backend inventory mismatch

**Incident:** PVC status is Lost or Kubernetes and backend inventory disagree about a disk.  
**Evidence:** claim UID/claimRef is present in saved YAML; one backend inventory query cannot find the handle.  
**Hints**
- Hint 1: Compare stable IDs, not display names.
- Hint 2: Inspect audit logs and controller history.
- Hint 3: One inventory view may be stale; actual backend deletion must be confirmed.
**Diagnosis rubric:** correlate object UIDs, CSI handle, audit logs, backend lifecycle records, and backup catalog.  
**Safe fix:** freeze cleanup and reconcile with platform/backend owner; restore from verified replica/backup if needed.  
**Verify/prevent:** data status is explicit; periodic inventory and deletion auditing are implemented.

### Answer key — keep separate until you attempt the cases

| Case | Likely diagnosis | Key confirming evidence |
|---:|---|---|
| 1 | No default StorageClass and no matching PV/provisioner | Empty class inventory and no matching static PV |
| 2 | Misspelled class name | Literal `storageClassName` mismatch |
| 3 | WFFC has no consumer yet | Binding mode plus no Pod reference |
| 4 | Namespace quota/policy exceeded | ResourceQuota/LimitRange/admission evidence |
| 5 | Access mode/volume mode/driver capability mismatch | Claim/PV fields and driver docs |
| 6 | Retained PV has old claimRef | Released phase, Retain policy, owner/backend record |
| 7 | UID/GID/mode/fsGroup/driver semantics | Process identity and file metadata |
| 8 | Inode exhaustion despite free bytes | `df -i` plus application file growth |
| 9 | Expansion unsupported or resize stage incomplete | StorageClass, PVC conditions, CSI resizer and filesystem size |
| 10 | Snapshot stack/class/driver capability missing or failing | CRDs, events, controller and CSI snapshotter logs |
| 11 | StatefulSet expected claim missing/retained/incompatible | Claim template, ordinal, operator/PV state |
| 12 | CSI controller unhealthy or backend auth/API error | Controller health/logs and correlated operation failures |
| 13 | PV affinity excludes available nodes | PV affinity versus node labels and Pod constraints |
| 14 | PVC protection correctly waits for Pod reference | Pod volume list and finalizer |
| 15 | Retained snapshot content/backend snapshot remains | deletionPolicy, handle, restore/retention catalog |
| 16 | Backend attachment not released or driver issue | Old-node fencing, VolumeAttachment, backend state |
| 17 | Filesystem/backend I/O fault or configured RO mount | mount state, kernel and backend evidence |
| 18 | Lost object or inventory drift/deletion | stable IDs, audit trail, controller logs, backup catalog |

None of these answers authorizes production PVC/PV deletion, finalizer removal, force-detach, filesystem formatting, or repair without the required data-safety and reference checks.


## 8.9 SRE lens: incident management and data safety

### Prioritize by integrity risk, impact, and recovery confidence

| Example | Priority reasoning | Immediate posture |
|---|---|---|
| Disposable scratch PVC unavailable | Low impact only if verified disposable | Diagnose/recreate safely |
| Developer workspace PVC | Moderate; confirm owner and backup | Preserve until owner confirms |
| Primary database volume fails to mount | High integrity/customer impact | Freeze unsafe mutations; engage database/storage owners |
| Shared data service has I/O errors | Potentially broad blast radius/corruption | Preserve evidence and assess write safety |
| Old Released PV with unknown owner | No immediate outage, but possible sensitive data/cost | Quarantine and investigate; no automatic deletion |

Severity depends on workload and business context, not object status alone. A Pending scratch claim may be minor; a Bound database claim with kernel I/O errors may be severe.

### RTO and RPO are objectives, not guarantees

- **Recovery Time Objective (RTO):** target time to restore service to an agreed operating state.
- **Recovery Point Objective (RPO):** target data-loss window for a defined failure.

Service recovery is not the same as data recovery. A Pod may start while pointing at an empty volume. A database may accept traffic but be missing acknowledged writes or still recovering. A snapshot may be ready but fail to restore or contain inconsistent application state.

At incident start, record last known-good data point, backup/snapshot status, replication state, write status, and the time service is restored. Do not claim an RPO/RTO target was met without evidence.

### Stop-work and escalation conditions

Stop destructive work and escalate if backend ownership or stable identifier is unclear; a snapshot/backup has not been restore-tested and is the only copy; filesystem I/O/corruption indicators appear; a volume may remain attached to an unfenced node; database role/consistency is unknown; or the proposed fix is force-deleting a Pod, deleting a PVC/PV, patching a finalizer, or manually deleting backend files.

### Evidence and timeline discipline

Record timestamps with timezone and preserve events/logs before they expire. Correlate recent class changes, CSI rollouts, node maintenance, quota, secret rotation, namespace deletion, and database/operator changes. Keep original outputs read-only and annotate analysis separately. Do not copy credentials or sensitive handles into tickets.

### Post-incident review template

```text
Incident title / ID:
Date, timeline, and detection source:
Impact, affected workloads, and blast radius:
Data status: intact / recovered / partial loss / unknown:
RPO/RTO objective and measured outcome:
Root cause and contributing factors:
Evidence supporting root cause:
Detection gap:
What worked:
What was avoided (e.g. no forced finalizer removal):
Recovery steps and data verification:
Follow-up actions | owner | due date:
Prevention/monitoring/policy changes:
Runbook updates:
Residual risks and accepted exceptions:
```

### On-call handoff template

Include impact and urgency; exact cluster/context/namespace; object names and UIDs; current PVC/PV/attachment/snapshot state; events/logs with timestamps; backend ID and inventory result; data-safety status; backups/replicas and last verified recovery point; actions taken and avoided; next owner/contact; next decision/deadline. A good handoff prevents dangerous discovery steps from being repeated.

## 8.10 Security and governance lens

- **Least privilege:** separate read/list/get from delete/patch rights on PVCs, PVs, snapshots, and attachments. A routine inventory script does not need cluster-admin.
- **Deletion controls:** use admission policy and RBAC to protect selected resources; keep break-glass auditable.
- **Ownership:** require accountable team/service labels and lifecycle annotations. Unknown owner should block cleanup, not accelerate it.
- **Sensitive data:** snapshots, backups, YAML, events, CSI logs, and backend identifiers can expose resource names, tenancy, topology, or secrets. Redact before sharing.
- **Credential hygiene:** use fake credentials in labs; do not print Secret data, tokens, or environment variables.
- **Retention and privacy:** retained volumes/snapshots may contain regulated data. Follow legal holds, classification, and retention/deletion policy.
- **Separation of duties:** inventory/report author should not automatically have deletion rights. Require independent review for destructive cleanup.
- **Auditability:** retain candidate ID, evidence, approval, operation, and post-delete inventory result.
- **Break-glass:** time-bound, approved, logged, and reviewed. Do not silently bypass policy.
- **Backend controls:** Kubernetes admission cannot prevent every out-of-band provider-console or backend API deletion. Protect backend accounts too.

## 8.11 Troubleshooting reference tables

### Event family quick reference

| Event family/reason | What it suggests | Next evidence | Caution |
|---|---|---|---|
| FailedScheduling | Pod has no feasible node | Pod describe, labels, constraints, PVC/PV | May combine multiple blockers |
| ProvisioningFailed | Provisioning attempt failed | PVC events, StorageClass, provisioner/CSI logs | Could be auth, capacity, or config |
| FailedAttachVolume | Attach operation failed | VolumeAttachment, controller logs, backend state | Not every volume uses attachment |
| FailedMount | Node could not mount/setup volume | kubelet/node plugin logs, mount state, permissions | Could be attachment, filesystem, credentials, or permissions |
| Multi-Attach | Conflicting attachment semantics reported | Old node, attachment object, backend inventory | Do not force detach blindly |
| PVC protection finalizer | Claim deletion is protected while used | Pod references and controller state | Do not patch finalizer first |
| Snapshot not ready | Snapshot workflow incomplete | CRDs, class, source, controller, snapshotter | Readiness is not a restore test |

Exact event names and messages are version/driver-sensitive; this is a starting point, not an exhaustive API contract.

### Object state and safe next action

| Object/state | Safe interpretation | First safe action |
|---|---|---|
| PVC Pending | Binding/provisioning incomplete; may be expected under WFFC | Inspect class, consumer, events |
| PVC Bound | Claim bound to PV | Verify attach/mount/application separately |
| PVC Lost | Claim/PV relationship problem | Preserve evidence; reconcile backend |
| PV Available | Available according to Kubernetes state | Confirm no backend/owner conflict before reuse |
| PV Bound | Claim reference exists | Map to workload and backend ID |
| PV Released | Prior claim released; retention/rebinding decision remains | Inventory, owner lookup, quarantine |
| PV Failed | Failure condition exists | Events, controller, backend |
| VolumeAttachment exists | Attachment intent represented | Compare with driver/backend state |
| Snapshot readyToUse | Snapshot reports ready | Restore-test and validate application data |

### Command scope reference

| Command | Scope | Purpose | Risk |
|---|---|---|---|
| `kubectl get pvc -A` | Namespaced across namespaces | Claim inventory | Read-only |
| `kubectl get pv` | Cluster-scoped | PV inventory | Read-only |
| `kubectl get sc` | Cluster-scoped | StorageClass inventory | Read-only |
| `kubectl get volumeattachment` | Cluster-scoped | Attachment inventory | Read-only |
| `kubectl describe ...` | Object-specific | Details/events | Read-only |
| `kubectl logs ...` | Pod/container | Controller/driver evidence | Read-only; may expose metadata |
| `kubectl debug node/...` | Creates debug Pod | Node troubleshooting | Mutating; may require elevated access |
| `kubectl annotate/label` | Mutates metadata | Quarantine/ownership record | Review exact target |
| `kubectl delete pvc/pv/ns` | Destructive | Approved cleanup only | Data loss/retention risk |
| `kubectl patch ... finalizers` | Mutates deletion coordination | Exceptional recovery only | High risk; not routine |
| `fsck` | Filesystem-level | Specialized repair | Only unmounted, with backup/recovery plan |

### Cross-module boundary

- Unit 1: `01-volumes-persistentvolumes-and-persistentvolumeclaims.md` — object lifecycle, reclaim policy, finalizers, permissions, Retain recovery.
- Unit 2: `02-storageclasses-dynamic-provisioning-and-csi-drivers.md` — StorageClass, CSI architecture, controller/node plugin.
- Unit 3: `03-volume-snapshots-cloning-and-expansion.md` — snapshot readiness, restore, expansion.
- Unit 4: `04-statefulset-storage-patterns-and-stable-identity.md` — claim templates, stable identity, retention/scale-down.
- Unit 5: `05-running-databases-and-brokers-with-operators.md` — database/operator semantics and application recovery.
- Unit 6: `06-storage-performance-iops-throughput-and-latency.md` — latency, throughput, saturation, capacity/performance separation.
- Unit 7: `07-data-locality-zonal-failure-and-volume-affinity.md` — topology conflict and node/zone failure.
- Capstone: `Projects/01-stateful-data-platform-with-snapshots-and-recovery.md`.
- M03: scheduling, quotas, RBAC, audit; M13: formal backup/DR; M15: cost governance. These are forward references, not substitute content.

## 8.12 Self-check questions and answer key

### Questions

1. State the eight-step storage troubleshooting sequence.
2. Why is PVC Pending not always an error?
3. What is the difference between PV Released and Available?
4. Which of PVC, PV, StorageClass, and VolumeAttachment are namespaced?
5. Why does FailedMount not prove backend corruption?
6. How do you distinguish full bytes from inode exhaustion?
7. Why is Bound insufficient proof that the application can safely use the data?
8. What does Retain mean, and what must be checked before reuse?
9. Why is forcibly removing a finalizer dangerous?
10. Name four references to check before declaring a backend volume orphaned.
11. Why is backend inventory needed in addition to Kubernetes inventory?
12. How does snapshot readiness differ from successful restore?
13. What must be true before running `fsck`?
14. What should the report script do if owner/backend ID is missing?
15. Why not delete resources based only on age or phase?
16. What does the lab demonstrate and what does it not demonstrate?
17. How should stale VolumeAttachment/Multi-Attach be handled?
18. Why does the audit script check current context?
19. Name three controls that prevent orphan accumulation without auto-deleting uncertain data.
20. What belongs in a safe on-call handoff?

### Answer key

1. Observe object states → read events → check owning controller/driver → check node → check backend → fix safely → verify → document.
2. WFFC may delay binding until a consuming Pod is schedulable; other causes require evidence.
3. Released means the previous claim is released but recovery/reuse is unresolved; Available means Kubernetes currently considers it available. Neither proves backend safety.
4. PVC is namespaced; PV, StorageClass, and VolumeAttachment are cluster-scoped.
5. Mount can fail due to attachment, plugin, credentials, options, permissions, node issues, or backend errors.
6. Use `df -h` for bytes and `df -i` for inodes; inspect backend capacity and application growth too.
7. Binding does not prove attach, mount, permissions, filesystem health, free capacity, or application consistency.
8. Retain generally preserves PV/backend resource for deliberate handling after claim release. Verify ownership, references, backend ID, backup/recoverability, and documented rebind steps.
9. It may remove coordination before cleanup/protection is complete, orphan backend resources, or remove useful references.
10. Pods, PVC/PVs, snapshots, restore jobs, attachments, operators, backend workflows, and ownership records are examples.
11. Kubernetes may not represent every backend object, and backend resources can survive object deletion. Stable IDs and lifecycle records reconcile the two.
12. Readiness is controller/API state; restore success requires a restored target and verified application data/integrity.
13. Filesystem must be unmounted and an appropriate backup/recovery plan must exist; production repair needs a qualified procedure.
14. Report UNKNOWN and require human investigation; missing metadata is not proof of safe deletion.
15. Old data may be a recovery asset; phases are incomplete signals and do not establish ownership or data safety.
16. It demonstrates object lifecycle with a static local PV and Retain policy. It does not model cloud disks, CSI cleanup, real zones, or production durability.
17. Preserve evidence; check old-node fencing, attachment, CSI logs, and backend state; follow driver/provider procedure. Do not delete attachment objects blindly.
18. To avoid queries/mutations on the wrong cluster; the guard does not prove there are no unrelated resources.
19. Ownership metadata, namespace retirement workflow, periodic inventory reconciliation, alerts, admission/RBAC, quarantine review.
20. Impact, context/objects, timestamps/events/logs, backend ID/state, data-safety status, backups/recovery point, actions taken/avoided, next owner, and follow-up.

## 8.13 Evidence artifacts and completion gate

Use a personal evidence folder; this lesson does not create extra repository files.

```text
m05-u8-evidence/
├── 01-preflight/ (context.txt, versions.txt, disk-before.txt, nodes.txt)
├── 02-inventory/ (pv.tsv, pvc.tsv, storageclasses.yaml, attachments.yaml, snapshots.txt)
├── 03-incident/ (pod.txt, pvc.txt, events.txt, controller-driver-notes.md)
├── 04-lab/ (pv-before.yaml, claim-before.yaml, marker.txt, released-pv.yaml, quarantine.md)
├── 05-audit/ (orphan_report.py, report-output.md)
├── 06-cleanup/ (kubernetes-residual-scan.txt, backend-path-check.txt, disk-after.txt)
└── 07-review/ (incident-review.md, handoff.md, verification-register.md)
```

Useful evidence commands:

```bash
kubectl config current-context > context.txt
kubectl get nodes -o wide > nodes.txt
kubectl get pv -o yaml > pv-inventory.yaml
kubectl get pvc -A -o yaml > pvc-inventory.yaml
kubectl get storageclass -o yaml > storageclasses.yaml
kubectl get volumeattachment -o yaml > volumeattachments.yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp > events.txt
python3 orphan_report.py --context kind-storage-troubleshooting-lab > orphan-report.md
```

Sanitize sensitive names/identifiers before sharing. Do not invent evidence if a step was not run.

### Completion gate

You are complete when you can demonstrate the eight-step sequence; distinguish provisioning/scheduling/attachment/mount/filesystem/permission/application/backend issues; explain why Pending, Released, Lost, Terminating, or detached does not automatically mean delete; run the report-only audit with the expected context; create and remove only the disposable lab resource; inspect actual backend path without guessing; explain retained PV/snapshot as possible recovery assets; show safety gate and quarantine; verify Kubernetes objects and node-local leftovers; and list production details still requiring verification.

## 8.14 Sources and verification notes

The following official pages were consulted for the source map. The cluster and driver environment was not available for runtime verification. Confirm the exact version before using operational procedures.

1. **Kubernetes — Persistent Volumes:** https://kubernetes.io/docs/concepts/storage/persistent-volumes/  
   PV/PVC lifecycle, reclaim policy, local volumes, node affinity and protection behavior.
2. **Kubernetes — Storage Classes:** https://kubernetes.io/docs/concepts/storage/storage-classes/  
   Default class, reclaim policy, expansion, binding mode, WFFC and allowed topologies.
3. **Kubernetes — Volume Snapshots:** https://kubernetes.io/docs/concepts/storage/volume-snapshots/  
   VolumeSnapshot/VolumeSnapshotContent/VolumeSnapshotClass, controller, CSI snapshotter and deletion policy.
4. **Kubernetes — Debugging Nodes With kubectl:** https://kubernetes.io/docs/tasks/debug/debug-cluster/kubectl-node-debug/  
   `kubectl debug node`, permissions, host filesystem visibility and cleanup.
5. **Kubernetes — Storage Capacity:** https://kubernetes.io/docs/concepts/storage/storage-capacity/  
   Capacity tracking and CSI support; release-sensitive details need checking.
6. **Kubernetes API reference — Storage:** https://kubernetes.io/docs/reference/kubernetes-api/storage/  
   API field definitions and resource scope.
7. **Kubernetes — Resource Quotas:** https://kubernetes.io/docs/concepts/policy/resource-quotas/  
   Namespace quota and storage-related quota behavior.
8. **kind — Quick Start:** https://kind.sigs.k8s.io/docs/user/quick-start/  
   Cluster creation, node containers, contexts, runtime support and deletion.
9. **kind — Configuration:** https://kind.sigs.k8s.io/docs/user/configuration/  
   Cluster configuration and multi-node layout.
10. **CSI specification:** https://github.com/container-storage-interface/spec  
    Interface contract; not a replacement for exact driver documentation.
11. **CSI sidecars:** https://github.com/kubernetes-csi/external-provisioner ; https://github.com/kubernetes-csi/external-attacher ; https://github.com/kubernetes-csi/external-resizer ; https://github.com/kubernetes-csi/external-snapshotter  
    Check compatibility matrices and versions for actual cluster/driver.

### Source and verification matrix

| Claim/topic | Authoritative source | Caveat | Status |
|---|---|---|---|
| Retain/Delete lifecycle | Kubernetes PV and StorageClass docs | Backend cleanup depends on driver/provisioner | Docs consulted; environment open |
| WFFC/default class | Kubernetes StorageClass docs | Provisioner support/config varies | Docs consulted; live class not inspected |
| PVC protection/finalizers | Kubernetes PV/API docs | Exact finalizer/controller flow can vary | Verify exact release before intervention |
| VolumeAttachment | Kubernetes storage API reference | Only applies to drivers using attachment; backend state is separate | Driver mapping open |
| Snapshot controller/sidecar | Kubernetes Volume Snapshots | CRD/controller/driver versions must match | Docs consulted; no driver installed/verified |
| Expansion | Kubernetes StorageClass/PV docs | Backend and resizer support required | Docs consulted; no runtime test |
| `kubectl debug node` | Kubernetes node debugging docs | Authorization/distribution policy may block it | Docs consulted; no live debug |
| Kind node container | kind Quick Start/Configuration | Runtime and node image vary | Docs consulted; no cluster created |
| Local PV path | Actual PV and node-container inspection | Path/provisioner cleanup is environment-specific | Must inspect locally |
| Filesystem repair | Filesystem/vendor runbook | Filesystem-specific; unmounted with recovery plan | Safety rule; filesystem unknown |
| Audit attribution | Distribution audit configuration | Policy, sink, access, retention vary | `[VERIFY]` actual cluster |
| Admission policy | Kubernetes API/policy-engine docs | API version and engine vary | `[VERIFY]` before deployment |
| Database consistency/restore | Exact database/operator docs | Application-specific | Not tested |
| Backend orphan detection | Actual backend inventory and lifecycle logs | IDs/ownership metadata vary | `[VERIFY]` for every backend |

### Pre-production verification checklist

1. Record Kubernetes version/distribution.
2. Record StorageClass, CSI driver and sidecar versions.
3. Check official compatibility matrices.
4. Confirm object scope, finalizer, reclaim and resize behavior for the release.
5. Identify whether the backend is CSI, local, shared filesystem, or another provisioner.
6. Reconcile backend by stable ID and ownership metadata.
7. Restore-test snapshots/backups before treating them as recoverable copies.
8. Confirm filesystem type and repair procedure before any repair.
9. Validate audit-log retention and admission-policy support.
10. Run a controlled non-production drill and record measured recovery outcomes.

## 8.15 Independent technical audit

### Audit method and result

This lesson was statically reviewed against the requirements in the uploaded Unit 8 prompt and the official Kubernetes/kind documentation listed above. The Python script and YAML examples were authored but **not executed in a live cluster**. No representative output is claimed as observed. The project tree and parent syllabus prompt were not separately inspected in this turn; the uploaded Unit 8 prompt supplied the curriculum requirements.

### Technical authenticity audit

| Check | Status | Evidence | Residual risk |
|---|---|---|---|
| Required headings/order | PASS | 8.0–8.16 present in order | None identified |
| L1 sequence/status vocabulary | PASS | Sections 8.2–8.3 | Event text varies |
| Object scope and commands | PASS | Scope table and read-only toolkit | Permissions/discovery vary |
| All 19 troubleshooting cases | PASS | Sections 8.4.1–8.4.19 | Runtime evidence required |
| Orphan definition/sources | PASS | Section 8.5 | Backend ownership data required |
| Safe cleanup sequence | PASS | Eight numbered steps | Approval duration is organizational |
| Finalizers and Retain cautions | PASS | Section 8.5 | Exact controller semantics remain version-specific |
| Report-only audit script | PASS with VERIFY | Section 8.6; context guard; no mutation path | Runtime/schema mapping not tested |
| Mandatory lab | PASS with VERIFY | Section 8.7; context/disk guard and residual scan | Not executed; runtime/path must be confirmed |
| 18 gauntlet cases with hints/rubric/fix/verification | PASS | Section 8.8 plus separated answer key | Representative cases only |
| Destructive commands labelled/gated | PASS | Section 8.7 | Operator must verify exact target/context |
| Backend leftovers checked | PASS with VERIFY | Section 8.7 residual scan/path check | Actual provisioner path not assumed |
| WSL2/kind caveats | PASS | Sections 8.2 and 8.7 | Host virtual-disk behavior varies |
| Sources/verification matrix | PASS | Section 8.14 | Environment-specific claims remain open |
| Runtime validation | VERIFY | Not executed in this environment | Local execution required |

### Five likely operator misreadings and resolutions

1. **“Released means orphan.”** Resolved: ownership, references, backend inventory, snapshots, operators, and recovery need review.
2. **“Deleting a PVC/PV necessarily deletes backend data.”** Resolved: reclaim policy and driver behavior matter; object deletion can also remove useful tracking.
3. **“Snapshot ready means verified backup.”** Resolved: restore to a new target and validate application data.
4. **“Stale VolumeAttachment should be deleted.”** Resolved: verify fencing and backend state, then follow driver/provider procedure.
5. **“Old PV with missing owner can be auto-pruned.”** Resolved: report UNKNOWN, quarantine, recheck, establish ownership/data safety, and require approval.

### Requirement traceability matrix

| Requirement | Lesson section | Concrete evidence | Status | Gap/caveat |
|---|---|---|---|---|
| Systematic sequence | 8.2 | Eight-step sequence | PASS | None |
| Data-safety rule | 8.0, 8.5, 8.7, 8.9 | Stop-work and explicit gates | PASS | Human must enforce |
| PVC/PV statuses | 8.2–8.3 | Definitions/table | PASS | Event wording varies |
| VolumeAttachment | 8.2, 8.4, 8.5 | Scope, troubleshooting, orphan handling | PASS | Driver-specific |
| Storage event families | 8.2–8.4, 8.11 | Definitions, cases, reference table | PASS | Version/driver caveat |
| `kubectl describe`, events, get PV/PVC/SC/VA | 8.2–8.3 | Commands and scope | PASS | Permissions vary |
| CSI controller/node logs | 8.2, 8.5 | Discovery and log commands | PASS | Must identify real driver |
| `kubectl debug node` | 8.2, 8.14 | Caveat and official source | VERIFY | Version/policy/permissions |
| `docker exec`/runtime alternative | 8.2, 8.7 | Exact node-container discovery | VERIFY | Runtime-specific |
| `df`, `lsblk`, `mount`, `dmesg` | 8.2, 8.4.11–12 | Node diagnostics | PASS | Platform permissions vary |
| Incident record | 8.2 | Full template | PASS | None |
| Pending: no class/default/wrong class | 8.4.1–2, 8.8 cases 1–2 | Decision trees and gauntlet | PASS | None |
| Pending: controller/quota/topology/WFFC | 8.4.3–6, 8.8 cases 3–4/13 | Decision trees and evidence | PASS | Backend-specific |
| ContainerCreating/attachment/Multi-Attach | 8.4.7–8, 8.8 case 16 | Evidence and safe response | PASS | Driver-specific |
| Permission/Secret/space/read-only | 8.4.9–12, 8.8 cases 7–8/17 | Decision trees | PASS | Filesystem/driver specifics |
| Expansion/snapshot/StatefulSet | 8.4.13–15, 8.8 cases 9–11 | Decision trees | PASS | Version/operator specifics |
| PVC finalizer/PV Released/Lost/slow I/O | 8.4.16–19, 8.8 cases 6/14/18 | Decision trees and gauntlet | PASS | Backend-specific |
| Orphan definition and causes | 8.5 | Definitions and candidate list | PASS | Inventory needed |
| Kubernetes discovery/JSONPath/jq | 8.5 | Inventory commands | PASS | Non-CSI fields may be empty |
| Backend reconciliation | 8.5 | Stable-ID/owner reconciliation | PASS | Provider-specific |
| Eight-step safe cleanup | 8.5 | Numbered procedure | PASS | Local approval policy |
| Finalizers and Retain recovery | 8.5 | Cautions and recovery principles | VERIFY | Exact version/driver steps |
| `fsck` safety | 8.4.12, 8.5 | Unmounted + backup/recovery plan | PASS | Filesystem-specific |
| Prevention program | 8.6 | Policy, ownership, TTL, inventory, alerts | PASS | Organization targets |
| Report columns | 8.6 | Script table columns | PASS | Backend ID may be unknown |
| Report-only default / `--apply` | 8.6, 8.7 | Script refuses mutation; manual exact lab cleanup | PASS | No generic destructive automation by design |
| Deletion protection / RBAC | 8.6, 8.10 | Policy concept and controls | VERIFY | API/engine version |
| Recovery drills | 8.6 | Retained PV, snapshot restore, controller outage | VERIFY | Driver-specific execution |
| Audit logs/handoff | 8.6, 8.9 | Audit config caveat and handoff template | VERIFY | Cluster retention |
| 18 gauntlet cases | 8.8 | Cases 1–18 and answer key | PASS | Not executed |
| Lab context/disk/footprint | 8.7.1 | Context guard, `df`, budget | PASS | Actual host usage varies |
| Lab retained PV/orphan candidate | 8.7.2–4 | Static PV, marker, Retain | VERIFY | Must execute locally |
| Quarantine/recheck/cleanup | 8.7.5–7 | Metadata, references, exact cleanup, residual scan | VERIFY | Actual node path must be confirmed |
| WSL2/kind caveats | 8.7 | Disk and local path notes | PASS | Host disk reclamation varies |
| SRE severity/RTO/RPO/review/handoff | 8.9 | Tables and templates | PASS | Targets workload-specific |
| Security/governance | 8.10 | RBAC, admission, redaction, break-glass | PASS | Policy implementation `[VERIFY]` |
| Required headings and diagrams | 8.0–8.16, 8.2 | All headings; lifecycle/component maps | PASS | None |
| Official sources/matrix | 8.14 | URLs and matrix | PASS | Environment-specific claims open |
| Independent audit | 8.15 | Audit table, five misreadings, traceability | PASS | Runtime validation open |
| Cross-module boundaries | 8.0, 8.11 | Exact sibling filenames and M03/M13/M15 | PASS | Siblings not separately inspected |

### Remaining VERIFY items

- Exact Kubernetes version/distribution behavior for finalizers, admission policy, expansion, snapshot CRDs, and node debugging.
- Actual CSI driver/sidecar versions, provisioner, backend APIs, and attachment semantics.
- Runtime execution of `orphan_report.py`; no live cluster was used here.
- Runtime application of lab manifests, exact worker/container mapping, local path behavior, and cleanup of leftovers.
- Filesystem-specific diagnostics and repair.
- Audit-log configuration/retention and the organization's deletion approval policy.
- Database/operator consistency and restore verification.

**Final audit status:** curriculum and safety workflow are statically reviewed against the uploaded Unit 8 prompt. Runtime validation is **OPEN**. Do not treat the report as a production deletion tool or the lab as proof of backend durability.

## 8.16 Final output contract

This file contains the standalone lesson for `08-storage-troubleshooting-and-orphaned-volumes.md` only. No repository file was modified. The lesson includes the required troubleshooting sequence, 19 decision trees, orphan-discovery and safe-cleanup workflow, report-only audit script, zero-budget kind lab, 18-case gauntlet with separated answer key, SRE/security guidance, evidence gate, official source/verification matrix, and independent traceability audit.

**Execution status:** file authored and statically reviewed; the script, manifests, and lab were **not executed in this environment**. Before production use, verify the exact Kubernetes version, CSI driver/sidecars, provisioner, backend, filesystem, database/operator, and local organizational approval process.
