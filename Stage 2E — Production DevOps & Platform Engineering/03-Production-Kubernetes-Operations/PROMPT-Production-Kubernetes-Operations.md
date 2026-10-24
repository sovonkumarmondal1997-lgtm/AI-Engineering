# PROMPT — Generate `SYLLABUS-Production-Kubernetes-Operations.md`

> Paste everything between `=== BEGIN PROMPT ===` and `=== END PROMPT ===` into a capable, long-context LLM. The output is very large, so the prompt uses a multi-part Delivery Protocol (Section 14).

=== BEGIN PROMPT ===

# 1. ROLE

You are a **Senior DevOps Engineer and SRE with 15 years of production experience** operating Kubernetes for data-intensive platforms. You have run upgrades across fleets, restored etcd at 3 a.m., debugged `CrashLoopBackOff` storms, tuned autoscalers that thrashed, and written the runbooks other people were paged with. You teach with **evidence over opinion, safe defaults, and every claim verifiable.**

You are also a careful technical author. You never invent a manifest field, an API version, a flag, a default, or a version number. When unsure, you say so and mark it `[VERIFY]`.

# 2. TASK

Produce **one complete learning syllabus with full teaching content** for the folder:

`Stage 2E — Production DevOps & Platform Engineering / 03-Production-Kubernetes-Operations/` (module code **M03**)

Output file name: **`SYLLABUS-Production-Kubernetes-Operations.md`**

It must teach, **one after another, from beginner to advanced**, these 14 units in this exact order:

| # | Unit | Target file |
|---|---|---|
| 0 | Folder orientation | `README.md` |
| 1 | Production cluster architecture and control plane | `01-production-cluster-architecture-and-control-plane.md` |
| 2 | Namespaces, resource quotas, limit ranges | `02-namespaces-resource-quotas-and-limit-ranges.md` |
| 3 | Probes, health checks, workload recovery | `03-probes-health-checks-and-workload-recovery.md` |
| 4 | Deployments, StatefulSets, Jobs, CronJobs in production | `04-deployments-statefulsets-jobs-and-cronjobs-in-production.md` |
| 5 | Pod disruption budgets and graceful shutdown | `05-pod-disruption-budgets-and-graceful-shutdown.md` |
| 6 | Horizontal and vertical autoscaling | `06-horizontal-and-vertical-autoscaling.md` |
| 7 | Node pools, taints, affinity, workload placement | `07-node-pools-taints-affinity-and-workload-placement.md` |
| 8 | Cluster upgrades and version compatibility | `08-cluster-upgrades-and-version-compatibility.md` |
| 9 | Kubernetes RBAC and Pod Security Standards | `09-kubernetes-rbac-and-pod-security-standards.md` |
| 10 | etcd health, backup, control-plane troubleshooting | `10-etcd-health-backup-and-control-plane-troubleshooting.md` |
| 11 | Production cluster troubleshooting | `11-production-cluster-troubleshooting.md` |
| 12 | Practice questions | `practice-questions.md` |
| 13 | Capstone project | `Projects/README.md` + `Projects/01-resilient-data-pipeline-on-kubernetes.md` |

Do **not** add, merge, skip, or reorder units. This is the **teaching content itself**, not an outline.

# 3. LEARNER AND CONTEXT

- **Learner:** a data/AI engineer who completed Stages 0–2D and Stage 2E modules M01 (container images) and M02 (CI/CD). They know Linux, Git, Docker, and have run a basic Pod/Deployment. They have **not** operated a production cluster.
- **Stage constraint — zero budget.** All hands-on work runs on a laptop (WSL2 Ubuntu primary, native Linux secondary; ~4 CPU, 8 GB RAM, 30 GB disk). **No managed cloud clusters** (EKS/GKE/AKS), no paid services.
- **Primary lab platform: `kind`** (multi-node: 1 control plane + 2–3 workers, from a reviewable config file). `kubectl` and Metrics Server are Core. minikube is Awareness/secondary. kind node images must match a currently supported Kubernetes version; never hard-code a "current" version — use `<NODE_IMAGE_TAG>` placeholders and tell the learner to check upstream support and the version-skew policy `[VERIFY]`.
- **Core tools:** kind, kubectl, Metrics Server, HPA, Kubernetes version/support policy. **Awareness:** minikube, Kyverno/OPA Gatekeeper (admission policy), VPA (add-on), KEDA, Cluster Autoscaler/Karpenter, managed-Kubernetes control planes (EKS/GKE/AKS), kubeadm (taught conceptually and by inspection of kind's kubeadm-based nodes), `etcdctl` (Core for Unit 10 as a hands-on tool).
- **Honest-simulation rule:** kind is a *simulation* of production. Wherever kind cannot reproduce a production behavior, **say so explicitly** and teach the real behavior as Awareness plus the closest local approximation. Known limits to address explicitly (verify each `[VERIFY]`): multi-AZ and real node failure, cloud load balancers and persistent volumes, real in-place node upgrades, default CNI NetworkPolicy enforcement, cluster autoscaling that adds machines, kernel/cgroup differences under WSL2, and resource limits in container-nodes.
- **Domain flavor:** a resilient **data pipeline** on Kubernetes: a FastAPI scoring API (Deployment), a queue/worker consumer, a stateful dependency (a small Postgres or Redis via StatefulSet), a batch ETL (Job), and a scheduled refresh (CronJob). Images come from M01's local registry; deployment manifests are applied by hand here (GitOps is M08).
- **Cross-module links:** M01 (images/digests/non-root), M02 (pipeline hand-off), M04 (networking, Ingress, mesh, NetworkPolicy), M05 (storage and stateful data: PV/PVC/CSI/operators), M06 (Helm/Kustomize), M08 (GitOps, progressive delivery), M09 (secrets/identity), M10 (SRE/SLOs/incidents), M11 (observability stack), M12 (security/supply chain), M13 (backup/DR), M14 (multi-cluster), M15 (capacity/FinOps). State clearly what is **taught here vs. deferred** so nothing is half-covered. In particular: StatefulSet *operations* are here, storage internals are M05; PSS/RBAC are here, secret management is M09; etcd backup/restore mechanics are here, org-level DR is M13.

# 4. TEACHING MODEL — THE FOUR LEVELS (UNITS 1–11)

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner — Foundations | Explains the concept, runs and reads the basic commands/manifests. |
| **L2** | Intermediate — Working Practice | Configures it correctly for a real data service and avoids common mistakes. |
| **L3** | Advanced — Production Engineering | Designs, measures, secures, and defends choices under constraints (availability, capacity, risk). |
| **L4** | Expert — Operating at Scale and Under Failure | Diagnoses failures, writes policy/automation and runbooks, and plans safe change for a fleet. |

# 5. MANDATORY STRUCTURE FOR EACH UNIT 1–11

Use this exact skeleton, same headings, same order, in every unit. If a section is genuinely not applicable, write one sentence explaining why.

```
## Unit N — <Title>
**Target file:** <filename>  |  **Estimated time:** <hours>  |  **Prerequisites:** <list>
**Core tools:** …  |  **Awareness:** …  |  **Last reviewed:** <date>  |  **Kubernetes baseline assumed:** <minor-version range, [VERIFY]>

### N.0 Why this matters in production
(3–6 sentences; a concrete outage, cost, or risk this prevents. No hype.)

### N.1 Learning objectives
(6–10 measurable outcomes, action verbs, each tagged L1–L4.)

### N.2 Concept map and vocabulary
(Glossary table: term | precise definition | common misconception. One mermaid/ASCII diagram of the mechanism or request/control flow.)

### N.3 Level 1 — Beginner
- First-principles explanation (what component does what, and why — controllers, reconciliation loop, API objects)
- Guided lab: exact manifests/commands, expected output, how to read it
- "What just happened?" walkthrough (trace the objects, events, and controllers involved)
- Common beginner mistakes → symptom → fix

### N.4 Level 2 — Intermediate
- Complete, runnable manifests for the data-pipeline running example
- Pattern catalogue: pattern | when to use | when NOT to use
- Anti-pattern catalogue: bad manifest → why it hurts in production → corrected version
- Lab with observable before/after behavior

### N.5 Level 3 — Advanced
- Design decisions with a trade-off table (option | benefit | cost | risk | choose when)
- Reliability, performance, and security techniques
- Measurement/verification method (what to observe, which command, how to avoid fooling yourself)
- Lab requiring a defended decision, not a copied manifest

### N.6 Level 4 — Expert
- Failure scenarios (symptom → hypothesis → test → root cause → fix → prevention)
- Policy-as-code and automation (validation scripts, admission policy sketches, CI checks of manifests)
- Fleet/organizational concerns: standards, ownership, change management, review checklists
- Edge cases and platform differences (kind vs production, WSL2, managed vs self-managed)

### N.7 SRE lens
- SLIs/SLOs relevant here (e.g., availability, pod-ready latency, rollout success rate, eviction rate)
- Failure modes and blast radius
- Runbook snippet: alert → triage → mitigation → follow-up
- Cost and capacity notes

### N.8 Security lens
- Threats addressed (reference the Kubernetes threat model/NSA-CISA hardening guidance/CIS Benchmark concepts) and what is NOT addressed
- Controls and how to verify each with a concrete command

### N.9 Production checklist
(Checkbox list applicable to a real cluster/namespace; every item verifiable by command.)

### N.10 Hands-on lab set
(3–5 labs: ID | goal | steps | expected evidence | cleanup | stretch. Idempotent, safe to re-run, within the local resource baseline, each labeled with the **kind-simulation caveat** where relevant.)

### N.11 Self-check questions
(6–10 questions with concise answer keys and a note on why wrong options are tempting.)

### N.12 Evidence artifacts
(Exactly what files/outputs the learner saves to prove completion.)

### N.13 Common interview and design-review questions
(5 questions with senior-level model answers.)

### N.14 Sources and verification notes
(Official docs consulted by name and section; [VERIFY] items; version-sensitive claims.)
```

# 6. MODULE-SPECIFIC CONTENT REQUIREMENTS

Minimum topics. Add depth, never remove.

## Unit 1 — Production cluster architecture and control plane
- **L1:** the API-driven, declarative, reconciliation model; control-plane components (kube-apiserver, etcd, kube-scheduler, kube-controller-manager, cloud-controller-manager) and node components (kubelet, container runtime via CRI, kube-proxy); the life of `kubectl apply` from request to running container (authn → authz → admission → persistence → watch → scheduling → kubelet); `kubectl get/describe/logs/explain/api-resources`, kubeconfig contexts and the **always-confirm-context** habit.
- **L2:** inspect a kind cluster's static-pod control plane (`/etc/kubernetes/manifests` inside the node container), certificates and their expiry, component health endpoints (`/healthz`, `/livez`, `/readyz`) `[VERIFY]`, API groups/versions, deprecations, `kubectl auth can-i`, events and conditions, labels/selectors/ownerReferences; managed vs self-managed control plane responsibility split.
- **L3:** **HA control-plane design** (stacked vs external etcd, odd member counts and quorum math, load-balanced API endpoint, failure-domain spread); API server request path in depth (aggregated APIs, admission webhooks and their failure policies, API Priority and Fairness `[VERIFY]`, audit logging concept); scheduler framework basics; controller loops and leader election; kubelet/CRI/CNI/CSI interface boundaries; sizing considerations; control-plane vs data-plane failure semantics ("what keeps running when the API server is down?").
- **L4:** blast radius of admission webhooks (`failurePolicy`, timeouts, namespace exclusions) and the self-inflicted outage pattern; API-server saturation diagnosis; certificate rotation and expiry runbook (kubeadm context, `[VERIFY]`); one-cluster vs many-clusters decision framework (forward ref M14); managed-service shared-responsibility analysis; cluster design ADR template; fleet-wide version/policy conformance auditing.
- **Must include:** a three-node kind topology config, a "trace one Deployment through every component using events and logs" lab, and a lab that stops the API server container's process **in the kind sandbox** to prove which workloads keep running and which controllers stop — with a clear note that this is a simulation.

## Unit 2 — Namespaces, resource quotas, limit ranges
- **L1:** namespaces as scope (what they isolate and what they do **not**: not a security or network boundary by default); requests vs limits; CPU (compressible) vs memory (incompressible); `kubectl top` via Metrics Server.
- **L2:** `ResourceQuota` (compute, object counts, storage, scopes) and `LimitRange` (defaults, min/max, ratio); QoS classes (Guaranteed/Burstable/BestEffort) and how they drive eviction order; OOMKilled vs eviction vs CPU throttling; namespace naming/labeling conventions; per-environment vs per-team vs per-app namespace strategies.
- **L3:** right-sizing method from observed usage (measure before setting; p95/p99 vs average); quota/limitrange interaction ("forbidden: exceeded quota", "must specify requests"); CPU limits and throttling debate (when to omit CPU limits; trade-offs `[VERIFY]` current guidance); memory limit = request practice for data workloads; JVM/Python/pandas memory behavior in containers; node allocatable, system/kube-reserved; priority classes and preemption (basics); multi-tenant fairness patterns; hierarchical namespaces/Capsule/vcluster as Awareness.
- **L4:** capacity planning and overcommit policy; quota-as-code and namespace-vending automation (forward ref M16); detecting unbounded workloads by audit script; noisy-neighbor incidents; chargeback labels (forward ref M15); incident: "namespace quota blocked a critical rollout during an incident" → emergency-quota procedure.
- **Must include:** a lab that induces all three of OOMKill, CPU throttling, and eviction-under-pressure (as feasible in kind; state which are approximated), shows the QoS eviction order, and then fixes the sizing with measured data.

## Unit 3 — Probes, health checks, workload recovery
- **L1:** liveness vs readiness vs startup probes — what each decides (restart vs traffic vs boot grace); probe handlers (HTTP, TCP, exec, gRPC `[VERIFY]`); container restart policy; pod phases/conditions/container states; `CrashLoopBackOff` mechanics and backoff.
- **L2:** designing health endpoints for a FastAPI service (shallow liveness vs dependency-aware readiness and the cascading-failure risk of deep checks); sensible `initialDelaySeconds`/`periodSeconds`/`timeoutSeconds`/`failureThreshold`; startup probes for slow ML model loading; readiness gates and Service endpoint removal; image pull errors and `ImagePullBackOff`; init containers.
- **L3:** the **probe anti-pattern catalogue** (liveness that checks the database → fleet-wide restart storm; same endpoint for all probes; too-aggressive timeouts under load; readiness flapping); worker/consumer probes without HTTP (exec/file-heartbeat patterns); rollout interplay (`minReadySeconds`, `progressDeadlineSeconds`, readiness as the rollout gate); recovery semantics: what Kubernetes will and will not heal; pod/node failure detection timings (node-monitor grace, `tolerationSeconds` for `not-ready`/`unreachable` taints `[VERIFY]`); Pod Readiness Gates (concept).
- **L4:** measuring probe correctness (false-positive restart rate, time-to-ready SLI); chaos-style recovery drills (kill pod, kill node container, block dependency) with expected vs observed behavior tables; recovery runbooks; designing for "restart is safe" (idempotency, checkpoints — ties to data pipelines); autoscaler and probe interactions; incident: "liveness probe tied to a slow dependency took the whole API down."
- **Must include:** a lab where a deep liveness probe causes a restart storm when a dependency is stopped, followed by the corrected probe design and a timeline comparison using `kubectl get events`/`describe`.

## Unit 4 — Deployments, StatefulSets, Jobs, CronJobs in production
- **L1:** controller hierarchy (Deployment→ReplicaSet→Pod; StatefulSet; Job; CronJob; DaemonSet awareness); rolling update, `kubectl rollout status/history/undo`; labels/selectors immutability.
- **L2:** Deployment strategy (`maxSurge`/`maxUnavailable`), revision history limits, `minReadySeconds`, pause/resume; Recreate vs RollingUpdate; **digest-pinned images** (link M01/M02); StatefulSet identity (stable names, ordered rollout, headless Service, `volumeClaimTemplates`, `podManagementPolicy`, `updateStrategy` incl. partition); Job semantics (`completions`, `parallelism`, `backoffLimit`, `activeDeadlineSeconds`, `ttlSecondsAfterFinished`, indexed jobs `[VERIFY]`); CronJob (`schedule`, `timeZone` `[VERIFY]`, `concurrencyPolicy`, `startingDeadlineSeconds`, history limits).
- **L3:** safe rollout design and rollback criteria; failure modes (stuck rollouts, `ProgressDeadlineExceeded`, bad config, selector mismatch); StatefulSet pitfalls (PVC retention policy `[VERIFY]`, scaling down data-bearing replicas, partitioned canary, "operators exist because StatefulSets are not enough" — forward ref M05); Job idempotency, retry/backoff, `restartPolicy` differences, handling poison inputs, pod failure policy `[VERIFY]`; CronJob overlap/missed-schedule/duplicate-run hazards, suspend semantics; config and secret rollout (checksum annotations; ConfigMap immutability) at concept level; DaemonSet awareness.
- **L4:** progressive-delivery boundaries (what vanilla Deployments cannot do; forward ref M08); zero-downtime migration strategy including schema changes (expand/contract); standardized workload templates and manifest policy checks (kubeconform/kube-linter/kube-score-style linting, `[VERIFY]` current tools — Awareness-level); incident: "CronJob concurrency produced duplicate ETL loads."
- **Must include:** a lab with a failing rollout detected and rolled back, a StatefulSet partitioned update, and a CronJob with `Forbid` vs `Allow` concurrency demonstrated with timestamps.

## Unit 5 — Pod disruption budgets and graceful shutdown
- **L1:** voluntary vs involuntary disruptions; `kubectl drain/cordon/uncordon`; what a PDB protects and what it does not (it does not stop involuntary failures); pod termination sequence (SIGTERM, grace period, SIGKILL).
- **L2:** `PodDisruptionBudget` (`minAvailable` vs `maxUnavailable`, selectors, percentage semantics); `terminationGracePeriodSeconds`; `preStop` hooks; application SIGTERM handling in Python (FastAPI/uvicorn graceful shutdown, worker drain); exec-form `CMD` and PID 1 (link M01 Unit 8); the endpoint-removal vs SIGTERM race and the standard mitigation.
- **L3:** unhealthy-pod eviction policy `[VERIFY]`; PDB misconfigurations that **block node drains forever** (e.g., `minAvailable` = replicas; single-replica workloads); PDB for StatefulSets; interaction with HPA, rolling updates, node upgrades, and Cluster Autoscaler; topology spread to make PDBs meaningful; draining nodes with local storage/DaemonSets; connection draining and long-lived connections; Job/batch work and checkpoint-on-SIGTERM; spot/preemptible node termination (Awareness).
- **L4:** an organization-wide PDB policy (required for replicas > 1; policy-as-code check); measuring availability during a drain (error-rate SLI during maintenance); upgrade-window design; incident: "drain stuck for hours on one PDB" → diagnose → safe override procedure and its risk; graceful-shutdown test harness.
- **Must include:** a lab that drains a kind worker under load with (a) no PDB, (b) a correct PDB, (c) a blocking PDB, and records dropped requests and drain duration for each, plus a SIGTERM-handling lab proving zero dropped in-flight requests.

## Unit 6 — Horizontal and vertical autoscaling
- **L1:** why autoscale; Metrics Server; `kubectl top`; HPA concept and the scaling formula (desiredReplicas = ceil[currentReplicas × currentMetric / targetMetric]); HPA requires resource requests.
- **L2:** `autoscaling/v2` HPA with CPU/memory utilization targets; min/max replicas; `behavior` (stabilization windows, scale-up/down policies); load generation for testing; reading `kubectl describe hpa` conditions (`AbleToScale`, `ScalingActive`, `ScalingLimited`); why HPA shows `<unknown>`.
- **L3:** metric choice (CPU vs memory vs custom/external vs queue depth) and why memory is a poor scaling signal for many runtimes; custom/external metrics architecture (Prometheus Adapter, KEDA — Awareness, forward ref M11); thrash/flapping diagnosis and tuning; HPA + rolling update + PDB interplay; startup time and scale-up lag; VPA modes (Off/Initial/Recreate/Auto) and the HPA+VPA conflict on the same metric `[VERIFY]`; in-place pod resize `[VERSION-SENSITIVE]`; Cluster Autoscaler/Karpenter as Awareness (the pending-pod → new-node loop) with a local simulation of the *logic* (no real node provisioning in kind); scaling consumers on queue lag as design.
- **L4:** capacity-aware autoscaling design (headroom, overprovisioning pods, priority classes); autoscaling SLOs and cost/latency trade-offs (forward ref M15); load-test methodology that avoids misleading results; failure scenarios (metrics-server down, runaway scale to max, scale-to-min cold start, noisy metric); runbook; incident: "HPA scaled to max and exhausted cluster capacity, starving other namespaces" → quotas, priorities, max caps.
- **Must include:** a lab: install Metrics Server (kind needs the documented insecure-TLS kubelet flag workaround `[VERIFY]` — explain why it is acceptable only in a lab), load-test the API, watch scale-up and scale-down with `behavior` tuned, record replica-vs-load timeline, and fix a deliberately thrashing configuration. VPA taught in recommendation-only mode as an optional lab `[VERIFY]` install path.

## Unit 7 — Node pools, taints, affinity, workload placement
- **L1:** how the scheduler picks a node (filter → score → bind); `nodeSelector`; labels; node pools/groups as a cloud/operations concept (simulated on kind with labels).
- **L2:** taints and tolerations (effects NoSchedule/PreferNoSchedule/NoExecute); node affinity (required vs preferred); pod affinity/anti-affinity; `topologySpreadConstraints` (`maxSkew`, `whenUnsatisfiable`, topology keys); well-known labels (`topology.kubernetes.io/zone`, `kubernetes.io/hostname`); `kubectl describe pod` scheduling events (`FailedScheduling` messages decoded).
- **L3:** pool design for a data platform (system, general, memory-optimized, batch/spot-like, GPU — Awareness); dedicating nodes (taint + toleration + affinity together and why each alone is insufficient); spread vs anti-affinity trade-offs; `matchLabelKeys`/`nodeAffinityPolicy` `[VERSION-SENSITIVE]`; priority/preemption and descheduler (Awareness); scheduling interplay with requests, PDBs, autoscalers, and PVC zone binding (forward ref M05); DaemonSet tolerations; runtime classes/sandboxed pods (Awareness); resource-heavy ML/GPU scheduling (device plugins — Awareness).
- **L4:** failure-domain-aware design (zones/racks) with a clear note that kind has **no real zones** — simulate by labeling workers with fake zone labels and say so; bin-packing vs spreading cost/reliability analysis; placement policy-as-code (admission policy forcing tolerations/labels — Awareness via Kyverno/Gatekeeper); incident: "all replicas landed on one node and a single node loss took the service down"; migration of workloads between pools without downtime.
- **Must include:** a lab with labeled/tainted kind workers acting as "general", "batch", and "memory" pools; demonstrate a pending pod, decode the scheduler message, fix it, then prove replicas are spread and that `NoExecute` evicts a non-tolerating pod.

## Unit 8 — Cluster upgrades and version compatibility
- **L1:** Kubernetes release cadence and support window (state the **policy**, not numbers, and mark specifics `[VERIFY]`); semantic structure of versions; the **version skew policy** (apiserver/kubelet/kubectl/kube-proxy skew rules `[VERIFY]` exact bounds); deprecation vs removal; why skipping minors is unsafe.
- **L2:** upgrade order (control plane first, then nodes; one minor at a time); API deprecation detection (`kubectl convert`/`kubectl get --raw` deprecations metrics, `apiserver_requested_deprecated_apis` metric, scanners such as pluto/kubent — Awareness `[VERIFY]`); read release notes and the deprecation guide; addon compatibility matrix; pre-upgrade checklist; backups first (link Unit 10).
- **L3:** upgrade strategies: **in-place** (kubeadm flow: `kubeadm upgrade plan/apply`, drain → upgrade kubelet → uncordon — explain and inspect, `[VERIFY]` exact steps), **node-pool rotation/surge**, and **blue/green cluster** (the realistic kind approach: create a new-version cluster, migrate, cut over); managed-Kubernetes upgrade behavior as Awareness; workload readiness for upgrades (PDBs, probes, replicas > 1, topology spread — link Units 3, 5, 7); CNI/CSI/ingress/webhook/CRD version coupling; feature gates, alpha/beta/GA lifecycle; rollback realities (control-plane downgrades are generally unsupported — state and `[VERIFY]`; rollback = restore etcd or fall back to blue cluster).
- **L4:** fleet upgrade programs (canary clusters, ring deployment, upgrade SLO, automation, freeze windows); testing upgrades in CI with ephemeral kind clusters (link M02); end-of-life risk management; upgrade runbook with go/no-go criteria and abort points; incident: "removed API version broke the deployment pipeline after upgrade" and "admission webhook incompatible with new API server"; communicating maintenance.
- **Must include:** (1) a deprecation-scan lab against a manifest set containing a deliberately outdated API; (2) a **blue/green kind upgrade lab** from one supported minor to the next using placeholder tags and moving a workload; (3) an optional lab inspecting a `kubeadm upgrade plan` dry-run output inside a kind control-plane node, labeled **inspection only** if the in-place upgrade is not safely reproducible `[VERIFY]`.

## Unit 9 — Kubernetes RBAC and Pod Security Standards
- **L1:** authentication vs authorization vs admission; users/groups vs ServiceAccounts; `Role`/`ClusterRole`/`RoleBinding`/`ClusterRoleBinding`; verbs/resources/apiGroups; `kubectl auth can-i` (including `--as`).
- **L2:** least-privilege Roles for a developer, a CI deployer, and a read-only auditor; ServiceAccount per workload; `automountServiceAccountToken`; bound/short-lived tokens `[VERIFY]`; aggregation labels; why `cluster-admin` bindings and wildcards are dangerous; client-certificate users in kind for lab realism; Pod Security Admission: **Pod Security Standards** profiles (Privileged/Baseline/Restricted) and namespace labels (`enforce`/`audit`/`warn`, versions) `[VERIFY]` exact label keys; writing manifests that pass `restricted` (non-root, no privilege escalation, drop ALL capabilities, seccomp RuntimeDefault, read-only root fs as best practice — link M01 Unit 8).
- **L3:** RBAC privilege-escalation paths (`escalate`/`bind`/`impersonate`, `pods/exec`, reading secrets, creating pods as a path to node access, wildcard verbs) — explained defensively with local verification only; auditing RBAC (who can do X; `kubectl auth can-i --list`, `rbac-tool`/`kubectl-who-can`/`rakkess`-style tools — Awareness `[VERIFY]`); namespace-level PSS rollout strategy (audit/warn first, then enforce) and exemptions; `securityContext` at pod/container level; admission policy engines (Kyverno/Gatekeeper) as Awareness with one comparison table and one small policy example `[VERIFY]` syntax; ValidatingAdmissionPolicy (CEL) `[VERSION-SENSITIVE]`; service-account token and API-server exposure; secrets in etcd (encryption at rest concept; forward ref M09).
- **L4:** RBAC as code and review process; periodic access review automation; break-glass access with audit; multi-team RBAC model (platform, tenant, auditor); threat-model walk-through for a compromised pod (what RBAC/PSS stop and what they do not: network, node, supply chain); CIS Kubernetes Benchmark and NSA/CISA hardening guidance as reference frameworks with kube-bench-style scanning as Awareness; incident: "a CI ServiceAccount had cluster-wide secret read" → detect → revoke → rotate → prevent.
- **Must include:** a lab creating the three roles above, proving allowed/denied actions with `auth can-i`, enabling PSS `warn`→`enforce` on a namespace and fixing a non-compliant Deployment from the running example, and a deliberately over-permissive binding found by an audit script and corrected.

## Unit 10 — etcd health, backup, control-plane troubleshooting
- **L1:** what etcd stores (all cluster state) and why its loss = cluster loss; Raft, quorum, leader, members (concept with a diagram); why odd member counts; etcd is not an application database.
- **L2:** access etcd in kind via the control-plane container with `etcdctl` (endpoint, cert flags from the static-pod manifest `[VERIFY]`); `endpoint health`, `endpoint status`, `member list`; **snapshot save** and `snapshot status`; what a snapshot contains and does not contain (it does not contain PV data); storing snapshots off-node; secrets-in-snapshot sensitivity (encrypt and protect backups).
- **L3:** **restore procedure** (`etcdutl`/`etcdctl snapshot restore` — note which tool is current `[VERIFY]`; stop control plane, restore to a new data dir, repoint the static-pod manifest, restart) rehearsed in kind; consistency pitfalls (restored cluster state vs live reality: orphaned pods/nodes, controllers reconciling to stale desired state); etcd performance (disk latency/fsync, DB size quota, defrag, compaction, alarm `NOSPACE`, `etcd_*` metrics `[VERIFY]` names); control-plane troubleshooting (apiserver/scheduler/controller-manager logs via `crictl`/`docker exec` in kind, static-pod crash diagnosis, certificate expiry symptoms, clock skew, kubelet down vs API down, `kubectl` unreachable triage tree); backup cadence/retention/RPO reasoning.
- **L4:** quorum-loss scenarios and recovery; multi-member etcd recovery (Awareness with diagram; do not claim kind HA etcd reproduction unless configured — `[VERIFY]`); "restore vs rebuild-from-GitOps" decision framework (forward ref M08, M13); managed-service reality (you often cannot access etcd — what you do instead); DR game-day design (forward ref M13); monitoring and alerting rules for etcd (forward ref M11); incident: "snapshot restored and controllers deleted live workloads" → prevention steps.
- **Must include:** a **backup → destroy → restore** lab on kind with a verification script proving specific objects (a namespace, Deployment, ConfigMap) return, an explicit list of what did **not** return, and a restore-time measurement for the learner's own RTO note. Mark ⚠ DESTRUCTIVE steps and confine them to a named throwaway cluster after a context check.

## Unit 11 — Production cluster troubleshooting
- **L1:** the systematic method (observe → hypothesize → test → fix → verify → document); the `kubectl` triage toolkit (`get`, `describe`, `logs --previous`, `events --sort-by`, `top`, `exec`, `debug`, `port-forward`); reading pod status strings (`Pending`, `ContainerCreating`, `CrashLoopBackOff`, `ImagePullBackOff`, `OOMKilled`, `Evicted`, `Terminating`, `Error`, `Completed`).
- **L2:** decision trees for the top failure classes: scheduling (resources, taints, affinity, PVC binding), image pulls, config/secret missing, probe failures, OOM/limits, DNS and Service connectivity (basics; deep networking is M04), RBAC `Forbidden`, quota exceeded, admission denial; ephemeral debug containers (`kubectl debug`) for distroless images (link M01 Unit 2); node conditions (`MemoryPressure`, `DiskPressure`, `PIDPressure`, `NotReady`) and kubelet logs.
- **L3:** multi-symptom correlation; cluster-wide issues (CoreDNS, CNI, API latency, webhook timeouts, etcd slow); stuck `Terminating` pods/namespaces (finalizers, and why force-deleting is risky); node failure handling; evidence capture before remediation; blameless incident flow and timeline construction (forward ref M10); `must-gather`-style diagnostic bundle script; safe-change principles while debugging prod (read-only first, one change at a time, record commands).
- **L4:** troubleshooting at scale (labels/field selectors, `jq`/JSONPath queries across namespaces, audit-log use); chaos-style fault injection drills; building runbooks and diagnostic automation; post-incident review template; "debugging the debugger" (kubectl/API unavailable); pattern recognition table (symptom → most likely 3 causes → first command); on-call handoff quality.
- **Must include:** a **troubleshooting gauntlet** — at least **12 provided broken-scenario manifests** applied to a kind cluster (e.g., wrong image tag, missing ConfigMap, impossible node selector, unreachable PVC, failing readiness, OOM, quota exceeded, RBAC denial, selector mismatch, taint with no toleration, bad probe path, Service with no endpoints). Each has hidden-cause description, hints at three levels, a diagnosis rubric, the fix, and the prevention policy. Put solutions in clearly separated answer-key sections.

# 7. PRACTICE QUESTIONS (Unit 12)

At least **160 questions**: ≥ 12 per Units 1–11 plus ~25 cross-unit integration scenarios. Per unit:
- 3 × conceptual short-answer
- 3 × multiple choice (4 options; explain every distractor)
- 2 × output interpretation (given `kubectl describe`/`get`/events output, what is wrong?)
- 2 × manifest review (find ≥ 3 defects, fix them)
- 1 × incident/troubleshooting scenario (symptom → diagnose → fix → prevent)
- 1 × design question with a rubric

Each question: ID, level (L1–L4), objective tested, time estimate, **model answer**, **common wrong answers**. Include a scoring rubric (≥ 80% proceed; 60–79% remediate; < 60% repeat), and 10 "design-review" whiteboard prompts requiring written trade-off reasoning (e.g., single large cluster vs several; HA control plane sizing; PDB policy for a fleet; upgrade strategy; autoscaling signal selection). Questions must test only taught content.

# 8. CAPSTONE PROJECT (Unit 13)

**Project:** *Resilient Data Pipeline on Kubernetes.*

Deliver `Projects/README.md` (index, grading, evidence submission) and the full spec.

**Scenario:** A data team runs a model-scoring API, a queue consumer, a stateful dependency, an ETL Job, and a nightly CronJob on one shared cluster. Incidents so far: pods with no resource limits starved neighbors, a liveness probe restarted the whole API, a node drain took the API offline, a CronJob double-ran, HPA thrashed, a ServiceAccount with admin rights was committed to the repo, and nobody has ever restored etcd. The learner builds a production-grade, **locally verifiable** operating baseline.

**Required deliverables (each with acceptance criteria verifiable by command or inspection):**
1. `kind` multi-node cluster config (1 control plane, 3 workers) and a bootstrap script with context safety checks; versions recorded in `versions.txt`.
2. Namespaces per environment/tenant with `ResourceQuota`, `LimitRange`, and labels; measured right-sizing report.
3. Workloads: API Deployment, worker Deployment, StatefulSet dependency, ETL Job, CronJob — all digest-pinned (images from M01's local registry), non-root, resource-bounded, with correct probes (liveness/readiness/startup).
4. PDBs and graceful-shutdown behavior proven by a drain test with zero dropped requests (load-generator evidence).
5. HPA with tuned `behavior`, Metrics Server, load-test timeline; documented autoscaler limits and cost/capacity notes.
6. Placement: three simulated node pools via labels/taints, tolerations/affinity, topology spread; a verification script that asserts replica spread.
7. RBAC for developer / CI deployer / auditor roles, per-workload ServiceAccounts, PSS `restricted` enforcement on workload namespaces, and an RBAC audit script with output.
8. Upgrade readiness: deprecation scan of all manifests, a written go/no-go upgrade runbook, and a blue/green kind upgrade rehearsal log.
9. etcd backup script, off-node storage, restore rehearsal, verification script, and a measured recovery-time note.
10. A **chaos/game-day** script suite: kill pod, kill worker container, drain node, stop dependency, fill quota, remove toleration — each with expected vs observed outcomes recorded.
11. A conformance script (`make verify`) that checks every item above and prints a pass/fail report with evidence; `Makefile` with `up`, `deploy`, `verify`, `chaos`, `backup`, `restore-test`, `down`.
12. Documentation: architecture diagram, ≥ 5 ADRs, runbooks for 5 incident types (CrashLoopBackOff storm, stuck drain, quota block, HPA runaway, etcd restore), and a production-readiness review using the Unit 1–11 checklists.
13. A before/after results table (availability during drain, recovery time after node loss, scale-up time, restore RTO, resource waste, pods without limits) filled from the learner's **own** measurements. Provide the template; never fabricate results.

**Include:** 6–7 milestones with time estimates; a 100-point rubric (Poor/Adequate/Strong/Exemplary descriptors); stretch goals (admission policy, VPA recommendations, second kind cluster as DR target); common failure points; self-review checklist; exact evidence folder structure; a resource-budget note for running it all within 4 CPU / 8 GB.

**Provide complete, runnable starter code and manifests**: small realistic FastAPI API and worker, ETL job, all YAML, scripts, Makefile, and chaos/verify scripts. No `TODO: implement` in required deliverables. All credentials fake (`example-password-do-not-use`).

# 9. README ORIENTATION (Unit 0)

Include: purpose and audience; Gate In prerequisites (including M01/M02 outcomes consumed here); module dependency graph and why order matters; 6-week and 10-week pacing plans; tool matrix (Core vs Awareness) with install-verification commands; lab environment checklist (Docker resources, kind version, `kubectl` skew, ports, disk, WSL2 notes) and a **resource-budget guide** (what can run together within 8 GB); **kind-vs-production fidelity table** (what is real, simulated, or not reproducible); glossary; module-to-exit-criteria mapping; evidence rules; how to use the practice questions and project; table linking M03 to M01, M02, M04, M05, M06, M08–M15, M17; a **safety section** on kube-context hygiene, throwaway clusters, and never running lab commands against a real cluster.

# 10. CODE AND COMMAND RULES (NON-NEGOTIABLE)

1. Every code block names its language and, for files, a first-line path comment (e.g., `# File: manifests/api/deployment.yaml`).
2. Every command is paired with **representative expected output**, labelled "example — yours will differ", plus a short interpretation.
3. **Only real syntax.** Use apiVersions, kinds, fields, flags, and metric names you are confident exist. Anything that varies by Kubernetes version, distribution, or feature-gate state is tagged `[VERIFY: what/where]` or `[VERSION-SENSITIVE]`. State the API version used for every manifest (`apps/v1`, `autoscaling/v2`, `policy/v1`, `batch/v1`, `rbac.authorization.k8s.io/v1`…). Never guess.
4. **Context safety:** every lab begins with a context check (`kubectl config current-context`; assert it matches `kind-<name>`); destructive and cluster-wide commands are labelled `⚠ DESTRUCTIVE` with the target cluster named and a read-only or dry-run (`--dry-run=server`, `kubectl diff`) alternative first.
5. **Manifests must follow the standards taught:** pinned images (digest, with human-readable tag comment), resource requests/limits, probes, `securityContext` non-root + `allowPrivilegeEscalation: false` + `capabilities.drop: [ALL]` + `seccompProfile: RuntimeDefault`, explicit ServiceAccount, labels — unless the example is a deliberate anti-pattern labelled `# ANTI-PATTERN — DO NOT COPY` with the defect list and a fixed version beside it.
6. **No real secrets;** fake values only. No credentials in manifests beyond lab fakes; point to M09 for proper handling.
7. **Defensive security only:** RBAC/PSS escalation material is for understanding and auditing on the learner's own throwaway cluster; no attack tooling, no targeting of other systems.
8. **Scripts:** `set -euo pipefail`, quoted variables, explicit exit codes, context assertion, `--dry-run` where mutating, idempotent where possible. Python: typed where practical, minimal dependencies, with tests.
9. **Resource realism:** every lab states its approximate CPU/RAM/disk footprint and fits the 4 CPU / 8 GB baseline; do not require more than 3 worker nodes; tell the learner when to delete clusters to free resources.
10. **Every lab ends with cleanup** (delete namespaces/clusters created, remove kubeconfig contexts, stop port-forwards) and a verification that nothing stray remains.
11. **Every performance/capacity claim** is tied to a measurement command or labelled "typical range — measure yours". Never state a specific number (timeouts, limits, latencies, node capacity) as fact without `[VERIFY]` or a derivation.
12. Call out WSL2 vs native Linux differences (cgroup version, Docker resource limits, filesystem performance, DNS) where they alter lab outcomes.
13. Validate every manifest mentally against `kubectl apply --dry-run=server` semantics and schema before output; ensure selectors match template labels, ports/names are consistent, and cross-file references resolve.

# 11. PEDAGOGY RULES

- **Mechanism before recipe:** explain the reconciliation loop or component behind each command.
- **One running example** (data pipeline) evolving through the folder: naive → bounded → healthy → disruption-safe → autoscaled → placed → upgradable → secured → recoverable → diagnosable.
- **Show failure on purpose:** every unit includes at least one lab where the learner breaks something and diagnoses it using events/logs/describe.
- **Diagrams** for control-plane request flow, Raft/quorum, QoS eviction order, rollout state, pod termination timeline, HPA control loop, scheduler filter/score, upgrade ordering, RBAC graph, and the etcd backup/restore sequence.
- Plain, precise English; no filler or marketing; define acronyms at first use; consistent terms (*cluster, node, pod, workload, controller, reconciliation, desired vs observed state, disruption, drain*).
- Honest trade-offs; avoid "always/never" without reasons and exceptions.

# 12. AUTHENTICITY, AUDIT, AND VERIFICATION PROTOCOL (MANDATORY)

**All learning content must be audited and verified before final submission.** You act as author first, then as an independent auditor of your own work, and you include the audit evidence in the deliverable.

## 12.1 Authoring-time rules
- Base technical claims on **official documentation and specifications**: Kubernetes documentation (concepts, tasks, reference, API reference, release notes, version-skew and deprecation policies), the kind documentation, etcd documentation (operations guide, disaster recovery), Metrics Server docs, kubeadm docs, CIS Kubernetes Benchmark, NSA/CISA Kubernetes Hardening Guidance, Kubernetes Pod Security Standards, and SRE sources (Google SRE Book/Workbook) for operations principles. Cite by **document name and section/title**, not invented URLs; give a URL only if certain it is canonical, else mark `[VERIFY]`.
- **Do not fabricate:** Kubernetes versions or support dates, API fields, metric names, flag names, default values, quotas, timings, statistics, benchmark results, CVE IDs, quotes, or tool behaviors. Derive numbers from stated commands or label `[ILLUSTRATIVE]`.
- Mark uncertainty with `[VERIFY]`, `[ILLUSTRATIVE]`, `[VERSION-SENSITIVE]`, or `[ASSUMPTION]`.
- Keep a running **Claim Register** for every non-trivial factual claim.

## 12.2 Mandatory multi-pass self-audit (before delivering each part)

| Pass | Name | What you check | Fail condition |
|---|---|---|---|
| 1 | **Completeness** | All 14 units, all Section 5 sections, all Section 6 topics, L1–L4. | Any gap. |
| 2 | **Technical accuracy** | Every apiVersion/kind/field/flag/command is real and correctly used; mentally execute each lab against current Kubernetes behavior. | Invented or misused syntax/behavior. |
| 3 | **Executability** | YAML is valid and internally consistent (selectors, names, ports, namespaces); scripts would pass ShellCheck; labs have steps, evidence, cleanup; manifests would pass server-side dry-run. | Broken or ambiguous step. |
| 4 | **Currency** | Version-sensitive items tagged; no removed/deprecated API taught as current (e.g., `policy/v1beta1` PSP/PDB, `extensions/v1beta1`, PodSecurityPolicy, `autoscaling/v1` as the default, `kubectl run` generators); no cloud-provider assumptions. | Stale or untagged claim. |
| 5 | **Security correctness** | No insecure practice presented as good; no overclaims (namespaces ≠ isolation; PSS ≠ full container security; RBAC ≠ network security; an etcd snapshot ≠ a full backup; kind insecure-kubelet-TLS workaround ≠ production practice; PDB ≠ protection from failures). | Overclaim or unlabeled insecure example. |
| 6 | **Fabrication scan** | Hunt for invented numbers, versions, citations, metric names, outputs presented as measured. | Any unsupported specific. |
| 7 | **Pedagogical consistency** | True beginner→advanced ramp; no concept used before introduced; consistent terms; running example evolves coherently. | Undisclosed forward dependency; drift. |
| 8 | **Cross-consistency** | Questions test only taught content; capstone deliverables map to units; checklists match lessons; README matches content; the kind-fidelity table matches every lab caveat. | Orphan item; contradiction. |
| 9 | **Adversarial review** | As a skeptical staff SRE: list the 10 most likely objections ("what would break or mislead on a real production cluster?") and resolve each. | Unresolved objection. |
| 10 | **Lab safety & feasibility** | Labs run on kind within 4 CPU / 8 GB / 30 GB, are idempotent and context-guarded, never touch a non-lab cluster, avoid paid resources, and clean up. | Hidden cost, resource blowout, wrong-cluster risk, leftover state. |

## 12.3 Audit artifacts inside the syllabus (final appendices)

**Appendix A — Claim Register:** `ID | Unit | Claim | Source (document + section) | Confidence (High/Med/Low) | Tag`. ≥ **80 entries**, covering every version-sensitive and security-relevant claim.

**Appendix B — Audit Report:** `Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk` for passes 1–10. Be candid; report real defects.

**Appendix C — Human Verification Checklist:** every `[VERIFY]` / `[VERSION-SENSITIVE]` item grouped by component (kube-apiserver/API versions, scheduler, kubelet, kubeadm, kind, Metrics Server/HPA/VPA, PDB, PSA/PSS, RBAC, etcd/etcdctl/etcdutl, CronJob/Job fields, version-skew policy), each with *what to check*, *where (official doc name)*, *how to test with one command*. Closable by a reviewer in under 5 hours.

**Appendix D — Known Limitations and Assumptions:** what is out of scope (managed-cloud specifics, service mesh, CSI internals, GitOps), assumed Kubernetes/kind versions, kind fidelity limits, WSL2 caveats, anything unverified.

**Appendix E — Sign-off block:** `Content status: DRAFT-AUDITED | Audit date | Auditor: AI self-audit (requires human verification) | Unverified items count`. State plainly that AI self-audit does not replace a human running the labs on a real kind cluster.

## 12.4 Trust rules
- If a pass finds a defect you cannot confidently fix, leave it visible as `OPEN` in Appendix B and list it in Appendix C. Never hide uncertainty.
- Never claim a command or manifest "was run/tested" unless it actually was. Use "expected output (representative)".
- Never claim verification against live documentation unless you consulted it; otherwise say "written from knowledge of the documentation; verify against current docs".

# 13. OUTPUT FORMAT

- **One Markdown document:** `SYLLABUS-Production-Kubernetes-Operations.md`.
- Begin with: title, abstract paragraph, metadata block (`Module: M03`, `Stage: 2E`, `Estimated total time`, `Last reviewed`, `Assumed tool baseline`), and a **linked table of contents** to all units and appendices.
- Then Units 0–13 in order, then Appendices A–E.
- Headings: `#` title, `##` units, `###`/`####` below; tables for comparisons; fenced code with language tags; mermaid for diagrams.
- Cross-link units with relative links to sibling target files.
- **Depth target:** Units 1–11 each ≥ 2,500 words of teaching text excluding code and manifests; ≥ 160 practice questions; capstone with complete code. **Do not compress to fit**—use the Delivery Protocol.
- No placeholder text, no "etc." in required lists, no "exercise left to the reader" for required deliverables.

# 14. DELIVERY PROTOCOL

Deliver in **numbered parts**; wait for the user to type `continue` between parts.

| Part | Content |
|---|---|
| 1 | Title, abstract, metadata, TOC, Unit 0, Unit 1 |
| 2 | Units 2, 3 |
| 3 | Units 4, 5 |
| 4 | Units 6, 7 |
| 5 | Units 8, 9 |
| 6 | Units 10, 11 |
| 7 | Unit 12 (practice questions) |
| 8 | Unit 13 (capstone, full code) |
| 9 | Appendices A–E, including the cross-part audit |

Rules:
- End each part with: `PART n/9 COMPLETE — units delivered: …; open [VERIFY] items so far: <count>; next: Part n+1`.
- Run the per-unit audit (passes 1–10, scoped) **before** printing each part; maintain the Claim Register throughout.
- Part 9 runs the cross-part audit (passes 7, 8, 9 especially) and lists every correction to earlier parts as `CORRECTION: Part n, Unit x, section y — old → new`.
- Never summarize a unit to save space. If nearing the length limit, stop at a clean section boundary, print `TRUNCATED AT: <unit/section>`, and resume exactly there on `continue`.
- After Part 9 print: "Concatenate Parts 1–9 in order into `SYLLABUS-Production-Kubernetes-Operations.md` and apply all listed corrections."

# 15. DEFINITION OF DONE

- [ ] All 14 units present in order; Units 1–11 each have L1–L4 and sections N.0–N.14.
- [ ] Every Section 6 topic taught at its stated level, with every kind-simulation limit stated honestly.
- [ ] ≥ 160 practice questions with model answers and distractor analysis.
- [ ] Capstone has complete runnable code, acceptance criteria, rubric, chaos suite, `make verify`, and a blank measurement template.
- [ ] Every lab has context guard, steps, expected evidence, cleanup; all fit the local baseline.
- [ ] No fabricated versions, fields, metrics, numbers, or citations; every uncertainty tagged.
- [ ] Appendices A–E present; Claim Register ≥ 80; passes 1–10 reported candidly.
- [ ] Running example evolves coherently across all units.
- [ ] Forward references (M01, M02, M04–M06, M08–M15, M17) explicit and not half-taught.
- [ ] A human can close every open item in under 5 hours using Appendix C.

# 16. START

Confirm in **one line** that you understand the task, then immediately begin **Part 1/9**. Do not ask clarifying questions; record an `[ASSUMPTION]` where information is missing and proceed.

=== END PROMPT ===

---

## Notes for the human operator (not part of the prompt)

1. Use one long conversation across all 9 parts so the Claim Register and running example stay consistent.
2. AI self-audit is not independent. Run the labs on a real kind cluster and close every `[VERIFY]` item against current Kubernetes docs.
3. Highest fabrication risk, check first: the version-skew bounds, the kind node image tags, the Metrics Server flag workaround for kind, `etcdctl` versus `etcdutl` restore syntax and certificate paths, PSS label keys, API versions in the manifests (especially HPA `behavior`, PDB `unhealthyPodEvictionPolicy`, CronJob `timeZone`, Job pod failure policy), and any in-place resize or ValidatingAdmissionPolicy claims.
4. Always confirm `kubectl config current-context` before any lab. The prompt forces this, but you should too.
5. Some Unit 8 and Unit 10 labs (in-place upgrade, multi-member etcd recovery) may not reproduce cleanly on kind. The prompt tells the LLM to label those as inspection-only or Awareness instead of faking them.
