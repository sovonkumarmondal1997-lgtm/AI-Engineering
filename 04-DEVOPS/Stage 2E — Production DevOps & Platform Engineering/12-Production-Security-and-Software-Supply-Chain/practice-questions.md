# M12 Practice Questions — Production Security and Software Supply Chain
> A source-aligned assessment bank for explaining, implementing, validating, troubleshooting and operating the M12 controls. All fabricated artifacts are labelled `[SYNTHETIC]`; this file does not claim that commands or tests were executed.
## Metadata

- **Module:** M12
- **Stage:** 2E — Production DevOps & Platform Engineering
- **Unit:** 13 — Practice questions
- **Target file:** `practice-questions.md`
- **Estimated completion time:** `[ILLUSTRATIVE]` 35–55 hours for the full bank; split across review sessions and lab validation.
- **Last reviewed date:** 2026-10-29
- **Assumed tool/specification baseline:** conceptual assessment based on the supplied M12 syllabus-generation prompt and roadmap export; no exact tool versions are assumed. Version-sensitive commands, policy schemas, SLSA requirements, Falco fields and metrics remain `[VERIFY]` unless checked against a named official source/version.
- **Source files reviewed:** `PROMPT-Production-Security-and-Software-Supply-Chain.md`, `Roadmap(20261029-113851).md`, and the supplied Unit 13 generation prompt. The roadmap contains M12 Units 1–12, `practice-questions.md`, and `Projects/01-secure-and-verified-container-release.md`.
- **Source limitation:** the standalone generated `SYLLABUS-Production-Security-and-Software-Supply-Chain.md` was not separately supplied as a file in this turn; topic requirements are taken from the supplied syllabus-generation prompt. No claim is made that unavailable content was inspected.

## Table of contents

- [How to use this bank](#how-to-use-this-bank)
- [Assessment safety and evidence rules](#assessment-safety-and-evidence-rules)
- [Coverage and count plan](#coverage-and-count-plan)
- [Unit 1 — Threat modelling for data and ML platforms](#unit-1-threat-modelling-for-data-and-ml-platforms)- [Unit 2 — Container image scanning and vulnerability triage](#unit-2-container-image-scanning-and-vulnerability-triage)- [Unit 3 — Software bills of materials and dependency provenance](#unit-3-software-bills-of-materials-and-dependency-provenance)- [Unit 4 — Image signing and deployment verification](#unit-4-image-signing-and-deployment-verification)- [Unit 5 — Build isolation and short-lived CI identities](#unit-5-build-isolation-and-short-lived-ci-identities)- [Unit 6 — Workload identity and credential rotation (security architecture view)](#unit-6-workload-identity-and-credential-rotation-security-architecture-view)- [Unit 7 — Runtime security and container hardening](#unit-7-runtime-security-and-container-hardening)- [Unit 8 — Admission controls and deployment policy enforcement](#unit-8-admission-controls-and-deployment-policy-enforcement)- [Unit 9 — Security auditing and vulnerability remediation workflows](#unit-9-security-auditing-and-vulnerability-remediation-workflows)- [Unit 10 — SLSA framework and build provenance levels](#unit-10-slsa-framework-and-build-provenance-levels)- [Unit 11 — Kyverno and OPA Gatekeeper policy authoring](#unit-11-kyverno-and-opa-gatekeeper-policy-authoring)- [Unit 12 — Runtime threat detection with Falco](#unit-12-runtime-threat-detection-with-falco)- [Cross-unit integration questions](#cross-unit-integration-questions)
- [Design-review whiteboard prompts](#design-review-whiteboard-prompts)
- [Scoring and remediation](#scoring-and-remediation)
- [Roadmap coverage matrix](#roadmap-coverage-matrix)
- [References and version-verification register](#references-and-version-verification-register)
- [Final independent audit report](#final-independent-audit-report)

## How to use this bank

Use the bank as a closed-book reasoning assessment first, then validate operational answers in a learner-owned lab. Answer the question before reading the model answer. For artifact and configuration questions, identify the evidence boundary, at least one alternative explanation, the safe corrective action and the regression test. Use the source units in order for remediation; do not treat this bank as a substitute for the unit labs or capstone.

**Learner profile:** a data/AI engineer who completed Stages 0–2D and Stage 2E M01–M11. The learner has baseline familiarity with container images, Trivy, Syft, CI/CD and OIDC concepts, `kind`, Kubernetes RBAC/PSS/NetworkPolicy, Helm/Kustomize, GitOps, identity/secrets, incident response and observability. M12 focuses on integrating those mechanics into a defensible supply-chain security programme.

### L1–L4 calibration

| Level | Meaning | Strong response demonstrates |
|---|---|---|
| **L1 — Beginner / Foundations** | Explain threat, control, vocabulary or output. | Accurate first principles and avoids common misconceptions. |
| **L2 — Intermediate / Working Practice** | Apply a control and validate it. | Correct interpretation, positive/negative tests and practical reasoning. |
| **L3 — Advanced / Production Engineering** | Design layered controls and trade-offs. | Threat-model-driven decisions, failure modes and evidence-based justification. |
| **L4 — Expert / Operations Under Failure** | Operate, govern, debug and improve the programme. | Blast-radius reasoning, exception governance, metrics, incident ordering and residual-risk analysis. |

## Assessment safety and evidence rules

- All scenarios are defensive and limited to authorized, learner-owned fixtures. No working exploit, malware, credential theft, container-escape instructions or third-party targeting is included.
- Never use real credentials in a lab; use dummy identities and synthetic markers. Do not test credentials found in logs or third-party systems.
- Label results `PASS`, `FAIL`, `NOT RUN` or `OPEN`. A file existing is not a successful test. Never claim execution unless evidence exists.
- Treat tool flags, policy APIs, schema fields, rule names, metric names, provider claims and SLSA requirements as version-sensitive. Mark unresolved facts `[VERIFY]`.
- Mark illustrative thresholds `[ILLUSTRATIVE]` and fabricated data `[SYNTHETIC]`.
- Preserve evidence before destructive remediation when feasible. High-impact automated response needs an explicit safety case and recovery path.
- A passing assessment is evidence of learning, not proof of production security, compliance or certification.

## Coverage and count plan

| Section | Minimum / required count | IDs |
|---|---:|---|
| Units 1–12 | 15 each; 180 total | `U01-Q01`–`U12-Q15` |
| Cross-unit integration | 50 | `XINT-Q01`–`XINT-Q50` |
| Design-review whiteboards | Exactly 16 additional prompts | `DRW-Q01`–`DRW-Q16` |
| **Core question total** | **230** | 180 unit + 50 integration |
| **All unique question IDs including design reviews** | **246** | 230 core + 16 whiteboards |

Each unit contains 3 conceptual short answers, 3 four-option MCQs, 3 self-contained artifact interpretations, 3 configuration/artifact reviews (each requires at least three defects, corrections, failure mapping and regression tests), 1 incident response, 1 scored design question and 1 synthesis/troubleshooting question.

## Unit 1 — Threat modelling for data and ML platforms

**Source unit file:** `01-threat-modelling-for-data-and-ml-platforms.md`

**Coverage focus:** threat modelling before control selection; assets, actors, trust boundaries, attack surface, vulnerability/threat/risk, CIA and privacy; data-flow diagrams with processes, stores, external entities, flows and boundaries; STRIDE applied to DFD elements; lab-platform threat model with at least 10 elements, qualitative likelihood/impact, threat/control mapping, residual risk, owner and review date; attack trees for attacker-controlled code in an inference pod and training-data exfiltration; source-to-runtime supply-chain stages; ML/data threats including unsafe deserialization, poisoned training data or feature stores, compromised model hubs, notebook compromise, model theft, prompt-injection/data-exfiltration awareness, GPU/driver supply chain and over-broad access; frameworks as vocabulary/completeness aids; threat-model-as-code, validation, traceability, security debt, review cadence and limits of false precision.

### U01-Q01 — Conceptual short answer

- **ID:** `U01-Q01`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Explain the core principle: a threat model must connect an asset and trust boundary to a plausible threat, control, owner, evidence and residual risk. Why is this control or reasoning step necessary before a team makes a production decision?

**Model answer and reasoning**

The key principle is that a control claim must be bounded by its scope, trust assumptions and evidence. In this unit, a threat model must connect an asset and trust boundary to a plausible threat, control, owner, evidence and residual risk. Start from the asset/workload and the failure or threat being controlled, then state the evidence that would demonstrate the intended behavior. State residual risk rather than turning one signal into a universal guarantee.

**Common wrong answers / approaches**

Treating a tool, manifest or document as proof by itself; using a score or label without assumptions; omitting the failure mode or residual risk.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U01-Q02 — Conceptual short answer

- **ID:** `U01-Q02`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Name three distinct failure modes relevant to threat modelling for data and ml platforms and explain how you would distinguish them during review.

**Model answer and reasoning**

Use at least three categories: (1) design gap—control intent or scope is incomplete; (2) implementation/coverage gap—the configuration does not enforce the intended rule across relevant paths; (3) evidence/operations gap—the control may exist but freshness, health, ownership or actual behavior is not demonstrated. Distinguish them with architecture review, positive and negative tests, and versioned evidence.

**Common wrong answers / approaches**

Calling every failure a tooling bug; assuming configuration presence proves runtime behavior; assuming an absent alert means no event occurred.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U01-Q03 — Conceptual short answer

- **ID:** `U01-Q03`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Conceptual short answer
- **Level:** L2
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

How should this unit hand off to the earlier M01–M11 foundations without re-teaching them?

**Model answer and reasoning**

Reuse prior mechanics only as prerequisites: container basics and scanning/SBOM foundations (M01), CI/CD and OIDC concepts (M02), Kubernetes controls (M03–M04), packaging/GitOps (M06/M08), identity/secrets (M09), incident practices (M10) and observability (M11). This unit adds the security-specific trust model, evidence requirements, negative tests, governance and operational trade-offs. Record the exact prerequisite artifact or evidence instead of assuming mastery.

**Common wrong answers / approaches**

Rebuilding every earlier module; treating a prior lab success as production proof; assuming the learner knows a version-specific API not included in the source syllabus.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U01-Q04 — Multiple choice (exactly four options)

- **ID:** `U01-Q04`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Multiple choice (exactly four options)
- **Level:** L1
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Why should threat modelling precede control selection?

A. It links assets, trust boundaries and plausible threat events to controls and evidence, so controls address the actual risk.
B. Because it proves the platform has no vulnerabilities.
C. Because a framework checklist replaces architecture review.
D. Because risk scores can be calculated precisely before evidence exists.

**Model answer and reasoning**

**Correct answer: A.** It links assets, trust boundaries and plausible threat events to controls and evidence, so controls address the actual risk. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** It links assets, trust boundaries and plausible threat events to controls and evidence, so controls address the actual risk.
- **B — Incorrect/tempting:** Because it proves the platform has no vulnerabilities. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Because a framework checklist replaces architecture review. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Because risk scores can be calculated precisely before evidence exists. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to threat modelling for data and ml platforms.

**Source / verification note**

a threat model must connect an asset and trust boundary to a plausible threat, control, owner, evidence and residual risk Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U01-Q05 — Multiple choice (exactly four options)

- **ID:** `U01-Q05`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which evidence is strongest when evaluating the main control in threat modelling for data and ml platforms?

A. A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
B. A screenshot showing a configuration file exists.
C. A statement that the control is industry standard.
D. A successful test on a different platform with no recorded assumptions.

**Model answer and reasoning**

**Correct answer: A.** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
- **B — Incorrect/tempting:** A screenshot showing a configuration file exists. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A statement that the control is industry standard. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A successful test on a different platform with no recorded assumptions. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to threat modelling for data and ml platforms.

**Source / verification note**

a threat model must connect an asset and trust boundary to a plausible threat, control, owner, evidence and residual risk Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U01-Q06 — Multiple choice (exactly four options)

- **ID:** `U01-Q06`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

A team reports success for threat modelling for data and ml platforms but has not tested a failure case. What is the best review response?

A. Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
B. Accept the claim because the happy path passed.
C. Disable the control until every possible edge case is known.
D. Replace evidence with a numerical maturity score.

**Model answer and reasoning**

**Correct answer: A.** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
- **B — Incorrect/tempting:** Accept the claim because the happy path passed. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Disable the control until every possible edge case is known. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Replace evidence with a numerical maturity score. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to threat modelling for data and ml platforms.

**Source / verification note**

a threat model must connect an asset and trust boundary to a plausible threat, control, owner, evidence and residual risk Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U01-Q07 — Artifact interpretation

- **ID:** `U01-Q07`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Risk row: Asset=training data; Threat=“old Python library”; Likelihood=5; Impact=5; Control=“scanner”; Residual risk=blank; Owner=blank.
```

**Model answer and reasoning**

The row mixes a weakness with a threat event and presents unexplained precision. A scanner is only one control and does not address access, exfiltration or misuse. Rewrite as a plausible event (unauthorized principal reads/exfiltrates training data), document qualitative criteria, map least privilege, audit/detection and response, then assign owner and residual risk. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U01-Q08 — Artifact interpretation

- **ID:** `U01-Q08`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] DFD: external model hub → build runner → registry tag `latest` → inference pod. No digest, signature check or actor identity is shown.
```

**Model answer and reasoning**

The flow hides identity and mutable-tag risks. Add publisher/source identity, immutable digest, build and registry trust boundaries, signing/attestation verification, and runtime data-access paths. This still does not prove the model is safe or the source is benign. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U01-Q09 — Artifact interpretation

- **ID:** `U01-Q09`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Threat entry: “Prompt injection is always a container escape.” Control: “install Falco.”
```

**Model answer and reasoning**

The threat statement conflates application-level instruction manipulation with host/container compromise. Model the actual path to data access or tool invocation; use authorization and data-boundary controls, and separately evaluate runtime detection. Falco alone does not prevent unsafe application behavior. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U01-Q10 — Configuration / artifact review

- **ID:** `U01-Q10`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Configuration / artifact review
- **Level:** L2
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **DFD and trust-boundary review.** The diagram omits the external model hub, treats the registry as trusted by default, and does not label the shared service-account boundary. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The diagram omits the external model hub. **Correction:** Add external entity and data flows, mark CI/registry/workload trust boundaries, and trace who can publish and deploy artifacts. The omissions hide compromised-source, registry-write, and lateral-access paths. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Treats the registry as trusted by default. **Correction:** Add external entity and data flows, mark CI/registry/workload trust boundaries, and trace who can publish and deploy artifacts. The omissions hide compromised-source, registry-write, and lateral-access paths. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Does not label the shared service-account boundary. **Correction:** Add external entity and data flows, mark CI/registry/workload trust boundaries, and trace who can publish and deploy artifacts. The omissions hide compromised-source, registry-write, and lateral-access paths. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

A threat/control matrix with owner, evidence, residual risk and review date. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U01-Q11 — Configuration / artifact review

- **ID:** `U01-Q11`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **STRIDE and risk review.** The risk register calls a vulnerable package a threat, assigns a precise numeric risk score without criteria, and leaves residual risk and owner blank. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The risk register calls a vulnerable package a threat. **Correction:** Separate weakness, threat event and risk; define qualitative likelihood/impact criteria; record compensating controls, residual risk, accountable owner and review date. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Assigns a precise numeric risk score without criteria. **Correction:** Separate weakness, threat event and risk; define qualitative likelihood/impact criteria; record compensating controls, residual risk, accountable owner and review date. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Leaves residual risk and owner blank. **Correction:** Separate weakness, threat event and risk; define qualitative likelihood/impact criteria; record compensating controls, residual risk, accountable owner and review date. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

A validated risk register and at least one threat mapped to a preventive and detective control. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U01-Q12 — Configuration / artifact review

- **ID:** `U01-Q12`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **ML asset inventory review.** The model weights, training data and notebook credentials are absent; feature-store write access is not traced; model deserialization is assumed safe. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The model weights. **Correction:** Inventory data, model artifacts, identities, pipelines and runtime dependencies; record read/write paths; treat model loading as a trust boundary requiring format and provenance review. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Training data and notebook credentials are absent; feature-store write access is not traced; model deserialization is assumed safe. **Correction:** Inventory data, model artifacts, identities, pipelines and runtime dependencies; record read/write paths; treat model loading as a trust boundary requiring format and provenance review. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** The absence of a verified regression test and accountable evidence. **Correction:** Inventory data, model artifacts, identities, pipelines and runtime dependencies; record read/write paths; treat model loading as a trust boundary requiring format and provenance review. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Asset-to-flow traceability and a test that fails if a critical asset has no owner or mapped threat. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U01-Q13 — Incident / response scenario

- **ID:** `U01-Q13`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Incident / response scenario
- **Level:** L4
- **Objective tested:** Apply a safe ordered response, preserve evidence and distinguish confirmed facts from hypotheses.
- **Estimated time:** 12 minutes

**Question / scenario**

a team launches an inference API, an ETL job, and a notebook service that can read training data and pull model artifacts from a registry. Provide the response in this order: symptom → first action → contain → scope → eradicate → recover → verify → prevent.

**Model answer and reasoning**

1. **Symptom:** record the observed signal and confidence; do not assume root cause.
2. **First action:** preserve relevant logs, event records, deployment digest, identity/audit trail and timestamps; open an incident record and establish an authorized owner.
3. **Contain:** apply the least disruptive safe isolation or gate appropriate to the exposure; preserve evidence before destructive replacement where feasible.
4. **Scope:** identify affected digests, identities, workloads, data paths, trust relationships and time window.
5. **Eradicate:** remove the root cause, revoke/rotate credentials when indicated, rebuild from a trusted source and remove unsafe artifacts or policy gaps.
6. **Recover:** restore only verified artifacts/configuration and communicate service impact.
7. **Verify:** rerun safe positive/negative tests, check old credentials or untrusted artifacts are rejected where relevant, and confirm telemetry/availability.
8. **Prevent:** add a regression test, owner, expiry/review date, alert or runbook update and post-incident follow-up.

**Common wrong answers / approaches**

Immediately deleting the workload before preserving evidence; rotating credentials without inventorying downstream consumers; testing discovered third-party credentials; declaring root cause before scoping; closing the incident because service recovered.

**Evidence / verification expected**

Timeline, preserved evidence references, containment decision, affected-scope list, remediation change, recovery checks, regression test and post-incident action owner.

**Source / verification note**

Follow M10 incident-management foundations. Use only learner-owned lab resources and dummy credentials; exact platform response commands are `[VERIFY]`.

---

### U01-Q14 — Design question with scoring rubric

- **ID:** `U01-Q14`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Design question with scoring rubric
- **Level:** L3
- **Objective tested:** Produce a threat-driven design with measurable controls, safe rollout and explicit residual risk.
- **Estimated time:** 15 minutes

**Question / scenario**

Design a threat model for the inference API, ETL job, notebook platform, registry, CI runner and training-data store. Include at least 10 elements, data flows, boundaries, threats, controls, residual risk, owners and review dates.

**Model answer and reasoning**

A strong design begins with the protected assets and trust boundaries; states the intended threat reduction; assigns each control to a stage; records ownership and evidence; includes positive and negative tests; defines freshness, exception and failure behavior; and distinguishes local lab evidence from production guarantees. For this unit, prioritize: a threat model must connect an asset and trust boundary to a plausible threat, control, owner, evidence and residual risk. Include a traceability row for every high-priority threat and a residual-risk decision for each gap.

**Scoring rubric (10 points)**

- Threat/assets and trust boundaries (2)
- Correct control selection and explicit assumptions (2)
- Positive/negative tests and evidence quality (2)
- Operational ownership, exceptions and failure handling (2)
- Residual risk, limitations and review cadence (2)

**Weak (0–3):** lists tools, no trust boundary or evidence. **Adequate (4–7):** correct controls and basic tests, but incomplete ownership or residual risk. **Excellent (8–10):** threat-mapped controls, versioned evidence, safe rollout, failure tests, clear owners, measurable outcomes and candid open gaps.

**Common wrong answers / approaches**

Choosing tools before threats; designing only the happy path; ignoring service availability; treating a local test as universal; leaving exceptions unowned or indefinite.

**Evidence / verification expected**

Architecture/flow diagram, control matrix, test plan, sample evidence bundle, exception record and a list of `[VERIFY]` items.

**Source / verification note**

Use the supplied M12 unit scope; exact product-specific API details must be verified against versioned official documentation.

---

### U01-Q15 — Synthesis / troubleshooting

- **ID:** `U01-Q15`
- **Unit / scope:** Unit 1 — Threat modelling for data and ML platforms
- **Type:** Synthesis / troubleshooting
- **Level:** L4
- **Objective tested:** Distinguish control existence from effectiveness and plan evidence-driven diagnosis.
- **Estimated time:** 10 minutes

**Question / scenario**

A team claims its threat model is complete because every STRIDE category appears once. Determine what additional evidence is needed to demonstrate useful coverage.

**Model answer and reasoning**

The claim is incomplete until the team demonstrates the model’s elements and their relationships, not merely category labels. Inspect actual coverage, trust boundaries, assumptions, test evidence, ownership, residual risk and review cadence. Choose one missing or weak path, construct a benign synthetic fixture, predict expected behavior, run the check in the learner-owned environment, preserve the output and update the traceability record. Mark any platform-specific claim `[VERIFY]` until confirmed.

**Common wrong answers / approaches**

Counting labels as coverage; relying on a single happy-path test; inventing a score threshold; omitting evidence freshness; suppressing the issue instead of closing the gap.

**Evidence / verification expected**

A concise diagnosis with hypothesis, distinguishing evidence, safe test, expected outcome, result status (`PASS`, `FAIL`, `NOT RUN` or `OPEN`) and follow-up owner.

**Source / verification note**

The question tests source-syllabus principles. Any unprovided platform-specific detail remains `[VERIFY]`.

---

## Unit 2 — Container image scanning and vulnerability triage

**Source unit file:** `02-container-image-scanning-and-vulnerability-triage.md`

**Coverage focus:** scanner capabilities and blind spots; CVE/NVD/GHSA/OSV/distro advisories, CVSS versus contextual risk, CWE awareness and database freshness; Trivy image/filesystem/config/Kubernetes scanning and report interpretation; version-sensitive output/flags; OS and language packages, lockfiles, transitive dependencies, vendored/static components and scanner blind spots; controlled comparison of naive, hardened and distroless-style images with identical scanner/version/database/settings; CI gates, SARIF/JSON evidence, caching, rate limits/offline behavior, registry and scheduled rescanning; risk-based triage using exposure, reachability, exploitability, fix availability, compensating controls, criticality and blast radius; KEV/EPSS contextual use; VEX evidence, expiring ignores, DB freshness gates, remediation SLAs, trends, exposure windows, zero-day drills and metric gaming.

### U02-Q01 — Conceptual short answer

- **ID:** `U02-Q01`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Explain the core principle: a scanner finding is a triage input, not a complete risk decision; a clean report is bounded by scan scope and database freshness. Why is this control or reasoning step necessary before a team makes a production decision?

**Model answer and reasoning**

The key principle is that a control claim must be bounded by its scope, trust assumptions and evidence. In this unit, a scanner finding is a triage input, not a complete risk decision; a clean report is bounded by scan scope and database freshness. Start from the asset/workload and the failure or threat being controlled, then state the evidence that would demonstrate the intended behavior. State residual risk rather than turning one signal into a universal guarantee.

**Common wrong answers / approaches**

Treating a tool, manifest or document as proof by itself; using a score or label without assumptions; omitting the failure mode or residual risk.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U02-Q02 — Conceptual short answer

- **ID:** `U02-Q02`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Name three distinct failure modes relevant to container image scanning and vulnerability triage and explain how you would distinguish them during review.

**Model answer and reasoning**

Use at least three categories: (1) design gap—control intent or scope is incomplete; (2) implementation/coverage gap—the configuration does not enforce the intended rule across relevant paths; (3) evidence/operations gap—the control may exist but freshness, health, ownership or actual behavior is not demonstrated. Distinguish them with architecture review, positive and negative tests, and versioned evidence.

**Common wrong answers / approaches**

Calling every failure a tooling bug; assuming configuration presence proves runtime behavior; assuming an absent alert means no event occurred.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U02-Q03 — Conceptual short answer

- **ID:** `U02-Q03`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Conceptual short answer
- **Level:** L2
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

How should this unit hand off to the earlier M01–M11 foundations without re-teaching them?

**Model answer and reasoning**

Reuse prior mechanics only as prerequisites: container basics and scanning/SBOM foundations (M01), CI/CD and OIDC concepts (M02), Kubernetes controls (M03–M04), packaging/GitOps (M06/M08), identity/secrets (M09), incident practices (M10) and observability (M11). This unit adds the security-specific trust model, evidence requirements, negative tests, governance and operational trade-offs. Record the exact prerequisite artifact or evidence instead of assuming mastery.

**Common wrong answers / approaches**

Rebuilding every earlier module; treating a prior lab success as production proof; assuming the learner knows a version-specific API not included in the source syllabus.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U02-Q04 — Multiple choice (exactly four options)

- **ID:** `U02-Q04`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Multiple choice (exactly four options)
- **Level:** L1
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which is the strongest interpretation of a zero-finding scan?

A. No findings were reported within the scanner’s coverage, configuration, database state and scan time; blind spots remain.
B. The image contains no vulnerabilities.
C. All transitive, vendored and statically linked components are proven safe.
D. The image can skip future rescanning.

**Model answer and reasoning**

**Correct answer: A.** No findings were reported within the scanner’s coverage, configuration, database state and scan time; blind spots remain. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** No findings were reported within the scanner’s coverage, configuration, database state and scan time; blind spots remain.
- **B — Incorrect/tempting:** The image contains no vulnerabilities. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** All transitive, vendored and statically linked components are proven safe. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** The image can skip future rescanning. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to container image scanning and vulnerability triage.

**Source / verification note**

a scanner finding is a triage input, not a complete risk decision; a clean report is bounded by scan scope and database freshness Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U02-Q05 — Multiple choice (exactly four options)

- **ID:** `U02-Q05`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which evidence is strongest when evaluating the main control in container image scanning and vulnerability triage?

A. A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
B. A screenshot showing a configuration file exists.
C. A statement that the control is industry standard.
D. A successful test on a different platform with no recorded assumptions.

**Model answer and reasoning**

**Correct answer: A.** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
- **B — Incorrect/tempting:** A screenshot showing a configuration file exists. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A statement that the control is industry standard. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A successful test on a different platform with no recorded assumptions. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to container image scanning and vulnerability triage.

**Source / verification note**

a scanner finding is a triage input, not a complete risk decision; a clean report is bounded by scan scope and database freshness Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U02-Q06 — Multiple choice (exactly four options)

- **ID:** `U02-Q06`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

A team reports success for container image scanning and vulnerability triage but has not tested a failure case. What is the best review response?

A. Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
B. Accept the claim because the happy path passed.
C. Disable the control until every possible edge case is known.
D. Replace evidence with a numerical maturity score.

**Model answer and reasoning**

**Correct answer: A.** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
- **B — Incorrect/tempting:** Accept the claim because the happy path passed. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Disable the control until every possible edge case is known. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Replace evidence with a numerical maturity score. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to container image scanning and vulnerability triage.

**Source / verification note**

a scanner finding is a triage input, not a complete risk decision; a clean report is bounded by scan scope and database freshness Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U02-Q07 — Artifact interpretation

- **ID:** `U02-Q07`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Report metadata: image digest `sha256:abc…`; scanner version `unknown`; DB updated `2026-01-01`; scan date `2026-10-01`; finding count `0`.
```

**Model answer and reasoning**

Zero findings is not evidence of safety when scanner/database metadata are unknown or stale. Fail or mark the result inconclusive when freshness requirements are unmet; rerun with known version, current database, intended scope and captured output. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U02-Q08 — Artifact interpretation

- **ID:** `U02-Q08`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Finding A: severity=CRITICAL, internet exposed, reachable=true, fixed_version=available. Finding B: severity=HIGH, build-only, reachability=unknown, no fix. Finding C: severity=MEDIUM, not internet exposed, compensating control documented.
```

**Model answer and reasoning**

Prioritize A first based on exposure, reachability and fix availability; investigate B and seek vendor/remediation guidance rather than dismissing it; evaluate C using evidence and residual risk. Severity is a signal, not a complete ordering. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U02-Q09 — Artifact interpretation

- **ID:** `U02-Q09`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] VEX: status=not_affected; justification=blank; evidence=blank; expires=never; approver=missing.
```

**Model answer and reasoning**

Reject the assertion as unsupported; require a defensible justification, affected-product/version scope, evidence, approver and expiry/review. Do not turn missing evidence into a permanent ignore. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U02-Q10 — Configuration / artifact review

- **ID:** `U02-Q10`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Configuration / artifact review
- **Level:** L2
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **CI scan gate review.** The pipeline uses an unpinned scanner, ignores all unfixed findings forever, and uploads no machine-readable report. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The pipeline uses an unpinned scanner. **Correction:** Pin or govern the scanner version; keep time-bounded, justified exceptions; publish reports and scanner/database metadata. Otherwise results are non-reproducible, risk can be hidden, and audits cannot reconstruct the decision. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Ignores all unfixed findings forever. **Correction:** Pin or govern the scanner version; keep time-bounded, justified exceptions; publish reports and scanner/database metadata. Otherwise results are non-reproducible, risk can be hidden, and audits cannot reconstruct the decision. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Uploads no machine-readable report. **Correction:** Pin or govern the scanner version; keep time-bounded, justified exceptions; publish reports and scanner/database metadata. Otherwise results are non-reproducible, risk can be hidden, and audits cannot reconstruct the decision. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

A gate test with a blocking fixture and a reviewed, expiring exception. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U02-Q11 — Configuration / artifact review

- **ID:** `U02-Q11`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Triage queue review.** Findings are ranked by CVSS only, KEV/EPSS are treated as definitive verdicts, and fix availability is not recorded. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** Findings are ranked by CVSS only. **Correction:** Use exposure, reachability, exploitability, business criticality, fix availability and blast radius; treat KEV/EPSS as time-sensitive signals with provenance; record owner and next action. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** KEV/EPSS are treated as definitive verdicts. **Correction:** Use exposure, reachability, exploitability, business criticality, fix availability and blast radius; treat KEV/EPSS as time-sensitive signals with provenance; record owner and next action. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Fix availability is not recorded. **Correction:** Use exposure, reachability, exploitability, business criticality, fix availability and blast radius; treat KEV/EPSS as time-sensitive signals with provenance; record owner and next action. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Ranked queue with rationale and source timestamps. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U02-Q12 — Configuration / artifact review

- **ID:** `U02-Q12`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Scan-comparison review.** The naive image and distroless-style image are scanned with different scanner versions, different databases and different configuration. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The naive image and distroless-style image are scanned with different scanner versions. **Correction:** Normalize scanner, database snapshot, scope and policy; compare findings and runtime compatibility separately. Different settings make the comparison confounded. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Different databases and different configuration. **Correction:** Normalize scanner, database snapshot, scope and policy; compare findings and runtime compatibility separately. Different settings make the comparison confounded. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** The absence of a verified regression test and accountable evidence. **Correction:** Normalize scanner, database snapshot, scope and policy; compare findings and runtime compatibility separately. Different settings make the comparison confounded. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Reproducible scan manifest and a limitations note for unobservable components. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U02-Q13 — Incident / response scenario

- **ID:** `U02-Q13`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Incident / response scenario
- **Level:** L4
- **Objective tested:** Apply a safe ordered response, preserve evidence and distinguish confirmed facts from hypotheses.
- **Estimated time:** 12 minutes

**Question / scenario**

the same inference image is scanned in CI and in a weekly registry sweep; the two reports disagree because their database timestamps and scan scope differ. Provide the response in this order: symptom → first action → contain → scope → eradicate → recover → verify → prevent.

**Model answer and reasoning**

1. **Symptom:** record the observed signal and confidence; do not assume root cause.
2. **First action:** preserve relevant logs, event records, deployment digest, identity/audit trail and timestamps; open an incident record and establish an authorized owner.
3. **Contain:** apply the least disruptive safe isolation or gate appropriate to the exposure; preserve evidence before destructive replacement where feasible.
4. **Scope:** identify affected digests, identities, workloads, data paths, trust relationships and time window.
5. **Eradicate:** remove the root cause, revoke/rotate credentials when indicated, rebuild from a trusted source and remove unsafe artifacts or policy gaps.
6. **Recover:** restore only verified artifacts/configuration and communicate service impact.
7. **Verify:** rerun safe positive/negative tests, check old credentials or untrusted artifacts are rejected where relevant, and confirm telemetry/availability.
8. **Prevent:** add a regression test, owner, expiry/review date, alert or runbook update and post-incident follow-up.

**Common wrong answers / approaches**

Immediately deleting the workload before preserving evidence; rotating credentials without inventorying downstream consumers; testing discovered third-party credentials; declaring root cause before scoping; closing the incident because service recovered.

**Evidence / verification expected**

Timeline, preserved evidence references, containment decision, affected-scope list, remediation change, recovery checks, regression test and post-incident action owner.

**Source / verification note**

Follow M10 incident-management foundations. Use only learner-owned lab resources and dummy credentials; exact platform response commands are `[VERIFY]`.

---

### U02-Q14 — Design question with scoring rubric

- **ID:** `U02-Q14`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Design question with scoring rubric
- **Level:** L3
- **Objective tested:** Produce a threat-driven design with measurable controls, safe rollout and explicit residual risk.
- **Estimated time:** 15 minutes

**Question / scenario**

Design a laptop-budget scanning and triage workflow that produces reproducible evidence, contextual prioritization, expiring exceptions, freshness gates and rescanning of running digests.

**Model answer and reasoning**

A strong design begins with the protected assets and trust boundaries; states the intended threat reduction; assigns each control to a stage; records ownership and evidence; includes positive and negative tests; defines freshness, exception and failure behavior; and distinguishes local lab evidence from production guarantees. For this unit, prioritize: a scanner finding is a triage input, not a complete risk decision; a clean report is bounded by scan scope and database freshness. Include a traceability row for every high-priority threat and a residual-risk decision for each gap.

**Scoring rubric (10 points)**

- Threat/assets and trust boundaries (2)
- Correct control selection and explicit assumptions (2)
- Positive/negative tests and evidence quality (2)
- Operational ownership, exceptions and failure handling (2)
- Residual risk, limitations and review cadence (2)

**Weak (0–3):** lists tools, no trust boundary or evidence. **Adequate (4–7):** correct controls and basic tests, but incomplete ownership or residual risk. **Excellent (8–10):** threat-mapped controls, versioned evidence, safe rollout, failure tests, clear owners, measurable outcomes and candid open gaps.

**Common wrong answers / approaches**

Choosing tools before threats; designing only the happy path; ignoring service availability; treating a local test as universal; leaving exceptions unowned or indefinite.

**Evidence / verification expected**

Architecture/flow diagram, control matrix, test plan, sample evidence bundle, exception record and a list of `[VERIFY]` items.

**Source / verification note**

Use the supplied M12 unit scope; exact product-specific API details must be verified against versioned official documentation.

---

### U02-Q15 — Synthesis / troubleshooting

- **ID:** `U02-Q15`
- **Unit / scope:** Unit 2 — Container image scanning and vulnerability triage
- **Type:** Synthesis / troubleshooting
- **Level:** L4
- **Objective tested:** Distinguish control existence from effectiveness and plan evidence-driven diagnosis.
- **Estimated time:** 10 minutes

**Question / scenario**

A team reduces its finding count by 80% after enabling a broad ignore file. Explain how to test whether risk actually fell.

**Model answer and reasoning**

The claim is incomplete until the team demonstrates the model’s elements and their relationships, not merely category labels. Inspect actual coverage, trust boundaries, assumptions, test evidence, ownership, residual risk and review cadence. Choose one missing or weak path, construct a benign synthetic fixture, predict expected behavior, run the check in the learner-owned environment, preserve the output and update the traceability record. Mark any platform-specific claim `[VERIFY]` until confirmed.

**Common wrong answers / approaches**

Counting labels as coverage; relying on a single happy-path test; inventing a score threshold; omitting evidence freshness; suppressing the issue instead of closing the gap.

**Evidence / verification expected**

A concise diagnosis with hypothesis, distinguishing evidence, safe test, expected outcome, result status (`PASS`, `FAIL`, `NOT RUN` or `OPEN`) and follow-up owner.

**Source / verification note**

The question tests source-syllabus principles. Any unprovided platform-specific detail remains `[VERIFY]`.

---

## Unit 3 — Software bills of materials and dependency provenance

**Source unit file:** `03-software-bills-of-materials-and-dependency-provenance.md`

**Coverage focus:** SBOM purpose and limits; SPDX versus CycloneDX; component metadata, PURLs, hashes, relationships, licenses and tool metadata; Syft/Trivy SBOM generation and version-sensitive formats; source/lockfile versus built-image SBOM reconciliation; digest association, build-time generation, storage, indexing, release diffs and cross-artifact queries; SBOM-based vulnerability analysis, VEX relationship, signed SBOM versus attestation versus provenance; vendored, static and dynamically downloaded components; cataloger limits and false completeness; ML-BOM/model inventory awareness and limits of software SBOMs for weights, datasets, training parameters and model lineage; incident response: answer “are we affected?” from inventory; distinguish provenance from inventory.

### U03-Q01 — Conceptual short answer

- **ID:** `U03-Q01`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Explain the core principle: an SBOM is an inventory assertion about a defined subject and observation process; it does not prove build origin, safety or completeness. Why is this control or reasoning step necessary before a team makes a production decision?

**Model answer and reasoning**

The key principle is that a control claim must be bounded by its scope, trust assumptions and evidence. In this unit, an SBOM is an inventory assertion about a defined subject and observation process; it does not prove build origin, safety or completeness. Start from the asset/workload and the failure or threat being controlled, then state the evidence that would demonstrate the intended behavior. State residual risk rather than turning one signal into a universal guarantee.

**Common wrong answers / approaches**

Treating a tool, manifest or document as proof by itself; using a score or label without assumptions; omitting the failure mode or residual risk.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U03-Q02 — Conceptual short answer

- **ID:** `U03-Q02`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Name three distinct failure modes relevant to software bills of materials and dependency provenance and explain how you would distinguish them during review.

**Model answer and reasoning**

Use at least three categories: (1) design gap—control intent or scope is incomplete; (2) implementation/coverage gap—the configuration does not enforce the intended rule across relevant paths; (3) evidence/operations gap—the control may exist but freshness, health, ownership or actual behavior is not demonstrated. Distinguish them with architecture review, positive and negative tests, and versioned evidence.

**Common wrong answers / approaches**

Calling every failure a tooling bug; assuming configuration presence proves runtime behavior; assuming an absent alert means no event occurred.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U03-Q03 — Conceptual short answer

- **ID:** `U03-Q03`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Conceptual short answer
- **Level:** L2
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

How should this unit hand off to the earlier M01–M11 foundations without re-teaching them?

**Model answer and reasoning**

Reuse prior mechanics only as prerequisites: container basics and scanning/SBOM foundations (M01), CI/CD and OIDC concepts (M02), Kubernetes controls (M03–M04), packaging/GitOps (M06/M08), identity/secrets (M09), incident practices (M10) and observability (M11). This unit adds the security-specific trust model, evidence requirements, negative tests, governance and operational trade-offs. Record the exact prerequisite artifact or evidence instead of assuming mastery.

**Common wrong answers / approaches**

Rebuilding every earlier module; treating a prior lab success as production proof; assuming the learner knows a version-specific API not included in the source syllabus.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U03-Q04 — Multiple choice (exactly four options)

- **ID:** `U03-Q04`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Multiple choice (exactly four options)
- **Level:** L1
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

What question does an SBOM most directly help answer?

A. Which components are asserted to be present in a specified software artifact, subject to tool coverage and quality.
B. Who approved the source and isolated the build environment?
C. Whether every component is exploitable in the deployed context.
D. Whether a model’s predictions are fair and accurate.

**Model answer and reasoning**

**Correct answer: A.** Which components are asserted to be present in a specified software artifact, subject to tool coverage and quality. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Which components are asserted to be present in a specified software artifact, subject to tool coverage and quality.
- **B — Incorrect/tempting:** Who approved the source and isolated the build environment? This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Whether every component is exploitable in the deployed context. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Whether a model’s predictions are fair and accurate. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to software bills of materials and dependency provenance.

**Source / verification note**

an SBOM is an inventory assertion about a defined subject and observation process; it does not prove build origin, safety or completeness Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U03-Q05 — Multiple choice (exactly four options)

- **ID:** `U03-Q05`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which evidence is strongest when evaluating the main control in software bills of materials and dependency provenance?

A. A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
B. A screenshot showing a configuration file exists.
C. A statement that the control is industry standard.
D. A successful test on a different platform with no recorded assumptions.

**Model answer and reasoning**

**Correct answer: A.** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
- **B — Incorrect/tempting:** A screenshot showing a configuration file exists. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A statement that the control is industry standard. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A successful test on a different platform with no recorded assumptions. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to software bills of materials and dependency provenance.

**Source / verification note**

an SBOM is an inventory assertion about a defined subject and observation process; it does not prove build origin, safety or completeness Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U03-Q06 — Multiple choice (exactly four options)

- **ID:** `U03-Q06`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

A team reports success for software bills of materials and dependency provenance but has not tested a failure case. What is the best review response?

A. Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
B. Accept the claim because the happy path passed.
C. Disable the control until every possible edge case is known.
D. Replace evidence with a numerical maturity score.

**Model answer and reasoning**

**Correct answer: A.** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
- **B — Incorrect/tempting:** Accept the claim because the happy path passed. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Disable the control until every possible edge case is known. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Replace evidence with a numerical maturity score. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to software bills of materials and dependency provenance.

**Source / verification note**

an SBOM is an inventory assertion about a defined subject and observation process; it does not prove build origin, safety or completeness Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U03-Q07 — Artifact interpretation

- **ID:** `U03-Q07`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Source lockfile lists `lib-a==1.2`; image SBOM lists `lib-a==1.2` and `lib-b==4.0`; a static native library appears in the binary but not either inventory.
```

**Model answer and reasoning**

The source lockfile and image SBOM answer different questions. Investigate `lib-b` as a transitive/runtime addition and the native library as a cataloger blind spot; reconcile lockfile, build manifest, image and binary inspection before claiming completeness. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U03-Q08 — Artifact interpretation

- **ID:** `U03-Q08`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Release R7: SBOM subject digest=`sha256:aaa`; deployed image digest=`sha256:bbb`; release tag=`prod`.
```

**Model answer and reasoning**

The digest mismatch makes the SBOM association invalid for this deployment. Resolve the actual deployed digest from cluster/registry evidence and attach or regenerate an SBOM for that exact subject; do not rely on the mutable tag. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U03-Q09 — Artifact interpretation

- **ID:** `U03-Q09`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] “SBOM signed = build was produced from reviewed source.” No provenance predicate or builder record is attached.
```

**Model answer and reasoning**

Signing authenticates the signed statement under a trust policy; it does not transform inventory into build provenance. Obtain and verify appropriate provenance and source/builder identity evidence, and separately assess inventory completeness. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U03-Q10 — Configuration / artifact review

- **ID:** `U03-Q10`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Configuration / artifact review
- **Level:** L2
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **SBOM subject review.** The SBOM is attached to a mutable tag, the subject digest differs from the deployed digest, and the build tool/version is omitted. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The SBOM is attached to a mutable tag. **Correction:** Bind the inventory to the exact image digest; regenerate or reconcile against the actual build artifact; record generation tool and context. A tag can move, and a mismatched SBOM cannot answer whether the deployed subject contains a component. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** The subject digest differs from the deployed digest. **Correction:** Bind the inventory to the exact image digest; regenerate or reconcile against the actual build artifact; record generation tool and context. A tag can move, and a mismatched SBOM cannot answer whether the deployed subject contains a component. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** The build tool/version is omitted. **Correction:** Bind the inventory to the exact image digest; regenerate or reconcile against the actual build artifact; record generation tool and context. A tag can move, and a mismatched SBOM cannot answer whether the deployed subject contains a component. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Digest-to-SBOM index with a mismatch negative test. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U03-Q11 — Configuration / artifact review

- **ID:** `U03-Q11`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Component completeness review.** The report omits vendored native code, records no hashes, and treats absence from the inventory as proof of absence. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The report omits vendored native code. **Correction:** Check cataloger coverage, source/build/image comparison, hashes and relationships; document unobservable components and supplement with build manifests or manual inventory. Absence can be a detection gap. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Records no hashes. **Correction:** Check cataloger coverage, source/build/image comparison, hashes and relationships; document unobservable components and supplement with build manifests or manual inventory. Absence can be a detection gap. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Treats absence from the inventory as proof of absence. **Correction:** Check cataloger coverage, source/build/image comparison, hashes and relationships; document unobservable components and supplement with build manifests or manual inventory. Absence can be a detection gap. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

A completeness checklist with known synthetic components and expected detection. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U03-Q12 — Configuration / artifact review

- **ID:** `U03-Q12`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Provenance distinction review.** The team calls an SBOM “provenance,” assumes its signature proves the build was trusted, and never validates the attestation subject. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The team calls an SBOM “provenance. **Correction:** Separate inventory from origin claims; verify signature/trust policy and subject digest; evaluate builder/source claims independently. A signed inaccurate inventory can still be incomplete. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** ” assumes its signature proves the build was trusted. **Correction:** Separate inventory from origin claims; verify signature/trust policy and subject digest; evaluate builder/source claims independently. A signed inaccurate inventory can still be incomplete. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Never validates the attestation subject. **Correction:** Separate inventory from origin claims; verify signature/trust policy and subject digest; evaluate builder/source claims independently. A signed inaccurate inventory can still be incomplete. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

A verifier report connecting subject digest, SBOM and origin evidence. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U03-Q13 — Incident / response scenario

- **ID:** `U03-Q13`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Incident / response scenario
- **Level:** L4
- **Objective tested:** Apply a safe ordered response, preserve evidence and distinguish confirmed facts from hypotheses.
- **Estimated time:** 12 minutes

**Question / scenario**

a newly disclosed dependency issue needs an answer across deployed inference images, ETL workers, notebook images and model-serving bundles. Provide the response in this order: symptom → first action → contain → scope → eradicate → recover → verify → prevent.

**Model answer and reasoning**

1. **Symptom:** record the observed signal and confidence; do not assume root cause.
2. **First action:** preserve relevant logs, event records, deployment digest, identity/audit trail and timestamps; open an incident record and establish an authorized owner.
3. **Contain:** apply the least disruptive safe isolation or gate appropriate to the exposure; preserve evidence before destructive replacement where feasible.
4. **Scope:** identify affected digests, identities, workloads, data paths, trust relationships and time window.
5. **Eradicate:** remove the root cause, revoke/rotate credentials when indicated, rebuild from a trusted source and remove unsafe artifacts or policy gaps.
6. **Recover:** restore only verified artifacts/configuration and communicate service impact.
7. **Verify:** rerun safe positive/negative tests, check old credentials or untrusted artifacts are rejected where relevant, and confirm telemetry/availability.
8. **Prevent:** add a regression test, owner, expiry/review date, alert or runbook update and post-incident follow-up.

**Common wrong answers / approaches**

Immediately deleting the workload before preserving evidence; rotating credentials without inventorying downstream consumers; testing discovered third-party credentials; declaring root cause before scoping; closing the incident because service recovered.

**Evidence / verification expected**

Timeline, preserved evidence references, containment decision, affected-scope list, remediation change, recovery checks, regression test and post-incident action owner.

**Source / verification note**

Follow M10 incident-management foundations. Use only learner-owned lab resources and dummy credentials; exact platform response commands are `[VERIFY]`.

---

### U03-Q14 — Design question with scoring rubric

- **ID:** `U03-Q14`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Design question with scoring rubric
- **Level:** L3
- **Objective tested:** Produce a threat-driven design with measurable controls, safe rollout and explicit residual risk.
- **Estimated time:** 15 minutes

**Question / scenario**

Design a minimal SBOM program for image build, storage, digest indexing, release diffing, vulnerability queries and an incident-time “are we affected?” response.

**Model answer and reasoning**

A strong design begins with the protected assets and trust boundaries; states the intended threat reduction; assigns each control to a stage; records ownership and evidence; includes positive and negative tests; defines freshness, exception and failure behavior; and distinguishes local lab evidence from production guarantees. For this unit, prioritize: an SBOM is an inventory assertion about a defined subject and observation process; it does not prove build origin, safety or completeness. Include a traceability row for every high-priority threat and a residual-risk decision for each gap.

**Scoring rubric (10 points)**

- Threat/assets and trust boundaries (2)
- Correct control selection and explicit assumptions (2)
- Positive/negative tests and evidence quality (2)
- Operational ownership, exceptions and failure handling (2)
- Residual risk, limitations and review cadence (2)

**Weak (0–3):** lists tools, no trust boundary or evidence. **Adequate (4–7):** correct controls and basic tests, but incomplete ownership or residual risk. **Excellent (8–10):** threat-mapped controls, versioned evidence, safe rollout, failure tests, clear owners, measurable outcomes and candid open gaps.

**Common wrong answers / approaches**

Choosing tools before threats; designing only the happy path; ignoring service availability; treating a local test as universal; leaving exceptions unowned or indefinite.

**Evidence / verification expected**

Architecture/flow diagram, control matrix, test plan, sample evidence bundle, exception record and a list of `[VERIFY]` items.

**Source / verification note**

Use the supplied M12 unit scope; exact product-specific API details must be verified against versioned official documentation.

---

### U03-Q15 — Synthesis / troubleshooting

- **ID:** `U03-Q15`
- **Unit / scope:** Unit 3 — Software bills of materials and dependency provenance
- **Type:** Synthesis / troubleshooting
- **Level:** L4
- **Objective tested:** Distinguish control existence from effectiveness and plan evidence-driven diagnosis.
- **Estimated time:** 10 minutes

**Question / scenario**

A signed SBOM is complete according to its generator but omits a vendored static library. Explain what can and cannot be concluded.

**Model answer and reasoning**

The claim is incomplete until the team demonstrates the model’s elements and their relationships, not merely category labels. Inspect actual coverage, trust boundaries, assumptions, test evidence, ownership, residual risk and review cadence. Choose one missing or weak path, construct a benign synthetic fixture, predict expected behavior, run the check in the learner-owned environment, preserve the output and update the traceability record. Mark any platform-specific claim `[VERIFY]` until confirmed.

**Common wrong answers / approaches**

Counting labels as coverage; relying on a single happy-path test; inventing a score threshold; omitting evidence freshness; suppressing the issue instead of closing the gap.

**Evidence / verification expected**

A concise diagnosis with hypothesis, distinguishing evidence, safe test, expected outcome, result status (`PASS`, `FAIL`, `NOT RUN` or `OPEN`) and follow-up owner.

**Source / verification note**

The question tests source-syllabus principles. Any unprovided platform-specific detail remains `[VERIFY]`.

---

## Unit 4 — Image signing and deployment verification

**Source unit file:** `04-image-signing-and-deployment-verification.md`

**Coverage focus:** integrity, authenticity, identity, trust roots, digest versus tag, signature versus scan, attestation and provenance; cosign key-based signing/verification and safe key custody; keyless/OIDC trust assumptions; pinned signer identity/key, repository/ref/builder expectations and CI/admission trust policy; attestations for SBOM, scan summary, tests and provenance where supported; negative cases: unsigned artifact, wrong identity/key, tag mutation/digest mismatch, missing/stale attestation, wrong source/builder; key rotation and compromise response; model-artifact verification awareness; why signed does not mean safe; local/public Sigstore trust limitations.

### U04-Q01 — Conceptual short answer

- **ID:** `U04-Q01`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Explain the core principle: verification must bind the exact artifact digest to an expected identity and trust policy; signature validity alone does not establish safety. Why is this control or reasoning step necessary before a team makes a production decision?

**Model answer and reasoning**

The key principle is that a control claim must be bounded by its scope, trust assumptions and evidence. In this unit, verification must bind the exact artifact digest to an expected identity and trust policy; signature validity alone does not establish safety. Start from the asset/workload and the failure or threat being controlled, then state the evidence that would demonstrate the intended behavior. State residual risk rather than turning one signal into a universal guarantee.

**Common wrong answers / approaches**

Treating a tool, manifest or document as proof by itself; using a score or label without assumptions; omitting the failure mode or residual risk.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U04-Q02 — Conceptual short answer

- **ID:** `U04-Q02`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Name three distinct failure modes relevant to image signing and deployment verification and explain how you would distinguish them during review.

**Model answer and reasoning**

Use at least three categories: (1) design gap—control intent or scope is incomplete; (2) implementation/coverage gap—the configuration does not enforce the intended rule across relevant paths; (3) evidence/operations gap—the control may exist but freshness, health, ownership or actual behavior is not demonstrated. Distinguish them with architecture review, positive and negative tests, and versioned evidence.

**Common wrong answers / approaches**

Calling every failure a tooling bug; assuming configuration presence proves runtime behavior; assuming an absent alert means no event occurred.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U04-Q03 — Conceptual short answer

- **ID:** `U04-Q03`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Conceptual short answer
- **Level:** L2
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

How should this unit hand off to the earlier M01–M11 foundations without re-teaching them?

**Model answer and reasoning**

Reuse prior mechanics only as prerequisites: container basics and scanning/SBOM foundations (M01), CI/CD and OIDC concepts (M02), Kubernetes controls (M03–M04), packaging/GitOps (M06/M08), identity/secrets (M09), incident practices (M10) and observability (M11). This unit adds the security-specific trust model, evidence requirements, negative tests, governance and operational trade-offs. Record the exact prerequisite artifact or evidence instead of assuming mastery.

**Common wrong answers / approaches**

Rebuilding every earlier module; treating a prior lab success as production proof; assuming the learner knows a version-specific API not included in the source syllabus.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U04-Q04 — Multiple choice (exactly four options)

- **ID:** `U04-Q04`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Multiple choice (exactly four options)
- **Level:** L1
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

What is the purpose of checking signer identity in addition to signature validity?

A. It restricts acceptance to an expected principal/workflow rather than any party able to produce a valid signature.
B. It proves the image has no vulnerabilities.
C. It makes mutable tags immutable.
D. It proves the builder is isolated without separate evidence.

**Model answer and reasoning**

**Correct answer: A.** It restricts acceptance to an expected principal/workflow rather than any party able to produce a valid signature. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** It restricts acceptance to an expected principal/workflow rather than any party able to produce a valid signature.
- **B — Incorrect/tempting:** It proves the image has no vulnerabilities. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** It makes mutable tags immutable. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** It proves the builder is isolated without separate evidence. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to image signing and deployment verification.

**Source / verification note**

verification must bind the exact artifact digest to an expected identity and trust policy; signature validity alone does not establish safety Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U04-Q05 — Multiple choice (exactly four options)

- **ID:** `U04-Q05`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which evidence is strongest when evaluating the main control in image signing and deployment verification?

A. A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
B. A screenshot showing a configuration file exists.
C. A statement that the control is industry standard.
D. A successful test on a different platform with no recorded assumptions.

**Model answer and reasoning**

**Correct answer: A.** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
- **B — Incorrect/tempting:** A screenshot showing a configuration file exists. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A statement that the control is industry standard. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A successful test on a different platform with no recorded assumptions. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to image signing and deployment verification.

**Source / verification note**

verification must bind the exact artifact digest to an expected identity and trust policy; signature validity alone does not establish safety Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U04-Q06 — Multiple choice (exactly four options)

- **ID:** `U04-Q06`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

A team reports success for image signing and deployment verification but has not tested a failure case. What is the best review response?

A. Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
B. Accept the claim because the happy path passed.
C. Disable the control until every possible edge case is known.
D. Replace evidence with a numerical maturity score.

**Model answer and reasoning**

**Correct answer: A.** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
- **B — Incorrect/tempting:** Accept the claim because the happy path passed. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Disable the control until every possible edge case is known. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Replace evidence with a numerical maturity score. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to image signing and deployment verification.

**Source / verification note**

verification must bind the exact artifact digest to an expected identity and trust policy; signature validity alone does not establish safety Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U04-Q07 — Artifact interpretation

- **ID:** `U04-Q07`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] `verified: true`; `subject: sha256:abc`; `identity: untrusted fork workflow`; deployment digest=`sha256:abc`; policy requires protected release workflow.
```

**Model answer and reasoning**

Digest alignment is necessary but insufficient: the identity violates the policy. Deny deployment, preserve verification output and correct the signer-identity trust policy; do not widen trust to any valid signer. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U04-Q08 — Artifact interpretation

- **ID:** `U04-Q08`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Tag `inference:stable` resolved to `sha256:111` at signing; deployment later resolves it to `sha256:222`.
```

**Model answer and reasoning**

A mutable tag changed the artifact identity. Deploy by digest and verify the signature for that exact digest; retain registry audit evidence and test tag mutation as a negative case. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U04-Q09 — Artifact interpretation

- **ID:** `U04-Q09`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Image signature passes; scan report has a critical reachable finding; SBOM subject digest matches; no exception exists.
```

**Model answer and reasoning**

The image’s authenticity is supported, but the risk gate fails. Signature verification does not establish absence of vulnerabilities; block or quarantine under the release policy, remediate or approve a documented time-bounded exception. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U04-Q10 — Configuration / artifact review

- **ID:** `U04-Q10`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Configuration / artifact review
- **Level:** L2
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Verification policy review.** The check accepts any valid signature, verifies a tag rather than the requested digest, and ignores the signer identity. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The check accepts any valid signature. **Correction:** Verify the digest requested for deployment, constrain trusted signer identity/key and expected source/ref/builder, and fail closed for the protected release path. Otherwise any unrelated signed image or a different artifact may pass. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Verifies a tag rather than the requested digest. **Correction:** Verify the digest requested for deployment, constrain trusted signer identity/key and expected source/ref/builder, and fail closed for the protected release path. Otherwise any unrelated signed image or a different artifact may pass. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Ignores the signer identity. **Correction:** Verify the digest requested for deployment, constrain trusted signer identity/key and expected source/ref/builder, and fail closed for the protected release path. Otherwise any unrelated signed image or a different artifact may pass. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Positive test for approved digest and negative tests for wrong identity and digest. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U04-Q11 — Configuration / artifact review

- **ID:** `U04-Q11`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Key custody review.** The private key is stored in a shared repository, rotation has no overlap plan, and old keys are never revoked after compromise. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The private key is stored in a shared repository. **Correction:** Move key material to a controlled secret store or use a justified keyless flow; document rotation and trust-root updates; revoke/retire compromised trust material and verify old signatures are no longer accepted under the intended policy. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Rotation has no overlap plan. **Correction:** Move key material to a controlled secret store or use a justified keyless flow; document rotation and trust-root updates; revoke/retire compromised trust material and verify old signatures are no longer accepted under the intended policy. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Old keys are never revoked after compromise. **Correction:** Move key material to a controlled secret store or use a justified keyless flow; document rotation and trust-root updates; revoke/retire compromised trust material and verify old signatures are no longer accepted under the intended policy. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Key inventory, rotation rehearsal evidence and old-key rejection. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U04-Q12 — Configuration / artifact review

- **ID:** `U04-Q12`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Attestation review.** The SBOM attestation subject is not checked, a missing attestation is treated as success, and stale scan results are accepted indefinitely. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The SBOM attestation subject is not checked. **Correction:** Bind every attestation to the exact subject digest; define required predicates and freshness policy; make missing evidence fail or explicitly enter an approved exception path. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** A missing attestation is treated as success. **Correction:** Bind every attestation to the exact subject digest; define required predicates and freshness policy; make missing evidence fail or explicitly enter an approved exception path. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Stale scan results are accepted indefinitely. **Correction:** Bind every attestation to the exact subject digest; define required predicates and freshness policy; make missing evidence fail or explicitly enter an approved exception path. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Tampered-subject and missing-attestation policy tests. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U04-Q13 — Incident / response scenario

- **ID:** `U04-Q13`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Incident / response scenario
- **Level:** L4
- **Objective tested:** Apply a safe ordered response, preserve evidence and distinguish confirmed facts from hypotheses.
- **Estimated time:** 12 minutes

**Question / scenario**

a GitOps controller is about to deploy an image tag that has a valid signature from an identity outside the approved release workflow. Provide the response in this order: symptom → first action → contain → scope → eradicate → recover → verify → prevent.

**Model answer and reasoning**

1. **Symptom:** record the observed signal and confidence; do not assume root cause.
2. **First action:** preserve relevant logs, event records, deployment digest, identity/audit trail and timestamps; open an incident record and establish an authorized owner.
3. **Contain:** apply the least disruptive safe isolation or gate appropriate to the exposure; preserve evidence before destructive replacement where feasible.
4. **Scope:** identify affected digests, identities, workloads, data paths, trust relationships and time window.
5. **Eradicate:** remove the root cause, revoke/rotate credentials when indicated, rebuild from a trusted source and remove unsafe artifacts or policy gaps.
6. **Recover:** restore only verified artifacts/configuration and communicate service impact.
7. **Verify:** rerun safe positive/negative tests, check old credentials or untrusted artifacts are rejected where relevant, and confirm telemetry/availability.
8. **Prevent:** add a regression test, owner, expiry/review date, alert or runbook update and post-incident follow-up.

**Common wrong answers / approaches**

Immediately deleting the workload before preserving evidence; rotating credentials without inventorying downstream consumers; testing discovered third-party credentials; declaring root cause before scoping; closing the incident because service recovered.

**Evidence / verification expected**

Timeline, preserved evidence references, containment decision, affected-scope list, remediation change, recovery checks, regression test and post-incident action owner.

**Source / verification note**

Follow M10 incident-management foundations. Use only learner-owned lab resources and dummy credentials; exact platform response commands are `[VERIFY]`.

---

### U04-Q14 — Design question with scoring rubric

- **ID:** `U04-Q14`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Design question with scoring rubric
- **Level:** L3
- **Objective tested:** Produce a threat-driven design with measurable controls, safe rollout and explicit residual risk.
- **Estimated time:** 15 minutes

**Question / scenario**

Design a trust policy for a signed inference image covering digest binding, signer identity, key custody or keyless assumptions, attestations, negative tests and compromise response.

**Model answer and reasoning**

A strong design begins with the protected assets and trust boundaries; states the intended threat reduction; assigns each control to a stage; records ownership and evidence; includes positive and negative tests; defines freshness, exception and failure behavior; and distinguishes local lab evidence from production guarantees. For this unit, prioritize: verification must bind the exact artifact digest to an expected identity and trust policy; signature validity alone does not establish safety. Include a traceability row for every high-priority threat and a residual-risk decision for each gap.

**Scoring rubric (10 points)**

- Threat/assets and trust boundaries (2)
- Correct control selection and explicit assumptions (2)
- Positive/negative tests and evidence quality (2)
- Operational ownership, exceptions and failure handling (2)
- Residual risk, limitations and review cadence (2)

**Weak (0–3):** lists tools, no trust boundary or evidence. **Adequate (4–7):** correct controls and basic tests, but incomplete ownership or residual risk. **Excellent (8–10):** threat-mapped controls, versioned evidence, safe rollout, failure tests, clear owners, measurable outcomes and candid open gaps.

**Common wrong answers / approaches**

Choosing tools before threats; designing only the happy path; ignoring service availability; treating a local test as universal; leaving exceptions unowned or indefinite.

**Evidence / verification expected**

Architecture/flow diagram, control matrix, test plan, sample evidence bundle, exception record and a list of `[VERIFY]` items.

**Source / verification note**

Use the supplied M12 unit scope; exact product-specific API details must be verified against versioned official documentation.

---

### U04-Q15 — Synthesis / troubleshooting

- **ID:** `U04-Q15`
- **Unit / scope:** Unit 4 — Image signing and deployment verification
- **Type:** Synthesis / troubleshooting
- **Level:** L4
- **Objective tested:** Distinguish control existence from effectiveness and plan evidence-driven diagnosis.
- **Estimated time:** 10 minutes

**Question / scenario**

An image has a valid signature, current SBOM and provenance document, but the source repository was not the approved repository. Decide whether admission should pass.

**Model answer and reasoning**

The claim is incomplete until the team demonstrates the model’s elements and their relationships, not merely category labels. Inspect actual coverage, trust boundaries, assumptions, test evidence, ownership, residual risk and review cadence. Choose one missing or weak path, construct a benign synthetic fixture, predict expected behavior, run the check in the learner-owned environment, preserve the output and update the traceability record. Mark any platform-specific claim `[VERIFY]` until confirmed.

**Common wrong answers / approaches**

Counting labels as coverage; relying on a single happy-path test; inventing a score threshold; omitting evidence freshness; suppressing the issue instead of closing the gap.

**Evidence / verification expected**

A concise diagnosis with hypothesis, distinguishing evidence, safe test, expected outcome, result status (`PASS`, `FAIL`, `NOT RUN` or `OPEN`) and follow-up owner.

**Source / verification note**

The question tests source-syllabus principles. Any unprovided platform-specific detail remains `[VERIFY]`.

---

## Unit 5 — Build isolation and short-lived CI identities

**Source unit file:** `05-build-isolation-and-short-lived-ci-identities.md`

**Coverage focus:** separation of untrusted PR/fork validation from trusted release jobs; ephemeral/rootless builders where supported, least privilege and no exposed Docker socket to untrusted jobs; short-lived federated/OIDC identities; provider-specific claims only when verified; avoid long-lived registry passwords; protected refs/environments, job permissions, secret isolation, trusted/untrusted cache separation, dependency/tool pinning, hermeticity limits and controlled egress; trusted-builder claims and CI compromise kill switch; negative tests for release capability from untrusted jobs, harmless cache poisoning, dummy-secret exposure, unauthorized egress and unprotected-ref release; static CI audit limitations; M02 handoff focuses on security-specific application.

### U05-Q01 — Conceptual short answer

- **ID:** `U05-Q01`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Explain the core principle: a CI job should receive only the authority needed for its trust domain, and untrusted code must not inherit release credentials or caches. Why is this control or reasoning step necessary before a team makes a production decision?

**Model answer and reasoning**

The key principle is that a control claim must be bounded by its scope, trust assumptions and evidence. In this unit, a CI job should receive only the authority needed for its trust domain, and untrusted code must not inherit release credentials or caches. Start from the asset/workload and the failure or threat being controlled, then state the evidence that would demonstrate the intended behavior. State residual risk rather than turning one signal into a universal guarantee.

**Common wrong answers / approaches**

Treating a tool, manifest or document as proof by itself; using a score or label without assumptions; omitting the failure mode or residual risk.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U05-Q02 — Conceptual short answer

- **ID:** `U05-Q02`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Name three distinct failure modes relevant to build isolation and short-lived ci identities and explain how you would distinguish them during review.

**Model answer and reasoning**

Use at least three categories: (1) design gap—control intent or scope is incomplete; (2) implementation/coverage gap—the configuration does not enforce the intended rule across relevant paths; (3) evidence/operations gap—the control may exist but freshness, health, ownership or actual behavior is not demonstrated. Distinguish them with architecture review, positive and negative tests, and versioned evidence.

**Common wrong answers / approaches**

Calling every failure a tooling bug; assuming configuration presence proves runtime behavior; assuming an absent alert means no event occurred.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U05-Q03 — Conceptual short answer

- **ID:** `U05-Q03`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Conceptual short answer
- **Level:** L2
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

How should this unit hand off to the earlier M01–M11 foundations without re-teaching them?

**Model answer and reasoning**

Reuse prior mechanics only as prerequisites: container basics and scanning/SBOM foundations (M01), CI/CD and OIDC concepts (M02), Kubernetes controls (M03–M04), packaging/GitOps (M06/M08), identity/secrets (M09), incident practices (M10) and observability (M11). This unit adds the security-specific trust model, evidence requirements, negative tests, governance and operational trade-offs. Record the exact prerequisite artifact or evidence instead of assuming mastery.

**Common wrong answers / approaches**

Rebuilding every earlier module; treating a prior lab success as production proof; assuming the learner knows a version-specific API not included in the source syllabus.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U05-Q04 — Multiple choice (exactly four options)

- **ID:** `U05-Q04`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Multiple choice (exactly four options)
- **Level:** L1
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which control most directly limits the impact of a fork pull request?

A. Ensure untrusted jobs have no release secrets/permissions and cannot share writable trust-sensitive state with trusted jobs.
B. Run the same release workflow but add a comment warning contributors.
C. Use a longer-lived registry password so jobs do not fail.
D. Trust cache keys as proof that cached outputs are safe.

**Model answer and reasoning**

**Correct answer: A.** Ensure untrusted jobs have no release secrets/permissions and cannot share writable trust-sensitive state with trusted jobs. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Ensure untrusted jobs have no release secrets/permissions and cannot share writable trust-sensitive state with trusted jobs.
- **B — Incorrect/tempting:** Run the same release workflow but add a comment warning contributors. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Use a longer-lived registry password so jobs do not fail. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Trust cache keys as proof that cached outputs are safe. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to build isolation and short-lived ci identities.

**Source / verification note**

a CI job should receive only the authority needed for its trust domain, and untrusted code must not inherit release credentials or caches Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U05-Q05 — Multiple choice (exactly four options)

- **ID:** `U05-Q05`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which evidence is strongest when evaluating the main control in build isolation and short-lived ci identities?

A. A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
B. A screenshot showing a configuration file exists.
C. A statement that the control is industry standard.
D. A successful test on a different platform with no recorded assumptions.

**Model answer and reasoning**

**Correct answer: A.** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
- **B — Incorrect/tempting:** A screenshot showing a configuration file exists. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A statement that the control is industry standard. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A successful test on a different platform with no recorded assumptions. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to build isolation and short-lived ci identities.

**Source / verification note**

a CI job should receive only the authority needed for its trust domain, and untrusted code must not inherit release credentials or caches Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U05-Q06 — Multiple choice (exactly four options)

- **ID:** `U05-Q06`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

A team reports success for build isolation and short-lived ci identities but has not tested a failure case. What is the best review response?

A. Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
B. Accept the claim because the happy path passed.
C. Disable the control until every possible edge case is known.
D. Replace evidence with a numerical maturity score.

**Model answer and reasoning**

**Correct answer: A.** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
- **B — Incorrect/tempting:** Accept the claim because the happy path passed. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Disable the control until every possible edge case is known. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Replace evidence with a numerical maturity score. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to build isolation and short-lived ci identities.

**Source / verification note**

a CI job should receive only the authority needed for its trust domain, and untrusted code must not inherit release credentials or caches Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U05-Q07 — Artifact interpretation

- **ID:** `U05-Q07`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Job permissions: `contents: write`, `packages: write`, `id-token: write`; trigger includes fork PR; signing step has no protected-ref condition.
```

**Model answer and reasoning**

The job has excessive authority on an untrusted trigger. Minimize permissions and isolate the release workflow behind protected-ref/environment conditions plus identity-policy checks; verify with a harmless PR fixture. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U05-Q08 — Artifact interpretation

- **ID:** `U05-Q08`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Cache key=`linux-main`; both fork PR and protected release can write and restore it.
```

**Model answer and reasoning**

A shared writable cache crosses a trust boundary. Partition cache namespaces and permissions, avoid treating cache content as proof, and add a test that writes a unique harmless marker from an untrusted job and confirms it cannot reach the trusted release. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U05-Q09 — Artifact interpretation

- **ID:** `U05-Q09`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] CI credential: static registry password; expiry=`never`; available to build, test and release jobs.
```

**Model answer and reasoning**

A persistent credential broadens blast radius and complicates revocation. Replace it with narrowly scoped short-lived federation where supported; audit claim mapping and test token expiry/revocation without using real credentials. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U05-Q10 — Configuration / artifact review

- **ID:** `U05-Q10`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Configuration / artifact review
- **Level:** L2
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Workflow trust review.** Fork validation and release share one job, every job has write permissions, and signing can run for an untrusted pull request. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** Fork validation and release share one job. **Correction:** Split trust domains; use least-privilege job permissions; expose signing only after protected-ref/environment checks and verified identity claims. The current design lets attacker-controlled changes request release authority. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Every job has write permissions. **Correction:** Split trust domains; use least-privilege job permissions; expose signing only after protected-ref/environment checks and verified identity claims. The current design lets attacker-controlled changes request release authority. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Signing can run for an untrusted pull request. **Correction:** Split trust domains; use least-privilege job permissions; expose signing only after protected-ref/environment checks and verified identity claims. The current design lets attacker-controlled changes request release authority. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Negative test proves fork PR cannot sign or publish. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U05-Q11 — Configuration / artifact review

- **ID:** `U05-Q11`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Cache isolation review.** Untrusted PR writes the cache later consumed by a trusted release, cache keys omit trust-domain separation, and build outputs are accepted without validation. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** Untrusted PR writes the cache later consumed by a trusted release. **Correction:** Separate caches by trust domain; use immutable/pinned dependencies and validate outputs; do not treat cache hits as trusted build evidence. A poisoned cache can influence trusted artifacts. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Cache keys omit trust-domain separation. **Correction:** Separate caches by trust domain; use immutable/pinned dependencies and validate outputs; do not treat cache hits as trusted build evidence. A poisoned cache can influence trusted artifacts. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Build outputs are accepted without validation. **Correction:** Separate caches by trust domain; use immutable/pinned dependencies and validate outputs; do not treat cache hits as trusted build evidence. A poisoned cache can influence trusted artifacts. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Synthetic cache poisoning fixture is rejected or cannot cross trust boundary. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U05-Q12 — Configuration / artifact review

- **ID:** `U05-Q12`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Credential/egress review.** Long-lived registry secret is injected into all jobs, runner can reach arbitrary destinations, and runner lifecycle is persistent after untrusted execution. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** Long-lived registry secret is injected into all jobs. **Correction:** Use short-lived federated identity scoped to approved job/ref, restrict egress where feasible, and use ephemeral isolated runners. A dummy-secret canary and denied-egress test validate the boundary. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Runner can reach arbitrary destinations. **Correction:** Use short-lived federated identity scoped to approved job/ref, restrict egress where feasible, and use ephemeral isolated runners. A dummy-secret canary and denied-egress test validate the boundary. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Runner lifecycle is persistent after untrusted execution. **Correction:** Use short-lived federated identity scoped to approved job/ref, restrict egress where feasible, and use ephemeral isolated runners. A dummy-secret canary and denied-egress test validate the boundary. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Evidence that untrusted job lacks release identity and egress is restricted. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U05-Q13 — Incident / response scenario

- **ID:** `U05-Q13`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Incident / response scenario
- **Level:** L4
- **Objective tested:** Apply a safe ordered response, preserve evidence and distinguish confirmed facts from hypotheses.
- **Estimated time:** 12 minutes

**Question / scenario**

a fork pull request can modify workflow files while the same pipeline definition also contains signing and production-publish steps. Provide the response in this order: symptom → first action → contain → scope → eradicate → recover → verify → prevent.

**Model answer and reasoning**

1. **Symptom:** record the observed signal and confidence; do not assume root cause.
2. **First action:** preserve relevant logs, event records, deployment digest, identity/audit trail and timestamps; open an incident record and establish an authorized owner.
3. **Contain:** apply the least disruptive safe isolation or gate appropriate to the exposure; preserve evidence before destructive replacement where feasible.
4. **Scope:** identify affected digests, identities, workloads, data paths, trust relationships and time window.
5. **Eradicate:** remove the root cause, revoke/rotate credentials when indicated, rebuild from a trusted source and remove unsafe artifacts or policy gaps.
6. **Recover:** restore only verified artifacts/configuration and communicate service impact.
7. **Verify:** rerun safe positive/negative tests, check old credentials or untrusted artifacts are rejected where relevant, and confirm telemetry/availability.
8. **Prevent:** add a regression test, owner, expiry/review date, alert or runbook update and post-incident follow-up.

**Common wrong answers / approaches**

Immediately deleting the workload before preserving evidence; rotating credentials without inventorying downstream consumers; testing discovered third-party credentials; declaring root cause before scoping; closing the incident because service recovered.

**Evidence / verification expected**

Timeline, preserved evidence references, containment decision, affected-scope list, remediation change, recovery checks, regression test and post-incident action owner.

**Source / verification note**

Follow M10 incident-management foundations. Use only learner-owned lab resources and dummy credentials; exact platform response commands are `[VERIFY]`.

---

### U05-Q14 — Design question with scoring rubric

- **ID:** `U05-Q14`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Design question with scoring rubric
- **Level:** L3
- **Objective tested:** Produce a threat-driven design with measurable controls, safe rollout and explicit residual risk.
- **Estimated time:** 15 minutes

**Question / scenario**

Design an isolated CI trust boundary with separate untrusted validation and trusted release paths, ephemeral execution, cache separation, OIDC claims, egress policy and kill switch.

**Model answer and reasoning**

A strong design begins with the protected assets and trust boundaries; states the intended threat reduction; assigns each control to a stage; records ownership and evidence; includes positive and negative tests; defines freshness, exception and failure behavior; and distinguishes local lab evidence from production guarantees. For this unit, prioritize: a CI job should receive only the authority needed for its trust domain, and untrusted code must not inherit release credentials or caches. Include a traceability row for every high-priority threat and a residual-risk decision for each gap.

**Scoring rubric (10 points)**

- Threat/assets and trust boundaries (2)
- Correct control selection and explicit assumptions (2)
- Positive/negative tests and evidence quality (2)
- Operational ownership, exceptions and failure handling (2)
- Residual risk, limitations and review cadence (2)

**Weak (0–3):** lists tools, no trust boundary or evidence. **Adequate (4–7):** correct controls and basic tests, but incomplete ownership or residual risk. **Excellent (8–10):** threat-mapped controls, versioned evidence, safe rollout, failure tests, clear owners, measurable outcomes and candid open gaps.

**Common wrong answers / approaches**

Choosing tools before threats; designing only the happy path; ignoring service availability; treating a local test as universal; leaving exceptions unowned or indefinite.

**Evidence / verification expected**

Architecture/flow diagram, control matrix, test plan, sample evidence bundle, exception record and a list of `[VERIFY]` items.

**Source / verification note**

Use the supplied M12 unit scope; exact product-specific API details must be verified against versioned official documentation.

---

### U05-Q15 — Synthesis / troubleshooting

- **ID:** `U05-Q15`
- **Unit / scope:** Unit 5 — Build isolation and short-lived CI identities
- **Type:** Synthesis / troubleshooting
- **Level:** L4
- **Objective tested:** Distinguish control existence from effectiveness and plan evidence-driven diagnosis.
- **Estimated time:** 10 minutes

**Question / scenario**

A static workflow linter finds no issue, but runtime logs show a fork job requested an identity token. Explain the evidence gap and safe next steps.

**Model answer and reasoning**

The claim is incomplete until the team demonstrates the model’s elements and their relationships, not merely category labels. Inspect actual coverage, trust boundaries, assumptions, test evidence, ownership, residual risk and review cadence. Choose one missing or weak path, construct a benign synthetic fixture, predict expected behavior, run the check in the learner-owned environment, preserve the output and update the traceability record. Mark any platform-specific claim `[VERIFY]` until confirmed.

**Common wrong answers / approaches**

Counting labels as coverage; relying on a single happy-path test; inventing a score threshold; omitting evidence freshness; suppressing the issue instead of closing the gap.

**Evidence / verification expected**

A concise diagnosis with hypothesis, distinguishing evidence, safe test, expected outcome, result status (`PASS`, `FAIL`, `NOT RUN` or `OPEN`) and follow-up owner.

**Source / verification note**

The question tests source-syllabus principles. Any unprovided platform-specific detail remains `[VERIFY]`.

---

## Unit 6 — Workload identity and credential rotation (security architecture view)

**Source unit file:** `06-workload-identity-and-credential-rotation.md`

**Coverage focus:** identity inventory and trust relationships across workloads, service accounts, cloud identities, CI identities and humans; workload identity versus static credentials; least privilege, just-in-time access, token lifetime, rotation/revocation, ownership and auditability; attack paths and blast radius if an identity/token is stolen; rotation drills with measured timestamps, token-theft detection concepts and verification old credentials no longer work; dummy lab identities only; M09 handoff avoids re-teaching identity mechanism implementation; incident ordering: preserve evidence, revoke/rotate appropriately, assess downstream trust and verify recovery.

### U06-Q01 — Conceptual short answer

- **ID:** `U06-Q01`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Explain the core principle: identity security is an authorization and lifecycle problem; rotating a credential is incomplete until old material is rejected and downstream trust is assessed. Why is this control or reasoning step necessary before a team makes a production decision?

**Model answer and reasoning**

The key principle is that a control claim must be bounded by its scope, trust assumptions and evidence. In this unit, identity security is an authorization and lifecycle problem; rotating a credential is incomplete until old material is rejected and downstream trust is assessed. Start from the asset/workload and the failure or threat being controlled, then state the evidence that would demonstrate the intended behavior. State residual risk rather than turning one signal into a universal guarantee.

**Common wrong answers / approaches**

Treating a tool, manifest or document as proof by itself; using a score or label without assumptions; omitting the failure mode or residual risk.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U06-Q02 — Conceptual short answer

- **ID:** `U06-Q02`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Name three distinct failure modes relevant to workload identity and credential rotation (security architecture view) and explain how you would distinguish them during review.

**Model answer and reasoning**

Use at least three categories: (1) design gap—control intent or scope is incomplete; (2) implementation/coverage gap—the configuration does not enforce the intended rule across relevant paths; (3) evidence/operations gap—the control may exist but freshness, health, ownership or actual behavior is not demonstrated. Distinguish them with architecture review, positive and negative tests, and versioned evidence.

**Common wrong answers / approaches**

Calling every failure a tooling bug; assuming configuration presence proves runtime behavior; assuming an absent alert means no event occurred.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U06-Q03 — Conceptual short answer

- **ID:** `U06-Q03`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Conceptual short answer
- **Level:** L2
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

How should this unit hand off to the earlier M01–M11 foundations without re-teaching them?

**Model answer and reasoning**

Reuse prior mechanics only as prerequisites: container basics and scanning/SBOM foundations (M01), CI/CD and OIDC concepts (M02), Kubernetes controls (M03–M04), packaging/GitOps (M06/M08), identity/secrets (M09), incident practices (M10) and observability (M11). This unit adds the security-specific trust model, evidence requirements, negative tests, governance and operational trade-offs. Record the exact prerequisite artifact or evidence instead of assuming mastery.

**Common wrong answers / approaches**

Rebuilding every earlier module; treating a prior lab success as production proof; assuming the learner knows a version-specific API not included in the source syllabus.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U06-Q04 — Multiple choice (exactly four options)

- **ID:** `U06-Q04`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Multiple choice (exactly four options)
- **Level:** L1
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

What is the best evidence that a credential rotation succeeded?

A. The new credential works as intended and the old credential is rejected by all relevant relying services, with timestamps and downstream scope documented.
B. A secret manager shows a new version number.
C. The workload restarted once.
D. The old token was not observed in logs for five minutes.

**Model answer and reasoning**

**Correct answer: A.** The new credential works as intended and the old credential is rejected by all relevant relying services, with timestamps and downstream scope documented. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** The new credential works as intended and the old credential is rejected by all relevant relying services, with timestamps and downstream scope documented.
- **B — Incorrect/tempting:** A secret manager shows a new version number. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** The workload restarted once. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** The old token was not observed in logs for five minutes. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to workload identity and credential rotation (security architecture view).

**Source / verification note**

identity security is an authorization and lifecycle problem; rotating a credential is incomplete until old material is rejected and downstream trust is assessed Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U06-Q05 — Multiple choice (exactly four options)

- **ID:** `U06-Q05`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which evidence is strongest when evaluating the main control in workload identity and credential rotation (security architecture view)?

A. A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
B. A screenshot showing a configuration file exists.
C. A statement that the control is industry standard.
D. A successful test on a different platform with no recorded assumptions.

**Model answer and reasoning**

**Correct answer: A.** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
- **B — Incorrect/tempting:** A screenshot showing a configuration file exists. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A statement that the control is industry standard. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A successful test on a different platform with no recorded assumptions. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to workload identity and credential rotation (security architecture view).

**Source / verification note**

identity security is an authorization and lifecycle problem; rotating a credential is incomplete until old material is rejected and downstream trust is assessed Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U06-Q06 — Multiple choice (exactly four options)

- **ID:** `U06-Q06`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

A team reports success for workload identity and credential rotation (security architecture view) but has not tested a failure case. What is the best review response?

A. Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
B. Accept the claim because the happy path passed.
C. Disable the control until every possible edge case is known.
D. Replace evidence with a numerical maturity score.

**Model answer and reasoning**

**Correct answer: A.** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
- **B — Incorrect/tempting:** Accept the claim because the happy path passed. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Disable the control until every possible edge case is known. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Replace evidence with a numerical maturity score. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to workload identity and credential rotation (security architecture view).

**Source / verification note**

identity security is an authorization and lifecycle problem; rotating a credential is incomplete until old material is rejected and downstream trust is assessed Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U06-Q07 — Artifact interpretation

- **ID:** `U06-Q07`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Identity A can `read:training-data`, `write:model-registry`, and `update:deployment-policy`; Identity B can only `read:model-registry`; both are used by inference.
```

**Model answer and reasoning**

Identity A has a disproportionate blast radius for inference. Split publishing/deployment authority from runtime read access, then validate permissions using a harmless authorization test and audit logs. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U06-Q08 — Artifact interpretation

- **ID:** `U06-Q08`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Rotation record: new credential issued 10:00; old credential rejection=NOT TESTED; cached copy search=NOT DONE; downstream consumers=unknown.
```

**Model answer and reasoning**

Rotation is incomplete. Inventory consumers and caches, test rejection of the old dummy credential at every relying service, and record measured completion timestamps and residual dependencies. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U06-Q09 — Artifact interpretation

- **ID:** `U06-Q09`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Token event: access denied at 10:04; operator immediately deletes pod; no audit snapshot or downstream token inventory retained.
```

**Model answer and reasoning**

Deleting the workload first may destroy evidence and does not revoke downstream credentials. Preserve relevant audit/runtime evidence, contain exposure, revoke or rotate as justified, scope dependent services, then replace and verify the workload. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U06-Q10 — Configuration / artifact review

- **ID:** `U06-Q10`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Configuration / artifact review
- **Level:** L2
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Identity inventory review.** A production identity has no owner, its permissions exceed the workload need, and audit evidence has no destination. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** A production identity has no owner. **Correction:** Assign an owner, reduce permissions to necessary resources/actions and verify logs reach a protected audit sink. Without these, token compromise is difficult to contain or investigate. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Its permissions exceed the workload need. **Correction:** Assign an owner, reduce permissions to necessary resources/actions and verify logs reach a protected audit sink. Without these, token compromise is difficult to contain or investigate. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Audit evidence has no destination. **Correction:** Assign an owner, reduce permissions to necessary resources/actions and verify logs reach a protected audit sink. Without these, token compromise is difficult to contain or investigate. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Inventory with owner, scope, expiry and evidence source. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U06-Q11 — Configuration / artifact review

- **ID:** `U06-Q11`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Rotation drill review.** The drill records the new token issuance but never tests the old token, leaves cached credentials unexamined, and has no recovery/rollback plan. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The drill records the new token issuance but never tests the old token. **Correction:** Use dummy credentials; record start/end timestamps; prove old token rejection across every relying service; locate caches and downstream trust; define safe rollback that does not re-enable compromised material. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Leaves cached credentials unexamined. **Correction:** Use dummy credentials; record start/end timestamps; prove old token rejection across every relying service; locate caches and downstream trust; define safe rollback that does not re-enable compromised material. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Has no recovery/rollback plan. **Correction:** Use dummy credentials; record start/end timestamps; prove old token rejection across every relying service; locate caches and downstream trust; define safe rollback that does not re-enable compromised material. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Evidence old credential fails and new credential works within the stated objective. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U06-Q12 — Configuration / artifact review

- **ID:** `U06-Q12`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Blast-radius review.** One identity can read training data, publish model artifacts and alter deployment policy; the design assumes token theft is unlikely. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** One identity can read training data. **Correction:** Separate identities by trust boundary and privilege; map allowed resources/actions and downstream trust; define revocation order and impact if the identity is compromised. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Publish model artifacts and alter deployment policy; the design assumes token theft is unlikely. **Correction:** Separate identities by trust boundary and privilege; map allowed resources/actions and downstream trust; define revocation order and impact if the identity is compromised. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** The absence of a verified regression test and accountable evidence. **Correction:** Separate identities by trust boundary and privilege; map allowed resources/actions and downstream trust; define revocation order and impact if the identity is compromised. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Access graph and a least-privilege regression test. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U06-Q13 — Incident / response scenario

- **ID:** `U06-Q13`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Incident / response scenario
- **Level:** L4
- **Objective tested:** Apply a safe ordered response, preserve evidence and distinguish confirmed facts from hypotheses.
- **Estimated time:** 12 minutes

**Question / scenario**

an inference workload's service identity can read training data, write to a feature store and retrieve registry artifacts, but only one of those permissions is required. Provide the response in this order: symptom → first action → contain → scope → eradicate → recover → verify → prevent.

**Model answer and reasoning**

1. **Symptom:** record the observed signal and confidence; do not assume root cause.
2. **First action:** preserve relevant logs, event records, deployment digest, identity/audit trail and timestamps; open an incident record and establish an authorized owner.
3. **Contain:** apply the least disruptive safe isolation or gate appropriate to the exposure; preserve evidence before destructive replacement where feasible.
4. **Scope:** identify affected digests, identities, workloads, data paths, trust relationships and time window.
5. **Eradicate:** remove the root cause, revoke/rotate credentials when indicated, rebuild from a trusted source and remove unsafe artifacts or policy gaps.
6. **Recover:** restore only verified artifacts/configuration and communicate service impact.
7. **Verify:** rerun safe positive/negative tests, check old credentials or untrusted artifacts are rejected where relevant, and confirm telemetry/availability.
8. **Prevent:** add a regression test, owner, expiry/review date, alert or runbook update and post-incident follow-up.

**Common wrong answers / approaches**

Immediately deleting the workload before preserving evidence; rotating credentials without inventorying downstream consumers; testing discovered third-party credentials; declaring root cause before scoping; closing the incident because service recovered.

**Evidence / verification expected**

Timeline, preserved evidence references, containment decision, affected-scope list, remediation change, recovery checks, regression test and post-incident action owner.

**Source / verification note**

Follow M10 incident-management foundations. Use only learner-owned lab resources and dummy credentials; exact platform response commands are `[VERIFY]`.

---

### U06-Q14 — Design question with scoring rubric

- **ID:** `U06-Q14`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Design question with scoring rubric
- **Level:** L3
- **Objective tested:** Produce a threat-driven design with measurable controls, safe rollout and explicit residual risk.
- **Estimated time:** 15 minutes

**Question / scenario**

Design an identity inventory and rotation drill for CI, inference, ETL and notebook workloads using dummy identities, owners, expiry, auditability and old-token rejection evidence.

**Model answer and reasoning**

A strong design begins with the protected assets and trust boundaries; states the intended threat reduction; assigns each control to a stage; records ownership and evidence; includes positive and negative tests; defines freshness, exception and failure behavior; and distinguishes local lab evidence from production guarantees. For this unit, prioritize: identity security is an authorization and lifecycle problem; rotating a credential is incomplete until old material is rejected and downstream trust is assessed. Include a traceability row for every high-priority threat and a residual-risk decision for each gap.

**Scoring rubric (10 points)**

- Threat/assets and trust boundaries (2)
- Correct control selection and explicit assumptions (2)
- Positive/negative tests and evidence quality (2)
- Operational ownership, exceptions and failure handling (2)
- Residual risk, limitations and review cadence (2)

**Weak (0–3):** lists tools, no trust boundary or evidence. **Adequate (4–7):** correct controls and basic tests, but incomplete ownership or residual risk. **Excellent (8–10):** threat-mapped controls, versioned evidence, safe rollout, failure tests, clear owners, measurable outcomes and candid open gaps.

**Common wrong answers / approaches**

Choosing tools before threats; designing only the happy path; ignoring service availability; treating a local test as universal; leaving exceptions unowned or indefinite.

**Evidence / verification expected**

Architecture/flow diagram, control matrix, test plan, sample evidence bundle, exception record and a list of `[VERIFY]` items.

**Source / verification note**

Use the supplied M12 unit scope; exact product-specific API details must be verified against versioned official documentation.

---

### U06-Q15 — Synthesis / troubleshooting

- **ID:** `U06-Q15`
- **Unit / scope:** Unit 6 — Workload identity and credential rotation (security architecture view)
- **Type:** Synthesis / troubleshooting
- **Level:** L4
- **Objective tested:** Distinguish control existence from effectiveness and plan evidence-driven diagnosis.
- **Estimated time:** 10 minutes

**Question / scenario**

A token is short-lived but can mint broader credentials through an overprivileged identity. Explain why lifetime alone does not bound blast radius.

**Model answer and reasoning**

The claim is incomplete until the team demonstrates the model’s elements and their relationships, not merely category labels. Inspect actual coverage, trust boundaries, assumptions, test evidence, ownership, residual risk and review cadence. Choose one missing or weak path, construct a benign synthetic fixture, predict expected behavior, run the check in the learner-owned environment, preserve the output and update the traceability record. Mark any platform-specific claim `[VERIFY]` until confirmed.

**Common wrong answers / approaches**

Counting labels as coverage; relying on a single happy-path test; inventing a score threshold; omitting evidence freshness; suppressing the issue instead of closing the gap.

**Evidence / verification expected**

A concise diagnosis with hypothesis, distinguishing evidence, safe test, expected outcome, result status (`PASS`, `FAIL`, `NOT RUN` or `OPEN`) and follow-up owner.

**Source / verification note**

The question tests source-syllabus principles. Any unprovided platform-specific detail remains `[VERIFY]`.

---

## Unit 7 — Runtime security and container hardening

**Source unit file:** `07-runtime-security-and-container-hardening.md`

**Coverage focus:** non-root, read-only root filesystem, capability dropping, allowPrivilegeEscalation, seccomp, resources, service-account token mounting and probes; Pod Security Standards and version-sensitive enforcement behavior; NetworkPolicy default-deny, explicit flows and CNI enforcement caveats; runtime conformance suite with expected denials; kube-bench/CIS triage with verified versions; container-compromise drill: isolate, preserve evidence, rotate credentials and replace workload; hardening trade-offs, compatibility, exception owners and expiry; limits of runtime hardening.

### U07-Q01 — Conceptual short answer

- **ID:** `U07-Q01`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Explain the core principle: runtime hardening reduces available privilege and reachable paths but does not prove application safety or replace supply-chain controls. Why is this control or reasoning step necessary before a team makes a production decision?

**Model answer and reasoning**

The key principle is that a control claim must be bounded by its scope, trust assumptions and evidence. In this unit, runtime hardening reduces available privilege and reachable paths but does not prove application safety or replace supply-chain controls. Start from the asset/workload and the failure or threat being controlled, then state the evidence that would demonstrate the intended behavior. State residual risk rather than turning one signal into a universal guarantee.

**Common wrong answers / approaches**

Treating a tool, manifest or document as proof by itself; using a score or label without assumptions; omitting the failure mode or residual risk.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U07-Q02 — Conceptual short answer

- **ID:** `U07-Q02`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Name three distinct failure modes relevant to runtime security and container hardening and explain how you would distinguish them during review.

**Model answer and reasoning**

Use at least three categories: (1) design gap—control intent or scope is incomplete; (2) implementation/coverage gap—the configuration does not enforce the intended rule across relevant paths; (3) evidence/operations gap—the control may exist but freshness, health, ownership or actual behavior is not demonstrated. Distinguish them with architecture review, positive and negative tests, and versioned evidence.

**Common wrong answers / approaches**

Calling every failure a tooling bug; assuming configuration presence proves runtime behavior; assuming an absent alert means no event occurred.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U07-Q03 — Conceptual short answer

- **ID:** `U07-Q03`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Conceptual short answer
- **Level:** L2
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

How should this unit hand off to the earlier M01–M11 foundations without re-teaching them?

**Model answer and reasoning**

Reuse prior mechanics only as prerequisites: container basics and scanning/SBOM foundations (M01), CI/CD and OIDC concepts (M02), Kubernetes controls (M03–M04), packaging/GitOps (M06/M08), identity/secrets (M09), incident practices (M10) and observability (M11). This unit adds the security-specific trust model, evidence requirements, negative tests, governance and operational trade-offs. Record the exact prerequisite artifact or evidence instead of assuming mastery.

**Common wrong answers / approaches**

Rebuilding every earlier module; treating a prior lab success as production proof; assuming the learner knows a version-specific API not included in the source syllabus.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U07-Q04 — Multiple choice (exactly four options)

- **ID:** `U07-Q04`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Multiple choice (exactly four options)
- **Level:** L1
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

What does a non-root, read-only, least-privilege pod configuration establish?

A. It reduces selected runtime privileges and write paths, but does not prove the image is trustworthy or the application cannot access authorized sensitive data.
B. It guarantees no container compromise is possible.
C. It proves NetworkPolicy is enforced by the CNI.
D. It proves the image signature and SBOM are valid.

**Model answer and reasoning**

**Correct answer: A.** It reduces selected runtime privileges and write paths, but does not prove the image is trustworthy or the application cannot access authorized sensitive data. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** It reduces selected runtime privileges and write paths, but does not prove the image is trustworthy or the application cannot access authorized sensitive data.
- **B — Incorrect/tempting:** It guarantees no container compromise is possible. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** It proves NetworkPolicy is enforced by the CNI. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** It proves the image signature and SBOM are valid. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to runtime security and container hardening.

**Source / verification note**

runtime hardening reduces available privilege and reachable paths but does not prove application safety or replace supply-chain controls Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U07-Q05 — Multiple choice (exactly four options)

- **ID:** `U07-Q05`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which evidence is strongest when evaluating the main control in runtime security and container hardening?

A. A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
B. A screenshot showing a configuration file exists.
C. A statement that the control is industry standard.
D. A successful test on a different platform with no recorded assumptions.

**Model answer and reasoning**

**Correct answer: A.** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
- **B — Incorrect/tempting:** A screenshot showing a configuration file exists. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A statement that the control is industry standard. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A successful test on a different platform with no recorded assumptions. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to runtime security and container hardening.

**Source / verification note**

runtime hardening reduces available privilege and reachable paths but does not prove application safety or replace supply-chain controls Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U07-Q06 — Multiple choice (exactly four options)

- **ID:** `U07-Q06`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

A team reports success for runtime security and container hardening but has not tested a failure case. What is the best review response?

A. Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
B. Accept the claim because the happy path passed.
C. Disable the control until every possible edge case is known.
D. Replace evidence with a numerical maturity score.

**Model answer and reasoning**

**Correct answer: A.** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
- **B — Incorrect/tempting:** Accept the claim because the happy path passed. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Disable the control until every possible edge case is known. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Replace evidence with a numerical maturity score. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to runtime security and container hardening.

**Source / verification note**

runtime hardening reduces available privilege and reachable paths but does not prove application safety or replace supply-chain controls Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U07-Q07 — Artifact interpretation

- **ID:** `U07-Q07`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Pod security summary: non-root=false; capabilities=default; root filesystem=writable; token mounted=true; `kind` test=pass.
```

**Model answer and reasoning**

The configuration retains avoidable privilege and the local result is limited to that environment. Harden identity, filesystem and capabilities; test both allowed and denied cases and record platform/version limitations. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U07-Q08 — Artifact interpretation

- **ID:** `U07-Q08`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] NetworkPolicy manifest exists; CNI is not identified; policy selects `app=inference`; no ingress/egress rules shown in excerpt.
```

**Model answer and reasoning**

Manifest existence does not prove enforcement. Verify CNI support and effective policy behavior using harmless allowed/denied connectivity tests; confirm labels match the actual pods. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U07-Q09 — Artifact interpretation

- **ID:** `U07-Q09`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Exception: `allow-root=true`; owner=`platform`; expiry=`never`; evidence=`works on my machine`.
```

**Model answer and reasoning**

This is not a governed exception. Require specific workload scope, justification, compensating controls, accountable owner, expiry, review date and regression evidence; reject indefinite blanket exceptions. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U07-Q10 — Configuration / artifact review

- **ID:** `U07-Q10`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Configuration / artifact review
- **Level:** L2
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Pod hardening review.** The workload runs as root, permits privilege escalation, and leaves the root filesystem writable. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The workload runs as root. **Correction:** Run as a non-root identity where compatible, disable privilege escalation and use a read-only root filesystem with explicit writable volumes. These defaults increase the impact of application compromise. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Permits privilege escalation. **Correction:** Run as a non-root identity where compatible, disable privilege escalation and use a read-only root filesystem with explicit writable volumes. These defaults increase the impact of application compromise. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Leaves the root filesystem writable. **Correction:** Run as a non-root identity where compatible, disable privilege escalation and use a read-only root filesystem with explicit writable volumes. These defaults increase the impact of application compromise. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Conformance test showing intended insecure fixture denied. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U07-Q11 — Configuration / artifact review

- **ID:** `U07-Q11`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Identity/network review.** The default service account is used, token automount is enabled without need, and no explicit network boundary exists. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The default service account is used. **Correction:** Use a dedicated least-privilege service account, disable token mounting when unnecessary, and apply default-deny plus documented flows only where the CNI enforces NetworkPolicy. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Token automount is enabled without need. **Correction:** Use a dedicated least-privilege service account, disable token mounting when unnecessary, and apply default-deny plus documented flows only where the CNI enforces NetworkPolicy. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** No explicit network boundary exists. **Correction:** Use a dedicated least-privilege service account, disable token mounting when unnecessary, and apply default-deny plus documented flows only where the CNI enforces NetworkPolicy. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Evidence from the target CNI/platform, not just YAML presence. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U07-Q12 — Configuration / artifact review

- **ID:** `U07-Q12`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Operational limits review.** No resource limits/probes are set, a broad exception has no expiry, and a local `kind` test is claimed as managed-cluster proof. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** No resource limits/probes are set. **Correction:** Add workload-appropriate resources and probes; require owner/expiry for exceptions; distinguish local fixture results from production kernel/CNI behavior. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** A broad exception has no expiry. **Correction:** Add workload-appropriate resources and probes; require owner/expiry for exceptions; distinguish local fixture results from production kernel/CNI behavior. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** A local `kind` test is claimed as managed-cluster proof. **Correction:** Add workload-appropriate resources and probes; require owner/expiry for exceptions; distinguish local fixture results from production kernel/CNI behavior. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Versioned conformance evidence and an open-gap record for unsupported platform behavior. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U07-Q13 — Incident / response scenario

- **ID:** `U07-Q13`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Incident / response scenario
- **Level:** L4
- **Objective tested:** Apply a safe ordered response, preserve evidence and distinguish confirmed facts from hypotheses.
- **Estimated time:** 12 minutes

**Question / scenario**

an inference pod runs as root, mounts a writable root filesystem, retains a service-account token and has broad egress. Provide the response in this order: symptom → first action → contain → scope → eradicate → recover → verify → prevent.

**Model answer and reasoning**

1. **Symptom:** record the observed signal and confidence; do not assume root cause.
2. **First action:** preserve relevant logs, event records, deployment digest, identity/audit trail and timestamps; open an incident record and establish an authorized owner.
3. **Contain:** apply the least disruptive safe isolation or gate appropriate to the exposure; preserve evidence before destructive replacement where feasible.
4. **Scope:** identify affected digests, identities, workloads, data paths, trust relationships and time window.
5. **Eradicate:** remove the root cause, revoke/rotate credentials when indicated, rebuild from a trusted source and remove unsafe artifacts or policy gaps.
6. **Recover:** restore only verified artifacts/configuration and communicate service impact.
7. **Verify:** rerun safe positive/negative tests, check old credentials or untrusted artifacts are rejected where relevant, and confirm telemetry/availability.
8. **Prevent:** add a regression test, owner, expiry/review date, alert or runbook update and post-incident follow-up.

**Common wrong answers / approaches**

Immediately deleting the workload before preserving evidence; rotating credentials without inventorying downstream consumers; testing discovered third-party credentials; declaring root cause before scoping; closing the incident because service recovered.

**Evidence / verification expected**

Timeline, preserved evidence references, containment decision, affected-scope list, remediation change, recovery checks, regression test and post-incident action owner.

**Source / verification note**

Follow M10 incident-management foundations. Use only learner-owned lab resources and dummy credentials; exact platform response commands are `[VERIFY]`.

---

### U07-Q14 — Design question with scoring rubric

- **ID:** `U07-Q14`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Design question with scoring rubric
- **Level:** L3
- **Objective tested:** Produce a threat-driven design with measurable controls, safe rollout and explicit residual risk.
- **Estimated time:** 15 minutes

**Question / scenario**

Define a hardened runtime baseline and safe conformance tests for inference, ETL and notebook workloads, including compatibility exceptions and platform evidence.

**Model answer and reasoning**

A strong design begins with the protected assets and trust boundaries; states the intended threat reduction; assigns each control to a stage; records ownership and evidence; includes positive and negative tests; defines freshness, exception and failure behavior; and distinguishes local lab evidence from production guarantees. For this unit, prioritize: runtime hardening reduces available privilege and reachable paths but does not prove application safety or replace supply-chain controls. Include a traceability row for every high-priority threat and a residual-risk decision for each gap.

**Scoring rubric (10 points)**

- Threat/assets and trust boundaries (2)
- Correct control selection and explicit assumptions (2)
- Positive/negative tests and evidence quality (2)
- Operational ownership, exceptions and failure handling (2)
- Residual risk, limitations and review cadence (2)

**Weak (0–3):** lists tools, no trust boundary or evidence. **Adequate (4–7):** correct controls and basic tests, but incomplete ownership or residual risk. **Excellent (8–10):** threat-mapped controls, versioned evidence, safe rollout, failure tests, clear owners, measurable outcomes and candid open gaps.

**Common wrong answers / approaches**

Choosing tools before threats; designing only the happy path; ignoring service availability; treating a local test as universal; leaving exceptions unowned or indefinite.

**Evidence / verification expected**

Architecture/flow diagram, control matrix, test plan, sample evidence bundle, exception record and a list of `[VERIFY]` items.

**Source / verification note**

Use the supplied M12 unit scope; exact product-specific API details must be verified against versioned official documentation.

---

### U07-Q15 — Synthesis / troubleshooting

- **ID:** `U07-Q15`
- **Unit / scope:** Unit 7 — Runtime security and container hardening
- **Type:** Synthesis / troubleshooting
- **Level:** L4
- **Objective tested:** Distinguish control existence from effectiveness and plan evidence-driven diagnosis.
- **Estimated time:** 10 minutes

**Question / scenario**

A pod passes static policy but a connectivity test reaches a forbidden endpoint. Explain which control assumption failed and how to localize it.

**Model answer and reasoning**

The claim is incomplete until the team demonstrates the model’s elements and their relationships, not merely category labels. Inspect actual coverage, trust boundaries, assumptions, test evidence, ownership, residual risk and review cadence. Choose one missing or weak path, construct a benign synthetic fixture, predict expected behavior, run the check in the learner-owned environment, preserve the output and update the traceability record. Mark any platform-specific claim `[VERIFY]` until confirmed.

**Common wrong answers / approaches**

Counting labels as coverage; relying on a single happy-path test; inventing a score threshold; omitting evidence freshness; suppressing the issue instead of closing the gap.

**Evidence / verification expected**

A concise diagnosis with hypothesis, distinguishing evidence, safe test, expected outcome, result status (`PASS`, `FAIL`, `NOT RUN` or `OPEN`) and follow-up owner.

**Source / verification note**

The question tests source-syllabus principles. Any unprovided platform-specific detail remains `[VERIFY]`.

---

## Unit 8 — Admission controls and deployment policy enforcement

**Source unit file:** `08-admission-controls-and-deployment-policy-enforcement.md`

**Coverage focus:** admission-time versus build-time/runtime controls; fail-open/fail-closed and availability/blast radius; ValidatingAdmissionPolicy, Kyverno and Gatekeeper/OPA; API versions and syntax verified or [VERIFY]; registry allow-list, digest pinning, signatures/attestations, privileged settings, initContainers, workload kinds and update paths; bypasses: unanchored registry regex, only containers checked, broad label opt-out, absent/null bugs, UPDATE gaps, Pod-only matching, always-pass defects; audit/warn/deny staged rollout, policy reports, test coverage, engine upgrade rehearsal, webhook HA and failure policy; exceptions-as-code, expiry enforcement, RBAC and policy engines as privileged infrastructure; Kyverno and Gatekeeper are tested in separate clusters/environments; negative fixtures and mutation/correctness-trap tests.

### U08-Q01 — Conceptual short answer

- **ID:** `U08-Q01`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Explain the core principle: an admission policy is effective only when its scope, logic, failure mode and test evidence cover the resources and update paths that matter. Why is this control or reasoning step necessary before a team makes a production decision?

**Model answer and reasoning**

The key principle is that a control claim must be bounded by its scope, trust assumptions and evidence. In this unit, an admission policy is effective only when its scope, logic, failure mode and test evidence cover the resources and update paths that matter. Start from the asset/workload and the failure or threat being controlled, then state the evidence that would demonstrate the intended behavior. State residual risk rather than turning one signal into a universal guarantee.

**Common wrong answers / approaches**

Treating a tool, manifest or document as proof by itself; using a score or label without assumptions; omitting the failure mode or residual risk.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U08-Q02 — Conceptual short answer

- **ID:** `U08-Q02`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Name three distinct failure modes relevant to admission controls and deployment policy enforcement and explain how you would distinguish them during review.

**Model answer and reasoning**

Use at least three categories: (1) design gap—control intent or scope is incomplete; (2) implementation/coverage gap—the configuration does not enforce the intended rule across relevant paths; (3) evidence/operations gap—the control may exist but freshness, health, ownership or actual behavior is not demonstrated. Distinguish them with architecture review, positive and negative tests, and versioned evidence.

**Common wrong answers / approaches**

Calling every failure a tooling bug; assuming configuration presence proves runtime behavior; assuming an absent alert means no event occurred.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U08-Q03 — Conceptual short answer

- **ID:** `U08-Q03`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Conceptual short answer
- **Level:** L2
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

How should this unit hand off to the earlier M01–M11 foundations without re-teaching them?

**Model answer and reasoning**

Reuse prior mechanics only as prerequisites: container basics and scanning/SBOM foundations (M01), CI/CD and OIDC concepts (M02), Kubernetes controls (M03–M04), packaging/GitOps (M06/M08), identity/secrets (M09), incident practices (M10) and observability (M11). This unit adds the security-specific trust model, evidence requirements, negative tests, governance and operational trade-offs. Record the exact prerequisite artifact or evidence instead of assuming mastery.

**Common wrong answers / approaches**

Rebuilding every earlier module; treating a prior lab success as production proof; assuming the learner knows a version-specific API not included in the source syllabus.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U08-Q04 — Multiple choice (exactly four options)

- **ID:** `U08-Q04`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Multiple choice (exactly four options)
- **Level:** L1
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Why stage admission enforcement from audit/warn toward deny?

A. It exposes false positives and scope gaps before the control becomes a deployment availability dependency.
B. Audit mode proves every future denial will be correct.
C. Deny mode should always be avoided.
D. A policy engine automatically verifies signatures without an explicit rule or configuration.

**Model answer and reasoning**

**Correct answer: A.** It exposes false positives and scope gaps before the control becomes a deployment availability dependency. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** It exposes false positives and scope gaps before the control becomes a deployment availability dependency.
- **B — Incorrect/tempting:** Audit mode proves every future denial will be correct. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Deny mode should always be avoided. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A policy engine automatically verifies signatures without an explicit rule or configuration. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to admission controls and deployment policy enforcement.

**Source / verification note**

an admission policy is effective only when its scope, logic, failure mode and test evidence cover the resources and update paths that matter Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U08-Q05 — Multiple choice (exactly four options)

- **ID:** `U08-Q05`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which evidence is strongest when evaluating the main control in admission controls and deployment policy enforcement?

A. A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
B. A screenshot showing a configuration file exists.
C. A statement that the control is industry standard.
D. A successful test on a different platform with no recorded assumptions.

**Model answer and reasoning**

**Correct answer: A.** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
- **B — Incorrect/tempting:** A screenshot showing a configuration file exists. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A statement that the control is industry standard. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A successful test on a different platform with no recorded assumptions. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to admission controls and deployment policy enforcement.

**Source / verification note**

an admission policy is effective only when its scope, logic, failure mode and test evidence cover the resources and update paths that matter Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U08-Q06 — Multiple choice (exactly four options)

- **ID:** `U08-Q06`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

A team reports success for admission controls and deployment policy enforcement but has not tested a failure case. What is the best review response?

A. Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
B. Accept the claim because the happy path passed.
C. Disable the control until every possible edge case is known.
D. Replace evidence with a numerical maturity score.

**Model answer and reasoning**

**Correct answer: A.** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
- **B — Incorrect/tempting:** Accept the claim because the happy path passed. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Disable the control until every possible edge case is known. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Replace evidence with a numerical maturity score. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to admission controls and deployment policy enforcement.

**Source / verification note**

an admission policy is effective only when its scope, logic, failure mode and test evidence cover the resources and update paths that matter Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U08-Q07 — Artifact interpretation

- **ID:** `U08-Q07`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC PSEUDOCODE — NOT VALID CONFIGURATION] Policy checks `spec.containers` but not `spec.initContainers`; fixture has approved main image and unapproved init image.
```

**Model answer and reasoning**

The policy misses an execution-bearing container field. Extend coverage for all relevant container lists and workload templates, then add a fixture that must be denied. Treat exact API fields as version/schema-sensitive. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U08-Q08 — Artifact interpretation

- **ID:** `U08-Q08`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Policy exception: any workload with label `security-exempt=true` is allowed; any namespace user can set labels.
```

**Model answer and reasoning**

The exception is user-controlled and defeats the control. Restrict exception creation through RBAC and a reviewed exception object with owner, scope, expiry and audit trail; test unauthorized label use. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U08-Q09 — Artifact interpretation

- **ID:** `U08-Q09`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Policy unit tests cover CREATE only; production changes use UPDATE; engine webhook failure mode not recorded.
```

**Model answer and reasoning**

Add update and mutation/correctness-trap tests and explicitly decide fail-open/fail-closed based on risk and availability. Verify webhook behavior under outage before enforcing. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U08-Q10 — Configuration / artifact review

- **ID:** `U08-Q10`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Configuration / artifact review
- **Level:** L2
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Scope and bypass review.** Only `containers` are inspected, initContainers are omitted, and a broad user-settable label bypasses the rule. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** Only `containers` are inspected. **Correction:** Evaluate all relevant container lists and resource kinds; restrict exception authority to governed identities; test create and update paths. Otherwise the same trust boundary can be bypassed through unexamined fields or labels. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** InitContainers are omitted. **Correction:** Evaluate all relevant container lists and resource kinds; restrict exception authority to governed identities; test create and update paths. Otherwise the same trust boundary can be bypassed through unexamined fields or labels. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** A broad user-settable label bypasses the rule. **Correction:** Evaluate all relevant container lists and resource kinds; restrict exception authority to governed identities; test create and update paths. Otherwise the same trust boundary can be bypassed through unexamined fields or labels. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Negative fixtures for initContainer, update and unauthorized exemption. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U08-Q11 — Configuration / artifact review

- **ID:** `U08-Q11`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Registry and digest review.** The registry matcher is unanchored, tags are accepted, and the policy only covers Pod resources. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The registry matcher is unanchored. **Correction:** Use a well-defined registry allow-list, require digest pinning where intended and cover controllers/templates plus actual Pods as appropriate. Verify engine-specific matching semantics before production rollout. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Tags are accepted. **Correction:** Use a well-defined registry allow-list, require digest pinning where intended and cover controllers/templates plus actual Pods as appropriate. Verify engine-specific matching semantics before production rollout. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** The policy only covers Pod resources. **Correction:** Use a well-defined registry allow-list, require digest pinning where intended and cover controllers/templates plus actual Pods as appropriate. Verify engine-specific matching semantics before production rollout. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Tests for lookalike registry, tag-only image and each supported workload kind. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U08-Q12 — Configuration / artifact review

- **ID:** `U08-Q12`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Rollout and availability review.** The policy starts in deny mode, webhook failure behavior is unknown, and there is no engine-upgrade rehearsal. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The policy starts in deny mode. **Correction:** Begin with audit/warn or equivalent observation, measure false positives, stage enforcement, test outage/failure policy and maintain rollback/exception controls. A first-day deny can block critical deployments. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Webhook failure behavior is unknown. **Correction:** Begin with audit/warn or equivalent observation, measure false positives, stage enforcement, test outage/failure policy and maintain rollback/exception controls. A first-day deny can block critical deployments. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** There is no engine-upgrade rehearsal. **Correction:** Begin with audit/warn or equivalent observation, measure false positives, stage enforcement, test outage/failure policy and maintain rollback/exception controls. A first-day deny can block critical deployments. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Rollout evidence, failure-mode test and reviewed rollback plan. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U08-Q13 — Incident / response scenario

- **ID:** `U08-Q13`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Incident / response scenario
- **Level:** L4
- **Objective tested:** Apply a safe ordered response, preserve evidence and distinguish confirmed facts from hypotheses.
- **Estimated time:** 12 minutes

**Question / scenario**

a policy blocks ordinary containers but a deployment can still introduce an unapproved init container or use a broad opt-out label. Provide the response in this order: symptom → first action → contain → scope → eradicate → recover → verify → prevent.

**Model answer and reasoning**

1. **Symptom:** record the observed signal and confidence; do not assume root cause.
2. **First action:** preserve relevant logs, event records, deployment digest, identity/audit trail and timestamps; open an incident record and establish an authorized owner.
3. **Contain:** apply the least disruptive safe isolation or gate appropriate to the exposure; preserve evidence before destructive replacement where feasible.
4. **Scope:** identify affected digests, identities, workloads, data paths, trust relationships and time window.
5. **Eradicate:** remove the root cause, revoke/rotate credentials when indicated, rebuild from a trusted source and remove unsafe artifacts or policy gaps.
6. **Recover:** restore only verified artifacts/configuration and communicate service impact.
7. **Verify:** rerun safe positive/negative tests, check old credentials or untrusted artifacts are rejected where relevant, and confirm telemetry/availability.
8. **Prevent:** add a regression test, owner, expiry/review date, alert or runbook update and post-incident follow-up.

**Common wrong answers / approaches**

Immediately deleting the workload before preserving evidence; rotating credentials without inventorying downstream consumers; testing discovered third-party credentials; declaring root cause before scoping; closing the incident because service recovered.

**Evidence / verification expected**

Timeline, preserved evidence references, containment decision, affected-scope list, remediation change, recovery checks, regression test and post-incident action owner.

**Source / verification note**

Follow M10 incident-management foundations. Use only learner-owned lab resources and dummy credentials; exact platform response commands are `[VERIFY]`.

---

### U08-Q14 — Design question with scoring rubric

- **ID:** `U08-Q14`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Design question with scoring rubric
- **Level:** L3
- **Objective tested:** Produce a threat-driven design with measurable controls, safe rollout and explicit residual risk.
- **Estimated time:** 15 minutes

**Question / scenario**

Design an admission architecture and rollout for digest pinning, approved registry, signer/attestation checks and runtime hardening, with separate Kyverno/Gatekeeper environments.

**Model answer and reasoning**

A strong design begins with the protected assets and trust boundaries; states the intended threat reduction; assigns each control to a stage; records ownership and evidence; includes positive and negative tests; defines freshness, exception and failure behavior; and distinguishes local lab evidence from production guarantees. For this unit, prioritize: an admission policy is effective only when its scope, logic, failure mode and test evidence cover the resources and update paths that matter. Include a traceability row for every high-priority threat and a residual-risk decision for each gap.

**Scoring rubric (10 points)**

- Threat/assets and trust boundaries (2)
- Correct control selection and explicit assumptions (2)
- Positive/negative tests and evidence quality (2)
- Operational ownership, exceptions and failure handling (2)
- Residual risk, limitations and review cadence (2)

**Weak (0–3):** lists tools, no trust boundary or evidence. **Adequate (4–7):** correct controls and basic tests, but incomplete ownership or residual risk. **Excellent (8–10):** threat-mapped controls, versioned evidence, safe rollout, failure tests, clear owners, measurable outcomes and candid open gaps.

**Common wrong answers / approaches**

Choosing tools before threats; designing only the happy path; ignoring service availability; treating a local test as universal; leaving exceptions unowned or indefinite.

**Evidence / verification expected**

Architecture/flow diagram, control matrix, test plan, sample evidence bundle, exception record and a list of `[VERIFY]` items.

**Source / verification note**

Use the supplied M12 unit scope; exact product-specific API details must be verified against versioned official documentation.

---

### U08-Q15 — Synthesis / troubleshooting

- **ID:** `U08-Q15`
- **Unit / scope:** Unit 8 — Admission controls and deployment policy enforcement
- **Type:** Synthesis / troubleshooting
- **Level:** L4
- **Objective tested:** Distinguish control existence from effectiveness and plan evidence-driven diagnosis.
- **Estimated time:** 10 minutes

**Question / scenario**

A policy test suite passes but a real controller update bypasses the intended rule. Identify the missing coverage and safe response.

**Model answer and reasoning**

The claim is incomplete until the team demonstrates the model’s elements and their relationships, not merely category labels. Inspect actual coverage, trust boundaries, assumptions, test evidence, ownership, residual risk and review cadence. Choose one missing or weak path, construct a benign synthetic fixture, predict expected behavior, run the check in the learner-owned environment, preserve the output and update the traceability record. Mark any platform-specific claim `[VERIFY]` until confirmed.

**Common wrong answers / approaches**

Counting labels as coverage; relying on a single happy-path test; inventing a score threshold; omitting evidence freshness; suppressing the issue instead of closing the gap.

**Evidence / verification expected**

A concise diagnosis with hypothesis, distinguishing evidence, safe test, expected outcome, result status (`PASS`, `FAIL`, `NOT RUN` or `OPEN`) and follow-up owner.

**Source / verification note**

The question tests source-syllabus principles. Any unprovided platform-specific detail remains `[VERIFY]`.

---

## Unit 9 — Security auditing and vulnerability remediation workflows

**Source unit file:** `09-security-auditing-and-vulnerability-remediation-workflows.md`

**Coverage focus:** finding normalization, lifecycle states, triage, ownership, remediation SLAs and risk-based prioritization; re-scan-verified closure, evidence quality, expiring exceptions, VEX and justified not-affected claims; scheduled scans, freshness, coverage of running digests, time-to-remediate, SLA breaches, exception age and audit trails; KEV/EPSS freshness and contextual use; synthetic advisory “are we affected?” drill; dashboards, Goodhart resistance and zero-finding metric pitfalls; mock audit, evidence retention, access control, privacy and reporting; stale database, unreviewed ignore, no owner, exception abuse and gate disabled due to noise.

### U09-Q01 — Conceptual short answer

- **ID:** `U09-Q01`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Explain the core principle: a finding is closed only when remediation or a justified disposition is supported by fresh evidence for the relevant artifact and deployment. Why is this control or reasoning step necessary before a team makes a production decision?

**Model answer and reasoning**

The key principle is that a control claim must be bounded by its scope, trust assumptions and evidence. In this unit, a finding is closed only when remediation or a justified disposition is supported by fresh evidence for the relevant artifact and deployment. Start from the asset/workload and the failure or threat being controlled, then state the evidence that would demonstrate the intended behavior. State residual risk rather than turning one signal into a universal guarantee.

**Common wrong answers / approaches**

Treating a tool, manifest or document as proof by itself; using a score or label without assumptions; omitting the failure mode or residual risk.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U09-Q02 — Conceptual short answer

- **ID:** `U09-Q02`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Name three distinct failure modes relevant to security auditing and vulnerability remediation workflows and explain how you would distinguish them during review.

**Model answer and reasoning**

Use at least three categories: (1) design gap—control intent or scope is incomplete; (2) implementation/coverage gap—the configuration does not enforce the intended rule across relevant paths; (3) evidence/operations gap—the control may exist but freshness, health, ownership or actual behavior is not demonstrated. Distinguish them with architecture review, positive and negative tests, and versioned evidence.

**Common wrong answers / approaches**

Calling every failure a tooling bug; assuming configuration presence proves runtime behavior; assuming an absent alert means no event occurred.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U09-Q03 — Conceptual short answer

- **ID:** `U09-Q03`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Conceptual short answer
- **Level:** L2
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

How should this unit hand off to the earlier M01–M11 foundations without re-teaching them?

**Model answer and reasoning**

Reuse prior mechanics only as prerequisites: container basics and scanning/SBOM foundations (M01), CI/CD and OIDC concepts (M02), Kubernetes controls (M03–M04), packaging/GitOps (M06/M08), identity/secrets (M09), incident practices (M10) and observability (M11). This unit adds the security-specific trust model, evidence requirements, negative tests, governance and operational trade-offs. Record the exact prerequisite artifact or evidence instead of assuming mastery.

**Common wrong answers / approaches**

Rebuilding every earlier module; treating a prior lab success as production proof; assuming the learner knows a version-specific API not included in the source syllabus.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U09-Q04 — Multiple choice (exactly four options)

- **ID:** `U09-Q04`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Multiple choice (exactly four options)
- **Level:** L1
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

What is the strongest closure criterion for a fixed image vulnerability?

A. A fresh verification tied to the affected digest or evidence that the digest is no longer deployed, with an auditable disposition.
B. A developer comment says the patch was merged.
C. The total dashboard count decreased.
D. The exception was copied into a new file.

**Model answer and reasoning**

**Correct answer: A.** A fresh verification tied to the affected digest or evidence that the digest is no longer deployed, with an auditable disposition. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A fresh verification tied to the affected digest or evidence that the digest is no longer deployed, with an auditable disposition.
- **B — Incorrect/tempting:** A developer comment says the patch was merged. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** The total dashboard count decreased. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** The exception was copied into a new file. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to security auditing and vulnerability remediation workflows.

**Source / verification note**

a finding is closed only when remediation or a justified disposition is supported by fresh evidence for the relevant artifact and deployment Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U09-Q05 — Multiple choice (exactly four options)

- **ID:** `U09-Q05`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which evidence is strongest when evaluating the main control in security auditing and vulnerability remediation workflows?

A. A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
B. A screenshot showing a configuration file exists.
C. A statement that the control is industry standard.
D. A successful test on a different platform with no recorded assumptions.

**Model answer and reasoning**

**Correct answer: A.** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
- **B — Incorrect/tempting:** A screenshot showing a configuration file exists. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A statement that the control is industry standard. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A successful test on a different platform with no recorded assumptions. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to security auditing and vulnerability remediation workflows.

**Source / verification note**

a finding is closed only when remediation or a justified disposition is supported by fresh evidence for the relevant artifact and deployment Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U09-Q06 — Multiple choice (exactly four options)

- **ID:** `U09-Q06`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

A team reports success for security auditing and vulnerability remediation workflows but has not tested a failure case. What is the best review response?

A. Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
B. Accept the claim because the happy path passed.
C. Disable the control until every possible edge case is known.
D. Replace evidence with a numerical maturity score.

**Model answer and reasoning**

**Correct answer: A.** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
- **B — Incorrect/tempting:** Accept the claim because the happy path passed. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Disable the control until every possible edge case is known. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Replace evidence with a numerical maturity score. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to security auditing and vulnerability remediation workflows.

**Source / verification note**

a finding is closed only when remediation or a justified disposition is supported by fresh evidence for the relevant artifact and deployment Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U09-Q07 — Artifact interpretation

- **ID:** `U09-Q07`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] KPI: findings fell from 800 to 90 after policy `ignore all unfixed`; scan coverage fell from 98% to 22%.
```

**Model answer and reasoning**

The improvement is not credible without coverage and policy context. Restore meaningful coverage, inspect ignore changes, compare comparable scans and report unresolved risk honestly. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U09-Q08 — Artifact interpretation

- **ID:** `U09-Q08`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Closure evidence: ticket marked done; new image digest differs from deployed digest; old digest remains in cluster inventory.
```

**Model answer and reasoning**

Do not close based on a different build. Verify the deployed digest was replaced or rescan it; link rollout and cluster evidence and retain an auditable transition. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U09-Q09 — Artifact interpretation

- **ID:** `U09-Q09`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Advisory review: KEV status checked 90 days ago; EPSS snapshot has no timestamp; no owner is assigned.
```

**Model answer and reasoning**

Refresh time-sensitive sources and record retrieval time; assign an owner and prioritize based on current evidence plus exposure and criticality, not a stale score alone. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U09-Q10 — Configuration / artifact review

- **ID:** `U09-Q10`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Configuration / artifact review
- **Level:** L2
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Lifecycle review.** Closure evidence is for a different digest, the owner is blank, and no remediation evidence is linked. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** Closure evidence is for a different digest. **Correction:** Reopen or mark closure unverified; rescan the exact affected digest or prove the old digest is no longer deployed; assign owner and link change/test evidence. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** The owner is blank. **Correction:** Reopen or mark closure unverified; rescan the exact affected digest or prove the old digest is no longer deployed; assign owner and link change/test evidence. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** No remediation evidence is linked. **Correction:** Reopen or mark closure unverified; rescan the exact affected digest or prove the old digest is no longer deployed; assign owner and link change/test evidence. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Lifecycle transition audit trail and exact-digest rescan. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U09-Q11 — Configuration / artifact review

- **ID:** `U09-Q11`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Exception governance review.** The ignore has no expiry, approver is missing, and its justification says only “noise.” Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The ignore has no expiry. **Correction:** Require evidence-based rationale, scoped affected versions, compensating controls, approver, expiry and re-review; reject blanket suppression. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Approver is missing. **Correction:** Require evidence-based rationale, scoped affected versions, compensating controls, approver, expiry and re-review; reject blanket suppression. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Its justification says only “noise.”. **Correction:** Require evidence-based rationale, scoped affected versions, compensating controls, approver, expiry and re-review; reject blanket suppression. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Exception report with overdue items and an enforced expiry test. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U09-Q12 — Configuration / artifact review

- **ID:** `U09-Q12`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Audit dashboard review.** The dashboard reports only total finding count, omits database freshness and running-digest coverage, and exposes sensitive detail to all users. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The dashboard reports only total finding count. **Correction:** Add freshness, coverage, age/SLA, exception and exposure-window measures; restrict sensitive detail; provide aggregated views to broader audiences. Raw count alone can be gamed. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Omits database freshness and running-digest coverage. **Correction:** Add freshness, coverage, age/SLA, exception and exposure-window measures; restrict sensitive detail; provide aggregated views to broader audiences. Raw count alone can be gamed. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Exposes sensitive detail to all users. **Correction:** Add freshness, coverage, age/SLA, exception and exposure-window measures; restrict sensitive detail; provide aggregated views to broader audiences. Raw count alone can be gamed. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Reconciled dashboard against source findings and access review. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U09-Q13 — Incident / response scenario

- **ID:** `U09-Q13`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Incident / response scenario
- **Level:** L4
- **Objective tested:** Apply a safe ordered response, preserve evidence and distinguish confirmed facts from hypotheses.
- **Estimated time:** 12 minutes

**Question / scenario**

an auditor asks why a critical finding was closed while the production digest still appears in the cluster inventory. Provide the response in this order: symptom → first action → contain → scope → eradicate → recover → verify → prevent.

**Model answer and reasoning**

1. **Symptom:** record the observed signal and confidence; do not assume root cause.
2. **First action:** preserve relevant logs, event records, deployment digest, identity/audit trail and timestamps; open an incident record and establish an authorized owner.
3. **Contain:** apply the least disruptive safe isolation or gate appropriate to the exposure; preserve evidence before destructive replacement where feasible.
4. **Scope:** identify affected digests, identities, workloads, data paths, trust relationships and time window.
5. **Eradicate:** remove the root cause, revoke/rotate credentials when indicated, rebuild from a trusted source and remove unsafe artifacts or policy gaps.
6. **Recover:** restore only verified artifacts/configuration and communicate service impact.
7. **Verify:** rerun safe positive/negative tests, check old credentials or untrusted artifacts are rejected where relevant, and confirm telemetry/availability.
8. **Prevent:** add a regression test, owner, expiry/review date, alert or runbook update and post-incident follow-up.

**Common wrong answers / approaches**

Immediately deleting the workload before preserving evidence; rotating credentials without inventorying downstream consumers; testing discovered third-party credentials; declaring root cause before scoping; closing the incident because service recovered.

**Evidence / verification expected**

Timeline, preserved evidence references, containment decision, affected-scope list, remediation change, recovery checks, regression test and post-incident action owner.

**Source / verification note**

Follow M10 incident-management foundations. Use only learner-owned lab resources and dummy credentials; exact platform response commands are `[VERIFY]`.

---

### U09-Q14 — Design question with scoring rubric

- **ID:** `U09-Q14`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Design question with scoring rubric
- **Level:** L3
- **Objective tested:** Produce a threat-driven design with measurable controls, safe rollout and explicit residual risk.
- **Estimated time:** 15 minutes

**Question / scenario**

Design a finding lifecycle, remediation SLA and audit-evidence workflow that tracks exact digests, freshness, exceptions, ownership, closure and privacy.

**Model answer and reasoning**

A strong design begins with the protected assets and trust boundaries; states the intended threat reduction; assigns each control to a stage; records ownership and evidence; includes positive and negative tests; defines freshness, exception and failure behavior; and distinguishes local lab evidence from production guarantees. For this unit, prioritize: a finding is closed only when remediation or a justified disposition is supported by fresh evidence for the relevant artifact and deployment. Include a traceability row for every high-priority threat and a residual-risk decision for each gap.

**Scoring rubric (10 points)**

- Threat/assets and trust boundaries (2)
- Correct control selection and explicit assumptions (2)
- Positive/negative tests and evidence quality (2)
- Operational ownership, exceptions and failure handling (2)
- Residual risk, limitations and review cadence (2)

**Weak (0–3):** lists tools, no trust boundary or evidence. **Adequate (4–7):** correct controls and basic tests, but incomplete ownership or residual risk. **Excellent (8–10):** threat-mapped controls, versioned evidence, safe rollout, failure tests, clear owners, measurable outcomes and candid open gaps.

**Common wrong answers / approaches**

Choosing tools before threats; designing only the happy path; ignoring service availability; treating a local test as universal; leaving exceptions unowned or indefinite.

**Evidence / verification expected**

Architecture/flow diagram, control matrix, test plan, sample evidence bundle, exception record and a list of `[VERIFY]` items.

**Source / verification note**

Use the supplied M12 unit scope; exact product-specific API details must be verified against versioned official documentation.

---

### U09-Q15 — Synthesis / troubleshooting

- **ID:** `U09-Q15`
- **Unit / scope:** Unit 9 — Security auditing and vulnerability remediation workflows
- **Type:** Synthesis / troubleshooting
- **Level:** L4
- **Objective tested:** Distinguish control existence from effectiveness and plan evidence-driven diagnosis.
- **Estimated time:** 10 minutes

**Question / scenario**

A team meets its remediation SLA by closing findings at merge time. Production deployment evidence often arrives days later. Redesign the metric and workflow.

**Model answer and reasoning**

The claim is incomplete until the team demonstrates the model’s elements and their relationships, not merely category labels. Inspect actual coverage, trust boundaries, assumptions, test evidence, ownership, residual risk and review cadence. Choose one missing or weak path, construct a benign synthetic fixture, predict expected behavior, run the check in the learner-owned environment, preserve the output and update the traceability record. Mark any platform-specific claim `[VERIFY]` until confirmed.

**Common wrong answers / approaches**

Counting labels as coverage; relying on a single happy-path test; inventing a score threshold; omitting evidence freshness; suppressing the issue instead of closing the gap.

**Evidence / verification expected**

A concise diagnosis with hypothesis, distinguishing evidence, safe test, expected outcome, result status (`PASS`, `FAIL`, `NOT RUN` or `OPEN`) and follow-up owner.

**Source / verification note**

The question tests source-syllabus principles. Any unprovided platform-specific detail remains `[VERIFY]`.

---

## Unit 10 — SLSA framework and build provenance levels

**Source unit file:** `10-slsa-framework-and-build-provenance-levels.md`

**Coverage focus:** supply-chain integrity and threat categories grounded in verified source spec; avoid memorized/outdated level definitions; provenance purpose, subject digest, builder identity, source reference, build type, external parameters and supported schema fields; verified spec version/track and requirements; map requirement to threat/control using verified notes; trusted-builder simulation, forged-provenance negative test, admission-time verification and reproducible-rebuild comparison; why provenance existence does not prove authentic/trustworthy provenance; no SLSA level claim unless every applicable requirement is evidenced; local simulation versus hosted trusted-builder guarantees.

### U10-Q01 — Conceptual short answer

- **ID:** `U10-Q01`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Explain the core principle: provenance is useful only when its authenticity, subject and claims are verified against an explicit policy; a level claim requires evidence for every applicable requirement. Why is this control or reasoning step necessary before a team makes a production decision?

**Model answer and reasoning**

The key principle is that a control claim must be bounded by its scope, trust assumptions and evidence. In this unit, provenance is useful only when its authenticity, subject and claims are verified against an explicit policy; a level claim requires evidence for every applicable requirement. Start from the asset/workload and the failure or threat being controlled, then state the evidence that would demonstrate the intended behavior. State residual risk rather than turning one signal into a universal guarantee.

**Common wrong answers / approaches**

Treating a tool, manifest or document as proof by itself; using a score or label without assumptions; omitting the failure mode or residual risk.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U10-Q02 — Conceptual short answer

- **ID:** `U10-Q02`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Name three distinct failure modes relevant to slsa framework and build provenance levels and explain how you would distinguish them during review.

**Model answer and reasoning**

Use at least three categories: (1) design gap—control intent or scope is incomplete; (2) implementation/coverage gap—the configuration does not enforce the intended rule across relevant paths; (3) evidence/operations gap—the control may exist but freshness, health, ownership or actual behavior is not demonstrated. Distinguish them with architecture review, positive and negative tests, and versioned evidence.

**Common wrong answers / approaches**

Calling every failure a tooling bug; assuming configuration presence proves runtime behavior; assuming an absent alert means no event occurred.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U10-Q03 — Conceptual short answer

- **ID:** `U10-Q03`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Conceptual short answer
- **Level:** L2
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

How should this unit hand off to the earlier M01–M11 foundations without re-teaching them?

**Model answer and reasoning**

Reuse prior mechanics only as prerequisites: container basics and scanning/SBOM foundations (M01), CI/CD and OIDC concepts (M02), Kubernetes controls (M03–M04), packaging/GitOps (M06/M08), identity/secrets (M09), incident practices (M10) and observability (M11). This unit adds the security-specific trust model, evidence requirements, negative tests, governance and operational trade-offs. Record the exact prerequisite artifact or evidence instead of assuming mastery.

**Common wrong answers / approaches**

Rebuilding every earlier module; treating a prior lab success as production proof; assuming the learner knows a version-specific API not included in the source syllabus.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U10-Q04 — Multiple choice (exactly four options)

- **ID:** `U10-Q04`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Multiple choice (exactly four options)
- **Level:** L1
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

What is needed before making a SLSA level claim?

A. Evidence that every applicable requirement for the explicitly selected, verified specification track/version is satisfied.
B. A provenance file exists in the artifact registry.
C. A local script prints `trusted=true`.
D. The image has no scanner findings.

**Model answer and reasoning**

**Correct answer: A.** Evidence that every applicable requirement for the explicitly selected, verified specification track/version is satisfied. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Evidence that every applicable requirement for the explicitly selected, verified specification track/version is satisfied.
- **B — Incorrect/tempting:** A provenance file exists in the artifact registry. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A local script prints `trusted=true`. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** The image has no scanner findings. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to slsa framework and build provenance levels.

**Source / verification note**

provenance is useful only when its authenticity, subject and claims are verified against an explicit policy; a level claim requires evidence for every applicable requirement Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U10-Q05 — Multiple choice (exactly four options)

- **ID:** `U10-Q05`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which evidence is strongest when evaluating the main control in slsa framework and build provenance levels?

A. A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
B. A screenshot showing a configuration file exists.
C. A statement that the control is industry standard.
D. A successful test on a different platform with no recorded assumptions.

**Model answer and reasoning**

**Correct answer: A.** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
- **B — Incorrect/tempting:** A screenshot showing a configuration file exists. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A statement that the control is industry standard. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A successful test on a different platform with no recorded assumptions. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to slsa framework and build provenance levels.

**Source / verification note**

provenance is useful only when its authenticity, subject and claims are verified against an explicit policy; a level claim requires evidence for every applicable requirement Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U10-Q06 — Multiple choice (exactly four options)

- **ID:** `U10-Q06`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

A team reports success for slsa framework and build provenance levels but has not tested a failure case. What is the best review response?

A. Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
B. Accept the claim because the happy path passed.
C. Disable the control until every possible edge case is known.
D. Replace evidence with a numerical maturity score.

**Model answer and reasoning**

**Correct answer: A.** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
- **B — Incorrect/tempting:** Accept the claim because the happy path passed. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Disable the control until every possible edge case is known. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Replace evidence with a numerical maturity score. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to slsa framework and build provenance levels.

**Source / verification note**

provenance is useful only when its authenticity, subject and claims are verified against an explicit policy; a level claim requires evidence for every applicable requirement Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U10-Q07 — Artifact interpretation

- **ID:** `U10-Q07`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Provenance exists and contains a builder string, but no signature, subject digest or authenticated source reference is verified.
```

**Model answer and reasoning**

Presence alone proves only that a document exists. Verify authentic origin, subject digest, builder identity and expected source/ref under a declared policy; otherwise deny or mark evidence insufficient. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U10-Q08 — Artifact interpretation

- **ID:** `U10-Q08`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Compliance table: requirement R1=PASS, R2=PASS, R3=NOT RUN; claimed level=target level.
```

**Model answer and reasoning**

A missing applicable requirement cannot be silently counted as pass. Keep the claim open; verify the current spec track/version and collect evidence for R3 before making any level claim. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U10-Q09 — Artifact interpretation

- **ID:** `U10-Q09`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Rebuild A and B produce different digests; build A used an unrecorded external parameter; build B used a different dependency snapshot.
```

**Model answer and reasoning**

The difference is not enough to infer compromise. Rebuild under controlled inputs, record external parameters and dependency versions, compare artifact contents, and document which reproducibility guarantees are actually intended. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U10-Q10 — Configuration / artifact review

- **ID:** `U10-Q10`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Configuration / artifact review
- **Level:** L2
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Provenance trust review.** The statement is unsigned, the subject does not match the deployed digest, and builder/source claims are not checked against policy. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The statement is unsigned. **Correction:** Authenticate the statement using an established trust model; bind the subject to the exact deployed digest; verify builder and source against approved identities. Treat the claimed level as unsupported until verified requirements are met. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** The subject does not match the deployed digest. **Correction:** Authenticate the statement using an established trust model; bind the subject to the exact deployed digest; verify builder and source against approved identities. Treat the claimed level as unsupported until verified requirements are met. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Builder/source claims are not checked against policy. **Correction:** Authenticate the statement using an established trust model; bind the subject to the exact deployed digest; verify builder and source against approved identities. Treat the claimed level as unsupported until verified requirements are met. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Forged statement and wrong-subject negative tests. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U10-Q11 — Configuration / artifact review

- **ID:** `U10-Q11`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Requirement mapping review.** The team uses a blog summary instead of the selected specification, counts a local simulation as hosted trusted-builder proof, and omits evidence for one requirement. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The team uses a blog summary instead of the selected specification. **Correction:** Record spec track/version and exact requirement text from verified notes; map each requirement to threat, control and evidence; separate local learning evidence from production guarantees. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Counts a local simulation as hosted trusted-builder proof. **Correction:** Record spec track/version and exact requirement text from verified notes; map each requirement to threat, control and evidence; separate local learning evidence from production guarantees. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Omits evidence for one requirement. **Correction:** Record spec track/version and exact requirement text from verified notes; map each requirement to threat, control and evidence; separate local learning evidence from production guarantees. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Requirement-to-evidence matrix with `[VERIFY]` items. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U10-Q12 — Configuration / artifact review

- **ID:** `U10-Q12`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Reproducibility review.** Two builds differ, the team assumes this proves malicious tampering, and external parameters are not recorded. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** Two builds differ. **Correction:** Investigate environment, dependencies, timestamps and declared parameters; record comparison scope and limits. Non-identical builds are a signal for analysis, not automatic proof of compromise. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** The team assumes this proves malicious tampering. **Correction:** Investigate environment, dependencies, timestamps and declared parameters; record comparison scope and limits. Non-identical builds are a signal for analysis, not automatic proof of compromise. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** External parameters are not recorded. **Correction:** Investigate environment, dependencies, timestamps and declared parameters; record comparison scope and limits. Non-identical builds are a signal for analysis, not automatic proof of compromise. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Rebuild comparison report and documented hypotheses. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U10-Q13 — Incident / response scenario

- **ID:** `U10-Q13`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Incident / response scenario
- **Level:** L4
- **Objective tested:** Apply a safe ordered response, preserve evidence and distinguish confirmed facts from hypotheses.
- **Estimated time:** 12 minutes

**Question / scenario**

a release pipeline attaches a provenance JSON file, but no verifier authenticates it and the subject digest differs from the deployed image. Provide the response in this order: symptom → first action → contain → scope → eradicate → recover → verify → prevent.

**Model answer and reasoning**

1. **Symptom:** record the observed signal and confidence; do not assume root cause.
2. **First action:** preserve relevant logs, event records, deployment digest, identity/audit trail and timestamps; open an incident record and establish an authorized owner.
3. **Contain:** apply the least disruptive safe isolation or gate appropriate to the exposure; preserve evidence before destructive replacement where feasible.
4. **Scope:** identify affected digests, identities, workloads, data paths, trust relationships and time window.
5. **Eradicate:** remove the root cause, revoke/rotate credentials when indicated, rebuild from a trusted source and remove unsafe artifacts or policy gaps.
6. **Recover:** restore only verified artifacts/configuration and communicate service impact.
7. **Verify:** rerun safe positive/negative tests, check old credentials or untrusted artifacts are rejected where relevant, and confirm telemetry/availability.
8. **Prevent:** add a regression test, owner, expiry/review date, alert or runbook update and post-incident follow-up.

**Common wrong answers / approaches**

Immediately deleting the workload before preserving evidence; rotating credentials without inventorying downstream consumers; testing discovered third-party credentials; declaring root cause before scoping; closing the incident because service recovered.

**Evidence / verification expected**

Timeline, preserved evidence references, containment decision, affected-scope list, remediation change, recovery checks, regression test and post-incident action owner.

**Source / verification note**

Follow M10 incident-management foundations. Use only learner-owned lab resources and dummy credentials; exact platform response commands are `[VERIFY]`.

---

### U10-Q14 — Design question with scoring rubric

- **ID:** `U10-Q14`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Design question with scoring rubric
- **Level:** L3
- **Objective tested:** Produce a threat-driven design with measurable controls, safe rollout and explicit residual risk.
- **Estimated time:** 15 minutes

**Question / scenario**

Build a provenance adoption plan grounded in verified specification notes, including threat mapping, authenticated statements, subject binding, negative tests and honest gaps.

**Model answer and reasoning**

A strong design begins with the protected assets and trust boundaries; states the intended threat reduction; assigns each control to a stage; records ownership and evidence; includes positive and negative tests; defines freshness, exception and failure behavior; and distinguishes local lab evidence from production guarantees. For this unit, prioritize: provenance is useful only when its authenticity, subject and claims are verified against an explicit policy; a level claim requires evidence for every applicable requirement. Include a traceability row for every high-priority threat and a residual-risk decision for each gap.

**Scoring rubric (10 points)**

- Threat/assets and trust boundaries (2)
- Correct control selection and explicit assumptions (2)
- Positive/negative tests and evidence quality (2)
- Operational ownership, exceptions and failure handling (2)
- Residual risk, limitations and review cadence (2)

**Weak (0–3):** lists tools, no trust boundary or evidence. **Adequate (4–7):** correct controls and basic tests, but incomplete ownership or residual risk. **Excellent (8–10):** threat-mapped controls, versioned evidence, safe rollout, failure tests, clear owners, measurable outcomes and candid open gaps.

**Common wrong answers / approaches**

Choosing tools before threats; designing only the happy path; ignoring service availability; treating a local test as universal; leaving exceptions unowned or indefinite.

**Evidence / verification expected**

Architecture/flow diagram, control matrix, test plan, sample evidence bundle, exception record and a list of `[VERIFY]` items.

**Source / verification note**

Use the supplied M12 unit scope; exact product-specific API details must be verified against versioned official documentation.

---

### U10-Q15 — Synthesis / troubleshooting

- **ID:** `U10-Q15`
- **Unit / scope:** Unit 10 — SLSA framework and build provenance levels
- **Type:** Synthesis / troubleshooting
- **Level:** L4
- **Objective tested:** Distinguish control existence from effectiveness and plan evidence-driven diagnosis.
- **Estimated time:** 10 minutes

**Question / scenario**

A local pipeline produces identical rebuilds twice but uses long-lived credentials and no isolated builder. State what reproducibility supports and what it does not.

**Model answer and reasoning**

The claim is incomplete until the team demonstrates the model’s elements and their relationships, not merely category labels. Inspect actual coverage, trust boundaries, assumptions, test evidence, ownership, residual risk and review cadence. Choose one missing or weak path, construct a benign synthetic fixture, predict expected behavior, run the check in the learner-owned environment, preserve the output and update the traceability record. Mark any platform-specific claim `[VERIFY]` until confirmed.

**Common wrong answers / approaches**

Counting labels as coverage; relying on a single happy-path test; inventing a score threshold; omitting evidence freshness; suppressing the issue instead of closing the gap.

**Evidence / verification expected**

A concise diagnosis with hypothesis, distinguishing evidence, safe test, expected outcome, result status (`PASS`, `FAIL`, `NOT RUN` or `OPEN`) and follow-up owner.

**Source / verification note**

The question tests source-syllabus principles. Any unprovided platform-specific detail remains `[VERIFY]`.

---

## Unit 11 — Kyverno and OPA Gatekeeper policy authoring

**Source unit file:** `11-kyverno-and-opa-gatekeeper-policy-authoring.md`

**Coverage focus:** policy design, scope, matching/exclusions, validate/mutate/generate/verifyImages where supported and version-sensitive; Gatekeeper ConstraintTemplates/Constraints/Rego where supported; separate engine-specific semantics; policy tests, unit fixtures, mutation/correctness traps, exception governance and RBAC; scope across workload kinds, initContainers, updates, missing/null fields, registry matching and policy-engine always-pass defects; separate Kyverno and Gatekeeper clusters/environments; staged rollout, reports, upgrades and rollback; policy engine as privileged infrastructure, admission availability, monitoring and safe failure behavior.

### U11-Q01 — Conceptual short answer

- **ID:** `U11-Q01`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Explain the core principle: policy authoring is a software-engineering discipline: define intent, scope, tests, exceptions, rollout and failure handling separately for each engine. Why is this control or reasoning step necessary before a team makes a production decision?

**Model answer and reasoning**

The key principle is that a control claim must be bounded by its scope, trust assumptions and evidence. In this unit, policy authoring is a software-engineering discipline: define intent, scope, tests, exceptions, rollout and failure handling separately for each engine. Start from the asset/workload and the failure or threat being controlled, then state the evidence that would demonstrate the intended behavior. State residual risk rather than turning one signal into a universal guarantee.

**Common wrong answers / approaches**

Treating a tool, manifest or document as proof by itself; using a score or label without assumptions; omitting the failure mode or residual risk.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U11-Q02 — Conceptual short answer

- **ID:** `U11-Q02`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Name three distinct failure modes relevant to kyverno and opa gatekeeper policy authoring and explain how you would distinguish them during review.

**Model answer and reasoning**

Use at least three categories: (1) design gap—control intent or scope is incomplete; (2) implementation/coverage gap—the configuration does not enforce the intended rule across relevant paths; (3) evidence/operations gap—the control may exist but freshness, health, ownership or actual behavior is not demonstrated. Distinguish them with architecture review, positive and negative tests, and versioned evidence.

**Common wrong answers / approaches**

Calling every failure a tooling bug; assuming configuration presence proves runtime behavior; assuming an absent alert means no event occurred.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U11-Q03 — Conceptual short answer

- **ID:** `U11-Q03`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Conceptual short answer
- **Level:** L2
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

How should this unit hand off to the earlier M01–M11 foundations without re-teaching them?

**Model answer and reasoning**

Reuse prior mechanics only as prerequisites: container basics and scanning/SBOM foundations (M01), CI/CD and OIDC concepts (M02), Kubernetes controls (M03–M04), packaging/GitOps (M06/M08), identity/secrets (M09), incident practices (M10) and observability (M11). This unit adds the security-specific trust model, evidence requirements, negative tests, governance and operational trade-offs. Record the exact prerequisite artifact or evidence instead of assuming mastery.

**Common wrong answers / approaches**

Rebuilding every earlier module; treating a prior lab success as production proof; assuming the learner knows a version-specific API not included in the source syllabus.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U11-Q04 — Multiple choice (exactly four options)

- **ID:** `U11-Q04`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Multiple choice (exactly four options)
- **Level:** L1
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Why should Kyverno and Gatekeeper labs be sequenced in separate environments?

A. Their controllers and policy semantics are distinct; separate environments prevent overlapping admission behavior from obscuring which engine produced a result.
B. They use identical schemas and cannot coexist technically.
C. A separate environment guarantees every policy is correct.
D. Policy testing is unnecessary when both engines are installed.

**Model answer and reasoning**

**Correct answer: A.** Their controllers and policy semantics are distinct; separate environments prevent overlapping admission behavior from obscuring which engine produced a result. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Their controllers and policy semantics are distinct; separate environments prevent overlapping admission behavior from obscuring which engine produced a result.
- **B — Incorrect/tempting:** They use identical schemas and cannot coexist technically. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A separate environment guarantees every policy is correct. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Policy testing is unnecessary when both engines are installed. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to kyverno and opa gatekeeper policy authoring.

**Source / verification note**

policy authoring is a software-engineering discipline: define intent, scope, tests, exceptions, rollout and failure handling separately for each engine Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U11-Q05 — Multiple choice (exactly four options)

- **ID:** `U11-Q05`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which evidence is strongest when evaluating the main control in kyverno and opa gatekeeper policy authoring?

A. A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
B. A screenshot showing a configuration file exists.
C. A statement that the control is industry standard.
D. A successful test on a different platform with no recorded assumptions.

**Model answer and reasoning**

**Correct answer: A.** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
- **B — Incorrect/tempting:** A screenshot showing a configuration file exists. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A statement that the control is industry standard. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A successful test on a different platform with no recorded assumptions. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to kyverno and opa gatekeeper policy authoring.

**Source / verification note**

policy authoring is a software-engineering discipline: define intent, scope, tests, exceptions, rollout and failure handling separately for each engine Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U11-Q06 — Multiple choice (exactly four options)

- **ID:** `U11-Q06`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

A team reports success for kyverno and opa gatekeeper policy authoring but has not tested a failure case. What is the best review response?

A. Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
B. Accept the claim because the happy path passed.
C. Disable the control until every possible edge case is known.
D. Replace evidence with a numerical maturity score.

**Model answer and reasoning**

**Correct answer: A.** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
- **B — Incorrect/tempting:** Accept the claim because the happy path passed. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Disable the control until every possible edge case is known. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Replace evidence with a numerical maturity score. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to kyverno and opa gatekeeper policy authoring.

**Source / verification note**

policy authoring is a software-engineering discipline: define intent, scope, tests, exceptions, rollout and failure handling separately for each engine Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U11-Q07 — Artifact interpretation

- **ID:** `U11-Q07`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Test report: approved image passes; no tests for lookalike registry, absent image field, initContainer or UPDATE.
```

**Model answer and reasoning**

The suite has false confidence due to missing negative/boundary cases. Add fixtures for every bypass class and use the actual engine/version/schema before asserting production behavior. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U11-Q08 — Artifact interpretation

- **ID:** `U11-Q08`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC PSEUDOCODE — NOT VALID CONFIGURATION] `if image is missing then allow` and `if namespace has label exempt then allow`.
```

**Model answer and reasoning**

Missing fields and broad exemptions create fail-open paths. Define explicit behavior for absent values and govern exemptions through RBAC, scope, owner, expiry and audit evidence. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U11-Q09 — Artifact interpretation

- **ID:** `U11-Q09`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Kyverno and Gatekeeper test outputs are combined into one report; engine version and cluster identity are absent.
```

**Model answer and reasoning**

Results cannot be attributed reliably to an engine/environment. Keep separate environments and evidence bundles with engine version, cluster identity, test inputs and outcome. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U11-Q10 — Configuration / artifact review

- **ID:** `U11-Q10`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Configuration / artifact review
- **Level:** L2
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Policy logic review.** The rule checks only main containers, excludes all team-owned namespaces, and treats missing image as allow. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The rule checks only main containers. **Correction:** Cover every relevant image-bearing field and resource kind, restrict exclusions to controlled scopes, and decide missing-field behavior explicitly. Add fixtures for absent/null, init container, sidecar and namespace exclusion. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Excludes all team-owned namespaces. **Correction:** Cover every relevant image-bearing field and resource kind, restrict exclusions to controlled scopes, and decide missing-field behavior explicitly. Add fixtures for absent/null, init container, sidecar and namespace exclusion. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Treats missing image as allow. **Correction:** Cover every relevant image-bearing field and resource kind, restrict exclusions to controlled scopes, and decide missing-field behavior explicitly. Add fixtures for absent/null, init container, sidecar and namespace exclusion. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Corrected artifact, at least three negative fixtures, one legitimate positive fixture, and a regression test for each defect. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U11-Q11 — Configuration / artifact review

- **ID:** `U11-Q11`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Test-quality review.** Only positive fixtures exist, no mutation test changes the matcher, and tests run against a different engine version from the deployment. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** Only positive fixtures exist. **Correction:** Add expected-deny and boundary fixtures, mutation/correctness-trap tests and version-matched engine rehearsal. Passing a single positive example does not demonstrate policy completeness. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** No mutation test changes the matcher. **Correction:** Add expected-deny and boundary fixtures, mutation/correctness-trap tests and version-matched engine rehearsal. Passing a single positive example does not demonstrate policy completeness. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Tests run against a different engine version from the deployment. **Correction:** Add expected-deny and boundary fixtures, mutation/correctness-trap tests and version-matched engine rehearsal. Passing a single positive example does not demonstrate policy completeness. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Corrected artifact, at least three negative fixtures, one legitimate positive fixture, and a regression test for each defect. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U11-Q12 — Configuration / artifact review

- **ID:** `U11-Q12`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Engine governance review.** Kyverno and Gatekeeper are installed together in one lab, engine permissions are broad, and webhook health is not monitored. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** Kyverno and Gatekeeper are installed together in one lab. **Correction:** Test each engine in a separate cluster/environment; reduce controller permissions; monitor availability and policy decisions; rehearse upgrades and failure policy before enforcement. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Engine permissions are broad. **Correction:** Test each engine in a separate cluster/environment; reduce controller permissions; monitor availability and policy decisions; rehearse upgrades and failure policy before enforcement. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Webhook health is not monitored. **Correction:** Test each engine in a separate cluster/environment; reduce controller permissions; monitor availability and policy decisions; rehearse upgrades and failure policy before enforcement. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Corrected artifact, at least three negative fixtures, one legitimate positive fixture, and a regression test for each defect. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U11-Q13 — Incident / response scenario

- **ID:** `U11-Q13`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Incident / response scenario
- **Level:** L4
- **Objective tested:** Apply a safe ordered response, preserve evidence and distinguish confirmed facts from hypotheses.
- **Estimated time:** 12 minutes

**Question / scenario**

a policy appears to require approved registries, but a harmless negative fixture with a lookalike registry is admitted. Provide the response in this order: symptom → first action → contain → scope → eradicate → recover → verify → prevent.

**Model answer and reasoning**

1. **Symptom:** record the observed signal and confidence; do not assume root cause.
2. **First action:** preserve relevant logs, event records, deployment digest, identity/audit trail and timestamps; open an incident record and establish an authorized owner.
3. **Contain:** apply the least disruptive safe isolation or gate appropriate to the exposure; preserve evidence before destructive replacement where feasible.
4. **Scope:** identify affected digests, identities, workloads, data paths, trust relationships and time window.
5. **Eradicate:** remove the root cause, revoke/rotate credentials when indicated, rebuild from a trusted source and remove unsafe artifacts or policy gaps.
6. **Recover:** restore only verified artifacts/configuration and communicate service impact.
7. **Verify:** rerun safe positive/negative tests, check old credentials or untrusted artifacts are rejected where relevant, and confirm telemetry/availability.
8. **Prevent:** add a regression test, owner, expiry/review date, alert or runbook update and post-incident follow-up.

**Common wrong answers / approaches**

Immediately deleting the workload before preserving evidence; rotating credentials without inventorying downstream consumers; testing discovered third-party credentials; declaring root cause before scoping; closing the incident because service recovered.

**Evidence / verification expected**

Timeline, preserved evidence references, containment decision, affected-scope list, remediation change, recovery checks, regression test and post-incident action owner.

**Source / verification note**

Follow M10 incident-management foundations. Use only learner-owned lab resources and dummy credentials; exact platform response commands are `[VERIFY]`.

---

### U11-Q14 — Design question with scoring rubric

- **ID:** `U11-Q14`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Design question with scoring rubric
- **Level:** L3
- **Objective tested:** Produce a threat-driven design with measurable controls, safe rollout and explicit residual risk.
- **Estimated time:** 15 minutes

**Question / scenario**

Design policy lifecycle governance for one selected engine at a time, including scope, tests, exemptions, staged rollout, monitoring, upgrades and rollback.

**Model answer and reasoning**

A strong design begins with the protected assets and trust boundaries; states the intended threat reduction; assigns each control to a stage; records ownership and evidence; includes positive and negative tests; defines freshness, exception and failure behavior; and distinguishes local lab evidence from production guarantees. For this unit, prioritize: policy authoring is a software-engineering discipline: define intent, scope, tests, exceptions, rollout and failure handling separately for each engine. Include a traceability row for every high-priority threat and a residual-risk decision for each gap.

**Scoring rubric (10 points)**

- Threat/assets and trust boundaries (2)
- Correct control selection and explicit assumptions (2)
- Positive/negative tests and evidence quality (2)
- Operational ownership, exceptions and failure handling (2)
- Residual risk, limitations and review cadence (2)

**Weak (0–3):** lists tools, no trust boundary or evidence. **Adequate (4–7):** correct controls and basic tests, but incomplete ownership or residual risk. **Excellent (8–10):** threat-mapped controls, versioned evidence, safe rollout, failure tests, clear owners, measurable outcomes and candid open gaps.

**Common wrong answers / approaches**

Choosing tools before threats; designing only the happy path; ignoring service availability; treating a local test as universal; leaving exceptions unowned or indefinite.

**Evidence / verification expected**

Architecture/flow diagram, control matrix, test plan, sample evidence bundle, exception record and a list of `[VERIFY]` items.

**Source / verification note**

Use the supplied M12 unit scope; exact product-specific API details must be verified against versioned official documentation.

---

### U11-Q15 — Synthesis / troubleshooting

- **ID:** `U11-Q15`
- **Unit / scope:** Unit 11 — Kyverno and OPA Gatekeeper policy authoring
- **Type:** Synthesis / troubleshooting
- **Level:** L4
- **Objective tested:** Distinguish control existence from effectiveness and plan evidence-driven diagnosis.
- **Estimated time:** 10 minutes

**Question / scenario**

A Rego unit test passes but admission behavior differs in-cluster. List the evidence needed to distinguish logic, version, webhook and scope issues.

**Model answer and reasoning**

The claim is incomplete until the team demonstrates the model’s elements and their relationships, not merely category labels. Inspect actual coverage, trust boundaries, assumptions, test evidence, ownership, residual risk and review cadence. Choose one missing or weak path, construct a benign synthetic fixture, predict expected behavior, run the check in the learner-owned environment, preserve the output and update the traceability record. Mark any platform-specific claim `[VERIFY]` until confirmed.

**Common wrong answers / approaches**

Counting labels as coverage; relying on a single happy-path test; inventing a score threshold; omitting evidence freshness; suppressing the issue instead of closing the gap.

**Evidence / verification expected**

A concise diagnosis with hypothesis, distinguishing evidence, safe test, expected outcome, result status (`PASS`, `FAIL`, `NOT RUN` or `OPEN`) and follow-up owner.

**Source / verification note**

The question tests source-syllabus principles. Any unprovided platform-specific detail remains `[VERIFY]`.

---

## Unit 12 — Runtime threat detection with Falco

**Source unit file:** `12-runtime-threat-detection-with-falco.md`

**Coverage focus:** runtime event sources, Falco rules/fields and version-sensitive driver/plugin support; detection logic, expected behavior, false positives/negatives, severity and rule tuning without blindness; benign authorized purple-team markers and expected-denial tests; sensor health, event-source coverage, dropped events, permissions, tampering and meta-monitoring; alert triage, evidence preservation, containment, scope, credential rotation, recovery and prevention; Prometheus/Alertmanager/Loki integration and syntax/metric names marked [VERIFY] unless verified; detection coverage matrix, alert quality, overhead and limitations; no alerts does not mean no attack.

### U12-Q01 — Conceptual short answer

- **ID:** `U12-Q01`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Explain the core principle: runtime detection depends on event-source coverage, sensor health, rule quality and triage; an alert is evidence to investigate, not proof by itself. Why is this control or reasoning step necessary before a team makes a production decision?

**Model answer and reasoning**

The key principle is that a control claim must be bounded by its scope, trust assumptions and evidence. In this unit, runtime detection depends on event-source coverage, sensor health, rule quality and triage; an alert is evidence to investigate, not proof by itself. Start from the asset/workload and the failure or threat being controlled, then state the evidence that would demonstrate the intended behavior. State residual risk rather than turning one signal into a universal guarantee.

**Common wrong answers / approaches**

Treating a tool, manifest or document as proof by itself; using a score or label without assumptions; omitting the failure mode or residual risk.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U12-Q02 — Conceptual short answer

- **ID:** `U12-Q02`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Conceptual short answer
- **Level:** L1
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

Name three distinct failure modes relevant to runtime threat detection with falco and explain how you would distinguish them during review.

**Model answer and reasoning**

Use at least three categories: (1) design gap—control intent or scope is incomplete; (2) implementation/coverage gap—the configuration does not enforce the intended rule across relevant paths; (3) evidence/operations gap—the control may exist but freshness, health, ownership or actual behavior is not demonstrated. Distinguish them with architecture review, positive and negative tests, and versioned evidence.

**Common wrong answers / approaches**

Calling every failure a tooling bug; assuming configuration presence proves runtime behavior; assuming an absent alert means no event occurred.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U12-Q03 — Conceptual short answer

- **ID:** `U12-Q03`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Conceptual short answer
- **Level:** L2
- **Objective tested:** Explain the unit’s core principle, limits and evidence boundary.
- **Estimated time:** 5 minutes

**Question / scenario**

How should this unit hand off to the earlier M01–M11 foundations without re-teaching them?

**Model answer and reasoning**

Reuse prior mechanics only as prerequisites: container basics and scanning/SBOM foundations (M01), CI/CD and OIDC concepts (M02), Kubernetes controls (M03–M04), packaging/GitOps (M06/M08), identity/secrets (M09), incident practices (M10) and observability (M11). This unit adds the security-specific trust model, evidence requirements, negative tests, governance and operational trade-offs. Record the exact prerequisite artifact or evidence instead of assuming mastery.

**Common wrong answers / approaches**

Rebuilding every earlier module; treating a prior lab success as production proof; assuming the learner knows a version-specific API not included in the source syllabus.

**Evidence / verification expected**

A concise written explanation plus the specific artifact, test or record that supports any operational claim.

**Source / verification note**

[VERIFY] Version-sensitive implementation details must be checked against the installed tool/schema; this question tests the stated principle, not an unverified flag.

---

### U12-Q04 — Multiple choice (exactly four options)

- **ID:** `U12-Q04`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Multiple choice (exactly four options)
- **Level:** L1
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

What does “no Falco alerts” establish when sensor health is unknown?

A. Nothing conclusive about threat absence; telemetry may be missing, unsupported or unhealthy.
B. It proves no runtime threat occurred.
C. It proves all rules are correctly tuned.
D. It proves admission policy blocked every unsafe workload.

**Model answer and reasoning**

**Correct answer: A.** Nothing conclusive about threat absence; telemetry may be missing, unsupported or unhealthy. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Nothing conclusive about threat absence; telemetry may be missing, unsupported or unhealthy.
- **B — Incorrect/tempting:** It proves no runtime threat occurred. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** It proves all rules are correctly tuned. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** It proves admission policy blocked every unsafe workload. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to runtime threat detection with falco.

**Source / verification note**

runtime detection depends on event-source coverage, sensor health, rule quality and triage; an alert is evidence to investigate, not proof by itself Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U12-Q05 — Multiple choice (exactly four options)

- **ID:** `U12-Q05`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

Which evidence is strongest when evaluating the main control in runtime threat detection with falco?

A. A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
B. A screenshot showing a configuration file exists.
C. A statement that the control is industry standard.
D. A successful test on a different platform with no recorded assumptions.

**Model answer and reasoning**

**Correct answer: A.** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** A reproducible positive test, a negative/correctness-trap test, captured inputs and outputs, and an explicit scope/version record.
- **B — Incorrect/tempting:** A screenshot showing a configuration file exists. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** A statement that the control is industry standard. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** A successful test on a different platform with no recorded assumptions. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to runtime threat detection with falco.

**Source / verification note**

runtime detection depends on event-source coverage, sensor health, rule quality and triage; an alert is evidence to investigate, not proof by itself Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U12-Q06 — Multiple choice (exactly four options)

- **ID:** `U12-Q06`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Multiple choice (exactly four options)
- **Level:** L2
- **Objective tested:** Select the defensible interpretation and explain every option.
- **Estimated time:** 4 minutes

**Question / scenario**

A team reports success for runtime threat detection with falco but has not tested a failure case. What is the best review response?

A. Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
B. Accept the claim because the happy path passed.
C. Disable the control until every possible edge case is known.
D. Replace evidence with a numerical maturity score.

**Model answer and reasoning**

**Correct answer: A.** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations. It is the only option that respects the control boundary and requires evidence rather than assuming effectiveness.

**Option analysis**

- **A — Correct:** Mark effectiveness as unproven, add a safe negative fixture, define expected behavior, and retain the result with limitations.
- **B — Incorrect/tempting:** Accept the claim because the happy path passed. This is insufficient because presence or assertion does not demonstrate behavior.
- **C — Incorrect/tempting:** Disable the control until every possible edge case is known. This overgeneralizes and does not establish the control’s actual scope.
- **D — Incorrect/tempting:** Replace evidence with a numerical maturity score. This substitutes unrelated evidence or an unsupported conclusion for verification.

**Evidence / verification expected**

Record the selected option, assumptions, and one positive plus one negative test relevant to runtime threat detection with falco.

**Source / verification note**

runtime detection depends on event-source coverage, sensor health, rule quality and triage; an alert is evidence to investigate, not proof by itself Tool flags, policy fields and specification text remain `[VERIFY]` unless a versioned official source is recorded.

---

### U12-Q07 — Artifact interpretation

- **ID:** `U12-Q07`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Rule test: expected event=`sensitive-path read`; observed events=0; sensor status=unknown; fixture=NOT RUN.
```

**Model answer and reasoning**

This is not evidence of a rule miss until sensor health and event-source coverage are established. Run an authorized harmless fixture, verify telemetry path and event loss, then inspect rule field support and filters. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U12-Q08 — Artifact interpretation

- **ID:** `U12-Q08`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Artifact interpretation
- **Level:** L2
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Alert: severity=high; process label=`python`; namespace=`ml`; rule name is custom; no command-line or user fields are included.
```

**Model answer and reasoning**

Do not infer maliciousness from a generic process label. Correlate process/user/container identity, expected workload behavior, audit events and deployment digest; preserve evidence and scope before disruptive response. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U12-Q09 — Artifact interpretation

- **ID:** `U12-Q09`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Artifact interpretation
- **Level:** L3
- **Objective tested:** Interpret a self-contained synthetic artifact and state the evidence boundary.
- **Estimated time:** 7 minutes

**Question / scenario**

Interpret the following excerpt. Identify the most important conclusion, what it does not establish, and the next safe verification step.

```text
[SYNTHETIC] Dashboard: alert count=0; event drops=unknown; sensor uptime=unknown; last event timestamp=unknown.
```

**Model answer and reasoning**

Zero alerts with unknown sensor health means detection status is unknown, not safe. Add monitored heartbeat/last-event/event-loss indicators and run scheduled benign test events. State what is known, unknown, and required to change the decision. Do not claim the artifact was generated by a real tool; it is synthetic assessment data.

**Common wrong answers / approaches**

Treating the artifact as authentic production output; ignoring subject/scope/freshness; concluding that one field proves the entire security property; failing to request a negative test.

**Evidence / verification expected**

Preserve the original excerpt, record the exact subject and environment, and run a harmless positive/negative fixture on the learner-owned lab if operational behavior is at issue.

**Source / verification note**

Artifact is `[SYNTHETIC]`; any exact tool output schema or API syntax is `[VERIFY]` against the selected version.

---

### U12-Q10 — Configuration / artifact review

- **ID:** `U12-Q10`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Configuration / artifact review
- **Level:** L2
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Detection rule review.** The rule uses an unsupported field for the selected event source, has no positive test, and suppresses an entire namespace to reduce noise. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** The rule uses an unsupported field for the selected event source. **Correction:** Verify field/source support for the installed version; add benign positive and negative fixtures; narrow suppression and document residual blind spots. Do not claim a rule works from YAML presence alone. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Has no positive test. **Correction:** Verify field/source support for the installed version; add benign positive and negative fixtures; narrow suppression and document residual blind spots. Do not claim a rule works from YAML presence alone. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Suppresses an entire namespace to reduce noise. **Correction:** Verify field/source support for the installed version; add benign positive and negative fixtures; narrow suppression and document residual blind spots. Do not claim a rule works from YAML presence alone. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Corrected artifact, at least three negative fixtures, one legitimate positive fixture, and a regression test for each defect. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U12-Q11 — Configuration / artifact review

- **ID:** `U12-Q11`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Sensor-health review.** No sensor-health metric is monitored, workloads can modify the sensor configuration, and dropped events are not surfaced. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** No sensor-health metric is monitored. **Correction:** Protect sensor deployment/RBAC, monitor process/driver/plugin health and event loss using supported signals, and alert on telemetry gaps. Confirm exact metrics/fields against versioned docs. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Workloads can modify the sensor configuration. **Correction:** Protect sensor deployment/RBAC, monitor process/driver/plugin health and event loss using supported signals, and alert on telemetry gaps. Confirm exact metrics/fields against versioned docs. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Dropped events are not surfaced. **Correction:** Protect sensor deployment/RBAC, monitor process/driver/plugin health and event loss using supported signals, and alert on telemetry gaps. Confirm exact metrics/fields against versioned docs. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Corrected artifact, at least three negative fixtures, one legitimate positive fixture, and a regression test for each defect. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U12-Q12 — Configuration / artifact review

- **ID:** `U12-Q12`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Configuration / artifact review
- **Level:** L3
- **Objective tested:** Find at least three defects, map each to a failure path, and propose defensive corrections.
- **Estimated time:** 10 minutes

**Question / scenario**

Review this synthetic review brief: **Response workflow review.** Alerts trigger immediate pod deletion, logs are not preserved, and credential rotation is omitted from the runbook. Identify at least three defects, correct each, name the attack or failure each enables, and specify a regression test.

**Model answer and reasoning**

1. **Defect:** Alerts trigger immediate pod deletion. **Correction:** Preserve relevant telemetry, contain exposure, scope related identities and workloads, rotate/revoke as justified, recover from trusted artifacts and verify. Automated destructive action requires a reviewed safety case. **Attack / failure enabled:** the omitted path or asset may remain outside the security model.
2. **Defect:** Logs are not preserved. **Correction:** Preserve relevant telemetry, contain exposure, scope related identities and workloads, rotate/revoke as justified, recover from trusted artifacts and verify. Automated destructive action requires a reviewed safety case. **Attack / failure enabled:** an untrusted input or resource may bypass the intended control.
3. **Defect:** Credential rotation is omitted from the runbook. **Correction:** Preserve relevant telemetry, contain exposure, scope related identities and workloads, rotate/revoke as justified, recover from trusted artifacts and verify. Automated destructive action requires a reviewed safety case. **Attack / failure enabled:** operators may mistake an unverified control for an effective one and fail to notice drift.

**Corrected approach:** implement the corrections above; add one legitimate positive fixture and at least three negative fixtures that exercise the identified paths. Record scope, owner, version, evidence and residual risk. Confirm the exact syntax against the selected tool or policy-engine version before deployment.

**Common wrong answers / approaches**

Listing defects without mapping them to a failure; suggesting a blanket disablement; claiming a policy or scanner guarantees security; failing to add a regression test for each defect.

**Evidence / verification expected**

Corrected artifact, at least three negative fixtures, one legitimate positive fixture, and a regression test for each defect. Include the corrected artifact or policy logic, three negative fixtures and at least one legitimate positive fixture. Verify exact syntax against the selected version.

**Source / verification note**

Any engine-specific syntax or schema is `[VERIFY]`; pseudocode is not deployable configuration. Use a learner-owned isolated lab only.

---

### U12-Q13 — Incident / response scenario

- **ID:** `U12-Q13`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Incident / response scenario
- **Level:** L4
- **Objective tested:** Apply a safe ordered response, preserve evidence and distinguish confirmed facts from hypotheses.
- **Estimated time:** 12 minutes

**Question / scenario**

a benign authorized lab action creates a harmless unexpected file/process marker, but the expected Falco alert does not appear. Provide the response in this order: symptom → first action → contain → scope → eradicate → recover → verify → prevent.

**Model answer and reasoning**

1. **Symptom:** record the observed signal and confidence; do not assume root cause.
2. **First action:** preserve relevant logs, event records, deployment digest, identity/audit trail and timestamps; open an incident record and establish an authorized owner.
3. **Contain:** apply the least disruptive safe isolation or gate appropriate to the exposure; preserve evidence before destructive replacement where feasible.
4. **Scope:** identify affected digests, identities, workloads, data paths, trust relationships and time window.
5. **Eradicate:** remove the root cause, revoke/rotate credentials when indicated, rebuild from a trusted source and remove unsafe artifacts or policy gaps.
6. **Recover:** restore only verified artifacts/configuration and communicate service impact.
7. **Verify:** rerun safe positive/negative tests, check old credentials or untrusted artifacts are rejected where relevant, and confirm telemetry/availability.
8. **Prevent:** add a regression test, owner, expiry/review date, alert or runbook update and post-incident follow-up.

**Common wrong answers / approaches**

Immediately deleting the workload before preserving evidence; rotating credentials without inventorying downstream consumers; testing discovered third-party credentials; declaring root cause before scoping; closing the incident because service recovered.

**Evidence / verification expected**

Timeline, preserved evidence references, containment decision, affected-scope list, remediation change, recovery checks, regression test and post-incident action owner.

**Source / verification note**

Follow M10 incident-management foundations. Use only learner-owned lab resources and dummy credentials; exact platform response commands are `[VERIFY]`.

---

### U12-Q14 — Design question with scoring rubric

- **ID:** `U12-Q14`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Design question with scoring rubric
- **Level:** L3
- **Objective tested:** Produce a threat-driven design with measurable controls, safe rollout and explicit residual risk.
- **Estimated time:** 15 minutes

**Question / scenario**

Design a runtime detection and response programme with verified event sources, benign test fixtures, sensor meta-monitoring, triage, tuning and evidence-preserving response.

**Model answer and reasoning**

A strong design begins with the protected assets and trust boundaries; states the intended threat reduction; assigns each control to a stage; records ownership and evidence; includes positive and negative tests; defines freshness, exception and failure behavior; and distinguishes local lab evidence from production guarantees. For this unit, prioritize: runtime detection depends on event-source coverage, sensor health, rule quality and triage; an alert is evidence to investigate, not proof by itself. Include a traceability row for every high-priority threat and a residual-risk decision for each gap.

**Scoring rubric (10 points)**

- Threat/assets and trust boundaries (2)
- Correct control selection and explicit assumptions (2)
- Positive/negative tests and evidence quality (2)
- Operational ownership, exceptions and failure handling (2)
- Residual risk, limitations and review cadence (2)

**Weak (0–3):** lists tools, no trust boundary or evidence. **Adequate (4–7):** correct controls and basic tests, but incomplete ownership or residual risk. **Excellent (8–10):** threat-mapped controls, versioned evidence, safe rollout, failure tests, clear owners, measurable outcomes and candid open gaps.

**Common wrong answers / approaches**

Choosing tools before threats; designing only the happy path; ignoring service availability; treating a local test as universal; leaving exceptions unowned or indefinite.

**Evidence / verification expected**

Architecture/flow diagram, control matrix, test plan, sample evidence bundle, exception record and a list of `[VERIFY]` items.

**Source / verification note**

Use the supplied M12 unit scope; exact product-specific API details must be verified against versioned official documentation.

---

### U12-Q15 — Synthesis / troubleshooting

- **ID:** `U12-Q15`
- **Unit / scope:** Unit 12 — Runtime threat detection with Falco
- **Type:** Synthesis / troubleshooting
- **Level:** L4
- **Objective tested:** Distinguish control existence from effectiveness and plan evidence-driven diagnosis.
- **Estimated time:** 10 minutes

**Question / scenario**

A purple-team fixture does not alert, but a dashboard shows zero events since a driver upgrade. Explain the first diagnostic sequence.

**Model answer and reasoning**

The claim is incomplete until the team demonstrates the model’s elements and their relationships, not merely category labels. Inspect actual coverage, trust boundaries, assumptions, test evidence, ownership, residual risk and review cadence. Choose one missing or weak path, construct a benign synthetic fixture, predict expected behavior, run the check in the learner-owned environment, preserve the output and update the traceability record. Mark any platform-specific claim `[VERIFY]` until confirmed.

**Common wrong answers / approaches**

Counting labels as coverage; relying on a single happy-path test; inventing a score threshold; omitting evidence freshness; suppressing the issue instead of closing the gap.

**Evidence / verification expected**

A concise diagnosis with hypothesis, distinguishing evidence, safe test, expected outcome, result status (`PASS`, `FAIL`, `NOT RUN` or `OPEN`) and follow-up owner.

**Source / verification note**

The question tests source-syllabus principles. Any unprovided platform-specific detail remains `[VERIFY]`.

---

## Cross-unit integration questions

Each integration question names the cross-unit dependency, asks for a decision, and requires evidence that distinguishes control existence from effectiveness.

### XINT-Q01 — Integration scenario

- **ID:** `XINT-Q01`
- **Unit / scope:** Cross-unit integration — U01 + U08
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect threat model → admission to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**Threat model → admission.** A model-serving deployment is blocked by a signature policy, but the threat model lists only package vulnerabilities.

**Model answer and reasoning**

Trace the asset and trust boundary: verify the exact digest, approved signer identity, source/builder claims and policy scope; add the artifact-origin threat and residual risk to the model. A signature is not a vulnerability verdict. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Updated threat-to-control traceability row and wrong-signer negative fixture. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q02 — Integration scenario

- **ID:** `XINT-Q02`
- **Unit / scope:** Cross-unit integration — U02 + U09
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect scanning → release decision to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**Scanning → release decision.** Two findings have the same CVSS severity; one is reachable on an internet-facing API and fixed, the other is build-only with no fix.

**Model answer and reasoning**

Prioritize exposure, reachability, exploitability, fix availability, criticality and blast radius; record uncertainty for the build-only issue. CVSS alone does not settle ordering. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Ranked finding queue with timestamps and rationale. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q03 — Integration scenario

- **ID:** `XINT-Q03`
- **Unit / scope:** Cross-unit integration — U03 + U09
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect sbom → incident response to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**SBOM → incident response.** An advisory affects a dependency; an SBOM exists for the release tag but not for the digest deployed last week.

**Model answer and reasoning**

Resolve the deployed digest from cluster/registry evidence, index the matching SBOM or regenerate it, query component inventory and scope all affected workloads. Do not assume tag equals digest. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Digest inventory, affected-workload list and evidence provenance. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q04 — Integration scenario

- **ID:** `XINT-Q04`
- **Unit / scope:** Cross-unit integration — U04 + U02
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect signature → vulnerable image to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**Signature → vulnerable image.** Signature verification passes and the image has a critical reachable vulnerability with a fix available.

**Model answer and reasoning**

Treat authenticity and vulnerability posture as separate gates; block/quarantine or use a documented time-bounded exception while patching, then rescan the exact digest. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Signature evidence plus scan/triage and deployment decision. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q05 — Integration scenario

- **ID:** `XINT-Q05`
- **Unit / scope:** Cross-unit integration — U05 + U03
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect build identity → cache trust to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**Build identity → cache trust.** An untrusted pull request cannot access a signing secret directly but can write a cache used by the release job.

**Model answer and reasoning**

Separate writable cache trust domains, validate build inputs and use isolated trusted build execution; test with a harmless cache marker. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Cache access controls and negative cross-domain fixture. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q06 — Integration scenario

- **ID:** `XINT-Q06`
- **Unit / scope:** Cross-unit integration — U06 + U01
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect workload identity → blast radius to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**Workload identity → blast radius.** A short-lived inference token can write to the model registry and change deployment policy.

**Model answer and reasoning**

Short lifetime does not cure excess authorization. Split runtime read access from publish/deploy authority, audit the access graph and test denied writes. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Permission graph, policy test and owner list. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q07 — Integration scenario

- **ID:** `XINT-Q07`
- **Unit / scope:** Cross-unit integration — U07 + U12
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect runtime hardening → detection to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**Runtime hardening → detection.** A pod is non-root and read-only but a sensitive data-access event still occurs.

**Model answer and reasoning**

Hardening reduces some privilege and write paths but does not remove authorized data access or application-level misuse. Review identity, data authorization, network paths and detection evidence. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Data-access audit and scoped least-privilege test. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q08 — Integration scenario

- **ID:** `XINT-Q08`
- **Unit / scope:** Cross-unit integration — U08 + U11
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect admission → update path to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**Admission → update path.** A policy denies an unapproved image on Pod CREATE, but a controller UPDATE changes the workload template.

**Model answer and reasoning**

Test the actual resource kind and CREATE/UPDATE paths, then verify controller-generated Pods and mutation order. Keep engine/version behavior explicit. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Update-path negative test and controller-level evidence. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q09 — Integration scenario

- **ID:** `XINT-Q09`
- **Unit / scope:** Cross-unit integration — U10 + U04
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect slsa → authenticity to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**SLSA → authenticity.** A provenance document includes a builder field but is unsigned and the subject differs from deployment.

**Model answer and reasoning**

Presence of fields is not authentication. Verify signature/trust chain, subject digest, source and builder under the selected verified policy; otherwise keep the claim open. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Authenticated provenance verification output and wrong-subject fixture. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q10 — Integration scenario

- **ID:** `XINT-Q10`
- **Unit / scope:** Cross-unit integration — U12 + U11
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect falco → missing event to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**Falco → missing event.** A benign test does not alert and the sensor dashboard has no heartbeat.

**Model answer and reasoning**

First establish sensor/event-source health and event delivery, then inspect rule syntax, field support, filters and expected fixture. Do not tune a rule until telemetry is known to be present. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Heartbeat/last-event evidence and controlled benign test. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q11 — Integration scenario

- **ID:** `XINT-Q11`
- **Unit / scope:** Cross-unit integration — U02 + U09
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect audit → stale scanner to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**Audit → stale scanner.** A finding dashboard is green, but the scanner database refresh failed three days ago.

**Model answer and reasoning**

Treat results as stale/inconclusive if freshness policy is not met; repair refresh, rerun scans against running digests and preserve the failed-refresh event. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Freshness gate negative test and reconciled digest coverage. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q12 — Integration scenario

- **ID:** `XINT-Q12`
- **Unit / scope:** Cross-unit integration — U08 + U09
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect exception → emergency release to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**Exception → emergency release.** A critical fix must ship while an admission policy blocks the image because a required attestation is delayed.

**Model answer and reasoning**

Use a narrowly scoped, approved, time-bounded exception only if policy allows; record owner, rationale, compensating controls, expiry and post-release verification. Do not disable the global policy. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Exception record, audit event and expiry enforcement test. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q13 — Integration scenario

- **ID:** `XINT-Q13`
- **Unit / scope:** Cross-unit integration — U06 + U10
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect credential rotation → incident to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**Credential rotation → incident.** A token may be exposed and the workload has access to a shared data store.

**Model answer and reasoning**

Preserve logs, contain exposure, inventory relying services and downstream credentials, revoke/rotate with safe sequencing, scope reads/writes, then verify old-token rejection. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Timeline, downstream consumer list and old-token negative test. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q14 — Integration scenario

- **ID:** `XINT-Q14`
- **Unit / scope:** Cross-unit integration — U03 + U09
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect vex → closure to a defensible operational decision.
- **Estimated time:** 8 minutes

**Question / scenario**

**VEX → closure.** A VEX statement says not affected but has no evidence and no expiry.

**Model answer and reasoning**

Reject or reopen the disposition; require product/version scope, technical justification, evidence, approver and review date. Do not suppress the finding solely on a label. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Reviewed VEX record and expiry check. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q15 — Integration scenario

- **ID:** `XINT-Q15`
- **Unit / scope:** Cross-unit integration — U03 + U01
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect sbom → model inventory to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**SBOM → model inventory.** The image SBOM lists Python packages but not model weights or training-data lineage.

**Model answer and reasoning**

Use software SBOM for components it observes; maintain model-artifact/data lineage inventory separately and bind model artifact digest and origin evidence. Do not claim SBOM describes model behavior. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Model inventory record linked to release and artifact digest. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q16 — Integration scenario

- **ID:** `XINT-Q16`
- **Unit / scope:** Cross-unit integration — U11 + U08
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect policy engine → privilege to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Policy engine → privilege.** A policy controller can generate RoleBindings but its own permissions are not reviewed.

**Model answer and reasoning**

Treat the policy engine as privileged infrastructure; minimize RBAC, audit policy changes and generated resources, restrict exceptions, monitor controller health and rehearse upgrades. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

RBAC diff, audit logs and privilege regression test. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q17 — Integration scenario

- **ID:** `XINT-Q17`
- **Unit / scope:** Cross-unit integration — U12 + U11
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect falco → alert precision to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Falco → alert precision.** A rule alerts on every Python process in a namespace and the team proposes suppressing the namespace.

**Model answer and reasoning**

Build a baseline of expected behavior, use supported context fields and narrow the condition without blinding coverage; validate benign positives and known negative controls. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Precision/recall-style review with false-positive samples and a detection gap statement. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q18 — Integration scenario

- **ID:** `XINT-Q18`
- **Unit / scope:** Cross-unit integration — U08 + U11
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect registry allow-list → regex bypass to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Registry allow-list → regex bypass.** A registry rule matches `trusted.example` as a substring, and a lookalike hostname is admitted.

**Model answer and reasoning**

Use anchored, parsed registry identity matching appropriate to the engine; add lookalike-host and port/path fixtures. Verify matching semantics with the selected policy engine. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Negative fixture for lookalike host and approved registry positive fixture. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q19 — Integration scenario

- **ID:** `XINT-Q19`
- **Unit / scope:** Cross-unit integration — U07 + U01
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect cis benchmark → platform to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**CIS benchmark → platform.** A kube-bench-style report shows a control failed on a managed cluster where the setting is provider-controlled.

**Model answer and reasoning**

Map the finding to the actual platform responsibility boundary, verify benchmark/version, document compensating controls and provider evidence, and avoid changing unsupported control-plane settings blindly. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Triage entry with applicability, owner and residual risk. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q20 — Integration scenario

- **ID:** `XINT-Q20`
- **Unit / scope:** Cross-unit integration — U10 + U03
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect build provenance → external parameters to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Build provenance → external parameters.** Two builds differ and one used an unrecorded dependency source.

**Model answer and reasoning**

Capture declared external parameters and dependency snapshots; reproduce under controlled inputs and compare outputs. Different hashes alone do not prove malicious tampering. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Rebuild manifest and hypothesis log. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q21 — Integration scenario

- **ID:** `XINT-Q21`
- **Unit / scope:** Cross-unit integration — U09 + U02
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect scanner count → goodhart to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Scanner count → Goodhart.** A team is rewarded for reducing findings and begins ignoring all unfixed issues.

**Model answer and reasoning**

Replace raw count with coverage, freshness, age, exposure window, verified remediation, exception age and risk-weighted trends. Audit ignore changes and report limitations. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Metric definition sheet and a counter-metric. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q22 — Integration scenario

- **ID:** `XINT-Q22`
- **Unit / scope:** Cross-unit integration — U12 + U10
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect runtime response → evidence to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Runtime response → evidence.** An operator deletes a pod immediately after an alert and later cannot reconstruct its process state.

**Model answer and reasoning**

Preserve relevant logs, event and deployment evidence first where feasible, then contain; scope related identities, rotate credentials if indicated, recover from trusted artifacts and add prevention. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Incident timeline and runbook change. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q23 — Integration scenario

- **ID:** `XINT-Q23`
- **Unit / scope:** Cross-unit integration — U03 + U04
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect attestation → subject binding to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Attestation → subject binding.** A signed SBOM attestation is valid but its subject digest differs from the deployment.

**Model answer and reasoning**

Reject the association; regenerate/attach for the exact digest and verify the subject. A valid signature authenticates the wrong subject if binding is not checked. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Wrong-subject negative test. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q24 — Integration scenario

- **ID:** `XINT-Q24`
- **Unit / scope:** Cross-unit integration — U08 + U07
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect admission fail-open → outage to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Admission fail-open → outage.** The team must choose webhook failure policy for a critical service.

**Model answer and reasoning**

Make the decision threat- and availability-driven; document what is allowed during webhook outage, stage rollout, monitor HA and test failure behavior. Do not claim one universal answer. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Failure-mode analysis, recovery/rollback plan and test evidence. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q25 — Integration scenario

- **ID:** `XINT-Q25`
- **Unit / scope:** Cross-unit integration — U05 + U06
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect oidc → provider claim to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**OIDC → provider claim.** A workflow trusts any token from the CI provider rather than a particular repository/ref/environment.

**Model answer and reasoning**

Constrain trust to the verified issuer, audience and repository/workflow/ref claims supported by that provider; record exact claim semantics as `[VERIFY]` until checked. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Negative token/claim test and trust-policy evidence. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q26 — Integration scenario

- **ID:** `XINT-Q26`
- **Unit / scope:** Cross-unit integration — U02 + U09
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect vulnerability → running digest to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Vulnerability → running digest.** A patched image was built but old pods remain running.

**Model answer and reasoning**

Compare image digests in cluster inventory to the patched digest, roll out safely, verify replacements and rescan/close only after exact-digest evidence. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Cluster digest report and post-deployment scan. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q27 — Integration scenario

- **ID:** `XINT-Q27`
- **Unit / scope:** Cross-unit integration — U03 + U01
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect sbom quality → missing component to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**SBOM quality → missing component.** A generator does not detect a statically linked library.

**Model answer and reasoning**

Record tool coverage limits, reconcile build manifests and binary inventory, and do not treat absence as proof. Add a known-component fixture to monitor coverage. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Known-component detection test and limitations note. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q28 — Integration scenario

- **ID:** `XINT-Q28`
- **Unit / scope:** Cross-unit integration — U01 + U12
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect threat model → incident learning to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Threat model → incident learning.** An incident reveals a model registry write path missing from the DFD.

**Model answer and reasoning**

Update the DFD, threat/control mapping, owners and residual risk; add a regression test and review trigger so incident learning changes the system of record. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Versioned threat-model diff and assigned actions. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q29 — Integration scenario

- **ID:** `XINT-Q29`
- **Unit / scope:** Cross-unit integration — U05 + U04
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect ci isolation → kill switch to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**CI isolation → kill switch.** A trusted runner may be compromised while queued releases wait.

**Model answer and reasoning**

Pause trusted release capability, revoke/disable affected identity, preserve runner/job logs and cache evidence, assess published digests, rotate trust material if indicated and rebuild from a known-good environment. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Kill-switch runbook and safe rehearsal result. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q30 — Integration scenario

- **ID:** `XINT-Q30`
- **Unit / scope:** Cross-unit integration — U04 + U10
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect key rotation → old trust to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Key rotation → old trust.** A new signing key is in use but admission still trusts the compromised key.

**Model answer and reasoning**

Update verifier trust policy, define any necessary transition window, reject old key for new releases and audit artifacts signed during exposure. Verify rollback does not reintroduce the key. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Old-key rejection test and key inventory. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q31 — Integration scenario

- **ID:** `XINT-Q31`
- **Unit / scope:** Cross-unit integration — U07 + U08
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect runtime network → cni to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Runtime network → CNI.** A default-deny NetworkPolicy exists but forbidden egress succeeds.

**Model answer and reasoning**

Verify the CNI supports/enforces policies, selectors and effective rules; check namespace/pod labels and alternate network paths. YAML existence is not runtime proof. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Allowed/denied connectivity matrix on the target CNI. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q32 — Integration scenario

- **ID:** `XINT-Q32`
- **Unit / scope:** Cross-unit integration — U10 + U04
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect provenance → local simulation to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Provenance → local simulation.** A local script produces a provenance-like statement and the team calls the builder production-trusted.

**Model answer and reasoning**

Label the exercise a simulation, identify absent hosted-builder isolation/identity guarantees and make no level claim without applicable verified requirements and evidence. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Gap matrix separating lab and production guarantees. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q33 — Integration scenario

- **ID:** `XINT-Q33`
- **Unit / scope:** Cross-unit integration — U12 + U10
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect falco → destructive automation to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Falco → destructive automation.** A high-severity alert automatically deletes the pod before triage.

**Model answer and reasoning**

Require a reviewed safety case, confidence and scope checks, evidence preservation, human approval or bounded containment, and recovery path before high-impact action. Alert severity alone is not enough. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Dry-run response test and evidence-retention check. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q34 — Integration scenario

- **ID:** `XINT-Q34`
- **Unit / scope:** Cross-unit integration — U03 + U02
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect vex → scanner suppression to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**VEX → scanner suppression.** A finding is suppressed because a component is not reachable in one code path.

**Model answer and reasoning**

Scope the claim to affected product/version and demonstrated reachability assumptions; preserve evidence and re-review on build/runtime change. Do not generalize beyond the tested conditions. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

VEX evidence and change-trigger review. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q35 — Integration scenario

- **ID:** `XINT-Q35`
- **Unit / scope:** Cross-unit integration — U06 + U12
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect admission → workload kinds to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Admission → workload kinds.** Policy covers Deployments but misses Jobs used for ETL.

**Model answer and reasoning**

Enumerate supported workload kinds and generated Pods; test templates and actual resources across create/update paths. Keep the resource coverage matrix in version control. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Kind-by-kind test matrix. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q36 — Integration scenario

- **ID:** `XINT-Q36`
- **Unit / scope:** Cross-unit integration — U03 + U04
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect secrets → cache leakage to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Secrets → cache leakage.** A dummy secret marker appears in a trusted cache artifact after untrusted testing.

**Model answer and reasoning**

Quarantine the cache, inspect access and retention, rotate any real credentials if evidence indicates exposure, separate cache namespaces and add a canary test. Never print or test real secrets unnecessarily. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Cache lineage and dummy-marker regression test. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q37 — Integration scenario

- **ID:** `XINT-Q37`
- **Unit / scope:** Cross-unit integration — U01 + U06
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect model hub → source trust to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Model hub → source trust.** A model is downloaded from an unfamiliar hub and then signed by the internal build job.

**Model answer and reasoning**

Internal signing only attests to the signer’s action; it does not independently prove upstream origin or model safety. Verify source, hash, license, deserialization format and approval workflow. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Source provenance and model-artifact review record. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q38 — Integration scenario

- **ID:** `XINT-Q38`
- **Unit / scope:** Cross-unit integration — U05 + U04
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect observability → tampering to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Observability → tampering.** An alert source is suspected of being modified by the same operator who controls the workload.

**Model answer and reasoning**

Use independent audit/log paths and restrict sensor configuration changes; preserve multiple evidence sources and review RBAC separation. Note any single-admin trust limitation. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Audit-source integrity and role-separation review. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q39 — Integration scenario

- **ID:** `XINT-Q39`
- **Unit / scope:** Cross-unit integration — U09 + U02
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect incident → affected scope to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Incident → affected scope.** A critical dependency advisory is announced, but registry tags are mutable and historical digest inventory is incomplete.

**Model answer and reasoning**

Reconstruct deployed digests from cluster/audit/registry records, use SBOM index where available, state uncertainty and prioritize exposed workloads. Do not assume current tag maps to historical release. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Time-bounded affected-digest list and confidence notes. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q40 — Integration scenario

- **ID:** `XINT-Q40`
- **Unit / scope:** Cross-unit integration — U03 + U10
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect build → release authorization to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Build → release authorization.** A branch protection rule exists but a workflow can publish on an unprotected ref.

**Model answer and reasoning**

Test actual trigger/ref conditions and token permissions, restrict identity claims to protected refs/environments and verify the negative path using a harmless fixture. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Unprotected-ref publish denial evidence. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q41 — Integration scenario

- **ID:** `XINT-Q41`
- **Unit / scope:** Cross-unit integration — U08 + U09
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect audit → exception abuse to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Audit → exception abuse.** The exception report shows the same team repeatedly renews the same waiver.

**Model answer and reasoning**

Review root cause, expiry and compensating controls; require independent approval and escalation for repeat renewals; track exception age and affected exposure rather than hiding the finding. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Exception trend, approver record and remediation plan. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q42 — Integration scenario

- **ID:** `XINT-Q42`
- **Unit / scope:** Cross-unit integration — U01 + U03
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect sbom → provenance → signature to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**SBOM → provenance → signature.** An SBOM, provenance and signature each exist but refer to three different digests.

**Model answer and reasoning**

Reject the bundle as internally inconsistent. Bind every statement to the same intended subject digest and verify each trust relationship independently. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Cross-artifact digest consistency test. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q43 — Integration scenario

- **ID:** `XINT-Q43`
- **Unit / scope:** Cross-unit integration — U08 + U11
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect admission → rollout to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Admission → rollout.** Deny mode blocks a critical rollback because the rollback image lacks current attestations.

**Model answer and reasoning**

Keep rollback artifacts and required evidence prepared before rollout; define a narrowly scoped audited emergency path with expiry and post-event verification rather than disabling policy globally. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Rollback rehearsal and exception audit trail. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q44 — Integration scenario

- **ID:** `XINT-Q44`
- **Unit / scope:** Cross-unit integration — U06 + U09
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect threat model → privacy to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Threat model → privacy.** A data-flow diagram shows model telemetry but not sensitive prompt or inference payload retention.

**Model answer and reasoning**

Add observability stores and operators to the DFD, classify data, set retention/access controls and consider privacy threats; avoid collecting raw payloads without a purpose and authorization. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Updated DFD, retention policy and access review. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q45 — Integration scenario

- **ID:** `XINT-Q45`
- **Unit / scope:** Cross-unit integration — U12 + U11
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect scanner → offline mode to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Scanner → offline mode.** An offline build uses a cached vulnerability database whose age is not recorded.

**Model answer and reasoning**

Record database snapshot age and policy; fail or mark inconclusive beyond the defined freshness window, and refresh through an approved path. Never represent stale data as current. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Offline freshness fixture and evidence metadata. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q46 — Integration scenario

- **ID:** `XINT-Q46`
- **Unit / scope:** Cross-unit integration — U05 + U08
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect slsa → requirement claim to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**SLSA → requirement claim.** A manager asks for a level label before the team has mapped every requirement to evidence.

**Model answer and reasoning**

Select and verify the current track/version, map every applicable requirement to threat/control/evidence and leave gaps open. No unsupported level claim. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Traceability matrix and verified spec notes. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q47 — Integration scenario

- **ID:** `XINT-Q47`
- **Unit / scope:** Cross-unit integration — U09 + U02
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect policy → missing/null to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Policy → missing/null.** A policy tests a field only when present, and absence results in allow.

**Model answer and reasoning**

Define explicit missing/null semantics for the actual engine/schema; test absent, null, empty and malformed inputs. Do not rely on accidental default behavior. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Boundary fixtures for all value states. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q48 — Integration scenario

- **ID:** `XINT-Q48`
- **Unit / scope:** Cross-unit integration — U08 + U01
- **Type:** Integration scenario
- **Level:** L2
- **Objective tested:** Connect runtime → identity rotation to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Runtime → identity rotation.** A pod is replaced but the old token remains valid in a downstream service.

**Model answer and reasoning**

Test old-token rejection at relying services, inventory caches and token exchange paths, then revoke/rotate as needed. Pod replacement is not credential revocation. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Old-token denial evidence and downstream inventory. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q49 — Integration scenario

- **ID:** `XINT-Q49`
- **Unit / scope:** Cross-unit integration — U10 + U04
- **Type:** Integration scenario
- **Level:** L3
- **Objective tested:** Connect detection → alert quality to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Detection → alert quality.** A rule has high alert volume but no confirmed outcomes or coverage denominator.

**Model answer and reasoning**

Track tested coverage, true/false positive review, event-source health, alert-to-triage time and known blind spots; avoid optimizing alert volume alone. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Detection coverage matrix and sample disposition audit. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

### XINT-Q50 — Integration scenario

- **ID:** `XINT-Q50`
- **Unit / scope:** Cross-unit integration — U02 + U05
- **Type:** Integration scenario
- **Level:** L4
- **Objective tested:** Connect zero budget → production claims to a defensible operational decision.
- **Estimated time:** 10 minutes

**Question / scenario**

**Zero budget → production claims.** A learner uses `kind`, local signing and synthetic identities and asks whether production security is proven.

**Model answer and reasoning**

Report local evidence as local; list untested managed-cluster, hosted CI, identity-provider, CNI, kernel and trust-root assumptions. Zero-budget learning can demonstrate reasoning but not certify production controls. State the residual risk and do not infer more than the evidence supports.

**Common wrong answers / approaches**

Assuming one control proves the whole chain; skipping the exact subject/identity; making a version-specific claim without verification; choosing a high-impact action before preserving evidence; hiding uncertainty instead of marking `OPEN`.

**Evidence / verification expected**

Open-gap register and planned platform verification. Include input artifact, environment/version, expected and observed results, owner, timestamp and any open gap. Use `NOT RUN` when no execution evidence exists.

**Source / verification note**

This is a source-aligned integration scenario with `[SYNTHETIC]` facts. Verify exact tool/API/spec behavior against the installed version; do not infer a SLSA requirement or policy field from memory.

---

## Design-review whiteboard prompts

These 16 prompts are additional to the 230 core questions. Each is intended for a 20–40 minute design review and should be answered with a diagram or structured artifact, not only prose.

### DRW-Q01 — Threat model for a new data/ML platform

- **ID:** `DRW-Q01`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** Inference API, ETL, notebooks, model registry and training data; small team; laptop-first lab.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Draw DFD with at least 10 elements and trust boundaries, STRIDE threats, controls, owners, residual risk and review dates.

**Required diagram/table or written artifact**

DFD, threat register and control traceability matrix.

**Weighted rubric**

Assets/boundaries 25%; threat quality 25%; control/evidence mapping 20%; residual risk/ownership 20%; clarity 10%.

**Weak / adequate / excellent characteristics**

Weak: framework checklist only. Adequate: main flows and threats. Excellent: explicit assumptions, abuse paths, testable controls and incident-driven review.

**Likely reviewer follow-ups**

Which trust boundary has the highest blast radius? What evidence would change the likelihood assessment?

**Common pitfalls**

False precision; omitted external entities; controls without owners.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q02 — Vulnerability triage and remediation policy

- **ID:** `DRW-Q02`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** A few hundred synthetic findings, mixed exposure and uncertain fix availability.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Design triage, gating, SLA, exception and rescanning policy without relying on severity alone.

**Required diagram/table or written artifact**

Risk-ranked queue, lifecycle states and metric definitions.

**Weighted rubric**

Contextual risk 30%; evidence/freshness 20%; remediation workflow 20%; exception governance 15%; metrics 15%.

**Weak / adequate / excellent characteristics**

Weak: sort by CVSS. Adequate: includes exposure and owner. Excellent: incorporates fixability, running digest, freshness and gaming resistance.

**Likely reviewer follow-ups**

What if the database is stale? How do you close an unfixable finding?

**Common pitfalls**

Raw count KPI; permanent ignores; stale source signals.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q03 — SBOM programme and “are we affected?” response

- **ID:** `DRW-Q03`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** Multiple deployed image digests and a new synthetic advisory.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Design generation, digest association, indexing, diffing, completeness review and incident query.

**Required diagram/table or written artifact**

SBOM lifecycle diagram and incident response query plan.

**Weighted rubric**

Digest binding 25%; completeness 20%; storage/query 20%; incident usability 20%; limitations 15%.

**Weak / adequate / excellent characteristics**

Weak: generate one SBOM. Adequate: attach to releases. Excellent: reconcile source/image inventory and state blind spots.

**Likely reviewer follow-ups**

How would you detect a vendored static library? What is provenance’s separate role?

**Common pitfalls**

Assuming SBOM completeness or treating it as provenance.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q04 — Image-signing trust model

- **ID:** `DRW-Q04`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** Local lab now; future hosted CI; key-based and keyless options under consideration.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Compare identity, key custody, trust roots, subject binding and operational recovery.

**Required diagram/table or written artifact**

Trust-boundary diagram and positive/negative verification matrix.

**Weighted rubric**

Identity/trust 25%; digest binding 20%; custody/rotation 20%; tests 20%; limitations 15%.

**Weak / adequate / excellent characteristics**

Weak: “signature valid.” Adequate: pinned signer. Excellent: compromise handling and scoped trust assumptions.

**Likely reviewer follow-ups**

What exactly does keyless trust depend on? How do you revoke compromised trust?

**Common pitfalls**

Claiming signing proves safety; conflating local and public trust.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q05 — CI hardening and short-lived identity

- **ID:** `DRW-Q05`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** Fork PRs and trusted release jobs currently share workflow and cache infrastructure.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Design separation, ephemeral runners, minimal permissions, OIDC trust and egress boundaries.

**Required diagram/table or written artifact**

Workflow trust diagram, permission matrix and kill-switch runbook.

**Weighted rubric**

Trust separation 30%; identity 20%; cache isolation 20%; tests 15%; operations 15%.

**Weak / adequate / excellent characteristics**

Weak: secret masking only. Adequate: separate release job. Excellent: negative tests for trigger, cache and identity claims.

**Likely reviewer follow-ups**

How can a cache cross a trust boundary? What if runner compromise is suspected?

**Common pitfalls**

Assuming OIDC alone means least privilege; untrusted writable cache.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q06 — Workload identity and rotation

- **ID:** `DRW-Q06`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** Inference, ETL and notebook jobs share data and registry resources.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Design identity inventory, least privilege, measured rotation and old-token rejection.

**Required diagram/table or written artifact**

Access graph, rotation timeline and evidence checklist.

**Weighted rubric**

Least privilege 25%; blast radius 20%; rotation validation 25%; auditability 15%; recovery 15%.

**Weak / adequate / excellent characteristics**

Weak: issue a new token. Adequate: rotate and restart. Excellent: prove old-token rejection across consumers and assess downstream trust.

**Likely reviewer follow-ups**

What if a downstream cache keeps the old token?

**Common pitfalls**

No consumer inventory; treating short TTL as complete mitigation.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q07 — Runtime hardening baseline and exceptions

- **ID:** `DRW-Q07`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** Inference, ETL and notebook workloads have different compatibility needs.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Define baseline for identity, filesystem, capabilities, seccomp, resources, probes and network boundaries; govern exceptions.

**Required diagram/table or written artifact**

Baseline table, conformance matrix and exception record.

**Weighted rubric**

Threat alignment 25%; workload fit 20%; negative tests 20%; exception governance 20%; platform caveats 15%.

**Weak / adequate / excellent characteristics**

Weak: same settings blindly everywhere. Adequate: baseline plus exceptions. Excellent: evidence-driven profile and expiry.

**Likely reviewer follow-ups**

What does the CNI enforce? Which writable paths are required?

**Common pitfalls**

Assuming NetworkPolicy YAML guarantees enforcement.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q08 — Admission policy architecture and rollout

- **ID:** `DRW-Q08`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** A policy must verify image digest, approved registry and signature evidence without causing a first-day outage.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Compare build/admission/runtime controls, fail-open/closed, staged rollout, webhook HA and exceptions.

**Required diagram/table or written artifact**

Policy architecture, rollout gates and failure-mode table.

**Weighted rubric**

Coverage 25%; correctness tests 25%; availability 20%; exception control 15%; upgrade/rollback 15%.

**Weak / adequate / excellent characteristics**

Weak: immediate deny. Adequate: audit then enforce. Excellent: negative fixtures, update paths, outage behavior and rollback rehearsal.

**Likely reviewer follow-ups**

How do you test missing/null fields? What happens if webhook is down?

**Common pitfalls**

Policy existence as proof; broad opt-out labels.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q09 — Remediation SLAs, exceptions and audit evidence

- **ID:** `DRW-Q09`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** An audit finds overdue exceptions and closures tied to different digests.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Design normalized lifecycle, evidence retention, owners, SLA breaches and expiry enforcement.

**Required diagram/table or written artifact**

Lifecycle state diagram, dashboard specification and sample evidence index.

**Weighted rubric**

Lifecycle correctness 25%; evidence 25%; exception governance 20%; metrics 15%; privacy/access 15%.

**Weak / adequate / excellent characteristics**

Weak: ticket closed. Adequate: rescan and owner. Excellent: exact digest, freshness, auditability and counter-metrics.

**Likely reviewer follow-ups**

How are false closures detected? Who can see sensitive findings?

**Common pitfalls**

Close at merge; exposing sensitive findings broadly.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q10 — SLSA/provenance adoption roadmap

- **ID:** `DRW-Q10`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** The team has local provenance-like output but no verified hosted-builder evidence.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Select and verify a spec track/version, map requirements to threat/control/evidence and stage adoption.

**Required diagram/table or written artifact**

Requirement traceability matrix and open-gap plan.

**Weighted rubric**

Spec fidelity 25%; threat mapping 20%; evidence 25%; staged plan 15%; honesty about gaps 15%.

**Weak / adequate / excellent characteristics**

Weak: level badge. Adequate: basic provenance verification. Excellent: requirement-by-requirement evidence and no unsupported claim.

**Likely reviewer follow-ups**

Which requirement text is verified? What is simulated only?

**Common pitfalls**

Memorized/outdated level definitions; local simulation called production-grade.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q11 — Kyverno vs Gatekeeper vs VAP

- **ID:** `DRW-Q11`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** A platform must choose a policy mechanism and migrate safely.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Compare scope, operational model, tests and support; plan separate engine rehearsals and staged enforcement.

**Required diagram/table or written artifact**

Decision matrix and migration test plan.

**Weighted rubric**

Fit 20%; correctness 25%; operational burden 20%; testing 20%; failure handling 15%.

**Weak / adequate / excellent characteristics**

Weak: popularity-based choice. Adequate: criteria and pilot. Excellent: versioned evaluation, negative tests and rollback.

**Likely reviewer follow-ups**

What exact version/schema is supported? How do you detect always-pass defects?

**Common pitfalls**

Installing both engines in same lab and conflating results.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q12 — Falco detection strategy

- **ID:** `DRW-Q12`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** A small team needs useful runtime detections without alert fatigue.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Design rule coverage, benign fixtures, event-source verification, sensor health and safe response.

**Required diagram/table or written artifact**

Detection matrix, test fixtures and alert triage runbook.

**Weighted rubric**

Coverage 25%; rule quality 20%; sensor health 20%; response safety 20%; overhead/metrics 15%.

**Weak / adequate / excellent characteristics**

Weak: more rules. Adequate: test rules and tune. Excellent: meta-monitoring, known blind spots and evidence-preserving response.

**Likely reviewer follow-ups**

How do you distinguish rule defect from missing telemetry?

**Common pitfalls**

Suppressing whole namespaces; automated pod deletion by default.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q13 — Supply-chain incident response and recovery

- **ID:** `DRW-Q13`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** A builder identity may be compromised and several releases are deployed.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Define evidence preservation, kill switch, artifact scoping, key/identity revocation, rebuild and verification order.

**Required diagram/table or written artifact**

Incident timeline, affected digest list and recovery checklist.

**Weighted rubric**

Ordering 25%; scope 20%; trust recovery 20%; evidence 20%; prevention 15%.

**Weak / adequate / excellent characteristics**

Weak: rotate everything immediately without scoping. Adequate: isolate and rebuild. Excellent: preserves evidence and validates old trust rejection.

**Likely reviewer follow-ups**

Which artifacts remain trustworthy? How are rollback artifacts verified?

**Common pitfalls**

Destroying evidence; reusing compromised build environment.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q14 — Security-versus-velocity negotiation

- **ID:** `DRW-Q14`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** A release is blocked by missing attestation and business impact is material.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Design an exception/alternative that preserves accountability and avoids global gate disablement.

**Required diagram/table or written artifact**

Decision record, exception record and post-release verification plan.

**Weighted rubric**

Risk transparency 25%; options/trade-offs 20%; authorization 20%; expiry/verification 20%; communication 15%.

**Weak / adequate / excellent characteristics**

Weak: disable the gate. Adequate: approved exception. Excellent: scoped, time-bounded, compensating controls and follow-up.

**Likely reviewer follow-ups**

Who owns residual risk? What prevents exception becoming permanent?

**Common pitfalls**

Unapproved bypass or indefinite waiver.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q15 — Model-artifact supply chain

- **ID:** `DRW-Q15`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** A model is imported from an external hub and loaded by an inference service.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Design model inventory, origin/hash checks, format/deserialization safety, approval and data lineage.

**Required diagram/table or written artifact**

Model artifact record and trust-boundary diagram.

**Weighted rubric**

Origin/integrity 25%; safe loading 20%; inventory/lineage 20%; access control 15%; evidence/gaps 20%.

**Weak / adequate / excellent characteristics**

Weak: sign after download. Adequate: source and hash checks. Excellent: independent source review and runtime boundary controls.

**Likely reviewer follow-ups**

What does a software SBOM miss? How is model behavior evaluated separately?

**Common pitfalls**

Assuming internal signature proves upstream safety.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

### DRW-Q16 — Security metrics and Goodhart resistance

- **ID:** `DRW-Q16`
- **Scope:** M12 design review
- **Type:** Whiteboard design prompt
- **Level:** L3–L4
- **Estimated time:** 25 minutes `[ILLUSTRATIVE]`
- **Business / technical context:** Leadership wants one security KPI and teams can manipulate finding counts.
- **Constraints / assumptions:** laptop-first budget; learner-owned environment; no real credentials; source-sensitive behavior marked `[VERIFY]`.

**Design question**

Design balanced measures of coverage, freshness, remediation, exception age, alert quality and verified outcomes.

**Required diagram/table or written artifact**

Metric dictionary, dashboard sketch and governance notes.

**Weighted rubric**

Coverage 25%; outcome measures 20%; gaming resistance 20%; data quality 15%; actionability 20%.

**Weak / adequate / excellent characteristics**

Weak: zero findings. Adequate: count plus SLA. Excellent: counter-metrics, coverage denominators and audit of suppression changes.

**Likely reviewer follow-ups**

How would you detect declining scan coverage? Which metric drives action?

**Common pitfalls**

Rewarding suppression; no source freshness or coverage denominator.

**Model answer direction**

A strong response identifies the protected asset and trust boundaries, states assumptions, maps controls to threats, specifies positive and negative tests, assigns owners, plans safe rollout/rollback, distinguishes local simulation from production evidence, and leaves unresolved source-sensitive claims open. It records residual risk rather than claiming completeness.

---

## Scoring and remediation

### Required overall scoring rubric

- **80% or higher — Proceed:** review missed items, then complete or defend the capstone.
- **60–79% — Remediate:** revisit the relevant units and repeat the failed question categories.
- **Below 60% — Repeat:** revisit the foundational units, redo the labs, and retake the bank after remediation.

An unanswered, `NOT RUN`, or unsupported-platform question is not automatically correct. Passing the question bank is evidence of learning, not proof that a production environment is secure.

### Blank learner scorecard

| Measure | Correct | Attempted / eligible | Percentage | Notes / remediation |
|---|---:|---:|---:|---|
| Unit 1 — Threat modelling | | | | |
| Unit 2 — Scanning and triage | | | | |
| Unit 3 — SBOM and provenance | | | | |
| Unit 4 — Signing and verification | | | | |
| Unit 5 — CI isolation and identities | | | | |
| Unit 6 — Workload identity and rotation | | | | |
| Unit 7 — Runtime hardening | | | | |
| Unit 8 — Admission controls | | | | |
| Unit 9 — Audit and remediation | | | | |
| Unit 10 — SLSA/provenance | | | | |
| Unit 11 — Policy authoring | | | | |
| Unit 12 — Falco detection | | | | |
| Cross-unit integration | | | | |
| L1 — Foundations | | | | |
| L2 — Working practice | | | | |
| L3 — Production engineering | | | | |
| L4 — Operations under failure | | | | |
| Conceptual short answer | | | | |
| Multiple choice | | | | |
| Artifact interpretation | | | | |
| Configuration/artifact review | | | | |
| Incident ordering | | | | |
| Design and synthesis | | | | |
| **Overall core bank** | | | | |

**Calculation:** percentage = correct ÷ attempted/eligible × 100. Exclude nothing silently: list `NOT RUN`, unsupported-platform items and unanswered questions separately, and do not count them as correct. For open-ended design items, use the stated rubric and retain reviewer notes.

### Remediation map

| Weak category / topic | Revisit unit(s) | Required evidence before retry |
|---|---|---|
| Assets, DFD, STRIDE, residual risk | Unit 1 | Updated threat model, owners, review dates and threat/control mapping |
| Scanner scope, freshness, contextual triage | Units 2, 9 | Comparable scan metadata, ranked queue and expiry controls |
| SBOM quality, digest binding, “are we affected?” | Units 3, 9 | Exact-digest inventory query and completeness limitations |
| Signatures, identity, trust roots, attestations | Units 4, 10 | Positive/negative verification evidence for exact digest and identity |
| CI trust boundaries, OIDC, caches, runner isolation | Units 5, 6 | Untrusted-job negative tests and cache/identity separation evidence |
| Least privilege and credential rotation | Unit 6 | Identity inventory, timestamps and old-token rejection evidence |
| Runtime hardening, CNI, PSS and exceptions | Unit 7 | Conformance matrix with target-platform caveats |
| Admission scope, update paths, fail-open/closed | Units 8, 11 | Negative fixtures, staged rollout and failure-mode test |
| Finding lifecycle, exceptions and audit evidence | Unit 9 | Exact-digest closure record, freshness and overdue-exception report |
| SLSA/provenance requirements | Unit 10 | Verified spec notes and requirement-to-evidence mapping; otherwise keep `[VERIFY]` |
| Policy engine semantics and mutation tests | Unit 11 | Versioned engine tests, boundary fixtures and separate environment evidence |
| Falco rule precision and sensor health | Unit 12 | Benign event fixture, heartbeat/event-source evidence and alert disposition |
| Incident ordering and recovery | Units 6, 9, 12 | Timeline, containment rationale, scope, verification and prevention actions |
| Metrics / Goodhart resistance | Units 2, 9, 12 | Coverage denominators, freshness, exceptions and outcome-based metrics |

### Scoring by level and question type

Report percentages by unit, L1–L4, and question type. Review configuration-review performance separately: record the number of defects found, corrections proposed, failure paths named and regression tests specified. Review incident ordering separately from root-cause accuracy. A high total score must not conceal a critical weakness in incident response, identity trust or admission correctness.

## Roadmap coverage matrix

The following matrix maps the required source topics to actual question IDs. `PASS` means the bank contains direct assessment and a model answer; version-specific execution claims remain separately marked `[VERIFY]`.

| Source unit/topic | Required assessment coverage | Question IDs | Question types | Levels | Coverage status | Open gap / verification note |
|---|---|---|---|---|---|---|
| Unit 1: Threat modelling for data and ML platforms — all listed topics | Concepts, MCQs, artifacts, three config reviews, incident, design and synthesis | `U01-Q01`–`U01-Q15`; related integration IDs | All required types | L1–L4 | PASS | Exact tool/API/spec behavior remains `[VERIFY]` where no versioned source is supplied. |
| Unit 2: Container image scanning and vulnerability triage — all listed topics | Concepts, MCQs, artifacts, three config reviews, incident, design and synthesis | `U02-Q01`–`U02-Q15`; related integration IDs | All required types | L1–L4 | PASS | Exact tool/API/spec behavior remains `[VERIFY]` where no versioned source is supplied. |
| Unit 3: Software bills of materials and dependency provenance — all listed topics | Concepts, MCQs, artifacts, three config reviews, incident, design and synthesis | `U03-Q01`–`U03-Q15`; related integration IDs | All required types | L1–L4 | PASS | Exact tool/API/spec behavior remains `[VERIFY]` where no versioned source is supplied. |
| Unit 4: Image signing and deployment verification — all listed topics | Concepts, MCQs, artifacts, three config reviews, incident, design and synthesis | `U04-Q01`–`U04-Q15`; related integration IDs | All required types | L1–L4 | PASS | Exact tool/API/spec behavior remains `[VERIFY]` where no versioned source is supplied. |
| Unit 5: Build isolation and short-lived CI identities — all listed topics | Concepts, MCQs, artifacts, three config reviews, incident, design and synthesis | `U05-Q01`–`U05-Q15`; related integration IDs | All required types | L1–L4 | PASS | Exact tool/API/spec behavior remains `[VERIFY]` where no versioned source is supplied. |
| Unit 6: Workload identity and credential rotation (security architecture view) — all listed topics | Concepts, MCQs, artifacts, three config reviews, incident, design and synthesis | `U06-Q01`–`U06-Q15`; related integration IDs | All required types | L1–L4 | PASS | Exact tool/API/spec behavior remains `[VERIFY]` where no versioned source is supplied. |
| Unit 7: Runtime security and container hardening — all listed topics | Concepts, MCQs, artifacts, three config reviews, incident, design and synthesis | `U07-Q01`–`U07-Q15`; related integration IDs | All required types | L1–L4 | PASS | Exact tool/API/spec behavior remains `[VERIFY]` where no versioned source is supplied. |
| Unit 8: Admission controls and deployment policy enforcement — all listed topics | Concepts, MCQs, artifacts, three config reviews, incident, design and synthesis | `U08-Q01`–`U08-Q15`; related integration IDs | All required types | L1–L4 | PASS | Exact tool/API/spec behavior remains `[VERIFY]` where no versioned source is supplied. |
| Unit 9: Security auditing and vulnerability remediation workflows — all listed topics | Concepts, MCQs, artifacts, three config reviews, incident, design and synthesis | `U09-Q01`–`U09-Q15`; related integration IDs | All required types | L1–L4 | PASS | Exact tool/API/spec behavior remains `[VERIFY]` where no versioned source is supplied. |
| Unit 10: SLSA framework and build provenance levels — all listed topics | Concepts, MCQs, artifacts, three config reviews, incident, design and synthesis | `U10-Q01`–`U10-Q15`; related integration IDs | All required types | L1–L4 | PASS | Exact tool/API/spec behavior remains `[VERIFY]` where no versioned source is supplied. |
| Unit 11: Kyverno and OPA Gatekeeper policy authoring — all listed topics | Concepts, MCQs, artifacts, three config reviews, incident, design and synthesis | `U11-Q01`–`U11-Q15`; related integration IDs | All required types | L1–L4 | PASS | Exact tool/API/spec behavior remains `[VERIFY]` where no versioned source is supplied. |
| Unit 12: Runtime threat detection with Falco — all listed topics | Concepts, MCQs, artifacts, three config reviews, incident, design and synthesis | `U12-Q01`–`U12-Q15`; related integration IDs | All required types | L1–L4 | PASS | Exact tool/API/spec behavior remains `[VERIFY]` where no versioned source is supplied. |
| Cross-unit dependencies: threat model → scan/SBOM/sign/provenance/admission/runtime/detection | End-to-end reasoning and trust-boundary failures | `XINT-Q01`–`XINT-Q50` | Integration scenarios | L2–L4 | PASS | Production guarantees require environment-specific evidence. |
| Design-review themes 1–16 | Sixteen distinct design reviews, rubrics, follow-ups and pitfalls | `DRW-Q01`–`DRW-Q16` | Design review | L3–L4 | PASS | Reviewer should confirm scoring consistency. |
| Scoring, remediation and source-verification rules | Blank scorecard, percentage method, remediation map and explicit non-certification statement | Scoring section; all source-sensitive questions | Scoring / governance | L1–L4 | PASS | Learner score intentionally blank. |
| Current tool/spec details | Versioned official documentation, schema/flag/metric details, SLSA requirement text | All `[VERIFY]` notes | Verification register | L2–L4 | OPEN | The standalone generated syllabus and versioned tool baseline were not supplied; do not infer exact current syntax or SLSA requirements. |

### Topic-level coverage ledger

This detailed ledger maps each syllabus topic family to stable question IDs. `PASS WITH OPEN ITEMS` means the assessment content is present; version-specific implementation claims remain open until verified. Human review should confirm that each linked question directly tests the entire row rather than only mentioning its vocabulary.

| Source unit/topic | Required assessment coverage | Question IDs | Question types | Levels | Coverage status | Open gap / verification note |
|---|---|---|---|---|---|---|
| Unit 1: threat modelling before control selection; assets, actors, trust boundaries, attack surface, vulnerability/threat/risk, CIA and privacy | Explain, interpret, review and apply the stated topic | `U01-Q01`, `U01-Q04`, `U01-Q07` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 1: data-flow diagrams with processes, stores, external entities, flows and boundaries; STRIDE applied to DFD elements | Explain, interpret, review and apply the stated topic | `U01-Q02`, `U01-Q05`, `U01-Q08` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 1: lab-platform threat model with at least 10 elements, qualitative likelihood/impact, threat/control mapping, residual risk, owner and review date | Explain, interpret, review and apply the stated topic | `U01-Q03`, `U01-Q06`, `U01-Q09` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 1: attack trees for attacker-controlled code in an inference pod and training-data exfiltration; source-to-runtime supply-chain stages | Explain, interpret, review and apply the stated topic | `U01-Q10`, `U01-Q11`, `U01-Q13` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 1: ML/data threats including unsafe deserialization, poisoned training data or feature stores, compromised model hubs, notebook compromise, model theft, prompt-injection/data-exfiltration awareness, GPU/driver supply chain and over-broad access | Explain, interpret, review and apply the stated topic | `U01-Q12`, `U01-Q14`, `U01-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 1: frameworks as vocabulary/completeness aids; threat-model-as-code, validation, traceability, security debt, review cadence and limits of false precision | Explain, interpret, review and apply the stated topic | `U01-Q13`, `U01-Q14`, `U01-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 2: scanner capabilities and blind spots; CVE/NVD/GHSA/OSV/distro advisories, CVSS versus contextual risk, CWE awareness and database freshness | Explain, interpret, review and apply the stated topic | `U02-Q01`, `U02-Q04`, `U02-Q07` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 2: Trivy image/filesystem/config/Kubernetes scanning and report interpretation; version-sensitive output/flags | Explain, interpret, review and apply the stated topic | `U02-Q02`, `U02-Q05`, `U02-Q08` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 2: OS and language packages, lockfiles, transitive dependencies, vendored/static components and scanner blind spots | Explain, interpret, review and apply the stated topic | `U02-Q03`, `U02-Q06`, `U02-Q09` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 2: controlled comparison of naive, hardened and distroless-style images with identical scanner/version/database/settings | Explain, interpret, review and apply the stated topic | `U02-Q10`, `U02-Q11`, `U02-Q13` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 2: CI gates, SARIF/JSON evidence, caching, rate limits/offline behavior, registry and scheduled rescanning | Explain, interpret, review and apply the stated topic | `U02-Q12`, `U02-Q14`, `U02-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 2: risk-based triage using exposure, reachability, exploitability, fix availability, compensating controls, criticality and blast radius; KEV/EPSS contextual use | Explain, interpret, review and apply the stated topic | `U02-Q13`, `U02-Q14`, `U02-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 2: VEX evidence, expiring ignores, DB freshness gates, remediation SLAs, trends, exposure windows, zero-day drills and metric gaming | Explain, interpret, review and apply the stated topic | `U02-Q13`, `U02-Q14`, `U02-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 3: SBOM purpose and limits; SPDX versus CycloneDX; component metadata, PURLs, hashes, relationships, licenses and tool metadata | Explain, interpret, review and apply the stated topic | `U03-Q01`, `U03-Q04`, `U03-Q07` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 3: Syft/Trivy SBOM generation and version-sensitive formats; source/lockfile versus built-image SBOM reconciliation | Explain, interpret, review and apply the stated topic | `U03-Q02`, `U03-Q05`, `U03-Q08` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 3: digest association, build-time generation, storage, indexing, release diffs and cross-artifact queries | Explain, interpret, review and apply the stated topic | `U03-Q03`, `U03-Q06`, `U03-Q09` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 3: SBOM-based vulnerability analysis, VEX relationship, signed SBOM versus attestation versus provenance | Explain, interpret, review and apply the stated topic | `U03-Q10`, `U03-Q11`, `U03-Q13` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 3: vendored, static and dynamically downloaded components; cataloger limits and false completeness | Explain, interpret, review and apply the stated topic | `U03-Q12`, `U03-Q14`, `U03-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 3: ML-BOM/model inventory awareness and limits of software SBOMs for weights, datasets, training parameters and model lineage | Explain, interpret, review and apply the stated topic | `U03-Q13`, `U03-Q14`, `U03-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 3: incident response: answer “are we affected?” from inventory; distinguish provenance from inventory | Explain, interpret, review and apply the stated topic | `U03-Q13`, `U03-Q14`, `U03-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 4: integrity, authenticity, identity, trust roots, digest versus tag, signature versus scan, attestation and provenance | Explain, interpret, review and apply the stated topic | `U04-Q01`, `U04-Q04`, `U04-Q07` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 4: cosign key-based signing/verification and safe key custody; keyless/OIDC trust assumptions | Explain, interpret, review and apply the stated topic | `U04-Q02`, `U04-Q05`, `U04-Q08` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 4: pinned signer identity/key, repository/ref/builder expectations and CI/admission trust policy | Explain, interpret, review and apply the stated topic | `U04-Q03`, `U04-Q06`, `U04-Q09` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 4: attestations for SBOM, scan summary, tests and provenance where supported | Explain, interpret, review and apply the stated topic | `U04-Q10`, `U04-Q11`, `U04-Q13` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 4: negative cases: unsigned artifact, wrong identity/key, tag mutation/digest mismatch, missing/stale attestation, wrong source/builder | Explain, interpret, review and apply the stated topic | `U04-Q12`, `U04-Q14`, `U04-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 4: key rotation and compromise response; model-artifact verification awareness | Explain, interpret, review and apply the stated topic | `U04-Q13`, `U04-Q14`, `U04-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 4: why signed does not mean safe; local/public Sigstore trust limitations | Explain, interpret, review and apply the stated topic | `U04-Q13`, `U04-Q14`, `U04-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 5: separation of untrusted PR/fork validation from trusted release jobs | Explain, interpret, review and apply the stated topic | `U05-Q01`, `U05-Q04`, `U05-Q07` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 5: ephemeral/rootless builders where supported, least privilege and no exposed Docker socket to untrusted jobs | Explain, interpret, review and apply the stated topic | `U05-Q02`, `U05-Q05`, `U05-Q08` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 5: short-lived federated/OIDC identities; provider-specific claims only when verified; avoid long-lived registry passwords | Explain, interpret, review and apply the stated topic | `U05-Q03`, `U05-Q06`, `U05-Q09` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 5: protected refs/environments, job permissions, secret isolation, trusted/untrusted cache separation, dependency/tool pinning, hermeticity limits and controlled egress | Explain, interpret, review and apply the stated topic | `U05-Q10`, `U05-Q11`, `U05-Q13` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 5: trusted-builder claims and CI compromise kill switch | Explain, interpret, review and apply the stated topic | `U05-Q12`, `U05-Q14`, `U05-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 5: negative tests for release capability from untrusted jobs, harmless cache poisoning, dummy-secret exposure, unauthorized egress and unprotected-ref release | Explain, interpret, review and apply the stated topic | `U05-Q13`, `U05-Q14`, `U05-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 5: static CI audit limitations; M02 handoff focuses on security-specific application | Explain, interpret, review and apply the stated topic | `U05-Q13`, `U05-Q14`, `U05-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 6: identity inventory and trust relationships across workloads, service accounts, cloud identities, CI identities and humans | Explain, interpret, review and apply the stated topic | `U06-Q01`, `U06-Q04`, `U06-Q07` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 6: workload identity versus static credentials; least privilege, just-in-time access, token lifetime, rotation/revocation, ownership and auditability | Explain, interpret, review and apply the stated topic | `U06-Q02`, `U06-Q05`, `U06-Q08` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 6: attack paths and blast radius if an identity/token is stolen | Explain, interpret, review and apply the stated topic | `U06-Q03`, `U06-Q06`, `U06-Q09` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 6: rotation drills with measured timestamps, token-theft detection concepts and verification old credentials no longer work | Explain, interpret, review and apply the stated topic | `U06-Q10`, `U06-Q11`, `U06-Q13` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 6: dummy lab identities only; M09 handoff avoids re-teaching identity mechanism implementation | Explain, interpret, review and apply the stated topic | `U06-Q12`, `U06-Q14`, `U06-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 6: incident ordering: preserve evidence, revoke/rotate appropriately, assess downstream trust and verify recovery | Explain, interpret, review and apply the stated topic | `U06-Q13`, `U06-Q14`, `U06-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 7: non-root, read-only root filesystem, capability dropping, allowPrivilegeEscalation, seccomp, resources, service-account token mounting and probes | Explain, interpret, review and apply the stated topic | `U07-Q01`, `U07-Q04`, `U07-Q07` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 7: Pod Security Standards and version-sensitive enforcement behavior | Explain, interpret, review and apply the stated topic | `U07-Q02`, `U07-Q05`, `U07-Q08` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 7: NetworkPolicy default-deny, explicit flows and CNI enforcement caveats | Explain, interpret, review and apply the stated topic | `U07-Q03`, `U07-Q06`, `U07-Q09` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 7: runtime conformance suite with expected denials; kube-bench/CIS triage with verified versions | Explain, interpret, review and apply the stated topic | `U07-Q10`, `U07-Q11`, `U07-Q13` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 7: container-compromise drill: isolate, preserve evidence, rotate credentials and replace workload | Explain, interpret, review and apply the stated topic | `U07-Q12`, `U07-Q14`, `U07-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 7: hardening trade-offs, compatibility, exception owners and expiry; limits of runtime hardening | Explain, interpret, review and apply the stated topic | `U07-Q13`, `U07-Q14`, `U07-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 8: admission-time versus build-time/runtime controls; fail-open/fail-closed and availability/blast radius | Explain, interpret, review and apply the stated topic | `U08-Q01`, `U08-Q04`, `U08-Q07` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 8: ValidatingAdmissionPolicy, Kyverno and Gatekeeper/OPA; API versions and syntax verified or [VERIFY] | Explain, interpret, review and apply the stated topic | `U08-Q02`, `U08-Q05`, `U08-Q08` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 8: registry allow-list, digest pinning, signatures/attestations, privileged settings, initContainers, workload kinds and update paths | Explain, interpret, review and apply the stated topic | `U08-Q03`, `U08-Q06`, `U08-Q09` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 8: bypasses: unanchored registry regex, only containers checked, broad label opt-out, absent/null bugs, UPDATE gaps, Pod-only matching, always-pass defects | Explain, interpret, review and apply the stated topic | `U08-Q10`, `U08-Q11`, `U08-Q13` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 8: audit/warn/deny staged rollout, policy reports, test coverage, engine upgrade rehearsal, webhook HA and failure policy | Explain, interpret, review and apply the stated topic | `U08-Q12`, `U08-Q14`, `U08-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 8: exceptions-as-code, expiry enforcement, RBAC and policy engines as privileged infrastructure | Explain, interpret, review and apply the stated topic | `U08-Q13`, `U08-Q14`, `U08-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 8: Kyverno and Gatekeeper are tested in separate clusters/environments; negative fixtures and mutation/correctness-trap tests | Explain, interpret, review and apply the stated topic | `U08-Q13`, `U08-Q14`, `U08-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 9: finding normalization, lifecycle states, triage, ownership, remediation SLAs and risk-based prioritization | Explain, interpret, review and apply the stated topic | `U09-Q01`, `U09-Q04`, `U09-Q07` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 9: re-scan-verified closure, evidence quality, expiring exceptions, VEX and justified not-affected claims | Explain, interpret, review and apply the stated topic | `U09-Q02`, `U09-Q05`, `U09-Q08` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 9: scheduled scans, freshness, coverage of running digests, time-to-remediate, SLA breaches, exception age and audit trails | Explain, interpret, review and apply the stated topic | `U09-Q03`, `U09-Q06`, `U09-Q09` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 9: KEV/EPSS freshness and contextual use; synthetic advisory “are we affected?” drill | Explain, interpret, review and apply the stated topic | `U09-Q10`, `U09-Q11`, `U09-Q13` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 9: dashboards, Goodhart resistance and zero-finding metric pitfalls | Explain, interpret, review and apply the stated topic | `U09-Q12`, `U09-Q14`, `U09-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 9: mock audit, evidence retention, access control, privacy and reporting | Explain, interpret, review and apply the stated topic | `U09-Q13`, `U09-Q14`, `U09-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 9: stale database, unreviewed ignore, no owner, exception abuse and gate disabled due to noise | Explain, interpret, review and apply the stated topic | `U09-Q13`, `U09-Q14`, `U09-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 10: supply-chain integrity and threat categories grounded in verified source spec; avoid memorized/outdated level definitions | Explain, interpret, review and apply the stated topic | `U10-Q01`, `U10-Q04`, `U10-Q07` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 10: provenance purpose, subject digest, builder identity, source reference, build type, external parameters and supported schema fields | Explain, interpret, review and apply the stated topic | `U10-Q02`, `U10-Q05`, `U10-Q08` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 10: verified spec version/track and requirements; map requirement to threat/control using verified notes | Explain, interpret, review and apply the stated topic | `U10-Q03`, `U10-Q06`, `U10-Q09` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 10: trusted-builder simulation, forged-provenance negative test, admission-time verification and reproducible-rebuild comparison | Explain, interpret, review and apply the stated topic | `U10-Q10`, `U10-Q11`, `U10-Q13` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 10: why provenance existence does not prove authentic/trustworthy provenance | Explain, interpret, review and apply the stated topic | `U10-Q12`, `U10-Q14`, `U10-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 10: no SLSA level claim unless every applicable requirement is evidenced; local simulation versus hosted trusted-builder guarantees | Explain, interpret, review and apply the stated topic | `U10-Q13`, `U10-Q14`, `U10-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 11: policy design, scope, matching/exclusions, validate/mutate/generate/verifyImages where supported and version-sensitive | Explain, interpret, review and apply the stated topic | `U11-Q01`, `U11-Q04`, `U11-Q07` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 11: Gatekeeper ConstraintTemplates/Constraints/Rego where supported; separate engine-specific semantics | Explain, interpret, review and apply the stated topic | `U11-Q02`, `U11-Q05`, `U11-Q08` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 11: policy tests, unit fixtures, mutation/correctness traps, exception governance and RBAC | Explain, interpret, review and apply the stated topic | `U11-Q03`, `U11-Q06`, `U11-Q09` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 11: scope across workload kinds, initContainers, updates, missing/null fields, registry matching and policy-engine always-pass defects | Explain, interpret, review and apply the stated topic | `U11-Q10`, `U11-Q11`, `U11-Q13` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 11: separate Kyverno and Gatekeeper clusters/environments; staged rollout, reports, upgrades and rollback | Explain, interpret, review and apply the stated topic | `U11-Q12`, `U11-Q14`, `U11-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 11: policy engine as privileged infrastructure, admission availability, monitoring and safe failure behavior | Explain, interpret, review and apply the stated topic | `U11-Q13`, `U11-Q14`, `U11-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 12: runtime event sources, Falco rules/fields and version-sensitive driver/plugin support | Explain, interpret, review and apply the stated topic | `U12-Q01`, `U12-Q04`, `U12-Q07` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 12: detection logic, expected behavior, false positives/negatives, severity and rule tuning without blindness | Explain, interpret, review and apply the stated topic | `U12-Q02`, `U12-Q05`, `U12-Q08` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 12: benign authorized purple-team markers and expected-denial tests | Explain, interpret, review and apply the stated topic | `U12-Q03`, `U12-Q06`, `U12-Q09` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 12: sensor health, event-source coverage, dropped events, permissions, tampering and meta-monitoring | Explain, interpret, review and apply the stated topic | `U12-Q10`, `U12-Q11`, `U12-Q13` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 12: alert triage, evidence preservation, containment, scope, credential rotation, recovery and prevention | Explain, interpret, review and apply the stated topic | `U12-Q12`, `U12-Q14`, `U12-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 12: Prometheus/Alertmanager/Loki integration and syntax/metric names marked [VERIFY] unless verified | Explain, interpret, review and apply the stated topic | `U12-Q13`, `U12-Q14`, `U12-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Unit 12: detection coverage matrix, alert quality, overhead and limitations; no alerts does not mean no attack | Explain, interpret, review and apply the stated topic | `U12-Q13`, `U12-Q14`, `U12-Q15` | Concept/artifact/config review/design | L1–L4 | PASS WITH OPEN ITEMS | Verify exact tool/spec details and ensure the linked question directly exercises the topic during human review. |
| Cross-unit integration: end-to-end trust chain, incidents, exceptions and operational failure | Integrate multiple controls and explain dependencies | `XINT-Q01`–`XINT-Q50` | Integration scenarios | L2–L4 | PASS | Verify exact platform behavior before executing the scenario. |
| Whiteboard design review themes 1–16 | Threat model, triage, SBOM, signing, CI, identity, runtime, admission, audit, SLSA, policy, Falco, incident, velocity, model artifacts, metrics | `DRW-Q01`–`DRW-Q16` | Design reviews | L3–L4 | PASS | Human reviewer should score against the supplied weighted rubric. |

## References and version-verification register

### Source hierarchy

1. `PROMPT-Production-Security-and-Software-Supply-Chain.md` — authoritative syllabus-generation requirements supplied in this conversation.
2. `Roadmap(20261029-113851).md` — roadmap export confirming M12 filenames and capstone location.
3. The supplied Unit 13 generation prompt — authoritative assessment counts, question fields, whiteboard themes, scoring, safety and audit requirements.
4. The separately generated `SYLLABUS-Production-Security-and-Software-Supply-Chain.md` was not available as a distinct source file in this turn. Its expected concepts were taken only from the supplied generation prompt; any syllabus-specific detail not explicitly present remains open.

### Technical verification register

| Claim / topic | Source/spec | Version/date | Status | Next action |
|---|---|---|---|---|
| Trivy flags, output formats, DB freshness, ignore/VEX behavior | Official Trivy docs and selected installed CLI help | `[VERIFY]` | OPEN | Record exact version, DB timestamp and official doc revision before running a real gate. |
| Syft output formats, SPDX/CycloneDX schema | Official Syft docs; SPDX/CycloneDX specs | `[VERIFY]` | OPEN | Validate generated documents against the chosen schema/version and record tool metadata. |
| cosign signing, verification, attestations, keyless identity | Official Sigstore/cosign docs | `[VERIFY]` | OPEN | Verify signer identity, trust roots, subject binding and key rotation behavior for chosen trust model. |
| CI OIDC claims, permissions and action pinning | Selected CI provider’s official security docs | `[VERIFY]` | OPEN | Confirm issuer, audience and repository/ref/environment claims; use harmless negative tests. |
| Kubernetes API versions, PSS and NetworkPolicy | Official Kubernetes docs and target CNI docs | `[VERIFY]` | OPEN | Check cluster version, enforcement mode and actual allowed/denied connectivity. |
| ValidatingAdmissionPolicy, Kyverno, Gatekeeper/CEL/Rego syntax | Official docs for selected Kubernetes/engine versions | `[VERIFY]` | OPEN | Validate schemas, test create/update paths and rehearse webhook failure behavior. |
| SLSA track, level requirements and provenance fields | Selected official SLSA specification version/track and supplied verified notes | `[VERIFY]` | OPEN | Copy exact requirement text into the evidence matrix; make no level claim until every applicable requirement is evidenced. |
| Falco driver/plugin/rule fields and metrics | Official Falco docs for selected release/event source | `[VERIFY]` | OPEN | Verify field support, event source, sensor-health signals and benign fixture results. |
| Prometheus/Alertmanager/Loki metric and query syntax | Official docs for selected versions | `[VERIFY]` | OPEN | Verify metric names and query syntax; do not infer a working dashboard from this assessment. |
| Framework names/current versions (ATT&CK, CIS, NIST SP 800-190, OWASP, MITRE ATLAS, LINDDUN) | Respective official sources | `[VERIFY]` | OPEN | Confirm current name/version when using framework mappings in an implementation. |

No external source verification is claimed in this artifact. The table records what a human implementing the lab must verify; no version-sensitive claim is silently presented as verified.

## Final independent audit report

### 1. Audit status

**Audit status: PASS WITH OPEN ITEMS.** The Markdown is generated from the supplied prompt and roadmap export, with source-sensitive implementation facts explicitly marked `[VERIFY]`. This is a structural/content self-audit, not a live execution audit.

### 2. Count report

| Section | Count | Expected | Status |
|---|---:|---:|---|
| Unit 1 — Threat modelling for data and ML platforms | 15 | ≥15 | PASS |
| Unit 2 — Container image scanning and vulnerability triage | 15 | ≥15 | PASS |
| Unit 3 — Software bills of materials and dependency provenance | 15 | ≥15 | PASS |
| Unit 4 — Image signing and deployment verification | 15 | ≥15 | PASS |
| Unit 5 — Build isolation and short-lived CI identities | 15 | ≥15 | PASS |
| Unit 6 — Workload identity and credential rotation (security architecture view) | 15 | ≥15 | PASS |
| Unit 7 — Runtime security and container hardening | 15 | ≥15 | PASS |
| Unit 8 — Admission controls and deployment policy enforcement | 15 | ≥15 | PASS |
| Unit 9 — Security auditing and vulnerability remediation workflows | 15 | ≥15 | PASS |
| Unit 10 — SLSA framework and build provenance levels | 15 | ≥15 | PASS |
| Unit 11 — Kyverno and OPA Gatekeeper policy authoring | 15 | ≥15 | PASS |
| Unit 12 — Runtime threat detection with Falco | 15 | ≥15 | PASS |
| Cross-unit integration | 50 | ≥50 | PASS |
| Design-review prompts | 16 | exactly 16 | PASS |
| Core questions | 230 | ≥230 | PASS |
| Unique IDs including design reviews | 246 | 230 + 16 | PASS |

### 3. Distribution report

| Type | Expected count | Status |
|---|---:|---|
| Conceptual short answer | 36 | PASS |
| Multiple choice (four options each) | 36 | PASS |
| Artifact interpretation | 36 | PASS |
| Configuration/artifact review | 36 | PASS |
| Incident / response scenario | 12 | PASS |
| Design question with rubric | 12 | PASS |
| Synthesis / troubleshooting | 12 | PASS |
| Cross-unit integration scenarios | 50 | PASS |
| Whiteboard design reviews | 16 | PASS |

**Core-question level distribution (230 questions):** L1 = 36; L2 = 88; L3 = 65; L4 = 41. Whiteboard prompts are additionally marked L3–L4 and are not included in those 230 core counts. These counts describe the authored metadata, not learner performance.

### 4. Coverage report

- **PASS:** M12 Units 1–12 are represented in roadmap order, with all required question types and the major topic families from the supplied prompt.
- **OPEN:** exact current Trivy/Syft/cosign/CI OIDC/Kubernetes/VAP/Kyverno/Gatekeeper/Falco/observability syntax and current SLSA requirement text need versioned official verification.
- **OPEN:** the separately generated `SYLLABUS-Production-Security-and-Software-Supply-Chain.md` was not supplied as a standalone source file; coverage is based on the supplied syllabus-generation prompt, not unseen syllabus text.
- **OPEN:** actual lab tests and production-platform behavior have not been executed as part of this document generation.

### 5. Technical verification register

See the register above. Every version-sensitive family is marked `[VERIFY]`; no CVE IDs, real incidents, universal thresholds or SLSA level definitions are invented.

### 6. Defect log

| ID | Severity | Finding | Correction made | Residual risk |
|---|---|---|---|---|
| AUD-01 | Medium | Standalone generated syllabus file unavailable as a distinct source | Used supplied syllabus-generation prompt as authority and disclosed limitation | An omitted syllabus-only topic may remain uncovered until comparison against that file. |
| AUD-02 | Medium | No selected live tool/spec baseline provided | Marked tool/API/schema/metric/SLSA specifics `[VERIFY]` | Human must verify before converting excerpts into executable lab tests. |
| AUD-03 | Medium | No live execution evidence supplied | All artifacts labelled synthetic and tests described as expected validation, not run | No production security or compliance claim is supported. |
| AUD-04 | Low | Some examples intentionally use simplified synthetic summaries | Marked synthetic/pseudocode and stated verification boundary | Reviewers must not copy pseudocode as deployable policy. |

### 7. Human review checklist

- [ ] Compare against the generated syllabus file when available, topic by topic.
- [ ] Verify all tool flags, schemas, fields, provider claims and policy semantics against selected versions.
- [ ] Insert verified SLSA requirement excerpts before grading exact requirement-mapping answers.
- [ ] Run the positive and negative fixtures in isolated, learner-owned environments and capture actual evidence.
- [ ] Confirm the coverage matrix against question content and update any partial/open rows.
- [ ] Review MCQ option explanations, design rubrics and question difficulty before formal assessment use.
- [ ] Keep all credentials synthetic; do not test third-party systems or credentials.

### 8. Sign-off

- Content status: `DRAFT-AUDITED`
- **Audit date:** 2026-10-29
- **Auditor:** AI self-audit; human technical review required
- **Unresolved `[VERIFY]` item count:** 10 topic families in the technical verification register, plus individual source/version references inside questions.
- **Execution statement:** Generated answers and synthetic artifacts are not evidence of real tool execution. No live test is claimed to have run or passed.
- **Certification statement:** This assessment does not certify production security, compliance or regulatory conformance.

