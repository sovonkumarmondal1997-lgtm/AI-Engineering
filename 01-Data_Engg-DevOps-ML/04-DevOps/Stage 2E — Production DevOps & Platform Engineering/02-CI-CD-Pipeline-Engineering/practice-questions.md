# CI/CD Pipeline Engineering — Practice Questions and Answer Key

## Document metadata

- **Stage/module:** Stage 2E — Production DevOps & Platform Engineering / M02 — CI/CD Pipeline Engineering
- **Target:** `Stage 2E — Production DevOps & Platform Engineering/02-CI-CD-Pipeline-Engineering/practice-questions.md`
- **Learner baseline:** Git, Linux shell, Python, basic pytest, and container-image fundamentals; limited production CI/CD experience.
- **Environment:** laptop-first, zero-budget, WSL2 Ubuntu primary; no paid runners or production credentials required.
- **Estimated completion time:** 24–36 hours (estimate, including written answers and remediation).
- **Status:** Draft answer key. No workflow, script, test, API call, or lab was executed; no live documentation was consulted. Version-sensitive claims are marked `[VERIFY]`.
- **Source boundary:** The supplied practice prompt, available roadmap tree, and syllabus-generation prompt were inspected. Not all lesson files were independently re-read; cross-check answers against each lesson before formal grading.

## How to use this question bank

Attempt each question before reading the answer. For reviews, identify root cause and impact for every defect. For incidents, separate observations from hypotheses and state what evidence would change the conclusion. Treat `[VERIFY]` as a pre-production documentation check.

## Coverage map and question inventory

| Section | SA | MCQ | CFG | REV | INC | DES | Total |
|---|---:|---:|---:|---:|---:|---:|---:|

| Unit 1: CI/CD architecture and pipeline design principles | 3 | 3 | 2 | 2 | 1 | 1 | 12 |

| Unit 2: GitHub Actions: workflows, runners, reusable workflows | 3 | 3 | 2 | 2 | 1 | 1 | 12 |

| Unit 3: GitLab CI: stages, jobs, templates | 3 | 3 | 2 | 2 | 1 | 1 | 12 |

| Unit 4: Build caching, parallelism, and pipeline speed | 3 | 3 | 2 | 2 | 1 | 1 | 12 |

| Unit 5: Monorepo and path-based pipelines | 3 | 3 | 2 | 2 | 1 | 1 | 12 |

| Unit 6: Test stages, quality gates, flaky-test management | 3 | 3 | 2 | 2 | 1 | 1 | 12 |

| Unit 7: Artifact repositories and package publishing | 3 | 3 | 2 | 2 | 1 | 1 | 12 |

| Unit 8: Semantic versioning, changelogs, release automation | 3 | 3 | 2 | 2 | 1 | 1 | 12 |

| Unit 9: Environment promotion, approvals, protected branches | 3 | 3 | 2 | 2 | 1 | 1 | 12 |

| Unit 10: Self-hosted runners: scaling and security | 3 | 3 | 2 | 2 | 1 | 1 | 12 |

| Unit 11: Pipeline observability and DORA delivery metrics | 3 | 3 | 2 | 2 | 1 | 1 | 12 |

| Cross-unit integration | — | — | — | — | — | — | 20 |
| **Total scored questions** | **33** | **33** | **22** | **22** | **11** | **11** | **152** |
| Additional whiteboard prompts | — | — | — | — | — | — | 8 |

### ID inventory

Each unit uses `Uxx-SA-01..03`, `Uxx-MCQ-01..03`, `Uxx-CFG-01..02`, `Uxx-REV-01..02`, `Uxx-INC-01`, and `Uxx-DES-01`. Integration IDs are `XINT-01..20`; whiteboard IDs are `DR-01..08`.

### Coverage map


- **Unit 1 — CI/CD architecture and pipeline design principles:** ['CI vs continuous delivery vs deployment', 'DAGs, critical path, fail-fast', 'build once, deploy many, immutable digest']. IDs: `U01-SA-*`, `U01-MCQ-*`, `U01-CFG-*`, `U01-REV-*`, `U01-INC-01`, `U01-DES-01`.

- **Unit 2 — GitHub Actions: workflows, runners, reusable workflows:** ['Reusable workflow vs composite action', 'Least-privilege permissions and full-SHA pinning', 'pull_request vs pull_request_target trust boundary']. IDs: `U02-SA-*`, `U02-MCQ-*`, `U02-CFG-*`, `U02-REV-*`, `U02-INC-01`, `U02-DES-01`.

- **Unit 3 — GitLab CI: stages, jobs, templates:** ['Artifacts vs cache', 'workflow:rules vs job rules', 'Cross-platform mapping and syntax verification']. IDs: `U03-SA-*`, `U03-MCQ-*`, `U03-CFG-*`, `U03-REV-*`, `U03-INC-01`, `U03-DES-01`.

- **Unit 4 — Build caching, parallelism, and pipeline speed:** ['Cache key by runtime and lockfile', 'Queue vs execution time; critical path', 'Cold/warm benchmarking and cache trust']. IDs: `U04-SA-*`, `U04-MCQ-*`, `U04-CFG-*`, `U04-REV-*`, `U04-INC-01`, `U04-DES-01`.

- **Unit 5 — Monorepo and path-based pipelines:** ['Shared-library dependency fan-out', 'Stable required aggregate gate', 'Merge base, shallow clones, force pushes and merge queues']. IDs: `U05-SA-*`, `U05-MCQ-*`, `U05-CFG-*`, `U05-REV-*`, `U05-INC-01`, `U05-DES-01`.

- **Unit 6 — Test stages, quality gates, flaky-test management:** ['pytest/JUnit/coverage gates', 'Data-contract and ML evaluation gates', 'Flake rate, quarantine owner/expiry, retry limits']. IDs: `U06-SA-*`, `U06-MCQ-*`, `U06-CFG-*`, `U06-REV-*`, `U06-INC-01`, `U06-DES-01`.

- **Unit 7 — Artifact repositories and package publishing:** ['Artifact vs cache vs package vs image', 'Digest/checksum and manifest verification', 'Trusted publication and immutable versions']. IDs: `U07-SA-*`, `U07-MCQ-*`, `U07-CFG-*`, `U07-REV-*`, `U07-INC-01`, `U07-DES-01`.

- **Unit 8 — Semantic versioning, changelogs, release automation:** ['SemVer MAJOR/MINOR/PATCH', 'Conventional Commit limits and changelog consistency', 'Idempotent release recovery and partial external state']. IDs: `U08-SA-*`, `U08-MCQ-*`, `U08-CFG-*`, `U08-REV-*`, `U08-INC-01`, `U08-DES-01`.

- **Unit 9 — Environment promotion, approvals, protected branches:** ['Promote same digest through environments', 'Branch/environment rules and separation of duties', 'Bypass auditing, rollback, deployment handoff']. IDs: `U09-SA-*`, `U09-MCQ-*`, `U09-CFG-*`, `U09-REV-*`, `U09-INC-01`, `U09-DES-01`.

- **Unit 10 — Self-hosted runners: scaling and security:** ['Persistent vs ephemeral lifecycle', 'Public-fork trust boundary, Docker socket and egress', 'Compromise response and queue-driven scaling']. IDs: `U10-SA-*`, `U10-MCQ-*`, `U10-CFG-*`, `U10-REV-*`, `U10-INC-01`, `U10-DES-01`.

- **Unit 11 — Pipeline observability and DORA delivery metrics:** ['DORA metric definitions and anti-gaming', 'Queue/execution duration, flake/retry rate, pipeline SLOs', 'Missing telemetry, correlation IDs, percentiles and coverage']. IDs: `U11-SA-*`, `U11-MCQ-*`, `U11-CFG-*`, `U11-REV-*`, `U11-INC-01`, `U11-DES-01`.


## Scoring and readiness criteria

- **80% or higher:** proceed to the next unit or capstone.
- **60%–79%:** remediate weak objectives and retake missed question types.
- **Below 60%:** repeat the unit learning materials and retake a fresh subset.

Give partial credit for correct diagnosis, safe reasoning, and valid alternatives. Missed conceptual questions → revisit definitions; missed MCQs → explain every distractor; missed reviews → reproduce and validate the fix; missed incidents → write symptom → hypothesis → test → root cause → fix → prevention; missed designs → state assumptions, trade-offs, risks, and acceptance criteria. Mandatory safety constraints include no secret exposure, no untrusted fork code on sensitive persistent runners, no untrusted PR publishing, and no deployment-success claim without rollout evidence.


## Unit 1 — CI/CD architecture and pipeline design principles

**Target lesson:** [`01-ci-cd-architecture-and-pipeline-design-principles.md`](./01-ci-cd-architecture-and-pipeline-design-principles.md)  
**Coverage:** ['CI vs continuous delivery vs deployment', 'DAGs, critical path, fail-fast', 'build once, deploy many, immutable digest']

### Conceptual short-answer


### U01-SA-01 — Short answer

**ID:** `U01-SA-01`  
**Unit / topic:** CI/CD architecture and pipeline design principles  
**Level:** L1  
**Objective tested:** Explain a core concept in CI/CD architecture and pipeline design principles.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

A release waits for a human approval after automated gates. Which delivery model fits?

**Model answer**

Continuous delivery permits an approval before production; continuous deployment normally releases automatically after gates pass.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U01-SA-02 — Short answer

**ID:** `U01-SA-02`  
**Unit / topic:** CI/CD architecture and pipeline design principles  
**Level:** L2  
**Objective tested:** Explain a core concept in CI/CD architecture and pipeline design principles.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Independent lint (2m) and tests (5m) precede a build (3m). What is the critical path?

**Model answer**

The independent jobs fan out; build waits for the slower job, so the minimum is 5 + 3 = 8 minutes.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U01-SA-03 — Short answer

**ID:** `U01-SA-03`  
**Unit / topic:** CI/CD architecture and pipeline design principles  
**Level:** L3  
**Objective tested:** Explain a core concept in CI/CD architecture and pipeline design principles.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What evidence proves staging and production received the same artifact?

**Model answer**

Record and verify the immutable digest from the tested build at each promotion boundary.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### Multiple choice


### U01-MCQ-01 — Multiple choice

**ID:** `U01-MCQ-01`  
**Unit / topic:** CI/CD architecture and pipeline design principles — ['CI vs continuous delivery vs deployment', 'DAGs, critical path, fail-fast', 'build once, deploy many, immutable digest']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For CI vs continuous delivery vs deployment, which choice best satisfies production correctness?

**Options**

- **A.** Option A: Use an unreviewed mutable reference.
- **B.** Option B: Assume a successful workflow proves production outcome.
- **C.** Option C: Continuous delivery permits an approval before production; continuous deployment normally releases automatically after gates pass.
- **D.** Option D: Skip the gate to improve speed.

**Correct answer:** C

**Why the correct option is best:** Continuous delivery permits an approval before production; continuous deployment normally releases automatically after gates pass.

**Distractor analysis**

- **A is incorrect:** Option A: Use an unreviewed mutable reference. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: Assume a successful workflow proves production outcome. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Skip the gate to improve speed. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Continuous delivery permits an approval before production; continuous deployment normally releases automatically after gates pass.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U01-MCQ-02 — Multiple choice

**ID:** `U01-MCQ-02`  
**Unit / topic:** CI/CD architecture and pipeline design principles — ['CI vs continuous delivery vs deployment', 'DAGs, critical path, fail-fast', 'build once, deploy many, immutable digest']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For DAGs, critical path, fail-fast, which control best handles the stated risk?

**Options**

- **A.** Option A: Serialize every job without examining dependencies.
- **B.** Option B: Use a cache as the authoritative release copy.
- **C.** Option C: Treat missing telemetry as a zero value.
- **D.** Option D: The independent jobs fan out; build waits for the slower job, so the minimum is 5 + 3 = 8 minutes.

**Correct answer:** D

**Why the correct option is best:** The independent jobs fan out; build waits for the slower job, so the minimum is 5 + 3 = 8 minutes.

**Distractor analysis**

- **A is incorrect:** Option A: Serialize every job without examining dependencies. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: Use a cache as the authoritative release copy. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Treat missing telemetry as a zero value. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

The independent jobs fan out; build waits for the slower job, so the minimum is 5 + 3 = 8 minutes.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U01-MCQ-03 — Multiple choice

**ID:** `U01-MCQ-03`  
**Unit / topic:** CI/CD architecture and pipeline design principles — ['CI vs continuous delivery vs deployment', 'DAGs, critical path, fail-fast', 'build once, deploy many, immutable digest']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For build once, deploy many, immutable digest, which evidence should be required?

**Options**

- **A.** Option A: Record and verify the immutable digest from the tested build at each promotion boundary.
- **B.** Option B: A mutable label alone.
- **C.** Option C: A successful rerun without first-attempt metrics.
- **D.** Option D: A local simulation as proof of remote enforcement.

**Correct answer:** A

**Why the correct option is best:** Record and verify the immutable digest from the tested build at each promotion boundary.

**Distractor analysis**

- **B is incorrect:** Option B: A mutable label alone. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: A successful rerun without first-attempt metrics. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: A local simulation as proof of remote enforcement. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Record and verify the immutable digest from the tested build at each promotion boundary.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### Configuration interpretation or output reading


### U01-CFG-01 — Configuration/output interpretation

**ID:** `U01-CFG-01`  
**Unit / topic:** CI/CD architecture and pipeline design principles  
**Level:** L2  
**Objective tested:** Interpret configuration and identify missing evidence for CI/CD architecture and pipeline design principles.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret the following pipeline fragment. Identify the missing safety/correctness condition.

```yaml
jobs:
  validate:
    steps: [{run: "pytest"}]
  publish:
    steps: [{run: "publish dist/*"}]
```

**Model answer**

The publish job must depend on successful validation and consume the exact artifact produced by the build. Add explicit dependencies, trusted release conditions, bounded permissions, and immutable artifact identity.

**Reasoning / explanation**

File order does not establish a dependency; verify the actual DAG and failure behavior.

**Common wrong answers or failure modes**

Assuming publish runs after validate because it appears later in YAML.

**Why a tempting wrong answer is wrong**

Use a linter and private test repository; test success, failure, and skipped prerequisite cases.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### U01-CFG-02 — Configuration/output interpretation

**ID:** `U01-CFG-02`  
**Unit / topic:** CI/CD architecture and pipeline design principles  
**Level:** L3  
**Objective tested:** Interpret configuration and identify missing evidence for CI/CD architecture and pipeline design principles.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret this synthetic metric/config output.

```yaml
queue_p95_minutes: 9
execution_p50_minutes: 4
missing_events: 7
reported_failures: 0
```

**Model answer**

Queue delay and execution duration are different signals. Missing events make the failure count incomplete; report coverage/unknown rather than claiming zero failures. Investigate eligible runner capacity and collector errors.

**Reasoning / explanation**

A single aggregate duration cannot identify the bottleneck, and missing observations are not zero.

**Common wrong answers or failure modes**

Assuming the system is healthy because the reported failure count is zero.

**Why a tempting wrong answer is wrong**

Reconcile with raw events and test a synthetic collection gap.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### Pipeline/configuration review


### U01-REV-01 — Configuration review

**ID:** `U01-REV-01`  
**Unit / topic:** CI/CD architecture and pipeline design principles  
**Level:** L3  
**Objective tested:** Find and fix at least three independent defects in CI/CD architecture and pipeline design principles.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three defects and propose a patch.

```yaml
permissions: write-all
cache: dist/
release_tag: latest
run: publish dist/*
```

**Model answer**

Defects: (1) broad permissions; (2) cache used as authoritative artifact handoff; (3) mutable tag without digest; (4) no explicit trusted-ref gate; (5) no checksum/manifest validation. Narrow permissions, publish only from a trusted release context, hand off the exact artifact, record digest/hash, and add a validation gate.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U01-REV-02 — Configuration review

**ID:** `U01-REV-02`  
**Unit / topic:** CI/CD architecture and pipeline design principles  
**Level:** L2  
**Objective tested:** Find and fix at least three independent defects in CI/CD architecture and pipeline design principles.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three independent defects.

```yaml
on: pull_request_target
runs-on: self-hosted
uses: actions/checkout@v4
run: echo $TOKEN
```

**Model answer**

Defects: (1) privileged event context may execute untrusted code; (2) sensitive persistent runner; (3) action not pinned to full SHA; (4) token may be printed/exposed; (5) no least-privilege permissions. Use a restricted PR event on isolated runners, avoid secrets, pin reviewed actions, and scope permissions.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U01-INC-01 — Incident scenario

**ID:** `U01-INC-01`  
**Unit / topic:** CI/CD architecture and pipeline design principles  
**Level:** L4  
**Objective tested:** Diagnose an incident relevant to CI/CD architecture and pipeline design principles and define safe recovery.  
**Estimated time:** 12 min  
**Question type:** Incident scenario

**Question prompt**

A pipeline change coincides with a reliability regression. Available evidence is partial; a retry or green aggregate status may hide the underlying problem. Give symptom → hypotheses → tests → likely cause → mitigation → prevention.

Initial hypotheses: configuration regression, capacity/provider issue, trust-boundary issue, or incomplete telemetry.

**Model answer**

Symptoms: a recent change increased pipeline failures/duration, and the current dashboard is incomplete. Diagnose by inspecting event/runner/job logs, comparing queue vs execution time, reproducing with cache disabled or tests isolated, and checking the relevant dependency/rules/credential boundary. Likely causes remain hypotheses until evidence distinguishes them. Mitigate safely: stop unsafe publishing/deployment, preserve logs, revoke exposed credentials if applicable, and restore only required gates. Prevent with a regression test, explicit ownership, and monitoring. Evidence that would change the conclusion includes a provider-wide incident, a complete independent event log, or reproduction outside CI.

**Reasoning / explanation**

Use the order: contain immediate risk, preserve evidence, discriminate hypotheses, remediate, verify, and record follow-up.

**Common wrong answers or failure modes**

Blind retries, disabling required gates, or changing multiple variables before collecting evidence.

**Why a tempting wrong answer is wrong**

The correlation does not prove the new change caused the incident; evidence must discriminate alternatives.

**Scoring rubric / acceptance criteria**

5 points: symptoms/hypotheses, diagnostic sequence, safe mitigation, prevention, verification, and evidence that could change the conclusion.


### U01-DES-01 — Design with rubric

**ID:** `U01-DES-01`  
**Unit / topic:** CI/CD architecture and pipeline design principles  
**Level:** L4  
**Objective tested:** Design a production-aware CI/CD architecture and pipeline design principles approach under zero-budget constraints.  
**Estimated time:** 18 min  
**Question type:** Design with rubric

**Question prompt**

A slow linear pipeline leaks a publish token and deploys a mutable tag. Redesign it using independent validation, scoped publishing, immutable artifact identity, explicit gates, and a rollback path.

Deliver a diagram or configuration outline, dependency/ownership map, security controls, acceptance criteria, and verification plan. State assumptions and distinguish M02 scope from forward references.

**Model answer**

Design should satisfy: explicit gates; minimal permissions; immutable artifact/evidence where relevant; reproducible validation; failure handling; rollback/recovery; measurable operational outcomes. Compare at least one alternative and explain why it is less suitable under the stated constraints.

**Reasoning / explanation**

A good design documents assumptions, risks, trade-offs, owner, and testable acceptance criteria.

**Common wrong answers or failure modes**

Optimizing speed alone, relying on mutable identifiers, or claiming remote controls are proven by a local simulation.

**Why a tempting wrong answer is wrong**

The best design is not a single rigid topology; it must satisfy mandatory safety and correctness requirements.

**Scoring rubric / acceptance criteria**

10 points: architecture 2, correctness/gates 2, security 2, reliability/rollback 1, measurement 1, trade-offs/clarity 2.


## Unit 2 — GitHub Actions: workflows, runners, reusable workflows

**Target lesson:** [`02-github-actions-workflows-runners-and-reusable-workflows.md`](./02-github-actions-workflows-runners-and-reusable-workflows.md)  
**Coverage:** ['Reusable workflow vs composite action', 'Least-privilege permissions and full-SHA pinning', 'pull_request vs pull_request_target trust boundary']

### Conceptual short-answer


### U02-SA-01 — Short answer

**ID:** `U02-SA-01`  
**Unit / topic:** GitHub Actions: workflows, runners, reusable workflows  
**Level:** L1  
**Objective tested:** Explain a core concept in GitHub Actions: workflows, runners, reusable workflows.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

How does a reusable workflow differ from a composite action?

**Model answer**

Reusable workflows orchestrate jobs; composite actions package steps inside a job.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U02-SA-02 — Short answer

**ID:** `U02-SA-02`  
**Unit / topic:** GitHub Actions: workflows, runners, reusable workflows  
**Level:** L2  
**Objective tested:** Explain a core concept in GitHub Actions: workflows, runners, reusable workflows.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Why pin third-party actions to a full commit SHA?

**Model answer**

A full SHA makes the referenced action revision immutable for that workflow review.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U02-SA-03 — Short answer

**ID:** `U02-SA-03`  
**Unit / topic:** GitHub Actions: workflows, runners, reusable workflows  
**Level:** L3  
**Objective tested:** Explain a core concept in GitHub Actions: workflows, runners, reusable workflows.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What is the danger of running fork code in pull_request_target?

**Model answer**

The base-repository context may have access to privileged resources; untrusted PR code must not be executed there.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### Multiple choice


### U02-MCQ-01 — Multiple choice

**ID:** `U02-MCQ-01`  
**Unit / topic:** GitHub Actions: workflows, runners, reusable workflows — ['Reusable workflow vs composite action', 'Least-privilege permissions and full-SHA pinning', 'pull_request vs pull_request_target trust boundary']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Reusable workflow vs composite action, which choice best satisfies production correctness?

**Options**

- **A.** Option A: Use an unreviewed mutable reference.
- **B.** Option B: Assume a successful workflow proves production outcome.
- **C.** Option C: Skip the gate to improve speed.
- **D.** Option D: Reusable workflows orchestrate jobs; composite actions package steps inside a job.

**Correct answer:** D

**Why the correct option is best:** Reusable workflows orchestrate jobs; composite actions package steps inside a job.

**Distractor analysis**

- **A is incorrect:** Option A: Use an unreviewed mutable reference. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: Assume a successful workflow proves production outcome. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Skip the gate to improve speed. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Reusable workflows orchestrate jobs; composite actions package steps inside a job.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U02-MCQ-02 — Multiple choice

**ID:** `U02-MCQ-02`  
**Unit / topic:** GitHub Actions: workflows, runners, reusable workflows — ['Reusable workflow vs composite action', 'Least-privilege permissions and full-SHA pinning', 'pull_request vs pull_request_target trust boundary']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Least-privilege permissions and full-SHA pinning, which control best handles the stated risk?

**Options**

- **A.** Option A: A full SHA makes the referenced action revision immutable for that workflow review.
- **B.** Option B: Serialize every job without examining dependencies.
- **C.** Option C: Use a cache as the authoritative release copy.
- **D.** Option D: Treat missing telemetry as a zero value.

**Correct answer:** A

**Why the correct option is best:** A full SHA makes the referenced action revision immutable for that workflow review.

**Distractor analysis**

- **B is incorrect:** Option B: Serialize every job without examining dependencies. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Use a cache as the authoritative release copy. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Treat missing telemetry as a zero value. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

A full SHA makes the referenced action revision immutable for that workflow review.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U02-MCQ-03 — Multiple choice

**ID:** `U02-MCQ-03`  
**Unit / topic:** GitHub Actions: workflows, runners, reusable workflows — ['Reusable workflow vs composite action', 'Least-privilege permissions and full-SHA pinning', 'pull_request vs pull_request_target trust boundary']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For pull_request vs pull_request_target trust boundary, which evidence should be required?

**Options**

- **A.** Option A: A mutable label alone.
- **B.** Option B: The base-repository context may have access to privileged resources; untrusted PR code must not be executed there.
- **C.** Option C: A successful rerun without first-attempt metrics.
- **D.** Option D: A local simulation as proof of remote enforcement.

**Correct answer:** B

**Why the correct option is best:** The base-repository context may have access to privileged resources; untrusted PR code must not be executed there.

**Distractor analysis**

- **A is incorrect:** Option A: A mutable label alone. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: A successful rerun without first-attempt metrics. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: A local simulation as proof of remote enforcement. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

The base-repository context may have access to privileged resources; untrusted PR code must not be executed there.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### Configuration interpretation or output reading


### U02-CFG-01 — Configuration/output interpretation

**ID:** `U02-CFG-01`  
**Unit / topic:** GitHub Actions: workflows, runners, reusable workflows  
**Level:** L2  
**Objective tested:** Interpret configuration and identify missing evidence for GitHub Actions: workflows, runners, reusable workflows.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret the following pipeline fragment. Identify the missing safety/correctness condition.

```yaml
jobs:
  validate:
    steps: [{run: "pytest"}]
  publish:
    steps: [{run: "publish dist/*"}]
```

**Model answer**

The publish job must depend on successful validation and consume the exact artifact produced by the build. Add explicit dependencies, trusted release conditions, bounded permissions, and immutable artifact identity.

**Reasoning / explanation**

File order does not establish a dependency; verify the actual DAG and failure behavior.

**Common wrong answers or failure modes**

Assuming publish runs after validate because it appears later in YAML.

**Why a tempting wrong answer is wrong**

Use a linter and private test repository; test success, failure, and skipped prerequisite cases.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### U02-CFG-02 — Configuration/output interpretation

**ID:** `U02-CFG-02`  
**Unit / topic:** GitHub Actions: workflows, runners, reusable workflows  
**Level:** L3  
**Objective tested:** Interpret configuration and identify missing evidence for GitHub Actions: workflows, runners, reusable workflows.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret this synthetic metric/config output.

```yaml
queue_p95_minutes: 9
execution_p50_minutes: 4
missing_events: 7
reported_failures: 0
```

**Model answer**

Queue delay and execution duration are different signals. Missing events make the failure count incomplete; report coverage/unknown rather than claiming zero failures. Investigate eligible runner capacity and collector errors.

**Reasoning / explanation**

A single aggregate duration cannot identify the bottleneck, and missing observations are not zero.

**Common wrong answers or failure modes**

Assuming the system is healthy because the reported failure count is zero.

**Why a tempting wrong answer is wrong**

Reconcile with raw events and test a synthetic collection gap.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### Pipeline/configuration review


### U02-REV-01 — Configuration review

**ID:** `U02-REV-01`  
**Unit / topic:** GitHub Actions: workflows, runners, reusable workflows  
**Level:** L3  
**Objective tested:** Find and fix at least three independent defects in GitHub Actions: workflows, runners, reusable workflows.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three defects and propose a patch.

```yaml
permissions: write-all
cache: dist/
release_tag: latest
run: publish dist/*
```

**Model answer**

Defects: (1) broad permissions; (2) cache used as authoritative artifact handoff; (3) mutable tag without digest; (4) no explicit trusted-ref gate; (5) no checksum/manifest validation. Narrow permissions, publish only from a trusted release context, hand off the exact artifact, record digest/hash, and add a validation gate.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U02-REV-02 — Configuration review

**ID:** `U02-REV-02`  
**Unit / topic:** GitHub Actions: workflows, runners, reusable workflows  
**Level:** L2  
**Objective tested:** Find and fix at least three independent defects in GitHub Actions: workflows, runners, reusable workflows.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three independent defects.

```yaml
on: pull_request_target
runs-on: self-hosted
uses: actions/checkout@v4
run: echo $TOKEN
```

**Model answer**

Defects: (1) privileged event context may execute untrusted code; (2) sensitive persistent runner; (3) action not pinned to full SHA; (4) token may be printed/exposed; (5) no least-privilege permissions. Use a restricted PR event on isolated runners, avoid secrets, pin reviewed actions, and scope permissions.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U02-INC-01 — Incident scenario

**ID:** `U02-INC-01`  
**Unit / topic:** GitHub Actions: workflows, runners, reusable workflows  
**Level:** L4  
**Objective tested:** Diagnose an incident relevant to GitHub Actions: workflows, runners, reusable workflows and define safe recovery.  
**Estimated time:** 12 min  
**Question type:** Incident scenario

**Question prompt**

A pipeline change coincides with a reliability regression. Available evidence is partial; a retry or green aggregate status may hide the underlying problem. Give symptom → hypotheses → tests → likely cause → mitigation → prevention.

Initial hypotheses: configuration regression, capacity/provider issue, trust-boundary issue, or incomplete telemetry.

**Model answer**

Symptoms: a recent change increased pipeline failures/duration, and the current dashboard is incomplete. Diagnose by inspecting event/runner/job logs, comparing queue vs execution time, reproducing with cache disabled or tests isolated, and checking the relevant dependency/rules/credential boundary. Likely causes remain hypotheses until evidence distinguishes them. Mitigate safely: stop unsafe publishing/deployment, preserve logs, revoke exposed credentials if applicable, and restore only required gates. Prevent with a regression test, explicit ownership, and monitoring. Evidence that would change the conclusion includes a provider-wide incident, a complete independent event log, or reproduction outside CI.

**Reasoning / explanation**

Use the order: contain immediate risk, preserve evidence, discriminate hypotheses, remediate, verify, and record follow-up.

**Common wrong answers or failure modes**

Blind retries, disabling required gates, or changing multiple variables before collecting evidence.

**Why a tempting wrong answer is wrong**

The correlation does not prove the new change caused the incident; evidence must discriminate alternatives.

**Scoring rubric / acceptance criteria**

5 points: symptoms/hypotheses, diagnostic sequence, safe mitigation, prevention, verification, and evidence that could change the conclusion.


### U02-DES-01 — Design with rubric

**ID:** `U02-DES-01`  
**Unit / topic:** GitHub Actions: workflows, runners, reusable workflows  
**Level:** L4  
**Objective tested:** Design a production-aware GitHub Actions: workflows, runners, reusable workflows approach under zero-budget constraints.  
**Estimated time:** 18 min  
**Question type:** Design with rubric

**Question prompt**

Review a PR workflow using pull_request_target, write-all permissions, a persistent self-hosted runner, and an unpinned checkout action. Identify trust defects and propose a safe test path.

Deliver a diagram or configuration outline, dependency/ownership map, security controls, acceptance criteria, and verification plan. State assumptions and distinguish M02 scope from forward references.

**Model answer**

Design should satisfy: explicit gates; minimal permissions; immutable artifact/evidence where relevant; reproducible validation; failure handling; rollback/recovery; measurable operational outcomes. Compare at least one alternative and explain why it is less suitable under the stated constraints.

**Reasoning / explanation**

A good design documents assumptions, risks, trade-offs, owner, and testable acceptance criteria.

**Common wrong answers or failure modes**

Optimizing speed alone, relying on mutable identifiers, or claiming remote controls are proven by a local simulation.

**Why a tempting wrong answer is wrong**

The best design is not a single rigid topology; it must satisfy mandatory safety and correctness requirements.

**Scoring rubric / acceptance criteria**

10 points: architecture 2, correctness/gates 2, security 2, reliability/rollback 1, measurement 1, trade-offs/clarity 2.


## Unit 3 — GitLab CI: stages, jobs, templates

**Target lesson:** [`03-gitlab-ci-stages-jobs-and-templates.md`](./03-gitlab-ci-stages-jobs-and-templates.md)  
**Coverage:** ['Artifacts vs cache', 'workflow:rules vs job rules', 'Cross-platform mapping and syntax verification']

### Conceptual short-answer


### U03-SA-01 — Short answer

**ID:** `U03-SA-01`  
**Unit / topic:** GitLab CI: stages, jobs, templates  
**Level:** L1  
**Objective tested:** Explain a core concept in GitLab CI: stages, jobs, templates.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

How do GitLab artifacts differ from cache?

**Model answer**

Artifacts are outputs/evidence; cache is disposable performance state.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U03-SA-02 — Short answer

**ID:** `U03-SA-02`  
**Unit / topic:** GitLab CI: stages, jobs, templates  
**Level:** L2  
**Objective tested:** Explain a core concept in GitLab CI: stages, jobs, templates.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What does workflow:rules control compared with job rules?

**Model answer**

workflow:rules determines whether a pipeline is created; job rules control job inclusion. Verify current behavior [VERIFY].

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U03-SA-03 — Short answer

**ID:** `U03-SA-03`  
**Unit / topic:** GitLab CI: stages, jobs, templates  
**Level:** L3  
**Objective tested:** Explain a core concept in GitLab CI: stages, jobs, templates.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Why is direct GitHub Actions YAML translation unsafe?

**Model answer**

Schemas, conditions, permissions, events, and execution models differ; port intent and test behavior, not just YAML.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### Multiple choice


### U03-MCQ-01 — Multiple choice

**ID:** `U03-MCQ-01`  
**Unit / topic:** GitLab CI: stages, jobs, templates — ['Artifacts vs cache', 'workflow:rules vs job rules', 'Cross-platform mapping and syntax verification']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Artifacts vs cache, which choice best satisfies production correctness?

**Options**

- **A.** Option A: Artifacts are outputs/evidence; cache is disposable performance state.
- **B.** Option B: Use an unreviewed mutable reference.
- **C.** Option C: Assume a successful workflow proves production outcome.
- **D.** Option D: Skip the gate to improve speed.

**Correct answer:** A

**Why the correct option is best:** Artifacts are outputs/evidence; cache is disposable performance state.

**Distractor analysis**

- **B is incorrect:** Option B: Use an unreviewed mutable reference. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Assume a successful workflow proves production outcome. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Skip the gate to improve speed. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Artifacts are outputs/evidence; cache is disposable performance state.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U03-MCQ-02 — Multiple choice

**ID:** `U03-MCQ-02`  
**Unit / topic:** GitLab CI: stages, jobs, templates — ['Artifacts vs cache', 'workflow:rules vs job rules', 'Cross-platform mapping and syntax verification']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For workflow:rules vs job rules, which control best handles the stated risk?

**Options**

- **A.** Option A: Serialize every job without examining dependencies.
- **B.** Option B: workflow:rules determines whether a pipeline is created; job rules control job inclusion. Verify current behavior [VERIFY].
- **C.** Option C: Use a cache as the authoritative release copy.
- **D.** Option D: Treat missing telemetry as a zero value.

**Correct answer:** B

**Why the correct option is best:** workflow:rules determines whether a pipeline is created; job rules control job inclusion. Verify current behavior [VERIFY].

**Distractor analysis**

- **A is incorrect:** Option A: Serialize every job without examining dependencies. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Use a cache as the authoritative release copy. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Treat missing telemetry as a zero value. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

workflow:rules determines whether a pipeline is created; job rules control job inclusion. Verify current behavior [VERIFY].

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U03-MCQ-03 — Multiple choice

**ID:** `U03-MCQ-03`  
**Unit / topic:** GitLab CI: stages, jobs, templates — ['Artifacts vs cache', 'workflow:rules vs job rules', 'Cross-platform mapping and syntax verification']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Cross-platform mapping and syntax verification, which evidence should be required?

**Options**

- **A.** Option A: A mutable label alone.
- **B.** Option B: A successful rerun without first-attempt metrics.
- **C.** Option C: Schemas, conditions, permissions, events, and execution models differ; port intent and test behavior, not just YAML.
- **D.** Option D: A local simulation as proof of remote enforcement.

**Correct answer:** C

**Why the correct option is best:** Schemas, conditions, permissions, events, and execution models differ; port intent and test behavior, not just YAML.

**Distractor analysis**

- **A is incorrect:** Option A: A mutable label alone. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: A successful rerun without first-attempt metrics. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: A local simulation as proof of remote enforcement. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Schemas, conditions, permissions, events, and execution models differ; port intent and test behavior, not just YAML.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### Configuration interpretation or output reading


### U03-CFG-01 — Configuration/output interpretation

**ID:** `U03-CFG-01`  
**Unit / topic:** GitLab CI: stages, jobs, templates  
**Level:** L2  
**Objective tested:** Interpret configuration and identify missing evidence for GitLab CI: stages, jobs, templates.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret the following pipeline fragment. Identify the missing safety/correctness condition.

```yaml
jobs:
  validate:
    steps: [{run: "pytest"}]
  publish:
    steps: [{run: "publish dist/*"}]
```

**Model answer**

The publish job must depend on successful validation and consume the exact artifact produced by the build. Add explicit dependencies, trusted release conditions, bounded permissions, and immutable artifact identity.

**Reasoning / explanation**

File order does not establish a dependency; verify the actual DAG and failure behavior.

**Common wrong answers or failure modes**

Assuming publish runs after validate because it appears later in YAML.

**Why a tempting wrong answer is wrong**

Use a linter and private test repository; test success, failure, and skipped prerequisite cases.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### U03-CFG-02 — Configuration/output interpretation

**ID:** `U03-CFG-02`  
**Unit / topic:** GitLab CI: stages, jobs, templates  
**Level:** L3  
**Objective tested:** Interpret configuration and identify missing evidence for GitLab CI: stages, jobs, templates.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret this synthetic metric/config output.

```yaml
queue_p95_minutes: 9
execution_p50_minutes: 4
missing_events: 7
reported_failures: 0
```

**Model answer**

Queue delay and execution duration are different signals. Missing events make the failure count incomplete; report coverage/unknown rather than claiming zero failures. Investigate eligible runner capacity and collector errors.

**Reasoning / explanation**

A single aggregate duration cannot identify the bottleneck, and missing observations are not zero.

**Common wrong answers or failure modes**

Assuming the system is healthy because the reported failure count is zero.

**Why a tempting wrong answer is wrong**

Reconcile with raw events and test a synthetic collection gap.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### Pipeline/configuration review


### U03-REV-01 — Configuration review

**ID:** `U03-REV-01`  
**Unit / topic:** GitLab CI: stages, jobs, templates  
**Level:** L3  
**Objective tested:** Find and fix at least three independent defects in GitLab CI: stages, jobs, templates.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three defects and propose a patch.

```yaml
permissions: write-all
cache: dist/
release_tag: latest
run: publish dist/*
```

**Model answer**

Defects: (1) broad permissions; (2) cache used as authoritative artifact handoff; (3) mutable tag without digest; (4) no explicit trusted-ref gate; (5) no checksum/manifest validation. Narrow permissions, publish only from a trusted release context, hand off the exact artifact, record digest/hash, and add a validation gate.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U03-REV-02 — Configuration review

**ID:** `U03-REV-02`  
**Unit / topic:** GitLab CI: stages, jobs, templates  
**Level:** L2  
**Objective tested:** Find and fix at least three independent defects in GitLab CI: stages, jobs, templates.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three independent defects.

```yaml
on: pull_request_target
runs-on: self-hosted
uses: actions/checkout@v4
run: echo $TOKEN
```

**Model answer**

Defects: (1) privileged event context may execute untrusted code; (2) sensitive persistent runner; (3) action not pinned to full SHA; (4) token may be printed/exposed; (5) no least-privilege permissions. Use a restricted PR event on isolated runners, avoid secrets, pin reviewed actions, and scope permissions.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U03-INC-01 — Incident scenario

**ID:** `U03-INC-01`  
**Unit / topic:** GitLab CI: stages, jobs, templates  
**Level:** L4  
**Objective tested:** Diagnose an incident relevant to GitLab CI: stages, jobs, templates and define safe recovery.  
**Estimated time:** 12 min  
**Question type:** Incident scenario

**Question prompt**

A pipeline change coincides with a reliability regression. Available evidence is partial; a retry or green aggregate status may hide the underlying problem. Give symptom → hypotheses → tests → likely cause → mitigation → prevention.

Initial hypotheses: configuration regression, capacity/provider issue, trust-boundary issue, or incomplete telemetry.

**Model answer**

Symptoms: a recent change increased pipeline failures/duration, and the current dashboard is incomplete. Diagnose by inspecting event/runner/job logs, comparing queue vs execution time, reproducing with cache disabled or tests isolated, and checking the relevant dependency/rules/credential boundary. Likely causes remain hypotheses until evidence distinguishes them. Mitigate safely: stop unsafe publishing/deployment, preserve logs, revoke exposed credentials if applicable, and restore only required gates. Prevent with a regression test, explicit ownership, and monitoring. Evidence that would change the conclusion includes a provider-wide incident, a complete independent event log, or reproduction outside CI.

**Reasoning / explanation**

Use the order: contain immediate risk, preserve evidence, discriminate hypotheses, remediate, verify, and record follow-up.

**Common wrong answers or failure modes**

Blind retries, disabling required gates, or changing multiple variables before collecting evidence.

**Why a tempting wrong answer is wrong**

The correlation does not prove the new change caused the incident; evidence must discriminate alternatives.

**Scoring rubric / acceptance criteria**

5 points: symptoms/hypotheses, diagnostic sequence, safe mitigation, prevention, verification, and evidence that could change the conclusion.


### U03-DES-01 — Design with rubric

**ID:** `U03-DES-01`  
**Unit / topic:** GitLab CI: stages, jobs, templates  
**Level:** L4  
**Objective tested:** Design a production-aware GitLab CI: stages, jobs, templates approach under zero-budget constraints.  
**Estimated time:** 18 min  
**Question type:** Design with rubric

**Question prompt**

Two GitLab pipelines run for one merge request. Diagnose event sources and rules, then propose an event matrix and a safe correction.

Deliver a diagram or configuration outline, dependency/ownership map, security controls, acceptance criteria, and verification plan. State assumptions and distinguish M02 scope from forward references.

**Model answer**

Design should satisfy: explicit gates; minimal permissions; immutable artifact/evidence where relevant; reproducible validation; failure handling; rollback/recovery; measurable operational outcomes. Compare at least one alternative and explain why it is less suitable under the stated constraints.

**Reasoning / explanation**

A good design documents assumptions, risks, trade-offs, owner, and testable acceptance criteria.

**Common wrong answers or failure modes**

Optimizing speed alone, relying on mutable identifiers, or claiming remote controls are proven by a local simulation.

**Why a tempting wrong answer is wrong**

The best design is not a single rigid topology; it must satisfy mandatory safety and correctness requirements.

**Scoring rubric / acceptance criteria**

10 points: architecture 2, correctness/gates 2, security 2, reliability/rollback 1, measurement 1, trade-offs/clarity 2.


## Unit 4 — Build caching, parallelism, and pipeline speed

**Target lesson:** [`04-build-caching-parallelism-and-pipeline-speed.md`](./04-build-caching-parallelism-and-pipeline-speed.md)  
**Coverage:** ['Cache key by runtime and lockfile', 'Queue vs execution time; critical path', 'Cold/warm benchmarking and cache trust']

### Conceptual short-answer


### U04-SA-01 — Short answer

**ID:** `U04-SA-01`  
**Unit / topic:** Build caching, parallelism, and pipeline speed  
**Level:** L1  
**Objective tested:** Explain a core concept in Build caching, parallelism, and pipeline speed.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Why must a cold build succeed without cache?

**Model answer**

Cache is an optimization, never a correctness dependency.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U04-SA-02 — Short answer

**ID:** `U04-SA-02`  
**Unit / topic:** Build caching, parallelism, and pipeline speed  
**Level:** L2  
**Objective tested:** Explain a core concept in Build caching, parallelism, and pipeline speed.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Why can more parallel jobs increase wall-clock time?

**Model answer**

Setup, queue contention, downloads, memory pressure, and aggregation can outweigh parallelism.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U04-SA-03 — Short answer

**ID:** `U04-SA-03`  
**Unit / topic:** Build caching, parallelism, and pipeline speed  
**Level:** L3  
**Objective tested:** Explain a core concept in Build caching, parallelism, and pipeline speed.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

How should a cache benchmark be designed?

**Model answer**

Repeat comparable cold/warm/partial-change runs; report median/p95 and separate queue from execution time.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### Multiple choice


### U04-MCQ-01 — Multiple choice

**ID:** `U04-MCQ-01`  
**Unit / topic:** Build caching, parallelism, and pipeline speed — ['Cache key by runtime and lockfile', 'Queue vs execution time; critical path', 'Cold/warm benchmarking and cache trust']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Cache key by runtime and lockfile, which choice best satisfies production correctness?

**Options**

- **A.** Option A: Use an unreviewed mutable reference.
- **B.** Option B: Cache is an optimization, never a correctness dependency.
- **C.** Option C: Assume a successful workflow proves production outcome.
- **D.** Option D: Skip the gate to improve speed.

**Correct answer:** B

**Why the correct option is best:** Cache is an optimization, never a correctness dependency.

**Distractor analysis**

- **A is incorrect:** Option A: Use an unreviewed mutable reference. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Assume a successful workflow proves production outcome. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Skip the gate to improve speed. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Cache is an optimization, never a correctness dependency.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U04-MCQ-02 — Multiple choice

**ID:** `U04-MCQ-02`  
**Unit / topic:** Build caching, parallelism, and pipeline speed — ['Cache key by runtime and lockfile', 'Queue vs execution time; critical path', 'Cold/warm benchmarking and cache trust']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Queue vs execution time; critical path, which control best handles the stated risk?

**Options**

- **A.** Option A: Serialize every job without examining dependencies.
- **B.** Option B: Use a cache as the authoritative release copy.
- **C.** Option C: Setup, queue contention, downloads, memory pressure, and aggregation can outweigh parallelism.
- **D.** Option D: Treat missing telemetry as a zero value.

**Correct answer:** C

**Why the correct option is best:** Setup, queue contention, downloads, memory pressure, and aggregation can outweigh parallelism.

**Distractor analysis**

- **A is incorrect:** Option A: Serialize every job without examining dependencies. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: Use a cache as the authoritative release copy. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Treat missing telemetry as a zero value. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Setup, queue contention, downloads, memory pressure, and aggregation can outweigh parallelism.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U04-MCQ-03 — Multiple choice

**ID:** `U04-MCQ-03`  
**Unit / topic:** Build caching, parallelism, and pipeline speed — ['Cache key by runtime and lockfile', 'Queue vs execution time; critical path', 'Cold/warm benchmarking and cache trust']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Cold/warm benchmarking and cache trust, which evidence should be required?

**Options**

- **A.** Option A: A mutable label alone.
- **B.** Option B: A successful rerun without first-attempt metrics.
- **C.** Option C: A local simulation as proof of remote enforcement.
- **D.** Option D: Repeat comparable cold/warm/partial-change runs; report median/p95 and separate queue from execution time.

**Correct answer:** D

**Why the correct option is best:** Repeat comparable cold/warm/partial-change runs; report median/p95 and separate queue from execution time.

**Distractor analysis**

- **A is incorrect:** Option A: A mutable label alone. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: A successful rerun without first-attempt metrics. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: A local simulation as proof of remote enforcement. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Repeat comparable cold/warm/partial-change runs; report median/p95 and separate queue from execution time.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### Configuration interpretation or output reading


### U04-CFG-01 — Configuration/output interpretation

**ID:** `U04-CFG-01`  
**Unit / topic:** Build caching, parallelism, and pipeline speed  
**Level:** L2  
**Objective tested:** Interpret configuration and identify missing evidence for Build caching, parallelism, and pipeline speed.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret the following pipeline fragment. Identify the missing safety/correctness condition.

```yaml
jobs:
  validate:
    steps: [{run: "pytest"}]
  publish:
    steps: [{run: "publish dist/*"}]
```

**Model answer**

The publish job must depend on successful validation and consume the exact artifact produced by the build. Add explicit dependencies, trusted release conditions, bounded permissions, and immutable artifact identity.

**Reasoning / explanation**

File order does not establish a dependency; verify the actual DAG and failure behavior.

**Common wrong answers or failure modes**

Assuming publish runs after validate because it appears later in YAML.

**Why a tempting wrong answer is wrong**

Use a linter and private test repository; test success, failure, and skipped prerequisite cases.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### U04-CFG-02 — Configuration/output interpretation

**ID:** `U04-CFG-02`  
**Unit / topic:** Build caching, parallelism, and pipeline speed  
**Level:** L3  
**Objective tested:** Interpret configuration and identify missing evidence for Build caching, parallelism, and pipeline speed.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret this synthetic metric/config output.

```yaml
queue_p95_minutes: 9
execution_p50_minutes: 4
missing_events: 7
reported_failures: 0
```

**Model answer**

Queue delay and execution duration are different signals. Missing events make the failure count incomplete; report coverage/unknown rather than claiming zero failures. Investigate eligible runner capacity and collector errors.

**Reasoning / explanation**

A single aggregate duration cannot identify the bottleneck, and missing observations are not zero.

**Common wrong answers or failure modes**

Assuming the system is healthy because the reported failure count is zero.

**Why a tempting wrong answer is wrong**

Reconcile with raw events and test a synthetic collection gap.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### Pipeline/configuration review


### U04-REV-01 — Configuration review

**ID:** `U04-REV-01`  
**Unit / topic:** Build caching, parallelism, and pipeline speed  
**Level:** L3  
**Objective tested:** Find and fix at least three independent defects in Build caching, parallelism, and pipeline speed.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three defects and propose a patch.

```yaml
permissions: write-all
cache: dist/
release_tag: latest
run: publish dist/*
```

**Model answer**

Defects: (1) broad permissions; (2) cache used as authoritative artifact handoff; (3) mutable tag without digest; (4) no explicit trusted-ref gate; (5) no checksum/manifest validation. Narrow permissions, publish only from a trusted release context, hand off the exact artifact, record digest/hash, and add a validation gate.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U04-REV-02 — Configuration review

**ID:** `U04-REV-02`  
**Unit / topic:** Build caching, parallelism, and pipeline speed  
**Level:** L2  
**Objective tested:** Find and fix at least three independent defects in Build caching, parallelism, and pipeline speed.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three independent defects.

```yaml
on: pull_request_target
runs-on: self-hosted
uses: actions/checkout@v4
run: echo $TOKEN
```

**Model answer**

Defects: (1) privileged event context may execute untrusted code; (2) sensitive persistent runner; (3) action not pinned to full SHA; (4) token may be printed/exposed; (5) no least-privilege permissions. Use a restricted PR event on isolated runners, avoid secrets, pin reviewed actions, and scope permissions.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U04-INC-01 — Incident scenario

**ID:** `U04-INC-01`  
**Unit / topic:** Build caching, parallelism, and pipeline speed  
**Level:** L4  
**Objective tested:** Diagnose an incident relevant to Build caching, parallelism, and pipeline speed and define safe recovery.  
**Estimated time:** 12 min  
**Question type:** Incident scenario

**Question prompt**

A pipeline change coincides with a reliability regression. Available evidence is partial; a retry or green aggregate status may hide the underlying problem. Give symptom → hypotheses → tests → likely cause → mitigation → prevention.

Initial hypotheses: configuration regression, capacity/provider issue, trust-boundary issue, or incomplete telemetry.

**Model answer**

Symptoms: a recent change increased pipeline failures/duration, and the current dashboard is incomplete. Diagnose by inspecting event/runner/job logs, comparing queue vs execution time, reproducing with cache disabled or tests isolated, and checking the relevant dependency/rules/credential boundary. Likely causes remain hypotheses until evidence distinguishes them. Mitigate safely: stop unsafe publishing/deployment, preserve logs, revoke exposed credentials if applicable, and restore only required gates. Prevent with a regression test, explicit ownership, and monitoring. Evidence that would change the conclusion includes a provider-wide incident, a complete independent event log, or reproduction outside CI.

**Reasoning / explanation**

Use the order: contain immediate risk, preserve evidence, discriminate hypotheses, remediate, verify, and record follow-up.

**Common wrong answers or failure modes**

Blind retries, disabling required gates, or changing multiple variables before collecting evidence.

**Why a tempting wrong answer is wrong**

The correlation does not prove the new change caused the incident; evidence must discriminate alternatives.

**Scoring rubric / acceptance criteria**

5 points: symptoms/hypotheses, diagnostic sequence, safe mitigation, prevention, verification, and evidence that could change the conclusion.


### U04-DES-01 — Design with rubric

**ID:** `U04-DES-01`  
**Unit / topic:** Build caching, parallelism, and pipeline speed  
**Level:** L4  
**Objective tested:** Design a production-aware Build caching, parallelism, and pipeline speed approach under zero-budget constraints.  
**Estimated time:** 18 min  
**Question type:** Design with rubric

**Question prompt**

Warm builds are fast but cold builds fail on an undeclared dependency. Diagnose and fix without making cache authoritative.

Deliver a diagram or configuration outline, dependency/ownership map, security controls, acceptance criteria, and verification plan. State assumptions and distinguish M02 scope from forward references.

**Model answer**

Design should satisfy: explicit gates; minimal permissions; immutable artifact/evidence where relevant; reproducible validation; failure handling; rollback/recovery; measurable operational outcomes. Compare at least one alternative and explain why it is less suitable under the stated constraints.

**Reasoning / explanation**

A good design documents assumptions, risks, trade-offs, owner, and testable acceptance criteria.

**Common wrong answers or failure modes**

Optimizing speed alone, relying on mutable identifiers, or claiming remote controls are proven by a local simulation.

**Why a tempting wrong answer is wrong**

The best design is not a single rigid topology; it must satisfy mandatory safety and correctness requirements.

**Scoring rubric / acceptance criteria**

10 points: architecture 2, correctness/gates 2, security 2, reliability/rollback 1, measurement 1, trade-offs/clarity 2.


## Unit 5 — Monorepo and path-based pipelines

**Target lesson:** [`05-monorepo-and-path-based-pipelines.md`](./05-monorepo-and-path-based-pipelines.md)  
**Coverage:** ['Shared-library dependency fan-out', 'Stable required aggregate gate', 'Merge base, shallow clones, force pushes and merge queues']

### Conceptual short-answer


### U05-SA-01 — Short answer

**ID:** `U05-SA-01`  
**Unit / topic:** Monorepo and path-based pipelines  
**Level:** L1  
**Objective tested:** Explain a core concept in Monorepo and path-based pipelines.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Why must shared-library changes trigger dependent components?

**Model answer**

Path policy must model downstream dependencies, not only directly edited directories.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U05-SA-02 — Short answer

**ID:** `U05-SA-02`  
**Unit / topic:** Monorepo and path-based pipelines  
**Level:** L2  
**Objective tested:** Explain a core concept in Monorepo and path-based pipelines.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What is the required-check hazard of path-filtered workflows?

**Model answer**

A skipped workflow may leave a required status absent/pending; use a stable aggregate gate and verify platform behavior [VERIFY].

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U05-SA-03 — Short answer

**ID:** `U05-SA-03`  
**Unit / topic:** Monorepo and path-based pipelines  
**Level:** L3  
**Objective tested:** Explain a core concept in Monorepo and path-based pipelines.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

How can shallow clones break changed-path classification?

**Model answer**

The target commit or merge base may be missing; fetch sufficient history and compute the intended base.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### Multiple choice


### U05-MCQ-01 — Multiple choice

**ID:** `U05-MCQ-01`  
**Unit / topic:** Monorepo and path-based pipelines — ['Shared-library dependency fan-out', 'Stable required aggregate gate', 'Merge base, shallow clones, force pushes and merge queues']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Shared-library dependency fan-out, which choice best satisfies production correctness?

**Options**

- **A.** Option A: Use an unreviewed mutable reference.
- **B.** Option B: Assume a successful workflow proves production outcome.
- **C.** Option C: Path policy must model downstream dependencies, not only directly edited directories.
- **D.** Option D: Skip the gate to improve speed.

**Correct answer:** C

**Why the correct option is best:** Path policy must model downstream dependencies, not only directly edited directories.

**Distractor analysis**

- **A is incorrect:** Option A: Use an unreviewed mutable reference. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: Assume a successful workflow proves production outcome. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Skip the gate to improve speed. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Path policy must model downstream dependencies, not only directly edited directories.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U05-MCQ-02 — Multiple choice

**ID:** `U05-MCQ-02`  
**Unit / topic:** Monorepo and path-based pipelines — ['Shared-library dependency fan-out', 'Stable required aggregate gate', 'Merge base, shallow clones, force pushes and merge queues']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Stable required aggregate gate, which control best handles the stated risk?

**Options**

- **A.** Option A: Serialize every job without examining dependencies.
- **B.** Option B: Use a cache as the authoritative release copy.
- **C.** Option C: Treat missing telemetry as a zero value.
- **D.** Option D: A skipped workflow may leave a required status absent/pending; use a stable aggregate gate and verify platform behavior [VERIFY].

**Correct answer:** D

**Why the correct option is best:** A skipped workflow may leave a required status absent/pending; use a stable aggregate gate and verify platform behavior [VERIFY].

**Distractor analysis**

- **A is incorrect:** Option A: Serialize every job without examining dependencies. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: Use a cache as the authoritative release copy. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Treat missing telemetry as a zero value. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

A skipped workflow may leave a required status absent/pending; use a stable aggregate gate and verify platform behavior [VERIFY].

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U05-MCQ-03 — Multiple choice

**ID:** `U05-MCQ-03`  
**Unit / topic:** Monorepo and path-based pipelines — ['Shared-library dependency fan-out', 'Stable required aggregate gate', 'Merge base, shallow clones, force pushes and merge queues']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Merge base, shallow clones, force pushes and merge queues, which evidence should be required?

**Options**

- **A.** Option A: The target commit or merge base may be missing; fetch sufficient history and compute the intended base.
- **B.** Option B: A mutable label alone.
- **C.** Option C: A successful rerun without first-attempt metrics.
- **D.** Option D: A local simulation as proof of remote enforcement.

**Correct answer:** A

**Why the correct option is best:** The target commit or merge base may be missing; fetch sufficient history and compute the intended base.

**Distractor analysis**

- **B is incorrect:** Option B: A mutable label alone. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: A successful rerun without first-attempt metrics. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: A local simulation as proof of remote enforcement. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

The target commit or merge base may be missing; fetch sufficient history and compute the intended base.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### Configuration interpretation or output reading


### U05-CFG-01 — Configuration/output interpretation

**ID:** `U05-CFG-01`  
**Unit / topic:** Monorepo and path-based pipelines  
**Level:** L2  
**Objective tested:** Interpret configuration and identify missing evidence for Monorepo and path-based pipelines.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret the following pipeline fragment. Identify the missing safety/correctness condition.

```yaml
jobs:
  validate:
    steps: [{run: "pytest"}]
  publish:
    steps: [{run: "publish dist/*"}]
```

**Model answer**

The publish job must depend on successful validation and consume the exact artifact produced by the build. Add explicit dependencies, trusted release conditions, bounded permissions, and immutable artifact identity.

**Reasoning / explanation**

File order does not establish a dependency; verify the actual DAG and failure behavior.

**Common wrong answers or failure modes**

Assuming publish runs after validate because it appears later in YAML.

**Why a tempting wrong answer is wrong**

Use a linter and private test repository; test success, failure, and skipped prerequisite cases.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### U05-CFG-02 — Configuration/output interpretation

**ID:** `U05-CFG-02`  
**Unit / topic:** Monorepo and path-based pipelines  
**Level:** L3  
**Objective tested:** Interpret configuration and identify missing evidence for Monorepo and path-based pipelines.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret this synthetic metric/config output.

```yaml
queue_p95_minutes: 9
execution_p50_minutes: 4
missing_events: 7
reported_failures: 0
```

**Model answer**

Queue delay and execution duration are different signals. Missing events make the failure count incomplete; report coverage/unknown rather than claiming zero failures. Investigate eligible runner capacity and collector errors.

**Reasoning / explanation**

A single aggregate duration cannot identify the bottleneck, and missing observations are not zero.

**Common wrong answers or failure modes**

Assuming the system is healthy because the reported failure count is zero.

**Why a tempting wrong answer is wrong**

Reconcile with raw events and test a synthetic collection gap.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### Pipeline/configuration review


### U05-REV-01 — Configuration review

**ID:** `U05-REV-01`  
**Unit / topic:** Monorepo and path-based pipelines  
**Level:** L3  
**Objective tested:** Find and fix at least three independent defects in Monorepo and path-based pipelines.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three defects and propose a patch.

```yaml
permissions: write-all
cache: dist/
release_tag: latest
run: publish dist/*
```

**Model answer**

Defects: (1) broad permissions; (2) cache used as authoritative artifact handoff; (3) mutable tag without digest; (4) no explicit trusted-ref gate; (5) no checksum/manifest validation. Narrow permissions, publish only from a trusted release context, hand off the exact artifact, record digest/hash, and add a validation gate.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U05-REV-02 — Configuration review

**ID:** `U05-REV-02`  
**Unit / topic:** Monorepo and path-based pipelines  
**Level:** L2  
**Objective tested:** Find and fix at least three independent defects in Monorepo and path-based pipelines.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three independent defects.

```yaml
on: pull_request_target
runs-on: self-hosted
uses: actions/checkout@v4
run: echo $TOKEN
```

**Model answer**

Defects: (1) privileged event context may execute untrusted code; (2) sensitive persistent runner; (3) action not pinned to full SHA; (4) token may be printed/exposed; (5) no least-privilege permissions. Use a restricted PR event on isolated runners, avoid secrets, pin reviewed actions, and scope permissions.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U05-INC-01 — Incident scenario

**ID:** `U05-INC-01`  
**Unit / topic:** Monorepo and path-based pipelines  
**Level:** L4  
**Objective tested:** Diagnose an incident relevant to Monorepo and path-based pipelines and define safe recovery.  
**Estimated time:** 12 min  
**Question type:** Incident scenario

**Question prompt**

A pipeline change coincides with a reliability regression. Available evidence is partial; a retry or green aggregate status may hide the underlying problem. Give symptom → hypotheses → tests → likely cause → mitigation → prevention.

Initial hypotheses: configuration regression, capacity/provider issue, trust-boundary issue, or incomplete telemetry.

**Model answer**

Symptoms: a recent change increased pipeline failures/duration, and the current dashboard is incomplete. Diagnose by inspecting event/runner/job logs, comparing queue vs execution time, reproducing with cache disabled or tests isolated, and checking the relevant dependency/rules/credential boundary. Likely causes remain hypotheses until evidence distinguishes them. Mitigate safely: stop unsafe publishing/deployment, preserve logs, revoke exposed credentials if applicable, and restore only required gates. Prevent with a regression test, explicit ownership, and monitoring. Evidence that would change the conclusion includes a provider-wide incident, a complete independent event log, or reproduction outside CI.

**Reasoning / explanation**

Use the order: contain immediate risk, preserve evidence, discriminate hypotheses, remediate, verify, and record follow-up.

**Common wrong answers or failure modes**

Blind retries, disabling required gates, or changing multiple variables before collecting evidence.

**Why a tempting wrong answer is wrong**

The correlation does not prove the new change caused the incident; evidence must discriminate alternatives.

**Scoring rubric / acceptance criteria**

5 points: symptoms/hypotheses, diagnostic sequence, safe mitigation, prevention, verification, and evidence that could change the conclusion.


### U05-DES-01 — Design with rubric

**ID:** `U05-DES-01`  
**Unit / topic:** Monorepo and path-based pipelines  
**Level:** L4  
**Objective tested:** Design a production-aware Monorepo and path-based pipelines approach under zero-budget constraints.  
**Estimated time:** 18 min  
**Question type:** Design with rubric

**Question prompt**

A docs-only PR is blocked by a pending required check. Design a policy that skips unnecessary component tests but never loses the aggregate status.

Deliver a diagram or configuration outline, dependency/ownership map, security controls, acceptance criteria, and verification plan. State assumptions and distinguish M02 scope from forward references.

**Model answer**

Design should satisfy: explicit gates; minimal permissions; immutable artifact/evidence where relevant; reproducible validation; failure handling; rollback/recovery; measurable operational outcomes. Compare at least one alternative and explain why it is less suitable under the stated constraints.

**Reasoning / explanation**

A good design documents assumptions, risks, trade-offs, owner, and testable acceptance criteria.

**Common wrong answers or failure modes**

Optimizing speed alone, relying on mutable identifiers, or claiming remote controls are proven by a local simulation.

**Why a tempting wrong answer is wrong**

The best design is not a single rigid topology; it must satisfy mandatory safety and correctness requirements.

**Scoring rubric / acceptance criteria**

10 points: architecture 2, correctness/gates 2, security 2, reliability/rollback 1, measurement 1, trade-offs/clarity 2.


## Unit 6 — Test stages, quality gates, flaky-test management

**Target lesson:** [`06-test-stages-quality-gates-and-flaky-test-management.md`](./06-test-stages-quality-gates-and-flaky-test-management.md)  
**Coverage:** ['pytest/JUnit/coverage gates', 'Data-contract and ML evaluation gates', 'Flake rate, quarantine owner/expiry, retry limits']

### Conceptual short-answer


### U06-SA-01 — Short answer

**ID:** `U06-SA-01`  
**Unit / topic:** Test stages, quality gates, flaky-test management  
**Level:** L1  
**Objective tested:** Explain a core concept in Test stages, quality gates, flaky-test management.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Why is retry not a permanent fix for a flaky test?

**Model answer**

Retries can hide order dependence, shared state, races, or resource contention; track first-attempt failures and fix root causes.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U06-SA-02 — Short answer

**ID:** `U06-SA-02`  
**Unit / topic:** Test stages, quality gates, flaky-test management  
**Level:** L2  
**Objective tested:** Explain a core concept in Test stages, quality gates, flaky-test management.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What does coverage fail to prove?

**Model answer**

Coverage measures execution, not whether assertions detect defects.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U06-SA-03 — Short answer

**ID:** `U06-SA-03`  
**Unit / topic:** Test stages, quality gates, flaky-test management  
**Level:** L3  
**Objective tested:** Explain a core concept in Test stages, quality gates, flaky-test management.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What evidence makes an ML metric gate trustworthy?

**Model answer**

Use versioned evaluation data, explicit metric/threshold, sample-size awareness, controlled configuration, and uncertainty analysis.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### Multiple choice


### U06-MCQ-01 — Multiple choice

**ID:** `U06-MCQ-01`  
**Unit / topic:** Test stages, quality gates, flaky-test management — ['pytest/JUnit/coverage gates', 'Data-contract and ML evaluation gates', 'Flake rate, quarantine owner/expiry, retry limits']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For pytest/JUnit/coverage gates, which choice best satisfies production correctness?

**Options**

- **A.** Option A: Use an unreviewed mutable reference.
- **B.** Option B: Assume a successful workflow proves production outcome.
- **C.** Option C: Skip the gate to improve speed.
- **D.** Option D: Retries can hide order dependence, shared state, races, or resource contention; track first-attempt failures and fix root causes.

**Correct answer:** D

**Why the correct option is best:** Retries can hide order dependence, shared state, races, or resource contention; track first-attempt failures and fix root causes.

**Distractor analysis**

- **A is incorrect:** Option A: Use an unreviewed mutable reference. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: Assume a successful workflow proves production outcome. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Skip the gate to improve speed. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Retries can hide order dependence, shared state, races, or resource contention; track first-attempt failures and fix root causes.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U06-MCQ-02 — Multiple choice

**ID:** `U06-MCQ-02`  
**Unit / topic:** Test stages, quality gates, flaky-test management — ['pytest/JUnit/coverage gates', 'Data-contract and ML evaluation gates', 'Flake rate, quarantine owner/expiry, retry limits']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Data-contract and ML evaluation gates, which control best handles the stated risk?

**Options**

- **A.** Option A: Coverage measures execution, not whether assertions detect defects.
- **B.** Option B: Serialize every job without examining dependencies.
- **C.** Option C: Use a cache as the authoritative release copy.
- **D.** Option D: Treat missing telemetry as a zero value.

**Correct answer:** A

**Why the correct option is best:** Coverage measures execution, not whether assertions detect defects.

**Distractor analysis**

- **B is incorrect:** Option B: Serialize every job without examining dependencies. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Use a cache as the authoritative release copy. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Treat missing telemetry as a zero value. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Coverage measures execution, not whether assertions detect defects.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U06-MCQ-03 — Multiple choice

**ID:** `U06-MCQ-03`  
**Unit / topic:** Test stages, quality gates, flaky-test management — ['pytest/JUnit/coverage gates', 'Data-contract and ML evaluation gates', 'Flake rate, quarantine owner/expiry, retry limits']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Flake rate, quarantine owner/expiry, retry limits, which evidence should be required?

**Options**

- **A.** Option A: A mutable label alone.
- **B.** Option B: Use versioned evaluation data, explicit metric/threshold, sample-size awareness, controlled configuration, and uncertainty analysis.
- **C.** Option C: A successful rerun without first-attempt metrics.
- **D.** Option D: A local simulation as proof of remote enforcement.

**Correct answer:** B

**Why the correct option is best:** Use versioned evaluation data, explicit metric/threshold, sample-size awareness, controlled configuration, and uncertainty analysis.

**Distractor analysis**

- **A is incorrect:** Option A: A mutable label alone. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: A successful rerun without first-attempt metrics. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: A local simulation as proof of remote enforcement. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Use versioned evaluation data, explicit metric/threshold, sample-size awareness, controlled configuration, and uncertainty analysis.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### Configuration interpretation or output reading


### U06-CFG-01 — Configuration/output interpretation

**ID:** `U06-CFG-01`  
**Unit / topic:** Test stages, quality gates, flaky-test management  
**Level:** L2  
**Objective tested:** Interpret configuration and identify missing evidence for Test stages, quality gates, flaky-test management.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret the following pipeline fragment. Identify the missing safety/correctness condition.

```yaml
jobs:
  validate:
    steps: [{run: "pytest"}]
  publish:
    steps: [{run: "publish dist/*"}]
```

**Model answer**

The publish job must depend on successful validation and consume the exact artifact produced by the build. Add explicit dependencies, trusted release conditions, bounded permissions, and immutable artifact identity.

**Reasoning / explanation**

File order does not establish a dependency; verify the actual DAG and failure behavior.

**Common wrong answers or failure modes**

Assuming publish runs after validate because it appears later in YAML.

**Why a tempting wrong answer is wrong**

Use a linter and private test repository; test success, failure, and skipped prerequisite cases.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### U06-CFG-02 — Configuration/output interpretation

**ID:** `U06-CFG-02`  
**Unit / topic:** Test stages, quality gates, flaky-test management  
**Level:** L3  
**Objective tested:** Interpret configuration and identify missing evidence for Test stages, quality gates, flaky-test management.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret this synthetic metric/config output.

```yaml
queue_p95_minutes: 9
execution_p50_minutes: 4
missing_events: 7
reported_failures: 0
```

**Model answer**

Queue delay and execution duration are different signals. Missing events make the failure count incomplete; report coverage/unknown rather than claiming zero failures. Investigate eligible runner capacity and collector errors.

**Reasoning / explanation**

A single aggregate duration cannot identify the bottleneck, and missing observations are not zero.

**Common wrong answers or failure modes**

Assuming the system is healthy because the reported failure count is zero.

**Why a tempting wrong answer is wrong**

Reconcile with raw events and test a synthetic collection gap.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### Pipeline/configuration review


### U06-REV-01 — Configuration review

**ID:** `U06-REV-01`  
**Unit / topic:** Test stages, quality gates, flaky-test management  
**Level:** L3  
**Objective tested:** Find and fix at least three independent defects in Test stages, quality gates, flaky-test management.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three defects and propose a patch.

```yaml
permissions: write-all
cache: dist/
release_tag: latest
run: publish dist/*
```

**Model answer**

Defects: (1) broad permissions; (2) cache used as authoritative artifact handoff; (3) mutable tag without digest; (4) no explicit trusted-ref gate; (5) no checksum/manifest validation. Narrow permissions, publish only from a trusted release context, hand off the exact artifact, record digest/hash, and add a validation gate.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U06-REV-02 — Configuration review

**ID:** `U06-REV-02`  
**Unit / topic:** Test stages, quality gates, flaky-test management  
**Level:** L2  
**Objective tested:** Find and fix at least three independent defects in Test stages, quality gates, flaky-test management.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three independent defects.

```yaml
on: pull_request_target
runs-on: self-hosted
uses: actions/checkout@v4
run: echo $TOKEN
```

**Model answer**

Defects: (1) privileged event context may execute untrusted code; (2) sensitive persistent runner; (3) action not pinned to full SHA; (4) token may be printed/exposed; (5) no least-privilege permissions. Use a restricted PR event on isolated runners, avoid secrets, pin reviewed actions, and scope permissions.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U06-INC-01 — Incident scenario

**ID:** `U06-INC-01`  
**Unit / topic:** Test stages, quality gates, flaky-test management  
**Level:** L4  
**Objective tested:** Diagnose an incident relevant to Test stages, quality gates, flaky-test management and define safe recovery.  
**Estimated time:** 12 min  
**Question type:** Incident scenario

**Question prompt**

A pipeline change coincides with a reliability regression. Available evidence is partial; a retry or green aggregate status may hide the underlying problem. Give symptom → hypotheses → tests → likely cause → mitigation → prevention.

Initial hypotheses: configuration regression, capacity/provider issue, trust-boundary issue, or incomplete telemetry.

**Model answer**

Symptoms: a recent change increased pipeline failures/duration, and the current dashboard is incomplete. Diagnose by inspecting event/runner/job logs, comparing queue vs execution time, reproducing with cache disabled or tests isolated, and checking the relevant dependency/rules/credential boundary. Likely causes remain hypotheses until evidence distinguishes them. Mitigate safely: stop unsafe publishing/deployment, preserve logs, revoke exposed credentials if applicable, and restore only required gates. Prevent with a regression test, explicit ownership, and monitoring. Evidence that would change the conclusion includes a provider-wide incident, a complete independent event log, or reproduction outside CI.

**Reasoning / explanation**

Use the order: contain immediate risk, preserve evidence, discriminate hypotheses, remediate, verify, and record follow-up.

**Common wrong answers or failure modes**

Blind retries, disabling required gates, or changing multiple variables before collecting evidence.

**Why a tempting wrong answer is wrong**

The correlation does not prove the new change caused the incident; evidence must discriminate alternatives.

**Scoring rubric / acceptance criteria**

5 points: symptoms/hypotheses, diagnostic sequence, safe mitigation, prevention, verification, and evidence that could change the conclusion.


### U06-DES-01 — Design with rubric

**ID:** `U06-DES-01`  
**Unit / topic:** Test stages, quality gates, flaky-test management  
**Level:** L4  
**Objective tested:** Design a production-aware Test stages, quality gates, flaky-test management approach under zero-budget constraints.  
**Estimated time:** 18 min  
**Question type:** Design with rubric

**Question prompt**

An integration test fails 8% of first attempts, passes on retry, and mutates shared database state. Diagnose, remediate, and define quarantine governance.

Deliver a diagram or configuration outline, dependency/ownership map, security controls, acceptance criteria, and verification plan. State assumptions and distinguish M02 scope from forward references.

**Model answer**

Design should satisfy: explicit gates; minimal permissions; immutable artifact/evidence where relevant; reproducible validation; failure handling; rollback/recovery; measurable operational outcomes. Compare at least one alternative and explain why it is less suitable under the stated constraints.

**Reasoning / explanation**

A good design documents assumptions, risks, trade-offs, owner, and testable acceptance criteria.

**Common wrong answers or failure modes**

Optimizing speed alone, relying on mutable identifiers, or claiming remote controls are proven by a local simulation.

**Why a tempting wrong answer is wrong**

The best design is not a single rigid topology; it must satisfy mandatory safety and correctness requirements.

**Scoring rubric / acceptance criteria**

10 points: architecture 2, correctness/gates 2, security 2, reliability/rollback 1, measurement 1, trade-offs/clarity 2.


## Unit 7 — Artifact repositories and package publishing

**Target lesson:** [`07-artifact-repositories-and-package-publishing.md`](./07-artifact-repositories-and-package-publishing.md)  
**Coverage:** ['Artifact vs cache vs package vs image', 'Digest/checksum and manifest verification', 'Trusted publication and immutable versions']

### Conceptual short-answer


### U07-SA-01 — Short answer

**ID:** `U07-SA-01`  
**Unit / topic:** Artifact repositories and package publishing  
**Level:** L1  
**Objective tested:** Explain a core concept in Artifact repositories and package publishing.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Distinguish build artifact, package, image, and cache.

**Model answer**

Artifact is a job output, package is a versioned distribution, image is a container filesystem/config bundle, cache is disposable acceleration.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U07-SA-02 — Short answer

**ID:** `U07-SA-02`  
**Unit / topic:** Artifact repositories and package publishing  
**Level:** L2  
**Objective tested:** Explain a core concept in Artifact repositories and package publishing.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What does a checksum prove and not prove?

**Model answer**

A checksum detects byte mismatch against a trusted reference but does not prove publisher identity or safety.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U07-SA-03 — Short answer

**ID:** `U07-SA-03`  
**Unit / topic:** Artifact repositories and package publishing  
**Level:** L3  
**Objective tested:** Explain a core concept in Artifact repositories and package publishing.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Why should untrusted PR builds not publish release packages?

**Model answer**

Untrusted code may influence content or access credentials; publish only from a trusted protected release path.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### Multiple choice


### U07-MCQ-01 — Multiple choice

**ID:** `U07-MCQ-01`  
**Unit / topic:** Artifact repositories and package publishing — ['Artifact vs cache vs package vs image', 'Digest/checksum and manifest verification', 'Trusted publication and immutable versions']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Artifact vs cache vs package vs image, which choice best satisfies production correctness?

**Options**

- **A.** Option A: Artifact is a job output, package is a versioned distribution, image is a container filesystem/config bundle, cache is disposable acceleration.
- **B.** Option B: Use an unreviewed mutable reference.
- **C.** Option C: Assume a successful workflow proves production outcome.
- **D.** Option D: Skip the gate to improve speed.

**Correct answer:** A

**Why the correct option is best:** Artifact is a job output, package is a versioned distribution, image is a container filesystem/config bundle, cache is disposable acceleration.

**Distractor analysis**

- **B is incorrect:** Option B: Use an unreviewed mutable reference. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Assume a successful workflow proves production outcome. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Skip the gate to improve speed. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Artifact is a job output, package is a versioned distribution, image is a container filesystem/config bundle, cache is disposable acceleration.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U07-MCQ-02 — Multiple choice

**ID:** `U07-MCQ-02`  
**Unit / topic:** Artifact repositories and package publishing — ['Artifact vs cache vs package vs image', 'Digest/checksum and manifest verification', 'Trusted publication and immutable versions']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Digest/checksum and manifest verification, which control best handles the stated risk?

**Options**

- **A.** Option A: Serialize every job without examining dependencies.
- **B.** Option B: A checksum detects byte mismatch against a trusted reference but does not prove publisher identity or safety.
- **C.** Option C: Use a cache as the authoritative release copy.
- **D.** Option D: Treat missing telemetry as a zero value.

**Correct answer:** B

**Why the correct option is best:** A checksum detects byte mismatch against a trusted reference but does not prove publisher identity or safety.

**Distractor analysis**

- **A is incorrect:** Option A: Serialize every job without examining dependencies. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Use a cache as the authoritative release copy. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Treat missing telemetry as a zero value. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

A checksum detects byte mismatch against a trusted reference but does not prove publisher identity or safety.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U07-MCQ-03 — Multiple choice

**ID:** `U07-MCQ-03`  
**Unit / topic:** Artifact repositories and package publishing — ['Artifact vs cache vs package vs image', 'Digest/checksum and manifest verification', 'Trusted publication and immutable versions']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Trusted publication and immutable versions, which evidence should be required?

**Options**

- **A.** Option A: A mutable label alone.
- **B.** Option B: A successful rerun without first-attempt metrics.
- **C.** Option C: Untrusted code may influence content or access credentials; publish only from a trusted protected release path.
- **D.** Option D: A local simulation as proof of remote enforcement.

**Correct answer:** C

**Why the correct option is best:** Untrusted code may influence content or access credentials; publish only from a trusted protected release path.

**Distractor analysis**

- **A is incorrect:** Option A: A mutable label alone. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: A successful rerun without first-attempt metrics. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: A local simulation as proof of remote enforcement. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Untrusted code may influence content or access credentials; publish only from a trusted protected release path.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### Configuration interpretation or output reading


### U07-CFG-01 — Configuration/output interpretation

**ID:** `U07-CFG-01`  
**Unit / topic:** Artifact repositories and package publishing  
**Level:** L2  
**Objective tested:** Interpret configuration and identify missing evidence for Artifact repositories and package publishing.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret the following pipeline fragment. Identify the missing safety/correctness condition.

```yaml
jobs:
  validate:
    steps: [{run: "pytest"}]
  publish:
    steps: [{run: "publish dist/*"}]
```

**Model answer**

The publish job must depend on successful validation and consume the exact artifact produced by the build. Add explicit dependencies, trusted release conditions, bounded permissions, and immutable artifact identity.

**Reasoning / explanation**

File order does not establish a dependency; verify the actual DAG and failure behavior.

**Common wrong answers or failure modes**

Assuming publish runs after validate because it appears later in YAML.

**Why a tempting wrong answer is wrong**

Use a linter and private test repository; test success, failure, and skipped prerequisite cases.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### U07-CFG-02 — Configuration/output interpretation

**ID:** `U07-CFG-02`  
**Unit / topic:** Artifact repositories and package publishing  
**Level:** L3  
**Objective tested:** Interpret configuration and identify missing evidence for Artifact repositories and package publishing.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret this synthetic metric/config output.

```yaml
queue_p95_minutes: 9
execution_p50_minutes: 4
missing_events: 7
reported_failures: 0
```

**Model answer**

Queue delay and execution duration are different signals. Missing events make the failure count incomplete; report coverage/unknown rather than claiming zero failures. Investigate eligible runner capacity and collector errors.

**Reasoning / explanation**

A single aggregate duration cannot identify the bottleneck, and missing observations are not zero.

**Common wrong answers or failure modes**

Assuming the system is healthy because the reported failure count is zero.

**Why a tempting wrong answer is wrong**

Reconcile with raw events and test a synthetic collection gap.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### Pipeline/configuration review


### U07-REV-01 — Configuration review

**ID:** `U07-REV-01`  
**Unit / topic:** Artifact repositories and package publishing  
**Level:** L3  
**Objective tested:** Find and fix at least three independent defects in Artifact repositories and package publishing.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three defects and propose a patch.

```yaml
permissions: write-all
cache: dist/
release_tag: latest
run: publish dist/*
```

**Model answer**

Defects: (1) broad permissions; (2) cache used as authoritative artifact handoff; (3) mutable tag without digest; (4) no explicit trusted-ref gate; (5) no checksum/manifest validation. Narrow permissions, publish only from a trusted release context, hand off the exact artifact, record digest/hash, and add a validation gate.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U07-REV-02 — Configuration review

**ID:** `U07-REV-02`  
**Unit / topic:** Artifact repositories and package publishing  
**Level:** L2  
**Objective tested:** Find and fix at least three independent defects in Artifact repositories and package publishing.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three independent defects.

```yaml
on: pull_request_target
runs-on: self-hosted
uses: actions/checkout@v4
run: echo $TOKEN
```

**Model answer**

Defects: (1) privileged event context may execute untrusted code; (2) sensitive persistent runner; (3) action not pinned to full SHA; (4) token may be printed/exposed; (5) no least-privilege permissions. Use a restricted PR event on isolated runners, avoid secrets, pin reviewed actions, and scope permissions.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U07-INC-01 — Incident scenario

**ID:** `U07-INC-01`  
**Unit / topic:** Artifact repositories and package publishing  
**Level:** L4  
**Objective tested:** Diagnose an incident relevant to Artifact repositories and package publishing and define safe recovery.  
**Estimated time:** 12 min  
**Question type:** Incident scenario

**Question prompt**

A pipeline change coincides with a reliability regression. Available evidence is partial; a retry or green aggregate status may hide the underlying problem. Give symptom → hypotheses → tests → likely cause → mitigation → prevention.

Initial hypotheses: configuration regression, capacity/provider issue, trust-boundary issue, or incomplete telemetry.

**Model answer**

Symptoms: a recent change increased pipeline failures/duration, and the current dashboard is incomplete. Diagnose by inspecting event/runner/job logs, comparing queue vs execution time, reproducing with cache disabled or tests isolated, and checking the relevant dependency/rules/credential boundary. Likely causes remain hypotheses until evidence distinguishes them. Mitigate safely: stop unsafe publishing/deployment, preserve logs, revoke exposed credentials if applicable, and restore only required gates. Prevent with a regression test, explicit ownership, and monitoring. Evidence that would change the conclusion includes a provider-wide incident, a complete independent event log, or reproduction outside CI.

**Reasoning / explanation**

Use the order: contain immediate risk, preserve evidence, discriminate hypotheses, remediate, verify, and record follow-up.

**Common wrong answers or failure modes**

Blind retries, disabling required gates, or changing multiple variables before collecting evidence.

**Why a tempting wrong answer is wrong**

The correlation does not prove the new change caused the incident; evidence must discriminate alternatives.

**Scoring rubric / acceptance criteria**

5 points: symptoms/hypotheses, diagnostic sequence, safe mitigation, prevention, verification, and evidence that could change the conclusion.


### U07-DES-01 — Design with rubric

**ID:** `U07-DES-01`  
**Unit / topic:** Artifact repositories and package publishing  
**Level:** L4  
**Objective tested:** Design a production-aware Artifact repositories and package publishing approach under zero-budget constraints.  
**Estimated time:** 18 min  
**Question type:** Design with rubric

**Question prompt**

Staging package hash differs from the release manifest. Investigate safely and define publication/promotion prevention controls.

Deliver a diagram or configuration outline, dependency/ownership map, security controls, acceptance criteria, and verification plan. State assumptions and distinguish M02 scope from forward references.

**Model answer**

Design should satisfy: explicit gates; minimal permissions; immutable artifact/evidence where relevant; reproducible validation; failure handling; rollback/recovery; measurable operational outcomes. Compare at least one alternative and explain why it is less suitable under the stated constraints.

**Reasoning / explanation**

A good design documents assumptions, risks, trade-offs, owner, and testable acceptance criteria.

**Common wrong answers or failure modes**

Optimizing speed alone, relying on mutable identifiers, or claiming remote controls are proven by a local simulation.

**Why a tempting wrong answer is wrong**

The best design is not a single rigid topology; it must satisfy mandatory safety and correctness requirements.

**Scoring rubric / acceptance criteria**

10 points: architecture 2, correctness/gates 2, security 2, reliability/rollback 1, measurement 1, trade-offs/clarity 2.


## Unit 8 — Semantic versioning, changelogs, release automation

**Target lesson:** [`08-semantic-versioning-changelogs-and-release-automation.md`](./08-semantic-versioning-changelogs-and-release-automation.md)  
**Coverage:** ['SemVer MAJOR/MINOR/PATCH', 'Conventional Commit limits and changelog consistency', 'Idempotent release recovery and partial external state']

### Conceptual short-answer


### U08-SA-01 — Short answer

**ID:** `U08-SA-01`  
**Unit / topic:** Semantic versioning, changelogs, release automation  
**Level:** L1  
**Objective tested:** Explain a core concept in Semantic versioning, changelogs, release automation.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

When does a public library normally require a MAJOR increment?

**Model answer**

A public incompatible API change requires a MAJOR increment under the declared compatibility contract.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U08-SA-02 — Short answer

**ID:** `U08-SA-02`  
**Unit / topic:** Semantic versioning, changelogs, release automation  
**Level:** L2  
**Objective tested:** Explain a core concept in Semantic versioning, changelogs, release automation.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What are the limits of Conventional Commit automation?

**Model answer**

Commit messages are hints; they do not prove compatibility or detect every breaking change.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U08-SA-03 — Short answer

**ID:** `U08-SA-03`  
**Unit / topic:** Semantic versioning, changelogs, release automation  
**Level:** L3  
**Objective tested:** Explain a core concept in Semantic versioning, changelogs, release automation.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What does idempotent release automation guarantee?

**Model answer**

A rerun does not create conflicting tags/releases or publish different bytes under the same version; partial state is reconciled.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### Multiple choice


### U08-MCQ-01 — Multiple choice

**ID:** `U08-MCQ-01`  
**Unit / topic:** Semantic versioning, changelogs, release automation — ['SemVer MAJOR/MINOR/PATCH', 'Conventional Commit limits and changelog consistency', 'Idempotent release recovery and partial external state']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For SemVer MAJOR/MINOR/PATCH, which choice best satisfies production correctness?

**Options**

- **A.** Option A: Use an unreviewed mutable reference.
- **B.** Option B: A public incompatible API change requires a MAJOR increment under the declared compatibility contract.
- **C.** Option C: Assume a successful workflow proves production outcome.
- **D.** Option D: Skip the gate to improve speed.

**Correct answer:** B

**Why the correct option is best:** A public incompatible API change requires a MAJOR increment under the declared compatibility contract.

**Distractor analysis**

- **A is incorrect:** Option A: Use an unreviewed mutable reference. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Assume a successful workflow proves production outcome. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Skip the gate to improve speed. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

A public incompatible API change requires a MAJOR increment under the declared compatibility contract.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U08-MCQ-02 — Multiple choice

**ID:** `U08-MCQ-02`  
**Unit / topic:** Semantic versioning, changelogs, release automation — ['SemVer MAJOR/MINOR/PATCH', 'Conventional Commit limits and changelog consistency', 'Idempotent release recovery and partial external state']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Conventional Commit limits and changelog consistency, which control best handles the stated risk?

**Options**

- **A.** Option A: Serialize every job without examining dependencies.
- **B.** Option B: Use a cache as the authoritative release copy.
- **C.** Option C: Commit messages are hints; they do not prove compatibility or detect every breaking change.
- **D.** Option D: Treat missing telemetry as a zero value.

**Correct answer:** C

**Why the correct option is best:** Commit messages are hints; they do not prove compatibility or detect every breaking change.

**Distractor analysis**

- **A is incorrect:** Option A: Serialize every job without examining dependencies. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: Use a cache as the authoritative release copy. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Treat missing telemetry as a zero value. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Commit messages are hints; they do not prove compatibility or detect every breaking change.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U08-MCQ-03 — Multiple choice

**ID:** `U08-MCQ-03`  
**Unit / topic:** Semantic versioning, changelogs, release automation — ['SemVer MAJOR/MINOR/PATCH', 'Conventional Commit limits and changelog consistency', 'Idempotent release recovery and partial external state']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Idempotent release recovery and partial external state, which evidence should be required?

**Options**

- **A.** Option A: A mutable label alone.
- **B.** Option B: A successful rerun without first-attempt metrics.
- **C.** Option C: A local simulation as proof of remote enforcement.
- **D.** Option D: A rerun does not create conflicting tags/releases or publish different bytes under the same version; partial state is reconciled.

**Correct answer:** D

**Why the correct option is best:** A rerun does not create conflicting tags/releases or publish different bytes under the same version; partial state is reconciled.

**Distractor analysis**

- **A is incorrect:** Option A: A mutable label alone. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: A successful rerun without first-attempt metrics. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: A local simulation as proof of remote enforcement. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

A rerun does not create conflicting tags/releases or publish different bytes under the same version; partial state is reconciled.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### Configuration interpretation or output reading


### U08-CFG-01 — Configuration/output interpretation

**ID:** `U08-CFG-01`  
**Unit / topic:** Semantic versioning, changelogs, release automation  
**Level:** L2  
**Objective tested:** Interpret configuration and identify missing evidence for Semantic versioning, changelogs, release automation.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret the following pipeline fragment. Identify the missing safety/correctness condition.

```yaml
jobs:
  validate:
    steps: [{run: "pytest"}]
  publish:
    steps: [{run: "publish dist/*"}]
```

**Model answer**

The publish job must depend on successful validation and consume the exact artifact produced by the build. Add explicit dependencies, trusted release conditions, bounded permissions, and immutable artifact identity.

**Reasoning / explanation**

File order does not establish a dependency; verify the actual DAG and failure behavior.

**Common wrong answers or failure modes**

Assuming publish runs after validate because it appears later in YAML.

**Why a tempting wrong answer is wrong**

Use a linter and private test repository; test success, failure, and skipped prerequisite cases.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### U08-CFG-02 — Configuration/output interpretation

**ID:** `U08-CFG-02`  
**Unit / topic:** Semantic versioning, changelogs, release automation  
**Level:** L3  
**Objective tested:** Interpret configuration and identify missing evidence for Semantic versioning, changelogs, release automation.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret this synthetic metric/config output.

```yaml
queue_p95_minutes: 9
execution_p50_minutes: 4
missing_events: 7
reported_failures: 0
```

**Model answer**

Queue delay and execution duration are different signals. Missing events make the failure count incomplete; report coverage/unknown rather than claiming zero failures. Investigate eligible runner capacity and collector errors.

**Reasoning / explanation**

A single aggregate duration cannot identify the bottleneck, and missing observations are not zero.

**Common wrong answers or failure modes**

Assuming the system is healthy because the reported failure count is zero.

**Why a tempting wrong answer is wrong**

Reconcile with raw events and test a synthetic collection gap.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### Pipeline/configuration review


### U08-REV-01 — Configuration review

**ID:** `U08-REV-01`  
**Unit / topic:** Semantic versioning, changelogs, release automation  
**Level:** L3  
**Objective tested:** Find and fix at least three independent defects in Semantic versioning, changelogs, release automation.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three defects and propose a patch.

```yaml
permissions: write-all
cache: dist/
release_tag: latest
run: publish dist/*
```

**Model answer**

Defects: (1) broad permissions; (2) cache used as authoritative artifact handoff; (3) mutable tag without digest; (4) no explicit trusted-ref gate; (5) no checksum/manifest validation. Narrow permissions, publish only from a trusted release context, hand off the exact artifact, record digest/hash, and add a validation gate.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U08-REV-02 — Configuration review

**ID:** `U08-REV-02`  
**Unit / topic:** Semantic versioning, changelogs, release automation  
**Level:** L2  
**Objective tested:** Find and fix at least three independent defects in Semantic versioning, changelogs, release automation.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three independent defects.

```yaml
on: pull_request_target
runs-on: self-hosted
uses: actions/checkout@v4
run: echo $TOKEN
```

**Model answer**

Defects: (1) privileged event context may execute untrusted code; (2) sensitive persistent runner; (3) action not pinned to full SHA; (4) token may be printed/exposed; (5) no least-privilege permissions. Use a restricted PR event on isolated runners, avoid secrets, pin reviewed actions, and scope permissions.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U08-INC-01 — Incident scenario

**ID:** `U08-INC-01`  
**Unit / topic:** Semantic versioning, changelogs, release automation  
**Level:** L4  
**Objective tested:** Diagnose an incident relevant to Semantic versioning, changelogs, release automation and define safe recovery.  
**Estimated time:** 12 min  
**Question type:** Incident scenario

**Question prompt**

A pipeline change coincides with a reliability regression. Available evidence is partial; a retry or green aggregate status may hide the underlying problem. Give symptom → hypotheses → tests → likely cause → mitigation → prevention.

Initial hypotheses: configuration regression, capacity/provider issue, trust-boundary issue, or incomplete telemetry.

**Model answer**

Symptoms: a recent change increased pipeline failures/duration, and the current dashboard is incomplete. Diagnose by inspecting event/runner/job logs, comparing queue vs execution time, reproducing with cache disabled or tests isolated, and checking the relevant dependency/rules/credential boundary. Likely causes remain hypotheses until evidence distinguishes them. Mitigate safely: stop unsafe publishing/deployment, preserve logs, revoke exposed credentials if applicable, and restore only required gates. Prevent with a regression test, explicit ownership, and monitoring. Evidence that would change the conclusion includes a provider-wide incident, a complete independent event log, or reproduction outside CI.

**Reasoning / explanation**

Use the order: contain immediate risk, preserve evidence, discriminate hypotheses, remediate, verify, and record follow-up.

**Common wrong answers or failure modes**

Blind retries, disabling required gates, or changing multiple variables before collecting evidence.

**Why a tempting wrong answer is wrong**

The correlation does not prove the new change caused the incident; evidence must discriminate alternatives.

**Scoring rubric / acceptance criteria**

5 points: symptoms/hypotheses, diagnostic sequence, safe mitigation, prevention, verification, and evidence that could change the conclusion.


### U08-DES-01 — Design with rubric

**ID:** `U08-DES-01`  
**Unit / topic:** Semantic versioning, changelogs, release automation  
**Level:** L4  
**Objective tested:** Design a production-aware Semantic versioning, changelogs, release automation approach under zero-budget constraints.  
**Estimated time:** 18 min  
**Question type:** Design with rubric

**Question prompt**

A tag exists but publication timed out. Design an idempotent recovery without force-moving the tag or overwriting unknown content.

Deliver a diagram or configuration outline, dependency/ownership map, security controls, acceptance criteria, and verification plan. State assumptions and distinguish M02 scope from forward references.

**Model answer**

Design should satisfy: explicit gates; minimal permissions; immutable artifact/evidence where relevant; reproducible validation; failure handling; rollback/recovery; measurable operational outcomes. Compare at least one alternative and explain why it is less suitable under the stated constraints.

**Reasoning / explanation**

A good design documents assumptions, risks, trade-offs, owner, and testable acceptance criteria.

**Common wrong answers or failure modes**

Optimizing speed alone, relying on mutable identifiers, or claiming remote controls are proven by a local simulation.

**Why a tempting wrong answer is wrong**

The best design is not a single rigid topology; it must satisfy mandatory safety and correctness requirements.

**Scoring rubric / acceptance criteria**

10 points: architecture 2, correctness/gates 2, security 2, reliability/rollback 1, measurement 1, trade-offs/clarity 2.


## Unit 9 — Environment promotion, approvals, protected branches

**Target lesson:** [`09-environment-promotion-approvals-and-protected-branches.md`](./09-environment-promotion-approvals-and-protected-branches.md)  
**Coverage:** ['Promote same digest through environments', 'Branch/environment rules and separation of duties', 'Bypass auditing, rollback, deployment handoff']

### Conceptual short-answer


### U09-SA-01 — Short answer

**ID:** `U09-SA-01`  
**Unit / topic:** Environment promotion, approvals, protected branches  
**Level:** L1  
**Objective tested:** Explain a core concept in Environment promotion, approvals, protected branches.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Why promote the same digest rather than rebuild?

**Model answer**

The digest links tested content to promoted bytes; rebuilding can change output.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U09-SA-02 — Short answer

**ID:** `U09-SA-02`  
**Unit / topic:** Environment promotion, approvals, protected branches  
**Level:** L2  
**Objective tested:** Explain a core concept in Environment promotion, approvals, protected branches.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What does separation of duties protect?

**Model answer**

It separates authoring/review/approval/deployment powers proportionally to risk and makes bypass auditable.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U09-SA-03 — Short answer

**ID:** `U09-SA-03`  
**Unit / topic:** Environment promotion, approvals, protected branches  
**Level:** L3  
**Objective tested:** Explain a core concept in Environment promotion, approvals, protected branches.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What can a local approval simulation prove?

**Model answer**

It tests local state logic, not remote branch/environment enforcement.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### Multiple choice


### U09-MCQ-01 — Multiple choice

**ID:** `U09-MCQ-01`  
**Unit / topic:** Environment promotion, approvals, protected branches — ['Promote same digest through environments', 'Branch/environment rules and separation of duties', 'Bypass auditing, rollback, deployment handoff']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Promote same digest through environments, which choice best satisfies production correctness?

**Options**

- **A.** Option A: Use an unreviewed mutable reference.
- **B.** Option B: Assume a successful workflow proves production outcome.
- **C.** Option C: The digest links tested content to promoted bytes; rebuilding can change output.
- **D.** Option D: Skip the gate to improve speed.

**Correct answer:** C

**Why the correct option is best:** The digest links tested content to promoted bytes; rebuilding can change output.

**Distractor analysis**

- **A is incorrect:** Option A: Use an unreviewed mutable reference. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: Assume a successful workflow proves production outcome. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Skip the gate to improve speed. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

The digest links tested content to promoted bytes; rebuilding can change output.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U09-MCQ-02 — Multiple choice

**ID:** `U09-MCQ-02`  
**Unit / topic:** Environment promotion, approvals, protected branches — ['Promote same digest through environments', 'Branch/environment rules and separation of duties', 'Bypass auditing, rollback, deployment handoff']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Branch/environment rules and separation of duties, which control best handles the stated risk?

**Options**

- **A.** Option A: Serialize every job without examining dependencies.
- **B.** Option B: Use a cache as the authoritative release copy.
- **C.** Option C: Treat missing telemetry as a zero value.
- **D.** Option D: It separates authoring/review/approval/deployment powers proportionally to risk and makes bypass auditable.

**Correct answer:** D

**Why the correct option is best:** It separates authoring/review/approval/deployment powers proportionally to risk and makes bypass auditable.

**Distractor analysis**

- **A is incorrect:** Option A: Serialize every job without examining dependencies. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: Use a cache as the authoritative release copy. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Treat missing telemetry as a zero value. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

It separates authoring/review/approval/deployment powers proportionally to risk and makes bypass auditable.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U09-MCQ-03 — Multiple choice

**ID:** `U09-MCQ-03`  
**Unit / topic:** Environment promotion, approvals, protected branches — ['Promote same digest through environments', 'Branch/environment rules and separation of duties', 'Bypass auditing, rollback, deployment handoff']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Bypass auditing, rollback, deployment handoff, which evidence should be required?

**Options**

- **A.** Option A: It tests local state logic, not remote branch/environment enforcement.
- **B.** Option B: A mutable label alone.
- **C.** Option C: A successful rerun without first-attempt metrics.
- **D.** Option D: A local simulation as proof of remote enforcement.

**Correct answer:** A

**Why the correct option is best:** It tests local state logic, not remote branch/environment enforcement.

**Distractor analysis**

- **B is incorrect:** Option B: A mutable label alone. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: A successful rerun without first-attempt metrics. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: A local simulation as proof of remote enforcement. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

It tests local state logic, not remote branch/environment enforcement.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### Configuration interpretation or output reading


### U09-CFG-01 — Configuration/output interpretation

**ID:** `U09-CFG-01`  
**Unit / topic:** Environment promotion, approvals, protected branches  
**Level:** L2  
**Objective tested:** Interpret configuration and identify missing evidence for Environment promotion, approvals, protected branches.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret the following pipeline fragment. Identify the missing safety/correctness condition.

```yaml
jobs:
  validate:
    steps: [{run: "pytest"}]
  publish:
    steps: [{run: "publish dist/*"}]
```

**Model answer**

The publish job must depend on successful validation and consume the exact artifact produced by the build. Add explicit dependencies, trusted release conditions, bounded permissions, and immutable artifact identity.

**Reasoning / explanation**

File order does not establish a dependency; verify the actual DAG and failure behavior.

**Common wrong answers or failure modes**

Assuming publish runs after validate because it appears later in YAML.

**Why a tempting wrong answer is wrong**

Use a linter and private test repository; test success, failure, and skipped prerequisite cases.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### U09-CFG-02 — Configuration/output interpretation

**ID:** `U09-CFG-02`  
**Unit / topic:** Environment promotion, approvals, protected branches  
**Level:** L3  
**Objective tested:** Interpret configuration and identify missing evidence for Environment promotion, approvals, protected branches.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret this synthetic metric/config output.

```yaml
queue_p95_minutes: 9
execution_p50_minutes: 4
missing_events: 7
reported_failures: 0
```

**Model answer**

Queue delay and execution duration are different signals. Missing events make the failure count incomplete; report coverage/unknown rather than claiming zero failures. Investigate eligible runner capacity and collector errors.

**Reasoning / explanation**

A single aggregate duration cannot identify the bottleneck, and missing observations are not zero.

**Common wrong answers or failure modes**

Assuming the system is healthy because the reported failure count is zero.

**Why a tempting wrong answer is wrong**

Reconcile with raw events and test a synthetic collection gap.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### Pipeline/configuration review


### U09-REV-01 — Configuration review

**ID:** `U09-REV-01`  
**Unit / topic:** Environment promotion, approvals, protected branches  
**Level:** L3  
**Objective tested:** Find and fix at least three independent defects in Environment promotion, approvals, protected branches.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three defects and propose a patch.

```yaml
permissions: write-all
cache: dist/
release_tag: latest
run: publish dist/*
```

**Model answer**

Defects: (1) broad permissions; (2) cache used as authoritative artifact handoff; (3) mutable tag without digest; (4) no explicit trusted-ref gate; (5) no checksum/manifest validation. Narrow permissions, publish only from a trusted release context, hand off the exact artifact, record digest/hash, and add a validation gate.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U09-REV-02 — Configuration review

**ID:** `U09-REV-02`  
**Unit / topic:** Environment promotion, approvals, protected branches  
**Level:** L2  
**Objective tested:** Find and fix at least three independent defects in Environment promotion, approvals, protected branches.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three independent defects.

```yaml
on: pull_request_target
runs-on: self-hosted
uses: actions/checkout@v4
run: echo $TOKEN
```

**Model answer**

Defects: (1) privileged event context may execute untrusted code; (2) sensitive persistent runner; (3) action not pinned to full SHA; (4) token may be printed/exposed; (5) no least-privilege permissions. Use a restricted PR event on isolated runners, avoid secrets, pin reviewed actions, and scope permissions.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U09-INC-01 — Incident scenario

**ID:** `U09-INC-01`  
**Unit / topic:** Environment promotion, approvals, protected branches  
**Level:** L4  
**Objective tested:** Diagnose an incident relevant to Environment promotion, approvals, protected branches and define safe recovery.  
**Estimated time:** 12 min  
**Question type:** Incident scenario

**Question prompt**

A pipeline change coincides with a reliability regression. Available evidence is partial; a retry or green aggregate status may hide the underlying problem. Give symptom → hypotheses → tests → likely cause → mitigation → prevention.

Initial hypotheses: configuration regression, capacity/provider issue, trust-boundary issue, or incomplete telemetry.

**Model answer**

Symptoms: a recent change increased pipeline failures/duration, and the current dashboard is incomplete. Diagnose by inspecting event/runner/job logs, comparing queue vs execution time, reproducing with cache disabled or tests isolated, and checking the relevant dependency/rules/credential boundary. Likely causes remain hypotheses until evidence distinguishes them. Mitigate safely: stop unsafe publishing/deployment, preserve logs, revoke exposed credentials if applicable, and restore only required gates. Prevent with a regression test, explicit ownership, and monitoring. Evidence that would change the conclusion includes a provider-wide incident, a complete independent event log, or reproduction outside CI.

**Reasoning / explanation**

Use the order: contain immediate risk, preserve evidence, discriminate hypotheses, remediate, verify, and record follow-up.

**Common wrong answers or failure modes**

Blind retries, disabling required gates, or changing multiple variables before collecting evidence.

**Why a tempting wrong answer is wrong**

The correlation does not prove the new change caused the incident; evidence must discriminate alternatives.

**Scoring rubric / acceptance criteria**

5 points: symptoms/hypotheses, diagnostic sequence, safe mitigation, prevention, verification, and evidence that could change the conclusion.


### U09-DES-01 — Design with rubric

**ID:** `U09-DES-01`  
**Unit / topic:** Environment promotion, approvals, protected branches  
**Level:** L4  
**Objective tested:** Design a production-aware Environment promotion, approvals, protected branches approach under zero-budget constraints.  
**Estimated time:** 18 min  
**Question type:** Design with rubric

**Question prompt**

Production ran without an approval event and a broad token exists. Triage, contain, verify artifact identity, and prevent recurrence.

Deliver a diagram or configuration outline, dependency/ownership map, security controls, acceptance criteria, and verification plan. State assumptions and distinguish M02 scope from forward references.

**Model answer**

Design should satisfy: explicit gates; minimal permissions; immutable artifact/evidence where relevant; reproducible validation; failure handling; rollback/recovery; measurable operational outcomes. Compare at least one alternative and explain why it is less suitable under the stated constraints.

**Reasoning / explanation**

A good design documents assumptions, risks, trade-offs, owner, and testable acceptance criteria.

**Common wrong answers or failure modes**

Optimizing speed alone, relying on mutable identifiers, or claiming remote controls are proven by a local simulation.

**Why a tempting wrong answer is wrong**

The best design is not a single rigid topology; it must satisfy mandatory safety and correctness requirements.

**Scoring rubric / acceptance criteria**

10 points: architecture 2, correctness/gates 2, security 2, reliability/rollback 1, measurement 1, trade-offs/clarity 2.


## Unit 10 — Self-hosted runners: scaling and security

**Target lesson:** [`10-self-hosted-runners-scaling-and-security.md`](./10-self-hosted-runners-scaling-and-security.md)  
**Coverage:** ['Persistent vs ephemeral lifecycle', 'Public-fork trust boundary, Docker socket and egress', 'Compromise response and queue-driven scaling']

### Conceptual short-answer


### U10-SA-01 — Short answer

**ID:** `U10-SA-01`  
**Unit / topic:** Self-hosted runners: scaling and security  
**Level:** L1  
**Objective tested:** Explain a core concept in Self-hosted runners: scaling and security.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What risk differs between persistent and ephemeral runners?

**Model answer**

Persistent hosts can retain state; ephemeral lifecycle reduces residue but does not eliminate in-job exposure.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U10-SA-02 — Short answer

**ID:** `U10-SA-02`  
**Unit / topic:** Self-hosted runners: scaling and security  
**Level:** L2  
**Objective tested:** Explain a core concept in Self-hosted runners: scaling and security.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Why should public-fork code not run on sensitive self-hosted runners?

**Model answer**

Untrusted code can access host privileges, workspace residue, credentials, Docker socket, or internal network.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U10-SA-03 — Short answer

**ID:** `U10-SA-03`  
**Unit / topic:** Self-hosted runners: scaling and security  
**Level:** L3  
**Objective tested:** Explain a core concept in Self-hosted runners: scaling and security.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

What is the response sequence for a potentially compromised runner?

**Model answer**

Isolate, preserve evidence, revoke/rotate credentials, rebuild from trusted image, investigate, validate before reuse.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### Multiple choice


### U10-MCQ-01 — Multiple choice

**ID:** `U10-MCQ-01`  
**Unit / topic:** Self-hosted runners: scaling and security — ['Persistent vs ephemeral lifecycle', 'Public-fork trust boundary, Docker socket and egress', 'Compromise response and queue-driven scaling']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Persistent vs ephemeral lifecycle, which choice best satisfies production correctness?

**Options**

- **A.** Option A: Use an unreviewed mutable reference.
- **B.** Option B: Assume a successful workflow proves production outcome.
- **C.** Option C: Skip the gate to improve speed.
- **D.** Option D: Persistent hosts can retain state; ephemeral lifecycle reduces residue but does not eliminate in-job exposure.

**Correct answer:** D

**Why the correct option is best:** Persistent hosts can retain state; ephemeral lifecycle reduces residue but does not eliminate in-job exposure.

**Distractor analysis**

- **A is incorrect:** Option A: Use an unreviewed mutable reference. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: Assume a successful workflow proves production outcome. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Skip the gate to improve speed. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Persistent hosts can retain state; ephemeral lifecycle reduces residue but does not eliminate in-job exposure.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U10-MCQ-02 — Multiple choice

**ID:** `U10-MCQ-02`  
**Unit / topic:** Self-hosted runners: scaling and security — ['Persistent vs ephemeral lifecycle', 'Public-fork trust boundary, Docker socket and egress', 'Compromise response and queue-driven scaling']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Public-fork trust boundary, Docker socket and egress, which control best handles the stated risk?

**Options**

- **A.** Option A: Untrusted code can access host privileges, workspace residue, credentials, Docker socket, or internal network.
- **B.** Option B: Serialize every job without examining dependencies.
- **C.** Option C: Use a cache as the authoritative release copy.
- **D.** Option D: Treat missing telemetry as a zero value.

**Correct answer:** A

**Why the correct option is best:** Untrusted code can access host privileges, workspace residue, credentials, Docker socket, or internal network.

**Distractor analysis**

- **B is incorrect:** Option B: Serialize every job without examining dependencies. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Use a cache as the authoritative release copy. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Treat missing telemetry as a zero value. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Untrusted code can access host privileges, workspace residue, credentials, Docker socket, or internal network.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U10-MCQ-03 — Multiple choice

**ID:** `U10-MCQ-03`  
**Unit / topic:** Self-hosted runners: scaling and security — ['Persistent vs ephemeral lifecycle', 'Public-fork trust boundary, Docker socket and egress', 'Compromise response and queue-driven scaling']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Compromise response and queue-driven scaling, which evidence should be required?

**Options**

- **A.** Option A: A mutable label alone.
- **B.** Option B: Isolate, preserve evidence, revoke/rotate credentials, rebuild from trusted image, investigate, validate before reuse.
- **C.** Option C: A successful rerun without first-attempt metrics.
- **D.** Option D: A local simulation as proof of remote enforcement.

**Correct answer:** B

**Why the correct option is best:** Isolate, preserve evidence, revoke/rotate credentials, rebuild from trusted image, investigate, validate before reuse.

**Distractor analysis**

- **A is incorrect:** Option A: A mutable label alone. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: A successful rerun without first-attempt metrics. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: A local simulation as proof of remote enforcement. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Isolate, preserve evidence, revoke/rotate credentials, rebuild from trusted image, investigate, validate before reuse.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### Configuration interpretation or output reading


### U10-CFG-01 — Configuration/output interpretation

**ID:** `U10-CFG-01`  
**Unit / topic:** Self-hosted runners: scaling and security  
**Level:** L2  
**Objective tested:** Interpret configuration and identify missing evidence for Self-hosted runners: scaling and security.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret the following pipeline fragment. Identify the missing safety/correctness condition.

```yaml
jobs:
  validate:
    steps: [{run: "pytest"}]
  publish:
    steps: [{run: "publish dist/*"}]
```

**Model answer**

The publish job must depend on successful validation and consume the exact artifact produced by the build. Add explicit dependencies, trusted release conditions, bounded permissions, and immutable artifact identity.

**Reasoning / explanation**

File order does not establish a dependency; verify the actual DAG and failure behavior.

**Common wrong answers or failure modes**

Assuming publish runs after validate because it appears later in YAML.

**Why a tempting wrong answer is wrong**

Use a linter and private test repository; test success, failure, and skipped prerequisite cases.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### U10-CFG-02 — Configuration/output interpretation

**ID:** `U10-CFG-02`  
**Unit / topic:** Self-hosted runners: scaling and security  
**Level:** L3  
**Objective tested:** Interpret configuration and identify missing evidence for Self-hosted runners: scaling and security.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret this synthetic metric/config output.

```yaml
queue_p95_minutes: 9
execution_p50_minutes: 4
missing_events: 7
reported_failures: 0
```

**Model answer**

Queue delay and execution duration are different signals. Missing events make the failure count incomplete; report coverage/unknown rather than claiming zero failures. Investigate eligible runner capacity and collector errors.

**Reasoning / explanation**

A single aggregate duration cannot identify the bottleneck, and missing observations are not zero.

**Common wrong answers or failure modes**

Assuming the system is healthy because the reported failure count is zero.

**Why a tempting wrong answer is wrong**

Reconcile with raw events and test a synthetic collection gap.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### Pipeline/configuration review


### U10-REV-01 — Configuration review

**ID:** `U10-REV-01`  
**Unit / topic:** Self-hosted runners: scaling and security  
**Level:** L3  
**Objective tested:** Find and fix at least three independent defects in Self-hosted runners: scaling and security.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three defects and propose a patch.

```yaml
permissions: write-all
cache: dist/
release_tag: latest
run: publish dist/*
```

**Model answer**

Defects: (1) broad permissions; (2) cache used as authoritative artifact handoff; (3) mutable tag without digest; (4) no explicit trusted-ref gate; (5) no checksum/manifest validation. Narrow permissions, publish only from a trusted release context, hand off the exact artifact, record digest/hash, and add a validation gate.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U10-REV-02 — Configuration review

**ID:** `U10-REV-02`  
**Unit / topic:** Self-hosted runners: scaling and security  
**Level:** L2  
**Objective tested:** Find and fix at least three independent defects in Self-hosted runners: scaling and security.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three independent defects.

```yaml
on: pull_request_target
runs-on: self-hosted
uses: actions/checkout@v4
run: echo $TOKEN
```

**Model answer**

Defects: (1) privileged event context may execute untrusted code; (2) sensitive persistent runner; (3) action not pinned to full SHA; (4) token may be printed/exposed; (5) no least-privilege permissions. Use a restricted PR event on isolated runners, avoid secrets, pin reviewed actions, and scope permissions.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U10-INC-01 — Incident scenario

**ID:** `U10-INC-01`  
**Unit / topic:** Self-hosted runners: scaling and security  
**Level:** L4  
**Objective tested:** Diagnose an incident relevant to Self-hosted runners: scaling and security and define safe recovery.  
**Estimated time:** 12 min  
**Question type:** Incident scenario

**Question prompt**

A pipeline change coincides with a reliability regression. Available evidence is partial; a retry or green aggregate status may hide the underlying problem. Give symptom → hypotheses → tests → likely cause → mitigation → prevention.

Initial hypotheses: configuration regression, capacity/provider issue, trust-boundary issue, or incomplete telemetry.

**Model answer**

Symptoms: a recent change increased pipeline failures/duration, and the current dashboard is incomplete. Diagnose by inspecting event/runner/job logs, comparing queue vs execution time, reproducing with cache disabled or tests isolated, and checking the relevant dependency/rules/credential boundary. Likely causes remain hypotheses until evidence distinguishes them. Mitigate safely: stop unsafe publishing/deployment, preserve logs, revoke exposed credentials if applicable, and restore only required gates. Prevent with a regression test, explicit ownership, and monitoring. Evidence that would change the conclusion includes a provider-wide incident, a complete independent event log, or reproduction outside CI.

**Reasoning / explanation**

Use the order: contain immediate risk, preserve evidence, discriminate hypotheses, remediate, verify, and record follow-up.

**Common wrong answers or failure modes**

Blind retries, disabling required gates, or changing multiple variables before collecting evidence.

**Why a tempting wrong answer is wrong**

The correlation does not prove the new change caused the incident; evidence must discriminate alternatives.

**Scoring rubric / acceptance criteria**

5 points: symptoms/hypotheses, diagnostic sequence, safe mitigation, prevention, verification, and evidence that could change the conclusion.


### U10-DES-01 — Design with rubric

**ID:** `U10-DES-01`  
**Unit / topic:** Self-hosted runners: scaling and security  
**Level:** L4  
**Objective tested:** Design a production-aware Self-hosted runners: scaling and security approach under zero-budget constraints.  
**Estimated time:** 18 min  
**Question type:** Design with rubric

**Question prompt**

Unexpected commands ran on a persistent runner with a static cloud token. Respond without destroying evidence or reusing a compromised host.

Deliver a diagram or configuration outline, dependency/ownership map, security controls, acceptance criteria, and verification plan. State assumptions and distinguish M02 scope from forward references.

**Model answer**

Design should satisfy: explicit gates; minimal permissions; immutable artifact/evidence where relevant; reproducible validation; failure handling; rollback/recovery; measurable operational outcomes. Compare at least one alternative and explain why it is less suitable under the stated constraints.

**Reasoning / explanation**

A good design documents assumptions, risks, trade-offs, owner, and testable acceptance criteria.

**Common wrong answers or failure modes**

Optimizing speed alone, relying on mutable identifiers, or claiming remote controls are proven by a local simulation.

**Why a tempting wrong answer is wrong**

The best design is not a single rigid topology; it must satisfy mandatory safety and correctness requirements.

**Scoring rubric / acceptance criteria**

10 points: architecture 2, correctness/gates 2, security 2, reliability/rollback 1, measurement 1, trade-offs/clarity 2.


## Unit 11 — Pipeline observability and DORA delivery metrics

**Target lesson:** [`11-pipeline-observability-and-dora-delivery-metrics.md`](./11-pipeline-observability-and-dora-delivery-metrics.md)  
**Coverage:** ['DORA metric definitions and anti-gaming', 'Queue/execution duration, flake/retry rate, pipeline SLOs', 'Missing telemetry, correlation IDs, percentiles and coverage']

### Conceptual short-answer


### U11-SA-01 — Short answer

**ID:** `U11-SA-01`  
**Unit / topic:** Pipeline observability and DORA delivery metrics  
**Level:** L1  
**Objective tested:** Explain a core concept in Pipeline observability and DORA delivery metrics.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Why are delivery metrics team/system signals rather than individual rankings?

**Model answer**

Metrics depend on context and definitions; individual rankings incentivize gaming and obscure systemic constraints.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U11-SA-02 — Short answer

**ID:** `U11-SA-02`  
**Unit / topic:** Pipeline observability and DORA delivery metrics  
**Level:** L2  
**Objective tested:** Explain a core concept in Pipeline observability and DORA delivery metrics.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Distinguish queue time from execution time.

**Model answer**

Queue time is waiting for eligible capacity; execution time is running work after start.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### U11-SA-03 — Short answer

**ID:** `U11-SA-03`  
**Unit / topic:** Pipeline observability and DORA delivery metrics  
**Level:** L3  
**Objective tested:** Explain a core concept in Pipeline observability and DORA delivery metrics.  
**Estimated time:** 4 min  
**Question type:** Short answer

**Question prompt**

Why is unknown telemetry not the same as zero deployments?

**Model answer**

Unknown means observation is incomplete; zero means a complete window recorded no events.

**Reasoning / explanation**

The answer links a definition to its operational consequence and names the relevant boundary.

**Common wrong answers or failure modes**

Treating two different lifecycle concepts as synonyms; ignoring failure modes; assuming a label or green status proves correctness.

**Why a tempting wrong answer is wrong**

The tempting shortcut optimizes one local concern but does not establish the stated guarantee.

**Scoring rubric / acceptance criteria**

3 points: 1 for accurate concept, 1 for consequence, 1 for example or limitation.


### Multiple choice


### U11-MCQ-01 — Multiple choice

**ID:** `U11-MCQ-01`  
**Unit / topic:** Pipeline observability and DORA delivery metrics — ['DORA metric definitions and anti-gaming', 'Queue/execution duration, flake/retry rate, pipeline SLOs', 'Missing telemetry, correlation IDs, percentiles and coverage']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For DORA metric definitions and anti-gaming, which choice best satisfies production correctness?

**Options**

- **A.** Option A: Metrics depend on context and definitions; individual rankings incentivize gaming and obscure systemic constraints.
- **B.** Option B: Use an unreviewed mutable reference.
- **C.** Option C: Assume a successful workflow proves production outcome.
- **D.** Option D: Skip the gate to improve speed.

**Correct answer:** A

**Why the correct option is best:** Metrics depend on context and definitions; individual rankings incentivize gaming and obscure systemic constraints.

**Distractor analysis**

- **B is incorrect:** Option B: Use an unreviewed mutable reference. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Assume a successful workflow proves production outcome. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Skip the gate to improve speed. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Metrics depend on context and definitions; individual rankings incentivize gaming and obscure systemic constraints.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U11-MCQ-02 — Multiple choice

**ID:** `U11-MCQ-02`  
**Unit / topic:** Pipeline observability and DORA delivery metrics — ['DORA metric definitions and anti-gaming', 'Queue/execution duration, flake/retry rate, pipeline SLOs', 'Missing telemetry, correlation IDs, percentiles and coverage']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Queue/execution duration, flake/retry rate, pipeline SLOs, which control best handles the stated risk?

**Options**

- **A.** Option A: Serialize every job without examining dependencies.
- **B.** Option B: Queue time is waiting for eligible capacity; execution time is running work after start.
- **C.** Option C: Use a cache as the authoritative release copy.
- **D.** Option D: Treat missing telemetry as a zero value.

**Correct answer:** B

**Why the correct option is best:** Queue time is waiting for eligible capacity; execution time is running work after start.

**Distractor analysis**

- **A is incorrect:** Option A: Serialize every job without examining dependencies. This fails because it does not satisfy the stated safety/correctness condition.
- **C is incorrect:** Option C: Use a cache as the authoritative release copy. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: Treat missing telemetry as a zero value. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Queue time is waiting for eligible capacity; execution time is running work after start.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### U11-MCQ-03 — Multiple choice

**ID:** `U11-MCQ-03`  
**Unit / topic:** Pipeline observability and DORA delivery metrics — ['DORA metric definitions and anti-gaming', 'Queue/execution duration, flake/retry rate, pipeline SLOs', 'Missing telemetry, correlation IDs, percentiles and coverage']  
**Level:** L2  
**Objective tested:** Select a safe, technically correct approach under stated assumptions.  
**Estimated time:** 3 min  
**Question type:** Multiple choice

**Question prompt**

For Missing telemetry, correlation IDs, percentiles and coverage, which evidence should be required?

**Options**

- **A.** Option A: A mutable label alone.
- **B.** Option B: A successful rerun without first-attempt metrics.
- **C.** Option C: Unknown means observation is incomplete; zero means a complete window recorded no events.
- **D.** Option D: A local simulation as proof of remote enforcement.

**Correct answer:** C

**Why the correct option is best:** Unknown means observation is incomplete; zero means a complete window recorded no events.

**Distractor analysis**

- **A is incorrect:** Option A: A mutable label alone. This fails because it does not satisfy the stated safety/correctness condition.
- **B is incorrect:** Option B: A successful rerun without first-attempt metrics. This fails because it does not satisfy the stated safety/correctness condition.
- **D is incorrect:** Option D: A local simulation as proof of remote enforcement. This fails because it does not satisfy the stated safety/correctness condition.

**Reasoning / explanation**

Unknown means observation is incomplete; zero means a complete window recorded no events.

**Common wrong answers or failure modes**

Selecting an option based only on convenience, green status, or speed while ignoring trust boundaries or evidence.

**Why a tempting wrong answer is wrong**

A safe answer must satisfy the full scenario, not only one local objective.

**Scoring rubric / acceptance criteria**

2 points: 1 for the correct option and 1 for explaining the governing principle.


### Configuration interpretation or output reading


### U11-CFG-01 — Configuration/output interpretation

**ID:** `U11-CFG-01`  
**Unit / topic:** Pipeline observability and DORA delivery metrics  
**Level:** L2  
**Objective tested:** Interpret configuration and identify missing evidence for Pipeline observability and DORA delivery metrics.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret the following pipeline fragment. Identify the missing safety/correctness condition.

```yaml
jobs:
  validate:
    steps: [{run: "pytest"}]
  publish:
    steps: [{run: "publish dist/*"}]
```

**Model answer**

The publish job must depend on successful validation and consume the exact artifact produced by the build. Add explicit dependencies, trusted release conditions, bounded permissions, and immutable artifact identity.

**Reasoning / explanation**

File order does not establish a dependency; verify the actual DAG and failure behavior.

**Common wrong answers or failure modes**

Assuming publish runs after validate because it appears later in YAML.

**Why a tempting wrong answer is wrong**

Use a linter and private test repository; test success, failure, and skipped prerequisite cases.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### U11-CFG-02 — Configuration/output interpretation

**ID:** `U11-CFG-02`  
**Unit / topic:** Pipeline observability and DORA delivery metrics  
**Level:** L3  
**Objective tested:** Interpret configuration and identify missing evidence for Pipeline observability and DORA delivery metrics.  
**Estimated time:** 5 min  
**Question type:** Configuration/output interpretation

**Question prompt**

Interpret this synthetic metric/config output.

```yaml
queue_p95_minutes: 9
execution_p50_minutes: 4
missing_events: 7
reported_failures: 0
```

**Model answer**

Queue delay and execution duration are different signals. Missing events make the failure count incomplete; report coverage/unknown rather than claiming zero failures. Investigate eligible runner capacity and collector errors.

**Reasoning / explanation**

A single aggregate duration cannot identify the bottleneck, and missing observations are not zero.

**Common wrong answers or failure modes**

Assuming the system is healthy because the reported failure count is zero.

**Why a tempting wrong answer is wrong**

Reconcile with raw events and test a synthetic collection gap.

**Scoring rubric / acceptance criteria**

3 points: 1 for interpretation, 1 for missing condition, 1 for validation. Validate with a linter and a private test repository.


### Pipeline/configuration review


### U11-REV-01 — Configuration review

**ID:** `U11-REV-01`  
**Unit / topic:** Pipeline observability and DORA delivery metrics  
**Level:** L3  
**Objective tested:** Find and fix at least three independent defects in Pipeline observability and DORA delivery metrics.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three defects and propose a patch.

```yaml
permissions: write-all
cache: dist/
release_tag: latest
run: publish dist/*
```

**Model answer**

Defects: (1) broad permissions; (2) cache used as authoritative artifact handoff; (3) mutable tag without digest; (4) no explicit trusted-ref gate; (5) no checksum/manifest validation. Narrow permissions, publish only from a trusted release context, hand off the exact artifact, record digest/hash, and add a validation gate.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U11-REV-02 — Configuration review

**ID:** `U11-REV-02`  
**Unit / topic:** Pipeline observability and DORA delivery metrics  
**Level:** L2  
**Objective tested:** Find and fix at least three independent defects in Pipeline observability and DORA delivery metrics.  
**Estimated time:** 8 min  
**Question type:** Configuration review

**Question prompt**

Find at least three independent defects.

```yaml
on: pull_request_target
runs-on: self-hosted
uses: actions/checkout@v4
run: echo $TOKEN
```

**Model answer**

Defects: (1) privileged event context may execute untrusted code; (2) sensitive persistent runner; (3) action not pinned to full SHA; (4) token may be printed/exposed; (5) no least-privilege permissions. Use a restricted PR event on isolated runners, avoid secrets, pin reviewed actions, and scope permissions.

**Reasoning / explanation**

Trace each defect to root cause and operational impact; correct the trust boundary and validate failure cases.

**Common wrong answers or failure modes**

Fixing only one visible defect; accepting a green status without inspecting what was executed.

**Why a tempting wrong answer is wrong**

A valid correction must preserve required checks, artifact integrity, and least privilege.

**Scoring rubric / acceptance criteria**

8 points: up to 4 for independent defects and impacts, 2 for correction, 1 for validation, 1 for version/security caveat. Include a numbered defect list and test in a private repo; exact platform behavior is [VERIFY].


### U11-INC-01 — Incident scenario

**ID:** `U11-INC-01`  
**Unit / topic:** Pipeline observability and DORA delivery metrics  
**Level:** L4  
**Objective tested:** Diagnose an incident relevant to Pipeline observability and DORA delivery metrics and define safe recovery.  
**Estimated time:** 12 min  
**Question type:** Incident scenario

**Question prompt**

A pipeline change coincides with a reliability regression. Available evidence is partial; a retry or green aggregate status may hide the underlying problem. Give symptom → hypotheses → tests → likely cause → mitigation → prevention.

Initial hypotheses: configuration regression, capacity/provider issue, trust-boundary issue, or incomplete telemetry.

**Model answer**

Symptoms: a recent change increased pipeline failures/duration, and the current dashboard is incomplete. Diagnose by inspecting event/runner/job logs, comparing queue vs execution time, reproducing with cache disabled or tests isolated, and checking the relevant dependency/rules/credential boundary. Likely causes remain hypotheses until evidence distinguishes them. Mitigate safely: stop unsafe publishing/deployment, preserve logs, revoke exposed credentials if applicable, and restore only required gates. Prevent with a regression test, explicit ownership, and monitoring. Evidence that would change the conclusion includes a provider-wide incident, a complete independent event log, or reproduction outside CI.

**Reasoning / explanation**

Use the order: contain immediate risk, preserve evidence, discriminate hypotheses, remediate, verify, and record follow-up.

**Common wrong answers or failure modes**

Blind retries, disabling required gates, or changing multiple variables before collecting evidence.

**Why a tempting wrong answer is wrong**

The correlation does not prove the new change caused the incident; evidence must discriminate alternatives.

**Scoring rubric / acceptance criteria**

5 points: symptoms/hypotheses, diagnostic sequence, safe mitigation, prevention, verification, and evidence that could change the conclusion.


### U11-DES-01 — Design with rubric

**ID:** `U11-DES-01`  
**Unit / topic:** Pipeline observability and DORA delivery metrics  
**Level:** L4  
**Objective tested:** Design a production-aware Pipeline observability and DORA delivery metrics approach under zero-budget constraints.  
**Estimated time:** 18 min  
**Question type:** Design with rubric

**Question prompt**

Dashboard duration improves while incidents rise and the collector hit API rate limits. Reconstruct valid metrics and communicate uncertainty.

Deliver a diagram or configuration outline, dependency/ownership map, security controls, acceptance criteria, and verification plan. State assumptions and distinguish M02 scope from forward references.

**Model answer**

Design should satisfy: explicit gates; minimal permissions; immutable artifact/evidence where relevant; reproducible validation; failure handling; rollback/recovery; measurable operational outcomes. Compare at least one alternative and explain why it is less suitable under the stated constraints.

**Reasoning / explanation**

A good design documents assumptions, risks, trade-offs, owner, and testable acceptance criteria.

**Common wrong answers or failure modes**

Optimizing speed alone, relying on mutable identifiers, or claiming remote controls are proven by a local simulation.

**Why a tempting wrong answer is wrong**

The best design is not a single rigid topology; it must satisfy mandatory safety and correctness requirements.

**Scoring rubric / acceptance criteria**

10 points: architecture 2, correctness/gates 2, security 2, reliability/rollback 1, measurement 1, trade-offs/clarity 2.


## Cross-unit integration questions


### XINT-01 — Cross-unit integration scenario

**ID:** `XINT-01`  
**Unit / topic:** DAG for API, ETL and ML  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve dag for api, etl and ml.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** DAG for API, ETL and ML. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Design fan-out/fan-in; keep lint and unit tests independent, add data-contract/ML gates, build and scan candidate, publish once, record digest, then request deployment.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U01,U04,U06,U07. **Safety/trade-off:** Do not bypass gates; CI success is not live rollout proof.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-02 — Cross-unit integration scenario

**ID:** `XINT-02`  
**Unit / topic:** Path-filtered required check pending  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve path-filtered required check pending.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Path-filtered required check pending. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Inspect skipped workflow/status; add stable aggregate gate and tested affected-component classifier; test docs, root config, shared library, merge queue.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U02,U05,U06. **Safety/trade-off:** Do not remove branch protection or equate unknown affected set with no tests.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-03 — Cross-unit integration scenario

**ID:** `XINT-03`  
**Unit / topic:** Cold-build dependency failure  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve cold-build dependency failure.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Cold-build dependency failure. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Reproduce without cache, inspect lockfile/install inventory, fix declaration, invalidate incompatible cache, require cold-build correctness.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U04,U06,U07. **Safety/trade-off:** Cache is never the sole source of release output.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-04 — Cross-unit integration scenario

**ID:** `XINT-04`  
**Unit / topic:** Flaky test corrupts shared state  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve flaky test corrupts shared state.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Flaky test corrupts shared state. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Measure first-attempt flake rate, randomize order, isolate fixtures/data, bound retries, quarantine with owner and expiry.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U04,U06,U11. **Safety/trade-off:** A retry passing does not erase the first failure.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-05 — Cross-unit integration scenario

**ID:** `XINT-05`  
**Unit / topic:** Staging digest differs from build  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve staging digest differs from build.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Staging digest differs from build. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Freeze promotion, independently resolve digest, inspect rebuild/tag mutation, restore only verified artifact and preserve evidence.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U01,U07,U09. **Safety/trade-off:** Do not edit the manifest to match unknown content.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-06 — Cross-unit integration scenario

**ID:** `XINT-06`  
**Unit / topic:** Tag exists, publish failed  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve tag exists, publish failed.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Tag exists, publish failed. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Inspect tag target and registry state, verify exact artifact hash, resume only missing idempotent step; never force-move tag.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U07,U08,U09. **Safety/trade-off:** Partial external state must be reconciled.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-07 — Cross-unit integration scenario

**ID:** `XINT-07`  
**Unit / topic:** Approval bypass via token  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve approval bypass via token.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Approval bypass via token. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Stop promotion, preserve audit logs, identify identity and scope, revoke/narrow token, verify deployed digest, test negative cases.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U02,U09,U10. **Safety/trade-off:** Check whether external approval evidence exists before concluding.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-08 — Cross-unit integration scenario

**ID:** `XINT-08`  
**Unit / topic:** Fork PR reaches self-hosted runner  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve fork pr reaches self-hosted runner.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Fork PR reaches self-hosted runner. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Disable route, inspect trigger/ref/runner group, isolate host, revoke exposed credentials, rebuild if compromise plausible.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U02,U09,U10. **Safety/trade-off:** Labels are not isolation; do not test with exploit payloads.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-09 — Cross-unit integration scenario

**ID:** `XINT-09`  
**Unit / topic:** Reusable workflow requests write-all  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve reusable workflow requests write-all.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Reusable workflow requests write-all. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Split read-only validation and privileged publish/deploy workflows; constrain inputs and permissions; pin dependencies and verify caller behavior.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U02,U07,U09. **Safety/trade-off:** Central reuse should not centralize broad credentials.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-10 — Cross-unit integration scenario

**ID:** `XINT-10`  
**Unit / topic:** GitHub/GitLab matrix differs  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve github/gitlab matrix differs.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** GitHub/GitLab matrix differs. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Create event/condition truth table, inspect pipeline creation vs job inclusion, lint/simulate both, maintain stable gate.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U02,U03,U05. **Safety/trade-off:** Syntax and semantics require platform-specific validation [VERIFY].

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-11 — Cross-unit integration scenario

**ID:** `XINT-11`  
**Unit / topic:** Queue grows; runtime stable  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve queue grows; runtime stable.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Queue grows; runtime stable. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Segment queue by runner group and labels, inspect capacity/provisioning/provider health, scale only after confirming eligible-capacity bottleneck.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U04,U10,U11. **Safety/trade-off:** Do not increase timeout or weaken isolation as a capacity fix.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-12 — Cross-unit integration scenario

**ID:** `XINT-12`  
**Unit / topic:** Frequency and failure rate rise  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve frequency and failure rate rise.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Frequency and failure rate rise. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Recompute using production deployment events, correlate failures, segment by service/cohort, inspect missingness and change size.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U01,U06,U09,U11. **Safety/trade-off:** Do not use individual rankings or throughput alone.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-13 — Cross-unit integration scenario

**ID:** `XINT-13`  
**Unit / topic:** Incident has no deployment ID  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve incident has no deployment id.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Incident has no deployment ID. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Reconstruct from digest, commit, timestamps, controller logs and manifest; add stable correlation ID across request and rollout events.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U07,U09,U11. **Safety/trade-off:** A commit may correspond to multiple builds/deployments.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-14 — Cross-unit integration scenario

**ID:** `XINT-14`  
**Unit / topic:** Docs-only classifier misses root config  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve docs-only classifier misses root config.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Docs-only classifier misses root config. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Fail closed on unclassified files, update dependency mapping, run affected validation, add fixtures and keep aggregate gate.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U05,U06. **Safety/trade-off:** Classification failure must not mean no impact.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-15 — Cross-unit integration scenario

**ID:** `XINT-15`  
**Unit / topic:** Collector rate-limited; zeros reported  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve collector rate-limited; zeros reported.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Collector rate-limited; zeros reported. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Mark coverage incomplete, report unknown, backoff/retry/backfill safely and reconcile raw events.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U02,U11. **Safety/trade-off:** Never interpret API failure as zero events; rate details [VERIFY].

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-16 — Cross-unit integration scenario

**ID:** `XINT-16`  
**Unit / topic:** Checksum differs at release  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve checksum differs at release.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Checksum differs at release. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Freeze promotion, hash downloaded exact bytes, inspect rebuild/overwrite/manifest provenance, publish only verified bytes.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U07,U08,U09. **Safety/trade-off:** Version string alone does not identify content.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-17 — Cross-unit integration scenario

**ID:** `XINT-17`  
**Unit / topic:** Static token exposed on runner  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve static token exposed on runner.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** Static token exposed on runner. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Isolate runner, preserve evidence, revoke/rotate credentials, inspect audit/egress, rebuild from trusted image, assess downstream artifacts.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U02,U07,U10. **Safety/trade-off:** Workspace cleanup does not restore host trust.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-18 — Cross-unit integration scenario

**ID:** `XINT-18`  
**Unit / topic:** ML metric noisy on tiny sample  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve ml metric noisy on tiny sample.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** ML metric noisy on tiny sample. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Verify dataset version, metric, sample size, class balance, seed/config and uncertainty; define tolerance before gate decision.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U01,U06,U11. **Safety/trade-off:** Do not reseed until the metric passes.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-19 — Cross-unit integration scenario

**ID:** `XINT-19`  
**Unit / topic:** GitOps rollout fails after CI green  
**Level:** L3  
**Objective tested:** Integrate the relevant M02 units to solve gitops rollout fails after ci green.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** GitOps rollout fails after CI green. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Separate artifact publish and deployment request from live rollout; correlate digest/request with controller status and apply M08 runbook.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U01,U07,U09,U11. **Safety/trade-off:** Full GitOps reconciliation is a forward reference, not an M02 prerequisite.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


### XINT-20 — Cross-unit integration scenario

**ID:** `XINT-20`  
**Unit / topic:** SLO breach: provider or repo config  
**Level:** L4  
**Objective tested:** Integrate the relevant M02 units to solve slo breach: provider or repo config.  
**Estimated time:** 12 min  
**Question type:** Cross-unit integration scenario

**Question prompt**

**Scenario:** SLO breach: provider or repo config. Evidence is incomplete and a production delivery decision is waiting.

**Required:** state the first three investigative steps, identify the trust boundary, propose a safe mitigation, and list verification evidence.

**Model answer**

Compare affected repositories, queue/execution, recent changes, runner labels and provider evidence; communicate scope/confidence and mitigate separately.

**Reasoning / explanation**

Investigate before asserting cause; distinguish CI build/test success from production rollout; preserve artifacts, logs, and audit evidence.

**Common wrong answers or failure modes**

Blind retries, mutable tags, broad tokens, missing-data-as-zero, or removing required checks.

**Why a tempting wrong answer is wrong**

The shortcut can make the dashboard or workflow green without restoring the actual safety property.

**Scoring rubric / acceptance criteria**

**Units involved:** U04,U10,U11. **Safety/trade-off:** Many queued jobs alone do not prove provider outage.

5 points: 1 for evidence-led triage, 1 for correct cross-unit reasoning, 1 for safe mitigation, 1 for prevention/verification, 1 for alternative hypothesis or trade-off.


## Design-review whiteboard prompts

These eight prompts are additional to the 152 scored questions.


### DR-01 — CI/CD DAG for data/ML monorepo

**Scenario and constraints:** FastAPI, ETL, model scoring, shared library and docs; p95 feedback target under 15 minutes; no required gate may be skipped.

**Diagram/artifacts required:** DAG, dependency graph, path-to-test matrix, artifact manifest, failure policy.

**Design questions:** What is the minimum safe design? Which gates are parallel/dependent? How are identity, secrets, rollback, and evidence preserved? What metric proves improvement?

**Expected considerations:** Fan-out independent checks; shared-library dependency mapping; aggregate gate; data/ML gates; digest promotion; rollback.

**Scoring rubric:** Architecture 2; correctness 2; security 2; reliability 2; cost/operability 1; clarity 1.

**Common omissions:** Missing a trust boundary, denominator, rollback target, edge-case test, or owner makes the design unsafe or inoperable.

**Reviewer follow-up:** How do root config and merge queues affect the classifier?


### DR-02 — Reusable workflows and portability

**Scenario and constraints:** Three repositories share validation and publishing; GitHub Actions is primary and GitLab is taught for transfer.

**Diagram/artifacts required:** Workflow interface, permission matrix, GitLab equivalent-intent sketch, portability table.

**Design questions:** What is the minimum safe design? Which gates are parallel/dependent? How are identity, secrets, rollback, and evidence preserved? What metric proves improvement?

**Expected considerations:** Distinguish reusable workflow from composite action; narrow permissions; document semantic differences and [VERIFY] features.

**Scoring rubric:** Architecture 2; interface 2; permissions 2; portability 2; verification 1; trade-offs 1.

**Common omissions:** Missing a trust boundary, denominator, rollback target, edge-case test, or owner makes the design unsafe or inoperable.

**Reviewer follow-up:** Who owns workflow upgrades and compatibility?


### DR-03 — Cache and flake remediation

**Scenario and constraints:** Warm builds pass; cold builds fail; integration flake rate is 8%; pipeline SLO is breached.

**Diagram/artifacts required:** Benchmark plan, cache key policy, flake dashboard, quarantine register.

**Design questions:** What is the minimum safe design? Which gates are parallel/dependent? How are identity, secrets, rollback, and evidence preserved? What metric proves improvement?

**Expected considerations:** Cold build correctness; lockfile/runtime keys; isolated test data; owner/expiry; first-attempt metrics; queue vs runtime.

**Scoring rubric:** Measurement 2; cache integrity 2; test diagnosis 2; gates 2; operations 1; clarity 1.

**Common omissions:** Missing a trust boundary, denominator, rollback target, edge-case test, or owner makes the design unsafe or inoperable.

**Reviewer follow-up:** How distinguish cache poisoning from undeclared dependency?


### DR-04 — Artifact repository and promotion

**Scenario and constraints:** Python wheel and container image must move through test/staging/production with no production credentials in the lab.

**Diagram/artifacts required:** Lifecycle diagram, manifest schema, hash/digest checks, registry access policy.

**Design questions:** What is the minimum safe design? Which gates are parallel/dependent? How are identity, secrets, rollback, and evidence preserved? What metric proves improvement?

**Expected considerations:** Build once, verify exact bytes, trusted publish, immutable identity, retention, rollback.

**Scoring rubric:** Lifecycle 2; integrity 2; access 2; promotion 2; retention 1; clarity 1.

**Common omissions:** Missing a trust boundary, denominator, rollback target, edge-case test, or owner makes the design unsafe or inoperable.

**Reviewer follow-up:** What proves staging consumed the tested artifact?


### DR-05 — Branch protection and approvals

**Scenario and constraints:** A broad token bypassed a nominal approval; emergency releases must remain auditable.

**Diagram/artifacts required:** Branch/environment matrix, roles, negative tests, bypass runbook, evidence manifest.

**Design questions:** What is the minimum safe design? Which gates are parallel/dependent? How are identity, secrets, rollback, and evidence preserved? What metric proves improvement?

**Expected considerations:** Required checks/reviews, scoped tokens, remote setting verification, audited break-glass path.

**Scoring rubric:** Policy 2; duties 2; least privilege 2; negative tests 2; audit 2.

**Common omissions:** Missing a trust boundary, denominator, rollback target, edge-case test, or owner makes the design unsafe or inoperable.

**Reviewer follow-up:** How prove remote enforcement rather than documentation?


### DR-06 — Ephemeral runner fleet

**Scenario and constraints:** Trusted jobs need private network; public-fork code must never run on the fleet.

**Diagram/artifacts required:** Trust diagram, lifecycle, scaling signals, egress/identity policy, incident runbook.

**Design questions:** What is the minimum safe design? Which gates are parallel/dependent? How are identity, secrets, rollback, and evidence preserved? What metric proves improvement?

**Expected considerations:** Ephemeral isolation, restricted egress, short-lived credentials where supported, patching, queue-driven scaling.

**Scoring rubric:** Trust 2; isolation 2; identity/network 2; scaling 2; response 2.

**Common omissions:** Missing a trust boundary, denominator, rollback target, edge-case test, or owner makes the design unsafe or inoperable.

**Reviewer follow-up:** What can still be exposed during an active job?


### DR-07 — DORA and pipeline telemetry

**Scenario and constraints:** Leadership wants trends; API collection misses events; individual ranking is prohibited.

**Diagram/artifacts required:** Event schema, source map, correlation IDs, SLOs, coverage panel, privacy/retention policy.

**Design questions:** What is the minimum safe design? Which gates are parallel/dependent? How are identity, secrets, rollback, and evidence preserved? What metric proves improvement?

**Expected considerations:** Define deployment events, expose missingness, use percentiles/cohorts, avoid personal scorecards.

**Scoring rubric:** Definitions 2; data quality 2; SLO 2; privacy 1; failure handling 1; anti-gaming 2.

**Common omissions:** Missing a trust boundary, denominator, rollback target, edge-case test, or owner makes the design unsafe or inoperable.

**Reviewer follow-up:** How avoid treating collector outage as zero failures?


### DR-08 — End-to-end capstone

**Scenario and constraints:** FastAPI, ETL and ML evaluation move from commit to verified artifact and deployment handoff on free/laptop tools.

**Diagram/artifacts required:** Architecture, pipeline, test evidence, manifest, release plan, rollback runbook, dashboard, risk register.

**Design questions:** What is the minimum safe design? Which gates are parallel/dependent? How are identity, secrets, rollback, and evidence preserved? What metric proves improvement?

**Expected considerations:** Lint/tests/contracts/build/scan/publish/promotion, digest identity, secure runner, idempotent release, observability; stop at handoff.

**Scoring rubric:** Architecture 2; correctness 2; security 2; release 1; SRE 1; cost 1; evidence 1.

**Common omissions:** Missing a trust boundary, denominator, rollback target, edge-case test, or owner makes the design unsafe or inoperable.

**Reviewer follow-up:** What failures will you inject after publish, during promotion, and during collection?


## Answer-key consistency and audit report

| Audit pass | Status | Checked | Open items |
|---|---|---|---|
| 1. Roadmap completeness | PASS WITH OPEN ITEMS | All 11 unit scopes and integration clusters are represented. | Cross-check against every lesson; not all lesson files were independently re-read. |
| 2. Count and format | PASS | Intended 132 unit questions + 20 integration = 152; eight additional DR prompts. | Re-run counts after manual edits. |
| 3. Answer correctness | PASS WITH OPEN ITEMS | Answers, rationale, distractor explanations and rubrics are included. | Human SME peer review not performed. |
| 4. Technical syntax | PASS WITH OPEN ITEMS | Representative snippets reviewed conceptually; mutable details marked [VERIFY]. | No workflow parser, linter, script, or API was executed. |
| 5. Security | PASS WITH OPEN ITEMS | Synthetic values and defensive scenarios; no real secrets or exploit payloads. | Remote controls need private-repository validation. |
| 6. Fabrication scan | PASS WITH OPEN ITEMS | No docs are claimed as live-consulted; no pricing/quotas asserted. | Check current official documentation before production use. |
| 7. Pedagogy | PASS | L1–L4, scenarios, wrong-answer analysis, scoring and remediation are present. | Time estimates are instructional estimates. |
| 8. Cross-consistency | PASS WITH OPEN ITEMS | Intended ID scheme and inventory align. | Automated structural check is recommended after edits. |
| 9. Adversarial review | PASS WITH OPEN ITEMS | Missing evidence, mutable tags, skipped gates, trust boundaries and metric denominators are addressed. | Instructor should retain scenario assumptions when adapting questions. |
| 10. Scope/output | PASS | Only this requested standalone Markdown artifact is intended. | Repository destination was not mounted; no repository file was changed. |

### Inventory reconciliation

- Units: 11 × 12 = 132 (each: 3 SA, 3 MCQ, 2 CFG, 2 REV, 1 INC, 1 DES).
- Cross-unit integration: 20 (`XINT-01` through `XINT-20`).
- Total scored questions: **152**. Additional whiteboards: 8 (`DR-01` through `DR-08`).
- Per-question MCQs have exactly four options and individual explanations for all distractors. Reviews contain at least three independently identifiable defects and a correction/validation approach.

### Sources and verification notes

Inspected: supplied `Pasted markdown(20261024-134822).md`; available `PROMPT-CI-CD-Pipeline-Engineering.md` syllabus-generation prompt; and `Roadmap_ptree(20261024-094751).md` for tree context. No live official documentation was consulted and no commands, workflows, tests, APIs, or labs were executed.

Before production use, verify current GitHub Actions workflow syntax/events/permissions/reusable workflows/actions pinning/runners/artifacts/caches; GitLab CI rules/templates/artifacts/cache/runners/OIDC; pytest JUnit/coverage integration; package publishing and registry authentication; SemVer 2.0.0; current official DORA definitions; Prometheus/OpenTelemetry integration; and branch/environment protection/bypass behavior. Mark version-sensitive features `[VERIFY]`.

M01 image/digest concepts are consumed here. Full Kubernetes operations, Helm/Kustomize, GitOps reconciliation, advanced supply-chain provenance/signing, and organization-wide FinOps/platform engineering are forward references, not prerequisites for this bank.
