# Unit 1 — Volumes, PersistentVolumes, PersistentVolumeClaims

This lesson introduces Kubernetes storage from first principles and progresses to production design, safe recovery, policy, and incident response. It uses disposable `kind` labs to demonstrate object lifecycle mechanics. It does **not** prove production durability: Kubernetes storage objects are API metadata; the actual bytes live in a filesystem, block device, network storage system, or driver-managed backend.

**Target file:** `01-volumes-persistentvolumes-and-persistentvolumeclaims.md` | **Estimated time:** 8–12 hours | **Prerequisites:** Pods, namespaces, security contexts, `kubectl`, basic Linux filesystems, SQL/data-pipeline familiarity.

**Core tools:** `kubectl`, `kind`, Bash, `jq` (optional), Docker or the runtime used by `kind` | **Awareness:** CSI drivers, cloud block/file storage, Ceph/Rook, Longhorn, OpenEBS, local static provisioner, backup/DR tools | **Last reviewed:** 2026-10-28 | **Kubernetes/tool baseline assumed:** Kubernetes APIs commonly available in a current supported `kind` release; exact cluster, runtime, provisioner and image versions are **[VERIFY]**. Discover them before execution. No lab below is claimed to have been run here.

## Contents

- [1.0 Why this matters in production](#10-why-this-matters-in-production)
- [1.1 Learning objectives](#11-learning-objectives)
- [1.2 Concept map and vocabulary](#12-concept-map-and-vocabulary)
- [1.3 Level 1 — Beginner](#13-level-1--beginner)
- [1.4 Level 2 — Intermediate](#14-level-2--intermediate)
- [1.5 Level 3 — Advanced](#15-level-3--advanced)
- [1.6 Level 4 — Expert](#16-level-4--expert)
- [1.7 SRE lens](#17-sre-lens)
- [1.8 Security lens](#18-security-lens)
- [1.9 Production checklist](#19-production-checklist)
- [1.10 Hands-on lab set](#110-hands-on-lab-set)
- [1.11 Self-check questions](#111-self-check-questions)
- [1.12 Evidence artifacts](#112-evidence-artifacts)
- [1.13 Common interview and design-review questions](#113-common-interview-and-design-review-questions)
- [1.14 Sources and verification notes](#114-sources-and-verification-notes)

## Unit 1 — Volumes, PersistentVolumes, PersistentVolumeClaims

### 1.0 Why this matters in production

A database Pod can be recreated after a node drain, rollout, or crash; if its only copy of the data lived in the container writable layer, the replacement may start empty. A PVC can preserve the association to storage across Pod replacement, but a reclaim policy or backend lifecycle mistake can still delete the underlying data. A local volume may remain intact while its node is unavailable, which is an outage even when the bytes are not destroyed. A permission change in a non-root image can turn a previously healthy database into a failed workload. Treat storage changes as data-plane changes: capture evidence, identify the exact volume, and verify recovery before returning service.

### 1.1 Learning objectives

By the end of this unit, the learner can:

1. [L1] Explain the difference between an image layer, container writable layer, Pod, node, PV/PVC API objects, and backing storage.
2. [L1] Create and inspect a PVC and prove data survives Pod deletion and recreation.
3. [L1] Compare volume sources and accurately describe RWO, ROX, RWX, and RWOP limitations.
4. [L2] Choose `Filesystem` or `Block`, a reclaim policy, and security context based on a workload's requirements.
5. [L2] Diagnose common `Pending`, mount, permission, and PVC-deletion symptoms using Events and object descriptions.
6. [L3] Trace the provision/bind/attach/mount/use/unmount/detach/reclaim lifecycle and identify responsible components.
7. [L3] Design a safe `Retain` recovery decision process and explain why etcd snapshots do not back up PV bytes.
8. [L4] Run a read-only audit for suspicious PVs/PVCs and ownership gaps.
9. [L4] Propose storage policy and incident-prevention controls with explicit verification evidence.

### 1.2 Concept map and vocabulary

| Term | Precise definition | Common misconception |
|---|---|---|
| Volume | A Pod-mounted storage source with a lifecycle and implementation defined by its type | Every volume survives Pod deletion |
| `emptyDir` | Scratch volume created for a Pod and removed when that Pod is removed from its node | It is a durable disk |
| PV | Cluster-scoped API object representing a provisioned storage resource | The PV object itself contains file bytes |
| PVC | Namespaced request for storage; usually binds to one PV | A PVC is a directory or backup |
| StorageClass | Cluster object describing a storage provisioning class and parameters | Every cluster has the same default class |
| Provisioner / CSI driver | Components that create, attach, mount, or otherwise manage backend storage | Kubernetes core implements every backend operation |
| Access mode | Declared access semantics used in matching and supported mount workflows | RWO is a universal database lock |
| Reclaim policy | Instruction for what happens to a PV's backing resource after its claim is released | `Retain` means the data is backed up |
| `volumeMode` | Whether the volume is exposed as a filesystem or raw block device | Block mode is mounted as a normal directory |
| Backing storage | The actual disk, filesystem, network share, or driver-managed resource holding bytes | API YAML is the data itself |
| Finalizer | Metadata that delays deletion until a controller's cleanup/protection condition is satisfied | A `Terminating` object should be force-deleted immediately |

```text
Pod container
   | volumeMount (path inside container)
   v
PVC (namespaced request) ---- PVC/PV controller binds ---- PV (cluster object)
                                                     |
                                  provisioner / CSI driver / kubelet
                                                     |
                                                     v
                      backing storage: host path, disk, network filesystem,
                      or driver-managed device (THE ACTUAL DATA BYTES)
```

The diagram is conceptual: not all volume types use a PV, CSI, attach step, or network device. For a PVC-backed volume, the Pod references the PVC by name. Kubernetes controllers coordinate objects; a provisioner and/or CSI driver maps the PV to real storage. The kubelet and node-side driver make the storage available to the Pod. A local-path provisioner may map the PV to a path on the kind node container. That path is not a cloud disk and can disappear with the node/cluster.

#### Volume-source comparison

| Source | Lifecycle / data source | Typical purpose | Persistence boundary | Key risk |
|---|---|---|---|---|
| `emptyDir` | Created for a Pod on a node | Scratch, shared files between containers | Pod lifetime on node | Data lost when Pod is removed |
| `hostPath` | Existing path on the node filesystem | Narrow node-level integration or lab demos | Node and host path | Host data exposure, node coupling |
| `configMap` | Kubernetes ConfigMap data projected into a volume | Non-secret configuration | ConfigMap/Pod projection behavior | Not intended for application data |
| `secret` | Kubernetes Secret data projected into a volume | Credentials, keys | Secret object/projection lifecycle | Requires access control and encryption practices |
| projected | Combines supported sources such as Secret, ConfigMap, downward API, service-account token | Unified configuration directory | Source-object/token lifecycle | Not a general persistent-data store |
| `persistentVolumeClaim` | References a PVC bound to a PV | Database/data that must outlive a Pod | Backing-storage and reclaim policy | PVC is not a backup or durability guarantee |
| generic ephemeral | Pod template creates a PVC-backed volume with Pod lifecycle | Temporary storage with StorageClass features | Typically tied to owning Pod | Cleanup/provisioner behavior must be understood |
| CSI inline ephemeral | Driver-managed ephemeral volume declared in Pod | Specialized ephemeral storage | Driver-defined Pod lifecycle | Requires driver support and permissions |

#### Access-mode comparison

| Mode | Declared semantics | Typical use | Important caveat |
|---|---|---|---|
| `ReadWriteOnce` (RWO) | Read-write mount from one node at a time | Single-node database volume | It does **not** universally mean only one Pod; same-node behavior depends on Kubernetes/driver/backend **[VERIFY]** |
| `ReadOnlyMany` (ROX) | Read-only mounts from multiple nodes, where supported | Shared read-only datasets | Backend and driver must support it |
| `ReadWriteMany` (RWX) | Read-write mounts from multiple nodes, where supported | Shared filesystem content | Usually requires a shared filesystem or equivalent; concurrent writers need application-level correctness |
| `ReadWriteOncePod` (RWOP) | Intended to restrict a CSI volume to one Pod | Stronger single-Pod mounting constraint | Kubernetes/CSI sidecar compatibility and deployment conditions are **[VERIFY]** |

Access modes help Kubernetes match and mount volumes; they are not database replication, application locks, or a universal proof of backend behavior. Verify the installed driver's capabilities and Kubernetes version.

### 1.3 Level 1 — Beginner

#### What disappears when a container stops?

An image contains read-only layers. A running container normally adds a writable layer above them. If a container or Pod is replaced, data written only to that writable layer is not a reliable persistence mechanism. A volume provides a separate source mounted into the container. Its survival depends on the volume type: `emptyDir` is scratch, while a PVC can refer to storage that outlives the Pod.

- **Image layer:** packaged application files; immutable at runtime.
- **Container writable layer:** changes local to a container instance; do not use as the system of record.
- **Pod lifetime:** `emptyDir` normally ends when the Pod is removed from its node.
- **Node lifetime:** local storage is tied to a node and may become unavailable or be lost with it.
- **Backing storage lifetime:** determined by backend, provisioning, reclaim policy, operator, and operational procedures.

#### PV and PVC in plain language

A PV is the supply side; a PVC is a namespaced request. A claim asks for a capacity, access mode, volume mode, and optionally a StorageClass. A matching PV can bind to the claim. A typical PV/PVC binding is one-to-one: one claim binds to one volume. The requested size is a capacity request, not a promise of IOPS, throughput, latency, encryption, replication, or backup.

A PVC can be `Pending` while no suitable volume is available or provisioning is waiting; `Bound` means a PV has been bound; `Lost` indicates the claim's bound volume is no longer available as expected. Investigate actual status, conditions, and Events rather than assuming a phase has only one cause.

#### First commands

```bash
kubectl config current-context
kubectl get storageclass
kubectl get pv,pvc
kubectl get pvc -A
kubectl describe pvc <claim-name> -n <namespace>
kubectl describe pv <pv-name>
kubectl get events -n <namespace> --sort-by=.metadata.creationTimestamp
```

Events may be absent because none were emitted or they expired. `describe` is evidence, not a root-cause guarantee.

#### Static provisioning: the idea

With static provisioning, an administrator creates a PV that points to an existing backend, then a PVC claims it. Local static PVs require node affinity and are not portable. A production-quality local static PV requires a deliberately prepared host path/device, ownership, node affinity, capacity accounting, and a recovery plan. Do not copy a `hostPath` example into production.

#### Runnable PVC persistence proof

First inspect your environment:

```bash
set -euo pipefail
kubectl config current-context
kind get clusters
kubectl get storageclass
df -h .
```

Use a disposable cluster/context only. Discover the actual default StorageClass; do not assume its name. The following uses no explicit class and therefore depends on a default class being configured.

**File: `lab-a-pvc-persistence.yaml` — disposable namespace, PVC, and writer Pod**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: m05-pv-pvc-lab
  labels:
    app.kubernetes.io/part-of: m05-storage-labs
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: persistence-data
  namespace: m05-pv-pvc-lab
  labels:
    app.kubernetes.io/part-of: m05-storage-labs
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 256Mi
---
apiVersion: v1
kind: Pod
metadata:
  name: persistence-writer
  namespace: m05-pv-pvc-lab
  labels:
    app.kubernetes.io/part-of: m05-storage-labs
spec:
  restartPolicy: Never
  containers:
    - name: writer
      image: busybox:1.36
      command: ["/bin/sh", "-c"]
      args:
        - "date -u +%FT%TZ > /data/marker.txt; echo 'm05-persistence-marker-v1' >> /data/marker.txt; cat /data/marker.txt; sleep 3600"
      resources:
        requests:
          cpu: 10m
          memory: 16Mi
          ephemeral-storage: 16Mi
        limits:
          cpu: 100m
          memory: 64Mi
          ephemeral-storage: 64Mi
      securityContext:
        allowPrivilegeEscalation: false
        runAsUser: 1000
        runAsGroup: 1000
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: persistence-data
```

[VERIFY] The selected default provisioner must support this access mode and the non-root write permissions. If the Pod cannot write, inspect ownership and use the `fsGroup` lab below rather than weakening the security context blindly.

```bash
kubectl apply --dry-run=client -f lab-a-pvc-persistence.yaml
kubectl apply -f lab-a-pvc-persistence.yaml
kubectl get pvc,pod -n m05-pv-pvc-lab -o wide
kubectl describe pvc persistence-data -n m05-pv-pvc-lab
kubectl logs persistence-writer -n m05-pv-pvc-lab
kubectl exec -n m05-pv-pvc-lab persistence-writer -- cat /data/marker.txt
```

**Expected output (representative; not executed here):** PVC phase `Bound`; Pod eventually `Running` or `Completed` only if its command exits (this example sleeps); marker includes `m05-persistence-marker-v1`.

**DATA-SAFETY PREFACE — THROWAWAY LAB ONLY:** Before deleting the Pod, confirm the current context and exact namespace/Pod name. This deletion is intended to remove only the writer Pod, not the PVC.

```bash
kubectl config current-context
kubectl get pod persistence-writer -n m05-pv-pvc-lab
kubectl delete pod persistence-writer -n m05-pv-pvc-lab
```

Recreate only the Pod from the same manifest. Applying the manifest recreates the Pod and leaves the PVC object in place:

```bash
kubectl apply -f lab-a-pvc-persistence.yaml
kubectl wait --for=condition=Ready pod/persistence-writer -n m05-pv-pvc-lab --timeout=120s
kubectl exec -n m05-pv-pvc-lab persistence-writer -- cat /data/marker.txt
```

If the marker survives, the Pod was replaced while the claim/backing volume remained. Deleting the PVC is a different operation and may trigger PV/backend cleanup according to reclaim policy. Deleting a kind cluster can destroy node-local backing data. Do not infer backup or node-failure resilience from this test.

### 1.4 Level 2 — Intermediate

#### Filesystem versus block mode

| `volumeMode` | Consumption | Use when | Risk / caveat |
|---|---|---|---|
| `Filesystem` (default when omitted) | Mounted at a container path as a filesystem | Most databases and file-oriented applications | Filesystem and ownership behavior depend on backend/driver |
| `Block` | Exposed as a raw device through `volumeDevices`, not a directory mount | Applications explicitly designed to manage a block device | Application must handle device semantics; support is backend-dependent |

#### `Retain` versus `Delete`

| Policy | PV object after claim release | Backing-data consequence | Appropriate use | Risk |
|---|---|---|---|---|
| `Retain` | Commonly becomes `Released` and remains for administrator recovery | Backend resource is intended to remain; exact behavior is backend-specific | Data requiring controlled review before reuse/deletion | Orphaned capacity and manual recovery mistakes |
| `Delete` | PV object and provisioned backing resource are generally deleted by the provisioner/controller workflow | Data may be irreversibly removed | Disposable data or explicitly approved lifecycle deletion | Accidental claim deletion can delete data |
| `Recycle` | Deprecated/removed or unsupported in modern clusters; **[VERIFY]** | Do not rely on it | Do not choose for new designs | Behavior is version-sensitive |

The PV object's deletion and the backing resource's deletion are distinct events. `Retain` is not a backup. Never choose `Delete` for data that must be preserved unless a separately tested backup/recovery design exists.

#### `Immediate` versus `WaitForFirstConsumer`

`Immediate` provisioning/binding may happen as soon as a PVC is created. `WaitForFirstConsumer` delays provisioning/binding until a Pod is scheduled, allowing topology-aware provisioning to consider the consumer's scheduling constraints. Actual behavior depends on the StorageClass and provisioner; Unit 2 covers CSI and topology in depth.

#### PVC `selector`, `volumeName`, and mount options

- A PVC `selector` can restrict matching PVs by labels; it does not create a PV.
- `volumeName` can target a specific PV for pre-binding. The PV must still be compatible and available; conflicts can leave a claim pending.
- `mountOptions` are backend/filesystem-specific. Kubernetes does not validate every option for every backend. Copy only options documented for the actual driver/filesystem.

#### `subPath` and `subPathExpr`

Use `subPath` to mount a subdirectory from a volume, such as `/data/team-a`, into a container path without mounting the entire volume. `subPathExpr` can derive a subpath from environment variables where supported by the Kubernetes baseline. Avoid unsafe symlink assumptions and ensure untrusted workloads cannot manipulate paths to access unintended data. **[VERIFY]** Check current Kubernetes documentation for the exact subPath security behavior and supported features. ConfigMap/Secret updates do not propagate as live updates through a `subPath` mount; verify current behavior before relying on rotation semantics.

#### Non-root permissions and `fsGroup`

`runAsUser` selects the process UID; `runAsGroup` selects its primary GID. `fsGroup` can provide a supplemental group used for volume access, but how ownership/mode changes occur depends on volume type, filesystem, and CSI driver's `CSIDriver.spec.fsGroupPolicy`. **[VERIFY]** Do not assume `fsGroup` recursively changes every backend's ownership.

**File: `lab-c-fsgroup.yaml` — disposable permission test**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: fsgroup-data
  namespace: m05-pv-pvc-lab
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 256Mi
---
apiVersion: v1
kind: Pod
metadata:
  name: fsgroup-check
  namespace: m05-pv-pvc-lab
spec:
  restartPolicy: Never
  securityContext:
    runAsUser: 10001
    runAsGroup: 20001
    fsGroup: 20001
    fsGroupChangePolicy: OnRootMismatch
  containers:
    - name: check
      image: busybox:1.36
      command: ["/bin/sh", "-c"]
      args: ["id; ls -ldn /data; echo fsgroup-proof > /data/proof.txt; ls -ln /data/proof.txt; sleep 3600"]
      resources:
        requests:
          cpu: 10m
          memory: 16Mi
          ephemeral-storage: 16Mi
        limits:
          cpu: 100m
          memory: 64Mi
          ephemeral-storage: 64Mi
      securityContext:
        allowPrivilegeEscalation: false
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: fsgroup-data
```

Apply after confirming the context and that the namespace is disposable:

```bash
kubectl apply --dry-run=client -f lab-c-fsgroup.yaml
kubectl apply -f lab-c-fsgroup.yaml
kubectl wait --for=condition=Ready pod/fsgroup-check -n m05-pv-pvc-lab --timeout=120s
kubectl exec -n m05-pv-pvc-lab fsgroup-check -- id
kubectl exec -n m05-pv-pvc-lab fsgroup-check -- ls -ln /data /data/proof.txt
kubectl logs -n m05-pv-pvc-lab fsgroup-check
```

If the write fails, collect `kubectl describe pod`, PVC/PV YAML, Events, UID/GID and mode output, and provisioner documentation. Do not “fix” it by running the application as root without assessing the security impact.

#### `emptyDir.medium: Memory` and `sizeLimit`

A memory-backed `emptyDir` is typically implemented with tmpfs. A `sizeLimit` can cap the volume, but memory accounting and pressure behavior vary with node/runtime configuration. Treat it as memory-consuming scratch, not free disk. Set Pod memory requests/limits and verify actual behavior on the target platform.

#### `hostPath`, protection finalizers, and Events

`hostPath` couples a Pod to node filesystem state and can expose host files or sockets; it is not a general production persistence strategy. PVC/PV protection finalizers (`kubernetes.io/pvc-protection`, `kubernetes.io/pv-protection`) can delay deletion while an object is in use. A PVC stuck in `Terminating` is a reason to investigate Pod references, controller state, Events, and backend state—not a reason to immediately remove a finalizer.

| Symptom / Event | Likely meaning | Safe verification | Next action |
|---|---|---|---|
| PVC `Pending` | No matching PV, provisioner issue, quota, or delayed binding | `kubectl describe pvc`; inspect StorageClass and Events | Resolve the specific mismatch; do not repeatedly delete/recreate blindly |
| `FailedBinding` | Claim cannot bind to a compatible PV | Inspect capacity, modes, class, selector and `volumeName` | Correct claim/PV design after capturing YAML |
| `ProvisioningFailed` | Provisioner/backend failed | Inspect provisioner logs and class parameters | Follow driver-specific runbook |
| `FailedMount` / `MountVolume.SetUp failed` | Node plugin, filesystem, permissions, or backend problem | Describe Pod; inspect node/CSI logs if authorized | Fix root cause before restarting repeatedly |
| `Multi-Attach` | Backend volume is still attached or attachment constraints conflict | Inspect Pods, nodes, `VolumeAttachment` where applicable | Ensure old writer is stopped; follow driver recovery steps |
| PVC `Terminating` | Protection finalizer or controller cleanup is waiting | Inspect finalizers and Pods referencing the claim | Resolve references/controller problem; finalizer removal is last resort |
| `Lost` | Previously bound volume is no longer available as expected | Inspect PV status, events, backend and provisioner | Preserve evidence and invoke recovery runbook |

### 1.5 Level 3 — Advanced

#### End-to-end volume lifecycle

`provision → bind → attach → mount → use → unmount → detach → release → reclaim`

| Stage | Typical owner(s) | Notes |
|---|---|---|
| Provision | Dynamic provisioner / CSI controller plugin / backend | Static PVs may already exist |
| Bind | Kubernetes PV controller | Matches claim and PV constraints |
| Attach | Attach/detach controller and CSI attacher/controller, when required | Some storage types do not require a separate attach |
| Mount | kubelet and CSI node plugin / filesystem tooling | Node-specific; errors often surface in Pod Events |
| Use | Application process in container | Application correctness and locking remain application responsibilities |
| Unmount / detach | kubelet, CSI node/controller plugins and backend | Must account for stale writers and detach delays |
| Release | Kubernetes PV controller after claim deletion/release | PV may become `Released` |
| Reclaim | Provisioner/backend according to reclaim policy | Verify whether data/resource is retained or deleted |

The exact sequence and components vary by volume type. CSI external sidecars (for example provisioner, attacher, resizer) coordinate API interactions; the CSI controller and node plugins implement driver operations. Kubernetes core does not implement every backend feature.

#### Safe `Retain` recovery for a `Released` PV

> **DATA-SAFETY PREFACE — RECOVERY PROCEDURE:** Do not mutate `claimRef`, bind the PV, mount the device read-write, or delete anything until the old workload is stopped, the exact PV/backend identity is confirmed, evidence is captured, and a copy/snapshot is made where supported. A wrong-PV edit can expose or overwrite another workload's data.

1. Freeze changes to the workload and confirm no Pod or external process can write to the volume.
2. Capture `kubectl get pv <pv> -o yaml`, `kubectl describe pv <pv>`, the former PVC YAML if available, relevant Pod YAML, Events, and driver/backend identifiers.
3. Confirm the PV's `persistentVolumeReclaimPolicy`, phase, `claimRef`, StorageClass, node affinity, CSI volume handle or local path. Never guess a host path or volume handle.
4. Create a backend snapshot/copy if supported, and verify its identity. A snapshot is not necessarily application-consistent and is not automatically an off-system backup.
5. Determine the supported rebind procedure for the exact Kubernetes version and provisioner. Clearing `claimRef` is a mutation with ownership and race risks; do not copy a generic patch into production.
6. Rebind only to a reviewed, compatible claim and verify PV/PVC binding and mount behavior in an isolated recovery Pod if appropriate.
7. Validate application-level integrity (for example, database recovery/checksums and expected records) before service resumes. Document the decision and evidence.

#### Local PVs, scratch, quota, encryption, and backups

A `local` PV requires `nodeAffinity` to constrain scheduling to the node holding the storage. If the node is unavailable, data may be unavailable; if the node/device is destroyed without another copy, data may be lost. Draining or replacing the node does not magically move local bytes. Distinguish unavailability from destruction and follow the platform's recovery policy.

Generic ephemeral volumes can provide PVC-backed scratch with a Pod-linked lifecycle. CSI inline ephemeral volumes are driver-specific. They can fit ETL temporary files or Spark shuffle only if the selected driver supports the feature and its lifecycle is understood. Use PVC-backed persistent storage for data that must survive Pod replacement.

A namespace `ResourceQuota` can constrain `requests.storage` and, where configured, per-StorageClass consumption. A `LimitRange` may set PVC request bounds depending on cluster configuration. These are admission/accounting controls, not proof that physical backend capacity is available. See M03 Unit 2 for quota fundamentals.

Storage-layer encryption at rest belongs to the backend, driver, or platform and must be verified with configuration and key-management evidence. Kubernetes etcd snapshots contain Kubernetes API state, not the bytes stored in PV backing storage. Restoring cluster metadata without the corresponding backing data does not restore a database. See M03 Unit 10 and M13 for backup/DR programs, offsite copies, immutability, RPO/RTO, and cross-cluster recovery.

#### Design trade-offs

| Decision | Benefit | Cost / risk | Choose when |
|---|---|---|---|
| Ephemeral volume vs PVC | Ephemeral is simple and disposable; PVC survives Pod replacement | Ephemeral data loss vs storage lifecycle complexity | Scratch → ephemeral; required retained data → PVC |
| Local PV vs network-backed | Local can offer low-latency access; network storage can decouple data from node | Local node failure coupling; network latency/cost/backend dependency | Local only with explicit node-loss plan; network-backed for supported mobility/availability needs |
| RWO vs RWX/RWOP | Matches common single-writer or shared-data patterns | Backend capability and concurrency correctness vary | Select from application semantics and driver support, not convenience |
| `Retain` vs `Delete` | Retain allows reviewed recovery; Delete automates cleanup | Orphans/manual work vs accidental data deletion | Retain for data requiring controlled disposition; Delete only when deletion is intended |
| Filesystem vs block | Filesystem simplifies file-based applications; block enables raw-device applications | Filesystem overhead/semantics vs app/device complexity | Most file-oriented services → filesystem; block only for applications designed for it |

#### Decision exercise

Write a short decision record for:
- **PostgreSQL metadata:** state required recovery objectives, single-writer behavior, backup/restore method, reclaim policy, encryption, monitoring, and what happens on node loss.
- **ETL scratch:** decide whether data can be recomputed; choose ephemeral or PVC storage; set capacity limits and cleanup.
- **Shared read-only artifacts:** choose a backend/driver that truly supports shared reads; distinguish a filesystem share from object storage mounted through a gateway; verify consistency and update semantics.

Defend trade-offs and explicitly list what a local `kind` test cannot prove.

### 1.6 Level 4 — Expert

#### Governance at fleet scale

Use stable labels/annotations for ownership and inventory, for example:

```yaml
metadata:
  labels:
    app.kubernetes.io/part-of: feature-platform
    platform.example.com/team: data-platform
    platform.example.com/environment: production
    platform.example.com/data-classification: confidential
  annotations:
    platform.example.com/owner-runbook: "runbooks/storage/feature-db"
    platform.example.com/backup-policy: "daily-plus-pitr"
    platform.example.com/cost-center: "data-platform"
```

These example labels and annotations are organization-defined metadata, not Kubernetes-enforced controls. Define a naming standard, data classification, service owner, StorageClass owner, retention decision, backup evidence, decommissioning approver, and incident escalation path. Require a review record before storage-class or reclaim-policy changes.

#### Policy-as-code design

A production policy should validate PVC requests against an approved StorageClass catalog, minimum/maximum size, allowed access modes, namespace/environment, and forbidden volume sources such as `hostPath`. Enforce PV reclaim policy at the layer that manages PV/StorageClass creation; a PVC admission policy cannot automatically rewrite a separate PV object unless a specific policy/controller is designed to do that. Kyverno, Gatekeeper, and ValidatingAdmissionPolicy are possible approaches; exact APIs and syntax are **[VERIFY]** against the deployed Kubernetes and policy-engine versions.

Illustrative policy requirements (not a drop-in policy):
- production PVC must set an approved `storageClassName`;
- `requests.storage` must be within an approved range;
- `hostPath` is denied except a narrowly approved platform namespace;
- PVs in designated production classes must use an approved reclaim policy;
- every PVC/PV must carry ownership metadata or be reported as a policy violation.

Test policies with valid and invalid manifests in a disposable cluster before enforcement.

#### Read-only audit script

**File: `audit-pv-pvc.sh` — read-only inventory; requires `kubectl` and `jq`**

```bash
#!/usr/bin/env bash
set -euo pipefail

context="$(kubectl config current-context)"
printf 'Context: %s\n' "$context"
printf '%s\n' 'READ-ONLY audit: no resources will be changed.'

pvc_json="$(kubectl get pvc -A -o json)"
pv_json="$(kubectl get pv -o json)"

printf '\nPVCs not Bound:\n'
jq -r '.items[] | select(.status.phase != "Bound") |
  [.metadata.namespace, .metadata.name, (.status.phase // "Unknown"),
   (.spec.storageClassName // "<default-or-empty>")] | @tsv' <<<"$pvc_json"

printf '\nPVCs missing team ownership label:\n'
jq -r '.items[] | select((.metadata.labels["platform.example.com/team"] // "") == "") |
  [.metadata.namespace, .metadata.name] | @tsv' <<<"$pvc_json"

printf '\nSuspicious PV phases:\n'
jq -r '.items[] | select(.status.phase == "Released" or .status.phase == "Failed" or .status.phase == "Lost") |
  [.metadata.name, (.status.phase // "Unknown"),
   (.spec.persistentVolumeReclaimPolicy // "<unset>"),
   (.spec.claimRef.namespace // "<none>"),
   (.spec.claimRef.name // "<none>")] | @tsv' <<<"$pv_json"

printf '\nPVs missing team ownership label:\n'
jq -r '.items[] | select((.metadata.labels["platform.example.com/team"] // "") == "") |
  [.metadata.name, (.status.phase // "Unknown")] | @tsv' <<<"$pv_json"
```

The script intentionally does not delete or mutate. `kubectl get` requires permissions to list PVs cluster-wide and PVCs across namespaces; least-privilege access may prevent the complete report. Empty lists produce no matching rows. Without `jq`, save the JSON and inspect it with a reviewed alternative; do not improvise a destructive parser. “Possibly orphaned” is a lead for investigation, not a deletion decision: compare owner records, Pods, claims, backend resources, and retention policies.

#### Incident A — PVC deletion removed production data under `Delete`

- **Symptom:** PVC and PV disappear; backend volume or data path is absent.
- **Hypotheses:** expected reclaim behavior; provisioner cleanup; wrong claim deleted; backend lifecycle automation removed the resource.
- **Safe checks:** stop automation that could delete more; capture audit logs, prior YAML, PV reclaim policy, provisioner logs and backend identifiers. Do not recreate a same-named claim and assume it reconnects to the old bytes.
- **Root cause:** claim deletion released a PV whose policy/provisioner workflow deleted the backing resource.
- **Recovery:** restore from a tested backup/snapshot/replica if one exists. Deleted backend data is not guaranteed recoverable; escalate to the storage provider/platform team.
- **Prevention:** policy gates, explicit deletion approval, backups outside the same failure domain, restore drills, and alerts on PV/PVC deletion.

#### Incident B — mounted volume fails after image switches to non-root

- Check `runAsUser`, `runAsGroup`, `fsGroup`, file owner/mode (`ls -ln`), mount path, read-only flags, and Pod Events.
- Inspect the driver and `CSIDriver.spec.fsGroupPolicy` where relevant. A filesystem that worked for root may deny UID/GID 10001.
- Prefer deliberate ownership/group setup and least privilege. Avoid recursive `chown` against a live database directory unless the application is stopped and the storage procedure is approved.
- Add a regression test that mounts a disposable claim using the production security context and verifies read/write behavior.

#### Incident C — PVC remains `Terminating`

Decision path:
1. Capture current context, PVC YAML, finalizers, Events, and namespace.
2. Identify Pods that reference the PVC and confirm whether any writer is active.
3. Check the PV phase/claim reference and provisioner/controller state; inspect CSI/backend state if the driver uses it.
4. Resolve legitimate references or controller/backend failures and allow cleanup to reconcile.
5. Consider finalizer mutation only as an incident-specific last resort after storage ownership, backup/copy, and controller/backend state are confirmed by the storage owner. Removing finalizers can orphan storage, bypass cleanup, or cause data loss. This lesson does not recommend a routine force-removal command.

#### Ten adversarial failure checks

1. Pod deletion mistaken for PVC deletion.
2. PVC deletion mistaken for harmless metadata cleanup under `Delete`.
3. `Retain` mistaken for backup.
4. etcd snapshot mistaken for PV-data backup.
5. RWO mistaken for application-level single-writer locking.
6. Local volume assumed to move with a replacement node.
7. `fsGroup` assumed to work identically for every CSI driver.
8. `Terminating` finalizer removed before checking active Pod references.
9. Host path guessed instead of discovered from PV/driver metadata.
10. `kind` persistence proof mistaken for production durability.

Each is addressed in the sections above; backend/version-specific items remain open until verified on the actual environment.

### 1.7 SRE lens

#### Storage SLIs and signals

| SLI / signal | Likely source | Interpretation |
|---|---|---|
| PVC-bound time and Pending count | Kubernetes object status and Events | Provisioning/scheduling friction |
| Attach/mount latency and failures | Events, CSI controller/node logs, backend telemetry | Driver/backend or topology issue |
| Volume capacity/headroom | Node filesystem metrics, backend metrics, application metrics | Disk-full risk; Kubernetes requests are not physical capacity |
| Write/read errors and database availability | Application/database telemetry | User-visible impact, not always visible from PVC phase |
| Backup age and restore-test pass rate | Backup system and scheduled restore tests | Recovery capability, not merely storage health |

Kubernetes exposes object status and Events natively; detailed attach latency, backend capacity, IOPS, replication health, and database integrity often require CSI/backend/application telemetry. Failure blast radius ranges from one Pod's scratch files to every workload sharing a storage backend. Node-local data can create a node-sized blast radius; a shared backend or bad automation can affect many claims.

**Runbook snippet:** alert → confirm current context and affected claim → collect PVC/PV/Pod YAML and Events → determine whether data is unavailable or destroyed → stop unsafe retries/writers → follow driver-specific recovery → validate application integrity → record timeline and prevent recurrence.

Capacity notes: a requested size is not a throughput or physical-capacity guarantee. Track node disk pressure, provisioned versus consumed storage, quotas, orphaned retained volumes, and backup storage separately. WSL2 virtual-disk files may not shrink automatically after in-container deletion; verify host and VM disk usage separately.

### 1.8 Security lens

Threats include cross-tenant access, broad `hostPath` exposure, secrets in configuration, sensitive data in snapshots/backups, unencrypted storage, privileged CSI node plugins, and overly broad operator/service-account permissions.

Controls and checks:
- Verify namespace/RBAC boundaries: `kubectl auth can-i get pvc -n <namespace> --as=<subject>`.
- Inspect Pod security context and mounts: `kubectl get pod <pod> -n <namespace> -o yaml`.
- Search manifests/policies for `hostPath`; enforce deny-by-default policy and document exceptions.
- Inspect PV/StorageClass and backend configuration for encryption claims; Kubernetes YAML alone may not prove encryption at rest.
- Restrict snapshot/backup read access and test key recovery separately.
- Use fake lab credentials only; do not commit real secrets in manifests.
- Review CSI node plugin privileges and host mounts as part of platform threat modeling.

This lesson does not establish a complete security boundary, prove backend encryption, secure a real cluster, or create an enterprise backup program. Those require platform-specific controls and verification.

### 1.9 Production checklist

- [ ] Confirm the selected StorageClass, provisioner, and backend capability with `kubectl get sc -o yaml` and driver documentation.
- [ ] Document requested capacity and validate backend capacity/headroom separately.
- [ ] Verify access mode and filesystem/block support against the actual backend.
- [ ] Review reclaim policy and test deletion behavior only with disposable data.
- [ ] Add team/service/environment/data-classification ownership labels and verify them.
- [ ] Test the production `runAsUser`/`runAsGroup`/`fsGroup` context against a disposable PVC.
- [ ] Enforce PVC size quotas and approved StorageClass policy.
- [ ] Restrict `hostPath` with admission policy and audit.
- [ ] Investigate finalizers and active Pod references before any deletion escalation.
- [ ] Document that etcd backups do not contain PV backing bytes.
- [ ] Preserve evidence that data survives Pod recreation.
- [ ] Document an independent backup/restore path and retain restore-test evidence; the local-path lab is not that path.
- [ ] Record the owner, runbook, retention decision, and decommissioning approval for each production claim.
- [ ] Verify monitoring for Pending claims, mount failures, disk headroom, backup age, and restore success.

### 1.10 Hands-on lab set

All estimates below are rough incremental footprints, not guarantees. Check `df -h .` and your WSL2/host free space before each lab. Do not run heavy stacks concurrently. Every lab must run in a disposable `kind` context.

#### Lab A — PVC persistence across Pod deletion

- **Goal:** Prove write → Pod deletion → recreation → marker persistence.
- **Prerequisites:** `kind`, `kubectl`, default StorageClass discovered; about 50–200 MiB estimated.
- **Steps:** Use `lab-a-pvc-persistence.yaml` from Section 1.3; capture context; apply; inspect PVC/Pod; read marker; delete only `persistence-writer`; reapply and read the marker again.
- **Expected evidence:** PVC remains `Bound`; exact `m05-persistence-marker-v1` text is still readable.
- **Cleanup:** See the cleanup block below; this removes the lab namespace and its PVC/data.
- **Re-run safety:** Reapplying is safe only after confirming the existing claim contains disposable data. If the Pod already exists, inspect it before replacing it.
- **Stretch:** Record PV name, provisioner, reclaim policy, and backing location from discovered metadata.
- **Kind caveat:** Proves persistence across Pod replacement only. It does not prove node-loss recovery or cloud durability.

#### Lab B — `Delete` versus `Retain` reclaim policy (throwaway data only)

- **Goal:** Observe PV-object and backend behavior separately.
- **Prerequisites:** A disposable cluster and provisioner whose reclaim behavior you have verified; estimate 100–300 MiB. Do not assume the default class exposes a host path or honors policy exactly as expected.
- **Steps:** Create two isolated disposable claims with clearly distinct names and policies, write unique marker files, capture PV/PVC YAML, then delete only the named claims after the warning below. Observe whether PV objects and backend data remain. If the provisioner does not expose or honor this comparison, stop and document the limitation; use a conceptual lifecycle diagram or a separately created static local PV in a disposable node for the object-state explanation instead.
- **Expected evidence:** Before/after `kubectl get pv,pvc`, PV YAML including `persistentVolumeReclaimPolicy`, provisioner logs where available, and backend identity/path if discoverable.
- **Host-path inspection:** If `kind` uses Docker, discover node container names with `docker ps --format '{{.Names}}'` and identify the PV's actual `spec.hostPath.path` or documented driver mapping first. Only then inspect the discovered path inside the correct node container. Do not guess paths. With Podman, use the corresponding Podman commands; if the runtime is different, follow its documented node-container inspection method.
- **Cleanup:** Delete only the named throwaway claims/Pods and then inspect for retained PVs/backend leftovers. Remove retained data only after confirming the exact identity.
- **Re-run safety:** Never reuse a previous lab's PV/backend path without inspecting its contents and ownership.
- **Stretch:** Explain why the PV object disappearing does not prove every backend byte was securely erased.
- **Kind caveat:** Behavior depends on the installed provisioner; do not claim the comparison succeeded unless observed.

> **⚠ DESTRUCTIVE — DATA LOSS:** The next operation, if you choose to perform the comparison, deletes only the specifically named throwaway claim and may delete its backing data under `Delete`. First run `kubectl config current-context`, `kubectl get pvc -n m05-pv-pvc-lab`, `kubectl get pv -o wide`, and capture YAML. Do not run this against production or any claim with valuable data.

#### Lab C — non-root volume permissions and `fsGroup`

- **Goal:** Verify UID/GID and write behavior for a non-root process.
- **Prerequisites:** disposable PVC; estimate 50–200 MiB.
- **Steps:** Use `lab-c-fsgroup.yaml`; apply; inspect `id`, directory mode, and proof file; if the baseline fails, capture Events and driver behavior before changing anything.
- **Expected evidence:** UID 10001, group information including GID 20001 where configured, and `/data/proof.txt` listing. Exact ownership and mode are driver/filesystem-dependent.
- **Cleanup:** Remove only `fsgroup-check` and `fsgroup-data` after capturing evidence.
- **Re-run safety:** Inspect the existing claim and file first; do not reuse data you need.
- **Stretch:** Compare `fsGroupChangePolicy: OnRootMismatch` with the default behavior on a disposable volume, documenting the observed cost and behavior.
- **Kind caveat:** Local-path provisioners and CSI drivers may handle group ownership differently.

#### Lab D — PVC stuck `Terminating`: finalizer reasoning

- **Goal:** Learn to diagnose a deletion that is waiting on protection or cleanup without corrupting a resource.
- **Prerequisites:** Lab namespace; read-only `kubectl` access; negligible incremental disk.
- **Steps:** On a healthy disposable PVC, inspect `metadata.finalizers`, Pods that reference it, `kubectl describe pvc`, and Events. Observe normal deletion protection by ensuring the claim is referenced by a Pod, then remove the Pod only after checking the exact names and data-safety status; inspect the claim lifecycle afterward. If the behavior does not reliably remain `Terminating`, do not force a failure. The finalizer-removal portion is conceptual.
- **Expected evidence:** PVC YAML before/after, Pod references, Events and a short explanation of the protection condition.
- **Cleanup:** Delete only named lab objects after confirming they are disposable; verify no Pod/PVC remains.
- **Re-run safety:** This is a read-only diagnostic exercise except for deletion of the explicitly disposable Pod/claim.
- **Stretch:** Build a decision tree for PVCs that remain `Terminating` after all Pod references disappear.
- **Kind caveat:** A deliberately stuck finalizer is not reliably reproduced without introducing unsafe controller/backend faults.

#### Lab E — optional local PV and node affinity boundary

- **Goal:** Understand how a local PV binds a workload to a node.
- **Prerequisites:** disposable multi-node kind cluster; 50–200 MiB estimated; exact node names and paths discovered first.
- **Steps:** Create a local PV only after reviewing `nodeAffinity` and the actual node path; write a marker; inspect Pod placement and PV affinity. Do not delete or simulate loss of a node that holds valuable data.
- **Expected evidence:** PV node affinity and Pod node assignment.
- **Cleanup:** Remove only disposable resources and inspect the node path before any removal.
- **Re-run safety:** Use a fresh unique path or confirm the old path contains only lab data.
- **Stretch:** Explain the difference between a node being unavailable and its disk being destroyed.
- **Kind caveat:** Node labels and node containers simulate scheduling constraints, not independent physical failure domains.

#### Environment guards and cleanup

Before each lab, run:

```bash
set -euo pipefail
kubectl config current-context
kind get clusters
kubectl get nodes -o wide
df -h .
```

Confirm the context is the intended disposable `kind-...` context and verify the namespace and exact names before destructive actions. A client-side dry-run validates client-side structure only; it does not prove admission, provisioning, mount, or application success.

> **⚠ DESTRUCTIVE — DATA LOSS:** The following cleanup deletes the named lab namespace, its Pods, PVCs, and namespaced data. Depending on reclaim policy/provisioner, backing storage may also be deleted or retained. Confirm the context and inspect all lab resources first.

```bash
kubectl config current-context
kubectl get all,pvc -n m05-pv-pvc-lab
kubectl get pv -o wide
# Run only after confirming this namespace contains disposable lab resources:
kubectl delete namespace m05-pv-pvc-lab
kubectl get namespace m05-pv-pvc-lab
kubectl get pv -o wide
```

If the namespace remains terminating, diagnose references/finalizers; do not force-delete it by default. Inspect for retained PVs and backend leftovers. Check free disk with `df -h .` and, on WSL2, check host/virtual-disk use separately because deleting files inside a virtual disk may not shrink the host file automatically.

### 1.11 Self-check questions

1. **A Pod is deleted but its PVC remains Bound. What should you expect?**  
   **Answer:** A replacement Pod can mount the same claim and see existing data if the backend and mount succeed. The tempting wrong answer is “the Pod owns the data”; PVC-backed bytes are separate from the Pod lifecycle.

2. **Does RWO guarantee exactly one Pod can ever access a volume?**  
   **Answer:** No; its scope is node-oriented and actual behavior depends on driver/backend and Kubernetes version. It is not application locking.

3. **What is the practical difference between `Retain` and `Delete`?**  
   **Answer:** They control reclaim behavior after claim release. `Retain` preserves a resource for controlled handling; `Delete` may delete the backing resource. Neither is a backup.

4. **Why can a PVC remain Pending even if a PV exists?**  
   **Answer:** Capacity, access mode, class, selector, volume mode, topology, or binding constraints may not match; provisioning may also fail. Inspect Events and YAML.

5. **When should `volumeMode: Block` be used?**  
   **Answer:** When the application explicitly consumes a raw block device via `volumeDevices`; it is not a normal directory mount.

6. **A non-root image gets `Permission denied` on `/data`. What do you inspect first?**  
   **Answer:** UID/GID, directory/file owner and mode, Pod security context, volume type, driver `fsGroup` behavior, and Events. Blindly switching to root is an unsafe shortcut.

7. **Why might a PVC be stuck in Terminating?**  
   **Answer:** It may still be in use or a controller/backend cleanup is pending. Inspect references and finalizers before considering any exceptional escalation.

8. **A local PV's node is permanently lost. Is the data definitely destroyed?**  
   **Answer:** Not necessarily; it may be unavailable if the storage survives elsewhere, but node/device loss can destroy it. Establish physical/backend state rather than guessing.

9. **Does an etcd snapshot restore PV file bytes?**  
   **Answer:** No. It restores Kubernetes API state, not the backing storage bytes. A separate backup/recovery plan is required.

10. **What does a 10Gi PVC request guarantee?**  
    **Answer:** It requests capacity for matching/provisioning; it does not guarantee IOPS, throughput, latency, replication, encryption, or backup.

### 1.12 Evidence artifacts

Save the following artifacts yourself; they are not generated automatically by this lesson:

- `evidence/context-and-storageclass.txt`: current context, node list, StorageClass list and provisioner.
- `evidence/lab-a-persistence.yaml`: exact manifest used.
- `evidence/lab-a-before-after.txt`: PVC/PV/Pod status and marker output before and after Pod recreation.
- `evidence/pvc-describe.txt`: `kubectl describe pvc` and relevant Events.
- `evidence/fsgroup-permissions.txt`: `id`, directory mode, UID/GID and proof-file output.
- `evidence/reclaim-policy-before-after.txt`: PV YAML, policy, object states, and backend evidence if actually observable.
- `evidence/audit-pv-pvc.sh` and `evidence/audit-output.txt`: read-only script and captured output.
- `evidence/storage-decision-record.md`: workload choices, trade-offs, risks, assumptions and open verification items.
- `evidence/cleanup-confirmation.txt`: exact resources checked after cleanup and remaining retained resources.
- Do not record a lab as passed if it was not executed; label representative examples as such.

### 1.13 Common interview and design-review questions

1. **How do PV and PVC differ, and why separate them?**  
   **Model answer:** A PV represents cluster storage supply; a PVC is a namespaced consumer request. The abstraction lets workloads request storage without hard-coding backend details, while administrators govern provisioning and lifecycle. Binding is usually one-to-one, but it does not guarantee backend durability or performance.

2. **What is the risk of using `Delete` for a database PVC?**  
   **Model answer:** Deleting the claim can release the PV and trigger deletion of the provisioned backing resource. The exact workflow is provisioner-dependent. Use it only when deletion is intended and backup/recovery is tested; enforce policy and require explicit decommission review for important data.

3. **When would you choose local PVs over network storage?**  
   **Model answer:** Local PVs may offer useful locality and low latency, but couple data availability to a particular node/device. They require node affinity and a credible node-loss/recovery plan. Network storage can improve mobility or shared access but adds backend, network, latency, and cost dependencies.

4. **How do you investigate a mount failure after switching to non-root?**  
   **Model answer:** Capture Pod/PVC/PV YAML and Events; inspect UID/GID, mode, mount path, read-only flags, `fsGroup`, filesystem behavior, and CSI policy. Reproduce with a disposable claim using the same security context. Avoid recursive ownership changes on live data without a reviewed procedure.

5. **Why is a snapshot or etcd backup not enough for disaster recovery?**  
   **Model answer:** A volume snapshot may be crash-consistent, backend-local, and not application-consistent; an etcd snapshot contains API metadata, not PV bytes. A credible plan combines application-aware backup/PITR as needed, independent storage copies, retention/security controls, and tested restores with measured RPO/RTO.

### 1.14 Sources and verification notes

#### Official documentation entry points

The following canonical documentation sources are appropriate references. No live documentation or cluster execution was performed while writing this lesson; verify the exact content for your installed version before relying on version-sensitive behavior.

- Kubernetes documentation, **Volumes**: https://kubernetes.io/docs/concepts/storage/volumes/ — volume sources, lifecycle and mounts.
- Kubernetes documentation, **Persistent Volumes**: https://kubernetes.io/docs/concepts/storage/persistent-volumes/ — PV/PVC binding, access modes, reclaim policy, volume mode, local volumes.
- Kubernetes documentation, **Storage Classes**: https://kubernetes.io/docs/concepts/storage/storage-classes/ — provisioner, default class and volume binding mode.
- Kubernetes documentation, **Configure a Pod to Use a PersistentVolume for Storage**: https://kubernetes.io/docs/tasks/configure-pod-container/configure-persistent-volume-storage/ — practical PVC usage.
- Kubernetes documentation, **Configure a Security Context for a Pod or Container**: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/ — UID/GID and `fsGroup`.
- Kubernetes documentation, **Resource Quotas**: https://kubernetes.io/docs/concepts/policy/resource-quotas/ — storage request quotas.
- Kubernetes documentation, **Limit Range**: https://kubernetes.io/docs/concepts/policy/limit-range/ — configured request bounds.
- Kubernetes documentation, **Debugging Pods**: https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/ — event and Pod troubleshooting.
- kind documentation: https://kind.sigs.k8s.io/docs/user/quick-start/ — cluster setup and runtime notes.
- CSI specification/project: https://github.com/container-storage-interface/spec — CSI service and capability concepts.

#### `[VERIFY]` register

| Claim / area | Why sensitive | How to verify | Blocks execution? |
|---|---|---|---|
| Kubernetes, kind, kubectl and BusyBox versions | Versions were not discovered from the learner's environment | `kubectl version`, `kind version`, inspect image tags/digests and supported Kubernetes releases | Yes, for version-specific conclusions |
| Actual default StorageClass and provisioner | Cluster-specific | `kubectl get sc -o yaml` and provisioner docs | Yes, before PVC lab |
| RWO same-node behavior and RWOP support | Version/driver-specific | Official PV docs, CSI compatibility matrix, driver documentation | Yes, before designing multi-Pod access |
| `Recycle` status | Version-sensitive | Current PV docs/API reference | Yes, before any legacy design |
| CSI `fsGroup` behavior and `fsGroupPolicy` | Driver/filesystem-specific | `kubectl get csidriver -o yaml`; official driver docs | Yes, before assuming ownership changes |
| `subPath` update/security details | Kubernetes-version-specific | Current volumes documentation and security advisories | Yes, if relying on updates or isolation |
| Reclaim policy and backend deletion behavior | Provisioner/backend-specific | StorageClass/PV YAML and driver docs; disposable test | Yes, before deleting claims |
| `hostPath` / local-path backing location | Runtime/provisioner-specific | PV YAML and provisioner documentation; inspect exact node mapping | Yes, before node-path inspection |
| Finalizer behavior and supported recovery | Controller/version/incident-specific | PV/PVC YAML, current API docs, controller/driver runbook | Yes, before finalizer mutation |
| `WaitForFirstConsumer`, selectors and pre-binding | StorageClass/provisioner topology-specific | Current StorageClass/PV docs and installed provisioner behavior | Yes, for topology-dependent design |
| Quota and LimitRange enforcement | Cluster policy/configuration-specific | Inspect namespace policies and test admission in disposable namespace | Yes, before claiming enforcement |
| Encryption-at-rest | Backend/platform-specific | Backend configuration, key-management records and platform evidence | Yes, before security assurance |

#### AI self-audit

This is an **AI self-audit**, not an independent human review, a live cluster test, or a guarantee that every command works unchanged in every environment.

- **Roadmap completeness:** PASS for the required Unit 1 topic groups, four required labs, sections 1.0–1.14, comparison tables, SRE/security lenses, evidence artifacts, and exactly five senior interview questions.
- **Technical authenticity:** OPEN — `[VERIFY]` for version-, driver-, provisioner-, filesystem-, and runtime-specific behavior listed above. No live execution is claimed.
- **Lab safety and reproducibility:** PASS for explicit environment guards, named disposable namespace, warning before destructive cleanup, no guessed host path, read-only audit script, and a non-mutating finalizer diagnosis. Lab B's exact reclaim comparison is conditional on provisioner behavior.
- **Writing and scope boundaries:** PASS for keeping Unit 1 focused and referring to M03/M06/M09/M10/M11/M12/M13 only where relevant.
- **Unresolved `[VERIFY]` areas:** 11 grouped areas are listed in the register. Confirm all applicable items before using these procedures on a real cluster.
- **Adversarial review:** The ten common data-loss/unsafe-operation traps are explicitly listed in Section 1.6 and addressed throughout.
- **Execution status:** The lab procedures still require execution on the learner's own disposable `kind` cluster. No repository file has been edited by this lesson.
