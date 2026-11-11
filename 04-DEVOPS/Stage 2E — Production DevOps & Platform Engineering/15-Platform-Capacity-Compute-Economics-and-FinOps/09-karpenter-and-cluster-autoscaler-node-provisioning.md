# Unit 9 — Karpenter and Cluster Autoscaler Node Provisioning

**Stage:** Stage 2E — Production DevOps & Platform Engineering  
**Subfolder:** `15-Platform-Capacity-Compute-Economics-and-FinOps/`  
**Module:** M15 — Platform Capacity, Compute Economics and FinOps  
**Target file:** `09-karpenter-and-cluster-autoscaler-node-provisioning.md`  
**Estimated study time:** 36–48 hours (reading/architecture 9–12 h; simulator and labs 20–27 h; review/design defence 7–9 h)  
**Prerequisites:** Stages 0–2D and Stage 2E M01–M14; especially M03 Unit 2 (requests/limits, QoS, quotas, priorities, right-sizing), Unit 5 (PDBs, drain and disruption), Unit 6 (HPA/VPA and introductory autoscaling), Unit 7 (taints, tolerations, affinity and placement); M10 Unit 6 (queueing, headroom, traffic ramps and retry amplification); M11 Units 9/13 (saturation and load testing); M12 Unit 7 (node image rotation/drift); M14 (multi-cluster/region); M15 Units 1–2 (capacity/headroom, quotas/priorities) and Unit 8 (spot/on-demand pools).  
**Core tools:** Python 3.11+ `[VERIFY]`, standard library, `unittest`, JSON/CSV, shell and Git.  
**Awareness / optional tools:** `kind`, `kubectl`, KWOK/`kwokctl`, Cluster Autoscaler (CA), Karpenter, Prometheus/`promtool`, cloud-provider integrations and managed node-autoscaling offerings. Verify exact versions and compatibility before use.  
**Last reviewed:** 2026-11-03  
**Tool baseline assumed:** Python 3.11+ syntax `[VERIFY]`; Kubernetes/kind versions inherited from M03/M11 and recorded in `versions.txt`; no CA, Karpenter, KWOK, Prometheus or provider version is prescribed.  
**Stack profile required:** Cap+Scale for the full simulation sequence. The guaranteed path is the learner-built Python simulator. Cap-Core is the reduced path when laptop resources are constrained. Cap+Obs is optional for Lab 4/observability extensions only.  
**Footprint:** Python simulator is small and has no cluster dependency. Optional kind/KWOK/Prometheus components can be material on an 8-GB laptop; sequence them, measure CPU/memory/disk, and stop after each lab. Do not assume a fixed footprint — **measure yours**.  
**Prices used:** hypothetical cost units (HCU) only. Node shapes, HCU rates, delays, thresholds, traces and outputs are `[SYNTHETIC]` or `[ILLUSTRATIVE]`; no real prices, discounts, instance specifications, quotas or provider lead times are asserted.

> **Completion outcome:** Diagnose why a pod is pending, distinguish pod autoscaling from node provisioning, compare CA-style node-group expansion with Karpenter-style flexible provisioning, model bin-packing and fragmentation, set safe capacity ceilings, reason about consolidation and disruption, calculate simulated HCU cost, and operate node provisioning as a governed platform capability. All practical node provisioning in this unit is simulated; no cloud resources are created.

## Prerequisite handoff and scope

### Mandatory handoff statement — reproduce verbatim

> M03 Unit 6 taught HPA/VPA and introduced Cluster Autoscaler and Karpenter as Awareness (the pending-pod → new-node loop), explicitly deferring capacity-aware autoscaling and cost trade-offs to M15. The stage tooling map lists Cluster Autoscaler as "not feasible free": actual node provisioning requires a compatible infrastructure provider. This unit teaches **node provisioning architecture, decision logic, configuration, failure modes, and cost guardrails**, with **hands-on only through simulation** (kwok-based simulated nodes where feasible, plus a learner-built scheduling simulator) — it never claims real-provider behavior from the lab.

### Cross-module handoff map

| Earlier/later module | Reuse here | Boundary |
|---|---|---|
| M03 Unit 2 | Requests/limits, QoS, quotas, priorities, placeholders and right-sizing | Do not re-teach resource basics |
| M03 Unit 5 | PDBs, drain and disruption safety | Apply to consolidation; do not imply PDBs block involuntary node loss |
| M03 Unit 6 | HPA/VPA and introductory autoscaler concepts | Teach node provisioning and cost/reliability controls |
| M03 Unit 7 | Taints, tolerations, affinity, labels and pools | Reuse scheduling vocabulary |
| M10 Unit 6 | Queueing, latency knee, N−1 headroom, traffic ramps and catch-up | Use to judge scale-out timing |
| M11 Units 9/13 | Saturation, traffic traces, latency distributions and load testing | Use measured or synthetic time budgets; no fake benchmark claims |
| M12 Unit 7 | Node image patching, rotation and drift | Apply staged rollout and blast-radius controls |
| M12 security modules | Admission, RBAC, audit and policy-as-code | Apply to autoscaler/NodePool mutation |
| M14 | Multi-cluster/region capacity and failover | Do not duplicate multi-cluster curriculum |
| M15 Units 1–2 | Forecast/headroom, quotas, priorities, contention and requests accuracy | Reuse the capacity and governance model |
| M15 Unit 8 | Spot/on-demand capacity types | Refer to eligibility/fallback; do not repeat Unit 8 |
| M15 Unit 10 | KEDA creates/scales pods from event sources | Node provisioning remains a separate layer |
| M15 Unit 11 | OpenCost visibility | Simulator HCU is not billing or invoice data |
| M15 Unit 12 | GPU requests and fragmentation | GPU economics/sharing is expanded there |
| M16 | Golden paths and developer platform | Forward reference only |

### Running data/ML platform example

- `inference-api`: latency-sensitive replicated service.
- `batch-etl`: restartable batch workload.
- `stream-consumer`: queue-driven worker with freshness requirements.
- `training-job`: long-running ML workload; GPU needs are synthetic extended resources.
- `notebooks`: interactive workloads with uncertain demand.
- `metadata-db`: shared dependency with finite connection capacity.
- `platform-services`: system DaemonSets, CNI/CSI and observability agents.

### Evidence labels

- `[ASSUMPTION]` — model input selected by the learner; explain why and who owns it.
- `[ILLUSTRATIVE]` — sample policy/threshold, not a universal recommendation.
- `[SYNTHETIC]` — generated input, simulated event or simulator result.
- `[HYPOTHETICAL]` — HCU rate or cost assumption, never a provider quote.
- `[MEASURED — YOUR ENVIRONMENT]` — actually measured by the learner, with command, timestamp and environment.
- `[VERIFY]` — provider-, project-, version-, API-, flag-, field- or metric-specific detail requiring current official verification.
- `[VERSION-SENSITIVE]` — syntax/behavior tied to a specific release/API.

### Zero-budget and safety contract

1. **No real cloud provisioning.** No cloud API calls, credentials, billable VMs, provider node pools, real GPU resources or paid services are needed or permitted in these labs.
2. `kind` nodes are local containers, not cloud VMs. KWOK nodes are simulated Kubernetes objects without real kubelets. Neither reproduces cloud capacity, API latency, billing or provider failure behavior.
3. The guaranteed path is the Python teaching simulator. It models selected scheduling and cost decisions; it is not a reimplementation of CA or Karpenter.
4. KWOK/provider integrations are optional only after verifying compatible versions and official installation instructions. A provider package in a repository does not prove production readiness.
5. All costs use HCU. No real provider rate card, discount, free-tier limit, instance specification or commercial term appears here.
6. Every fault is bounded and synthetic. No process kills, node deletes, cloud changes or production-context commands are required.
7. Every lab has preflight, scope, negative test, abort criteria, evidence, cleanup and cleanup verification.
8. If the laptop is constrained, complete Cap-Core first. Run one optional component at a time and stop it after evidence capture.
9. Never raise a ceiling automatically when reached. Diagnose, protect critical workloads, and obtain an owner-approved decision.
10. Never optimize utilization at the expense of an SLO, data durability, security or recovery margin.

---

## Unit 9 — Karpenter and Cluster Autoscaler node provisioning

### 9.0 Why this matters in production

A pod can remain `Pending` even when an HPA correctly increases replicas, because no existing node has enough compatible capacity. Node autoscaling helps only when a feasible node shape exists and the provisioning system is allowed and able to supply it. Incorrect requests, impossible selectors, quota ceilings, capacity shortages, bootstrap failures or overlapping autoscalers can all cause pending workloads or runaway node growth. This unit teaches how to distinguish those causes before changing capacity or cost limits.

### 9.1 Learning objectives

1. **[L1]** Explain pod-level autoscaling versus node-level provisioning.
2. **[L1]** Describe CA node-group expansion and Karpenter-style flexible provisioning without claiming feature parity.
3. **[L1]** Trace the pending-pod-to-ready-workload critical path and identify what simulation omits.
4. **[L2]** Build/test a Python simulator for node groups, flexible shapes, resource fit, constraints, ceilings and HCU.
5. **[L2]** Demonstrate scale-up, scale-down blockers, ceiling hits, impossible constraints and policy comparison.
6. **[L2/L3]** Quantify bin-packing, stranded capacity, right-sizing impact and HCU per workload unit.
7. **[L3]** Design safe ceilings, disruption/consolidation policies, fallback, quota headroom and denial-of-wallet controls.
8. **[L3/L4]** Diagnose capacity, quota, permission, node-join and controller-overlap failures using evidence/runbooks.
9. **[L4]** Define policy-as-code, least privilege, ownership, SLOs, dashboards, alerts and review cadence.

### 9.2 Concept map and vocabulary

```text
Demand / traffic / queue
          |
          v
Pod-level autoscaler (HPA / KEDA / VPA inputs)
          |
          v
New or larger pod requests
          |
          v
Kubernetes scheduler evaluates existing nodes
          |
      +---+----------------------+
      |                          |
      v                          v
Pod fits existing node      Pod remains Pending
                                 |
                                 v
                        Node autoscaler observes
                                 |
                    +------------+-------------+
                    |                          |
                    v                          v
             CA-style node groups      Karpenter-style flexible
             predefined shapes         NodePool + candidate catalog
                    |                          |
                    +------------+-------------+
                                 |
                                 v
                    Capacity / quota / policy checks
                                 |
                                 v
                      Node provision decision
                                 |
                                 v
          API -> boot -> kubelet -> CNI/CSI -> Ready
                                 |
                                 v
                scheduler places pod / image starts
                                 |
                                 v
             SLO, utilization, cost and disruption review
```

**Owners/data:** workload teams own accurate requests and SLOs; platform owns node pools/autoscaler policy; SRE owns reliability/disruption review; FinOps owns HCU assumptions and allocation. Data comes from pod specs/events, scheduler events, node conditions, controller logs, load tests, synthetic traces and cost assumptions.

| Term | Precise definition | Common misconception |
|---|---|---|
| Pod autoscaling | Changes workload pod count or resource requests | It creates nodes |
| Node autoscaling | Adds/removes nodes so pods can schedule and unused capacity can be removed | It can satisfy any constraint |
| Unschedulable pod | Scheduler finds no feasible node | Every pending pod is a CPU shortage |
| Node group | Preconfigured group of similar node shape/configuration | All groups are interchangeable |
| Expander | CA selection policy among candidate groups | Universal price optimizer |
| NodePool | Karpenter policy for node requirements, limits and disruption | Provider VM group of identical size |
| NodeClaim | Karpenter-managed representation of requested/provisioned node | A resource users normally create by hand |
| NodeClass | Provider-specific launch configuration | Portable Kubernetes API object |
| Bin-packing | Assigning workloads to node capacity while satisfying constraints | Packing by CPU only |
| Fragmentation | Free resources exist in aggregate but not in a compatible combination on one node | Aggregate free CPU guarantees schedulability |
| Allocatable | Capacity available to pods after system reservations/overhead | Physical capacity equals pod capacity |
| Stranded capacity | Allocatable resources left unused due to fit/shape/placement | All unused resources are safely removable |
| Consolidation | Removing/replacing nodes when workloads can safely fit elsewhere | Delete every low-utilization node |
| Drift | Existing nodes no longer match selected desired configuration | Every node update is harmless |
| Disruption budget | Limit on selected voluntary disruption actions | Guarantees workload availability |
| Ceiling | Hard policy maximum on nodes/resources or external quota | Raising it is the default fix |
| Scale-up latency | Demand signal to usable application capacity | VM object creation time only |
| Impossible constraint | No allowed node can satisfy hard selector/affinity/taint/topology/storage need | A larger node will fix it |
| HCU | Hypothetical teaching unit for modeled node-time cost | Real bill/provider rate |

#### Pod autoscaling versus node autoscaling

HPA changes pod replicas. KEDA can activate/scale workloads from event-source metrics (Unit 10 owns its detailed behavior). VPA can recommend/change requests within its supported mode (M03 Unit 6 owns its fundamentals). CA/Karpenter/node autoscaling addresses **node capacity** required by pending pods. The layers interact but solve different problems.

#### Cluster Autoscaler: node-group model

At a high level, CA observes pods the scheduler cannot place, simulates whether adding a node from a configured group would make them schedulable, and selects a compatible group to expand. It generally works with predefined node groups supplied by a provider integration. Scale-down considers whether nodes are unneeded and whether their pods can be moved safely.

- Candidate groups must match pod resources and scheduling constraints.
- Minimum/maximum group sizes bound the permitted group range; maximum is a hard ceiling.
- Expanders select among candidates. Current docs show options such as `random`, `most-pods`, `least-waste`, `priority` and custom/provider-specific options `[VERIFY]`; support varies by release/provider.
- Scale-down can be affected by requests-based utilization, PDBs, eviction constraints, local storage, system pods, DaemonSets and unneeded-time/cooldown controls `[VERIFY]`. Requests-based utilization is not the same as actual CPU/memory use. One non-evictable pod can keep a node from being removable; DaemonSet-only nodes and local storage need release-specific handling. Verify exact flags/defaults and unneeded-time semantics for the deployed CA/provider version.
- Do not copy CA flags/defaults from old articles. Record the exact Kubernetes/CA/provider compatibility and consult the matching official docs.

#### Karpenter: flexible node-provisioning model

Karpenter watches unschedulable pods and evaluates requests/constraints against NodePool constraints and a provider capacity catalog. It can select among flexible shapes rather than requiring every shape to be preconfigured as a fixed group.

- **NodePool:** policy boundary for requirements, labels/taints, limits and disruption behavior.
- **NodeClaim:** controller-managed desired/actual node provisioning object. Its lifecycle exposes launch, registration, initialization and Ready states; these help localize whether failure occurred before the node existed, before it joined, or before its resources became usable.
- **NodeClass:** provider-specific launch configuration. `EC2NodeClass` is AWS-provider-specific; not portable Kubernetes syntax `[VERIFY]`.
- **Requirements:** resource requests, node selectors/affinity, topology, taints/tolerations, zone and capacity type.
- **Consolidation:** remove empty nodes or move workloads to fewer/other nodes when safe and beneficial. Current documentation describes `WhenEmpty` and `WhenEmptyOrUnderutilized` policies; exact availability/semantics are release-sensitive `[VERIFY]`.
- **Disruption budgets:** can constrain selected voluntary disruption reasons and support count/percentage/schedule-based limits in current documentation; verify exact fields and semantics for the installed release. Current docs describe reason categories such as `Drifted`, `Underutilized`, `Empty` and `Unhealthy`. Budgets do not erase PDB semantics, do not block every forceful method (for example expiry), and do not guarantee no disruption.
- **Drift/expiry/repair and empty-node timing:** version/provider-sensitive lifecycle mechanisms. `consolidateAfter`, `expireAfter`, termination grace and drift behavior have different meanings; verify exact fields and whether the action is graceful or forceful before relying on them.

The current Kubernetes SIG Autoscaling page lists both Cluster Autoscaler and Karpenter among its subprojects. This is a current project-ownership observation, not a guarantee about every provider implementation or support level.

#### Managed alternatives — awareness only

Examples include EKS managed node groups, GKE node auto-provisioning/Autopilot, AKS node autoprovisioning and EKS Auto Mode. Names, capability boundaries, availability and terms are provider/time-dependent `[VERIFY]`. Do not claim feature parity. Compare operational burden, supported shapes, control, lock-in, policy integration, upgrade responsibility and SLO needs.

#### Scale-out critical path

```text
Pending pod -> scheduler event -> autoscaler observation/decision
 -> provider API request (real cloud only; not called in this unit)
 -> node boot/bootstrap -> kubelet registration -> CNI/CSI ready
 -> node Ready -> pod scheduling -> image pull -> container start
 -> application warm-up/readiness
```

A VM existing is not usable application capacity. The critical path can include controller queues, API retries, bootstrap, CNI/CSI, DaemonSets, image pulls and model/cache warm-up. Exact timing is workload/provider-specific and is not asserted here. Compare measured or explicitly synthetic stage durations with traffic ramp and SLO. HPA can create pods faster than nodes become usable; placeholders, pre-scaling, queueing or load shedding may be necessary.

#### Why real node provisioning is not a free lab

Real CA/Karpenter provisioning requires a compatible infrastructure provider and permission to create/terminate infrastructure. Those nodes are billable. A local kind cluster does not contain a cloud provider capable of creating genuine instances. KWOK simulates Kubernetes node/pod objects but does not create actual kubelets or cloud VMs. This unit therefore uses a learner-built simulator as its guaranteed hands-on path.

#### KWOK feasibility boundary

KWOK is an official Kubernetes SIGs project for simulating fake nodes and pods. Current CA project documentation lists a `kwok` cloud-provider option, and the Karpenter repository documents a KWOK provider workflow. This makes a KWOK route worth checking, but does not prove the learner's versions are compatible or that every provider path is production-ready. The current Karpenter KWOK provider instructions warn not to have an installed Karpenter version in the target cluster before using that provider workflow; use a dedicated disposable cluster and follow its exact release instructions `[VERIFY]`. Its documented path requires a cluster and an image repository able to build/push/pull the controller images; it can use a custom fake instance-type catalog. KWOK-only labels/catalog entries are not valid for a real Karpenter provider. The package page also warns that the displayed package snapshot is not necessarily the module's latest version, so resolve the current release before using it. Never combine the simulator provider with a real cloud provider in the same lab. Lab 1 records the path decision. In the authoring environment, `kind`, `kubectl`, Docker/Podman, KWOK and `promtool` were absent; only the Python simulator path was selected.

### 9.3 Level 1 — Beginner

#### 9.3.1 Why a pod becomes Pending

The scheduler evaluates a pod against nodes using requests and hard constraints. It needs a **single compatible node** with sufficient allocatable CPU, memory and extended resources, plus matching labels, taints/tolerations, affinity, topology and storage placement.

| Pending cause | Example | Can node autoscaler help? |
|---|---|---|
| Insufficient CPU/memory | No compatible node has sufficient free allocatable resources | Possibly, if an allowed shape can fit |
| GPU/extended resource | Pod requests GPU but no allowed node exposes it | Only if pool/catalog supports it |
| Missing node label | Requires `accelerator=type-x`, no candidate has it | No, unless catalog/policy changes |
| Taint not tolerated | Candidate nodes carry an untolerated taint | No, until workload/pool contract is corrected |
| Zone/PVC conflict | Storage bound to zone with no allowed node shape | No, unless topology/storage design permits it |
| Max nodes/resource limit | Pool reached configured ceiling | Not until approved limit/quota decision changes |
| Provider quota/capacity | Provider cannot allocate requested capacity | Not by retrying same request |
| Node join/bootstrap failure | Resource exists but does not register/turn Ready | Not by blindly creating more nodes |

**Critical distinction:** “No current node fits” is not enough. Determine whether the cause is a shortage of compatible capacity or an unsatisfiable constraint.

#### Scheduling inputs that change node count

- **Requests:** scheduler fit is based on requests and allocatable capacity, not a simple live-usage average. Over-requesting can force larger/more nodes; under-requesting can create saturation after placement.
- **DaemonSets/system reservations:** every new node reserves resources for system agents; model this per node.
- **PodPriority/preemption:** priority can affect scheduling order and whether lower-priority pods may be preempted. Preemption does not create capacity and must not be treated as a substitute for a correct node plan `[VERIFY]` for exact controller behavior.
- **Pod anti-affinity and PodTopologySpread:** can deliberately prevent packing several replicas on one node/zone, increasing required nodes. The teaching simulator does not implement full inter-pod affinity or topology-spread scoring.
- **Taints/tolerations and labels:** can make otherwise large nodes unusable to a workload.
- **GPU/extended resources:** integer resource fit, taints and device/driver compatibility matter; aggregate GPU count is not enough.
- **PDBs:** influence voluntary eviction/consolidation safety, not initial CPU fit.

Node-pool-per-class provides clearer isolation and budgets; a shared pool can improve packing but needs stronger tenancy, priority, labels and quota controls. A common separation is a stable on-demand tier-0/system pool, a checkpointed batch spot pool (Unit 8), a separately governed GPU pool and a general-purpose pool. Larger nodes reduce per-node overhead but increase failure blast radius; topology spread/PDBs can contain impact. Smaller nodes reduce per-node blast radius but may increase DaemonSet overhead and fragmentation. Balance equivalent node-group capacity across zones where the provider/controller supports it `[VERIFY]`. Choose by workload isolation, capacity diversity and governance rather than a blanket rule.

#### 9.3.2 Worked example 1 — resource shortage versus impossible selector

`[SYNTHETIC]` Catalog: `general-small` has 3,900m allocatable CPU and 8,064 MiB allocatable memory; `general-large` has 7,900m and 16,256 MiB. Pod A requests 3,000m CPU and 12,000 MiB memory: small cannot fit memory, large can. This is a resource-fit problem if no free compatible node exists. Pod B requests 500m/512 MiB and requires `accelerator=type-x`; neither candidate has the label. This is impossible under the current catalog. More general nodes do not solve it.

Correct diagnostic order: inspect pod events/spec; compare hard constraints to allowed node catalog; decide whether to add compatible capacity or correct the workload/pool contract.

#### 9.3.3 Worked example 2 — fragmentation

`[SYNTHETIC]` Two nodes each have `2,000m` CPU free. Aggregate free CPU is `4,000m`. A pod requests `2,500m`; neither node can fit it, even though aggregate free CPU exceeds the request. Scheduling requires a compatible per-node fit, not a sum across nodes. Memory, GPU count, zone, taints and topology create the same effect.

#### 9.3.4 What CA and Karpenter optimize

| Dimension | CA-style node groups | Karpenter-style flexible provisioning |
|---|---|---|
| Capacity choices | Predefined groups/shapes | Candidate shapes constrained by NodePool/provider catalog |
| Scale-up | Select a group that can fit pending pods | Select compatible shape(s) for pending requirements |
| Strength | Explicit node-group boundaries | Flexible shape selection/consolidation |
| Trade-off | Group sprawl and stranded capacity | Provider-specific policy complexity and heterogeneity |
| Limitation | Cannot fix impossible constraints or quota | Cannot fix impossible constraints, unavailable capacity or invalid provider config |

This is conceptual. The simulator is not a product implementation.

#### 9.3.5 Guided simulator walkthrough

Create the workspace and files shown in Level 2. Then run:

```bash
# Run from the workspace root.
python --version
python -m src.lab_runner preflight
python -m src.lab_runner pending
```

Representative output — yours will differ:

```text
kind: not found
kubectl: not found
kwok: not found
cloud_api_calls: disabled
selected_path: Python teaching simulator
nodes=1, scheduled=['etl-batch']
simulated_decision_latency_minutes=0.5
simulated_ready_at_minute=4.5
negative_test_pending={'oversized': 'no_shape_fits_resources'}
```

Interpretation: the simulator can represent a node decision and synthetic ready time. It does not create a node or wait for real bootstrap.

#### 9.3.6 Common beginner mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Every Pending pod is treated as CPU shortage | More nodes change nothing | Inspect scheduler reason and hard constraints |
| Assume HPA creates nodes | Replicas increase but remain Pending | Add node provisioning layer or stable capacity |
| Use aggregate free CPU only | Large pod remains Pending | Inspect per-node CPU/memory/GPU/constraints |
| Increase max nodes first | Spend exposure grows without fixing root cause | Check catalog, selectors, quota and requests |
| Use stale requests | Over-requesting adds nodes; under-requesting risks saturation | Right-size from percentiles and load tests |
| Assume kind is cloud | Local node appears but no provider VM exists | State exactly what is simulated |
| Overlap controllers | Competing scale-up/down decisions | Define disjoint capacity ownership |

### 9.4 Level 2 — Intermediate

#### 9.4.1 Guaranteed simulator implementation

The simulator uses only Python's standard library. It represents node shapes, pod requests/constraints, CA-like predefined groups, Karpenter-like flexible selection, synthetic readiness, utilization, stranded resources and HCU. It deliberately does **not** implement the Kubernetes scheduler, CA or Karpenter internals. It uses a simple greedy best-fit heuristic and deterministic traces. `PoolPolicy.max_memory_mib` and `.max_gpu` are teaching-policy fields, not claims about Karpenter CRD field names; only the provider/version-verified fields in the separate NodePool example are shown as Kubernetes API syntax. The example allowlists are synthetic platform policy, not a universal provider catalog.

```python
# File: src/__init__.py
# Empty package marker.
```

```python
# File: src/simulator.py
"""Teaching model, not Cluster Autoscaler or Karpenter. No cloud API calls."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple
import random


@dataclass(frozen=True)
class NodeShape:
    name: str
    family: str
    cpu_m: int
    memory_mib: int
    gpu: int
    zone: str
    capacity_type: str
    rate_hcu_per_hour: float
    labels: Tuple[Tuple[str, str], ...] = ()
    taints: Tuple[str, ...] = ()
    daemon_cpu_m: int = 100
    daemon_memory_mib: int = 128

    @property
    def allocatable_cpu_m(self) -> int:
        return self.cpu_m - self.daemon_cpu_m

    @property
    def allocatable_memory_mib(self) -> int:
        return self.memory_mib - self.daemon_memory_mib


@dataclass(frozen=True)
class PodRequest:
    name: str
    cpu_m: int
    memory_mib: int
    gpu: int = 0
    required_labels: Tuple[Tuple[str, str], ...] = ()
    tolerations: Tuple[str, ...] = ()
    zone: Optional[str] = None
    pvc_zone: Optional[str] = None
    safe_to_evict: bool = True
    pdb_blocked: bool = False
    local_storage: bool = False
    do_not_disrupt: bool = False
    priority: int = 0
    workload: str = "batch"


@dataclass
class Node:
    name: str
    shape: NodeShape
    ready_at_minute: float
    created_at_minute: float = 0.0
    pods: List[PodRequest] = field(default_factory=list)

    @property
    def used_cpu_m(self) -> int:
        return sum(p.cpu_m for p in self.pods)

    @property
    def used_memory_mib(self) -> int:
        return sum(p.memory_mib for p in self.pods)

    @property
    def used_gpu(self) -> int:
        return sum(p.gpu for p in self.pods)

    @property
    def cpu_utilization(self) -> float:
        return self.used_cpu_m / self.shape.allocatable_cpu_m if self.shape.allocatable_cpu_m > 0 else 0.0

    @property
    def memory_utilization(self) -> float:
        return self.used_memory_mib / self.shape.allocatable_memory_mib if self.shape.allocatable_memory_mib > 0 else 0.0

    @property
    def stranded_cpu_m(self) -> int:
        return self.shape.allocatable_cpu_m - self.used_cpu_m

    @property
    def stranded_memory_mib(self) -> int:
        return self.shape.allocatable_memory_mib - self.used_memory_mib


@dataclass(frozen=True)
class NodeGroup:
    name: str
    shape: NodeShape
    min_nodes: int
    max_nodes: int
    priority: int = 0


@dataclass(frozen=True)
class PoolPolicy:
    name: str
    max_nodes: int
    allowed_families: Tuple[str, ...]
    allowed_capacity_types: Tuple[str, ...]
    max_cpu_m: Optional[int] = None
    owner: str = "platform"
    max_memory_mib: Optional[int] = None
    max_gpu: Optional[int] = None


@dataclass
class SimulationResult:
    policy: str
    nodes: List[Node]
    scheduled: Dict[str, str]
    pending: Dict[str, str]
    decision_log: List[str]
    decision_latency_minutes: List[float]
    total_hcu: float
    duration_hours: float

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def allocatable_cpu_m(self) -> int:
        return sum(n.shape.allocatable_cpu_m for n in self.nodes)

    @property
    def used_cpu_m(self) -> int:
        return sum(n.used_cpu_m for n in self.nodes)

    @property
    def allocatable_memory_mib(self) -> int:
        return sum(n.shape.allocatable_memory_mib for n in self.nodes)

    @property
    def used_memory_mib(self) -> int:
        return sum(n.used_memory_mib for n in self.nodes)

    @property
    def cpu_utilization(self) -> float:
        return self.used_cpu_m / self.allocatable_cpu_m if self.allocatable_cpu_m else 0.0

    @property
    def memory_utilization(self) -> float:
        return self.used_memory_mib / self.allocatable_memory_mib if self.allocatable_memory_mib else 0.0

    @property
    def stranded_cpu_m(self) -> int:
        return self.allocatable_cpu_m - self.used_cpu_m

    @property
    def stranded_memory_mib(self) -> int:
        return self.allocatable_memory_mib - self.used_memory_mib


def shape_fits_constraints(shape: NodeShape, pod: PodRequest) -> Tuple[bool, str]:
    labels = dict(shape.labels)
    for key, value in pod.required_labels:
        if labels.get(key) != value:
            return False, f"label:{key}={value}"
    if pod.zone and shape.zone != pod.zone:
        return False, f"zone:{pod.zone}"
    if pod.pvc_zone and shape.zone != pod.pvc_zone:
        return False, f"pvc-zone:{pod.pvc_zone}"
    missing = set(shape.taints) - set(pod.tolerations)
    if missing:
        return False, "taint:" + ",".join(sorted(missing))
    return True, ""


def shape_fits_resources(shape: NodeShape, pod: PodRequest) -> bool:
    return (pod.cpu_m <= shape.allocatable_cpu_m
            and pod.memory_mib <= shape.allocatable_memory_mib
            and pod.gpu <= shape.gpu)


def pod_feasibility(pod: PodRequest, catalog: Sequence[NodeShape]) -> Tuple[bool, str]:
    compatible = [s for s in catalog if shape_fits_constraints(s, pod)[0]]
    if not compatible:
        return False, "impossible_constraints"
    if not any(shape_fits_resources(s, pod) for s in compatible):
        return False, "no_shape_fits_resources"
    return True, "provisionable"


def node_can_fit(node: Node, pod: PodRequest, now_minute: float) -> bool:
    # Planned capacity can be assigned before synthetic ready_at; not live scheduling.
    if not shape_fits_constraints(node.shape, pod)[0]:
        return False
    return (node.used_cpu_m + pod.cpu_m <= node.shape.allocatable_cpu_m
            and node.used_memory_mib + pod.memory_mib <= node.shape.allocatable_memory_mib
            and node.used_gpu + pod.gpu <= node.shape.gpu)


def place_on_existing(nodes: Sequence[Node], pod: PodRequest, now_minute: float) -> Optional[Node]:
    candidates = [n for n in nodes if node_can_fit(n, pod, now_minute)]
    if not candidates:
        return None
    return min(candidates, key=lambda n:
        (n.shape.allocatable_cpu_m - n.used_cpu_m - pod.cpu_m) / max(1, n.shape.allocatable_cpu_m)
        + (n.shape.allocatable_memory_mib - n.used_memory_mib - pod.memory_mib) / max(1, n.shape.allocatable_memory_mib))


def resource_waste(shape: NodeShape, pod: PodRequest) -> float:
    cpu = (shape.allocatable_cpu_m - pod.cpu_m) / max(1, shape.allocatable_cpu_m)
    mem = (shape.allocatable_memory_mib - pod.memory_mib) / max(1, shape.allocatable_memory_mib)
    gpu = 0.0 if shape.gpu == 0 else (shape.gpu - pod.gpu) / max(1, shape.gpu)
    return cpu + mem + gpu


def simulate_ca(pods: Sequence[PodRequest], groups: Sequence[NodeGroup],
                boot_delay_minutes: float = 4.0, duration_hours: float = 1.0,
                expander: str = "least-waste", max_total_nodes: Optional[int] = None,
                seed: int = 7, decision_latency_minutes: float = 0.5) -> SimulationResult:
    """CA-like policy: provision only from predeclared node groups."""
    if boot_delay_minutes < 0 or decision_latency_minutes < 0 or duration_hours <= 0:
        raise ValueError("invalid simulation duration")
    if any(g.min_nodes < 0 or g.max_nodes < g.min_nodes for g in groups):
        raise ValueError("invalid node-group min/max")
    min_total = sum(g.min_nodes for g in groups)
    if max_total_nodes is not None and min_total > max_total_nodes:
        raise ValueError("node-group minimums exceed cluster node ceiling")
    nodes: List[Node] = []
    counts = {g.name: 0 for g in groups}
    scheduled: Dict[str, str] = {}
    pending: Dict[str, str] = {}
    decisions: List[str] = []
    decision_times: List[float] = []
    rng = random.Random(seed)
    next_id = 1
    for group in groups:
        for _ in range(group.min_nodes):
            nodes.append(Node(f"ca-node-{next_id}", group.shape, 0.0))
            next_id += 1
            counts[group.name] += 1
    for pod in pods:
        existing = place_on_existing(nodes, pod, 0.0)
        if existing:
            existing.pods.append(pod)
            scheduled[pod.name] = existing.name
            continue
        constraint_matches = [g for g in groups if shape_fits_constraints(g.shape, pod)[0]]
        if not constraint_matches:
            pending[pod.name] = "impossible_constraints"
            decisions.append(f"{pod.name}: no group satisfies hard constraints")
            continue
        resource_matches = [g for g in constraint_matches if shape_fits_resources(g.shape, pod)]
        if not resource_matches:
            pending[pod.name] = "no_shape_fits_resources"
            decisions.append(f"{pod.name}: no configured group shape fits requests")
            continue
        candidates = [g for g in resource_matches if counts[g.name] < g.max_nodes]
        if not candidates:
            pending[pod.name] = "node_group_or_cluster_ceiling"
            decisions.append(f"{pod.name}: compatible group ceiling reached")
            continue
        if max_total_nodes is not None and len(nodes) >= max_total_nodes:
            pending[pod.name] = "cluster_node_ceiling"
            decisions.append(f"{pod.name}: cluster node ceiling reached")
            continue
        if expander == "priority":
            chosen = max(candidates, key=lambda g: (g.priority, -resource_waste(g.shape, pod)))
        elif expander == "random":
            chosen = rng.choice(sorted(candidates, key=lambda g: g.name))
        elif expander == "least-waste":
            chosen = min(candidates, key=lambda g: (resource_waste(g.shape, pod), g.shape.rate_hcu_per_hour, g.name))
        else:
            raise ValueError("expander must be least-waste, priority, or random")
        node = Node(f"ca-node-{next_id}", chosen.shape,
                    decision_latency_minutes + boot_delay_minutes,
                    created_at_minute=decision_latency_minutes)
        next_id += 1
        nodes.append(node)
        counts[chosen.name] += 1
        decision_times.append(decision_latency_minutes)
        decisions.append(f"{pod.name}: group={chosen.name}, shape={chosen.shape.name}, decision={decision_latency_minutes:.1f}m, ready_at={node.ready_at_minute:.1f}m")
        node.pods.append(pod)
        scheduled[pod.name] = node.name
    total = sum(n.shape.rate_hcu_per_hour for n in nodes) * duration_hours
    return SimulationResult("CA-like", nodes, scheduled, pending, decisions, decision_times, total, duration_hours)


def simulate_karpenter_like(pods: Sequence[PodRequest], catalog: Sequence[NodeShape],
                            boot_delay_minutes: float = 4.0, duration_hours: float = 1.0,
                            max_nodes: int = 10, allowed_families: Optional[Sequence[str]] = None,
                            allowed_capacity_types: Sequence[str] = ("on-demand", "spot"),
                            decision_latency_minutes: float = 0.5) -> SimulationResult:
    """Flexible-catalog teaching model; not a Karpenter implementation."""
    if boot_delay_minutes < 0 or decision_latency_minutes < 0 or duration_hours <= 0 or max_nodes < 0:
        raise ValueError("invalid simulation inputs")
    families = tuple(allowed_families or sorted({s.family for s in catalog}))
    nodes: List[Node] = []
    scheduled: Dict[str, str] = {}
    pending: Dict[str, str] = {}
    decisions: List[str] = []
    decision_times: List[float] = []
    for pod in pods:
        existing = place_on_existing(nodes, pod, 0.0)
        if existing:
            existing.pods.append(pod)
            scheduled[pod.name] = existing.name
            continue
        candidates = [s for s in catalog if s.family in families
                      and s.capacity_type in allowed_capacity_types
                      and shape_fits_constraints(s, pod)[0]]
        if not candidates:
            pending[pod.name] = "impossible_constraints"
            decisions.append(f"{pod.name}: no catalog candidate satisfies constraints")
            continue
        fitting = [s for s in candidates if shape_fits_resources(s, pod)]
        if not fitting:
            pending[pod.name] = "no_shape_fits_resources"
            decisions.append(f"{pod.name}: no candidate shape fits requests")
            continue
        if len(nodes) >= max_nodes:
            pending[pod.name] = "nodepool_ceiling"
            decisions.append(f"{pod.name}: NodePool node ceiling reached")
            continue
        chosen = min(fitting, key=lambda s: (resource_waste(s, pod), s.rate_hcu_per_hour, s.name))
        node = Node(f"karpenter-like-node-{len(nodes)+1}", chosen,
                    decision_latency_minutes + boot_delay_minutes,
                    created_at_minute=decision_latency_minutes)
        nodes.append(node)
        decision_times.append(decision_latency_minutes)
        decisions.append(f"{pod.name}: shape={chosen.name}, decision={decision_latency_minutes:.1f}m, ready_at={node.ready_at_minute:.1f}m")
        node.pods.append(pod)
        scheduled[pod.name] = node.name
    total = sum(n.shape.rate_hcu_per_hour for n in nodes) * duration_hours
    return SimulationResult("Karpenter-like", nodes, scheduled, pending, decisions, decision_times, total, duration_hours)


def consolidation_blockers(pods: Sequence[PodRequest]) -> List[str]:
    blockers = []
    for p in pods:
        if p.pdb_blocked: blockers.append(f"{p.name}:PDB")
        if not p.safe_to_evict: blockers.append(f"{p.name}:safe-to-evict=false")
        if p.local_storage: blockers.append(f"{p.name}:local-storage")
        if p.do_not_disrupt: blockers.append(f"{p.name}:do-not-disrupt")
    return blockers


def nodepool_policy_violations(
    policy: PoolPolicy,
    approved_families: Sequence[str] = ("general", "compute", "memory", "accelerated"),
    approved_capacity_types: Sequence[str] = ("on-demand", "spot"),
) -> List[str]:
    errors = []
    if not policy.owner.strip(): errors.append("owner_required")
    if policy.max_nodes <= 0: errors.append("max_nodes_must_be_positive")
    if not policy.allowed_families: errors.append("allowed_families_required")
    if not policy.allowed_capacity_types: errors.append("allowed_capacity_types_required")
    if policy.max_cpu_m is not None and policy.max_cpu_m <= 0: errors.append("max_cpu_must_be_positive")
    if policy.max_memory_mib is not None and policy.max_memory_mib <= 0: errors.append("max_memory_mib_must_be_positive")
    if policy.max_gpu is not None and policy.max_gpu < 0: errors.append("max_gpu_must_be_non_negative")
    if any(f not in approved_families for f in policy.allowed_families):
        errors.append("unsupported_family")
    if any(c not in approved_capacity_types for c in policy.allowed_capacity_types):
        errors.append("unsupported_capacity_type")
    if "spot" in policy.allowed_capacity_types and "on-demand" not in policy.allowed_capacity_types:
        errors.append("spot_only_requires_explicit_fallback_exception")
    return errors


def consolidation_candidate(cpu_utilization: float, utilization_threshold: float,
                            disruptions_in_progress: int, disruption_budget: int) -> str:
    """Simple teaching gate; not a controller's actual consolidation algorithm."""
    if not 0 <= cpu_utilization <= 1 or not 0 <= utilization_threshold <= 1:
        raise ValueError("utilization values must be between zero and one")
    if disruptions_in_progress < 0 or disruption_budget < 0:
        raise ValueError("disruption counts cannot be negative")
    if cpu_utilization > utilization_threshold:
        return "not_underutilized"
    if disruptions_in_progress >= disruption_budget:
        return "disruption_budget_exhausted"
    return "candidate_for_review"


def bounded_retry_delays(attempts: int, base_seconds: float = 1.0,
                         cap_seconds: float = 8.0) -> List[float]:
    """Deterministic backoff ceiling; real retries should add jitter."""
    if attempts < 0 or base_seconds <= 0 or cap_seconds <= 0:
        raise ValueError("invalid retry settings")
    return [min(cap_seconds, base_seconds * (2 ** min(i, 30))) for i in range(attempts)]


def scale_out_budget(hpa_reaction_min: float, autoscaler_decision_min: float,
                     node_boot_join_min: float, cni_csi_ready_min: float,
                     image_pull_start_min: float, app_warmup_min: float) -> Dict[str, float]:
    values = [hpa_reaction_min, autoscaler_decision_min, node_boot_join_min,
              cni_csi_ready_min, image_pull_start_min, app_warmup_min]
    if any(v < 0 for v in values):
        raise ValueError("stage durations cannot be negative")
    return {"hpa_reaction_min": hpa_reaction_min,
            "autoscaler_decision_min": autoscaler_decision_min,
            "node_boot_join_min": node_boot_join_min,
            "cni_csi_ready_min": cni_csi_ready_min,
            "image_pull_start_min": image_pull_start_min,
            "app_warmup_min": app_warmup_min,
            "end_to_end_min": sum(values)}
```

Create `src/lab_runner.py`:

```python
# File: src/lab_runner.py
"""CLI for the Unit 9 local teaching simulator."""
import argparse
import shutil
from src.simulator import (NodeShape, PodRequest, NodeGroup, PoolPolicy,
    simulate_ca, simulate_karpenter_like, consolidation_blockers,
    nodepool_policy_violations, scale_out_budget, consolidation_candidate,
    bounded_retry_delays)

SMALL = NodeShape("general-small", "general", 4000, 8192, 0, "zone-a", "on-demand", 3.0,
                  (("pool", "general"),))
LARGE = NodeShape("general-large", "general", 8000, 16384, 0, "zone-a", "on-demand", 5.0,
                  (("pool", "general"),))


def preflight():
    for name in ("python", "kind", "kubectl", "docker", "podman", "kwok", "kwokctl", "promtool"):
        print(f"{name}: {shutil.which(name) or 'not found'}")
    print("cloud_api_calls: disabled")
    print("selected_path: Python teaching simulator")
    print("fidelity: no real nodes, provider APIs, boot times, quotas, capacity, or billing")


def pending():
    r = simulate_karpenter_like([PodRequest("etl-batch", 3000, 12000)], [LARGE], boot_delay_minutes=4)
    print(f"nodes={r.node_count}, scheduled={sorted(r.scheduled)}")
    print(f"simulated_decision_latency_minutes={r.decision_latency_minutes[0]:.1f}")
    print(f"simulated_ready_at_minute={r.nodes[0].ready_at_minute:.1f}")
    r2 = simulate_karpenter_like([PodRequest("oversized", 9000, 20000)], [SMALL, LARGE])
    print(f"negative_test_pending={r2.pending}")


def consolidation():
    pods = [PodRequest("stateless", 500, 512),
            PodRequest("batch", 500, 512, safe_to_evict=False, local_storage=True),
            PodRequest("protected", 500, 512, pdb_blocked=True, do_not_disrupt=True)]
    print("low_util_candidate=" + consolidation_candidate(0.15, 0.40, 0, 1))
    print("budget_blocked=" + consolidation_candidate(0.15, 0.40, 1, 1))
    print("blockers=" + repr(consolidation_blockers(pods)))


def ceiling():
    pods = [PodRequest(f"job-{i}", 3000, 5000) for i in range(3)]
    r = simulate_ca(pods, [NodeGroup("fixed-small", SMALL, 0, 4)], max_total_nodes=1)
    print(f"nodes={r.node_count}, scheduled={sorted(r.scheduled)}, pending={r.pending}")


def impossible():
    pod = PodRequest("bad-selector", 500, 512, required_labels=(("accelerator", "special"),))
    r = simulate_karpenter_like([pod], [SMALL, LARGE])
    print(f"pending={r.pending}")
    print("interpretation=hard constraint has no matching catalog shape")


def compare():
    pods = [PodRequest("api-a", 1500, 3000), PodRequest("api-b", 1500, 3000),
            PodRequest("etl", 3000, 12000)]
    ca = simulate_ca(pods, [NodeGroup("general-8cpu", LARGE, 0, 4)], duration_hours=2)
    kp = simulate_karpenter_like(pods, [SMALL, LARGE], duration_hours=2)
    for r in (ca, kp):
        print(f"{r.policy}: nodes={r.node_count}, cpu_util={r.cpu_utilization:.3f}, "
              f"memory_util={r.memory_utilization:.3f}, stranded_cpu_m={r.stranded_cpu_m}, "
              f"stranded_memory_mib={r.stranded_memory_mib}, total_hcu={r.total_hcu:.1f}, "
              f"decision_latency_min={max(r.decision_latency_minutes, default=0):.1f}, "
              f"ready_at_minute={max((n.ready_at_minute for n in r.nodes), default=0):.1f}, "
              f"simulated_disruptions=0")


def rightsize():
    over = [PodRequest(f"svc-{i}", 2500, 1024) for i in range(6)]
    right = [PodRequest(f"svc-{i}", 1000, 1024) for i in range(6)]
    a = simulate_karpenter_like(over, [SMALL], duration_hours=1, max_nodes=10)
    b = simulate_karpenter_like(right, [SMALL], duration_hours=1, max_nodes=10)
    print(f"over_requested: nodes={a.node_count}, hcu={a.total_hcu:.1f}")
    print(f"right_sized: nodes={b.node_count}, hcu={b.total_hcu:.1f}")
    print("interpretation=synthetic request changes alter packing; validate SLO before adoption")


def denial_wallet():
    pods = [PodRequest(f"rogue-job-{i}", 3000, 4096) for i in range(8)]
    r = simulate_karpenter_like(pods, [SMALL, LARGE], max_nodes=2)
    print(f"node_count={r.node_count}, pending_count={len(r.pending)}")
    print(f"pending_reasons={r.pending}")


def failures():
    cases = {"capacity_unavailable": "bounded_backoff_and_approved_alternative_shape",
             "quota_exhausted": "stop_scale_up_alert_owner_and_request_approved_quota_review",
             "node_join_failure": "inspect_bootstrap_cni_csi_and_node_registration; do_not_loop_create"}
    for reason, action in cases.items(): print(f"[SYNTHETIC] {reason} -> {action}")
    print("bounded_retry_delays_seconds=" + repr(bounded_retry_delays(5, 1, 8)))


def scaleout():
    r = scale_out_budget(1.5, 0.5, 4.0, 1.0, 2.0, 1.0)
    print("stage_minutes=" + repr(r))
    print("interpretation=synthetic total compared with traffic-ramp budget")


def security():
    good = PoolPolicy("batch", 4, ("general",), ("on-demand", "spot"),
                      16000, "data-platform", 65536, 0)
    bad = PoolPolicy("unbounded", 0, ("ultra" ,), ("spot", "magic"),
                     0, "", 0, -1)
    print(f"good_policy_violations={nodepool_policy_violations(good)}")
    print(f"bad_policy_violations={nodepool_policy_violations(bad)}")


SCENARIOS = {"preflight": preflight, "pending": pending, "consolidation": consolidation,
             "ceiling": ceiling, "impossible": impossible, "compare": compare,
             "rightsize": rightsize, "denial-wallet": denial_wallet, "failures": failures,
             "scaleout": scaleout, "security": security}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unit 9 local teaching simulator")
    parser.add_argument("scenario", choices=SCENARIOS)
    SCENARIOS[parser.parse_args().scenario]()
```

Create `tests/test_simulator.py`:

```python
# File: tests/test_simulator.py
import unittest
from src.simulator import (NodeShape, PodRequest, NodeGroup, PoolPolicy,
    simulate_ca, simulate_karpenter_like, pod_feasibility,
    consolidation_blockers, nodepool_policy_violations, scale_out_budget,
    consolidation_candidate, bounded_retry_delays)

SMALL = NodeShape("small", "general", 4000, 8192, 0, "zone-a", "on-demand", 3.0,
                  (("pool", "general"),))
LARGE = NodeShape("large", "general", 8000, 16384, 0, "zone-a", "on-demand", 5.0,
                  (("pool", "general"),))
GPU = NodeShape("gpu", "accelerated", 8000, 32768, 1, "zone-b", "on-demand", 9.0,
                (("pool", "gpu"),), ("gpu-only",))

class SimulatorTests(unittest.TestCase):
    def test_ca_group_scaleup(self):
        r = simulate_ca([PodRequest("p1", 3000, 4096)], [NodeGroup("g", SMALL, 0, 2)])
        self.assertEqual(r.node_count, 1); self.assertIn("p1", r.scheduled)

    def test_flexible_policy_selects_small_shape(self):
        r = simulate_karpenter_like([PodRequest("p1", 3000, 4096)], [SMALL, LARGE])
        self.assertEqual(r.nodes[0].shape.name, "small")

    def test_impossible_label(self):
        ok, reason = pod_feasibility(PodRequest("bad", 500, 512, required_labels=(("disk", "nvme"),)), [SMALL, LARGE])
        self.assertFalse(ok); self.assertEqual(reason, "impossible_constraints")

    def test_no_shape_fits_resources(self):
        ok, reason = pod_feasibility(PodRequest("huge", 9000, 20000), [SMALL, LARGE])
        self.assertFalse(ok); self.assertEqual(reason, "no_shape_fits_resources")

    def test_group_ceiling(self):
        r = simulate_ca([PodRequest("p", 3000, 4096)], [NodeGroup("g", SMALL, 0, 0)])
        self.assertEqual(r.pending["p"], "node_group_or_cluster_ceiling")

    def test_cluster_ceiling(self):
        pods = [PodRequest("p1", 3000, 4096), PodRequest("p2", 3000, 4096)]
        r = simulate_ca(pods, [NodeGroup("g", SMALL, 0, 3)], max_total_nodes=1)
        self.assertEqual(r.pending["p2"], "cluster_node_ceiling")

    def test_zero_cluster_ceiling(self):
        r = simulate_ca([PodRequest("p", 100, 100)], [NodeGroup("g", SMALL, 0, 2)], max_total_nodes=0)
        self.assertIn("p", r.pending)

    def test_taint_needs_toleration(self):
        ok, reason = pod_feasibility(PodRequest("gpu", 1000, 1024, gpu=1), [GPU])
        self.assertFalse(ok); self.assertEqual(reason, "impossible_constraints")

    def test_gpu_toleration(self):
        ok, reason = pod_feasibility(PodRequest("gpu", 1000, 1024, gpu=1, tolerations=("gpu-only",)), [GPU])
        self.assertTrue(ok); self.assertEqual(reason, "provisionable")

    def test_pvc_zone_mismatch(self):
        ok, reason = pod_feasibility(PodRequest("db", 1000, 1024, pvc_zone="zone-c"), [SMALL, GPU])
        self.assertFalse(ok); self.assertEqual(reason, "impossible_constraints")

    def test_consolidation_blockers(self):
        p = PodRequest("batch", 1000, 1024, pdb_blocked=True, local_storage=True)
        self.assertEqual(consolidation_blockers([p]), ["batch:PDB", "batch:local-storage"])

    def test_policy_rejects_unbounded_and_ownerless(self):
        errors = nodepool_policy_violations(PoolPolicy("bad", 0, (), ("spot",), 0, ""))
        self.assertIn("owner_required", errors); self.assertIn("max_nodes_must_be_positive", errors)
        self.assertIn("allowed_families_required", errors); self.assertIn("max_cpu_must_be_positive", errors)
        self.assertIn("spot_only_requires_explicit_fallback_exception", errors)

    def test_scaleout_sum(self):
        r = scale_out_budget(1, 0.5, 4, 1, 2, 1)
        self.assertEqual(r["end_to_end_min"], 9.5)

    def test_negative_stage_duration(self):
        with self.assertRaises(ValueError): scale_out_budget(1, -1, 4, 1, 2, 1)

    def test_invalid_expander(self):
        with self.assertRaises(ValueError):
            simulate_ca([PodRequest("p", 100, 100)], [NodeGroup("g", SMALL, 0, 2)], expander="magic")

    def test_invalid_simulation_duration(self):
        with self.assertRaises(ValueError): simulate_karpenter_like([], [SMALL], duration_hours=0)

    def test_group_minimum_baseline(self):
        r = simulate_ca([], [NodeGroup("g", SMALL, 1, 2)])
        self.assertEqual(r.node_count, 1)

    def test_group_minimum_exceeds_ceiling(self):
        with self.assertRaises(ValueError):
            simulate_ca([], [NodeGroup("g", SMALL, 2, 3)], max_total_nodes=1)

    def test_decision_latency_is_separate_from_node_ready_time(self):
        r = simulate_karpenter_like([PodRequest("p", 1000, 1000)], [SMALL],
                                    decision_latency_minutes=0.5, boot_delay_minutes=4)
        self.assertEqual(r.decision_latency_minutes, [0.5])
        self.assertEqual(r.nodes[0].ready_at_minute, 4.5)

    def test_negative_decision_latency_rejected(self):
        with self.assertRaises(ValueError):
            simulate_ca([PodRequest("p", 100, 100)], [NodeGroup("g", SMALL, 0, 1)],
                        decision_latency_minutes=-0.1)

    def test_ca_decision_latency_is_separate_from_ready_time(self):
        r = simulate_ca([PodRequest("p", 1000, 1000)], [NodeGroup("g", SMALL, 0, 1)],
                        decision_latency_minutes=0.5, boot_delay_minutes=4)
        self.assertEqual(r.decision_latency_minutes, [0.5])
        self.assertEqual(r.nodes[0].ready_at_minute, 4.5)

    def test_consolidation_underutilized_and_budget(self):
        self.assertEqual(consolidation_candidate(0.2, 0.4, 0, 1), "candidate_for_review")
        self.assertEqual(consolidation_candidate(0.2, 0.4, 1, 1), "disruption_budget_exhausted")
        self.assertEqual(consolidation_candidate(0.7, 0.4, 0, 1), "not_underutilized")

    def test_consolidation_rejects_invalid_utilization(self):
        with self.assertRaises(ValueError): consolidation_candidate(1.2, 0.4, 0, 1)

    def test_retry_backoff_is_bounded(self):
        self.assertEqual(bounded_retry_delays(5, 1, 8), [1, 2, 4, 8, 8])

    def test_retry_backoff_rejects_invalid_attempts(self):
        with self.assertRaises(ValueError): bounded_retry_delays(-1)

    def test_policy_rejects_memory_gpu_and_allowlist_violations(self):
        p = PoolPolicy("bad", 2, ("ultra",), ("magic",), 4000, "owner", 0, -1)
        errors = nodepool_policy_violations(p)
        self.assertIn("unsupported_family", errors)
        self.assertIn("unsupported_capacity_type", errors)
        self.assertIn("max_memory_mib_must_be_positive", errors)
        self.assertIn("max_gpu_must_be_non_negative", errors)

if __name__ == "__main__":
    unittest.main()
```

Run from workspace root:

```bash
python -m src.lab_runner compare
python -m unittest discover -s tests -v
```

Representative test output: `Ran 26 tests in <measured-duration>` followed by `OK`. This validates the included model only, not Kubernetes, CA, Karpenter or a provider integration.

#### 9.4.2 Synthetic comparison — predefined groups versus flexible catalog

`[SYNTHETIC]` Shapes: `general-small` = 4,000m CPU / 8,192 MiB / 0 GPU / 3 HCU per node-hour; `general-large` = 8,000m / 16,384 MiB / 0 GPU / 5 HCU per node-hour. The simulator subtracts `100m CPU` and `128 MiB` per node for DaemonSet/system overhead. Workload: `api-a` 1,500m/3,000 MiB; `api-b` 1,500m/3,000 MiB; `etl` 3,000m/12,000 MiB.

Representative output:

```text
CA-like: nodes=2, cpu_util=0.380, memory_util=0.554,
  stranded_cpu_m=9800, stranded_memory_mib=14512, total_hcu=20.0
Karpenter-like: nodes=2, cpu_util=0.508, memory_util=0.740,
  stranded_cpu_m=5800, stranded_memory_mib=6320, total_hcu=16.0
```

Both schedule three pods on two nodes. The fixed group uses two large shapes; the flexible model uses a small shape for the API pods and a large shape for ETL. The HCU difference is specific to this synthetic two-hour trace, not a claim that Karpenter always saves cost. The model omits provider capacity, real pricing, controller heuristics, API retries, network/storage and workload performance.

#### 9.4.3 CA-style node-group design

A node group needs an owner, workload class, compatible shape, labels/taints/zones, min/max size, quota relationship, ceiling, fallback policy and observability.

| Expander | Selection principle | Benefit | Limitation |
|---|---|---|---|
| `least-waste` | Lower estimated unused CPU/memory | Reduces simple resource waste | Does not necessarily minimize HCU or disruption |
| `priority` | Configured group ranking | Explicit workload-class policy | Bad ranking can overuse costly groups |
| `random` | Choose among candidates | Simple tie-break | No cost-aware preference |
| `most-pods` | Prefer group expected to schedule more pending pods | Can reduce pending backlog | Candidate simulation matters |
| Price/custom | Provider/extension-specific | May include rate information | Support is `[VERIFY]`; not assumed here |

The simulator implements `least-waste`, `priority` and seeded `random`; it does not implement all real CA expanders.

#### 9.4.4 Karpenter NodePool design example

The following is an **illustrative AWS-provider-specific design fragment**, not a complete deployable installation. It uses the Karpenter `NodePool` v1 API shape documented by the project; the referenced `EC2NodeClass` must exist and match the installed provider release. Do not apply it without version, provider, IAM, subnet, security group, image, quota and budget review.

```yaml
# File: manifests/nodepool-design-example.yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: data-batch
spec:
  template:
    metadata:
      labels:
        workload-class: batch
        owner: data-platform
    spec:
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
      taints:
        - key: workload-class
          value: batch
          effect: NoSchedule
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: reviewed-batch-class
  limits:
    cpu: "64"
  disruption:
    consolidationPolicy: WhenEmpty
    consolidateAfter: 5m
    budgets:
      - nodes: "1"
```

Review: `karpenter.sh/v1`, NodePool fields, limits and disruption settings are version-sensitive. `EC2NodeClass` is AWS-specific. CPU ceiling `64`, `5m` and `1` are `[ILLUSTRATIVE]`. CPU limit alone is not a complete cost guardrail: review memory/GPU, node count, allowed families/capacity types, quotas, namespace quotas, max replicas, HCU budget and alerts. Do not include static credentials or secrets.

#### 9.4.5 Scale-down and consolidation

Consolidation is a placement and disruption decision, not just a utilization threshold. Blockers may include PDBs, `safe-to-evict: "false"` where supported `[VERIFY]`, Karpenter `karpenter.sh/do-not-disrupt: "true"` `[VERSION-SENSITIVE]`, local storage, singleton/stateful workloads, DaemonSet overhead, topology/anti-affinity, disruption budgets and insufficient replacement headroom.

A PDB limits supported voluntary eviction; it is not a general guarantee against involuntary node loss. Karpenter NodePool disruption budgets and Kubernetes PDBs are separate controls. Expiration/forceful disruption behavior may differ from graceful consolidation; verify current release documentation.

**Worked example 3 — one stubborn pod:** `[SYNTHETIC]` A low-utilization node has four pods. Three are safe to move; one batch pod has local state and cannot be evicted. Deleting the node would lose work or violate recovery policy. Leave it, checkpoint/migrate through an approved process, or wait for the batch to finish. A blocked consolidation may be the correct result.

#### 9.4.6 Overprovisioning placeholders

Placeholder pods reserve spare capacity so a high-priority workload can schedule quickly when demand rises. When a real high-priority pod arrives, placeholders may be preempted and the node autoscaler replenishes spare capacity. Benefits: less wait for new nodes and better protection for critical scale-out SLOs. Costs/risks: idle HCU, churn, hidden request mistakes and unbounded headroom. Use M15 Unit 2 placeholders and Unit 1 headroom; measure latency benefit against incremental HCU and SLO outcome.

#### 9.4.7 Observability baseline

Collect pending pod count/age by scheduler reason; autoscaler decision time/reason; selected group/NodePool/shape; node creation-to-Ready duration; kubelet/CNI/CSI failures; scale-up success/failure/retries; node count by pool/zone/capacity type; allocatable versus requested and actual usage; stranded CPU/memory/GPU; ceiling/quota proximity; consolidation attempts/success/blockers; disruption and workload impact; simulated HCU per node-time and completed unit. Metric names such as `cluster_autoscaler_*` and `karpenter_*` are `[VERIFY]`; do not invent names or queries.

#### 9.4.8 Pattern catalogue

| Pattern | Use when | Do not use when |
|---|---|---|
| Fixed CA node groups | Workload classes map to known shapes and provider integration is supported | Shape differences create unmanageable group sprawl |
| Flexible NodePool | Workload requirements vary and catalog supports useful flexibility | Team cannot govern provider-specific config/IAM/images |
| Dedicated system pool | Platform components need stable placement/isolation | No owner, ceiling or forecast exists |
| On-demand floor + spot batch | Critical services need stable capacity; tolerant batch uses spot | Batch lacks checkpoint/fallback (Unit 8) |
| Placeholder headroom | Critical scale-out SLO is shorter than node provisioning path | Idle capacity cost is unbounded |
| Conservative consolidation | Workloads are stateful, long-running or disruption-sensitive | Aggressive savings are expected without SLO tests |
| Pre-scale for known event | Demand ramp is predictable and lead-time risk matters | Forecast uncertainty is high and pre-scale is unbounded |
| Multi-cluster failover pre-scale | DR failover needs spare capacity | Quota, data, image, network and routing are untested |

#### 9.4.9 Anti-pattern catalogue

| Bad practice | Waste/reliability failure | Corrected version |
|---|---|---|
| Unbounded NodePool | Runaway replicas create uncontrolled node growth | Require resource/node ceilings, owner and alert |
| Increase max nodes for every Pending pod | Does not fix impossible selectors/storage/taints | Classify scheduler reason first |
| Two autoscalers manage same capacity | Duplicate/conflicting decisions | Disjoint pools and explicit ownership |
| Scale down on average utilization only | Peak demand or disruption breaches SLO | Use peaks, requests, PDB and workload risk |
| One large node for every workload | Large failure blast radius and fragmentation | Pool/shape by workload class |
| PDB treated as guarantee | Involuntary loss still occurs | Replication, recovery and failure-domain design |
| Ignore DaemonSet overhead | Allocatable capacity overstated | Include system overhead |
| Reduce requests below observed need | Throttling/OOM and failed scheduling | Right-size from percentiles and load tests |
| Delete only node hosting singleton | Workload unavailable | Review eviction safety and replacement headroom |
| Teams edit NodePools directly | Unauthorized costly/unsafe shapes | RBAC, admission, Git review and audit |
| Rotate all nodes together | Capacity dip and cold-cache storm | Canary/ring rollout and disruption budget |
| Treat simulator boot time as SLO | False confidence | Measure actual environment |

### 9.5 Level 3 — Advanced

#### 9.5.1 Node-shape flexibility versus node-group simplicity

| Design option | Benefit | HCU impact `[HYPOTHETICAL]` | Risk | Choose when |
|---|---|---|---|---|
| Few fixed node groups | Simple boundaries/review | Can strand capacity if shapes are coarse | Group mismatch/sprawl | Workload profiles are stable |
| Many specialized groups | Precise isolation/predictable hardware | More idle/fragmented HCU possible | Config/upgrade complexity | Security, licensing or hardware constraints require it |
| Flexible catalog | More candidate fits and possibly better packing | May reduce stranded HCU in some traces | Provider-specific policy and heterogeneity | Workloads vary and compatibility is understood |
| Larger nodes | Lower per-node DaemonSet overhead | Fewer node-hours may be needed | Larger failure blast radius | Workloads tolerate node failure and can spread |
| Smaller nodes | Smaller failure domain | More per-node overhead may accrue | Fragmentation/node count | Workloads are small or need isolation |

Instance flexibility can improve the chance of finding a compatible shape and, where a provider exposes multiple eligible capacity types, may improve the set of spot candidates (Unit 8). It also increases heterogeneity. Validate CPU architecture, memory, storage, network, GPU, licensing, kernel/driver and workload constraints. A synthetic catalog does not prove a provider can supply those shapes.

#### 9.5.2 Zones, storage and topology

A pod with a zonal persistent volume may only schedule in the volume's zone. A candidate node in another zone does not solve it. Storage binding mode, topology constraints, anti-affinity and PodTopologySpread narrow the candidate set. For stateful workloads, validate storage topology and failover before increasing ceilings. `WaitForFirstConsumer` and CSI behavior are `[VERIFY]` for the actual provisioner/Kubernetes version. The simulator's `pvc_zone` field demonstrates a hard zone constraint; it does not model CSI provisioning.

#### 9.5.3 Worked example 4 — CA-like versus flexible bin-packing

Use the synthetic trace from Level 2: CA-like exposes only `general-large`; the flexible policy can select `general-small` and `general-large`. Both schedule the three pods on two nodes. CA-like modeled HCU is `20`; flexible modeled HCU is `16`. Flexible selection has less stranded CPU/memory in this trace. Change the catalog, workload mix, zone, capacity type, ceiling, boot delay or HCU rate and the result may change. Sensitivity analysis is mandatory; do not conclude that one product is universally cheaper.

#### 9.5.4 Worked example 5 — HCU cost, stranded capacity and node time

For simulated node shape `i`:

\[
C_i = N_i \times T_i \times R_i
\]

where `N_i` is node count, `T_i` is simulated node-time in hours, and `R_i` is `[HYPOTHETICAL]` HCU per node-hour.

\[
C_{total}=\sum_i(N_i\times T_i\times R_i)+C_{platform-overhead}+C_{disruption-retry}
\]

Report CPU/memory/GPU utilization, stranded capacity, pending count/duration, deadline outcome, disruption/retry count and HCU per completed job/request. Include idle node-time and system/DaemonSet overhead explicitly; do not hide them in a utilization percentage. A lower HCU total is not a win if jobs remain pending or SLOs are missed.

#### 9.5.5 Worked example 6 — right-sizing changes node count

`[SYNTHETIC]` Six service pods run on a small shape. Over-requested case: each asks for `2,500m CPU` and `1,024 MiB`; one fits per node, six nodes at `3 HCU/node-hour` for one simulated hour = `18 HCU`. Right-sized case: each asks for `1,000m CPU` and `1,024 MiB`; three fit per node, two nodes = `6 HCU`. The modeled difference is `12 HCU` in this trace. This is not a recommendation to reduce requests blindly. Verify CPU throttling, memory peaks, OOM behavior, tail latency and SLOs using representative load/soak tests.

#### 9.5.6 Worked example 7 — cost ceiling and safe response

`[SYNTHETIC]` A pool is allowed at most two nodes, each at `5 HCU/node-hour`.

\[
Maximum\ modeled\ rate = 2\ nodes \times 5\ HCU/node-hour = 10\ HCU/hour
\]

If the ceiling is reached and a critical pod remains pending: confirm the reason is compatible capacity; inspect pool limits and external quota; identify priority/deadline; check approved alternative pools; protect the stable floor/SLO; escalate for a human decision; record new ceiling, owner, expiry and rollback. Do not automatically raise it. A ceiling is a spend/blast-radius control and can intentionally leave low-priority work pending.

#### Worked example 8 — Scale-out time budget

\[
T_{usable}=T_{pod-autoscaler}+T_{node-decision}+T_{boot/join}+T_{CNI/CSI}+T_{image/start}+T_{app-warmup}
\]

`[SYNTHETIC]` Example assumptions: pod autoscaler 1.5 min; node decision 0.5 min; boot/join 4 min; CNI/CSI 1 min; image/start 2 min; app warm-up 1 min. Total = 10 min. If the synthetic traffic ramp reaches its unsafe region in 6 min, new capacity arrives too late for the first part of the ramp. Options: measured headroom/placeholders, pre-scale for known events, queue/buffer work, load shed/degrade non-critical work, cache images/models, or improve readiness sequencing. These are assumptions, not real provider lead times.

#### Worked example 9 — quota, capacity-unavailable and node-join triage

`[SYNTHETIC]` Three pending-workload cases have different causes:

| Injected condition | Observable evidence | Correct response | Incorrect response |
|---|---|---|---|
| Capacity unavailable | Candidate shape is valid, but no capacity is returned | Bounded backoff and approved alternative shape/pool | Infinite retry of same shape |
| Quota exhausted | Pool is within its own max, but external quota blocks request | Stop scale-up, alert quota owner and request approved quota review | Raise NodePool max without quota review |
| Node join failure | Provision request accepted, but node never becomes Ready | Inspect bootstrap, kubelet, CNI/CSI, IP and image chain | Keep creating identical nodes |

The diagnosis changes the owner and mitigation. The simulator injects these as scenario labels; it does not reproduce provider API responses.

#### Worked example 10 — denial-of-wallet with a hard ceiling

`[SYNTHETIC]` Eight Jobs each request `3,000m CPU` and `4,096 MiB`. A flexible pool is capped at two nodes. The simulator schedules two jobs and leaves six pending with `nodepool_ceiling`. If each selected small node is `3 HCU/node-hour`, the maximum modeled rate for this two-node scenario is `6 HCU/hour`. The safe action is to pause low-priority admission, alert the owner, preserve critical work and request a bounded human decision. The ceiling is not silently raised.

#### Worked example 11 — placeholders versus waiting for node readiness

`[SYNTHETIC]` A traffic ramp reaches its unsafe region in 6 minutes. The simulated scale-out path from Example 8 takes 10 minutes. Without spare capacity, new pods may wait through the gap. A placeholder policy keeps one spare node available at `3 HCU/node-hour`; if held for a quarter-hour, its modeled cost is:

\[
3\ HCU/node-hour \times 0.25\ hour = 0.75\ HCU
\]

The placeholder can reduce the time to place the real high-priority pod, but it is not free and may be preempted. Choose it only if measured SLO benefit justifies the HCU and the placeholder has a clear owner, priority and maximum count.

#### Worked example 12 — policy-as-code rejects an unsafe NodePool

`[SYNTHETIC]` Approved fixture: owner `data-platform`, max nodes `4`, CPU limit `16,000m`, allowed family `general`, and capacity types `on-demand`/`spot`. Rejected fixture: empty owner, max nodes `0`, no allowed family, no CPU ceiling and spot-only capacity without a documented fallback exception. The policy test should return one violation per missing guardrail and fail CI. A production policy must also validate allowed family/type membership against a versioned allowlist; the small teaching validator demonstrates only the core checks.

#### 9.5.8 Scale-down, consolidation and disruption economics

Consolidation saves modeled node-time but may create pod restarts, cache cold starts, image-pull storms, queue rebalances, retry amplification, lost batch work, topology violations and SLO degradation. Compare HCU saved with disruption cost/risk. PDBs and controller disruption budgets constrain specific voluntary operations; they do not guarantee no disruption. A blocked consolidation can be the correct safe result.

#### 9.5.9 Failure diagnosis decision tree

```text
Pod Pending
  -> Does any allowed shape satisfy hard constraints?
       No: selector/taint/zone/PVC/GPU mismatch -> fix contract/catalog; do not add nodes
       Yes:
         Does any shape fit CPU/memory/GPU?
           No: request/shape mismatch -> right-size or approve shape
           Yes:
             ceiling/quota reached? -> protect priority, alert, escalate
             capacity available? -> if no, bounded retry/approved alternative
             permission/API valid? -> if no, stop and repair identity/config
             node joins/Ready? -> if no, inspect bootstrap/CNI/CSI/image
             app ready within SLO? -> if no, headroom/cache/queue/pre-scale
```

#### 9.5.10 Failure modes and controls

| Failure mode | Why scaling more may worsen it | Safe diagnosis/control |
|---|---|---|
| Impossible selector/affinity | More nodes with wrong labels do not help | Compare hard constraints to catalog |
| Quota exhausted | Retries repeat a rejected request | Stop retry loop, alert and request quota review |
| Capacity unavailable | Same shape requests can stall | Bounded backoff and approved alternatives |
| Permission/API failure | More requests create noise | Stop and inspect least-privilege identity/config |
| Invalid NodeClass/subnet/security group | Every retry reuses invalid launch config | Validate provider class, network selectors and permissions before retry |
| Provider API throttling | Retry storm worsens control-plane pressure | Bounded exponential backoff with jitter and request-rate review |
| Node never joins | Original bootstrap fault remains | Inspect kubelet, CNI/CSI, image and node conditions |
| IP exhaustion | More nodes may worsen IP pressure | Model pod IP/subnet capacity with network owner |
| DaemonSet overhead | Every new node consumes resources | Include system overhead in allocatable model |
| GPU fragmentation | Aggregate GPU count may not fit the pod | Match GPU count, topology, taints and shape |
| Scale-up storm | Replica growth exceeds ceilings/budget | Max replicas, quotas, node limits and alerts |
| Consolidation deadlock | PDB/stubborn pod prevents movement | Report blocker and review workload/disruption policy |
| Consolidation flapping | Scale-up/down oscillation creates churn | Hysteresis/stable windows/cooldowns `[VERIFY]` |
| Image pull storm | Many nodes pull images simultaneously | Registry caching/mirroring, pre-pulled/baked images where supported and staged rollout |
| GPU driver/device-plugin slow init | Node may be Ready before the accelerator resource is usable | Verify node initialization/resource registration before declaring workload-ready |
| CA/Karpenter overlap | Competing decisions | Non-overlapping pools and migration plan |
| Rotation blast radius | Simultaneous replacement removes capacity | Canary/ring rollout and headroom |

#### 9.5.11 Managed versus self-managed decision

| Option | Operational burden | Control | Questions |
|---|---|---|---|
| Managed node groups + CA | Provider manages group primitives; CA still needs config/upgrade | Group-oriented | Does provider integration fit workload shapes/quotas? |
| Karpenter with provider integration | Flexible policy; provider-specific controller/NodeClass | Flexible requirements/consolidation | Can team govern APIs, limits, images, IAM and disruption? |
| Managed/autopilot node provisioning | Provider owns more lifecycle details | Potentially less low-level control | Are scheduling, security, cost and portability boundaries acceptable? |
| Static capacity + scheduled scaling | Simple/predictable | Less dynamic | Is demand predictable and headroom acceptable? |
| Serverless/container platform | Provider abstracts node lifecycle | Service-specific controls | Do workload state, networking and economics fit? |

Alternatives include static capacity with schedule-based scaling, KEDA for pod-level event-driven scaling (Unit 10), and serverless container services (awareness only). Do not assume current availability or feature parity for EKS/GKE/AKS offerings. Verify provider documentation and organizational constraints.

### 9.6 Level 4 — Expert

#### 9.6.1 Operate node provisioning as a platform service

| Role | Accountability |
|---|---|
| Platform engineering | NodePool/node-group templates, autoscaler config, supported shapes, limits and upgrades |
| Workload team | Accurate requests, constraints, readiness probes, SLO and disruption tolerance |
| SRE | Scale-out SLO, disruption policy, runbooks, error-budget/freeze decisions |
| FinOps | HCU assumptions, unit-cost reporting, allocation and budget review |
| Security | Controller identity, permissions, admission policy, audit and node image controls |
| Network/storage teams | IP/subnet, CNI/CSI, volume topology and capacity dependencies |
| Business owner | Priority/deadline decisions and approved exceptions |

No team should be able to add unlimited capacity without an owner, approved ceiling and audit trail.

#### 9.6.2 Node-pool golden-path contract

Every approved pool template specifies: owner/purpose/tier; allowed CPU architecture/families/zones/capacity types; labels/taints; node group min/max or NodePool resource ceilings; quota headroom/escalation owner; system overhead; disruption/consolidation policy; image/bootstrap/CNI/CSI compatibility; identity/security posture; cost labels (`team`, `service`, `env`, `cost-center`); metrics/alerts/runbooks/SLO; change approval, rollout rings and exception expiry. M16 owns the full developer-platform experience; this unit defines the node-provisioning contract.

#### 9.6.3 Capacity ceiling and HCU worksheet

| Field | Example `[SYNTHETIC]` | Owner |
|---|---|---|
| Pool | `batch-general` | Platform |
| Owner/team | `data-platform` | Workload owner |
| Max nodes | 4 | Platform + FinOps |
| Max CPU | 16,000m | Platform |
| Allowed families | `general` | Platform |
| Allowed capacity types | `on-demand`, `spot` | Platform/SRE |
| HCU rate/node-hour | 3 HCU | FinOps model owner |
| Maximum modeled node rate | 12 HCU/hour | FinOps |
| Quota safety margin | `[ILLUSTRATIVE]` below provider quota | Platform |
| Critical workload fallback | Approved stable pool/queue | SRE |
| Exception expiry | Explicit date/owner | Approver |

This is not an invoice. Real governance also reviews provider quota, billing lag, network/storage costs and external resources.

#### 9.6.4 Policy-as-code

Reject missing owner, absent/zero node ceiling, missing resource limit, unsupported family/capacity type, unapproved zone/GPU, spot-only pool without explicit fallback decision, missing labels, broad permissions and expired exceptions. The included Python validator is intentionally small. A real platform uses its chosen admission/CI policy engine and tests exact syntax/version `[VERIFY]`. Checking only `max_nodes` while ignoring CPU/GPU, quotas, replicas and HCU rate is incomplete.

#### 9.6.5 CA and Karpenter ownership boundaries

Do not run multiple node autoscalers over the same capacity domain unless ownership is explicitly defined and tested. Safe migration: inventory groups/workloads; assign disjoint labels/taints; ensure only one controller manages each domain; move a low-risk workload class; observe pending duration, scale-up success, node count, cost and disruptions; expand only after SLO/rollback criteria pass; remove old ownership only when no dependencies remain.

#### 9.6.6 Denial-of-wallet protection

A runaway HPA, Job or compromised workload can generate pods that cause node growth. Layer controls: namespace `ResourceQuota`/`LimitRange` (M03 Unit 2); HPA/KEDA max replicas; NodePool/node-group ceilings; allowed shapes/zones/capacity types; per-team budgets/alerts (Unit 3); node-growth alerts; GPU admission policy; least-privilege autoscaler permissions; human approval for emergency ceiling changes; kill switch for the synthetic drill. A cost ceiling may intentionally leave pods pending. Pair it with priority policy, fallback/degradation, owner alert and escalation.

#### 9.6.7 Node image drift and rotation

Node image updates/drift are security and reliability work. Test image/bootstrap in isolation; roll through canary pool/ring; keep replacement headroom; use disruption budgets and PDBs appropriately; monitor NotReady nodes, pending pods and SLOs; avoid synchronized rotation across zones/clusters; preserve rollback to known-good config where supported; verify exact drift/expiry behavior for installed Karpenter/provider `[VERIFY]`.

#### 9.6.8 Fleet and multi-cluster considerations

Compare per-cluster/region ceilings, independent quota boundaries, regional capacity/shape differences, failover surge and pre-scale requirements, node-pool cost allocation, stranded capacity distribution, commitment/reservation coverage `[VERIFY]`, consistent policy templates and exceptions. Allocate node-pool cost to teams using Unit 4 ownership metadata and a documented driver (for example, requested CPU/memory share); show idle/stranded capacity separately rather than hiding it in team usage. Use OpenCost as a cost-visibility comparison path (Unit 11), not as a substitute for provider invoice reconciliation. A second region cannot absorb load without verified quota, node shapes, network, data readiness, image availability, identity and traffic routing. M14 owns detailed multi-region design.

#### 9.6.9 Upgrade strategy, capacity reservations and commitment coverage

**Autoscaler/Kubernetes upgrades:** align CA compatibility with the Kubernetes release and verify the supported version-skew policy `[VERIFY]`. For Karpenter, review controller release, CRD/API migrations, provider release and NodeClass schema together. Test in an ephemeral/simulation environment, then canary one pool/ring before fleet rollout. Keep rollback artifacts and avoid combining an autoscaler upgrade, node-image rotation and broad pool-policy change in one uncontrolled event.

**KWOK regression:** where compatible KWOK integration exists, use it as a policy/regression safety net in CI for selected scheduling/provisioning cases. It is not provider-fidelity evidence. The Python simulator remains the guaranteed path in this unit.

**Capacity reservations — Awareness:** reserved capacity can be appropriate for critical pools or scarce GPU shapes when availability matters more than lowest modeled HCU. Verify reservation semantics, matching constraints, ownership and cancellation/expiry conditions with the provider `[VERIFY]`.

**Commitment coverage — Awareness:** model stable baseline nodes separately from elastic/on-demand/spot nodes. A commitment can lower the modeled cost of baseline usage but can create regret when forecasts are wrong or the workload moves. Record a base/high/low demand scenario, commitment utilization and unused commitment exposure; do not assume autoscaled nodes are automatically covered or that a commitment is always cheaper. Provider terms are `[VERIFY]` and are outside this HCU lesson.

A commitment/reservation regret worksheet should compare low/base/high demand, covered baseline node-hours, actual utilization of the committed amount, unused commitment exposure, peak capacity gap, and the owner-approved flexibility premium. Do not report coverage as savings unless unused commitment and incremental burst capacity are included.

#### 9.6.10 Eight organizational incident scenarios

All incidents and impacts below are hypothetical. The “10×” in Case 1 is a source-mandated synthetic descriptor, not an observed production statistic.

**Case 1 — Runaway NodePool**
- **Symptoms:** no CPU/resource ceiling; HPA/Job increases demand continuously.
- **Impact:** `[SYNTHETIC]` node count grows to 10× expected; modeled HCU and blast radius rise.
- **Evidence:** HPA desired/current replicas, pending pods, node count timeline, NodePool spec, owner labels and quota.
- **Immediate mitigation:** stop low-priority admission; cap/pause offending workload through approved control; do not delete critical workloads blindly.
- **Root cause:** no NodePool ceiling, missing replica cap and no growth alert.
- **Corrective fix:** resource/node ceilings, namespace quotas, HPA max replicas and owner labels.
- **Preventive control:** policy rejects missing ceilings; CI tests runaway fixture.
- **Verification metric:** node growth rate, ceiling proximity, pending duration and HCU per completed job.

**Case 2 — Quota exhaustion during launch**
- **Symptoms:** scale-up attempted; nodes do not appear; pods remain pending.
- **Impact:** critical workload misses ramp; no alert on quota/max-node proximity.
- **Evidence:** pending reasons, pool status, provider quota source `[VERIFY]`, max-size config and timeline.
- **Immediate mitigation:** prioritize critical pods, protect headroom and activate approved fallback/queue.
- **Root cause:** internal ceiling not reconciled with external quota; no quota alert.
- **Corrective fix:** set autoscaler ceiling below quota with reviewed margin and alerts.
- **Preventive control:** quota reconciliation and launch-readiness review.
- **Verification metric:** quota proximity, pending duration by priority and scale-up failure rate.

**Case 3 — Consolidation evicts long-running batch job**
- **Symptoms:** job near completion terminated during consolidation.
- **Impact:** `[SYNTHETIC]` job repeats work and misses completion window.
- **Evidence:** pod/node events, disruption decision, checkpoint age, output commit history and PDB/annotation.
- **Immediate mitigation:** pause voluntary consolidation for affected pool; resume from valid checkpoint or rerun safely.
- **Root cause:** no checkpoint/idempotency evidence and disruption tolerance absent from policy.
- **Corrective fix:** checkpoint/resume, safe eviction policy and workload-class consolidation controls.
- **Preventive control:** interruption/consolidation test before eligibility.
- **Verification metric:** lost-work fraction, completion, disruption retry and deadline attainment.

**Case 4 — Impossible node selector**
- **Symptoms:** pods require label no allowed shape has; alerting covers scale-up failure only.
- **Impact:** workload never schedules; operators waste time increasing capacity.
- **Evidence:** rendered pod selector/affinity, node labels, scheduler events and autoscaler logs.
- **Immediate mitigation:** stop retries for impossible class; correct selector or approve matching pool.
- **Root cause:** no reason-aware pending alert.
- **Corrective fix:** pending-reason classifier and catalog/selector validation.
- **Preventive control:** admission/CI check against supported labels and constraints.
- **Verification metric:** impossible-constraint pending rate and time-to-diagnosis.

**Case 5 — CA and Karpenter overlap**
- **Symptoms:** two controllers act on overlapping workloads/capacity; node count/decisions oscillate.
- **Impact:** duplicate capacity, unexpected HCU, churn or unstable placement.
- **Evidence:** controller logs/events, ownership labels, group/NodePool inventory and node timeline.
- **Immediate mitigation:** freeze config changes; establish controller of record.
- **Root cause:** no disjoint ownership boundary/migration plan.
- **Corrective fix:** separate pools by labels/taints; one controller per capacity domain.
- **Preventive control:** overlap policy check and migration runbook.
- **Verification metric:** competing decisions, node churn and HCU per completed workload.

**Case 6 — PDB deadlock blocks consolidation**
- **Symptoms:** PDB `maxUnavailable: 0` blocks voluntary eviction; low-use nodes remain.
- **Impact:** idle/stranded capacity persists; modeled HCU stays higher.
- **Evidence:** PDB status, healthy/desired replicas, node events, consolidation blocker and topology.
- **Immediate mitigation:** do not weaken PDB blindly; confirm it represents a real availability requirement.
- **Root cause:** PDB and consolidation objective not reviewed together.
- **Corrective fix:** adjust replicas/topology/disruption policy only after SLO review; consider empty-node-only cleanup.
- **Preventive control:** PDB/consolidation review in ORR and policy test.
- **Verification metric:** blocked consolidation rate, available replicas and SLO impact.

**Case 7 — Node drift rotation has excessive blast radius**
- **Symptoms:** image drift rotates many nodes together.
- **Impact:** capacity dips below demand; caches/images warm simultaneously; latency rises.
- **Evidence:** node age/image versions, rotation events, pending pods, traffic/latency timeline and disruption budget.
- **Immediate mitigation:** pause voluntary rotation/consolidation; preserve stable capacity; roll back if supported.
- **Root cause:** no canary/ring and no replacement headroom.
- **Corrective fix:** staged rollout, explicit disruption budget and per-zone capacity floor.
- **Preventive control:** image update CI, drift review and game-day.
- **Verification metric:** concurrent disruptions, scale-out time and SLO/error-budget burn.

**Case 8 — Unauthorized NodePool change enables GPU nodes**
- **Symptoms:** NodePool edited to allow expensive/unsupported GPU class; unexpected node growth/allocation appears.
- **Impact:** `[SYNTHETIC]` unapproved HCU and security/compliance exposure.
- **Evidence:** audit event, Git diff, RBAC, admission decision, NodePool generation and node resources.
- **Immediate mitigation:** block further provisioning through approved policy; restore reviewed config; preserve audit evidence.
- **Root cause:** broad write access and no admission policy for allowed GPU/family.
- **Corrective fix:** least-privilege RBAC, protected GitOps workflow, admission checks and owner/expiry.
- **Preventive control:** negative tests for unapproved GPU/family/zone and tamper alert.
- **Verification metric:** unauthorized mutation count, policy rejection and unapproved node count.

#### 9.6.11 Operational runbook templates

Every runbook follows **trigger → checks → safe action → prohibited action → escalation → rollback/fallback → verification → evidence**.

**Pending pods/no scale-up:** trigger pending age; inspect scheduler reason, requests, selectors/affinity, taints, topology/PVC, limits, quota and controller health; classify resource shortage versus impossible constraint; prioritize by SLO; use approved compatible pool; never blindly raise max nodes/remove selectors; escalate to platform/workload/network/storage owners; queue/degrade lower priority; verify scheduling, scale-up and SLO; retain pod spec/events, pool snapshot and timeline.

**Ceiling/quota reached:** trigger max node/resource limit or quota proximity; inspect nodes, pending priority, HCU, quota and growth source; stop runaway admission and preserve critical floor; never auto-lift limits; escalate platform/FinOps/workload owner; use expiring approved change or queue; verify bounded growth and critical SLO; retain config diff, approval and HCU model.

**Capacity unavailable:** trigger no compatible shape available; inspect catalog, zone/family restrictions, quota and alternatives; use bounded backoff and approved alternatives; never retry indefinitely or broaden shapes silently; escalate platform/provider owner; queue or use stable pool; verify pending age/deadline; retain candidate list, failure reason and retry count.

**Node join/NotReady:** trigger node fails registration/readiness; inspect bootstrap, kubelet, image, CNI/CSI, IP/subnet and node conditions `[VERIFY]`; stop repeated identical create attempts; never loop-create nodes; escalate platform/network/storage/image owners; use stable capacity/queue and revert tested config; verify Ready and scheduling; retain conditions/logs/timeline.

**Scale-up loop/controller failure:** trigger repeated provisioning attempts without Ready nodes or repeated no-progress decisions; inspect controller health/leader election, pending reason, backoff, provider/API errors, permissions and ownership overlap; stop duplicate/overlapping controllers and pause repeated unsafe requests; never increase replicas or remove ceilings to silence the alert; escalate platform/provider owner; restore last reviewed controller/pool config; verify one controller owns the capacity domain and the next synthetic request makes bounded progress; retain controller logs, decision timeline and config diff.

**Consolidation blocked/disruptive:** trigger sustained blocked consolidation or SLO-impacting disruption; inspect PDB, disruption budget, safe-to-evict/do-not-disrupt, local storage, topology and replacement headroom; pause voluntary consolidation for affected class; never remove all PDBs to meet savings target; escalate SRE/workload/platform; restore conservative policy; verify no repeat disruption and SLO recovery; retain events/policy diff/SLO evidence.

**Denial-of-wallet/unexpected growth:** trigger node growth/HCU rate above approved threshold `[ILLUSTRATIVE]`; inspect HPA/Job replicas, quotas, pool limits, config changes, owner and audit; pause offending admission and cap replicas within policy; never delete arbitrary nodes/workloads; escalate security/platform/FinOps/owner; restore reviewed policy and re-enable gradually; verify growth is bounded and attribution complete; retain timeline/audit/HCU/approval.

#### 9.6.12 Reusable operational artifact templates

Use these templates as the minimum contents of the corresponding files in `runbooks/`.

**Node-pool/NodePool design review:** pool name and owner; workload classes; supported shapes/families/zones/capacity types; labels/taints; min/max or resource ceilings; system overhead; quotas/IP capacity; PDB/disruption/rotation policy; HCU envelope; SLO and scale-out budget; security reviewer; rollback and exception expiry.

**Capacity ceiling/HCU worksheet:** pool/owner; maximum nodes; maximum CPU/memory/GPU; per-shape synthetic HCU rate; maximum modeled HCU/hour; quota source and safety margin; namespace/HPA/Job caps; pending-work priority; alert owner; exception approver/expiry; rollback value.

**Scale-up/scale-down runbook:** pending reason; candidate shapes; controller decision; ceiling/quota; node join stages; safe consolidation conditions; PDB/eviction blockers; stop conditions; fallback; verification metrics; evidence links.

**Impossible-constraint triage:** pod name/owner/priority; selector/affinity; taints/tolerations; zone/PVC; GPU/extended resource; candidate catalog result; exact unsatisfied constraint; approved fix; test proving it is schedulable.

**Quota/capacity-unavailable response:** requested shape/zone/capacity type; quota and capacity evidence; retry/backoff budget; approved alternative candidates; criticality/deadline; fallback/queue decision; escalation owner; time to recovery.

**Node-join failure response:** provisioning request ID; node identity; bootstrap/kubelet state; CNI/CSI; IP/subnet; image/driver; node conditions; last successful stage; stop-retry decision; rollback/fallback; owner and evidence.

**Consolidation/PDB blockage review:** node/pods; utilization basis; PDB state; safe-to-evict/do-not-disrupt/local-storage; topology; replacement headroom; disruption budget; HCU saved; workload/SLO risk; approved action or reason to retain node.

**Denial-of-wallet incident:** growth timeline; HPA/Job source; owner; quota and node ceiling; unauthorized config changes; critical/non-critical workloads; containment action; HCU exposure estimate; audit trail; restore/reenable criteria.

**NodePool change approval/exception:** use the YAML template below; require approver, rationale, exact diff, risk, compensating controls, rollback and expiry.

**Autoscaler security review:** read/write permission inventory; controller identity; RBAC/admission; allowed shapes/regions/capacity types; audit; secret/bootstrap handling; NodeClass protection; threat scenarios; negative-test results; security owner.

**End-to-end scale-out time-budget memo:** workload/SLO; traffic-ramp envelope; each measured or synthetic stage; p50/p95 if measured; critical path; headroom/placeholder decision; HCU trade-off; fallback/load-shed; rollback and owner.

**Blameless postmortem:** use the template below; add corrective action owner/date, regression test, alert/policy change and follow-up verification.

#### 9.6.13 Change approval and exception template

```yaml
# File: runbooks/nodepool-change-approval.yaml
change:
  id: "CHG-SYNTHETIC-001"
  pool: "batch-general"
  owner: "data-platform"
  requested_by: "workload-owner"
  reason: "Documented workload demand change"
  requested_limits:
    max_nodes: 4
    max_cpu_m: 16000
  allowed_families: ["general"]
  allowed_capacity_types: ["on-demand", "spot"]
  disruption_policy_reviewed: true
  quota_reviewed: true
  security_reviewed: true
  slo_reviewed: true
  hcu_model_ref: "results/hcu-ceiling-worksheet.csv"
  rollback:
    previous_config_ref: "git:reviewed-commit"
    owner: "platform-oncall"
  exception:
    enabled: false
    approver: null
    expires_at: null
```

Values are illustrative placeholders. A real workflow must use the organization's approved change-management system and schema.

#### 9.6.14 Blameless postmortem template

```markdown
# File: runbooks/postmortem-template.md
## Summary
What happened and which workload/pool was affected?
## Customer/workload impact
Availability, latency, queue age, batch deadline and data correctness.
## Timeline
Demand -> pending -> autoscaler decision -> capacity action -> node Ready -> workload recovery.
## Detection
Which alert fired? Which signal was missing or delayed?
## Contributing conditions
Requests, constraints, ceilings, quota, permissions, capacity, bootstrap, PDB and disruption policy.
## Root cause
State the system/control failure, not an individual's mistake.
## Corrective actions
Owner, due date, verification test and rollback.
## Prevention
Policy-as-code, runbook, alert, capacity model or regression test.
## FinOps/SRE review
HCU impact, unit cost, SLO/error-budget impact and risk accepted.
```

### 9.7 SRE lens

#### SLIs, SLOs and operational KPIs

| KPI | Formula / definition | Unit | Source/window | Owner | Limitation |
|---|---|---|---|---|---|
| Pending pod count | Count Pending by reason | pods | Scheduler/API events | Platform | Count hides age/priority |
| Pending duration | Pending transition to scheduled/running | seconds/minutes | Pod timeline | SRE | Separate impossible constraints |
| Scale-up decision latency | Decision timestamp − unschedulable observation | seconds | Controller logs/events | Platform | Metric names `[VERIFY]` |
| Scale-up latency p95 | 95th percentile of demand-to-usable-capacity duration | seconds/minutes | Correlated HPA/node/pod/app events | SRE | Needs consistent event clocks and cohorting |
| Autoscaler decision error rate | Decisions later shown to be infeasible/incorrect ÷ evaluated decisions | % | Decision logs + scheduling outcome | Platform | Define an error taxonomy; model-only in this lab |
| Node age distribution | Age of nodes by pool/image/zone | time/quantiles | Node inventory | Platform | Age alone does not imply drift or risk |
| End-to-end scale-out | Demand trigger to application-ready capacity | seconds/minutes | HPA/node/pod/app timeline | SRE | Include image pull and warm-up |
| Scale-up success | Successful capacity actions ÷ attempts | % | Controller/provider events | Platform | Failure taxonomy must be stable |
| Ceiling proximity | Current nodes/resources ÷ configured maximum | ratio/% | Pool status/config | Platform + FinOps | Provider quota may be lower |
| Quota proximity | Consumed quota ÷ approved quota | ratio/% | Provider source `[VERIFY]` | Platform | Data may be delayed/incomplete |
| Node utilization | Requested or measured use ÷ allocatable | % | Scheduler/node metrics | Platform | Requests differ from actual use |
| Stranded capacity | Allocatable minus assigned requests | CPU/memory/GPU | Node/pod inventory | FinOps | Not all stranded capacity is removable |
| Fragmentation | Workloads that cannot fit despite aggregate free capacity | count/reason | Scheduler/catalog model | Platform | Multi-resource constraints matter |
| Consolidation success | Completed safe consolidations ÷ eligible attempts | % | Controller events | Platform | High success is not always desirable |
| Consolidation blocked | Blocked attempts ÷ eligible attempts | % | Controller events | Platform | Some blockers protect workloads |
| Disruption rate | Voluntary node/pod disruptions per workload window | events | Controller/workload events | SRE | Separate planned/involuntary events |
| HCU per node-time | Sum of node HCU rate × simulated node-hours | HCU | Synthetic rate card | FinOps | Not an invoice |
| HCU per workload unit | Total modeled HCU ÷ successful jobs/requests | HCU/job/request | Simulator/job ledger | FinOps + owner | Compare equivalent work |
| Node join failure | Failed registrations ÷ attempted nodes | % | Node conditions/provider events | Platform | Simulator only injects categories |
| Impossible-constraint rate | Such Pending pods ÷ all Pending pods | % | Scheduler/policy model | Workload/platform | Classification may be incomplete |
| SLO impact | Error-budget burn or missed deadline attributable to scaling | ratio/time | SLI/SLO telemetry | SRE | Attribution can be uncertain |
| Node growth rate | Change in node count per window | nodes/min or nodes/hour | Node inventory | Platform/Security | Growth can be legitimate; route by owner |

Pair cost/utilization with pending duration, completion, availability, latency, disruption and priority. Low node count may mean under-capacity. Average utilization hides peaks. Request-based utilization differs from actual use. Simulator HCU is not provider billing.

#### Alert catalogue

Thresholds are `[ILLUSTRATIVE]`; derive them from workload SLO, capacity plan and baseline.

- Pending pod age exceeds priority-specific threshold.
- Pending reason is impossible selector/taint/topology/PVC constraint.
- NodePool/node-group maximum reached.
- Provider quota proximity exceeds approved threshold.
- Scale-up attempt fails or repeatedly retries.
- Node fails to register/turn Ready within the measured expected envelope.
- Node-count growth exceeds approved policy.
- Consolidation disruption exceeds budget.
- PDB/disruption budget blocks eligible consolidation for a sustained window.
- HCU rate or cost per workload unit diverges from approved model.
- NodePool/node-class config changes outside reviewed GitOps/admission path.

If Prometheus rules are used, define metric names from the actual exporter and validate with matching `promtool`. This unit does not invent autoscaler metric names.

#### Runbook decision loop

```text
Alert -> classify pending reason / pool / workload priority
 -> inspect requests, constraints, ceiling, quota and controller health
 -> choose: fix constraint / approved scale-up / queue / fallback / pause
 -> verify node Ready and application readiness
 -> verify SLO, cost ceiling and owner attribution
 -> communicate decision and impact
 -> preserve evidence and add regression control
```

### 9.8 Security lens

| Threat | Control | Negative test |
|---|---|---|
| Over-privileged autoscaler identity | Least-privilege provider permissions/workload identity; no static keys | Policy rejects wildcard/admin permissions |
| Unauthorized NodePool edit | RBAC, protected GitOps, admission and audit | Unapproved family/GPU/zone change is rejected |
| Missing cost ceiling | Required NodePool/node-group limits and owner | Policy rejects missing/zero limits |
| GPU/expensive-node abuse | Namespace quotas, approved namespaces/priorities and allowed families | Unauthorized GPU request rejected |
| Denial-of-wallet | Replica caps, quotas, node ceiling, alerts and owner routing | Runaway synthetic Job cannot exceed node cap |
| Secret exposure in bootstrap | Secret manager/workload identity; never commit secrets | Scan fixtures/logs for credential-like values |
| Node metadata abuse | Restrict metadata access/workload identity `[VERIFY]` | Threat-model test identifies untrusted access path |
| Image/bootstrap tampering | Reviewed images and controlled node updates `[VERIFY]` | Policy rejects unapproved image reference |
| Audit evasion | Required audit/log routing | Policy rejects disabled audit requirement |
| Controller ownership overlap | Explicit pool ownership labels/scoping | Policy rejects duplicate ownership in synthetic inventory |

**Not addressed by local simulator:** actual cloud IAM, metadata service controls, network security groups, node image signing, production audit retention, regulatory controls and enterprise key management. These require environment-specific review.

### 9.9 Production checklist

- [ ] Every pool/group has named owner, workload class and purpose.
- [ ] HPA/KEDA/VPA and node autoscaling responsibilities are distinct.
- [ ] Pending reasons are classified before changing capacity.
- [ ] Requests/limits are reviewed against representative usage and load tests.
- [ ] Allocatable capacity includes DaemonSet/system overhead.
- [ ] Allowed shapes satisfy resource, label, taint, zone, storage and GPU constraints.
- [ ] Node-group min/max or NodePool CPU/memory/node limits are explicit.
- [ ] Provider quotas/IP/subnet limits are reconciled with internal ceilings.
- [ ] Ceiling proximity and node-growth alerts are tested.
- [ ] No overlapping CA/Karpenter ownership exists without an approved boundary.
- [ ] Spot/on-demand follows Unit 8 eligibility and fallback rules.
- [ ] PDB, disruption budget, local storage and safe-eviction behavior are reviewed.
- [ ] Consolidation/rotation has replacement headroom and staged rollout.
- [ ] Node image/bootstrap/CNI/CSI changes are tested and canaried.
- [ ] Scale-out time budget includes app readiness and warm-up.
- [ ] Cost reporting uses HCU or verified finance inputs and includes unit cost.
- [ ] Cost ceiling is not automatically lifted when reached.
- [ ] NodePool/node-class edits are reviewed, audited and policy-checked.
- [ ] Autoscaler identity is least-privilege and has no static credentials.
- [ ] Dashboards/runbooks cover pending, quota, ceiling, node join and disruption.
- [ ] Simulation is not represented as provider performance or billing.
- [ ] Every exception has approver, rationale, compensating control and expiry.
- [ ] CI tests cover impossible constraints, ceilings and policy tampering.
- [ ] Cleanup/teardown is verified for local labs.

### 9.10 Hands-on lab set

All eleven labs use the Cap+Scale simulation profile with the Python simulator as the guaranteed path; Cap-Core can run the same scripts without kind/KWOK if laptop resources are constrained. Optional KWOK is not selected here because kind, kubectl, container runtime, KWOK and promtool were absent in the authoring environment.

#### Shared workspace and safety preflight

```bash
# Run in an isolated directory.
mkdir -p unit9-node-provisioning/{src,tests,fixtures,results,runbooks}
cd unit9-node-provisioning
```

Before optional cluster work:

```bash
# Read-only checks only; no cloud API is called.
python --version
command -v kind || true
command -v kubectl || true
command -v docker || true
command -v podman || true
command -v kwok || true
command -v kwokctl || true
command -v promtool || true
```

Representative output:

```text
Python 3.11.x
kind: not found
kubectl: not found
docker: not found
podman: not found
kwok: not found
kwokctl: not found
promtool: not found
```

If tools are absent, use the simulator. If evaluating KWOK, verify exact Kubernetes/KWOK/CA/Karpenter versions, provider maturity and official install docs first. Abort if any optional step requires cloud credentials/resources, if a command targets a non-lab kube context, if a test attempts external API access, or if local resources are constrained. Preserve `results/`; remove only lab-created resources and verify no background process/context remains.

#### Lab 1 — Feasibility preflight and path selection

**Goal/profile:** determine whether optional KWOK is genuinely feasible; Cap+Scale uses the Python simulation path, with Cap-Core as the reduced alternative. **Inputs:** local tool inventory and official docs. **Real:** shell/Python version checks. **Simulated:** all node decisions/HCU.

**Steps:** (1) Create `results/preflight.md`. (2) Run `python -m src.lab_runner preflight`. (3) Record Python and presence of kind/kubectl/Docker/Podman/kwok/kwokctl/promtool. (4) If considering KWOK, verify CA `kwok` provider or Karpenter KWOK provider compatibility with chosen Kubernetes/controller versions. (5) Record docs/version/maturity; mark uncertainty `[VERIFY]`. (6) Select Python unless optional path is demonstrably compatible. (7) Record no cloud API was contacted.

**Command:** `python -m src.lab_runner preflight`. **Expected:** `cloud_api_calls: disabled`; `selected_path: Python teaching simulator`. **Positive test:** simulator selected if optional tools absent. **Negative test:** reject any report claiming KWOK ran when only docs were inspected; reject steps requiring cloud credentials. **Abort:** optional install requires cloud resources or laptop headroom is insufficient. **Evidence:** preflight, versions and source notes. **Cleanup:** verify no cluster/container started. **Pass:** path and fidelity are explicit. **Fidelity:** tool presence does not prove provider compatibility/maturity.

#### Lab 2 — Pending pod to simulated scale-up

**Goal/profile:** model feasible Pending workload receiving compatible capacity and impossible workload remaining Pending; Cap+Scale simulator path, Cap-Core alternative. **Steps:** (1) Run `python -m src.lab_runner pending`. (2) Inspect shape/resource fit/ready-at. (3) Increase request beyond all candidate shapes. (4) Require a label absent from catalog. (5) Compare resource shortage with impossible constraint.

**Expected:** `nodes=1, scheduled=['etl-batch']`; `simulated_decision_latency_minutes=0.5
simulated_ready_at_minute=4.5`; negative fixture reports `no_shape_fits_resources`. **Positive:** feasible pod selects a node. **Negative:** oversized/missing-label pod stays pending. **Abort:** any network/cloud call or write outside workspace. **Evidence:** pending report and decision explanation. **Cleanup:** simulator-only; preserve report. **Pass:** explain node selection vs real Ready node. **Fidelity:** ready time is an input, not measured boot time.

#### Lab 3 — Scale-down and consolidation safety

**Goal/profile:** identify why a low-utilization node cannot safely consolidate; Cap+Scale simulator path, Cap-Core alternative. **Steps:** (1) Run `python -m src.lab_runner consolidation`. (2) Inspect PDB, safe-to-evict, local-storage and do-not-disrupt blockers. (3) Remove one blocker at a time in copied fixture. (4) Label each control as Kubernetes-native, controller-specific or simulator flag. (5) Compare with safe-to-evict workload.

**Expected:** `low_util_candidate=candidate_for_review`, `budget_blocked=disruption_budget_exhausted`, plus blockers `batch:safe-to-evict=false`, `batch:local-storage`, `protected:PDB`, `protected:do-not-disrupt`. **Positive:** utilization threshold and disruption budget are checked before a candidate is reviewed; blockers are reason-coded. **Negative:** do not treat PDB as involuntary-loss protection; do not remove PDB without SLO review. **Abort:** never point at real cluster/data workload. **Evidence:** blocker report. **Cleanup:** no cluster state should change. **Pass:** distinguish PDB from NodePool disruption budget. **Fidelity:** no pod is evicted.

#### Lab 4 — Ceiling guardrails and alert

**Goal/profile:** hit simulated node ceiling, leave excess pods pending, calculate cost-rate alert; Cap+Scale simulator path, Cap-Core alternative, Cap+Obs optional. **Assumptions:** one node at `5 HCU/node-hour`, maximum one node `[HYPOTHETICAL]`. **Steps:** (1) Run `python -m src.lab_runner ceiling`. (2) Observe one node and pending jobs. (3) Calculate `1 × 5 = 5 HCU/hour`. (4) Add synthetic alert when node count equals max or critical pending age exceeds budget. (5) If using Prometheus, define metrics from your exporter and validate with matching promtool; do not invent CA/Karpenter metric names. (6) Write priority-preserving response.

**Expected:** `nodes=1`, one scheduled job, remaining jobs pending with `cluster_node_ceiling`. **Positive:** ceiling blocks growth and reason is clear.

Optional Prometheus fixture (metric names are invented **for this synthetic lab only**; they are not CA/Karpenter exporter metrics):

```yaml
# File: fixtures/unit9-ceiling.rules.yml
groups:
  - name: unit9-synthetic-ceiling
    rules:
      - alert: SyntheticNodePoolCeilingReached
        expr: nodepool_current_nodes >= on(pool) nodepool_max_nodes
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Synthetic node pool reached its configured ceiling"
```

```yaml
# File: fixtures/unit9-ceiling.test.yml
rule_files:
  - unit9-ceiling.rules.yml
evaluation_interval: 1m
tests:
  - interval: 1m
    input_series:
      - series: 'nodepool_current_nodes{pool="batch"}'
        values: '0 1 2 2'
      - series: 'nodepool_max_nodes{pool="batch"}'
        values: '2 2 2 2'
    alert_rule_test:
      - eval_time: 3m
        alertname: SyntheticNodePoolCeilingReached
        exp_alerts:
          - exp_labels:
              pool: batch
              severity: warning
            exp_annotations:
              summary: "Synthetic node pool reached its configured ceiling"
```

Commands when the matching Prometheus tools are installed:

```bash
# Run from the fixtures directory.
promtool check rules unit9-ceiling.rules.yml
promtool test rules unit9-ceiling.test.yml
```

The authoring environment did not have `promtool`, so these rules/tests are included but were **not executed here**. The Python ceiling scenario was executed. **Negative:** alert must not auto-increase max; missing metric is not zero. **Abort:** no real cost API/cluster mutation. **Evidence:** ceiling report, HCU worksheet, alert test. **Cleanup:** remove synthetic alert fixture after evidence. **Pass:** safe escalation is documented. **Fidelity:** HCU is not provider billing cap.

#### Lab 5 — Impossible constraints and triage runbook

**Goal/profile:** prove autoscaler cannot satisfy selector/taint/zone/PVC constraint absent from catalog; Cap+Scale simulator path, Cap-Core alternative. **Steps:** (1) Run `python -m src.lab_runner impossible`. (2) Add missing-label, untolerated-taint, unavailable-zone and PVC-zone fixtures. (3) Run `pod_feasibility`. (4) Confirm `impossible_constraints`, not generic shortage. (5) Write reason-aware alert and runbook.

**Expected:** `pending={'bad-selector': 'impossible_constraints'}`. **Positive:** matching label/zone/toleration is provisionable. **Negative:** adding same incompatible node shapes does not help. **Abort:** no real manifest. **Evidence:** CSV/runbook/tests. **Cleanup:** simulator-only. **Pass:** classify fit vs hard constraint. **Fidelity:** model omits inter-pod affinity scoring, full topology spread and CSI.

#### Lab 6 — CA-like versus Karpenter-like simulator comparison

**Goal/profile:** compare node count, utilization, stranded capacity, HCU and decisions; Cap+Scale simulator path, Cap-Core alternative. **Steps:** (1) Run `python -m src.lab_runner compare`. (2) Save output. (3) Add a smaller CA group. (4) Remove a flexible candidate or restrict family. (5) Vary HCU rate/duration and synthetic decision/boot delay. (6) Record node count, HCU, stranded, pending, simulated disruption count and readiness time. (7) Run a sensitivity table across at least three catalog/rate scenarios. (8) Avoid universal product claims.

**Expected:** CA-like `2 nodes`, `20 HCU`; flexible model `2 nodes`, `16 HCU`; both report synthetic decision latency `0.5 min`, readiness time `4.5 min` and `simulated_disruptions=0` for the baseline trace. **Positive:** same workload inputs and reconciled arithmetic. **Negative:** removing compatible shape creates pending; never claim product internals. **Abort:** no result labelled real price/benchmark. **Evidence:** comparison CSV/sensitivity notes/tests. **Cleanup:** preserve report; remove temporary copies. **Pass:** defend policy by trace. **Fidelity:** greedy teaching policies only.

#### Lab 7 — Right-sizing to node-count impact

**Goal/profile:** compare over-requested and right-sized requests; Cap+Scale simulator path, Cap-Core alternative; optional M11 load test if already available. **Steps:** (1) Run `python -m src.lab_runner rightsize`. (2) Compare six pods requesting 2,500m CPU with six requesting 1,000m. (3) Record node count/HCU. (4) Add memory/burst assumptions. (5) If load test is used, verify latency/throttling before accepting request change. (6) Record rollback threshold/owner.

**Expected:** over-requested `6 nodes/18 HCU`; right-sized `2 nodes/6 HCU`. **Positive:** same workload count/catalog, only request changes. **Negative:** if peak usage, latency or OOM guardrail fails, reject. **Abort:** no automated changes to real requests. **Evidence:** right-sizing report and load-test result or explicit proxy limitation. **Cleanup:** restore fixture defaults. **Pass:** explain why SLO validation is mandatory. **Fidelity:** synthetic requests are not production guidance.

#### Lab 8 — Denial-of-wallet drill and NodePool policy-as-code

**Goal/profile:** simulate runaway Job/HPA growth and reject unsafe pool policy; Cap+Scale simulator path, Cap-Core alternative. **Steps:** (1) Run `python -m src.lab_runner denial-wallet`. (2) Observe max-node bound and pending pods. (3) Run `python -m src.lab_runner security`. (4) Add missing-owner, no-max, no-CPU-limit, unsupported-family/capacity-type, spot-only and unauthorized-GPU negatives. (5) Add dry-run report/kill switch; simulator never applies changes.

**Expected:** `node_count=2`, `pending_count=6`; good policy has no violations, bad policy returns owner/limit/family/fallback violations. **Positive:** bounded policy passes. **Negative:** unsafe config rejected; no real mutation. **Abort:** stop if runner is modified to call provider API. **Evidence:** drill log, policy fixtures, negative report. **Cleanup:** simulator-only. **Pass:** bounded growth and human-approved escalation. **Fidelity:** no actual HPA/Job/billing runs.

#### Lab 9 — Node-provisioning failure drill

**Goal/profile:** distinguish capacity unavailable, quota exhausted and node join failure; Cap+Scale simulator path, Cap-Core alternative. **Steps:** (1) Run `python -m src.lab_runner failures`. (2) Create fixture for each required failure. (3) Record symptom/evidence/safe action/prohibited action/owner. (4) Add API-throttled and permission-denied stretch cases. (5) Compare bounded backoff with unbounded retry. (6) Verify node-join failures are diagnosed rather than solved by repeated creation.

**Expected:** three distinct `[SYNTHETIC]` branches and bounded retry delays such as `[1, 2, 4, 8, 8]` seconds. **Positive:** each failure has its own diagnosis and retry budget. **Negative:** unknown failure is not silently classified as capacity shortage; retry budget bounded. **Abort:** no real cloud API. **Evidence:** failure drill and runbooks. **Cleanup:** remove synthetic fixtures. **Pass:** correct diagnostic branch for all three. **Fidelity:** failure labels are injected, not provider responses.

#### Lab 10 — End-to-end scale-out time budget

**Goal/profile:** compare time-to-usable-capacity with synthetic traffic ramp; Cap+Scale simulator path, Cap-Core alternative, optional Cap+Obs. **Steps:** (1) Run `python -m src.lab_runner scaleout`. (2) Record each stage. (3) Compare total with traffic-ramp budget. (4) Choose headroom/placeholders, pre-scale, queue, load shedding or startup optimization. (5) Calculate HCU for headroom with synthetic assumptions. (6) Write design memo/rollback.

**Expected:** stage sum is 10 synthetic minutes. **Positive:** total equals component sum; no negative durations. **Negative:** incomplete model omitting image/app warm-up is rejected. **Abort:** never present as provider guarantee. **Evidence:** scale-out memo/calculation. **Cleanup:** simulator-only. **Pass:** defended decision protects SLO and explains HCU. **Fidelity:** timings are assumptions, not measured lead times.

#### Lab 11 — Autoscaler security review

**Goal/profile:** least privilege, NodePool tamper controls, admission/audit and secret handling; Cap+Scale simulator path, Cap-Core alternative. **Steps:** (1) Inventory conceptual read/write permissions; create no credentials. (2) Separate read from write. (3) Require protected GitOps for pool/class changes. (4) Reject missing ceilings, unapproved families/zones/capacity/GPU, missing owner/audit. (5) Add synthetic unauthorized mutation event and alert. (6) Review bootstrap secret handling; include no secrets. (7) Produce threat model/remediation.

**Expected:** approved policy passes; bad policy rejects missing owner/ceilings, unsupported family/capacity type, invalid memory/GPU guardrails and spot-only fallback omission. **Positive:** reviewed bounded config passes. **Negative:** unauthorized GPU/family and missing limits rejected; no credential created. **Abort:** no real IAM/provider resource. **Evidence:** security review, threat model, policy tests and audit fixture. **Cleanup:** remove synthetic fixtures and verify no credentials. **Pass:** permissions/config mutation/secrets have explicit controls. **Fidelity:** conceptual IAM review is not a provider security audit.

### 9.11 Self-check questions

1. **Does HPA create nodes?** No. HPA changes pod replicas; node autoscaling supplies nodes. Wrong answer temptation: HPA increases capacity, but it increases workload pods, not the fleet.
2. **When can node autoscaling not help a Pending pod?** When no allowed shape satisfies hard constraints. Wrong answer: more nodes always solve pending; more incompatible nodes do not help.
3. **Core difference between CA and Karpenter-style provisioning?** CA generally selects predefined node groups; Karpenter evaluates requirements against NodePool/provider catalog. Wrong answer: identical controllers/config.
4. **Why can aggregate free CPU mislead?** A pod must fit on one compatible node. Wrong answer: sum across nodes guarantees placement.
5. **Does a PDB guarantee a node can never be disrupted?** No; it constrains supported voluntary eviction. Wrong answer: PDB is node-level availability guarantee.
6. **What when a node ceiling is reached?** Alert, classify pending reason/priority, inspect quota/alternatives, escalate bounded change/fallback. Wrong answer: auto-raise max.
7. **Why can right-sizing reduce node count?** Accurate smaller requests can allow more pods per node. Wrong answer: lower requests always improve efficiency; under-requesting can throttle/OOM.
8. **Why is boot time not full scale-out time?** Registration, CNI/CSI, DaemonSets, image pull, container start and app warm-up remain. Wrong answer: VM exists, app ready.
9. **Why is CA/Karpenter overlap risky?** Competing controllers can create conflicting decisions. Wrong answer: more controllers mean redundancy.
10. **What protects against denial-of-wallet?** Replica caps, quotas, node ceilings, allowed shapes, alerts, owner routing, least privilege and approved escalation. Wrong answer: budget alert alone prevents creation.

### 9.12 Evidence artifacts

```text
unit9-node-provisioning/
├── README.md
├── versions.txt
├── assumptions.md
├── src/{__init__.py,simulator.py,lab_runner.py}
├── tests/test_simulator.py
├── fixtures/{instance-catalog.synthetic.yaml,workload-trace.synthetic.yaml,
│             impossible-constraints.synthetic.yaml,nodepool-policy.good.yaml,
│             nodepool-policy.bad.yaml}
├── manifests/nodepool-design-example.yaml
├── results/{preflight.md,pending-to-scaleup.txt,consolidation-blockers.md,
│            ceiling-report.md,impossible-constraints.csv,policy-comparison.csv,
│            right-sizing-report.csv,denial-of-wallet.log,provisioning-failure-drill.md,
│            scale-out-budget-memo.md,security-review.md,unit-test-report.txt}
└── runbooks/{pending-pods.md,ceiling-quota.md,capacity-unavailable.md,
              node-join-failure.md,consolidation-blocked.md,denial-of-wallet.md,
              nodepool-change-approval.yaml,postmortem-template.md}
```

Keep shapes/traces/HCU synthetic; record tool versions and verification date; label simulator outputs `[SYNTHETIC]`; never store real credentials, secrets, customer data, production identifiers or billing exports. Do not describe expected output as measurement. If later running KWOK, record versions and distinguish it from Python path.

### 9.13 Common interview and design-review questions

**1. Explain HPA versus node autoscaling.** HPA adjusts desired pod count from workload metrics. Scheduler tries existing nodes. Node autoscaler observes unschedulable pods and requests compatible capacity through provider integration. HPA can create pending pods faster than nodes become usable, so headroom, queueing or pre-scale may be required.

**2. Compare CA and Karpenter.** CA generally expands predefined node groups and chooses among them using expander logic. Karpenter evaluates pending requirements against NodePool constraints and provider catalog, then can consolidate eligible nodes. Choose based on provider support, workload heterogeneity, operations, upgrade burden, cost and disruption—not blanket claims.

**3. Diagnose a pod still Pending after autoscaler activity.** Start with scheduler events/full pod spec. Separate resource fit from hard constraints. Check selectors, affinity, taints, topology, PVC zone, GPU, requests, DaemonSet overhead, pool limits, quota, provider capacity, permissions and node registration. If no allowed candidate exists, stop retries and fix the contract. Otherwise use bounded retry/fallback.

**4. Design safe consolidation for long-running ETL.** Verify checkpoint/resume/idempotent output, disruption tolerance, PDB, local storage, replacement headroom and conservative budgets. Test under load; measure lost work, completion, SLO and HCU/job. A blocked consolidation may be correct.

**5. Derive an HCU ceiling.** Sum each allowed shape's maximum node count × hypothetical HCU/node-hour, plus explicit overhead. Reconcile with quotas, namespace quotas and HPA/Job limits. Add owner, alert, pending-work policy and expiring exception. It is not an invoice or provider cap.

**6. Protect against CA/Karpenter fighting.** Assign disjoint pools via labels/taints; ensure one controller owns each capacity domain; test migration with low-risk workload; compare node events/churn; remove old ownership only after evidence.

**7. Autoscaler security review.** Separate read/write permissions; least privilege/workload identity; protect NodePool/NodeClass with RBAC, admission and Git review; restrict families/zones/capacity/GPU; require ceilings/owner; audit; protect bootstrap secrets; negative-test unauthorized changes.

### 9.14 Sources and verification notes

#### Official sources consulted

- Kubernetes, **Node Autoscaling** — provisioning, scheduling constraints, node groups, auto-provisioning, consolidation and workload-autoscaling relationship: https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/
- Kubernetes, **Scheduling, Preemption and Eviction** — scheduler, constraints, pod disruption and eviction: https://kubernetes.io/docs/concepts/scheduling-eviction/
- Kubernetes, **Disruptions and PodDisruptionBudgets** — voluntary/involuntary disruption boundaries: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/
- Kubernetes SIG Autoscaling, **SIG Autoscaling** — current subproject ownership list: https://www.kubernetes.dev/community/community-groups/sigs/autoscaling/
- Kubernetes Autoscaler repository, **Cluster Autoscaler FAQ** — provider options and implementation-specific behavior: https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/FAQ.md
- Cluster Autoscaler provider documentation — expander/provider examples; verify exact release/provider: https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler
- Karpenter, **NodePools** — NodePool constraints, limits and API concepts: https://karpenter.sh/docs/concepts/nodepools/
- Karpenter, **NodeClaims** — NodeClaim requirements/lifecycle: https://karpenter.sh/docs/concepts/nodeclaims/
- Karpenter, **Disruption** — consolidation, drift, disruption budgets and termination: https://karpenter.sh/docs/concepts/disruption/
- KWOK, **Kubernetes WithOut Kubelet** — fake node/pod lifecycle simulation: https://github.com/kubernetes-sigs/kwok
- Karpenter repository KWOK provider documentation — optional simulation path; verify exact release/compatibility: https://pkg.go.dev/sigs.k8s.io/karpenter/kwok
- Prometheus, **Defining recording and alerting rules** — syntax checks and `promtool`: https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/

#### Claims requiring `[VERIFY]` before production use

| Component | Verify | Where/how |
|---|---|---|
| Kubernetes scheduler | Exact event reasons, topology, storage and extended-resource behavior | Docs matching installed version; inspect pod events in non-production |
| Cluster Autoscaler | Kubernetes compatibility, supported provider, expander list, flags/defaults, scale-down rules/annotations | Official CA docs/release notes for exact version/provider; inspect controller args |
| Karpenter | Project status/provider support, CRD versions, NodePool/NodeClaim/NodeClass schema, limits, consolidation, drift, expiry and disruption | Official Karpenter/provider docs matching installed release; inspect CRDs |
| KWOK | Compatibility, simulated behavior, provider integration and limitations | Official KWOK docs and exact CA/Karpenter provider repository/release |
| Prometheus | Metric names, labels, alert syntax and `promtool` compatibility | Actual exporter docs and matching Prometheus release |
| Managed offerings | Current name, feature boundary, availability and responsibilities | Official EKS/GKE/AKS docs; do not assume parity |
| CNI/CSI/IP | Bootstrap, subnet, pod-IP, storage topology and failure behavior | Provider/network/storage documentation |
| Security | Provider permissions, identity, metadata and audit controls | Provider IAM/security docs and organizational threat model |

#### Technical boundaries and limitations

- The simulator is a teaching model with greedy placement. It is not CA, Karpenter or the Kubernetes scheduler.
- It does not model real API latency, provider boot time, cloud quota enforcement, capacity scarcity, pricing, network/IP allocation, image registries, CSI, GPU drivers, real consolidation heuristics or controller concurrency.
- The simulator assigns pods to planned capacity before synthetic `ready_at`; this is a packing decision, not proof a real pod schedules before a node is Ready.
- HCU is not an invoice or quote.
- No real cloud resources, credentials or billing data are used.
- KWOK provider availability is a feasibility option, not a promise of compatibility or production maturity.
- Karpenter NodePool/NodeClaim/NodeClass schemas and CA flags/metrics are version-sensitive. No default values are asserted.
- The AWS `EC2NodeClass` reference is provider-specific and not portable.
- Local preflight found Python 3.13.5 available and `kind`, `kubectl`, Docker, Podman, KWOK, `kwokctl` and `promtool` absent. Therefore only the Python simulator path was selected for artifact validation; no cluster/provider integration was executed.

#### Unit-level claim register

| ID | Claim | Source/basis | Confidence/treatment |
|---|---|---|---|
| U9-C01 | HPA scales pods; node autoscaling supplies nodes | Kubernetes Node Autoscaling docs | High; cited |
| U9-C02 | Node autoscalers use pod scheduling and node constraints | Kubernetes Node Autoscaling docs | High; cited |
| U9-C03 | CA manages predefined node groups | Kubernetes Node Autoscaling and CA docs | High; cited |
| U9-C04 | Karpenter evaluates pending requirements against NodePool constraints | Karpenter NodePool/NodeClaim docs | High; cited |
| U9-C05 | Karpenter has NodePool and NodeClaim concepts | Karpenter official docs | High; API version-sensitive |
| U9-C06 | Consolidation can remove/replace underutilized nodes | Karpenter Disruption docs | High; policy version-sensitive |
| U9-C07 | Disruption budgets control selected voluntary Karpenter disruption | Karpenter Disruption docs | High; version-sensitive |
| U9-C08 | PDBs do not prevent all involuntary disruption | Kubernetes disruption docs | High; cited |
| U9-C09 | KWOK simulates fake node/pod lifecycle without kubelets | KWOK project docs | High; cited |
| U9-C10 | CA repository documents a KWOK provider option | CA repository FAQ | High for current source; verify release |
| U9-C11 | Karpenter repository documents a KWOK provider workflow | Karpenter KWOK package docs | High for documented path; verify release |
| U9-C12 | Current SIG Autoscaling page lists CA and Karpenter subprojects | Kubernetes SIG Autoscaling page | High as checked on review date |
| U9-C13 | HCU examples are synthetic | This lesson's rate assumptions | High; not external pricing |
| U9-C14 | Python model is not CA/Karpenter | Simulator implementation and explicit limitation | High |
| U9-C15 | NodePool limits are a capacity guardrail | Karpenter NodePool docs | High; schema version-sensitive |
| U9-C16 | Managed node autoscaling offerings differ by provider | Provider documentation required | `[VERIFY]`; no parity claim |
| U9-C17 | Scale-out includes join, networking, image and app readiness | Architecture decomposition | High-level; durations synthetic |
| U9-C18 | Right-sizing can improve packing | Scheduler resource-request model and synthetic tests | Mechanism; validate workload SLO |
| U9-C19 | Cost ceilings can leave pods pending | Simulator ceiling behavior and node limits | High; policy trade-off |
| U9-C20 | Multiple autoscalers need explicit non-overlapping ownership | Operational safety recommendation | `[ASSUMPTION]`; verify chosen integrations |

#### Final audit report

| Audit | Result | Notes |
|---|---|---|
| Source and placement | PASS | Attached Unit 9 prompt, M15 syllabus prompt and Roadmap tree inspected; Unit 9 is between Units 8 and 10 |
| Handoff statement | PASS | Verbatim statement included |
| L1–L4 coverage | PASS | Architecture, simulation, failure analysis, economics, governance and operating model included |
| Eight incident scenarios | PASS | All eight enumerated cases included; prompt's “seven” typo resolved in favor of its explicit eight-item list |
| Eleven mandatory labs | PASS | Eleven distinct labs with steps, tests, evidence, abort, cleanup and fidelity caveat |
| Twelve worked examples | PASS | Pending causes, CA/Karpenter packing, fragmentation, timing, consolidation, ceiling, HCU, right-sizing, failure triage, denial-of-wallet, scale-out and policy |
| Operational artifacts | PASS | Runbooks, design review, budget worksheet, change approval, security review and postmortem template |
| Metrics and governance | PASS | Formula/unit/source/window/owner/limitation supplied |
| Safety/authenticity | PASS | No cloud provisioning, credentials, real prices or provider guarantees; simulator caveats explicit |
| Code validation | PASS | Python standard-library simulator/tests executed in isolated temporary workspace; 26 tests passed |
| Local cluster/KWOK validation | NOT RUN | Required binaries/runtime absent; Python path selected |
| Prometheus rule validation | NOT RUN | `promtool` absent; sample rule/test fixture included, but not executed here |
| Repository safety | PASS | Standalone Unit 9 artifact only; no supplied curriculum file modified |

**Content status:** `DRAFT-AUDITED`  
**Audit date:** 2026-11-03  
**Auditor:** AI self-audit; human verification required  
**Unverified items:** provider-specific CA/Karpenter compatibility, exact release schemas/flags/metrics, KWOK provider compatibility and managed-provider feature availability.

AI self-audit does not replace a human running every model/lab with installed versions. All monetary values are hypothetical units; no real prices, discounts or provider limits are asserted. Outputs, traces, readiness times and HCU values are synthetic, not captured from a real provider or invoice. Simulated nodes do not reproduce cloud boot, quota, capacity or billing behavior. Project APIs, metric names and statuses must be re-verified against current official documentation. No cost-reduction measure should be trusted until its reliability effect has been measured in the learner's own environment.
