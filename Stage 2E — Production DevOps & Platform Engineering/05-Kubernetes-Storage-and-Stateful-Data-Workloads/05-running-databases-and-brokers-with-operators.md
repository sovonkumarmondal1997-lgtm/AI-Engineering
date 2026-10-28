## Unit 5 — Running databases and brokers with operators

**Target file:** 05-running-databases-and-brokers-with-operators.md  |  **Estimated time:** 10–14 hours  |  **Prerequisites:** M05 Units 1–4, M03 Kubernetes operations, M04 Services/DNS/NetworkPolicy

**Core tools:** kubectl, kind, CloudNativePG, PostgreSQL, local S3-compatible object store where feasible  |  **Awareness:** Strimzi/Kafka, Redis, RabbitMQ, NATS, managed databases  |  **Last reviewed:** 2026-10-28  |  **Kubernetes/operator baseline assumed:** Recent Kubernetes and CloudNativePG releases compatible with the selected kind release; exact versions, CRD APIs, plugins, and compatibility must be **[VERIFY]** against current official documentation before installation.

### 5.0 Why this matters in production

A database operator reports that a primary failover completed, but the application still has open connections to the former primary and returns errors. In another incident, write-ahead log (WAL) archiving quietly stops while PostgreSQL continues accepting writes; the database volume fills, writes fail, and recovery is delayed. In a third incident, a scheduled backup job reports success, but a restore later fails because required WAL files are missing or the recovery procedure was never tested.

These incidents illustrate the difference between **automation** and **recoverability**. An operator can reconcile custom resources, manage database Pods, and automate supported lifecycle operations. It cannot guarantee that clients reconnect safely, that backups contain all required recovery data, that object storage remains available, or that a restore meets the business recovery point objective (RPO) and recovery time objective (RTO).

This unit uses CloudNativePG (CNPG) and PostgreSQL for the primary learning path. A local kind cluster is a mechanics lab, not production infrastructure: it does not provide independent physical availability zones, durable cloud storage, or realistic failure domains. All data must be synthetic and all destructive operations must target a disposable cluster and namespace.

The guiding questions are:

1. Should this database or broker run on Kubernetes at all?
2. Which operator is suitable, supported, and compatible with the chosen versions?
3. Who owns the on-call responsibility when automation cannot complete recovery?

An operator does not remove the need for backup validation, restore testing, security review, capacity planning, incident response, or an accountable owner.

### 5.1 Learning objectives

- **[L1]** Explain how Custom Resource Definitions (CRDs), custom resources, and operator controllers work together, and distinguish Kubernetes reconciliation from database-native replication.
- **[L1/L2]** Explain what an operator can automate, what it cannot guarantee, and how its lifecycle relates to StatefulSet mechanics in `04-statefulset-storage-patterns-and-stable-identity.md`.
- **[L2]** Install a compatible CloudNativePG release in a disposable kind cluster, create a small PostgreSQL Cluster custom resource, and inspect its Pods, PVCs, Services, Secrets metadata, events, and operator logs.
- **[L2]** Insert deterministic synthetic data, perform a documented planned switchover and a separate Pod-deletion failover exercise, and validate data after each event.
- **[L3]** Describe base backups, continuous WAL archiving, retention, and point-in-time recovery (PITR), including how to restore to a specific timestamp into a new cluster.
- **[L3]** Evaluate PostgreSQL upgrade, pooling, TLS, monitoring, memory, replication, and network-policy choices using version-specific documentation.
- **[L3]** Explain the major operational concepts in Strimzi/Kafka, including partitions, in-sync replicas, KRaft quorum, storage, and broker rollout risks.
- **[L4]** Evaluate operator governance, CRD upgrades, controller permissions, failure modes, incident evidence, and managed-database alternatives.
- **[L4]** Build runbooks and game-day checks that validate client behavior, backup freshness, recovery correctness, and post-recovery data integrity.

### 5.2 Concept map and vocabulary

```text
Platform / operator
    |
    | installs CRDs and controller
    v
User applies a database custom resource (e.g., Cluster)
    |
    v
Operator controller continuously reconciles desired vs observed state
    |
    +--> StatefulSet / Pods / Services / PVCs / Secrets / PDB (version-dependent)
    |           |
    |           v
    |       PostgreSQL processes and persistent data
    |
    +--> database-aware lifecycle actions (only those supported by this operator)
                |
                +--> primary/replica roles and failover
                +--> backup orchestration and WAL archive configuration
                +--> restore/bootstrap workflow

PostgreSQL-native layer:
  transactions -> WAL -> replication/replay -> base backup + archived WAL -> PITR

Storage/object-store layer:
  PVC/PV -> CSI/provisioner/backend
  backup/WAL -> object store (credentials, retention, capacity, availability)

Client layer:
  DNS/service endpoint -> connection pool -> retry/transaction semantics
```

The **CRD** defines a new API type that the Kubernetes API server can validate and store. A **custom resource (CR)** is an object of that type, such as a database cluster declaration. An **operator controller** watches the custom resource and related resources, then reconciles actual state toward desired state. Reconciliation is a loop, not a guarantee that every desired state is attainable.

| Term | Definition | Common misconception |
|---|---|---|
| CRD | Extends the Kubernetes API with a new resource type | Installing a CRD automatically installs a working controller |
| Custom resource | An instance of a CRD, describing desired application state | It is just a static YAML file with no lifecycle behavior |
| Operator | Controller plus application-specific operational knowledge and related resources | It guarantees every failover and restore succeeds |
| Reconciliation | Repeatedly compares desired and observed state and takes corrective action | It is the same thing as PostgreSQL replication |
| Primary / replica | PostgreSQL roles in a replication topology | Kubernetes ordinal zero is always the primary |
| WAL | PostgreSQL write-ahead log used for durability, recovery, and replication | A base backup alone always supports arbitrary PITR |
| Base backup | A physical baseline of a PostgreSQL cluster’s data | A successful job proves all WAL needed for recovery exists |
| WAL archiving | Shipping WAL segments to an archive destination | A recent base backup means archiving cannot be broken |
| PITR | Recovery to a specific point in time using a base backup and required WAL | It overwrites or repairs the source automatically |
| Switchover | Planned role transition, typically when the current primary is healthy and coordinated | It is equivalent to an unplanned node failure |
| Failover | Promotion/recovery after a primary is unavailable or considered failed | Every client instantly reconnects |
| Fencing | Preventing a stale or isolated former writer from continuing to write | Removing a Pod API object proves the old process is dead |
| RPO / RTO | Maximum acceptable data loss / recovery duration | Kubernetes availability alone establishes either objective |
| KRaft | Kafka’s Raft-based metadata quorum mode | A one-broker demo proves quorum or HA |
| ISR | Kafka in-sync replica set for a partition | It is a Kubernetes Pod readiness condition |

**Where responsibilities end:** Kubernetes schedules Pods and manages API objects. The operator implements supported database-aware workflows. PostgreSQL implements transaction semantics, WAL, replication, recovery, and database roles. The storage system determines actual persistence and attachment behavior. Clients must manage connections and retry semantics. A safe design validates all of these layers.

The maturity sequence used in this lesson is **install → lifecycle → backup/recovery → monitoring → autoscale → tuning**. It is a learning/evaluation progression, not a universal maturity standard. Do not progress to tuning or autoscaling before the service can be recovered reliably.

### 5.3 Level 1 — Beginner

#### 5.3.1 Why a StatefulSet alone is insufficient

A StatefulSet provides stable Pod identity and storage-claim relationships. It does not know whether PostgreSQL has replayed WAL, whether a replica is caught up, whether a primary can safely be promoted, or whether a backup is restorable. A database operator adds application-specific reconciliation: depending on its implementation and configuration, it may manage initialization, primary/replica roles, failover, controlled updates, backup integration, TLS, users, and metrics.

The exact capability set matters. Two operators for the same database can differ in supported versions, backup methods, recovery workflows, extension support, generated Services, and upgrade semantics. Evaluate the actual operator rather than treating “operator-managed” as a universal feature guarantee.

#### 5.3.2 Operator lifecycle and maturity

| Stage | What to prove | Evidence before progressing |
|---|---|---|
| Install | Controller and CRDs are compatible and healthy | Controller Deployment ready; CRDs established; supported API confirmed |
| Lifecycle | Create, update, restart, switchover, and recovery behavior are understood | Resource status, events, roles, application checks, bounded operation times |
| Backup/recovery | Backups and required WAL are available and a restore works | Restore into a separate cluster, timestamp evidence, integrity checks |
| Monitoring | Failure signals are observable and actionable | Role, replication lag, archive freshness, disk, backup age, restart/failover alerts |
| Autoscale | Capacity and application-level scaling are safe | Load tests, storage headroom, replica/partition reconfiguration procedure |
| Tuning | Settings improve measured outcomes without destabilizing the service | Baseline, controlled change, comparison, rollback plan |

The order is intentional. A database that cannot be restored is not production-ready merely because its Pods are healthy.

#### 5.3.3 What operators can and cannot do

An operator may automate supported tasks such as bootstrap, replica reconciliation, planned switchover, failover, backup scheduling, or restore orchestration. It may also generate Services, PDBs, Secrets, monitoring configuration, or StatefulSets. **[VERIFY]** every item against the chosen release’s documentation and live resources.

The team still owns:
- schema and query design;
- application retry/idempotency behavior;
- backup policy and independent restore testing;
- capacity, cost, and storage growth;
- security, credential lifecycle, network policy, and image/CRD supply chain;
- version compatibility and change windows;
- monitoring, incident escalation, and recovery decisions;
- data export and an exit strategy.

#### 5.3.4 Choosing where to run a database

Running a database on Kubernetes can make sense when the team already operates Kubernetes well, the operator is mature for the target database/version, storage and failure domains are suitable, and the team can execute recovery drills. It may be a poor fit when the database has specialized hardware/licensing needs, the team lacks database on-call expertise, the required RPO/RTO cannot be met by the available storage and topology, or a managed service materially reduces operational risk.

A managed service does not eliminate customer responsibilities. The application team still owns access patterns, schema, credentials, data classification, client behavior, and verification that provider recovery features meet requirements.

### 5.4 Level 2 — Intermediate

#### 5.4.1 Installation and version compatibility

Use the current official CloudNativePG installation instructions rather than copying an old manifest. CloudNativePG API versions, supported Kubernetes versions, installation methods, generated resources, backup architecture, and field names evolve. This lesson does not claim a live compatibility check was performed.

Official starting points:
- CloudNativePG documentation: https://cloudnative-pg.io/documentation/
- CloudNativePG project: https://github.com/cloudnative-pg/cloudnative-pg
- kind: https://kind.sigs.k8s.io/
- Kubernetes custom resources: https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/

Before installation, record:
```bash
kind version
kubectl version
kubectl config current-context
kubectl get nodes -o wide
kubectl get storageclass
df -h .
free -h
```

**[VERIFY]** Choose a CloudNativePG release explicitly documented as compatible with the Kubernetes server version and kind node image. Follow the current official installation page for the exact manifest or Helm command, CRD installation order, namespace behavior, and upgrade path. Do not invent a tag or apply an unreviewed remote manifest. Pin the selected version in your lab notes.

A three-instance PostgreSQL cluster can be heavy for an 8 GB laptop. A practical planning budget is approximately 2–4 GB of additional memory for a minimal three-instance database plus the operator and Kubernetes system components, but actual usage depends on images, PostgreSQL settings, and kind. **[VERIFY]** current documented minimums and observe live memory. Keep the workload idle and use small PVCs (for example, 1 GiB per instance only if the provisioner supports it and disk budget allows). A local object store later adds additional memory and disk overhead.

If the three-instance cluster causes memory pressure, use the reduced one-instance variant for resource and API inspection only. It does **not** demonstrate replication, switchover, failover, quorum, or high availability.

#### 5.4.2 Install and inspect the operator

The exact install command depends on the current supported release and chosen installation method. Follow the official documentation and record the command and version used. After installation, verify the controller and CRDs before applying a database custom resource:

```bash
kubectl get crd | grep -i postgresql
kubectl get deployments,pods -A | grep -i cloudnative
kubectl get events -A --sort-by=.lastTimestamp
kubectl api-resources | grep -i postgresql
```

**Expected output (representative; not executed here):** one or more CRDs related to CloudNativePG, a ready operator controller, and a PostgreSQL Cluster API resource. Names and namespaces depend on the installed release and installation method.

If CRDs are missing, the controller is not ready, or the API kind is absent, stop before applying the database resource. Inspect controller logs and installation events. Do not repeatedly apply a CR that the API server cannot recognize.

#### 5.4.3 Create a three-instance PostgreSQL Cluster

The following custom resource is a **shape example**, not a verified current manifest. Before applying it, compare every field and API version with the current CloudNativePG API reference for your installed release. In particular, verify `apiVersion`, `spec.instances`, `spec.storage`, resource fields, image configuration, and any required bootstrap options. If any field differs, use the documented version-specific example.

Save as `cnpg-cluster.yaml`:

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: pg-lab
  namespace: db-lab
spec:
  instances: 3
  storage:
    size: 1Gi
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "768Mi"
      cpu: "750m"
```

**[VERIFY]** The `postgresql.cnpg.io/v1` API and these field names must exist in the selected release. Resource values are intentionally small lab estimates, not production sizing guidance. If the current API requires or recommends additional fields, use the official example rather than silently adapting an older schema. Small memory limits can trigger out-of-memory (OOM) kills; monitor actual usage and raise the limits or use a reduced lab if necessary.

Create a disposable namespace and apply only after the CRD is established:

```bash
kubectl create namespace db-lab
kubectl apply --dry-run=server -f cnpg-cluster.yaml
kubectl apply -f cnpg-cluster.yaml
kubectl get cluster -n db-lab -w
```

Use a bounded watch in practice (for example, stop after a defined time and inspect status rather than waiting indefinitely). The command above is illustrative; do not leave an unbounded watch running in an unattended session.

Inspect resources:

```bash
kubectl get cluster -n db-lab -o wide
kubectl describe cluster pg-lab -n db-lab
kubectl get pods,pvc,svc -n db-lab -o wide
kubectl get events -n db-lab --sort-by=.lastTimestamp
kubectl get pdb -n db-lab
kubectl get secrets -n db-lab
kubectl logs -n <operator-namespace> deploy/<operator-deployment> --tail=200
```

Replace the operator namespace/deployment placeholders using actual resources discovered after installation. Do not assume all versions generate a PDB or the same Services. In versions where generated Service names include `-rw`, `-ro`, and `-r`, inspect their selectors and endpoints before using them; verify the meaning of each suffix in the installed version’s documentation. Commonly these distinguish read-write, read-only, and replication-oriented access, but do not rely on the name alone.

Inspect Secret **metadata only**:

```bash
kubectl get secrets -n db-lab
kubectl describe secret <verified-secret-name> -n db-lab
```

Do not run `kubectl get secret -o yaml`, decode Secret values, or paste credentials into notes. Secret names and ownership vary by release and configuration.

#### 5.4.4 Connect safely and verify synthetic data

Use the operator’s documented connection instructions. Avoid placing a password directly in a shell command or source file. A safe pattern is to open an interactive shell in an authorized database container and use the documented credential mechanism, or use a temporary client Pod with a Secret mounted under controlled access. The exact container name, database/user Secret, and connection Service must be obtained from the live cluster and official documentation.

After connecting, create a deterministic synthetic table:

```sql
CREATE TABLE IF NOT EXISTS lab_records (
    id integer PRIMARY KEY,
    payload text NOT NULL
);
INSERT INTO lab_records (id, payload)
VALUES (1, 'before-switchover'), (2, 'stable-marker')
ON CONFLICT (id) DO UPDATE SET payload = EXCLUDED.payload;
SELECT count(*) AS row_count,
       min(id) AS min_id,
       max(id) AS max_id
FROM lab_records;
SELECT id, payload FROM lab_records ORDER BY id;
```

**Expected output (representative; not executed here):** two rows with IDs 1 and 2 and the exact marker strings above. This is synthetic evidence only. For stronger integrity evidence, export deterministic query results before and after the exercise and compare them.

#### 5.4.5 Planned switchover and Pod-deletion failover

A **planned switchover** is a coordinated role transition while the current primary is available. Follow the current CloudNativePG documentation for the supported command or custom-resource field. Do not guess a `kubectl cnpg` plugin command or custom-resource field. **[VERIFY]** the current procedure and required preconditions.

Before the switchover:
1. Confirm all intended instances are healthy and replication is caught up.
2. Confirm the synthetic table contents and save the query result.
3. Record current primary identity, Cluster status, events, and client endpoint.
4. Establish a maintenance window and a bounded timeout.

After the switchover:
1. Inspect Cluster status and Pod roles using the documented status fields/commands.
2. Confirm the new primary.
3. Reconnect the client using the documented read-write endpoint; do not assume an existing TCP session survives.
4. Run the deterministic query again and compare results.

For the separate **primary-Pod deletion** exercise, first confirm the namespace is disposable and the cluster is healthy. Delete only the verified current primary Pod and observe the operator’s response. This is a Pod-level disruption, not a physical node-loss test and not a disaster-recovery test.

**DATA-SAFETY PREFACE — primary-Pod deletion:** This action deletes the selected Pod object and may cause a database role transition or temporary outage. It is permitted only in the disposable `db-lab` cluster with synthetic data. Confirm the current context, namespace, Cluster name, and primary Pod from live status before deleting anything. Never copy the command into production.

```bash
kubectl config current-context
kubectl get cluster,pods -n db-lab -o wide
# Set PRIMARY_POD only after identifying the actual current primary from verified status.
kubectl delete pod "$PRIMARY_POD" -n db-lab --wait=true --timeout=120s
kubectl get cluster,pods -n db-lab -o wide
kubectl get events -n db-lab --sort-by=.lastTimestamp
```

The placeholder `PRIMARY_POD` is not a command to run until set to the verified primary Pod. Observe actual behavior; do not assume a fixed failover time or exact status transition. Then reconnect and re-run the row-level validation query.

Availability means the service resumes accepting work. Durability means committed data survives the failure according to the system’s guarantees. Correctness means the data and application invariants remain valid. One successful query is useful but not a complete durability proof.

#### 5.4.6 Troubleshooting a Cluster that does not become healthy

| Symptom | First checks | Likely investigation |
|---|---|---|
| Custom resource rejected | `kubectl get crd`; `kubectl explain cluster` if the resource exists; API server error | CRD not installed, wrong API version, stale fields |
| Operator not ready | Operator Pods, Deployment, events, logs | Image pull, permissions, invalid configuration, incompatible version |
| PostgreSQL Pod Pending | `kubectl describe pod`; PVC status; node resources | PVC not provisioned, insufficient CPU/memory, topology/affinity |
| PVC Pending | `kubectl describe pvc`; StorageClass and provisioner | No default class, invalid class, unavailable provisioner |
| Pod repeatedly restarts | Pod events and container logs; memory usage | OOM, bad configuration, startup failure, permissions |
| Cluster remains degraded | Cluster status, operator logs, database logs, replication state | Application issue, missing instance, insufficient resources, reconciliation failure |
| Client cannot connect | Service/endpoints, NetworkPolicy, credentials metadata, TLS configuration | Wrong endpoint, stale connection, blocked traffic, authentication mismatch |

Collect evidence before deleting Pods or claims. Repeated restarts can make recovery slower and erase useful timing evidence. Do not “fix” a memory issue by removing limits without a resource plan.

### 5.5 Level 3 — Advanced

#### 5.5.1 Base backups, WAL archiving, retention, and PITR

PostgreSQL records changes in write-ahead log (WAL). A physical base backup supplies a baseline, while archived WAL supplies the sequence of changes needed to recover forward from that baseline. Point-in-time recovery (PITR) restores a cluster to a chosen time within the available recovery window.

A successful base-backup job does not prove PITR is possible. PITR requires a usable base backup, all required WAL from the backup’s starting point through the target, accessible archive storage, compatible recovery configuration, and enough space to restore. Retention must preserve the base backups and WAL needed to meet the required recovery window.

Monitor at least:
- time and status of the most recent successful base backup;
- time of the most recent successfully archived WAL and archive failure counters/logs;
- archive backlog or freshness, where the chosen implementation exposes it;
- object-store reachability and credential validity;
- available PVC and object-store capacity;
- backup retention and expiration behavior;
- age and outcome of the most recent successful restore test.

Exact metrics and status fields depend on the CloudNativePG release and backup implementation. **[VERIFY]** current documented metrics and alerting guidance.

#### 5.5.2 Current backup architecture: do not assume legacy fields

CloudNativePG backup APIs and recommended architecture have evolved. The current release may recommend a Barman Cloud plugin or another supported mechanism; do not assume an older in-tree configuration is still recommended. Before authoring backup manifests, verify:

1. Current official CloudNativePG backup documentation for the selected release.
2. Whether a plugin is required/recommended, its compatible version, installation procedure, and CRDs.
3. Exact `Cluster`, plugin, object-store, `ScheduledBackup`, and recovery API fields.
4. The supported credential Secret format and object-store endpoint/TLS settings.
5. Which status fields and logs prove base backup completion and WAL archive activity.
6. The supported PITR procedure and how to specify the target timestamp/time zone.

**[VERIFY]** `ScheduledBackup`, plugin resources, object-store fields, and `bootstrap.recovery` are not presented here as universally valid current APIs. Use the current official examples verbatim as the starting point and run server-side dry-run validation in a disposable cluster.

#### 5.5.3 Local S3-compatible object storage and MinIO

The parent curriculum asks for local MinIO as an S3-compatible dependency, but compatibility, current CloudNativePG backup architecture, and laptop footprint must be checked first. MinIO’s S3 API compatibility does not by itself guarantee that a particular CloudNativePG plugin version supports the chosen configuration. **[VERIFY]** the current CloudNativePG backup guide and plugin compatibility documentation before installation.

On an 8 GB laptop, kind + three PostgreSQL instances + operator + object store can exceed practical memory or disk limits. A realistic plan is to begin with a database-only lab, measure actual usage, and add the object store only if there is enough headroom. If not, use an explicitly labelled design review or dry-run exercise and mark end-to-end backup/PITR as **not demonstrated**. Do not quietly substitute a different backup path and claim it is the current recommended mechanism.

For any object-store lab:
- use a dedicated disposable bucket and fake credentials;
- grant only the required bucket/object permissions;
- keep credentials in a Kubernetes Secret or current supported secret mechanism;
- do not print credentials or place them in shell history;
- use a short retention policy suitable for synthetic data;
- inspect object names, sizes, and timestamps without exposing secret configuration;
- record both PostgreSQL volume use and object-store disk use.

#### 5.5.4 Scheduled backup and archive pipeline evidence

A scheduled backup resource should be created only after its API and fields are confirmed. **[VERIFY]** the exact `ScheduledBackup` kind, API version, schedule syntax, owner reference, and retention semantics for the selected release. A schedule firing is not evidence that the resulting backup is usable.

Use an evidence table:

| Evidence item | What it proves | What it does not prove |
|---|---|---|
| Backup resource reports completed | Operator reports the operation completed according to its status contract | Restore succeeds or all WAL is available |
| Backup object exists in bucket | Some artifact was written | Artifact is complete, consistent, decryptable, or restorable |
| Recent WAL archive activity | Archive pipeline has moved WAL recently | Every required segment for a chosen PITR target exists |
| Object-store health check | Endpoint is reachable | Credentials have all needed permissions or retention is adequate |
| Restore into a new cluster succeeds | Recovery procedure worked for that tested point/configuration | Every future backup or arbitrary target timestamp will work |
| Application integrity query passes | Selected invariants and rows match expectations | All business-level invariants are correct |

A silent archive failure can be masked by continued database activity until storage fills. Alert on freshness and failure, not merely on whether a backup schedule object exists. Verify exact archive metrics/log messages for the selected plugin and release.

#### 5.5.5 PITR into a new Cluster at a specific timestamp

Restore into a **new Cluster with new PVCs**. Never overwrite the source cluster during this exercise. Use the current official CloudNativePG recovery workflow and exact API fields. The parent syllabus mentions `bootstrap.recovery`, but that field and its shape must be verified against the selected version. **[VERIFY]**

A safe conceptual exercise is:

1. Insert a marker transaction before the target time, for example `before_target`.
2. Record the exact target timestamp in UTC (for example, `2026-10-28T12:00:00Z` is an example timestamp, not a claim that a backup exists at that time).
3. After the target time, insert a second marker `after_target`.
4. Confirm a suitable base backup and continuous WAL covering both transactions and the target time.
5. Create a new recovery Cluster with a distinct name, namespace if appropriate, and new PVCs using the documented recovery API.
6. Wait with a bounded timeout; capture recovery status and logs.
7. Query the restored database. The pre-target transaction should be present and the post-target transaction should be absent if the selected target and recovery semantics are correct.
8. Record restore start/end time, requested target timestamp and timezone, resource identity, status, query results, and integrity checks.

Use a timestamp with an explicit timezone and verify the operator’s documented format. Do not infer success from Pod readiness. If the required WAL is missing, the object store is unavailable, credentials are wrong, the timestamp is outside the recoverable window, or disk is insufficient, stop and diagnose; do not keep retrying destructive changes against the source.

If the full workflow cannot be verified or reproduced on the laptop, mark PITR **not demonstrated** and perform a design review using official documentation. Do not claim a completed PITR test without the restored cluster and data evidence.

#### 5.5.6 PostgreSQL upgrades, pooling, TLS, monitoring, and tuning

**Major versus minor upgrades:** minor releases generally contain fixes within a major version, while major releases can introduce catalog, binary, extension, and behavior changes. Exact upgrade paths and supported in-place or replica-based workflows are operator-specific. Review the operator’s compatibility matrix and PostgreSQL release notes, verify extension compatibility, back up and rehearse restore, then follow the current documented procedure. A backup is not a rollback plan until restoration is tested; data-format changes may make a simple image rollback unsafe.

**Connection pooling:** CloudNativePG may provide a `Pooler` resource integration for PgBouncer in supported releases. **[VERIFY]** whether it is supported in the chosen release, its API version, and exact fields. Pooling can reduce connection overhead but introduces its own sizing, transaction-mode, session-state, timeout, and failover considerations. Test client retry behavior and avoid assuming pooled connections transparently recover every in-flight transaction.

**TLS and credentials:** verify server/client TLS configuration, certificate rotation, user/password rotation, and the selected operator’s supported mechanisms. Keep credentials out of Git, terminal history, and logs. See M09 for broader secret and encryption-key management.

**Monitoring:** use the operator’s documented metrics and alerts. Useful signals include primary/replica roles, replication lag, connection saturation, transaction latency, backup age, WAL archive freshness/failures, PVC utilization, restart/failover events, and restore-test status. Distinguish built-in metrics from proposed custom metrics. See M11 for observability design.

**Storage choices:** a separate WAL volume may be supported in some operator/version combinations, but do not invent a field or assume it improves performance. **[VERIFY]** the current API and driver behavior. Separate volumes introduce additional capacity, attachment, and coordinated-recovery complexity; see Unit 3 for snapshot consistency and Unit 6 (`06-storage-performance-iops-throughput-and-latency.md`) for performance analysis.

**Memory tuning:** `shared_buffers` and other PostgreSQL memory settings must be considered alongside container memory limits, per-connection memory, maintenance operations, and other processes. There is no universal percentage that is optimal for every workload. A too-small limit can cause OOM kills; an overly large setting can starve the container or node. Establish a baseline, measure representative workload, change one variable at a time, and retain a rollback path.

**Fencing and replication:** synchronous replication can reduce the risk of losing recently acknowledged transactions under defined configurations but can increase latency or reduce write availability when required synchronous standbys are unavailable. Asynchronous replication can preserve availability and lower latency but may lose recent acknowledged changes if the primary fails before the replica receives them. Exact semantics depend on PostgreSQL settings and operator configuration. **[VERIFY]** the chosen operator’s supported fields and test the failure cases.

**Network policy and disruption controls:** limit database traffic using M04 NetworkPolicy concepts. Verify whether the operator generates PDBs, anti-affinity, topology constraints, and Service objects by default. Do not duplicate or override generated resources without understanding reconciliation ownership.

#### 5.5.7 Broker awareness: Strimzi/Kafka and alternatives

A PostgreSQL operator manages a database with primary/replica roles, WAL, and database-specific backup/recovery. A Kafka operator manages a distributed log system with brokers, topics, partitions, replicas, metadata quorum, and partition reassignment. The lifecycle concepts overlap, but their safety rules are not interchangeable.

Kafka concepts to know:
- **Partition:** ordered log unit; partitions are the unit of parallelism and replication.
- **ISR (in-sync replicas):** replicas considered sufficiently caught up under Kafka’s rules.
- **KRaft quorum:** Kafka metadata quorum using the Raft-based protocol; controller quorum membership and availability matter independently of application topic replicas.
- **`min.insync.replicas`:** producer durability constraint when using appropriate acknowledgements; exact behavior depends on producer configuration and topic/broker settings.
- **Rebalancing:** moving partition leadership or replicas after broker membership changes; adding a broker does not automatically mean all data is balanced optimally.
- **Rack/topology awareness:** mapping brokers to actual failure domains, which kind does not realistically model.
- **Persistent volumes per broker:** storage capacity, throughput, retention, and recovery time are operational constraints.
- **Rolling restart:** can affect leaders, ISR, and client errors; use documented operator and Kafka procedures.
- **JBOD:** multiple log directories/devices per broker, with failure and recovery implications that depend on Kafka and operator support.

**[VERIFY]** Strimzi installation instructions, current custom-resource API version, KRaft requirements, storage schema, and fields against official documentation before applying a Kafka custom resource. Official starting point: https://strimzi.io/documentation/

An annotated Kafka manifest should be treated as a design-review exercise unless the API version and all fields are verified. A one-node broker can teach object structure and client basics, but it does not demonstrate quorum, replication, or high availability. With an 8 GB laptop, this lesson does not require installing a second operator stack.

At awareness level:
- **Redis:** persistence options, replication, sentinel/cluster topology, and operator-specific backup/upgrade behavior differ by deployment mode.
- **RabbitMQ:** quorum queues, cluster membership, message persistence, and rolling upgrade compatibility require application-aware procedures.
- **NATS:** JetStream persistence, replicas, stream placement, and recovery differ from PostgreSQL WAL or Kafka partitions.

Do not generalize a PostgreSQL failover or backup method to these brokers.

### 5.6 Level 4 — Expert

#### 5.6.1 Operator evaluation and governance

Evaluate an operator with evidence, not popularity alone:

| Criterion | Questions and evidence |
|---|---|
| Maintenance and release governance | Are releases active, security issues handled, and release notes understandable? |
| Compatibility | Which Kubernetes and database versions are supported? Is there a published compatibility matrix? |
| Backup/PITR | Is the current backup architecture documented? Are restore steps explicit and testable? |
| Failover | Is behavior documented under primary failure, network partition, and replica lag? Can it be rehearsed safely? |
| Upgrades and CRDs | How are CRD schema changes applied? Are controller and CRD versions compatible? What rollback limits exist? |
| Observability | Are metrics, events, status conditions, and alerts documented? |
| Security | What RBAC does the controller require? Can scope be reduced? How are images, webhooks, and dependencies released? |
| License and support | Is the license acceptable? Is there vendor support, community support, or only internal ownership? |
| Portability and exit | Can data be exported in a standard format? How are custom resources translated or retired? |
| Operational burden | Who owns on-call, restores, upgrades, storage capacity, incident response, and postmortems? |

Mark candidate-specific claims **[VERIFY]** against the exact release, release notes, support policy, license, and compatibility matrix. A promising repository alone is not evidence of production support.

#### 5.6.2 Operator and CRD upgrades

An operator upgrade can change controller behavior, generated resources, CRD schemas, defaults, admission webhooks, or supported database versions. Plan upgrades in this order:

1. Read release notes, upgrade guides, compatibility matrices, and known issues.
2. Confirm the target controller and CRD versions are compatible with existing custom resources.
3. Identify whether the upgrade changes defaults or requires a CR migration.
4. Verify a current backup and a tested restore path.
5. Test in a disposable cluster with representative resources and extensions.
6. Define canary scope, maintenance window, success criteria, and abort conditions.
7. Apply the documented CRD/controller ordering. Do not invent an order; it varies by operator.
8. Monitor reconciliation, database roles, replication, storage, client errors, and backup freshness.
9. Document rollback limitations. Rolling the controller image back may not reverse CRD schema changes or database on-disk changes.

#### 5.6.3 Operator blast radius and outage behavior

A cluster-wide controller may have broad permissions across namespaces or cluster-scoped resources. Threat-model its service account, role bindings, Secret access, ability to create Pods, admission webhooks, image supply chain, and network egress. Consider whether namespace-scoped installation is supported and whether it materially reduces permissions.

If the operator crashes or is deleted, already-running database Pods will often continue running for some time because their processes are separate from the controller. However, reconciliation, automated failover, replacement Pod creation, backup scheduling, and other lifecycle actions may stop or become delayed. Exact behavior depends on the operator, database state, Kubernetes version, and whether a webhook or other component is required. **[VERIFY]** the chosen operator’s documented behavior. Do not assume a controller outage is harmless, and do not delete the operator as an incident response shortcut.

Keep the operator’s configuration and custom resources in a reviewed GitOps workflow where appropriate. Do not commit plaintext credentials. See M08 for GitOps handoff; see M09 and M12 for secrets and security.

#### 5.6.4 Required incident case: failover occurred but clients kept the old connection

**Symptom/impact:** the database reports a new primary, but clients continue to receive connection errors, writes fail, or a connection pool keeps stale sessions.

**Read-only checks:**
```bash
kubectl get cluster,pods,svc -n db-lab -o wide
kubectl get endpointslice -n db-lab
kubectl get events -n db-lab --sort-by=.lastTimestamp
kubectl logs -n <operator-namespace> deploy/<operator-deployment> --tail=200
```
Use the actual operator namespace/deployment and documented Cluster status fields. Do not assume the service suffix alone proves role routing.

**Evidence:** time of role transition, old/new primary identities, service endpoints, client error logs, pool state, DNS results, transaction outcome, and replication/cluster health.

**Avoid:** blindly retrying non-idempotent writes; assuming an in-flight transaction either committed or rolled back; manually changing endpoints without understanding operator reconciliation.

**Decision/recovery:** confirm the current primary and read-write endpoint, reset/recycle stale client connections using the application’s supported procedure, and implement bounded reconnects with transaction-aware retry/idempotency. Reconcile uncertain transactions before replaying them.

**Post-recovery:** run deterministic reads, verify expected transaction state, confirm no duplicate writes, check application error rates, and document connection recovery time.

#### 5.6.5 Required incident case: WAL archiving failed silently and the volume filled

**Symptom/impact:** PostgreSQL data volume approaches full capacity because WAL cannot be archived or recycled according to the expected policy. Write availability may degrade or stop.

**Read-only checks:** inspect Cluster status, database/operator logs, archive freshness/failure metrics, PVC utilization, object-store health, credentials metadata, network policy, and recent backup events. Do not print Secret contents.

**Evidence:** last successful archived WAL time, archive error details, PVC free space over time, object-store request failures, credentials rotation history, retention configuration, and recent base-backup state.

**Avoid:** deleting WAL files manually; deleting PVCs or backup objects; lowering retention without understanding PITR requirements; restarting repeatedly without addressing the archive destination.

**Decision/recovery:** identify whether the failure is credentials, endpoint/TLS, permissions, object-store capacity, network access, or a plugin/controller issue. Restore archive flow using the documented procedure, confirm new WAL archives are arriving, and evaluate free-space headroom. If capacity is critical, escalate to the database/storage owner and follow a tested emergency capacity procedure. Do not delete files from PostgreSQL’s data directory manually.

**Post-recovery:** verify archive freshness, capacity trend, base-backup status, and the ability to restore from the intended recovery window. Add an alert on archive freshness and disk runway if absent.

#### 5.6.6 Required incident case: backup job succeeded but restore was never tested

A green job status is incomplete evidence. It may show that an operation finished according to the controller’s status contract, but not that the backup is complete, that the required WAL is present, that credentials remain valid, or that the target can restore within the RTO.

**Immediate actions:** preserve job status, logs, object metadata, configuration, and retention details. Identify the most recent backup that has actually been restored successfully. Do not delete older backups merely because a newer job reports success.

**Recovery and remediation:** create a separate restore target using the documented procedure, record target timestamp and restore duration, validate expected transactions before/after the target, compare row counts/checksums and application invariants, and capture errors. If the restore fails, determine whether the issue is missing WAL, incompatible version, access/credential failure, insufficient capacity, or invalid recovery configuration. Update the backup policy only after understanding the failure.

**Success criteria:** an independent restore completes, application integrity checks pass, and measured RTO/RPO are compared with service objectives.

#### 5.6.7 Required incident case: operator/CRD not ready or reconciliation stalled

**Symptom/impact:** custom resources remain pending, controller pods restart, or the operator stops reconciling expected changes.

**First read-only checks:** CRD existence and conditions, operator Deployment/Pod status, recent events, controller logs, custom resource status/conditions, API errors, and service account permissions.

**Evidence:** controller image/version, CRD schema version, custom resource API version, relevant log excerpt, events, and any recent upgrade/change.

**Avoid:** deleting CRDs to “reset” the operator; force-applying incompatible schemas; deleting database Pods/PVCs as a controller workaround.

**Decision/recovery:** compare installed controller, CRDs, and custom resources against the supported compatibility matrix. Follow the documented repair/upgrade path. If databases are running, preserve them while restoring controller health. Escalate if CRD conversion, webhook, or database state is uncertain.

**Post-recovery:** verify reconciliation resumes, roles/replication remain healthy, backup scheduling and monitoring work, and no custom resources were silently dropped or defaulted unexpectedly.

#### 5.6.8 Required incident case: PITR missing WAL or wrong timestamp

**Symptom/impact:** recovery fails before reaching the target or the restored database contains unexpected transactions.

**Read-only checks:** requested target timestamp/timezone, restore logs, base-backup metadata, archived WAL inventory, object-store availability and permissions, recovery resource status, and disk capacity.

**Avoid:** restoring over the source, deleting archives to free space, changing the target timestamp without recording the change, or treating a partial recovery as success.

**Decision/recovery:** verify the selected base backup can reach the target using available WAL; confirm timestamp format and timezone; check plugin/API compatibility and object-store credentials; create a corrected recovery Cluster with a new name and new PVCs only after evidence is preserved. If required WAL is absent, select an explicitly approved recoverable point and document the resulting data-loss window.

**Post-recovery:** verify a transaction before the target is present and a transaction after the target is absent, plus row counts and application invariants. Record the actual recovered point, not just the requested point.

#### 5.6.9 Required incident case: operator crash/deletion during a database outage

**Symptom/impact:** database Pods may still run, but automated reconciliation, failover, or replacement actions may be unavailable.

**Read-only checks:** controller status and logs, CRDs, Cluster status, Pod roles, database logs, current primary, replication health, and recent changes.

**Avoid:** deleting the database resources or CRDs, reinstalling a different operator version without compatibility review, or assuming the database will automatically fail over while the controller is down.

**Decision/recovery:** restore the compatible controller using the documented installation/upgrade path; preserve database resources and data. If a database-level outage is in progress, follow the application-specific manual recovery procedure only with database-owner approval and fencing checks.

**Post-recovery:** verify reconciliation, primary/replica roles, replication, client connections, backups, alerts, and custom-resource conditions.

#### 5.6.10 Required incident case: upgrade or CRD compatibility failure

**Symptom/impact:** operator fails to start, custom resources are rejected, fields are pruned/defaulted, or reconciliation behaves differently after an upgrade.

**Read-only checks:** controller/CRD versions, release notes, API discovery, custom resource YAML, webhook logs, and recent rollout events.

**Avoid:** deleting CRDs, reverting controller images without understanding schema compatibility, or applying manifests copied from a different release.

**Decision/recovery:** follow the documented upgrade path, restore compatibility in a staging environment where possible, and use supported conversion/migration procedures. Confirm backup/restore before any database-version transition. Escalate if a CRD schema change or database on-disk format change may not be reversible.

**Post-recovery:** compare custom resource specs/status, verify reconciliation and database integrity, validate backups and WAL archiving, and document the final supported version combination.

#### 5.6.11 Managed database alternative

| Dimension | Operator on Kubernetes | Managed database service |
|---|---|---|
| Operational effort | Team owns Kubernetes/operator lifecycle, storage, database behavior, and on-call | Provider owns more infrastructure operations; team still owns application and data policy |
| Control | Greater control over configuration and placement, bounded by operator support | Configuration options constrained by service offering |
| Portability | Kubernetes/operator-specific APIs and extensions can create migration work | Provider APIs and proprietary features can create vendor coupling |
| Availability/recovery | Depends on operator, storage, topology, replication, and tested runbooks | Depends on service tier and documented provider capabilities; validate restore and failover |
| Cost model | Infrastructure plus engineering/on-call cost; “self-hosted” is not free | Service charges plus network/egress and operational integration cost |
| Compliance | Team owns platform controls, evidence, patching, and data handling | Shared responsibility; verify residency, audit, encryption, and access controls |
| Exit strategy | Plan data export and replacement of custom resources/operator-specific workflows | Test export, schema compatibility, downtime, and provider-specific dependencies |

No paid service is required for this unit’s labs. Use the table to make a design decision, not to imply that managed services are always superior. The right choice is the one the organization can secure, operate, and recover within its objectives.

### 5.7 SRE lens

#### Availability, durability, and correctness

These are separate properties:

- **Availability:** the service accepts and completes useful requests.
- **Durability:** acknowledged data survives failures within the system’s stated guarantees.
- **Correctness:** recovered data and application invariants are valid.

A failover may restore availability while a client retains a stale connection. A backup may exist while the needed WAL is absent. A restore may complete while business invariants are violated. Track each property with separate checks.

#### Define RPO and RTO

RPO is the maximum acceptable data-loss window. RTO is the maximum acceptable recovery duration. Define them with service owners and validate them with measured drills. A target is not evidence; the latest restore-test result and its duration are evidence. Record the actual recovery point and data-loss window after every exercise.

#### Capacity and WAL freshness

Monitor PVC utilization, growth rate, and estimated time to full. Monitor WAL archive freshness and errors, backup age, object-store capacity, and retention. A volume that is 70% full but growing rapidly may be more urgent than a stable volume at 85%. Establish alert thresholds from workload measurements and the time required to respond, not from a generic percentage alone.

#### Failover, retries, and transaction safety

Clients must reconnect to the current read-write endpoint and handle broken connections. Retry only when transaction semantics are understood. A connection failure does not reveal whether a transaction committed. Use idempotency keys, transaction outcome checks, or application-specific reconciliation before replaying non-idempotent work.

#### Game days and abort criteria

Run failover and restore exercises during an approved window in disposable environments first. Define abort conditions: unexpected data loss, replication lag beyond a threshold, quorum risk, disk exhaustion, loss of the source recovery path, repeated OOMs, or inability to establish the current primary. Preserve evidence and stop the exercise when safety assumptions are violated.

#### Game-day matrix

| Scenario | Hypothesis | Safe injection and preconditions | Expected evidence | Abort conditions | Recovery verification | kind limitation |
|---|---|---|---|---|---|---|
| Planned switchover | Operator coordinates role change and clients can reconnect | Disposable cluster; synthetic data; healthy replicas; record baseline | Primary role changes; client reconnects; rows unchanged | Replication unhealthy or data baseline unavailable | Query markers, role/replication status, client smoke test | Does not model real-zone latency/failure |
| Primary Pod deletion | Operator responds to Pod-level disruption | Separate DATA-SAFETY PREFACE; verify current primary and namespace | Events, role transition, new Pod state | Unclear primary, unhealthy replicas, unexpected data discrepancy | Reconnect, compare row values, inspect logs | Not equivalent to physical node loss or disaster recovery |
| PITR restore | Base backup and WAL can restore a target point | New Cluster/new PVCs; target timestamp recorded; source preserved | Recovery status, start/end time, before/after marker query | Missing WAL, object store unavailable, source at risk | Integrity queries and target timestamp evidence | Local storage/object store is not durable offsite backup |
| Worker-node loss | Team follows evidence-led recovery without unsafe dual writer | Dedicated kind cluster; synthetic data; record worker and resources | Actual node/Pod/PVC states and event timeline | Process state or storage attachment uncertain | Restart/recovery according to documented procedure; verify data | kind does not simulate all partitions, fencing, or hardware failures |

### 5.8 Security lens

- **Controller RBAC and blast radius:** inspect the operator’s ServiceAccount, Roles/ClusterRoles, and bindings. Determine whether it can read Secrets across namespaces, create arbitrary Pods, mutate storage resources, or manage cluster-scoped objects. Use namespace scope where supported and sufficient.
- **Secrets:** use fake lab credentials only. Do not put credentials in Git, command-line arguments, logs, shell history, or evidence bundles. Avoid `kubectl get secret -o yaml` in transcripts. See M09 for secret lifecycle, TLS, and encryption-key handling.
- **Object-store permissions:** use a dedicated lab bucket with the minimum required object read/write/list/delete permissions documented by the selected backup implementation. Separate lab and production credentials and avoid broad account-level keys.
- **TLS and rotation:** verify certificate validation, trust roots, client TLS requirements, rotation behavior, and connection-pool refresh. Test rotation in staging; do not disable verification as a shortcut.
- **Network segmentation:** use M04 NetworkPolicy principles to restrict database and object-store access. Allow only required client/operator/backup traffic and required DNS. Confirm the CNI enforces policies in the target environment.
- **Backup data:** backups can contain the entire database, including sensitive records and credentials stored in tables. Apply encryption, access controls, retention, and secure deletion policies. Sanitize test restores before broader access.
- **Supply chain:** pin controller, database, plugin, sidecar, and object-store images to reviewed versions/digests where supported. Review CRD changes, webhooks, release notes, signatures/provenance where available, and security advisories.
- **Pod security and volume permissions:** prefer non-root containers and minimal capabilities; verify UID/GID, `fsGroup`, volume ownership, and init-container privilege needs. See M01.
- **Exit and upgrade risks:** avoid depending on undocumented custom fields or unexportable data formats. Maintain a tested data-export path and plan for operator replacement or retirement.
- **Policy checks:** define reviewable checks for image pinning, Secret handling, resource limits, TLS, network policy, backup configuration, retention, and RBAC. This lesson does not assume a policy engine is installed.

### 5.9 Production checklist

#### Design review

- [ ] Decide whether the database should run on Kubernetes; document the rationale and alternatives.
- [ ] Identify an accountable database/on-call owner and escalation path.
- [ ] Confirm operator maintenance, license, support model, compatibility matrix, CRD lifecycle, and exit path.
- [ ] Define SLOs, RPO, RTO, maintenance windows, and abort conditions.
- [ ] Document replication, failover, fencing, client retry, and transaction idempotency behavior.
- [ ] Confirm topology and storage backend support the intended failure model; do not treat kind as production proof.

#### Installation

- [ ] Pin and record Kubernetes, operator, database, plugin, and image versions.
- [ ] Verify CRDs and API versions against official documentation before applying custom resources.
- [ ] Confirm controller health and minimum RBAC required.
- [ ] Review resource requests/limits, storage size/class, topology, and capacity headroom.
- [ ] Inspect generated Pods, PVCs, Services, Secrets metadata, PDBs where present, events, and logs.
- [ ] Verify TLS, credentials, NetworkPolicy, non-root execution, and volume permissions.

#### Day-2 operations

- [ ] Monitor primary/replica roles, replication lag, connection saturation, restart/failover events, and client errors.
- [ ] Verify readiness probes reflect traffic eligibility and do not confuse Pod readiness with replication health.
- [ ] Confirm clients reconnect to the correct read-write endpoint and handle uncertain transaction outcomes.
- [ ] Track PVC growth, object-store capacity, backup age, WAL archive freshness, and retention.
- [ ] Document switchover, failover, upgrade, and operator-outage runbooks.
- [ ] Test maintenance and disruption behavior before production rollout.

#### Backup and recovery

- [ ] Verify current supported backup architecture and exact API fields.
- [ ] Confirm base backup completion and continuous WAL archive freshness.
- [ ] Check retention covers the required recovery window.
- [ ] Protect object-store credentials and verify object-store permissions/connectivity.
- [ ] Restore into a separate cluster with new PVCs.
- [ ] Test specific timestamp recovery with timezone and transaction-presence/absence checks.
- [ ] Record restore duration, recovery point, data-loss window, and integrity results.
- [ ] Do not treat Kubernetes etcd snapshots as PV backups: etcd snapshots do **not** contain PV data.

#### Upgrade

- [ ] Review release notes, compatibility matrices, CRD changes, and database upgrade path.
- [ ] Rehearse in staging with representative extensions and data.
- [ ] Verify backup and restore before major database upgrades.
- [ ] Document canary/maintenance plan, abort conditions, and rollback limitations.
- [ ] Validate roles, replication, clients, backups, WAL archive, and alerts after upgrade.

#### Incident response

- [ ] Start with read-only status, logs, events, and capacity checks.
- [ ] Preserve source resources and data during restore investigations.
- [ ] Never restore over the source during a PITR exercise.
- [ ] Do not delete WAL, PVCs, PVs, or backup objects as generic cleanup.
- [ ] Validate client behavior and transaction outcomes after failover.
- [ ] Escalate when process state, fencing, required WAL, credentials, or recovery target is uncertain.
- [ ] Run application-level integrity checks before declaring recovery complete.

### 5.10 Hands-on lab set

#### Common environment preflight

The labs are designed for a disposable kind cluster on WSL2 Ubuntu or native Linux. They have not been executed here. Check resources before installing anything:

```bash
kind version
kubectl version
kubectl config current-context
kubectl get nodes -o wide
kubectl get storageclass
df -h .
free -h
docker system df
```

**Expected output (representative; not executed here):** a kind version, Kubernetes client/server versions, a lab context, one control-plane node and at least one worker, available storage class information, and free disk/memory figures. Stop if the context is shared or production. Record versions and actual resource usage.

Use one lab namespace per exercise where possible. Do not use real credentials or business data. The resource estimates below are planning estimates, not guarantees.

#### Lab 1 — Install CloudNativePG and create a three-instance PostgreSQL cluster

**Objective:** install a compatible operator, create a three-instance cluster, inspect generated resources, write synthetic data, test planned switchover, and separately observe Pod-deletion failover.

**Estimated duration:** 90–150 minutes. **Approximate resource budget:** 2–4 GB additional memory for three small PostgreSQL instances plus operator and related Pods; disk varies by images and provisioner. Verify current requirements and actual use before installation.

**Prerequisites:** kind and container runtime; a dedicated disposable cluster/context; sufficient disk; current official CloudNativePG docs open for the selected version.

**Installation steps:**
1. Create or select a dedicated kind cluster named `cnpg-lab`; verify it does not already contain valuable resources.
2. Follow the current CloudNativePG official installation page for the chosen compatible release. Record the exact version, install method, and source. Do not paste an unverified remote manifest or guess a version tag.
3. Wait for controller readiness with a bounded timeout and verify CRDs are established.
4. Create namespace `db-lab`.
5. Validate `cnpg-cluster.yaml` with server-side dry-run and apply only after confirming all fields against the installed API.
6. Wait for the Cluster to become healthy with a bounded timeout; if it does not, stop and troubleshoot rather than repeatedly deleting Pods.

The sample `cnpg-cluster.yaml` is provided in Section 5.4.3 and must be checked against current docs. It uses `pg-lab`, three instances, and small resource requests/limits. **[VERIFY]** current API version, fields, minimum resources, image defaults, and storage requirements.

**Inspection commands:**

```bash
kubectl get crd | grep -i postgresql
kubectl get cluster -n db-lab -o wide
kubectl describe cluster pg-lab -n db-lab
kubectl get pods,pvc,svc -n db-lab -o wide
kubectl get pdb -n db-lab
kubectl get secrets -n db-lab
kubectl get events -n db-lab --sort-by=.lastTimestamp
kubectl logs -n <operator-namespace> deploy/<operator-deployment> --tail=200
```

Replace placeholders using discovered names. Inspect Secret metadata only; never print values.

**Data validation:** connect using the current official documented method, run the `lab_records` SQL in Section 5.4.4, and save its row-level result. Record current primary and replica roles using the documented status interface.

**Planned switchover:** follow the current official procedure, verify preconditions, record old/new primary identities, reconnect the client, and compare the same deterministic query.

**Primary Pod deletion:** perform the separate DATA-SAFETY PREFACE and controlled deletion in Section 5.4.5. Verify the actual primary role after reconciliation and rerun the integrity query. This is not a node-loss or disaster-recovery test.

**Success criteria:** operator and CRDs are healthy; the three-instance Cluster reaches its documented healthy state; generated resources are understood; synthetic rows remain correct after planned switchover and the separate Pod disruption; client reconnection is observed.

**Reduced variant:** if the three-instance cluster exceeds the laptop budget, create a one-instance cluster using the same current API but `instances: 1`, only after verifying the schema. This variant teaches installation and resource inspection; it cannot prove replication, switchover, failover, quorum, or HA.

**Troubleshooting:** use the table in Section 5.4.6. Capture events and logs before changing resources. Check CRDs, controller readiness, PVC binding, image pulls, scheduling, memory pressure/OOM, PostgreSQL logs, and operator reconciliation logs.

**DATA-SAFETY PREFACE — Lab 1 cleanup:** The following cleanup removes the disposable database resources and may delete PVCs and their backing lab data, depending on the operator and storage reclaim behavior. Verify the current context, namespace, Cluster name, and synthetic-only contents. Preserve evidence first. Remove the database custom resource according to the current operator documentation; then remove the operator only if this is a dedicated lab installation and no other custom resources depend on it. Do not delete shared CRDs or operator resources from a shared cluster.

```bash
kubectl config current-context
kubectl get cluster,pods,pvc,svc -n db-lab -o wide
# After confirming the target is disposable, follow the documented resource cleanup order.
kubectl delete namespace db-lab --wait=true --timeout=120s
```

Namespace deletion does not guarantee every cluster-scoped resource or backend asset is removed. Inspect remaining PVs and operator resources. Do not automatically delete them.

#### Lab 2 — Backup to local S3-compatible object storage and scheduled backup

**Objective:** design and, if current documentation and laptop resources permit, configure a supported base-backup and continuous-WAL archive path to a local S3-compatible object store.

**Estimated duration:** 2–4 hours. **Resource/disk estimate:** highly dependent on object-store implementation, images, backup data, and WAL volume. Plan several additional GB of disk headroom and monitor memory; the full stack may exceed the laptop budget.

**Prerequisites:** successful Lab 1; current CloudNativePG backup documentation; verified plugin/backup API and compatibility; dedicated object-store endpoint/bucket; fake credentials only.

**Version gate:** do not proceed to apply backup YAML until you have recorded:
- CloudNativePG version and current recommended backup mechanism;
- plugin/CRD versions if required;
- exact Cluster backup fields and Secret schema;
- exact scheduled-backup API/fields if supported;
- object-store compatibility and required permissions.

**[VERIFY]** The current release may recommend a Barman Cloud plugin or another mechanism. Do not assume an older in-tree backup configuration is supported. The exact custom resources are intentionally not fabricated here because they must match the chosen release. Use the current official documentation’s example and perform `kubectl apply --dry-run=server` in the disposable cluster.

**MinIO decision:** use local MinIO only if the current CloudNativePG docs support the chosen S3-compatible configuration and resource measurements show enough headroom. If not, complete a design-only exercise and mark end-to-end backup/PITR **not demonstrated**. Do not silently substitute a different backend.

**Procedure after version/API verification:**
1. Create a dedicated object-store namespace or isolated deployment and a bucket used only by this lab.
2. Configure fake credentials in a Secret using the supported format. Do not print the Secret.
3. Apply the documented backup configuration and verify the Cluster reconciles.
4. Trigger a base backup using the documented mechanism.
5. Verify the backup’s status and inspect object metadata (names, sizes, timestamps) without printing credentials.
6. Verify continuous WAL archiving by checking documented status/metrics/logs and that new archive objects appear over time.
7. Configure a scheduled backup only if the current release supports the documented API; verify the schedule and the resulting backup separately.
8. Record retention, disk/object-store use, and the most recent archive time.

**Expected output (representative; not executed here):** the documented backup resource reports completion, backup artifacts appear in the dedicated bucket, and archive freshness advances while the database generates writes. Actual resource names, status conditions, and logs depend on the selected backup implementation.

**Success criteria:** a base backup is evidenced, WAL archiving is demonstrably active, scheduled backup behavior is documented if configured, credentials remain secret, and the recovery window/retention limits are understood.

**Troubleshooting:** credential/permission errors—verify Secret key names and bucket-scoped permissions without exposing values; no new WAL—inspect plugin/operator/PostgreSQL logs and archive freshness; object store unavailable—check DNS, service endpoints, NetworkPolicy, TLS, and capacity; PVC filling—stop workload growth if necessary and follow a reviewed capacity response, never manually delete WAL.

**DATA-SAFETY PREFACE — Lab 2 cleanup:** Deleting the bucket, object-store PVC, backup custom resources, or database resources destroys synthetic backup artifacts and may eliminate the only recovery copy for this lab. Record evidence and confirm the bucket is dedicated to this exercise before cleanup. Use the selected object-store’s documented deletion procedure. Do not delete backups from any shared bucket.

#### Lab 3 — Restore to a specific timestamp (PITR) into a new Cluster

**Objective:** demonstrate, or transparently document why it cannot be demonstrated, a point-in-time restore into a new Cluster using a verified current CloudNativePG recovery workflow.

**Estimated duration:** 2–4 hours if backup/WAL and resources are available; longer when troubleshooting. **Resource/disk estimate:** a second database cluster and restore workspace may roughly double database storage and memory demand. Verify headroom before creating it.

**Prerequisites:** Lab 2 has a verified base backup and WAL archive spanning the target; current recovery API documentation; enough disk for source and target clusters; synthetic data.

**DATA-SAFETY PREFACE:** This lab creates a separate recovery Cluster and new PVCs; it must not overwrite or mutate the source cluster. Confirm source Cluster name, target Cluster name, namespace, and object-store bucket. Preserve the source and its backups until validation is complete. If the required WAL or disk headroom is uncertain, do not start a full restore.

**Procedure:**
1. Insert a transaction with a unique marker before the chosen target time, and verify it in the source.
2. Record a target timestamp in UTC using the exact format documented by the current API. Wait until after that timestamp, insert a second marker transaction, and verify both are present in the source.
3. Confirm the base backup and WAL archive cover the target. If the archive is not continuous or the target falls outside the recoverable range, stop.
4. Create a new Cluster with a distinct name, such as `pg-restore-lab`, using the current official PITR recovery fields. **[VERIFY]** the current `bootstrap.recovery` shape or other supported API before writing/applying the manifest.
5. Use new PVCs and the documented object-store credentials mechanism. Validate with server-side dry-run first.
6. Wait with a bounded timeout. Capture recovery status, events, operator logs, PostgreSQL logs, and actual start/end times.
7. Connect to the restored Cluster and query both marker transactions. The transaction before the target should be present and the transaction after the target should be absent if the recovery target and semantics are correct.
8. Validate row counts, deterministic values, and application-level invariants. Record the actual recovered point and any data-loss window.

**Expected output (representative; not executed here):** the restore Cluster becomes healthy, the pre-target marker exists, and the post-target marker is absent. This is an acceptance criterion, not a claim that a restore ran.

**Failure handling:**
- Missing WAL: identify the last available archived segment and choose an approved recoverable target; record the data-loss implication.
- Wrong timestamp/timezone: verify documented format, UTC conversion, and the actual target used.
- Credential error: verify Secret metadata/key names and bucket permissions without printing values.
- Object-store unavailable: inspect endpoint, TLS, DNS, policy, and backend health.
- Insufficient disk: stop safely and free only explicitly disposable lab resources after evidence collection; do not delete source data or required backups.
- Recovery Cluster stuck: inspect CRD fields, status, events, logs, PVC binding, and operator compatibility before retrying.

If full PITR cannot be reproduced within the laptop budget or current APIs cannot be verified, complete the design/evidence worksheet and mark PITR **not demonstrated**. Do not claim success based on a successful base backup or a manifest that merely applies.

**Cleanup — DATA-SAFETY PREFACE:** Deleting the restore Cluster and its PVCs destroys the recovered lab copy. Deleting the source Cluster or object-store bucket can destroy the only source/recovery evidence. Confirm names and preserve results before deleting any resource.

#### Lab 4 — Optional broker operator awareness lab

**Objective:** learn to review broker custom-resource design without implying that a single broker proves high availability.

**Resource gate:** optional and not required on the 8 GB laptop. A second operator stack may exceed available memory/disk.

Use the current official Strimzi documentation to verify installation, API version, KRaft mode requirements, and storage schema. Do not apply an unverified Kafka manifest. In a design-only exercise, annotate:
- Kafka metadata quorum/controller topology;
- broker count and failure-domain assumptions;
- topic partition count and replication factor;
- ISR and `min.insync.replicas`;
- storage class, capacity, retention, and JBOD choice if supported;
- rack/topology awareness and actual failure domains;
- rolling restart and partition-reassignment procedure;
- client retry and delivery semantics.

If a minimal one-node broker is installed, label it a single-node mechanics lab only. It does not demonstrate quorum, replication, or high availability. **[VERIFY]** current image footprint and version compatibility before installation.

**DATA-SAFETY PREFACE — broker cleanup:** Removing a broker custom resource, namespace, PVCs, or object-store data can destroy all messages and metadata in the lab. Verify the context and that the cluster contains synthetic data only; preserve evidence before cleanup.

#### Required game-day exercise

Use the matrix in Section 5.7 to run a controlled switchover, primary-Pod deletion, and restore exercise. For node loss, use the safe observational approach from Unit 4 and do not force-delete a Pod while process state is uncertain. Record a hypothesis before each exercise and compare expected versus observed behavior.

| Field | Record |
|---|---|
| Scenario and hypothesis | What failure behavior are you testing, and what should happen? |
| Preconditions | Synthetic data, healthy baseline, backups where relevant, capacity, owner approval |
| DATA-SAFETY PREFACE | Exact resources affected and proof they are disposable |
| Injection | Exact documented command/action and timestamp |
| Expected behavior | Based on the selected operator/version docs |
| Observed evidence | Resource status, logs/events, roles, client errors, archive freshness, query results |
| Abort condition | Data discrepancy, quorum risk, disk exhaustion, unclear process/fencing state |
| Recovery verification | Role/replication status, client reconnection, data-integrity checks |
| Limitations | What kind does not represent: physical zones, durable object storage, realistic partitions |

### 5.11 Self-check questions

1. What is the difference between a CRD, a custom resource, and an operator controller?
2. Why is a StatefulSet insufficient by itself to guarantee PostgreSQL high availability?
3. What evidence should you inspect before and after a CloudNativePG planned switchover?
4. Why does a successful base backup not prove that PITR will work?
5. What are the prerequisites for restoring to a specific timestamp, and why must the restore use a new Cluster?
6. How can WAL archiving fail silently, and what signals should alert on it?
7. What is the trade-off between synchronous and asynchronous replication?
8. Why can a failover succeed while clients still experience errors?
9. What must be checked before upgrading an operator or CRD?
10. Why does a one-node Kafka lab not prove quorum or high availability?
11. What happens operationally if an operator controller crashes while database Pods are running?
12. Which responsibilities remain with the team even when using a managed database service?

**Answer key / rubric:**

- **Strong:** separates Kubernetes, operator, database, storage, and client responsibilities; cites version-specific docs and live evidence; includes backup plus WAL requirements; restores into a new cluster; validates transaction presence/absence and application invariants; describes abort criteria and security controls.
- **Partial:** names the correct concepts but treats controller status as proof of data correctness, does not check WAL freshness, or omits client reconnection and restore evidence.
- **Unsafe:** restores over the source, deletes WAL/PVCs as generic cleanup, exposes Secret values, treats a single broker as HA, assumes a backup job guarantees recovery, or performs version upgrades without compatibility and restore checks.

### 5.12 Evidence artifacts

Keep evidence concise, timestamped, and free of credentials or sensitive records.

- `environment.txt`: kind/Kubernetes/operator/database/plugin versions, current context, node list, CPU/memory/disk availability.
- `operator-install.md`: official source, exact installation method, version, CRDs installed, compatibility checks, and unresolved `[VERIFY]` items.
- `cluster-before.yaml` / `cluster-after.yaml`: custom resource and status evidence with sensitive values removed.
- `resource-inventory.txt`: Pods, PVCs, Services, PDBs where present, Secret names/metadata, and events.
- `operator-logs.txt` and `postgres-logs.txt`: bounded relevant excerpts, timestamps, and redaction.
- `synthetic-data-baseline.csv`: deterministic row values before switchover/failover and after recovery.
- `failover-timeline.md`: old/new primary, start/end timestamps, client errors, reconnect duration, and integrity results.
- `backup-evidence.md`: base backup ID/status, artifact metadata, most recent WAL archive time, retention, object-store capacity, and relevant logs.
- `restore-test.md`: source and target cluster names, requested UTC target, actual recovery point, start/end, status, before/after marker results, row counts, and integrity checks.
- `upgrade-review.md`: compatibility matrix, release notes, CRD changes, rehearsal, abort/rollback criteria, and owner approval.
- `game-day-results.md`: hypothesis, preconditions, injection, expected vs observed behavior, abort decision, recovery validation, limitations.
- `verification-register.md`: exact docs/API/resource checks for each `[VERIFY]`, observed outcome, date, and reviewer.

Never include decoded Secret values, passwords, access keys, customer data, or unredacted connection strings in these artifacts. Store them only in the approved secure evidence location.

### 5.13 Common interview and design-review questions

1. **What does a database operator add beyond a StatefulSet?**  
   A controller can encode application-specific lifecycle operations such as bootstrap, role management, failover, backup, and recovery where supported. A StatefulSet supplies identity and Pod lifecycle primitives; neither one alone proves application correctness or recoverability.

2. **How would you prove PostgreSQL is recoverable to a point in time?**  
   Show a usable base backup, continuous required WAL, documented recovery configuration, and a successful restore into a separate cluster. Validate a transaction before the target is present and one after the target is absent, then check application invariants and measured recovery time.

3. **Why might clients fail after a successful primary switchover?**  
   Existing TCP sessions and pool connections may point to the old primary; DNS and endpoint updates are not equivalent to reconnecting an application session. Verify the new read-write endpoint, recycle stale connections safely, and retry only when transaction outcome/idempotency is understood.

4. **What are the risks of upgrading an operator and its CRDs?**  
   Controller and schema compatibility can change; fields may be defaulted, rejected, or converted, and database on-disk changes may make rollback unsafe. Review release notes and compatibility matrices, rehearse in staging, verify backup/restore, and define abort criteria.

5. **When would you choose an operator versus a managed database or an external database platform?**  
   Compare team expertise, on-call capacity, RPO/RTO, backup/restore evidence, upgrade requirements, security, compliance, cost, portability, and exit strategy. Choose the model the organization can actually operate and recover.

### 5.14 Sources and verification notes

The lesson was authored from the supplied prompt and technical knowledge. The manifests, commands, operator installation, switchover, failover, backup, and restore procedures **were not executed here**. The links below are official starting points but were not live-verified in this response. Treat every version-sensitive field as `[VERIFY]` before use.

#### Official sources

- CloudNativePG documentation: https://cloudnative-pg.io/documentation/
  - Verify current installation method, Kubernetes compatibility, Cluster API, generated resources, role/status fields, switchover/failover procedure, metrics, and operator upgrade guidance.
- CloudNativePG GitHub project/releases: https://github.com/cloudnative-pg/cloudnative-pg
  - Verify the selected release, release notes, CRD versions, source, security advisories, and compatibility information.
- PostgreSQL documentation: https://www.postgresql.org/docs/
  - Verify the exact PostgreSQL major version for WAL, physical backup, recovery targets, replication, upgrades, memory settings, and extension compatibility.
- Kubernetes custom resources: https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
  - Verify CRD/custom-resource API behavior.
- Kubernetes Secrets: https://kubernetes.io/docs/concepts/configuration/secret/
  - Verify Secret access and handling practices.
- Kubernetes NetworkPolicy: https://kubernetes.io/docs/concepts/services-networking/network-policies/
  - Verify NetworkPolicy behavior and CNI support in the target cluster.
- Kubernetes resource management: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
  - Verify requests/limits and resource enforcement behavior.
- kind documentation: https://kind.sigs.k8s.io/
  - Verify cluster creation, node image compatibility, and lifecycle commands.
- Strimzi documentation: https://strimzi.io/documentation/
  - Verify current installation, Kafka API version, KRaft, storage schema, broker rollout, and supported configuration.
- MinIO documentation: https://min.io/docs/
  - Verify current local deployment requirements, S3-compatible behavior, and storage/security configuration. Compatibility with a specific CloudNativePG backup plugin must be confirmed separately.

#### Required verification register

| Item | Exact check | Why it matters |
|---|---|---|
| Kubernetes/operator compatibility | Record `kubectl version`, operator release, and current official compatibility matrix | Prevent unsupported combinations and API mismatch |
| CRD/API schema | `kubectl get crd`; `kubectl explain <kind>`; server-side dry-run; official API reference | Avoid stale or invented fields |
| Generated Services/PDBs | Inspect live `svc`, EndpointSlices, PDBs, selectors, and current docs | Names and generated objects may differ by release/configuration |
| Operator install and upgrade | Current official install/upgrade guide and release notes | CRD/controller ordering and rollback constraints are version-sensitive |
| Backup architecture | Current official backup guide; plugin/in-tree status; compatibility matrix | Avoid relying on deprecated or unsupported backup paths |
| Scheduled backup | Confirm kind/API version, schedule fields, status semantics, and retention | Prevent invalid schedules and false confidence |
| PITR fields/timestamp | Current recovery API docs; exact timestamp format/timezone; server-side validation | A wrong field or timestamp can restore the wrong state or fail |
| Object-store support | Current plugin docs, endpoint/TLS support, required permissions, footprint | S3 API compatibility alone is not sufficient |
| Pooler, separate WAL volume, replication fields | Current API reference and supported configuration examples | These features/fields vary by release |
| Metrics and alerts | Current operator metrics docs; verify metric names in live endpoint | Avoid alerts on nonexistent or misunderstood signals |
| Strimzi/Kafka | Current API version, KRaft requirements, storage schema, release matrix | Broker APIs and quorum requirements evolve |
| Lab commands and cleanup | Run only in a disposable cluster; inspect resource inventory before deletion | Prevent accidental data loss and preserve evidence |

#### Cross-module boundaries

- **M05 Unit 1:** `01-volumes-persistentvolumes-and-persistentvolumeclaims.md` — PV/PVC and volume fundamentals.
- **M05 Unit 2:** `02-storageclasses-dynamic-provisioning-and-csi-drivers.md` — StorageClasses and CSI.
- **M05 Unit 3:** `03-volume-snapshots-cloning-and-expansion.md` — snapshots, cloning, expansion, and consistency limits.
- **M05 Unit 4:** `04-statefulset-storage-patterns-and-stable-identity.md` — StatefulSet identity, per-replica claims, rollout, and node-loss safety.
- **M05 Unit 6:** `06-storage-performance-iops-throughput-and-latency.md` — storage performance and capacity measurement.
- **M05 Unit 7:** `07-data-locality-zonal-failure-and-volume-affinity.md` — topology, locality, and failure domains.
- **M05 Unit 8:** `08-storage-troubleshooting-and-orphaned-volumes.md` — storage troubleshooting and orphaned volumes.
- **M01:** non-root images, UID/GID, `fsGroup`, and volume permissions.
- **M03:** StatefulSet/probes/PDB/RBAC/PSS and etcd backup. **etcd snapshots do not contain PV data.**
- **M04:** Services/DNS and NetworkPolicy for database namespaces.
- **M06:** Helm/Kustomize packaging; this lesson applies manifests directly except where a verified official Helm install is used.
- **M08:** GitOps handoff for operator configuration and custom resources.
- **M09:** Secrets, TLS, credentials, and encryption-key handling.
- **M10:** SLOs and incidents.
- **M11:** database/storage observability and metrics.
- **M12:** security.
- **M13:** backup/DR, immutability, offsite and cross-region recovery.
- **M14:** multi-cluster operations.
- **M15:** storage cost.

This unit teaches operator fundamentals, a CloudNativePG/PostgreSQL lifecycle lab, backup/PITR design and verification, broker awareness, incident runbooks, and operating-model selection. Deeper storage mechanics remain in M05 Units 1–4 and 6–8; GitOps, broad secret management, SLO governance, observability implementation, enterprise backup/DR, multi-cluster operations, and cost management are linked forward to their named modules.

#### Self-audit

- [x] Exact Unit 5 title, target filename, and section order 5.0–5.14.
- [x] Operator/CRD/custom-resource model, maturity progression, and three decision questions.
- [x] CloudNativePG three-instance lab, resource inspection, synthetic data, switchover and Pod-deletion failover steps.
- [x] Backup, WAL archiving, scheduled backup, PITR-to-new-cluster design, restore evidence, and explicit not-demonstrated path.
- [x] PostgreSQL upgrade, Pooler/PgBouncer, TLS, metrics, storage, memory, fencing, replication, and NetworkPolicy concepts.
- [x] Kafka/Strimzi and Redis/RabbitMQ/NATS awareness coverage.
- [x] Operator governance, CRD upgrade risk, blast radius, outage behavior, GitOps, game-day matrix, incident runbooks, and managed-database comparison.
- [x] Security/SRE lenses, production checklist, evidence artifacts, self-check rubric, and exactly five interview/design-review questions.
- [x] Cross-module links include the explicit note that etcd snapshots do not contain PV data.
- [ ] Current APIs, compatibility, manifest validation, backup/PITR, MinIO compatibility, and lab execution remain **[VERIFY]**; none are claimed as completed.
