# Pod Disruption Budgets and Graceful Shutdown

## Lesson metadata

| Field | Details |
|---|---|
| Roadmap | Stage 2E — Production DevOps & Platform Engineering |
| Module / unit | M03 — Production Kubernetes Operations, Unit 5 |
| Target filename | `05-pod-disruption-budgets-and-graceful-shutdown.md` |
| Level progression | L1 beginner → L2 intermediate → L3 advanced → L4 expert |
| Estimated learning time | 10–14 hours including the four core labs; optional Lab 5 adds 1–2 hours |
| Prerequisites | Linux and Git basics; Docker/container image fundamentals; `kubectl`; Pods, Deployments, Services, readiness probes, and basic logs |
| Learning tools | `kubectl`, `kind`, Docker/Podman compatible with kind, Python 3 standard library; a terminal |
| Knowledge baseline | Learner has not operated a production cluster and has not previously configured PDBs |
| Review date | 2026-10-25 |
| Kubernetes baseline | Use the API and CLI supported by the learner's installed cluster. Check the current Kubernetes documentation, version-skew policy, `kubectl drain --help`, and `kubectl explain poddisruptionbudget` before running version-sensitive examples. |
| Verification status | No cluster, lab, command, or live documentation check was performed while authoring this lesson. Version-sensitive details are marked `[VERIFY]`. |

> **Safety contract:** These labs are disposable-cluster simulations only. Do not run them against production or a shared cluster. Read every command before executing it. The examples do not prove zero downtime, production safety, or cloud-provider behavior.

## Why this matters in production

Node maintenance is routine: a worker may need a kernel patch, kubelet upgrade, hardware replacement, or retirement. The difficult part is not merely removing Pods from a node; it is preserving enough healthy service capacity while applications stop work, replacement Pods become ready, and traffic shifts.

A PodDisruptionBudget (PDB) is a guardrail for supported voluntary eviction operations. It expresses how much disruption a selected group of Pods may tolerate at a point in time. It does not add replicas, create spare nodes, fix broken readiness checks, protect against sudden node failure, or guarantee that clients experience no errors.

Graceful shutdown is the application-side counterpart. A service should stop accepting new work, allow in-flight work to finish within a bounded time, checkpoint or safely release work where applicable, close dependencies, and exit. A PDB cannot make an application handle `SIGTERM` correctly. Conversely, a graceful application cannot create capacity for a replacement Pod that has nowhere to schedule.

Production availability therefore depends on a chain of conditions:

1. The workload has the right replica count and application-level redundancy.
2. The PDB selector matches exactly the intended Pods and permits a safe disruption.
3. The scheduler has feasible capacity and placement for replacements.
4. The application is healthy and can shut down within its measured budget.
5. Traffic routing and endpoint propagation tolerate transition races.
6. Operators have a stop/abort decision tied to service indicators and explicit risk acceptance.

A drain that waits for hours may be protecting availability—or exposing an availability design that cannot tolerate maintenance. The correct response is evidence-first diagnosis, not immediately weakening the budget.

## Learning objectives

By the end of this lesson, the learner will be able to:

- [L1] Distinguish voluntary from involuntary disruptions and explain the limits of a PDB.
- [L1] Describe the cordon → drain/eviction → termination → rescheduling → validation workflow.
- [L2] Write a PDB whose selector exactly matches a workload and explain `minAvailable`, `maxUnavailable`, percentage semantics, and status.
- [L2] Design bounded, observable shutdown behavior for an HTTP API or queue worker, including signal handling and in-flight work.
- [L3] Diagnose a blocked drain using PDB status, Pod readiness, events, ownership, scheduling constraints, and capacity evidence.
- [L3] Explain PDB interactions with rollouts, StatefulSets/quorum, HPA, Jobs, CronJobs, DaemonSets, local data, long-lived connections, and node replacement.
- [L3] Run safe local simulations and record actual evidence without treating illustrative output as observed results.
- [L4] Propose a workload-aware PDB policy, maintenance decision matrix, and SLI/SLO-based stop criteria.
- [L4] Review a drain plan and identify assumptions, residual risk, approvals, and recovery evidence.

## Prerequisite refresher and scope boundaries

| In scope in this unit | Deferred to a later unit |
|---|---|
| Voluntary disruption, eviction, PDB configuration/status, node cordon/drain/uncordon | Full cluster upgrade orchestration → M03 Unit 8 |
| Termination grace period, `preStop`, signal delivery, bounded shutdown, readiness during termination | Container image construction and hardening → M01 |
| Deployment/StatefulSet/Job/CronJob interactions relevant to disruption | Full controller fundamentals → M03 Unit 4 |
| Capacity and replica-count interactions with HPA | Autoscaler tuning → M03 Unit 6 |
| Placement, topology spread, anti-affinity and failure domains as availability prerequisites | Full node-pool/taint/placement design → M03 Unit 7 |
| Endpoint/connection-draining concepts needed to understand shutdown races | Ingress, service mesh, NetworkPolicy and advanced routing → M04 |
| Local data and stateful recovery risks | PV/PVC/CSI/operator internals → M05 |
| SLI/SLO, maintenance evidence, incident and governance practices | Full observability stack → M11; full SRE/incident program → M10 |
| Least-privilege concepts for drain/eviction | Full RBAC and Pod Security Standards → M03 Unit 9 |
| Checkpointing, retries, idempotency and residual recovery risk | Organization-wide backup/DR → M13; GitOps implementation → M08 |

Cross-module links are intentional: Unit 3 covers probe design and recovery; Unit 4 covers workload-controller behavior; Unit 6 covers autoscaling; Unit 7 covers placement; Unit 8 covers cluster upgrades; Unit 9 covers RBAC/PSS. This lesson supplies only the concepts required to make safe disruption decisions.

## Glossary

| Term | Precise definition | Operational significance |
|---|---|---|
| Pod | Kubernetes' smallest deployable workload unit, containing one or more containers sharing selected resources and network identity | A Pod is replaceable; its identity and local state do not automatically survive replacement |
| Replica | One running instance among a workload's intended instances | Replica count is not the same as healthy, ready capacity |
| Readiness | Whether a Pod is currently considered ready to receive ordinary Service traffic | A ready count influences whether a budget permits disruption; readiness must reflect real serving ability |
| Voluntary disruption | A disruption initiated by an actor or operation, such as a supported eviction for node maintenance | A PDB can constrain supported voluntary eviction paths |
| Involuntary disruption | A disruption caused by events outside a planned eviction, such as machine failure, kernel crash, or abrupt power loss | A PDB cannot prevent the event |
| Eviction | An API operation that requests removal of a Pod while allowing disruption controls, including PDB checks, to apply where supported | Preferred mechanism for maintenance workflows that must respect a PDB |
| Direct deletion | A request to delete a Pod object rather than using the Eviction API | Do not assume it has the same PDB enforcement as eviction; verify current behavior |
| Cordon | Marking a node unschedulable for new ordinary Pods | Does not evict existing Pods |
| Drain | A maintenance workflow that cordons a node and evicts eligible Pods, subject to options and constraints | May wait or fail due to PDBs, local data, DaemonSets, unmanaged Pods, or scheduling problems |
| Uncordon | Marking a node schedulable again | Do this only after the node is actually ready to receive workloads |
| PDB | `PodDisruptionBudget`, a policy for allowed voluntary disruption among selected Pods | A guardrail, not an uptime guarantee |
| `disruptionsAllowed` | Current budget status indicating how many voluntary disruptions are allowed at that observation | A snapshot, not a promise that every drain will succeed |
| Termination grace period | Bounded time Kubernetes allows for Pod termination before final forced termination behavior may occur | Must be sized from measured application shutdown behavior |
| `preStop` | A container lifecycle hook invoked as part of termination when configured | Can coordinate shutdown but consumes the termination grace-period budget |
| `SIGTERM` | A conventional termination signal sent to a process | Application code and process layout determine whether it is handled correctly |
| PID 1 | The process with process ID 1 inside a container's PID namespace | Signal forwarding and child-process reaping can be affected by shell wrappers and process supervisors |
| EndpointSlice | Kubernetes API representation of endpoints associated with a Service | Endpoint state and data-plane routing do not update instantaneously everywhere |
| In-flight request | A request already being processed when shutdown starts | Must be completed, safely failed, or bounded by an explicit timeout |
| Checkpoint | Durable record of completed work or progress | Supports recovery after termination; checkpoint boundaries must be correct |
| Idempotency | Repeating an operation has the same intended effect as performing it once | Reduces harm from retries and duplicate queue/batch processing |
| Quorum | Minimum participating members needed for a distributed system to make progress safely | A PDB alone cannot prove that a database or consensus group retains quorum |
| Failure domain | A unit that may fail together, such as a node, rack, or availability zone | Replicas colocated in one failure domain may not provide meaningful resilience |
| SLI / SLO | Service-level indicator / objective | Maintenance decisions should be grounded in the service's own observed reliability target |

## Mental model: disruption, eviction, termination, and recovery

```text
Operator / maintenance controller
             |
             v
      Confirm target + health
             |
             v
       Cordon node
   (new ordinary Pods avoid it)
             |
             v
       Drain / Eviction API
             |
       +-----+------+
       |            |
 PDB permits?     PDB blocks?
       |            |
       v            v
  Eviction accepted  Diagnose health, budget,
       |             selectors, capacity, owners
       v
 Pod termination begins
       |
       +--> lifecycle hook (if configured)
       +--> process receives termination signal
       +--> app stops new work and drains
       +--> exits before grace deadline?
       |             |
       | yes         | no
       v             v
   Pod exits      forced termination may occur
       |
       v
 Controller creates/reconciles replacement
       |
       v
 Scheduler places replacement
       |
       v
 Readiness + service-health verification
       |
       v
 Infrastructure maintenance / uncordon when safe
```

The diagram is conceptual, not a universal event-order guarantee. Kubernetes control-plane reconciliation, kubelet actions, endpoint updates, proxy/data-plane convergence, and application behavior can overlap. Verify current lifecycle documentation for the cluster version and runtime.

Key distinctions:

- **Cordon is not drain.** Cordon prevents ordinary new scheduling to the node; it does not remove existing Pods.
- **Drain is not a guarantee of replacement.** Eviction can be accepted while the replacement later remains Pending because capacity, affinity, taints, quota, topology, or storage constraints make it unschedulable.
- **A PDB is not a replica controller.** Deployments and StatefulSets reconcile desired replicas; the PDB constrains supported voluntary eviction. Neither can instantly create node capacity.
- **Termination is not an atomic traffic switch.** Readiness changes, endpoint updates, connection handling, and signal delivery have timing differences.
- **Recovery must be observed.** A successful drain command is not proof that the application returned to its baseline SLI or that every replacement is healthy.

## L1 — Beginner: understand disruption and maintenance

### 1. What is a disruption?

A disruption is an event that reduces or changes the running workload instances. Two broad categories matter:

**Voluntary disruptions** are initiated by an actor or planned operation: draining a node for maintenance, evicting a Pod through the Eviction API, or other supported administrative operations. PDBs are primarily designed to constrain supported voluntary evictions.

**Involuntary disruptions** are unplanned events such as node power loss, kernel crash, hardware failure, or a process/node becoming unhealthy due to resource exhaustion. A PDB cannot stop a node from failing. Some planned operations can also lead to disruption through paths that do not honor a PDB; never assume every deletion path is budget-gated.

A PDB is useful only when its workload, readiness, replica count, placement, and capacity assumptions are sound. If three replicas all run on one worker, a single node failure can remove all three even if the PDB was configured carefully.

### 2. Pod, replica, readiness, availability, and replacement

A Deployment may desire three replicas. That is a desired count, not proof that three instances are healthy. At a given moment, the cluster might have three Pod objects but only two ready Pods. A readiness probe that is too permissive may report a process ready even though its dependency is unavailable; a probe that is too strict can unnecessarily shrink the healthy count.

When an eviction is accepted, the Pod begins termination. A controller may create a replacement Pod to restore the desired replica count. The scheduler must then find a feasible node, and the new Pod must start and become ready. The old Pod's exit and the replacement's readiness are separate events.

For a user-facing API, “available” should ultimately be measured from successful client requests and latency, not only by counting Ready Pods. For a queue worker, useful indicators may include oldest-message age, queue lag, completion latency, and durable work completion.

### 3. What a PDB protects—and what it does not

A PDB communicates a minimum healthy count or maximum unavailable count for selected Pods during supported voluntary evictions. For example, a three-replica service with `minAvailable: 2` is intended to preserve at least two healthy Pods during a budget-governed voluntary disruption.

A PDB does **not**:

- prevent involuntary node or process failure;
- guarantee zero failed requests;
- create replicas or spare node capacity;
- ensure replacement Pods can schedule;
- guarantee an application's quorum, transaction safety, or data durability;
- make readiness probes correct;
- block every direct Pod deletion path;
- replace graceful shutdown, topology-aware placement, backups, or application-level replication.

### 4. Basic node maintenance commands

The command classification below is important. Commands that inspect state are read-only; cordon, drain, and uncordon change cluster state.

| Command | Classification | Purpose and caution |
|---|---|---|
| `kubectl get nodes -o wide` | Read-only | Inventory nodes and their readiness |
| `kubectl get pdb -A` | Read-only | Inventory PDBs across namespaces; access may be restricted |
| `kubectl describe pdb -n <namespace> <pdb-name>` | Read-only | Inspect selector, current/desired health and allowed disruptions |
| `kubectl get pods -n <namespace> -o wide` | Read-only | Inspect Pod readiness and node placement |
| `kubectl get events -n <namespace> --sort-by=.lastTimestamp` | Read-only | Inspect recent events; sorting field/output behavior is `[VERIFY]` for the installed version |
| `kubectl cordon <node>` | Mutating | Prevent ordinary new scheduling to a node; confirm context and node first |
| `kubectl drain <node> ...` | Mutating | Evicts eligible Pods; options and behavior must be checked with current `kubectl drain --help` |
| `kubectl uncordon <node>` | Mutating | Re-enable scheduling only after the node is safe |

Before any mutating command, run and inspect:

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get namespaces
```

Then explicitly choose the namespace for workload commands. Do not copy a node name or context from an example without verifying it. A command aimed at the wrong context can disrupt an unrelated environment.

### 5. Conceptual termination sequence

When a supported deletion or eviction starts termination, Kubernetes coordinates Pod shutdown. The kubelet and container runtime participate; configured lifecycle hooks may run; the application process may receive a termination signal; the application gets a bounded grace period; and if it has not exited when the deadline is exhausted, final termination behavior can be forced. Exact ordering and edge cases depend on the lifecycle path, runtime, hooks, and Kubernetes version: consult the official Pod termination documentation.

Do not teach this as “the endpoint is removed everywhere, then SIGTERM is sent, then all requests finish.” Those events are not globally atomic. Endpoint and data-plane propagation can overlap with application shutdown.

### 6. Eviction API versus direct deletion

The Eviction API is the maintenance-oriented path that can honor a PDB. A direct Pod deletion is a different API operation and must not be assumed to enforce the same disruption-budget gate. Drain commonly uses eviction behavior for eligible Pods, but exact flags and fallback behavior are version-sensitive. Check current official documentation and `kubectl drain --help` before operational use. `[VERIFY]`

### 7. First operational mental model

A safe operator asks four questions before a drain:

1. **What will be disrupted?** List Pods, owners, and data implications on the node.
2. **What does the budget permit now?** Inspect matching PDBs and `disruptionsAllowed`.
3. **Can the workload recover?** Check replicas, readiness, placement, quota, and spare capacity.
4. **How will we know it is safe?** Define service-level indicators, stop conditions, and recovery evidence.

## L2 — Intermediate: configure PDBs and graceful application shutdown

### 1. PDB fields and semantics

A PDB in `policy/v1` has a selector identifying the Pods to which it applies and a disruption allowance expressed using one of the main alternatives:

- `spec.selector`: labels matching the intended Pod set. A PDB does not automatically select Pods by Deployment name. The labels must match the Pod template's labels.
- `spec.minAvailable`: desired minimum number or percentage of healthy selected Pods that should remain available during voluntary disruption.
- `spec.maxUnavailable`: maximum number or percentage of selected Pods that may be unavailable due to voluntary disruption.
- `status.currentHealthy`: currently observed healthy selected Pods.
- `status.desiredHealthy`: healthy count the budget is trying to preserve.
- `status.disruptionsAllowed`: current count of voluntary disruptions allowed.
- `status.expectedPods`: expected selected Pod count in the status model, where exposed by the API.

Status is controller-maintained and can lag changes. Read it as a current observation, not a reservation of future capacity. The `policy/v1` API and exact behavior must be checked for the installed version. `[VERIFY]`

`minAvailable` and `maxUnavailable` are alternative ways to express the same kind of policy; choose the one that makes the operational intent clearer. Do not configure both in the same PDB. Integer and percentage rounding rules are important: consult the current official docs before using percentages for small replica sets. `[VERIFY]`

### 2. Example A: Deployment and `minAvailable`

The following is a coherent local example. The image is a placeholder; replace it with an image you can pull or load into kind. This example does not provide an HTTP server implementation.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  namespace: disruption-lab
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: scoring-api
    spec:
      terminationGracePeriodSeconds: 30
      containers:
        - name: api
          image: <REPLACE_WITH_AVAILABLE_HTTP_IMAGE>
          ports:
            - name: http
              containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: scoring-api
  namespace: disruption-lab
spec:
  selector:
    app.kubernetes.io/name: scoring-api
  ports:
    - name: http
      port: 80
      targetPort: http
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: scoring-api-pdb
  namespace: disruption-lab
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
```

The PDB selector matches the Pod-template label exactly. The Deployment selector and Service selector use the same label intentionally. In a real service, include resource requests, appropriate probes, a real image, and workload-specific shutdown settings; those details are omitted here to keep the PDB relationship visible.

### 3. Example B: `maxUnavailable` and percentage

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: scoring-api-pdb-max-unavailable
  namespace: disruption-lab
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
```

An illustrative percentage form is:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: scoring-api-pdb-percent
  namespace: disruption-lab
spec:
  maxUnavailable: "25%"
  selector:
    matchLabels:
      app.kubernetes.io/name: scoring-api
```

Use only one of these PDB definitions for the selected workload at a time. The percentage is a string in the manifest. Rounding and small-replica behavior are version-sensitive details to verify against the official API docs. A percentage that looks conservative can behave unexpectedly for a small selected set; calculate the effective result and test it in a disposable cluster before adoption. `[VERIFY]`

### 4. Example C: intentionally blocking PDB (unsafe, local-only)

This configuration is intentionally restrictive for Lab 3. Do not copy it as a production default.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: intentionally-blocking-pdb
  namespace: disruption-lab
  labels:
    lesson.example.com/purpose: local-only-blocked-drain-lab
spec:
  minAvailable: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: blocked-demo
```

If exactly three selected Pods are healthy, the budget may allow zero voluntary disruptions at that observation. The actual status depends on current Pod health and the controller's status calculation. Confirm with `kubectl describe pdb`; never infer the live allowance from YAML alone.

### 5. Selector failures and blast radius

Common selector mistakes include:

- **Mismatch:** PDB selector matches no Pods, so the budget is not protecting the intended workload.
- **Overbroad selector:** multiple unrelated applications share the same label and become one disruption group.
- **Assumed owner selection:** the PDB does not automatically infer a Deployment name or owner reference from its name.
- **Accidental overlap:** more than one PDB may select the same Pod set. Validate supported behavior and avoid overlapping budgets unless the current API documentation explicitly supports the design. `[VERIFY]`

Inspect actual labels and owners:

```bash
kubectl get pods -n disruption-lab --show-labels
kubectl get pods -n disruption-lab -o wide
kubectl get pdb -n disruption-lab
kubectl describe pdb -n disruption-lab scoring-api-pdb
```

### 6. Choosing `terminationGracePeriodSeconds`

The grace period is not a guess or a substitute for fixing a stuck shutdown. Measure normal shutdown duration under representative load, including the slowest supported in-flight operation and time to close dependencies. Then add a justified margin consistent with the maintenance objective. A 30-second example is not a universal recommendation.

A practical shutdown budget might be decomposed as:

| Phase | Measurement to collect |
|---|---|
| Stop admission / stop polling | Time from shutdown signal to refusal of new work |
| Drain in-flight requests/work | Distribution and worst supported duration |
| Flush/checkpoint | Time to persist required state safely |
| Close clients and exit | Time to close pools, sockets, and child processes |
| Safety margin | Explicitly justified allowance for scheduling and runtime variance |

If work can take longer than the grace period, design a safe cancellation/checkpoint/retry strategy rather than choosing an arbitrarily huge grace period. A process can still be killed after the deadline.

### 7. `preStop` hooks: use with care

A configured `preStop` hook runs as part of container termination and its execution consumes the Pod's termination grace-period budget. It can call a local endpoint, notify the process, or coordinate an application-specific transition if the implementation is correct. It cannot guarantee endpoint propagation, repair broken signal handling, or ensure every request finishes.

A long `sleep` is not a universal or race-free fix. It consumes the same bounded shutdown window and may simply delay useful work. Endpoint and data-plane propagation are not instantaneous or perfectly ordered. Prefer explicit application readiness/shutdown behavior and measure the transition. Verify exact hook semantics and timing for the target Kubernetes version. `[VERIFY]`

### 8. Python process signals, PID 1, and server shutdown

On Unix-like systems, signal handling is a process concern. Container command form matters:

- Exec-form commands typically launch the target executable directly as the container process.
- Shell-form commands can introduce a shell wrapper that may not forward signals as intended.
- If a wrapper is needed, use a deliberate process-management design and test signal delivery. Do not assume a shell script will forward `SIGTERM`.
- PID 1 has special process-management implications in a PID namespace; an init process or supervisor may be needed when a container manages children. Refer to M01 for image construction and runtime defaults.

FastAPI is an ASGI framework; Uvicorn is an ASGI server. Their shutdown lifecycle is affected by the server version and configuration, including graceful-shutdown timeout settings. Do not claim a specific default or exact ordering without checking the installed version's official documentation. `[VERIFY]`

A robust API shutdown should:
1. stop admitting new work or mark itself unready as appropriate;
2. allow already admitted requests to finish within a bounded deadline;
3. stop background tasks safely;
4. close database/HTTP clients and connection pools;
5. log phase timestamps and outstanding work;
6. exit before the Kubernetes grace period expires, under normal conditions.

A queue consumer should stop polling/claiming new messages, finish or safely release in-flight work, acknowledge only after durable success, and checkpoint long ETL jobs at meaningful boundaries. Exactly-once processing should not be assumed: retries and duplicate delivery are common design constraints.

### 9. Illustrative Python shutdown pattern (standard library)

This is a teaching pattern, not a complete production server. It demonstrates a signal flag and bounded work loop. It does not implement HTTP, a durable queue, or a real checkpoint store.

```python
import logging
import signal
import threading
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
stop_requested = threading.Event()

def request_stop(signum, frame):
    logging.info("shutdown_signal_received signal=%s", signum)
    stop_requested.set()

signal.signal(signal.SIGTERM, request_stop)
signal.signal(signal.SIGINT, request_stop)

def do_one_bounded_unit():
    # Replace with one unit whose duration and recovery behavior are understood.
    time.sleep(0.2)
    return "durable-success"

logging.info("worker_started")
while not stop_requested.is_set():
    # In a real consumer, stop claiming new work once stop_requested is set.
    result = do_one_bounded_unit()
    logging.info("unit_finished result=%s", result)

logging.info("stop_new_work=true")
# In a real system: wait for tracked in-flight work up to a deadline,
# flush/checkpoint durable state, release unfinished leases, then close clients.
logging.info("shutdown_complete")
```

The sample intentionally keeps signal handlers simple. Production code must use the framework's documented lifecycle hooks, track in-flight work, enforce deadlines, and test a forced-timeout case. The example's `do_one_bounded_unit` is not a durable transaction; its result string is not proof of persistence.

### 10. Readiness, endpoint propagation, and connection draining

Readiness and termination are related but distinct. A readiness probe informs Kubernetes whether a Pod should be considered ready for ordinary Service traffic. During termination, endpoint conditions and routing behavior change, but propagation across controllers and data planes takes time. Existing keep-alive HTTP connections, WebSockets, gRPC streams, and client-side connection pools may outlive a routing update.

Mitigation patterns include:
- application-controlled “not accepting new work” state;
- a readiness transition based on actual serving capability;
- bounded in-flight request draining;
- explicit client/server timeouts;
- retry-safe request design and idempotency keys where appropriate;
- observing endpoint conditions and request outcomes during a controlled test.

No single sleep duration makes the system race-free. Measure the behavior in the actual deployment path; kind cannot reproduce every cloud load balancer or production data-plane condition.

Conceptual relationship:

```text
Traffic / endpoint handling ----\
                                 \ (events can overlap)
Readiness transition ------------+--> stop accepting new work
Termination signal --------------/            |
                                              v
                                    drain in-flight work
                                              |
                                              v
                              flush / checkpoint / close
                                              |
                                              v
                                         process exit
```

## L3 — Advanced: diagnose blocked drains and termination failures

### 1. Why a drain can block

A drain can remain blocked because the PDB currently permits no eviction, selected Pods are unhealthy, the replacement cannot become schedulable, or the command is waiting on another condition. A blocked drain is not proof that the PDB is wrong.

Common cases:

1. `minAvailable` equals the current healthy replica count. A voluntary eviction would reduce health below the configured target.
2. A single-replica workload has a budget that allows no disruption. Maintenance may be impossible without a planned outage or a workload design change.
3. Selector mismatch means the budget does not cover the intended Pods, or an overbroad selector covers unrelated Pods.
4. Unready Pods reduce the available allowance.
5. Replacement Pods cannot schedule due to CPU/memory requests, node selectors, taints/tolerations, affinity, topology spread, quota, storage constraints, or insufficient nodes.
6. A stateful workload needs application-level quorum or ordered maintenance beyond what the PDB expresses.
7. A local-data Pod, DaemonSet, unmanaged Pod, or Job requires a specific drain option or a separate recovery decision.

### 2. Read-only diagnostic sequence

First establish scope and capture evidence:

```bash
# Read-only
kubectl config current-context
kubectl get nodes -o wide
kubectl get pods -A -o wide
kubectl get pdb -A
kubectl get events -A --sort-by=.lastTimestamp
```

Then narrow to the affected namespace and workload:

```bash
# Read-only
kubectl get pdb -n <namespace>
kubectl describe pdb -n <namespace> <pdb-name>
kubectl get pods -n <namespace> -o wide --show-labels
kubectl describe pod -n <namespace> <pod-name>
kubectl get deploy,statefulset,job,cronjob -n <namespace>
```

Use `kubectl describe node <node>` and inspect Pending replacement Pods' events. For each Pod on the target node, determine its owner and data implications. Check current CLI help before using drain options:

```bash
kubectl drain --help
kubectl explain poddisruptionbudget
kubectl explain poddisruptionbudget.spec
```

The output of `kubectl get events --sort-by=.lastTimestamp` and available `kubectl explain` fields can vary by version. `[VERIFY]`

### 3. Unhealthy Pods and PDB behavior

Kubernetes has behavior and configuration concerning eviction of unhealthy Pods, and support has evolved across releases. Do not guess field names, defaults, or feature-gate requirements. Check the current PodDisruptionBudget documentation and API reference for the exact cluster version before relying on an unhealthy-Pod eviction policy. `[VERIFY]`

Operationally, establish whether the selected Pods are healthy and whether the budget is blocked by health. Avoid using an exception to hide a persistent application failure. If a Pod is unhealthy, identify whether it can be recovered safely, whether it has local state, and what duplicate/loss risk eviction creates.

### 4. Interactions with workload types and controllers

**Deployment rolling updates.** A Deployment rollout's `maxSurge` and `maxUnavailable` govern rollout behavior, while the PDB governs supported voluntary eviction. They are different controls and should not be assumed to compose into a single guaranteed availability number. Capacity, readiness, rollout progress, and concurrent drains can interact. See Unit 4 for rollout fundamentals.

**StatefulSets and quorum.** StatefulSets preserve stable identity and ordered behavior according to their configuration, but this is not the same as application correctness. A database may need quorum, replication lag limits, leader transfer, or one-at-a-time maintenance. Consult the database's operational guidance. A PDB cannot infer quorum from Pod health.

**HPA.** Autoscaling can change replica count while maintenance is being planned. A budget's current status may change as replicas and health change. Avoid treating a single `disruptionsAllowed` reading as a long-lived reservation. Unit 6 covers autoscaling.

**Cluster autoscaler / managed node replacement.** Automated node replacement or upgrade tools may drain nodes using their own retry and timeout policies. Behavior is provider- and version-specific. Verify the provider's current documentation and ensure the application owner understands the effect of a PDB that blocks replacement. Do not assume all providers use identical drain semantics. `[VERIFY]`

**Jobs and CronJobs.** A non-replicated batch Job may not have a redundant replica to replace an interrupted task. A CronJob may create a new run according to its schedule and concurrency policy, but that does not prove the previous work was completed exactly once. Design checkpoints, retries, and idempotency. A PDB is not a substitute for a job recovery plan.

**DaemonSets.** Drain commonly treats DaemonSet-managed Pods specially; operators may need the documented DaemonSet option. Verify the exact behavior and flags in current `kubectl drain --help`. Do not add a flag just to make a command complete without understanding what it changes. `[VERIFY]`

**Local ephemeral storage and local data.** A Pod may have data on node-local storage that does not follow it to another node. Drain options that permit local data loss must be treated as explicit risk acceptance. Do not delete PVCs or persistent data in these labs. Storage implementation details are deferred to M05.

**Topology spread and anti-affinity.** Replicas that cannot spread across nodes or failure domains may all be exposed to the same event. Replacement Pods can remain Pending if constraints cannot be satisfied. Unit 7 covers placement in depth.

**Long-lived connections.** Routing changes do not guarantee that existing streams end immediately. Applications and clients need bounded connection lifetimes, retry behavior, and a drain strategy appropriate to HTTP, WebSockets, or gRPC.

**Spot/preemptible nodes.** A termination notice may offer a bounded window, but it is not a guarantee that the application has time to complete all work. Verify provider-specific interruption timing and build checkpoint/retry safety.

### 5. Safe maintenance sequencing

1. Confirm current context, namespace, and target node.
2. Inventory all Pods on the node and identify owners, controllers, local data, Jobs, DaemonSets, and stateful/quorum dependencies.
3. Inspect PDBs, selectors, `disruptionsAllowed`, current health, and replica counts.
4. Verify spare schedulable capacity and that replacement constraints can be met.
5. Coordinate a maintenance window with service and platform owners; record SLI baseline and stop criteria.
6. Cordon the target node after approval.
7. Drain with documented, version-verified options and a bounded timeout/abort plan. Do not drain the control-plane node in the local labs.
8. Observe eviction, rescheduling, readiness, logs, events, and service indicators.
9. Perform infrastructure maintenance only after safe eviction and service validation.
10. Uncordon only after the node is healthy and ready to accept workloads.
11. Revalidate service health, capture evidence, and document exceptions/follow-up.

### 6. Why bypassing a PDB is not a routine fix

Forceful deletion or an option that ignores PDB protection can remove the guardrail that was preventing simultaneous disruption. It may be appropriate only under an explicitly approved risk decision—for example, an urgent security patch where leaving a vulnerable node in service is the greater risk—but it is not the default response to a stuck drain.

Before an override:
- capture PDB status, selected Pods, readiness, scheduling constraints, and SLI;
- identify the service owner and decision authority;
- calculate the expected blast radius and recovery path;
- state why normal eviction cannot proceed and why delay is more dangerous;
- obtain the required approval and record expiry/scope;
- use the narrowest supported operation;
- monitor the service and verify recovery;
- create follow-up actions to prevent recurrence.

Do not execute a forceful bypass in the labs. Check exact flag semantics against current help and official docs before any real maintenance. `[VERIFY]`

### 7. Incident walkthrough: “Node drain has been blocked for hours by a PDB”

All names, times, and output below are **illustrative examples**, not observed command results.

**Symptom.** At 10:00, an operator starts a planned worker drain. The command remains waiting on a Pod eviction and the maintenance window is at risk.

**Impact.** A patch is delayed. The API remains healthy, but the unpatched node remains in service longer than planned. There is no evidence yet that the budget is misconfigured.

**Initial hypotheses.**
- The PDB allows zero disruptions.
- The selected Pod is unready.
- A selector covers more Pods than intended.
- Replacement Pods cannot schedule.
- The Pod is a DaemonSet, Job, or uses local data.
- The drain is using an incompatible option or API path.

**Read-only diagnostics.**
- Confirm context, node state, PDB inventory and status.
- Identify the Pod's owner, labels, readiness, node placement, and recent events.
- Inspect Pending replacements and scheduler events.
- Review spare node capacity, quota, taints, affinity, and topology constraints.
- Compare the service SLI with its baseline.

**Illustrative finding.** The API has three desired replicas, but only two are healthy. The PDB asks for two healthy replicas and status reports zero disruptions allowed at this moment. The third Pod is unready because its dependency connection pool is failing. A replacement Pod would also be constrained by a node selector and current capacity. This means the PDB is exposing a real recovery/capacity issue rather than merely blocking a safe operation.

**Safest mitigation.**
1. Pause the drain; do not bypass the budget.
2. Engage the service owner and restore the unready replica or correct its dependency problem.
3. Confirm the replacement can schedule and become ready.
4. Re-check PDB status and service SLI.
5. Resume only when the maintenance preconditions are met. If the security deadline makes delay unacceptable, follow the organization's formal risk-acceptance path.

**Illustrative timeline.**

| Time | Event | Decision/evidence |
|---|---|---|
| 10:00 | Drain begins | Baseline SLI and node/Pod inventory captured |
| 10:10 | Eviction still blocked | Pause; inspect PDB and Pod health |
| 10:20 | One selected Pod found unready | Escalate to service owner; do not override |
| 10:45 | Dependency issue corrected | Confirm readiness, endpoint and request behavior |
| 10:55 | PDB allowance changes | Re-evaluate capacity and maintenance window |
| 11:05 | Drain resumes | Observe eviction and replacement readiness |
| 11:20 | Workload healthy on remaining nodes | Validate SLI and document actual duration |

**Recovery verification.** Confirm the target node is drained as intended, replacement Pods are Ready, no unexpected Pending Pods remain, service SLI has returned to its agreed range, and relevant events/logs have been captured. Do not assume the example timeline or result will match a real cluster.

**Prevention.** Add pre-maintenance checks for healthy replica count, scheduling headroom, PDB allowance, and dependency readiness; review capacity and topology; establish an owner escalation path; and rehearse the runbook.

### 8. Graceful-shutdown test plan

A shutdown test should deliberately put work in flight, start termination, and capture timestamps for each phase. Record whether the request completes, whether new work is rejected or routed away, whether the process exits before the grace deadline, and whether any forced termination occurs.

| Test | Setup | Expected evidence | Pass criterion |
|---|---|---|---|
| In-flight request | Start a request whose bounded duration is known, then initiate Pod termination | Client timestamp, app logs, Pod events/status | Outcome matches the declared shutdown contract |
| New work during shutdown | Send additional requests after shutdown begins | Readiness/endpoint observations and request outcomes | App does not silently accept work it cannot safely finish |
| Normal exit | Set grace period longer than measured normal drain budget | Signal and phase timestamps, process exit evidence | Process exits before deadline without forced termination |
| Forced timeout | Separate disposable workload with intentionally longer work than grace period | Timeout and termination evidence | Failure mode is understood; no production resources affected |
| Endpoint overlap | Observe readiness, endpoint conditions, and client outcomes | Timestamps from multiple views | Races and limitations are documented, not assumed away |

A test passes only based on observed evidence. Do not assert zero dropped requests unless the harness and results demonstrate it for the tested setup.

### 9. ETL and queue checkpointing

For a batch ETL Job or queue worker, shutdown correctness is primarily a data-integrity question.

- Define a durable checkpoint boundary: for example, after a batch is committed and its output manifest is durable.
- Do not acknowledge a queue message before its side effect is durably committed.
- If commit succeeds but acknowledgement fails, the message may be delivered again. Make the operation idempotent or use a deduplication key.
- If a worker is terminated mid-unit, either finish within the deadline or safely release/allow retry. Never mark unfinished work complete.
- Isolate poison messages with bounded retry and an explicit dead-letter or operator review policy.
- Record checkpoint position, attempt count, idempotency key, and final outcome without logging sensitive payloads.
- If shutdown exceeds the grace period, assume the process may be killed at an arbitrary point and design recovery from the last durable boundary.

## L4 — Expert: policy, SLOs, and maintenance governance

### 1. Multi-team PDB policy design

A platform policy should express an operational contract, not a universal YAML template. A useful baseline:

**Generally require a reviewed PDB for:** replicated, user-facing services whose availability objective requires preserving a minimum healthy count during planned node maintenance.

**Require explicit exception review for:** single-replica services; Jobs/CronJobs; operators and controllers with specialized lifecycle rules; system components; and workloads whose application-level quorum or ordered maintenance cannot be represented by a generic PDB.

**Ownership requirements:**
- Each workload has a named service owner and a declared availability/recovery model.
- PDB intent is documented alongside replica count, readiness, topology, and capacity assumptions.
- Changes are reviewed with application owners and platform/SRE stakeholders.
- Exceptions include rationale, blast radius, approver, expiration date, and compensating controls.
- Policy is tested against representative manifests in a staging/disposable cluster before broad enforcement.
- Rollout begins in audit/warn mode where supported, then moves to enforcement after false positives and exceptions are understood. Exact policy-engine syntax and mode depend on the chosen implementation. `[VERIFY]`

Safe defaults are workload-specific. A multi-replica stateless API may use a minimum healthy count or bounded unavailable count. A single-replica service cannot promise zero voluntary downtime without another replica or a deliberate maintenance outage. A database needs application-aware quorum and failover guidance in addition to any PDB.

### 2. Conceptual policy-as-code check

The following is **pseudocode**, not a runnable Kyverno, Gatekeeper, CEL, or Kubernetes policy:

```text
for each workload in a namespace:
    classify workload type and owner
    if workload is a replicated user-facing service:
        require an explicit availability owner and replica intent
        require a PDB selecting exactly its intended Pod labels
        flag PDB if observed/tested policy permits zero planned disruption
        flag selectors that match zero Pods or unexpected workloads
        flag single-replica workloads without a documented maintenance exception
        require tests that simulate eviction and replacement scheduling
    if workload is a Job, CronJob, operator, system component, or quorum-sensitive stateful app:
        require workload-specific review rather than blindly applying the API default
    require exception owner, rationale, compensating control, and expiry
```

A static manifest linter cannot know current readiness, available node capacity, live PDB status, or whether the application will complete shutdown correctly. Policy checks should be paired with runtime preflight and test evidence. Do not present the pseudocode as an installable policy API.

### 3. SLI/SLO and maintenance decisions

For the sample scoring API, define an availability SLI such as:

`successful_valid_requests / total_valid_requests`

Define “successful” consistently (for example, acceptable status codes and valid requests only) and report the error rate and latency distribution alongside it. Exclude invalid client requests only if the service's SLI specification says to do so. For workers, use oldest-message age, queue lag, completion latency, retry rate, and durable completion.

Compare the maintenance window with a pre-change baseline and the service's own SLO. There is no universal acceptable error-rate threshold. Stop criteria should be defined before the drain, such as a sustained breach of the service's agreed SLO guardrail, a material rise in queue lag, loss of quorum margin, or unexpected Pending replacements. The threshold and evaluation window belong to the service's reliability contract.

`disruptionsAllowed` is useful but only a snapshot. Even when it is positive, the drain can fail or recovery can stall because of health changes, concurrent evictions, placement constraints, storage, or capacity. Re-check the relevant evidence at decision points.

### 4. Upgrade-window design checklist

- [ ] Confirm replica count and healthy replica count; record evidence.
- [ ] Confirm PDB selector and status; record `disruptionsAllowed`.
- [ ] Verify replacement capacity and placement across intended failure domains.
- [ ] Check resource requests, quotas, taints, affinity, topology spread, and local-data dependencies.
- [ ] Confirm application shutdown behavior has been tested against realistic in-flight work.
- [ ] Establish the SLI baseline, SLO guardrail, stop/abort criteria, and monitoring owner.
- [ ] Sequence nodes/failure domains to avoid correlated disruption.
- [ ] Estimate drain duration from rehearsal and include a timeout/escalation path.
- [ ] Notify service owners and confirm on-call escalation contacts.
- [ ] Define rollback/stop criteria before maintenance begins.
- [ ] Validate each workload and the aggregate service after each maintenance step.
- [ ] Capture evidence, exceptions, approvals, and follow-up items.
- [ ] Link full upgrade orchestration to M03 Unit 8; do not improvise provider-specific upgrade behavior.

### 5. Governance and residual risk

A PDB can preserve the currently healthy replica count by blocking a voluntary eviction. That may delay patching, extend the life of a vulnerable node, or prolong an unhealthy machine's presence. The decision is a trade-off between availability risk and maintenance/security risk, not an absolute rule that “PDB must never be bypassed” or “maintenance must always proceed.”

A sound governance process includes:
- maintenance calendar and change record;
- named change owner, service owner, approver, and escalation contact;
- preflight evidence and declared SLI/SLO stop conditions;
- audit trail of affected node/workloads and observed drain duration;
- explicit risk acceptance for any override, scoped to the minimum necessary action;
- expiry and review of exceptions;
- post-change verification and post-incident actions.

Least privilege matters. Drain and eviction permissions can disrupt many workloads. Use role-scoped operational access and approval controls appropriate to the platform; do not make broad cluster-admin access the default. Full authorization design is covered in M03 Unit 9.

### 6. Workload decision matrix

| Workload type | PDB approach | Shutdown/recovery concern | Maintenance decision |
|---|---|---|---|
| Stateless API with multiple replicas | Usually use a reviewed PDB matching its Pod labels | Stop admission, drain in-flight requests, readiness and endpoint propagation | Proceed only with healthy replicas, capacity, and SLI guardrails |
| Single-replica service | PDB alone cannot create redundancy; document exception or add redundancy | Planned outage may be unavoidable | Pause for owner approval and explicit outage/risk acceptance |
| Replicated queue worker | Use a PDB only if voluntary disruption semantics match the worker design | Stop polling, finish/release work, durable ack/checkpoint, idempotent retry | Check queue lag and in-flight work before and after |
| StatefulSet database | Application-aware budget plus database-specific maintenance rules | Quorum, leader transfer, replication lag, stable identity and storage | Follow database vendor/runbook; do not infer quorum from Pod health |
| Batch Job | Often requires job-specific retry/checkpoint handling rather than a generic PDB | Duplicate work and partial outputs | Checkpoint/retry semantics and deadline; coordinate with job owner |
| CronJob | Evaluate the active Job, schedule, concurrency policy, and idempotency | Overlap, missed work, retries, and durable checkpoints | Confirm schedule impact and recovery behavior |
| DaemonSet | Understand documented drain handling; PDB behavior is not a universal substitute | Node-local agents and system-level dependencies | Use current drain help and platform-specific maintenance procedure |

### 7. Senior design review: prove a node can be drained without violating the SLO

A strong review does not answer “the PDB says one disruption is allowed, so yes.” It constructs an evidence-based argument.

**Assumptions.** State workload replica count, readiness semantics, request profile, failure domains, current node health, storage constraints, and whether concurrent changes are frozen.

**PDB and health evidence.** Capture PDB selector, status, healthy count, desired healthy count, and allowed disruptions. Confirm the selector matches exactly the intended Pods. Check for unhealthy replicas and overlapping maintenance.

**Capacity math.** Sum schedulable capacity after removing the target node, accounting for resource requests, system reservations, quota, taints, affinity, topology, and expected replacement overhead. A raw CPU total is insufficient if constraints prevent placement. Include memory and other requested resources.

**Shutdown evidence.** Show a test with in-flight requests/work, measured stop-admission time, drain duration, checkpoint/close time, and margin against the configured grace period. Include forced-timeout behavior.

**Rollout/controller interactions.** Review active Deployment rollouts, HPA changes, StatefulSet quorum requirements, Jobs, CronJobs, DaemonSets, and node autoscaler/provider behavior. Prevent uncoordinated changes where necessary.

**SLI/SLO evidence.** Compare baseline and rehearsal request success/error rate, latency, and worker lag. Define pre-approved stop criteria from the actual service SLO.

**Operational plan.** Record the exact target node and context, owners, window, timeout, pause/abort decisions, escalation contacts, and recovery checks.

**Unknowns.** List what the local rehearsal cannot prove: cloud load balancer behavior, real failure-domain isolation, provider node replacement, production traffic shape, or a database's actual quorum behavior. Resolve critical unknowns with staging rehearsal or authoritative provider/application guidance.

The review conclusion should be conditional: proceed only if evidence supports the assumptions; otherwise pause, increase capacity, restore health, change placement, redesign shutdown, or accept a documented risk through the correct authority.

## Production runbook: drain a node safely

This runbook is a template, not a command sequence to run blindly. Adapt it to the cluster's supported Kubernetes version, platform provider, application runbooks, and change process.

### Preconditions and ownership

- Change owner and service owners are identified.
- Maintenance window and expected impact are communicated.
- Target node and current context are recorded.
- Service SLI baseline, SLO guardrail, and stop criteria are recorded.
- PDBs, healthy replicas, spare capacity, and replacement feasibility have been checked.
- Stateful/quorum workloads, local data, Jobs, CronJobs, and DaemonSets have explicit handling plans.
- `kubectl drain --help` and official docs have been checked for this cluster version.
- A timeout, abort path, and escalation contact are available.

### Preflight (read-only)

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get pods -A -o wide
kubectl get pdb -A
kubectl get events -A --sort-by=.lastTimestamp
```

Record the target node's Pod inventory and owners. For each workload, ask:
- Is it a Deployment, StatefulSet, Job/CronJob, DaemonSet, or unmanaged Pod?
- Does it have local data or a local-storage dependency?
- Is the application single-replica or quorum-sensitive?
- Can a replacement Pod schedule on a remaining node?
- Does its PDB match the exact intended labels?
- Are health and SLI within the agreed pre-maintenance range?

### Decision gate

- **Proceed:** health is acceptable, budget and capacity evidence are sufficient, owners approve, and no unresolved high-risk dependency exists.
- **Pause:** a Pod is unready, replacement capacity is uncertain, a drain is blocked, or evidence is incomplete.
- **Abort/rollback:** service SLI breaches the predeclared guardrail, quorum margin is threatened, data-loss risk is discovered, or recovery cannot be demonstrated.
- **Escalate:** urgent security/maintenance deadline conflicts with availability safeguards. Any override requires explicit risk acceptance and a narrow, documented scope.

### Cordon and drain

First confirm the exact context and node again immediately before mutation:

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get pods -A -o wide
```

After approval, cordon the verified node:

```bash
# MUTATING — replace <verified-node> only after confirming context and approval.
kubectl cordon <verified-node>
```

Re-check workload health and the node's state. Then consult current help and use the organization's approved drain invocation with a bounded timeout and only the options justified by the Pod inventory. A generic safe-looking command cannot be prescribed for every workload because flags that ignore DaemonSets, local data, or PDBs change the safety contract. `[VERIFY]`

Illustrative command shape only—not ready to paste:

```text
kubectl drain <verified-node> [approved, version-verified options]
```

Do not include a PDB-bypass option as routine remediation. If drain blocks, stop and diagnose rather than repeatedly retrying without collecting evidence.

### During drain

- Observe PDB status, Pod status, events, application logs, request outcomes, queue lag, and latency.
- Record timestamps for start, first eviction, replacement scheduling, readiness recovery, and completion.
- If the drain exceeds its planned timeout, pause and escalate; do not infer that waiting longer will solve capacity or readiness problems.
- Do not begin infrastructure maintenance until the required evictions have completed and service health is validated.

### Post-maintenance and uncordon

Before uncordoning, confirm the node is healthy, kubelet/runtime/network/storage prerequisites are restored, and the platform owner considers it ready. Then, after context verification and approval:

```bash
# MUTATING — only after the node is confirmed healthy and approved for scheduling.
kubectl uncordon <verified-node>
```

Validate:
- node readiness and schedulability;
- expected workload replica count and readiness;
- no unexplained Pending Pods or recurring restarts;
- PDB status returned to the expected operating state;
- application SLI/SLO and worker lag returned to the agreed range;
- relevant events and logs captured;
- change record contains actual duration, approvals, exceptions, and follow-up actions.

## Hands-on labs

All labs are **local simulations** using a disposable kind cluster. They are not faithful simulations of cloud-provider node replacement, multi-AZ failure, a real load balancer, machine failure, or production network behavior. WSL2 kernel/cgroup behavior and container-node resource limits can differ from production. `[VERIFY]`

### Shared lab safety and setup rules

Use one dedicated cluster and namespace. Do not run against a shared or production cluster. Before each mutating operation, verify current context and node topology. The commands below intentionally use a lab cluster name; if a cluster with that name already exists, inspect it instead of deleting or recreating it blindly.

```bash
# Read-only preflight
kind get clusters
kubectl config current-context
kubectl get nodes -o wide
kubectl get namespaces
```

Set shell variables only after checking your cluster:

```bash
export CLUSTER_NAME="pdb-lab"
export LAB_NS="disruption-lab"
```

Before mutating commands, re-run `kubectl config current-context` and `kubectl get nodes -o wide`. Verify that the selected context is the intended kind context. The `kind` context usually includes the cluster name, but do not rely on naming alone.

#### Lab 1 — Establish a safe local cluster and workload baseline

**Goal:** Create or verify a small local cluster, deploy a replicated HTTP workload, and record readiness, placement, and baseline request behavior.

**Prerequisites:** Docker or compatible container runtime, `kind`, `kubectl`, Python 3. **Estimated time:** 45–75 minutes.

**Cluster configuration.** Save this configuration only as an inline lesson example; create a local file yourself if desired. Replace `<NODE_IMAGE_TAG>` with a currently supported kind node image tag after checking kind documentation and Kubernetes version-skew guidance.

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: pdb-lab
nodes:
  - role: control-plane
  - role: worker
  - role: worker
  - role: worker
    # image: kindest/node:<NODE_IMAGE_TAG>
```

The commented image line shows the placeholder requirement; if you uncomment it, use the same supported image tag for all nodes unless the current kind docs explicitly support the intended mixed-version setup. The exact configuration API and image support are `[VERIFY]`.

If creating a new cluster, first check `kind get clusters`. If `pdb-lab` already exists, inspect its topology and context; do not delete it automatically. Only create the cluster after verifying the selected environment:

```bash
# MUTATING: creates local cluster resources; confirm runtime and target first.
kind create cluster --name pdb-lab --config <path-to-your-verified-kind-config>
kubectl config current-context
kubectl get nodes -o wide
```

**Workload assumption:** Use a small HTTP image available to your environment, or build and load a simple local server image following M01. Do not assume an external image is available. For a ready-to-apply workload, replace the image placeholder below with a verified image that listens on port 8080 and responds to HTTP requests.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: disruption-lab
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: baseline-api
  namespace: disruption-lab
spec:
  replicas: 3
  selector:
    matchLabels:
      app: baseline-api
  template:
    metadata:
      labels:
        app: baseline-api
    spec:
      terminationGracePeriodSeconds: 20
      containers:
        - name: http
          image: <REPLACE_WITH_VERIFIED_HTTP_IMAGE>
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 250m
              memory: 128Mi
---
apiVersion: v1
kind: Service
metadata:
  name: baseline-api
  namespace: disruption-lab
spec:
  selector:
    app: baseline-api
  ports:
    - port: 80
      targetPort: 8080
```

**Apply only after context checks** (mutating):

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl apply -f <your-reviewed-manifest-file>
kubectl rollout status deployment/baseline-api -n disruption-lab --timeout=120s
```

**Evidence to collect (actual observation required):**
- `kubectl get pods -n disruption-lab -o wide` and labels;
- `kubectl get deploy,svc -n disruption-lab`;
- baseline request count/success/error rate and a time window;
- node placement and relevant events;
- cluster topology and exact node image/version.

For a low-dependency request check, port-forward the Service in one terminal and run a small Python standard-library loop in another. This assumes the chosen image exposes HTTP on port 8080.

```bash
# Terminal A; local forwarding process
kubectl port-forward -n disruption-lab svc/baseline-api 18080:80
```

```python
# Terminal B; lightweight local HTTP sampling, no third-party package required
import time
import urllib.error
import urllib.request

total = successes = failures = 0
deadline = time.monotonic() + 30
while time.monotonic() < deadline:
    total += 1
    try:
        with urllib.request.urlopen("http://127.0.0.1:18080/", timeout=1) as response:
            if 200 <= response.status < 400:
                successes += 1
            else:
                failures += 1
    except (urllib.error.URLError, TimeoutError):
        failures += 1
    time.sleep(0.1)

print({"total": total, "successes": successes, "failures": failures,
       "success_rate": successes / total if total else None})
```

This client is deliberately simple and may not represent concurrent production traffic. Record actual values; do not copy example numbers from elsewhere.

**Interpretation:** A Deployment with three desired replicas may have fewer than three Ready Pods. Record the real baseline before testing disruptions.

**Troubleshooting:** If Pods are ImagePullBackOff, verify image name and kind image availability. If Pending, inspect events and resource constraints. If port-forward fails, verify Service selector and container port.

**Cleanup:** Delete only the dedicated namespace and cluster resources you created, after confirming they contain no unrelated data:

```bash
kubectl config current-context
kubectl get pods -n disruption-lab -o wide
# CLEANUP — only if this namespace was created exclusively for this lab:
kubectl delete namespace disruption-lab --wait=true
kubectl get namespace disruption-lab
```

Keep the cluster for later labs. Delete the cluster only if you created it for this lesson and have verified the name/context and that no needed work remains:

```bash
kind get clusters
# CLEANUP — destructive to the named local cluster:
kind delete cluster --name pdb-lab
kind get clusters
```

**Cleanup verification:** Namespace should be absent if deleted; if cluster was deleted, verify it no longer appears. **Stretch challenge:** Repeat baseline measurements from two terminals and compare observed failures and latency; explain why this still does not prove production SLO behavior.

#### Lab 2 — Drain under load: no PDB versus a matching PDB

**Goal:** Compare a voluntary drain with and without a PDB and measure what actually happens. **Estimated time:** 60–90 minutes.

**Prerequisites:** Lab 1 cluster/workload, at least one worker node, an HTTP image and request sampler. Use a dedicated worker node, never the control-plane node.

**Baseline and safety checks:**

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get pods -n disruption-lab -o wide
kubectl get deploy,svc -n disruption-lab
kubectl get pdb -n disruption-lab
```

Identify a worker that hosts at least one `baseline-api` Pod and record the exact node name. Confirm other worker nodes have capacity to run replacements. If no replacement capacity is feasible, stop before the drain.

**Phase A: no PDB.** Ensure no PDB selects `app=baseline-api`. Keep the request sampler running and record baseline. Cordon and drain the selected worker only after reviewing current help and confirming the target:

```bash
kubectl drain --help
kubectl config current-context
kubectl get nodes -o wide
# MUTATING — use only the verified worker name and approved, version-checked options.
kubectl cordon <verified-worker-node>
kubectl drain <verified-worker-node> --timeout=60s
```

The exact drain command may need version-verified options for DaemonSets or other Pods. Do not use `--ignore-daemonsets`, `--delete-emptydir-data`, or any PDB-bypass option without understanding the consequences and verifying current support. If the command stops because of a known Pod type, diagnose and adapt only after reviewing the official docs. If it times out, stop and collect evidence rather than retrying indefinitely.

**Phase B: matching PDB.** Restore the node to a safe schedulable state only when appropriate, wait for the workload to return to baseline, and apply a PDB matching the Pod label. The following assumes the workload has three replicas and all three are healthy:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: baseline-api-pdb
  namespace: disruption-lab
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: baseline-api
```

Apply after context checks, then observe the live status:

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl apply -f <reviewed-pdb-manifest>
kubectl get pdb -n disruption-lab
kubectl describe pdb -n disruption-lab baseline-api-pdb
```

Choose a worker hosting a selected Pod, confirm capacity again, run the same request sampler, and repeat the bounded drain procedure. If the node remains cordoned from Phase A, decide whether it should be uncordoned before the next comparison; do not assume the environment is in a clean baseline state.

**Evidence table:** Fill this from actual observations.

| Measurement | No PDB | Matching PDB |
|---|---|---|
| Selected worker | Record | Record |
| Healthy replicas before | Record | Record |
| PDB `disruptionsAllowed` | N/A | Record |
| Drain start/end/duration | Record | Record |
| Request total/success/failure | Record | Record |
| Pending replacement Pods | Record | Record |
| Ready replicas during/after | Record | Record |
| Events and relevant timestamps | Record | Record |
| Interpretation / caveats | Record | Record |

**Expected interpretation:** A PDB can block or limit supported voluntary eviction when its budget would be violated. It does not promise zero request failures. Results depend on the HTTP server, request duration, routing, endpoint propagation, Pod placement, capacity, and kind environment.

**Abort and recovery:** If the drain exceeds the planned timeout or service health degrades beyond your test stop condition, stop the test and inspect PDB status, Pod readiness, node state, events, and Pending replacements. Do not bypass the PDB to finish the exercise. If a worker remains cordoned, uncordon it only after verifying it is healthy and the lab owner decides to restore it:

```bash
kubectl config current-context
kubectl get nodes -o wide
# MUTATING recovery — only for the verified lab worker when safe:
kubectl uncordon <verified-worker-node>
kubectl get nodes -o wide
```

**Cleanup:** Delete only the lab PDB and workload resources you created, or delete the dedicated namespace after confirming scope. Verify the namespace/resource absence. Do not delete the cluster if you intend to continue to Lab 3 or 4.

**Troubleshooting:** If the PDB selector matches no Pods, compare `kubectl get pods --show-labels` with the PDB selector. If drain blocks, inspect the exact selected Pods and status. If replacements are Pending, inspect Pod events and scheduling constraints.

**Stretch challenge:** Repeat with `maxUnavailable: 1` and compare status. Explain why a single run is not sufficient to conclude zero downtime.

#### Lab 3 — Deliberately blocking PDB and diagnosis

**Goal:** Reproduce a blocked eviction safely, diagnose it, correct the local-only configuration, and restore node schedulability. **Estimated time:** 45–75 minutes.

**Prerequisites:** Disposable kind cluster and a dedicated namespace. This lab uses a workload with three replicas and a PDB requiring all three healthy replicas.

**Manifest:**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: pdb-blocked-lab
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blocked-demo
  namespace: pdb-blocked-lab
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: blocked-demo
  template:
    metadata:
      labels:
        app.kubernetes.io/name: blocked-demo
    spec:
      containers:
        - name: web
          image: <REPLACE_WITH_VERIFIED_HTTP_IMAGE>
          ports:
            - containerPort: 8080
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: blocked-demo-pdb
  namespace: pdb-blocked-lab
  labels:
    lesson.example.com/purpose: intentionally-blocking-local-lab
spec:
  minAvailable: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: blocked-demo
```

The image placeholder must be replaced with a compatible image; the example does not assume an external registry is available.

**Setup and preflight:**

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl apply -f <reviewed-blocked-lab-manifest>
kubectl rollout status deployment/blocked-demo -n pdb-blocked-lab --timeout=120s
kubectl get pods -n pdb-blocked-lab -o wide --show-labels
kubectl get pdb -n pdb-blocked-lab
kubectl describe pdb -n pdb-blocked-lab blocked-demo-pdb
```

If the replicas are not healthy, fix the lab setup or stop; do not treat an unhealthy baseline as a clean PDB demonstration.

**Bounded drain attempt:** Identify a worker containing a `blocked-demo` Pod, never the control-plane node. Confirm the worker and current context immediately before the mutation. Run current help and use a bounded timeout:

```bash
kubectl drain --help
kubectl config current-context
kubectl get nodes -o wide
# MUTATING; expected to block or time out because the PDB is intentionally restrictive.
kubectl drain <verified-worker-node> --timeout=30s
```

This is an expected test condition, not a claim that the command was executed by the author. Your exact output may differ. If the command times out, collect PDB status, Pod readiness, events, and node state. Do not use a bypass option.

**Diagnosis:** Explain why `minAvailable: 3` with three healthy replicas may permit zero disruptions. Confirm actual `disruptionsAllowed` from status. Distinguish the observation “the budget currently permits zero” from the decision “we are approved to change the policy.”

**Safe correction:** In this disposable lab only, change the PDB to `minAvailable: 2`, after confirming context and namespace. For example, edit the reviewed manifest and re-apply it. Then verify PDB status and workload health. If the node remains cordoned, determine whether it is safe to uncordon or to retry the bounded drain with the corrected budget. Never leave the lab node cordoned by accident.

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get pdb -n pdb-blocked-lab
kubectl describe pdb -n pdb-blocked-lab blocked-demo-pdb
# MUTATING only in the disposable lab, after editing the PDB to minAvailable: 2:
kubectl apply -f <corrected-pdb-manifest>
kubectl get pdb -n pdb-blocked-lab
kubectl get pods -n pdb-blocked-lab -o wide
```

**Evidence:** Initial and corrected PDB status, selected Pod labels, drain start/end and exit status, node schedulability, events, and post-correction replica readiness.

**Cleanup:** Verify context and namespace, then delete only `pdb-blocked-lab` if it was created for this exercise:

```bash
kubectl config current-context
kubectl get pods -n pdb-blocked-lab -o wide
# CLEANUP — namespace must be dedicated to this lab:
kubectl delete namespace pdb-blocked-lab --wait=true
kubectl get namespace pdb-blocked-lab
```

If a worker remains cordoned, inspect node status and uncordon only after the node is safe. **Cleanup verification:** no namespace remains, and any node you intend to keep is in the intended schedulability state.

**Troubleshooting:** If the drain fails for a reason other than PDB allowance, record that reason; do not claim the lab demonstrated a PDB block unless the evidence supports it. If replacement Pods cannot schedule, fix capacity/constraints or terminate the lab after collecting evidence.

**Stretch challenge:** Change the selector to a label that matches no Pods, inspect the mismatch, and then restore the exact selector. Do not leave the misconfigured PDB in a shared environment.

#### Lab 4 — SIGTERM and graceful shutdown with an in-flight request

**Goal:** Observe an in-flight request while a Pod terminates, correlate logs and request outcomes, and compare normal shutdown with a separately isolated forced-timeout case. **Estimated time:** 90–150 minutes.

**Prerequisites:** Disposable kind cluster, Python 3, a way to build a local image and load it into kind (M01), and basic Pod/log inspection. This lab includes application code but does not claim it has been executed.

**Application design:** Build a small HTTP service that tracks active requests, exposes readiness, logs timestamps, stops admitting new work on termination, waits a bounded interval for in-flight requests, and exits. Because framework/server lifecycle APIs vary, this lab's safest reproducible route is to implement a standard-library HTTP server and test it on the local platform before packaging it. The exact behavior of `http.server` under threaded requests and signals must be tested in your Python version; do not assume the code below is a production server.

Illustrative server skeleton:

```python
# graceful_server.py — teaching skeleton; validate on your Python version.
import json
import logging
import signal
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
stopping = threading.Event()
active_lock = threading.Lock()
active_requests = 0

class Server(ThreadingHTTPServer):
    daemon_threads = False
    block_on_close = True

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global active_requests
        if self.path == "/ready":
            self.send_response(503 if stopping.is_set() else 200)
            self.end_headers()
            self.wfile.write(b"stopping" if stopping.is_set() else b"ready")
            return
        with active_lock:
            active_requests += 1
            current = active_requests
        logging.info("request_started path=%s active=%d", self.path, current)
        try:
            # Deliberately long request for the lab; keep bounded.
            time.sleep(8)
            body = json.dumps({"ok": True, "completed": True}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            logging.info("request_completed")
        except (BrokenPipeError, ConnectionResetError):
            logging.warning("client_disconnected")
        finally:
            with active_lock:
                active_requests -= 1
                logging.info("request_finished active=%d", active_requests)

    def log_message(self, fmt, *args):
        logging.info("http_access " + fmt, *args)

def handle_signal(signum, frame):
    logging.info("shutdown_signal_received signal=%s", signum)
    stopping.set()

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

server = Server(("0.0.0.0", 8080), Handler)
server.timeout = 0.5
logging.info("server_started port=8080")
try:
    while not stopping.is_set():
        server.handle_request()
finally:
    logging.info("stop_accepting_new_work=true active=%d", active_requests)
    server.server_close()
    logging.info("server_closed active=%d", active_requests)
```

**Important limitation:** This skeleton demonstrates signal/readiness ideas but is not a fully verified graceful HTTP server. A handler may be active in a separate thread while `server_close()` waits according to implementation details; the signal handler, `handle_request()` loop, and threaded server semantics must be validated for the installed Python version. It also does not implement an explicit deadline-driven wait loop for active requests. For a production-quality exercise, add explicit in-flight tracking and a bounded shutdown coordinator, or use a verified ASGI lifecycle implementation whose exact APIs match the installed version. Do not deploy this skeleton as a production server.

For a verified ASGI implementation, follow the installed FastAPI/Uvicorn versions' official lifespan and graceful-shutdown documentation. Record the versions and configure the server's graceful timeout and Kubernetes `terminationGracePeriodSeconds` coherently. `[VERIFY]`

**Pod setup:** Package the application into a local image using M01 practices, load it into kind, and apply a dedicated Deployment in `graceful-lab` with a termination grace period chosen from measured request and shutdown durations. Use a readiness endpoint only if the application implements it correctly. The manifest must reference the actual local image name and use a pull policy compatible with that image's availability in kind.

**Test sequence:**
1. Confirm context, node topology, namespace, and image availability.
2. Start the Pod and verify readiness.
3. Start a request that takes approximately eight seconds; record client start time.
4. While the request is active, terminate the Pod through the supported local test path.
5. Capture client result, application logs, Pod status/events, readiness and endpoint observations.
6. Repeat in a separate disposable workload with a grace period intentionally shorter than the request duration. This is the forced-timeout test; keep it isolated and do not use production data.
7. Repeat enough times to identify variability, not just one lucky outcome.

**Evidence commands (read-only):**

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl get pods -n graceful-lab -o wide
kubectl logs -n graceful-lab <pod-name> --timestamps
kubectl describe pod -n graceful-lab <pod-name>
kubectl get events -n graceful-lab --sort-by=.lastTimestamp
```

**Result table:** Fill actual results after testing.

| Scenario | Expected signal/phase | Request outcome | Exit behavior | Evidence | Caveats |
|---|---|---|---|---|---|
| Normal grace budget | Signal observed; new work stops; active request drains | Record actual result | Expected clean exit if implementation works | Logs, client timestamps, Pod status | Depends on server implementation and runtime |
| Grace budget too short | Signal observed; work may not finish before deadline | Record actual result | Forced termination may occur | Events, logs, client error/result | Separate disposable workload only |
| Endpoint/readiness overlap | Readiness/endpoint state changes while request path is active | Record actual result | Not the primary pass criterion | Endpoint observations and client outcomes | kind does not reproduce all production data planes |

**Pass criteria:** The test has correlated timestamps, a known in-flight request, a declared shutdown contract, a measured normal exit before the grace deadline, and a separately observed timeout behavior. If the skeleton does not behave as expected, treat that as a finding and improve the implementation rather than fabricating a pass.

**Cleanup:** After confirming context and scope, delete only the dedicated `graceful-lab` namespace and verify its absence. Keep any local source/image only if needed for the learner's own work; this lesson does not create separate files automatically.

**Troubleshooting:** If termination signal logs are absent, verify command form, PID 1/process tree, runtime behavior, and logs. If the client sees a disconnect, correlate it with shutdown and endpoint timestamps. If readiness never changes, verify the endpoint implementation and probe configuration.

**Stretch challenge:** Implement a bounded drain coordinator with a monotonic deadline, active-request counter, explicit stop-admission state, and a test that proves no normal-path forced kill occurs in repeated runs.

#### Optional Lab 5 — Worker checkpoint and maintenance runbook tabletop

**Goal:** Practice the decision to proceed, pause, or escalate for a queue worker or ETL job. **Estimated time:** 45–60 minutes.

**Scenario:** A worker processes batches of records. It receives a termination signal during batch 12. The output commit may succeed while the queue acknowledgement fails, causing batch 12 to be delivered again.

**Exercise:**
1. Define a durable checkpoint: last fully committed batch ID and output manifest.
2. Define acknowledgement order: commit durable output first, then acknowledge the message.
3. Define idempotency: repeated batch ID maps to the same intended output rather than duplicating side effects.
4. Define poison-message behavior and maximum retries.
5. Set a bounded shutdown deadline and decide whether to finish, checkpoint, or release the in-flight unit.
6. Write a short node maintenance runbook with owners, preflight evidence, SLI, pause/abort criteria, and recovery verification.
7. Produce a decision record: proceed, pause, or escalate, with evidence and residual risk.

**Evidence:** checkpoint position, in-flight item identity, duplicate-handling policy, retry/ack sequence, and completed tabletop runbook. Use synthetic identifiers only; do not include secrets or real payloads.

**Cleanup:** No cluster changes are required. If you created test resources, verify scope and remove only those resources. **Stretch challenge:** Add a failure injection at each boundary—before commit, after commit/before ack, and after ack—and explain the recovery outcome.

## Troubleshooting decision table

| Symptom | Likely causes | Evidence to collect | Safe next action | Escalation / stop condition |
|---|---|---|---|---|
| Drain remains blocked by PDB | `disruptionsAllowed` is zero; selected Pod unready; budget too restrictive | `get/describe pdb`, selected Pod readiness, events | Pause and diagnose health, selectors, replicas, capacity | Escalate if maintenance deadline conflicts with service safety |
| PDB selects no Pods | Selector mismatch or label drift | PDB selector and `get pods --show-labels` | Correct the selector after review; test in staging | Stop if intended workload coverage is unknown |
| PDB selects too many Pods | Shared/overbroad label | Actual selected Pod list and owners | Narrow selector and review ownership | Stop if unrelated services are in the same budget |
| Replacement Pod stays Pending | No capacity, taints, affinity, quota, topology or storage constraints | Pod events, node allocatable/requests, quota and placement config | Restore capacity or resolve constraints; retry only after evidence | Stop if SLO or quorum margin is threatened |
| `disruptionsAllowed` is positive but drain fails | Status changed; concurrent disruption; other drain constraint | Fresh PDB status, events, node Pod inventory | Re-read live state; inspect exact blocker | Escalate if repeated failures exceed maintenance window |
| Single-replica workload blocks maintenance | No redundancy or strict budget | Replica count, PDB, service owner plan | Schedule outage or add redundancy; obtain explicit approval | Do not bypass silently |
| StatefulSet/database at risk | Quorum, leader, replication lag, ordered maintenance | Database-specific health and maintenance checks | Follow application/database runbook one member at a time as required | Stop on loss of quorum margin or unknown data risk |
| DaemonSet prevents drain completion | DaemonSet Pods require documented handling | Pod owner and current drain help | Use only verified, justified options | Stop if system agent impact is unclear |
| Local data warning | `emptyDir`/node-local state or local storage dependency | Pod spec, owner, data recovery plan | Determine whether data can be lost/rebuilt; approve explicitly | Stop if data-loss implications are unknown |
| Requests fail during termination | Shutdown race, endpoint propagation, long-lived connections, abrupt close | Client timestamps, app logs, readiness/endpoint observations | Improve bounded drain and retry-safe client behavior | Stop if SLI breaches agreed guardrail |
| Process is killed before completing work | Grace period too short, signal not handled, work unbounded | Logs, exit status, Pod events, process command | Fix signal delivery, bound work, checkpoint, measure grace | Stop rollout if durable work can be lost |
| `preStop` sleep delays exit | Hook consumes grace budget; race remains | Hook duration and termination timestamps | Replace arbitrary sleep with measured lifecycle coordination | Escalate if hook can exceed deadline |
| Queue duplicates appear | Ack/commit ordering, at-least-once delivery, missing idempotency | Message IDs, checkpoint, transaction and ack logs | Make side effects idempotent and repair recovery protocol | Stop if duplicates create non-reversible side effects |
| PDB blocks urgent patch | Availability safeguards conflict with security deadline | Vulnerability/maintenance deadline, PDB and SLI evidence | Escalate for documented risk acceptance and narrow mitigation | No override without authorized decision |
| Node remains cordoned after test | Drain aborted or cleanup incomplete | Node schedulability and lab state | Uncordon only after node health/scope verification | Stop if node identity or environment is uncertain |

## Production readiness checklist

Use this checklist before a real maintenance event. Each checkbox must be supported by evidence, not merely by a verbal assertion.

- [ ] Current context and target node recorded (`kubectl config current-context`, `kubectl get nodes -o wide`).
- [ ] Every Pod on the target node has an identified owner and workload type (`kubectl get pods -A -o wide`; inspect owners).
- [ ] PDB inventory captured and selectors verified against actual Pod labels (`kubectl get pdb -A`, `kubectl describe pdb`, `--show-labels`).
- [ ] Current healthy replica count and `disruptionsAllowed` recorded immediately before maintenance.
- [ ] Single-replica and quorum-sensitive workloads have an approved plan.
- [ ] DaemonSet, Job/CronJob, unmanaged Pod, local-data, and local-storage implications reviewed.
- [ ] Replacement scheduling feasibility checked for resource requests, quota, taints, affinity, topology and storage.
- [ ] Spare capacity is sufficient after accounting for the target node's loss and normal workload headroom.
- [ ] Application shutdown has a test record for in-flight work, signal handling, checkpointing, and deadline behavior.
- [ ] `terminationGracePeriodSeconds` is justified by measured shutdown time and recovery design.
- [ ] `preStop` hook behavior, if any, is measured and does not consume the entire grace budget.
- [ ] Readiness and endpoint transition behavior has been tested; no instantaneous propagation assumption is used.
- [ ] Baseline SLI/SLO and explicit stop/abort thresholds are recorded.
- [ ] Change owner, service owner, approval, escalation contact, and maintenance window are documented.
- [ ] Current `kubectl drain --help` and official docs were checked for version-sensitive flags.
- [ ] Drain timeout and escalation strategy are defined.
- [ ] No routine PDB-bypass or force-delete path is embedded in the runbook.
- [ ] Post-drain validation covers Pod readiness, service SLI, queue lag, events/logs, and node health.
- [ ] Uncordon criteria are explicit and the node is not re-enabled until healthy.
- [ ] Evidence includes timestamps, actual output, decisions, exceptions, and post-change follow-up.
- [ ] Any local rehearsal limitations (kind/WSL2/data-plane/provider differences) are documented.

## SRE and security lens

### Availability and error budget

A PDB is a control over a class of voluntary disruptions, not the service SLO itself. The API's successful-request SLI, error rate, latency, and worker lag should be monitored through the maintenance window. Define acceptable degradation from the actual service SLO and error-budget policy; do not use a universal threshold invented for this lesson.

The drain should pause if the service's declared guardrail is breached, replacement capacity disappears, queue lag grows beyond its agreed bound, or a quorum-sensitive application loses required safety margin. The exact threshold and evaluation window are service-specific.

### Blast radius and resilience

Risk depends on the number of replicas, their placement, the failure domains they share, application-level replication, and whether the service can recover from interrupted work. Three replicas on one node do not protect against that node's failure. A PDB does not provide application quorum, queue durability, checkpointing, backups, or idempotency.

### Least privilege and change control

Node drains and evictions can affect many teams. Give operators only the permissions required for their approved maintenance scope. Use change approvals, separate read-only diagnosis from mutating operations, and record the identity of the operator and approver. Do not use cluster-admin as the default operational identity.

### Audit evidence

Retain:
- approved change record and target node;
- context and workload inventory;
- PDB status before/during/after;
- baseline and maintenance-window SLI;
- drain start/end timestamps and actual duration;
- relevant Pod events, application logs and request/queue outcomes;
- any override, its approver, rationale, scope and expiry;
- post-maintenance verification and follow-up owners.

### Incident fragment

**Alert/symptom:** drain blocked or service SLI worsens.  
**Triage:** pause mutations; verify context/node; inspect PDB, readiness, events, owners, scheduling and capacity.  
**Mitigation:** restore health/capacity or follow the approved maintenance risk decision; do not bypass safeguards reflexively.  
**Recovery validation:** confirm replacements ready, SLI back within its guardrail, node state correct, and no unexplained Pending Pods.  
**Follow-up:** update PDB/workload design, capacity assumptions, shutdown tests, maintenance policy, and owner escalation documentation.

## Self-check questions

### 1. Does a PDB prevent a worker node from failing?

**Answer:** No. A PDB is primarily a guardrail for supported voluntary eviction. Involuntary failure can still remove multiple Pods.  
**Tempting wrong answer:** “The budget says two replicas must remain, so Kubernetes guarantees two survive.” This confuses voluntary-eviction policy with failure prevention.

### 2. What is the difference between cordon and drain?

**Answer:** Cordon prevents ordinary new scheduling to a node; drain attempts to evict eligible existing Pods under its documented rules.  
**Tempting wrong answer:** “Cordon moves Pods.” It does not evict existing Pods.

### 3. Why is `disruptionsAllowed: 1` not a guarantee that drain will succeed?

**Answer:** It is a status snapshot. Health may change, concurrent disruptions may consume allowance, and replacement Pods may not schedule. Other Pod types and drain constraints may also block progress.  
**Tempting wrong answer:** “One means exactly one Pod is guaranteed to be replaced.” The status does not reserve capacity or guarantee recovery.

### 4. Why must a PDB selector be checked against Pod labels?

**Answer:** A PDB selects Pods by labels, not by its own name or an assumed Deployment owner. A mismatch can leave the intended workload unprotected; an overbroad selector can combine unrelated workloads.  
**Tempting wrong answer:** “Naming the PDB after the Deployment links them automatically.”

### 5. Why can a PDB block maintenance for a single-replica service?

**Answer:** If the budget permits no voluntary disruption, evicting the only healthy Pod would violate the budget. The correct response may be to add redundancy or plan an approved outage.  
**Tempting wrong answer:** “Set a more permissive PDB and downtime disappears.” A budget cannot create another replica.

### 6. Why is a long `preStop: sleep` not a complete graceful-shutdown strategy?

**Answer:** It consumes the termination grace period and does not guarantee endpoint convergence or correct in-flight request handling. It may delay useful work without removing races.  
**Tempting wrong answer:** “Wait long enough and every load balancer has updated.” Propagation is not a global atomic event.

### 7. What should a queue worker do before acknowledging a message?

**Answer:** Ensure the required side effect is durable, then acknowledge according to the queue's contract; make retries and duplicate delivery safe through idempotency or deduplication.  
**Tempting wrong answer:** “Acknowledge first to avoid redelivery.” That can lose work if the process dies before durable success.

### 8. Why can a drain remain blocked even when a PDB is configured sensibly?

**Answer:** A selected Pod may be unready, the allowance may be zero at the current moment, or replacements may not schedule due to capacity, affinity, taints, quota, topology or storage.  
**Tempting wrong answer:** “Any blocked drain proves the PDB is too strict.” The budget may be exposing a real capacity or health problem.

### 9. What evidence should support a decision to proceed with maintenance?

**Answer:** Verified context/target, Pod owners, PDB selector/status, healthy replicas, replacement capacity, shutdown-test evidence, SLI baseline and stop criteria, owner approval, and a recovery plan.  
**Tempting wrong answer:** “A green node status and one allowed disruption are enough.” Those facts do not establish service-level safety.

### 10. When may an operator override a PDB safeguard?

**Answer:** Only through an authorized, documented risk decision when the trade-off justifies it, with narrow scope, evidence, owner approval, monitoring, recovery validation and follow-up.  
**Tempting wrong answer:** “Whenever drain is stuck.” A blocked drain is a diagnostic signal, not automatic authorization to bypass.

## Senior interview and design-review questions

### 1. A three-replica API has `minAvailable: 2`. Why might a drain still violate its SLO?

**Expected answer points:** readiness may be inaccurate; replicas may share a failure domain; replacement scheduling can fail; existing connections may be cut; shutdown may exceed grace; endpoints/data plane converge asynchronously; the SLO is request-level, not Pod-count-only; capacity and test evidence are needed.

### 2. A node drain has been blocked for two hours, and a critical security patch is overdue. What do you do?

**Expected answer points:** pause repeated mutations; verify context and node; capture PDB/Pod/owner/events/capacity/SLI evidence; identify root cause; involve service/security/platform owners; compare security risk of delay with availability/data risk; seek explicit risk acceptance if an override is necessary; use the narrowest supported action; monitor and document recovery. Do not default to force deletion.

### 3. Design shutdown behavior for a queue consumer processing long ETL batches.

**Expected answer points:** stop polling/claiming new messages; track in-flight work; define bounded completion/checkpoint deadline; commit durable output before acknowledgement; make duplicate work idempotent; release or retry unfinished work; handle poison messages; log timestamps and checkpoint IDs; test normal and forced termination; size grace period from measurements.

### 4. How should a platform team define and enforce PDB policy across hundreds of teams?

**Expected answer points:** classify workload types; require owner and availability intent; validate exact selectors and risky zero-disruption budgets; handle single replicas, Jobs, operators and quorum-sensitive apps as reviewed exceptions; test policy in audit mode; avoid unverified policy syntax; define exception expiry, change approval, runtime preflight, and a clear escalation process.

### 5. How would you prove that a node can be drained without violating the service SLO?

**Expected answer points:** declare assumptions and unknowns; capture PDB status and healthy replicas; calculate feasible capacity after node loss; verify topology and controller interactions; run representative shutdown and load tests; compare baseline and rehearsal SLI; define stop/abort criteria; coordinate owners; validate recovery and preserve evidence. A positive PDB allowance alone is insufficient.

## Evidence artifacts and exit criteria

Retain the following as notes or evidence in your own learning repository; this lesson does not create separate evidence files.

- Cluster name, node image tag, Kubernetes/kubectl/kind versions, and context.
- Baseline Pod placement, labels, owner references, readiness, events and service request sample.
- PDB manifest and before/during/after status, including `currentHealthy`, `desiredHealthy`, `disruptionsAllowed`, and `expectedPods` where exposed.
- Drain timeline: start, first eviction, replacement scheduling, readiness recovery, completion, and any timeout.
- Actual request counts, errors, latency observations, queue lag/checkpoint position where applicable.
- Application shutdown logs and client outcome for in-flight work.
- Diagnostic decision record for a deliberately blocked drain and its safe correction.
- Maintenance runbook with proceed/pause/abort/escalate gates.
- SLI/SLO baseline, stop criteria, approval record, exceptions and post-change review.
- Explicit list of what the local simulation does not validate.

**Exit criteria:** The learner can explain the distinction between disruption policy and application resilience; produce a matching PDB; diagnose a blocked drain without reflexively bypassing it; show actual evidence from at least four local labs; explain shutdown and retry safety; and defend a maintenance decision using capacity, health, and SLI/SLO evidence.

## Sources and claim register

### Authoritative sources to consult

The authoring environment did not perform live browsing or verify current page contents. The URLs below are official documentation entry points to consult before applying version-sensitive behavior. Treat all version-dependent details as `[VERIFY]` until checked against the target cluster and installed CLI.

| Source title | Organization | URL | Topics to verify |
|---|---|---|---|
| Disruptions | Kubernetes | https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | Voluntary/involuntary disruptions, PDB purpose and limitations |
| Safely Drain a Node | Kubernetes | https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/ | Drain/cordon behavior, options, PDB interaction |
| Pod Lifecycle | Kubernetes | https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/ | Termination, grace period, lifecycle sequencing |
| Container Lifecycle Hooks | Kubernetes | https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/ | `preStop` timing and termination budget |
| Configure Liveness, Readiness and Startup Probes | Kubernetes | https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ | Readiness behavior and probe configuration |
| PodDisruptionBudget API reference | Kubernetes | https://kubernetes.io/docs/reference/kubernetes-api/policy/pod-disruption-budget-v1/ | `policy/v1` fields and status |
| Deployments | Kubernetes | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ | Rolling update interaction |
| StatefulSets | Kubernetes | https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | Identity, ordering and controller behavior |
| Python `signal` module | Python | https://docs.python.org/3/library/signal.html | Signal delivery and handler constraints |
| Python `http.server` | Python | https://docs.python.org/3/library/http.server.html | Teaching server API behavior; not a production server recommendation |
| FastAPI lifespan events | FastAPI | https://fastapi.tiangolo.com/advanced/events/ | Framework lifecycle API if used |
| Uvicorn settings | Uvicorn | https://www.uvicorn.org/settings/ | Graceful-shutdown settings and version-specific behavior |
| kind quick start | kind | https://kind.sigs.k8s.io/docs/user/quick-start/ | Cluster config and local setup |
| Kubernetes version-skew policy | Kubernetes | https://kubernetes.io/releases/version-skew-policy/ | Supported client/server version combinations |

### Claim register

**Status note:** Since no live documentation or cluster verification was performed during authoring, source URLs are provided as official verification targets rather than claims that the pages were checked today. Material details marked `[VERIFY]` must be confirmed against the actual Kubernetes, `kubectl`, runtime, Python, and server versions in use.

| Claim ID | Claim or behavior being asserted | Authoritative source and URL | Version-sensitive? | Verification status | Notes or scope limitation |
|---|---|---|---|---|---|
| C01 | Voluntary and involuntary disruptions are distinct categories | Kubernetes Disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | No, concepts stable; confirm wording | [VERIFY] | PDBs do not prevent node failure |
| C02 | PDBs primarily constrain supported voluntary eviction paths | Kubernetes Disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | Yes, API/path details | [VERIFY] | Do not generalize to every deletion path |
| C03 | PDBs do not create replicas or capacity | Kubernetes Disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | No, conceptual | [VERIFY] | Workload controllers and scheduler have separate roles |
| C04 | `minAvailable` expresses minimum healthy selected Pods | PDB API: https://kubernetes.io/docs/reference/kubernetes-api/policy/pod-disruption-budget-v1/ | API semantics | [VERIFY] | Check exact installed API docs |
| C05 | `maxUnavailable` expresses maximum unavailable selected Pods | PDB API: https://kubernetes.io/docs/reference/kubernetes-api/policy/pod-disruption-budget-v1/ | API semantics | [VERIFY] | Do not set both alternatives together |
| C06 | Percentage values have rounding semantics | Kubernetes Disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | Yes | [VERIFY] | Verify current rounding behavior, especially small sets |
| C07 | PDB status includes health and disruption-allowance fields | PDB API: https://kubernetes.io/docs/reference/kubernetes-api/policy/pod-disruption-budget-v1/ | Field availability/version | [VERIFY] | `expectedPods` may not be surfaced identically in all views |
| C08 | PDB selector matches Pod labels, not Deployment name automatically | PDB API: https://kubernetes.io/docs/reference/kubernetes-api/policy/pod-disruption-budget-v1/ | No, selector model | [VERIFY] | Validate live selected Pods |
| C09 | `disruptionsAllowed` is a current status observation, not capacity reservation | Kubernetes Disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | Status timing | [VERIFY] | Re-check before decision points |
| C10 | Unhealthy Pod eviction behavior has version-specific details | Kubernetes Disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | Yes | [VERIFY] | Verify supported fields and feature requirements |
| C11 | Drain cordons the node and evicts eligible Pods under documented rules | Safely Drain a Node: https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/ | Yes, flags and paths | [VERIFY] | Check installed `kubectl drain --help` |
| C12 | Eviction API and direct Pod deletion do not have identical PDB behavior | Kubernetes Disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | Yes | [VERIFY] | Verify exact current API behavior |
| C13 | DaemonSet Pods require special consideration during drain | Safely Drain a Node: https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/ | Yes, flags | [VERIFY] | Never add a flag without understanding consequences |
| C14 | Local-storage drain options may permit loss of local data | Safely Drain a Node: https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/ | Yes, flags | [VERIFY] | Determine actual data dependencies first |
| C15 | Pod termination includes a bounded grace period | Pod Lifecycle: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/ | Runtime/version nuances | [VERIFY] | Exact sequencing must be checked |
| C16 | `preStop` hook execution interacts with the termination grace budget | Container Lifecycle Hooks: https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/ | Yes, details | [VERIFY] | Verify exact timing and edge cases |
| C17 | Container processes may receive a termination signal during shutdown | Pod Lifecycle: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/ | Runtime nuances | [VERIFY] | Do not assume every process handles it |
| C18 | Shell wrappers can affect signal forwarding and PID 1 behavior | Python signal docs: https://docs.python.org/3/library/signal.html ; Kubernetes Pod Lifecycle: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/ | Environment-dependent | [VERIFY] | Test the actual image entrypoint/process tree |
| C19 | Readiness does not imply globally instantaneous endpoint/data-plane convergence | Kubernetes readiness probes: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ | Implementation-dependent | [VERIFY] | Avoid exact global ordering claims |
| C20 | FastAPI lifecycle APIs and Uvicorn shutdown settings must match installed versions | FastAPI: https://fastapi.tiangolo.com/advanced/events/ ; Uvicorn: https://www.uvicorn.org/settings/ | Yes | [VERIFY] | No specific defaults asserted here |
| C21 | Deployment rolling-update settings and PDBs are separate controls | Deployments: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ ; Disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | Interaction-dependent | [VERIFY] | Do not treat them as a single availability guarantee |
| C22 | StatefulSet identity/order does not prove database quorum safety | StatefulSets: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/ | Workload-specific | [VERIFY] | Database guidance remains authoritative |
| C23 | HPA changes replica count and may change PDB status | Kubernetes Disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | Runtime-dependent | [VERIFY] | Re-read status at maintenance decision points |
| C24 | Replacement Pods may remain Pending due to capacity or placement constraints | Kubernetes scheduling concepts: https://kubernetes.io/docs/concepts/scheduling-eviction/ | Cluster-dependent | [VERIFY] | Inspect actual Pod events and constraints |
| C25 | Jobs and CronJobs need their own retry/checkpoint/idempotency plan | Jobs: https://kubernetes.io/docs/concepts/workloads/controllers/job/ ; CronJobs: https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/ | Controller details | [VERIFY] | PDB is not an exactly-once processing guarantee |
| C26 | Topology spread and anti-affinity affect replacement feasibility and resilience | Kubernetes topology spread: https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ | Cluster-dependent | [VERIFY] | Full placement design is deferred to Unit 7 |
| C27 | Long-lived connections can outlive routing changes | Kubernetes readiness docs: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ | Data-plane-dependent | [VERIFY] | Validate real clients, ingress and data plane |
| C28 | kind is a local cluster tool and does not reproduce all provider failure behavior | kind quick start: https://kind.sigs.k8s.io/docs/user/quick-start/ | Version/tool-dependent | [VERIFY] | Provider, AZ, and load-balancer behavior not simulated |
| C29 | WSL2 kernel/cgroup/resource behavior may differ from production | WSL documentation: https://learn.microsoft.com/windows/wsl/ | Environment-dependent | [VERIFY] | Compare with actual WSL and container-runtime versions |
| C30 | A worker should not acknowledge work before required durable success | Python signal docs do not define queue semantics; use the chosen queue/database's official transaction docs | Application-specific | [VERIFY] | General design principle; exact protocol depends on technology |
| C31 | Idempotency reduces harm from retry and duplicate processing | Application/queue system's official documentation must be selected | Application-specific | [VERIFY] | No universal exactly-once claim |
| C32 | Drain/eviction permissions can have broad operational impact and should be least-privileged | Kubernetes RBAC: https://kubernetes.io/docs/reference/access-authn-authz/rbac/ | Cluster-policy-dependent | [VERIFY] | Full RBAC design is Unit 9 |
| C33 | Policy-as-code checks cannot infer all live capacity and health facts from manifests | Chosen policy engine docs must be consulted | Tool-specific | [VERIFY] | Pseudocode is intentionally not runnable |
| C34 | SLI/SLO thresholds should be service-specific, not universal constants | No universal Kubernetes source; define in the service reliability contract | No universal threshold | [VERIFY] | Organizational decision, not an API default |
| C35 | `kubectl get events --sort-by=.lastTimestamp` behavior/output may vary | kubectl reference: https://kubernetes.io/docs/reference/kubectl/ | Yes | [VERIFY] | Check installed CLI help and available fields |
| C36 | Python `http.server` is a teaching tool, not a production server recommendation | Python `http.server`: https://docs.python.org/3/library/http.server.html | Python-version dependent | [VERIFY] | Lab skeleton requires local validation |
| C37 | Cluster upgrade/version skew must be checked for node-image and client compatibility | Kubernetes version-skew policy: https://kubernetes.io/releases/version-skew-policy/ | Yes | [VERIFY] | Use current supported versions, not a hard-coded “latest” |
| C38 | A PDB can delay maintenance and thereby prolong a security/patching exposure | Kubernetes Disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ | Risk depends on context | [VERIFY] | Requires explicit risk assessment and governance |

## Ten-pass content audit

This audit is a structural/content review of the authored lesson only. No cluster or live source verification was performed. “Pass with limitations” means the teaching content is present while the explicitly identified verification remains outstanding; it does not mean runtime behavior was tested.

| Pass | Audit focus | Checks performed | Status | Findings / corrections |
|---|---|---|---|---|
| 1 | Roadmap alignment | Target filename and Unit 5 scope reflected; adjacent units referenced rather than replaced | Pass with limitations | Repository tree and authoritative syllabus file were not available for independent inspection in this authoring context; target placement follows the supplied prompt |
| 2 | Completeness | L1–L4 concepts, interactions, runbook, four core labs and optional fifth lab included | Pass with limitations | Examples require learner-supplied image and environment-specific verification |
| 3 | Technical correctness | PDB limitations, eviction/deletion distinction, termination, hooks, signals, readiness races discussed with caveats | Pass with limitations | Current official docs were not live-checked; relevant claims marked `[VERIFY]` |
| 4 | Manifest correctness | PDB selectors match labels in examples; deliberately blocking example is isolated and labeled | Pass with limitations | Placeholder images prevent direct application until replaced; learner should run server-side validation |
| 5 | Command correctness and safety | Read-only/mutating/cleanup distinctions, context checks, bounded drain and no default bypass | Pass with limitations | `kubectl drain` flags intentionally require installed-help verification |
| 6 | Application examples | Signal-aware worker pattern and HTTP shutdown skeleton included; limitations disclosed | Pass with limitations | HTTP skeleton is explicitly not a verified production server; learner must test before packaging |
| 7 | Operational depth | Deployment, StatefulSet, HPA, Jobs, CronJobs, DaemonSets, local data, topology, long-lived connections and node replacement addressed | Pass with limitations | Provider-specific node replacement and quorum behavior need workload/provider runbooks |
| 8 | Evidence and observability | SLI, logs, events, request outcomes, timestamps, evidence tables and recovery verification defined | Pass with limitations | No fabricated lab results; learner must fill observed measurements |
| 9 | Source and claim integrity | Official documentation entry points and 38-claim register included | Pass with limitations | URLs are supplied as verification targets, not represented as live-checked sources |
| 10 | Pedagogy and sign-off | Objectives, progressive levels, answer keys, exactly five interview questions, and honest execution status included | Pass with limitations | Labs and commands were documented but not executed by the author |

## Honest sign-off

- **Exact target file:** `Stage 2E — Production DevOps & Platform Engineering/03-Production-Kubernetes-Operations/05-pod-disruption-budgets-and-graceful-shutdown.md` (the standalone artifact is saved as `05-pod-disruption-budgets-and-graceful-shutdown.md`).
- **Coverage:** L1, L2, L3, and L4 are covered, including PDB semantics, graceful shutdown, failure diagnosis, policy, SLOs, governance, and maintenance operations.
- **Labs:** Four core labs and one optional tabletop lab are documented. **Labs are documented but were not executed by the author.**
- **Claim register:** 38 material claims. The claim register marks the claims `[VERIFY]` because live documentation and cluster behavior were not verified in this authoring run.
- **Audit:** Ten content-audit passes are recorded as “Pass with limitations”; no runtime, manifest-server-side, or live-source validation is claimed.
- **Limitations:** The repository tree and authoritative M03 syllabus were not independently inspected in this authoring context. Image names are placeholders. `kubectl` flags, API behavior, Python/server behavior, and provider-specific maintenance semantics must be verified against the actual environment.
- **Repository boundary:** This output is a standalone Markdown artifact. No other repository files were intentionally modified; no repository diff was available to inspect.

