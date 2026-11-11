# Unit 3 — Volume snapshots, cloning, expansion

This lesson teaches snapshot, restore, clone, and volume-expansion workflows for Kubernetes stateful workloads. It separates Kubernetes API objects from CSI (Container Storage Interface) controller behavior and backend storage semantics. All labs are designed for disposable local resources. The CSI hostpath driver is a test/teaching driver, not production storage; **hostpath-driver snapshots live on the same node disk**, so they do not protect against loss of that node disk or its relevant local failure domain.

**Target file:** `03-volume-snapshots-cloning-and-expansion.md` | **Estimated time:** 10–14 hours | **Prerequisites:** M05 Units 1 and 2; PV/PVC, StorageClass, CSI, Pods, StatefulSets, namespaces, basic SQL and shell skills.

**Core tools:** `kubectl`, `kind`, Bash, `psql` or a small file-based test workload, `df`, optional `lsblk`, official CSI hostpath test/reference driver, external-snapshotter components | **Awareness:** Velero/Kasten-style hooks, application-native backups, volume group snapshots, optional policy engines | **Last reviewed:** 2026-10-28 | **Baseline:** Kubernetes, CSI hostpath driver, snapshot CRDs/controller, external-snapshotter sidecar and PostgreSQL versions must be chosen as a compatible set from official release guidance. Exact versions are **[VERIFY]**. No lab in this document was executed here.

## Unit 3 — Volume snapshots, cloning, expansion

### 3.0 Why this matters in production

Stateful services need a recovery path that has been tested, not merely a collection of storage objects. A snapshot can exist and still be unusable: the backend may be in the same failure domain as the source, the snapshot may represent inconsistent application state, the driver may not support restoration into the intended class, or the restore may complete without the application data being correct. A database outage can become a data-loss incident when teams mistake a successful API operation for a verified recovery point.

Volume expansion has a different but related risk profile. Increasing a PVC request, expanding the underlying volume, and growing the filesystem are distinct operations. They may finish at different times. A claim can appear larger in the API while the filesystem inside a container still reports the old size. Blind restarts, deletion, or forced finalizer removal can turn a recoverable condition into an outage or data-loss event.

This unit builds the operational discipline to:
- create and inspect snapshots, restore into a **new** PVC, and validate the recovered data;
- clone a PVC only where the selected driver/backend supports the workflow;
- expand a claim without attempting an unsupported shrink;
- distinguish crash consistency from application consistency;
- test restores and retain evidence;
- define ownership, access control, retention and failure-domain expectations.

**Core rule:** `VolumeSnapshot.status.readyToUse: true` is useful API evidence, not proof of application consistency, independent backup, or successful recovery. A PVC being `Bound` is not proof that the mounted filesystem has the expected size or that its data is correct.

### 3.1 Learning objectives

By the end of this unit, the learner can:

1. Identify `VolumeSnapshot`, `VolumeSnapshotContent`, and `VolumeSnapshotClass` and explain their relationship. [L1]
2. Explain the external-snapshotter CRDs/controller, CSI snapshotter sidecar, driver, and backend roles. [L1/L2]
3. Create a snapshot and restore it into a new PVC, then validate a known dataset. [L2]
4. Compare snapshot restore and PVC clone workflows, including constraints and driver dependencies. [L2/L3]
5. Increase a PVC request and distinguish controller-side volume expansion from node-side filesystem expansion. [L2]
6. Diagnose `Resizing` and `FileSystemResizePending` using conditions, Events, PVC/PV state, and mounted-filesystem evidence. [L2/L3]
7. Explain crash-consistent versus application-consistent snapshots, multi-volume consistency, and why snapshots are not a complete backup strategy. [L3]
8. Design dry-run-first snapshot lifecycle automation and restore-test automation with bounded waits and auditable cleanup. [L4]
9. Apply least-privilege, retention, ownership, failure-domain, and restore-test controls to stateful storage operations. [L4]

### 3.2 Concept map and vocabulary

```text
Snapshot request:
VolumeSnapshot (namespaced)
        |
        v
snapshot-controller + external-snapshotter sidecar
        |
        v
CSI driver snapshot capability
        |
        v
Backend snapshot  <---- VolumeSnapshotContent (cluster-scoped API representation)
        |
        | restore via PVC dataSource
        v
New PVC ---> PV ---> mounted filesystem/application validation

Clone request:
Source PVC ---> new PVC with dataSource.kind: PersistentVolumeClaim
                     |
                     v
              driver/backend clone path (if supported)

Expansion request:
PVC requested size increases
        |
        v
controller-side volume expansion (if supported)
        |
        v
PV/backend capacity update
        |
        v
node-side filesystem expansion (if required/supported)
        |
        v
df -h / application-level validation
```

The exact controller/sidecar sequence and supported operations depend on the installed Kubernetes version, snapshot CRDs/controller, CSI driver, sidecars, and backend. A plain `kind` cluster does not install the snapshot API stack by default.

#### Glossary

| Term | Meaning in this unit | Operational caveat |
|---|---|---|
| Point-in-time | A representation of data at a particular point or backend-defined boundary | The point may not be application-consistent |
| Source volume | PVC/PV-backed volume being snapshotted or cloned | Protect it from accidental overwrite/deletion |
| Restore target | A new PVC populated from a snapshot | Use a new claim; validate contents before cutover |
| `VolumeSnapshot` | Namespaced request/representation for a snapshot | Object existence does not prove readiness |
| `VolumeSnapshotContent` | Cluster-scoped representation binding a snapshot API object to a backend snapshot | Handle deletion and finalizers carefully |
| `VolumeSnapshotClass` | Cluster-scoped policy/configuration for snapshot operations | Driver-specific parameters and deletion policy require verification |
| Snapshot handle | Driver/backend identifier for a snapshot | May be sensitive operational metadata; do not invent or manually alter it |
| Consistency | Whether the captured data is mutually valid for the application | Crash recovery is not the same as a coordinated application backup |
| Crash recovery | Application recovers as if abruptly stopped at a point in time | Depends on application logs and storage semantics |
| Clone | New volume initialized from a source PVC | Capability and semantics are driver/backend-specific |
| Resize | Increase requested capacity and provisioned capacity | Not a general way to shrink a volume |
| Filesystem resize | Grow filesystem to use expanded block/device capacity | May require node-side work and workload conditions |

#### Snapshot API objects versus components

| Item | Responsibility | What it does not prove |
|---|---|---|
| `VolumeSnapshot` | User-facing namespaced snapshot request/status | Independent backup or app correctness |
| `VolumeSnapshotContent` | Cluster-scoped binding to a snapshot resource/handle | Cross-cluster portability |
| `VolumeSnapshotClass` | Snapshot driver/configuration and deletion policy | That the backend supports all snapshot features |
| Snapshot CRDs | Define snapshot API types | That a controller or CSI driver is installed |
| Snapshot controller | Reconciles snapshot API objects and content relationships | That data is application-consistent |
| CSI external-snapshotter sidecar | Coordinates CSI driver snapshot operations with Kubernetes objects | That every CSI driver supports snapshots |
| CSI driver | Implements driver-specific operations | That snapshots are replicated/offsite |
| Backend | Stores snapshot data/metadata according to its implementation | That a restore has been tested by the application |

**[VERIFY]** Snapshot API group is `snapshot.storage.k8s.io`; exact API versions and compatible external-snapshotter release must be checked against the selected Kubernetes/driver release and installed CRDs.

### 3.3 Level 1 — Beginner

#### What a snapshot is—and is not

A volume snapshot is a driver-implemented point-in-time representation or copy of volume data, according to backend semantics. Some backends may implement incremental or copy-on-write snapshots, but those properties are not universal and must not be assumed.

A snapshot is **not automatically**:
- an independent backup;
- application-consistent;
- portable to another CSI driver, cluster, region, or backend;
- protected from deletion by the same identity that can delete the source;
- safe against loss of the source's local failure domain;
- evidence that the application can restore successfully.

#### Snapshot creation and restoration flow

1. Confirm the source PVC is backed by a driver that supports snapshots.
2. Ensure the snapshot CRDs/controller and compatible external-snapshotter components are installed.
3. Create a `VolumeSnapshot` in the same namespace as the source PVC (for a normal dynamically created snapshot).
4. The snapshot controller and CSI sidecar coordinate with the driver; the driver asks the backend to create the snapshot.
5. Inspect `status.readyToUse`, bound content reference, Events, and controller/driver logs.
6. Create a **new** PVC whose `dataSource` references the `VolumeSnapshot`.
7. Wait for provisioning/binding, mount the new PVC in an isolated workload, and validate expected data.

The API objects represent the workflow; actual bytes and failure-domain semantics belong to the driver/backend. Restore may be delayed or fail if the target class, size, topology, driver, or snapshot handle is incompatible.

#### Minimal object shapes

**File: `snapshot-class-template.yaml` — illustrative template only.** Replace the provisioner placeholder with the exact documented driver name. Use only parameters documented for that driver.

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: m05-hostpath-snapshots
driver: "<DOCUMENTED_CSI_DRIVER_NAME>"
deletionPolicy: Delete
parameters: {}
```

This template is not directly runnable until the API version, CRDs, driver name and parameters are verified. `Delete` can permit deletion of the underlying snapshot when the corresponding API objects are deleted, subject to controller/driver semantics. Use `Retain` when the intended lifecycle requires retaining the backend snapshot after Kubernetes snapshot object deletion, but verify the selected stack's exact behavior.

**File: `snapshot-request-template.yaml` — snapshot of a disposable source claim.**

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: m05-example-snapshot
  namespace: m05-storage-lab
spec:
  volumeSnapshotClassName: m05-hostpath-snapshots
  source:
    persistentVolumeClaimName: m05-source
```

**File: `restore-pvc-template.yaml` — restore to a new PVC, never overwrite the source.**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: m05-restored
  namespace: m05-storage-lab
spec:
  storageClassName: "<DOCUMENTED_RESTORE_STORAGE_CLASS>"
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 256Mi
  dataSource:
    name: m05-example-snapshot
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
```

The target size and class must satisfy the source snapshot and driver/backend constraints. Use the actual source size and documented restore requirements rather than blindly copying `256Mi`.

#### Snapshot readiness

Inspect the object, not just its existence:

```bash
kubectl get volumesnapshot -n m05-storage-lab
kubectl describe volumesnapshot m05-example-snapshot -n m05-storage-lab
kubectl get volumesnapshotcontent
kubectl get events -n m05-storage-lab
```

**Expected output (representative; not executed here):** a completed snapshot may show `readyToUse: true` and a bound `VolumeSnapshotContent`. Pending or failed states may include Events describing unsupported snapshot operations, missing classes, permission failures, or backend errors. Exact conditions/messages are version- and driver-dependent.

`readyToUse` means the snapshot controller reports it ready for use under the API's semantics. It does not verify SQL queries, filesystem integrity, transaction correctness, or independent failure-domain protection.

#### Expansion mental model

A PVC's requested capacity is expressed in `spec.resources.requests.storage`. Expansion typically requires:
- a StorageClass with `allowVolumeExpansion: true`;
- a driver/backend that supports the requested volume expansion;
- Kubernetes/CSI controller support to expand the underlying volume;
- node-side/filesystem support to grow the mounted filesystem, where required.

Increasing the request is not proof that the filesystem has grown. Do not attempt to shrink a PVC as if resize were reversible. If a smaller volume is required, create a smaller target and migrate/copy application data through a separate validated process.

### 3.4 Level 2 — Intermediate

#### Prerequisites for the local snapshot lab

The official Kubernetes CSI hostpath driver is a teaching/reference driver, not production storage. Its snapshots live on the same node disk. They therefore do not protect against loss of that node disk or the relevant local failure domain.

Official project entry point: `https://github.com/kubernetes-csi/csi-driver-host-path`. External snapshotter documentation: `https://kubernetes-csi.github.io/docs/`. **[VERIFY]** Select a driver release, snapshotter release, CRD bundle, Kubernetes version, and sidecar combination using official compatibility guidance. Do not use a guessed Git tag or unverified `latest` URL.

Before installing:
```bash
set -euo pipefail
kubectl config current-context
kind get clusters
kubectl get nodes -o wide
df -h .
kubectl get storageclass
kubectl get crd
```

Read the selected driver's README and release notes, inspect its exact install manifests, and verify how the external-snapshotter CRDs/controller are installed. Snapshot CRDs and controller are not included by default in a plain kind cluster. Avoid running multiple storage stacks simultaneously on a 4-core/8-GB/30-GB laptop.

#### Lab workload choice

The labs below use a tiny file-backed dataset to keep resource usage low and make byte-level validation deterministic. A PostgreSQL variation is discussed after the core flow. This avoids treating a live database's filesystem snapshot as an application-consistent backup.

**File: `lab-workload.yaml` — small disposable source PVC and writer Pod.** Resolve the class placeholder from the verified CSI hostpath installation. The class must support dynamic provisioning and mounting in this selected release.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: m05-storage-lab
  labels:
    app.kubernetes.io/part-of: m05-storage-lab
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: m05-source
  namespace: m05-storage-lab
spec:
  storageClassName: "<DOCUMENTED_HOSTPATH_STORAGE_CLASS>"
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 256Mi
---
apiVersion: v1
kind: Pod
metadata:
  name: m05-source-writer
  namespace: m05-storage-lab
spec:
  restartPolicy: Never
  containers:
    - name: writer
      image: busybox:1.36
      command: ["/bin/sh", "-c", "printf 'recovery-marker-v1\\n' > /data/marker.txt; printf 'dataset-row-001\\n' > /data/records.txt; sha256sum /data/marker.txt /data/records.txt; sleep 3600"]
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
        runAsUser: 1000
        runAsGroup: 1000
        allowPrivilegeEscalation: false
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: m05-source
```

If the selected hostpath driver or filesystem permissions reject UID 1000, inspect events and driver docs; do not fix it by making the container privileged. Use a documented security context compatible with the driver.

#### Lab 1 — Snapshot → destructive data change → restore → integrity verification

- **Goal:** prove a new restore target contains the known pre-change dataset.
- **Duration:** 45–90 minutes after compatible driver/snapshot stack is installed.
- **Disk footprint:** source/restore claims request 256 MiB each, plus snapshots and images; allow roughly 0.5–1.5 GiB incremental as a planning estimate **[VERIFY]**. Check actual disk.
- **Context guard:** `kubectl config current-context`, `kind get clusters`, `kubectl get nodes -o wide`, `df -h .`; confirm the dedicated disposable cluster and namespace.
- **Architecture:** source PVC `m05-source`; snapshot `m05-snapshot-v1`; restored PVC `m05-restored`; separate reader Pod.

Apply the workload after replacing the StorageClass placeholder. Validate source data:

```bash
kubectl apply --dry-run=client -f lab-workload.yaml
kubectl apply -f lab-workload.yaml
kubectl wait --for=condition=Ready pod/m05-source-writer -n m05-storage-lab --timeout=180s
kubectl exec -n m05-storage-lab m05-source-writer -- sh -c 'cat /data/marker.txt /data/records.txt; sha256sum /data/marker.txt /data/records.txt'
kubectl get pvc,pod -n m05-storage-lab -o wide
```

**File: `lab1-snapshot.yaml` — snapshot request.** Replace class name only after verifying the selected driver and snapshot API installation.

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: m05-snapshot-v1
  namespace: m05-storage-lab
spec:
  volumeSnapshotClassName: m05-hostpath-snapshots
  source:
    persistentVolumeClaimName: m05-source
```

Before applying, verify the class's driver identity and deletion policy:
```bash
kubectl get volumesnapshotclass m05-hostpath-snapshots -o yaml
kubectl apply --dry-run=client -f lab1-snapshot.yaml
kubectl apply -f lab1-snapshot.yaml
kubectl describe volumesnapshot m05-snapshot-v1 -n m05-storage-lab
kubectl get volumesnapshotcontent
```

Use a bounded wait by polling the API rather than assuming an unverified condition name. For example:
```bash
# Polls for readyToUse=true for at most about 3 minutes; requires jq.
set -euo pipefail
deadline=$((SECONDS + 180))
while (( SECONDS < deadline )); do
  ready="$(kubectl get volumesnapshot m05-snapshot-v1 -n m05-storage-lab -o json |
    jq -r '.status.readyToUse // false')"
  [[ "$ready" == "true" ]] && break
  sleep 3
done
[[ "$(kubectl get volumesnapshot m05-snapshot-v1 -n m05-storage-lab -o json | jq -r '.status.readyToUse // false')" == "true" ]] || {
  kubectl describe volumesnapshot m05-snapshot-v1 -n m05-storage-lab
  kubectl get events -n m05-storage-lab
  exit 1
}
```

Capture evidence before changing source data:
```bash
kubectl get pvc m05-source -n m05-storage-lab -o yaml > source-pvc-before.yaml
kubectl get volumesnapshot m05-snapshot-v1 -n m05-storage-lab -o yaml > snapshot-before-change.yaml
kubectl exec -n m05-storage-lab m05-source-writer -- sh -c 'sha256sum /data/marker.txt /data/records.txt' > source-checksums-before.txt
```

> **DATA-SAFETY PREFACE — THROWAWAY LAB ONLY:** The next command intentionally changes data on the disposable source PVC. Confirm the current context, namespace, Pod and claim names, and that the data is not valuable. Capture the snapshot and checksums first. Never run this against a real workload.

```bash
kubectl config current-context
kubectl exec -n m05-storage-lab m05-source-writer -- sh -c \
  'printf "destructive-change-after-snapshot\n" > /data/marker.txt; rm -f /data/records.txt; sync'
kubectl exec -n m05-storage-lab m05-source-writer -- sh -c 'ls -l /data; cat /data/marker.txt'
```

Restore to a **new PVC**, not the source.

**File: `lab1-restore-pvc.yaml` — new target from the snapshot.**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: m05-restored
  namespace: m05-storage-lab
spec:
  storageClassName: "<DOCUMENTED_HOSTPATH_STORAGE_CLASS>"
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 256Mi
  dataSource:
    name: m05-snapshot-v1
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
```

**File: `lab1-restore-reader.yaml` — read-only validation Pod.**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: m05-restore-reader
  namespace: m05-storage-lab
spec:
  restartPolicy: Never
  containers:
    - name: reader
      image: busybox:1.36
      command: ["/bin/sh", "-c", "cat /data/marker.txt /data/records.txt; sha256sum /data/marker.txt /data/records.txt; sleep 3600"]
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
        runAsUser: 1000
        runAsGroup: 1000
        allowPrivilegeEscalation: false
      volumeMounts:
        - name: data
          mountPath: /data
          readOnly: true
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: m05-restored
```

Apply and verify:
```bash
kubectl apply --dry-run=client -f lab1-restore-pvc.yaml
kubectl apply -f lab1-restore-pvc.yaml
kubectl get pvc m05-restored -n m05-storage-lab -o wide
kubectl describe pvc m05-restored -n m05-storage-lab
kubectl apply --dry-run=client -f lab1-restore-reader.yaml
kubectl apply -f lab1-restore-reader.yaml
kubectl wait --for=condition=Ready pod/m05-restore-reader -n m05-storage-lab --timeout=180s
kubectl logs m05-restore-reader -n m05-storage-lab
```

**Success criteria:** restored output includes `recovery-marker-v1` and `dataset-row-001`, while source data shows the destructive change and missing `records.txt`. Compare restored checksums to `source-checksums-before.txt`. **Expected output (representative; not executed here):** the restored claim should show the snapshot's earlier data if the selected driver supports this workflow correctly. If it does not, stop and inspect PVC/snapshot Events, `VolumeSnapshotContent`, controller logs and driver capability docs; do not delete source resources to “retry.”

**What this proves:** data returned to a new PVC from a snapshot within this test setup. It does not prove application consistency, off-node durability, offsite backup, cross-cluster portability or production recovery. Hostpath-driver snapshots live on the same node disk.

**PostgreSQL variation:** if using PostgreSQL, seed a tiny table and record row counts/checksums, but do not call a filesystem snapshot of a running database application-consistent. PostgreSQL may recover from a crash-consistent storage point if its data/WAL and storage semantics are coherent; this must be validated with the exact PostgreSQL and driver setup. Prefer a database-native logical/physical backup for production recovery tests.

#### Lab 2 — PVC clone for a test environment

- **Goal:** create an isolated PVC initialized from a source PVC.
- **Duration:** 30–60 minutes; **disk:** two 256 MiB claims plus backend clone/snapshot overhead; budget roughly 0.5–1.5 GiB and verify.
- **Prerequisites:** selected CSI driver supports PVC cloning; compatible class and target size confirmed in official documentation.
- **Context guard:** verify context, namespace and disk. Use only `m05-storage-lab`.

Create a source PVC with a known dataset (Lab 1's source can be reused only if you intentionally reset it and understand its current contents). For a clean source, create a fresh claim and writer Pod using the same shape as `lab-workload.yaml` but with claim name `m05-clone-source`.

**File: `lab2-clone-pvc.yaml` — target claim cloned from source.**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: m05-clone-target
  namespace: m05-storage-lab
spec:
  storageClassName: "<SAME_DOCUMENTED_STORAGE_CLASS>"
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 256Mi
  dataSource:
    name: m05-clone-source
    kind: PersistentVolumeClaim
```

The source PVC must exist and be in the same namespace for the ordinary PVC clone workflow described here. The parent syllabus expects the same StorageClass and target size at least as large as the source; exact constraints can vary by Kubernetes and driver versions, so verify them. Do not infer clone support from snapshot support.

Mount the clone in a separate Pod, read its marker/checksum, then write a unique marker to the clone and confirm the source marker remains unchanged. Only claim isolation after that test passes. Backend copy-on-write, instantaneous behavior, space savings, and physical independence are driver/backend-specific.

**Expected output (representative; not executed here):** the clone target becomes `Bound`, the cloned dataset matches the source, and a write to the clone does not alter the source. If the clone remains Pending or provisioning fails, inspect PVC Events, class/driver support, source/target class and size, and controller logs.

#### Lab 3 — PVC online expansion with filesystem-resize proof

- **Goal:** increase a disposable claim and prove the filesystem-visible size changed.
- **Duration:** 30–60 minutes; **disk:** request a small size such as 128 MiB and expand to 256 MiB; incremental backend use is driver-dependent.
- **Prerequisites:** a class with `allowVolumeExpansion: true` and verified driver/backend/filesystem expansion support.
- **Context guard:** verify context, disk, class YAML and that this is a disposable claim. Never test shrink.

Inspect the class first:
```bash
kubectl get sc <VERIFIED_EXPANDABLE_CLASS> -o yaml
kubectl describe sc <VERIFIED_EXPANDABLE_CLASS>
kubectl explain persistentvolumeclaim.spec.resources.requests
```

Create a small PVC and Pod with known data. Inside the mounted container, collect:
```bash
df -h /data
lsblk
```
`lsblk` may not exist in a minimal image or be meaningful inside a container; use a suitable diagnostic image or node-level inspection only where safe. `df -h` shows filesystem-visible capacity, not necessarily backend physical consumption.

Increase the request only:

```bash
kubectl patch pvc m05-expand-data -n m05-storage-lab \
  --type merge \
  -p '{"spec":{"resources":{"requests":{"storage":"256Mi"}}}}'
kubectl get pvc m05-expand-data -n m05-storage-lab -o yaml
kubectl describe pvc m05-expand-data -n m05-storage-lab
kubectl get pv -o wide
kubectl get events -n m05-storage-lab
```

Use a bounded wait, then inspect conditions and filesystem size. A generic poll can check the PVC request/capacity but does not prove filesystem expansion:

```bash
set -euo pipefail
deadline=$((SECONDS + 180))
while (( SECONDS < deadline )); do
  kubectl get pvc m05-expand-data -n m05-storage-lab -o wide
  phase="$(kubectl get pvc m05-expand-data -n m05-storage-lab -o jsonpath='{.status.phase}')"
  [[ "$phase" == "Bound" ]] || true
  sleep 5
  # Exit the loop only after separately confirming status.capacity is >= the new request.
  capacity="$(kubectl get pvc m05-expand-data -n m05-storage-lab -o jsonpath='{.status.capacity.storage}')"
  [[ "$capacity" == "256Mi" ]] && break
done
kubectl describe pvc m05-expand-data -n m05-storage-lab
```

The capacity string comparison above is suitable only for this illustrative `256Mi` example; use quantity-aware comparison for a reusable script. If the filesystem still reports the old size, inspect `Resizing`/`FileSystemResizePending`, PVC Events, driver/controller/node-plugin logs, filesystem type, mount state and documented online/offline support. Do not blindly restart or delete the Pod. Some driver/filesystem combinations require a controlled remount or workload restart, but only follow the documented procedure for the selected version.

**Expected output (representative; not executed here):** the PVC request and PV capacity may update before the filesystem reports the larger size. Completion requires `df -h /data` in the mounted workload to show the expected increased filesystem capacity, plus preserved test data.

#### Lab 4 — StatefulSet volume expansion on throwaway data

- **Goal:** observe how `volumeClaimTemplates` and already-created PVCs interact with expansion.
- **Duration:** 60–120 minutes; **disk:** one small PVC, typically 128–256 MiB requested, plus images.
- **Prerequisites:** disposable kind cluster, verified expandable class, and current official StatefulSet documentation.
- **Context guard:** record context, StatefulSet name, generated PVC name, data marker and current replicas. This lab must never use valuable data.

**File: `lab4-statefulset.yaml` — disposable StatefulSet with a claim template.**

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: m05-expand-demo
  namespace: m05-storage-lab
spec:
  serviceName: m05-expand-demo
  replicas: 1
  selector:
    matchLabels:
      app: m05-expand-demo
  template:
    metadata:
      labels:
        app: m05-expand-demo
    spec:
      containers:
        - name: writer
          image: busybox:1.36
          command: ["/bin/sh", "-c", "printf 'statefulset-marker-v1\\n' > /data/marker.txt; sleep 3600"]
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
            runAsUser: 1000
            runAsGroup: 1000
            allowPrivilegeEscalation: false
          volumeMounts:
            - name: data
              mountPath: /data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        storageClassName: "<VERIFIED_EXPANDABLE_CLASS>"
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 128Mi
```

The generated PVC name normally includes the claim-template name, StatefulSet name and ordinal; inspect actual resources rather than hardcoding assumptions:
```bash
kubectl get sts,pod,pvc -n m05-storage-lab -o wide
kubectl get pvc -n m05-storage-lab -o yaml
kubectl exec -n m05-storage-lab <DISCOVERED_POD> -- cat /data/marker.txt
```

Updating the template does not necessarily resize existing PVCs. Existing claims are separate objects. The parent syllabus calls for a manual PVC patch plus StatefulSet recreate-with-orphan-cascade workaround, but exact behavior and safe commands are **[VERIFY]** for the selected Kubernetes version and current StatefulSet state. Do not run a remembered command sequence blindly. Check the current official StatefulSet documentation and Kubernetes behavior for orphan deletion/cascade semantics first.

> **DATA-SAFETY PREFACE — THROWAWAY LAB ONLY:** The following operation can disrupt the StatefulSet controller and may affect workload availability. Confirm the namespace contains only disposable lab data, capture the StatefulSet/PVC YAML and marker contents, and verify the exact documented procedure for the selected Kubernetes version. Do not run against a real StatefulSet.

If and only if official documentation confirms the selected workaround, use a reviewed sequence that:
1. records the original StatefulSet manifest, replicas, generated PVC names, current claim sizes and data marker;
2. patches the **specific** generated PVC request upward;
3. uses the documented orphaning/recreation procedure to update the StatefulSet template without deleting the PVCs;
4. verifies the StatefulSet returns Ready and the original PVC remains bound;
5. verifies filesystem-visible size and marker data;
6. aborts if the controller operation would delete PVCs or the selected class does not support expansion.

This lesson intentionally does not supply an unverified orphan-cascade command as a universal recipe. If the current documented behavior differs, follow the supported alternative and record `[VERIFY]` rather than guessing. Deleting a StatefulSet controller is not the same as deleting its PVCs, but a mistaken cascade policy or selector can still disrupt the workload. **Expected output (representative; not executed here):** the PVC capacity and filesystem size grow while the marker remains readable, provided the class, driver, filesystem and procedure support the operation.

#### Required reflection — “Snapshot is not a backup”

Write three distinct failure scenarios the lab snapshot would not survive, and identify a control for each. At minimum address:
1. **Loss of the same node disk/failure domain:** hostpath snapshots live on the same node disk, so a disk loss can destroy both source and snapshot. Control: a backend-independent copy or backup in a separate failure domain.
2. **Loss of relevant cluster/backend control plane or accidental deletion:** depending on architecture, snapshot metadata, backend snapshot or credentials may be lost or inaccessible. Control: documented independent retention, access separation and recovery of required metadata/keys.
3. **Corruption or application-level inconsistency already present at snapshot time:** restoring reproduces the bad state. Control: application-native backup/PITR, integrity checks, and restore tests against known-good recovery points.

Other scenarios may apply depending on architecture. State the assumptions explicitly; do not claim that every failure mode applies to every backend.

### 3.5 Level 3 — Advanced

#### Crash-consistent versus application-consistent snapshots

A **crash-consistent** snapshot resembles storage captured after an abrupt interruption. A database may recover using its transaction logs, but the result depends on write ordering, durable flushes, filesystem semantics, and whether all required data and WAL files are captured coherently.

An **application-consistent** recovery point coordinates the application so its data structures and required logs represent a valid recovery boundary. It may involve database-native backup protocols, checkpoint/quiesce hooks, and coordinated snapshots. It must be validated for the exact application and storage stack.

For PostgreSQL, `CHECKPOINT` can influence writing dirty buffers, but it is not by itself a complete backup protocol. PostgreSQL's backup functions and required procedures are version-sensitive; check the official PostgreSQL documentation before using `pg_backup_start` / `pg_backup_stop`, and follow the correct physical-backup workflow for the installed version. A filesystem snapshot of a running PostgreSQL instance is generally closer to a crash-recovery point than a fully coordinated database backup. It is not a substitute for tested logical/physical backups.

`fsfreeze` can freeze a supported filesystem for a coordinated storage operation, but requires appropriate privileges, correct filesystem scope, and a guaranteed unfreeze path on every error/timeout. It does not automatically coordinate database transactions, multiple filesystems, or multiple volumes. Do not introduce it into production without a reviewed runbook and failure-path tests.

Velero/Kasten-style backup hooks are ecosystem options, not built-in core Kubernetes features and not part of the zero-budget baseline here. Hook correctness, ordering, timeout behavior, permissions and application-specific quiescing must be tested.

#### Multi-volume consistency

Consider a database whose data directory is on one volume and WAL on another. Independent snapshots can represent different points in time. Restoring both does not automatically create a consistent set. Use a coordinated mechanism only where the application, driver, backend and snapshot API support it.

`VolumeGroupSnapshot` is **[VERSION-SENSITIVE]** awareness only here. Do not assume it is available or supported by the selected cluster. Verify current official API/driver support before designing around group snapshots.

#### Snapshot storage location, capacity, retention and failure domain

Snapshot implementations may be full-copy, incremental, copy-on-write or another backend-specific design. Do not generalize about space usage or performance. Determine:
- where snapshot data physically resides;
- whether it shares disks, nodes, accounts, regions or credentials with the source;
- what happens when the source volume is deleted;
- whether retention is independent of the source class or namespace;
- what capacity/quotas are consumed;
- who can delete the snapshot and the underlying backend data;
- how snapshot metadata and encryption keys are recovered;
- whether restore has been tested after a realistic failure.

#### Snapshots vs backups vs replicas vs PITR

| Mechanism | Primary purpose | Typical recovery method | Main failure modes | RPO/RTO reasoning | Limitations |
|---|---|---|---|---|---|
| Volume snapshot | Fast point-in-time storage recovery where backend supports it | Create new volume/PVC from snapshot | Same failure domain, accidental deletion, inconsistent app state, unsupported restore path | Depends on snapshot frequency and restore time; measure it | Not automatically independent or application-consistent |
| Backup | Retained recoverable copy, often independent of source lifecycle | Restore data/application from backup repository or media | Backup corruption, missing keys/catalog, untested procedure, same-account deletion | RPO depends on backup schedule/log capture; RTO includes retrieval and validation | Requires retention, access controls and restore drills |
| Replica | Availability/continuity through a second live or near-live copy | Fail over/promote or redirect workload | Replicated corruption/deletion, lag, split brain, shared failure domain | RPO depends on replication lag; RTO depends on failover | Replication may copy logical errors and is not a historical backup |
| Point-in-time recovery (PITR) | Recover to a time/transaction point using base backup plus logs | Restore base backup and replay logs to target point | Missing/corrupt logs, incompatible base backup, key/catalog loss | RPO can be bounded by log capture; RTO includes replay and validation | Requires complete log chain and application-specific tooling |

RPO (recovery point objective) and RTO (recovery time objective) are service/business requirements, not universal properties of a snapshot product. Define them with workload owners and validate them in timed restore drills.

#### StatefulSet expansion and claim templates

`volumeClaimTemplates` define claims for StatefulSet Pods, but the generated PVCs are independent API objects after creation. Editing a template does not reliably resize existing claims. The correct process is version- and state-sensitive. The parent syllabus asks for a manual PVC patch plus StatefulSet recreate-with-orphan-cascade workaround, but use it only after verifying current official documentation for the exact Kubernetes version and understanding cascade/orphan semantics. Newer behavior or platform-specific tooling may offer alternatives. Mark any unverified sequence `[VERIFY]`; never copy a generic command that risks deleting claims.

#### Filesystem resizing: block device versus filesystem

Expansion has separate layers:
1. PVC request increases.
2. Kubernetes/CSI controller requests backend volume expansion.
3. PV capacity reflects the provisioned volume.
4. Node-side operation expands the device/filesystem where required.
5. The mounted filesystem reports the new capacity.

`df -h` reports filesystem-visible size. `lsblk` can show block-device size where the command and device mapping are available, but it may not be installed inside the container and may not expose host details. Use the right observation point.

ext4 and XFS have different growth and shrink behavior. XFS cannot be shrunk in place in the normal supported filesystem workflow; verify the filesystem and tool documentation for the target system. In general, Kubernetes PVC shrinking is not supported as a reverse resize. If a smaller target is needed, provision a new smaller volume and perform a validated application-aware copy/migration.

#### Diagnosing `Resizing` and `FileSystemResizePending`

When a PVC remains in a resize-related condition:
1. Capture `kubectl describe pvc`, PVC/PV YAML and Events.
2. Compare requested PVC size with PV status capacity.
3. Inspect StorageClass `allowVolumeExpansion` and driver capability documentation.
4. Check controller-side expansion logs and node-plugin logs.
5. Check whether the filesystem has mounted and whether node-side resize is supported online.
6. Inspect Pod scheduling/mount Events and the filesystem size from the workload.
7. Check for unsupported filesystem, insufficient backend capacity, missing permissions, sidecar incompatibility, or a driver bug.
8. Follow the selected driver's documented recovery path; do not blindly restart Pods, delete claims, or force-remove finalizers.

#### Clone versus snapshot restore

| Dimension | PVC clone | Snapshot restore |
|---|---|---|
| Source reference | Source PVC | `VolumeSnapshot` |
| Typical purpose | Create a copy for testing/dev or data workflows | Recover to a captured point in time |
| API path | PVC `dataSource` with kind `PersistentVolumeClaim` | PVC `dataSource` with kind `VolumeSnapshot` |
| Constraints | Driver/backend clone support, namespace/class/size rules | Snapshot API stack, snapshot class/content and restore compatibility |
| Physical implementation | Could be copy, clone, or copy-on-write depending on backend | Could be full, incremental, copy-on-write or another implementation |
| Independence | Must be tested; not guaranteed by API | Must be tested; not guaranteed by API |
| Main safety issue | Test writes/data exposure | Wrong point-in-time, retention/deletion, failure-domain assumptions |

### 3.6 Level 4 — Expert

#### Dry-run-first snapshot lifecycle automation

A production snapshot scheduler needs ownership, retention rules, bounded retries, event/log evidence, and restore-test feedback. It must not delete snapshots simply because they are old if they are the last valid recovery point or subject to legal/retention requirements.

A safe design is:

1. **Inventory:** list eligible PVCs with an explicit opt-in label and approved snapshot class.
2. **Plan:** calculate timestamped snapshot names, intended retention candidates, and expected effects.
3. **Dry-run default:** print the plan; make no API changes.
4. **Apply mode:** require an explicit `--apply` flag, a dedicated ServiceAccount, least-privilege RBAC, and an audit trail.
5. **Create:** create snapshots with deterministic owner/labels and wait with bounded timeout.
6. **Validate:** record ready status and relevant content reference; do not claim application consistency unless hooks and validation prove it.
7. **Prune:** only delete snapshots matching exact ownership labels and policy; preserve a minimum count and any protected/last-known-good point.
8. **Report:** emit success/failure counts, age of last successful snapshot, request-to-ready duration, prune results and diagnostics.

A generic executable pruner is unsafe without a verified snapshot API version, driver deletion semantics, owner labels, and retention policy. The following is **pseudocode/design**, not an executable controller:

```text
load policy and approved namespaces/classes
discover only explicitly opted-in PVCs
compute proposed snapshot names and prune candidates
if --apply absent:
    print plan and exit without mutation
for each approved PVC:
    create snapshot using verified API schema
    wait until ready/failure/timeout
    capture Events and object status
    if snapshot not ready:
        mark failure; preserve source and prior snapshots
for each prune candidate:
    require exact ownership label and age/count policy
    refuse to delete protected/last-good snapshots
    print deletion plan
    delete only with --apply and audit record
emit summary and non-zero exit on any failed required operation
```

RBAC should grant only required verbs on approved namespaces and snapshot resources. Access to cluster-scoped `VolumeSnapshotContent` deserves special care because deletion can affect backend snapshots. Exact verbs/resources depend on the selected API version and controller design; **[VERIFY]** against current RBAC APIs and the actual manifests.

#### Restore-test automation

A restore test is stronger than a snapshot-created test. A robust automation workflow:
- restores into an isolated scratch namespace/claim;
- uses bounded waits for snapshot readiness, PVC binding, Pod readiness and application checks;
- validates a known record count, checksum or application query;
- emits explicit pass/fail evidence with timestamps and object names;
- captures Events and logs on failure;
- deletes only resources it created, and only after successful evidence capture;
- preserves diagnostics and leaves the failed target for investigation when unexpected state is detected;
- reports restore-test success age and time-to-restore.

Do not write a cleanup trap that blindly deletes resources after a failed restore test. A failed test may be the only evidence of a broken recovery path. Cleanup must be scoped to unique lab-generated names and require an explicit opt-in when it could delete data.

#### Incident case: “Snapshots lived in the same failure domain as the volume”

- **Symptoms:** the source volume and snapshots became unavailable after a node-disk failure; the team expected recovery from a snapshot but had no usable copy.
- **Timeline:** snapshots were created successfully; `readyToUse` was treated as durability proof; the local node disk failed; source and snapshot data disappeared together; restore was attempted and failed.
- **Impact:** longer outage, data loss beyond the last independent backup, and missed RTO.
- **Mistaken assumption:** “snapshot exists” meant “backup exists.”
- **Contributing factors:** local hostpath backend, same node disk, no independent copy, no restore drill, unclear ownership and no documented failure-domain map.
- **Detection gaps:** no restore-test SLI, no independent-failure-domain inventory, no alert on age of last successful restore test.
- **Immediate containment:** preserve remaining nodes/disks; stop cleanup/pruning; inventory surviving copies and logs; communicate the known RPO/RTO impact.
- **Recovery options:** restore from an independent backup, replica, or application-native backup/PITR chain if available; otherwise quantify unrecoverable data rather than claiming a snapshot can help.
- **Prevention:** store recovery copies in an independent failure domain, define retention/access separation, test restore, and explicitly label local hostpath snapshots as test-only.

**Required limitation:** hostpath-driver snapshots live on the same node disk and do not protect against loss of that disk.

#### Incident case: expansion stuck in `FileSystemResizePending`

- **Symptoms:** PVC request/PV capacity appears increased but `df -h` inside the workload still reports the old size, or the PVC retains a resize-related condition.
- **Timeline:** request was increased; controller-side expansion progressed; node-side filesystem growth did not complete or was not supported in the current state.
- **Plausible causes:** unsupported online expansion, filesystem/driver limitations, node-plugin failure, missing sidecar compatibility, mount state, capacity/permission issue, or version-specific behavior.
- **Evidence:** PVC/PV YAML and conditions, Events, StorageClass, controller/node logs, Pod state, filesystem type, `df -h`, and `lsblk` where meaningful.
- **Discriminating checks:** did PV capacity change? Does the driver document online filesystem expansion? Is the Pod mounted on a node with a healthy plugin? Does the backend report the larger volume?
- **Safe remediation:** follow the exact driver/filesystem runbook; if a controlled remount or workload restart is documented, schedule it with application owner approval and a rollback/abort plan. Do not blindly restart, delete/recreate PVCs, or remove finalizers.
- **Escalation:** stop if the backend state is ambiguous, data integrity is uncertain, or the operation may detach an active writer.
- **Post-incident actions:** add a filesystem-size validation step, alert on persistent resize conditions, test upgrades in staging and document supported online/offline paths.

#### Guardrails and M13 handoff

- Require approved snapshot classes and lifecycle settings for production workloads.
- Restrict creation/deletion of snapshots and especially `VolumeSnapshotContent` with least-privilege RBAC.
- Use admission policy to validate class names, owner metadata, retention settings and namespace policy where feasible.
- Keep ownership, retention, deprecation and audit logs.
- Separate backup administration from application operation for high-value data.
- Treat snapshots/clones as sensitive copies; apply data masking and credential rotation for test clones.
- Review CSI driver/sidecar provenance and privileges.
- Do not claim encryption-at-rest, immutability or independent retention unless the backend and key-management design guarantee it.

OPA Gatekeeper and Kyverno are optional policy-engine examples; neither is assumed installed. Verify policy syntax/API compatibility before enforcement.

**M13 handoff:** offsite copies, immutability, cross-cluster restoration, key escrow, enterprise backup/DR and comprehensive disaster-recovery testing belong to M13. This local lab does not implement or prove those capabilities.

### 3.7 SRE lens

#### Recovery objectives and measurable signals

RPO is the maximum acceptable amount of data loss; RTO is the maximum acceptable recovery time. Neither is supplied by a snapshot API. Workload owners must define objectives based on business impact, then validate them through drills.

Useful signals include:
- snapshot request-to-ready duration;
- snapshot creation failures;
- age of the last successful snapshot;
- age and result of the last successful restore test;
- restore duration and integrity-check result;
- PVCs stuck in resize-related conditions;
- time between request expansion and filesystem-visible expansion;
- retention-prune success/failure and remaining recovery points;
- application-specific query/checksum results.

Some are custom metrics/design suggestions rather than metrics universally exposed by Kubernetes or a driver. Use object status, Events, sidecar logs, backend telemetry and application checks together.

#### Runbook pattern

1. **Alert:** identify workload, PVC, snapshot, time and requested recovery objective.
2. **Triage:** distinguish snapshot API failure, backend operation failure, restore provisioning failure, filesystem expansion failure, and application validation failure.
3. **Evidence:** save object YAML, Events, controller/sidecar/node logs, backend state and checksums/query output.
4. **Safety gate:** preserve source and existing recovery points; confirm the restore target is new and isolated.
5. **Mitigation:** follow driver/backend/application-specific recovery procedures; do not force-delete objects to clear status.
6. **Validation:** mount target and run application integrity checks; record elapsed time and data point recovered.
7. **Follow-up:** review failure domain, retention, access controls, RPO/RTO and whether automation should be changed.

A snapshot success alert is not a restore-success alert. Capacity planning must account for backend snapshot retention, clone/restore targets, temporary recovery copies, and possible copy-on-write behavior. Never assume snapshots are free or incremental.

### 3.8 Security lens

- **Least privilege:** scope who can create/delete `VolumeSnapshot` and `VolumeSnapshotContent`; the latter is cluster-scoped and can affect backend snapshot lifecycle.
- **Data sensitivity:** snapshots and clones can reproduce credentials, tokens, PII and production records. Use masking/synthetic data for test environments.
- **Tenant boundaries:** namespace boundaries do not alone protect a shared backend or cluster-scoped content objects.
- **Secrets:** restored database data may contain credentials and secrets. Rotate/revoke test credentials when required; never store real credentials in lab manifests.
- **Encryption and keys:** encryption-at-rest, key retention and recovery are backend/key-management concerns. A snapshot may depend on access to the original key or key service; verify before disaster recovery.
- **Deletion/retention:** protect last-known-good recovery points, audit deletions, and separate duties for high-value workloads.
- **Driver/controller trust:** inspect image provenance, service accounts, RBAC, host access and compatibility. Snapshot sidecars and CSI components are part of the storage control plane.
- **Policy:** admission controls may restrict approved classes and deletion policies, but policy-engine availability and syntax are version-sensitive.
- **Clone exposure:** cloned test volumes should be isolated, access-controlled and masked before broader developer access.

Useful read-only checks:

```bash
kubectl get volumesnapshotclass -o yaml
kubectl get volumesnapshot -A -o yaml
kubectl get volumesnapshotcontent -o yaml
kubectl get csidriver -o yaml
kubectl get serviceaccounts,roles,rolebindings -A
kubectl get clusterroles,clusterrolebindings
kubectl auth can-i delete volumesnapshots.snapshot.storage.k8s.io -n m05-storage-lab
kubectl auth can-i delete volumesnapshotcontents.snapshot.storage.k8s.io
```

These checks are evidence, not a complete security audit. Do not paste unredacted sensitive object output into tickets or artifacts.

### 3.9 Production checklist

**Before the change**
- [ ] Source PVC, PV, StorageClass, driver and backend are identified.
- [ ] Snapshot CRDs/controller and external-snapshotter compatibility are verified.
- [ ] Driver snapshot/clone/expansion capabilities are documented for the exact version.
- [ ] The intended consistency level is stated and appropriate for the application.
- [ ] The snapshot failure domain is independent enough for the required risk; local hostpath is explicitly not production backup.
- [ ] Restore target uses a new PVC and the correct class/size.
- [ ] Deletion policy, retention and ownership are reviewed.
- [ ] Available disk/backend capacity and temporary restore capacity are checked.
- [ ] Application owner, change window, abort conditions and recovery path are known.

**During execution**
- [ ] Capture source data checksums or application-level baseline.
- [ ] Use bounded waits and collect Events/logs on failure.
- [ ] Verify snapshot readiness and content binding.
- [ ] Avoid destructive source changes until evidence is captured.
- [ ] For expansion, distinguish PVC request, PV/backend capacity and filesystem size.
- [ ] Do not attempt PVC shrink or use blind restart/delete shortcuts.

**After execution**
- [ ] Restore/clone is mounted in isolation and application data is validated.
- [ ] `df -h` or equivalent proves filesystem-visible expansion.
- [ ] Restore duration, recovered point and validation result are recorded.
- [ ] Cleanup is limited to named lab resources and its deletion effects are understood.
- [ ] Snapshot/restore-test metrics and last-success timestamp are updated.
- [ ] Backup/DR requirements are handed to M13; snapshot existence is not treated as a backup test.

### 3.10 Hands-on lab set

#### Universal lab safety

> **DATA-SAFETY PREFACE — THROWAWAY LAB ONLY:** Any command below that changes data, deletes a resource, prunes snapshots, or alters a controller must be run only against a disposable `kind` cluster and the explicitly named `m05-storage-lab` resources. Confirm `kubectl config current-context`, namespace contents, resource names, driver ownership, and available disk. Capture evidence first. Never run these sequences against production or valuable data.

Check disk before and after each lab:
```bash
kubectl config current-context
kind get clusters
kubectl get nodes -o wide
df -h .
```

The CSI hostpath driver and external-snapshotter installation steps are intentionally release-selected rather than hardcoded: inspect the official project docs, compatibility matrix and exact manifests first. Disk estimates below are planning ranges, not measured values. Every output is representative and not executed here.

**Lab 1 — Snapshot → destructive data change → restore → integrity verification**  
Detailed manifests and commands are in Section 3.4. Evidence: source checksums, snapshot YAML/status, `VolumeSnapshotContent`, destructive-change proof, restored claim state and restored checksums. Cleanup must preserve evidence first and delete only the named lab namespace/resources. Expected incremental disk footprint: roughly 0.5–1.5 GiB, backend-dependent. Failure branches: class missing, snapshot CRDs absent, `readyToUse` false, restore claim Pending, or checksum mismatch. On checksum mismatch, stop and preserve objects/logs; do not retry by deleting the source.

**Lab 2 — PVC clone for a test environment**  
Create a source PVC and write a deterministic marker; create `m05-clone-target` with `dataSource.kind: PersistentVolumeClaim`; mount it in a separate Pod; compare source and clone checksums; write a different marker only to the clone and prove the source is unchanged. Verify same-namespace, class and target-size constraints against the selected driver/version. Expected incremental disk footprint: roughly 0.5–1.5 GiB. Cleanup: delete only the test Pods and claims after evidence capture; inspect reclaim behavior. If clone support is absent, mark the capability unsupported for this driver and do not substitute snapshot restore while claiming the clone lab passed.

**Lab 3 — PVC online expansion with filesystem-resize proof**  
Create a 128 MiB disposable PVC with a verified expandable class; write a known marker; record `df -h /data`; patch the claim request upward to 256 MiB; watch PVC/PV YAML, conditions, Events and driver logs; then record `df -h /data` again. Success requires both capacity status and filesystem-visible size increase while marker data remains intact. Expansion can require controller and node operations; online behavior is driver/filesystem-specific. Use bounded waits. If `FileSystemResizePending` persists, follow Section 3.5 diagnosis and do not blindly restart/delete. Cleanup may remove the disposable claim and its backing data.

**Lab 4 — StatefulSet volume expansion on throwaway data**  
Create the StatefulSet in Section 3.4, record the actual generated PVC name and marker, and verify current official StatefulSet behavior before attempting any template workaround. The manual PVC patch plus recreate-with-orphan-cascade procedure is **[VERIFY]** and must only be attempted after confirming the selected Kubernetes version's documented semantics. If the behavior is unclear, do not perform the controller deletion; use the safest documented alternative and document the limitation. Validate marker data, PVC capacity and filesystem size afterward. Cleanup must explicitly distinguish controller deletion from PVC deletion and must not use broad wildcards.

**Required reflection — “Snapshot is not a backup”**  
Submit three failure scenarios not survived by the lab snapshot and the additional control for each. Include same-node-disk loss, relevant cluster/backend control-plane loss or accidental deletion where applicable, and corruption/application inconsistency already present at snapshot time. Qualify each by architecture.

### 3.11 Self-check questions

1. **What are `VolumeSnapshot`, `VolumeSnapshotContent`, and `VolumeSnapshotClass`?**  
   **Answer:** The namespaced request/status, cluster-scoped backend-content binding, and class/policy for snapshot operations. They are not interchangeable. **Tempting error:** assuming the API object itself contains the volume bytes.

2. **Does `readyToUse: true` prove a database can recover?**  
   **Answer:** No; it reports API-level snapshot readiness. Application validation and restore testing are still required. **Tempting error:** treating controller status as a database integrity test.

3. **What is the difference between `Delete` and `Retain` in a snapshot class?**  
   **Answer:** They govern intended lifecycle of the underlying snapshot when API objects are deleted, subject to controller/driver behavior. Verify exact semantics. **Tempting error:** assuming deletion always removes or always preserves backend data.

4. **When would you choose clone versus snapshot restore?**  
   **Answer:** A clone creates a target from a source PVC where supported; snapshot restore recreates a target from a point-in-time snapshot. Constraints and physical implementation vary. **Tempting error:** assuming either is universally supported or copy-on-write.

5. **Why can a PVC show a larger capacity while `df -h` remains unchanged?**  
   **Answer:** Controller/backend expansion and node-side filesystem growth are separate steps. **Tempting error:** assuming PV capacity alone proves filesystem growth.

6. **Crash-consistent versus application-consistent: what is the difference?**  
   **Answer:** Crash-consistent storage may require application crash recovery; application-consistent capture coordinates the application to a valid recovery boundary. **Tempting error:** calling any snapshot of a running database application-consistent.

7. **Why doesn't changing `volumeClaimTemplates` necessarily resize an existing StatefulSet PVC?**  
   **Answer:** Existing PVCs are independent objects created from the template; update behavior is version-sensitive. **Tempting error:** assuming template edits mutate all existing claims.

8. **Why are hostpath snapshots not production backups?**  
   **Answer:** They live on the same node disk and share its failure domain. **Tempting error:** assuming a separate API object means physically independent data.

9. **How should you diagnose `FileSystemResizePending`?**  
   **Answer:** Compare request/PV capacity, Events, driver logs, node plugin, filesystem and `df -h`; follow the exact documented driver procedure. **Tempting error:** blindly restarting a Pod or deleting the claim.

10. **What proves a recovery process works?**  
    **Answer:** A restore into an isolated target followed by application-level integrity checks and recorded duration. **Tempting error:** counting snapshot creation as a restore test.

11. **What controls should protect snapshot deletion?**  
    **Answer:** Least-privilege RBAC, approved classes/policies, ownership, retention rules, audit logs and separation of duties. **Tempting error:** relying on namespace boundaries alone for cluster-scoped content and backend data.

### 3.12 Evidence artifacts

Retain only sanitized evidence; never include credentials or sensitive application data.

- `evidence/context-disk.txt`: current context, kind cluster, node status, before/after disk checks.
- `evidence/driver-and-snapshotter-versions.md`: exact driver, CRD/controller, sidecar and Kubernetes versions with official compatibility references.
- `evidence/source-pvc.yaml` and `evidence/source-checksums-before.txt`.
- `evidence/volumesnapshot.yaml`, `evidence/volumesnapshotcontent.yaml`, readiness status and Events.
- `evidence/restore-pvc.yaml`, restore Pod logs, integrity query/checksum output and pass/fail result.
- `evidence/clone-source-target.yaml`, source/clone checksums and independent-write test.
- `evidence/resize-before-after.txt`: PVC/PV capacity, conditions, Events, `df -h`, and `lsblk` only where meaningful.
- `evidence/statefulset-expansion.md`: actual generated PVC name, documented procedure/version, before/after manifest and data marker.
- `evidence/snapshot-is-not-backup-reflection.md`: three failure scenarios and controls.
- `evidence/cleanup-confirmation.txt`: named resources removed, PV/snapshot state reviewed, disk check.
- `evidence/restore-test-report.md`: recovery point, elapsed time, integrity result, failure diagnostics and unresolved `[VERIFY]` items.

These artifacts do not exist until the learner collects them. A failed test should retain diagnostics rather than silently cleaning away the evidence.

### 3.13 Common interview and design-review questions

1. **Why is a volume snapshot not automatically a backup?**  
   **Model answer:** It may share the source's failure domain and lifecycle, may not be application-consistent, and may never have been restored. A backup strategy requires independent retention, access separation, a defined RPO/RTO and successful restore tests. Hostpath snapshots live on the same node disk.

2. **How do you distinguish crash-consistent from application-consistent recovery for PostgreSQL?**  
   **Model answer:** A crash-consistent snapshot captures storage state without necessarily coordinating database writes and logs; PostgreSQL may recover from it, but the exact storage and WAL arrangement matters. Application-consistent recovery requires a documented database backup/quiescing protocol, coordinated volumes if applicable, and validation. `CHECKPOINT` alone is not a complete backup protocol; verify version-specific PostgreSQL backup documentation.

3. **When would you choose a PVC clone over a snapshot restore?**  
   **Model answer:** A clone can provision an isolated target from a source PVC for test/dev where supported; snapshot restore targets a captured point in time. Verify namespace, class, size, driver and backend constraints. Do not assume copy-on-write, space savings or independence without evidence.

4. **A PVC is stuck in `FileSystemResizePending`. What is your response?**  
   **Model answer:** Preserve evidence; compare requested and PV capacity; inspect Events, controller/node logs, filesystem type, mount state and documented online/offline support; validate with `df -h`. Follow the driver-specific runbook and coordinate any remount/restart. Never blindly delete the claim or remove finalizers.

5. **How would you govern snapshots and expansion for a production StatefulSet/database?**  
   **Model answer:** Define approved classes, capability/version evidence, owner, retention, deletion policy, backup/restore protocol, RPO/RTO, capacity guardrails, least-privilege RBAC, application consistency, canary testing, abort criteria and restore drills. Treat `volumeClaimTemplates` changes as version-sensitive and migrate/expand existing claims through a documented process.

### 3.14 Sources and verification notes

No live web consultation or cluster execution was performed while writing this lesson. The following official entry points are provided for verification; exact release compatibility and installed API behavior remain open until checked.

#### Official source references

- Kubernetes documentation — **Volume Snapshots**: https://kubernetes.io/docs/concepts/storage/volume-snapshots/ — snapshot object roles, lifecycle and restore concepts.
- Kubernetes documentation — **Persistent Volumes**: https://kubernetes.io/docs/concepts/storage/persistent-volumes/ — PVC/PV lifecycle and volume expansion concepts.
- Kubernetes documentation — **StatefulSets**: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ — claim templates and StatefulSet lifecycle; verify current orphan/cascade behavior before any workaround.
- Kubernetes CSI project documentation: https://kubernetes-csi.github.io/docs/ — CSI sidecars and snapshot integration.
- Official external-snapshotter repository: https://github.com/kubernetes-csi/external-snapshotter — CRDs, controller/sidecar release and compatibility details.
- Official CSI hostpath test/reference driver: https://github.com/kubernetes-csi/csi-driver-host-path — installation, release manifests and driver capabilities. Required caveat: hostpath snapshots live on the same node disk.
- Kubernetes API reference — PVC: https://kubernetes.io/docs/reference/kubernetes-api/config-and-storage-resources/persistent-volume-claim-v1/ — `dataSource` fields and PVC API schema.
- PostgreSQL official documentation: https://www.postgresql.org/docs/ — check the version-specific backup, checkpoint and recovery procedures before using database-native functions.
- kind documentation: https://kind.sigs.k8s.io/docs/user/quick-start/ — local cluster setup and resource/runtime details.
- Optional policy engines (awareness only): official Gatekeeper/Kyverno documentation must be checked for the exact policy syntax/API version before installation or enforcement.

#### Verification register

| Claim | Why version/backend-sensitive | Official source/check | Blocks execution? | Status |
|---|---|---|---|---|
| Snapshot API group/version and CRD installation | Kubernetes and external-snapshotter release compatibility | Kubernetes snapshot docs; selected external-snapshotter release | Yes, before snapshot labs | OPEN — `[VERIFY]` |
| Controller/sidecar compatibility | Multiple independently versioned components | External-snapshotter compatibility docs and driver release notes | Yes | OPEN — `[VERIFY]` |
| Hostpath install manifests and driver name | Release-specific packaging | Official CSI hostpath README/release manifests | Yes | OPEN — `[VERIFY]` |
| Hostpath snapshot failure domain | Driver implementation and selected deployment | Official driver docs/source; inspect backend path | Yes, for any durability claim | Required limitation stated; confirm selected release |
| `VolumeSnapshotClass.deletionPolicy` lifecycle | Controller/driver/backend behavior | Kubernetes snapshot docs and selected driver docs | Yes, before deleting snapshots | OPEN — `[VERIFY]` |
| `readyToUse` exact status semantics | API/controller version | Snapshot API reference and installed CRD schema | Yes, before automation | OPEN — `[VERIFY]` |
| Snapshot restore class/size constraints | Driver/backend and Kubernetes version | Driver docs and controlled test | Yes | OPEN — `[VERIFY]` |
| PVC clone namespace/class/size constraints | Kubernetes and CSI driver versions | Kubernetes PVC docs and driver clone docs | Yes, before clone lab | OPEN — `[VERIFY]` |
| Expansion/online filesystem resize | Driver, backend, filesystem and sidecars | Kubernetes PV docs and driver docs | Yes, before expansion lab | OPEN — `[VERIFY]` |
| `Resizing`/`FileSystemResizePending` handling | Driver/filesystem/node state | PVC API/events, driver runbook | Yes, before remediation | OPEN — `[VERIFY]` |
| PostgreSQL backup API names and usage | PostgreSQL major version and backup method | Official PostgreSQL docs for installed version | Yes, before using functions | OPEN — `[VERIFY]` |
| `fsfreeze` prerequisites/recovery | Filesystem, privilege and mount scope | Official OS/filesystem docs and platform runbook | Yes, before use | OPEN — `[VERIFY]` |
| StatefulSet orphan/recreate workaround | Kubernetes version and controller state | Current StatefulSet docs and tested disposable cluster | Yes, before Lab 4 workaround | OPEN — `[VERIFY]` |
| ext4/XFS resize behavior | Filesystem and utility versions | Official filesystem documentation | Yes, before filesystem-specific remediation | OPEN — `[VERIFY]` |
| `VolumeGroupSnapshot` support | API maturity, CRDs, driver/backend | Official Kubernetes CSI/external-snapshotter docs | Yes, before relying on it | OPEN — `[VERIFY]` |
| Snapshot/clone incremental or copy-on-write behavior | Backend implementation | Official backend/driver documentation | Yes, before cost/performance claims | OPEN — `[VERIFY]` |
| Policy engine syntax and admission APIs | Kubernetes and policy-engine versions | Official API/policy docs | Yes, before enforcement | OPEN — `[VERIFY]` |

#### AI self-audit

This is an AI content audit, not an independent review or successful runtime test.

- **Scope and headings:** PASS — exact Unit 3 scope and headings 3.0–3.14 are present in order.
- **L1–L4 curriculum:** PASS at lesson-content level for API objects, snapshot/restore, clone, expansion, consistency, automation, incidents and guardrails.
- **Four labs:** PASS for all four requested lab designs and the required reflection; OPEN — `[VERIFY]` for exact driver installation, snapshotter compatibility, clone/expansion support and StatefulSet workaround until checked against selected releases.
- **Data safety:** PASS for new-PVC restore, disposable data, explicit destructive prefaces, bounded waits, named cleanup, and no generic force-delete/finalizer shortcuts.
- **Technical authenticity:** PASS for distinguishing API readiness from application validation and API objects from backend bytes. Version/backend-sensitive claims remain open as listed.
- **Sources:** official entry points are provided, but live consultation was not performed; none is represented as consulted during generation.
- **Execution status:** no manifests or labs were executed here. All expected behavior is labelled representative or described as a success criterion.
- **Unresolved verification:** 16 grouped items remain `OPEN — [VERIFY]`; resolve them for the actual Kubernetes, snapshotter, driver, backend and filesystem versions before executing the relevant steps.
