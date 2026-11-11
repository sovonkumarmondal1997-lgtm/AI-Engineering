# Unit 8 — Spot and Preemptible Instances for Data Workloads

**Stage:** Stage 2E — Production DevOps & Platform Engineering  
**Subfolder:** `15-Platform-Capacity-Compute-Economics-and-FinOps/`  
**Module:** M15 — Platform Capacity, Compute Economics and FinOps  
**Target file:** `08-spot-and-preemptible-instances-for-data-workloads.md`  
**Estimated study time:** 32–44 hours (reading and worked examples 8–11 h; hands-on labs 18–25 h; review and design defence 6–8 h)  
**Prerequisites:** Stages 0–2D and Stage 2E M01–M14; especially M03 Unit 5 pod termination/PDBs and Unit 7 placement; M10 Unit 2 freshness SLOs, Unit 6 queues/retry amplification/catch-up, Unit 8 ORR, Unit 9 error-budget policy; M11 observability and load/soak testing; M13 Units 4/8/10 checkpointing, bounded fault injection and game days; M15 Units 1–7 capacity, quotas, HCU economics, allocation, cleanup, trade-offs and release review.  
**Core tools:** Python 3.11+ standard-library syntax `[VERIFY]`, `unittest`, `kind`, `kubectl`, local container runtime used by the existing kind installation, synthetic workload/checkpoint fixtures, JSON/CSV reports.  
**Awareness:** AWS Spot, Google Cloud Spot/Preemptible terminology, Azure Spot terminology `[VERIFY]`; provider node termination handlers `[VERIFY]`; Spark/Flink executor decommissioning and shuffle services `[VERIFY]`; distributed ML checkpoint frameworks `[VERIFY]`; Karpenter/Cluster Autoscaler integration (Unit 9); Prometheus/Grafana/`promtool` from M11.  
**Last reviewed:** 2026-11-03  
**Tool baseline assumed:** Python 3.11+ `[VERIFY]`; kind/Kubernetes/kubectl and Docker or compatible container runtime versions inherited from M03/M11 and must be recorded from the learner's environment; provider-specific APIs, notice semantics, flags, termination handlers and framework integration are `[VERIFY]`.  
**Stack profile required:** Cap+Scale for the full simulation labs. Cap-Core is the reduced planning, economics and policy path when laptop resources are limited.  
**Footprint:** Cap-Core is local Python and synthetic files. Cap+Scale adds a small disposable kind cluster with a control-plane and worker containers; optional observability is started only for Lab 9. Do not assume all components fit on an 8-GB laptop. Record baseline and peak CPU, memory and disk — **measure yours**.  
**Prices used:** hypothetical cost units (HCU) only. No real prices, currency symbols, discounts, interruption rates, provider notice durations or commercial terms are quoted.

> **Completion outcome:** Decide which workloads are safe candidates for interruptible capacity, design checkpoint/resume and idempotent recovery, operate a mixed spot/on-demand pool, run bounded interruption drills, calculate net savings and break-even assumptions, protect SLOs and deadlines, and govern spot eligibility with evidence. You will demonstrate the mechanisms locally without claiming that a local simulation reproduces provider reclaim behavior.

## Contents

- [Prerequisite handoff and scope](#prerequisite-handoff-and-scope)
- [Running example, labels and safety contract](#running-example-labels-and-safety-contract)
- [Unit 8 — Spot and preemptible instances for data workloads](#unit-8--spot-and-preemptible-instances-for-data-workloads)
  - [8.0 Why this matters in production](#80-why-this-matters-in-production)
  - [8.1 Learning objectives](#81-learning-objectives)
  - [8.2 Concept map and vocabulary](#82-concept-map-and-vocabulary)
  - [8.3 Level 1 — Beginner](#83-level-1--beginner)
  - [8.4 Level 2 — Intermediate](#84-level-2--intermediate)
  - [8.5 Level 3 — Advanced](#85-level-3--advanced)
  - [8.6 Level 4 — Expert](#86-level-4--expert)
  - [8.7 SRE lens](#87-sre-lens)
  - [8.8 Security lens](#88-security-lens)
  - [8.9 Production checklist](#89-production-checklist)
  - [8.10 Hands-on lab set](#810-hands-on-lab-set)
  - [8.11 Self-check questions](#811-self-check-questions)
  - [8.12 Evidence artifacts](#812-evidence-artifacts)
  - [8.13 Common interview and design-review questions](#813-common-interview-and-design-review-questions)
  - [8.14 Sources and verification notes](#814-sources-and-verification-notes)

---

## Prerequisite handoff and scope

### Cross-module handoff

M13 Unit 4 taught idempotency, checkpointing, restore/recovery correctness and retry safety; M13 Unit 8 taught bounded fault-injection and recovery-drill safety; M13 Unit 10 taught chaos/game-day design and verification. M03 Unit 5 taught SIGTERM handling, pod termination, drain and PDBs; M03 Unit 7 taught taints, tolerations, affinity, placement and node pools. M10 Unit 2 taught freshness SLOs and stream-versus-micro-batch; M10 Unit 6 taught queues, retry amplification, catch-up and thundering-herd risks; M10 Unit 8 taught ORR; M10 Unit 9 taught error-budget gates and reliability freezes. M11 supplies interruption/queue/saturation observability, dashboards, alerts and `promtool` validation. M15 Units 1–7 supply capacity/headroom, quotas/priorities, spending guardrails, cost allocation, idle cleanup, reliability-aware cost trade-offs and release-review practices.

This unit turns those foundations into a **spot/preemptible operating practice**: workload eligibility, interruption handling, recovery correctness, mixed-pool scheduling, net economics, fallback, security, observability and governance. It does not re-teach Kubernetes scheduling primitives, basic checkpoint theory, general queueing, or the complete node-provisioning/autoscaling implementation.

| Boundary | Reuse or teach here |
|---|---|
| Reuse from M13 Unit 4 | Checkpoint format, idempotency key, restore validation, output equivalence and retry safety |
| Reuse from M13 Units 8/10 | Bounded fault injection, abort conditions, game-day evidence and post-drill review |
| Reuse from M03 Units 5/7 | SIGTERM, `preStop`, termination grace, drain, PDB, taints, tolerations, affinity and node pools |
| Reuse from M10 Units 2/6/8/9 | Freshness/deadline SLOs, queue catch-up, retry control, ORR and error-budget freeze decisions |
| Reuse from M11 | Interruption, checkpoint-age, queue, saturation, latency, alert and dashboard patterns |
| M15 Unit 1/2 | Headroom, N−1 thinking, quotas, priorities, contention and capacity buffers |
| M15 Unit 3/4 | Synthetic rate-card/HCU and owner allocation; net savings are allocated to workloads |
| M15 Unit 6/7 | Reliability-cost trade-offs and release-readiness evidence |
| M15 Unit 9 | Node provisioning and flexible instance selection are implemented later; this unit defines the spot-pool contract |
| M15 Unit 10 | Event-driven scale-out and queue activation are later; this unit defines safe interruptible consumer behavior |
| M15 Unit 12 | GPU scarcity and GPU economics are expanded later; this unit introduces GPU spot risk |
| M16 | Reusable spot-ready golden paths are a forward reference, not a deliverable here |

### Running example

Use one synthetic data/ML platform throughout:

- `inference-api`: customer-facing, latency-sensitive service.
- `batch-etl`: checkpointed, idempotent batch transformation.
- `stream-consumer`: queue-driven consumer with a freshness SLO.
- `training-job`: long-running ML training job with checkpoint and resume.
- `notebooks`: interactive environments, not assumed to be safe spot candidates.
- `metadata-db`: dependency with finite connection and write capacity.
- `platform-services`: control-plane-adjacent services, registry, GitOps and observability.

### Evidence labels and cost contract

- `[ASSUMPTION]` — a model input chosen for a scenario; record why it is plausible and who owns it.
- `[ILLUSTRATIVE]` — an example policy threshold or decision rule, not a universal standard.
- `[SYNTHETIC]` — generated fixture, simulated event or calculated result from the teaching model.
- `[MEASURED — YOUR ENVIRONMENT]` — a value actually measured on your machine or disposable local cluster.
- `[VERIFY]` — provider-, version-, API-, tool- or framework-specific behavior to verify against current official documentation.
- HCU is a comparative teaching unit. It is not currency, a provider rate, a bill or a quote.

### Zero-budget safety contract

1. No cloud account, provider API, real credential, paid service, real billing export, billable cloud resource or real GPU is required or permitted in these labs.
2. All workloads and data are synthetic. All Kubernetes actions target a disposable local `kind` cluster created specifically for this unit.
3. A kind worker is a container that behaves like a Kubernetes node for scheduling demonstrations. It is **not** a cloud spot VM and cannot reproduce provider reclaim, notice, pricing or capacity scarcity.
4. Every fault injector must default to dry-run, have a strict event cap and timeout, validate the expected lab context and worker label, and expose an immediate abort/kill switch.
5. Never automatically delete data-bearing resources. Checkpoint corruption tests operate only on a dedicated synthetic directory.
6. Stop optional observability after Lab 9. Measure your own resource footprint; do not assume an 8-GB laptop can run every component simultaneously.
7. Cleanup must verify that the local cluster and containers created by this unit are stopped/removed. Do not run the cleanup commands against a shared or production context.

### Stack profiles

| Profile | Contents | Use |
|---|---|---|
| **Cap-Core** | Python standard library, JSON/CSV fixtures, simulator, unit tests and worksheets | All planning/economics/policy concepts; reduced path for low-resource machines |
| **Cap+Scale** | Cap-Core plus a disposable kind cluster with one control-plane and two or three worker containers, labels/taints and synthetic workloads | Required full-path profile for Labs 1–4, 8 and 10 |
| **Cap+Obs** | Existing M11 Prometheus/Grafana stack or a minimal local equivalent | Optional extension for Lab 9 only; start after core labs and stop immediately after evidence capture |

Before starting Cap+Scale, record available resources. Example host checks (Linux/WSL2; use your OS equivalent where needed):

```bash
free -h
df -h .
docker version
kind version
kubectl version --client
python --version
```

These commands report your environment; they do not prove a specific footprint is sufficient. If the machine is constrained, complete Cap-Core first and run only one cluster lab at a time.

---

## Unit 8 — Spot and preemptible instances for data workloads

### 8.0 Why this matters in production

Interruptible capacity can lower the direct compute rate, but it can disappear when the provider reclaims spare capacity and may not be available again when the workload needs to resume. A long-running ETL or training job that cannot checkpoint may lose hours of work; a stateful primary on a reclaimable node may threaten correctness or quorum; and a mass interruption can turn retries into a downstream outage. The correct decision is therefore not “spot is cheaper” but “the workload can recover correctly, meet its deadline and SLO, obtain fallback capacity, and still save HCU after waste is counted.”

### 8.1 Learning objectives

By the end of this unit, you can:

1. **[L1]** Explain spot/preemptible capacity, provider variation, reclaim risk and why availability is not guaranteed.
2. **[L1]** Classify stateless, batch, queue, streaming, stateful and ML workloads as eligible, conditional or ineligible with evidence.
3. **[L2]** Configure a local spot-lab pool using labels, taints, tolerations and preferred placement without confusing it with real cloud spot.
4. **[L2]** Build checkpoint/resume behavior with integrity validation, idempotent outputs and a no-checkpoint control.
5. **[L2]** Run bounded interruption drills and measure lost work, resume time, completion-time inflation and correctness.
6. **[L2/L3]** Calculate effective HCU cost, break-even interruption assumptions and a sensitivity range that includes checkpoint, retry and fallback overhead.
7. **[L3]** Design diversified pools, deadline-aware fallback, retry budgets and safe behavior during correlated interruption waves.
8. **[L3/L4]** Define eligibility policy, operational metrics, runbooks, readiness evidence and a governed spot program.

### 8.2 Concept map and vocabulary

```text
Workload + SLO + deadline + correctness requirements
                 |
                 v
      Eligibility and risk assessment
                 |
        +--------+---------+
        |                  |
        v                  v
  Spot pool             On-demand pool
  spare capacity        stable fallback
  taint/label            reserved headroom
        |                  |
        +--------+---------+
                 |
                 v
        Scheduling / placement
                 |
                 v
        Interruption / reclaim
                 |
                 v
   SIGTERM / drain / termination
                 |
                 v
  checkpoint -> validate -> resume
                 |
                 v
  idempotent output + correctness test
                 |
                 v
  metrics + net HCU + SLO/deadline review
                 |
                 v
       policy / fallback / feedback
```

| Term | Precise meaning | Common misconception |
|---|---|---|
| Spot/preemptible capacity | Provider-supplied spare capacity that can be reclaimed under provider-defined conditions | “It is ordinary capacity with a permanent discount” |
| Interruption/reclaim | Event in which a provider stops, deletes or otherwise reclaims an interruptible VM/node | “Kubernetes can prevent the provider from reclaiming it” |
| Notice window | Provider-specific time or signal between warning and termination, if provided | “All providers and products give the same notice” |
| Checkpoint | Durable, versioned record of progress sufficient to resume from a known state | “Any file written before shutdown is a valid checkpoint” |
| Resume correctness | Proof that continuing from a checkpoint yields the same valid logical result as uninterrupted execution | “The process restarted, therefore recovery worked” |
| Idempotency | Repeating an operation with the same logical key does not create an unintended duplicate effect | “At-least-once delivery means exactly-once processing” |
| Lost work | Work performed after the last valid checkpoint that must be repeated | “Only the time spent after SIGTERM is at risk” |
| Fallback capacity | Non-spot capacity that can accept work when spot is unavailable or unsafe | “A toleration automatically creates more capacity” |
| Correlated interruption | Multiple nodes in a shared pool/failure domain are interrupted in a related period | “Each node interruption is independent” |
| Spot share | Fraction of eligible workload compute assigned to spot | “Higher spot share always means better economics” |
| Net savings | On-demand counterfactual HCU minus total interruptible-strategy HCU, including waste and fallback | “Gross rate discount is realized savings” |
| Shuffle data | Intermediate distributed-processing data exchanged between workers | “An executor can always be replaced without recomputation” |
| Gang scheduling | Coordinated placement/start of a group of workers that must run together | “Distributed training always makes progress if one worker survives” |

**The central decision rule:** a workload is not spot-ready because it is labelled “batch” or “stateless.” It is spot-ready only after interruption, recovery correctness, deadline impact, fallback, security and net economics have been tested.

#### Provider terminology and verification boundary

Provider names and mechanics vary. Common terminology includes AWS Spot, Google Cloud Spot VMs and the older Preemptible VM terminology, and Azure Spot Virtual Machines `[VERIFY]` for current naming and behavior. Notice signals, shutdown behavior, maximum lifetime, pricing model, capacity availability and restart semantics vary by product, region and time. This course deliberately quotes **no typical interruption rate, discount, notice duration or maximum lifetime**. Before any separately approved real deployment, verify the exact product documentation, region, workload integration and contract conditions.

### 8.3 Level 1 — Beginner

#### 8.3.1 What spot capacity is

Cloud providers sometimes make spare compute capacity available under an interruptible purchasing or provisioning model. The provider can reclaim that capacity. The trade is:

- **Potential benefit:** lower direct compute HCU for work that can tolerate interruption.
- **Capacity risk:** the requested capacity may be unavailable when a job starts or when it needs to resume.
- **Recovery cost:** progress since the last valid checkpoint may need to be repeated.
- **Operational cost:** checkpoint storage, I/O, retries, backoff, fallback and on-call complexity.
- **SLO/deadline risk:** completion or freshness can degrade even if the job eventually succeeds.

The relevant unit is not the discounted compute hour. It is the **cost per successfully completed, correct unit of work within its deadline**.

#### 8.3.2 Workload eligibility

| Workload | Initial classification | Evidence required before approval |
|---|---|---|
| Stateless replicated API with spare replicas | Conditional | Replicas spread across failure domains; on-demand floor; load/SLO test during interruption wave |
| Checkpointed, idempotent batch ETL | Candidate | Checkpoint integrity, deterministic resume, duplicate-safe sink, deadline and fallback test |
| ML training with checkpoint/resume | Conditional candidate | Framework checkpoint completeness, optimizer/scheduler/RNG state, data-loader position, experiment tracking and distributed-worker recovery `[VERIFY]` |
| CI runners and development/test | Candidate | Job restartability, ephemeral credentials, cache correctness and retry budget |
| Data-parallel executor pool | Conditional | Executor loss/retry tolerance, shuffle recovery, driver availability and bounded recomputation |
| Queue consumers | Conditional candidate | At-least-once handling, idempotency keys, safe rebalance, bounded retries and visibility/ack semantics |
| Single-replica latency-critical service | Ineligible by default | Do not use spot unless a separate architecture provides tested redundancy and fallback |
| Database primary or broker leader | Ineligible by default | Keep stateful primary/quorum majority on stable capacity |
| Long non-checkpointed job | Ineligible | Add and validate checkpoint/resume first |
| Workload whose only state is local ephemeral disk | Ineligible | Externalize durable state and validate recovery |
| Strict-SLO workload with no fallback | Ineligible | Create a safe fallback design before considering spot |
| Quorum-based stateful system | Ineligible by default | Never place the quorum majority on spot |

This is a starting classification, not automatic approval. Evidence can move a workload from “ineligible” to “conditional,” but a label cannot override correctness, quorum or SLO requirements.

#### 8.3.3 What happens during an interruption

A simplified lifecycle:

1. A provider decides to reclaim a spot VM/node.
2. A provider-specific notice or metadata/event may be exposed `[VERIFY]`.
3. A node termination handler or node lifecycle integration may cordon/drain the node `[VERIFY]`.
4. Pods may receive termination handling, be evicted, be killed, or become unavailable.
5. Kubernetes controllers attempt to restore desired replicas or reschedule workloads.
6. Scheduling can remain pending if spot capacity is unavailable and fallback is absent or exhausted.
7. A job must resume from the last **valid** checkpoint, not merely the newest-looking checkpoint file.
8. The output sink must prevent duplicate or partial writes.

A Pod's `terminationGracePeriodSeconds` is a Kubernetes pod shutdown budget. It is not a promise that the provider will give the node that much warning. If the actual available notice is shorter, the pod may be terminated before a final checkpoint completes. Therefore, periodic checkpoints must already exist before interruption; the final SIGTERM checkpoint is only a best-effort optimization.

`preStop` runs as part of pod termination when configured; the kubelet later sends the container stop signal. Exact shutdown sequencing and provider node handling must be checked against the current Kubernetes/provider version `[VERIFY]`. A PDB constrains supported voluntary disruptions; **it does not prevent involuntary provider reclaim**.

#### 8.3.4 Graceful termination and checkpoint design

A safe job has four independent protections:

1. **Periodic durable checkpoint:** persist progress before a termination event occurs.
2. **Checkpoint validation:** write to a temporary path, flush/close, compute checksum, validate schema/version, then atomically publish a manifest or pointer.
3. **Resume validation:** reject corrupt, incomplete, incompatible or stale checkpoints before processing.
4. **Idempotent output:** write output by stable partition/batch key, use staging plus commit, or deduplicate on a deterministic operation key.

A final checkpoint attempt on SIGTERM is useful only if enough time remains. Never make correctness depend on it.

Example pod lifecycle fragment (illustrative only):

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: checkpointed-etl
  labels:
    app: checkpointed-etl
    team: data-platform
    workload-class: batch
spec:
  template:
    spec:
      restartPolicy: Never
      terminationGracePeriodSeconds: 25 # [SYNTHETIC] local lab value
      tolerations:
        - key: "spot-lab"
          operator: "Equal"
          value: "true"
          effect: "NoSchedule"
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              preference:
                matchExpressions:
                  - key: pool
                    operator: In
                    values: ["spot-lab"]
      containers:
        - name: worker
          image: python:3.11-slim
          command: ["python", "/app/etl.py"]
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "python /app/checkpoint.py --best-effort"]
          volumeMounts:
            - name: synthetic-checkpoints
              mountPath: /lab/checkpoints
      volumes:
        - name: synthetic-checkpoints
          emptyDir: {}
```

**Important:** `emptyDir` is node-local/ephemeral in this example. It is acceptable only for a tiny local mechanism demonstration and is not a durable production checkpoint store. A production design needs storage that survives node loss, with appropriate durability, access control, retention and restore validation. Do not copy this manifest as a production checkpoint architecture.

#### 8.3.5 Pool design: separate spot from on-demand

Use separate node pools or equivalent placement classes:

- Label spot workers, for example `pool=spot-lab`.
- Taint spot workers, for example `spot-lab=true:NoSchedule`.
- Add a matching toleration only to approved workloads.
- Use **preferred** affinity for spot, not a hard spot-only selector, when the workload is allowed to fall back to on-demand.
- Keep system-critical and stateful primaries off spot by default.
- Diversify instance families/sizes/zones where provider capabilities allow `[VERIFY]`.
- Reserve on-demand capacity for critical services and fallback; size it from a capacity model, not optimism.

A toleration permits scheduling onto a tainted node; it does not require the pod to use that node. A node selector or required affinity can accidentally remove fallback. Kubernetes taints/tolerations and node affinity are separate scheduling controls; verify the actual rendered Pod spec and placement.

#### 8.3.6 First economics model

Define:

- \(W\): useful productive compute work, in compute-hours.
- \(r_o\): on-demand rate, HCU per compute-hour.
- \(r_s\): spot rate, HCU per compute-hour.
- \(C_{cp}\): checkpoint storage and I/O cost, HCU.
- \(C_{retry}\): retry/recomputation cost, HCU.
- \(C_{fallback}\): fallback on-demand cost, HCU.
- \(C_{deadline}\): modeled deadline/freshness penalty, HCU, if the organization has a defensible model.
- \(C_{ops}\): incremental operational cost, HCU, if explicitly modeled.

Then:

\[
C_{\text{spot,total}} =
C_{\text{spot compute}} + C_{cp} + C_{retry} +
C_{fallback} + C_{deadline} + C_{ops}
\]

\[
C_{\text{on-demand}} = W \times r_o
\]

\[
\text{Net savings} =
C_{\text{on-demand}} - C_{\text{spot,total}}
\]

Net savings is positive only when the spot strategy costs less for the same successfully completed work and accepted SLO/deadline outcome. If the job misses its deadline or returns incorrect output, the apparent compute saving is not a valid success.

A simple interruption-aware approximation will be derived in L3. Do not multiply a discount by an arbitrary “interruption factor” without explaining what that factor means.

#### 8.3.7 Local simulation: what it demonstrates and what it cannot

The local lab creates a kind cluster with worker containers labelled and tainted as `spot-lab`. A bounded injector can select one labelled worker and stop its container after a dry-run and explicit confirmation. The Kubernetes control plane observes node loss and workloads become unavailable or reschedule according to the local cluster behavior.

This demonstrates scheduling, process interruption, retry, checkpoint and fallback mechanisms. It does **not** reproduce:

- real provider reclaim selection or correlation;
- real provider notice windows or shutdown signals;
- real spot capacity scarcity or pending behavior at fleet scale;
- real dynamic prices, discounts or billing;
- real instance hardware, network, storage or GPU performance;
- real provider node termination handler semantics.

#### 8.3.8 Beginner mistakes

| Mistake | Symptom | Correction |
|---|---|---|
| “Spot is just cheaper compute” | Gross savings reported while retries rise | Report net HCU per completed job |
| Only checkpoint on SIGTERM | Lost progress after abrupt interruption | Periodic checkpoints plus best-effort final checkpoint |
| Resume from newest file without validation | Corrupt or partial output | Check checksum, schema, version and completion marker |
| Use PDB as a reclaim shield | Node disappears despite PDB | Treat reclaim as involuntary; replicate and recover |
| Tolerate spot on every pod | Databases/system pods land on spot | Admission policy and workload-specific toleration |
| Retry immediately | Retry storm and dependency overload | Bounded exponential backoff with jitter and queue admission |
| Ignore fallback capacity | Pods remain pending and deadlines slip | Reserve and test on-demand fallback |
| Count gross discount as savings | Finance sees lower realized benefit | Subtract lost work, checkpoint, retry and fallback costs |

### 8.4 Level 2 — Intermediate

#### 8.4.1 Create a disposable kind spot-lab pool

Create a separate workspace:

```bash
mkdir -p ./lab-spot-preemptible/{manifests,src,tests,fixtures,results,checkpoints}
cd ./lab-spot-preemptible
```

Create `kind.yaml`:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: spot-lab
nodes:
  - role: control-plane
  - role: worker
  - role: worker
```

Create the cluster only if the local container runtime and kind are already installed:

```bash
kind create cluster --name spot-lab --config kind.yaml
kubectl --context kind-spot-lab get nodes -o wide
```

Label the two worker nodes. First inspect the names returned by the previous command; do not assume ordering:

```bash
kubectl --context kind-spot-lab get nodes
```

Then label and taint the worker nodes using the actual names:

```bash
kubectl --context kind-spot-lab label node <worker-a> pool=spot-lab spot-lab=true
kubectl --context kind-spot-lab taint node <worker-a> spot-lab=true:NoSchedule

kubectl --context kind-spot-lab label node <worker-b> pool=ondemand
```

Replace placeholders only after checking the output. Record the exact node names in `results/node-inventory.txt`.

**Safety check before every apply/delete/stop:**

```bash
kubectl config current-context
kubectl --context kind-spot-lab get nodes
kind get clusters
```

The expected context is `kind-spot-lab`. If it differs, stop. Never reuse this command sequence against another context.

#### 8.4.2 Spot-preferred placement with on-demand fallback

A workload needs a toleration to use the spot-lab taint. Preferred affinity makes spot attractive without making it mandatory:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: spot-preferred-worker
  labels:
    app: spot-preferred-worker
    workload-class: batch
spec:
  restartPolicy: Never
  tolerations:
    - key: spot-lab
      operator: Equal
      value: "true"
      effect: NoSchedule
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          preference:
            matchExpressions:
              - key: pool
                operator: In
                values: ["spot-lab"]
  containers:
    - name: worker
      image: busybox:1.36
      command: ["sh", "-c", "echo scheduled; sleep 3600"]
```

`busybox:1.36` is a lab example; pin and verify the image available to your local environment. If you want a fully offline lab, preload the image into kind before applying.

```bash
kubectl --context kind-spot-lab apply -f manifests/spot-preferred-worker.yaml
kubectl --context kind-spot-lab get pod spot-preferred-worker -o wide
kubectl --context kind-spot-lab describe pod spot-preferred-worker
```

Expected interpretation:

- If a spot-lab worker is available and feasible, the scheduler should prefer it.
- If no spot worker is feasible but an on-demand worker is, the pod may schedule there because affinity is preferred, not required.
- If the pod remains pending, inspect taints, tolerations, labels, resource requests, image availability and node readiness. Do not conclude that a provider spot pool would behave the same way.

#### 8.4.3 Checkpointed ETL/training-like job

The minimal job below is a deterministic simulator rather than a production data pipeline. It writes a checkpoint after each batch and uses a stable output key to avoid duplicate output after retry.

Create `src/spot_model.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable


@dataclass(frozen=True)
class CostInputs:
    useful_hours: float
    on_demand_rate: float
    spot_rate: float
    checkpoint_interval_hours: float
    checkpoint_cost_hours: float
    interruption_rate_per_hour: float
    checkpoint_storage_hcu: float = 0.0
    fallback_hcu: float = 0.0
    retry_hcu: float = 0.0

    def validate(self) -> None:
        values = (
            self.useful_hours, self.on_demand_rate, self.spot_rate,
            self.checkpoint_interval_hours, self.checkpoint_cost_hours,
            self.interruption_rate_per_hour, self.checkpoint_storage_hcu,
            self.fallback_hcu, self.retry_hcu,
        )
        if any(v < 0 for v in values):
            raise ValueError("cost inputs cannot be negative")
        if self.useful_hours <= 0:
            raise ValueError("useful_hours must be positive")
        if self.on_demand_rate <= 0 or self.spot_rate <= 0:
            raise ValueError("rates must be positive")
        if self.checkpoint_interval_hours <= 0:
            raise ValueError("checkpoint interval must be positive")


def overhead_fraction(checkpoint_interval_hours: float,
                      checkpoint_cost_hours: float,
                      interruption_rate_per_hour: float) -> float:
    """Simplified periodic-checkpoint overhead approximation."""
    if checkpoint_interval_hours <= 0 or checkpoint_cost_hours < 0:
        raise ValueError("invalid checkpoint parameters")
    if interruption_rate_per_hour < 0:
        raise ValueError("interruption rate cannot be negative")
    return (checkpoint_cost_hours / checkpoint_interval_hours) + (
        interruption_rate_per_hour * checkpoint_interval_hours / 2
    )


def estimate_costs(inputs: CostInputs) -> dict[str, float]:
    inputs.validate()
    overhead = overhead_fraction(
        inputs.checkpoint_interval_hours,
        inputs.checkpoint_cost_hours,
        inputs.interruption_rate_per_hour,
    )
    spot_compute = inputs.useful_hours * inputs.spot_rate * (1 + overhead)
    spot_total = (
        spot_compute + inputs.checkpoint_storage_hcu +
        inputs.fallback_hcu + inputs.retry_hcu
    )
    on_demand = inputs.useful_hours * inputs.on_demand_rate
    return {
        "overhead_fraction": overhead,
        "spot_compute_hcu": spot_compute,
        "spot_total_hcu": spot_total,
        "on_demand_hcu": on_demand,
        "net_savings_hcu": on_demand - spot_total,
    }


def break_even_interruption_rate(inputs: CostInputs) -> float:
    """Break-even λ for the simplified model with fixed extras set to zero."""
    inputs.validate()
    fixed = (
        inputs.checkpoint_storage_hcu + inputs.fallback_hcu +
        inputs.retry_hcu
    )
    if fixed:
        # Fixed extras are included by solving the full linear expression.
        remaining_rate = (
            inputs.on_demand_rate -
            fixed / inputs.useful_hours
        )
    else:
        remaining_rate = inputs.on_demand_rate
    ratio = remaining_rate / inputs.spot_rate
    lam = (2 / inputs.checkpoint_interval_hours) * (
        ratio - 1 -
        inputs.checkpoint_cost_hours / inputs.checkpoint_interval_hours
    )
    return max(0.0, lam)


def young_daly_interval_hours(checkpoint_cost_hours: float,
                              mean_time_between_interruptions_hours: float
                              ) -> float:
    """Conceptual Young/Daly-style interval; assumptions are not a guarantee."""
    if checkpoint_cost_hours <= 0 or mean_time_between_interruptions_hours <= 0:
        raise ValueError("inputs must be positive")
    return sqrt(2 * checkpoint_cost_hours *
                mean_time_between_interruptions_hours)


def should_fallback(interruptions: int, max_interruptions: int,
                    predicted_finish_hours: float,
                    remaining_deadline_hours: float,
                    fallback_available: bool) -> bool:
    if min(interruptions, max_interruptions) < 0:
        raise ValueError("interruption counts cannot be negative")
    if predicted_finish_hours < 0 or remaining_deadline_hours < 0:
        raise ValueError("time values cannot be negative")
    if interruptions >= max_interruptions and max_interruptions > 0:
        return fallback_available
    return (
        predicted_finish_hours > remaining_deadline_hours
        and fallback_available
    )


def bounded_backoff(attempt: int, base_seconds: float = 2.0,
                    cap_seconds: float = 60.0) -> float:
    """Deterministic ceiling before adding random jitter in a real worker."""
    if attempt < 0 or base_seconds <= 0 or cap_seconds <= 0:
        raise ValueError("invalid backoff input")
    return min(cap_seconds, base_seconds * (2 ** min(attempt, 30)))


def lost_work_hours(checkpoint_age_hours: float) -> float:
    if checkpoint_age_hours < 0:
        raise ValueError("checkpoint age cannot be negative")
    return checkpoint_age_hours


def net_savings(on_demand_hcu: float, spot_total_hcu: float) -> float:
    return on_demand_hcu - spot_total_hcu


def validate_checkpoint(record: dict) -> bool:
    required = {
        "schema_version", "sequence", "checksum", "complete", "payload"
    }
    if not required.issubset(record):
        return False
    if not (
        record["schema_version"] == 1
        and isinstance(record["sequence"], int)
        and record["sequence"] >= 0
        and isinstance(record["checksum"], str)
        and len(record["checksum"]) == 64
        and record["complete"] is True
        and isinstance(record["payload"], str)
    ):
        return False
    import hashlib
    actual = hashlib.sha256(record["payload"].encode("utf-8")).hexdigest()
    return actual == record["checksum"]


def simulate_executor_loss(executor_count: int, lost_count: int,
                           shuffle_recomputable: bool) -> dict[str, int | bool]:
    if executor_count <= 0 or lost_count < 0 or lost_count > executor_count:
        raise ValueError("invalid executor counts")
    shuffle_lost = lost_count > 0 and not shuffle_recomputable
    return {
        "surviving_executors": executor_count - lost_count,
        "retry_required": lost_count > 0,
        "shuffle_recompute_required": shuffle_lost,
        "all_workers_lost": lost_count == executor_count,
    }
```

Create `tests/test_spot_model.py`:

```python
import hashlib
import unittest

from src.spot_model import (
    CostInputs, overhead_fraction, estimate_costs,
    break_even_interruption_rate, young_daly_interval_hours,
    should_fallback, bounded_backoff, lost_work_hours,
    net_savings, validate_checkpoint, simulate_executor_loss,
)


class SpotModelTests(unittest.TestCase):
    def test_zero_interruption_overhead_is_checkpoint_cost_only(self):
        self.assertAlmostEqual(overhead_fraction(2, 0.1, 0), 0.05)

    def test_interruption_adds_expected_loss_component(self):
        self.assertAlmostEqual(overhead_fraction(2, 0.1, 0.05), 0.10)

    def test_cost_model_includes_storage_and_fallback(self):
        x = CostInputs(10, 10, 8, 2, 0.1, 0.05, 2, 10, 0)
        result = estimate_costs(x)
        self.assertAlmostEqual(result["spot_total_hcu"], 100.0)
        self.assertAlmostEqual(result["net_savings_hcu"], 0.0)

    def test_negative_rate_rejected(self):
        x = CostInputs(10, 10, -1, 2, 0.1, 0.05)
        with self.assertRaises(ValueError):
            estimate_costs(x)

    def test_break_even_is_non_negative(self):
        x = CostInputs(10, 10, 8, 2, 0.1, 0.05)
        self.assertGreaterEqual(break_even_interruption_rate(x), 0)

    def test_young_daly_interval(self):
        self.assertAlmostEqual(young_daly_interval_hours(0.1, 20), 2.0)

    def test_checkpoint_interval_rejects_zero(self):
        with self.assertRaises(ValueError):
            young_daly_interval_hours(0, 20)

    def test_fallback_on_attempt_budget(self):
        self.assertTrue(should_fallback(3, 3, 1, 4, True))

    def test_no_fallback_when_capacity_unavailable(self):
        self.assertFalse(should_fallback(3, 3, 1, 4, False))

    def test_fallback_on_deadline_risk(self):
        self.assertTrue(should_fallback(1, 4, 5, 3, True))

    def test_backoff_is_capped(self):
        self.assertEqual(bounded_backoff(20, 2, 30), 30)

    def test_lost_work_equals_checkpoint_age(self):
        self.assertEqual(lost_work_hours(0.75), 0.75)

    def test_checkpoint_integrity_schema(self):
        payload = "batch=12|input=v1|output=committed"
        good = {
            "schema_version": 1, "sequence": 12,
            "checksum": hashlib.sha256(payload.encode()).hexdigest(),
            "complete": True, "payload": payload
        }
        bad = dict(good, complete=False)
        corrupt = dict(good, payload="tampered")
        self.assertTrue(validate_checkpoint(good))
        self.assertFalse(validate_checkpoint(bad))
        self.assertFalse(validate_checkpoint(corrupt))

    def test_executor_loss_with_recomputable_shuffle(self):
        r = simulate_executor_loss(6, 2, True)
        self.assertEqual(r["surviving_executors"], 4)
        self.assertFalse(r["shuffle_recompute_required"])

    def test_executor_loss_with_lost_shuffle(self):
        r = simulate_executor_loss(6, 2, False)
        self.assertTrue(r["shuffle_recompute_required"])

    def test_invalid_executor_count(self):
        with self.assertRaises(ValueError):
            simulate_executor_loss(2, 3, True)


if __name__ == "__main__":
    unittest.main()
```

Run from the workspace root:

```bash
python -m unittest discover -s tests -v
```

The script is deliberately a teaching model. It does not call a cloud API, Kubernetes API or provider billing service. The `src` directory should contain an empty `__init__.py` if your Python import configuration requires it.

#### 8.4.4 Checkpoint lifecycle and correctness

A checkpoint should be treated as a transaction:

```text
1. Compute batch N
2. Write checkpoint.tmp
3. Flush and close
4. Compute checksum
5. Validate schema and sequence
6. Publish checkpoint manifest / atomic pointer
7. Mark checkpoint complete
8. Commit idempotent output for batch N
9. Advance to batch N+1
```

A partial checkpoint must never replace the last known-good checkpoint. The resume program should select the newest checkpoint whose completion marker, schema version and checksum validate. If validation fails, it should fall back to the prior valid checkpoint and record the rejected artifact.

A checkpoint is not correct merely because its checksum matches. The checksum proves byte integrity, not logical completeness. Add semantic checks: expected sequence range, input partition offsets, model/optimizer state version, output manifest, row counts or domain invariants.

#### 8.4.5 Queue consumers on spot

At-least-once message processing means a message may be delivered again after a consumer interruption. Use:

- a stable idempotency key derived from the message/business event;
- durable output deduplication or upsert semantics;
- bounded retries with exponential backoff and jitter;
- a dead-letter or poison-message policy;
- graceful stop: stop fetching new work, finish/commit only if safe, otherwise release/allow redelivery;
- consumer rebalance handling and bounded shutdown;
- queue-age and freshness-SLO monitoring.

Do not acknowledge a message before its durable output commit. Do not assume a visibility timeout, lease or consumer-group rebalance is identical across queue systems; verify the specific broker/client semantics `[VERIFY]`.

#### 8.4.6 Mixed spot/on-demand stateless service

Use replicas across both pools, a PDB for supported voluntary disruptions, and topology spread/anti-affinity where feasible. Keep a stable on-demand floor. A PDB is a voluntary-disruption guardrail, not a shield against involuntary reclaim. During a spot wave, verify actual available endpoints, not just desired replica count.

Illustrative Deployment fragment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-mixed-pool
spec:
  replicas: 4
  selector:
    matchLabels:
      app: api-mixed-pool
  template:
    metadata:
      labels:
        app: api-mixed-pool
    spec:
      tolerations:
        - key: spot-lab
          operator: Equal
          value: "true"
          effect: NoSchedule
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              preference:
                matchExpressions:
                  - key: pool
                    operator: In
                    values: ["spot-lab"]
      containers:
        - name: api
          image: nginx:stable
          resources:
            requests:
              cpu: 100m
              memory: 64Mi
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-mixed-pool-pdb
spec:
  minAvailable: 3
  selector:
    matchLabels:
      app: api-mixed-pool
```

This is a local scheduling demonstration, not a production-ready API manifest. Validate image pinning, resource sizing, topology, readiness probes, service behavior, PDB feasibility and version compatibility before any real use.

#### 8.4.7 Spark/Flink-style executor-loss tolerance — awareness

A distributed data job often has a driver/coordinator and multiple executors/workers. A worker loss may trigger task retry, stage recomputation, shuffle recovery or job failure depending on the engine and configuration.

The source curriculum requires awareness of:

- dynamic allocation;
- external shuffle service/storage;
- executor decommissioning;
- shuffle-data loss risk;
- driver on on-demand and executors on spot.

The exact behavior and supported configuration depend on framework version, deployment mode and storage integration `[VERIFY]`. This unit uses a small multi-worker simulator in Lab 10; it does not require Spark/Flink installation.

#### 8.4.8 Observability baseline

Collect at least:

| Signal | Why it matters |
|---|---|
| Interruption count and rate by pool/zone | Detect waves and correlated loss |
| Checkpoint age | Upper bound on progress at risk |
| Checkpoint write/validation failures | Detect unsafe resume paths |
| Lost-work fraction | Measure recomputation |
| Resume duration | Measure recovery latency |
| Job completion-time distribution | Quantify deadline inflation |
| Wasted compute HCU | Convert lost work into economics |
| Spot share of eligible compute | Understand adoption, not success by itself |
| Fallback rate | Detect spot scarcity or risk |
| Pending pod/job duration | Detect unavailable capacity |
| Retry amplification | Detect retry storms |
| Deadline attainment/freshness SLO | Verify business outcome |
| Net HCU savings per completed unit | Prevent gross-discount reporting |

#### 8.4.9 Pattern catalogue

| Pattern | Use when | Do not use when |
|---|---|---|
| Checkpointed batch on spot | Durable checkpoint and idempotent sink are proven | Checkpoint is local-only or resume is not correct |
| Spot-preferred mixed pool | Workload can use spot but needs stable fallback | Fallback capacity is not reserved or affordable |
| Queue consumers on spot | Rebalance and at-least-once processing are safe | Ack/commit semantics can lose messages |
| Driver on on-demand, executors on spot | Engine tolerates executor loss and shuffle recovery is verified | Driver is also interruptible or gang requirement is strict |
| On-demand floor plus spot burst | Online service needs stable baseline with elastic spare work | Spot is the only capacity path |
| Deadline-aware fallback | Job can estimate remaining time and fallback lead time | Forecast is too weak or fallback is unavailable |
| Diversified spot pools | Provider supports multiple families/zones and app tolerates heterogeneity | Workload requires a single specialized hardware shape |

#### 8.4.10 Anti-pattern catalogue

| Bad practice | Hidden cost/risk | Safer version |
|---|---|---|
| Place all workers in one spot pool/type/zone | Correlated loss can remove the whole batch tier | Diversify across supported failure domains and retain fallback |
| Use a PDB as a reclaim guarantee | Involuntary reclaim can still remove pods | Replication, checkpointing and fallback |
| Put stateful quorum majority on spot | Loss of quorum and possible write unavailability | Keep quorum majority on stable capacity |
| Final checkpoint only | Sudden reclaim loses most progress | Periodic durable checkpoints |
| Retry without jitter or cap | Thundering herd overloads metadata DB/queue | Exponential backoff, jitter, max attempts and admission control |
| Report rate discount as savings | Lost work/fallback erase savings | Net HCU per completed unit |
| Require spot-only placement | No capacity means pending work and missed deadline | Preferred spot placement plus explicit fallback |
| Put credentials on ephemeral nodes | Credential exposure and persistence risk | Workload identity, short-lived credentials and least privilege |

### 8.5 Level 3 — Advanced

#### 8.5.1 Capacity diversification and correlated interruption

A single spot pool using one instance family and one zone is a concentrated risk. Diversification can include:

- multiple instance families and sizes;
- multiple zones or regions where data locality and policy permit;
- flexible CPU/memory shapes;
- separate pools for CPU, memory and GPU jobs;
- a stable on-demand floor;
- independent fallback and quota planning.

Diversification reduces dependence on one capacity pool; it does not guarantee independent interruption. Provider reclaim events may be correlated by zone, capacity type, time or resource family. Model a correlated wave explicitly rather than assuming independent Bernoulli failures.

**Pool-level scenario table `[SYNTHETIC]`:**

| Scenario | Spot nodes lost | Remaining spot | On-demand spare | Expected action |
|---|---:|---:|---:|---|
| Isolated interruption | 1 of 6 | 5 | 2 | Resume one task; preserve on-demand floor |
| Pool wave | 3 of 6 | 3 | 2 | Queue retries; use fallback only for deadline-critical work |
| Zone unavailable | 6 of 6 in zone A | 0 in A | 4 in zone B | Rebalance if data locality and quota permit |
| Spot unavailable at job start | 0 available | 0 | 2 | Wait within budget or move to on-demand by policy |

All values are synthetic, not provider availability claims.

#### 8.5.2 Interruption-aware scheduling and buffer sizing

A safe mixed-pool design answers:

1. What fraction of replicas may be interrupted simultaneously without violating the SLO?
2. How long does on-demand fallback take to become schedulable?
3. Does the fallback pool have CPU, memory, GPU, pod-IP, quota and downstream capacity?
4. Can image pulls, model loads, metadata DB connections and queue rebalances absorb the wave?
5. What work should be paused or throttled while capacity recovers?

A simple buffer model:

\[
B_{\text{stable}} \geq D_{\text{critical}} + H_{\text{failure}} + H_{\text{scale-lag}}
\]

where:

- \(B_{\text{stable}}\) = stable on-demand capacity in compatible resource units;
- \(D_{\text{critical}}\) = critical demand that must remain served;
- \(H_{\text{failure}}\) = reserve for the largest planned simultaneous loss;
- \(H_{\text{scale-lag}}\) = additional capacity needed during provisioning/fallback delay.

Do not double-count the same failure reserve in both \(H_{\text{failure}}\) and the Unit 1 headroom model. Record which failure modes each reserve covers.

#### 8.5.3 Checkpoint interval: overhead versus lost work

Checkpointing too frequently wastes compute and I/O. Checkpointing too rarely increases expected lost work. A conceptual periodic-checkpoint model uses:

\[
\text{overhead fraction} \approx \frac{C}{\tau} + \frac{\lambda \tau}{2}
\]

where:

- \(C\) = checkpoint time, hours;
- \(\tau\) = checkpoint interval, hours;
- \(\lambda\) = interruption rate per hour;
- \(\lambda\tau/2\) = expected lost-work fraction under a simplified low-interruption-rate approximation.

This is a teaching approximation. It assumes approximately independent interruptions, a stable hazard rate, periodic checkpoints, negligible or separately modeled restart time, and no complex correlated failure or asynchronous checkpoint behavior. It does not model checkpoint I/O contention, storage failures, application-level inconsistency, or deadline effects.

A Young/Daly-style conceptual interval is:

\[
\tau^* \approx \sqrt{2 C \times MTBI}
\]

where \(MTBI\) is mean time between interruptions, in hours, and \(C\) is checkpoint cost, in hours. The result is in hours. Exact formulations and assumptions vary `[VERIFY]`; treat this as a starting point for sensitivity analysis, not a guarantee. Validate it against your synthetic interruption simulation and then against measured behavior in an approved environment.

#### 8.5.4 Deadline-aware orchestration and retry budgets

Every retry consumes deadline budget. A robust job controller should consider:

- maximum attempts;
- maximum total retry time;
- exponential backoff with jitter;
- current checkpoint age;
- remaining work estimate;
- fallback startup/queue delay;
- deadline/freshness SLO;
- on-demand budget approval.

**Decision rule `[ILLUSTRATIVE]`:**

- Continue on spot while predicted completion remains within the deadline with a safety margin and retry budget remains.
- Switch to on-demand after a configurable interruption count or when predicted completion threatens the deadline.
- If fallback is unavailable, stop admitting new work, preserve valid checkpoints, throttle catch-up and escalate before the deadline is irrecoverable.
- Do not keep retrying indefinitely because the HCU rate is low.

Example pseudo-policy:

```python
if not checkpoint_valid:
    reject_checkpoint_and_restore_previous()

if interruptions >= MAX_INTERRUPTS:
    request_fallback_or_pause()

elif predicted_finish > deadline - safety_margin:
    request_fallback_or_degrade()

elif retry_budget_exhausted:
    stop_retrying_and_escalate()

else:
    retry_with_exponential_backoff_and_jitter()
```

The code is a policy illustration; it needs workload-specific estimation and idempotency.

#### 8.5.5 ML training on spot

A training checkpoint may need more than model weights. Depending on the framework and training design, it may need:

- model parameters;
- optimizer state;
- learning-rate scheduler state;
- random-number-generator state;
- epoch, step and batch position;
- sampler/data-loader state;
- distributed rank/worker metadata;
- gradient scaler state;
- experiment-tracking run identity;
- dataset version and feature schema.

If only model weights are saved, the resumed training run may not be equivalent to continuing the original run. Exact framework support and elastic/distributed behavior are `[VERIFY]`.

**Gang/all-or-nothing risk:** distributed training may require all workers to participate. Losing one worker can stall the whole job or force coordinated restart. A GPU spot pool can be scarce even when CPU spot capacity is available. Calculate cost per successful training run, not GPU-hour discount alone. Include model load, data-loader warm-up, checkpoint transfer and experiment tracking.

#### 8.5.6 Streaming and stateful workloads

Stateful stream processors and state stores are risky candidates because recovery can involve restoring operator state, replaying input, rebuilding local state and catching up before the freshness SLO is restored.

Kafka-like consumers may be suitable if consumer rebalancing, idempotent sink writes and offset commits are correct. Brokers and leaders are not suitable by default. A quorum-based stateful system must keep its quorum majority on on-demand/stable capacity; **never place the majority of a quorum on spot**.

Evaluate:

\[
T_{\text{recovery}} =
T_{\text{detect}} + T_{\text{reschedule}} +
T_{\text{restore}} + T_{\text{replay}} + T_{\text{catch-up}}
\]

Compare the recovery time to the freshness/deadline SLO and backlog capacity. A recovery path that eventually works but cannot catch up before the freshness objective is not acceptable.

#### 8.5.7 Eligibility and SLO policy

Example tier policy `[ILLUSTRATIVE]`:

| Tier/class | Spot share policy | Required evidence |
|---|---|---|
| Tier-0 online | 0% by default | Explicit architecture exception, stable quorum/floor and proven failover |
| Tier-1 stateless service | Limited tested share | Replication, PDB awareness, topology spread, on-demand floor, interruption-wave SLO test |
| Tier-2 batch/ETL | Higher share permitted if deadline allows | Checkpoint, idempotency, max retries, fallback and correctness suite |
| ML training | Conditional | Full training-state checkpoint, resume equivalence, GPU fallback/queue and cost-per-run model |
| Dev/test/CI | Policy-defined | Ephemeral credentials, retry safety, artifact/cache correctness |

Spot eligibility is evidence-based. The workload owner must provide a readiness packet; the platform team validates placement/policy; SRE validates SLO and recovery; FinOps validates net economics; security validates ephemeral-node identity and data handling.

#### 8.5.8 Capacity unavailable and thundering herd

When spot capacity is unavailable, pending pods/jobs may accumulate. When a mass interruption happens, thousands of workers can retry together. The system can overload:

- metadata databases;
- object stores/checkpoint APIs;
- queue brokers;
- container registries;
- feature stores;
- external APIs;
- on-demand fallback pools.

Controls:

1. exponential backoff with randomized jitter;
2. maximum attempts and retry time budgets;
3. queue-based admission and concurrency caps;
4. per-tenant or per-job retry quotas;
5. staggered restart and checkpoint restore;
6. throttled catch-up to protect downstream systems;
7. circuit breakers and load shedding;
8. explicit fallback approval/budget policy;
9. alerts on pending duration, retry amplification and dependency saturation.

The node autoscaler's exact behavior when spot capacity is exhausted is implementation-specific and deferred to M15 Unit 9 `[VERIFY]`. Do not assume a cluster autoscaler can always obtain the requested shape.

#### 8.5.9 Cost accounting, security, risk and alternatives

**Cost accounting:** allocate spot HCU, lost work, checkpoint storage, retries and fallback to the owning workload/team using Unit 4 ownership metadata. Report gross spot-rate difference separately from net savings. Effective cost per completed job is:

\[
\text{HCU per completed job} =
\frac{\text{spot compute + checkpoint + retry + fallback + modeled delay}}
{\text{successful jobs}}
\]

**Security:** ephemeral nodes should not contain long-lived credentials. Use least-privilege workload identity and short-lived credentials. A node termination handler may need provider permissions; those privileges are `[VERIFY]` and must be scoped to the minimum operations. Quotas and admission policy help limit abusive compute consumption and cryptomining. Protect checkpoint data with access control, encryption and retention appropriate to the dataset.

**Alternatives:**

| Alternative | Benefit | Trade-off |
|---|---|---|
| Right-size first | Reduces waste without adding interruption risk | Requires profiling and SLO verification |
| Stable on-demand plus autoscaling | Predictable baseline with elastic growth | Can cost more during peaks; capacity/scale lag remains |
| Commitments/reservations plus autoscaling | May optimize stable baseline economics | Forecast error and inflexibility; terms must be verified |
| Schedule work at flexible times/regions | May increase access to capacity options | Data gravity, egress, freshness and operational complexity |
| Scale-to-zero | Avoids idle compute | Cold start and activation delay; M15 Unit 10 |
| Managed/serverless batch | Less node lifecycle management | Service semantics, limits, lock-in and pricing `[VERIFY]` |

Right-size before adding a more complex interruptible-capacity strategy. Spot is not a substitute for sound capacity planning.

### 8.6 Level 4 — Expert

#### 8.6.1 Operate spot as a managed program

A platform-level spot program has explicit roles:

| Role | Accountability |
|---|---|
| Workload owner | Checkpoint/resume, idempotency, correctness, deadline and runbook |
| Platform engineering | Pool templates, labels/taints, scheduling policy, metrics and safe defaults |
| SRE | SLO/error-budget impact, interruption drills, recovery runbooks and freeze decisions |
| FinOps | Rate-card version, net-savings model, owner allocation and savings reconciliation |
| Security | Workload identity, ephemeral-node access, checkpoint data protection and least privilege |
| Finance/business owner | Approves material fallback/budget trade-offs where organizational policy requires |

Teams own workload readiness. Platform provides reusable templates and safe defaults. M16 golden paths are a forward reference; this unit defines the readiness contract.

#### 8.6.2 Spot readiness review / ORR

A workload cannot be approved based on a “batch” label alone. The review packet must include:

- workload owner, team, tier, data classification and business deadline;
- expected spot share and stable on-demand floor;
- checkpoint format, storage durability, age objective and schema version;
- checksum/integrity validation and corrupted-checkpoint test;
- idempotency/deduplication proof and output-equivalence test;
- SIGTERM/preStop behavior and notice-window mismatch test;
- interruption drill results, lost-work fraction and resume duration;
- max retry/attempt/time budget and backoff/jitter configuration;
- fallback capacity, quota, approval and budget impact;
- dependency capacity and catch-up throttle;
- security review of node/workload identity and data access;
- dashboards, alerts, runbook, escalation and risk acceptance expiry;
- net HCU savings sensitivity and cost per completed unit;
- game-day date and next review date.

#### 8.6.3 Metrics and KPIs

| Metric | Formula/definition | Unit | Source/window | Owner | Limitation |
|---|---|---|---|---|---|
| Spot coverage of eligible compute | Spot compute-hours ÷ eligible compute-hours | % | Scheduler/accounting data per week | Platform | Adoption is not a success metric alone |
| Gross spot HCU difference | On-demand counterfactual HCU − direct spot compute HCU | HCU | Rate-card model per job/month | FinOps | Excludes waste and fallback |
| Net realized savings | On-demand counterfactual − spot compute − checkpoint − retry − fallback − modeled delay | HCU | Job ledger per completed workload | FinOps + owner | Counterfactual assumptions matter |
| Cost per completed job | Total strategy HCU ÷ successful completed jobs | HCU/job | Job ledger per release/window | Owner | Compare equivalent job sizes and correctness |
| Interruption rate | Interruption events ÷ spot node-hours | events/node-hour | Provider or simulator event stream | Platform | Local simulator is not provider data |
| Lost-work fraction | Recomputed useful work ÷ total attempted useful work | % | Checkpoint/job telemetry | Owner | Must distinguish recompute from planned work |
| Checkpoint age | Now − last valid checkpoint time | time | Job/checkpoint metadata | Owner | A recent but invalid checkpoint does not count |
| Checkpoint failure rate | Failed checkpoint writes/validations ÷ attempts | % | Job logs/metrics | Owner | Sample size and job mix matter |
| Resume time | Valid interruption detection to verified resumed progress | time | Job event timeline | SRE/owner | Include queue wait and restore |
| Completion-time inflation | (Interrupted completion − baseline completion) ÷ baseline completion | % | Matched job runs | Owner | Compare same data and load |
| Deadline attainment | Jobs completed by deadline ÷ eligible jobs | % | Orchestrator/job ledger | Owner | Define deadline and exclusions |
| Fallback rate | Jobs/compute-hours switched to on-demand ÷ spot-attempted jobs/compute-hours | % | Scheduler/orchestrator | Platform | High fallback may be correct under risk |
| Pending spot duration | Time eligible work remains pending for spot capacity | time | Scheduler events | Platform | Requires consistent event timestamps |
| Retry amplification | Attempts ÷ logical jobs | ratio | Job/queue telemetry | Owner | Distinguish legitimate fan-out |
| Backlog recovery time | Time until backlog returns to normal after interruption wave | time | Queue metrics | SRE | Depends on incoming traffic |
| SLO/error-budget impact | Error-budget burn attributable to interruption/recovery | ratio/time | SLI/SLO telemetry | SRE | Attribution can be uncertain |
| Wasted compute ratio | Compute spent on invalidated/repeated work ÷ total compute | % | Job/checkpoint accounting | Owner | Needs reliable progress accounting |
| Checkpoint overhead | Checkpoint compute and I/O ÷ productive compute | % | Job and storage telemetry | Owner | Storage billing may be outside cluster metrics |

Pair spot coverage and gross savings with correctness, deadline attainment, SLOs, lost work, fallback and net HCU. Goodhart risk: if teams are rewarded only for spot share, they may move unsuitable workloads to spot or undercount retries.

#### 8.6.4 Dashboards and alert rules

Dashboard panels should include:

- interruption count/rate by pool, zone and workload class;
- spot capacity pending pods/jobs and oldest pending age;
- checkpoint age against policy;
- checkpoint write/validation failure and corruption count;
- lost-work fraction and wasted HCU;
- retry amplification and queue depth;
- fallback-to-on-demand rate and remaining fallback headroom;
- completion-time distribution and deadline attainment;
- SLO/error-budget burn attributable to interruption;
- net savings per completed job and gross-to-net difference.

Alert conditions `[ILLUSTRATIVE]`:

- checkpoint age exceeds the workload's configured recovery-point objective;
- a job has exhausted its retry budget;
- pending eligible work threatens its deadline;
- interruption rate spikes relative to that pool's own baseline;
- retry amplification and metadata DB saturation rise together;
- fallback capacity falls below the protected floor;
- net savings becomes negative over a sufficiently representative window.

If Prometheus rules are used, validate syntax and expected firing behavior with the matching `promtool` version `[VERIFY]`. Do not invent metric names. The lab should define its own synthetic metric schema and tests.

#### 8.6.5 Incident runbooks

**Runbook A — Mass interruption**

- Trigger: interruption wave, simultaneous worker loss, pending spot work or rising retry rate.
- Check: identify affected pools/workloads; inspect last valid checkpoint; confirm output idempotency; inspect queue/metadata DB/object-store saturation; check fallback headroom and deadline risk.
- Act: pause new low-priority admissions; prevent immediate synchronized retries; resume only from validated checkpoints; cap concurrency; switch deadline-critical jobs to approved fallback.
- Do not: blindly replay all jobs; accept unvalidated checkpoint files; raise all retry counts; move stateful primaries to spot.
- Verify: output equivalence, queue drain, dependency health, deadline attainment, SLO and net HCU.
- Communicate: affected owners, SRE, platform, FinOps and business stakeholders.
- Follow-up: preserve timeline, calculate lost work, add regression tests and update pool diversification.

**Runbook B — Spot capacity unavailable**

- Trigger: eligible jobs remain pending or spot pool cannot scale.
- Check: capacity availability by pool/zone/family; pod scheduling events; quotas; node-pool ceilings; fallback capacity; job deadline.
- Act: wait within retry/deadline budget; queue/admit in priority order; use on-demand only under the documented approval/budget policy; throttle catch-up.
- Do not: remove all scheduling constraints or send every tenant to the same fallback pool.
- Verify: pending age falls, fallback floor remains healthy, SLO/deadline is met, and cost is recorded.
- Follow-up: revise diversification and forecast; record the capacity-unavailable period.

**Runbook C — Stuck or corrupted checkpoint**

- Trigger: checkpoint age exceeds policy, validation fails, resume loops or output mismatch occurs.
- Check: schema version, checksum, completion marker, sequence, input offsets, storage durability and last known-good checkpoint.
- Act: reject the invalid checkpoint; restore the previous validated checkpoint; quarantine the corrupt synthetic artifact; resume with idempotent output.
- Do not: overwrite the last good checkpoint or skip integrity validation to meet a deadline.
- Verify: output equivalence and monotonic progress.
- Follow-up: fix atomic publication, checksum and schema compatibility tests.

**Runbook D — Backlog catch-up overload**

- Trigger: backlog grows while recovery increases DB/object-store/queue saturation.
- Check: consumer concurrency, retry amplification, downstream connection budget, queue age, checkpoint restore load.
- Act: apply admission control, jitter, bounded concurrency and staged catch-up; prioritize freshness-critical partitions.
- Do not: scale consumers without checking downstream capacity.
- Verify: backlog slope turns negative without dependency SLO breach.
- Follow-up: add catch-up capacity model and game-day scenario.

#### 8.6.6 Eight organizational incident case studies

All incident facts and values below are hypothetical scenario statements, not industry statistics. Each scenario must be investigated with workload evidence, not blame.

**Case 1 — A 14-hour training job had no checkpoints and was interrupted near completion**

- **Symptoms:** a long training run restarts from the beginning after a reclaim event.
- **Impact:** almost all prior work is repeated; the hypothetical full rerun HCU exceeds the direct spot saving.
- **Evidence:** no checkpoint artifact, job timeline, GPU/CPU utilization history, retry count and rate-card calculation.
- **Immediate mitigation:** pause repeated retries; move the run to stable capacity if deadline-critical; preserve logs and artifacts.
- **Root cause:** workload was labelled spot-eligible without checkpoint/resume evidence.
- **Corrective fix:** periodic durable checkpoint including optimizer/scheduler/data position and experiment identity; resume-equivalence test.
- **Prevention/control:** eligibility policy requires a successful mid-run interruption test and checkpoint-age objective.
- **Verification metric:** lost-work fraction, resume correctness, net HCU per completed training run.

**Case 2 — All spot nodes used one instance type in one zone**

- **Symptoms:** one reclaim wave removes most of the batch pool.
- **Impact:** batch tier stalls and deadlines are missed.
- **Evidence:** node labels, pool inventory, interruption timestamps, pending jobs and zone distribution.
- **Immediate mitigation:** queue retries with jitter; protect on-demand floor; use approved alternate capacity.
- **Root cause:** no diversification and correlated capacity exposure.
- **Corrective fix:** support multiple compatible families/sizes/zones where available; define pool-specific quotas and fallback.
- **Prevention/control:** architecture review rejects a single-pool design for critical batch throughput.
- **Verification metric:** maximum simultaneous loss tolerated; deadline attainment during wave drill.

**Case 3 — Majority of a stateful quorum was placed on spot**

- **Symptoms:** stateful cluster loses quorum during reclaim.
- **Impact:** writes stop or recovery becomes unsafe; potential data availability risk.
- **Evidence:** member placement, quorum membership, election logs and node interruption timeline.
- **Immediate mitigation:** stop further spot placement; restore stable members according to the system's recovery procedure.
- **Root cause:** spot scheduling policy was applied to stateful members without quorum analysis.
- **Corrective fix:** keep quorum majority on stable on-demand capacity; use policy to reject stateful primaries/quorum majority on spot.
- **Prevention/control:** admission policy and placement test for stateful labels/roles.
- **Verification metric:** quorum remains available under the approved N−1 interruption test.

**Case 4 — Grace period exceeded actual notice; corrupted partial checkpoint resumed**

- **Symptoms:** final checkpoint write is interrupted; restart picks up a partial file and produces inconsistent output.
- **Impact:** correctness failure and additional recovery time.
- **Evidence:** notice signal timestamp, pod termination timestamps, grace period, checkpoint temp/final paths, checksum and schema logs.
- **Immediate mitigation:** stop the job; reject the invalid checkpoint; restore the previous known-good checkpoint.
- **Root cause:** the design assumed the final checkpoint would finish and published a partially written file as valid.
- **Corrective fix:** periodic checkpointing, atomic publish, checksum/schema/completion marker, fallback to last valid checkpoint.
- **Prevention/control:** corruption injection and notice-shorter-than-grace test required for readiness.
- **Verification metric:** invalid checkpoint rejection rate and output-equivalence test pass rate.

**Case 5 — Retry storm overwhelmed metadata database**

- **Symptoms:** mass interruption triggers synchronized resume attempts; metadata DB connections and write latency spike.
- **Impact:** unrelated jobs fail; queue recovery slows.
- **Evidence:** retry timestamps, DB connection saturation, queue depth, resume rate and interruption events.
- **Immediate mitigation:** pause admissions, cap retries/concurrency, apply jitter and staggered restore.
- **Root cause:** unbounded immediate retries and no admission control.
- **Corrective fix:** exponential backoff with jitter, max attempts, queue admission and downstream connection budget.
- **Prevention/control:** mass-interruption drill with DB-load proxy and abort threshold.
- **Verification metric:** retry amplification, DB saturation and backlog recovery time.

**Case 6 — Savings reported without lost-work cost**

- **Symptoms:** dashboard reports a large gross rate difference, but finance finds net savings much lower.
- **Impact:** business decisions are based on an incomplete economic model.
- **Evidence:** direct spot HCU, failed/retried work, checkpoint storage, fallback hours and completed-job count.
- **Immediate mitigation:** restate gross versus net savings; suspend the misleading KPI.
- **Root cause:** lost work and fallback were not allocated to the workload.
- **Corrective fix:** net savings ledger and cost-per-completed-job metric.
- **Prevention/control:** FinOps report must reconcile spot, waste, checkpoint and fallback HCU.
- **Verification metric:** percentage of spot compute with complete cost attribution; net HCU per completed job.

**Case 7 — Fallback to on-demand required a manual action**

- **Symptoms:** spot capacity disappears; operator notices late and manually changes placement.
- **Impact:** batch misses deadline despite available stable capacity.
- **Evidence:** pending age, escalation timestamps, fallback pool headroom, job deadline and manual change log.
- **Immediate mitigation:** invoke approved fallback for deadline-critical work; protect downstream dependencies.
- **Root cause:** fallback decision had no deadline-aware automation or owner.
- **Corrective fix:** bounded policy triggers fallback after N interruptions or projected deadline risk, with approval and budget guardrails.
- **Prevention/control:** test automatic and unavailable-fallback paths.
- **Verification metric:** time from deadline-risk detection to fallback scheduling; deadline attainment.

**Case 8 — Spot capacity unavailable at month-end**

- **Symptoms:** backfill jobs remain pending during a business-critical window.
- **Impact:** reporting/freshness window is missed.
- **Evidence:** spot pool pending duration, historical demand scenarios, on-demand quota, job schedule and data volume.
- **Immediate mitigation:** prioritize mandatory backfill; use approved stable capacity or reschedule lower-priority work.
- **Root cause:** plan assumed spot capacity would be available at a specific time.
- **Corrective fix:** schedule flexible jobs earlier; reserve a stable fallback budget/capacity; include month-end scenario in forecast.
- **Prevention/control:** release calendar and capacity plan include spot-unavailable case.
- **Verification metric:** month-end deadline attainment and fallback capacity coverage.

#### 8.6.7 Governance cadence and continuous validation

- **Per workload onboarding:** eligibility review and readiness packet.
- **Per release:** re-check image, memory, checkpoint format, concurrency, dependencies, deadline and fallback assumptions.
- **Monthly or workload-appropriate review:** compare predicted versus actual interruption waste, net HCU, deadline and SLO outcomes.
- **Scheduled staging game days:** interrupt one worker, then a bounded wave; validate correctness and recovery.
- **CI regression:** kill the synthetic job mid-run and compare output to uninterrupted baseline.
- **Quarterly policy review `[ILLUSTRATIVE]`:** tier mapping, exceptions, owner expiry and provider capability changes.
- **After incident:** convert a blameless action item into a fixture, policy test, runbook or alert.

#### 8.6.8 Limits and honesty

- Local simulation cannot reproduce provider interruption selection, notice, reclaim dynamics, price movement or capacity scarcity.
- HCU does not predict an invoice.
- A checkpoint checksum does not prove application-level correctness.
- A successful single-worker interruption test does not prove distributed training recovery.
- Spot availability is not guaranteed; a node autoscaler cannot create provider capacity that is unavailable.
- A higher spot share can increase operational toil and deadline risk.
- No single spot-share percentage, checkpoint interval or retry policy fits every workload.
- Re-evaluate provider product names, pricing, APIs, node termination integrations and framework behavior before a real deployment.

### 8.7 SRE lens

#### SLI/SLO design

Define workload-specific SLI/SLOs before enabling spot:

| Workload | SLI | Example objective style |
|---|---|---|
| Batch ETL | Correct jobs completed before deadline | Percentage of scheduled runs completed by freshness deadline |
| ML training | Successful, reproducible training runs | Percentage of runs completing with valid artifacts within agreed window |
| Queue consumer | Message age / processing freshness | Percentage of messages processed within freshness objective |
| Stateless API | Availability and latency | Request success and latency objectives, measured during interruption waves |
| Recovery system | Time to valid resumed progress | Recovery duration distribution and checkpoint integrity |

Spot should consume only the reliability margin explicitly approved for that workload. If the error budget is exhausted or a critical incident is active, freeze new spot experiments and use the stable operating mode until the service recovers.

#### Failure modes and blast radius

| Failure mode | Blast radius | Guardrail |
|---|---|---|
| Single pool interruption wave | Batch tier or whole service | Diversification and stable floor |
| Invalid checkpoint | Incorrect output across replayed partitions | Integrity + semantic validation |
| Retry storm | Metadata DB, queue, object store and unrelated tenants | Backoff, jitter, concurrency cap |
| No fallback capacity | Deadline/SLO failure | Reserve and test fallback |
| Spot quorum majority | Stateful service unavailability | Admission policy and stable quorum majority |
| Leaked ephemeral credentials | Account/project compromise and unauthorized spend | Workload identity, least privilege, short-lived credentials |
| Overaggressive catch-up | Downstream dependency overload | Throttle and dependency headroom |
| Misleading savings KPI | Bad architecture/business decisions | Net HCU per successful unit of work |

#### Runbook decision loop

```text
Trigger -> identify affected pool/workloads
        -> validate last good checkpoint and output state
        -> protect dependencies and stop retry amplification
        -> choose resume / queue / fallback / pause
        -> verify correctness, SLO, deadline and HCU
        -> communicate impact and decision
        -> retain evidence and add regression control
```

### 8.8 Security lens

| Threat | Control | Concrete negative test |
|---|---|---|
| Long-lived credentials on ephemeral nodes | Workload identity or short-lived scoped credentials | Inspect synthetic node/workload config and fail if a static secret is mounted into a spot worker |
| Over-privileged termination handler | Scope provider permissions to required node lifecycle operations `[VERIFY]` | Policy fixture rejects wildcard/admin permission |
| Untrusted checkpoint content | Validate schema, checksum, version and semantic metadata before deserialization/use | Corrupt checksum and schema; resume must reject |
| Malicious or oversized job consumes cheap capacity | Namespace quotas, concurrency caps, max attempts and budget guardrails | Submit job fixture exceeding allowed GPU/CPU/attempt limits |
| Cryptomining/abuse | Admission restrictions, runtime monitoring and owner attribution | Policy rejects unknown owner/tier and unauthorized spot pool |
| Checkpoint data exposure | Encryption, access controls, retention and audit | Negative test rejects public/unauthenticated checkpoint store configuration |
| Fault injector targets wrong cluster | Explicit context/cluster/label checks and dry-run | Test wrong context, missing label and non-lab cluster; no stop action |
| Rate-card tampering | Versioned, reviewed synthetic rate card with checksum | Reject unapproved rate-card version |
| CI secret leakage | No secrets in fixtures/logs; least-privilege CI | Scan generated evidence for credential-like values and fail on match |

**Not addressed by this local unit:** production cloud IAM implementation, provider node termination-handler deployment, enterprise key management, formal data residency review and production threat-model sign-off. These require environment-specific review `[VERIFY]`.

### 8.9 Production checklist

- [ ] Workload owner, team, tier, data classification and deadline are recorded.
- [ ] Eligibility decision is evidence-based; workload is not approved solely because it is labelled batch/stateless.
- [ ] Stateful primaries and quorum majority remain on stable on-demand capacity.
- [ ] Spot pool is separate and clearly labelled/tainted.
- [ ] Only approved workloads have spot tolerations.
- [ ] Preferred placement does not accidentally remove on-demand fallback.
- [ ] Spot pool is diversified across compatible capacity options where supported.
- [ ] Stable fallback capacity and quota are documented and tested.
- [ ] Checkpoint is durable, versioned, checksummed and atomically published.
- [ ] Resume rejects corrupt/partial/incompatible checkpoints.
- [ ] Output is idempotent and duplicate-safe.
- [ ] Interruption drill passed with output equivalence.
- [ ] SIGTERM/preStop is best effort; correctness does not rely on final checkpoint completion.
- [ ] Retry budget, exponential backoff, jitter and concurrency cap are configured.
- [ ] Deadline-aware fallback and fallback-unavailable behavior are tested.
- [ ] Queue/metadata DB/object-store capacity is sufficient for recovery/catch-up.
- [ ] SLO/error-budget impact and freeze criteria are documented.
- [ ] Net HCU includes lost work, checkpoint, retry, fallback and modeled delay.
- [ ] Dashboards and alerts cover interruptions, checkpoint age, waste, pending, retries, fallback and deadlines.
- [ ] Ephemeral node identity is least-privilege; no long-lived credentials are stored on nodes.
- [ ] Runbooks, risk acceptance, owner and expiry are recorded.
- [ ] Game-day and CI interruption tests are scheduled.
- [ ] Post-release/post-game-day review verifies actual outcomes.
- [ ] Cleanup of the local lab cluster and synthetic files is verified.

### 8.10 Hands-on lab set

All ten labs are distinct. Full simulation uses Cap+Scale and a throwaway kind cluster; Cap-Core provides the worksheet/simulator path. All cost rates and outputs are HCU and synthetic. Every interruption is bounded and local. Do not run commands against a shared cluster.

#### Common lab workspace and safety preflight

Workspace:

```text
lab-spot-preemptible/
├── README.md
├── kind.yaml
├── manifests/
├── src/
├── tests/
├── fixtures/
│   ├── rate_card.json
│   ├── jobs.json
│   └── checkpoints/
├── results/
└── runbooks/
```

`fixtures/rate_card.json`:

```json
{
  "label": "[SYNTHETIC]",
  "version": "spot-lab-rate-card-v1",
  "units": "HCU per compute-hour",
  "on_demand": 10.0,
  "spot": 8.0,
  "checkpoint_storage_hcu": 2.0
}
```

Before every destructive/local-fault step:

```bash
test "$(kubectl config current-context)" = "kind-spot-lab"
kind get clusters | grep -qx "spot-lab"
kubectl --context kind-spot-lab get nodes -l spot-lab=true
```

If any check fails, stop. The injector must also check the target node's `spot-lab=true` label and the kind cluster identity. Start in dry-run. Default maximum events: one. Default timeout: short and explicit. A second event requires a deliberate parameter change and a new confirmation.

**Common stop conditions:** wrong context; worker label missing; more than configured event count; timeout exceeded; checkpoint corruption outside the synthetic directory; SLO/dependency abort threshold reached; operator presses Ctrl-C/kill switch.

**Common cleanup:** remove only lab namespace resources, then delete only the named `spot-lab` kind cluster after verifying current context and cluster list. Preserve evidence before cleanup.

---

#### Lab 1 — Bounded interruption injector

**Outcome:** build a dry-run-first injector that can select only a worker in the disposable `spot-lab` kind cluster, log the planned action, enforce event/time bounds and expose a kill switch.

**Profile:** Cap+Scale. Cap-Core alternative: run the injector's target-validation tests against a fake node inventory without stopping containers.

**Prerequisites:** kind cluster, `kubectl`, Docker or compatible runtime used by kind, Python 3.11+ `[VERIFY]`. Measure your machine first.

**Workspace:** `lab-spot-preemptible/lab1-injector/`.

**Procedure:**

1. Create the `spot-lab` cluster and label/taint one worker as described in L2.
2. Save the actual worker name and container name in a local lab inventory file.
3. Implement `injector.py` with arguments `--context`, `--cluster`, `--node`, `--rate`, `--notice-seconds`, `--max-events`, `--timeout-seconds`, `--seed` and `--confirm`. Dry-run is the default; there is no separate flag that enables destructive behavior.
4. Require context exactly `kind-spot-lab`, cluster exactly `spot-lab`, and node label `spot-lab=true`.
5. Require `--max-events` to equal 1 for this lab build and require a bounded positive timeout. With no `--confirm`, the injector only logs a dry-run. A real local stop requires `--confirm` and a second typed confirmation.
6. Resolve the node's backing kind container using `kind get nodes --name spot-lab`; verify the exact node appears in that result. Do not accept arbitrary container names.
7. Log timestamp, context, cluster, node, dry-run state, event count and result to `results/injector.log`.
8. For the actual interruption, use the container runtime to stop only the validated worker container. Do not remove volumes or delete the cluster as part of the injection.
9. Observe the node become NotReady/unavailable and record pod status. Restart the worker container only after the drill is complete and the cluster is in a safe state.

**Illustrative safe command interface:**

```bash
python injector.py --context kind-spot-lab --cluster spot-lab \
  --node <validated-worker> --max-events 1 --timeout-seconds 20
```

Only after reviewing the dry-run log, and only for the disposable cluster:

```bash
python injector.py --context kind-spot-lab --cluster spot-lab \
  --node <validated-worker> --max-events 1 --timeout-seconds 20 --confirm
```

The implementation must refuse unknown flags/targets and must never accept a production context. Keep the real stop operation disabled until all checks pass.

**Example bounded injector implementation (`src/injector.py`):**

This implementation deliberately supports only the named disposable kind cluster and a single event per invocation. Its default is dry-run. A real local stop requires the exact worker to be listed by `kind get nodes`, carry the `spot-lab=true` label, not be the control-plane node, pass a kill-switch check, and receive a typed confirmation. It does not call a cloud API.

```python
from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_CONTEXT = "kind-spot-lab"
EXPECTED_CLUSTER = "spot-lab"
KILL_SWITCH = Path(".STOP_SPOT_LAB_INJECTOR")


def run(command: list[str], timeout: float = 5.0) -> str:
    result = subprocess.run(
        command, check=True, capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip()


def validate_target(context: str, cluster: str, node: str) -> dict:
    if context != EXPECTED_CONTEXT or cluster != EXPECTED_CLUSTER:
        raise ValueError("refusing: only kind-spot-lab / spot-lab is allowed")
    if KILL_SWITCH.exists():
        raise ValueError("kill switch exists; refusing all interruption actions")

    current = run(["kubectl", "config", "current-context"])
    if current != EXPECTED_CONTEXT:
        raise ValueError(f"current context is {current!r}, not the lab context")

    clusters = run(["kind", "get", "clusters"]).splitlines()
    if EXPECTED_CLUSTER not in clusters:
        raise ValueError("named kind cluster is not present")

    nodes = run(["kind", "get", "nodes", "--name", EXPECTED_CLUSTER]).splitlines()
    if node not in nodes:
        raise ValueError("target is not a node container in the named kind cluster")

    raw = run([
        "kubectl", "--context", EXPECTED_CONTEXT,
        "get", "node", node, "-o", "json"
    ])
    record = json.loads(raw)
    labels = record.get("metadata", {}).get("labels", {})
    if labels.get("spot-lab") != "true":
        raise ValueError("target node does not have spot-lab=true")
    if "node-role.kubernetes.io/control-plane" in labels:
        raise ValueError("control-plane interruption is prohibited")
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", required=True)
    parser.add_argument("--cluster", required=True)
    parser.add_argument("--node", required=True)
    parser.add_argument("--rate", type=float, default=0.0,
                        help="probability for this one invocation; default 0")
    parser.add_argument("--notice-seconds", type=float, default=0.0,
                        help="synthetic delay before local stop; max 30")
    parser.add_argument("--max-events", type=int, default=1)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--confirm", action="store_true")
        args = parser.parse_args()

    if not (0.0 <= args.rate <= 1.0):
        parser.error("--rate must be between 0 and 1")
    if not (0.0 <= args.notice_seconds <= 30.0):
        parser.error("--notice-seconds must be between 0 and 30")
    if args.max_events != 1:
        parser.error("this lab build permits exactly one event per invocation")
    if not (1.0 <= args.timeout_seconds <= 60.0):
        parser.error("--timeout-seconds must be between 1 and 60")

    log_path = Path("results/injector.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "time": datetime.now(timezone.utc).isoformat(),
        "context": args.context,
        "cluster": args.cluster,
        "node": args.node,
        "rate": args.rate,
        "notice_seconds": args.notice_seconds,
        "dry_run": not args.confirm,
    }

    try:
        validate_target(args.context, args.cluster, args.node)
        selected = random.Random(args.seed).random() < args.rate
        event["selected_by_rate"] = selected
        if not selected:
            event["result"] = "no interruption selected"
            log_path.write_text(json.dumps(event) + "\n", encoding="utf-8")
            print(event["result"])
            return 0

        if not args.confirm:
            event["result"] = "dry-run only; no container stopped"
            log_path.write_text(json.dumps(event) + "\n", encoding="utf-8")
            print(event["result"])
            return 0

        typed = input(f"Type STOP {args.node} to stop this lab worker: ")
        if typed != f"STOP {args.node}":
            raise ValueError("confirmation did not match target node")

        deadline = time.monotonic() + args.timeout_seconds
        if args.notice_seconds:
            time.sleep(args.notice_seconds)
        if time.monotonic() >= deadline:
            raise TimeoutError("injector deadline expired before stop")

        # kind node container names match the node names returned above.
        subprocess.run(
            ["docker", "stop", "--time", "1", args.node],
            check=True, capture_output=True, text=True,
            timeout=max(1.0, deadline - time.monotonic()),
        )
        event["result"] = "one validated lab worker stopped"
        log_path.write_text(json.dumps(event) + "\n", encoding="utf-8")
        print(event["result"])
        return 0
    except (ValueError, TimeoutError, subprocess.SubprocessError,
            json.JSONDecodeError) as exc:
        event["result"] = f"refused: {exc}"
        log_path.write_text(json.dumps(event) + "\n", encoding="utf-8")
        print(event["result"], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

**Injector validation tests:** test `validate_target` with mocked command results rather than stopping a real container. Required cases: wrong context, wrong cluster, missing cluster, target not returned by `kind get nodes`, missing `spot-lab=true`, control-plane label, kill-switch file present, invalid probability, event cap above one, timeout above the bound, and confirmation mismatch. In every negative case, assert that the mocked `docker stop` function was never called. A dry-run with `--rate 1` must log the selected event without stopping the container.

Example dry-run:

```bash
python src/injector.py --context kind-spot-lab --cluster spot-lab \
  --node <validated-worker> --rate 1 --notice-seconds 2 \
  --max-events 1 --timeout-seconds 20
```

For the one explicitly approved local stop, add `--confirm`, type the exact target confirmation, and verify the worker is the only container affected.

**Positive tests:** correct cluster + labelled worker passes dry-run; event cap of one is accepted; timeout is enforced.

**Negative tests:** wrong context; wrong cluster; unlabelled node; control-plane node; zero/negative timeout; event count greater than cap; missing confirmation; timeout already expired; kill switch set. Each must refuse the stop action.

**Expected evidence:** inventory, dry-run log, negative-test report, one bounded interruption event log, node recovery evidence.

**Abort/rollback:** Ctrl-C; do not attempt a second stop; restart only the exact worker container if it is safe; if cluster state is uncertain, stop the lab and rebuild the disposable cluster rather than improvising.

**Pass criteria:** every invalid target is rejected before any stop command; dry-run never changes cluster state; event count cannot exceed cap; evidence is retained.

**Fidelity caveat:** stopping a kind worker container is a local failure simulation, not a provider reclaim event or realistic cloud notice.

---

#### Lab 2 — Checkpointed ETL/training-like job and no-checkpoint control

**Outcome:** compare checkpointed and non-checkpointed synthetic work under interruption; prove output equivalence and measure lost work, resume time and HCU.

**Profile:** Cap+Scale; Cap-Core simulator path is acceptable for limited hardware.

**Synthetic workload:** process 100 numbered batches; each batch produces deterministic output `hash(batch_id + input_version)`. Checkpoint after every 10 batches `[ILLUSTRATIVE]`. Use a dedicated `fixtures/checkpoints/` directory.

**Steps:**

1. Create `src/job.py` with deterministic batch processing and a stable idempotency key.
2. Write checkpoint records containing schema version, last completed batch, input version, output manifest and checksum.
3. Publish checkpoints atomically: temporary file → flush/close → checksum → completion marker → atomic rename.
4. Run uninterrupted baseline and save `results/baseline-output.json`.
5. Run checkpointed job; interrupt after a synthetic batch boundary using Lab 1's bounded injector or a deterministic simulator event.
6. Resume from the last valid checkpoint and compare final output to baseline.
7. Run a no-checkpoint control with the same interruption; restart from batch zero and calculate repeated work.
8. Record lost batches, resume time, completion-time inflation, attempts, output equivalence and HCU.

**Expected output table `[SYNTHETIC]`:**

| Run | Interruption | Restart point | Recomputed batches | Output correct |
|---|---|---:|---:|---|
| Baseline | None | 0 | 0 | Yes |
| Checkpointed | After batch 47 | 40 | 7 | Yes |
| No-checkpoint control | After batch 47 | 0 | 47 | Yes after full rerun |

The table illustrates the arithmetic; your local measurements must be labelled `[MEASURED — YOUR ENVIRONMENT]`.

**Positive tests:** uninterrupted output equals resumed output; repeated batch execution does not duplicate sink records; checkpoint resumes from last valid sequence.

**Negative tests:** missing checkpoint; invalid checksum; wrong input version; partial checkpoint; duplicated batch delivery; output commit failure.

**Stop/rollback:** stop the local job if checkpoint path resolves outside the workspace, output manifest is malformed, or the injector target is uncertain. Remove only the synthetic test directory after preserving evidence.

**Pass criteria:** checkpointed and baseline output are equivalent; no-checkpoint control demonstrates higher recomputation; lost work and cost are calculated transparently.

**Evidence:** baseline output, checkpoint manifests, interruption log, resume report, no-checkpoint comparison and tests.

**Fidelity caveat:** batch processing and interruptions are deterministic local simulations; they do not represent provider reclaim probability.

---

#### Lab 3 — Graceful termination and checkpoint integrity

**Outcome:** prove that final checkpoint completion is not guaranteed and corrupted checkpoints are rejected before resume.

**Profile:** Cap+Scale or Cap-Core for file-level tests.

**Synthetic parameters:** notice delay 20 seconds and pod grace 30 seconds `[SYNTHETIC]` in one run; reverse the values in another. These are lab timings only and not provider notice claims.

**Steps:**

1. Create a worker that checkpoints periodically and attempts a final checkpoint on SIGTERM.
2. Add `preStop` only as an additional best-effort hook; record when it starts/ends.
3. Run Case A where simulated notice is longer than checkpoint write time.
4. Run Case B where notice is shorter than the checkpoint write time.
5. Kill the worker during a partial checkpoint write; leave a `.tmp` file with no completion marker.
6. Attempt resume; the loader must reject the partial file and choose the previous valid checkpoint.
7. Change the checkpoint schema version; verify that incompatible versions are rejected or migrated by an explicit tested migration.
8. Compare output with the uninterrupted baseline.

**Expected observations:** Case A may complete a final checkpoint; Case B may not. Both must recover correctly from the last periodic valid checkpoint. The final checkpoint is never the only correctness path.

**Positive tests:** valid checkpoint loads; complete marker and checksum validate; old schema migration works only when explicitly implemented.

**Negative tests:** truncated JSON, checksum mismatch, missing marker, stale sequence, wrong schema, symlink/path escape.

**Abort/rollback:** stop if the test attempts to read/write outside the synthetic checkpoint directory. Restore the last valid fixture; never overwrite it with the corrupt test file.

**Pass criteria:** corrupted/partial checkpoints are rejected; output equivalence holds; no assumption is made that `preStop` or SIGTERM always finishes.

**Evidence:** timing traces, checkpoint validation report, rejected-corruption fixtures and output-equivalence test.

**Fidelity caveat:** the simulated notice/grace relationship illustrates timing races, not a real provider's termination sequence.

---

#### Lab 4 — Mixed spot/on-demand service

**Outcome:** run a stateless replicated service across local spot-lab and on-demand workers; observe availability and fallback; demonstrate PDB limitations.

**Profile:** Cap+Scale.

**Steps:**

1. Label/taint one worker as spot-lab and another as on-demand.
2. Deploy a stateless multi-replica service with preferred spot affinity and toleration.
3. Add readiness checks and a PDB. Keep one or more replicas on the stable pool by policy `[ILLUSTRATIVE]`.
4. Record pod placement, ready endpoints and synthetic request success before interruption.
5. Stop one spot worker using Lab 1.
6. Observe endpoint count, pending pods, rescheduling and request outcomes.
7. Repeat with an interruption wave only if the one-event drill passed and the abort threshold is understood.
8. Compare with a deployment whose pods require spot-only placement; show that no fallback can leave pods pending.
9. Compare PDB behavior during voluntary `kubectl drain` versus abrupt worker stop. The PDB can constrain supported voluntary eviction; it cannot prevent involuntary loss.

**Metrics:** available replicas, successful synthetic requests, pending duration, fallback count, HCU cost and SLO result.

**Positive tests:** service stays above its minimum available replica threshold during the tested one-worker loss; fallback placement occurs where capacity permits.

**Negative tests:** spot-only affinity causes pending pods after worker loss; PDB is not treated as protection against involuntary loss; no stateful primary is deployed to spot.

**Abort/rollback:** stop load generation if synthetic request success falls below the lab SLO for the defined window; restore worker; scale to stable capacity; delete only lab resources.

**Pass criteria:** learner can explain observed availability, pending behavior and the difference between voluntary drain and involuntary loss.

**Evidence:** manifests, placement snapshots, endpoint/request report, PDB experiment and HCU worksheet.

**Fidelity caveat:** local worker stop is not a cloud reclaim; kind topology and capacity are not production hardware.

---

#### Lab 5 — Spot economics, break-even and checkpoint interval

**Outcome:** calculate net HCU, break-even interruption assumptions and checkpoint-interval sensitivity.

**Profile:** Cap-Core required; Cap+Scale optional for validating assumptions against Lab 2 measurements.

**Synthetic inputs `[SYNTHETIC]`:**

- useful work \(W=10\) compute-hours;
- on-demand rate \(r_o=10\) HCU/compute-hour;
- spot rate \(r_s=8\) HCU/compute-hour;
- checkpoint interval \(\tau=2\) hours;
- checkpoint cost \(C=0.1\) hours;
- interruption rate \(\lambda=0.05\) per hour;
- checkpoint storage cost = 2 HCU;
- fallback cost = 10 HCU;
- additional retry cost = 0 HCU.

Using the simplified model:

\[
h = C/\tau + \lambda\tau/2 = 0.1/2 + 0.05(2)/2 = 0.10
\]

\[
C_{\text{spot compute}} = W r_s (1+h) = 10 \times 8 \times 1.10 = 88\ HCU
\]

\[
C_{\text{spot total}} = 88 + 2 + 10 = 100\ HCU
\]

\[
C_{\text{on-demand}} = 10 \times 10 = 100\ HCU
\]

\[
\text{Net savings} = 100 - 100 = 0\ HCU
\]

The gross direct compute difference is 20 HCU, but checkpoint and fallback costs consume it in this synthetic example. Do not call this positive savings.

**Break-even derivation:** with fixed extras \(F\) per useful-work interval and the simplified overhead model:

\[
W r_s (1 + C/\tau + \lambda\tau/2) + F = W r_o
\]

\[
\lambda^* =
\frac{2}{\tau}
\left(
\frac{r_o - F/W}{r_s} - 1 - \frac{C}{\tau}
\right)
\]

If the right-hand side is negative, the strategy is not cheaper even at zero interruption rate under these assumptions. This break-even expression is a simplified model; fallback cost may itself depend on interruption rate and deadline policy, so a full model should solve that dependency rather than treating it as fixed.

**Checkpoint interval:** use the Young/Daly-style approximation with explicit assumptions and compare \(\tau^*\) to the simulated results.

**Sensitivity:** vary interruption rate, checkpoint interval, spot rate, checkpoint cost and fallback share. Plot or tabulate net savings and lost-work fraction.

**Positive tests:** zero interruption produces only checkpoint overhead; increasing interruption rate does not reduce modeled savings; adding fallback cost cannot improve net savings.

**Negative tests:** reject negative rates, zero interval, negative interruption rate and negative work.

**Pass criteria:** explain when spot stops saving HCU and why the optimum interval is only a starting estimate.

**Evidence:** input register, formulas, sensitivity table, script/test output and decision memo.

**Fidelity caveat:** all rates and interruption rates are synthetic; no provider economics are inferred.

---

#### Lab 6 — Deadline-aware fallback

**Outcome:** switch a synthetic job to on-demand after N interruptions or when predicted completion threatens its deadline.

**Profile:** Cap-Core required; Cap+Scale optional.

**Steps:**

1. Create a job fixture with useful work remaining, last checkpoint age, interruption count, deadline and estimated fallback start time.
2. Implement a policy with `max_interruptions`, retry budget, remaining deadline and `fallback_available`.
3. Run a safe path where spot can finish within deadline.
4. Run an interruption-budget path where fallback is available.
5. Run a deadline-risk path where predicted completion on spot exceeds remaining deadline.
6. Run a fallback-unavailable path; policy must pause/queue/escalate rather than claim the deadline is safe.
7. Run retry-exhaustion and corrupted-checkpoint paths.

**Expected decisions `[SYNTHETIC]`:**

| Scenario | Predicted spot finish | Remaining deadline | Fallback | Decision |
|---|---:|---:|---|---|
| A | 2 h | 5 h | Available | Continue spot |
| B | 6 h | 5 h | Available | Fallback |
| C | 6 h | 5 h | Unavailable | Pause/queue/escalate |
| D | Retry budget exhausted | 4 h | Available | Fallback or controlled stop |

**Positive tests:** fallback occurs on interruption budget or deadline risk; fallback does not occur when spot is safe and policy allows it.

**Negative tests:** negative interruption count, missing deadline, fallback unavailable, retry exhaustion, invalid checkpoint.

**Abort/rollback:** no real scheduler or cloud resource is called. Stop if test attempts external access.

**Pass criteria:** decision is deterministic for the same inputs, reason is logged, and HCU impact is recorded.

**Evidence:** policy code, decision table, test report and fallback HCU comparison.

**Fidelity caveat:** this is a local decision simulator, not an autoscaler or provider capacity guarantee.

---

#### Lab 7 — Thundering-herd interruption drill

**Outcome:** demonstrate retry amplification after a mass interruption, then reduce it with exponential backoff, jitter, queueing and throttled catch-up.

**Profile:** Cap+Scale; Cap-Core simulator path is available.

**Steps:**

1. Create 50 synthetic jobs with the same interruption timestamp `[SYNTHETIC]`.
2. In the baseline, retry immediately and count metadata DB calls per time bucket.
3. Measure retry amplification, queue depth, DB-load proxy, resume rate and backlog recovery time.
4. Add exponential backoff with randomized jitter.
5. Add queue admission/concurrency caps and a maximum attempt budget.
6. Throttle catch-up so dependency load remains under a synthetic safe ceiling.
7. Repeat with a partial interruption wave and a correlated full-pool wave.
8. Compare before/after and document the trade-off between faster retry and stable recovery.

**Expected direction:** jitter spreads retries over time; admission control limits peak concurrency; throttled catch-up can increase total recovery time while preventing dependency overload. The desired result is stable recovery within the freshness/deadline objective, not the fastest possible retry spike.

**Positive tests:** retry timestamps are distributed; max attempts respected; concurrency cap respected; backlog eventually drains in the synthetic model.

**Negative tests:** no jitter; infinite retry; zero concurrency cap; catch-up rate above dependency limit; corrupted checkpoint.

**Abort thresholds `[ILLUSTRATIVE]`:** stop if DB-load proxy exceeds its synthetic ceiling for multiple consecutive intervals, queue depth exceeds the lab cap, or output correctness fails.

**Evidence:** baseline/fixed time series, retry histogram, dependency-load proxy, backlog recovery report and tests.

**Fidelity caveat:** the DB load is a synthetic proxy, not a benchmark of a real database.

---

#### Lab 8 — Spot eligibility policy-as-code and readiness checklist

**Outcome:** reject stateful primaries and tier-0 workloads from spot by default; accept only tested eligible workloads with complete evidence.

**Profile:** Cap+Scale for local manifest fixtures; Cap-Core for pure policy tests.

**Policy inputs:**

```yaml
workload:
  name: batch-etl
  owner: data-platform
  tier: batch
  stateful_primary: false
  spot_requested: true
  checkpoint_test: passed
  idempotency_test: passed
  sigterm_test: passed
  corruption_test: passed
  fallback_test: passed
  deadline_test: passed
  runbook: present
  exception_expiry: null
```

**Steps:**

1. Build a policy validator that reads only JSON/YAML fixture data and does not execute embedded content.
2. Require owner and tier.
3. Reject `stateful_primary=true` when `spot_requested=true`.
4. Reject tier-0 spot use unless an explicit, reviewed exception is present; default policy is zero.
5. Require checkpoint, idempotency, SIGTERM, corruption, fallback and deadline evidence for batch/ML.
6. Require exception owner, rationale, compensating controls and expiry.
7. Add positive fixtures for a tested batch ETL and CI runner.
8. Add negative fixtures for a stateful primary, tier-0, missing evidence, expired exception, missing owner and unknown tier.
9. Run the policy check in a local CI simulation.

**Positive tests:** tested batch job passes; eligible CI runner passes; an approved, unexpired exception follows the documented review path.

**Negative tests:** stateful primary rejected; tier-0 rejected; missing checkpoint test rejected; expired exception rejected; missing owner rejected; malformed input rejected; attempts to bypass by changing a display label rejected.

**Pass criteria:** policy decisions are deterministic, explainable and auditable; exceptions cannot be indefinite.

**Evidence:** policy source, fixtures, positive/negative test report, readiness checklist and exception record.

**Fidelity caveat:** this is a CI/admission-style policy model. Exact admission controller syntax is intentionally not assumed.

---

#### Lab 9 — Observability dashboards and alert rules

**Outcome:** build synthetic metrics and alert rules for interruption, checkpoint, waste, pending, fallback and deadline risk; catch a planted alerting gap.

**Profile:** Cap+Obs optional; Cap-Core can use CSV and Python checks.

**Synthetic metric schema:**

```text
spot_interruptions_total{pool,zone,workload}
spot_pending_jobs{pool,workload}
spot_checkpoint_age_seconds{workload}
spot_checkpoint_failures_total{workload}
spot_lost_work_seconds_total{workload}
spot_resume_seconds_bucket{workload,le}
spot_fallback_total{workload}
spot_job_deadline_missed_total{workload}
spot_net_savings_hcu_total{workload}
spot_retry_attempts_total{workload}
```

These are lab-defined metric names, not claims about a provider or standard exporter.

**Steps:**

1. Generate a small synthetic time series for normal operation.
2. Plant an interruption spike, a stale checkpoint, a pending job and a negative net-savings period.
3. Build dashboard panels for the metrics above.
4. Define alert rules with explicit windows and thresholds `[ILLUSTRATIVE]`.
5. Add unit tests for alert conditions. If Prometheus rule files are used, run `promtool test rules` from the matching Prometheus distribution `[VERIFY]`.
6. Plant a gap: omit checkpoint-age monitoring. The test suite must fail because a stale checkpoint is not detected.
7. Add the alert and prove the test passes.
8. Interpret the dashboard: distinguish interruption rate from job impact, gross savings from net savings, and pending work from capacity shortage.

**Positive tests:** interruption storm, stale checkpoint and retry storm fire their intended alerts; normal baseline does not fire.

**Negative tests:** no false alert on one isolated event; missing metric is not treated as zero; invalid label/series data is rejected or marked unknown.

**Pass criteria:** all planted alert gaps are detected and fixed; dashboard supports an operational decision.

**Evidence:** metric fixtures, dashboard JSON/Markdown, alert rules, `promtool` output if used, alert test report and interpretation notes.

**Fidelity caveat:** metrics are synthetic; no real provider telemetry or cost data is present.

---

#### Lab 10 — Multi-worker Spark-like simulator

**Outcome:** simulate a driver/coordinator on on-demand and executors on spot; compare with a single spot pool under executor loss and shuffle-data loss.

**Profile:** Cap+Scale recommended; Cap-Core simulator path required if cluster resources are limited.

**Simulator model:**

- one driver;
- six synthetic executors;
- deterministic partition IDs;
- a flag indicating whether shuffle data is recoverable;
- executor-loss count;
- retry and recomputation cost;
- completion time and HCU.

**Steps:**

1. Build a simulator that assigns the driver to `pool=ondemand`.
2. Assign executors to `pool=spot-lab` with fallback allowed only for the configured scenario.
3. Run baseline with no executor loss.
4. Remove one executor; compare recovery with recomputable versus non-recomputable shuffle data.
5. Remove multiple executors simultaneously; test the all-workers-lost case.
6. Compare single-pool spot design to diversified mixed design.
7. Record completion time, lost work, retries, shuffle recomputation, HCU and output correctness.
8. State the engine-specific behaviors that would need verification before translating this to Spark/Flink `[VERIFY]`.

**Positive tests:** one executor loss triggers retry; recomputable shuffle does not require full shuffle reconstruction; output remains equivalent.

**Negative tests:** all executors lost; non-recomputable shuffle lost; driver assigned to spot in the default policy; two correlated losses exceed the configured tolerance.

**Pass criteria:** explain why driver-on-on-demand/executors-on-spot can reduce control-plane interruption risk while still leaving executor-loss and shuffle risks.

**Evidence:** simulator source, fixtures, run outputs, comparison table, tests and architecture decision record.

**Fidelity caveat:** this is not a Spark/Flink benchmark and does not reproduce their scheduler, shuffle service or decommissioning implementation.

---

### 8.11 Self-check questions

1. **Why is “batch workload” not enough to approve spot?**  
   **Answer:** Batch work may be non-checkpointed, non-idempotent, deadline-bound or dependent on local state. Approval requires tested recovery, correctness, fallback and economics.  
   **Tempting wrong answer:** “Batch has no users.” Batch freshness and downstream consumers are still user/business outcomes.

2. **Does a PDB prevent a provider from reclaiming a spot node?**  
   **Answer:** No. PDBs constrain supported voluntary disruption paths; involuntary disruptions cannot be prevented by PDBs.  
   **Tempting wrong answer:** “PDB says minAvailable, so Kubernetes must keep those pods alive.” A lost node cannot be held by a budget object.

3. **Why should a final SIGTERM checkpoint be best-effort only?**  
   **Answer:** The actual notice may be shorter than the pod grace period or the process may be killed before the write completes. Periodic durable checkpoints must carry correctness.  
   **Tempting wrong answer:** “Increase terminationGracePeriodSeconds.” The provider controls node reclaim timing.

4. **What proves a checkpoint is safe to resume?**  
   **Answer:** Integrity, schema/version, completion marker, sequence/input offsets and application-level invariants, followed by output-equivalence tests.  
   **Tempting wrong answer:** “The file exists.” Existence does not prove completeness or semantic correctness.

5. **Why can a lower spot rate produce higher cost per completed job?**  
   **Answer:** Recomputed work, checkpoint overhead, storage, retries, fallback and deadline penalties can exceed the direct rate difference.  
   **Tempting wrong answer:** “The rate is lower, so total cost must be lower.” That ignores work that must be repeated.

6. **When should a job fall back to on-demand?**  
   **Answer:** When retry budget is exhausted or projected completion threatens the deadline and approved fallback is available; otherwise pause/queue/escalate safely.  
   **Tempting wrong answer:** “Only after spot becomes unavailable.” Deadline risk can become unacceptable earlier.

7. **Why diversify spot pools?**  
   **Answer:** A single type/zone creates correlated exposure. Diversification can reduce dependence on one pool, but does not guarantee independent interruptions.  
   **Tempting wrong answer:** “Use many nodes of the same type.” More nodes in one failure domain can still fail together.

8. **What is the difference between gross and net savings?**  
   **Answer:** Gross savings compare direct rates; net savings subtract lost work, checkpoints, retries, fallback and modeled delay.  
   **Tempting wrong answer:** “Subtract only failed-job compute.” Successful jobs may also pay checkpoint and fallback overhead.

9. **Why is a queue consumer often more suitable than a broker leader?**  
   **Answer:** Consumers can often be replicated/rebalanced and process messages idempotently; broker leaders are stateful control/data-plane roles with quorum and durability requirements.  
   **Tempting wrong answer:** “Both are containers.” Stateful role and recovery semantics matter more than packaging.

10. **What does a local kind interruption drill prove?**  
    **Answer:** It tests local scheduling, process interruption, recovery code, policy and evidence workflow. It does not prove provider reclaim timing, capacity availability, pricing or cloud performance.  
    **Tempting wrong answer:** “A successful kill test proves production spot readiness.” It is one layer of evidence only.

11. **How should distributed training handle worker loss?**  
    **Answer:** Verify framework-specific checkpoint/resume, optimizer and data-loader state, gang/elastic semantics, GPU availability, and experiment tracking.  
    **Tempting wrong answer:** “Restart the missing pod.” The distributed job may require coordinated restart.

12. **Why is spot coverage a dangerous standalone KPI?**  
    **Answer:** It rewards adoption regardless of workload suitability, SLO, correctness or net savings. Pair it with completed-job cost, deadline attainment, lost work and incident outcomes.  
    **Tempting wrong answer:** “Higher coverage proves FinOps maturity.” It may reward unsafe placement.

### 8.12 Evidence artifacts

Retain the following in `lab-spot-preemptible/`:

```text
lab-spot-preemptible/
├── README.md                         # safety, scope, fidelity and cleanup
├── assumptions.md                    # all assumptions and [ILLUSTRATIVE] thresholds
├── kind.yaml                         # disposable local cluster definition
├── inventory/
│   └── nodes.json                    # actual local node/container mapping
├── fixtures/
│   ├── rate_card.json                # synthetic HCU rate card
│   ├── jobs.json                     # workload eligibility fixtures
│   ├── checkpoints/                  # synthetic checkpoints only
│   └── corrupt-checkpoints/           # intentionally invalid fixtures
├── manifests/
│   ├── spot-preferred-worker.yaml
│   ├── mixed-pool-service.yaml
│   └── policy-fixtures/
├── src/
│   ├── spot_model.py
│   ├── injector.py
│   ├── checkpoint_job.py
│   ├── fallback_policy.py
│   └── executor_simulator.py
├── tests/
│   ├── test_spot_model.py
│   ├── test_injector_safety.py
│   ├── test_checkpoint_integrity.py
│   ├── test_policy.py
│   └── test_alerts.py
├── results/
│   ├── injector-dry-run.log
│   ├── interruption-drill.json
│   ├── checkpoint-equivalence.json
│   ├── no-checkpoint-control.json
│   ├── economics-sensitivity.csv
│   ├── fallback-decisions.csv
│   ├── retry-storm-before-after.csv
│   ├── alert-test-report.txt
│   └── executor-simulator-report.json
└── runbooks/
    ├── spot-readiness-review.md
    ├── mass-interruption.md
    ├── capacity-unavailable.md
    ├── checkpoint-recovery.md
    ├── backlog-catch-up.md
    ├── risk-acceptance.md
    ├── game-day-report.md
    ├── net-savings-report.md
    └── postmortem.md
```

Do not store real credentials, private provider pricing, production identifiers, customer data or real billing exports. Preserve exact local measurement context, including machine/cluster version and timestamp, but do not publish sensitive host information.

### 8.13 Common interview and design-review questions

**1. How would you decide whether an ETL workload is suitable for spot?**

**Model answer:** I would inspect its deadline/freshness SLO, checkpoint interval and durability, idempotent sink semantics, maximum recomputation, input partitioning, dependency capacity and fallback. Then I would run bounded interruption tests at different progress points, corrupt a checkpoint, compare output to an uninterrupted baseline, and calculate net HCU per completed job. I would approve only with an owner, runbook, alerting and expiry/review trigger.

**2. Why does a PDB not guarantee availability during spot reclaim?**

**Model answer:** A PDB limits certain voluntary evictions through supported disruption paths. Provider reclaim or node loss is involuntary and cannot be prevented by the PDB. Availability comes from replicas across failure domains, stable capacity, correct readiness/traffic handling and recovery/fallback.

**3. Derive the break-even interruption rate for a checkpointed job. What assumptions can invalidate it?**

**Model answer:** Start with on-demand cost \(W r_o\) and spot cost \(W r_s(1+C/\tau+\lambda\tau/2)+F\). Solve for \(\lambda\), where \(F\) includes fixed checkpoint storage/retry/fallback. The approximation assumes a stable interruption hazard, periodic checkpoints and simplified recovery. Correlated interruption, fallback triggered by \(\lambda\), non-negligible restart, checkpoint I/O contention, variable work and deadlines require a richer model and sensitivity analysis.

**4. How do you design fallback for a deadline-bound batch workload?**

**Model answer:** Estimate remaining work and fallback start delay, track checkpoint age and retry budget, and compare predicted finish to the deadline with a safety margin. Trigger fallback before the deadline is unrecoverable. If fallback is unavailable, pause/admit by priority, preserve state, throttle catch-up and escalate. Validate the policy under spot-unavailable and downstream-saturation scenarios.

**5. What would you change after a retry storm caused a metadata database outage?**

**Model answer:** Add exponential backoff with jitter, max attempts and retry-time budget, queue-based admission, per-workload concurrency limits, staged checkpoint restore and throttled catch-up. Monitor retry amplification, DB connection saturation and backlog recovery. Add a mass-interruption game-day and CI regression test that verifies bounded retries and dependency load.

**6. How would you govern spot eligibility across hundreds of services?**

**Model answer:** Define workload tiers and evidence requirements; expose a reusable spot pool template; enforce labels, tolerations and policy-as-code; require checkpoint/idempotency/fallback/SLO tests; record exceptions with owner and expiry; measure net savings, correctness, deadline attainment and error-budget impact; run scheduled interruption game days; and feed incidents into policy and golden-path improvements.

### 8.14 Sources and verification notes

#### Official documentation consulted

- Kubernetes, **Taints and Tolerations**: scheduling behavior, taints, tolerations and placement.  
  https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/
- Kubernetes, **Pod Lifecycle**: termination flow, `preStop`, termination grace and stop signal behavior.  
  https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
- Kubernetes, **Disruptions and PodDisruptionBudgets**: voluntary versus involuntary disruption; PDB limits and behavior.  
  https://kubernetes.io/docs/concepts/workloads/pods/disruptions/
- Amazon EC2, **Spot Instance interruption notices**: provider-specific interruption notice mechanisms and behavior.  
  https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html
- Google Cloud Compute Engine, **Spot VMs**: Spot VM terminology, reclaimability and provider-specific behavior.  
  https://cloud.google.com/compute/docs/instances/spot

#### Claims deliberately marked `[VERIFY]`

- Current provider product names, interruption notices, maximum lifetimes, reclaim signals, pricing and availability by region/resource type.
- Provider node termination handlers, IAM permissions, node shutdown integration and exact drain behavior.
- Azure Spot current terminology and reclaim mechanics.
- Spark/Flink dynamic allocation, shuffle recovery, decommissioning and external shuffle behavior.
- Distributed training framework checkpoint/elastic recovery semantics.
- Karpenter/Cluster Autoscaler behavior when spot capacity is unavailable; detailed implementation belongs to M15 Unit 9.
- Prometheus metric names, alert rule compatibility and `promtool` version.
- Exact Kubernetes/kind API compatibility and local image availability.

#### Technical interpretation boundaries

- The M15 syllabus is the curriculum source of truth. Official documentation verifies implementation-specific details; it does not replace curriculum requirements.
- The local lab's kind worker is a containerized test node, not a cloud spot instance.
- HCU values are synthetic and cannot predict provider invoices.
- No provider discount percentage, typical interruption rate, notice duration or maximum runtime is asserted.
- A local success is evidence about the local recovery implementation only. Real deployment requires a separate approved provider-specific validation plan.

---

## Final completion audit

### Audit A — Source and scope

- [x] Target is Unit 8 only: `08-spot-and-preemptible-instances-for-data-workloads.md`.
- [x] M15 authoritative syllabus Unit 8 requirements were inspected and used.
- [x] M15 unit sequence and Stage 2E/M15 subtree were checked against `Roadmap(20261103-035611).md`.
- [x] Unit 8 is positioned after Unit 7 and before Unit 9.
- [x] Cross-module handoffs to M03, M10, M11, M13, M14, M15 and M16 are included.
- [x] Existing M15 Units 1–7 were used as continuity references where accessible. Unit 4, Unit 5, Unit 6 and Unit 7 teaching artifacts were inspected; prior context and source prompts were used for Units 1–3.
- [x] No other M15 unit is generated and no repository file is modified.

### Audit B — Curriculum coverage

- [x] L1: spot/preemptible definition, provider differences `[VERIFY]`, no real discount/notice figures, workload eligibility, Kubernetes termination, design requirements, HCU model and simulation fidelity.
- [x] L2: checkpointed job, interruption drills, graceful termination/corrupt checkpoint, mixed pool, queue consumers, economics, observability, policy and Spark/Flink-style simulator.
- [x] L3: diversification/correlation, PDB limitations, checkpoint interval, deadline-aware fallback, ML training, streaming/stateful safeguards, SLO policy, capacity-unavailable/thundering-herd handling, cost accounting, security and alternatives.
- [x] L4: eligibility/ORR, metrics, alerts, runbooks, organizational model, game days/CI validation, multi-cluster considerations and limits/honesty.
- [x] All eight organizational incident scenarios use symptoms → impact → evidence → mitigation → root cause → corrective fix → prevention → verification.
- [x] All ten distinct mandatory labs are present.
- [x] Twelve worked examples are included across the teaching sections and labs: workload classification; interruption lifecycle; checkpoint loss; effective cost; break-even; checkpoint interval; mixed pools/PDB; deadline fallback; retry storm; executor-loss model; net savings; eligibility policy.
- [x] Runbooks, metrics, self-checks, six interview questions, evidence artifacts and sources are included.

### Audit C — Safety and technical correctness

- [x] No cloud provisioning, paid services, real billing or credentials required.
- [x] No real prices/currency symbols, discount percentages, interruption rates or typical notice windows.
- [x] HCU, assumptions, illustrative policies and synthetic results are labelled.
- [x] PDB is not described as preventing involuntary reclaim.
- [x] Correctness does not rely on final checkpoint completion.
- [x] Checkpoint corruption is detected before resume.
- [x] Idempotency and correctness are tested, not assumed.
- [x] Stateful primaries and quorum majority are not placed on spot by default.
- [x] Retries are bounded and use backoff/jitter; mass interruption has a safe abort path.
- [x] Fallback capacity, deadline, SLO and budget implications are considered.
- [x] Security and fault-injector boundaries are addressed.
- [x] Local simulation limitations are explicit.

### Audit D — Structure and artifact integrity

- [x] Mandatory M15 skeleton headings 8.0–8.14 appear in order.
- [x] Ten distinct labs are documented with outcomes, profile, steps, tests, safety, cleanup, evidence and fidelity caveats.
- [x] Eight incident cases include diagnosis, mitigation, root cause, prevention and verification.
- [x] Formulas define variables, units, assumptions and limitations.
- [x] Document is a teaching lesson, not an outline.
- [x] No other unit or repository artifact is generated or modified.

### Audit E — Output verification

- [x] Exact target filename was used.
- [x] File was reopened and checked for expected beginning/end and required section/lab/incident markers.
- [x] The generated artifact is standalone Markdown.
- [x] No repository files were changed.

**Authoring and validation note:** The document was generated as a standalone artifact. The included code snippets and commands are teaching examples; unless a separate test result is explicitly recorded by the learner, they should not be interpreted as executed against a real cluster or provider. The local simulator is intentionally not represented as a production-scale or provider-fidelity test.
