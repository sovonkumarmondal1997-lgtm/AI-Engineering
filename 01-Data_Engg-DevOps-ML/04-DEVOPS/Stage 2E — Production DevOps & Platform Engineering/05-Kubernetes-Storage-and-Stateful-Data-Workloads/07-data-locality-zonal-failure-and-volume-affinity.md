# Data Locality, Zonal Failure, and Volume Affinity

> **Stage:** 2E — Production DevOps & Platform Engineering  
> **Module:** M05 — Kubernetes Storage and Stateful Data Workloads  
> **Unit:** 7 of M05  
> **Audience:** Learners who have completed M05 Units 1–6  
> **Environment:** Zero-budget `kind` lab on WSL2 Ubuntu or native Linux  
> **Safety priority:** Protect data before restoring scheduling or availability.

**Evidence labels used in this lesson**

- **Roadmap requirement** — a required Unit 7 learning outcome.
- **Engineering context** — general design guidance that must be adapted to the workload.
- **[VERSION-SENSITIVE]** — behavior or fields that can vary by Kubernetes version.
- **[VERIFY: …]** — check the named official document and the exact Kubernetes/CSI/provider version before applying the guidance.
- **[ILLUSTRATIVE]** — example output or scenario, not a result observed in your environment.
- **[ASSUMPTION]** — a stated premise used to make an example concrete.

> **Data-safety preface:** Do not use a production cluster for this lesson. Do not force-delete Pods, delete PVCs/PVs, patch PV finalizers, or remove node-local data to “fix” a scheduling problem. First establish the cluster context, resource ownership, data location, replication/backup status, and recovery path. All disruptive commands in this lesson are limited to a disposable local `kind` cluster.

## 7.0 Why this matters in production

Imagine a database Pod that was running correctly yesterday. A node-pool upgrade replaces a node, or a cloud zone becomes unavailable. Kubernetes sees healthy API objects and tries to schedule the Pod elsewhere. The Pod remains `Pending`, because its PersistentVolume (PV) is tied to a node or zone that the new placement cannot access.

This is not necessarily a Kubernetes defect. The scheduler must respect storage topology. Starting the Pod on an incompatible node could fail to attach or mount the volume, or could violate the storage backend's access guarantees. A scheduler that refuses an impossible placement can be protecting data integrity.

A common production sequence is:

1. A StatefulSet has three database Pods and three claims.
2. Each claim is bound to a zonal block volume.
3. A maintenance operation removes a node pool or an entire zone loses capacity.
4. The controller recreates a missing Pod.
5. The replacement Pod is eligible for other nodes, but its already-bound volume is available only in the original zone.
6. Scheduling or attach/mount fails. The Pod remains unavailable until the zone returns, the volume can safely reattach, or the database is recovered using another replica or a documented recovery process.

The important distinction is between **compute placement** and **data placement**. Kubernetes can create a replacement Pod; it does not automatically copy a database's files to a different zone. A StatefulSet provides stable identities and claim templates, not database replication. A PVC is a request for storage, not a cross-zone durability promise.

Scheduling and storage provisioning must therefore be designed together. The StorageClass's binding mode, CSI driver's topology support, PV node affinity, Pod scheduling constraints, available storage capacity, application replication, and recovery plan jointly determine whether a stateful workload can survive a failure.

**Unit boundary:** This lesson explains topology and first-response reasoning. M03 covers the wider scheduling toolkit; M04 covers Services, DNS, and NetworkPolicy; M05 Unit 2 covers StorageClasses and CSI; Unit 4 covers StatefulSets; Unit 5 covers database operators such as CloudNativePG; Unit 6 covers I/O performance. Unit 8 goes deeper into storage troubleshooting and orphaned volumes. Formal disaster recovery and multi-cluster design belong to M13/M14; cost trade-offs are revisited in M15.

## 7.1 Learning objectives

After completing the lesson and lab, you should be able to:

1. Explain node, rack, zone, and region as distinct failure domains.
2. Describe data locality and data gravity, and explain why storage location can constrain compute placement.
3. Read PV `spec.nodeAffinity` and recognize topology labels such as `topology.kubernetes.io/zone` and `kubernetes.io/hostname`.
4. Diagnose a `Pending` Pod using read-only inspection of Pods, PVCs, PVs, StorageClasses, node labels, and events.
5. Compare `Immediate` with `WaitForFirstConsumer`, and explain when immediate provisioning can create a topology mismatch.
6. Explain `allowedTopologies` and its interaction with scheduling constraints.
7. Reason about volume binding alongside node affinity, taints/tolerations, Pod affinity/anti-affinity, and topology spread constraints.
8. Explain the availability and durability limits of local PVs.
9. Design replicas across zones with application-level replication and appropriately placed volumes.
10. Compare zonal block volumes, regional/replicated storage, shared network filesystems, and node-local PVs at an awareness level.
11. Explain topology spread policy, synchronous/asynchronous replication, quorum, rebalancing, reattachment, and `Multi-Attach` errors.
12. Run the mandatory `kind` simulation, gather evidence, and label its fidelity limits.
13. Produce a design review, failure matrix, audit result, and verification checklist for a real backend.

## 7.2 Concept map and vocabulary

### Failure domains

A **failure domain** is a set of components that may fail together because they share a dependency or physical boundary.

- **Node:** one machine or VM. A kernel panic, VM deletion, disk failure, or container-runtime issue can affect workloads on it.
- **Rack:** a physical rack or closely coupled infrastructure group. Power, top-of-rack networking, or cooling failures can affect multiple nodes.
- **Zone:** a provider-defined failure domain within a region. The exact independence and services available in a zone are provider-specific.
- **Region:** a broader geographic and service boundary. Regional network, control-plane, identity, or provider incidents can affect multiple zones.

Failure domains are not automatically independent. Two Pods in different zones may still depend on the same regional control plane, credentials, network route, DNS, or upstream service.

### Storage and scheduling vocabulary

- **PersistentVolume (PV):** a cluster-scoped Kubernetes object representing a provisioned storage resource.
- **PersistentVolumeClaim (PVC):** a namespaced request for storage by a workload.
- **StorageClass:** a cluster-scoped description of how dynamic storage should be provisioned, including a provisioner, parameters, reclaim policy, and binding mode.
- **Container Storage Interface (CSI) driver:** software implementing the CSI interface to connect Kubernetes storage operations to a backend. Support and topology semantics are driver-specific.
- **Provisioner:** the component responsible for creating storage for a claim; for CSI, this commonly includes the CSI external-provisioner sidecar and driver components.
- **PV `nodeAffinity`:** a PV field that restricts which nodes may use that PV. For topology-constrained storage, it often represents the zone or node where the volume is accessible.
- **Topology labels:** node labels describing placement domains. Common labels include `topology.kubernetes.io/zone` and `kubernetes.io/hostname`. The labels' values and presence must be inspected, not assumed.
- **`allowedTopologies`:** a StorageClass field restricting topologies in which dynamically provisioned volumes may be created. The provisioner must understand the topology keys and constraints.
- **`volumeBindingMode`:** the StorageClass setting that controls when a PVC binds or is dynamically provisioned.
- **`Immediate`:** the default binding mode when not specified; binding/provisioning begins without waiting for a consuming Pod's scheduling constraints.
- **`WaitForFirstConsumer` (WFFC):** delays binding/provisioning until a Pod references the PVC, allowing scheduling constraints to inform volume placement.
- **Topology spread constraint:** a Pod scheduling rule that attempts to distribute matching Pods across topology domains.
- **Node affinity:** a Pod scheduling rule that attracts or restricts placement to nodes matching labels.
- **Taint/toleration:** a node taint repels Pods unless their Pod spec has a matching toleration; a toleration allows consideration but does not force placement.
- **Local PV:** a PV backed by storage local to a particular node and represented with required node affinity. The node's loss may make the data inaccessible or lost.
- **Zonal block volume:** a block-storage volume accessible within a provider-defined zone or topology segment; details depend on the backend.
- **Regional/replicated storage:** storage whose backend maintains copies or provides access across a wider failure domain. “Regional” does not mean every failure is tolerated; implementation and consistency guarantees vary.
- **Shared network filesystem:** a filesystem accessed over a network by multiple clients. Shared access alone does not provide database replication, transaction consistency, or high availability.
- **Attach/detach:** operations that make a volume available to a node and later release it, where the backend/driver requires attachment.
- **`VolumeAttachment`:** a cluster-scoped Kubernetes storage object representing the intent to attach or detach a volume to/from a node for drivers that use this mechanism.
- **`Multi-Attach`:** a common error label when a volume with restrictive attachment semantics is already attached to another node or cannot safely be attached to the requested node. Exact conditions are backend-specific.
- **Replica:** an application-level copy or member of a replicated system. A Pod replica is not necessarily a data replica.
- **Quorum:** the minimum participating set required by a distributed system to make a defined decision safely.
- **Synchronous replication:** a write is acknowledged only after a configured remote durability condition is met. The exact acknowledgment boundary varies.
- **Asynchronous replication:** writes may be acknowledged before remote replicas have received them, creating a potential replication lag and nonzero data-loss window.
- **Recovery Point Objective (RPO):** the tolerated amount of data loss, usually expressed as a time window.
- **Recovery Time Objective (RTO):** the target time to restore a service to an agreed operating state.

### Topology relationship diagram

```text
Application / StatefulSet
        |
        +-- Pod db-0 -------------------- Node A (zone-a)
        |                                   |
        |                                   +-- PV volume-a
        |                                         ^ nodeAffinity:
        |                                           zone-a / node A
        |
        +-- PVC data-db-0 ------------------------+
                    |
                    +-- bound to PV volume-a

Replacement Pod db-0 is considered for Node B (zone-b)
        |
        +-- Scheduler checks Pod constraints AND PV accessibility
                    |
                    +-- PV requires zone-a
                    +-- Node B is zone-b
                    |
                    +-- incompatible placement => Pod cannot run there
```

Plain-English interpretation: the claim identifies the storage request, the PV records the bound storage, and the PV's affinity/topology requirements restrict eligible nodes. A controller can recreate the Pod without relocating the underlying data. If no eligible node can access the volume, `Pending` is an expected result.

### Which component influences which decision?

| Component/object | What it contributes | What it does not guarantee |
|---|---|---|
| StatefulSet/controller | Stable ordinal identity and Pod recreation | Database replication, cross-zone data copy, quorum |
| Scheduler | Chooses a node satisfying resource and scheduling constraints, including volume binding integration | That a database can safely promote a replica |
| PVC/PV | Request and binding relationship to storage | Cross-zone access unless backend supports it |
| StorageClass | Provisioning policy and binding mode | A specific provider's resilience unless documented |
| CSI driver/backend | Creates, attaches, mounts, and reports storage according to its capabilities | Behavior beyond its published contract |
| Topology spread | Shapes Pod placement across labeled domains | Independent data copies or sufficient capacity in each domain |
| Database/operator | May coordinate replication, failover, and recovery | Correctness unless configured, tested, and monitored |

## 7.3 Level 1 — Beginner: topology and locality

### From node to region

A node failure can be caused by a VM being deleted or a kernel crash. A rack failure can affect several nodes together. A zone outage can remove many nodes and zonal storage endpoints at once. A regional event can affect all zones in that region and shared regional services.

The larger the failure domain, the more independent capacity and recovery planning is usually required. But adding replicas is not enough unless replicas are actually placed in independent domains and the application can continue safely after a failure.

### Data locality and data gravity

**Data locality** means placing compute near the data it reads or writes. It can reduce network transfer and latency, and can improve throughput. **Data gravity** is the tendency for large or important datasets to attract compute and dependent services because moving the data is expensive, slow, or operationally risky.

For an ETL job, compute may be scheduled near a dataset to reduce cross-zone reads. For a database, however, locality must be balanced against resilience: putting every replica in one zone can optimize local latency while creating a single-zone failure exposure. Cross-zone transfer cost and latency should be measured for the actual workload (see M15).

### Why volumes have topology

A node-local disk exists on a particular node. A cloud block volume may be created in a particular zone and attach only to nodes in that zone. A regional disk or replicated storage system may provide broader access, but the precise semantics are product-specific.

Never infer topology from the word “persistent.” Persistence is not the same as replication, portability, or disaster recovery.

### Read node and PV topology

Start with read-only inspection:

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get nodes -L topology.kubernetes.io/zone,kubernetes.io/hostname
kubectl get storageclass
kubectl get pv
kubectl get pvc -A
```

For a particular Pod and claim:

```bash
kubectl -n <namespace> describe pod <pod-name>
kubectl -n <namespace> get pod <pod-name> -o yaml
kubectl -n <namespace> describe pvc <pvc-name>
kubectl get pv <pv-name> -o yaml
kubectl describe storageclass <storageclass-name>
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Replace angle-bracket placeholders before running commands. These commands inspect state; they do not repair it.

Inspect `spec.nodeAffinity` on the PV. Example fragment:

```yaml
spec:
  nodeAffinity:
    required:
      nodeSelectorTerms:
        - matchExpressions:
            - key: topology.kubernetes.io/zone
              operator: In
              values:
                - zone-a
```

This is an illustrative fragment, not a complete PV. It means that nodes must match the stated topology requirement for the PV to be usable. A local PV may instead use `kubernetes.io/hostname` with one node name. The exact affinity generated by a driver is backend-specific.

### Worked scenario: Pod can run on B, volume is local to A

**[ASSUMPTION]** Node A has label `kubernetes.io/hostname=node-a`; Node B has `kubernetes.io/hostname=node-b`. A local PV requires `node-a`. The Pod's other constraints permit either node.

Evidence to collect:

1. `kubectl describe pod ...` shows `Pending` and a scheduler event describing volume node affinity conflict, or a similar message.
2. `kubectl get pv <pv> -o yaml` shows a required hostname affinity for `node-a`.
3. `kubectl get nodes -L kubernetes.io/hostname,topology.kubernetes.io/zone` confirms which node has each label.
4. The PVC is already bound to that PV, so creating another Pod does not move the data.

Do not “fix” the problem by forcing the Pod onto Node B, removing affinity, or deleting the claim. If Node A is merely temporarily unavailable, recovery may mean restoring it. If it is permanently lost, the data may be inaccessible or physically lost; recover from a verified replica or backup according to the application runbook.

**Unavailable is not the same as permanently lost.** A failed node may later return with intact data. Conversely, if the only copy lived on a destroyed local disk, the data may be permanently lost. Establish which case applies before taking action.

### Why `Pending` may be protective

`Pending` is a Pod phase, not a root-cause diagnosis. The scheduler may have no feasible node because of CPU/memory constraints, node affinity, taints, topology spread, unbound claims, or PV topology. A `Pending` Pod can be evidence that Kubernetes is refusing an invalid placement rather than silently mounting the wrong data.

## 7.4 Level 2 — Intermediate: scheduling and volume binding

### `Immediate` versus `WaitForFirstConsumer`

With `Immediate`, binding or dynamic provisioning starts as soon as the PVC is created. For a topology-constrained backend, the volume may be provisioned in a zone before the scheduler knows the eventual Pod's node affinity, anti-affinity, resource needs, or tolerations. The Pod can then be unschedulable if no eligible node can access the volume.

With `WaitForFirstConsumer`, binding/provisioning is delayed until a Pod references the PVC. The scheduler can consider the consuming Pod's scheduling constraints when selecting a compatible topology. It does not guarantee success: there may be insufficient capacity, unsupported topology, an unavailable driver, or incompatible constraints.

A WFFC claim can remain `Pending` before a consuming Pod exists. That is normal by design; check the consumer Pod and events before diagnosing it as stuck.

Official Kubernetes documentation describes the binding-mode behavior and topology restrictions. See Sources below. **[VERIFY]** Check the documentation for the cluster's exact Kubernetes release and CSI driver.

### StorageClass example using delayed binding

A generic example can safely show the Kubernetes field without inventing a CSI provisioner or backend parameter:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: example-wffc
provisioner: REPLACE_WITH_A_REAL_SUPPORTED_PROVISIONER
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Retain
```

This is a **template**, not directly deployable until the provisioner is replaced with a real driver installed in the cluster. The `Retain` policy is included to make the example's data-retention intent explicit; it is not a substitute for backup. A `StorageClass` is cluster-scoped and changing policy later does not automatically change every already-created PV.

To restrict topologies, a provider-supported StorageClass can add a block like this:

```yaml
allowedTopologies:
  - matchLabelExpressions:
      - key: topology.kubernetes.io/zone
        values:
          - zone-a
          - zone-b
```

Use only values that the actual nodes and driver recognize. `allowedTopologies` is not a way to make a backend support a zone it cannot use. With WFFC, Kubernetes documentation notes that an explicit topology restriction is often unnecessary, but can still be used when the design requires it. The provisioner must support the topology labels and restrictions.

**Never apply the template unchanged.** First inspect the installed StorageClasses and CSI driver:

```bash
kubectl get storageclass -o wide
kubectl get csidrivers
kubectl get pods -A | grep -i -E 'csi|provisioner|attacher'
kubectl describe storageclass <actual-class>
```

The `grep` command is only a convenience; Windows shells may differ. If no CSI driver is installed, do not invent one. In the kind lab below, the topology mismatch is demonstrated with a static local PV and node affinity, not by pretending that the default kind provisioner is a cloud zonal block driver.

### Interacting constraints

A Pod is schedulable only if the relevant constraints can be satisfied together:

- **Volume binding / PV affinity:** the node must be able to use the bound or provisioned volume.
- **Node affinity / nodeSelector:** the Pod must match required node labels.
- **Taints and tolerations:** a node taint can exclude a Pod unless tolerated; toleration alone does not guarantee placement.
- **Pod affinity/anti-affinity:** the Pod may need to co-locate with or avoid other Pods in a topology domain.
- **Topology spread:** matching Pods may be constrained to a permitted skew across eligible topology domains.
- **Resources:** CPU, memory, and other resource requests must fit.
- **Storage capacity tracking:** if supported and enabled for the CSI driver and binding mode, the scheduler can use CSI capacity information when considering volume placement. It is not a universal or perfect capacity oracle. **[VERSION-SENSITIVE]** Check the Kubernetes version and CSI driver's official capacity-tracking documentation.

A configuration can be individually reasonable but jointly impossible. For example, a Pod may require zone C, tolerate only a subset of nodes, and use a PV restricted to zone A. No scheduler preference can make those requirements compatible.

### Diagnostic walk-through

Run read-only checks first:

```bash
kubectl -n <namespace> get pod <pod-name> -o wide
kubectl -n <namespace> describe pod <pod-name>
kubectl -n <namespace> get pvc
kubectl -n <namespace> describe pvc <claim-name>
kubectl get pv <pv-name> -o yaml
kubectl get nodes -L topology.kubernetes.io/zone,kubernetes.io/hostname
kubectl describe storageclass <class-name>
kubectl get events -n <namespace> --sort-by=.metadata.creationTimestamp
```

How to interpret evidence:

- A scheduler event mentioning `volume node affinity conflict` supports the hypothesis that no feasible node matches the PV's topology.
- An unbound PVC using WFFC, with no consuming Pod, may be expected.
- A PVC with a consumer Pod but no progress requires inspection of Pod events, provisioner/CSI events, capacity, and driver logs.
- A StorageClass `allowedTopologies` block that excludes every otherwise eligible node is a likely configuration mismatch.
- A `Multi-Attach` message may indicate the volume is still considered attached to another node; do not manually remove attachment metadata without the backend's documented recovery process.
- Exact event wording and controller behavior can change. Treat messages as evidence, not as the entire diagnosis.

| Mechanism | Benefit | Common failure mode | Evidence to inspect | Suitable use |
|---|---|---|---|---|
| `Immediate` binding | Simple when topology is irrelevant or backend chooses a globally usable volume | Volume provisioned where the Pod cannot run | PVC/PV topology, Pod events | Topology-independent storage or carefully designed backends |
| `WaitForFirstConsumer` | Scheduling constraints can inform provisioning | No compatible topology/capacity; claim remains pending while waiting for consumer | Consumer Pod, events, StorageClass, CSI logs | Topology-constrained dynamic provisioning |
| `allowedTopologies` | Restricts provisioning to approved domains | Restriction excludes eligible nodes or uses wrong labels | StorageClass YAML, node labels, driver docs | Intentional placement boundary |
| PV `nodeAffinity` | Prevents use from incompatible nodes | Pod cannot move after node/zone loss | PV YAML and node labels | Local and topology-bound volumes |
| Topology spread `DoNotSchedule` | Enforces a placement skew limit | Pods remain pending when domains are unavailable | Pod events and eligible domain labels | Strict placement requirement with capacity planning |
| Topology spread `ScheduleAnyway` | Prefers balance without hard spread rejection | Workload may concentrate when constraints/capacity force it | Actual placement and labels | Best-effort spreading where scheduling is preferred |

## 7.5 Level 3 — Advanced: designing for zonal failure

### Application-level replication across zones

A common database design uses one database member per zone and a separate zonal volume for each member. The database system—not the StatefulSet—replicates records or logs, decides whether a member can be promoted, and manages consistency.

Example conceptual placement:

```text
Zone A: db-0 + volume-a  <---- database replication ----> Zone B: db-1 + volume-b
                                  |
                                  +---------------------> Zone C: db-2 + volume-c
```

This only helps if the database's replication protocol, quorum policy, and failover behavior are correctly configured and tested. Three Pods in three zones are not enough by themselves. Three database processes using the same underlying data directory is not a valid replication design. Each replica's volume should match the database's supported storage model.

### Storage architecture choices

| Option | Topology | Failure scope | Latency | Durability assumptions | Operational complexity | Suitable workloads |
|---|---|---|---|---|---|---|
| Zonal block volume | Usually tied to a zone; verify backend | Zone loss can make the volume unavailable | Often good local I/O; cross-zone access may be prohibited or unsupported | Backend-specific; a single zonal volume is not cross-zone replication | Moderate; attach/detach and zone-aware provisioning matter | Database member with application-level replication |
| Regional/replicated storage | Backend-defined copies/access across domains | Can tolerate only the failures promised by its design | Replication can add write latency; varies by product | Must inspect replication mode, consistency, and failure guarantees | Moderate to high | Workloads needing storage-layer replication or broader access |
| Shared network filesystem | Network-accessible from multiple nodes, subject to driver semantics | Depends on service and mount path; shared access is not HA for the application | Network latency and metadata semantics matter | Filesystem durability/replication is backend-specific | Moderate; permissions, throughput, mount behavior | Shared content, artifacts, some application data; databases only when vendor-supported |
| Node-local PV | One node or local device | Node loss can make data unavailable or lost | Often low latency | No implied replication; durability depends on local hardware and recovery | High operational responsibility for placement and node replacement | Cache, scratch, or deliberately managed local-data workloads |

Do not generalize across vendors. “Regional disk,” Ceph/Rook, Longhorn, and managed network filesystems differ in replication, fencing, consistency, repair, and failure behavior. **[VERIFY]** Use the exact backend's architecture, limitations, and failure-mode documentation before making a production claim.

### Why one-zone storage and multi-zone scheduling conflict

Suppose a PVC is bound to a volume in zone A, but a Pod has node affinity to zone B or strict spread constraints make zone A ineligible. The scheduler cannot move the volume merely because the Pod template permits multiple zones. If the volume is zonal, the Pod must run where the volume can be used, or the application must recover onto a different replica/volume through an explicitly supported procedure.

For stateful services, design the unit of failure carefully: the database replica and its volume should be placed together, while independent replicas should be spread across failure domains.

### `DoNotSchedule` versus `ScheduleAnyway`

A topology spread constraint includes a `topologyKey`, `maxSkew`, a selector, and `whenUnsatisfiable`.

- `DoNotSchedule` treats the spread limit as a hard scheduling constraint. If no node can satisfy it, the Pod remains unscheduled. This preserves the placement policy but may reduce immediate availability after a domain loss.
- `ScheduleAnyway` lets the scheduler continue and scores nodes that improve balance more favorably. It is a preference, not a guarantee of balanced placement.

Use strict spread only if you have enough eligible domains and capacity to satisfy it during expected maintenance and failure scenarios. With a zone missing, strict spreading may intentionally block a replacement Pod. With best-effort spreading, replicas may concentrate in surviving zones. Either can be correct depending on the application and failure policy.

**[VERSION-SENSITIVE]** Verify `minDomains`, `nodeAffinityPolicy`, `nodeTaintsPolicy`, and any newer topology-spread fields against the Kubernetes version in use. Missing topology labels can also cause nodes to be omitted from calculations.

### Synchronous and asynchronous cross-zone replication

The trade-off depends on the replication protocol and what “acknowledged” means.

- **Synchronous:** if a write is acknowledged only after a remote durability condition, the system can reduce acknowledged-write loss after certain failures. The cost may include additional write latency and reduced write availability when the remote member or link is unavailable. Some systems use synchronous quorum rather than requiring every replica.
- **Asynchronous:** the primary can acknowledge writes before remote copies catch up, often improving write latency and availability under some conditions. A sudden failure can lose writes that had not reached the surviving replica; the risk depends on replication lag and promotion rules.

Do not state that synchronous always means zero RPO or that asynchronous always means a fixed amount of loss. The actual RPO depends on the protocol, failure scenario, commit/ack semantics, and operator configuration. Measure the system and read its official replication documentation.

### Quorum: three versus five members

For a simple majority-based voting system, the majority is `floor(N / 2) + 1`.

| Voting members | Majority needed | Members that can be lost while retaining a majority, under ideal independent-failure assumptions |
|---:|---:|---:|
| 3 | 2 | 1 |
| 5 | 3 | 2 |

This arithmetic is not a complete availability guarantee. A database may have a leader, synchronous replica policy, non-voting replicas, or other requirements. A 3-member system with all members in one zone can lose quorum in one zone failure despite having three members. A 3-member system spread across three independent zones can often retain a majority after one zone loss, assuming the remaining members are healthy and the system permits continued operation. A 5-member system across zones requires deliberate placement, such as 2/2/1, and the consequences of losing the zone with two members differ from losing the zone with one.

Replica count alone does not create resilience. Confirm voter roles, failure detection, promotion safety, and the exact protocol.

### Rebalancing after a zone returns

When a zone returns, do not assume the system automatically rebalances Pods, data, or leadership. Topology spread does not necessarily evict existing Pods to restore balance. A database may need replica catch-up, leader transfer, or a documented rejoin process. A storage backend may need replica rebuild or healing.

A safe rebalancing plan should specify:

1. Confirm the recovered zone and storage backend are healthy.
2. Confirm the database's replication state and data consistency.
3. Restore a replica only through the supported database/operator procedure.
4. Monitor replication lag, rebuild progress, I/O pressure, and error rates.
5. Confirm the intended distribution and quorum after recovery.
6. Avoid deleting old volumes until ownership, replacement state, and recovery success are proven.

### Volume attachment and `Multi-Attach`

For drivers that require attachment, Kubernetes and CSI components coordinate attach/detach. A `VolumeAttachment` object records intent for a volume/node relationship. Following node failure, the control plane may still consider a volume attached to the old node, or the storage backend may not yet have released it. A replacement Pod may show a `Multi-Attach` or mount error.

Safe response:

- Inspect the Pod events, PV, `VolumeAttachment` objects, CSI controller logs, and provider/backend state.
- Determine whether the old node is actually fenced/offline and whether the backend confirms detach is safe.
- Follow the CSI driver and provider recovery procedure.
- Do not manually delete `VolumeAttachment` or PV finalizers as a generic fix. Doing so may remove Kubernetes bookkeeping without proving the storage is detached or safe to attach elsewhere.

Do not rely on fixed detach timeouts. **[VERIFY]** Check the Kubernetes controller-manager, CSI external-attacher, driver, and provider documentation for the deployed versions.

### Local PVs and node replacement

A local PV's node affinity records where its data resides. Replacing the node does not move the data to the replacement node. A new node with a similar label is not equivalent to the old disk. Before node replacement, determine whether the workload is disposable, replicated elsewhere, or recoverable from backup. Plan migration/rebuild at the application layer.

**[VERIFY]** Do not assume PV node affinity can be edited in place or that a local PV can be rebound safely. Check the relevant Kubernetes API version and the local storage provisioner's documentation. The safe general plan is to recover data to a new, correctly provisioned volume through an approved application/backup workflow, not to rewrite topology metadata to bypass reality.

### Data gravity and compute-follows-data

For large ETL or analytics jobs, moving compute near stored data can reduce network transfer, cross-zone charges, and contention. Conversely, placing all stateful compute in one zone to minimize I/O can increase correlated failure risk. A good design makes the trade-off explicit: locality for routine operations, replication or recovery for failure, and measured cross-zone costs. See M15 for cost modeling and M13/M14 for broader recovery design.

### Decision summary

- Choose **zonal block storage plus application replication** when the database supports one member per volume and cross-zone failover is part of the database design.
- Consider **regional/replicated storage** when its documented semantics fit the workload and the team can operate its failure and repair mechanisms.
- Choose a **shared network filesystem** for supported shared-file use cases; do not infer database HA from shared mounts.
- Choose **local PVs** only when the performance/use case justifies the node affinity and the team has an explicit node-loss data plan.

### Failure simulation limits

A `kind` cluster runs Kubernetes nodes as containers on one host. Adding fake zone labels tests label-driven scheduling behavior only. Stopping a kind worker container does not reproduce an independent cloud-zone failure, cloud block-volume detachment, regional replication, real cross-zone latency, separate power/network paths, or provider control-plane behavior. The lab can prove that Kubernetes responds to labels and node loss in the local simulation; it cannot prove production zonal resilience.

## 7.6 Level 4 — Expert: failure operations and fleet guardrails

### Multi-zone architecture review checklist

Before approving a stateful deployment, ask:

1. Which physical or provider failure domains exist, and how are they represented by verified node labels?
2. Can each database replica's volume be accessed only from one node, one zone, or a broader domain?
3. Does the StorageClass use the intended binding mode? Is `allowedTopologies` necessary and correct?
4. Does the CSI driver support topology-aware provisioning and capacity tracking, if required?
5. Are the replicas spread across independent domains, including after maintenance and node-pool replacement?
6. What is the voting/quorum layout, and which zone-loss scenarios retain quorum?
7. What happens to writes during cross-zone network loss?
8. Can the surviving replicas accept writes safely? Is promotion fenced and documented?
9. What are the detach/reattach and recovery procedures for the backend?
10. Are backup and restore independently tested? Replication is not backup.
11. Are alerts in place for topology concentration, pending Pods, PVC provisioning failures, attach failures, replication lag, and quorum loss?
12. Who owns the Kubernetes layer, CSI driver, storage backend, and database recovery?
13. Are the cost and latency of cross-zone traffic measured?
14. Has the exact failure scenario been tested in a representative non-production environment?
15. Which assumptions remain `[VERIFY]` items?

### Zone-evacuation runbook

> **⚠ DESTRUCTIVE OR DISRUPTIVE — THROWAWAY LAB ONLY.** Never run this sequence on a production context. It intentionally removes local lab capacity and may make local data unavailable.

1. Establish the current context and identify the intended throwaway cluster.
2. Confirm database quorum and data safety first. For this basic lab, use a stateless or disposable demonstration workload; do not improvise database failover.
3. Record node labels, Pods, PVCs, PVs, `VolumeAttachment` objects, and events.
4. Inspect the PV affinity and determine which workloads depend on the target node.
5. Identify the exact kind worker container by listing containers; do not guess a name.
6. Stop only the selected worker container after verifying the context and container identity. This disrupts the lab.
7. Observe which Pods become `Pending`, which are recreated elsewhere, and what events occur.
8. Restore the worker container and wait for node readiness.
9. Verify Pod, PVC/PV, and application state. For local volumes, verify the data rather than assuming it survived.
10. Save evidence, document the simulated failure boundary, and clean up only resources created by this lab.

The exact commands are in Section 7.7. If any precondition is unclear, stop and use the non-disruptive alternative.

### Failure scenario matrix

| Blast radius | Expected behavior | Detection/evidence | Data risk and RPO/RTO reasoning | Recovery and prevention |
|---|---|---|---|---|
| Pod failure | Controller may recreate Pod; same claim is reused | Pod events, restart count, PVC/PV | Usually no data loss if volume and application state remain intact; RTO depends on startup/recovery | Fix root cause; monitor probes and application health |
| Node failure | Pods may be recreated elsewhere, but node-local or node-bound volumes can block them | Node condition, PV affinity, attach events, `VolumeAttachment` | Data may be unavailable or lost if sole copy was local; RTO includes fencing/reattach/recovery | Restore node or recover to new storage from replica/backup |
| Zone failure | Zonal volumes may be inaccessible; surviving application replicas may retain service if quorum and routing allow | Zone/node labels, pending Pods, database quorum/lag, provider events | RPO depends on replication/commit policy; RTO includes failover and possible rebuild | Pre-place independent replicas, test quorum, follow database runbook |
| Region failure | Multiple zones and shared services may be affected | Provider status, cross-region health checks, app/DR telemetry | Regional RPO/RTO require separate recovery architecture and tested dependencies | M13/M14: cross-region backups/replication, failover criteria, dependency plan |

### Audit script: replica spread and PV topology alignment

The following Python script uses `kubectl` JSON output and the Python standard library. It is deliberately conservative: missing zone labels or an unresolved PVC/PV/node mapping are reported as **UNKNOWN**, not passed. It checks selected StatefulSets by label selector and namespace. It does not understand every CSI/provider-specific topology model; treat it as a review aid, not an enforcement engine.

Prerequisites: Python 3 and a working `kubectl` context with least-privilege read access to the target namespace's StatefulSets/Pods/PVCs and cluster-scoped PVs/nodes. It does not need cluster-admin. Save it as `audit_topology.py` in your personal lab notes, not in the repository unless your project workflow explicitly calls for that.

```python
#!/usr/bin/env python3
"""Read-only audit of StatefulSet replica zone spread and PVC/PV topology.

Exit code 0 means no FAIL findings; UNKNOWN findings can still exist.
Exit code 1 means at least one FAIL finding.
Requires: Python 3, kubectl, permission to list relevant objects.
"""
import json
import subprocess
import sys


def kubectl_json(*args):
    proc = subprocess.run(
        ["kubectl", *args, "-o", "json"],
        check=False, capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"kubectl {' '.join(args)} failed: {proc.stderr.strip()}"
        )
    return json.loads(proc.stdout)


def labels(obj):
    return (obj.get("metadata") or {}).get("labels") or {}


def matches_selector(pod_labels, selector):
    match_labels = selector.get("matchLabels") or {}
    if not all(pod_labels.get(k) == v for k, v in match_labels.items()):
        return False
    for expr in selector.get("matchExpressions") or []:
        key, op, values = expr.get("key"), expr.get("operator"), expr.get("values", [])
        present = key in pod_labels
        value = pod_labels.get(key)
        if op == "In" and (not present or value not in values):
            return False
        if op == "NotIn" and present and value in values:
            return False
        if op == "Exists" and not present:
            return False
        if op == "DoesNotExist" and present:
            return False
        if op not in {"In", "NotIn", "Exists", "DoesNotExist"}:
            print(f"UNKNOWN: unsupported selector operator {op!r}")
            return False
    return True


def pv_required_values(pv, key):
    affinity = (pv.get("spec") or {}).get("nodeAffinity") or {}
    required = affinity.get("required") or {}
    found = []
    for term in required.get("nodeSelectorTerms") or []:
        for expr in term.get("matchExpressions") or []:
            if expr.get("key") == key and expr.get("operator") == "In":
                found.extend(expr.get("values") or [])
        for field in term.get("matchFields") or []:
            if key == "metadata.name" and field.get("operator") == "In":
                found.extend(field.get("values") or [])
    return sorted(set(found))


def main():
    namespace = sys.argv[1] if len(sys.argv) > 1 else "default"
    statefulsets = kubectl_json("-n", namespace, "get", "statefulsets").get("items", [])
    pods = kubectl_json("-n", namespace, "get", "pods").get("items", [])
    pvcs = kubectl_json("-n", namespace, "get", "pvc").get("items", [])
    pvs = kubectl_json("get", "pv").get("items", [])
    nodes = kubectl_json("get", "nodes").get("items", [])

    node_by_name = {
        (n.get("metadata") or {}).get("name"): labels(n) for n in nodes
    }
    pvc_by_name = {(p.get("metadata") or {}).get("name"): p for p in pvcs}
    pv_by_name = {(p.get("metadata") or {}).get("name"): p for p in pvs}
    findings = 0

    if not statefulsets:
        print(f"UNKNOWN: no StatefulSets found in namespace {namespace!r}")
        return 0

    for sts in statefulsets:
        meta = sts.get("metadata") or {}
        name = meta.get("name", "<unknown>")
        selector = (sts.get("spec") or {}).get("selector") or {}
        matched = [
            p for p in pods
            if matches_selector(labels(p), selector)
        ]
        zones = {}
        print(f"\nStatefulSet {namespace}/{name}: matched Pods={len(matched)}")
        if not matched:
            print("  UNKNOWN: no matching Pods found; selector or controller state may be unexpected")
        for pod in matched:
            pm = pod.get("metadata") or {}
            pod_name = pm.get("name", "<unknown>")
            spec = pod.get("spec") or {}
            node_name = spec.get("nodeName")
            node_labels = node_by_name.get(node_name, {}) if node_name else {}
            zone = node_labels.get("topology.kubernetes.io/zone")
            if not node_name:
                print(f"  UNKNOWN: Pod {pod_name} has no assigned node")
            elif zone is None:
                print(f"  UNKNOWN: node {node_name} has no topology.kubernetes.io/zone label")
            else:
                zones[zone] = zones.get(zone, 0) + 1
                print(f"  INFO: Pod {pod_name} -> node={node_name}, zone={zone}")

            for vol in spec.get("volumes") or []:
                claim_name = ((vol.get("persistentVolumeClaim") or {}).get("claimName"))
                if not claim_name:
                    continue
                claim = pvc_by_name.get(claim_name)
                if not claim:
                    print(f"  UNKNOWN: PVC {claim_name} not found in namespace view")
                    continue
                pv_name = (claim.get("spec") or {}).get("volumeName")
                pv = pv_by_name.get(pv_name) if pv_name else None
                if not pv:
                    print(f"  UNKNOWN: PVC {claim_name} has no resolved PV (volumeName={pv_name!r})")
                    continue
                pv_zone = pv_required_values(pv, "topology.kubernetes.io/zone")
                pv_host = pv_required_values(pv, "kubernetes.io/hostname")
                if pv_zone and zone and zone not in pv_zone:
                    findings += 1
                    print(f"  FAIL: {pod_name} runs in zone {zone}, PV {pv_name} requires zone value(s) {pv_zone}")
                elif pv_host and node_name and node_name not in pv_host:
                    findings += 1
                    print(f"  FAIL: {pod_name} runs on node {node_name}, PV {pv_name} requires hostname value(s) {pv_host}")
                elif not pv_zone and not pv_host:
                    print(f"  UNKNOWN: PV {pv_name} has no recognized zone/hostname affinity; inspect driver-specific topology")
                else:
                    print(f"  INFO: PV {pv_name} recognized affinity zone={pv_zone or 'none'}, hostname={pv_host or 'none'}")

        if len(zones) < 2 and len(matched) > 1:
            print(f"  WARN: replicas occupy fewer than two observed zones: {zones or 'no known zones'}")
        else:
            print(f"  INFO: observed replica distribution by zone: {zones}")

    print("\nSummary:")
    print(f"  FAIL findings: {findings}")
    print("  UNKNOWN/WARN findings require human review; absence of FAIL is not proof of resilience.")
    return 1 if findings else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
```

Run it against a namespace you own:

```bash
python3 audit_topology.py <namespace>
```

Interpretation and limitations:

- `FAIL` means a recognized PV zone/hostname affinity conflicts with the Pod's assigned node.
- `UNKNOWN` means a label or mapping is missing, or the PV's topology representation is not understood.
- `WARN` means replicas appear concentrated in fewer than two observed zones; it does not assess database quorum or replication health.
- The script uses the PV affinity as represented in Kubernetes. CSI topology may be expressed using driver-specific keys or metadata not covered here.
- It does not prove independent power/network paths, actual storage replication, or application-level data consistency.
- For policy-as-code, prefer a tested admission policy (for example, a policy engine already approved by your platform team) that targets named workload/storage classes. Flag `Immediate` for selected zonal classes only when WFFC is the intended backend policy; do not ban `Immediate` universally. Likewise, validate topology spread for selected StatefulSets, not every workload indiscriminately.

### Incident walkthrough 1: all PostgreSQL replicas landed in one zone

**Symptoms:** three database Pods are running, but the node labels show all three in one zone after a node-pool change. The application may be healthy now but has correlated zone-failure exposure.

**Evidence:** collect StatefulSet and Pod YAML, node zone labels, PVC/PV mappings, database/operator status, replica roles, replication lag, quorum/voting configuration, and recent scheduling events. Run the read-only audit script and save its output.

**Hypotheses:** the replacement node pool has incorrect/missing zone labels; the topology spread selector does not match the Pod labels; the constraint is `ScheduleAnyway`; required domains are not eligible; or the operator's scheduling template does not include the expected constraints.

**Safe diagnosis:** verify node labels against provider metadata, inspect the StatefulSet/operator configuration, and compare actual database membership with Kubernetes placement. Do not move database volumes manually.

**Recovery options:** correct verified node labels through the platform process; update the workload/operator scheduling configuration; add eligible capacity in other zones; then use the database's supported replica relocation/rebuild procedure. A Pod's placement change alone does not relocate its data.

**Prevention/post-incident:** add placement audits and alerts, test node-pool upgrades, verify selector matching, and record the intended distribution and quorum policy.

### Incident walkthrough 2: Pods remain Pending after a simulated zone outage

**Symptoms:** a worker container representing a fake zone is stopped; Pods using local PVs or volumes constrained to that node remain `Pending`, or the node is `NotReady`.

**Evidence:** record the exact cluster context, container identity, node labels, Pod events, PV `nodeAffinity`, PVC binding, and current `VolumeAttachment` objects if applicable.

**Hypotheses:** the PV is node-local; the PV is bound to a topology unavailable to remaining nodes; topology spread blocks scheduling; or a driver/backend has not completed safe detach/reattach.

**Safe diagnosis:** first distinguish a local PV from a network-attached or replicated backend. Inspect only; do not delete claims or patch affinity. For the local kind demo, accept that the volume may be unavailable or lost with the node/container.

**Recovery options:** restore the simulated worker for the lab; in production, restore the node/zone if possible, reattach only through documented backend behavior, or recover the application onto a new volume from a healthy replica/backup. Confirm database safety before promotion.

**Prevention/post-incident:** validate zone-level replica placement, test recovery, review RPO/RTO, and document what was simulated versus what requires a real provider test.

### Architecture Decision Record (ADR) example

**Title:** Stateful database storage topology

**Status:** Proposed; requires workload and provider validation.

**Context:** The database must tolerate the loss of one zone without depending on a single zonal volume. The workload needs durable per-member storage and a documented failover process.

**Decision:** Use a separate zonal block volume per database member, with application-level replication across three independent zones, if the selected database/operator officially supports this topology. Use `WaitForFirstConsumer` for the zonal StorageClass where supported and appropriate. Apply explicit topology spread/affinity and verify the operator's placement behavior.

**Alternatives:** a regional/replicated storage backend; a supported shared filesystem; node-local PVs. Reject node-local PVs for the primary database data path unless the team explicitly accepts the node-loss recovery implications.

**Consequences:** requires enough capacity in each zone, correct labels, database quorum/replication monitoring, tested rejoin/rebuild procedures, and cross-zone network/cost budgeting. Kubernetes placement does not replace database replication or backups.

**Verification required:** exact CSI driver and provider topology semantics; synchronous/asynchronous commit behavior; detach/reattach process; operator's replica scheduling controls; restore and zone-failure test results.

## 7.7 Hands-on lab: simulate zones with kind

### Lab goals and constraints

This mandatory lab demonstrates **scheduling topology and volume affinity**, then compares that simulation with real zonal-storage concepts.

- **Platform:** WSL2 Ubuntu or native Linux, `kind`, `kubectl`, Docker or another runtime supported by the installed kind version.
- **Budget:** no paid services or cloud volumes.
- **Cluster size:** one control-plane node and no more than three workers.
- **Estimated footprint:** approximate only; a small kind cluster and a few tiny test Pods often fit within the 4 CPU / 8 GB RAM / 30 GB disk lab budget, but actual usage depends on image cache and host environment. Keep other heavy services stopped. Check free disk before starting.
- **Duration:** about 45–90 minutes, depending on image pulls and troubleshooting.
- **Fidelity limitation:** fake zone labels are labels only. They do not create independent zones, cloud storage behavior, cross-zone latency, or production resilience.

### 7.7.1 Preflight and safety guard

Check disk and tools:

```bash
df -h .
kind version
kubectl version --client
docker version
kind get clusters
kubectl config current-context
```

If Docker is unavailable, stop and configure the local runtime using its official documentation. On WSL2, check the Windows host's free disk space as well as the Linux filesystem. Deleting files inside WSL2 does not guarantee that the virtual disk file on the Windows host immediately shrinks.

Use a uniquely named throwaway cluster:

```bash
export LAB_CLUSTER="m05-u7-topology-lab"
```

Before any disruptive action, verify the context and cluster. If an existing cluster with that name contains work you care about, do not reuse or delete it.

```bash
kind get clusters
kubectl config get-contexts
```

### 7.7.2 Create a small throwaway cluster

If the named cluster does not exist, create it with three workers. Save the following as `kind-u7.yaml` in your personal lab directory:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: m05-u7-topology-lab
nodes:
  - role: control-plane
  - role: worker
  - role: worker
  - role: worker
```

`kind.x-k8s.io/v1alpha4` is the cluster config API used in kind examples; verify against the installed kind documentation if your version reports an error.

Create only if the cluster does not already exist:

```bash
if kind get clusters | grep -qx "$LAB_CLUSTER"; then
  echo "Cluster already exists; inspect it before continuing."
else
  kind create cluster --config kind-u7.yaml
fi
```

Set the context explicitly and check it:

```bash
kubectl config use-context "kind-${LAB_CLUSTER}"
kubectl config current-context
kubectl get nodes -o wide
```

**Stop** if the context is not `kind-m05-u7-topology-lab` or if node names differ from the nodes you inspected. Do not proceed on a production or shared cluster.

### 7.7.3 Label worker nodes with fake zones

Discover names instead of assuming them:

```bash
kubectl get nodes -o wide
kubectl get nodes -l node-role.kubernetes.io/control-plane
kubectl get nodes -l '!node-role.kubernetes.io/control-plane' -o name
```

Choose the three worker node names from the last command. Label each with a fake zone. Replace the example names below with the exact discovered names:

```bash
kubectl label node <worker-a-name> topology.kubernetes.io/zone=a --overwrite
kubectl label node <worker-b-name> topology.kubernetes.io/zone=b --overwrite
kubectl label node <worker-c-name> topology.kubernetes.io/zone=c --overwrite
kubectl get nodes -L topology.kubernetes.io/zone,kubernetes.io/hostname
```

These labels are not evidence of real zones. They only let the scheduler apply label-based rules to nodes in this cluster.

### 7.7.4 Inspect the actual StorageClass and provisioner

```bash
kubectl get storageclass -o wide
kubectl get storageclass -o yaml
kubectl get csidrivers
kubectl get pv,pvc -A
```

Do not assume the default class is `standard`, that it uses a particular provisioner, or that it emulates cloud zonal storage. Read the actual StorageClass's `provisioner` and installed driver documentation. If the cluster uses a node-local host-backed provisioner, treat its data as local to the kind node/container and not as replicated.

This lab uses a **static local PV with explicit hostname affinity** for the core mismatch. That avoids inventing a CSI driver or claiming the default local-path provisioner behaves like a cloud zonal block volume.

### 7.7.5 Create the lab namespace and a pinned local PV

Choose one worker and record its exact `kubernetes.io/hostname` label:

```bash
kubectl get nodes -L kubernetes.io/hostname,topology.kubernetes.io/zone
```

Set `LAB_NODE` to the exact hostname label value for one worker. Do not use a guessed name:

```bash
export LAB_NODE="<exact-kubernetes.io/hostname-value>"
kubectl get nodes -l "kubernetes.io/hostname=${LAB_NODE}"
```

The query must return exactly the intended worker. If it returns no node or multiple nodes, stop and correct the value.

Create the namespace and a local PV backed by a directory inside the selected kind node. The path exists inside that node container, not necessarily on your host filesystem.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: m05-u7-lab
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: m05-u7-local-pv
spec:
  capacity:
    storage: 1Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: m05-u7-static-local
  local:
    path: /mnt/m05-u7-data
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
  name: m05-u7-local-claim
  namespace: m05-u7-lab
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  storageClassName: m05-u7-static-local
  resources:
    requests:
      storage: 1Gi
```

Before applying, replace `REPLACE_WITH_EXACT_NODE_HOSTNAME` with the exact value stored in `LAB_NODE`. Create the directory inside the selected worker container, using the exact kind node container name discovered from `docker ps`:

```bash
docker ps --format '{{.Names}}'
```

Confirm the container name corresponds to the worker whose hostname label equals `LAB_NODE`. Then create the path:

```bash
docker exec <exact-worker-container-name> mkdir -p /mnt/m05-u7-data
```

**⚠ DISRUPTIVE — THROWAWAY LAB ONLY:** this command changes the filesystem inside the selected kind worker container. Do not run it against any container you have not identified.

Save the YAML as `static-local-pv.yaml`, replace the hostname placeholder, then apply:

```bash
kubectl apply -f static-local-pv.yaml
kubectl -n m05-u7-lab get pvc
kubectl get pv m05-u7-local-pv -o yaml
```

**[VERIFY]** Local PV behavior and the availability of the path depend on the kind node image and Kubernetes version. If the PV fails to bind or mount, inspect events and the official Kubernetes local-volume documentation rather than weakening its affinity. The static PV is a scheduling demonstration; it is not a recommended production storage setup.

### 7.7.6 Demonstrate a topology/volume-affinity mismatch

Create a Pod that requests the claim but is forced to a *different* worker than the PV's required node. Replace the node label value below with a worker hostname that differs from `LAB_NODE`.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: m05-u7-mismatch
  namespace: m05-u7-lab
spec:
  nodeSelector:
    kubernetes.io/hostname: REPLACE_WITH_DIFFERENT_NODE_HOSTNAME
  containers:
    - name: writer
      image: busybox:1.36
      command: ["sh", "-c", "date > /data/lab-marker.txt; sleep 3600"]
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: m05-u7-local-claim
```

Replace the node hostname with an actual different worker and apply:

```bash
kubectl apply -f mismatch-pod.yaml
kubectl -n m05-u7-lab describe pod m05-u7-mismatch
kubectl get pv m05-u7-local-pv -o yaml
kubectl get nodes -L kubernetes.io/hostname,topology.kubernetes.io/zone
kubectl -n m05-u7-lab get events --sort-by=.metadata.creationTimestamp
```

**Expected observation [ILLUSTRATIVE]:** the Pod cannot schedule onto the selected different node because the PV requires the original node. Exact event text varies. If the claim has not bound or the provisioner behaves differently, inspect the PVC and events before interpreting the result.

Do not force the Pod onto the other node or edit PV affinity to make the test pass. The mismatch is the lesson.

### 7.7.7 Compare `Immediate` and WFFC correctly

The cluster's default local provisioner may not model a cloud zone-aware block volume. Therefore this lab separates two concepts:

1. **Scheduling-only simulation:** the static PV above demonstrates that node affinity can make a Pod unschedulable.
2. **Provisioning behavior:** `Immediate` versus WFFC is a StorageClass/driver behavior. To test it accurately, use a disposable environment with a documented provisioner that supports the relevant topology semantics. Do not claim that a local-path provisioner proves cloud CSI behavior.

Inspect the existing StorageClass:

```bash
kubectl get storageclass -o yaml
kubectl describe storageclass <actual-storageclass-name>
kubectl get csidrivers
```

If the installed class uses `Immediate`, record that fact. If it uses WFFC, create a disposable PVC and consuming Pod in a lab namespace, then observe when binding/provisioning occurs. Do not create a StorageClass with a made-up provisioner. If the cluster does not have a topology-aware CSI driver, mark the dynamic provisioning comparison **conceptual/not reproduced**.

For a compatible driver, use the template in Section 7.4 after replacing the provisioner and any required parameters with values from the driver's official documentation. Record the driver's version, Kubernetes version, class YAML, PVC/Pod events, and PV topology. That is the evidence needed to distinguish the behavior from a generic local provisioner.

### 7.7.8 Deploy three replicas with fake-zone spread

This equivalent stateful demonstration uses a StatefulSet and a headless Service, but intentionally uses `emptyDir` rather than a persistent claim. It demonstrates Pod placement only; it does not claim persistent storage or database HA. This keeps the lab small and avoids tying each replica to a local volume while teaching topology spread.

Save as `spread-demo.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: m05-u7-spread
---
apiVersion: v1
kind: Service
metadata:
  name: spread-demo
  namespace: m05-u7-spread
spec:
  clusterIP: None
  selector:
    app: spread-demo
  ports:
    - name: dummy
      port: 80
      targetPort: 8080
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: spread-demo
  namespace: m05-u7-spread
spec:
  serviceName: spread-demo
  replicas: 3
  selector:
    matchLabels:
      app: spread-demo
  template:
    metadata:
      labels:
        app: spread-demo
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: spread-demo
      containers:
        - name: sleeper
          image: busybox:1.36
          command: ["sh", "-c", "hostname; sleep 3600"]
          resources:
            requests:
              cpu: 10m
              memory: 16Mi
          volumeMounts:
            - name: scratch
              mountPath: /scratch
      volumes:
        - name: scratch
          emptyDir: {}
```

Apply and inspect:

```bash
kubectl apply -f spread-demo.yaml
kubectl -n m05-u7-spread rollout status statefulset/spread-demo --timeout=120s
kubectl -n m05-u7-spread get pods -o wide
kubectl -n m05-u7-spread get pods -o custom-columns='NAME:.metadata.name,NODE:.spec.nodeName,PHASE:.status.phase'
kubectl get nodes -L topology.kubernetes.io/zone
kubectl -n m05-u7-spread describe pods
```

**Expected observation [ILLUSTRATIVE]:** with three eligible workers carrying zones `a`, `b`, and `c`, the scheduler should try to satisfy the spread constraint. The exact placement depends on resource availability, labels, node eligibility, and scheduler behavior. If a zone label is absent or only one eligible domain remains, strict spread can leave Pods Pending.

This StatefulSet is not a highly available database. It has no database protocol, no replication, and no persistent data. The `emptyDir` contents are ephemeral and tied to the Pod lifecycle.

### 7.7.9 Simulate loss of one fake zone

First capture a baseline:

```bash
kubectl config current-context
kubectl get nodes -L topology.kubernetes.io/zone,kubernetes.io/hostname
kubectl -n m05-u7-spread get pods -o wide
kubectl -n m05-u7-lab get pod,pvc
kubectl get pv m05-u7-local-pv -o yaml
```

Discover the exact kind worker container name with `docker ps --format '{{.Names}}'`. Map it to the Kubernetes node name and its fake zone label before proceeding.

> **⚠ DESTRUCTIVE OR DISRUPTIVE — THROWAWAY LAB ONLY.** Stopping a kind worker can disrupt Pods and make node-local data unavailable. Do not run on production or a shared cluster.

Use a shell variable containing the exact container name you discovered. Re-check it immediately before stopping:

```bash
export TARGET_WORKER_CONTAINER="<exact-discovered-container-name>"
docker ps --format '{{.Names}}' | grep -Fx -- "$TARGET_WORKER_CONTAINER"
```

If the check returns no exact match, stop. Verify the corresponding Kubernetes node and fake zone. Then stop only that exact worker:

```bash
docker stop "$TARGET_WORKER_CONTAINER"
```

Observe and save evidence:

```bash
kubectl get nodes -L topology.kubernetes.io/zone,kubernetes.io/hostname
kubectl -n m05-u7-spread get pods -o wide
kubectl -n m05-u7-spread get events --sort-by=.metadata.creationTimestamp
kubectl -n m05-u7-lab describe pod m05-u7-mismatch
kubectl get pv m05-u7-local-pv -o yaml
```

Expected observations are **illustrative**. The node may become `NotReady`; Pods may remain assigned to it for a period; strict topology spread can block replacements; and local storage tied to the stopped worker may be unavailable. Do not infer a fixed timing from the lab. The `emptyDir` data is not durable across Pod recreation. The static local PV's data may remain inside the stopped worker container, but it is unavailable while that worker is stopped and may be lost if the container is removed.

**Non-disruptive alternative:** skip `docker stop`; instead inspect the PV's required hostname affinity and reason through which node remains eligible. You can also use the mismatch Pod already created to demonstrate the scheduling constraint.

### 7.7.10 Restore and verify

Restart the exact worker container:

```bash
docker start "$TARGET_WORKER_CONTAINER"
kubectl get nodes -w
```

Stop watching with Ctrl-C once the node state is stable. Then inspect:

```bash
kubectl get nodes -L topology.kubernetes.io/zone,kubernetes.io/hostname
kubectl -n m05-u7-spread get pods -o wide
kubectl -n m05-u7-spread get events --sort-by=.metadata.creationTimestamp
kubectl -n m05-u7-lab get pod,pvc
kubectl get pv m05-u7-local-pv -o yaml
```

If the local PV Pod was not successfully mounted earlier, do not infer data behavior from a missing marker. If it was mounted and wrote a marker, verify the marker only after the original node is healthy and the Pod is safely scheduled to the node that owns the PV. Never mount the same underlying data path from another node just to inspect it.

This lab does not demonstrate database replica catch-up. A real replicated database has application-level state and a replication protocol; a set of Pods with labels does not.

### 7.7.11 Cleanup

Cleanup removes only the lab namespaces and the static PV created by this lesson. First confirm context:

```bash
kubectl config current-context
```

It must be `kind-m05-u7-topology-lab`. If not, stop.

Delete the lab namespaces, then inspect the PV:

```bash
kubectl delete namespace m05-u7-spread --wait=true
kubectl delete namespace m05-u7-lab --wait=true
kubectl get pv m05-u7-local-pv -o yaml
```

Because the PV uses `Retain`, the PV object may remain in `Released` state after the claim is deleted. **Do not patch finalizers or delete a PV as a reflex.** For this disposable lab only, verify the PV name and ownership, confirm no claim or important data is associated with it, then delete the exact lab-created PV:

```bash
kubectl get pv m05-u7-local-pv -o wide
kubectl delete pv m05-u7-local-pv
```

The directory `/mnt/m05-u7-data` is inside the worker container. Do not remove it until you have confirmed the exact worker container and that the data is disposable. For the simplest safe cleanup, delete the entire throwaway cluster only after confirming its exact name and that it contains no other work:

```bash
kind get clusters
kubectl config current-context
```

**⚠ DESTRUCTIVE — THROWAWAY LAB ONLY:** deleting a kind cluster removes its nodes and lab data. Continue only if the current context is `kind-m05-u7-topology-lab` and the cluster is disposable.

```bash
kind delete cluster --name m05-u7-topology-lab
kind get clusters
```

Finally, verify the lab cluster is absent and that no lab namespace/PV remains in any cluster you intentionally used. Do not delete global CSI drivers or CRDs; this lab did not install them. Review WSL2 host disk usage separately because virtual disk space may not shrink automatically.

### Lab evidence to capture

Save terminal output or sanitized text for:

- `kubectl config current-context` and kind cluster list;
- node names and fake zone labels before/during/after the simulation;
- actual StorageClass and CSI driver inventory;
- PV node affinity and PVC binding state;
- mismatch Pod description and scheduler events;
- the StatefulSet's Pod-to-node distribution;
- audit script output, including all `UNKNOWN` and `WARN` findings;
- recovery observations and cleanup verification.

Do not label expected results as observed. Write “not reproduced” where the installed provisioner cannot test a behavior faithfully.

## 7.8 SRE lens: availability, RTO, and RPO

**Placement is not replication. Replication is not backup.** A Pod can be spread across zones but still use no durable storage. A volume can be persistent but exist in one failure domain. A replicated database can tolerate some member failures but still be vulnerable to accidental deletion, corruption replicated to every member, credential compromise, or a region-wide event.

Separate these properties:

- **Availability:** can the service accept the required operations now?
- **Durability:** will acknowledged data survive the stated failures?
- **Consistency:** what read/write guarantees are provided during normal operation and failures?
- **RPO:** how much recent data can be lost in a defined recovery scenario?
- **RTO:** how long until the service is restored to an agreed state?

A Pod rescheduled to another node does not mean its data followed it. With a zonal volume, the replacement may need to remain in the same zone. With a database replica, service restoration may require quorum, promotion, endpoint changes, and client reconnects. With a backup, restoration may require provisioning new storage and replaying logs.

### SLO and measurement examples

Treat the following as examples of *what to define*, not production target recommendations:

- Service availability SLO: define the user-visible success condition, measurement window, and excluded maintenance (if any).
- Storage attachment objective: measure time from a legitimate Pod scheduling attempt to successful mount, broken down by driver/backend.
- Database recovery objective: measure time to a safe writable primary and verify replication/consistency after failover.
- Data-loss objective: define an RPO for each failure class and validate it with the replication protocol and recovery tests.

Do not choose numeric targets without workload requirements and measured evidence. Monitor Pending state and scheduling reasons, PVC provisioning latency/failures, attachment errors, node/zone distribution, database quorum, replication lag, failed writes, restore success, and end-to-end user transactions.

### Incident evidence packet

At incident start, capture the timestamp and cluster context; affected nodes and zone labels; Pod/StatefulSet/PVC/PV state; scheduler and attach/mount events; CSI controller/driver and provider events; database member roles, quorum, and replication lag; recent deployment/node-pool changes; and backup status. Sanitize resource names and workload metadata before sharing externally.

Use evidence to separate layers:

- **Scheduler/storage:** Pod cannot be placed, claim cannot bind, volume cannot attach/mount.
- **Database:** Pods run, but quorum, leader election, replication, or consistency is unhealthy.
- **Application/network:** database is healthy but Service routing, DNS, NetworkPolicy, or client reconnect fails.

Formal multi-region disaster recovery, backup retention, and cross-cluster failover are deferred to M13/M14.

## 7.9 Security and data-safety lens

1. **Inspect before mutation.** Record context, resource ownership, PV/PVC mapping, backend identity, replica health, and backup/restore status before any disruptive action.
2. **Never force-delete a Pod or patch PV finalizers as a topology shortcut.** These actions do not prove the storage backend has safely detached or that another copy exists.
3. **Never delete a PVC/PV to make a Pending Pod disappear** unless the approved recovery plan explicitly calls for it and the data implications are understood.
4. **Use least privilege.** The audit script needs read-only access to the relevant objects; it does not need cluster-admin for routine diagnosis. Scope RBAC to required namespaces and resources where feasible.
5. **Protect evidence.** Logs, YAML, events, snapshot metadata, and audit output can expose internal resource names, labels, namespaces, image references, or topology. Sanitize before sharing.
6. **Use fake credentials and disposable data.** Do not place real secrets in manifests or lab files.
7. **Treat local kind data as disposable.** It is not a durable replicated storage service. A worker container or cluster deletion may remove the only copy.
8. **Use documented detach/recovery procedures.** Do not manually remove `VolumeAttachment` objects or edit PV affinity without driver/provider guidance.
9. **Keep the failure boundary explicit.** Simulated zones are not production zones; passing this lab is not evidence of production-grade resilience.
10. **Backups are a separate control.** Replication can copy logical corruption or accidental deletes. Test restoration to a new target and verify application correctness.

## 7.10 Troubleshooting decision tree

Begin with read-only evidence. Do not delete or patch storage objects to clear symptoms.

### A. Pod is Pending with `volume node affinity conflict`

1. **Check:** `kubectl describe pod <pod>` and events.
2. **Check:** `kubectl get pv <pv> -o yaml`; inspect `spec.nodeAffinity`.
3. **Check:** `kubectl get nodes -L topology.kubernetes.io/zone,kubernetes.io/hostname`.
4. **Likely causes:** volume belongs to a different node/zone; Pod node affinity or topology spread excludes the compatible node; node labels are missing or incorrect.
5. **Safe remediation:** restore the required node/zone if possible, correct verified labels through the platform process, or recover the application onto a new volume through a supported replica/backup workflow.
6. **Verify:** Pod is on a compatible node, volume mounted, application data and health verified.
7. **Prevent:** topology-aware provisioning, placement audits, maintenance testing.
8. **[VERIFY]:** exact affinity generated by the CSI/local driver and any provider-specific recovery options.

### B. PVC is Pending under `WaitForFirstConsumer`

1. **Check:** is there a Pod referencing the claim?
2. **Check:** `kubectl describe pvc <claim>` and the consuming Pod's events.
3. **Likely causes:** no consumer Pod yet (expected); no eligible node; resource/taint/affinity/spread conflict; unavailable provisioner; insufficient backend capacity.
4. **Safe remediation:** create/inspect the intended consumer; resolve the actual scheduling constraint or backend capacity issue. Do not switch binding mode blindly.
5. **Verify:** events show binding/provisioning progress and the PV topology is compatible with the scheduled Pod.
6. **Prevent:** test class behavior with the actual driver and keep capacity/topology evidence.
7. **[VERIFY]:** driver provisioning events and capacity tracking support.

### C. StorageClass topology excludes eligible nodes

1. **Check:** `kubectl describe storageclass <class>` and `kubectl get nodes -L topology.kubernetes.io/zone`.
2. **Check:** compare `allowedTopologies` values to actual node labels and driver-supported topology keys.
3. **Likely causes:** wrong zone values, missing labels, wrong key, or a policy that excludes every eligible node.
4. **Safe remediation:** plan a corrected class for new claims and migrate data through the supported path. Do not assume changing a class moves existing volumes.
5. **Verify:** a disposable test claim provisions in an intended domain.
6. **Prevent:** admission checks and configuration review.
7. **[VERIFY]:** whether the driver supports the chosen key and how existing PVs are affected.

### D. Stateful replicas concentrate in one zone

1. **Check:** `kubectl get pods -o wide` and node zone labels; inspect the workload's spread selector.
2. **Check:** ensure the selector matches the Pods' own labels; inspect `DoNotSchedule` versus `ScheduleAnyway`.
3. **Likely causes:** wrong/missing labels, missing eligible zones, best-effort spread, insufficient capacity, operator templates overriding expected placement.
4. **Safe remediation:** correct verified labels/configuration and use the database/operator's supported relocation or replica-rebuild process.
5. **Verify:** both Kubernetes placement and database member/replication state.
6. **Prevent:** run the audit regularly and test node-pool replacement.
7. **[VERIFY]:** operator-specific placement and anti-affinity settings.

### E. Node/zone is lost and volumes cannot attach elsewhere

1. **Check:** node/zone health, PV topology, Pod events, `VolumeAttachment`, CSI logs, backend status.
2. **Likely causes:** zonal restriction, old attachment not released, backend outage, or local-only data.
3. **Safe remediation:** follow backend detach/reattach rules; restore the zone or recover from another replica/backup. Confirm fencing and database safety before promotion.
4. **Verify:** attach/mount succeeds and application-level data is correct.
5. **Prevent:** test the exact failure path and document RPO/RTO.
6. **[VERIFY]:** provider's volume accessibility and failover contract.

### F. `Multi-Attach` or stale `VolumeAttachment`

1. **Check:** Pod/PV events and the relevant `VolumeAttachment` object; inspect CSI external-attacher and driver logs.
2. **Likely causes:** old node still owns the attachment, backend detach is pending, or the backend forbids multi-node attach for this volume mode.
3. **Safe remediation:** verify old-node fencing and follow the driver's documented recovery procedure.
4. **Verify:** backend confirms safe detach/attach; mount and application checks succeed.
5. **Prevent:** monitor attach errors and rehearse node-loss recovery.
6. **[VERIFY]:** do not use fixed timeout assumptions; check controller/driver/provider documentation. Never delete attachment objects as a generic shortcut.

### G. Local PV's node disappeared

1. **Check:** PV `nodeAffinity`, node status, local storage path/host ownership, and whether the node can return.
2. **Likely causes:** node/container loss, disk failure, or local path not present on replacement node.
3. **Safe remediation:** restore the original node/data if possible; otherwise use the application's replica/backup recovery process. Do not relabel a replacement node to impersonate the old data location.
4. **Verify:** data integrity and application recovery.
5. **Prevent:** use local PVs only with an explicit node-loss plan.
6. **[VERIFY]:** local provisioner behavior and data recovery capabilities.

### H. Topology spread blocks scheduling because fewer domains remain

1. **Check:** Pod events, eligible nodes, zone labels, taints, node affinity, and the topology spread constraint.
2. **Likely causes:** `DoNotSchedule`, `maxSkew`, insufficient eligible domains/capacity, or missing topology labels.
3. **Safe remediation:** decide whether strict placement or temporary availability is the correct policy; change the workload policy only through review. Do not silently weaken a safety constraint during an incident.
4. **Verify:** placement is consistent with the chosen policy and the application retains quorum/data safety.
5. **Prevent:** test planned maintenance and zone-loss cases.
6. **[VERIFY]:** version-specific topology spread fields and the scheduler's eligible-domain behavior.

## 7.11 Production design-review checklist

### Topology and failure domains

- [ ] Node/rack/zone/region failure domains are explicitly identified.
- [ ] Zone labels are verified against provider/platform metadata.
- [ ] Missing or incorrect labels are monitored.
- [ ] Failure-domain independence assumptions are documented.

### StorageClass and binding mode

- [ ] StorageClass `provisioner`, parameters, reclaim policy, and binding mode are reviewed.
- [ ] `WaitForFirstConsumer` is used where appropriate for topology-aware provisioning.
- [ ] Any use of `Immediate` is intentional and tested with the actual backend.
- [ ] `allowedTopologies` values match real labels and driver-supported topology.
- [ ] Storage capacity tracking requirements and support are verified.

### PV node affinity and driver support

- [ ] PV `nodeAffinity` is understood for every stateful claim.
- [ ] Local PVs have an explicit node-loss recovery plan.
- [ ] CSI driver and Kubernetes version compatibility are confirmed.
- [ ] Attach/detach, reattachment, and `Multi-Attach` recovery are documented.
- [ ] No procedure assumes that rewriting affinity relocates data.

### Replica placement and quorum

- [ ] Database replicas occupy intended independent failure domains.
- [ ] Database member roles and quorum requirements are known.
- [ ] StatefulSet replica count is not mistaken for data replication.
- [ ] Strict versus best-effort spread policy is an explicit decision.
- [ ] Node-pool changes and zone-loss scenarios have been tested.

### Recovery and data safety

- [ ] RPO and RTO are defined per failure scenario.
- [ ] Backup/restore is tested independently of replication.
- [ ] Promotion and rejoin/rebuild procedures are documented.
- [ ] Data integrity is checked after failover/recovery.
- [ ] No generic force-delete/finalizer-removal shortcut is used.

### Monitoring and alerts

- [ ] Pending Pods and scheduler reasons are monitored.
- [ ] PVC provisioning and mount failures are monitored.
- [ ] Attachment errors and stale attachments are investigated safely.
- [ ] Replica placement and zone concentration are audited.
- [ ] Database quorum, replication lag, and failed writes are monitored.
- [ ] Restore tests and recovery objective attainment are recorded.

### Failure testing

- [ ] Tests use disposable resources and have a clear stop/rollback plan.
- [ ] Node, zone, and regional failures are distinguished.
- [ ] Simulations are not reported as proof of provider resilience.
- [ ] Evidence and limitations are captured after every exercise.

### Cost and operational ownership

- [ ] Cross-zone traffic, replication overhead, and storage cost are measured.
- [ ] Platform, CSI/backend, database/operator, and application ownership is clear.
- [ ] Runbooks identify who can approve disruptive actions.
- [ ] The design's operational burden matches team capability.

### Provider/backend verification

- [ ] Actual volume zone/region accessibility contract is checked.
- [ ] Replication mode, consistency, and failure guarantees are checked.
- [ ] CSI topology keys and attachment semantics are checked.
- [ ] Controller behavior and recovery steps are checked for exact versions.
- [ ] CloudNativePG or other operator documentation is checked if used.
- [ ] Every unresolved claim is tracked as `[VERIFY]`, with an owner and validation method.

## 7.12 Self-check questions and answer key

### Questions

1. Define a failure domain and name four common levels.
2. Why can a Pod remain Pending even when CPU and memory are available?
3. What does PV `spec.nodeAffinity` tell you?
4. How do `topology.kubernetes.io/zone` and `kubernetes.io/hostname` differ conceptually?
5. What is the key difference between `Immediate` and `WaitForFirstConsumer`?
6. A PVC using WFFC has no Pod consuming it. Is the Pending claim automatically stuck? Explain.
7. What does `allowedTopologies` restrict, and what can it not do?
8. Why is a toleration not a guarantee that a Pod will run on a tainted node?
9. A database StatefulSet has three Pods in three zones. What additional evidence is required before calling the database highly available?
10. Explain `DoNotSchedule` versus `ScheduleAnyway` for topology spread.
11. A single zonal volume is bound to zone A. The Pod is forced to zone B. What evidence would you inspect first, and what is an unsafe “fix”?
12. For a majority-based system, how many votes are needed out of three and out of five? Why does that not by itself prove zone resilience?
13. Compare the RPO risks of synchronous and asynchronous replication, stating the assumptions.
14. A `Multi-Attach` event appears after node failure. Why should an operator not immediately delete the `VolumeAttachment`?
15. What can and cannot be concluded when a local PV's node disappears?
16. Why does a `kind` cluster with fake zone labels not prove real zonal resilience?
17. The audit script reports `UNKNOWN` because a node lacks a zone label. Should this count as a pass? Why?
18. After a zone returns, will topology spread automatically move existing Pods to rebalance the system? What else may be needed?
19. Why are replication and backup separate controls?
20. Name at least five evidence types to collect during a zonal storage incident.

### Answer key

1. A failure domain is a group of components that may fail together. Common levels are node, rack, zone, and region.
2. The scheduler also checks node/volume affinity, taints/tolerations, Pod affinity, topology spread, PVC binding, and other constraints. Available resources alone do not make a node feasible.
3. It declares node labels/fields that must match for the PV to be usable. It is a placement/access constraint, not a data migration mechanism.
4. Zone labels identify a broader topology domain; hostname labels identify a node. Exact label presence and values must be inspected.
5. Immediate binding/provisioning starts when the claim is created; WFFC waits for a consuming Pod so scheduling constraints can inform placement.
6. No. WFFC intentionally delays binding until a consuming Pod exists. Inspect the consumer and events before diagnosing a failure.
7. It restricts the topologies in which dynamic provisioning is allowed, according to driver support. It cannot make a backend support a zone or topology it does not support.
8. A toleration allows the scheduler to consider a tainted node; resource, affinity, topology, and other constraints still apply.
9. Confirm application/database replication, member roles, quorum, independent volumes/domains, promotion/fencing behavior, monitoring, tested recovery, and backup/restore. Three Pods alone prove none of those.
10. `DoNotSchedule` makes the spread limit hard and can leave Pods pending. `ScheduleAnyway` treats balance as a preference and can permit concentration when constraints require it.
11. Inspect Pod events, PV affinity, node labels, PVC binding, and StorageClass. Unsafe fixes include deleting the claim, removing affinity without moving data, or forcing the Pod onto an incompatible node.
12. Three members need two votes; five need three. This assumes majority-based voting and independent healthy members. Placement, roles, network partitions, application protocol, and failure correlation still matter.
13. Synchronous replication can reduce loss of acknowledged writes if acknowledgment waits for the defined remote durability condition, but can increase latency or reduce write availability. Asynchronous replication can acknowledge before remote copies catch up, so recent writes may be lost. Actual behavior depends on protocol and configuration.
14. The backend may still have the volume attached, or the old node may not be safely fenced. Deleting the object can remove bookkeeping without proving detach safety.
15. The data may be inaccessible temporarily if the node returns, or permanently lost if the sole local copy is destroyed. Inspect the actual storage and recovery options; do not assume either outcome.
16. `kind` nodes share one host and fake labels only affect scheduling. It does not simulate independent cloud infrastructure, zonal block storage, or provider control-plane behavior.
17. No. Missing labels mean the script cannot establish topology alignment; the result must remain UNKNOWN until verified.
18. Not necessarily. Spread constraints influence scheduling but do not guarantee eviction/rebalancing of existing Pods. The database/operator may need a supported rejoin, replica rebuild, or leader-transfer procedure.
19. Replication can propagate accidental deletion or corruption; backup provides a separate recovery point and must be tested independently.
20. Context/timestamp, node status and labels, Pod events, PVC/PV YAML, StorageClass, VolumeAttachment, CSI/provider logs, database quorum/roles/lag, recent changes, and backup status are examples.

## 7.13 Evidence artifacts and completion gate

Use a personal evidence directory; this lesson does not create additional repository files.

```text
m05-u7-evidence/
├── 01-context-and-nodes/
│   ├── context.txt
│   ├── nodes-before.txt
│   ├── nodes-during.txt
│   └── nodes-after.txt
├── 02-storage/
│   ├── storageclasses.yaml
│   ├── pv-before.yaml
│   ├── pvc-before.yaml
│   └── driver-inventory.txt
├── 03-scheduling-mismatch/
│   ├── pod-describe.txt
│   ├── pv-node-affinity.yaml
│   └── events.txt
├── 04-binding-mode/
│   ├── class.yaml
│   ├── pvc-events.txt
│   └── observation.md
├── 05-zone-simulation/
│   ├── pods-before.txt
│   ├── pods-during.txt
│   ├── events-during.txt
│   └── recovery-notes.md
├── 06-audit/
│   ├── audit_topology.py
│   └── audit-output.txt
├── 07-cleanup/
│   └── cleanup-verification.txt
└── 08-review/
    ├── incident-review.md
    └── adr.md
```

Capture evidence with commands such as:

```bash
kubectl config current-context > context.txt
kubectl get nodes -L topology.kubernetes.io/zone,kubernetes.io/hostname -o wide
kubectl get storageclass -o yaml
kubectl get pv -o yaml
kubectl -n m05-u7-lab get pvc -o yaml
kubectl -n m05-u7-lab describe pod m05-u7-mismatch
kubectl -n m05-u7-lab get events --sort-by=.metadata.creationTimestamp
python3 audit_topology.py m05-u7-spread
```

Adapt output redirection paths to your evidence folder. Sanitize sensitive names before sharing. Do not invent evidence if a step was not run.

### Completion gate

The unit is complete when you can:

- explain the difference between Pod placement, volume topology, database replication, and backup;
- diagnose a volume-affinity Pending Pod using events and PV/node evidence;
- explain when WFFC is expected to leave a claim unbound;
- demonstrate the static local PV mismatch and capture evidence;
- describe the actual StorageClass/provisioner in your lab without guessing;
- label fake zones as a scheduling-only simulation;
- explain why the lab cannot prove cloud zonal resilience;
- submit an audit output that reports unknown/missing topology honestly;
- produce a failure scenario matrix and an ADR with explicit assumptions;
- state which production evidence is still required from the exact Kubernetes version, CSI driver, provider, and database/operator.

If you did not have a topology-aware CSI driver, mark the dynamic provisioning comparison “conceptual/not reproduced.” That is a valid, honest outcome.

## 7.14 Sources and verification notes

The following official documentation is the starting point for verification. Documentation pages can change; confirm the Kubernetes release, CSI driver version, and provider/backend before operational use.

1. **Kubernetes — Storage Classes**  
   https://kubernetes.io/docs/concepts/storage/storage-classes/  
   Relevant topics: `volumeBindingMode`, `Immediate`, `WaitForFirstConsumer`, `allowedTopologies`, and provisioning parameters.

2. **Kubernetes — Persistent Volumes**  
   https://kubernetes.io/docs/concepts/storage/persistent-volumes/  
   Relevant topics: PV/PVC lifecycle, local volumes, node affinity, reclaim policy, and storage binding.

3. **Kubernetes — Volumes**  
   https://kubernetes.io/docs/concepts/storage/volumes/  
   Relevant topics: volume types, CSI volume integration, and driver compatibility.

4. **Kubernetes — Pod Topology Spread Constraints**  
   https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/  
   Relevant topics: `maxSkew`, `topologyKey`, `DoNotSchedule`, `ScheduleAnyway`, eligible domains, and interaction with node affinity.

5. **Kubernetes — Storage Capacity**  
   https://kubernetes.io/docs/concepts/storage/storage-capacity/  
   Relevant topics: `CSIStorageCapacity`, CSI driver support, WFFC scheduling, and limitations.

6. **Kubernetes API reference — StorageClass**  
   https://kubernetes.io/docs/reference/kubernetes-api/storage/storage-class-v1/  
   Relevant topics: field definitions and API semantics.

7. **Kubernetes API reference — VolumeAttachment / storage API**  
   https://kubernetes.io/docs/reference/kubernetes-api/storage/  
   Relevant topics: attachment intent and storage API objects.

8. **kind — Quick Start / Configuration**  
   https://kind.sigs.k8s.io/docs/user/quick-start/  
   https://kind.sigs.k8s.io/docs/user/configuration/  
   Relevant topics: cluster creation, node containers, and cluster configuration. Confirm details for the installed kind version.

9. **CSI specification and driver documentation**  
   https://github.com/container-storage-interface/spec  
   Relevant topics: CSI interface contract. The spec alone does not define a particular vendor's zonal semantics; also consult the official driver documentation and compatibility matrix.

10. **Database/operator documentation, if used**  
    For CloudNativePG, consult the official documentation at https://cloudnative-pg.io/documentation/ for the exact operator version, replication model, scheduling settings, and recovery procedures. This lesson's mandatory lab does not require CloudNativePG.

11. **Provider-specific storage documentation**  
    Use the official documentation for the actual cloud/backend in production. Verify volume zone accessibility, regional replication, consistency and acknowledgment semantics, attachment limits, failure behavior, and recovery procedures. No provider-specific guarantee is assumed here.

### Claim register

| ID | Claim | Source/document section | Confidence | Tag |
|---|---|---|---|---|
| C1 | `Immediate` is the default binding mode when `volumeBindingMode` is unset | Kubernetes Storage Classes | High for documented API behavior; confirm release | [VERSION-SENSITIVE] |
| C2 | WFFC delays binding/provisioning until a consuming Pod allows scheduling constraints to be considered | Kubernetes Storage Classes | High for documented API behavior | [VERSION-SENSITIVE] |
| C3 | `allowedTopologies` restricts where dynamic provisioning may occur, subject to plugin support | Kubernetes Storage Classes / StorageClass API | High for documented field; driver-specific effects vary | [VERIFY] |
| C4 | PV `nodeAffinity` can restrict the nodes that can use a volume | Kubernetes Persistent Volumes / local volumes | High for documented API behavior | [VERSION-SENSITIVE] |
| C5 | `DoNotSchedule` can leave a Pod unscheduled when spread constraints cannot be satisfied; `ScheduleAnyway` is preferential | Kubernetes Pod Topology Spread Constraints | High for documented API behavior | [VERSION-SENSITIVE] |
| C6 | Storage capacity tracking requires compatible Kubernetes and CSI support and does not guarantee successful provisioning | Kubernetes Storage Capacity | High for documented behavior; exact version matters | [VERSION-SENSITIVE] |
| C7 | `VolumeAttachment` represents attach/detach intent for applicable drivers | Kubernetes storage API reference | High for object purpose; workflow details vary | [VERIFY] |
| C8 | A local PV's node loss can make its data unavailable or lost | Kubernetes local-volume docs plus physical locality | High conceptually; actual recovery depends on environment | [VERIFY] |
| C9 | Kind worker labels can simulate scheduling topology but do not create independent physical/cloud zones | kind architecture and lab design | High conceptually | [ILLUSTRATIVE] |
| C10 | Three/five member majority thresholds are 2/3 for a simple majority system | Majority arithmetic | High under stated assumption | [ASSUMPTION] |
| C11 | Synchronous/asynchronous replication trade-offs depend on protocol and acknowledgment semantics | Database/operator's official replication documentation | General engineering principle; not a claim about one product | [VERIFY] |
| C12 | A `Multi-Attach` event should be resolved using driver/backend guidance rather than deleting metadata blindly | Kubernetes storage objects plus CSI/provider behavior | General safety guidance; exact recovery varies | [VERIFY] |
| C13 | The audit script can recognize only standard zone/hostname PV affinity patterns | Script logic in this lesson | High; known limitation | [ILLUSTRATIVE] |

### Exact verification steps before production

1. Record `kubectl version`, distribution, and control-plane/node versions.
2. Record the StorageClass YAML and CSI driver image/version.
3. Check the driver's compatibility matrix and topology/attachment documentation.
4. Verify which topology labels are emitted and whether `allowedTopologies` uses those exact keys.
5. Confirm the backend's zone/region accessibility, replication, and consistency contract.
6. Test `WaitForFirstConsumer`, capacity, and attach/detach behavior in a disposable environment matching production.
7. Confirm database operator placement and replica-recovery procedures for the exact operator version.
8. Run a controlled failure exercise and record measured RPO/RTO; do not infer them from architecture diagrams alone.

## 7.15 Independent technical audit

### Audit summary

This lesson has been statically reviewed against the requested Unit 7 coverage and the cited official Kubernetes documentation pages available during authoring. It was **not executed in a live Kubernetes/kind environment**. No lab output, benchmark, provider behavior, or production recovery time is claimed as observed.

### Audit result table

| Check | PASS/FIXED/OPEN | Evidence | Residual risk |
|---|---|---|---|
| Completeness | PASS | Required headings 7.0–7.15 and requested core topics are included | Actual syllabus file was not separately available for line-by-line comparison in this turn; prompt's stated requirements were used |
| Technical correctness | PASS with OPEN items | Generic Kubernetes fields are explained; unknown provisioner names are placeholders, not fabricated drivers | Manifest behavior still depends on installed Kubernetes/kind and local storage setup |
| Currency | OPEN | Official current Kubernetes pages for StorageClasses, topology spread, storage capacity, volumes, and API references were consulted | Confirm release-specific behavior and fields against learner's exact version |
| Topology truthfulness | PASS | Fake zones are repeatedly described as labels/scheduling simulation only | A reader may still overgeneralize from a local simulation; completion gate explicitly forbids that |
| Data safety | PASS | Disruptive operations are labeled and context-guarded; no force-delete or finalizer-patching fix is prescribed | User must correctly identify exact worker/container before lab disruption |
| Lab feasibility | PASS with OPEN items | No paid services; no more than three workers; lightweight test Pods; no heavy stack | Actual resource use and WSL2 disk reclamation vary by host; verify capacity before running |
| Cross-module consistency | PASS | References M03/M04, M05 Units 1–6, Unit 8, M13/M14, and M15 by scope | Other module contents were not independently opened during this authoring turn |
| Fabrication scan | PASS | Expected output is labeled illustrative; no actual lab execution or fixed timeout is claimed | Provisioner/driver-specific behavior remains intentionally unasserted |
| SRE review | PASS with residual risks | Five likely misleading interpretations are addressed below | Exact provider and database guarantees require their own documentation and tests |

### Five most likely ways this lesson could mislead an operator

1. **Mistaking fake zone labels for real fault isolation.**  
   Resolution: the lesson explicitly says kind nodes share one host and fake labels simulate scheduling only; no cloud-zone resilience is proven.

2. **Assuming a WFFC claim should bind before a consumer Pod exists.**  
   Resolution: the lesson states that an unbound claim may be expected until a consuming Pod exists and directs the learner to inspect events.

3. **Treating three spread Pods as a highly available database.**  
   Resolution: the spread demo uses `emptyDir` and a sleeping container, with explicit warnings that it has no database replication or persistent state.

4. **Treating PV affinity as metadata that can be edited to move data.**  
   Resolution: the lesson prohibits affinity edits as a generic recovery fix and requires a supported data migration/recovery process.

5. **Assuming `Multi-Attach`, synchronous replication, or regional storage has one universal behavior.**  
   Resolution: the lesson avoids fixed controller timeouts and universal RPO claims; it requires exact CSI/provider/database documentation and tests.

### Remaining `[VERIFY]` items

- The learner's Kubernetes and kind versions, and any distribution-specific scheduler behavior.
- The actual default StorageClass, provisioner, CSI driver, and whether its local data path survives any particular node/container operation.
- The exact local-PV manifest behavior in the installed environment, including directory permissions and event wording.
- Whether the chosen CSI driver supports WFFC, `allowedTopologies`, topology-aware provisioning, and storage capacity tracking.
- Provider-specific zone/region boundaries, detach/reattach semantics, and volume replication guarantees.
- Database/operator-specific quorum, synchronous/asynchronous replication, promotion, and rejoin procedures.
- Version-specific topology spread fields and local PV/PV-affinity update restrictions.
- Runtime validation of the audit script and lab manifests; these were not executed in this environment.

**Final audit status:** The requested lesson content is present and statically reviewed; live validation is OPEN. Use the lesson as a learning artifact, not as a substitute for the exact Kubernetes, CSI driver, provider, and database/operator runbooks.
