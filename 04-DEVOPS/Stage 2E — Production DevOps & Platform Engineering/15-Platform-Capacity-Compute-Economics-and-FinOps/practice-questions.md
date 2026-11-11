# M15 Practice Questions — Platform Capacity, Compute Economics, and FinOps

> Stage 2E — Production DevOps & Platform Engineering | Module M15 | Unit 13

**Target:** `15-Platform-Capacity-Compute-Economics-and-FinOps/practice-questions.md`  
**Source baseline:** Uploaded Roadmap, authoritative M15 prompt, Units 1–12, capstone specification and practice-question prompt.  
**Review date:** 2026-11-03 | **Status:** DRAFT-AUDITED; human/runtime verification remains open.

## Purpose, prerequisites and use

This is an answer-keyed assessment of concepts actually taught in M15 Units 1–12. The learner is assumed to know Kubernetes fundamentals, requests/limits, HPA, namespaces, quotas/placement, SLOs/error budgets, observability, load testing, cleanup safety, backup/DR and multi-region concepts from Stages 0–2D and M01–M14. Attempt each question before reading its answer. Record assumptions and evidence for all L3/L4 responses.

## Zero-budget, HCU and fidelity contract

- No question requires a cloud account, billable resource, real credential, paid FinOps product, real billing export or physical GPU. All amounts are HCU (Hypothetical Cost Units), never currency; every amount below is `[HYPOTHETICAL]`.
- `kind`/KWOK nodes are not priced cloud VMs; simulated GPUs do not demonstrate hardware performance; synthetic billing is not an invoice; local OpenCost output is not real spend.
- Budgets are alerts, not caps. Billing may lag. Allocation is a model and must reconcile without hiding residuals.
- Low utilization alone does not prove idleness. Data-bearing resources must never be automatically deleted.
- Automation must be dry-run-first, lab-scoped, allow-listed, bounded, auditable, reversible where possible and protected by a kill switch.
- Cost reductions must be evaluated against SLOs, latency, throughput, quality, queue wait, security and recovery.

## Difficulty levels and scoring

| Level | Definition |
|---|---|
| L1 | Define, distinguish, explain and recognize |
| L2 | Calculate, interpret artifacts and select methods |
| L3 | Diagnose multi-signal incidents and review flawed models |
| L4 | Design measurable policy, ownership, guardrails and residual-risk controls |

**Scoring gate:** ≥80% proceed to the capstone; 60–79% remediate weak topics; below 60% repeat relevant units and this bank. This is a learning gate, not certification or a hiring guarantee. Time estimates and thresholds are `[ILLUSTRATIVE]`.

## Shared running example and notation

A synthetic local data/ML platform contains online inference, batch ETL, streaming consumers, ML training, notebooks, CI/platform services, stateful storage and multi-region/DR. Teams need transparent showback. `HCU` is a teaching unit. `[SYNTHETIC]` means fabricated evidence; `[ASSUMPTION]` means a modeling choice; `[VERIFY]` means check the exact installed version/API.

| Generic rate card | Rate |
|---|---:|
| CPU allocation unit-hour | 1 HCU/hour `[HYPOTHETICAL]` |
| Memory allocation unit-hour | 0.25 HCU/hour `[HYPOTHETICAL]` |
| Simulated GPU-hour | 8 HCU/hour `[HYPOTHETICAL]` |
| Shared platform pool | 10 HCU/day `[HYPOTHETICAL]` |
Question-specific rates override this card. No rate is a provider price.

## Unit map

| Unit | Question IDs | Source file |
| 1. Platform capacity forecasting and headroom | U01-Q01–Q14 | [01-platform-capacity-forecasting-and-headroom.md](01-platform-capacity-forecasting-and-headroom.md) |
| 2. Workload priorities, quotas, and resource contention | U02-Q01–Q14 | [02-workload-priorities-quotas-and-resource-contention.md](02-workload-priorities-quotas-and-resource-contention.md) |
| 3. Cloud budget alerts and spending guardrails | U03-Q01–Q14 | [03-cloud-budget-alerts-and-spending-guardrails.md](03-cloud-budget-alerts-and-spending-guardrails.md) |
| 4. Cost allocation by team, project, and workload | U04-Q01–Q14 | [04-cost-allocation-by-team-project-and-workload.md](04-cost-allocation-by-team-project-and-workload.md) |
| 5. Idle resource detection and automated cleanup | U05-Q01–Q14 | [05-idle-resource-detection-and-automated-cleanup.md](05-idle-resource-detection-and-automated-cleanup.md) |
| 6. Cost, reliability, and performance trade-offs | U06-Q01–Q14 | [06-cost-reliability-and-performance-tradeoffs.md](06-cost-reliability-and-performance-tradeoffs.md) |
| 7. Capacity and cost review for production releases | U07-Q01–Q14 | [07-capacity-and-cost-review-for-production-releases.md](07-capacity-and-cost-review-for-production-releases.md) |
| 8. Spot and preemptible instances for data workloads | U08-Q01–Q14 | [08-spot-and-preemptible-instances-for-data-workloads.md](08-spot-and-preemptible-instances-for-data-workloads.md) |
| 9. Karpenter and Cluster Autoscaler node provisioning | U09-Q01–Q14 | [09-karpenter-and-cluster-autoscaler-node-provisioning.md](09-karpenter-and-cluster-autoscaler-node-provisioning.md) |
| 10. Event-driven autoscaling with KEDA | U10-Q01–Q14 | [10-event-driven-autoscaling-with-keda.md](10-event-driven-autoscaling-with-keda.md) |
| 11. Kubernetes cost visibility with OpenCost | U11-Q01–Q14 | [11-kubernetes-cost-visibility-with-opencost.md](11-kubernetes-cost-visibility-with-opencost.md) |
| 12. GPU scheduling, sharing, and ML workload economics | U12-Q01–Q14 | [12-gpu-scheduling-sharing-and-ml-workload-economics.md](12-gpu-scheduling-sharing-and-ml-workload-economics.md) |
| Cross-unit | X01–X42 | Integrated scenarios |

## Unit-specific questions


### Unit 1 — Platform capacity forecasting and headroom

**Source alignment:** [01-platform-capacity-forecasting-and-headroom.md](01-platform-capacity-forecasting-and-headroom.md).

#### U01-Q01 — Conceptual short-answer
- **Unit(s):** 1 | **Level:** L1 | **Objective:** assess demand, capacity and allocatable resources | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain demand, capacity and allocatable resources. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Demand, capacity and allocatable resources must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Platform capacity forecasting and headroom requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: demand, capacity and allocatable resources.

#### U01-Q02 — Conceptual short-answer
- **Unit(s):** 1 | **Level:** L1 | **Objective:** assess headroom, reserve and exhaustion | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain headroom, reserve and exhaustion. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Headroom, reserve and exhaustion must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Platform capacity forecasting and headroom requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: headroom, reserve and exhaustion.

#### U01-Q03 — Conceptual short-answer
- **Unit(s):** 1 | **Level:** L1 | **Objective:** assess percentiles and peak windows | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain percentiles and peak windows. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Percentiles and peak windows must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Platform capacity forecasting and headroom requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: percentiles and peak windows.

#### U01-Q04 — Multiple choice
- **Unit(s):** 1 | **Level:** L1 | **Objective:** assess workload demand profiles | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing workload demand profiles?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: workload demand profiles.

#### U01-Q05 — Multiple choice
- **Unit(s):** 1 | **Level:** L2 | **Objective:** assess N−1 failure allowance | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing N−1 failure allowance?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: N−1 failure allowance.

#### U01-Q06 — Multiple choice
- **Unit(s):** 1 | **Level:** L2 | **Objective:** assess naive forecast baseline | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing naive forecast baseline?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: naive forecast baseline.

#### U01-Q07 — Artifact/number interpretation
- **Unit(s):** 1 | **Level:** L2 | **Objective:** assess rolling-origin back-testing | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about rolling-origin back-testing: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: rolling-origin back-testing.

#### U01-Q08 — Artifact/number interpretation
- **Unit(s):** 1 | **Level:** L2 | **Objective:** assess prediction intervals and uncertainty | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about prediction intervals and uncertainty: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: prediction intervals and uncertainty.

#### U01-Q09 — Artifact/number interpretation
- **Unit(s):** 1 | **Level:** L2 | **Type:** Artifact/number interpretation | **Objective:** interpret evidence and choose a justified action | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Capacity alert: exhaustion forecast in 40 minutes; simulated scale-out lead time 55 minutes. [SYNTHETIC]
**Model answer:** Alert is 15 minutes too late under the stated lead-time assumption. Trigger earlier using uncertainty and action lead time; verify whether capacity can actually be provisioned.
**Worked interpretation:** State units and assumptions; show the arithmetic; distinguish what the artifact proves from what remains unknown; pair any action with an SLO/data-safety guardrail.
**Common wrong answers:** Extrapolating synthetic results to real provider spend; ignoring missing data; treating an estimate as a guarantee; taking irreversible action from one sample.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not a single dashboard number.
**Source alignment:** M15 Unit 1, applied examples and labs.
#### U01-Q10 — Configuration/model review
- **Unit(s):** 1 | **Level:** L3 | **Objective:** assess node shape and fragmentation | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for node shape and fragmentation; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: node shape and fragmentation.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U01-Q11 — Configuration/model review
- **Unit(s):** 1 | **Level:** L3 | **Objective:** assess exhaustion alerts and action lead time | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for exhaustion alerts and action lead time; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: exhaustion alerts and action lead time.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U01-Q12 — Configuration/model review
- **Unit(s):** 1 | **Level:** L3 | **Objective:** assess commitment-versus-flexibility regret | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for commitment-versus-flexibility regret; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: commitment-versus-flexibility regret.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U01-Q13 — Incident/diagnosis
- **Unit(s):** 1 | **Level:** L3 | **Objective:** assess right-sizing with load tests | **Time:** 20 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Incident: right-sizing with load tests causes an unexpected change in the shared platform. Explain safe diagnosis and recovery.
**Model answer:** **Impact:** identify affected tiers, SLOs, queue/backlog, data correctness and HCU exposure. **First safe action:** stop uncontrolled change and preserve evidence. **Hypotheses/evidence:** compare capacity, quota/contention, placement, autoscaler bounds, telemetry freshness, labels, billing lag and recent releases as applicable. **Mitigation:** smallest reversible action; protect critical tiers; pause unsafe automation. **Verification:** confirm SLO recovery, queue drain, bounded resource growth and telemetry correctness. **Prevention/communication:** add regression tests, owner, runbook, audit trail and blameless follow-up.
**Common wrong answers:** Common wrong response: immediately raising every limit or deleting a suspected idle resource without evidence.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: right-sizing with load tests.

#### U01-Q14 — Design with rubric
- **Unit(s):** 1 | **Level:** L4 | **Objective:** assess tier-specific headroom policy | **Time:** 30 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Design a governed policy for tier-specific headroom policy for inference, streaming, ETL, training and notebooks. Constraints: zero budget, synthetic data, no credentials, protect SLOs and data.
**Model answer:** **Sample answer:** define workload tiers and assumptions; model demand/resource/cost; select bounded controls; validate positive and negative cases; require owner approval, observability and rollback; state simulator limits. **10-point rubric:** workload model/assumptions 2; technical coherence 2; SLO/data safety 2; cost reasoning 1; observability/evidence 1; failure/rollback 1; ownership/governance 1.
**Common wrong answers:** Common weak answer: tool-first architecture without capacity math, owners, negative tests, evidence or rollback.
**Reliability/cost/safety implication:** Platform capacity forecasting and headroom must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 1, topic: tier-specific headroom policy.

### Unit 2 — Workload priorities, quotas, and resource contention

**Source alignment:** [02-workload-priorities-quotas-and-resource-contention.md](02-workload-priorities-quotas-and-resource-contention.md).

#### U02-Q01 — Conceptual short-answer
- **Unit(s):** 2 | **Level:** L1 | **Objective:** assess workload classes and priorities | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain workload classes and priorities. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Workload classes and priorities must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Workload priorities, quotas, and resource contention requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: workload classes and priorities.

#### U02-Q02 — Conceptual short-answer
- **Unit(s):** 2 | **Level:** L1 | **Objective:** assess PriorityClass and preemption | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain PriorityClass and preemption. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Priorityclass and preemption must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Workload priorities, quotas, and resource contention requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: PriorityClass and preemption.

#### U02-Q03 — Conceptual short-answer
- **Unit(s):** 2 | **Level:** L1 | **Objective:** assess requests versus limits | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain requests versus limits. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Requests versus limits must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Workload priorities, quotas, and resource contention requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: requests versus limits.

#### U02-Q04 — Multiple choice
- **Unit(s):** 2 | **Level:** L1 | **Objective:** assess ResourceQuota versus LimitRange | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing ResourceQuota versus LimitRange?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: ResourceQuota versus LimitRange.

#### U02-Q05 — Multiple choice
- **Unit(s):** 2 | **Level:** L2 | **Objective:** assess quota scopes and missing requests | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing quota scopes and missing requests?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: quota scopes and missing requests.

#### U02-Q06 — Multiple choice
- **Unit(s):** 2 | **Level:** L2 | **Objective:** assess quota-by-priority and admission | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing quota-by-priority and admission?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: quota-by-priority and admission.

#### U02-Q07 — Artifact/number interpretation
- **Unit(s):** 2 | **Level:** L2 | **Objective:** assess fair share and DRF concepts | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about fair share and DRF concepts: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: fair share and DRF concepts.

#### U02-Q08 — Artifact/number interpretation
- **Unit(s):** 2 | **Level:** L2 | **Objective:** assess quota hoarding and starvation | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about quota hoarding and starvation: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: quota hoarding and starvation.

#### U02-Q09 — Artifact/number interpretation
- **Unit(s):** 2 | **Level:** L2 | **Type:** Artifact/number interpretation | **Objective:** interpret evidence and choose a justified action | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Pending pod: quota has 10 CPU free; pod requests 8; every eligible node has at most 6 CPU free and required label is absent. [SYNTHETIC]
**Model answer:** Quota is not the blocker; per-node fit and selector are. Fix constraints or provide a matching node shape within approved ceilings.
**Worked interpretation:** State units and assumptions; show the arithmetic; distinguish what the artifact proves from what remains unknown; pair any action with an SLO/data-safety guardrail.
**Common wrong answers:** Extrapolating synthetic results to real provider spend; ignoring missing data; treating an estimate as a guarantee; taking irreversible action from one sample.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not a single dashboard number.
**Source alignment:** M15 Unit 2, applied examples and labs.
#### U02-Q10 — Configuration/model review
- **Unit(s):** 2 | **Level:** L3 | **Objective:** assess overprovisioning placeholders | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for overprovisioning placeholders; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: overprovisioning placeholders.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U02-Q11 — Configuration/model review
- **Unit(s):** 2 | **Level:** L3 | **Objective:** assess Pending-pod diagnosis | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for Pending-pod diagnosis; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: Pending-pod diagnosis.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U02-Q12 — Configuration/model review
- **Unit(s):** 2 | **Level:** L3 | **Objective:** assess GPU extended-resource quota | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for GPU extended-resource quota; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: GPU extended-resource quota.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U02-Q13 — Incident/diagnosis
- **Unit(s):** 2 | **Level:** L3 | **Objective:** assess online SLO protection during batch contention | **Time:** 20 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Incident: online SLO protection during batch contention causes an unexpected change in the shared platform. Explain safe diagnosis and recovery.
**Model answer:** **Impact:** identify affected tiers, SLOs, queue/backlog, data correctness and HCU exposure. **First safe action:** stop uncontrolled change and preserve evidence. **Hypotheses/evidence:** compare capacity, quota/contention, placement, autoscaler bounds, telemetry freshness, labels, billing lag and recent releases as applicable. **Mitigation:** smallest reversible action; protect critical tiers; pause unsafe automation. **Verification:** confirm SLO recovery, queue drain, bounded resource growth and telemetry correctness. **Prevention/communication:** add regression tests, owner, runbook, audit trail and blameless follow-up.
**Common wrong answers:** Common wrong response: immediately raising every limit or deleting a suspected idle resource without evidence.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: online SLO protection during batch contention.

#### U02-Q14 — Design with rubric
- **Unit(s):** 2 | **Level:** L4 | **Objective:** assess shared-cluster scheduling policy | **Time:** 30 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Design a governed policy for shared-cluster scheduling policy for inference, streaming, ETL, training and notebooks. Constraints: zero budget, synthetic data, no credentials, protect SLOs and data.
**Model answer:** **Sample answer:** define workload tiers and assumptions; model demand/resource/cost; select bounded controls; validate positive and negative cases; require owner approval, observability and rollback; state simulator limits. **10-point rubric:** workload model/assumptions 2; technical coherence 2; SLO/data safety 2; cost reasoning 1; observability/evidence 1; failure/rollback 1; ownership/governance 1.
**Common wrong answers:** Common weak answer: tool-first architecture without capacity math, owners, negative tests, evidence or rollback.
**Reliability/cost/safety implication:** Workload priorities, quotas, and resource contention must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 2, topic: shared-cluster scheduling policy.

### Unit 3 — Cloud budget alerts and spending guardrails

**Source alignment:** [03-cloud-budget-alerts-and-spending-guardrails.md](03-cloud-budget-alerts-and-spending-guardrails.md).

#### U03-Q01 — Conceptual short-answer
- **Unit(s):** 3 | **Level:** L1 | **Objective:** assess budget versus cap | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain budget versus cap. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Budget versus cap must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Cloud budget alerts and spending guardrails requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: budget versus cap.

#### U03-Q02 — Conceptual short-answer
- **Unit(s):** 3 | **Level:** L1 | **Objective:** assess actual-like and forecast spend | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain actual-like and forecast spend. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Actual-like and forecast spend must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Cloud budget alerts and spending guardrails requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: actual-like and forecast spend.

#### U03-Q03 — Conceptual short-answer
- **Unit(s):** 3 | **Level:** L1 | **Objective:** assess thresholds and alert latency | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain thresholds and alert latency. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Thresholds and alert latency must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Cloud budget alerts and spending guardrails requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: thresholds and alert latency.

#### U03-Q04 — Multiple choice
- **Unit(s):** 3 | **Level:** L1 | **Objective:** assess billing lag and usage proxies | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing billing lag and usage proxies?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: billing lag and usage proxies.

#### U03-Q05 — Multiple choice
- **Unit(s):** 3 | **Level:** L2 | **Objective:** assess budgets-as-code | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing budgets-as-code?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: budgets-as-code.

#### U03-Q06 — Multiple choice
- **Unit(s):** 3 | **Level:** L2 | **Objective:** assess forecast alerts and anomaly baselines | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing forecast alerts and anomaly baselines?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: forecast alerts and anomaly baselines.

#### U03-Q07 — Artifact/number interpretation
- **Unit(s):** 3 | **Level:** L2 | **Objective:** assess price-volume-mix variance | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about price-volume-mix variance: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: price-volume-mix variance.

#### U03-Q08 — Artifact/number interpretation
- **Unit(s):** 3 | **Level:** L2 | **Objective:** assess preventive quotas and ceilings | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about preventive quotas and ceilings: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: preventive quotas and ceilings.

#### U03-Q09 — Artifact/number interpretation
- **Unit(s):** 3 | **Level:** L2 | **Type:** Artifact/number interpretation | **Objective:** interpret evidence and choose a justified action | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Alert threshold is 80 HCU; notification arrives after observed spend reaches 105 HCU. Budget target is 100 HCU. [HYPOTHETICAL] [SYNTHETIC]
**Model answer:** Alert arrived 25 HCU after its threshold and 5 HCU beyond budget. An alert is not a cap; add preventive ceilings/quotas and test notification latency.
**Worked interpretation:** State units and assumptions; show the arithmetic; distinguish what the artifact proves from what remains unknown; pair any action with an SLO/data-safety guardrail.
**Common wrong answers:** Extrapolating synthetic results to real provider spend; ignoring missing data; treating an estimate as a guarantee; taking irreversible action from one sample.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not a single dashboard number.
**Source alignment:** M15 Unit 3, applied examples and labs.
#### U03-Q10 — Configuration/model review
- **Unit(s):** 3 | **Level:** L3 | **Objective:** assess dry-run and allow-list | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for dry-run and allow-list; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: dry-run and allow-list.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U03-Q11 — Configuration/model review
- **Unit(s):** 3 | **Level:** L3 | **Objective:** assess action caps and kill switch | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for action caps and kill switch; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: action caps and kill switch.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U03-Q12 — Configuration/model review
- **Unit(s):** 3 | **Level:** L3 | **Objective:** assess hidden cost drivers | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for hidden cost drivers; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: hidden cost drivers.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U03-Q13 — Incident/diagnosis
- **Unit(s):** 3 | **Level:** L3 | **Objective:** assess runaway scaling cost incident | **Time:** 20 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Incident: runaway scaling cost incident causes an unexpected change in the shared platform. Explain safe diagnosis and recovery.
**Model answer:** **Impact:** identify affected tiers, SLOs, queue/backlog, data correctness and HCU exposure. **First safe action:** stop uncontrolled change and preserve evidence. **Hypotheses/evidence:** compare capacity, quota/contention, placement, autoscaler bounds, telemetry freshness, labels, billing lag and recent releases as applicable. **Mitigation:** smallest reversible action; protect critical tiers; pause unsafe automation. **Verification:** confirm SLO recovery, queue drain, bounded resource growth and telemetry correctness. **Prevention/communication:** add regression tests, owner, runbook, audit trail and blameless follow-up.
**Common wrong answers:** Common wrong response: immediately raising every limit or deleting a suspected idle resource without evidence.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: runaway scaling cost incident.

#### U03-Q14 — Design with rubric
- **Unit(s):** 3 | **Level:** L4 | **Objective:** assess layered spending guardrails | **Time:** 30 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Design a governed policy for layered spending guardrails for inference, streaming, ETL, training and notebooks. Constraints: zero budget, synthetic data, no credentials, protect SLOs and data.
**Model answer:** **Sample answer:** define workload tiers and assumptions; model demand/resource/cost; select bounded controls; validate positive and negative cases; require owner approval, observability and rollback; state simulator limits. **10-point rubric:** workload model/assumptions 2; technical coherence 2; SLO/data safety 2; cost reasoning 1; observability/evidence 1; failure/rollback 1; ownership/governance 1.
**Common wrong answers:** Common weak answer: tool-first architecture without capacity math, owners, negative tests, evidence or rollback.
**Reliability/cost/safety implication:** Cloud budget alerts and spending guardrails must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 3, topic: layered spending guardrails.

### Unit 4 — Cost allocation by team, project, and workload

**Source alignment:** [04-cost-allocation-by-team-project-and-workload.md](04-cost-allocation-by-team-project-and-workload.md).

#### U04-Q01 — Conceptual short-answer
- **Unit(s):** 4 | **Level:** L1 | **Objective:** assess ownership registry and labels | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain ownership registry and labels. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Ownership registry and labels must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Cost allocation by team, project, and workload requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: ownership registry and labels.

#### U04-Q02 — Conceptual short-answer
- **Unit(s):** 4 | **Level:** L1 | **Objective:** assess metadata completeness | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain metadata completeness. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Metadata completeness must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Cost allocation by team, project, and workload requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: metadata completeness.

#### U04-Q03 — Conceptual short-answer
- **Unit(s):** 4 | **Level:** L1 | **Objective:** assess direct versus shared cost | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain direct versus shared cost. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Direct versus shared cost must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Cost allocation by team, project, and workload requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: direct versus shared cost.

#### U04-Q04 — Multiple choice
- **Unit(s):** 4 | **Level:** L1 | **Objective:** assess request-based allocation | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing request-based allocation?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: request-based allocation.

#### U04-Q05 — Multiple choice
- **Unit(s):** 4 | **Level:** L2 | **Objective:** assess usage-based allocation | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing usage-based allocation?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: usage-based allocation.

#### U04-Q06 — Multiple choice
- **Unit(s):** 4 | **Level:** L2 | **Objective:** assess max(request, usage) model | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing max(request, usage) model?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: max(request, usage) model.

#### U04-Q07 — Artifact/number interpretation
- **Unit(s):** 4 | **Level:** L2 | **Objective:** assess idle and unallocated buckets | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about idle and unallocated buckets: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: idle and unallocated buckets.

#### U04-Q08 — Artifact/number interpretation
- **Unit(s):** 4 | **Level:** L2 | **Objective:** assess shared platform and DR costs | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about shared platform and DR costs: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: shared platform and DR costs.

#### U04-Q09 — Artifact/number interpretation
- **Unit(s):** 4 | **Level:** L2 | **Type:** Artifact/number interpretation | **Objective:** interpret evidence and choose a justified action | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Shared pool 30 HCU is allocated by request share: Team A 50%, B 30%, C 20%. [HYPOTHETICAL]
**Model answer:** A=15, B=9, C=6 HCU; sum=30. State why request share is a fair driver and compare alternatives such as usage or fixed share.
**Worked interpretation:** State units and assumptions; show the arithmetic; distinguish what the artifact proves from what remains unknown; pair any action with an SLO/data-safety guardrail.
**Common wrong answers:** Extrapolating synthetic results to real provider spend; ignoring missing data; treating an estimate as a guarantee; taking irreversible action from one sample.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not a single dashboard number.
**Source alignment:** M15 Unit 4, applied examples and labs.
#### U04-Q10 — Configuration/model review
- **Unit(s):** 4 | **Level:** L3 | **Objective:** assess allocation sensitivity | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for allocation sensitivity; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: allocation sensitivity.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U04-Q11 — Configuration/model review
- **Unit(s):** 4 | **Level:** L3 | **Objective:** assess unit economics | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for unit economics; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: unit economics.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U04-Q12 — Configuration/model review
- **Unit(s):** 4 | **Level:** L3 | **Objective:** assess invoice reconciliation residual | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for invoice reconciliation residual; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: invoice reconciliation residual.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U04-Q13 — Incident/diagnosis
- **Unit(s):** 4 | **Level:** L3 | **Objective:** assess allocation accuracy versus completeness | **Time:** 20 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Incident: allocation accuracy versus completeness causes an unexpected change in the shared platform. Explain safe diagnosis and recovery.
**Model answer:** **Impact:** identify affected tiers, SLOs, queue/backlog, data correctness and HCU exposure. **First safe action:** stop uncontrolled change and preserve evidence. **Hypotheses/evidence:** compare capacity, quota/contention, placement, autoscaler bounds, telemetry freshness, labels, billing lag and recent releases as applicable. **Mitigation:** smallest reversible action; protect critical tiers; pause unsafe automation. **Verification:** confirm SLO recovery, queue drain, bounded resource growth and telemetry correctness. **Prevention/communication:** add regression tests, owner, runbook, audit trail and blameless follow-up.
**Common wrong answers:** Common wrong response: immediately raising every limit or deleting a suspected idle resource without evidence.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: allocation accuracy versus completeness.

#### U04-Q14 — Design with rubric
- **Unit(s):** 4 | **Level:** L4 | **Objective:** assess governed allocation and disputes | **Time:** 30 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Design a governed policy for governed allocation and disputes for inference, streaming, ETL, training and notebooks. Constraints: zero budget, synthetic data, no credentials, protect SLOs and data.
**Model answer:** **Sample answer:** define workload tiers and assumptions; model demand/resource/cost; select bounded controls; validate positive and negative cases; require owner approval, observability and rollback; state simulator limits. **10-point rubric:** workload model/assumptions 2; technical coherence 2; SLO/data safety 2; cost reasoning 1; observability/evidence 1; failure/rollback 1; ownership/governance 1.
**Common wrong answers:** Common weak answer: tool-first architecture without capacity math, owners, negative tests, evidence or rollback.
**Reliability/cost/safety implication:** Cost allocation by team, project, and workload must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 4, topic: governed allocation and disputes.

### Unit 5 — Idle resource detection and automated cleanup

**Source alignment:** [05-idle-resource-detection-and-automated-cleanup.md](05-idle-resource-detection-and-automated-cleanup.md).

#### U05-Q01 — Conceptual short-answer
- **Unit(s):** 5 | **Level:** L1 | **Objective:** assess idle versus underutilized | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain idle versus underutilized. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Idle versus underutilized must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Idle resource detection and automated cleanup requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: idle versus underutilized.

#### U05-Q02 — Conceptual short-answer
- **Unit(s):** 5 | **Level:** L1 | **Objective:** assess orphaned versus zombie resources | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain orphaned versus zombie resources. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Orphaned versus zombie resources must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Idle resource detection and automated cleanup requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: orphaned versus zombie resources.

#### U05-Q03 — Conceptual short-answer
- **Unit(s):** 5 | **Level:** L1 | **Objective:** assess missing telemetry versus zero usage | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain missing telemetry versus zero usage. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Missing telemetry versus zero usage must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Idle resource detection and automated cleanup requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: missing telemetry versus zero usage.

#### U05-Q04 — Multiple choice
- **Unit(s):** 5 | **Level:** L1 | **Objective:** assess evidence windows and confidence | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing evidence windows and confidence?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: evidence windows and confidence.

#### U05-Q05 — Multiple choice
- **Unit(s):** 5 | **Level:** L2 | **Objective:** assess false-positive exclusions | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing false-positive exclusions?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: false-positive exclusions.

#### U05-Q06 — Multiple choice
- **Unit(s):** 5 | **Level:** L2 | **Objective:** assess quarterly jobs and DR standby | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing quarterly jobs and DR standby?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: quarterly jobs and DR standby.

#### U05-Q07 — Artifact/number interpretation
- **Unit(s):** 5 | **Level:** L2 | **Objective:** assess legal holds and data protection | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about legal holds and data protection: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: legal holds and data protection.

#### U05-Q08 — Artifact/number interpretation
- **Unit(s):** 5 | **Level:** L2 | **Objective:** assess report-only to quarantine to stop | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about report-only to quarantine to stop: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: report-only to quarantine to stop.

#### U05-Q09 — Artifact/number interpretation
- **Unit(s):** 5 | **Level:** L2 | **Type:** Artifact/number interpretation | **Objective:** interpret evidence and choose a justified action | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Candidate has no usage samples because exporter is down; cleanup policy reports utilization as zero. [SYNTHETIC]
**Model answer:** This is missing telemetry, not zero use. Suppress action eligibility, restore telemetry and require a fresh evidence window.
**Worked interpretation:** State units and assumptions; show the arithmetic; distinguish what the artifact proves from what remains unknown; pair any action with an SLO/data-safety guardrail.
**Common wrong answers:** Extrapolating synthetic results to real provider spend; ignoring missing data; treating an estimate as a guarantee; taking irreversible action from one sample.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not a single dashboard number.
**Source alignment:** M15 Unit 5, applied examples and labs.
#### U05-Q10 — Configuration/model review
- **Unit(s):** 5 | **Level:** L3 | **Objective:** assess allow-list and action caps | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for allow-list and action caps; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: allow-list and action caps.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U05-Q11 — Configuration/model review
- **Unit(s):** 5 | **Level:** L3 | **Objective:** assess timezone/DST-safe scheduling | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for timezone/DST-safe scheduling; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: timezone/DST-safe scheduling.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U05-Q12 — Configuration/model review
- **Unit(s):** 5 | **Level:** L3 | **Objective:** assess right-sizing and HPA interaction | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for right-sizing and HPA interaction; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: right-sizing and HPA interaction.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U05-Q13 — Incident/diagnosis
- **Unit(s):** 5 | **Level:** L3 | **Objective:** assess least-privilege cleanup identity | **Time:** 20 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Incident: least-privilege cleanup identity causes an unexpected change in the shared platform. Explain safe diagnosis and recovery.
**Model answer:** **Impact:** identify affected tiers, SLOs, queue/backlog, data correctness and HCU exposure. **First safe action:** stop uncontrolled change and preserve evidence. **Hypotheses/evidence:** compare capacity, quota/contention, placement, autoscaler bounds, telemetry freshness, labels, billing lag and recent releases as applicable. **Mitigation:** smallest reversible action; protect critical tiers; pause unsafe automation. **Verification:** confirm SLO recovery, queue drain, bounded resource growth and telemetry correctness. **Prevention/communication:** add regression tests, owner, runbook, audit trail and blameless follow-up.
**Common wrong answers:** Common wrong response: immediately raising every limit or deleting a suspected idle resource without evidence.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: least-privilege cleanup identity.

#### U05-Q14 — Design with rubric
- **Unit(s):** 5 | **Level:** L4 | **Objective:** assess savings identified versus realized | **Time:** 30 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Design a governed policy for savings identified versus realized for inference, streaming, ETL, training and notebooks. Constraints: zero budget, synthetic data, no credentials, protect SLOs and data.
**Model answer:** **Sample answer:** define workload tiers and assumptions; model demand/resource/cost; select bounded controls; validate positive and negative cases; require owner approval, observability and rollback; state simulator limits. **10-point rubric:** workload model/assumptions 2; technical coherence 2; SLO/data safety 2; cost reasoning 1; observability/evidence 1; failure/rollback 1; ownership/governance 1.
**Common wrong answers:** Common weak answer: tool-first architecture without capacity math, owners, negative tests, evidence or rollback.
**Reliability/cost/safety implication:** Idle resource detection and automated cleanup must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 5, topic: savings identified versus realized.

### Unit 6 — Cost, reliability, and performance trade-offs

**Source alignment:** [06-cost-reliability-and-performance-tradeoffs.md](06-cost-reliability-and-performance-tradeoffs.md).

#### U06-Q01 — Conceptual short-answer
- **Unit(s):** 6 | **Level:** L1 | **Objective:** assess cost/reliability/performance trade-offs | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain cost/reliability/performance trade-offs. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Cost/reliability/performance trade-offs must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Cost, reliability, and performance trade-offs requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: cost/reliability/performance trade-offs.

#### U06-Q02 — Conceptual short-answer
- **Unit(s):** 6 | **Level:** L1 | **Objective:** assess workload-tier SLOs | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain workload-tier SLOs. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Workload-tier slos must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Cost, reliability, and performance trade-offs requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: workload-tier SLOs.

#### U06-Q03 — Conceptual short-answer
- **Unit(s):** 6 | **Level:** L1 | **Objective:** assess headroom as reliability spend | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain headroom as reliability spend. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Headroom as reliability spend must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Cost, reliability, and performance trade-offs requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: headroom as reliability spend.

#### U06-Q04 — Multiple choice
- **Unit(s):** 6 | **Level:** L1 | **Objective:** assess availability arithmetic | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing availability arithmetic?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: availability arithmetic.

#### U06-Q05 — Multiple choice
- **Unit(s):** 6 | **Level:** L2 | **Objective:** assess latency and throughput | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing latency and throughput?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: latency and throughput.

#### U06-Q06 — Multiple choice
- **Unit(s):** 6 | **Level:** L2 | **Objective:** assess queue wait and backlog recovery | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing queue wait and backlog recovery?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: queue wait and backlog recovery.

#### U06-Q07 — Artifact/number interpretation
- **Unit(s):** 6 | **Level:** L2 | **Objective:** assess observability and time-to-localize | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about observability and time-to-localize: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: observability and time-to-localize.

#### U06-Q08 — Artifact/number interpretation
- **Unit(s):** 6 | **Level:** L2 | **Objective:** assess backup, restore and DR | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about backup, restore and DR: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: backup, restore and DR.

#### U06-Q09 — Artifact/number interpretation
- **Unit(s):** 6 | **Level:** L2 | **Type:** Artifact/number interpretation | **Objective:** interpret evidence and choose a justified action | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Telemetry cut saves 8 HCU but increases time-to-localize from 10 to 35 minutes. [HYPOTHETICAL] [SYNTHETIC]
**Model answer:** Localization time increases 25 minutes (3.5× baseline). Compare incident impact with savings; restore useful signals or redesign telemetry.
**Worked interpretation:** State units and assumptions; show the arithmetic; distinguish what the artifact proves from what remains unknown; pair any action with an SLO/data-safety guardrail.
**Common wrong answers:** Extrapolating synthetic results to real provider spend; ignoring missing data; treating an estimate as a guarantee; taking irreversible action from one sample.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not a single dashboard number.
**Source alignment:** M15 Unit 6, applied examples and labs.
#### U06-Q10 — Configuration/model review
- **Unit(s):** 6 | **Level:** L3 | **Objective:** assess security and isolation | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for security and isolation; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: security and isolation.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U06-Q11 — Configuration/model review
- **Unit(s):** 6 | **Level:** L3 | **Objective:** assess developer velocity | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for developer velocity; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: developer velocity.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U06-Q12 — Configuration/model review
- **Unit(s):** 6 | **Level:** L3 | **Objective:** assess unit cost versus total spend | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for unit cost versus total spend; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: unit cost versus total spend.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U06-Q13 — Incident/diagnosis
- **Unit(s):** 6 | **Level:** L3 | **Objective:** assess Goodhart's law and utilization targets | **Time:** 20 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Incident: Goodhart's law and utilization targets causes an unexpected change in the shared platform. Explain safe diagnosis and recovery.
**Model answer:** **Impact:** identify affected tiers, SLOs, queue/backlog, data correctness and HCU exposure. **First safe action:** stop uncontrolled change and preserve evidence. **Hypotheses/evidence:** compare capacity, quota/contention, placement, autoscaler bounds, telemetry freshness, labels, billing lag and recent releases as applicable. **Mitigation:** smallest reversible action; protect critical tiers; pause unsafe automation. **Verification:** confirm SLO recovery, queue drain, bounded resource growth and telemetry correctness. **Prevention/communication:** add regression tests, owner, runbook, audit trail and blameless follow-up.
**Common wrong answers:** Common wrong response: immediately raising every limit or deleting a suspected idle resource without evidence.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: Goodhart's law and utilization targets.

#### U06-Q14 — Design with rubric
- **Unit(s):** 6 | **Level:** L4 | **Objective:** assess tiered cost policy and ADR | **Time:** 30 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Design a governed policy for tiered cost policy and ADR for inference, streaming, ETL, training and notebooks. Constraints: zero budget, synthetic data, no credentials, protect SLOs and data.
**Model answer:** **Sample answer:** define workload tiers and assumptions; model demand/resource/cost; select bounded controls; validate positive and negative cases; require owner approval, observability and rollback; state simulator limits. **10-point rubric:** workload model/assumptions 2; technical coherence 2; SLO/data safety 2; cost reasoning 1; observability/evidence 1; failure/rollback 1; ownership/governance 1.
**Common wrong answers:** Common weak answer: tool-first architecture without capacity math, owners, negative tests, evidence or rollback.
**Reliability/cost/safety implication:** Cost, reliability, and performance trade-offs must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 6, topic: tiered cost policy and ADR.

### Unit 7 — Capacity and cost review for production releases

**Source alignment:** [07-capacity-and-cost-review-for-production-releases.md](07-capacity-and-cost-review-for-production-releases.md).

#### U07-Q01 — Conceptual short-answer
- **Unit(s):** 7 | **Level:** L1 | **Objective:** assess release resource deltas | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain release resource deltas. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Release resource deltas must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Capacity and cost review for production releases requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: release resource deltas.

#### U07-Q02 — Conceptual short-answer
- **Unit(s):** 7 | **Level:** L1 | **Objective:** assess rendered manifest diff | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain rendered manifest diff. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Rendered manifest diff must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Capacity and cost review for production releases requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: rendered manifest diff.

#### U07-Q03 — Conceptual short-answer
- **Unit(s):** 7 | **Level:** L1 | **Objective:** assess replicas, requests and limits | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain replicas, requests and limits. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Replicas, requests and limits must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Capacity and cost review for production releases requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: replicas, requests and limits.

#### U07-Q04 — Multiple choice
- **Unit(s):** 7 | **Level:** L1 | **Objective:** assess HPA/KEDA maximum and quota | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing HPA/KEDA maximum and quota?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: HPA/KEDA maximum and quota.

#### U07-Q05 — Multiple choice
- **Unit(s):** 7 | **Level:** L2 | **Objective:** assess rollout surge and overlap | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing rollout surge and overlap?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: rollout surge and overlap.

#### U07-Q06 — Multiple choice
- **Unit(s):** 7 | **Level:** L2 | **Objective:** assess IaC plan estimate | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing IaC plan estimate?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: IaC plan estimate.

#### U07-Q07 — Artifact/number interpretation
- **Unit(s):** 7 | **Level:** L2 | **Objective:** assess load-test-based efficiency | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about load-test-based efficiency: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: load-test-based efficiency.

#### U07-Q08 — Artifact/number interpretation
- **Unit(s):** 7 | **Level:** L2 | **Objective:** assess launch capacity plan | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about launch capacity plan: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: launch capacity plan.

#### U07-Q09 — Artifact/number interpretation
- **Unit(s):** 7 | **Level:** L2 | **Type:** Artifact/number interpretation | **Objective:** interpret evidence and choose a justified action | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Estimator predicts 12 CPU; post-release measured peak is 17 CPU. [SYNTHETIC]
**Model answer:** Underestimate=5 CPU; relative to measured peak, 5/17≈29.4%. Investigate missing surge, telemetry or workload assumptions and recalibrate.
**Worked interpretation:** State units and assumptions; show the arithmetic; distinguish what the artifact proves from what remains unknown; pair any action with an SLO/data-safety guardrail.
**Common wrong answers:** Extrapolating synthetic results to real provider spend; ignoring missing data; treating an estimate as a guarantee; taking irreversible action from one sample.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not a single dashboard number.
**Source alignment:** M15 Unit 7, applied examples and labs.
#### U07-Q10 — Configuration/model review
- **Unit(s):** 7 | **Level:** L3 | **Objective:** assess noise-aware regression gate | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for noise-aware regression gate; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: noise-aware regression gate.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U07-Q11 — Configuration/model review
- **Unit(s):** 7 | **Level:** L3 | **Objective:** assess A/A testing | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for A/A testing; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: A/A testing.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U07-Q12 — Configuration/model review
- **Unit(s):** 7 | **Level:** L3 | **Objective:** assess ring promotion and canary | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for ring promotion and canary; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: ring promotion and canary.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U07-Q13 — Incident/diagnosis
- **Unit(s):** 7 | **Level:** L3 | **Objective:** assess accidental replica doubling | **Time:** 20 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Incident: accidental replica doubling causes an unexpected change in the shared platform. Explain safe diagnosis and recovery.
**Model answer:** **Impact:** identify affected tiers, SLOs, queue/backlog, data correctness and HCU exposure. **First safe action:** stop uncontrolled change and preserve evidence. **Hypotheses/evidence:** compare capacity, quota/contention, placement, autoscaler bounds, telemetry freshness, labels, billing lag and recent releases as applicable. **Mitigation:** smallest reversible action; protect critical tiers; pause unsafe automation. **Verification:** confirm SLO recovery, queue drain, bounded resource growth and telemetry correctness. **Prevention/communication:** add regression tests, owner, runbook, audit trail and blameless follow-up.
**Common wrong answers:** Common wrong response: immediately raising every limit or deleting a suspected idle resource without evidence.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: accidental replica doubling.

#### U07-Q14 — Design with rubric
- **Unit(s):** 7 | **Level:** L4 | **Objective:** assess release approval and rollback | **Time:** 30 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Design a governed policy for release approval and rollback for inference, streaming, ETL, training and notebooks. Constraints: zero budget, synthetic data, no credentials, protect SLOs and data.
**Model answer:** **Sample answer:** define workload tiers and assumptions; model demand/resource/cost; select bounded controls; validate positive and negative cases; require owner approval, observability and rollback; state simulator limits. **10-point rubric:** workload model/assumptions 2; technical coherence 2; SLO/data safety 2; cost reasoning 1; observability/evidence 1; failure/rollback 1; ownership/governance 1.
**Common wrong answers:** Common weak answer: tool-first architecture without capacity math, owners, negative tests, evidence or rollback.
**Reliability/cost/safety implication:** Capacity and cost review for production releases must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 7, topic: release approval and rollback.

### Unit 8 — Spot and preemptible instances for data workloads

**Source alignment:** [08-spot-and-preemptible-instances-for-data-workloads.md](08-spot-and-preemptible-instances-for-data-workloads.md).

#### U08-Q01 — Conceptual short-answer
- **Unit(s):** 8 | **Level:** L1 | **Objective:** assess spot/preemptible capacity | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain spot/preemptible capacity. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Spot/preemptible capacity must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Spot and preemptible instances for data workloads requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: spot/preemptible capacity.

#### U08-Q02 — Conceptual short-answer
- **Unit(s):** 8 | **Level:** L1 | **Objective:** assess workload eligibility | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain workload eligibility. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Workload eligibility must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Spot and preemptible instances for data workloads requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: workload eligibility.

#### U08-Q03 — Conceptual short-answer
- **Unit(s):** 8 | **Level:** L1 | **Objective:** assess graceful termination | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain graceful termination. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Graceful termination must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Spot and preemptible instances for data workloads requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: graceful termination.

#### U08-Q04 — Multiple choice
- **Unit(s):** 8 | **Level:** L1 | **Objective:** assess checkpoint lifecycle | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing checkpoint lifecycle?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: checkpoint lifecycle.

#### U08-Q05 — Multiple choice
- **Unit(s):** 8 | **Level:** L2 | **Objective:** assess idempotency and restart | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing idempotency and restart?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: idempotency and restart.

#### U08-Q06 — Multiple choice
- **Unit(s):** 8 | **Level:** L2 | **Objective:** assess checkpoint interval economics | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing checkpoint interval economics?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: checkpoint interval economics.

#### U08-Q07 — Artifact/number interpretation
- **Unit(s):** 8 | **Level:** L2 | **Objective:** assess deadline-aware fallback | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about deadline-aware fallback: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: deadline-aware fallback.

#### U08-Q08 — Artifact/number interpretation
- **Unit(s):** 8 | **Level:** L2 | **Objective:** assess correlated interruptions | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about correlated interruptions: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: correlated interruptions.

#### U08-Q09 — Artifact/number interpretation
- **Unit(s):** 8 | **Level:** L2 | **Type:** Artifact/number interpretation | **Objective:** interpret evidence and choose a justified action | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Spot pool interruption wave causes 4 retries at 3 HCU each. [HYPOTHETICAL] [SYNTHETIC]
**Model answer:** Retry overhead=4×3=12 HCU. Add this to productive/checkpoint/lost-work cost; bound retries and protect deadlines.
**Worked interpretation:** State units and assumptions; show the arithmetic; distinguish what the artifact proves from what remains unknown; pair any action with an SLO/data-safety guardrail.
**Common wrong answers:** Extrapolating synthetic results to real provider spend; ignoring missing data; treating an estimate as a guarantee; taking irreversible action from one sample.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not a single dashboard number.
**Source alignment:** M15 Unit 8, applied examples and labs.
#### U08-Q10 — Configuration/model review
- **Unit(s):** 8 | **Level:** L3 | **Objective:** assess eligibility and SLO policy | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for eligibility and SLO policy; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: eligibility and SLO policy.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U08-Q11 — Configuration/model review
- **Unit(s):** 8 | **Level:** L3 | **Objective:** assess retry budgets and thundering herd | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for retry budgets and thundering herd; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: retry budgets and thundering herd.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U08-Q12 — Configuration/model review
- **Unit(s):** 8 | **Level:** L3 | **Objective:** assess effective cost including lost work | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for effective cost including lost work; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: effective cost including lost work.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U08-Q13 — Incident/diagnosis
- **Unit(s):** 8 | **Level:** L3 | **Objective:** assess interrupted training incident | **Time:** 20 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Incident: interrupted training incident causes an unexpected change in the shared platform. Explain safe diagnosis and recovery.
**Model answer:** **Impact:** identify affected tiers, SLOs, queue/backlog, data correctness and HCU exposure. **First safe action:** stop uncontrolled change and preserve evidence. **Hypotheses/evidence:** compare capacity, quota/contention, placement, autoscaler bounds, telemetry freshness, labels, billing lag and recent releases as applicable. **Mitigation:** smallest reversible action; protect critical tiers; pause unsafe automation. **Verification:** confirm SLO recovery, queue drain, bounded resource growth and telemetry correctness. **Prevention/communication:** add regression tests, owner, runbook, audit trail and blameless follow-up.
**Common wrong answers:** Common wrong response: immediately raising every limit or deleting a suspected idle resource without evidence.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: interrupted training incident.

#### U08-Q14 — Design with rubric
- **Unit(s):** 8 | **Level:** L4 | **Objective:** assess mixed spot/on-demand design | **Time:** 30 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Design a governed policy for mixed spot/on-demand design for inference, streaming, ETL, training and notebooks. Constraints: zero budget, synthetic data, no credentials, protect SLOs and data.
**Model answer:** **Sample answer:** define workload tiers and assumptions; model demand/resource/cost; select bounded controls; validate positive and negative cases; require owner approval, observability and rollback; state simulator limits. **10-point rubric:** workload model/assumptions 2; technical coherence 2; SLO/data safety 2; cost reasoning 1; observability/evidence 1; failure/rollback 1; ownership/governance 1.
**Common wrong answers:** Common weak answer: tool-first architecture without capacity math, owners, negative tests, evidence or rollback.
**Reliability/cost/safety implication:** Spot and preemptible instances for data workloads must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 8, topic: mixed spot/on-demand design.

### Unit 9 — Karpenter and Cluster Autoscaler node provisioning

**Source alignment:** [09-karpenter-and-cluster-autoscaler-node-provisioning.md](09-karpenter-and-cluster-autoscaler-node-provisioning.md).

#### U09-Q01 — Conceptual short-answer
- **Unit(s):** 9 | **Level:** L1 | **Objective:** assess pod autoscaling versus node provisioning | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain pod autoscaling versus node provisioning. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Pod autoscaling versus node provisioning must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Karpenter and Cluster Autoscaler node provisioning requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: pod autoscaling versus node provisioning.

#### U09-Q02 — Conceptual short-answer
- **Unit(s):** 9 | **Level:** L1 | **Objective:** assess Pending-pod diagnosis | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain Pending-pod diagnosis. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Pending-pod diagnosis must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Karpenter and Cluster Autoscaler node provisioning requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: Pending-pod diagnosis.

#### U09-Q03 — Conceptual short-answer
- **Unit(s):** 9 | **Level:** L1 | **Objective:** assess Cluster Autoscaler node-group model | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain Cluster Autoscaler node-group model. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Cluster autoscaler node-group model must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Karpenter and Cluster Autoscaler node provisioning requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: Cluster Autoscaler node-group model.

#### U09-Q04 — Multiple choice
- **Unit(s):** 9 | **Level:** L1 | **Objective:** assess Karpenter flexible provisioning model | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing Karpenter flexible provisioning model?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: Karpenter flexible provisioning model.

#### U09-Q05 — Multiple choice
- **Unit(s):** 9 | **Level:** L2 | **Objective:** assess bin packing and fragmentation | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing bin packing and fragmentation?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: bin packing and fragmentation.

#### U09-Q06 — Multiple choice
- **Unit(s):** 9 | **Level:** L2 | **Objective:** assess node shape | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing node shape?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: node shape.

#### U09-Q07 — Artifact/number interpretation
- **Unit(s):** 9 | **Level:** L2 | **Objective:** assess selectors, taints and affinity | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about selectors, taints and affinity: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: selectors, taints and affinity.

#### U09-Q08 — Artifact/number interpretation
- **Unit(s):** 9 | **Level:** L2 | **Objective:** assess impossible constraints | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about impossible constraints: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: impossible constraints.

#### U09-Q09 — Artifact/number interpretation
- **Unit(s):** 9 | **Level:** L2 | **Type:** Artifact/number interpretation | **Objective:** interpret evidence and choose a justified action | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** A node has 8 CPU free in aggregate but workload requests 6 CPU and requires a GPU/taint-compatible pool. [SYNTHETIC]
**Model answer:** CPU alone is insufficient evidence. Check all requested resources and placement constraints; node shape/fragmentation may prevent fit.
**Worked interpretation:** State units and assumptions; show the arithmetic; distinguish what the artifact proves from what remains unknown; pair any action with an SLO/data-safety guardrail.
**Common wrong answers:** Extrapolating synthetic results to real provider spend; ignoring missing data; treating an estimate as a guarantee; taking irreversible action from one sample.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not a single dashboard number.
**Source alignment:** M15 Unit 9, applied examples and labs.
#### U09-Q10 — Configuration/model review
- **Unit(s):** 9 | **Level:** L3 | **Objective:** assess capacity ceilings | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for capacity ceilings; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: capacity ceilings.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U09-Q11 — Configuration/model review
- **Unit(s):** 9 | **Level:** L3 | **Objective:** assess consolidation and disruption | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for consolidation and disruption; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: consolidation and disruption.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U09-Q12 — Configuration/model review
- **Unit(s):** 9 | **Level:** L3 | **Objective:** assess overprovisioning placeholders | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for overprovisioning placeholders; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: overprovisioning placeholders.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U09-Q13 — Incident/diagnosis
- **Unit(s):** 9 | **Level:** L3 | **Objective:** assess runaway provisioning incident | **Time:** 20 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Incident: runaway provisioning incident causes an unexpected change in the shared platform. Explain safe diagnosis and recovery.
**Model answer:** **Impact:** identify affected tiers, SLOs, queue/backlog, data correctness and HCU exposure. **First safe action:** stop uncontrolled change and preserve evidence. **Hypotheses/evidence:** compare capacity, quota/contention, placement, autoscaler bounds, telemetry freshness, labels, billing lag and recent releases as applicable. **Mitigation:** smallest reversible action; protect critical tiers; pause unsafe automation. **Verification:** confirm SLO recovery, queue drain, bounded resource growth and telemetry correctness. **Prevention/communication:** add regression tests, owner, runbook, audit trail and blameless follow-up.
**Common wrong answers:** Common wrong response: immediately raising every limit or deleting a suspected idle resource without evidence.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: runaway provisioning incident.

#### U09-Q14 — Design with rubric
- **Unit(s):** 9 | **Level:** L4 | **Objective:** assess simulated node-provisioning design | **Time:** 30 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Design a governed policy for simulated node-provisioning design for inference, streaming, ETL, training and notebooks. Constraints: zero budget, synthetic data, no credentials, protect SLOs and data.
**Model answer:** **Sample answer:** define workload tiers and assumptions; model demand/resource/cost; select bounded controls; validate positive and negative cases; require owner approval, observability and rollback; state simulator limits. **10-point rubric:** workload model/assumptions 2; technical coherence 2; SLO/data safety 2; cost reasoning 1; observability/evidence 1; failure/rollback 1; ownership/governance 1.
**Common wrong answers:** Common weak answer: tool-first architecture without capacity math, owners, negative tests, evidence or rollback.
**Reliability/cost/safety implication:** Karpenter and Cluster Autoscaler node provisioning must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 9, topic: simulated node-provisioning design.

### Unit 10 — Event-driven autoscaling with KEDA

**Source alignment:** [10-event-driven-autoscaling-with-keda.md](10-event-driven-autoscaling-with-keda.md).

#### U10-Q01 — Conceptual short-answer
- **Unit(s):** 10 | **Level:** L1 | **Objective:** assess event-driven versus CPU scaling | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain event-driven versus CPU scaling. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Event-driven versus cpu scaling must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Event-driven autoscaling with KEDA requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: event-driven versus CPU scaling.

#### U10-Q02 — Conceptual short-answer
- **Unit(s):** 10 | **Level:** L1 | **Objective:** assess KEDA control flow and HPA | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain KEDA control flow and HPA. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Keda control flow and hpa must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Event-driven autoscaling with KEDA requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: KEDA control flow and HPA.

#### U10-Q03 — Conceptual short-answer
- **Unit(s):** 10 | **Level:** L1 | **Objective:** assess queue target derivation | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain queue target derivation. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Queue target derivation must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Event-driven autoscaling with KEDA requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: queue target derivation.

#### U10-Q04 — Multiple choice
- **Unit(s):** 10 | **Level:** L1 | **Objective:** assess ScaledObject versus ScaledJob | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing ScaledObject versus ScaledJob?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: ScaledObject versus ScaledJob.

#### U10-Q05 — Multiple choice
- **Unit(s):** 10 | **Level:** L2 | **Objective:** assess Redis queue scaling | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing Redis queue scaling?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: Redis queue scaling.

#### U10-Q06 — Multiple choice
- **Unit(s):** 10 | **Level:** L2 | **Objective:** assess cron baseline plus bursts | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing cron baseline plus bursts?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: cron baseline plus bursts.

#### U10-Q07 — Artifact/number interpretation
- **Unit(s):** 10 | **Level:** L2 | **Objective:** assess Prometheus scaler signal | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about Prometheus scaler signal: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: Prometheus scaler signal.

#### U10-Q08 — Artifact/number interpretation
- **Unit(s):** 10 | **Level:** L2 | **Objective:** assess downstream-capacity maximum | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about downstream-capacity maximum: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: downstream-capacity maximum.

#### U10-Q09 — Artifact/number interpretation
- **Unit(s):** 10 | **Level:** L2 | **Type:** Artifact/number interpretation | **Objective:** interpret evidence and choose a justified action | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Each worker handles 20 messages/minute; backlog 600; freshness deadline 10 minutes. [SYNTHETIC]
**Model answer:** Required rate=600/10=60 messages/minute; replicas=ceil(60/20)=3, assuming linear throughput and no downstream bottleneck.
**Worked interpretation:** State units and assumptions; show the arithmetic; distinguish what the artifact proves from what remains unknown; pair any action with an SLO/data-safety guardrail.
**Common wrong answers:** Extrapolating synthetic results to real provider spend; ignoring missing data; treating an estimate as a guarantee; taking irreversible action from one sample.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not a single dashboard number.
**Source alignment:** M15 Unit 10, applied examples and labs.
#### U10-Q10 — Configuration/model review
- **Unit(s):** 10 | **Level:** L3 | **Objective:** assess empty/stale/error metrics | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for empty/stale/error metrics; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: empty/stale/error metrics.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U10-Q11 — Configuration/model review
- **Unit(s):** 10 | **Level:** L3 | **Objective:** assess multi-trigger flapping | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for multi-trigger flapping; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: multi-trigger flapping.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U10-Q12 — Configuration/model review
- **Unit(s):** 10 | **Level:** L3 | **Objective:** assess tenant guardrails | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for tenant guardrails; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: tenant guardrails.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U10-Q13 — Incident/diagnosis
- **Unit(s):** 10 | **Level:** L3 | **Objective:** assess runaway scaling incident | **Time:** 20 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Incident: runaway scaling incident causes an unexpected change in the shared platform. Explain safe diagnosis and recovery.
**Model answer:** **Impact:** identify affected tiers, SLOs, queue/backlog, data correctness and HCU exposure. **First safe action:** stop uncontrolled change and preserve evidence. **Hypotheses/evidence:** compare capacity, quota/contention, placement, autoscaler bounds, telemetry freshness, labels, billing lag and recent releases as applicable. **Mitigation:** smallest reversible action; protect critical tiers; pause unsafe automation. **Verification:** confirm SLO recovery, queue drain, bounded resource growth and telemetry correctness. **Prevention/communication:** add regression tests, owner, runbook, audit trail and blameless follow-up.
**Common wrong answers:** Common wrong response: immediately raising every limit or deleting a suspected idle resource without evidence.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: runaway scaling incident.

#### U10-Q14 — Design with rubric
- **Unit(s):** 10 | **Level:** L4 | **Objective:** assess KEDA fail-safe platform policy | **Time:** 30 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Design a governed policy for KEDA fail-safe platform policy for inference, streaming, ETL, training and notebooks. Constraints: zero budget, synthetic data, no credentials, protect SLOs and data.
**Model answer:** **Sample answer:** define workload tiers and assumptions; model demand/resource/cost; select bounded controls; validate positive and negative cases; require owner approval, observability and rollback; state simulator limits. **10-point rubric:** workload model/assumptions 2; technical coherence 2; SLO/data safety 2; cost reasoning 1; observability/evidence 1; failure/rollback 1; ownership/governance 1.
**Common wrong answers:** Common weak answer: tool-first architecture without capacity math, owners, negative tests, evidence or rollback.
**Reliability/cost/safety implication:** Event-driven autoscaling with KEDA must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 10, topic: KEDA fail-safe platform policy.

### Unit 11 — Kubernetes cost visibility with OpenCost

**Source alignment:** [11-kubernetes-cost-visibility-with-opencost.md](11-kubernetes-cost-visibility-with-opencost.md).

#### U11-Q01 — Conceptual short-answer
- **Unit(s):** 11 | **Level:** L1 | **Objective:** assess OpenCost allocation pipeline | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain OpenCost allocation pipeline. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Opencost allocation pipeline must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Kubernetes cost visibility with OpenCost requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: OpenCost allocation pipeline.

#### U11-Q02 — Conceptual short-answer
- **Unit(s):** 11 | **Level:** L1 | **Objective:** assess HCU pricing inputs | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain HCU pricing inputs. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Hcu pricing inputs must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Kubernetes cost visibility with OpenCost requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: HCU pricing inputs.

#### U11-Q03 — Conceptual short-answer
- **Unit(s):** 11 | **Level:** L1 | **Objective:** assess namespace/controller/pod allocation | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain namespace/controller/pod allocation. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Namespace/controller/pod allocation must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. Kubernetes cost visibility with OpenCost requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: namespace/controller/pod allocation.

#### U11-Q04 — Multiple choice
- **Unit(s):** 11 | **Level:** L1 | **Objective:** assess requests, usage and efficiency | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing requests, usage and efficiency?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: requests, usage and efficiency.

#### U11-Q05 — Multiple choice
- **Unit(s):** 11 | **Level:** L2 | **Objective:** assess idle and unallocated cost | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing idle and unallocated cost?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: idle and unallocated cost.

#### U11-Q06 — Multiple choice
- **Unit(s):** 11 | **Level:** L2 | **Objective:** assess label quality | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing label quality?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: label quality.

#### U11-Q07 — Artifact/number interpretation
- **Unit(s):** 11 | **Level:** L2 | **Objective:** assess allocation API response | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about allocation API response: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: allocation API response.

#### U11-Q08 — Artifact/number interpretation
- **Unit(s):** 11 | **Level:** L2 | **Objective:** assess network/egress caveats | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about network/egress caveats: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: network/egress caveats.

#### U11-Q09 — Artifact/number interpretation
- **Unit(s):** 11 | **Level:** L2 | **Type:** Artifact/number interpretation | **Objective:** interpret evidence and choose a justified action | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Prometheus scrape coverage falls from 100% to 80% while reported cost drops 15%. [SYNTHETIC]
**Model answer:** Lower report may reflect missing observations. Treat coverage drop as data-quality alert; compare manual model and avoid declaring savings.
**Worked interpretation:** State units and assumptions; show the arithmetic; distinguish what the artifact proves from what remains unknown; pair any action with an SLO/data-safety guardrail.
**Common wrong answers:** Extrapolating synthetic results to real provider spend; ignoring missing data; treating an estimate as a guarantee; taking irreversible action from one sample.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not a single dashboard number.
**Source alignment:** M15 Unit 11, applied examples and labs.
#### U11-Q10 — Configuration/model review
- **Unit(s):** 11 | **Level:** L3 | **Objective:** assess synthetic invoice reconciliation | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for synthetic invoice reconciliation; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: synthetic invoice reconciliation.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U11-Q11 — Configuration/model review
- **Unit(s):** 11 | **Level:** L3 | **Objective:** assess missing metrics or pricing | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for missing metrics or pricing; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: missing metrics or pricing.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U11-Q12 — Configuration/model review
- **Unit(s):** 11 | **Level:** L3 | **Objective:** assess dashboards and alerts | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for dashboards and alerts; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: dashboards and alerts.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U11-Q13 — Incident/diagnosis
- **Unit(s):** 11 | **Level:** L3 | **Objective:** assess lower total caused by missing coverage | **Time:** 20 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Incident: lower total caused by missing coverage causes an unexpected change in the shared platform. Explain safe diagnosis and recovery.
**Model answer:** **Impact:** identify affected tiers, SLOs, queue/backlog, data correctness and HCU exposure. **First safe action:** stop uncontrolled change and preserve evidence. **Hypotheses/evidence:** compare capacity, quota/contention, placement, autoscaler bounds, telemetry freshness, labels, billing lag and recent releases as applicable. **Mitigation:** smallest reversible action; protect critical tiers; pause unsafe automation. **Verification:** confirm SLO recovery, queue drain, bounded resource growth and telemetry correctness. **Prevention/communication:** add regression tests, owner, runbook, audit trail and blameless follow-up.
**Common wrong answers:** Common wrong response: immediately raising every limit or deleting a suspected idle resource without evidence.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: lower total caused by missing coverage.

#### U11-Q14 — Design with rubric
- **Unit(s):** 11 | **Level:** L4 | **Objective:** assess cost visibility governance | **Time:** 30 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Design a governed policy for cost visibility governance for inference, streaming, ETL, training and notebooks. Constraints: zero budget, synthetic data, no credentials, protect SLOs and data.
**Model answer:** **Sample answer:** define workload tiers and assumptions; model demand/resource/cost; select bounded controls; validate positive and negative cases; require owner approval, observability and rollback; state simulator limits. **10-point rubric:** workload model/assumptions 2; technical coherence 2; SLO/data safety 2; cost reasoning 1; observability/evidence 1; failure/rollback 1; ownership/governance 1.
**Common wrong answers:** Common weak answer: tool-first architecture without capacity math, owners, negative tests, evidence or rollback.
**Reliability/cost/safety implication:** Kubernetes cost visibility with OpenCost must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 11, topic: cost visibility governance.

### Unit 12 — GPU scheduling, sharing, and ML workload economics

**Source alignment:** [12-gpu-scheduling-sharing-and-ml-workload-economics.md](12-gpu-scheduling-sharing-and-ml-workload-economics.md).

#### U12-Q01 — Conceptual short-answer
- **Unit(s):** 12 | **Level:** L1 | **Objective:** assess GPU workload classes | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain GPU workload classes. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Gpu workload classes must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. GPU scheduling, sharing, and ML workload economics requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: GPU workload classes.

#### U12-Q02 — Conceptual short-answer
- **Unit(s):** 12 | **Level:** L1 | **Objective:** assess Kubernetes GPU resource model | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain Kubernetes GPU resource model. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Kubernetes gpu resource model must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. GPU scheduling, sharing, and ML workload economics requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: Kubernetes GPU resource model.

#### U12-Q03 — Conceptual short-answer
- **Unit(s):** 12 | **Level:** L1 | **Objective:** assess GPU placement constraints | **Time:** 5 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Explain GPU placement constraints. Why does it matter in a shared data/ML platform, and what decision should it influence?
**Model answer:** **Answer:** Gpu placement constraints must be interpreted in the context of workload tier, evidence freshness, ownership and the relevant SLO/governance objective. GPU scheduling, sharing, and ML workload economics requires evidence-based decisions, not a single-metric shortcut.
**Common wrong answers:** Common mistakes: treating a single metric as sufficient; confusing a policy target with a guarantee; omitting workload context.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: GPU placement constraints.

#### U12-Q04 — Multiple choice
- **Unit(s):** 12 | **Level:** L1 | **Objective:** assess allocated GPU versus utilization | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing allocated GPU versus utilization?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: allocated GPU versus utilization.

#### U12-Q05 — Multiple choice
- **Unit(s):** 12 | **Level:** L2 | **Objective:** assess sharing and partitioning modes | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing sharing and partitioning modes?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: sharing and partitioning modes.

#### U12-Q06 — Multiple choice
- **Unit(s):** 12 | **Level:** L2 | **Objective:** assess GPU fragmentation and topology | **Time:** 4 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Which approach is most defensible when managing GPU fragmentation and topology?
**Options:** A. Evidence-led policy with workload guardrails. B. Optimize cost/utilization alone. C. Treat missing telemetry as zero. D. Apply unbounded immediate automation.
**Model answer:** **Correct answer: A.** Use current evidence, explicit assumptions and workload-specific guardrails; validate the result with tests and observable outcomes.
**Common wrong answers:** **Option analysis:** A is correct because it preserves evidence and safety. B (optimize headline utilization/cost only) ignores workload outcomes. C (treat missing or stale telemetry as zero) confuses unknown with zero. D (automate immediate action across all namespaces) lacks scope, approval, audit and rollback.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: GPU fragmentation and topology.

#### U12-Q07 — Artifact/number interpretation
- **Unit(s):** 12 | **Level:** L2 | **Objective:** assess extended-resource quota | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about extended-resource quota: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: extended-resource quota.

#### U12-Q08 — Artifact/number interpretation
- **Unit(s):** 12 | **Level:** L2 | **Objective:** assess gang scheduling deadlock | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Interpret this synthetic evidence about gang scheduling deadlock: **[SYNTHETIC]** observed value = 68 units; planning capacity = 100 units; failure allowance = 15 units; reserve = 5 units. What is established, what remains uncertain, and what action is justified?
**Model answer:** **Worked answer:** usable capacity = 100 − 15 − 5 = 80 units. Remaining headroom against observed demand = 80 − 68 = 12 units. This passes only the stated scenario; check resource dimensions, peak window, forecast interval, placement constraints and SLOs before approval.
**Common wrong answers:** Common mistakes: comparing with nominal capacity; omitting failure allowance; treating the synthetic calculation as a provider guarantee.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: gang scheduling deadlock.

#### U12-Q09 — Artifact/number interpretation
- **Unit(s):** 12 | **Level:** L2 | **Type:** Artifact/number interpretation | **Objective:** interpret evidence and choose a justified action | **Time:** 10 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Doubling simulated GPUs yields throughput 1.2× baseline. [SYNTHETIC]
**Model answer:** Relative scaling efficiency=1.2/2=60%. Investigate input, synchronization and communication bottlenecks; assess cost per completed run and quality.
**Worked interpretation:** State units and assumptions; show the arithmetic; distinguish what the artifact proves from what remains unknown; pair any action with an SLO/data-safety guardrail.
**Common wrong answers:** Extrapolating synthetic results to real provider spend; ignoring missing data; treating an estimate as a guarantee; taking irreversible action from one sample.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not a single dashboard number.
**Source alignment:** M15 Unit 12, applied examples and labs.
#### U12-Q10 — Configuration/model review
- **Unit(s):** 12 | **Level:** L3 | **Objective:** assess idle notebook detection | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for idle notebook detection; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: idle notebook detection.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U12-Q11 — Configuration/model review
- **Unit(s):** 12 | **Level:** L3 | **Objective:** assess inference batching economics | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for inference batching economics; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: inference batching economics.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U12-Q12 — Configuration/model review
- **Unit(s):** 12 | **Level:** L3 | **Objective:** assess training scaling efficiency | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Review this deliberately flawed pseudoconfiguration for training scaling efficiency; identify at least three defects and repair them. It is not executable API syntax.
**Model answer:** **Defects and repairs:** (1) `average_only` omits peak/percentile and forecast uncertainty; use an evidence window and baseline comparison. (2) `scope: all_namespaces` is unbounded; restrict to approved lab-labelled resources and owners. (3) `action: apply_immediately` has no dry-run, allow-list, cap, audit or approval; stage report-only → quarantine → approved action. (4) `rollback: none` is unsafe; define measurable rollback thresholds. (5) missing/stale evidence is not handled; fail safe and alert.
**Common wrong answers:** Common mistakes: correcting syntax but leaving semantic risk; omitting negative tests; assuming a priority, alert or autoscaler guarantees capacity or spend control.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: training scaling efficiency.
**Flawed pseudoconfiguration:**
```text
observe: average_only
scope: all_namespaces
action: apply_immediately
owner_check: disabled
rollback: none
```
**Corrected policy contract:** validate owner and exclusions; dry-run first; allow-list targets; cap each action; log decisions; deny by default on missing/stale signals; provide kill switch and recovery path. Verify exact API syntax separately `[VERIFY]`.

#### U12-Q13 — Incident/diagnosis
- **Unit(s):** 12 | **Level:** L3 | **Objective:** assess self-host versus API break-even | **Time:** 20 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Incident: self-host versus API break-even causes an unexpected change in the shared platform. Explain safe diagnosis and recovery.
**Model answer:** **Impact:** identify affected tiers, SLOs, queue/backlog, data correctness and HCU exposure. **First safe action:** stop uncontrolled change and preserve evidence. **Hypotheses/evidence:** compare capacity, quota/contention, placement, autoscaler bounds, telemetry freshness, labels, billing lag and recent releases as applicable. **Mitigation:** smallest reversible action; protect critical tiers; pause unsafe automation. **Verification:** confirm SLO recovery, queue drain, bounded resource growth and telemetry correctness. **Prevention/communication:** add regression tests, owner, runbook, audit trail and blameless follow-up.
**Common wrong answers:** Common wrong response: immediately raising every limit or deleting a suspected idle resource without evidence.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: self-host versus API break-even.

#### U12-Q14 — Design with rubric
- **Unit(s):** 12 | **Level:** L4 | **Objective:** assess GPU fair-share and admission policy | **Time:** 30 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Design a governed policy for GPU fair-share and admission policy for inference, streaming, ETL, training and notebooks. Constraints: zero budget, synthetic data, no credentials, protect SLOs and data.
**Model answer:** **Sample answer:** define workload tiers and assumptions; model demand/resource/cost; select bounded controls; validate positive and negative cases; require owner approval, observability and rollback; state simulator limits. **10-point rubric:** workload model/assumptions 2; technical coherence 2; SLO/data safety 2; cost reasoning 1; observability/evidence 1; failure/rollback 1; ownership/governance 1.
**Common wrong answers:** Common weak answer: tool-first architecture without capacity math, owners, negative tests, evidence or rollback.
**Reliability/cost/safety implication:** GPU scheduling, sharing, and ML workload economics must be governed with workload outcomes, not headline cost alone.
**Source alignment:** M15 Unit 12, topic: GPU fair-share and admission policy.

## Cross-unit integration scenarios — X01–X42


### X01 — Forecast versus node ceiling
- **Unit(s):** U1 + U9 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Forecast demand is 90 CPU units; current allocatable capacity is 70; simulated node ceiling adds at most 10. [SYNTHETIC]
**Model answer:** Maximum modeled capacity is 80; shortfall is 10. Validate forecast uncertainty and constraints; do not assume autoscaler can exceed ceiling.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U1 + U9; integrated capstone operating model.

### X02 — Batch flood degrades inference
- **Unit(s):** U2 + U6 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Inference p95 breaches SLO while batch quota is only 60% consumed. [SYNTHETIC]
**Model answer:** Quota headroom does not prove node-level capacity. Inspect saturation, placement, requests/usage and priority; protect inference.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U2 + U6; integrated capstone operating model.

### X03 — Late budget alert
- **Unit(s):** U3 + U9 + U10 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Spend is 75 HCU; forecast 130 HCU against 100 HCU budget; billing feed is stale. [HYPOTHETICAL] [SYNTHETIC]
**Model answer:** Forecast overrun is 30 HCU. Stale data lowers confidence; bound replicas/nodes and inspect fresh usage proxies.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U3 + U9 + U10; integrated capstone operating model.

### X04 — Allocation residual
- **Unit(s):** U4 + U11 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Invoice 200 HCU; direct 120, shared 40, idle 20, unallocated 8. [HYPOTHETICAL]
**Model answer:** Attributed = 188; residual = 12 HCU. Preserve and investigate residual; never force it to zero.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U4 + U11; integrated capstone operating model.

### X05 — DR standby marked idle
- **Unit(s):** U5 + U6 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** DR namespace shows low CPU but has a standby label and no recent failover event in telemetry. [SYNTHETIC]
**Model answer:** Treat as false-positive risk. Verify purpose, owner, schedule, dependencies and telemetry; no automatic stop/delete.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U5 + U6; integrated capstone operating model.

### X06 — Right-sizing worsens latency
- **Unit(s):** U1 + U6 + U7 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Requests fall 20%; p95 latency breaches its SLO after release. [SYNTHETIC]
**Model answer:** Rollback/reject. Lower requests do not prove efficiency; test at peak load and compare cost per successful request at SLO.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U1 + U6 + U7; integrated capstone operating model.

### X07 — Spot deadline miss
- **Unit(s):** U8 + U6 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Nominal spot run is 40 HCU; lost work and restart add 24 HCU. [HYPOTHETICAL]
**Model answer:** Effective modeled cost is at least 64 HCU before checkpoint overhead/deadline risk. Compare fallback and deadline outcomes.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U8 + U6; integrated capstone operating model.

### X08 — Pending pod with spare CPU
- **Unit(s):** U2 + U9 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Aggregate CPU is free, but required label and toleration do not exist on eligible pools. [SYNTHETIC]
**Model answer:** Scheduling constraint, not aggregate shortage. Fix placement or add a valid pool under ceiling; generic nodes will not help.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U2 + U9; integrated capstone operating model.

### X09 — KEDA empty query
- **Unit(s):** U10 + U6 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Metrics query returns no series during scrape gap while freshness objective indicates backlog. [SYNTHETIC]
**Model answer:** Empty is not necessarily zero. Fail safe, alert and retain bounded baseline; verify scaler semantics `[VERIFY]`.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U10 + U6; integrated capstone operating model.

### X10 — OpenCost total falls
- **Unit(s):** U11 + U4 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Reported total falls from 100 to 70 HCU after a pricing input is removed. [HYPOTHETICAL] [SYNTHETIC]
**Model answer:** Not savings; likely missing coverage. Validate pricing/metrics/labels and reconcile manually.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U11 + U4; integrated capstone operating model.

### X11 — Idle notebook reserves GPU
- **Unit(s):** U5 + U12 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Notebook has low GPU utilization but owner, schedule and process state are unknown. [SYNTHETIC]
**Model answer:** Check owner, session, memory, schedule and checkpoint before quarantine/approved stop. No deletion from utilization alone.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U5 + U12; integrated capstone operating model.

### X12 — Hyperparameter sweep exhausts quota
- **Unit(s):** U2 + U12 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Sweep fills GPU quota; interactive model debugging queues. [SYNTHETIC]
**Model answer:** Use experiment budgets, admission caps, priority/fair share and atomic gang admission.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U2 + U12; integrated capstone operating model.

### X13 — Cross-region egress increase
- **Unit(s):** U4 + U6 + U11 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Routing change increases synthetic egress while compute allocation is flat. [SYNTHETIC]
**Model answer:** Inspect network evidence and routing change; apply documented allocation driver and reconcile.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U4 + U6 + U11; integrated capstone operating model.

### X14 — Telemetry reduction increases diagnosis time
- **Unit(s):** U6 + U7 + U11 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Telemetry saves 8 HCU but time-to-localize rises from 10 to 35 minutes. [HYPOTHETICAL]
**Model answer:** Not automatically beneficial. Quantify incident impact and restore minimum useful signals or redesign sampling.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U6 + U7 + U11; integrated capstone operating model.

### X15 — Peak commitment underused
- **Unit(s):** U1 + U6 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Commitment sized to peak demand is underused after workload mix shifts. [SYNTHETIC]
**Model answer:** Model commitment regret under several demand/mix scenarios; retain flexibility where uncertainty is material.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U1 + U6; integrated capstone operating model.

### X16 — Cleanup targets protected volume
- **Unit(s):** U5 + U4 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Volume has no recent reads but carries legal-hold metadata. [SYNTHETIC]
**Model answer:** Deny automated deletion. Legal hold/data classification supersedes utilization heuristics.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U5 + U4; integrated capstone operating model.

### X17 — Shared-cost label gaming
- **Unit(s):** U4 + U6 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Teams can alter labels to lower showback; shared pool allocated by pod count only. [SYNTHETIC]
**Model answer:** Use ownership registry, provenance, documented drivers and sensitivity analysis; govern incentives.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U4 + U6; integrated capstone operating model.

### X18 — Serving rollout doubles replicas
- **Unit(s):** U7 + U10 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Release changes replica count and KEDA max; old/new pods overlap during rollout. [SYNTHETIC]
**Model answer:** Calculate peak simultaneous replicas, downstream capacity, quota and node ceiling; ring promote with rollback.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U7 + U10; integrated capstone operating model.

### X19 — Real idle and false positive look alike
- **Unit(s):** U5 + U11 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Two resources show zero CPU; one is abandoned dev, one is DR standby with telemetry gap. [SYNTHETIC]
**Model answer:** Missing data is unknown, not zero. Confirm ownership, schedule and dependencies; protect DR.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U5 + U11; integrated capstone operating model.

### X20 — Integrated multi-signal crisis
- **Unit(s):** U1–U5 + U9 + U11 | **Level:** L4 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Runaway replicas, batch contention, untagged workload and 12-HCU invoice residual occur together. [HYPOTHETICAL] [SYNTHETIC]
**Model answer:** Stabilize scaling and protect SLO first; diagnose pending/quota/ceiling; preserve residual; find owner; cleanup only after approval.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U1–U5 + U9 + U11; integrated capstone operating model.
**10-point rubric:** diagnosis/evidence 2; model/arithmetic 2; reliability/safety 2; guardrails/negative tests 2; ownership/communication/audit 2.

### X21 — Checkpoint interval
- **Unit(s):** U8 + U12 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Checkpoint costs 3 HCU/save; longer interval increases lost work. [HYPOTHETICAL]
**Model answer:** Compare checkpoint overhead with expected lost work/restart under stated assumptions; run sensitivity analysis.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U8 + U12; integrated capstone operating model.

### X22 — GPU gang deadlock
- **Unit(s):** U2 + U12 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Two jobs each need 2 GPUs; 3 are free; scheduler partially reserves one for each. [SYNTHETIC]
**Model answer:** Partial reservations can deadlock both. Use atomic gang admission or release partial resources.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U2 + U12; integrated capstone operating model.

### X23 — Consolidation disrupts jobs
- **Unit(s):** U8 + U9 + U6 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Consolidation targets node with checkpointing batch and latency-sensitive pod. [SYNTHETIC]
**Model answer:** Review disruption budget, drain and recovery; defer or migrate safely and verify SLO.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U8 + U9 + U6; integrated capstone operating model.

### X24 — KEDA exceeds downstream bound
- **Unit(s):** U10 + U2 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Queue suggests 12 workers; database safely supports 6 consumers. [SYNTHETIC]
**Model answer:** Set max ≤6 under stated assumption; tune target/throughput rather than overwhelming downstream.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U10 + U2; integrated capstone operating model.

### X25 — Quota unused but pod pending
- **Unit(s):** U2 + U9 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Namespace quota allows 20 CPU; pod requests 8; each eligible node has only 4 free. [SYNTHETIC]
**Model answer:** Quota is not node capacity. Provide feasible placement or approved capacity; diagnose constraints.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U2 + U9; integrated capstone operating model.

### X26 — Budget forecast and unallocated spend
- **Unit(s):** U3 + U4 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Actual-like spend 60 HCU; forecast 95; 15 HCU unallocated. [HYPOTHETICAL]
**Model answer:** Separate forecast from actual. Investigate unallocated ownership; it is not necessarily incremental spend.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U3 + U4; integrated capstone operating model.

### X27 — Allocation model changes team totals
- **Unit(s):** U4 + U11 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Switching request to usage model shifts 18 HCU between teams; invoice total unchanged. [HYPOTHETICAL]
**Model answer:** Attribution changed, not spend. Sensitivity test, version the model and communicate before chargeback.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U4 + U11; integrated capstone operating model.

### X28 — Release estimator misses overlap
- **Unit(s):** U7 + U1 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Steady estimate is 12 CPU; rollout overlap reaches 18 CPU. [SYNTHETIC]
**Model answer:** Add surge/overlap to peak estimator; verify quota/headroom and planted-regression tests.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U7 + U1; integrated capstone operating model.

### X29 — Spot interruption retry storm
- **Unit(s):** U8 + U10 + U2 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Workers restart together; queue and retries multiply. [SYNTHETIC]
**Model answer:** Bound retries, diversify pools, checkpoint, jitter recovery and protect downstream services.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U8 + U10 + U2; integrated capstone operating model.

### X30 — OpenCost/manual difference
- **Unit(s):** U11 + U4 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** OpenCost 88 HCU; manual model 100; 12% label coverage missing. [HYPOTHETICAL] [SYNTHETIC]
**Model answer:** Inspect labels, metrics, idle/shared categories and time windows; reconcile before conclusions.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U11 + U4; integrated capstone operating model.

### X31 — GPU busy but throughput low
- **Unit(s):** U12 + U6 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** GPU utilization is high while successful inference throughput falls and p95 rises. [SYNTHETIC]
**Model answer:** Utilization is not outcome. Inspect memory, batching, input pipeline and contention; optimize cost per successful inference at SLO.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U12 + U6; integrated capstone operating model.

### X32 — Training scale-out weak
- **Unit(s):** U12 + U1 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Doubling simulated GPUs produces only 1.2× throughput. [SYNTHETIC]
**Model answer:** Relative scaling efficiency = 1.2/2 = 60%. Investigate synchronization/input bottlenecks and cost per completed run.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U12 + U1; integrated capstone operating model.

### X33 — Scale-to-zero misses freshness
- **Unit(s):** U10 + U6 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Cold start is 4 minutes; freshness objective is 2 minutes. [SYNTHETIC]
**Model answer:** Scale-to-zero violates objective under assumption; retain warm minimum or scheduled pre-warm and compare HCU.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U10 + U6; integrated capstone operating model.

### X34 — Node ceiling blocks launch
- **Unit(s):** U1 + U7 + U9 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Launch requires 30 CPU additional; ceiling permits 20. [SYNTHETIC]
**Model answer:** Plan is infeasible by 10 CPU. Stage traffic or approve capacity after review; do not bypass ceiling.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U1 + U7 + U9; integrated capstone operating model.

### X35 — Identified savings not realized
- **Unit(s):** U5 + U4 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Waste report identifies 25 HCU/month but no resource has been stopped. [HYPOTHETICAL]
**Model answer:** Identified is not realized. Track owner decision, action completion, post-action measurement and service impact.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U5 + U4; integrated capstone operating model.

### X36 — DR savings threaten RTO
- **Unit(s):** U6 + U4 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Reducing standby saves 15 HCU/month but recovery test exceeds RTO. [HYPOTHETICAL] [SYNTHETIC]
**Model answer:** Reject or redesign; measured recovery objective outranks nominal saving.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U6 + U4; integrated capstone operating model.

### X37 — Showback missing owner
- **Unit(s):** U4 + U11 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Workload falls into unallocated; team claims it but registry has no project entry. [SYNTHETIC]
**Model answer:** Keep unallocated until verified; update registry with effective date and audit trail.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U4 + U11; integrated capstone operating model.

### X38 — Forecast misses peak window
- **Unit(s):** U1 + U6 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Forecast has lower aggregate MAE than baseline but underpredicts inference peak. [SYNTHETIC]
**Model answer:** Evaluate peak-window error and interval coverage, not MAE alone; select method by decision loss.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U1 + U6; integrated capstone operating model.

### X39 — Fair-share starves small tenant
- **Unit(s):** U2 + U12 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Large training jobs occupy GPUs; small tenant never obtains a full gang. [SYNTHETIC]
**Model answer:** Measure wait/share; use fair share/aging or reservation and atomic gang admission.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U2 + U12; integrated capstone operating model.

### X40 — Pricing config incomplete
- **Unit(s):** U11 + U3 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Pricing config omits one category and reported cost falls sharply. [SYNTHETIC]
**Model answer:** Treat as data-quality incident; validate inputs/coverage and manual HCU comparison.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U11 + U3; integrated capstone operating model.

### X41 — Telemetry gap triggers cleanup
- **Unit(s):** U5 + U11 | **Level:** L3 | **Type:** Integrated incident/artifact | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Scrape gap produces zero usage; both cost and cleanup dashboards mark workload idle. [SYNTHETIC]
**Model answer:** Missing data is not zero. Suppress cleanup eligibility and restore trustworthy telemetry.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U5 + U11; integrated capstone operating model.

### X42 — Integrated governance design
- **Unit(s):** U1–U12 | **Level:** L4 | **Type:** Design | **Time:** 15 minutes `[ILLUSTRATIVE]`
**Question and evidence:** Platform adds inference tier and training queue while preserving SLOs and transparent HCU showback. [ASSUMPTION]
**Model answer:** Build the loop: forecast/headroom → quotas/priorities → budgets/guardrails → allocation → safe cleanup → trade-offs/release review → spot/nodes/KEDA → OpenCost/GPU evidence. Assign owners and negative tests.
**Reasoning:** Stabilize the highest-impact workload; compare independent signals; state assumptions; choose a bounded reversible mitigation; verify SLO, queue, capacity and cost data; record owner and follow-up.
**Common wrong answers:** Treating a dashboard as ground truth; bypassing a ceiling without review; forcing allocation to invoice; deleting idle-looking data; claiming simulation proves provider behavior.
**Source alignment:** M15 U1–U12; integrated capstone operating model.
**10-point rubric:** diagnosis/evidence 2; model/arithmetic 2; reliability/safety 2; guardrails/negative tests 2; ownership/communication/audit 2.

## Exactly 16 additional design-review whiteboard prompts


### DR01 — Capacity forecasting and headroom policy
**Scenario and constraints:** Design a forecast for inference, ETL, streaming, training and notebooks. Deliver baseline comparison, prediction intervals, N−1 math, exhaustion alerts and review runbook. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: forecast 2; headroom 2; workload tiers 2; lead time 1; SLO guardrails 2; ownership 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR02 — Priority, quota, preemption and fair share
**Scenario and constraints:** Design CPU/memory/GPU policy for critical inference, streaming, batch and training. Deliver quota matrix, admission tests, fair-share and starvation response. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: tiers 2; quota semantics 2; fairness 2; preemption safety 2; tests 1; governance 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR03 — Layered budget and spending guardrails
**Scenario and constraints:** Design freshness-aware budgets, usage proxies, preventive ceilings, approvals and safe response ladder. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: alerts 2; preventive controls 2; identity 2; safe automation 2; observability 1; audit 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR04 — Allocation and shared-cost rules
**Scenario and constraints:** Design ownership registry, direct/shared/idle/unallocated allocation, reconciliation and sensitivity. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: metadata 2; drivers 2; shared rationale 2; reconciliation 2; disputes 1; unit economics 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR05 — Idle cleanup with safe exclusions
**Scenario and constraints:** Design detection for abandoned dev, quarterly jobs, DR standby and legal-hold storage. Include quarantine, approval and recovery. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: evidence 2; false positives 2; data safety 2; staged actions 2; recovery/audit 2.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR06 — Tier cost/reliability policy
**Scenario and constraints:** Design policy for online inference, streaming, ETL, training and notebooks. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: tiers 2; outcome metrics 2; cost model 2; rollback 2; ownership 1; assumptions 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR07 — Production release review gate
**Scenario and constraints:** Design manifest/IaC estimator, quota checks, surge math, noise-aware gate, canary and post-release review. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: peak footprint 2; quota 2; tests 2; release safety 2; evidence 1; approvals 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR08 — Spot eligibility and checkpoint policy
**Scenario and constraints:** Design eligibility, checkpoint/resume, interruption model, fallback and deadline guardrails. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: eligibility 2; correctness 2; effective economics 2; fallback 2; retries 1; evidence 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR09 — Node provisioning and ceilings
**Scenario and constraints:** Design Pending diagnosis, simulated pool policy, ceilings, consolidation and disruption budget. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: diagnosis 2; packing 2; ceilings 2; disruption safety 2; fidelity 1; owner 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR10 — Event-driven autoscaling bounds
**Scenario and constraints:** Design queue target, ScaledObject/ScaledJob choice, downstream max, scale-to-zero and empty-signal tests. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: throughput 2; signal validity 2; downstream bound 2; zero policy 1; tests 2; governance 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR11 — OpenCost accuracy and reconciliation
**Scenario and constraints:** Design HCU pricing, manual cross-check, label/coverage checks, synthetic invoice and alerts. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: coverage 2; labels 2; cross-check 2; residuals 2; security 1; fidelity 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR12 — GPU queueing and sharing
**Scenario and constraints:** Design gang admission, fair share, isolation, idle control and inference/training economics. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: scheduling 2; gang 2; isolation 2; economics 2; idle safety 1; SLO/quality 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR13 — FinOps operating model and KPIs
**Scenario and constraints:** Design owners, KPI definitions, monthly review, exception policy and maturity actions. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: ownership 2; KPIs 2; data integrity 2; cadence 1; exceptions 2; action tracking 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR14 — Commitments versus flexibility
**Scenario and constraints:** Model uncertain demand/mix scenarios and regret from fixed commitments versus flexible capacity. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: scenarios 2; uncertainty 2; regret math 2; flexibility 2; assumptions 1; triggers 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR15 — Cost versus observability and DR
**Scenario and constraints:** Evaluate telemetry, standby and multi-region choices against time-to-localize and recovery objectives. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: observability 2; DR/RTO 2; cost 2; failure scenarios 2; measurement 1; decision record 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

### DR16 — Showback versus chargeback incentives
**Scenario and constraints:** Design transparent allocation, dispute workflow and anti-gaming controls before any chargeback. Zero-budget local-first; synthetic data/HCU; no billable resources; protect SLOs and data.
**Expected deliverables:** diagram, assumptions register, policy/configuration contract, calculation, SLO guardrails, runbook, negative tests and evidence plan.
**10-point rubric:** Rubric: transparency 2; accuracy 2; incentives 2; disputes 2; audit 1; staged adoption 1.
**Sample defensible answer outline:** define tiers and assumptions; model demand/resource/cost; select bounded controls; test positive and negative paths; assign owner, approval, observability and rollback; state fidelity limits.
**Likely reviewer objections:** Which input is synthetic? What failure case is omitted? What if telemetry is missing? Who approves exceptions? What proves reliability did not degrade?

## Remediation matrix

| Weak group | Revisit | Remediation |
| U01-Q01–Q14 | [01-platform-capacity-forecasting-and-headroom.md](01-platform-capacity-forecasting-and-headroom.md) | Rework the core model, redo one calculation/artifact lab, then explain a failure mode with evidence. |
| U02-Q01–Q14 | [02-workload-priorities-quotas-and-resource-contention.md](02-workload-priorities-quotas-and-resource-contention.md) | Rework the core model, redo one calculation/artifact lab, then explain a failure mode with evidence. |
| U03-Q01–Q14 | [03-cloud-budget-alerts-and-spending-guardrails.md](03-cloud-budget-alerts-and-spending-guardrails.md) | Rework the core model, redo one calculation/artifact lab, then explain a failure mode with evidence. |
| U04-Q01–Q14 | [04-cost-allocation-by-team-project-and-workload.md](04-cost-allocation-by-team-project-and-workload.md) | Rework the core model, redo one calculation/artifact lab, then explain a failure mode with evidence. |
| U05-Q01–Q14 | [05-idle-resource-detection-and-automated-cleanup.md](05-idle-resource-detection-and-automated-cleanup.md) | Rework the core model, redo one calculation/artifact lab, then explain a failure mode with evidence. |
| U06-Q01–Q14 | [06-cost-reliability-and-performance-tradeoffs.md](06-cost-reliability-and-performance-tradeoffs.md) | Rework the core model, redo one calculation/artifact lab, then explain a failure mode with evidence. |
| U07-Q01–Q14 | [07-capacity-and-cost-review-for-production-releases.md](07-capacity-and-cost-review-for-production-releases.md) | Rework the core model, redo one calculation/artifact lab, then explain a failure mode with evidence. |
| U08-Q01–Q14 | [08-spot-and-preemptible-instances-for-data-workloads.md](08-spot-and-preemptible-instances-for-data-workloads.md) | Rework the core model, redo one calculation/artifact lab, then explain a failure mode with evidence. |
| U09-Q01–Q14 | [09-karpenter-and-cluster-autoscaler-node-provisioning.md](09-karpenter-and-cluster-autoscaler-node-provisioning.md) | Rework the core model, redo one calculation/artifact lab, then explain a failure mode with evidence. |
| U10-Q01–Q14 | [10-event-driven-autoscaling-with-keda.md](10-event-driven-autoscaling-with-keda.md) | Rework the core model, redo one calculation/artifact lab, then explain a failure mode with evidence. |
| U11-Q01–Q14 | [11-kubernetes-cost-visibility-with-opencost.md](11-kubernetes-cost-visibility-with-opencost.md) | Rework the core model, redo one calculation/artifact lab, then explain a failure mode with evidence. |
| U12-Q01–Q14 | [12-gpu-scheduling-sharing-and-ml-workload-economics.md](12-gpu-scheduling-sharing-and-ml-workload-economics.md) | Rework the core model, redo one calculation/artifact lab, then explain a failure mode with evidence. |
| X01, X08, X22, X33 | Units 1, 2, 7, 9 | Rebuild demand-to-node math and diagnose Pending pods. |
| X03, X04, X27, X37 | Units 3, 4, 11 | Reconcile synthetic usage/allocation and identify freshness/coverage gaps. |
| X05, X16, X35, X39 | Units 5, 6, 11 | Re-run false-positive cleanup and reliability guardrail review. |
| X07, X21, X28, X31 | Units 2, 8, 10, 12 | Recalculate interruption, checkpoint, queue and GPU economics. |

## Claim register and verification notes

| Claim | Source basis | Confidence | Verification action |
| Forecasts should be compared with a naive baseline and rolling-origin back-testing. | Unit 1 forecast/bake-off sections | Source-derived | Reproduce with synthetic data and local tests. |
| Headroom should account for failure modes, lead time and forecast error. | Unit 1 headroom sections | Source-derived | Review assumptions against workload SLOs. |
| Priority does not create physical capacity or guarantee scheduling. | Unit 2 scheduling sections | Source-derived | Verify behavior against installed Kubernetes version. |
| Requests, limits and quota are distinct controls. | Unit 2 resource governance | Source-derived | Check API schema and quota scopes. |
| Budget alerts are not hard caps; billing may lag. | Unit 3 budget/freshness sections | Source-derived | Provider freshness is out of scope unless separately researched. |
| Allocation is a model and must preserve residuals. | Unit 4 reconciliation sections | Source-derived | Run independent synthetic invoice reconciliation. |
| Low utilization alone is not proof of safe deletion. | Unit 5 cleanup sections | Source-derived | Test DR, schedule and legal-hold false positives. |
| Cost reductions require reliability/performance measurement. | Unit 6 trade-off sections | Source-derived | Run staged experiments and rollback checks. |
| Release review includes rollout overlap and autoscaling maximum. | Unit 7 release sections | Source-derived | Validate estimator against rendered manifests. |
| Spot economics include lost work, checkpointing and fallback. | Unit 8 economics sections | Source-derived | Provider reclaim behavior remains unverified. |
| Node provisioning practical work is simulated. | Unit 9 scope/fidelity statement | Source-derived | Do not infer provider behavior from simulator. |
| KEDA signal/CRD behavior is version-sensitive. | Unit 10 failure behavior | Source-derived; `[VERIFY]` | Verify exact installed scaler/CRD semantics. |
| OpenCost results depend on labels, metrics, pricing and allocation. | Unit 11 scope/reconciliation | Source-derived | Verify chart/API/metrics for installed release. |
| GPU allocation, utilization, memory and throughput differ. | Unit 12 GPU model | Source-derived | Simulator is not hardware performance evidence. |
| Gang admission can deadlock under partial reservation. | Unit 12 scheduling | Source-derived | Test atomic admission/release in simulator. |

### Version-sensitive checklist

- Kubernetes: verify API server schema, ResourceQuota keys, PriorityClass/preemption, GPU extended-resource handling and exact manifest syntax with the installed version. `[VERIFY]`
- Metrics Server/HPA: record versions and confirm compatibility; do not assume metric names/defaults. `[VERIFY]`
- Cluster Autoscaler/Karpenter/KWOK: verify provider integration, APIs, NodePool fields, disruption/consolidation and simulator-provider compatibility. Node provisioning in Unit 9 remains simulated. `[VERIFY]`
- KEDA: verify CRDs, scaler metadata, activation, fallback, empty-result behavior and HPA ownership. Source baseline KEDA 2.21.0 is `[VERSION-SENSITIVE]`; check compatibility before installation.
- OpenCost: source baseline application 1.121.3/chart 2.5.33 is `[VERSION-SENSITIVE]`; verify image digest, chart values, API and metrics before use.
- Prometheus/promtool: use matching versions and validate rule syntax/metric availability against local scrape configuration. `[VERIFY]`
- NVIDIA device plugins, GPU Operator, MIG/MPS/time-slicing, DCGM, Kueue/Volcano/YuniKorn and serving frameworks remain awareness/compatibility topics unless verified against actual hardware and drivers. `[VERIFY]`
- Provider pricing, billing exports, budgets, spot notice semantics, commitments and instance catalogs are not asserted; no real prices or commercial terms appear. `[VERIFY]`

## Final authenticity and structural audit

| Audit | Status | Evidence | Defect/remaining action |
|---|---|---|---|
| Count and uniqueness | PASS — structural | 168 unit questions + 42 cross-unit = 210; IDs U01-Q01–U12-Q14 and X01–X42. | Human should rerun ID/count check before repository integration. |
| Unit distribution | PASS — structural | Every unit has 3 conceptual, 3 MCQ, 3 artifact, 3 config, 1 incident and 1 design. | Verify rendered Markdown grouping. |
| MCQ explanations | PASS — structural | All 36 MCQs have four options and explanations for all distractors. | Review exact version-specific claims separately. |
| Configuration review | PASS — structural | All 36 reviews identify at least three defects and repairs; pseudoconfig is not executable. | Do not copy as production YAML. |
| Cross-unit coverage | PASS — authored | 42 distinct scenarios include multi-stage incidents, arithmetic/reconciliation and design. | Expand orally where deeper evidence is needed. |
| Technical authenticity | OPEN — human verification | Version-sensitive items are marked; no runtime syntax test claimed. | Verify installed APIs, flags, metrics and compatibility. |
| Cost and safety | PASS — authoring | HCU only; no billable resources/credentials; cleanup safety stated. | Keep all experiments lab-scoped and dry-run-first. |
| Source consistency | PASS — authoring | Scope mapped to supplied M15 Units 1–12 and capstone. | Reconfirm filenames on repository copy. |
| Runtime validation | OPEN — not performed | No cluster, cloud, GPU, scripts or manifests were run. | Learner must execute labs/negative tests. |
| File integrity | PASS — output | Standalone `practice-questions.md` created. | Repository copy not performed. |

### Limitations and sign-off

This is a source-aligned assessment bank, not a production runbook or certification. AI authoring review does not replace a human technical audit. No live documentation, cluster, cloud, GPU, script or manifest was executed for this artifact. All amounts are hypothetical HCU; all evidence is synthetic. Simulated nodes/GPUs do not reproduce provider behavior or hardware performance. No existing repository file was intentionally modified. **Content status: DRAFT-AUDITED; human verification remains open.**
