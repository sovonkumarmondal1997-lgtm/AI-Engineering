# Horizontal and Vertical Autoscaling

## Lesson metadata

| Field | Details |
|---|---|
| Roadmap | Stage 2E — Production DevOps & Platform Engineering |
| Module / unit | M03 — Production Kubernetes Operations, Unit 6 |
| Level progression | L1 beginner → L2 intermediate → L3 advanced → L4 expert |
| Estimated time | 12–16 hours, including four core labs; optional VPA exercise adds 1–2 hours |
| Prerequisites | Linux, Git, Docker/container images, `kubectl`, basic Pods and Deployments, resource requests/limits from Unit 2, readiness probes from Unit 3 |
| Tools | `kubectl`, `kind`, Metrics Server, Python 3 standard library, optional VPA/custom-metrics tooling for awareness only |
| Review date | 2026-10-25 |
| Kubernetes support baseline | Use the Kubernetes version supported by the installed `kind` release and verify client/server skew guidance before creating a cluster. Do not assume a particular version is current. |
| Verification status | No live documentation lookup, cluster execution, or lab execution was performed while authoring this lesson. Version-sensitive claims are marked `[VERIFY]`. |

> **Safety contract:** The labs are for a dedicated, disposable local `kind` cluster only. Never run the exercises against production or a shared cluster. Load is bounded, and no exercise intentionally exhausts the host machine. This lesson documents experiments; it does not claim they were executed.

## Why autoscaling matters in production

Demand changes. A scoring API may see a burst after a batch job completes; a queue worker may fall behind after an upstream import; a model-serving process may need more CPU during inference; and memory usage may reflect model weights or caches rather than current traffic. Static capacity can be wasteful during quiet periods and inadequate during peaks.

Autoscaling is a feedback-control problem. A controller observes a signal, compares it with a target, and changes a desired state. Kubernetes then reconciles that state, but the change takes time: new Pods must be admitted, scheduled, have images available, initialize, pass readiness checks, and begin serving. If node capacity is insufficient, additional replicas can remain Pending. Scaling is not instantaneous and does not guarantee that latency stays within an SLO.

Three distinct layers matter:

1. **Horizontal Pod autoscaling (HPA):** changes the number of Pod replicas for a supported scalable target.
2. **Vertical Pod autoscaling (VPA):** recommends or adjusts resource sizing for containers, depending on its implementation and mode.
3. **Cluster/node autoscaling:** changes node capacity. HPA does not itself create worker nodes.

A reliable design chooses a metric that reflects the bottleneck, sets resource requests that make utilization meaningful, provides safe replica bounds, accounts for startup delay and downstream limits, and measures user-visible outcomes. A CPU target is not a substitute for request latency; memory usage is not always a good scale-out signal; queue depth is not useful if more workers would overload the database.

## Learning objectives

- [L1] Explain the difference between HPA, VPA, and node autoscaling, including their control loops and delays.
- [L1] Interpret requests, limits, observed usage, utilization, desired/current/ready replicas, and Metrics Server output.
- [L2] Write and inspect an `autoscaling/v2` HPA with correct target references, resource requests, bounds, metrics, and behavior controls.
- [L2] Diagnose an HPA reporting `<unknown>` using read-only checks of the HPA, Metrics API, Pods, requests, and events.
- [L3] Choose among CPU, memory, request rate, queue lag, custom metrics, and external metrics based on the workload bottleneck and failure modes.
- [L3] Explain HPA flapping, startup lag, HPA/VPA resource ownership, and interactions with rollouts, PDBs, quotas, scheduling, and stateful workloads.
- [L3] Demonstrate bounded scale-up/scale-down behavior in a disposable kind cluster and record actual evidence.
- [L4] Design capacity-aware scaling limits, SLI/SLO guardrails, fairness controls, and an incident response for capacity starvation.
- [L4] Defend an autoscaling design for an API and queue worker, including downstream bottlenecks, cost, cold starts, and unresolved assumptions.

## Prerequisite refresher and scope boundaries

| In scope | Deferred / cross-reference |
|---|---|
| HPA, resource utilization, Metrics Server, scaling behavior, custom/external metric architecture | Full metrics stack and alerting implementation → M11 |
| VPA modes and HPA/VPA ownership considerations | Production VPA installation and policy design; verify upstream support |
| Replica, request, capacity, and queue-lag trade-offs | Namespace quotas and resource governance → M03 Unit 2 |
| Readiness/startup effects on scaling | Probe design and recovery → M03 Unit 3 |
| Deployment/StatefulSet/Job/CronJob scaling boundaries | Controller fundamentals → M03 Unit 4 |
| PDB, replica availability, and maintenance interaction | PDB and graceful shutdown → M03 Unit 5 |
| Scheduling, Pending Pods, node capacity and placement awareness | Taints, affinity, topology spread, and node pools → M03 Unit 7 |
| Metrics access and least-privilege awareness | Full RBAC/PSS → M03 Unit 9 |
| Scaling SLI/SLO, capacity and cost trade-offs | Broader capacity/FinOps → M15; SRE program → M10 |
| Manifest hand-off and change review | CI/CD → M02; Helm/Kustomize → M06; GitOps/progressive delivery → M08 |
| No production broker required; queue lag can be synthetic or conceptual | Storage internals → M05; networking internals → M04; secrets → M09; DR → M13; multi-cluster → M14 |

## Glossary

| Term | Definition | Operational significance |
|---|---|---|
| HPA | HorizontalPodAutoscaler controller that adjusts a scalable target's replica count from configured metrics | Adds/removes Pod replicas, but does not create node capacity |
| VPA | Vertical Pod Autoscaler system that recommends or adjusts resource requests, depending on mode and implementation | Helps size containers; updates may require Pod recreation or have version-dependent behavior |
| Node autoscaler | System that changes node capacity in response to scheduling/capacity needs | Bridges Pending Pods to more cluster capacity; not available as real provisioning in kind |
| Resource request | Resource quantity used for scheduling and as a baseline for certain utilization calculations | Incorrect requests distort utilization and scheduling decisions |
| Resource limit | Runtime resource ceiling enforced according to the resource and platform behavior | A too-low CPU limit may throttle; a memory limit can lead to OOM termination |
| Observed usage | Measured consumption at a point or over a sampling window | Metrics are sampled, may lag, and are not a full workload benchmark |
| Utilization | Usage expressed relative to a configured request for resource-utilization metrics | CPU utilization target depends on requests |
| Desired replicas | Replica count the HPA computes or requests | May differ from actual or ready replicas |
| Current replicas | Current replica count reported by the target/controller | Does not imply all Pods are healthy |
| Ready / available replicas | Pods meeting the relevant readiness/availability condition | More directly related to serving capacity, but not equal to successful client requests |
| Metrics Server | Lightweight resource-metrics source used by common resource metrics APIs and `kubectl top` | Not a full historical monitoring system or general custom-metrics store |
| Custom metric | Application/workload metric exposed through an appropriate metrics API integration | Can reflect request rate, queue lag, or domain-specific pressure |
| External metric | Metric sourced outside the Kubernetes object metric model and exposed through an adapter/API integration | Useful for queues or external systems when configured correctly |
| Stabilization window | Window used by HPA behavior to dampen rapid scaling decisions | Reduces oscillation at the cost of slower response |
| Scaling policy | Rate limit for how many replicas may be added or removed over a period | Controls aggressiveness and risk |
| Flapping / thrashing | Repeated rapid scale-up and scale-down oscillation | Causes churn, cold starts, and unstable latency |
| Pending Pod | Pod not yet scheduled onto a node | May indicate capacity or constraint problems; does not automatically mean node autoscaling is configured |
| Node allocatable | Node resources available to Pods after system reservations and related overhead | Capacity calculations should not use raw machine size alone |
| Queue lag | Amount of work waiting or age of the oldest unprocessed item | Can be a useful worker-scaling signal if downstream capacity and semantics are understood |
| Cold start | Time needed for a new replica to initialize and become useful | Model loading, cache warm-up, image pull, and readiness can delay capacity |
| SLI / SLO | Service-level indicator / objective | Scaling changes must be judged against user-visible reliability, not replica count alone |

## Autoscaling mental model

```text
                 Metrics source
          (resource / custom / external)
                       |
                       v
              Metrics API / adapter
                       |
                       v
                HPA controller
          (target, bounds, behavior)
                       |
                       v
              Scalable target
          (e.g. Deployment replicas)
                       |
                       v
                   Scheduler
                       |
             +---------+----------+
             |                    |
     feasible node exists     no feasible node
             |                    |
             v                    v
      Pod starts on node     Pod remains Pending
             |                    |
             v                    v
   image/init/warm-up       node autoscaler may
             |              provision capacity
             v                    |
      readiness succeeds <--------+
             |
             v
        serve workload
             |
             v
     new metrics / feedback
```

HPA's loop changes the desired replica count. It does not directly schedule Pods, make an image pull faster, repair a failing readiness probe, or provision nodes. A node autoscaler may react to unschedulable Pods, but its behavior depends on the chosen implementation and environment. `kind` uses local containers as nodes; it does not provision cloud machines.

### The simplified replica formula

A common single-metric mental model is:

\[
\text{desiredReplicas} =
\left\lceil
\text{currentReplicas}
\times
\frac{\text{currentMetric}}{\text{targetMetric}}
\right\rceil
\]

For example, if three replicas are each averaging a metric that is 1.5 times the target, the simplified calculation suggests \(\lceil 3 \times 1.5\rceil = 5\) replicas, subject to configured bounds.

This is **not the entire HPA algorithm**. Real behavior includes tolerance, missing metrics, readiness handling, multiple metrics, scaling policies, stabilization windows, minimum/maximum replicas, and controller reconciliation. When multiple metrics are configured, the controller does not simply average them into one number; verify current official algorithm details and version behavior. `[VERIFY]`

## L1 — Beginner: understand autoscaling

### 1. Why autoscaling exists

Autoscaling can reduce manual toil and improve response to changing demand, but it trades off latency, cost, and complexity.

- **Too little capacity:** latency and errors increase, queues grow, or requests time out.
- **Too much fixed capacity:** idle resources cost money and reduce shared-cluster fairness.
- **Scaling too late:** the control loop reacts after the workload is already degraded.
- **Scaling the wrong thing:** more API replicas do not fix a saturated database; more queue consumers may worsen downstream contention.
- **Scaling too aggressively:** frequent starts/stops create cold starts, cache churn, and unstable latency.

The objective is not “maximize replicas.” It is to maintain the required service level at a reasonable cost while respecting downstream and cluster constraints.

### 2. HPA, VPA, and node autoscaling

| Layer | What changes | Typical signal / purpose | What it cannot guarantee |
|---|---|---|---|
| HPA | Replica count | CPU utilization, memory utilization, custom or external metrics | Does not create node capacity or guarantee the new Pods become Ready |
| VPA | Container resource recommendations/requests, and possibly applied sizing depending on mode | Historical/current resource behavior and sizing recommendations | Does not replace horizontal capacity or guarantee no disruption |
| Node autoscaling | Node count/capacity | Unschedulable Pods and configured capacity logic | Does not instantly create a node or solve every scheduling constraint |

A service may need more replicas, more CPU per replica, and more node capacity at the same time—but those are separate decisions and controllers.

### 3. Requests, limits, and utilization

A **request** is used in scheduling and is the baseline for CPU utilization targets in common HPA resource metrics. A **limit** constrains resource use according to runtime behavior. **Observed usage** is a measured value. **Utilization** for a resource utilization target is usage relative to the configured request, not relative to the limit.

For example, if a container requests `200m` CPU and uses `100m`, its CPU usage is approximately 50% of that request for the relevant sample. If the request is missing, a CPU utilization percentage may be unavailable for that Pod; HPA may be unable to calculate the resource metric as intended. Verify exact behavior in the current docs and cluster. `[VERIFY]`

Memory requires special care. A process can retain heap pages or caches after traffic drops, so memory may not fall in proportion to demand. Adding replicas can multiply memory use. A memory target can still be useful when memory pressure is the actual bottleneck, but it must be selected deliberately.

### 4. Metrics Server and evidence tools

Metrics Server supplies resource usage metrics for common Kubernetes workflows; it is not a general-purpose historical time-series database or a universal source for application-specific metrics.

| Command | What it helps answer | What it cannot prove |
|---|---|---|
| `kubectl top nodes` | Recent resource usage reported through the resource metrics pipeline | Long-term trends, exact peak usage, or full node capacity by itself |
| `kubectl top pods -n <namespace>` | Recent per-Pod resource usage | Application latency or whether a Pod is meeting its SLO |
| `kubectl get hpa -n <namespace>` | Current HPA summary, targets and replica counts | Root cause of every scaling issue |
| `kubectl describe hpa -n <namespace> <name>` | HPA conditions, events and target details | A condition alone does not establish the entire root cause |
| `kubectl get pods -n <namespace> -w` | Pod state changes over time | Whether new Pods serve successful requests |
| `kubectl get events -n <namespace> --sort-by=.lastTimestamp` | Recent events in a convenient order | Complete durable history; field availability/output is `[VERIFY]` |
| `kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes` | Whether a common resource metrics API endpoint responds | That every metric is fresh or every Pod has valid metrics; endpoint support is `[VERIFY]` |

Use commands as evidence, not as substitutes for application-level measurements. `kubectl top` can help explain a resource target, but pair it with latency/error rate, readiness, and replica timeline.

### 5. Three scaling layers in a data pipeline

- **FastAPI scoring API:** scale replicas based on CPU, request rate, or a suitable latency-related/custom signal. CPU can be useful for compute-heavy inference, but request latency and model warm-up still matter.
- **Queue worker:** queue lag or oldest-message age may better represent backlog than CPU. Add limits so more workers do not overwhelm the database or external API.
- **Stateful dependency:** a PostgreSQL or Redis StatefulSet usually needs application-specific replication and operational guidance. Do not assume a generic HPA makes a database safely horizontally scalable.
- **Batch ETL Job:** standard HPA does not automatically turn every Job into a horizontally scalable queue consumer. Parallelism and retry semantics are workload/controller-specific.
- **CronJob:** schedule and concurrency policy govern runs; a generic HPA does not automatically scale CronJobs as if they were a Deployment.

## L2 — Intermediate: configure and test HPA

### 1. `autoscaling/v2` resource-metric HPA

The following examples use `autoscaling/v2`, a Deployment target, and explicit CPU requests. Confirm the API is served by the installed cluster before applying. `[VERIFY]`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  namespace: autoscaling-lab
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring-api
    spec:
      containers:
        - name: api
          image: <REPLACE_WITH_VERIFIED_HTTP_IMAGE>
          ports:
            - name: http
              containerPort: 8080
          resources:
            requests:
              cpu: 200m
              memory: 128Mi
            limits:
              cpu: "1"
              memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
  namespace: autoscaling-lab
spec:
  selector:
    app.kubernetes.io/name: scoring-api
  ports:
    - name: http
      port: 80
      targetPort: http
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: scoring-api-hpa
  namespace: autoscaling-lab
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scoring-api
  minReplicas: 2
  maxReplicas: 6
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      selectPolicy: Max
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
        - type: Pods
          value: 2
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      selectPolicy: Max
      policies:
        - type: Percent
          value: 25
          periodSeconds: 60
```

**Example interpretation:** the target is 60% average CPU utilization relative to requests, not 60% of CPU limits. The sample behavior explicitly allows a fast scale-up policy and a more conservative scale-down window. These are teaching values, not universal defaults or production recommendations. Verify current field support and default behavior before use. `[VERIFY]`

The image is a placeholder. Replace it with a verified image that listens on port 8080 and responds to HTTP requests, or build/load a local image following M01. Do not assume a local registry exists.

### 2. Memory utilization example

This is a separate alternative HPA, not a second HPA to apply to the same target alongside the CPU HPA. Use it only after verifying the memory metric semantics and confirming that memory tracks the workload's limiting factor.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: scoring-api-memory-hpa
  namespace: autoscaling-lab
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scoring-api
  minReplicas: 2
  maxReplicas: 6
  metrics:
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 70
```

The target must be interpreted relative to memory requests in the relevant resource metrics model. This example may be a poor policy for applications whose memory footprint remains high after traffic falls. Avoid two competing HPAs attempting to control the same target; select one deliberate policy.

### 3. Understanding HPA behavior controls

| Field | Purpose | Trade-off / verification |
|---|---|---|
| `behavior.scaleUp` | Controls scale-up rate and stabilization behavior | Faster growth can improve response but may overload downstream systems or hit quota/capacity |
| `behavior.scaleDown` | Controls scale-down rate and stabilization behavior | Conservative downscaling reduces churn but retains idle cost longer |
| `stabilizationWindowSeconds` | Dampens decisions by considering recent recommendations according to the documented algorithm | Longer windows reduce oscillation but can delay response |
| `selectPolicy` | Chooses how configured scaling policies are selected when more than one applies | Verify the exact supported values and semantics for the installed version |
| `policies` | Defines rate limits using pod counts or percentages over a period | Check whether the chosen policy is sufficiently conservative for the service |
| `periodSeconds` | Window over which a policy's change limit applies | Exact constraints and behavior are API-version-sensitive `[VERIFY]` |
| `type: Pods` | Policy uses an absolute number of replicas | Easier to reason about for small workloads |
| `type: Percent` | Policy uses a percentage of current replicas | Rounding and small replica counts can matter `[VERIFY]` |

Do not infer defaults from this example. If a field is omitted, the API/controller may apply documented defaults that can change across versions. Inspect the current API reference and `kubectl explain horizontalpodautoscaler.spec.behavior`.

### 4. Load generation with a hard stop

A safe local load test is bounded in time and rate. The following standard-library client makes sequential requests for at most 30 seconds; it is a smoke-test generator, not a realistic concurrency or capacity benchmark.

```python
import time
import urllib.error
import urllib.request

url = "http://127.0.0.1:18080/"
duration_seconds = 30
interval_seconds = 0.1
deadline = time.monotonic() + duration_seconds
total = successes = failures = 0

while time.monotonic() < deadline:
    total += 1
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            if 200 <= response.status < 400:
                successes += 1
            else:
                failures += 1
    except (urllib.error.URLError, TimeoutError):
        failures += 1
    time.sleep(interval_seconds)

print({
    "total": total,
    "successes": successes,
    "failures": failures,
    "success_rate": successes / total if total else None,
})
```

Run it only after the Service is port-forwarded and the verified image responds at the chosen path. Stop by allowing the script to finish; if you use a separate load tool, document its exact stop command and rate cap.

### 5. HPA conditions and diagnosis

`kubectl describe hpa` may show conditions including:

- **`AbleToScale`:** whether the controller can obtain/update the scale target in the current situation. A false condition needs inspection of the reason/message and events.
- **`ScalingActive`:** whether the HPA can calculate scaling from its configured metrics. False may indicate metric/configuration issues.
- **`ScalingLimited`:** whether the computed desired scale is constrained by configured bounds or policies. True can be expected when the workload reaches a configured limit.

These are diagnostic clues, not complete root-cause statements. Exact reason strings and details are version-sensitive. `[VERIFY]`

### 6. Why metrics show `<unknown>`

Common hypotheses include:
- Metrics Server is absent, not ready, or unable to reach kubelets.
- The metrics API is not available or has errors.
- Metrics are missing or stale for one or more Pods.
- Resource requests required for utilization calculation are missing.
- The HPA references the wrong target or metric.
- A custom/external metric selector or adapter is misconfigured.
- The workload has not yet produced usable samples.

Read-only diagnostic sequence:

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get hpa -n <namespace>
kubectl describe hpa -n <namespace> <hpa-name>
kubectl get pods -n kube-system
kubectl top nodes
kubectl top pods -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
kubectl get deployment -n <namespace> <deployment-name> -o yaml
kubectl explain horizontalpodautoscaler.spec.metrics
kubectl explain horizontalpodautoscaler.spec.behavior
```

For Metrics Server-specific diagnosis, inspect its Pod status/logs and the APIService registration using read-only commands, if the installed cluster exposes those resources. Avoid applying an unverified TLS workaround as the first response.

### 7. Illustrative scaling timeline

**Illustrative example — your output will differ.**

| Relative time | Event | What to observe |
|---|---|---|
| T+00s | Load begins to increase | Client request rate and latency |
| T+20s | Resource metrics reflect increased usage | `kubectl top pods`, acknowledging sample delay |
| T+30s | HPA calculates a higher desired replica count | HPA target/desired/current counts and conditions |
| T+35s | New Pods are created | `kubectl get pods -w` |
| T+35–90s | Scheduler, image pull, initialization and warm-up occur | Pending reason, Pod events, startup logs |
| T+60–120s | New Pods become Ready if startup succeeds | Ready replicas and client latency |
| Later | Load decreases and downscale behavior applies | Replica timeline, stabilization and resource usage |

This is an illustrative sequence, not a promised timing profile. Your environment's image pull, resource limits, metrics sampling, startup behavior, and scheduling will determine actual timings.

## L3 — Advanced: metric selection, VPA, and scaling interactions

### 1. Select metrics based on the bottleneck

| Workload / signal | Why it can help | Failure mode | Caveats |
|---|---|---|---|
| CPU utilization | Useful for compute-bound API/inference when CPU tracks demand | CPU may be throttled or unrelated to latency | Requires meaningful requests for utilization-based targets |
| Memory utilization | Useful when memory pressure or per-replica footprint is the bottleneck | Retained heap/cache may not fall with load; more replicas multiply memory | Watch total memory and OOM risk, not just per-Pod percentage |
| Request rate | Can reflect incoming demand more directly than CPU | Request cost varies; rate alone may ignore expensive requests | Requires correct metric collection and adapter/API |
| Latency | Closely relates to user experience | Reactive signal may be late and noisy; tail latency needs careful aggregation | Scaling cannot fix every latency cause; dependencies may be saturated |
| Queue depth / oldest-message age | Captures backlog for workers | Queue count may be misleading if message cost varies; stale metrics can trigger bad decisions | Bound consumer concurrency and protect downstream systems |
| Custom metric | Models domain-specific pressure, e.g. active jobs or concurrency | Metric pipeline/selector errors or cardinality issues | Requires a supported custom-metrics integration |
| External metric | Uses a signal from a broker or external service | Adapter/API outage or stale values | Requires external metrics integration and well-defined semantics |

The best signal is the one that leads to the desired service outcome without creating an unstable or unsafe feedback loop. Use more than one metric only when the combination is understood and tested.

### 2. Memory is sometimes useful, sometimes misleading

Memory can be a meaningful scaling signal when each replica has a bounded working set that grows with active demand or when memory pressure directly threatens reliability. It is often a weak proxy for current load when runtimes retain heaps, caches, loaded models, or memory arenas after requests complete.

If memory remains high after traffic falls, HPA may keep or add replicas. If every new replica loads a large model, scale-out can increase total cluster memory dramatically and cause Pending Pods or OOM kills. Before selecting memory, measure memory over realistic workload phases and understand the application's memory model.

### 3. Custom and external metrics architecture

At an awareness level, the path is:

```text
Application / queue / external system
                |
                v
       Metrics exporter/source
                |
                v
     Adapter / custom or external API
                |
                v
        HPA controller calculation
                |
                v
        Scalable target replicas
```

Prometheus Adapter and KEDA are common ecosystem options to investigate, depending on whether the metric comes from Prometheus or a supported event source. This lesson does not provide a verified install manifest or a production configuration. Consult their current official documentation and M11 before adopting either. A synthetic queue metric in a local exercise is a teaching simulation, not a live broker integration.

### 4. HPA flapping / thrashing

Flapping is repeated scale-up and scale-down that can cause cold starts, image-pull pressure, cache churn, and inconsistent latency. Likely causes include:
- noisy or delayed metrics;
- aggressive scale-down behavior;
- insufficient stabilization;
- startup delay causing the controller to react before new replicas become useful;
- requests that do not reflect normal consumption;
- load generator oscillation;
- downstream saturation, causing more replicas without more throughput.

**Diagnostic method:**
1. Capture timestamps for load, metrics, HPA desired/current replicas, ready replicas, and request latency.
2. Determine whether the metric changes before or after the user-visible problem.
3. Change one parameter at a time.
4. Use a conservative scale-down policy and sufficient observation window when evidence supports it.
5. Re-run the same bounded profile and compare outcomes.
6. Record both improvements and costs, such as extra replica-minutes or slower scale-down.

Do not tune from a single screenshot or assume that a smoother replica curve proves better user experience.

### 5. Interactions with other Kubernetes controls

**Deployment rollouts.** HPA may change the Deployment's desired replica count while a rollout is in progress. Capacity, surge replicas, readiness, and rollout limits interact. Inspect both HPA and Deployment rollout status.

**PDB.** HPA changes desired replicas and therefore can change PDB status. PDBs govern supported voluntary disruption, not normal HPA scaling as a universal mechanism. Re-check PDB health before maintenance; see Unit 5.

**Readiness/startup probes.** Slow initialization or inaccurate readiness can make new replicas take longer to contribute capacity. Readiness is not the same as process existence. See Unit 3.

**Requests, limits, and quota.** Utilization depends on requests; requests also affect scheduling. Namespace quota can reject or constrain additional Pods. A low request can make a utilization target look low while the Pod is actually saturated; an overly high request can make Pods unschedulable.

**Placement constraints.** Taints, affinity, topology spread, and node selectors can prevent replicas from landing where expected. See Unit 7.

**HPA max versus cluster capacity.** `maxReplicas` caps the HPA target. Even below that cap, Pods can remain Pending if the cluster lacks feasible capacity. A high cap does not guarantee the cluster can run the replicas.

**Jobs/CronJobs.** Do not assume standard HPA automatically scales arbitrary Jobs or CronJobs. A worker architecture may need a Deployment or an appropriate controller/integration. Job parallelism and schedule semantics are distinct.

**Stateful workloads.** Scaling database replicas is not equivalent to safely scaling a stateless API. Application-level replication, quorum, storage, and consistency rules remain authoritative.

### 6. Startup time and scale-up lag

The time from load increase to useful capacity can include:
- metric sampling and controller reconciliation;
- HPA calculation and target update;
- scheduling and resource admission;
- image pull or local image availability;
- process startup, model load, cache warm-up;
- readiness checks and endpoint propagation.

A scale-up policy can react quickly while useful capacity arrives late. Mitigations include realistic minimum replicas for latency-sensitive services, smaller images and efficient startup (M01), pre-warming where justified, well-designed readiness probes (Unit 3), capacity headroom, and alerting on pending duration and service latency. These mitigations have costs; measure before adopting them.

### 7. VPA: recommendation and update modes

Vertical Pod Autoscaler (VPA) is an upstream project with its own components and installation/version compatibility considerations. Its modes have specific meanings that can change over time; check the current VPA documentation before configuring them. `[VERIFY]`

| Mode name in this lesson | Conceptual intent | Operational concern |
|---|---|---|
| `Off` | Produce recommendations without applying them, where supported by the installed VPA version | Safest starting posture for learning; confirm the actual installed version's mode semantics |
| `Initial` | Apply sizing when a Pod is created, where supported | Existing Pods may not be changed; new Pods can start with different requests |
| `Recreate` | Apply recommendations by evicting/recreating Pods, where supported | Can cause disruption and must be coordinated with PDBs and workload availability |
| `Auto` | Historical/current mode name whose exact behavior must be checked in the installed version | Do not assume it means a particular in-place update or recreation path |

Do not install VPA automatically in a small local cluster if it would consume too much memory or require unsupported components. A recommendation-only exercise is useful only when installation is supported and its resource costs are acceptable. Compare recommendations with observed load, latency, replica behavior, and scheduling requirements; a recommender cannot know every business constraint.

### 8. HPA and VPA together

HPA and VPA can be complementary when they have clear ownership of different dimensions. A common conflict arises when HPA uses CPU utilization relative to requests while VPA changes those same CPU requests: changing the denominator can change the utilization signal and therefore the HPA decision.

This does not mean every HPA/VPA combination is universally impossible. Compatibility depends on metric choice, VPA mode, implementation/version, and configuration. Verify the current VPA documentation and test the intended combination. `[VERIFY]` A safer design review explicitly assigns ownership: for example, HPA scales replicas based on a metric that remains meaningful while VPA recommends resource sizing for review.

### 9. In-place Pod resize

In-place resource resize is a version-sensitive Kubernetes capability. Feature maturity, supported resource types, kubelet/runtime requirements, API shape, and limitations can change between releases. Treat this section as conceptual only and consult the release notes and API docs for the exact cluster version before relying on it. `[VERIFY]`

Do not describe in-place resize as universally available or assume it eliminates all disruption. Even if supported, a resize may be constrained by node capacity and runtime behavior.

### 10. Cluster Autoscaler / Karpenter awareness

The conceptual loop is:

1. HPA requests more replicas.
2. The scheduler finds no feasible node for some Pods.
3. Pods remain Pending with scheduling evidence.
4. A configured node autoscaler may identify a capacity solution and provision nodes.
5. Nodes register and become Ready.
6. Pending Pods schedule, initialize, and pass readiness.
7. Useful capacity arrives after all those steps.

Cluster Autoscaler and Karpenter are distinct systems with different configuration models and provider integrations. `kind` does not provision real cloud nodes, so local labs can simulate the decision logic but cannot validate node creation, cloud quotas, machine boot time, or provider-specific failure handling. `[VERIFY]`

### 11. Queue lag and consumer scaling

Queue lag can be a better worker signal than CPU when the objective is to drain backlog within a service target. But a naive “more messages means more workers” policy can overload a database or third-party API.

Guardrails should include:
- maximum replicas and per-worker concurrency;
- downstream connection-pool and rate-limit budgets;
- queue lease/visibility semantics and retry policy;
- idempotent side effects and poison-message handling;
- oldest-message age and completion latency, not only raw count;
- a saturation signal for the downstream dependency;
- a clear scale-down policy that lets in-flight work finish safely.

A synthetic metric can teach the control concept, but production scaling requires a real, verified metric pipeline and correct operational semantics.

## L4 — Expert: capacity, SLOs, and cost-aware design

### 1. Capacity-aware scaling

A replica limit is only one constraint. Capacity planning must account for:
- requests for CPU, memory, and other resources;
- node allocatable rather than raw machine capacity;
- system Pods and DaemonSet overhead;
- namespace quota and admission policy;
- topology, affinity, taints, and node selectors;
- startup time and image/model warm-up;
- downstream service limits;
- spare headroom for maintenance and failure.

Do not plan from average observed CPU alone. Scheduling is based on resource requests and constraints; a cluster can have apparent free CPU but no node that satisfies a Pod's placement or memory requirement. Overprovisioning Pods and PriorityClass/preemption are advanced capacity techniques to study with Unit 7 and M15, not universal fixes.

### 2. Fairness across namespaces

An HPA with a high maximum can consume capacity needed by other workloads. Namespace quotas can limit that growth, but a quota rejection or Pending Pod does not necessarily tell the service owner which constraint is most important. Diagnose the admission event, HPA status, Pod events, and actual node allocatable.

Coordinate with application owners on:
- a justified `maxReplicas`;
- realistic requests and limits;
- quota and priority policy;
- expected traffic envelope;
- downstream concurrency;
- alerts for Pending duration, saturation, and SLO impact.

Do not use one universal replica count or CPU target for all services.

### 3. Scaling SLI/SLO and cost trade-offs

Useful measurements include:

- time from load increase to additional **Ready** capacity;
- request success/error rate and p95/p99 latency during scaling;
- queue lag, oldest-message age, and drain time;
- CPU/memory consumption and Pending Pod duration;
- cost or resource consumption per successful request / completed work unit;
- cold-start frequency and minimum-replica cost.

A service may choose a higher minimum replica count to reduce cold-start latency, accepting higher idle cost. A lower minimum may reduce cost but increase the time to restore capacity. Faster scale-up may protect latency but overload downstream dependencies. Define stop criteria from the service's own SLO and error budget; there is no universal threshold that applies to every workload.

### 4. Safe load-test methodology

1. Use a dedicated namespace and disposable kind cluster.
2. Capture a baseline before applying load.
3. Define a bounded ramp, steady phase, and ramp-down.
4. Set a maximum duration and a hard stop condition.
5. Capture request rate, latency, errors, resource metrics, desired/current/ready replicas, Pending time, and relevant events.
6. Stop if laptop resources, cluster stability, or error thresholds exceed the predeclared limit.
7. Compare one parameter change at a time.
8. Record limitations: synthetic traffic, small cluster, local image cache, WSL2/container-node overhead, and absence of real cloud nodes/load balancers.
9. Do not call the result a production capacity benchmark.

### 5. Failure scenarios and first response

- **Metrics API unavailable:** verify Metrics Server/API health and logs before changing HPA policy.
- **HPA `<unknown>`:** inspect metrics, requests, target references, and metric adapters.
- **HPA stuck at `maxReplicas`:** determine whether the metric remains above target, whether scale-up is bounded, and whether more replicas can be scheduled.
- **Scale-to-min latency spike:** examine cold starts, warm-up, readiness, and whether the minimum is appropriate.
- **Flapping:** correlate metric and replica timestamps; adjust one behavior parameter at a time.
- **Runaway scale:** verify metric quality, max replicas, quotas, downstream limits, and approval policy.
- **Replicas created but Pending:** inspect scheduler events, requests, quota, and placement; do not assume HPA creates nodes.
- **Queue lag grows despite more workers:** determine whether the downstream system is saturated, work cost varies, or workers are failing/retrying.

### 6. Incident walkthrough: HPA reached max and starved other namespaces

All output, names, timestamps, and numbers below are **illustrative**, not observed results.

**Symptom.** An API's HPA reaches `maxReplicas`; some new Pods are Pending. A different namespace begins reporting scheduling failures.

**Impact.** API latency remains above its SLO guardrail, and a batch worker in another namespace cannot schedule. The issue is now a shared-capacity fairness incident, not merely an HPA configuration problem.

**Hypotheses.**
- Incoming demand genuinely exceeds planned capacity.
- Requests are unrealistic and consume too much schedulable capacity.
- HPA target/max bounds are too aggressive for the cluster's capacity.
- Namespace quota or admission constraints are reached.
- Topology/affinity/taints prevent otherwise plausible placement.
- Downstream saturation means additional API replicas do not improve throughput.
- Metrics are stale or do not represent the actual bottleneck.

**Read-only diagnostics.**

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get hpa -A
kubectl get pods -A -o wide
kubectl get events -A --sort-by=.lastTimestamp
kubectl top nodes
kubectl top pods -A
kubectl describe hpa -n <api-namespace> <hpa-name>
kubectl describe pod -n <api-namespace> <pending-pod>
kubectl describe quota -n <api-namespace>
```

Use `kubectl describe quota` only when a quota object is present; list quotas first if needed. Inspect request values, node allocatable, system/DaemonSet overhead, Pending reasons, and SLI. Commands and event fields should be checked against the installed CLI. `[VERIFY]`

**Illustrative root cause.** The API's request rate is high, HPA is at its configured maximum, and several replicas remain Pending because the remaining nodes cannot satisfy their CPU/memory requests while respecting placement constraints. A noncritical batch workload is also requesting capacity. More API replicas do not arrive, and the database is near its concurrency limit.

**Safe mitigation.**
1. Declare an incident owner and pause nonessential scaling-policy changes.
2. Verify user impact and current service SLI.
3. Avoid blindly raising `maxReplicas`; that may increase contention.
4. Reduce or defer noncritical work only through its owner-approved control.
5. If the API is the priority, use the organization's approved capacity/priority procedure; do not arbitrarily kill unrelated Pods.
6. Evaluate whether requests are inaccurate, whether the bottleneck is downstream, and whether temporary capacity is available.
7. If the actual limit is node capacity, escalate to the platform/capacity owner; kind cannot validate real node provisioning.
8. Reassess the scaling target only after identifying the bottleneck.

**Recovery verification.** Confirm Pending Pods are resolved or have an approved disposition, the API SLI returns within its agreed guardrail, the starved namespace can schedule its critical workload, and downstream systems are healthy. Record the time to recovery and the residual risk.

**Prevention and owners.** Define service-specific `maxReplicas`, capacity headroom, quotas, priority policy, downstream concurrency limits, Pending Pod alerts, SLO guardrails, and an escalation route between service and platform owners.

### 7. Data-pipeline design review

**FastAPI scoring API**
- Candidate signals: CPU utilization for compute-heavy inference, request rate for demand, and latency/error rate as SLO indicators.
- Boundaries: explicit `minReplicas`/`maxReplicas`, realistic CPU/memory requests, startup/readiness behavior, downstream model-serving or database capacity.
- Evidence: load profile, HPA conditions, request latency/error rate, ready replica timeline, Pending time, and cold-start distribution.

**Queue worker**
- Candidate signal: oldest-message age or queue lag; CPU can be a secondary diagnostic signal.
- Boundaries: maximum worker concurrency, downstream database/API limits, idempotent work, checkpointing, poison-message handling, and queue visibility/lease semantics.
- Evidence: lag and completion latency, per-worker throughput, retry/duplicate rate, downstream saturation, and time to drain backlog.

**Stateful dependency**
- Do not assume horizontal scaling is the answer. Review database-specific replication, consistency, connection limits, and storage behavior with its owner.

**Capacity assumptions**
- Calculate the resource request footprint of the target replicas and required headroom.
- Include system/DaemonSet overhead and node allocatable.
- Check quotas and placement constraints.
- Estimate time to Ready capacity, not just time to create a Pod.
- State unknowns explicitly, especially anything that requires production metrics or managed-cloud testing.

## Production runbook: HPA not scaling as expected

This runbook is a template. Adapt it to the actual cluster, API version, metric source, and service SLO.

### 1. Confirm scope and impact

```bash
# Read-only
kubectl config current-context
kubectl get nodes -o wide
kubectl get hpa -A
kubectl get pods -A -o wide
```

Record the affected namespace, HPA, target workload, change revision, customer/workload impact, and SLI baseline.

### 2. Inspect the HPA and metric pipeline

```bash
# Read-only
kubectl get hpa -n <namespace>
kubectl describe hpa -n <namespace> <hpa-name>
kubectl top nodes
kubectl top pods -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
kubectl explain horizontalpodautoscaler.spec
kubectl explain horizontalpodautoscaler.spec.metrics
kubectl explain horizontalpodautoscaler.spec.behavior
```

If `top` fails, diagnose Metrics Server and the Metrics API before tuning targets. If `<unknown>` appears, inspect missing requests, metric freshness, selector/target configuration, and adapter health.

### 3. Inspect target and scheduling

```bash
# Read-only
kubectl get deployment -n <namespace> <deployment-name> -o yaml
kubectl get pods -n <namespace> -o wide
kubectl describe pod -n <namespace> <pending-pod>
kubectl get resourcequota -n <namespace>
kubectl describe resourcequota -n <namespace> <quota-name>
```

Check request/limit sizing, readiness/startup delays, desired/current/ready replicas, HPA bounds, rollout state, quota, Pending reasons, node allocatable, and placement constraints.

### 4. Decide: proceed, pause, mitigate, escalate

- **Proceed with a scaling change** only when the signal represents the bottleneck, the change is bounded, capacity and downstream effects are understood, and the test/rollout has an SLO guardrail.
- **Pause** when metrics are unknown, the root cause is unclear, the change would affect a shared cluster, or the workload is already outside its reliability guardrail.
- **Mitigate** by restoring the metrics pipeline, correcting an approved request/metric configuration, reducing noncritical load through an owner-approved control, or requesting capacity from the platform owner.
- **Escalate** when the service has reached its maximum, nodes/quota are exhausted, downstream saturation dominates, or an action could starve other namespaces.

Do not change multiple variables simultaneously unless the incident response requires an explicitly approved emergency action.

### 5. Validate and follow up

Verify actual replica count and readiness, request/latency/error outcomes, queue lag, Pending Pod state, downstream health, and resource use. Capture timestamps and the exact configuration revision. Add follow-up owners for metric quality, capacity, quota, scaling bounds, startup time, and runbook improvements.

## Hands-on labs

All labs below are **local simulations**. The author did not execute them. Use a dedicated disposable kind cluster; never use a production or shared context. Commands are labeled by intent where relevant. Replace all image placeholders with a verified image or a local image you have built and loaded. No public image tag is asserted to be current.

### Shared lab safety

Before mutation, verify:

```bash
kubectl config current-context
kubectl get nodes -o wide
kind get clusters
```

Use a dedicated cluster such as `autoscaling-lab` and namespace `autoscaling-lab`. If the cluster already exists, inspect it rather than recreating or deleting it. Use `<NODE_IMAGE_TAG>` after checking current kind support and Kubernetes version-skew guidance. WSL2/container-node resources are limited; do not run unbounded load or memory tests.

### Lab 1 — Metrics Server, HPA, and CPU-driven API scaling

**Goal:** Verify the resource metrics pipeline, apply a CPU HPA to a Deployment with requests, generate bounded local traffic, and record actual scale behavior.  
**Time:** 90–150 minutes.  
**Prerequisites:** kind, kubectl, compatible container runtime, Python 3, a verified HTTP image or local image.

#### Step A — Verify or create a disposable cluster

Read-only checks:

```bash
kind get clusters
kubectl config current-context
kubectl get nodes -o wide
```

If creating a new cluster, use a reviewed kind config with one control-plane and two workers. Use `<NODE_IMAGE_TAG>` only after checking current support. Do not recreate an existing cluster without confirming it contains no work to preserve.

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: autoscaling-lab
nodes:
  - role: control-plane
  - role: worker
  - role: worker
    # image: kindest/node:<NODE_IMAGE_TAG>
```

The exact config schema and image compatibility are `[VERIFY]`. Create only after confirming the target:

```bash
# MUTATING — creates local cluster resources.
kind create cluster --name autoscaling-lab --config <path-to-reviewed-kind-config>
kubectl config current-context
kubectl get nodes -o wide
```

#### Step B — Install Metrics Server

Follow the current official Metrics Server installation instructions. Do not paste an unverified manifest from an old tutorial. In some kind configurations, kubelet certificate/address behavior may require a local-only workaround; the exact flag and need are `[VERIFY]`. If a TLS-verification bypass is necessary for the disposable lab, understand that it weakens endpoint identity verification and **must not be used in production**. Prefer a secure supported configuration whenever possible.

Verify before continuing:

```bash
# Read-only
kubectl get deployment -n kube-system metrics-server
kubectl get pods -n kube-system
kubectl top nodes
kubectl top pods -n kube-system
kubectl get apiservices
```

If `kubectl top` does not work, stop and diagnose Metrics Server and the Metrics API. Do not proceed as though the HPA test were valid.

#### Step C — Apply workload and HPA

Replace `<REPLACE_WITH_VERIFIED_HTTP_IMAGE>` with an image that listens on 8080 and returns a response. Ensure it is available to kind; do not assume a registry exists.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: autoscaling-lab
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  namespace: autoscaling-lab
spec:
  replicas: 2
  selector:
    matchLabels:
      app: scoring-api
  template:
    metadata:
      labels:
        app: scoring-api
    spec:
      containers:
        - name: api
          image: <REPLACE_WITH_VERIFIED_HTTP_IMAGE>
          ports:
            - name: http
              containerPort: 8080
          resources:
            requests:
              cpu: 200m
              memory: 128Mi
            limits:
              cpu: "1"
              memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
  namespace: autoscaling-lab
spec:
  selector:
    app: scoring-api
  ports:
    - name: http
      port: 80
      targetPort: http
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: scoring-api-hpa
  namespace: autoscaling-lab
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scoring-api
  minReplicas: 2
  maxReplicas: 6
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
  behavior:
    scaleUp:
      policies:
        - type: Pods
          value: 2
          periodSeconds: 60
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 25
          periodSeconds: 60
      selectPolicy: Max
```

Apply only after verifying context and topology:

```bash
# MUTATING — apply only the reviewed manifest to this disposable cluster.
kubectl config current-context
kubectl get nodes -o wide
kubectl apply -f <reviewed-autoscaling-lab-manifest>
kubectl rollout status deployment/scoring-api -n autoscaling-lab --timeout=120s
```

#### Step D — Bounded traffic and observation

Port-forward in one terminal:

```bash
# Local port-forward process; stop with Ctrl-C.
kubectl port-forward -n autoscaling-lab svc/scoring-api 18080:80
```

Run the 30-second Python request sampler from the L2 section in a second terminal. Do not increase duration or concurrency without checking laptop resource use and setting an explicit stop condition. A sequential sampler may not create enough CPU load to trigger scaling; that is a valid observed result, not a reason to fabricate scale-up.

Watch in separate terminals:

```bash
kubectl get hpa -n autoscaling-lab -w
kubectl get pods -n autoscaling-lab -w
kubectl top pods -n autoscaling-lab
kubectl describe hpa -n autoscaling-lab scoring-api-hpa
```

Record actual observations with timestamps:

| Evidence | Learner records |
|---|---|
| Versions and context | kind, Kubernetes server, kubectl, Metrics Server, current context |
| Baseline | desired/current/ready replicas, CPU usage, request successes/errors/latency |
| Load phase | start/end time, total requests, observed CPU and HPA status |
| Scaling | desired/current/ready replicas, Pending duration, startup/readiness time |
| Scale-down | observed time and replica trajectory after load stops |
| Limitations | whether load was sufficient, local resource constraints, metric sampling lag |

**Interpretation:** If HPA does not scale, first verify that the test creates meaningful CPU pressure, that metrics are available, and that requests and target are coherent. Do not assume a sequential client will saturate a service.

**Cleanup:** Delete only the dedicated namespace after verifying context and contents. If Metrics Server was installed specifically for this lab into an otherwise shared local cluster, remove only the exact resources installed according to its official installation instructions. Do not delete an installation that predates the lab.

```bash
kubectl config current-context
kubectl get pods -n autoscaling-lab -o wide
# CLEANUP — only if the namespace belongs exclusively to this lab:
kubectl delete namespace autoscaling-lab --wait=true
kubectl get namespace autoscaling-lab
```

**Cleanup verification:** Namespace is absent if deleted; Metrics Server is left in the intended state; no other namespace or cluster was deleted.  
**Troubleshooting:** Check image availability, Service selector/port, Metrics API, CPU requests, HPA conditions, and actual load.  
**Stretch:** Repeat with a more representative but still bounded request pattern, recording latency and error rate as well as replica count.

### Lab 2 — Diagnose `<unknown>` metrics

**Goal:** Learn to distinguish a broken metric pipeline from an invalid HPA target or missing resource requests.  
**Time:** 45–75 minutes.  
**Prerequisites:** Lab 1 environment or another disposable cluster where you have permission to inspect metrics.

#### Step A — Read-only diagnosis

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get hpa -n autoscaling-lab
kubectl describe hpa -n autoscaling-lab scoring-api-hpa
kubectl get pods -n kube-system
kubectl top nodes
kubectl top pods -n autoscaling-lab
kubectl get apiservices
kubectl get events -n autoscaling-lab --sort-by=.lastTimestamp
kubectl get deployment scoring-api -n autoscaling-lab -o yaml
```

Check whether Metrics Server is Ready, whether the resource metrics API responds, whether Pods have requests, and whether the HPA target name/kind/API version match the Deployment.

#### Step B — Safe missing-request reasoning

Do not mutate the live Lab 1 HPA workload blindly. In a dedicated copy or reviewed manifest, remove a required resource request from one container only if you are prepared to restore it immediately. Observe whether the HPA calculation becomes incomplete or reports an error; exact behavior varies with metrics and Pods. `[VERIFY]` The lab may be completed as a read-only tabletop by inspecting a manifest with missing requests if you do not want to mutate the cluster.

#### Step C — Optional Metrics Server fault simulation

Prefer a read-only diagnosis unless you are comfortable restoring the exact Metrics Server deployment. If temporarily scaling down or changing a lab-only component, first verify it was installed for this lab, capture its original configuration, and record the restoration command. Do not disable a shared metrics service. The safest default is to analyze the expected symptom without intentionally breaking the component.

**Evidence:** HPA conditions/messages, Metrics API response, Metrics Server Pod/log status, request configuration, and recovery observation. Exact output is not guaranteed.

**Recovery:** Restore any changed request and verify the HPA returns to a valid state. If a component was changed, restore it using the exact saved/reviewed configuration and verify `kubectl top` and HPA conditions.

**Cleanup and verification:** Remove only lab-owned resources; verify HPA, Deployment, and metrics component are in the intended state.  
**Troubleshooting:** If the cluster has no Metrics Server, install only by following current official instructions; do not assume a resource-metrics API exists by default.  
**Stretch:** Create a diagnostic decision tree that maps each observed symptom to a next read-only check before any mutation.

### Lab 3 — Deliberately thrashing HPA and stabilize it

**Goal:** Observe a bounded oscillation or aggressive scaling policy, then change one behavior parameter and compare the actual result.  
**Time:** 60–90 minutes.  
**Prerequisites:** Working Lab 1 HPA and metrics, bounded request generator, disposable cluster.

Do not create unbounded CPU loops or exhaust the host. Use a safe HTTP workload and a bounded request profile. If the load generator does not create sufficient variability, simulate the analysis with recorded metrics rather than forcing resource exhaustion.

#### Step A — Capture baseline

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get hpa -n autoscaling-lab
kubectl describe hpa -n autoscaling-lab scoring-api-hpa
kubectl get pods -n autoscaling-lab -w
kubectl top pods -n autoscaling-lab
```

Record the HPA behavior configuration and timestamped load/metric/replica observations.

#### Step B — Change one variable

Use a reviewed manifest in the disposable namespace. For example, compare a short or omitted scale-down stabilization setting with an explicitly longer window, after checking current field semantics and defaults. Do not claim that every workload will thrash on demand. If the current setup does not show oscillation, document that and use a controlled tabletop timeline.

#### Step C — Repeat the same bounded load

Run the same duration/rate profile, record the same signals, and compare:
- number of replica changes;
- time to ready capacity;
- request errors and latency;
- peak and idle replica counts;
- Pending time and resource consumption.

**Expected evidence:** A before/after table filled with actual results. No particular curve or time is promised.

**Interpretation:** A smoother replica curve can reduce churn but may delay cost savings or response to a real demand drop. Judge by SLO outcomes and cost together.

**Cleanup:** Restore the reviewed original HPA manifest or delete only the dedicated namespace after checking scope. Verify the intended replica count, HPA behavior and namespace state.  
**Troubleshooting:** If metrics are unknown, stop and use Lab 2 diagnostics. If Pods are Pending, inspect capacity before changing scaling behavior.  
**Stretch:** Compare a second behavior parameter, changing only one parameter per run.

### Lab 4 — Capacity starvation and Pending Pods tabletop

**Goal:** Demonstrate that desired replicas do not guarantee schedulable replicas, and simulate the node-autoscaler decision logic without claiming kind provisions nodes.  
**Time:** 60–90 minutes.  
**Prerequisites:** Disposable kind cluster, namespace quota awareness, basic scheduler events.

#### Step A — Inspect current capacity

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl describe nodes
kubectl get pods -A -o wide
kubectl top nodes
```

Record node allocatable, requests, system/DaemonSet overhead where visible, and current workload placement. `kubectl top` is usage evidence, not a complete scheduling-capacity calculation.

#### Step B — Bounded manifest example

The following illustrates how a high replica target and requests can exceed local schedulable capacity. Do **not** apply an unbounded or intentionally huge resource request. Choose a small request that is known to be above remaining capacity only after inspecting the disposable cluster, or complete this as a tabletop using the manifest as an example.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: capacity-demo
  namespace: capacity-lab
spec:
  replicas: 3
  selector:
    matchLabels:
      app: capacity-demo
  template:
    metadata:
      labels:
        app: capacity-demo
    spec:
      containers:
        - name: demo
          image: <REPLACE_WITH_VERIFIED_SMALL_HTTP_IMAGE>
          resources:
            requests:
              cpu: <SMALL_BUT_REVIEWED_CPU_REQUEST>
              memory: <SMALL_BUT_REVIEWED_MEMORY_REQUEST>
```

The placeholders intentionally make this manifest non-applicable until reviewed. Do not create host exhaustion. If using a resource quota, set a bounded quota in the dedicated namespace and retain the exact original configuration for cleanup.

#### Step C — Diagnose Pending

```bash
kubectl get pods -n capacity-lab -o wide
kubectl describe pod -n capacity-lab <pending-pod>
kubectl get events -n capacity-lab --sort-by=.lastTimestamp
kubectl get resourcequota -n capacity-lab
kubectl describe nodes
```

Explain the scheduler evidence: insufficient resources, affinity/taints/topology, quota/admission, or other constraints. HPA can ask for replicas while the scheduler cannot place them.

#### Step D — Tabletop node-autoscaler loop

| Step | Evidence | Decision |
|---|---|---|
| HPA raises desired replicas | HPA desired/current count | Is the metric legitimate and within policy? |
| Pods become Pending | Pod events and scheduling reason | Is the issue capacity or a placement/configuration constraint? |
| Node autoscaler evaluates | Provider/controller-specific logs/configuration (not present in kind by default) | Would a supported node shape satisfy the constraints? |
| Capacity appears | New node registers Ready in a real integrated environment | Not simulated by kind |
| Pods schedule/start | Pod events, readiness, application SLI | Did the new capacity arrive before the SLO was breached? |

**Safe mitigation options:** reduce noncritical demand through an approved control, correct unrealistic requests after measurement, revise an inappropriate placement constraint, adjust bounded replica/quota limits with owner approval, or escalate for capacity. Do not kill unrelated workloads arbitrarily.

**Cleanup:** Delete only `capacity-demo` and the dedicated namespace after verifying scope; remove only quota objects created for this lab. Confirm no lab Pending Pods remain and no shared quota was changed.  
**Troubleshooting:** If no Pending Pod appears, the chosen constraints may not exceed capacity; record that result rather than increasing resource requests blindly.  
**Stretch:** Estimate how many replicas fit on the remaining allocatable capacity using requests and overhead, and list assumptions.

### Optional Lab 5 — VPA recommendation-only mode

**Goal:** Compare VPA recommendations with actual resource requests and workload behavior without automatically applying disruptive updates.  
**Time:** 60–120 minutes.  
**Prerequisites:** Disposable cluster with enough headroom; current VPA installation instructions and supported version.

VPA installation and mode semantics are version-specific. `[VERIFY]` Do not install it if the cluster is already resource-constrained or the current installation path is unclear. Follow the official VPA project instructions; use a recommendation-only/off mode only if the installed version documents that mode and its behavior.

Record:
- workload resource requests and limits;
- observed usage across representative load phases;
- VPA recommendation fields exposed by the installed version;
- whether recommendations are stable or sensitive to the sample window;
- reasons to accept, reject, or investigate the recommendation.

Do not enable `Initial`, `Recreate`, or any mode that updates resources without a separate change review and disruption plan. A recommendation is not a command: include latency, startup, node capacity, quota, and application memory behavior in the decision.

**Cleanup:** Remove only the lab VPA object and components installed specifically for this exercise, following the current project's instructions. Verify the original workload and cluster components remain in the intended state.  
**Troubleshooting:** If recommendations are absent, verify the recommender/controller health, object selectors, and supported version.  
**Stretch:** Compare VPA recommendations before and after a bounded load phase and explain why a short local sample may be misleading.

## Troubleshooting decision table

| Symptom | Likely cause | Evidence / command | Safe action | Stop / escalation condition |
|---|---|---|---|---|
| HPA target shows `<unknown>` | Metrics API unavailable, missing request, stale/missing sample, wrong target/selector | `describe hpa`, `top pods`, Metrics API/APIService, Pod YAML/events | Diagnose metric path before tuning policy | Stop scaling changes while metric validity is unknown |
| HPA does not scale up | Metric below target, insufficient load, metric failure, max reached, target mismatch | HPA conditions, metrics, request profile, desired/current replicas | Verify signal and workload bottleneck | Escalate if SLO breaches and cause remains unknown |
| HPA at `maxReplicas` | Demand exceeds configured bound, bad target, downstream saturation | HPA, latency/errors, CPU, queue lag, downstream health | Confirm bottleneck; adjust bounds only with capacity/owner review | Stop if increasing replicas would starve shared workloads |
| New Pods Pending | Node capacity, requests, quota, taints/affinity/topology | `describe pod`, events, quota, node allocatable | Fix constraints or request capacity through approved path | Stop if SLO or other namespaces are affected |
| HPA flaps | Noisy metric, aggressive policy, startup lag, poor requests | Timestamped metric/replica/latency timeline | Change one behavior parameter and repeat bounded test | Stop if changes worsen SLO or cause churn |
| Scale-down increases latency | Minimum too low, cold starts, cache/model warm-up | Latency, ready replicas, startup logs, load timeline | Reassess minimum and stabilization from evidence | Escalate on SLO breach |
| CPU utilization looks unexpectedly low | Requests too high, metric lag, CPU not the bottleneck | Request values, `top`, latency, throttling evidence if available | Validate request sizing and signal relevance | Do not lower requests blindly |
| CPU utilization looks high but replicas do not help | Downstream bottleneck, limits/throttling, max bound, scheduling failure | HPA, Pod events, downstream metrics, request outcomes | Identify limiting dependency and capacity | Stop if more replicas increase dependency failure |
| Memory-based HPA keeps replicas high | Retained heap/cache/model memory | Memory time series and application behavior | Consider a better demand metric or measured policy | Escalate if memory pressure threatens cluster |
| Queue lag grows despite more workers | Downstream saturation, poison messages, retries, metric semantics | Lag age, throughput, retries, dependency health | Bound concurrency and fix downstream bottleneck | Stop if retries/duplicates threaten data integrity |
| Metrics Server unavailable | Deployment/APIService/TLS/reachability issue | Pod status/logs, APIService, official docs | Restore supported metrics path | Do not apply insecure workaround in production |
| VPA changes destabilize Pods | Update/recreation mode or resource conflict | VPA mode/status, Pod events, HPA metrics | Pause changes; return to approved configuration | Escalate if availability or resource safety is affected |
| Another namespace is starved | Scaling bound/request footprint/quota/priority imbalance | `get pods -A`, quota, node allocatable, HPA | Coordinate fair capacity mitigation with owners | Treat as shared-cluster incident |
| kind results differ from expected | Resource limits, WSL2 overhead, cached image, no real nodes | Node/runtime versions, events, host usage | Document limitations and repeat safely | Stop if host becomes unstable |

## Production readiness checklist

- [ ] Kubernetes/kubectl/kind versions and current context recorded.
- [ ] Current Metrics API and Metrics Server status verified before HPA testing.
- [ ] HPA target reference points to the intended scalable resource.
- [ ] CPU utilization-based HPA has meaningful CPU requests on the relevant containers.
- [ ] Memory metric semantics and application memory behavior are understood before using memory as a scale signal.
- [ ] `minReplicas`, `maxReplicas`, and behavior policies are justified by measured load and capacity, not copied defaults.
- [ ] Metric source, freshness, selector, and adapter behavior are documented.
- [ ] Startup/readiness delay and image/model initialization are measured.
- [ ] Load tests are bounded, isolated, and have predeclared stop criteria.
- [ ] HPA conditions and actual desired/current/ready replica counts are captured.
- [ ] Pending Pod events and node allocatable/capacity are understood.
- [ ] Quotas and cross-namespace fairness are reviewed.
- [ ] Downstream database/API concurrency and rate limits are considered.
- [ ] Queue consumers have idempotency, retry, poison-message, and checkpoint handling.
- [ ] HPA/VPA ownership of resource dimensions is explicit.
- [ ] VPA mode/version support is verified before installation or mutation.
- [ ] Node-autoscaler assumptions are validated in a suitable environment; kind is not treated as real node provisioning.
- [ ] SLI/SLO baseline and scale-test abort thresholds are recorded.
- [ ] Change owner, service owner, manifest revision, and rollback/restore plan are documented.
- [ ] Cleanup commands are scoped to lab-owned resources and cleanup verification is recorded.

## SRE, security, and capacity lens

### SLI/SLO guardrails

For an API, use successful valid requests divided by total valid requests, error rate, and latency percentiles. For a worker, use oldest-message age, queue lag, completion latency, retry rate, and durable completion. Define “successful” and the observation window in the service's own SLI specification.

A load test should stop when the service's agreed SLO guardrail is breached, the laptop/cluster approaches unsafe resource use, or the test exceeds its bounded duration. Do not invent a universal error rate, p95 target, CPU target, or replica count.

### Capacity and fairness

Use node allocatable, requests, system/DaemonSet overhead, quota, topology constraints, and startup lag to estimate whether new replicas can become Ready. Apparent free CPU from `kubectl top` does not prove that a Pod can schedule. A high HPA maximum can harm other namespaces if there is no capacity/fairness policy.

### Security and least privilege

Metrics access and scale changes should use the least privilege appropriate to the environment. Do not grant broad cluster-admin by default. Separate read-only diagnosis from mutating actions, review manifests before applying them, and record the operator/change identity. If a local Metrics Server TLS workaround is necessary for kind, isolate it to the disposable cluster and do not carry it into production.

### Trade-off table

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Higher `minReplicas` | More warm capacity; lower cold-start exposure | Higher idle resource cost | Can consume shared capacity | Latency sensitivity and load variability justify the cost |
| Higher `maxReplicas` | Allows more horizontal growth | Potentially more resource use | Can starve other namespaces or overload dependencies | Capacity and downstream limits have been validated |
| Conservative scale-down | Less churn and fewer cold starts | Slower cost reduction | Idle replicas remain longer | Startup/warm-up is expensive or metrics are noisy |
| Faster scale-up | Can respond to sharp demand | More burst capacity and downstream concurrency | May overshoot or overload dependencies | The signal is trustworthy and downstream is protected |
| CPU metric | Native resource metric and straightforward model | Requires good requests; may miss non-CPU bottlenecks | Wrong request sizing distorts utilization | CPU tracks useful work |
| Queue-lag metric | Directly reflects backlog | Requires metric pipeline and correct semantics | Can trigger runaway consumers if downstream is saturated | Worker throughput and queue delay are the SLO concern |
| VPA recommendations | Helps identify request-sizing issues | Additional components and interpretation effort | Recommendation can be misleading if workload sample is unrepresentative | Resource sizing is uncertain and recommendations can be reviewed safely |
| Additional node capacity | Makes Pending replicas schedulable when capacity is the issue | Cost and provisioning delay | Does not fix invalid placement or downstream bottlenecks | Evidence shows node capacity is the limiting factor |

### Incident response fragment

**Alert/symptom:** HPA not scaling, at max, or creating Pending Pods.  
**Triage:** verify context; inspect HPA conditions, metric source, requests, Pod events, quota, node allocatable, and service SLI.  
**Mitigation:** fix metric pipeline, correct a proven configuration issue, reduce noncritical work through an approved control, or escalate for capacity.  
**Validation:** check Ready replicas, latency/error rate, queue lag, Pending duration, and downstream health.  
**Follow-up:** assign owners for metric quality, request sizing, scaling bounds, capacity, fairness, and startup improvements.

## Self-check questions

### 1. Does HPA add worker nodes when it increases replicas?

**Answer:** No. HPA changes the desired replica count. A separate node-autoscaling system may provision capacity if configured and supported.  
**Tempting wrong answer:** “HPA owns the entire scaling stack.” It does not own the scheduler or cloud infrastructure.

### 2. Why does CPU utilization depend on resource requests?

**Answer:** Utilization-based CPU targets express usage relative to CPU requests. Missing or poorly chosen requests can make the metric unavailable or misleading.  
**Tempting wrong answer:** “The target is always a percentage of the CPU limit.”

### 3. What does `kubectl top pods` prove?

**Answer:** It provides recent resource-usage metrics from the configured resource metrics pipeline. It does not prove the application meets its latency SLO or show a complete historical peak profile.  
**Tempting wrong answer:** “Low CPU means the service has enough capacity.” The bottleneck may be elsewhere.

### 4. Why might HPA display `<unknown>`?

**Answer:** The metrics pipeline may be unavailable, data may be missing/stale, requests may be missing, or the target/metric configuration may be wrong.  
**Tempting wrong answer:** “The HPA controller is always broken.” Diagnose the metric path and workload first.

### 5. Why can memory be a poor scale-out signal?

**Answer:** Heap/cache/model memory may remain high after demand falls, and new replicas can multiply memory use. It is useful when memory pressure genuinely tracks demand, but needs workload-specific evidence.  
**Tempting wrong answer:** “Memory is never useful.” That overgeneralizes.

### 6. Why can more replicas fail to improve latency?

**Answer:** The bottleneck may be a database, rate-limited external API, CPU throttling, bad requests, or scheduling capacity. Additional replicas can increase contention.  
**Tempting wrong answer:** “More replicas always mean more throughput.”

### 7. How do stabilization windows help with flapping?

**Answer:** They dampen rapid changes based on recent recommendations, reducing churn. They can also delay a needed scale change and should be tuned from measured behavior.  
**Tempting wrong answer:** “The longest window is always safest.” It may preserve too little capacity or waste resources.

### 8. Why is HPA plus VPA potentially tricky?

**Answer:** If HPA scales on utilization relative to requests while VPA changes those requests, the utilization denominator changes and the control loops can interact. Compatibility depends on metric, mode, and version.  
**Tempting wrong answer:** “They are always incompatible.” The actual configuration must be reviewed.

### 9. What does a Pending Pod mean when HPA has already increased desired replicas?

**Answer:** The desired state changed, but the scheduler could not place the Pod or admission was constrained. Inspect events, requests, quota, node allocatable, and placement rules.  
**Tempting wrong answer:** “The autoscaler has failed to add a replica.” The Pod may exist but be unschedulable.

### 10. What should happen when queue lag rises but downstream database saturation is already high?

**Answer:** Do not blindly add workers. Bound concurrency, inspect downstream throughput and retries, and resolve the limiting dependency or use an approved load-shedding policy.  
**Tempting wrong answer:** “Scale until queue depth drops.” That can worsen the bottleneck.

## Senior interview and design-review questions

### 1. Design HPA for a CPU-bound scoring API that has expensive model startup.

**Expected answer points:** choose a signal that tracks inference work; set measured requests and bounded replica limits; account for model load/readiness delay; decide minimum warm replicas based on SLO/cost; use conservative scale-down where evidence supports it; test bounded traffic; measure latency/errors and time to Ready capacity.

### 2. HPA is at `maxReplicas`, several Pods are Pending, and another namespace is starved. What do you do?

**Expected answer points:** establish incident owner and SLI; inspect HPA conditions, Pending events, requests, quota, node allocatable and placement; determine whether demand, bad sizing, or downstream saturation is the root cause; protect critical workloads through approved fairness policy; avoid blindly increasing maximum; request capacity if node capacity is the limit; verify recovery and document follow-up.

### 3. Explain why a CPU utilization target is misleading when requests are poorly chosen.

**Expected answer points:** utilization is relative to requests; too-low requests can make a service appear highly utilized and cause scheduling contention; too-high requests can suppress utilization percentage and reduce schedulable capacity; requests affect both scheduling and scaling; validate against workload performance and resource behavior.

### 4. How would you scale queue consumers without overwhelming the downstream database?

**Expected answer points:** choose lag/age and throughput signals; cap replicas and per-worker concurrency; understand queue leases, retry and idempotency; measure database saturation and rate limits; use bounded scale-up/down behavior; protect against poison messages and duplicate work; define queue-lag SLO and stop conditions.

### 5. What evidence would prove an autoscaling change improved reliability rather than merely increasing replicas?

**Expected answer points:** compare baseline and post-change load profiles; request success/error rate and latency; time to Ready capacity; Pending duration; queue lag/completion latency; downstream saturation; replica/resource timeline; cost per successful request/work unit; limitations of the test; explicit SLO guardrails and rollback criteria.

## Evidence artifacts and exit criteria

Retain the following as learning evidence in your own repository; this lesson does not create separate files automatically.

- Kubernetes/kubectl/kind/Metrics Server versions and current context.
- HPA and Deployment manifests, including resource requests, target, min/max, and behavior.
- Metrics API availability and `kubectl top` observations.
- Baseline and bounded load profile, including duration and stop criteria.
- Timestamped HPA desired/current/ready replica timeline.
- Request totals, successes/errors, latency observations, and queue lag where relevant.
- Pending Pod events, quota state, node allocatable/capacity assumptions.
- Before/after comparison for a behavior tuning experiment.
- Diagnostic decision tree for `<unknown>` metrics.
- Capacity-starvation incident tabletop and decision record.
- Any VPA recommendation snapshot and explicit review decision, if Lab 5 was performed.
- Cleanup verification and documented limitations of kind/WSL2.

**Exit criteria:** The learner can configure and diagnose a resource-metric HPA; explain how requests and bounds affect behavior; select metrics based on workload bottlenecks; explain VPA/node-autoscaler boundaries; conduct bounded local experiments with actual evidence; and justify an autoscaling policy using SLI/SLO, capacity, fairness, and downstream constraints.

## Sources and claim register

### Authoritative source list

No live documentation lookup was performed during authoring. The URLs below are official documentation entry points to consult before applying version-sensitive behavior. They are verification targets, not a claim that the pages were checked on the review date. Marked details remain `[VERIFY]` until checked against the installed cluster and component versions.

| Source title | Organization / project | URL | Claims/topics supported |
|---|---|---|---|
| Horizontal Pod Autoscaling | Kubernetes | https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ | HPA purpose, metrics, formula and behavior |
| HPA algorithm details | Kubernetes | https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ | Algorithm nuances and examples |
| HorizontalPodAutoscaler API reference | Kubernetes | https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/horizontal-pod-autoscaler-v2/ | `autoscaling/v2` fields |
| Resource Management for Pods and Containers | Kubernetes | https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ | Requests, limits, resource semantics |
| Resource metrics pipeline | Kubernetes | https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/ | Metrics Server and resource metrics architecture |
| Metrics Server repository and documentation | Kubernetes SIG Instrumentation / Metrics Server project | https://github.com/kubernetes-sigs/metrics-server | Supported versions, install instructions and limitations |
| Scheduling, Preemption and Eviction | Kubernetes | https://kubernetes.io/docs/concepts/scheduling-eviction/ | Scheduling and Pending Pod concepts |
| Node status / node allocatable concepts | Kubernetes | https://kubernetes.io/docs/concepts/architecture/nodes/ | Node capacity and allocatable resources |
| Kubernetes version-skew policy | Kubernetes | https://kubernetes.io/releases/version-skew-policy/ | Client/server compatibility |
| Vertical Pod Autoscaler | Kubernetes autoscaler project | https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler | VPA installation, modes, recommendations and limitations |
| KEDA documentation | KEDA project | https://keda.sh/docs/ | Event-driven/custom metric scaling awareness |
| Prometheus Adapter | Kubernetes SIG Instrumentation / Prometheus Adapter project | https://github.com/kubernetes-sigs/prometheus-adapter | Custom/external metric adapter awareness |
| kind quick start | kind project | https://kind.sigs.k8s.io/docs/user/quick-start/ | Local cluster creation and node image selection |
| Kubernetes release notes | Kubernetes | https://kubernetes.io/releases/ | Version-sensitive features such as in-place resize |
| Prometheus metric types | Prometheus project | https://prometheus.io/docs/concepts/metric_types/ | Metric semantics when Prometheus is used |

### Claim register

**Verification status:** No live sources or cluster behavior were checked during authoring. The following material claims are marked `[VERIFY]` as a record of required verification, not as a statement that the official source has been validated in this run.

| Claim ID | Claim | Source and URL | Version-sensitive? | Verification status | Notes / limitations |
|---|---|---|---|---|---|
| C01 | HPA changes desired replica count based on configured metrics | Kubernetes HPA: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ | Algorithm details yes | [VERIFY] | Does not provision nodes |
| C02 | The single-metric replica formula is a simplified mental model | HPA algorithm: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ | Yes | [VERIFY] | Real behavior includes multiple conditions |
| C03 | CPU utilization targets are relative to CPU requests | Kubernetes HPA: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ | API behavior yes | [VERIFY] | Verify current resource metric calculation |
| C04 | Missing resource requests can prevent or distort utilization scaling | Kubernetes HPA: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ | Yes | [VERIFY] | Exact behavior depends on Pod/metric state |
| C05 | Metrics Server supplies resource metrics but is not a general historical monitoring system | Metrics Server: https://github.com/kubernetes-sigs/metrics-server | Version/tool-dependent | [VERIFY] | Check project support and limitations |
| C06 | `kubectl top` relies on the resource metrics pipeline | Kubernetes resource metrics: https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/ | Yes | [VERIFY] | Recent resource observations, not SLO proof |
| C07 | `autoscaling/v2` exposes HPA metrics and behavior configuration | HPA API: https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/horizontal-pod-autoscaler-v2/ | Yes | [VERIFY] | Check served API and fields |
| C08 | HPA can use multiple metrics and implementation selects a desired scale according to documented behavior | HPA algorithm: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ | Yes | [VERIFY] | Do not assume metrics are averaged |
| C09 | `minReplicas` and `maxReplicas` bound HPA replica count | HPA API: https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/horizontal-pod-autoscaler-v2/ | API details yes | [VERIFY] | Bounds do not guarantee capacity |
| C10 | HPA `behavior` can configure scale-up/down policies and stabilization | HPA API: https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/horizontal-pod-autoscaler-v2/ | Yes | [VERIFY] | Defaults are not asserted |
| C11 | `AbleToScale` is an HPA condition used for scaling-target/control status | HPA algorithm: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ | Yes | [VERIFY] | Inspect current condition reasons/messages |
| C12 | `ScalingActive` is an HPA condition related to active metric-based scaling | HPA algorithm: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ | Yes | [VERIFY] | A condition alone does not prove root cause |
| C13 | `ScalingLimited` can indicate configured scaling bounds or policies constrain desired scale | HPA algorithm: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/ | Yes | [VERIFY] | Verify current condition semantics |
| C14 | `<unknown>` can result from metrics/API/request/target issues | HPA docs: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ | Yes | [VERIFY] | Diagnostic possibilities, not exhaustive |
| C15 | Memory may remain high after demand drops because of application/runtime retention | Resource management: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ | Workload-dependent | [VERIFY] | Must measure actual application behavior |
| C16 | Custom/external metric scaling requires an appropriate metric API integration | HPA docs: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ | Yes | [VERIFY] | Adapter implementation varies |
| C17 | Prometheus Adapter exposes custom metrics integration for HPA use | Prometheus Adapter: https://github.com/kubernetes-sigs/prometheus-adapter | Yes | [VERIFY] | Awareness only; no configuration asserted |
| C18 | KEDA supports event-driven autoscaling integrations | KEDA docs: https://keda.sh/docs/ | Yes | [VERIFY] | Supported scalers/versions change |
| C19 | VPA modes and update behavior depend on the installed VPA project version | VPA project: https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler | Yes | [VERIFY] | Verify exact semantics for `Off`, `Initial`, `Recreate`, `Auto` |
| C20 | HPA and VPA can interact when both influence resource utilization/request sizing | HPA docs: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ ; VPA project: https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler | Yes | [VERIFY] | Not a claim that every combination is impossible |
| C21 | In-place Pod resize support is version-sensitive | Kubernetes releases: https://kubernetes.io/releases/ | Yes | [VERIFY] | Check release notes and API support |
| C22 | Pending Pods can reflect scheduling/capacity/constraint issues | Scheduling concepts: https://kubernetes.io/docs/concepts/scheduling-eviction/ | Cluster-dependent | [VERIFY] | Inspect actual events |
| C23 | Cluster Autoscaler/Karpenter can add capacity under their configured conditions | Kubernetes autoscaling project: https://github.com/kubernetes/autoscaler ; Karpenter docs: https://karpenter.sh/docs/ | Provider/version-dependent | [VERIFY] | Do not generalize across implementations |
| C24 | kind does not provision real cloud nodes | kind docs: https://kind.sigs.k8s.io/docs/user/quick-start/ | Tool-dependent | [VERIFY] | Local containers simulate nodes |
| C25 | PDB status and readiness interact with disruption safety but do not govern all scaling behavior | Kubernetes disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | Yes | [VERIFY] | Cross-link to Unit 5 |
| C26 | Deployment rollouts can interact with HPA replica changes | Deployment docs: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ ; HPA docs: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ | Controller-dependent | [VERIFY] | Inspect live rollout and HPA state |
| C27 | Startup/readiness delay can delay useful capacity after scale-up | Readiness probes: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ | Workload-dependent | [VERIFY] | Measure actual startup profile |
| C28 | Quotas and requests can constrain admission/scheduling as replica count rises | Resource management: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ | Cluster policy-dependent | [VERIFY] | Inspect quota and events |
| C29 | Standard HPA should not be assumed to scale every Job/CronJob automatically | HPA docs: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ ; Jobs: https://kubernetes.io/docs/concepts/workloads/controllers/job/ | Controller-specific | [VERIFY] | Use a suitable workload/controller design |
| C30 | Queue-lag scaling requires correct metric semantics and downstream guardrails | HPA docs: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ ; chosen queue docs must be added | Queue-specific | [VERIFY] | No broker-specific behavior asserted |
| C31 | HPA maximums can be reached while Pods remain Pending | HPA and scheduling docs: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/ ; https://kubernetes.io/docs/concepts/scheduling-eviction/ | Cluster-dependent | [VERIFY] | Replica desired state is not schedulable capacity |
| C32 | Node allocatable is more useful for Pod capacity planning than raw machine capacity alone | Nodes: https://kubernetes.io/docs/concepts/architecture/nodes/ | Version/platform nuances | [VERIFY] | Include system reservations and overhead |
| C33 | `kubectl get events --sort-by=.lastTimestamp` output/field behavior can vary | kubectl reference: https://kubernetes.io/docs/reference/kubectl/ | Yes | [VERIFY] | Verify installed CLI |
| C34 | A kind Metrics Server TLS workaround, if needed, is environment-specific and weakens verification if TLS checking is disabled | Metrics Server: https://github.com/kubernetes-sigs/metrics-server ; kind: https://kind.sigs.k8s.io/docs/user/quick-start/ | Yes | [VERIFY] | Do not use insecure settings in production |
| C35 | WSL2/container-node resources can limit the representativeness of local experiments | WSL documentation: https://learn.microsoft.com/windows/wsl/ ; kind: https://kind.sigs.k8s.io/docs/user/quick-start/ | Environment-dependent | [VERIFY] | Compare installed versions and host limits |
| C36 | A sequential local HTTP sampler is not a production capacity benchmark | No universal Kubernetes source; test methodology claim | No universal API claim | [VERIFY] | Synthetic load must be interpreted narrowly |
| C37 | Autoscaling SLO thresholds must be service-specific | Service reliability contract / SLO documentation owned by service | Workload-specific | [VERIFY] | No universal thresholds asserted |
| C38 | Metrics and scaling changes should use least-privilege access and change records | Kubernetes RBAC: https://kubernetes.io/docs/reference/access-authn-authz/rbac/ | Policy-dependent | [VERIFY] | Full RBAC design deferred to Unit 9 |

## Ten-pass content audit

This is an editorial and structural audit of the lesson text. No live docs, cluster, YAML server-side validation, or labs were executed. A “pass with limitations” means the content is present and its unresolved verification is explicitly recorded; it does not mean runtime behavior was tested.

| Pass | Focus | Checks performed | Status | Findings / corrections |
|---|---|---|---|---|
| 1 | Roadmap alignment | Correct Unit 6 title and neighboring unit links; no adjacent lesson included as a replacement | Pass with limitations | Repository tree and authoritative syllabus were not independently inspected in this authoring context; scope follows the supplied prompt |
| 2 | Coverage completeness | L1–L4, VPA awareness, incident scenario, node capacity loop, and required labs addressed | Pass with limitations | VPA installation is intentionally conditional on verified support |
| 3 | Kubernetes correctness | HPA API, requests, formula caveats, metrics, behavior fields and condition explanations included | Pass with limitations | Live docs not checked; version-sensitive details remain `[VERIFY]` |
| 4 | Version-sensitive claims | VPA modes, in-place resize, Metrics Server setup and TLS workaround qualified | Pass with limitations | Learner must verify exact component and cluster versions |
| 5 | Manifest correctness | HPA target references and label selectors are internally consistent; resource requests included | Pass with limitations | Image and capacity-lab placeholders prevent blind application; server-side validation not run |
| 6 | Command and lab safety | Context checks, bounded load, dedicated namespaces, cleanup and cleanup verification included | Pass with limitations | Exact Metrics Server installation and drain-free scaling environment must be verified |
| 7 | Scaling analysis | Metrics, flapping, startup lag, HPA/VPA interaction, quota, Pending Pods, queue lag and controller boundaries covered | Pass with limitations | Provider-specific autoscaling is conceptual only |
| 8 | SRE/capacity/security | SLI/SLO, fairness, headroom, risk, least privilege, runbook and evidence included | Pass with limitations | No production metrics or cost data available |
| 9 | Source integrity | Official source entry points and 38 material claims registered | Pass with limitations | URLs are verification targets, not represented as live-checked |
| 10 | Pedagogy and sign-off | Measurable objectives, progressive levels, answer keys, exactly five senior questions and honest limitations included | Pass with limitations | Labs are documented, not executed; no fabricated output is claimed |

## Honest sign-off

- **Exact target file:** `Stage 2E — Production DevOps & Platform Engineering/03-Production-Kubernetes-Operations/06-horizontal-and-vertical-autoscaling.md`; standalone artifact saved as `06-horizontal-and-vertical-autoscaling.md`.
- **Coverage:** L1, L2, L3 and L4 included, covering HPA, VPA awareness, metrics, capacity, queue scaling, SLOs, incidents, governance and safe local labs.
- **Labs:** Four core labs plus one optional VPA recommendation exercise. **Labs are documented but were not executed by the author.**
- **Claim register:** 38 material claims; all remain `[VERIFY]` because no live documentation or cluster verification was performed in this authoring run.
- **Audit:** Ten editorial/content passes recorded as “Pass with limitations.”
- **Unresolved limitations:** The repository tree and authoritative M03 syllabus were not independently inspected. Images and selected resource values are placeholders. Current API fields, behavior defaults, Metrics Server installation/TLS behavior, VPA modes, in-place resize support, and provider-specific node autoscaling must be checked against the actual environment. No cluster commands or manifests were executed or server-side validated.
- **Diff status:** No repository diff was available to inspect.
- **Repository boundary:** This is a standalone artifact. No other repository files were intentionally modified.
