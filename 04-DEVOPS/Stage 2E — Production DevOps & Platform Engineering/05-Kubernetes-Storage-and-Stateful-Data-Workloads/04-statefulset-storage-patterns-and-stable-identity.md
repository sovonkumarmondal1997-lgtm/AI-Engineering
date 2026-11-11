## Unit 4 — StatefulSet storage patterns and stable identity

**Target file:** 04-statefulset-storage-patterns-and-stable-identity.md  |  **Estimated time:** 6–9 hours  |  **Prerequisites:** Units 1–3, M03 StatefulSet/probes/PDB/RBAC foundations, M04 Services/DNS

**Core tools:** kubectl, kind, YAML, a small synthetic stateful workload  |  **Awareness:** operators, consensus, managed databases  |  **Last reviewed:** 2026-10-28  |  **Kubernetes/tool baseline assumed:** Kubernetes APIs commonly available in recent supported releases and kind on a compatible local container runtime; exact feature gates, defaults, and patch-level behavior are **[VERIFY]** against the installed cluster and official documentation.

### 4.0 Why this matters in production

Imagine a database Pod is recreated after a node incident. The new Pod has a different IP, a client still caches the old address, and the service reports the Pod as Ready before the database has caught up with its peers. Separately, an operator sees a StatefulSet Pod stuck in `Terminating` and force-deletes it. If the old node was only partitioned—not actually stopped—the old database process may still be writing to storage while a replacement starts. The result can be corruption, competing writers, or a split-brain event.

A StatefulSet is useful because it gives Pods stable ordinal identity and predictable storage-claim relationships. It does not turn a database into a replicated, highly available database. Kubernetes can create Pods and mount volumes; the database or broker must still implement replication, leader election, quorum, fencing, recovery, and data correctness. The storage backend must support the required access, durability, attachment, and failure semantics. DNS provides discovery, not a guarantee that every client immediately reconnects.

This unit teaches the boundary between those responsibilities. The labs use tiny synthetic markers on a disposable `kind` cluster. They demonstrate Kubernetes mechanics, not production durability. A kind worker is a container, and local node-backed storage does not simulate independent availability zones or replicated storage. Never use a production namespace or real database data for the failure-injection lab.

### 4.1 Learning objectives

By the end of this unit, you should be able to:

- **[L1]** Explain StatefulSet guarantees and non-guarantees, and trace a Pod ordinal through a headless Service, DNS name, PVC, PV, and storage backend.
- **[L1]** Derive a per-replica PVC name using `<claim-template-name>-<statefulset-name>-<ordinal>` and verify the claim-to-Pod relationship with `kubectl`.
- **[L1/L2]** Predict and verify the effects of scale-up, scale-down, rolling updates, and PVC retention settings without assuming that scale-down deletes data.
- **[L2]** Select and inspect `podManagementPolicy`, `updateStrategy`, `partition`, `minReadySeconds`, probes, termination grace, and disruption/topology settings.
- **[L2/L3]** Design a safe stateful rollout and scale operation that checks application health and replication state, not only Kubernetes Pod readiness.
- **[L3]** Explain why ordinal identity and init scripts do not implement replication, leader election, quorum, rebalancing, or fencing.
- **[L3/L4]** Diagnose common PVC, StorageClass, ordinal, rollout, DNS, and node-loss incidents using read-only evidence before considering changes.
- **[L4]** Choose between a hand-managed StatefulSet, an operator, a managed database service, or not running the database on Kubernetes based on recovery objectives and operational ownership.

### 4.2 Concept map and vocabulary

```text
StatefulSet (name: marker-db)
  ├── Pod ordinal: marker-db-0
  │     ├── stable DNS identity via headless Service:
  │     │     marker-db-0.marker-db-hs.<namespace>.svc.<cluster-domain>
  │     └── volumeClaimTemplates (name: data)
  │           └── PVC: data-marker-db-0
  │                 └── PV (provisioned/bound according to StorageClass)
  │                       └── storage backend / node-local path / CSI driver
  ├── Pod ordinal: marker-db-1 → PVC: data-marker-db-1 → PV/storage
  └── Pod ordinal: marker-db-2 → PVC: data-marker-db-2 → PV/storage

Kubernetes controls identity, scheduling, Pod lifecycle, claims and rollout mechanics.
The database/operator controls membership, replication, leader election, quorum,
application-level consistency, recovery and safe reconfiguration.
The storage implementation controls actual persistence, attachment and failure semantics.
```

A typical fully qualified Pod DNS name has this illustrative form:

`<pod-name>.<headless-service-name>.<namespace>.svc.<cluster-domain>`

For example, `marker-db-0.marker-db-hs.storage-lab.svc.cluster.local` is illustrative; derive the real name from the Pod, Service, namespace, and cluster DNS domain rather than assuming every cluster uses `cluster.local`. A stable DNS name is not a stable IP address. Clients must handle DNS caching, connection failures, retries, and reconnects.

PVC naming follows:

`<claim-template-name>-<statefulset-name>-<ordinal>`

With a claim template named `data`, StatefulSet `marker-db`, and ordinal `0`, the claim is `data-marker-db-0`. The claim is associated with a particular Pod ordinal, not a generic pool shared by all replicas.

| Term | Precise meaning | Common misconception |
|---|---|---|
| StatefulSet | Controller that manages Pods with stable identities and ordered or parallel lifecycle behavior | It replicates the database contents |
| Ordinal | Numeric identity suffix for a StatefulSet Pod, usually starting at zero unless a supported start-ordinal configuration changes it | It is a database role such as primary or replica |
| Headless Service | Service with `clusterIP: None`, used for direct endpoint discovery and StatefulSet Pod DNS | It freezes a Pod IP |
| `volumeClaimTemplates` | Claim template used to create a distinct PVC for each StatefulSet Pod identity | Editing it resizes or migrates existing claims |
| PVC / PV | Namespaced claim / cluster storage resource bound to a backing storage implementation | A PVC is itself a backup |
| `OrderedReady` | Default Pod management policy in common StatefulSet configurations; creates/deletes in order and waits for readiness in relevant steps | Readiness means replication is caught up |
| `Parallel` | Relaxes ordered creation/deletion behavior | It adds consistency or quorum |
| `partition` | Ordinal threshold controlling which Pods receive a rolling-update revision | It automatically evaluates canary metrics |
| PDB | Voluntary-disruption budget used by supported eviction workflows | It prevents node failures or guarantees database availability |
| Fencing | Mechanism that ensures a potentially stale process cannot continue acting as a writer | Deleting a Pod object necessarily stops its process |
| Operator | Controller that encodes application-specific lifecycle and recovery procedures | It removes the need for backups and on-call expertise |

**Responsibility boundary:** Kubernetes can report a Pod `Ready` because its configured readiness check passes. That is not proof that the application has quorum, is caught up, can safely become primary, or contains correct data. Those are application-specific checks and must be designed and observed separately.

### 4.3 Level 1 — Beginner

#### 4.3.1 What a StatefulSet gives you

A StatefulSet is appropriate when replicas need stable identities or stable per-replica storage relationships. Its main primitives are:

1. **Stable ordinal identity:** Pods have predictable names such as `marker-db-0`, `marker-db-1`, and `marker-db-2`.
2. **Stable network identity:** when associated with a suitable headless Service, each Pod can be discovered through a predictable DNS name.
3. **Stable storage association:** a `volumeClaimTemplates` entry creates a separate PVC for each ordinal.
4. **Lifecycle ordering:** management and update policies determine how Pods are created, deleted, and updated.

A StatefulSet does **not** provide data replication, application failover, backup, restore, consistency, quorum, leader election, partition rebalancing, or resharding. Three Pods with three PVCs are three separate storage locations unless the application copies data between them. A `replicas: 3` field is not a database HA design.

#### 4.3.2 Headless Service and stable DNS

A headless Service is declared with `clusterIP: None`. It selects the StatefulSet Pods and supplies the governing Service name used for per-Pod DNS identity. The Service selector must match the Pod labels. The StatefulSet’s `spec.serviceName` must name the intended headless Service.

DNS records can be affected by readiness and cluster DNS behavior. Verify the actual endpoints and DNS response. A client may cache an address longer than desired, retain a broken TCP connection, or fail to retry. Design client connection pools with bounded retries, reconnect logic, and application-aware handling.

#### 4.3.3 Per-replica claims and storage location

The sample labs use a claim template called `data`. The resulting PVCs are named `data-marker-db-0`, `data-marker-db-1`, and `data-marker-db-2`. Inspect them rather than inferring from naming alone:

```bash
kubectl get sts,pods,pvc -n storage-lab
kubectl describe sts marker-db -n storage-lab
kubectl describe pod marker-db-0 -n storage-lab
kubectl get pvc data-marker-db-0 -n storage-lab -o yaml
```

On a local kind setup, storage may be backed by a provisioner and a path associated with a kind node container. The exact implementation depends on the installed StorageClass and provisioner. Inspect it:

```bash
kubectl get storageclass
kubectl get pvc -n storage-lab -o wide
kubectl get pv -o wide
kubectl describe pv <pv-name>
```

Do not assume that a `Bound` claim implies multi-node durability. A local PV can be bound and working while remaining tied to one node. kind workers do not represent separate physical zones, and local lab storage is not a production backup.

#### 4.3.4 Scale-down does not automatically mean delete data

When a StatefulSet scales from three replicas to two, `marker-db-2` is removed as a Pod. The PVC for ordinal 2 commonly remains unless an applicable retention policy specifies otherwise. If the StatefulSet later scales back up, the same ordinal can use the same retained PVC. Confirm the claim and marker after every scale operation.

Before deleting a PVC, StatefulSet, or namespace, identify the exact target and whether its data is disposable. A PVC can outlive a Pod, and deletion behavior can also depend on StatefulSet retention policy, PV reclaim policy, provisioner, and backend. Never treat resource deletion as a backup or recovery mechanism.

### 4.4 Level 2 — Intermediate

#### 4.4.1 Pod management policy

`podManagementPolicy` controls StatefulSet Pod creation and deletion ordering:

- **`OrderedReady`** is the conventional default. Creation proceeds in ordinal order and waits for earlier Pods to become Ready before moving to the next; scale-down proceeds in reverse ordinal order. A readiness failure can therefore block later lifecycle actions.
- **`Parallel`** permits creation and deletion without waiting for each Pod to become Ready in the same ordered manner. It can shorten orchestration time but does not create replication, quorum, or consistency.

Choose the policy to match application bootstrap dependencies. Do not set `Parallel` just to “make the database faster” without understanding the application’s cluster-join behavior.

#### 4.4.2 Update strategies and staged rollout

`updateStrategy.type: RollingUpdate` allows the StatefulSet controller to update Pods toward the current Pod template. A `partition` can hold lower ordinals on the previous revision while higher ordinals update. For example, with three replicas and partition `2`, ordinal 2 is the eligible first test target; ordinals 0 and 1 remain on the prior revision until the partition is reduced. Verify the exact revision and ordinal behavior against the selected Kubernetes version and live StatefulSet status.

`OnDelete` means template changes do not automatically replace existing Pods; Pods are updated when they are deleted and recreated by the controller. This provides manual sequencing but also creates a risk that operators forget an outdated member.

A partition is a rollout control, not a canary analysis system. Evaluate application metrics, replication lag, error rates, logs, and recovery behavior before proceeding. Check `status.currentRevision`, `status.updateRevision`, Pod template image, and actual application health. Abort when the first updated member fails readiness, violates the error budget, or fails application-specific health checks.

#### 4.4.3 `minReadySeconds` and health semantics

`minReadySeconds` requires a Pod to remain Ready for a specified period before the StatefulSet considers it available for progression. It reduces reaction to a brief Ready transition; it does not prove the database is correct or caught up. Readiness should represent whether the instance can serve the intended traffic. A separate replication or quorum check may be needed.

Probe roles:

- **Startup probe:** protects slow-starting applications from premature liveness failures while startup is in progress.
- **Readiness probe:** controls whether the Pod is considered ready for normal traffic.
- **Liveness probe:** detects a process that should be restarted when the probe fails repeatedly.

A database replaying write-ahead logs (WAL) after a restart may be slow but healthy. A liveness probe that is too aggressive can repeatedly kill it and extend recovery. Do not copy probe endpoints from another image without verifying the chosen image’s documentation. See M03 Unit 3 for general probe semantics.

#### 4.4.4 PVC retention policy and template immutability

`persistentVolumeClaimRetentionPolicy` has `whenDeleted` and `whenScaled` dimensions, each commonly configured as `Retain` or `Delete` in versions that support the field. The policy changes whether claims are retained or deleted when the StatefulSet is deleted or scaled down. **[VERIFY]** feature availability, stability, default values, and API support against the Kubernetes version in the cluster using the official StatefulSet documentation and `kubectl explain statefulset.spec.persistentVolumeClaimRetentionPolicy`. Inspect the actual spec; do not assume the default from memory.

A production default is often to retain claims until a separately reviewed data-retention procedure decides otherwise. `Delete` may be appropriate for disposable test environments, but can turn an ordinary scale-down into data loss. The PVC’s deletion and the PV/backend reclaim behavior are separate layers: inspect the PVC, PV reclaim policy, events, and provisioner before making a claim about what data will remain.

`volumeClaimTemplates` is not a general live migration mechanism. Editing a template does not automatically resize existing PVCs or move their data to a different StorageClass. For expansion, follow Unit 3 (`03-volume-snapshots-cloning-and-expansion.md`) and verify StorageClass/PVC expansion support. For migration, create and validate replacement claims, copy or replicate data using an application-appropriate method, and perform a controlled cutover.

#### 4.4.5 Init containers, permissions, and data-directory layout

An init container may prepare a directory or adjust ownership before the main container starts. It must have only the privileges it needs. Avoid running a privileged recursive `chown` over a large volume on every restart without understanding its cost and security implications. Prefer an image and storage permission design that works with a non-root UID/GID. `fsGroup` can affect volume group ownership or access behavior depending on volume type and driver; verify the behavior for the selected CSI driver. Refer to M01 for image engineering and non-root container practices.

Filesystem roots may contain filesystem-created entries such as `lost+found`. Some database initialization commands expect an empty data directory and may reject a directory containing unrelated entries. For PostgreSQL, a dedicated subdirectory pattern can be used, for example mounting a volume at `/var/lib/postgresql/data` and setting an image-supported `PGDATA` path beneath it. **[VERIFY]** the exact path, environment variable behavior, UID/GID, and initialization semantics for the specific image tag. Do not assume all images use the same directory layout.

#### 4.4.6 Graceful termination, PDBs, and topology

When a Pod terminates, Kubernetes normally asks the container process to stop and observes the configured grace period. The application must handle `SIGTERM` correctly. Set `terminationGracePeriodSeconds` long enough for the application’s documented shutdown and checkpoint behavior, but bounded enough to avoid indefinite maintenance. Use `preStop` only when it has a specific, bounded purpose, such as invoking a documented drain endpoint. A sleep hook alone does not make shutdown safe.

A PodDisruptionBudget (PDB) can limit certain voluntary disruptions initiated through eviction-aware workflows. It does not prevent involuntary node loss, does not cover every deletion path, and does not guarantee database availability. For quorum systems, configure the budget only after calculating the minimum healthy membership needed by the application. See M03 Unit 5.

Anti-affinity and topology spread can help distribute Pods across nodes or topology domains. They are useful only when the cluster actually has those domains and sufficient capacity. In kind, worker containers are not independent physical failure domains. See M03 Unit 7 and M05 Unit 7 (`07-data-locality-zonal-failure-and-volume-affinity.md`) for storage locality and topology constraints.

### 4.5 Level 3 — Advanced

#### 4.5.1 Bootstrap is not ongoing replication

A common fragile pattern is to treat ordinal zero as primary and every other ordinal as a replica using a one-time init script. This fails to handle primary loss, promotion, split-brain prevention, stale membership, replication reconfiguration, rejoin after a long outage, credential rotation, or version upgrades. An ordinal is an identity label, not a database role.

Separate these concerns:

- **Bootstrap:** create initial application state and join a member to the cluster.
- **Ongoing replication:** continuously transfer and apply changes.
- **Leader election/promotion:** choose the active writer according to the application’s protocol.
- **Fencing:** prevent an old or partitioned writer from continuing to act as leader.
- **Rejoin/recovery:** reconcile a returning member’s state with the authoritative cluster state.

These responsibilities usually belong to the application itself or a domain-aware operator. A StatefulSet can supply predictable Pod names and volumes to such a system, but it cannot implement those protocols by itself. M05 Unit 5 (`05-running-databases-and-brokers-with-operators.md`) covers operators and application-specific lifecycle management.

#### 4.5.2 Consensus and quorum awareness

Raft-based systems and systems such as etcd, ZooKeeper, and Kafka using KRaft have their own membership, quorum, and leader-election rules. A StatefulSet’s ordered rollout is not a consensus protocol. Before replacing a member, know the required quorum, which member is leader, whether the remaining members are healthy, and whether the replacement can safely rejoin.

For a quorum-sensitive rollout, change one member at a time when required by the application’s rules. After each change, wait for the member to be healthy and replication or log catch-up to complete. Do not advance based only on Pod Ready. Use `partition` for controlled staging, but separately evaluate application metrics and health. Verify exact ordinal update behavior for the cluster version and update policy.

#### 4.5.3 Scaling is an application operation too

Increasing `spec.replicas` creates more Pods and claims; it does not necessarily add a database member correctly, rebalance partitions, redistribute shards, or change client routing. Scaling down removes a Pod identity but does not safely remove application membership or move data for you. Before scale-in, use the application’s documented decommission or rebalance workflow, confirm data movement, verify quorum, and only then reduce replicas.

For brokers, partitions and leaders may need reassignment. For sharded databases, data may need resharding and client metadata updates. For replicated databases, membership and replication slots or peer lists may need reconfiguration. These are application-specific procedures; never infer them from the StatefulSet manifest.

#### 4.5.4 PVC retention by environment

| Environment | Typical policy posture | Trade-off and guardrail |
|---|---|---|
| Local learning / ephemeral tests | Deletion may be acceptable if every resource is synthetic and disposable | Explicitly label the namespace and confirm target names before cleanup |
| Shared development | Usually retain or use separately managed cleanup with owner/TTL controls | Developers may need state across restarts; retained data can contain sensitive copies |
| Integration / staging | Retain until test evidence and recovery needs are satisfied; controlled cleanup | Snapshot/restore and data sanitization need ownership and documented criteria |
| Production | Prefer deliberate, reviewed retention and backup policy rather than incidental deletion | Retention is not backup; verify recovery, ownership, encryption, and deletion approvals |

The policy should be explicit, reviewed, and observed. Retention can preserve data after a workload disappears, which is useful for recovery but can also leave orphaned, costly, or sensitive volumes.

#### 4.5.5 Multi-volume Pods and recovery consistency

A database may separate data files, WAL, and logs across volumes for performance or operational reasons. This introduces additional failure and recovery considerations: the volumes may have different attachment constraints, capacities, retention, and snapshot support. Separate snapshots taken at different times are not automatically one coordinated recovery point. For application-consistent recovery, coordinate snapshots with the database’s supported freeze/checkpoint/backup process, or use a tested backup mechanism. See Unit 3 (`03-volume-snapshots-cloning-and-expansion.md`) for snapshots, cloning, expansion, and consistency limits.

M03 etcd snapshots are snapshots of Kubernetes control-plane state; they do **not** contain PV data. A recoverable application needs both Kubernetes resource recovery and a separately verified way to restore the underlying data.

#### 4.5.6 `ReadWriteOnce` versus `ReadWriteOncePod`

`ReadWriteOnce` (RWO) generally expresses read-write mounting from a single node; it does not universally mean a volume can be mounted by only one Pod in every circumstance. Multiple Pods on the same node may be able to use an RWO volume, depending on the volume implementation and configuration.

`ReadWriteOncePod` (RWOP) is intended to constrain a volume to use by a single Pod and has CSI and Kubernetes-version requirements. **[VERIFY]** support in the cluster, the CSI driver, sidecar versions, and the selected volume implementation before relying on it as a safety control. Access mode is not a substitute for application-level fencing.

#### 4.5.7 Shared-nothing versus shared storage

In a **shared-nothing** design, each member owns its local data and the application replicates or partitions it across members. This can reduce shared-storage contention but requires robust replication, membership, and recovery workflows. In a **shared-storage** design, multiple compute instances may access a common storage system when the backend and application support it. This may simplify some data-sharing patterns but introduces storage contention, locking, fencing, and backend availability considerations. Neither architecture is universally superior.

A local-volume Pod may not reschedule with its data after node drain or node loss. A PV with node affinity can constrain placement to the original node. Inspect PV topology, events, and the StorageClass before moving or deleting anything. See M05 Unit 7 for locality and volume affinity.

#### 4.5.8 DNS, sidecars, and shutdown coordination

DNS clients can cache answers; TCP connections can outlive a Pod’s usefulness or fail when the Pod terminates. Use bounded DNS caching, connection retries, jittered backoff, health-aware endpoint selection, and application-level reconnect logic appropriate to the client library. Verify the actual cluster DNS configuration rather than assuming a particular TTL.

Backup agents, exporters, log shippers, and other sidecars can share mounts with the main container. Check UID/GID and file permissions, read/write needs, resource requests, and whether the sidecar can keep files open during shutdown. Backup sidecars must not be treated as a substitute for tested off-cluster backup. Vendor-specific coordination and shutdown behavior must be verified against the chosen application and sidecar documentation.

### 4.6 Level 4 — Expert

#### 4.6.1 Node lost; Pod is `Terminating` or `Unknown`

**[VERSION-SENSITIVE] [VERIFY]** Exact node-shutdown and StatefulSet replacement behavior depends on Kubernetes version, node conditions, storage implementation, and configuration. Consult the current Kubernetes documentation on StatefulSets, node shutdown, Pod termination, and force deletion; inspect the live Pod, Node, PV, attachment objects, and events.

The key risk is uncertainty: the control plane may not know whether the old process has stopped. Deleting the API object does not prove the process is dead. A partitioned node may continue writing while a replacement Pod is scheduled. Before any manual deletion, establish that the old node/process is stopped or fenced and that storage is safely detached according to the backend’s documented behavior.

Safe decision tree:

```text
Pod stuck Terminating / Unknown
        |
        v
Collect read-only evidence: Pod, Node, events, PVC/PV, attachments, app health
        |
        v
Can the old node/process be reached and verified stopped?
        | YES                                  | NO / UNCERTAIN
        v                                      v
Verify storage detach/fencing and       Treat as potential live writer.
application quorum/state.              Do not force-delete as routine cleanup.
        |                                      |
        v                                      v
Follow documented recovery path         Escalate to infrastructure/storage owner;
for this version/backend;               establish fencing or safe isolation first.
restore/reattach only after proof.       Do not start a competing writer.
        |
        v
Verify member identity, integrity, replication catch-up, and client health.
```

`kubectl delete pod <pod> --force --grace-period=0` is a high-risk manual action. It removes the API object without waiting for normal confirmation of process termination. It must not be used as a routine fix. The required precondition is evidence that the old process is truly stopped/fenced and that storage attachment behavior is understood. If that cannot be established, stop and escalate.

#### 4.6.2 PVC accidentally deleted

1. **Contain:** stop further cleanup, scaling, or namespace deletion; notify the data owner and incident lead.
2. **Collect read-only evidence:** record the PVC name/UID, StatefulSet and Pod, namespace, PV name and status, reclaim policy, StorageClass, events, snapshots, and backend asset identifiers.
3. **Preserve:** do not delete related PVs, snapshots, backups, or backend storage assets. Avoid provisioning a replacement claim that could obscure evidence or attach an unexpected volume.
4. **Assess:** determine whether the PV still exists, whether the backend data remains, whether reclaim policy or provisioner actions have run, and whether a supported restore point exists.
5. **Recover only through a tested procedure:** recovery may involve re-binding or restoring to a new claim, but exact actions depend on PV state, backend behavior, and version. Do not promise recovery.
6. **Validate:** check application logs, data checksums or database-native integrity, expected record counts, and replication state before returning traffic.

Escalate immediately if the PV/backend has been deleted, reclaim behavior is unclear, or the only recovery point is untested.

#### 4.6.3 Claim-template change or StorageClass migration

Changing the claim template does not migrate existing data. Treat migration as a data-movement project:

1. Record current StatefulSet, claim, PV, StorageClass, access mode, topology, capacity, and ownership.
2. Verify a restorable backup or supported snapshot; perform a restore test where feasible.
3. Create new PVCs using the target StorageClass, respecting topology and access-mode requirements.
4. Copy data with an application-consistent method, or use application-native replication and catch-up.
5. Verify checksums, application-native consistency, permissions, capacity, and performance.
6. Define a controlled cutover, stop or fence writers as required, and record explicit rollback criteria.
7. Keep old data until the new deployment passes integrity and operational checks. Delete old resources only under a separate reviewed cleanup plan.

A parent-syllabus pattern may mention orphaning claims and recreating a StatefulSet. **[VERIFY]** exact supported procedure for the installed version. Do not perform an orphan-delete/recreate sequence without verified backups, ownership checks, and a rehearsed recovery plan. See Unit 3 for expansion and Unit 8 (`08-storage-troubleshooting-and-orphaned-volumes.md`) for orphaned-volume troubleshooting.

#### 4.6.4 Rolling update blocked by readiness

Start with read-only inspection:

```bash
kubectl get sts marker-db -n storage-lab -o yaml
kubectl get pods -n storage-lab -o wide
kubectl describe pod marker-db-2 -n storage-lab
kubectl get events -n storage-lab --sort-by=.lastTimestamp
kubectl logs marker-db-2 -n storage-lab --all-containers=true --tail=200
kubectl get pvc -n storage-lab -o wide
```

Check `status.currentRevision`, `status.updateRevision`, `spec.updateStrategy`, `partition`, image tags, Pod events, startup/readiness/liveness results, mounts, PVC binding, application logs, and cluster health. A blocked rollout may be caused by an invalid image, permission failure, unavailable storage, an overly aggressive probe, or an application-level quorum problem.

Do not blindly delete the blocked Pod or weaken health checks. First decide whether the updated member is safe to keep running. If a known-good prior template is available, use a reviewed rollback plan and confirm the application can safely return to that revision. Rollback is not automatically safe when data formats or database versions have changed.

#### 4.6.5 Unexpected ordinal or missing Pod/PVC

Verify the actual StatefulSet name, namespace, replica count, start-ordinal settings if supported, selector, claim-template names, Pod list, PVC list, owner references, and events. **[VERIFY]** support and behavior of `.spec.ordinals.start` in the chosen Kubernetes version. Do not manually rename a live Pod or attempt to renumber data directories. StatefulSet identity is controller-managed; data movement between ordinals requires an application-aware plan.

#### 4.6.6 Local-volume Pod cannot reschedule

Inspect the PV’s node affinity, volume topology, StorageClass, Pod scheduling events, node state, and whether the data still exists on the original node. A local PV generally cannot be moved to another node simply by deleting and recreating the Pod. If the original node and its storage are lost, recovery may require a backup or application replica. Do not remove PV affinity or force a replacement to mount an unrelated empty volume under the same identity without an explicit recovery plan.

#### 4.6.7 Decision framework: where should the database run?

| Operating model | Ownership and on-call | Backup, restore, failover, upgrades | Cost and portability | Best fit / cautions |
|---|---|---|---|---|
| Hand-managed StatefulSet | Highest burden; team owns manifests, runbooks, and application operations | Mostly manual unless separately engineered; team must prove replication and recovery | Potentially portable and low infrastructure entry cost, but engineering/on-call cost is real | Small, well-understood systems or learning; unsuitable when expertise and operational capacity are absent |
| StatefulSet managed by an operator | Team owns Kubernetes platform and operator lifecycle; operator automates domain workflows | Can automate backup, failover, and upgrades if explicitly supported and correctly configured; restore drills remain mandatory | Adds operator complexity and version coupling | Applications with mature, maintained operators and a team able to operate them |
| Managed database service | Provider owns much of the underlying platform; customer still owns schema, access, data policy, and application behavior | Service-dependent backups, failover, patching, and restore capabilities; verify RPO/RTO and test restores | Recurring service cost and potential provider coupling | Teams prioritizing product delivery over database infrastructure operations |
| Do not run database on Kubernetes | Database platform or another team/service owns runtime; app team consumes it | Depends on chosen platform; may reduce Kubernetes-specific failure modes | May simplify operations or increase integration cost | Often best when database lifecycle, performance, licensing, or recovery requirements exceed team/platform capability |

An operator encodes domain workflows; it does not eliminate the need for tested restore, capacity planning, security, monitoring, and incident ownership. “Run it on Kubernetes” is a design option, not a default objective.

### 4.7 SRE lens

#### Availability, recovery objectives, and rollout budgets

Define service-level objectives (SLOs) for the user-visible service, not merely “all Pods are Ready.” Define recovery time objective (RTO) and recovery point objective (RPO) based on business impact. Verify that the actual architecture and tested recovery procedure can meet them. StatefulSet identity does not establish either objective.

Before maintenance, calculate application quorum and the maximum number of members that may be unavailable simultaneously. For quorum-sensitive systems, use one-member-at-a-time changes when required, validate replication catch-up, and stop on predefined abort conditions. A PodDisruptionBudget is one control for voluntary eviction; it is not a complete maintenance plan.

#### Runbook fragment: node lost, Pod stuck `Terminating` / `Unknown`

**Symptom and impact:** StatefulSet Pod does not terminate cleanly after a node outage; replacement is blocked or its safety is uncertain.

**First safe read-only commands:**

```bash
kubectl get pod -n <namespace> <pod> -o wide
kubectl describe pod -n <namespace> <pod>
kubectl get node <node> -o yaml
kubectl get events -n <namespace> --sort-by=.lastTimestamp
kubectl get pvc -n <namespace> -o wide
kubectl get pv -o wide
kubectl get volumeattachments.storage.k8s.io
```

The `VolumeAttachment` resource may not be relevant or present for every storage implementation; inspect what the driver supports. Capture timestamps, Pod UID, node conditions, PVC/PV identity, backend attachment state, application membership, and recent logs.

**Avoid:** force deletion while the old node may still run; deleting the PVC/PV; manually detaching a volume without backend guidance; starting a second writer.

**Decision and escalation:** determine whether the node is powered off/fenced or merely unreachable. If uncertain, involve infrastructure and storage owners and establish fencing before proceeding. Follow the version/backend-specific recovery procedure only after process and attachment safety are established.

**Post-recovery:** verify that the correct volume and ordinal are mounted, inspect application-native integrity, confirm replication catch-up/quorum, check client reconnects and service error rates, and record the incident timeline.

#### Runbook fragment: PVC accidentally deleted

**Symptom and impact:** expected claim disappears or a Pod cannot mount its volume.

**Read-only evidence:** `kubectl get pvc,pv -A`, `kubectl describe pv <pv>`, events, StatefulSet YAML, StorageClass, snapshots, backup inventory, and backend asset IDs. Preserve output before making changes.

**Avoid:** cleaning up “orphaned” PVs; deleting snapshots; creating a same-named claim without checking what it may bind to; assuming a retained backend is recoverable.

**Decision and escalation:** determine whether the PV object and underlying data remain, what reclaim policy applied, and whether a tested restore exists. Escalate if the backend state is ambiguous or destructive reclaim has started. Restore to a new claim where the documented method supports it, then verify data integrity before cutover.

#### Runbook fragment: claim-template or StorageClass migration

**Symptom and impact:** desired storage attributes changed, but existing claims still use old capacity or class.

**Read-only evidence:** StatefulSet template, all PVC/PV specs, StorageClass definitions, capacity, topology/affinity, events, backend health, backup/snapshot evidence.

**Avoid:** expecting a template edit to migrate data; deleting old claims to “force” new ones; removing topology constraints without a storage plan.

**Decision and escalation:** choose supported in-place expansion only if the current class, driver, and filesystem support it; otherwise plan a new-claim migration with verified backup, copy/replication, integrity check, cutover, rollback, and old-data retention. See Unit 3 for expansion and Unit 8 for orphaned volumes.

#### Runbook fragment: rolling update blocked by a Pod that never becomes Ready

**Symptom and impact:** rollout stalls at an ordinal, leaving mixed revisions or reduced capacity.

**Read-only evidence:** StatefulSet `currentRevision`/`updateRevision`, update strategy and partition, Pod events, image, probes, mounts, PVC status, app logs, quorum and replication status.

**Avoid:** blind Pod deletion, lowering readiness thresholds without evidence, or continuing to update additional quorum members.

**Decision and escalation:** determine whether failure is image/configuration, storage/permissions, probe behavior, or application health. Pause progression by retaining the partition or using the approved rollout control, and use a tested rollback only if data/version compatibility permits. Escalate if quorum is threatened or data-format changes may have occurred.

#### Runbook fragment: unexpected ordinal or missing Pod/PVC

**Symptom and impact:** expected identity is absent, claim name is unexpected, or an ordinal appears to have a gap.

**Read-only evidence:** namespace, StatefulSet selector/replicas/start ordinal, Pod and PVC names, owner references, events, current/update revisions, PV affinity, and recent changes.

**Avoid:** manually renaming resources, copying one ordinal’s data onto another without application guidance, or deleting “extra” claims based only on names.

**Decision and escalation:** compare actual resources with the desired template and version-supported ordinal settings. Determine whether the object is pending, intentionally scaled down, retained, or genuinely missing. Use the application’s documented recovery or membership repair process.

#### Runbook fragment: local-volume Pod cannot reschedule after node loss

**Symptom and impact:** a Pod remains Pending because its volume is tied to a lost node or unavailable topology.

**Read-only evidence:** Pod scheduling events, PV node affinity, StorageClass, node condition, backend location, snapshots/backups, and application replicas.

**Avoid:** removing affinity or binding a different empty volume under the same identity as a shortcut.

**Decision and escalation:** determine whether the original storage can be recovered and safely reattached. If not, use a verified backup or application-native replica recovery. Escalate if the only copy is on the failed node. After recovery, verify checksums or database-native integrity, expected records, replication, and client traffic.

#### Error budgets, evidence, and recovery validation

Abort a rollout when an SLO burn threshold is exceeded, quorum is at risk, replication lag crosses the application’s safe limit, data-integrity checks fail, or the recovery path is no longer understood. Evidence should include manifests before and after, resource YAML, events, relevant logs, image digests, storage identifiers, timestamps, change approvals, and application-level checks. Keep evidence free of credentials and sensitive data.

A successful Pod restart is not proof of successful recovery. Require application-specific integrity checks, membership/replication validation, and client-level smoke tests. Document what was restored, from which recovery point, and what data-loss window remains.

### 4.8 Security lens

- **Least privilege:** restrict who can create or mutate StatefulSets, PVCs, PVs, StorageClasses, Secrets, and volume attachments. Limit `pods/exec` because a shell in a database Pod can expose data and credentials. Use namespace-scoped RBAC where possible and review cluster-scoped storage permissions separately.
- **Non-root execution and volume permissions:** use an image designed for non-root operation, pin its version/digest according to policy, and verify UID/GID ownership. `fsGroup` behavior depends on the volume and driver. Init containers that alter ownership should have minimal permissions and narrowly scoped mounts. See M01 for image engineering.
- **Secrets and diagnostics:** avoid printing credentials in environment dumps, debug output, logs, shell history, or backup-sidecar arguments. Do not expose production secrets to a temporary debug Pod merely to test DNS.
- **Pod Security Standards:** use restricted security settings where compatible; avoid privileged containers, hostPath mounts, host namespaces, and unnecessary Linux capabilities. If a storage driver requires an exception, document the narrow exception and owner.
- **Network segmentation:** limit database/broker ingress to approved application and operator identities using NetworkPolicy where supported. Confirm policy behavior and DNS egress requirements. See M04 for Services, DNS, and NetworkPolicy.
- **Supply chain and version pinning:** pin database images, sidecars, and operators to reviewed versions or digests; track compatibility and security advisories. Avoid floating tags in production.
- **Retained data access:** scale-down or workload deletion can leave PVCs behind. Define who can mount retained claims and how ownership is transferred. A cloned volume may contain credentials, customer data, tokens, or production-like information.
- **Sanitization:** before using a clone in development/test, apply an approved sanitization process and restrict network access. Do not assume a snapshot or clone is automatically safe to share.
- **Policy checks:** use a review checklist or CI policy to validate probes, resources, security context, PVC templates, retention policy, disruption settings, topology hints, and update strategy. This lesson does not assume that Kyverno, Gatekeeper, or another policy engine is installed.

### 4.9 Production checklist

#### Before deployment

- [ ] Choose the operating model based on team expertise, application support, RPO/RTO, upgrade needs, and cost.
- [ ] Confirm the StatefulSet is needed; document what the application/operator—not Kubernetes—does for replication, election, fencing, and recovery.
- [ ] Verify headless Service selectors and `spec.serviceName`; test Pod DNS and client reconnect behavior.
- [ ] Review claim-template names, storage class, access mode, capacity, topology, expansion support, and reclaim/retention behavior.
- [ ] Set and test startup, readiness, and liveness probes based on application documentation.
- [ ] Configure resource requests/limits and storage capacity alerts.
- [ ] Define non-root UID/GID, volume permissions, Secret access, network policy, and image/operator version policy.
- [ ] Verify backups and complete a restore test. Remember that M03 etcd snapshots do not contain PV data.
- [ ] Set termination grace based on documented application shutdown; add only necessary bounded `preStop` hooks.
- [ ] Review anti-affinity, topology spread, PDB, and actual failure domains.

#### Before scale or rollout

- [ ] Confirm current quorum, replication health/lag, leader/member status, and application integrity.
- [ ] Review `podManagementPolicy`, `updateStrategy`, `partition`, `minReadySeconds`, and the intended ordinal sequence.
- [ ] Define canary success metrics, abort criteria, rollback steps, and maintenance window.
- [ ] Confirm scale-in/rebalance/decommission steps with the application documentation.
- [ ] Check PVC retention settings and identify which claims will persist or be deleted.
- [ ] Confirm the target volume is not the only copy and that old-node fencing/storage attachment assumptions are safe.
- [ ] Verify DNS TTL/caching and client reconnect behavior for Pod replacement.

#### During an incident

- [ ] Start with read-only commands and preserve resource YAML, events, logs, and timestamps.
- [ ] Identify the exact namespace, Pod UID, ordinal, PVC, PV, StorageClass, node, and backend asset.
- [ ] Do not force-delete a Pod until the old process is proven stopped/fenced and storage is safe.
- [ ] Do not delete claims, PVs, snapshots, or backend assets as a generic troubleshooting step.
- [ ] Check app-level quorum, replication, membership, and data integrity separately from Pod Ready.
- [ ] Escalate when process state, volume attachment, reclaim behavior, or restore path is uncertain.

#### After recovery

- [ ] Validate the expected ordinal-to-PVC mapping and that the correct data volume is mounted.
- [ ] Run application-native integrity checks, checksums or record-count checks as appropriate.
- [ ] Verify replication catch-up, quorum, leader state, and client-facing smoke tests.
- [ ] Confirm SLOs have recovered and error-budget impact is understood.
- [ ] Record actual recovery point, data-loss window, timeline, and evidence.
- [ ] Update runbooks, backup/restore tests, retention policy, and alerting based on findings.

### 4.10 Hands-on lab set

All labs use synthetic data only. Run `kind` commands only when you have verified the cluster name and target resources. The example commands below are instructional and have **not** been executed here. Any output shown is **Expected output (representative; not executed here)**. Adjust the kind image and Kubernetes version to one supported by your local kind installation, then record the actual version.

Common preflight:

```bash
kind version
kubectl version
kubectl config current-context
kubectl get nodes -o wide
df -h .
docker ps --format 'table {{.Names}}\t{{.Status}}'
```

**Expected output (representative; not executed here):** a kind client version, Kubernetes client/server version information, a current context such as `kind-stateful-lab`, one control-plane container and one or more worker containers, and a disk filesystem with adequate free space. Stop if the current context is not the disposable lab cluster.

For a 4-CPU/8-GB RAM/30-GB-free-disk laptop, keep the database-like workload to small Alpine-based marker containers and tiny PVCs. Reserve a few GB for kind images, node containers, logs, and image layers. Inspect disk before and after each lab; exact footprint depends on cached images and the storage provisioner.

#### Lab 1 — Three-replica StatefulSet: stable DNS and per-Pod PVCs

**Objective and outcomes:** create three Pods with stable ordinal names, a headless Service, one PVC per ordinal, unique marker files, and verify DNS from a temporary client Pod.

**Estimated duration:** 35–50 minutes. **Approximate incremental disk:** usually under 1 GB for small images plus three 64 MiB claims; actual use varies by provisioner and image cache.

**Prerequisites:** disposable kind cluster, `kubectl` context confirmed, `kind` and a container runtime installed, and enough free disk.

**Architecture/resources:** namespace `storage-lab`; Service `marker-db-hs`; StatefulSet `marker-db`; claim template `data`; PVCs `data-marker-db-0` through `data-marker-db-2`.

Create `lab1-statefulset.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: storage-lab
  labels:
    purpose: disposable-learning-lab
---
apiVersion: v1
kind: Service
metadata:
  name: marker-db-hs
  namespace: storage-lab
spec:
  clusterIP: None
  selector:
    app: marker-db
  ports:
    - name: marker
      port: 8080
      targetPort: 8080
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: marker-db
  namespace: storage-lab
spec:
  serviceName: marker-db-hs
  replicas: 3
  selector:
    matchLabels:
      app: marker-db
  podManagementPolicy: OrderedReady
  updateStrategy:
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: marker-db
    spec:
      terminationGracePeriodSeconds: 10
      containers:
        - name: marker
          image: busybox:1.36
          command: ["/bin/sh", "-c"]
          args:
            - |
              ordinal="${HOSTNAME##*-}"
              printf 'pod=%s\nordinal=%s\n' "$HOSTNAME" "$ordinal" > "/data/marker-${ordinal}.txt"
              exec sleep 36000
          ports:
            - name: marker
              containerPort: 8080
          volumeMounts:
            - name: data
              mountPath: /data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 64Mi
```

This is a marker workload, not a database and not an HA application. It writes one file per ordinal and sleeps. The declared port is illustrative and does not mean an application server listens on it. `ReadWriteOnce` is sufficient for this simple test on many local provisioners; verify your StorageClass supports dynamic provisioning and the requested size. If the cluster has no default StorageClass, add `storageClassName` only after inspecting available classes.

Apply and wait with bounded timeouts:

```bash
kubectl apply -f lab1-statefulset.yaml
kubectl rollout status sts/marker-db -n storage-lab --timeout=180s
kubectl get sts,pods,pvc -n storage-lab -o wide
kubectl get svc,endpointslice -n storage-lab
```

Inspect marker files and mount identity:

```bash
for i in 0 1 2; do
  echo "=== marker-db-$i ==="
  kubectl exec -n storage-lab "marker-db-$i" -- sh -c \
    "cat /data/marker-${i}.txt && df -h /data"
done
kubectl get pvc -n storage-lab -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,VOLUME:.spec.volumeName,CLASS:.spec.storageClassName
```

**Expected output (representative; not executed here):** three Ready Pods named `marker-db-0`, `marker-db-1`, and `marker-db-2`; three Bound PVCs named `data-marker-db-0`, `data-marker-db-1`, and `data-marker-db-2`; each marker file identifies the matching Pod and ordinal.

Test DNS from a temporary client Pod:

```bash
kubectl run dns-check -n storage-lab --image=busybox:1.36 \
  --restart=Never --command -- sh -c \
  'for i in 0 1 2; do nslookup marker-db-${i}.marker-db-hs.storage-lab.svc.cluster.local; done; sleep 30'
kubectl wait -n storage-lab --for=jsonpath='{.status.phase}'=Succeeded pod/dns-check --timeout=60s
kubectl logs -n storage-lab dns-check
```

The `cluster.local` suffix is an assumption for many clusters, not a universal constant. If DNS lookups fail, inspect the cluster DNS domain/configuration and use the actual FQDN. Depending on cluster DNS/readiness settings, records may not appear exactly as expected until endpoints are ready. A successful DNS lookup proves discovery, not application replication.

**Success criteria:** distinct claim per ordinal; each marker is unique and on the corresponding claim; DNS resolves the intended Pod names; no claim is shared as a data-replication mechanism.

**Failure modes and troubleshooting:** `Pending` PVCs—inspect `kubectl describe pvc`, StorageClass and provisioner; Pod stuck Pending—inspect scheduling events and PV topology; `ImagePullBackOff`—check image availability and runtime; DNS failure—check Service selector, Pod labels, endpoints, namespace and cluster domain.

**DATA-SAFETY PREFACE — Lab 1 cleanup:** The commands below delete only the disposable `storage-lab` namespace and its namespaced objects, including the StatefulSet, Pods, Service, and PVC objects. Depending on PV reclaim policy and provisioner, backend data cleanup may differ. Before running them, confirm the current context is your lab cluster and the namespace contains only synthetic lab resources.

```bash
kubectl config current-context
kubectl get all,pvc -n storage-lab
kubectl delete namespace storage-lab --wait=true --timeout=120s
```

After cleanup, inspect any remaining PVs; do not delete them automatically.

#### Lab 2 — Partitioned rolling update, scale-down/up, and PVC retention

**Objective and outcomes:** stage a revision update with `partition`, inspect revisions and images, scale down/up, and verify whether the retained ordinal sees its previous marker.

**Estimated duration:** 35–50 minutes. **Approximate incremental disk:** less than 1 GB beyond Lab 1. Use the same namespace and workload if Lab 1 is still present; otherwise recreate it first.

**DATA-SAFETY PREFACE:** This lab changes a disposable StatefulSet’s Pod template and replica count. It writes only synthetic markers, but scale-down removes a Pod and may delete its PVC if the configured retention policy says `Delete`. Confirm the namespace and retention policy before scaling. The example below does not explicitly set a deletion retention policy; inspect the actual policy supported by your cluster.

Inspect current policy and versions:

```bash
kubectl get sts marker-db -n storage-lab -o yaml
kubectl explain statefulset.spec.persistentVolumeClaimRetentionPolicy
kubectl get pvc -n storage-lab
kubectl get sts marker-db -n storage-lab -o jsonpath='{.status.currentRevision}{" / "}{.status.updateRevision}{"\n"}'
```

**[VERIFY]** The `persistentVolumeClaimRetentionPolicy` field, feature maturity, and defaults vary by Kubernetes version. If `kubectl explain` reports that the field is unknown, do not apply a manifest containing it. Consult the official StatefulSet documentation for the exact server version and inspect the live API schema.

Set a partition of 2 and change the marker workload image to a second pinned tag available in your environment. For a repeatable lab, use the same image with a changed command marker instead of relying on a new image pull:

```bash
kubectl patch sts marker-db -n storage-lab --type=merge -p \
'{"spec":{"updateStrategy":{"type":"RollingUpdate","rollingUpdate":{"partition":2}}}}'
kubectl patch sts marker-db -n storage-lab --type=json -p \
'[{"op":"replace","path":"/spec/template/spec/containers/0/args/0","value":"ordinal=\"${HOSTNAME##*-}\"; printf \"revision=lab-v2\\npod=%s\\nordinal=%s\\n\" \"$HOSTNAME\" \"$ordinal\" > \"/data/marker-${ordinal}.txt\"; exec sleep 36000"}]'
kubectl get sts marker-db -n storage-lab -o jsonpath='{.status.currentRevision}{" / "}{.status.updateRevision}{"\n"}'
kubectl get pods -n storage-lab -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,READY:.status.containerStatuses[0].ready
```

With partition 2, ordinal 2 is the expected first eligible update target. Wait for it and inspect its marker:

```bash
kubectl rollout status sts/marker-db -n storage-lab --timeout=180s
kubectl exec -n storage-lab marker-db-2 -- cat /data/marker-2.txt
kubectl exec -n storage-lab marker-db-0 -- cat /data/marker-0.txt
kubectl exec -n storage-lab marker-db-1 -- cat /data/marker-1.txt
```

**Expected output (representative; not executed here):** ordinal 2 contains `revision=lab-v2`; ordinals 0 and 1 retain their prior marker until the partition is lowered. Exact status fields and controller progression must be observed in the live cluster.

To advance the staged rollout, lower the partition one step at a time and inspect after each change:

```bash
kubectl patch sts marker-db -n storage-lab --type=merge -p \
'{"spec":{"updateStrategy":{"rollingUpdate":{"partition":1}}}}'
kubectl rollout status sts/marker-db -n storage-lab --timeout=180s
kubectl get pods -n storage-lab -o wide
kubectl patch sts marker-db -n storage-lab --type=merge -p \
'{"spec":{"updateStrategy":{"rollingUpdate":{"partition":0}}}}'
kubectl rollout status sts/marker-db -n storage-lab --timeout=180s
```

For each step, verify the actual image/template revision and application health before continuing. In a real database, never use marker-file success as a substitute for quorum or replication checks.

Now test PVC persistence on scale-down/up. Record the marker and PVC identity first:

```bash
kubectl exec -n storage-lab marker-db-2 -- cat /data/marker-2.txt
kubectl get pvc data-marker-db-2 -n storage-lab -o yaml > pvc-ordinal-2-before.yaml
kubectl scale sts/marker-db -n storage-lab --replicas=2
kubectl wait -n storage-lab --for=delete pod/marker-db-2 --timeout=120s
kubectl get pvc data-marker-db-2 -n storage-lab
```

If the claim remains, scale back to three and verify the same ordinal’s claim and marker:

```bash
kubectl scale sts/marker-db -n storage-lab --replicas=3
kubectl rollout status sts/marker-db -n storage-lab --timeout=180s
kubectl exec -n storage-lab marker-db-2 -- cat /data/marker-2.txt
kubectl get pvc data-marker-db-2 -n storage-lab -o wide
```

If the PVC was deleted by a configured retention policy, stop: do not assume its marker can be recovered. Record the actual result and investigate policy, events, PV reclaim policy, and provisioner behavior. Do not automatically delete retained PVCs during cleanup.

**Retention variants:** On a version that supports the field, a test-only manifest can explicitly set `whenScaled: Retain` and `whenDeleted: Retain`, or test `Delete` in a separate disposable cluster. **[VERIFY]** the exact schema and semantics before applying. A deletion test must begin with a separate **DATA-SAFETY PREFACE** and must never target valuable data.

**Success criteria:** partitioned rollout behavior is evidenced by Pod revisions/markers; scale-down removes ordinal 2’s Pod; the PVC’s actual fate matches the configured/live retention policy; scale-up reuses the same claim and marker only if that claim was retained.

**Troubleshooting:** a rollout that never completes—inspect events, readiness, current/update revision, and Pod template; PVC absent after scale-down—inspect retention policy and events; ordinal 2 returns with an empty marker—check whether a new claim was provisioned and whether the original data survived.

#### Lab 3 — Simulated worker-node loss on kind and safe recovery

**Objective and outcomes:** observe the effect of stopping a kind worker container, preserve evidence, and practice a safe recovery decision tree without assuming a fixed Pod state or forcing a replacement while process state is uncertain.

**Estimated duration:** 45–75 minutes. **Approximate incremental disk:** minimal for marker data; kind node image and logs can consume several GB. Inspect disk first:

```bash
df -h .
kind get clusters
docker ps --format 'table {{.Names}}\t{{.Status}}'
kubectl config current-context
kubectl get nodes -o wide
kubectl get sts,pods,pvc -n storage-lab -o wide
```

**DATA-SAFETY PREFACE — node failure injection:** This experiment stops a container that represents a kind worker. It may make Pods unavailable and leaves the cluster in a degraded state; deleting the cluster later destroys all its local lab data. Use a dedicated disposable cluster named `stateful-lab`, with synthetic data only. Confirm the cluster and worker names before stopping anything. Do not run this against a shared or production cluster.

Create a dedicated cluster configuration `kind-stateful-lab.yaml`:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: stateful-lab
nodes:
  - role: control-plane
  - role: worker
```

Create it only if that cluster name does not already exist:

```bash
kind get clusters
kind create cluster --config kind-stateful-lab.yaml --wait 120s
kubectl config use-context kind-stateful-lab
kubectl get nodes -o wide
```

Apply Lab 1’s manifest to this cluster, wait for all three Pods and PVCs, and write/check the synthetic markers. Record node and container mapping:

```bash
kubectl get nodes -o wide
docker ps --format 'table {{.Names}}\t{{.Status}}'
kubectl get pods -n storage-lab -o wide
kubectl get pvc -n storage-lab -o wide
kubectl get pv -o wide
```

Identify the worker container name from the actual `docker ps` output and kind node list. Do not guess the name. Save the output to your lab notes. Stop exactly that worker container:

```bash
docker stop <verified-kind-worker-container-name>
```

Observe rather than assume:

```bash
kubectl get nodes -o wide
kubectl get pods -n storage-lab -o wide
kubectl describe pod -n storage-lab marker-db-0
kubectl get events -n storage-lab --sort-by=.lastTimestamp
kubectl get pvc -n storage-lab -o wide
kubectl get pv -o wide
```

Repeat `kubectl get` at bounded intervals for up to a few minutes. The actual state may be `Unknown`, `Terminating`, `NotReady`, or another state depending on Kubernetes version and timing. Do not promise a fixed transition. A StatefulSet may avoid safely creating a replacement ordinal while the previous Pod’s process state is uncertain. kind simulates a worker container stopping; it does not reproduce every hardware, network partition, storage fencing, or real-world node-shutdown scenario.

**Recovery decision tree:**

1. **Verify identity:** capture Pod UID, ordinal, node, PVC, PV, worker container name, and events.
2. **Determine process state:** is the worker container definitely stopped, or could the node merely be partitioned from the control plane while the process continues?
3. **Verify storage safety:** inspect PV topology, volume attachment objects if relevant, and the local storage implementation. Establish whether the data remains and whether a replacement could access it safely.
4. **If uncertain:** do not force-delete the Pod or start a competing writer. Escalate and preserve the cluster for observation.
5. **If stopped/fenced and this is the disposable kind cluster:** follow the documented kind/Kubernetes recovery path for the exact version. You may restart the worker container if the local runtime permits and observe node recovery; do not assume a particular restart procedure repairs every storage state.
6. **After the node is Ready:** inspect Pods, claims, and PVs; confirm the correct ordinal is mounted and marker content remains intact.

For a controlled restart of the same stopped worker container, first verify the exact container name again:

```bash
docker ps -a --format 'table {{.Names}}\t{{.Status}}'
docker start <verified-kind-worker-container-name>
kubectl get nodes -o wide
kubectl get pods -n storage-lab -o wide
```

**Do not use force deletion as the lab’s routine recovery step.** If a separate demonstration is approved by an instructor, it must have an explicit DATA-SAFETY PREFACE and evidence that the old node/process is stopped or fenced, with storage attachment safety understood. The danger if that assumption is wrong is duplicate live processes accessing the same logical identity/data, corruption, or split-brain.

Verify the marker before and after recovery:

```bash
kubectl rollout status sts/marker-db -n storage-lab --timeout=180s
kubectl get sts,pods,pvc -n storage-lab -o wide
for i in 0 1 2; do
  kubectl exec -n storage-lab "marker-db-$i" -- cat "/data/marker-${i}.txt"
done
```

If a Pod cannot schedule because its PV is local to the failed node, do not remove affinity or create a new empty claim and call it recovery. Record the evidence and explain that the actual data recovery path may require restoring from a backup or using application-native replication. A single local copy can be lost with its node/container storage.

**Success criteria:** the learner records the actual observed state, avoids unsupported assumptions, does not force-delete under uncertain process state, follows a documented recovery path, and verifies marker integrity after recovery.

**Cleanup — DATA-SAFETY PREFACE:** Deleting the `stateful-lab` kind cluster destroys all Pods, PVCs, PV objects, and local lab data in that cluster. Verify the cluster name and that it contains only this exercise before deleting it.

```bash
kubectl config current-context
kind get clusters
kubectl --context kind-stateful-lab get all,pvc -A
kind delete cluster --name stateful-lab
kind get clusters
df -h .
```

#### Required mini-design exercise — Choose the right stateful operating model

Choose a model for a service with a business-defined RPO/RTO, a limited on-call team, and a database that requires patching and tested restores. Document the following:

1. Application: database/broker type, replication model, consistency requirements, and supported Kubernetes/operator options.
2. Recovery: measured restore time, acceptable data-loss window, backup location, restore-test cadence, and failure-domain assumptions.
3. Ownership: who owns the operator, database upgrades, incidents, security patches, and recovery approval.
4. Cost: infrastructure and storage charges plus engineering time, on-call load, and opportunity cost.
5. Exit/rollback: how to export data, validate it, and move to another operating model.

Use the table in Section 4.6.7. Do not select Kubernetes solely because it is already available. An operator is useful only if it is maintained, supports the required application/version, and the team can operate it. A managed service may reduce infrastructure work but still requires restore testing, access controls, and application-level validation. Running the database outside Kubernetes may be the lowest-risk option when operational expertise or recovery guarantees are insufficient.

### 4.11 Self-check questions

Answer each question in your own words before consulting the rubric.

1. What does a StatefulSet guarantee, and what must the application or operator provide?
2. Given template `data`, StatefulSet `ledger`, and ordinal `2`, what is the expected PVC name? What evidence confirms the actual mapping?
3. Why can a Pod’s DNS name remain stable while its IP changes? What must a client do?
4. How do `OrderedReady` and `Parallel` differ? Why is neither a consistency protocol?
5. With three replicas and a rolling-update partition of `2`, which ordinal is eligible for the staged update first? What evidence should be checked before lowering the partition?
6. Why is Pod readiness not sufficient evidence that a database member is safe or caught up?
7. What are the risks of setting `whenScaled: Delete`? What must be verified before relying on a retention policy?
8. Why does changing `volumeClaimTemplates` not migrate or resize existing PVCs?
9. Why is an ordinal-based init script not a robust leader-election or replication design?
10. What is the difference between RWO and RWOP, and why must CSI support be checked?
11. A StatefulSet Pod is stuck `Terminating` on an unreachable node. What evidence must exist before considering force deletion?
12. A PVC has been deleted accidentally. What should be preserved, and what facts determine whether recovery is possible?
13. Why can snapshots of separate data and WAL volumes taken at different times be inconsistent?
14. What do etcd snapshots contain, and what do they not contain?
15. Which operating model would you choose for a small team with strict RPO/RTO requirements, and what evidence supports that choice?

**Answer rubric:**

- **Strong answer:** distinguishes controller behavior, storage behavior, and application behavior; names the exact resource fields/commands to inspect; identifies destructive risks and required preconditions; includes application-level integrity and replication checks.
- **Partial answer:** recalls field names but treats Pod Ready as application health, assumes scale-down deletes or retains claims without inspection, or proposes recovery without confirming process/storage state.
- **Unsafe answer:** recommends force deletion while a node may still be running, deletes PVC/PV assets before preserving evidence, assumes StatefulSet provides replication/backup, or returns traffic without data-integrity validation.

### 4.12 Evidence artifacts

Keep a compact evidence bundle for every lab and any real operational exercise. Do not include credentials, secret values, or customer data.

- `environment.txt`: `kind version`, `kubectl version`, current context, cluster name, and node/container mapping.
- `statefulset-before.yaml` and `statefulset-after.yaml`: relevant StatefulSet specs and status, with secrets excluded.
- `pods-and-events.txt`: Pod list, `describe` output, sorted namespace events, and timestamps.
- `claims-and-volumes.txt`: PVC/PV status, claim-to-volume mapping, StorageClass, reclaim policy, topology, and attachment evidence where applicable.
- `dns-check.txt`: queried FQDNs and actual DNS results, plus the cluster DNS-domain assumption.
- `marker-integrity.txt`: ordinal, Pod name, PVC name, marker content, and whether it matched before/after recovery.
- `rollout-evidence.txt`: current/update revision, partition, images, Pod readiness, and application-specific health evidence.
- `incident-timeline.md`: symptom, impact, read-only evidence, decisions, approvals, recovery steps, data-loss window, and post-recovery checks.
- `verification-register.md`: every `[VERIFY]` item, the installed version/driver/image checked, the official documentation/resource consulted, the observed result, and reviewer/date.

For a production system, add database-native replication/quorum status, backup inventory and restore-test results, SLO/error-budget impact, and relevant change approvals. Store evidence in the approved secure location and apply retention/access controls.

### 4.13 Common interview and design-review questions

1. **Why use a StatefulSet instead of a Deployment for a database?**  
   A StatefulSet provides stable Pod identity, ordered/controlled lifecycle behavior, and per-ordinal claim relationships. It does not itself supply database replication or HA; the application and storage architecture determine whether the design is safe.

2. **How do headless Services and StatefulSet DNS work together?**  
   The headless Service supplies endpoint discovery and the governing Service name; each Pod can have a predictable DNS identity derived from Pod name, Service, namespace, and cluster domain. DNS does not guarantee a fixed IP or automatic client reconnect.

3. **How would you roll out a database change safely?**  
   Verify application quorum, replication lag, backup/restore, and compatibility first; stage with the supported update strategy/partition; change members in the application’s safe order; validate app-level health after each member; stop on predefined abort criteria and use a compatibility-aware rollback plan.

4. **What would you do if a StatefulSet Pod is stuck on a lost node?**  
   Preserve read-only evidence, determine whether the old process is stopped or fenced, inspect storage attachment/topology and application membership, and follow a version/backend-specific recovery plan. Do not force-delete while the old node may still write.

5. **When would you choose an operator, a managed database, or a database outside Kubernetes?**  
   Compare team expertise, measured RPO/RTO, application support, backup/restore and failover behavior, upgrade burden, security, portability, cost, and on-call ownership. Choose the simplest model the team can operate and recover reliably.

### 4.14 Sources and verification notes

Use official documentation as the authority for version-sensitive behavior. This lesson was authored from the supplied prompt and technical knowledge; the commands and labs were **not executed here**, and the links below were not live-verified in this response. Treat unresolved details as `[VERIFY]` before using them in a real cluster.

#### Official Kubernetes sources

- StatefulSets: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
  - Verify stable identity, governing Service, ordinal behavior, `podManagementPolicy`, update strategies, partition behavior, and PVC retention policy for the installed version.
- StatefulSet basics/tutorial: https://kubernetes.io/docs/tutorials/stateful-application/basic-stateful-set/
  - Verify examples for headless Services, stable Pod identity, and claim-template naming.
- Persistent Volumes: https://kubernetes.io/docs/concepts/storage/persistent-volumes/
  - Verify PV/PVC lifecycle, reclaim policies, access modes, local volume affinity, and expansion-related behavior.
- Storage Classes: https://kubernetes.io/docs/concepts/storage/storage-classes/
  - Verify the default StorageClass, provisioner, parameters, and volume binding mode in the target cluster.
- Probes: https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/
  - Verify startup, readiness, and liveness semantics and the configured probe fields.
- Pod lifecycle and termination: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
  - Verify termination grace, container shutdown, and version-specific behavior.
- Pod disruptions and PDBs: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/
  - Verify which disruptions are voluntary/involuntary and the supported eviction behavior.
- Topology spread constraints: https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/
  - Verify supported fields and the topology domains actually available in the cluster.
- Pod Security Standards: https://kubernetes.io/docs/concepts/security/pod-security-standards/
  - Verify the selected security profile and enforcement configuration.
- RBAC: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
  - Verify least-privilege roles for StatefulSets, PVCs, Secrets, and exec access.
- DNS for Services and Pods: https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/
  - Verify the actual cluster domain, Pod DNS behavior, and DNS configuration.
- Node shutdown behavior: https://kubernetes.io/docs/concepts/cluster-administration/node-shutdown/
  - **[VERIFY] [VERSION-SENSITIVE]** Check the exact Kubernetes release, graceful node-shutdown configuration, and node-management behavior. Do not extrapolate to every node-loss or network-partition scenario.
- Force deletion: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination
  - **[VERIFY]** Confirm current warning and behavior before using any force-delete procedure; API-object removal is not proof that the process has stopped.

#### Official tool and application sources

- kind documentation: https://kind.sigs.k8s.io/
  - Verify the installed kind version, cluster configuration, node container names, and lifecycle commands.
- PostgreSQL documentation: https://www.postgresql.org/docs/
  - **[VERIFY]** Check the exact PostgreSQL version and image for `PGDATA`, `initdb` requirements, WAL/recovery, signal handling, and readiness/health-check semantics.
- Kubernetes etcd administration documentation: https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/
  - Verify the scope and restore process for etcd snapshots. An etcd snapshot does **not** contain PV file contents or external storage-backend data.

#### Required live verification register

| Item | Why it matters | Exact check before production use |
|---|---|---|
| Kubernetes version and API schema | Fields and defaults vary by release | `kubectl version`; `kubectl explain statefulset.spec`; inspect live StatefulSet YAML and matching official docs |
| PVC retention policy | May delete claims on scale-down or StatefulSet deletion | `kubectl explain statefulset.spec.persistentVolumeClaimRetentionPolicy`; inspect `spec.persistentVolumeClaimRetentionPolicy`; verify version documentation |
| Start ordinal | Can change expected Pod/PVC names | Check whether `.spec.ordinals.start` is supported in the installed API and verify controller behavior |
| CSI/RWOP | Single-Pod access semantics depend on Kubernetes/driver support | Inspect CSI driver and sidecar versions, StorageClass, access mode, and official driver support matrix |
| Storage topology and local PV | A Pod may not move with its data after node loss | Inspect PVC/PV, PV node affinity, StorageClass, events, and backend attachment/locality documentation |
| Node shutdown / force deletion | Incorrect assumptions can cause duplicate writers | Verify official docs for exact version; inspect node/process/fencing and backend attachment state before action |
| Database probes and shutdown | Bad probes can restart a recovering database | Verify selected image/application docs, test recovery, and measure shutdown duration |
| DNS domain and caching | Hard-coded FQDN or TTL assumptions may be wrong | Inspect cluster DNS config, resolve actual names, and test client reconnect behavior |
| Backup/restore and consistency | Snapshots may be crash-consistent or uncoordinated across volumes | Verify backup product/application procedure and complete a restore/integrity test |
| Manifest validity | YAML can be syntactically valid but invalid for a target API | In the disposable target cluster, use `kubectl apply --dry-run=server -f <manifest>` and review API validation output |

#### Scope and cross-module boundaries

- **M05 Unit 1:** `01-volumes-persistentvolumes-and-persistentvolumeclaims.md` — PV/PVC and volume fundamentals.
- **M05 Unit 2:** `02-storageclasses-dynamic-provisioning-and-csi-drivers.md` — StorageClasses and CSI.
- **M05 Unit 3:** `03-volume-snapshots-cloning-and-expansion.md` — snapshots, cloning, expansion, and consistency limitations.
- **M05 Unit 5:** `05-running-databases-and-brokers-with-operators.md` — operators and application-specific lifecycle automation.
- **M05 Unit 7:** `07-data-locality-zonal-failure-and-volume-affinity.md` — topology, locality, and volume affinity.
- **M05 Unit 8:** `08-storage-troubleshooting-and-orphaned-volumes.md` — broader storage troubleshooting and orphaned volumes.
- **M01:** image engineering, non-root containers, UID/GID, `fsGroup`, and volume permissions.
- **M03:** Unit 3 probes; Unit 5 PDBs; Unit 7 anti-affinity/topology spread; RBAC/PSS, node drain, and etcd backup context. **etcd snapshots do not contain PV data.**
- **M04:** headless Services, DNS, and NetworkPolicy for database traffic.
- **M06:** Helm/Kustomize packaging is a forward reference; this unit applies manifests directly.
- **M09:** credentials and encryption-key management (forward reference).
- **M10:** SLOs and incident management (forward reference).
- **M11:** storage/database observability (forward reference).
- **M12:** security (forward reference).
- **M13:** organization-wide backup/DR, immutability, offsite and cross-region recovery (forward reference).
- **M14:** multi-cluster operations (forward reference).
- **M15:** storage cost (forward reference).

#### Self-audit

- [x] Exact Unit 4 title and target filename.
- [x] Headings 4.0 through 4.14 included once and in order.
- [x] L1–L4 cover stable identity, PVCs, retention, rollouts, coordination, failure handling, and operating-model decisions.
- [x] Three labs include manifests/commands, bounded waits, evidence, troubleshooting, and cleanup safety notes.
- [x] Force deletion is explicitly high risk and not presented as a routine fix.
- [x] Six incident runbook categories and the operating-model decision matrix are included.
- [x] Security, SRE, production checklist, evidence artifacts, self-check rubric, and exactly five interview/design-review questions are included.
- [x] Cross-module links include the explicit warning that etcd snapshots do not contain PV data.
- [ ] Live API/schema, version defaults, links, manifest validation, and lab execution remain **[VERIFY]**; none are claimed as completed here.
