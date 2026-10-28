# Practice Questions — Site Reliability Engineering and Incident Management

**Target path:** `10-Site-Reliability-Engineering-and-Incident-Management/practice-questions.md`  
**Module:** Stage 2E — Production DevOps & Platform Engineering / Unit 10 — Site Reliability Engineering and Incident Management

> **Source limitation:** The authoritative SRE syllabus/prompt and a local roadmap copy were inspected. Unit 2–11 chapter artifacts were available by filename; Unit 1 chapter, M10 README, M10 Projects files, and a writable repository checkout were not available for direct inspection. Unit 1 follows the detailed syllabus embedded in the prompt. This is a standalone artifact; no repository modification is claimed.

## Table of contents

- [Unit 1 — Service-level indicators, objectives, and error budgets](#unit-1---service-level-indicators-objectives-and-error-budgets)
- [Unit 2 — Reliability targets for batch, streaming, and inference](#unit-2---reliability-targets-for-batch-streaming-and-inference)
- [Unit 3 — Alert quality, noise reduction, and escalation policies](#unit-3---alert-quality-noise-reduction-and-escalation-policies)
- [Unit 4 — Incident severity, roles, and command structure](#unit-4---incident-severity-roles-and-command-structure)
- [Unit 5 — Production triage and blameless postmortems](#unit-5---production-triage-and-blameless-postmortems)
- [Unit 6 — Capacity-related failures and cascading outages](#unit-6---capacity-related-failures-and-cascading-outages)
- [Unit 7 — Toil reduction and operational automation](#unit-7---toil-reduction-and-operational-automation)
- [Unit 8 — Runbook design and operational readiness reviews](#unit-8---runbook-design-and-operational-readiness-reviews)
- [Unit 9 — Error-budget policies and release freezes](#unit-9---error-budget-policies-and-release-freezes)
- [Unit 10 — On-call rotations, handoffs, and sustainable paging](#unit-10---on-call-rotations-handoffs-and-sustainable-paging)
- [Unit 11 — DORA metrics and engineering performance measurement](#unit-11---dora-metrics-and-engineering-performance-measurement)
- [Cross-unit integration scenarios](#cross-unit-integration-scenarios)
- [Design-review whiteboard prompts](#design-review-whiteboard-prompts)
- [Scoring and remediation](#scoring-and-remediation)
- [Coverage and authenticity audit](#coverage-and-authenticity-audit)
- [Source and assumption register](#source-and-assumption-register)

## How to use this bank
Answer before reading the model answer. Treat all numerical data as synthetic. Use disposable, explicitly scoped lab environments only. Never run destructive actions against production or shared systems. Passing is a learning signal, not proof of production readiness.

### Learning levels
- **L1:** foundations, terminology and simple interpretation.
- **L2:** practitioner calculations, artifact reading and routine repair.
- **L3:** interacting failures, diagnosis, uncertainty and trade-offs.
- **L4:** policy, governance, ownership, incentives and organizational design.

## Unit 1 — Service-level indicators, objectives, and error budgets
**Scope:** Unit 1. **ID range:** `U01-Q001`–`U01-Q014`.

### U01-Q001 — Conceptual short answer

- **Question ID:** `U01-Q001`
- **Scope:** Unit 1
- **Level:** L1
- **Learning objective tested:** user-centric SLI boundaries
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Explain user-centric SLI boundaries and why it matters operationally.

**Model answer**

User-centric sli boundaries must be defined at an observable boundary, connected to user or operator impact, owned, and used to guide a decision. A definition without measurement or action is not operationally useful.

**Common wrong answer(s) / failure modes**

Reciting a label without explaining its boundary or decision use.

**Why the wrong answer is wrong**

The question tests application of the concept, not vocabulary alone.

**Evidence / assumption note**

Illustrative course-level question; align implementation details to the local chapter.

### U01-Q002 — Conceptual short answer

- **Question ID:** `U01-Q002`
- **Scope:** Unit 1
- **Level:** L1
- **Learning objective tested:** good events and valid events
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Distinguish good events and valid events from a nearby signal or policy concept, and give one failure mode caused by confusing them.

**Model answer**

The concepts have different purposes. Define each one, show where it is measured or applied, and state how the confusion could conceal impact or create unsafe action.

**Common wrong answer(s) / failure modes**

Treating a proxy as proof of the desired outcome.

**Why the wrong answer is wrong**

A proxy may be useful, but it does not establish the user outcome without evidence.

**Evidence / assumption note**

Synthetic framing; use definitions supplied in the syllabus.

### U01-Q003 — Conceptual short answer

- **Question ID:** `U01-Q003`
- **Scope:** Unit 1
- **Level:** L2
- **Learning objective tested:** SLI versus SLO versus SLA
- **Estimated time:** 5 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

What evidence would you collect before changing a production policy related to SLI versus SLO versus SLA?

**Model answer**

Collect a baseline, validate data quality and event boundaries, identify owners and affected users, model likely failure modes, test the change in a disposable environment, define rollback and acceptance criteria, and review the trade-off with stakeholders.

**Common wrong answer(s) / failure modes**

Changing the threshold or policy based only on intuition.

**Why the wrong answer is wrong**

Without baseline and validation, the team cannot distinguish improvement from metric drift or shifted risk.

**Evidence / assumption note**

No live production change is required.

### U01-Q004 — Multiple choice

- **Question ID:** `U01-Q004`
- **Scope:** Unit 1
- **Level:** L1
- **Learning objective tested:** error-budget arithmetic
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which choice best operationalizes user-centric SLI boundaries?

- **A.** A measurable definition with a stated boundary, owner, evidence source, and decision rule.
- **B.** A vague statement that user-centric SLI boundaries should be “good”.
- **C.** A single resource metric with no user or operational interpretation.
- **D.** An undocumented threshold copied from another service.

**Model answer**

**Correct option: A.** The selected answer is measurable, owned and decision-relevant. **B is incorrect:** A vague statement that user-centric SLI boundaries should be “good”. **C is incorrect:** A single resource metric with no user or operational interpretation. **D is incorrect:** An undocumented threshold copied from another service.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U01-Q005 — Multiple choice

- **Question ID:** `U01-Q005`
- **Scope:** Unit 1
- **Level:** L1
- **Learning objective tested:** burn rate
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

What is the safest response when evidence for good events and valid events is missing or stale?

- **A.** Treat the state as unknown, validate the measurement path, and follow the documented fallback/exception policy.
- **B.** Assume the service is healthy because no failure was recorded.
- **C.** Silently replace missing values with zero.
- **D.** Disable the check until the next review.

**Model answer**

**Correct option: A.** Unknown evidence must not be represented as healthy by default. **B is incorrect:** Assume the service is healthy because no failure was recorded. **C is incorrect:** Silently replace missing values with zero. **D is incorrect:** Disable the check until the next review.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U01-Q006 — Multiple choice

- **Question ID:** `U01-Q006`
- **Scope:** Unit 1
- **Level:** L2
- **Learning objective tested:** missing telemetry
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which practice best reduces risk when applying SLI versus SLO versus SLA?

- **A.** Use explicit preconditions, scoped ownership, tests, rollback/abort conditions, and post-change verification.
- **B.** Apply a broad change to all services at once.
- **C.** Skip validation because the change is reversible in theory.
- **D.** Use an undocumented verbal override.

**Model answer**

**Correct option: A.** The selected answer makes scope, failure handling, and verification explicit. **B is incorrect:** Apply a broad change to all services at once. **C is incorrect:** Skip validation because the change is reversible in theory. **D is incorrect:** Use an undocumented verbal override.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U01-Q007 — Artifact interpretation

- **Question ID:** `U01-Q007`
- **Scope:** Unit 1
- **Level:** L2
- **Learning objective tested:** user-centric SLI boundaries
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

**Is this a good SLI/SLO?** Specification: “99.9% API uptime, measured from pod readiness over a calendar month; exclude all 4xx and planned maintenance; no named owner.” Identify the defects and propose a testable replacement.

**Model answer**

No. Pod readiness is not a user outcome; the target lacks a justified user journey and exact event denominator; excluding all 4xx can hide authentication/authorization regressions; planned-maintenance exclusions are undefined; owner and source are absent. Replace with a request-based SLI at an agreed user-relevant boundary, explicit client-error semantics and narrow approved exclusions, a stated window/source/owner, and linked budget policy. Test success, 5xx, auth regression, missing data, and traffic-collapse cases.

**Common wrong answer(s) / failure modes**

Accepting the specification because it contains a percentage or because pods are ready.

**Why the wrong answer is wrong**

A target is only useful if its events represent the user outcome and its exclusions cannot silently hide failures.

**Evidence / assumption note**

The 99.9% value is illustrative; objective selection requires stakeholder and historical evidence.

### U01-Q008 — Artifact interpretation

- **Question ID:** `U01-Q008`
- **Scope:** Unit 1
- **Level:** L2
- **Learning objective tested:** good events and valid events
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact B: pod uptime is used as a proxy for user success; exclusions are undocumented; no owner or window is named. Dashboard status is green, but no independent evidence is supplied.

**Model answer**

There are substantive defects: pod uptime is used as a proxy for user success; exclusions are undocumented; no owner or window is named. Repair with Measure valid user requests at a meaningful boundary, state exclusions/window/source/owner, treat missing telemetry as unknown, and link the objective to an explicit budget policy. Verify with a positive, negative, missing-data and boundary test.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U01-Q009 — Artifact interpretation

- **Question ID:** `U01-Q009`
- **Scope:** Unit 1
- **Level:** L3
- **Learning objective tested:** SLI versus SLO versus SLA
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact C: A service has 20,000 eligible events, 120 bad events, and an SLO of 99.5%.

**Model answer**

Allowed bad fraction = 1 − 0.995 = 0.005; allowed bad events = 20,000 × 0.005 = 100. Consumption = 120/100 = 120%; budget is exceeded by 20 bad events. Remaining budget is zero, with an overrun of 20 events.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U01-Q010 — Artifact review

- **Question ID:** `U01-Q010`
- **Scope:** Unit 1
- **Level:** L3
- **Learning objective tested:** SLI versus SLO versus SLA
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> pod uptime is used as a proxy for user success; exclusions are undocumented; no owner or window is named; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) pod uptime is used as a proxy for user success; exclusions are undocumented; no owner or window is named; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Measure valid user requests at a meaningful boundary, state exclusions/window/source/owner, treat missing telemetry as unknown, and link the objective to an explicit budget policy. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U01-Q011 — Artifact review

- **Question ID:** `U01-Q011`
- **Scope:** Unit 1
- **Level:** L3
- **Learning objective tested:** error-budget arithmetic
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> pod uptime is used as a proxy for user success; exclusions are undocumented; no owner or window is named; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) pod uptime is used as a proxy for user success; exclusions are undocumented; no owner or window is named; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Measure valid user requests at a meaningful boundary, state exclusions/window/source/owner, treat missing telemetry as unknown, and link the objective to an explicit budget policy. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U01-Q012 — Incident/triage scenario

- **Question ID:** `U01-Q012`
- **Scope:** Unit 1
- **Level:** L3
- **Learning objective tested:** Safe incident response
- **Estimated time:** 10 minutes
- **Question type:** Incident/triage scenario

**Prompt / artifact / scenario**

SLO remains green during traffic collapse because only requests reaching the server are counted.

**Model answer**

Use independent client/synthetic evidence, declare based on credible impact, mitigate, communicate, then fix the denominator and test missing-data behavior.

**Common wrong answer(s) / failure modes**

Wait for confirmed root cause before declaration or mitigation.

**Why the wrong answer is wrong**

The operational sequence is stabilize/mitigate first, diagnose second, fix third; communication and verification continue throughout.

**Evidence / assumption note**

Synthetic incident; apply the organization’s severity and escalation policy.

### U01-Q013 — Design question

- **Question ID:** `U01-Q013`
- **Scope:** Unit 1
- **Level:** L4
- **Learning objective tested:** Design a measurable, safe, auditable control
- **Estimated time:** 20 minutes
- **Question type:** Design question

**Prompt / artifact / scenario**

Design an operational control for user-centric SLI boundaries and low traffic and denominator bias. Include objective, event/data boundary, owner, safety limits, decision rights, failure behavior, rollback, verification, and review cadence.

**Model answer**

A strong design states the user/operational outcome, precise measurement and exclusions, owner, threshold rationale, missing-data behavior, safe scope, decision/override rights, rollback/abort conditions, and evidence-based acceptance. **10-point rubric:** outcome/definition 2; boundary and data quality 2; safety/rollback 2; ownership/governance 2; test evidence and review 2. Acceptable alternatives are context-dependent if their trade-offs are explicit. Common omissions: unowned controls, assumed-good missing data, no test or rollback.

**Common wrong answer(s) / failure modes**

A tool list without measurable outcomes, decision rights, or tests.

**Why the wrong answer is wrong**

A design must be testable, owned, and explicit about risk and alternatives.

**Evidence / assumption note**

Rubric and synthetic design assumptions are provided in the answer.

### U01-Q014 — Numeric/application

- **Question ID:** `U01-Q014`
- **Scope:** Unit 1
- **Level:** L2
- **Learning objective tested:** Apply the unit decision rule to supplied evidence
- **Estimated time:** 7 minutes
- **Question type:** Numeric/application

**Prompt / artifact / scenario**

**Compute the budget/burn rate.** A service has 20,000 eligible events in the window, 120 bad events, and an SLO of 99.5%. Compute the allowed bad-event budget, budget consumed, remaining budget, and burn rate using the same window and denominator.

**Model answer**

Allowed bad fraction = 1 − 0.995 = 0.005. Allowed bad events = 20,000 × 0.005 = 100. Observed bad events = 120. Budget consumed = 120/100 = 120%; the budget is exceeded by 20 bad events. Remaining budget is 0 events (−20 before clamping). Observed bad-event rate = 120/20,000 = 0.006 = 0.6%. Allowed bad-event rate = 1 − 0.995 = 0.005 = 0.5%. Burn rate = 0.6%/0.5% = 1.2×. The 120% budget-consumption figure and 1.2× burn rate answer different questions: total window consumption versus the rate relative to the allowed rate.

**Common wrong answer(s) / failure modes**

Treating the 99.5% objective as the allowed error fraction, or reporting 120/20,000 as budget consumed.

**Why the wrong answer is wrong**

Observed error ratio and fraction of budget consumed are different quantities; burn rate is a ratio of error rates.

**Evidence / assumption note**

Assumes 20,000 is the complete eligible denominator and no exclusions; values are synthetic.

## Unit 2 — Reliability targets for batch, streaming, and inference
**Scope:** Unit 2. **ID range:** `U02-Q001`–`U02-Q014`.

### U02-Q001 — Conceptual short answer

- **Question ID:** `U02-Q001`
- **Scope:** Unit 2
- **Level:** L1
- **Learning objective tested:** batch freshness/completeness/correctness
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Explain batch freshness/completeness/correctness and why it matters operationally.

**Model answer**

Batch freshness/completeness/correctness must be defined at an observable boundary, connected to user or operator impact, owned, and used to guide a decision. A definition without measurement or action is not operationally useful.

**Common wrong answer(s) / failure modes**

Reciting a label without explaining its boundary or decision use.

**Why the wrong answer is wrong**

The question tests application of the concept, not vocabulary alone.

**Evidence / assumption note**

Illustrative course-level question; align implementation details to the local chapter.

### U02-Q002 — Conceptual short answer

- **Question ID:** `U02-Q002`
- **Scope:** Unit 2
- **Level:** L1
- **Learning objective tested:** streaming time lag and replay
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Distinguish streaming time lag and replay from a nearby signal or policy concept, and give one failure mode caused by confusing them.

**Model answer**

The concepts have different purposes. Define each one, show where it is measured or applied, and state how the confusion could conceal impact or create unsafe action.

**Common wrong answer(s) / failure modes**

Treating a proxy as proof of the desired outcome.

**Why the wrong answer is wrong**

A proxy may be useful, but it does not establish the user outcome without evidence.

**Evidence / assumption note**

Synthetic framing; use definitions supplied in the syllabus.

### U02-Q003 — Conceptual short answer

- **Question ID:** `U02-Q003`
- **Scope:** Unit 2
- **Level:** L2
- **Learning objective tested:** inference latency and quality proxies
- **Estimated time:** 5 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

What evidence would you collect before changing a production policy related to inference latency and quality proxies?

**Model answer**

Collect a baseline, validate data quality and event boundaries, identify owners and affected users, model likely failure modes, test the change in a disposable environment, define rollback and acceptance criteria, and review the trade-off with stakeholders.

**Common wrong answer(s) / failure modes**

Changing the threshold or policy based only on intuition.

**Why the wrong answer is wrong**

Without baseline and validation, the team cannot distinguish improvement from metric drift or shifted risk.

**Evidence / assumption note**

No live production change is required.

### U02-Q004 — Multiple choice

- **Question ID:** `U02-Q004`
- **Scope:** Unit 2
- **Level:** L1
- **Learning objective tested:** event-based versus time-based SLIs
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which choice best operationalizes batch freshness/completeness/correctness?

- **A.** A measurable definition with a stated boundary, owner, evidence source, and decision rule.
- **B.** A vague statement that batch freshness/completeness/correctness should be “good”.
- **C.** A single resource metric with no user or operational interpretation.
- **D.** An undocumented threshold copied from another service.

**Model answer**

**Correct option: A.** The selected answer is measurable, owned and decision-relevant. **B is incorrect:** A vague statement that batch freshness/completeness/correctness should be “good”. **C is incorrect:** A single resource metric with no user or operational interpretation. **D is incorrect:** An undocumented threshold copied from another service.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U02-Q005 — Multiple choice

- **Question ID:** `U02-Q005`
- **Scope:** Unit 2
- **Level:** L1
- **Learning objective tested:** silent failure
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

What is the safest response when evidence for streaming time lag and replay is missing or stale?

- **A.** Treat the state as unknown, validate the measurement path, and follow the documented fallback/exception policy.
- **B.** Assume the service is healthy because no failure was recorded.
- **C.** Silently replace missing values with zero.
- **D.** Disable the check until the next review.

**Model answer**

**Correct option: A.** Unknown evidence must not be represented as healthy by default. **B is incorrect:** Assume the service is healthy because no failure was recorded. **C is incorrect:** Silently replace missing values with zero. **D is incorrect:** Disable the check until the next review.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U02-Q006 — Multiple choice

- **Question ID:** `U02-Q006`
- **Scope:** Unit 2
- **Level:** L2
- **Learning objective tested:** catch-up capacity
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which practice best reduces risk when applying inference latency and quality proxies?

- **A.** Use explicit preconditions, scoped ownership, tests, rollback/abort conditions, and post-change verification.
- **B.** Apply a broad change to all services at once.
- **C.** Skip validation because the change is reversible in theory.
- **D.** Use an undocumented verbal override.

**Model answer**

**Correct option: A.** The selected answer makes scope, failure handling, and verification explicit. **B is incorrect:** Apply a broad change to all services at once. **C is incorrect:** Skip validation because the change is reversible in theory. **D is incorrect:** Use an undocumented verbal override.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U02-Q007 — Artifact interpretation

- **Question ID:** `U02-Q007`
- **Scope:** Unit 2
- **Level:** L2
- **Learning objective tested:** batch freshness/completeness/correctness
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact A: freshness, completeness, correctness, time lag, inference latency/quality proxy. Source data are current and the service owner confirms the denominator.

**Model answer**

Interpret the artifact using the supplied definition: verify numerator and denominator, measurement window, exclusions, ownership and user impact. A green label alone does not prove the target is meaningful. Define workload-specific consumer outcomes and watermarks; add coverage/correctness checks and stale/dead-pipeline detection; verify recovery against output quality, not job status alone.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U02-Q008 — Artifact interpretation

- **Question ID:** `U02-Q008`
- **Scope:** Unit 2
- **Level:** L2
- **Learning objective tested:** streaming time lag and replay
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact B: job exit code is treated as data correctness; no-data is treated as success; stream lag is only measured as offset count. Dashboard status is green, but no independent evidence is supplied.

**Model answer**

There are substantive defects: job exit code is treated as data correctness; no-data is treated as success; stream lag is only measured as offset count. Repair with Define workload-specific consumer outcomes and watermarks; add coverage/correctness checks and stale/dead-pipeline detection; verify recovery against output quality, not job status alone. Verify with a positive, negative, missing-data and boundary test.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U02-Q009 — Artifact interpretation

- **Question ID:** `U02-Q009`
- **Scope:** Unit 2
- **Level:** L3
- **Learning objective tested:** inference latency and quality proxies
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact C: A stream receives 8,000 events/min and processes 10,000/min for 10 minutes while starting 20,000 events behind.

**Model answer**

Net catch-up = 10,000 − 8,000 = 2,000 events/min. In 10 minutes it clears 20,000 events, leaving zero lag if rates stay constant and no new burst occurs.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U02-Q010 — Artifact review

- **Question ID:** `U02-Q010`
- **Scope:** Unit 2
- **Level:** L3
- **Learning objective tested:** inference latency and quality proxies
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> job exit code is treated as data correctness; no-data is treated as success; stream lag is only measured as offset count; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) job exit code is treated as data correctness; no-data is treated as success; stream lag is only measured as offset count; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Define workload-specific consumer outcomes and watermarks; add coverage/correctness checks and stale/dead-pipeline detection; verify recovery against output quality, not job status alone. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U02-Q011 — Artifact review

- **Question ID:** `U02-Q011`
- **Scope:** Unit 2
- **Level:** L3
- **Learning objective tested:** event-based versus time-based SLIs
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> job exit code is treated as data correctness; no-data is treated as success; stream lag is only measured as offset count; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) job exit code is treated as data correctness; no-data is treated as success; stream lag is only measured as offset count; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Define workload-specific consumer outcomes and watermarks; add coverage/correctness checks and stale/dead-pipeline detection; verify recovery against output quality, not job status alone. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U02-Q012 — Incident/triage scenario

- **Question ID:** `U02-Q012`
- **Scope:** Unit 2
- **Level:** L3
- **Learning objective tested:** Safe incident response
- **Estimated time:** 10 minutes
- **Question type:** Incident/triage scenario

**Prompt / artifact / scenario**

A batch job exits 0 but emits zero rows despite an expected partition.

**Model answer**

Treat this as a possible correctness/completeness incident, protect downstream consumers, verify watermark and expected partitions, restore valid output, then add a zero-row/data-contract test.

**Common wrong answer(s) / failure modes**

Wait for confirmed root cause before declaration or mitigation.

**Why the wrong answer is wrong**

The operational sequence is stabilize/mitigate first, diagnose second, fix third; communication and verification continue throughout.

**Evidence / assumption note**

Synthetic incident; apply the organization’s severity and escalation policy.

### U02-Q013 — Design question

- **Question ID:** `U02-Q013`
- **Scope:** Unit 2
- **Level:** L4
- **Learning objective tested:** Design a measurable, safe, auditable control
- **Estimated time:** 20 minutes
- **Question type:** Design question

**Prompt / artifact / scenario**

Design an operational control for batch freshness/completeness/correctness and catch-up capacity. Include objective, event/data boundary, owner, safety limits, decision rights, failure behavior, rollback, verification, and review cadence.

**Model answer**

A strong design states the user/operational outcome, precise measurement and exclusions, owner, threshold rationale, missing-data behavior, safe scope, decision/override rights, rollback/abort conditions, and evidence-based acceptance. **10-point rubric:** outcome/definition 2; boundary and data quality 2; safety/rollback 2; ownership/governance 2; test evidence and review 2. Acceptable alternatives are context-dependent if their trade-offs are explicit. Common omissions: unowned controls, assumed-good missing data, no test or rollback.

**Common wrong answer(s) / failure modes**

A tool list without measurable outcomes, decision rights, or tests.

**Why the wrong answer is wrong**

A design must be testable, owned, and explicit about risk and alternatives.

**Evidence / assumption note**

Rubric and synthetic design assumptions are provided in the answer.

### U02-Q014 — Numeric/application

- **Question ID:** `U02-Q014`
- **Scope:** Unit 2
- **Level:** L2
- **Learning objective tested:** Apply the unit decision rule to supplied evidence
- **Estimated time:** 7 minutes
- **Question type:** Numeric/application

**Prompt / artifact / scenario**

A stream receives 8,000 events/min and processes 10,000/min for 10 minutes while starting 20,000 events behind.

**Model answer**

Net catch-up = 10,000 − 8,000 = 2,000 events/min. In 10 minutes it clears 20,000 events, leaving zero lag if rates stay constant and no new burst occurs.

**Common wrong answer(s) / failure modes**

Skipping the formula, units, event boundaries, or uncertainty.

**Why the wrong answer is wrong**

The result is not reproducible unless inputs, assumptions and decision rule are explicit.

**Evidence / assumption note**

Illustrative numbers and simplified models; do not generalize to production without validation.

## Unit 3 — Alert quality, noise reduction, and escalation policies
**Scope:** Unit 3. **ID range:** `U03-Q001`–`U03-Q014`.

### U03-Q001 — Conceptual short answer

- **Question ID:** `U03-Q001`
- **Scope:** Unit 3
- **Level:** L1
- **Learning objective tested:** page versus ticket/dashboard
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Explain page versus ticket/dashboard and why it matters operationally.

**Model answer**

Page versus ticket/dashboard must be defined at an observable boundary, connected to user or operator impact, owned, and used to guide a decision. A definition without measurement or action is not operationally useful.

**Common wrong answer(s) / failure modes**

Reciting a label without explaining its boundary or decision use.

**Why the wrong answer is wrong**

The question tests application of the concept, not vocabulary alone.

**Evidence / assumption note**

Illustrative course-level question; align implementation details to the local chapter.

### U03-Q002 — Conceptual short answer

- **Question ID:** `U03-Q002`
- **Scope:** Unit 3
- **Level:** L1
- **Learning objective tested:** symptom-based alerting
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Distinguish symptom-based alerting from a nearby signal or policy concept, and give one failure mode caused by confusing them.

**Model answer**

The concepts have different purposes. Define each one, show where it is measured or applied, and state how the confusion could conceal impact or create unsafe action.

**Common wrong answer(s) / failure modes**

Treating a proxy as proof of the desired outcome.

**Why the wrong answer is wrong**

A proxy may be useful, but it does not establish the user outcome without evidence.

**Evidence / assumption note**

Synthetic framing; use definitions supplied in the syllabus.

### U03-Q003 — Conceptual short answer

- **Question ID:** `U03-Q003`
- **Scope:** Unit 3
- **Level:** L2
- **Learning objective tested:** Prometheus pending/firing
- **Estimated time:** 5 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

What evidence would you collect before changing a production policy related to Prometheus pending/firing?

**Model answer**

Collect a baseline, validate data quality and event boundaries, identify owners and affected users, model likely failure modes, test the change in a disposable environment, define rollback and acceptance criteria, and review the trade-off with stakeholders.

**Common wrong answer(s) / failure modes**

Changing the threshold or policy based only on intuition.

**Why the wrong answer is wrong**

Without baseline and validation, the team cannot distinguish improvement from metric drift or shifted risk.

**Evidence / assumption note**

No live production change is required.

### U03-Q004 — Multiple choice

- **Question ID:** `U03-Q004`
- **Scope:** Unit 3
- **Level:** L1
- **Learning objective tested:** Alertmanager routes/grouping/inhibition
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which choice best operationalizes page versus ticket/dashboard?

- **A.** A measurable definition with a stated boundary, owner, evidence source, and decision rule.
- **B.** A vague statement that page versus ticket/dashboard should be “good”.
- **C.** A single resource metric with no user or operational interpretation.
- **D.** An undocumented threshold copied from another service.

**Model answer**

**Correct option: A.** The selected answer is measurable, owned and decision-relevant. **B is incorrect:** A vague statement that page versus ticket/dashboard should be “good”. **C is incorrect:** A single resource metric with no user or operational interpretation. **D is incorrect:** An undocumented threshold copied from another service.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U03-Q005 — Multiple choice

- **Question ID:** `U03-Q005`
- **Scope:** Unit 3
- **Level:** L1
- **Learning objective tested:** no-data/watchdog
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

What is the safest response when evidence for symptom-based alerting is missing or stale?

- **A.** Treat the state as unknown, validate the measurement path, and follow the documented fallback/exception policy.
- **B.** Assume the service is healthy because no failure was recorded.
- **C.** Silently replace missing values with zero.
- **D.** Disable the check until the next review.

**Model answer**

**Correct option: A.** Unknown evidence must not be represented as healthy by default. **B is incorrect:** Assume the service is healthy because no failure was recorded. **C is incorrect:** Silently replace missing values with zero. **D is incorrect:** Disable the check until the next review.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U03-Q006 — Multiple choice

- **Question ID:** `U03-Q006`
- **Scope:** Unit 3
- **Level:** L2
- **Learning objective tested:** burn rate
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which practice best reduces risk when applying Prometheus pending/firing?

- **A.** Use explicit preconditions, scoped ownership, tests, rollback/abort conditions, and post-change verification.
- **B.** Apply a broad change to all services at once.
- **C.** Skip validation because the change is reversible in theory.
- **D.** Use an undocumented verbal override.

**Model answer**

**Correct option: A.** The selected answer makes scope, failure handling, and verification explicit. **B is incorrect:** Apply a broad change to all services at once. **C is incorrect:** Skip validation because the change is reversible in theory. **D is incorrect:** Use an undocumented verbal override.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U03-Q007 — Artifact interpretation

- **Question ID:** `U03-Q007`
- **Scope:** Unit 3
- **Level:** L2
- **Learning objective tested:** page versus ticket/dashboard
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

**Will this alert fire?** Illustrative Prometheus rule: `expr: error_ratio > 0.02`, `for: 5m`, evaluation every minute. At evaluations 10:00, 10:01, 10:02, 10:03 and 10:04 the value is 0.03; at 10:05 it is 0.01. Under the simplified assumption that the condition must still be true at the evaluation that would complete five minutes, does it fire at 10:05?

**Model answer**

No. The condition is true at the first five listed evaluations but is false at 10:05, so the pending condition resets before it becomes firing under the stated simplified evaluation assumption. Test the exact boundary behavior with `promtool` and the deployed Prometheus version.

**Common wrong answer(s) / failure modes**

Assuming any one high sample immediately fires the alert, or ignoring the `for` duration.

**Why the wrong answer is wrong**

The rule includes a persistence requirement; the current sample is below the threshold and the question explicitly defines the evaluation assumption.

**Evidence / assumption note**

Illustrative rule and simplified timeline; actual rule testing should use the installed Prometheus version and its test tooling.

### U03-Q008 — Artifact interpretation

- **Question ID:** `U03-Q008`
- **Scope:** Unit 3
- **Level:** L2
- **Learning objective tested:** symptom-based alerting
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact B: no owner/runbook; broad silence or inhibition; empty vector treated as zero errors. Dashboard status is green, but no independent evidence is supplied.

**Model answer**

There are substantive defects: no owner/runbook; broad silence or inhibition; empty vector treated as zero errors. Repair with Use tested symptom-based pages with owner, severity, runbook, scoped routes/inhibition, explicit absent-data behavior, and independent delivery watchdog. Verify with a positive, negative, missing-data and boundary test.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U03-Q009 — Artifact interpretation

- **Question ID:** `U03-Q009`
- **Scope:** Unit 3
- **Level:** L3
- **Learning objective tested:** Prometheus pending/firing
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact C: Allowed bad-event rate is 0.1%; observed bad-event rate is 0.5%.

**Model answer**

Burn rate = observed error rate / allowed error rate = 0.5% / 0.1% = 5×, assuming compatible denominators and windows.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U03-Q010 — Artifact review

- **Question ID:** `U03-Q010`
- **Scope:** Unit 3
- **Level:** L3
- **Learning objective tested:** Prometheus pending/firing
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> no owner/runbook; broad silence or inhibition; empty vector treated as zero errors; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) no owner/runbook; broad silence or inhibition; empty vector treated as zero errors; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Use tested symptom-based pages with owner, severity, runbook, scoped routes/inhibition, explicit absent-data behavior, and independent delivery watchdog. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U03-Q011 — Artifact review

- **Question ID:** `U03-Q011`
- **Scope:** Unit 3
- **Level:** L3
- **Learning objective tested:** Alertmanager routes/grouping/inhibition
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> no owner/runbook; broad silence or inhibition; empty vector treated as zero errors; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) no owner/runbook; broad silence or inhibition; empty vector treated as zero errors; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Use tested symptom-based pages with owner, severity, runbook, scoped routes/inhibition, explicit absent-data behavior, and independent delivery watchdog. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U03-Q012 — Incident/triage scenario

- **Question ID:** `U03-Q012`
- **Scope:** Unit 3
- **Level:** L3
- **Learning objective tested:** Safe incident response
- **Estimated time:** 10 minutes
- **Question type:** Incident/triage scenario

**Prompt / artifact / scenario**

Prometheus evaluates a rule but Alertmanager routing is broken during customer impact.

**Model answer**

Declare from impact, use fallback contact, mitigate and communicate; later test rule-to-receiver delivery end to end and add dead-routing detection.

**Common wrong answer(s) / failure modes**

Wait for confirmed root cause before declaration or mitigation.

**Why the wrong answer is wrong**

The operational sequence is stabilize/mitigate first, diagnose second, fix third; communication and verification continue throughout.

**Evidence / assumption note**

Synthetic incident; apply the organization’s severity and escalation policy.

### U03-Q013 — Design question

- **Question ID:** `U03-Q013`
- **Scope:** Unit 3
- **Level:** L4
- **Learning objective tested:** Design a measurable, safe, auditable control
- **Estimated time:** 20 minutes
- **Question type:** Design question

**Prompt / artifact / scenario**

Design an operational control for page versus ticket/dashboard and alert quality. Include objective, event/data boundary, owner, safety limits, decision rights, failure behavior, rollback, verification, and review cadence.

**Model answer**

A strong design states the user/operational outcome, precise measurement and exclusions, owner, threshold rationale, missing-data behavior, safe scope, decision/override rights, rollback/abort conditions, and evidence-based acceptance. **10-point rubric:** outcome/definition 2; boundary and data quality 2; safety/rollback 2; ownership/governance 2; test evidence and review 2. Acceptable alternatives are context-dependent if their trade-offs are explicit. Common omissions: unowned controls, assumed-good missing data, no test or rollback.

**Common wrong answer(s) / failure modes**

A tool list without measurable outcomes, decision rights, or tests.

**Why the wrong answer is wrong**

A design must be testable, owned, and explicit about risk and alternatives.

**Evidence / assumption note**

Rubric and synthetic design assumptions are provided in the answer.

### U03-Q014 — Numeric/application

- **Question ID:** `U03-Q014`
- **Scope:** Unit 3
- **Level:** L2
- **Learning objective tested:** Apply the unit decision rule to supplied evidence
- **Estimated time:** 7 minutes
- **Question type:** Numeric/application

**Prompt / artifact / scenario**

Allowed bad-event rate is 0.1%; observed bad-event rate is 0.5%.

**Model answer**

Burn rate = observed error rate / allowed error rate = 0.5% / 0.1% = 5×, assuming compatible denominators and windows.

**Common wrong answer(s) / failure modes**

Skipping the formula, units, event boundaries, or uncertainty.

**Why the wrong answer is wrong**

The result is not reproducible unless inputs, assumptions and decision rule are explicit.

**Evidence / assumption note**

Illustrative numbers and simplified models; do not generalize to production without validation.

## Unit 4 — Incident severity, roles, and command structure
**Scope:** Unit 4. **ID range:** `U04-Q001`–`U04-Q014`.

### U04-Q001 — Conceptual short answer

- **Question ID:** `U04-Q001`
- **Scope:** Unit 4
- **Level:** L1
- **Learning objective tested:** impact-based severity
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Explain impact-based severity and why it matters operationally.

**Model answer**

Impact-based severity must be defined at an observable boundary, connected to user or operator impact, owned, and used to guide a decision. A definition without measurement or action is not operationally useful.

**Common wrong answer(s) / failure modes**

Reciting a label without explaining its boundary or decision use.

**Why the wrong answer is wrong**

The question tests application of the concept, not vocabulary alone.

**Evidence / assumption note**

Illustrative course-level question; align implementation details to the local chapter.

### U04-Q002 — Conceptual short answer

- **Question ID:** `U04-Q002`
- **Scope:** Unit 4
- **Level:** L1
- **Learning objective tested:** early declaration
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Distinguish early declaration from a nearby signal or policy concept, and give one failure mode caused by confusing them.

**Model answer**

The concepts have different purposes. Define each one, show where it is measured or applied, and state how the confusion could conceal impact or create unsafe action.

**Common wrong answer(s) / failure modes**

Treating a proxy as proof of the desired outcome.

**Why the wrong answer is wrong**

A proxy may be useful, but it does not establish the user outcome without evidence.

**Evidence / assumption note**

Synthetic framing; use definitions supplied in the syllabus.

### U04-Q003 — Conceptual short answer

- **Question ID:** `U04-Q003`
- **Scope:** Unit 4
- **Level:** L2
- **Learning objective tested:** incident commander
- **Estimated time:** 5 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

What evidence would you collect before changing a production policy related to incident commander?

**Model answer**

Collect a baseline, validate data quality and event boundaries, identify owners and affected users, model likely failure modes, test the change in a disposable environment, define rollback and acceptance criteria, and review the trade-off with stakeholders.

**Common wrong answer(s) / failure modes**

Changing the threshold or policy based only on intuition.

**Why the wrong answer is wrong**

Without baseline and validation, the team cannot distinguish improvement from metric drift or shifted risk.

**Evidence / assumption note**

No live production change is required.

### U04-Q004 — Multiple choice

- **Question ID:** `U04-Q004`
- **Scope:** Unit 4
- **Level:** L1
- **Learning objective tested:** technical/operations lead
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which choice best operationalizes impact-based severity?

- **A.** A measurable definition with a stated boundary, owner, evidence source, and decision rule.
- **B.** A vague statement that impact-based severity should be “good”.
- **C.** A single resource metric with no user or operational interpretation.
- **D.** An undocumented threshold copied from another service.

**Model answer**

**Correct option: A.** The selected answer is measurable, owned and decision-relevant. **B is incorrect:** A vague statement that impact-based severity should be “good”. **C is incorrect:** A single resource metric with no user or operational interpretation. **D is incorrect:** An undocumented threshold copied from another service.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U04-Q005 — Multiple choice

- **Question ID:** `U04-Q005`
- **Scope:** Unit 4
- **Level:** L1
- **Learning objective tested:** communications
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

What is the safest response when evidence for early declaration is missing or stale?

- **A.** Treat the state as unknown, validate the measurement path, and follow the documented fallback/exception policy.
- **B.** Assume the service is healthy because no failure was recorded.
- **C.** Silently replace missing values with zero.
- **D.** Disable the check until the next review.

**Model answer**

**Correct option: A.** Unknown evidence must not be represented as healthy by default. **B is incorrect:** Assume the service is healthy because no failure was recorded. **C is incorrect:** Silently replace missing values with zero. **D is incorrect:** Disable the check until the next review.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U04-Q006 — Multiple choice

- **Question ID:** `U04-Q006`
- **Scope:** Unit 4
- **Level:** L2
- **Learning objective tested:** handoffs and fallback channels
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which practice best reduces risk when applying incident commander?

- **A.** Use explicit preconditions, scoped ownership, tests, rollback/abort conditions, and post-change verification.
- **B.** Apply a broad change to all services at once.
- **C.** Skip validation because the change is reversible in theory.
- **D.** Use an undocumented verbal override.

**Model answer**

**Correct option: A.** The selected answer makes scope, failure handling, and verification explicit. **B is incorrect:** Apply a broad change to all services at once. **C is incorrect:** Skip validation because the change is reversible in theory. **D is incorrect:** Use an undocumented verbal override.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U04-Q007 — Artifact interpretation

- **Question ID:** `U04-Q007`
- **Scope:** Unit 4
- **Level:** L2
- **Learning objective tested:** impact-based severity
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact A: stabilize/mitigate first, diagnose second, fix third. Source data are current and the service owner confirms the denominator.

**Model answer**

Interpret the artifact using the supplied definition: verify numerator and denominator, measurement window, exclusions, ownership and user impact. A green label alone does not prove the target is meaningful. Declare from impact, assign command/technical/comms responsibilities, set cadence and fallback channels, maintain a sourced timeline, and verify user recovery before closure.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U04-Q008 — Artifact interpretation

- **Question ID:** `U04-Q008`
- **Scope:** Unit 4
- **Level:** L2
- **Learning objective tested:** early declaration
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact B: severity depends on root-cause certainty; roles overlap without decision rights; closure relies on resource metrics. Dashboard status is green, but no independent evidence is supplied.

**Model answer**

There are substantive defects: severity depends on root-cause certainty; roles overlap without decision rights; closure relies on resource metrics. Repair with Declare from impact, assign command/technical/comms responsibilities, set cadence and fallback channels, maintain a sourced timeline, and verify user recovery before closure. Verify with a positive, negative, missing-data and boundary test.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U04-Q009 — Artifact interpretation

- **Question ID:** `U04-Q009`
- **Scope:** Unit 4
- **Level:** L3
- **Learning objective tested:** incident commander
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact C: Impact begins at 09:00; IC assigned at 09:18; mitigation at 09:40; first stakeholder update at 10:00.

**Model answer**

The timeline shows delayed coordination, mitigation, and communication relative to reported impact. Check evidence and blockers, then improve declaration thresholds, role assignment, and cadence; timestamps alone do not establish motive.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U04-Q010 — Artifact review

- **Question ID:** `U04-Q010`
- **Scope:** Unit 4
- **Level:** L3
- **Learning objective tested:** incident commander
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> severity depends on root-cause certainty; roles overlap without decision rights; closure relies on resource metrics; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) severity depends on root-cause certainty; roles overlap without decision rights; closure relies on resource metrics; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Declare from impact, assign command/technical/comms responsibilities, set cadence and fallback channels, maintain a sourced timeline, and verify user recovery before closure. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U04-Q011 — Artifact review

- **Question ID:** `U04-Q011`
- **Scope:** Unit 4
- **Level:** L3
- **Learning objective tested:** technical/operations lead
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> severity depends on root-cause certainty; roles overlap without decision rights; closure relies on resource metrics; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) severity depends on root-cause certainty; roles overlap without decision rights; closure relies on resource metrics; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Declare from impact, assign command/technical/comms responsibilities, set cadence and fallback channels, maintain a sourced timeline, and verify user recovery before closure. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U04-Q012 — Incident/triage scenario

- **Question ID:** `U04-Q012`
- **Scope:** Unit 4
- **Level:** L3
- **Learning objective tested:** Safe incident response
- **Estimated time:** 10 minutes
- **Question type:** Incident/triage scenario

**Prompt / artifact / scenario**

**What is the IC's next action?** Credible evidence shows a severe customer journey is failing, root cause is unknown, and normal chat is unavailable. Order the immediate actions.

**Model answer**

Declare/coordinate based on impact; activate the backup communication path; assign or explicitly combine command, technical and communications roles; direct the safest mitigation; communicate on cadence; record decisions and verify user recovery. Root-cause diagnosis continues in parallel but must not delay mitigation.

**Common wrong answer(s) / failure modes**

Wait for root cause, keep retrying the failed chat, or let every responder investigate without coordination.

**Why the wrong answer is wrong**

Impact can justify declaration before root cause is known, and tool loss requires an independent fallback path.

**Evidence / assumption note**

Role names and update cadence should follow the organization’s stated policy.

### U04-Q013 — Design question

- **Question ID:** `U04-Q013`
- **Scope:** Unit 4
- **Level:** L4
- **Learning objective tested:** Design a measurable, safe, auditable control
- **Estimated time:** 20 minutes
- **Question type:** Design question

**Prompt / artifact / scenario**

Design an operational control for impact-based severity and handoffs and fallback channels. Include objective, event/data boundary, owner, safety limits, decision rights, failure behavior, rollback, verification, and review cadence.

**Model answer**

A strong design states the user/operational outcome, precise measurement and exclusions, owner, threshold rationale, missing-data behavior, safe scope, decision/override rights, rollback/abort conditions, and evidence-based acceptance. **10-point rubric:** outcome/definition 2; boundary and data quality 2; safety/rollback 2; ownership/governance 2; test evidence and review 2. Acceptable alternatives are context-dependent if their trade-offs are explicit. Common omissions: unowned controls, assumed-good missing data, no test or rollback.

**Common wrong answer(s) / failure modes**

A tool list without measurable outcomes, decision rights, or tests.

**Why the wrong answer is wrong**

A design must be testable, owned, and explicit about risk and alternatives.

**Evidence / assumption note**

Rubric and synthetic design assumptions are provided in the answer.

### U04-Q014 — Numeric/application

- **Question ID:** `U04-Q014`
- **Scope:** Unit 4
- **Level:** L3
- **Learning objective tested:** Apply the unit decision rule to supplied evidence
- **Estimated time:** 7 minutes
- **Question type:** Numeric/application

**Prompt / artifact / scenario**

Impact begins at 09:00; IC assigned at 09:18; mitigation at 09:40; first stakeholder update at 10:00.

**Model answer**

The timeline shows delayed coordination, mitigation, and communication relative to reported impact. Check evidence and blockers, then improve declaration thresholds, role assignment, and cadence; timestamps alone do not establish motive.

**Common wrong answer(s) / failure modes**

Skipping the formula, units, event boundaries, or uncertainty.

**Why the wrong answer is wrong**

The result is not reproducible unless inputs, assumptions and decision rule are explicit.

**Evidence / assumption note**

Illustrative numbers and simplified models; do not generalize to production without validation.

## Unit 5 — Production triage and blameless postmortems
**Scope:** Unit 5. **ID range:** `U05-Q001`–`U05-Q014`.

### U05-Q001 — Conceptual short answer

- **Question ID:** `U05-Q001`
- **Scope:** Unit 5
- **Level:** L1
- **Learning objective tested:** impact and hypothesis ledger
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Explain impact and hypothesis ledger and why it matters operationally.

**Model answer**

Impact and hypothesis ledger must be defined at an observable boundary, connected to user or operator impact, owned, and used to guide a decision. A definition without measurement or action is not operationally useful.

**Common wrong answer(s) / failure modes**

Reciting a label without explaining its boundary or decision use.

**Why the wrong answer is wrong**

The question tests application of the concept, not vocabulary alone.

**Evidence / assumption note**

Illustrative course-level question; align implementation details to the local chapter.

### U05-Q002 — Conceptual short answer

- **Question ID:** `U05-Q002`
- **Scope:** Unit 5
- **Level:** L1
- **Learning objective tested:** mitigation before diagnosis
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Distinguish mitigation before diagnosis from a nearby signal or policy concept, and give one failure mode caused by confusing them.

**Model answer**

The concepts have different purposes. Define each one, show where it is measured or applied, and state how the confusion could conceal impact or create unsafe action.

**Common wrong answer(s) / failure modes**

Treating a proxy as proof of the desired outcome.

**Why the wrong answer is wrong**

A proxy may be useful, but it does not establish the user outcome without evidence.

**Evidence / assumption note**

Synthetic framing; use definitions supplied in the syllabus.

### U05-Q003 — Conceptual short answer

- **Question ID:** `U05-Q003`
- **Scope:** Unit 5
- **Level:** L2
- **Learning objective tested:** correlation versus causation
- **Estimated time:** 5 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

What evidence would you collect before changing a production policy related to correlation versus causation?

**Model answer**

Collect a baseline, validate data quality and event boundaries, identify owners and affected users, model likely failure modes, test the change in a disposable environment, define rollback and acceptance criteria, and review the trade-off with stakeholders.

**Common wrong answer(s) / failure modes**

Changing the threshold or policy based only on intuition.

**Why the wrong answer is wrong**

Without baseline and validation, the team cannot distinguish improvement from metric drift or shifted risk.

**Evidence / assumption note**

No live production change is required.

### U05-Q004 — Multiple choice

- **Question ID:** `U05-Q004`
- **Scope:** Unit 5
- **Level:** L1
- **Learning objective tested:** systems-focused language
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

**Rewrite this blameful statement:** “The responder was careless and caused the outage.” Choose the best rewrite.

- **A.** The release process allowed an unvalidated dependency path into production; assign an owner and verify a preventive check.
- **B.** The responder is still careless, but we should avoid saying it in the report.
- **C.** Human error caused the incident; remind everyone to be more careful.
- **D.** No one is accountable because the report must be blameless.

**Model answer**

**Correct option:** A. The best rewrite describes the conditions and evidence without removing accountability: “The change reached production without a validated guard for this dependency path; the release owner will add a tested pre-deployment check by the agreed date and provide evidence in the change record.”

**B is incorrect:** The responder is still careless, but we should avoid saying it in the report. **C is incorrect:** Human error caused the incident; remind everyone to be more careful. **D is incorrect:** No one is accountable because the report must be blameless.

**Common wrong answer(s) / failure modes**

Blaming a person, replacing blame with a vague label, or treating blamelessness as removal of accountability.

**Why the wrong answer is wrong**

The best option identifies a system/control gap and preserves owned, verifiable follow-through.

**Evidence / assumption note**

Synthetic wording; adapt to evidence and avoid asserting a cause that has not been established.

### U05-Q005 — Multiple choice

- **Question ID:** `U05-Q005`
- **Scope:** Unit 5
- **Level:** L1
- **Learning objective tested:** control hierarchy
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

**Which control is highest in the hierarchy for preventing this failure?** An invalid configuration can reach production because review depends on a human noticing a subtle field. Choose the strongest practical control.

- **A.** A tested policy/validation gate that makes the invalid configuration undeployable.
- **B.** A dashboard that highlights the field after deployment.
- **C.** A training reminder to review the field more carefully.
- **D.** A runbook that explains how to roll back after customers are affected.

**Model answer**

**Correct option:** A. A preventive automated invariant that rejects the invalid configuration before deployment is strongest among these options, with monitoring and runbooks as supporting layers. It removes reliance on memory at the point of failure.

**B is incorrect:** A dashboard that highlights the field after deployment. **C is incorrect:** A training reminder to review the field more carefully. **D is incorrect:** A runbook that explains how to roll back after customers are affected.

**Common wrong answer(s) / failure modes**

Choosing detection, training, or post-failure mitigation as the only control.

**Why the wrong answer is wrong**

A preventive constraint blocks the failure path earlier; the other options can help but depend on detection or human action after risk remains.

**Evidence / assumption note**

The hierarchy is context-dependent; feasibility, bypass risks, and test coverage still need review.

### U05-Q006 — Multiple choice

- **Question ID:** `U05-Q006`
- **Scope:** Unit 5
- **Level:** L2
- **Learning objective tested:** verifiable action items
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which practice best reduces risk when applying correlation versus causation?

- **A.** Use explicit preconditions, scoped ownership, tests, rollback/abort conditions, and post-change verification.
- **B.** Apply a broad change to all services at once.
- **C.** Skip validation because the change is reversible in theory.
- **D.** Use an undocumented verbal override.

**Model answer**

**Correct option: A.** The selected answer makes scope, failure handling, and verification explicit. **B is incorrect:** Apply a broad change to all services at once. **C is incorrect:** Skip validation because the change is reversible in theory. **D is incorrect:** Use an undocumented verbal override.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U05-Q007 — Artifact interpretation

- **Question ID:** `U05-Q007`
- **Scope:** Unit 5
- **Level:** L2
- **Learning objective tested:** impact and hypothesis ledger
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact A: evidence distinguishes hypotheses from confirmed causes. Source data are current and the service owner confirms the denominator.

**Model answer**

Interpret the artifact using the supplied definition: verify numerator and denominator, measurement window, exclusions, ownership and user impact. A green label alone does not prove the target is meaningful. Use impact and sourced timeline, distinguish facts/hypotheses, examine technical/process/human conditions, assign owners/dates/tests, and prefer stronger preventive controls where practical.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U05-Q008 — Artifact interpretation

- **Question ID:** `U05-Q008`
- **Scope:** Unit 5
- **Level:** L2
- **Learning objective tested:** mitigation before diagnosis
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact B: named culprit with no system analysis; timeline omits mitigation; action says “be more careful”. Dashboard status is green, but no independent evidence is supplied.

**Model answer**

There are substantive defects: named culprit with no system analysis; timeline omits mitigation; action says “be more careful”. Repair with Use impact and sourced timeline, distinguish facts/hypotheses, examine technical/process/human conditions, assign owners/dates/tests, and prefer stronger preventive controls where practical. Verify with a positive, negative, missing-data and boundary test.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U05-Q009 — Artifact interpretation

- **Question ID:** `U05-Q009`
- **Scope:** Unit 5
- **Level:** L3
- **Learning objective tested:** correlation versus causation
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact C: A deploy occurs at 14:00, errors rise at 14:03, and dependency latency rises at 14:02.

**Model answer**

Temporal proximity alone does not prove the deploy caused the incident. Compare traces, cohorts, rollback evidence, dependency behavior, and alternatives; preserve uncertainty until evidence discriminates.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U05-Q010 — Artifact review

- **Question ID:** `U05-Q010`
- **Scope:** Unit 5
- **Level:** L3
- **Learning objective tested:** correlation versus causation
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> named culprit with no system analysis; timeline omits mitigation; action says “be more careful”; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) named culprit with no system analysis; timeline omits mitigation; action says “be more careful”; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Use impact and sourced timeline, distinguish facts/hypotheses, examine technical/process/human conditions, assign owners/dates/tests, and prefer stronger preventive controls where practical. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U05-Q011 — Artifact review

- **Question ID:** `U05-Q011`
- **Scope:** Unit 5
- **Level:** L3
- **Learning objective tested:** systems-focused language
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> named culprit with no system analysis; timeline omits mitigation; action says “be more careful”; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) named culprit with no system analysis; timeline omits mitigation; action says “be more careful”; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Use impact and sourced timeline, distinguish facts/hypotheses, examine technical/process/human conditions, assign owners/dates/tests, and prefer stronger preventive controls where practical. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U05-Q012 — Incident/triage scenario

- **Question ID:** `U05-Q012`
- **Scope:** Unit 5
- **Level:** L3
- **Learning objective tested:** Safe incident response
- **Estimated time:** 10 minutes
- **Question type:** Incident/triage scenario

**Prompt / artifact / scenario**

A customer-impacting regression follows a release while a dependency is also slow.

**Model answer**

Coordinate and mitigate first, communicate, record competing hypotheses and evidence, verify recovery, then investigate without prematurely assigning sole cause.

**Common wrong answer(s) / failure modes**

Wait for confirmed root cause before declaration or mitigation.

**Why the wrong answer is wrong**

The operational sequence is stabilize/mitigate first, diagnose second, fix third; communication and verification continue throughout.

**Evidence / assumption note**

Synthetic incident; apply the organization’s severity and escalation policy.

### U05-Q013 — Design question

- **Question ID:** `U05-Q013`
- **Scope:** Unit 5
- **Level:** L4
- **Learning objective tested:** Design a measurable, safe, auditable control
- **Estimated time:** 20 minutes
- **Question type:** Design question

**Prompt / artifact / scenario**

Design an operational control for impact and hypothesis ledger and verifiable action items. Include objective, event/data boundary, owner, safety limits, decision rights, failure behavior, rollback, verification, and review cadence.

**Model answer**

A strong design states the user/operational outcome, precise measurement and exclusions, owner, threshold rationale, missing-data behavior, safe scope, decision/override rights, rollback/abort conditions, and evidence-based acceptance. **10-point rubric:** outcome/definition 2; boundary and data quality 2; safety/rollback 2; ownership/governance 2; test evidence and review 2. Acceptable alternatives are context-dependent if their trade-offs are explicit. Common omissions: unowned controls, assumed-good missing data, no test or rollback.

**Common wrong answer(s) / failure modes**

A tool list without measurable outcomes, decision rights, or tests.

**Why the wrong answer is wrong**

A design must be testable, owned, and explicit about risk and alternatives.

**Evidence / assumption note**

Rubric and synthetic design assumptions are provided in the answer.

### U05-Q014 — Numeric/application

- **Question ID:** `U05-Q014`
- **Scope:** Unit 5
- **Level:** L3
- **Learning objective tested:** Apply the unit decision rule to supplied evidence
- **Estimated time:** 7 minutes
- **Question type:** Numeric/application

**Prompt / artifact / scenario**

A deploy occurs at 14:00, errors rise at 14:03, and dependency latency rises at 14:02.

**Model answer**

Temporal proximity alone does not prove the deploy caused the incident. Compare traces, cohorts, rollback evidence, dependency behavior, and alternatives; preserve uncertainty until evidence discriminates.

**Common wrong answer(s) / failure modes**

Skipping the formula, units, event boundaries, or uncertainty.

**Why the wrong answer is wrong**

The result is not reproducible unless inputs, assumptions and decision rule are explicit.

**Evidence / assumption note**

Illustrative numbers and simplified models; do not generalize to production without validation.

## Unit 6 — Capacity-related failures and cascading outages
**Scope:** Unit 6. **ID range:** `U06-Q001`–`U06-Q014`.

### U06-Q001 — Conceptual short answer

- **Question ID:** `U06-Q001`
- **Scope:** Unit 6
- **Level:** L1
- **Learning objective tested:** saturation/queues/backpressure
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Explain saturation/queues/backpressure and why it matters operationally.

**Model answer**

Saturation/queues/backpressure must be defined at an observable boundary, connected to user or operator impact, owned, and used to guide a decision. A definition without measurement or action is not operationally useful.

**Common wrong answer(s) / failure modes**

Reciting a label without explaining its boundary or decision use.

**Why the wrong answer is wrong**

The question tests application of the concept, not vocabulary alone.

**Evidence / assumption note**

Illustrative course-level question; align implementation details to the local chapter.

### U06-Q002 — Conceptual short answer

- **Question ID:** `U06-Q002`
- **Scope:** Unit 6
- **Level:** L1
- **Learning objective tested:** Little’s Law
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Distinguish Little’s Law from a nearby signal or policy concept, and give one failure mode caused by confusing them.

**Model answer**

The concepts have different purposes. Define each one, show where it is measured or applied, and state how the confusion could conceal impact or create unsafe action.

**Common wrong answer(s) / failure modes**

Treating a proxy as proof of the desired outcome.

**Why the wrong answer is wrong**

A proxy may be useful, but it does not establish the user outcome without evidence.

**Evidence / assumption note**

Synthetic framing; use definitions supplied in the syllabus.

### U06-Q003 — Conceptual short answer

- **Question ID:** `U06-Q003`
- **Scope:** Unit 6
- **Level:** L2
- **Learning objective tested:** retry amplification
- **Estimated time:** 5 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

What evidence would you collect before changing a production policy related to retry amplification?

**Model answer**

Collect a baseline, validate data quality and event boundaries, identify owners and affected users, model likely failure modes, test the change in a disposable environment, define rollback and acceptance criteria, and review the trade-off with stakeholders.

**Common wrong answer(s) / failure modes**

Changing the threshold or policy based only on intuition.

**Why the wrong answer is wrong**

Without baseline and validation, the team cannot distinguish improvement from metric drift or shifted risk.

**Evidence / assumption note**

No live production change is required.

### U06-Q004 — Multiple choice

- **Question ID:** `U06-Q004`
- **Scope:** Unit 6
- **Level:** L1
- **Learning objective tested:** bounded timeouts/retry budgets
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which choice best operationalizes saturation/queues/backpressure?

- **A.** A measurable definition with a stated boundary, owner, evidence source, and decision rule.
- **B.** A vague statement that saturation/queues/backpressure should be “good”.
- **C.** A single resource metric with no user or operational interpretation.
- **D.** An undocumented threshold copied from another service.

**Model answer**

**Correct option: A.** The selected answer is measurable, owned and decision-relevant. **B is incorrect:** A vague statement that saturation/queues/backpressure should be “good”. **C is incorrect:** A single resource metric with no user or operational interpretation. **D is incorrect:** An undocumented threshold copied from another service.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U06-Q005 — Multiple choice

- **Question ID:** `U06-Q005`
- **Scope:** Unit 6
- **Level:** L1
- **Learning objective tested:** load shedding
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

What is the safest response when evidence for Little’s Law is missing or stale?

- **A.** Treat the state as unknown, validate the measurement path, and follow the documented fallback/exception policy.
- **B.** Assume the service is healthy because no failure was recorded.
- **C.** Silently replace missing values with zero.
- **D.** Disable the check until the next review.

**Model answer**

**Correct option: A.** Unknown evidence must not be represented as healthy by default. **B is incorrect:** Assume the service is healthy because no failure was recorded. **C is incorrect:** Silently replace missing values with zero. **D is incorrect:** Disable the check until the next review.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U06-Q006 — Multiple choice

- **Question ID:** `U06-Q006`
- **Scope:** Unit 6
- **Level:** L2
- **Learning objective tested:** N−1
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

**Will this cascade?** Dependency graph: inference service → shared database. Demand is 80 original requests/s; each failed original creates one retry; database safe capacity is 100 attempts/s. Assume all originals reach the database and each original produces one additional retry. Which conclusion is best?

- **A.** Offered load can reach 160 attempts/s, exceeding capacity and risking queue growth and further latency.
- **B.** Offered load remains 80 attempts/s because retries do not count as new attempts.
- **C.** The database is safe because its capacity is greater than the original request rate.
- **D.** The only possible effect is higher CPU; queue depth and latency cannot change.

**Model answer**

**Correct option: A.** Total attempts can be 80 originals/s + 80 retries/s = 160 attempts/s, above the stated safe capacity of 100 attempts/s. Under the assumptions, this can grow queues and latency and amplify the original failure. Bound retries, enforce deadlines/retry budgets, and use admission control or load shedding.

**B is incorrect:** retries add attempts under the stated assumption. **C is incorrect:** capacity must be compared with total offered attempts, not originals alone. **D is incorrect:** overload can increase queue depth and latency; CPU is not the only possible symptom.

**Common wrong answer(s) / failure modes**

Assuming retries are free, or comparing only the 80 original requests/s with capacity.

**Why the wrong answer is wrong**

The relevant load is total attempts, including retries; once offered load exceeds safe capacity, queue and latency behavior can worsen the original failure.

**Evidence / assumption note**

Simplified illustrative model; actual cascade depends on retry timing, failure rate, service-time distribution and other clients.

### U06-Q007 — Artifact interpretation

- **Question ID:** `U06-Q007`
- **Scope:** Unit 6
- **Level:** L2
- **Learning objective tested:** saturation/queues/backpressure
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact A: L = λW under stable-system assumptions. Source data are current and the service owner confirms the denominator.

**Model answer**

Interpret the artifact using the supplied definition: verify numerator and denominator, measurement window, exclusions, ownership and user impact. A green label alone does not prove the target is meaningful. Bound retries and deadlines, apply admission control/backpressure, isolate workloads, load-shed safely, and test N−1 plus backlog recovery with stated assumptions.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U06-Q008 — Artifact interpretation

- **Question ID:** `U06-Q008`
- **Scope:** Unit 6
- **Level:** L2
- **Learning objective tested:** Little’s Law
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact B: unbounded retries; unbounded queue; no workload isolation; average load used as peak forecast. Dashboard status is green, but no independent evidence is supplied.

**Model answer**

There are substantive defects: unbounded retries; unbounded queue; no workload isolation; average load used as peak forecast. Repair with Bound retries and deadlines, apply admission control/backpressure, isolate workloads, load-shed safely, and test N−1 plus backlog recovery with stated assumptions. Verify with a positive, negative, missing-data and boundary test.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U06-Q009 — Artifact interpretation

- **Question ID:** `U06-Q009`
- **Scope:** Unit 6
- **Level:** L3
- **Learning objective tested:** retry amplification
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact C: Three replicas each sustain 70 requests/s; demand is 150 requests/s. Can it meet demand after one replica is lost?

**Model answer**

Remaining capacity = 2 × 70 = 140 requests/s, below 150 requests/s; N−1 capacity is short by 10 requests/s under the stated simplified model.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U06-Q010 — Artifact review

- **Question ID:** `U06-Q010`
- **Scope:** Unit 6
- **Level:** L3
- **Learning objective tested:** retry amplification
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> unbounded retries; unbounded queue; no workload isolation; average load used as peak forecast; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) unbounded retries; unbounded queue; no workload isolation; average load used as peak forecast; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Bound retries and deadlines, apply admission control/backpressure, isolate workloads, load-shed safely, and test N−1 plus backlog recovery with stated assumptions. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U06-Q011 — Artifact review

- **Question ID:** `U06-Q011`
- **Scope:** Unit 6
- **Level:** L3
- **Learning objective tested:** bounded timeouts/retry budgets
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> unbounded retries; unbounded queue; no workload isolation; average load used as peak forecast; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) unbounded retries; unbounded queue; no workload isolation; average load used as peak forecast; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Bound retries and deadlines, apply admission control/backpressure, isolate workloads, load-shed safely, and test N−1 plus backlog recovery with stated assumptions. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U06-Q012 — Incident/triage scenario

- **Question ID:** `U06-Q012`
- **Scope:** Unit 6
- **Level:** L3
- **Learning objective tested:** Safe incident response
- **Estimated time:** 10 minutes
- **Question type:** Incident/triage scenario

**Prompt / artifact / scenario**

A dependency slows, retries increase traffic, and queue depth grows while inference p99 breaches its SLO.

**Model answer**

Reduce demand and protect critical paths, bound retries, shed noncritical work, isolate dependencies, verify user SLIs, then investigate the dependency and validate capacity assumptions.

**Common wrong answer(s) / failure modes**

Wait for confirmed root cause before declaration or mitigation.

**Why the wrong answer is wrong**

The operational sequence is stabilize/mitigate first, diagnose second, fix third; communication and verification continue throughout.

**Evidence / assumption note**

Synthetic incident; apply the organization’s severity and escalation policy.

### U06-Q013 — Design question

- **Question ID:** `U06-Q013`
- **Scope:** Unit 6
- **Level:** L4
- **Learning objective tested:** Design a measurable, safe, auditable control
- **Estimated time:** 20 minutes
- **Question type:** Design question

**Prompt / artifact / scenario**

Design an operational control for saturation/queues/backpressure and catch-up capacity. Include objective, event/data boundary, owner, safety limits, decision rights, failure behavior, rollback, verification, and review cadence.

**Model answer**

A strong design states the user/operational outcome, precise measurement and exclusions, owner, threshold rationale, missing-data behavior, safe scope, decision/override rights, rollback/abort conditions, and evidence-based acceptance. **10-point rubric:** outcome/definition 2; boundary and data quality 2; safety/rollback 2; ownership/governance 2; test evidence and review 2. Acceptable alternatives are context-dependent if their trade-offs are explicit. Common omissions: unowned controls, assumed-good missing data, no test or rollback.

**Common wrong answer(s) / failure modes**

A tool list without measurable outcomes, decision rights, or tests.

**Why the wrong answer is wrong**

A design must be testable, owned, and explicit about risk and alternatives.

**Evidence / assumption note**

Rubric and synthetic design assumptions are provided in the answer.

### U06-Q014 — Numeric/application

- **Question ID:** `U06-Q014`
- **Scope:** Unit 6
- **Level:** L2
- **Learning objective tested:** Apply the unit decision rule to supplied evidence
- **Estimated time:** 7 minutes
- **Question type:** Numeric/application

**Prompt / artifact / scenario**

Three replicas each sustain 70 requests/s; demand is 150 requests/s. Can it meet demand after one replica is lost?

**Model answer**

Remaining capacity = 2 × 70 = 140 requests/s, below 150 requests/s; N−1 capacity is short by 10 requests/s under the stated simplified model.

**Common wrong answer(s) / failure modes**

Skipping the formula, units, event boundaries, or uncertainty.

**Why the wrong answer is wrong**

The result is not reproducible unless inputs, assumptions and decision rule are explicit.

**Evidence / assumption note**

Illustrative numbers and simplified models; do not generalize to production without validation.

## Unit 7 — Toil reduction and operational automation
**Scope:** Unit 7. **ID range:** `U07-Q001`–`U07-Q014`.

### U07-Q001 — Conceptual short answer

- **Question ID:** `U07-Q001`
- **Scope:** Unit 7
- **Level:** L1
- **Learning objective tested:** toil frequency/duration
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Explain toil frequency/duration and why it matters operationally.

**Model answer**

Toil frequency/duration must be defined at an observable boundary, connected to user or operator impact, owned, and used to guide a decision. A definition without measurement or action is not operationally useful.

**Common wrong answer(s) / failure modes**

Reciting a label without explaining its boundary or decision use.

**Why the wrong answer is wrong**

The question tests application of the concept, not vocabulary alone.

**Evidence / assumption note**

Illustrative course-level question; align implementation details to the local chapter.

### U07-Q002 — Conceptual short answer

- **Question ID:** `U07-Q002`
- **Scope:** Unit 7
- **Level:** L1
- **Learning objective tested:** ROI/payback
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Distinguish ROI/payback from a nearby signal or policy concept, and give one failure mode caused by confusing them.

**Model answer**

The concepts have different purposes. Define each one, show where it is measured or applied, and state how the confusion could conceal impact or create unsafe action.

**Common wrong answer(s) / failure modes**

Treating a proxy as proof of the desired outcome.

**Why the wrong answer is wrong**

A proxy may be useful, but it does not establish the user outcome without evidence.

**Evidence / assumption note**

Synthetic framing; use definitions supplied in the syllabus.

### U07-Q003 — Conceptual short answer

- **Question ID:** `U07-Q003`
- **Scope:** Unit 7
- **Level:** L2
- **Learning objective tested:** idempotency
- **Estimated time:** 5 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

What evidence would you collect before changing a production policy related to idempotency?

**Model answer**

Collect a baseline, validate data quality and event boundaries, identify owners and affected users, model likely failure modes, test the change in a disposable environment, define rollback and acceptance criteria, and review the trade-off with stakeholders.

**Common wrong answer(s) / failure modes**

Changing the threshold or policy based only on intuition.

**Why the wrong answer is wrong**

Without baseline and validation, the team cannot distinguish improvement from metric drift or shifted risk.

**Evidence / assumption note**

No live production change is required.

### U07-Q004 — Multiple choice

- **Question ID:** `U07-Q004`
- **Scope:** Unit 7
- **Level:** L1
- **Learning objective tested:** bounded retries/blast radius
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which choice best operationalizes toil frequency/duration?

- **A.** A measurable definition with a stated boundary, owner, evidence source, and decision rule.
- **B.** A vague statement that toil frequency/duration should be “good”.
- **C.** A single resource metric with no user or operational interpretation.
- **D.** An undocumented threshold copied from another service.

**Model answer**

**Correct option: A.** The selected answer is measurable, owned and decision-relevant. **B is incorrect:** A vague statement that toil frequency/duration should be “good”. **C is incorrect:** A single resource metric with no user or operational interpretation. **D is incorrect:** An undocumented threshold copied from another service.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U07-Q005 — Multiple choice

- **Question ID:** `U07-Q005`
- **Scope:** Unit 7
- **Level:** L1
- **Learning objective tested:** dry-run/approval
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

What is the safest response when evidence for ROI/payback is missing or stale?

- **A.** Treat the state as unknown, validate the measurement path, and follow the documented fallback/exception policy.
- **B.** Assume the service is healthy because no failure was recorded.
- **C.** Silently replace missing values with zero.
- **D.** Disable the check until the next review.

**Model answer**

**Correct option: A.** Unknown evidence must not be represented as healthy by default. **B is incorrect:** Assume the service is healthy because no failure was recorded. **C is incorrect:** Silently replace missing values with zero. **D is incorrect:** Disable the check until the next review.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U07-Q006 — Multiple choice

- **Question ID:** `U07-Q006`
- **Scope:** Unit 7
- **Level:** L2
- **Learning objective tested:** rollback/auditability
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which practice best reduces risk when applying idempotency?

- **A.** Use explicit preconditions, scoped ownership, tests, rollback/abort conditions, and post-change verification.
- **B.** Apply a broad change to all services at once.
- **C.** Skip validation because the change is reversible in theory.
- **D.** Use an undocumented verbal override.

**Model answer**

**Correct option: A.** The selected answer makes scope, failure handling, and verification explicit. **B is incorrect:** Apply a broad change to all services at once. **C is incorrect:** Skip validation because the change is reversible in theory. **D is incorrect:** Use an undocumented verbal override.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U07-Q007 — Artifact interpretation

- **Question ID:** `U07-Q007`
- **Scope:** Unit 7
- **Level:** L2
- **Learning objective tested:** toil frequency/duration
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact A: automation decision includes maintenance, failure risk, and opportunity cost. Source data are current and the service owner confirms the denominator.

**Model answer**

Interpret the artifact using the supplied definition: verify numerator and denominator, measurement window, exclusions, ownership and user impact. A green label alone does not prove the target is meaningful. Validate the manual procedure, measure toil, narrow scope, make operations idempotent, bound retries/rate, add approvals/audit/postconditions/rollback, and compare net ROI.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U07-Q008 — Artifact interpretation

- **Question ID:** `U07-Q008`
- **Scope:** Unit 7
- **Level:** L2
- **Learning objective tested:** ROI/payback
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact B: wildcard target selector; no dry-run; retries forever; no audit or postcondition. Dashboard status is green, but no independent evidence is supplied.

**Model answer**

There are substantive defects: wildcard target selector; no dry-run; retries forever; no audit or postcondition. Repair with Validate the manual procedure, measure toil, narrow scope, make operations idempotent, bound retries/rate, add approvals/audit/postconditions/rollback, and compare net ROI. Verify with a positive, negative, missing-data and boundary test.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U07-Q009 — Artifact interpretation

- **Question ID:** `U07-Q009`
- **Scope:** Unit 7
- **Level:** L3
- **Learning objective tested:** idempotency
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact C: A task costs 8 minutes and occurs 50 times/month. Automation saves 75% of time and costs 3 hours/month to maintain.

**Model answer**

Gross saving = 8 × 50 × 0.75 = 300 minutes = 5 hours/month. Net = 5 − 3 = 2 hours/month, excluding implementation and failure costs.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U07-Q010 — Artifact review

- **Question ID:** `U07-Q010`
- **Scope:** Unit 7
- **Level:** L3
- **Learning objective tested:** idempotency
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> wildcard target selector; no dry-run; retries forever; no audit or postcondition; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) wildcard target selector; no dry-run; retries forever; no audit or postcondition; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Validate the manual procedure, measure toil, narrow scope, make operations idempotent, bound retries/rate, add approvals/audit/postconditions/rollback, and compare net ROI. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U07-Q011 — Artifact review

- **Question ID:** `U07-Q011`
- **Scope:** Unit 7
- **Level:** L3
- **Learning objective tested:** bounded retries/blast radius
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> wildcard target selector; no dry-run; retries forever; no audit or postcondition; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) wildcard target selector; no dry-run; retries forever; no audit or postcondition; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Validate the manual procedure, measure toil, narrow scope, make operations idempotent, bound retries/rate, add approvals/audit/postconditions/rollback, and compare net ROI. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U07-Q012 — Incident/triage scenario

- **Question ID:** `U07-Q012`
- **Scope:** Unit 7
- **Level:** L3
- **Learning objective tested:** Safe incident response
- **Estimated time:** 10 minutes
- **Question type:** Incident/triage scenario

**Prompt / artifact / scenario**

A rare restart can interrupt a critical data store and the procedure is not validated.

**Model answer**

Do not start with autonomous remediation; validate the runbook and quantify risk, then consider a guarded dry-run or human-approved action.

**Common wrong answer(s) / failure modes**

Wait for confirmed root cause before declaration or mitigation.

**Why the wrong answer is wrong**

The operational sequence is stabilize/mitigate first, diagnose second, fix third; communication and verification continue throughout.

**Evidence / assumption note**

Synthetic incident; apply the organization’s severity and escalation policy.

### U07-Q013 — Design question

- **Question ID:** `U07-Q013`
- **Scope:** Unit 7
- **Level:** L4
- **Learning objective tested:** Design a measurable, safe, auditable control
- **Estimated time:** 20 minutes
- **Question type:** Design question

**Prompt / artifact / scenario**

Design an operational control for toil frequency/duration and rollback/auditability. Include objective, event/data boundary, owner, safety limits, decision rights, failure behavior, rollback, verification, and review cadence.

**Model answer**

A strong design states the user/operational outcome, precise measurement and exclusions, owner, threshold rationale, missing-data behavior, safe scope, decision/override rights, rollback/abort conditions, and evidence-based acceptance. **10-point rubric:** outcome/definition 2; boundary and data quality 2; safety/rollback 2; ownership/governance 2; test evidence and review 2. Acceptable alternatives are context-dependent if their trade-offs are explicit. Common omissions: unowned controls, assumed-good missing data, no test or rollback.

**Common wrong answer(s) / failure modes**

A tool list without measurable outcomes, decision rights, or tests.

**Why the wrong answer is wrong**

A design must be testable, owned, and explicit about risk and alternatives.

**Evidence / assumption note**

Rubric and synthetic design assumptions are provided in the answer.

### U07-Q014 — Numeric/application

- **Question ID:** `U07-Q014`
- **Scope:** Unit 7
- **Level:** L2
- **Learning objective tested:** Apply the unit decision rule to supplied evidence
- **Estimated time:** 7 minutes
- **Question type:** Numeric/application

**Prompt / artifact / scenario**

**Automate or not?** A task takes 5 minutes and occurs 4 times/month. A proposed automation saves all task time but requires 90 minutes/month of maintenance, before implementation and failure costs. Calculate net monthly time benefit and recommend a first step.

**Model answer**

Gross saved = 5 × 4 = 20 minutes/month. Maintenance = 90 minutes/month. Net = 20 − 90 = −70 minutes/month, before implementation/failure costs. Full automation is not justified on time savings alone. Validate the manual runbook, investigate whether the task can be eliminated or simplified, and reconsider only if risk reduction or frequency changes the case.

**Common wrong answer(s) / failure modes**

Approving automation because the task is repetitive, or reporting gross savings without maintenance.

**Why the wrong answer is wrong**

Maintenance exceeds the measured recurring time saved; frequency, risk reduction and opportunity cost must be considered.

**Evidence / assumption note**

Illustrative labor model; this is not a complete financial ROI model.

## Unit 8 — Runbook design and operational readiness reviews
**Scope:** Unit 8. **ID range:** `U08-Q001`–`U08-Q014`.

### U08-Q001 — Conceptual short answer

- **Question ID:** `U08-Q001`
- **Scope:** Unit 8
- **Level:** L1
- **Learning objective tested:** trigger/scope
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Explain trigger/scope and why it matters operationally.

**Model answer**

Trigger/scope must be defined at an observable boundary, connected to user or operator impact, owned, and used to guide a decision. A definition without measurement or action is not operationally useful.

**Common wrong answer(s) / failure modes**

Reciting a label without explaining its boundary or decision use.

**Why the wrong answer is wrong**

The question tests application of the concept, not vocabulary alone.

**Evidence / assumption note**

Illustrative course-level question; align implementation details to the local chapter.

### U08-Q002 — Conceptual short answer

- **Question ID:** `U08-Q002`
- **Scope:** Unit 8
- **Level:** L1
- **Learning objective tested:** prerequisites/safety checks
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Distinguish prerequisites/safety checks from a nearby signal or policy concept, and give one failure mode caused by confusing them.

**Model answer**

The concepts have different purposes. Define each one, show where it is measured or applied, and state how the confusion could conceal impact or create unsafe action.

**Common wrong answer(s) / failure modes**

Treating a proxy as proof of the desired outcome.

**Why the wrong answer is wrong**

A proxy may be useful, but it does not establish the user outcome without evidence.

**Evidence / assumption note**

Synthetic framing; use definitions supplied in the syllabus.

### U08-Q003 — Conceptual short answer

- **Question ID:** `U08-Q003`
- **Scope:** Unit 8
- **Level:** L2
- **Learning objective tested:** expected outputs/verification
- **Estimated time:** 5 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

What evidence would you collect before changing a production policy related to expected outputs/verification?

**Model answer**

Collect a baseline, validate data quality and event boundaries, identify owners and affected users, model likely failure modes, test the change in a disposable environment, define rollback and acceptance criteria, and review the trade-off with stakeholders.

**Common wrong answer(s) / failure modes**

Changing the threshold or policy based only on intuition.

**Why the wrong answer is wrong**

Without baseline and validation, the team cannot distinguish improvement from metric drift or shifted risk.

**Evidence / assumption note**

No live production change is required.

### U08-Q004 — Multiple choice

- **Question ID:** `U08-Q004`
- **Scope:** Unit 8
- **Level:** L1
- **Learning objective tested:** rollback/escalation
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which choice best operationalizes trigger/scope?

- **A.** A measurable definition with a stated boundary, owner, evidence source, and decision rule.
- **B.** A vague statement that trigger/scope should be “good”.
- **C.** A single resource metric with no user or operational interpretation.
- **D.** An undocumented threshold copied from another service.

**Model answer**

**Correct option: A.** The selected answer is measurable, owned and decision-relevant. **B is incorrect:** A vague statement that trigger/scope should be “good”. **C is incorrect:** A single resource metric with no user or operational interpretation. **D is incorrect:** An undocumented threshold copied from another service.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U08-Q005 — Multiple choice

- **Question ID:** `U08-Q005`
- **Scope:** Unit 8
- **Level:** L1
- **Learning objective tested:** ORR/PRR evidence
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

What is the safest response when evidence for prerequisites/safety checks is missing or stale?

- **A.** Treat the state as unknown, validate the measurement path, and follow the documented fallback/exception policy.
- **B.** Assume the service is healthy because no failure was recorded.
- **C.** Silently replace missing values with zero.
- **D.** Disable the check until the next review.

**Model answer**

**Correct option: A.** Unknown evidence must not be represented as healthy by default. **B is incorrect:** Assume the service is healthy because no failure was recorded. **C is incorrect:** Silently replace missing values with zero. **D is incorrect:** Disable the check until the next review.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U08-Q006 — Multiple choice

- **Question ID:** `U08-Q006`
- **Scope:** Unit 8
- **Level:** L2
- **Learning objective tested:** dependency ownership
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which practice best reduces risk when applying expected outputs/verification?

- **A.** Use explicit preconditions, scoped ownership, tests, rollback/abort conditions, and post-change verification.
- **B.** Apply a broad change to all services at once.
- **C.** Skip validation because the change is reversible in theory.
- **D.** Use an undocumented verbal override.

**Model answer**

**Correct option: A.** The selected answer makes scope, failure handling, and verification explicit. **B is incorrect:** Apply a broad change to all services at once. **C is incorrect:** Skip validation because the change is reversible in theory. **D is incorrect:** Use an undocumented verbal override.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U08-Q007 — Artifact interpretation

- **Question ID:** `U08-Q007`
- **Scope:** Unit 8
- **Level:** L2
- **Learning objective tested:** trigger/scope
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact A: readiness needs evidence, not checked boxes. Source data are current and the service owner confirms the denominator.

**Model answer**

Interpret the artifact using the supplied definition: verify numerator and denominator, measurement window, exclusions, ownership and user impact. A green label alone does not prove the target is meaningful. Runbooks need scope guards, preconditions, safe steps, expected outputs, abort/rollback, escalation, and SLI verification. ORRs link actual test evidence and named owners.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U08-Q008 — Artifact interpretation

- **Question ID:** `U08-Q008`
- **Scope:** Unit 8
- **Level:** L2
- **Learning objective tested:** prerequisites/safety checks
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact B: no environment guard; restart all replicas; no rollback; “confirm healthy” undefined. Dashboard status is green, but no independent evidence is supplied.

**Model answer**

There are substantive defects: no environment guard; restart all replicas; no rollback; “confirm healthy” undefined. Repair with Runbooks need scope guards, preconditions, safe steps, expected outputs, abort/rollback, escalation, and SLI verification. ORRs link actual test evidence and named owners. Verify with a positive, negative, missing-data and boundary test.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U08-Q009 — Artifact interpretation

- **Question ID:** `U08-Q009`
- **Scope:** Unit 8
- **Level:** L3
- **Learning objective tested:** expected outputs/verification
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact C: An ORR has 12 checks; 10 pass, while rollback testing and downstream ownership are unverified.

**Model answer**

A raw 10/12 score is insufficient. Untested rollback and ownerless dependency can be critical blockers; apply the explicit gate, gather evidence, or approve a bounded exception with owner and expiry.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U08-Q010 — Artifact review

- **Question ID:** `U08-Q010`
- **Scope:** Unit 8
- **Level:** L3
- **Learning objective tested:** expected outputs/verification
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> no environment guard; restart all replicas; no rollback; “confirm healthy” undefined; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) no environment guard; restart all replicas; no rollback; “confirm healthy” undefined; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Runbooks need scope guards, preconditions, safe steps, expected outputs, abort/rollback, escalation, and SLI verification. ORRs link actual test evidence and named owners. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U08-Q011 — Artifact review

- **Question ID:** `U08-Q011`
- **Scope:** Unit 8
- **Level:** L3
- **Learning objective tested:** rollback/escalation
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> no environment guard; restart all replicas; no rollback; “confirm healthy” undefined; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) no environment guard; restart all replicas; no rollback; “confirm healthy” undefined; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Runbooks need scope guards, preconditions, safe steps, expected outputs, abort/rollback, escalation, and SLI verification. ORRs link actual test evidence and named owners. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U08-Q012 — Incident/triage scenario

- **Question ID:** `U08-Q012`
- **Scope:** Unit 8
- **Level:** L3
- **Learning objective tested:** Safe incident response
- **Estimated time:** 10 minutes
- **Question type:** Incident/triage scenario

**Prompt / artifact / scenario**

During a high-severity incident, a runbook restart command lacks a target guard and the service is overloaded.

**Model answer**

Do not run the ambiguous command; coordinate, use verified safe mitigation, confirm target and preconditions, escalate, verify recovery, and repair the runbook.

**Common wrong answer(s) / failure modes**

Wait for confirmed root cause before declaration or mitigation.

**Why the wrong answer is wrong**

The operational sequence is stabilize/mitigate first, diagnose second, fix third; communication and verification continue throughout.

**Evidence / assumption note**

Synthetic incident; apply the organization’s severity and escalation policy.

### U08-Q013 — Design question

- **Question ID:** `U08-Q013`
- **Scope:** Unit 8
- **Level:** L4
- **Learning objective tested:** Design a measurable, safe, auditable control
- **Estimated time:** 20 minutes
- **Question type:** Design question

**Prompt / artifact / scenario**

Design an operational control for trigger/scope and dependency ownership. Include objective, event/data boundary, owner, safety limits, decision rights, failure behavior, rollback, verification, and review cadence.

**Model answer**

A strong design states the user/operational outcome, precise measurement and exclusions, owner, threshold rationale, missing-data behavior, safe scope, decision/override rights, rollback/abort conditions, and evidence-based acceptance. **10-point rubric:** outcome/definition 2; boundary and data quality 2; safety/rollback 2; ownership/governance 2; test evidence and review 2. Acceptable alternatives are context-dependent if their trade-offs are explicit. Common omissions: unowned controls, assumed-good missing data, no test or rollback.

**Common wrong answer(s) / failure modes**

A tool list without measurable outcomes, decision rights, or tests.

**Why the wrong answer is wrong**

A design must be testable, owned, and explicit about risk and alternatives.

**Evidence / assumption note**

Rubric and synthetic design assumptions are provided in the answer.

### U08-Q014 — Numeric/application

- **Question ID:** `U08-Q014`
- **Scope:** Unit 8
- **Level:** L3
- **Learning objective tested:** Apply the unit decision rule to supplied evidence
- **Estimated time:** 7 minutes
- **Question type:** Numeric/application

**Prompt / artifact / scenario**

An ORR has 12 checks; 10 pass, while rollback testing and downstream ownership are unverified.

**Model answer**

A raw 10/12 score is insufficient. Untested rollback and ownerless dependency can be critical blockers; apply the explicit gate, gather evidence, or approve a bounded exception with owner and expiry.

**Common wrong answer(s) / failure modes**

Skipping the formula, units, event boundaries, or uncertainty.

**Why the wrong answer is wrong**

The result is not reproducible unless inputs, assumptions and decision rule are explicit.

**Evidence / assumption note**

Illustrative numbers and simplified models; do not generalize to production without validation.

## Unit 9 — Error-budget policies and release freezes
**Scope:** Unit 9. **ID range:** `U09-Q001`–`U09-Q014`.

### U09-Q001 — Conceptual short answer

- **Question ID:** `U09-Q001`
- **Scope:** Unit 9
- **Level:** L1
- **Learning objective tested:** remaining budget/burn
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Explain remaining budget/burn and why it matters operationally.

**Model answer**

Remaining budget/burn must be defined at an observable boundary, connected to user or operator impact, owned, and used to guide a decision. A definition without measurement or action is not operationally useful.

**Common wrong answer(s) / failure modes**

Reciting a label without explaining its boundary or decision use.

**Why the wrong answer is wrong**

The question tests application of the concept, not vocabulary alone.

**Evidence / assumption note**

Illustrative course-level question; align implementation details to the local chapter.

### U09-Q002 — Conceptual short answer

- **Question ID:** `U09-Q002`
- **Scope:** Unit 9
- **Level:** L1
- **Learning objective tested:** freeze/slowdown/normal release
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Distinguish freeze/slowdown/normal release from a nearby signal or policy concept, and give one failure mode caused by confusing them.

**Model answer**

The concepts have different purposes. Define each one, show where it is measured or applied, and state how the confusion could conceal impact or create unsafe action.

**Common wrong answer(s) / failure modes**

Treating a proxy as proof of the desired outcome.

**Why the wrong answer is wrong**

A proxy may be useful, but it does not establish the user outcome without evidence.

**Evidence / assumption note**

Synthetic framing; use definitions supplied in the syllabus.

### U09-Q003 — Conceptual short answer

- **Question ID:** `U09-Q003`
- **Scope:** Unit 9
- **Level:** L2
- **Learning objective tested:** exceptions
- **Estimated time:** 5 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

What evidence would you collect before changing a production policy related to exceptions?

**Model answer**

Collect a baseline, validate data quality and event boundaries, identify owners and affected users, model likely failure modes, test the change in a disposable environment, define rollback and acceptance criteria, and review the trade-off with stakeholders.

**Common wrong answer(s) / failure modes**

Changing the threshold or policy based only on intuition.

**Why the wrong answer is wrong**

Without baseline and validation, the team cannot distinguish improvement from metric drift or shifted risk.

**Evidence / assumption note**

No live production change is required.

### U09-Q004 — Multiple choice

- **Question ID:** `U09-Q004`
- **Scope:** Unit 9
- **Level:** L1
- **Learning objective tested:** policy-as-code
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

**Should we freeze?** Policy says: “Pause routine releases when remaining budget is below 10%; emergency security fixes require IC and security-owner approval.” Remaining budget is 6% and an urgent security patch addresses active exposure. What is the best action?

- **A.** Pause routine releases but use the defined, approved security exception for this patch.
- **B.** Freeze every change including the security patch without considering the exception.
- **C.** Deploy immediately without approval because security work is always exempt.
- **D.** Change the budget denominator so the gate returns allow.

**Model answer**

**Correct option:** A. Invoke the explicitly stated emergency security exception: obtain IC and security-owner approval, scope the patch, use safe rollout/rollback and monitoring, record the override, and review it afterward. Routine releases remain paused. The policy supplies the decision path.

**B is incorrect:** Freeze every change including the security patch without considering the exception. **C is incorrect:** Deploy immediately without approval because security work is always exempt. **D is incorrect:** Change the budget denominator so the gate returns allow.

**Common wrong answer(s) / failure modes**

Ignoring the stated exception, bypassing approvals, or manipulating the metric.

**Why the wrong answer is wrong**

The policy explicitly distinguishes routine releases from an approved emergency security path.

**Evidence / assumption note**

Threshold and policy are illustrative; organizations must define exception authority and evidence.

### U09-Q005 — Multiple choice

- **Question ID:** `U09-Q005`
- **Scope:** Unit 9
- **Level:** L1
- **Learning objective tested:** stale telemetry
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

What is the safest response when evidence for freeze/slowdown/normal release is missing or stale?

- **A.** Treat the state as unknown, validate the measurement path, and follow the documented fallback/exception policy.
- **B.** Assume the service is healthy because no failure was recorded.
- **C.** Silently replace missing values with zero.
- **D.** Disable the check until the next review.

**Model answer**

**Correct option: A.** Unknown evidence must not be represented as healthy by default. **B is incorrect:** Assume the service is healthy because no failure was recorded. **C is incorrect:** Silently replace missing values with zero. **D is incorrect:** Disable the check until the next review.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U09-Q006 — Multiple choice

- **Question ID:** `U09-Q006`
- **Scope:** Unit 9
- **Level:** L2
- **Learning objective tested:** fail-open/fail-closed
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which practice best reduces risk when applying exceptions?

- **A.** Use explicit preconditions, scoped ownership, tests, rollback/abort conditions, and post-change verification.
- **B.** Apply a broad change to all services at once.
- **C.** Skip validation because the change is reversible in theory.
- **D.** Use an undocumented verbal override.

**Model answer**

**Correct option: A.** The selected answer makes scope, failure handling, and verification explicit. **B is incorrect:** Apply a broad change to all services at once. **C is incorrect:** Skip validation because the change is reversible in theory. **D is incorrect:** Use an undocumented verbal override.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U09-Q007 — Artifact interpretation

- **Question ID:** `U09-Q007`
- **Scope:** Unit 9
- **Level:** L2
- **Learning objective tested:** remaining budget/burn
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact A: a gate needs explicit decision rights and valid telemetry. Source data are current and the service owner confirms the denominator.

**Model answer**

Interpret the artifact using the supplied definition: verify numerator and denominator, measurement window, exclusions, ownership and user impact. A green label alone does not prove the target is meaningful. Define measurable policy states, telemetry freshness, workload-specific rules, authorized scoped overrides, expiry, audit, canary/rollback, and tests for unknown data.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U09-Q008 — Artifact interpretation

- **Question ID:** `U09-Q008`
- **Scope:** Unit 9
- **Level:** L2
- **Learning objective tested:** freeze/slowdown/normal release
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact B: “freeze when bad”; verbal override; stale budget cache allowed; all workloads use one threshold. Dashboard status is green, but no independent evidence is supplied.

**Model answer**

There are substantive defects: “freeze when bad”; verbal override; stale budget cache allowed; all workloads use one threshold. Repair with Define measurable policy states, telemetry freshness, workload-specific rules, authorized scoped overrides, expiry, audit, canary/rollback, and tests for unknown data. Verify with a positive, negative, missing-data and boundary test.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U09-Q009 — Artifact interpretation

- **Question ID:** `U09-Q009`
- **Scope:** Unit 9
- **Level:** L3
- **Learning objective tested:** exceptions
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact C: Budget is 6%, and an urgent security patch fixes active exposure; policy pauses routine releases but allows security exceptions with IC and security-owner approval.

**Model answer**

Pause routine releases; invoke the defined exception path, obtain both approvals, scope and monitor the patch, preserve rollback, record the override, and review it.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U09-Q010 — Artifact review

- **Question ID:** `U09-Q010`
- **Scope:** Unit 9
- **Level:** L3
- **Learning objective tested:** exceptions
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> “freeze when bad”; verbal override; stale budget cache allowed; all workloads use one threshold; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) “freeze when bad”; verbal override; stale budget cache allowed; all workloads use one threshold; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Define measurable policy states, telemetry freshness, workload-specific rules, authorized scoped overrides, expiry, audit, canary/rollback, and tests for unknown data. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U09-Q011 — Artifact review

- **Question ID:** `U09-Q011`
- **Scope:** Unit 9
- **Level:** L3
- **Learning objective tested:** policy-as-code
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> “freeze when bad”; verbal override; stale budget cache allowed; all workloads use one threshold; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) “freeze when bad”; verbal override; stale budget cache allowed; all workloads use one threshold; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Define measurable policy states, telemetry freshness, workload-specific rules, authorized scoped overrides, expiry, audit, canary/rollback, and tests for unknown data. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U09-Q012 — Incident/triage scenario

- **Question ID:** `U09-Q012`
- **Scope:** Unit 9
- **Level:** L3
- **Learning objective tested:** Safe incident response
- **Estimated time:** 10 minutes
- **Question type:** Incident/triage scenario

**Prompt / artifact / scenario**

A strict release gate blocks a rollback needed to mitigate an active incident.

**Model answer**

Use the explicit incident-response override for the mitigating rollback, record authority/scope and verify recovery; policy should distinguish mitigation from risky forward release.

**Common wrong answer(s) / failure modes**

Wait for confirmed root cause before declaration or mitigation.

**Why the wrong answer is wrong**

The operational sequence is stabilize/mitigate first, diagnose second, fix third; communication and verification continue throughout.

**Evidence / assumption note**

Synthetic incident; apply the organization’s severity and escalation policy.

### U09-Q013 — Design question

- **Question ID:** `U09-Q013`
- **Scope:** Unit 9
- **Level:** L4
- **Learning objective tested:** Design a measurable, safe, auditable control
- **Estimated time:** 20 minutes
- **Question type:** Design question

**Prompt / artifact / scenario**

Design an operational control for remaining budget/burn and fail-open/fail-closed. Include objective, event/data boundary, owner, safety limits, decision rights, failure behavior, rollback, verification, and review cadence.

**Model answer**

A strong design states the user/operational outcome, precise measurement and exclusions, owner, threshold rationale, missing-data behavior, safe scope, decision/override rights, rollback/abort conditions, and evidence-based acceptance. **10-point rubric:** outcome/definition 2; boundary and data quality 2; safety/rollback 2; ownership/governance 2; test evidence and review 2. Acceptable alternatives are context-dependent if their trade-offs are explicit. Common omissions: unowned controls, assumed-good missing data, no test or rollback.

**Common wrong answer(s) / failure modes**

A tool list without measurable outcomes, decision rights, or tests.

**Why the wrong answer is wrong**

A design must be testable, owned, and explicit about risk and alternatives.

**Evidence / assumption note**

Rubric and synthetic design assumptions are provided in the answer.

### U09-Q014 — Numeric/application

- **Question ID:** `U09-Q014`
- **Scope:** Unit 9
- **Level:** L2
- **Learning objective tested:** Apply the unit decision rule to supplied evidence
- **Estimated time:** 7 minutes
- **Question type:** Numeric/application

**Prompt / artifact / scenario**

Budget is 6%, and an urgent security patch fixes active exposure; policy pauses routine releases but allows security exceptions with IC and security-owner approval.

**Model answer**

Pause routine releases; invoke the defined exception path, obtain both approvals, scope and monitor the patch, preserve rollback, record the override, and review it.

**Common wrong answer(s) / failure modes**

Skipping the formula, units, event boundaries, or uncertainty.

**Why the wrong answer is wrong**

The result is not reproducible unless inputs, assumptions and decision rule are explicit.

**Evidence / assumption note**

Illustrative numbers and simplified models; do not generalize to production without validation.

## Unit 10 — On-call rotations, handoffs, and sustainable paging
**Scope:** Unit 10. **ID range:** `U10-Q001`–`U10-Q014`.

### U10-Q001 — Conceptual short answer

- **Question ID:** `U10-Q001`
- **Scope:** Unit 10
- **Level:** L1
- **Learning objective tested:** primary/secondary
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Explain primary/secondary and why it matters operationally.

**Model answer**

Primary/secondary must be defined at an observable boundary, connected to user or operator impact, owned, and used to guide a decision. A definition without measurement or action is not operationally useful.

**Common wrong answer(s) / failure modes**

Reciting a label without explaining its boundary or decision use.

**Why the wrong answer is wrong**

The question tests application of the concept, not vocabulary alone.

**Evidence / assumption note**

Illustrative course-level question; align implementation details to the local chapter.

### U10-Q002 — Conceptual short answer

- **Question ID:** `U10-Q002`
- **Scope:** Unit 10
- **Level:** L1
- **Learning objective tested:** fairness and eligible shifts
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Distinguish fairness and eligible shifts from a nearby signal or policy concept, and give one failure mode caused by confusing them.

**Model answer**

The concepts have different purposes. Define each one, show where it is measured or applied, and state how the confusion could conceal impact or create unsafe action.

**Common wrong answer(s) / failure modes**

Treating a proxy as proof of the desired outcome.

**Why the wrong answer is wrong**

A proxy may be useful, but it does not establish the user outcome without evidence.

**Evidence / assumption note**

Synthetic framing; use definitions supplied in the syllabus.

### U10-Q003 — Conceptual short answer

- **Question ID:** `U10-Q003`
- **Scope:** Unit 10
- **Level:** L2
- **Learning objective tested:** night pages/rest
- **Estimated time:** 5 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

What evidence would you collect before changing a production policy related to night pages/rest?

**Model answer**

Collect a baseline, validate data quality and event boundaries, identify owners and affected users, model likely failure modes, test the change in a disposable environment, define rollback and acceptance criteria, and review the trade-off with stakeholders.

**Common wrong answer(s) / failure modes**

Changing the threshold or policy based only on intuition.

**Why the wrong answer is wrong**

Without baseline and validation, the team cannot distinguish improvement from metric drift or shifted risk.

**Evidence / assumption note**

No live production change is required.

### U10-Q004 — Multiple choice

- **Question ID:** `U10-Q004`
- **Scope:** Unit 10
- **Level:** L1
- **Learning objective tested:** page-ticket-delete
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

**Is this rotation sustainable?** A synthetic four-person team has 14 pages/week, 8 overnight pages, and one responder receives 60% of all pages. No severity, eligible-shift, or leave context has yet been reviewed. What is the best conclusion?

- **A.** It needs investigation: raw counts show concentration and night load but need exposure and context.
- **B.** It is sustainable because 14 divided by four is only 3.5 pages per person.
- **C.** It is unsustainable solely because any overnight page is unacceptable.
- **D.** Ignore the distribution and add another alert threshold.

**Model answer**

**Correct option:** A. The data are a warning, not enough for a universal pass/fail. Investigate page actionability, per-person and per-eligible-shift distribution, night-page clustering, severity, response effort, leave and rest. Reduce noisy pages and correct routing before making staffing claims.

**B is incorrect:** It is sustainable because 14 divided by four is only 3.5 pages per person. **C is incorrect:** It is unsustainable solely because any overnight page is unacceptable. **D is incorrect:** Ignore the distribution and add another alert threshold.

**Common wrong answer(s) / failure modes**

Using only a team average, assuming all night pages are unacceptable, or adding alerts without diagnosing load.

**Why the wrong answer is wrong**

Sustainability depends on concentration, timing, severity, eligible shifts, rest and actionability, not one raw average.

**Evidence / assumption note**

All values are synthetic; no universal page-count threshold is asserted.

### U10-Q005 — Multiple choice

- **Question ID:** `U10-Q005`
- **Scope:** Unit 10
- **Level:** L1
- **Learning objective tested:** handoffs
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

What is the safest response when evidence for fairness and eligible shifts is missing or stale?

- **A.** Treat the state as unknown, validate the measurement path, and follow the documented fallback/exception policy.
- **B.** Assume the service is healthy because no failure was recorded.
- **C.** Silently replace missing values with zero.
- **D.** Disable the check until the next review.

**Model answer**

**Correct option: A.** Unknown evidence must not be represented as healthy by default. **B is incorrect:** Assume the service is healthy because no failure was recorded. **C is incorrect:** Silently replace missing values with zero. **D is incorrect:** Disable the check until the next review.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U10-Q006 — Multiple choice

- **Question ID:** `U10-Q006`
- **Scope:** Unit 10
- **Level:** L2
- **Learning objective tested:** dead routing
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which practice best reduces risk when applying night pages/rest?

- **A.** Use explicit preconditions, scoped ownership, tests, rollback/abort conditions, and post-change verification.
- **B.** Apply a broad change to all services at once.
- **C.** Skip validation because the change is reversible in theory.
- **D.** Use an undocumented verbal override.

**Model answer**

**Correct option: A.** The selected answer makes scope, failure handling, and verification explicit. **B is incorrect:** Apply a broad change to all services at once. **C is incorrect:** Skip validation because the change is reversible in theory. **D is incorrect:** Use an undocumented verbal override.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U10-Q007 — Artifact interpretation

- **Question ID:** `U10-Q007`
- **Scope:** Unit 10
- **Level:** L2
- **Learning objective tested:** primary/secondary
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact A: on-call fatigue and pager-path reliability affect incident outcomes. Source data are current and the service owner confirms the denominator.

**Model answer**

Interpret the artifact using the supplied definition: verify numerator and denominator, measurement window, exclusions, ownership and user impact. A green label alone does not prove the target is meaningful. Review alert quality and per-eligible-shift load, provide primary/secondary and fallback paths, require acknowledged handoffs, and protect rest/privacy.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U10-Q008 — Artifact interpretation

- **Question ID:** `U10-Q008`
- **Scope:** Unit 10
- **Level:** L2
- **Learning objective tested:** fairness and eligible shifts
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact B: raw totals used without leave/shift context; swaps have no handoff; no pager fallback. Dashboard status is green, but no independent evidence is supplied.

**Model answer**

There are substantive defects: raw totals used without leave/shift context; swaps have no handoff; no pager fallback. Repair with Review alert quality and per-eligible-shift load, provide primary/secondary and fallback paths, require acknowledged handoffs, and protect rest/privacy. Verify with a positive, negative, missing-data and boundary test.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U10-Q009 — Artifact interpretation

- **Question ID:** `U10-Q009`
- **Scope:** Unit 10
- **Level:** L3
- **Learning objective tested:** night pages/rest
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact C: In 28 days, responder A has 6 night pages over 4 eligible night shifts; B has 6 over 12 eligible shifts.

**Model answer**

Rates are A: 6/4 = 1.5 night pages per eligible shift; B: 6/12 = 0.5. Investigate exposure, severity and routing; do not turn the metric into an individual ranking.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U10-Q010 — Artifact review

- **Question ID:** `U10-Q010`
- **Scope:** Unit 10
- **Level:** L3
- **Learning objective tested:** night pages/rest
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> raw totals used without leave/shift context; swaps have no handoff; no pager fallback; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) raw totals used without leave/shift context; swaps have no handoff; no pager fallback; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Review alert quality and per-eligible-shift load, provide primary/secondary and fallback paths, require acknowledged handoffs, and protect rest/privacy. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U10-Q011 — Artifact review

- **Question ID:** `U10-Q011`
- **Scope:** Unit 10
- **Level:** L3
- **Learning objective tested:** page-ticket-delete
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> raw totals used without leave/shift context; swaps have no handoff; no pager fallback; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) raw totals used without leave/shift context; swaps have no handoff; no pager fallback; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Review alert quality and per-eligible-shift load, provide primary/secondary and fallback paths, require acknowledged handoffs, and protect rest/privacy. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U10-Q012 — Incident/triage scenario

- **Question ID:** `U10-Q012`
- **Scope:** Unit 10
- **Level:** L3
- **Learning objective tested:** Safe incident response
- **Estimated time:** 10 minutes
- **Question type:** Incident/triage scenario

**Prompt / artifact / scenario**

Primary does not acknowledge a customer-impacting page and secondary routing is broken.

**Model answer**

Use an independent fallback path, declare/coordinate, mitigate and communicate; afterward test routing end to end and add dead-routing meta-monitoring.

**Common wrong answer(s) / failure modes**

Wait for confirmed root cause before declaration or mitigation.

**Why the wrong answer is wrong**

The operational sequence is stabilize/mitigate first, diagnose second, fix third; communication and verification continue throughout.

**Evidence / assumption note**

Synthetic incident; apply the organization’s severity and escalation policy.

### U10-Q013 — Design question

- **Question ID:** `U10-Q013`
- **Scope:** Unit 10
- **Level:** L4
- **Learning objective tested:** Design a measurable, safe, auditable control
- **Estimated time:** 20 minutes
- **Question type:** Design question

**Prompt / artifact / scenario**

Design an operational control for primary/secondary and small-team coverage. Include objective, event/data boundary, owner, safety limits, decision rights, failure behavior, rollback, verification, and review cadence.

**Model answer**

A strong design states the user/operational outcome, precise measurement and exclusions, owner, threshold rationale, missing-data behavior, safe scope, decision/override rights, rollback/abort conditions, and evidence-based acceptance. **10-point rubric:** outcome/definition 2; boundary and data quality 2; safety/rollback 2; ownership/governance 2; test evidence and review 2. Acceptable alternatives are context-dependent if their trade-offs are explicit. Common omissions: unowned controls, assumed-good missing data, no test or rollback.

**Common wrong answer(s) / failure modes**

A tool list without measurable outcomes, decision rights, or tests.

**Why the wrong answer is wrong**

A design must be testable, owned, and explicit about risk and alternatives.

**Evidence / assumption note**

Rubric and synthetic design assumptions are provided in the answer.

### U10-Q014 — Numeric/application

- **Question ID:** `U10-Q014`
- **Scope:** Unit 10
- **Level:** L2
- **Learning objective tested:** Apply the unit decision rule to supplied evidence
- **Estimated time:** 7 minutes
- **Question type:** Numeric/application

**Prompt / artifact / scenario**

In 28 days, responder A has 6 night pages over 4 eligible night shifts; B has 6 over 12 eligible shifts.

**Model answer**

Rates are A: 6/4 = 1.5 night pages per eligible shift; B: 6/12 = 0.5. Investigate exposure, severity and routing; do not turn the metric into an individual ranking.

**Common wrong answer(s) / failure modes**

Skipping the formula, units, event boundaries, or uncertainty.

**Why the wrong answer is wrong**

The result is not reproducible unless inputs, assumptions and decision rule are explicit.

**Evidence / assumption note**

Illustrative numbers and simplified models; do not generalize to production without validation.

## Unit 11 — DORA metrics and engineering performance measurement
**Scope:** Unit 11. **ID range:** `U11-Q001`–`U11-Q014`.

### U11-Q001 — Conceptual short answer

- **Question ID:** `U11-Q001`
- **Scope:** Unit 11
- **Level:** L1
- **Learning objective tested:** deployment frequency
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Explain deployment frequency and why it matters operationally.

**Model answer**

Deployment frequency must be defined at an observable boundary, connected to user or operator impact, owned, and used to guide a decision. A definition without measurement or action is not operationally useful.

**Common wrong answer(s) / failure modes**

Reciting a label without explaining its boundary or decision use.

**Why the wrong answer is wrong**

The question tests application of the concept, not vocabulary alone.

**Evidence / assumption note**

Illustrative course-level question; align implementation details to the local chapter.

### U11-Q002 — Conceptual short answer

- **Question ID:** `U11-Q002`
- **Scope:** Unit 11
- **Level:** L1
- **Learning objective tested:** lead time
- **Estimated time:** 4 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

Distinguish lead time from a nearby signal or policy concept, and give one failure mode caused by confusing them.

**Model answer**

The concepts have different purposes. Define each one, show where it is measured or applied, and state how the confusion could conceal impact or create unsafe action.

**Common wrong answer(s) / failure modes**

Treating a proxy as proof of the desired outcome.

**Why the wrong answer is wrong**

A proxy may be useful, but it does not establish the user outcome without evidence.

**Evidence / assumption note**

Synthetic framing; use definitions supplied in the syllabus.

### U11-Q003 — Conceptual short answer

- **Question ID:** `U11-Q003`
- **Scope:** Unit 11
- **Level:** L2
- **Learning objective tested:** change failure rate
- **Estimated time:** 5 minutes
- **Question type:** Conceptual short answer

**Prompt / artifact / scenario**

What evidence would you collect before changing a production policy related to change failure rate?

**Model answer**

Collect a baseline, validate data quality and event boundaries, identify owners and affected users, model likely failure modes, test the change in a disposable environment, define rollback and acceptance criteria, and review the trade-off with stakeholders.

**Common wrong answer(s) / failure modes**

Changing the threshold or policy based only on intuition.

**Why the wrong answer is wrong**

Without baseline and validation, the team cannot distinguish improvement from metric drift or shifted risk.

**Evidence / assumption note**

No live production change is required.

### U11-Q004 — Multiple choice

- **Question ID:** `U11-Q004`
- **Scope:** Unit 11
- **Level:** L1
- **Learning objective tested:** time to restore
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which choice best operationalizes deployment frequency?

- **A.** A measurable definition with a stated boundary, owner, evidence source, and decision rule.
- **B.** A vague statement that deployment frequency should be “good”.
- **C.** A single resource metric with no user or operational interpretation.
- **D.** An undocumented threshold copied from another service.

**Model answer**

**Correct option: A.** The selected answer is measurable, owned and decision-relevant. **B is incorrect:** A vague statement that deployment frequency should be “good”. **C is incorrect:** A single resource metric with no user or operational interpretation. **D is incorrect:** An undocumented threshold copied from another service.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U11-Q005 — Multiple choice

- **Question ID:** `U11-Q005`
- **Scope:** Unit 11
- **Level:** L1
- **Learning objective tested:** event definitions
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

What is the safest response when evidence for lead time is missing or stale?

- **A.** Treat the state as unknown, validate the measurement path, and follow the documented fallback/exception policy.
- **B.** Assume the service is healthy because no failure was recorded.
- **C.** Silently replace missing values with zero.
- **D.** Disable the check until the next review.

**Model answer**

**Correct option: A.** Unknown evidence must not be represented as healthy by default. **B is incorrect:** Assume the service is healthy because no failure was recorded. **C is incorrect:** Silently replace missing values with zero. **D is incorrect:** Disable the check until the next review.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U11-Q006 — Multiple choice

- **Question ID:** `U11-Q006`
- **Scope:** Unit 11
- **Level:** L2
- **Learning objective tested:** incident links
- **Estimated time:** 3 minutes
- **Question type:** Multiple choice

**Prompt / artifact / scenario**

Which practice best reduces risk when applying change failure rate?

- **A.** Use explicit preconditions, scoped ownership, tests, rollback/abort conditions, and post-change verification.
- **B.** Apply a broad change to all services at once.
- **C.** Skip validation because the change is reversible in theory.
- **D.** Use an undocumented verbal override.

**Model answer**

**Correct option: A.** The selected answer makes scope, failure handling, and verification explicit. **B is incorrect:** Apply a broad change to all services at once. **C is incorrect:** Skip validation because the change is reversible in theory. **D is incorrect:** Use an undocumented verbal override.

**Common wrong answer(s) / failure modes**

Selecting a vague, untested, or unsafe shortcut.

**Why the wrong answer is wrong**

Each distractor fails the measurability, evidence, or safety requirement stated in the question.

**Evidence / assumption note**

Options are synthetic; exact tool behavior must be verified against installed versions.

### U11-Q007 — Artifact interpretation

- **Question ID:** `U11-Q007`
- **Scope:** Unit 11
- **Level:** L2
- **Learning objective tested:** deployment frequency
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

**What is this metric hiding?** Scorecard shows deployment frequency +30%, lead time −20%, change failure rate −50%, but SLO attainment falls and incident declarations drop sharply. Identify at least two plausible blind spots and the next audit.

**Model answer**

Possible blind spots include under-declared incidents, shifted change-failure denominator, no-op deployments, changes in service/traffic mix, or worsening user outcomes hidden by aggregate delivery metrics. Audit event definitions, incident declarations/linking, missingness and customer evidence; segment responsibly and pair DORA metrics with SLO outcomes before claiming improvement.

**Common wrong answer(s) / failure modes**

Declaring success because all three delivery metrics improved, or asserting deliberate gaming without evidence.

**Why the wrong answer is wrong**

The pattern indicates competing signals and possible definition drift; it raises hypotheses but does not prove intent or cause.

**Evidence / assumption note**

Synthetic scorecard; investigate evidence before making attribution or misconduct claims.

### U11-Q008 — Artifact interpretation

- **Question ID:** `U11-Q008`
- **Scope:** Unit 11
- **Level:** L2
- **Learning objective tested:** lead time
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact B: individual leaderboard; nearest-deploy attribution treated as causal; missing restore time counted as zero. Dashboard status is green, but no independent evidence is supplied.

**Model answer**

There are substantive defects: individual leaderboard; nearest-deploy attribution treated as causal; missing restore time counted as zero. Repair with Define event boundaries and denominators, preserve missingness, audit attribution sensitivity, segment responsibly, protect privacy, and pair delivery flow with SLO/customer outcomes. Verify with a positive, negative, missing-data and boundary test.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U11-Q009 — Artifact interpretation

- **Question ID:** `U11-Q009`
- **Scope:** Unit 11
- **Level:** L3
- **Learning objective tested:** change failure rate
- **Estimated time:** 6 minutes
- **Question type:** Artifact interpretation

**Prompt / artifact / scenario**

Read this artifact and state what it proves, what it does not prove, and the next safe verification step.

> Artifact C: Twelve production deployment attempts include three qualifying failed changes; two incidents have missing restore timestamps.

**Model answer**

CFR = 3/12 = 25% under the supplied definitions. Time to restore cannot be reliably computed for incidents with missing timestamps; do not substitute zero or silently hide missingness.

**Common wrong answer(s) / failure modes**

Assuming the displayed status proves the complete user outcome or ignoring missing context.

**Why the wrong answer is wrong**

Artifact interpretation must separate observation from inference and name the test that would reduce uncertainty.

**Evidence / assumption note**

Synthetic artifact; values and assumptions are illustrative.

### U11-Q010 — Artifact review

- **Question ID:** `U11-Q010`
- **Scope:** Unit 11
- **Level:** L3
- **Learning objective tested:** change failure rate
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> individual leaderboard; nearest-deploy attribution treated as causal; missing restore time counted as zero; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) individual leaderboard; nearest-deploy attribution treated as causal; missing restore time counted as zero; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Define event boundaries and denominators, preserve missingness, audit attribution sensitivity, segment responsibly, protect privacy, and pair delivery flow with SLO/customer outcomes. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U11-Q011 — Artifact review

- **Question ID:** `U11-Q011`
- **Scope:** Unit 11
- **Level:** L3
- **Learning objective tested:** time to restore
- **Estimated time:** 10 minutes
- **Question type:** Artifact review

**Prompt / artifact / scenario**

Review this flawed excerpt. Identify at least three substantive defects, prioritize critical blockers, rewrite the relevant part, and specify verification.

> individual leaderboard; nearest-deploy attribution treated as causal; missing restore time counted as zero; no named owner; no verification/rollback criterion; missing-data behavior is unspecified.

**Model answer**

Defects include: (1) individual leaderboard; nearest-deploy attribution treated as causal; missing restore time counted as zero; (2) no named owner/decision right; (3) no verification or rollback criterion; (4) missing-data behavior is unspecified. Repair: Define event boundaries and denominators, preserve missingness, audit attribution sensitivity, segment responsibly, protect privacy, and pair delivery flow with SLO/customer outcomes. Add owner, bounded scope, test cases for expected and failure behavior, and recorded acceptance evidence. Critical blockers are unsafe scope, incorrect measurement, and lack of rollback; wording/style is lower priority.

**Common wrong answer(s) / failure modes**

Fixing cosmetic wording only, or listing problems without repairs and tests.

**Why the wrong answer is wrong**

A review must link each defect to operational risk and provide a verifiable correction.

**Evidence / assumption note**

All excerpts are synthetic. Validate exact configuration syntax with the relevant tool/version.

### U11-Q012 — Incident/triage scenario

- **Question ID:** `U11-Q012`
- **Scope:** Unit 11
- **Level:** L3
- **Learning objective tested:** Safe incident response
- **Estimated time:** 10 minutes
- **Question type:** Incident/triage scenario

**Prompt / artifact / scenario**

Lead time improves but SLO attainment worsens and declared incidents fall sharply.

**Model answer**

Audit definitions, missingness, incident declaration/linking, deployment meaning and customer outcomes before claiming improvement; use system-level measures rather than ranking people.

**Common wrong answer(s) / failure modes**

Wait for confirmed root cause before declaration or mitigation.

**Why the wrong answer is wrong**

The operational sequence is stabilize/mitigate first, diagnose second, fix third; communication and verification continue throughout.

**Evidence / assumption note**

Synthetic incident; apply the organization’s severity and escalation policy.

### U11-Q013 — Design question

- **Question ID:** `U11-Q013`
- **Scope:** Unit 11
- **Level:** L4
- **Learning objective tested:** Design a measurable, safe, auditable control
- **Estimated time:** 20 minutes
- **Question type:** Design question

**Prompt / artifact / scenario**

Design an operational control for deployment frequency and gaming/privacy. Include objective, event/data boundary, owner, safety limits, decision rights, failure behavior, rollback, verification, and review cadence.

**Model answer**

A strong design states the user/operational outcome, precise measurement and exclusions, owner, threshold rationale, missing-data behavior, safe scope, decision/override rights, rollback/abort conditions, and evidence-based acceptance. **10-point rubric:** outcome/definition 2; boundary and data quality 2; safety/rollback 2; ownership/governance 2; test evidence and review 2. Acceptable alternatives are context-dependent if their trade-offs are explicit. Common omissions: unowned controls, assumed-good missing data, no test or rollback.

**Common wrong answer(s) / failure modes**

A tool list without measurable outcomes, decision rights, or tests.

**Why the wrong answer is wrong**

A design must be testable, owned, and explicit about risk and alternatives.

**Evidence / assumption note**

Rubric and synthetic design assumptions are provided in the answer.

### U11-Q014 — Numeric/application

- **Question ID:** `U11-Q014`
- **Scope:** Unit 11
- **Level:** L2
- **Learning objective tested:** Apply the unit decision rule to supplied evidence
- **Estimated time:** 7 minutes
- **Question type:** Numeric/application

**Prompt / artifact / scenario**

Twelve production deployment attempts include three qualifying failed changes; two incidents have missing restore timestamps.

**Model answer**

CFR = 3/12 = 25% under the supplied definitions. Time to restore cannot be reliably computed for incidents with missing timestamps; do not substitute zero or silently hide missingness.

**Common wrong answer(s) / failure modes**

Skipping the formula, units, event boundaries, or uncertainty.

**Why the wrong answer is wrong**

The result is not reproducible unless inputs, assumptions and decision rule are explicit.

**Evidence / assumption note**

Illustrative numbers and simplified models; do not generalize to production without validation.

## Cross-unit integration scenarios
Each scenario combines at least two named units; each answer integrates evidence, response, and verification. All incidents/data are synthetic.

### XINT-Q001 — SLO burn, noisy alerts and declaration

- **Question ID:** `XINT-Q001`
- **Scope:** Cross-unit — Units 1, 3, 4
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

An illustrative 30-minute window shows 4× burn, but alerts disagree and routing is uncertain. Decide the response order.

**Model answer**

Declare from credible impact, validate independent SLI evidence, use fallback contact if routing is uncertain, mitigate and communicate. Repair routing after stabilization.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q002 — Inference latency and retry amplification

- **Question ID:** `XINT-Q002`
- **Scope:** Cross-unit — Units 2, 3, 6
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Inference p99 doubles; dependency latency rises; two client layers each retry twice and queue depth grows.

**Model answer**

Bound retries/deadlines, shed or defer noncritical work, isolate the dependency, verify latency/error/fallback SLIs, then test the cascade in a disposable environment.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q003 — Batch freshness and stale pushed metric

- **Question ID:** `XINT-Q003`
- **Scope:** Cross-unit — Units 2, 3, 8
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

A pipeline stops but a push-based success metric retains yesterday’s value and the dashboard is green.

**Model answer**

Treat the metric as stale/unknown; verify output watermark and expected partitions, notify consumers, and add heartbeat freshness and dead-pipeline detection.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q004 — Streaming lag after dependency outage

- **Question ID:** `XINT-Q004`
- **Scope:** Cross-unit — Units 2, 6
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Arrival rate is 9,000/min and recovered processing capacity is 10,000/min with 120,000 events behind.

**Model answer**

Net catch-up is 1,000/min, so ideal clearance is 120 minutes absent new bursts/failures. Check time lag, correctness, duplicates and downstream capacity before promising recovery.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q005 — Model quality regression during canary

- **Question ID:** `XINT-Q005`
- **Scope:** Cross-unit — Units 2, 8, 9
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Availability is normal but fallback ratio and a quality proxy worsen; 15% budget remains.

**Model answer**

Apply defined canary abort/rollback policy, treat proxy limits explicitly, verify user outcome and budget, and classify change failure according to stated production-exposure rules.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q006 — CFR competing incident links

- **Question ID:** `XINT-Q006`
- **Scope:** Cross-unit — Units 5, 11
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Ten production attempts include one confirmed change-caused incident and one merely time-adjacent dependency incident.

**Model answer**

Confirmed-link CFR is 1/10=10%; nearest-deploy attribution could report 2/10=20% but is not causal proof. Report definitions and sensitivity.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q007 — Role confusion and delayed communication

- **Question ID:** `XINT-Q007`
- **Scope:** Cross-unit — Units 4, 5
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

IC debugs code, technical lead writes updates, and the timeline has no timestamps.

**Model answer**

Clarify roles, establish cadence, mitigate first, reconstruct a sourced timeline, then review coordination controls and assign verifiable actions.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q008 — N−1 headroom plus retry budget

- **Question ID:** `XINT-Q008`
- **Scope:** Cross-unit — Units 6, 9
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Three nodes each sustain 60 rps; demand is 110 rps; a node failure leaves 120 rps nominally, but retries add 20 rps.

**Model answer**

Post-failure offered attempts are 130 rps against 120 capacity. Bound retries, shed demand or add headroom; validate N−1 behavior under the explicit load.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q009 — Toil automation with negative ROI

- **Question ID:** `XINT-Q009`
- **Scope:** Cross-unit — Units 7, 8
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

A monthly task saves 5 minutes but proposed automation needs 2 hours maintenance/month and broad delete privileges.

**Model answer**

Do not automate autonomously. Validate the runbook, narrow privileges, measure real frequency and risk, and consider dry-run or human-approved automation.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q010 — Unsafe runbook preconditions

- **Question ID:** `XINT-Q010`
- **Scope:** Cross-unit — Units 4, 8
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

A runbook says restart all replicas but has no target guard and the service is overloaded.

**Model answer**

Do not execute blindly. Coordinate and mitigate safely, verify target/preconditions, and repair with abort/rollback and SLI verification.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q011 — ORR rollback gap under deadline

- **Question ID:** `XINT-Q011`
- **Scope:** Cross-unit — Units 8, 9
- **Level:** L4
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

A business-critical release has no tested rollback and unresolved downstream ownership.

**Model answer**

Treat as a material readiness gap; test rollback or stage a safer limited release, assign owner, and require documented risk authority, expiry and compensating controls.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q012 — Budget freeze versus security patch

- **Question ID:** `XINT-Q012`
- **Scope:** Cross-unit — Units 4, 8, 9
- **Level:** L4
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Budget is exhausted but an urgent security patch addresses active exposure and policy has an exception path.

**Model answer**

Use the defined IC/security approvals, scope the patch, monitor and preserve rollback, audit the exception, and review outcome afterward.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q013 — On-call overloaded by noisy pages

- **Question ID:** `XINT-Q013`
- **Scope:** Cross-unit — Units 3, 10
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

One responder receives most night pages; many alerts lack owners and runbooks.

**Model answer**

Protect coverage, triage actionability, repair ownership/routing, normalize load by eligible shift, and review fatigue/rest without individual surveillance.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q014 — Primary non-ack and broken secondary

- **Question ID:** `XINT-Q014`
- **Scope:** Cross-unit — Units 3, 4, 10
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Customer-impacting page is unacknowledged and the secondary route fails.

**Model answer**

Use independent fallback, declare/coordinate, mitigate and communicate; later test escalation end to end and add dead-routing meta-monitoring.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q015 — Alert receiver outage

- **Question ID:** `XINT-Q015`
- **Scope:** Cross-unit — Units 3, 4, 10
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Rules evaluate but webhook delivery is broken during degradation.

**Model answer**

Use independent contact/monitoring, inspect pipeline stages, mitigate and only close after delivery path is verified; do not rely on the failed receiver to report itself.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q016 — Wildcard silence suppresses critical page

- **Question ID:** `XINT-Q016`
- **Scope:** Cross-unit — Units 3, 9
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Maintenance silence matches every alert for a service.

**Model answer**

Narrow matchers, bound duration, document reason/owner, test critical alert delivery and use a specific maintenance-aware policy rather than blanket muting.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q017 — Blameful postmortem without actions

- **Question ID:** `XINT-Q017`
- **Scope:** Cross-unit — Units 5, 7
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Report says “responder was careless”; only action is “be careful”.

**Model answer**

Rewrite around system conditions and evidence; add owner, due date, preventive control, verification test and tracking.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q018 — Manual toil competes with reliability investment

- **Question ID:** `XINT-Q018`
- **Scope:** Cross-unit — Units 7, 9
- **Level:** L4
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Small toil savings compete with a high-risk dependency isolation project.

**Model answer**

Compare measured toil and expected risk reduction, frequency, maintenance and opportunity cost; prioritize by user risk rather than convenience alone.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q019 — Gate fails open on stale budget

- **Question ID:** `XINT-Q019`
- **Scope:** Cross-unit — Units 1, 9
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Budget cache is eight hours old and gate defaults to allow.

**Model answer**

Represent stale state as unknown; apply explicit fallback/exception policy, log source timestamp and policy version, and test stale/missing/malformed data.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q020 — Gate blocks incident rollback

- **Question ID:** `XINT-Q020`
- **Scope:** Cross-unit — Units 4, 9
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Strict release gate blocks rollback needed to mitigate active impact.

**Model answer**

Use explicit audited incident-response override; distinguish rollback/mitigation from risky forward release and verify recovery.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q021 — DORA improves while SLO worsens

- **Question ID:** `XINT-Q021`
- **Scope:** Cross-unit — Units 1, 9, 11
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Lead time improves 20% while user success declines and incidents rise.

**Model answer**

Audit definitions, segment mix and attribution; pair delivery measures with SLO/customer outcomes and do not claim improvement until trade-offs are understood.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q022 — Empty deployments inflate frequency

- **Question ID:** `XINT-Q022`
- **Scope:** Cross-unit — Units 8, 11
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Team creates no-op production deployments to improve frequency.

**Model answer**

Audit event meaning and production scope, exclude meaningless events under a documented definition, and pair throughput with reliability/outcomes.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q023 — CFR improves as incident declarations fall

- **Question ID:** `XINT-Q023`
- **Scope:** Cross-unit — Units 4, 5, 11
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

CFR falls, complaints persist, and restore timestamps disappear.

**Model answer**

Audit declaration policy, missingness, customer evidence and incident linkage; do not substitute zero or reward under-reporting.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q024 — Data platform compared with mobile app

- **Question ID:** `XINT-Q024`
- **Scope:** Cross-unit — Units 2, 11
- **Level:** L4
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Leadership ranks raw lead-time averages across unlike services.

**Model answer**

Define comparable event boundaries and segments; compare trends in context and pair with workload-specific SLOs rather than ranking teams.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q025 — Squash merges double-counted

- **Question ID:** `XINT-Q025`
- **Scope:** Cross-unit — Units 5, 11
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Pipeline counts original commits and squash merge as separate changes.

**Model answer**

Define stable change identity, deduplicate, test merge styles, and recompute distributions with reconciliation evidence.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q026 — Canary aborts counted as failures

- **Question ID:** `XINT-Q026`
- **Scope:** Cross-unit — Units 8, 9, 11
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Teams are penalized for aborting canaries that prevent exposure.

**Model answer**

Separate safe prevention from qualifying customer-impacting failure under a documented rule; pair CFR with rollout safety to avoid incentives to disable canaries.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q027 — Self-service changes deployment volume

- **Question ID:** `XINT-Q027`
- **Scope:** Cross-unit — Units 7, 8, 11
- **Level:** L4
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Platform reduces approval waiting and deployment count rises.

**Model answer**

Interpret volume with lead time, failure/rework, SLOs and platform adoption; preserve event definitions and detect no-op events.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q028 — Batch backfill competes with inference

- **Question ID:** `XINT-Q028`
- **Scope:** Cross-unit — Units 2, 6, 9
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Backfill consumes database connections and inference tail latency breaches its SLO.

**Model answer**

Throttle/pause backfill, isolate pools or quotas, protect customer path, verify inference SLIs and define resumption criteria.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q029 — Stream replay creates duplicates

- **Question ID:** `XINT-Q029`
- **Scope:** Cross-unit — Units 2, 6, 8
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Replay reduces lag but duplicate count rises.

**Model answer**

Treat correctness as part of recovery; bound replay, validate idempotency/deduplication, and verify lag plus correctness before closure.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q030 — Fatigue slows acknowledgement

- **Question ID:** `XINT-Q030`
- **Scope:** Cross-unit — Units 4, 5, 10
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Response times worsen after repeated night pages.

**Model answer**

Protect coverage, reduce non-actionable pages, rebalance load and review rest policy; analyze system contributors without blaming an individual.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q031 — Non-idempotent automation retry

- **Question ID:** `XINT-Q031`
- **Scope:** Cross-unit — Units 6, 7, 8
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Timeout triggers retry of a write that may already have succeeded.

**Model answer**

Stop uncontrolled retries, inspect state, add idempotency/state checks, bounded attempts and postcondition verification; test with disposable data.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q032 — Fault injection endpoint ambiguous

- **Question ID:** `XINT-Q032`
- **Scope:** Cross-unit — Units 6, 8
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Lab endpoint variable points to shared staging instead of local-only service.

**Model answer**

Abort before mutation. Require allowlisted local context, explicit guard and dry-run; test that the guard fails closed.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q033 — SLO telemetry missing at release time

- **Question ID:** `XINT-Q033`
- **Scope:** Cross-unit — Units 1, 9
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

No SLO samples for 40 minutes and a release decision is due.

**Model answer**

Treat state as unknown, validate telemetry and alternate evidence, follow policy/authorized exception and record uncertainty; never infer zero errors.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q034 — Dependency failure creates downstream page storm

- **Question ID:** `XINT-Q034`
- **Scope:** Cross-unit — Units 3, 4, 6
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Shared dependency failure triggers 30 pages with unclear ownership.

**Model answer**

Coordinate a shared incident, assign dependency/consumer leads, group carefully and preserve distinct user symptoms; use only scoped tested inhibition.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q035 — Action item says be careful

- **Question ID:** `XINT-Q035`
- **Scope:** Cross-unit — Units 5, 7
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Recurring incident action list contains only training reminders.

**Model answer**

Specify owner, due date, control change, test/acceptance evidence and tracking; prefer preventive controls where feasible.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q036 — Cost reduction removes headroom

- **Question ID:** `XINT-Q036`
- **Scope:** Cross-unit — Units 6, 9
- **Level:** L4
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Proposal removes 25% spare capacity; restoration time worsens in tests.

**Model answer**

Compare savings with N−1/catch-up risk and user impact; preserve justified headroom or add shedding/quotas, then test peak/failure recovery.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q037 — No downstream data-contract owner

- **Question ID:** `XINT-Q037`
- **Scope:** Cross-unit — Units 2, 8
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Pipeline schema changes affect a consumer but no team owns the contract.

**Model answer**

Treat as readiness gap; assign parties, define compatibility/freshness/correctness, add alert/runbook and launch condition.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q038 — Customer symptom with normal CPU

- **Question ID:** `XINT-Q038`
- **Scope:** Cross-unit — Units 1, 2, 3, 5
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Customers report incorrect outputs while CPU and memory look normal.

**Model answer**

Use user-centric correctness/quality SLIs, triage model/data/dependency path, mitigate and verify; healthy resource metrics do not negate user impact.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q039 — Unrealistic follow-the-sun proposal

- **Question ID:** `XINT-Q039`
- **Scope:** Cross-unit — Units 4, 10
- **Level:** L4
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Four people are expected to cover three time zones continuously with no secondary staffing.

**Model answer**

Calculate leave/rest/skills/overlap/handoff coverage; disclose gaps, reduce coverage promises or add staffing/fallback.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q040 — Executive requests DORA individual ranking

- **Question ID:** `XINT-Q040`
- **Scope:** Cross-unit — Units 5, 11
- **Level:** L4
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Leadership asks for engineer leaderboard based on deployment frequency and lead time.

**Model answer**

Decline individual ranking; explain confounding and gaming, report system trends with privacy protections and reliability outcomes.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q041 — Scorecard rewards harmful exclusion

- **Question ID:** `XINT-Q041`
- **Scope:** Cross-unit — Units 1, 2, 11
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Success ratio improves after all authentication failures are excluded.

**Model answer**

Audit user impact and eligibility semantics, narrow justified exclusions, version definitions, compare independent client evidence and include access outcomes.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q042 — Monitoring outage during degradation

- **Question ID:** `XINT-Q042`
- **Scope:** Cross-unit — Units 3, 4, 8
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Metrics stop while customers report errors.

**Model answer**

Use backup evidence and communication, declare from credible impact, mitigate, restore monitoring and mark SLI unknown during the gap.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q043 — Freeze override authority unclear

- **Question ID:** `XINT-Q043`
- **Scope:** Cross-unit — Units 4, 9
- **Level:** L4
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Policy says leadership may override but names no role or audit rule.

**Model answer**

Define decision rights, reason, scope, expiry, compensating controls, record and review; escalate rather than invent informal authority.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q044 — Average passes but tail breaches

- **Question ID:** `XINT-Q044`
- **Scope:** Cross-unit — Units 1, 2, 3
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Average latency is 70 ms while a critical tail objective is breached.

**Model answer**

Use the specified tail/threshold-ratio SLI, segment critical journeys and investigate slow cohorts; average cannot prove tail compliance.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q045 — Batch succeeds with zero rows

- **Question ID:** `XINT-Q045`
- **Scope:** Cross-unit — Units 2, 3, 8
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Job exits 0 with zero rows although data is expected.

**Model answer**

Treat as potential correctness/completeness incident, protect publication, check expected partitions/watermark, notify consumers and add zero-row validation.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q046 — Stale metric masks stopped pipeline

- **Question ID:** `XINT-Q046`
- **Scope:** Cross-unit — Units 2, 3, 8
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Success gauge retains its prior value after producer dies.

**Model answer**

Use freshness timestamp/TTL and independent heartbeat/dead-pipeline alert; verify after process termination in a lab.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q047 — Temporal deployment link without evidence

- **Question ID:** `XINT-Q047`
- **Scope:** Cross-unit — Units 5, 11
- **Level:** L3
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Incident begins four minutes after deploy, but traces show dependency errors across versions.

**Model answer**

Keep attribution unconfirmed; compare cohorts/traces, report CFR sensitivity and do not infer causation from proximity.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

### XINT-Q048 — Automate before manual runbook validated

- **Question ID:** `XINT-Q048`
- **Scope:** Cross-unit — Units 7, 8
- **Level:** L4
- **Learning objective tested:** Integrate evidence, safe response, and operational governance across multiple units.
- **Estimated time:** 12 minutes
- **Question type:** Cross-unit integration scenario

**Prompt / scenario**

Team wants autonomous restart bot for poorly understood failure.

**Model answer**

Validate and rehearse manual procedure, define preconditions/abort/rollback, then automate a narrow idempotent step with dry-run, approval, bounds, audit and tests.

**Common wrong answer(s) / failure modes**

Optimizing one tool or metric in isolation, acting on unverified assumptions, or skipping impact assessment, ownership, communication and recovery verification.

**Why the wrong answer is wrong**

The scenario couples failure modes; a local fix can move risk elsewhere or conceal user impact.

**Evidence / assumption note**

All incidents and data are synthetic. Apply stated policy; where it is absent, state what evidence and decision authority are required.

## Design-review whiteboard prompts
Exactly 14 prompts. These are additional and are not counted toward the 190 numbered-question minimum.

### Whiteboard 1: Design SLOs for a data platform

- **Question ID:** `WB-01`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Produce service map, user journeys, SLI/SLO worksheet, ownership and review plan for batch and streaming consumers.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Freshness, completeness, correctness, consumer boundary, low volume, missing telemetry, dependency contracts and budget policy.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Tiered objectives by consumer criticality can be preferable when cost and fairness are explicit.

**10-point rubric**

Outcome/SLIs 2; boundaries/windows 2; workload fit 2; ownership 2; tests/evidence 2.

**Common failure modes**

Pod uptime only or one global ratio hides tenant impact.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Tiered objectives by consumer criticality can be preferable when cost and fairness are explicit.

### Whiteboard 2: Design SLOs for batch freshness

- **Question ID:** `WB-02`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Produce watermark timeline, freshness/completeness objective and breach procedure for an hourly feed.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Expected partitions, watermark semantics/timezone, late data, backfill, no-data and correctness.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Event-based objective may fit better when each partition is the unit of consumer value.

**10-point rubric**

Watermark 2; freshness/coverage 2; missing data 2; consumer agreement 2; tests 2.

**Common failure modes**

Job exit success is treated as fresh output.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Event-based objective may fit better when each partition is the unit of consumer value.

### Whiteboard 3: Design an alerting strategy from SLOs

- **Question ID:** `WB-03`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Produce page/ticket/dashboard taxonomy and route tests for availability, latency and missing metrics.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

SLO burn, owner/runbook, no-data watchdog, grouping/inhibition, route-delivery tests.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Separate critical-journey pages when distinct response actions are required.

**10-point rubric**

SLO linkage 2; actionability 2; missing data 2; routing 2; tests 2.

**Common failure modes**

Every resource threshold pages or no series means zero.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Separate critical-journey pages when distinct response actions are required.

### Whiteboard 4: Design severity and command for a small team

- **Question ID:** `WB-04`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Five-person team handles two incidents with normal chat unavailable; produce severity matrix and fallback comms.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Impact/urgency, declaration, IC/technical/comms roles, role combinations, cadence, timeline.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Combined roles may fit low-severity incidents with explicit split triggers.

**10-point rubric**

Impact 2; roles 2; mitigation 2; fallback comms 2; tabletop evidence 2.

**Common failure modes**

Wait for root cause or overload IC without trade-off.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Combined roles may fit low-severity incidents with explicit split triggers.

### Whiteboard 5: Design a blameless postmortem program

- **Question ID:** `WB-05`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Produce workflow, report template, review gate and action tracking for recurring incidents.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Sourced timeline, impact/budget, evidence versus hypotheses, conditions, control hierarchy, owners/dates/tests.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Lightweight review can fit low-impact incidents if recurrence risk is still tracked.

**10-point rubric**

Impact/timeline 2; causal reasoning 2; systems framing 2; actions 3; follow-through 1.

**Common failure modes**

Remove names but retain “be careful” actions.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Lightweight review can fit low-impact incidents if recurrence risk is still tracked.

### Whiteboard 6: Design defenses against cascading failure

- **Question ID:** `WB-06`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Inference, database and batch workloads share dependencies; produce dependency graph and load model.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Deadlines, bounded retries, retry budget, jitter, bounded queues, admission, bulkheads, shedding, N−1/catch-up.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Degrade noncritical features if full redundancy is cost-prohibitive.

**10-point rubric**

Failure model 2; retry/deadline 2; isolation/backpressure 2; N−1 2; safe tests 2.

**Common failure modes**

Add replicas but leave unbounded retries/shared bottlenecks.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Degrade noncritical features if full redundancy is cost-prohibitive.

### Whiteboard 7: Design safe operational automation

- **Question ID:** `WB-07`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Produce threat model, state machine and acceptance tests for remediation.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Scope guards, preconditions, dry-run, idempotency, bounds, approval, audit, postconditions, rollback/watchdog and ROI.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Human-approved automation fits high-impact or ambiguous actions.

**10-point rubric**

Scope/safety 2; idempotency/bounds 2; approval/audit 2; tests/rollback 2; ROI 2.

**Common failure modes**

Autonomous wildcard mutation without validated manual process.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Human-approved automation fits high-impact or ambiguous actions.

### Whiteboard 8: Design runbooks and ORR/PRR gating

- **Question ID:** `WB-08`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Produce evidence checklist and gate decisions for inference API and data pipeline.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Ownership, SLOs, tested alerts, dependencies, capacity, security, rollback, on-call, exception expiry.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Staged launch with traffic cap and exit criteria may manage residual risk.

**10-point rubric**

Evidence 3; operational controls 2; rollback/dependency 2; exception governance 2; verification 1.

**Common failure modes**

Pass checklist without evidence links.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Staged launch with traffic cap and exit criteria may manage residual risk.

### Whiteboard 9: Design error-budget and freeze governance

- **Question ID:** `WB-09`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Budget telemetry may be stale; urgent security fixes occur during freezes; produce policy state machine.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Measurable bands, workload-specific criteria, freshness, allow/block/unknown, override authority, audit, canary/recovery.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Risk-tiered online/batch policies can be justified by different impact models.

**10-point rubric**

Clarity 2; telemetry 2; exceptions 2; rollout/rollback 2; tests/audit 2.

**Common failure modes**

“Freeze if bad” or verbal override.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Risk-tiered online/batch policies can be justified by different impact models.

### Whiteboard 10: Design sustainable on-call for four people

- **Question ID:** `WB-10`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Produce coverage math, rota, escalation and load-review plan with uneven night pages.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Leave/rest, primary/secondary, eligible shifts, fairness, page triage, handoffs, pager failure, privacy and limits.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Reduced support window plus managed escalation may be safer.

**10-point rubric**

Coverage 2; rest/fairness 2; escalation/fallback 2; alert quality 2; evidence/privacy 2.

**Common failure modes**

Promise 24×7 coverage without staffing math.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Reduced support window plus managed escalation may be safer.

### Whiteboard 11: Design a DORA measurement program

- **Question ID:** `WB-11`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Leadership wants cross-team comparison; restore timestamps and incident links are incomplete.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Event definitions, sources, data quality, segments, attribution, anti-gaming, privacy, SLO pairing.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Use trend-only internal reporting until data quality is reliable.

**10-point rubric**

Definitions 2; data quality 2; attribution 2; governance/privacy 2; balanced outcomes 2.

**Common failure modes**

Rank individuals or treat missing restore as zero.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Use trend-only internal reporting until data quality is reliable.

### Whiteboard 12: Prioritize reliability investment under budget constraint

- **Question ID:** `WB-12`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Choose among toil reduction, shared dependency isolation and dashboards; produce decision matrix.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Risk reduction, user impact, frequency, maintenance, uncertainty, opportunity cost and control hierarchy.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Fund measurement first if uncertainty dominates the decision.

**10-point rubric**

Impact/risk 2; evidence 2; cost 2; trade-offs 2; staged verification 2.

**Common failure modes**

Choose easiest task without risk analysis.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Fund measurement first if uncertainty dominates the decision.

### Whiteboard 13: Design readiness for loss of tooling

- **Question ID:** `WB-13`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

Monitoring, alert delivery or communications may fail; produce fallback map and drill plan.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Independent paths, roles, secure contacts, status updates, path-failure detection and drills.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Multiple fallback tiers can vary by severity.

**10-point rubric**

Independence 2; roles 2; comms 2; drills 2; privacy/maintenance 2.

**Common failure modes**

Backup relies on the same failed dependency.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Multiple fallback tiers can vary by severity.

### Whiteboard 14: Design an SRE engagement and handback model

- **Question ID:** `WB-14`
- **Scope:** Cross-unit design review
- **Level:** L4
- **Learning objective tested:** Defend a measurable, safe, owned design under explicit constraints.
- **Estimated time:** 30–45 minutes
- **Question type:** Design-review whiteboard prompt

**Scenario and constraints**

A platform/SRE team temporarily supports a product team with unclear ownership; produce charter and exit plan.

**What the learner must produce**

A diagram or written proposal, decision table, assumptions, owners, operational boundaries and verification plan.

**Required considerations and trade-offs**

Service owner, SLO/alert responsibilities, runbook/on-call readiness, exit criteria, transfer and exception governance.

**Model approach / reference solution**

A defensible design satisfies the scenario and makes evidence, owners, risk, failure handling and rollback explicit. Alternative: Long-term managed operation can fit if product team cannot safely own it and governance funds it.

**10-point rubric**

Ownership 2; SLO/alerts 2; readiness 2; handback 2; governance 2.

**Common failure modes**

Indefinite shared ownership with no decision rights.

**Evidence needed to defend the design**

Reviewed design artifact, synthetic test results, owner sign-off, stated assumptions, failure-mode coverage and acceptance criteria. No live production change is required.

**Acceptable alternatives and when preferable**

Long-term managed operation can fit if product team cannot safely own it and governance funds it.

## Scoring and remediation
### Course progression thresholds
- **80% or higher — Proceed:** learner demonstrates sufficient command to move forward, while continuing normal review.
- **60%–79% — Remediate:** revisit weak units, redo relevant labs, and retry missed artifact/numeric questions.
- **Below 60% — Repeat:** revisit foundational material, complete guided practice, and retake the assessment.

These are course progression rules, not professional certification or proof of production readiness.

### Scorecard
| Score area | Scoring method | Remediation if weak |
|---|---|---|
| Per-unit score U01–U11 | Points earned / points available per unit | Revisit chapter and repeat relevant labs with new data |
| Cross-unit integration | Score each scenario for synthesis, safety, ownership and verification | Rehearse incident timelines and decision records |
| Practical-artifact score | Defects identified, fixes, tests and blocker priority | Rebuild artifact and validate positive/negative/missing-data cases |
| Design-review score | Each whiteboard uses a 10-point rubric | Redraw and defend trade-offs with evidence |

### Critical-failure items
Remediation is required regardless of total score if the learner:
- proceeds with destructive fault injection when target may be production/shared or a scope guard fails;
- exposes credentials or private customer/employee data;
- delays declaration/mitigation during active customer impact solely to establish root cause or ignores the safe escalation path;
- executes a destructive runbook action without required target/precondition checks and rollback;
- treats missing/stale SLO telemetry as proof of health or silently substitutes zero for missing restore data.

### Remediation map
| Missed objective | Revisit | Suggested lab/evidence |
|---|---|---|
| Service-level indicators, objectives, and error budgets | Unit 1 | SLO worksheet, budget arithmetic, denominator-collapse exercise |
| Reliability targets for batch, streaming, and inference | Unit 2 | Freshness watermark, stream catch-up and correctness exercise |
| Alert quality, noise reduction, and escalation policies | Unit 3 | Rule/routing tests, absent-series and watchdog test |
| Incident severity, roles, and command structure | Unit 4 | Severity tabletop, role switch and fallback communication drill |
| Production triage and blameless postmortems | Unit 5 | Timeline reconstruction, blameless rewrite and action verification |
| Capacity-related failures and cascading outages | Unit 6 | Capacity/cascade model, retry-storm and N−1 test |
| Toil reduction and operational automation | Unit 7 | Toil inventory, ROI sensitivity and idempotency tests |
| Runbook design and operational readiness reviews | Unit 8 | Runbook linting, defect repair, rollback and ORR evidence |
| Error-budget policies and release freezes | Unit 9 | Policy-as-code gate tests for stale data, emergency patch and rollback |
| On-call rotations, handoffs, and sustainable paging | Unit 10 | Synthetic load report, fairness and dead-routing drill |
| DORA metrics and engineering performance measurement | Unit 11 | Deployment/incident linker, CFR sensitivity and metrics charter audit |

### Retest process
1. Identify the missed objective. 2. Re-read the relevant chapter and redo the linked lab in a disposable environment. 3. Use new synthetic values or a changed failure condition. 4. Explain formulas, evidence, assumptions and verification aloud. 5. Re-score and record remaining uncertainty.

## Coverage and authenticity audit
### Question-count audit
| Section | Unique IDs | Required minimum | Status |
|---|---:|---:|---|
| Unit 01 | 14 | 13 | PASS |
| Unit 02 | 14 | 13 | PASS |
| Unit 03 | 14 | 13 | PASS |
| Unit 04 | 14 | 13 | PASS |
| Unit 05 | 14 | 13 | PASS |
| Unit 06 | 14 | 13 | PASS |
| Unit 07 | 14 | 13 | PASS |
| Unit 08 | 14 | 13 | PASS |
| Unit 09 | 14 | 13 | PASS |
| Unit 10 | 14 | 13 | PASS |
| Unit 11 | 14 | 13 | PASS |
| Unit-specific subtotal | 154 | 150 | PASS |
| Cross-unit integration | 48 | 40 | PASS |
| **Grand total numbered questions** | **202** | **190** | **PASS** |
| Additional whiteboard prompts | 14 | exactly 14 | PASS |

Whiteboards are additional and are not counted toward the 190 numbered-question minimum.

### Coverage matrix
| Requirement | Evidence | Status | Limitation / action |
|---|---|---|---|
| Unit 1: Service-level indicators, objectives, and error budgets | U01-Q001–Q014 | PARTIAL | Unit 1 chapter file unavailable; syllabus prompt used. |
| Unit 2: Reliability targets for batch, streaming, and inference | U02-Q001–Q014 | PASS | Chapter artifact present locally; no line-by-line audit claimed. |
| Unit 3: Alert quality, noise reduction, and escalation policies | U03-Q001–Q014 | PASS | Chapter artifact present locally; no line-by-line audit claimed. |
| Unit 4: Incident severity, roles, and command structure | U04-Q001–Q014 | PASS | Chapter artifact present locally; no line-by-line audit claimed. |
| Unit 5: Production triage and blameless postmortems | U05-Q001–Q014 | PASS | Chapter artifact present locally; no line-by-line audit claimed. |
| Unit 6: Capacity-related failures and cascading outages | U06-Q001–Q014 | PASS | Chapter artifact present locally; no line-by-line audit claimed. |
| Unit 7: Toil reduction and operational automation | U07-Q001–Q014 | PASS | Chapter artifact present locally; no line-by-line audit claimed. |
| Unit 8: Runbook design and operational readiness reviews | U08-Q001–Q014 | PASS | Chapter artifact present locally; no line-by-line audit claimed. |
| Unit 9: Error-budget policies and release freezes | U09-Q001–Q014 | PASS | Chapter artifact present locally; no line-by-line audit claimed. |
| Unit 10: On-call rotations, handoffs, and sustainable paging | U10-Q001–Q014 | PASS | Chapter artifact present locally; no line-by-line audit claimed. |
| Unit 11: DORA metrics and engineering performance measurement | U11-Q001–Q014 | PASS | Chapter artifact present locally; no line-by-line audit claimed. |
| 40 cross-unit scenarios | XINT-Q001–Q048 | PASS | Scenarios identify multiple units and integrated answers. |
| 14 whiteboard prompts | WB-01–WB-14 | PASS | Separate from question count. |
| Mandatory question patterns | U01-Q007/Q014, U03-Q007, U04-Q012, U05-Q004/Q005, U06-Q006, U07-Q014, U09-Q004, U10-Q004, U11-Q007 | PASS | Explicit prompts cover SLI/SLO critique, budget arithmetic, alert firing, IC action, blameful rewrite, hierarchy, cascade, automation ROI, freeze, rotation sustainability and metric hiding. |
| Four-option MCQs with distractor explanations | U01–U11, Q004–Q006 | PASS | Three distractors explained per MCQ. |
| Two artifact reviews with 3+ defects per unit | U01–U11, Q010–Q011 | PASS | Repairs and verification included. |
| Metadata and model answer | All Uxx and XINT blocks | PASS (structural) | Structural presence checked; expert content review still required. |
| Scoring and remediation | Scoring section | PASS | Thresholds match requested course progression wording. |
| Repository boundary | Standalone artifact | PARTIAL | No writable repository checkout was available; no repository mutation is claimed. |

### Structural and authenticity checks
- Intended distribution per unit: 3 conceptual short answers, 3 MCQs with A–D, 3 artifact interpretations, 2 artifact reviews, 1 incident/triage scenario, 1 design question, and 1 additional application question.
- Each unit question includes ID, scope, level, objective, time, type, prompt, model answer, common failure, explanation, and evidence/assumption note.
- Artifact reviews identify multiple substantive defects and include concrete repair and verification guidance.
- All scenarios, numerical values, timelines and thresholds authored here are synthetic/illustrative. No DORA benchmark bands or real incidents are claimed.
- Prometheus/PromQL/Alertmanager behavior is version-sensitive; verify exact syntax and edge cases against installed versions.
- No live service, cluster, pager, ORR, fault injection, or external system was executed.

## Source and assumption register
- **Primary specification:** local `PROMPT-Site-Reliability-Engineering-and-Incident-Management.md`, including Unit 1–11 syllabus and Unit 12 requirements.
- **Tree inspected:** local `Roadmap(20261028-154953).md` excerpt listing M10, Units 1–11, Projects, README, prompt and practice-question target. A file literally named `Roadmap_ptree.md` was not available; a differently named roadmap copy was used.
- **Chapter files:** Unit 2–11 Markdown artifacts were present locally; their filenames were checked, but a complete line-by-line audit of every chapter was not performed. Unit 1 chapter was unavailable.
- **Unavailable for direct inspection:** M10 README, M10 Projects content, writable repository checkout.
- **External verification:** no web research was performed; no current vendor claims or benchmark bands are asserted.
- **Execution:** static structural checks only; no Prometheus, Alertmanager, production service, cluster or external command was run.

## Final limitation
This is a standalone question bank aligned to the detailed syllabus prompt and available Unit 2–11 chapter artifacts. It is not certified as fully chapter-verified because Unit 1 and several repository-level source files were unavailable. The actual repository path was not writable or verified; only this standalone file was created.
