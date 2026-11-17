# Unit 2 — StorageClasses, Dynamic Provisioning, and CSI Drivers

This unit explains how Kubernetes turns a storage request into a provisioned volume, how StorageClasses express storage policy, and how Container Storage Interface (CSI) components coordinate with a backend. It progresses from inspecting a local `kind` cluster to capability assessment, safe driver operations, governance, and incident response. The labs use disposable data and the official Kubernetes CSI hostpath **test/reference driver** where compatible instructions can be confirmed from the selected release. This driver is for development and testing, not production storage.

**Target file:** `02-storageclasses-dynamic-provisioning-and-csi-drivers.md` | **Estimated time:** 8–12 hours | **Prerequisites:** M05 Unit 1 PV/PVC vocabulary, Pods and scheduling, namespaces, RBAC, `kubectl`, basic Linux filesystems, shell fundamentals.

**Core tools:** `kubectl`, `kind`, Bash, `jq` (optional), Git, Docker or the runtime used by `kind` | **Awareness:** cloud block/file CSI drivers, NFS/SMB, Ceph/Rook, Longhorn, OpenEBS, local static provisioners, object-storage gateways, external-snapshotter | **Last reviewed:** 2026-10-28 | **Kubernetes/tool baseline assumed:** current supported `kind`/Kubernetes release and a compatible CSI hostpath release, but exact versions are **[VERIFY]** before installation. No command, manifest, or lab in this document is claimed to have been executed.

## Contents

- [2.0 Why this matters in production](#20-why-this-matters-in-production)
- [2.1 Learning objectives](#21-learning-objectives)
- [2.2 Concept map and vocabulary](#22-concept-map-and-vocabulary)
- [2.3 Level 1 — Beginner](#23-level-1--beginner)
- [2.4 Level 2 — Intermediate](#24-level-2--intermediate)
- [2.5 Level 3 — Advanced](#25-level-3--advanced)
- [2.6 Level 4 — Expert](#26-level-4--expert)
- [2.7 SRE lens](#27-sre-lens)
- [2.8 Security lens](#28-security-lens)
- [2.9 Production checklist](#29-production-checklist)
- [2.10 Hands-on lab set](#210-hands-on-lab-set)
- [2.11 Self-check questions](#211-self-check-questions)
- [2.12 Evidence artifacts](#212-evidence-artifacts)
- [2.13 Common interview and design-review questions](#213-common-interview-and-design-review-questions)
- [2.14 Sources and verification notes](#214-sources-and-verification-notes)

## Unit 2 — StorageClasses, Dynamic Provisioning, and CSI Drivers

### 2.0 Why this matters in production

A team should not need a platform administrator to hand-create a PersistentVolume for every database, metadata service, or data pipeline. Dynamic provisioning makes storage requests self-service: a workload creates a PVC, Kubernetes selects a StorageClass, and a provisioner/driver asks a backend to create a storage resource. This reduces repetitive operations, but it also turns StorageClass design into a platform contract. A misconfigured default class, an unreviewed parameter, or an incompatible driver upgrade can affect many workloads at once.

A StorageClass is not the disk. It is a cluster-scoped template/policy that names a provisioner and may pass driver-specific parameters. The provisioner and driver determine whether a request can be fulfilled and what resource is created. The backend determines physical or logical storage behavior. A class named `fast-retain` does not prove high IOPS, replication, encryption, or backup unless those features are actually configured and evidenced.

CSI is a standardized interface between Kubernetes-side components and storage drivers; it is not a storage backend. A CSI driver connects Kubernetes to a particular storage system and implements the capabilities that system supports. A local `kind` PVC can prove that a development flow works. It cannot prove production durability, failure-domain independence, performance, or recoverability.

### 2.1 Learning objectives

By the end of this unit, the learner can:

1. [L1] Explain static versus dynamic provisioning and trace a PVC through StorageClass selection to PV and backing storage.
2. [L1] Inspect a cluster's real StorageClasses, default annotation, provisioner, parameters, and PVC events without assuming a class name.
3. [L2] Explain controller-plugin, node-plugin, sidecar, kubelet, `CSIDriver`, `CSINode`, and `VolumeAttachment` responsibilities.
4. [L2] Install and verify a compatible release of the official CSI hostpath test/reference driver by following its official release instructions.
5. [L2] Compare `Immediate` and `WaitForFirstConsumer` using disposable claims and consumer Pods.
6. [L3] Build a driver capability matrix that separates Kubernetes API support from actual driver/backend support.
7. [L3] Design a StorageClass catalog and decision record for scratch, standard persistent, retained, and shared workloads.
8. [L4] Diagnose CSI provisioning, attach, mount, topology, and compatibility incidents using multiple evidence sources.
9. [L4] Design controls for class ownership, driver upgrades, unapproved provisioners, and safe migration/deprecation.

### 2.2 Concept map and vocabulary

```text
Application / Pod
      |
      | PVC reference
      v
PersistentVolumeClaim (namespaced request)
      |
      | selects class / binding policy
      v
StorageClass (cluster-scoped template)
      |
      | provisioner identity + driver-specific parameters
      v
External provisioner / CSI controller plugin
      |
      | CSI gRPC calls (capabilities vary by driver)
      v
Storage backend  <-------------------->  PV (cluster API object)
      ^                                      |
      |                                      | binds to PVC
      |                                      v
Actual bytes                         kubelet + CSI node plugin
                                             |
                                             v
                                    stage / publish / mount
                                             |
                                             v
                                     container volume path
```

The diagram is conceptual. Some static PVs do not use dynamic provisioning. Some volume types do not require attach operations or a `VolumeAttachment` object. The PV is Kubernetes metadata that represents a resource; the backend stores the bytes.

#### Core vocabulary

| Term | Meaning | Common mistake |
|---|---|---|
| StorageClass | Cluster-scoped provisioning template and policy | Treating it as the disk or a performance guarantee |
| Provisioner | Component that reacts to PVC requests and coordinates provisioning | Assuming the string in `provisioner` alone proves capability |
| CSI driver | Plugin implementing CSI operations for a storage system | Calling CSI itself the backend |
| Controller plugin | Driver component for control-plane operations, such as create/delete/attach when supported | Assuming every driver has the same deployment shape |
| Node plugin | Driver component that runs on nodes and performs node-side storage operations | Assuming controller health proves node mount health |
| Sidecar | Separate Kubernetes component that watches API objects and calls driver/controller operations | Assuming every sidecar is always installed |
| `CSIDriver` | Cluster object describing a CSI driver and selected Kubernetes integration settings | Assuming it lists every feature the driver supports |
| `CSINode` | Node-scoped registration/capability information for CSI drivers | Treating it as the backing-storage inventory |
| `VolumeAttachment` | API object used for attach/detach coordination for attachable volumes | Expecting one for every volume |
| `CSIStorageCapacity` | Optional capacity information used by compatible provisioning/scheduling paths | Assuming it is always published or honored |
| StorageClass parameter | Driver-specific value passed during provisioning | Copying parameter keys from a different driver |
| `volumeBindingMode` | Controls whether binding/provisioning occurs immediately or waits for a consumer | Treating delayed binding as a universal scheduling fix |

#### Static PV provisioning versus dynamic provisioning

| Dimension | Static provisioning | Dynamic provisioning |
|---|---|---|
| Who creates storage | Administrator/platform process creates backend resource and PV | Provisioner/driver creates resource in response to a claim |
| PVC workflow | Claim must match an existing PV | Claim selects a StorageClass and requests storage |
| Operational burden | More manual inventory, naming, matching and lifecycle work | More self-service and repeatability |
| Best fit | Pre-existing storage, special recovery, carefully managed local PVs | Standardized workloads with approved classes |
| Main risks | Wrong PV binding, stale inventory, manual mistakes | Bad class defaults/parameters, uncontrolled backend growth, driver-wide failures |
| Evidence | PV YAML and backend inventory | PVC/PV events, StorageClass, driver logs, backend evidence |

Dynamic provisioning reduces toil but does not eliminate capacity planning, access control, ownership, backups, or backend lifecycle management.

### 2.3 Level 1 — Beginner

#### The PVC-to-storage flow

A typical dynamic provisioning path is:

1. A user creates a PVC with capacity, access mode, and optional `storageClassName`.
2. Kubernetes evaluates class selection and binding behavior.
3. The PV controller coordinates binding; if dynamic provisioning is required, the external provisioner watches the claim and requests the appropriate driver operation.
4. The driver/controller asks the backend to create or allocate a resource.
5. A PV object represents the provisioned resource and binds to the PVC.
6. When a Pod consumes the claim, the scheduler, attach/detach path where applicable, kubelet, and node plugin arrange node access and mounting.
7. On claim deletion, reclaim behavior and the driver/backend determine what happens to the PV object and backing resource.

Not every backend follows identical steps. Static PVs can skip dynamic provisioning; some drivers do not need a separate attach operation; delayed binding can wait for a consumer before provisioning.

#### StorageClass field reference

| Field | Purpose / scope | Example shape | Common mistake / dependency |
|---|---|---|---|
| `provisioner` | Required identity of the provisioner/driver for this class; cluster-scoped StorageClass | `provisioner: <documented-driver-name>` | Never invent the name; it must match the installed provisioner |
| `parameters` | Map of backend/driver-specific provisioning settings | `parameters: {}` or documented keys | Kubernetes does not validate arbitrary semantics uniformly; invalid values may fail only at provisioning time |
| `reclaimPolicy` | Reclaim behavior for dynamically provisioned PVs; commonly `Delete` or `Retain` | `reclaimPolicy: Retain` | Does not mean backup; backend deletion semantics are driver-specific |
| `volumeBindingMode` | Binding/provision timing | `Immediate` or `WaitForFirstConsumer` | Delayed binding is useful for topology but cannot make an impossible Pod schedulable |
| `allowVolumeExpansion` | Whether PVC capacity expansion may be requested for supported volumes | `allowVolumeExpansion: true` | API permission is not proof of driver/filesystem support or online expansion |
| `mountOptions` | Backend/filesystem mount options | `mountOptions: ["<documented-option>"]` | Kubernetes may not validate option semantics; a bad option can break mounting |
| `allowedTopologies` | Restricts where dynamically provisioned volumes may be created, using topology label expressions | `allowedTopologies: ...` | Label keys and supported topology are driver/platform-specific; wrong restrictions can leave claims pending |

`parameters` must come from the exact driver's official documentation. Do not paste parameters from a cloud provider, NFS driver, or test driver into another class. The API may accept a string map while the driver rejects its contents later.

#### Default StorageClass behavior

The annotation commonly used to mark a default class is:

```yaml
metadata:
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
```

**[VERIFY]** Confirm current default-selection and retroactive assignment semantics in the official StorageClass documentation for the installed Kubernetes version. Inspect the live cluster rather than relying on this example.

| PVC configuration | Meaning / expected behavior |
|---|---|
| `storageClassName` omitted | Requests default-class selection where a default exists; behavior for no default or later default assignment is version-sensitive |
| `storageClassName: ""` | Explicitly requests no StorageClass; dynamic class selection is disabled and a matching static PV may be needed |
| `storageClassName: "some-class"` | Selects that named class; it must exist and use a working provisioner |
| No default class | An omitted class may remain unassigned/pending until class selection is possible; verify current version behavior |
| Multiple defaults | Kubernetes has defined behavior for default selection, but it is an ambiguity and governance defect; inspect official version documentation and fix the cluster catalog |

Do not use an empty class name as a synonym for “use the default.” Omission and an explicit empty string are different intents.

#### Discover the actual cluster configuration

Run the following read-only commands before creating resources:

```bash
set -euo pipefail
kubectl config current-context
kind get clusters
kubectl get nodes -o wide
df -h .
kubectl get storageclass
kubectl get sc -o yaml
kubectl get pvc -A
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

If event sorting is unsupported or there are no events, use:

```bash
kubectl get events -A
kubectl describe pvc <claim-name> -n <namespace>
kubectl describe storageclass <class-name>
```

Events can expire or may never have been emitted. A missing Event is not proof that provisioning succeeded.

Inspect a StorageClass:

```bash
kubectl get sc <class-name> -o yaml
kubectl describe sc <class-name>
kubectl get pv -o wide
kubectl get pvc -A -o wide
```

For `kind`, discover the actual default class, provisioner, and backing implementation. A common local-path-style class is convenient for learning but usually depends on node-local/host-backed storage. Do not assume its name, reclaim behavior, expansion, snapshots, replication, or durability.

#### Minimal claim using a discovered class

**File: `lab-a-pvc.yaml` — a small disposable claim.** Replace `<DISCOVERED_CLASS>` with a real class name from `kubectl get sc`. This is a template, not directly runnable until the placeholder is replaced.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: m05-storageclass-lab
  labels:
    app.kubernetes.io/part-of: m05-storageclass-lab
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: class-discovery-data
  namespace: m05-storageclass-lab
  labels:
    app.kubernetes.io/part-of: m05-storageclass-lab
spec:
  storageClassName: "<DISCOVERED_CLASS>"
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 128Mi
```

Validation and inspection:

```bash
kubectl apply --dry-run=client -f lab-a-pvc.yaml
kubectl explain storageclass.spec
kubectl apply -f lab-a-pvc.yaml
kubectl get pvc -n m05-storageclass-lab -o wide
kubectl describe pvc class-discovery-data -n m05-storageclass-lab
kubectl get pv -o yaml
kubectl get events -n m05-storageclass-lab
```

Client-side dry-run validates client-side structure only. It does not prove admission acceptance, provisioner health, backend success, or mountability. If `WaitForFirstConsumer` is configured, the PVC may not bind until a consuming Pod can be scheduled.

**Expected output (representative; not executed here):** the PVC may be `Pending` until a consumer exists for a delayed-binding class, or become `Bound` if the class provisions immediately. The resulting PV should identify its StorageClass and provisioner-specific source. Exact names, phases, and Events depend on the installed class and cluster.

### 2.4 Level 2 — Intermediate

#### CSI architecture: what each component does

CSI standardizes communication between Kubernetes integration components and a driver. The CSI protocol uses gRPC service families conceptually grouped as:

- **Identity service:** reports driver identity and supported protocol details.
- **Controller service:** storage control-plane operations such as create/delete volume, attach/detach, snapshots or expansion where implemented.
- **Node service:** node-side operations such as staging, publishing, unpublishing, un-staging, and node capability reporting.

A driver implements only the operations and capabilities appropriate to its design. Never assume that every method or feature is supported just because the driver is CSI-compatible.

| Component | Common deployment shape | Responsibility | Important caveat |
|---|---|---|---|
| CSI controller plugin | Deployment or StatefulSet, depending on package | Driver control-plane operations | Exact packaging is release-specific |
| External provisioner sidecar | Often alongside controller plugin | Watches PVCs and coordinates `CreateVolume`/`DeleteVolume` calls | Must be compatible with driver and Kubernetes |
| External attacher sidecar | Present when attach/detach integration is used | Coordinates attachment through Kubernetes APIs and driver | Not required for every driver/volume path |
| External resizer sidecar | Present when expansion is supported/configured | Coordinates volume expansion | Sidecar alone does not make expansion possible |
| External snapshotter sidecar | Present when snapshot support is installed/configured | Coordinates snapshot API operations | Snapshot CRDs/controller and backend support are also needed |
| Node plugin | Commonly DaemonSet | Implements node-side mount/stage/publish operations | Node plugin readiness is node-specific |
| `node-driver-registrar` | Often a node-plugin sidecar | Registers the driver with kubelet | Exact package/version details must be checked |
| kubelet | Kubernetes node agent | Coordinates volume setup for Pods and invokes supported driver paths | Successful controller provisioning does not prove node mount success |
| API controllers | Kubernetes control plane | Reconcile PVC/PV, attach, scheduling and related objects | Different controllers own different parts of the lifecycle |

#### Object and operation chain

| Object/component | Role | Evidence |
|---|---|---|
| PVC | User's namespaced request | `kubectl get/describe pvc` |
| StorageClass | Provisioning template | `kubectl get sc -o yaml` |
| External provisioner | Watches claims and requests provisioning | Controller Pod logs and PVC Events |
| CSI controller plugin | Driver control-plane operations | Driver controller logs and deployment status |
| PV | Cluster API representation of the provisioned resource | `kubectl get pv -o yaml` |
| `CSIDriver` | Driver integration settings such as selected lifecycle behavior | `kubectl get csidriver -o yaml` |
| `CSINode` | Driver registration/capability information per node | `kubectl get csinode -o yaml` |
| `VolumeAttachment` | Attach coordination for attachable volumes | `kubectl get volumeattachment -o yaml` |
| CSI node plugin | Node-side stage/publish/mount | Node-plugin logs, Pod Events |
| Backend | Actual storage system holding data | Driver/backend telemetry and inventory |

A `VolumeAttachment` is not universally present. A local-path or non-attachable volume path may not create one. If it is absent, inspect the driver's documented design, `CSINode`, Pod Events, and node-plugin logs rather than treating absence as an error.

#### `Immediate` versus `WaitForFirstConsumer`

| Mode | Binding/provision timing | Benefits | Risks / limitations |
|---|---|---|---|
| `Immediate` | Binding/provisioning can begin as soon as the PVC is created | Simple for topology-independent storage | May provision in a topology incompatible with the eventual Pod |
| `WaitForFirstConsumer` | Delays binding/provisioning until a consuming Pod's scheduling constraints can inform placement | Better alignment with topology, node affinity and scheduling constraints | PVC can remain Pending if no consumer can schedule; not a universal fix |

A delayed-binding PVC without a consumer Pod can remain Pending by design. A consumer Pod with impossible node affinity, insufficient resources, a selector conflict, or unsupported topology may still be unschedulable. The test driver may demonstrate the API/scheduler sequence without representing real zones or cloud topology.

#### Official CSI hostpath test/reference driver lab

Use the official repository and release instructions: `https://github.com/kubernetes-csi/csi-driver-host-path`. **[VERIFY]** The exact install command, release tag, manifest directory, Kubernetes compatibility, sidecar versions, and cleanup steps must be selected from the official README/release assets for the learner's current `kind` Kubernetes version. This lesson deliberately does not invent a tag or a manifest URL.

Before installation:
1. Read the repository README and release notes for the chosen release.
2. Identify the supported Kubernetes version and any required CRDs/sidecars.
3. Inspect the exact manifests or deployment script before applying them.
4. Confirm resource names, namespaces, labels, controller shape, node DaemonSet, `CSIDriver`, and any class example.
5. Use a disposable `kind` cluster and check disk first.

Example discovery sequence:

```bash
set -euo pipefail
kubectl config current-context
kind get clusters
kubectl get nodes -o wide
df -h .
git --version
```

Clone only after choosing a verified release from the official project page:

```bash
# Replace <VERIFIED_RELEASE_TAG> with a tag confirmed in the official repository.
git clone https://github.com/kubernetes-csi/csi-driver-host-path.git
cd csi-driver-host-path
git checkout <VERIFIED_RELEASE_TAG>
# Inspect README, release notes and deploy manifests before executing any installer.
git status --short
find . -maxdepth 3 -type f | sort | sed -n '1,160p'
```

The checkout command is intentionally a template; `<VERIFIED_RELEASE_TAG>` is not a real tag. Do not paste it unchanged. Follow the selected release's documented installation instructions rather than guessing a `deploy/...` path. The driver is a test/reference implementation, not production storage.

After the official install procedure, verify resources by discovery rather than invented selectors:

```bash
kubectl get pods -A -o wide
kubectl get deployments,statefulsets,daemonsets -A
kubectl get crd
kubectl get csidriver
kubectl get csinode -o yaml
kubectl get storageclass -o yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Identify driver-related resources by comparing output with the manifests from the selected checkout. For each discovered controller/node Pod, capture status and logs:

```bash
kubectl describe pod <DISCOVERED_CONTROLLER_POD> -n <DISCOVERED_NAMESPACE>
kubectl logs <DISCOVERED_CONTROLLER_POD> -n <DISCOVERED_NAMESPACE> --all-containers=true
kubectl describe pod <DISCOVERED_NODE_PLUGIN_POD> -n <DISCOVERED_NAMESPACE>
kubectl logs <DISCOVERED_NODE_PLUGIN_POD> -n <DISCOVERED_NAMESPACE> --all-containers=true
```

Replace all placeholders after discovery. Do not run the example until names and namespace are verified. If a selected release uses different resources or sidecar names, follow that release's documentation.

Create a StorageClass only after verifying the provisioner string and parameters from the selected driver release. **File: `lab-b-hostpath-storageclass.yaml` — template only; not directly runnable until placeholders and documented parameters are resolved.**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: m05-hostpath-test
  labels:
    app.kubernetes.io/part-of: m05-storageclass-lab
provisioner: "<DOCUMENTED_CSI_PROVISIONER_NAME>"
reclaimPolicy: Delete
volumeBindingMode: Immediate
allowVolumeExpansion: false
parameters: {}
```

The `parameters: {}` shape is deliberately empty; add only parameters explicitly documented by the selected driver release. Replace the provisioner placeholder with the exact documented identity. If the driver requires parameters, this class may not work until those are supplied. Do not treat this template as evidence that a particular hostpath driver release supports the selected mode or class.

Validate and inspect:

```bash
kubectl apply --dry-run=client -f lab-b-hostpath-storageclass.yaml
kubectl apply -f lab-b-hostpath-storageclass.yaml
kubectl get sc m05-hostpath-test -o yaml
kubectl describe sc m05-hostpath-test
```

The class is cluster-scoped even though it carries a lab label. Cleanup must not remove shared driver CRDs or components. Use the exact uninstall procedure documented by the selected release and inspect what it deletes. If a driver installation is shared or its ownership is unclear, do not uninstall it.

#### Capability comparison: local-path-style kind class versus hostpath test driver

| Capability | kind default local-path-style class | CSI hostpath test/reference driver | Production CSI backend |
|---|---|---|---|
| Dynamic provisioning | Often available; inspect actual class | Intended for testing; verify selected release | Driver/backend-specific |
| Node locality | Commonly node/host-path dependent; verify | Test-driver implementation dependent | May be local, network, or distributed |
| Attach / `VolumeAttachment` | May not use CSI attach; inspect actual path | Driver/release dependent; do not assume | Backend/driver-specific |
| Filesystem | Usually filesystem-oriented; verify | Verify documented modes | Backend/driver-specific |
| Raw block | Unknown unless documented | Verify release capability | Backend/driver-specific |
| RWO/RWX/ROX/RWOP | Must be tested/documented | Test-driver capabilities are not production evidence | Explicit driver/backend evidence required |
| Snapshots / clones | Do not assume | May support selected test features; verify | Driver + sidecars + CRDs + backend support |
| Expansion | Often not configured; verify | Verify release and class setup | Driver/backend/filesystem dependent |
| Topology | Local scheduling constraints may apply | Not genuine multi-zone simulation | Backend and scheduler integration dependent |
| Replication / durability | No production durability inference | Not production durability | Requires documented backend design |
| Encryption at rest | Not proven by class | Not proven by test driver | Verify backend and key management |
| Resource footprint | Usually low | Depends on selected manifest/sidecars | Varies; heavyweight systems may exceed laptop budget |
| Intended use | Local development | Driver development and integration testing | Production only after design and evidence |

### 2.5 Level 3 — Advanced

#### Capability matrix: API possibility versus evidence

Use this matrix as a template, not as a declaration of support. Fill in the actual driver/version and cite its official capability matrix and observed tests.

| Capability | Kubernetes/API concept | Driver/backend evidence required | Status |
|---|---|---|---|
| Dynamic provisioning | StorageClass and provisioner | Provisioning succeeds for the documented class | `[VERIFY]` per driver |
| Attach/detach | CSI controller attach capability and Kubernetes attachment integration | Driver docs, `VolumeAttachment` behavior, logs | `[VERIFY]` |
| Filesystem | PVC volume mount | Supported filesystems and mount options | `[VERIFY]` |
| Raw block | PVC `volumeMode: Block`, `volumeDevices` | Driver/backend block support | `[VERIFY]` |
| RWO | Kubernetes access mode | Node/backend semantics and version | `[VERIFY]` |
| ROX/RWX | Kubernetes access modes | Shared backend and concurrency semantics | `[VERIFY]` |
| RWOP | Kubernetes access mode | Kubernetes, CSI sidecar, and driver compatibility | `[VERIFY]` |
| Snapshots | Snapshot APIs and external-snapshotter integration | Snapshot CRDs/controller, driver capability, backend support | `[VERIFY]` |
| Clones | PVC data source support where implemented | Driver/backend clone support and same-class/topology constraints | `[VERIFY]` |
| Expansion | PVC expansion API and resizer integration | Controller/node expansion, filesystem support, online/offline semantics | `[VERIFY]` |
| Topology / `allowedTopologies` | StorageClass topology constraints | Driver topology keys and backend placement behavior | `[VERIFY]` |
| Volume health | Optional health reporting/driver integration | Actual driver metrics/events and Kubernetes support | `[VERIFY]` |
| Encryption at rest | Backend/platform feature | Encryption configuration, key management and audit evidence | `[VERIFY]` |
| Replication/durability | Backend architecture | Replication mode, failure domains, RPO/RTO and restore evidence | `[VERIFY]` |
| Mount options | StorageClass mountOptions | Driver/filesystem supported values | `[VERIFY]` |
| `fsGroup` | Pod security context and `CSIDriver.spec.fsGroupPolicy` | Actual driver/filesystem ownership behavior | `[VERIFY]` |
| Capacity reporting | `CSIStorageCapacity` and scheduler/provisioner integration | API maturity/enablement and driver publishing behavior | `[VERIFY]` |

The presence of a Kubernetes API field proves that the API can express a request, not that the selected driver honors it. A successful mount proves neither replication nor backup. A snapshot object proves only that an API operation was accepted/completed according to its status; it does not prove application consistency or an independent restore.

#### `CSIDriver.spec.fsGroupPolicy`

The `CSIDriver` object can declare how Kubernetes should handle filesystem group ownership for supported driver paths. Exact field availability, defaulting, and behavior are version-sensitive. **[VERIFY]** Check the current Kubernetes API reference and selected driver's documentation. Do not assume that every CSI driver recursively changes ownership or that `fsGroup` can fix a backend permission problem.

#### StorageClass parameter design

A class can express a platform's intent for performance tier, replication, encryption, topology, reclaim policy, binding mode, expansion, and mount options. Only some of these are generic Kubernetes fields; backend-specific performance, replication, and encryption settings often live in `parameters`. The exact keys and allowed values must come from the driver's official documentation. Do not put credentials in StorageClass parameters.

A class should be reviewed as a contract:
- **What is requested?** Capacity, access pattern, filesystem/block mode, topology.
- **What is guaranteed?** Only documented and measured capabilities.
- **What is not guaranteed?** Anything not backed by driver/backend configuration and evidence.
- **Who owns it?** Platform/storage owner, with an escalation route.
- **What happens at deletion?** Explicit reclaim and retention semantics.
- **How is recovery proven?** Backup/restore path and restore test, not just PVC binding.

#### Illustrative StorageClass taxonomy

These names are organizational examples only; they do not exist automatically and do not imply universal settings.

| Illustrative class | Intent | Guardrails | Capabilities to verify | Owner |
|---|---|---|---|---|
| `fast-retain` | Important state with controlled deletion and a performance requirement | Approval for creation/deletion, quota, backup policy | Performance evidence, reclaim behavior, encryption, expansion, topology | Storage platform + service owner |
| `standard-delete` | Routine state whose lifecycle explicitly permits backend deletion | Namespace quota and clear data classification | Provisioning, backend deletion behavior, capacity limits | Platform owner |
| `shared-rwx` | Workloads requiring concurrent shared filesystem access | Approved tenants, concurrency and permissions review | True RWX support, locking, consistency, failover, performance | Shared-storage owner |
| `scratch` | Recomputable ETL temporary data | Size limits, cleanup and ephemeral-storage monitoring | Capacity/cleanup behavior; whether PVC or `emptyDir` is appropriate | Data-platform owner |

Do not call a class `fast` unless performance has a defined workload, measurement method, and acceptance threshold. Do not call a class `retain` unless the reclaim behavior is verified and a retained-volume lifecycle exists.

#### Decision record template

```markdown
# StorageClass / workload decision record

- Workload and service owner:
- Data classification:
- Capacity estimate and growth:
- Read/write pattern and concurrency:
- Access mode and volume mode:
- Latency / throughput / IOPS requirement and measurement method:
- Durability and failure-domain requirements:
- Topology / scheduling constraints:
- Encryption and key-management requirements:
- StorageClass name and provisioner:
- Driver, sidecar and Kubernetes compatibility evidence:
- Supported snapshots / clones / expansion (source + test evidence):
- Reclaim policy and deletion approval:
- Quota/cost estimate and capacity alerts:
- Backup, restore test, RPO and RTO:
- Operational runbook and escalation:
- Rejected alternatives and reasons:
- Open [VERIFY] items:
- Owner approval / review date:
```

#### Upgrade and compatibility planning

A CSI stack can include Kubernetes, the CSI driver, controller and node components, and multiple sidecars. Their compatibility must be evaluated together. Do not use a random combination of the newest driver and newest sidecars.

Before upgrading:
1. Read the driver's compatibility matrix and release notes.
2. Check supported Kubernetes versions and sidecar versions.
3. Identify CRD/API changes and whether rollback can restore prior objects or schemas.
4. Test in a disposable/staging cluster with representative provisioning, mount, restart, expansion/snapshot operations if relevant.
5. Capture the current manifests, image digests/tags, configuration, class definitions and backend inventory.
6. Define canary scope, maintenance window, success criteria, rollback triggers and an owner.
7. Confirm backup/restore readiness before changes that can affect data paths.
8. Monitor new provisioning and mount operations after rollout; existing mounts alone are insufficient validation.

**[VERIFY]** Every concrete compatibility range and release-specific deployment shape must come from the selected driver's official matrix/release notes. Rollback may be constrained by backend changes, CRD migrations, or data format changes; reverting images does not necessarily reverse those changes.

#### Failure semantics

| Failure | Likely affected operations | What may continue temporarily | Qualification |
|---|---|---|---|
| Controller plugin unavailable | New provisioning, delete operations, attach, resize, snapshots or clones where controller-managed | Already mounted workloads may continue using a mounted device | Backend and driver design determine behavior; operations can still fail later |
| Provisioner sidecar unavailable | New dynamic claims may wait or fail | Existing bound/mounted volumes may continue | Depends on other controller components and reconciliation |
| Attacher/controller unavailable | Attach/detach for attachable volumes may stall | Existing attachments may remain active | Stale attachment and node-loss cases need careful handling |
| Node plugin unavailable on one node | New mounts/publishes on that node; node-side operations | Workloads already mounted may continue, but no guarantee | Crash, reboot, kubelet behavior and driver design matter |
| Node plugin CrashLoopBackOff | Mount/stage/publish operations fail on affected nodes | Existing mounts may or may not remain usable | Inspect node-level state and logs; avoid assuming continuity |
| Backend unavailable | Provisioning, attach, mount, I/O or metadata operations may fail | Some cached/already mounted I/O might continue temporarily | Never promise safe continuation; storage errors can affect writes and integrity |
| Sidecar compatibility mismatch | Reconciliation/attach/resize/snapshot may fail | Existing workloads may be unaffected initially | Verify logs and compatibility, then follow rollback plan |

A running Pod is not proof that storage is healthy. A bound PVC is not proof that the volume is mounted, writable, performant, durable, or backed up.

#### `CSIStorageCapacity`

`CSIStorageCapacity` is a Kubernetes mechanism for publishing storage-capacity information for topology-aware provisioning/scheduling paths. API maturity, feature-gate/default status, scheduler behavior, and driver publication are version-sensitive. **[VERIFY]** Check current API documentation and the selected driver/provisioner integration. Capacity objects may be absent or not honored; never treat their presence as a universal backend capacity guarantee.

#### RWX choices and object-storage caveats

| Option | Strengths | Trade-offs / failure modes | What to verify |
|---|---|---|---|
| NFS | Familiar shared filesystem model | Server availability, network latency, locking and permission mapping | Server failover, NFS version, locking, identity mapping, security |
| SMB | Shared file access and common enterprise identity integrations | Protocol/identity/locking behavior and client compatibility | SMB version, auth, permissions, availability, client support |
| Managed/shared filesystem service | May provide operational features such as managed failover | Cost, service limits, network dependency and vendor semantics | Availability, performance, encryption, quotas, consistency |
| Object storage through gateway/FUSE | Convenient file-like interface for some datasets | Not a full POSIX filesystem; rename/locking/metadata semantics can differ | Consistency, rename behavior, concurrency, caching, API limits |

Object storage is organized around objects and API operations, not a native POSIX filesystem. A FUSE/gateway mount does not magically provide atomic rename, advisory locking, full metadata semantics, low-latency small-file operations, or database-grade durability semantics. Behavior is backend- and implementation-specific. It may suit immutable artifacts or batch data access, but it is usually a poor substitute for a database filesystem unless the application and gateway explicitly support the semantics.

#### CSI secrets

Some CSI integrations support Secret references for provisioning, controller publish/attach, node stage, or node publish operations. Exact fields are driver-specific and must be sourced from the driver documentation; do not invent fields. Store credentials in Kubernetes Secrets or an approved secret system, scope RBAC tightly, restrict which namespaces/service accounts can reference them, rotate credentials, and prevent them from appearing in logs or shell history. Do not place credentials in plain StorageClass parameters or source-controlled manifests.

### 2.6 Level 4 — Expert

#### Storage platform as an internal product

A mature platform provides a documented catalog, a self-service request path, service ownership, support boundaries, capacity guardrails, security claims, backup expectations, and a migration/deprecation policy. The class catalog is a contract with workload teams, not a list of names.

**Class catalog record template**

| Field | Required content |
|---|---|
| Name / status | Class name, approved/deprecated, deprecation date |
| Provisioner / driver | Exact provisioner identity, driver release and compatibility record |
| Purpose / owner | Workload intent, platform owner, escalation route |
| Modes / topology | Supported access and volume modes, topology constraints |
| Capabilities | Expansion, snapshot, clone, capacity reporting, mount options with evidence |
| Reclaim policy | PV behavior and backend deletion/retention proof |
| Performance / durability | Measured workload and backend guarantees; avoid unsupported adjectives |
| Security | Encryption/key ownership, tenant boundaries, secret path |
| Capacity / quota | Request limits, alert thresholds, cost owner |
| Backup / restore | Separate backup plan and restore-test evidence |
| Lifecycle | Upgrade path, migration plan, deprecation date and communications |
| Verification | Official source, test evidence, review date and open `[VERIFY]` items |

#### StorageClass changes and migration

A StorageClass is not a universal in-place migration mechanism. Some fields are immutable; others do not reconfigure already provisioned PVs. Existing PVs keep the backend and properties created for them. PVC binding and `volumeName` relationships constrain changes. **[VERIFY]** Check exact immutability rules for the current Kubernetes API and provisioner before proposing a patch.

Common migration patterns:
1. Create a new approved StorageClass.
2. Create a new PVC using it.
3. Copy data with an application-aware method, snapshot/restore or clone only if the driver supports it, or use application-level replication.
4. Validate checksums/application integrity and cutover behavior.
5. Keep the old volume under a documented rollback/retention plan until acceptance.
6. Retire the old volume only after owner approval and backup evidence.

`pv-migrate`-style tools are awareness-level options; verify the tool's current project, security posture, data consistency semantics and compatibility. A snapshot/clone is not available just because the API exists.

#### Event decoder

Exact event wording varies by Kubernetes version, driver, sidecar and backend. Use the table as a diagnostic map, not a promise that the exact string will appear.

| Symptom / event family | Possible cause | Safe evidence collection | Next test / action | Risk |
|---|---|---|---|---|
| `ProvisioningFailed` | Invalid class parameter, missing driver, backend quota/permission failure | PVC describe, class YAML, controller/provisioner logs | Validate exact driver docs and backend state | Repeated retries can create noisy failures or partial resources |
| `ExternalProvisioning` / waiting message | Provisioner is expected to act or has not reconciled | PVC events, driver Pod status, provisioner logs | Confirm provisioner identity and readiness | Do not assume the backend is being created |
| `AttachVolume.Attach failed` | Attach permission, backend attach conflict, unsupported path | Pod events, VolumeAttachment if applicable, controller logs | Inspect attachment state and driver runbook | Avoid deleting attachment objects as a shortcut |
| `FailedAttachVolume` / multi-attach | Previous node still attached, access-mode/backend constraints | Pods/nodes, VolumeAttachment, backend attach inventory | Confirm old writer/node state before recovery | Concurrent writers can corrupt data |
| `MountVolume.SetUp failed` / `FailedMount` | Node plugin, filesystem, mount options, permissions, missing device | Pod events, node-plugin logs, PV/driver metadata | Verify node plugin readiness and documented mount options | Avoid blind permission changes or forced remount |
| Stale/orphaned `VolumeAttachment` | Node loss, controller/backend reconciliation gap | Object YAML, node status, driver logs and backend attachment state | Follow driver-specific detach recovery | Deleting the object may not detach backend hardware |
| Node-plugin CrashLoopBackOff | Image/config mismatch, host mount/privilege problem, incompatible node | Pod description/logs, node events, installed manifest | Roll back only using approved version plan | Affected-node mount outage |
| Driver missing/unregistered | Node plugin not running/registered, name mismatch | `CSIDriver`, `CSINode`, node Pod logs | Compare exact driver name in PV and installed manifests | New mounts may fail across nodes |
| Topology/capacity mismatch | `allowedTopologies`, affinity, capacity or delayed binding conflict | PVC/Pod events, class YAML, node labels and capacity objects | Validate consumer scheduling and driver topology keys | Repeated class edits can strand claims |

Collect evidence before changing resources. A `VolumeAttachment` deletion does not necessarily detach the actual backend volume. Do not remove PV/PVC/attachment objects to “clear the error” without understanding the data and driver state.

#### Privileged CSI component review

Depending on the driver, node plugins may need privileged containers, host mounts, device access, or broad host-level permissions. This expands the blast radius: a compromised node plugin may affect host resources and workloads on that node. Review:
- image source, provenance, signature/digest policy, vulnerability response and release notes;
- ServiceAccount identity and minimum RBAC;
- privileged settings, capabilities, hostPath mounts, host namespaces and device mounts;
- node placement, tolerations and isolation from untrusted workloads;
- network access to API server and storage backend;
- secret references and logging behavior;
- upgrade, rollback and emergency response procedure.

Not every driver needs identical privileges. Compare the actual rendered manifests with the official driver documentation and your organization's node security baseline.

#### Policy against unapproved StorageClasses

Use multiple controls:
- **RBAC:** restrict who may create/update/delete cluster-scoped StorageClasses and CSI driver resources.
- **Admission policy:** validate PVCs to require an approved class in production, enforce ownership labels, and reject forbidden names/parameters where feasible.
- **Catalog review:** maintain an authoritative file/record with owners, capabilities, lifecycle state and evidence.
- **Audit:** compare live classes to the catalog and flag unknown provisioners, ambiguous defaults, missing owners, and deprecated classes still in use.

RBAC controls who can perform API verbs; admission policy evaluates whether an otherwise authorized object should be accepted. Neither alone proves that a backend parameter is safe or a driver capability exists. Policy engine syntax and `ValidatingAdmissionPolicy` availability are **[VERIFY]** against the installed Kubernetes and policy-engine versions.

#### Read-only audit procedure

**File: `audit-storage-platform.sh` — read-only Bash inventory.** Requires `kubectl` and `jq`. It does not delete or mutate resources.

```bash
#!/usr/bin/env bash
set -euo pipefail

context="$(kubectl config current-context)"
printf 'Context: %s\n' "$context"
printf '%s\n' 'READ-ONLY audit: no resources will be changed.'

sc_json="$(kubectl get storageclass -o json)"
pvc_json="$(kubectl get pvc -A -o json)"
pv_json="$(kubectl get pv -o json)"
va_json="$(kubectl get volumeattachment -o json)"
pod_json="$(kubectl get pods -A -o json)"
csidriver_json="$(kubectl get csidriver -o json)"
csinode_json="$(kubectl get csinode -o json)"

printf '\nStorageClasses and default annotations:\n'
jq -r '.items[] |
  [.metadata.name,
   (.provisioner // "<none>"),
   (.metadata.annotations["storageclass.kubernetes.io/is-default-class"] // "false"),
   (.metadata.labels["platform.example.com/owner"] // "<missing-owner>")] | @tsv' <<<"$sc_json"

printf '\nPVCs not Bound or with no explicit class:\n'
jq -r '.items[] |
  select((.status.phase != "Bound") or (.spec.storageClassName == null)) |
  [.metadata.namespace, .metadata.name, (.status.phase // "Unknown"),
   (if .spec.storageClassName == null then "<omitted>" else .spec.storageClassName end)] | @tsv' <<<"$pvc_json"

printf '\nPV phases requiring review:\n'
jq -r '.items[] |
  select(.status.phase == "Released" or .status.phase == "Failed" or .status.phase == "Lost") |
  [.metadata.name, (.status.phase // "Unknown"),
   (.spec.storageClassName // "<none>"),
   (.spec.persistentVolumeReclaimPolicy // "<unset>")] | @tsv' <<<"$pv_json"

printf '\nVolumeAttachments (review, do not infer orphan status from age alone):\n'
jq -r '.items[] |
  [.metadata.name, (.spec.attacher // "<none>"),
   (.spec.nodeName // "<none>"),
   (.spec.source.persistentVolumeName // "<none>"),
   (.status.attached // false | tostring)] | @tsv' <<<"$va_json"

printf '\nCSI drivers:\n'
jq -r '.items[] | [.metadata.name, (.spec.attachRequired // "unspecified" | tostring)] | @tsv' <<<"$csidriver_json"

printf '\nCSINode names:\n'
jq -r '.items[] | .metadata.name' <<<"$csinode_json"

printf '\nCSI-related Pods not Ready (name/namespace inspection is heuristic):\n'
jq -r '.items[] |
  select((([.status.containerStatuses[]?.ready] | all) | not)) |
  [.metadata.namespace, .metadata.name, (.status.phase // "Unknown")] | @tsv' <<<"$pod_json"
```

The final Pod list is deliberately broad and may include unrelated non-Ready Pods; compare it to the selected driver manifests. A missing `jq` can be handled by saving JSON and inspecting it with a reviewed tool. The script does not prove a class is unapproved unless the approved catalog is supplied for comparison. It does not call a PVC orphaned from a single signal. Permissions may prevent cluster-wide listing.

For Pending-age reporting, choose an explicit threshold and use timestamps only after checking their meaning and timezone. Do not assume a creation timestamp alone distinguishes an expected `WaitForFirstConsumer` PVC from a provisioning incident.

#### Incident scenarios

**A. New PVC remains Pending after a class/driver change**

- **Symptom:** New claims stop binding; old workloads may continue.
- **Hypothesis:** Wrong provisioner name, removed controller, invalid parameters, default-class ambiguity, quota, or incompatible sidecar.
- **Evidence:** PVC events, StorageClass YAML, controller/provisioner status and logs, current manifests and release versions.
- **Data-safety gate:** Do not delete/recreate production claims; preserve YAML and backend identifiers.
- **Fix:** Restore the approved class/driver configuration or roll back through the reviewed change plan.
- **Prevention:** Class contract tests, canary PVC, compatibility matrix, and post-change SLI alerts.

**B. `WaitForFirstConsumer` PVC stays Pending**

- **Symptom:** Claim is pending and may show delayed-binding status; Pod is unschedulable or no consumer exists.
- **Hypothesis:** No consumer Pod, impossible node affinity, insufficient CPU/memory, topology mismatch, selector conflict, or driver capacity limitation.
- **Evidence:** `kubectl describe pvc`, `kubectl describe pod`, node labels/resources, StorageClass `volumeBindingMode`/`allowedTopologies`, events.
- **Data-safety gate:** No deletion is needed for diagnosis.
- **Fix:** Correct the actual scheduling or topology constraint; do not switch to `Immediate` blindly.
- **Prevention:** Test class topology with representative Pod scheduling constraints.

**C. Controller/provisioner outage**

- **Symptom:** New provisioning and controller-managed operations stall.
- **Hypothesis:** CrashLoopBackOff, unavailable API permissions, incompatible sidecar, or backend/API failure.
- **Evidence:** Controller Pod status/logs, events, deployment replicas, backend status.
- **Data-safety gate:** Avoid deleting claims or attachments to clear symptoms.
- **Fix:** Restore the known-good controller/sidecar configuration and verify readiness.
- **Prevention:** Compatibility-tested releases, alerts, staged rollout and rollback evidence.

**D. Node plugin outage**

- **Symptom:** Mount/publish operations fail on one or more nodes.
- **Hypothesis:** DaemonSet not ready, node-specific host mount/permission issue, image mismatch or node registration failure.
- **Evidence:** Node-plugin Pod placement/logs, `CSINode`, Pod events and node condition.
- **Data-safety gate:** Do not reschedule stateful writers until backend attachment and application state are understood.
- **Fix:** Restore node plugin and follow driver recovery guidance.
- **Prevention:** Per-node readiness monitoring and node-specific canary tests.

**E. Driver upgrade breaks attach/mount**

- **Symptom:** Failures begin after a driver or sidecar rollout.
- **Hypothesis:** Incompatible sidecars/Kubernetes, changed configuration, API migration or driver regression.
- **Evidence:** Release versions, manifest diff, events, controller/node logs, compatibility matrix.
- **Data-safety gate:** Preserve data and backend IDs; avoid forced detach/finalizer removal.
- **Fix:** Follow tested rollback or vendor/project recovery guidance; backend changes may not be reversible.
- **Prevention:** Staging, canary, change window and documented rollback limits.

**F. Orphaned `VolumeAttachment` after node loss**

- **Symptom:** New Pod cannot attach a volume and an attachment object references a failed node.
- **Hypothesis:** The backend still considers the volume attached; controller cleanup did not complete; node is unreachable.
- **Evidence:** `VolumeAttachment` YAML, node status, driver/controller logs, backend attachment inventory.
- **Data-safety gate:** Confirm no old writer can still access the device and determine backend state.
- **Fix:** Follow the specific driver's documented detach/recovery workflow with the storage owner. Do not delete the API object as a substitute for backend detach.
- **Prevention:** Node-loss runbook, attachment monitoring, tested fencing and clear ownership.

### 2.7 SRE lens

#### Storage SLIs

| Signal / SLI | Source | What it does and does not tell you |
|---|---|---|
| PVC provisioning/bound time | PVC conditions and Events | Shows API workflow latency, not successful application I/O |
| PVCs Pending beyond threshold | Kubernetes objects plus workload intent | Must account for expected `WaitForFirstConsumer` claims |
| Provisioning error rate | Events, provisioner logs/metrics | Requires reliable parsing/metrics and driver context |
| Attach/mount latency | Events, CSI logs/metrics | Only applicable to relevant volume paths; backend detail may be separate |
| CSI controller/node plugin availability | Pod readiness, DaemonSet/Deployment status, driver metrics | Ready Pods do not prove every operation works |
| Volume health/capacity | Driver/backend metrics where exposed | Not universally available through Kubernetes |
| Application read/write success | Application/database telemetry | Required to assess user-visible impact and integrity |

Native Kubernetes evidence includes object status, conditions, Events, scheduling state, Pod readiness and component health. Backend capacity, IOPS, latency, replication, encryption status and detailed health often require driver/backend/application telemetry.

A PVC-bound SLO alone does not prove that the volume is mounted, writable, performant, durable or backed up.

#### Failure modes and blast radius

- **Class misconfiguration:** can block many new claims across namespaces.
- **Provisioner outage:** primarily affects provisioning and related controller-managed operations; existing mounts may continue temporarily.
- **Node plugin failure:** can prevent mount operations on affected nodes.
- **Backend outage:** can affect both new operations and I/O from existing mounts.
- **Capacity/topology mismatch:** can leave claims pending or workloads unschedulable.
- **Incompatible sidecars:** can break reconciliation, attach, resize or snapshot operations.
- **Missing permissions:** can prevent provisioning/attach operations even if Pods are Running.
- **Stale attachment objects:** can block recovery or rescheduling.
- **Uncontrolled local disk use:** can cause node DiskPressure and affect unrelated workloads.

#### Runbook snippet

1. **Alert:** identify affected class, namespace, claim, nodes, and start time.
2. **Triage:** distinguish new provisioning, attachment, mount, backend I/O and application symptoms.
3. **Safe evidence collection:** current context; PVC/PV/StorageClass YAML; Pod events; driver/controller/node logs; `CSIDriver`, `CSINode`, `VolumeAttachment` where relevant; backend status.
4. **Mitigation:** use the approved driver/backend runbook; avoid deleting objects or forcing detach before data-safety checks.
5. **Validation:** prove new provisioning or mount works, then test application-level read/write and integrity.
6. **Follow-up:** record cause, timeline, data impact, capacity/compatibility changes, and prevention actions.

Capacity/cost controls must separate requested capacity from actual backend consumption. Thin provisioning may overcommit logical capacity; confirm backend semantics. Track unused retained PVs, quotas, class-level capacity, sidecar/controller resource overhead, local disk pressure and backup capacity. In local labs, disk is limited; check `df -h .` before each install or experiment.

### 2.8 Security lens

- **Supply chain:** verify official project/release source, image provenance, digest/signature policy where available, vulnerability handling and release notes.
- **ServiceAccount/RBAC:** inspect controller and node plugin identities and permissions. Grant only required API verbs and scope where feasible.
- **Privileged node components:** inspect `securityContext`, capabilities, host mounts, device access, host namespaces and node placement. The exact privilege needs vary by driver.
- **Secrets:** use fake credentials in labs. Avoid secrets in manifests, command arguments, source control, StorageClass parameters and shell history. Restrict Secret read access and references; rotate credentials.
- **Parameters and metadata:** do not place credentials in class parameters. Treat backend identifiers and topology as operationally sensitive where applicable.
- **Unapproved provisioners:** restrict StorageClass/CSIDriver creation through RBAC and admission controls; keep an approved catalog.
- **Tenant boundaries:** PVCs are namespaced but PVs, StorageClasses, CSI drivers and VolumeAttachments are cluster-scoped. Namespace separation alone does not secure a shared backend or privileged node plugin.
- **Logs:** review whether driver logs can include sensitive identifiers or credentials; redact before sharing.

Concrete checks:

```bash
kubectl get storageclass -o yaml
kubectl get csidriver -o yaml
kubectl get pods -A -o wide
kubectl get serviceaccounts,roles,rolebindings -A
kubectl get clusterroles,clusterrolebindings
kubectl get daemonsets,deployments,statefulsets -A -o yaml
kubectl auth can-i create storageclasses.storage.k8s.io
kubectl auth can-i update storageclasses.storage.k8s.io
```

These commands inspect or test permissions; their output does not by itself prove a complete security posture. This lesson does not secure the cluster, prove encryption at rest, validate a driver's supply chain independently, or create a full secrets-management system.

### 2.9 Production checklist

- [ ] A StorageClass catalog exists with an owner, purpose, status, and review date.
- [ ] The provisioner identity, CSI driver release, and sidecar versions are known and documented.
- [ ] Supported capabilities are evidenced from official driver documentation and a relevant test.
- [ ] Default StorageClass behavior is understood and unambiguous.
- [ ] Omitted `storageClassName` versus `storageClassName: ""` semantics are understood for the deployed version.
- [ ] `volumeBindingMode` is chosen intentionally and tested with workload scheduling constraints.
- [ ] Reclaim policy and actual backend deletion/retention behavior are understood.
- [ ] `allowedTopologies` and scheduling implications are reviewed against actual driver topology keys.
- [ ] Expansion, snapshots, clones, access modes, block mode and RWX are not promised without evidence.
- [ ] Driver, sidecar and Kubernetes compatibility is checked against official matrices.
- [ ] Controller and node plugin health/logs are observable and ownership is clear.
- [ ] RBAC, secrets, privileged containers, host mounts and image provenance are reviewed.
- [ ] Capacity, quotas, backend overcommit and SLOs are defined.
- [ ] Upgrade, rollback, migration and deprecation plans exist, including irreversible backend changes.
- [ ] A policy restricts production PVCs to approved classes and limits class creation/update.
- [ ] The distinction between API objects and backend bytes is in the runbook.
- [ ] Lab cleanup and no-production-use limitations are documented.
- [ ] Backup and restore are owned separately; a working CSI driver is not a backup strategy.

### 2.10 Hands-on lab set

**Shared lab rules:** use a disposable `kind` cluster and a dedicated namespace such as `m05-storageclass-lab`. Every lab should fit the laptop budget; do not run multiple storage stacks together. Check `df -h .` and the host/WSL2 virtual disk before installing a driver. Commands below are templates where placeholders are shown. Expected output is representative and not executed here.

#### Lab A — Discover the cluster and StorageClass behavior

- **ID / goal:** A — discover actual class/provisioner/default behavior and compare omitted versus empty `storageClassName`.
- **Prerequisites:** `kind`, `kubectl`, cluster admin rights to inspect cluster-scoped classes; estimate 10–50 MiB incremental, excluding existing cluster.
- **Context guard:** run `kubectl config current-context`, `kind get clusters`, `kubectl get nodes -o wide`, and `df -h .`. Confirm the context is the intended disposable `kind-...` cluster.
- **Steps:**

```bash
set -euo pipefail
kubectl config current-context
kind get clusters
kubectl get nodes -o wide
df -h .
kubectl get sc
kubectl get sc -o yaml
kubectl get pvc -A -o wide
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Create a namespace and two claims. **File: `lab-a-class-selection.yaml` — compares an omitted class to an explicit empty class.** It does not hardcode any class name.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: m05-storageclass-lab
  labels:
    app.kubernetes.io/part-of: m05-storageclass-lab
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: class-omitted
  namespace: m05-storageclass-lab
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 64Mi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: class-empty
  namespace: m05-storageclass-lab
spec:
  storageClassName: ""
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 64Mi
```

Validate and apply only after reviewing the namespace and current context:

```bash
kubectl apply --dry-run=client -f lab-a-class-selection.yaml
kubectl apply -f lab-a-class-selection.yaml
kubectl get pvc -n m05-storageclass-lab -o wide
kubectl describe pvc class-omitted -n m05-storageclass-lab
kubectl describe pvc class-empty -n m05-storageclass-lab
kubectl get pv -o wide
kubectl get events -n m05-storageclass-lab
```

- **Expected evidence:** `class-omitted` may select the default class; `class-empty` explicitly requests no class and may remain Pending without a matching static PV. Exact behavior for omitted-class retroactive assignment and multiple defaults is **[VERIFY]** for the installed version.
- **Cleanup:** see the named cleanup procedure at the end of Section 2.10.
- **Re-run safety:** inspect existing claims and PVs before reapplying; do not assume the prior data is disposable.
- **Stretch:** write a one-page explanation of the discovered default and provisioner.
- **Disk estimate:** 10–50 MiB incremental, class/backend dependent.
- **kind caveat:** a local-path class does not prove production durability, snapshots, expansion or topology.

#### Lab B — Install the official CSI hostpath test/reference driver

- **ID / goal:** verify driver components and use the selected release's documented StorageClass.
- **Prerequisites:** compatible release identified from official documentation; Git; disposable cluster; estimate 100–500 MiB or more depending on images/manifests **[VERIFY]**.
- **Context guard:** verify current context, kind cluster, node status and free disk. Confirm no other workload depends on the driver installation.
- **Steps:** follow the official repository `https://github.com/kubernetes-csi/csi-driver-host-path` README and release instructions. Select `<VERIFIED_RELEASE_TAG>` from official release/compatibility information; inspect the exact manifests/scripts before applying. Do not invent a tag, install URL, labels or provisioner name.
- **Verification commands:**

```bash
kubectl get pods -A -o wide
kubectl get deployments,statefulsets,daemonsets -A
kubectl get crd
kubectl get csidriver
kubectl get csinode -o yaml
kubectl get storageclass -o yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Use output and selected release manifests to discover controller/node plugin names and labels, then inspect the exact Pods:

```bash
kubectl describe pod <DISCOVERED_CONTROLLER_POD> -n <DISCOVERED_NAMESPACE>
kubectl logs <DISCOVERED_CONTROLLER_POD> -n <DISCOVERED_NAMESPACE> --all-containers=true
kubectl describe pod <DISCOVERED_NODE_PLUGIN_POD> -n <DISCOVERED_NAMESPACE>
kubectl logs <DISCOVERED_NODE_PLUGIN_POD> -n <DISCOVERED_NAMESPACE> --all-containers=true
```

- **Expected evidence:** driver Pods ready, driver registration objects present where expected, StorageClass/provisioner identity matched to the official selected release, and no unresolved install errors.
- **Cleanup:** follow the selected release's uninstall procedure. Remove only resources created exclusively for this lab. Do not casually delete CRDs, shared CSI components, or StorageClasses used by other workloads.
- **Re-run safety:** inspect existing installation ownership and resources first; avoid installing a second copy over an existing driver.
- **Stretch:** create a class catalog record with every unverified capability marked unknown.
- **Disk estimate:** 100–500 MiB or more; check actual image layers before installation.
- **kind caveat:** this is a test/reference driver. It does not prove cloud durability, replication, zone failure behavior, or production performance.

#### Lab C — Compare `Immediate` and `WaitForFirstConsumer`

- **ID / goal:** observe binding and scheduling differences using the selected hostpath release's documented provisioner.
- **Prerequisites:** Lab B complete; the selected release's class parameters/provisioner confirmed; estimate 50–200 MiB.
- **Context guard:** verify context, namespace, node status and free disk. Do not run against a shared or production CSI controller.
- **Manifests:** create two StorageClasses using the exact documented provisioner and parameters, differing only in `volumeBindingMode`. Do not invent the driver string. The following shows the generic shape and requires the documented identity to be inserted.

**File: `lab-c-binding-modes.yaml` — StorageClass/PVC comparison template; resolve placeholders first.**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: m05-hostpath-immediate
  labels:
    app.kubernetes.io/part-of: m05-storageclass-lab
provisioner: "<DOCUMENTED_CSI_PROVISIONER_NAME>"
reclaimPolicy: Delete
volumeBindingMode: Immediate
parameters: {}
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: m05-hostpath-wffc
  labels:
    app.kubernetes.io/part-of: m05-storageclass-lab
provisioner: "<DOCUMENTED_CSI_PROVISIONER_NAME>"
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
parameters: {}
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: immediate-claim
  namespace: m05-storageclass-lab
spec:
  storageClassName: m05-hostpath-immediate
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 64Mi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: wffc-claim
  namespace: m05-storageclass-lab
spec:
  storageClassName: m05-hostpath-wffc
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 64Mi
```

This template is not directly runnable until the provisioner and any required documented parameters are resolved. Apply only after validation and inspection. Observe claim status before and after creating consumer Pods. A minimal consumer can be added after confirming that the selected driver supports the requested mode:

**File: `lab-c-consumers.yaml` — consumers for the two claims.**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: immediate-consumer
  namespace: m05-storageclass-lab
spec:
  restartPolicy: Never
  containers:
    - name: check
      image: busybox:1.36
      command: ["/bin/sh", "-c", "echo immediate > /data/proof.txt; sleep 300"]
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
        claimName: immediate-claim
---
apiVersion: v1
kind: Pod
metadata:
  name: wffc-consumer
  namespace: m05-storageclass-lab
spec:
  restartPolicy: Never
  containers:
    - name: check
      image: busybox:1.36
      command: ["/bin/sh", "-c", "echo wffc > /data/proof.txt; sleep 300"]
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
        claimName: wffc-claim
```

Inspect:

```bash
kubectl get pvc,pod -n m05-storageclass-lab -o wide
kubectl describe pvc immediate-claim -n m05-storageclass-lab
kubectl describe pvc wffc-claim -n m05-storageclass-lab
kubectl describe pod immediate-consumer -n m05-storageclass-lab
kubectl describe pod wffc-consumer -n m05-storageclass-lab
kubectl get pv -o yaml
kubectl get events -n m05-storageclass-lab
```

- **Expected evidence:** the immediate claim may provision before a consumer is scheduled; the delayed claim typically waits for a consumer's scheduling context. Exact timing depends on the provisioner and driver.
- **Cleanup:** use the named cleanup procedure below.
- **Re-run safety:** inspect old claims and backing resources before reusing class names.
- **Stretch:** create a consumer with an intentionally impossible node selector in a disposable environment, observe scheduling failure, then remove the constraint and explain why WFFC did not solve it.
- **Disk estimate:** 50–200 MiB incremental.
- **kind caveat:** this tests binding/scheduling mechanics, not real multi-zone placement. Do not claim the hostpath driver implements topology unless its selected release documents it.

> **DATA-SAFETY PREFACE — THROWAWAY LAB ONLY:** The following cleanup may delete disposable PVCs and their backing data. Confirm the current context, exact namespace, claim names, and driver installation ownership. Capture evidence first. Never run against production.

#### Lab D — Trace CSI objects and simulate controller/provisioner failure

- **ID / goal:** trace the object chain and understand which operations fail when a dedicated test controller is unavailable.
- **Prerequisites:** Lab B installed with a separately scalable dedicated controller component; exact resource discovered; estimate 50–200 MiB.
- **Context guard:** verify current context, node status and disk. Confirm the controller belongs only to this lab and is not shared.
- **Before failure:** create a disposable claim and Pod, capture PVC/PV/Pod YAML, events, controller/node logs, and the original replica count for the actual controller Deployment/StatefulSet. Verify the Pod is mounted and record a simple read/write result.
- **Find the component:** use `kubectl get deployments,statefulsets,daemonsets -A` and compare against the selected release manifests. Do not guess labels or names.
- **Failure simulation:** if the selected package exposes a dedicated, lab-owned controller Deployment or StatefulSet that can safely be scaled, use a reviewed command against the exact resource only after recording its original replica count. If the controller is packaged differently or not safely separable, do not mutate it; use the conceptual alternative below.

**DATA-SAFETY PREFACE — THROWAWAY LAB ONLY:** Scaling a controller can disrupt storage operations for every workload using that controller. Proceed only in a disposable cluster with dedicated lab-owned resources and disposable claims. Do not do this on a shared or production cluster. Record the exact resource and original replica count; never guess the count.

```bash
# Replace placeholders only after inspecting the actual resource.
kubectl config current-context
kubectl get deployment <DISCOVERED_CONTROLLER_DEPLOYMENT> -n <DISCOVERED_NAMESPACE> -o yaml
# Record .spec.replicas from the actual output before changing it.
kubectl scale deployment/<DISCOVERED_CONTROLLER_DEPLOYMENT> \
  -n <DISCOVERED_NAMESPACE> --replicas=0
```

Observe whether new provisioning waits/fails, and whether the already-mounted disposable Pod continues. Outcomes are driver-specific; never infer a universal guarantee. Inspect Events and controller/node logs. Do not delete `VolumeAttachment`, PV, PVC, or backend data as a shortcut.

Restore the exact original count recorded before the change, even if the experiment fails:

```bash
# Replace <ORIGINAL_REPLICAS> and placeholders with the recorded values.
kubectl scale deployment/<DISCOVERED_CONTROLLER_DEPLOYMENT> \
  -n <DISCOVERED_NAMESPACE> --replicas=<ORIGINAL_REPLICAS>
kubectl rollout status deployment/<DISCOVERED_CONTROLLER_DEPLOYMENT> \
  -n <DISCOVERED_NAMESPACE> --timeout=180s
kubectl get pods -n <DISCOVERED_NAMESPACE> -o wide
```

If the component is a StatefulSet, use the matching StatefulSet commands and restore its recorded original count. If any command fails, use a separate terminal to restore the original count and verify readiness before continuing. This is a human-operated recovery path; do not place the failure and restore into a script that can exit before restoration without a trap.

**Conceptual alternative:** if the selected hostpath release does not expose a safely scalable dedicated controller, draw the failure chain and review logs/events from a known test incident or official issue. Do not invent a component or deliberately break shared storage.

- **Expected evidence:** original/current replica count, controller Pod state before/during/after, new claim event behavior, existing Pod read/write result, and restored readiness.
- **Cleanup:** do not delete attachment objects. Clean only the explicitly named disposable claim/Pod and follow the driver's documented cleanup.
- **Re-run safety:** verify the controller's original replica count and ownership anew for each attempt.
- **Stretch:** write a runbook distinguishing controller, node-plugin and backend outage symptoms.
- **Disk estimate:** 50–200 MiB incremental.
- **kind caveat:** no real failure-domain or production backend behavior is proven. The observed behavior is specific to the selected driver/release.

#### Optional Lab E — StorageClass catalog and capability decision record

- **Goal:** compare the discovered local-path class and the CSI hostpath class based on evidence.
- **Prerequisites:** Labs A and B; estimate 10–50 MiB.
- **Steps:** populate the capability matrix in Section 2.5, mark unobserved capabilities `[VERIFY]`, and create a decision record for a hypothetical PostgreSQL metadata PVC, ETL scratch, and shared artifact workload.
- **Expected evidence:** class YAML, provisioner identity, a capability matrix with source references, and decision record.
- **Cleanup:** no additional resources required beyond prior labs.
- **Re-run safety:** update observations rather than overwriting unresolved unknowns with assumptions.
- **Stretch:** define acceptance tests and an owner for each class.
- **kind caveat:** a local test cannot prove production performance, encryption, replication, or disaster recovery.

#### Named cleanup and disk verification

> **⚠ DESTRUCTIVE — DATA LOSS:** The next command deletes the named lab namespace and its namespaced Pods/PVCs. Depending on reclaim policy and provisioner behavior, backing data may be deleted or retained. First capture evidence and verify the current context, exact namespace contents, and that all data is disposable.

```bash
set -euo pipefail
kubectl config current-context
kubectl get all,pvc -n m05-storageclass-lab
kubectl get pv -o wide
# Run only if this namespace contains only disposable lab resources:
kubectl delete namespace m05-storageclass-lab
kubectl get namespace m05-storageclass-lab
kubectl get pv -o wide
```

Do not use `--force` or remove finalizers just because cleanup is delayed. Investigate remaining Pods, claims, PVs, finalizers and driver/backend state. Driver uninstall commands must come from the exact release documentation and must not delete shared CRDs or resources.

Check disk again with `df -h .`. In WSL2, removing files inside the virtual disk does not always shrink the host-side virtual disk file automatically; check host and WSL2 disk usage separately. Check Docker/Podman images and kind node containers before pruning anything. Do not use broad prune commands without inspecting their scope.

### 2.11 Self-check questions

1. **Why use dynamic provisioning instead of manually creating every PV?**  
   **Answer:** It automates repeated provisioning and supports self-service through approved classes. It still requires class governance, capacity control and backend validation. Wrong answer: “dynamic means no operator responsibility.”

2. **What is the difference between omitted `storageClassName` and `storageClassName: ""`?**  
   **Answer:** Omission participates in default-class selection under current Kubernetes rules; empty explicitly requests no class. Exact default/retroactive behavior is version-sensitive. Wrong answer: “empty means use the default.”

3. **When is `WaitForFirstConsumer` useful, and what can still go wrong?**  
   **Answer:** It delays binding/provisioning so consumer scheduling constraints can inform topology placement. Impossible affinity, insufficient resources, selectors, capacity and unsupported topology can still block scheduling. Wrong answer: “it fixes all Pending PVCs.”

4. **What does the CSI controller do that the node plugin does not?**  
   **Answer:** Controller-side operations coordinate provisioning and other control-plane capabilities; the node plugin handles node-side stage/publish/mount operations. Exact operations vary by driver. Wrong answer: “controller readiness proves mounts work.”

5. **What do `CSIDriver`, `CSINode`, and `VolumeAttachment` represent?**  
   **Answer:** Driver integration settings, node-level CSI registration/capability information, and attach/detach coordination for attachable volumes respectively. Wrong answer: “every volume has a VolumeAttachment.”

6. **Why is a capability matrix better than trusting a class name?**  
   **Answer:** API possibility, driver support and backend configuration are different. Evidence must cover modes, snapshots, expansion, topology, encryption, replication and performance. Wrong answer: “`fast-rwx` proves fast shared storage.”

7. **What might happen if the CSI controller is down?**  
   **Answer:** New provisioning and controller-managed operations may stall; already-mounted workloads may continue temporarily, but no universal guarantee exists. Wrong answer: “all current Pods are safe” or “all mounts immediately fail.”

8. **Can a StorageClass change migrate existing PVs in place?**  
   **Answer:** Not as a universal mechanism. Existing PVs retain their provisioned backend/properties; migration usually uses a new claim and data migration/replication/restore. Wrong answer: “patch the class and every disk changes.”

9. **Why must CSI node plugins be security-reviewed?**  
   **Answer:** Depending on driver, they may require privileged context and host mounts, increasing node-level blast radius. Review images, RBAC, service accounts, host access, secrets and upgrades. Wrong answer: “CSI drivers are isolated like ordinary application Pods.”

10. **Does a successful CSI hostpath lab prove production durability?**  
    **Answer:** No. It tests integration behavior only. Production durability requires backend design, failure-domain evidence, security configuration, backups and restore tests. Wrong answer: “a Bound PVC is a backup.”

### 2.12 Evidence artifacts

Save these artifacts yourself; they do not exist until you collect them:

- `evidence/context-and-disk.txt`: current context, kind clusters, nodes, and before/after free-disk checks.
- `evidence/storageclasses-before.yaml`: discovered StorageClass YAML and default annotations.
- `evidence/provisioner-identity.md`: exact provisioner and driver identity, with source/release reference.
- `evidence/lab-a-pvc-before-after.txt`: PVC/PV status and Events for omitted versus empty class selection.
- `evidence/hostpath-release-selection.md`: selected official release, compatibility source, install instructions reviewed and unresolved `[VERIFY]` items.
- `evidence/csi-components.txt`: controller/node Pods, Deployment/StatefulSet/DaemonSet status, `CSIDriver` and `CSINode` YAML.
- `evidence/volumeattachment.yaml`: relevant attachment objects where applicable, or a written explanation of why none is expected.
- `evidence/binding-modes.txt`: PVC/PV state and events before and after consumer scheduling.
- `evidence/controller-failure-timeline.md`: original replica count, timeline, observed effects, restoration and readiness proof.
- `evidence/capability-matrix.md`: source-backed capabilities with `[VERIFY]` flags.
- `evidence/storageclass-decision-record.md`: workload requirements, trade-offs, owner, cost/capacity and backup plan.
- `evidence/audit-storage-platform.sh` and `evidence/audit-output.txt`: read-only audit script and captured output.
- `evidence/cleanup-confirmation.txt`: namespace, claims, PVs, driver resources and disk checks after cleanup.

Do not mark an artifact as collected or a lab as passed unless you actually ran it and saved the evidence.

### 2.13 Common interview and design-review questions

1. **Design question: How would you provide three storage classes for a data platform?**  
   **Model answer:** Start from workload contracts, not labels. Define standard persistent state, retained state and shared filesystem only if needed. For each class document provisioner, driver/version, modes, topology, performance/durability evidence, reclaim policy, expansion/snapshot support, quota, encryption, owner and restore process. Enforce approved classes for production and canary-test new configurations. The names `standard-delete`, `fast-retain` and `shared-rwx` are illustrative until the backend proves the properties.

2. **CSI incident: New PVCs are Pending after a driver upgrade, but existing Pods still run. What do you do?**  
   **Model answer:** Treat the split as a clue, not proof. Capture PVC events, StorageClass YAML, controller/provisioner status and logs, driver/sidecar versions, and backend status. Verify the provisioner identity and compatibility matrix. Avoid deleting claims. Restore a known-good controller configuration or use the tested rollback plan, then validate new provisioning and application I/O.

3. **Topology question: Why can `WaitForFirstConsumer` help, and why might the PVC still remain Pending?**  
   **Model answer:** It allows scheduling constraints to influence provisioning for topology-aware storage. It cannot overcome impossible affinity, insufficient resources, invalid selectors, missing capacity, or unsupported topology. Inspect Pod scheduling events and class/driver topology keys. A kind cluster does not reproduce real independent zones.

4. **Upgrade/migration question: A new driver version changes supported parameters. How do you migrate?**  
   **Model answer:** Read official release/compatibility notes, test in staging, create a new class, provision a new claim, and use supported snapshot/clone, application replication or a reviewed copy method. Validate data and cut over with a rollback window. Existing PVs do not automatically change backend properties when a StorageClass changes. Verify whether CRD/API changes and backend changes are reversible.

5. **Security/governance question: How do you prevent teams from creating unapproved StorageClasses?**  
   **Model answer:** Use RBAC to restrict cluster-scoped class and driver resource mutations, admission policy to validate production PVC class selection and required metadata, and a catalog/audit to flag unowned or deprecated classes. Review driver images, privileged node-plugin settings, host mounts, service accounts and secrets. Policy enforcement must be tested and does not replace backend capability evidence.

### 2.14 Sources and verification notes

#### Official source references

No live web or documentation consultation and no cluster execution were performed while writing this lesson. These are canonical official entry points to check; the exact content and release-specific instructions must be verified before use.

- Kubernetes documentation — **Storage Classes**: https://kubernetes.io/docs/concepts/storage/storage-classes/ — StorageClass fields, default class, binding mode, parameters and topology.
- Kubernetes documentation — **Persistent Volumes**: https://kubernetes.io/docs/concepts/storage/persistent-volumes/ — PVC/PV binding, provisioning and reclaim concepts.
- Kubernetes documentation — **CSI**: https://kubernetes.io/docs/concepts/storage/volumes/#csi — CSI volume integration overview; verify current page structure.
- Kubernetes documentation — **Storage Capacity**: https://kubernetes.io/docs/concepts/storage/storage-capacity/ — capacity-aware scheduling concepts and supported workflow.
- Kubernetes API reference — **StorageClass**: https://kubernetes.io/docs/reference/kubernetes-api/config-and-storage-resources/storage-class-v1/ — field types and API behavior.
- Kubernetes API reference — **CSIDriver**: https://kubernetes.io/docs/reference/kubernetes-api/config-and-storage-resources/csi-driver-v1/ — driver configuration fields such as `fsGroupPolicy`; verify current reference.
- Kubernetes API reference — **CSINode**: https://kubernetes.io/docs/reference/kubernetes-api/config-and-storage-resources/csi-node-v1/ — node driver registration data.
- Kubernetes documentation — **Volume Snapshots**: https://kubernetes.io/docs/concepts/storage/volume-snapshots/ — snapshot APIs and controller relationship; snapshots are deferred to Unit 3.
- Kubernetes CSI project documentation: https://kubernetes-csi.github.io/docs/ — sidecar and CSI integration documentation.
- Official Kubernetes CSI hostpath test/reference driver: https://github.com/kubernetes-csi/csi-driver-host-path — release-specific install, deployment shape, class example and supported test capabilities.
- CSI specification: https://github.com/container-storage-interface/spec — CSI Identity, Controller and Node service concepts.
- kind documentation: https://kind.sigs.k8s.io/docs/user/quick-start/ — local cluster setup and runtime details.

#### `[VERIFY]` register

| Claim | Why version/backend-sensitive | Official source/check | Blocks execution? | Status |
|---|---|---|---|---|
| Default annotation and multiple-default behavior | Kubernetes version and cluster configuration | Kubernetes Storage Classes docs; inspect `kubectl get sc -o yaml` | Yes, before relying on omitted class | OPEN — `[VERIFY]` |
| Omitted vs empty `storageClassName` and retroactive assignment | Version-sensitive defaulting behavior | Storage Classes docs and API reference; test in disposable cluster | Yes, before class-selection conclusions | OPEN — `[VERIFY]` |
| Valid StorageClass fields and immutability | API version and field-specific rules | StorageClass API reference; `kubectl explain storageclass.spec` | Yes, before changing a class | OPEN — `[VERIFY]` |
| CSI hostpath installation and compatible release | Release-specific manifests, sidecars and Kubernetes compatibility | Official `csi-driver-host-path` README/releases | Yes, before installation | OPEN — `[VERIFY]` |
| Controller/node plugin resource names and deployment shape | Packaging can vary by release | Selected release's exact manifests and docs | Yes, before logs/scaling/cleanup | OPEN — `[VERIFY]` |
| Sidecar/Kubernetes compatibility | Multiple independently versioned components | Official CSI sidecar docs and driver's compatibility matrix | Yes, before upgrades | OPEN — `[VERIFY]` |
| CSI access mode and `VolumeAttachment` behavior | Driver/backend/volume path and Kubernetes version | Kubernetes PV docs, CSI driver docs and observed objects | Yes, before access-mode design | OPEN — `[VERIFY]` |
| `CSIDriver.spec.fsGroupPolicy` | API and driver/filesystem behavior | CSIDriver API reference and driver docs | Yes, before permission guarantees | OPEN — `[VERIFY]` |
| `CSIStorageCapacity` maturity and enablement | API maturity, feature settings, scheduler/provisioner support | Kubernetes Storage Capacity docs and driver integration docs | Yes, before capacity-aware claims | OPEN — `[VERIFY]` |
| CSI migration status for named in-tree plugins | Plugin-specific and version-sensitive | Current Kubernetes CSI migration documentation | Yes, before migration statements | OPEN — `[VERIFY]`; no blanket status claimed |
| Snapshots, clones, expansion, topology, RWX, block mode | Driver/backend/sidecar/CRD capability varies | Official driver capability matrix and test evidence | Yes, before promising feature | OPEN — `[VERIFY]` |
| Encryption at rest and replication/durability | Backend architecture and configuration | Backend official docs, platform configuration and restore evidence | Yes, before security/durability claims | OPEN — `[VERIFY]` |
| `allowedTopologies` key semantics | Driver and backend topology keys | StorageClass docs and selected driver docs | Yes, for topology-constrained class | OPEN — `[VERIFY]` |
| Reclaim policy backend effects | Provisioner and backend cleanup implementation | Kubernetes PV docs, driver docs and disposable test | Yes, before destructive use | OPEN — `[VERIFY]` |
| Driver install disk footprint | Images and selected release vary | Inspect images/manifests; check `df -h .` | Yes, if near disk limit | OPEN — `[VERIFY]` |
| Policy engine syntax/API | Kubernetes and policy engine versions | Official policy-engine docs and API reference | Yes, before enforcement | OPEN — `[VERIFY]` |

#### AI self-audit

This is an **AI self-audit**, not an independent human review, a live documentation audit, or a successful runtime test.

- **Audit A — Roadmap completeness:** PASS for sections 2.0–2.14 in order; the four learning levels; all four mandatory lab components; required comparison tables; SRE/security lenses; checklist; 10 self-check questions; evidence artifacts; and exactly five senior interview/design questions.
- **Audit B — Technical authenticity:** PASS for distinguishing CSI interface from backend, API possibilities from driver/backend capabilities, controller from node roles, and conditional `VolumeAttachment` behavior. OPEN — `[VERIFY]` for release/version/backend-sensitive items in the register.
- **Audit C — Lab safety:** PASS for context guards, named namespace, explicit destructive warnings, placeholder use instead of invented release/provisioner details, resource discovery, and controller restoration instructions. OPEN — `[VERIFY]` for exact hostpath install and cleanup steps until a compatible release is selected and its official instructions are inspected.
- **Audit D — Production readiness and scope:** PASS for catalog ownership, SLOs, capacity, security, upgrades, migration, Unit 1 references, and boundaries to Units 3, 7 and 8. No other repository file was generated or modified by this lesson.
- **Unresolved verification areas:** 15 grouped entries in the register remain `OPEN — [VERIFY]`; they must be checked for the actual Kubernetes version, driver release, sidecars, backend and policy engine.
- **Adversarial review:** The lesson explicitly addresses wrong default-class assumptions, invalid driver parameters, topology deadlocks, unsafe controller scaling, accidental claim/backend deletion, stale attachment cleanup, unsupported capability claims, secret exposure, privileged node-plugin risk and untested rollback.
- **Execution status:** No labs or manifests were executed here. The learner must test all procedures in their own disposable `kind` cluster and record the resulting evidence before treating a capability or procedure as verified.
