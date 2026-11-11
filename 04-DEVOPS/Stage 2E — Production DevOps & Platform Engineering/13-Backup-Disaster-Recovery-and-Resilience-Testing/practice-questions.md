# M13 — Practice Questions: Backup, Disaster Recovery, and Resilience Testing

**Stage:** Stage 2E — Production DevOps & Platform Engineering  
**Module:** `13-Backup-Disaster-Recovery-and-Resilience-Testing/`
(M13)  
**Unit:** Unit 11 — Practice questions  
**Target file:** `practice-questions.md`

> **Source and scope note.** This bank follows the Unit 11 contract and
> the Unit 1–10 titles and filenames in the supplied prompt and the
> available syllabus search results. The authoritative syllabus names
> M13 and the 13-unit sequence. A full repository project-tree snapshot
> and every Unit 1–10 lesson were not directly available for inspection
> in this turn; therefore questions stay within the supplied syllabus
> outcomes and avoid undocumented implementation details.
> Version-sensitive Velero, Chaos Mesh, LitmusChaos, Kubernetes, and
> policy-engine behavior is framed as a verification task rather than
> asserted as universal. All sample artifacts are illustrative, not
> executed measurements.

## How to use this bank

Attempt each question before reading its model answer. Record answer and
confidence separately; review high-confidence errors first. For MCQs,
explain every distractor. For artifacts, state what is proven, what is
unknown, and what evidence closes the gap. For incident scenarios, use
**symptom → first action → decide → execute → verify → communicate →
prevent**. Use only synthetic data, fake credentials, and throwaway lab
resources; never run destructive actions against production, shared
clusters, real customer data, or real SaaS dependencies.

## Levels, scoring, and remediation

- **L1 — Beginner:** terminology, fundamentals, basic interpretation,
  safe first decisions.
- **L2 — Practitioner:** operational choices, calculations, runbooks,
  artifact interpretation.
- **L3 — Advanced:** multi-system dependencies, security, failure
  analysis, incident decisions.
- **L4 — Expert:** trade-offs under uncertainty, cross-system
  consistency, governance, failure-domain reasoning, program design.

Scoring: **≥ 80% proceed; 60–79% remediate; \< 60% repeat** the unit
question set. A score is a learning gate, not proof of production
readiness. Justify decisions, state assumptions, and identify missing
evidence; do not merely match model-answer wording.

## Question-count manifest

| Section                          |      Required | Included |
|----------------------------------|--------------:|---------:|
| Unit questions                   | 16 × 10 = 160 |      160 |
| Cross-unit integration           |    exactly 40 |       40 |
| Numbered questions               |  at least 200 |      200 |
| Additional design-review prompts |    exactly 16 |       16 |

## Glossary

\| RTO \| Recovery Time Objective: agreed maximum tolerable recovery
time. \| \| RPO \| Recovery Point Objective: agreed maximum tolerable
data-loss interval. \| \| RTA \| Recovery Time Actual: observed time to
the defined usable-service endpoint. \| \| RPA \| Recovery Point Actual:
age of the newest verified, consistent recoverable business state at
failure. \| \| BIA \| Business Impact Analysis. \| \| PITR \|
Point-in-time recovery to a selected recoverable time/transaction
boundary. \| \| WAL \| Write-ahead log, a database transaction log used
by some recovery designs. \| \| SLI/SLO \| Service Level Indicator /
Service Level Objective. \| \| DR \| Disaster recovery. \| \| CR/CRD \|
Kubernetes Custom Resource / Custom Resource Definition. \| \| PV/PVC \|
PersistentVolume / PersistentVolumeClaim. \| \| GitOps \| Reconciliation
of version-controlled desired state into a running environment. \| \|
Idempotency \| Repeated operation yields the same intended result
without duplicating effects. \| \| Watermark \| Pipeline
progress/completeness marker, often based on event time. \| \| Fencing
\| Prevents an old or isolated primary from continuing authoritative
writes. \| \| Canary \| Small end-to-end check validating service
behavior. \| \| BSL \| Velero BackupStorageLocation concept; verify
exact API/version for the pinned release. \| \| CSI/FSB \| Container
Storage Interface / file-system backup path; support is
environment/version dependent. \| \| Fallback ratio \| Fraction of
requests served by a fallback model/path rather than the primary path.
\| \| RCA \| Root-cause analysis; keep it blameless and evidence-based.
\|

## Unit 1 — Recovery time and recovery point objectives

**Target file:** `01-recovery-time-and-recovery-point-objectives.md`  
**Learning objectives:** RTO versus RTA, RPO versus RPA,
dependency-implied objectives.

### Conceptual short answer (3 questions)

### U01-SA-01

- **Question ID:** `U01-SA-01`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L1
- **Objective tested:** RTO versus RTA
- **Estimated time:** 5 minutes
- **Question/prompt:** A service has a 60-minute RTO target. Detection
  takes 8 min, decision 5, provisioning 12, restore 18, verification 10,
  cutover 7. What is the end-to-end RTA?
- **Model answer:** RTO is the agreed recovery-time limit; RTA is the
  observed time to the defined usable state. The calculated RTA is
  8+5+12+18+10+7 = 60 minutes, equal to the target if the clock
  boundaries are as stated. It is a calculation from supplied values,
  not a measured production result.
- **Reasoning/worked solution:** RTO is the agreed recovery-time limit;
  RTA is the observed time to the defined usable state. The calculated
  RTA is 8+5+12+18+10+7 = 60 minutes, equal to the target if the clock
  boundaries are as stated. It is a calculation from supplied values,
  not a measured production result.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U01-SA-02

- **Question ID:** `U01-SA-02`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L1
- **Objective tested:** RPO versus RPA
- **Estimated time:** 5 minutes
- **Question/prompt:** The newest backup is 20 minutes old, but the
  newest verified business transaction is 31 minutes before failure.
  What is the defensible RPA estimate?
- **Model answer:** The verified recovery point is 31 minutes old, so
  the evidence supports an RPA of at least 31 minutes. The 20-minute
  backup age is not sufficient evidence because it was not verified as a
  consistent business point. Validate transaction continuity and
  integrity.
- **Reasoning/worked solution:** The verified recovery point is 31
  minutes old, so the evidence supports an RPA of at least 31 minutes.
  The 20-minute backup age is not sufficient evidence because it was not
  verified as a consistent business point. Validate transaction
  continuity and integrity.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U01-SA-03

- **Question ID:** `U01-SA-03`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L2
- **Objective tested:** dependency-implied objectives
- **Estimated time:** 5 minutes
- **Question/prompt:** A database has a 20-minute RTO but its required
  secrets backend takes 45 minutes to recover. Is the database service
  objective feasible as stated?
- **Model answer:** No, not through that dependency path: the service
  cannot be usable before a required secrets backend. Redesign
  bootstrap/recovery or renegotiate the objective; verify with a
  dependency graph and timed drill.
- **Reasoning/worked solution:** No, not through that dependency path:
  the service cannot be usable before a required secrets backend.
  Redesign bootstrap/recovery or renegotiate the objective; verify with
  a dependency graph and timed drill.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### Multiple-choice (3 questions)

#### U01-MCQ-01 — prompt

RTO target 60 min; detection 8, decision 5, provisioning 12, restore 18,
verification 10, cutover 7. What is RTA?

- **A.** 18 minutes
- **B.** 60 minutes
- **C.** 53 minutes
- **D.** The target RTO is the measurement

**Correct answer: B.**

- **A — why this distractor is wrong:** 18 minutes is only the restore
  phase; the stated RTA includes detection, decision, provisioning,
  verification, and cutover. Option text: “18 minutes”

- **B — why best:** 8+5+12+18+10+7 = 60 minutes. It is calculated from
  supplied phase durations, not a measured production outcome.

- **C — why this distractor is wrong:** 53 minutes omits the 7-minute
  cutover phase; all six supplied phases must be added. Option text: “53
  minutes”

- **D — why this distractor is wrong:** RTO is the agreed target; RTA is
  calculated from the observed phases. Option text: “The target RTO is
  the measurement”

- **Question ID:** `U01-MCQ-01`

- **Unit(s):** Unit 1 — Recovery time and recovery point objectives

- **Level:** L1

- **Objective tested:** Choose the safest evidence-based decision about
  RTO versus RTA.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** RTO target 60 min; detection 8, decision 5,
  provisioning 12, restore 18, verification 10, cutover 7. What is RTA?

- **Model answer:** B. - **B — why best:** 8+5+12+18+10+7 = 60 minutes.
  It is calculated from supplied phase durations, not a measured
  production outcome.

- **Reasoning/worked solution:** - **B — why best:** 8+5+12+18+10+7 = 60
  minutes. It is calculated from supplied phase durations, not a
  measured production outcome.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U01-MCQ-02 — prompt

Backup timestamp is 20 minutes old, but latest verified consistent
transaction is 31 minutes old. What is supported?

- **A.** RPA is exactly 20 minutes
- **B.** RPO target is automatically met
- **C.** RPA is at least 31 minutes based on current verified evidence
- **D.** RTA is 31 minutes

**Correct answer: C.**

- **A — why this distractor is wrong:** The 20-minute object age is not
  the newest verified business point; the prompt gives a 31-minute-old
  verified transaction. Option text: “RPA is exactly 20 minutes”

- **B — why this distractor is wrong:** An unverified backup timestamp
  cannot prove that the RPO target is met. Option text: “RPO target is
  automatically met”

- **C — why best:** RPA uses the newest verified consistent business
  point, not merely the newest object timestamp.

- **D — why this distractor is wrong:** RPA measures data-loss age; RTA
  measures elapsed time to recovery. Option text: “RTA is 31 minutes”

- **Question ID:** `U01-MCQ-02`

- **Unit(s):** Unit 1 — Recovery time and recovery point objectives

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  RPO versus RPA.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Backup timestamp is 20 minutes old, but latest
  verified consistent transaction is 31 minutes old. What is supported?

- **Model answer:** C. - **C — why best:** RPA uses the newest verified
  consistent business point, not merely the newest object timestamp.

- **Reasoning/worked solution:** - **C — why best:** RPA uses the newest
  verified consistent business point, not merely the newest object
  timestamp.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U01-MCQ-03 — prompt

Database RTO is 20 minutes but required secrets backend recovery takes
45 minutes. Is the objective feasible?

- **A.** Not through this dependency path without changing recovery
  design or objective
- **B.** Yes, because database restore takes 10 minutes
- **C.** Yes, if the RTO target is written in a dashboard
- **D.** No service can ever recover when a dependency fails

**Correct answer: A.**

- **A — why best:** A required dependency with a 45-minute recovery time
  exceeds the 20-minute objective unless a different bootstrap/recovery
  path exists.

- **B — why this distractor is wrong:** A 10-minute database restore
  cannot bypass a required 45-minute secrets dependency. Option text:
  “Yes, because database restore takes 10 minutes”

- **C — why this distractor is wrong:** A dashboard label is not
  evidence that the dependency path can meet the target. Option text:
  “Yes, if the RTO target is written in a dashboard”

- **D — why this distractor is wrong:** A dependency can make the
  current path infeasible, but a different bootstrap design may change
  that; 'never' is unsupported. Option text: “No service can ever
  recover when a dependency fails”

- **Question ID:** `U01-MCQ-03`

- **Unit(s):** Unit 1 — Recovery time and recovery point objectives

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  dependency-implied objectives.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Database RTO is 20 minutes but required secrets
  backend recovery takes 45 minutes. Is the objective feasible?

- **Model answer:** A. - **A — why best:** A required dependency with a
  45-minute recovery time exceeds the 20-minute objective unless a
  different bootstrap/recovery path exists.

- **Reasoning/worked solution:** - **A — why best:** A required
  dependency with a 45-minute recovery time exceeds the 20-minute
  objective unless a different bootstrap/recovery path exists.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

### Artifact interpretation (3 questions)

### U01-AI-01

- **Question ID:** `U01-AI-01`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L1
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** A restore report shows `restore=18m`,
  `verification=not run`, `traffic=not cut over`. What does it prove?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
restore_duration=18m
verification=NOT_RUN
traffic_cutover=NOT_DONE
```

- **Model answer:** RTO is the agreed recovery-time limit; RTA is the
  observed time to the defined usable state. The calculated RTA is
  8+5+12+18+10+7 = 60 minutes, equal to the target if the clock
  boundaries are as stated. It is a calculation from supplied values,
  not a measured production result.
- **Reasoning/worked solution:** RTO is the agreed recovery-time limit;
  RTA is the observed time to the defined usable state. The calculated
  RTA is 8+5+12+18+10+7 = 60 minutes, equal to the target if the clock
  boundaries are as stated. It is a calculation from supplied values,
  not a measured production result.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U01-AI-02

- **Question ID:** `U01-AI-02`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L2
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** A drill has start 09:00, first successful canary
  09:42, restore completion 09:25. Calculate RTA if canary is the
  endpoint.

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
drill_start=09:00
restore_complete=09:25
first_canary_pass=09:42
```

- **Model answer:** The verified recovery point is 31 minutes old, so
  the evidence supports an RPA of at least 31 minutes. The 20-minute
  backup age is not sufficient evidence because it was not verified as a
  consistent business point. Validate transaction continuity and
  integrity.
- **Reasoning/worked solution:** The verified recovery point is 31
  minutes old, so the evidence supports an RPA of at least 31 minutes.
  The 20-minute backup age is not sufficient evidence because it was not
  verified as a consistent business point. Validate transaction
  continuity and integrity.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U01-AI-03

- **Question ID:** `U01-AI-03`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L3
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Failure time is 12:00; latest verified consistent
  transaction is 11:47; latest object timestamp is 11:58. What should be
  reported?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
failure_time=12:00
latest_object_timestamp=11:58
latest_verified_consistent_transaction=11:47
```

- **Model answer:** No, not through that dependency path: the service
  cannot be usable before a required secrets backend. Redesign
  bootstrap/recovery or renegotiate the objective; verify with a
  dependency graph and timed drill.
- **Reasoning/worked solution:** No, not through that dependency path:
  the service cannot be usable before a required secrets backend.
  Redesign bootstrap/recovery or renegotiate the objective; verify with
  a dependency graph and timed drill.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### Artifact review (3 questions)

### U01-AR-01

- **Question ID:** `U01-AR-01`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L2
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** RTO/RPO register has no owner or clock
  boundaries. Identify at least three defects and, for each, explain the
  failure mechanism, correction, and test/evidence that would prove the
  correction works.
- **Model answer:** Defects: (1) identical objectives lack a
  business-impact rationale, so critical and low-impact services are
  treated alike; (2) no dependency graph means a dependency may recover
  after the service target; (3) no clock boundaries or measured RTA/RPA
  makes compliance unverifiable; (4) no named owner/approval weakens
  accountability. Correct with BIA-based tiers, dependency-implied
  limits, explicit timestamps, and an owner. Pass when a timed drill
  records usable-service end and verified recovery point.
- **Reasoning/worked solution:** Defects: (1) identical objectives lack
  a business-impact rationale, so critical and low-impact services are
  treated alike; (2) no dependency graph means a dependency may recover
  after the service target; (3) no clock boundaries or measured RTA/RPA
  makes compliance unverifiable; (4) no named owner/approval weakens
  accountability. Correct with BIA-based tiers, dependency-implied
  limits, explicit timestamps, and an owner. Pass when a timed drill
  records usable-service end and verified recovery point.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U01-AR-02

- **Question ID:** `U01-AR-02`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Dashboard calls restore-command duration the RTA.
  Identify at least three defects and, for each, explain the failure
  mechanism, correction, and test/evidence that would prove the
  correction works.
- **Model answer:** Defects: (1) restore-command duration excludes
  detection and decision; (2) verification and cutover are omitted; (3)
  RPO/data consistency is not tested; (4) no timeline or independent
  evidence supports the green status. Measure from the agreed start to a
  passing canary and record RPA separately. Pass with a cold-read drill
  and complete timestamps.
- **Reasoning/worked solution:** Defects: (1) restore-command duration
  excludes detection and decision; (2) verification and cutover are
  omitted; (3) RPO/data consistency is not tested; (4) no timeline or
  independent evidence supports the green status. Measure from the
  agreed start to a passing canary and record RPA separately. Pass with
  a cold-read drill and complete timestamps.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U01-AR-03

- **Question ID:** `U01-AR-03`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** RPO is set equal to backup interval despite
  failed jobs and corruption risk. Identify at least three defects and,
  for each, explain the failure mechanism, correction, and test/evidence
  that would prove the correction works.
- **Model answer:** Defects: (1) backup cadence is mistaken for achieved
  RPA; (2) failed jobs are not incorporated; (3) logical corruption may
  predate the newest backup; (4) no restore/integrity evidence exists.
  Track the newest verified consistent point, alert on failed
  protection, and test corruption recovery. Pass when a restore proves a
  valid point and the calculated RPA is compared to target.
- **Reasoning/worked solution:** Defects: (1) backup cadence is mistaken
  for achieved RPA; (2) failed jobs are not incorporated; (3) logical
  corruption may predate the newest backup; (4) no restore/integrity
  evidence exists. Track the newest verified consistent point, alert on
  failed protection, and test corruption recovery. Pass when a restore
  proves a valid point and the calculated RPA is compared to target.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### Incident/recovery scenario (1 question)

### U01-IR-01

- **Question ID:** `U01-IR-01`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L3
- **Objective tested:** Respond safely under uncertainty using symptom →
  first action → decide → execute → verify → communicate → prevent.
- **Estimated time:** 12 minutes
- **Question/prompt:** A reporting service is unavailable; the RTO
  target is 30 minutes, identity recovery is estimated at 50 minutes,
  and the newest verified data point is 40 minutes old against a
  10-minute RPO. What is the response? Evidence/timeline
  `[ILLUSTRATIVE — NOT EXECUTED]`: incident declared T+0; identity
  recovery estimate 50 min; latest verified transaction age 40 min; RPO
  target 10 min.
- **Model answer:** Defects: (1) backup cadence is mistaken for achieved
  RPA; (2) failed jobs are not incorporated; (3) logical corruption may
  predate the newest backup; (4) no restore/integrity evidence exists.
  Track the newest verified consistent point, alert on failed
  protection, and test corruption recovery. Pass when a restore proves a
  valid point and the calculated RPA is compared to target.
- **Reasoning/worked solution:** Defects: (1) backup cadence is mistaken
  for achieved RPA; (2) failed jobs are not incorporated; (3) logical
  corruption may predate the newest backup; (4) no restore/integrity
  evidence exists. Track the newest verified consistent point, alert on
  failed protection, and test corruption recovery. Pass when a restore
  proves a valid point and the calculated RPA is compared to target.
- **Common wrong answers or failure modes:** Blind promotion; deletion
  of the last known-good backup; unbounded replay; trusting CR status;
  skipping evidence preservation or communication.
- **Evidence/verification:** Incident timeline, decision log, target
  identity, recovery-point evidence, application invariants, canary, and
  tracked follow-up.
- **Assumptions and limitations:** Illustrative scenario. Containment
  must stop ongoing harm while preserving necessary forensic evidence.

### Design question with scoring rubric (1 question)

### U01-DES-01

- **Question ID:** `U01-DES-01`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L4
- **Objective tested:** Produce a reviewable architecture/runbook with
  explicit trade-offs, ownership, safety gates, and verifiable
  acceptance criteria.
- **Estimated time:** 20 minutes
- **Question/prompt:** Design a tiered objective register for an API, a
  batch pipeline, and model serving. Include owners, RTO/RPO targets,
  dependency constraints, measurement boundaries, and evidence.
- **Model answer:** Defects: (1) backup cadence is mistaken for achieved
  RPA; (2) failed jobs are not incorporated; (3) logical corruption may
  predate the newest backup; (4) no restore/integrity evidence exists.
  Track the newest verified consistent point, alert on failed
  protection, and test corruption recovery. Pass when a restore proves a
  valid point and the calculated RPA is compared to target.
- **Reasoning/worked solution:** Defects: (1) backup cadence is mistaken
  for achieved RPA; (2) failed jobs are not incorporated; (3) logical
  corruption may predate the newest backup; (4) no restore/integrity
  evidence exists. Track the newest verified consistent point, alert on
  failed protection, and test corruption recovery. Pass when a restore
  proves a valid point and the calculated RPA is compared to target.
- **Common wrong answers or failure modes:** A diagram without
  reasoning; targets without evidence; complexity without ownership;
  hidden assumptions; no rollback or acceptance gate.
- **Evidence/verification:** Design record, dependency graph/table,
  named owners, explicit pass/fail checks, and a rehearsal result.
- **Assumptions and limitations:** Rubric totals 16 points. Adapt to
  real workloads only through authorized review.

### Additional questions (2 questions)

### U01-EX-01

- **Question ID:** `U01-EX-01`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L2
- **Objective tested:** Apply calculation reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** Failure at 12:00; latest verified consistent
  transaction at 11:52. Calculate RPA.
- **Model answer:** Defects: (1) backup cadence is mistaken for achieved
  RPA; (2) failed jobs are not incorporated; (3) logical corruption may
  predate the newest backup; (4) no restore/integrity evidence exists.
  Track the newest verified consistent point, alert on failed
  protection, and test corruption recovery. Pass when a restore proves a
  valid point and the calculated RPA is compared to target.
- **Reasoning/worked solution:** Defects: (1) backup cadence is mistaken
  for achieved RPA; (2) failed jobs are not incorporated; (3) logical
  corruption may predate the newest backup; (4) no restore/integrity
  evidence exists. Track the newest verified consistent point, alert on
  failed protection, and test corruption recovery. Pass when a restore
  proves a valid point and the calculated RPA is compared to target.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

### U01-EX-02

- **Question ID:** `U01-EX-02`
- **Unit(s):** Unit 1 — Recovery time and recovery point objectives
- **Level:** L3
- **Objective tested:** Apply troubleshooting reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** A drill reports RTA=14 minutes, but the first
  successful canary is at minute 22. Which value should be reported?
- **Model answer:** Defects: (1) backup cadence is mistaken for achieved
  RPA; (2) failed jobs are not incorporated; (3) logical corruption may
  predate the newest backup; (4) no restore/integrity evidence exists.
  Track the newest verified consistent point, alert on failed
  protection, and test corruption recovery. Pass when a restore proves a
  valid point and the calculated RPA is compared to target.
- **Reasoning/worked solution:** Defects: (1) backup cadence is mistaken
  for achieved RPA; (2) failed jobs are not incorporated; (3) logical
  corruption may predate the newest backup; (4) no restore/integrity
  evidence exists. Track the newest verified consistent point, alert on
  failed protection, and test corruption recovery. Pass when a restore
  proves a valid point and the calculated RPA is compared to target.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

------------------------------------------------------------------------

## Unit 2 — Backup scope, retention, and immutability

**Target file:** `02-backup-scope-retention-and-immutability.md`  
**Learning objectives:** backup versus replica versus snapshot,
retention and survivability, immutability and key custody.

### Conceptual short answer (3 questions)

### U02-SA-01

- **Question ID:** `U02-SA-01`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L1
- **Objective tested:** backup versus replica versus snapshot
- **Estimated time:** 5 minutes
- **Question/prompt:** A replica copies a logical deletion within
  seconds. What protection is missing?
- **Model answer:** Replication improves availability but can reproduce
  logical deletion. Recoverability needs a protected historical point
  and a tested restore path.
- **Reasoning/worked solution:** Replication improves availability but
  can reproduce logical deletion. Recoverability needs a protected
  historical point and a tested restore path.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U02-SA-02

- **Question ID:** `U02-SA-02`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L1
- **Objective tested:** retention and survivability
- **Estimated time:** 5 minutes
- **Question/prompt:** An immutable encrypted backup exists but its only
  decryption key is lost. Is the data recoverable?
- **Model answer:** Not with current evidence. Immutability protects
  stored bytes from certain changes; it does not restore key
  availability. Recover escrowed keys through authorized procedure or
  report the backup as unusable until proven.
- **Reasoning/worked solution:** Not with current evidence. Immutability
  protects stored bytes from certain changes; it does not restore key
  availability. Recover escrowed keys through authorized procedure or
  report the backup as unusable until proven.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U02-SA-03

- **Question ID:** `U02-SA-03`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L2
- **Objective tested:** immutability and key custody
- **Estimated time:** 5 minutes
- **Question/prompt:** A prune job wants to delete the oldest backup
  because storage is low. What evidence must precede approval?
- **Model answer:** Confirm retention/legal holds, identify surviving
  verified recovery points for every required scope, confirm key
  availability and restore status, run a dry-run candidate list, and
  require review. Never delete the last known-good point based only on
  age.
- **Reasoning/worked solution:** Confirm retention/legal holds, identify
  surviving verified recovery points for every required scope, confirm
  key availability and restore status, run a dry-run candidate list, and
  require review. Never delete the last known-good point based only on
  age.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### Multiple-choice (3 questions)

#### U02-MCQ-01 — prompt

A replica copies a logical deletion. What does this show?

- **A.** Replication is broken
- **B.** Replica alone is not independent protection from this failure
- **C.** More replicas always recover the deletion
- **D.** The correct action is to delete all replicas

**Correct answer: B.**

- **A — why this distractor is wrong:** The replica may be working
  correctly while faithfully copying the deletion. Option text:
  “Replication is broken”

- **B — why best:** Replication may work correctly while copying the
  deletion; a protected historical recovery point is needed.

- **C — why this distractor is wrong:** More replicas can propagate the
  same logical deletion and do not create historical recovery points.
  Option text: “More replicas always recover the deletion”

- **D — why this distractor is wrong:** Deleting replicas is destructive
  and does not recover the missing table. Option text: “The correct
  action is to delete all replicas”

- **Question ID:** `U02-MCQ-01`

- **Unit(s):** Unit 2 — Backup scope, retention, and immutability

- **Level:** L1

- **Objective tested:** Choose the safest evidence-based decision about
  backup versus replica versus snapshot.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** A replica copies a logical deletion. What does
  this show?

- **Model answer:** B. - **B — why best:** Replication may work
  correctly while copying the deletion; a protected historical recovery
  point is needed.

- **Reasoning/worked solution:** - **B — why best:** Replication may
  work correctly while copying the deletion; a protected historical
  recovery point is needed.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U02-MCQ-02 — prompt

Immutable encrypted backup exists, but the only key is lost. Is it
recoverable?

- **A.** Yes, immutability restores the key
- **B.** Yes, because ciphertext cannot change
- **C.** Not proven recoverable until a valid key path is restored
- **D.** The backup is safe because the job succeeded

**Correct answer: C.**

- **A — why this distractor is wrong:** Immutability does not recreate a
  lost decryption key. Option text: “Yes, immutability restores the key”

- **B — why this distractor is wrong:** Unchanged ciphertext is not
  usable data without a valid key. Option text: “Yes, because ciphertext
  cannot change”

- **C — why best:** Immutability protects bytes under configured
  conditions, not key availability.

- **D — why this distractor is wrong:** Job success says nothing about
  key availability or tested decryptability. Option text: “The backup is
  safe because the job succeeded”

- **Question ID:** `U02-MCQ-02`

- **Unit(s):** Unit 2 — Backup scope, retention, and immutability

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  retention and survivability.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Immutable encrypted backup exists, but the only
  key is lost. Is it recoverable?

- **Model answer:** C. - **C — why best:** Immutability protects bytes
  under configured conditions, not key availability.

- **Reasoning/worked solution:** - **C — why best:** Immutability
  protects bytes under configured conditions, not key availability.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U02-MCQ-03 — prompt

What must precede backup pruning?

- **A.** A retention-aware review proving compliant verified recovery
  points survive, with key access and dry-run evidence
- **B.** Object age alone
- **C.** A recent backup job success status
- **D.** Immediate deletion because storage is low

**Correct answer: A.**

- **A — why best:** Pruning must preserve the last good recovery point
  and honor retention/holds.

- **B — why this distractor is wrong:** Age alone cannot show whether a
  candidate is the last verified good point or subject to retention.
  Option text: “Object age alone”

- **C — why this distractor is wrong:** A recent successful job does not
  prove a usable restore or that another compliant point survives.
  Option text: “A recent backup job success status”

- **D — why this distractor is wrong:** Storage pressure is not evidence
  that deletion is safe; pruning may destroy the only good point. Option
  text: “Immediate deletion because storage is low”

- **Question ID:** `U02-MCQ-03`

- **Unit(s):** Unit 2 — Backup scope, retention, and immutability

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  immutability and key custody.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** What must precede backup pruning?

- **Model answer:** A. - **A — why best:** Pruning must preserve the
  last good recovery point and honor retention/holds.

- **Reasoning/worked solution:** - **A — why best:** Pruning must
  preserve the last good recovery point and honor retention/holds.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

### Artifact interpretation (3 questions)

### U02-AI-01

- **Question ID:** `U02-AI-01`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L1
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Inventory includes database snapshots but omits
  model blobs and key backup. What gap matters most?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
database_snapshot=present
model_blobs=absent
key_owner=unknown
```

- **Model answer:** Replication improves availability but can reproduce
  logical deletion. Recoverability needs a protected historical point
  and a tested restore path.
- **Reasoning/worked solution:** Replication improves availability but
  can reproduce logical deletion. Recoverability needs a protected
  historical point and a tested restore path.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U02-AI-02

- **Question ID:** `U02-AI-02`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L2
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** A bucket has versioning, but the same compromised
  role can delete all versions. What does versioning prove?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
bucket_versioning=enabled
backup_admin_can_delete_versions=true
independent_credential_test=missing
```

- **Model answer:** Not with current evidence. Immutability protects
  stored bytes from certain changes; it does not restore key
  availability. Recover escrowed keys through authorized procedure or
  report the backup as unusable until proven.
- **Reasoning/worked solution:** Not with current evidence. Immutability
  protects stored bytes from certain changes; it does not restore key
  availability. Recover escrowed keys through authorized procedure or
  report the backup as unusable until proven.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U02-AI-03

- **Question ID:** `U02-AI-03`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L3
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Backup inventory: daily copies 7 days; corruption
  may go undetected for 21 days. Is retention adequate?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
daily_retention=7d
corruption_detection_window=21d
last_verified_restore_point=unknown
```

- **Model answer:** Confirm retention/legal holds, identify surviving
  verified recovery points for every required scope, confirm key
  availability and restore status, run a dry-run candidate list, and
  require review. Never delete the last known-good point based only on
  age.
- **Reasoning/worked solution:** Confirm retention/legal holds, identify
  surviving verified recovery points for every required scope, confirm
  key availability and restore status, run a dry-run candidate list, and
  require review. Never delete the last known-good point based only on
  age.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### Artifact review (3 questions)

### U02-AR-01

- **Question ID:** `U02-AR-01`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L2
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** All backups share application credentials and one
  failure domain. Identify at least three defects and, for each, explain
  the failure mechanism, correction, and test/evidence that would prove
  the correction works.
- **Model answer:** Defects: (1) application credentials can destroy
  their own backups; (2) same bucket/account/failure domain exposes all
  copies to one event; (3) no immutability or retention-lock
  verification exists; (4) seven days may be shorter than corruption
  discovery; (5) no restore evidence. Separate identities/failure
  domains, define retention from detection risk, test object-lock
  behavior for the pinned provider, and restore using independent
  credentials.
- **Reasoning/worked solution:** Defects: (1) application credentials
  can destroy their own backups; (2) same bucket/account/failure domain
  exposes all copies to one event; (3) no immutability or retention-lock
  verification exists; (4) seven days may be shorter than corruption
  discovery; (5) no restore evidence. Separate identities/failure
  domains, define retention from detection risk, test object-lock
  behavior for the pinned provider, and restore using independent
  credentials.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U02-AR-02

- **Question ID:** `U02-AR-02`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Policy has retention duration but no restore test
  or key owner. Identify at least three defects and, for each, explain
  the failure mechanism, correction, and test/evidence that would prove
  the correction works.
- **Model answer:** Defects: (1) state inventory omits model blobs; (2)
  keys have no owner or independent recovery path; (3) registry metadata
  is mistaken for artifact bytes; (4) external DNS/identity dependencies
  are absent; (5) no end-to-end test. Inventory every authoritative
  state plane, name owners, protect keys independently, and test a cold
  restore. Pass when serving validates the recovered artifact and
  dependencies.
- **Reasoning/worked solution:** Defects: (1) state inventory omits
  model blobs; (2) keys have no owner or independent recovery path; (3)
  registry metadata is mistaken for artifact bytes; (4) external
  DNS/identity dependencies are absent; (5) no end-to-end test.
  Inventory every authoritative state plane, name owners, protect keys
  independently, and test a cold restore. Pass when serving validates
  the recovered artifact and dependencies.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U02-AR-03

- **Question ID:** `U02-AR-03`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Prune deletes by age only, ignoring the last
  verified restore point. Identify at least three defects and, for each,
  explain the failure mechanism, correction, and test/evidence that
  would prove the correction works.
- **Model answer:** Defects: (1) age alone can select the last
  known-good point; (2) legal holds/retention obligations are
  ignored; (3) restore status/integrity is ignored; (4) no dry-run or
  approval; (5) no post-prune inventory. Require retention-aware
  candidate evaluation and explicit approval; test with a simulated
  inventory where newest backups are corrupt. Never delete the only
  verified point.
- **Reasoning/worked solution:** Defects: (1) age alone can select the
  last known-good point; (2) legal holds/retention obligations are
  ignored; (3) restore status/integrity is ignored; (4) no dry-run or
  approval; (5) no post-prune inventory. Require retention-aware
  candidate evaluation and explicit approval; test with a simulated
  inventory where newest backups are corrupt. Never delete the only
  verified point.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### Incident/recovery scenario (1 question)

### U02-IR-01

- **Question ID:** `U02-IR-01`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L3
- **Objective tested:** Respond safely under uncertainty using symptom →
  first action → decide → execute → verify → communicate → prevent.
- **Estimated time:** 12 minutes
- **Question/prompt:** A suspected credential compromise is deleting
  backup objects. What should the incident team do first, and how should
  recovery proceed? Evidence/timeline `[ILLUSTRATIVE — NOT EXECUTED]`:
  object-delete audit events at T+0; backup credential suspected
  compromised; latest known-good restore point not yet independently
  verified.
- **Model answer:** Defects: (1) age alone can select the last
  known-good point; (2) legal holds/retention obligations are
  ignored; (3) restore status/integrity is ignored; (4) no dry-run or
  approval; (5) no post-prune inventory. Require retention-aware
  candidate evaluation and explicit approval; test with a simulated
  inventory where newest backups are corrupt. Never delete the only
  verified point.
- **Reasoning/worked solution:** Defects: (1) age alone can select the
  last known-good point; (2) legal holds/retention obligations are
  ignored; (3) restore status/integrity is ignored; (4) no dry-run or
  approval; (5) no post-prune inventory. Require retention-aware
  candidate evaluation and explicit approval; test with a simulated
  inventory where newest backups are corrupt. Never delete the only
  verified point.
- **Common wrong answers or failure modes:** Blind promotion; deletion
  of the last known-good backup; unbounded replay; trusting CR status;
  skipping evidence preservation or communication.
- **Evidence/verification:** Incident timeline, decision log, target
  identity, recovery-point evidence, application invariants, canary, and
  tracked follow-up.
- **Assumptions and limitations:** Illustrative scenario. Containment
  must stop ongoing harm while preserving necessary forensic evidence.

### Design question with scoring rubric (1 question)

### U02-DES-01

- **Question ID:** `U02-DES-01`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L4
- **Objective tested:** Produce a reviewable architecture/runbook with
  explicit trade-offs, ownership, safety gates, and verifiable
  acceptance criteria.
- **Estimated time:** 20 minutes
- **Question/prompt:** Design a survivability matrix for snapshot,
  replica, versioning, immutable copy, Git mirror, and pull-based backup
  against deletion, corruption, credential compromise, and site loss.
- **Model answer:** Defects: (1) age alone can select the last
  known-good point; (2) legal holds/retention obligations are
  ignored; (3) restore status/integrity is ignored; (4) no dry-run or
  approval; (5) no post-prune inventory. Require retention-aware
  candidate evaluation and explicit approval; test with a simulated
  inventory where newest backups are corrupt. Never delete the only
  verified point.
- **Reasoning/worked solution:** Defects: (1) age alone can select the
  last known-good point; (2) legal holds/retention obligations are
  ignored; (3) restore status/integrity is ignored; (4) no dry-run or
  approval; (5) no post-prune inventory. Require retention-aware
  candidate evaluation and explicit approval; test with a simulated
  inventory where newest backups are corrupt. Never delete the only
  verified point.
- **Common wrong answers or failure modes:** A diagram without
  reasoning; targets without evidence; complexity without ownership;
  hidden assumptions; no rollback or acceptance gate.
- **Evidence/verification:** Design record, dependency graph/table,
  named owners, explicit pass/fail checks, and a rehearsal result.
- **Assumptions and limitations:** Rubric totals 16 points. Adapt to
  real workloads only through authorized review.

### Additional questions (2 questions)

### U02-EX-01

- **Question ID:** `U02-EX-01`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L2
- **Objective tested:** Apply artifact reasoning reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** Versioned bucket has 30 versions, but the same
  compromised role can permanently delete all versions and keys are
  shared. Is this sufficient?
- **Model answer:** Defects: (1) age alone can select the last
  known-good point; (2) legal holds/retention obligations are
  ignored; (3) restore status/integrity is ignored; (4) no dry-run or
  approval; (5) no post-prune inventory. Require retention-aware
  candidate evaluation and explicit approval; test with a simulated
  inventory where newest backups are corrupt. Never delete the only
  verified point.
- **Reasoning/worked solution:** Defects: (1) age alone can select the
  last known-good point; (2) legal holds/retention obligations are
  ignored; (3) restore status/integrity is ignored; (4) no dry-run or
  approval; (5) no post-prune inventory. Require retention-aware
  candidate evaluation and explicit approval; test with a simulated
  inventory where newest backups are corrupt. Never delete the only
  verified point.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

### U02-EX-02

- **Question ID:** `U02-EX-02`
- **Unit(s):** Unit 2 — Backup scope, retention, and immutability
- **Level:** L3
- **Objective tested:** Apply safe operation reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** What must a prune plan prove before deleting a
  candidate?
- **Model answer:** Defects: (1) age alone can select the last
  known-good point; (2) legal holds/retention obligations are
  ignored; (3) restore status/integrity is ignored; (4) no dry-run or
  approval; (5) no post-prune inventory. Require retention-aware
  candidate evaluation and explicit approval; test with a simulated
  inventory where newest backups are corrupt. Never delete the only
  verified point.
- **Reasoning/worked solution:** Defects: (1) age alone can select the
  last known-good point; (2) legal holds/retention obligations are
  ignored; (3) restore status/integrity is ignored; (4) no dry-run or
  approval; (5) no post-prune inventory. Require retention-aware
  candidate evaluation and explicit approval; test with a simulated
  inventory where newest backups are corrupt. Never delete the only
  verified point.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

------------------------------------------------------------------------

## Unit 3 — Restoring platform metadata and configuration

**Target file:** `03-restoring-platform-metadata-and-configuration.md`  
**Learning objectives:** platform metadata versus application data,
CRD/operator/bootstrap ordering, GitOps ownership and reconciliation.

### Conceptual short answer (3 questions)

### U03-SA-01

- **Question ID:** `U03-SA-01`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L1
- **Objective tested:** platform metadata versus application data
- **Estimated time:** 5 minutes
- **Question/prompt:** A Deployment YAML is restored but its PVC data is
  absent. What has and has not been recovered?
- **Model answer:** The desired workload metadata may be present, but
  the application data plane is not recovered. Restore and verify
  persistent data separately, then validate application invariants.
- **Reasoning/worked solution:** The desired workload metadata may be
  present, but the application data plane is not recovered. Restore and
  verify persistent data separately, then validate application
  invariants.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U03-SA-02

- **Question ID:** `U03-SA-02`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L1
- **Objective tested:** CRD/operator/bootstrap ordering
- **Estimated time:** 5 minutes
- **Question/prompt:** A custom resource is rejected because its kind is
  unknown. What prerequisite is missing?
- **Model answer:** The compatible CRD/API registration must exist
  before the API server can accept that custom resource. Install/verify
  the CRD and controller version, then restore instances.
- **Reasoning/worked solution:** The compatible CRD/API registration
  must exist before the API server can accept that custom resource.
  Install/verify the CRD and controller version, then restore instances.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U03-SA-03

- **Question ID:** `U03-SA-03`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L2
- **Objective tested:** GitOps ownership and reconciliation
- **Estimated time:** 5 minutes
- **Question/prompt:** GitOps prunes a manually restored object absent
  from Git. How should recovery proceed?
- **Model answer:** Coordinate ownership and reconciliation: preserve
  evidence, make intended state explicit in reviewed Git or approved
  ownership policy, restore dependencies, and resume reconciliation only
  after the restore plan is safe. Verify convergence and no unwanted
  prune.
- **Reasoning/worked solution:** Coordinate ownership and
  reconciliation: preserve evidence, make intended state explicit in
  reviewed Git or approved ownership policy, restore dependencies, and
  resume reconciliation only after the restore plan is safe. Verify
  convergence and no unwanted prune.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### Multiple-choice (3 questions)

#### U03-MCQ-01 — prompt

A custom resource kind is unknown during restore. What prerequisite is
missing?

- **A.** A second Deployment replica
- **B.** The compatible CRD/API registration
- **C.** A larger PVC
- **D.** A DNS TTL change

**Correct answer: B.**

- **A — why this distractor is wrong:** A Deployment replica count does
  not register a custom API kind. Option text: “A second Deployment
  replica”

- **B — why best:** The API must recognize the custom kind before it can
  accept its instances.

- **C — why this distractor is wrong:** Storage capacity is unrelated to
  whether the API server knows the custom resource type. Option text: “A
  larger PVC”

- **D — why this distractor is wrong:** DNS TTL does not register the
  missing CRD. Option text: “A DNS TTL change”

- **Question ID:** `U03-MCQ-01`

- **Unit(s):** Unit 3 — Restoring platform metadata and configuration

- **Level:** L1

- **Objective tested:** Choose the safest evidence-based decision about
  platform metadata versus application data.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** A custom resource kind is unknown during restore.
  What prerequisite is missing?

- **Model answer:** B. - **B — why best:** The API must recognize the
  custom kind before it can accept its instances.

- **Reasoning/worked solution:** - **B — why best:** The API must
  recognize the custom kind before it can accept its instances.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U03-MCQ-02 — prompt

GitOps prunes a restored object absent from Git. What should the team
do?

- **A.** Disable GitOps forever
- **B.** Repeat restore until it remains
- **C.** Coordinate ownership and desired state, then resume
  reconciliation deliberately
- **D.** Delete the Git repository

**Correct answer: C.**

- **A — why this distractor is wrong:** Permanently disabling GitOps
  creates uncontrolled drift rather than resolving ownership. Option
  text: “Disable GitOps forever”

- **B — why this distractor is wrong:** Repeated restore can be pruned
  again if desired state and ownership remain inconsistent. Option text:
  “Repeat restore until it remains”

- **C — why best:** Restored state must be reconciled with the
  authoritative desired-state system.

- **D — why this distractor is wrong:** Deleting Git removes a recovery
  input and does not fix reconciliation semantics. Option text: “Delete
  the Git repository”

- **Question ID:** `U03-MCQ-02`

- **Unit(s):** Unit 3 — Restoring platform metadata and configuration

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  CRD/operator/bootstrap ordering.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** GitOps prunes a restored object absent from Git.
  What should the team do?

- **Model answer:** C. - **C — why best:** Restored state must be
  reconciled with the authoritative desired-state system.

- **Reasoning/worked solution:** - **C — why best:** Restored state must
  be reconciled with the authoritative desired-state system.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U03-MCQ-03 — prompt

What do Kubernetes manifests alone prove?

- **A.** They are one recovery input; external data, keys, and
  dependencies require separate recovery evidence
- **B.** They contain every PV byte
- **C.** They guarantee secret values are recoverable
- **D.** Applying them proves service usability

**Correct answer: A.**

- **A — why best:** Metadata and persistent application data are
  separate recovery concerns.

- **B — why this distractor is wrong:** Manifests generally do not
  contain persistent-volume bytes unless explicitly represented and
  protected elsewhere. Option text: “They contain every PV byte”

- **C — why this distractor is wrong:** A reference to a secret does not
  prove the secret value, key, or backend can be recovered. Option text:
  “They guarantee secret values are recoverable”

- **D — why this distractor is wrong:** Apply success does not prove
  data, dependencies, or application invariants are correct. Option
  text: “Applying them proves service usability”

- **Question ID:** `U03-MCQ-03`

- **Unit(s):** Unit 3 — Restoring platform metadata and configuration

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  GitOps ownership and reconciliation.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** What do Kubernetes manifests alone prove?

- **Model answer:** A. - **A — why best:** Metadata and persistent
  application data are separate recovery concerns.

- **Reasoning/worked solution:** - **A — why best:** Metadata and
  persistent application data are separate recovery concerns.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

### Artifact interpretation (3 questions)

### U03-AI-01

- **Question ID:** `U03-AI-01`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L1
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Restore order lists app before CRD/operator and
  database. Identify the first structural defect.

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
restore_order=app,custom_resource,CRD,operator,database
canary=not_run
```

- **Model answer:** The desired workload metadata may be present, but
  the application data plane is not recovered. Restore and verify
  persistent data separately, then validate application invariants.
- **Reasoning/worked solution:** The desired workload metadata may be
  present, but the application data plane is not recovered. Restore and
  verify persistent data separately, then validate application
  invariants.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U03-AI-02

- **Question ID:** `U03-AI-02`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L2
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Vault requires cluster identity, while cluster
  bootstrap requires Vault credentials. What is the design issue?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
Vault_requires=cluster_identity
cluster_bootstrap_requires=Vault_credentials
independent_bootstrap_path=none
```

- **Model answer:** The compatible CRD/API registration must exist
  before the API server can accept that custom resource. Install/verify
  the CRD and controller version, then restore instances.
- **Reasoning/worked solution:** The compatible CRD/API registration
  must exist before the API server can accept that custom resource.
  Install/verify the CRD and controller version, then restore instances.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U03-AI-03

- **Question ID:** `U03-AI-03`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L3
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** What evidence beyond successful `kubectl apply`
  is needed to claim recovery?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
kubectl_apply=success
controller_reconcile=unknown
GitOps_prune=pending
canary=not_run
```

- **Model answer:** Coordinate ownership and reconciliation: preserve
  evidence, make intended state explicit in reviewed Git or approved
  ownership policy, restore dependencies, and resume reconciliation only
  after the restore plan is safe. Verify convergence and no unwanted
  prune.
- **Reasoning/worked solution:** Coordinate ownership and
  reconciliation: preserve evidence, make intended state explicit in
  reviewed Git or approved ownership policy, restore dependencies, and
  resume reconciliation only after the restore plan is safe. Verify
  convergence and no unwanted prune.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### Artifact review (3 questions)

### U03-AR-01

- **Question ID:** `U03-AR-01`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L2
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Runbook says apply all manifests in one batch and
  start traffic. Identify at least three defects and, for each, explain
  the failure mechanism, correction, and test/evidence that would prove
  the correction works.
- **Model answer:** Defects: (1) no dependency order; (2) no explicit
  data restore; (3) no bootstrap identity/key path; (4) no GitOps
  ownership control; (5) no application invariant or evidence. Add
  phased gates and separate data recovery from manifest application.
  Pass when another operator cold-reads the runbook and restores a
  throwaway service with verified data.
- **Reasoning/worked solution:** Defects: (1) no dependency order; (2)
  no explicit data restore; (3) no bootstrap identity/key path; (4) no
  GitOps ownership control; (5) no application invariant or evidence.
  Add phased gates and separate data recovery from manifest application.
  Pass when another operator cold-reads the runbook and restores a
  throwaway service with verified data.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U03-AR-02

- **Question ID:** `U03-AR-02`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Control-plane backup is assumed to include
  external volume bytes and keys. Identify at least three defects and,
  for each, explain the failure mechanism, correction, and test/evidence
  that would prove the correction works.
- **Model answer:** Defects: (1) control-plane metadata is conflated
  with external PV/object bytes; (2) encryption keys and secrets are
  omitted; (3) recovery consistency boundary is unspecified; (4)
  dependency order is absent; (5) no restore drill. Inventory state by
  source of truth, recover keys and external data separately, and prove
  the app can read the recovered records.
- **Reasoning/worked solution:** Defects: (1) control-plane metadata is
  conflated with external PV/object bytes; (2) encryption keys and
  secrets are omitted; (3) recovery consistency boundary is
  unspecified; (4) dependency order is absent; (5) no restore drill.
  Inventory state by source of truth, recover keys and external data
  separately, and prove the app can read the recovered records.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U03-AR-03

- **Question ID:** `U03-AR-03`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** GitOps resumes before data and operators are
  restored. Identify at least three defects and, for each, explain the
  failure mechanism, correction, and test/evidence that would prove the
  correction works.
- **Model answer:** Defects: (1) custom resources may be applied before
  CRDs/operators; (2) compatibility and controller health are
  unchecked; (3) GitOps may prune or overwrite state; (4)
  credentials/data readiness are not gated; (5) no post-reconcile
  verification. Install compatible prerequisites, coordinate GitOps
  ownership, and validate controller and application behavior in an
  ephemeral cluster.
- **Reasoning/worked solution:** Defects: (1) custom resources may be
  applied before CRDs/operators; (2) compatibility and controller health
  are unchecked; (3) GitOps may prune or overwrite state; (4)
  credentials/data readiness are not gated; (5) no post-reconcile
  verification. Install compatible prerequisites, coordinate GitOps
  ownership, and validate controller and application behavior in an
  ephemeral cluster.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### Incident/recovery scenario (1 question)

### U03-IR-01

- **Question ID:** `U03-IR-01`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L3
- **Objective tested:** Respond safely under uncertainty using symptom →
  first action → decide → execute → verify → communicate → prevent.
- **Estimated time:** 12 minutes
- **Question/prompt:** A cluster was lost. Git is reachable, but the
  registry, secrets backend, and operator CRDs are not yet available.
  Design the recovery sequence. Evidence/timeline
  `[ILLUSTRATIVE — NOT EXECUTED]`: cluster lost at T+0; Git reachable;
  registry and secrets backend unavailable; required CRDs absent.
- **Model answer:** Defects: (1) custom resources may be applied before
  CRDs/operators; (2) compatibility and controller health are
  unchecked; (3) GitOps may prune or overwrite state; (4)
  credentials/data readiness are not gated; (5) no post-reconcile
  verification. Install compatible prerequisites, coordinate GitOps
  ownership, and validate controller and application behavior in an
  ephemeral cluster.
- **Reasoning/worked solution:** Defects: (1) custom resources may be
  applied before CRDs/operators; (2) compatibility and controller health
  are unchecked; (3) GitOps may prune or overwrite state; (4)
  credentials/data readiness are not gated; (5) no post-reconcile
  verification. Install compatible prerequisites, coordinate GitOps
  ownership, and validate controller and application behavior in an
  ephemeral cluster.
- **Common wrong answers or failure modes:** Blind promotion; deletion
  of the last known-good backup; unbounded replay; trusting CR status;
  skipping evidence preservation or communication.
- **Evidence/verification:** Incident timeline, decision log, target
  identity, recovery-point evidence, application invariants, canary, and
  tracked follow-up.
- **Assumptions and limitations:** Illustrative scenario. Containment
  must stop ongoing harm while preserving necessary forensic evidence.

### Design question with scoring rubric (1 question)

### U03-DES-01

- **Question ID:** `U03-DES-01`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L4
- **Objective tested:** Produce a reviewable architecture/runbook with
  explicit trade-offs, ownership, safety gates, and verifiable
  acceptance criteria.
- **Estimated time:** 20 minutes
- **Question/prompt:** Design a recovery sequence for a Kubernetes data
  platform with GitOps, private registry, secrets backend, database
  operator, and model-serving workloads.
- **Model answer:** Defects: (1) custom resources may be applied before
  CRDs/operators; (2) compatibility and controller health are
  unchecked; (3) GitOps may prune or overwrite state; (4)
  credentials/data readiness are not gated; (5) no post-reconcile
  verification. Install compatible prerequisites, coordinate GitOps
  ownership, and validate controller and application behavior in an
  ephemeral cluster.
- **Reasoning/worked solution:** Defects: (1) custom resources may be
  applied before CRDs/operators; (2) compatibility and controller health
  are unchecked; (3) GitOps may prune or overwrite state; (4)
  credentials/data readiness are not gated; (5) no post-reconcile
  verification. Install compatible prerequisites, coordinate GitOps
  ownership, and validate controller and application behavior in an
  ephemeral cluster.
- **Common wrong answers or failure modes:** A diagram without
  reasoning; targets without evidence; complexity without ownership;
  hidden assumptions; no rollback or acceptance gate.
- **Evidence/verification:** Design record, dependency graph/table,
  named owners, explicit pass/fail checks, and a rehearsal result.
- **Assumptions and limitations:** Rubric totals 16 points. Adapt to
  real workloads only through authorized review.

### Additional questions (2 questions)

### U03-EX-01

- **Question ID:** `U03-EX-01`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L2
- **Objective tested:** Apply diagnosis reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** CRD is established but custom resources do not
  reconcile. What do you inspect?
- **Model answer:** Defects: (1) custom resources may be applied before
  CRDs/operators; (2) compatibility and controller health are
  unchecked; (3) GitOps may prune or overwrite state; (4)
  credentials/data readiness are not gated; (5) no post-reconcile
  verification. Install compatible prerequisites, coordinate GitOps
  ownership, and validate controller and application behavior in an
  ephemeral cluster.
- **Reasoning/worked solution:** Defects: (1) custom resources may be
  applied before CRDs/operators; (2) compatibility and controller health
  are unchecked; (3) GitOps may prune or overwrite state; (4)
  credentials/data readiness are not gated; (5) no post-reconcile
  verification. Install compatible prerequisites, coordinate GitOps
  ownership, and validate controller and application behavior in an
  ephemeral cluster.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

### U03-EX-02

- **Question ID:** `U03-EX-02`
- **Unit(s):** Unit 3 — Restoring platform metadata and configuration
- **Level:** L3
- **Objective tested:** Apply verification reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** Name three kinds of evidence beyond successful
  apply.
- **Model answer:** Defects: (1) custom resources may be applied before
  CRDs/operators; (2) compatibility and controller health are
  unchecked; (3) GitOps may prune or overwrite state; (4)
  credentials/data readiness are not gated; (5) no post-reconcile
  verification. Install compatible prerequisites, coordinate GitOps
  ownership, and validate controller and application behavior in an
  ephemeral cluster.
- **Reasoning/worked solution:** Defects: (1) custom resources may be
  applied before CRDs/operators; (2) compatibility and controller health
  are unchecked; (3) GitOps may prune or overwrite state; (4)
  credentials/data readiness are not gated; (5) no post-reconcile
  verification. Install compatible prerequisites, coordinate GitOps
  ownership, and validate controller and application behavior in an
  ephemeral cluster.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

------------------------------------------------------------------------

## Unit 4 — Recovering data pipeline state and checkpoints

**Target file:**
`04-recovering-data-pipeline-state-and-checkpoints.md`  
**Learning objectives:** checkpoint/offset and sink transaction
alignment, idempotency and replay safety, watermarks, retention,
freshness, reconciliation.

### Conceptual short answer (3 questions)

### U04-SA-01

- **Question ID:** `U04-SA-01`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L1
- **Objective tested:** checkpoint/offset and sink transaction alignment
- **Estimated time:** 5 minutes
- **Question/prompt:** Checkpoint is at offset 500, sink commit ledger
  at 480. What should recovery do?
- **Model answer:** Do not resume blindly at 500 or replay everything.
  Reconcile committed effects, select a bounded consistent boundary,
  replay with idempotency/deduplication, and validate output keys and
  counts.
- **Reasoning/worked solution:** Do not resume blindly at 500 or replay
  everything. Reconcile committed effects, select a bounded consistent
  boundary, replay with idempotency/deduplication, and validate output
  keys and counts.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U04-SA-02

- **Question ID:** `U04-SA-02`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L1
- **Objective tested:** idempotency and replay safety
- **Estimated time:** 5 minutes
- **Question/prompt:** Requested replay is 48 hours but source retention
  is 24 hours. What is the constraint?
- **Model answer:** The source may no longer contain the full requested
  replay range. Align retention with detection + recovery + replay needs
  or document an archive/reconstruction path.
- **Reasoning/worked solution:** The source may no longer contain the
  full requested replay range. Align retention with detection +
  recovery + replay needs or document an archive/reconstruction path.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U04-SA-03

- **Question ID:** `U04-SA-03`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L2
- **Objective tested:** watermarks, retention, freshness, reconciliation
- **Estimated time:** 5 minutes
- **Question/prompt:** Why does `RUNNING` plus zero consumer lag not
  prove correct pipeline recovery?
- **Model answer:** Lag is only one progress signal. Verify
  watermarks/freshness, row/object invariants, duplicates, missing keys,
  sink commit state, and downstream side effects.
- **Reasoning/worked solution:** Lag is only one progress signal. Verify
  watermarks/freshness, row/object invariants, duplicates, missing keys,
  sink commit state, and downstream side effects.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### Multiple-choice (3 questions)

#### U04-MCQ-01 — prompt

Checkpoint=500, sink commit=480. What is safest?

- **A.** Resume at 500 without inspection
- **B.** Reconcile committed effects and replay a bounded range with
  idempotency controls
- **C.** Delete all output and restart from zero
- **D.** Trust the newer checkpoint

**Correct answer: B.**

- **A — why this distractor is wrong:** Resuming at 500 can skip input
  whose sink effects are not committed through that offset. Option text:
  “Resume at 500 without inspection”

- **B — why best:** Checkpoint and sink state disagree; a bounded
  reconciliation avoids gaps and duplicates.

- **C — why this distractor is wrong:** Deleting all output risks data
  loss and duplicates irreversible external side effects. Option text:
  “Delete all output and restart from zero”

- **D — why this distractor is wrong:** A newer checkpoint can be ahead
  of durable sink state; timestamp/order alone is not consistency.
  Option text: “Trust the newer checkpoint”

- **Question ID:** `U04-MCQ-01`

- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints

- **Level:** L1

- **Objective tested:** Choose the safest evidence-based decision about
  checkpoint/offset and sink transaction alignment.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Checkpoint=500, sink commit=480. What is safest?

- **Model answer:** B. - **B — why best:** Checkpoint and sink state
  disagree; a bounded reconciliation avoids gaps and duplicates.

- **Reasoning/worked solution:** - **B — why best:** Checkpoint and sink
  state disagree; a bounded reconciliation avoids gaps and duplicates.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U04-MCQ-02 — prompt

Replay requested is 48 h but source retention is 24 h. What is the
constraint?

- **A.** Retries recover expired input automatically
- **B.** Checkpoint contains all source payload
- **C.** Full replay may be impossible without another source/archive
- **D.** The job must be faster

**Correct answer: C.**

- **A — why this distractor is wrong:** Retries cannot retrieve source
  records that have expired from retention. Option text: “Retries
  recover expired input automatically”

- **B — why this distractor is wrong:** A checkpoint records
  progress/state, not necessarily the original source payload. Option
  text: “Checkpoint contains all source payload”

- **C — why best:** Replay requires source events to remain available or
  an alternate authoritative source.

- **D — why this distractor is wrong:** Processing speed does not solve
  unavailable historical input. Option text: “The job must be faster”

- **Question ID:** `U04-MCQ-02`

- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  idempotency and replay safety.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Replay requested is 48 h but source retention is
  24 h. What is the constraint?

- **Model answer:** C. - **C — why best:** Replay requires source events
  to remain available or an alternate authoritative source.

- **Reasoning/worked solution:** - **C — why best:** Replay requires
  source events to remain available or an alternate authoritative
  source.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U04-MCQ-03 — prompt

What proves pipeline recovery better than RUNNING and zero lag?

- **A.** Freshness/watermark plus reconciled keys, counts, sink commits,
  and application invariants
- **B.** Pod readiness alone
- **C.** Job status alone
- **D.** One zero-lag sample

**Correct answer: A.**

- **A — why best:** Progress signals must be combined with data
  correctness and freshness checks.

- **B — why this distractor is wrong:** Pod readiness only reports
  workload health, not data completeness or freshness. Option text: “Pod
  readiness alone”

- **C — why this distractor is wrong:** Job status can be green even
  when output is missing or duplicated. Option text: “Job status alone”

- **D — why this distractor is wrong:** A single lag sample can miss
  stale output, wrong watermarks, or sink inconsistencies. Option text:
  “One zero-lag sample”

- **Question ID:** `U04-MCQ-03`

- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  watermarks, retention, freshness, reconciliation.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** What proves pipeline recovery better than RUNNING
  and zero lag?

- **Model answer:** A. - **A — why best:** Progress signals must be
  combined with data correctness and freshness checks.

- **Reasoning/worked solution:** - **A — why best:** Progress signals
  must be combined with data correctness and freshness checks.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

### Artifact interpretation (3 questions)

### U04-AI-01

- **Question ID:** `U04-AI-01`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L1
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Checkpoint=900, sink committed=875, dedupe keys
  absent. What is the immediate risk?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
checkpoint_offset=900
sink_committed_offset=875
dedupe_keys=none
```

- **Model answer:** Do not resume blindly at 500 or replay everything.
  Reconcile committed effects, select a bounded consistent boundary,
  replay with idempotency/deduplication, and validate output keys and
  counts.
- **Reasoning/worked solution:** Do not resume blindly at 500 or replay
  everything. Reconcile committed effects, select a bounded consistent
  boundary, replay with idempotency/deduplication, and validate output
  keys and counts.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U04-AI-02

- **Question ID:** `U04-AI-02`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L2
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** A pipeline has 1.2 million records and replay
  throughput 20,000 records/min. Calculate ideal replay time before
  overhead.

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
records=1200000
replay_rate=20000_records_per_minute
retries_and_overhead=excluded
```

- **Model answer:** The source may no longer contain the full requested
  replay range. Align retention with detection + recovery + replay needs
  or document an archive/reconstruction path.
- **Reasoning/worked solution:** The source may no longer contain the
  full requested replay range. Align retention with detection +
  recovery + replay needs or document an archive/reconstruction path.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U04-AI-03

- **Question ID:** `U04-AI-03`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L3
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Counts match after replay but duplicate IDs and
  missing IDs coexist. Why can counts mislead?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
expected_keys=K1..K100
actual_keys=K1..K100_except_K17_plus_duplicate_K55
row_count=100
```

- **Model answer:** Lag is only one progress signal. Verify
  watermarks/freshness, row/object invariants, duplicates, missing keys,
  sink commit state, and downstream side effects.
- **Reasoning/worked solution:** Lag is only one progress signal. Verify
  watermarks/freshness, row/object invariants, duplicates, missing keys,
  sink commit state, and downstream side effects.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### Artifact review (3 questions)

### U04-AR-01

- **Question ID:** `U04-AR-01`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L2
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Runbook resets all offsets to zero against
  non-idempotent production sinks. Identify at least three defects and,
  for each, explain the failure mechanism, correction, and test/evidence
  that would prove the correction works.
- **Model answer:** Defects: (1) replay from zero is unbounded; (2) side
  effects are non-idempotent; (3) no sink/checkpoint transaction
  boundary is inspected; (4) no source-retention check; (5) no isolated
  rehearsal or throttle. Reconcile the last committed range and replay
  only a bounded range with deduplication/compensation. Pass with
  duplicate/missing-key tests and downstream side-effect checks.
- **Reasoning/worked solution:** Defects: (1) replay from zero is
  unbounded; (2) side effects are non-idempotent; (3) no sink/checkpoint
  transaction boundary is inspected; (4) no source-retention check; (5)
  no isolated rehearsal or throttle. Reconcile the last committed range
  and replay only a bounded range with deduplication/compensation. Pass
  with duplicate/missing-key tests and downstream side-effect checks.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U04-AR-02

- **Question ID:** `U04-AR-02`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Success is defined as process running with no lag
  alert. Identify at least three defects and, for each, explain the
  failure mechanism, correction, and test/evidence that would prove the
  correction works.
- **Model answer:** Defects: (1) process status/lag is not a data
  correctness check; (2) watermark/freshness is absent; (3) duplicates
  and missing keys are undetected; (4) sink commit state is not
  checked; (5) no reconciliation output. Add freshness SLI, key-level
  reconciliation, and sink commit verification. Pass by injecting a
  known omission/duplicate in a disposable dataset and detecting it.
- **Reasoning/worked solution:** Defects: (1) process status/lag is not
  a data correctness check; (2) watermark/freshness is absent; (3)
  duplicates and missing keys are undetected; (4) sink commit state is
  not checked; (5) no reconciliation output. Add freshness SLI,
  key-level reconciliation, and sink commit verification. Pass by
  injecting a known omission/duplicate in a disposable dataset and
  detecting it.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U04-AR-03

- **Question ID:** `U04-AR-03`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Checkpoint retention is shorter than maximum
  recovery time. Identify at least three defects and, for each, explain
  the failure mechanism, correction, and test/evidence that would prove
  the correction works.
- **Model answer:** Defects: (1) input retention is shorter than
  detection + recovery + replay needs; (2) checkpoint schedule may be
  too sparse; (3) no archive fallback; (4) no catch-up capacity/throttle
  plan; (5) no explicit unrecoverable-gap reporting. Align retention to
  worst-case outage and replay horizon, add a tested archive path or
  document the limit, and validate catch-up time.
- **Reasoning/worked solution:** Defects: (1) input retention is shorter
  than detection + recovery + replay needs; (2) checkpoint schedule may
  be too sparse; (3) no archive fallback; (4) no catch-up
  capacity/throttle plan; (5) no explicit unrecoverable-gap reporting.
  Align retention to worst-case outage and replay horizon, add a tested
  archive path or document the limit, and validate catch-up time.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### Incident/recovery scenario (1 question)

### U04-IR-01

- **Question ID:** `U04-IR-01`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L3
- **Objective tested:** Respond safely under uncertainty using symptom →
  first action → decide → execute → verify → communicate → prevent.
- **Estimated time:** 12 minutes
- **Question/prompt:** A worker crashes after writing some output but
  before checkpoint completion; downstream notifications may already
  have been sent. What is the safe recovery plan? Evidence/timeline
  `[ILLUSTRATIVE — NOT EXECUTED]`: worker crashed after sink writes and
  before checkpoint commit; notification side effects may already exist.
- **Model answer:** Defects: (1) input retention is shorter than
  detection + recovery + replay needs; (2) checkpoint schedule may be
  too sparse; (3) no archive fallback; (4) no catch-up capacity/throttle
  plan; (5) no explicit unrecoverable-gap reporting. Align retention to
  worst-case outage and replay horizon, add a tested archive path or
  document the limit, and validate catch-up time.
- **Reasoning/worked solution:** Defects: (1) input retention is shorter
  than detection + recovery + replay needs; (2) checkpoint schedule may
  be too sparse; (3) no archive fallback; (4) no catch-up
  capacity/throttle plan; (5) no explicit unrecoverable-gap reporting.
  Align retention to worst-case outage and replay horizon, add a tested
  archive path or document the limit, and validate catch-up time.
- **Common wrong answers or failure modes:** Blind promotion; deletion
  of the last known-good backup; unbounded replay; trusting CR status;
  skipping evidence preservation or communication.
- **Evidence/verification:** Incident timeline, decision log, target
  identity, recovery-point evidence, application invariants, canary, and
  tracked follow-up.
- **Assumptions and limitations:** Illustrative scenario. Containment
  must stop ongoing harm while preserving necessary forensic evidence.

### Design question with scoring rubric (1 question)

### U04-DES-01

- **Question ID:** `U04-DES-01`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L4
- **Objective tested:** Produce a reviewable architecture/runbook with
  explicit trade-offs, ownership, safety gates, and verifiable
  acceptance criteria.
- **Estimated time:** 20 minutes
- **Question/prompt:** Design replay-safe recovery for a stream
  processor writing to a database and object store, including offsets,
  idempotency, retention, throttling, and reconciliation.
- **Model answer:** Defects: (1) input retention is shorter than
  detection + recovery + replay needs; (2) checkpoint schedule may be
  too sparse; (3) no archive fallback; (4) no catch-up capacity/throttle
  plan; (5) no explicit unrecoverable-gap reporting. Align retention to
  worst-case outage and replay horizon, add a tested archive path or
  document the limit, and validate catch-up time.
- **Reasoning/worked solution:** Defects: (1) input retention is shorter
  than detection + recovery + replay needs; (2) checkpoint schedule may
  be too sparse; (3) no archive fallback; (4) no catch-up
  capacity/throttle plan; (5) no explicit unrecoverable-gap reporting.
  Align retention to worst-case outage and replay horizon, add a tested
  archive path or document the limit, and validate catch-up time.
- **Common wrong answers or failure modes:** A diagram without
  reasoning; targets without evidence; complexity without ownership;
  hidden assumptions; no rollback or acceptance gate.
- **Evidence/verification:** Design record, dependency graph/table,
  named owners, explicit pass/fail checks, and a rehearsal result.
- **Assumptions and limitations:** Rubric totals 16 points. Adapt to
  real workloads only through authorized review.

### Additional questions (2 questions)

### U04-EX-01

- **Question ID:** `U04-EX-01`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L2
- **Objective tested:** Apply calculation reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** 1.2 million records replay at 20,000 records/min.
  Calculate ideal replay time before overhead.
- **Model answer:** Defects: (1) input retention is shorter than
  detection + recovery + replay needs; (2) checkpoint schedule may be
  too sparse; (3) no archive fallback; (4) no catch-up capacity/throttle
  plan; (5) no explicit unrecoverable-gap reporting. Align retention to
  worst-case outage and replay horizon, add a tested archive path or
  document the limit, and validate catch-up time.
- **Reasoning/worked solution:** Defects: (1) input retention is shorter
  than detection + recovery + replay needs; (2) checkpoint schedule may
  be too sparse; (3) no archive fallback; (4) no catch-up
  capacity/throttle plan; (5) no explicit unrecoverable-gap reporting.
  Align retention to worst-case outage and replay horizon, add a tested
  archive path or document the limit, and validate catch-up time.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

### U04-EX-02

- **Question ID:** `U04-EX-02`
- **Unit(s):** Unit 4 — Recovering data pipeline state and checkpoints
- **Level:** L3
- **Objective tested:** Apply diagnosis reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** Counts match but duplicate IDs and missing IDs
  coexist. Why are counts insufficient?
- **Model answer:** Defects: (1) input retention is shorter than
  detection + recovery + replay needs; (2) checkpoint schedule may be
  too sparse; (3) no archive fallback; (4) no catch-up capacity/throttle
  plan; (5) no explicit unrecoverable-gap reporting. Align retention to
  worst-case outage and replay horizon, add a tested archive path or
  document the limit, and validate catch-up time.
- **Reasoning/worked solution:** Defects: (1) input retention is shorter
  than detection + recovery + replay needs; (2) checkpoint schedule may
  be too sparse; (3) no archive fallback; (4) no catch-up
  capacity/throttle plan; (5) no explicit unrecoverable-gap reporting.
  Align retention to worst-case outage and replay horizon, add a tested
  archive path or document the limit, and validate catch-up time.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

------------------------------------------------------------------------

## Unit 5 — Recovering model artifacts and registry metadata

**Target file:**
`05-recovering-model-artifacts-and-registry-metadata.md`  
**Learning objectives:** artifact integrity and provenance, registry
aliases and version-triple consistency, restore versus retrain versus
rollback.

### Conceptual short answer (3 questions)

### U05-SA-01

- **Question ID:** `U05-SA-01`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L1
- **Objective tested:** artifact integrity and provenance
- **Estimated time:** 5 minutes
- **Question/prompt:** Registry digest is X but restored blob digest
  is Y. What should serving do?
- **Model answer:** Fail closed for that candidate, preserve evidence,
  and recover the expected artifact from a trusted source. Do not
  rewrite metadata automatically to match a suspect blob.
- **Reasoning/worked solution:** Fail closed for that candidate,
  preserve evidence, and recover the expected artifact from a trusted
  source. Do not rewrite metadata automatically to match a suspect blob.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U05-SA-02

- **Question ID:** `U05-SA-02`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L1
- **Objective tested:** registry aliases and version-triple consistency
- **Estimated time:** 5 minutes
- **Question/prompt:** Why is retraining not automatically equivalent to
  restoring a prior model?
- **Model answer:** Retraining can differ because of data, feature
  definitions, code, dependencies, seeds, runtime, or nondeterminism.
  Treat it as a new model version with lineage and regression evidence.
- **Reasoning/worked solution:** Retraining can differ because of data,
  feature definitions, code, dependencies, seeds, runtime, or
  nondeterminism. Treat it as a new model version with lineage and
  regression evidence.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U05-SA-03

- **Question ID:** `U05-SA-03`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L2
- **Objective tested:** restore versus retrain versus rollback
- **Estimated time:** 5 minutes
- **Question/prompt:** What must the model
  metadata/artifact/data-feature version triple prove?
- **Model answer:** The registry entry, exact artifact bytes, and
  data/feature/training lineage must correspond. Verify
  digest/signature, compatibility, alias history, and prediction
  behavior; timestamps alone are insufficient.
- **Reasoning/worked solution:** The registry entry, exact artifact
  bytes, and data/feature/training lineage must correspond. Verify
  digest/signature, compatibility, alias history, and prediction
  behavior; timestamps alone are insufficient.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### Multiple-choice (3 questions)

#### U05-MCQ-01 — prompt

Registry digest X, restored artifact digest Y. What should serving do?

- **A.** Load Y because it exists
- **B.** Fail closed for this candidate and preserve evidence
- **C.** Rewrite registry metadata to Y automatically
- **D.** Retrain and reuse the old version label

**Correct answer: B.**

- **A — why this distractor is wrong:** A blob's existence does not make
  a digest mismatch trustworthy. Option text: “Load Y because it exists”

- **B — why best:** Digest mismatch is an integrity failure until
  resolved against a trusted expected digest.

- **C — why this distractor is wrong:** Rewriting metadata to match
  suspect bytes can conceal corruption or substitution. Option text:
  “Rewrite registry metadata to Y automatically”

- **D — why this distractor is wrong:** Retraining produces a new
  artifact and does not resolve the identity of the original version.
  Option text: “Retrain and reuse the old version label”

- **Question ID:** `U05-MCQ-01`

- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata

- **Level:** L1

- **Objective tested:** Choose the safest evidence-based decision about
  artifact integrity and provenance.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Registry digest X, restored artifact digest Y.
  What should serving do?

- **Model answer:** B. - **B — why best:** Digest mismatch is an
  integrity failure until resolved against a trusted expected digest.

- **Reasoning/worked solution:** - **B — why best:** Digest mismatch is
  an integrity failure until resolved against a trusted expected digest.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U05-MCQ-02 — prompt

Why is retraining not equivalent to restoring?

- **A.** A retrained model is always identical
- **B.** Version numbers make models interchangeable
- **C.** Data, features, code, dependencies, seeds, and runtime can
  change outputs
- **D.** Retraining always reduces recovery time

**Correct answer: C.**

- **A — why this distractor is wrong:** Retraining is not guaranteed to
  reproduce the exact model or its provenance. Option text: “A retrained
  model is always identical”

- **B — why this distractor is wrong:** A version number alone does not
  prove artifact identity or feature compatibility. Option text:
  “Version numbers make models interchangeable”

- **C — why best:** Retraining may produce a different model and
  provenance; it must be treated as a new version.

- **D — why this distractor is wrong:** Retraining can take longer and
  does not inherently reduce recovery time. Option text: “Retraining
  always reduces recovery time”

- **Question ID:** `U05-MCQ-02`

- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  registry aliases and version-triple consistency.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Why is retraining not equivalent to restoring?

- **Model answer:** C. - **C — why best:** Retraining may produce a
  different model and provenance; it must be treated as a new version.

- **Reasoning/worked solution:** - **C — why best:** Retraining may
  produce a different model and provenance; it must be treated as a new
  version.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U05-MCQ-03 — prompt

Artifact hash passes but prediction regression fails tolerance. What is
next?

- **A.** Keep candidate out of promotion; investigate compatibility and
  validate an approved fallback
- **B.** Promote because hash is enough
- **C.** Increase tolerance after the fact
- **D.** Ignore prediction drift if pod is Ready

**Correct answer: A.**

- **A — why best:** Byte integrity is necessary but functional behavior
  must also pass.

- **B — why this distractor is wrong:** A passing hash does not override
  a failing prediction regression. Option text: “Promote because hash is
  enough”

- **C — why this distractor is wrong:** Changing tolerance after seeing
  the failure changes the acceptance criterion without approval. Option
  text: “Increase tolerance after the fact”

- **D — why this distractor is wrong:** Pod readiness does not test
  prediction quality or feature compatibility. Option text: “Ignore
  prediction drift if pod is Ready”

- **Question ID:** `U05-MCQ-03`

- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  restore versus retrain versus rollback.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Artifact hash passes but prediction regression
  fails tolerance. What is next?

- **Model answer:** A. - **A — why best:** Byte integrity is necessary
  but functional behavior must also pass.

- **Reasoning/worked solution:** - **A — why best:** Byte integrity is
  necessary but functional behavior must also pass.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

### Artifact interpretation (3 questions)

### U05-AI-01

- **Question ID:** `U05-AI-01`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L1
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Artifact hash passes but prediction regression
  fails approved tolerance. What next?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
expected_digest=sha256:aaa
restored_digest=sha256:bbb
prediction_regression=FAIL
```

- **Model answer:** Fail closed for that candidate, preserve evidence,
  and recover the expected artifact from a trusted source. Do not
  rewrite metadata automatically to match a suspect blob.
- **Reasoning/worked solution:** Fail closed for that candidate,
  preserve evidence, and recover the expected artifact from a trusted
  source. Do not rewrite metadata automatically to match a suspect blob.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U05-AI-02

- **Question ID:** `U05-AI-02`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L2
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Alias history says production-\>v42; restored
  registry says production-\>v40. What evidence is needed?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
live_alias=production->v42
backup_alias=production->v40
v42_digest_report=missing
```

- **Model answer:** Retraining can differ because of data, feature
  definitions, code, dependencies, seeds, runtime, or nondeterminism.
  Treat it as a new model version with lineage and regression evidence.
- **Reasoning/worked solution:** Retraining can differ because of data,
  feature definitions, code, dependencies, seeds, runtime, or
  nondeterminism. Treat it as a new model version with lineage and
  regression evidence.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U05-AI-03

- **Question ID:** `U05-AI-03`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L3
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Model registry unavailable at startup. Define a
  safe fallback policy and its SLI.

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
registry=unavailable
fallback_artifact_digest=unknown
fallback_ratio=not_measured
```

- **Model answer:** The registry entry, exact artifact bytes, and
  data/feature/training lineage must correspond. Verify
  digest/signature, compatibility, alias history, and prediction
  behavior; timestamps alone are insufficient.
- **Reasoning/worked solution:** The registry entry, exact artifact
  bytes, and data/feature/training lineage must correspond. Verify
  digest/signature, compatibility, alias history, and prediction
  behavior; timestamps alone are insufficient.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### Artifact review (3 questions)

### U05-AR-01

- **Question ID:** `U05-AR-01`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L2
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Registry database restored but model blobs are
  absent. Identify at least three defects and, for each, explain the
  failure mechanism, correction, and test/evidence that would prove the
  correction works.
- **Model answer:** Defects: (1) artifact bytes are not verified; (2)
  signature/provenance is missing; (3) alias history and feature schema
  are unverified; (4) no prediction regression; (5) no fail-closed gate.
  Restore the exact version triple and validate digest, signature,
  feature contract, and predictions before promotion. Pass with a
  negative digest-mismatch test.
- **Reasoning/worked solution:** Defects: (1) artifact bytes are not
  verified; (2) signature/provenance is missing; (3) alias history and
  feature schema are unverified; (4) no prediction regression; (5) no
  fail-closed gate. Restore the exact version triple and validate
  digest, signature, feature contract, and predictions before promotion.
  Pass with a negative digest-mismatch test.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U05-AR-02

- **Question ID:** `U05-AR-02`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Serving falls back to an unverified local model
  when registry is down. Identify at least three defects and, for each,
  explain the failure mechanism, correction, and test/evidence that
  would prove the correction works.
- **Model answer:** Defects: (1) retraining can produce different
  outputs; (2) lineage and training inputs may differ; (3) old version
  label corrupts provenance; (4) no approval/alias history; (5) no
  regression evidence. Assign a new model version and record lineage or
  restore a verified prior artifact. Pass with immutable audit records
  and approved regression tests.
- **Reasoning/worked solution:** Defects: (1) retraining can produce
  different outputs; (2) lineage and training inputs may differ; (3) old
  version label corrupts provenance; (4) no approval/alias history; (5)
  no regression evidence. Assign a new model version and record lineage
  or restore a verified prior artifact. Pass with immutable audit
  records and approved regression tests.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U05-AR-03

- **Question ID:** `U05-AR-03`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Team relabels a retrained model as the old
  version. Identify at least three defects and, for each, explain the
  failure mechanism, correction, and test/evidence that would prove the
  correction works.
- **Model answer:** Defects: (1) dynamic alias can move during
  outage; (2) local fallback is unverified; (3) fallback behavior is not
  observable; (4) feature/runtime compatibility is unknown; (5) no
  outage test. Pin verified digest and define an approved fail-closed or
  verified fallback policy, emit fallback-ratio SLI, and test startup
  with registry unavailable.
- **Reasoning/worked solution:** Defects: (1) dynamic alias can move
  during outage; (2) local fallback is unverified; (3) fallback behavior
  is not observable; (4) feature/runtime compatibility is unknown; (5)
  no outage test. Pin verified digest and define an approved fail-closed
  or verified fallback policy, emit fallback-ratio SLI, and test startup
  with registry unavailable.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### Incident/recovery scenario (1 question)

### U05-IR-01

- **Question ID:** `U05-IR-01`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L3
- **Objective tested:** Respond safely under uncertainty using symptom →
  first action → decide → execute → verify → communicate → prevent.
- **Estimated time:** 12 minutes
- **Question/prompt:** Model serving fails after a registry outage; a
  cached model loads but its digest and feature schema are unknown. What
  should the team do? Evidence/timeline `[ILLUSTRATIVE — NOT EXECUTED]`:
  registry outage begins T+0; cached artifact loads; digest and feature
  schema unknown; prediction regression not run.
- **Model answer:** Defects: (1) dynamic alias can move during
  outage; (2) local fallback is unverified; (3) fallback behavior is not
  observable; (4) feature/runtime compatibility is unknown; (5) no
  outage test. Pin verified digest and define an approved fail-closed or
  verified fallback policy, emit fallback-ratio SLI, and test startup
  with registry unavailable.
- **Reasoning/worked solution:** Defects: (1) dynamic alias can move
  during outage; (2) local fallback is unverified; (3) fallback behavior
  is not observable; (4) feature/runtime compatibility is unknown; (5)
  no outage test. Pin verified digest and define an approved fail-closed
  or verified fallback policy, emit fallback-ratio SLI, and test startup
  with registry unavailable.
- **Common wrong answers or failure modes:** Blind promotion; deletion
  of the last known-good backup; unbounded replay; trusting CR status;
  skipping evidence preservation or communication.
- **Evidence/verification:** Incident timeline, decision log, target
  identity, recovery-point evidence, application invariants, canary, and
  tracked follow-up.
- **Assumptions and limitations:** Illustrative scenario. Containment
  must stop ongoing harm while preserving necessary forensic evidence.

### Design question with scoring rubric (1 question)

### U05-DES-01

- **Question ID:** `U05-DES-01`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L4
- **Objective tested:** Produce a reviewable architecture/runbook with
  explicit trade-offs, ownership, safety gates, and verifiable
  acceptance criteria.
- **Estimated time:** 20 minutes
- **Question/prompt:** Design model recovery covering registry metadata,
  artifact bytes, lineage, alias history, keys/signatures, and serving
  validation.
- **Model answer:** Defects: (1) dynamic alias can move during
  outage; (2) local fallback is unverified; (3) fallback behavior is not
  observable; (4) feature/runtime compatibility is unknown; (5) no
  outage test. Pin verified digest and define an approved fail-closed or
  verified fallback policy, emit fallback-ratio SLI, and test startup
  with registry unavailable.
- **Reasoning/worked solution:** Defects: (1) dynamic alias can move
  during outage; (2) local fallback is unverified; (3) fallback behavior
  is not observable; (4) feature/runtime compatibility is unknown; (5)
  no outage test. Pin verified digest and define an approved fail-closed
  or verified fallback policy, emit fallback-ratio SLI, and test startup
  with registry unavailable.
- **Common wrong answers or failure modes:** A diagram without
  reasoning; targets without evidence; complexity without ownership;
  hidden assumptions; no rollback or acceptance gate.
- **Evidence/verification:** Design record, dependency graph/table,
  named owners, explicit pass/fail checks, and a rehearsal result.
- **Assumptions and limitations:** Rubric totals 16 points. Adapt to
  real workloads only through authorized review.

### Additional questions (2 questions)

### U05-EX-01

- **Question ID:** `U05-EX-01`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L2
- **Objective tested:** Apply decision reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** Last verified model is older but hash, feature
  contract, and prediction tests pass; newest registry entry has no
  blob. What is safer?
- **Model answer:** Defects: (1) dynamic alias can move during
  outage; (2) local fallback is unverified; (3) fallback behavior is not
  observable; (4) feature/runtime compatibility is unknown; (5) no
  outage test. Pin verified digest and define an approved fail-closed or
  verified fallback policy, emit fallback-ratio SLI, and test startup
  with registry unavailable.
- **Reasoning/worked solution:** Defects: (1) dynamic alias can move
  during outage; (2) local fallback is unverified; (3) fallback behavior
  is not observable; (4) feature/runtime compatibility is unknown; (5)
  no outage test. Pin verified digest and define an approved fail-closed
  or verified fallback policy, emit fallback-ratio SLI, and test startup
  with registry unavailable.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

### U05-EX-02

- **Question ID:** `U05-EX-02`
- **Unit(s):** Unit 5 — Recovering model artifacts and registry metadata
- **Level:** L3
- **Objective tested:** Apply evidence reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** What does a matching artifact hash prove—and not
  prove?
- **Model answer:** Defects: (1) dynamic alias can move during
  outage; (2) local fallback is unverified; (3) fallback behavior is not
  observable; (4) feature/runtime compatibility is unknown; (5) no
  outage test. Pin verified digest and define an approved fail-closed or
  verified fallback policy, emit fallback-ratio SLI, and test startup
  with registry unavailable.
- **Reasoning/worked solution:** Defects: (1) dynamic alias can move
  during outage; (2) local fallback is unverified; (3) fallback behavior
  is not observable; (4) feature/runtime compatibility is unknown; (5)
  no outage test. Pin verified digest and define an approved fail-closed
  or verified fallback policy, emit fallback-ratio SLI, and test startup
  with registry unavailable.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

------------------------------------------------------------------------

## Unit 6 — Regional failure and dependency outage strategies

**Target file:**
`06-regional-failure-and-dependency-outage-strategies.md`  
**Learning objectives:** failure domains and regional simulation limits,
replication lag, fencing, split brain, dependency-aware failover and
fail-back.

### Conceptual short answer (3 questions)

### U06-SA-01

- **Question ID:** `U06-SA-01`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L1
- **Objective tested:** failure domains and regional simulation limits
- **Estimated time:** 5 minutes
- **Question/prompt:** Primary is unreachable from one segment and
  replica lag is unknown. Should you promote immediately?
- **Model answer:** Not from those facts alone. Gather independent
  health and lag evidence, assess RPO, establish fencing and authority,
  and communicate the action-versus-delay trade-off. A network partition
  may mimic primary failure.
- **Reasoning/worked solution:** Not from those facts alone. Gather
  independent health and lag evidence, assess RPO, establish fencing and
  authority, and communicate the action-versus-delay trade-off. A
  network partition may mimic primary failure.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U06-SA-02

- **Question ID:** `U06-SA-02`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L1
- **Objective tested:** replication lag, fencing, split brain
- **Estimated time:** 5 minutes
- **Question/prompt:** Why is fencing required before promoting a
  standby?
- **Model answer:** Fencing prevents the old primary from accepting
  writes after promotion; without it, two writers can diverge. Verify
  the actual fencing mechanism before promotion.
- **Reasoning/worked solution:** Fencing prevents the old primary from
  accepting writes after promotion; without it, two writers can diverge.
  Verify the actual fencing mechanism before promotion.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U06-SA-03

- **Question ID:** `U06-SA-03`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L2
- **Objective tested:** dependency-aware failover and fail-back
- **Estimated time:** 5 minutes
- **Question/prompt:** What can a two-kind-cluster laptop drill prove
  about regional resilience?
- **Model answer:** It can rehearse workflow and local dependency
  handling, but clusters share host, power, storage, and often network
  failure domains. It does not prove geographic independence or real
  regional RTO/RPO.
- **Reasoning/worked solution:** It can rehearse workflow and local
  dependency handling, but clusters share host, power, storage, and
  often network failure domains. It does not prove geographic
  independence or real regional RTO/RPO.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### Multiple-choice (3 questions)

#### U06-MCQ-01 — prompt

Primary is unreachable from one segment and replica lag is unknown. What
is safest?

- **A.** Promote immediately
- **B.** Gather independent health/lag evidence and establish fencing
  before promotion
- **C.** Wait forever without communication
- **D.** Delete primary metadata

**Correct answer: B.**

- **A — why this distractor is wrong:** Immediate promotion without
  evidence risks split brain and unknown data loss. Option text:
  “Promote immediately”

- **B — why best:** Partition can mimic failure; fencing and bounded
  decision criteria reduce split-brain risk.

- **C — why this distractor is wrong:** Waiting indefinitely ignores
  business impact and the need for bounded decisions and updates. Option
  text: “Wait forever without communication”

- **D — why this distractor is wrong:** Deleting metadata does not
  establish authority or fence the old writer. Option text: “Delete
  primary metadata”

- **Question ID:** `U06-MCQ-01`

- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies

- **Level:** L1

- **Objective tested:** Choose the safest evidence-based decision about
  failure domains and regional simulation limits.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Primary is unreachable from one segment and
  replica lag is unknown. What is safest?

- **Model answer:** B. - **B — why best:** Partition can mimic failure;
  fencing and bounded decision criteria reduce split-brain risk.

- **Reasoning/worked solution:** - **B — why best:** Partition can mimic
  failure; fencing and bounded decision criteria reduce split-brain
  risk.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U06-MCQ-02 — prompt

Why fence the old primary?

- **A.** To lower storage costs
- **B.** To reduce DNS TTL
- **C.** To prevent the old primary continuing authoritative writes
- **D.** To prove replica data is current

**Correct answer: C.**

- **A — why this distractor is wrong:** Storage cost is unrelated to the
  purpose of fencing. Option text: “To lower storage costs”

- **B — why this distractor is wrong:** DNS TTL may affect traffic
  cutover but does not stop the old primary writing. Option text: “To
  reduce DNS TTL”

- **C — why best:** Fencing prevents dual writers; it does not itself
  prove data currency.

- **D — why this distractor is wrong:** Fencing prevents dual writers;
  it does not prove replica currency. Option text: “To prove replica
  data is current”

- **Question ID:** `U06-MCQ-02`

- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  replication lag, fencing, split brain.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Why fence the old primary?

- **Model answer:** C. - **C — why best:** Fencing prevents dual
  writers; it does not itself prove data currency.

- **Reasoning/worked solution:** - **C — why best:** Fencing prevents
  dual writers; it does not itself prove data currency.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U06-MCQ-03 — prompt

Two kind clusters share one laptop. What does a drill prove?

- **A.** Workflow behavior in a shared local failure domain, not real
  regional independence
- **B.** Two independent regions
- **C.** Real cloud provider regional SLA
- **D.** Nothing useful at all

**Correct answer: A.**

- **A — why best:** Local labs can test procedures but cannot prove
  geographic failure-domain separation.

- **B — why this distractor is wrong:** Different contexts do not create
  separate physical regions or failure domains. Option text: “Two
  independent regions”

- **C — why this distractor is wrong:** A local laptop test cannot
  establish a cloud provider's real regional SLA. Option text: “Real
  cloud provider regional SLA”

- **D — why this distractor is wrong:** Local clusters are useful for
  workflow practice even though they cannot prove regional independence.
  Option text: “Nothing useful at all”

- **Question ID:** `U06-MCQ-03`

- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  dependency-aware failover and fail-back.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Two kind clusters share one laptop. What does a
  drill prove?

- **Model answer:** A. - **A — why best:** Local labs can test
  procedures but cannot prove geographic failure-domain separation.

- **Reasoning/worked solution:** - **A — why best:** Local labs can test
  procedures but cannot prove geographic failure-domain separation.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

### Artifact interpretation (3 questions)

### U06-AI-01

- **Question ID:** `U06-AI-01`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L1
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Lag telemetry is stale, primary unreachable, RPO
  2 minutes. What information is missing?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
primary_probe=timeout
replica_lag=unknown
fencing=pending
promotion_approved=yes
```

- **Model answer:** Not from those facts alone. Gather independent
  health and lag evidence, assess RPO, establish fencing and authority,
  and communicate the action-versus-delay trade-off. A network partition
  may mimic primary failure.
- **Reasoning/worked solution:** Not from those facts alone. Gather
  independent health and lag evidence, assess RPO, establish fencing and
  authority, and communicate the action-versus-delay trade-off. A
  network partition may mimic primary failure.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U06-AI-02

- **Question ID:** `U06-AI-02`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L2
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Replica is 90 seconds behind with a 2-minute RPO.
  Can you declare success?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
replica_lag=90s
RPO_target=120s
continuity_check=unknown
```

- **Model answer:** Fencing prevents the old primary from accepting
  writes after promotion; without it, two writers can diverge. Verify
  the actual fencing mechanism before promotion.
- **Reasoning/worked solution:** Fencing prevents the old primary from
  accepting writes after promotion; without it, two writers can diverge.
  Verify the actual fencing mechanism before promotion.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U06-AI-03

- **Question ID:** `U06-AI-03`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L3
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Runbook is stored only on the failed cluster.
  What resilience gap exists?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
runbook_location=inside_primary_cluster
independent_copy=none
bootstrap_contacts=unknown
```

- **Model answer:** It can rehearse workflow and local dependency
  handling, but clusters share host, power, storage, and often network
  failure domains. It does not prove geographic independence or real
  regional RTO/RPO.
- **Reasoning/worked solution:** It can rehearse workflow and local
  dependency handling, but clusters share host, power, storage, and
  often network failure domains. It does not prove geographic
  independence or real regional RTO/RPO.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### Artifact review (3 questions)

### U06-AR-01

- **Question ID:** `U06-AR-01`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L2
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Failover triggers on three failed pings with no
  fencing. Identify at least three defects and, for each, explain the
  failure mechanism, correction, and test/evidence that would prove the
  correction works.
- **Model answer:** Defects: (1) ping timeout can be a network
  partition; (2) no fencing; (3) replication lag/RPO is unknown; (4) no
  independent health signals; (5) no communication or owner. Require
  bounded independent evidence and fencing before promotion under the
  approved policy. Pass by simulating a partition and proving there are
  never two writable primaries.
- **Reasoning/worked solution:** Defects: (1) ping timeout can be a
  network partition; (2) no fencing; (3) replication lag/RPO is
  unknown; (4) no independent health signals; (5) no communication or
  owner. Require bounded independent evidence and fencing before
  promotion under the approved policy. Pass by simulating a partition
  and proving there are never two writable primaries.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U06-AR-02

- **Question ID:** `U06-AR-02`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Plan says two kind clusters are independent
  regions. Identify at least three defects and, for each, explain the
  failure mechanism, correction, and test/evidence that would prove the
  correction works.
- **Model answer:** Defects: (1) local clusters share
  host/power/storage/network; (2) no independent provider/quota
  proof; (3) identity/key path is not tested; (4) workflow simulation is
  mislabeled as regional assurance; (5) no real failure-domain evidence.
  Re-label as workflow rehearsal and plan separate authorized validation
  in independent domains.
- **Reasoning/worked solution:** Defects: (1) local clusters share
  host/power/storage/network; (2) no independent provider/quota
  proof; (3) identity/key path is not tested; (4) workflow simulation is
  mislabeled as regional assurance; (5) no real failure-domain evidence.
  Re-label as workflow rehearsal and plan separate authorized validation
  in independent domains.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U06-AR-03

- **Question ID:** `U06-AR-03`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Fail-back occurs as soon as old primary becomes
  reachable. Identify at least three defects and, for each, explain the
  failure mechanism, correction, and test/evidence that would prove the
  correction works.
- **Model answer:** Defects: (1) old primary may have divergent
  writes; (2) fencing/reconciliation is missing; (3) replication
  direction is not verified; (4) security parity and dependency health
  are absent; (5) no rollback/approval. Define catch-up, reconciliation,
  write authority transfer, staged traffic cutover, and fail-back
  criteria. Pass with a rehearsal showing no write overlap.
- **Reasoning/worked solution:** Defects: (1) old primary may have
  divergent writes; (2) fencing/reconciliation is missing; (3)
  replication direction is not verified; (4) security parity and
  dependency health are absent; (5) no rollback/approval. Define
  catch-up, reconciliation, write authority transfer, staged traffic
  cutover, and fail-back criteria. Pass with a rehearsal showing no
  write overlap.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### Incident/recovery scenario (1 question)

### U06-IR-01

- **Question ID:** `U06-IR-01`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L3
- **Objective tested:** Respond safely under uncertainty using symptom →
  first action → decide → execute → verify → communicate → prevent.
- **Estimated time:** 12 minutes
- **Question/prompt:** Primary connectivity is intermittent; replication
  lag telemetry is stale; business RPO is 5 minutes. How should the team
  decide whether to fail over? Evidence/timeline
  `[ILLUSTRATIVE — NOT EXECUTED]`: primary connectivity intermittent;
  lag metric stale; RPO target 5 min; fencing status unknown.
- **Model answer:** Defects: (1) old primary may have divergent
  writes; (2) fencing/reconciliation is missing; (3) replication
  direction is not verified; (4) security parity and dependency health
  are absent; (5) no rollback/approval. Define catch-up, reconciliation,
  write authority transfer, staged traffic cutover, and fail-back
  criteria. Pass with a rehearsal showing no write overlap.
- **Reasoning/worked solution:** Defects: (1) old primary may have
  divergent writes; (2) fencing/reconciliation is missing; (3)
  replication direction is not verified; (4) security parity and
  dependency health are absent; (5) no rollback/approval. Define
  catch-up, reconciliation, write authority transfer, staged traffic
  cutover, and fail-back criteria. Pass with a rehearsal showing no
  write overlap.
- **Common wrong answers or failure modes:** Blind promotion; deletion
  of the last known-good backup; unbounded replay; trusting CR status;
  skipping evidence preservation or communication.
- **Evidence/verification:** Incident timeline, decision log, target
  identity, recovery-point evidence, application invariants, canary, and
  tracked follow-up.
- **Assumptions and limitations:** Illustrative scenario. Containment
  must stop ongoing harm while preserving necessary forensic evidence.

### Design question with scoring rubric (1 question)

### U06-DES-01

- **Question ID:** `U06-DES-01`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L4
- **Objective tested:** Produce a reviewable architecture/runbook with
  explicit trade-offs, ownership, safety gates, and verifiable
  acceptance criteria.
- **Estimated time:** 20 minutes
- **Question/prompt:** Design a failover/fail-back decision tree for a
  database with asynchronous replication and dependencies on DNS,
  identity, secrets, and registry.
- **Model answer:** Defects: (1) old primary may have divergent
  writes; (2) fencing/reconciliation is missing; (3) replication
  direction is not verified; (4) security parity and dependency health
  are absent; (5) no rollback/approval. Define catch-up, reconciliation,
  write authority transfer, staged traffic cutover, and fail-back
  criteria. Pass with a rehearsal showing no write overlap.
- **Reasoning/worked solution:** Defects: (1) old primary may have
  divergent writes; (2) fencing/reconciliation is missing; (3)
  replication direction is not verified; (4) security parity and
  dependency health are absent; (5) no rollback/approval. Define
  catch-up, reconciliation, write authority transfer, staged traffic
  cutover, and fail-back criteria. Pass with a rehearsal showing no
  write overlap.
- **Common wrong answers or failure modes:** A diagram without
  reasoning; targets without evidence; complexity without ownership;
  hidden assumptions; no rollback or acceptance gate.
- **Evidence/verification:** Design record, dependency graph/table,
  named owners, explicit pass/fail checks, and a rehearsal result.
- **Assumptions and limitations:** Rubric totals 16 points. Adapt to
  real workloads only through authorized review.

### Additional questions (2 questions)

### U06-EX-01

- **Question ID:** `U06-EX-01`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L2
- **Objective tested:** Apply calculation reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** Replica lag is 90 seconds; RPO target is 2
  minutes. Can compliance be declared?
- **Model answer:** Defects: (1) old primary may have divergent
  writes; (2) fencing/reconciliation is missing; (3) replication
  direction is not verified; (4) security parity and dependency health
  are absent; (5) no rollback/approval. Define catch-up, reconciliation,
  write authority transfer, staged traffic cutover, and fail-back
  criteria. Pass with a rehearsal showing no write overlap.
- **Reasoning/worked solution:** Defects: (1) old primary may have
  divergent writes; (2) fencing/reconciliation is missing; (3)
  replication direction is not verified; (4) security parity and
  dependency health are absent; (5) no rollback/approval. Define
  catch-up, reconciliation, write authority transfer, staged traffic
  cutover, and fail-back criteria. Pass with a rehearsal showing no
  write overlap.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

### U06-EX-02

- **Question ID:** `U06-EX-02`
- **Unit(s):** Unit 6 — Regional failure and dependency outage
  strategies
- **Level:** L3
- **Objective tested:** Apply decision reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** Management plane is unavailable but database and
  standby are reachable. What should the runbook provide?
- **Model answer:** Defects: (1) old primary may have divergent
  writes; (2) fencing/reconciliation is missing; (3) replication
  direction is not verified; (4) security parity and dependency health
  are absent; (5) no rollback/approval. Define catch-up, reconciliation,
  write authority transfer, staged traffic cutover, and fail-back
  criteria. Pass with a rehearsal showing no write overlap.
- **Reasoning/worked solution:** Defects: (1) old primary may have
  divergent writes; (2) fencing/reconciliation is missing; (3)
  replication direction is not verified; (4) security parity and
  dependency health are absent; (5) no rollback/approval. Define
  catch-up, reconciliation, write authority transfer, staged traffic
  cutover, and fail-back criteria. Pass with a rehearsal showing no
  write overlap.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

------------------------------------------------------------------------

## Unit 7 — Restore drills and recovery evidence

**Target file:** `07-restore-drills-and-recovery-evidence.md`  
**Learning objectives:** restore-first and layered verification, RTA/RPA
measurement and evidence integrity, drill freshness, cold-read,
remediation.

### Conceptual short answer (3 questions)

### U07-SA-01

- **Question ID:** `U07-SA-01`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L1
- **Objective tested:** restore-first and layered verification
- **Estimated time:** 5 minutes
- **Question/prompt:** Restore command succeeds but application
  invariant fails. What is the drill result?
- **Model answer:** The drill fails acceptance: successful operation
  status is necessary but not sufficient. Preserve evidence, diagnose
  the invariant failure, fix and rerun.
- **Reasoning/worked solution:** The drill fails acceptance: successful
  operation status is necessary but not sufficient. Preserve evidence,
  diagnose the invariant failure, fix and rerun.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U07-SA-02

- **Question ID:** `U07-SA-02`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L1
- **Objective tested:** RTA/RPA measurement and evidence integrity
- **Estimated time:** 5 minutes
- **Question/prompt:** What should an evidence bundle contain to support
  reproducibility?
- **Model answer:** Include scope/hypothesis, versions, recovery-point
  identity, timestamps, commands/runbook steps, restore status,
  structural/checksum/application checks, RTA/RPA, logs, evidence
  hashes, exceptions, owners, and remediation.
- **Reasoning/worked solution:** Include scope/hypothesis, versions,
  recovery-point identity, timestamps, commands/runbook steps, restore
  status, structural/checksum/application checks, RTA/RPA, logs,
  evidence hashes, exceptions, owners, and remediation.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U07-SA-03

- **Question ID:** `U07-SA-03`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L2
- **Objective tested:** drill freshness, cold-read, remediation
- **Estimated time:** 5 minutes
- **Question/prompt:** Why should recovery evidence expire or trigger
  retesting after material changes?
- **Model answer:** Versions, schemas, dependencies, credentials,
  workloads, and paths change. A past pass may no longer describe
  today's recovery. Set freshness windows and change-triggered drills.
- **Reasoning/worked solution:** Versions, schemas, dependencies,
  credentials, workloads, and paths change. A past pass may no longer
  describe today's recovery. Set freshness windows and change-triggered
  drills.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### Multiple-choice (3 questions)

#### U07-MCQ-01 — prompt

Restore succeeds but an application invariant fails. What is the result?

- **A.** Pass because command succeeded
- **B.** Failed drill; preserve evidence, diagnose, and retest
- **C.** Pass if pod is Ready
- **D.** Delete logs and rerun

**Correct answer: B.**

- **A — why this distractor is wrong:** A successful restore command is
  only one layer; the invariant failure means correctness is not
  established. Option text: “Pass because command succeeded”

- **B — why best:** Application correctness is a required recovery gate.

- **C — why this distractor is wrong:** Pod readiness is not a
  substitute for data and application invariants. Option text: “Pass if
  pod is Ready”

- **D — why this distractor is wrong:** Deleting logs destroys
  diagnostic evidence and does not correct the failure. Option text:
  “Delete logs and rerun”

- **Question ID:** `U07-MCQ-01`

- **Unit(s):** Unit 7 — Restore drills and recovery evidence

- **Level:** L1

- **Objective tested:** Choose the safest evidence-based decision about
  restore-first and layered verification.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Restore succeeds but an application invariant
  fails. What is the result?

- **Model answer:** B. - **B — why best:** Application correctness is a
  required recovery gate.

- **Reasoning/worked solution:** - **B — why best:** Application
  correctness is a required recovery gate.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U07-MCQ-02 — prompt

What does an evidence hash prove?

- **A.** That recovery was correct
- **B.** That all required checks were performed
- **C.** Integrity of the hashed bytes relative to a trusted hash, not
  truth or completeness
- **D.** That timestamps are accurate

**Correct answer: C.**

- **A — why this distractor is wrong:** A hash does not establish that
  the recovery process itself was correct. Option text: “That recovery
  was correct”

- **B — why this distractor is wrong:** A hash cannot prove that
  required checks were performed or that the evidence is complete.
  Option text: “That all required checks were performed”

- **C — why best:** A hash detects later byte changes under trusted
  handling but does not validate the content's claims.

- **D — why this distractor is wrong:** A hash does not validate clock
  accuracy or timestamp provenance. Option text: “That timestamps are
  accurate”

- **Question ID:** `U07-MCQ-02`

- **Unit(s):** Unit 7 — Restore drills and recovery evidence

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  RTA/RPA measurement and evidence integrity.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** What does an evidence hash prove?

- **Model answer:** C. - **C — why best:** A hash detects later byte
  changes under trusted handling but does not validate the content's
  claims.

- **Reasoning/worked solution:** - **C — why best:** A hash detects
  later byte changes under trusted handling but does not validate the
  content's claims.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U07-MCQ-03 — prompt

Why expire old drill evidence?

- **A.** Recovery paths and dependencies change, so stale evidence must
  be retested
- **B.** Historical success is always valid
- **C.** To reduce documentation work only
- **D.** Because hashes expire automatically

**Correct answer: A.**

- **A — why best:** Evidence is valid only within stated assumptions,
  versions, and freshness windows.

- **B — why this distractor is wrong:** Historical success can become
  stale after dependency, schema, credential, or version changes. Option
  text: “Historical success is always valid”

- **C — why this distractor is wrong:** Evidence freshness is a
  reliability control, not merely documentation overhead. Option text:
  “To reduce documentation work only”

- **D — why this distractor is wrong:** Hashes do not automatically
  expire; freshness is an operational policy. Option text: “Because
  hashes expire automatically”

- **Question ID:** `U07-MCQ-03`

- **Unit(s):** Unit 7 — Restore drills and recovery evidence

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  drill freshness, cold-read, remediation.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Why expire old drill evidence?

- **Model answer:** A. - **A — why best:** Evidence is valid only within
  stated assumptions, versions, and freshness windows.

- **Reasoning/worked solution:** - **A — why best:** Evidence is valid
  only within stated assumptions, versions, and freshness windows.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

### Artifact interpretation (3 questions)

### U07-AI-01

- **Question ID:** `U07-AI-01`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L1
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Report: backup PASS, restore PASS, checksum FAIL,
  canary NOT RUN. Is the drill green?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
backup_job=PASS
restore_operation=PASS
checksum=FAIL
application_canary=NOT_RUN
```

- **Model answer:** The drill fails acceptance: successful operation
  status is necessary but not sufficient. Preserve evidence, diagnose
  the invariant failure, fix and rerun.
- **Reasoning/worked solution:** The drill fails acceptance: successful
  operation status is necessary but not sufficient. Preserve evidence,
  diagnose the invariant failure, fix and rerun.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U07-AI-02

- **Question ID:** `U07-AI-02`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L2
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Start 10:00; usable canary 10:38; restore
  completed 10:20. Calculate RTA.

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
manifest_hash=missing
start_timestamp=present
end_timestamp=missing
tool_version=missing
```

- **Model answer:** Include scope/hypothesis, versions, recovery-point
  identity, timestamps, commands/runbook steps, restore status,
  structural/checksum/application checks, RTA/RPA, logs, evidence
  hashes, exceptions, owners, and remediation.
- **Reasoning/worked solution:** Include scope/hypothesis, versions,
  recovery-point identity, timestamps, commands/runbook steps, restore
  status, structural/checksum/application checks, RTA/RPA, logs,
  evidence hashes, exceptions, owners, and remediation.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U07-AI-03

- **Question ID:** `U07-AI-03`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L3
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Evidence hash matches but no application
  invariant is recorded. What remains unknown?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
restore_finished=09:10
schema_check=PASS
checksum=PASS
canary_pass=09:26
traffic_open=09:30
```

- **Model answer:** Versions, schemas, dependencies, credentials,
  workloads, and paths change. A past pass may no longer describe
  today's recovery. Set freshness windows and change-triggered drills.
- **Reasoning/worked solution:** Versions, schemas, dependencies,
  credentials, workloads, and paths change. A past pass may no longer
  describe today's recovery. Set freshness windows and change-triggered
  drills.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### Artifact review (3 questions)

### U07-AR-01

- **Question ID:** `U07-AR-01`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L2
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Green backup job and restored pod screenshot are
  treated as proof. Identify at least three defects and, for each,
  explain the failure mechanism, correction, and test/evidence that
  would prove the correction works.
- **Model answer:** Defects: (1) job status is not restore proof; (2)
  pod readiness is not application correctness; (3)
  checksum/schema/invariants are absent; (4) RTA/RPA are not
  measured; (5) evidence timestamps/hash are missing. Add layered
  validation and a reproducible evidence bundle. Pass when intentional
  corruption or missing-object tests fail the drill.
- **Reasoning/worked solution:** Defects: (1) job status is not restore
  proof; (2) pod readiness is not application correctness; (3)
  checksum/schema/invariants are absent; (4) RTA/RPA are not
  measured; (5) evidence timestamps/hash are missing. Add layered
  validation and a reproducible evidence bundle. Pass when intentional
  corruption or missing-object tests fail the drill.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U07-AR-02

- **Question ID:** `U07-AR-02`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Permanent green badge has no tested version/date.
  Identify at least three defects and, for each, explain the failure
  mechanism, correction, and test/evidence that would prove the
  correction works.
- **Model answer:** Defects: (1) evidence has no freshness window; (2)
  version/dependency drift is invisible; (3) no owner; (4) no
  change-triggered retest; (5) no remediation link. Define expiry and
  change-triggered drills, retain tested versions and owner, and alert
  on stale evidence. Pass with an expired-evidence test that blocks a
  green readiness claim.
- **Reasoning/worked solution:** Defects: (1) evidence has no freshness
  window; (2) version/dependency drift is invisible; (3) no owner; (4)
  no change-triggered retest; (5) no remediation link. Define expiry and
  change-triggered drills, retain tested versions and owner, and alert
  on stale evidence. Pass with an expired-evidence test that blocks a
  green readiness claim.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U07-AR-03

- **Question ID:** `U07-AR-03`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Only runbook author can complete drill because
  steps are undocumented. Identify at least three defects and, for each,
  explain the failure mechanism, correction, and test/evidence that
  would prove the correction works.
- **Model answer:** Defects: (1) runbook depends on author
  knowledge; (2) hidden fixes make the result non-repeatable; (3)
  undocumented changes bypass review; (4) no deviation log; (5) no
  retest. Have an independent cold reader execute it, record deviations,
  review changes, and repeat. Pass when the procedure works without
  verbal coaching.
- **Reasoning/worked solution:** Defects: (1) runbook depends on author
  knowledge; (2) hidden fixes make the result non-repeatable; (3)
  undocumented changes bypass review; (4) no deviation log; (5) no
  retest. Have an independent cold reader execute it, record deviations,
  review changes, and repeat. Pass when the procedure works without
  verbal coaching.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### Incident/recovery scenario (1 question)

### U07-IR-01

- **Question ID:** `U07-IR-01`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L3
- **Objective tested:** Respond safely under uncertainty using symptom →
  first action → decide → execute → verify → communicate → prevent.
- **Estimated time:** 12 minutes
- **Question/prompt:** A scheduled restore drill reports successful
  restore status but object checksum and application canary fail. What
  happens next? Evidence/timeline `[ILLUSTRATIVE — NOT EXECUTED]`:
  restore operation reports success; checksum and canary fail; promotion
  has not occurred.
- **Model answer:** Defects: (1) runbook depends on author
  knowledge; (2) hidden fixes make the result non-repeatable; (3)
  undocumented changes bypass review; (4) no deviation log; (5) no
  retest. Have an independent cold reader execute it, record deviations,
  review changes, and repeat. Pass when the procedure works without
  verbal coaching.
- **Reasoning/worked solution:** Defects: (1) runbook depends on author
  knowledge; (2) hidden fixes make the result non-repeatable; (3)
  undocumented changes bypass review; (4) no deviation log; (5) no
  retest. Have an independent cold reader execute it, record deviations,
  review changes, and repeat. Pass when the procedure works without
  verbal coaching.
- **Common wrong answers or failure modes:** Blind promotion; deletion
  of the last known-good backup; unbounded replay; trusting CR status;
  skipping evidence preservation or communication.
- **Evidence/verification:** Incident timeline, decision log, target
  identity, recovery-point evidence, application invariants, canary, and
  tracked follow-up.
- **Assumptions and limitations:** Illustrative scenario. Containment
  must stop ongoing harm while preserving necessary forensic evidence.

### Design question with scoring rubric (1 question)

### U07-DES-01

- **Question ID:** `U07-DES-01`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L4
- **Objective tested:** Produce a reviewable architecture/runbook with
  explicit trade-offs, ownership, safety gates, and verifiable
  acceptance criteria.
- **Estimated time:** 20 minutes
- **Question/prompt:** Design a restore-drill scorecard with
  evidence-based pass/fail gates and expiry when assumptions change.
- **Model answer:** Defects: (1) runbook depends on author
  knowledge; (2) hidden fixes make the result non-repeatable; (3)
  undocumented changes bypass review; (4) no deviation log; (5) no
  retest. Have an independent cold reader execute it, record deviations,
  review changes, and repeat. Pass when the procedure works without
  verbal coaching.
- **Reasoning/worked solution:** Defects: (1) runbook depends on author
  knowledge; (2) hidden fixes make the result non-repeatable; (3)
  undocumented changes bypass review; (4) no deviation log; (5) no
  retest. Have an independent cold reader execute it, record deviations,
  review changes, and repeat. Pass when the procedure works without
  verbal coaching.
- **Common wrong answers or failure modes:** A diagram without
  reasoning; targets without evidence; complexity without ownership;
  hidden assumptions; no rollback or acceptance gate.
- **Evidence/verification:** Design record, dependency graph/table,
  named owners, explicit pass/fail checks, and a rehearsal result.
- **Assumptions and limitations:** Rubric totals 16 points. Adapt to
  real workloads only through authorized review.

### Additional questions (2 questions)

### U07-EX-01

- **Question ID:** `U07-EX-01`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L2
- **Objective tested:** Apply evidence reasoning reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** Bundle hash matches but application invariant
  result is missing. What is known?
- **Model answer:** Defects: (1) runbook depends on author
  knowledge; (2) hidden fixes make the result non-repeatable; (3)
  undocumented changes bypass review; (4) no deviation log; (5) no
  retest. Have an independent cold reader execute it, record deviations,
  review changes, and repeat. Pass when the procedure works without
  verbal coaching.
- **Reasoning/worked solution:** Defects: (1) runbook depends on author
  knowledge; (2) hidden fixes make the result non-repeatable; (3)
  undocumented changes bypass review; (4) no deviation log; (5) no
  retest. Have an independent cold reader execute it, record deviations,
  review changes, and repeat. Pass when the procedure works without
  verbal coaching.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

### U07-EX-02

- **Question ID:** `U07-EX-02`
- **Unit(s):** Unit 7 — Restore drills and recovery evidence
- **Level:** L3
- **Objective tested:** Apply cold-read reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** Why should someone other than the author execute
  the runbook?
- **Model answer:** Defects: (1) runbook depends on author
  knowledge; (2) hidden fixes make the result non-repeatable; (3)
  undocumented changes bypass review; (4) no deviation log; (5) no
  retest. Have an independent cold reader execute it, record deviations,
  review changes, and repeat. Pass when the procedure works without
  verbal coaching.
- **Reasoning/worked solution:** Defects: (1) runbook depends on author
  knowledge; (2) hidden fixes make the result non-repeatable; (3)
  undocumented changes bypass review; (4) no deviation log; (5) no
  retest. Have an independent cold reader execute it, record deviations,
  review changes, and repeat. Pass when the procedure works without
  verbal coaching.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

------------------------------------------------------------------------

## Unit 8 — Failure injection and resilience exercises

**Target file:** `08-failure-injection-and-resilience-exercises.md`  
**Learning objectives:** hypothesis and steady state, blast radius,
abort, cleanup, compound failures, scorecards, game days.

### Conceptual short answer (3 questions)

### U08-SA-01

- **Question ID:** `U08-SA-01`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L1
- **Objective tested:** hypothesis and steady state
- **Estimated time:** 5 minutes
- **Question/prompt:** A fault experiment has no baseline or falsifiable
  hypothesis. What is missing?
- **Model answer:** It lacks measurable expected behavior, steady-state
  indicators, target/scope, duration, abort criteria, and independent
  injection evidence. Rewrite before execution.
- **Reasoning/worked solution:** It lacks measurable expected behavior,
  steady-state indicators, target/scope, duration, abort criteria, and
  independent injection evidence. Rewrite before execution.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U08-SA-02

- **Question ID:** `U08-SA-02`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L1
- **Objective tested:** blast radius, abort, cleanup
- **Estimated time:** 5 minutes
- **Question/prompt:** Why is cleanup distinct from abort?
- **Model answer:** Abort decides when to stop for safety; cleanup
  removes experiment and residual effects and verifies recovery.
  Deleting a resource may not remove host-level effects after a daemon
  crash.
- **Reasoning/worked solution:** Abort decides when to stop for safety;
  cleanup removes experiment and residual effects and verifies recovery.
  Deleting a resource may not remove host-level effects after a daemon
  crash.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U08-SA-03

- **Question ID:** `U08-SA-03`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L2
- **Objective tested:** compound failures, scorecards, game days
- **Estimated time:** 5 minutes
- **Question/prompt:** What should happen when a fault breaches an abort
  threshold?
- **Model answer:** Trigger kill switch, preserve timeline, stop new
  experiments, remove only scoped effects, verify recovery, and record
  the outcome. Do not continue for completeness after a safety threshold
  is crossed.
- **Reasoning/worked solution:** Trigger kill switch, preserve timeline,
  stop new experiments, remove only scoped effects, verify recovery, and
  record the outcome. Do not continue for completeness after a safety
  threshold is crossed.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### Multiple-choice (3 questions)

#### U08-MCQ-01 — prompt

Experiment CR says Completed, selector matched zero pods. Conclusion?

- **A.** Resilience proven
- **B.** Inconclusive/failed; fix selector and require independent
  injection proof
- **C.** Broaden to all namespaces
- **D.** Delete all pods

**Correct answer: B.**

- **A — why this distractor is wrong:** No target means the intended
  fault was not shown to occur, so survival is not demonstrated. Option
  text: “Resilience proven”

- **B — why best:** The intended fault was not proven to have occurred.

- **C — why this distractor is wrong:** Broadening to every namespace
  violates blast-radius controls and can affect shared workloads. Option
  text: “Broaden to all namespaces”

- **D — why this distractor is wrong:** Controller status cannot
  substitute for selector and workload evidence. Option text: “Delete
  all pods”

- **Question ID:** `U08-MCQ-01`

- **Unit(s):** Unit 8 — Failure injection and resilience exercises

- **Level:** L1

- **Objective tested:** Choose the safest evidence-based decision about
  hypothesis and steady state.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Experiment CR says Completed, selector matched
  zero pods. Conclusion?

- **Model answer:** B. - **B — why best:** The intended fault was not
  proven to have occurred.

- **Reasoning/worked solution:** - **B — why best:** The intended fault
  was not proven to have occurred.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U08-MCQ-02 — prompt

A fault breaches abort threshold. What happens?

- **A.** Continue for statistical confidence
- **B.** Raise threshold mid-run
- **C.** Invoke kill switch, preserve timeline, remove fault, verify
  recovery
- **D.** Ignore app metrics if controller is healthy

**Correct answer: C.**

- **A — why this distractor is wrong:** Continuing after a safety
  threshold is crossed violates the pre-approved abort condition. Option
  text: “Continue for statistical confidence”

- **B — why this distractor is wrong:** Changing thresholds mid-run
  invalidates the approved experiment and hides the safety breach.
  Option text: “Raise threshold mid-run”

- **C — why best:** Safety thresholds are stop conditions; controller
  status does not override workload impact.

- **D — why this distractor is wrong:** Application metrics are part of
  the safety contract even if the controller is healthy. Option text:
  “Ignore app metrics if controller is healthy”

- **Question ID:** `U08-MCQ-02`

- **Unit(s):** Unit 8 — Failure injection and resilience exercises

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  blast radius, abort, cleanup.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** A fault breaches abort threshold. What happens?

- **Model answer:** C. - **C — why best:** Safety thresholds are stop
  conditions; controller status does not override workload impact.

- **Reasoning/worked solution:** - **C — why best:** Safety thresholds
  are stop conditions; controller status does not override workload
  impact.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U08-MCQ-03 — prompt

When should a scheduled chaos experiment be blocked?

- **A.** When an incident/freeze gate is active or the error budget/SLO
  guardrail blocks it
- **B.** When owner and hypothesis are present
- **C.** When selector matches one lab pod
- **D.** When cleanup was tested

**Correct answer: A.**

- **A — why best:** Governance and safety state take precedence over
  schedule.

- **B — why this distractor is wrong:** A known lab target is a positive
  readiness signal, assuming all other gates pass. Option text: “When
  owner and hypothesis are present”

- **C — why this distractor is wrong:** Tested cleanup and a kill switch
  support safe execution rather than blocking it. Option text: “When
  selector matches one lab pod”

- **D — why this distractor is wrong:** An active incident/freeze or
  exhausted error budget is a reason to block the experiment. Option
  text: “When cleanup was tested”

- **Question ID:** `U08-MCQ-03`

- **Unit(s):** Unit 8 — Failure injection and resilience exercises

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  compound failures, scorecards, game days.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** When should a scheduled chaos experiment be
  blocked?

- **Model answer:** A. - **A — why best:** Governance and safety state
  take precedence over schedule.

- **Reasoning/worked solution:** - **A — why best:** Governance and
  safety state take precedence over schedule.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

### Artifact interpretation (3 questions)

### U08-AI-01

- **Question ID:** `U08-AI-01`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L1
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Selector matches zero pods but CR says Completed.
  What is the conclusion?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
selector_matches=0
experiment_CR=Completed
expected_SLI_change=not_observed
```

- **Model answer:** It lacks measurable expected behavior, steady-state
  indicators, target/scope, duration, abort criteria, and independent
  injection evidence. Rewrite before execution.
- **Reasoning/worked solution:** It lacks measurable expected behavior,
  steady-state indicators, target/scope, duration, abort criteria, and
  independent injection evidence. Rewrite before execution.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U08-AI-02

- **Question ID:** `U08-AI-02`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L2
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Which is stronger evidence: controller event or
  independent workload SLI change plus target proof? Explain.

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
abort_threshold_p95=500ms
p95_at_10:00:15=900ms
CR_deleted_at=10:00:45
p95_at_10:02=700ms
```

- **Model answer:** Abort decides when to stop for safety; cleanup
  removes experiment and residual effects and verifies recovery.
  Deleting a resource may not remove host-level effects after a daemon
  crash.
- **Reasoning/worked solution:** Abort decides when to stop for safety;
  cleanup removes experiment and residual effects and verifies recovery.
  Deleting a resource may not remove host-level effects after a daemon
  crash.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U08-AI-03

- **Question ID:** `U08-AI-03`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L3
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** An incident is open and error budget exhausted.
  Should a scheduled experiment proceed?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
hypothesis=missing
selector=app=*
duration=missing
abort_query=missing
```

- **Model answer:** Trigger kill switch, preserve timeline, stop new
  experiments, remove only scoped effects, verify recovery, and record
  the outcome. Do not continue for completeness after a safety threshold
  is crossed.
- **Reasoning/worked solution:** Trigger kill switch, preserve timeline,
  stop new experiments, remove only scoped effects, verify recovery, and
  record the outcome. Do not continue for completeness after a safety
  threshold is crossed.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### Artifact review (3 questions)

### U08-AR-01

- **Question ID:** `U08-AR-01`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L2
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** mode=all, broad selector, no duration, no safety
  officer. Identify at least three defects and, for each, explain the
  failure mechanism, correction, and test/evidence that would prove the
  correction works.
- **Model answer:** Defects: (1) mode=all/broad selector expands blast
  radius; (2) no allow-list; (3) duration is not an abort control; (4)
  no SLI baseline/abort threshold; (5) no kill switch or cleanup
  verification. Restrict to one disposable target and require preflight,
  watchdog, safety owner, and residual-effect checks. Pass when negative
  scope tests are denied.
- **Reasoning/worked solution:** Defects: (1) mode=all/broad selector
  expands blast radius; (2) no allow-list; (3) duration is not an abort
  control; (4) no SLI baseline/abort threshold; (5) no kill switch or
  cleanup verification. Restrict to one disposable target and require
  preflight, watchdog, safety owner, and residual-effect checks. Pass
  when negative scope tests are denied.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U08-AR-02

- **Question ID:** `U08-AR-02`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Experiment is called successful solely from
  controller completion status. Identify at least three defects and, for
  each, explain the failure mechanism, correction, and test/evidence
  that would prove the correction works.
- **Model answer:** Defects: (1) controller completion is not proof of
  injection; (2) hypothesis/baseline are absent; (3) no application
  SLI; (4) no cleanup check; (5) no expected-versus-observed comparison.
  Add independent target and workload evidence plus residual-fault
  checks. Pass when a zero-match test is marked inconclusive.
- **Reasoning/worked solution:** Defects: (1) controller completion is
  not proof of injection; (2) hypothesis/baseline are absent; (3) no
  application SLI; (4) no cleanup check; (5) no expected-versus-observed
  comparison. Add independent target and workload evidence plus
  residual-fault checks. Pass when a zero-match test is marked
  inconclusive.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U08-AR-03

- **Question ID:** `U08-AR-03`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Game day combines four faults with no hypothesis
  or inter-step gate. Identify at least three defects and, for each,
  explain the failure mechanism, correction, and test/evidence that
  would prove the correction works.
- **Model answer:** Defects: (1) multiple simultaneous faults prevent
  attribution; (2) blast radius is not bounded; (3) no inter-step
  recovery gate; (4) roles/abort authority are unclear; (5) cleanup is
  undefined. Stage one hypothesis at a time with approved combinations,
  stop thresholds, and evidence. Pass with a rehearsed abort and
  verified cleanup.
- **Reasoning/worked solution:** Defects: (1) multiple simultaneous
  faults prevent attribution; (2) blast radius is not bounded; (3) no
  inter-step recovery gate; (4) roles/abort authority are unclear; (5)
  cleanup is undefined. Stage one hypothesis at a time with approved
  combinations, stop thresholds, and evidence. Pass with a rehearsed
  abort and verified cleanup.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### Incident/recovery scenario (1 question)

### U08-IR-01

- **Question ID:** `U08-IR-01`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L3
- **Objective tested:** Respond safely under uncertainty using symptom →
  first action → decide → execute → verify → communicate → prevent.
- **Estimated time:** 12 minutes
- **Question/prompt:** A disposable lab network experiment crosses abort
  thresholds and the controller becomes unhealthy. What should the
  safety officer do? Evidence/timeline `[ILLUSTRATIVE — NOT EXECUTED]`:
  p95/error abort threshold crossed; controller health degrades; fault
  cleanup not yet independently verified.
- **Model answer:** Defects: (1) multiple simultaneous faults prevent
  attribution; (2) blast radius is not bounded; (3) no inter-step
  recovery gate; (4) roles/abort authority are unclear; (5) cleanup is
  undefined. Stage one hypothesis at a time with approved combinations,
  stop thresholds, and evidence. Pass with a rehearsed abort and
  verified cleanup.
- **Reasoning/worked solution:** Defects: (1) multiple simultaneous
  faults prevent attribution; (2) blast radius is not bounded; (3) no
  inter-step recovery gate; (4) roles/abort authority are unclear; (5)
  cleanup is undefined. Stage one hypothesis at a time with approved
  combinations, stop thresholds, and evidence. Pass with a rehearsed
  abort and verified cleanup.
- **Common wrong answers or failure modes:** Blind promotion; deletion
  of the last known-good backup; unbounded replay; trusting CR status;
  skipping evidence preservation or communication.
- **Evidence/verification:** Incident timeline, decision log, target
  identity, recovery-point evidence, application invariants, canary, and
  tracked follow-up.
- **Assumptions and limitations:** Illustrative scenario. Containment
  must stop ongoing harm while preserving necessary forensic evidence.

### Design question with scoring rubric (1 question)

### U08-DES-01

- **Question ID:** `U08-DES-01`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L4
- **Objective tested:** Produce a reviewable architecture/runbook with
  explicit trade-offs, ownership, safety gates, and verifiable
  acceptance criteria.
- **Estimated time:** 20 minutes
- **Question/prompt:** Design an experiment template and governance gate
  for a low-risk single-pod fault and a higher-risk network partition.
- **Model answer:** Defects: (1) multiple simultaneous faults prevent
  attribution; (2) blast radius is not bounded; (3) no inter-step
  recovery gate; (4) roles/abort authority are unclear; (5) cleanup is
  undefined. Stage one hypothesis at a time with approved combinations,
  stop thresholds, and evidence. Pass with a rehearsed abort and
  verified cleanup.
- **Reasoning/worked solution:** Defects: (1) multiple simultaneous
  faults prevent attribution; (2) blast radius is not bounded; (3) no
  inter-step recovery gate; (4) roles/abort authority are unclear; (5)
  cleanup is undefined. Stage one hypothesis at a time with approved
  combinations, stop thresholds, and evidence. Pass with a rehearsed
  abort and verified cleanup.
- **Common wrong answers or failure modes:** A diagram without
  reasoning; targets without evidence; complexity without ownership;
  hidden assumptions; no rollback or acceptance gate.
- **Evidence/verification:** Design record, dependency graph/table,
  named owners, explicit pass/fail checks, and a rehearsal result.
- **Assumptions and limitations:** Rubric totals 16 points. Adapt to
  real workloads only through authorized review.

### Additional questions (2 questions)

### U08-EX-01

- **Question ID:** `U08-EX-01`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L2
- **Objective tested:** Apply diagnosis reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** Why include a negative control/non-injection
  test?
- **Model answer:** Defects: (1) multiple simultaneous faults prevent
  attribution; (2) blast radius is not bounded; (3) no inter-step
  recovery gate; (4) roles/abort authority are unclear; (5) cleanup is
  undefined. Stage one hypothesis at a time with approved combinations,
  stop thresholds, and evidence. Pass with a rehearsed abort and
  verified cleanup.
- **Reasoning/worked solution:** Defects: (1) multiple simultaneous
  faults prevent attribution; (2) blast radius is not bounded; (3) no
  inter-step recovery gate; (4) roles/abort authority are unclear; (5)
  cleanup is undefined. Stage one hypothesis at a time with approved
  combinations, stop thresholds, and evidence. Pass with a rehearsed
  abort and verified cleanup.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

### U08-EX-02

- **Question ID:** `U08-EX-02`
- **Unit(s):** Unit 8 — Failure injection and resilience exercises
- **Level:** L3
- **Objective tested:** Apply evidence reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** What minimum evidence supports an experiment
  conclusion?
- **Model answer:** Defects: (1) multiple simultaneous faults prevent
  attribution; (2) blast radius is not bounded; (3) no inter-step
  recovery gate; (4) roles/abort authority are unclear; (5) cleanup is
  undefined. Stage one hypothesis at a time with approved combinations,
  stop thresholds, and evidence. Pass with a rehearsed abort and
  verified cleanup.
- **Reasoning/worked solution:** Defects: (1) multiple simultaneous
  faults prevent attribution; (2) blast radius is not bounded; (3) no
  inter-step recovery gate; (4) roles/abort authority are unclear; (5)
  cleanup is undefined. Stage one hypothesis at a time with approved
  combinations, stop thresholds, and evidence. Pass with a rehearsed
  abort and verified cleanup.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

------------------------------------------------------------------------

## Unit 9 — Kubernetes backup and restore with Velero

**Target file:** `09-kubernetes-backup-and-restore-with-velero.md`  
**Learning objectives:** Kubernetes objects versus PV data, volume
snapshots versus file-system backup, restore ordering, GitOps, CronJobs,
version compatibility.

### Conceptual short answer (3 questions)

### U09-SA-01

- **Question ID:** `U09-SA-01`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L1
- **Objective tested:** Kubernetes objects versus PV data
- **Estimated time:** 5 minutes
- **Question/prompt:** Backup status is Completed but no PV data
  evidence exists. What is unproven?
- **Model answer:** API-object backup may have succeeded, but persistent
  bytes are unproven. Verify the configured volume data path and perform
  a throwaway restore with checksums and application invariants.
- **Reasoning/worked solution:** API-object backup may have succeeded,
  but persistent bytes are unproven. Verify the configured volume data
  path and perform a throwaway restore with checksums and application
  invariants.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U09-SA-02

- **Question ID:** `U09-SA-02`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L1
- **Objective tested:** volume snapshots versus file-system backup
- **Estimated time:** 5 minutes
- **Question/prompt:** Why must the pinned Velero/plugin/storage version
  combination be verified?
- **Model answer:** Flags, schemas, provider plugins, CRDs, and data
  paths can vary by release. Check official docs and live schema for the
  pinned version, then validate in a disposable cluster before a
  destructive restore.
- **Reasoning/worked solution:** Flags, schemas, provider plugins, CRDs,
  and data paths can vary by release. Check official docs and live
  schema for the pinned version, then validate in a disposable cluster
  before a destructive restore.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U09-SA-03

- **Question ID:** `U09-SA-03`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L2
- **Objective tested:** restore ordering, GitOps, CronJobs, version
  compatibility
- **Estimated time:** 5 minutes
- **Question/prompt:** Why can CronJobs and GitOps complicate restore?
- **Model answer:** GitOps may overwrite/prune restored state, and
  schedules can replay partial side effects or run twice. Coordinate
  ownership, restore dependencies, reconcile side effects, and resume
  workers/schedules deliberately.
- **Reasoning/worked solution:** GitOps may overwrite/prune restored
  state, and schedules can replay partial side effects or run twice.
  Coordinate ownership, restore dependencies, reconcile side effects,
  and resume workers/schedules deliberately.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### Multiple-choice (3 questions)

#### U09-MCQ-01 — prompt

Velero Backup completed but PV data path is unknown. What is proven?

- **A.** Full application recoverability
- **B.** Possibly API-object backup; PV data recovery remains unproven
- **C.** All PVC data is always included
- **D.** A restore is unnecessary

**Correct answer: B.**

- **A — why this distractor is wrong:** Backup completion does not prove
  PV bytes were captured or are restorable. Option text: “Full
  application recoverability”

- **B — why best:** Object status cannot establish persistent-volume
  content coverage.

- **C — why this distractor is wrong:** PV data coverage depends on
  configured data paths and environment/version support. Option text:
  “All PVC data is always included”

- **D — why this distractor is wrong:** A restore test is needed to
  establish recoverability; backup status cannot replace it. Option
  text: “A restore is unnecessary”

- **Question ID:** `U09-MCQ-01`

- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero

- **Level:** L1

- **Objective tested:** Choose the safest evidence-based decision about
  Kubernetes objects versus PV data.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Velero Backup completed but PV data path is
  unknown. What is proven?

- **Model answer:** B. - **B — why best:** Object status cannot
  establish persistent-volume content coverage.

- **Reasoning/worked solution:** - **B — why best:** Object status
  cannot establish persistent-volume content coverage.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U09-MCQ-02 — prompt

How handle version-specific Velero flags/fields?

- **A.** Copy a random blog command
- **B.** Assume provider plugins share schemas
- **C.** Pin version, verify official docs/schema, and test in throwaway
  cluster
- **D.** Run against main cluster to see what happens

**Correct answer: C.**

- **A — why this distractor is wrong:** Disabling all reconciliation
  permanently leaves uncontrolled drift. Option text: “Copy a random
  blog command”

- **B — why this distractor is wrong:** Repeating restore without
  resolving ownership lets reconciliation prune the object again. Option
  text: “Assume provider plugins share schemas”

- **C — why best:** Version pinning and disposable validation reduce
  unsafe assumptions.

- **D — why this distractor is wrong:** Deleting Git removes
  desired-state recovery input and is destructive. Option text: “Run
  against main cluster to see what happens”

- **Question ID:** `U09-MCQ-02`

- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  volume snapshots versus file-system backup.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** How handle version-specific Velero flags/fields?

- **Model answer:** C. - **C — why best:** Version pinning and
  disposable validation reduce unsafe assumptions.

- **Reasoning/worked solution:** - **C — why best:** Version pinning and
  disposable validation reduce unsafe assumptions.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U09-MCQ-03 — prompt

Why coordinate CronJobs and GitOps during restore?

- **A.** They may replay side effects or overwrite/prune restored state
- **B.** They always prevent restore
- **C.** They restore PV bytes automatically
- **D.** They eliminate need for validation

**Correct answer: A.**

- **A — why best:** Scheduling and reconciliation can change restored
  state or repeat work.

- **B — why this distractor is wrong:** Provider plugins and storage
  configurations do not necessarily share schemas or behavior. Option
  text: “They always prevent restore”

- **C — why this distractor is wrong:** This option overlooks a stated
  prerequisite or verification gate; it is not supported by the supplied
  evidence. Option text: “They restore PV bytes automatically”

- **D — why this distractor is wrong:** Testing a destructive restore
  against the main cluster violates the isolated-lab safety contract.
  Option text: “They eliminate need for validation”

- **Question ID:** `U09-MCQ-03`

- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  restore ordering, GitOps, CronJobs, version compatibility.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Why coordinate CronJobs and GitOps during
  restore?

- **Model answer:** A. - **A — why best:** Scheduling and reconciliation
  can change restored state or repeat work.

- **Reasoning/worked solution:** - **A — why best:** Scheduling and
  reconciliation can change restored state or repeat work.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

### Artifact interpretation (3 questions)

### U09-AI-01

- **Question ID:** `U09-AI-01`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L1
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** PVC is Bound but records are missing. What does
  Bound prove?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
backup_status=Completed
PVC_count=3
volume_data_method=unknown
snapshot_records=0
```

- **Model answer:** API-object backup may have succeeded, but persistent
  bytes are unproven. Verify the configured volume data path and perform
  a throwaway restore with checksums and application invariants.
- **Reasoning/worked solution:** API-object backup may have succeeded,
  but persistent bytes are unproven. Verify the configured volume data
  path and perform a throwaway restore with checksums and application
  invariants.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U09-AI-02

- **Question ID:** `U09-AI-02`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L2
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** What is the safe response when an installed CRD
  schema disagrees with a blog's manifest?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
restore_order=Deployments,PVCs,operator_CRs,CRDs
GitOps=resume_immediate
```

- **Model answer:** Flags, schemas, provider plugins, CRDs, and data
  paths can vary by release. Check official docs and live schema for the
  pinned version, then validate in a disposable cluster before a
  destructive restore.
- **Reasoning/worked solution:** Flags, schemas, provider plugins, CRDs,
  and data paths can vary by release. Check official docs and live
  schema for the pinned version, then validate in a disposable cluster
  before a destructive restore.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U09-AI-03

- **Question ID:** `U09-AI-03`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L3
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** After restore, a CronJob is due in two minutes
  and prior run may have partially committed. What next?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
CronJob=active
prior_partial_side_effects=possible
idempotency_key=none
next_run=2m
```

- **Model answer:** GitOps may overwrite/prune restored state, and
  schedules can replay partial side effects or run twice. Coordinate
  ownership, restore dependencies, reconcile side effects, and resume
  workers/schedules deliberately.
- **Reasoning/worked solution:** GitOps may overwrite/prune restored
  state, and schedules can replay partial side effects or run twice.
  Coordinate ownership, restore dependencies, reconcile side effects,
  and resume workers/schedules deliberately.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### Artifact review (3 questions)

### U09-AR-01

- **Question ID:** `U09-AR-01`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L2
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Backup report says Completed; volume method
  unknown; snapshot count zero. Identify at least three defects and, for
  each, explain the failure mechanism, correction, and test/evidence
  that would prove the correction works.
- **Model answer:** Defects: (1) no restore drill; (2) PV data path
  unknown; (3) application invariants missing; (4) restore order and
  GitOps ownership absent; (5) no versions/evidence. Verify the pinned
  configuration and volume mechanism, restore to a throwaway target, and
  validate data and app behavior.
- **Reasoning/worked solution:** Defects: (1) no restore drill; (2) PV
  data path unknown; (3) application invariants missing; (4) restore
  order and GitOps ownership absent; (5) no versions/evidence. Verify
  the pinned configuration and volume mechanism, restore to a throwaway
  target, and validate data and app behavior.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U09-AR-02

- **Question ID:** `U09-AR-02`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Restore applies custom resources before CRDs and
  immediately resumes GitOps. Identify at least three defects and, for
  each, explain the failure mechanism, correction, and test/evidence
  that would prove the correction works.
- **Model answer:** Defects: (1) CRs precede CRDs/operators; (2)
  scheduled work can duplicate partial effects; (3) GitOps may prune
  restored objects; (4) credentials and data readiness are not
  gates; (5) no application verification. Restore prerequisites/data
  first, reconcile ownership and side effects, then resume schedules
  deliberately. Pass with an idempotency test.
- **Reasoning/worked solution:** Defects: (1) CRs precede
  CRDs/operators; (2) scheduled work can duplicate partial effects; (3)
  GitOps may prune restored objects; (4) credentials and data readiness
  are not gates; (5) no application verification. Restore
  prerequisites/data first, reconcile ownership and side effects, then
  resume schedules deliberately. Pass with an idempotency test.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U09-AR-03

- **Question ID:** `U09-AR-03`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Backup credentials are shared with application
  workload identity. Identify at least three defects and, for each,
  explain the failure mechanism, correction, and test/evidence that
  would prove the correction works.
- **Model answer:** Defects: (1) compromised workload identity can
  delete backups; (2) version/plugin compatibility is undocumented; (3)
  keys/BSL access may share the failure domain; (4) least privilege is
  unaudited; (5) no restore proof. Separate credentials, pin versions,
  verify official docs/schema, and test a full isolated restore.
- **Reasoning/worked solution:** Defects: (1) compromised workload
  identity can delete backups; (2) version/plugin compatibility is
  undocumented; (3) keys/BSL access may share the failure domain; (4)
  least privilege is unaudited; (5) no restore proof. Separate
  credentials, pin versions, verify official docs/schema, and test a
  full isolated restore.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### Incident/recovery scenario (1 question)

### U09-IR-01

- **Question ID:** `U09-IR-01`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L3
- **Objective tested:** Respond safely under uncertainty using symptom →
  first action → decide → execute → verify → communicate → prevent.
- **Estimated time:** 12 minutes
- **Question/prompt:** Restore recreated Deployments but the application
  reports missing historical records; a CronJob is due soon. What is the
  recovery sequence? Evidence/timeline `[ILLUSTRATIVE — NOT EXECUTED]`:
  restored Deployment ready; application reports missing records;
  CronJob due soon; partial prior side effects possible.
- **Model answer:** Defects: (1) compromised workload identity can
  delete backups; (2) version/plugin compatibility is undocumented; (3)
  keys/BSL access may share the failure domain; (4) least privilege is
  unaudited; (5) no restore proof. Separate credentials, pin versions,
  verify official docs/schema, and test a full isolated restore.
- **Reasoning/worked solution:** Defects: (1) compromised workload
  identity can delete backups; (2) version/plugin compatibility is
  undocumented; (3) keys/BSL access may share the failure domain; (4)
  least privilege is unaudited; (5) no restore proof. Separate
  credentials, pin versions, verify official docs/schema, and test a
  full isolated restore.
- **Common wrong answers or failure modes:** Blind promotion; deletion
  of the last known-good backup; unbounded replay; trusting CR status;
  skipping evidence preservation or communication.
- **Evidence/verification:** Incident timeline, decision log, target
  identity, recovery-point evidence, application invariants, canary, and
  tracked follow-up.
- **Assumptions and limitations:** Illustrative scenario. Containment
  must stop ongoing harm while preserving necessary forensic evidence.

### Design question with scoring rubric (1 question)

### U09-DES-01

- **Question ID:** `U09-DES-01`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L4
- **Objective tested:** Produce a reviewable architecture/runbook with
  explicit trade-offs, ownership, safety gates, and verifiable
  acceptance criteria.
- **Estimated time:** 20 minutes
- **Question/prompt:** Design a Velero restore decision record covering
  cluster objects, PV data path, CRDs/operators, GitOps ownership,
  CronJobs, credentials, and verification.
- **Model answer:** Defects: (1) compromised workload identity can
  delete backups; (2) version/plugin compatibility is undocumented; (3)
  keys/BSL access may share the failure domain; (4) least privilege is
  unaudited; (5) no restore proof. Separate credentials, pin versions,
  verify official docs/schema, and test a full isolated restore.
- **Reasoning/worked solution:** Defects: (1) compromised workload
  identity can delete backups; (2) version/plugin compatibility is
  undocumented; (3) keys/BSL access may share the failure domain; (4)
  least privilege is unaudited; (5) no restore proof. Separate
  credentials, pin versions, verify official docs/schema, and test a
  full isolated restore.
- **Common wrong answers or failure modes:** A diagram without
  reasoning; targets without evidence; complexity without ownership;
  hidden assumptions; no rollback or acceptance gate.
- **Evidence/verification:** Design record, dependency graph/table,
  named owners, explicit pass/fail checks, and a rehearsal result.
- **Assumptions and limitations:** Rubric totals 16 points. Adapt to
  real workloads only through authorized review.

### Additional questions (2 questions)

### U09-EX-01

- **Question ID:** `U09-EX-01`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L2
- **Objective tested:** Apply diagnosis reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** A PVC is Bound but records are missing. What does
  Bound prove?
- **Model answer:** Defects: (1) compromised workload identity can
  delete backups; (2) version/plugin compatibility is undocumented; (3)
  keys/BSL access may share the failure domain; (4) least privilege is
  unaudited; (5) no restore proof. Separate credentials, pin versions,
  verify official docs/schema, and test a full isolated restore.
- **Reasoning/worked solution:** Defects: (1) compromised workload
  identity can delete backups; (2) version/plugin compatibility is
  undocumented; (3) keys/BSL access may share the failure domain; (4)
  least privilege is unaudited; (5) no restore proof. Separate
  credentials, pin versions, verify official docs/schema, and test a
  full isolated restore.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

### U09-EX-02

- **Question ID:** `U09-EX-02`
- **Unit(s):** Unit 9 — Kubernetes backup and restore with Velero
- **Level:** L3
- **Objective tested:** Apply safe command review reasoning to a
  concrete operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** Why use an explicit lab context and preflight
  before restore?
- **Model answer:** Defects: (1) compromised workload identity can
  delete backups; (2) version/plugin compatibility is undocumented; (3)
  keys/BSL access may share the failure domain; (4) least privilege is
  unaudited; (5) no restore proof. Separate credentials, pin versions,
  verify official docs/schema, and test a full isolated restore.
- **Reasoning/worked solution:** Defects: (1) compromised workload
  identity can delete backups; (2) version/plugin compatibility is
  undocumented; (3) keys/BSL access may share the failure domain; (4)
  least privilege is unaudited; (5) no restore proof. Separate
  credentials, pin versions, verify official docs/schema, and test a
  full isolated restore.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

------------------------------------------------------------------------

## Unit 10 — Chaos engineering with Litmus and Chaos Mesh

**Target file:** `10-chaos-engineering-with-litmus-and-chaos-mesh.md`  
**Learning objectives:** hypothesis, selectors, injection evidence,
RBAC/admission/watchdog and cleanup, platform comparison, probes, CI,
threat model.

### Conceptual short answer (3 questions)

### U10-SA-01

- **Question ID:** `U10-SA-01`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L1
- **Objective tested:** hypothesis, selectors, injection evidence
- **Estimated time:** 5 minutes
- **Question/prompt:** Chaos resource reports Completed but selector
  matched zero pods. Is the experiment a pass?
- **Model answer:** No. It is inconclusive or failed because intended
  fault application was not proven. Fix selector preflight, target only
  opted-in lab resources, and independently verify workload effect.
- **Reasoning/worked solution:** No. It is inconclusive or failed
  because intended fault application was not proven. Fix selector
  preflight, target only opted-in lab resources, and independently
  verify workload effect.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U10-SA-02

- **Question ID:** `U10-SA-02`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L1
- **Objective tested:** RBAC/admission/watchdog and cleanup
- **Estimated time:** 5 minutes
- **Question/prompt:** Why are chaos controller/daemon privileges a
  security concern?
- **Model answer:** Controller/daemon capabilities may disrupt workloads
  or node networking; compromise can become a denial-of-service or
  node-level incident. Use least privilege, isolated lab, pinned images,
  audit, admission controls, and a tested kill switch.
- **Reasoning/worked solution:** Controller/daemon capabilities may
  disrupt workloads or node networking; compromise can become a
  denial-of-service or node-level incident. Use least privilege,
  isolated lab, pinned images, audit, admission controls, and a tested
  kill switch.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### U10-SA-03

- **Question ID:** `U10-SA-03`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L2
- **Objective tested:** platform comparison, probes, CI, threat model
- **Estimated time:** 5 minutes
- **Question/prompt:** How should Chaos Mesh and LitmusChaos be
  compared?
- **Model answer:** Compare catalog fit, probes, workflow/scheduling,
  footprint, RBAC/security, CI, extensibility, version burden, and
  ownership. No universal winner; Litmus hands-on remains optional and
  can be a read-only comparison.
- **Reasoning/worked solution:** Compare catalog fit, probes,
  workflow/scheduling, footprint, RBAC/security, CI, extensibility,
  version burden, and ownership. No universal winner; Litmus hands-on
  remains optional and can be a read-only comparison.
- **Common wrong answers or failure modes:** Definition-only answers
  miss operational consequences; do not confuse target with measurement,
  metadata with payload, or a status with correctness.
- **Evidence/verification:** Objective register, dependency graph,
  relevant runbook, or a controlled recovery test; cite the exact
  evidence.
- **Assumptions and limitations:** Use only supplied facts; if
  consistency, key availability, or version support is unknown, state
  it.

### Multiple-choice (3 questions)

#### U10-MCQ-01 — prompt

Chaos CR reports Completed but selector matched zero pods. What is
status?

- **A.** Pass
- **B.** Inconclusive/failed; correct selector and rerun only after
  preflight
- **C.** Broaden selector to every namespace
- **D.** Assume controller status proves fault

**Correct answer: B.**

- **A — why this distractor is wrong:** A terminal CR status does not
  prove that the intended target was selected or affected. Option text:
  “Pass”

- **B — why best:** No target means no proof of the intended fault.

- **C — why this distractor is wrong:** A broad selector expands blast
  radius instead of correcting the zero-match issue safely. Option text:
  “Broaden selector to every namespace”

- **D — why this distractor is wrong:** Controller status alone is not
  independent proof of injection. Option text: “Assume controller status
  proves fault”

- **Question ID:** `U10-MCQ-01`

- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh

- **Level:** L1

- **Objective tested:** Choose the safest evidence-based decision about
  hypothesis, selectors, injection evidence.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Chaos CR reports Completed but selector matched
  zero pods. What is status?

- **Model answer:** B. - **B — why best:** No target means no proof of
  the intended fault.

- **Reasoning/worked solution:** - **B — why best:** No target means no
  proof of the intended fault.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U10-MCQ-02 — prompt

What is the correction for cluster-wide chaos permissions?

- **A.** Expose dashboard publicly
- **B.** Disable alerts
- **C.** Least-privilege RBAC plus namespace/selector admission
  guardrails
- **D.** Use mode=all

**Correct answer: C.**

- **A — why this distractor is wrong:** Public dashboard exposure
  increases attack surface rather than narrowing authority. Option text:
  “Expose dashboard publicly”

- **B — why this distractor is wrong:** Disabling alerts removes an
  essential safety control. Option text: “Disable alerts”

- **C — why best:** Scoped permissions and admission controls reduce
  blast radius.

- **D — why this distractor is wrong:** `mode: all` broadens the target
  set and is prohibited in the required lab path. Option text: “Use
  mode=all”

- **Question ID:** `U10-MCQ-02`

- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  RBAC/admission/watchdog and cleanup.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** What is the correction for cluster-wide chaos
  permissions?

- **Model answer:** C. - **C — why best:** Scoped permissions and
  admission controls reduce blast radius.

- **Reasoning/worked solution:** - **C — why best:** Scoped permissions
  and admission controls reduce blast radius.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

#### U10-MCQ-03 — prompt

Watchdog cannot query Prometheus or Kubernetes API. What should it do?

- **A.** Fail safe within bounded lab scope and verify cleanup; treat
  unknown as unsafe
- **B.** Continue until duration ends without alert
- **C.** Treat missing metric as healthy
- **D.** Delete every chaos resource cluster-wide

**Correct answer: A.**

- **A — why best:** Missing telemetry is unknown, not evidence of
  safety; abort actions must remain narrowly scoped.

- **B — why this distractor is wrong:** Continuing when the metric
  source is unavailable treats unknown as healthy. Option text:
  “Continue until duration ends without alert”

- **C — why this distractor is wrong:** Cluster-wide deletion exceeds
  the watchdog's allowed scope and can affect unrelated experiments.
  Option text: “Treat missing metric as healthy”

- **D — why this distractor is wrong:** Waiting without a bounded safe
  action leaves a harmful experiment running with no telemetry. Option
  text: “Delete every chaos resource cluster-wide”

- **Question ID:** `U10-MCQ-03`

- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh

- **Level:** L2

- **Objective tested:** Choose the safest evidence-based decision about
  platform comparison, probes, CI, threat model.

- **Estimated time:** 4 minutes

- **Evidence/verification:** Use the register, log, independent metric,
  schema, or controlled drill specified by the prompt.

- **Assumptions and limitations:** One best answer under the supplied
  facts; new evidence can change a real incident decision.

- **Question/prompt:** Watchdog cannot query Prometheus or Kubernetes
  API. What should it do?

- **Model answer:** A. - **A — why best:** Missing telemetry is unknown,
  not evidence of safety; abort actions must remain narrowly scoped.

- **Reasoning/worked solution:** - **A — why best:** Missing telemetry
  is unknown, not evidence of safety; abort actions must remain narrowly
  scoped.

- **Common wrong answers or failure modes:** See the three
  distractor-specific explanations above; each identifies the unsafe
  shortcut or misconception.

### Artifact interpretation (3 questions)

### U10-AI-01

- **Question ID:** `U10-AI-01`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L1
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** Watchdog metric query is unavailable but it
  continues the experiment. What is wrong?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
namespace=chaos-lab
selector=app=api
matched_pods=0
CR_status=Completed
p95_change=none
```

- **Model answer:** No. It is inconclusive or failed because intended
  fault application was not proven. Fix selector preflight, target only
  opted-in lab resources, and independently verify workload effect.
- **Reasoning/worked solution:** No. It is inconclusive or failed
  because intended fault application was not proven. Fix selector
  preflight, target only opted-in lab resources, and independently
  verify workload effect.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U10-AI-02

- **Question ID:** `U10-AI-02`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L2
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** CR deleted, daemon restarted, residual network
  state not checked, latency still elevated. What next?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
watchdog_query=unavailable
watchdog_action=continue
reason=no_breach_detected
```

- **Model answer:** Controller/daemon capabilities may disrupt workloads
  or node networking; compromise can become a denial-of-service or
  node-level incident. Use least privilege, isolated lab, pinned images,
  audit, admission controls, and a tested kill switch.
- **Reasoning/worked solution:** Controller/daemon capabilities may
  disrupt workloads or node networking; compromise can become a
  denial-of-service or node-level incident. Use least privilege,
  isolated lab, pinned images, audit, admission controls, and a tested
  kill switch.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### U10-AI-03

- **Question ID:** `U10-AI-03`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L3
- **Objective tested:** Interpret a recovery artifact and distinguish
  operation status from end-to-end correctness.
- **Estimated time:** 7 minutes
- **Question/prompt:** A version-sensitive experiment field is found
  only in an old blog. What is the safe verification path?

The artifact is `[ILLUSTRATIVE — NOT EXECUTED]`. State what it proves,
what it does not prove, the next safe action, and the evidence needed to
close the gap. **Self-contained artifact
`[ILLUSTRATIVE — NOT EXECUTED]`:**

``` text
CR=deleted
daemon=restarted
node_network_rule_check=not_run
application_latency=elevated
```

- **Model answer:** Compare catalog fit, probes, workflow/scheduling,
  footprint, RBAC/security, CI, extensibility, version burden, and
  ownership. No universal winner; Litmus hands-on remains optional and
  can be a read-only comparison.
- **Reasoning/worked solution:** Compare catalog fit, probes,
  workflow/scheduling, footprint, RBAC/security, CI, extensibility,
  version burden, and ownership. No universal winner; Litmus hands-on
  remains optional and can be a read-only comparison.
- **Common wrong answers or failure modes:** Treating timestamps or a
  terminal status as proof; skipping integrity, consistency, or
  application-level checks; promoting before gaps are resolved.
- **Evidence/verification:** Relevant status/events plus independent
  checks such as checksums, invariants, canary, reconciliation, or
  scoped target evidence.
- **Assumptions and limitations:** Artifact is hypothetical and not a
  measured result.

### Artifact review (3 questions)

### U10-AR-01

- **Question ID:** `U10-AR-01`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L2
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Experiment has mode=all, no duration, no
  owner/hypothesis metadata. Identify at least three defects and, for
  each, explain the failure mechanism, correction, and test/evidence
  that would prove the correction works.
- **Model answer:** Defects: (1) broad mode/selector; (2) no bounded
  duration; (3) no owner/hypothesis; (4) no abort query or kill
  switch; (5) no cleanup/injection evidence. Reject through policy and
  rewrite for one opted-in lab target with verified schema and
  independent proof.
- **Reasoning/worked solution:** Defects: (1) broad mode/selector; (2)
  no bounded duration; (3) no owner/hypothesis; (4) no abort query or
  kill switch; (5) no cleanup/injection evidence. Reject through policy
  and rewrite for one opted-in lab target with verified schema and
  independent proof.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U10-AR-02

- **Question ID:** `U10-AR-02`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** CI passes when CR status is terminal without SLO
  or cleanup evidence. Identify at least three defects and, for each,
  explain the failure mechanism, correction, and test/evidence that
  would prove the correction works.
- **Model answer:** Defects: (1) CR terminal status can occur without
  intended fault; (2) no SLO assertion; (3) no abort path; (4) cleanup
  is unverified; (5) evidence bundle is missing. Add selector preflight,
  independent health/metric assertions, watchdog, and residual-effect
  verification. Pass when planted non-injection causes CI
  failure/inconclusive verdict.
- **Reasoning/worked solution:** Defects: (1) CR terminal status can
  occur without intended fault; (2) no SLO assertion; (3) no abort
  path; (4) cleanup is unverified; (5) evidence bundle is missing. Add
  selector preflight, independent health/metric assertions, watchdog,
  and residual-effect verification. Pass when planted non-injection
  causes CI failure/inconclusive verdict.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### U10-AR-03

- **Question ID:** `U10-AR-03`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L3
- **Objective tested:** Identify at least three distinct design defects
  and repair/test each one.
- **Estimated time:** 8 minutes
- **Question/prompt:** Both chaos platforms installed simultaneously on
  a resource-constrained laptop. Identify at least three defects and,
  for each, explain the failure mechanism, correction, and test/evidence
  that would prove the correction works.
- **Model answer:** Defects: (1) simultaneous installations exceed
  footprint and complicate diagnosis; (2) version/catalog availability
  is assumed; (3) schemas are not pinned; (4) two controllers can
  conflict; (5) no fallback plan. Run one platform at a time, verify
  chosen release and catalog, measure footprint, and use guided
  read-only comparison when resources are insufficient.
- **Reasoning/worked solution:** Defects: (1) simultaneous installations
  exceed footprint and complicate diagnosis; (2) version/catalog
  availability is assumed; (3) schemas are not pinned; (4) two
  controllers can conflict; (5) no fallback plan. Run one platform at a
  time, verify chosen release and catalog, measure footprint, and use
  guided read-only comparison when resources are insufficient.
- **Common wrong answers or failure modes:** Listing vague concerns
  without linking each to a concrete failure; fixing configuration
  without a negative test; trusting a green status alone.
- **Evidence/verification:** Reviewed artifact, negative tests,
  controlled restore/drill, and recorded pass/fail gates.
- **Assumptions and limitations:** Scenario is hypothetical;
  product-specific syntax must be verified against the pinned release.

### Incident/recovery scenario (1 question)

### U10-IR-01

- **Question ID:** `U10-IR-01`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L3
- **Objective tested:** Respond safely under uncertainty using symptom →
  first action → decide → execute → verify → communicate → prevent.
- **Estimated time:** 12 minutes
- **Question/prompt:** A lab NetworkChaos experiment breaches its abort
  threshold and the daemon crashes before cleanup. What is the response?
  Evidence/timeline `[ILLUSTRATIVE — NOT EXECUTED]`: NetworkChaos
  crosses abort threshold; daemon crashes before cleanup; node-level
  residual state unknown.
- **Model answer:** Defects: (1) simultaneous installations exceed
  footprint and complicate diagnosis; (2) version/catalog availability
  is assumed; (3) schemas are not pinned; (4) two controllers can
  conflict; (5) no fallback plan. Run one platform at a time, verify
  chosen release and catalog, measure footprint, and use guided
  read-only comparison when resources are insufficient.
- **Reasoning/worked solution:** Defects: (1) simultaneous installations
  exceed footprint and complicate diagnosis; (2) version/catalog
  availability is assumed; (3) schemas are not pinned; (4) two
  controllers can conflict; (5) no fallback plan. Run one platform at a
  time, verify chosen release and catalog, measure footprint, and use
  guided read-only comparison when resources are insufficient.
- **Common wrong answers or failure modes:** Blind promotion; deletion
  of the last known-good backup; unbounded replay; trusting CR status;
  skipping evidence preservation or communication.
- **Evidence/verification:** Incident timeline, decision log, target
  identity, recovery-point evidence, application invariants, canary, and
  tracked follow-up.
- **Assumptions and limitations:** Illustrative scenario. Containment
  must stop ongoing harm while preserving necessary forensic evidence.

### Design question with scoring rubric (1 question)

### U10-DES-01

- **Question ID:** `U10-DES-01`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L4
- **Objective tested:** Produce a reviewable architecture/runbook with
  explicit trade-offs, ownership, safety gates, and verifiable
  acceptance criteria.
- **Estimated time:** 20 minutes
- **Question/prompt:** Design guardrails for a Chaos Mesh lab and an
  evidence-based comparison with LitmusChaos.
- **Model answer:** Defects: (1) simultaneous installations exceed
  footprint and complicate diagnosis; (2) version/catalog availability
  is assumed; (3) schemas are not pinned; (4) two controllers can
  conflict; (5) no fallback plan. Run one platform at a time, verify
  chosen release and catalog, measure footprint, and use guided
  read-only comparison when resources are insufficient.
- **Reasoning/worked solution:** Defects: (1) simultaneous installations
  exceed footprint and complicate diagnosis; (2) version/catalog
  availability is assumed; (3) schemas are not pinned; (4) two
  controllers can conflict; (5) no fallback plan. Run one platform at a
  time, verify chosen release and catalog, measure footprint, and use
  guided read-only comparison when resources are insufficient.
- **Common wrong answers or failure modes:** A diagram without
  reasoning; targets without evidence; complexity without ownership;
  hidden assumptions; no rollback or acceptance gate.
- **Evidence/verification:** Design record, dependency graph/table,
  named owners, explicit pass/fail checks, and a rehearsal result.
- **Assumptions and limitations:** Rubric totals 16 points. Adapt to
  real workloads only through authorized review.

### Additional questions (2 questions)

### U10-EX-01

- **Question ID:** `U10-EX-01`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L2
- **Objective tested:** Apply version verification reasoning to a
  concrete operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** A blog lists a chaos CR field but the installed
  CRD schema differs. What next?
- **Model answer:** Defects: (1) simultaneous installations exceed
  footprint and complicate diagnosis; (2) version/catalog availability
  is assumed; (3) schemas are not pinned; (4) two controllers can
  conflict; (5) no fallback plan. Run one platform at a time, verify
  chosen release and catalog, measure footprint, and use guided
  read-only comparison when resources are insufficient.
- **Reasoning/worked solution:** Defects: (1) simultaneous installations
  exceed footprint and complicate diagnosis; (2) version/catalog
  availability is assumed; (3) schemas are not pinned; (4) two
  controllers can conflict; (5) no fallback plan. Run one platform at a
  time, verify chosen release and catalog, measure footprint, and use
  guided read-only comparison when resources are insufficient.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

### U10-EX-02

- **Question ID:** `U10-EX-02`
- **Unit(s):** Unit 10 — Chaos engineering with Litmus and Chaos Mesh
- **Level:** L3
- **Objective tested:** Apply fidelity reasoning to a concrete
  operational decision.
- **Estimated time:** 6 minutes
- **Question/prompt:** A network partition passes between two kind
  clusters on one laptop. What claim is justified?
- **Model answer:** Defects: (1) simultaneous installations exceed
  footprint and complicate diagnosis; (2) version/catalog availability
  is assumed; (3) schemas are not pinned; (4) two controllers can
  conflict; (5) no fallback plan. Run one platform at a time, verify
  chosen release and catalog, measure footprint, and use guided
  read-only comparison when resources are insufficient.
- **Reasoning/worked solution:** Defects: (1) simultaneous installations
  exceed footprint and complicate diagnosis; (2) version/catalog
  availability is assumed; (3) schemas are not pinned; (4) two
  controllers can conflict; (5) no fallback plan. Run one platform at a
  time, verify chosen release and catalog, measure footprint, and use
  guided read-only comparison when resources are insufficient.
- **Common wrong answers or failure modes:** Confusing calculated values
  with measured results; relying on one status signal; omitting
  assumptions or next verification.
- **Evidence/verification:** Show calculations and units where relevant;
  identify the register, log, invariant, or test needed.
- **Assumptions and limitations:** Use supplied values only; unprovided
  environment behavior is unknown until tested.

------------------------------------------------------------------------

## Cross-unit integration scenarios XU-01–XU-40

Each scenario integrates at least two units. Numeric inputs are scenario
facts; results are calculated, not measured production results. Sample
artifacts and scenarios are illustrative. Every destructive action is
restricted to a hypothetical incident or throwaway lab.

### XU-01

- **Question ID:** `XU-01`
- **Unit(s):** U01,U02,U06
- **Level:** L3
- **Objective tested:** RTO/RPO from cadence and lag
- **Estimated time:** 8 minutes
- **Question/prompt:** Backup cadence is 15 min; two jobs failed;
  replica lag is 7 min at failure; latest verified recovery point is 28
  min old. RPO target is 10 min. Is it met?
- **Model answer:** No. Use the latest verified consistent point: RPA =
  28 min, exceeding the 10-minute target by 18 min. The 15-minute
  schedule is only nominal and failed jobs plus lag matter. Preserve
  job/lag evidence, find another valid point, and remediate
  schedule/alerting. Verify with a restore and transaction continuity.
- **Reasoning/worked solution:** No. Use the latest verified consistent
  point: RPA = 28 min, exceeding the 10-minute target by 18 min. The
  15-minute schedule is only nominal and failed jobs plus lag matter.
  Preserve job/lag evidence, find another valid point, and remediate
  schedule/alerting. Verify with a restore and transaction continuity.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-02

- **Question ID:** `XU-02`
- **Unit(s):** U01,U07,U09
- **Level:** L4
- **Objective tested:** RTO lower bound from size and throughput
- **Estimated time:** 8 minutes
- **Question/prompt:** A 240 GiB dataset restores at 40 GiB/hour. Add 20
  min detection, 10 decision, 30 provisioning, 25 verification, 15
  cutover. Calculate the lower bound.
- **Model answer:** Transfer time = 240/40 = 6 hours. Other phases total
  100 minutes = 1 h 40 min, so lower bound is 7 h 40 min, excluding
  retries/contention. This is a calculation, not measured RTA. A 2-hour
  target is infeasible on these assumptions.
- **Reasoning/worked solution:** Transfer time = 240/40 = 6 hours. Other
  phases total 100 minutes = 1 h 40 min, so lower bound is 7 h 40 min,
  excluding retries/contention. This is a calculation, not measured RTA.
  A 2-hour target is infeasible on these assumptions.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-03

- **Question ID:** `XU-03`
- **Unit(s):** U02,U03,U07
- **Level:** L2
- **Objective tested:** Immutable backup but key unavailable
- **Estimated time:** 8 minutes
- **Question/prompt:** Backup objects are immutable for 30 days, but the
  only decryption key was stored in the failed cluster. What is the
  recovery decision?
- **Model answer:** Treat data as not currently recoverable;
  immutability does not supply keys. Preserve objects, recover key
  custody through an independent approved escrow/bootstrap path, and
  restore into isolation. Verify decryptability, data invariants, and
  key audit. Prevent with independently protected key recovery.
- **Reasoning/worked solution:** Treat data as not currently
  recoverable; immutability does not supply keys. Preserve objects,
  recover key custody through an independent approved escrow/bootstrap
  path, and restore into isolation. Verify decryptability, data
  invariants, and key audit. Prevent with independently protected key
  recovery.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-04

- **Question ID:** `XU-04`
- **Unit(s):** U02,U06
- **Level:** L3
- **Objective tested:** Snapshot vs replica vs immutable copy
- **Estimated time:** 8 minutes
- **Question/prompt:** A bad migration corrupts rows, replica has
  already copied it, and a same-volume snapshot was taken after the
  migration. Which recovery source is preferred?
- **Model answer:** None is automatically good: replica and
  post-corruption snapshot may both contain corruption. Find a verified
  pre-corruption immutable/historical point, confirm key availability
  and retention, restore isolated, and reconcile. Compare timestamps
  with corruption onset, not just recency.
- **Reasoning/worked solution:** None is automatically good: replica and
  post-corruption snapshot may both contain corruption. Find a verified
  pre-corruption immutable/historical point, confirm key availability
  and retention, restore isolated, and reconcile. Compare timestamps
  with corruption onset, not just recency.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-05

- **Question ID:** `XU-05`
- **Unit(s):** U03,U09
- **Level:** L4
- **Objective tested:** Kubernetes platform missing CRDs/operators
- **Estimated time:** 8 minutes
- **Question/prompt:** A restored app custom resource is rejected
  because its CRD/operator is absent. Database data is separately
  protected. Order recovery.
- **Model answer:** Establish trusted cluster/bootstrap and
  secrets/registry access; install compatible CRDs/operators; restore
  database/PV data and verify; apply custom resources; deploy
  applications; coordinate GitOps and start workers only after gates.
  Validate API acceptance, controller reconciliation, and app
  invariants.
- **Reasoning/worked solution:** Establish trusted cluster/bootstrap and
  secrets/registry access; install compatible CRDs/operators; restore
  database/PV data and verify; apply custom resources; deploy
  applications; coordinate GitOps and start workers only after gates.
  Validate API acceptance, controller reconciliation, and app
  invariants.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-06

- **Question ID:** `XU-06`
- **Unit(s):** U03,U06
- **Level:** L2
- **Objective tested:** Circular identity/secrets/registry dependencies
- **Estimated time:** 8 minutes
- **Question/prompt:** Cluster bootstrap needs registry credentials from
  Vault; Vault needs cluster identity; identity configuration is in the
  registry. Break the cycle.
- **Model answer:** Create a separately governed bootstrap path with
  independent identity/key custody and offline documentation. Use it to
  restore foundational identity/networking and secrets access, then
  registry, compatible platform components, and workloads. Test from a
  clean environment; do not assume the failed cluster can unlock itself.
- **Reasoning/worked solution:** Create a separately governed bootstrap
  path with independent identity/key custody and offline documentation.
  Use it to restore foundational identity/networking and secrets access,
  then registry, compatible platform components, and workloads. Test
  from a clean environment; do not assume the failed cluster can unlock
  itself.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-07

- **Question ID:** `XU-07`
- **Unit(s):** U04,U05,U07
- **Level:** L3
- **Objective tested:** Database/object-store/stream consistent point
- **Estimated time:** 8 minutes
- **Question/prompt:** DB transaction boundary is 10:05; object manifest
  is 10:07; stream checkpoint is 10:02; model registry points to a model
  trained on data through 10:06. What is wrong?
- **Model answer:** Timestamps show potentially inconsistent states:
  object side effects may postdate DB, stream checkpoint predates data,
  and model lineage exceeds the stream point. Choose a common business
  boundary, align transaction IDs/watermarks/offsets, replay/reconcile,
  and validate model/data triple. Timestamps alone do not prove causal
  consistency.
- **Reasoning/worked solution:** Timestamps show potentially
  inconsistent states: object side effects may postdate DB, stream
  checkpoint predates data, and model lineage exceeds the stream point.
  Choose a common business boundary, align transaction
  IDs/watermarks/offsets, replay/reconcile, and validate model/data
  triple. Timestamps alone do not prove causal consistency.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-08

- **Question ID:** `XU-08`
- **Unit(s):** U04,U07
- **Level:** L4
- **Objective tested:** Replay after partial commit
- **Estimated time:** 8 minutes
- **Question/prompt:** A batch wrote 70% of rows, then crashed before
  checkpoint. Sink has no idempotency key. Should the whole batch be
  replayed?
- **Model answer:** Not blindly. Inspect transaction/commit evidence and
  side effects, isolate the replay target, create a
  deduplication/reconciliation plan or compensate effects, then replay a
  bounded range. Verify keys, counts, and downstream effects. If effects
  cannot be distinguished, disclose uncertainty and avoid duplicate
  external actions.
- **Reasoning/worked solution:** Not blindly. Inspect transaction/commit
  evidence and side effects, isolate the replay target, create a
  deduplication/reconciliation plan or compensate effects, then replay a
  bounded range. Verify keys, counts, and downstream effects. If effects
  cannot be distinguished, disclose uncertainty and avoid duplicate
  external actions.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-09

- **Question ID:** `XU-09`
- **Unit(s):** U04,U05
- **Level:** L2
- **Objective tested:** Phantom data from checkpoint mismatch
- **Estimated time:** 8 minutes
- **Question/prompt:** Checkpoint says offset 900; DB ledger ends at
  875; object store has output files for 876–890 but manifest has no
  commit record. Explain likely phantom/orphan state.
- **Model answer:** State may be split across checkpoint, DB, and object
  manifest. Do not treat files as committed output. Reconcile
  authoritative commit markers, inspect idempotency and write ordering,
  and either complete a verified transaction or quarantine orphan files
  before bounded replay. Validate referential and count invariants.
- **Reasoning/worked solution:** State may be split across checkpoint,
  DB, and object manifest. Do not treat files as committed output.
  Reconcile authoritative commit markers, inspect idempotency and write
  ordering, and either complete a verified transaction or quarantine
  orphan files before bounded replay. Validate referential and count
  invariants.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-10

- **Question ID:** `XU-10`
- **Unit(s):** U05,U02
- **Level:** L3
- **Objective tested:** Registry metadata exists but hash fails
- **Estimated time:** 8 minutes
- **Question/prompt:** Registry version 42 exists but artifact hash
  differs from the signed manifest. What should serving do?
- **Model answer:** Fail closed for version 42, preserve evidence, and
  retrieve the expected bytes from a trusted protected copy. Verify
  signature/digest provenance, feature contract, dependencies, and
  prediction regression before promotion. Do not rewrite the manifest to
  match the suspect blob.
- **Reasoning/worked solution:** Fail closed for version 42, preserve
  evidence, and retrieve the expected bytes from a trusted protected
  copy. Verify signature/digest provenance, feature contract,
  dependencies, and prediction regression before promotion. Do not
  rewrite the manifest to match the suspect blob.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-11

- **Question ID:** `XU-11`
- **Unit(s):** U05,U07
- **Level:** L4
- **Objective tested:** Restore versus retrain versus rollback
- **Estimated time:** 8 minutes
- **Question/prompt:** A new model has prediction drift; prior artifact
  is hash-verified but 3 months old; retraining data snapshot is
  incomplete. Decide.
- **Model answer:** Prefer restore/rollback to the verified prior
  artifact if business and compatibility policy allow, with explicit
  staleness risk and canary. Do not claim retraining reproduces the old
  model with incomplete data. Verify predictions and lineage; if neither
  path passes, use an approved fallback and communicate capability
  limits.
- **Reasoning/worked solution:** Prefer restore/rollback to the verified
  prior artifact if business and compatibility policy allow, with
  explicit staleness risk and canary. Do not claim retraining reproduces
  the old model with incomplete data. Verify predictions and lineage; if
  neither path passes, use an approved fallback and communicate
  capability limits.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-12

- **Question ID:** `XU-12`
- **Unit(s):** U02,U07,U09
- **Level:** L2
- **Objective tested:** Missing objects despite successful restore
- **Estimated time:** 8 minutes
- **Question/prompt:** Restore command returns success; object count is
  10,000 vs expected 10,000, but one required key is missing and an
  unrelated duplicate exists. Does count pass?
- **Model answer:** No. Aggregate counts conceal substitutions. Compare
  exact key sets, per-object hashes, and application invariants.
  Preserve report, isolate target, restore the missing key from a
  verified point, and rerun checks. Successful restore status and equal
  counts are insufficient.
- **Reasoning/worked solution:** No. Aggregate counts conceal
  substitutions. Compare exact key sets, per-object hashes, and
  application invariants. Preserve report, isolate target, restore the
  missing key from a verified point, and rerun checks. Successful
  restore status and equal counts are insufficient.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-13

- **Question ID:** `XU-13`
- **Unit(s):** U01,U07
- **Level:** L3
- **Objective tested:** Layered verification invariant fails
- **Estimated time:** 8 minutes
- **Question/prompt:** Restore operation, schema, and checksums pass; a
  business invariant `paid_orders = ledger_entries` fails by 17. What
  result?
- **Model answer:** Fail the drill and do not promote. Preserve all
  evidence, investigate cross-system consistency and transaction
  boundaries, reconcile the 17-entry difference, then rerun. Record RTA
  only when the agreed usable endpoint passes; report objective miss if
  applicable.
- **Reasoning/worked solution:** Fail the drill and do not promote.
  Preserve all evidence, investigate cross-system consistency and
  transaction boundaries, reconcile the 17-entry difference, then rerun.
  Record RTA only when the agreed usable endpoint passes; report
  objective miss if applicable.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-14

- **Question ID:** `XU-14`
- **Unit(s):** U01,U06
- **Level:** L4
- **Objective tested:** Failover with uncertain lag and split-brain risk
- **Estimated time:** 8 minutes
- **Question/prompt:** Primary is unreachable, lag metric is 9 minutes
  old, target RPO is 2 minutes, and fencing is pending. What should
  incident commander do?
- **Model answer:** Do not claim the standby meets RPO or promote
  without following the approved fencing/authority path. Obtain
  independent signals, assess delay versus data-loss risk, preserve
  timeline, and communicate the uncertainty. If emergency policy permits
  a risk-accepted promotion, document explicit authority and expected
  loss, then reconcile.
- **Reasoning/worked solution:** Do not claim the standby meets RPO or
  promote without following the approved fencing/authority path. Obtain
  independent signals, assess delay versus data-loss risk, preserve
  timeline, and communicate the uncertainty. If emergency policy permits
  a risk-accepted promotion, document explicit authority and expected
  loss, then reconcile.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-15

- **Question ID:** `XU-15`
- **Unit(s):** U03,U06
- **Level:** L2
- **Objective tested:** DNS or identity dependency outage
- **Estimated time:** 8 minutes
- **Question/prompt:** Application pods are healthy but cannot resolve
  the secrets endpoint; identity provider is also degraded. What does
  recovery prioritize?
- **Model answer:** Restore independent bootstrap network/DNS and
  identity trust before dependent secrets and applications, following
  the tested dependency graph. Use approved break-glass credentials and
  verify trust chain. Do not weaken authentication globally as a
  shortcut; validate service canary after dependencies recover.
- **Reasoning/worked solution:** Restore independent bootstrap
  network/DNS and identity trust before dependent secrets and
  applications, following the tested dependency graph. Use approved
  break-glass credentials and verify trust chain. Do not weaken
  authentication globally as a shortcut; validate service canary after
  dependencies recover.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-16

- **Question ID:** `XU-16`
- **Unit(s):** U02,U03,U06
- **Level:** L3
- **Objective tested:** Secrets backend and key custody
- **Estimated time:** 8 minutes
- **Question/prompt:** Vault snapshot is available, but unseal/recovery
  material is held only in the failed region. What is missing?
- **Model answer:** Key custody and bootstrap independence. Recover
  escrowed material under dual control, verify integrity and access
  logs, restore secrets backend in isolation, rotate compromised
  credentials as incident facts require, and test consuming workloads. A
  snapshot without usable keys is not a recoverable secrets service.
- **Reasoning/worked solution:** Key custody and bootstrap independence.
  Recover escrowed material under dual control, verify integrity and
  access logs, restore secrets backend in isolation, rotate compromised
  credentials as incident facts require, and test consuming workloads. A
  snapshot without usable keys is not a recoverable secrets service.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-17

- **Question ID:** `XU-17`
- **Unit(s):** U03,U07,U09
- **Level:** L4
- **Objective tested:** Velero report lacks PV data coverage
- **Estimated time:** 8 minutes
- **Question/prompt:** Backup reports Completed and contains
  Deployment/Service objects; no volume snapshot or file-system backup
  evidence is present. What can be claimed?
- **Model answer:** Only API-object capture may be supported. PV bytes
  are unproven. Inspect the pinned Velero/provider configuration and
  backup logs, then restore a throwaway PVC and compare
  data/checksums/application invariants. Avoid version-specific
  assumptions until official docs/schema are checked.
- **Reasoning/worked solution:** Only API-object capture may be
  supported. PV bytes are unproven. Inspect the pinned Velero/provider
  configuration and backup logs, then restore a throwaway PVC and
  compare data/checksums/application invariants. Avoid version-specific
  assumptions until official docs/schema are checked.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-18

- **Question ID:** `XU-18`
- **Unit(s):** U04,U09
- **Level:** L2
- **Objective tested:** CronJob double execution after restore
- **Estimated time:** 8 minutes
- **Question/prompt:** Restored CronJob starts immediately; previous
  execution partially wrote a ledger but checkpoint is old. What first?
- **Model answer:** Suspend/contain the lab schedule using a verified
  version-appropriate method; preserve run logs and ledger evidence;
  reconcile partial side effects and checkpoint boundary; then resume
  only with idempotency/replay gates. Verify exactly one intended effect
  per business key.
- **Reasoning/worked solution:** Suspend/contain the lab schedule using
  a verified version-appropriate method; preserve run logs and ledger
  evidence; reconcile partial side effects and checkpoint boundary; then
  resume only with idempotency/replay gates. Verify exactly one intended
  effect per business key.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-19

- **Question ID:** `XU-19`
- **Unit(s):** U03,U09
- **Level:** L3
- **Objective tested:** GitOps prunes recovered state
- **Estimated time:** 8 minutes
- **Question/prompt:** Velero restores a Service, but GitOps deletes it
  because desired state lacks the object. How should the team proceed?
- **Model answer:** Coordinate ownership and reconciliation; preserve
  audit evidence; decide whether Git should declare the resource or
  whether ownership intentionally differs; restore dependencies/data
  first and resume GitOps after a reviewed plan. Verify no repeated
  prune and application behavior.
- **Reasoning/worked solution:** Coordinate ownership and
  reconciliation; preserve audit evidence; decide whether Git should
  declare the resource or whether ownership intentionally differs;
  restore dependencies/data first and resume GitOps after a reviewed
  plan. Verify no repeated prune and application behavior.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-20

- **Question ID:** `XU-20`
- **Unit(s):** U03,U06
- **Level:** L4
- **Objective tested:** DR runbook only on failed platform
- **Estimated time:** 8 minutes
- **Question/prompt:** The cluster is gone and the only recovery runbook
  was stored in a wiki hosted inside that cluster. What design defect?
- **Model answer:** Recovery documentation shares the failure domain
  with the system it recovers. Establish offline/read-only replicated
  runbooks, bootstrap inventory, key-custody contacts, and authenticated
  access outside the primary platform. Test cold-read access during a
  tabletop.
- **Reasoning/worked solution:** Recovery documentation shares the
  failure domain with the system it recovers. Establish
  offline/read-only replicated runbooks, bootstrap inventory,
  key-custody contacts, and authenticated access outside the primary
  platform. Test cold-read access during a tabletop.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-21

- **Question ID:** `XU-21`
- **Unit(s):** U01,U07
- **Level:** L2
- **Objective tested:** Tier objectives vs measured RTA/RPA
- **Estimated time:** 8 minutes
- **Question/prompt:** Tier-1 target is RTO 60 min/RPO 5 min. Drill
  RTA=54 min and RPA=11 min. Is it compliant?
- **Model answer:** RTO passes by 6 min; RPO fails by 6 min. Report both
  separately, inspect recovery-point evidence, and open remediation for
  data-loss tolerance. Do not collapse into one green score.
- **Reasoning/worked solution:** RTO passes by 6 min; RPO fails by 6
  min. Report both separately, inspect recovery-point evidence, and open
  remediation for data-loss tolerance. Do not collapse into one green
  score.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-22

- **Question ID:** `XU-22`
- **Unit(s):** U07,U01
- **Level:** L3
- **Objective tested:** Evidence bundle missing hashes/timestamps
- **Estimated time:** 8 minutes
- **Question/prompt:** Evidence contains screenshots but no start time,
  end time, manifest hash, or tool versions. What can be concluded?
- **Model answer:** The bundle cannot support reproducible RTA or
  integrity of evidence. Mark the evidence incomplete; preserve
  available artifacts, rerun with timestamped logs/version manifest/hash
  and explicit checks. Do not backfill invented timestamps.
- **Reasoning/worked solution:** The bundle cannot support reproducible
  RTA or integrity of evidence. Mark the evidence incomplete; preserve
  available artifacts, rerun with timestamped logs/version manifest/hash
  and explicit checks. Do not backfill invented timestamps.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-23

- **Question ID:** `XU-23`
- **Unit(s):** U08,U10
- **Level:** L4
- **Objective tested:** Experiment lacks hypothesis/abort baseline
- **Estimated time:** 8 minutes
- **Question/prompt:** Experiment says 'test network resilience',
  selector is `app=*`, no baseline, duration, or abort query. Approve?
- **Model answer:** No. Require falsifiable hypothesis, exact lab
  namespace/selector, baseline SLIs, bounded duration, abort/kill
  switch, safety owner, independent injection proof, and cleanup
  evidence. Run only after preflight and governance gates pass.
- **Reasoning/worked solution:** No. Require falsifiable hypothesis,
  exact lab namespace/selector, baseline SLIs, bounded duration,
  abort/kill switch, safety owner, independent injection proof, and
  cleanup evidence. Run only after preflight and governance gates pass.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-24

- **Question ID:** `XU-24`
- **Unit(s):** U08,U10
- **Level:** L2
- **Objective tested:** Chaos selector matches too many pods
- **Estimated time:** 8 minutes
- **Question/prompt:** Preflight expects one lab pod but selector
  returns 17 pods including monitoring. What next?
- **Model answer:** Block the experiment. Fix namespace/labels and use
  explicit allow-list and max-match guard; do not broaden or apply.
  Capture preflight output and add a negative test that rejects
  cross-namespace or excess matches.
- **Reasoning/worked solution:** Block the experiment. Fix
  namespace/labels and use explicit allow-list and max-match guard; do
  not broaden or apply. Capture preflight output and add a negative test
  that rejects cross-namespace or excess matches.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-25

- **Question ID:** `XU-25`
- **Unit(s):** U08,U10
- **Level:** L3
- **Objective tested:** Chaos reports success but fault did not apply
- **Estimated time:** 8 minutes
- **Question/prompt:** CR status is terminal, target pod stayed
  unchanged, and metrics show no expected signal. How report?
- **Model answer:** Inconclusive/failed, not resilience success. Check
  selector, injection prerequisites, controller/daemon health, and
  independent evidence; preserve events and rerun only after a reviewed
  fix. Include a negative control to detect false success.
- **Reasoning/worked solution:** Inconclusive/failed, not resilience
  success. Check selector, injection prerequisites, controller/daemon
  health, and independent evidence; preserve events and rerun only after
  a reviewed fix. Include a negative control to detect false success.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-26

- **Question ID:** `XU-26`
- **Unit(s):** U08,U10
- **Level:** L4
- **Objective tested:** Watchdog cannot reach Prometheus/API
- **Estimated time:** 8 minutes
- **Question/prompt:** Abort watchdog query times out during a harmful
  lab fault. It has no cached result and continues waiting. What is
  wrong?
- **Model answer:** Fail-safe behavior is missing. Unknown telemetry
  must trigger a bounded abort/escalation for only allow-listed lab
  experiments; log query error, timestamp, experiment identity, and
  action. Test source outage and API denial; verify fault removal and
  recovery.
- **Reasoning/worked solution:** Fail-safe behavior is missing. Unknown
  telemetry must trigger a bounded abort/escalation for only
  allow-listed lab experiments; log query error, timestamp, experiment
  identity, and action. Test source outage and API denial; verify fault
  removal and recovery.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-27

- **Question ID:** `XU-27`
- **Unit(s):** U08,U10
- **Level:** L2
- **Objective tested:** Residual network rules after daemon crash
- **Estimated time:** 8 minutes
- **Question/prompt:** Experiment CR is deleted and daemon restarted,
  but latency remains elevated. What do you inspect?
- **Model answer:** Treat residual fault as possible. Preserve evidence;
  identify the exact kind node and experiment-created qdisc/rule; use
  version/host-appropriate read-only inspection and remove only the
  identified lab rule. Never flush all networking. Verify baseline
  latency and cleanup.
- **Reasoning/worked solution:** Treat residual fault as possible.
  Preserve evidence; identify the exact kind node and experiment-created
  qdisc/rule; use version/host-appropriate read-only inspection and
  remove only the identified lab rule. Never flush all networking.
  Verify baseline latency and cleanup.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-28

- **Question ID:** `XU-28`
- **Unit(s):** U08,U10
- **Level:** L3
- **Objective tested:** Choose Chaos Mesh vs Litmus
- **Estimated time:** 8 minutes
- **Question/prompt:** Team wants Kubernetes-native experiments, probes,
  small laptop footprint, and governed CI; full Litmus portal may be
  heavy. Decide how to evaluate.
- **Model answer:** Compare actual pinned-release fault catalog, probes,
  workflow, footprint, security, CI and upgrade ownership. Hands-on core
  can use Chaos Mesh; Litmus can be read-only/optional until its install
  requirements are verified. Run one platform at a time; no universal
  winner.
- **Reasoning/worked solution:** Compare actual pinned-release fault
  catalog, probes, workflow, footprint, security, CI and upgrade
  ownership. Hands-on core can use Chaos Mesh; Litmus can be
  read-only/optional until its install requirements are verified. Run
  one platform at a time; no universal winner.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-29

- **Question ID:** `XU-29`
- **Unit(s):** U08,U10
- **Level:** L4
- **Objective tested:** Admission policy missing duration/selector
- **Estimated time:** 8 minutes
- **Question/prompt:** Policy checks owner annotation but not duration,
  target namespace, selector, or KernelChaos. Is it sufficient?
- **Model answer:** No. Add required bounded duration, allow-listed lab
  namespace, approved labels/selector, required hypothesis/owner, deny
  broad mode and KernelChaos, and deny unsupported kinds. Validate
  policy schema and negative tests on pinned Kubernetes/policy-engine
  versions.
- **Reasoning/worked solution:** No. Add required bounded duration,
  allow-listed lab namespace, approved labels/selector, required
  hypothesis/owner, deny broad mode and KernelChaos, and deny
  unsupported kinds. Validate policy schema and negative tests on pinned
  Kubernetes/policy-engine versions.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-30

- **Question ID:** `XU-30`
- **Unit(s):** U08,U10
- **Level:** L2
- **Objective tested:** Chaos during incident/freeze
- **Estimated time:** 8 minutes
- **Question/prompt:** A scheduled experiment is due while an incident
  is open and the error budget is exhausted. What should happen?
- **Model answer:** Block the experiment. Freeze/incident gate must
  override schedule, record reason, notify owner, and require
  re-approval after recovery. Audit policy and ensure missed schedule
  does not auto-run later without a fresh gate.
- **Reasoning/worked solution:** Block the experiment. Freeze/incident
  gate must override schedule, record reason, notify owner, and require
  re-approval after recovery. Audit policy and ensure missed schedule
  does not auto-run later without a fresh gate.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-31

- **Question ID:** `XU-31`
- **Unit(s):** U06,U07,U08,U10
- **Level:** L3
- **Objective tested:** DR game day and regional claims
- **Estimated time:** 8 minutes
- **Question/prompt:** A game day stops one kind cluster and fails over
  to another on the same laptop. What report is honest?
- **Model answer:** Describe a workflow simulation only. Measure RTA/RPA
  and capture Unit 7 evidence, but explicitly state common
  host/power/storage/network failure domains prevent regional assurance.
  Roles include safety officer, incident commander, observers, and
  recorder.
- **Reasoning/worked solution:** Describe a workflow simulation only.
  Measure RTA/RPA and capture Unit 7 evidence, but explicitly state
  common host/power/storage/network failure domains prevent regional
  assurance. Roles include safety officer, incident commander,
  observers, and recorder.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-32

- **Question ID:** `XU-32`
- **Unit(s):** U03,U08,U10
- **Level:** L4
- **Objective tested:** Fail-open/fail-closed verification
- **Estimated time:** 8 minutes
- **Question/prompt:** A lab policy engine is stopped; admission begins
  accepting requests although policy intent was fail-closed. What is the
  finding?
- **Model answer:** A critical policy availability/semantics defect.
  Preserve audit and workload evidence, restore the policy component,
  assess objects admitted during outage, and test fail-open/closed
  behavior under bounded lab load. Document expected behavior and
  exception policy; do not test against shared workloads.
- **Reasoning/worked solution:** A critical policy
  availability/semantics defect. Preserve audit and workload evidence,
  restore the policy component, assess objects admitted during outage,
  and test fail-open/closed behavior under bounded lab load. Document
  expected behavior and exception policy; do not test against shared
  workloads.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-33

- **Question ID:** `XU-33`
- **Unit(s):** U04,U06,U07
- **Level:** L2
- **Objective tested:** Data platform after object-store latency and DB
  failover
- **Estimated time:** 8 minutes
- **Question/prompt:** Object writes slow down while database failover
  occurs; checkpoint advances but object manifest lags. What recovery
  invariant matters?
- **Model answer:** Do not advance/declare checkpoint past durable
  output. Reconcile DB transactions, object manifest, stream offsets and
  watermarks at one consistent boundary; throttle replay/catch-up and
  verify freshness/invariants. Add fault tests and alerts for
  checkpoint/output divergence.
- **Reasoning/worked solution:** Do not advance/declare checkpoint past
  durable output. Reconcile DB transactions, object manifest, stream
  offsets and watermarks at one consistent boundary; throttle
  replay/catch-up and verify freshness/invariants. Add fault tests and
  alerts for checkpoint/output divergence.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-34

- **Question ID:** `XU-34`
- **Unit(s):** U05,U06,U07
- **Level:** L3
- **Objective tested:** Model fallback safety and ratio SLI
- **Estimated time:** 8 minutes
- **Question/prompt:** Primary model registry is unavailable; approved
  fallback serves 70% of requests, but no fallback ratio metric exists.
  What is missing?
- **Model answer:** Define fallback ratio = fallback-served requests /
  total eligible requests over a stated window, plus correctness/latency
  guardrails and alert thresholds. Verify fallback artifact integrity
  and feature compatibility; track the unavailable primary path and
  communicate degraded mode.
- **Reasoning/worked solution:** Define fallback ratio = fallback-served
  requests / total eligible requests over a stated window, plus
  correctness/latency guardrails and alert thresholds. Verify fallback
  artifact integrity and feature compatibility; track the unavailable
  primary path and communicate degraded mode.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-35

- **Question ID:** `XU-35`
- **Unit(s):** U02,U07
- **Level:** L4
- **Objective tested:** Backup prune safety
- **Estimated time:** 8 minutes
- **Question/prompt:** The newest backup passed job status but failed
  restore; the older backup is the only verified recovery point and is
  due for pruning. What should happen?
- **Model answer:** Block pruning. Preserve the older verified point
  until a replacement is successfully restored and verified, retention
  obligations are met, and approval is recorded. Job status is not
  enough to retire the only good point.
- **Reasoning/worked solution:** Block pruning. Preserve the older
  verified point until a replacement is successfully restored and
  verified, retention obligations are met, and approval is recorded. Job
  status is not enough to retire the only good point.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-36

- **Question ID:** `XU-36`
- **Unit(s):** U03,U07,U09
- **Level:** L2
- **Objective tested:** Restore succeeds but security parity fails
- **Estimated time:** 8 minutes
- **Question/prompt:** Data and canary pass, but restored workload uses
  a broad service account and unsigned image unlike approved baseline.
  Is recovery complete?
- **Model answer:** No. Service usability without security parity is not
  full recovery. Isolate, restore approved RBAC/image provenance/secrets
  controls, assess exposure, and rerun security and functional gates
  before promotion. Preserve evidence and record the objective impact.
- **Reasoning/worked solution:** No. Service usability without security
  parity is not full recovery. Isolate, restore approved RBAC/image
  provenance/secrets controls, assess exposure, and rerun security and
  functional gates before promotion. Preserve evidence and record the
  objective impact.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-37

- **Question ID:** `XU-37`
- **Unit(s):** U02,U03,U06
- **Level:** L3
- **Objective tested:** Primary key store unavailable but escrow keys
  exist
- **Estimated time:** 8 minutes
- **Question/prompt:** Primary KMS is unavailable; escrowed recovery
  material exists under dual control. What sequence is appropriate?
- **Model answer:** Follow documented key-custody/dual-control
  procedure, verify escrow integrity and authorization, establish
  decryption in isolated recovery, restore secrets/data, and audit use.
  Do not bypass controls or expose raw keys. Test escrow periodically.
- **Reasoning/worked solution:** Follow documented
  key-custody/dual-control procedure, verify escrow integrity and
  authorization, establish decryption in isolated recovery, restore
  secrets/data, and audit use. Do not bypass controls or expose raw
  keys. Test escrow periodically.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-38

- **Question ID:** `XU-38`
- **Unit(s):** U03,U05,U07
- **Level:** L4
- **Objective tested:** Restore-first vs rebuild/retrain
- **Estimated time:** 8 minutes
- **Question/prompt:** Model artifact is missing but full training data
  and code are available; service RTO is 30 min and retraining takes
  4 h. What is the decision framework?
- **Model answer:** Search for a verified previous artifact or approved
  fallback first; retraining cannot meet the 30-minute objective under
  stated timing and may not reproduce outputs. If no verified artifact
  exists, communicate degraded service and retraining estimate; preserve
  lineage and validate a new version before promotion.
- **Reasoning/worked solution:** Search for a verified previous artifact
  or approved fallback first; retraining cannot meet the 30-minute
  objective under stated timing and may not reproduce outputs. If no
  verified artifact exists, communicate degraded service and retraining
  estimate; preserve lineage and validate a new version before
  promotion.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-39

- **Question ID:** `XU-39`
- **Unit(s):** U06,U08,U10
- **Level:** L2
- **Objective tested:** Compound failure during recovery
- **Estimated time:** 8 minutes
- **Question/prompt:** During an isolated DR drill, dependency latency
  rises while the recovery target fails its canary and the error
  threshold is crossed. Continue?
- **Model answer:** Abort or pause the experiment/recovery step
  according to the pre-approved threshold, preserve evidence, restore
  safe dependency state, and verify the canary before resuming. Do not
  add another fault while current hypothesis is invalid. Record why the
  plan stopped.
- **Reasoning/worked solution:** Abort or pause the experiment/recovery
  step according to the pre-approved threshold, preserve evidence,
  restore safe dependency state, and verify the canary before resuming.
  Do not add another fault while current hypothesis is invalid. Record
  why the plan stopped.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

### XU-40

- **Question ID:** `XU-40`
- **Unit(s):** U01,U07,U08,U09,U10
- **Level:** L3
- **Objective tested:** Cross-unit remediation plan
- **Estimated time:** 8 minutes
- **Question/prompt:** A drill finds RPO miss, missing PV data, and a
  chaos false-pass. Create a remediation plan.
- **Model answer:** Create separate defects with severity, owner, due
  date, dependency, acceptance evidence, and retest version. Restore PV
  data path and verify a full restore; improve recovery-point
  objective/measurement; fix selector and add negative test/independent
  injection proof. Update RTA/RPA targets only with owner approval and
  retest evidence.
- **Reasoning/worked solution:** Create separate defects with severity,
  owner, due date, dependency, acceptance evidence, and retest version.
  Restore PV data path and verify a full restore; improve recovery-point
  objective/measurement; fix selector and add negative test/independent
  injection proof. Update RTA/RPA targets only with owner approval and
  retest evidence.
- **Common wrong answers or failure modes:** Common failure modes
  include trusting a timestamp or terminal status alone, promoting
  before fencing/verification, replaying without idempotency, deleting
  the last good recovery point, or overstating what a laptop simulation
  proves.
- **Evidence/verification:** Use the named unit artifacts: objective
  register, backup inventory, dependency graph, checkpoint/commit
  ledger, digest/lineage, restore evidence bundle, experiment preflight,
  alerts, and decision log as applicable.
- **Assumptions and limitations:** The scenario is illustrative; any
  unspecified version, service limit, or implementation behavior must be
  verified against official documentation and the pinned environment.

## 16 design-review whiteboard prompts

These prompts are **additional** to the 200 numbered questions. Each
requires written trade-off reasoning, not only a diagram. Use the common
32-point rubric at the end of this section.

### WB-01 — Recovery objective tiers and negotiation for a data/ML platform

- **Objective and context:** Design objective tiers for API, batch data,
  and model serving. Include BIA inputs, owners, RTO/RPO, dependencies,
  clock boundaries, measured RTA/RPA, and negotiation records.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: service impact versus cost; serial
  versus parallel recovery; target versus demonstrated capability.
- **Common failure modes:** Failure modes: one-size-fits-all objectives;
  target without owner; restore time mistaken for RTA; dependency
  impossible to recover in budget.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-02 — Backup architecture and ransomware-style resilience

- **Objective and context:** Draw state inventory and protection paths
  for DB, object store, Kubernetes metadata, model artifacts, keys, Git,
  and credentials against benign simulated deletion/corruption and
  compromised credentials.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: replicas/snapshots/immutable copies;
  retention duration; separate accounts and key custody; pull-based
  access.
- **Common failure modes:** Failure modes: shared credentials; key loss;
  replication of corruption; no restore proof; pruning last good point.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-03 — Platform rebuild versus etcd restore

- **Objective and context:** Design a decision record choosing
  rebuild-from-Git versus control-plane state restore for a throwaway
  cluster; state assumptions and data-plane separation.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: speed, state fidelity, compatibility,
  secret availability, cluster identity, and external data recovery.
- **Common failure modes:** Failure modes: assuming etcd contains PV
  bytes; incompatible versions; missing CRDs/operators; uncoordinated
  GitOps.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-04 — Data pipeline recoverability and replay design

- **Objective and context:** Design offset/checkpoint/sink-commit
  alignment, idempotency, replay retention, throttling, watermarks, and
  reconciliation for a streaming pipeline.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: exactly-once boundaries, replay cost,
  deduplication storage, late events, and external side effects.
- **Common failure modes:** Failure modes: phantom data, duplicate side
  effects, expired input, checkpoint ahead of durable output.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-05 — ML artifact and registry recovery

- **Objective and context:** Design model metadata/artifact/data-feature
  version triple, integrity gates, alias history, approved fallback,
  rollback/retrain decision, and prediction regression.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: exact restore versus retrain,
  staleness versus integrity, availability versus fail-closed security.
- **Common failure modes:** Failure modes: metadata without blobs; hash
  mismatch; feature drift; retraining relabeled as old version.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-06 — Regional DR strategy and fail-back

- **Objective and context:** Design failover/fail-back decision tree for
  async replication, DNS, identity, secrets, and database, including
  fencing and uncertainty branches.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: downtime versus possible data loss;
  automation versus human authority; recovery capacity and consistency.
- **Common failure modes:** Failure modes: split brain; stale lag
  telemetry; untested quota/capacity; claiming a local drill proves
  region independence.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-07 — Dependency outage strategy for registry, secrets backend, and identity provider

- **Objective and context:** Design bootstrap sequence and independent
  trust path for a cluster that depends on identity, secrets, and
  registry to start.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: offline bootstrap material, dual
  control, security exposure, operational complexity, and emergency
  access.
- **Common failure modes:** Failure modes: circular dependency; keys
  stored only in failed region; global auth bypass; no audit of
  break-glass use.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-08 — Restore-drill program and evidence design

- **Objective and context:** Design drill cadence, evidence bundle,
  expiry rules, cold-read execution, defect corpus, RTA/RPA measurement,
  and remediation tracking.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: drill frequency, workload realism,
  resource budget, and confidence versus cost.
- **Common failure modes:** Failure modes: screenshot-only evidence;
  stale green badge; author-only runbook; missing application
  invariants.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-09 — Chaos program with safety guardrails

- **Objective and context:** Design a governed chaos catalog with risk
  classes, lab opt-in, selector preflight, duration, abort, watchdog,
  cleanup, approvals, and scorecard.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: learning value versus blast radius;
  automation versus oversight; fault realism versus local-host limits.
- **Common failure modes:** Failure modes: mode=all; no hypothesis; no
  abort; no independent injection proof; residual network rules.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-10 — Velero versus GitOps versus application-native recovery responsibilities

- **Objective and context:** Create a responsibility matrix
  distinguishing API objects, PV data, operator CRDs, desired-state
  reconciliation, DB-native recovery, and scheduled work.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: source of truth, restore ordering,
  version compatibility, data consistency, and ownership boundaries.
- **Common failure modes:** Failure modes: assuming object backup
  includes PV bytes; GitOps prunes restore; CronJob duplicates;
  unverified flags.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-11 — Backup encryption key custody and escrow

- **Objective and context:** Design key creation, backup, escrow,
  dual-control recovery, rotation, audit, and testing independent of the
  primary platform.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: availability, separation of duties,
  cryptographic exposure, recovery latency, and regulatory constraints.
- **Common failure modes:** Failure modes: immutable ciphertext with
  lost key; key backup shares failure domain; uncontrolled break-glass
  access.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-12 — Post-failover steady-state operations and security parity

- **Objective and context:** Define post-failover checks for data
  consistency, SLOs, identity, secrets, RBAC, image provenance, logging,
  and controlled fail-back.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: rapid traffic restoration versus
  security and correctness gates.
- **Common failure modes:** Failure modes: canary-only acceptance; broad
  emergency permissions; missing audit; fail-back without
  reconciliation.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-13 — DR cost/capacity trade-offs using resource units

- **Objective and context:** Compare warm, pilot-light, and rebuild
  approaches using relative compute/storage/network units rather than
  invented prices. Include recovery concurrency and quota assumptions.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: reserved capacity, idle resource cost,
  restore throughput, and dependency startup order.
- **Common failure modes:** Failure modes: assuming capacity exists;
  serial restores exceed RTO; data transfer bottleneck ignored; no
  measured throughput.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-14 — Consistent recovery point across database, object store, and queue/stream

- **Objective and context:** Design a cross-system consistency protocol
  using transaction IDs, object manifests, offsets, checkpoints,
  watermarks, and reconciliation.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: pause/freeze duration, distributed
  transaction limitations, replay complexity, and bounded loss.
- **Common failure modes:** Failure modes: timestamp-only alignment;
  orphan objects; phantom rows; model metadata newer than source data.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-15 — DR security parity and trust continuity

- **Objective and context:** Design identity/key/bootstrap recovery and
  security validation before promoting a restored environment.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: break-glass access, least privilege,
  service availability, credential rotation, and forensic preservation.
- **Common failure modes:** Failure modes: service runs with unsafe
  permissions; secrets unavailable; compromised identity reused;
  signed-image policy bypass.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

### WB-16 — Resilience program metrics and governance

- **Objective and context:** Design program KPIs for verified restore
  coverage, objective attainment, defect remediation, repeat incidents,
  abort/cleanup reliability, and evidence freshness.
- **Constraints/assumptions:** Zero-budget laptop lab is the default; no
  cloud account, production system, real customer data, or real SaaS
  disruption. State which facts are assumptions and which are measured.
  Two local kind clusters are not independent regions.
- **Required artifacts:** A diagram or decision table; owner and
  approval matrix; sequence/runbook; objective/acceptance criteria;
  evidence bundle outline; rollback/abort plan; and an explicit
  limitations section.
- **Key trade-offs:** Trade-offs: measurement cost, causal attribution,
  useful leading indicators, and avoiding vanity counts.
- **Common failure modes:** Failure modes: number of experiments as
  success metric; findings never fixed; stale evidence; no owners or
  review cadence.
- **Evaluation rubric:** Apply the common rubric below; award full
  credit only for observable evidence and reasoned trade-offs.

**Common whiteboard rubric (32 points per prompt):** correctness and
scope (0–4); explicit assumptions and uncertainty (0–4); recovery safety
and blast-radius controls (0–4); dependency/failure-domain realism
(0–4); verification and evidence (0–4); trade-offs and alternatives
(0–4); ownership/governance/communication (0–4); and measurable
acceptance/rollback criteria (0–4). A diagram without a reasoned
explanation earns at most half of the correctness points. Suggested
interpretation: 28–32 ready for peer review; 22–27 revise weak areas;
below 22 redesign before implementation.

## Score tracking and remediation templates

### Score tracker

| Unit / scenario | Level | Question type                        | Attempted | Correct / points | Confidence (L/M/H) | Error pattern | Remediation action | Retest date / result |
|-----------------|-------|--------------------------------------|-----------|------------------|--------------------|---------------|--------------------|----------------------|
| Unit 1          | L1–L4 | SA/MCQ/AI/AR/IR/DES/EX               |           |                  |                    |               |                    |                      |
| Unit 2          | L1–L4 | SA/MCQ/AI/AR/IR/DES/EX               |           |                  |                    |               |                    |                      |
| Unit 3          | L1–L4 | SA/MCQ/AI/AR/IR/DES/EX               |           |                  |                    |               |                    |                      |
| Unit 4          | L1–L4 | SA/MCQ/AI/AR/IR/DES/EX               |           |                  |                    |               |                    |                      |
| Unit 5          | L1–L4 | SA/MCQ/AI/AR/IR/DES/EX               |           |                  |                    |               |                    |                      |
| Unit 6          | L1–L4 | SA/MCQ/AI/AR/IR/DES/EX               |           |                  |                    |               |                    |                      |
| Unit 7          | L1–L4 | SA/MCQ/AI/AR/IR/DES/EX               |           |                  |                    |               |                    |                      |
| Unit 8          | L1–L4 | SA/MCQ/AI/AR/IR/DES/EX               |           |                  |                    |               |                    |                      |
| Unit 9          | L1–L4 | SA/MCQ/AI/AR/IR/DES/EX               |           |                  |                    |               |                    |                      |
| Unit 10         | L1–L4 | SA/MCQ/AI/AR/IR/DES/EX               |           |                  |                    |               |                    |                      |
| Cross-unit XU   | L2–L4 | Calculation/artifact/decision/design |           |                  |                    |               |                    |                      |

### Remediation map

| Error pattern                                                             | Revisit            | Retest activity                                                                   | Passing evidence                                                       |
|---------------------------------------------------------------------------|--------------------|-----------------------------------------------------------------------------------|------------------------------------------------------------------------|
| RTO confused with restore-command time; RPO confused with backup interval | Unit 1             | Recalculate a full timeline and newest verified recovery point                    | Correct units, clock boundaries, and target-vs-measured distinction    |
| Backup job treated as proof; keys or state omitted                        | Unit 2 and Unit 7  | Build survivability matrix and restore a synthetic historical point               | Verified restore, key access, integrity and application checks         |
| Metadata confused with persistent bytes; GitOps conflict ignored          | Unit 3 and Unit 9  | Rebuild throwaway cluster with ordered dependencies and controlled reconciliation | CRDs/operators ready, data verified, no unintended prune               |
| Replay without transaction boundary or idempotency                        | Unit 4             | Simulate crash between sink commit and checkpoint; reconcile bounded replay       | No missing/duplicate business keys and freshness restored              |
| Model hash/lineage mismatch ignored                                       | Unit 5             | Reject mismatched artifact and verify approved fallback                           | Digest/signature, feature contract, prediction regression, audit trail |
| Failover without fencing or honest failure-domain claim                   | Unit 6             | Walk stale-lag and partition decision tree                                        | Decision thresholds, authority, fencing, comms, limitation stated      |
| Evidence bundle incomplete or stale                                       | Unit 7             | Cold-read restore drill with intentional missing-object test                      | Reproducible timestamps, hashes, invariants, owner and retest          |
| Fault reported successful without proof or cleanup                        | Unit 8 and Unit 10 | Run selector negative test and abort/cleanup drill in lab                         | Target proof, SLI evidence, kill switch, no residual effect            |
| Version-specific flag/CRD assumed                                         | Unit 9 and Unit 10 | Check pinned-release official docs/schema and validate in disposable cluster      | Verification register closed before execution                          |
| Design rubric misses ownership or evidence                                | Relevant WB prompt | Redraw decision tree and add measurable acceptance gates                          | Peer can execute/verify without undocumented assumptions               |

## Source-to-question traceability matrix

| Source requirement/topic                                                                                                                      | Unit(s) covered                          | Question IDs                                                                       | Question type/level                                     | What the answer tests                                                            | Evidence/worked solution                                          | Status                                              |
|-----------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|------------------------------------------------------------------------------------|---------------------------------------------------------|----------------------------------------------------------------------------------|-------------------------------------------------------------------|-----------------------------------------------------|
| Recovery time and recovery point objectives and learning objectives                                                                           | Unit 1                                   | `U01-SA-01–03`, `MCQ-01–03`, `AI-01–03`, `AR-01–03`, `IR-01`, `DES-01`, `EX-01–02` | L1–L4; all required types                               | Topic-specific reasoning and safe recovery decisions                             | Explanations, artifact analysis, incident sequence, design rubric | PASS (generated structure; content review required) |
| Backup scope, retention, and immutability and learning objectives                                                                             | Unit 2                                   | `U02-SA-01–03`, `MCQ-01–03`, `AI-01–03`, `AR-01–03`, `IR-01`, `DES-01`, `EX-01–02` | L1–L4; all required types                               | Topic-specific reasoning and safe recovery decisions                             | Explanations, artifact analysis, incident sequence, design rubric | PASS (generated structure; content review required) |
| Restoring platform metadata and configuration and learning objectives                                                                         | Unit 3                                   | `U03-SA-01–03`, `MCQ-01–03`, `AI-01–03`, `AR-01–03`, `IR-01`, `DES-01`, `EX-01–02` | L1–L4; all required types                               | Topic-specific reasoning and safe recovery decisions                             | Explanations, artifact analysis, incident sequence, design rubric | PASS (generated structure; content review required) |
| Recovering data pipeline state and checkpoints and learning objectives                                                                        | Unit 4                                   | `U04-SA-01–03`, `MCQ-01–03`, `AI-01–03`, `AR-01–03`, `IR-01`, `DES-01`, `EX-01–02` | L1–L4; all required types                               | Topic-specific reasoning and safe recovery decisions                             | Explanations, artifact analysis, incident sequence, design rubric | PASS (generated structure; content review required) |
| Recovering model artifacts and registry metadata and learning objectives                                                                      | Unit 5                                   | `U05-SA-01–03`, `MCQ-01–03`, `AI-01–03`, `AR-01–03`, `IR-01`, `DES-01`, `EX-01–02` | L1–L4; all required types                               | Topic-specific reasoning and safe recovery decisions                             | Explanations, artifact analysis, incident sequence, design rubric | PASS (generated structure; content review required) |
| Regional failure and dependency outage strategies and learning objectives                                                                     | Unit 6                                   | `U06-SA-01–03`, `MCQ-01–03`, `AI-01–03`, `AR-01–03`, `IR-01`, `DES-01`, `EX-01–02` | L1–L4; all required types                               | Topic-specific reasoning and safe recovery decisions                             | Explanations, artifact analysis, incident sequence, design rubric | PASS (generated structure; content review required) |
| Restore drills and recovery evidence and learning objectives                                                                                  | Unit 7                                   | `U07-SA-01–03`, `MCQ-01–03`, `AI-01–03`, `AR-01–03`, `IR-01`, `DES-01`, `EX-01–02` | L1–L4; all required types                               | Topic-specific reasoning and safe recovery decisions                             | Explanations, artifact analysis, incident sequence, design rubric | PASS (generated structure; content review required) |
| Failure injection and resilience exercises and learning objectives                                                                            | Unit 8                                   | `U08-SA-01–03`, `MCQ-01–03`, `AI-01–03`, `AR-01–03`, `IR-01`, `DES-01`, `EX-01–02` | L1–L4; all required types                               | Topic-specific reasoning and safe recovery decisions                             | Explanations, artifact analysis, incident sequence, design rubric | PASS (generated structure; content review required) |
| Kubernetes backup and restore with Velero and learning objectives                                                                             | Unit 9                                   | `U09-SA-01–03`, `MCQ-01–03`, `AI-01–03`, `AR-01–03`, `IR-01`, `DES-01`, `EX-01–02` | L1–L4; all required types                               | Topic-specific reasoning and safe recovery decisions                             | Explanations, artifact analysis, incident sequence, design rubric | PASS (generated structure; content review required) |
| Chaos engineering with Litmus and Chaos Mesh and learning objectives                                                                          | Unit 10                                  | `U10-SA-01–03`, `MCQ-01–03`, `AI-01–03`, `AR-01–03`, `IR-01`, `DES-01`, `EX-01–02` | L1–L4; all required types                               | Topic-specific reasoning and safe recovery decisions                             | Explanations, artifact analysis, incident sequence, design rubric | PASS (generated structure; content review required) |
| RTO/RPO calculations and target vs measured results                                                                                           | U01, U06, U07, XU-01–02, XU-21, XU-38    | `U01-EX-01`, `XU-01`, `XU-02`, `XU-21`                                             | L2–L4 calculation/decision                              | Backup cadence, lag, throughput, phase timing, RTA/RPA                           | Equations and units in answers                                    | PASS                                                |
| Backup survivability matrix: snapshot, replica, versioning, Git/mirror, immutable, pull-based                                                 | U02, XU-03–04, XU-35, WB-02              | `U02-DES-01`, `XU-03`, `XU-04`, `XU-35`, `WB-02`                                   | L3–L4 design/decision                                   | Deletion, corruption, credential compromise, site loss, keys/retention           | Scenario-specific matrix and restore checks                       | PASS                                                |
| Recovery ordering, bootstrap trust, DNS, identity, secrets, registry, storage, DB, control plane, CRDs/operators, GitOps, apps, observability | U03, U06, U09, XU-05–06, XU-15–16, XU-20 | `U03-DES-01`, `XU-05`, `XU-06`, `XU-15`, `XU-16`, `XU-20`                          | L3–L4                                                   | Dependency graph, circular dependencies, metadata/data separation                | Ordered recovery and cold-read evidence                           | PASS                                                |
| Consistent cross-system recovery point: DB/object/queue/checkpoint/model                                                                      | U04, U05, U07, XU-07–09, XU-33, XU-39    | `XU-07–09`, `XU-33`, `XU-39`                                                       | L3–L4                                                   | Transactions, watermarks, offsets, orphan/phantom state, replay                  | Reconciliation and invariant checks                               | PASS                                                |
| Restore verification: operation, structure, checksums, invariants, canary, model regression, evidence hashes                                  | U05, U07, U09, XU-12–13, XU-22, XU-36    | `U07-AI-01–03`, `XU-12`, `XU-13`, `XU-22`, `XU-36`                                 | L2–L4                                                   | Shallow pass versus usable service                                               | Layered evidence and RTA/RPA                                      | PASS                                                |
| Pipeline replay safety, idempotency, retention, throttling, phantom data                                                                      | U04, XU-08–09, XU-18, XU-33              | `U04-SA-01–03`, `U04-EX-01`, `XU-08`, `XU-09`, `XU-18`, `XU-33`                    | L1–L4                                                   | Bounded replay and reconciliation                                                | Commit/checkpoint ledger and key checks                           | PASS                                                |
| ML restore/retrain/rollback, artifact integrity, aliases, version triple, fallback                                                            | U05, XU-10–11, XU-34, XU-38              | `U05-SA-01–03`, `U05-IR-01`, `XU-10`, `XU-11`, `XU-34`, `XU-38`                    | L1–L4                                                   | Fail-closed integrity and model behavior                                         | Digest, lineage, feature checks, prediction regression            | PASS                                                |
| Failover uncertainty, replication lag, fencing, split brain, fail-back                                                                        | U06, XU-14, XU-20, XU-31, XU-37          | `U06-SA-01–03`, `U06-IR-01`, `XU-14`, `XU-20`, `XU-31`, `XU-37`                    | L2–L4                                                   | Decision thresholds, alternatives, communication                                 | Lag/fencing evidence and decision log                             | PASS                                                |
| Chaos safety, selector, abort, watchdog, cleanup, freeze, evidence of injection                                                               | U08, U10, XU-23–30, XU-32, XU-39         | `U08-SA-01–03`, `U10-SA-01–03`, `XU-23–30`, `XU-32`, `XU-39`                       | L1–L4                                                   | Narrow scope, independent injection proof, residual-fault checks                 | Preflight, SLI, abort/cleanup evidence                            | PASS                                                |
| Velero and GitOps, PV data path, CRD/operator ordering, CronJob hazards, version verification                                                 | U03, U09, XU-17–19, XU-35–36             | `U09-SA-01–03`, `U09-IR-01`, `XU-17–19`, `XU-35–36`                                | L1–L4                                                   | Objects versus data and reconciliation risks                                     | Pinned version docs/schema and throwaway restore                  | VERIFY for version-specific product behavior        |
| 40 unique cross-unit scenarios                                                                                                                | Multiple units                           | `XU-01`–`XU-40`                                                                    | L2–L4                                                   | All 40 required scenario families                                                | Full model answer and verification guidance per scenario          | PASS (count audited)                                |
| 16 whiteboard prompts                                                                                                                         | Multiple units                           | `WB-01`–`WB-16`                                                                    | L4                                                      | All required design-review topics                                                | Artifacts, trade-offs, common failure modes, common rubric        | PASS (count audited)                                |
| Per-unit question categories and counts                                                                                                       | U01–U10                                  | Each `Uxx` family                                                                  | 16 per unit; 3 SA, 3 MCQ, 3 AI, 3 AR, 1 IR, 1 DES, 2 EX | Required format coverage                                                         | IDs, answer material, distractor explanations, design rubric      | PASS (count audited)                                |
| Scoring, remediation, source limits, safety and fidelity                                                                                      | All                                      | Front matter, remediation table, audit checklist                                   | All levels                                              | 80/60 thresholds; source gaps; no production/destructive claims; laptop fidelity | Templates and final audit                                         | PASS with stated source limitations                 |

## Final audit checklist

- [x] 10 Unit sections in the required order and filenames.
- [x] 16 numbered questions per unit: 3 conceptual, 3 MCQ, 3 artifact
  interpretation, 3 artifact review, 1 incident, 1 design, 2 additional.
- [x] Exactly 40 cross-unit IDs `XU-01` through `XU-40`.
- [x] Exactly 16 separate design-review prompts; not counted toward the
  200 numbered questions.
- [x] Each numbered question includes ID, unit(s), level, objective,
  time, prompt, model answer/reasoning, wrong-answer guidance, evidence,
  and assumptions/limitations.
- [x] Each MCQ has exactly A–D and explanations for correct option and
  all distractors.
- [x] Each artifact-review prompt explicitly requires at least three
  defects, mechanisms, corrections, and passing evidence.
- [x] Scoring thresholds exactly:
  `≥ 80% proceed; 60–79% remediate; < 60% repeat`.
- [x] Destructive scenarios are hypothetical or lab-only; no
  production/shared-cluster execution is required.
- [x] Local kind cluster simulations are not represented as real
  regional assurance.
- [x] Version-sensitive tool behavior is framed for verification rather
  than invented universal claims.
- [x] Source limitations are disclosed; not all repository tree/lesson
  files were directly available for inspection.
- [ ] Independent technical review of all 200 model answers and every
  product-specific detail remains recommended before using this bank as
  a formal assessment.

### Audit report

- **Numbered question IDs:** 200 planned (160 unit questions + 40
  cross-unit scenarios).
- **Per-unit counts:** 16 each for Units 1–10.
- **Cross-unit count:** 40, IDs XU-01–XU-40.
- **Design-review prompts:** 16, IDs WB-01–WB-16.
- **MCQ structure:** 30 MCQs total; each authored with four options A–D
  and a rationale for the correct answer and each distractor.
- **Calculation audit:** example arithmetic is shown in answers where
  required; computed values are explicitly distinguished from measured
  outcomes. This is a structural/calculation review, not independent
  execution against production data.
- **Safety audit:** prompts prohibit production/shared targets and
  require isolation, verification, and preservation of evidence.
- **Traceability status:** syllabus topics mapped to unit/scenario IDs;
  version-sensitive Velero/Chaos/Litmus behavior remains `VERIFY`.
- **Source limitations:** no claim is made that the entire repository
  tree or all Unit 1–10 lesson files were read in this turn.
