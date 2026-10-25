# Namespaces, Resource Quotas, and Limit Ranges

**Module:** Stage 2E — Production DevOps & Platform Engineering / M03  
**Unit:** 2  
**Target file:** `02-namespaces-resource-quotas-and-limit-ranges.md`  
**Estimated time:** 12–16 hours, including labs, evidence capture, and review  
**Prerequisites:** Stages 0–2D; M01 container image engineering; M02 CI/CD; M03 Unit 1 cluster architecture; Linux, Git, Docker, basic Pods and Deployments  
**Core tools:** `kind`, `kubectl`, Metrics Server, shell, Python 3 for the optional audit script  
**Awareness topics:** Hierarchical namespaces, Capsule, vcluster, PriorityClass/preemption, namespace vending, showback/chargeback  
**Last reviewed:** 2026-10-25; not live-verified against official documentation in this authoring pass  
**Kubernetes baseline assumed:** Use a currently supported Kubernetes minor compatible with the installed `kind` release and node image. **[VERIFY]** Kubernetes version/skew policy, kind node-image compatibility, API fields, and Metrics Server compatibility before lab execution.

> **Safety and evidence rule:** All output examples in this lesson are illustrative. No cluster, manifest, script, or lab was executed to author this file. Do not run mutation commands against a production or shared context. The suggested evidence directory is learner-created; this lesson does not create repository files.

## 1. Why This Matters in Production

A multi-tenant data platform rarely fails because a manifest is syntactically invalid alone. It can fail because one team consumes the available memory, a batch job competes with a latency-sensitive scoring API, a quota blocks a rollout, or a namespace has inconsistent resource defaults. These are resource-governance failures: the platform permits workloads to compete without enough explicit policy, or applies policy that does not match actual demand.

Namespaces, `ResourceQuota`, and `LimitRange` provide useful governance primitives, but they solve different problems. A namespace groups namespaced API objects. A quota limits what can be admitted in a namespace for configured resource dimensions. A LimitRange can default or constrain resource settings for supported objects. None creates physical CPU or memory, guarantees a workload can be scheduled, or makes a namespace a complete security boundary.

The operational skill is to separate five stages:

1. **Desired state:** a workload manifest describes what the team wants.
2. **Admission-time defaulting and validation:** API admission may add defaults or reject the object based on LimitRange, quota, policy, or other constraints.
3. **Scheduling-time decisions:** the scheduler uses resource requests and placement constraints to choose a node; it does not reserve a private pool of physical capacity just because quota exists.
4. **Runtime enforcement:** the kubelet and container runtime rely on operating-system mechanisms such as cgroups to enforce applicable CPU and memory constraints.
5. **Node-pressure response:** when a node is under pressure, kubelet eviction decisions can terminate Pods based on several factors, including usage relative to requests, Pod priority, and QoS-related considerations.

Confusing these stages causes bad incident response. A `FailedCreate` quota error is not fixed by changing node affinity. A `Pending` Pod caused by insufficient allocatable CPU is not fixed by increasing namespace quota. `OOMKilled` is not the same event as kubelet eviction. CPU throttling may cause latency without a restart.

### Running example

This unit uses a small multi-tenant data platform:

- a model-scoring API serving interactive requests;
- a queue worker consuming background tasks;
- a stateful dependency, represented only as a governance example;
- a batch ETL `Job`;
- a scheduled refresh `CronJob`.

The lesson governs namespaces and resources rather than implementing these services. M01 covers image construction and non-root execution; M02 covers CI/CD; M03 Unit 1 covers cluster architecture. Unit 3 covers probes/recovery, Unit 4 workload controllers, Unit 6 autoscaling, Unit 7 placement, Unit 9 RBAC/Pod Security Standards, M05 storage internals, M10 SRE/incident management, M11 observability, M15 capacity/FinOps, and M16 platform automation. Forward references identify ownership boundaries; they do not imply those later topics are fully taught here.

## 2. Learning Objectives

By the end of this unit, you should be able to:

- Explain namespace scope and distinguish it from authorization, admission, network isolation, and infrastructure failure-domain boundaries.
- Read and design requests and limits without conflating their roles.
- Explain why CPU can be throttled while memory overuse can lead to an OOM kill.
- Verify whether Metrics Server and the metrics API are working, and interpret `kubectl top` as sampled current usage rather than historical profiling.
- Design a `ResourceQuota` for compute resources and selected object counts, and explain the limits of storage quota examples.
- Use `LimitRange` defaults, minimums, maximums, and `maxLimitRequestRatio` where applicable.
- Diagnose quota and LimitRange admission failures separately from scheduling failures and runtime failures.
- Predict `Guaranteed`, `Burstable`, and `BestEffort` QoS from effective resource settings, while understanding eviction nuance.
- Develop a measurement-first right-sizing proposal using representative load and appropriate time windows.
- Defend a CPU-limit policy for a latency-sensitive API versus a batch workload, and explain memory-limit trade-offs.
- Explain JVM heap/native memory and Python/pandas interpreter overhead, temporary allocations, and data copies without inventing universal overhead percentages.
- Distinguish node capacity from node allocatable and explain `system-reserved` and `kube-reserved`.
- Evaluate namespace tenancy strategies, PriorityClass/preemption fundamentals, and multi-tenant fairness.
- Run a read-only audit of selected workload resource settings and state what the audit cannot prove.
- Respond to a quota-blocked critical rollout through an authorized, temporary, auditable procedure.
- Capture reproducible evidence and explicitly identify uncertainties and version-sensitive behavior.

## 3. Prerequisites and Scope Boundaries

### Required prerequisites

1. `kubectl config current-context`, `kubectl get`, `kubectl describe`, and basic YAML reading.
2. Deployment, Pod, Job, and CronJob concepts at an introductory level.
3. Container image/resource basics from M01 and CI/CD hand-off from M02.
4. Safe handling of contexts and credentials.
5. A working `kind` installation, compatible container runtime, and enough local capacity to run a small cluster.

### Scope boundaries

This lesson does not teach complete RBAC, Pod Security Standards, NetworkPolicy, storage provisioning, HPA/VPA configuration, node placement, autoscaler operation, or a full FinOps platform. It explains how resource governance interacts with those areas and tells you where to continue.

- A namespace is not an automatic network boundary. NetworkPolicy enforcement depends on the installed networking implementation and policy configuration.
- A quota is admission accounting, not a reservation of node resources.
- A LimitRange is not a replacement for explicit, reviewed workload resource declarations.
- `kubectl top` is not a historical metrics store and does not show all relevant runtime counters.
- kind is a useful local learning environment, not proof of production capacity, independent failure domains, or reliable node-pressure behavior.
- A short lab is not statistically sufficient to establish production p95/p99 sizing.
- A self-audit does not replace tests, policy review, or human approval.

## 4. Concept Map and Vocabulary

| Term | Meaning | Do not confuse it with |
|---|---|---|
| Namespace | Logical scope for namespaced API objects and names | VM, node, network, or complete security boundary |
| Resource request | Declared resource amount used by scheduling and relevant resource accounting | Guaranteed exclusive physical capacity |
| Resource limit | Runtime constraint for supported resource types | Scheduler reservation |
| `ResourceQuota` | Admission/accounting constraint for configured namespace resource dimensions | Physical capacity or a workload SLO |
| `LimitRange` | Namespace policy for defaults and minimum/maximum/ratio constraints on supported objects | Complete workload policy engine |
| QoS class | Kubernetes classification based on effective Pod resource configuration | A complete ranking of all eviction outcomes |
| `OOMKilled` | Container termination status commonly associated with an out-of-memory kill | Kubelet eviction |
| Eviction | Kubelet termination of a Pod to reclaim node resources under relevant conditions | A container reaching its memory limit |
| CPU throttling | Runtime/kernel limits CPU execution time under CPU quota controls | A restart or OOM event |
| Node capacity | Total capacity advertised by a node | Capacity available to Pods |
| Node allocatable | Capacity Kubernetes makes available for Pods after applicable reservations/overhead | Total machine capacity |
| Overcommit | Policy allowing declared demands to exceed a simple capacity sum under assumptions | A guarantee that all demands peak together safely |
| Metrics Server | Aggregates resource usage for the Kubernetes resource metrics API | Long-term time-series monitoring |
| PriorityClass | Cluster-scoped class assigning priority to Pods | A reservation or guarantee of capacity |
| Preemption | Scheduler mechanism that may remove lower-priority Pods to make room for a higher-priority Pod | Universal emergency capacity or instant recovery |
| Governance label | Metadata for ownership, environment, cost attribution, and automation | Enforcement unless a controller/policy consumes it |

### Conceptual request and enforcement path

```text
Pod / Deployment manifest
        |
        v
API request: authentication -> authorization -> admission/defaulting/validation
        |
        +--> applicable LimitRange defaults/constraints
        +--> ResourceQuota accounting/admission
        +--> other admission plugins/policies/webhooks
        |
        v
Accepted object persisted (acceptance != runnable)
        |
        v
Scheduler evaluates requests + constraints and binds a node
        |
        v
Kubelet / runtime / OS cgroups enforce applicable runtime limits
        |
        +--> sampled usage via Metrics Server (if installed and healthy)
        +--> container OOM termination when memory constraints are exceeded
        +--> kubelet node-pressure eviction when pressure criteria apply
```

This is a **conceptual** sequence, not a claim that every admission plugin is always invoked in this exact order for every request. **[VERIFY]** consult the documentation for the selected Kubernetes release and any installed admission webhooks. The important distinction is that admission, scheduling, runtime enforcement, and node-pressure response are different mechanisms.

## 5. Level 1 — Beginner: Namespaces and Resource Fundamentals

### 5.1 What a namespace does

Namespaces partition names for namespaced resources such as Pods, Deployments, Services, ConfigMaps, and Secrets. Two namespaces can each contain a Service named `scoring-api` without a name collision. Namespace names are cluster-scoped and should be treated as stable identifiers.

Not every Kubernetes resource is namespaced. Nodes, PersistentVolumes, StorageClasses, and PriorityClasses are examples of cluster-scoped resources. Discover scope instead of guessing:

```bash
kubectl api-resources
kubectl api-resources --namespaced=true
kubectl api-resources --namespaced=false
```

**Purpose:** inspect which resources are namespaced or cluster-scoped.  
**Prerequisite:** valid API access; read permission to discovery information.  
**Example — yours will differ:**
```text
NAME        SHORTNAMES   APIVERSION   NAMESPACED   KIND
pods        po           v1           true         Pod
nodes       no           v1           false        Node
```
**Interpretation:** this is representative output shape, not observed output. API discovery and installed extensions may differ by cluster.

### 5.2 Naming and governance labels

Use names that encode a stable purpose without overloading the name with every changeable attribute. Example convention:

- namespace: `team-forecast-prod`;
- `platform.example.com/team: forecast`;
- `platform.example.com/environment: production`;
- `platform.example.com/owner: forecasting-platform`;
- `platform.example.com/cost-center: cc-042`.

The domain `platform.example.com` is illustrative; replace it with an organization-controlled label prefix. Labels support selection, reporting, policy matching, and automation only when a consumer uses them. A label is not enforcement by itself.

**Path comment — learner lab file:** `# Save as: labs/m03-u02/namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team-forecast-lab
  labels:
    platform.example.com/team: forecast
    platform.example.com/environment: lab
    platform.example.com/owner: forecasting-platform
    app.kubernetes.io/part-of: data-platform
```

Apply only in the disposable cluster after the lab context guard. Namespace creation is a cluster-level mutation and typically requires appropriate permission.

```bash
kubectl get namespaces --show-labels
kubectl get namespace team-forecast-lab -o yaml
```

**Purpose:** verify creation and metadata.  
**Example — yours will differ:**
```text
NAME                STATUS   AGE
team-forecast-lab   Active   12s
```
**Interpretation:** `Active` means the namespace is present and not terminating; it does not prove the namespace is secure, isolated, or governed correctly.

### 5.3 What namespaces do not isolate

| Concern | Namespace alone? | Additional control to evaluate |
|---|---|---|
| Name collisions for namespaced resources | Yes, within namespace scope | Naming conventions for clarity |
| Who can read/update objects | No | Authentication, RBAC authorization, admission policy |
| Pod-to-Pod network reachability | No | NetworkPolicy plus a supporting CNI implementation |
| Node/kernel/runtime boundary | No | Node isolation, runtime hardening, workload trust model |
| Resource consumption | Not by itself | Requests/limits, quota, LimitRange, capacity policy |
| Cluster-scoped resources | No | Cluster-level permissions and governance |
| Secret access | No automatic isolation beyond API authorization and configured controls | RBAC, secret handling, encryption and identity controls |
| Independent failure domain | No | Separate nodes/clusters/regions where justified |

**Production use:** namespaces are a useful tenancy and ownership unit when paired with access controls, network policy, workload security controls, quotas, and a defined lifecycle.

**Anti-pattern — DO NOT COPY:** “Every team has a namespace, so workloads are isolated.”  
**Defect:** namespace boundaries do not alone prevent cross-namespace network traffic or excessive permissions.  
**Correction:** define the trust boundary; review RBAC, admission, Pod security, network policy, resource governance, and node access separately.

### 5.4 Requests versus limits

A **request** is the amount used by the scheduler when evaluating whether a Pod fits on a node. It also informs resource-management behavior and some eviction decisions. A **limit** is a runtime constraint for supported resources, enforced through node/runtime mechanisms. A request does not mean a process permanently receives that amount exclusively, and a limit does not reserve that amount on a node.

| Dimension | CPU | Memory |
|---|---|---|
| Request | Used for scheduling; affects relative placement/capacity accounting | Used for scheduling; informs pressure/eviction reasoning |
| Limit | CPU execution can be throttled under the configured limit | Exceeding the container memory limit can cause an OOM kill |
| Compressibility | CPU is generally compressible: less CPU time slows work | Memory is effectively non-compressible from scheduler perspective; pages cannot simply be throttled like CPU time |
| Typical symptom | Higher latency, slower throughput, throttling | OOM termination, restart, or node pressure if broader memory exhaustion occurs |
| Caveat | CPU shares/weights and enforcement details depend on runtime/kernel configuration | Actual memory accounting includes more than language-level heap estimates |

Kubernetes quantity examples: `100m` CPU means one tenth of a CPU unit; `500m` means half a CPU unit. Memory quantities such as `128Mi` are binary mebibytes. Use explicit units and do not mix decimal and binary assumptions casually.

**Path comment — learner lab file:** `# Save as: labs/m03-u02/pod-resources.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
  namespace: team-forecast-lab
  labels:
    app.kubernetes.io/name: resource-demo
spec:
  containers:
    - name: pause
      image: registry.k8s.io/pause:3.10
      resources:
        requests:
          cpu: "100m"
          memory: "64Mi"
        limits:
          cpu: "250m"
          memory: "128Mi"
```

**[VERIFY]** Confirm the selected image tag and cluster compatibility before applying. These values are `[ILLUSTRATIVE]`, not production sizing guidance.

### 5.5 `kubectl top` and Metrics Server

`kubectl top` queries the Kubernetes resource metrics API, commonly served by Metrics Server. It provides sampled current usage suitable for basic troubleshooting and autoscaling inputs; it is not a complete historical time series, a profiler, or a guarantee of peak memory/CPU.

Verify the installation and API:

```bash
kubectl get deployment metrics-server -n kube-system
kubectl get apiservice v1beta1.metrics.k8s.io
kubectl top nodes
kubectl top pods -n team-forecast-lab
```

**Purpose:** check deployment presence, API registration, node metrics, and namespace Pod metrics.  
**Prerequisites:** context access and a functioning Metrics Server compatible with the cluster; permissions to read metrics.  
**Example — yours will differ:**
```text
NAME             CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
kind-worker      125m         6%     780Mi           20%
```
**Interpretation:** illustrative only. If `kubectl top` returns an error, do not interpret it as zero usage. Investigate API registration, Metrics Server logs, kubelet reachability/TLS/configuration, and version compatibility. **[VERIFY]** use official Metrics Server installation requirements and the Kubernetes metrics API docs. Avoid blindly applying an old installation manifest or disabling TLS verification to “make it work.”

### 5.6 Beginner mistakes table

| Symptom | Likely cause | Verification | Correction |
|---|---|---|---|
| Two teams both use `default` | Namespace convention is not established | `kubectl get pods -A` | Create owned namespaces and explicit deployment targets |
| Pod is `Pending` | Requests cannot fit or another constraint blocks placement | `kubectl describe pod` and events | Diagnose scheduler constraints/capacity; quota alone is not the cause |
| `kubectl top` says metrics unavailable | Metrics API/Server missing or unhealthy | `kubectl get apiservice v1beta1.metrics.k8s.io` | Fix compatible Metrics Server setup; do not assume usage is zero |
| CPU-heavy process is slow but not restarting | CPU throttling or contention | Inspect limit, usage and available runtime metrics | Measure latency and throttling; review CPU policy |
| Container shows `OOMKilled` | Memory limit or broader memory exhaustion may be involved | Pod status, previous logs, events, node condition | Determine container OOM versus node pressure before changing values |
| Quota is raised but Pod stays Pending | No schedulable node capacity or another constraint | `describe pod`, node allocatable/requests | Capacity/placement remediation; quota does not create capacity |
| Namespace has labels but no policy effect | Labels have no enforcing consumer | Inspect policies/controllers | Connect labels to reviewed policy or reporting automation |

## 6. Level 2 — Intermediate: Quotas, Limit Ranges, and QoS

### 6.1 `ResourceQuota`

A `ResourceQuota` constrains aggregate consumption or object counts for a namespace. Common compute keys include `requests.cpu`, `requests.memory`, `limits.cpu`, and `limits.memory`. Object-count quotas may use forms such as `pods`, `services`, `secrets`, `configmaps`, and resource-specific count keys. Storage-related quota keys can include `requests.storage` and per-StorageClass variants, but behavior depends on relevant APIs and storage-class naming; storage internals belong to M05.

A quota may reject a create/update request at admission. It does not guarantee node capacity, balance workloads across nodes, or reserve a private pool. Quota dimensions must be selected to match governance objectives: CPU/memory request and limit ceilings, object counts, and storage request accounting are distinct concerns.

**Path comment — learner lab file:** `# Save as: labs/m03-u02/resourcequota.yaml`

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: forecast-budget
  namespace: team-forecast-lab
spec:
  hard:
    requests.cpu: "1"
    requests.memory: "1Gi"
    limits.cpu: "2"
    limits.memory: "2Gi"
    pods: "10"
    configmaps: "20"
    secrets: "20"
```

Values are `[ILLUSTRATIVE]`. Apply only after creating the namespace and verifying context. Do not add storage-class-specific keys until the actual storage class and supported quota key are verified.

```bash
kubectl describe resourcequota forecast-budget -n team-forecast-lab
kubectl get resourcequota -n team-forecast-lab -o yaml
```

**Purpose:** inspect configured hard limits and current usage.  
**Prerequisite:** read access to quota objects.  
**Example — yours will differ:**
```text
Resource            Used   Hard
requests.cpu        200m   1
requests.memory     128Mi  1Gi
pods                1      10
```
**Interpretation:** values are illustrative. `Used` and `Hard` represent quota accounting for the listed dimensions, not actual physical capacity or a guarantee of future scheduling.

### 6.2 `LimitRange`

A `LimitRange` can set default requests/limits for supported container/Pod resource dimensions and can validate minimums, maximums, and limit-to-request ratios. It is often used to prevent tiny or enormous per-container declarations and to supply defaults when a workload omits fields.

**Path comment — learner lab file:** `# Save as: labs/m03-u02/limitrange.yaml`

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: forecast-container-policy
  namespace: team-forecast-lab
spec:
  limits:
    - type: Container
      default:
        cpu: "250m"
        memory: "256Mi"
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      min:
        cpu: "50m"
        memory: "64Mi"
      max:
        cpu: "1"
        memory: "1Gi"
      maxLimitRequestRatio:
        cpu: "4"
        memory: "2"
```

These values are `[ILLUSTRATIVE]`. Verify supported fields and exact defaulting/validation behavior against the selected Kubernetes API version. LimitRange constraints are admission-time policy; they do not make a container’s actual memory use stay under the default.

```bash
kubectl describe limitrange forecast-container-policy -n team-forecast-lab
kubectl get limitrange -n team-forecast-lab -o yaml
```

**Purpose:** inspect defaults and constraints.  
**Example — yours will differ:**
```text
Type       Resource  Min   Max   Default Request  Default Limit
Container  cpu       50m   1     100m             250m
Container  memory    64Mi  1Gi   128Mi            256Mi
```
**Interpretation:** representative output only; actual formatting may differ. Verify the object itself for the authoritative values.

### 6.3 Quota and LimitRange interaction

These objects have complementary roles:

- LimitRange can default omitted resource fields and validate per-container or per-Pod constraints where supported.
- ResourceQuota tracks namespace-wide totals and may reject a request when the hard budget would be exceeded.
- A request that omits resources may be defaulted by applicable policy, but exact behavior depends on object type, policy, and API version.
- If quota tracks a resource dimension, a workload may need to specify the corresponding requests/limits or receive suitable defaults; otherwise admission may reject the request.
- A LimitRange default can change effective resource settings, QoS class, and quota accounting compared with the manifest as authored.
- A manifest accepted by admission can still remain Pending if no node fits.

**Bad example — ANTI-PATTERN — DO NOT COPY**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: too-large
  namespace: team-forecast-lab
spec:
  containers:
    - name: pause
      image: registry.k8s.io/pause:3.10
      resources:
        requests:
          cpu: "2"
          memory: "2Gi"
```

**Defect:** request values exceed the illustrative LimitRange maximum and namespace quota budget. This should be rejected by applicable admission validation, but exact error text and the first reported constraint depend on current usage and implementation.  
**Correction:** choose values within the namespace budget and per-container bounds, and verify that aggregate totals still fit.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: within-budget
  namespace: team-forecast-lab
spec:
  containers:
    - name: pause
      image: registry.k8s.io/pause:3.10
      resources:
        requests:
          cpu: "100m"
          memory: "128Mi"
        limits:
          cpu: "250m"
          memory: "256Mi"
```

This corrected example is accepted **in principle** if the namespace exists, the image is available, quota has remaining budget, the LimitRange policy matches the example, and no other admission policy rejects it. Do not claim acceptance until you test it in the disposable cluster.

### 6.4 Object counts and storage-related quotas

Object-count quotas can prevent uncontrolled creation of objects such as Pods, Services, ConfigMaps, and Secrets. They can protect the API/control plane and constrain accidental object storms, but they need capacity-appropriate values and operational exceptions. They do not prevent all API abuse and do not replace RBAC.

Storage-related quota can limit aggregate requested storage and, where supported, per-StorageClass requests or PVC counts. **[VERIFY]** exact keys and semantics in the ResourceQuota documentation/API reference for the chosen release and storage setup. A storage quota generally accounts for requests, not a universal measure of bytes actually written by every volume. M05 covers PV/PVC/CSI semantics.

### 6.5 QoS classes

Kubernetes classifies Pods as `Guaranteed`, `Burstable`, or `BestEffort` based on the effective CPU/memory requests and limits of all containers (and applicable init/sidecar behavior, depending on release). Inspect the actual Pod spec/status rather than inferring from a Deployment template alone.

| QoS | Simplified resource condition | Operational meaning |
|---|---|---|
| `Guaranteed` | Every relevant container has CPU and memory requests equal to limits, with required fields present | More predictable declared envelope; may reduce flexibility and raise scheduling reservation |
| `Burstable` | Not Guaranteed and at least one relevant request/limit is set | Mix of explicit and potentially flexible resource settings |
| `BestEffort` | No CPU or memory requests/limits for relevant containers | Least explicit protection against resource contention; generally risky for critical workloads |

The exact criteria have edge cases; **[VERIFY]** the official Pod QoS page for the selected version. LimitRange defaults may cause a manifest that omits resources to become `Burstable` rather than `BestEffort`.

### 6.6 Eviction factors and failure distinctions

Do not memorize a simplistic universal eviction order such as “BestEffort always dies first, then Burstable, then Guaranteed.” During node-pressure eviction, kubelet considers whether a Pod’s usage exceeds requests, Pod priority, and QoS-related factors. A `Guaranteed` Pod can still be terminated under severe conditions, and priority does not create capacity or prevent every termination. The exact decision details are **[VERIFY]** against the current Node-pressure Eviction documentation.

| Event | What it means | Evidence to inspect | What it is not |
|---|---|---|---|
| `OOMKilled` | Container was terminated following an out-of-memory kill; often associated with its memory limit, but confirm context | `lastState.terminated.reason`, exit code, previous logs, events | Not synonymous with kubelet eviction |
| Node-pressure eviction | Kubelet evicts a Pod to reclaim node resources under pressure | Pod reason/message, events, node conditions, kubelet logs if available | Not simply a container exceeding its own limit |
| CPU throttling | CPU execution is constrained by CPU quota/period or contention | CPU usage, latency, and runtime/kernel throttling counters where available | Not necessarily a restart or Kubernetes event |
| Admission rejection | API request denied before persistence due to quota/LimitRange/other validation | API error, events where present, quota/LimitRange state | Not a scheduler decision |
| `Pending` | Pod not yet running; can be unscheduled or waiting for another condition | `kubectl describe pod`, conditions/events | Not itself a root cause |

### 6.7 Namespace tenancy strategies

| Pattern | Use when | Avoid when |
|---|---|---|
| Per environment | Dev/test/prod need different lifecycle, access, or policy | One environment contains unrelated trust domains that need stronger separation |
| Per team/tenant | Ownership, quota, and access boundaries align by team | A team hosts workloads with incompatible trust/lifecycle requirements |
| Per application | Application ownership and lifecycle are independent | Too many namespaces create high policy/observability overhead without clear benefit |
| Hybrid: team + environment | Teams own multiple environments and need separate policy budgets | Naming/automation is inconsistent or ownership is unclear |

A platform may use one namespace per team per environment (for example, `team-forecast-prod`) with centrally governed labels and quota templates. The trade-off is additional operational objects in exchange for clearer ownership and blast-radius boundaries. A namespace does not replace cluster-level isolation where tenants are mutually untrusted.

**Pattern catalogue**

| Pattern | Use when | Avoid when |
|---|---|---|
| Namespace template with labels, quota, LimitRange | Many teams need consistent guardrails | Teams need fundamentally different policies without an exception process |
| Quota by workload class | API and batch have different fairness/criticality | Quota boundaries do not map to ownership or actual contention |
| Default requests plus explicit overrides | Workloads are initially onboarding and need safe starting points | Defaults conceal missing performance testing |
| Explicit exceptions with owner/expiry | A legitimate workload cannot fit standard policy | Exceptions become permanent undocumented policy |
| Separate cluster for trust boundary | Tenant threat model demands stronger isolation | Team cannot operate fleet lifecycle/monitoring responsibly |

**Anti-pattern catalogue**

| Bad configuration | Production risk | Correction |
|---|---|---|
| No requests for all workloads | Scheduler has weak information; noisy-neighbor risk | Require reviewed requests or explicit exception |
| Quota only on CPU requests | Memory or object storms remain unbounded | Add relevant memory, limits, and object-count dimensions |
| One huge quota for every team | No per-tenant fairness | Define ownership-aligned budgets and shared capacity policy |
| Very restrictive LimitRange defaults | Hidden defaults cause latency/OOM/scheduling issues | Measure workload classes and document defaults |
| Namespace as only security control | Cross-namespace access/network paths may remain | Add RBAC, admission, network and node controls |
| Delete quota during incident | Removes guardrails without capacity review | Temporary scoped change with approval, expiry and reversal |
| CPU limit copied from a generic template | Throttling harms latency or batch duration | Measure and document workload-specific trade-off |

## 7. Level 3 — Advanced: Measurement, Right-Sizing, and Multi-Tenant Design

### 7.1 Measure before changing resources

Right-sizing is a decision process, not a command that prints the correct request. Start by identifying workload type, service objective, traffic/load profile, replica count, batch concurrency, startup/warmup behavior, memory peaks, and failure consequences. Collect representative observations across quiet and peak periods. Record changes, versions, and caveats so before/after comparisons are meaningful.

A useful loop:

1. Define the workload and its success metric (latency, throughput, completion time, error rate).
2. Confirm the container image, process model, replica count, and workload conditions.
3. Collect usage and application signals over representative conditions.
4. Compare usage to current requests/limits and node allocatable/headroom.
5. Form a hypothesis: request too high, request too low, CPU limit throttling, memory peak, or measurement gap.
6. Change one dimension at a time in a disposable environment or through a reviewed change.
7. Compare outcomes under equivalent load; record regressions and uncertainty.
8. Set an owner, review date, and remeasurement trigger.

### 7.2 Mean versus p95/p99

The mean answers an average question and can hide brief but important spikes. The 95th percentile (p95) is a value at or below which roughly 95% of observations fall; p99 is the analogous 99th percentile. Percentiles are only meaningful relative to a defined population, time window, sampling cadence, and enough observations. A handful of manual samples from `kubectl top` cannot establish a robust p95 or p99. Usage metrics also need context: batch jobs, cache warmup, garbage collection, traffic bursts, and concurrent data copies may change memory demand.

| Statistic | Useful for | Limitation |
|---|---|---|
| Mean | Typical average consumption across a stated interval | Can hide bursts and tail behavior |
| Maximum | Observed worst point in collected data | Sensitive to sampling gaps and isolated outliers |
| p95 | High-end behavior with less sensitivity to a single maximum | Needs enough representative samples and defined window |
| p99 | Rare high-end behavior when sample volume is adequate | Unstable with small datasets; may mislead if traffic mix changes |
| App-level heap/working set | Process-specific diagnosis | Does not necessarily equal container memory accounting |
| `kubectl top` | Quick sampled current usage | Not a history, profiler, or complete throttling/pressure diagnosis |

### 7.3 CPU limit policy: API versus batch worker

CPU is compressible: under contention or quota enforcement, work can slow down rather than immediately fail. A finite CPU limit can reduce a container's ability to monopolize CPU, but may also introduce throttling and latency variance. Omitting CPU limits may be considered in some latency-sensitive environments with strong requests, admission governance, and adequate node-level protections; that decision must be explicit, reviewed, and validated against current platform guidance. **[VERIFY]** current Kubernetes and distribution guidance; do not treat any one policy as universal.

For a scoring API, the trade-off may prioritize tail latency and consistent throughput. For a batch worker, a limit may make runtime more predictable across tenants but lengthen job duration under quota. Evaluate CPU request, limit, concurrency, replicas, node contention, latency/completion SLOs, and available throttling metrics. Do not remove CPU limits just because one benchmark improved.

### 7.4 Memory limit policy and data workloads

Memory is not throttled in the same way as CPU. A process may allocate memory rapidly; when a container crosses its memory limit, the kernel may kill a process/container. Setting memory limit equal to request can be useful for some data workloads because it makes the declared and maximum envelope align and may yield `Guaranteed` QoS when all relevant containers meet the required CPU/memory conditions. However, it can also force the scheduler to account for a larger request, reduce packing density, and leave less room for temporary spikes. It is not universally correct.

**Python and pandas:** process memory includes the interpreter, loaded modules, native libraries, allocator fragmentation, input buffers, dataframe columns, temporary arrays, serialization/deserialization buffers, and copies created by operations. A DataFrame's logical memory estimate does not necessarily equal total process/container memory. Native libraries may allocate outside Python object accounting. A join, sort, conversion, or vectorized operation may temporarily hold both source and destination arrays.

**JVM:** heap size is not total process/container memory. Native memory can include thread stacks, direct buffers, JIT/compiler structures, metaspace, code cache, and other runtime allocations. Garbage collection and allocation bursts affect observed usage. Container-aware JVM behavior varies by version/configuration; **[VERIFY]** the selected JVM's container support and memory options. Do not size a container by heap alone.

For both runtimes, measure process/container behavior under representative peak workload, include startup and temporary allocations, and set a deliberate safety margin based on evidence—not an invented universal percentage.

### 7.5 Node capacity versus allocatable

Node **capacity** describes resources reported by the node. **Allocatable** is the amount Kubernetes makes available for Pods after applicable reservations and overhead. `system-reserved` is intended for operating-system/system daemons; `kube-reserved` is intended for Kubernetes system daemons. Exact configuration and accounting vary by distribution and node provisioning.

```bash
kubectl describe node <NODE_NAME>
kubectl get node <NODE_NAME> -o jsonpath='{.status.capacity}{"\n"}{.status.allocatable}{"\n"}'
```

**Purpose:** compare reported capacity and allocatable.  
**Prerequisite:** read access to node objects.  
**Example — yours will differ:**
```text
capacity:    cpu: "4", memory: "8Gi"
allocatable: cpu: "3900m", memory: "7600Mi"
```
**Interpretation:** illustrative only. Never infer a standard reservation from this example. Inspect provider/node configuration and official Node Allocatable documentation.

Quota and allocatable answer different questions. Quota constrains namespace admission accounting; allocatable informs scheduling capacity on a node. If quota is increased without sufficient allocatable headroom, new Pods can remain Pending. Conversely, low quota can block admission even when nodes have free capacity.

### 7.6 PriorityClass, preemption, and fairness

A `PriorityClass` assigns priority to Pods. The scheduler may preempt lower-priority Pods to make room for a higher-priority Pod when its scheduling rules permit. Preemption is not a guarantee: there may be no suitable victim set, constraints may still prevent placement, graceful termination takes time, and disruption may harm another workload. Priority does not create CPU/memory, bypass every admission rule, or automatically override quota. **[VERIFY]** current scheduler and preemption documentation for exact behavior.

Multi-tenant fairness usually combines ownership-aligned quotas, requests/limits, priority policy, admission controls, workload classes, monitoring, and an exception process. Avoid allowing every tenant to declare top priority. Define which workloads are critical, who approves priority changes, what lower-priority work may be displaced, and how fairness is measured.

### 7.7 Awareness: hierarchical namespaces, Capsule, vcluster

- **Hierarchical namespaces** address parent/child namespace organization and policy inheritance concepts that can simplify large tenant structures. Research current SIG Multitenancy documentation and feature maturity before adoption.
- **Capsule** is a Kubernetes multi-tenancy project that provides tenant-oriented governance features. Research its supported versions, policy model, upgrade path, and operational ownership.
- **vcluster** provides virtual Kubernetes control-plane concepts for tenant isolation and delegated cluster-like environments. It introduces additional lifecycle, security, and operational considerations.

These are awareness topics, not endorsements or implementation instructions. Evaluate project activity, compatibility, threat model, operational burden, and exit strategy before use.

### 7.8 Defended namespace decision exercise

Choose a namespace strategy for the example platform using the following facts you must define yourself: team count, environment count, trust boundaries, rollout cadence, resource contention, ownership, compliance, and platform-team capacity.

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Per environment | Clear prod/non-prod separation | More repeated configuration | Teams may still be mixed within one environment | Environment policy is the dominant boundary |
| Per team/tenant | Ownership and quotas align | Teams may mix criticality/workload types | Namespace not a full security boundary | Tenant governance is primary |
| Per application | Independent lifecycle | Many namespaces and policy objects | Operational sprawl | App owners and trust needs differ |
| Team × environment hybrid | Clear ownership and production separation | Requires namespace-vending automation | Drift if templates are not centrally maintained | Platform can manage a consistent template |

Write a short decision record with alternatives, evidence, assumptions, trade-offs, owner, and revisit triggers. A copied YAML manifest is not a defended design.

## 8. Level 4 — Expert: Capacity Policy, Automation, and Incident Response

### 8.1 Explicit overcommit policy

Overcommit policy describes what aggregate declared demand is allowed relative to capacity and which risks are accepted. It must distinguish CPU from memory.

- **CPU:** workloads can often share CPU over time; requests guide placement/accounting, and CPU limits may throttle. Overcommit can be viable when demand peaks are not perfectly correlated and SLOs tolerate contention.
- **Memory:** memory cannot be slowed down in the same manner; correlated peaks can cause OOM kills or node pressure. Memory overcommit requires conservative assumptions, observed peaks, headroom, and clear workload criticality.
- **Quota:** tenant budgets constrain admitted requests/limits or counts; they do not make the cluster safe if aggregate actual demand or declared requests are inconsistent with node capacity.
- **Headroom:** reserve capacity for system services, rolling deployments, failure recovery, and workload bursts. Headroom must be measured and justified rather than copied from a generic percentage.

A policy should state workload classes, request/limit expectations, CPU-limit stance, memory safety approach, quota dimensions, priority rules, node headroom, exception authority, measurement period, and review triggers. Review it whenever workload mix, node shape, runtime, kernel, or service objectives materially change.

### 8.2 Quota-as-code and namespace vending

Quota-as-code stores namespace, quota, LimitRange, labels, and policy definitions in reviewed version control. Namespace vending automates creation with approved templates, owner metadata, guardrails, and lifecycle operations. At this level, the design should include:

1. request form or declarative tenant specification;
2. owner/team/environment validation;
3. approved namespace naming and labels;
4. standard quota and LimitRange templates by workload class;
5. RBAC and network/admission policy hand-off;
6. reconciliation/drift detection;
7. quota change approval and audit;
8. expiry and deletion lifecycle;
9. evidence and rollback.

Do not implement the full platform automation system here. M16 owns deeper platform automation. A YAML template alone is not a vending service: it needs authorization, validation, idempotency, ownership, error handling, and operational support.

### 8.3 Defensive audit script

The following Python script reads a local JSON fixture, checks an explicit allowlist of namespaces, and reports policy findings. It distinguishes missing requests, missing memory limits, and missing CPU limits. The default policy does **not** automatically mark a missing CPU limit unsafe; teams must document their CPU-limit decision. It does not contact a cluster and uses no external dependencies.

**Path comment — learner-created file:** `# Save as: labs/m03-u02/audit_resources.py`

```python
#!/usr/bin/env python3
"""Audit resource declarations in a local Kubernetes Pod-list JSON export.

Checks only containers in explicitly allowlisted namespaces:
- missing or non-positive CPU/memory requests;
- missing or non-positive memory limits;
- missing CPU limits only when --require-cpu-limit is selected.

It does not prove runtime usage, admission-policy correctness, quota headroom,
QoS correctness for every Kubernetes edge case, node capacity, security, or
production safety. It does not connect to a cluster.
"""
import argparse
import json
import sys
from pathlib import Path

def positive_quantity(value):
    """Conservative presence check, not a complete Kubernetes quantity parser."""
    if value is None:
        return False
    text = str(value).strip()
    if not text or text in {"0", "0m", "0Mi", "0Gi", "0Ki"}:
        return False
    return True

def audit(document, namespaces, require_cpu_limit=False):
    findings = []
    items = document.get("items", [])
    for pod in items:
        namespace = pod.get("metadata", {}).get("namespace", "default")
        if namespace not in namespaces:
            continue
        pod_name = pod.get("metadata", {}).get("name", "<unnamed>")
        spec = pod.get("spec", {})
        containers = list(spec.get("containers", []))
        for container in containers:
            name = container.get("name", "<unnamed>")
            resources = container.get("resources", {})
            requests = resources.get("requests", {})
            limits = resources.get("limits", {})
            for resource in ("cpu", "memory"):
                if not positive_quantity(requests.get(resource)):
                    findings.append(
                        f"{namespace}/{pod_name}:{name}: missing/non-positive {resource} request"
                    )
            if not positive_quantity(limits.get("memory")):
                findings.append(
                    f"{namespace}/{pod_name}:{name}: missing/non-positive memory limit"
                )
            if require_cpu_limit and not positive_quantity(limits.get("cpu")):
                findings.append(
                    f"{namespace}/{pod_name}:{name}: CPU limit required by selected policy but missing/non-positive"
                )
    return findings

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Local JSON file exported for offline review")
    parser.add_argument("--namespaces", required=True,
                        help="Comma-separated explicit namespace allowlist")
    parser.add_argument("--require-cpu-limit", action="store_true",
                        help="Apply an organization policy requiring CPU limits")
    args = parser.parse_args()
    namespaces = {part.strip() for part in args.namespaces.split(",") if part.strip()}
    if not namespaces:
        parser.error("--namespaces must contain at least one namespace")
    path = Path(args.input)
    if not path.is_file():
        parser.error(f"input file does not exist: {path}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read valid JSON: {exc}", file=sys.stderr)
        return 2
    findings = audit(document, namespaces, args.require_cpu_limit)
    if findings:
        print("\n".join(findings))
        print(f"Policy findings: {len(findings)}")
        return 1
    print("No findings for the selected checks and namespace allowlist.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

**Path comment — local test fixture:** `# Save as: labs/m03-u02/pods-fixture.json`

```json
{
  "apiVersion": "v1",
  "kind": "PodList",
  "items": [
    {
      "metadata": {"name": "api-example", "namespace": "team-forecast-lab"},
      "spec": {
        "containers": [
          {
            "name": "web",
            "resources": {
              "requests": {"cpu": "100m", "memory": "128Mi"},
              "limits": {"memory": "256Mi"}
            }
          }
        ]
      }
    },
    {
      "metadata": {"name": "unrelated", "namespace": "other-team"},
      "spec": {"containers": [{"name": "web", "resources": {}}]}
    }
  ]
}
```

Run only against the local fixture:

```bash
python3 labs/m03-u02/audit_resources.py \
  --input labs/m03-u02/pods-fixture.json \
  --namespaces team-forecast-lab
```

**Purpose:** exercise the policy checks offline.  
**Prerequisite:** Python 3; save both inline files to the stated local paths.  
**Example — yours will differ:**
```text
team-forecast-lab/api-example:web: missing/non-positive cpu limit
Policy findings: 1
```
**Interpretation:** representative output. The sample has a memory limit and both requests but no CPU limit. Because `--require-cpu-limit` was not set, the audit reports no CPU-limit finding by default. If you enable that flag, it should report the missing CPU limit. The script uses a conservative presence check, not a full Kubernetes quantity parser.

A minimal self-test can be run by importing `audit` in a Python test or by adding a fixture with a missing memory limit. **Do not point this script at a live cluster**; it accepts only a local JSON file. A live export, if later used by a platform team, should be created through an approved read-only workflow, with namespace allowlist and sensitive metadata reviewed.

### 8.4 Noisy-neighbor incident: symptom to prevention

**Symptom:** scoring API tail latency rises while ETL and queue-worker activity increases.  
**Hypotheses:** CPU contention/throttling; memory pressure; request under-declaration; batch concurrency burst; node allocatable/headroom too small; shared downstream dependency; or unrelated application regression.  
**Tests:** compare application latency and throughput; inspect Pod usage and requests/limits; inspect events and node conditions; check node allocatable and scheduling; review runtime throttling metrics if available; compare with deployment and workload changes.  
**Root cause:** do not assert one until evidence discriminates among hypotheses.  
**Mitigation:** reduce or pause noncritical batch concurrency through approved controls, restore capacity if available, or adjust resource policy through review; avoid randomly raising all limits.  
**Prevention:** representative load tests, per-class budgets, explicit priority policy, alert ownership, trend review, and a repeatable post-incident action list.

### 8.5 Incident scenario: namespace quota blocked a critical rollout

**Scenario `[ILLUSTRATIVE]`:** a critical API Deployment needs another Pod during an incident, but its namespace quota rejects Pod creation. The API error identifies a quota dimension that would exceed its hard value. The correct response is not “delete the quota.”

**Runbook:**

1. **Confirm context and ownership.** Record `kubectl config current-context`; confirm the intended cluster and namespace, service owner, incident commander, and authorized approver.
2. **Capture evidence before changes.** Save Deployment/ReplicaSet/Pod status, rollout output, events, quota/usage, LimitRange, and the exact admission error. Record time and actor.
3. **Identify the specific blocking key.** Use `kubectl describe resourcequota <NAME> -n <NS>` and the error message. Determine whether the issue is requests, limits, Pod count, or another quota dimension.
4. **Check capacity and business criticality.** Inspect node allocatable, current requests, pressure conditions, and competing workloads. Confirm whether increasing quota will merely admit a Pod that remains Pending.
5. **Choose the smallest authorized mitigation.** Options may include reducing noncritical replicas/concurrency, moving a workload through a reviewed placement/capacity process, or temporarily raising only the blocking quota key. A PriorityClass change is not a substitute for admission/quota resolution and must be governed separately.
6. **Record approval and scope.** Include actor, approver, reason, exact old/new values, namespace, affected key, start time, expiry or reversal condition, and rollback owner.
7. **Apply and verify.** Confirm admission succeeds, Pods schedule and become ready, service-level health recovers, and other tenants remain within the agreed risk envelope.
8. **Reverse temporary policy.** At expiry or once capacity is restored, return to standard quota and verify current usage/policy remain valid. Do not reduce quota below active usage without understanding resulting behavior.
9. **Post-incident review.** Explain why the quota blocked recovery, whether the standard budget was wrong or capacity was unavailable, how emergency approval worked, and which alert/test/automation must change.

**Representative incident timeline `[ILLUSTRATIVE]`:**

| Time | Event | Evidence |
|---|---|---|
| 09:12 | Critical rollout stalls | Deployment/ReplicaSet status and event |
| 09:15 | Quota rejection identified | Exact API error and quota usage |
| 09:18 | Owner and approver confirm criticality | Incident record |
| 09:22 | Node headroom and competing workloads reviewed | Node and workload evidence |
| 09:25 | Small temporary quota change approved with 30-minute expiry | Change record |
| 09:29 | New Pod scheduled and ready | Pod status plus application SLI |
| 09:55 | Temporary value reverted after capacity stabilized | Before/after quota |
| Next day | Review actions assigned | Post-incident record |

Times and expiry are illustrative, not measured. This procedure requires organization-specific authorization and may differ by platform. Do not weaken controls permanently to solve a single incident.

### 8.6 Hierarchical namespace and cost governance awareness

Hierarchical namespaces, Capsule, and vcluster may help organize tenants or delegate control, but add a control plane, policy, compatibility, and lifecycle surface. Investigate them when namespace count, delegated ownership, inheritance, or stronger virtual-cluster semantics become hard to manage with native primitives.

Governance labels such as team, environment, owner, application, and cost center can support showback/chargeback reporting. Labels do not themselves allocate a cloud bill or guarantee accurate attribution. M15 covers cost models, allocation rules, shared costs, and FinOps; this unit only establishes consistent metadata and resource-policy evidence.

## 9. SRE Lens

Resource governance is an availability mechanism. Requests that are too high can waste schedulable capacity and block rollouts. Requests that are too low can lead to dense packing, contention, and misleading scheduling decisions. CPU limits can protect a tenant but may increase latency through throttling. Memory limits can bound a container but make peak-allocation failures more likely if the limit is based on averages. Quota can protect other tenants while also blocking critical recovery if budgets do not account for rollout surge and incident needs.

### Useful signals and SLIs

| Signal / SLI | What it answers | Limitation |
|---|---|---|
| Application latency/error/throughput | Is service quality degraded? | Not enough to identify resource root cause alone |
| Pod resource usage from Metrics Server | What is sampled CPU/memory use now? | Not a historical time series or profiler |
| Requests/limits versus usage | Are declared envelopes plausibly aligned with observed demand? | Requires representative sampling and workload context |
| Pod pending duration and events | Is scheduling/admission blocking progress? | Events can expire/aggregate; not a full audit log |
| Node conditions and allocatable | Is node capacity/pressure relevant? | API state may be stale during control-plane problems |
| CPU throttling counters from monitoring/runtime | Is CPU quota limiting execution? | Metric availability/name depends on stack; verify |
| OOM/eviction counts and restart reasons | Are resource failures occurring? | Different causes must not be combined blindly |
| Quota used/hard ratio | Is a namespace approaching its admission ceiling? | Does not reveal physical node headroom |

### Read-only triage runbook

1. Confirm cluster context, namespace, owner, and incident scope.
2. Read Deployment/Pod state, events, quota usage, and LimitRange.
3. Separate admission rejection from scheduling and runtime symptoms.
4. Inspect node conditions, capacity/allocatable, and competing workloads where access permits.
5. Compare resource evidence with application SLIs and recent changes.
6. Mitigate through an approved, reversible action; verify service recovery.
7. Record uncertainty, follow-up owner, expiry, and remeasurement date.

### Capacity and cost

Capacity planning must account for system/kube reserved resources, rolling updates, failure recovery, burst behavior, replicas, and criticality. A namespace quota is one layer of policy, not the capacity model. Excessively high requests reduce packing efficiency; excessively low requests increase contention and risk. Monitoring and incident management details belong to M10/M11, while deeper capacity and cost allocation belong to M15.

## 10. Security and Isolation Lens

Resource exhaustion can become a denial-of-service (DoS) or availability incident even when a tenant has no malicious intent. Namespace quotas, LimitRanges, object-count quotas, and request/limit policy reduce some risks, but do not replace authentication, authorization, admission policy, Pod Security Standards, NetworkPolicy, node hardening, image supply-chain controls, or a complete threat model.

### Verification commands and limits

```bash
kubectl config current-context
kubectl auth can-i get pods -n team-forecast-lab
kubectl auth can-i create deployments -n team-forecast-lab
kubectl get networkpolicy -n team-forecast-lab
kubectl get resourcequota,limitrange -n team-forecast-lab
```

**Purpose:** verify the current context, ask the authorization layer about particular actions, and inspect visible namespace policies.  
**Prerequisite:** the current identity must be allowed to query these resources.  
**Example — yours will differ:**
```text
yes
no
```
**Interpretation:** illustrative only. `kubectl auth can-i` answers a specific authorization question for the current identity/context; it does not prove admission will accept the request, nor that every access path is secure. An empty NetworkPolicy list does not prove that no network controls exist elsewhere, and policy objects do not prove enforcement unless the installed network implementation supports them.

Security review checklist:

- Use least-privilege RBAC and review service-account permissions.
- Treat labels as metadata until an explicit policy/controller enforces them.
- Confirm whether NetworkPolicy is supported and enforced by the chosen CNI.
- Apply the organization’s Pod Security Standards/admission controls (M03 Unit 9).
- Avoid broad cluster-admin access for namespace creation or quota adjustment.
- Audit emergency changes and expire temporary exceptions.
- Protect kubeconfig credentials and redact sensitive infrastructure metadata from evidence.
- Use official Kubernetes security concepts, NSA/CISA Kubernetes Hardening Guidance, and the CIS Kubernetes Benchmark only after checking the relevant edition and applicability. This lesson is not a full hardening baseline.

## 11. Guided Labs

### Lab A — Namespace tenancy and admission behavior

**Goal:** create a namespace with governance labels, apply quota and LimitRange, and distinguish admission rejection from scheduling/runtime behavior.  
**Footprint:** approximately 1 CPU, 1–2 GB RAM, under 1 GB extra disk for this lab; actual overhead varies.  
**Prerequisites:** `kind`, `kubectl`, verified image access, and permission to create namespaces and quota objects in the disposable cluster.  
**Context guard:** first command in the lab is required.

```bash
kubectl config current-context
```

Assert that the context is exactly `kind-m03-u02-lab` (or the actual context name if you deliberately chose a different lab name). If not, stop. Do not use a production or shared context.

**Step 1 — inspect the target.**

```bash
kind get clusters
kubectl get nodes -o wide
```

**Purpose:** verify the named disposable cluster and nodes.  
**Example — yours will differ:**
```text
m03-u02-lab
NAME                         STATUS   ROLES
m03-u02-lab-control-plane    Ready    control-plane
m03-u02-lab-worker           Ready    <none>
```
**Interpretation:** illustrative. Confirm the intended cluster before mutation.

**Step 2 — create the namespace.** Save the Namespace manifest from Section 5.2 to `labs/m03-u02/namespace.yaml`, then:

```bash
kubectl apply -f labs/m03-u02/namespace.yaml
kubectl get namespace team-forecast-lab --show-labels
```

**Step 3 — apply governance.** Save Section 6.1 as `labs/m03-u02/resourcequota.yaml` and Section 6.2 as `labs/m03-u02/limitrange.yaml`.

```bash
kubectl apply -f labs/m03-u02/resourcequota.yaml
kubectl apply -f labs/m03-u02/limitrange.yaml
kubectl describe resourcequota forecast-budget -n team-forecast-lab
kubectl describe limitrange forecast-container-policy -n team-forecast-lab
```

**Step 4 — test defaulting.** Save this Pod as `labs/m03-u02/omitted-resources-pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: defaults-demo
  namespace: team-forecast-lab
spec:
  containers:
    - name: pause
      image: registry.k8s.io/pause:3.10
```

```bash
kubectl apply -f labs/m03-u02/omitted-resources-pod.yaml
kubectl get pod defaults-demo -n team-forecast-lab -o yaml
kubectl describe resourcequota forecast-budget -n team-forecast-lab
```

**Expected behavior:** if the configured LimitRange applies to this Pod/container, default resource fields may be injected. Inspect the resulting Pod spec and quota accounting. **[VERIFY]** exact defaulting and quota admission behavior against the selected version. If the request is rejected, preserve the error and determine which admission rule was applied.

**Step 5 — test rejection.** Save the deliberately invalid manifest from Section 6.3 as `labs/m03-u02/too-large-pod.yaml` and apply only in this lab. Capture the exact API error. Do not infer that an object exists after a rejected request. Explain whether the error indicates LimitRange validation or quota accounting; then compare with `kubectl describe pod` only if the Pod was actually created.

**Namespace boundary discussion:** create a second namespace only if needed, inspect resource visibility under the current identity, and explain why this does not prove network isolation. Do not create broad roles or network policies as part of this unit.

**Evidence:** namespace labels, quota/LimitRange YAML, defaulted Pod YAML, rejection message, and a short explanation of admission versus scheduling.  
**Cleanup:**

```bash
kubectl config current-context
kubectl get namespace team-forecast-lab
```

After confirming the disposable context and evidence capture, remove the namespace:

```bash
kubectl delete namespace team-forecast-lab
kubectl get namespace team-forecast-lab
```

**Example — yours will differ:** a `NotFound` result after deletion is expected; wait for termination if necessary. Namespace deletion removes namespaced lab objects.  
**Stretch:** add a separate object-count quota and explain what resource-creation risk it addresses and what it does not prevent.

### Lab B — Measure before right-sizing

**Goal:** collect repeated observations, compare with requests/limits, and propose a resource change based on evidence.  
**Footprint:** approximately 1 CPU, 1–2 GB RAM, under 1 GB disk; keep the workload modest.  
**Prerequisites:** disposable cluster, a verified lab image, Metrics Server if `kubectl top` is to be used.  
**Context guard:**

```bash
kubectl config current-context
```

Assert `kind-m03-u02-lab` before applying anything.

**Step 1 — verify Metrics Server.**

```bash
kubectl get deployment metrics-server -n kube-system
kubectl get apiservice v1beta1.metrics.k8s.io
kubectl top nodes
```

**Purpose:** confirm metrics collection works.  
**Example — yours will differ:**
```text
NAME             CPU(cores)   MEMORY(bytes)
m03-u02-lab-worker  75m        650Mi
```
**Interpretation:** illustrative. If the metrics API is unavailable, record the failure and investigate; do not record zero usage.

**Step 2 — deploy a modest test workload.** Use a previously verified container image that remains running and has a known resource behavior. Keep its requests/limits explicit and modest; avoid using an unknown image or unbounded stress tool. Record exact image tag/digest and configuration. A `pause` container validates scheduling but is not a useful CPU/memory load generator, so do not pretend it represents an API or ETL workload.

**Step 3 — record observations.** Manually collect at least several samples under documented conditions. These samples are for practice, not statistically sound p95/p99 estimates.

**Path comment — learner-created CSV:** `# Save as: evidence/m03-unit-02-namespaces-resources/before-usage.csv`

```csv
timestamp,workload,replicas,condition,cpu_usage,memory_usage,cpu_request,memory_request,cpu_limit,memory_limit,caveats
<ISO-8601>,scoring-api-lab,1,idle,<record>,<record>,100m,128Mi,250m,256Mi,Metrics Server sample; idle only
```

Replace all angle-bracket placeholders. Do not enter invented numbers.

**Step 4 — change one setting.** Choose a request or limit change based on evidence and the workload’s service objective. Apply through the same controlled lab process. Record the hypothesis, change, and rollback value.

**Step 5 — compare.** Capture another set of samples under equivalent conditions. Discuss whether load was representative, whether the sample window includes peaks, and what historical telemetry would be needed for p95/p99. M11 covers a durable monitoring history.

**Evidence:** before/after CSV, exact manifest, conditions, and a short decision record.  
**Cleanup:** verify context, then delete only the lab workload and namespace created for this lab. Confirm no lab Pods remain.  
**Stretch:** define a production measurement plan with traffic profile, sample cadence, duration, SLOs, p95/p99 method, and a rollback threshold.

### Lab C — OOMKill, CPU throttling, and node-pressure eviction

**Goal:** distinguish three different failure mechanisms, capture evidence, and revise sizing using observations.  
**Footprint:** sequential experiments only; approximately 1–2 CPU and 2–3 GB RAM headroom. Do not run stress workloads concurrently.  
**Prerequisites:** disposable kind cluster, recovery access, Metrics Server where available, and host resource monitoring.  
**Context guard:**

```bash
kubectl config current-context
```

Assert `kind-m03-u02-lab`. If this is not a throwaway cluster, stop. Never exhaust the host, use production, or perform pressure tests on a shared cluster.

#### C1. Bounded OOMKill demonstration

Use a small purpose-built memory allocator only if you understand its behavior and can bound allocation. Avoid a command that consumes all host memory. A safe alternative is to use a purpose-built lab image/program with a hard allocation ceiling and a deliberately low container memory limit, but its image/tag and command must be verified first. The lesson does not provide an unverified stress image as if it were guaranteed safe.

**Required learner setup:** choose a trusted, reviewed local image/program that allocates a bounded amount above a test container’s memory limit but below a conservative host budget. Set an explicit `resources.limits.memory`, request, and short timeout. Do not run if you cannot establish the bound. **[VERIFY]** the image behavior and runtime enforcement in your environment.

Capture:

```bash
kubectl describe pod <POD_NAME> -n <NAMESPACE>
kubectl get pod <POD_NAME> -n <NAMESPACE> -o jsonpath='{.status.containerStatuses[*].lastState.terminated.reason}{"\n"}'
kubectl get events -n <NAMESPACE> --sort-by=.metadata.creationTimestamp
kubectl logs <POD_NAME> -n <NAMESPACE> --previous
```

**Purpose:** inspect termination reason, events, and previous logs.  
**Prerequisite:** substitute the actual Pod/namespace; the previous log may be unavailable.  
**Example — yours will differ:**
```text
OOMKilled
```
**Interpretation:** illustrative. A confirmed `OOMKilled` status supports a container-level OOM diagnosis, but inspect node conditions/events to understand whether broader node pressure also existed. Do not claim the event occurred until your evidence shows it.

#### C2. CPU throttling demonstration

Use a CPU-intensive workload with a finite CPU limit and bounded duration, without launching multiple stress processes. CPU cgroup quota/period mechanisms limit the amount of CPU time available over a scheduling period; a process can be throttled and run more slowly rather than restarting. The exact runtime configuration and metrics exposed depend on kernel/cgroup version and monitoring stack.

Collect application duration/latency and CPU usage. If the local environment exposes throttling counters, record their source and exact metric name after verifying it. Do not invent a metric name. If direct throttling metrics are unavailable, write “throttling not directly measured” and record the observed slowdown as suggestive, not conclusive.

**[VERIFY]** official kernel/cgroup and monitoring documentation for your runtime. Metrics Server `kubectl top` alone does not reliably prove throttling.

#### C3. Node-pressure eviction: safe decision path

A `kind` node is a container sharing the host kernel and constrained by host/container runtime settings. Forcing node memory or disk pressure may destabilize the workstation and may not reproduce production kubelet eviction behavior. This lesson therefore does **not** instruct learners to exhaust the host or deliberately starve a kind node.

Safe path:
1. Inspect node conditions and Pod events in the disposable cluster.
2. Read the official Node-pressure Eviction documentation for the selected Kubernetes release.
3. Use a pre-existing naturally occurring pressure event only if it happened without intentionally destabilizing the host.
4. Otherwise complete an **inspection/simulation-only** exercise: explain the expected mechanism, list the evidence needed, and explicitly record that eviction was not reproduced.
5. If an organization later wants a real pressure test, use an isolated disposable test environment with an approved resource budget, recovery path, and SRE sign-off—not this laptop lab.

```bash
kubectl describe node <NODE_NAME>
kubectl get pods -A -o wide
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

**Example — yours will differ:** node conditions may include `MemoryPressure` or `DiskPressure`, or no pressure condition at all. Absence of pressure in a short lab is not a failure of the lesson.

#### C4. Expected-versus-observed worksheet

| Mechanism | Expected mechanism | Learner observation | Evidence |
|---|---|---|---|
| OOMKill | Container may terminate when it exceeds applicable memory limit | `[record; or not reproduced]` | Pod status, previous logs, events |
| CPU throttling | CPU-heavy process may run slower under CPU quota | `[record; or not directly measured]` | Runtime counters if available, workload duration |
| Node-pressure eviction | Kubelet may evict Pods when node pressure thresholds/conditions apply | `[record; or simulation/inspection only]` | Node conditions, Pod reason/events |
| QoS/priority nuance | Usage relative to requests, priority, QoS-related factors influence eviction decisions | `[explain with sources]` | Policy notes and docs checked |

#### C5. Correct sizing from evidence

After the experiments, revise the workload request/limit only using recorded evidence. State:
- observed workload conditions and sample limitations;
- why the request is appropriate for scheduling;
- why the limit is appropriate for runtime protection;
- whether CPU throttling is acceptable for this workload;
- how memory peaks and temporary allocations are handled;
- what residual uncertainty remains and what production telemetry is needed.

**Cleanup:** verify context; delete only the named lab Pod/Deployment and namespace; verify no lab workloads remain.  
**Stretch:** design an approved node-pressure test plan that includes isolation, maximum resource budget, abort condition, recovery method, observer, and evidence. Do not execute it on a personal laptop as part of this lesson.

### Lab D — Quota-blocked critical rollout incident

**Goal:** diagnose a quota admission rejection and practice a controlled emergency-quota change.  
**Footprint:** minimal; use only a disposable cluster.  
**Prerequisites:** Lab A quota policy, a sample Deployment, and a written change/approval record.  
**Context guard:**

```bash
kubectl config current-context
```

Assert `kind-m03-u02-lab` before applying any manifest.

**Step 1 — create a bounded quota scenario.** In the disposable namespace, apply a deliberately small quota and a Deployment whose aggregate requested resources or replica count will exceed it. Keep values modest. Use the namespace and quota from Lab A only if they still exist and you understand their current state. Record the expected blocking key before applying.

**Step 2 — capture the failure.**

```bash
kubectl describe deployment <DEPLOYMENT_NAME> -n <NAMESPACE>
kubectl get replicasets,pods -n <NAMESPACE> -o wide
kubectl describe resourcequota <QUOTA_NAME> -n <NAMESPACE>
kubectl get events -n <NAMESPACE> --sort-by=.metadata.creationTimestamp
```

**Purpose:** distinguish Deployment intent from failed Pod creation and quota usage.  
**Example — yours will differ:**
```text
FailedCreate ... exceeded quota: forecast-budget
```
**Interpretation:** illustrative only. Preserve the exact error and verify the actual quota key. The error should be diagnosed at admission if the API rejects creation; a Pod that is admitted but unschedulable is a different failure.

**Step 3 — rehearse the emergency procedure on paper.** Fill the runbook template in Section 8.5. State who approves, which key is temporarily changed, how node headroom is checked, what expiry/reversal condition applies, and how service health will be verified. You may apply a temporary change only in the disposable lab after review; do not normalize quota deletion as a response.

**Step 4 — verify and reverse.** If you do make the temporary change, verify Pod creation, scheduling, readiness, and quota usage. Revert the quota to the standard value and verify the policy state. A quota reduction may conflict with current usage or affect future admissions; inspect before reverting.

**Evidence:** exact admission error, before/after quota, approval simulation, rollout status, reversal proof, and post-incident notes.  
**Cleanup:** context guard, delete lab namespace, verify namespace is absent.  
**Stretch:** propose a quota-as-code change with tests and an emergency exception expiry mechanism, but do not build the full M16 automation platform here.

## 12. Production Checklist

- [ ] Namespace has a clear purpose, owner, lifecycle, naming convention, and review date.
- [ ] Team/environment/owner labels use a documented convention and an organization-controlled prefix.
- [ ] Governance labels are not mistaken for enforcement unless a policy/controller consumes them.
- [ ] Tenant isolation assumptions are documented; RBAC, admission, network, Pod security, and node controls are reviewed separately.
- [ ] ResourceQuota covers the relevant CPU/memory request/limit dimensions and selected object counts.
- [ ] Storage-related quota keys are verified against actual API/version/storage configuration.
- [ ] LimitRange defaults, minimums, maximums, and ratios are reviewed against workload classes.
- [ ] Existing manifests have been tested against defaults; policy changes do not silently create unexpected QoS/accounting outcomes.
- [ ] Requests and limits are explicit or have a documented exception and owner.
- [ ] CPU-limit policy is workload-specific and its latency/noisy-neighbor trade-off is documented.
- [ ] Memory limits reflect measured peak behavior and temporary allocations, not only averages or language-level heap estimates.
- [ ] QoS classes and node-pressure behavior are understood; eviction risk is not reduced to a simplistic fixed ordering.
- [ ] Measurement window, traffic/load representativeness, replica count, and sampling limitations are recorded.
- [ ] p95/p99 decisions use adequate representative samples and a reliable history, not a few `kubectl top` samples.
- [ ] Node capacity and allocatable are distinguished; `system-reserved` and `kube-reserved` assumptions are known.
- [ ] Headroom covers rollout surge, failure recovery, system services, and justified bursts.
- [ ] PriorityClass/preemption rules have owners and do not imply guaranteed capacity.
- [ ] Quota changes have approval, audit trail, expiry/reversal, and post-change verification.
- [ ] Emergency runbook checks node capacity before raising quota.
- [ ] Monitoring and alert ownership cover quota saturation, OOMs, evictions, pending workloads, latency, and relevant resource metrics.
- [ ] Chargeback/showback labels are consistent; actual cost allocation is handled by the relevant FinOps process.
- [ ] Local kind limitations are documented; kind results are not used as proof of production HA or node-pressure fidelity.
- [ ] Production readiness is reviewed by accountable humans; no checklist or command alone guarantees safety.

## 13. Self-Check Questions and Answer Key

### Self-check

**1. A namespace has a quota of two CPUs. Does that reserve two CPUs on nodes?**  
**Answer:** No. It constrains configured namespace quota accounting. Node capacity and scheduling are separate.  
**Why the tempting answer is wrong:** quota admission does not create physical capacity or reserve a private pool.

**2. A Pod create request is rejected with “exceeded quota.” Is the Pod Pending?**  
**Answer:** Usually no Pod object was persisted for the rejected create; the API admission request failed. Inspect the exact error and object state.  
**Why the tempting answer is wrong:** `Pending` describes an existing Pod that has not reached Running; admission rejection is earlier.

**3. Why can a CPU-limited API become slow without restarting?**  
**Answer:** CPU can be throttled under the applicable quota/period enforcement.  
**Why the tempting answer is wrong:** CPU limitation usually constrains execution time; it does not inherently require process termination.

**4. What is the difference between request and limit?**  
**Answer:** Requests guide scheduling and resource accounting; limits constrain runtime use for supported resources.  
**Why the tempting answer is wrong:** a request is not an exclusive physical reservation, and a limit is not a scheduler reservation.

**5. What does `kubectl top pods` tell you, and what does it not tell you?**  
**Answer:** It shows sampled current CPU/memory usage via the metrics API. It does not provide a complete historical time series, robust p95/p99, or proof of CPU throttling.  
**Why the tempting answer is wrong:** a current sample misses peaks and causal context.

**6. Is a namespace a security boundary?**  
**Answer:** It is an API-object scope, not a complete security or network boundary.  
**Why the tempting answer is wrong:** access and traffic depend on RBAC, admission, network implementation/policy, and other controls.

**7. Does `Guaranteed` QoS mean a Pod can never be evicted?**  
**Answer:** No. QoS is one consideration; usage relative to requests and priority also matter, and severe conditions can still affect workloads.  
**Why the tempting answer is wrong:** QoS is not an absolute availability guarantee.

**8. How do OOMKill, node-pressure eviction, and CPU throttling differ?**  
**Answer:** OOMKill is a container/process memory-termination outcome; eviction is a kubelet action to reclaim node resources under pressure; throttling constrains CPU execution and may slow work without restart.  
**Why the tempting answer is wrong:** they have different triggers and evidence.

**9. Why are a few manual samples not enough for p99 sizing?**  
**Answer:** Tail percentiles require enough representative observations over a defined window and workload mix.  
**Why the tempting answer is wrong:** small samples produce unstable estimates and may miss bursts.

**10. A critical rollout is blocked by quota. What is the first safe response?**  
**Answer:** Confirm context/owner, capture the exact error and quota usage, check node headroom and business criticality, obtain authorized approval, then make the smallest temporary reversible change with expiry.  
**Why the tempting answer is wrong:** deleting quota blindly can remove guardrails without creating capacity and without an audit trail.

### Interview and design-review questions

**1. Design resource governance for a multi-tenant model-scoring API and batch ETL platform.**  
**Model answer:** Align namespaces to ownership/environment/trust boundaries, use consistent labels, quotas for relevant requests/limits/object counts, LimitRange defaults and constraints, and explicit workload resources. Define API versus batch CPU policy, memory sizing from representative peaks, priority policy, exception ownership, monitoring, and quota-vending lifecycle. Namespace alone is not security isolation. Validate policy against real workloads and node allocatable.

**2. Why can increasing quota fail to resolve a rollout?**  
**Model answer:** Quota may have blocked admission, but after increasing it the Pod can still be unschedulable due to node allocatable, requests, taints, affinity, storage, or other constraints. Quota is not capacity. Capture the admission error, inspect node capacity and Pod events, and verify each stage independently.

**3. Explain CPU-limit trade-offs for an interactive API versus a batch worker.**  
**Model answer:** CPU limits can reduce noisy-neighbor risk but can throttle a latency-sensitive API and increase tail latency. A batch worker may tolerate slower completion in exchange for bounded CPU use. The policy should be measured, version/runtime aware, and documented; omission may be considered only with explicit governance and capacity controls.

**4. Explain memory sizing for pandas or a JVM service.**  
**Model answer:** Application-level heap/DataFrame estimates omit interpreter/runtime, native allocations, buffers, temporary arrays/data copies, thread stacks, direct buffers, and other overhead. Measure under representative peak workload; include transient allocations and uncertainty. A memory limit equal to request can be useful but increases scheduling reservation and is not universal.

**5. A Pod was evicted under node pressure. What evidence separates the causes?**  
**Model answer:** Inspect Pod status/reason, events, node pressure conditions, resource usage relative to requests, Pod priority, QoS, and kubelet/runtime logs where accessible. Do not assume QoS alone determines the outcome or conflate eviction with container OOM. Then assess whether capacity, declarations, priority, or workload behavior needs change.

## 14. Evidence Artifacts

Create this **suggested learner-owned local directory** manually. It is not a request to modify the repository automatically.

```text
evidence/
└── m03-unit-02-namespaces-resources/
    ├── environment-and-context.txt
    ├── namespace-and-labels.yaml
    ├── resourcequota.yaml
    ├── limitrange.yaml
    ├── before-usage.csv
    ├── after-usage.csv
    ├── quota-admission-failure.txt
    ├── qos-class-observations.txt
    ├── oomkill-evidence.txt
    ├── cpu-throttling-evidence.txt
    ├── eviction-evidence-or-simulation-note.txt
    ├── audit-script-output.txt
    ├── incident-runbook-exercise.md
    └── learner-decisions.md
```

| Artifact | Required content | Acceptance criterion |
|---|---|---|
| `environment-and-context.txt` | OS/runtime, kind/kubectl versions, context name, node image tag | Exact observed values; no credentials |
| `namespace-and-labels.yaml` | Applied namespace metadata | Labels and owner are consistent |
| `resourcequota.yaml` | Hard values and namespace | Keys and scope are verified |
| `limitrange.yaml` | Defaults/min/max/ratio | Policy is consistent with test workloads |
| `before-usage.csv` / `after-usage.csv` | Time, conditions, replicas, usage, requests/limits, caveats | No invented values; same conditions compared where possible |
| `quota-admission-failure.txt` | Exact API error and quota state | Admission versus scheduling distinction explained |
| `qos-class-observations.txt` | Effective Pod resources and observed QoS | Derived from actual object/status |
| `oomkill-evidence.txt` | Status, events, previous logs, limitations | Only claim OOMKill if evidence confirms it |
| `cpu-throttling-evidence.txt` | Metric source/name if available; otherwise limitation | No fabricated metric name or causal claim |
| `eviction-evidence-or-simulation-note.txt` | Node conditions/events, or explicit simulation note | If not reproduced, write “simulation/inspection only” and explain why |
| `audit-script-output.txt` | Command, fixture, output, exit status | Offline fixture used; no shared cluster |
| `incident-runbook-exercise.md` | Approval, change scope, capacity review, expiry, reversal, follow-up | Emergency procedure is auditable and reversible |
| `learner-decisions.md` | Namespace strategy, CPU policy, sizing assumptions, unresolved risks | Decision defended with evidence and trade-offs |

Redact tokens, kubeconfig data, private keys, customer data, and sensitive infrastructure details. A learner-created evidence file must distinguish actual observation, expected behavior, and inference.

## 15. Interview and Design-Review Questions

The five senior-level model answers in Section 13 are the primary interview bank. Use the following review prompts to deepen them:

- Which exact resource dimensions and object counts does the quota protect, and why?
- What evidence shows the LimitRange defaults actually applied to the admitted Pod?
- How does the namespace template avoid a hidden policy change affecting existing workload manifests?
- What is the smallest reversible emergency action, who can approve it, and when must it expire?
- Which production telemetry would change your resource decision, and what would falsify your current hypothesis?

A strong answer identifies the mechanism, evidence, assumptions, alternative hypotheses, mitigation risk, and follow-up. “Increase memory,” “add a namespace,” or “delete quota” without diagnosis is not a senior-level answer.

## 16. Sources, Claim Register, and Verification Notes

### Official sources to consult

Live official documentation was **not opened** in this authoring pass. Use the following canonical document names/titles to verify the chosen Kubernetes release. Where a URL is not supplied, locate it from the official documentation site rather than relying on a stale copied link.

1. Kubernetes documentation — **Namespaces**.
2. Kubernetes documentation — **Resource Quotas**.
3. Kubernetes documentation — **Limit Ranges**.
4. Kubernetes documentation — **Manage Resources for Containers**.
5. Kubernetes documentation — **Pod Quality of Service**.
6. Kubernetes documentation — **Configure Default Memory Requests and Limits for a Namespace**.
7. Kubernetes documentation — **Configure Default CPU Requests and Limits for a Namespace**.
8. Kubernetes documentation — **Resource Management for Pods and Containers**.
9. Kubernetes documentation — **Node-pressure Eviction**.
10. Kubernetes documentation — **Node Allocatable**.
11. Kubernetes documentation — **Assign Pods to Nodes**, **Priority and Preemption**.
12. Kubernetes API reference — `ResourceQuota`, `LimitRange`, Namespace metadata, Pod resource requirements, and `PriorityClass`.
13. Kubernetes documentation — **Version and Version Skew Support Policy**.
14. kind documentation — Quick Start, configuration, node images, and troubleshooting.
15. Metrics Server documentation — installation requirements and resource metrics API behavior.
16. Google SRE Book/Workbook — capacity planning, saturation, and incident response.
17. NSA/CISA — **Kubernetes Hardening Guidance**; verify edition and applicability.
18. Center for Internet Security — **CIS Kubernetes Benchmark**; verify version/distribution.

### Claim Register

| ID | Claim | Source document + section/title | Confidence | Tag / verification needed |
|---|---|---|---|---|
| C01 | Namespaces scope namespaced API objects and names | Kubernetes docs: Namespaces | High | Confirm resource scope with API discovery |
| C02 | Namespaces alone do not provide complete network isolation | Kubernetes docs: Network Policies; Namespaces | High | CNI enforcement varies |
| C03 | ResourceQuota constrains aggregate namespace resource/object accounting | Kubernetes docs: Resource Quotas | High | Verify keys and scopes for chosen release |
| C04 | Quota does not reserve physical node capacity | Resource Quotas; Scheduling concepts | High | General mechanism; validate cluster-specific policy |
| C05 | LimitRange can default and constrain resource values | Kubernetes docs: Limit Ranges | High | Verify exact API fields/defaulting behavior |
| C06 | LimitRange defaults can affect effective resource declarations and accounting | Limit Ranges; Resource Quotas | Medium | Test with selected release and policy combination |
| C07 | Requests influence scheduling; limits are runtime constraints | Manage Resources for Containers | High | Runtime/kernel behavior varies |
| C08 | CPU can be throttled under CPU limit enforcement | Manage Resources for Containers; cgroup documentation | High | Verify runtime/cgroup setup |
| C09 | Exceeding a container memory limit can result in OOM termination | Manage Resources for Containers | High | Confirm actual reason and node conditions |
| C10 | OOMKill and kubelet node-pressure eviction are distinct | Node-pressure Eviction; Pod status docs | High | Inspect actual event/status |
| C11 | QoS classification depends on effective CPU/memory requests/limits | Pod Quality of Service | High | Edge cases and release details must be checked |
| C12 | Eviction decisions include usage relative to requests and Pod priority as well as QoS considerations | Node-pressure Eviction | High | Verify exact current decision logic |
| C13 | `kubectl top` relies on the resource metrics API, commonly Metrics Server | Metrics Server docs; Resource Metrics Pipeline | High | Verify API registration and compatibility |
| C14 | `kubectl top` is not a durable historical time series | Metrics Server docs | High | Use monitoring history for trend/percentile analysis |
| C15 | p95/p99 require representative observations and adequate samples | Statistical practice; SRE measurement principles | High | Define population/window; no universal sample count asserted |
| C16 | CPU-limit policy has latency/noisy-neighbor trade-offs | Resource management docs; workload measurements | Medium | Current recommendations marked [VERIFY] |
| C17 | Memory limit equal to request can increase declared reservation and may support Guaranteed QoS if all criteria hold | Pod Quality of Service; resource management docs | High | Not a universal recommendation |
| C18 | Python/pandas memory may include native allocations and temporary copies beyond logical object estimates | Python/pandas/runtime docs to verify | Medium | Measure application-specific behavior; no universal overhead ratio |
| C19 | JVM heap is not total process/container memory | JVM container/runtime docs to verify | Medium | Verify selected JVM version/options |
| C20 | Node allocatable differs from total node capacity | Kubernetes docs: Node Allocatable | High | Provider/node configuration varies |
| C21 | `system-reserved` and `kube-reserved` have different reservation purposes | Kubernetes docs: Node Allocatable | High | Exact configuration varies by distribution |
| C22 | PriorityClass/preemption does not guarantee capacity or universal recovery | Kubernetes docs: Priority and Preemption | High | Verify selected scheduler behavior |
| C23 | kind nodes share host-level resources and do not prove independent production failure domains | kind docs: design/limitations; general container behavior | High | Verify current kind docs and runtime |
| C24 | Forcing node pressure in kind may be unsafe or unrepresentative | kind docs; Node-pressure Eviction | Medium | This lesson substitutes inspection/simulation |
| C25 | Emergency quota increases do not create node capacity | Resource Quotas; scheduling concepts | High | Always inspect allocatable and placement |
| C26 | Governance labels support reporting only if a consumer interprets them | Kubernetes labels/annotations concepts | High | Verify automation/reporting integration |
| C27 | Quota-as-code and namespace vending require lifecycle, validation, authorization, and drift handling | Platform engineering design inference | Medium | Review against local platform architecture; M16 forward reference |
| C28 | Hierarchical namespaces, Capsule, and vcluster address tenancy organization/delegation problems | Project documentation to verify | Medium | Awareness only; verify activity and compatibility |
| C29 | Audit script cannot prove runtime usage, cluster admission behavior, or production safety | Script scope/design | High | It checks only local JSON input |
| C30 | Object-count and storage quota key availability/semantics can depend on API/resource/storage setup | Kubernetes docs: Resource Quotas/API reference | Medium | Verify exact keys and StorageClass behavior |

### Verification log template

```text
Date checked:
Kubernetes version/minor:
kind version:
kind node image tag:
Host OS / WSL2 version:
Container runtime/version:
Cgroup mode/version (if known):
ResourceQuota API fields/keys verified:
LimitRange API fields/defaulting verified:
QoS and eviction docs verified:
Metrics Server version/compatibility verified:
Node allocatable/reserved config reviewed:
Example image tags/behavior verified:
Commands actually executed:
Tests not executed:
Open [VERIFY] items:
```

## 17. Final Self-Audit and Sign-Off

### Ten-pass audit

| Pass | Result (PASS / FIXED / OPEN) | Defects found | Corrections applied | Residual risk |
|---|---|---|---|---|
| 1. Scope completeness | PASS | Broad syllabus has many requirements | Covered all named topic groups and four labs | Human review should map to full authoritative syllabus |
| 2. Technical/API accuracy | OPEN | Some exact behavior depends on Kubernetes minor and admission implementation | Marked version-sensitive claims and listed official sources | Live docs not checked |
| 3. Manifest consistency | OPEN | Example image compatibility and exact LimitRange/defaulting behavior not tested | Namespaces and labels are internally aligned; examples labeled illustrative | Apply/validation not executed |
| 4. Command and script executability | OPEN | Commands depend on environment, permissions, images, and cluster state | Commands include purpose, representative output, and placeholders; audit script is self-contained | No commands or script executed |
| 5. Version currency | OPEN | Kubernetes/kind/Metrics Server versions not selected | No current version invented; verification checklist included | Verify support/skew and compatibility before labs |
| 6. Security/isolation correctness | PASS | Namespace could be misread as security boundary | Explicitly separates RBAC, admission, network and node controls | Full security review is deferred |
| 7. Measurement and data integrity | PASS | Risk of treating tiny samples as p95/p99 or fabricating outputs | Outputs labeled illustrative; CSVs use placeholders; sample limitations explained | Learner must collect real evidence |
| 8. Teaching progression and scope boundaries | PASS | Risk of duplicating later modules | Level 1–4 progression and forward references included | Full later modules not reviewed here |
| 9. Adversarial production review | PASS | Quota change could be framed as delete-and-retry | Emergency process requires approval, capacity review, expiry, reversal and post-incident follow-up | Organization-specific authorization required |
| 10. Lab safety and resource feasibility | PASS with OPEN items | Node-pressure eviction is unsafe/unreliable to force on a laptop | Replaced forced pressure with inspection/simulation path; bounded sequential experiments | OOM/CPU workload must be independently bounded and verified |

### Remaining verification actions

- Check official documentation for the selected Kubernetes minor, especially ResourceQuota keys, LimitRange defaulting, QoS, node-pressure eviction, PriorityClass/preemption, and Node Allocatable.
- Verify the kind node image, Metrics Server compatibility, and exact lab image behavior.
- Execute Labs A–D only on a disposable local kind cluster after confirming context and resource budget.
- Do not force node pressure on a personal workstation. If no safe reproducible event occurs, record “simulation/inspection only.”
- Validate the audit script against its local fixture and review its policy assumptions.
- Have a platform/SRE reviewer approve production quota policy and emergency change procedures.

```text
Content status: DRAFT-AUDITED
Audit date: 2026-10-25 (system date at authoring)
Auditor: AI self-audit (requires human verification)
Open verification items: 6 categories (live docs, API/version details, images, lab execution, runtime/cgroup behavior, production policy review)
Execution status: Commands/labs not executed unless explicitly evidenced
```

A self-audit is not a substitute for running manifests and labs against a disposable `kind` cluster and checking version-sensitive claims against current official documentation. This file is a substantial instructional draft with explicit safety boundaries and evidence requirements, not a verified production runbook.
