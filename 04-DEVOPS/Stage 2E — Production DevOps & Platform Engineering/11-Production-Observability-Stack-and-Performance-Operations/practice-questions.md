# M11 Practice Question Bank — Production Observability Stack and Performance Operations

**Purpose.** A self-contained assessment bank that tests foundations, artifact reading, configuration review, incident diagnosis, and cross-unit design judgment for M11.

| Metadata | Value |
|---|---|
| Module | M11 — Production Observability Stack and Performance Operations |
| Stage | Stage 2E — Production DevOps & Platform Engineering |
| Target | `11-Production-Observability-Stack-and-Performance-Operations/practice-questions.md` |
| Question count rule | Count unique explicit question IDs only; options, subparts, and rubric criteria do not count. |
| Source basis | Current uploaded question-bank prompt. Search results exposed partial content from M11 lesson files Unit 1, Unit 10, Unit 11, Unit 12, and Unit 13; those lessons were not read in full. |
| Source limitations | The authoritative `Roadmap_ptree.md`, full M11 syllabus-generation prompt, all Units 2–9 lesson bodies, `Projects/README.md`, and both capstone specs were not located/inspected in this run. Therefore this bank follows the detailed curriculum map in the supplied prompt but cannot claim complete cross-check against the unavailable sources. |
| Tool documentation | No live official documentation was consulted. Version-sensitive PromQL, LogQL, Collector, Grafana, and Alertmanager details are marked `[VERIFY]`. |

**Status:** DRAFT-AUDITED — AI self-audit; human verification required.

## Table of contents

- [How to use and score this bank](#how-to-use-and-score-this-bank)
- [Question schema and difficulty levels](#question-schema-and-difficulty-levels)
- [Units 1–13](#units-113)
  - [Unit 1 — Production telemetry architecture and retention](#unit-1--production-telemetry-architecture-and-retention)
  - [Unit 2 — Prometheus metrics, scraping, and PromQL](#unit-2--prometheus-metrics-scraping-and-promql)
  - [Unit 3 — Grafana dashboards and dashboard-as-code](#unit-3--grafana-dashboards-and-dashboard-as-code)
  - [Unit 4 — Loki and centralized log pipelines](#unit-4--loki-and-centralized-log-pipelines)
  - [Unit 5 — OpenTelemetry Collector and trace pipelines](#unit-5--opentelemetry-collector-and-trace-pipelines)
  - [Unit 6 — Alertmanager routing, silencing, and on-call integration](#unit-6--alertmanager-routing-silencing-and-on-call-integration)
  - [Unit 7 — Service dependencies and end-to-end failure correlation](#unit-7--service-dependencies-and-end-to-end-failure-correlation)
  - [Unit 8 — Actionable alerts and symptom-based monitoring](#unit-8--actionable-alerts-and-symptom-based-monitoring)
  - [Unit 9 — Saturation, queue depth, and resource exhaustion](#unit-9--saturation-queue-depth-and-resource-exhaustion)
  - [Unit 10 — Distributed trace analysis and bottleneck isolation](#unit-10--distributed-trace-analysis-and-bottleneck-isolation)
  - [Unit 11 — Scheduled-job freshness and deadline monitoring](#unit-11--scheduled-job-freshness-and-deadline-monitoring)
  - [Unit 12 — Observability cost, cardinality, and data retention](#unit-12--observability-cost-cardinality-and-data-retention)
  - [Unit 13 — Production load, stress, and soak testing](#unit-13--production-load-stress-and-soak-testing)
- [Cross-unit integration scenarios](#cross-unit-integration-scenarios)
  - [Design-review whiteboard prompts](#design-review-whiteboard-prompts)
  - [Additional integration scenarios](#additional-integration-scenarios)
- [Question inventory and coverage matrix](#question-inventory-and-coverage-matrix)
- [Ten-pass audit and sign-off](#ten-pass-audit-and-sign-off)
  - [Open verification register](#open-verification-register)
  - [References and verification notes](#references-and-verification-notes)

## How to use and score this bank

1. Attempt each question before reading its model answer; record confidence and the evidence used.
2. For every diagnosis, separate **observed fact**, **hypothesis**, and **next discriminating test**.
3. Recompute every calculation from the supplied fixture; all scenario values are synthetic unless explicitly stated otherwise.
4. **[ILLUSTRATIVE] Readiness bands:** 80% or higher — proceed; 60–79% — remediate weak topics and retry; below 60% — revisit lessons and repeat. These are study guidance, not a certification standard.
5. For safety- or evidence-integrity questions, unsafe reasoning fails the item even if the aggregate score is high.

### Scoring guidance

- **MCQ:** 4 points; one for the correct option and up to three for explaining distractors.
- **Artifact interpretation:** 5 points; conclusion, evidence/calculation, limitation, next check.
- **Artifact review:** 8 points; defects, corrected plan, validation/version caveat.
- **Incident diagnosis:** 12 points; impact, first action, differential diagnosis, evidence, safe mitigation, verification, prevention.
- **Design / integration:** use each item’s explicit rubric. Partial credit rewards supported uncertainty and safe reasoning; unsupported certainty or unsafe mitigation earns no credit for the affected criterion.

## Question schema and difficulty levels

Every item includes ID, scope, type, level, objective, estimated time, prompt/artifact, model answer, rationale, common failure modes, scoring, source note, and version/assumption note.

- **L1:** define, identify, classify, or read a simple artifact.
- **L2:** apply a known method, interpret output, calculate, or repair a common defect.
- **L3:** diagnose interacting failures, compare hypotheses, quantify uncertainty, or test a control.
- **L4:** justify system-level reliability/cost/governance decisions with ownership, rollback, and acceptance criteria.

All sample telemetry, incident packets, counts, timestamps, and snippets are `[SYNTHETIC]` or `[ILLUSTRATIVE]`. Exact syntax or behavior that depends on installed versions is `[VERIFY]`. No real vendor prices are used. Load scenarios are hypothetical/local-lab-only; never target unauthorized systems.

## Units 1–13

## Unit 1 — Production telemetry architecture and retention

**Coverage:** signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring

### U01-SA-01 — Short answer

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational production telemetry architecture and retention concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in production telemetry architecture and retention and give one example of a question it answers.
- **Artifact/scenario:** An API p99 rises while error rate remains flat; a metric shows when/how much, a trace shows the request path, logs show event details, and a deployment event supplies change context.
- **Model answer:** Choose the least costly signal that can answer a specific operational question, then trace its collection, processing, storage, query, alerting, ownership, and failure boundaries.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring.
- **Version / assumption note:** No version-sensitive behavior required

### U01-SA-02 — Short answer

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational production telemetry architecture and retention concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** An API p99 rises while error rate remains flat; a metric shows when/how much, a trace shows the request path, logs show event details, and a deployment event supplies change context.
- **Model answer:** Use this evidence: An API p99 rises while error rate remains flat; a metric shows when/how much, a trace shows the request path, logs show event details, and a deployment event supplies change context. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring.
- **Version / assumption note:** No version-sensitive behavior required

### U01-SA-03 — Short answer

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational production telemetry architecture and retention concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected production telemetry architecture and retention failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** An API p99 rises while error rate remains flat; a metric shows when/how much, a trace shows the request path, logs show event details, and a deployment event supplies change context.
- **Model answer:** Core profile for metrics and essential alerts; add logs only when incident questions require them; use traces selectively. Keep local-only, redact sensitive fields, and monitor telemetry pipeline health.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring.
- **Version / assumption note:** No version-sensitive behavior required

### U01-MCQ-01 — MCQ

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for production telemetry architecture and retention.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Treat missing observations as zero and infer that the service is healthy.
  - **B.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **C.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **D.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
- **Artifact/scenario:** An API p99 rises while error rate remains flat; a metric shows when/how much, a trace shows the request path, logs show event details, and a deployment event supplies change context.
- **Model answer:** **Correct option: C.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **B:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **D:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring.
- **Version / assumption note:** No version-sensitive behavior required

### U01-MCQ-02 — MCQ

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for production telemetry architecture and retention.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **B.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **C.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **D.** Treat missing observations as zero and infer that the service is healthy.
- **Artifact/scenario:** A service emits 120 metric series at 15-second scrape intervals; local retention is 7 days. A dashboard is useful but the local disk is 80% full.
- **Model answer:** **Correct option: B.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **C:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **D:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring.
- **Version / assumption note:** No version-sensitive behavior required

### U01-MCQ-03 — MCQ

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for production telemetry architecture and retention.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **B.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **C.** Treat missing observations as zero and infer that the service is healthy.
  - **D.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
- **Artifact/scenario:** A service emits 120 metric series at 15-second scrape intervals; local retention is 7 days. A dashboard is useful but the local disk is 80% full.
- **Model answer:** **Correct option: A.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **B:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **C:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **D:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring.
- **Version / assumption note:** No version-sensitive behavior required

### U01-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to production telemetry architecture and retention.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** An API p99 rises while error rate remains flat; a metric shows when/how much, a trace shows the request path, logs show event details, and a deployment event supplies change context.
- **Model answer:** The artifact supports this conclusion: Choose the least costly signal that can answer a specific operational question, then trace its collection, processing, storage, query, alerting, ownership, and failure boundaries. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U01-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to production telemetry architecture and retention.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** A service emits 120 metric series at 15-second scrape intervals; local retention is 7 days. A dashboard is useful but the local disk is 80% full.
- **Model answer:** It hides the distinction between signal selection and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U01-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to production telemetry architecture and retention.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** An API p99 rises while error rate remains flat; a metric shows when/how much, a trace shows the request path, logs show event details, and a deployment event supplies change context.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U01-REV-01 — Artifact review

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
profile: full
metrics:
  labels: [service, request_id]
logs:
  retention_days: 365
pipeline_health_alerts: false
owner: 
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Telemetry architecture):**
1. Request/user identifiers are unbounded metric labels and create privacy/cardinality risk.
2. Retention is excessive/implicit and no resource budget or pipeline-health alert is defined.
3. No owner or redaction policy exists.

**Corrected artifact / plan:** Use bounded dimensions, keep identifiers out of metric labels, define measured retention and resource budgets, redact sensitive fields, add pipeline-health canaries, and assign an owner/runbook. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U01-REV-02 — Artifact review

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
telemetry:
  traces: all_requests
  resource_limits: null
privacy:
  redact_fields: []
retention_policy: "implicit"
owner: 
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Telemetry architecture):**
1. Request/user identifiers are unbounded metric labels and create privacy/cardinality risk.
2. Retention is excessive/implicit and no resource budget or pipeline-health alert is defined.
3. No owner or redaction policy exists.

**Corrected artifact / plan:** Use bounded dimensions, keep identifiers out of metric labels, define measured retention and resource budgets, redact sensitive fields, add pipeline-health canaries, and assign an owner/runbook. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U01-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to production telemetry architecture and retention.
- Fixture: An API p99 rises while error rate remains flat; a metric shows when/how much, a trace shows the request path, logs show event details, and a deployment event supplies change context.
- Additional context: A service emits 120 metric series at 15-second scrape intervals; local retention is 7 days. A dashboard is useful but the local disk is 80% full.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Choose the least costly signal that can answer a specific operational question, then trace its collection, processing, storage, query, alerting, ownership, and failure boundaries.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U01-DES-01 — Design

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for production telemetry architecture and retention.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for production telemetry architecture and retention. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** A service emits 120 metric series at 15-second scrape intervals; local retention is 7 days. A dashboard is useful but the local disk is 80% full.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.

### U01-EXT-01 — Additional unit question

- **Scope / unit:** Unit 1 — Production telemetry architecture and retention
- **Question type:** Additional unit question
- **Level:** L3
- **Objective tested:** Extend the core fixture with one testable failure mode in production telemetry architecture and retention.
- **Estimated time:** 9 minutes
- **Question prompt:** Evaluate one additional failure mode not covered by the core fixture and propose a targeted test.
- **Artifact/scenario:** Using An API p99 rises while error rate remains flat; a metric shows when/how much, a trace shows the request path, logs show event details, and a deployment event supplies change context., construct a negative test that distinguishes a real zero from missing/stale evidence. State the expected output and cleanup.
- **Model answer:** The added test extends coverage without duplicating the required question categories; the expected result should be falsifiable and safe.
- **Rationale / evidence:** ['Add an unbounded workload or external dependency merely to make the test realistic.', 'Accept a test without a negative case or cleanup.']
- **Common wrong answers / failure modes:**
  1. 5
  2.  
- **Scoring rubric:** signal selection, telemetry lifecycle, resource profiles, retention, privacy, and meta-monitoring
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; [ASSUMPTION] local test harness..
- **Version / assumption note:** No version-sensitive behavior required


## Unit 2 — Prometheus metrics, scraping, and PromQL

**Coverage:** metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests

### U02-SA-01 — Short answer

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational prometheus metrics, scraping, and promql concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in prometheus metrics, scraping, and promql and give one example of a question it answers.
- **Artifact/scenario:** Synthetic counter samples: 100, 130, 165 at t=0, 30s, 60s. A gauge reports queue depth 4, 8, 12. Scrape interval is 15s.
- **Model answer:** Interpret series and query semantics using explicit labels, timestamps, scrape intervals, and evaluation context; distinguish zero, absent, stale, and failed collection.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests.
- **Version / assumption note:** No version-sensitive behavior required

### U02-SA-02 — Short answer

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational prometheus metrics, scraping, and promql concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** Synthetic counter samples: 100, 130, 165 at t=0, 30s, 60s. A gauge reports queue depth 4, 8, 12. Scrape interval is 15s.
- **Model answer:** Use this evidence: Synthetic counter samples: 100, 130, 165 at t=0, 30s, 60s. A gauge reports queue depth 4, 8, 12. Scrape interval is 15s. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests.
- **Version / assumption note:** No version-sensitive behavior required

### U02-SA-03 — Short answer

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational prometheus metrics, scraping, and promql concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected prometheus metrics, scraping, and promql failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** Synthetic counter samples: 100, 130, 165 at t=0, 30s, 60s. A gauge reports queue depth 4, 8, 12. Scrape interval is 15s.
- **Model answer:** Use rate/increase for counters with adequate windows; aggregate histogram buckets while preserving le before histogram_quantile; test missing-series and label-matching cases.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests.
- **Version / assumption note:** No version-sensitive behavior required

### U02-MCQ-01 — MCQ

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for prometheus metrics, scraping, and promql.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **B.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **C.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **D.** Treat missing observations as zero and infer that the service is healthy.
- **Artifact/scenario:** Synthetic counter samples: 100, 130, 165 at t=0, 30s, 60s. A gauge reports queue depth 4, 8, 12. Scrape interval is 15s.
- **Model answer:** **Correct option: B.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **C:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **D:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests.
- **Version / assumption note:** No version-sensitive behavior required

### U02-MCQ-02 — MCQ

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for prometheus metrics, scraping, and promql.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **B.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **C.** Treat missing observations as zero and infer that the service is healthy.
  - **D.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
- **Artifact/scenario:** Histogram fixture: request_duration_seconds_bucket{le="0.1"}=40, {le="0.5"}=90, {le="1"}=98, {le="+Inf"}=100 for one service and window.
- **Model answer:** **Correct option: A.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **B:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **C:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **D:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests.
- **Version / assumption note:** No version-sensitive behavior required

### U02-MCQ-03 — MCQ

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for prometheus metrics, scraping, and promql.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **B.** Treat missing observations as zero and infer that the service is healthy.
  - **C.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **D.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
- **Artifact/scenario:** Histogram fixture: request_duration_seconds_bucket{le="0.1"}=40, {le="0.5"}=90, {le="1"}=98, {le="+Inf"}=100 for one service and window.
- **Model answer:** **Correct option: D.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **B:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **C:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests.
- **Version / assumption note:** No version-sensitive behavior required

### U02-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to prometheus metrics, scraping, and promql.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** Synthetic counter samples: 100, 130, 165 at t=0, 30s, 60s. A gauge reports queue depth 4, 8, 12. Scrape interval is 15s.
- **Model answer:** The artifact supports this conclusion: Interpret series and query semantics using explicit labels, timestamps, scrape intervals, and evaluation context; distinguish zero, absent, stale, and failed collection. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U02-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to prometheus metrics, scraping, and promql.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** Histogram fixture: request_duration_seconds_bucket{le="0.1"}=40, {le="0.5"}=90, {le="1"}=98, {le="+Inf"}=100 for one service and window.
- **Model answer:** It hides the distinction between metric types and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U02-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to prometheus metrics, scraping, and promql.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** Synthetic counter samples: 100, 130, 165 at t=0, 30s, 60s. A gauge reports queue depth 4, 8, 12. Scrape interval is 15s.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U02-REV-01 — Artifact review

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```promql
# [SYNTHETIC] PromQL
rate(queue_depth[15s])
# joins request rate to per-pod metadata on service only
sum(rate(api_requests_total[1m])) / sum(rate(api_requests_total{status=~"5.."}[1m]))
# no explicit missing-series test
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Prometheus/PromQL):**
1. `rate(queue_depth[15s])` applies counter-rate semantics to a gauge and uses a very short range for the stated scrape cadence.
2. The vector join is not shown to have unique matching keys and may be many-to-many.
3. The error ratio expression reverses numerator/denominator intent and lacks absent-series tests/ownership.

**Corrected artifact / plan:** Query the gauge directly or explicitly analyze its change; choose a window with multiple samples for counters; aggregate vectors to unique keys before joining; compute error rate over total requests; test absent/low-traffic fixtures and assign ownership. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U02-REV-02 — Artifact review

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```promql
# [SYNTHETIC] rule fragment
- alert: ApiErrors
  expr: rate(api_errors_total[15s]) > 0
  for: 0s
# rule has no owner/runbook labels and no unit tests
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Prometheus/PromQL):**
1. `rate(queue_depth[15s])` applies counter-rate semantics to a gauge and uses a very short range for the stated scrape cadence.
2. The vector join is not shown to have unique matching keys and may be many-to-many.
3. The error ratio expression reverses numerator/denominator intent and lacks absent-series tests/ownership.

**Corrected artifact / plan:** Query the gauge directly or explicitly analyze its change; choose a window with multiple samples for counters; aggregate vectors to unique keys before joining; compute error rate over total requests; test absent/low-traffic fixtures and assign ownership. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U02-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to prometheus metrics, scraping, and promql.
- Fixture: Synthetic counter samples: 100, 130, 165 at t=0, 30s, 60s. A gauge reports queue depth 4, 8, 12. Scrape interval is 15s.
- Additional context: Histogram fixture: request_duration_seconds_bucket{le="0.1"}=40, {le="0.5"}=90, {le="1"}=98, {le="+Inf"}=100 for one service and window.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Interpret series and query semantics using explicit labels, timestamps, scrape intervals, and evaluation context; distinguish zero, absent, stale, and failed collection.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U02-DES-01 — Design

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for prometheus metrics, scraping, and promql.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for prometheus metrics, scraping, and promql. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** Histogram fixture: request_duration_seconds_bucket{le="0.1"}=40, {le="0.5"}=90, {le="1"}=98, {le="+Inf"}=100 for one service and window.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.

### U02-EXT-01 — Additional unit question

- **Scope / unit:** Unit 2 — Prometheus metrics, scraping, and PromQL
- **Question type:** Additional unit question
- **Level:** L3
- **Objective tested:** Extend the core fixture with one testable failure mode in prometheus metrics, scraping, and promql.
- **Estimated time:** 9 minutes
- **Question prompt:** Evaluate one additional failure mode not covered by the core fixture and propose a targeted test.
- **Artifact/scenario:** Using Synthetic counter samples: 100, 130, 165 at t=0, 30s, 60s. A gauge reports queue depth 4, 8, 12. Scrape interval is 15s., construct a negative test that distinguishes a real zero from missing/stale evidence. State the expected output and cleanup.
- **Model answer:** The added test extends coverage without duplicating the required question categories; the expected result should be falsifiable and safe.
- **Rationale / evidence:** ['Add an unbounded workload or external dependency merely to make the test realistic.', 'Accept a test without a negative case or cleanup.']
- **Common wrong answers / failure modes:**
  1. 5
  2.  
- **Scoring rubric:** metric types, scrape targets, PromQL, rates, histograms, missing data, cardinality, and rule tests
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; [ASSUMPTION] local test harness..
- **Version / assumption note:** No version-sensitive behavior required


## Unit 3 — Grafana dashboards and dashboard-as-code

**Coverage:** panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift

### U03-SA-01 — Short answer

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational grafana dashboards and dashboard-as-code concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in grafana dashboards and dashboard-as-code and give one example of a question it answers.
- **Artifact/scenario:** Panel A shows mean latency 80 ms; panel B has p99 900 ms; one instance has 5% errors but is excluded by `{instance!="api-3"}`.
- **Model answer:** Read a panel as an operational argument: query, aggregation, units, time range, legend, missing-data behavior, and links must support a diagnostic decision.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift.
- **Version / assumption note:** No version-sensitive behavior required

### U03-SA-02 — Short answer

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational grafana dashboards and dashboard-as-code concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** Panel A shows mean latency 80 ms; panel B has p99 900 ms; one instance has 5% errors but is excluded by `{instance!="api-3"}`.
- **Model answer:** Use this evidence: Panel A shows mean latency 80 ms; panel B has p99 900 ms; one instance has 5% errors but is excluded by `{instance!="api-3"}`. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift.
- **Version / assumption note:** No version-sensitive behavior required

### U03-SA-03 — Short answer

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational grafana dashboards and dashboard-as-code concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected grafana dashboards and dashboard-as-code failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** Panel A shows mean latency 80 ms; panel B has p99 900 ms; one instance has 5% errors but is excluded by `{instance!="api-3"}`.
- **Model answer:** Version-control dashboard definitions, validate JSON/schema against installed Grafana, review queries and permissions, and detect drift rather than editing production panels invisibly.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift.
- **Version / assumption note:** No version-sensitive behavior required

### U03-MCQ-01 — MCQ

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for grafana dashboards and dashboard-as-code.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **B.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **C.** Treat missing observations as zero and infer that the service is healthy.
  - **D.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
- **Artifact/scenario:** Panel A shows mean latency 80 ms; panel B has p99 900 ms; one instance has 5% errors but is excluded by `{instance!="api-3"}`.
- **Model answer:** **Correct option: A.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **B:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **C:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **D:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift.
- **Version / assumption note:** No version-sensitive behavior required

### U03-MCQ-02 — MCQ

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for grafana dashboards and dashboard-as-code.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **B.** Treat missing observations as zero and infer that the service is healthy.
  - **C.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **D.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
- **Artifact/scenario:** Provisioned dashboard declares a 5-minute range and unit `s`, but query outputs milliseconds; a variable is interpolated into a broad selector.
- **Model answer:** **Correct option: D.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **B:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **C:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift.
- **Version / assumption note:** No version-sensitive behavior required

### U03-MCQ-03 — MCQ

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for grafana dashboards and dashboard-as-code.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Treat missing observations as zero and infer that the service is healthy.
  - **B.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **C.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **D.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
- **Artifact/scenario:** Provisioned dashboard declares a 5-minute range and unit `s`, but query outputs milliseconds; a variable is interpolated into a broad selector.
- **Model answer:** **Correct option: C.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **B:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **D:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift.
- **Version / assumption note:** No version-sensitive behavior required

### U03-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to grafana dashboards and dashboard-as-code.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** Panel A shows mean latency 80 ms; panel B has p99 900 ms; one instance has 5% errors but is excluded by `{instance!="api-3"}`.
- **Model answer:** The artifact supports this conclusion: Read a panel as an operational argument: query, aggregation, units, time range, legend, missing-data behavior, and links must support a diagnostic decision. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U03-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to grafana dashboards and dashboard-as-code.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** Provisioned dashboard declares a 5-minute range and unit `s`, but query outputs milliseconds; a variable is interpolated into a broad selector.
- **Model answer:** It hides the distinction between panel queries and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U03-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to grafana dashboards and dashboard-as-code.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** Panel A shows mean latency 80 ms; panel B has p99 900 ms; one instance has 5% errors but is excluded by `{instance!="api-3"}`.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U03-REV-01 — Artifact review

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```json
{
  "title": "API latency",
  "targets": [{"expr": "api_latency_ms{instance!="api-3"}"}],
  "fieldConfig": {"defaults": {"unit": "s"}},
  "time": {"from": "now-30d", "to": "now"}
}
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Grafana dashboard):**
1. The query excludes the failing instance.
2. The panel unit is seconds while the metric is milliseconds.
3. The long time range/unsafe variable or empty description impairs incident use and review.

**Corrected artifact / plan:** Include all intended instances, convert units or configure the matching unit, use a bounded time range and validated variables, add description/owner/links, and validate dashboard JSON/schema against the installed Grafana version. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U03-REV-02 — Artifact review

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```json
{
  "title": "Errors",
  "targets": [{"expr": "sum(rate(api_errors_total[5m]))"}],
  "templating": {"list": [{"name": "request_id", "query": ".*"}]},
  "description": ""
}
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Grafana dashboard):**
1. The query excludes the failing instance.
2. The panel unit is seconds while the metric is milliseconds.
3. The long time range/unsafe variable or empty description impairs incident use and review.

**Corrected artifact / plan:** Include all intended instances, convert units or configure the matching unit, use a bounded time range and validated variables, add description/owner/links, and validate dashboard JSON/schema against the installed Grafana version. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U03-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to grafana dashboards and dashboard-as-code.
- Fixture: Panel A shows mean latency 80 ms; panel B has p99 900 ms; one instance has 5% errors but is excluded by `{instance!="api-3"}`.
- Additional context: Provisioned dashboard declares a 5-minute range and unit `s`, but query outputs milliseconds; a variable is interpolated into a broad selector.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Read a panel as an operational argument: query, aggregation, units, time range, legend, missing-data behavior, and links must support a diagnostic decision.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U03-DES-01 — Design

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for grafana dashboards and dashboard-as-code.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for grafana dashboards and dashboard-as-code. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** Provisioned dashboard declares a 5-minute range and unit `s`, but query outputs milliseconds; a variable is interpolated into a broad selector.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.

### U03-EXT-01 — Additional unit question

- **Scope / unit:** Unit 3 — Grafana dashboards and dashboard-as-code
- **Question type:** Additional unit question
- **Level:** L3
- **Objective tested:** Extend the core fixture with one testable failure mode in grafana dashboards and dashboard-as-code.
- **Estimated time:** 9 minutes
- **Question prompt:** Evaluate one additional failure mode not covered by the core fixture and propose a targeted test.
- **Artifact/scenario:** Using Panel A shows mean latency 80 ms; panel B has p99 900 ms; one instance has 5% errors but is excluded by `{instance!="api-3"}`., construct a negative test that distinguishes a real zero from missing/stale evidence. State the expected output and cleanup.
- **Model answer:** The added test extends coverage without duplicating the required question categories; the expected result should be falsifiable and safe.
- **Rationale / evidence:** ['Add an unbounded workload or external dependency merely to make the test realistic.', 'Accept a test without a negative case or cleanup.']
- **Common wrong answers / failure modes:**
  1. 5
  2.  
- **Scoring rubric:** panel queries, units, variables, legends, RED/USE, provisioning, validation, and drift
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; [ASSUMPTION] local test harness..
- **Version / assumption note:** No version-sensitive behavior required


## Unit 4 — Loki and centralized log pipelines

**Coverage:** event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation

### U04-SA-01 — Short answer

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational loki and centralized log pipelines concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in loki and centralized log pipelines and give one example of a question it answers.
- **Artifact/scenario:** Synthetic source emits 1,000 records; collector reports 1,000 read, 980 sent, 20 dropped; backend ingests 980. Records include service, level, trace_id, and a synthetic token field.
- **Model answer:** Keep indexed labels bounded; preserve high-cardinality values as event fields; distinguish no query results from proof that no event occurred.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation.
- **Version / assumption note:** No version-sensitive behavior required

### U04-SA-02 — Short answer

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational loki and centralized log pipelines concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** Synthetic source emits 1,000 records; collector reports 1,000 read, 980 sent, 20 dropped; backend ingests 980. Records include service, level, trace_id, and a synthetic token field.
- **Model answer:** Use this evidence: Synthetic source emits 1,000 records; collector reports 1,000 read, 980 sent, 20 dropped; backend ingests 980. Records include service, level, trace_id, and a synthetic token field. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation.
- **Version / assumption note:** No version-sensitive behavior required

### U04-SA-03 — Short answer

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational loki and centralized log pipelines concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected loki and centralized log pipelines failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** Synthetic source emits 1,000 records; collector reports 1,000 read, 980 sent, 20 dropped; backend ingests 980. Records include service, level, trace_id, and a synthetic token field.
- **Model answer:** Localize losses by comparing source, collector, and backend counters over aligned windows; fix label explosion and redact before persistence; verify with synthetic canaries.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation.
- **Version / assumption note:** No version-sensitive behavior required

### U04-MCQ-01 — MCQ

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for loki and centralized log pipelines.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **B.** Treat missing observations as zero and infer that the service is healthy.
  - **C.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **D.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
- **Artifact/scenario:** Synthetic source emits 1,000 records; collector reports 1,000 read, 980 sent, 20 dropped; backend ingests 980. Records include service, level, trace_id, and a synthetic token field.
- **Model answer:** **Correct option: D.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **B:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **C:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation.
- **Version / assumption note:** No version-sensitive behavior required

### U04-MCQ-02 — MCQ

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for loki and centralized log pipelines.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Treat missing observations as zero and infer that the service is healthy.
  - **B.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **C.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **D.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
- **Artifact/scenario:** A pipeline labels `user_id` and `request_id`, parses timestamps from inconsistent formats, and redacts only `authorization` but not `token`.
- **Model answer:** **Correct option: C.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **B:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **D:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation.
- **Version / assumption note:** No version-sensitive behavior required

### U04-MCQ-03 — MCQ

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for loki and centralized log pipelines.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **B.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **C.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **D.** Treat missing observations as zero and infer that the service is healthy.
- **Artifact/scenario:** A pipeline labels `user_id` and `request_id`, parses timestamps from inconsistent formats, and redacts only `authorization` but not `token`.
- **Model answer:** **Correct option: B.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **C:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **D:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation.
- **Version / assumption note:** No version-sensitive behavior required

### U04-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to loki and centralized log pipelines.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** Synthetic source emits 1,000 records; collector reports 1,000 read, 980 sent, 20 dropped; backend ingests 980. Records include service, level, trace_id, and a synthetic token field.
- **Model answer:** The artifact supports this conclusion: Keep indexed labels bounded; preserve high-cardinality values as event fields; distinguish no query results from proof that no event occurred. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U04-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to loki and centralized log pipelines.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** A pipeline labels `user_id` and `request_id`, parses timestamps from inconsistent formats, and redacts only `authorization` but not `token`.
- **Model answer:** It hides the distinction between event fields versus labels and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U04-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to loki and centralized log pipelines.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** Synthetic source emits 1,000 records; collector reports 1,000 read, 980 sent, 20 dropped; backend ingests 980. Records include service, level, trace_id, and a synthetic token field.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U04-REV-01 — Artifact review

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
pipeline:
  labels: [service, user_id, request_id]
  parse_timestamp: "auto"
  redact_fields: [authorization]
  owner: ""
  dropped_record_alert: false
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Loki pipeline):**
1. `user_id`/`request_id` labels cause high cardinality.
2. Redaction misses token-like sensitive fields and timestamp parsing silently accepts malformed input.
3. Unbounded retries/no drop alert or owner can hide backpressure and loss.

**Corrected artifact / plan:** Keep labels bounded, redact all policy-defined secret/PII fields before persistence, reject/quarantine malformed timestamps, bound retries/queues, alert on drops, and verify with a synthetic canary. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U04-REV-02 — Artifact review

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
pipeline:
  labels: [service, trace_id, level]
  retries: "unbounded"
  malformed_timestamp: "silently_accept"
  redact_fields: []
  retention_days: 30
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Loki pipeline):**
1. `user_id`/`request_id` labels cause high cardinality.
2. Redaction misses token-like sensitive fields and timestamp parsing silently accepts malformed input.
3. Unbounded retries/no drop alert or owner can hide backpressure and loss.

**Corrected artifact / plan:** Keep labels bounded, redact all policy-defined secret/PII fields before persistence, reject/quarantine malformed timestamps, bound retries/queues, alert on drops, and verify with a synthetic canary. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U04-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to loki and centralized log pipelines.
- Fixture: Synthetic source emits 1,000 records; collector reports 1,000 read, 980 sent, 20 dropped; backend ingests 980. Records include service, level, trace_id, and a synthetic token field.
- Additional context: A pipeline labels `user_id` and `request_id`, parses timestamps from inconsistent formats, and redacts only `authorization` but not `token`.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Keep indexed labels bounded; preserve high-cardinality values as event fields; distinguish no query results from proof that no event occurred.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U04-DES-01 — Design

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for loki and centralized log pipelines.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for loki and centralized log pipelines. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** A pipeline labels `user_id` and `request_id`, parses timestamps from inconsistent formats, and redacts only `authorization` but not `token`.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.

### U04-EXT-01 — Additional unit question

- **Scope / unit:** Unit 4 — Loki and centralized log pipelines
- **Question type:** Additional unit question
- **Level:** L3
- **Objective tested:** Extend the core fixture with one testable failure mode in loki and centralized log pipelines.
- **Estimated time:** 9 minutes
- **Question prompt:** Evaluate one additional failure mode not covered by the core fixture and propose a targeted test.
- **Artifact/scenario:** Using Synthetic source emits 1,000 records; collector reports 1,000 read, 980 sent, 20 dropped; backend ingests 980. Records include service, level, trace_id, and a synthetic token field., construct a negative test that distinguishes a real zero from missing/stale evidence. State the expected output and cleanup.
- **Model answer:** The added test extends coverage without duplicating the required question categories; the expected result should be falsifiable and safe.
- **Rationale / evidence:** ['Add an unbounded workload or external dependency merely to make the test realistic.', 'Accept a test without a negative case or cleanup.']
- **Common wrong answers / failure modes:**
  1. 5
  2.  
- **Scoring rubric:** event fields versus labels, parsing, redaction, ingestion gaps, LogQL, retention, and correlation
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; [ASSUMPTION] local test harness..
- **Version / assumption note:** No version-sensitive behavior required


## Unit 5 — OpenTelemetry Collector and trace pipelines

**Coverage:** receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability

### U05-SA-01 — Short answer

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational opentelemetry collector and trace pipelines concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in opentelemetry collector and trace pipelines and give one example of a question it answers.
- **Artifact/scenario:** Synthetic pipeline: source spans created=10,000; exporter attempted=9,800; Collector send_failed=200; queue occupancy reaches capacity; backend received=9,750 in same aligned window.
- **Model answer:** Use pipeline-stage evidence to localize missing telemetry and distinguish instrumentation absence, filtering, sampling, delay, exporter failure, and backend rejection.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability.
- **Version / assumption note:** No version-sensitive behavior required

### U05-SA-02 — Short answer

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational opentelemetry collector and trace pipelines concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** Synthetic pipeline: source spans created=10,000; exporter attempted=9,800; Collector send_failed=200; queue occupancy reaches capacity; backend received=9,750 in same aligned window.
- **Model answer:** Use this evidence: Synthetic pipeline: source spans created=10,000; exporter attempted=9,800; Collector send_failed=200; queue occupancy reaches capacity; backend received=9,750 in same aligned window. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability.
- **Version / assumption note:** No version-sensitive behavior required

### U05-SA-03 — Short answer

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational opentelemetry collector and trace pipelines concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected opentelemetry collector and trace pipelines failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** Synthetic pipeline: source spans created=10,000; exporter attempted=9,800; Collector send_failed=200; queue occupancy reaches capacity; backend received=9,750 in same aligned window.
- **Model answer:** Validate configuration against the installed distribution/version; monitor receiver/exporter/queue/drop telemetry; do not assume every distribution supports every component.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability.
- **Version / assumption note:** No version-sensitive behavior required

### U05-MCQ-01 — MCQ

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for opentelemetry collector and trace pipelines.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Treat missing observations as zero and infer that the service is healthy.
  - **B.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **C.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **D.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
- **Artifact/scenario:** Synthetic pipeline: source spans created=10,000; exporter attempted=9,800; Collector send_failed=200; queue occupancy reaches capacity; backend received=9,750 in same aligned window.
- **Model answer:** **Correct option: C.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **B:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **D:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability.
- **Version / assumption note:** No version-sensitive behavior required

### U05-MCQ-02 — MCQ

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for opentelemetry collector and trace pipelines.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **B.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **C.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **D.** Treat missing observations as zero and infer that the service is healthy.
- **Artifact/scenario:** Collector pipeline has a receiver but no exporter in the traces pipeline, uses an unverified component name, and sets a queue size without bounded memory strategy.
- **Model answer:** **Correct option: B.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **C:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **D:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability.
- **Version / assumption note:** No version-sensitive behavior required

### U05-MCQ-03 — MCQ

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for opentelemetry collector and trace pipelines.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **B.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **C.** Treat missing observations as zero and infer that the service is healthy.
  - **D.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
- **Artifact/scenario:** Collector pipeline has a receiver but no exporter in the traces pipeline, uses an unverified component name, and sets a queue size without bounded memory strategy.
- **Model answer:** **Correct option: A.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **B:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **C:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **D:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability.
- **Version / assumption note:** No version-sensitive behavior required

### U05-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to opentelemetry collector and trace pipelines.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** Synthetic pipeline: source spans created=10,000; exporter attempted=9,800; Collector send_failed=200; queue occupancy reaches capacity; backend received=9,750 in same aligned window.
- **Model answer:** The artifact supports this conclusion: Use pipeline-stage evidence to localize missing telemetry and distinguish instrumentation absence, filtering, sampling, delay, exporter failure, and backend rejection. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U05-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to opentelemetry collector and trace pipelines.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** Collector pipeline has a receiver but no exporter in the traces pipeline, uses an unverified component name, and sets a queue size without bounded memory strategy.
- **Model answer:** It hides the distinction between receivers and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U05-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to opentelemetry collector and trace pipelines.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** Synthetic pipeline: source spans created=10,000; exporter attempted=9,800; Collector send_failed=200; queue occupancy reaches capacity; backend received=9,750 in same aligned window.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U05-REV-01 — Artifact review

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
receivers: [otlp]
processors:
  - batch
  - memory_limiter
exporters: []
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
# no exporter; queue/resource bound not defined
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (OpenTelemetry Collector):**
1. The traces pipeline has no exporter in one variant, so it cannot deliver to a backend.
2. An exporter/component name is unverified for the installed distribution.
3. Queue/memory bounds and send-failure/drop telemetry are absent.

**Corrected artifact / plan:** Define a compatible exporter, validate config with the installed distribution, set bounded queue/memory/retry behavior, and monitor accepted/sent/failed/dropped counts plus canary spans. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U05-REV-02 — Artifact review

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
receivers: [otlp]
processors: [batch]
exporters:
  - name: exporter-that-may-not-exist [VERIFY]
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [exporter-that-may-not-exist]
# no send-failure/drop monitoring
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (OpenTelemetry Collector):**
1. The traces pipeline has no exporter in one variant, so it cannot deliver to a backend.
2. An exporter/component name is unverified for the installed distribution.
3. Queue/memory bounds and send-failure/drop telemetry are absent.

**Corrected artifact / plan:** Define a compatible exporter, validate config with the installed distribution, set bounded queue/memory/retry behavior, and monitor accepted/sent/failed/dropped counts plus canary spans. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U05-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to opentelemetry collector and trace pipelines.
- Fixture: Synthetic pipeline: source spans created=10,000; exporter attempted=9,800; Collector send_failed=200; queue occupancy reaches capacity; backend received=9,750 in same aligned window.
- Additional context: Collector pipeline has a receiver but no exporter in the traces pipeline, uses an unverified component name, and sets a queue size without bounded memory strategy.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Use pipeline-stage evidence to localize missing telemetry and distinguish instrumentation absence, filtering, sampling, delay, exporter failure, and backend rejection.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U05-DES-01 — Design

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for opentelemetry collector and trace pipelines.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for opentelemetry collector and trace pipelines. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** Collector pipeline has a receiver but no exporter in the traces pipeline, uses an unverified component name, and sets a queue size without bounded memory strategy.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.

### U05-EXT-01 — Additional unit question

- **Scope / unit:** Unit 5 — OpenTelemetry Collector and trace pipelines
- **Question type:** Additional unit question
- **Level:** L3
- **Objective tested:** Extend the core fixture with one testable failure mode in opentelemetry collector and trace pipelines.
- **Estimated time:** 9 minutes
- **Question prompt:** Evaluate one additional failure mode not covered by the core fixture and propose a targeted test.
- **Artifact/scenario:** Using Synthetic pipeline: source spans created=10,000; exporter attempted=9,800; Collector send_failed=200; queue occupancy reaches capacity; backend received=9,750 in same aligned window., construct a negative test that distinguishes a real zero from missing/stale evidence. State the expected output and cleanup.
- **Model answer:** The added test extends coverage without duplicating the required question categories; the expected result should be falsifiable and safe.
- **Rationale / evidence:** ['Add an unbounded workload or external dependency merely to make the test realistic.', 'Accept a test without a negative case or cleanup.']
- **Common wrong answers / failure modes:**
  1. 5
  2.  
- **Scoring rubric:** receivers, processors, exporters, resource attributes, batching, queues, retries, sampling, and self-observability
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; [ASSUMPTION] local test harness..
- **Version / assumption note:** No version-sensitive behavior required


## Unit 6 — Alertmanager routing, silencing, and on-call integration

**Coverage:** labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation

### U06-SA-01 — Short answer

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational alertmanager routing, silencing, and on-call integration concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in alertmanager routing, silencing, and on-call integration and give one example of a question it answers.
- **Artifact/scenario:** Synthetic alert labels: alertname=ApiHighErrorRate, service=checkout, severity=page, team=payments. Route matcher expects team="payment"; receiver is `payments-oncall`.
- **Model answer:** Trace an alert from firing rule through labels, route selection, grouping, receiver configuration, and delivery evidence without assuming a notification was sent.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation.
- **Version / assumption note:** No version-sensitive behavior required

### U06-SA-02 — Short answer

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational alertmanager routing, silencing, and on-call integration concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** Synthetic alert labels: alertname=ApiHighErrorRate, service=checkout, severity=page, team=payments. Route matcher expects team="payment"; receiver is `payments-oncall`.
- **Model answer:** Use this evidence: Synthetic alert labels: alertname=ApiHighErrorRate, service=checkout, severity=page, team=payments. Route matcher expects team="payment"; receiver is `payments-oncall`. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation.
- **Version / assumption note:** No version-sensitive behavior required

### U06-SA-03 — Short answer

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational alertmanager routing, silencing, and on-call integration concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected alertmanager routing, silencing, and on-call integration failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** Synthetic alert labels: alertname=ApiHighErrorRate, service=checkout, severity=page, team=payments. Route matcher expects team="payment"; receiver is `payments-oncall`.
- **Model answer:** Use narrow, time-bounded, owned silences; validate routing with fixtures and delivery evidence; version-sensitive route semantics are [VERIFY].
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation.
- **Version / assumption note:** No version-sensitive behavior required

### U06-MCQ-01 — MCQ

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for alertmanager routing, silencing, and on-call integration.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **B.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **C.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **D.** Treat missing observations as zero and infer that the service is healthy.
- **Artifact/scenario:** Synthetic alert labels: alertname=ApiHighErrorRate, service=checkout, severity=page, team=payments. Route matcher expects team="payment"; receiver is `payments-oncall`.
- **Model answer:** **Correct option: B.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **C:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **D:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation.
- **Version / assumption note:** No version-sensitive behavior required

### U06-MCQ-02 — MCQ

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for alertmanager routing, silencing, and on-call integration.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **B.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **C.** Treat missing observations as zero and infer that the service is healthy.
  - **D.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
- **Artifact/scenario:** A silence has no owner/reason, expires in 72 hours, matches `severity=~".*"`, and there is no external delivery verification.
- **Model answer:** **Correct option: A.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **B:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **C:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **D:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation.
- **Version / assumption note:** No version-sensitive behavior required

### U06-MCQ-03 — MCQ

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for alertmanager routing, silencing, and on-call integration.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **B.** Treat missing observations as zero and infer that the service is healthy.
  - **C.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **D.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
- **Artifact/scenario:** A silence has no owner/reason, expires in 72 hours, matches `severity=~".*"`, and there is no external delivery verification.
- **Model answer:** **Correct option: D.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **B:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **C:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation.
- **Version / assumption note:** No version-sensitive behavior required

### U06-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to alertmanager routing, silencing, and on-call integration.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** Synthetic alert labels: alertname=ApiHighErrorRate, service=checkout, severity=page, team=payments. Route matcher expects team="payment"; receiver is `payments-oncall`.
- **Model answer:** The artifact supports this conclusion: Trace an alert from firing rule through labels, route selection, grouping, receiver configuration, and delivery evidence without assuming a notification was sent. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U06-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to alertmanager routing, silencing, and on-call integration.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** A silence has no owner/reason, expires in 72 hours, matches `severity=~".*"`, and there is no external delivery verification.
- **Model answer:** It hides the distinction between labels and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U06-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to alertmanager routing, silencing, and on-call integration.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** Synthetic alert labels: alertname=ApiHighErrorRate, service=checkout, severity=page, team=payments. Route matcher expects team="payment"; receiver is `payments-oncall`.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U06-REV-01 — Artifact review

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
route:
  receiver: default
  routes:
    - matchers: ['team="payment"']
      receiver: payments
receivers:
  - name: default
  - name: payments
silence:
  matchers: ['severity=~".*"']
  duration: 72h
  owner: 
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Alertmanager):**
1. Route label spelling/value mismatches prevent intended matching.
2. A broad or long-lived silence can suppress unrelated pages and has no owner/expiry rationale.
3. A referenced receiver may be missing and no routing test is supplied.

**Corrected artifact / plan:** Align the label contract, narrow silences by alert/service and set owner/reason/expiry, define every referenced receiver, validate config and run routing fixtures; verify delivery separately. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U06-REV-02 — Artifact review

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
route:
  receiver: default
  group_by: [alertname]
  routes:
    - matchers: ['team="payments"']
      receiver: payments-oncall
receivers:
  - name: default
# referenced receiver absent; no routing test
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Alertmanager):**
1. Route label spelling/value mismatches prevent intended matching.
2. A broad or long-lived silence can suppress unrelated pages and has no owner/expiry rationale.
3. A referenced receiver may be missing and no routing test is supplied.

**Corrected artifact / plan:** Align the label contract, narrow silences by alert/service and set owner/reason/expiry, define every referenced receiver, validate config and run routing fixtures; verify delivery separately. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U06-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to alertmanager routing, silencing, and on-call integration.
- Fixture: Synthetic alert labels: alertname=ApiHighErrorRate, service=checkout, severity=page, team=payments. Route matcher expects team="payment"; receiver is `payments-oncall`.
- Additional context: A silence has no owner/reason, expires in 72 hours, matches `severity=~".*"`, and there is no external delivery verification.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Trace an alert from firing rule through labels, route selection, grouping, receiver configuration, and delivery evidence without assuming a notification was sent.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U06-DES-01 — Design

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for alertmanager routing, silencing, and on-call integration.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for alertmanager routing, silencing, and on-call integration. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** A silence has no owner/reason, expires in 72 hours, matches `severity=~".*"`, and there is no external delivery verification.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.

### U06-EXT-01 — Additional unit question

- **Scope / unit:** Unit 6 — Alertmanager routing, silencing, and on-call integration
- **Question type:** Additional unit question
- **Level:** L3
- **Objective tested:** Extend the core fixture with one testable failure mode in alertmanager routing, silencing, and on-call integration.
- **Estimated time:** 9 minutes
- **Question prompt:** Evaluate one additional failure mode not covered by the core fixture and propose a targeted test.
- **Artifact/scenario:** Using Synthetic alert labels: alertname=ApiHighErrorRate, service=checkout, severity=page, team=payments. Route matcher expects team="payment"; receiver is `payments-oncall`., construct a negative test that distinguishes a real zero from missing/stale evidence. State the expected output and cleanup.
- **Model answer:** The added test extends coverage without duplicating the required question categories; the expected result should be falsifiable and safe.
- **Rationale / evidence:** ['Add an unbounded workload or external dependency merely to make the test realistic.', 'Accept a test without a negative case or cleanup.']
- **Common wrong answers / failure modes:**
  1. 5
  2.  
- **Scoring rubric:** labels, route tree, grouping, receivers, inhibition, silences, templates, delivery, and validation
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; [ASSUMPTION] local test harness..
- **Version / assumption note:** No version-sensitive behavior required


## Unit 7 — Service dependencies and end-to-end failure correlation

**Coverage:** declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization

### U07-SA-01 — Short answer

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational service dependencies and end-to-end failure correlation concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in service dependencies and end-to-end failure correlation and give one example of a question it answers.
- **Artifact/scenario:** Synthetic timeline: checkout p99 rises at 10:04; payment DB pool wait rises at 10:03; deployment to checkout at 10:02; trace shows 700 ms in payment call.
- **Model answer:** Combine multiple signals to identify the best-supported failure boundary, compare alternative hypotheses, and verify causality instead of treating correlation as proof.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization.
- **Version / assumption note:** No version-sensitive behavior required

### U07-SA-02 — Short answer

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational service dependencies and end-to-end failure correlation concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** Synthetic timeline: checkout p99 rises at 10:04; payment DB pool wait rises at 10:03; deployment to checkout at 10:02; trace shows 700 ms in payment call.
- **Model answer:** Use this evidence: Synthetic timeline: checkout p99 rises at 10:04; payment DB pool wait rises at 10:03; deployment to checkout at 10:02; trace shows 700 ms in payment call. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization.
- **Version / assumption note:** No version-sensitive behavior required

### U07-SA-03 — Short answer

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational service dependencies and end-to-end failure correlation concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected service dependencies and end-to-end failure correlation failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** Synthetic timeline: checkout p99 rises at 10:04; payment DB pool wait rises at 10:03; deployment to checkout at 10:02; trace shows 700 ms in payment call.
- **Model answer:** Use a repeatable alert → dashboard → trace/exemplar → logs → change timeline path; record uncertainty and run the next discriminating test.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization.
- **Version / assumption note:** No version-sensitive behavior required

### U07-MCQ-01 — MCQ

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for service dependencies and end-to-end failure correlation.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **B.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **C.** Treat missing observations as zero and infer that the service is healthy.
  - **D.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
- **Artifact/scenario:** Synthetic timeline: checkout p99 rises at 10:04; payment DB pool wait rises at 10:03; deployment to checkout at 10:02; trace shows 700 ms in payment call.
- **Model answer:** **Correct option: A.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **B:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **C:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **D:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization.
- **Version / assumption note:** No version-sensitive behavior required

### U07-MCQ-02 — MCQ

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for service dependencies and end-to-end failure correlation.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **B.** Treat missing observations as zero and infer that the service is healthy.
  - **C.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **D.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
- **Artifact/scenario:** Dependency graph omits payment-cache, a dashboard link points to the wrong service, and an alert includes no change/version context.
- **Model answer:** **Correct option: D.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **B:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **C:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization.
- **Version / assumption note:** No version-sensitive behavior required

### U07-MCQ-03 — MCQ

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for service dependencies and end-to-end failure correlation.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Treat missing observations as zero and infer that the service is healthy.
  - **B.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **C.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **D.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
- **Artifact/scenario:** Dependency graph omits payment-cache, a dashboard link points to the wrong service, and an alert includes no change/version context.
- **Model answer:** **Correct option: C.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **B:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **D:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization.
- **Version / assumption note:** No version-sensitive behavior required

### U07-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to service dependencies and end-to-end failure correlation.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** Synthetic timeline: checkout p99 rises at 10:04; payment DB pool wait rises at 10:03; deployment to checkout at 10:02; trace shows 700 ms in payment call.
- **Model answer:** The artifact supports this conclusion: Combine multiple signals to identify the best-supported failure boundary, compare alternative hypotheses, and verify causality instead of treating correlation as proof. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U07-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to service dependencies and end-to-end failure correlation.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** Dependency graph omits payment-cache, a dashboard link points to the wrong service, and an alert includes no change/version context.
- **Model answer:** It hides the distinction between declared versus observed dependency graphs and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U07-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to service dependencies and end-to-end failure correlation.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** Synthetic timeline: checkout p99 rises at 10:04; payment DB pool wait rises at 10:03; deployment to checkout at 10:02; trace shows 700 ms in payment call.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U07-REV-01 — Artifact review

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
declared_edges:
  - [checkout, payment]
observed_trace_edges:
  - [checkout, risk, payment]
links:
  checkout_dashboard: "/d/wrong-service"
owner: 
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Dependency correlation):**
1. The declared graph omits a dependency visible in traces.
2. A dashboard link points to the wrong service or an illustrative invalid link.
3. No drift detection, correlation fields, or ownership exists.

**Corrected artifact / plan:** Reconcile observed and declared edges after verification, correct context links, define allowed correlation fields, detect graph drift, and assign ownership; test a synthetic incident navigation path. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U07-REV-02 — Artifact review

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
dependency_policy:
  graph_source: declared_only
  drift_detection: false
  correlation_fields: []
  alert_context_link: "https://invalid.example/not-a-real-endpoint"
# illustrative invalid link; do not use as a real target
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Dependency correlation):**
1. The declared graph omits a dependency visible in traces.
2. A dashboard link points to the wrong service or an illustrative invalid link.
3. No drift detection, correlation fields, or ownership exists.

**Corrected artifact / plan:** Reconcile observed and declared edges after verification, correct context links, define allowed correlation fields, detect graph drift, and assign ownership; test a synthetic incident navigation path. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U07-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to service dependencies and end-to-end failure correlation.
- Fixture: Synthetic timeline: checkout p99 rises at 10:04; payment DB pool wait rises at 10:03; deployment to checkout at 10:02; trace shows 700 ms in payment call.
- Additional context: Dependency graph omits payment-cache, a dashboard link points to the wrong service, and an alert includes no change/version context.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Combine multiple signals to identify the best-supported failure boundary, compare alternative hypotheses, and verify causality instead of treating correlation as proof.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U07-DES-01 — Design

- **Scope / unit:** Unit 7 — Service dependencies and end-to-end failure correlation
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for service dependencies and end-to-end failure correlation.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for service dependencies and end-to-end failure correlation. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** Dependency graph omits payment-cache, a dashboard link points to the wrong service, and an alert includes no change/version context.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: declared versus observed dependency graphs, change timelines, metrics/logs/traces, causal reasoning, and localization.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.


## Unit 8 — Actionable alerts and symptom-based monitoring

**Coverage:** user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health

### U08-SA-01 — Short answer

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational actionable alerts and symptom-based monitoring concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in actionable alerts and symptom-based monitoring and give one example of a question it answers.
- **Artifact/scenario:** Synthetic alert rule: `sum(rate(api_requests_total{status=~"5.."}[5m])) / sum(rate(api_requests_total[5m])) > 0.03`; request series disappear when target discovery fails.
- **Model answer:** Decide whether an alert represents user impact and includes enough ownership, context, runbook, and telemetry-health evidence to support action.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health.
- **Version / assumption note:** No version-sensitive behavior required

### U08-SA-02 — Short answer

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational actionable alerts and symptom-based monitoring concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** Synthetic alert rule: `sum(rate(api_requests_total{status=~"5.."}[5m])) / sum(rate(api_requests_total[5m])) > 0.03`; request series disappear when target discovery fails.
- **Model answer:** Use this evidence: Synthetic alert rule: `sum(rate(api_requests_total{status=~"5.."}[5m])) / sum(rate(api_requests_total[5m])) > 0.03`; request series disappear when target discovery fails. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health.
- **Version / assumption note:** No version-sensitive behavior required

### U08-SA-03 — Short answer

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational actionable alerts and symptom-based monitoring concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected actionable alerts and symptom-based monitoring failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** Synthetic alert rule: `sum(rate(api_requests_total{status=~"5.."}[5m])) / sum(rate(api_requests_total[5m])) > 0.03`; request series disappear when target discovery fails.
- **Model answer:** Separate service symptoms from suspected causes; test positive, negative, absent-series, and telemetry-failure cases; watchdogs need an independent path where possible.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health.
- **Version / assumption note:** No version-sensitive behavior required

### U08-MCQ-01 — MCQ

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for actionable alerts and symptom-based monitoring.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **B.** Treat missing observations as zero and infer that the service is healthy.
  - **C.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **D.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
- **Artifact/scenario:** Synthetic alert rule: `sum(rate(api_requests_total{status=~"5.."}[5m])) / sum(rate(api_requests_total[5m])) > 0.03`; request series disappear when target discovery fails.
- **Model answer:** **Correct option: D.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **B:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **C:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health.
- **Version / assumption note:** No version-sensitive behavior required

### U08-MCQ-02 — MCQ

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for actionable alerts and symptom-based monitoring.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Treat missing observations as zero and infer that the service is healthy.
  - **B.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **C.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **D.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
- **Artifact/scenario:** Alert has no owner or runbook, treats missing data as healthy, and fires on a transient one-scrape spike without a test.
- **Model answer:** **Correct option: C.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **B:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **D:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health.
- **Version / assumption note:** No version-sensitive behavior required

### U08-MCQ-03 — MCQ

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for actionable alerts and symptom-based monitoring.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **B.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **C.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **D.** Treat missing observations as zero and infer that the service is healthy.
- **Artifact/scenario:** Alert has no owner or runbook, treats missing data as healthy, and fires on a transient one-scrape spike without a test.
- **Model answer:** **Correct option: B.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **C:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **D:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health.
- **Version / assumption note:** No version-sensitive behavior required

### U08-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to actionable alerts and symptom-based monitoring.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** Synthetic alert rule: `sum(rate(api_requests_total{status=~"5.."}[5m])) / sum(rate(api_requests_total[5m])) > 0.03`; request series disappear when target discovery fails.
- **Model answer:** The artifact supports this conclusion: Decide whether an alert represents user impact and includes enough ownership, context, runbook, and telemetry-health evidence to support action. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U08-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to actionable alerts and symptom-based monitoring.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** Alert has no owner or runbook, treats missing data as healthy, and fires on a transient one-scrape spike without a test.
- **Model answer:** It hides the distinction between user symptoms and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U08-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to actionable alerts and symptom-based monitoring.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** Synthetic alert rule: `sum(rate(api_requests_total{status=~"5.."}[5m])) / sum(rate(api_requests_total[5m])) > 0.03`; request series disappear when target discovery fails.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U08-REV-01 — Artifact review

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
alert:
  name: ApiHighErrors
  expr: error_ratio > 0.03
  labels: {severity: page}
  annotations: {summary: "API errors"}
  owner: ""
  runbook_url: ""
  no_data_policy: "healthy"
  tests: []
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Actionable alert):**
1. Owner/runbook/summary metadata is missing.
2. Missing data is treated as healthy or expected-series absence is not handled.
3. No positive, negative, or telemetry-failure tests exist.

**Corrected artifact / plan:** Add owner/runbook/actionable annotations, explicitly test no-data/absent-series behavior and target health, include telemetry-pipeline health, and test firing, non-firing, and missing-data fixtures. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U08-REV-02 — Artifact review

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
alert:
  name: TargetMissing
  expr: up == 0
  for: 0s
  labels: {severity: page}
  annotations: {}
  owner: platform
  tests: []
# expected-series absence and telemetry pipeline health are not covered
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Actionable alert):**
1. Owner/runbook/summary metadata is missing.
2. Missing data is treated as healthy or expected-series absence is not handled.
3. No positive, negative, or telemetry-failure tests exist.

**Corrected artifact / plan:** Add owner/runbook/actionable annotations, explicitly test no-data/absent-series behavior and target health, include telemetry-pipeline health, and test firing, non-firing, and missing-data fixtures. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U08-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to actionable alerts and symptom-based monitoring.
- Fixture: Synthetic alert rule: `sum(rate(api_requests_total{status=~"5.."}[5m])) / sum(rate(api_requests_total[5m])) > 0.03`; request series disappear when target discovery fails.
- Additional context: Alert has no owner or runbook, treats missing data as healthy, and fires on a transient one-scrape spike without a test.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Decide whether an alert represents user impact and includes enough ownership, context, runbook, and telemetry-health evidence to support action.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U08-DES-01 — Design

- **Scope / unit:** Unit 8 — Actionable alerts and symptom-based monitoring
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for actionable alerts and symptom-based monitoring.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for actionable alerts and symptom-based monitoring. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** Alert has no owner or runbook, treats missing data as healthy, and fires on a transient one-scrape spike without a test.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: user symptoms, page/ticket, metadata, absent data, flapping, tests, watchdogs, and pipeline health.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.


## Unit 9 — Saturation, queue depth, and resource exhaustion

**Coverage:** utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery

### U09-SA-01 — Short answer

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational saturation, queue depth, and resource exhaustion concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in saturation, queue depth, and resource exhaustion and give one example of a question it answers.
- **Artifact/scenario:** Synthetic queue: depth 100 at 12:00, 220 at 12:05, 340 at 12:10; incoming 80 jobs/min, drained 56 jobs/min over the same period.
- **Model answer:** Estimate whether a resource is approaching exhaustion using rate-of-change, service capacity, queue depth, and workload evidence rather than host averages alone.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery.
- **Version / assumption note:** No version-sensitive behavior required

### U09-SA-02 — Short answer

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational saturation, queue depth, and resource exhaustion concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** Synthetic queue: depth 100 at 12:00, 220 at 12:05, 340 at 12:10; incoming 80 jobs/min, drained 56 jobs/min over the same period.
- **Model answer:** Use this evidence: Synthetic queue: depth 100 at 12:00, 220 at 12:05, 340 at 12:10; incoming 80 jobs/min, drained 56 jobs/min over the same period. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery.
- **Version / assumption note:** No version-sensitive behavior required

### U09-SA-03 — Short answer

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational saturation, queue depth, and resource exhaustion concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected saturation, queue depth, and resource exhaustion failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** Synthetic queue: depth 100 at 12:00, 220 at 12:05, 340 at 12:10; incoming 80 jobs/min, drained 56 jobs/min over the same period.
- **Model answer:** Prioritize safe admission control, bounded retries, and queue protection; verify queue drain and user symptoms after mitigation.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery.
- **Version / assumption note:** No version-sensitive behavior required

### U09-MCQ-01 — MCQ

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for saturation, queue depth, and resource exhaustion.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Treat missing observations as zero and infer that the service is healthy.
  - **B.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **C.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **D.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
- **Artifact/scenario:** Synthetic queue: depth 100 at 12:00, 220 at 12:05, 340 at 12:10; incoming 80 jobs/min, drained 56 jobs/min over the same period.
- **Model answer:** **Correct option: C.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **B:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **D:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery.
- **Version / assumption note:** No version-sensitive behavior required

### U09-MCQ-02 — MCQ

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for saturation, queue depth, and resource exhaustion.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **B.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **C.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **D.** Treat missing observations as zero and infer that the service is healthy.
- **Artifact/scenario:** Host CPU average is 35%, but one container is throttled; connection pool has 50/50 in use and wait time is rising.
- **Model answer:** **Correct option: B.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **C:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **D:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery.
- **Version / assumption note:** No version-sensitive behavior required

### U09-MCQ-03 — MCQ

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for saturation, queue depth, and resource exhaustion.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **B.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **C.** Treat missing observations as zero and infer that the service is healthy.
  - **D.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
- **Artifact/scenario:** Host CPU average is 35%, but one container is throttled; connection pool has 50/50 in use and wait time is rising.
- **Model answer:** **Correct option: A.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **B:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **C:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **D:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery.
- **Version / assumption note:** No version-sensitive behavior required

### U09-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to saturation, queue depth, and resource exhaustion.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** Synthetic queue: depth 100 at 12:00, 220 at 12:05, 340 at 12:10; incoming 80 jobs/min, drained 56 jobs/min over the same period.
- **Model answer:** The artifact supports this conclusion: Estimate whether a resource is approaching exhaustion using rate-of-change, service capacity, queue depth, and workload evidence rather than host averages alone. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U09-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to saturation, queue depth, and resource exhaustion.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** Host CPU average is 35%, but one container is throttled; connection pool has 50/50 in use and wait time is rising.
- **Model answer:** It hides the distinction between utilization versus saturation and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U09-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to saturation, queue depth, and resource exhaustion.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** Synthetic queue: depth 100 at 12:00, 220 at 12:05, 340 at 12:10; incoming 80 jobs/min, drained 56 jobs/min over the same period.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U09-REV-01 — Artifact review

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```promql
# host average hides per-container saturation
avg(rate(node_cpu_seconds_total[5m]))
# queue growth and pool wait not shown
# no unit/legend/owner metadata
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Saturation dashboard):**
1. Host CPU average masks per-container throttling.
2. Queue growth, drain rate, and pool wait are omitted.
3. An average queue threshold can hide one overloaded workload and lacks units/ownership.

**Corrected artifact / plan:** Show per-container resource signals, queue depth plus arrival/drain rates and pool wait, use per-service/workload breakdowns, annotate units and ownership, and test with a synthetic overloaded instance. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U09-REV-02 — Artifact review

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```promql
# [SYNTHETIC] query proposal
avg(queue_depth) < 100
# hides a single overloaded service/pod
# no alert for queue growth or drain-rate deficit
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Saturation dashboard):**
1. Host CPU average masks per-container throttling.
2. Queue growth, drain rate, and pool wait are omitted.
3. An average queue threshold can hide one overloaded workload and lacks units/ownership.

**Corrected artifact / plan:** Show per-container resource signals, queue depth plus arrival/drain rates and pool wait, use per-service/workload breakdowns, annotate units and ownership, and test with a synthetic overloaded instance. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U09-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to saturation, queue depth, and resource exhaustion.
- Fixture: Synthetic queue: depth 100 at 12:00, 220 at 12:05, 340 at 12:10; incoming 80 jobs/min, drained 56 jobs/min over the same period.
- Additional context: Host CPU average is 35%, but one container is throttled; connection pool has 50/50 in use and wait time is rising.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Estimate whether a resource is approaching exhaustion using rate-of-change, service capacity, queue depth, and workload evidence rather than host averages alone.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U09-DES-01 — Design

- **Scope / unit:** Unit 9 — Saturation, queue depth, and resource exhaustion
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for saturation, queue depth, and resource exhaustion.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for saturation, queue depth, and resource exhaustion. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** Host CPU average is 35%, but one container is throttled; connection pool has 50/50 in use and wait time is rising.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: utilization versus saturation, queue growth, concurrency, backpressure, capacity margins, and recovery.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.


## Unit 10 — Distributed trace analysis and bottleneck isolation

**Coverage:** span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links

### U10-SA-01 — Short answer

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational distributed trace analysis and bottleneck isolation concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in distributed trace analysis and bottleneck isolation and give one example of a question it answers.
- **Artifact/scenario:** Synthetic waterfall: root 0–900 ms; auth 20–80; profile 100–240; inventory 250–700; pricing 260–500 (parallel with inventory); serialize 710–850.
- **Model answer:** Calculate request wall time and critical path from a supplied waterfall; do not sum overlapping span durations as request latency.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links.
- **Version / assumption note:** No version-sensitive behavior required

### U10-SA-02 — Short answer

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational distributed trace analysis and bottleneck isolation concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** Synthetic waterfall: root 0–900 ms; auth 20–80; profile 100–240; inventory 250–700; pricing 260–500 (parallel with inventory); serialize 710–850.
- **Model answer:** Use this evidence: Synthetic waterfall: root 0–900 ms; auth 20–80; profile 100–240; inventory 250–700; pricing 260–500 (parallel with inventory); serialize 710–850. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links.
- **Version / assumption note:** No version-sensitive behavior required

### U10-SA-03 — Short answer

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational distributed trace analysis and bottleneck isolation concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected distributed trace analysis and bottleneck isolation failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** Synthetic waterfall: root 0–900 ms; auth 20–80; profile 100–240; inventory 250–700; pricing 260–500 (parallel with inventory); serialize 710–850.
- **Model answer:** Use parent-child timing and parallel relationships; compare slow traces with baseline traces and confirm with metrics/logs before attributing cause.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links.
- **Version / assumption note:** No version-sensitive behavior required

### U10-MCQ-01 — MCQ

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for distributed trace analysis and bottleneck isolation.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **B.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **C.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **D.** Treat missing observations as zero and infer that the service is healthy.
- **Artifact/scenario:** Synthetic waterfall: root 0–900 ms; auth 20–80; profile 100–240; inventory 250–700; pricing 260–500 (parallel with inventory); serialize 710–850.
- **Model answer:** **Correct option: B.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **C:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **D:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links.
- **Version / assumption note:** No version-sensitive behavior required

### U10-MCQ-02 — MCQ

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for distributed trace analysis and bottleneck isolation.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **B.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **C.** Treat missing observations as zero and infer that the service is healthy.
  - **D.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
- **Artifact/scenario:** Trace omits one downstream span due to sampling, clocks are not verified, and an analysis sums all child durations to claim 1.3 seconds of latency.
- **Model answer:** **Correct option: A.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **B:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **C:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **D:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links.
- **Version / assumption note:** No version-sensitive behavior required

### U10-MCQ-03 — MCQ

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for distributed trace analysis and bottleneck isolation.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **B.** Treat missing observations as zero and infer that the service is healthy.
  - **C.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **D.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
- **Artifact/scenario:** Trace omits one downstream span due to sampling, clocks are not verified, and an analysis sums all child durations to claim 1.3 seconds of latency.
- **Model answer:** **Correct option: D.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **B:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **C:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links.
- **Version / assumption note:** No version-sensitive behavior required

### U10-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to distributed trace analysis and bottleneck isolation.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** Synthetic waterfall: root 0–900 ms; auth 20–80; profile 100–240; inventory 250–700; pricing 260–500 (parallel with inventory); serialize 710–850.
- **Model answer:** The artifact supports this conclusion: Calculate request wall time and critical path from a supplied waterfall; do not sum overlapping span durations as request latency. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U10-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to distributed trace analysis and bottleneck isolation.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** Trace omits one downstream span due to sampling, clocks are not verified, and an analysis sums all child durations to claim 1.3 seconds of latency.
- **Model answer:** It hides the distinction between span timing and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U10-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to distributed trace analysis and bottleneck isolation.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** Synthetic waterfall: root 0–900 ms; auth 20–80; profile 100–240; inventory 250–700; pricing 260–500 (parallel with inventory); serialize 710–850.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U10-REV-01 — Artifact review

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```json
{
  "trace_id": "synthetic-001",
  "root_ms": 900,
  "spans_ms": [60, 140, 450, 240, 140],
  "computed_request_ms": 1030,
  "sampling": "unknown"
}
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Trace analysis):**
1. Summing overlapping span durations overstates request wall time.
2. Parallel span relationships and exclusive time are not represented correctly.
3. Sampling/context limitations are unknown and trace correlation is missing.

**Corrected artifact / plan:** Use root wall time and parent-child intervals to identify the critical path, treat parallel spans as overlapping, calculate exclusive time only from interval relationships, and record sampling/context limitations before corroborating with metrics/logs. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U10-REV-02 — Artifact review

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```json
{
  "parent": "checkout",
  "spans": [
    {"name": "inventory", "start_ms": 250, "end_ms": 700},
    {"name": "pricing", "start_ms": 260, "end_ms": 500}
  ],
  "analysis": "sum all span durations as latency",
  "trace_context": null
}
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Trace analysis):**
1. Summing overlapping span durations overstates request wall time.
2. Parallel span relationships and exclusive time are not represented correctly.
3. Sampling/context limitations are unknown and trace correlation is missing.

**Corrected artifact / plan:** Use root wall time and parent-child intervals to identify the critical path, treat parallel spans as overlapping, calculate exclusive time only from interval relationships, and record sampling/context limitations before corroborating with metrics/logs. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U10-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to distributed trace analysis and bottleneck isolation.
- Fixture: Synthetic waterfall: root 0–900 ms; auth 20–80; profile 100–240; inventory 250–700; pricing 260–500 (parallel with inventory); serialize 710–850.
- Additional context: Trace omits one downstream span due to sampling, clocks are not verified, and an analysis sums all child durations to claim 1.3 seconds of latency.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Calculate request wall time and critical path from a supplied waterfall; do not sum overlapping span durations as request latency.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U10-DES-01 — Design

- **Scope / unit:** Unit 10 — Distributed trace analysis and bottleneck isolation
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for distributed trace analysis and bottleneck isolation.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for distributed trace analysis and bottleneck isolation. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** Trace omits one downstream span due to sampling, clocks are not verified, and an analysis sums all child durations to claim 1.3 seconds of latency.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: span timing, parent-child structure, critical path, exclusive time, parallelism, sampling, and trace/log links.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.


## Unit 11 — Scheduled-job freshness and deadline monitoring

**Coverage:** freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries

### U11-SA-01 — Short answer

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational scheduled-job freshness and deadline monitoring concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in scheduled-job freshness and deadline monitoring and give one example of a question it answers.
- **Artifact/scenario:** Synthetic schedule every 15 min; current time 10:40; last successful run 10:00; event watermark 09:30; expected canary for 10:15 absent.
- **Model answer:** Distinguish process success from fresh, complete, correct output using schedule, last-success, watermark, expected canary, and dependency state.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries.
- **Version / assumption note:** No version-sensitive behavior required

### U11-SA-02 — Short answer

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational scheduled-job freshness and deadline monitoring concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** Synthetic schedule every 15 min; current time 10:40; last successful run 10:00; event watermark 09:30; expected canary for 10:15 absent.
- **Model answer:** Use this evidence: Synthetic schedule every 15 min; current time 10:40; last successful run 10:00; event watermark 09:30; expected canary for 10:15 absent. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries.
- **Version / assumption note:** No version-sensitive behavior required

### U11-SA-03 — Short answer

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational scheduled-job freshness and deadline monitoring concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected scheduled-job freshness and deadline monitoring failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** Synthetic schedule every 15 min; current time 10:40; last successful run 10:00; event watermark 09:30; expected canary for 10:15 absent.
- **Model answer:** Monitor last success and output progress independently; verify a synthetic canary or watermark advances, and test stale/missing-series behavior.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries.
- **Version / assumption note:** No version-sensitive behavior required

### U11-MCQ-01 — MCQ

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for scheduled-job freshness and deadline monitoring.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **B.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **C.** Treat missing observations as zero and infer that the service is healthy.
  - **D.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
- **Artifact/scenario:** Synthetic schedule every 15 min; current time 10:40; last successful run 10:00; event watermark 09:30; expected canary for 10:15 absent.
- **Model answer:** **Correct option: A.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **B:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **C:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **D:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries.
- **Version / assumption note:** No version-sensitive behavior required

### U11-MCQ-02 — MCQ

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for scheduled-job freshness and deadline monitoring.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **B.** Treat missing observations as zero and infer that the service is healthy.
  - **C.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **D.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
- **Artifact/scenario:** Freshness alert relies on a gauge last updated by the job itself; after the exporter stops, the old gauge remains queryable.
- **Model answer:** **Correct option: D.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **B:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **C:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries.
- **Version / assumption note:** No version-sensitive behavior required

### U11-MCQ-03 — MCQ

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for scheduled-job freshness and deadline monitoring.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Treat missing observations as zero and infer that the service is healthy.
  - **B.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **C.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **D.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
- **Artifact/scenario:** Freshness alert relies on a gauge last updated by the job itself; after the exporter stops, the old gauge remains queryable.
- **Model answer:** **Correct option: C.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **B:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **D:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries.
- **Version / assumption note:** No version-sensitive behavior required

### U11-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to scheduled-job freshness and deadline monitoring.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** Synthetic schedule every 15 min; current time 10:40; last successful run 10:00; event watermark 09:30; expected canary for 10:15 absent.
- **Model answer:** The artifact supports this conclusion: Distinguish process success from fresh, complete, correct output using schedule, last-success, watermark, expected canary, and dependency state. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U11-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to scheduled-job freshness and deadline monitoring.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** Freshness alert relies on a gauge last updated by the job itself; after the exporter stops, the old gauge remains queryable.
- **Model answer:** It hides the distinction between freshness and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U11-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to scheduled-job freshness and deadline monitoring.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** Synthetic schedule every 15 min; current time 10:40; last successful run 10:00; event watermark 09:30; expected canary for 10:15 absent.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U11-REV-01 — Artifact review

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
freshness_alert:
  schedule_minutes: 15
  expr: job_last_success_timestamp_seconds > 0
  absent_series: "ignore"
  watermark_check: false
  output_count_check: false
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Freshness monitoring):**
1. A positive last-success gauge proves only a previous success, not current freshness.
2. Watermark/output/canary progress is not checked.
3. Absent exporter/series conditions are ignored.

**Corrected artifact / plan:** Alert on last-success age relative to schedule, watermark and expected canary/output count, target/exporter health, and both stale and absent series; test a successful-empty-output scenario. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U11-REV-02 — Artifact review

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
job:
  last_success: "10:00"
  current_time: "10:40"
  process_exit: 0
  watermark: "09:30"
  canary_expected: "10:15"
# success is treated as fresh output without validation
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Freshness monitoring):**
1. A positive last-success gauge proves only a previous success, not current freshness.
2. Watermark/output/canary progress is not checked.
3. Absent exporter/series conditions are ignored.

**Corrected artifact / plan:** Alert on last-success age relative to schedule, watermark and expected canary/output count, target/exporter health, and both stale and absent series; test a successful-empty-output scenario. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U11-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to scheduled-job freshness and deadline monitoring.
- Fixture: Synthetic schedule every 15 min; current time 10:40; last successful run 10:00; event watermark 09:30; expected canary for 10:15 absent.
- Additional context: Freshness alert relies on a gauge last updated by the job itself; after the exporter stops, the old gauge remains queryable.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Distinguish process success from fresh, complete, correct output using schedule, last-success, watermark, expected canary, and dependency state.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U11-DES-01 — Design

- **Scope / unit:** Unit 11 — Scheduled-job freshness and deadline monitoring
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for scheduled-job freshness and deadline monitoring.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for scheduled-job freshness and deadline monitoring. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** Freshness alert relies on a gauge last updated by the job itself; after the exporter stops, the old gauge remains queryable.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: freshness, last-success age, event-time watermark, output correctness, DAG dependencies, stale series, and canaries.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.


## Unit 12 — Observability cost, cardinality, and data retention

**Coverage:** series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs

### U12-SA-01 — Short answer

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational observability cost, cardinality, and data retention concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in observability cost, cardinality, and data retention and give one example of a question it answers.
- **Artifact/scenario:** Metric dimensions: 8 services × 4 regions × 3 environments × 6 status values × 12 pods; histogram has 10 finite buckets plus +Inf, sum, count.
- **Model answer:** Estimate telemetry growth with explicit dimensions and retention assumptions, then choose reversible reductions while preserving required incident evidence.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs.
- **Version / assumption note:** No version-sensitive behavior required

### U12-SA-02 — Short answer

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational observability cost, cardinality, and data retention concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** Metric dimensions: 8 services × 4 regions × 3 environments × 6 status values × 12 pods; histogram has 10 finite buckets plus +Inf, sum, count.
- **Model answer:** Use this evidence: Metric dimensions: 8 services × 4 regions × 3 environments × 6 status values × 12 pods; histogram has 10 finite buckets plus +Inf, sum, count. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs.
- **Version / assumption note:** No version-sensitive behavior required

### U12-SA-03 — Short answer

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational observability cost, cardinality, and data retention concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected observability cost, cardinality, and data retention failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** Metric dimensions: 8 services × 4 regions × 3 environments × 6 status values × 12 pods; histogram has 10 finite buckets plus +Inf, sum, count.
- **Model answer:** Use budgets and linting, measure actual series/bytes, remove high-cardinality labels first, and verify both deletion and incident-evidence adequacy.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs.
- **Version / assumption note:** No version-sensitive behavior required

### U12-MCQ-01 — MCQ

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for observability cost, cardinality, and data retention.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **B.** Treat missing observations as zero and infer that the service is healthy.
  - **C.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **D.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
- **Artifact/scenario:** Metric dimensions: 8 services × 4 regions × 3 environments × 6 status values × 12 pods; histogram has 10 finite buckets plus +Inf, sum, count.
- **Model answer:** **Correct option: D.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **B:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **C:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs.
- **Version / assumption note:** No version-sensitive behavior required

### U12-MCQ-02 — MCQ

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for observability cost, cardinality, and data retention.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Treat missing observations as zero and infer that the service is healthy.
  - **B.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **C.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **D.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
- **Artifact/scenario:** Metric catalog allows request_id as a label; retention policy differs between metric and log stores; deletion job reports success but no post-delete query is run.
- **Model answer:** **Correct option: C.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **B:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **D:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs.
- **Version / assumption note:** No version-sensitive behavior required

### U12-MCQ-03 — MCQ

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for observability cost, cardinality, and data retention.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **B.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **C.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **D.** Treat missing observations as zero and infer that the service is healthy.
- **Artifact/scenario:** Metric catalog allows request_id as a label; retention policy differs between metric and log stores; deletion job reports success but no post-delete query is run.
- **Model answer:** **Correct option: B.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **C:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **D:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs.
- **Version / assumption note:** No version-sensitive behavior required

### U12-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to observability cost, cardinality, and data retention.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** Metric dimensions: 8 services × 4 regions × 3 environments × 6 status values × 12 pods; histogram has 10 finite buckets plus +Inf, sum, count.
- **Model answer:** The artifact supports this conclusion: Estimate telemetry growth with explicit dimensions and retention assumptions, then choose reversible reductions while preserving required incident evidence. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U12-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to observability cost, cardinality, and data retention.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** Metric catalog allows request_id as a label; retention policy differs between metric and log stores; deletion job reports success but no post-delete query is run.
- **Model answer:** It hides the distinction between series cardinality and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U12-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to observability cost, cardinality, and data retention.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** Metric dimensions: 8 services × 4 regions × 3 environments × 6 status values × 12 pods; histogram has 10 finite buckets plus +Inf, sum, count.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U12-REV-01 — Artifact review

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
metric:
  name: api_requests_total
  labels: [service, region, request_id, user_id]
retention:
  metrics_days: 30
  logs_days: 7
incident_reconstruction_days: 14
deletion_verification: false
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Cardinality and retention):**
1. `request_id`/`user_id` labels are unbounded.
2. Retention conflicts with the stated incident-reconstruction requirement.
3. Deletion lacks an audit manifest and post-delete verification; histogram/churn budget is undefined.

**Corrected artifact / plan:** Remove unbounded dimensions, compare retention against documented evidence needs, record deletion counts/manifests and verify queries after deletion, and estimate histogram/churn series from explicit dimensions then measure actual values. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U12-REV-02 — Artifact review

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```yaml
cardinality_budget:
  request_id: allowed
  histogram_finite_buckets: 12
  pod_churn_allowance: null
retention:
  policy: "delete after 7d"
  audit_manifest: false
  post_delete_query: false
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Cardinality and retention):**
1. `request_id`/`user_id` labels are unbounded.
2. Retention conflicts with the stated incident-reconstruction requirement.
3. Deletion lacks an audit manifest and post-delete verification; histogram/churn budget is undefined.

**Corrected artifact / plan:** Remove unbounded dimensions, compare retention against documented evidence needs, record deletion counts/manifests and verify queries after deletion, and estimate histogram/churn series from explicit dimensions then measure actual values. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U12-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to observability cost, cardinality, and data retention.
- Fixture: Metric dimensions: 8 services × 4 regions × 3 environments × 6 status values × 12 pods; histogram has 10 finite buckets plus +Inf, sum, count.
- Additional context: Metric catalog allows request_id as a label; retention policy differs between metric and log stores; deletion job reports success but no post-delete query is run.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Estimate telemetry growth with explicit dimensions and retention assumptions, then choose reversible reductions while preserving required incident evidence.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U12-DES-01 — Design

- **Scope / unit:** Unit 12 — Observability cost, cardinality, and data retention
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for observability cost, cardinality, and data retention.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for observability cost, cardinality, and data retention. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** Metric catalog allows request_id as a label; retention policy differs between metric and log stores; deletion job reports success but no post-delete query is run.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: series cardinality, label churn, histogram multiplication, bytes/spans, retention, guardrails, deletion verification, and trade-offs.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.


## Unit 13 — Production load, stress, and soak testing

**Coverage:** load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety

### U13-SA-01 — Short answer

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** Short answer
- **Level:** L1
- **Objective tested:** Explain and apply a foundational production load, stress, and soak testing concept.
- **Estimated time:** 5 minutes
- **Question prompt:** Explain the central operational distinction in production load, stress, and soak testing and give one example of a question it answers.
- **Artifact/scenario:** Synthetic load test: offered 120 req/s, achieved 82 req/s, generator CPU 98%, SUT CPU 42%, mean latency 90 ms, p99 1.8 s, timeout rate 2%.
- **Model answer:** Treat performance testing as a bounded experiment with controlled workload, client and server evidence, uncertainty, abort criteria, and honest fidelity limits.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety.
- **Version / assumption note:** No version-sensitive behavior required

### U13-SA-02 — Short answer

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** Short answer
- **Level:** L2
- **Objective tested:** Explain and apply a foundational production load, stress, and soak testing concept.
- **Estimated time:** 7 minutes
- **Question prompt:** A teammate claims that one dashboard/query/configuration is sufficient to prove the system is healthy. Explain why that claim is too strong and name two independent checks.
- **Artifact/scenario:** Synthetic load test: offered 120 req/s, achieved 82 req/s, generator CPU 98%, SUT CPU 42%, mean latency 90 ms, p99 1.8 s, timeout rate 2%.
- **Model answer:** Use this evidence: Synthetic load test: offered 120 req/s, achieved 82 req/s, generator CPU 98%, SUT CPU 42%, mean latency 90 ms, p99 1.8 s, timeout rate 2%. The evidence supports a bounded conclusion only; establish freshness, coverage, and an independent corroborating signal.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety.
- **Version / assumption note:** No version-sensitive behavior required

### U13-SA-03 — Short answer

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** Short answer
- **Level:** L3
- **Objective tested:** Explain and apply a foundational production load, stress, and soak testing concept.
- **Estimated time:** 9 minutes
- **Question prompt:** Describe a safe, repeatable procedure for investigating a suspected production load, stress, and soak testing failure. Include the first action, a discriminating test, and a recovery check.
- **Artifact/scenario:** Synthetic load test: offered 120 req/s, achieved 82 req/s, generator CPU 98%, SUT CPU 42%, mean latency 90 ms, p99 1.8 s, timeout rate 2%.
- **Model answer:** Check generator headroom, offered versus achieved rate, distribution, warm-up, percentiles, and recovery; never load-test unauthorized targets.
- **Rationale / evidence:** The supplied facts bound what can be concluded; a correct answer links an operational question to evidence, limitations, and verification.
- **Common wrong answers / failure modes:**
  1. Assume one signal proves root cause without a corroborating test.
  2. Recommend collecting everything or changing production before preserving evidence.
- **Scoring rubric:** 4 points: correct concept (2), evidence/limitation (1), safe verification (1). Partial credit for a sound hypothesis clearly labelled as such.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety.
- **Version / assumption note:** No version-sensitive behavior required

### U13-MCQ-01 — MCQ

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** MCQ
- **Level:** L1
- **Objective tested:** Select the evidence-backed response for production load, stress, and soak testing.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. The service is slow but errors are flat.

  - **A.** Treat missing observations as zero and infer that the service is healthy.
  - **B.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **C.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **D.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
- **Artifact/scenario:** Synthetic load test: offered 120 req/s, achieved 82 req/s, generator CPU 98%, SUT CPU 42%, mean latency 90 ms, p99 1.8 s, timeout rate 2%.
- **Model answer:** **Correct option: C.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **B:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **D:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety.
- **Version / assumption note:** No version-sensitive behavior required

### U13-MCQ-02 — MCQ

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** MCQ
- **Level:** L2
- **Objective tested:** Select the evidence-backed response for production load, stress, and soak testing.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A query returns no rows after target discovery changes.

  - **A.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
  - **B.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **C.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **D.** Treat missing observations as zero and infer that the service is healthy.
- **Artifact/scenario:** Closed-loop client waits for each response; workload uses one tiny warm-cache payload; test lasts 90 seconds with no abort threshold.
- **Model answer:** **Correct option: B.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **A:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **C:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **D:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety.
- **Version / assumption note:** No version-sensitive behavior required

### U13-MCQ-03 — MCQ

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** MCQ
- **Level:** L3
- **Objective tested:** Select the evidence-backed response for production load, stress, and soak testing.
- **Estimated time:** 4 minutes
- **Question prompt:** Given the scenario, select the single best next interpretation or action. A proposed quick fix would hide a symptom without verifying recovery.

  - **A.** Choose the signal/query/configuration that directly answers the stated operational question and preserves necessary context.
  - **B.** Choose the broadest collection/query because more telemetry automatically guarantees a correct diagnosis.
  - **C.** Treat missing observations as zero and infer that the service is healthy.
  - **D.** Apply an immediate destructive mitigation before preserving evidence or checking the failure boundary.
- **Artifact/scenario:** Closed-loop client waits for each response; workload uses one tiny warm-cache payload; test lasts 90 seconds with no abort threshold.
- **Model answer:** **Correct option: A.** Correct: it is the smallest evidence-backed action that answers the question while retaining diagnostic context.

- **B:** Incorrect: more telemetry can increase cost/noise and still fail to answer the specific question.
- **C:** Incorrect: absent, stale, filtered, and zero-valued data are different states.
- **D:** Incorrect: mitigation should be proportionate, reversible, and preceded by safe evidence collection where possible.
- **Rationale / evidence:** Only option A is consistent with evidence-first diagnosis, explicit data-state handling, and safe operations.
- **Common wrong answers / failure modes:**
  1. B: maximizing data volume is not equivalent to diagnostic sufficiency.
  2. C or D: missing data is not zero, and destructive action before verification risks concealing the cause.
- **Scoring rubric:** 4 points: 1 for the best option and 1 each for correctly explaining why three distractors fail. No credit for a bare letter.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety.
- **Version / assumption note:** No version-sensitive behavior required

### U13-ART-01 — Artifact interpretation

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** Artifact interpretation
- **Level:** L1
- **Objective tested:** Interpret a complete synthetic artifact relevant to production load, stress, and soak testing.
- **Estimated time:** 6 minutes
- **Question prompt:** Interpret the artifact and state the strongest conclusion supported, one limitation, and the next discriminating check.
- **Artifact/scenario:** Synthetic load test: offered 120 req/s, achieved 82 req/s, generator CPU 98%, SUT CPU 42%, mean latency 90 ms, p99 1.8 s, timeout rate 2%.
- **Model answer:** The artifact supports this conclusion: Treat performance testing as a bounded experiment with controlled workload, client and server evidence, uncertainty, abort criteria, and honest fidelity limits. Limitation: it does not independently establish causality or complete telemetry coverage. Next, compare the relevant upstream and downstream evidence over aligned time windows and run a targeted verification.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U13-ART-02 — Artifact interpretation

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a complete synthetic artifact relevant to production load, stress, and soak testing.
- **Estimated time:** 8 minutes
- **Question prompt:** What is the artifact hiding or failing to distinguish? Identify at least two competing explanations and correct the interpretation.
- **Artifact/scenario:** Closed-loop client waits for each response; workload uses one tiny warm-cache payload; test lasts 90 seconds with no abort threshold.
- **Model answer:** It hides the distinction between load models and a complete causal explanation. Plausible alternatives include a collection/query gap and a real service condition. Check freshness, scope, aggregation, and an independent signal before concluding.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U13-ART-03 — Artifact interpretation

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a complete synthetic artifact relevant to production load, stress, and soak testing.
- **Estimated time:** 10 minutes
- **Question prompt:** Calculate or classify the operational consequence from the supplied fixture. Show any arithmetic and state assumptions.
- **Artifact/scenario:** Synthetic load test: offered 120 req/s, achieved 82 req/s, generator CPU 98%, SUT CPU 42%, mean latency 90 ms, p99 1.8 s, timeout rate 2%.
- **Model answer:** Use only the supplied values and units. Where the fixture gives counts or rates, compute the difference/rate over the stated interval; where it gives a trace or configuration, classify the failure boundary instead of inventing a numeric result. The result is synthetic and cannot be generalized without measurement.
- **Rationale / evidence:** The answer is constrained by the complete artifact shown in the question; explicit limitations prevent overclaiming.
- **Common wrong answers / failure modes:**
  1. Treat an empty result as proof no events occurred.
  2. Infer causality from a timestamp correlation without a discriminating test.
- **Scoring rubric:** 5 points: interpretation (2), evidence or calculation (1), limitation/alternative (1), next verification (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety.
- **Version / assumption note:** [SYNTHETIC] Fixture values; [VERIFY] installed-tool semantics if the exact query/configuration is executed.

### U13-REV-01 — Artifact review

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** Artifact review
- **Level:** L2
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 9 minutes
- **Question prompt:** Review this complete synthetic artifact:

```javascript
// [SYNTHETIC] local-test profile
const options = {
  vus: 1000,
  duration: '30m',
  target: 'https://unapproved-target.invalid',
  thresholds: {},
};
// no abort switch, allow-list, or cleanup plan
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Load test):**
1. The target is not local/allow-listed and violates the local-only safety boundary.
2. There is no rate cap, abort threshold, or cleanup plan.
3. The closed-loop tiny-payload warm-cache workload lacks representative distribution and generator-side measurements.

**Corrected artifact / plan:** Use an explicit loopback allow-list, bounded rate/duration, error/latency abort criteria and cleanup; model open/closed-loop intentionally, include payload/key distributions and warm-up phases, and capture generator CPU/network plus achieved arrivals. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U13-REV-02 — Artifact review

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** Artifact review
- **Level:** L3
- **Objective tested:** Find at least three distinct defects or operational risks in the snippet, correct them, and define validation.
- **Estimated time:** 11 minutes
- **Question prompt:** Review this complete synthetic artifact:

```javascript
// [SYNTHETIC] workload pseudocode
while (true) {
  await request('/api', { payload: 'x' });
  // next request waits for response
}
// one tiny payload, warm cache only; no generator metrics or abort condition
```
- **Artifact/scenario:** **Defects and corrections:**
1. **Unbounded or high-cardinality dimension (for example, request/user/trace identifier) is used as an indexed label or metric label.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
2. **Missing or misleading handling for absent, stale, delayed, or failed telemetry.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.
3. **No owner, validation, resource limit, privacy control, rollback, or independent recovery verification.** This can cause operational risk because it obscures state or creates uncontrolled cost. Correct it by bounding dimensions, defining explicit absent/stale behavior, and adding ownership plus a validated rollback/verification path.

**Corrected plan:** use bounded labels such as service/environment/region; retain request/trace IDs in event fields where appropriate; alert on telemetry health separately; set explicit retention/resource limits; assign an owner/runbook; validate with synthetic fixtures and a negative test. Exact schema/field names are [VERIFY] against the installed tool version.
- **Model answer:** **Defects and corrections (Load test):**
1. The target is not local/allow-listed and violates the local-only safety boundary.
2. There is no rate cap, abort threshold, or cleanup plan.
3. The closed-loop tiny-payload warm-cache workload lacks representative distribution and generator-side measurements.

**Corrected artifact / plan:** Use an explicit loopback allow-list, bounded rate/duration, error/latency abort criteria and cleanup; model open/closed-loop intentionally, include payload/key distributions and warm-up phases, and capture generator CPU/network plus achieved arrivals. Validate with a positive case, a negative/absent-data case, and an installed-version configuration/query check; record the result. Version-sensitive fields remain [VERIFY].
- **Rationale / evidence:** ['Only change formatting and ignore semantic risks.', 'Replace the whole system without a bounded migration or a test proving the defect is fixed.']
- **Common wrong answers / failure modes:**
  1. 8
  2.  
- **Scoring rubric:** load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC]; exact configuration schema is [VERIFY]..
- **Version / assumption note:** No version-sensitive behavior required

### U13-INC-01 — Incident/diagnosis

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** Incident/diagnosis
- **Level:** L3
- **Objective tested:** Diagnose a synthetic incident across symptom, first action, alternatives, mitigation, verification, and prevention.
- **Estimated time:** 15 minutes
- **Question prompt:** Use this complete incident packet:

[SYNTHETIC] Incident packet:
- Impact: operators report a degraded or missing signal related to production load, stress, and soak testing.
- Fixture: Synthetic load test: offered 120 req/s, achieved 82 req/s, generator CPU 98%, SUT CPU 42%, mean latency 90 ms, p99 1.8 s, timeout rate 2%.
- Additional context: Closed-loop client waits for each response; workload uses one tiny warm-cache payload; test lasts 90 seconds with no abort threshold.
- Scope: local lab only; no external endpoint or production credential is involved.
- **Artifact/scenario:** 1. **Symptom and impact:** State the observed impact without assuming its cause: Treat performance testing as a bounded experiment with controlled workload, client and server evidence, uncertainty, abort criteria, and honest fidelity limits.
2. **First safe query/action:** Preserve the time window and run the narrowest read-only check that compares source, processing, and destination evidence. Explain what each result would discriminate.
3. **Differential diagnosis:** (a) source/instrumentation gap; (b) processing/filtering/drop or query-scope error; (c) destination, storage, or delivery failure. Also consider delay/sampling where applicable.
4. **Diagnosis:** The supplied fixture supports only the stage explicitly evidenced by its counts/timestamps. Separate those facts from hypotheses; request aligned counters/logs before naming a root cause.
5. **Mitigation:** Choose a reversible, least-blast-radius action (restore a bounded pipeline/configuration or reduce load safely); preserve samples and prior config.
6. **Verification:** Confirm source-to-destination counts converge over a known window, freshness advances, the user-visible symptom recovers, and no new drops/cardinality/privacy regressions appear.
7. **Prevention:** Add a synthetic canary, alert on pipeline health, config validation, a runbook, ownership, and a fault-injection test.
8. **Common failure modes:** Do not restart/delete data first, call correlation proof, or declare recovery from a green heartbeat alone.
- **Model answer:** A disciplined diagnosis separates observed evidence from hypotheses and verifies recovery across the user-facing system and telemetry path.
- **Rationale / evidence:** ['Prematurely assert one root cause from a single chart.', 'Restart all components or delete retained data before preserving evidence.']
- **Common wrong answers / failure modes:**
  1. 1
  2. 2
- **Scoring rubric:** load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: [SYNTHETIC].
- **Version / assumption note:** No version-sensitive behavior required

### U13-DES-01 — Design

- **Scope / unit:** Unit 13 — Production load, stress, and soak testing
- **Question type:** Design
- **Level:** L4
- **Objective tested:** Design an evidence-backed, resource-aware solution for production load, stress, and soak testing.
- **Estimated time:** 20 minutes
- **Question prompt:** Design a laptop-scale, zero-budget operating approach for production load, stress, and soak testing. State requirements and assumptions; compare at least two viable options; explain signal coverage, resource/privacy risks, failure modes, ownership, and rollback. Define a measurable acceptance test and what evidence would change the decision.
- **Artifact/scenario:** Closed-loop client waits for each response; workload uses one tiny warm-cache payload; test lasts 90 seconds with no abort threshold.
- **Model answer:** **Requirements/assumptions:** local-only, synthetic data, bounded resource use, no paid backend, and no secrets/PII. **Option A:** the smallest single-node/local profile with essential signals and short retention; simpler to operate but has limited failure isolation and durability. **Option B:** add a separate component or richer signal only when a stated diagnostic gap justifies its cost; it improves capability but increases resource use and failure modes. **Decision:** begin with A, measure actual resource and evidence coverage, then add only the component that closes a demonstrated gap. **Failure modes:** telemetry outage, cardinality growth, stale data, storage exhaustion, and privacy leakage. **Acceptance:** run a synthetic fault; collect evidence from source through query; verify a bounded resource budget, redaction, alert delivery where in scope, and a documented rollback. **Change the decision if:** incident evidence shows a persistent blind spot or measured local capacity allows a justified extension.
- **Rationale / evidence:** A defensible design compares viable alternatives against requirements, defines a measurable test, and makes the decision reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without stating assumptions.
  2. Use vendor prices or assume unlimited laptop resources.
- **Scoring rubric:** 12 points: requirements/assumptions (2), two options/trade-offs (3), failure/safety/ownership (2), measurable acceptance test (3), rollback and decision-changing evidence (2).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: load models, percentiles, coordinated omission, generator health, capacity knee, soak slopes, statistical comparisons, and safety.
- **Version / assumption note:** [ASSUMPTION] zero-budget laptop lab; no vendor pricing assumed.


## Cross-unit integration scenarios

### Design-review whiteboard prompts

The first 16 scenarios are the required design-review whiteboard prompts. They are full questions with model answers and scoring rubrics, and are counted within the cross-unit total.

### XINT-001 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U01/U02/U04/U05/U12
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U01/U02/U04/U05/U12 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Telemetry architecture and retention for a laptop-scale platform. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** Core metrics plus bounded logs/traces on a local-only host; 8 GB RAM and 30 GB disk are ceilings, not targets.
- **Model answer:** Start with Core, short measured retention, bounded labels, redaction, and a synthetic end-to-end fault test. Compare single-node minimal stack against richer multi-component stack; choose the former until evidence demonstrates a blind spot.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U01/U02/U04/U05/U12.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-002 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U01/U02/U03/U06
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U01/U02/U03/U06 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Single versus federated Prometheus. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** Two small lab environments need a shared overview, but no high availability or multi-cluster requirement is stated.
- **Model answer:** A single local Prometheus is simpler and avoids federation failure/duplication; federation may help selective aggregation across independent sources but adds query, label, and freshness complexity. Measure query needs and ownership before adopting it.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U01/U02/U03/U06.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-003 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U02/U09/U12
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U02/U09/U12 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Label/cardinality policy with churn and histograms. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** Metric dimensions: 6 services × 3 environments × 4 regions × 5 statuses × 10 pods; histogram has 8 finite buckets plus +Inf, sum, count.
- **Model answer:** Bound each label, keep request/user IDs out of labels, estimate active series and churn, include bucket/sum/count series only when exported, and validate actual TSDB series. Compare dropping a dimension against retaining a bounded one; preserve diagnostic needs.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U09/U12.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-004 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U01/U04/U05/U07
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U01/U04/U05/U07 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Centralized logs with redaction and incident evidence. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** Logs need service, severity, trace correlation, and error class; tokens and user identifiers must not be persisted.
- **Model answer:** Redact at the earliest trusted processing boundary, use bounded indexed labels, keep correlation IDs only where policy permits, and canary-test both redaction and useful error reconstruction. Compare local per-service files with centralized pipeline.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U01/U04/U05/U07.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-005 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U05/U07/U10/U13
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U05/U07/U10/U13 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Trace sampling and missing-evidence risks. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** High-volume normal traffic and rare failures need diagnosis; storage is constrained.
- **Model answer:** Compare head sampling with a policy that preferentially preserves errors/slow traces where supported; state implementation/version limits and sampling bias. Acceptance: planted errors are retained at a measured rate and sampled-out spans are never treated as proof of absence.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U05/U07/U10/U13.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-006 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U06/U08/U01
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U06/U08/U01 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Alertmanager routing, delivery reliability, and HA assumptions. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** Page-worthy alert has `team=payments`; route matcher expects `team=payment`; local receiver logs accepted payload but not external delivery.
- **Model answer:** Fix label contract and test routing fixtures; distinguish Alertmanager acceptance from end-user delivery. Compare one local instance with HA only if supported/required. Use a narrow silence with owner, reason, expiry, and audit trail.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U06/U08/U01.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-007 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U07/U03/U05/U02
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U07/U03/U05/U02 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Dependency correlation and graph drift. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** Declared graph says checkout→payment; traces show checkout→risk→payment; deployment at 10:02 precedes latency increase.
- **Model answer:** Combine declared and observed graphs; add missing risk dependency after verification; compare trace timing and deployment timeline; do not assert deployment causality until rollback/canary or controlled comparison supports it.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U07/U03/U05/U02.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-008 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U08/U06/U02/U01
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U08/U06/U02/U01 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Symptom-based alert catalog and quality gates. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** API errors rise but target-discovery failure also removes one instance; alert has no owner/runbook.
- **Model answer:** Define user symptom separately from telemetry health; include owner/runbook, positive/negative/absent-series tests, and a watchdog with an independent evidence path. Compare page versus ticket based on user impact and response urgency.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U08/U06/U02/U01.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-009 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U09/U07/U02
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U09/U07/U02 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Saturation monitoring and capacity forecasting. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** Queue depth 100→220→340 over 10 minutes; arrivals 80/min and drains 56/min; one container throttled while host average CPU is 35%.
- **Model answer:** Queue growth is 24/min; linear time to 1,000 from 340 is (1000−340)/24≈27.5 min under the stated constant-rate assumption. Add per-workload throttling, pool wait, and dependency latency; use admission control/backpressure before adding retries.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U09/U07/U02.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-010 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U10/U13/U09/U07
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U10/U13/U09/U07 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Trace-driven bottleneck diagnosis and performance program. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** Request wall time 900 ms; inventory 250–700 ms; pricing 260–500 ms in parallel; dependency pool wait rises under load.
- **Model answer:** Critical path includes inventory and not the full sum of overlapping spans. Test under controlled local load and correlate queue/pool wait. Compare single trace with distributions; acceptance requires repeated samples and generator headroom.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U10/U13/U09/U07.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-011 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U11/U07/U02/U08
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U11/U07/U02/U08 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Freshness/deadline monitoring for a multi-stage DAG. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** Job runs every 15 minutes; last process success 10:00; current time 10:40; watermark 09:30; canary for 10:15 absent.
- **Model answer:** Process success is not output freshness. Alert on last-success age plus watermark/canary advancement and upstream dependency state; a stale gauge can mask a dead exporter, so test stale and missing series explicitly.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U11/U07/U02/U08.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-012 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U12/U01/U02/U04/U05
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U12/U01/U02/U04/U05 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Observability governance without price estimates. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** A report shows high-cardinality request IDs, 14-day logs, sampled traces, and retention deletion without post-delete verification.
- **Model answer:** Remove request IDs from indexed labels first; compare series/bytes/spans and retention requirements; retain evidence required for incident reconstruction. Use reversible staged changes and measure post-change coverage; do not assign vendor prices.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U12/U01/U02/U04/U05.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-013 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U13/U02/U03/U09/U10
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U13/U02/U03/U09/U10 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Load/soak program and safe CI gates. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** Baseline/candidate p99 differs by 12%, but A/A runs vary by 15%; generator CPU reaches 98%, service CPU 42%.
- **Model answer:** Verdict is inconclusive: generator saturation and A/A noise overwhelm the apparent effect. Improve generator headroom, interleave runs, preserve raw samples, use confidence intervals and a planted regression test; local allow-list and abort criteria are mandatory.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U13/U02/U03/U09/U10.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-014 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U01/U04/U05/U06/U08
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U01/U04/U05/U06/U08 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Observability-stack failure recovery and meta-monitoring. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** App remains healthy, but Collector queue is full, Loki ingest stops, Alertmanager notification fails, and local watchdog stays green.
- **Model answer:** Use independent checks for each pipeline boundary and externalized/second-path evidence where feasible. A local green heartbeat cannot prove end-to-end delivery. Restore one boundary at a time, preserve queued data, and verify canary arrival plus notification receipt.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U01/U04/U05/U06/U08.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-015 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U03/U02/U06/U07
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U03/U02/U06/U07 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Dashboard-as-code ownership, validation, and drift. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** Dashboard query uses milliseconds but panel unit is seconds; one failing instance is excluded; manual UI edits differ from repository.
- **Model answer:** Correct units and selector, add explicit missing-series handling, validate definitions against installed schema, assign owner, review in version control, and detect drift. Compare UI-only changes with reviewed-as-code provisioning.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U03/U02/U06/U07.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-016 — Integration scenario / design-review whiteboard

- **Scope / unit:** Cross-unit: U01/U03/U04/U05/U12
- **Question type:** Integration scenario / design-review whiteboard
- **Level:** L4
- **Objective tested:** Integrate evidence from U01/U03/U04/U05/U12 to make a defensible operational decision.
- **Estimated time:** 22 minutes
- **Question prompt:** **Design-review prompt:** Build versus buy versus adopt for a small team. State requirements and assumptions; compare at least two viable options; explain trade-offs and failure modes; define measurable acceptance criteria, rollback/recovery, and evidence that would change the decision.
- **Artifact/scenario:** Zero budget, laptop-scale learning environment, need metrics, selected logs, and traces for synthetic incidents.
- **Model answer:** Compare minimal open-source local stack, a single tool with reduced signal coverage, and managed SaaS as a future option. Given zero budget and local-only constraints, start with local open-source; document limitations and revisit only if measured needs/operating burden change.

**Scoring notes:** Full credit requires alternatives, measurable acceptance, rollback/recovery, and decision-changing evidence.
- **Rationale / evidence:** System-level design must make constraints and trade-offs explicit and remain falsifiable and reversible.
- **Common wrong answers / failure modes:**
  1. Declare one architecture universally best without constraints or alternatives.
  2. Omit a measurable acceptance test, rollback, or ownership.
- **Scoring rubric:** 14 points: requirements/assumptions (2); two viable options and trade-offs (3); evidence and technical correctness (3); safety/privacy/ownership (2); measurable acceptance test (2); rollback and decision-changing evidence (2). Partial credit requires explicit uncertainty and safe operation.
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U01/U03/U04/U05/U12.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### Additional integration scenarios

The following scenarios focus on artifact interpretation, calculations, diagnosis, and verification across multiple M11 units.

### XINT-017 — Integration scenario

- **Scope / unit:** Cross-unit: U02/U03
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U02/U03 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** PromQL: rate applied to a gauge. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] `queue_depth` samples at 0s=4, 15s=9, 30s=12. Query: `rate(queue_depth[1m])`.
- **Model answer:** `queue_depth` is a gauge; rate is intended for counter-like monotonic increase semantics. Use a gauge-oriented query such as `queue_depth` or a measured derivative only if change rate is the question. The supplied samples imply +8 items/30 s, but do not by themselves justify counter semantics.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U03.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-018 — Integration scenario

- **Scope / unit:** Cross-unit: U02/U03/U09
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U02/U03/U09 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** PromQL: averaging precomputed percentiles. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] Instance A p99=100 ms for 1,000 requests; instance B p99=900 ms for 10 requests. Dashboard computes `(A_p99+B_p99)/2`.
- **Model answer:** The arithmetic mean of per-instance p99 values is not the fleet p99. Aggregate histogram buckets and compute a fleet quantile where histogram data is available; otherwise label the panel as an approximation and show per-instance distributions.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U03/U09.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-019 — Integration scenario

- **Scope / unit:** Cross-unit: U02/U07
- **Question type:** Integration scenario
- **Level:** L4
- **Objective tested:** Integrate evidence from U02/U07 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** PromQL: many-to-many vector matching. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] Left vector has two series per `service`; right vector has three series per `service`, and query joins only on `service`.
- **Model answer:** The join can be ambiguous/many-to-many. Reduce one side to unique keys or define a valid one-to-many relationship with explicit matching modifiers and grouping labels after checking the data model. Do not silence the error by dropping meaningful dimensions.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U07.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-020 — Integration scenario

- **Scope / unit:** Cross-unit: U02/U08
- **Question type:** Integration scenario
- **Level:** L2
- **Objective tested:** Integrate evidence from U02/U08 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** PromQL: range too short for scrape/evaluation pattern. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] Scrape interval 30 s, rule evaluation 30 s, query `rate(api_requests_total[15s])`.
- **Model answer:** The range is shorter than a reliable multi-sample window for this scrape pattern; rate may be empty or unstable. Use a window containing multiple samples and test at the actual evaluation timestamps; exact recommendations depend on rule design and are [VERIFY].

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U08.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-021 — Integration scenario

- **Scope / unit:** Cross-unit: U02/U12
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U02/U12 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** PromQL: histogram quantile drops `le`. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] Query: `histogram_quantile(0.99, sum by (service) (rate(http_request_duration_seconds_bucket[5m])))`.
- **Model answer:** The aggregation removed `le`, which identifies bucket boundaries. Preserve it: aggregate by `(service, le)` before `histogram_quantile`. Confirm metric is a classic histogram bucket series and check installed Prometheus semantics [VERIFY].

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U12.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-022 — Integration scenario

- **Scope / unit:** Cross-unit: U02/U06/U08
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U02/U06/U08 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Will this alert fire? Complete fixture. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] Rule: `- alert: QueueHigh; expr: queue_depth > 10; for: 2m`. Evaluations every 30s: t=0 depth 12, t=30 12, t=60 8, t=90 12, t=120 12, t=150 12. Assume continuous rule evaluations and standard `for` pending semantics [VERIFY].
- **Model answer:** It does not become firing by t=150 if the pending condition was interrupted at t=60; the later uninterrupted interval starts at t=90 and reaches 2 minutes at t=210. State the evaluation model and validate with rule tests against the installed version.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U06/U08.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-023 — Integration scenario

- **Scope / unit:** Cross-unit: U02/U12
- **Question type:** Integration scenario
- **Level:** L4
- **Objective tested:** Integrate evidence from U02/U12 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** How many series will this create? Histogram dimensions. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] 4 services × 3 regions × 2 environments × 5 status values. Each label combination emits 8 finite buckets + +Inf, plus `_sum` and `_count` (assume all are exposed).
- **Model answer:** Label combinations=4×3×2×5=120. Per combination: 8+1+1+1=11 series. Upper-bound estimate=120×11=1,320 active series, before churn/overlap. This is a theoretical upper bound under the stated assumptions, not observed TSDB series.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U12.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-024 — Integration scenario

- **Scope / unit:** Cross-unit: U02/U09/U12
- **Question type:** Integration scenario
- **Level:** L2
- **Objective tested:** Integrate evidence from U02/U09/U12 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Series count with pod churn and rollout overlap. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] 6 services × 2 regions × 3 status values × 8 pods normally; rollout temporarily has 3 extra pods per service in one region. One scalar metric per label set.
- **Model answer:** Normal series=6×2×3×8=288. If 3 extra pods exist for all 6 services in one region, added=6×3×3=54, peak=342. Do not multiply by scrape count; time samples are not distinct series.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U09/U12.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-025 — Integration scenario

- **Scope / unit:** Cross-unit: U01/U04/U05/U07
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U01/U04/U05/U07 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Which signal answers this question?. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** Need answer: ‘Did checkout p99 rise?’, ‘Which request path was slow?’, ‘What exception was thrown?’, ‘Which deployment happened at 10:02?’
- **Model answer:** Metrics answer trend/aggregate latency; traces reveal per-request spans and critical path; logs carry event/error detail; change events establish timeline. No single signal proves causality. Choose by question and corroborate.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U01/U04/U05/U07.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-026 — Integration scenario

- **Scope / unit:** Cross-unit: U02/U03/U09
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U02/U03/U09 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** What is this dashboard hiding?. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] Panel query excludes `instance="api-3"`; shown mean latency=80 ms; p99 panel is absent; time range is last 5 minutes; unit configured seconds while query returns milliseconds.
- **Model answer:** It hides the failing instance, tail latency, and unit mismatch. Remove exclusion, show p50/p95/p99 or histograms, distinguish no data from zero, label units correctly, and add per-instance detail plus query freshness.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U03/U09.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-027 — Integration scenario

- **Scope / unit:** Cross-unit: U01/U04/U05
- **Question type:** Integration scenario
- **Level:** L4
- **Objective tested:** Integrate evidence from U01/U04/U05 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Is this pipeline losing data, and where?. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] source sent=10,000; Collector accepted=10,000; processor filtered=500 by policy; exporter attempted=9,500, failed=200; backend received=9,300 over aligned interval.
- **Model answer:** Evidence shows 500 intentionally filtered and 200 failed sends; backend received 9,300, which reconciles 10,000−500−200. Determine whether failed sends were retried/delayed or permanently dropped before calling all 200 data loss. Inspect queue/retry/drop counters and a canary.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U01/U04/U05.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-028 — Integration scenario

- **Scope / unit:** Cross-unit: U11/U02/U08
- **Question type:** Integration scenario
- **Level:** L2
- **Objective tested:** Integrate evidence from U11/U02/U08 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Freshness alert and stale time series. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] Schedule every 15 min; last success 10:00; now 10:40; gauge `job_last_success_timestamp_seconds` remains present from 10:00; exporter target is down.
- **Model answer:** An age calculation against current time may detect stale success only if it is evaluated and the timestamp is correct; a rule based solely on series presence can miss the failure. Add target health, last-success age, watermark/canary progress, and absent-series tests.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U11/U02/U08.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-029 — Integration scenario

- **Scope / unit:** Cross-unit: U11/U07/U08
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U11/U07/U08 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Job succeeds but output is empty. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] job exit code 0 at 10:30; expected rows 1,000–1,200; actual rows=0; watermark remains 10:00; upstream dependency reported degraded.
- **Model answer:** Process success is not data correctness/freshness. Alert on output count/quality and watermark advancement; inspect upstream dependency and input partition. Preserve the output and rerun only after idempotency/backfill safety is understood.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U11/U07/U08.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-030 — Integration scenario

- **Scope / unit:** Cross-unit: U13/U09/U10
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U13/U09/U10 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** What's wrong with this load test? Closed-loop omission. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] closed-loop client sends next request only after response; during 3 s stalls it sends fewer requests; reports mean 110 ms and p99 300 ms while server queue grows.
- **Model answer:** Closed-loop load self-throttles when the service slows and may underrepresent latency from the intended offered-arrival workload (coordinated omission risk). Record intended/actual arrivals, use an appropriate open-loop model when arrival rate is the question, and compare generator-side timings.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U13/U09/U10.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-031 — Integration scenario

- **Scope / unit:** Cross-unit: U13/U02/U09
- **Question type:** Integration scenario
- **Level:** L4
- **Objective tested:** Integrate evidence from U13/U02/U09 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** What's wrong with this load test? Generator saturation. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] offered 120 req/s; achieved 82 req/s; generator CPU 98%; service CPU 42%; p99 1.8 s; timeout 2%.
- **Model answer:** Cannot attribute the result to SUT capacity because the generator is saturated. Reduce client overhead, distribute/generate locally with headroom, or lower the offered rate while documenting the question. Monitor client CPU, network, and achieved rate.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U13/U02/U09.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-032 — Integration scenario

- **Scope / unit:** Cross-unit: U13/U03/U10
- **Question type:** Integration scenario
- **Level:** L2
- **Objective tested:** Integrate evidence from U13/U03/U10 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Cold-cache and tiny-data mismatch. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] 90-second test uses one 1 KB payload and warm cache; production-like workload has skewed keys and 4 MB payloads; average latency is reported only.
- **Model answer:** The workload lacks payload and key-distribution realism and the duration may not reach steady state. Define request mix, payload distribution, cache warm-up, warm/cold phases, percentiles, errors, and SUT telemetry. State that the result only describes this fixture.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U13/U03/U10.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-033 — Integration scenario

- **Scope / unit:** Cross-unit: U13/U09
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U13/U09 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Is this a leak or cache warming?. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] RSS MB at minutes 0,10,20,30,40: 400, 430, 452, 468, 480. Cache hit ratio: 20%, 40%, 60%, 75%, 82%. Workload is steady; no post-test baseline sample.
- **Model answer:** Endpoint slope=(480−400)/40=2 MB/min, but growth is decelerating while cache hit ratio rises, so warming is plausible; not enough evidence to rule out a leak. Fit a robust slope with uncertainty, repeat after cache stabilizes, compare idle/cleanup baseline, inspect heap/object metrics, and project OOM only with explicit assumptions.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U13/U09.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-034 — Integration scenario

- **Scope / unit:** Cross-unit: U13/U09/U07
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U13/U09/U07 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Backfill versus online traffic. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] online p99 rises 120→420 ms after backfill begins; queue depth rises 20→500; dependency pool wait rises; online request rate is unchanged.
- **Model answer:** Evidence suggests shared resource contention but does not prove the precise bottleneck. Limit/backpressure backfill, isolate worker/pool/priority where safe, verify online latency and queue drain, and compare an interleaved baseline with backfill disabled.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U13/U09/U07.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-035 — Integration scenario

- **Scope / unit:** Cross-unit: U05/U01/U08
- **Question type:** Integration scenario
- **Level:** L4
- **Objective tested:** Integrate evidence from U05/U01/U08 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Collector queue full while service looks healthy. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] application request metrics normal; Collector queue reaches 100%; send failures rise; backend trace count drops; local Collector process is alive.
- **Model answer:** The observability pipeline is degraded despite app health. Check exporter/backend reachability, retry/queue/drop metrics and canary spans; apply bounded recovery and preserve evidence. A process heartbeat does not prove successful telemetry delivery.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U05/U01/U08.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-036 — Integration scenario

- **Scope / unit:** Cross-unit: U06/U08/U01
- **Question type:** Integration scenario
- **Level:** L2
- **Objective tested:** Integrate evidence from U06/U08/U01 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Alert delivery failure and watchdog. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] alert rule is firing; Alertmanager accepted alert; receiver log says connection refused; local watchdog remains green.
- **Model answer:** The failure is downstream of rule evaluation and likely in receiver/delivery path; test routing and destination connectivity. A green local watchdog only covers its own path. Verify delivery through an independent receiver/test event and alert on delivery failures.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U06/U08/U01.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-037 — Integration scenario

- **Scope / unit:** Cross-unit: U07/U03/U02
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U07/U03/U02 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Deployment timeline versus root cause. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] latency starts at 10:04; deploy at 10:02; payment pool wait begins 10:03; CPU stable; rollback not yet tested.
- **Model answer:** Deployment is a plausible hypothesis, not proven cause. Compare traces and pool metrics before/after, inspect dependency changes, and use a controlled rollback/canary if safe. Record alternative causes and verify outcome.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U07/U03/U02.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-038 — Integration scenario

- **Scope / unit:** Cross-unit: U01/U04/U12
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U01/U04/U12 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Retention deletion and incident reconstruction. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] retention job reports deleting logs older than 7 days; incident occurred 8 days ago; audit requires reconstruction; no post-delete query or deletion manifest exists.
- **Model answer:** The policy may have removed required evidence and deletion success is unverified. Define incident/legal retention needs, preserve scoped evidence, record deletion manifests and counts, run post-delete verification, and document what cannot be reconstructed.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U01/U04/U12.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-039 — Integration scenario

- **Scope / unit:** Cross-unit: U04/U05/U07/U12
- **Question type:** Integration scenario
- **Level:** L4
- **Objective tested:** Integrate evidence from U04/U05/U07/U12 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Privacy versus correlation. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] logs contain `authorization`, email, and trace_id; a proposed redactor removes the whole message, destroying error class and correlation context.
- **Model answer:** Redact secrets/PII at a trusted boundary while retaining allow-listed error class, service, timestamp, and policy-approved trace context. Test positive redaction and reconstruction utility; verify whether trace IDs themselves are permitted identifiers.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U04/U05/U07/U12.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-040 — Integration scenario

- **Scope / unit:** Cross-unit: U10/U13/U09
- **Question type:** Integration scenario
- **Level:** L2
- **Objective tested:** Integrate evidence from U10/U13/U09 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Trace critical path with parallel spans. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] root 0–900 ms; auth 20–80; inventory 250–700; pricing 260–500; serialize 710–850; inventory and pricing run in parallel.
- **Model answer:** Request wall time is 900 ms. The longest downstream parallel branch is inventory (450 ms), not inventory+pricing (690 ms). Investigate inventory and pool wait; confirm with repeated slow traces and load metrics.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U10/U13/U09.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-041 — Integration scenario

- **Scope / unit:** Cross-unit: U09/U10/U07
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U09/U10/U07 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Saturation plus tail latency. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] p50=90 ms, p99=1.2 s; queue grows 25/min; connection pool wait rises; CPU average=40%.
- **Model answer:** Tail latency plus queue/pool wait indicates saturation or dependency contention masked by host average. Inspect per-container throttling, pool capacity, dependency spans, and queue arrival/drain rates. Mitigate with bounded admission control and verify p99 plus queue drain.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U09/U10/U07.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-042 — Integration scenario

- **Scope / unit:** Cross-unit: U02/U12/U01
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U02/U12/U01 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Histogram cardinality versus retention. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] 1,000 services? No: 10 services × 4 regions × 3 environments × 6 status values; histogram has 12 finite buckets +Inf, sum, count; pod overlap doubles active pod identities temporarily.
- **Model answer:** Base combinations=10×4×3×6=720. Series per combination=12+1+1+1=15, yielding 10,800 series before pod dimension; if the stated dimensions omit pods, multiply by observed pod identities, not an assumed universal number. Retention changes samples/disk, not label-set cardinality itself.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U12/U01.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-043 — Integration scenario

- **Scope / unit:** Cross-unit: U13/U02/U03
- **Question type:** Integration scenario
- **Level:** L4
- **Objective tested:** Integrate evidence from U13/U02/U03 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** A/A noise and false-positive performance gate. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] five A/A comparisons show p99 deltas +8%, −11%, +13%, +2%, −9%; a proposed gate fails any run with >5% change.
- **Model answer:** The gate has a high false-positive risk under observed noise. Use repeated/interleaved runs, bootstrap confidence intervals/effect size, define a practical threshold, test planted regression and no-change fixtures, and classify ambiguous evidence as inconclusive.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U13/U02/U03.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-044 — Integration scenario

- **Scope / unit:** Cross-unit: U13/U09/U12
- **Question type:** Integration scenario
- **Level:** L2
- **Objective tested:** Integrate evidence from U13/U09/U12 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Soak growth and projected OOM uncertainty. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] RSS grows 40 MB over 30 minutes; available memory headroom is 1,200 MB; observed slope is based on only three samples and cache is still warming.
- **Model answer:** Naive slope=40/30≈1.33 MB/min, naive time-to-headroom≈900 min (15 h), but this projection is unreliable because samples are sparse and cache state changes. Collect longer stabilized samples, estimate slope uncertainty, monitor heap/cache separately, and treat extrapolation as conditional.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U13/U09/U12.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-045 — Integration scenario

- **Scope / unit:** Cross-unit: U02/U08/U11
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U02/U08/U11 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Missing series versus zero traffic. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] request counter series disappears after target discovery failure; query displays no result, while a separate target-health metric reports scrape failure.
- **Model answer:** No result is not zero traffic. Display explicit no-data state, alert on target health/expected series absence, and test discovery failures. Avoid filling missing values with zero unless the metric contract justifies it.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U08/U11.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-046 — Integration scenario

- **Scope / unit:** Cross-unit: U04/U01/U05
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U04/U01/U05 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Log ingestion gap versus quiet service. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] source canary emits one log/min; collector read count stops at 12:10; backend query has no rows after 12:10; application metrics continue.
- **Model answer:** The source canary and collector counters localize the likely gap near collection/processing rather than quiet application traffic. Check agent health, file offsets/permissions, dropped counters, and timestamp parsing; do not infer no events from query emptiness.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U04/U01/U05.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-047 — Integration scenario

- **Scope / unit:** Cross-unit: U09/U13
- **Question type:** Integration scenario
- **Level:** L4
- **Objective tested:** Integrate evidence from U09/U13 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Queue drain-rate calculation. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] queue=340; arrivals=80 jobs/min; completed=56 jobs/min; target queue=1,000. Assume constant rates for arithmetic only.
- **Model answer:** Net growth=80−56=24 jobs/min. Time to 1,000=(1,000−340)/24≈27.5 minutes. This is a linear illustrative estimate; burstiness, retries, and capacity changes invalidate it.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U09/U13.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-048 — Integration scenario

- **Scope / unit:** Cross-unit: U01/U05/U06/U08
- **Question type:** Integration scenario
- **Level:** L2
- **Objective tested:** Integrate evidence from U01/U05/U06/U08 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Can a local green heartbeat prove end-to-end health?. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] Prometheus up=1; Collector process alive; traces absent in backend; Alertmanager receiver refuses connections.
- **Model answer:** No. `up=1`/process alive establish only local reachability/process state. Verify a synthetic trace reaches the backend and a test alert reaches a controlled receiver through an independent path.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U01/U05/U06/U08.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-049 — Integration scenario

- **Scope / unit:** Cross-unit: U13/U09/U01
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U13/U09/U01 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Safe abort and cleanup for local load test. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] local allow-list contains `http://127.0.0.1:8080`; max duration 60 s; request rate capped; abort threshold is error rate >5%; cleanup command removes only the test namespace.
- **Model answer:** Before running, confirm exact loopback target, rate/duration caps, resource headroom, abort switch, and cleanup scope. Stop immediately on abort threshold, preserve results, wait for queues to drain, and confirm service returns to baseline. Never repoint to a public/third-party endpoint.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U13/U09/U01.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-050 — Integration scenario

- **Scope / unit:** Cross-unit: U01/U02/U04/U05/U07
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U01/U02/U04/U05/U07 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Four-signal evidence packet and uncertainty. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] metric p99 rises at 10:04; trace has 700 ms payment span; log records pool timeout; deploy at 10:02; no rollback/canary comparison yet.
- **Model answer:** The combined evidence strongly supports payment-pool contention as the proximate bottleneck, while deployment causality remains a hypothesis. Verify pool wait/usage and compare a controlled rollback or pool change; do not confuse proximate bottleneck with trigger.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U01/U02/U04/U05/U07.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-051 — Integration scenario

- **Scope / unit:** Cross-unit: U01/U02/U04/U05/U12
- **Question type:** Integration scenario
- **Level:** L4
- **Objective tested:** Integrate evidence from U01/U02/U04/U05/U12 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Cost cut trade-off decision. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] report: request_id label drives 70% of series; logs retain 14 days; traces sampled 10%; incident requirement is to reconstruct a request for 48 hours.
- **Model answer:** First remove request_id from metric labels while retaining policy-approved correlation in logs/traces. Compare retention reductions only after validating incident reconstruction. Roll out in stages, record before/after series and evidence coverage, and define rollback if traceability drops below acceptance.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U01/U02/U04/U05/U12.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-052 — Integration scenario

- **Scope / unit:** Cross-unit: U03/U02/U09/U10
- **Question type:** Integration scenario
- **Level:** L2
- **Objective tested:** Integrate evidence from U03/U02/U09/U10 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Dashboard average hides failing instance. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] three instances p99 100, 120, 1,100 ms; dashboard reports average of p99s=440 ms and host CPU=30%.
- **Model answer:** The mean of per-instance percentiles is not fleet p99 and the average hides one failing instance. Show per-instance tails, aggregate histograms correctly if available, and correlate slow traces with queue/pool saturation.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U03/U02/U09/U10.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-053 — Integration scenario

- **Scope / unit:** Cross-unit: U13/U03/U02
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U13/U03/U02 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** CI smoke test versus production capacity. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] local test on 4 CPU/8 GB laptop passes 20 req/s for 2 minutes; target production has different hardware, network, cache, and data volume.
- **Model answer:** The test proves only that the local fixture passed its defined gate. It does not establish production capacity. Use it as a regression smoke test, preserve fidelity limitations, and require environment-representative validation before capacity claims.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U13/U03/U02.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-054 — Integration scenario

- **Scope / unit:** Cross-unit: U11/U02/U07
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U11/U02/U07 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Freshness signal stale but job process healthy. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] scheduler says job exited 0; last-success gauge remains 10:00; current time 10:40; output watermark unchanged since 09:30.
- **Model answer:** Process health and output freshness disagree; investigate exporter freshness, output correctness, upstream lag, and stale metric semantics. Verify with a canary/watermark and expected row count.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U11/U02/U07.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-055 — Integration scenario

- **Scope / unit:** Cross-unit: U04/U12/U03
- **Question type:** Integration scenario
- **Level:** L4
- **Objective tested:** Integrate evidence from U04/U12/U03 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Loki label cardinality and query cost. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] indexed labels include service, env, request_id, user_id; query filters only by `level`; ingestion volume rises and query latency degrades.
- **Model answer:** Move unbounded identifiers to event fields where supported, retain bounded labels, and make queries selective on stable labels/time ranges. Validate redaction and incident lookup usability; exact pipeline/query syntax is [VERIFY].

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U04/U12/U03.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-056 — Integration scenario

- **Scope / unit:** Cross-unit: U02/U08/U13
- **Question type:** Integration scenario
- **Level:** L2
- **Objective tested:** Integrate evidence from U02/U08/U13 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** PromQL short window and low traffic. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] counter has only one sample in a 20-second range; scrape every 30 seconds; rule evaluates every 15 seconds; low traffic yields intermittent series.
- **Model answer:** The window may not contain enough samples for stable counter-rate calculation and may return no data. Use a window aligned to scrape/evaluation cadence and test low-traffic/missing-series cases; exact rule behavior [VERIFY].

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U02/U08/U13.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-057 — Integration scenario

- **Scope / unit:** Cross-unit: U05/U04/U01
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U05/U04/U01 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Collector delay versus permanent loss. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] exporter queue rises; send failures spike; backend count catches up 5 minutes later; no dropped counter increase observed.
- **Model answer:** Evidence favors delay/backpressure rather than proven permanent loss, but missing drop telemetry weakens certainty. Align counters by event time, inspect retries/queue age and canary arrival, then confirm eventual delivery.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U05/U04/U01.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-058 — Integration scenario

- **Scope / unit:** Cross-unit: U07/U03/U06
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U07/U03/U06 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Deployment and dependency graph diff. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] deployment adds a new dependency call; observed trace graph includes risk-service but declared map and dashboard links do not; alert routes to platform team.
- **Model answer:** Update declared graph and links only after verifying observed path, assign owning team, and test alert context. Compare deployment and symptom timeline; correlation suggests a lead, not causal proof.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U07/U03/U06.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-059 — Integration scenario

- **Scope / unit:** Cross-unit: U12/U01/U04
- **Question type:** Integration scenario
- **Level:** L4
- **Objective tested:** Integrate evidence from U12/U01/U04 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Retention and telemetry deletion verification. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] deletion job says 500 log chunks removed; query still returns records outside policy window due to delayed compaction/index behavior [VERIFY].
- **Model answer:** Do not claim deletion complete from the job log alone. Inspect store-specific retention/deletion semantics [VERIFY], query by event time and ingestion time, capture audit evidence, and preserve records under hold if required.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U12/U01/U04.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-060 — Integration scenario

- **Scope / unit:** Cross-unit: U05/U10/U13
- **Question type:** Integration scenario
- **Level:** L2
- **Objective tested:** Integrate evidence from U05/U10/U13 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Trace sampling bias under load. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] slow requests are 2% of traffic; head sampling retains 1% independently; a short test observes no slow trace although p99 rises.
- **Model answer:** Absence of a slow trace is compatible with sampling. Compare trace counts to request counts, check sampling policy and instrumentation, and use metrics/exemplars or a targeted local test to collect enough slow-path evidence where supported.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U05/U10/U13.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-061 — Integration scenario

- **Scope / unit:** Cross-unit: U11/U13/U09/U07
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U11/U13/U09/U07 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Online latency during scheduled backfill. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] backfill starts at 01:00; queue and database pool wait rise; scheduled freshness deadline at 01:15 is missed; online p99 doubles.
- **Model answer:** Backfill may be competing for shared resources and blocking both online traffic and the DAG. Limit or isolate backfill, protect online capacity, monitor queue/pool and watermark, and verify both online recovery and freshness catch-up.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U11/U13/U09/U07.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].

### XINT-062 — Integration scenario

- **Scope / unit:** Cross-unit: U01/U04/U05/U06/U12
- **Question type:** Integration scenario
- **Level:** L3
- **Objective tested:** Integrate evidence from U01/U04/U05/U06/U12 to make a defensible operational decision.
- **Estimated time:** 14 minutes
- **Question prompt:** **Scenario:** Evidence-preserving incident response. Use the evidence packet to state (1) observed facts, (2) the strongest supported diagnosis, (3) at least one alternative hypothesis, (4) the next discriminating check, (5) least-risk mitigation, and (6) recovery verification.
- **Artifact/scenario:** [SYNTHETIC] telemetry store nearing capacity during an incident; engineer proposes deleting all traces and restarting the Collector immediately.
- **Model answer:** First preserve a bounded evidence slice and record current counters/config; apply least-risk retention or queue mitigation, then restart only if evidence supports it. Verify pipeline recovery, dropped counts, and incident reconstruction. Broad deletion destroys evidence and may not solve the cause.

**Verification:** Re-check the relevant source and destination counters over an aligned interval, verify the user-visible symptom, and preserve a synthetic evidence record.
- **Rationale / evidence:** The packet combines at least two M11 units; no single signal establishes every causal link. Align time windows and preserve uncertainty.
- **Common wrong answers / failure modes:**
  1. Treat temporal correlation or one dashboard as proof of causation.
  2. Take a destructive action or claim recovery without an independent verification.
- **Scoring rubric:** 10 points: evidence interpretation (3); diagnosis and alternative (2); next discriminating check (2); safe mitigation/verification (2); uncertainty/limitations (1).
- **Source / coverage note:** Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Topic: Derived from the supplied prompt's curriculum map; exact syllabus section/lesson-section mapping unavailable for cross-check. Cross-unit concepts: U01/U04/U05/U06/U12.
- **Version / assumption note:** [SYNTHETIC] unless marked [ASSUMPTION]; exact tool semantics requiring installed-version confirmation are [VERIFY].



## Question inventory and coverage matrix

### Question count by unit

| Unit | Required minimum | Actual count | ID range / groups |
|---|---:|---:|---|
| Unit 1 | 13 | 14 | `U01-SA-01` … `U01-DES-01`; U01-EXT-01 |
| Unit 2 | 13 | 14 | `U02-SA-01` … `U02-DES-01`; U02-EXT-01 |
| Unit 3 | 13 | 14 | `U03-SA-01` … `U03-DES-01`; U03-EXT-01 |
| Unit 4 | 13 | 14 | `U04-SA-01` … `U04-DES-01`; U04-EXT-01 |
| Unit 5 | 13 | 14 | `U05-SA-01` … `U05-DES-01`; U05-EXT-01 |
| Unit 6 | 13 | 14 | `U06-SA-01` … `U06-DES-01`; U06-EXT-01 |
| Unit 7 | 13 | 13 | `U07-SA-01` … `U07-DES-01` |
| Unit 8 | 13 | 13 | `U08-SA-01` … `U08-DES-01` |
| Unit 9 | 13 | 13 | `U09-SA-01` … `U09-DES-01` |
| Unit 10 | 13 | 13 | `U10-SA-01` … `U10-DES-01` |
| Unit 11 | 13 | 13 | `U11-SA-01` … `U11-DES-01` |
| Unit 12 | 13 | 13 | `U12-SA-01` … `U12-DES-01` |
| Unit 13 | 13 | 13 | `U13-SA-01` … `U13-DES-01` |
| **Unit-specific subtotal** | **175** | **175** | 13 units × 13 core questions + 6 additional questions |
| **Cross-unit integration** | **45** | **62** | `XINT-001` … `XINT-062` |
| **Grand total** | **220** | **237** | **237 unique explicit question IDs** |

### Question type distribution

| Type | Actual count |
|---|---:|
| Short answer | 39 |
| MCQ | 39 |
| Artifact interpretation | 39 |
| Artifact review | 26 |
| Incident/diagnosis | 13 |
| Design | 13 |
| Additional unit questions | 6 |
| Cross-unit integration | 62 |

### Difficulty distribution

| Level | Actual count |
|---|---:|
| L1 | 39 |
| L2 | 63 |
| L3 | 95 |
| L4 | 40 |
| **Total** | **237** |

### Curriculum coverage matrix

| Unit / topic map | Representative IDs |
|---|---|
| Architecture, signal selection, lifecycle, retention, privacy, meta-monitoring | U01-SA-01–03; U01-MCQ-01–03; U01-ART-01–03; U01-REV-01–02; U01-INC-01; U01-DES-01; XINT-001, 017, 025, 035, 048, 062 |
| Prometheus types/scrape/PromQL/rate/histograms/absence/cardinality | U02-SA-01–03; U02-MCQ-01–03; U02-ART-01–03; U02-REV-01–02; U02-INC-01; U02-DES-01; XINT-017–024, 045, 056 |
| Grafana queries, units, missing data, dashboard-as-code, drift | U03-SA-01–03; U03-MCQ-01–03; U03-ART-01–03; U03-REV-01–02; U03-INC-01; U03-DES-01; XINT-018, 026, 037, 052 |
| Loki labels, redaction, parsing, gaps, retention, LogQL verification | U04-SA-01–03; U04-MCQ-01–03; U04-ART-01–03; U04-REV-01–02; U04-INC-01; U04-DES-01; XINT-004, 027, 039, 046, 055, 059 |
| Collector receivers/processors/exporters, queues, sampling, self-observability | U05-SA-01–03; U05-MCQ-01–03; U05-ART-01–03; U05-REV-01–02; U05-INC-01; U05-DES-01; XINT-005, 027, 035, 048, 057, 060 |
| Alertmanager labels/routes/groups/silences/delivery | U06-SA-01–03; U06-MCQ-01–03; U06-ART-01–03; U06-REV-01–02; U06-INC-01; U06-DES-01; XINT-006, 022, 036, 048 |
| Dependency graphs, correlation, change timelines, causal uncertainty | U07-SA-01–03; U07-MCQ-01–03; U07-ART-01–03; U07-REV-01–02; U07-INC-01; U07-DES-01; XINT-007, 025, 037, 050, 058 |
| Symptom alerts, absent/stale data, metadata, watchdogs and tests | U08-SA-01–03; U08-MCQ-01–03; U08-ART-01–03; U08-REV-01–02; U08-INC-01; U08-DES-01; XINT-008, 022, 028, 029, 045, 048 |
| Saturation, queue growth/drain, pool limits, capacity and safe mitigation | U09-SA-01–03; U09-MCQ-01–03; U09-ART-01–03; U09-REV-01–02; U09-INC-01; U09-DES-01; XINT-009, 031, 034, 041, 047 |
| Trace wall time, critical path, parallel spans, sampling and bottlenecks | U10-SA-01–03; U10-MCQ-01–03; U10-ART-01–03; U10-REV-01–02; U10-INC-01; U10-DES-01; XINT-010, 040, 041, 050, 060 |
| Freshness, deadlines, watermarks, output correctness, DAG dependencies | U11-SA-01–03; U11-MCQ-01–03; U11-ART-01–03; U11-REV-01–02; U11-INC-01; U11-DES-01; XINT-011, 028, 029, 054, 061 |
| Cardinality, churn, retention, telemetry volume, deletion verification | U12-SA-01–03; U12-MCQ-01–03; U12-ART-01–03; U12-REV-01–02; U12-INC-01; U12-DES-01; XINT-003, 012, 023, 024, 042, 051, 059 |
| Load/stress/soak, generator limits, statistical noise, leak vs cache, CI safety | U13-SA-01–03; U13-MCQ-01–03; U13-ART-01–03; U13-REV-01–02; U13-INC-01; U13-DES-01; XINT-013, 030–034, 043–044, 049, 053, 060–061 |

### Cross-unit coverage by ID

| ID | Units / concepts integrated |
|---|---|
| `XINT-001` | U01/U02/U04/U05/U12: Telemetry architecture and retention for a laptop-scale platform |
| `XINT-002` | U01/U02/U03/U06: Single versus federated Prometheus |
| `XINT-003` | U02/U09/U12: Label/cardinality policy with churn and histograms |
| `XINT-004` | U01/U04/U05/U07: Centralized logs with redaction and incident evidence |
| `XINT-005` | U05/U07/U10/U13: Trace sampling and missing-evidence risks |
| `XINT-006` | U06/U08/U01: Alertmanager routing, delivery reliability, and HA assumptions |
| `XINT-007` | U07/U03/U05/U02: Dependency correlation and graph drift |
| `XINT-008` | U08/U06/U02/U01: Symptom-based alert catalog and quality gates |
| `XINT-009` | U09/U07/U02: Saturation monitoring and capacity forecasting |
| `XINT-010` | U10/U13/U09/U07: Trace-driven bottleneck diagnosis and performance program |
| `XINT-011` | U11/U07/U02/U08: Freshness/deadline monitoring for a multi-stage DAG |
| `XINT-012` | U12/U01/U02/U04/U05: Observability governance without price estimates |
| `XINT-013` | U13/U02/U03/U09/U10: Load/soak program and safe CI gates |
| `XINT-014` | U01/U04/U05/U06/U08: Observability-stack failure recovery and meta-monitoring |
| `XINT-015` | U03/U02/U06/U07: Dashboard-as-code ownership, validation, and drift |
| `XINT-016` | U01/U03/U04/U05/U12: Build versus buy versus adopt for a small team |
| `XINT-017` | U02/U03: PromQL: rate applied to a gauge |
| `XINT-018` | U02/U03/U09: PromQL: averaging precomputed percentiles |
| `XINT-019` | U02/U07: PromQL: many-to-many vector matching |
| `XINT-020` | U02/U08: PromQL: range too short for scrape/evaluation pattern |
| `XINT-021` | U02/U12: PromQL: histogram quantile drops `le` |
| `XINT-022` | U02/U06/U08: Will this alert fire? Complete fixture |
| `XINT-023` | U02/U12: How many series will this create? Histogram dimensions |
| `XINT-024` | U02/U09/U12: Series count with pod churn and rollout overlap |
| `XINT-025` | U01/U04/U05/U07: Which signal answers this question? |
| `XINT-026` | U02/U03/U09: What is this dashboard hiding? |
| `XINT-027` | U01/U04/U05: Is this pipeline losing data, and where? |
| `XINT-028` | U11/U02/U08: Freshness alert and stale time series |
| `XINT-029` | U11/U07/U08: Job succeeds but output is empty |
| `XINT-030` | U13/U09/U10: What's wrong with this load test? Closed-loop omission |
| `XINT-031` | U13/U02/U09: What's wrong with this load test? Generator saturation |
| `XINT-032` | U13/U03/U10: Cold-cache and tiny-data mismatch |
| `XINT-033` | U13/U09: Is this a leak or cache warming? |
| `XINT-034` | U13/U09/U07: Backfill versus online traffic |
| `XINT-035` | U05/U01/U08: Collector queue full while service looks healthy |
| `XINT-036` | U06/U08/U01: Alert delivery failure and watchdog |
| `XINT-037` | U07/U03/U02: Deployment timeline versus root cause |
| `XINT-038` | U01/U04/U12: Retention deletion and incident reconstruction |
| `XINT-039` | U04/U05/U07/U12: Privacy versus correlation |
| `XINT-040` | U10/U13/U09: Trace critical path with parallel spans |
| `XINT-041` | U09/U10/U07: Saturation plus tail latency |
| `XINT-042` | U02/U12/U01: Histogram cardinality versus retention |
| `XINT-043` | U13/U02/U03: A/A noise and false-positive performance gate |
| `XINT-044` | U13/U09/U12: Soak growth and projected OOM uncertainty |
| `XINT-045` | U02/U08/U11: Missing series versus zero traffic |
| `XINT-046` | U04/U01/U05: Log ingestion gap versus quiet service |
| `XINT-047` | U09/U13: Queue drain-rate calculation |
| `XINT-048` | U01/U05/U06/U08: Can a local green heartbeat prove end-to-end health? |
| `XINT-049` | U13/U09/U01: Safe abort and cleanup for local load test |
| `XINT-050` | U01/U02/U04/U05/U07: Four-signal evidence packet and uncertainty |
| `XINT-051` | U01/U02/U04/U05/U12: Cost cut trade-off decision |
| `XINT-052` | U03/U02/U09/U10: Dashboard average hides failing instance |
| `XINT-053` | U13/U03/U02: CI smoke test versus production capacity |
| `XINT-054` | U11/U02/U07: Freshness signal stale but job process healthy |
| `XINT-055` | U04/U12/U03: Loki label cardinality and query cost |
| `XINT-056` | U02/U08/U13: PromQL short window and low traffic |
| `XINT-057` | U05/U04/U01: Collector delay versus permanent loss |
| `XINT-058` | U07/U03/U06: Deployment and dependency graph diff |
| `XINT-059` | U12/U01/U04: Retention and telemetry deletion verification |
| `XINT-060` | U05/U10/U13: Trace sampling bias under load |
| `XINT-061` | U11/U13/U09/U07: Online latency during scheduled backfill |
| `XINT-062` | U01/U04/U05/U06/U12: Evidence-preserving incident response |

### Named mandatory question styles

| Required style | Question IDs that instantiate it |
|---|---|
| “What does this PromQL return, and why is it wrong?” — rate on gauge | XINT-017 |
| PromQL average of precomputed percentiles | XINT-018 |
| PromQL many-to-many vector matching | XINT-019 |
| PromQL range too short for scrape/evaluation pattern | XINT-020; XINT-056 |
| Histogram quantile aggregation preserves `le` | XINT-021; XINT-042 |
| “Will this alert fire?” with explicit series/evaluation fixture | XINT-022 |
| “How many series will this create?” including histogram dimensions and churn | XINT-023; XINT-024 |
| “Which signal answers this question?” | XINT-025 |
| “What is this dashboard hiding?” | XINT-026; XINT-052 |
| “Is this pipeline losing data, and where?” | XINT-027; XINT-057 |
| “Will this job’s freshness alert catch this failure?” | XINT-028; XINT-029; XINT-054 |
| “What’s wrong with this load test?” — coordinated omission, generator, workload realism | XINT-030; XINT-031; XINT-032 |
| “Is this a leak or a cache warming?” | XINT-033; XINT-044 |
| “What do we cut, and what do we lose?” | XINT-051 |

### Design-review whiteboard inventory (16 required)

| ID | Design-review prompt |
|---|---|
| `XINT-001` | Telemetry architecture and retention for a laptop-scale platform |
| `XINT-002` | Single versus federated Prometheus |
| `XINT-003` | Label/cardinality policy with churn and histograms |
| `XINT-004` | Centralized logs with redaction and incident evidence |
| `XINT-005` | Trace sampling and missing-evidence risks |
| `XINT-006` | Alertmanager routing, delivery reliability, and HA assumptions |
| `XINT-007` | Dependency correlation and graph drift |
| `XINT-008` | Symptom-based alert catalog and quality gates |
| `XINT-009` | Saturation monitoring and capacity forecasting |
| `XINT-010` | Trace-driven bottleneck diagnosis and performance program |
| `XINT-011` | Freshness/deadline monitoring for a multi-stage DAG |
| `XINT-012` | Observability governance without price estimates |
| `XINT-013` | Load/soak program and safe CI gates |
| `XINT-014` | Observability-stack failure recovery and meta-monitoring |
| `XINT-015` | Dashboard-as-code ownership, validation, and drift |
| `XINT-016` | Build versus buy versus adopt for a small team |


## Ten-pass audit and sign-off

| Pass | Audit question | Result / limitation |
|---|---|---|
| 1 — Source and tree fidelity | Was the target tree and full authoritative syllabus verified? | **Partial.** The supplied prompt explicitly names the target and unit order. `Roadmap_ptree.md`, the complete syllabus-generation prompt, project README, and both capstones were not inspected. Partial search snippets for Units 1, 10, 11, 12, and 13 were visible, but their full lesson bodies were not read. |
| 2 — Curriculum coverage | Are all Units 1–13 represented with the required pattern, six extras, 45+ integrations, and 16 design reviews? | **Count passes:** each unit has 13 required categories; Units 1–6 each have one extra; unit-specific total 175; 62 cross-unit scenarios; 16 design-review prompts. Topic-level coverage uses the supplied prompt map, not an independently verified syllabus. |
| 3 — Count and ID integrity | Do IDs reconcile? | **Pass for generated document structure:** 237 explicit IDs, no duplicate IDs detected by the final inventory-generation logic; 175 unit-specific + 62 integration = 237. |
| 4 — Answer correctness and reasoning | Are calculations and technical claims internally consistent? | **Partial.** Arithmetic fixtures were constructed with explicit assumptions, including queue growth and histogram series counts. PromQL/LogQL/Alertmanager/Collector/Grafana behavior has not been run against installed versions; verify all `[VERIFY]` items. |
| 5 — Artifact quality | Are all 26 unit-specific review questions complete and corrected? | **Structural pass:** 2 review questions per unit, each with a complete synthetic snippet, three distinct risk classes, correction plan, and validation note. Human review is still needed to ensure every example fits the final syllabus and tool versions. |
| 6 — Incident and design quality | Are incident paths and design criteria present? | **Structural pass:** each unit includes symptom, first safe action, differential diagnosis, mitigation, verification, prevention, and failure modes. All 16 whiteboard prompts include alternatives, trade-offs, acceptance tests, rollback/recovery, and scoring. |
| 7 — Technical/version authenticity | Were official docs consulted or tool behavior tested? | **No.** No official documentation was consulted and no telemetry platform was run. Version-sensitive semantics remain explicitly `[VERIFY]`; do not treat this self-audit as a technical conformance test. |
| 8 — Safety and scope | Are examples local, synthetic, and cost-safe? | **Pass by content review:** fixtures use synthetic identifiers; load scenarios are local-lab-only, bounded in intent, and include abort/cleanup considerations. No credentials, customer data, public endpoints, or real vendor prices are required. |
| 9 — Learning progression | Are L1–L4 represented and scoring/readiness guidance present? | **Count pass:** L1=39, L2=63, L3=95, L4=40. Readiness bands are marked `[ILLUSTRATIVE]`; rubrics reward evidence and safety rather than unsupported certainty. |
| 10 — Completeness and disclosure | Are limitations and verification items disclosed? | **Partial.** Required sections, tables, and count reconciliation are included. Exact alignment to unavailable source files and independent human verification remain open. |

### Open verification register

1. **[VERIFY] Prometheus/PromQL:** `rate` behavior on non-counter data, range-window/sample requirements, vector matching, histogram exposition, and alert pending/firing evaluation must be checked against the installed Prometheus version and rule tests.
2. **[VERIFY] Grafana:** dashboard/provisioning schema, panel units, variable interpolation, and drift checks must be validated against the installed version.
3. **[VERIFY] Loki/LogQL:** pipeline stages, label semantics, retention and deletion behavior must be checked against the installed Loki version.
4. **[VERIFY] OpenTelemetry Collector:** component availability, configuration keys, queue/retry/drop metrics, and distribution compatibility must be checked against the installed distribution.
5. **[VERIFY] Alertmanager:** route inheritance/matching, grouping, silence behavior, templates, and delivery semantics must be tested with the installed version.
6. **[VERIFY] Telemetry backend retention/deletion:** completion requires store-specific verification, not only a successful job message.
7. **[VERIFY] Load generation/statistics:** client model semantics, coordinated-omission handling, bootstrap procedure, and confidence-interval implementation need a reproducible local harness and planted regression/A-A tests.
8. **[VERIFY] Source alignment:** inspect the actual `Roadmap_ptree.md`, complete M11 syllabus prompt, all sibling lessons, and capstone specs before treating this as the repository's final authoritative assessment.

**Unresolved verification groups:** 8 grouped areas above. Repeated `[VERIFY]` markers elsewhere refer to these groups and are not a separate test count.

### References and verification notes

No official documentation was consulted during authoring, so no external source citations are claimed. Consult the official documentation for the installed Prometheus, Grafana, Loki, OpenTelemetry Collector, and Alertmanager versions before executing or relying on version-sensitive examples. The only source-derived curriculum details used here are from the uploaded prompt's explicit topic map and visible partial search snippets; unavailable source files are listed in the metadata and audit above.

### Known limitations

- This bank was generated from the uploaded prompt's topic map and general engineering knowledge; it is not proof that each item matches a specific lesson section.
- The model answers are instructional starting points, not substitutes for checking installed tool behavior or peer review.
- All evidence packets and incident values are `[SYNTHETIC]`; none describe a real production incident.
- No code, PromQL, LogQL, YAML, dashboard JSON, Collector configuration, live query, or load test was executed in a telemetry environment.
- The AI self-audit is not independent human review. Reviewers should check factual correctness, ambiguity, rubric fairness, and curriculum fidelity before adoption.

### Final sign-off

- **Status:** `DRAFT-AUDITED — AI self-audit; human verification required`
- **Audit date:** 2026-10-28
- **Question inventory:** 237 unique IDs = 175 unit-specific + 62 cross-unit
- **Design-review prompts:** 16, IDs `XINT-001`–`XINT-016`
- **Unresolved [VERIFY] groups:** 8
- **Source availability:** uploaded prompt available; roadmap, complete syllabus-generation prompt, all full lesson bodies, project README, and both capstone specs not fully inspected.
- **Repository scope:** only this standalone `practice-questions.md` artifact is intended; no repository tree or sibling lesson was edited.
- **Human verification:** required before use as a graded or authoritative assessment.
