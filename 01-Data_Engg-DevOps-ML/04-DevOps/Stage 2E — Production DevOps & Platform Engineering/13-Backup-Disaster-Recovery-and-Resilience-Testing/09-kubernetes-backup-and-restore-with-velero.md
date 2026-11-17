# Unit 9 — Kubernetes Backup and Restore with Velero

**Target:** `Stage 2E — Production DevOps & Platform Engineering/13-Backup-Disaster-Recovery-and-Resilience-Testing/09-kubernetes-backup-and-restore-with-velero.md`  
**Environment:** Linux/WSL2 Ubuntu, Docker/Podman, `kind`, `kubectl`, Python 3; about 4 CPU, 8 GB RAM and 30 GB free disk.  
**Budget:** zero-cost local labs with synthetic data only.

> **Safety/authenticity contract:** a Velero backup with phase `Completed` is not proof of recoverability. A restore of API objects is not proof that volume bytes or application state are correct. Version-sensitive commands, flags, annotations, CRDs, plugins, metrics and provider behavior are marked `[VERIFY]`. `[ASSUMPTION]` marks an assumption, `[ILLUSTRATIVE]` marks an example rather than a measurement, and `[AWARENESS]` marks optional topics. Every `kind` result is a **local lab observation**, not proof of independent-region recovery.

## 9.0 Why this matters in production

Kubernetes applications have distinct recovery domains:

1. **API objects:** Deployments, Services, ConfigMaps, Secrets, PVC definitions, RBAC, custom resources and selected cluster-scoped resources.
2. **Persistent-volume bytes:** files, database pages, checkpoints, queue segments, model files or pipeline state.
3. **Application-native state:** database backup chains, write-ahead logs (WAL), point-in-time recovery (PITR), queue replication, application checkpoints and consistency metadata.
4. **Declarative source of truth:** Git repositories, infrastructure-as-code, Helm values and GitOps definitions.
5. **External dependencies:** object stores, DNS, certificates, identity systems, encryption keys, registries, cloud resources and service endpoints.

Velero helps back up and restore Kubernetes resources and, with supported integrations and explicit configuration, persistent-volume data. It does not combine all five domains into one automatically consistent, portable, immutable and verified recovery point.

### Why `Completed` is insufficient

A controller can serialize API objects while a volume-data operation was not selected, skipped, unsupported or failed separately. The backup may contain a PVC object but no usable PVC bytes. A snapshot may remain tied to a particular storage system, cluster or region. Secrets may now be compromised. A restore may create objects while an operator, admission webhook, StorageClass mismatch, GitOps controller or missing image prevents the service from working.

The proof chain is:

`scope declared → backup created → volume method confirmed → contents inspected → restore executed → data checked → application checked → RTA/RPA recorded → evidence retained`

### Hypothetical incident

**[ILLUSTRATIVE]** A team sees `Completed` backups for months. After namespace deletion, it restores Deployments, Services, PVC definitions and ConfigMaps. Pods start, but application directories are empty because no supported volume-data method was configured or the PVC-mounted volume was not selected for file-system backup. The backup succeeded for the objects it captured; the team's assumption that it also captured bytes was wrong.

- **Detect:** stop treating the restored workload as healthy; compare known-answer records, checksums, database recovery metadata and backup inventory.
- **Contain:** stop writes to the incomplete restore, suspend CronJobs/consumers and avoid overwriting remaining source data.
- **Recover:** find an independent snapshot, file-system backup, native backup/PITR chain or replica. Restore in isolation and validate before cutover. If no usable copy exists, declare the data-loss boundary honestly.
- **Remediate:** configure a supported data method for each required volume and verify its operation records.
- **Prevent:** run restore drills that check bytes and application invariants; alert on uncovered PVCs; retain evidence beyond backup status.

This scenario is hypothetical, not a real incident report.

### Production implications and curriculum boundary

A snapshot is not automatically portable or independent. GitOps reconstructs declared configuration, not arbitrary runtime data. Velero does not replace native database backups/PITR, immutable independent copies or a tested recovery plan. Restore can reintroduce compromised Secrets/RBAC, re-run CronJobs, conflict with GitOps, or fail due to storage, CRD, operator, plugin or Kubernetes-version differences.

This unit owns Velero's role in Kubernetes resource/volume backup, installation, scope, restore, cross-cluster recovery, GitOps interactions, security and operations. M05 owns application-native database recovery/PITR. M13 Units 1–8 establish objectives, protection, platform/pipeline/model recovery, regional dependencies, restore evidence and failure-injection safety. Unit 10 owns dedicated chaos-engineering tools.

## 9.1 Learning objectives

By the end, the learner should be able to:

- Explain Velero's role and limits without confusing API-object capture with data recovery.
- Distinguish API backup, volume snapshots, file-system backup, snapshot data movement, native backup/PITR, GitOps rebuild and independent copies.
- Describe the server/CLI, Backup/Restore/Schedule, storage locations, plugins, node-agent and version-dependent data-movement components.
- Build a local Velero + MinIO lab using compatibility checks rather than guessed versions.
- Back up and restore a namespace and verify resources plus actual synthetic data.
- Compare FSB, CSI snapshots, provider-native snapshots and snapshot data movement.
- Use selectors, filters, TTL, schedules and hooks after checking release-specific syntax.
- Restore to another namespace and a second `kind` cluster, documenting shared-host limitations.
- Measure achieved recovery time (RTA) and achieved recovery point (RPA) against RTO/RPO.
- Plan around CRDs, operators, GitOps ownership, storage classes, identities and external dependencies.
- Prevent ETL replay and unsafe restoration of compromised Secrets/RBAC.
- Secure storage credentials, permissions, deletion paths and evidence.
- Monitor backup age, failures, coverage, BSL, node-agent and restore-test success.
- Run fallback and N−1 compatibility drills without risking the only known-good copy.
- Choose between Velero-centric, GitOps + native recovery, and layered designs using evidence.

## 9.2 Concept map and vocabulary

### What Velero is and is not

Velero is an open-source Kubernetes backup/restore project for API resources and, through supported integrations, persistent-volume data. **Current governance, maintenance status and supported releases must be checked before adoption** `[VERIFY]`; do not infer status from a `main`-branch tutorial.

Volume data may be protected through:

- **CSI snapshots:** Kubernetes Container Storage Interface snapshot APIs plus a compatible driver/controller/backend.
- **File-system backup (FSB):** Velero node-agent and supported file-system data path; current documentation describes Kopia integration, but verify release-specific behavior `[VERIFY]`.
- **Provider-native snapshots:** supported provider/plugin snapshot path.
- **CSI snapshot data movement:** where supported, copy snapshot data into object storage.

Velero does not automatically guarantee etcd backup, external cloud resources, node-local state, all bytes in every PVC, database consistency/PITR, encryption keys, GitOps source code or application recoverability.

### Vocabulary

| Term | Meaning | Operational question |
|---|---|---|
| `Backup` | Custom resource describing a backup request/status | What was included and which volume methods ran? |
| `Restore` | Request to recreate selected objects/data | What was restored, skipped, failed or mapped? |
| `Schedule` | Recurring backup definition | Did it produce fresh, restorable backups? |
| BSL | BackupStorageLocation; object-store configuration | Can the cluster read/write the expected bucket? |
| VSL | VolumeSnapshotLocation; snapshot-provider configuration where used | Which snapshot backend is configured? |
| `PodVolumeBackup` / `PodVolumeRestore` | Version-dependent FSB operation resources | Did volume bytes complete separately from the main phase? `[VERIFY]` |
| `BackupRepository` | Version-dependent file-system repository resource | Is repository access/maintenance healthy? `[VERIFY]` |
| `DataUpload` / `DataDownload` | Version-dependent data-movement resources | Did transfer actually finish? `[VERIFY]` |
| CRD | CustomResourceDefinition extending the Kubernetes API | Are extensions installed before custom resources? |
| RTO/RPO | Recovery time / recovery point objective | What outage and data-loss window is allowed? |
| RTA/RPA | Achieved recovery time / achieved recovery point | What did a verified drill actually achieve? |
| Crash-consistent | Storage point without guaranteed app coordination | Can the app recover using its own protocol? |
| Application-consistent | Recovery coordinated with application procedure | What proves the transaction boundary is valid? |
| Independent copy | Copy protected from source failure modes | Can source credentials delete this copy too? |

### Architecture

```text
Operator / CI / runbook
       | creates Backup/Restore/Schedule
       v
  velero CLI ---> Kubernetes API <--- Velero server Deployment
                                      |             |
                                      v             v
                                API objects   volume integration
                                              /      |       \
                                       CSI snapshot node-agent provider plugin
                                              \      |       /
                                               BSL/object store
                                                      |
                                      independent copy only if configured
```

Object storage holds backup metadata and data produced by the selected method. A CSI snapshot may remain in a provider's snapshot system unless data movement or another portable copy path is configured. Components/CRDs vary by release and enabled features.

### Compatibility matrix

Fill this before installation and upgrades; only call a combination compatible when official release notes/provider docs support the exact tuple.

| Dimension | Record | Evidence |
|---|---|---|
| Velero CLI/server | `<VERSION>` | `velero version`, image tag, release notes |
| Kubernetes | `<VERSION>` | `kubectl version`, provider matrix |
| Object-store plugin | exact image and tag | official plugin release notes |
| CSI integration | built-in/plugin state | official CSI docs, installed CRDs |
| Node-agent/FSB | image, enabled state, method | install and FSB docs |
| Data mover | enabled state and requirements | official data-movement docs/CRDs |
| Storage driver | name/version/snapshot support | driver docs and snapshot CRDs |
| Backup storage | endpoint, region/path-style, versioning/immutability | provider docs, redacted config |
| API extensions | installed CRD names/versions | `kubectl get crd`, release docs |

Preflight:

```bash
kubectl config current-context
kubectl version
kubectl get nodes -o wide
velero version
velero install --help
velero backup create --help
velero restore create --help
kubectl get crd | grep -E 'velero.io|snapshot.storage.k8s.io' || true
```

If the CLI is not installed, verify the downloaded release/checksum on its official release page. Do not copy `/docs/main/` commands into a pinned environment without checking versioned docs.

### Decision matrix

| Method | Protects | Consistency | Portability/speed | Failure modes | Required test |
|---|---|---|---|---|---|
| Velero API backup | Selected Kubernetes objects | API-object, not app transaction consistency | Often fast; target API differences matter | scope/CRDs/RBAC/partial restore | isolated restore and content inventory |
| GitOps rebuild | Declared configuration | Configuration only, not runtime bytes | Portable if source/dependencies are available | missing secrets/images/external resources/drift | clean-cluster reconcile and functional check |
| Native backup/PITR | Application-defined data/log chain | Can be app-aware when configured correctly | Depends on dataset/replay and engine | missing WAL/base backup/wrong timeline | native restore and integrity query |
| CSI snapshot | Volume state | Often crash-consistent without coordination | Backend/driver/region dependent; creation can be fast | snapshot backend/driver unavailable | restore with target driver; validate app |
| FSB | Files in mounted pod volumes | File-level; not automatically app-consistent | Potentially portable via object storage; scan/upload cost | missing selection, node-agent, unsupported mount | operation evidence + checksums |
| Snapshot data movement | Snapshot data copied to object storage | Inherits snapshot consistency | More portable if supported; adds transfer time | feature/plugin/repository failure | restore from copy to supported target |
| Provider snapshot | Provider-managed volume | Provider semantics; not automatically app-consistent | Provider/account/region bound unless copied | provider API/permission/account loss | target account/region restore |
| Independent immutable copy | Copied layer | Inherits source consistency | Depends on format/target; replication lag | shared credentials, lifecycle/key loss | deletion-resistance and restore test |

**Layering principle:** GitOps for declarative configuration; native backup for databases/queues/PITR; Velero for selected Kubernetes resources, namespace capture/migration and supported PVC data; independent protected copies for deletion/compromise resilience. Avoid dual ownership and a single-tool dependency for tier-0 data.

## 9.3 Level 1 — Beginner

### Local topology and preflight

```text
Laptop/WSL2 (one failure domain)
  kind cluster: velero-lab
    namespace velero ---> MinIO S3-compatible endpoint
    namespace app-lab ---> Deployment + PVC + synthetic marker
```

1. Check at least 30 GB free disk and record `kind version`, `kubectl version`, container runtime and Velero release.
2. Check official versioned Velero install docs and the object-store plugin release notes. Pin exact tags; plugin compatibility is `[VERIFY]` until confirmed.
3. Use fake credentials and synthetic data only. Do not paste secrets into Markdown, shell history or evidence.
4. If a feature is unavailable, record `NOT RUN — unsupported` and document the fidelity gap.

`versions.txt` template:

```text
observed_at_utc=<YYYY-MM-DDTHH:MM:SSZ>
os=<distribution/version>
container_runtime=<Docker/Podman version>
kind=<version>
kubectl=<client/server versions>
velero_cli=<VERSION>
velero_server=<VERSION or not installed>
object_store_plugin=<image:tag>
node_agent=<image:tag or not enabled>
snapshot_crds=<versions or absent>
storage_driver=<name/version or not applicable>
source_urls=<official sources checked>
compatibility_decision=<verified/blocked/pending>
notes=<limitations>
```

### MinIO and Velero installation

The official MinIO evaluation guide uses an AWS-compatible plugin pattern and `s3ForcePathStyle=true`; its example tag is not a universal compatibility promise `[VERIFY]`. Confirm endpoint, bucket and plugin tag first. Create a fake credentials file with restrictive permissions:

```bash
umask 077
cat > credentials-velero <<'EOF'
[default]
aws_access_key_id = lab-access-key
aws_secret_access_key = lab-only-not-a-real-secret
EOF
chmod 600 credentials-velero
```

**Never reuse these fake values outside the lab.** For production, use supported identity, least privilege and secret-management processes.

Typical version-sensitive command shape; replace placeholders only after checking official docs:

```bash
# [VERIFY] Plugin image/tag must match the selected Velero release.
velero install \
  --provider aws \
  --plugins <PLUGIN_IMAGE:TAG> \
  --bucket velero \
  --secret-file ./credentials-velero \
  --backup-location-config region=minio,s3ForcePathStyle="true",s3Url=http://minio.velero.svc:9000 \
  --use-volume-snapshots=false \
  --wait
```

Assumptions: MinIO is reachable at `minio.velero.svc:9000` from Velero and bucket `velero` exists. A local MinIO deployment may use ephemeral storage. This simple object-resource lab disables snapshots. FSB requires supported node-agent setup and is not assumed enabled by default.

```bash
kubectl --context kind-velero-lab -n velero get deploy,ds,pods
kubectl --context kind-velero-lab -n velero get backupstoragelocations
velero version
velero backup-location get
```

If the credential Secret name differs, inspect generated manifests and docs. Never dump Secret YAML in evidence.

### Synthetic application manifest

Check StorageClasses before applying. The image/command is a lightweight example; verify logs and readiness.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: app-lab
  labels:
    purpose: velero-training
    data-class: synthetic
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: sample-data
  namespace: app-lab
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 1Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-web
  namespace: app-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sample-web
  template:
    metadata:
      labels:
        app: sample-web
      annotations:
        backup.velero.io/backup-volumes: data
    spec:
      containers:
      - name: web
        image: busybox:1.36
        command: ["sh", "-c"]
        args:
        - |
          mkdir -p /data
          printf 'velero-lab-record-v1\n' > /data/known-answer.txt
          sha256sum /data/known-answer.txt > /data/known-answer.sha256
          httpd -f -p 8080 -h /data
        ports:
        - name: http
          containerPort: 8080
        volumeMounts:
        - name: data
          mountPath: /data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: sample-data
```

The annotation matters only when FSB is installed/supported; it does not prove data was captured. Apply and record source checksum:

```bash
kubectl --context kind-velero-lab apply -f app-lab.yaml
kubectl --context kind-velero-lab -n app-lab rollout status deploy/sample-web --timeout=120s
kubectl --context kind-velero-lab -n app-lab get pvc,pods
kubectl --context kind-velero-lab -n app-lab exec deploy/sample-web -- sha256sum /data/known-answer.txt
kubectl --context kind-velero-lab -n app-lab exec deploy/sample-web -- cat /data/known-answer.txt
```

Fix a failed source check before backup; otherwise the test is invalid.

### Backup, inspect and restore

Confirm flags with installed CLI help `[VERIFY]`:

```bash
velero backup create app-lab-before-test --include-namespaces app-lab --ttl 168h
velero backup describe app-lab-before-test --details
velero backup logs app-lab-before-test
velero backup get
```

Inspect included objects. If data was expected, confirm its method: FSB operation resources/logs; CSI snapshot section and provider-side snapshot; or supported data-movement records. CRDs/fields vary by release `[VERIFY]`.

```bash
velero restore create app-lab-restore-01 \
  --from-backup app-lab-before-test \
  --namespace-mappings app-lab:app-lab-restore
velero restore describe app-lab-restore-01 --details
velero restore logs app-lab-restore-01
kubectl --context kind-velero-lab -n app-lab-restore get deploy,pods,pvc
kubectl --context kind-velero-lab -n app-lab-restore rollout status deploy/sample-web --timeout=120s
kubectl --context kind-velero-lab -n app-lab-restore exec deploy/sample-web -- sha256sum /data/known-answer.txt
kubectl --context kind-velero-lab -n app-lab-restore exec deploy/sample-web -- cat /data/known-answer.txt
```

Namespace mapping/PVC references may need release-appropriate adjustments. Compare restored checksum with source. If PVC is empty, resource restoration may have succeeded while volume restoration did not. Diagnose rather than blindly repeating destructive operations.

Inspect object storage using a supported MinIO/provider CLI `[VERIFY]`; object names are not assumed stable across releases. Do not edit repository objects by hand.

### RTA/RPA measurement

Record UTC timestamps: `t0` drill starts; `t1` restore accepted; `t2` resources and volume bytes available; `t3` application checks pass; `t4` cutover approved. **RTA** = `t4 - t0`. **RPA** = gap between loss point and newest verified recoverable application point. A single marker does not yield precise RPA. This is a local lab observation, not regional independence, production throughput, database consistency or compliance evidence.

## 9.4 Level 2 — Intermediate

### Backup scope, filters and volume inclusion

Namespace selection controls objects; it does not guarantee PVC bytes. Release-sensitive options include `--include-namespaces`, `--exclude-namespaces`, resource include/exclude filters, label selectors, `--include-cluster-resources`, `--snapshot-volumes`, `--default-volumes-to-fs-backup`, pod annotation `backup.velero.io/backup-volumes`, TTL and Schedule resources. Confirm spelling/defaults/interactions against installed release `[VERIFY]`.

```bash
# [VERIFY] Confirm options with velero backup create --help first.
velero backup create payments-config-daily \
  --include-namespaces payments \
  --selector 'backup-tier=application' \
  --ttl 720h
```

Selectors can drift as labels change; cluster-scoped resources can affect other workloads. Use an inventory and coverage audit, not a selector alone.

### Schedules, TTL and tiers

| Tier | Policy intent | Required verification |
|---|---|---|
| Tier 0 | Native backup/PITR + selected Kubernetes resources + independent protected copy | database/service restore, RTA/RPA, alternate-copy access |
| Tier 1 | Frequent native data backup + resources + tested volume method | verified age, volume coverage and restore drill |
| Tier 2 | Frequency matched to loss tolerance | coverage, retention and restore evidence |
| Rebuildable stateless | GitOps-first; Velero only for justified unmanaged resources | clean-cluster rebuild without hidden state |

A Schedule is intent, not proof of fresh restorable backups. Define frequency, TTL, lifecycle retention, data method, consistency, maximum verified age, test cadence, owner and evidence location. `[ILLUSTRATIVE]` For a 24-hour RPO, alert before the newest *verified recoverable* point reaches 24 hours old; API-object backup time may not qualify.

### Hooks and consistency

Hook syntax such as `pre.hook.backup.velero.io/command`, container, timeout and `onError` is `[VERIFY]` for the selected release. Hooks may request a checkpoint or pause a writer, but can fail, time out, run in the wrong container or fail to coordinate other writers/PVCs. File-system freeze is not automatically database consistency. Multiple PVCs (data and WAL) may need coordinated snapshots or native recovery `[VERIFY]`.

**[ASSUMPTION]** Production databases should default to application-native/operator-managed backup/PITR unless a tested design proves another method satisfies consistency and objectives. Use M05 for PostgreSQL and CloudNativePG.

### Restore options, order and pitfalls

Plan source backup, target context, namespace mapping, filters, existing-resource policy, volume restore mode, CRD/operator prerequisites and external dependencies before restore. Namespace mapping, `none`/`update` existing-resource policy, NodePort preservation, PV settings, restore hooks and custom ordering are release-dependent `[VERIFY]`. Dry-run does not validate every webhook, volume byte, provider API or application dependency.

A partial restore is not a healthy service. Inspect `velero restore describe --details`, logs, events and volume-operation resources. Plan for:

- LoadBalancer IPs, NodePorts, Ingress, DNS and TLS not being portable.
- StorageClass, access mode, capacity and PVC binding differences.
- CRDs/operators/webhooks/finalizers/owner references/UID differences.
- Pods normally recreated by controllers; status subresources and HPA/replica state may differ.
- Cluster-scoped resource conflicts and non-portable ServiceAccount identity.
- CronJob/Job replay and compromised Secrets/RBAC.

### Volume methods compared

| Method | Consistency | Portability | Overhead/failure mode | Must verify |
|---|---|---|---|---|
| CSI snapshot | Often crash-consistent without app coordination | Driver/backend/region dependent | Snapshot may disappear with provider/account | snapshot exists, target driver can restore, data/app check |
| File-system backup | File-level; not automatically app-consistent | Potentially portable through object storage | CPU/I/O, file scan, node-agent/repository issues | volume selected, operation completed, checksum matches |
| Snapshot data movement | Inherits snapshot consistency | Can improve portability when supported | transfer/data mover add complexity | feature support, upload/download completion, cross-cluster test |
| Provider-native snapshot | Provider semantics; app consistency separate | Often provider/account/region bound | API/permission/quota dependency | target account/region restore |

A `kind` hostpath snapshot on the node is not a portable DR copy; node/host loss may lose both source and snapshot. If CSI/data movement is unavailable, mark it not run and use a documented FSB/object-store fallback.

Schedule YAML shape only—verify schema/API version and fields first:

```yaml
# [VERIFY] Policy sketch, not a universal copy/paste contract.
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: app-lab-hourly
  namespace: velero
spec:
  schedule: "0 * * * *"
  template:
    includedNamespaces: ["app-lab"]
    ttl: 168h
```

Confirm it creates a Backup, then inspect scope, volume evidence, age and restoreability.

## 9.5 Level 3 — Advanced

### Cross-cluster restore

A second `kind` cluster exercises workflow only; it shares the laptop's CPU, disk, network and power failure domains.

```text
Laptop (shared failure domain)
 kind primary ---> MinIO lab bucket <--- kind DR
     source        (possibly same host)   restore target
```

Safe sequence: prepare the DR cluster; record Kubernetes/Velero/plugin/storage versions; install CRDs/operators first; configure a readable BSL (prefer read-only DR credentials if supported `[VERIFY]`); inspect backup contents; restore into an isolated namespace; configure target StorageClass mapping through the supported release mechanism `[VERIFY]`; verify volume bytes, application invariants, images, network/DNS/identity; measure RTA/RPA; only then document controlled cutover. CSI snapshots alone are usually tied to a backend/cluster/region. Cross-cluster DR needs a tested portable copy such as FSB to object storage, supported snapshot data movement or a replicated provider snapshot `[VERIFY]`.

### GitOps ownership conflict

GitOps reconstructs declared configuration; Velero restores selected point-in-time objects/data. If both own the same object, reconciliation can overwrite or prune recovered state.

1. Map ownership per resource (GitOps, Velero, operator, cloud controller or emergency-only).
2. Pause/constrain auto-sync/prune only through the documented approved procedure `[VERIFY]`.
3. Restore in isolation where possible.
4. Restore only resources/data designated for Velero; let GitOps rebuild declared configuration.
5. Inspect tracking labels/annotations, owner references and diffs.
6. Hand ownership back deliberately, resume reconciliation and verify convergence.

Argo CD and Flux behaviors vary. Evidence should include pre-restore desired state, restore logs, controller events/diffs and final ownership decision.

### Operators and custom resources

CRDs and relevant operators/webhooks must be ready before custom resources. Operators may reconcile child resources or reject fields that differ across versions; UIDs, owner references, finalizers and status complicate recovery. **CloudNativePG warning:** restoring a `Cluster` CR plus PVCs through Velero is generally not the recommended recovery path. Use the operator's native backup/bootstrap/recovery workflow from M05 and verify current guidance `[VERIFY]`.

### Consistency, load and performance

- A crash-consistent point may require application recovery logs/checkpoints; one file checksum does not prove database integrity.
- A PVC copy without required WAL/base-backup chain may not provide the desired PITR point.
- Multiple PVC snapshots may represent different moments; group-snapshot semantics are platform-dependent `[VERIFY]`.
- Hooks coordinate only commands actually run; check exit code, timeout, `onError` and every writer.
- Node-agent/FSB consumes CPU, memory, disk I/O and network. File enumeration and deduplication scans can dominate runtime, especially with many small files.
- Stagger schedules and observe API/storage saturation. Parallel upload/throttling options are version-dependent `[VERIFY]`.
- Investigate unexplained size drops and duration spikes; they may indicate missing data or failure, not optimization.

### Security and restore safety

Backups can contain Kubernetes Secrets; base64 is encoding, not encryption. Treat metadata, object contents, repository keys and logs as sensitive.

- Encrypt object storage in transit/at rest; control key custody and test key recovery.
- Separate backup writer, restore reader and deletion administrator identities where practical. Restrict workload identity from deleting backups.
- Apply least-privilege Kubernetes RBAC/admission controls to `Backup`, `Restore`, `Schedule` and deletion requests. Arbitrary restore creation can reintroduce privileged objects or unsafe workloads.
- Protect BSL/VSL credentials. Avoid broad cloud credentials with backup deletion authority stored in the same cluster where alternatives exist.
- Use versioning/immutability/object lock and independent copies where supported; verify provider semantics and retention `[VERIFY]`.
- Verify repository encryption/key behavior for the installed release `[VERIFY]`; do not assume it protects data from every object-store reader.
- Restore in isolation; avoid overwriting existing resources. Existing-resource policy values such as `none` are version-dependent `[VERIFY]`.
- Rotate/reissue credentials after compromise; review Secrets/RBAC before enabling workloads.
- Treat hooks as executable code; restrict who can change them and avoid shell interpolation of untrusted input.
- Do not casually disable admission/webhooks. Any temporary change must be lab-only or approved, time-bounded, reversible and verified.
- Suspend/exclude CronJobs and side-effect workloads until replay safety is established `[VERIFY]`.
- Redact credentials and Secret values from logs/evidence.

### Multi-cluster, versions and failure modes

A robust design includes a tested BSL read path, replicated/independent copies, target prerequisites, a compatibility matrix and restore tests. A shared bucket is not independent if both cluster identities can delete it; replication lag contributes to RPA.

Maintain versions for Velero CLI/server, Kubernetes, plugins, CRDs, node-agent/data mover and storage method. Test N−1 recovery before upgrades. After upgrades, verify fresh backups and restores; a Schedule object that still exists does not prove it produces backups.

Failure modes include BSL outage/expired credentials, partial backups, `PodVolumeBackup` failures, missing node-agent, plugin mismatch, repository maintenance/corruption `[VERIFY]`, StorageClass mismatch, retention deleting needed points, CRD changes and replication lag.

**[AWARENESS]** Alternatives include application-native backup + GitOps + CSI/FSB, Kasten K10, Stash/Trilio and cloud-native backup services. Compare current support, consistency, multi-cluster recovery, evidence, cost, lock-in and exit path. No universal winner; verify maintenance and feature support.

## 9.6 Level 4 — Expert

### Policy as code and coverage audit

Define a service tier register with namespace, owner, RTO/RPO, native recovery, resource policy, volume method, retention, immutability, newest verified recovery point, restore-test cadence and runbook. Do not let an undocumented pod annotation be the only protection for a critical PVC.

```csv
service,namespace,tier,rto_minutes,rpo_minutes,owner,resource_backup,volume_method,native_recovery,restore_test_days
synthetic-web,app-lab,3,120,1440,platform-training,velero,fsb-if-supported,not-applicable,30
synthetic-db,db-lab,0,30,5,data-platform,velero-selected,operator-native,postgresql-pitr,7
```

These are illustrative training values, not universal objectives. A meaningful audit asks: which namespaces/PVCs are required; which enabled schedule covers them; did a recent backup complete; did the volume method complete; is it portable to DR; and has a layered restore test passed?

The following audit accepts a normalized JSON inventory produced by a reviewed read-only exporter. It deliberately does not guess release-specific raw Velero fields. It exits non-zero for missing coverage and does not read Secret values.

```python
#!/usr/bin/env python3
"""Audit a normalized Velero coverage inventory; synthetic/example input only."""
import json, sys
from pathlib import Path
REQUIRED = {"namespaces", "schedules", "pvcs", "backup_methods"}

def main(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = REQUIRED - data.keys()
    if missing:
        raise ValueError(f"missing top-level keys: {sorted(missing)}")
    failures, rows = [], []
    for ns in data["namespaces"]:
        name = ns["name"]
        required = bool(ns.get("backup_required", True))
        schedules = [s for s in data["schedules"] if name in s.get("namespaces", []) and s.get("enabled")]
        if required and not schedules:
            failures.append(f"namespace {name}: no enabled covering schedule")
        for pvc in (p for p in data["pvcs"] if p["namespace"] == name):
            m = data["backup_methods"].get(f"{name}/{pvc['name']}", {})
            valid = m.get("method") in {"fsb", "csi-snapshot", "snapshot-data-movement", "provider-snapshot", "application-native"}
            complete = m.get("last_operation") == "Completed"
            if required and not (valid and complete):
                failures.append(f"PVC {name}/{pvc['name']}: no verified completed data method")
            rows.append({"namespace": name, "pvc": pvc["name"], "method": m.get("method", "missing"),
                         "completed": complete, "portable_to_target": m.get("portable_to_target") is True})
    print(json.dumps({"status": "FAIL" if failures else "PASS", "pvc_rows": rows, "findings": failures}, indent=2))
    return 1 if failures else 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} normalized-inventory.json", file=sys.stderr); raise SystemExit(2)
    try: raise SystemExit(main(sys.argv[1]))
    except (OSError, json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
        print(f"audit input error: {e}", file=sys.stderr); raise SystemExit(2)
```

The exporter must be version-specific and tested against real installed CRDs; this skeleton alone does not prove live coverage.

### Metrics and alerts

Exact Velero metric names/labels vary by release/configuration `[VERIFY]`. Example names sometimes cited (`velero_backup_success_total`, `velero_backup_last_successful_timestamp`, `velero_backup_failure_total`) must be confirmed against the actual metrics endpoint/docs; do not deploy rules against guessed names.

| Signal | Definition/unit | Source | Target/alert | Owner/caveat |
|---|---|---|---|---|
| Verified backup age | seconds since newest valid recovery point | backup + volume evidence | age approaches/exceeds tier RPO | service owner; API success alone may not qualify |
| Failure rate | failed required operations/count or rate | metrics/logs normalized by exporter | repeated failures or missed deadline | platform; metric names `[VERIFY]` |
| Duration/size | seconds/bytes and trend | backup metadata + object inventory | window breach or unexplained drop/spike | platform/data owner; compression changes size |
| BSL health | read/write test or availability | location status + synthetic canary | unavailable/auth failure | platform/security; status-only may be insufficient |
| PVC coverage | covered required PVCs / required PVCs | coverage audit | any critical PVC uncovered | workload owner; selectors drift |
| Node-agent health | ready/desired + operation errors | DaemonSet and volume CRs | missing agent/repeated errors | platform; health does not prove coverage |
| Restore-test pass rate | layered passing tests / scheduled tests | evidence registry | missed/failed test | SRE + service owner |
| RTA/RPA | observed recovery duration/point gap | drill timeline + data checks | objective breach | service owner; state measurement boundary |

Rule file uses **organization-owned normalized metrics**, not assumed Velero metrics. `backup_last_verified_success_timestamp_seconds` must mean a backup passed data-method checks; `backup_required_namespace_uncovered` is 1 for an uncovered namespace.

```yaml
# backup-alerts.yml; run: promtool check rules backup-alerts.yml
# Metric producer semantics must be documented and tested.
groups:
- name: backup-recovery
  rules:
  - alert: RequiredBackupTooOld
    expr: (time() - backup_last_verified_success_timestamp_seconds) > backup_rpo_budget_seconds
    for: 5m
    labels: {severity: critical}
    annotations:
      summary: "Verified recovery point is older than configured RPO budget"
      description: "Inspect backup, volume-method and object-store evidence for {{ $labels.namespace }}."
  - alert: RequiredBackupFailed
    expr: increase(backup_verified_failure_total[30m]) > 0
    for: 1m
    labels: {severity: warning}
    annotations:
      summary: "A required backup operation failed"
      description: "Inspect normalized failure event and Velero logs for {{ $labels.namespace }}."
  - alert: NamespaceBackupCoverageMissing
    expr: backup_required_namespace_uncovered == 1
    for: 5m
    labels: {severity: critical}
    annotations:
      summary: "Required namespace has no verified backup coverage"
      description: "Check tier register, selectors, PVC method and owner for {{ $labels.namespace }}."
```

Durations are illustrative. Match the Prometheus tooling version, run `promtool check rules`, then test firing and clearing with controlled fixtures; syntax validation alone is not behavior validation.

### Runbooks and full-stack rehearsal

Runbooks must identify severity/owner, safe preflight, containment, diagnosis, recovery options, verification, abort/rollback, evidence, communication and follow-up. Cover stale/failed backups, BSL outage/credential rotation, partial restore/missing bytes, cross-cluster StorageClass mismatch, upgrades, repository maintenance `[VERIFY]`, GitOps conflict, compromised restored Secret, CronJob replay and failed restore tests.

Full rehearsal order: declare synthetic incident and `t0`; select target with fail-closed guard; prepare CRDs/operators; verify BSL/copy and inspect contents; restore selected Velero resources/portable data in isolation; use native DB/queue recovery; let GitOps rebuild configuration without dual ownership; hold CronJobs/consumers; run integrity, authorization, network and functional checks; record timeline/RTA/RPA/deviations; approve/reject cutover by explicit criteria; clean up and verify.

### Nine organizational failure scenarios

Use **symptom → cause → containment → corrective action → prevention → evidence of fix**.

| Scenario | Response pattern |
|---|---|
| `Completed`, PVC bytes missing | Empty app data → method absent/unselected; stop writes; recover from native/independent copy; configure method and coverage audit; prove volume operation + checksum + app test. |
| CronJob reruns ETL | duplicate output → schedule active on restore; suspend/block side effects; deduplicate safely; add idempotency and restore hold; prove Job history/marker. |
| Argo CD prunes restore | objects disappear → desired state excludes them; control sync; assign ownership and reconcile deliberately; test isolated restore; retain diffs/events. |
| BSL credential is cluster-admin-like | workload can delete backups → overpowered shared identity; revoke/rotate; separate writer/reader/deleter; immutability and audit; prove denied delete + role review. |
| Compromised Secret restored | old token active → blind Secret restore; isolate/revoke; rotate and validate dependencies; add post-compromise hygiene; old token fails/new identity works. |
| Node-local snapshot called DR | lost with node/region → shared failure domain; declare gap; create portable independent copy; audit failure domains; restore from distinct copy. |
| Upgrade stops schedules | Schedule exists but no fresh Backup → CRD/API mismatch; halt rollout/preserve copies; follow rollback docs and repair schedule; N−1 gate; prove fresh backup+restore. |
| DR StorageClass differs | PVC Pending → storage mismatch; isolate; supported mapping/provisioner; target matrix; prove PVC bound and checksum matches. |
| Crash-consistent DB copy corrupt | integrity failure → no app coordination/WAL; stop writes; use native PITR/operator flow; test app consistency; retain recovery logs and integrity queries. |

### Scaling, governance and exit

At scale evaluate namespace/PVC count, API load, concurrency, object-store requests, bytes/file count, backup window, restore throughput, quotas and on-call load. Stagger schedules and test representative workloads. Parallel upload, concurrency, repository maintenance and throttling are `[VERIFY]`.

Exit strategy covers data export, repository/plugin dependencies, encryption-key custody, restore without the original cluster, alternate readers, costs/contracts and migration rehearsal. Keep old copies until the replacement passes a restore test. A laptop lab is not compliance proof.

## 9.7 SRE lens

SRE treats recovery as a measurable service capability. Define objectives by tier, measure achieved results and alert on loss of recoverability—not just failed commands.

- **RTO:** maximum acceptable service outage.
- **RPO:** maximum acceptable data-loss interval relative to a defined recovery point.
- **RTA:** elapsed time from the agreed incident start to a verified recovery milestone.
- **RPA:** gap between the incident/loss point and newest verified recoverable application point.

State the measurement boundary. If timing stops when Kubernetes objects exist, that is not end-to-end application RTA. If only a marker file is restored, it does not provide precise database RPA.

| Metric | Definition/unit | Source | Target/alert | Owner/caveat |
|---|---|---|---|---|
| Verified backup age | seconds since newest valid recovery point | backup + volume evidence | approaches/exceeds tier RPO | service owner; API success alone may not qualify |
| Failure rate | failed required operations/count or rate | metrics/logs normalized by exporter | repeated failure or missed deadline | platform; raw metric names `[VERIFY]` |
| Duration/size | seconds/bytes and trend | backup metadata + object inventory | window breach or unexplained drop/spike | platform/data owner; compression changes size |
| BSL health | read/write test or availability | location status + synthetic canary | unavailable/auth failure | platform/security; status-only may be insufficient |
| PVC coverage | covered required PVCs / required PVCs | coverage audit | any critical PVC uncovered | workload owner; selectors drift |
| Node-agent health | ready/desired + operation errors | DaemonSet and volume CRs | missing agent/repeated errors | platform; health alone does not prove coverage |
| Restore-test pass rate | layered passing tests / scheduled tests | evidence registry | missed/failed test | SRE + service owner |
| RTA/RPA | observed recovery duration/point gap | drill timeline + data checks | objective breach | service owner; state measurement boundary |

Principles: alert on unprotected namespaces/PVCs, stale verified points, volume failures, BSL problems and failed restore tests; monitor API/storage saturation; classify partial failures by resource, volume, application, dependency and policy; assign runbook ownership; and choose performance/cost trade-offs using measured recovery behavior.

## 9.8 Security lens

Backup content can include application data, Secrets, identity configuration, RBAC, endpoints and executable hooks. Protect it at least as carefully as the source.

1. Encrypt in transit/at rest, restrict bucket/prefix access and use versioning/immutability or object lock where supported. Keep an independent copy with separate deletion rights.
2. Separate writer, restore reader and deletion administrator identities where practical; rotate BSL credentials safely; document key custody and test key recovery.
3. Apply least-privilege Kubernetes RBAC/admission controls to `Backup`, `Restore`, `Schedule` and deletion requests. Arbitrary Restore creation may reintroduce privileged objects.
4. Test workload credentials cannot delete backups. Kubernetes RBAC and object-store IAM are separate controls.
5. Restore into isolation; inspect content; avoid overwriting existing resources; review RBAC, service accounts, webhooks, finalizers and owner references.
6. After compromise, revoke/rotate credentials; do not blindly restore old Secrets/certificates/tokens.
7. Treat hooks as executable code; restrict writers and avoid shell interpolation of untrusted input.
8. Audit who backed up/restored/deleted what. Redact credentials and Secret values from logs/evidence.
9. Fail closed on unknown context, namespace, bucket or backup ID. Never use unscoped deletion for cleanup.
10. Delete only lab clusters/buckets/fake credentials after retaining redacted evidence; verify cleanup.

Do not casually weaken production admission/webhooks/RBAC/encryption. Temporary policy changes must be lab-only or explicitly approved, time-bounded, reversible and verified.

## 9.9 Production checklist

Every item needs observable proof, a test or a named owner.

- [ ] **Scope/coverage:** inventory namespaces, cluster resources, PVCs and exclusions; retain coverage report and owner sign-off.
- [ ] **Volume method:** record method per PVC, portability limits and completed operation/snapshot evidence.
- [ ] **BSL/VSL:** test object-store and snapshot-provider access; retain redacted status/configuration and restore-read check.
- [ ] **Compatibility:** record Velero, Kubernetes, plugin, CRD, node-agent/data-mover and driver versions with official checks.
- [ ] **Consistency:** document crash/app consistency and native backup/PITR decision; retain application recovery test.
- [ ] **Schedule/TTL/retention:** map to tier register and prove fresh backups; check lifecycle/immutability interaction.
- [ ] **Hooks:** review syntax, command, timeout, error policy and failure behavior; retain negative test or rationale for none.
- [ ] **Restore target:** exact context/namespace guards and isolated restore plan.
- [ ] **CRDs/operators:** readiness before custom resources; retain readiness/log evidence.
- [ ] **GitOps:** ownership and auto-sync/prune plan; retain diffs/events and handoff proof.
- [ ] **CronJobs/Jobs:** suspend/exclude or prove idempotency; retain replay-prevention evidence.
- [ ] **Secrets/RBAC:** review restored identities and rotate compromised credentials; retain redacted authorization results.
- [ ] **RTA/RPA:** time full restore through application checks; retain timeline and hashes/queries.
- [ ] **Cross-cluster:** validate images, network, DNS, identity, StorageClasses, quotas and portable data method.
- [ ] **Alerts:** test backup age, failures, BSL, node-agent and uncovered-namespace alerts; retain rule/firing evidence.
- [ ] **Restore cadence:** assign tier-based frequency and retain layered test evidence.
- [ ] **Immutability:** test workload cannot delete protected copy; document encryption and independent failure domain.
- [ ] **Fallback/N−1:** restore from earlier known-good copy and test compatibility matrix.
- [ ] **Upgrade/exit:** stage upgrades, test CRDs/schedules, preserve old copies and rehearse exit.
- [ ] **Cleanup/operations:** remove throwaway resources, control restored jobs, revoke fake credentials and hand ownership back.

## 9.10 Hands-on lab set

**Safety contract for all labs:** synthetic data only; never production credentials/customer data/production clusters. Destructive commands must target named throwaway contexts, namespaces and buckets; preserve a known-good copy; stop on mismatch. A second `kind` cluster on one laptop is not a separate region. Version-sensitive commands are `[VERIFY]`.

### Lab 1 — Install Velero with MinIO and perform first backup/restore

**Creates/changes/deletes:** a throwaway `kind-velero-lab`, MinIO lab endpoint/bucket, Velero resources and synthetic `app-lab`. Never target a non-lab context or real bucket. Does not simulate independent storage or region loss.

**Goal/outcomes:** version-match CLI/server/plugin; backup and inspect objects/volume method; restore; compare checksum; record RTA/RPA. **Prerequisites/resources:** Docker/Podman, kind, kubectl, 2–3 GB RAM and official docs. **Topology:** one cluster, MinIO, source `app-lab`, target `app-lab-restore`.

**Preflight:**

```bash
set -eu
CTX=kind-velero-lab
kubectl config current-context | grep -Fx "$CTX" >/dev/null || { echo "wrong context" >&2; exit 2; }
kubectl --context "$CTX" get nodes
```

Create cluster if needed: `kind create cluster --name velero-lab`; verify `kubectl config current-context` exactly equals `kind-velero-lab`. Follow §9.3 install and manifest steps, using pinned verified plugin tag and fake credentials only. Create backup and restore:

```bash
velero backup create app-lab-lab1 --include-namespaces app-lab --ttl 168h
velero backup describe app-lab-lab1 --details
velero backup logs app-lab-lab1
velero restore create app-lab-lab1-restore --from-backup app-lab-lab1 \
  --namespace-mappings app-lab:app-lab-restore
velero restore describe app-lab-lab1-restore --details
velero restore logs app-lab-lab1-restore
```

**Assertions:** expected objects exist; no unexplained restore failures; volume method actually completed; restored marker/checksum equals source. **RTA/RPA:** time through app checks; marker alone cannot give precise RPA. **Evidence:** `versions.txt`, redacted BSL status, logs/descriptions, object inventory, checksums, timestamps and limitations. **Cleanup:** recheck context and exact cluster name; delete only `velero-lab`, verify `kind get clusters`, remove fake credential file. Do not delete shared MinIO. **Common failures:** endpoint/path-style mismatch, missing bucket, plugin incompatibility, no StorageClass, FSB absent, invalid namespace mapping. **Fidelity:** local observation only.

### Lab 2 — Compare PVC file-system backup, CSI snapshot and snapshot data movement

**Safety contract:** synthetic files and named lab PVC only; preserve a verified backup before deletion. Never delete non-lab snapshots. **Goal:** compare method evidence, timings, checksums and portability. **Prerequisites:** Lab 1, PVC provisioner; CSI CRDs/driver and data mover only if feasible. **Topology:** separate backups per method; source PVC with known files.

**Preflight:** confirm exact context/namespace/PVC; inspect `kubectl get sc`, `kubectl get volumesnapshotclass`, and snapshot CRDs without assuming they exist. Populate synthetic files:

```bash
kubectl --context kind-velero-lab -n app-lab exec deploy/sample-web -- sh -c \
 'for i in 1 2 3 4 5; do printf "synthetic-record-%s\n" "$i" > "/data/record-$i.txt"; done; cd /data; sha256sum record-*.txt > checksums.txt; cat checksums.txt'
```

For **FSB**, verify node-agent/support, select volume via annotation or supported default option, then inspect per-volume operation records. For **CSI**, proceed only with compatible driver/controller/class and inspect snapshot/backend. For **snapshot data movement**, verify official prerequisites and inspect `DataUpload`/`DataDownload` if present `[VERIFY]`. If unsupported, record `NOT RUN — unsupported`; do not claim a comparison ran.

**Assertions:** restore each supported method to isolation; compare file count and hashes; record bytes/duration/resource pressure. **RTA/RPA:** measured times only; file timestamp does not necessarily measure application RPA. **Evidence:** logs, PVB/snapshot/data-movement evidence, hashes, timings, portability note. **Cleanup:** recheck context; remove only lab PVC/snapshots after preserving a known-good copy; verify no unintended resources remain. **Common failures:** missing snapshot class, FSB not enabled, volume not mounted, storage class mismatch, permissions. **Fidelity:** node-local hostpath snapshots are not DR-capable if node/host is lost.

### Lab 3 — Application-consistency hooks vs PostgreSQL native recovery

**Safety contract:** disposable synthetic DB/state only; no external endpoints or real credentials. **Goal:** demonstrate checkpoint/hook concepts and compare native PostgreSQL backup/PITR from M05. **Prerequisites:** working lab; lightweight PostgreSQL/operator only if resources allow; otherwise use the file simulation below. **Topology:** tiny database with known-answer query; capture while writes may be in flight.

Verify official hook syntax for selected Velero release `[VERIFY]`. Annotation names, argument encoding, container, timeout and `onError` are not guessed. Hook design intent:

```yaml
# Design intent only; translate to exact versioned hook syntax.
# pre-backup: request checkpoint/quiesce
# verify exit status and timeout
# backup: capture configured resources/data
# post-backup: resume writers according to documented outcome
```

For native path, follow M05's PostgreSQL/operator procedure, including base backup and required WAL/archive chain for PITR. Verify timeline/recovery target and integrity using official engine procedures. **Fallback simulation:** write synthetic records to a local file while a process updates it; compare uncoordinated copy with a copy after writer pause and flush marker. This is not equivalent to database recovery.

**Assertions:** hook outcome/failure policy visible; native recovery queries match; PVC copy is not labelled application-consistent without evidence. **RTA/RPA:** record comparable validation boundaries only. **Evidence:** hook docs/config, redacted logs, SQL/marker checks, native recovery logs, limitations. **Cleanup:** verify context/DB host; remove only lab DB namespace/PVC/fake credentials and verify. **Common failures:** hook never runs, missing WAL, wrong target, operator absent. **Fidelity:** hook demo is not proof of DB consistency.

### Lab 4 — Schedules, TTL, tier selectors, metrics and coverage audit

**Safety contract:** lab-only schedule and synthetic inventory; no production schedule modifications. **Goal:** test schedule creation, coverage audit and alerts. **Prerequisites:** Python 3, lab, optional `promtool`. **Topology:** tier register, Schedule and normalized inventory.

Fixture:

```json
{
  "namespaces":[{"name":"app-lab","tier":"3","backup_required":true},{"name":"uncovered-lab","tier":"2","backup_required":true}],
  "schedules":[{"name":"app-lab-hourly","namespaces":["app-lab"],"enabled":true}],
  "pvcs":[{"namespace":"app-lab","name":"sample-data"},{"namespace":"uncovered-lab","name":"missing-data"}],
  "backup_methods":{"app-lab/sample-data":{"method":"fsb","last_operation":"Completed","portable_to_target":true}}
}
```

Save §9.6 coverage script as `coverage_audit.py`, fixture as `inventory.json`, run `python3 coverage_audit.py inventory.json`; expected exit is non-zero because uncovered namespace/PVC are intentional. Add valid records and verify a passing fixture. Apply Schedule only after checking installed CRD schema/version; verify it produces a fresh Backup and inspect actual scope/data method. Use §9.6 normalized alert rules; run `promtool check rules backup-alerts.yml` if installed, then test firing/clearing separately.

**Assertions:** audit fails uncovered fixture and passes complete fixture; schedule produces a backup; TTL/selectors match release. **RTA/RPA:** report verified point age vs tier budget. **Evidence:** tier register, manifest, backup result, audit output, rule test and owners. **Cleanup:** verify context; remove exact lab Schedule and fixtures; verify absence. **Common failures:** API schema mismatch, selector drift, TTL confused with lifecycle, guessed metrics. **Fidelity:** fixture tests audit logic, not live exporter.


### Lab 5 — Restore to a second `kind` cluster

**Safety contract:** creates `kind-velero-primary` and `kind-velero-dr`, synthetic namespace and disposable bucket/prefix only. Never target a real/shared bucket. **Goal:** exercise cross-cluster restore and measure RTA/RPA. **Prerequisites:** Lab 1, disk/RAM headroom; if 8 GB is insufficient, stop one cluster and use a sequential simulation. **Topology:** both clusters share laptop/host/network; no region isolation.

**Preflight:** record contexts and versions, verify source backup and completed volume method, confirm target CRDs/operators and object-store access. Create target only if necessary:

```bash
kind create cluster --name velero-dr
kubectl config get-contexts
kubectl config use-context kind-velero-dr
kubectl config current-context | grep -Fx kind-velero-dr
kubectl --context kind-velero-dr get nodes
```

Install compatible Velero/plugin and configure BSL using versioned docs. Prefer read-only DR credentials if supported `[VERIFY]`; install CRDs/operators first and configure StorageClass mapping through supported mechanism `[VERIFY]`. Inspect backup contents, restore to isolated `app-lab-dr`, verify object state, PVC binding, checksums, app query, images, network/DNS/identity. If volume data is not portable, fail honestly.

**Assertions:** DR reads backup; no unexplained failures; data matches; RTA/RPA recorded. **Evidence:** versions/contexts, redacted BSL, logs, storage mapping, checksums and shared-host caveat. **Cleanup:** verify context and exact names, delete only clusters created by this lab, verify `kind get clusters`; preserve explicitly shared MinIO. **Common failures:** BSL path mismatch, plugin/CRD/StorageClass mismatch, image unavailable, provider-bound snapshot. **Fidelity:** two clusters on one laptop are not two regions.

### Lab 6 — GitOps and Velero ownership conflict

**Safety contract:** Argo CD **or** Flux in a throwaway cluster, not both owning same object; synthetic app only. Never change production sync/prune. **Goal:** observe conflict and perform deliberate ownership handoff. **Prerequisites:** Lab 1; optional controller install; otherwise use a clearly labelled desired-state/prune simulation. **Topology:** GitOps-declared Deployment and Velero restore introduce a live/desired difference.

**Preflight:** verify `kind-velero-lab`, app owner, Git commit, controller version/settings and initial live state. **Procedure:** deploy synthetic app; back it up; create a controlled drift; observe events/diff; use documented controller procedure to pause/control sync/prune `[VERIFY]`; restore into isolation or restore only designated data/unmanaged resources; inspect tracking labels/annotations and owner references; update source of truth if appropriate; resume reconciliation and verify stable convergence.

**Assertions:** ownership explicitly assigned; no unreviewed prune; final controller state matches intended configuration. **RTA/RPA:** include ownership resolution and app checks. **Evidence:** controller version, diffs/events, restore logs, pause/resume record, ownership matrix. **Cleanup:** verify context and remove only lab app/controller installed for this lab; retain shared controller. **Common failures:** release-specific behavior, stale Git source, sync resumes too early, missing CRDs. **Fidelity:** behavior is `[VERIFY]`, not universal.

### Lab 7 — CronJob/Job restore hazard

**Safety contract:** CronJob writes bounded synthetic markers only; no external endpoints. **Goal:** prove restored schedule may replay work and a mitigation prevents unintended execution. **Prerequisites:** lab cluster, `kubectl`, no real credentials. **Topology:** synthetic ETL CronJob in `etl-lab`, initially suspended.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: etl-lab
  labels: {purpose: velero-training}
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: synthetic-etl
  namespace: etl-lab
spec:
  schedule: "*/5 * * * *"
  suspend: true
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
          - name: etl
            image: busybox:1.36
            command: ["sh", "-c"]
            args: ['mkdir -p /work; date -u +%Y-%m-%dT%H:%M:%SZ >> /work/run-log.txt; echo synthetic-only']
            volumeMounts: [{name: work, mountPath: /work}]
          volumes: [{name: work, emptyDir: {}}]
```

`emptyDir` is pod-local and illustrates scheduling, not durable output. For persistent output, use a lab PVC plus deterministic idempotency key. Verify context and `spec.suspend`; back up while suspended; restore to another namespace; inspect schedule state and do not enable until idempotency/target checks pass. A separate short hazard demo may enable the job only if no external side effects are possible.

**Assertions:** no unexpected Job before approval; one intentional run creates bounded marker; replay guard is documented. **RTA/RPA:** time until safe resume, not object creation. **Evidence:** CronJob YAML, logs, Job history, marker/idempotency result. **Cleanup:** suspend, remove only named lab job/CronJob and `etl-lab`, verify no resources remain. **Common failures:** schedule unexpectedly active, image unavailable, `emptyDir` mistaken for durable state. **Fidelity:** synthetic workload only.

### Lab 8 — Security hardening and negative tests

**Safety contract:** fake credentials, throwaway bucket/namespace and test identity only. Expected-deny attempts only; never test deletion against real backup. **Goal:** prove workload cannot delete backups or create Restore, inspect Secret inclusion without exposing values, and test a simple redacted scan. **Prerequisites:** Velero lab, `kubectl`, test ServiceAccount/RBAC; object lock only if supported by selected MinIO version `[VERIFY]`.

```bash
kubectl --context kind-velero-lab -n app-lab create secret generic fake-api-token \
  --from-literal=token='SYNTHETIC-NOT-A-REAL-TOKEN'
kubectl --context kind-velero-lab -n app-lab create serviceaccount workload-test
kubectl --context kind-velero-lab auth can-i delete backups.velero.io \
  --as=system:serviceaccount:app-lab:workload-test -n velero
kubectl --context kind-velero-lab auth can-i create restores.velero.io \
  --as=system:serviceaccount:app-lab:workload-test -n velero
```

Expected answer is `no`; if `yes`, stop and fix lab RBAC. This checks Kubernetes authorization, not object-store IAM. Test object-store deletion separately only with a fake identity and disposable bucket. Admission-policy examples are engine/version-specific `[VERIFY]`. Inspect backup contents without dumping Secret values. Example scanner for a synthetic text inventory:

```python
#!/usr/bin/env python3
import re, sys
from pathlib import Path
PATTERNS = [re.compile(r"(?i)(password|token|secret|api[_-]?key)\s*[:=]")]
def main(path):
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    count = sum(any(p.search(line) for p in PATTERNS) for line in lines)
    print(f"scanned_lines={len(lines)} suspicious_lines={count}")
    return 1 if count else 0
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} synthetic-inventory.txt", file=sys.stderr); raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
```

Scanner is not comprehensive; never print matches or scan unapproved data. Object lock/versioning must be verified against the exact MinIO/provider version.

**Assertions:** test identity denied; inventory shows Secrets may be included; scanner reports count only; immutability claimed only if actually verified. **RTA/RPA:** not a timing lab; record whether test identity could delete/read. **Evidence:** `auth can-i`, admission result, redacted inventory, scan summary, identity map. **Cleanup:** verify context; remove only fake Secret/ServiceAccount/RBAC and unique test bucket; revoke fake credentials. **Common failures:** inherited permissions, IAM confused with RBAC, scanner leaks values, object lock unsupported. **Fidelity:** base64 is not encryption; MinIO does not prove cloud semantics.

### Lab 9 — Failure and fallback drill

**Safety contract:** disposable test copy/prefix only; preserve known-good backup; never corrupt the only usable copy or hand-edit production repository internals. **Goal:** invalid-copy failure, fallback restore, incorrect fake BSL credential detection. **Prerequisites:** Lab 1 and two known-good synthetic backups. **Topology:** `app-lab-known-good` plus separate test-only copy; exact repository manipulation is `[VERIFY]`.

**Preflight:** confirm context, backup IDs, bucket/prefix and known-good readability; record object inventory/checksum. If a safe repository copy cannot be made, simulate corruption with a disposable invalid inventory or deny access to a disposable prefix—do not edit shared repository objects.

**Procedure:** restore known-good to isolated namespace and check marker; attempt restore of invalid copy and ensure failure is visible; restore from known-good and recheck checksum; use a separate test BSL or intentionally wrong fake credential, run backup and verify failure/staleness alert; restore valid credentials and prove a fresh backup/checksum.

**Assertions:** invalid copy does not pass application validation; fallback restores correct data; credential failure is detected; repaired path creates a verified fresh backup. **RTA/RPA:** measure fallback time and older point; do not invent values. **Evidence:** inventory/checksum, failed restore logs, fallback report, redacted auth error, alert and repair timeline. **Cleanup:** restore valid fake credential; remove only test prefix/namespaces; prove known-good remains readable. **Common failures:** accidentally altering source, shared repository metadata, credential change affects other lab, status-only monitoring. **Fidelity:** not a ransomware simulation.

### Lab 10 — Velero vs GitOps + application-native recovery comparison

**Safety contract:** memo uses prior synthetic lab evidence; no production changes or invented measurements. **Goal:** compare Velero-centric, GitOps + native recovery and layered combination. **Prerequisites:** Labs 1–9 evidence and tier register. **Topology:** compare equivalent verified recovery milestones; mismatched boundaries invalidate direct timing comparison.

```markdown
# Recovery-method decision memo
## Service/tier
- Service: <synthetic service>
- RTO/RPO: <tier register>
- Data domains: <API objects, PVC bytes, database, dependencies>
## Evidence reviewed
- Lab IDs/timestamps:
- Version checks:
- Methods not run and why:
## Comparison
| Design | RTA | RPA | Consistency | Portability | Security/failure mode | Complexity |
|---|---|---|---|---|---|---|
| Velero-centric | <measured/not tested> | <measured/not measurable> | <evidence> | <evidence> | <evidence> | <evidence> |
| GitOps + native | <measured/not tested> | <measured/not measurable> | <evidence> | <evidence> | <evidence> | <evidence> |
| Layered | <measured/not tested> | <measured/not measurable> | <evidence> | <evidence> | <evidence> | <evidence> |
## Recommendation
- Selected design and assumptions:
- Residual risks, owner and retest date:
## Exit strategy
- Export format/location, keys, alternate restore path:
- Test required before retiring current path:
```

**Assertions:** missing measurements are labelled; consistency and portability are separate; exit strategy names formats/keys and a tested alternative. **RTA/RPA:** use prior results only. **Evidence:** memo, assumptions and owners. **Cleanup:** no cluster changes; verify none created. **Common failures:** fabricated timings, popularity-based choice, omitted independent copy/exit. **Fidelity:** no production-scale or compliance claim.

### Lab 11 — N−1/upgrade compatibility and operating-program audit

**Safety contract:** disposable cluster/test plan only; never upgrade production or risk only backup. Do not downgrade CRDs unless official docs support it. **Goal:** test a prior-version backup against a candidate stack if safe and audit schedules, coverage, BSL, metrics, restore cadence, maintenance and deletion permissions. **Prerequisites:** versions and official release/upgrade docs; known-good synthetic backup. **Topology:** prior backup restored into fresh candidate cluster; if unsafe/unavailable, submit an unverified scaffold.

```csv
backup_velero_version,restore_velero_version,kubernetes_version,plugin_version,node_agent_mode,volume_method,crd_state,result,evidence,owner
<VERSION>,<VERSION>,<VERSION>,<IMAGE:TAG>,<mode>,<method>,<verified CRDs>,NOT_RUN,<source links>,<owner>
```

Procedure: verify official exact version pair; preserve backup and inventory; create fresh test cluster; install candidate Velero/plugin/CRDs per docs; configure read-only test-copy access if supported; inspect metadata; restore in isolation and validate objects/bytes/app marker; audit schedules for fresh Backup, PVC method completion, BSL credential scope/rotation, metrics, restore cadence, maintenance support `[VERIFY]`, cleanup and deletion permissions; assign each defect an owner/due date/retest.

**Assertions:** no compatibility claim without source plus test; schedules produce fresh backups; least-privilege delete tests pass; defects owned. **RTA/RPA:** record only if actually measured; scaffold has none. **Evidence:** matrix/source URLs, restore result or unverified scaffold, audit, owners/due dates and cleanup. **Cleanup:** verify context and test prefix; remove only disposable cluster/copy; prove original known-good remains. **Common failures:** CRD/plugin mismatch, repository unreadable, stale schedule, only-copy risk. **Fidelity:** one version pair does not prove every upgrade path.

## 9.11 Self-check questions

Answer with assumptions and safety boundaries. Command exit status alone is not proof of application recovery.

1. Why is Backup phase `Completed` not proof of recoverability?
2. Distinguish Kubernetes API objects and PVC bytes.
3. What evidence distinguishes FSB, CSI snapshot and snapshot data movement?
4. Why is a node-local `kind` hostpath snapshot not a regional DR copy?
5. What is the difference between BSL and VSL?
6. How do namespace filters, selectors and cluster-resource options affect scope?
7. What does TTL control, and why is it not identical to object-store lifecycle retention?
8. What can a pre-backup hook guarantee and not guarantee?
9. What is required before cross-cluster restore?
10. Why must CRDs/operators be ready before their custom resources?
11. How can GitOps auto-sync/prune conflict with restore, and how should ownership be resolved?
12. Why can restored CronJobs duplicate work? Give two mitigations.
13. Why is base64 not encryption, and why can restoring a Secret be dangerous after compromise?
14. Define RTA/RPA and their measurement boundaries.
15. What should backup-age/failure alerts measure? Why not guess metric names?
16. A restore reports partial failure. What is the diagnostic sequence?
17. What is N−1 compatibility testing, and why not use the only backup copy?
18. Design a tier-0 recovery layer with GitOps, Velero, native recovery and an independent copy.
19. A DR PVC is Pending due to StorageClass mismatch. What must happen before cutover?
20. How do you prove workload credentials cannot delete backups? Distinguish Kubernetes RBAC from object-store IAM.

### Answer key with reasoning

1. `Completed` describes controller operations/scope, not all bytes, dependencies or application correctness. Inspect volume-operation evidence, contents and restore tests.
2. A PVC is an API declaration; bytes reside in a volume/backend. Restoring the claim may yield an empty volume. Verify objects and known-answer bytes.
3. FSB needs node-agent/file-system operation evidence; CSI needs snapshot/backend evidence; data movement needs transfer and object-store-copy evidence. Resource existence alone is insufficient.
4. Snapshot may share host/node disk with source; losing the host can lose both. A distinct failure domain and tested portable copy are required.
5. BSL configures object storage for backup data/metadata; VSL configures snapshot-provider operations where used. Check access/credentials separately.
6. Filters select objects; cluster-scoped resources may affect other workloads; label drift can silently remove scope. Compare contents with inventory.
7. TTL is backup resource retention; object-store lifecycle, immutability and repository cleanup are separate. Test interactions to avoid early deletion.
8. A hook runs a documented command with configured timeout/error handling. It cannot coordinate every writer/PVC or prove consistency without application-specific procedure and evidence.
9. Compatible versions, readable portable copy, CRDs/operators, target storage, images, network/DNS/identity and application verification. Same-laptop clusters are not independent regions.
10. API must recognize the kind and controller/webhooks must understand/reconcile it; otherwise CR may be rejected or remain unreconciled.
11. GitOps reconciles toward declared state and may remove restored drift. Assign ownership, isolate, control sync/prune through documented procedure, then hand ownership back deliberately.
12. Restored schedules may run again. Suspend/exclude until validation; use idempotency keys, bounded outputs or deduplication and verify no duplicate effects.
13. Base64 is reversible. Backups can expose Secret data; old compromised credentials may become active. Review, revoke and rotate before enabling workloads.
14. RTA is time from defined incident start to verified recovery; RPA is gap between loss event and newest verified recoverable point. Include application checks and state time/data boundary.
15. Alert on age of newest verified point, repeated failures, missing coverage, BSL/node-agent problems and failed restore tests. Metric names/labels vary; inspect actual endpoint and normalize with tested exporter.
16. Keep isolated; inspect describe/logs/events; classify restored/skipped/failed; inspect volume operations and storage binding; verify CRDs, policy, identity and dependencies; run data/app checks; fallback if needed.
17. Test recovery across a supported version boundary in a disposable environment. Preserve a known-good copy because incompatibility can make the test unusable.
18. GitOps rebuilds configuration; Velero restores selected Kubernetes objects/portable PVC data; native backup/PITR protects application consistency; independent immutable copy protects against deletion/compromise. Trade-offs: complexity, cost, ordering and multiple toolchains.
19. Keep isolated; inspect target classes/events, configure supported mapping/provisioner, verify capacity/access mode and restore data; validate bytes before cutover.
20. Use a dedicated identity and `kubectl auth can-i`/admission tests for Kubernetes API permissions; separately test provider IAM with fake identity and disposable bucket. One denial does not prove the other.

## 9.12 Evidence artifacts

Evidence must prove what was tested and its limits—not merely that a Backup exists. Keep timestamped evidence in access-controlled storage with redaction.

| Artifact | Minimum contents | Quality check |
|---|---|---|
| Compatibility matrix | CLI/server, Kubernetes, plugin, node-agent/data mover, CRDs, storage method, official sources | exact tags, date, verified/unverified status |
| Topology/fidelity note | contexts, namespaces, storage endpoint and failure domains | explicitly says `kind` is not a region |
| BSL/VSL status/config | endpoint/region/path-style, status, redacted credentials | no secrets/tokens |
| Backup/restore descriptions/logs | IDs, timestamps, warnings and phases | redact secrets |
| Backup contents inventory | resources and volume methods | matches tier register; exclusions understood |
| Namespace/PVC coverage | required vs covered, method and owner | uncovered items cause non-zero audit result |
| Checksums/known answers | source/target hashes, queries and timestamps | same algorithm/data |
| Volume-method comparison | FSB/snapshot/data movement, duration, bytes, portability | unsupported method is `not run`, not passed |
| Native consistency report | hook/native PITR output and integrity checks | no claim from snapshot alone |
| Schedule/TTL policy | tier register, manifests and generated Backup results | proves fresh backup was produced |
| Metrics/alert tests | actual metrics, rule file and `promtool` or alternative tests | syntax and behavior separately tested |
| Cross-cluster report | versions, BSL access, storage mapping, RTA/RPA | shared-laptop caveat included |
| GitOps conflict evidence | before/after diff, events and handoff | final state stable |
| CronJob replay evidence | suspend/exclude, Job history, idempotency | no uncontrolled side effects |
| RBAC/admission tests | expected-deny outcomes and identities | separate Kubernetes RBAC from object IAM |
| Secret scan | summary counts and redacted findings | no raw values |
| Failure/fallback report | invalid-copy failure, fallback restore and checksum | known-good copy remains readable |
| Decision memo | measured comparison, assumptions, residual risks, exit path | no fabricated numbers |
| N−1 result | tested matrix or explicitly unverified scaffold | exact versions and source checks |
| Cleanup verification | contexts, namespaces, clusters, buckets, credentials | only lab resources removed |
| Defect register | finding, severity, owner, due date and retest | each defect accountable |

Example naming: `2026-10-29T120000Z-lab1-restore-report.md` `[ILLUSTRATIVE]`. Store redacted reports separately from restricted raw logs. Never include credentials, Secret values, customer data or unnecessary personal data. Identify every result as a live lab observation, unverified scaffold or source-based design recommendation.

## 9.13 Common interview and design-review questions

1. **Velero vs GitOps vs native backup?** GitOps reconstructs configuration; Velero captures selected Kubernetes objects and supported volume data; native backup/PITR protects application-defined consistency. Layer them and test recovery order.
2. **What does Velero protect/not protect?** Selected API objects and supported volume data; not automatically etcd recovery, external resources, every PVC byte, PITR, keys or app correctness.
3. **Why isn't `Completed` proof?** It does not prove all bytes/dependencies were covered or app checks pass. Inspect method evidence, contents and isolated restore.
4. **Compare CSI, FSB and data movement.** CSI depends on driver/backend and may be provider-bound; FSB reads mounted volume files through supported node-agent path; data movement copies snapshot data to object storage where supported, adding transfer complexity.
5. **Crash vs application consistency?** Crash-consistent state may need logs/recovery; app-consistent recovery coordinates writers/transactions. Prove with native procedures and integrity checks.
6. **BSL vs VSL?** BSL configures object storage; VSL configures snapshot provider. Check plugins and credentials separately.
7. **Cross-cluster prerequisites?** Compatible versions, portable readable copy, CRDs/operators, storage, images, network/DNS/identity and app validation.
8. **Why CRDs/operators first?** Custom resources depend on API schema/controller; otherwise rejected or unreconciled.
9. **Prevent GitOps conflict?** Map ownership, isolate, control sync/prune, restore designated resources/data, reconcile from source and hand back with diff evidence.
10. **Prevent CronJob replay?** Suspend/exclude until safe, use idempotency keys/bounded side effects, verify Job history before resume.
11. **Secrets/RBAC risks?** Backups contain credentials/privileges. Inspect content, restrict Restore, rotate compromised identities and audit.
12. **How do immutable copies help?** Object lock/immutability and separate identities can constrain deletion; verify provider semantics and test with fake identity/disposable bucket.
13. **Important metrics?** Verified recovery-point age, failures, duration/size anomalies, BSL, volume coverage, node-agent and layered restore-test success. Confirm metric names/labels.
14. **Partial restore diagnosis?** Separate object, volume, binding, CRD/operator, policy, dependency and app failures; keep isolated until all required checks pass.
15. **N−1 compatibility?** Test proposed stack with prior-version backup using exact versions in disposable environment; it doesn't guarantee all paths.
16. **Tier-0 architecture?** GitOps + native backup/PITR + selected Velero resources/portable data + independent copy; define order, ownership, keys and measured RTA/RPA.
17. **Upgrade governance?** Pin versions, check official notes, test CRD/plugin compatibility, preserve copies, run new backup/restore and verify schedules.
18. **Missing StorageClass in DR?** Inspect events/classes, use supported mapping/provisioner, isolate, restore and verify bytes before cutover.
19. **Exit strategy?** Document export format, keys, alternate reader/restore procedure and prove it before retiring old path.
20. **Evidence for recovery claim?** Version matrix, content/method proof, restore logs, application checks, RTA/RPA, dependencies/ownership and limitations. Resource status alone is insufficient.

### Design-review exercise

Design recovery for a hypothetical tier-0 AI inference platform: API Deployment, model artifacts, PostgreSQL metadata DB, operator, GitOps configuration, Secrets and ingestion CronJob. State assumptions/RTO/RPO, consistency, resource ownership, layers, independent-copy boundary, restore order, key strategy, replay controls, checks, metrics, fallback and exit. Mark provider/version items `[VERIFY]`. Pass only if each data domain has an owner and testable recovery proof.

## 9.14 Sources and verification notes

Use versioned official docs for the exact deployment. `/docs/main/` may describe development behavior. Record exact page/release and date in `versions.txt`. The URLs are authoritative starting points, not a claim that any particular version tuple is compatible.

### Velero

- Install overview: <https://velero.io/docs/main/basic-install/>
- Customize installation/plugins/node-agent: <https://velero.io/docs/main/customize-installation/>
- MinIO evaluation setup (not production architecture): <https://velero.io/docs/main/contributions/minio/>
- BSL/VSL: <https://velero.io/docs/main/locations/>
- File-system backup: <https://velero.io/docs/main/file-system-backup/>
- CSI snapshots: <https://velero.io/docs/main/csi/>
- CSI snapshot data movement: <https://velero.io/docs/main/csi-snapshot-data-movement/>
- Restore reference: <https://velero.io/docs/main/restore-reference/>
- Backup reference: <https://velero.io/docs/main/backup-reference/>
- Schedule reference: <https://velero.io/docs/main/backup-reference/#schedule-reference> `[VERIFY]` anchor/current URL.
- Hooks: <https://velero.io/docs/main/backup-hooks/> `[VERIFY]` current page/release support.
- Metrics: <https://velero.io/docs/main/metrics/> `[VERIFY]` exact names/labels/endpoint.
- Upgrade guide example is version-specific: <https://velero.io/docs/main/upgrade-to-1.14/>; find matching page for selected release `[VERIFY]`.
- Project repository/releases: <https://github.com/vmware-tanzu/velero> `[VERIFY]` current governance, organization and maintenance before adoption.

### Kubernetes

- PVs/StorageClasses: <https://kubernetes.io/docs/concepts/storage/persistent-volumes/> and <https://kubernetes.io/docs/concepts/storage/storage-classes/>
- Volume snapshots: <https://kubernetes.io/docs/concepts/storage/volume-snapshots/>
- Custom resources/CRDs: <https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/>
- RBAC: <https://kubernetes.io/docs/reference/access-authn-authz/rbac/>
- CronJobs: <https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/>
- Namespaces: <https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/>

### Storage, database, GitOps and metrics

- MinIO docs: <https://min.io/docs/>; verify current versioning/object-lock support and lab image compatibility `[VERIFY]`.
- PostgreSQL backup/PITR: <https://www.postgresql.org/docs/current/backup.html> and <https://www.postgresql.org/docs/current/continuous-archiving.html>; match installed major version.
- CloudNativePG: <https://cloudnative-pg.io/documentation/>; verify operator-native recovery guidance.
- Argo CD: <https://argo-cd.readthedocs.io/en/stable/>; verify sync/prune behavior for chosen release.
- Flux: <https://fluxcd.io/flux/>; verify reconciliation/suspension behavior.
- Prometheus rules/`promtool`: <https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/> and <https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/>.
- Vault, if Vault-specific behavior is used: <https://developer.hashicorp.com/vault/docs>; verify deployment/edition behavior.

### Verification ledger

Before running labs, verify and record: selected CLI/server versions and Kubernetes range; exact plugin image compatibility; CSI built-in/plugin state; CRDs and prerequisites for FSB/node-agent/CSI/data movement; exact flags/annotations/hooks/restore policies; metric names/labels; MinIO endpoint/path-style/versioning/object lock; native PostgreSQL/CloudNativePG recovery; GitOps sync/prune; Prometheus syntax.

If a claim cannot be verified, keep `[VERIFY]` and do not run the dependent command as known-good. If unsupported, record `NOT RUN — unsupported` and document the fidelity gap. Do not fabricate outputs, measurements, maintenance status or compatibility. A local `kind` drill proves only the tested workflow—not true regional recovery, production-scale objectives, compliance or consistency beyond the checks actually performed.
