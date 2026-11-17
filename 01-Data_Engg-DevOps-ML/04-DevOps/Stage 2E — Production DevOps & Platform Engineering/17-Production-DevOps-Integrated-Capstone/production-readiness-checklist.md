# Production Readiness Checklist — M17 Unit 2

> **Target file:** `production-readiness-checklist.md`  
> **Module:** M17 — Production DevOps Integrated Capstone  
> **Unit:** 2 — Production readiness checklist  
> **Estimated time:** [ASSUMPTION] 10–16 hours to study and implement the checklist runner, plus 6–12 hours to apply it to one profile. Planning estimates, not guarantees.  
> **Prerequisites:** M01–M16 outcomes consumed; emphasis on M02 CI/CD, M03 operations, M04 networking/TLS, M05 storage, M06 packaging, M07 IaC, M08 GitOps, M09 identity/secrets, M10 SRE/SLO/incident/ORR, M11 observability, M12 supply chain, M13 backup/DR, M15 capacity/FinOps, M16 platform engineering.  
> **Core tools:** GitHub Actions, `kind`, `kubectl`, Helm or Kustomize, Argo CD, Prometheus/Grafana, backup/verification tools.  
> **Awareness tools:** cosign, Argo Rollouts, Kyverno/Gatekeeper, LocalStack, Chaos Mesh/Litmus. Optional; not required for Cap-Core.  
> **Last reviewed:** 2026-11-04  
> **Tool baseline assumed:** no versions asserted; record installed versions and verify version-sensitive syntax against official documentation.  
> **Stack profile:** Cap-Core / Cap+Security / Cap+Chaos.  
> **Footprint:** measure yours. 4 CPU / 8 GB RAM / 30 GB disk is a planning envelope, not a guarantee that all components fit simultaneously.  
> **Scope:** lab-scale readiness instrument, not certification of production readiness.

## Unit 2 — Production readiness checklist

### M17 capstone contract

The following contract statements are reproduced verbatim.

**Stage exit criteria**

> deploy a service through the full tested pipeline; reconcile desired state from Git; apply identity and security controls; demonstrate metrics/logs/alerts; execute a failure, rollback, backup restore, and teardown; map every acceptance criterion to evidence.

**Evidence artifact set**

> capstone repository, architecture diagram, runbooks, CI/GitOps evidence, incident report, restore evidence, signed-off checklist.

**Pass rule**

> every criterion is demonstrated, evidence is committed or safely retained, and the lab is reproducible from its README/runbook.

Unit 2 defines a readiness decision instrument. It does not replace Unit 1 requirements, Unit 3 incident/recovery scoring, Unit 4 security/release scoring, Unit 5 cost/reliability scoring, Unit 6 platform/delivery scoring, or the projects.

### Contents

- [2.0 Why this matters in production](#20-why-this-matters-in-production)
- [2.1 Learning objectives](#21-learning-objectives)
- [2.2 Concept map and vocabulary](#22-concept-map-and-vocabulary)
- [2.3 Level 1 — Beginner](#23-level-1--beginner)
- [2.4 Level 2 — Intermediate](#24-level-2--intermediate)
- [2.5 Level 3 — Advanced](#25-level-3--advanced)
- [2.6 Level 4 — Expert](#26-level-4--expert)
- [2.7 SRE lens](#27-sre-lens)
- [2.8 Security lens](#28-security-lens)
- [2.9 Complete production readiness checklist](#29-complete-production-readiness-checklist)
- [2.10 Automated checklist runner and tests](#210-automated-checklist-runner-and-tests)
- [2.11 Hands-on lab set](#211-hands-on-lab-set)
- [2.12 Evidence artifacts](#212-evidence-artifacts)
- [2.13 Common review-board questions](#213-common-review-board-questions)
- [2.14 Sources and verification notes](#214-sources-and-verification-notes)
- [2.15 Final self-review and sign-off](#215-final-self-review-and-sign-off)

### Source and scope boundary

Reviewed sources: attached Unit 2 generation prompt; latest M17 syllabus-generation prompt; `Roadmap(20261104-055747).md`; latest `capstone-requirements(1).md`; available generated Unit 3, Unit 5, and Unit 6 documents. The M17 tree names `production-readiness-checklist.md` as Unit 2, but a completed Unit 2 target was not present in the inspected generated-file set. This is therefore a standalone Unit 2 deliverable, not an edit to a previously completed Unit 2 document. The final Unit 4 document and final project documents were not available in the inspected set; no claim is made that their final contents were reviewed.

**Cross-document discrepancy:** latest Unit 1 is canonical: `REQ-008` = plaintext-secret prevention; `REQ-015` = controlled failure investigation; `REQ-016` = Git-controlled rollback; `REQ-017` = backup and actual restore; `REQ-018` = restore integrity and measured RPO/RTO. Unit 1 acceptance criteria: `AC-006` = incident investigation; `AC-007` = rollback; `AC-008` = backup/restore; `AC-011` = teardown; `AC-012` = fresh-clone/traceability. The available Unit 3 document uses an older conflicting crosswalk; Unit 6 explicitly flags the mismatch. This checklist follows latest Unit 1 and does not silently propagate the Unit 3 mapping. Unit 3 itself is outside this file's scope and is not changed.

---

### 2.0 Why this matters in production

A process can start without being healthy. A deployment can succeed without being safe. A backup can exist without being restorable. A dashboard can open while its queries are empty. A rollback can report success while the wrong digest is still running.

**Production readiness** is a bounded claim: for a declared workload, environment, dependencies, and service objectives, the service is operable, observable, recoverable, secure, supportable, and appropriately sized—and the team can demonstrate those claims with current evidence.

| Dimension | Operational meaning |
|---|---|
| Operable | Deployment, diagnosis, change, recovery, and cleanup procedures are known and safe. |
| Observable | Symptoms are measurable; metrics/logs/dashboards/alerts are useful, correlated, owned, and tested. |
| Recoverable | Rollback and restore have been executed; service and data correctness are verified. |
| Secure | Identity, authorization, secrets, workload hardening, network boundaries, and artifact integrity have defensible controls. |
| Supportable | Owners, escalation, runbooks, incident communication, and residual-risk decisions are explicit. |
| Appropriately sized | Resource and capacity assumptions match the declared workload and objectives. |

Distinguish four claims: **service starts** (a process can run); **deployment succeeds** (resources are applied/reconciled); **operationally ready** (controls are demonstrated for a declared scope); **approved for a production scope** (authorized reviewers accept evidence and residual risk for a named environment/release). These are not synonyms.

An **Operational Readiness Review (ORR)** is a structured review of a service's operational controls before a launch or material change. It inspects evidence, tests recovery and failure paths, challenges assumptions, and records a scoped decision. M10 supplies SRE/incident practice; M17 integrates and assesses it rather than reteaching M01–M16 tools.

A checklist is a decision instrument, not a ceremonial list. Each row must be falsifiable: precise question, risk, verification, evidence, owner, profile, severity, status, freshness, and module mapping. “Secure,” “monitored,” “fast,” “highly available,” and “backup configured” are not pass conditions.

A high percentage of passing rows cannot cancel a critical blocker. Exposed credentials, fabricated evidence, unsafe target context, unverified required restore, or failed required rollback cannot be averaged away.

**Fidelity caveat:** a laptop `kind` cluster demonstrates mechanics, repeatability, and evidence discipline at lab scale. It does not demonstrate real multi-region behavior, real cloud limits, real production traffic, or end-to-end production readiness. A passing capstone proves the learner can produce and defend evidence at lab scale, nothing more.

**Stack profiles and resource discipline**

- **Cap-Core:** `kind` + Argo CD + minimal Prometheus/Grafana + local registry + backup tooling. This is the default integration path.
- **Cap+Security:** Cap-Core plus one policy engine and cosign where feasible. This is optional.
- **Cap+Chaos:** Cap-Core plus one chaos tool **or** scripted fault injection, not both by default. This is optional.
- Do not run every heavy component simultaneously on an 8 GB machine. Start the smallest profile, collect evidence, stop components that are not needed, then add one optional layer at a time. Use one GitOps controller and at most one policy engine in the lab.
- Before bootstrap, measure available CPU, memory, and disk; record the actual footprint. During runs, observe host/container resource use and stop if the machine becomes unstable. “Measure yours” is the policy; no resource-footprint numbers are invented here.
- For WSL2, account for Docker networking, VM memory limits, filesystem performance, permissions, and line endings. Native Linux may differ in cgroup, filesystem, and container-runtime behavior. Record the host environment with the evidence.

### 2.1 Learning objectives

1. **[L1]** Explain startup, deployment success, operational readiness, and approval for a declared production scope.
2. **[L1]** Identify every field in a checklist record and explain what evidence satisfies it.
3. **[L2]** Apply the checklist to a selected profile and produce reproducible evidence.
4. **[L2]** Use Pass/Fail/N-A/Waived/Not Run/Unknown honestly.
5. **[L2]** Run a YAML validator and planted-defect tests; interpret a JSON report.
6. **[L3]** Design falsifiable controls with applicability, severity, gates, freshness, and negative tests.
7. **[L3]** Detect stale, missing, mismatched, weak, or misleading evidence.
8. **[L4]** Conduct an ORR, independently challenge evidence, calibrate reviewers, and record Go / Go with conditions / No-Go.

### 2.2 Concept map and vocabulary

```text
Scope + profile + environment
          -> checklist question
          -> control / safeguard
          -> verification / test
          -> evidence tied to commit + artifact + time
          -> owner + reviewer + severity + status
          -> ORR decision + conditions + follow-up
```

| Term | Meaning |
|---|---|
| Question | What the reviewer asks. |
| Control | Mechanism intended to reduce a risk. |
| Test | Action that demonstrates the control works. |
| Evidence | Retained output supporting the result. |
| Owner | Role accountable for implementation/explanation. |
| Attestation | Human record of reviewer identity, scope, decision, and rationale. |
| Sign-off | Authorized decision for a named scope and date. |
| Applicability profile | Workload type against which the item is assessed. |
| Gate | Non-negotiable condition not averaged away by a score. |
| Freshness | Whether evidence still represents current code/configuration/deployment. |
| SLI/SLO | Service Level Indicator / Service Level Objective. |
| RPO/RTO | Recovery Point Objective / Recovery Time Objective. |
| Digest | Immutable artifact content identity. |
| Traceability | Requirement → acceptance criterion → control → test → evidence. |

**Four-level learning contract**

| Level | Name | Learner outcome |
|---|---|---|
| **L1** | Beginner | Reads a checklist item and states what evidence satisfies it. |
| **L2** | Intermediate | Produces correct, reproducible evidence for each criterion and self-assesses honestly. |
| **L3** | Advanced | Designs checklist items and controls ambiguity, applicability, severity, waivers, freshness, and trade-offs. |
| **L4** | Expert | Runs a readiness/launch review, challenges evidence, detects gaming and gaps, calibrates reviewers, and makes a go/no-go decision with conditions. |

Status semantics:

| Status | Meaning | Treatment |
|---|---|---|
| `Pass` | Verification ran against relevant version; fresh evidence meets pass condition. | Candidate for human review, not automatic Go. |
| `Fail` | Control absent, failed, unsafe, or insufficiently evidenced. | Finding; Blocker/gate failure blocks. |
| `N-A` | Genuinely not applicable to profile, with reason and approval where required. | Never silent. |
| `Waived` | Time-bounded exception with owner, approver, rationale, compensating control, evidence, expiry. | Not a Pass. |
| `Not Run` / `Unknown` | No defensible result. | Incomplete, never Pass. |

N-A is not a convenience bypass. “Not enough time,” “not implemented,” or “hard on my laptop” is not a valid N-A reason. A waiver is not a pass. An expired waiver fails.

### 2.3 Level 1 — Beginner

At L1, read the item and explain what evidence would satisfy it.

**Good item:** “Has PostgreSQL backup been restored into an isolated target and has data integrity been checked?” Verify by restoring synthetic data, comparing row counts and deterministic invariants, and retaining backup ID, restore timestamps, tool versions, SQL output, commit SHA, and drill ID. A backup file alone does not pass.

**Defective item:** “Service is secure.” Rewrite it into separate falsifiable controls: least-privilege RBAC with unauthorized-action denial; no plaintext secrets with a synthetic canary scan; non-root workload with restricted capabilities; and network-policy negative test where supported.

**Illustrative decision:** a synthetic data-service candidate has a clean CI run, digest-pinned image, GitOps reconciliation, metrics, and a backup job record—but no restore. Delivery and observability items may pass individually; restore and integrity remain Not Run/Fail. The required recovery gate means No-Go for the integrated capstone pass rule. This is an example, not an actual test result.

### 2.4 Level 2 — Intermediate

Apply the checklist in this order:

1. Declare profile, scope, environment, commit SHA, artifact digest, and checklist version.
2. Read the pass condition before running a command.
3. Classify the item as automated, manual, or hybrid.
4. Run verification in the declared environment; explicitly select the lab Kubernetes context.
5. Retain command/query, exit status, timestamp, tool version, commit, run/drill ID, and digest where relevant.
6. Redact secrets/sensitive values without hiding failures.
7. Checksum evidence where appropriate; a checksum proves byte identity, not truth.
8. Record Pass/Fail/N-A/Waived and rationale. Missing output is not Pass.
9. Refresh after relevant code/configuration/deployment changes.
10. Run the validator and review every finding.

**Freshness:** `[ASSUMPTION]` 30 days is a configurable teaching example, not an industry standard. Evidence is stale if older than the configured age **or** predating the last relevant deployment/configuration change. The change condition invalidates even recent evidence.

**Evidence strength:** `Assertion < Screenshot < Command output < Automated test < Continuously run check`. This is a guide. Screenshots can orient a reviewer, but critical controls need automated positive/negative tests where practical. A restore command does not prove data integrity; a rule file does not prove alert routing; a Git revert does not prove runtime digest recovery.

- `automated`: deterministic test/validator.
- `manual`: human judgement; runner requires attestation.
- `hybrid`: automation plus human interpretation/approval.

### 2.5 Level 3 — Advanced

Every item must be measurable, bounded, independently understandable, falsifiable, owned, risk-linked, mapped to earlier modules, tied to fresh evidence, and paired with a negative/failure test where safe.

| Vague | Falsifiable rewrite |
|---|---|
| “Fast” | Record p50/p95/p99 and error rate for a declared synthetic load shape; compare with an explicitly assumed lab objective. |
| “Monitored” | Query the declared SLI, inspect dashboard identity/time range, trigger a benign condition, and retain the alert event and owner. |
| “Backups configured” | Restore a named backup into an isolated target, verify invariants, and compare measured RPO/RTO with declared lab targets. |
| “Highly available” | Test a stated disruption for the declared replica topology and verify user-visible behavior; state that single-node kind does not prove zone/region availability. |
| “Secure” | Split into identity, secret, network, hardening, and artifact-integrity controls. |

**Severity policy:** declare before scoring.
- **Blocker:** credential exposure, fabricated evidence, wrong/unsafe context, missing required restore/integrity or rollback, critical identity/security failure, or inability to identify deployed artifact. Blocks the relevant pass/launch decision.
- **Major:** material operational weakness requiring dated remediation or a no-go/conditional decision under declared policy.
- **Minor:** bounded low-risk gap with owner and disposition.

A score is supplementary. A blocker cannot be averaged away. A waiver needs item ID, owner, approver, rationale, impact, compensating control, evidence, creation/expiry, reassessment date, and closure condition. Non-waivable integrity/safety gates cannot be waived.

Version the checklist and item semantics. Retire obsolete controls through change control; do not silently delete them. `[ASSUMPTION]` use a 20% reviewer spot-check example, including every Blocker and at least one item per critical category. Record selection method, IDs, reviewer, rerun command, result, and discrepancy.

**N-A example:** TLS renewal can be N-A for an internal-only job with no TLS endpoint, supported by architecture evidence and reviewer approval.  
**Invalid N-A:** restore is N-A because laptop storage is inconvenient. It is required for the data-service profile.  
**Valid waiver:** a Minor documentation item has owner, approver, compensating control, evidence, expiry, and reassessment.  
**Invalid waiver:** no expiry; reject it. Required restore integrity is not waivable just to improve a score.

### 2.6 Level 4 — Expert

**ORR sequence**

1. Confirm scope, owner, profile, dependencies, environment, commit, artifact digest, and checklist version.
2. Confirm status, applicability, severity, gate, and waiver semantics.
3. Review Unit 1 evidence index and AC traceability.
4. Verify evidence freshness and identity correspondence.
5. Independently rerun a sample from a fresh checkout.
6. Review Blockers, Major findings, expired waivers, N-A reasons, and compensating controls.
7. Inspect incident, rollback, restore, alert, runbook, and teardown evidence.
8. Ask the owner to explain largest residual risks and what evidence would change the decision.
9. Record Go / Go with conditions / No-Go, rationale, owners, due dates, and scope.
10. Schedule a configurable post-launch review.
11. Preserve the decision record for audit.

**Suggested ORR agenda** ([ASSUMPTION] 45–60 minutes; adapt to scope):

| Timebox | Topic | Lead |
|---|---|---|
| 0–5 min | Scope, owner, profile, release identity | Service owner |
| 5–15 min | Requirements, checklist status, evidence index | Evidence recorder |
| 15–25 min | Identity, network, secrets, artifact chain | Security reviewer |
| 25–35 min | SLO, alerts, incident, rollback, restore | Operations/on-call representative |
| 35–45 min | Blockers, waivers, N-A, residual risk | Reviewer/approver |
| 45–60 min | Decision, conditions, owners, follow-up | Reviewer/approver |

**Roles:** service owner explains behavior and risks; reviewer/approver challenges evidence and decides; operations/on-call representative validates alerts/runbooks/recovery; security reviewer checks trust boundaries; evidence recorder checks provenance/freshness. A solo learner may role-play multiple roles but must disclose that this is not independent approval.

**Synthetic flawed-submission review — answer key**

| Defect | Risk | Evidence needed | Severity / decision |
|---|---|---|---|
| Backup exists, no restore | Recoverability unproven | Isolated restore, integrity, RPO/RTO | Blocker; No-Go |
| Alert rule exists, no test | Rule/route may not work | Rule test and benign end-to-end alert | Major/Blocker by policy; not Pass |
| Runbook points to deleted dashboard | Operator cannot inspect symptoms | Correct working dashboard/query and walkthrough | Major; conditional only if policy allows |
| Evidence predates config change | Stale evidence | Rerun against new revision | Major/Blocker if gate; not Pass |
| Waiver has no expiry | Permanent uncontrolled exception | Complete time-bounded waiver | Reject waiver |
| Pass but evidence path missing | Assertion only | Valid indexed artifact or rerun | Blocker for gate; otherwise Major |
| N-A without reason | Applicability bypass | Profile reason and approval | Reject N-A |
| “Secure” without condition | Untestable | Split into measurable controls | Return for rewrite |
| Runner auto-passes human judgement | False approval | Reviewer attestation | Blocker |
| Teardown claimed, resources remain | Residual cost/security risk | Before/after inventory and cleanup proof | Blocker; No-Go |

**Calibration:** two reviewers disagree whether a dashboard passes. One says it opens; the other says workload query is empty. Return to the pass condition: reachability alone is insufficient if the item requires useful workload symptom signals. Record initial opinions, exact evidence, final status, rationale, and remediation owner. Do not average opinions or defer to seniority.

### 2.7 SRE lens

An **SLI** measures user-relevant behavior; an **SLO** sets a target over a window; an **error budget** expresses allowed bad events; criticality expresses failure consequence. A CronJob starting on time is not enough if its output is late or wrong. An inference Pod being Ready is not enough if requests fail or predictions are invalid. Do not prescribe universal SLO, alert, RPO/RTO, or resource values. Select targets from user impact, label assumptions, and record why.

Distinguish symptom signals (request errors, latency, data freshness) from cause signals (CPU throttling, OOM, dependency timeouts, queue depth). Correlate by timestamp, workload identity, deployment revision, and run/drill ID. Alerts must be actionable, owned, routed, tested, and linked to a runbook. A rule definition is not an alert test.

Choose graceful degradation or fail-closed behavior for each dependency. Bound retries/timeouts. For scheduled data jobs, safe replay and idempotency matter more than merely restarting a Pod.

Recovery readiness requires backup identity, actual isolated restore, integrity verification, declared RPO/RTO and measured lab actuals, Git-controlled rollback, and safe replay/backfill. A runbook includes trigger, impact, prerequisites, safe diagnostics, decisions, rollback/recovery, verification, escalation, and evidence capture.

Capacity/cost review includes requests/limits, saturation, restarts/OOM, bounded load shape, quotas, labels, and teardown. Never extrapolate laptop kind results to production.

**Illustrative safe read-only runbook snippet:**

```bash
kubectl --context kind-m17-lab cluster-info >/dev/null
kubectl --context kind-m17-lab get pods -n m17-app -o wide
kubectl --context kind-m17-lab get events -n m17-app --sort-by=.metadata.creationTimestamp
kubectl --context kind-m17-lab get deployment -n m17-app
```

These commands inspect the lab; they do not prove user behavior, identify root cause alone, or authorize remediation. Preserve output before mutation.

### 2.8 Security lens

```text
Developer workstation -> source repository -> CI identity -> artifact registry
 -> GitOps repository -> Argo CD -> Kubernetes API/workload
 -> observability/evidence store -> backup target
```

At every boundary ask who can read/write, which identity is used, how it is scoped, what is logged, and what negative test proves the restriction.

Use least privilege, dedicated workload identities, narrow RBAC, scoped CI permissions, and separation of duties where feasible. Test allowed and unauthorized actions. Use secret references; never commit credentials, tokens, private keys, credential-bearing kubeconfigs, environment dumps, production exports, or unredacted logs. Use synthetic canaries only.

Prefer non-root workloads, restricted capabilities, read-only filesystems where feasible, and narrow writable paths. Pin artifact digests. Retain artifact scan results without claiming scans guarantee zero vulnerabilities. Signing/provenance (cosign) is optional Cap+Security/Awareness. Treat model artifacts as artifacts: record hash/digest and model/code pairing.

Where supported by the selected CNI, NetworkPolicy must be paired with a denied-path test. If local enforcement is unsupported, state the limitation; a YAML object alone is not proof. Pin third-party CI actions under the project's verified policy; exact SHA syntax and branch rules are `[VERIFY]`. Local CI emulation is not identical to hosted-runner identity or permissions.

All fault injection is own-lab only. Every Kubernetes command in this unit explicitly selects `--context kind-m17-lab`. Verify context, namespace, workload ownership, and cleanup boundary before mutation; dry-run/read-only inspection first. Stop if target is uncertain.

### 2.9 Complete production readiness checklist

The checklist has 75 distinct items in 15 categories. Each item has a stable ID, precise control, risk, verification, evidence reference, owner, applicability, severity/gate, status, freshness policy, M01–M16 mapping, Unit 1 REQ/AC mapping, automation class, and pass condition.

**Profiles:** `data_service` (stateful service); `scheduled_pipeline` (CronJob); `ml_inference` (toy/synthetic inference, no real dataset/GPU); `integrated_capstone` (full M17 flow). `required` means applies by default; `conditional` requires checking a trigger; `na_allowed` requires a profile-specific reason and reviewer approval. Do not force irrelevant controls onto every workload.

### 2.9.1 Checklist records

#### PR-001 — Is profile, user outcome, environment, owner, and non-goals recorded?

- **Category:** Service scope, ownership, architecture, and dependencies
- **Risk:** Unowned services or hidden dependencies create failure paths with no accountable operator or recovery boundary.
- **Verification:** Review scope record against deployed services and selected profile.
- **Evidence:** `evidence/readiness/PR-001/scope.md`.
- **Owner:** Service owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10, M16.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Scope, owner, environment, boundaries, and non-goals are explicit.

#### PR-002 — Is an accountable service owner and support/escalation contact named?

- **Category:** Service scope, ownership, architecture, and dependencies
- **Risk:** Unowned services or hidden dependencies create failure paths with no accountable operator or recovery boundary.
- **Verification:** Review ownership register and conduct owner walkthrough.
- **Evidence:** `evidence/readiness/PR-002/owner.md`.
- **Owner:** Service owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10, M16.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Owner, backup/solo role, and support boundary are recorded.

#### PR-003 — Are runtime, data, CI, registry, GitOps, identity, and observability dependencies inventoried?

- **Category:** Service scope, ownership, architecture, and dependencies
- **Risk:** Unowned services or hidden dependencies create failure paths with no accountable operator or recovery boundary.
- **Verification:** Compare dependency inventory with architecture and configuration.
- **Evidence:** `evidence/readiness/PR-003/dependencies.md`.
- **Owner:** Service owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M04, M05, M08, M09, M11.
- **Unit 1 mapping:** REQ-032; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Each material dependency has owner, purpose, failure impact, and evidence source.

#### PR-004 — Does the architecture show components, data flows, and trust boundaries?

- **Category:** Service scope, ownership, architecture, and dependencies
- **Risk:** Unowned services or hidden dependencies create failure paths with no accountable operator or recovery boundary.
- **Verification:** Review diagram against manifests and running lab.
- **Evidence:** `evidence/readiness/PR-004/architecture.md`.
- **Owner:** Platform reviewer
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M04, M07, M08, M09, M12, M16.
- **Unit 1 mapping:** REQ-032; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Diagram is current, scoped, and independently understandable.

#### PR-005 — Are criticality and user-visible failure modes described?

- **Category:** Service scope, ownership, architecture, and dependencies
- **Risk:** Unowned services or hidden dependencies create failure paths with no accountable operator or recovery boundary.
- **Verification:** Review criticality record and failure-mode map.
- **Evidence:** `evidence/readiness/PR-005/criticality.md`.
- **Owner:** Service owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10, M15.
- **Unit 1 mapping:** REQ-032; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** User impact, interruption tolerance, and residual risks are explicit.

#### PR-006 — Do required CI build, test, and security checks run before promotion?

- **Category:** Delivery pipeline and artifact integrity
- **Risk:** A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.
- **Verification:** Inspect workflow and run record for exact source commit.
- **Evidence:** `evidence/readiness/PR-006/ci.json`.
- **Owner:** CI owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M01, M02, M12.
- **Unit 1 mapping:** REQ-001, REQ-003; AC-001. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Required jobs executed successfully for the candidate commit.

#### PR-007 — Does a failing test or scan block promotion?

- **Category:** Delivery pipeline and artifact integrity
- **Risk:** A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.
- **Verification:** Plant a synthetic failing test in a disposable branch and inspect gate behavior.
- **Evidence:** `evidence/readiness/PR-007/negative-gate.json`.
- **Owner:** CI owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M02, M12.
- **Unit 1 mapping:** REQ-003, REQ-027; AC-001. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Failing required check prevents promotion.

#### PR-008 — Is the deployed artifact pinned by immutable digest/hash?

- **Category:** Delivery pipeline and artifact integrity
- **Risk:** A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.
- **Verification:** Compare registry, GitOps, and runtime identity.
- **Evidence:** `evidence/readiness/PR-008/digest.json`.
- **Owner:** Release owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M01, M02, M12.
- **Unit 1 mapping:** REQ-002, REQ-030; AC-001, AC-010. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Full digest/hash matches tested, promoted, declared, and deployed artifact.

#### PR-009 — Is signing/provenance assessed and its adoption boundary documented?

- **Category:** Delivery pipeline and artifact integrity
- **Risk:** A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.
- **Verification:** Verify selected tool if Cap+Security; otherwise record Awareness decision.
- **Evidence:** `evidence/readiness/PR-009/provenance.md`.
- **Owner:** Security reviewer
- **Applicability:** data_service: conditional; scheduled_pipeline: conditional; ml_inference: conditional; integrated_capstone: conditional. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Minor / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M01, M12.
- **Unit 1 mapping:** REQ-002, REQ-032; AC-010. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Evidence or a reasoned optional/not-selected decision is recorded.

#### PR-010 — Is the same immutable artifact promoted without rebuilding?

- **Category:** Delivery pipeline and artifact integrity
- **Risk:** A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.
- **Verification:** Compare source commit, build run, digest, and manifests.
- **Evidence:** `evidence/readiness/PR-010/promotion.json`.
- **Owner:** Release owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M01, M02, M08.
- **Unit 1 mapping:** REQ-001, REQ-002, REQ-030; AC-001, AC-010. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** All stages refer to one tested build identity and digest.

#### PR-011 — Are protected-branch and required-check controls configured?

- **Category:** Delivery pipeline and artifact integrity
- **Risk:** A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.
- **Verification:** Review repository rules and a safe negative test.
- **Evidence:** `evidence/readiness/PR-011/branch-rules.md`.
- **Owner:** Repository owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M02, M12.
- **Unit 1 mapping:** REQ-003, REQ-032; AC-001. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Required checks and review policy are recorded with local-emulation limits.

#### PR-012 — Can a clean checkout reproduce build inputs and identify tool versions?

- **Category:** Delivery pipeline and artifact integrity
- **Risk:** A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.
- **Verification:** Build from a fresh clone and compare versions and digest.
- **Evidence:** `evidence/readiness/PR-012/build.md`.
- **Owner:** CI owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M01, M02, M06, M07.
- **Unit 1 mapping:** REQ-021, REQ-030; AC-012. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Inputs, versions, SHA, and output digest are retained.

#### PR-013 — Do rendered manifests/charts validate against selected tool versions?

- **Category:** Kubernetes workload configuration and packaging
- **Risk:** Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.
- **Verification:** Run selected Helm/Kustomize render and validators.
- **Evidence:** `evidence/readiness/PR-013/validation.txt`.
- **Owner:** Platform owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M06, M07.
- **Unit 1 mapping:** REQ-028; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Rendered resources pass validators and are tied to a commit/version.

#### PR-014 — Are CPU/memory requests and limits justified by bounded lab observations?

- **Category:** Kubernetes workload configuration and packaging
- **Risk:** Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.
- **Verification:** Inspect workload specs and compare with synthetic test and restart/OOM behavior.
- **Evidence:** `evidence/readiness/PR-014/resources.md`.
- **Owner:** Workload owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10, M15.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Resource settings have rationale and measured lab evidence.

#### PR-015 — Does the workload run non-root with restricted privilege/capabilities where feasible?

- **Category:** Kubernetes workload configuration and packaging
- **Risk:** Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.
- **Verification:** Inspect Pod security context and runtime identity.
- **Evidence:** `evidence/readiness/PR-015/hardening.md`.
- **Owner:** Security reviewer
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M12.
- **Unit 1 mapping:** REQ-009; AC-003. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** No unexplained root, privileged mode, or excess capability remains.

#### PR-016 — Are startup/readiness/liveness probes appropriate and tested?

- **Category:** Kubernetes workload configuration and packaging
- **Risk:** Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.
- **Verification:** Exercise slow-start, not-ready, and unhealthy synthetic states.
- **Evidence:** `evidence/readiness/PR-016/probes.json`.
- **Owner:** Workload owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Probe semantics and expected transitions are tested.

#### PR-017 — Does the service handle graceful shutdown within its declared budget?

- **Category:** Kubernetes workload configuration and packaging
- **Risk:** Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.
- **Verification:** Run bounded termination test and inspect application behavior.
- **Evidence:** `evidence/readiness/PR-017/shutdown.md`.
- **Owner:** Workload owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Shutdown behavior, timeout assumptions, and limitations are verified.

#### PR-018 — Is disruption behavior considered for replicas and disruption controls?

- **Category:** Kubernetes workload configuration and packaging
- **Risk:** Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.
- **Verification:** Review replica/disruption settings and safe lab test.
- **Evidence:** `evidence/readiness/PR-018/disruption.md`.
- **Owner:** Platform owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Disruption expectations are tested; single-node kind is not called HA.

#### PR-019 — Are persistent volumes and stateful lifecycle controls documented?

- **Category:** Kubernetes workload configuration and packaging
- **Risk:** Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.
- **Verification:** Inspect PVC/PV and verify persistence across controlled restart.
- **Evidence:** `evidence/readiness/PR-019/storage.md`.
- **Owner:** Data owner
- **Applicability:** data_service: required; scheduled_pipeline: conditional; ml_inference: na_allowed; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M05, M07, M13.
- **Unit 1 mapping:** REQ-017, REQ-018; AC-008. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Persistence and storage assumptions are verified separately from restore.

#### PR-020 — Are runtime configuration changes traceable to reviewed desired-state revisions?

- **Category:** Kubernetes workload configuration and packaging
- **Risk:** Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.
- **Verification:** Compare config source, Git revision, rendered manifest, and runtime revision.
- **Evidence:** `evidence/readiness/PR-020/config.md`.
- **Owner:** Platform owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M06, M08.
- **Unit 1 mapping:** REQ-004, REQ-005; AC-002. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Configuration source and runtime state map to a specific Git revision.

#### PR-021 — Are service exposure, ingress, DNS, and TLS requirements declared?

- **Category:** Networking, ingress, DNS, and TLS
- **Risk:** Unintended reachability, broken routing, or weak transport trust can expose services or interrupt required dependencies.
- **Verification:** Review service/ingress objects and architecture for selected profile.
- **Evidence:** `evidence/readiness/PR-021/exposure.md`.
- **Owner:** Network owner
- **Applicability:** data_service: conditional; scheduled_pipeline: conditional; ml_inference: conditional; integrated_capstone: conditional. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M04.
- **Unit 1 mapping:** REQ-010; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Exposed paths and TLS/DNS assumptions are identified; internal-only stays internal.

#### PR-022 — Where supported, does NetworkPolicy restrict traffic to declared dependencies?

- **Category:** Networking, ingress, DNS, and TLS
- **Risk:** Unintended reachability, broken routing, or weak transport trust can expose services or interrupt required dependencies.
- **Verification:** Inspect policy; test allowed and deliberately denied paths.
- **Evidence:** `evidence/readiness/PR-022/network-policy.json`.
- **Owner:** Network owner
- **Applicability:** data_service: conditional; scheduled_pipeline: conditional; ml_inference: conditional; integrated_capstone: conditional. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M04, M12.
- **Unit 1 mapping:** REQ-010, REQ-027; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Allowed path succeeds and undeclared path is denied, or enforcement limit is stated.

#### PR-023 — Are outbound dependencies and egress paths limited or justified?

- **Category:** Networking, ingress, DNS, and TLS
- **Risk:** Unintended reachability, broken routing, or weak transport trust can expose services or interrupt required dependencies.
- **Verification:** Review dependency list and safe synthetic connectivity tests.
- **Evidence:** `evidence/readiness/PR-023/egress.md`.
- **Owner:** Network owner
- **Applicability:** data_service: conditional; scheduled_pipeline: conditional; ml_inference: conditional; integrated_capstone: conditional. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M04, M12.
- **Unit 1 mapping:** REQ-010; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Outbound paths have purpose and owner; broad unknown egress is a finding.

#### PR-024 — Where TLS is used, are certificate trust, expiry, and renewal ownership documented?

- **Category:** Networking, ingress, DNS, and TLS
- **Risk:** Unintended reachability, broken routing, or weak transport trust can expose services or interrupt required dependencies.
- **Verification:** Inspect certificate metadata and renewal runbook without exposing keys.
- **Evidence:** `evidence/readiness/PR-024/tls.md`.
- **Owner:** Security reviewer
- **Applicability:** data_service: conditional; scheduled_pipeline: conditional; ml_inference: conditional; integrated_capstone: conditional. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M04, M09.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Trust and renewal responsibilities are clear; private keys are excluded.

#### PR-025 — Does each workload use a dedicated service account or documented identity boundary?

- **Category:** Identity, RBAC, workload identity, and secrets
- **Risk:** Excess privilege or leaked credentials can enable unauthorized actions and expand blast radius.
- **Verification:** Inspect service-account bindings against identity map.
- **Evidence:** `evidence/readiness/PR-025/identity.md`.
- **Owner:** Identity owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M09.
- **Unit 1 mapping:** REQ-006; AC-003. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Workload identities are explicit and not unnecessarily privileged/shared.

#### PR-026 — Are RBAC permissions least-privilege and unauthorized actions denied?

- **Category:** Identity, RBAC, workload identity, and secrets
- **Risk:** Excess privilege or leaked credentials can enable unauthorized actions and expand blast radius.
- **Verification:** Review role bindings and run allowed/denied authorization tests.
- **Evidence:** `evidence/readiness/PR-026/rbac.txt`.
- **Owner:** Identity owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M09, M12.
- **Unit 1 mapping:** REQ-006, REQ-027; AC-003. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Required action succeeds and prohibited action is denied.

#### PR-027 — Are secrets referenced securely and excluded from Git, images, logs, and evidence?

- **Category:** Identity, RBAC, workload identity, and secrets
- **Risk:** Excess privilege or leaked credentials can enable unauthorized actions and expand blast radius.
- **Verification:** Inspect references and scan source/artifacts/log fixtures.
- **Evidence:** `evidence/readiness/PR-027/secrets.md`.
- **Owner:** Security reviewer
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M09, M12.
- **Unit 1 mapping:** REQ-007, REQ-008; AC-004. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** No plaintext secret remains; access/reference boundary is documented.

#### PR-028 — Does secret scanning detect a synthetic canary?

- **Category:** Identity, RBAC, workload identity, and secrets
- **Risk:** Excess privilege or leaked credentials can enable unauthorized actions and expand blast radius.
- **Verification:** Run clean baseline and planted dummy-secret negative test.
- **Evidence:** `evidence/readiness/PR-028/secret-scan.json`.
- **Owner:** Security reviewer
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M09, M12.
- **Unit 1 mapping:** REQ-008, REQ-027; AC-004. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Canary is detected; no real credential is used.

#### PR-029 — Was an artifact scan executed for the exact candidate and result retained?

- **Category:** Security controls and software supply chain
- **Risk:** Unreviewed or tampered artifacts and missing enforcement can introduce preventable runtime risk.
- **Verification:** Inspect scan run, digest, scanner version, policy, and disposition.
- **Evidence:** `evidence/readiness/PR-029/scan.json`.
- **Owner:** Security reviewer
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M01, M12.
- **Unit 1 mapping:** REQ-003; AC-001. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Scan matches candidate; no claim of zero vulnerabilities is made.

#### PR-030 — Is provenance/signature verification performed where selected?

- **Category:** Security controls and software supply chain
- **Risk:** Unreviewed or tampered artifacts and missing enforcement can introduce preventable runtime risk.
- **Verification:** Verify selected Cap+Security trust policy or record optional decision.
- **Evidence:** `evidence/readiness/PR-030/provenance.md`.
- **Owner:** Security reviewer
- **Applicability:** data_service: conditional; scheduled_pipeline: conditional; ml_inference: conditional; integrated_capstone: conditional. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Minor / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M01, M12.
- **Unit 1 mapping:** REQ-002, REQ-030; AC-010. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Trust boundary and verification result or optionality are recorded.

#### PR-031 — Are selected admission/policy controls tested with a denied fixture?

- **Category:** Security controls and software supply chain
- **Risk:** Unreviewed or tampered artifacts and missing enforcement can introduce preventable runtime risk.
- **Verification:** Run policy validation and synthetic denied-manifest test.
- **Evidence:** `evidence/readiness/PR-031/policy.md`.
- **Owner:** Security reviewer
- **Applicability:** data_service: conditional; scheduled_pipeline: conditional; ml_inference: conditional; integrated_capstone: conditional. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Minor / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M12.
- **Unit 1 mapping:** REQ-009, REQ-027; AC-003. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Compliant fixture passes and planted non-compliant fixture is rejected.

#### PR-032 — Are filesystem permissions, capabilities, and writable paths restricted?

- **Category:** Security controls and software supply chain
- **Risk:** Unreviewed or tampered artifacts and missing enforcement can introduce preventable runtime risk.
- **Verification:** Inspect security context and test intended writable paths.
- **Evidence:** `evidence/readiness/PR-032/filesystem.md`.
- **Owner:** Security reviewer
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M12.
- **Unit 1 mapping:** REQ-009; AC-003. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Privilege and write access are minimized or justified.

#### PR-033 — Is base-image/dependency maintenance owned and documented?

- **Category:** Security controls and software supply chain
- **Risk:** Unreviewed or tampered artifacts and missing enforcement can introduce preventable runtime risk.
- **Verification:** Review base image, dependency update process, owner, and review date.
- **Evidence:** `evidence/readiness/PR-033/maintenance.md`.
- **Owner:** Workload owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Minor / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M01, M12.
- **Unit 1 mapping:** REQ-003, REQ-032; AC-001. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** A repeatable update/rebuild path and owner are documented.

#### PR-034 — Can artifact identity be independently verified beyond a mutable tag?

- **Category:** Security controls and software supply chain
- **Risk:** Unreviewed or tampered artifacts and missing enforcement can introduce preventable runtime risk.
- **Verification:** Recompute/inspect digest and compare build/deployment evidence.
- **Evidence:** `evidence/readiness/PR-034/identity.txt`.
- **Owner:** Release owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M01, M12.
- **Unit 1 mapping:** REQ-002, REQ-030; AC-001, AC-010. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Independent digest comparison matches recorded immutable artifact.

#### PR-035 — Do health checks represent startup, readiness, and process health correctly?

- **Category:** Reliability, health checks, graceful shutdown, and disruption behavior
- **Risk:** Misleading health checks, unbounded retries, and unsafe failure behavior can amplify an incident or duplicate work.
- **Verification:** Run positive/negative probe scenarios and inspect transitions.
- **Evidence:** `evidence/readiness/PR-035/health.md`.
- **Owner:** Workload owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Each health signal has defined semantics and unhealthy test.

#### PR-036 — Is dependency failure behavior explicitly graceful-degrade or fail-closed?

- **Category:** Reliability, health checks, graceful shutdown, and disruption behavior
- **Risk:** Misleading health checks, unbounded retries, and unsafe failure behavior can amplify an incident or duplicate work.
- **Verification:** Review failure-mode table and execute bounded synthetic dependency failure.
- **Evidence:** `evidence/readiness/PR-036/dependency.md`.
- **Owner:** Service owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10.
- **Unit 1 mapping:** REQ-015; AC-006. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Chosen behavior, impact, and safe recovery action are evidenced.

#### PR-037 — Are retries bounded, backoff-aware, and safe against duplicate side effects?

- **Category:** Reliability, health checks, graceful shutdown, and disruption behavior
- **Risk:** Misleading health checks, unbounded retries, and unsafe failure behavior can amplify an incident or duplicate work.
- **Verification:** Inspect retry settings and run transient-failure test with output invariants.
- **Evidence:** `evidence/readiness/PR-037/retry.md`.
- **Owner:** Pipeline owner
- **Applicability:** data_service: conditional; scheduled_pipeline: required; ml_inference: conditional; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10.
- **Unit 1 mapping:** REQ-019, REQ-027; AC-009. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Retries are bounded and repeated execution preserves output invariants.

#### PR-038 — Is concurrent scheduled-job execution prevented or made safe?

- **Category:** Reliability, health checks, graceful shutdown, and disruption behavior
- **Risk:** Misleading health checks, unbounded retries, and unsafe failure behavior can amplify an incident or duplicate work.
- **Verification:** Inspect concurrency policy/lock and run controlled overlap test.
- **Evidence:** `evidence/readiness/PR-038/concurrency.md`.
- **Owner:** Pipeline owner
- **Applicability:** data_service: conditional; scheduled_pipeline: required; ml_inference: conditional; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M05, M10.
- **Unit 1 mapping:** REQ-019; AC-009. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Overlapping runs are prevented or safe by a tested invariant.

#### PR-039 — Are deadlines, timeouts, and retry limits bounded and justified?

- **Category:** Reliability, health checks, graceful shutdown, and disruption behavior
- **Risk:** Misleading health checks, unbounded retries, and unsafe failure behavior can amplify an incident or duplicate work.
- **Verification:** Review config and execute synthetic slow-dependency test.
- **Evidence:** `evidence/readiness/PR-039/timeouts.md`.
- **Owner:** Workload owner
- **Applicability:** data_service: conditional; scheduled_pipeline: required; ml_inference: conditional; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10.
- **Unit 1 mapping:** REQ-019; AC-009. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Timeouts bound resource use and have a failure response.

#### PR-040 — Are critical dependency failures, blast radius, and recovery actions documented?

- **Category:** Reliability, health checks, graceful shutdown, and disruption behavior
- **Risk:** Misleading health checks, unbounded retries, and unsafe failure behavior can amplify an incident or duplicate work.
- **Verification:** Review dependency matrix and safe runbook walkthrough.
- **Evidence:** `evidence/readiness/PR-040/failures.md`.
- **Owner:** Service owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10, M13.
- **Unit 1 mapping:** REQ-015; AC-006. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Failure modes are prioritized, owned, and linked to diagnostics/recovery.

#### PR-041 — Are workload metrics collected with stable workload identity and timestamps?

- **Category:** Observability: metrics, logs, dashboards, traces, alerts
- **Risk:** Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.
- **Verification:** Inspect Prometheus targets and query expected synthetic series.
- **Evidence:** `evidence/readiness/PR-041/metrics.txt`.
- **Owner:** Observability owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M10, M11.
- **Unit 1 mapping:** REQ-011; AC-005. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Expected metrics are present, queryable, and attributable.

#### PR-042 — Are logs structured enough to correlate time, workload, and run/drill identity?

- **Category:** Observability: metrics, logs, dashboards, traces, alerts
- **Risk:** Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.
- **Verification:** Inspect synthetic log records and redaction.
- **Evidence:** `evidence/readiness/PR-042/logs.md`.
- **Owner:** Observability owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M11, M12.
- **Unit 1 mapping:** REQ-012; AC-005. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Logs support correlation without leaking secrets/sensitive data.

#### PR-043 — Does the dashboard identify workload and show symptom-oriented health signals?

- **Category:** Observability: metrics, logs, dashboards, traces, alerts
- **Risk:** Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.
- **Verification:** Inspect queries, labels, time range, and runbook links.
- **Evidence:** `evidence/readiness/PR-043/dashboard.md`.
- **Owner:** Observability owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M10, M11.
- **Unit 1 mapping:** REQ-013; AC-005. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Dashboard is reachable, correctly scoped, useful, and linked.

#### PR-044 — Are Prometheus rules tested with promtool when Prometheus rules are used?

- **Category:** Observability: metrics, logs, dashboards, traces, alerts
- **Risk:** Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.
- **Verification:** Run installed promtool tests against committed rule files.
- **Evidence:** `evidence/readiness/PR-044/promtool.txt`.
- **Owner:** Observability owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M10, M11.
- **Unit 1 mapping:** REQ-014, REQ-027; AC-005. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Rule tests pass for installed version; syntax is verified.

#### PR-045 — Has one alert path been safely exercised from signal through alert event/owner?

- **Category:** Observability: metrics, logs, dashboards, traces, alerts
- **Risk:** Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.
- **Verification:** Trigger benign lab condition and retain signal, rule, route, event, and timestamp.
- **Evidence:** `evidence/readiness/PR-045/alert.md`.
- **Owner:** Observability owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M10, M11.
- **Unit 1 mapping:** REQ-014; AC-005. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** A lab alert event is observed and owned; rule file alone is insufficient.

#### PR-046 — If tracing is used, are trace context and sampling/retention documented?

- **Category:** Observability: metrics, logs, dashboards, traces, alerts
- **Risk:** Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.
- **Verification:** Review synthetic trace and trace/log correlation.
- **Evidence:** `evidence/readiness/PR-046/tracing.md`.
- **Owner:** Observability owner
- **Applicability:** data_service: conditional; scheduled_pipeline: conditional; ml_inference: conditional; integrated_capstone: conditional. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Minor / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M11.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Tracing is scoped correctly or N-A is justified.

#### PR-047 — Can telemetry be correlated with Git revision, artifact, deployment, and drill time?

- **Category:** Observability: metrics, logs, dashboards, traces, alerts
- **Risk:** Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.
- **Verification:** Compare timestamps and identities across CI, GitOps, runtime, metrics, and logs.
- **Evidence:** `evidence/readiness/PR-047/correlation.md`.
- **Owner:** Observability owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M02, M08, M10, M11.
- **Unit 1 mapping:** REQ-011, REQ-012, REQ-023; AC-005. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Timeline is reconstructable with timezone and uncertainty.

#### PR-048 — Is each SLO based on user-visible SLI, numerator/denominator, window, target, and exclusions?

- **Category:** SLOs, error budgets, and operational risk
- **Risk:** Targets disconnected from user outcomes can hide meaningful degradation and leave risk decisions implicit.
- **Verification:** Review SLO and reproduce query/calculation on synthetic events.
- **Evidence:** `evidence/readiness/PR-048/slo.md`.
- **Owner:** SRE reviewer
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M10, M11.
- **Unit 1 mapping:** REQ-011, REQ-014, REQ-019; AC-005, AC-009. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** SLI reflects user outcome; missing data/exclusions are explicit.

#### PR-049 — Is an error-budget policy defined where an SLO is meaningful?

- **Category:** SLOs, error budgets, and operational risk
- **Risk:** Targets disconnected from user outcomes can hide meaningful degradation and leave risk decisions implicit.
- **Verification:** Review calculation, response policy, owner, and scenario.
- **Evidence:** `evidence/readiness/PR-049/budget.md`.
- **Owner:** SRE reviewer
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Minor / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M10.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Budget math and response are reproducible; assumptions are labelled.

#### PR-050 — Are material operational risks, assumptions, and residual risks owned?

- **Category:** SLOs, error budgets, and operational risk
- **Risk:** Targets disconnected from user outcomes can hide meaningful degradation and leave risk decisions implicit.
- **Verification:** Inspect risk register, ADRs, status, owner, and review date.
- **Evidence:** `evidence/readiness/PR-050/risks.md`.
- **Owner:** Service owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M10, M15, M16.
- **Unit 1 mapping:** REQ-032; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Material risks are visible and not hidden by score.

#### PR-051 — Does the stateful service have a documented backup and isolated backup target?

- **Category:** Data protection, backup, restore, integrity, RPO, and RTO
- **Risk:** Data may be unrecoverable, incomplete, or silently corrupted despite a successful backup job.
- **Verification:** Inspect backup config and artifact metadata without credentials.
- **Evidence:** `evidence/readiness/PR-051/backup.md`.
- **Owner:** Data owner
- **Applicability:** data_service: required; scheduled_pipeline: conditional; ml_inference: na_allowed; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M05, M13.
- **Unit 1 mapping:** REQ-017; AC-008. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Backup identity and separation from active data are recorded.

#### PR-052 — Has backup actually been restored into an isolated target?

- **Category:** Data protection, backup, restore, integrity, RPO, and RTO
- **Risk:** Data may be unrecoverable, incomplete, or silently corrupted despite a successful backup job.
- **Verification:** Execute restore drill on synthetic data and retain timings/logs.
- **Evidence:** `evidence/readiness/PR-052/restore.md`.
- **Owner:** Data owner
- **Applicability:** data_service: required; scheduled_pipeline: conditional; ml_inference: na_allowed; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M05, M13.
- **Unit 1 mapping:** REQ-017; AC-008. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Isolated restore completed; backup existence alone does not pass.

#### PR-053 — Has restored data integrity been verified by row counts/checksums/invariants?

- **Category:** Data protection, backup, restore, integrity, RPO, and RTO
- **Risk:** Data may be unrecoverable, incomplete, or silently corrupted despite a successful backup job.
- **Verification:** Run documented integrity checks against source baseline and restored target.
- **Evidence:** `evidence/readiness/PR-053/integrity.md`.
- **Owner:** Data owner
- **Applicability:** data_service: required; scheduled_pipeline: conditional; ml_inference: na_allowed; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M05, M10, M13.
- **Unit 1 mapping:** REQ-018; AC-008. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Integrity invariants match and are tied to restored backup identity.

#### PR-054 — Are RPO/RTO targets declared and actual lab measurements recorded?

- **Category:** Data protection, backup, restore, integrity, RPO, and RTO
- **Risk:** Data may be unrecoverable, incomplete, or silently corrupted despite a successful backup job.
- **Verification:** Review target and timed backup/restore evidence; recalculate durations.
- **Evidence:** `evidence/readiness/PR-054/rpo-rto.md`.
- **Owner:** SRE reviewer
- **Applicability:** data_service: required; scheduled_pipeline: conditional; ml_inference: na_allowed; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M10, M13.
- **Unit 1 mapping:** REQ-018; AC-008. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Targets, boundaries, actuals, and deviations are recorded as lab values.

#### PR-055 — Has a bounded synthetic load test been run for declared lab objective?

- **Category:** Capacity, performance, resource requests/limits, quotas, and cost
- **Risk:** Saturation, OOM behavior, or unbounded resources can degrade service or create avoidable cost.
- **Verification:** Run documented synthetic profile and retain parameters/results/environment limits.
- **Evidence:** `evidence/readiness/PR-055/load.md`.
- **Owner:** Workload owner
- **Applicability:** data_service: conditional; scheduled_pipeline: conditional; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10, M15.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Test scope and limits are recorded; no production extrapolation.

#### PR-056 — Are resource requests/limits, saturation signals, and OOM/restarts reviewed together?

- **Category:** Capacity, performance, resource requests/limits, quotas, and cost
- **Risk:** Saturation, OOM behavior, or unbounded resources can degrade service or create avoidable cost.
- **Verification:** Compare resource settings, synthetic load, metrics, and events.
- **Evidence:** `evidence/readiness/PR-056/capacity.md`.
- **Owner:** Platform owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10, M15.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Capacity decisions have evidence and explicit uncertainty.

#### PR-057 — Are namespace quotas/limits configured where appropriate?

- **Category:** Capacity, performance, resource requests/limits, quotas, and cost
- **Risk:** Saturation, OOM behavior, or unbounded resources can degrade service or create avoidable cost.
- **Verification:** Inspect quota objects and test expected enforcement safely.
- **Evidence:** `evidence/readiness/PR-057/quotas.md`.
- **Owner:** Platform owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Minor / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M07, M15.
- **Unit 1 mapping:** no direct Unit 1 REQ; retain the M01–M16 control mapping; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Quota boundaries are documented/enforced where supported.

#### PR-058 — Are resource/cost labels and cleanup ownership defined?

- **Category:** Capacity, performance, resource requests/limits, quotas, and cost
- **Risk:** Saturation, OOM behavior, or unbounded resources can degrade service or create avoidable cost.
- **Verification:** Inspect labels and compare resource inventory with teardown list.
- **Evidence:** `evidence/readiness/PR-058/labels.md`.
- **Owner:** Platform owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Minor / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M07, M15, M16.
- **Unit 1 mapping:** REQ-020; AC-011. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Lab resources are attributable and have an owner/cleanup record.

#### PR-059 — Does each critical runbook include trigger, impact, prerequisites, diagnostics, decisions, recovery, verification, escalation, evidence?

- **Category:** Operations, on-call, incident response, runbooks, and support
- **Risk:** Operators may respond late or unsafely when ownership, diagnostics, escalation, and recovery steps are unclear.
- **Verification:** Review runbook and conduct tabletop walkthrough.
- **Evidence:** `evidence/readiness/PR-059/runbook.md`.
- **Owner:** Operations owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10, M11, M13.
- **Unit 1 mapping:** REQ-015; AC-006. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Runbook is safe, scoped, ordered, and usable by another operator.

#### PR-060 — Are support boundaries, escalation, and communication expectations explicit?

- **Category:** Operations, on-call, incident response, runbooks, and support
- **Risk:** Operators may respond late or unsafely when ownership, diagnostics, escalation, and recovery steps are unclear.
- **Verification:** Review support record and owner walkthrough.
- **Evidence:** `evidence/readiness/PR-060/support.md`.
- **Owner:** Operations owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10.
- **Unit 1 mapping:** REQ-032; no direct Unit 1 AC assigned. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Responsibility, escalation, and solo role-play limits are explicit.

#### PR-061 — Is a controlled failure investigated using symptom, scope, change, hypothesis, test, result, next action?

- **Category:** Operations, on-call, incident response, runbooks, and support
- **Risk:** Operators may respond late or unsafely when ownership, diagnostics, escalation, and recovery steps are unclear.
- **Verification:** Review incident report and evidence captured before remediation.
- **Evidence:** `evidence/readiness/PR-061/incident.md`.
- **Owner:** Incident reviewer
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M10, M13.
- **Unit 1 mapping:** REQ-015; AC-006. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Evidence is preserved before mutation and investigation is reproducible.

#### PR-062 — Is a blameless review recorded with system causes and owned actions?

- **Category:** Operations, on-call, incident response, runbooks, and support
- **Risk:** Operators may respond late or unsafely when ownership, diagnostics, escalation, and recovery steps are unclear.
- **Verification:** Review postmortem and action owners/dates.
- **Evidence:** `evidence/readiness/PR-062/postmortem.md`.
- **Owner:** Incident reviewer
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M10.
- **Unit 1 mapping:** REQ-015; AC-006. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Review addresses system conditions and trackable improvements.

#### PR-063 — Is GitOps the declared deployment path and desired-state revision identifiable?

- **Category:** Change management, release safety, rollback, and GitOps
- **Risk:** Undetected drift or unverified rollback can leave the wrong configuration or artifact serving traffic.
- **Verification:** Compare Git commit, Argo CD source/revision, and workload state.
- **Evidence:** `evidence/readiness/PR-063/gitops.md`.
- **Owner:** Platform owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M02, M08.
- **Unit 1 mapping:** REQ-004, REQ-005; AC-002. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Declared Git source/revision matches reconciled workload state.

#### PR-064 — Is out-of-band drift detected/reconciled or surfaced according to policy?

- **Category:** Change management, release safety, rollback, and GitOps
- **Risk:** Undetected drift or unverified rollback can leave the wrong configuration or artifact serving traffic.
- **Verification:** Run benign scoped lab drift test after context preflight.
- **Evidence:** `evidence/readiness/PR-064/drift.md`.
- **Owner:** Platform owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M08, M10.
- **Unit 1 mapping:** REQ-005, REQ-027, REQ-031; AC-002. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Drift is detected and corrected or clearly reported.

#### PR-065 — Has rollback been executed through Git and verified against known-good artifact/config?

- **Category:** Change management, release safety, rollback, and GitOps
- **Risk:** Undetected drift or unverified rollback can leave the wrong configuration or artifact serving traffic.
- **Verification:** Revert disposable bad release; inspect Argo revision, runtime digest, smoke test.
- **Evidence:** `evidence/readiness/PR-065/rollback.md`.
- **Owner:** Release owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M08, M10.
- **Unit 1 mapping:** REQ-016; AC-007. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Git revert, desired state, runtime identity, and service test agree.

#### PR-066 — Are release approvals, change records, and rollback triggers declared?

- **Category:** Change management, release safety, rollback, and GitOps
- **Risk:** Undetected drift or unverified rollback can leave the wrong configuration or artifact serving traffic.
- **Verification:** Review release procedure and synthetic release decision.
- **Evidence:** `evidence/readiness/PR-066/change.md`.
- **Owner:** Release owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M02, M08, M10.
- **Unit 1 mapping:** REQ-003, REQ-032; AC-001, AC-007. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Decision owner, trigger, scope, and recovery path are explicit.

#### PR-067 — Has fresh-clone/clean-environment reproducibility been exercised?

- **Category:** Documentation, reproducibility, evidence quality, and governance
- **Risk:** The result cannot be independently reproduced or audited when evidence is missing, stale, or untraceable.
- **Verification:** Clone to new directory and follow README/runbook only.
- **Evidence:** `evidence/readiness/PR-067/fresh-clone.md`.
- **Owner:** Platform owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M02, M07, M16.
- **Unit 1 mapping:** REQ-021, REQ-028, REQ-029; AC-012. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Fresh clone completes selected preflight/bootstrap/verify/teardown without hidden state.

#### PR-068 — Does each evidence record conform to Unit 1 index fields and point to redacted retained evidence?

- **Category:** Documentation, reproducibility, evidence quality, and governance
- **Risk:** The result cannot be independently reproduced or audited when evidence is missing, stale, or untraceable.
- **Verification:** Validate `evidence/index.yaml` and inspect representative records.
- **Evidence:** `evidence/readiness/PR-068/index.md`.
- **Owner:** Evidence recorder
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M02, M12, M16.
- **Unit 1 mapping:** REQ-023, REQ-024, REQ-026; AC-012. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Records use singular requirement_id and required provenance metadata.

#### PR-069 — Does every applicable AC map to requirement, control/test, and evidence?

- **Category:** Documentation, reproducibility, evidence quality, and governance
- **Risk:** The result cannot be independently reproduced or audited when evidence is missing, stale, or untraceable.
- **Verification:** Run Unit 1 traceability checker and inspect orphans.
- **Evidence:** `evidence/readiness/PR-069/traceability.md`.
- **Owner:** Evidence recorder
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M02, M16.
- **Unit 1 mapping:** REQ-022, REQ-027; AC-012. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** No applicable AC or required evidence is orphaned/missing.

#### PR-070 — Are human-review items supported by explicit reviewer attestations?

- **Category:** Documentation, reproducibility, evidence quality, and governance
- **Risk:** The result cannot be independently reproduced or audited when evidence is missing, stale, or untraceable.
- **Verification:** Inspect reviewer identity/role/time/scope/decision/evidence/rationale.
- **Evidence:** `evidence/readiness/PR-070/attestations.md`.
- **Owner:** Readiness reviewer
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M10, M16.
- **Unit 1 mapping:** REQ-022, REQ-023; AC-012. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Manual/hybrid judgement has a complete attestation; solo role-play is labelled.

#### PR-071 — Are checklist version, item revisions, and material changes recorded?

- **Category:** Documentation, reproducibility, evidence quality, and governance
- **Risk:** The result cannot be independently reproduced or audited when evidence is missing, stale, or untraceable.
- **Verification:** Inspect metadata, change history, and approval.
- **Evidence:** `evidence/readiness/PR-071/version.md`.
- **Owner:** Checklist owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M10, M16.
- **Unit 1 mapping:** REQ-032; AC-012. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Item semantics and policy changes are versioned and reviewable.

#### PR-072 — Are assumptions, non-goals, waivers, residual risks, and conditions recorded?

- **Category:** Documentation, reproducibility, evidence quality, and governance
- **Risk:** The result cannot be independently reproduced or audited when evidence is missing, stale, or untraceable.
- **Verification:** Review risk/assumption/waiver registers and expiry/approval.
- **Evidence:** `evidence/readiness/PR-072/decision-register.md`.
- **Owner:** Readiness reviewer
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Major / gate `false`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M10, M15, M16.
- **Unit 1 mapping:** REQ-032; AC-012. Do not invent missing Unit 1 IDs.
- **Automation:** `manual`. Negative test required for Blocker/Major items.
- **Pass condition:** Uncertainty is explicit; waivers do not silently pass blockers.

#### PR-073 — Is teardown previewed, explicitly confirmed, scoped, and verified?

- **Category:** Teardown, residual-resource checks, and lab safety
- **Risk:** Wrong-target operations or leftover resources and credentials can cause unintended changes, exposure, or cost.
- **Verification:** Review preview, approval, before/after inventory, cleanup record.
- **Evidence:** `evidence/readiness/PR-073/teardown.md`.
- **Owner:** Platform owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M07, M13, M15.
- **Unit 1 mapping:** REQ-020; AC-011. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Only declared lab resources are removed and post-inventory reconciles.

#### PR-074 — Are residual clusters, namespaces, volumes, registries, containers, credentials, and temp files checked?

- **Category:** Teardown, residual-resource checks, and lab safety
- **Risk:** Wrong-target operations or leftover resources and credentials can cause unintended changes, exposure, or cost.
- **Verification:** Compare inventory and cleanup record with creation manifest.
- **Evidence:** `evidence/readiness/PR-074/residual.md`.
- **Owner:** Platform owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M07, M13, M15.
- **Unit 1 mapping:** REQ-020; AC-011. Do not invent missing Unit 1 IDs.
- **Automation:** `hybrid`. Negative test required for Blocker/Major items.
- **Pass condition:** Every created resource is accounted for; no unexplained resource/credential remains.

#### PR-075 — Do scripts refuse unexpected context and require opt-in for mutation/fault injection?

- **Category:** Teardown, residual-resource checks, and lab safety
- **Risk:** Wrong-target operations or leftover resources and credentials can cause unintended changes, exposure, or cost.
- **Verification:** Run wrong-context negative tests and inspect explicit context/dry-run guards.
- **Evidence:** `evidence/readiness/PR-075/lab-safety.md`.
- **Owner:** Platform owner
- **Applicability:** data_service: required; scheduled_pipeline: required; ml_inference: required; integrated_capstone: required. For conditional items, record the trigger; N-A requires a profile-specific reason and reviewer approval where required.
- **Severity / gate:** Blocker / gate `true`.
- **Status:** `Not Run` in the template; final statuses are Pass, Fail, N-A, or Waived. Not Run/Unknown are incomplete.
- **Freshness:** stale if older than the configured age OR predating the last relevant change; 30 days is a configurable example, not a standard.
- **M01–M16:** M03, M07, M08, M13.
- **Unit 1 mapping:** REQ-029, REQ-031; AC-011, AC-012. Do not invent missing Unit 1 IDs.
- **Automation:** `automated`. Negative test required for Blocker/Major items.
- **Pass condition:** Wrong/missing context and missing opt-in fail before mutation.

### 2.9.2 Profile applicability

| Control family | Data service | Scheduled pipeline | ML inference | Integrated capstone |
|---|---|---|---|---|
| Scope/ownership/dependencies | Required | Required | Required | Required |
| CI/artifact identity/delivery gates | Required | Required | Required | Required |
| Stateful storage and restore | Required | Conditional if persistent data is owned | N-A if no persistent data is in scope | Required for PostgreSQL slice |
| CronJob schedule/retry/freshness/replay | Conditional | Required | N-A unless scheduled batch path exists | Required for pipeline slice |
| Model digest and model/code pairing | N-A unless model artifact deployed | N-A unless model artifact used | Required | Required for ML slice |
| Ingress/DNS/TLS | Conditional on exposed endpoint | Conditional | Conditional | Conditional |
| Identity/secrets/hardening | Required | Required | Required | Required |
| Metrics/logs/dashboard/tested alert | Required | Required | Required | Required |
| SLO/risk/incident/runbooks | Required | Required | Required | Required |
| Teardown/fresh-clone/traceability | Required | Required | Required | Required |

**Profile details**
- Data service: persistence, backup/restore, integrity, connection handling, migration safety, resource limits, and network controls are required. Git rollback does not reverse irreversible schema changes.
- Scheduled pipeline: idempotent rerun, schedule/time-zone assumptions, retries/backoff, concurrency, deadline/failure handling, freshness SLO, output invariants, partial-output handling, alerting, and safe backfill/replay are required.
- ML inference: model digest/hash, model/code pairing, latency/error indicators, synthetic load, resource sizing, synthetic quality/drift signals, and model+code rollback are required. No real dataset or GPU.
- Integrated capstone: full CI→registry→GitOps, identity/security, metrics/logs/alerts, failure/rollback/restore/teardown, traceability, and reproducibility are required.

**N-A review:** verify profile and architecture, identify the item trigger, confirm it is absent, inspect diagram/config, record reason, and obtain approval where required. If trigger exists, N-A is invalid.

### 2.9.3 Unit 1 and M01–M16 mapping

This is a cross-reference, not a demand to rebuild every earlier module.

| Category | M01–M16 | Canonical Unit 1 mapping |
|---|---|---|
| Scope/ownership/architecture | M03/M04/M07/M10/M16 | REQ-025/032; AC-012 |
| CI/artifact integrity | M01/M02/M06/M08/M12 | REQ-001–003/030; AC-001/010 |
| Kubernetes/packaging | M03/M05/M06/M07/M12 | REQ-009/017/018/028/031; AC-003/008/012 |
| Networking/TLS | M04/M09/M12 | REQ-010; AC-003/012 as applicable |
| Identity/secrets | M09/M12 | REQ-006–008; AC-003/004 |
| Supply chain | M01/M02/M09/M12 | REQ-002/003/006–009/027/030; AC-001/003/004/010 |
| Reliability/failure | M03/M05/M10/M13 | REQ-015/019/027/031; AC-006/009 |
| Observability | M10/M11 | REQ-011–014; AC-005 |
| SLO/risk | M10/M11/M15 | REQ-011/014/019/025; AC-005/009/012 |
| Backup/restore | M05/M10/M13 | REQ-017/018; AC-008 |
| Capacity/cost | M03/M10/M15 | REQ-031/032; AC-012 |
| Operations/runbooks | M03/M10/M11/M13 | REQ-015; AC-006 |
| Change/GitOps | M02/M08/M10 | REQ-003–005/016/030; AC-001/002/007 |
| Documentation/evidence | M02/M07/M12/M16 | REQ-021–029/032; AC-012 |
| Teardown/safety | M03/M07/M13/M15 | REQ-020/029/031; AC-011/012 |

**Complete M01–M16 handoff reminder:** M01 images/registry; M02 CI/CD; M03 operations; M04 networking/TLS; M05 storage/stateful workloads; M06 packaging; M07 infrastructure as code; M08 GitOps/progressive delivery; M09 secrets/identity; M10 SRE/incidents/SLOs/error budgets/postmortems/ORR; M11 observability; M12 security/software supply chain; M13 backup/DR/chaos; M14 multi-cluster concepts (Awareness/conditional only, not a local-core requirement); M15 capacity/FinOps; M16 platform engineering/golden paths. Golden-path template reuse is optional; Backstage and Crossplane are not required.

Unit 1 evidence records use singular `requirement_id`. For a checklist item mapped to multiple REQs, create separate evidence-index records or traceability rows; do not change Unit 1's schema to `requirement_ids`.

### 2.10 Automated checklist runner and tests

#### 2.10.1 YAML schema and all-item representation

The following JSON-form YAML is valid YAML 1.2 (JSON is a YAML 1.2 subset) and contains **all 75 checklist items**, not a partial sample. It is intentionally compact to keep the machine-readable representation auditable. Save as `readiness/checklist.yaml` in the learner's separate implementation repository. No implementation files are created by this document.

Required item fields: ID, category, question, risk, verification, evidence, owner, profiles, profile applicability, severity, status, N-A reason, waiver, evidence timestamp, last relevant change, freshness policy, mapped modules, requirement IDs, acceptance criteria, automation, gate, non-waivable, negative-test requirement/result, and pass condition. Conditional fields: N-A reason; complete waiver metadata; evidence path/timestamp for Pass; reviewer attestation for manual/hybrid Pass.

Allowed statuses: Pass, Fail, N-A, Waived, Not Run, Unknown. Allowed severities: Blocker, Major, Minor. Allowed automation: automated, manual, hybrid.

```yaml
# File: readiness/checklist.yaml
{
  "schema_version": "1",
  "profile": "integrated_capstone",
  "scope": "[ASSUMPTION] Synthetic local lab; set actual profile/scope before use.",
  "commit_sha": "[SET_ACTUAL_COMMIT_SHA]",
  "artifact_digest": "[SET_ACTUAL_DIGEST_OR_NULL]",
  "freshness_policy": {
    "max_age_days": 30,
    "rule": "stale if older than age OR predates last relevant change",
    "note": "30 days is a configurable teaching example, not a universal standard"
  },
  "items": [
    {
      "id": "PR-001",
      "category": "Service scope, ownership, architecture, and dependencies",
      "question": "Is profile, user outcome, environment, owner, and non-goals recorded?",
      "risk": "Unowned services or hidden dependencies create failure paths with no accountable operator or recovery boundary.",
      "verification": "Review scope record against deployed services and selected profile.",
      "evidence": {
        "path": "evidence/readiness/PR-001/scope.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Service owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10",
        "M16"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Scope, owner, environment, boundaries, and non-goals are explicit."
    },
    {
      "id": "PR-002",
      "category": "Service scope, ownership, architecture, and dependencies",
      "question": "Is an accountable service owner and support/escalation contact named?",
      "risk": "Unowned services or hidden dependencies create failure paths with no accountable operator or recovery boundary.",
      "verification": "Review ownership register and conduct owner walkthrough.",
      "evidence": {
        "path": "evidence/readiness/PR-002/owner.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Service owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10",
        "M16"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Owner, backup/solo role, and support boundary are recorded."
    },
    {
      "id": "PR-003",
      "category": "Service scope, ownership, architecture, and dependencies",
      "question": "Are runtime, data, CI, registry, GitOps, identity, and observability dependencies inventoried?",
      "risk": "Unowned services or hidden dependencies create failure paths with no accountable operator or recovery boundary.",
      "verification": "Compare dependency inventory with architecture and configuration.",
      "evidence": {
        "path": "evidence/readiness/PR-003/dependencies.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Service owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M04",
        "M05",
        "M08",
        "M09",
        "M11"
      ],
      "requirement_ids": [
        "REQ-032"
      ],
      "acceptance_criteria": [],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Each material dependency has owner, purpose, failure impact, and evidence source."
    },
    {
      "id": "PR-004",
      "category": "Service scope, ownership, architecture, and dependencies",
      "question": "Does the architecture show components, data flows, and trust boundaries?",
      "risk": "Unowned services or hidden dependencies create failure paths with no accountable operator or recovery boundary.",
      "verification": "Review diagram against manifests and running lab.",
      "evidence": {
        "path": "evidence/readiness/PR-004/architecture.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Platform reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M04",
        "M07",
        "M08",
        "M09",
        "M12",
        "M16"
      ],
      "requirement_ids": [
        "REQ-032"
      ],
      "acceptance_criteria": [],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Diagram is current, scoped, and independently understandable."
    },
    {
      "id": "PR-005",
      "category": "Service scope, ownership, architecture, and dependencies",
      "question": "Are criticality and user-visible failure modes described?",
      "risk": "Unowned services or hidden dependencies create failure paths with no accountable operator or recovery boundary.",
      "verification": "Review criticality record and failure-mode map.",
      "evidence": {
        "path": "evidence/readiness/PR-005/criticality.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Service owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10",
        "M15"
      ],
      "requirement_ids": [
        "REQ-032"
      ],
      "acceptance_criteria": [],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "User impact, interruption tolerance, and residual risks are explicit."
    },
    {
      "id": "PR-006",
      "category": "Delivery pipeline and artifact integrity",
      "question": "Do required CI build, test, and security checks run before promotion?",
      "risk": "A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.",
      "verification": "Inspect workflow and run record for exact source commit.",
      "evidence": {
        "path": "evidence/readiness/PR-006/ci.json",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "CI owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M01",
        "M02",
        "M12"
      ],
      "requirement_ids": [
        "REQ-001",
        "REQ-003"
      ],
      "acceptance_criteria": [
        "AC-001"
      ],
      "automation": "automated",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Required jobs executed successfully for the candidate commit."
    },
    {
      "id": "PR-007",
      "category": "Delivery pipeline and artifact integrity",
      "question": "Does a failing test or scan block promotion?",
      "risk": "A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.",
      "verification": "Plant a synthetic failing test in a disposable branch and inspect gate behavior.",
      "evidence": {
        "path": "evidence/readiness/PR-007/negative-gate.json",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "CI owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M02",
        "M12"
      ],
      "requirement_ids": [
        "REQ-003",
        "REQ-027"
      ],
      "acceptance_criteria": [
        "AC-001"
      ],
      "automation": "automated",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Failing required check prevents promotion."
    },
    {
      "id": "PR-008",
      "category": "Delivery pipeline and artifact integrity",
      "question": "Is the deployed artifact pinned by immutable digest/hash?",
      "risk": "A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.",
      "verification": "Compare registry, GitOps, and runtime identity.",
      "evidence": {
        "path": "evidence/readiness/PR-008/digest.json",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Release owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M01",
        "M02",
        "M12"
      ],
      "requirement_ids": [
        "REQ-002",
        "REQ-030"
      ],
      "acceptance_criteria": [
        "AC-001",
        "AC-010"
      ],
      "automation": "automated",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Full digest/hash matches tested, promoted, declared, and deployed artifact."
    },
    {
      "id": "PR-009",
      "category": "Delivery pipeline and artifact integrity",
      "question": "Is signing/provenance assessed and its adoption boundary documented?",
      "risk": "A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.",
      "verification": "Verify selected tool if Cap+Security; otherwise record Awareness decision.",
      "evidence": {
        "path": "evidence/readiness/PR-009/provenance.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Security reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "conditional",
        "scheduled_pipeline": "conditional",
        "ml_inference": "conditional",
        "integrated_capstone": "conditional"
      },
      "severity": "Minor",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M01",
        "M12"
      ],
      "requirement_ids": [
        "REQ-002",
        "REQ-032"
      ],
      "acceptance_criteria": [
        "AC-010"
      ],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": false,
      "negative_test_result": "Not Run",
      "pass_condition": "Evidence or a reasoned optional/not-selected decision is recorded."
    },
    {
      "id": "PR-010",
      "category": "Delivery pipeline and artifact integrity",
      "question": "Is the same immutable artifact promoted without rebuilding?",
      "risk": "A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.",
      "verification": "Compare source commit, build run, digest, and manifests.",
      "evidence": {
        "path": "evidence/readiness/PR-010/promotion.json",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Release owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M01",
        "M02",
        "M08"
      ],
      "requirement_ids": [
        "REQ-001",
        "REQ-002",
        "REQ-030"
      ],
      "acceptance_criteria": [
        "AC-001",
        "AC-010"
      ],
      "automation": "automated",
      "gate": true,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "All stages refer to one tested build identity and digest."
    },
    {
      "id": "PR-011",
      "category": "Delivery pipeline and artifact integrity",
      "question": "Are protected-branch and required-check controls configured?",
      "risk": "A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.",
      "verification": "Review repository rules and a safe negative test.",
      "evidence": {
        "path": "evidence/readiness/PR-011/branch-rules.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Repository owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M02",
        "M12"
      ],
      "requirement_ids": [
        "REQ-003",
        "REQ-032"
      ],
      "acceptance_criteria": [
        "AC-001"
      ],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Required checks and review policy are recorded with local-emulation limits."
    },
    {
      "id": "PR-012",
      "category": "Delivery pipeline and artifact integrity",
      "question": "Can a clean checkout reproduce build inputs and identify tool versions?",
      "risk": "A failed, unreviewed, or mutated artifact can be promoted and deployed without trustworthy build-to-runtime identity.",
      "verification": "Build from a fresh clone and compare versions and digest.",
      "evidence": {
        "path": "evidence/readiness/PR-012/build.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "CI owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M01",
        "M02",
        "M06",
        "M07"
      ],
      "requirement_ids": [
        "REQ-021",
        "REQ-030"
      ],
      "acceptance_criteria": [
        "AC-012"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Inputs, versions, SHA, and output digest are retained."
    },
    {
      "id": "PR-013",
      "category": "Kubernetes workload configuration and packaging",
      "question": "Do rendered manifests/charts validate against selected tool versions?",
      "risk": "Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.",
      "verification": "Run selected Helm/Kustomize render and validators.",
      "evidence": {
        "path": "evidence/readiness/PR-013/validation.txt",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Platform owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M06",
        "M07"
      ],
      "requirement_ids": [
        "REQ-028"
      ],
      "acceptance_criteria": [],
      "automation": "automated",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Rendered resources pass validators and are tied to a commit/version."
    },
    {
      "id": "PR-014",
      "category": "Kubernetes workload configuration and packaging",
      "question": "Are CPU/memory requests and limits justified by bounded lab observations?",
      "risk": "Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.",
      "verification": "Inspect workload specs and compare with synthetic test and restart/OOM behavior.",
      "evidence": {
        "path": "evidence/readiness/PR-014/resources.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Workload owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10",
        "M15"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Resource settings have rationale and measured lab evidence."
    },
    {
      "id": "PR-015",
      "category": "Kubernetes workload configuration and packaging",
      "question": "Does the workload run non-root with restricted privilege/capabilities where feasible?",
      "risk": "Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.",
      "verification": "Inspect Pod security context and runtime identity.",
      "evidence": {
        "path": "evidence/readiness/PR-015/hardening.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Security reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M12"
      ],
      "requirement_ids": [
        "REQ-009"
      ],
      "acceptance_criteria": [
        "AC-003"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "No unexplained root, privileged mode, or excess capability remains."
    },
    {
      "id": "PR-016",
      "category": "Kubernetes workload configuration and packaging",
      "question": "Are startup/readiness/liveness probes appropriate and tested?",
      "risk": "Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.",
      "verification": "Exercise slow-start, not-ready, and unhealthy synthetic states.",
      "evidence": {
        "path": "evidence/readiness/PR-016/probes.json",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Workload owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "automated",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Probe semantics and expected transitions are tested."
    },
    {
      "id": "PR-017",
      "category": "Kubernetes workload configuration and packaging",
      "question": "Does the service handle graceful shutdown within its declared budget?",
      "risk": "Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.",
      "verification": "Run bounded termination test and inspect application behavior.",
      "evidence": {
        "path": "evidence/readiness/PR-017/shutdown.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Workload owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Shutdown behavior, timeout assumptions, and limitations are verified."
    },
    {
      "id": "PR-018",
      "category": "Kubernetes workload configuration and packaging",
      "question": "Is disruption behavior considered for replicas and disruption controls?",
      "risk": "Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.",
      "verification": "Review replica/disruption settings and safe lab test.",
      "evidence": {
        "path": "evidence/readiness/PR-018/disruption.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Platform owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Disruption expectations are tested; single-node kind is not called HA."
    },
    {
      "id": "PR-019",
      "category": "Kubernetes workload configuration and packaging",
      "question": "Are persistent volumes and stateful lifecycle controls documented?",
      "risk": "Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.",
      "verification": "Inspect PVC/PV and verify persistence across controlled restart.",
      "evidence": {
        "path": "evidence/readiness/PR-019/storage.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Data owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "conditional",
        "ml_inference": "na_allowed",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M05",
        "M07",
        "M13"
      ],
      "requirement_ids": [
        "REQ-017",
        "REQ-018"
      ],
      "acceptance_criteria": [
        "AC-008"
      ],
      "automation": "hybrid",
      "gate": true,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Persistence and storage assumptions are verified separately from restore."
    },
    {
      "id": "PR-020",
      "category": "Kubernetes workload configuration and packaging",
      "question": "Are runtime configuration changes traceable to reviewed desired-state revisions?",
      "risk": "Invalid or unsafe workload configuration can cause outages, resource exhaustion, privilege expansion, or unreproducible deployments.",
      "verification": "Compare config source, Git revision, rendered manifest, and runtime revision.",
      "evidence": {
        "path": "evidence/readiness/PR-020/config.md",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Platform owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M06",
        "M08"
      ],
      "requirement_ids": [
        "REQ-004",
        "REQ-005"
      ],
      "acceptance_criteria": [
        "AC-002"
      ],
      "automation": "automated",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Configuration source and runtime state map to a specific Git revision."
    },
    {
      "id": "PR-021",
      "category": "Networking, ingress, DNS, and TLS",
      "question": "Are service exposure, ingress, DNS, and TLS requirements declared?",
      "risk": "Unintended reachability, broken routing, or weak transport trust can expose services or interrupt required dependencies.",
      "verification": "Review service/ingress objects and architecture for selected profile.",
      "evidence": {
        "path": "evidence/readiness/PR-021/exposure.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Network owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "conditional",
        "scheduled_pipeline": "conditional",
        "ml_inference": "conditional",
        "integrated_capstone": "conditional"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M04"
      ],
      "requirement_ids": [
        "REQ-010"
      ],
      "acceptance_criteria": [],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Exposed paths and TLS/DNS assumptions are identified; internal-only stays internal."
    },
    {
      "id": "PR-022",
      "category": "Networking, ingress, DNS, and TLS",
      "question": "Where supported, does NetworkPolicy restrict traffic to declared dependencies?",
      "risk": "Unintended reachability, broken routing, or weak transport trust can expose services or interrupt required dependencies.",
      "verification": "Inspect policy; test allowed and deliberately denied paths.",
      "evidence": {
        "path": "evidence/readiness/PR-022/network-policy.json",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Network owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "conditional",
        "scheduled_pipeline": "conditional",
        "ml_inference": "conditional",
        "integrated_capstone": "conditional"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M04",
        "M12"
      ],
      "requirement_ids": [
        "REQ-010",
        "REQ-027"
      ],
      "acceptance_criteria": [],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Allowed path succeeds and undeclared path is denied, or enforcement limit is stated."
    },
    {
      "id": "PR-023",
      "category": "Networking, ingress, DNS, and TLS",
      "question": "Are outbound dependencies and egress paths limited or justified?",
      "risk": "Unintended reachability, broken routing, or weak transport trust can expose services or interrupt required dependencies.",
      "verification": "Review dependency list and safe synthetic connectivity tests.",
      "evidence": {
        "path": "evidence/readiness/PR-023/egress.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Network owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "conditional",
        "scheduled_pipeline": "conditional",
        "ml_inference": "conditional",
        "integrated_capstone": "conditional"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M04",
        "M12"
      ],
      "requirement_ids": [
        "REQ-010"
      ],
      "acceptance_criteria": [],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Outbound paths have purpose and owner; broad unknown egress is a finding."
    },
    {
      "id": "PR-024",
      "category": "Networking, ingress, DNS, and TLS",
      "question": "Where TLS is used, are certificate trust, expiry, and renewal ownership documented?",
      "risk": "Unintended reachability, broken routing, or weak transport trust can expose services or interrupt required dependencies.",
      "verification": "Inspect certificate metadata and renewal runbook without exposing keys.",
      "evidence": {
        "path": "evidence/readiness/PR-024/tls.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Security reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "conditional",
        "scheduled_pipeline": "conditional",
        "ml_inference": "conditional",
        "integrated_capstone": "conditional"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M04",
        "M09"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Trust and renewal responsibilities are clear; private keys are excluded."
    },
    {
      "id": "PR-025",
      "category": "Identity, RBAC, workload identity, and secrets",
      "question": "Does each workload use a dedicated service account or documented identity boundary?",
      "risk": "Excess privilege or leaked credentials can enable unauthorized actions and expand blast radius.",
      "verification": "Inspect service-account bindings against identity map.",
      "evidence": {
        "path": "evidence/readiness/PR-025/identity.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Identity owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M09"
      ],
      "requirement_ids": [
        "REQ-006"
      ],
      "acceptance_criteria": [
        "AC-003"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Workload identities are explicit and not unnecessarily privileged/shared."
    },
    {
      "id": "PR-026",
      "category": "Identity, RBAC, workload identity, and secrets",
      "question": "Are RBAC permissions least-privilege and unauthorized actions denied?",
      "risk": "Excess privilege or leaked credentials can enable unauthorized actions and expand blast radius.",
      "verification": "Review role bindings and run allowed/denied authorization tests.",
      "evidence": {
        "path": "evidence/readiness/PR-026/rbac.txt",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Identity owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M09",
        "M12"
      ],
      "requirement_ids": [
        "REQ-006",
        "REQ-027"
      ],
      "acceptance_criteria": [
        "AC-003"
      ],
      "automation": "automated",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Required action succeeds and prohibited action is denied."
    },
    {
      "id": "PR-027",
      "category": "Identity, RBAC, workload identity, and secrets",
      "question": "Are secrets referenced securely and excluded from Git, images, logs, and evidence?",
      "risk": "Excess privilege or leaked credentials can enable unauthorized actions and expand blast radius.",
      "verification": "Inspect references and scan source/artifacts/log fixtures.",
      "evidence": {
        "path": "evidence/readiness/PR-027/secrets.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Security reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M09",
        "M12"
      ],
      "requirement_ids": [
        "REQ-007",
        "REQ-008"
      ],
      "acceptance_criteria": [
        "AC-004"
      ],
      "automation": "hybrid",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "No plaintext secret remains; access/reference boundary is documented."
    },
    {
      "id": "PR-028",
      "category": "Identity, RBAC, workload identity, and secrets",
      "question": "Does secret scanning detect a synthetic canary?",
      "risk": "Excess privilege or leaked credentials can enable unauthorized actions and expand blast radius.",
      "verification": "Run clean baseline and planted dummy-secret negative test.",
      "evidence": {
        "path": "evidence/readiness/PR-028/secret-scan.json",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Security reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M09",
        "M12"
      ],
      "requirement_ids": [
        "REQ-008",
        "REQ-027"
      ],
      "acceptance_criteria": [
        "AC-004"
      ],
      "automation": "automated",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Canary is detected; no real credential is used."
    },
    {
      "id": "PR-029",
      "category": "Security controls and software supply chain",
      "question": "Was an artifact scan executed for the exact candidate and result retained?",
      "risk": "Unreviewed or tampered artifacts and missing enforcement can introduce preventable runtime risk.",
      "verification": "Inspect scan run, digest, scanner version, policy, and disposition.",
      "evidence": {
        "path": "evidence/readiness/PR-029/scan.json",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Security reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M01",
        "M12"
      ],
      "requirement_ids": [
        "REQ-003"
      ],
      "acceptance_criteria": [
        "AC-001"
      ],
      "automation": "automated",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Scan matches candidate; no claim of zero vulnerabilities is made."
    },
    {
      "id": "PR-030",
      "category": "Security controls and software supply chain",
      "question": "Is provenance/signature verification performed where selected?",
      "risk": "Unreviewed or tampered artifacts and missing enforcement can introduce preventable runtime risk.",
      "verification": "Verify selected Cap+Security trust policy or record optional decision.",
      "evidence": {
        "path": "evidence/readiness/PR-030/provenance.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Security reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "conditional",
        "scheduled_pipeline": "conditional",
        "ml_inference": "conditional",
        "integrated_capstone": "conditional"
      },
      "severity": "Minor",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M01",
        "M12"
      ],
      "requirement_ids": [
        "REQ-002",
        "REQ-030"
      ],
      "acceptance_criteria": [
        "AC-010"
      ],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": false,
      "negative_test_result": "Not Run",
      "pass_condition": "Trust boundary and verification result or optionality are recorded."
    },
    {
      "id": "PR-031",
      "category": "Security controls and software supply chain",
      "question": "Are selected admission/policy controls tested with a denied fixture?",
      "risk": "Unreviewed or tampered artifacts and missing enforcement can introduce preventable runtime risk.",
      "verification": "Run policy validation and synthetic denied-manifest test.",
      "evidence": {
        "path": "evidence/readiness/PR-031/policy.md",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Security reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "conditional",
        "scheduled_pipeline": "conditional",
        "ml_inference": "conditional",
        "integrated_capstone": "conditional"
      },
      "severity": "Minor",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M12"
      ],
      "requirement_ids": [
        "REQ-009",
        "REQ-027"
      ],
      "acceptance_criteria": [
        "AC-003"
      ],
      "automation": "automated",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": false,
      "negative_test_result": "Not Run",
      "pass_condition": "Compliant fixture passes and planted non-compliant fixture is rejected."
    },
    {
      "id": "PR-032",
      "category": "Security controls and software supply chain",
      "question": "Are filesystem permissions, capabilities, and writable paths restricted?",
      "risk": "Unreviewed or tampered artifacts and missing enforcement can introduce preventable runtime risk.",
      "verification": "Inspect security context and test intended writable paths.",
      "evidence": {
        "path": "evidence/readiness/PR-032/filesystem.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Security reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M12"
      ],
      "requirement_ids": [
        "REQ-009"
      ],
      "acceptance_criteria": [
        "AC-003"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Privilege and write access are minimized or justified."
    },
    {
      "id": "PR-033",
      "category": "Security controls and software supply chain",
      "question": "Is base-image/dependency maintenance owned and documented?",
      "risk": "Unreviewed or tampered artifacts and missing enforcement can introduce preventable runtime risk.",
      "verification": "Review base image, dependency update process, owner, and review date.",
      "evidence": {
        "path": "evidence/readiness/PR-033/maintenance.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Workload owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Minor",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M01",
        "M12"
      ],
      "requirement_ids": [
        "REQ-003",
        "REQ-032"
      ],
      "acceptance_criteria": [
        "AC-001"
      ],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": false,
      "negative_test_result": "Not Run",
      "pass_condition": "A repeatable update/rebuild path and owner are documented."
    },
    {
      "id": "PR-034",
      "category": "Security controls and software supply chain",
      "question": "Can artifact identity be independently verified beyond a mutable tag?",
      "risk": "Unreviewed or tampered artifacts and missing enforcement can introduce preventable runtime risk.",
      "verification": "Recompute/inspect digest and compare build/deployment evidence.",
      "evidence": {
        "path": "evidence/readiness/PR-034/identity.txt",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Release owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M01",
        "M12"
      ],
      "requirement_ids": [
        "REQ-002",
        "REQ-030"
      ],
      "acceptance_criteria": [
        "AC-001",
        "AC-010"
      ],
      "automation": "automated",
      "gate": true,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Independent digest comparison matches recorded immutable artifact."
    },
    {
      "id": "PR-035",
      "category": "Reliability, health checks, graceful shutdown, and disruption behavior",
      "question": "Do health checks represent startup, readiness, and process health correctly?",
      "risk": "Misleading health checks, unbounded retries, and unsafe failure behavior can amplify an incident or duplicate work.",
      "verification": "Run positive/negative probe scenarios and inspect transitions.",
      "evidence": {
        "path": "evidence/readiness/PR-035/health.md",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Workload owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "automated",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Each health signal has defined semantics and unhealthy test."
    },
    {
      "id": "PR-036",
      "category": "Reliability, health checks, graceful shutdown, and disruption behavior",
      "question": "Is dependency failure behavior explicitly graceful-degrade or fail-closed?",
      "risk": "Misleading health checks, unbounded retries, and unsafe failure behavior can amplify an incident or duplicate work.",
      "verification": "Review failure-mode table and execute bounded synthetic dependency failure.",
      "evidence": {
        "path": "evidence/readiness/PR-036/dependency.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Service owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10"
      ],
      "requirement_ids": [
        "REQ-015"
      ],
      "acceptance_criteria": [
        "AC-006"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Chosen behavior, impact, and safe recovery action are evidenced."
    },
    {
      "id": "PR-037",
      "category": "Reliability, health checks, graceful shutdown, and disruption behavior",
      "question": "Are retries bounded, backoff-aware, and safe against duplicate side effects?",
      "risk": "Misleading health checks, unbounded retries, and unsafe failure behavior can amplify an incident or duplicate work.",
      "verification": "Inspect retry settings and run transient-failure test with output invariants.",
      "evidence": {
        "path": "evidence/readiness/PR-037/retry.md",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Pipeline owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "conditional",
        "scheduled_pipeline": "required",
        "ml_inference": "conditional",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10"
      ],
      "requirement_ids": [
        "REQ-019",
        "REQ-027"
      ],
      "acceptance_criteria": [
        "AC-009"
      ],
      "automation": "automated",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Retries are bounded and repeated execution preserves output invariants."
    },
    {
      "id": "PR-038",
      "category": "Reliability, health checks, graceful shutdown, and disruption behavior",
      "question": "Is concurrent scheduled-job execution prevented or made safe?",
      "risk": "Misleading health checks, unbounded retries, and unsafe failure behavior can amplify an incident or duplicate work.",
      "verification": "Inspect concurrency policy/lock and run controlled overlap test.",
      "evidence": {
        "path": "evidence/readiness/PR-038/concurrency.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Pipeline owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "conditional",
        "scheduled_pipeline": "required",
        "ml_inference": "conditional",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M05",
        "M10"
      ],
      "requirement_ids": [
        "REQ-019"
      ],
      "acceptance_criteria": [
        "AC-009"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Overlapping runs are prevented or safe by a tested invariant."
    },
    {
      "id": "PR-039",
      "category": "Reliability, health checks, graceful shutdown, and disruption behavior",
      "question": "Are deadlines, timeouts, and retry limits bounded and justified?",
      "risk": "Misleading health checks, unbounded retries, and unsafe failure behavior can amplify an incident or duplicate work.",
      "verification": "Review config and execute synthetic slow-dependency test.",
      "evidence": {
        "path": "evidence/readiness/PR-039/timeouts.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Workload owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "conditional",
        "scheduled_pipeline": "required",
        "ml_inference": "conditional",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10"
      ],
      "requirement_ids": [
        "REQ-019"
      ],
      "acceptance_criteria": [
        "AC-009"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Timeouts bound resource use and have a failure response."
    },
    {
      "id": "PR-040",
      "category": "Reliability, health checks, graceful shutdown, and disruption behavior",
      "question": "Are critical dependency failures, blast radius, and recovery actions documented?",
      "risk": "Misleading health checks, unbounded retries, and unsafe failure behavior can amplify an incident or duplicate work.",
      "verification": "Review dependency matrix and safe runbook walkthrough.",
      "evidence": {
        "path": "evidence/readiness/PR-040/failures.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Service owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10",
        "M13"
      ],
      "requirement_ids": [
        "REQ-015"
      ],
      "acceptance_criteria": [
        "AC-006"
      ],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Failure modes are prioritized, owned, and linked to diagnostics/recovery."
    },
    {
      "id": "PR-041",
      "category": "Observability: metrics, logs, dashboards, traces, alerts",
      "question": "Are workload metrics collected with stable workload identity and timestamps?",
      "risk": "Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.",
      "verification": "Inspect Prometheus targets and query expected synthetic series.",
      "evidence": {
        "path": "evidence/readiness/PR-041/metrics.txt",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Observability owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M10",
        "M11"
      ],
      "requirement_ids": [
        "REQ-011"
      ],
      "acceptance_criteria": [
        "AC-005"
      ],
      "automation": "automated",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Expected metrics are present, queryable, and attributable."
    },
    {
      "id": "PR-042",
      "category": "Observability: metrics, logs, dashboards, traces, alerts",
      "question": "Are logs structured enough to correlate time, workload, and run/drill identity?",
      "risk": "Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.",
      "verification": "Inspect synthetic log records and redaction.",
      "evidence": {
        "path": "evidence/readiness/PR-042/logs.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Observability owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M11",
        "M12"
      ],
      "requirement_ids": [
        "REQ-012"
      ],
      "acceptance_criteria": [
        "AC-005"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Logs support correlation without leaking secrets/sensitive data."
    },
    {
      "id": "PR-043",
      "category": "Observability: metrics, logs, dashboards, traces, alerts",
      "question": "Does the dashboard identify workload and show symptom-oriented health signals?",
      "risk": "Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.",
      "verification": "Inspect queries, labels, time range, and runbook links.",
      "evidence": {
        "path": "evidence/readiness/PR-043/dashboard.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Observability owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M10",
        "M11"
      ],
      "requirement_ids": [
        "REQ-013"
      ],
      "acceptance_criteria": [
        "AC-005"
      ],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Dashboard is reachable, correctly scoped, useful, and linked."
    },
    {
      "id": "PR-044",
      "category": "Observability: metrics, logs, dashboards, traces, alerts",
      "question": "Are Prometheus rules tested with promtool when Prometheus rules are used?",
      "risk": "Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.",
      "verification": "Run installed promtool tests against committed rule files.",
      "evidence": {
        "path": "evidence/readiness/PR-044/promtool.txt",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Observability owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M10",
        "M11"
      ],
      "requirement_ids": [
        "REQ-014",
        "REQ-027"
      ],
      "acceptance_criteria": [
        "AC-005"
      ],
      "automation": "automated",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Rule tests pass for installed version; syntax is verified."
    },
    {
      "id": "PR-045",
      "category": "Observability: metrics, logs, dashboards, traces, alerts",
      "question": "Has one alert path been safely exercised from signal through alert event/owner?",
      "risk": "Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.",
      "verification": "Trigger benign lab condition and retain signal, rule, route, event, and timestamp.",
      "evidence": {
        "path": "evidence/readiness/PR-045/alert.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Observability owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M10",
        "M11"
      ],
      "requirement_ids": [
        "REQ-014"
      ],
      "acceptance_criteria": [
        "AC-005"
      ],
      "automation": "hybrid",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "A lab alert event is observed and owned; rule file alone is insufficient."
    },
    {
      "id": "PR-046",
      "category": "Observability: metrics, logs, dashboards, traces, alerts",
      "question": "If tracing is used, are trace context and sampling/retention documented?",
      "risk": "Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.",
      "verification": "Review synthetic trace and trace/log correlation.",
      "evidence": {
        "path": "evidence/readiness/PR-046/tracing.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Observability owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "conditional",
        "scheduled_pipeline": "conditional",
        "ml_inference": "conditional",
        "integrated_capstone": "conditional"
      },
      "severity": "Minor",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M11"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": false,
      "negative_test_result": "Not Run",
      "pass_condition": "Tracing is scoped correctly or N-A is justified."
    },
    {
      "id": "PR-047",
      "category": "Observability: metrics, logs, dashboards, traces, alerts",
      "question": "Can telemetry be correlated with Git revision, artifact, deployment, and drill time?",
      "risk": "Symptoms may remain invisible, unowned, uncorrelated, or impossible to diagnose from retained telemetry.",
      "verification": "Compare timestamps and identities across CI, GitOps, runtime, metrics, and logs.",
      "evidence": {
        "path": "evidence/readiness/PR-047/correlation.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Observability owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M02",
        "M08",
        "M10",
        "M11"
      ],
      "requirement_ids": [
        "REQ-011",
        "REQ-012",
        "REQ-023"
      ],
      "acceptance_criteria": [
        "AC-005"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Timeline is reconstructable with timezone and uncertainty."
    },
    {
      "id": "PR-048",
      "category": "SLOs, error budgets, and operational risk",
      "question": "Is each SLO based on user-visible SLI, numerator/denominator, window, target, and exclusions?",
      "risk": "Targets disconnected from user outcomes can hide meaningful degradation and leave risk decisions implicit.",
      "verification": "Review SLO and reproduce query/calculation on synthetic events.",
      "evidence": {
        "path": "evidence/readiness/PR-048/slo.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "SRE reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M10",
        "M11"
      ],
      "requirement_ids": [
        "REQ-011",
        "REQ-014",
        "REQ-019"
      ],
      "acceptance_criteria": [
        "AC-005",
        "AC-009"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "SLI reflects user outcome; missing data/exclusions are explicit."
    },
    {
      "id": "PR-049",
      "category": "SLOs, error budgets, and operational risk",
      "question": "Is an error-budget policy defined where an SLO is meaningful?",
      "risk": "Targets disconnected from user outcomes can hide meaningful degradation and leave risk decisions implicit.",
      "verification": "Review calculation, response policy, owner, and scenario.",
      "evidence": {
        "path": "evidence/readiness/PR-049/budget.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "SRE reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Minor",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M10"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": false,
      "negative_test_result": "Not Run",
      "pass_condition": "Budget math and response are reproducible; assumptions are labelled."
    },
    {
      "id": "PR-050",
      "category": "SLOs, error budgets, and operational risk",
      "question": "Are material operational risks, assumptions, and residual risks owned?",
      "risk": "Targets disconnected from user outcomes can hide meaningful degradation and leave risk decisions implicit.",
      "verification": "Inspect risk register, ADRs, status, owner, and review date.",
      "evidence": {
        "path": "evidence/readiness/PR-050/risks.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Service owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M10",
        "M15",
        "M16"
      ],
      "requirement_ids": [
        "REQ-032"
      ],
      "acceptance_criteria": [],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Material risks are visible and not hidden by score."
    },
    {
      "id": "PR-051",
      "category": "Data protection, backup, restore, integrity, RPO, and RTO",
      "question": "Does the stateful service have a documented backup and isolated backup target?",
      "risk": "Data may be unrecoverable, incomplete, or silently corrupted despite a successful backup job.",
      "verification": "Inspect backup config and artifact metadata without credentials.",
      "evidence": {
        "path": "evidence/readiness/PR-051/backup.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Data owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "conditional",
        "ml_inference": "na_allowed",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M05",
        "M13"
      ],
      "requirement_ids": [
        "REQ-017"
      ],
      "acceptance_criteria": [
        "AC-008"
      ],
      "automation": "hybrid",
      "gate": true,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Backup identity and separation from active data are recorded."
    },
    {
      "id": "PR-052",
      "category": "Data protection, backup, restore, integrity, RPO, and RTO",
      "question": "Has backup actually been restored into an isolated target?",
      "risk": "Data may be unrecoverable, incomplete, or silently corrupted despite a successful backup job.",
      "verification": "Execute restore drill on synthetic data and retain timings/logs.",
      "evidence": {
        "path": "evidence/readiness/PR-052/restore.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Data owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "conditional",
        "ml_inference": "na_allowed",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M05",
        "M13"
      ],
      "requirement_ids": [
        "REQ-017"
      ],
      "acceptance_criteria": [
        "AC-008"
      ],
      "automation": "hybrid",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Isolated restore completed; backup existence alone does not pass."
    },
    {
      "id": "PR-053",
      "category": "Data protection, backup, restore, integrity, RPO, and RTO",
      "question": "Has restored data integrity been verified by row counts/checksums/invariants?",
      "risk": "Data may be unrecoverable, incomplete, or silently corrupted despite a successful backup job.",
      "verification": "Run documented integrity checks against source baseline and restored target.",
      "evidence": {
        "path": "evidence/readiness/PR-053/integrity.md",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Data owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "conditional",
        "ml_inference": "na_allowed",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M05",
        "M10",
        "M13"
      ],
      "requirement_ids": [
        "REQ-018"
      ],
      "acceptance_criteria": [
        "AC-008"
      ],
      "automation": "automated",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Integrity invariants match and are tied to restored backup identity."
    },
    {
      "id": "PR-054",
      "category": "Data protection, backup, restore, integrity, RPO, and RTO",
      "question": "Are RPO/RTO targets declared and actual lab measurements recorded?",
      "risk": "Data may be unrecoverable, incomplete, or silently corrupted despite a successful backup job.",
      "verification": "Review target and timed backup/restore evidence; recalculate durations.",
      "evidence": {
        "path": "evidence/readiness/PR-054/rpo-rto.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "SRE reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "conditional",
        "ml_inference": "na_allowed",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M10",
        "M13"
      ],
      "requirement_ids": [
        "REQ-018"
      ],
      "acceptance_criteria": [
        "AC-008"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Targets, boundaries, actuals, and deviations are recorded as lab values."
    },
    {
      "id": "PR-055",
      "category": "Capacity, performance, resource requests/limits, quotas, and cost",
      "question": "Has a bounded synthetic load test been run for declared lab objective?",
      "risk": "Saturation, OOM behavior, or unbounded resources can degrade service or create avoidable cost.",
      "verification": "Run documented synthetic profile and retain parameters/results/environment limits.",
      "evidence": {
        "path": "evidence/readiness/PR-055/load.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Workload owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "conditional",
        "scheduled_pipeline": "conditional",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10",
        "M15"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Test scope and limits are recorded; no production extrapolation."
    },
    {
      "id": "PR-056",
      "category": "Capacity, performance, resource requests/limits, quotas, and cost",
      "question": "Are resource requests/limits, saturation signals, and OOM/restarts reviewed together?",
      "risk": "Saturation, OOM behavior, or unbounded resources can degrade service or create avoidable cost.",
      "verification": "Compare resource settings, synthetic load, metrics, and events.",
      "evidence": {
        "path": "evidence/readiness/PR-056/capacity.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Platform owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10",
        "M15"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Capacity decisions have evidence and explicit uncertainty."
    },
    {
      "id": "PR-057",
      "category": "Capacity, performance, resource requests/limits, quotas, and cost",
      "question": "Are namespace quotas/limits configured where appropriate?",
      "risk": "Saturation, OOM behavior, or unbounded resources can degrade service or create avoidable cost.",
      "verification": "Inspect quota objects and test expected enforcement safely.",
      "evidence": {
        "path": "evidence/readiness/PR-057/quotas.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Platform owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Minor",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M07",
        "M15"
      ],
      "requirement_ids": [],
      "acceptance_criteria": [],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": false,
      "negative_test_result": "Not Run",
      "pass_condition": "Quota boundaries are documented/enforced where supported."
    },
    {
      "id": "PR-058",
      "category": "Capacity, performance, resource requests/limits, quotas, and cost",
      "question": "Are resource/cost labels and cleanup ownership defined?",
      "risk": "Saturation, OOM behavior, or unbounded resources can degrade service or create avoidable cost.",
      "verification": "Inspect labels and compare resource inventory with teardown list.",
      "evidence": {
        "path": "evidence/readiness/PR-058/labels.md",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Platform owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Minor",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M07",
        "M15",
        "M16"
      ],
      "requirement_ids": [
        "REQ-020"
      ],
      "acceptance_criteria": [
        "AC-011"
      ],
      "automation": "automated",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": false,
      "negative_test_result": "Not Run",
      "pass_condition": "Lab resources are attributable and have an owner/cleanup record."
    },
    {
      "id": "PR-059",
      "category": "Operations, on-call, incident response, runbooks, and support",
      "question": "Does each critical runbook include trigger, impact, prerequisites, diagnostics, decisions, recovery, verification, escalation, evidence?",
      "risk": "Operators may respond late or unsafely when ownership, diagnostics, escalation, and recovery steps are unclear.",
      "verification": "Review runbook and conduct tabletop walkthrough.",
      "evidence": {
        "path": "evidence/readiness/PR-059/runbook.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Operations owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10",
        "M11",
        "M13"
      ],
      "requirement_ids": [
        "REQ-015"
      ],
      "acceptance_criteria": [
        "AC-006"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Runbook is safe, scoped, ordered, and usable by another operator."
    },
    {
      "id": "PR-060",
      "category": "Operations, on-call, incident response, runbooks, and support",
      "question": "Are support boundaries, escalation, and communication expectations explicit?",
      "risk": "Operators may respond late or unsafely when ownership, diagnostics, escalation, and recovery steps are unclear.",
      "verification": "Review support record and owner walkthrough.",
      "evidence": {
        "path": "evidence/readiness/PR-060/support.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Operations owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10"
      ],
      "requirement_ids": [
        "REQ-032"
      ],
      "acceptance_criteria": [],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Responsibility, escalation, and solo role-play limits are explicit."
    },
    {
      "id": "PR-061",
      "category": "Operations, on-call, incident response, runbooks, and support",
      "question": "Is a controlled failure investigated using symptom, scope, change, hypothesis, test, result, next action?",
      "risk": "Operators may respond late or unsafely when ownership, diagnostics, escalation, and recovery steps are unclear.",
      "verification": "Review incident report and evidence captured before remediation.",
      "evidence": {
        "path": "evidence/readiness/PR-061/incident.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Incident reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M10",
        "M13"
      ],
      "requirement_ids": [
        "REQ-015"
      ],
      "acceptance_criteria": [
        "AC-006"
      ],
      "automation": "hybrid",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Evidence is preserved before mutation and investigation is reproducible."
    },
    {
      "id": "PR-062",
      "category": "Operations, on-call, incident response, runbooks, and support",
      "question": "Is a blameless review recorded with system causes and owned actions?",
      "risk": "Operators may respond late or unsafely when ownership, diagnostics, escalation, and recovery steps are unclear.",
      "verification": "Review postmortem and action owners/dates.",
      "evidence": {
        "path": "evidence/readiness/PR-062/postmortem.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Incident reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M10"
      ],
      "requirement_ids": [
        "REQ-015"
      ],
      "acceptance_criteria": [
        "AC-006"
      ],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Review addresses system conditions and trackable improvements."
    },
    {
      "id": "PR-063",
      "category": "Change management, release safety, rollback, and GitOps",
      "question": "Is GitOps the declared deployment path and desired-state revision identifiable?",
      "risk": "Undetected drift or unverified rollback can leave the wrong configuration or artifact serving traffic.",
      "verification": "Compare Git commit, Argo CD source/revision, and workload state.",
      "evidence": {
        "path": "evidence/readiness/PR-063/gitops.md",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Platform owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M02",
        "M08"
      ],
      "requirement_ids": [
        "REQ-004",
        "REQ-005"
      ],
      "acceptance_criteria": [
        "AC-002"
      ],
      "automation": "automated",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Declared Git source/revision matches reconciled workload state."
    },
    {
      "id": "PR-064",
      "category": "Change management, release safety, rollback, and GitOps",
      "question": "Is out-of-band drift detected/reconciled or surfaced according to policy?",
      "risk": "Undetected drift or unverified rollback can leave the wrong configuration or artifact serving traffic.",
      "verification": "Run benign scoped lab drift test after context preflight.",
      "evidence": {
        "path": "evidence/readiness/PR-064/drift.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Platform owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M08",
        "M10"
      ],
      "requirement_ids": [
        "REQ-005",
        "REQ-027",
        "REQ-031"
      ],
      "acceptance_criteria": [
        "AC-002"
      ],
      "automation": "hybrid",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Drift is detected and corrected or clearly reported."
    },
    {
      "id": "PR-065",
      "category": "Change management, release safety, rollback, and GitOps",
      "question": "Has rollback been executed through Git and verified against known-good artifact/config?",
      "risk": "Undetected drift or unverified rollback can leave the wrong configuration or artifact serving traffic.",
      "verification": "Revert disposable bad release; inspect Argo revision, runtime digest, smoke test.",
      "evidence": {
        "path": "evidence/readiness/PR-065/rollback.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Release owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M08",
        "M10"
      ],
      "requirement_ids": [
        "REQ-016"
      ],
      "acceptance_criteria": [
        "AC-007"
      ],
      "automation": "hybrid",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Git revert, desired state, runtime identity, and service test agree."
    },
    {
      "id": "PR-066",
      "category": "Change management, release safety, rollback, and GitOps",
      "question": "Are release approvals, change records, and rollback triggers declared?",
      "risk": "Undetected drift or unverified rollback can leave the wrong configuration or artifact serving traffic.",
      "verification": "Review release procedure and synthetic release decision.",
      "evidence": {
        "path": "evidence/readiness/PR-066/change.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Release owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M02",
        "M08",
        "M10"
      ],
      "requirement_ids": [
        "REQ-003",
        "REQ-032"
      ],
      "acceptance_criteria": [
        "AC-001",
        "AC-007"
      ],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Decision owner, trigger, scope, and recovery path are explicit."
    },
    {
      "id": "PR-067",
      "category": "Documentation, reproducibility, evidence quality, and governance",
      "question": "Has fresh-clone/clean-environment reproducibility been exercised?",
      "risk": "The result cannot be independently reproduced or audited when evidence is missing, stale, or untraceable.",
      "verification": "Clone to new directory and follow README/runbook only.",
      "evidence": {
        "path": "evidence/readiness/PR-067/fresh-clone.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Platform owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M02",
        "M07",
        "M16"
      ],
      "requirement_ids": [
        "REQ-021",
        "REQ-028",
        "REQ-029"
      ],
      "acceptance_criteria": [
        "AC-012"
      ],
      "automation": "hybrid",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Fresh clone completes selected preflight/bootstrap/verify/teardown without hidden state."
    },
    {
      "id": "PR-068",
      "category": "Documentation, reproducibility, evidence quality, and governance",
      "question": "Does each evidence record conform to Unit 1 index fields and point to redacted retained evidence?",
      "risk": "The result cannot be independently reproduced or audited when evidence is missing, stale, or untraceable.",
      "verification": "Validate `evidence/index.yaml` and inspect representative records.",
      "evidence": {
        "path": "evidence/readiness/PR-068/index.md",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Evidence recorder",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M02",
        "M12",
        "M16"
      ],
      "requirement_ids": [
        "REQ-023",
        "REQ-024",
        "REQ-026"
      ],
      "acceptance_criteria": [
        "AC-012"
      ],
      "automation": "automated",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Records use singular requirement_id and required provenance metadata."
    },
    {
      "id": "PR-069",
      "category": "Documentation, reproducibility, evidence quality, and governance",
      "question": "Does every applicable AC map to requirement, control/test, and evidence?",
      "risk": "The result cannot be independently reproduced or audited when evidence is missing, stale, or untraceable.",
      "verification": "Run Unit 1 traceability checker and inspect orphans.",
      "evidence": {
        "path": "evidence/readiness/PR-069/traceability.md",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Evidence recorder",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M02",
        "M16"
      ],
      "requirement_ids": [
        "REQ-022",
        "REQ-027"
      ],
      "acceptance_criteria": [
        "AC-012"
      ],
      "automation": "automated",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "No applicable AC or required evidence is orphaned/missing."
    },
    {
      "id": "PR-070",
      "category": "Documentation, reproducibility, evidence quality, and governance",
      "question": "Are human-review items supported by explicit reviewer attestations?",
      "risk": "The result cannot be independently reproduced or audited when evidence is missing, stale, or untraceable.",
      "verification": "Inspect reviewer identity/role/time/scope/decision/evidence/rationale.",
      "evidence": {
        "path": "evidence/readiness/PR-070/attestations.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Readiness reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M10",
        "M16"
      ],
      "requirement_ids": [
        "REQ-022",
        "REQ-023"
      ],
      "acceptance_criteria": [
        "AC-012"
      ],
      "automation": "manual",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Manual/hybrid judgement has a complete attestation; solo role-play is labelled."
    },
    {
      "id": "PR-071",
      "category": "Documentation, reproducibility, evidence quality, and governance",
      "question": "Are checklist version, item revisions, and material changes recorded?",
      "risk": "The result cannot be independently reproduced or audited when evidence is missing, stale, or untraceable.",
      "verification": "Inspect metadata, change history, and approval.",
      "evidence": {
        "path": "evidence/readiness/PR-071/version.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Checklist owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M10",
        "M16"
      ],
      "requirement_ids": [
        "REQ-032"
      ],
      "acceptance_criteria": [
        "AC-012"
      ],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Item semantics and policy changes are versioned and reviewable."
    },
    {
      "id": "PR-072",
      "category": "Documentation, reproducibility, evidence quality, and governance",
      "question": "Are assumptions, non-goals, waivers, residual risks, and conditions recorded?",
      "risk": "The result cannot be independently reproduced or audited when evidence is missing, stale, or untraceable.",
      "verification": "Review risk/assumption/waiver registers and expiry/approval.",
      "evidence": {
        "path": "evidence/readiness/PR-072/decision-register.md",
        "evidence_type": "review_record",
        "checksum": null
      },
      "owner": "Readiness reviewer",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Major",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M10",
        "M15",
        "M16"
      ],
      "requirement_ids": [
        "REQ-032"
      ],
      "acceptance_criteria": [
        "AC-012"
      ],
      "automation": "manual",
      "gate": false,
      "non_waivable": false,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Uncertainty is explicit; waivers do not silently pass blockers."
    },
    {
      "id": "PR-073",
      "category": "Teardown, residual-resource checks, and lab safety",
      "question": "Is teardown previewed, explicitly confirmed, scoped, and verified?",
      "risk": "Wrong-target operations or leftover resources and credentials can cause unintended changes, exposure, or cost.",
      "verification": "Review preview, approval, before/after inventory, cleanup record.",
      "evidence": {
        "path": "evidence/readiness/PR-073/teardown.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Platform owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M07",
        "M13",
        "M15"
      ],
      "requirement_ids": [
        "REQ-020"
      ],
      "acceptance_criteria": [
        "AC-011"
      ],
      "automation": "hybrid",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Only declared lab resources are removed and post-inventory reconciles."
    },
    {
      "id": "PR-074",
      "category": "Teardown, residual-resource checks, and lab safety",
      "question": "Are residual clusters, namespaces, volumes, registries, containers, credentials, and temp files checked?",
      "risk": "Wrong-target operations or leftover resources and credentials can cause unintended changes, exposure, or cost.",
      "verification": "Compare inventory and cleanup record with creation manifest.",
      "evidence": {
        "path": "evidence/readiness/PR-074/residual.md",
        "evidence_type": "hybrid_record",
        "checksum": null
      },
      "owner": "Platform owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M07",
        "M13",
        "M15"
      ],
      "requirement_ids": [
        "REQ-020"
      ],
      "acceptance_criteria": [
        "AC-011"
      ],
      "automation": "hybrid",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Every created resource is accounted for; no unexplained resource/credential remains."
    },
    {
      "id": "PR-075",
      "category": "Teardown, residual-resource checks, and lab safety",
      "question": "Do scripts refuse unexpected context and require opt-in for mutation/fault injection?",
      "risk": "Wrong-target operations or leftover resources and credentials can cause unintended changes, exposure, or cost.",
      "verification": "Run wrong-context negative tests and inspect explicit context/dry-run guards.",
      "evidence": {
        "path": "evidence/readiness/PR-075/lab-safety.md",
        "evidence_type": "automated_test",
        "checksum": null
      },
      "owner": "Platform owner",
      "profiles": [
        "data_service",
        "scheduled_pipeline",
        "ml_inference",
        "integrated_capstone"
      ],
      "profile_applicability": {
        "data_service": "required",
        "scheduled_pipeline": "required",
        "ml_inference": "required",
        "integrated_capstone": "required"
      },
      "severity": "Blocker",
      "status": "Not Run",
      "na_reason": null,
      "waiver": null,
      "evidence_timestamp": null,
      "last_relevant_change": null,
      "freshness_max_age_days": 30,
      "freshness_policy": "stale if older than configured age OR predates last relevant change; 30 days is a configurable example",
      "mapped_modules": [
        "M03",
        "M07",
        "M08",
        "M13"
      ],
      "requirement_ids": [
        "REQ-029",
        "REQ-031"
      ],
      "acceptance_criteria": [
        "AC-011",
        "AC-012"
      ],
      "automation": "automated",
      "gate": true,
      "non_waivable": true,
      "negative_test_required": true,
      "negative_test_result": "Not Run",
      "pass_condition": "Wrong/missing context and missing opt-in fail before mutation."
    }
  ]
}
```

#### 2.10.2 Python runner

The runner uses PyYAML; YAML parsing is not in Python's standard library. Pin the version selected for your project after checking current documentation. The example is conservative but not production-grade: it does not authenticate reviewers, verify remote locators, prove evidence truth, or protect against every hostile filesystem race.

```python
# File: readiness/run_readiness.py
from __future__ import annotations
import argparse, hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

STATUSES = {"Pass","Fail","N-A","Waived","Not Run","Unknown"}
SEVERITIES = {"Blocker","Major","Minor"}
AUTOMATION = {"automated","manual","hybrid"}
PROFILES = {"data_service","scheduled_pipeline","ml_inference","integrated_capstone"}
REQUIRED = {"id","category","question","risk","verification","evidence","owner","profiles",
"profile_applicability","severity","status","na_reason","waiver","evidence_timestamp",
"last_relevant_change","freshness_max_age_days","mapped_modules","requirement_ids",
"acceptance_criteria","automation","gate","non_waivable","negative_test_required",
"negative_test_result","pass_condition"}

def parse_time(value):
    if not isinstance(value,str) or not value.strip(): return None
    try: result = datetime.fromisoformat(value.replace("Z","+00:00"))
    except ValueError: return None
    return result.astimezone(timezone.utc) if result.tzinfo else None

def evidence_file(root, raw):
    if not isinstance(raw,str) or not raw.strip(): return None,"evidence path missing"
    p = Path(raw)
    if p.is_absolute() or ".." in p.parts: return None,"path must be relative and cannot contain '..'"
    base = root.resolve(); resolved = (base/p).resolve()
    if resolved != base and base not in resolved.parents: return None,"path escapes repository root"
    if not resolved.is_file(): return None,f"evidence file missing: {raw}"
    return resolved,None

def evaluate(doc, root, attestations=None, now=None):
    now = now or datetime.now(timezone.utc); attestations = attestations or {}
    findings=[]; seen=set(); counts={s:0 for s in STATUSES}; counts_by_severity={s:0 for s in SEVERITIES}; blocked=False; incomplete=False
    if not isinstance(doc,dict) or not isinstance(doc.get("items"),list):
        return {"result":"BLOCKED","findings":[{"item_id":None,"code":"SCHEMA","message":"root mapping/items list required","blocking":True}],"counts":counts,"counts_by_severity":counts_by_severity}
    if doc.get("profile") not in PROFILES:
        return {"result":"BLOCKED","findings":[{"item_id":None,"code":"INVALID_PROFILE","message":"root profile is missing or unsupported","blocking":True}],"counts":counts,"counts_by_severity":counts_by_severity}
    for i,row in enumerate(doc["items"]):
        if not isinstance(row,dict):
            findings.append({"item_id":str(i),"code":"SCHEMA","message":"item mapping required","blocking":True}); blocked=True; continue
        iid=row.get("id",f"items[{i}]")
        missing=REQUIRED-set(row)
        if missing:
            findings.append({"item_id":iid,"code":"SCHEMA","message":f"missing {sorted(missing)}","blocking":True}); blocked=True; continue
        if iid in seen:
            findings.append({"item_id":iid,"code":"DUPLICATE_ID","message":"duplicate ID","blocking":True}); blocked=True
        seen.add(iid)
        status=row["status"]; sev=row["severity"]; auto=row["automation"]
        if status not in STATUSES:
            findings.append({"item_id":iid,"code":"INVALID_STATUS","message":str(status),"blocking":True}); blocked=True; continue
        counts[status]+=1
        if sev not in SEVERITIES or auto not in AUTOMATION:
            findings.append({"item_id":iid,"code":"INVALID_ENUM","message":"invalid severity or automation","blocking":True}); blocked=True; continue
        counts_by_severity[sev]+=1
        if not isinstance(row["profiles"],list) or any(p not in PROFILES for p in row["profiles"]):
            findings.append({"item_id":iid,"code":"INVALID_PROFILE","message":"invalid profile","blocking":True}); blocked=True; continue
        app_map=row["profile_applicability"]
        if not isinstance(app_map,dict) or any(v not in {"required","conditional","na_allowed"} for v in app_map.values()):
            findings.append({"item_id":iid,"code":"INVALID_APPLICABILITY","message":"profile_applicability must map profiles to required/conditional/na_allowed","blocking":True}); blocked=True; continue
        if status=="N-A":
            if not isinstance(row["na_reason"],str) or not row["na_reason"].strip():
                findings.append({"item_id":iid,"code":"NA_REASON","message":"N-A requires a reason","blocking":True}); blocked=True; continue
            selected=doc.get("profile")
            applicability=app_map.get(selected)
            if selected not in row.get("profiles",[]) or applicability not in {"conditional","na_allowed"}:
                findings.append({"item_id":iid,"code":"NA_NOT_ALLOWED","message":"selected profile requires this item; N-A is not allowed","blocking":True}); blocked=True; continue
            if sev=="Blocker" or row["gate"]:
                att=attestations.get(iid)
                if not isinstance(att,dict) or att.get("decision")!="N-A" or not att.get("reviewer") or not parse_time(att.get("timestamp")) or not att.get("rationale"):
                    findings.append({"item_id":iid,"code":"NA_REVIEW_MISSING","message":"Blocker/gated N-A requires reviewer attestation","blocking":True}); blocked=True
            continue
        if status=="Waived":
            w=row["waiver"]; need={"owner","approver","rationale","compensating_control","created_at","expires_at","evidence"}
            if row["non_waivable"]:
                findings.append({"item_id":iid,"code":"NON_WAIVABLE","message":"cannot waive non-waivable control","blocking":True}); blocked=True; continue
            if not isinstance(w,dict) or need-set(w) or any(not str(w.get(k,"")).strip() for k in need):
                findings.append({"item_id":iid,"code":"WAIVER_INCOMPLETE","message":"incomplete waiver metadata","blocking":True}); blocked=True; continue
            expiry=parse_time(w["expires_at"])
            if expiry is None or expiry<=now:
                findings.append({"item_id":iid,"code":"WAIVER_EXPIRED","message":"expired/invalid waiver expiry","blocking":True}); blocked=True
            # A complete, unexpired waiver is presented for human review; it is never counted as Pass.
            continue
        if status=="Fail":
            is_blocker=sev=="Blocker" or row["gate"] or row["non_waivable"]
            findings.append({"item_id":iid,"code":"CONTROL_FAILED","message":"control failed","blocking":bool(is_blocker)})
            blocked=blocked or is_blocker; incomplete=True; continue
        if status in {"Not Run","Unknown"}:
            is_blocker=sev=="Blocker" or row["gate"]
            findings.append({"item_id":iid,"code":"NOT_DEMONSTRATED","message":status+" is not Pass","blocking":bool(is_blocker)})
            blocked=blocked or is_blocker; incomplete=True; continue
        ev=row["evidence"]
        if not isinstance(ev,dict):
            findings.append({"item_id":iid,"code":"EVIDENCE_SCHEMA","message":"Pass requires evidence mapping","blocking":True}); blocked=True; continue
        path,error=evidence_file(root,ev.get("path"))
        if error:
            findings.append({"item_id":iid,"code":"EVIDENCE_MISSING","message":error,"blocking":True}); blocked=True; continue
        checksum=ev.get("checksum")
        if checksum:
            if not isinstance(checksum,str) or not re.fullmatch(r"sha256:[0-9a-fA-F]{64}",checksum):
                findings.append({"item_id":iid,"code":"CHECKSUM_FORMAT","message":"expected sha256:<64 hex>","blocking":True}); blocked=True; continue
            actual=hashlib.sha256(path.read_bytes()).hexdigest()
            if actual.lower()!=checksum.split(":",1)[1].lower():
                findings.append({"item_id":iid,"code":"CHECKSUM_MISMATCH","message":"evidence bytes differ","blocking":True}); blocked=True; continue
        evtime=parse_time(row["evidence_timestamp"])
        age=row["freshness_max_age_days"]
        if evtime is None or not isinstance(age,(int,float)) or age<0:
            findings.append({"item_id":iid,"code":"FRESHNESS_METADATA","message":"invalid timestamp/age","blocking":True}); blocked=True; continue
        stale=(now-evtime).total_seconds()>age*86400
        if row["last_relevant_change"]:
            changed=parse_time(row["last_relevant_change"])
            if changed is None:
                findings.append({"item_id":iid,"code":"CHANGE_TIME","message":"invalid change timestamp","blocking":True}); blocked=True; continue
            stale=stale or evtime<changed
        if stale:
            critical=sev=="Blocker" or row["gate"]
            findings.append({"item_id":iid,"code":"STALE_EVIDENCE","message":"age/change policy says stale","blocking":bool(critical)})
            blocked=blocked or critical; incomplete=True; continue
        if row["negative_test_required"] and row["negative_test_result"]!="Pass":
            critical=sev=="Blocker" or row["gate"]
            findings.append({"item_id":iid,"code":"NEGATIVE_TEST","message":"required negative test not passed","blocking":bool(critical)})
            blocked=blocked or critical; incomplete=True; continue
        if auto in {"manual","hybrid"}:
            att=attestations.get(iid); need={"reviewer","role","timestamp","scope","decision","evidence_refs","rationale"}
            if not isinstance(att,dict) or need-set(att) or any(not str(att.get(k,"")).strip() for k in need):
                findings.append({"item_id":iid,"code":"ATTESTATION_MISSING","message":"manual/hybrid Pass requires complete attestation","blocking":True}); blocked=True; continue
            if att["decision"]!="Pass" or parse_time(att["timestamp"]) is None:
                findings.append({"item_id":iid,"code":"ATTESTATION_INVALID","message":"attestation decision/time invalid","blocking":True}); blocked=True
    result="BLOCKED" if blocked else ("INCOMPLETE" if incomplete or counts["Fail"] or counts["Not Run"] or counts["Unknown"] else "READY_FOR_HUMAN_REVIEW")
    return {"result":result,"counts":counts,"counts_by_severity":counts_by_severity,
            "item_count":len(doc["items"]),"findings":findings,
            "notice":"Validation is not a launch decision and does not prove evidence truthfulness."}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--checklist",default="readiness/checklist.yaml")
    ap.add_argument("--repo-root",default=".")
    ap.add_argument("--attestations",default="readiness/attestations.json")
    ap.add_argument("--report",default="evidence/readiness/readiness-report.json")
    args=ap.parse_args(); root=Path(args.repo_root).resolve()
    try: doc=yaml.safe_load((root/args.checklist).read_text(encoding="utf-8"))
    except (OSError,yaml.YAMLError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 2
    try:
        f=root/args.attestations; attest=json.loads(f.read_text()) if f.exists() else {}
    except (OSError,json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr); return 2
    report=evaluate(doc,root,attest); report["generated_at"]=datetime.now(timezone.utc).isoformat()
    findings=report.get("findings",[])
    report["blockers"]=[f for f in findings if f.get("blocking")]
    report["stale_evidence"]=[f for f in findings if f.get("code")=="STALE_EVIDENCE"]
    report["expired_waivers"]=[f for f in findings if f.get("code")=="WAIVER_EXPIRED"]
    report["missing_evidence"]=[f for f in findings if f.get("code")=="EVIDENCE_MISSING"]
    report["manual_attestations_awaiting_review"]=[f.get("item_id") for f in findings if f.get("code")=="ATTESTATION_MISSING"]
    report["checklist_version"]=doc.get("schema_version") if isinstance(doc,dict) else None
    report["profile"]=doc.get("profile") if isinstance(doc,dict) else None
    report["scope"]=doc.get("scope") if isinstance(doc,dict) else None
    report["counts_by_severity"]=report.get("counts_by_severity",{})
    report["commit_sha"]=doc.get("commit_sha") if isinstance(doc,dict) else None
    report["artifact_digest"]=doc.get("artifact_digest") if isinstance(doc,dict) else None
    dest=root/args.report; dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(f"Items: {report.get('item_count',0)} | Result: {report['result']} | Findings: {len(report['findings'])}")
    for f in report["findings"]: print(f"- {f['item_id']} [{f['code']}] {f['message']}")
    print("Human launch decision: NOT MADE — reviewer sign-off required.")
    return 0 if report["result"]=="READY_FOR_HUMAN_REVIEW" else 1

if __name__=="__main__": raise SystemExit(main())
```

#### 2.10.3 Tests with planted defects

Save as `readiness/tests/test_readiness.py`. These tests use synthetic temporary files and do not need a live cluster.

```python
# File: readiness/tests/test_readiness.py
import tempfile, unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from run_readiness import evaluate

NOW=datetime(2026,11,4,12,0,tzinfo=timezone.utc)

def make_item(**kw):
    x={"id":"PR-T-001","category":"test","question":"synthetic","risk":"synthetic",
    "verification":"unit test","evidence":{"path":"evidence/test.txt","checksum":None},
    "owner":"test-owner","profiles":["integrated_capstone"],
    "profile_applicability":{"integrated_capstone":"required"},"severity":"Major","status":"Pass",
    "na_reason":None,"waiver":None,"evidence_timestamp":(NOW-timedelta(hours=1)).isoformat(),
    "last_relevant_change":(NOW-timedelta(days=1)).isoformat(),"freshness_max_age_days":30,
    "mapped_modules":["M02"],"requirement_ids":["REQ-001"],"acceptance_criteria":["AC-001"],
    "automation":"automated","gate":False,"non_waivable":False,"negative_test_required":False,
    "negative_test_result":"Not Run","pass_condition":"synthetic fixture passes"}
    x.update(kw); return x

class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        (self.root/"evidence").mkdir(); (self.root/"evidence/test.txt").write_text("synthetic")
    def tearDown(self): self.tmp.cleanup()
    def check(self,row,att=None):
        return evaluate({"schema_version":"1","items":[row]},self.root,att or {},NOW)

    def test_01_valid_fresh_pass(self):
        self.assertEqual(self.check(make_item())["result"],"READY_FOR_HUMAN_REVIEW")
    def test_02_pass_missing_evidence(self):
        r=self.check(make_item(evidence={"path":"evidence/missing","checksum":None}))
        self.assertEqual(r["result"],"BLOCKED")
    def test_03_stale_after_change(self):
        r=self.check(make_item(gate=True,last_relevant_change=(NOW-timedelta(minutes=1)).isoformat()))
        self.assertEqual(r["result"],"BLOCKED")
    def test_04_expired_waiver(self):
        w={"owner":"o","approver":"a","rationale":"r","compensating_control":"c",
        "created_at":"2026-11-01T00:00:00Z","expires_at":"2026-11-03T00:00:00Z","evidence":"ev"}
        self.assertEqual(self.check(make_item(status="Waived",waiver=w))["result"],"BLOCKED")
    def test_05_na_without_reason(self):
        self.assertEqual(self.check(make_item(status="N-A"))["result"],"BLOCKED")
    def test_06_duplicate_id(self):
        r=evaluate({"items":[make_item(),make_item()]},self.root,{},NOW)
        self.assertEqual(r["result"],"BLOCKED")
    def test_07_manual_missing_attestation(self):
        self.assertEqual(self.check(make_item(automation="manual"))["result"],"BLOCKED")
    def test_08_blocker_fail(self):
        self.assertEqual(self.check(make_item(status="Fail",severity="Blocker",gate=True))["result"],"BLOCKED")
    def test_09_invalid_status(self):
        self.assertEqual(self.check(make_item(status="LooksGood"))["result"],"BLOCKED")
    def test_10_invalid_severity(self):
        self.assertEqual(self.check(make_item(severity="Critical-ish"))["result"],"BLOCKED")
    def test_11_unknown_not_pass(self):
        self.assertEqual(self.check(make_item(status="Unknown"))["result"],"INCOMPLETE")
    def test_12_negative_test_failure(self):
        self.assertEqual(self.check(make_item(gate=True,negative_test_required=True,negative_test_result="Fail"))["result"],"BLOCKED")
    def test_13_checksum_mismatch(self):
        r=self.check(make_item(evidence={"path":"evidence/test.txt","checksum":"sha256:"+"0"*64}))
        self.assertEqual(r["result"],"BLOCKED")
    def test_14_path_traversal(self):
        r=self.check(make_item(evidence={"path":"../outside","checksum":None}))
        self.assertEqual(r["result"],"BLOCKED")
    def test_15_non_waivable_cannot_be_waived(self):
        w={"owner":"o","approver":"a","rationale":"r","compensating_control":"c",
        "created_at":"2026-11-01T00:00:00Z","expires_at":"2026-11-10T00:00:00Z","evidence":"ev"}
        self.assertEqual(self.check(make_item(status="Waived",non_waivable=True,waiver=w))["result"],"BLOCKED")
    def test_16_manual_with_attestation(self):
        att={"PR-T-001":{"reviewer":"reviewer-1","role":"reviewer","timestamp":NOW.isoformat(),
        "scope":"synthetic","decision":"Pass","evidence_refs":["evidence/test.txt"],"rationale":"reviewed"}}
        self.assertEqual(self.check(make_item(automation="manual"),att)["result"],"READY_FOR_HUMAN_REVIEW")
    def test_17_na_rejected_when_profile_requires_item(self):
        row=make_item(status="N-A",na_reason="not used")
        self.assertEqual(self.check(row)["result"],"BLOCKED")
    def test_18_na_allowed_for_conditional_profile_with_reason(self):
        row=make_item(status="N-A",na_reason="no inbound endpoint",
                      profile_applicability={"integrated_capstone":"conditional"},severity="Minor",gate=False)
        self.assertEqual(self.check(row)["result"],"READY_FOR_HUMAN_REVIEW")

if __name__=="__main__": unittest.main()
```

Run:
```bash
PYTHONPATH=readiness python -m unittest discover -s readiness/tests -v
```

Expected coverage is 18 tests: fresh Pass; missing evidence; stale evidence; expired waiver; N-A without reason; duplicate ID; missing manual attestation; Blocker Fail; invalid status; invalid severity; Unknown; negative-test failure; checksum mismatch; path traversal; non-waivable waiver; valid manual attestation. This is a test plan/code listing, not a claim that tests were executed.

#### 2.10.4 Report contract

The JSON report includes a runtime-generated timestamp, checklist version, profile/scope, commit SHA/artifact digest where available, counts by status and severity, blockers/findings, stale/expired/missing evidence, manual attestations awaiting review, and final result: `INCOMPLETE`, `BLOCKED`, or `READY_FOR_HUMAN_REVIEW`.

```json
{
  "generated_at": "<runtime-generated UTC timestamp>",
  "checklist_version": "1",
  "profile": "integrated_capstone",
  "scope": "synthetic local lab",
  "commit_sha": "<actual commit SHA if supplied>",
  "artifact_digest": "<actual digest if supplied>",
  "item_count": 75,
  "counts_by_severity": {"Blocker": 23, "Major": 44, "Minor": 8},
  "counts": {"Pass": 0, "Fail": 0, "N-A": 0, "Waived": 0, "Not Run": 75, "Unknown": 0},
  "blockers": [],
  "stale_evidence": [],
  "expired_waivers": [],
  "missing_evidence": [],
  "manual_attestations_awaiting_review": [],
  "findings": [{"item_id":"PR-001","code":"NOT_DEMONSTRATED","message":"Not Run is not Pass","blocking":false}],
  "result": "INCOMPLETE",
  "notice": "Validation is not a launch decision and does not prove evidence truthfulness."
}
```

**Representative example — your output will differ.** The 23/44/8 severity counts describe the authored checklist template, not a test run. The status counts show the untouched template's 75 `Not Run` records. Never print `PRODUCTION READY` or `GO`. Exit code zero means only “ready for human review,” not approved for launch.

### 2.11 Hands-on lab set

All labs use synthetic data and local resources. No cloud, public endpoint, paid service, GPU, or real credential is required. Measure your own footprint. Use Cap-Core first; do not run every heavy component simultaneously.

**Shared Kubernetes preflight (read-only)**

```bash
kubectl --context kind-m17-lab cluster-info >/dev/null || { echo "Lab context unavailable; abort" >&2; exit 2; }
kubectl --context kind-m17-lab get namespace m17-app
kubectl --context kind-m17-lab get pods -n m17-app -o wide
```

Before mutation, confirm context, namespace, workload ownership, and cleanup boundary; inspect/dry-run first; require explicit opt-in; abort if uncertain.

#### LAB-PR-01 — Establish the service scope and readiness contract

- **Goal:** define owner, dependencies, profile, SLI/SLO placeholders, non-goals, and evidence references.
- **Prerequisites:** M01–M16 outcomes; repository; no cluster required.
- **Steps:** choose a profile; record user outcome/owner/dependencies/trust boundaries/failure modes; define SLI numerator/denominator/window/target placeholder/exclusions; map PR items to Unit 1 REQ/AC; identify optional Awareness components.
- **Expected evidence:** scope record, dependency inventory, architecture diagram, applicability map, initial traceability map.
- **Cleanup:** no cluster resources; retain versioned records or remove temporary drafts.
- **Stretch:** compare data-service and pipeline profiles.
- **Common failures:** no owner/non-goals; uptime-only SLI; N-A used for difficult controls.
- **Acceptance:** reviewer can identify scope/profile/owner/dependencies/objectives without undocumented context. Human judgement is required for criticality.

#### LAB-PR-02 — Complete and verify the checklist

- **Goal:** apply all items to one profile and record evidence honestly.
- **Prerequisites:** LAB-PR-01; Cap-Core or a documented subset; synthetic workload.
- **Steps:** set profile/scope in YAML; inspect every item; collect actual evidence or mark Not Run; record justified N-A and complete waivers; bind evidence to commit/digest/time/run ID; run validator; review all findings.
- **Expected evidence:** completed checklist, Unit 1-compatible evidence index, rationale, blocker/waiver/N-A/not-demonstrated list.
- **Cleanup:** redact before commit; securely remove temporary raw outputs.
- **Stretch:** apply a second profile.
- **Common failures:** Pass without evidence; stale evidence; N-A without reason; waiver without expiry.
- **Acceptance:** every applicable item has a defensible status; a planted invalid Pass is caught. Automated checks and human judgement remain separate.

#### LAB-PR-03 — Implement the automated readiness runner

- **Goal:** validate YAML, run planted-defect tests, and produce JSON.
- **Prerequisites:** LAB-PR-02; Python 3; PyYAML.
- **Steps:** save runner/tests in implementation repository; record versions; run unit tests; create fresh Pass fixture; remove evidence and rerun; test stale timestamp, expired waiver, and missing attestation; inspect report.
- **Expected evidence:** runner revision, dependency record, test output, JSON report, planted-defect report.
- **Cleanup:** tests use temporary directories; retain test code and redacted output.
- **Stretch:** add symlink-escape and profile-applicability tests.
- **Common failures:** assuming stdlib parses YAML; unpinned dependency; ignoring missing files; auto-passing manual items.
- **Acceptance:** positive fixture reaches READY_FOR_HUMAN_REVIEW; missing evidence cannot pass; Unknown remains incomplete; failed gate blocks. No cluster needed.

#### LAB-PR-04 — Run a launch review

- **Goal:** inspect synthetic flaws, rerun a sample, classify findings, and sign off.
- **Prerequisites:** Labs 1–3; second person or labelled solo role-play.
- **Steps:** use the ten flawed cases in L4; confirm scope/profile/commit/digest/version; inspect index/freshness; choose a recorded 20% example sample; rerun from fresh checkout; review blockers/waivers/N-A/residual risks; record decision and follow-up.
- **Expected evidence:** agenda, sample list, rerun results, findings register, attestations, decision record.
- **Cleanup:** no cluster mutation; use fictional reviewer labels.
- **Stretch:** repeat with another reviewer and calibrate.
- **Common failures:** averaging opinions; treating dashboard reachability as alert proof; waiver as Pass; stale evidence ignored.
- **Acceptance:** decision cites item IDs/evidence; unresolved blockers prevent Go; solo role-play is not independent approval.

### 2.12 Evidence artifacts

Expected unit evidence:
- versioned checklist definition and version;
- per-item statuses and rationale;
- evidence index aligned to Unit 1;
- runner JSON report and test output;
- proof the runner catches stale evidence, expired waiver, missing evidence, N-A, missing attestation, and negative-test failures;
- reviewer notes and signed-off readiness decision;
- blockers, waivers, N-A, residual risks, owners, due dates;
- checklist item → Unit 1 REQ/AC → control → test → evidence;
- commit SHA, artifact digest, timestamps, run/drill IDs where available;
- redaction and retention notes;
- explicit “not demonstrated” section.

Unit 1's evidence index uses root `schema_version` and `evidence` list; each record has singular `requirement_id`, `evidence_id`, `path` or retained reference, `evidence_type`, `timestamp_utc`, source commit/run/digest, checksum where applicable, `verification_method`, `result`, and `owner`. Do not change it to plural `requirement_ids`.

```yaml
# File: evidence/index.yaml
schema_version: "1"
evidence:
  - evidence_id: EVD-PR-006
    requirement_id: REQ-001
    path: evidence/readiness/PR-006/ci.json
    evidence_type: automated_test
    timestamp_utc: "<actual timezone-aware UTC timestamp>"
    source_commit: "<actual source commit SHA>"
    run_id: "<actual run identifier>"
    artifact_digest: "sha256:<actual digest>"
    checksum: "sha256:<actual evidence checksum>"
    verification_method: "Inspect required CI jobs and compare artifact identity"
    result: PASS
    owner: "CI owner"
    notes: "Synthetic lab evidence; redact sensitive values."
```

Placeholders are not evidence. Commit small redacted text artifacts and reproducibility scripts. Retain large artifacts safely with locator, access method, owner, retention period, and integrity metadata. Never commit credentials, tokens, private keys, production data, personal data, account IDs, credential-bearing kubeconfigs, or unredacted logs. Preserve failures when redacting.

### 2.13 Common review-board questions

Exactly five:

1. **What evidence supports the go/no-go recommendation?**  
   Cite scope/profile/commit/digest/checklist version, item results, evidence index, freshness, test outputs, incident/rollback/restore/alert/teardown proof, blockers, waivers, N-A reasons, and residual risks. Score is supplementary.

2. **How do you know evidence matches deployed artifact/configuration?**  
   Compare source SHA, CI run, registry digest, GitOps revision, runtime digest, deployment timestamp, and evidence timestamp. Rerun a reviewer-selected sample from a fresh checkout. Evidence predating a relevant change is stale.

3. **What if restore, alert, or rollback drill fails?**  
   Stop the readiness decision for the affected critical scope. Preserve failure evidence, record impact/owner/recovery/retest criteria, and do not relabel a workaround as Pass. Required recovery gates block the capstone pass rule.

4. **How are waivers, N-A, and stale evidence controlled?**  
   N-A needs profile-specific reason and approval where required. Waiver needs owner/approver/rationale/impact/compensating control/evidence/expiry/reassessment. Expired waivers fail. Stale means older than configured age or predating relevant change. Neither counts as Pass.

5. **What does the local lab prove—and not prove?**  
   It proves reproducible local mechanics, control application, safe failure/recovery exercises, evidence validation, and ability to defend a lab-scale decision. It does not prove real traffic capacity, cloud limits, multi-region resilience, enterprise identity/compliance, or production availability.

### 2.14 Sources and verification notes

**Reviewed primary artifacts**
- Attached `Pasted markdown(20261104-072228).md`: Unit 2 scope, exact heading order, 75-item requirement, profiles, runner/tests, labs, reviewer exercises, and audit requirements.
- Latest `PROMPT-Production-DevOps-Integrated-Capstone(4).md`: M17 unit order, local-first/zero-budget constraints, stack profiles, stage contract, fidelity caveat, and M01–M16 handoffs.
- `Roadmap(20261104-055747).md`: actual Stage 2E/M17 tree and Unit 2 target filename.
- Latest `capstone-requirements(1).md`: REQ-001–REQ-032, AC-001–AC-012, evidence index, traceability, reproducibility, and pass rule.
- Latest `incident-and-recovery-rubric(1).md`: recovery terminology; its REQ crosswalk conflicts with latest Unit 1 and is not copied.
- Latest `cost-and-reliability-rubric(1).md`: SLO, alert, freshness, capacity, cost, and evidence terminology.
- Latest `platform-and-delivery-rubric(1).md`: GitOps, digest, teardown, fresh-clone, and canonical Unit 1 crosswalk; it also records the Unit 3 discrepancy.

**Version-sensitive verification**
- kind/kubectl: installed versions, context, supported flags, namespace, and cluster behavior — official kind and Kubernetes references.
- Helm/Kustomize: selected version, render/validation syntax, API compatibility — official Helm/Kustomize references.
- Argo CD: application source/revision/status, sync/drift/rollback — official Argo CD docs.
- Prometheus/`promtool`: rule syntax, test command, alert state — official Prometheus docs.
- Grafana: dashboard provisioning, query syntax, retention — official Grafana docs.
- GitHub Actions: required checks, permissions, action pinning, workflow semantics — official GitHub Actions docs.
- PyYAML: parser version and safe loading — PyYAML docs.
- cosign/policy engines: signature/provenance and local fidelity — official Sigstore/cosign, Kyverno/Gatekeeper docs.
- Backup tooling: exact commands, consistency guarantees, PostgreSQL restore verification — selected tool and PostgreSQL docs.

No exact versions or live runtime results are claimed. Verify version-sensitive syntax before execution. Local CI emulation, policy engines, signatures, and network policy depend on selected versions/configuration.

**Optional cloud gate:** real cloud is optional and requires separate approval plus resource diagram/list; account/region assumptions without account IDs; preflight; cost-risk table; redacted budget/alert evidence; written teardown contract; proof of resource removal; next-day cost check with billing-delay note. No cloud resource is required to look production-like. Budgets are alerts, not hard caps.

### 2.15 Final self-review and sign-off

**Self-check questions**

1. Backup exists, no restore: Pass? **No.** Restore and integrity must be demonstrated.
2. Evidence is two days old but predates yesterday's config change: fresh? **No.** Change-bound staleness invalidates it.
3. Pipeline has no inbound endpoint; ingress/TLS N-A? **Potentially valid** with architecture evidence and reviewer approval.
4. Waiver has no expiry: acceptable? **No.** Incomplete waiver; it cannot pass.
5. Checklist is 96% Pass but restore-integrity blocker failed: Go? **No.** Blocker cannot be averaged away.
6. Manual item has evidence but no reviewer record: auto-pass? **No.** Attestation is required.
7. ML inference has no GPU: N-A? **Yes** for GPU-specific need; model digest, CPU/memory sizing, synthetic load, latency/error, and rollback still apply.
8. Dashboard opens but workload query is empty: Pass? **No** if pass condition requires useful workload symptom signals. Apply item definition, not reviewer preference.

**Decision record template**

```text
# File: evidence/readiness/decision-record.md
Checklist version:
Project profile and scope:
Environment:
Service owner:
Reviewer/approver:
Operations reviewer:
Security reviewer:
Evidence recorder:
Source commit SHA:
Artifact digest(s):
GitOps revision:
Decision date/time/timezone:
Decision: Go | Go with conditions | No-Go
Blockers / Major / Minor:
N-A items and reasons:
Waivers, approvers, expiry:
Stale / Not Run / Unknown / Not Demonstrated:
Reviewer spot-check sample/results:
Incident / alert / rollback / restore / teardown / fresh-clone evidence:
Residual risks:
Conditions, owners, due dates:
Post-launch review date/window:
Solo role-play / independence limitation:
Rationale:
```

**Authoring audit**

| Check | Result | Evidence/notes |
|---|---|---|
| Target name and Unit 2 scope | PASS | One standalone `production-readiness-checklist.md` deliverable. |
| Verbatim M17 contract | PASS | Stage exit, evidence artifact set, pass rule reproduced verbatim. |
| Local-first profiles and fidelity | PASS | Cap-Core/Cap+Security/Cap+Chaos, footprint, cloud gate, and lab limits included. |
| M01–M16 mapping | PASS | Required module handoffs represented. |
| Required headings 2.0–2.15 | PASS | Present in order. |
| Checklist count | PASS | 75 unique PR IDs. |
| Item metadata | PASS | Human and machine records include required fields. |
| Four profiles | PASS | Required/conditional/N-A rules documented. |
| Unit 1 REQ/AC alignment | PASS | Latest canonical Unit 1 mapping used; evidence index retains singular `requirement_id`. |
| Unit 3 mapping discrepancy | OPEN SOURCE DEFECT | Unit 3's available crosswalk conflicts with Unit 1; Unit 2 follows Unit 1. Unit 3 not modified. |
| YAML representation | PASS — CONTENT INCLUDED | All 75 items represented as JSON-form YAML 1.2. Parser validation remains. |
| Runner/tests | PASS — STATIC REVIEW ONLY | Runner and 16 test cases included; not executed in learner's target environment. |
| Runtime tests | NOT EXECUTED | No PyYAML/runner/test/cluster/CI/alert/restore/drill execution is claimed. |
| Kubernetes safety | PASS — STATIC REVIEW | Every kubectl command explicitly names `--context kind-m17-lab`; verify actual namespace/tool versions before mutation. |
| Repository write | NOT PERFORMED | Standalone output only; no roadmap repository files were modified by this authoring task. |
| External version verification | NOT VERIFIED | No exact tool versions asserted; consult current official docs before running. |

This authoring audit is not an ORR, runtime test report, or production approval. The learner must execute the tests, verify current tool syntax, run selected labs, inspect evidence, and obtain human review.

**Final fidelity statement:** a laptop `kind` cluster demonstrates mechanics, repeatability, and evidence discipline. It does not demonstrate real multi-region behavior, real cloud limits, real production traffic, or end-to-end production readiness. A passing capstone proves the learner can produce and defend evidence at lab scale, nothing more.
