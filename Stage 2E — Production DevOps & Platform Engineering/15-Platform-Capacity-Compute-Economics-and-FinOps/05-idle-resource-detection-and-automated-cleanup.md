## Unit 5 — Idle resource detection and automated cleanup

**Stage:** Stage 2E — Production DevOps & Platform Engineering  
**Subfolder:** `15-Platform-Capacity-Compute-Economics-and-FinOps/`  
**Module:** M15 | **Unit:** 5  
**Target file:** `05-idle-resource-detection-and-automated-cleanup.md`  
**Estimated study time:** 24–32 hours (reading 6–8 h; labs 14–18 h; review 4–6 h)  
**Prerequisites:** Stages 0–2D and M01–M14; M03 requests/limits and HPA/VPA; M05 storage lifecycle and orphaned-volume cleanup; M07 decommissioning, TTL cleanup and audit logs; M08 GitOps; M09 identity; M10 SLOs/incident response; M11 utilization and telemetry; M13 backup/DR; M14 multi-cluster operations; M15 Units 1–4.  
**Core tools:** Python 3 standard library, CSV/JSON, `kind`, `kubectl`, local synthetic inventory and telemetry, `unittest`.  
**Optional tools:** existing M11 Prometheus/Grafana profile; KEDA cron only if already available and compatible.  
**Awareness:** VPA recommendation mode, registry inventory APIs, cloud resource recommenders, OpenCost, service catalog and policy engines. Provider/tool details are `[VERIFY]`.  
**Stack profile:** Cap-Core required; Cap+Obs optional; Cap+Scale not required.  
**Prices:** hypothetical cost units (HCU) only. No real provider prices or currency symbols are used.

> **Completion outcome:** Build a tested, evidence-based waste-detection and cleanup program. Produce a waste report with owner, confidence, risk and HCU estimate; demonstrate safe scheduling and TTL handling; protect quarterly jobs, DR standby and legal-hold data; simulate quarantine and deletion only in a throwaway local lab; and verify savings without double-counting.

## Contents

- [5.0 Learning contract and prerequisites](#50-learning-contract-and-prerequisites)
- [5.1 Verbatim handoff and scope boundaries](#51-verbatim-handoff-and-scope-boundaries)
- [5.2 L1 — Beginner: Foundations](#52-l1--beginner-foundations)
- [5.3 L2 — Intermediate: Working Practice](#53-l2--intermediate-working-practice)
- [5.4 L3 — Advanced: Production Engineering](#54-l3--advanced-production-engineering)
- [5.5 L4 — Expert: Operating at Scale and Under Failure](#55-l4--expert-operating-at-scale-and-under-failure)
- [5.6 Worked examples and decision walkthroughs](#56-worked-examples-and-decision-walkthroughs)
- [5.7 Failure modes, incident scenarios, and recovery](#57-failure-modes-incident-scenarios-and-recovery)
- [5.8 Security, reliability, governance, and cost guardrails](#58-security-reliability-governance-and-cost-guardrails)
- [5.9 Metrics, KPIs, and operating review](#59-metrics-kpis-and-operating-review)
- [5.10 Hands-on lab set](#510-hands-on-lab-set)
- [5.11 Self-check questions](#511-self-check-questions)
- [5.12 Evidence artifacts](#512-evidence-artifacts)
- [5.13 Common interview and design-review questions](#513-common-interview-and-design-review-questions)
- [5.14 Sources and verification notes](#514-sources-and-verification-notes)

---

### 5.0 Learning contract and prerequisites

#### Learning objectives

By the end of this unit, you can:

1. **[L1]** Distinguish idle, underutilized, orphaned and zombie resources, and explain why low utilization is not proof that deletion is safe.
2. **[L1/L2]** Identify waste candidates across Kubernetes, storage, registries, CI, telemetry, ML workloads and synthetic cloud inventories.
3. **[L2]** Build a waste report with an evidence window, owner, estimated monthly HCU, confidence, risk class and recommended next action.
4. **[L2]** Apply PromQL-style percentile reasoning, Kubernetes inventory checks, TTL and scheduled non-production scale-down while accounting for telemetry gaps, state and timezone/DST.
5. **[L3]** Design resource-class-specific idle policies, confidence scoring, expiring exemptions, owner confirmation, staged cleanup and savings verification.
6. **[L3/L4]** Operate cleanup automation with least privilege, allow-lists, dry-run defaults, action caps, audit records, rollback and cleanup SLOs.
7. **[L4]** Govern a fleet-wide waste program with KPIs, maturity gates, monthly reviews, incident learning and reliability constraints.
8. **[L4]** Distinguish identified, forecast, avoided and realized savings, and prove that a saving was not counted twice.

#### Prerequisite knowledge and boundaries

This unit assumes the learner can inspect Kubernetes resources, understand requests/limits, read utilization telemetry, use labels/annotations, work with GitOps, reason about SLOs and execute a previously designed report-only cleanup workflow. The learner should be comfortable running Python scripts, reading CSV/JSON and writing basic unit tests.

| Reused capability | How Unit 5 uses it | What Unit 5 does not repeat |
|---|---|---|
| M01 Unit 7 registry/image hygiene | Pull recency, retention and rollback-critical image exclusions | Full registry operations |
| M02 Unit 10 CI runner lifecycle | Idle runner time and ephemeral runners | CI architecture |
| M03 Units 2, 6, 7 | Requests/limits, HPA/VPA and placement constraints | Kubernetes scheduling fundamentals |
| M05 Units 3 and 8 | PVC/storage migration and orphaned-volume safety | Storage fundamentals or generic orphan cleanup |
| M07 Unit 8 | Report-only, TTL, deletion caps and audit patterns | Rebuilding the original cleanup framework |
| M08 | GitOps PRs, preview environments and declarative rollback | GitOps fundamentals |
| M09 | Least privilege and short-lived credentials | Identity fundamentals |
| M10 | SLOs, error budgets, incident response and postmortems | Incident-management fundamentals |
| M11 Units 9, 12, 13 | Utilization, telemetry cost and load testing | Telemetry architecture and saturation basics |
| M12 Unit 12 | Suspicious workloads and security monitoring | Security monitoring fundamentals |
| M13 | DR, backups, legal retention, timezone/DST and recovery | DR design |
| M14 | Idle clusters, standby regions, replicas and ephemeral clusters | Multi-cluster architecture |
| M15 Units 1–4 | Capacity/headroom, workload governance, budgets and cost allocation | Rebuilding those models |
| M15 Units 6–12 | Trade-off, release, node, KEDA, OpenCost and GPU topics | Detailed later-unit implementation |
| M16/M17 | Service catalog and integrated capstone | Platform portal or capstone implementation |

#### Stack profiles and safety

- **Cap-Core (required):** existing disposable `kind` cluster, `kubectl`, Python standard library, synthetic telemetry/inventory, CSV/JSON and `unittest`.
- **Cap+Obs (optional):** the existing M11 Prometheus/Grafana profile. Start only for the relevant query/metrics exercise; stop it afterwards. Do not install a second observability stack.
- **Cap+Scale (not required):** KEDA cron or cluster-provisioning simulations are optional extensions only.

A 4-CPU/8-GB laptop is a planning reference, not a guaranteed footprint. Measure local CPU, memory and disk before optional components. Do not run Prometheus, Grafana, OpenCost, KEDA and other optional components simultaneously merely to complete this unit.

**No cloud account, real billing export, production credential, paid service, real GPU or billable resource is required.** All cost values are HCU. A synthetic inventory is not a provider API response. A `kind` experiment is not proof of managed-cloud behavior.

Use these evidence labels consistently:

- `[ASSUMPTION]` — an explicit modeling choice.
- `[ILLUSTRATIVE]` — an example policy or threshold, not a universal default.
- `[SYNTHETIC]` — generated input or simulated output.
- `[VERIFY]` — version-, provider- or tool-specific behavior not verified against current documentation.
- `[MEASURED — YOUR ENVIRONMENT]` — a value actually measured by the learner.

Before any cluster command, check `kubectl config current-context` and confirm it is the dedicated disposable lab context. Do not run destructive commands against an unknown context. The only deletion exercises in this unit are confined to resources created by the lab.

---

### 5.1 Verbatim handoff and scope boundaries

> M07 Unit 8 taught decommissioning, orphan discovery, TTL-based cleanup scripts with report-only defaults, deletion caps, and audit logs; M05 Unit 8 taught orphaned-volume discovery and safe cleanup; M11 Unit 9 taught saturation/utilization signals. This unit **applies and extends those patterns to cost**: defining idle and underutilized resources with evidence, finding waste across Kubernetes and (conceptually) cloud inventories, measuring its cost, and automating **safe** cleanup and scheduling — reusing, not re-teaching, the cleanup safety mechanics.

**This unit teaches:** cost-aware classification, evidence windows, candidate confidence, risk scoring, ownership resolution, resource-class-specific retention, scheduled non-production operation, waste reporting, HCU estimates, savings verification, and program governance.

**This unit reuses:** the report-only default, explicit allow-list, deletion cap, audit log, TTL concept, quarantine window, owner notification and safe cleanup mechanics from M07 Unit 8; orphaned-volume checks from M05 Unit 8; utilization signals from M11 Unit 9.

**This unit defers:** node consolidation implementation (Unit 9), KEDA event-driven scaling (Unit 10), OpenCost deployment (Unit 11), GPU fleet economics (Unit 12), full cost/reliability trade-off modeling (Unit 6), and the platform service catalog (M16). Those later units consume the reports and policies produced here.

A candidate is not an authorization. A detector can recommend inspection; it cannot infer business purpose, legal retention, DR intent or owner approval from CPU metrics alone.

---

### 5.2 L1 — Beginner: Foundations

#### 5.2.1 Four resource classifications

| Classification | Definition | Example | Safe first response |
|---|---|---|---|
| **Idle** | Provisioned and billable but performing no useful work over a defined evidence window | Development Deployment has no requests and negligible activity across the agreed window | Verify telemetry and owner; recommend review |
| **Underutilized / over-provisioned** | Provisioned requests/capacity materially exceed observed demand, including relevant peaks and cycles | CPU p95 is low relative to request for several representative weeks | Recommend right-sizing review, not deletion |
| **Orphaned** | No valid owner or parent relationship can be established | Unattached volume with no matching workload or ticket | Resolve ownership and retention before action |
| **Zombie** | Still running or retained but apparently abandoned | Old notebook, stuck Job, forgotten preview environment | Confirm owner, schedule and dependencies |

These categories overlap. A forgotten development namespace may be idle, orphaned and zombie.


#### Decision table — evidence required before action

| Resource class | Minimum evidence before a recommendation | Additional approval / protection checks | Permitted first action |
|---|---|---|---|
| Stateless non-production Deployment | Fresh CPU/memory plus request/traffic evidence; schedule and dependency check; owner and GitOps source | No active release, no protected label, no tier-0 dependency; confirm restart path | Owner notification, then reversible quarantine |
| Batch Job / CronJob | Last successful run, next scheduled run, expected recurrence, queue/backlog state and owner | Cover weekly/monthly/quarterly cycles; inspect missed-run and retry behavior | Report and notify; do not infer deletion from age |
| PVC / PV / database / bucket | Mount/attachment state, data owner, backup/restore evidence, retention class and legal hold | Storage class, reclaim policy, snapshot/backup relationship, RPO/RTO, compliance approval | Report only; manual review and explicit data approval |
| Snapshot / backup / replica | Retention policy, restore-point coverage, DR relationship and last restore test | Legal hold, immutable retention, regional recovery plan | Report/tier recommendation only |
| Node / cluster | Pod placement, requests, allocatable capacity, PDBs, DaemonSets, local storage, topology, autoscaler state and headroom | N−1 / failure-domain capacity and disruption approval | Recommendation or controlled consolidation plan |
| Registry image / CI artifact | Last pull/use, deployment references, signature/provenance, release and rollback policy | Pinning, incident-forensic retention, active build references | Mark for retention review; never delete by age alone |
| GPU / notebook / experiment | GPU process/queue state, owner, experiment/run metadata, checkpoint and dataset provenance | Security anomaly check, reservation/queue intent, reproducibility and recovery | Notify owner; investigate suspicious activity before cleanup |
| Unknown-owner resource | Inventory provenance, dependency graph and ownership-registry lookup attempt | Platform escalation; unknown owner is not low risk | Escalate and retain pending review |

A detector must return `UNKNOWN` or `REVIEW` when telemetry is absent, stale, reset, or inconsistent. It must not translate “no sample” into a measured zero.
 An unmounted PVC may be orphaned but still legally retained. A Deployment with low CPU may be underutilized while still serving rare but critical requests.

#### 5.2.2 Where waste appears

- Unattached volumes and old snapshots (M05/M13).
- Unused load balancers and IP addresses.
- Idle databases, clusters and nodes.
- Development/test environments left running continuously.
- Over-requested Pods whose requests substantially exceed representative use.
- Idle GPUs, notebooks and model experiments (M15 Unit 12).
- Oversized instances or node shapes.
- Stale CI artifacts, runners and container images (M01/M02).
- Log, metric and trace retention beyond operational, security or compliance need (M11 Unit 12).
- Cross-region replicas with no consumer, while preserving declared DR/replication intent (M14).
- Abandoned namespaces, Helm releases and Argo Applications.
- Completed Jobs, stale CronJobs and PVCs no longer required.
- Forgotten port-forwards and LoadBalancer Services.
- Orphaned training artifacts, cached datasets and zombie experiments.

“Old” is not synonymous with “waste.” An image can be old and still be the only known-good rollback artifact. A snapshot can be old and still be required by retention policy.

#### 5.2.3 Detection signals

A useful detector combines signals from different domains:

| Signal family | Example evidence | Limitation |
|---|---|---|
| Compute | CPU/memory usage versus requests over 7–14 days or longer | Short windows miss monthly/quarterly work; metric gaps look like zero |
| Network | Near-zero ingress/egress or request count | No traffic may be expected for batch or standby |
| Storage | Last object access, last registry pull, PVC mount state | Access logs may be incomplete; retained data may be required |
| Lifecycle | TTL/expiry label, last deployment, last commit, last Job run | Git activity does not prove runtime use |
| Ownership | Missing, invalid or inactive owner | Registry may be stale |
| Kubernetes relationships | PVC not mounted, Service without endpoints, Ingress without requests | A disconnected resource may be intentionally staged |
| Scheduling | Suspended/never-succeeded Job, stale CronJob, missing TTL | A future schedule may be quarterly |
| Platform inventory | Last-used/utilization signals for instance, disk, snapshot, IP, LB or DB | Provider-specific fields and recommenders are `[VERIFY]` |

#### 5.2.4 Why idle detection is risky

A quiet resource may be:
- a quarterly financial or regulatory job;
- a DR standby or cross-region replica;
- a legal-hold or compliance archive;
- a break-glass or on-call-only tool;
- a canary or rare-use service;
- a cold cache awaiting scheduled input;
- a backup or security asset used only during an incident.

A false positive can cause data loss, missed reporting, longer recovery, a security blind spot or an SLO violation. The cost of the mistake can exceed the savings. Therefore, the correct output of an uncertain detector is **“needs owner review”**, not “delete.”

#### 5.2.5 Evidence window and confidence

An evidence window is the time interval over which observations are collected. The window must cover the resource's business cycle, not merely a convenient dashboard range. Seven days may cover weekdays and weekends; it does not necessarily cover monthly close or a quarterly run.

A simple confidence model is:

- **High:** several independent signals agree; metrics are fresh; owner is known; no hold/exemption; workload calendar has been checked.
- **Medium:** signals agree but ownership, schedule or telemetry is incomplete.
- **Low:** only one weak signal exists, data is stale, or a known exception is unresolved.

Confidence is not a probability unless calibrated against labelled outcomes. A label such as “high” is a decision aid, not a statistical guarantee.

#### 5.2.6 Cleanup safety ladder

```text
IDENTIFY
   ↓
CLASSIFY
   ↓
NOTIFY OWNER
   ↓
QUARANTINE (scale to zero / disable / rename / snapshot where appropriate)
   ↓
WAIT (owner response + scream-test / rollback window)
   ↓
DELETE (approved low-risk class only; bounded batch)
   ↓
VERIFY (health, data, dependencies, spend and SLO)
   ↓
RECORD (audit evidence, savings ledger, policy feedback)
```

| Stage | Required evidence | Gate / rollback |
|---|---|---|
| Identify | Inventory ID, source, timestamp, evidence window | Reject malformed or stale inventory |
| Classify | Resource class, signals, confidence, risk and exception check | Unknown risk → manual review |
| Notify | Owner, contact route, reason and response deadline | Unknown owner escalates to platform |
| Quarantine | Reversible action, dependency check, recovery path | Restore/scale back if impact appears |
| Wait | Business-cycle-aware delay and scream-test window | No deletion until window and approval pass |
| Delete | Explicit allow-list, action cap, approval and audit ID | Data-bearing resources require manual approval |
| Verify | Resource absent/disabled as intended; service/data intact | Restore from snapshot/GitOps if needed |
| Record | Before/after evidence, HCU estimate and realized outcome | Finance/FinOps validates savings claim |

#### 5.2.7 L1 lab seed

The local lab seeds an idle Deployment, an over-requested Pod, an unmounted PVC, an old namespace, a stale Job and a Service with no endpoints. It also seeds three false-positive traps: a quarterly job, a DR standby and a legal-hold PVC. The first report must classify and explain every item; it must not delete anything. Age or low CPU alone is never sufficient.

---

### 5.3 L2 — Intermediate: Working Practice

#### 5.3.1 Detection queries and scripts

**Over-provisioned workload ratio.** For a resource dimension with compatible units:

\[
R = \frac{p95(\text{observed usage over window})}{\text{requested capacity}}
\]

A low ratio can identify a review candidate, but the ratio must be calculated per container/workload and then aggregated carefully. Do not divide total usage by an unrelated sum of requests across different resource dimensions. Guard against zero/missing requests. Use p95 or another percentile appropriate to the service; averages hide bursts. A 7–14 day example window is only a starting point and must be extended to cover monthly or quarterly cycles.

PromQL-style pattern (metric names are `[VERIFY]` against the actual M11 instrumentation and exporter versions):

```promql
# Illustrative query shape only; confirm metric names and label joins.
quantile_over_time(
  0.95,
  (
    container_cpu_usage_seconds_total_rate
    /
    on (cluster, namespace, pod, container)
    container_cpu_request_cores
  )[14d:]
)
```

This is a query-shape teaching example, not a drop-in PromQL expression: actual counter-rate handling, request metrics, scrape interval, joins and missing-series behavior depend on the deployed metrics pipeline. A safe implementation should explicitly exclude zero denominators and surface missing data as `unknown`, not zero.

**Idle Pods/Deployments.** Combine CPU/network evidence with ingress or service-mesh request metrics where available. Confirm the workload has not been scaled down intentionally and that no batch schedule or external trigger exists. Distinguish “no requests” from “request telemetry unavailable.”

**Idle namespaces.** Check running Pods, recent Events, Jobs, Deployments, Services, PVCs, owner labels and GitOps source. A namespace with no running Pods can still contain retained data or a future scheduled Job.

**PVs/PVCs.** Reuse M05 Unit 8 patterns. Distinguish unbound, bound-but-unmounted, released and intentionally retained states using the actual Kubernetes version and reclaim policy `[VERIFY]`. Never delete a data-bearing PVC automatically in the first iteration.

**Images/artifacts.** Use registry pull recency and retention metadata. Preserve pinned images, rollback-critical digests, security-investigation artifacts and images referenced by supported releases.

**Nodes.** Compare utilization with requests and consider consolidation candidates for Unit 9. Check PDBs, DaemonSets, local storage, topology constraints, system overhead and autoscaler behavior before any node action.

**Jobs/CronJobs.** Inspect completion/failure state, owner, last run, next schedule, TTL behavior and whether the job is a one-off or recurring workflow. A suspended Job may be paused deliberately.

**Helm/Argo.** Verify sync/health, GitOps source, traffic and owner. Do not manually delete GitOps-managed objects without accounting for reconciliation; GitOps may recreate them.

**Cloud analogues.** Use a generic synthetic inventory schema for instances, disks, snapshots, IPs, load balancers and databases. Do not invent provider API field names. Real provider “last used” and recommender semantics are `[VERIFY]`.

#### 5.3.2 Normalized candidate schema

A waste report should include at least:

```csv
candidate_id,resource_type,resource_id,scope,owner,evidence_window,last_activity_utc,signals,estimated_monthly_hcu,confidence,risk_class,exemption,exemption_expiry,recommended_action,approver,next_review
C-001,deployment,dev-search,lab-dev,team-search,14d,2026-10-15T10:00:00Z,"low_cpu|zero_requests",18.0,high,low,none,,notify_then_quarantine,team-search,2026-11-08
C-002,pvc,legal-archive,lab-data,team-data,30d,unknown,"unmounted|legal_hold",7.0,low,critical,legal_hold,2027-01-31,retain_and_review,compliance,2026-12-01
```

This is `[SYNTHETIC]`. The `estimated_monthly_hcu` field is an estimate, not a guaranteed bill reduction.

#### 5.3.3 HCU estimate

A basic estimate is:

\[
\text{estimated monthly HCU}
=
\text{hypothetical hourly HCU rate}
\times
\text{estimated billable hours in period}
\]

Example `[SYNTHETIC]`: a non-production environment has a modeled rate of 0.8 HCU/hour and would otherwise run 10 hours/day for 22 working days:

\[
0.8 \times 10 \times 22 = 176\ \text{HCU}
\]

This is the modeled avoidable compute component only. It may exclude persistent disks, snapshots, network, load balancers, minimum database charges, commitments, support, shared overhead, startup time and data transfer. A scheduled environment may still incur storage and dependency costs while stopped.

#### 5.3.4 Scheduled non-production scale-down

A schedule is appropriate only when the workload has predictable operating hours, can restart safely, and has no hidden stateful dependency. Before scale-down:

1. verify owner and schedule;
2. stop or drain producers before consumers where relevant;
3. check queues and in-flight work;
4. ensure database and persistent data are safe;
5. preserve required backups;
6. scale stateless compute down;
7. verify it returns to service in the correct startup order.

Timezone and daylight-saving changes matter. Prefer an explicitly named timezone supported by the scheduling mechanism; do not assume a UTC schedule equals local business hours throughout the year. Validate DST transition dates in tests. KEDA cron syntax and timezone support are version-sensitive `[VERIFY]`; a Kubernetes CronJob can invoke a local scale script, but the script must be idempotent and state-aware.

#### 5.3.5 TTL for ephemeral environments

A TTL reaper should read an explicit expiry timestamp, owner and environment class. It should produce a report first, then quarantine eligible non-production namespaces, wait, and delete only after approval. A missing TTL is a governance defect, not automatic permission to delete. Preview environments per PR should have owner and PR metadata, expiry, exception route and cleanup evidence.

#### 5.3.6 Right-sizing recommendation to PR

Use percentile data to create a recommendation, not an unreviewed production mutation. A GitOps PR should include:
- baseline and proposed request values;
- p50/p95/p99 usage and peak window;
- startup and memory-growth evidence;
- HPA target impact;
- min/max bounds;
- load-test evidence and SLO comparison;
- rollback instructions.

Changing requests changes the denominator of CPU-utilization-based HPA targets. A request reduction can therefore change scaling behavior even if actual CPU usage remains the same. Coordinate with the M03 HPA configuration and validate the result.

#### 5.3.7 Safe cleanup automation

Required behavior:

- report-only is the default;
- explicit resource allow-list and protected-resource deny-list;
- owner notification stub;
- quarantine before deletion;
- deletion cap per run;
- dry-run output and audit record;
- kill switch;
- idempotency;
- exemptions with reason and expiry;
- manual approval for stateful/data-bearing resources;
- context and namespace checks;
- post-action verification.

The following Python example is a local decision simulator. It does not call Kubernetes or cloud APIs.

```python
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class Candidate:
    resource_id: str
    namespace: str
    resource_class: str
    owner: str
    expires_at: str
    confidence: str
    risk: str
    has_data: bool = False
    protected: bool = False

def eligible(candidate, now, allowed_namespaces):
    expiry = datetime.fromisoformat(candidate.expires_at.replace("Z", "+00:00"))
    return all([
        candidate.namespace in allowed_namespaces,
        candidate.resource_class == "ephemeral-namespace",
        candidate.owner != "",
        candidate.confidence == "high",
        candidate.risk == "low",
        not candidate.has_data,
        not candidate.protected,
        expiry <= now,
    ])

def plan_actions(candidates, *, now, allowed_namespaces,
                 dry_run=True, kill_switch=False, max_actions=2):
    if kill_switch:
        return [{"action": "BLOCKED", "reason": "kill_switch"}]
    plan = []
    for item in candidates:
        if not eligible(item, now, allowed_namespaces):
            plan.append({"resource_id": item.resource_id,
                         "action": "SKIP", "reason": "policy_not_satisfied"})
            continue
        if len([x for x in plan if x["action"] == "QUARANTINE"]) >= max_actions:
            plan.append({"resource_id": item.resource_id,
                         "action": "SKIP", "reason": "action_cap"})
            continue
        plan.append({"resource_id": item.resource_id,
                     "action": "REPORT" if dry_run else "QUARANTINE",
                     "owner": item.owner})
    return plan
```

A production controller would additionally need authenticated identity, Kubernetes API error handling, concurrency control, immutable audit storage, policy evaluation, retries, race protection and a tested rollback path. This simulator is not production-ready deletion automation.

---

### 5.4 L3 — Advanced: Production Engineering

#### 5.4.1 Define idle per resource class

There is no universal idle threshold. A Deployment, database, snapshot, registry image, GPU node and development namespace have different evidence and risk.

An illustrative rule might say: “CPU p95 below 10% of request for 14 days and no inbound requests during that window.” This is `[ILLUSTRATIVE]`, not a recommended global threshold. A batch workload may be inactive for 13 days and perform a critical monthly run on day 14. A database may have no request traffic while retaining data required by an application.

Every policy should specify:
- resource class and scope;
- required evidence sources and freshness;
- observation window and business-cycle coverage;
- thresholds and aggregation method;
- owner-resolution method;
- exclusion/hold classes;
- confidence and risk requirements;
- permitted actions and approval roles;
- quarantine and rollback window;
- verification and savings method;
- review date and policy version.

#### 5.4.2 Exemptions and retention annotations

An illustrative convention:

```yaml
metadata:
  annotations:
    finops.example/retain: "quarterly-close"
    finops.example/retain-until: "2027-01-31T00:00:00Z"
    finops.example/retain-owner: "finance-platform"
```

These are course-defined annotations, not built-in Kubernetes standards. A valid exemption must have a reason, owner, approver and expiry. Expired exemptions return to review; they do not silently become deletable. Legal holds and compliance retention require the appropriate policy authority, not a generic engineering override.

#### 5.4.3 Confidence and risk model

Keep confidence and risk separate:

- **Confidence** asks: “How strong is the evidence that this resource is unused or oversized?”
- **Risk** asks: “What is the consequence if we are wrong?”

A simple prioritization score can be:

\[
P = \frac{C \times W}{1 + R}
\]

where `C` is a numeric confidence score, `W` is estimated avoidable HCU over the review horizon, and `R` is a risk score. All values and weights are `[ASSUMPTION]`; this is a sorting aid, not a deletion authorization. High cost and high confidence cannot override a legal hold, tier-0 classification or stateful-resource restriction.

Use multiple independent signals. If telemetry is missing, stale or reset, lower confidence. If the owner is unknown, route to the platform team with a deadline. If the workload is security-sensitive or suspicious, use the security incident process rather than treating it as waste.

#### 5.4.4 Right-sizing at scale

Percentile-based recommendations must consider:
- peak and startup spikes;
- memory behavior of JVM/Python processes, including delayed reclamation;
- requests versus limits and CPU throttling;
- HPA utilization targets relative to requests;
- VPA recommendation mode and disruption behavior `[VERIFY]`;
- workload priority and queue wait;
- SLO/error budget and load-test results;
- node-level fragmentation and DaemonSet/system overhead.

Do not recommend requests based on p50 alone. Do not auto-apply a tier-0 recommendation. Generate a PR, run load tests, observe rollout health and retain rollback capacity.

#### 5.4.5 Waste domains and specialized controls

**Node-level waste:** low bin-packing efficiency and stranded resources feed M15 Unit 9. Do not remove a node until disruption budgets, local storage, topology, DaemonSets, system pods, autoscaler state and recovery capacity are understood.

**Storage waste:** over-provisioned PVCs may not be shrinkable in place; use the M05 Unit 3 migration approach. Snapshot sprawl and retention tiering must respect M13 Unit 2 backup and legal requirements. Never automatically delete PVCs, buckets, snapshots or database storage in the first iteration.

**Telemetry waste:** reuse M11 Unit 12 cost-driver reports. Reduce unused metrics/logs/traces only after checking incident response, security monitoring, audit and retention obligations.

**Registry/CI waste:** preserve signed and rollback-critical artifacts; apply retention and garbage collection from M01 Unit 7. For CI runners, use M02 Unit 10 lifecycle and ephemeral runner controls.

**Environment sprawl:** per-developer and per-PR environments should have owner, expiry, dependency graph and teardown proof. Sandbox clusters reuse M14 TTL patterns.

**ML waste:** idle notebooks/GPUs, abandoned experiments, orphaned training artifacts and cached datasets need owner, run/model metadata and reproducibility checks. GPU idleness alone does not establish that the node is safe to reclaim.

#### 5.4.6 Savings accounting

Distinguish four claims:

| Claim | Meaning | Evidence |
|---|---|---|
| Identified savings | Estimated cost associated with a candidate | Waste report and model assumptions |
| Forecast savings | Expected future cost reduction if the proposed action succeeds | Approved forecast with baseline and uncertainty |
| Avoided spend | Cost not incurred because an approved future action was prevented | Counterfactual model and event record |
| Realized/verified savings | Observed cost reduction after action, adjusted for demand, rate and scope changes | Before/after cost trend, allocation, usage and finance review |

Do not add identified and forecast savings as if they were separate realized savings. Give each candidate a stable savings ID and link it to one action. Verify after the action using a comparable time window and the Unit 4 allocation model. A scale-down that shifts cost to another team or leaves disks running is not full savings.

#### 5.4.7 Reliability guardrails

- Never auto-delete tier-0 or stateful resources.
- Canary cleanup on a small low-risk batch.
- Use a scream-test/quarantine period appropriate to business cycles.
- Preserve rollback through snapshot, GitOps redeploy or restore procedure.
- Verify service health, data integrity, dependency health and SLO after action.
- Stop cleanup experiments during active incidents or exhausted error budgets.
- Track false-positive rate and time to restore after a wrong cleanup.
- Review cleanup incidents without blame and convert findings into policy/tests.

#### 5.4.8 Security controls

The cleanup identity is powerful. Scope it to named namespaces/resource classes and explicit labels; use short-lived credentials; protect the allow-list and kill switch; audit every decision; and test that the controller cannot act outside its scope. Attackers may tamper with labels or abuse a cleanup identity. Unexpected high-CPU “idle-looking” workloads can indicate cryptomining or compromise; investigate with M12 security monitoring before cleanup.

---

### 5.5 L4 — Expert: Operating at Scale and Under Failure

#### 5.5.1 Program KPIs

| KPI | Formula | Source/window | Owner | Caveat |
|---|---|---|---|---|
| Idle/waste share | Candidate idle HCU ÷ in-scope HCU × 100 | Waste report + Unit 4 allocation; monthly | FinOps/platform | Candidate estimate is not realized savings |
| Over-provisioning ratio | Requests ÷ p95 usage, same resource and scope | Metrics + requests; rolling 14/30 days | Service owner | Undefined if p95 is zero/missing; use `unknown`, not infinity |
| Scheduled/TTL coverage | Eligible non-prod environments with valid schedule/TTL ÷ eligible environments | Inventory; monthly | Platform | Coverage does not prove safe restart |
| Orphan count/age | Count and age distribution of ownerless resources | Inventory; weekly | Platform | Aged orphan may be intentionally retained |
| Verified vs identified savings | Verified HCU / identified HCU | Savings ledger; monthly/quarterly | FinOps + Finance | Compare matching periods and avoid overlap |
| Cleanup false-positive rate | Incorrectly flagged/actioned candidates ÷ reviewed candidates | Review outcomes; quarterly | SRE | Labels depend on review completeness |
| Mean time to remediate | Mean time from confirmed finding to verified disposition | Ticket/audit system; monthly | Service/platform | Fast deletion is not necessarily good remediation |
| Idle cost per team | Idle HCU attributed by Unit 4 allocation | Showback; monthly | FinOps | Shared/idle allocation policy influences result |
| Cleanup automation SLO | Safe completed actions / eligible approved actions; plus restore-time objective | Audit + health checks; monthly | Platform/SRE | Define exclusions and action outcome states |
| Restore time | Time from detected cleanup harm to verified restoration | Incident record; per incident | SRE/service owner | Median and tail matter; report sample count |

Every KPI needs a denominator, scope, data freshness, owner and caveat. Do not set a target that encourages under-provisioning, hidden exemptions or false-negative classification.

#### 5.5.2 Automation maturity ladder

| Rung | Operating model | Entry criteria | Required evidence / approval | Rollback and exit criteria |
|---|---|---|---|---|
| 1. Manual reports | Humans inspect candidates | Inventory and owner data exist | Reproducible report, freshness and sample review | Remediate data gaps; move only after stable reports |
| 2. Owner tickets | Automated routing, human action | Owner registry and contact routes are maintained | Ticket evidence, expiry and owner disposition | Close stale tickets; measure response and false positives |
| 3. Non-prod quarantine | Reversible automation | Rung 2 outcomes demonstrate reliable classification | Allow-list, dry-run, cap, kill switch, audit, restore drill | Restore tested; zero out-of-scope actions |
| 4. Narrow low-risk auto-delete | Deletion for a tightly defined ephemeral class | Repeated successful quarantine and review | Written policy, approvals, small batches, no data-bearing resource | Immediate stop on false positive; restore path proven |
| 5. Continuous right-sizing | Recommendations/PRs and guarded rollout | Reliable percentile evidence and SLO test automation | PR review, HPA analysis, load test, rollback and post-change observation | Revert on SLO regression; demonstrate stable unit cost |

Progression is earned by evidence, not by elapsed time or management pressure.

#### 5.5.3 Fleet-scale operations

Analyze idle clusters, standby regions, per-cluster overhead and multi-cluster economics using M14 Unit 1. Compare consolidation with blast radius, isolation, noisy-neighbor risk, recovery and compliance. Ephemeral clusters with TTL reuse M14 Unit 2. On-demand infrastructure created through GitOps/IaC should have a time-to-ready SLO and a dependency startup plan.

A simple productivity model:

\[
\text{Net benefit HCU} =
\text{avoided infrastructure HCU}
-
\text{developer wait-time HCU}
-
\text{startup/operations HCU}
\]

All conversion rates are `[ASSUMPTION]`. If an environment takes too long to become ready, developers may create workarounds or leave it running. Always-on can be rational for shared dependencies or high-value developer workflows.

#### 5.5.4 Runaway/zombie incident response

For a forgotten large resource or suspected runaway workload:

1. Validate the signal, source freshness and scope.
2. Determine whether activity is suspicious; preserve evidence if compromise is possible.
3. Identify owner, dependencies, data, business purpose and DR role.
4. Contain safely without destroying forensic evidence.
5. Confirm recovery and retention implications.
6. Remove or right-size under the approved path.
7. Verify cost, service health, data integrity and SLO after action.
8. Prevent recurrence through TTL, budget, policy, ownership and monitoring.
9. Write a blameless postmortem with owners and due dates.

#### 5.5.5 Organizational mechanics

Include waste review in the monthly cost review. An engineering optimization-time budget can be proposed as `[ASSUMPTION]`, not treated as a universal requirement. Celebrate verified savings rather than projected numbers. Pair efficiency targets with SLO checks and load tests. Do not reward lower requests if they increase throttling, paging, latency or incident risk.

---

### 5.6 Worked examples and decision walkthroughs

All values in this section are `[SYNTHETIC]` and all cost values are HCU. They demonstrate the calculation method, not provider rates or universal policy thresholds.

#### Example 1 — Low CPU does not prove a quarterly workload is idle

A namespace shows CPU p95 near zero for 14 days. Its Job runs once every 90 days and the next quarterly close is scheduled in 4 days.

A 14-day detector sees no recent work and may assign a high idle score. The business calendar says the evidence window is incomplete: it does not include the workload's recurrence interval. The correct classification is `REVIEW — scheduled workload`, not `DELETE`.

**Decision:** preserve the Job and namespace, notify the owner, record the quarterly schedule and an expiry on the exemption, and review after the scheduled run. A scream test is not appropriate if the test itself could prevent a legally required report.

#### Example 2 — Request-to-p95 ratio and the zero-denominator problem

`[SYNTHETIC]` A stateless worker requests 1.0 CPU core. Its p95 CPU usage over a representative window is 0.18 cores.

\[
\text{usage ratio} = 0.18 / 1.0 = 0.18 = 18\%
\]

\[
\text{request-to-p95 ratio} = 1.0 / 0.18 \approx 5.56
\]

The request is about 5.56 times the observed p95. That is a right-sizing review candidate, not proof that the workload can safely run at 0.18 cores. Inspect p99, startup spikes, throttling, queue backlog, memory, HPA behavior, monthly peaks and load-test results. Propose a bounded GitOps change and verify it under representative load.

If p95 is exactly zero, the ratio is undefined (division by zero); if p95 is missing, the result is unknown. Do not report infinity or zero as a valid recommendation. Keep the candidate in `REVIEW — insufficient measurement`.

#### Example 3 — Scale-to-zero does not remove attached costs

`[SYNTHETIC]` A disposable development service has this modeled monthly cost:

| Component | Before | After scaling compute to zero |
|---|---:|---:|
| Compute | 300 HCU | 0 HCU |
| Persistent disk | 60 HCU | 60 HCU |
| Snapshot retention | 15 HCU | 15 HCU |
| Reserved network endpoint / IP analogue | 6 HCU | 6 HCU |
| **Total** | **381 HCU** | **81 HCU** |

\[
\text{compute saving} = 300 - 0 = 300\ \text{HCU}
\]

\[
\text{total reduction} = 381 - 81 = 300\ \text{HCU}
\]

The compute line fell to zero, but the environment still costs 81 HCU. The reduction is about 78.7% of the modeled total, not 100%. Actual savings must be checked against the relevant allocation/billing model; this example does not prove that the endpoint or storage charge is avoidable.

**Decision:** report compute savings separately from residual storage/network costs. Do not delete data-bearing resources to make the dashboard show zero.

#### Example 4 — Cost, confidence and risk prioritization

Use the illustrative triage formula:

\[
\text{priority score} =
\frac{\text{monthly avoidable HCU} \times \text{confidence score}}
{\text{risk score}}
\]

`[ILLUSTRATIVE]` Candidate A: 240 HCU × 0.90 ÷ 2 = 108. Candidate B: 900 HCU × 0.40 ÷ 9 = 40. Candidate A is reviewed first even though B has a larger headline cost.

The score is a queue-ordering aid, not a probability and not an authorization. A legal hold, DR designation, tier-0 classification, suspicious workload, or data-bearing resource is excluded by hard policy regardless of score.

#### Example 5 — Identified, forecast and realized savings

`[SYNTHETIC]` A candidate report identifies 100 HCU/month as potentially avoidable. After owner approval, the team forecasts 80 HCU/month savings because 20 HCU/month of attached costs will remain. The resource is quarantined and later removed under the approved process.

The post-action comparison window is not complete yet. The ledger therefore records:
- Identified opportunity: 100 HCU/month.
- Forecast saving: 80 HCU/month.
- Realized/verified saving: `PENDING`.
- Cost avoidance: recorded separately only if a documented future spend was prevented.

After a complete, comparable verification window, the observed allocated cost falls by 74 HCU after adjusting for workload volume and scope. Finance and the service owner validate the evidence. The realized value becomes 74 HCU for that period; the 80 HCU forecast is not added to it. If the cost merely moved to another resource/team, the moved portion is not a saving.

#### Example 6 — On-demand environment break-even includes developer waiting time

`[SYNTHETIC]` Compare one month of three models:

| Model | Infrastructure HCU | Startup/operations HCU | Engineer waiting-time HCU | Total HCU |
|---|---:|---:|---:|---:|
| Always-on | 240 | 0 | 0 | 240 |
| Scheduled | 120 | 5 | 0 | 125 |
| On-demand | 70 | 25 | 60 | 155 |

On-demand is cheaper than always-on, but it is not cheaper than scheduled in this scenario. Its waiting-time cost is based on `[ASSUMPTION]` 600 minutes of aggregate waiting and 0.1 HCU/minute.

Against scheduled operation, the on-demand model can spend at most 25 HCU on waiting time before its total exceeds 125 HCU:

\[
\text{break-even wait cost} = 125 - 70 - 25 = 30\ \text{HCU}
\]

\[
\text{break-even rate} = 30 / 600 = 0.05\ \text{HCU/minute}
\]

At 0.1 HCU/minute, scheduled operation wins. Always-on may still be rational if startup latency, shared dependencies, or developer productivity have higher business value than the modeled assumptions capture.

#### Example 7 — A request change changes utilization-based HPA behavior

`[SYNTHETIC]` A Deployment has 3 ready Pods. Simplified average CPU usage is 300 millicores per Pod; each Pod requests 500 millicores. A utilization target is 60%.

\[
\text{current utilization} = 300/500 = 60\%
\]

The simplified HPA ratio is 60%/60% = 1, so no replica increase is indicated by this metric.

Now reduce the request to 250 millicores while usage remains 300 millicores:

\[
\text{new utilization} = 300/250 = 120\%
\]

\[
\text{simplified desired replicas} =
\lceil 3 \times (120/60) \rceil = 6
\]

The same workload now appears to be at 120% of its request, so a utilization-based HPA can recommend more replicas. More replicas can increase total cost and downstream pressure. This arithmetic is a teaching simplification; actual HPA decisions also account for metrics availability, readiness, tolerance, stabilization and configured behavior. The Kubernetes HPA documentation describes utilization relative to requests and the ratio-based scaling calculation [VERIFY against the deployed version].

**Coordinated fix:** do not change requests in isolation. Review the request, target utilization, min/max replicas, startup behavior, downstream capacity and SLO together; submit a PR; load-test; canary; and retain rollback.

### 5.7 Failure modes, incident scenarios, and recovery

Each scenario follows the required incident structure. Values and names are illustrative; no production event is being claimed.

#### Incident 1 — Quarterly-report namespace deleted

- **Symptoms:** The cleanup bot removes a namespace after a quiet 14-day window. Four days later, the quarterly reporting job cannot start.
- **Impact:** A scheduled business/regulatory report is late; recovery work and possible data reconstruction exceed the estimated saving.
- **Evidence to collect:** Detector input and version, metrics freshness, namespace annotations, CronJob schedule, last successful run, owner notification, audit log, GitOps history, backups and report deadline.
- **Immediate containment:** Disable the cleanup identity or activate the kill switch; stop further namespace actions; preserve logs and snapshots.
- **Root cause:** The detector treated short-window inactivity as proof of abandonment and did not join the business calendar/owner registry.
- **Corrective action:** Restore the namespace from GitOps and restore required state/data from the approved recovery source; rerun the report with owner oversight.
- **Preventive control:** Resource-class evidence windows must cover the longest known business cycle; quarterly jobs require an expiring exemption and explicit schedule metadata; unknown schedules are review-only.
- **Verification metric:** Quarterly job success by deadline; false-positive cleanup rate; time to restore; no repeated action on protected test fixtures.

#### Incident 2 — Quiet-week right-sizing causes month-end OOM kills

- **Symptoms:** A request reduction passes a quiet-week check, then Pods restart with OOMKilled during month-end processing.
- **Impact:** Batch backlog grows, data freshness SLOs are missed, and retries increase compute consumption.
- **Evidence to collect:** Before/after requests and limits, memory working-set/peak, OOM events, GC behavior, container restarts, queue depth, month-end load profile, rollout and HPA history.
- **Immediate containment:** Roll back the GitOps change to the last known-good request/limit; pause further right-sizing; protect backlog and downstream dependencies.
- **Root cause:** The recommendation used an incomplete evidence window and did not model monthly peaks or memory growth.
- **Corrective action:** Recompute recommendations using representative cycles and startup/peak windows; run a month-end load/soak test before another rollout.
- **Preventive control:** No p50-only sizing; require percentile evidence, peak-window coverage, minimum bounds, staged rollout and SLO guardrails.
- **Verification metric:** OOM rate, restart rate, queue age, data freshness SLO and post-change p95/p99 memory headroom.

#### Incident 3 — HPA behavior changes after requests are halved

- **Symptoms:** Replica count rises after CPU requests are reduced; the service scales out more aggressively and total HCU rises.
- **Impact:** Node pressure and downstream connection pressure increase; spend rises without a corresponding demand increase.
- **Evidence to collect:** Old/new requests, HPA target and status, per-Pod CPU, desired/current replicas, readiness, metrics gaps, max replicas, downstream saturation and cost allocation.
- **Immediate containment:** Stop the rollout or revert the request change; do not simply raise max replicas to hide the symptom.
- **Root cause:** Request and HPA utilization target were reviewed separately even though utilization is calculated relative to requests.
- **Corrective action:** Recalculate the coordinated request/target pair, validate the capacity ceiling and test under representative load.
- **Preventive control:** Every request change with a utilization-based HPA requires a paired HPA impact calculation, PR review, load test and rollback plan.
- **Verification metric:** Replica count at matched load, HPA recommendation stability, latency/error SLO and HCU per request.

#### Incident 4 — Scheduled development shutdown loses database data or fails on restart

- **Symptoms:** The scheduled scale-down stops a development stack; on restart the database is unavailable, data is missing, or dependent services fail readiness.
- **Impact:** Developer work is lost, tests cannot run, and recovery consumes engineering time.
- **Evidence to collect:** Workload dependency graph, Pod/PVC/PV state, storage reclaim policy, database shutdown logs, backup/snapshot status, startup ordering and readiness events.
- **Immediate containment:** Stop the schedule; do not delete PVC/PV/snapshot objects; restore from the approved backup if required.
- **Root cause:** The schedule treated the namespace as stateless and ignored persistent-data and dependency semantics.
- **Corrective action:** Restore the database and dependencies in a controlled order; verify data integrity before admitting traffic.
- **Preventive control:** Stateful/protected workloads are denied by default; scale-down requires an approved shutdown/startup runbook, backup proof and readiness gates.
- **Verification metric:** Successful restart rate, data-integrity check, recovery time and number of protected workloads denied by policy.

#### Incident 5 — Unknown-owner resource deleted; it was DR standby

- **Symptoms:** An ownerless-looking resource disappears without quarantine; a DR exercise later discovers the standby is missing.
- **Impact:** Recovery capability and RTO/RPO posture are weakened; an incident may become unrecoverable within the intended objective.
- **Evidence to collect:** Resource inventory, region/cluster tags, replication/backup relationships, DR runbook, owner-registry lookup, deletion identity audit and restore-test evidence.
- **Immediate containment:** Stop automation; notify DR/platform/security owners; preserve remaining replicas and recovery metadata.
- **Root cause:** Missing ownership was interpreted as low risk rather than uncertainty, and the workflow lacked a quarantine window.
- **Corrective action:** Recreate/restore the standby under the DR plan; validate replication and perform a controlled recovery test.
- **Preventive control:** Unknown-owner resources route to platform escalation and remain protected until resolved; DR labels/registry entries have an accountable owner and expiry review.
- **Verification metric:** DR inventory completeness, restore-test pass rate, RTO/RPO validation and zero direct deletion of unknown-owner resources.

#### Incident 6 — Savings counted twice; Finance loses trust

- **Symptoms:** A node-level saving and the savings of Pods formerly running on that node are both reported as independent realized savings.
- **Impact:** The savings report exceeds the actual cost reduction; Finance disputes the program and future reports lose credibility.
- **Evidence to collect:** Candidate IDs, savings IDs, action IDs, parent/child resource relationships, allocation model version, invoice/allocation periods and before/after costs.
- **Immediate containment:** Freeze the disputed savings claim; publish a corrected pending/rejected status; retain the original audit trail.
- **Root cause:** The ledger lacked stable IDs and overlap rules for hierarchical/shared costs.
- **Corrective action:** Reconcile the claim to the single cost pool and correct the period-level ledger; obtain finance review.
- **Preventive control:** One canonical savings ID per economic change; parent/child overlap checks; separate identified, forecast, avoided and realized categories.
- **Verification metric:** Reconciliation variance, duplicate-claim test count and percentage of realized claims with before/after evidence.

#### Incident 7 — Broad cleanup permissions delete unlabelled production resources

- **Symptoms:** A reaper bug selects resources without the expected labels and the cleanup identity has permission to delete them.
- **Impact:** Production workloads or data are disrupted; audit and recovery work begins.
- **Evidence to collect:** IAM/RBAC bindings, service-account token use, policy/config version, selector expansion, API audit logs, target preview, resource dependencies and backup state.
- **Immediate containment:** Revoke/disable the cleanup identity, activate the kill switch, preserve audit evidence and follow incident response; do not erase evidence.
- **Root cause:** Broad permissions were treated as a substitute for policy validation; missing labels were not fail-closed.
- **Corrective action:** Restore affected workloads through GitOps/IaC and approved backups; rotate credentials; validate data integrity.
- **Preventive control:** Separate read/recommendation identity from destructive execution; narrow scope; explicit allow-list; deny-by-default; target preview; deletion cap; second-person approval for higher-risk actions.
- **Verification metric:** Negative RBAC/policy tests, out-of-scope action count (must remain zero), restore time and audit completeness.

#### Incident 8 — Idle-looking GPU node is a cryptominer or suspicious workload

- **Symptoms:** A GPU node appears to have no legitimate experiment owner, but compute/network activity remains unexpectedly high.
- **Impact:** Possible compromise, data exposure, credential abuse and denial-of-wallet; deleting the node immediately could destroy forensic evidence.
- **Evidence to collect:** Process/container identity, image provenance, node and workload audit events, network destinations, service-account use, experiment registry, GPU telemetry and security alerts.
- **Immediate containment:** Treat as a security incident; isolate according to the incident-response plan while preserving disk, process and audit evidence. Do not run ordinary cleanup first.
- **Root cause:** The waste detector considered owner/experiment metadata but did not correlate anomalous compute/network behavior with security telemetry.
- **Corrective action:** Security team investigates, removes malicious access, rebuilds from trusted artifacts and validates credentials/data integrity.
- **Preventive control:** Join FinOps inventory with M12 security monitoring; unknown GPU owners are escalated; suspicious activity routes to incident response, not deletion.
- **Verification metric:** Time to detect/contain, evidence preservation, unauthorized workload recurrence and post-incident credential/audit review.

### 5.8 Security, reliability, governance, and cost guardrails

#### SRE guardrails

- A cost action must preserve service SLOs, recovery objectives and capacity headroom.
- Do not remove tier-0 redundancy or DR standby through an automated waste policy.
- Use a small canary batch and stop on SLO regression.
- Measure cleanup false positives, restore time and post-action health.
- Do not schedule shutdown if it risks data loss, queue loss, missed freshness SLOs or excessive cold-start delay.
- Validate load after right-sizing; M11 Unit 13 remains the load-test reference.

#### Threat model and controls

| Threat | Mitigation | Evidence / negative test |
|---|---|---|
| Over-privileged cleanup identity | Namespace/resource-scoped RBAC, short-lived credentials, no wildcard delete | Attempt action outside allow-list; expect deny |
| Billing/inventory export exposure | Least-privilege read access, encrypted storage, scoped reports | Unauthorized reader cannot access raw export |
| Label tampering | Validate ownership registry and source metadata; do not trust mutable labels alone | Unknown/mismatched owner is blocked |
| Leaked credentials / denial-of-wallet | M09 identity controls, usage anomaly monitoring and incident route | Simulate suspicious creation; route to security |
| Unauthorized region/service | Preventive policy and inventory review | Disallowed resource is flagged/blocked by local contract |
| Unauthorized GPU use | GPU owner, quota, workload identity and usage audit | Unknown GPU owner is escalated |
| Cleanup-tool abuse | Protect policy, allow-list and kill switch; audit changes | Unauthorized policy change is rejected |

#### Governance rules

- Every in-scope resource class has an owner or a documented exception.
- Exemptions require reason, owner, approver and expiry.
- Cleanup policy changes are versioned and reviewed.
- Audit records include candidate, evidence, decision, actor, timestamp, action and verification.
- Data-bearing resources are excluded from automatic deletion in the first iteration.
- Reports are scoped to the appropriate teams; customer/tenant identifiers are not exposed broadly.
- Cost reduction targets are paired with SLO, capacity and security guardrails.
- Use a dispute process for false positives, incorrect ownership and savings attribution.

#### Hidden costs to inspect

Include persistent storage after compute shutdown, snapshots, backup retention, cross-region transfer, NAT/gateway processing, load balancers, idle IP analogues, log/metric ingestion, API requests, registry storage, CI artifact storage, minimum database charges and engineer wait time. The HCU model must state which components it includes and excludes.

---

### 5.9 Metrics, KPIs, and operating review

A KPI is useful only when its scope, denominator, data freshness and guardrail are explicit. Do not reward deletion count, request reduction or a lower utilization number in isolation.

| KPI | Definition and formula | Unit | Source / window | Owner / cadence | Guardrail | Limitation |
|---|---|---|---|---|---|---|
| Idle/waste share of spend | Candidate idle/avoidable HCU ÷ in-scope allocated HCU × 100 | HCU and % | Waste report + Unit 4 allocation; monthly | FinOps + platform; monthly | Track SLOs, DR and security exceptions beside the percentage | Candidate estimate is not realized savings |
| Over-provisioning ratio | Requested capacity ÷ p95 observed usage, same resource dimension and scope | Ratio, e.g. 5.56× | Requests + telemetry; 14/30 days and business-cycle window | Service owner; monthly | Never act on p50 alone; zero/missing p95 is `UNKNOWN` | Ratios across mixed units or workloads are invalid |
| Non-production schedule/TTL coverage | Eligible non-prod environments with valid schedule/TTL ÷ all eligible non-prod environments × 100 | % | Inventory + policy registry; monthly | Platform; monthly | Coverage does not prove safe restart; stateful exclusions reported separately | A label can be stale or false |
| Orphan count and age | Count plus median/p95 age of resources without valid owner/parent | Count and days | Inventory + owner registry; weekly | Platform/service catalog owner; weekly | Unknown-owner resources are escalated, not deleted | Registry freshness affects the count |
| Verified vs identified savings | Verified realized HCU ÷ identified opportunity HCU; report both totals too | HCU and % | Savings ledger + allocation/billing reconciliation; monthly/quarterly | FinOps + Finance; monthly | Only completed verification windows count as realized | Identified denominator changes as discovery improves |
| Cleanup false-positive rate | Incorrectly classified candidates ÷ reviewed candidates × 100; separately report harmful actions | % | Owner dispositions, incident and quarantine records; quarterly | SRE + platform; quarterly | Any harmful action triggers review/stop gate | Unreviewed candidates bias the rate |
| Mean time to remediate flagged waste | Mean time from confirmed candidate to verified disposition | Hours/days | Ticket and audit trail; monthly | Service owner + platform; monthly | “Delete faster” is not the objective; include restoration and SLO impact | Mean hides long-tail cases; publish p50/p95 |
| Idle cost per team | Idle/avoidable HCU attributed to team using Unit 4 rules | HCU/team/period | Unit 4 showback + waste report; monthly | FinOps + team owner; monthly | Show shared/unallocated cost and allocation model version | Allocation is a model, not causal truth |
| Cleanup automation SLO | Approved eligible actions completed safely ÷ approved eligible actions; also report policy-blocked and failed actions | % | Audit logs + health checks; monthly | Platform/SRE; monthly | No out-of-scope action; report false positives separately | A high success rate can hide a biased eligibility set |
| Mean time to restore | Time from harmful cleanup detection to verified service/data restoration | Minutes/hours | Incident records and restore checks; per incident + quarterly | SRE/service owner; quarterly | Include p50/p95 and data integrity, not only service readiness | Few incidents produce unstable statistics |

#### Operating review cadence

| Cadence | Review | Participants | Required output |
|---|---|---|---|
| Daily | High-cost candidates, suspicious activity, failed automation and kill-switch state | Platform/SRE/security on call | Triage, incident or ticket; no automatic deletion based only on daily review |
| Weekly | Missing owners, expiring TTLs/exemptions, stale telemetry, quarantine windows and partial failures | Platform + team champions | Updated candidate report and escalation list |
| Monthly | Idle HCU by team, verified savings, cost allocation, SLO impact, schedule coverage and optimization backlog | FinOps, engineering, finance, product as needed | Signed review record with decisions and owners |
| Quarterly | Business-cycle false-positive corpus, DR/legal exclusions, maturity rung, retention and policy thresholds | Platform, SRE, security, compliance, finance | Versioned policy review and exception renewal/expiry evidence |

**Interpretation rules:** publish the allocation model version; compare like-for-like periods; separate forecast from realized savings; show residual attached costs; report missing telemetry and unknown owners; and pair every efficiency result with reliability, security and recovery evidence.

### 5.10 Hands-on lab set

All ten labs use Cap-Core as the required path. They are designed to be run sequentially and re-used from one synthetic dataset. Optional Cap+Obs work must be sequenced and stopped after use. Estimated times are planning estimates, not guarantees.

#### Shared lab workspace

```text
idle-cleanup-lab/
├── README.md
├── inventory/
│   ├── resources.csv
│   ├── telemetry.csv
│   ├── ownership.csv
│   └── exceptions.yaml
├── detector/
│   ├── detect_waste.py
│   └── policy.py
├── cleanup/
│   ├── cleanup_simulator.py
│   └── safety_config.json
├── schedules/
│   ├── environment_schedule.yaml
│   └── timezone_cases.csv
├── savings/
│   ├── ledger.csv
│   └── verify_savings.py
├── tests/
│   ├── test_detector.py
│   ├── test_cleanup.py
│   ├── test_savings.py
│   └── test_schedules.py
└── evidence/
    ├── waste-report.md
    ├── false-positive-tests.txt
    ├── quarantine-audit.jsonl
    ├── savings-review.md
    └── cleanup-proof.txt
```

Create this workspace outside the supplied repository. Before optional `kubectl` work, record `kubectl config current-context`, `kind get clusters`, `kubectl get nodes`, Python version, and host disk/memory. If the context is not the disposable lab context, stop.


#### 5.10.1 Executable Cap-Core starter: one shared synthetic dataset

The following starter makes the core detection, report, dry-run, quarantine-simulation and savings-ledger checks reproducible without a cluster. It is deliberately a local teaching harness, not a production cleanup controller.

Create the workspace and save the code as `idle_lab.py`:

```bash
mkdir -p idle-cleanup-lab/evidence
cd idle-cleanup-lab
python --version
```

```python
# idle_lab.py — Python standard library only
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INVENTORY = ROOT / "resources.csv"
REPORT = ROOT / "evidence" / "waste-report.csv"
AUDIT = ROOT / "evidence" / "quarantine-audit.jsonl"
LEDGER = ROOT / "savings-ledger.csv"

FIELDS = [
    "candidate_id", "resource_type", "resource_id", "namespace", "owner",
    "last_activity_utc", "evidence_window_days", "signals", "monthly_hcu",
    "confidence", "risk", "has_data", "protected", "expires_at"
]

SAMPLE = [
    ["C-001","deployment","preview-search","lab-preview","team-search",
     "2026-10-01T08:00:00Z","30","cpu_low|requests_zero|ttl_expired","18.0","high","low","false","false","2026-10-15T00:00:00Z"],
    ["C-002","job","quarterly-close","lab-batch","team-finance",
     "2026-08-01T08:00:00Z","90","no_recent_run|quarterly_schedule","12.0","medium","critical","false","true","2027-01-31T00:00:00Z"],
    ["C-003","deployment","dr-standby","lab-dr","team-platform",
     "2026-09-01T08:00:00Z","60","low_traffic|dr_annotation","42.0","high","critical","false","true","2027-06-30T00:00:00Z"],
    ["C-004","pvc","legal-archive","lab-data","team-compliance",
     "unknown","120","unmounted|legal_hold","7.0","low","critical","true","true","2027-01-31T00:00:00Z"],
    ["C-005","job","stale-etl","lab-batch","team-data",
     "2026-09-01T08:00:00Z","30","failed|ttl_missing","9.0","medium","medium","false","false","2026-10-15T00:00:00Z"],
    ["C-006","service","orphan-lb","lab-preview","team-search",
     "2026-10-01T08:00:00Z","30","no_endpoints|no_requests","5.0","high","low","false","false","2026-10-15T00:00:00Z"],
    ["C-007","pod","oversized-worker","lab-ml","team-ml",
     "2026-10-31T08:00:00Z","30","request_to_p95_ratio_high","24.0","high","medium","false","false",""],
    ["C-008","gpu-node","gpu-experiment","lab-ml","team-ml",
     "2026-10-31T08:00:00Z","30","low_gpu_utilization|unknown_experiment_owner","80.0","low","high","false","false",""]
]

def read_inventory():
    with INVENTORY.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def seed():
    ROOT.joinpath("evidence").mkdir(exist_ok=True)
    with INVENTORY.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        w.writerows(SAMPLE)
    print(f"[SYNTHETIC] wrote {len(SAMPLE)} rows to {INVENTORY.name}")

def classify(row, now):
    signals = set(row["signals"].split("|"))
    protected = row["protected"].lower() == "true"
    has_data = row["has_data"].lower() == "true"
    if protected:
        return "HOLD", "explicit_protection"
    if has_data:
        return "HOLD", "data_bearing_manual_review"
    if row["confidence"] != "high":
        return "REVIEW", "confidence_not_high"
    if row["risk"] != "low":
        return "REVIEW", "risk_not_low"
    if "unknown_experiment_owner" in signals:
        return "REVIEW", "owner_or_purpose_unknown"
    if "ttl_expired" in signals:
        return "CANDIDATE", "ttl_expired_plus_signals"
    if "no_endpoints" in signals and "no_requests" in signals:
        return "CANDIDATE", "service_signals_agree"
    return "REVIEW", "insufficient_independent_evidence"

def report():
    now = datetime.now(timezone.utc)
    rows = read_inventory()
    REPORT.parent.mkdir(exist_ok=True)
    with REPORT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FIELDS + ["disposition", "reason", "estimated_monthly_hcu"])
        for row in rows:
            disposition, reason = classify(row, now)
            writer.writerow([row[k] for k in FIELDS] + [disposition, reason, row["monthly_hcu"]])
    print(f"[SYNTHETIC] report rows={len(rows)} path={REPORT.relative_to(ROOT)}")
    for row in rows:
        disposition, reason = classify(row, now)
        print(f'{row["candidate_id"]} {row["resource_id"]}: {disposition} ({reason})')

def build_quarantine_plan(rows, max_actions=1, dry_run=True,
                          allow_namespaces=None):
    allow_namespaces = set(allow_namespaces or {"lab-preview"})
    planned = []
    for row in rows:
        disposition, reason = classify(row, datetime.now(timezone.utc))
        if disposition != "CANDIDATE" or row["namespace"] not in allow_namespaces:
            continue
        if len(planned) >= max_actions:
            break
        planned.append({"candidate_id": row["candidate_id"],
                        "resource_id": row["resource_id"],
                        "namespace": row["namespace"],
                        "action": "REPORT" if dry_run else "QUARANTINE_SIMULATED",
                        "reason": reason})
    return planned

def quarantine_sim(max_actions=1, dry_run=True, allow_namespaces=None):
    planned = build_quarantine_plan(read_inventory(), max_actions, dry_run,
                                    allow_namespaces)
    AUDIT.parent.mkdir(exist_ok=True)
    with AUDIT.open("a", encoding="utf-8") as f:
        for item in planned:
            f.write(json.dumps(item, sort_keys=True) + "\n")
    print(json.dumps({"dry_run": dry_run, "action_cap": max_actions,
                      "planned": planned}, indent=2, sort_keys=True))

def check_ledger():
    if not LEDGER.exists():
        with LEDGER.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["savings_id","candidate_id","action_id","claim_type",
                        "baseline_hcu","observed_hcu","verified","owner"])
            w.writerow(["S-001","C-001","A-001","realized",18,6,"true","team-search"])
            w.writerow(["S-001","C-001","A-001","realized",18,6,"true","team-search"])
    with LEDGER.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    seen, duplicates = set(), []
    for row in rows:
        key = row["savings_id"]
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    print(json.dumps({"rows": len(rows), "duplicate_savings_ids": sorted(set(duplicates)),
                      "realized_verified_rows": sum(
                          r["claim_type"] == "realized" and r["verified"].lower() == "true"
                          for r in rows)}, indent=2))
    if duplicates:
        raise SystemExit("FAIL: duplicate savings claims detected")
    print("PASS: no duplicate savings IDs")

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("seed")
    sub.add_parser("report")
    q = sub.add_parser("quarantine-sim")
    q.add_argument("--apply-simulation", action="store_true",
                   help="records a simulated quarantine; never calls a cluster API")
    q.add_argument("--max-actions", type=int, default=1)
    sub.add_parser("ledger-check")
    args = parser.parse_args()
    if args.command == "seed":
        seed()
    elif args.command == "report":
        report()
    elif args.command == "quarantine-sim":
        quarantine_sim(max_actions=args.max_actions,
                       dry_run=not args.apply_simulation)
    elif args.command == "ledger-check":
        check_ledger()

if __name__ == "__main__":
    main()
```

Run the shared harness:

```bash
python idle_lab.py seed
python idle_lab.py report
python idle_lab.py quarantine-sim
python idle_lab.py quarantine-sim --apply-simulation --max-actions 1
```

Expected `[SYNTHETIC]` behavior: C-001 and C-006 are candidates; C-002 quarterly close, C-003 DR standby and C-004 legal-hold PVC are held; C-005 and C-008 require review; C-007 is a right-sizing candidate for a separate recommendation path, not deletion. The quarantine simulator records a local audit line and never calls Kubernetes or a cloud API.


Save as `test_idle_lab.py` in the same directory:

```python
import unittest
from datetime import datetime, timezone
from idle_lab import SAMPLE, FIELDS, classify, build_quarantine_plan

class DetectorTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 1, tzinfo=timezone.utc)
        self.rows = [dict(zip(FIELDS, row)) for row in SAMPLE]

    def test_expired_preview_is_candidate(self):
        result, _ = classify(self.rows[0], self.now)
        self.assertEqual(result, "CANDIDATE")

    def test_quarterly_job_is_held(self):
        result, reason = classify(self.rows[1], self.now)
        self.assertEqual((result, reason), ("HOLD", "explicit_protection"))

    def test_dr_standby_is_held(self):
        result, _ = classify(self.rows[2], self.now)
        self.assertEqual(result, "HOLD")

    def test_legal_hold_pvc_is_held(self):
        result, _ = classify(self.rows[3], self.now)
        self.assertEqual(result, "HOLD")

    def test_medium_confidence_is_not_candidate(self):
        result, _ = classify(self.rows[4], self.now)
        self.assertEqual(result, "REVIEW")

    def test_unknown_gpu_owner_is_review(self):
        result, _ = classify(self.rows[7], self.now)
        self.assertEqual(result, "REVIEW")

    def test_cleanup_plan_respects_namespace_and_cap(self):
        plan = build_quarantine_plan(
            [self._candidate("a", "lab-preview"),
             self._candidate("b", "lab-preview"),
             self._candidate("c", "other")],
            max_actions=1, dry_run=False,
            allow_namespaces={"lab-preview"}
        )
        self.assertEqual(sum(x["action"] == "QUARANTINE_SIMULATED" for x in plan), 1)
        self.assertTrue(all(x.get("action") != "QUARANTINE_SIMULATED" or
                            x["namespace"] == "lab-preview" for x in plan))

    @staticmethod
    def _candidate(resource_id, namespace):
        return {
            "candidate_id": resource_id, "resource_type": "namespace",
            "resource_id": resource_id, "namespace": namespace,
            "owner": "team-a", "last_activity_utc": "2026-10-01T00:00:00Z",
            "evidence_window_days": "30", "signals": "ttl_expired",
            "monthly_hcu": "1.0", "confidence": "high", "risk": "low",
            "has_data": "false", "protected": "false",
            "expires_at": "2026-10-31T00:00:00Z"
        }

if __name__ == "__main__":
    unittest.main()
```

Run the tests:

```bash
python -m unittest -v
```

The sample ledger intentionally contains a duplicate. `python idle_lab.py ledger-check` should fail until one duplicate row is removed. This is a negative test, not an error to ignore.

#### Lab-to-command map

| Lab | Cap-Core command / action | Required additional evidence |
|---|---|---|
| 1 | `python idle_lab.py seed && python idle_lab.py report` | Add tests for all three protected traps and telemetry gaps |
| 2 | `python idle_lab.py report` | Export report rows and aggregate by owner/resource class |
| 3 | Run the schedule worksheet and `python -m unittest discover -s tests -v` | DST cases and stateful dependency denial |
| 4 | `python idle_lab.py quarantine-sim` then `python idle_lab.py quarantine-sim --apply-simulation --max-actions 1` | Bug-injection and action-cap tests |
| 5 | Run percentile worksheet; generate PR proposal only | HPA target calculation and load-test evidence |
| 6 | `python idle_lab.py ledger-check` | Remove duplicate, re-run and retain both failure/pass evidence |
| 7 | Run risk-scoring worksheet | Prove protected resources cannot be ranked as delete-eligible |
| 8 | Run the throwaway kind restore drill, if available | Incident timeline and restore verification |
| 9 | Run policy contract and `kubectl auth can-i` only in verified kind context | Outside-allow-list negative test |
| 10 | Run environment-cost worksheet | Sensitivity and decision memo |

For optional cluster work, use the exact M03/M11 kind context and the namespace created for this unit. Do not copy deletion commands into a shared cluster. The local starter does not create or delete Kubernetes objects.

#### Lab 1 — Waste detection suite with false-positive traps

- **Goal:** Detect over-provisioned Pods, idle Deployments, unmounted PVCs, idle namespaces, zombie Jobs, Services without endpoints, stale releases/Applications and old registry images.
- **Prerequisites/profile/time:** Cap-Core; Python, CSV and optional existing kind cluster; 2–3 hours.
- **Assumptions:** `[SYNTHETIC]` one simulated monthly cycle; candidate thresholds are `[ILLUSTRATIVE]`.
- **Setup/steps:** Create synthetic inventory and telemetry rows for each resource class. Plant a quarterly job, DR standby and legal-hold PVC. Add expiry/retention metadata. Run detectors, classify candidates, and compare the output with a separate ground-truth manifest.
- **Expected result:** ordinary candidates appear with evidence; all three false-positive traps are excluded from destructive recommendation and remain visible as protected records.
- **Verification:** tests for missing metrics, zero denominators, stale data, quarterly schedule, DR annotation and legal hold.
- **Evidence:** `evidence/waste-report.md`, detector test output and false-positive fixture.
- **Cleanup:** remove only generated CSV and local test fixtures after preserving evidence.
- **Stretch:** add a stale Helm/Argo resource with GitOps source and demonstrate why manual deletion is unsafe.
- **Fidelity caveat:** synthetic telemetry does not validate actual Prometheus metric names or Kubernetes API behavior.

#### Lab 2 — Waste report generator and dashboard dataset

- **Goal:** Produce one normalized row per candidate with owner, evidence window, last activity, HCU estimate, confidence, risk, exemption, recommendation, approver and next review.
- **Prerequisites/profile/time:** Lab 1; Cap-Core; 1–2 hours.
- **Assumptions:** rate card is HCU-only; missing cost rates produce `unknown`, not zero.
- **Setup/steps:** Join inventory, telemetry, owner registry and synthetic rate card. Calculate monthly HCU and output CSV/Markdown. Create a dashboard-ready aggregate by team, resource class, risk and confidence.
- **Expected result:** every candidate has a traceable source and assumptions; protected candidates show their hold reason.
- **Verification:** totals reconcile to the input candidate set; unknown owners and missing telemetry remain explicit.
- **Evidence:** `waste-report.csv`, `waste-report.md`, dashboard dataset and assumptions register.
- **Cleanup:** remove generated outputs only after saving evidence.
- **Stretch:** compare candidate ranking under two confidence/risk weights.
- **Fidelity caveat:** dashboard aggregates are not a live billing or inventory integration.

#### Lab 3 — Scheduled scale-down/up for non-production

- **Goal:** Model a safe off-hours schedule and prove stateful workloads are not stopped unsafely.
- **Prerequisites/profile/time:** Cap-Core; optional disposable kind; 2 hours.
- **Assumptions:** schedule times and timezone are synthetic.
- **Setup/steps:** Define a development namespace schedule, dependency startup order, data safety checks and restart validation. Simulate weekday/weekend windows and DST transition cases. If using kind, scale only the lab Deployment.
- **Expected result:** stateless eligible Deployment scales down/up; stateful database/PVC workload is denied unless an explicit safe procedure exists.
- **Verification:** idempotent repeated execution; no scale-down while a protected job is active; DST test cases are recorded.
- **Evidence:** schedule matrix, test output and before/after Pod inventory.
- **Cleanup:** restore original replica count and delete only lab-owned resources.
- **Stretch:** compare CronJob orchestration with KEDA cron if already installed and verified.
- **Fidelity caveat:** controller timezone and DST behavior are version-sensitive `[VERIFY]`.

#### Lab 4 — TTL reaper with quarantine and bug injection

- **Goal:** Reuse the M07 cleanup framework to demonstrate report-only → quarantine → delete, with safeguards.
- **Prerequisites/profile/time:** Cap-Core; 2–3 hours.
- **Assumptions:** only ephemeral namespaces in the explicit lab allow-list are eligible.
- **Setup/steps:** Seed expired and non-expired namespaces, an unknown owner, a protected namespace and a malformed TTL. Run report-only. Then quarantine up to a small cap. Inject a bug that marks every namespace expired; prove the cap, allow-list, protected deny-list and kill switch block unsafe action.
- **Expected result:** only eligible lab resources are quarantined; no delete occurs in dry-run; bug injection cannot affect protected or out-of-scope resources.
- **Verification:** assert dry-run default, idempotency, max action count, audit record, owner notification stub and kill-switch behavior.
- **Evidence:** `quarantine-audit.jsonl`, negative-test report and bug-injection result.
- **Cleanup:** restore quarantined resources or delete only explicitly named lab namespaces after context verification.
- **Stretch:** add a second-person approval token to the local simulator.
- **Fidelity caveat:** this is a policy simulator, not a production reaper or Kubernetes controller.

#### Lab 5 — Right-sizing recommendation to GitOps PR

- **Goal:** Generate a recommendation from percentile usage and demonstrate HPA interaction.
- **Prerequisites/profile/time:** Cap-Core; optional Prometheus from M11; 2–3 hours.
- **Assumptions:** usage data is synthetic or measured locally; thresholds are illustrative.
- **Setup/steps:** Calculate p50/p95/p99 for a stateless workload. Generate a proposed request change and PR-style report. Show how a CPU utilization target relative to request changes after request reduction. Add startup-spike and minimum-bound checks.
- **Expected result:** recommendation is generated, not automatically applied; HPA impact and load-test requirement are explicit.
- **Verification:** reject p50-only sizing, zero/missing usage, request below policy minimum and tier-0 auto-apply.
- **Evidence:** recommendation JSON, PR summary, HPA calculation and tests.
- **Cleanup:** do not alter non-lab workloads; restore lab request values if changed.
- **Stretch:** add VPA recommendation comparison in recommendation-only mode `[VERIFY]`.
- **Fidelity caveat:** local request/HPA arithmetic is not proof of production scaling behavior.

#### Lab 6 — Savings ledger and double-counting detector

- **Goal:** Track identified, forecast, avoided and realized savings with unique identities.
- **Prerequisites/profile/time:** Cap-Core; 1–2 hours.
- **Assumptions:** all costs use HCU; baseline and comparison windows are defined.
- **Setup/steps:** Create a ledger with candidate ID, savings ID, action ID, owner, baseline, estimate, action date, verification period, observed change, confidence and finance sign-off. Add duplicate claims and overlapping resource scopes.
- **Expected result:** duplicate savings IDs and overlapping claims are flagged; only verified post-action amounts count as realized.
- **Verification:** unit tests for duplicate ID, missing baseline, negative saving, unverified claim and shifted cost.
- **Evidence:** ledger CSV, verification report and rejected duplicate examples.
- **Cleanup:** retain evidence; no external system is modified.
- **Stretch:** add a confidence interval or scenario range to the forecast claim.
- **Fidelity caveat:** the local ledger does not establish accounting treatment or invoice truth.

#### Lab 7 — Waste-versus-risk prioritization

- **Goal:** Prioritize candidates without allowing cost to override risk.
- **Prerequisites/profile/time:** Labs 1–2; Cap-Core; 1 hour.
- **Assumptions:** confidence, HCU and risk scores are `[ASSUMPTION]`.
- **Setup/steps:** Score a low-risk preview namespace, medium-risk idle database, high-risk DR standby and legal-hold PVC. Compare ranking with a cost-only ordering.
- **Expected result:** DR and legal-hold items are excluded regardless of modeled HCU; low-risk candidates are prioritized for review.
- **Verification:** protected classes never become delete-eligible even when their cost is highest.
- **Evidence:** prioritization worksheet and decision memo.
- **Cleanup:** remove temporary worksheet copies only.
- **Stretch:** conduct sensitivity analysis on risk weights.
- **Fidelity caveat:** a score is not an authorization or calibrated probability.

#### Lab 8 — Cleanup incident drill and recovery

- **Goal:** Restore an incorrectly quarantined resource and produce a blameless postmortem.
- **Prerequisites/profile/time:** Cap-Core; optional kind; 2 hours.
- **Assumptions:** a throwaway Deployment is the only target.
- **Setup/steps:** Quarantine a lab Deployment, inject a simulated complaint that a quarterly task needs it, restore it through the recorded rollback path, verify service and data state, then create corrective actions.
- **Expected result:** restore succeeds; the incident timeline distinguishes detection, acknowledgement, mitigation and verification.
- **Verification:** resource state matches pre-quarantine baseline; audit record contains actor, reason, action and result.
- **Evidence:** incident timeline, restore proof, postmortem and policy change.
- **Cleanup:** restore desired state, then delete only the lab namespace after checking context.
- **Stretch:** test GitOps reconciliation and prove that manual changes are not durable.
- **Fidelity caveat:** no production backup or restore mechanism is tested.

#### Lab 9 — Cleanup identity least-privilege exercise

- **Goal:** Demonstrate that the reaper identity cannot act outside approved scope.
- **Prerequisites/profile/time:** Cap-Core; optional kind RBAC; 2 hours.
- **Assumptions:** namespace and role names are lab-only.
- **Setup/steps:** Define an abstract policy contract and, if cluster versions are verified, a namespaced Role/RoleBinding limited to read/list/watch and narrowly scoped patch/delete for approved ephemeral resources. Test allowed namespace and forbidden namespace.
- **Expected result:** action in the allow-listed lab namespace succeeds in the simulator; outside-scope delete is denied.
- **Verification:** negative test for wildcard permissions, cluster-wide delete, protected namespace and expired credential simulation.
- **Evidence:** RBAC/policy contract, `kubectl auth can-i` outputs if run, and negative-test report.
- **Cleanup:** delete only named lab RBAC objects after checking references.
- **Stretch:** add policy-file integrity verification and change audit.
- **Fidelity caveat:** exact RBAC/API behavior must be checked against the learner's Kubernetes version; the abstract contract remains the required fallback.

#### Lab 10 — On-demand versus always-on environment model

- **Goal:** Compare always-on, scheduled and on-demand development environments, including developer wait-time and startup dependencies.
- **Prerequisites/profile/time:** Cap-Core; 1–2 hours.
- **Assumptions:** HCU rates, working hours and developer-time conversion are synthetic.
- **Setup/steps:** Model infrastructure HCU, persistent-data costs, startup time, dependency ordering, recovery needs and developer wait-time. Run at least three scenarios and vary utilization and startup duration.
- **Expected result:** decision memo explains when always-on or scheduled operation is rational; scale-to-zero is not assumed to be universally best.
- **Verification:** arithmetic reconciles; sensitivity analysis changes at least one decision boundary.
- **Evidence:** worksheet/script, scenario comparison and decision memo.
- **Cleanup:** remove generated local data only after saving the memo.
- **Stretch:** add an on-demand environment readiness SLO and report its breach rate.
- **Fidelity caveat:** productivity conversion is an assumption, not a measured wage or universal business value.

---

#### 5.10.11 Reproducible execution contracts for all ten labs

The earlier lab descriptions define the learning goals and shared synthetic fixture. The following contracts make the execution sequence, positive/negative tests, rollback and acceptance evidence explicit. All commands are run from `idle-cleanup-lab/`, never from the supplied repository. The helper script below is local-only and does not call Kubernetes or cloud APIs.

**Create the helper files**

```bash
mkdir -p idle-cleanup-lab/evidence idle-cleanup-lab/tests
cd idle-cleanup-lab
python --version
kubectl config current-context 2>/dev/null || true
```

Save the following as `supporting_exercises.py`:

```python
from math import ceil
from datetime import datetime
from zoneinfo import ZoneInfo

ALLOWED_TYPES = {"deployment", "job", "service", "ephemeral-namespace"}

def hpa_desired_replicas(current_replicas, usage_mcpu, request_mcpu, target_percent):
    if current_replicas < 1 or request_mcpu <= 0 or target_percent <= 0:
        raise ValueError("replicas, request and target must be positive")
    utilization = 100.0 * usage_mcpu / request_mcpu
    return ceil(current_replicas * utilization / target_percent)

def scale_down_allowed(*, stateless, protected, active_job, dependencies_stopped):
    return bool(stateless and not protected and not active_job and dependencies_stopped)

def cleanup_allowed(*, namespace, resource_type, verb, allow_namespaces,
                    allowed_types, protected, owner_known):
    return all([
        namespace in allow_namespaces,
        resource_type in allowed_types,
        verb in {"get", "list", "watch", "patch"},
        not protected,
        owner_known,
    ])

def environment_total_hcu(infrastructure_hcu, startup_ops_hcu,
                          wait_minutes, hcu_per_wait_minute):
    if min(infrastructure_hcu, startup_ops_hcu, wait_minutes,
           hcu_per_wait_minute) < 0:
        raise ValueError("cost and time inputs cannot be negative")
    return infrastructure_hcu + startup_ops_hcu + wait_minutes * hcu_per_wait_minute

def restore_snapshot(snapshot, current):
    return dict(snapshot)

def utc_instant(local_time, zone_name):
    zone = ZoneInfo(zone_name)
    if local_time.tzinfo is None:
        raise ValueError("provide an aware datetime with an explicit timezone")
    return local_time.astimezone(zone).astimezone(ZoneInfo("UTC"))

def idempotency_key(environment, scheduled_instant):
    return f"{environment}:{scheduled_instant.isoformat()}"

def validate_inventory(rows, now):
    """Validate synthetic candidate rows; no action is ever executed."""
    if not rows:
        return [], [{"resource_id": None, "errors": ["empty_input"]}], []
    counts = {}
    for row in rows:
        rid = str(row.get("resource_id", "")).strip()
        if rid:
            counts[rid] = counts.get(rid, 0) + 1
    accepted, rejected, review = [], [], []
    for row in rows:
        errors, review_reasons = [], []
        rid = str(row.get("resource_id", "")).strip()
        if not rid:
            errors.append("missing_resource_id")
        elif counts.get(rid, 0) > 1:
            errors.append("duplicate_resource_id")
        if not str(row.get("owner", "")).strip():
            errors.append("missing_owner")
        if row.get("resource_type") not in ALLOWED_TYPES:
            errors.append("unknown_resource_type")
        raw_ttl = str(row.get("expires_at", "")).strip()
        if not raw_ttl:
            errors.append("missing_ttl")
        else:
            try:
                ttl = datetime.fromisoformat(raw_ttl.replace("Z", "+00:00"))
                if ttl.tzinfo is None:
                    errors.append("ttl_timezone_missing")
            except ValueError:
                errors.append("malformed_ttl")
        raw_exemption = str(row.get("retain_until", "")).strip()
        if raw_exemption:
            try:
                exemption = datetime.fromisoformat(raw_exemption.replace("Z", "+00:00"))
                if exemption.tzinfo is None:
                    errors.append("exemption_timezone_missing")
                elif exemption <= now:
                    review_reasons.append("expired_exemption_requires_owner_review")
            except ValueError:
                errors.append("malformed_exemption")
        if errors:
            rejected.append({"resource_id": rid or None, "errors": errors})
        elif review_reasons:
            review.append({"resource_id": rid, "reasons": review_reasons})
        else:
            accepted.append(dict(row))
    return accepted, rejected, review

def bounded_quarantine_plan(rows, allow_namespaces, max_actions):
    if max_actions < 0:
        raise ValueError("max_actions cannot be negative")
    plan, skipped = [], []
    for row in rows:
        if row.get("namespace") not in allow_namespaces:
            skipped.append((row.get("resource_id"), "outside_allow_list"))
        elif len(plan) >= max_actions:
            skipped.append((row.get("resource_id"), "deletion_or_action_cap"))
        else:
            plan.append({"resource_id": row["resource_id"], "action": "QUARANTINE_SIMULATED"})
    return plan, skipped

def simulate_partial_failure(actions, fail_at):
    """Simulate a controller failure; return completed actions and explicit partial state."""
    completed = []
    for index, action in enumerate(actions):
        if index == fail_at:
            return completed, {"partial_failure": True, "failed_action": action}
        completed.append(action)
    return completed, {"partial_failure": False, "failed_action": None}

```

Save the following as `test_supporting_exercises.py`:

```python
import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from supporting_exercises import (
    hpa_desired_replicas, scale_down_allowed, cleanup_allowed,
    environment_total_hcu, restore_snapshot, utc_instant, idempotency_key,
    validate_inventory, bounded_quarantine_plan, simulate_partial_failure
)

NOW = datetime(2026, 11, 2, tzinfo=timezone.utc)

def valid_row(**overrides):
    row = {
        "resource_id": "r-1", "resource_type": "deployment",
        "namespace": "idle-cleanup-lab", "owner": "team-a",
        "expires_at": "2026-11-30T00:00:00Z", "retain_until": ""
    }
    row.update(overrides)
    return row

class Unit5SupportTests(unittest.TestCase):
    def test_hpa_request_change_changes_utilization(self):
        self.assertEqual(hpa_desired_replicas(3, 300, 500, 60), 3)
        self.assertEqual(hpa_desired_replicas(3, 300, 250, 60), 6)

    def test_hpa_rejects_zero_request(self):
        with self.assertRaises(ValueError):
            hpa_desired_replicas(3, 300, 0, 60)

    def test_stateful_or_protected_environment_is_not_scaled_down(self):
        self.assertFalse(scale_down_allowed(stateless=False, protected=False,
                                            active_job=False, dependencies_stopped=True))
        self.assertFalse(scale_down_allowed(stateless=True, protected=True,
                                            active_job=False, dependencies_stopped=True))

    def test_stateless_idle_environment_can_be_scheduled(self):
        self.assertTrue(scale_down_allowed(stateless=True, protected=False,
                                           active_job=False, dependencies_stopped=True))

    def test_cleanup_denies_outside_allow_list(self):
        self.assertFalse(cleanup_allowed(
            namespace="production", resource_type="deployment", verb="patch",
            allow_namespaces={"idle-cleanup-lab"}, allowed_types={"deployment"},
            protected=False, owner_known=True))

    def test_cleanup_denies_data_and_delete_verb(self):
        self.assertFalse(cleanup_allowed(
            namespace="idle-cleanup-lab", resource_type="pvc", verb="patch",
            allow_namespaces={"idle-cleanup-lab"}, allowed_types={"deployment"},
            protected=False, owner_known=True))
        self.assertFalse(cleanup_allowed(
            namespace="idle-cleanup-lab", resource_type="deployment", verb="delete",
            allow_namespaces={"idle-cleanup-lab"}, allowed_types={"deployment"},
            protected=False, owner_known=True))

    def test_unknown_owner_and_protected_resource_are_denied(self):
        common = dict(namespace="idle-cleanup-lab", resource_type="deployment",
                      verb="patch", allow_namespaces={"idle-cleanup-lab"},
                      allowed_types={"deployment"})
        self.assertFalse(cleanup_allowed(**common, protected=False, owner_known=False))
        self.assertFalse(cleanup_allowed(**common, protected=True, owner_known=True))

    def test_environment_model_includes_wait_time(self):
        self.assertEqual(environment_total_hcu(70, 25, 600, 0.1), 155)

    def test_restore_returns_snapshot_state(self):
        before = {"replicas": 2, "image": "demo:v1"}
        changed = {"replicas": 0, "image": "demo:v1"}
        self.assertEqual(restore_snapshot(before, changed), before)
        self.assertEqual(changed["replicas"], 0)

    def test_timezone_conversion_is_explicit(self):
        local = datetime(2026, 11, 2, 9, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
        self.assertEqual(utc_instant(local, "Asia/Kolkata").hour, 3)
        self.assertEqual(utc_instant(local, "Asia/Kolkata").minute, 30)

    def test_schedule_idempotency_key_is_stable(self):
        instant = datetime(2026, 11, 2, 9, 0, tzinfo=ZoneInfo("UTC"))
        self.assertEqual(idempotency_key("dev-a", instant), idempotency_key("dev-a", instant))

    def test_empty_input_is_rejected(self):
        accepted, rejected, review = validate_inventory([], NOW)
        self.assertEqual(accepted, [])
        self.assertEqual(rejected[0]["errors"], ["empty_input"])

    def test_malformed_ttl_is_rejected(self):
        accepted, rejected, _ = validate_inventory([valid_row(expires_at="not-a-date")], NOW)
        self.assertEqual(accepted, [])
        self.assertIn("malformed_ttl", rejected[0]["errors"])

    def test_duplicate_ids_are_rejected(self):
        accepted, rejected, _ = validate_inventory([valid_row(), valid_row()], NOW)
        self.assertEqual(accepted, [])
        self.assertEqual(len(rejected), 2)
        self.assertIn("duplicate_resource_id", rejected[0]["errors"])

    def test_missing_owner_is_rejected(self):
        _, rejected, _ = validate_inventory([valid_row(owner="")], NOW)
        self.assertIn("missing_owner", rejected[0]["errors"])

    def test_missing_ttl_is_rejected(self):
        _, rejected, _ = validate_inventory([valid_row(expires_at="")], NOW)
        self.assertIn("missing_ttl", rejected[0]["errors"])

    def test_expired_exemption_goes_to_review_not_action(self):
        accepted, rejected, review = validate_inventory(
            [valid_row(retain_until="2026-10-01T00:00:00Z")], NOW)
        self.assertEqual(accepted, [])
        self.assertEqual(rejected, [])
        self.assertIn("expired_exemption_requires_owner_review", review[0]["reasons"])

    def test_unknown_resource_type_is_rejected(self):
        _, rejected, _ = validate_inventory([valid_row(resource_type="mystery")], NOW)
        self.assertIn("unknown_resource_type", rejected[0]["errors"])

    def test_action_cap_and_allow_list(self):
        rows = [valid_row(resource_id="a"), valid_row(resource_id="b"),
                valid_row(resource_id="c", namespace="outside")]
        plan, skipped = bounded_quarantine_plan(rows, {"idle-cleanup-lab"}, 1)
        self.assertEqual(len(plan), 1)
        self.assertIn(("b", "deletion_or_action_cap"), skipped)
        self.assertIn(("c", "outside_allow_list"), skipped)

    def test_partial_failure_is_reported(self):
        completed, status = simulate_partial_failure(["a", "b", "c"], fail_at=1)
        self.assertEqual(completed, ["a"])
        self.assertTrue(status["partial_failure"])
        self.assertEqual(status["failed_action"], "b")

if __name__ == "__main__":
    unittest.main()

```

Run:

```bash
python -m unittest -v
```

Representative expected result: all 20 support tests pass. This is an expected result for the learner to verify, not a test run performed while authoring this document.

| Lab | Resource budget | Numbered execution sequence | Positive test | Negative test / injected failure | Evidence and success criterion | Teardown / rollback |
|---|---|---|---|---|---|
| **1 — Detection suite** | Cap-Core: local CSV/JSON only; no cluster objects. | 1. Run `python idle_lab.py seed`. 2. Run `python idle_lab.py report`. 3. Compare each candidate with the ground-truth fixture. 4. Add one missing-telemetry row and rerun. | Eligible expired preview appears as a review/quarantine candidate with evidence. | Quarterly, DR and legal-hold fixtures are never action candidates; missing telemetry is `UNKNOWN`. | Save report, fixture and test output; every fixture has a disposition and reason. | Delete only generated CSV/report files after evidence is copied; no cluster action. |
| **2 — Waste report/dashboard** | Cap-Core: local files and standard-library Python only. | 1. Join inventory, telemetry, ownership and HCU rate fixtures. 2. Export CSV and Markdown. 3. Aggregate by owner and class. 4. Run malformed-row tests. | Valid row has owner, evidence window, HCU, confidence, risk and recommendation. | Missing owner, missing rate, malformed timestamp, duplicate ID and unknown class are rejected or explicitly marked unknown—not silently defaulted. | Report row count equals accepted + rejected rows; HCU totals reconcile to accepted records. | Remove generated exports only; retain fixtures and validation report. |
| **3 — Scheduled scale-down/up** | Cap-Core local simulation; optional one small disposable Deployment in kind. | 1. Create a schedule matrix with timezone and dependency order. 2. Run `python -m unittest -v`. 3. Simulate a missed run and retry using the same idempotency key. 4. If using kind, scale only the named disposable Deployment after context/namespace/target preview. | Stateless lab Deployment scales down/up and passes readiness before traffic. | Stateful/PVC-backed, protected, active-job or dependency-not-stopped cases are denied; duplicate schedule execution is idempotent. | Save schedule matrix, DST cases, readiness checks and before/after inventory. | Restore original replicas; verify readiness; delete only named lab resources. |
| **4 — TTL reaper** | Cap-Core: local simulator only; zero API credentials. | 1. Run report-only. 2. Print target list. 3. Verify namespace allow-list. 4. Run quarantine simulation with cap 1. 5. Inject an all-expired fixture and rerun tests. | Only named disposable resources enter the quarantine plan. | Cap overflow, malformed/missing TTL, expired exemption, unknown owner and out-of-allow-list resources cannot be actioned. | Save plan, target preview, audit log, cap test and kill-switch test. | Restore quarantined lab state; never auto-delete PVC, bucket, snapshot or database. |
| **5 — Right-sizing / HPA** | Cap-Core: synthetic telemetry and PR file; optional existing M11 Prometheus, stopped after use. | 1. Record p50/p95/p99 and startup peak fixture. 2. Run HPA arithmetic tests. 3. Generate a PR patch/report, not a live mutation. 4. Review min/max and SLO gates. | Recommendation includes percentile, peak, minimum bound and paired HPA analysis. | p50-only, zero/missing denominator, below-minimum request and tier-0 auto-apply are rejected. | Save recommendation JSON, PR stub, HPA before/after calculation and load-test plan. | Revert only lab fixture/manifest changes; no tier-0 or shared workload is changed. |
| **6 — Savings ledger** | Cap-Core: local CSV/JSON fixtures only. | 1. Seed duplicate and overlapping claims. 2. Run `python idle_lab.py ledger-check`. 3. Remove the duplicate in a copy. 4. Run again and inspect pending claims. | Unique, verified claim reconciles to one action and period. | Duplicate ID, node+Pod overlap, partial period, missing before/after and residual attached cost are rejected or pending. | Save ledger, accepted/rejected report and reconciliation evidence. | Restore original synthetic ledger from fixture; no finance system is touched. |
| **7 — Waste vs risk** | Cap-Core: worksheet/script only. | 1. Score the four required candidate classes. 2. Sort by score. 3. Apply hard exclusions after ranking. 4. Write owner/approver decision memo. | Low-cost/high-confidence/low-risk candidate is reviewed early. | High-cost/low-confidence/high-risk, DR/legal hold and unknown owner cannot become delete-eligible. | Save score assumptions, sensitivity table and signed-off mock decision memo. | Remove only temporary worksheet output. |
| **8 — Incident recovery** | Cap-Core local snapshot fixture; optional one throwaway Deployment. | 1. Save the throwaway Deployment desired state as a JSON fixture. 2. Simulate quarantine. 3. Run `restore_snapshot` test. 4. Verify service/readiness and data fixture checksum. 5. Write postmortem and regression test. | Restored state matches the saved desired-state fixture and checksum. | Missing snapshot, mismatched checksum or failed readiness stops the drill and escalates; do not claim successful recovery. | Save timeline, restore proof, checksum, postmortem and policy regression test. | Restore desired state; if kind is used, inspect target list and remove only lab-owned objects. |
| **9 — Least-privilege identity** | Cap-Core wrapper-policy tests; optional namespaced Role/RoleBinding in kind. | 1. Define allowed namespace/type/verb contract. 2. Run wrapper policy tests. 3. If using kind, inspect exact Role/RoleBinding and run `kubectl auth can-i` for the reaper service account. | Read/list/watch and narrowly scoped patch in the approved namespace succeeds where configured. | Outside namespace, PVC/data type, `delete`, wildcard and unrelated privileged actions are denied. | Save policy contract, RBAC YAML, `can-i` output and negative tests. | Delete only named lab Role/RoleBinding after confirming no other subject depends on them. |
| **10 — Environment economics** | Cap-Core: local worksheet/script only. | 1. Enter synthetic always-on/scheduled/on-demand HCU. 2. Add start count, wait minutes and startup/operations HCU. 3. Run sensitivity at multiple wait-time rates. 4. Write a decision memo. | Model identifies the lowest total cost under the stated assumptions. | Missing persistent-data cost, zero/negative inputs and hidden developer wait time invalidate the comparison. | Save worksheet, break-even formula, sensitivity and decision memo. | Remove generated worksheet copies after retaining evidence. |

**Resource budget:** Cap-Core uses Python standard library and synthetic files; no cluster is required for the ten core outcomes. Optional kind exercises use only the existing small disposable cluster and the dedicated namespace. Do not start Prometheus/Grafana/OpenCost/KEDA together for this unit. Stop optional components after the relevant lab. Measure local CPU, memory and disk rather than assuming a fixed footprint.

**Rollback and abort conditions:** stop immediately if the current context is not the disposable lab context, a target is not in the printed allow-list, the owner/retention record is unknown, telemetry is stale, the audit write fails, the deletion cap is exceeded, an SLO/health check fails, a suspicious workload is detected, or a stateful dependency cannot be proven safe. The required Cap-Core path never deletes a Kubernetes object; its “quarantine” and “delete” demonstrations are local simulations.


### 5.11 Self-check questions

Answer before reading the key. A strong answer names the evidence, the risk and the next safe action.

1. **Differentiate idle, underutilized, orphaned and zombie. Can one resource have multiple labels?**  
   **Answer:** Idle means no useful work over a defined evidence window; underutilized means provisioned/requested capacity materially exceeds representative use; orphaned means no valid owner/parent is known; zombie means apparently abandoned but still running/retained. Yes: a forgotten preview namespace can be idle, orphaned and zombie.  
   **Tempting wrong answer:** “They all mean unused.” That ignores ownership and the difference between waste and over-provisioning.

2. **Why is 14 days of near-zero CPU insufficient to delete a namespace?**  
   **Answer:** The workload may be quarterly, event-driven, DR standby, security-related or waiting for scheduled input. The evidence window must cover its business cycle and include independent traffic, schedule, owner and dependency checks.  
   **Tempting wrong answer:** “Fourteen days is long enough for every workload.” No universal window covers all recurrence intervals.

3. **What should a detector do when metrics are missing or stale?**  
   **Answer:** Mark the signal `UNKNOWN`, lower confidence, record telemetry health and route for review. Missing data is not zero usage.  
   **Tempting wrong answer:** “Treat missing as zero so the report remains complete.” This converts observability failure into a destructive false positive.

4. **A PVC is unmounted and old. What must be checked before any cleanup?**  
   **Answer:** Owner, data classification, legal hold, backup/snapshot, restore test, PV reclaim policy, storage class/platform semantics, DR/RPO/RTO and manual approval. Data-bearing resources are not auto-deleted in the first iteration.  
   **Tempting wrong answer:** “Delete the PVC; Kubernetes will handle the disk.” The underlying storage may remain, be deleted, or be retained depending on the actual reclaim and provisioner behavior.

5. **Why can halving a CPU request change HPA behavior?**  
   **Answer:** Utilization is usage divided by request. With unchanged usage, a smaller request produces a larger utilization percentage and can change the replica recommendation. Coordinate request and HPA target, then load-test.  
   **Tempting wrong answer:** “HPA watches raw CPU only.” That is not true for utilization-based resource metrics.

6. **What is the difference between identified, forecast, realized and avoided savings?**  
   **Answer:** Identified is a candidate opportunity; forecast is expected reduction if the action succeeds; realized is measured after action over a comparable verification window; avoided is a documented counterfactual spend not incurred. Do not add the categories together.  
   **Tempting wrong answer:** “The detector found 100 HCU, so 100 HCU was saved.” Detection is not action or verification.

7. **Why is quarantine useful, and what is a scream test?**  
   **Answer:** Quarantine is a reversible stage that creates an observation/rollback window before deletion. A scream test is a controlled period in which owners/users can reveal hidden dependencies; it must have a defined notification route, window and restore method.  
   **Tempting wrong answer:** “Quarantine is just deletion with a delay.” It must be reversible and observable.

8. **What controls prevent a reaper bug from affecting resources outside its scope?**  
   **Answer:** Report-only default, explicit allow-list, protected-class deny rules, target preview, small deletion cap, kill switch, separate recommendation/destructive identities, least privilege, audit, owner approval and negative tests.  
   **Tempting wrong answer:** “A label selector is enough.” Labels can be missing, stale or tampered with; identity scope and policy validation are also required.

9. **A GPU node looks idle but has unexplained network and compute activity. What is the correct response?**  
   **Answer:** Treat it as a potential security incident, preserve evidence and follow M12 incident response. Do not run ordinary cleanup until compromise is ruled out and evidence is preserved.  
   **Tempting wrong answer:** “Delete it to stop waste.” That can destroy forensic evidence and leave the compromise uncontained.

10. **When can always-on or scheduled infrastructure be more rational than on-demand?**  
    **Answer:** When startup latency, developer wait time, shared dependencies, persistent state, recovery needs or high utilization outweigh the infrastructure reduction. Use an explicit HCU model and sensitivity analysis.  
    **Tempting wrong answer:** “Scale-to-zero is always cheapest.” It ignores attached costs and human/productivity costs.

### 5.12 Evidence artifacts

| Artifact | Required contents | Acceptance criteria |
|---|---|---|
| Inventory baseline | Resource IDs/types, scope, owner, creation/last activity and source | Reproducible and timestamped |
| Synthetic telemetry | CPU/memory/network/request evidence and data gaps | Deterministic; gaps not converted to zero |
| Exceptions registry | Quarterly, DR and legal-hold records with owner and expiry | Protected resources excluded from action |
| Waste report | Evidence window, HCU estimate, confidence, risk, recommendation | Every candidate traceable |
| Detection tests | Normal cases, missing metrics and false-positive traps | All protected cases rejected for deletion |
| Schedule evidence | Timezone, DST, dependency and data-safety tests | Stateful safety proven |
| Quarantine audit | Actor, resource, decision, dry-run, cap and notification | No out-of-scope action |
| Right-sizing PR | Baseline/proposed values, HPA impact and load-test plan | Recommendation-only, reviewable |
| Savings ledger | Unique IDs, baseline, action and verification | No duplicate claims; verified separated |
| Incident postmortem | Timeline, impact, cause, recovery and action owners | Blameless and testable prevention |
| Identity evidence | RBAC/policy and negative tests | Outside-scope action denied |
| Environment model | HCU, developer wait, startup and recovery | Sensitivity and decision memo included |
| Cleanup proof | Exact lab context and named resources removed/restored | No shared or production resource touched |

---

### 5.13 Common interview and design-review questions

Exactly five senior-level questions are included. The model answers emphasize judgment and production failure modes.

1. **Design an idle-resource detector that avoids deleting quarterly jobs, DR standby and legal-hold data.**  
   **Model answer:** Start with resource-class-specific evidence windows and multiple independent signals. Join metrics health, request/traffic, schedules, owner registry, dependency graph, TTL and explicit retention/DR metadata. Missing owner or telemetry means `REVIEW`, not `DELETE`. Protected classes are hard exclusions. The lifecycle is identify → classify → notify → quarantine → wait → approved action → verify → record. Use report-only by default, an allow-list, bounded batch, kill switch and audit trail. Validate the detector with planted quarterly/DR/legal-hold negative tests and measure false positives.

2. **How do you select an evidence window and confidence score for a resource class?**  
   **Model answer:** Begin with the resource's business recurrence and operational purpose, not a universal number of days. Include weekday/weekend patterns, weekly jobs, monthly close, quarterly work, seasonal demand and DR tests. Confidence should reflect independent signals, telemetry freshness, owner validity and schedule/retention checks. Unless calibrated against labelled outcomes, confidence is an ordinal triage score—not a probability. Publish assumptions, sample size and exceptions.

3. **What must be true before cleanup automation moves from report-only to destructive action?**  
   **Model answer:** Stable classification precision over a representative period; complete ownership/retention data; proven quarantine and restoration; negative tests for false-positive traps; explicit allow-list and deletion cap; scoped identity; protected data-bearing/tier-0/DR classes; target preview; approval and audit; kill switch; post-action SLO/data/cost verification; and a tested incident runbook. Begin with one narrow, low-risk ephemeral class. Do not auto-delete PVCs, buckets, snapshots or databases in the first iteration.

4. **How do you prove savings and avoid double-counting?**  
   **Model answer:** Assign a stable savings ID to one economic change, link it to a resource/action and period, define the baseline and allocation model, and separate identified, forecast, avoided and realized amounts. Compare like-for-like post-action periods and adjust for demand/rate/scope changes. Reconcile to the Unit 4 allocation/synthetic invoice model. Check parent/child overlap and residual attached costs. Only a complete, validated before/after result is realized savings; finance/service owners review the evidence.

5. **How do you right-size a workload with HPA enabled while protecting SLOs?**  
   **Model answer:** Use p95/p99 and startup/peak windows, inspect memory/GC, throttling, queue/backlog and downstream saturation, and calculate how the request change alters utilization-based HPA behavior. Generate a GitOps PR, preserve minimum bounds/headroom, coordinate HPA target and max replicas, then load/soak test and canary. Monitor latency/errors, OOMs, throttling, replica count, queue age and HCU per unit of work. Roll back if SLO or recovery guardrails regress. Never auto-apply to tier-0.

### 5.14 Sources and verification notes

#### Source hierarchy and continuity review

1. **Attached Unit 5 generation prompt:** source for the exact Unit 5 scope, verbatim handoff, mandatory section order, L1–L4 curriculum, eight incident scenarios, ten labs, HCU-only examples, zero-budget rules and audit requirements.
2. **Authoritative M15 syllabus-generation prompt:** `PROMPT-Platform-Capacity-Compute-Economics-and-FinOps.md`. Its Unit 5 scope and M15-wide rules were consulted. It defines the 15-unit sequence, L1–L4 progression, local-first stack profiles, HCU convention and cross-module boundaries.
3. **Earlier generated M15 teaching artifacts reviewed for continuity:**
   - Unit 1 — `01-platform-capacity-forecasting-and-headroom.md`: capacity/headroom assumptions, p95/p99, peak windows and simulation fidelity.
   - Unit 2 — `02-workload-priorities-quotas-and-resource-contention.md`: requests/limits, quotas, priority, contention, and the distinction between capacity governance and financial showback.
   - Unit 3 — `03-cloud-budget-alerts-and-spending-guardrails.md`: synthetic billing, HCU rate-card context, billing freshness, budget alerts and preventive guardrails.
   - Unit 4 — `04-cost-allocation-by-team-project-and-workload.md`: owner metadata, allocation rules, idle/unallocated treatment, reconciliation and showback.
4. **Roadmap limitation:** the latest Roadmap file referenced by the earlier Unit 5 draft (`Roadmap(20261031-181942).md`) was not independently retrievable in this review. Older `Roadmap_ptree` copies were found, but they predate the current M15 sequence and are not suitable evidence for the current Stage 2E tree. Therefore, the latest repository tree and exact on-disk target placement remain **OPEN / not independently verified**. The target filename and M15 ordering are supported by the attached prompt and authoritative M15 syllabus prompt, not by a claim of current Roadmap inspection.
5. **Earlier Unit 5 draft:** `05-idle-resource-detection-and-automated-cleanup.md` was used as the starting draft and reviewed for gaps. This revised artifact expands its incomplete worked calculations, incident structures, KPI specification, self-check answer keys, interview model answers and lab execution contracts.

#### Official documentation checked

- Kubernetes, **CronJobs**: schedule behavior, concurrency policy, missed schedules, suspension and time-zone handling. The current documentation states that `.spec.timeZone` is the supported time-zone field; scheduling is approximate and Jobs should be idempotent. Verify the installed Kubernetes version and controller configuration before adoption: <https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/> [VERIFY for deployed version].
- Kubernetes, **Horizontal Pod Autoscaling**: resource utilization is calculated relative to requests for utilization targets; the controller uses a ratio-based recommendation and accounts for readiness/missing metrics. Verify the API version and deployed controller behavior: <https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/> [VERIFY for deployed version].
- Kubernetes, **Persistent Volumes**: reclaim policy affects what happens after a claim is released; `Retain` leaves the underlying storage for manual reclamation, and PVC expansion/shrink behavior depends on the storage class and platform: <https://kubernetes.io/docs/concepts/storage/persistent-volumes/> [VERIFY for storage provisioner and class].
- Kubernetes, **RBAC**: consult the current authorization documentation before designing the actual service account, Role and RoleBinding. This unit's wrapper policy checks are application-level controls; do not assume standard RBAC can enforce arbitrary label predicates: <https://kubernetes.io/docs/reference/access-authn-authz/rbac/> [VERIFY].
- Prometheus, **Querying basics and functions**: verify PromQL range-vector, aggregation and percentile semantics and the actual metric names/labels emitted by the learner's instrumentation: <https://prometheus.io/docs/prometheus/latest/querying/basics/> and <https://prometheus.io/docs/prometheus/latest/querying/functions/> [VERIFY].

No live provider API, cloud “last used” field, pricing API, KEDA configuration, VPA mode, OpenCost metric/API, Helm/Argo lifecycle behavior or production RBAC policy was tested here. These remain `[VERIFY]`. No cloud account, real billing export, real provider price, production credential or billable resource was used.

#### Claim and verification register

| Claim / topic | Basis | Status | Caveat |
|---|---|---|---|
| Unit 5 target, scope and verbatim handoff | Attached Unit 5 prompt + M15 syllabus prompt | Source-derived | Roadmap tree not independently verified |
| M15 sequence and Unit 5 position | M15 syllabus prompt | Source-derived | Confirm against current repository Roadmap before merge |
| L1–L4 model and Cap-Core / Cap+Obs / Cap+Scale | M15 syllabus prompt | Source-derived | Optional components must be measured locally |
| HPA utilization relative to requests | Kubernetes HPA documentation | Checked; `[VERIFY]` deployed version | Simplified arithmetic omits controller details |
| CronJob timezone/concurrency/missed schedules | Kubernetes CronJob documentation | Checked; `[VERIFY]` deployed version | Controller downtime and DST require tests |
| PV/PVC reclaim and expansion semantics | Kubernetes PV documentation | Checked; `[VERIFY]` provisioner/class | Do not infer data deletion from PVC deletion alone |
| PromQL metric names and joins | Prometheus documentation + local M11 handoff | `[VERIFY]` instrumentation | Example query is a shape, not a drop-in query |
| KEDA cron and VPA recommendation behavior | Later M15 units / external tools | `[VERIFY]` | Not required for Cap-Core |
| Cloud last-used/utilization fields | Synthetic normalized inventory model | `[VERIFY]` provider-specific | No provider schema is asserted |
| HCU cost and savings arithmetic | Explicit synthetic rate/quantity assumptions | `[SYNTHETIC]` | Not an invoice or quote |
| Confidence/risk score | Teaching prioritization model | `[ASSUMPTION]` | Not calibrated probability or deletion permission |
| Data-bearing resources not auto-deleted in first iteration | Attached prompt safety contract | Mandatory policy | Manual approval and recovery proof still required |
| RBAC label/selector limitations | Authorization model and wrapper policy distinction | `[VERIFY]` actual cluster | Test the deployed authorization chain |

#### Final content audit

| Audit area | Result | Evidence / limitation |
|---|---|---|
| Unit 5 only; target filename and sequence | PASS for content scope | Target is Unit 5; latest Roadmap tree remains OPEN |
| Verbatim handoff | PASS | §5.1 |
| Mandatory headings/order | PASS | §5.0–§5.14; top-level Unit 5 heading aligned |
| L1–L4 coverage | PASS with verification caveats | §5.2–§5.5 |
| All required waste classes, sources and signals | PASS | §5.2–§5.3 |
| Eight incident scenarios with all required fields | PASS | §5.7 |
| Ten distinct labs | PASS for documented execution contracts | §5.10; learner must run them to produce measured evidence |
| Seven worked examples/calculations | PASS | §5.6 |
| KPI definitions/formulas/units/source/cadence/owner/guardrails/limitations | PASS | §5.9 |
| Self-checks with answer keys and tempting-wrong-answer explanations | PASS | §5.11 |
| Exactly five senior interview questions with model answers | PASS | §5.13 |
| HCU-only, zero-budget and no billable-resource requirement | PASS by content review | No real prices or currency symbols intended |
| Report-only, allow-list, caps, kill switch, audit and data-bearing protections | PASS by content review | Cap-Core actions are local simulations; no production controller is supplied |
| Official-source verification | PARTIAL | Kubernetes CronJob/HPA/PV pages checked; Prometheus/RBAC pages identified; provider/KEDA/VPA/OpenCost behavior remains `[VERIFY]` |
| Commands and tests actually executed | NOT CLAIMED | Code and representative outputs are instructions/expected results for the learner |
| Current Roadmap tree inspection | OPEN | Latest referenced Roadmap file not retrieved |
| Repository modification | NONE | This is a standalone output artifact; no repository file is claimed changed |

**Limitations:** The document is a local teaching artifact, not production-ready cleanup software. The Python examples are policy simulators; they do not authenticate to Kubernetes or cloud providers. A local `kind` cluster cannot prove provider billing, managed storage, production-scale controller reliability or real GPU performance. The Roadmap tree limitation must be closed before merging this file into the repository. All thresholds, HCU values and sample data are synthetic/illustrative. Version-sensitive behavior must be verified against the exact installed versions and official documentation.

